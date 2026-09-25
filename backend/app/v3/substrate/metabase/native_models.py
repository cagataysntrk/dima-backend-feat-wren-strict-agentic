"""Typed contracts for the native Metabot engine bridge.

These contracts carry transport/correlation identity only. They are not semantic authority,
execution authorization, QueryReceipt, or Evidence contracts.
"""
from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NativeEngineIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)

    repository: str = "UpcyTech/dima-metabase-engine"
    engine_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    upstream_base_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    runtime_tag: str = Field(min_length=1)
    runtime_image_digest: str | None = None
    build_identity: str | None = None
    runtime_image_identity: str | None = None
    runtime_instance_id: UUID | None = None


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


class NativeExactOccurrenceExecutionObservation(BaseModel):
    """Transport observation for one engine-owned exact query occurrence execution."""

    model_config = ConfigDict(frozen=True)

    status_code: int
    latency_ms: int = Field(ge=0)
    native_conversation_id: UUID
    native_query_id: str = Field(min_length=1)
    attestation_id: str = Field(min_length=1)
    executed_pmbql_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    runtime_identity: dict[str, Any]
    payload: dict[str, Any]
    attestation: dict[str, Any]


class NativeProducedQuery(BaseModel):
    """Exact executable query representation emitted by the native Metabot stream."""

    model_config = ConfigDict(frozen=True)

    native_query_id: str = Field(min_length=1)
    query: dict[str, Any]
    query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    source: Literal["generated_entity", "state"]


class NativeDatasetExecutionObservation(BaseModel):
    """Transport-only observation for direct native Metabase dataset execution."""

    model_config = ConfigDict(frozen=True)

    status_code: int
    latency_ms: int = Field(ge=0)
    query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    payload: dict[str, Any]



class NativeExplorationObservation(BaseModel):
    """Transport-only observation for native Metabase exploration material."""

    model_config = ConfigDict(frozen=True)

    status_code: int
    latency_ms: int = Field(ge=0)
    exploration_kind: Literal["automagic_adhoc"] = "automagic_adhoc"
    query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    payload: dict[str, Any]
