"""Freeze externally-produced Day 6.5 hidden holdout without committing prompt text.

This utility is intentionally a prep/eval tool, not product code. Run it in the
independent evaluator environment that owns the hidden corpus. Only the generated
metadata JSON may be copied back into the repository/development context.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

REQUIRED_ATTESTATION = {
    "independent_evaluator": True,
    "development_model_generated": False,
    "prompt_text_committed": False,
    "prompt_text_shared_with_implementation": False,
    "frozen_before_implementation": True,
}

REQUIRED_KEYS = {
    "case_id",
    "taxonomy",
    "source_language",
    "expected_obligations",
    "expected_exclusions",
    "expected_deliverables",
    "expected_ambiguities",
    "expected_representability",
    "expected_terminal_state",
    "requires_adaptive_branch",
    "adversarial_flags",
}


def _load(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(raw.decode("utf-8"))
    elif suffix == ".json":
        data = json.loads(raw)
    elif suffix == ".jsonl":
        data = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    else:
        raise SystemExit("hidden corpus must be .yaml/.yml/.json/.jsonl")

    if isinstance(data, dict) and "cases" in data:
        data = data["cases"]
    if not isinstance(data, list):
        raise SystemExit("hidden corpus root must be a list or {cases:[...]}")

    cases: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise SystemExit(f"case[{index}] is not an object")
        missing = sorted(REQUIRED_KEYS - set(item))
        if missing:
            raise SystemExit(f"case[{index}] missing keys: {missing}")
        cases.append(item)
    return cases


def _load_attestation(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid external attestation: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit("external attestation must be a JSON object")

    if data.get("status") != "ATTESTED_EXTERNAL":
        raise SystemExit("external attestation status must be ATTESTED_EXTERNAL")

    for key, expected in REQUIRED_ATTESTATION.items():
        if data.get(key) != expected:
            raise SystemExit(
                f"external attestation {key} must be {expected!r}, got {data.get(key)!r}"
            )
    return data


def _taxonomy_values(case: dict[str, Any]) -> list[str]:
    raw = case["taxonomy"]
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list) and all(isinstance(x, str) and x for x in raw):
        return raw
    raise SystemExit(f"case {case.get('case_id')} taxonomy must be string/list[str]")


def _taxonomy_manifest(cases: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    adaptive = 0
    adversarial = 0

    for case in cases:
        counts.update(_taxonomy_values(case))
        languages[str(case["source_language"])] += 1
        adaptive += int(bool(case["requires_adaptive_branch"]))
        adversarial += int(bool(case["adversarial_flags"]))

    return {
        "case_count": len(cases),
        "taxonomy_counts": dict(sorted(counts.items())),
        "language_counts": dict(sorted(languages.items())),
        "adaptive_case_count": adaptive,
        "adversarial_case_count": adversarial,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--expected-count", type=int, default=50)
    parser.add_argument("--attestation", type=Path, required=True)
    parser.add_argument("--metadata-out", type=Path, required=True)
    args = parser.parse_args()

    raw = args.corpus.read_bytes()
    attestation_raw = args.attestation.read_bytes()
    attestation = _load_attestation(args.attestation)
    cases = _load(args.corpus)
    if len(cases) != args.expected_count:
        raise SystemExit(f"hidden case count {len(cases)} != expected {args.expected_count}")

    ids = [str(case["case_id"]) for case in cases]
    if len(ids) != len(set(ids)):
        raise SystemExit("hidden case_id values must be unique")

    taxonomy = _taxonomy_manifest(cases)
    taxonomy_bytes = json.dumps(
        taxonomy, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    metadata = {
        "status": "FROZEN_EXTERNAL",
        "case_count": len(cases),
        "corpus_sha256": hashlib.sha256(raw).hexdigest(),
        "taxonomy_sha256": hashlib.sha256(taxonomy_bytes).hexdigest(),
        "taxonomy_manifest": taxonomy,
        "attestation_sha256": hashlib.sha256(attestation_raw).hexdigest(),
        "independent_evaluator": bool(attestation["independent_evaluator"]),
        "prompt_text_committed": bool(attestation["prompt_text_committed"]),
        "prompt_text_shared_with_implementation": bool(
            attestation["prompt_text_shared_with_implementation"]
        ),
        "development_model_generated": bool(
            attestation["development_model_generated"]
        ),
        "frozen_before_implementation": bool(
            attestation["frozen_before_implementation"]
        ),
    }

    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Safe to paste back: metadata only, never corpus/prompt text.
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
