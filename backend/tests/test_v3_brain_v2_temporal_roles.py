from __future__ import annotations

import json
from types import SimpleNamespace

from app.v3.research_analytical_scope import analytical_scope_contract
from app.v3.research_contracts import (
    CausalEffectObservation,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_intake import (
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
    ResearchIntakeTerminal,
)
from tests.semantic_spec.model import (
    ChangeTemporalDisposition,
    reference_change_temporal_disposition,
)


class FakeTransport:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.call_count = 0

    def structured_json(self, system, user, *, schema, schema_name):
        self.call_count += 1
        return json.dumps({"result": self.payload})


def _metric(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=candidate_id,
        cube_names=("symbolic_cube",),
    )


def _time_dimension(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=candidate_id,
        cube_names=("symbolic_cube",),
    )


def _catalog() -> ResearchIntakeCatalog:
    return ResearchIntakeCatalog(
        context_version="ctx-temporal-law-v1",
        semantic_refs=(
            _metric("metric.effect"),
            _metric("metric.candidate_1"),
            _metric("metric.candidate_2"),
            _time_dimension("dimension.t"),
        ),
        temporal_dimension_ids=("dimension.t",),
    )


def _change_without_explicit_period_payload() -> tuple[str, dict]:
    fragment = (
        "Test the governed candidate explanations for the change in the effect."
    )
    return fragment, {
        "terminal": "READY",
        "objective": fragment,
        "goals": [
            {
                "goal_key": "goal_change",
                "kind": "root_cause",
                "source_text": fragment,
                "source_fragment_text": fragment,
                "subject_semantic_ids": [
                    "metric.effect",
                    "metric.candidate_1",
                    "metric.candidate_2",
                ],
                "related_semantic_ids": [],
                "ranking": None,
                "comparisons": [
                    {
                        "text": "candidate 1",
                        "role": "causal_candidate",
                        "semantic_id": "metric.candidate_1",
                    },
                    {
                        "text": "candidate 2",
                        "role": "causal_candidate",
                        "semantic_id": "metric.candidate_2",
                    },
                ],
                "causal_competition": {
                    "effect_semantic_id": "metric.effect",
                    "effect_observation": "change",
                    "candidate_mechanism_semantic_ids": [
                        "metric.candidate_1",
                        "metric.candidate_2",
                    ],
                    "diagnostic_dimension_ids": [],
                },
                "temporal_material": {"mode": "none"},
            }
        ],
        "deliverables": [],
        "investigation_directives": [],
        "time_periods": [],
        "required_domains": [],
    }


def test_change_without_user_period_uses_governed_time_observation_not_exception() -> None:
    expected = reference_change_temporal_disposition(
        effect_is_change=True,
        explicit_period_count=0,
        governed_temporal_dimension_count=1,
    )
    assert expected == ChangeTemporalDisposition.OBSERVE_GOVERNED_TIME

    question, payload = _change_without_explicit_period_payload()
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=question,
        catalog=_catalog(),
    )

    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.brief is not None
    assert result.brief.scope.periods == ()
    assert result.brief.scope.time_surfaces == ()
    assert result.brief.scope.temporal_dimension_ids == ("dimension.t",)
    assert "dimension.t" in {
        item.candidate_id for item in result.brief.scope.semantic_refs
    }

    goal = result.brief.questions[0]
    assert goal.causal_competition is not None
    assert (
        goal.causal_competition.effect_observation
        == CausalEffectObservation.CHANGE
    )

    session = SimpleNamespace(
        accepted_brief=result.brief,
        authority_id="authority-temporal-law",
        session_id="rs_" + "1" * 24,
        lineage_id="atl-temporal-law",
        context_version=result.brief.context_version,
    )
    contract = analytical_scope_contract(
        session=session,
        obligation_id=goal.goal_id,
    )

    assert contract.period is None
    assert contract.comparison is None
    assert contract.temporal_observation is not None
    assert contract.temporal_observation.kind == "change"
    assert contract.temporal_observation.time_dimension == "dimension.t"
    assert contract.temporal_observation.minimum_distinct_values == 2
