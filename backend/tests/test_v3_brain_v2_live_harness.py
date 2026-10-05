from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from uuid import UUID

from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus
from lab.metabase.brain_v2 import phase1_live
from lab.metabase.brain_v2.final_probes import FINAL_READINESS_PANEL
from lab.metabase.brain_v2.phase1_live import (
    _contextual_report_mechanical,
    _apply_orchestration_efficiency,
    _durable_resume_identity_checks,
    _mechanical,
    _native_occurrence_projection,
    _safety_unsupported_mechanical,
    _require_locked_engine_runtime,
)


def _link(*, fingerprint: str = "a" * 64, ordinal: int = 1):
    digit = str(ordinal)
    return SimpleNamespace(
        id=UUID(f"00000000-0000-4000-8000-{ordinal:012d}"),
        obligation_id="g_root",
        status="VERIFIED",
        native_query_id=f"query-{ordinal}",
        native_query_fingerprint=fingerprint,
        receipt_id="dqr_" + digit * 24,
        evidence_id="evi_" + str(ordinal + 1) * 24,
        execution_kind="P14_BASE",
    )


def _grounded_hypothesis():
    return SimpleNamespace(
        groundings=(
            SimpleNamespace(
                source_kind="P14_EVIDENCE",
            ),
        ),
    )


def test_live_receipt_uses_canonical_native_query_fingerprint() -> None:
    projected = _native_occurrence_projection((_link(),))

    assert projected == [
        {
            "execution_link_id": "00000000-0000-4000-8000-000000000001",
            "obligation_id": "g_root",
            "status": "VERIFIED",
            "native_query_id": "query-1",
            "query_fingerprint": "a" * 64,
            "receipt_id": "dqr_" + "1" * 24,
            "evidence_id": "evi_" + "2" * 24,
            "execution_kind": "P14_BASE",
        }
    ]


def test_durable_resume_identity_gate_accepts_same_executed_occurrence() -> None:
    attempts = [
        {
            "before_occurrences": [
                {
                    "execution_link_id": "link-1",
                    "status": "EXECUTED",
                    "native_query_id": "query-1",
                    "query_fingerprint": "a" * 64,
                }
            ],
            "after_occurrences": [
                {
                    "execution_link_id": "link-1",
                    "status": "VERIFIED",
                    "native_query_id": "query-1",
                    "query_fingerprint": "a" * 64,
                },
                {
                    "execution_link_id": "link-child",
                    "status": "VERIFIED",
                    "native_query_id": "query-child",
                    "query_fingerprint": "b" * 64,
                },
            ],
            "provider_delta_by_owner": {
                "research_intake": 0,
                "metabase": 0,
                "p17_manager": 0,
                "p18_manager": 0,
                "p19_manager": 0,
            },
        }
    ]

    result = _durable_resume_identity_checks(attempts)

    assert result == {
        "durable_resume_identity_preserved": True,
        "durable_resume_provider_replay_zero": True,
    }


def test_durable_resume_identity_gate_rejects_parent_replay() -> None:
    attempts = [
        {
            "before_occurrences": [
                {
                    "execution_link_id": "link-1",
                    "status": "EXECUTED",
                    "native_query_id": "query-1",
                    "query_fingerprint": "a" * 64,
                }
            ],
            "after_occurrences": [
                {
                    "execution_link_id": "link-2",
                    "status": "VERIFIED",
                    "native_query_id": "query-2",
                    "query_fingerprint": "c" * 64,
                }
            ],
            "provider_delta_by_owner": {
                "research_intake": 0,
                "metabase": 1,
            },
        }
    ]

    result = _durable_resume_identity_checks(attempts)

    assert result["durable_resume_identity_preserved"] is False
    assert result["durable_resume_provider_replay_zero"] is False



