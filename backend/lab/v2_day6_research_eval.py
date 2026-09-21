"""Manual P9 language + ResearchBrief gate.

This is intentionally NOT auto-triggered. It exercises the paid language owner only,
then continues through the real deterministic SemanticResolver and ResearchBriefBuilder.
No Wren query, dry-plan, research tool, or database execution occurs.
"""

from __future__ import annotations

import argparse
import json
import unicodedata
from functools import lru_cache
from pathlib import Path

import yaml

from app.config import get_settings
from app.llm import NoLlmGenerator, RuleBasedSqlGenerator, build_generator
from app.v2.interpreter import TurnInterpreter, TurnInterpreterError
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactRelationshipV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    PresentationKind,
    ResearchBriefStatus,
)
from app.v2.research import ResearchBriefBuilder
from app.v2.resolver import SemanticResolver

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


def _contains(values: list[str], fragment: str) -> bool:
    needle = _norm(fragment)
    return any(needle in _norm(value) for value in values)


def _context() -> BoundedSemanticContextV0:
    product = CompactSemanticFieldV0(
        canonical_name="axis_product_shared",
        display="Ürün",
        synonyms=("ürün", "ürünler", "urun", "urunler"),
    )
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-day6-manual-gate-v2",
            mdl_version="mdl-day6-manual-gate-v2",
            compact_catalog_builder_version="day6-eval-v2",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="day6-eval-v2",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="cube_prod_p17",
                display="Üretim Alanı",
                synonyms=("üretim",),
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="metric_prod_perf_q91",
                        display="Üretim Performansı",
                        synonyms=("üretim performansı", "üretim performansi"),
                    ),
                ),
                dimensions=(
                    product,
                    CompactSemanticFieldV0(
                        canonical_name="axis_machine_b42",
                        display="Makine",
                        synonyms=("makine", "makineler", "tezgah", "ekipman"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="axis_personnel_c53",
                        display="Personel",
                        synonyms=("personel", "personeller", "çalışan", "çalışanlar", "calisan"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="axis_shift_d64",
                        display="Vardiya",
                        synonyms=("vardiya", "vardiyalar"),
                    ),
                ),
                time_dimensions=("time_prod_t75",),
            ),
            CompactCubeContextV0(
                canonical_name="cube_sales_s28",
                display="Satış Alanı",
                synonyms=("satış", "satis"),
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="metric_sales_r82",
                        display="Satış Performansı",
                        synonyms=(
                            "satış performansı",
                            "satis performansi",
                            "sales performance",
                            "satış",
                            "satis",
                        ),
                    ),
                ),
                dimensions=(product,),
                time_dimensions=("time_sales_u97",),
            ),
            CompactCubeContextV0(
                canonical_name="cube_energy_e39",
                display="Enerji Alanı",
                synonyms=("enerji",),
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="metric_energy_v18",
                        display="Enerji Tüketimi",
                        synonyms=("enerji tüketimi", "enerji tuketimi"),
                    ),
                ),
                dimensions=(),
                time_dimensions=("time_energy_w19",),
            ),
        ),
        relationships=(
            # Semantic availability only. Day 7 still owns executable join/grain proof.
            CompactRelationshipV0(
                name="rel_prod_sales",
                cube_names=("cube_prod_p17", "cube_sales_s28"),
                certified="verified",
            ),
        ),
        approved_business_rules="",
        business_rules_truncated=False,
    )


def _schema() -> dict:
    return {
        "models": [],
        "cubes": [
            {"name": "cube_prod_p17", "dimension_values": {}},
            {"name": "cube_sales_s28", "dimension_values": {}},
            {"name": "cube_energy_e39", "dimension_values": {}},
        ],
        "company_vocabulary": [],
    }


def _goal_surface_values(goal) -> tuple[list[str], list[str], list[str]]:
    subject = [item.text for item in goal.subject_mentions]
    related = [item.text for item in goal.related_mentions]
    all_values = [goal.text, *subject, *related]
    return subject, related, all_values


def _signature_matches(signature: dict, goal) -> bool:
    if goal.kind.value != str(signature["kind"]):
        return False
    subject, related, _ = _goal_surface_values(goal)
    if not all(_contains(subject, str(fragment)) for fragment in signature.get("subject") or ()):
        return False
    if not all(_contains(related, str(fragment)) for fragment in signature.get("related") or ()):
        return False
    return True


def _deliverable_signature_matches(signature: dict, deliverable) -> bool:
    expected = str(signature.get("deliverable") or "")
    return bool(expected) and deliverable.kind.value == expected


