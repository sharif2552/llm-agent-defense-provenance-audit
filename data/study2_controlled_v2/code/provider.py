"""Local fault source; its oracle records are never given to the accounting guard."""
from __future__ import annotations

import contextlib
import json
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL = "gpt-evalfault-v2"
FAULTS = ("http_400", "context_length", "http_401", "http_404", "http_408",
          "http_429", "http_500", "http_502", "http_503", "http_504",
          "connect_timeout", "read_timeout", "connection_reset", "malformed_json",
          "empty_choices", "wrong_model_identity", "invalid_tool_arguments")


class Provider:
    def __init__(self, fault, sequence, content):
        self.fault, self.sequence, self.content = fault, sequence, content
        self.events = []
        self.lock = threading.Lock()

    def next_event(self, model):
        with self.lock:
            failing = self.fault != "none" and (self.sequence == "persistent" or len(self.events) == 0)
            event = {"attempt": len(self.events) + 1, "delivered_fault": self.fault if failing else None,
                     "requested_model": model, "transport": "http_loopback"}
            self.events.append(event)
        return event

    def completion(self, model):
        return {"id": "chatcmpl-v2", "object": "chat.completion", "created": 0,
                "model": model, "choices": [{"index": 0, "message": {"role": "assistant", "content": self.content},
                                              "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}

    @contextlib.contextmanager
    def serve(self):
        source = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                request = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                event = source.next_event(request.get("model"))
                fault = event["delivered_fault"]
                payload, status = source.completion(request.get("model")), 200
                if fault == "read_timeout":
                    time.sleep(2.0)
                    self.close_connection = True
                    return
                if fault == "connection_reset":
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                if fault and (fault.startswith("http_") or fault == "context_length"):
                    status = 400 if fault == "context_length" else int(fault.split("_")[1])
                    payload = {"error": {"message": "controlled provider failure", "type": "provider_error",
                                         "code": "context_length_exceeded" if fault == "context_length" else str(status)}}
                elif fault == "empty_choices":
                    payload["choices"] = []
                elif fault == "wrong_model_identity":
                    payload["model"] = "unrequested-model"
                elif fault == "invalid_tool_arguments":
                    payload["choices"][0]["message"]["tool_calls"] = [{"id": "call-v2", "type": "function",
                        "function": {"name": "fixture_tool", "arguments": "{"}}]
                    payload["choices"][0]["finish_reason"] = "tool_calls"
                body = b'{"choices":[' if fault == "malformed_json" else json.dumps(payload).encode()
                event["http_status"] = status
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_address[1]}/v1"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def transport(self):
        import httpx
        source = self

        class ConnectTransport(httpx.BaseTransport):
            def handle_request(self, request):
                model = json.loads(request.content).get("model")
                event = source.next_event(model)
                event["transport"] = "httpx_pre_socket"
                if event["delivered_fault"]:
                    raise httpx.ConnectTimeout("controlled connect timeout", request=request)
                return httpx.Response(200, json=source.completion(model), request=request)

        class AsyncConnectTransport(httpx.AsyncBaseTransport):
            async def handle_async_request(self, request):
                return ConnectTransport().handle_request(request)

        return ConnectTransport(), AsyncConnectTransport()
