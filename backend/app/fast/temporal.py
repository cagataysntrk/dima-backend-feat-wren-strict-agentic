"""Deterministic temporal authority for Fast Ask."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta

from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import DraftTemporalIntent, TemporalKind, TemporalWindow


def _next_month(day: date) -> date:
    if day.month == 12:
        return date(day.year + 1, 1, 1)
    return date(day.year, day.month + 1, 1)


def _previous_month_start(day: date) -> date:
    if day.month == 1:
        return date(day.year - 1, 12, 1)
    return date(day.year, day.month - 1, 1)


def bind_temporal(
    intent: DraftTemporalIntent,
    *,
    as_of_date: date | None,
) -> TemporalWindow | None:
    if intent.kind == TemporalKind.NONE:
        return None

    if intent.kind == TemporalKind.LAST_N_DAYS:
        if as_of_date is None:
            raise FastAskError(
                FastAskErrorCode.TEMPORAL_ANCHOR_REQUIRED,
                "relative temporal intent requires as_of_date",
            )
        assert intent.days is not None
        return TemporalWindow(
            kind=intent.kind,
            start=as_of_date - timedelta(days=intent.days - 1),
            end_exclusive=as_of_date + timedelta(days=1),
        )

    if intent.kind == TemporalKind.CURRENT_MONTH:
        if as_of_date is None:
            raise FastAskError(
                FastAskErrorCode.TEMPORAL_ANCHOR_REQUIRED,
                "current-month intent requires as_of_date",
            )
        start = date(as_of_date.year, as_of_date.month, 1)
        return TemporalWindow(kind=intent.kind, start=start, end_exclusive=_next_month(start))

    if intent.kind == TemporalKind.PREVIOUS_MONTH:
        if as_of_date is None:
            raise FastAskError(
                FastAskErrorCode.TEMPORAL_ANCHOR_REQUIRED,
                "previous-month intent requires as_of_date",
            )
        current = date(as_of_date.year, as_of_date.month, 1)
        return TemporalWindow(
            kind=intent.kind,
            start=_previous_month_start(current),
            end_exclusive=current,
        )

    if intent.kind == TemporalKind.ABSOLUTE_DATE_RANGE:
        try:
            start = date.fromisoformat(str(intent.start_date))
            end_inclusive = date.fromisoformat(str(intent.end_date))
        except ValueError as exc:
            raise FastAskError(
                FastAskErrorCode.TEMPORAL_INVALID,
                "absolute temporal dates must be ISO YYYY-MM-DD",
            ) from exc
        if start > end_inclusive:
            raise FastAskError(
                FastAskErrorCode.TEMPORAL_INVALID,
                "absolute temporal start must be <= end",
            )
        return TemporalWindow(
            kind=intent.kind,
            start=start,
            end_exclusive=end_inclusive + timedelta(days=1),
        )

    raise FastAskError(
        FastAskErrorCode.TEMPORAL_INVALID,
        f"unsupported temporal kind: {intent.kind}",
    )
