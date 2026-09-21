"""Day 6.5 pre-implementation gate.

This module contains no Manager product logic. It only answers whether the external
hidden architecture holdout has been frozen strongly enough to unlock production
Manager implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "eval" / "v2_day6_5_eval_manifest.yaml"

PLACEHOLDER = "REQUIRED_BEFORE_IMPLEMENTATION"


@dataclass(frozen=True)
class Day65Preflight:
    ready: bool
    status: str
    case_count: int
    corpus_sha256: str
    taxonomy_sha256: str
    attestation_sha256: str
    blockers: tuple[str, ...]


def _manifest() -> dict[str, Any]:
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Day6.5 eval manifest object değil")
    return data


def evaluate_day65_preflight() -> Day65Preflight:
    data = _manifest()
    hidden = ((data.get("corpus_target") or {}).get("hidden_holdout") or {})
    expected_count = int(hidden.get("count") or 0)
    corpus_sha = str(hidden.get("sha256") or "")
    taxonomy_sha = str(hidden.get("taxonomy_sha256") or "")
    attestation_sha = str(hidden.get("attestation_sha256") or "")
    attestation = hidden.get("external_attestation") or {}

    blockers: list[str] = []
    if expected_count != 50:
        blockers.append(f"hidden case_count 50 değil: {expected_count}")
    if not corpus_sha or corpus_sha == PLACEHOLDER:
        blockers.append("external hidden corpus sha256 freeze edilmedi")
    if not taxonomy_sha or taxonomy_sha == PLACEHOLDER:
        blockers.append("external hidden taxonomy sha256 freeze edilmedi")
    if not attestation_sha or attestation_sha == PLACEHOLDER:
        blockers.append("external hidden attestation sha256 freeze edilmedi")

    expected_attestation = {
        "independent_evaluator": True,
        "prompt_text_committed": False,
        "prompt_text_shared_with_implementation": False,
        "development_model_generated": False,
        "frozen_before_implementation": True,
    }
    if not isinstance(attestation, dict):
        blockers.append("external hidden attestation manifest object değil")
    else:
        for key, expected in expected_attestation.items():
            if attestation.get(key) != expected:
                blockers.append(
                    f"external hidden attestation {key} beklenen {expected!r} değil"
                )
    if bool(hidden.get("committed_to_repo", True)):
        blockers.append("hidden prompt corpus repo içine commit edilebilir görünüyor")
    if bool(hidden.get("generated_by_current_development_model", True)):
        blockers.append("hidden corpus development model tarafından üretilmiş görünüyor")
    if not bool(hidden.get("required_before_manager_implementation", False)):
        blockers.append("pre-implementation holdout gate manifestte zorunlu değil")

    return Day65Preflight(
        ready=not blockers,
        status="READY" if not blockers else "BLOCKED",
        case_count=expected_count,
        corpus_sha256=corpus_sha,
        taxonomy_sha256=taxonomy_sha,
        attestation_sha256=attestation_sha,
        blockers=tuple(blockers),
    )


def require_day65_preflight() -> Day65Preflight:
    result = evaluate_day65_preflight()
    if not result.ready:
        joined = "; ".join(result.blockers)
        raise RuntimeError(f"Day6.5 Manager implementation LOCKED: {joined}")
    return result


if __name__ == "__main__":
    result = evaluate_day65_preflight()
    print(
        yaml.safe_dump(
            {
                "status": result.status,
                "ready": result.ready,
                "case_count": result.case_count,
                "corpus_sha256": result.corpus_sha256,
                "taxonomy_sha256": result.taxonomy_sha256,
                "attestation_sha256": result.attestation_sha256,
                "blockers": list(result.blockers),
            },
            allow_unicode=True,
            sort_keys=False,
        ).strip()
    )
    raise SystemExit(0 if result.ready else 2)
