from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.v3.business_relationship_policy import (
    RelationshipPolicyDecision,
    RelationshipPolicyResolutionStatus,
)
from app.v3.business_relationship_v1 import (
    RelationshipLayerState,
    project_relationship_result,
)
from app.v3.hypothesis_root_cause import (
    CausalQualification,
    ContributionClass,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
)
from app.v3.hypothesis_root_cause_v1 import (
    ExpectedDiscriminatoryValue,
    NextTestEvidenceSurface,
    NextTestRequest,
    discriminating_test_is_callable,
    project_candidate_factors,
)
from app.v3.product.execution_mode import (
    ProductExecutionMode,
    classify_execution_mode,
)
from app.v3.product.process_manager import (
    P19EligibilityDecision,
    ProductProcessObservation,
    RootCauseCandidate,
    p19_eligibility,
)
from app.v3.root_cause_candidate_contract import (
    RootCauseCandidateRelation,
    RootCauseCandidateSemantics,
)
from app.v3.research_analytical_scope import (
    ResearchAnalyticalScopeError,
    analytical_scope_contract,
    coorigin_material_requirements,
)
from app.v3.research_native_gateway import NativeResearchMaterialExecutor
from app.v3.research_product import ResearchMaterialLimitation
from control_plane.authorize import Principal
from control_plane.models import NativeResourceBinding
from app.v3.research_contracts import (
    RankingSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeMutation,
    ScopeVersion,
    ScopeMutationKind,
    SemanticTargetKind,
    apply_scope_mutation,
)
from app.v3.research_manager import InvestigationIntent


MANIFEST = Path("eval/v1/phase1_metamorphic_manifest.json")


def _candidate(claim_id: str, mechanism: str, evidence: str) -> RootCauseCandidate:
    return RootCauseCandidate(
        claim_id=claim_id,
        semantics=RootCauseCandidateSemantics(
            explanatory_subject_ref="g_root",
            relation_kind=RootCauseCandidateRelation.EXPLANATORY_CANDIDATE,
            mechanism_ref=mechanism,
            scope_lineage_id="atl_meta",
            scope_version_id="scope_v2",
        ),
        evidence_refs=(evidence,),
    )


def _p6_observation(candidates, *, claims=("c1", "c2")):
    return ProductProcessObservation(
        claim_ids=tuple(claims),
        remaining_reasoning_steps=3,
        scoped_move_available=True,
        root_cause_candidates=tuple(candidates),
    )


