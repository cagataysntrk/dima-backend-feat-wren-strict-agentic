from __future__ import annotations

import json
from itertools import product
from types import SimpleNamespace

import pytest

from app.v3.analytical_boundary import (
    AnalyticalOperation,
    project_analytical_intent_v1,
)
from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
    AnalyticalTemporalChangeFrame,
)
from app.v3.brain_v2.adaptive_policy import adaptive_investigation_authorized
from app.v3.brain_v2.report_synthesis import StructuredP20SynthesisManager
from app.v3.research_contracts import (
    PresentationKind,
    RankingBasis,
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
    ScopeVersion,
    SemanticTargetKind,
    TemporalChangeFrameMode,
    TemporalRole,
)
from app.v3.research_product import ResearchBriefAuthoritySealer
from app.v3.research_scope_patch import (
    ScopePatchFacet,
    ScopePatchOperation,
    ScopePatchOperationKind,
    TurnScopePatch,
    resolve_scope_patch,
    scope_fingerprint,
)
from app.v3.research_temporal_authority import resolve_temporal_authority


def _metric(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=candidate_id,
        cube_names=("symbolic_cube",),
    )


def _dimension(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=candidate_id,
        cube_names=("symbolic_cube",),
    )


def _entity(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.ENTITY_VALUE,
        canonical_name=candidate_id,
        dimension_name="dimension.entity",
        value=candidate_id,
        cube_names=("symbolic_cube",),
    )


TIME = _dimension("dimension.t")
ENTITIES = (_entity("entity.e1"), _entity("entity.e2"))


def _periods(frame: str) -> tuple[ResearchTimePeriod, ...]:
    if frame == "PAIR":
        return (
            ResearchTimePeriod(
                source_text="baseline window",
                time_dimension_candidate_id=TIME.candidate_id,
                start="2026-01-01",
                end="2026-02-01",
                role=TemporalRole.BASELINE_PERIOD,
            ),
            ResearchTimePeriod(
                source_text="comparison window",
                time_dimension_candidate_id=TIME.candidate_id,
                start="2026-02-01",
                end="2026-03-01",
                role=TemporalRole.COMPARISON_PERIOD,
            ),
        )
    return (
        ResearchTimePeriod(
            source_text="bounded movement window",
            time_dimension_candidate_id=TIME.candidate_id,
            start="2026-01-01",
            end="2026-03-01",
            role=TemporalRole.MATERIAL_WINDOW,
        ),
    )


def _scope(
    *,
    metric_count: int,
    dimension_id: str,
    frame: str,
    reverse: bool,
    version: int = 1,
) -> ResearchScope:
    metrics = tuple(_metric(f"metric.m{i}") for i in range(1, metric_count + 1))
    breakdown = _dimension(dimension_id)
    periods = _periods(frame)
    authority = resolve_temporal_authority((*periods, *periods))
    assert len(authority.periods) == len(periods)
    refs = (*metrics, breakdown, TIME, *ENTITIES)
    if reverse:
        refs = tuple(reversed(refs))
    return ResearchScope(
        semantic_refs=tuple(refs),
        time_surfaces=tuple(
            dict.fromkeys(item.source_text for item in authority.periods)
        ),
        periods=authority.periods,
        temporal_dimension_ids=(TIME.candidate_id,),
        scope_version=ScopeVersion(
            version_id=f"scope_v{version}",
            ordinal=version,
            parent_version_id=(
                None if version == 1 else f"scope_v{version - 1}"
            ),
        ),
    )


def _question(
    *,
    metric_count: int,
    dimension_id: str,
    ranking: bool,
    suffix: str,
) -> ResearchQuestion:
    metrics = tuple(_metric(f"metric.m{i}") for i in range(1, metric_count + 1))
    kind = ResearchGoalKind.RANKING if ranking else ResearchGoalKind.OTHER
    ranking_surface = (
        RankingSurface(
            text="governed change ranking",
            direction="desc",
            limit=2,
            measure_semantic_id="metric.m1",
            basis=RankingBasis.CHANGE,
        )
        if ranking
        else None
    )
    return ResearchQuestion(
        goal_id=f"goal.{suffix}",
        kind=kind,
        source_text="symbolic governed analytical continuation",
        subject_refs=metrics,
        related_refs=(_dimension(dimension_id),),
        ranking=ranking_surface,
        status=ResearchGoalStatus.RESOLVED,
    )


