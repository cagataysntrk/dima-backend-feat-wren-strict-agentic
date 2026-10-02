from types import SimpleNamespace

from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus
from lab.metabase.brain_v2.final_mechanical import (
    MULTI_INTENT,
    RELATIONSHIP_REPORT,
    phase2_mechanical,
)


def _state(*, report=True, multi=False):
    direct = ("rank",) if multi else ()
    reports = ("report",) if report else ()
    open_ids = (*direct, "rel", *reports)
    terminal = (*direct, "rel", *reports)
    return BrainGraphState(
        thread_id="phase2",
        tenant_binding="id:t",
        principal_ref="u",
        research_session_id="rs_" + "1" * 24,
        accepted_brief_ref="brief",
        scope_version_id="scope_v1",
        open_requirement_ids=open_ids,
        material_requirement_ids=(*direct, "rel"),
        material_group_ids=("mg_" + "a" * 24,),
        completed_material_group_ids=("mg_" + "a" * 24,),
        terminal_requirement_ids=terminal,
        direct_requirement_ids=direct,
        relationship_requirement_ids=("rel",),
        report_requirement_ids=reports,
        evidence_revision=1,
        evidence_ids=("evi_" + "2" * 24,),
        p18_requirement_ids=("rel",),
        p18_result_refs=("p18r_" + "7" * 24,),
        p18_claim_refs=("clm_" + "3" * 24,),
        p18_policy_use_refs=("bru_" + "4" * 24,),
        completion_revision=2 if report else 1,
        presentation_revision=1 if report else 0,
        report_ref=("p20r_" + "5" * 24 if report else None),
        workflow_status=BrainWorkflowStatus.COMPLETE,
        last_completed_node="COMPLETE",
    )


def _use():
    return SimpleNamespace(
        resolution_status="NOT_REQUIRED",
        policy_id=None,
    )


def _native():
    return ({
        "status": "VERIFIED",
        "query_fingerprint": "f" * 64,
    },)


def test_relationship_report_requires_zero_second_turn_reanalysis():
    first = _state(report=False)
    final = _state(report=True)
    result = phase2_mechanical(
        probe_id=RELATIONSHIP_REPORT,
        state=final,
        first_state=first,
        native_occurrences=_native(),
        first_native_count=1,
        p18_uses=(_use(),),
        report_present=True,
        budget_before_report={
            "research_intake": 1,
            "metabase": 1,
            "p17_manager": 1,
            "p19_manager": 0,
        },
        budget_after={
            "research_intake": 1,
            "metabase": 1,
            "p17_manager": 1,
            "p19_manager": 0,
        },
        same_research_session=True,
        same_scope_version=True,
        checkpoint_roundtrip=True,
        legacy_composer_calls=0,
        agent_api_request_count=0,
        stale_evidence_count=0,
        cross_tenant_violation_count=0,
        causal_overclaim_count=0,
    )
    assert result["mechanical_green"] is True
    assert result["report_turn_native_delta"] == 0
    assert set(result["report_turn_budget_delta"].values()) == {0}


def test_relationship_report_rejects_hidden_report_turn_analytics():
    first = _state(report=False)
    final = _state(report=True)
    result = phase2_mechanical(
        probe_id=RELATIONSHIP_REPORT,
        state=final,
        first_state=first,
        native_occurrences=(
            *_native(),
            {"status": "VERIFIED", "query_fingerprint": "e" * 64},
        ),
        first_native_count=1,
        p18_uses=(_use(),),
        report_present=True,
        budget_before_report={"metabase": 1},
        budget_after={"metabase": 2},
        same_research_session=True,
        same_scope_version=True,
        checkpoint_roundtrip=True,
        legacy_composer_calls=0,
        agent_api_request_count=0,
        stale_evidence_count=0,
        cross_tenant_violation_count=0,
        causal_overclaim_count=0,
    )
    assert result["mechanical_green"] is False
    assert result["checks"]["report_only_native_delta_zero"] is False


def test_multi_intent_requires_one_shared_material_and_full_terminal_accounting():
    state = _state(report=True, multi=True)
    result = phase2_mechanical(
        probe_id=MULTI_INTENT,
        state=state,
        first_state=None,
        native_occurrences=_native(),
        first_native_count=None,
        p18_uses=(_use(),),
        report_present=True,
        budget_before_report=None,
        budget_after={
            "research_intake": 1,
            "metabase": 1,
            "p17_manager": 1,
            "p19_manager": 0,
        },
        same_research_session=True,
        same_scope_version=True,
        checkpoint_roundtrip=True,
        legacy_composer_calls=0,
        agent_api_request_count=0,
        stale_evidence_count=0,
        cross_tenant_violation_count=0,
        causal_overclaim_count=0,
    )
    assert result["mechanical_green"] is True
    assert result["checks"]["one_shared_material_group"] is True
    assert result["checks"]["one_native_acquisition"] is True


def test_phase2_mechanical_rejects_agent_api_or_legacy_runtime_usage():
    state = _state(report=True, multi=True)
    result = phase2_mechanical(
        probe_id=MULTI_INTENT,
        state=state,
        first_state=None,
        native_occurrences=_native(),
        first_native_count=None,
        p18_uses=(_use(),),
        report_present=True,
        budget_before_report=None,
        budget_after={"metabase": 1},
        same_research_session=True,
        same_scope_version=True,
        checkpoint_roundtrip=True,
        legacy_composer_calls=1,
        agent_api_request_count=1,
        stale_evidence_count=0,
        cross_tenant_violation_count=0,
        causal_overclaim_count=0,
    )
    assert result["mechanical_green"] is False
    assert result["checks"]["legacy_calls_zero"] is False
    assert result["checks"]["agent_api_calls_zero"] is False


def test_phase2_mechanical_rejects_stale_cross_tenant_or_causal_drift():
    state = _state(report=True, multi=True)
    result = phase2_mechanical(
        probe_id=MULTI_INTENT,
        state=state,
        first_state=None,
        native_occurrences=_native(),
        first_native_count=None,
        p18_uses=(_use(),),
        report_present=True,
        budget_before_report=None,
        budget_after={"metabase": 1},
        same_research_session=True,
        same_scope_version=True,
        checkpoint_roundtrip=True,
        legacy_composer_calls=0,
        agent_api_request_count=0,
        stale_evidence_count=1,
        cross_tenant_violation_count=1,
        causal_overclaim_count=1,
    )
    assert result["mechanical_green"] is False
    assert result["checks"]["stale_evidence_zero"] is False
    assert result["checks"]["cross_tenant_zero"] is False
    assert result["checks"]["causal_overclaim_zero"] is False
