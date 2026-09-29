"""Canonical semantic-binding input contracts for Standard analytics.

These are trusted resolved binding shapes. They are not language interpretation models.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.v3.research_contracts import SemanticTargetKind


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PeriodKind(StrEnum):
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    THIS_QUARTER = "this_quarter"
    THIS_YEAR = "this_year"
    LAST_N_DAYS = "last_n_days"
    LAST_N_WEEKS = "last_n_weeks"
    LAST_N_MONTHS = "last_n_months"
    PREVIOUS_WEEK = "previous_week"
    PREVIOUS_MONTH = "previous_month"
    PREVIOUS_QUARTER = "previous_quarter"
    PREVIOUS_YEAR = "previous_year"


class BoundSemanticRef(FrozenModel):
    candidate_id: str
    target_kind: SemanticTargetKind
    canonical_name: str
    cube_names: tuple[str, ...] = ()


class BoundFilterRef(FrozenModel):
    candidate_id: str
    dimension_name: str
    value: str
    cube_names: tuple[str, ...] = ()
    sensitive: bool = False


class BoundPeriod(FrozenModel):
    kind: PeriodKind
    source_text: str
    time_dimension: str
    start: str
    end: str | None = None
    n: int | None = None


class BoundComparison(FrozenModel):
    mode: Literal["previous_period"]
    source_text: str
    base_period: BoundPeriod
    reference_period: BoundPeriod