def _maximum_signature_match(signatures: list[dict], goals: tuple) -> tuple[int, list[tuple[int, int]]]:
    """Maximum bipartite match; catches repeated wrong goals and silent goal loss."""

    @lru_cache(maxsize=None)
    def solve(index: int, used_mask: int) -> tuple[int, tuple[tuple[int, int], ...]]:
        if index >= len(signatures):
            return 0, ()

        best_count, best_pairs = solve(index + 1, used_mask)
        for goal_index, goal in enumerate(goals):
            if used_mask & (1 << goal_index):
                continue
            if not _signature_matches(signatures[index], goal):
                continue
            count, pairs = solve(index + 1, used_mask | (1 << goal_index))
            count += 1
            candidate_pairs = ((index, goal_index), *pairs)
            if count > best_count:
                best_count, best_pairs = count, candidate_pairs
        return best_count, best_pairs

    count, pairs = solve(0, 0)
    return count, list(pairs)


def _maximum_deliverable_match(
    signatures: list[dict],
    deliverables: tuple,
) -> tuple[int, list[tuple[int, int]]]:
    @lru_cache(maxsize=None)
    def solve(index: int, used_mask: int) -> tuple[int, tuple[tuple[int, int], ...]]:
        if index >= len(signatures):
            return 0, ()
        best_count, best_pairs = solve(index + 1, used_mask)
        for item_index, item in enumerate(deliverables):
            if used_mask & (1 << item_index):
                continue
            if not _deliverable_signature_matches(signatures[index], item):
                continue
            count, pairs = solve(index + 1, used_mask | (1 << item_index))
            count += 1
            candidate_pairs = ((index, item_index), *pairs)
            if count > best_count:
                best_count, best_pairs = count, candidate_pairs
        return best_count, best_pairs

    count, pairs = solve(0, 0)
    return count, list(pairs)


def _time_coverage(request, expected: list[str]) -> dict[str, bool]:
    values = [item.text for item in request.time_mentions] if request is not None else []
    return {fragment: _contains(values, fragment) for fragment in expected}


def _forbidden_goal_hits(request, forbidden: list[str]) -> dict[str, bool]:
    if request is None:
        return {fragment: False for fragment in forbidden}
    values: list[str] = []
    for goal in request.goals:
        _, _, goal_values = _goal_surface_values(goal)
        values.extend(goal_values)
    values.extend(item.text for item in request.deliverables)
    return {fragment: _contains(values, fragment) for fragment in forbidden}


