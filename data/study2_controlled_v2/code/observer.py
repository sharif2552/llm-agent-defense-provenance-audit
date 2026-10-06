"""Operational accounting guard. No scenario names, injected labels, or oracle inputs."""
from __future__ import annotations

import contextlib
import functools
import json


def chain(error):
    names, seen = [], set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        names.append(type(error).__name__)
        error = error.__cause__ or error.__context__
    return names


def inspect_completion(response, requested_model):
    # Some SDK integrations return a raw response wrapper.
    if hasattr(response, "parse") and not hasattr(response, "choices"):
        response = response.parse()
    problems = []
    choices = getattr(response, "choices", None)
    if not choices:
        problems.append("missing_choices")
    actual = getattr(response, "model", None)
    if actual != requested_model:
        problems.append("model_identity_mismatch")
    for choice in choices or []:
        message = getattr(choice, "message", None)
        if message is None:
            problems.append("missing_message")
            continue
        for call in getattr(message, "tool_calls", None) or []:
            try:
                arguments = json.loads(call.function.arguments)
                if not isinstance(arguments, dict):
                    problems.append("tool_arguments_not_object")
            except (ValueError, TypeError, AttributeError):
                problems.append("invalid_tool_arguments")
        if getattr(choice, "finish_reason", None) not in ("stop", "tool_calls", "function_call"):
            problems.append("incomplete_completion")
    return sorted(set(problems))


class Observer:
    def __init__(self):
        self.events = []

    def accepted(self):
        # This experiment has one logical provider stage per run. Later successful
        # calls resolve an earlier failed attempt at that same stage.
        return bool(self.events) and self.events[-1]["ok"]

    def account(self, native):
        if native.get("included") and not self.accepted():
            return {**native, "included": False, "score": None,
                    "guard_reason": "provider_evidence_unresolved"}
        return {**native, "guard_reason": None}

    @contextlib.contextmanager
    def instrument(self):
        from openai.resources.chat.completions import Completions, AsyncCompletions
        old_sync, old_async = Completions.create, AsyncCompletions.create
        observer = self

        def success(response, kwargs):
            issues = inspect_completion(response, kwargs.get("model"))
            observer.events.append({"ok": not issues, "issues": issues, "error_chain": []})

        @functools.wraps(old_sync)
        def sync(*args, **kwargs):
            try:
                result = old_sync(*args, **kwargs)
                success(result, kwargs)
                return result
            except Exception as error:
                observer.events.append({"ok": False, "issues": [], "error_chain": chain(error)})
                raise

        @functools.wraps(old_async)
        async def asynchronous(*args, **kwargs):
            try:
                result = await old_async(*args, **kwargs)
                success(result, kwargs)
                return result
            except Exception as error:
                observer.events.append({"ok": False, "issues": [], "error_chain": chain(error)})
                raise

        Completions.create, AsyncCompletions.create = sync, asynchronous
        try:
            yield
        finally:
            Completions.create, AsyncCompletions.create = old_sync, old_async
