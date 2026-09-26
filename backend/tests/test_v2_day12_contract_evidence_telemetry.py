"""Day12 provider-free hardening: QueryContract audit lineage, Evidence identity, telemetry."""

from __future__ import annotations

import pytest

from app.v2.execution_receipts import build_query_contract_audit_receipt
from app.v2.manager_errors import ManagerAuthorityViolation
from app.v2.manager_executor import EvidenceStore
from app.v2.models import (
    AnalyticsIR,
    EvidenceArtifact,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
)
from app.v2.product_events import ProductEventSink
from app.v2.product_models import ProductEventKind


def _ir() -> AnalyticsIR:
    period = ResolvedPeriod(
        kind="relative",
        start="2026-01-01",
        end="2026-09-26",
        grain="month",
        source_text="this year",
    )
    return AnalyticsIR(
        cube="sales",
        metrics=(
            ResolvedSemanticRef(
                kind="metric",
                canonical_name="net_revenue",
                display_name="Net Revenue",
                model_name="sales",
            ),
        ),
        dimensions=(
            ResolvedSemanticRef(
                kind="dimension",
                canonical_name="region",
                display_name="Region",
                model_name="sales",
            ),
        ),
        filters=(),
        period=period,
        comparison=ResolvedComparison(
            base_period=period,
            compare_period=period.model_copy(
                update={
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


def test_evidence_store_rejects_second_canonical_evidence_for_same_task():
    store = EvidenceStore(
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day12",
    )
    store.put(_evidence())

    with pytest.raises(
        ManagerAuthorityViolation,
        match="ResearchTask already owns canonical Evidence",
    ):
        store.put(_evidence(artifact_id="evi_day12_b"))


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
