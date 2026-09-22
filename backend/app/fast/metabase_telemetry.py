"""Secret-free telemetry contract for Fast Track Metabase transport."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class FastMetabaseTelemetryEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    operation: str = Field(min_length=1)
    ok: bool
    status_code: int | None = None
    duration_ms: int = Field(ge=0)
    error_code: str | None = None


class FastMetabaseTelemetrySink(Protocol):
    def emit(self, event: FastMetabaseTelemetryEvent) -> None:
        ...


class NullFastMetabaseTelemetry:
    def emit(self, event: FastMetabaseTelemetryEvent) -> None:
        del event