def test_one_pass_mechanical_gate_reads_canonical_native_fingerprint() -> None:
    state = BrainGraphState(
        thread_id="live:test",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "1" * 24,
        accepted_brief_ref="rb_fixture",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        hypothesis_ids=("p19h_" + "3" * 24, "p19h_" + "4" * 24),
        latest_p19_assessment_ref="p19a_" + "5" * 24,
        open_requirement_ids=("d_report",),
        report_requirement_ids=("d_report",),
        report_ref="p20r_" + "6" * 24,
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="REPORT",
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 1,
            "p17_manager": 0,
            "p19_manager": 1,
        },
        "actual_provider_request_count": 3,
        "prompt_tokens": 1000,
        "blocked_request_count": 0,
    }
    p17_snapshot = SimpleNamespace(
        investigation=SimpleNamespace(nodes=()),
        claims=(),
    )
    p19_snapshot = SimpleNamespace(
        hypotheses=(_grounded_hypothesis(), _grounded_hypothesis()),
    )

    result = _mechanical(
        probe_id="R_LIVE_1_ONE_PASS",
        state=state,
        provider=provider,
        links=(_link(),),
        p17_snapshot=p17_snapshot,
        p19_snapshot=p19_snapshot,
        report_doc=object(),
    )

    assert result["mechanical_green"] is True
    assert result["duplicate_native_execution_zero"] is True
    assert result["native_acquisitions"] == 1




def test_one_pass_without_presentation_requirement_does_not_require_report() -> None:
    state = BrainGraphState(
        thread_id="live:one-pass-no-report",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "2" * 24,
        accepted_brief_ref="rb_no_report",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        hypothesis_ids=("p19h_" + "3" * 24, "p19h_" + "4" * 24),
        latest_p19_assessment_ref="p19a_" + "5" * 24,
        report_ref=None,
        report_requirement_ids=(),
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="COMPLETE",
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 1,
            "p17_manager": 0,
            "p19_manager": 1,
        },
        "actual_provider_request_count": 3,
        "prompt_tokens": 1000,
        "blocked_request_count": 0,
    }
    result = _mechanical(
        probe_id="R_LIVE_1_ONE_PASS",
        state=state,
        provider=provider,
        links=(_link(),),
        p17_snapshot=SimpleNamespace(
            investigation=SimpleNamespace(nodes=()),
            claims=(),
        ),
        p19_snapshot=SimpleNamespace(
            hypotheses=(_grounded_hypothesis(), _grounded_hypothesis()),
        ),
        report_doc=None,
    )

    assert result["presentation_required"] is False
    assert result["report_exists"] is False
    assert result["report_contract_coherent"] is True
    assert result["mechanical_green"] is True


def test_discovery_mechanical_gate_accepts_governed_candidate_path() -> None:
    state = BrainGraphState(
        thread_id="live:discovery-candidates",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "7" * 24,
        accepted_brief_ref="rb_discovery",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        hypothesis_ids=("p19h_" + "3" * 24, "p19h_" + "4" * 24),
        candidate_semantic_ids=("metric.a", "metric.b"),
        latest_p19_assessment_ref="p19a_" + "5" * 24,
        open_requirement_ids=("d_report",),
        report_requirement_ids=("d_report",),
        report_ref="p20r_" + "6" * 24,
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="REPORT",
        discovery_required=False,
        discovery_turns=0,
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 2,
            "p17_manager": 0,
            "p19_manager": 1,
        },
        "actual_provider_request_count": 4,
        "prompt_tokens": 2000,
        "blocked_request_count": 0,
    }
    p17_snapshot = SimpleNamespace(
        investigation=SimpleNamespace(nodes=()),
        claims=(),
        terminal_stop_reason=None,
    )
    p19_snapshot = SimpleNamespace(
        hypotheses=(_grounded_hypothesis(), _grounded_hypothesis()),
    )

    result = _mechanical(
        probe_id="R_LIVE_3_DISCOVERY",
        state=state,
        provider=provider,
        links=(_link(),),
        p17_snapshot=p17_snapshot,
        p19_snapshot=p19_snapshot,
        report_doc=object(),
    )

    assert result["mechanical_green"] is True
    assert result["discovery_candidate_path"] is True
    assert result["discovery_honest_stop"] is False
    assert result["p17_provider_requests"] == 0
    assert result["candidate_projection_coherent"] is True
    assert result["p19_provider_requests"] == 1


