"""Typed temporal language boundary for the Day 6.5 Manager path.

The model normalizes a bounded time/comparison surface into a closed temporal intent.
All date arithmetic remains deterministic. This module contains no regex or language
keyword parser.
"""

from __future__ import annotations

import calendar
import copy
import json
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Any, Callable, Literal

from pydantic import Field, model_validator

from app import mali_takvim
from app.v2.models import FrozenModel, PeriodKind, ResolvedComparison, ResolvedPeriod


class TemporalIntentKind(StrEnum):
    THIS_WEEK = "THIS_WEEK"
    THIS_MONTH = "THIS_MONTH"
    THIS_QUARTER = "THIS_QUARTER"
    THIS_YEAR = "THIS_YEAR"
    LAST_N_DAYS = "LAST_N_DAYS"
    LAST_N_WEEKS = "LAST_N_WEEKS"
    LAST_N_MONTHS = "LAST_N_MONTHS"
    PREVIOUS_WEEK = "PREVIOUS_WEEK"
    PREVIOUS_MONTH = "PREVIOUS_MONTH"
    PREVIOUS_QUARTER = "PREVIOUS_QUARTER"
    PREVIOUS_YEAR = "PREVIOUS_YEAR"


class ComparisonIntentKind(StrEnum):
    PREVIOUS_PERIOD = "PREVIOUS_PERIOD"
    PREVIOUS_YEAR_ALIGNED = "PREVIOUS_YEAR_ALIGNED"


class TemporalNormalizationChoice(FrozenModel):
    request_id: str
    target: Literal["PERIOD", "COMPARISON"]
    decision: Literal["NORMALIZED", "ABSTAIN"]
    period_kind: TemporalIntentKind | None = None
    comparison_kind: ComparisonIntentKind | None = None
    n: int | None = Field(default=None, ge=1, le=10000)
    reason: Literal[
        "AMBIGUOUS",
        "UNSUPPORTED",
        "INSUFFICIENT_CONTEXT",
    ] | None = None

    @model_validator(mode="after")
    def _shape(self):
        if self.decision == "ABSTAIN":
            if self.reason is None:
                raise ValueError("ABSTAIN requires reason")
            if self.period_kind is not None or self.comparison_kind is not None or self.n is not None:
                raise ValueError("ABSTAIN cannot carry normalized temporal fields")
            return self

        if self.reason is not None:
            raise ValueError("NORMALIZED cannot carry abstain reason")
        if self.target == "PERIOD":
            if self.period_kind is None or self.comparison_kind is not None:
                raise ValueError("PERIOD requires period_kind only")
            if self.period_kind in {
                TemporalIntentKind.LAST_N_DAYS,
                TemporalIntentKind.LAST_N_WEEKS,
                TemporalIntentKind.LAST_N_MONTHS,
            }:
                if self.n is None:
                    raise ValueError("LAST_N period requires n")
            elif self.n is not None:
                raise ValueError("non-LAST_N period cannot carry n")
        else:
            if self.comparison_kind is None or self.period_kind is not None or self.n is not None:
                raise ValueError("COMPARISON requires comparison_kind only")
        return self


class TemporalNormalizationBatch(FrozenModel):
    choices: tuple[TemporalNormalizationChoice, ...] = Field(min_length=1)


_TEMPORAL_SYSTEM = """You are Dima's bounded temporal intent normalizer.

For each supplied exact temporal surface, choose only one item from the closed temporal
ontology encoded by the output schema, or ABSTAIN. Normalize meaning only; never calculate
dates, never choose database/time dimensions, never emit SQL, and never invent additional
time constraints.

PERIOD describes the requested analytical period. COMPARISON describes how the reference
period relates to an already-governed base period. Return only strict schema.
"""


