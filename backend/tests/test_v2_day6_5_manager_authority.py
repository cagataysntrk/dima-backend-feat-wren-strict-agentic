"""Focused provider-free Day 6.5 authority tests."""

from __future__ import annotations

import pytest

from app.v2.acceptance import (
    AcceptedAuthorityConflict,
    AcceptedContractRegistry,
    IntentAcceptanceGate,
)
from app.v2.completion import CompletionGate
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    RepresentabilityDecision,
    ResearchRunTerminal,
    StandardProjection,
    UserIntentEnvelope,
    UserObligationLedger,
)
from app.v2.models import (
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
    PeriodKind,
)
from app.v2.representability import RepresentabilityGate
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


def _setup():
    spans = SourceSpanRegistry()
    text = "ürünleri karşılaştır ve makinelerle ilişkisini incele"
    source_hash = spans.register_message(message_id="m1", text=text)
    comparison = spans.mint_exact(message_id="m1", surface="karşılaştır")
    relationship = spans.mint_exact(message_id="m1", surface="makinelerle ilişkisini incele")
    handles = SemanticHandleRegistry()
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-1",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-1",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    base = ResolvedPeriod(
        kind=PeriodKind.THIS_MONTH,
        source_text="bu ay",
        time_dimension="Sales.order_date",
        start="2026-09-01",
        end="2026-09-21",
    )
    comp = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="comparison-1",
        target_kind="comparison",
        canonical_target=ResolvedComparison(
            mode="previous_period",
            source_text="önceki ay",
            base_period=base,
            reference_period=ResolvedPeriod(
                kind=PeriodKind.PREVIOUS_MONTH,
                source_text="önceki ay",
                time_dimension="Sales.order_date",
                start="2026-08-01",
                end="2026-08-21",
            ),
        ),
    )
    return spans, handles, gate, source_hash, comparison, relationship, metric, comp


def _envelope(*obligations, source_hash: str, attempt: str = "a1", turn: str = "t1"):
    return UserIntentEnvelope(
        attempt_id=attempt,
        turn_id=turn,
        request_ref="req-1",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=tuple(obligations),
    )


def test_runtime_source_refs_and_foreign_handle_are_non_bypassable():
    _, handles, gate, source_hash, comparison, _, metric, _ = _setup()
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.COMPARISON,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(comparison.source_ref,),
        semantic_handle_refs=(metric.handle_id,),
    )
    bad = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash),
        tenant_binding="tenant-b",
        context_version="ctx-1",
    )
    assert bad.status.value == "REJECTED"
    assert any("foreign-tenant" in reason for reason in bad.reasons)

    fabricated = obligation.model_copy(update={"source_refs": ("src_" + "0" * 24,)})
    bad_source = gate.evaluate(
        envelope=_envelope(fabricated, source_hash=source_hash),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert bad_source.status.value == "REJECTED"


def test_exactly_one_accepted_authority_per_turn():
    _, _, gate, source_hash, comparison, _, metric, _ = _setup()
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(comparison.source_ref,),
        semantic_handle_refs=(metric.handle_id,),
    )
    accepted = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert accepted.contract is not None
    registry = AcceptedContractRegistry()
    registry.commit(accepted.contract)

    # Exact retry is idempotent.
    registry.commit(accepted.contract)

    # A different semantic authority for the same turn is forbidden.
    conflicting = accepted.contract.model_copy(
        update={"contract_id": "atc_" + "f" * 24}
    )
    with pytest.raises(AcceptedAuthorityConflict):
        registry.commit(conflicting)


def test_standard_lossless_requires_complete_projection():
    _, _, gate, source_hash, comparison, _, metric, comp = _setup()
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.COMPARISON,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(comparison.source_ref,),
        semantic_handle_refs=(metric.handle_id, comp.handle_id),
    )
    accepted = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    incomplete = RepresentabilityGate().decide(
        contract=accepted.contract,
        ledger=accepted.ledger,
        projection=StandardProjection(
            obligation_ids=("U1",),
            metric_handles=(metric.handle_id,),
        ),
    )
    assert incomplete.decision == RepresentabilityDecision.RESEARCH_REQUIRED

    complete = RepresentabilityGate().decide(
        contract=accepted.contract,
        ledger=accepted.ledger,
        projection=StandardProjection(
            obligation_ids=("U1",),
            metric_handles=(metric.handle_id,),
            comparison_handle=comp.handle_id,
        ),
    )
    assert complete.decision == RepresentabilityDecision.STANDARD_LOSSLESS


def test_relationship_remains_research_required():
    _, _, gate, source_hash, _, relationship, _, _ = _setup()
    obligation = CandidateObligation(
        obligation_id="U2",
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(relationship.source_ref,),
    )
    accepted = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash, turn="t2"),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    decision = RepresentabilityGate().decide(
        contract=accepted.contract,
        ledger=accepted.ledger,
    )
    assert decision.decision == RepresentabilityDecision.RESEARCH_REQUIRED


def test_evidence_presence_is_not_verification():
    ledger = UserObligationLedger(
        lineage_id="atl-1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.RELATIONSHIP,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.ACCEPTED,
                source_refs=("src_" + "1" * 24,),
                evidence_refs=("E1",),
                introduced_in_version=1,
            ),
        ),
    )
    result = CompletionGate().evaluate(ledger)
    assert result.allowed is False
    assert result.terminal is None


def test_partial_and_verified_complete_are_distinct():
    base = dict(
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        source_refs=("src_" + "1" * 24,),
        introduced_in_version=1,
    )
    partial = UserObligationLedger(
        lineage_id="atl-1",
        version=1,
        items=(
            ObligationLedgerItem(obligation_id="U1", status=ObligationStatus.VERIFIED, **base),
            ObligationLedgerItem(
                obligation_id="U2",
                status=ObligationStatus.BLOCKED_DATA_GAP,
                blocker="missing data",
                **base,
            ),
        ),
    )
    assert CompletionGate().evaluate(partial).terminal == ResearchRunTerminal.PARTIAL

    complete = UserObligationLedger(
        lineage_id="atl-2",
        version=1,
        items=(
            ObligationLedgerItem(obligation_id="U1", status=ObligationStatus.VERIFIED, **base),
        ),
    )
    result = CompletionGate().evaluate(complete)
    assert result.allowed is True
    assert result.terminal == ResearchRunTerminal.VERIFIED_COMPLETE
