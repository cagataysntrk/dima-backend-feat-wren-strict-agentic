"""V2 conversation orchestrator.

Day 2 composes runtime binding → bounded context → TurnInterpreter → SemanticResolver.
There is still no AnalyticsIR planning, SQL generation, dry-plan or data execution.
"""

from __future__ import annotations

from control_plane.authorize import Principal
from control_plane.security import derive_hmac_key

from app.company_registry import wren_for_request
from app.v2.context_provider import ContextProviderV0
from app.v2.interpreter import TurnInterpreter
from app.v2.models import (
    AskV2BootstrapRequest,
    AskV2BootstrapResponse,
    AskV2Day2Response,
    AskV2Request,
    TenantAnalyticsRuntimeV0,
    TurnAct,
)
from app.v2.resolver import SemanticResolver


class V2Orchestrator:
    def __init__(self) -> None:
        self._context_provider = ContextProviderV0()
        self._interpreter = TurnInterpreter()
        self._resolver = SemanticResolver(
            signing_key=derive_hmac_key("v2-clarification-chip-v1")
        )

    @staticmethod
    def _bind_runtime(request, principal: Principal):
        service = wren_for_request(request)
        schema = service.schema()
        runtime = TenantAnalyticsRuntimeV0(
            tenant_id=str(principal.tenant_id) if principal.tenant_id else None,
            tenant_slug=principal.tenant_slug,
            principal_user_id=str(principal.user_id),
            roles=tuple(sorted(str(role) for role in (principal.roles or []))),
            mdl_version=str(service.mdl_version),
            catalog=schema.get("catalog"),
            schema_name=schema.get("schema_name"),
            db_online=bool(schema.get("db_online", True)),
        )
        return service, schema, runtime

    @staticmethod
    def _tenant_binding(runtime: TenantAnalyticsRuntimeV0) -> str:
        if runtime.tenant_id:
            return f"id:{runtime.tenant_id}"
        return f"slug:{runtime.tenant_slug or ''}"

    def bootstrap(
        self,
        request,
        body: AskV2BootstrapRequest,
        principal: Principal,
    ) -> AskV2BootstrapResponse:
        """Historical Day 0 boundary probe; not the Day 2 HTTP product path."""
        _, _, runtime = self._bind_runtime(request, principal)
        return AskV2BootstrapResponse(
            runtime=runtime,
            session_id=body.session_id,
            thread_id=body.thread_id,
        )

    def handle(
        self,
        request,
        body: AskV2Request,
        principal: Principal,
    ) -> AskV2Day2Response:
        service, schema, runtime = self._bind_runtime(request, principal)
        semantic_context = self._context_provider.build(service, runtime)
        tenant_binding = self._tenant_binding(runtime)

        if body.clarification_token:
            bundle = self._resolver.resume_signed(
                token=body.clarification_token,
                schema=schema,
                semantic_context=semantic_context,
                conversation=body.conversation,
                tenant_binding=tenant_binding,
                session_id=body.session_id,
                thread_id=body.thread_id,
            )
            turn = None
            resumed_by = "signed_chip"
        else:
            turn = self._interpreter.interpret(
                question=body.question,
                semantic_context=semantic_context,
                conversation=body.conversation,
                llm=request.app.state.llm,
            )
            pending = body.conversation.clarification_state
            if (
                turn.dialogue_act == TurnAct.CLARIFICATION_ANSWER
                and pending is not None
                and pending.pending
            ):
                bundle = self._resolver.resume_free_text(
                    turn=turn,
                    pending=pending,
                    schema=schema,
                    semantic_context=semantic_context,
                    conversation=body.conversation,
                    tenant_binding=tenant_binding,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                )
                resumed_by = "free_text"
            else:
                bundle = self._resolver.resolve_turn(
                    turn=turn,
                    schema=schema,
                    semantic_context=semantic_context,
                    conversation=body.conversation,
                    tenant_binding=tenant_binding,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                )
                resumed_by = None

        if not bundle.hypotheses and bundle.clarification is None:
            semantic_status = "not_applicable"
            next_stage = "conversation_policy_future"
        else:
            semantic_status = bundle.semantic_status
            next_stage = (
                "analytics_ir_day3"
                if semantic_status == "resolved"
                else "clarification_resume_day2"
            )

        return AskV2Day2Response(
            semantic_status=semantic_status,
            runtime=runtime,
            context_version=semantic_context.context_version,
            turn=turn,
            hypotheses=bundle.hypotheses,
            clarification=bundle.clarification,
            resumed_by=resumed_by,
            session_id=body.session_id,
            thread_id=body.thread_id,
            next_stage=next_stage,
        )

    # Compatibility name for Day 1 callers/tests; semantics now continue through Day 2.
    interpret = handle


# Compatibility name for Day 0 imports. New code should use V2Orchestrator.
V2BootstrapOrchestrator = V2Orchestrator
