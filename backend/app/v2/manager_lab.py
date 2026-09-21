"""Manual-only Day 6.5 Manager architecture harness.

This does not alter production /ask-v2 routing. It wires the bounded Manager candidate
to the existing trust plane for explicit lab invocations only.
"""

from __future__ import annotations

from control_plane.authorize import Principal
from control_plane.security import derive_hmac_key

from app.config import get_settings
from app.kaset import belki_sar
from app.llm import build_generator
from app.v2.acceptance import IntentAcceptanceGate
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
from app.v2.resolver import SemanticResolver
from app.v2.runtime_boundary import bind_runtime, request_ref, tenant_binding
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter


class ManagerLabResponse(FrozenModel):
    status: str = "manager_lab"
    model_role: str
    provider: str
    model: str
    snapshot: ManagerRunSnapshot
    run_finished: bool
    verified_complete: bool
    terminal_status: ResearchRunTerminal | None = None
    clarification_required: bool
    ledger: UserObligationLedger | None = None
    observations: tuple[dict, ...] = ()


class ManagerLabHarness:
    def run(
        self,
        *,
        request,
        body: AskV2Request,
        principal: Principal,
    ) -> ManagerLabResponse:
        settings = get_settings()
        scoped_settings, profile = ModelRolePolicy(settings).scoped_settings(
            ModelRole.RESEARCH_MANAGER
        )
        llm = belki_sar(build_generator(scoped_settings))

        service, schema, runtime = bind_runtime(request, principal)
        context = ContextProviderV0().build(service, runtime)
        binding = tenant_binding(runtime)

        source_spans = SourceSpanRegistry()
        semantic_handles = SemanticHandleRegistry()
        resolver = SemanticResolver(
            signing_key=derive_hmac_key("v2-manager-clarification-v1")
        )
        semantic_adapter = ManagerSemanticResolutionAdapter(
            resolver=resolver,
            source_spans=source_spans,
            semantic_handles=semantic_handles,
            semantic_context=context,
            conversation=body.conversation,
            schema=schema,
            tenant_binding=binding,
            session_id=body.session_id,
            thread_id=body.thread_id,
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
        manager_runtime = ManagerRuntime(request_ref=ref)
        loop = ResearchManagerLoop(llm=llm, source_spans=source_spans)
        outcome = loop.run(
            question=body.question,
            message_id=f"turn:{ref}",
            request_ref=ref,
            runtime=manager_runtime,
            executor=executor,
        )
        return ManagerLabResponse(
            model_role=profile.role.value,
            provider=profile.provider,
            model=profile.model,
            snapshot=outcome.snapshot,
            run_finished=outcome.run_finished,
            verified_complete=outcome.verified_complete,
            terminal_status=outcome.terminal_status,
            clarification_required=outcome.clarification_required,
            ledger=manager_runtime.ledger,
            observations=outcome.observations,
        )
