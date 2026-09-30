from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    CausalQualification,
    ContributionClass,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
)
from app.v3.hypothesis_root_cause_v1 import (
    NextTestEvidenceSurface,
    discriminating_test_is_callable,
    next_test_request,
)
from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductCompositionTerminal,
    ProductRequirementFulfillment,
    ProductRequirementKind,
    ProductRequirementState,
    RootCauseExecutionMode,
    _root_cause_execution_mode,
)
from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.product.execution_mode import (
    ProductExecutionMode,
    classify_execution_mode,
)
from app.v3.research_analytical_scope import (
    analytical_scope_contract,
    coorigin_material_requirements,
)
from app.v3.research_contracts import (
    CausalCompetitionSurface,
    PresentationKind,
    RankingSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeMutation,
    ScopeMutationKind,
    ScopeVersion,
    SemanticTargetKind,
    TemporalRole,
    apply_scope_mutation,
)
from app.v3.research_manager import InvestigationIntent


MANIFEST = Path(__file__).parents[1] / "eval" / "v1" / "phase1_capability_metamorphic_manifest.json"


def _ref(
    candidate_id: str,
    kind: SemanticTargetKind,
    *,
    dimension_name: str | None = None,
    value: str | None = None,
) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=kind,
        canonical_name=candidate_id,
        dimension_name=dimension_name,
        value=value,
        cube_names=("alternate_operations",),
    )


THROUGHPUT = _ref("metric.throughput_units", SemanticTargetKind.METRIC)
DEFECTS = _ref("metric.defect_units", SemanticTargetKind.METRIC)
ENERGY = _ref("metric.energy_loss_kwh", SemanticTargetKind.METRIC)
CALIBRATION = _ref("metric.calibration_delay_hours", SemanticTargetKind.METRIC)
MATERIAL = _ref("metric.material_wait_hours", SemanticTargetKind.METRIC)
LINE = _ref("dimension.production_line", SemanticTargetKind.DIMENSION)
SHIFT = _ref("dimension.shift", SemanticTargetKind.DIMENSION)
DATE = _ref("dimension.production_date", SemanticTargetKind.DIMENSION)
ALPHA = _ref(
    "entity.production_line.alpha",
    SemanticTargetKind.ENTITY_VALUE,
    dimension_name="production_line",
    value="Alpha",
)
BETA = _ref(
    "entity.production_line.beta",
    SemanticTargetKind.ENTITY_VALUE,
    dimension_name="production_line",
    value="Beta",
)


