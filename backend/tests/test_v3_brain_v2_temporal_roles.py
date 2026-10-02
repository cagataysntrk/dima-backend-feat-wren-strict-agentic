from __future__ import annotations

import json
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.v3.research_analytical_scope import (
    NativeMaterialBinding,
    ResearchAnalyticalScopeError,
    _assert_material_dimension_scope,
    _assert_material_time_scope,
    analytical_scope_contract,
)
from app.v3.research_material_coverage import (
    ResearchMaterialCoverageError,
    assert_material_result_coverage,
)
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
from app.v3.substrate.metabase.native_models import (
    NativeMaterialDimension,
    NativeMaterialObservation,
    NativeMaterialTemporalScope,
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


def _catalog(
    temporal_dimension_ids: tuple[str, ...] = ("dimension.t",),
) -> ResearchIntakeCatalog:
    return ResearchIntakeCatalog(
        context_version="ctx-temporal-law-v1",
        semantic_refs=(
            _metric("metric.effect"),
            _metric("metric.candidate_1"),
            _metric("metric.candidate_2"),
            _time_dimension("dimension.t"),
            _time_dimension("dimension.t2"),
        ),
        temporal_dimension_ids=temporal_dimension_ids,
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


    coverage = contract.model_dump(mode="json")["temporal_observation"]
    assert coverage["time_dimension"] == "dimension.t"


def test_change_without_user_period_and_multiple_time_axes_clarifies() -> None:
    question, payload = _change_without_explicit_period_payload()

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=question,
        catalog=_catalog(("dimension.t", "dimension.t2")),
    )

    assert result.terminal == ResearchIntakeTerminal.CLARIFY
    assert result.brief is None
    assert result.clarification_question is not None


def test_change_without_user_period_and_no_time_axis_is_unsupported() -> None:
    question, payload = _change_without_explicit_period_payload()

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=question,
        catalog=_catalog(()),
    )

    assert result.terminal == ResearchIntakeTerminal.UNSUPPORTED
    assert result.brief is None
    assert result.unsupported_reason is not None


def _observation(
    *,
    with_breakout: bool = True,
    with_temporal_scope: bool = False,
) -> NativeMaterialObservation:
    return NativeMaterialObservation(
        schema_version="dima_native_material_observation_v1",
        conversation_id=UUID("00000000-0000-4000-8000-000000000707"),
        native_query_id="native-temporal-law",
        assistant_message_id=1,
        tool_call_id="tool-temporal-law",
        query_fingerprint="a" * 64,
        authenticated_metabase_subject=7,
        database_id=1,
        runtime_identity={},
        dimensions=(
            (
                NativeMaterialDimension(
                    stage_number=0,
                    role="breakout",
                    field_id=44,
                    table_id=10,
                    temporal_grain="month",
                ),
            )
            if with_breakout
            else ()
        ),
        temporal_scopes=(
            (
                NativeMaterialTemporalScope(
                    time_field_id=44,
                    table_id=10,
                    lower_bound="2026-01-01",
                    lower_inclusive=True,
                    upper_bound="2026-07-01",
                    upper_inclusive=False,
                ),
            )
            if with_temporal_scope
            else ()
        ),
    )


def _binding() -> dict[str, NativeMaterialBinding]:
    return {
        "dimension.t": NativeMaterialBinding(
            candidate_id="dimension.t",
            candidate_kind="dimension",
            database_id=1,
            table_id=10,
            field_id=44,
        )
    }


def test_observation_only_time_axis_requires_breakout_without_calendar_filter() -> None:
    question, payload = _change_without_explicit_period_payload()
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(question=question, catalog=_catalog())
    assert result.brief is not None
    goal = result.brief.questions[0]
    session = SimpleNamespace(
        accepted_brief=result.brief,
        authority_id="authority-temporal-law",
        session_id="rs_" + "2" * 24,
        lineage_id="atl-temporal-law",
        context_version=result.brief.context_version,
    )
    contract = analytical_scope_contract(
        session=session,
        obligation_id=goal.goal_id,
    )

    observation = _observation()
    identity = _assert_material_time_scope(
        contract,
        observation,
        _binding(),
    )
    assert identity == (44, 10)
    _assert_material_dimension_scope(
        contract,
        observation,
        _binding(),
        time_identity=identity,
    )


def test_observation_only_time_axis_rejects_invented_calendar_filter() -> None:
    question, payload = _change_without_explicit_period_payload()
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(question=question, catalog=_catalog())
    assert result.brief is not None
    goal = result.brief.questions[0]
    session = SimpleNamespace(
        accepted_brief=result.brief,
        authority_id="authority-temporal-law",
        session_id="rs_" + "3" * 24,
        lineage_id="atl-temporal-law",
        context_version=result.brief.context_version,
    )
    contract = analytical_scope_contract(
        session=session,
        obligation_id=goal.goal_id,
    )

    with pytest.raises(ResearchAnalyticalScopeError) as exc:
        _assert_material_time_scope(
            contract,
            _observation(with_temporal_scope=True),
            _binding(),
        )
    assert exc.value.code == "R1_NATIVE_TEMPORAL_SCOPE_MISMATCH"


def test_unbounded_change_result_requires_two_distinct_governed_time_values() -> None:
    question, payload = _change_without_explicit_period_payload()
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(question=question, catalog=_catalog())
    assert result.brief is not None
    goal = result.brief.questions[0]
    session = SimpleNamespace(
        accepted_brief=result.brief,
        authority_id="authority-temporal-law",
        session_id="rs_" + "4" * 24,
        lineage_id="atl-temporal-law",
        context_version=result.brief.context_version,
    )
    contract = analytical_scope_contract(
        session=session,
        obligation_id=goal.goal_id,
    )
    good = {
        "data": {
            "cols": [
                {
                    "display_name": "Governed Time",
                    "field_ref": ["field", 44, {"temporal-unit": "month"}],
                },
                {"display_name": "Effect"},
            ],
            "rows": [
                ["2026-01-01", 10],
                ["2026-02-01", 12],
            ],
        }
    }

    coverage = assert_material_result_coverage(
        contract=contract,
        result_payload=good,
        bindings=_binding(),
    )
    assert coverage.status == "FULL"
    assert coverage.observed_temporal_value_count == 2

    one_value = {
        "data": {
            "cols": good["data"]["cols"],
            "rows": [
                ["2026-01-01", 10],
                ["2026-01-01", 12],
            ],
        }
    }
    with pytest.raises(ResearchMaterialCoverageError) as exc:
        assert_material_result_coverage(
            contract=contract,
            result_payload=one_value,
            bindings=_binding(),
        )
    assert exc.value.code == "R1_RESULT_CHANGE_COVERAGE_INCOMPLETE"
