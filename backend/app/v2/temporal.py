"""Typed temporal resolution for Day 3 standard analytics.

This module never receives the full raw user question. It consumes only the time and
comparison surface spans already isolated by TurnInterpreter, then performs closed-family
calendar arithmetic. Fiscal-year ownership remains app.mali_takvim.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

from app import mali_takvim
from app.donem_capasi import SAYI_KALIBI, sayi_coz
from app.llm import _norm
from app.v2.models import (
    ComparisonSurface,
    PeriodKind,
    ResolvedComparison,
    ResolvedPeriod,
    SemanticMention,
)


class TemporalResolutionError(ValueError):
    pass


def _months_ago(day: date, n: int) -> date:
    month0 = day.month - 1 - n
    year = day.year + month0 // 12
    month = month0 % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def _previous_month_window(day: date) -> tuple[date, date]:
    end = day.replace(day=1) - timedelta(days=1)
    return end.replace(day=1), end


def _shift_month(day: date, n: int = 1) -> date:
    return _months_ago(day, n)


def _shift_year(day: date, n: int = 1) -> date:
    year = day.year - n
    return date(year, day.month, min(day.day, calendar.monthrange(year, day.month)[1]))


_LAST_N_RE = re.compile(
    rf"^\s*(?:son|last)\s+(?P<n>\d+|{SAYI_KALIBI})\s+"
    r"(?P<unit>ay|month|months|gun|day|days)[a-z]*\s*$"
)
_PREVIOUS_RE = re.compile(
    r"\b(?:gecen|onceki|previous|last)\s+(?P<unit>ay|month|yil|sene|year)[a-z]*\b"
)
_PREVIOUS_N_RE = re.compile(
    rf"\b(?:gecen|onceki|previous|prior)\s+(?P<n>\d+|{SAYI_KALIBI})\s+"
    r"(?P<unit>ay|month|months|gun|day|days)[a-z]*\b"
)


def resolve_period(
    time_mentions: tuple[SemanticMention, ...],
    *,
    time_dimension: str,
    today: date | None = None,
) -> ResolvedPeriod | None:
    """Resolve the P6.2 closed MVP period family from typed time spans only."""
    if not time_mentions:
        return None
    if len(time_mentions) != 1:
        raise TemporalResolutionError("Day3 MVP bir turda tek resolved time span bekler")

    source = time_mentions[0].text
    text = _norm(source).strip()
    now = today or date.today()

    if re.search(r"\b(?:bu\s+ay|this\s+month)\b", text):
        return ResolvedPeriod(
            kind=PeriodKind.THIS_MONTH,
            source_text=source,
            time_dimension=time_dimension,
            start=now.replace(day=1).isoformat(),
            end=now.isoformat(),
        )

    if re.search(r"\b(?:bu\s+(?:yil|sene)|this\s+year)\b", text):
        return ResolvedPeriod(
            kind=PeriodKind.THIS_YEAR,
            source_text=source,
            time_dimension=time_dimension,
            start=mali_takvim.yil_basi(now).isoformat(),
            end=now.isoformat(),
        )

    match = _LAST_N_RE.match(text)
    if match:
        n = sayi_coz(match.group("n"))
        if not n or n < 1:
            raise TemporalResolutionError(f"geçersiz göreli dönem sayısı: {source!r}")
        unit = match.group("unit")
        if unit in {"gun", "day", "days"}:
            return ResolvedPeriod(
                kind=PeriodKind.LAST_N_DAYS,
                source_text=source,
                time_dimension=time_dimension,
                start=(now - timedelta(days=n)).isoformat(),
                end=now.isoformat(),
                n=n,
            )
        return ResolvedPeriod(
            kind=PeriodKind.LAST_N_MONTHS,
            source_text=source,
            time_dimension=time_dimension,
            start=_months_ago(now, n).isoformat(),
            end=now.isoformat(),
            n=n,
        )

    previous = _PREVIOUS_RE.search(text)
    if previous:
        unit = previous.group("unit")
        if unit in {"ay", "month"}:
            start, end = _previous_month_window(now)
            return ResolvedPeriod(
                kind=PeriodKind.PREVIOUS_MONTH,
                source_text=source,
                time_dimension=time_dimension,
                start=start.isoformat(),
                end=end.isoformat(),
            )
        start, end = mali_takvim.yil_penceresi(now, kac_yil_once=1)
        return ResolvedPeriod(
            kind=PeriodKind.PREVIOUS_YEAR,
            source_text=source,
            time_dimension=time_dimension,
            start=start.isoformat(),
            end=end.isoformat(),
        )

    raise TemporalResolutionError(f"Day3 MVP time span desteklenmiyor: {source!r}")


def resolve_comparison(
    comparisons: tuple[ComparisonSurface, ...],
    *,
    base_period: ResolvedPeriod | None,
    time_dimension: str,
    today: date | None = None,
) -> ResolvedComparison | None:
    """Resolve a simple previous-month/year comparison without collapsing A and B."""
    if not comparisons:
        return None
    if len(comparisons) != 1:
        raise TemporalResolutionError("Day3 MVP bir turda tek comparison bekler")

    source = comparisons[0].text
    text = _norm(source).strip()
    previous_n = _PREVIOUS_N_RE.search(text)
    match = _PREVIOUS_RE.search(text)
    if not match and not previous_n:
        raise TemporalResolutionError(f"Day3 MVP comparison desteklenmiyor: {source!r}")

    now = today or date.today()

    if previous_n:
        n = sayi_coz(previous_n.group("n"))
        if not n or n < 1:
            raise TemporalResolutionError(f"geçersiz comparison period count: {source!r}")
        unit_n = previous_n.group("unit")
        if unit_n in {"ay", "month", "months"}:
            if base_period is None or base_period.kind != PeriodKind.LAST_N_MONTHS or base_period.n != n:
                raise TemporalResolutionError(
                    "previous-N-month comparison aynı N ile LAST_N_MONTHS base gerektirir"
                )
            base_start = date.fromisoformat(base_period.start)
            reference = ResolvedPeriod(
                kind=PeriodKind.LAST_N_MONTHS,
                source_text=source,
                time_dimension=time_dimension,
                start=_months_ago(base_start, n).isoformat(),
                end=(base_start - timedelta(days=1)).isoformat(),
                n=n,
            )
        else:
            if base_period is None or base_period.kind != PeriodKind.LAST_N_DAYS or base_period.n != n:
                raise TemporalResolutionError(
                    "previous-N-day comparison aynı N ile LAST_N_DAYS base gerektirir"
                )
            base_start = date.fromisoformat(base_period.start)
            reference = ResolvedPeriod(
                kind=PeriodKind.LAST_N_DAYS,
                source_text=source,
                time_dimension=time_dimension,
                start=(base_start - timedelta(days=n)).isoformat(),
                end=(base_start - timedelta(days=1)).isoformat(),
                n=n,
            )
        return ResolvedComparison(
            mode="previous_period",
            source_text=source,
            base_period=base_period,
            reference_period=reference,
        )

    assert match is not None
    unit = match.group("unit")

    if unit in {"ay", "month"}:
        if base_period is None:
            base_period = ResolvedPeriod(
                kind=PeriodKind.THIS_MONTH,
                source_text="implicit-current-month-for-comparison",
                time_dimension=time_dimension,
                start=now.replace(day=1).isoformat(),
                end=now.isoformat(),
            )
        if base_period.kind != PeriodKind.THIS_MONTH:
            raise TemporalResolutionError(
                "previous-month comparison yalnız current-month base ile Day3 MVP'de desteklenir"
            )
        start = _shift_month(date.fromisoformat(base_period.start))
        end = _shift_month(date.fromisoformat(base_period.end or now.isoformat()))
        reference = ResolvedPeriod(
            kind=PeriodKind.PREVIOUS_MONTH,
            source_text=source,
            time_dimension=time_dimension,
            start=start.isoformat(),
            end=end.isoformat(),
        )
    else:
        if base_period is None:
            base_period = ResolvedPeriod(
                kind=PeriodKind.THIS_YEAR,
                source_text="implicit-current-year-for-comparison",
                time_dimension=time_dimension,
                start=mali_takvim.yil_basi(now).isoformat(),
                end=now.isoformat(),
            )
        if base_period.kind != PeriodKind.THIS_YEAR:
            raise TemporalResolutionError(
                "previous-year comparison yalnız current-year base ile Day3 MVP'de desteklenir"
            )
        reference = ResolvedPeriod(
            kind=PeriodKind.PREVIOUS_YEAR,
            source_text=source,
            time_dimension=time_dimension,
            start=_shift_year(date.fromisoformat(base_period.start)).isoformat(),
            end=_shift_year(date.fromisoformat(base_period.end or now.isoformat())).isoformat(),
        )

    return ResolvedComparison(
        mode="previous_period",
        source_text=source,
        base_period=base_period,
        reference_period=reference,
    )


def period_filters(period: ResolvedPeriod | None) -> list[dict]:
    if period is None:
        return []
    out = [
        {
            "dimension": period.time_dimension,
            "operator": "gte",
            "value": period.start,
        }
    ]
    if period.end:
        out.append(
            {
                "dimension": period.time_dimension,
                "operator": "lte",
                "value": period.end,
            }
        )
    return out
