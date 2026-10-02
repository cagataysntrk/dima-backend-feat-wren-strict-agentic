"""Read-only P20 projection of governed tabular Evidence.

This module performs no analytics. It preserves source-backed row/column meaning
that already exists in a terminal native result so P20 can present exact facts
without reopening Metabot or inventing calculations.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class GovernedTabularContext(Frozen):
    label: str = Field(min_length=1)
    value: str = Field(min_length=1)


class GovernedTabularMetric(Frozen):
    source_path: str = Field(pattern=r"^data\.rows\.[0-9]+\.[0-9]+$")
    label: str = Field(min_length=1)
    value: int | float

    @field_validator("value", mode="before")
    @classmethod
    def numeric_not_boolean(cls, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("governed tabular metric value must be numeric")
        return value


class GovernedTabularRowObservation(Frozen):
    context: tuple[GovernedTabularContext, ...] = ()
    metrics: tuple[GovernedTabularMetric, ...] = Field(min_length=1)


class GovernedTabularNumericFact(Frozen):
    source_path: str = Field(pattern=r"^data\.rows\.[0-9]+\.[0-9]+$")
    label: str = Field(min_length=1)
    context: tuple[GovernedTabularContext, ...] = ()
    value: int | float

    @field_validator("value", mode="before")
    @classmethod
    def numeric_not_boolean(cls, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("governed tabular fact value must be numeric")
        return value


def _column_label(data: dict[str, Any], column_index: int) -> str:
    cols = data.get("cols")
    if isinstance(cols, list) and column_index < len(cols):
        item = cols[column_index]
        if isinstance(item, dict):
            for key in ("display_name", "name"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return f"column_{column_index}"


def project_governed_tabular_rows(
    payload: Any,
) -> tuple[GovernedTabularRowObservation, ...]:
    """Project one source row to one exact presentation observation."""

    if not isinstance(payload, dict):
        return ()
    data = payload.get("data")
    if not isinstance(data, dict):
        return ()
    rows = data.get("rows")
    if not isinstance(rows, list):
        return ()

    projected: list[GovernedTabularRowObservation] = []
    for row_index, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        context = tuple(
            GovernedTabularContext(
                label=_column_label(data, column_index),
                value=value,
            )
            for column_index, value in enumerate(row)
            if isinstance(value, str) and value.strip()
        )
        metrics = tuple(
            GovernedTabularMetric(
                source_path=f"data.rows.{row_index}.{column_index}",
                label=_column_label(data, column_index),
                value=value,
            )
            for column_index, value in enumerate(row)
            if not isinstance(value, bool) and isinstance(value, (int, float))
        )
        if metrics:
            projected.append(
                GovernedTabularRowObservation(
                    context=context,
                    metrics=metrics,
                )
            )
    return tuple(projected)


def project_governed_tabular_numeric_facts(
    payload: Any,
) -> tuple[GovernedTabularNumericFact, ...]:
    """Project exact numeric cells with source-backed labels and row context."""

    if not isinstance(payload, dict):
        return ()
    data = payload.get("data")
    if not isinstance(data, dict):
        return ()
    rows = data.get("rows")
    if not isinstance(rows, list):
        return ()

    facts: list[GovernedTabularNumericFact] = []
    for row_index, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        context = tuple(
            GovernedTabularContext(
                label=_column_label(data, column_index),
                value=value,
            )
            for column_index, value in enumerate(row)
            if isinstance(value, str) and value.strip()
        )
        for column_index, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            facts.append(
                GovernedTabularNumericFact(
                    source_path=f"data.rows.{row_index}.{column_index}",
                    label=_column_label(data, column_index),
                    context=context,
                    value=value,
                )
            )
    return tuple(facts)


def governed_tabular_numeric_fact_for_path(
    payload: Any,
    source_path: str,
) -> GovernedTabularNumericFact | None:
    for fact in project_governed_tabular_numeric_facts(payload):
        if fact.source_path == source_path:
            return fact
    return None
