"""Typed contracts for the P3A Metabase semantic-duplication preflight.

P3A result/report models remain prototype-specific. Execution-binding primitives are
production-owned by execution_binding.py and are re-exported here for compatibility.
There is exactly one binding contract and one blocked-execution exception semantics.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    MetabaseCompilationBlocked,
    TemporalSemanticBinding,
)

# Backwards-compatible P3A name; exact type identity is intentional.
P3ABridgeBlocked = MetabaseCompilationBlocked


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


__all__ = [
    "BridgeFamily",
    "BridgeFamilyFinding",
    "BridgePlan",
    "BridgePreflightReport",
    "BridgeSafetyCounters",
    "CandidateSemanticBinding",
    "CurrentCatalogObject",
    "CurrentCatalogSnapshot",
    "DimaExecutionBindingSnapshot",
    "MetabaseCompilationBlocked",
    "P3ABridgeBlocked",
    "P3AResult",
    "PortableQueryStep",
    "TemporalSemanticBinding",
]
