"""Day12 provider-free hardening: QueryContract audit lineage, Evidence identity, telemetry."""

from __future__ import annotations

import pytest

from app.v2.execution_receipts import (
    build_development_performance_receipt,
    build_query_contract_audit_receipt,
)
from app.v2.manager_errors import ManagerAuthorityViolation
from app.v2.manager_executor import EvidenceStore
from app.v2.models import (
    AnalyticsIR,
    EvidenceArtifact,
    PeriodKind,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.product_events import ProductEventSink
from app.v2.product_models import ProductEventKind


def _ir() -> AnalyticsIR:
    period = ResolvedPeriod(
        kind=PeriodKind.THIS_YEAR,
        source_text="this year",
        time_dimension="order_date",
        start="2026-01-01",
        end="2026-09-26",
    )
    return AnalyticsIR(
        cube="sales",
        metrics=(
            ResolvedSemanticRef(
                candidate_id="cand_metric",
                target_kind=SemanticTargetKind.METRIC,
                canonical_name="net_revenue",
                cube_names=("sales",),
            ),
        ),
        dimensions=(
            ResolvedSemanticRef(
                candidate_id="cand_dimension",
                target_kind=SemanticTargetKind.DIMENSION,
                canonical_name="region",
                cube_names=("sales",),
            ),
        ),
        filters=(),
        period=period,
        comparison=ResolvedComparison(
            base_period=period,
            reference_period=period.model_copy(
                update={
                    "kind": PeriodKind.PREVIOUS_YEAR,
                    "start": "2025-01-01",
                    "end": "2025-09-26",
                    "source_text": "prior year",
                }
            ),
            mode="previous_period",
            source_text="vs prior year",
        ),
        context_version="ctx-day12",
    )


def _evidence(**updates) -> EvidenceArtifact:
    base = EvidenceArtifact(
        artifact_id="evi_day12_a",
        task_id="task-day12",
        obligation_ids=("U1",),
        query_contract_refs=("c-day12",),
        evidence_kind="standard_analytics",
        verified=True,
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day12",
        run_id="mgr-day12",
        lineage_id="atl-day12",
        accepted_contract_id="atc-day12",
    )
    return base.model_copy(update=updates)


def test_query_contract_audit_receipt_is_explicit_and_secret_minimized():
    receipt = build_query_contract_audit_receipt(
        execution_id="exec-1",
        accepted_authority_ref="atc-day12",
        obligation_ids=("U1",),
        requested_capabilities=("performance", "comparison", "breakdown"),
        semantic_handle_refs=("sem_metric", "sem_dimension", "sem_period"),
        analytics_ir=_ir(),
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day12",
        planner_id="planner",
        planner_version="v1",
        research_run_id="mgr-day12",
        research_task_id="task-day12",
    )

    assert receipt["accepted_authority_ref"] == "atc-day12"
    assert receipt["requested_capabilities"] == [
        "performance",
        "comparison",
        "breakdown",
    ]
    assert receipt["obligation_ids"] == ["U1"]
    assert receipt["canonical_semantic_refs"]["metrics"] == ["net_revenue"]
    assert receipt["canonical_semantic_refs"]["dimensions"] == ["region"]
    assert receipt["model_cube_authority"] == "sales"
    assert receipt["grain"] == ["region"]
    assert receipt["period"] is not None
    assert receipt["comparison"] is not None
    assert receipt["execution_identity"] == {
        "execution_id": "exec-1",
        "research_run_id": "mgr-day12",
        "research_task_id": "task-day12",
    }
    assert receipt["tenant_principal_context"] == {
        "tenant_binding": "tenant:a",
        "principal_subject": "user-a",
        "context_version": "ctx-day12",
    }
    assert "sql" not in receipt
    assert "rows" not in receipt
    assert "provider_message" not in receipt


def test_evidence_store_exact_replay_is_idempotent():
    store = EvidenceStore(
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day12",
    )
    evidence = _evidence()

    store.put(evidence)
    store.put(evidence)

    assert store.count == 1
    assert store.get(evidence.artifact_id) == evidence


def test_evidence_store_rejects_same_artifact_identity_with_different_truth():
    store = EvidenceStore(
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day12",
    )
    store.put(_evidence())

    with pytest.raises(ManagerAuthorityViolation, match="Evidence identity conflict"):
        store.put(_evidence(payload={"changed": True}))


def test_evidence_store_allows_distinct_artifacts_for_same_task_without_identity_laundering():
    store = EvidenceStore(
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day12",
    )
    first = _evidence()
    second = _evidence(
        artifact_id="evi_day12_b",
        query_contract_refs=("c-day12-b",),
    )

    store.put(first)
    store.put(second)

    assert store.count == 2
    assert store.get(first.artifact_id) == first
    assert store.get(second.artifact_id) == second


@pytest.mark.parametrize(
    ("field", "value", "needle"),
    [
        ("tenant_binding", "tenant:b", "tenant scope mismatch"),
        ("principal_subject", "user-b", "principal scope mismatch"),
        ("context_version", "ctx-stale", "context scope mismatch"),
    ],
)
def test_evidence_store_rejects_foreign_or_stale_scope(field, value, needle):
    store = EvidenceStore(
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day12",
    )

    with pytest.raises(ManagerAuthorityViolation, match=needle):
        store.put(_evidence(**{field: value}))


def test_product_events_remain_diagnostic_not_truth_authority():
    sink = ProductEventSink(request_ref="req-day12", turn_ref="turn-day12")
    event = sink.emit(
        ProductEventKind.EVIDENCE_VERIFIED,
        refs=("evi_day12_a",),
        transition_ref="transition-1",
    )
    replay = sink.emit(
        ProductEventKind.EVIDENCE_VERIFIED,
        refs=("evi_day12_a",),
        transition_ref="transition-1",
    )

    assert replay == event
    assert sink.events == (event,)
    assert event.refs == ("evi_day12_a",)
    assert not hasattr(event, "verified")
    assert not hasattr(event, "query_contract")


def test_performance_receipt_is_diagnostic_and_never_claims_p95():
    receipt = build_development_performance_receipt(
        first_status_ms=3,
        first_verified_evidence_ms=420,
        report_ready_ms=900,
        total_ms=1100,
        provider_calls_by_role={
            "RESEARCH_MANAGER": 3,
            "SEMANTIC_LINKER": 1,
        },
        wren_query_calls=2,
        wren_dry_plan_calls=2,
        wren_cube_sql_calls=2,
        manager_turns=4,
    )

    assert receipt["sample_count"] == 1
    assert receipt["p95_claim"] is False
    assert receipt["diagnostic_only"] is True
    assert receipt["provider_calls_by_role"] == {
        "RESEARCH_MANAGER": 3,
        "SEMANTIC_LINKER": 1,
    }
    assert receipt["wren_calls"] == {
        "query": 2,
        "dry_plan": 2,
        "cube_sql": 2,
    }
    assert "verified_complete" not in receipt
    assert "authority" not in receipt