def _semantic(cid: str, kind: SemanticTargetKind, name: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=kind,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


M1 = _semantic("metric.downtime", SemanticTargetKind.METRIC, "Downtime")
M2 = _semantic("metric.faults", SemanticTargetKind.METRIC, "Faults")
D1 = _semantic("dimension.department", SemanticTargetKind.DIMENSION, "Department")
E1 = ResearchSemanticRef(
    source_mention="Assembly",
    candidate_id="entity.department.assembly",
    target_kind=SemanticTargetKind.ENTITY_VALUE,
    canonical_name="Assembly",
    dimension_name="department",
    value="Assembly",
    cube_names=("machine_operations",),
)
E2 = ResearchSemanticRef(
    source_mention="Packaging",
    candidate_id="entity.department.packaging",
    target_kind=SemanticTargetKind.ENTITY_VALUE,
    canonical_name="Packaging",
    dimension_name="department",
    value="Packaging",
    cube_names=("machine_operations",),
)


def _brief(*, source_text="Show downtime", metrics=(M1,), kind=ResearchGoalKind.BREAKDOWN):
    refs = (*metrics, D1)
    question = ResearchQuestion(
        goal_id="g1",
        kind=kind,
        source_text=source_text,
        subject_refs=tuple(metrics),
        related_refs=(D1,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-meta",
        objective="metamorphic routing",
        scope=ResearchScope(semantic_refs=refs),
        questions=(question,),
        must_requirement_ids=("g1",),
        context_version="ctx-meta",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _next_test_request() -> NextTestRequest:
    return NextTestRequest(
        request_id="ntr_" + "a" * 24,
        ambiguity_code="COUNTER_EVIDENCE_REQUIRED",
        hypothesis_ids=("p19h_" + "1" * 24, "p19h_" + "2" * 24),
        required_evidence_surface=NextTestEvidenceSurface.COUNTER_EVIDENCE,
        expected_discriminatory_value=ExpectedDiscriminatoryValue.POSITIVE_MATERIAL,
        scope_lineage_id="atl_meta",
        scope_version_id="scope_v2",
    )


class _Profile:
    max_depth = 3

    @staticmethod
    def rule_for(intent):
        if intent == InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE:
            return object()
        return None


def _p8_snapshot(*, consumed=False, max_contract_depth=2):
    request = _next_test_request()
    nodes = (
        (SimpleNamespace(target_ref=request.request_id),)
        if consumed
        else (SimpleNamespace(target_ref="other"),)
    )
    return SimpleNamespace(
        remaining_followup_native_turns=1,
        action_profile=_Profile(),
        investigation=SimpleNamespace(
            nodes=nodes,
            max_contract_depth=max_contract_depth,
        ),
    )


def _p19_projection(*, challenge: bool):
    h1 = "p19h_" + "1" * 24
    h2 = "p19h_" + "2" * 24
    links1 = [
        SimpleNamespace(
            source_kind=GroundingSourceKind.P14_EVIDENCE,
            source_ref="evi_" + "1" * 24,
            relation=GroundingRelation.SUPPORTS,
        )
    ]
    if challenge:
        links1.append(
            SimpleNamespace(
                source_kind=GroundingSourceKind.P14_EVIDENCE,
                source_ref="evi_" + "3" * 24,
                relation=GroundingRelation.CHALLENGES,
            )
        )
    snapshot = SimpleNamespace(
        hypotheses=(
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h1),
                groundings=tuple(links1),
            ),
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h2),
                groundings=(
                    SimpleNamespace(
                        source_kind=GroundingSourceKind.P14_EVIDENCE,
                        source_ref="evi_" + "2" * 24,
                        relation=GroundingRelation.SUPPORTS,
                    ),
                ),
            ),
        )
    )
    candidates = tuple(
        SimpleNamespace(
            hypothesis_id=hypothesis_id,
            disposition=HypothesisDisposition.RETAINED,
            contribution_class=ContributionClass.MATERIAL,
            causal_qualification=CausalQualification.NOT_CLAIMED,
            identification_limitations=(),
            causal_identification_refs=(),
        )
        for hypothesis_id in (h1, h2)
    )
    return project_candidate_factors(
        snapshot=snapshot,
        assessment=SimpleNamespace(candidates=candidates),
        scope_lineage_id="atl_meta",
        scope_version_id="scope_v2",
    )


def _relationship_projection(*, challenge: bool):
    links = [
        SimpleNamespace(
            evidence_id="evi_" + "1" * 24,
            relation="SUPPORTS",
        )
    ]
    if challenge:
        links.append(
            SimpleNamespace(
                evidence_id="evi_" + "2" * 24,
                relation="CHALLENGES",
            )
        )
    claim = SimpleNamespace(
        claim_id="clm_" + "1" * 24,
        obligation_id="g1",
        proposition={"relationship_kind": "ASSOCIATION"},
        epistemic_state=SimpleNamespace(value="SUPPORTED"),
        limitations=("ASSOCIATION_ONLY",),
        evidence_links=tuple(links),
    )
    decision = RelationshipPolicyDecision(
        required=True,
        eligible=True,
        resolution_status=RelationshipPolicyResolutionStatus.SATISFIED,
        policy_use_id="bru_" + "1" * 24,
        policy_id="brp_" + "1" * 24,
        limitation_code=None,
    )
    return project_relationship_result(
        research_session_id="rs_" + "1" * 24,
        claim=claim,
        decision=decision,
        scope_lineage_id="atl_meta",
        scope_version_id="scope_v2",
        applicability_scope={"department": ["Assembly"]},
    )


def test_manifest_is_eval_only_and_covers_all_declared_mutations():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "dima-v1-phase1-metamorphic-v1"
    assert manifest["authority"] == "EVAL_ONLY"
    assert len(manifest["cases"]) == 12
    assert len({item["id"] for item in manifest["cases"]}) == 12
    assert {item["family"] for item in manifest["cases"]} >= {
        "P6", "P7_P9", "P8", "P11", "P2", "P10", "P0"
    }


def test_p6_paraphrase_and_candidate_permutation_do_not_change_typed_eligibility():
    candidates = (
        _candidate("c1", "fault-pressure", "e1"),
        _candidate("c2", "maintenance-delay", "e2"),
    )
    a = _p6_observation(candidates)
    b = _p6_observation(tuple(reversed(candidates)))
    # Claim prose is deliberately absent from ProductProcessObservation.
    assert p19_eligibility(a) == P19EligibilityDecision.CALL_P19
    assert p19_eligibility(b) == P19EligibilityDecision.CALL_P19


