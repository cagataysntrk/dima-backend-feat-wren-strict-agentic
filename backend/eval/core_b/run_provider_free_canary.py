#!/usr/bin/env python3
"""Run the frozen Core-B provider-free canary as exact pytest nodes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--candidate-sha",default=os.environ.get("GITHUB_SHA","LOCAL"))
    args=ap.parse_args()

    body=json.loads(args.manifest.read_text(encoding="utf-8"))
    if not 8 <= int(body["case_count"]) <= 16:
        raise RuntimeError("provider-free canary must remain 8..16 cases")
    if body.get("live_model_calls") != 0 or body.get("external_side_effects") != 0:
        raise RuntimeError("provider-free canary budget drift")

    results=[]
    for case in body["cases"]:
        started=time.monotonic()
        proc=subprocess.run(
            [sys.executable,"-m","pytest","-q",case["node"]],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        elapsed=max(0,int((time.monotonic()-started)*1000))
        results.append({
            "case_id":case["id"],
            "node":case["node"],
            "pass":proc.returncode==0,
            "duration_ms":elapsed,
            "output_tail":"\n".join(proc.stdout.splitlines()[-12:]),
        })

    receipt={
        "schema_version":"core_b_provider_free_canary_receipt_v1",
        "candidate_sha":args.candidate_sha,
        "manifest_path":str(args.manifest),
        "manifest_fingerprint":sha256(args.manifest),
        "case_count":len(results),
        "passed":sum(1 for item in results if item["pass"]),
        "failed":sum(1 for item in results if not item["pass"]),
        "live_model_calls":0,
        "external_side_effects":0,
        "cases":results,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return 0 if receipt["failed"]==0 else 1


if __name__=="__main__":
    raise SystemExit(main())