def _strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                props = node.get("properties") or {}
                node["required"] = list(props.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


class TypedTemporalNormalizer:
    def __init__(self, *, structured: Callable[..., Any] | None) -> None:
        self._structured = structured

    def normalize(
        self,
        requests: tuple[tuple[str, str, Literal["PERIOD", "COMPARISON"]], ...],
    ) -> tuple[TemporalNormalizationChoice, ...]:
        if not requests:
            return ()
        if self._structured is None:
            return tuple(
                TemporalNormalizationChoice(
                    request_id=request_id,
                    target=target,
                    decision="ABSTAIN",
                    reason="INSUFFICIENT_CONTEXT",
                )
                for request_id, _, target in requests
            )

        raw = self._structured(
            _TEMPORAL_SYSTEM,
            json.dumps(
                {
                    "requests": [
                        {
                            "request_id": request_id,
                            "surface": surface,
                            "target": target,
                        }
                        for request_id, surface, target in requests
                    ]
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            schema=_strict_schema(TemporalNormalizationBatch.model_json_schema()),
            schema_name="dima_typed_temporal_intent_v1",
        )
        data = json.loads(raw) if isinstance(raw, str) else raw
        decision = TemporalNormalizationBatch.model_validate(data)
        by_id = {choice.request_id: choice for choice in decision.choices}
        expected = {request_id for request_id, _, _ in requests}
        if set(by_id) != expected:
            raise ValueError("temporal normalizer response IDs do not match request batch")
        return tuple(by_id[request_id] for request_id, _, _ in requests)


@dataclass(frozen=True)
class TemporalBindingEngine:
    """Pure calendar arithmetic over typed temporal intent."""

    @staticmethod
    def _quarter_start(day: date) -> date:
        month = ((day.month - 1) // 3) * 3 + 1
        return date(day.year, month, 1)

    @staticmethod
    def _shift_month(day: date, months: int) -> date:
        month0 = day.month - 1 + months
        year = day.year + month0 // 12
        month = month0 % 12 + 1
        return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))

    @staticmethod
    def _shift_year(day: date, years: int) -> date:
        year = day.year + years
        return date(year, day.month, min(day.day, calendar.monthrange(year, day.month)[1]))

    @classmethod
    def period(
        cls,
        *,
        choice: TemporalNormalizationChoice,
        source_text: str,
        time_dimension: str,
        today: date | None = None,
    ) -> ResolvedPeriod:
        if choice.decision != "NORMALIZED" or choice.target != "PERIOD" or choice.period_kind is None:
            raise ValueError("typed period choice is not normalized")
        now = today or date.today()
        kind = choice.period_kind

        if kind == TemporalIntentKind.THIS_WEEK:
            start = now - timedelta(days=now.weekday())
            period_kind = PeriodKind.THIS_WEEK
            end = now
        elif kind == TemporalIntentKind.THIS_MONTH:
            start = now.replace(day=1)
            period_kind = PeriodKind.THIS_MONTH
            end = now
        elif kind == TemporalIntentKind.THIS_QUARTER:
            start = cls._quarter_start(now)
            period_kind = PeriodKind.THIS_QUARTER
            end = now
        elif kind == TemporalIntentKind.THIS_YEAR:
            start = mali_takvim.yil_basi(now)
            period_kind = PeriodKind.THIS_YEAR
            end = now
        elif kind == TemporalIntentKind.LAST_N_DAYS:
            assert choice.n is not None
            start = now - timedelta(days=choice.n - 1)
            period_kind = PeriodKind.LAST_N_DAYS
            end = now
        elif kind == TemporalIntentKind.LAST_N_WEEKS:
            assert choice.n is not None
            start = now - timedelta(days=(choice.n * 7) - 1)
            period_kind = PeriodKind.LAST_N_WEEKS
            end = now
        elif kind == TemporalIntentKind.LAST_N_MONTHS:
            assert choice.n is not None
            start = cls._shift_month(now, -choice.n)
            period_kind = PeriodKind.LAST_N_MONTHS
            end = now
        elif kind == TemporalIntentKind.PREVIOUS_WEEK:
            this_week = now - timedelta(days=now.weekday())
            end = this_week - timedelta(days=1)
            start = end - timedelta(days=6)
            period_kind = PeriodKind.PREVIOUS_WEEK
        elif kind == TemporalIntentKind.PREVIOUS_MONTH:
            end = now.replace(day=1) - timedelta(days=1)
            start = end.replace(day=1)
            period_kind = PeriodKind.PREVIOUS_MONTH
        elif kind == TemporalIntentKind.PREVIOUS_QUARTER:
            current_q = cls._quarter_start(now)
            end = current_q - timedelta(days=1)
            start = cls._quarter_start(end)
            period_kind = PeriodKind.PREVIOUS_QUARTER
        elif kind == TemporalIntentKind.PREVIOUS_YEAR:
            year_start = mali_takvim.yil_basi(now)
            end = year_start - timedelta(days=1)
            start = mali_takvim.yil_basi(end)
            period_kind = PeriodKind.PREVIOUS_YEAR
        else:
            raise ValueError(f"unsupported typed period: {kind}")

        return ResolvedPeriod(
            kind=period_kind,
            source_text=source_text,
            time_dimension=time_dimension,
            start=start.isoformat(),
            end=end.isoformat(),
            n=choice.n,
        )

    @classmethod
    def comparison(
        cls,
        *,
        choice: TemporalNormalizationChoice,
        source_text: str,
        time_dimension: str,
        base_period: ResolvedPeriod,
        today: date | None = None,
    ) -> ResolvedComparison:
        del today
        if (
            choice.decision != "NORMALIZED"
            or choice.target != "COMPARISON"
            or choice.comparison_kind is None
        ):
            raise ValueError("typed comparison choice is not normalized")

        base_start = date.fromisoformat(base_period.start)
        base_end = date.fromisoformat(base_period.end or base_period.start)
        duration = base_end - base_start

        if choice.comparison_kind == ComparisonIntentKind.PREVIOUS_PERIOD:
            reference_end = base_start - timedelta(days=1)
            reference_start = reference_end - duration
        elif choice.comparison_kind == ComparisonIntentKind.PREVIOUS_YEAR_ALIGNED:
            reference_start = cls._shift_year(base_start, -1)
            reference_end = cls._shift_year(base_end, -1)
        else:
            raise ValueError(f"unsupported comparison intent: {choice.comparison_kind}")

        reference = ResolvedPeriod(
            kind=(
                PeriodKind.PREVIOUS_YEAR
                if choice.comparison_kind == ComparisonIntentKind.PREVIOUS_YEAR_ALIGNED
                else base_period.kind
            ),
            source_text=source_text,
            time_dimension=time_dimension,
            start=reference_start.isoformat(),
            end=reference_end.isoformat(),
            n=base_period.n,
        )
        return ResolvedComparison(
            mode="previous_period",
            source_text=source_text,
            base_period=base_period,
            reference_period=reference,
        )
