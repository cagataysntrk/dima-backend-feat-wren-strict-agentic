"""Metabase P3 transport models.

REST serialized query identity and pagination continuation are deliberately distinct.
There is no MCP query-handle abstraction in this package.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MetabaseRuntimePolicy(FrozenModel):
    runtime_version: str = Field(min_length=1)
    runtime_image_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    api_surface: Literal["REST_AGENT_API"] = "REST_AGENT_API"
    required_api_version: Literal["v2"] = "v2"
    raw_sql_policy: Literal["disabled", "unused"]
    observed_page_size: int = Field(ge=1)
    observed_total_row_cap: int | None = Field(default=None, ge=1)


class ConstructedQuery(FrozenModel):
    serialized_query: str = Field(min_length=1)


class ContinuationToken(FrozenModel):
    token: str = Field(min_length=1)


class ExecutionStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class MetabaseExecutionResponse(FrozenModel):
    status: ExecutionStatus
    data: dict[str, Any] = Field(default_factory=dict)
    row_count: int = Field(default=0, ge=0)
    running_time: int | None = Field(default=None, ge=0)
    error: str | None = None

    @model_validator(mode="after")
    def _status_shape(self):
        if self.status == ExecutionStatus.FAILED and not self.error:
            raise ValueError("failed Metabase execution must carry an error")
        return self


class MetabaseQueryPage(MetabaseExecutionResponse):
    continuation: ContinuationToken | None = None


class SearchResponse(FrozenModel):
    data: tuple[dict[str, Any], ...] = ()
    total_count: int = Field(default=0, ge=0)


class MetabaseResourceContent(BaseModel):
    """Resource-specific payload from Agent API read-resource.

    The outer contract is stable, while inner resource shapes vary by URI. Preserve those
    fields without guessing business meaning; expose the documented structured-output envelope.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        populate_by_name=True,
    )

    structured_output: dict[str, Any] | None = Field(
        default=None,
        alias="structured-output",
    )
    formatted: str | None = None


class MetabaseResourceItem(FrozenModel):
    uri: str = Field(min_length=1)
    content: MetabaseResourceContent | None = None
    error: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _content_xor_error(self):
        if (self.content is None) == (self.error is None):
            raise ValueError("Metabase resource must contain exactly one of content or error")
        return self

    @property
    def failed(self) -> bool:
        return self.error is not None


class ReadResourceResponse(FrozenModel):
    resources: tuple[MetabaseResourceItem, ...] = Field(min_length=1)
    output: str = Field(min_length=1)


class MetabaseCapabilityHandshake(FrozenModel):
    ready: bool
    process_healthy: bool
    agent_api_enabled: bool
    construct_query: bool
    execute_query: bool
    combined_query: bool
    read_resource: bool
    api_surface: Literal["REST_AGENT_API"] = "REST_AGENT_API"
    required_api_version: Literal["v2"] = "v2"
    authenticated_surface: Literal["USER_SESSION"] = "USER_SESSION"
    raw_sql_policy: Literal["disabled", "unused"]
    observed_page_size: int = Field(ge=1)
    observed_total_row_cap: int | None = Field(default=None, ge=1)
    runtime_version: str
    runtime_image_digest: str
    verified_operations: tuple[str, ...] = ()