def test_discovery_mechanical_gate_accepts_typed_honest_insufficient_stop() -> None:
    state = BrainGraphState(
        thread_id="live:discovery-stop",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "8" * 24,
        accepted_brief_ref="rb_discovery",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        candidate_semantic_ids=(),
        hypothesis_ids=(),
        workflow_status=BrainWorkflowStatus.INCONCLUSIVE,
        last_completed_node="HONEST_STOP",
        discovery_required=False,
        discovery_turns=0,
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 2,
            "p17_manager": 0,
            "p19_manager": 0,
        },
        "actual_provider_request_count": 3,
        "prompt_tokens": 1500,
        "blocked_request_count": 0,
    }
    p17_snapshot = SimpleNamespace(
        investigation=SimpleNamespace(nodes=()),
        claims=(),
        terminal_stop_reason=None,
    )
    p19_snapshot = SimpleNamespace(hypotheses=())

    result = _mechanical(
        probe_id="R_LIVE_3_DISCOVERY",
        state=state,
        provider=provider,
        links=(_link(),),
        p17_snapshot=p17_snapshot,
        p19_snapshot=p19_snapshot,
        report_doc=None,
    )

    assert result["mechanical_green"] is True
    assert result["discovery_candidate_path"] is False
    assert result["discovery_honest_stop"] is True
    assert result["p17_provider_requests"] == 0
    assert result["p19_assessment_exists"] is False
    assert result["report_exists"] is False


def test_discovery_mechanical_gate_accepts_singleton_after_p19_honest_stop() -> None:
    state = BrainGraphState(
        thread_id="live:discovery-singleton-stop",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "9" * 24,
        accepted_brief_ref="rb_discovery",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        candidate_semantic_ids=("metric.a",),
        hypothesis_ids=("p19h_" + "3" * 24,),
        latest_p19_assessment_ref="p19a_" + "5" * 24,
        workflow_status=BrainWorkflowStatus.INCONCLUSIVE,
        last_completed_node="HONEST_STOP",
        discovery_required=False,
        discovery_turns=0,
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 2,
            "p17_manager": 0,
            "p19_manager": 1,
        },
        "actual_provider_request_count": 4,
        "prompt_tokens": 1500,
        "blocked_request_count": 0,
    }
    p17_snapshot = SimpleNamespace(
        investigation=SimpleNamespace(nodes=()),
        claims=(),
        terminal_stop_reason=None,
    )
    p19_snapshot = SimpleNamespace(
        hypotheses=(_grounded_hypothesis(),),
    )

    result = _mechanical(
        probe_id="R_LIVE_3_DISCOVERY",
        state=state,
        provider=provider,
        links=(_link(),),
        p17_snapshot=p17_snapshot,
        p19_snapshot=p19_snapshot,
        report_doc=None,
    )

    assert result["mechanical_green"] is True
    assert result["discovery_candidate_path"] is False
    assert result["discovery_honest_stop"] is True
    assert result["hypothesis_count"] == 1
    assert result["candidate_projection_coherent"] is True
    assert result["evidence_grounded_hypothesis_count"] == 1
    assert result["p19_assessment_exists"] is True
    assert result["p19_provider_requests"] == 1
    assert result["report_exists"] is False


def test_scope_resume_mechanical_gate_requires_new_scope_and_disjoint_evidence() -> None:
    state = BrainGraphState(
        thread_id="live:scope",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "9" * 24,
        accepted_brief_ref="rb_scope_v2",
        scope_version_id="scope_v2",
        evidence_revision=1,
        evidence_ids=("evi_" + "9" * 24,),
        hypothesis_ids=("p19h_" + "3" * 24, "p19h_" + "4" * 24),
        latest_p19_assessment_ref="p19a_" + "5" * 24,
        open_requirement_ids=("d_report",),
        report_requirement_ids=("d_report",),
        report_ref="p20r_" + "6" * 24,
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="REPORT",
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 2,
            "metabase": 6,
            "p17_manager": 0,
            "p19_manager": 2,
        },
        "actual_provider_request_count": 10,
        "prompt_tokens": 1000,
        "blocked_request_count": 0,
    }
    p17_snapshot = SimpleNamespace(
        investigation=SimpleNamespace(nodes=()),
        claims=(),
    )
    p19_snapshot = SimpleNamespace(
        hypotheses=(_grounded_hypothesis(), _grounded_hypothesis()),
    )
    scope_resume = {
        "first_scope_version_id": "scope_v1",
        "second_scope_version_id": "scope_v2",
        "same_lineage": True,
        "prior_historical": True,
        "evidence_disjoint": True,
        "checkpoint_resume": True,
    }

    result = _mechanical(
        probe_id="R_LIVE_4_SCOPE_RESUME",
        state=state,
        provider=provider,
        links=(
            _link(fingerprint="a" * 64, ordinal=1),
            _link(fingerprint="b" * 64, ordinal=2),
        ),
        p17_snapshot=p17_snapshot,
        p19_snapshot=p19_snapshot,
        report_doc=object(),
        scope_resume=scope_resume,
    )

    assert result["mechanical_green"] is True
    assert result["native_acquisitions"] == 2
    assert result["intake_provider_requests"] == 2
    assert result["duplicate_native_execution_zero"] is True


