"""Manual-only Day 6.5 Manager architecture harness.

This does not alter production /ask-v2 routing. It wires the bounded Manager candidate
to the existing trust plane for explicit lab invocations only.
"""

from __future__ import annotations

from control_plane.authorize import Principal

from app.config import get_settings
from app.kaset import belki_sar
from app.llm import build_generator
from app.v2.acceptance import AcceptedContractRegistry, IntentAcceptanceGate
from app.v2.context_provider import ContextProviderV0
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_models import (
    ManagerRunSnapshot,
    ResearchRunTerminal,
    UserObligationLedger,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.model_policy import ModelRole, ModelRolePolicy
from app.v2.models import AskV2Request, FrozenModel
from app.v2.runtime_boundary import bind_runtime, request_ref, tenant_binding
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_authority import AcceptedAuthorityRegistry
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.semantic_linker import StructuredSemanticCandidateDecisionProvider
from app.v2.temporal_intent import StructuredTemporalNormalizationProvider


class ManagerLabResponse(FrozenModel):
    status: str = "manager_lab"
    model_role: str
    provider: str
    model: str
    semantic_linker_provider: str
    semantic_linker_model: str
    temporal_normalizer_provider: str
    temporal_normalizer_model: str
    snapshot: ManagerRunSnapshot
    run_finished: bool
    verified_complete: bool
    terminal_status: ResearchRunTerminal | None = None
    clarification_required: bool
    preacceptance_status: str | None = None
    ledger: UserObligationLedger | None = None
    observations: tuple[dict, ...] = ()


def _build_role_scoped_manager_models(settings):
    """Build the three selected cognition contracts from distinct ModelRole scopes."""
    policy = ModelRolePolicy(settings)

    research_settings, research_profile = policy.scoped_settings(
        ModelRole.RESEARCH_MANAGER
    )
    semantic_settings, semantic_profile = policy.scoped_settings(
        ModelRole.SEMANTIC_LINKER
    )
    temporal_settings, temporal_profile = policy.scoped_settings(
        ModelRole.TEMPORAL_NORMALIZER
    )

    research_llm = belki_sar(build_generator(research_settings))
    semantic_llm = belki_sar(build_generator(semantic_settings))
    temporal_llm = belki_sar(build_generator(temporal_settings))
    return (
        research_llm,
        research_profile,
        semantic_llm,
        semantic_profile,
        temporal_llm,
        temporal_profile,
    )


class ManagerLabHarness:
    def __init__(self) -> None:
        self._accepted_contracts = AcceptedContractRegistry()
        self._accepted_authorities = AcceptedAuthorityRegistry()

    def run(
        self,
        *,
        request,
        body: AskV2Request,
        principal: Principal,
    ) -> ManagerLabResponse:
        settings = get_settings()
        (
            llm,
            profile,
            linker_llm,
            linker_profile,
            temporal_llm,
            temporal_profile,
        ) = _build_role_scoped_manager_models(settings)

        service, schema, runtime = bind_runtime(request, principal)
        context = ContextProviderV0().build(service, runtime)
        binding = tenant_binding(runtime)

        source_spans = SourceSpanRegistry()
        semantic_handles = SemanticHandleRegistry()
        semantic_structured = getattr(linker_llm, "structured_json", None)
        temporal_structured = getattr(temporal_llm, "structured_json", None)
        semantic_provider = (
            StructuredSemanticCandidateDecisionProvider(structured=semantic_structured)
            if semantic_structured is not None
            else None
        )
        temporal_provider = (
            StructuredTemporalNormalizationProvider(structured=temporal_structured)
            if temporal_structured is not None
            else None
        )

        semantic_adapter = ManagerSemanticResolutionAdapter(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
            semantic_context=context,
            conversation=body.conversation,
            schema=schema,
            tenant_binding=binding,
            session_id=body.session_id,
            thread_id=body.thread_id,
            semantic_decision_provider=semantic_provider,
            temporal_normalization_provider=temporal_provider,
        )
        acceptance = IntentAcceptanceGate(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
        )
        core_adapter = ManagerCoreAnalyticsAdapter(
            semantic_handles=semantic_handles,
        )
        execution_context = GovernedManagerExecutionContext(
            tenant_binding=binding,
            context_version=context.context_version.version,
            principal=principal,
            service=service,
            tenant_runtime=runtime,
            contract_store=getattr(request.app.state, "contracts", None),
            session_id=body.session_id,
        )
        executor = GovernedManagerExecutor(
            acceptance=acceptance,
            core_analytics=core_adapter,
            context=execution_context,
            semantic_resolution=semantic_adapter,
        )
        ref = request_ref(body)
        manager_runtime = ManagerRuntime(
            request_ref=ref,
            contract_registry=self._accepted_contracts,
            authority_registry=self._accepted_authorities,
        )
        loop = ResearchManagerLoop(llm=llm, source_spans=source_spans)
        outcome = loop.run(
            question=body.question,
            message_id=f"turn:{ref}",
            request_ref=ref,
            runtime=manager_runtime,
            executor=executor,
            conversation=body.conversation,
        )
        return ManagerLabResponse(
            model_role=profile.role.value,
            provider=profile.provider,
            model=profile.model,
            semantic_linker_provider=linker_profile.provider,
            semantic_linker_model=linker_profile.model,
            temporal_normalizer_provider=temporal_profile.provider,
            temporal_normalizer_model=temporal_profile.model,
            snapshot=outcome.snapshot,
            run_finished=outcome.run_finished,
            verified_complete=outcome.verified_complete,
            terminal_status=outcome.terminal_status,
            clarification_required=outcome.clarification_required,
            preacceptance_status=(
                outcome.preacceptance_status.value
                if outcome.preacceptance_status is not None
                else None
            ),
            ledger=manager_runtime.ledger,
            observations=outcome.observations,
        )
