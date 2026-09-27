from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.v3.business_relationship_policy import (
    RelationshipPolicyDecision,
    RelationshipPolicyResolutionStatus,
)
from app.v3.business_relationship_v1 import (
    RelationshipAnalyticalKind,
    RelationshipLayerState,
    project_relationship_result,
)
from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.product.execution_mode import (
    ProductExecutionMode,
    classify_execution_mode,
)
from app.v3.research_contracts import (
    ComparisonSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)


def sem(cid, kind, name):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=kind,
        canonical_name=name,
        cube_names=("operations",),
    )


M1 = sem("metric.one", SemanticTargetKind.METRIC, "Metric One")
M2 = sem("metric.two", SemanticTargetKind.METRIC, "Metric Two")
D1 = sem("dimension.one", SemanticTargetKind.DIMENSION, "Dimension One")


def question(goal_id, kind, *, subjects=(M1,), related=(D1,), comparisons=()):
    return ResearchQuestion(
        goal_id=goal_id,
        kind=kind,
        source_text=f"{kind.value} request",
        subject_refs=tuple(subjects),
        related_refs=tuple(related),
        comparisons=tuple(comparisons),
        status=ResearchGoalStatus.RESOLVED,
    )


def brief(*questions):
    refs = {}
    for item in questions:
        for ref in (*item.subject_refs, *item.related_refs):
            refs[ref.candidate_id] = ref
    return ResearchBrief(
        brief_id="rb-b2",
        objective="B2 routing proof",
        scope=ResearchScope(semantic_refs=tuple(refs.values())),
        questions=tuple(questions),
        must_requirement_ids=tuple(item.goal_id for item in questions),
        context_version="ctx-b2",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def link(index, relation):
    return SimpleNamespace(
        evidence_id="evi_" + f"{index:024x}",
        receipt_id="dqr_" + f"{index:024x}",
        relation=relation,
    )


def relationship_claim(*, epistemic="SUPPORTED", kind="ASSOCIATION"):
    return SimpleNamespace(
        claim_id="clm_" + "1" * 24,
        research_session_id="rs_" + "2" * 24,
        obligation_id="g_relationship",
        proposition={"relationship_kind": kind},
        epistemic_state=SimpleNamespace(value=epistemic),
        limitations=("ASSOCIATION_ONLY",),
        evidence_links=(
            link(1, "SUPPORTS"),
            link(2, "CHALLENGES"),
            link(3, "CONTEXTUALIZES"),
        ),
    )


def policy_decision(*, satisfied=True):
    return RelationshipPolicyDecision(
        required=True,
        eligible=satisfied,
        resolution_status=(
            RelationshipPolicyResolutionStatus.SATISFIED
            if satisfied
            else RelationshipPolicyResolutionStatus.BLOCKED_MISSING
        ),
        policy_use_id="bru_" + "3" * 24,
        policy_id=("brp_" + "4" * 24 if satisfied else None),
        limitation_code=(None if satisfied else "P18_RELATIONSHIP_POLICY_MISSING"),
    )


def test_p9_projection_preserves_evidence_scope_and_epistemic_layers_without_causal_promotion():
    result = project_relationship_result(
        research_session_id="rs_" + "2" * 24,
        claim=relationship_claim(),
        decision=policy_decision(),
        scope_lineage_id="atl_b2",
        scope_version_id="scope_v2",
        applicability_scope={"department": ["Assembly"]},
    )
    assert result.analytical_kind == RelationshipAnalyticalKind.ASSOCIATION
    assert result.association_state == RelationshipLayerState.SUPPORTED
    assert result.business_relationship_state == RelationshipLayerState.SATISFIED
    assert result.supporting_evidence_refs == ("evi_" + f"{1:024x}",)
    assert result.challenging_evidence_refs == ("evi_" + f"{2:024x}",)
    assert result.contextual_evidence_refs == ("evi_" + f"{3:024x}",)
    assert result.scope_lineage_id == "atl_b2"
    assert result.scope_version_id == "scope_v2"
    assert result.causality_state == RelationshipLayerState.NOT_ESTABLISHED
    assert result.contribution_state == RelationshipLayerState.NOT_ESTABLISHED


def test_p9_contested_claim_and_blocked_policy_remain_explicit():
    result = project_relationship_result(
        research_session_id="rs_" + "2" * 24,
        claim=relationship_claim(epistemic="CONTESTED", kind="CO_MOVEMENT"),
        decision=policy_decision(satisfied=False),
        scope_lineage_id="atl_b2",
        scope_version_id="scope_v1",
        applicability_scope={"department": ["Paint"]},
    )
    assert result.analytical_kind == RelationshipAnalyticalKind.CO_MOVEMENT
    assert result.association_state == RelationshipLayerState.CONTESTED
    assert result.co_movement_state == RelationshipLayerState.CONTESTED
    assert result.business_relationship_state == RelationshipLayerState.BLOCKED
    assert "P18_RELATIONSHIP_POLICY_MISSING" in result.limitation_codes
    assert "ASSOCIATION_ONLY" in result.limitation_codes


@pytest.mark.parametrize("kind", ["CAUSALITY", "CONTRIBUTION"])
def test_p9_rejects_unowned_stronger_relationship_kind(kind):
    with pytest.raises(
        ValueError,
        match="P9_RELATIONSHIP_KIND_REQUIRES_OTHER_GOVERNED_AUTHORITY",
    ):
        project_relationship_result(
            research_session_id="rs_" + "2" * 24,
            claim=relationship_claim(kind=kind),
            decision=policy_decision(),
            scope_lineage_id="atl_b2",
            scope_version_id="scope_v1",
            applicability_scope={"department": ["Assembly"]},
        )


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        (brief(question("g_breakdown", ResearchGoalKind.BREAKDOWN)), ProductExecutionMode.FAST),
        (brief(question("g_ranking", ResearchGoalKind.RANKING)), ProductExecutionMode.FAST),
        (
            brief(
                question(
                    "g_compare",
                    ResearchGoalKind.COMPARISON,
                    comparisons=(ComparisonSurface(text="current vs prior"),),
                )
            ),
            ProductExecutionMode.FAST,
        ),
        (
            brief(
                question(
                    "g_multi",
                    ResearchGoalKind.COMPARISON,
                    subjects=(M1, M2),
                    related=(D1,),
                )
            ),
            ProductExecutionMode.GUIDED,
        ),
        (
            brief(
                question(
                    "g_relationship",
                    ResearchGoalKind.RELATIONSHIP,
                    subjects=(M1, M2),
                    related=(D1,),
                )
            ),
            ProductExecutionMode.GUIDED,
        ),
        (brief(question("g_root", ResearchGoalKind.ROOT_CAUSE)), ProductExecutionMode.INVESTIGATION),
    ],
)
def test_p11_deterministic_router_matrix(item, expected):
    decision = classify_execution_mode(item)
    assert decision.mode == expected


def test_p11_adaptive_and_counter_evidence_are_investigation():
    base = brief(question("g_breakdown", ResearchGoalKind.BREAKDOWN))
    requirement = ProductInvestigationRequirement(
        requirement_id="pir_" + "a" * 20,
        kind=ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL,
        source_goal_id="g_breakdown",
        source_text="Follow verified material.",
    )
    assert (
        classify_execution_mode(
            base,
            investigation_requirements=(requirement,),
        ).mode
        == ProductExecutionMode.INVESTIGATION
    )
    assert (
        classify_execution_mode(
            base,
            counter_evidence_required=True,
        ).mode
        == ProductExecutionMode.INVESTIGATION
    )


def test_b2_projection_and_router_have_no_analytics_or_query_authority():
    import app.v3.business_relationship_v1 as p9
    import app.v3.product.execution_mode as p11

    source = (inspect.getsource(p9) + "\n" + inspect.getsource(p11)).lower()
    forbidden = (
        "execute_dataset",
        "execute_native_query",
        "attest_native_query",
        "sqlmodel",
        "sqlalchemy",
        "metabaseagentclient",
        "query_optimizer",
        "causal_probability",
        "correlation(",
    )
    assert not any(token in source for token in forbidden)