def test_scope_resume_without_presentation_requirement_does_not_require_report() -> None:
    state = BrainGraphState(
        thread_id="live:scope-no-report",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "8" * 24,
        accepted_brief_ref="rb_scope_v2_no_report",
        scope_version_id="scope_v2",
        evidence_revision=2,
        evidence_ids=("evi_" + "8" * 24,),
        hypothesis_ids=("p19h_" + "3" * 24, "p19h_" + "4" * 24),
        latest_p19_assessment_ref="p19a_" + "5" * 24,
        report_ref=None,
        report_requirement_ids=(),
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="COMPLETE",
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 2,
            "metabase": 6,
            "p17_manager": 0,
            "p19_manager": 2,
        },
        "actual_provider_request_count": 10,
        "prompt_tokens": 1000,
        "blocked_request_count": 0,
    }
    scope_resume = {
        "first_scope_version_id": "scope_v1",
        "second_scope_version_id": "scope_v2",
        "same_lineage": True,
        "prior_historical": True,
        "evidence_disjoint": True,
        "checkpoint_resume": True,
    }
    result = _mechanical(
        probe_id="R_LIVE_4_SCOPE_RESUME",
        state=state,
        provider=provider,
        links=(
            _link(fingerprint="a" * 64, ordinal=1),
            _link(fingerprint="b" * 64, ordinal=2),
        ),
        p17_snapshot=SimpleNamespace(
            investigation=SimpleNamespace(nodes=()),
            claims=(),
        ),
        p19_snapshot=SimpleNamespace(
            hypotheses=(_grounded_hypothesis(), _grounded_hypothesis()),
        ),
        report_doc=None,
        scope_resume=scope_resume,
    )

    assert result["report_exists"] is False
    assert result["mechanical_green"] is True


def test_live_runtime_guard_uses_certified_lock_instead_of_release_literal(
    tmp_path,
    monkeypatch,
) -> None:
    lock = {
        "engine_sha": "a" * 40,
        "upstream_sha": "b" * 40,
        "runtime_tag": "v0.63.18-dima.99",
        "registry_digest": "sha256:" + "c" * 64,
        "build_identity": "github-actions:123:" + "a" * 40,
    }
    lock_path = tmp_path / "engine_runtime_lock.json"
    lock_path.write_text(json.dumps(lock), encoding="utf-8")
    monkeypatch.setattr(phase1_live, "ENGINE_RUNTIME_LOCK", lock_path)

    args = SimpleNamespace(
        engine_sha=lock["engine_sha"],
        upstream_sha=lock["upstream_sha"],
        runtime_tag=lock["runtime_tag"],
        runtime_image_digest=lock["registry_digest"],
        build_identity=lock["build_identity"],
        image_identity=lock["registry_digest"],
    )

    _require_locked_engine_runtime(args)

    args.engine_sha = "d" * 40
    with pytest.raises(RuntimeError, match="certified runtime lock"):
        _require_locked_engine_runtime(args)


def test_exception_projection_includes_first_wrong_boundary_identity():
    from app.v3.brain_v2.owner_adapter import BrainV2OwnerError
    from lab.metabase.brain_v2.phase1_live import _exception

    exc = BrainV2OwnerError(
        "P20_TEST_RED",
        "g_relationship",
        last_valid_boundary="dima.completion.evaluate",
        first_invalid_boundary="dima.p20.report",
        scope_fingerprint="a" * 64,
        material_fingerprint="b" * 64,
        requirement_id="g_relationship",
        material_group_id="mg_" + "1" * 24,
        expected_owner="P20",
        observed_owner="P20",
    )
    receipt = _exception(exc)

    assert receipt["last_valid_boundary"] == "dima.completion.evaluate"
    assert receipt["first_invalid_boundary"] == "dima.p20.report"
    assert receipt["scope_fingerprint"] == "a" * 64
    assert receipt["material_fingerprint"] == "b" * 64
    assert receipt["requirement_id"] == "g_relationship"
    assert receipt["material_group_id"] == "mg_" + "1" * 24
    assert receipt["expected_owner"] == "P20"
    assert receipt["observed_owner"] == "P20"


