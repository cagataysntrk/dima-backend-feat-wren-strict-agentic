"""Day 0 V2 bootstrap orchestrator.

This module is deliberately boring: bind the already-authorized principal to the
tenant-specific Wren service, read semantic-engine metadata, return a typed snapshot,
and stop. It must not interpret user language or execute a query.
"""

from __future__ import annotations

from control_plane.authorize import Principal

from app.company_registry import wren_for_request
from app.v2.models import AskV2BootstrapRequest, AskV2BootstrapResponse, TenantAnalyticsRuntimeV0


class V2BootstrapOrchestrator:
    def bootstrap(
        self,
        request,
        body: AskV2BootstrapRequest,
        principal: Principal,
    ) -> AskV2BootstrapResponse:
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

        return AskV2BootstrapResponse(
            runtime=runtime,
            session_id=body.session_id,
            thread_id=body.thread_id,
        )
