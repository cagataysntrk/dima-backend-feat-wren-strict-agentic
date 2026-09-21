"""Minimal paid P9 language-owner gate.

Eight cases only. This script measures ResearchBrief goal extraction, not data execution.
It builds a synthetic/permuted semantic context, calls TurnInterpreter once per case
(with the existing single format-only retry ceiling), and never invokes Resolver/Wren.
"""

from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path

import yaml

from app.config import get_settings
from app.llm import NoLlmGenerator, RuleBasedSqlGenerator, build_v2_interpreter_generator
from app.v2.interpreter import TurnInterpreter, TurnInterpreterError
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    PresentationKind,
)

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_day6_research_cases.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day6_research_eval.json"


class CountingLlm:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def structured_text(self, system: str, user: str) -> str:
        self.calls += 1
        return self.inner.structured_text(system, user)


def _provider_names(llm) -> list[str]:
    gens = list(getattr(llm, "_gens", None) or [llm])
    return [
        str(getattr(g, "_model", None) or getattr(g, "_provider", type(g).__name__))
        for g in gens
    ]


def _is_real_llm(llm) -> bool:
    gens = list(getattr(llm, "_gens", None) or [llm])
    return any(not isinstance(g, (RuleBasedSqlGenerator, NoLlmGenerator)) for g in gens)


def _norm(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.casefold().replace("\u0307", "").split())


def _context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-day6-language-holdout",
            mdl_version="mdl-day6-language-holdout",
            compact_catalog_builder_version="day6-eval-v1",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="day6-eval-v1",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="cube_p17",
                display="Üretim Alanı",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="measure_q91",
                        display="Üretim Performansı",
                        synonyms=("üretim", "üretim performansı"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="axis_a31",
                        display="Ürün",
                        synonyms=("ürün", "ürünler"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="axis_b42",
                        display="Makine",
                        synonyms=("makine", "makineler"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="axis_c53",
                        display="Personel",
                        synonyms=("personel", "çalışan"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="axis_d64",
                        display="Vardiya",
                        synonyms=("vardiya",),
                    ),
                ),
                time_dimensions=("time_t75",),
            ),
            CompactCubeContextV0(
                canonical_name="cube_s28",
                display="Ticari Alan",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="measure_r82",
                        display="Satış Performansı",
                        synonyms=("satış", "satış performansı"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="axis_e86",
                        display="Ürün",
                        synonyms=("ürün", "ürünler"),
                    ),
                ),
                time_dimensions=("time_u97",),
            ),
        ),
        approved_business_rules="",
        business_rules_truncated=False,
    )


def _research_semantic_surfaces(turn) -> list[str]:
    request = turn.research_request
    if request is None:
        return []
    out: list[str] = []
    for goal in request.goals:
        out.extend(item.text for item in goal.subject_mentions)
        out.extend(item.text for item in goal.related_mentions)
    return out


def _has_fragment(values: list[str], fragment: str) -> bool:
    needle = _norm(fragment)
    return any(needle in _norm(value) for value in values)