def test_p6_missing_evidence_or_duplicate_mechanism_cannot_fake_distinct_candidates():
    missing = _p6_observation(
        (_candidate("c1", "fault-pressure", "e1"),),
        claims=("c1", "c2"),
    )
    duplicate = _p6_observation(
        (
            _candidate("c1", "same-mechanism", "e1"),
            _candidate("c2", "same-mechanism", "e2"),
        )
    )
    assert p19_eligibility(missing) == P19EligibilityDecision.NEED_MORE_EVIDENCE
    assert p19_eligibility(duplicate) == P19EligibilityDecision.NEED_MORE_EVIDENCE


def test_p7_challenge_mutation_is_visible_without_causal_promotion():
    before = _p19_projection(challenge=False)[0]
    after = _p19_projection(challenge=True)[0]
    assert before.challenging_evidence_refs == ()
    assert after.challenging_evidence_refs == ("evi_" + "3" * 24,)
    assert before.causal_qualification == after.causal_qualification == CausalQualification.NOT_CLAIMED


def test_p9_challenge_mutation_is_visible_without_contribution_or_causality():
    before = _relationship_projection(challenge=False)
    after = _relationship_projection(challenge=True)
    assert before.challenging_evidence_refs == ()
    assert after.challenging_evidence_refs == ("evi_" + "2" * 24,)
    assert after.causality_state == RelationshipLayerState.NOT_ESTABLISHED
    assert after.contribution_state == RelationshipLayerState.NOT_ESTABLISHED


def test_p8_same_next_test_request_is_one_shot_and_depth_three_is_hard_stop():
    request = _next_test_request()
    assert discriminating_test_is_callable(
        snapshot=_p8_snapshot(),
        request=request,
        evidence_surface_available=True,
    )
    assert not discriminating_test_is_callable(
        snapshot=_p8_snapshot(consumed=True),
        request=request,
        evidence_surface_available=True,
    )
    assert not discriminating_test_is_callable(
        snapshot=_p8_snapshot(max_contract_depth=3),
        request=request,
        evidence_surface_available=True,
    )


def test_p11_paraphrase_does_not_change_mode_but_second_typed_metric_does():
    original = _brief(source_text="Show downtime")
    paraphrase = _brief(source_text="Duruş süresini bölüm bazında getir.")
    multi = _brief(
        source_text="Show downtime and faults",
        metrics=(M1, M2),
        kind=ResearchGoalKind.COMPARISON,
    )
    assert classify_execution_mode(original).mode == ProductExecutionMode.FAST
    assert classify_execution_mode(paraphrase).mode == ProductExecutionMode.FAST
    assert classify_execution_mode(multi).mode == ProductExecutionMode.GUIDED


def test_p2_entity_narrowing_advances_exact_scope_version_and_parent():
    current = ResearchScope(
        semantic_refs=(M1, D1, E1, E2),
        time_surfaces=("2026-05", "2026-06"),
    )
    mutation = ScopeMutation(
        kind=ScopeMutationKind.NARROW_ENTITY,
        source_version_id="scope_v1",
        target_semantic_refs=(M1, D1, E1),
        target_time_surfaces=("2026-05", "2026-06"),
        reason="Narrow to Assembly.",
    )
    contract = apply_scope_mutation(current, mutation)
    assert contract.previous_scope.scope_version.version_id == "scope_v1"
    assert contract.current_scope.scope_version.version_id == "scope_v2"
    assert contract.current_scope.scope_version.parent_version_id == "scope_v1"
    assert {x.candidate_id for x in contract.current_scope.semantic_refs} == {
        M1.candidate_id, D1.candidate_id, E1.candidate_id
    }



# Phase-1 80/90 closure: co-origin material compression matrix.

M3 = _semantic("metric.revenue", SemanticTargetKind.METRIC, "Revenue")
M4 = _semantic("metric.margin", SemanticTargetKind.METRIC, "Margin")
D2 = _semantic("dimension.product", SemanticTargetKind.DIMENSION, "Product")
DT = _semantic("dimension.event_date", SemanticTargetKind.DIMENSION, "Event Date")


