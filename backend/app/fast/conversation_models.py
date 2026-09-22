"""Typed contracts for FT-005 conversation, turn lineage and accepted context."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.fast.ask_models import AggregationKind, AskDraft
from app.fast.run_models import FastRunState


class FrozenConversationModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FastContextSlot(StrEnum):
    ENTITY = "ENTITY"
    AGGREGATION = "AGGREGATION"
    MEASURE = "MEASURE"
    TEMPORAL = "TEMPORAL"
    BREAKDOWN = "BREAKDOWN"


class FastFollowupStatus(StrEnum):
    SELF_CONTAINED = "SELF_CONTAINED"
    CONTEXTUAL = "CONTEXTUAL"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"


class FastAcceptedContext(FrozenConversationModel):
    source_turn_ids: tuple[str, ...] = ()
    resource_ref: str | None = Field(
        default=None,
        pattern=r"^metabase://table/\d+$",
    )
    accepted_field_refs: dict[str, str] = Field(default_factory=dict)
    exact_time_bounds: dict[str, str] | None = None
    aggregation: AggregationKind | None = None
    evidence_ids: tuple[str, ...] = ()
    query_fingerprints: tuple[str, ...] = ()


class FastFollowupResolution(FrozenConversationModel):
    status: FastFollowupStatus
    inherited_slots: tuple[FastContextSlot, ...] = ()
    replaced_slots: tuple[FastContextSlot, ...] = ()
    effective_draft: AskDraft | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def _shape(self):
        if self.status in {
            FastFollowupStatus.SELF_CONTAINED,
            FastFollowupStatus.CONTEXTUAL,
        }:
            if self.effective_draft is None:
                raise ValueError("executable follow-up resolution requires effective_draft")
            if self.reason is not None:
                raise ValueError("executable follow-up resolution cannot carry reason")
        else:
            if self.effective_draft is not None:
                raise ValueError("non-executable follow-up resolution cannot carry effective_draft")
            if not (self.reason or "").strip():
                raise ValueError("non-executable follow-up resolution requires reason")
        if self.status == FastFollowupStatus.SELF_CONTAINED and self.inherited_slots:
            raise ValueError("SELF_CONTAINED cannot inherit prior context slots")
        return self


class FastConversationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=200)


class FastTurnCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=3, max_length=2000)
    as_of_date: date | None = None
    reply_to_turn_id: str | None = Field(
        default=None,
        pattern=r"^turn_[a-f0-9]{32}$",
    )
    clarifies_run_id: str | None = Field(
        default=None,
        pattern=r"^run_[a-f0-9]{32}$",
    )


class FastConversationSnapshot(FrozenConversationModel):
    conversation_id: str = Field(pattern=r"^conv_[a-f0-9]{32}$")
    title: str
    created_at: datetime
    updated_at: datetime
    latest_turn_id: str | None = None
    active_turn_id: str | None = None
    turn_count: int = Field(ge=0)


class FastTurnSnapshot(FrozenConversationModel):
    turn_id: str = Field(pattern=r"^turn_[a-f0-9]{32}$")
    conversation_id: str = Field(pattern=r"^conv_[a-f0-9]{32}$")
    seq: int = Field(ge=1)
    parent_turn_id: str | None = None
    reply_to_turn_id: str | None = None
    clarifies_run_id: str | None = None
    user_question: str
    run_id: str = Field(pattern=r"^run_[a-f0-9]{32}$")
    status: FastRunState
    context_source_turn_ids: tuple[str, ...] = ()
    accepted_context: FastAcceptedContext | None = None
    created_at: datetime
    updated_at: datetime


class FastConversationDetail(FrozenConversationModel):
    conversation: FastConversationSnapshot
    turns: tuple[FastTurnSnapshot, ...]