@pytest.mark.parametrize(
    ("probe_id", "native_count"),
    (
        ("DIRECT_ANALYTICS_V1", 1),
        ("TEMPORAL_COMPARISON_V1", 1),
        ("CHANGE_DEPENDENT_DRILLDOWN_V1", 2),
    ),
)
def test_basic_readiness_mechanical_gate_needs_governed_evidence_without_research_managers(
    probe_id,
    native_count,
) -> None:
    state = BrainGraphState(
        thread_id=f"live:{probe_id}",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "1" * 24,
        accepted_brief_ref="rb_basic",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="COMPLETE",
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": native_count,
            "p17_manager": 0,
            "p19_manager": 0,
        },
        "actual_provider_request_count": 1 + native_count,
        "prompt_tokens": 1000,
        "blocked_request_count": 0,
    }
    links = tuple(
        _link(fingerprint=(chr(96 + ordinal) * 64), ordinal=ordinal)
        for ordinal in range(1, native_count + 1)
    )

    result = _mechanical(
        probe_id=probe_id,
        state=state,
        provider=provider,
        links=links,
        p17_snapshot=SimpleNamespace(
            investigation=SimpleNamespace(nodes=()),
            claims=(),
        ),
        p19_snapshot=None,
        report_doc=None,
    )

    assert result["mechanical_green"] is True
    assert result["p17_provider_requests"] == 0
    assert result["p19_provider_requests"] == 0
    assert result["duplicate_native_execution_zero"] is True
    assert "scope_version_advanced" not in result["checks"]
    assert "two_intake_calls" not in result["checks"]
    assert "two_native_acquisitions" not in result["checks"]


def test_final_readiness_panel_matches_supervisor_nine_capabilities() -> None:
    assert FINAL_READINESS_PANEL == (
        "DIRECT_ANALYTICS_V1",
        "TEMPORAL_COMPARISON_V1",
        "CHANGE_DEPENDENT_DRILLDOWN_V1",
        "R_LIVE_2_ADAPTIVE",
        "RELATIONSHIP_REPORT_PHASE2_V1",
        "R_LIVE_4_SCOPE_RESUME",
        "CONTEXTUAL_REPORT_V1",
        "MULTI_INTENT_PHASE2_V1",
        "SAFETY_UNSUPPORTED_V1",
    )
    assert len(FINAL_READINESS_PANEL) == len(set(FINAL_READINESS_PANEL)) == 9


def test_orchestration_efficiency_slo_is_non_blocking() -> None:
    from lab.metabase.brain_v2.live_support import (
        ORCHESTRATION_EFFICIENCY_SLO_UNITS,
        OrchestrationEfficiencyTracker,
    )

    tracker = OrchestrationEfficiencyTracker()
    for _ in range(ORCHESTRATION_EFFICIENCY_SLO_UNITS + 5):
        tracker.consume("metabot")

    assert tracker.used == 17
    assert tracker.by_owner == {"metabot": 17}
    assert tracker.slo_met is False

    report = {
        "mechanical": {
            "checks": {"correctness": True},
            "efficiency_checks": {"provider_slo": True},
            "mechanical_green": True,
            "efficiency_green": True,
        }
    }
    _apply_orchestration_efficiency(report, tracker)

    assert report["mechanical"]["mechanical_green"] is True
    assert report["mechanical"]["efficiency_green"] is False
    assert report["mechanical"]["efficiency_checks"][
        "orchestration_units_slo"
    ] is False
    assert report["orchestration_efficiency"] == {
        "slo_units": 12,
        "used": 17,
        "by_owner": {"metabot": 17},
        "slo_met": False,
    }


