from __future__ import annotations

import inspect
from types import SimpleNamespace

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalEvidenceSynthesisRankingInvariant,
    AnalyticalFilterInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
)
from app.v3.research import ResearchManager
from app.v3.research_analytical_scope import native_request_context


def _contract(
    *,
    scope_version: str = "scope_v1",
    comparison: bool = True,
    evidence_synthesis: bool = True,
):
    reference = AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension="dimension.event_date",
        start="2026-05-01",
        end="2026-06-01",
    )
    base = AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension="dimension.event_date",
        start="2026-06-01",
        end="2026-07-01",
    )
    ranking = (
        AnalyticalEvidenceSynthesisRankingInvariant(
            direction="desc",
            limit=None,
        )
        if evidence_synthesis
        else AnalyticalRankingInvariant(
            measure="metric.machine_downtime_minutes",
            direction="desc",
            limit=2,
        )
    )
    return AnalyticalRequestContract(
        authority_id="authority-r7",
        request_ref=f"research-r7:{scope_version}",
        semantic_context_version="phase1-final-pinpoint-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="lineage-r7",
            version_id=scope_version,
        ),
        metric_refs=(
            "metric.machine_downtime_minutes",
            "metric.fault_count",
        ),
        dimension_refs=("dimension.department",),
        filters=(
            AnalyticalFilterInvariant(
                semantic_ref="entity.department.assembly",
                source_candidate_id="entity.department.assembly",
                dimension_name="dimension.department",
                value="Assembly",
            ),
        ),
        period=None if comparison else base,
        comparison=(
            AnalyticalComparisonInvariant(
                mode="explicit_periods",
                reference_period=reference,
                base_period=base,
            )
            if comparison
            else None
        ),
        ranking=ranking,
        grain_constraints=("dimension.department",),
        requested_output_surfaces=("table",),
    )


def _message(contract):
    return ResearchManager._native_material_message(
        SimpleNamespace(objective="Investigate the accepted obligation."),
        contract,
    )


def test_r7_delivers_exact_governed_contract_on_visible_native_message():
    message = _message(_contract())

    assert message.startswith("[DIMA ACCEPTED ANALYTICAL CONTRACT]\n")
    assert "scope_version: scope_v1" in message
    assert "metrics:\n- metric.machine_downtime_minutes\n- metric.fault_count" in message
    assert "dimensions:\n- dimension.department" in message
    assert (
        'filters:\n- entity.department.assembly: dimension.department = "Assembly"'
        in message
    )
    assert (
        "periods:\n"
        "- reference: dimension.event_date [2026-05-01, 2026-06-01)\n"
        "- base: dimension.event_date [2026-06-01, 2026-07-01)"
        in message
    )
    assert "grain_constraints:\n- dimension.department" in message
    assert "output_surfaces:\n- table" in message
    assert "[USER OBLIGATION]\nInvestigate the accepted obligation." in message


def test_r7_shared_material_contract_serializes_required_and_allowed_sets():
    contract = _contract(evidence_synthesis=False)
    message = _message(contract)
    context = native_request_context(contract)["dima_analytical_scope"]

    assert (
        "required_metrics:\n"
        "- metric.machine_downtime_minutes\n"
        "- metric.fault_count"
    ) in message
    assert (
        "allowed_metrics:\n"
        "- metric.machine_downtime_minutes\n"
        "- metric.fault_count"
    ) in message
    assert context["material_coverage"]["required_metric_refs"] == [
        "metric.machine_downtime_minutes",
        "metric.fault_count",
    ]
    assert context["material_coverage"]["allowed_metric_refs"] == [
        "metric.machine_downtime_minutes",
        "metric.fault_count",
    ]
    assert (
        "- every required metric must be observable in the same native occurrence"
        in message
    )
    assert "- no metric outside allowed_metrics may enter the occurrence" in message


def test_r7_evidence_synthesis_has_exact_metric_set_without_native_ranking_basis():
    message = _message(_contract(evidence_synthesis=True))

    assert "- metric.machine_downtime_minutes" in message
    assert "- metric.fault_count" in message
    assert "- kind: evidence_synthesis" in message
    assert "- native_measure: none" in message
    assert "- native_limit: none" in message
    assert "composite score" in message
    assert "return unranked analytical material" in message
    assert "\n- measure:" not in message


def test_r7_governed_native_metric_ranking_keeps_actual_measure_direction_and_limit():
    message = _message(_contract(evidence_synthesis=False))

    assert "- kind: native_metric" in message
    assert "- measure: metric.machine_downtime_minutes" in message
    assert "- direction: desc" in message
    assert "- limit: 2" in message
    assert "preserve the governed native ranking basis exactly" in message


def test_r7_followup_narrowing_delivers_only_current_scope_version_constraints():
    message = _message(
        _contract(
            scope_version="scope_v2",
            comparison=False,
            evidence_synthesis=True,
        )
    )

    assert "scope_version: scope_v2" in message
    assert "2026-06-01, 2026-07-01)" in message
    assert "2026-05-01" not in message
    assert "scope_v1" not in message


def test_r7_contract_delivery_has_no_planner_sql_mbql_or_benchmark_authority():
    source = inspect.getsource(ResearchManager._native_material_message)
    forbidden = (
        "sqlparse",
        "parse_mbql",
        "SELECT ",
        "SCOPE_CURRENTNESS_HARD",
        "RCA_P19_HARD",
        "F05_H",
        "F08_H",
        "F06_H",
        "Mayıs",
        "Haziran",
    )
    for value in forbidden:
        assert value not in source