def _forbidden_schema_leak(turn) -> bool:
    request = turn.research_request
    if request is None:
        return False

    forbidden = {"canonical_name", "candidate_id", "cube_names", "dimension_name"}

    def walk(value) -> bool:
        if isinstance(value, dict):
            if forbidden.intersection(value):
                return True
            return any(walk(item) for item in value.values())
        if isinstance(value, list):
            return any(walk(item) for item in value)
        return False

    return walk(request.model_dump(mode="json"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()

    cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))["cases"]
    llm = build_v2_interpreter_generator(get_settings())
    providers = _provider_names(llm)

    if not _is_real_llm(llm):
        payload = {
            "kind": "dima_v2_day6_research_language_eval",
            "status": "live_provider_unavailable",
            "providers": providers,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(payload, ensure_ascii=False))
        return 2 if args.require_live else 0

    interpreter = TurnInterpreter()
    context = _context()
    records = []

    expected_goal_total = 0
    covered_goal_total = 0
    expected_anchor_total = 0
    covered_anchor_total = 0
    invented_goal_total = 0
    forbidden_fragment_hits = 0
    canonical_pass = False
    simple_negative_pass = False
    surface_violations = 0
    total_calls = 0
    max_calls = 0

    for case in cases:
        counting = CountingLlm(llm)
        expected_act = str(case["expected_act"])
        expect_research = bool(case.get("expect_research", True))
        expected_counts = Counter(
            {str(k): int(v) for k, v in (case.get("expected_goal_counts") or {}).items()}
        )
        required_fragments = [str(x) for x in case.get("required_fragments") or ()]
        required_time = [str(x) for x in case.get("required_time_fragments") or ()]
        forbidden_fragments = [str(x) for x in case.get("forbidden_fragments") or ()]

        failure = None
        try:
            turn = interpreter.interpret(
                question=str(case["q"]),
                semantic_context=context,
                conversation=ConversationStateV2(),
                llm=counting,
            )
            request = turn.research_request
            actual_counts = Counter(
                goal.kind.value for goal in request.goals
            ) if request is not None else Counter()
            surfaces = _research_semantic_surfaces(turn)
            time_surfaces = (
                [item.text for item in request.time_mentions]
                if request is not None
                else []
            )

            act_ok = turn.dialogue_act.value == expected_act
            research_shape_ok = (request is not None) == expect_research
            count_exact = actual_counts == expected_counts
            fragment_results = {
                fragment: _has_fragment(surfaces, fragment)
                for fragment in required_fragments
            }
            time_results = {
                fragment: _has_fragment(time_surfaces, fragment)
                for fragment in required_time
            }
            forbidden_results = {
                fragment: _has_fragment(surfaces, fragment)
                for fragment in forbidden_fragments
            }
            schema_leak = _forbidden_schema_leak(turn)
            report_contract_ok = True
            if expected_counts.get("deliverable", 0):
                report_contract_ok = (
                    turn.presentation_request == PresentationKind.REPORT
                    and request is not None
                    and any(
                        goal.kind.value == "deliverable"
                        and goal.deliverable == PresentationKind.REPORT
                        for goal in request.goals
                    )
                )

            expected_goal_total += sum(expected_counts.values())
            covered_goal_total += sum(
                min(expected_counts[kind], actual_counts[kind])
                for kind in expected_counts
            )
            invented_goal_total += sum(
                max(actual_counts[kind] - expected_counts[kind], 0)
                for kind in actual_counts
            )
            expected_anchor_total += len(required_fragments)
            covered_anchor_total += sum(fragment_results.values())
            forbidden_fragment_hits += sum(forbidden_results.values())

            case_pass = (
                act_ok
                and research_shape_ok
                and count_exact
                and all(fragment_results.values())
                and all(time_results.values())
                and not any(forbidden_results.values())
                and not schema_leak
                and report_contract_ok
            )

            if case["id"] == "canonical":
                canonical_pass = case_pass
            if case["id"] == "simple_not_research":
                simple_negative_pass = case_pass

            record = {
                "id": case["id"],
                "question": case["q"],
                "expected_act": expected_act,
                "actual_act": turn.dialogue_act.value,
                "expected_goal_counts": dict(expected_counts),
                "actual_goal_counts": dict(actual_counts),
                "required_fragment_results": fragment_results,
                "required_time_results": time_results,
                "forbidden_fragment_results": forbidden_results,
                "research_shape_ok": research_shape_ok,
                "report_contract_ok": report_contract_ok,
                "canonical_schema_leak": schema_leak,
                "case_pass": case_pass,
                "calls": counting.calls,
                "failure": None,
            }
        except TurnInterpreterError as exc:
            if exc.failure.code == "surface_grounding_violation":
                surface_violations += 1
            expected_goal_total += sum(expected_counts.values())
            expected_anchor_total += len(required_fragments)
            failure = exc.failure.model_dump(mode="json")
            record = {
                "id": case["id"],
                "question": case["q"],
                "expected_act": expected_act,
                "actual_act": None,
                "expected_goal_counts": dict(expected_counts),
                "actual_goal_counts": {},
                "required_fragment_results": {
                    fragment: False for fragment in required_fragments
                },
                "required_time_results": {
                    fragment: False for fragment in required_time
                },
                "forbidden_fragment_results": {},
                "research_shape_ok": False,
                "report_contract_ok": False,
                "canonical_schema_leak": False,
                "case_pass": False,
                "calls": counting.calls,
                "failure": failure,
            }

        total_calls += counting.calls
        max_calls = max(max_calls, counting.calls)
        records.append(record)

    goal_coverage = (
        covered_goal_total / expected_goal_total if expected_goal_total else 1.0
    )
    anchor_coverage = (
        covered_anchor_total / expected_anchor_total if expected_anchor_total else 1.0
    )
    passed = (
        canonical_pass
        and goal_coverage >= 0.95
        and anchor_coverage >= 0.95
        and invented_goal_total == 0
        and forbidden_fragment_hits == 0
        and simple_negative_pass
        and surface_violations == 0
        and max_calls <= 2
    )

    payload = {
        "kind": "dima_v2_day6_research_language_eval",
        "status": "pass" if passed else "fail",
        "source_policy": "synthetic_permuted_context_no_data_query",
        "providers": providers,
        "case_count": len(cases),
        "canonical_complex_goal_extraction": bool(canonical_pass),
        "complex_validation_goal_coverage": round(goal_coverage, 4),
        "semantic_anchor_surface_coverage": round(anchor_coverage, 4),
        "invented_goal_count": invented_goal_total,
        "forbidden_fragment_hits": forbidden_fragment_hits,
        "surface_grounding_violations": surface_violations,
        "simple_non_research_negative": bool(simple_negative_pass),
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
        "Day6 research language eval: "
        f"cases={len(cases)} goals={goal_coverage:.1%} anchors={anchor_coverage:.1%} "
        f"invented={invented_goal_total} calls={total_calls} status={payload['status']}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