def test_exception_artifact_helper_preserves_provider_receipt_shape(tmp_path) -> None:
    from lab.metabase.brain_v2.phase1_live import _try_provider_receipt

    receipt = {
        "schema_version": "dima_openrouter_counting_proxy_v1",
        "actual_provider_request_count": 7,
        "blocked_request_count": 0,
        "provider_requests_by_source": {"metabase": 6, "research_intake": 1},
    }
    path = tmp_path / "provider.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")

    assert _try_provider_receipt(path) == receipt

    missing = _try_provider_receipt(tmp_path / "missing.json")
    assert missing["receipt_available"] is False
    assert "receipt_error" in missing


def test_quality_mechanical_does_not_fail_only_for_efficiency_debt() -> None:
    state = BrainGraphState(
        thread_id="live:efficiency-separation",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "1" * 24,
        accepted_brief_ref="rb_basic",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="COMPLETE",
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 7,
            "p17_manager": 0,
            "p19_manager": 0,
        },
        "actual_provider_request_count": 8,
        "prompt_tokens": 1000,
        "blocked_request_count": 0,
    }
    result = _mechanical(
        probe_id="DIRECT_ANALYTICS_V1",
        state=state,
        provider=provider,
        links=(_link(),),
        p17_snapshot=SimpleNamespace(
            investigation=SimpleNamespace(nodes=()),
            claims=(),
        ),
        p19_snapshot=None,
        report_doc=None,
    )
    assert result["mechanical_green"] is True
    assert result["efficiency_green"] is False
    assert result["efficiency_checks"]["provider_slo"] is False
    assert "provider_slo" not in result["checks"]


def test_contextual_report_mechanical_requires_zero_analytical_report_delta() -> None:
    first = BrainGraphState(
        thread_id="live:contextual-report",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        research_session_id="rs_" + "1" * 24,
        accepted_brief_ref="rb_contextual",
        scope_version_id="scope_v1",
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        open_requirement_ids=("g_direct",),
        direct_requirement_ids=("g_direct",),
        terminal_requirement_ids=("g_direct",),
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="COMPLETE",
    )
    final = first.model_copy(
        update={
            "open_requirement_ids": ("g_direct", "d_report_" + "3" * 24),
            "report_requirement_ids": ("d_report_" + "3" * 24,),
            "terminal_requirement_ids": (
                "g_direct",
                "d_report_" + "3" * 24,
            ),
            "presentation_revision": 1,
            "report_ref": "p20r_" + "4" * 24,
            "last_completed_node": "COMPLETE",
        }
    )
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 1,
            "p17_manager": 0,
            "p18_manager": 0,
            "p19_manager": 0,
        },
        "actual_provider_request_count": 2,
        "blocked_request_count": 0,
    }
    result = _contextual_report_mechanical(
        first_state=first,
        state=final,
        provider=provider,
        links=(_link(),),
        report_doc=object(),
        report_current=True,
        first_native_count=1,
        budget_before_report={
            "research_intake": 1,
            "metabase": 1,
        },
        budget_after={
            "research_intake": 1,
            "metabase": 1,
        },
        checkpoint_roundtrip=True,
        stale_evidence_count=0,
        cross_tenant_violation_count=0,
        causal_overclaim_count=0,
    )
    assert result["mechanical_green"] is True
    assert result["report_turn_native_delta"] == 0
    assert all(value == 0 for value in result["report_turn_owner_delta"].values())


def test_safety_unsupported_mechanical_accepts_typed_fail_closed_without_native() -> None:
    provider = {
        "provider_requests_by_source": {
            "research_intake": 1,
            "metabase": 0,
            "p17_manager": 0,
            "p18_manager": 0,
            "p19_manager": 0,
        },
        "actual_provider_request_count": 1,
        "blocked_request_count": 0,
    }
    result = _safety_unsupported_mechanical(
        terminal_code="BRAIN_V2_INTAKE_UNSUPPORTED",
        provider=provider,
        native_http_requests=(),
        agent_api_request_count=0,
    )
    assert result["mechanical_green"] is True
    assert result["efficiency_green"] is True

    unsafe = _safety_unsupported_mechanical(
        terminal_code="BRAIN_V2_INTAKE_UNSUPPORTED",
        provider={
            **provider,
            "provider_requests_by_source": {
                **provider["provider_requests_by_source"],
                "metabase": 1,
            },
            "actual_provider_request_count": 2,
        },
        native_http_requests=(("POST", "/api/dataset"),),
        agent_api_request_count=0,
    )
    assert unsafe["mechanical_green"] is False