def _brief(
    *,
    scope: ResearchScope,
    metric_count: int,
    dimension_id: str,
    ranking: bool,
    suffix: str,
    report: bool,
) -> ResearchBrief:
    question = _question(
        metric_count=metric_count,
        dimension_id=dimension_id,
        ranking=ranking,
        suffix=suffix,
    )
    deliverables = (
        (
            ResearchDeliverableRequirement(
                requirement_id=f"deliverable.{suffix}",
                kind=PresentationKind.REPORT,
                source_text="short governed management report",
            ),
        )
        if report
        else ()
    )
    return ResearchBrief(
        brief_id=f"brief.{suffix}",
        objective="symbolic governed objective",
        scope=scope,
        questions=(question,),
        deliverables=deliverables,
        must_requirement_ids=(
            question.goal_id,
            *(item.requirement_id for item in deliverables),
        ),
        context_version="ctx-semantic-authority-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _contract(
    *,
    scope: ResearchScope,
    metric_count: int,
    dimension_id: str,
    frame: str,
    ranking: bool,
    reverse: bool,
) -> AnalyticalRequestContract:
    metric_ids = [f"metric.m{i}" for i in range(1, metric_count + 1)]
    if reverse:
        metric_ids.reverse()

    period = None
    comparison = None
    change_frame = None
    if frame == "PAIR":
        baseline, candidate = scope.periods
        reference_period = AnalyticalPeriodInvariant(
            kind="explicit_half_open",
            time_dimension=baseline.time_dimension_candidate_id,
            start=baseline.start,
            end=baseline.end,
        )
        base_period = AnalyticalPeriodInvariant(
            kind="explicit_half_open",
            time_dimension=candidate.time_dimension_candidate_id,
            start=candidate.start,
            end=candidate.end,
        )
        comparison = AnalyticalComparisonInvariant(
            mode="explicit_periods",
            reference_period=reference_period,
            base_period=base_period,
        )
        if ranking:
            change_frame = AnalyticalTemporalChangeFrame(
                mode=TemporalChangeFrameMode.PAIR,
                time_dimension=TIME.candidate_id,
                baseline_period=reference_period,
                comparison_period=base_period,
            )
    else:
        (window,) = scope.periods
        period = AnalyticalPeriodInvariant(
            kind="explicit_half_open",
            time_dimension=window.time_dimension_candidate_id,
            start=window.start,
            end=window.end,
        )
        if ranking:
            change_frame = AnalyticalTemporalChangeFrame(
                mode=TemporalChangeFrameMode.SPAN,
                time_dimension=TIME.candidate_id,
                span_period=period,
            )

    return AnalyticalRequestContract(
        authority_id="authority.symbolic",
        request_ref="request.symbolic",
        semantic_context_version="ctx-semantic-authority-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="lineage.symbolic",
            version_id=scope.scope_version.version_id,
        ),
        scope_fingerprint=scope_fingerprint(
            scope,
            context_version="ctx-semantic-authority-v1",
        ),
        metric_refs=tuple(metric_ids),
        dimension_refs=(dimension_id,),
        period=period,
        comparison=comparison,
        temporal_change_frame=change_frame,
        ranking=(
            AnalyticalRankingInvariant(
                measure="metric.m1",
                direction="desc",
                limit=2,
                basis=RankingBasis.CHANGE,
            )
            if ranking
            else None
        ),
        grain_constraints=(dimension_id,),
        requested_output_surfaces=("report",),
    )


