"""Live P7 language evaluator over synthetic, schema-permuted business contexts.

This evaluator deliberately does NOT inspect the repository demo database. It isolates
TurnInterpreter's natural follow-up/repair behavior from data availability. Deterministic
Day4 tests separately prove that those typed deltas preserve prior canonical IR and execute
through the real Wren boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

from app.config import get_settings
from app.llm import NoLlmGenerator, RuleBasedSqlGenerator, build_generator
from app.v2.interpreter import TurnInterpreter, TurnInterpreterError
from app.v2.models import (
    AnalyticsIR,
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    FocusStateV0,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedSemanticRef,
    ResultAnchorV0,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
    TopicFrameV0,
)

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_day4_conversation_cases.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day4_conversation_eval.json"


class CountingLlm:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def structured_text(self, system: str, user: str) -> str:
        self.calls += 1
        return self.inner.structured_text(system, user)


def _provider_names(llm) -> list[str]:
    gens = list(getattr(llm, "_gens", None) or [llm])
    return [str(getattr(g, "_provider", type(g).__name__)) for g in gens]


def _is_real_llm(llm) -> bool:
    gens = list(getattr(llm, "_gens", None) or [llm])
    return any(not isinstance(g, (RuleBasedSqlGenerator, NoLlmGenerator)) for g in gens)


def _canon(thread_id: str, prefix: str) -> str:
    digest = hashlib.sha256(f"{thread_id}:{prefix}".encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def _context(thread: dict) -> tuple[BoundedSemanticContextV0, dict]:
    tid = str(thread["id"])
    names = {
        "cube": _canon(tid, "cube"),
        "metric": _canon(tid, "metric"),
        "dimension": _canon(tid, "dimension"),
        "time": _canon(tid, "time"),
    }
    version = ContextVersionV0(
        version=_canon(tid, "ctx"),
        mdl_version=_canon(tid, "mdl"),
        compact_catalog_builder_version="day4-live-synthetic-v1",
        business_rules_hash=hashlib.sha256(b"").hexdigest(),
        prompt_context_policy_version="day4-live-synthetic-v1",
    )
    context = BoundedSemanticContextV0(
        context_version=version,
        cubes=(
            CompactCubeContextV0(
                canonical_name=names["cube"],
                display=str(thread["cube_display"]),
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name=names["metric"],
                        display=str(thread["metric_display"]),
                        synonyms=tuple(str(x) for x in thread.get("metric_synonyms") or ()),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name=names["dimension"],
                        display=str(thread["dimension_display"]),
                        synonyms=tuple(str(x) for x in thread.get("dimension_synonyms") or ()),
                    ),
                ),
                time_dimensions=(names["time"],),
            ),
        ),
        kpis=(),
        relationships=(),
        approved_business_rules="",
        business_rules_truncated=False,
    )
    return context, names


def _period(kind: str, source: str, time_dimension: str) -> ResolvedPeriod:
    if kind == "this_year":
        return ResolvedPeriod(
            kind="this_year",
            source_text=source,
            time_dimension=time_dimension,
            start="2026-01-01",
            end="2026-09-21",
        )
    if kind == "last_n_months":
        return ResolvedPeriod(
            kind="last_n_months",
            source_text=source,
            time_dimension=time_dimension,
            start="2026-06-21",
            end="2026-09-21",
            n=3,
        )
    raise ValueError(kind)


def _conversation(thread: dict, names: dict, turn_index: int) -> ConversationStateV2:
    """Expected pre-turn state; avoids cascading one model error into the next case."""
    if turn_index == 0:
        return ConversationStateV2()

    metric = ResolvedSemanticRef(
        candidate_id=_canon(str(thread["id"]), "metric-candidate"),
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=names["metric"],
        cube_names=(names["cube"],),
    )
    dimension = ResolvedSemanticRef(
        candidate_id=_canon(str(thread["id"]), "dimension-candidate"),
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=names["dimension"],
        cube_names=(names["cube"],),
    )
    period = _period("this_year", "bu yıl", names["time"])
    filters = ()

    if turn_index >= 2:
        filters = (
            ResolvedFilterRef(
                candidate_id=_canon(str(thread["id"]), "entity-candidate"),
                dimension_name=names["dimension"],
                value=str(thread["entity"]),
                cube_names=(names["cube"],),
            ),
        )

    if turn_index >= 3:
        period = _period("last_n_months", "son üç ay", names["time"])

    ir = AnalyticsIR(
        cube=names["cube"],
        metrics=(metric,),
        dimensions=(dimension,),
        filters=filters,
        period=period,
        context_version=_canon(str(thread["id"]), "ctx"),
    )
    active_result = turn_index >= 3
    return ConversationStateV2(
        has_prior_analytical_request=True,
        has_active_result=active_result,
        topic_labels=(str(thread["cube_display"]),),
        focus_labels=(
            str(thread["metric_display"]),
            str(thread["dimension_display"]),
        ),
        topic=TopicFrameV0(
            topic_id=_canon(str(thread["id"]), "topic"),
            cube=names["cube"],
            context_version=ir.context_version,
        ),
        focus=FocusStateV0(
            metrics=ir.metrics,
            dimensions=ir.dimensions,
            filters=ir.filters,
            period=ir.period,
            last_contract_refs=("c-synthetic",) if active_result else (),
        ),
        last_ir=ir,
        last_result=(
            ResultAnchorV0(
                contract_refs=("c-synthetic",),
                result_hashes=("synthetic-hash",),
                executions=(),
                verified=True,
            )
            if active_result
            else None
        ),
    )


def _slots(turn) -> set[str]:
    request = turn.analytical_request
    out: set[str] = set()
    if request is None:
        return out
    if request.metric_mentions:
        out.add("metric")
    if request.dimension_mentions:
        out.add("dimension")
    if request.filter_mentions:
        out.add("filter")
    if request.time_mentions:
        out.add("time")
    if request.ranking is not None:
        out.add("ranking")
    if request.comparisons:
        out.add("comparison")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()

    threads = yaml.safe_load(CASES.read_text(encoding="utf-8"))["threads"]
    llm = build_generator(get_settings())
    providers = _provider_names(llm)

    if not _is_real_llm(llm):
        payload = {
            "kind": "dima_v2_day4_conversation_eval",
            "status": "live_provider_unavailable",
            "providers": providers,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2 if args.require_live else 0

    interpreter = TurnInterpreter()
    records = []
    structured_ok = 0
    act_ok = 0
    followup_ok = 0
    followup_total = 0
    repair_preservation_ok = 0
    repair_total = 0
    explain_ok = 0
    explain_total = 0
    social_ok = 0
    social_total = 0
    surface_violations = 0
    total_calls = 0
    max_calls = 0

    for thread in threads:
        context, names = _context(thread)
        for index, case in enumerate(thread["turns"]):
            counting = CountingLlm(llm)
            expected_slots = set(case.get("expected_slots") or ())
            conversation = _conversation(thread, names, index)
            try:
                turn = interpreter.interpret(
                    question=str(case["q"]),
                    semantic_context=context,
                    conversation=conversation,
                    llm=counting,
                )
                structured_ok += 1
                actual_slots = _slots(turn)
                act_correct = turn.dialogue_act.value == case["expected_act"]
                slot_correct = actual_slots == expected_slots
                act_ok += int(act_correct)

                if index in (1, 2):
                    followup_total += 1
                    followup_ok += int(act_correct and slot_correct)

                if case["expected_act"] == "USER_REPAIR":
                    repair_total += 1
                    preservation = (
                        act_correct
                        and slot_correct
                        and actual_slots == {"time"}
                        and turn.user_repair is not None
                    )
                    repair_preservation_ok += int(preservation)

                if case["expected_act"] == "RESULT_EXPLAIN":
                    explain_total += 1
                    explain_ok += int(act_correct and not actual_slots)

                if case["expected_act"] == "SOCIAL":
                    social_total += 1
                    social_ok += int(act_correct and not actual_slots)

                record = {
                    "thread": thread["id"],
                    "turn": index + 1,
                    "question": case["q"],
                    "expected_act": case["expected_act"],
                    "actual_act": turn.dialogue_act.value,
                    "expected_slots": sorted(expected_slots),
                    "actual_slots": sorted(actual_slots),
                    "act_correct": act_correct,
                    "slot_correct": slot_correct,
                    "structured_success": True,
                    "calls": counting.calls,
                    "failure": None,
                }
            except TurnInterpreterError as exc:
                if exc.failure.code == "surface_grounding_violation":
                    surface_violations += 1
                if index in (1, 2):
                    followup_total += 1
                if case["expected_act"] == "USER_REPAIR":
                    repair_total += 1
                if case["expected_act"] == "RESULT_EXPLAIN":
                    explain_total += 1
                if case["expected_act"] == "SOCIAL":
                    social_total += 1
                record = {
                    "thread": thread["id"],
                    "turn": index + 1,
                    "question": case["q"],
                    "expected_act": case["expected_act"],
                    "actual_act": None,
                    "expected_slots": sorted(expected_slots),
                    "actual_slots": [],
                    "act_correct": False,
                    "slot_correct": False,
                    "structured_success": False,
                    "calls": counting.calls,
                    "failure": exc.failure.model_dump(mode="json"),
                }

            total_calls += counting.calls
            max_calls = max(max_calls, counting.calls)
            records.append(record)

    n = len(records)
    structured_rate = structured_ok / n if n else 0.0
    act_accuracy = act_ok / n if n else 0.0
    followup_correctness = followup_ok / followup_total if followup_total else 0.0
    repair_preservation = (
        repair_preservation_ok / repair_total if repair_total else 0.0
    )
    explain_rate = explain_ok / explain_total if explain_total else 0.0
    social_rate = social_ok / social_total if social_total else 0.0

    passed = (
        structured_rate >= 0.99
        and act_accuracy >= 0.95
        and followup_correctness >= 0.90
        and repair_preservation == 1.0
        and explain_rate == 1.0
        and social_rate == 1.0
        and surface_violations == 0
        and max_calls <= 2
    )

    payload = {
        "kind": "dima_v2_day4_conversation_eval",
        "status": "pass" if passed else "fail",
        "source_policy": "synthetic_schema_permuted_no_demo_db",
        "providers": providers,
        "threads": len(threads),
        "n": n,
        "structured_success_rate": round(structured_rate, 4),
        "turn_act_accuracy": round(act_accuracy, 4),
        "followup_correctness": round(followup_correctness, 4),
        "repair_slot_preservation": round(repair_preservation, 4),
        "result_explain_classification": round(explain_rate, 4),
        "social_classification": round(social_rate, 4),
        "surface_grounding_violations": surface_violations,
        "total_llm_calls": total_calls,
        "max_calls_per_case": max_calls,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        "Day4 live eval: "
        f"n={n} structured={structured_rate:.1%} act={act_accuracy:.1%} "
        f"followup={followup_correctness:.1%} repair={repair_preservation:.1%} "
        f"explain={explain_rate:.1%} social={social_rate:.1%} "
        f"status={payload['status']}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
