"""Day 0 typed contracts for the isolated Dima V2 bootstrap.

No conversation interpretation, semantic resolution, planning, SQL or narration lives
here yet. The only goal is to freeze an explicit request-scoped runtime snapshot.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AskV2BootstrapRequest(BaseModel):
    """Future-compatible request envelope; Day 0 intentionally does not interpret it."""

    question: str = Field(min_length=1)
    session_id: str | None = None
    thread_id: str | None = None


class TenantAnalyticsRuntimeV0(BaseModel):
    """Immutable identity + semantic-engine snapshot for one V2 request."""

    model_config = ConfigDict(frozen=True)

    tenant_id: str | None = None
    tenant_slug: str | None = None
    principal_user_id: str
    roles: tuple[str, ...] = ()
    mdl_version: str
    catalog: str | None = None
    schema_name: str | None = None
    db_online: bool


class AskV2BootstrapResponse(BaseModel):
    status: Literal["bootstrap_ready"] = "bootstrap_ready"
    stage: Literal["day0_runtime_boundary"] = "day0_runtime_boundary"
    runtime: TenantAnalyticsRuntimeV0
    session_id: str | None = None
    thread_id: str | None = None
    query_executed: Literal[False] = False
    llm_called: Literal[False] = False
    legacy_semantic_path_called: Literal[False] = False
    next_stage: Literal["turn_interpreter_day1"] = "turn_interpreter_day1"
