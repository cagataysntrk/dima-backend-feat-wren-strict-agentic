"""Provider-free Day7 proofs for zero-query derived analytical Evidence."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.v2.derived_evidence import (
    ContributionDerivedArgs,
    DerivedEvidenceError,
    DerivedEvidenceService,
    PeerCompareDerivedArgs,
    TrendDerivedArgs,
)
from app.v2.models import EvidenceArtifact, ResearchTask, ResearchTaskKind


METRIC = "sem_metric"
TIME = "sem_time"
DIM = "sem_dimension"


def _task(
    kind: ResearchTaskKind,
    parent: EvidenceArtifact,
    *refs: str,
    task_id: str = "D1",
) -> ResearchTask:
    return ResearchTask(
        task_id=task_id,
        question_id="U1",
        task_kind=kind.value,
        input_refs=tuple(refs),
        origin="AGENT_DERIVED",
        parent_task_id=parent.task_id,
        parent_obligation_id="U1",
        trigger_evidence_ref=parent.artifact_id,
        branch_depth=1,
    )


def _parent(
    *,
    executions,
    verified: bool = True,
    artifact_id: str = "E_PARENT",
    task_id: str = "seed:U1",
    qrefs=("QC1",),
) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        task_id=task_id,
        obligation_ids=("U1",),
        query_contract_refs=tuple(qrefs),
        evidence_kind="standard_analytics",
        verified=verified,
        payload={
            "query_count": len(tuple(executions)),
            "executions": tuple(executions),
        },
    )


def _trend_parent(values=(10, 12, 15, 18, 21), times=None, verified=True):
    if times is None:
        times = (
            "2026-01-01",
            "2026-02-01",
            "2026-03-01",
            "2026-04-01",
            "2026-05-01",
        )[: len(values)]
    return _parent(
        verified=verified,
        executions=(
            {
                "execution_id": "trend-primary",
                "role": "primary",
                "columns": (TIME, METRIC),
                "row_count": len(values),
                "rows": tuple(
                    {TIME: t, METRIC: v}
                    for t, v in zip(times, values)
                ),
            },
        ),
    )


def _contribution_parent(*, verified=True, missing_reference_metric=False):
    reference_rows = [
        {DIM: "A", METRIC: 80.0},
        {DIM: "B", METRIC: 50.0},
        {DIM: "C", METRIC: 20.0},
    ]
    if missing_reference_metric:
        reference_rows[1] = {DIM: "B"}
    return _parent(
        verified=verified,
        qrefs=("QC_CUR", "QC_REF"),
        executions=(
            {
                "execution_id": "current",
                "role": "primary",
                "columns": (DIM, METRIC),
                "row_count": 3,
                "rows": (
                    {DIM: "A", METRIC: 100.0},
                    {DIM: "B", METRIC: 40.0},
                    {DIM: "C", METRIC: 30.0},
                ),
            },
            {
                "execution_id": "reference",
                "role": "comparison_reference",
                "columns": (DIM, METRIC),
                "row_count": 3,
                "rows": tuple(reference_rows),
            },
        ),
    )


def _peer_parent(*, rows=None, verified=True):
    if rows is None:
        rows = (
            {DIM: "TARGET", METRIC: 80.0},
            {DIM: "P1", METRIC: 100.0},
            {DIM: "P2", METRIC: 120.0},
        )
    return _parent(
        verified=verified,
        executions=(
            {
                "execution_id": "peers",
                "role": "primary",
                "columns": (DIM, METRIC),
                "row_count": len(rows),
                "rows": tuple(rows),
            },
        ),
    )


def test_trend_verified_ordered_series_produces_derived_evidence_with_lineage():
    parent = _trend_parent()
    task = _task(ResearchTaskKind.TREND, parent, METRIC, TIME)

    result = DerivedEvidenceService().trend(
        task=task,
        parent=parent,
        args=TrendDerivedArgs(
            metric_handle=METRIC,
            time_axis_handle=TIME,
            ordering="ASCENDING",
            ordering_provenance_ref="QC1:time-axis:asc",
        ),
    )

    assert result.verified is True
    assert result.source_kind == "DERIVED_ANALYTICAL"
    assert result.transformation == "TREND"
    assert result.parent_evidence_refs == ("E_PARENT",)
    assert result.parent_query_contract_refs == ("QC1",)
    assert result.query_contract_refs == ("QC1",)
    assert result.payload["sample_count"] == 5
    assert result.payload["trend"]["yon"] == "artan"
    assert "significance" in result.limitations[0]


def test_trend_below_minimum_has_no_claim():
    parent = _trend_parent(
        values=(1, 2, 3, 4),
        times=("2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"),
    )
    task = _task(ResearchTaskKind.TREND, parent, METRIC, TIME)

    with pytest.raises(DerivedEvidenceError, match="at least 5"):
        DerivedEvidenceService().trend(
            task=task,
            parent=parent,
            args=TrendDerivedArgs(
                metric_handle=METRIC,
                time_axis_handle=TIME,
                ordering="ASCENDING",
                ordering_provenance_ref="QC1:time-axis:asc",
            ),
        )


def test_trend_unordered_series_is_rejected():
    parent = _trend_parent(
        times=(
            "2026-01-01",
            "2026-03-01",
            "2026-02-01",
            "2026-04-01",
            "2026-05-01",
        )
    )
    task = _task(ResearchTaskKind.TREND, parent, METRIC, TIME)

    with pytest.raises(DerivedEvidenceError, match="ordering"):
        DerivedEvidenceService().trend(
            task=task,
            parent=parent,
            args=TrendDerivedArgs(
                metric_handle=METRIC,
                time_axis_handle=TIME,
                ordering="ASCENDING",
                ordering_provenance_ref="QC1:time-axis:asc",
            ),
        )


def test_derived_transform_rejects_unverified_parent_evidence():
    parent = _trend_parent(verified=False)
    task = _task(ResearchTaskKind.TREND, parent, METRIC, TIME)

    with pytest.raises(DerivedEvidenceError, match="not verified"):
        DerivedEvidenceService().trend(
            task=task,
            parent=parent,
            args=TrendDerivedArgs(
                metric_handle=METRIC,
                time_axis_handle=TIME,
                ordering="ASCENDING",
                ordering_provenance_ref="QC1:time-axis:asc",
            ),
        )


def test_contribution_verified_aligned_rows_preserve_mass_and_noncausal_semantics():
    parent = _contribution_parent()
    task = _task(ResearchTaskKind.CONTRIBUTION, parent, METRIC, DIM)

    result = DerivedEvidenceService().contribution(
        task=task,
        parent=parent,
        args=ContributionDerivedArgs(
            metric_handle=METRIC,
            dimension_handle=DIM,
            additivity_class="ADDITIVE",
            additivity_provenance_ref="mdl:Sales.revenue:additive",
        ),
    )

    assert result.verified is True
    assert result.transformation == "CONTRIBUTION"
    assert result.parent_query_contract_refs == ("QC_CUR", "QC_REF")
    assert result.query_contract_refs == ("QC_CUR", "QC_REF")
    assert result.payload["segment_count"] == 3
    assert result.payload["trimmed_segment_count"] == 0
    assert result.payload["trimmed_mass_share"] == 0.0
    assert result.payload["claim_semantics"] == "observed_change_decomposition_noncausal"
    assert all("cause" not in key.lower() for key in result.payload)


def test_contribution_missing_required_column_rejects_instead_of_zero_filling():
    parent = _contribution_parent(missing_reference_metric=True)
    task = _task(ResearchTaskKind.CONTRIBUTION, parent, METRIC, DIM)

    with pytest.raises(DerivedEvidenceError, match="missing required"):
        DerivedEvidenceService().contribution(
            task=task,
            parent=parent,
            args=ContributionDerivedArgs(
                metric_handle=METRIC,
                dimension_handle=DIM,
                additivity_provenance_ref="mdl:additive",
            ),
        )


def test_contribution_non_additive_contract_cannot_be_constructed():
    with pytest.raises(ValidationError):
        ContributionDerivedArgs(
            metric_handle=METRIC,
            dimension_handle=DIM,
            additivity_class="SEMI_ADDITIVE",
            additivity_provenance_ref="mdl:semi",
        )


def test_contribution_unaligned_segment_sets_reject():
    parent = _contribution_parent()
    executions = list(parent.payload["executions"])
    executions[1] = {
        **executions[1],
        "rows": (
            {DIM: "A", METRIC: 80.0},
            {DIM: "B", METRIC: 50.0},
            {DIM: "D", METRIC: 20.0},
        ),
    }
    parent = parent.model_copy(
        update={"payload": {"query_count": 2, "executions": tuple(executions)}}
    )
    task = _task(ResearchTaskKind.CONTRIBUTION, parent, METRIC, DIM)

    with pytest.raises(DerivedEvidenceError, match="not aligned"):
        DerivedEvidenceService().contribution(
            task=task,
            parent=parent,
            args=ContributionDerivedArgs(
                metric_handle=METRIC,
                dimension_handle=DIM,
                additivity_provenance_ref="mdl:additive",
            ),
        )


def test_peer_compare_governed_peer_set_produces_descriptive_derived_evidence():
    parent = _peer_parent()
    task = _task(ResearchTaskKind.PEER_COMPARE, parent, METRIC, DIM)

    result = DerivedEvidenceService().peer_compare(
        task=task,
        parent=parent,
        args=PeerCompareDerivedArgs(
            metric_handle=METRIC,
            dimension_handle=DIM,
            target_value="TARGET",
            target_provenance_ref="accepted-filter:target",
            peer_group_provenance_ref="accepted-dimension:peer-group",
        ),
    )

    assert result.verified is True
    assert result.transformation == "PEER_COMPARE"
    assert result.payload["comparison"]["hedef_deger"] == 80.0
    assert result.payload["comparison"]["akran_sayisi"] == 2
    assert result.payload["claim_semantics"] == "descriptive_peer_comparison_noncausal"
    assert "does not discover peers" in result.limitations[0]


def test_peer_compare_target_absent_has_no_claim():
    parent = _peer_parent()
    task = _task(ResearchTaskKind.PEER_COMPARE, parent, METRIC, DIM)

    with pytest.raises(DerivedEvidenceError, match="target plus at least two"):
        DerivedEvidenceService().peer_compare(
            task=task,
            parent=parent,
            args=PeerCompareDerivedArgs(
                metric_handle=METRIC,
                dimension_handle=DIM,
                target_value="MISSING",
                target_provenance_ref="accepted-filter:target",
                peer_group_provenance_ref="accepted-dimension:peer-group",
            ),
        )


def test_peer_compare_less_than_two_peers_has_no_claim():
    parent = _peer_parent(
        rows=(
            {DIM: "TARGET", METRIC: 80.0},
            {DIM: "ONLY_PEER", METRIC: 100.0},
        )
    )
    task = _task(ResearchTaskKind.PEER_COMPARE, parent, METRIC, DIM)

    with pytest.raises(DerivedEvidenceError, match="at least two"):
        DerivedEvidenceService().peer_compare(
            task=task,
            parent=parent,
            args=PeerCompareDerivedArgs(
                metric_handle=METRIC,
                dimension_handle=DIM,
                target_value="TARGET",
                target_provenance_ref="accepted-filter:target",
                peer_group_provenance_ref="accepted-dimension:peer-group",
            ),
        )


def test_peer_compare_requires_governed_provenance_fields():
    with pytest.raises(ValidationError):
        PeerCompareDerivedArgs(
            metric_handle=METRIC,
            dimension_handle=DIM,
            target_value="TARGET",
            target_provenance_ref="",
            peer_group_provenance_ref="",
        )


def test_derived_task_must_declare_semantic_inputs():
    parent = _peer_parent()
    task = _task(ResearchTaskKind.PEER_COMPARE, parent, METRIC)

    with pytest.raises(DerivedEvidenceError, match="did not declare"):
        DerivedEvidenceService().peer_compare(
            task=task,
            parent=parent,
            args=PeerCompareDerivedArgs(
                metric_handle=METRIC,
                dimension_handle=DIM,
                target_value="TARGET",
                target_provenance_ref="accepted-filter:target",
                peer_group_provenance_ref="accepted-dimension:peer-group",
            ),
        )
