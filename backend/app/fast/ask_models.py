"""Typed contracts for the first Fast Track Ask vertical slice."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DraftStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class AggregationKind(StrEnum):
    COUNT = "COUNT"
    SUM = "SUM"


class TemporalKind(StrEnum):
    NONE = "NONE"
    LAST_N_DAYS = "LAST_N_DAYS"
    CURRENT_MONTH = "CURRENT_MONTH"
    PREVIOUS_MONTH = "PREVIOUS_MONTH"
    ABSOLUTE_DATE_RANGE = "ABSOLUTE_DATE_RANGE"


class SelectionPurpose(StrEnum):
    RESOURCE = "RESOURCE"
    MEASURE = "MEASURE"
    TEMPORAL = "TEMPORAL"
    BREAKDOWN = "BREAKDOWN"


class AskOutcomeStatus(StrEnum):
    SUCCESS = "SUCCESS"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"
    FAILED = "FAILED"


class DraftTemporalIntent(FrozenModel):
    kind: TemporalKind
    days: int | None
    start_date: str | None
    end_date: str | None

    @model_validator(mode="after")
    def _shape(self):
        if self.kind == TemporalKind.LAST_N_DAYS:
            if self.days is None or self.days < 1 or self.days > 3660:
                raise ValueError("LAST_N_DAYS requires days in 1..3660")
            if self.start_date is not None or self.end_date is not None:
                raise ValueError("LAST_N_DAYS cannot carry absolute dates")
        elif self.kind == TemporalKind.ABSOLUTE_DATE_RANGE:
            if not self.start_date or not self.end_date:
                raise ValueError("ABSOLUTE_DATE_RANGE requires start_date and end_date")
            if self.days is not None:
                raise ValueError("ABSOLUTE_DATE_RANGE cannot carry days")
        else:
            if self.days is not None or self.start_date is not None or self.end_date is not None:
                raise ValueError(f"{self.kind.value} cannot carry extra temporal values")
        return self


class AskDraft(FrozenModel):
    status: DraftStatus
    unsupported_reason: str | None
    search_terms: tuple[str, ...] = Field(min_length=1, max_length=4)
    aggregation: AggregationKind
    measure_hint: str | None
    breakdown_hint: str | None
    temporal: DraftTemporalIntent

    @model_validator(mode="after")
    def _draft_shape(self):
        if any(not term.strip() for term in self.search_terms):
            raise ValueError("search_terms must be non-empty")
        if self.status == DraftStatus.UNSUPPORTED:
            if not (self.unsupported_reason or "").strip():
                raise ValueError("UNSUPPORTED draft requires unsupported_reason")
            return self
        if self.unsupported_reason is not None:
            raise ValueError("SUPPORTED draft must not carry unsupported_reason")
        if self.aggregation == AggregationKind.SUM and not (self.measure_hint or "").strip():
            raise ValueError("SUM requires measure_hint")
        if self.aggregation == AggregationKind.COUNT and self.measure_hint is not None:
            raise ValueError("COUNT must not carry measure_hint")
        return self


class SelectionDecision(FrozenModel):
    selected_handle: str | None


class ResourceCandidate(FrozenModel):
    handle: str = Field(pattern=r"^fast_res_\d{3}$")
    name: str = Field(min_length=1)
    display_name: str | None
    description: str | None
    resource_type: str = "table"


class FieldCandidate(FrozenModel):
    handle: str = Field(pattern=r"^fast_field_\d{3}$")
    name: str = Field(min_length=1)
    display_name: str | None
    type_hint: str | None
    numeric: bool
    temporal: bool


class TableAuthority(FrozenModel):
    resource_handle: str = Field(pattern=r"^fast_res_\d{3}$")
    resource_uri: str = Field(pattern=r"^metabase://table/\d+$")
    table_name: str = Field(min_length=1)
    database_name: str = Field(min_length=1)
    schema_name: str | None
    portable_fk: tuple[str | None, ...] = Field(min_length=3)


class FieldAuthority(FrozenModel):
    field_handle: str = Field(pattern=r"^fast_field_\d{3}$")
    field_name: str = Field(min_length=1)
    display_name: str | None
    portable_fk: tuple[str | None, ...] = Field(min_length=4)
    type_hint: str | None
    numeric: bool
    temporal: bool


class TemporalWindow(FrozenModel):
    kind: TemporalKind
    start: date
    end_exclusive: date

    @model_validator(mode="after")
    def _ordered(self):
        if self.start >= self.end_exclusive:
            raise ValueError("temporal window must have start < end_exclusive")
        return self


class FastAskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=3, max_length=2000)
    as_of_date: date | None = None


class FastQueryResult(FrozenModel):
    columns: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]
    row_count: int = Field(ge=0)


class FastEvidence(FrozenModel):
    evidence_id: str = Field(pattern=r"^ev_[a-f0-9]{20}$")
    question: str
    resource_handle: str
    resource_ref: str
    field_refs: dict[str, str]
    exact_time_bounds: dict[str, str] | None
    portable_query: dict[str, Any]
    query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    access_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    metabase_runtime_version: str
    result: FastQueryResult
    result_digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class FastAskErrorPayload(FrozenModel):
    code: str
    message: str


class FastAskResponse(FrozenModel):
    status: AskOutcomeStatus
    question: str
    answer: str | None = None
    result: FastQueryResult | None = None
    evidence: FastEvidence | None = None
    error: FastAskErrorPayload | None = None

    @model_validator(mode="after")
    def _outcome_shape(self):
        if self.status == AskOutcomeStatus.SUCCESS:
            if self.answer is None or self.result is None or self.evidence is None or self.error is not None:
                raise ValueError("SUCCESS requires answer/result/evidence and no error")
        else:
            if self.error is None or self.answer is not None or self.result is not None or self.evidence is not None:
                raise ValueError("non-success requires error and no result payload")
        return self
