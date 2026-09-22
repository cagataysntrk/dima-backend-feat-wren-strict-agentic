"""Deterministic portable MBQL builder for the FT-003 supported family."""

from __future__ import annotations

from typing import Any

from app.fast.ask_models import (
    AggregationKind,
    AskDraft,
    FieldAuthority,
    TableAuthority,
    TemporalWindow,
)


def field_ref(field: FieldAuthority) -> list[Any]:
    return ["field", {}, list(field.portable_fk)]


def build_portable_query(
    *,
    draft: AskDraft,
    table: TableAuthority,
    measure: FieldAuthority | None,
    temporal_field: FieldAuthority | None,
    breakdown: FieldAuthority | None,
    temporal_window: TemporalWindow | None,
) -> dict[str, Any]:
    if draft.aggregation == AggregationKind.SUM:
        if measure is None or not measure.numeric:
            raise ValueError("SUM requires an accepted numeric measure field")
        aggregation: list[Any] = ["sum", {}, field_ref(measure)]
    else:
        if measure is not None:
            raise ValueError("COUNT must not carry a measure field")
        aggregation = ["count", {}]

    stage: dict[str, Any] = {
        "lib/type": "mbql.stage/mbql",
        "source-table": list(table.portable_fk),
        "aggregation": [aggregation],
    }

    if temporal_window is not None:
        if temporal_field is None or not temporal_field.temporal:
            raise ValueError("temporal window requires an accepted temporal field")
        ref = field_ref(temporal_field)
        stage["filters"] = [[
            "and",
            {},
            [">=", {}, ref, temporal_window.start.isoformat()],
            ["<", {}, ref, temporal_window.end_exclusive.isoformat()],
        ]]
    elif temporal_field is not None:
        raise ValueError("temporal field without temporal window is not allowed")

    if breakdown is not None:
        stage["breakout"] = [field_ref(breakdown)]
        stage["order-by"] = [["desc", {}, ["aggregation", {}, 0]]]
        stage["limit"] = 100

    return {
        "lib/type": "mbql/query",
        "stages": [stage],
    }
