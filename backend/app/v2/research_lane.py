"""Production-owned Day10 RESEARCH lane construction.

This module extracts the canonical governed Research construction from the historical
manager lab without importing lab code. Product infrastructure context is supplied by
the front door; semantic authority is always created fresh inside the Research lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.llm import build_generator
from app.v2.acceptance import AcceptedContractRegistry, IntentAcceptanceGate
from app.v2.cross_domain_facts import CrossDomainJoinFactBuilder
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    EvidenceStore,
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import ManagerLoopOutcome, ResearchManagerLoop
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.model_policy import ModelProfile, ModelRole, ModelRolePolicy
from app.v2.models import AskV2Request, ConversationStateV2, EvidenceArtifact, EvidenceLinkedFinding
from app.v2.product_models import ProductRequestContext
from app.v2.relationship_adapter import (
    GovernedRelationshipAdapter,
    GovernedRelationshipExecutionContext,
)
from app.v2.research_tools import ResearchToolRunner
from app.v2.root_cause_orchestration import RootCauseLoopContext
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import StructuredSemanticCandidateDecisionProvider
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_authority import AcceptedAuthorityRegistry
from app.v2.temporal_intent import StructuredTemporalNormalizationProvider


@dataclass(frozen=True)
class ResearchCognition:
    manager_llm: Any
    manager_profile: ModelProfile
    semantic_provider: Any
    semantic_profile: ModelProfile
    temporal_provider: Any
    temporal_profile: ModelProfile


@dataclass(frozen=True)
class ResearchLaneResult:
    outcome: ManagerLoopOutcome
    evidence: tuple[EvidenceArtifact, ...]
    findings: tuple[EvidenceLinkedFinding, ...]
    runtime: ManagerRuntime
    evidence_store: EvidenceStore
    semantic_handles: SemanticHandleRegistry
    accepted_contract: Any
    ledger: Any

    @property
    def verified_complete(self) -> bool:
        return self.outcome.verified_complete


def build_research_cognition(settings) -> ResearchCognition:
    """Build only the sealed role-scoped cognition surfaces used by Research."""

    policy = ModelRolePolicy(settings)
    manager_settings, manager_profile = policy.scoped_settings(
        ModelRole.RESEARCH_MANAGER
    )
    semantic_settings, semantic_profile = policy.scoped_settings(
        ModelRole.SEMANTIC_LINKER
    )
    temporal_settings, temporal_profile = policy.scoped_settings(
        ModelRole.TEMPORAL_NORMALIZER
    )

    manager_llm = build_generator(manager_settings)
    semantic_llm = build_generator(semantic_settings)
    temporal_llm = build_generator(temporal_settings)

    semantic_structured = getattr(semantic_llm, "structured_json", None)
    temporal_structured = getattr(temporal_llm, "structured_json", None)
    return ResearchCognition(
        manager_llm=manager_llm,
        manager_profile=manager_profile,
        semantic_provider=(
            StructuredSemanticCandidateDecisionProvider(
                structured=semantic_structured
            )
            if callable(semantic_structured)
            else None
        ),
        semantic_profile=semantic_profile,
        temporal_provider=(
            StructuredTemporalNormalizationProvider(
                structured=temporal_structured
            )
            if callable(temporal_structured)
            else None
        ),
        temporal_profile=temporal_profile,
    )


class ResearchLaneService:
    """Production RESEARCH lane; owns construction, not underlying truth engines."""

    def __init__(
        self,
        *,
        cognition: ResearchCognition,
        contract_registry: AcceptedContractRegistry | None = None,
        authority_registry: AcceptedAuthorityRegistry | None = None,
    ) -> None:
        self._cognition = cognition
        self._contracts = contract_registry or AcceptedContractRegistry()
        self._authorities = authority_registry or AcceptedAuthorityRegistry()

    @classmethod
    def from_settings(cls, settings) -> "ResearchLaneService":
        return cls(cognition=build_research_cognition(settings))

    def run(
        self,
        *,
        context: ProductRequestContext,
        body: AskV2Request,
        progress_callback: Callable[[str, tuple[str, ...]], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> ResearchLaneResult:
        # Lane-local semantic authority. Nothing from a rejected Standard candidate is
        # accepted as an input to this construction seam.
        source_spans = SourceSpanRegistry()
        semantic_handles = SemanticHandleRegistry()

        semantic_adapter = ManagerSemanticResolutionAdapter(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
            semantic_context=context.semantic_context,
            conversation=body.conversation,
            schema=context.schema,
            tenant_binding=context.tenant_binding,
            session_id=body.session_id,
            thread_id=body.thread_id,
            semantic_decision_provider=self._cognition.semantic_provider,
            temporal_normalization_provider=self._cognition.temporal_provider,
        )
        acceptance = IntentAcceptanceGate(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
        )
        core_adapter = ManagerCoreAnalyticsAdapter(
            semantic_handles=semantic_handles,
        )
        execution_context = GovernedManagerExecutionContext(
            tenant_binding=context.tenant_binding,
            context_version=context.semantic_context.context_version.version,
            principal=context.principal,
            service=context.service,
            tenant_runtime=context.tenant_runtime,
            contract_store=context.contract_store,
            session_id=body.session_id,
        )
        relationship_adapter = GovernedRelationshipAdapter(
            fact_builder=CrossDomainJoinFactBuilder(
                semantic_handles=semantic_handles,
                tenant_binding=context.tenant_binding,
                context_version=context.semantic_context.context_version.version,
            ),
            core_analytics=core_adapter,
            context=GovernedRelationshipExecutionContext(
                tenant_binding=context.tenant_binding,
                principal=context.principal,
                service=context.service,
                tenant_runtime=context.tenant_runtime,
                contract_store=context.contract_store,
                session_id=body.session_id,
            ),
        )
        executor = GovernedManagerExecutor(
            acceptance=acceptance,
            core_analytics=core_adapter,
            context=execution_context,
            semantic_resolution=semantic_adapter,
            relationship=relationship_adapter,
        )
        manager_runtime = ManagerRuntime(
            request_ref=context.request_ref,
            contract_registry=self._contracts,
            authority_registry=self._authorities,
        )
        loop = ResearchManagerLoop(
            llm=self._cognition.manager_llm,
            source_spans=source_spans,
            research_tool_runner=ResearchToolRunner(),
            root_cause_context=RootCauseLoopContext(
                semantic_handles=semantic_handles,
                tenant_binding=context.tenant_binding,
                context_version=context.semantic_context.context_version.version,
            ),
            progress_callback=progress_callback,
            cancel_check=cancel_check,
        )
        outcome = loop.run(
            question=body.question,
            message_id=f"turn:{context.request_ref}",
            request_ref=context.request_ref,
            runtime=manager_runtime,
            executor=executor,
            conversation=body.conversation,
        )

        evidence: list[EvidenceArtifact] = []
        for evidence_ref in manager_runtime.snapshot.evidence_refs:
            item = executor.evidence_store.get(evidence_ref)
            if item.verified:
                evidence.append(item)

        return ResearchLaneResult(
            outcome=outcome,
            evidence=tuple(evidence),
            findings=outcome.findings,
            runtime=manager_runtime,
            evidence_store=executor.evidence_store,
            semantic_handles=semantic_handles,
            accepted_contract=manager_runtime.accepted_contract,
            ledger=manager_runtime.ledger,
        )


    def continue_run(
        self,
        *,
        context: ProductRequestContext,
        body: AskV2Request,
        prior: ResearchLaneResult,
        conversation: ConversationStateV2,
        section_scope_refs: tuple[str, ...],
        context_scope_by_kind: dict[str, tuple[str, ...]],
        progress_callback: Callable[[str, tuple[str, ...]], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> ResearchLaneResult:
        """Continue one signed report section on the same immutable Research lineage."""

        semantic_handles = prior.semantic_handles
        source_spans = SourceSpanRegistry()
        semantic_adapter = ManagerSemanticResolutionAdapter(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
            semantic_context=context.semantic_context,
            conversation=conversation,
            schema=context.schema,
            tenant_binding=context.tenant_binding,
            session_id=body.session_id,
            thread_id=body.thread_id,
            semantic_decision_provider=self._cognition.semantic_provider,
            temporal_normalization_provider=self._cognition.temporal_provider,
        )
        acceptance = IntentAcceptanceGate(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
            allowed_context_scope_refs=section_scope_refs,
        )
        core_adapter = ManagerCoreAnalyticsAdapter(
            semantic_handles=semantic_handles,
        )
        execution_context = GovernedManagerExecutionContext(
            tenant_binding=context.tenant_binding,
            context_version=context.semantic_context.context_version.version,
            principal=context.principal,
            service=context.service,
            tenant_runtime=context.tenant_runtime,
            contract_store=context.contract_store,
            session_id=body.session_id,
        )
        relationship_adapter = GovernedRelationshipAdapter(
            fact_builder=CrossDomainJoinFactBuilder(
                semantic_handles=semantic_handles,
                tenant_binding=context.tenant_binding,
                context_version=context.semantic_context.context_version.version,
            ),
            core_analytics=core_adapter,
            context=GovernedRelationshipExecutionContext(
                tenant_binding=context.tenant_binding,
                principal=context.principal,
                service=context.service,
                tenant_runtime=context.tenant_runtime,
                contract_store=context.contract_store,
                session_id=body.session_id,
            ),
        )
        executor = GovernedManagerExecutor(
            acceptance=acceptance,
            core_analytics=core_adapter,
            context=execution_context,
            evidence=prior.evidence_store,
            semantic_resolution=semantic_adapter,
            relationship=relationship_adapter,
        )

        manager_runtime = prior.runtime
        manager_runtime.begin_followup_turn()
        loop = ResearchManagerLoop(
            llm=self._cognition.manager_llm,
            source_spans=source_spans,
            research_tool_runner=ResearchToolRunner(),
            root_cause_context=RootCauseLoopContext(
                semantic_handles=semantic_handles,
                tenant_binding=context.tenant_binding,
                context_version=context.semantic_context.context_version.version,
            ),
            progress_callback=progress_callback,
            cancel_check=cancel_check,
            context_scope_by_kind=context_scope_by_kind,
        )
        outcome = loop.run(
            question=body.question,
            message_id=f"turn:{context.request_ref}",
            request_ref=context.request_ref,
            runtime=manager_runtime,
            executor=executor,
            conversation=conversation,
        )

        evidence: list[EvidenceArtifact] = []
        for evidence_ref in manager_runtime.snapshot.evidence_refs:
            item = executor.evidence_store.get(evidence_ref)
            if item.verified:
                evidence.append(item)

        findings_by_id = {
            item.finding_id: item
            for item in (*prior.findings, *outcome.findings)
        }
        return ResearchLaneResult(
            outcome=outcome,
            evidence=tuple(evidence),
            findings=tuple(findings_by_id.values()),
            runtime=manager_runtime,
            evidence_store=executor.evidence_store,
            semantic_handles=semantic_handles,
            accepted_contract=manager_runtime.accepted_contract,
            ledger=manager_runtime.ledger,
        )