def _brief(*questions: ResearchQuestion, report: bool = False) -> ResearchBrief:
    refs: dict[str, ResearchSemanticRef] = {}
    for question in questions:
        for item in (*question.subject_refs, *question.related_refs):
            refs[item.candidate_id] = item
    deliverables = (
        (
            ResearchDeliverableRequirement(
                requirement_id="d_alt_report",
                kind=PresentationKind.REPORT,
                source_text="Produce a governed alternate-operations report.",
            ),
        )
        if report
        else ()
    )
    return ResearchBrief(
        brief_id="rb-alt-capability",
        objective="Independent alternate-domain capability proof.",
        scope=ResearchScope(semantic_refs=tuple(refs.values())),
        questions=tuple(questions),
        deliverables=deliverables,
        must_requirement_ids=tuple(
            [item.goal_id for item in questions]
            + [item.requirement_id for item in deliverables]
        ),
        context_version="ctx-alt-capability-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _session(brief: ResearchBrief):
    return SimpleNamespace(
        session_id="rs_" + "a" * 24,
        accepted_brief=brief,
        authority_id="atc_alt_capability",
        context_version=brief.context_version,
        lineage_id="atl_alt_capability",
        tenant_binding="id:00000000-0000-4000-8000-000000009901",
        principal_subject="00000000-0000-4000-8000-000000009902",
    )


def test_capability_metamorphic_manifest_is_independent_and_complete():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "dima_phase1_capability_metamorphic_v1"
    assert manifest["paid_cognition_required"] is False
    assert manifest["benchmark_case_ids"] == []
    assert [item["family"] for item in manifest["cases"]] == [
        "scope_currentness",
        "relationship",
        "adaptive",
        "rca_one_pass",
        "rca_adaptive",
        "reporting",
        "multi_intent",
    ]
    serialized = json.dumps(manifest, sort_keys=True).lower()
    for forbidden in (
        "f04_h",
        "f05_h",
        "f06_h",
        "f07_h",
        "f08_h",
        "f10_h",
        "assembly",
        "packaging",
        "machine_downtime_minutes",
    ):
        assert forbidden not in serialized


def test_alt_scope_currentness_mutates_entity_then_date_without_stale_scope_reuse():
    august = ResearchTimePeriod(
        source_text="2026-08-01 through 2026-08-31",
        time_dimension_candidate_id=DATE.candidate_id,
        start="2026-08-01",
        end="2026-09-01",
        role=TemporalRole.MATERIAL_WINDOW,
    )
    september = ResearchTimePeriod(
        source_text="2026-09-01 through 2026-09-30",
        time_dimension_candidate_id=DATE.candidate_id,
        start="2026-09-01",
        end="2026-10-01",
        role=TemporalRole.MATERIAL_WINDOW,
    )
    v1 = ResearchScope(
        semantic_refs=(THROUGHPUT, LINE, DATE, ALPHA, BETA),
        time_surfaces=(august.source_text,),
        periods=(august,),
        temporal_dimension_ids=(DATE.candidate_id,),
    )
    v2 = apply_scope_mutation(
        v1,
        ScopeMutation(
            kind=ScopeMutationKind.NARROW_ENTITY,
            source_version_id="scope_v1",
            target_semantic_refs=(THROUGHPUT, LINE, DATE, ALPHA),
            target_time_surfaces=(august.source_text,),
            target_periods=(august,),
            target_temporal_dimension_ids=(DATE.candidate_id,),
            reason="Narrow alternate production scope to Alpha line.",
        ),
    ).current_scope
    assert v2.scope_version == ScopeVersion(
        version_id="scope_v2",
        ordinal=2,
        parent_version_id="scope_v1",
    )
    assert BETA.candidate_id not in {item.candidate_id for item in v2.semantic_refs}

    v3 = apply_scope_mutation(
        v2,
        ScopeMutation(
            kind=ScopeMutationKind.CHANGE_PERIOD,
            source_version_id="scope_v2",
            target_semantic_refs=v2.semantic_refs,
            target_time_surfaces=(september.source_text,),
            target_periods=(september,),
            target_temporal_dimension_ids=(DATE.candidate_id,),
            reason="Move the accepted Alpha-line analysis to September.",
        ),
    ).current_scope
    assert v3.scope_version.version_id == "scope_v3"
    assert v3.scope_version.parent_version_id == "scope_v2"
    assert v3.periods == (september,)


def test_alt_relationship_preserves_two_metrics_and_new_dimension():
    goal = ResearchQuestion(
        goal_id="g_alt_relationship",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text="Inspect energy loss with defect units by production line.",
        subject_refs=(ENERGY, DEFECTS),
        related_refs=(LINE,),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = _brief(goal)
    contract = analytical_scope_contract(
        session=_session(brief),
        obligation_id=goal.goal_id,
    )
    assert contract.metric_refs == (ENERGY.candidate_id, DEFECTS.candidate_id)
    assert contract.dimension_refs == (LINE.candidate_id,)
    assert contract.comparison is None


def test_alt_adaptive_requirement_routes_to_investigation_without_text_routing():
    goal = ResearchQuestion(
        goal_id="g_alt_adaptive",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect throughput by shift.",
        subject_refs=(THROUGHPUT,),
        related_refs=(SHIFT,),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = _brief(goal)
    requirement = ProductInvestigationRequirement(
        requirement_id="pir_" + "9" * 20,
        kind=ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL,
        source_goal_id=goal.goal_id,
        source_text="Follow a verified material direction if one emerges.",
    )
    decision = classify_execution_mode(
        brief,
        investigation_requirements=(requirement,),
    )
    assert decision.mode == ProductExecutionMode.INVESTIGATION
    assert decision.reason_codes == ("TYPED_ADAPTIVE_INVESTIGATION",)


def test_alt_one_pass_rca_uses_new_effect_candidates_dimension_and_dates():
    evidence_window = ResearchTimePeriod(
        source_text="2026-Q3 alternate evidence window",
        time_dimension_candidate_id=DATE.candidate_id,
        start="2026-07-01",
        end="2026-10-01",
        role=TemporalRole.EVIDENCE_WINDOW,
    )
    effect_period = ResearchTimePeriod(
        source_text="September 2026 alternate effect period",
        time_dimension_candidate_id=DATE.candidate_id,
        start="2026-09-01",
        end="2026-10-01",
        role=TemporalRole.EFFECT_PERIOD,
    )
    goal = ResearchQuestion(
        goal_id="g_alt_rca_one_pass",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate calibration delay versus material wait for energy loss.",
        subject_refs=(ENERGY, CALIBRATION, MATERIAL),
        related_refs=(LINE, DATE),
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id=ENERGY.candidate_id,
            candidate_mechanism_semantic_ids=(
                CALIBRATION.candidate_id,
                MATERIAL.candidate_id,
            ),
            diagnostic_dimension_ids=(LINE.candidate_id,),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = ResearchBrief(
        brief_id="rb-alt-rca-one-pass",
        objective=goal.source_text,
        scope=ResearchScope(
            semantic_refs=(ENERGY, CALIBRATION, MATERIAL, LINE, DATE),
            time_surfaces=(effect_period.source_text, evidence_window.source_text),
            periods=(effect_period, evidence_window),
            temporal_dimension_ids=(DATE.candidate_id,),
        ),
        questions=(goal,),
        must_requirement_ids=(goal.goal_id,),
        context_version="ctx-alt-rca-one-pass",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    requirement = coorigin_material_requirements(_session(brief))[0]
    assert requirement.required_metric_refs == (
        ENERGY.candidate_id,
        CALIBRATION.candidate_id,
        MATERIAL.candidate_id,
    )
    assert requirement.required_dimension_refs == (LINE.candidate_id, DATE.candidate_id)
    assert _root_cause_execution_mode(
        aggregate_outcome=AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED,
        analytical_reentry_count=0,
        unresolved_without_callable_test=False,
    ) == RootCauseExecutionMode.ONE_PASS


class _AdaptiveProfile:
    max_depth = 3

    @staticmethod
    def rule_for(intent):
        if intent == InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE:
            return object()
        return None


def test_alt_adaptive_rca_requests_only_a_callable_discriminating_surface():
    h1 = "p19h_" + "a" * 24
    h2 = "p19h_" + "b" * 24
    snapshot = SimpleNamespace(
        research_session_id="rs_" + "b" * 24,
        obligation_id="g_alt_rca_adaptive",
        hypotheses=(
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h1),
                groundings=(
                    SimpleNamespace(
                        source_kind=GroundingSourceKind.P14_EVIDENCE,
                        source_ref="evi_" + "a" * 24,
                        relation=GroundingRelation.SUPPORTS,
                    ),
                ),
            ),
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h2),
                groundings=(
                    SimpleNamespace(
                        source_kind=GroundingSourceKind.P14_EVIDENCE,
                        source_ref="evi_" + "b" * 24,
                        relation=GroundingRelation.SUPPORTS,
                    ),
                ),
            ),
        ),
    )

    def candidate(hypothesis_id: str):
        return SimpleNamespace(
            hypothesis_id=hypothesis_id,
            disposition=HypothesisDisposition.RETAINED,
            identification_limitations=(),
            causal_identification_refs=(),
            contribution_class=ContributionClass.UNKNOWN,
            causal_qualification=CausalQualification.NOT_CLAIMED,
        )

    assessment = SimpleNamespace(
        aggregate_outcome=AggregateOutcome.IN_PROGRESS,
        candidates=(candidate(h1), candidate(h2)),
    )
    request = next_test_request(
        snapshot=snapshot,
        assessment=assessment,
        scope_lineage_id="atl_alt_rca",
        scope_version_id="scope_v1",
    )
    assert request is not None
    assert request.required_evidence_surface == NextTestEvidenceSurface.TEMPORAL_ORDER
    callability = SimpleNamespace(
        remaining_followup_native_turns=1,
        action_profile=_AdaptiveProfile(),
        investigation=SimpleNamespace(nodes=(), max_contract_depth=1),
    )
    assert discriminating_test_is_callable(
        snapshot=callability,
        request=request,
        evidence_surface_available=True,
    )
    assert _root_cause_execution_mode(
        aggregate_outcome=AggregateOutcome.IN_PROGRESS,
        analytical_reentry_count=1,
    ) == RootCauseExecutionMode.ADAPTIVE


def test_alt_reporting_separates_process_and_requirement_completion():
    goal = ResearchQuestion(
        goal_id="g_alt_report_metric",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Report throughput by shift with governed evidence.",
        subject_refs=(THROUGHPUT,),
        related_refs=(SHIFT,),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = _brief(goal, report=True)
    projected = (
        ProductRequirementFulfillment(
            requirement_id=goal.goal_id,
            requirement_kind=ProductRequirementKind.ANALYTICAL,
            state=ProductRequirementState.VERIFIED,
            fulfilled_by_ref="evi_" + "c" * 24,
        ),
        ProductRequirementFulfillment(
            requirement_id="d_alt_report",
            requirement_kind=ProductRequirementKind.DELIVERABLE,
            state=ProductRequirementState.FULFILLED,
            fulfilled_by_ref="p20r_" + "d" * 24,
        ),
    )
    ledger = HeadlessProductComposer._completion_ledger(
        brief=brief,
        projected=projected,
        terminal=ProductCompositionTerminal.REPORT,
    )
    assert ledger.process_complete is True
    assert ledger.requirement_complete is True


def test_alt_multi_intent_compresses_shared_material_without_losing_ranking():
    fragment = "Rank throughput and inspect defect units together by shift."
    rank = ResearchQuestion(
        goal_id="g_alt_rank",
        kind=ResearchGoalKind.RANKING,
        source_text=fragment,
        source_fragment_identity="fragment-sha256:" + "f" * 64,
        subject_refs=(SHIFT, THROUGHPUT),
        ranking=RankingSurface(
            text="top three shifts",
            direction="desc",
            limit=3,
            measure_semantic_id=THROUGHPUT.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    relationship = ResearchQuestion(
        goal_id="g_alt_rel",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text=fragment,
        source_fragment_identity="fragment-sha256:" + "f" * 64,
        subject_refs=(THROUGHPUT, DEFECTS),
        related_refs=(SHIFT,),
        status=ResearchGoalStatus.RESOLVED,
    )
    period = ResearchTimePeriod(
        source_text="2026-07-15 through 2026-08-15",
        time_dimension_candidate_id=DATE.candidate_id,
        start="2026-07-15",
        end="2026-08-16",
        role=TemporalRole.MATERIAL_WINDOW,
    )
    brief = ResearchBrief(
        brief_id="rb-alt-multi",
        objective=fragment,
        scope=ResearchScope(
            semantic_refs=(THROUGHPUT, DEFECTS, SHIFT, DATE),
            time_surfaces=(period.source_text,),
            periods=(period,),
            temporal_dimension_ids=(DATE.candidate_id,),
        ),
        questions=(rank, relationship),
        deliverables=(
            ResearchDeliverableRequirement(
                requirement_id="d_alt_multi_report",
                kind=PresentationKind.REPORT,
                source_text="Produce a concise alternate-domain report.",
            ),
        ),
        must_requirement_ids=(
            rank.goal_id,
            relationship.goal_id,
            "d_alt_multi_report",
        ),
        context_version="ctx-alt-multi-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    session = _session(brief)
    requirement = coorigin_material_requirements(session)[0]
    assert requirement.source_goal_ids == (rank.goal_id, relationship.goal_id)
    assert requirement.required_metric_refs == (
        THROUGHPUT.candidate_id,
        DEFECTS.candidate_id,
    )
    contract = analytical_scope_contract(
        session=session,
        obligation_id=rank.goal_id,
    )
    assert contract.ranking is not None
    assert contract.ranking.measure == THROUGHPUT.candidate_id
    assert contract.ranking.limit == 3
    assert contract.metric_refs == (
        THROUGHPUT.candidate_id,
        DEFECTS.candidate_id,
    )
    assert classify_execution_mode(brief).mode == ProductExecutionMode.GUIDED