def _brief_safety(brief, hypotheses) -> dict[str, object]:
    all_candidates = {
        candidate.candidate_id: candidate
        for hypothesis in hypotheses
        for candidate in hypothesis.candidates
    }
    all_refs = list(brief.scope.semantic_refs)

    provenance_violations = [
        ref.candidate_id for ref in all_refs if ref.candidate_id not in all_candidates
    ]
    domain_violations = [
        domain
        for domain in brief.required_domains
        if not any(domain in ref.cube_names for ref in all_refs)
    ]

    expected_blocked = tuple(
        question.goal_id
        for question in brief.questions
        if question.status.value == "BLOCKED"
    )
    unresolved_consistent = all(
        bool(question.unresolved) == (question.status.value == "BLOCKED")
        for question in brief.questions
    )
    blocking_consistent = (
        expected_blocked == brief.blocking_goal_ids
        and unresolved_consistent
        and (
            (brief.status == ResearchBriefStatus.BLOCKED) == bool(expected_blocked)
        )
    )
    expected_must_ids = (
        tuple(question.goal_id for question in brief.questions)
        + tuple(item.requirement_id for item in brief.deliverables)
    )
    must_consistent = (
        len(brief.must_requirement_ids)
        == len(brief.questions) + len(brief.deliverables)
        and brief.must_requirement_ids == expected_must_ids
        and all(question.priority == "MUST" for question in brief.questions)
        and all(item.priority == "MUST" for item in brief.deliverables)
    )

    return {
        "resolver_ref_provenance_violations": provenance_violations,
        "required_domain_provenance_violations": domain_violations,
        "blocking_consistent": blocking_consistent,
        "must_consistent": must_consistent,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-live", action="store_true")
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Run only named case(s). Repeatable; useful for cheap targeted reruns.",
    )
    args = parser.parse_args()

    all_cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))["cases"]
    selected = set(args.case_id)
    cases = [
        case for case in all_cases
        if not selected or str(case["id"]) in selected
    ]
    missing_selected = selected - {str(case["id"]) for case in cases}
    if missing_selected:
        raise SystemExit(f"Unknown case ids: {sorted(missing_selected)}")

    llm = build_generator(get_settings())
    providers = _provider_names(llm)
    if not _is_real_llm(llm):
        payload = {
            "kind": "dima_v2_day6_research_eval",
            "status": "live_provider_unavailable",
            "providers": providers,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2 if args.require_live else 0

    interpreter = TurnInterpreter()
    resolver = SemanticResolver(signing_key=b"day6-manual-eval-signing-key")
    builder = ResearchBriefBuilder()
    context = _context()
    schema = _schema()

    records: list[dict] = []
    expected_goal_total = 0
    matched_goal_total = 0
    expected_deliverable_total = 0
    matched_deliverable_total = 0
    expected_time_total = 0
    matched_time_total = 0
    invented_goal_total = 0
    forbidden_goal_hit_total = 0
    research_act_ok = 0
    research_act_total = 0
    negative_act_ok = 0
    negative_act_total = 0
    expected_brief_status_ok = 0
    expected_brief_status_total = 0
    provenance_violation_total = 0
    domain_violation_total = 0
    blocking_consistency_violations = 0
    must_consistency_violations = 0
    surface_violations = 0
    total_calls = 0
    max_calls = 0
    canonical_pass = False

    for case in cases:
        counting = CountingLlm(llm)
        expect_research = bool(case.get("expect_research", True))
        yaml_expected_act = str(case["expected_act"])
        expected_act = (
            "COMPLEX_ANALYSIS"
            if expect_research
            else yaml_expected_act
        )
        requirement_signatures = list(case.get("goals") or ())
        signatures = [
            item for item in requirement_signatures
            if str(item.get("kind")) != "deliverable"
        ]
        deliverable_signatures = [
            item for item in requirement_signatures
            if str(item.get("kind")) == "deliverable"
        ]
        expected_time = [str(x) for x in case.get("time") or ()]
        forbidden = [str(x) for x in case.get("forbidden_goal_fragments") or ()]
        expected_brief_status = case.get("brief_status")
        failure = None

        try:
            turn = interpreter.interpret(
                question=str(case["q"]),
                semantic_context=context,
                conversation=ConversationStateV2(),
                llm=counting,
            )
            request = turn.research_request
            act_ok = turn.dialogue_act.value == expected_act
            research_shape_ok = (request is not None) == expect_research
            time_results = _time_coverage(request, expected_time)
            expected_time_total += len(expected_time)
            matched_time_total += sum(time_results.values())
            forbidden_results = _forbidden_goal_hits(request, forbidden)

            brief = None
            bundle = None
            safety = {
                "resolver_ref_provenance_violations": [],
                "required_domain_provenance_violations": [],
                "blocking_consistent": True,
                "must_consistent": True,
            }

            if expect_research:
                research_act_total += 1
                research_act_ok += int(act_ok and research_shape_ok)
                goals = request.goals if request is not None else ()
                deliverables = request.deliverables if request is not None else ()
                matched_count, matched_pairs = _maximum_signature_match(signatures, goals)
                matched_deliverable_count, matched_deliverable_pairs = (
                    _maximum_deliverable_match(
                        deliverable_signatures,
                        deliverables,
                    )
                )
                expected_goal_total += len(signatures)
                matched_goal_total += matched_count
                expected_deliverable_total += len(deliverable_signatures)
                matched_deliverable_total += matched_deliverable_count
                invented = (
                    max(len(goals) - matched_count, 0)
                    + max(len(deliverables) - matched_deliverable_count, 0)
                )
                invented_goal_total += invented
                forbidden_hits = sum(forbidden_results.values())
                forbidden_goal_hit_total += forbidden_hits

                if request is not None:
                    bundle = resolver.resolve_turn(
                        turn=turn,
                        schema=schema,
                        semantic_context=context,
                        conversation=ConversationStateV2(),
                        tenant_binding="id:day6-eval",
                        session_id="day6-eval",
                        thread_id=str(case["id"]),
                    )
                    brief = builder.build(
                        turn=turn,
                        hypotheses=bundle.hypotheses,
                        semantic_context=context,
                        context_version=context.context_version.version,
                    )
                    safety = _brief_safety(brief, bundle.hypotheses)

                provenance_violation_total += len(
                    safety["resolver_ref_provenance_violations"]
                )
                domain_violation_total += len(
                    safety["required_domain_provenance_violations"]
                )
                blocking_consistency_violations += int(
                    not bool(safety["blocking_consistent"])
                )
                must_consistency_violations += int(
                    not bool(safety["must_consistent"])
                )

                brief_status_ok = (
                    brief is not None
                    and (
                        expected_brief_status is None
                        or brief.status.value == str(expected_brief_status)
                    )
                )
                if expected_brief_status is not None:
                    expected_brief_status_total += 1
                    expected_brief_status_ok += int(brief_status_ok)

                case_pass = (
                    act_ok
                    and research_shape_ok
                    and matched_count == len(signatures)
                    and len(goals) == len(signatures)
                    and matched_deliverable_count == len(deliverable_signatures)
                    and len(deliverables) == len(deliverable_signatures)
                    and all(time_results.values())
                    and forbidden_hits == 0
                    and brief_status_ok
                    and not safety["resolver_ref_provenance_violations"]
                    and not safety["required_domain_provenance_violations"]
                    and bool(safety["blocking_consistent"])
                    and bool(safety["must_consistent"])
                )
                detail = {
                    "expected_goal_count": len(signatures),
                    "actual_goal_count": len(goals),
                    "matched_goal_count": matched_count,
                    "matched_pairs": matched_pairs,
                    "expected_deliverable_count": len(deliverable_signatures),
                    "actual_deliverable_count": len(deliverables),
                    "matched_deliverable_count": matched_deliverable_count,
                    "matched_deliverable_pairs": matched_deliverable_pairs,
                    "actual_goals": [
                        {
                            "kind": goal.kind.value,
                            "text": goal.text,
                            "subjects": [m.text for m in goal.subject_mentions],
                            "related": [m.text for m in goal.related_mentions],
                        }
                        for goal in goals
                    ],
                    "actual_deliverables": [
                        {
                            "kind": item.kind.value,
                            "text": item.text,
                        }
                        for item in deliverables
                    ],
                    "semantic_status": (
                        bundle.semantic_status if bundle is not None else None
                    ),
                    "brief_status": brief.status.value if brief is not None else None,
                    "blocking_goal_ids": (
                        list(brief.blocking_goal_ids) if brief is not None else []
                    ),
                    **safety,
                }
            else:
                negative_act_total += 1
                negative_act_ok += int(act_ok and research_shape_ok)
                case_pass = act_ok and research_shape_ok
                detail = {
                    "expected_goal_count": 0,
                    "actual_goal_count": 0 if request is None else len(request.goals),
                    "matched_goal_count": 0,
                    "actual_goals": (
                        []
                        if request is None
                        else [
                            {
                                "kind": goal.kind.value,
                                "text": goal.text,
                            }
                            for goal in request.goals
                        ]
                    ),
                }

            if str(case["id"]) == "canonical":
                canonical_pass = case_pass

            record = {
                "id": case["id"],
                "question": case["q"],
                "expected_act": expected_act,
                "actual_act": turn.dialogue_act.value,
                "expect_research": expect_research,
                "research_shape_ok": research_shape_ok,
                "time_results": time_results,
                "forbidden_goal_results": forbidden_results,
                "case_pass": case_pass,
                "calls": counting.calls,
                "failure": None,
                **detail,
            }
        except TurnInterpreterError as exc:
            if exc.failure.code == "surface_grounding_violation":
                surface_violations += 1
            expected_time_total += len(expected_time)
            if expect_research:
                research_act_total += 1
                expected_goal_total += len(signatures)
                expected_brief_status_total += int(expected_brief_status is not None)
            else:
                negative_act_total += 1
            failure = exc.failure.model_dump(mode="json")
            record = {
                "id": case["id"],
                "question": case["q"],
                "expected_act": expected_act,
                "actual_act": None,
                "expect_research": expect_research,
                "research_shape_ok": False,
                "expected_goal_count": len(signatures),
                "actual_goal_count": 0,
                "matched_goal_count": 0,
                "time_results": {x: False for x in expected_time},
                "forbidden_goal_results": {},
                "case_pass": False,
                "calls": counting.calls,
                "failure": failure,
            }

        total_calls += counting.calls
        max_calls = max(max_calls, counting.calls)
        records.append(record)

    goal_coverage = (
        matched_goal_total / expected_goal_total if expected_goal_total else 1.0
    )
    deliverable_coverage = (
        matched_deliverable_total / expected_deliverable_total
        if expected_deliverable_total
        else 1.0
    )
    total_expected_must = expected_goal_total + expected_deliverable_total
    total_matched_must = matched_goal_total + matched_deliverable_total
    must_requirement_coverage = (
        total_matched_must / total_expected_must if total_expected_must else 1.0
    )
    time_scope_coverage = (
        matched_time_total / expected_time_total if expected_time_total else 1.0
    )
    research_act_accuracy = (
        research_act_ok / research_act_total if research_act_total else 1.0
    )
    negative_act_accuracy = (
        negative_act_ok / negative_act_total if negative_act_total else 1.0
    )
    brief_status_accuracy = (
        expected_brief_status_ok / expected_brief_status_total
        if expected_brief_status_total
        else 1.0
    )
    case_pass_rate = (
        sum(bool(record["case_pass"]) for record in records) / len(records)
        if records else 1.0
    )
    format_retry_count = sum(max(int(record.get("calls") or 0) - 1, 0) for record in records)
    format_retry_rate = (
        format_retry_count / len(records) if records else 0.0
    )

    # For targeted subsets, canonical may not be selected. Full gate requires it.
    canonical_gate = canonical_pass if not selected or "canonical" in selected else True
    passed = (
        canonical_gate
        and goal_coverage >= 0.95
        and deliverable_coverage == 1.0
        and must_requirement_coverage >= 0.95
        and time_scope_coverage == 1.0
        and case_pass_rate >= 0.95
        and research_act_accuracy >= 0.95
        and negative_act_accuracy == 1.0
        and brief_status_accuracy == 1.0
        and invented_goal_total == 0
        and forbidden_goal_hit_total == 0
        and provenance_violation_total == 0
        and domain_violation_total == 0
        and blocking_consistency_violations == 0
        and must_consistency_violations == 0
        and surface_violations == 0
        and max_calls <= 2
        and format_retry_rate <= 0.10
    )

    payload = {
        "kind": "dima_v2_day6_research_eval",
        "status": "pass" if passed else "fail",
        "source_policy": (
            "real_provider_language_owner_plus_research_mode_policy_plus_real_resolver_and_brief_builder_"
            "synthetic_permuted_context_no_data_query"
        ),
        "providers": providers,
        "selected_case_ids": sorted(selected),
        "case_count": len(records),
        "case_pass_rate": round(case_pass_rate, 4),
        "canonical_complex_goal_extraction": bool(canonical_gate),
        "complex_validation_goal_coverage": round(goal_coverage, 4),
        "deliverable_requirement_coverage": round(deliverable_coverage, 4),
        "must_requirement_coverage": round(must_requirement_coverage, 4),
        "explicit_time_scope_coverage": round(time_scope_coverage, 4),
        "research_act_accuracy": round(research_act_accuracy, 4),
        "non_research_negative_accuracy": round(negative_act_accuracy, 4),
        "expected_brief_status_accuracy": round(brief_status_accuracy, 4),
        "invented_goal_count": invented_goal_total,
        "forbidden_goal_hits": forbidden_goal_hit_total,
        "resolver_ref_provenance_violations": provenance_violation_total,
        "required_domain_provenance_violations": domain_violation_total,
        "blocking_consistency_violations": blocking_consistency_violations,
        "must_consistency_violations": must_consistency_violations,
        "surface_grounding_violations": surface_violations,
        "total_llm_calls": total_calls,
        "format_retry_count": format_retry_count,
        "format_retry_rate": round(format_retry_rate, 4),
        "max_calls_per_case": max_calls,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        "Day6 manual research gate: "
        f"cases={len(records)} pass={case_pass_rate:.1%} "
        f"goals={goal_coverage:.1%} deliverables={deliverable_coverage:.1%} "
        f"must={must_requirement_coverage:.1%} time={time_scope_coverage:.1%} "
        f"research_act={research_act_accuracy:.1%} "
        f"negatives={negative_act_accuracy:.1%} invented={invented_goal_total} "
        f"calls={total_calls} retry_rate={format_retry_rate:.1%} status={payload['status']}"
    )
    for record in records:
        if record["case_pass"]:
            continue
        print(
            "DAY6_FAIL_CASE "
            + json.dumps(
                {
                    "id": record["id"],
                    "expected_act": record["expected_act"],
                    "actual_act": record.get("actual_act"),
                    "expected_goal_count": record.get("expected_goal_count"),
                    "actual_goal_count": record.get("actual_goal_count"),
                    "matched_goal_count": record.get("matched_goal_count"),
                    "actual_goals": record.get("actual_goals", []),
                    "actual_deliverables": record.get("actual_deliverables", []),
                    "expected_deliverable_count": record.get("expected_deliverable_count"),
                    "matched_deliverable_count": record.get("matched_deliverable_count"),
                    "brief_status": record.get("brief_status"),
                    "blocking_goal_ids": record.get("blocking_goal_ids", []),
                    "time_results": record.get("time_results", {}),
                    "forbidden_goal_results": record.get("forbidden_goal_results", {}),
                    "failure": record.get("failure"),
                    "calls": record.get("calls"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
