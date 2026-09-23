#!/usr/bin/env python3
"""C1-only resilient wrapper around native_probe.py.

A single runtime/case transport failure is benchmark evidence, not a reason to abort the
entire stock-vs-fork experiment. Successful probes remain owned by native_probe.py unchanged.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def classify(stderr: str) -> str:
    if "ReadTimeout" in stderr or "read timeout" in stderr.lower():
        return "TRANSPORT_READ_TIMEOUT"
    if "ConnectTimeout" in stderr or "connect timeout" in stderr.lower():
        return "TRANSPORT_CONNECT_TIMEOUT"
    if "HTTPStatusError" in stderr:
        return "HTTP_STATUS_ERROR"
    if "ConnectError" in stderr:
        return "TRANSPORT_CONNECT_ERROR"
    return "PROBE_PROCESS_FAILURE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--question", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--runtime-label", choices=["stock", "fork"], required=True)
    args = ap.parse_args()

    native_probe = Path(__file__).with_name("native_probe.py")
    started = time.perf_counter()
    proc = subprocess.run(
        [
            sys.executable,
            str(native_probe),
            "--base-url", args.base_url,
            "--email", args.email,
            "--password", args.password,
            "--question", args.question,
            "--output", str(args.output),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if proc.stdout:
        print(proc.stdout, end="")
    if proc.returncode == 0:
        if not args.output.exists():
            raise SystemExit("native_probe returned 0 without writing its artifact")
        return 0

    elapsed = round(time.perf_counter() - started, 6)
    stderr_tail = proc.stderr[-6000:]
    failure_class = classify(stderr_tail)
    artifact: dict[str, Any] = {
        "status_code": None,
        "case_id": args.case_id,
        "runtime_label": args.runtime_label,
        "question": args.question,
        "latency_seconds": elapsed,
        "session_version_fields": {},
        "metabot_permissions": {},
        "catalog_probe": None,
        "answer_text": "",
        "tool_calls": [],
        "tool_results": [],
        "data_parts": [],
        "errors": [{
            "type": "c1_probe_process_failure",
            "failure_class": failure_class,
            "return_code": proc.returncode,
            "stderr_tail": stderr_tail,
        }],
        "finish": None,
        "final_state": None,
        "generated_query": None,
        "generated_query_dataset_result": None,
        "raw_line_count": 0,
        "probe_process_failure": {
            "failure_class": failure_class,
            "return_code": proc.returncode,
            "stderr_tail": stderr_tail,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "case_id": args.case_id,
        "runtime_label": args.runtime_label,
        "captured_failure": failure_class,
        "latency_seconds": elapsed,
        "artifact": str(args.output),
    }, ensure_ascii=False, indent=2))
    # Candidate-level failure is now represented in the artifact. The C1 scorer owns pass/fail.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
