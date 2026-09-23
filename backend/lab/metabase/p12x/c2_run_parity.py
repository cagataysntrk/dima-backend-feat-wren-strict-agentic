#!/usr/bin/env python3
"""Run the bounded P12X-C2 direct-native vs typed-bridge parity experiment."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

CASES = ("PX-01", "PX-07", "PX-13", "PX-16")
REPEATS = 2


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain object")
    return value


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def question_for(corpus: dict[str, Any], case_id: str) -> str:
    rows = [x for x in corpus.get("cases") or [] if x.get("id") == case_id]
    if len(rows) != 1:
        raise RuntimeError(f"case not found: {case_id}")
    return str(rows[0]["question"])


def direct_probe(
    *,
    here: Path,
    base_url: str,
    email: str,
    password: str,
    case_id: str,
    question: str,
    output: Path,
) -> None:
    run([
        sys.executable,
        str(here / "c1_probe.py"),
        "--base-url", base_url,
        "--email", email,
        "--password", password,
        "--question", question,
        "--case-id", case_id,
        "--runtime-label", "fork",
        "--output", str(output),
    ])


def bridge_probe(
    *,
    here: Path,
    base_url: str,
    email: str,
    password: str,
    case_id: str,
    question: str,
    engine_sha: str,
    upstream_base_sha: str,
    output: Path,
) -> None:
    run([
        sys.executable,
        str(here / "c2_bridge_probe.py"),
        "--base-url", base_url,
        "--email", email,
        "--password", password,
        "--question", question,
        "--case-id", case_id,
        "--engine-sha", engine_sha,
        "--upstream-base-sha", upstream_base_sha,
        "--output", str(output),
    ])


def score(
    *,
    here: Path,
    oracle: Path,
    output_root: Path,
    phase: str,
) -> Path:
    output = output_root / ("C2_DISCOVERY.json" if phase == "discover" else "C2_FINAL.json")
    cmd = [
        sys.executable,
        str(here / "c2_score_bridge_parity.py"),
        "--cases", str(here / "c2_cases.json"),
        "--oracle", str(oracle),
        "--direct-dir", str(output_root / "direct"),
        "--bridge-dir", str(output_root / "bridge"),
        "--phase", phase,
        "--output", str(output),
    ]
    if phase == "final":
        cmd.extend(["--repeat-root", str(output_root / "repeats")])
    run(cmd)
    return output


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--oracle", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-base-sha", required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    corpus = load(here / "corpus_v1.json")
    root = args.output_root.resolve()
    for path in (
        root / "direct",
        root / "bridge",
        root / "repeats" / "direct",
        root / "repeats" / "bridge",
    ):
        path.mkdir(parents=True, exist_ok=True)

    for case_id in CASES:
        question = question_for(corpus, case_id)
        direct_probe(
            here=here,
            base_url=args.base_url,
            email=args.email,
            password=args.password,
            case_id=case_id,
            question=question,
            output=root / "direct" / f"{case_id}.json",
        )
        bridge_probe(
            here=here,
            base_url=args.base_url,
            email=args.email,
            password=args.password,
            case_id=case_id,
            question=question,
            engine_sha=args.engine_sha,
            upstream_base_sha=args.upstream_base_sha,
            output=root / "bridge" / f"{case_id}.json",
        )

    discovery_path = score(here=here, oracle=args.oracle, output_root=root, phase="discover")
    discovery = load(discovery_path)
    divergent = list(discovery.get("divergent_case_ids") or [])

    for case_id in divergent:
        question = question_for(corpus, case_id)
        for attempt in range(1, REPEATS + 1):
            direct_probe(
                here=here,
                base_url=args.base_url,
                email=args.email,
                password=args.password,
                case_id=case_id,
                question=question,
                output=root / "repeats" / "direct" / f"{case_id}-{attempt}.json",
            )
            bridge_probe(
                here=here,
                base_url=args.base_url,
                email=args.email,
                password=args.password,
                case_id=case_id,
                question=question,
                engine_sha=args.engine_sha,
                upstream_base_sha=args.upstream_base_sha,
                output=root / "repeats" / "bridge" / f"{case_id}-{attempt}.json",
            )

    final_path = score(here=here, oracle=args.oracle, output_root=root, phase="final")
    final = load(final_path)
    print(json.dumps({
        "status": final.get("status"),
        "closure": final.get("closure"),
    }, ensure_ascii=False, indent=2))
    return 0 if final.get("status") == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
