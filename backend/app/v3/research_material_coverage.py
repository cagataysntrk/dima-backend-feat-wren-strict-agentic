"""Deterministic result-coverage checks for governed Research material.

This module does not plan or interpret analytics. Metabase/Metabot already
computed the result and the native material observer already proved query-scope
semantics. Here Dima only verifies that a result promoted to Evidence actually
represents the typed material surface it claims to satisfy.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytical_request_contract import (
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
)
from app.v3.research_analytical_scope import NativeMaterialBinding
from app.v3.research_contracts import RankingBasis


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchMaterialCoverageError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class MaterialResultCoverage(Frozen):
    """Deterministic receipt of what result-level coverage was verified."""

    status: Literal["FULL"] = "FULL"
    result_row_count: int = Field(ge=0)
    time_field_id: int | None = Field(default=None, gt=0)
    observed_temporal_value_count: int = Field(default=0, ge=0)
    covered_comparison_roles: tuple[
        Literal["reference_period", "base_period"], ...
    ] = ()


def _rows_and_cols(
    payload: Mapping[str, Any],
) -> tuple[list[Any], list[Any]]:
    data = payload.get("data")
    if not isinstance(data, Mapping):
        raise ResearchMaterialCoverageError(
            "R1_RESULT_DATA_MISSING",
            "native material result has no dataset data object",
        )
    rows = data.get("rows")
    cols = data.get("cols")
    if not isinstance(rows, list):
        raise ResearchMaterialCoverageError(
            "R1_RESULT_ROWS_MISSING",
            "native material result has no row collection",
        )
    if not isinstance(cols, list):
        raise ResearchMaterialCoverageError(
            "R1_RESULT_COLUMNS_MISSING",
            "native material result has no column metadata",
        )
    return rows, cols


def _column_field_id(column: object) -> int | None:
    if not isinstance(column, Mapping):
        return None
    direct = column.get("id")
    if isinstance(direct, int) and direct > 0:
        return direct
    direct = column.get("field_id")
    if isinstance(direct, int) and direct > 0:
        return direct
    field_ref = column.get("field_ref")
    if field_ref is None:
        field_ref = column.get("field-ref")
    if (
        isinstance(field_ref, (list, tuple))
        and len(field_ref) >= 2
        and field_ref[0] == "field"
        and isinstance(field_ref[1], int)
        and field_ref[1] > 0
    ):
        return field_ref[1]
    return None


def _canonical_datetime(value: str) -> datetime:
    """Normalize a typed/result ISO datetime into one comparable UTC domain.

    AnalyticalPeriodInvariant does not carry a separate timezone authority.
    Offset-less datetimes therefore use the platform's canonical UTC basis;
    offset-aware values preserve their instant and are converted to UTC.
    """

    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        return stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc)


def _unbounded_temporal_value(raw: object) -> tuple[str, date | datetime]:
    """Normalize one observed time value without inventing calendar bounds."""

    if not isinstance(raw, str) or not raw.strip():
        raise ResearchMaterialCoverageError(
            "R1_RESULT_TEMPORAL_VALUE_INVALID",
            "change result temporal value is not a non-empty ISO string",
        )
    value = raw.strip()
    if "T" not in value:
        try:
            return ("date", date.fromisoformat(value))
        except ValueError as exc:
            raise ResearchMaterialCoverageError(
                "R1_RESULT_TEMPORAL_VALUE_INVALID",
                "change result temporal value is not ISO-8601",
            ) from exc
    try:
        return ("datetime", _canonical_datetime(value))
    except ValueError as exc:
        raise ResearchMaterialCoverageError(
            "R1_RESULT_TEMPORAL_VALUE_INVALID",
            "change result temporal value is not ISO-8601",
        ) from exc


def _period_value(
    raw: object,
    period: AnalyticalPeriodInvariant,
) -> date | datetime:
    if not isinstance(raw, str) or not raw.strip():
        raise ResearchMaterialCoverageError(
            "R1_RESULT_TEMPORAL_VALUE_INVALID",
            "comparison result temporal value is not a non-empty ISO string",
        )
    value = raw.strip()
    date_bounds = "T" not in period.start and (
        period.end is None or "T" not in period.end
    )
    if date_bounds:
        try:
            if "T" in value:
                return datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                ).date()
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ResearchMaterialCoverageError(
                "R1_RESULT_TEMPORAL_VALUE_INVALID",
                "comparison result temporal value is not ISO-8601",
            ) from exc
    try:
        return _canonical_datetime(value)
    except ValueError as exc:
        raise ResearchMaterialCoverageError(
            "R1_RESULT_TEMPORAL_VALUE_INVALID",
            "comparison result temporal value is not ISO-8601",
        ) from exc


def _period_bounds(
    period: AnalyticalPeriodInvariant,
) -> tuple[date | datetime, date | datetime]:
    if period.end is None:
        raise ResearchMaterialCoverageError(
            "R1_RESULT_OPEN_COMPARISON_UNSUPPORTED",
            "result coverage requires bounded comparison periods",
        )
    if "T" not in period.start and "T" not in period.end:
        return date.fromisoformat(period.start), date.fromisoformat(period.end)
    try:
        return (
            _canonical_datetime(period.start),
            _canonical_datetime(period.end),
        )
    except ValueError as exc:
        raise ResearchMaterialCoverageError(
            "R1_RESULT_COMPARISON_PERIOD_INVALID",
            "comparison period bounds are not ISO-8601",
        ) from exc


def _contains(
    raw: object,
    period: AnalyticalPeriodInvariant,
) -> bool:
    value = _period_value(raw, period)
    start, end = _period_bounds(period)
    return start <= value < end


def assert_material_result_coverage(
    *,
    contract: AnalyticalRequestContract,
    result_payload: Mapping[str, Any],
    bindings: Mapping[str, NativeMaterialBinding],
    attested_native_material: bool = False,
) -> MaterialResultCoverage:
    """Fail closed when VERIFIED Evidence would overstate result coverage.

    A native comparison or CHANGE ranking may legitimately project only final
    comparison/derived columns after Metabot used governed time material in
    earlier stages. Omitting that intermediate time column is admissible only
    when this exact native occurrence has already passed material-scope
    validation. Unattested results remain row-level strict, and any result that
    still exposes the governed time column must satisfy exact period coverage.
    """

    rows, cols = _rows_and_cols(result_payload)
    comparison = contract.comparison
    temporal_observation = contract.temporal_observation
    if comparison is None and temporal_observation is None:
        return MaterialResultCoverage(result_row_count=len(rows))

    if comparison is not None:
        reference_ref = comparison.reference_period.time_dimension
        base_ref = comparison.base_period.time_dimension
        if reference_ref != base_ref:
            raise ResearchMaterialCoverageError(
                "R1_RESULT_COMPARISON_DIMENSION_DRIFT",
                "comparison periods use different governed time dimensions",
            )
        time_ref = reference_ref
        missing_column_code = "R1_RESULT_TEMPORAL_COLUMN_MISMATCH"
        missing_column_detail = (
            "comparison Evidence requires exactly one result column bound "
            "to the governed time field"
        )
    else:
        assert temporal_observation is not None
        time_ref = temporal_observation.time_dimension
        missing_column_code = "R1_RESULT_CHANGE_TEMPORAL_COLUMN_REQUIRED"
        missing_column_detail = (
            "change Evidence requires exactly one result column bound "
            "to the governed time field"
        )

    binding = bindings.get(time_ref)
    if binding is None or binding.field_id is None:
        raise ResearchMaterialCoverageError(
            "R1_RESULT_TEMPORAL_BINDING_REQUIRED",
            time_ref,
        )
    matches = [
        index
        for index, column in enumerate(cols)
        if _column_field_id(column) == binding.field_id
    ]
    if len(matches) != 1:
        attested_temporal_projection = (
            attested_native_material
            and len(matches) == 0
            and (
                comparison is not None
                or (
                    isinstance(contract.ranking, AnalyticalRankingInvariant)
                    and contract.ranking.basis == RankingBasis.CHANGE
                )
            )
        )
        if attested_temporal_projection:
            # The exact native occurrence has already passed material-scope
            # validation for the accepted temporal contract. Metabase may
            # legitimately project away the intermediate time breakout in the
            # final rowset (comparison scalar/derived columns or CHANGE rank).
            # This propagates that semantic proof; it does not admit an
            # unattested result and it does not bypass row-level checks when a
            # governed time column is actually present.
            return MaterialResultCoverage(
                result_row_count=len(rows),
                covered_comparison_roles=(
                    ("reference_period", "base_period")
                    if comparison is not None
                    else ()
                ),
            )
        raise ResearchMaterialCoverageError(
            missing_column_code,
            missing_column_detail,
        )
    time_index = matches[0]
    temporal_values: list[object] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or time_index >= len(row):
            raise ResearchMaterialCoverageError(
                "R1_RESULT_ROW_SHAPE_INVALID",
                "temporal result row does not carry the governed time column",
            )
        temporal_values.append(row[time_index])

    if comparison is not None:
        reference_covered = any(
            _contains(value, comparison.reference_period)
            for value in temporal_values
        )
        base_covered = any(
            _contains(value, comparison.base_period)
            for value in temporal_values
        )
        if not reference_covered or not base_covered:
            missing = []
            if not reference_covered:
                missing.append("reference_period")
            if not base_covered:
                missing.append("base_period")
            raise ResearchMaterialCoverageError(
                "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
                ",".join(missing),
            )
        normalized_values = {
            _period_value(value, comparison.reference_period)
            for value in temporal_values
        }
        return MaterialResultCoverage(
            result_row_count=len(rows),
            time_field_id=binding.field_id,
            observed_temporal_value_count=len(normalized_values),
            covered_comparison_roles=("reference_period", "base_period"),
        )

    assert temporal_observation is not None
    period = contract.period
    if period is None:
        normalized_values = {
            _unbounded_temporal_value(value)
            for value in temporal_values
        }
    else:
        normalized_values = {
            _period_value(value, period)
            for value in temporal_values
            if _contains(value, period)
        }
    if len(normalized_values) < temporal_observation.minimum_distinct_values:
        raise ResearchMaterialCoverageError(
            "R1_RESULT_CHANGE_COVERAGE_INCOMPLETE",
            (
                f"observed {len(normalized_values)} distinct governed time "
                f"values; requires {temporal_observation.minimum_distinct_values}"
            ),
        )
    return MaterialResultCoverage(
        result_row_count=len(rows),
        time_field_id=binding.field_id,
        observed_temporal_value_count=len(normalized_values),
    )

