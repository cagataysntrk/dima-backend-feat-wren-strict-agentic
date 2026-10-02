from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from uuid import UUID

from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus
from lab.metabase.brain_v2 import phase1_live
from lab.metabase.brain_v2.phase1_live import (
    _mechanical,
    _native_occurrence_projection,
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