def _coorigin_session(
    *,
    source="Rank by metric A and inspect together with metric B.",
    anchor_source=None,
    source_fragment_identity="fragment-sha256:" + "a" * 64,
    relationship_fragment_identity=None,
    anchor_metric=M1,
    downstream_metric=M2,
    dimension=D1,
    anchor_kind=ResearchGoalKind.RANKING,
    relationship=True,
    relationship_source=None,
    anchor_extra_metrics=(),
    scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
    context_version="ctx-coorigin-v1",
    period=None,
    include_downstream_in_scope=True,
):
    anchor = ResearchQuestion(
        goal_id="g_anchor",
        kind=anchor_kind,
        source_text=(anchor_source if anchor_source is not None else source),
        source_fragment_identity=source_fragment_identity,
        subject_refs=(dimension, anchor_metric, *anchor_extra_metrics),
        related_refs=(),
        ranking=(
            RankingSurface(
                text="top 2",
                direction="desc",
                limit=2,
                measure_semantic_id=anchor_metric.candidate_id,
            )
            if anchor_kind == ResearchGoalKind.RANKING
            else None
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    questions = [anchor]
    if relationship:
        questions.append(
            ResearchQuestion(
                goal_id="g_relationship",
                kind=ResearchGoalKind.RELATIONSHIP,
                source_text=(relationship_source if relationship_source is not None else source),
                source_fragment_identity=(
                    relationship_fragment_identity
                    if relationship_fragment_identity is not None
                    else source_fragment_identity
                ),
                subject_refs=(anchor_metric, downstream_metric),
                related_refs=(dimension,),
                status=ResearchGoalStatus.RESOLVED,
            )
        )

    refs = [anchor_metric, dimension, *anchor_extra_metrics]
    if include_downstream_in_scope and downstream_metric.candidate_id not in {
        item.candidate_id for item in refs
    }:
        refs.append(downstream_metric)
    if period is not None and DT.candidate_id not in {item.candidate_id for item in refs}:
        refs.append(DT)

    scope_kwargs = {
        "semantic_refs": tuple(refs),
        "scope_version": scope_version,
    }
    if period is not None:
        scope_kwargs.update(
            {
                "time_surfaces": (period.source_text,),
                "periods": (period,),
                "temporal_dimension_ids": (DT.candidate_id,),
            }
        )
    brief = ResearchBrief(
        brief_id="rb-coorigin",
        objective=source,
        scope=ResearchScope(**scope_kwargs),
        questions=tuple(questions),
        must_requirement_ids=tuple(item.goal_id for item in questions),
        context_version=context_version,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    return SimpleNamespace(
        session_id="rs_" + "c" * 24,
        accepted_brief=brief,
        authority_id="atc_coorigin",
        context_version=context_version,
        lineage_id="atl_coorigin",
        tenant_binding="id:00000000-0000-4000-8000-000000009001",
        principal_subject="00000000-0000-4000-8000-000000009002",
    )


def test_coorigin_exact_subset_projects_one_union_without_mutating_ranking_semantics():
    session = _coorigin_session(
        anchor_source="En yüksek downtime olan iki bölümü incele.",
        relationship_source=(
            "En yüksek downtime olan iki bölümü fault count ile birlikte incele."
        ),
    )
    requirements = coorigin_material_requirements(session)
    assert len(requirements) == 1
    requirement = requirements[0]
    assert requirement.anchor_goal_id == "g_anchor"
    assert requirement.source_goal_ids == ("g_anchor", "g_relationship")
    assert requirement.required_metric_refs == (M1.candidate_id, M2.candidate_id)
    assert requirement.required_dimension_refs == (D1.candidate_id,)

    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert contract.metric_refs == (M1.candidate_id, M2.candidate_id)
    assert contract.dimension_refs == (D1.candidate_id,)
    assert contract.ranking is not None
    assert contract.ranking.kind == "native_metric"
    assert contract.ranking.measure == M1.candidate_id
    assert contract.ranking.direction == "desc"
    assert contract.ranking.limit == 2

    accepted_anchor = session.accepted_brief.questions[0]
    assert tuple(item.candidate_id for item in accepted_anchor.subject_refs) == (
        D1.candidate_id,
        M1.candidate_id,
    )
    assert M2.candidate_id not in {
        item.candidate_id for item in accepted_anchor.subject_refs
    }


def test_coorigin_m1_different_metric_identities_remain_generic():
    session = _coorigin_session(anchor_metric=M3, downstream_metric=M4, dimension=D2)
    requirement = coorigin_material_requirements(session)[0]
    assert requirement.required_metric_refs == (M3.candidate_id, M4.candidate_id)
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert contract.ranking.measure == M3.candidate_id
    assert contract.metric_refs == (M3.candidate_id, M4.candidate_id)


def test_coorigin_m2_different_dimension_remains_generic():
    session = _coorigin_session(anchor_metric=M3, downstream_metric=M4, dimension=D2)
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert contract.dimension_refs == (D2.candidate_id,)
    assert D1.candidate_id not in contract.dimension_refs


def test_coorigin_m3_different_date_range_preserves_typed_period():
    period = ResearchTimePeriod(
        source_text="2026-08-10 through 2026-08-24",
        time_dimension_candidate_id=DT.candidate_id,
        start="2026-08-10",
        end="2026-08-25",
    )
    session = _coorigin_session(period=period)
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert contract.period is not None
    assert contract.period.start == "2026-08-10"
    assert contract.period.end == "2026-08-25"
    assert contract.metric_refs == (M1.candidate_id, M2.candidate_id)


def test_coorigin_m4_ranking_only_does_not_fetch_unrelated_relationship_material():
    session = _coorigin_session(relationship=False)
    assert coorigin_material_requirements(session) == ()
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert contract.metric_refs == (M1.candidate_id,)
    assert contract.ranking.measure == M1.candidate_id


def test_coorigin_m5_relationship_only_preserves_direct_material_contract():
    source = "Inspect downtime together with faults by department."
    relationship = ResearchQuestion(
        goal_id="g_relationship",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text=source,
        subject_refs=(M1, M2),
        related_refs=(D1,),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = ResearchBrief(
        brief_id="rb-relationship-only",
        objective=source,
        scope=ResearchScope(semantic_refs=(M1, M2, D1)),
        questions=(relationship,),
        must_requirement_ids=(relationship.goal_id,),
        context_version="ctx-relationship-only",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    session = SimpleNamespace(
        session_id="rs_" + "d" * 24,
        accepted_brief=brief,
        authority_id="atc_relationship_only",
        context_version=brief.context_version,
        lineage_id="atl_relationship_only",
        tenant_binding="id:00000000-0000-4000-8000-000000009001",
        principal_subject="00000000-0000-4000-8000-000000009002",
    )
    assert coorigin_material_requirements(session) == ()
    contract = analytical_scope_contract(
        session=session,
        obligation_id=relationship.goal_id,
    )
    assert contract.metric_refs == (M1.candidate_id, M2.candidate_id)
    assert contract.dimension_refs == (D1.candidate_id,)


def test_coorigin_m6_overlapping_refs_different_provenance_do_not_merge():
    session = _coorigin_session(
        source="One current message with two distinct clauses.",
        anchor_source="Rank downtime by department.",
        relationship_source="Inspect downtime and faults together by department.",
        source_fragment_identity="fragment-sha256:" + "b" * 64,
        relationship_fragment_identity="fragment-sha256:" + "c" * 64,
    )
    assert coorigin_material_requirements(session) == ()
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert contract.metric_refs == (M1.candidate_id,)


def test_coorigin_m7_scope_version_is_part_of_projection_identity_and_never_cross_shared():
    v1 = _coorigin_session(
        scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
        context_version="ctx-scope-v1",
    )
    v2 = _coorigin_session(
        scope_version=ScopeVersion(
            version_id="scope_v2",
            ordinal=2,
            parent_version_id="scope_v1",
        ),
        context_version="ctx-scope-v2",
    )
    r1 = coorigin_material_requirements(v1)[0]
    r2 = coorigin_material_requirements(v2)[0]
    assert r1.source_fragment_identity == r2.source_fragment_identity
    assert r1.scope_version_id == "scope_v1"
    assert r2.scope_version_id == "scope_v2"
    assert r1.semantic_context_version != r2.semantic_context_version
    assert r1 != r2


def test_coorigin_m8_missing_governed_native_binding_fails_closed_before_execution():
    session = _coorigin_session(include_downstream_in_scope=True)
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert M2.candidate_id in contract.metric_refs

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    tenant_id = UUID("00000000-0000-4000-8000-000000009001")
    user_id = UUID("00000000-0000-4000-8000-000000009002")
    with Session(engine) as db:
        db.add(
            NativeResourceBinding(
                tenant_id=tenant_id,
                semantic_context_version=session.context_version,
                candidate_id=M1.candidate_id,
                candidate_kind=SemanticTargetKind.METRIC.value,
                semantic_id=M1.candidate_id,
                canonical_name=M1.canonical_name,
                locator_kind="metric",
                metabase_database_id=1,
                metabase_table_id=10,
                metabase_metric_id=501,
                metabase_entity_id="metric-downtime-v1",
                resource_entity_id="metabase:metric:metric-downtime-v1",
                resource_fingerprint="1" * 64,
                resource_version="coorigin-m8-v1",
                enabled=True,
            )
        )
        db.add(
            NativeResourceBinding(
                tenant_id=tenant_id,
                semantic_context_version=session.context_version,
                candidate_id=D1.candidate_id,
                candidate_kind=SemanticTargetKind.DIMENSION.value,
                semantic_id=D1.candidate_id,
                canonical_name=D1.canonical_name,
                locator_kind="field",
                metabase_database_id=1,
                metabase_table_id=10,
                metabase_field_id=20,
                resource_entity_id="metabase:field:20",
                resource_fingerprint="2" * 64,
                resource_version="coorigin-m8-v1",
                enabled=True,
            )
        )
        db.commit()

    executor = object.__new__(NativeResearchMaterialExecutor)
    executor._subjects = SimpleNamespace(db_engine=engine)
    principal = Principal(
        user_id=str(user_id),
        tenant_id=str(tenant_id),
        tenant_slug="coorigin-m8",
        roles=["analyst"],
    )
    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor._material_bindings(
            principal=principal,
            session=session,
            contract=contract,
        )
    assert exc.value.code == "R1_NATIVE_RESOURCE_BINDING_MISSING"
    assert M2.candidate_id in exc.value.detail


def test_coorigin_m9_full_semantic_superset_remains_legal_reuse_material():
    session = _coorigin_session(anchor_extra_metrics=(M2,))
    requirement = coorigin_material_requirements(session)[0]
    assert requirement.required_metric_refs == (M1.candidate_id, M2.candidate_id)
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert contract.metric_refs == (M1.candidate_id, M2.candidate_id)
    assert contract.ranking.measure == M1.candidate_id


def test_coorigin_m10_subset_is_expanded_pre_execution_not_reused_post_execution():
    session = _coorigin_session()
    anchor = session.accepted_brief.questions[0]
    assert M2.candidate_id not in {
        item.candidate_id for item in (*anchor.subject_refs, *anchor.related_refs)
    }
    contract = analytical_scope_contract(session=session, obligation_id="g_anchor")
    assert M2.candidate_id in contract.metric_refs
    assert contract.ranking.measure == M1.candidate_id


def test_coorigin_multiple_native_anchors_fail_closed_instead_of_first_goal_wins():
    source = "Rank and compare downtime, then inspect it with faults."
    rank = ResearchQuestion(
        goal_id="g_rank",
        kind=ResearchGoalKind.RANKING,
        source_text=source,
        subject_refs=(D1, M1),
        ranking=RankingSurface(
            text="top 2",
            direction="desc",
            limit=2,
            measure_semantic_id=M1.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    breakdown = ResearchQuestion(
        goal_id="g_break",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text=source,
        subject_refs=(M1,),
        related_refs=(D1,),
        status=ResearchGoalStatus.RESOLVED,
    )
    relationship = ResearchQuestion(
        goal_id="g_relationship",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text=source,
        subject_refs=(M1, M2),
        related_refs=(D1,),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = ResearchBrief(
        brief_id="rb-ambiguous-anchor",
        objective=source,
        scope=ResearchScope(semantic_refs=(M1, M2, D1)),
        questions=(rank, breakdown, relationship),
        must_requirement_ids=("g_rank", "g_break", "g_relationship"),
        context_version="ctx-ambiguous-anchor",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    session = SimpleNamespace(
        accepted_brief=brief,
        authority_id="atc_ambiguous",
        context_version=brief.context_version,
        lineage_id="atl_ambiguous",
    )
    try:
        coorigin_material_requirements(session)
    except ResearchAnalyticalScopeError as exc:
        assert exc.code == "R1_COORIGIN_MATERIAL_ANCHOR_AMBIGUOUS"
    else:
        raise AssertionError("ambiguous co-origin anchors must fail closed")
