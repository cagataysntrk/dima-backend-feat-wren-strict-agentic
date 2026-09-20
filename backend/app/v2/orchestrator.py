"""V2 conversation orchestrator.

Day 1 composes only runtime binding → bounded context → TurnInterpreter. There is no
resolver, planner, SQL, execution or legacy fallback in this module.
"""

from __future__ import annotations

from control_plane.authorize import Principal

from app.company_registry import wren_for_request
from app.v2.context_provider import ContextProviderV0
from app.v2.interpreter import TurnInterpreter
from app.v2.models import (
    AskV2BootstrapRequest,
    AskV2BootstrapResponse,
    AskV2Day1Response,
    AskV2Request,
    TenantAnalyticsRuntimeV0,
)


class V2Orchestrator:
    def __init__(self) -> None:
        self._context_provider = ContextProviderV0()
        self._interpreter = TurnInterpreter()

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
        return service, runtime

    def bootstrap(
        self,
        request,
        body: AskV2BootstrapRequest,
        principal: Principal,
    ) -> AskV2BootstrapResponse:
        """Historical Day 0 boundary probe; not the Day 1 HTTP product path."""
        _, runtime = self._bind_runtime(request, principal)
        return AskV2BootstrapResponse(
            runtime=runtime,
            session_id=body.session_id,
            thread_id=body.thread_id,
        )

    def interpret(
        self,
        request,
        body: AskV2Request,
        principal: Principal,
    ) -> AskV2Day1Response:
        service, runtime = self._bind_runtime(request, principal)
        semantic_context = self._context_provider.build(service, runtime)
        turn = self._interpreter.interpret(
            question=body.question,
            semantic_context=semantic_context,
            conversation=body.conversation,
            llm=request.app.state.llm,
        )
        return AskV2Day1Response(
            runtime=runtime,
            context_version=semantic_context.context_version,
            turn=turn,
            session_id=body.session_id,
            thread_id=body.thread_id,
        )


# Compatibility name for Day 0 imports. New code should use V2Orchestrator.
V2BootstrapOrchestrator = V2Orchestrator
