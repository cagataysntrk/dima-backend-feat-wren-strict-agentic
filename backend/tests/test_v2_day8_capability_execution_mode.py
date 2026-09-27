"""Provider-free D8-C0 tests for capability execution-mode authority."""

from __future__ import annotations

from app.v2.capability_bindings import CapabilityBindingValidator
from app.v2.manager_models import (
    AcceptedTurnContract,
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    RepresentabilityDecision,
    StandardProjection,
    UserObligationLedger,
)
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityRegistry,
)
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.representability import RepresentabilityGate
from app.v2.semantic_handles import SemanticHandleRegistry


TENANT = "tenant-d8-c0"
CTX = "ctx-d8-c0"
ROOT = "U_ROOT"


def _metric(handles: SemanticHandleRegistry):
    return handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id="resolver:d8:c0:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="d8-c0-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Ops.oee",
            cube_names=("Ops",),
        ),
        parent_obligation_id=ROOT,
    )


def _root_item(metric_ref: str) -> ObligationLedgerItem:
    return ObligationLedgerItem(
        obligation_id=ROOT,
        capability_key=ManagerCapabilityKey.ROOT_CAUSE,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.ACCEPTED,
        source_refs=("src_" + "a" * 24,),
        semantic_handle_refs=(metric_ref,),
        introduced_in_version=1,
    )


def _authority(item: ObligationLedgerItem):
    ledger = UserObligationLedger(lineage_id="lin-d8-c0", version=1, items=(item,))
    contract = AcceptedTurnContract(
        contract_id="atc-d8-c0",
        lineage_id=ledger.lineage_id,
        version=ledger.version,
        turn_id="turn-d8-c0",
        request_ref="req-d8-c0",
        source_message_hash="b" * 64,
        accepted_attempt_id="attempt-d8-c0",
        model_role="RESEARCH_MANAGER",
        obligation_ids=(item.obligation_id,),
        context_version=CTX,
        accepted_at_iso="2026-09-23T00:00:00+00:00",
    )
    return contract, ledger


def test_execution_mode_is_single_capability_truth():
    registry = ManagerCapabilityRegistry()
    assert registry.get(ManagerCapabilityKey.PERFORMANCE).execution_mode == ManagerCapabilityExecutionMode.DIRECT
    assert registry.get(ManagerCapabilityKey.RELATIONSHIP).execution_mode == ManagerCapabilityExecutionMode.DIRECT
    assert registry.get(ManagerCapabilityKey.ROOT_CAUSE).execution_mode == ManagerCapabilityExecutionMode.ORCHESTRATED
    assert registry.get(ManagerCapabilityKey.TREND).execution_mode == ManagerCapabilityExecutionMode.DEFERRED
    assert registry.get(ManagerCapabilityKey.REPORT).execution_mode == ManagerCapabilityExecutionMode.PRESENTATION


def test_executable_is_derived_direct_only_compatibility_view():
    registry = ManagerCapabilityRegistry()
    assert registry.get(ManagerCapabilityKey.PERFORMANCE).executable is True
    assert registry.get(ManagerCapabilityKey.ROOT_CAUSE).executable is False
    assert registry.get(ManagerCapabilityKey.TREND).executable is False
    assert registry.get(ManagerCapabilityKey.REPORT).executable is False


def test_root_cause_is_semantically_bindable_without_becoming_direct():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    result = CapabilityBindingValidator(semantic_handles=handles).validate(
        _root_item(metric.handle_id),
        tenant_binding=TENANT,
        context_version=CTX,
    )
    assert result.valid is True
    assert result.binding is not None
    assert result.binding.refs("metric") == (metric.handle_id,)
    assert result.binding.spec.execution_mode == ManagerCapabilityExecutionMode.ORCHESTRATED
    assert result.binding.spec.executable is False


def test_deferred_trend_stays_unavailable_to_current_binding_surface():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    item = _root_item(metric.handle_id).model_copy(
        update={"capability_key": ManagerCapabilityKey.TREND}
    )
    result = CapabilityBindingValidator(semantic_handles=handles).validate(
        item,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    assert result.valid is False
    assert any("deferred" in reason for reason in result.reasons)


def test_root_cause_routes_to_research_without_direct_projection():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    item = _root_item(metric.handle_id)
    contract, ledger = _authority(item)

    decision = RepresentabilityGate().decide(
        contract=contract,
        ledger=ledger,
        projection=StandardProjection(
            obligation_ids=(ROOT,),
            metric_handles=(metric.handle_id,),
        ),
    )
    assert decision.decision == RepresentabilityDecision.RESEARCH_REQUIRED
    assert decision.research_capability_keys == (ManagerCapabilityKey.ROOT_CAUSE,)


def test_existing_direct_standard_capability_remains_lossless():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    item = _root_item(metric.handle_id).model_copy(
        update={"capability_key": ManagerCapabilityKey.PERFORMANCE}
    )
    contract, ledger = _authority(item)
    decision = RepresentabilityGate().decide(
        contract=contract,
        ledger=ledger,
        projection=StandardProjection(
            obligation_ids=(ROOT,),
            metric_handles=(metric.handle_id,),
        ),
    )
    assert decision.decision == RepresentabilityDecision.STANDARD_LOSSLESS
