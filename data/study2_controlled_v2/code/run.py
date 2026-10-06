"""Run real native paths; never replay a stored expected outcome."""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import random
import signal
import sys
import time
from unittest.mock import patch

if "--benchmark" in sys.argv and sys.argv[sys.argv.index("--benchmark") + 1] == "agentharm":
    sys.path.insert(0, str(Path.home() / ".evalfault/v2-agentharm-deps"))

from observer import Observer, chain
from provider import FAULTS, Provider
from native import RUNNERS, SELECTION, content

HERE = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def code_hashes():
    return {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ("run.py", "native.py", "observer.py", "provider.py")}


def plan(benchmark, calibration=False):
    conditions = [("none", "control", "success"), ("none", "control", "failure")]
    faults = FAULTS
    conditions += [(fault, sequence, "success") for fault in faults for sequence in ("persistent", "once")]
    tasks = SELECTION[benchmark]["selected_task_ids"]
    return [dict(benchmark=benchmark, task_id=task, fault=fault, sequence=sequence, outcome=outcome, arm=arm)
            for task in tasks for fault, sequence, outcome in conditions for arm in ("native", "guarded")
            if not calibration or task == tasks[0] or fault == "none"]


class Deadline(BaseException):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", choices=sorted(RUNNERS), required=True)
    parser.add_argument("--phase", choices=("calibration", "study"), default="calibration")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    starting_code_sha256 = code_hashes()
    rows = plan(args.benchmark, args.phase == "calibration")
    if args.limit:
        if args.phase == "study":
            raise ValueError("Study may not silently truncate its plan")
        rows = rows[:args.limit]
    random.Random(1729).shuffle(rows)
    destination = HERE / "results" / args.phase
    if args.phase == "calibration":
        destination = destination / digest(code_hashes())[:12]
    destination.mkdir(parents=True, exist_ok=True)
    if args.phase == "study":
        manifest = json.loads((HERE / "freeze.json").read_text())
        assert manifest["code_sha256"] == code_hashes(), "Code changed after local freeze"
        assert manifest["protocol_sha256"] == hashlib.sha256((HERE / "PROTOCOL.md").read_bytes()).hexdigest()
        for relative, expected in manifest["input_sha256"].items():
            assert hashlib.sha256((HERE.parent / relative).read_bytes()).hexdigest() == expected, relative
        for relative, expected in manifest["vendor_input_sha256"].items():
            if relative.startswith("vendor/" + args.benchmark + "/"):
                assert hashlib.sha256((HERE.parent / relative).read_bytes()).hexdigest() == expected, relative
    path = destination / f"{args.benchmark}.jsonl"
    if path.exists() and args.phase == "study":
        raise FileExistsError("Study ledger already exists; retain it and use an explicit new version")
    log = (destination / f"{args.benchmark}.log").open("w", encoding="utf-8")
    previous = "0" * 64
    versions = {}
    for package in ("openai", "httpx", "litellm", "inspect-ai", "inspect-evals", "tenacity"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    environment_packages = {}
    for distribution in importlib.metadata.distributions():
        environment_packages.setdefault(distribution.metadata["Name"], distribution.version)
    from openai._base_client import BaseClient
    # Only backoff duration is zeroed; SDK retry predicates and budgets remain.
    with path.open("w", encoding="utf-8") as ledger, patch.object(BaseClient, "_calculate_retry_timeout", lambda *_args, **_kwargs: 0):
        for index, spec in enumerate(rows):
            started = time.monotonic()
            observer = Observer()
            provider = Provider(spec["fault"], spec["sequence"], content(args.benchmark, spec["task_id"], spec["outcome"]))
            caught, timed_out = None, False
            native = {"included": False, "score": None}
            def expired(*_):
                raise Deadline()
            prior_handler = signal.signal(signal.SIGALRM, expired)
            try:
                signal.alarm(180)
                with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log), provider.serve() as url, observer.instrument():
                    try:
                        native = RUNNERS[args.benchmark](spec["task_id"], spec["outcome"], url, provider)
                    except Exception as error:
                        caught = {"chain": chain(error), "message": str(error)}
                        import traceback
                        traceback.print_exc(file=log)
            except Deadline:
                timed_out = True
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, prior_handler)
            accounted = observer.account(native) if spec["arm"] == "guarded" else native
            record = {**spec, "case_id": digest(spec), "phase": args.phase, "native": native,
                "accounted": accounted, "observer": observer.events, "injection": provider.events,
                "uncaught": caught, "watchdog": timed_out, "elapsed_seconds": round(time.monotonic() - started, 6),
                "finished_utc": datetime.now(timezone.utc).isoformat(), "previous_sha256": previous}
            record["sha256"] = digest(record)
            previous = record["sha256"]
            ledger.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
            ledger.flush()
            print(json.dumps({"benchmark": args.benchmark, "progress": f"{index+1}/{len(rows)}", "fault": spec["fault"],
                              "included": native["included"], "score": native["score"], "requests": len(provider.events),
                              "observer": len(observer.events), "error": caught["chain"] if caught else None}), flush=True)
    source_hashes = {}
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename and filename.endswith(".py") and any(marker in filename for marker in ("/vendor/", "/inspect_ai/", "/inspect_evals/", "/tau2/", "/tool_sandbox/")):
            p = Path(filename)
            if p.exists():
                source_hashes[filename] = hashlib.sha256(p.read_bytes()).hexdigest()
    (destination / f"{args.benchmark}.receipt.json").write_text(json.dumps({"versions": versions, "code_sha256": starting_code_sha256,
        "ending_code_sha256": code_hashes(),
        "environment_packages": environment_packages,
        "native_sources_sha256": source_hashes, "records": len(rows), "last_sha256": previous}, indent=2))
    if args.phase == "study":
        assert manifest["code_sha256"] == code_hashes(), "Runtime code changed during execution"
    log.close()


if __name__ == "__main__":
    main()
