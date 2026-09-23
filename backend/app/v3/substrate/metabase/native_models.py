"""Typed contracts for the native Metabot engine bridge.

These contracts carry transport/correlation identity only. They are not semantic authority,
execution authorization, QueryReceipt, or Evidence contracts.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NativeEngineIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)

    repository: str = "UpcyTech/dima-metabase-engine"
    engine_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    upstream_base_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    runtime_tag: str = Field(min_length=1)
    runtime_image_digest: str | None = None


class NativeEngineRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    profile_id: str = "nlq"
    metabot_id: str | None = None
    message: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    conversation_id: UUID
    history: list[dict[str, Any]] | None = None
    state: dict[str, Any] = Field(default_factory=dict)
    dima_request_id: str = Field(min_length=1)
    dima_trace_id: str = Field(min_length=1)


class NativeStreamEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int
    prefix: str
    raw_line: str
    value: Any


class NativeEngineObservation(BaseModel):
    model_config = ConfigDict(frozen=True)

    engine_identity: NativeEngineIdentity
    status_code: int
    latency_ms: int
    runtime_version: dict[str, Any]
    events: tuple[NativeStreamEvent, ...]
    text_parts: tuple[str, ...] = ()
    data_parts: tuple[Any, ...] = ()
    tool_calls: tuple[Any, ...] = ()
    tool_results: tuple[Any, ...] = ()
    errors: tuple[Any, ...] = ()
    finish_parts: tuple[Any, ...] = ()
    final_state: dict[str, Any] | None = None
