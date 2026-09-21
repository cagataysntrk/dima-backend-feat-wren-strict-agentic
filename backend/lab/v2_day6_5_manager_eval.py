"""Manual Day 6.5 DEV/VALIDATION intent-acceptance evaluator.

This evaluator measures the bounded RESEARCH_MANAGER only through the pre-execution
understanding boundary:

  user turn -> Resolver-issued opaque handles -> IntentAcceptanceGate
  -> AcceptedTurnContract -> StandardProjectionCompiler -> RepresentabilityGate

No query, Wren execution, DB access, raw SQL tool, or evidence fabrication occurs here.
Adaptive/execution/completion proofs are separate focused gates.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import yaml

from app.config import get_settings
from app.kaset import belki_sar
from app.llm import NoLlmGenerator, RuleBasedSqlGenerator, build_generator
from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_preacceptance import FiniteAcceptanceStatus
from app.v2.manager_models import ObligationOrigin, ObligationPolarity
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.model_policy import ModelRole, ModelRolePolicy
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
)
from app.v2.representability import RepresentabilityGate
from app.v2.resolver import SemanticResolver
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_projection import StandardProjectionCompiler


ROOT = Path(__file__).resolve().parents[1]
DEV_CASES = ROOT / "eval" / "v2_day6_5_dev_cases.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day6_5_manager_eval.json"


class CountingLlm:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def structured_json(self, system: str, user: str, *, schema: dict, schema_name: str):
        self.calls += 1
        return self.inner.structured_json(
            system,
            user,
            schema=schema,
            schema_name=schema_name,
        )


def _is_real_llm(llm) -> bool:
    gens = list(getattr(llm, "_gens", None) or [llm])
    return any(not isinstance(g, (RuleBasedSqlGenerator, NoLlmGenerator)) for g in gens)


def _context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-day65-manager-eval-v2",
            mdl_version="mdl-day65-manager-eval-v2",
            compact_catalog_builder_version="day65-eval-v2",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="day65-manager-eval-v2",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales_omega",
                display="Satış",
                synonyms=("satış", "satis"),
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_value_x",
                        display="Net Gelir",
                        synonyms=("net gelir", "gelir"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="gross_value_y",
                        display="Brüt Gelir",
                        synonyms=("brüt gelir", "brut gelir", "gelir"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="order_count_k",
                        display="Sipariş Sayısı",
                        synonyms=("sipariş sayısı", "sipariş adedi", "siparis sayisi"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="sales_perf_v",
                        display="Satış Performansı",
                        synonyms=("satış performansı", "satis performansi", "performans"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="region_axis_m",
                        display="Bölge",
                        synonyms=("bölge", "bölgeler", "bolge", "bolgeler"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="product_axis_n",
                        display="Ürün",
                        synonyms=("ürün", "ürünler", "urun", "urunler"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="channel_axis_c",
                        display="Kanal",
                        synonyms=("kanal", "kanallar"),
                    ),
                ),
                time_dimensions=("booked_date_z",),
            ),
            CompactCubeContextV0(
                canonical_name="ops_delta",
                display="Üretim",
                synonyms=("üretim", "operasyon"),
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="yield_score_n",
                        display="Üretkenlik",
                        synonyms=("üretkenlik", "verimlilik", "performans"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="scrap_ratio_q",
                        display="Hurda Oranı",
                        synonyms=("hurda oranı", "hurda orani"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="oee_score_r",
                        display="OEE",
                        synonyms=("oee", "performans"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="line_axis_p",
                        display="Hat",
                        synonyms=("hat", "hatlar", "üretim hattı"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="shift_axis_s",
                        display="Vardiya",
                        synonyms=("vardiya", "vardiyalar"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="machine_axis_t",
                        display="Makine",
                        synonyms=("makine", "makineler", "ekipman"),
                    ),
                ),
                time_dimensions=("event_date_k",),
            ),
        ),
        approved_business_rules="",
        business_rules_truncated=False,
    )


def _schema() -> dict[str, Any]:
    return {
        "catalog": "day65-manager-eval",
        "schema_name": "main",
        "models": [],
        "cubes": [
            {
                "name": "sales_omega",
                "measures": [
                    "net_value_x",
                    "gross_value_y",
                    "order_count_k",
                    "sales_perf_v",
                ],
                "measure_synonyms": {
                    "net_value_x": ["net gelir", "gelir"],
                    "gross_value_y": ["brüt gelir", "brut gelir", "gelir"],
                    "order_count_k": ["sipariş sayısı", "sipariş adedi"],
                    "sales_perf_v": ["satış performansı", "performans"],
                },
                "dimensions": ["region_axis_m", "product_axis_n", "channel_axis_c"],
                "dimension_labels": {
                    "region_axis_m": "Bölge",
                    "product_axis_n": "Ürün",
                    "channel_axis_c": "Kanal",
                },
                "dimension_synonyms": {
                    "region_axis_m": ["bölge", "bölgeler"],
                    "product_axis_n": ["ürün", "ürünler"],
                    "channel_axis_c": ["kanal", "kanallar"],
                },
                "dimension_values": {},
                "time_dimensions": ["booked_date_z"],
            },
            {
                "name": "ops_delta",
                "measures": ["yield_score_n", "scrap_ratio_q", "oee_score_r"],
                "measure_synonyms": {
                    "yield_score_n": ["üretkenlik", "verimlilik", "performans"],
                    "scrap_ratio_q": ["hurda oranı"],
                    "oee_score_r": ["oee", "performans"],
                },
                "dimensions": ["line_axis_p", "shift_axis_s", "machine_axis_t"],
                "dimension_labels": {
                    "line_axis_p": "Hat",
                    "shift_axis_s": "Vardiya",
                    "machine_axis_t": "Makine",
                },
                "dimension_synonyms": {
                    "line_axis_p": ["hat", "hatlar", "üretim hattı"],
                    "shift_axis_s": ["vardiya", "vardiyalar"],
                    "machine_axis_t": ["makine", "makineler", "ekipman"],
                },
                "dimension_values": {},
                "time_dimensions": ["event_date_k"],
            },
        ],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


def _counter(values: list[str]) -> Counter[str]:
    return Counter(str(value) for value in values)


def _expected_required(case: dict[str, Any]) -> Counter[str]:
    return _counter(
        [
            *case.get("expected_obligations", []),
            *case.get("expected_deliverables", []),
        ]
    )


def _actual_contract_shape(runtime: ManagerRuntime) -> tuple[Counter[str], Counter[str], list[dict]]:
    if runtime.ledger is None:
        return Counter(), Counter(), []
    required: list[str] = []
    excluded: list[str] = []
    items: list[dict] = []
    for item in runtime.ledger.items:
        record = item.model_dump(mode="json")
        items.append(record)
        if item.origin != ObligationOrigin.USER_MUST:
            continue
        if item.polarity == ObligationPolarity.REQUIRED:
            required.append(item.capability_key.value)
        elif item.polarity == ObligationPolarity.EXCLUDED:
            excluded.append(item.capability_key.value)
    return _counter(required), _counter(excluded), items


def _representability(
    *,
    runtime: ManagerRuntime,
    handles: SemanticHandleRegistry,
    tenant_binding: str,
    context_version: str,
) -> tuple[str, dict[str, Any]]:
    if runtime.accepted_contract is None or runtime.ledger is None:
        return "CLARIFICATION_REQUIRED", {
            "compiled": False,
            "compile_reasons": ["no accepted contract"],
        }

    compiled = StandardProjectionCompiler(
        semantic_handles=handles,
    ).compile(
        contract=runtime.accepted_contract,
        ledger=runtime.ledger,
        tenant_binding=tenant_binding,
        context_version=context_version,
    )
    decision = RepresentabilityGate().decide(
        contract=runtime.accepted_contract,
        ledger=runtime.ledger,
        projection=compiled.projection,
    )
    return decision.decision.value, {
        "compiled": compiled.compiled,
        "compile_reasons": list(compiled.reasons),
        "projection": (
            compiled.projection.model_dump(mode="json")
            if compiled.projection is not None
            else None
        ),
        "gate_reasons": list(decision.reasons),
    }


def _run_case(
    case: dict[str, Any],
    *,
    role_settings,
    tenant_binding: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    inner = belki_sar(build_generator(role_settings))
    if not _is_real_llm(inner):
        raise RuntimeError("live RESEARCH_MANAGER provider unavailable")
    llm = CountingLlm(inner)

    context = _context()
    conversation = ConversationStateV2.model_validate(case.get("conversation") or {})
    source_spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    semantic = ManagerSemanticResolutionAdapter(
        resolver=SemanticResolver(signing_key=b"day65-manager-eval-signing-key"),
        source_spans=source_spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=conversation,
        schema=_schema(),
        tenant_binding=tenant_binding,
        session_id=f"eval-session:{case['id']}",
        thread_id=f"eval-thread:{case['id']}",
    )
    acceptance = IntentAcceptanceGate(
        source_spans=source_spans,
        semantic_handles=handles,
    )
    executor = GovernedManagerExecutor(
        acceptance=acceptance,
        core_analytics=object(),
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant_binding,
            context_version=context.context_version.version,
            principal=None,
            service=None,
            tenant_runtime=None,
            contract_store=None,
            session_id=f"eval-session:{case['id']}",
        ),
        semantic_resolution=semantic,
    )
    runtime = ManagerRuntime(request_ref=f"day65-eval:{case['id']}")
    loop = ResearchManagerLoop(llm=llm, source_spans=source_spans)
    outcome = loop.understand(
        question=str(case["prompt"]),
        message_id=f"turn:{case['id']}",
        request_ref=f"day65-eval:{case['id']}",
        runtime=runtime,
        executor=executor,
        conversation=conversation,
    )

    required, excluded, ledger_items = _actual_contract_shape(runtime)
    actual_rep, rep_detail = _representability(
        runtime=runtime,
        handles=handles,
        tenant_binding=tenant_binding,
        context_version=context.context_version.version,
    )
    expected_terminal = str(case["expected_terminal_state"])
    evaluation_valid = outcome.status not in {
        FiniteAcceptanceStatus.MODEL_FAILURE,
        FiniteAcceptanceStatus.GROUNDING_FAILURE,
    }
    actual_terminal = (
        "ACCEPTED"
        if outcome.status == FiniteAcceptanceStatus.ACCEPTED
        else "CLARIFICATION"
        if outcome.status == FiniteAcceptanceStatus.CLARIFICATION_REQUIRED
        else "NOT_ACCEPTED"
        if evaluation_valid
        else None
    )

    expected_required = _expected_required(case)
    expected_excluded = _counter(case.get("expected_exclusions", []))

    expected_required_total = sum(expected_required.values())
    matched_required = sum(
        min(required[key], expected_required[key]) for key in expected_required
    )
    invented_required = sum(
        max(required[key] - expected_required[key], 0) for key in required
    )
    missing_required = sum(
        max(expected_required[key] - required[key], 0) for key in expected_required
    )
    missing_exclusions = sum(
        max(expected_excluded[key] - excluded[key], 0) for key in expected_excluded
    )
    invented_exclusions = sum(
        max(excluded[key] - expected_excluded[key], 0) for key in excluded
    )

    accepted_handle_violations = 0
    if runtime.ledger is not None:
        for item in runtime.ledger.items:
            for handle_id in item.semantic_handle_refs:
                try:
                    handles.validate(
                        handle_id,
                        tenant_binding=tenant_binding,
                        context_version=context.context_version.version,
                    )
                except (KeyError, ValueError):
                    accepted_handle_violations += 1

    executed_tool_names = [
        obs.get("tool")
        for obs in outcome.observations
        if obs.get("kind") == "tool"
    ]
    forbidden_execution_tools = [
        name
        for name in executed_tool_names
        if name in {"run_analytics", "run_relationship", "inspect_evidence"}
    ]

    expected_rep = str(case["expected_representability"])
    terminal_ok = actual_terminal == expected_terminal
    obligation_ok = required == expected_required if expected_terminal == "ACCEPTED" else not outcome.accepted
    exclusion_ok = excluded == expected_excluded if expected_terminal == "ACCEPTED" else True
    representability_ok = actual_rep == expected_rep
    security_ok = accepted_handle_violations == 0 and not forbidden_execution_tools

    case_pass = (
        evaluation_valid
        and terminal_ok
        and obligation_ok
        and exclusion_ok
        and representability_ok
        and security_ok
    )

    return {
        "id": case["id"],
        "taxonomy": case["taxonomy"],
        "question": case["prompt"],
        "expected_terminal": expected_terminal,
        "actual_terminal": actual_terminal,
        "preacceptance_status": outcome.status.value,
        "evaluation_valid": evaluation_valid,
        "expected_required": dict(expected_required),
        "actual_required": dict(required),
        "expected_excluded": dict(expected_excluded),
        "actual_excluded": dict(excluded),
        "expected_representability": expected_rep,
        "actual_representability": actual_rep,
        "representability_detail": rep_detail,
        "matched_required": matched_required,
        "expected_required_total": expected_required_total,
        "missing_required": missing_required,
        "invented_required": invented_required,
        "missing_exclusions": missing_exclusions,
        "invented_exclusions": invented_exclusions,
        "accepted_handle_violations": accepted_handle_violations,
        "forbidden_execution_tools": forbidden_execution_tools,
        "model_calls": llm.calls,
        "manager_turns": outcome.snapshot.manager_turns,
        "latency_s": round(time.perf_counter() - started, 4),
        "case_pass": case_pass,
        "ledger": ledger_items,
        "observations": list(outcome.observations),
        "adversarial_flags": case.get("adversarial_flags", []),
        "requires_adaptive_branch": bool(case.get("requires_adaptive_branch")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEV_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--taxonomy", action="append", default=[])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model", default="")
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()

    document = yaml.safe_load(args.cases.read_text(encoding="utf-8"))
    cases = list(document.get("cases") or [])
    selected_ids = set(args.case_id)
    selected_taxonomy = set(args.taxonomy)
    if selected_ids:
        cases = [case for case in cases if str(case["id"]) in selected_ids]
    if selected_taxonomy:
        cases = [
            case
            for case in cases
            if selected_taxonomy.intersection(set(case.get("taxonomy") or []))
        ]
    if not cases:
        raise SystemExit("No Day 6.5 cases selected")

    settings = get_settings()
    try:
        role_settings, profile = ModelRolePolicy(settings).scoped_settings(
            ModelRole.RESEARCH_MANAGER,
            model_override=(args.model.strip() or None),
        )
    except ValueError as exc:
        payload = {
            "kind": "dima_v2_day6_5_manager_eval",
            "status": "model_role_unconfigured",
            "error": str(exc),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2 if args.require_live else 0

    probe = belki_sar(build_generator(role_settings))
    if not _is_real_llm(probe):
        payload = {
            "kind": "dima_v2_day6_5_manager_eval",
            "status": "live_provider_unavailable",
            "model": profile.model,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2 if args.require_live else 0

    tenant_binding = "id:day65-manager-eval"
    records: list[dict[str, Any]] = []
    workers = max(1, min(int(args.workers), 8))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {
            pool.submit(
                _run_case,
                case,
                role_settings=role_settings,
                tenant_binding=tenant_binding,
            ): case
            for case in cases
        }
        for future in as_completed(future_map):
            case = future_map[future]
            try:
                records.append(future.result())
            except Exception as exc:
                records.append(
                    {
                        "id": case["id"],
                        "taxonomy": case["taxonomy"],
                        "question": case["prompt"],
                        "case_pass": None,
                        "evaluation_valid": False,
                        "preacceptance_status": "HARNESS_FAILURE",
                        "actual_terminal": None,
                        "fatal_error": f"{type(exc).__name__}: {exc}",
                        "expected_required_total": len(case.get("expected_obligations") or [])
                        + len(case.get("expected_deliverables") or []),
                        "matched_required": 0,
                        "missing_required": len(case.get("expected_obligations") or [])
                        + len(case.get("expected_deliverables") or []),
                        "invented_required": 0,
                        "missing_exclusions": len(case.get("expected_exclusions") or []),
                        "invented_exclusions": 0,
                        "accepted_handle_violations": 0,
                        "forbidden_execution_tools": [],
                        "model_calls": 0,
                        "manager_turns": 0,
                        "latency_s": 0.0,
                    }
                )

    records.sort(key=lambda item: str(item["id"]))
    n = len(records)
    evaluable_records = [
        record for record in records if bool(record.get("evaluation_valid", True))
    ]
    evaluable_n = len(evaluable_records)
    measurement_failures = n - evaluable_n
    model_failures = sum(
        record.get("preacceptance_status") == FiniteAcceptanceStatus.MODEL_FAILURE.value
        for record in records
    )
    grounding_failures = sum(
        record.get("preacceptance_status") == FiniteAcceptanceStatus.GROUNDING_FAILURE.value
        for record in records
    )
    harness_failures = sum(
        record.get("preacceptance_status") == "HARNESS_FAILURE"
        for record in records
    )

    passed_cases = sum(bool(record.get("case_pass")) for record in evaluable_records)
    expected_must = sum(
        int(record.get("expected_required_total") or 0) for record in evaluable_records
    )
    matched_must = sum(
        int(record.get("matched_required") or 0) for record in evaluable_records
    )
    invented_must = sum(
        int(record.get("invented_required") or 0) for record in evaluable_records
    )
    missing_exclusions = sum(
        int(record.get("missing_exclusions") or 0) for record in evaluable_records
    )
    invented_exclusions = sum(
        int(record.get("invented_exclusions") or 0) for record in evaluable_records
    )
    handle_violations = sum(
        int(record.get("accepted_handle_violations") or 0) for record in evaluable_records
    )
    execution_violations = sum(
        len(record.get("forbidden_execution_tools") or [])
        for record in evaluable_records
    )

    cases_by_id = {str(case["id"]): case for case in cases}
    silent_ambiguity_accept = sum(
        1
        for record in evaluable_records
        if cases_by_id[str(record["id"])]["expected_terminal_state"] == "CLARIFICATION"
        and record.get("actual_terminal") == "ACCEPTED"
    )
    expected_standard = [
        record for record in evaluable_records
        if record.get("expected_representability") == "STANDARD_LOSSLESS"
    ]
    unsafe_fast = sum(
        1
        for record in evaluable_records
        if record.get("expected_representability") != "STANDARD_LOSSLESS"
        and record.get("actual_representability") == "STANDARD_LOSSLESS"
    )
    standard_correct = sum(
        1
        for record in expected_standard
        if record.get("actual_representability") == "STANDARD_LOSSLESS"
    )
    clarification_cases = [
        record for record in evaluable_records
        if record.get("expected_terminal") == "CLARIFICATION"
    ]
    clarification_correct = sum(
        1
        for record in clarification_cases
        if record.get("actual_terminal") == "CLARIFICATION"
    )

    case_pass_rate = passed_cases / evaluable_n if evaluable_n else 0.0
    must_recall = matched_must / expected_must if expected_must else 1.0
    standard_rate = standard_correct / len(expected_standard) if expected_standard else 1.0
    clarification_rate = (
        clarification_correct / len(clarification_cases) if clarification_cases else 1.0
    )
    max_turns = max(
        (int(record.get("manager_turns") or 0) for record in evaluable_records),
        default=0,
    )

    # DEV is tunable; the same hard authority gates still fail immediately.
    semantic_pass = (
        case_pass_rate >= 0.95
        and must_recall >= 0.95
        and invented_must == 0
        and missing_exclusions == 0
        and invented_exclusions == 0
        and handle_violations == 0
        and execution_violations == 0
        and silent_ambiguity_accept == 0
        and unsafe_fast == 0
        and standard_rate == 1.0
        and clarification_rate == 1.0
        and max_turns <= 8
    )
    complete_measurement = measurement_failures == 0
    passed = complete_measurement and semantic_pass
    run_status = (
        "pass"
        if passed
        else "incomplete"
        if not complete_measurement
        else "fail"
    )

    payload = {
        "kind": "dima_v2_day6_5_manager_eval",
        "status": run_status,
        "corpus_version": document.get("version"),
        "case_count": n,
        "model_role": ModelRole.RESEARCH_MANAGER.value,
        "model_profile": {
            "provider": profile.provider,
            "model": profile.model,
            "native_schema_required": profile.native_schema_required,
        },
        "workers": workers,
        "measurement": {
            "selected_cases": n,
            "evaluable_cases": evaluable_n,
            "measurement_failures": measurement_failures,
            "model_failures": model_failures,
            "grounding_failures": grounding_failures,
            "harness_failures": harness_failures,
        },
        "metrics": {
            "case_pass_rate": round(case_pass_rate, 4),
            "must_obligation_recall": round(must_recall, 4),
            "accepted_invented_must": invented_must,
            "missing_expected_exclusions": missing_exclusions,
            "invented_exclusions": invented_exclusions,
            "accepted_handle_violations": handle_violations,
            "preacceptance_execution_violations": execution_violations,
            "blocking_ambiguity_silent_accept": silent_ambiguity_accept,
            "unsafe_fast_admission": unsafe_fast,
            "standard_lossless_rate": round(standard_rate, 4),
            "clarification_canonical_rate": round(clarification_rate, 4),
            "max_manager_turns": max_turns,
            "total_model_calls": sum(int(record.get("model_calls") or 0) for record in records),
            "total_latency_s": round(sum(float(record.get("latency_s") or 0.0) for record in records), 4),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "records"}, ensure_ascii=False))
    for record in records:
        if record.get("case_pass"):
            continue
        print(
            "DAY65_DEV_FAIL "
            + json.dumps(
                {
                    "id": record["id"],
                    "actual_terminal": record.get("actual_terminal"),
                    "expected_terminal": record.get("expected_terminal"),
                    "preacceptance_status": record.get("preacceptance_status"),
                    "evaluation_valid": record.get("evaluation_valid"),
                    "actual_required": record.get("actual_required"),
                    "expected_required": record.get("expected_required"),
                    "actual_excluded": record.get("actual_excluded"),
                    "expected_excluded": record.get("expected_excluded"),
                    "actual_representability": record.get("actual_representability"),
                    "expected_representability": record.get("expected_representability"),
                    "fatal_error": record.get("fatal_error"),
                    "model_calls": record.get("model_calls"),
                    "manager_turns": record.get("manager_turns"),
                    "observations": record.get("observations", [])[-8:],
                    "representability_detail": record.get("representability_detail"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    if not complete_measurement:
        return 2
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
