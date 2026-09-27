"""Shared request-scoped V2 runtime identity boundary."""

from __future__ import annotations

import hashlib
import json

from control_plane.authorize import Principal

from app.company_registry import wren_for_request
from app.v2.models import AskV2Request, TenantAnalyticsRuntimeV0


def bind_runtime(request, principal: Principal):
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


def tenant_binding(runtime: TenantAnalyticsRuntimeV0) -> str:
    if runtime.tenant_id:
        return f"id:{runtime.tenant_id}"
    return f"slug:{runtime.tenant_slug or ''}"


def request_ref(body: AskV2Request) -> str:
    payload = json.dumps(
        {
            "question": body.question,
            "session_id": body.session_id,
            "thread_id": body.thread_id,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return "r-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
