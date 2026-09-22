"""Typed contracts for the P3A Metabase semantic-duplication preflight.

These are prototype-only Dima contracts. They do not route product traffic.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.semantic_spec import DimaSemanticSpec


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class P3AResult(StrEnum):
    PASS_B_SEAM = "PASS_B_SEAM"
    BLOCKED_DIMA_CONTRACT_GAP = "BLOCKED_DIMA_CONTRACT_GAP"
    REJECT_METABASE_STRUCTURED_EXECUTION = "REJECT_METABASE_STRUCTURED_EXECUTION"


class BridgeFamily(StrEnum):
    METRIC = "metric"
    METRIC_DIMENSION = "metric+dimension"
    METRIC_FILTER = "metric+filter"
    METRIC_PERIOD = "metric+period"
    PREVIOUS_PERIOD_COMPARISON = "previous-period-comparison"
    RANKING_LIMIT = "ranking/limit"
    TWO_DIMENSIONS = "two-compatible-dimensions"
    FILTER_PERIOD_DIMENSION = "filter+period+dimension"


class CandidateSemanticBinding(FrozenModel):
    """Context-bound candidate key -> stable Dima semantic id.

    candidate_id is an execution lookup key only. It is never a Metabase locator or
    durable receipt identity.
    """

    candidate_id: str = Field(min_length=1)
    semantic_id: str = Field(min_length=1)
    kind: Literal["metric", "dimension", "filter"]


class TemporalSemanticBinding(FrozenModel):
    """Exact governed compatibility token -> stable Dima time dimension id."""

    compatibility_key: str = Field(min_length=1)
    dimension_id: str = Field(min_length=1)


class P3ABridgeBlocked(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class DimaExecutionBindingSnapshot(FrozenModel):
    """Immutable Dima-owned execution snapshot for one semantic context.

    The snapshot bridges current context-bound candidate keys to stable semantic ids
    and explicit Dima SourceLineage. It performs no Metabase retrieval.
    """

    semantic_context_version: str = Field(min_length=1)
    semantic_spec: DimaSemanticSpec
    candidate_bindings: tuple[CandidateSemanticBinding, ...] = ()
    temporal_bindings: tuple[TemporalSemanticBinding, ...] = ()

    @model_validator(mode="after")
    def _integrity(self):
        if self.semantic_spec.semantic_context_version != self.semantic_context_version:
            raise ValueError("semantic spec/snapshot context mismatch")

        candidates = [item.candidate_id for item in self.candidate_bindings]
        if len(candidates) != len(set(candidates)):
            raise ValueError("duplicate candidate binding")

        temporal = [item.compatibility_key for item in self.temporal_bindings]
        if len(temporal) != len(set(temporal)):
            raise ValueError("duplicate temporal compatibility binding")

        metric_ids = {item.metric_id for item in self.semantic_spec.metrics}
        dimension_ids = {item.dimension_id for item in self.semantic_spec.dimensions}
        for item in self.candidate_bindings:
            if item.kind == "metric" and item.semantic_id not in metric_ids:
                raise ValueError("candidate metric binding references unknown Dima metric")
            if item.kind in {"dimension", "filter"} and item.semantic_id not in dimension_ids:
                raise ValueError("candidate dimension/filter binding references unknown Dima dimension")
        for item in self.temporal_bindings:
            if item.dimension_id not in dimension_ids:
                raise ValueError("temporal binding references unknown Dima dimension")
        return self

    def candidate(self, candidate_id: str, *, kind: str) -> str:
        for item in self.candidate_bindings:
            if item.candidate_id == candidate_id and item.kind == kind:
                return item.semantic_id
        raise P3ABridgeBlocked(
            "MISSING_STABLE_CANDIDATE_BINDING",
            f"no Dima-owned {kind} binding for candidate {candidate_id}",
        )

    def temporal_dimension(self, compatibility_key: str) -> str:
        for item in self.temporal_bindings:
            if item.compatibility_key == compatibility_key:
                return item.dimension_id
        raise P3ABridgeBlocked(
            "MISSING_STABLE_TIME_BINDING",
            "period/comparison time dimension has no explicit Dima-owned compatibility binding",
        )


class BridgeSafetyCounters(FrozenModel):
    raw_user_language_reinterpretation: int = Field(default=0, ge=0)
    manual_metric_redefinition: int = Field(default=0, ge=0)
    manual_relationship_redefinition: int = Field(default=0, ge=0)
    metabase_label_name_guessing: int = Field(default=0, ge=0)
    unapproved_implicit_fk_join: int = Field(default=0, ge=0)
    second_semantic_authority: int = Field(default=0, ge=0)

    @property
    def clean(self) -> bool:
        return all(value == 0 for value in self.model_dump().values())


class PortableQueryStep(FrozenModel):
    role: Literal["primary", "base", "reference"]
    query: dict[str, Any]


class BridgePlan(FrozenModel):
    family: BridgeFamily
    semantic_ids: tuple[str, ...]
    query_steps: tuple[PortableQueryStep, ...] = Field(min_length=1)
    counters: BridgeSafetyCounters = Field(default_factory=BridgeSafetyCounters)


class BridgeFamilyFinding(FrozenModel):
    family: BridgeFamily
    compiled: bool
    blocker_code: str | None = None
    detail: str | None = None
    query_count: int = Field(default=0, ge=0)


class BridgePreflightReport(FrozenModel):
    result: P3AResult
    findings: tuple[BridgeFamilyFinding, ...]
    counters: BridgeSafetyCounters
