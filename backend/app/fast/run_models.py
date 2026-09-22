"""Typed lifecycle contracts for Fast Track runs."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.fast.ask_models import FastAskRequest, FastAskResponse


class FrozenRunModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FastRunState(StrEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    WAITING_CLARIFICATION = "WAITING_CLARIFICATION"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"


TERMINAL_RUN_STATES = frozenset(
    {
        FastRunState.COMPLETED,
        FastRunState.FAILED,
        FastRunState.CANCELLED,
        FastRunState.INTERRUPTED,
    }
)

QUIESCENT_RUN_STATES = frozenset(
    {
        *TERMINAL_RUN_STATES,
        FastRunState.WAITING_CLARIFICATION,
    }
)


class FastRunEventType(StrEnum):
    RUN_CREATED = "RUN_CREATED"
    RUN_STARTED = "RUN_STARTED"
    RUN_PARTIAL = "RUN_PARTIAL"
    RUN_WAITING_CLARIFICATION = "RUN_WAITING_CLARIFICATION"
    RUN_COMPLETED = "RUN_COMPLETED"
    RUN_FAILED = "RUN_FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    RUN_CANCELLED = "RUN_CANCELLED"
    RUN_INTERRUPTED = "RUN_INTERRUPTED"


class FastRunCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=3, max_length=2000)
    as_of_date: date | None = None
    retry_of_run_id: str | None = Field(
        default=None,
        pattern=r"^run_[a-f0-9]{32}$",
    )

    def ask_request(self) -> FastAskRequest:
        return FastAskRequest(
            question=self.question,
            as_of_date=self.as_of_date,
        )


class FastRunErrorPayload(FrozenRunModel):
    code: str
    message: str


class FastRunEvent(FrozenRunModel):
    event_id: int = Field(ge=1)
    run_id: str = Field(pattern=r"^run_[a-f0-9]{32}$")
    type: FastRunEventType
    state: FastRunState
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
    dedupe_key: str = Field(min_length=1, max_length=200)


class FastRunSnapshot(FrozenRunModel):
    run_id: str = Field(pattern=r"^run_[a-f0-9]{32}$")
    state: FastRunState
    question: str
    as_of_date: date | None
    created_at: datetime
    updated_at: datetime
    response: FastAskResponse | None = None
    error: FastRunErrorPayload | None = None
    last_event_id: int = Field(ge=1)
    terminal_event_id: int | None = Field(default=None, ge=1)
    retry_of_run_id: str | None = None
    root_run_id: str = Field(pattern=r"^run_[a-f0-9]{32}$")
    attempt: int = Field(ge=1)
