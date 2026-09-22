"""FT-003 real-model cognition sentinel.

Small sequential certification only. It does not execute analytics queries; the separate
FT-003 live sentinel owns query/execution correctness. This sentinel proves that the real
structured model can map Turkish questions into Fast-owned typed cognition and can choose
only supplied opaque handles.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

from app.config import Settings
from app.fast.ask_cognition import StructuredJsonFastCognition
from app.fast.ask_models import (
    AggregationKind,
    DraftStatus,
    FieldCandidate,
    ResourceCandidate,
    SelectionPurpose,
    TemporalKind,
)
from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import FastMetabaseRuntimePolicy
from app.fast.resource_registry import discover_resource_registry
from app.llm import build_generator


MODEL = os.getenv("DIMA_OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
OUT = Path(
    os.getenv(
        "DIMA_FAST_ASK_MODEL_RECEIPT",
        "lab/metabase/artifacts/ft003-model-sentinel.json",
    )
)

SUPPORTED_CASES = (
    {
        "name": "count_last_n_days",
        "question": "Son 30 günde kaç sipariş var?",
        "aggregation": AggregationKind.COUNT,
        "temporal": TemporalKind.LAST_N_DAYS,
        "days": 30,
        "measure": None,
        "breakdown": None,
    },
    {
        "name": "sum_last_n_days",
        "question": "Son 30 gündeki sipariş tutarı ne kadar?",
        "aggregation": AggregationKind.SUM,
        "temporal": TemporalKind.LAST_N_DAYS,
        "days": 30,
        "measure": "amount",
        "breakdown": None,
    },
    {
        "name": "breakdown_last_n_days",
        "question": "Son 30 günde bölgelere göre sipariş tutarı",
        "aggregation": AggregationKind.SUM,
        "temporal": TemporalKind.LAST_N_DAYS,
        "days": 30,
        "measure": "amount",
        "breakdown": "region",
    },
    {
        "name": "count_current_month",
        "question": "Bu ay kaç sipariş var?",
        "aggregation": AggregationKind.COUNT,
        "temporal": TemporalKind.CURRENT_MONTH,
        "days": None,
        "measure": None,
        "breakdown": None,
    },
    {
        "name": "sum_previous_month",
        "question": "Geçen ayın sipariş tutarı toplamı ne kadar?",
        "aggregation": AggregationKind.SUM,
        "temporal": TemporalKind.PREVIOUS_MONTH,
        "days": None,
        "measure": "amount",
        "breakdown": None,
    },
    {
        "name": "absolute_date_range",
        "question": "1 Eylül 2026 ile 15 Eylül 2026 arasındaki sipariş tutarı ne kadar?",
        "aggregation": AggregationKind.SUM,
        "temporal": TemporalKind.ABSOLUTE_DATE_RANGE,
        "days": None,
        "measure": "amount",
        "breakdown": None,
        "start_date": "2026-09-01",
        "end_date": "2026-09-15",
    },
    {
        "name": "count_no_time",
        "question": "Toplam kaç sipariş var?",
        "aggregation": AggregationKind.COUNT,
        "temporal": TemporalKind.NONE,
        "days": None,
        "measure": None,
        "breakdown": None,
    },
)


def _metabase_login(base_url: str) -> str:
    response = httpx.post(
        base_url + "/api/session",
        json={
            "username": os.environ["MB_ADMIN_EMAIL"],
            "password": os.environ["MB_ADMIN_PASSWORD"],
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("id")
    if not token:
        raise RuntimeError("Metabase login returned no session")
    return str(token)


def _settings() -> Settings:
    key = os.getenv("DIMA_OPENROUTER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY is unavailable")
    return Settings(
        llm_provider="openrouter",
        openrouter_api_key=key,
        openrouter_api_keys="",
        openrouter_model=MODEL,
        openrouter_select_model=MODEL,
        rule_fallback=False,
        v2_structured_reasoning_enabled=False,
        v2_structured_max_tokens=4096,
    )


def _field_by_name(candidates: tuple[FieldCandidate, ...], name: str) -> str | None:
    for item in candidates:
        if item.name.lower() == name.lower():
            return item.handle
    return None


def main() -> int:
    receipt: dict = {
        "status": "RED",
        "model": MODEL,
        "workers": 1,
        "supported_cases": [],
        "ambiguity_case": None,
        "unsupported_case": None,
        "invented_id_count": 0,
        "failures": [],
    }

    try:
        cognition = StructuredJsonFastCognition(build_generator(_settings()))
        base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
        metabase_session = _metabase_login(base_url)

        with FastMetabaseGateway(
            base_url=base_url,
            auth=FastMetabaseAuthContext(
                tenant_id="ft003-model-sentinel",
                dima_user_id="ft003-model-sentinel",
                principal_id="metabase-lab-admin",
                mode=FastMetabaseAuthMode.SESSION,
                secret=metabase_session,
                role_scope_digest="ft003-model-sentinel",
            ),
            policy=FastMetabaseRuntimePolicy(
                max_page_rows=200,
                max_total_rows_per_run=1000,
            ),
        ) as gateway:
            for case in SUPPORTED_CASES:
                observed: dict = {
                    "name": case["name"],
                    "question": case["question"],
                    "checks": {},
                }
                try:
                    draft = cognition.draft(question=case["question"])
                    observed["draft"] = draft.model_dump(mode="json")
                    observed["checks"]["schema_valid"] = True
                    observed["checks"]["supported_status_correct"] = (
                        draft.status == DraftStatus.SUPPORTED
                    )
                    if draft.status != DraftStatus.SUPPORTED:
                        raise RuntimeError(
                            f"supported request classified as {draft.status.value}: {draft.unsupported_reason}"
                        )
                    observed["checks"]["aggregation_correct"] = (
                        draft.aggregation == case["aggregation"]
                    )
                    observed["checks"]["temporal_kind_correct"] = (
                        draft.temporal.kind == case["temporal"]
                    )
                    observed["checks"]["days_correct"] = (
                        draft.temporal.days == case.get("days")
                    )
                    observed["checks"]["absolute_dates_correct"] = (
                        (
                            draft.temporal.start_date == case.get("start_date")
                            and draft.temporal.end_date == case.get("end_date")
                        )
                        if case["temporal"] == TemporalKind.ABSOLUTE_DATE_RANGE
                        else True
                    )

                    direct_search = gateway.search(
                        term_queries=draft.search_terms,
                        semantic_queries=(case["question"],),
                    )
                    direct_registry_names = {
                        str(item.get("name") or "").lower()
                        for item in direct_search.data
                        if str(item.get("type") or "").lower() == "table"
                    }
                    observed["measurements"] = {
                        "direct_search_hit": "orders" in direct_registry_names,
                    }
                    registry, discovery_mode = discover_resource_registry(
                        gateway,
                        term_queries=draft.search_terms,
                        semantic_query=case["question"],
                        max_candidates=8,
                    )
                    observed["retrieval_mode"] = discovery_mode
                    observed["checks"]["resource_candidates_available"] = bool(
                        registry.candidates
                    )
                    decision = cognition.select_resource(
                        question=case["question"],
                        candidates=registry.candidates,
                    )
                    offered = {item.handle for item in registry.candidates}
                    if decision.selected_handle is not None and decision.selected_handle not in offered:
                        receipt["invented_id_count"] += 1
                    selected_uri = (
                        registry.resource_uri(decision.selected_handle)
                        if decision.selected_handle in offered
                        else None
                    )
                    observed["checks"]["resource_handle_correct"] = (
                        selected_uri is not None
                        and any(
                            item.name.lower() == "orders"
                            and item.handle == decision.selected_handle
                            for item in registry.candidates
                        )
                    )

                    if selected_uri is not None:
                        item = gateway.read_resource((selected_uri + "/fields",)).resources[0]
                        details = (
                            item.content.structured_output
                            if item.content is not None and not item.failed
                            else None
                        )
                        if not isinstance(details, dict):
                            raise RuntimeError("orders fields resource unavailable")
                        fields = registry.bind_table_details(decision.selected_handle, details)

                        if case["aggregation"] == AggregationKind.SUM:
                            candidates = fields.public_for_measure()
                            field_decision = cognition.select_field(
                                question=case["question"],
                                purpose=SelectionPurpose.MEASURE,
                                hint=str(case["measure"]),
                                candidates=candidates,
                            )
                            offered_fields = {candidate.handle for candidate in candidates}
                            if (
                                field_decision.selected_handle is not None
                                and field_decision.selected_handle not in offered_fields
                            ):
                                receipt["invented_id_count"] += 1
                            observed["checks"]["measure_field_correct"] = (
                                field_decision.selected_handle
                                == _field_by_name(candidates, str(case["measure"]))
                            )
                        else:
                            observed["checks"]["measure_field_correct"] = True

                        if case["temporal"] != TemporalKind.NONE:
                            candidates = fields.public_for_temporal()
                            field_decision = cognition.select_field(
                                question=case["question"],
                                purpose=SelectionPurpose.TEMPORAL,
                                hint="date/time field relevant to the user's requested period",
                                candidates=candidates,
                            )
                            offered_fields = {candidate.handle for candidate in candidates}
                            if (
                                field_decision.selected_handle is not None
                                and field_decision.selected_handle not in offered_fields
                            ):
                                receipt["invented_id_count"] += 1
                            observed["checks"]["temporal_field_correct"] = (
                                field_decision.selected_handle
                                == _field_by_name(candidates, "order_date")
                            )
                        else:
                            observed["checks"]["temporal_field_correct"] = True

                        if case.get("breakdown"):
                            candidates = fields.public_for_breakdown()
                            field_decision = cognition.select_field(
                                question=case["question"],
                                purpose=SelectionPurpose.BREAKDOWN,
                                hint=str(case["breakdown"]),
                                candidates=candidates,
                            )
                            offered_fields = {candidate.handle for candidate in candidates}
                            if (
                                field_decision.selected_handle is not None
                                and field_decision.selected_handle not in offered_fields
                            ):
                                receipt["invented_id_count"] += 1
                            observed["checks"]["breakdown_field_correct"] = (
                                field_decision.selected_handle
                                == _field_by_name(candidates, str(case["breakdown"]))
                            )
                        else:
                            observed["checks"]["breakdown_field_correct"] = True

                    observed["passed"] = all(observed["checks"].values())
                except Exception as exc:
                    observed["passed"] = False
                    observed["error"] = f"{type(exc).__name__}: {exc}"
                receipt["supported_cases"].append(observed)

            # Material ambiguity: the model must abstain rather than guess one of two
            # equally plausible opaque resources.
            ambiguous_candidates = (
                ResourceCandidate(
                    handle="fast_res_001",
                    name="dataset_alpha",
                    display_name="Order Facts",
                    description="Permitted order facts",
                    resource_type="table",
                ),
                ResourceCandidate(
                    handle="fast_res_002",
                    name="dataset_beta",
                    display_name="Order Facts",
                    description="Permitted order facts",
                    resource_type="table",
                ),
            )
            try:
                ambiguity = cognition.select_resource(
                    question="Siparişleri say.",
                    candidates=ambiguous_candidates,
                )
                if (
                    ambiguity.selected_handle is not None
                    and ambiguity.selected_handle not in {item.handle for item in ambiguous_candidates}
                ):
                    receipt["invented_id_count"] += 1
                receipt["ambiguity_case"] = {
                    "question": "Siparişleri say.",
                    "selected_handle": ambiguity.selected_handle,
                    "passed": ambiguity.selected_handle is None,
                }
            except Exception as exc:
                receipt["ambiguity_case"] = {
                    "question": "Siparişleri say.",
                    "passed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }

            # FT-003 supports COUNT/SUM only. AVG must be explicitly typed UNSUPPORTED,
            # never coerced into an executable SUM/COUNT draft.
            unsupported_question = "Siparişlerin ortalama tutarı nedir?"
            try:
                unsupported = cognition.draft(question=unsupported_question)
                receipt["unsupported_case"] = {
                    "question": unsupported_question,
                    "observed_draft": unsupported.model_dump(mode="json"),
                    "passed": (
                        unsupported.status == DraftStatus.UNSUPPORTED
                        and bool((unsupported.unsupported_reason or "").strip())
                    ),
                    "reason": (
                        "typed unsupported"
                        if unsupported.status == DraftStatus.UNSUPPORTED
                        else "unsupported request was coerced into an executable supported draft"
                    ),
                }
            except Exception as exc:
                receipt["unsupported_case"] = {
                    "question": unsupported_question,
                    "passed": False,
                    "reason": "unsupported request did not produce the typed UNSUPPORTED contract",
                    "observed_error": f"{type(exc).__name__}: {exc}",
                }

        all_supported = all(item.get("passed") for item in receipt["supported_cases"])
        ambiguity_ok = bool((receipt["ambiguity_case"] or {}).get("passed"))
        unsupported_ok = bool((receipt["unsupported_case"] or {}).get("passed"))
        receipt["status"] = (
            "GREEN"
            if all_supported
            and ambiguity_ok
            and unsupported_ok
            and receipt["invented_id_count"] == 0
            else "RED"
        )

        if not all_supported:
            receipt["failures"].append("supported_case_failure")
        if not ambiguity_ok:
            receipt["failures"].append("ambiguity_abstention_failure")
        if not unsupported_ok:
            receipt["failures"].append("unsupported_contract_failure")
        if receipt["invented_id_count"]:
            receipt["failures"].append("invented_id")

    except Exception as exc:
        receipt["failures"].append(f"sentinel_setup:{type(exc).__name__}:{exc}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