class _SynthesisTransport:
    def __init__(self, *, requirement_id: str, statement_id: str) -> None:
        self.call_count = 0
        self.native_call_count = 0
        self.requirement_id = requirement_id
        self.statement_id = statement_id

    def structured_json(self, system, user, *, schema, schema_name):
        self.call_count += 1
        assert "Metabase" not in schema_name
        assert "native" not in schema_name.lower()
        payload = {
            "deliverables": [
                {
                    "requirement_id": self.requirement_id,
                    "status": "FULFILLED",
                    "selected_statement_ids": [self.statement_id],
                    "sections": [
                        {
                            "kind": "management_implication",
                            "text": (
                                "Governed evidence supports a focused management "
                                "response while preserving the stated limitation."
                            ),
                            "supporting_statement_ids": [self.statement_id],
                        }
                    ],
                }
            ]
        }
        return json.dumps(payload)


SCENARIOS = tuple(
    product(
        (1, 2, 3),
        ("dimension.d1", "dimension.d2"),
        ("PAIR", "SPAN"),
        (False, True),
        ("SAME_SCOPE", "MUTATE_SCOPE"),
        (2, 3),
        (False, True),
    )
)

assert len(SCENARIOS) == 192


@pytest.mark.parametrize(
    (
        "metric_count",
        "dimension_id",
        "frame",
        "ranking",
        "transition",
        "turn_depth",
        "reverse",
    ),
    SCENARIOS,
)
def test_semantic_authority_collapse_metamorphic_matrix(
    metric_count: int,
    dimension_id: str,
    frame: str,
    ranking: bool,
    transition: str,
    turn_depth: int,
    reverse: bool,
) -> None:
    """Generated provider-free closure over generic semantic authority laws."""

    scope = _scope(
        metric_count=metric_count,
        dimension_id=dimension_id,
        frame=frame,
        reverse=reverse,
    )
    reordered = _scope(
        metric_count=metric_count,
        dimension_id=dimension_id,
        frame=frame,
        reverse=not reverse,
    )

    # Metric/entity tuple order cannot change accepted semantic identity.
    assert scope_fingerprint(
        scope,
        context_version="ctx-semantic-authority-v1",
    ) == scope_fingerprint(
        reordered,
        context_version="ctx-semantic-authority-v1",
    )

    # Repeated identical temporal authority is coalesced, never made ambiguous.
    repeated = resolve_temporal_authority(
        (*scope.periods, *scope.periods)
    )
    assert repeated.periods == scope.periods
    assert repeated.change_frame_mode == (
        TemporalChangeFrameMode.PAIR
        if frame == "PAIR"
        else TemporalChangeFrameMode.SPAN
    )

    contract = _contract(
        scope=scope,
        metric_count=metric_count,
        dimension_id=dimension_id,
        frame=frame,
        ranking=ranking,
        reverse=reverse,
    )
    contract_reordered = _contract(
        scope=reordered,
        metric_count=metric_count,
        dimension_id=dimension_id,
        frame=frame,
        ranking=ranking,
        reverse=not reverse,
    )
    assert contract.material_fingerprint == contract_reordered.material_fingerprint

    question = _question(
        metric_count=metric_count,
        dimension_id=dimension_id,
        ranking=ranking,
        suffix="current",
    )
    intent = project_analytical_intent_v1(
        question=question,
        scope=scope,
        contract=contract,
        tenant_id="tenant.symbolic",
        principal_id="principal.symbolic",
        currentness_token="current.symbolic",
        security_fingerprint="security.symbolic",
    )
    assert intent.operation == (
        AnalyticalOperation.RANK
        if ranking
        else AnalyticalOperation.OBSERVE
    )
    assert set(intent.metrics) == {
        f"metric.m{i}" for i in range(1, metric_count + 1)
    }
    assert set(intent.allowed_semantic_ids) == {
        item.candidate_id for item in scope.semantic_refs
    }

    # The operation enum is a routing hint: OTHER with governed material
    # projects to OBSERVE rather than becoming a capability rejection.
    if not ranking:
        assert question.kind == ResearchGoalKind.OTHER
        assert intent.operation == AnalyticalOperation.OBSERVE

    initial_brief = _brief(
        scope=scope,
        metric_count=metric_count,
        dimension_id=dimension_id,
        ranking=ranking,
        suffix="initial",
        report=False,
    )
    prior_session = SimpleNamespace(
        accepted_brief=initial_brief,
        context_version=initial_brief.context_version,
        lineage_id="lineage.symbolic",
        authority_revision=1,
        authority_id="authority.initial",
    )
    current_scope = scope

    if transition == "MUTATE_SCOPE":
        target_entity = ENTITIES[0]
        resolved = resolve_scope_patch(
            scope,
            TurnScopePatch(
                source_scope_version_id=scope.scope_version.version_id,
                operations=(
                    ScopePatchOperation(
                        facet=ScopePatchFacet.ENTITY,
                        operation=ScopePatchOperationKind.SET,
                        semantic_refs=(target_entity,),
                        source_fragment="restrict governed entity population",
                    ),
                ),
            ),
            context_version=initial_brief.context_version,
        )
        assert resolved.materially_changed is True
        assert (
            resolved.current_scope.scope_version.ordinal
            == scope.scope_version.ordinal + 1
        )
        current_scope = resolved.current_scope
    else:
        assert current_scope.scope_version == scope.scope_version

    # Turn authority revision advances independently from ScopeVersion.
    for turn in range(2, turn_depth + 1):
        current_brief = _brief(
            scope=current_scope,
            metric_count=metric_count,
            dimension_id=dimension_id,
            ranking=ranking,
            suffix=f"turn{turn}",
            report=(transition == "SAME_SCOPE"),
        )
        authority = ResearchBriefAuthoritySealer.seal(
            brief=current_brief,
            request_ref=f"request.turn.{turn}",
            source_message_hash=("a" if turn == 2 else "b") * 64,
            prior_session=prior_session,
        )
        assert authority.version == prior_session.authority_revision + 1
        if transition == "SAME_SCOPE":
            assert current_brief.scope.scope_version.version_id == "scope_v1"
        else:
            assert current_brief.scope.scope_version.version_id == "scope_v2"

        prior_session = SimpleNamespace(
            accepted_brief=current_brief,
            context_version=current_brief.context_version,
            lineage_id=authority.lineage_id,
            authority_revision=authority.version,
            authority_id=authority.contract_id,
        )

    # ROOT_CAUSE does not need duplicate FOLLOW_VERIFIED_MATERIAL authority;
    # ordinary direct work still does.
    adaptive_kind = (
        ResearchGoalKind.ROOT_CAUSE if reverse else ResearchGoalKind.OTHER
    )
    assert adaptive_investigation_authorized(
        goal_kind=adaptive_kind,
        explicit_follow_verified_material=not reverse,
    )
    if adaptive_kind != ResearchGoalKind.ROOT_CAUSE:
        assert not adaptive_investigation_authorized(
            goal_kind=adaptive_kind,
            explicit_follow_verified_material=False,
        )

    # Same-scope report continuation uses one cognition call and has no native
    # or Metabase execution surface. Numeric truth remains in governed source
    # statements rather than free-form synthesis text.
    if transition == "SAME_SCOPE":
        statement_id = "p20s_" + "c" * 24
        requirement_id = "deliverable.synthetic"
        transport = _SynthesisTransport(
            requirement_id=requirement_id,
            statement_id=statement_id,
        )
        manager = StructuredP20SynthesisManager(transport=transport)
        result = manager.synthesize(
            accepted_deliverables=(
                {
                    "requirement_id": requirement_id,
                    "kind": "report",
                    "source_text": "short management report",
                },
            ),
            scope_version_id=current_scope.scope_version.version_id,
            evidence_digests=(
                {
                    "statement_id": statement_id,
                    "statement_kind": "OBSERVATION",
                    "text": "Governed observation.",
                    "payload": {},
                    "upstream_epistemic_ceiling": "EXACT_GOVERNED_OBSERVATION",
                    "source_refs": [{"source_ref": "evidence.synthetic"}],
                },
            ),
            p18_results=(),
            p19_assessment=None,
            limitations=(),
        )
        assert result.deliverables[0].status == "FULFILLED"
        assert transport.call_count == 1
        assert transport.native_call_count == 0
