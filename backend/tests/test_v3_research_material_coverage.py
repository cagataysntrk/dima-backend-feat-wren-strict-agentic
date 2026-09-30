from __future__ import annotations

import pytest

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
)
from app.v3.research_analytical_scope import NativeMaterialBinding
from app.v3.research_material_coverage import (
    ResearchMaterialCoverageError,
    assert_material_result_coverage,
)


def _contract() -> AnalyticalRequestContract:
    return AnalyticalRequestContract(
        authority_id="authority-fixture",
        request_ref="request-fixture",
        semantic_context_version="context-fixture",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="lineage-fixture",
            version_id="scope_v1",
        ),
        metric_refs=("metric.effect", "metric.candidate.a", "metric.candidate.b"),
        dimension_refs=(),
        comparison=AnalyticalComparisonInvariant(
            mode="explicit_periods",
            reference_period=AnalyticalPeriodInvariant(
                kind="accepted_period",
                time_dimension="dimension.time",
                start="2026-03-01",
                end="2026-04-01",
            ),
            base_period=AnalyticalPeriodInvariant(
                kind="accepted_period",
                time_dimension="dimension.time",
                start="2026-04-01",
                end="2026-05-01",
            ),
        ),
    )


def _bindings() -> dict[str, NativeMaterialBinding]:
    return {
        "dimension.time": NativeMaterialBinding(
            candidate_id="dimension.time",
            candidate_kind="dimension",
            database_id=1,
            table_id=10,
            field_id=44,
        ),
    }


def _col(field_id: int, display_name: str) -> dict:
    return {
        "display_name": display_name,
        "field_ref": ["field", field_id, {"temporal-unit": "month"}],
    }


def test_comparison_result_without_governed_time_column_fails_closed() -> None:
    payload = {
        "data": {
            "cols": [
                {"display_name": "Effect"},
                {"display_name": "Candidate A"},
                {"display_name": "Candidate B"},
            ],
            "rows": [[120, 9, 4]],
        }
    }

    with pytest.raises(ResearchMaterialCoverageError) as exc:
        assert_material_result_coverage(
            contract=_contract(),
            result_payload=payload,
            bindings=_bindings(),
        )

    assert exc.value.code == "R1_RESULT_TEMPORAL_COLUMN_MISMATCH"


def test_comparison_result_covering_only_one_accepted_period_fails_closed() -> None:
    payload = {
        "data": {
            "cols": [
                _col(44, "Accepted Time"),
                {"display_name": "Effect"},
                {"display_name": "Candidate A"},
                {"display_name": "Candidate B"},
            ],
            "rows": [["2026-04-01", 120, 9, 4]],
        }
    }

    with pytest.raises(ResearchMaterialCoverageError) as exc:
        assert_material_result_coverage(
            contract=_contract(),
            result_payload=payload,
            bindings=_bindings(),
        )

    assert exc.value.code == "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE"
    assert exc.value.detail == "reference_period"


def test_comparison_result_covering_both_accepted_periods_is_full() -> None:
    payload = {
        "data": {
            "cols": [
                _col(44, "Accepted Time"),
                {"display_name": "Effect"},
                {"display_name": "Candidate A"},
                {"display_name": "Candidate B"},
            ],
            "rows": [
                ["2026-03-01", 100, 6, 5],
                ["2026-04-01", 120, 9, 4],
            ],
        }
    }

    coverage = assert_material_result_coverage(
        contract=_contract(),
        result_payload=payload,
        bindings=_bindings(),
    )

    assert coverage.status == "FULL"
    assert coverage.result_row_count == 2
    assert coverage.time_field_id == 44
    assert coverage.covered_comparison_roles == (
        "reference_period",
        "base_period",
    )


def _datetime_contract(
    *,
    reference_start: str,
    reference_end: str,
    base_start: str,
    base_end: str,
) -> AnalyticalRequestContract:
    return _contract().model_copy(
        update={
            "comparison": AnalyticalComparisonInvariant(
                mode="explicit_periods",
                reference_period=AnalyticalPeriodInvariant(
                    kind="accepted_period",
                    time_dimension="dimension.time",
                    start=reference_start,
                    end=reference_end,
                ),
                base_period=AnalyticalPeriodInvariant(
                    kind="accepted_period",
                    time_dimension="dimension.time",
                    start=base_start,
                    end=base_end,
                ),
            )
        }
    )


def _datetime_payload(reference_value: str, base_value: str) -> dict:
    return {
        "data": {
            "cols": [
                _col(44, "Accepted Time"),
                {"display_name": "Effect"},
            ],
            "rows": [
                [reference_value, 100],
                [base_value, 120],
            ],
        }
    }


def test_datetime_comparison_normalizes_naive_bounds_against_utc_result() -> None:
    coverage = assert_material_result_coverage(
        contract=_datetime_contract(
            reference_start="2026-03-01T00:00:00",
            reference_end="2026-04-01T00:00:00",
            base_start="2026-04-01T00:00:00",
            base_end="2026-05-01T00:00:00",
        ),
        result_payload=_datetime_payload(
            "2026-03-01T00:00:00Z",
            "2026-04-01T00:00:00+00:00",
        ),
        bindings=_bindings(),
    )

    assert coverage.status == "FULL"
    assert coverage.covered_comparison_roles == (
        "reference_period",
        "base_period",
    )


def test_datetime_comparison_normalizes_naive_result_against_utc_bounds() -> None:
    coverage = assert_material_result_coverage(
        contract=_datetime_contract(
            reference_start="2026-03-01T00:00:00Z",
            reference_end="2026-04-01T00:00:00Z",
            base_start="2026-04-01T00:00:00Z",
            base_end="2026-05-01T00:00:00Z",
        ),
        result_payload=_datetime_payload(
            "2026-03-01T00:00:00",
            "2026-04-01T00:00:00",
        ),
        bindings=_bindings(),
    )

    assert coverage.status == "FULL"


def test_datetime_comparison_compares_equivalent_instants_across_offsets() -> None:
    coverage = assert_material_result_coverage(
        contract=_datetime_contract(
            reference_start="2026-03-01T03:00:00+03:00",
            reference_end="2026-04-01T03:00:00+03:00",
            base_start="2026-04-01T03:00:00+03:00",
            base_end="2026-05-01T03:00:00+03:00",
        ),
        result_payload=_datetime_payload(
            "2026-03-01T00:00:00Z",
            "2026-04-01T00:00:00Z",
        ),
        bindings=_bindings(),
    )

    assert coverage.status == "FULL"


def test_non_comparison_material_does_not_invent_temporal_coverage_requirement() -> None:
    contract = _contract().model_copy(update={"comparison": None})
    payload = {
        "data": {
            "cols": [{"display_name": "Effect"}],
            "rows": [[120]],
        }
    }

    coverage = assert_material_result_coverage(
        contract=contract,
        result_payload=payload,
        bindings={},
    )

    assert coverage.status == "FULL"
    assert coverage.result_row_count == 1
    assert coverage.covered_comparison_roles == ()
