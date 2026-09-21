"""Small provider-free Day 6.5 correctness closure (S1-S8)."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from app.v2.completion import CompletionGate
from app.v2.manager_errors import ManagerSemanticGap
from app.v2.manager_loop import ManagerDecisionTransport, _strict_native_schema
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ManagerState,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    ResearchRunTerminal,
    StandardProjection,
    UserObligationLedger,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import (
    ManagerRelationshipObservation,
    ManagerToolCall,
    ManagerToolName,
    ResolveSemanticsArgs,
    RunRelationshipArgs,
)
from app.v2.models import (
    AnalyticsIR,
    BoundedSemanticContextV0,
    ComparisonSurface,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    EvidenceArtifact,
    PeriodKind,
    ResolvedPeriod,
    ResolvedRanking,
    ResolvedSemanticRef,
    SemanticMention,
    SemanticMentionKind,
    SemanticTargetKind,
)
from app.v2.obligation_verifier import StandardObligationVerifier
from app.v2.resolver import SemanticResolver
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.temporal import resolve_comparison, resolve_period


def _obligation(capability, *, handles=()):
    return ObligationLedgerItem(
        obligation_id="U1",
        capability_key=capability,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.IN_PROGRESS,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=handles,
        introduced_in_version=1,
    )


def _evidence():
    return EvidenceArtifact(
        artifact_id="evi_" + "1" * 24,
        task_id="T1",
        obligation_ids=("U1",),
        query_contract_refs=("QC1",),
        evidence_kind="standard_analytics",
        verified=True,
    )


def _metric_ir():
    return AnalyticsIR(
        cube="Sales",
        metrics=(
            ResolvedSemanticRef(
                candidate_id="m1",
                target_kind=SemanticTargetKind.METRIC,
                canonical_name="Sales.revenue",
                cube_names=("Sales",),
            ),
        ),
        context_version="ctx-1",
    )


def test_s1_plain_metric_query_does_not_verify_comparison():
    proof = StandardObligationVerifier().verify(
        obligation=_obligation(
            ManagerCapabilityKey.COMPARISON,
            handles=("sem_" + "1" * 24, "sem_" + "2" * 24),
        ),
        projection=StandardProjection(
            obligation_ids=("U1",),
            metric_handles=("sem_" + "1" * 24,),
        ),
        ir=_metric_ir(),
        evidence=_evidence(),
    )
    assert proof.verified is False
    assert any("comparison" in reason for reason in proof.reasons)


def test_s2_plain_metric_query_does_not_verify_ranking():
    proof = StandardObligationVerifier().verify(
        obligation=_obligation(
            ManagerCapabilityKey.RANKING,
            handles=("sem_" + "1" * 24,),
        ),
        projection=StandardProjection(
            obligation_ids=("U1",),
            metric_handles=("sem_" + "1" * 24,),
        ),
        ir=_metric_ir(),
        evidence=_evidence(),
    )
    assert proof.verified is False
    assert any("ranking" in reason for reason in proof.reasons)


def test_s4_agent_derived_semantic_resolution_can_discover_tenant_dimension():
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-1",
            mdl_version="mdl-1",
            compact_catalog_builder_version="v1",
            business_rules_hash="x",
            prompt_context_policy_version="v1",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="Production",
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="Production.shift",
                        display="Vardiya",
                        synonyms=("vardiya",),
                    ),
                ),
            ),
        ),
    )
    handles = SemanticHandleRegistry()
    adapter = ManagerSemanticResolutionAdapter(
        resolver=SemanticResolver(signing_key=b"x" * 32),
        source_spans=SourceSpanRegistry(),
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema={
            "cubes": [
                {
                    "name": "Production",
                    "measures": [],
                    "dimensions": ["Production.shift"],
                }
            ]
        },
        tenant_binding="tenant-a",
        session_id=None,
        thread_id=None,
    )
    result = adapter.resolve(
        ResolveSemanticsArgs(
            provenance="AGENT_DERIVED",
            target_kind_hints=("dimension",),
            parent_obligation_id="U2",
            evidence_ref="E7",
            natural_language_proposal="vardiya",
        )
    )
    assert len(result.resolved) == 1
    assert result.resolved[0].handle.provenance_type == "AGENT_DERIVED"
    assert result.resolved[0].handle.parent_obligation_id == "U2"
    assert result.resolved[0].handle.trigger_evidence_ref == "E7"


def test_s5_relationship_unavailable_becomes_typed_unsupported_not_exception():
    ledger = UserObligationLedger(
        lineage_id="atl-1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="Urel",
                capability_key=ManagerCapabilityKey.RELATIONSHIP,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.ACCEPTED,
                source_refs=("src_" + "1" * 24,),
                introduced_in_version=1,
            ),
        ),
    )

    class Runtime:
        def __init__(self):
            self.ledger = ledger
            self.snapshot = SimpleNamespace(evidence_refs=())

        def replace_ledger(self, value):
            self.ledger = value

    executor = GovernedManagerExecutor(
        acceptance=object(),
        core_analytics=object(),
        context=GovernedManagerExecutionContext(
            tenant_binding="tenant-a",
            context_version="ctx-1",
            principal=None,
            service=None,
            tenant_runtime=None,
            contract_store=None,
        ),
    )
    runtime = Runtime()
    result = executor.execute(
        ManagerToolCall(name=ManagerToolName.RUN_RELATIONSHIP, args={}),
        RunRelationshipArgs(
            obligation_id="Urel",
            focus_handles=("sem_" + "1" * 24,),
            counterpart_handles=("sem_" + "2" * 24,),
        ),
        runtime,
    )
    assert isinstance(result, ManagerRelationshipObservation)
    assert result.status == "UNSUPPORTED"
    assert runtime.ledger.items[0].status == ObligationStatus.UNSUPPORTED


def test_s6_recoverable_tool_error_does_not_fail_runtime():
    class RecoverableExecutor:
        def execute(self, call, validated_args, runtime):
            raise ManagerSemanticGap("wrong semantic handle type")

    runtime = ManagerRuntime(request_ref="r1")
    runtime.begin_understanding()
    call = ManagerToolCall(
        name=ManagerToolName.RESOLVE_SEMANTICS,
        args={
            "provenance": "USER_SOURCE",
            "source_refs": ("src_" + "1" * 24,),
            "target_kind_hints": ("metric",),
        },
    )
    with pytest.raises(ManagerSemanticGap):
        runtime.call_tool(call, executor=RecoverableExecutor())
    assert runtime.snapshot.state == ManagerState.UNDERSTANDING


def test_s7_partial_terminal_is_preserved_on_snapshot():
    runtime = ManagerRuntime(request_ref="r2")
    runtime._ledger = UserObligationLedger(
        lineage_id="atl-1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=("src_" + "1" * 24,),
                introduced_in_version=1,
            ),
            ObligationLedgerItem(
                obligation_id="U2",
                capability_key=ManagerCapabilityKey.RELATIONSHIP,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.BLOCKED_DATA_GAP,
                source_refs=("src_" + "2" * 24,),
                blocker="missing data",
                introduced_in_version=1,
            ),
        ),
    )
    snapshot = runtime.finish(CompletionGate())
    assert snapshot.state == ManagerState.COMPLETED
    assert snapshot.terminal_status == ResearchRunTerminal.PARTIAL


def test_s8_last_12_months_previous_12_months_is_typed():
    base = resolve_period(
        (SemanticMention(text="son 12 ay", kind=SemanticMentionKind.TIME),),
        time_dimension="Sales.order_date",
        today=date(2026, 9, 21),
    )
    comparison = resolve_comparison(
        (ComparisonSurface(text="geçen 12 ayla"),),
        base_period=base,
        time_dimension="Sales.order_date",
        today=date(2026, 9, 21),
    )
    assert base is not None and base.kind == PeriodKind.LAST_N_MONTHS and base.n == 12
    assert comparison is not None
    assert comparison.reference_period.kind == PeriodKind.LAST_N_MONTHS
    assert comparison.reference_period.n == 12
    assert comparison.reference_period.end < comparison.base_period.start


def test_manager_native_schema_is_strict_provider_compatible():
    schema = _strict_native_schema(ManagerDecisionTransport.model_json_schema())

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "object" or "properties" in node:
                properties = set((node.get("properties") or {}).keys())
                required = set(node.get("required") or ())
                assert required == properties
                assert node.get("additionalProperties") is False
                assert "default" not in node
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
