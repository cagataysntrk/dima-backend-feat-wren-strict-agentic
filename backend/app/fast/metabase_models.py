"""Typed contracts for the Fast Track Metabase Gateway."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


FAST_METABASE_RUNTIME_VERSION = "v0.63.18"
FAST_METABASE_RUNTIME_DIGEST = (
    "sha256:1160b570cb11c107bce00e71293552df"
    "8a8363e01a32c2c7a048cee002dc8a73"
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FastMetabaseRuntimePolicy(FrozenModel):
    runtime_version: str = FAST_METABASE_RUNTIME_VERSION
    runtime_image_digest: str = FAST_METABASE_RUNTIME_DIGEST
    api_surface: Literal["REST_AGENT_API"] = "REST_AGENT_API"
    required_api_version: Literal["v2"] = "v2"
    raw_sql_policy: Literal["disabled"] = "disabled"
    max_page_rows: int = Field(default=200, ge=1, le=200)
    max_total_rows_per_run: int = Field(default=1000, ge=1)


class ConstructedQuery(FrozenModel):
    serialized_query: str = Field(min_length=1)


class ContinuationToken(FrozenModel):
    token: str = Field(min_length=1)


class ExecutionStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionResponse(FrozenModel):
    status: ExecutionStatus
    data: dict[str, Any] = Field(default_factory=dict)
    row_count: int = Field(default=0, ge=0)
    running_time: int | None = Field(default=None, ge=0)
    error: str | None = None

    @model_validator(mode="after")
    def _status_shape(self):
        if self.status == ExecutionStatus.FAILED and not self.error:
            raise ValueError("failed execution must carry an error")
        return self


class QueryPage(ExecutionResponse):
    continuation: ContinuationToken | None = None


class SearchResponse(FrozenModel):
    data: tuple[dict[str, Any], ...] = ()
    total_count: int = Field(default=0, ge=0)


class ResourceContent(BaseModel):
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


class ResourceItem(FrozenModel):
    uri: str = Field(min_length=1)
    content: ResourceContent | None = None
    error: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _content_xor_error(self):
        if (self.content is None) == (self.error is None):
            raise ValueError("resource must contain exactly one of content or error")
        return self

    @property
    def failed(self) -> bool:
        return self.error is not None


class ReadResourceResponse(FrozenModel):
    resources: tuple[ResourceItem, ...] = Field(min_length=1)
    output: str = Field(min_length=1)


class CapabilityHandshake(FrozenModel):
    ready: bool
    process_healthy: bool
    agent_api_enabled: bool
    read_resource: bool
    construct_query: bool
    execute_query: bool
    combined_query: bool
    raw_sql_policy: Literal["disabled"] = "disabled"
    observed_page_limit: int = Field(ge=1, le=200)
    runtime_version: str
    runtime_image_digest: str
    verified_operations: tuple[str, ...] = ()
