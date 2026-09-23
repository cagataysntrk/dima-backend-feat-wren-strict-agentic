"""Manual-only Day7 capability cognition diagnostic.

Purpose: classify PERFORMANCE vs ROOT_CAUSE at the exact production intent-draft
boundary without semantic grounding, Wren execution, evidence, or completion logic.

This is a diagnostic measurement, not a product gate. Behavioral mismatches are
reported in the artifact; provider/harness failures invalidate the measurement.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "eval" / "v2_day7_capability_cognition_diagnostic.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day7_capability_cognition_diagnostic.json"

os.environ.setdefault("DIMA_LLM_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_RESEARCH_MANAGER_PROVIDER", "openrouter")
os.environ["DIMA_V2_RESEARCH_MANAGER_MODEL"] = os.getenv(
    "DIMA_DAY7_LIVE_MANAGER_MODEL", "openai/gpt-5.6-sol"
)
os.environ.setdefault("DIMA_V2_SEMANTIC_LINKER_PROVIDER", "openrouter")
os.environ["DIMA_V2_SEMANTIC_LINKER_MODEL"] = os.getenv(
    "DIMA_DAY7_LIVE_LINKER_MODEL", "openai/gpt-5.6-luna"
)
os.environ.setdefault("DIMA_V2_TEMPORAL_NORMALIZER_PROVIDER", "openrouter")
os.environ["DIMA_V2_TEMPORAL_NORMALIZER_MODEL"] = os.getenv(
    "DIMA_DAY7_LIVE_TEMPORAL_MODEL", "openai/gpt-5.6-sol"
)
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")

from app.config import get_settings
from app.v2.manager_lab import _build_role_scoped_manager_models
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry
from app.v2.manager_preacceptance import PreAcceptanceController
from app.v2.source_spans import SourceSpanRegistry


def _provider_failure(message: str) -> str | None:
    text = str(message or "").lower()
    if any(x in text for x in (
        "key limit exceeded", "quota", "rate limit", "rate_limit",
        "insufficient credits", "insufficient credit", "payment required", "402",
    )):
        return "PROVIDER_QUOTA_FAILURE"
    if any(x in text for x in ("unauthorized", "invalid api key", "401", "403")):
        return "PROVIDER_AUTH_FAILURE"
    if any(x in text for x in (
        "timeout", "timed out", "service unavailable", "502", "503", "504",
        "connection error", "connection reset",
    )):
        return "PROVIDER_UNAVAILABLE"
    return None


def _analytical_required_capabilities(draft) -> list[str]:
    registry = ManagerCapabilityRegistry()
    return [
        obligation.capability_key.value
        for obligation in draft.obligations
        if obligation.polarity.value == "REQUIRED"
        and registry.get(obligation.capability_key).lane
        in {
            ManagerCapabilityLane.STANDARD,
            ManagerCapabilityLane.RESEARCH,
        }
    ]


def _controller():
    settings = get_settings()
    research_llm, research_profile, *_ = _build_role_scoped_manager_models(settings)
    structured = getattr(research_llm, "structured_json", None)
    if not callable(structured):
        raise RuntimeError("RESEARCH_MANAGER structured_json is unavailable")
    return (
        PreAcceptanceController(
            structured=structured,
            source_spans=SourceSpanRegistry(),
            capabilities=ManagerCapabilityRegistry(),
            max_draft_attempts=1,
        ),
        research_profile,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    document = yaml.safe_load(args.cases.read_text(encoding="utf-8"))
    cases = list(document.get("cases") or [])
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        controller, profile = _controller()
    except Exception as exc:
        validity = _provider_failure(str(exc)) or "HARNESS_FAILURE"
        output.write_text(json.dumps({
            "kind": "day7_capability_cognition_diagnostic",
            "measurement_validity": validity,
            "measurement_valid": False,
            "records": [],
            "error": str(exc),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 2

    records: list[dict[str, Any]] = []
    provider_failures = 0
    start_all = time.perf_counter()

    for case in cases:
        started = time.perf_counter()
        try:
            draft = controller._draft(  # diagnostic: exact production cognition boundary
                question=str(case["question"]),
                conversation=None,
                revision_feedback=None,
            )
            capabilities = _analytical_required_capabilities(draft)
            expected = str(case["expected_capability"])
            matched = capabilities == [expected]
            records.append({
                "case_id": case["id"],
                "question": case["question"],
                "expected_capability": expected,
                "actual_capabilities": capabilities,
                "pass": matched,
                "latency_s": round(time.perf_counter() - started, 4),
                "draft": draft.model_dump(mode="json"),
            })
        except Exception as exc:
            validity = _provider_failure(str(exc))
            if validity:
                provider_failures += 1
            records.append({
                "case_id": case["id"],
                "question": case["question"],
                "expected_capability": case["expected_capability"],
                "actual_capabilities": [],
                "pass": None,
                "measurement_validity": validity or "HARNESS_FAILURE",
                "error": str(exc),
                "latency_s": round(time.perf_counter() - started, 4),
            })
            if validity:
                break

    evaluable = [r for r in records if r.get("pass") is not None]
    passed = [r for r in evaluable if r["pass"] is True]
    valid = provider_failures == 0 and len(evaluable) == len(cases)
    payload = {
        "kind": "day7_capability_cognition_diagnostic",
        "corpus_version": document.get("version"),
        "measurement_valid": valid,
        "measurement_validity": "VALID" if valid else (
            next(
                (r.get("measurement_validity") for r in records if r.get("measurement_validity")),
                "HARNESS_FAILURE",
            )
        ),
        "model": getattr(profile, "model", None),
        "provider": getattr(profile, "provider", None),
        "selected_cases": len(cases),
        "evaluable_cases": len(evaluable),
        "behavior_pass_count": len(passed),
        "behavior_pass_rate": (
            round(len(passed) / len(evaluable), 4) if evaluable else None
        ),
        "mismatches": [
            {
                "case_id": r["case_id"],
                "expected": r["expected_capability"],
                "actual": r["actual_capabilities"],
            }
            for r in evaluable
            if not r["pass"]
        ],
        "total_latency_s": round(time.perf_counter() - start_all, 4),
        "records": records,
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False))
    # Behavioral mismatch is the measurement we want; it is not a harness failure.
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
