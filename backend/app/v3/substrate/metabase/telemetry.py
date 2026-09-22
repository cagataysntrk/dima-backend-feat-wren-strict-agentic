"""Minimal safe telemetry for the Metabase P3 client."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class MetabaseTelemetryEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    operation: str = Field(min_length=1)
    ok: bool
    status_code: int | None = None
    duration_ms: int = Field(ge=0)
    error_code: str | None = None


class MetabaseTelemetrySink(Protocol):
    def emit(self, event: MetabaseTelemetryEvent) -> None:
        ...


class NullMetabaseTelemetry:
    def emit(self, event: MetabaseTelemetryEvent) -> None:
        del event
