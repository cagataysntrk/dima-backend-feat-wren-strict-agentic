from __future__ import annotations

import json
from uuid import UUID

import httpx
import pytest

from app.v3.product.contracts import (
    ProductErrorCode,
    ProductInvestigationRequirementKind,
)
from app.v3.product.errors import ProductError
from app.v3.product.service import HeadlessProductService, ProductSources
from app.v3.research_contracts import (
    CausalCompetitionSurface,
    ComparisonRole,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
    TemporalRole,
)
from app.v3.research_intake import (
    AllowedRelationship,
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
    ResearchIntakeError,
    ResearchIntakeTerminal,
    _followup_scope_provider_schema,
    _intake_provider_schema,
)
from app.v3.structured_transport import (
    OpenRouterStructuredJSONTransport,
    StructuredProviderError,
    strict_json_schema,
)
from control_plane.authorize import Principal


TENANT = UUID("00000000-0000-4000-8000-000000006701")
USER = UUID("00000000-0000-4000-8000-000000006702")


def principal(*, user: str | None = None):
    return Principal(
        user_id=str(USER) if user is None else user,
        tenant_id=str(TENANT),
        roles=["analyst"],
        tenant_slug="core-b-live",
    )


def metric(cid: str, name: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def dimension(cid: str, name: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def catalog() -> ResearchIntakeCatalog:
    return ResearchIntakeCatalog(
        context_version="ctx-core-b-neutral-v1",
        semantic_refs=(
            metric("metric.downtime", "Machine Downtime Minutes"),
            metric("metric.fault_count", "Fault Count"),
            metric("metric.performance", "Performance Score"),
            dimension("dimension.department", "Department"),
            dimension("dimension.event_date", "Event Date"),
            dimension("dimension.machine_id", "Machine"),
        ),
        allowed_relationships=(
            AllowedRelationship(
                relationship_id="rel.downtime_fault_by_department",
                left_semantic_id="metric.downtime",
                right_semantic_id="metric.fault_count",
                dimension_semantic_id="dimension.department",
            ),
            AllowedRelationship(
                relationship_id="rel.downtime_performance_by_department",
                left_semantic_id="metric.downtime",
                right_semantic_id="metric.performance",
                dimension_semantic_id="dimension.department",
            ),
        ),
        supported_domains=("machine_operations",),
    )


class FakeTransport:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls: list[dict] = []
        self.call_count = 0

    def structured_json(self, system, user, *, schema, schema_name):
        self.call_count += 1
        self.calls.append(
            {
                "system": system,
                "user": json.loads(user),
                "schema": schema,
                "schema_name": schema_name,
            }
        )
        return json.dumps({"result": self.payload})


class SequenceTransport:
    def __init__(self, payloads: list[dict]):
        self.payloads = list(payloads)
        self.calls: list[dict] = []
        self.call_count = 0

    def structured_json(self, system, user, *, schema, schema_name):
        if self.call_count >= len(self.payloads):
            raise AssertionError("unexpected extra intake provider call")
        payload = self.payloads[self.call_count]
        self.call_count += 1
        self.calls.append(
            {
                "system": system,
                "user": json.loads(user),
                "schema": schema,
                "schema_name": schema_name,
            }
        )
        return json.dumps({"result": payload})


def ready_payload(
    *,
    kind="breakdown",
    subject=("metric.downtime",),
    related=("dimension.department",),
):
    return {
        "terminal": "READY",
        "objective": "Inspect the current governed analytical request.",
        "goals": [
            {
                "goal_key": "g-current",
                "kind": kind,
                "source_text": "Inspect the requested governed analytical scope.",
                "subject_semantic_ids": list(subject),
                "related_semantic_ids": list(related),
                "ranking": None,
                "comparisons": [],
            }
        ],
        "deliverables": [],
        "investigation_directives": [],
        "required_domains": ["machine_operations"],
    }


def test_causal_competition_is_one_root_cause_goal_not_relationship_query_plan():
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    fragment = (
        "Determine which governed explanation better accounts for the outcome "
        "and preserve supporting and challenging evidence."
    )
    payload["goals"][0]["source_text"] = fragment
    payload["goals"][0]["source_fragment_text"] = fragment
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": [
            "metric.fault_count",
            "metric.performance",
        ],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    transport = FakeTransport(payload)

    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(
        question=fragment,
        catalog=catalog(),
    )

    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.brief is not None
    assert len(result.brief.questions) == 1
    goal = result.brief.questions[0]
    assert goal.kind == ResearchGoalKind.ROOT_CAUSE
    assert {item.candidate_id for item in goal.subject_refs} == {
        "metric.downtime",
        "metric.fault_count",
        "metric.performance",
    }
    assert tuple(item.candidate_id for item in goal.related_refs) == (
        "dimension.department",
    )
    assert goal.causal_competition == CausalCompetitionSurface(
        effect_semantic_id="metric.downtime",
        candidate_mechanism_semantic_ids=(
            "metric.fault_count",
            "metric.performance",
        ),
        diagnostic_dimension_ids=("dimension.department",),
    )
    system = transport.calls[0]["system"]
    assert "Do NOT manufacture separate RELATIONSHIP goals" in system
    assert "P17/P19 own governed hypothesis competition" in system


def test_typed_causal_surface_canonicalizes_required_refs_into_goal_scope():
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.event_date",),
    )
    fragment = "Evaluate two governed explanations within the accepted diagnostic scope."
    payload["goals"][0]["source_text"] = fragment
    payload["goals"][0]["source_fragment_text"] = fragment
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": [
            "metric.fault_count",
            "metric.performance",
        ],
        "diagnostic_dimension_ids": [
            "dimension.department",
            "dimension.event_date",
        ],
    }
    transport = FakeTransport(payload)

    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(
        question=fragment,
        catalog=catalog(),
    )

    assert result.brief is not None
    assert transport.call_count == 1
    goal = result.brief.questions[0]
    assert tuple(item.candidate_id for item in goal.subject_refs) == (
        "metric.downtime",
        "metric.fault_count",
        "metric.performance",
    )
    assert tuple(item.candidate_id for item in goal.related_refs) == (
        "dimension.event_date",
        "dimension.department",
    )
    assert goal.causal_competition == CausalCompetitionSurface(
        effect_semantic_id="metric.downtime",
        candidate_mechanism_semantic_ids=(
            "metric.fault_count",
            "metric.performance",
        ),
        diagnostic_dimension_ids=(
            "dimension.department",
            "dimension.event_date",
        ),
    )


def test_duplicate_root_cause_identity_fails_closed_without_stochastic_repair():
    first_clause = "Determine which governed explanation better accounts for downtime."
    second_clause = "Keep supporting and challenging evidence separate."
    question = first_clause + " " + second_clause
    causal = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": [
            "metric.fault_count",
            "metric.performance",
        ],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    bad = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    bad["goals"][0].update(
        {
            "goal_key": "g-causal-main",
            "source_text": first_clause,
            "source_fragment_text": first_clause,
            "causal_competition": causal,
        }
    )
    duplicate = dict(bad["goals"][0])
    duplicate["goal_key"] = "g-causal-evidence"
    duplicate["source_text"] = second_clause
    duplicate["source_fragment_text"] = second_clause
    bad["goals"].append(duplicate)
    transport = FakeTransport(bad)

    with pytest.raises(
        ResearchIntakeError,
        match="INTAKE_DUPLICATE_ANALYTICAL_GOAL",
    ):
        ResearchIntakeCompiler(
            transport=transport,
            calendar_reference_date="2026-09-30",
        ).compile(
            question=question,
            catalog=catalog(),
        )

    assert transport.call_count == 1


def test_non_executable_other_subgoal_fully_covered_by_one_root_cause_is_absorbed():
    clause = "Determine which governed explanation better accounts for downtime."
    evidence_clause = "Preserve the governed evidence needed to assess the alternatives."
    question = clause + " " + evidence_clause
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-causal-main",
            "source_text": clause,
            "source_fragment_text": clause,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-evidence-handling",
            "kind": "other",
            "source_text": evidence_clause,
            "source_fragment_text": evidence_clause,
            "subject_semantic_ids": [
                "metric.downtime",
                "metric.fault_count",
            ],
            "related_semantic_ids": ["dimension.department"],
            "ranking": None,
            "comparisons": [],
            "causal_competition": None,
        }
    )
    transport = FakeTransport(payload)

    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(
        question=question,
        catalog=catalog(),
    )

    assert result.brief is not None
    assert transport.call_count == 1
    assert len(result.brief.questions) == 1
    assert result.brief.questions[0].kind == ResearchGoalKind.ROOT_CAUSE



def test_zero_ref_other_instruction_is_not_a_second_analytical_goal_beside_one_root():
    root_clause = "Assess which governed mechanism better explains the accepted effect."
    routing_clause = "If evidence stays ambiguous, preserve the bounded follow-up instruction."
    question = root_clause + " " + routing_clause
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.fault_count",
            "metric.downtime",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-root",
            "source_text": root_clause,
            "source_fragment_text": root_clause,
            "causal_competition": {
                "effect_semantic_id": "metric.fault_count",
                "candidate_mechanism_semantic_ids": [
                    "metric.downtime",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-routing-only",
            "kind": "other",
            "source_text": routing_clause,
            "source_fragment_text": routing_clause,
            "subject_semantic_ids": [],
            "related_semantic_ids": [],
            "ranking": None,
            "comparisons": [],
            "causal_competition": None,
        }
    )
    payload["investigation_directives"] = [
        {
            "key": "follow-if-needed",
            "kind": "FOLLOW_VERIFIED_MATERIAL",
            "source_goal_key": "g-root",
            "source_text": routing_clause,
        }
    ]

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload),
        calendar_reference_date="2026-09-30",
    ).compile(
        question=question,
        catalog=catalog(),
    )

    assert result.brief is not None
    assert len(result.brief.questions) == 1
    assert result.brief.questions[0].kind == ResearchGoalKind.ROOT_CAUSE
    assert len(result.investigation_requirements) == 1
    assert (
        result.investigation_requirements[0].kind
        == ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL
    )
    assert (
        result.investigation_requirements[0].source_goal_id
        == result.brief.questions[0].goal_id
    )


def test_other_goal_with_distinct_governed_scope_is_not_absorbed_into_root_cause():
    clause = "Determine which governed explanation better accounts for downtime."
    separate_clause = "Also inspect machine-level context."
    question = clause + " " + separate_clause
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-causal-main",
            "source_text": clause,
            "source_fragment_text": clause,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-machine-context",
            "kind": "other",
            "source_text": separate_clause,
            "source_fragment_text": separate_clause,
            "subject_semantic_ids": ["metric.downtime"],
            "related_semantic_ids": ["dimension.machine_id"],
            "ranking": None,
            "comparisons": [],
            "causal_competition": None,
        }
    )

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload),
        calendar_reference_date="2026-09-30",
    ).compile(
        question=question,
        catalog=catalog(),
    )

    assert result.brief is not None
    assert tuple(item.kind for item in result.brief.questions) == (
        ResearchGoalKind.ROOT_CAUSE,
        ResearchGoalKind.OTHER,
    )


def test_ready_breakdown_compiles_to_typed_research_brief():
    transport = FakeTransport(ready_payload())
    compiler = ResearchIntakeCompiler(transport=transport)
    result = compiler.compile(
        question="Show machine downtime by department.",
        catalog=catalog(),
    )
    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.model_calls == 1
    assert result.brief is not None
    brief = result.brief
    assert brief.status == ResearchBriefStatus.READY_FOR_RESEARCH
    assert len(brief.questions) == 1
    question = brief.questions[0]
    assert question.kind == ResearchGoalKind.BREAKDOWN
    assert question.subject_refs[0].candidate_id == "metric.downtime"
    assert question.related_refs[0].candidate_id == "dimension.department"
    assert brief.must_requirement_ids == (question.goal_id,)


def test_ranking_provider_schema_closes_basis_to_governed_metrics_or_null():
    schema=_intake_provider_schema(catalog())
    draft=schema["$defs"]["DraftRanking"]
    basis=draft["properties"]["measure_semantic_id"]["anyOf"]
    assert basis == [
        {
            "type":"string",
            "enum":[
                "metric.downtime",
                "metric.fault_count",
                "metric.performance",
            ],
        },
        {"type":"null"},
    ]


def test_multi_metric_ranking_without_explicit_basis_preserves_synthesis_intent():
    payload=ready_payload(
        kind="ranking",
        subject=("metric.downtime","metric.fault_count"),
        related=("dimension.department",),
    )
    payload["goals"][0]["ranking"]={
        "direction":"desc",
        "limit":None,
        "measure_semantic_id":None,
        "source_text":"Rank deterioration by department.",
    }
    result=ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Compare downtime and fault count and rank deterioration.",
        catalog=catalog(),
    )
    assert result.brief is not None
    ranking=result.brief.questions[0].ranking
    assert ranking is not None
    assert ranking.direction == "desc"
    assert ranking.limit is None
    assert ranking.measure_semantic_id is None


def test_ranking_basis_must_belong_to_the_current_goal_metric_scope():
    payload=ready_payload(
        kind="ranking",
        subject=("metric.downtime","metric.fault_count"),
        related=("dimension.department",),
    )
    payload["goals"][0]["ranking"]={
        "direction":"desc",
        "limit":3,
        "measure_semantic_id":"metric.performance",
        "source_text":"Rank by governed metric.",
    }
    with pytest.raises(
        ResearchIntakeError,
        match="INTAKE_RANKING_MEASURE_OUTSIDE_GOAL_SCOPE",
    ):
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Rank downtime and faults by one governed basis.",
            catalog=catalog(),
        )


def test_adaptive_intent_compiles_to_core_b_requirement_not_second_p14_goal():
    payload = ready_payload()
    payload["deliverables"] = [
        {
            "key": "report-current",
            "kind": "report",
            "source_text": "Produce a governed report.",
        }
    ]
    payload["investigation_directives"] = [
        {
            "key": "follow-material",
            "kind": "FOLLOW_VERIFIED_MATERIAL",
            "source_goal_key": "g-current",
            "source_text": (
                "If verified evidence reveals a new material direction, "
                "follow that direction."
            ),
        }
    ]
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=(
            "Makine duruşlarını bölüm bazında araştır; doğrulanmış kanıt "
            "yeni ve maddi bir bölüm kırılımı gösterirse o yönü takip et "
            "ve raporla."
        ),
        catalog=catalog(),
    )
    assert result.brief is not None
    assert len(result.brief.questions) == 1
    source_goal = result.brief.questions[0]
    assert source_goal.kind == ResearchGoalKind.BREAKDOWN
    assert len(result.investigation_requirements) == 1
    requirement = result.investigation_requirements[0]
    assert (
        requirement.kind
        == ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL
    )
    assert requirement.source_goal_id == source_goal.goal_id
    assert requirement.requirement_id.startswith("pir_")
    assert result.brief.must_requirement_ids == (
        source_goal.goal_id,
        result.brief.deliverables[0].requirement_id,
    )


def test_adaptive_dependency_unknown_goal_key_fails_closed():
    payload = ready_payload()
    payload["investigation_directives"] = [
        {
            "key": "follow-material",
            "kind": "FOLLOW_VERIFIED_MATERIAL",
            "source_goal_key": "not-a-current-goal",
            "source_text": "Follow verified material if warranted.",
        }
    ]
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Follow a bounded verified direction.",
            catalog=catalog(),
        )
    assert exc.value.code == "INTAKE_INVESTIGATION_SOURCE_UNKNOWN"


def test_authorized_relationship_compiles_and_preserves_exact_catalog_refs():
    payload = ready_payload(
        kind="relationship",
        subject=(),
        related=(),
    )
    payload["goals"][0]["allowed_relationship_id"] = (
        "rel.downtime_fault_by_department"
    )
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Inspect downtime and fault count by department.",
        catalog=catalog(),
    )
    assert result.brief is not None
    refs = {
        item.candidate_id
        for item in (
            *result.brief.questions[0].subject_refs,
            *result.brief.questions[0].related_refs,
        )
    }
    assert refs == {
        "metric.downtime",
        "metric.fault_count",
        "dimension.department",
    }


def test_unapproved_relationship_fails_closed():
    payload = ready_payload(
        kind="relationship",
        subject=(),
        related=(),
    )
    payload["goals"][0]["allowed_relationship_id"] = "rel.invented"
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Inspect an unapproved relationship.",
            catalog=catalog(),
        )
    assert exc.value.code == "INTAKE_RELATIONSHIP_UNAUTHORIZED"


def test_unknown_semantic_ref_fails_closed():
    payload = ready_payload(subject=("metric.not_in_catalog",))
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Use an unknown metric.",
            catalog=catalog(),
        )
    assert exc.value.code == "INTAKE_UNKNOWN_SEMANTIC_REF"


@pytest.mark.parametrize(
    ("payload", "terminal", "field"),
    [
        (
            {
                "terminal": "CLARIFY",
                "clarification_question": "Which metric do you mean?",
            },
            ResearchIntakeTerminal.CLARIFY,
            "clarification_question",
        ),
        (
            {
                "terminal": "UNSUPPORTED",
                "unsupported_reason": "Requested fact is absent from governed data.",
            },
            ResearchIntakeTerminal.UNSUPPORTED,
            "unsupported_reason",
        ),
    ],
)
def test_bounded_non_executable_terminal_states(payload, terminal, field):
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="A request that cannot legally enter analytics.",
        catalog=catalog(),
    )
    assert result.terminal == terminal
    assert result.brief is None
    assert getattr(result, field)


def _temporal_catalog() -> ResearchIntakeCatalog:
    return catalog().model_copy(
        update={"temporal_dimension_ids": ("dimension.event_date",)}
    )


def test_temporal_only_clarification_gets_one_bounded_calendar_reconsideration():
    first = {
        "terminal": "CLARIFY",
        "clarification_question": "Which year do May and June refer to?",
    }
    second = ready_payload(
        kind="comparison",
        subject=("metric.downtime",),
        related=("dimension.department",),
    )
    second["time_periods"] = [
        {
            "source_text": "May-June",
            "time_dimension_semantic_id": "dimension.event_date",
            "start": "2026-05-01",
            "end": "2026-07-01",
        }
    ]
    transport = SequenceTransport([first, second])
    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(
        question="Compare May-June downtime by department.",
        catalog=_temporal_catalog(),
    )
    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.model_calls == 2
    assert result.brief is not None
    assert result.brief.scope.periods[0].start == "2026-05-01"
    assert result.brief.scope.periods[0].end == "2026-07-01"
    assert transport.calls[0]["user"]["calendar_reference_date"] == "2026-09-30"
    assert (
        transport.calls[1]["user"]["reconsideration"]["kind"]
        == "TEMPORAL_CLARIFICATION_ONLY"
    )


def test_non_temporal_clarification_remains_fail_closed_after_bounded_reconsideration():
    clarify = {
        "terminal": "CLARIFY",
        "clarification_question": "Which governed metric do you mean?",
    }
    transport = SequenceTransport([clarify, clarify])
    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(
        question="Compare the important metric by department.",
        catalog=_temporal_catalog(),
    )
    assert result.terminal == ResearchIntakeTerminal.CLARIFY
    assert result.model_calls == 2
    assert result.brief is None


def test_single_domain_report_only_intent_gets_one_grounded_overview_reconsideration():
    first = {
        "terminal": "UNSUPPORTED",
        "unsupported_reason": "No explicit analytical subject was selected.",
    }
    second = ready_payload(
        kind="breakdown",
        subject=("metric.downtime", "metric.fault_count"),
        related=("dimension.department",),
    )
    second["deliverables"] = [
        {
            "key": "management-report",
            "kind": "report",
            "source_text": "Produce an evidence-backed management report.",
        }
    ]
    transport = SequenceTransport([first, second])
    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(
        question=(
            "Produce an evidence-backed management report over the governed "
            "operational domain and preserve limitations."
        ),
        catalog=catalog(),
    )
    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.model_calls == 2
    assert result.brief is not None
    assert result.brief.deliverables[0].kind.value == "report"
    assert (
        transport.calls[1]["user"]["reconsideration"]["kind"]
        == "SINGLE_DOMAIN_GROUNDED_OVERVIEW"
    )
    assert (
        transport.calls[1]["user"]["reconsideration"]["supported_domain"]
        == "machine_operations"
    )


def test_single_domain_reconsideration_cannot_rescue_absent_concepts():
    unsupported = {
        "terminal": "UNSUPPORTED",
        "unsupported_reason": (
            "Requested psychological and predictive concepts are absent from "
            "the grounded catalog."
        ),
    }
    transport = SequenceTransport([unsupported, unsupported])
    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(
        question="Predict employee morale from unavailable psychological data.",
        catalog=catalog(),
    )
    assert result.terminal == ResearchIntakeTerminal.UNSUPPORTED
    assert result.model_calls == 2
    assert result.brief is None


def test_calendar_reference_date_must_be_iso_date():
    with pytest.raises(
        ResearchIntakeError,
        match="INTAKE_CALENDAR_REFERENCE_INVALID",
    ):
        ResearchIntakeCompiler(
            transport=FakeTransport(ready_payload()),
            calendar_reference_date="September 30",
        )


def prior_brief() -> ResearchBrief:
    downtime = catalog().semantic_refs[0]
    faults = catalog().semantic_refs[1]
    dept = catalog().semantic_refs[3]
    q1 = ResearchQuestion(
        goal_id="g_prior_downtime",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Prior downtime obligation.",
        subject_refs=(downtime,),
        related_refs=(dept,),
        status=ResearchGoalStatus.RESOLVED,
    )
    q2 = ResearchQuestion(
        goal_id="g_prior_faults",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Prior fault obligation.",
        subject_refs=(faults,),
        related_refs=(dept,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb_prior",
        objective="Prior combined request.",
        scope=ResearchScope(semantic_refs=(downtime, faults, dept)),
        questions=(q1, q2),
        must_requirement_ids=(q1.goal_id, q2.goal_id),
        context_version="ctx-core-b-neutral-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def test_followup_scope_patch_rejects_ungrounded_current_turn_fragment():
    payload = {
        "terminal": "READY",
        "operations": [
            {
                "facet": "METRIC",
                "operation": "SET",
                "semantic_ids": ["metric.downtime"],
                "source_fragment": "use downtime from some other message",
            }
        ],
    }
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Keep this investigation otherwise unchanged.",
            catalog=catalog(),
            prior_brief=prior_brief(),
        )

    assert exc.value.code == "INTAKE_SCOPE_PATCH_SOURCE_UNGROUNDED"


def test_followup_scope_patch_noop_inherits_prior_scope_without_new_version():
    prior = prior_brief()
    result = ResearchIntakeCompiler(
        transport=FakeTransport(
            {
                "terminal": "READY",
                "operations": [],
            }
        )
    ).compile(
        question="Report this without changing the analytical scope.",
        catalog=catalog(),
        prior_brief=prior,
    )

    assert result.brief is not None
    assert result.scope_contract is None
    assert result.brief.scope == prior.scope
    assert (
        result.brief.scope.scope_version.version_id
        == prior.scope.scope_version.version_id
    )
    assert result.brief.scope_fingerprint == prior.scope_fingerprint


def test_explicit_repair_does_not_restore_removed_prior_obligation():
    payload = {
        "terminal": "READY",
        "operations": [
            {
                "facet": "METRIC",
                "operation": "SET",
                "semantic_ids": ["metric.downtime"],
                "source_fragment": "include downtime only",
            }
        ],
    }
    transport = FakeTransport(payload)
    result = ResearchIntakeCompiler(
        transport=transport
    ).compile(
        question=(
            "Correction: include downtime only; exclude fault count "
            "from the current request."
        ),
        catalog=catalog(),
        prior_brief=prior_brief(),
    )
    assert result.brief is not None
    refs = {
        ref.candidate_id
        for question in result.brief.questions
        for ref in (*question.subject_refs, *question.related_refs)
    }
    assert "metric.downtime" in refs
    assert "metric.fault_count" not in refs
    assert result.scope_contract is not None
    assert result.brief.scope.scope_version.version_id == "scope_v2"
    assert result.brief.scope.scope_version.parent_version_id == "scope_v1"
    sent = transport.calls[0]["user"]
    prior = sent["prior_brief"]
    assert prior["context_version"] == "ctx-core-b-neutral-v1"
    assert prior["scope"]["semantic_ids"] == [
        "dimension.department",
        "metric.downtime",
        "metric.fault_count",
    ]
    serialized_prior = json.dumps(prior, sort_keys=True)
    for machine_owned in (
        "brief_id",
        "goal_id",
        "requirement_id",
        "scope_version",
        "native_verification_bindings",
        "must_requirement_ids",
        "budget",
    ):
        assert machine_owned not in serialized_prior
    assert "CURRENT-turn scope delta" in sent["instruction"]
    assert "Absent facets inherit from prior scope" in sent["instruction"]


def test_provider_catalog_contains_semantic_choices_not_runtime_binding_state():
    payload = ResearchIntakeCompiler._catalog_payload(catalog())
    serialized = json.dumps(payload, sort_keys=True)
    assert "candidate_id" in serialized
    assert "canonical_name" in serialized
    assert "cube_names" not in serialized
    assert "sensitive" not in serialized
    assert "native_verification_bindings" not in serialized


def test_intake_schema_is_strict_for_every_object():
    schema = strict_json_schema(
        __import__(
            "app.v3.research_intake",
            fromlist=["ModelResearchBriefDraft"],
        ).ModelResearchBriefDraft
    )

    def visit(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False
                props = node.get("properties") or {}
                assert set(node.get("required") or ()) == set(props)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)


def test_openrouter_transport_uses_strict_json_schema_without_model_cascade():
    seen = {}

    def handler(request: httpx.Request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["Authorization"]
        seen["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(ready_payload())
                        }
                    }
                ]
            },
        )

    transport = OpenRouterStructuredJSONTransport(
        api_key="secret-test-key",
        model="openai/gpt-5.6-luna",
        transport=httpx.MockTransport(handler),
    )
    with transport:
        raw = transport.structured_json(
            "system",
            "user",
            schema={"type": "object", "properties": {}, "additionalProperties": False},
            schema_name="test_schema",
        )
    assert json.loads(raw)["terminal"] == "READY"
    assert transport.call_count == 1
    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["auth"] == "Bearer secret-test-key"
    payload = seen["payload"]
    assert payload["model"] == "openai/gpt-5.6-luna"
    assert payload["provider"] == {"require_parameters": True}
    assert payload["reasoning_effort"] == "none"
    assert "reasoning" not in payload
    assert payload["max_completion_tokens"] == 4096
    assert "max_tokens" not in payload
    assert payload["response_format"]["type"] == "json_schema"
    assert "temperature" not in payload
    assert "secret-test-key" not in json.dumps(payload)


def test_headless_product_checks_principal_before_paid_intake_call():
    transport = FakeTransport(ready_payload())
    compiler = ResearchIntakeCompiler(transport=transport)
    service = HeadlessProductService(
        sources=ProductSources(
            research=object(),  # not used by this bounded product seam
            intake=compiler,
        )
    )
    with pytest.raises(ProductError) as exc:
        service.research_question(
            question="Show downtime.",
            catalog=catalog(),
            principal=principal(user=""),
        )
    assert exc.value.code == ProductErrorCode.FORBIDDEN
    assert transport.call_count == 0


def test_product_normalization_preserves_exact_structured_transport_owner_code():
    class ExhaustedTransport:
        call_count = 0

        def structured_json(self, system, user, *, schema, schema_name):
            del system, user, schema, schema_name
            self.call_count += 1
            raise StructuredProviderError(
                "COGNITION_OUTPUT_BUDGET_EXHAUSTED",
                "provider exhausted the structured completion budget before content",
            )

    service = HeadlessProductService(
        sources=ProductSources(
            research=object(),
            intake=ResearchIntakeCompiler(
                transport=ExhaustedTransport()
            ),
        )
    )
    with pytest.raises(ProductError) as caught:
        service.research_question(
            question="Rank the first three departments by downtime.",
            catalog=catalog(),
            principal=principal(),
        )

    assert caught.value.code == ProductErrorCode.UNAVAILABLE
    diagnostic = caught.value.diagnostic
    assert diagnostic is not None
    assert diagnostic.owner == "RESEARCH_INTAKE"
    assert (
        diagnostic.owner_error_code
        == "COGNITION_OUTPUT_BUDGET_EXHAUSTED"
    )


def test_headless_product_delegates_raw_question_to_intake_owner():
    transport = FakeTransport(ready_payload())
    service = HeadlessProductService(
        sources=ProductSources(
            research=object(),
            intake=ResearchIntakeCompiler(transport=transport),
        )
    )
    result = service.research_question(
        question="Show downtime by department.",
        catalog=catalog(),
        principal=principal(),
    )
    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.brief is not None
    assert transport.call_count == 1



def test_request_scoped_intake_schema_closes_authority_ids_before_domain_execution():
    schema = _intake_provider_schema(catalog())
    goal = schema["$defs"]["ModelGoalDraft"]
    variants = goal["anyOf"]
    relationship = next(
        item
        for item in variants
        if item["properties"]["kind"]["enum"] == ["relationship"]
    )
    assert set(relationship["properties"]) == {
        "goal_key",
        "source_text",
        "source_fragment_text",
        "ranking",
        "comparisons",
        "kind",
        "allowed_relationship_id",
        "relationship_intent",
    }
    assert relationship["properties"]["allowed_relationship_id"]["enum"] == [
        "rel.downtime_fault_by_department",
        "rel.downtime_performance_by_department",
    ]
    assert "subject_semantic_ids" not in relationship["properties"]
    assert "related_semantic_ids" not in relationship["properties"]
    assert "causal_competition" not in relationship["properties"]

    root_cause = next(
        item
        for item in variants
        if item["properties"]["kind"]["enum"] == ["root_cause"]
    )
    assert "causal_competition" in root_cause["properties"]
    assert "temporal_material" in root_cause["properties"]
    assert "temporal_material" in root_cause["required"]
    temporal_variants = root_cause["properties"]["temporal_material"]["anyOf"]
    temporal_defs = [
        schema["$defs"][item["$ref"].rsplit("/", 1)[-1]]
        for item in temporal_variants
    ]
    assert {
        item["properties"]["mode"]["const"]
        for item in temporal_defs
    } == {"none", "window", "comparison"}
    by_mode = {
        item["properties"]["mode"]["const"]: item
        for item in temporal_defs
    }
    assert set(by_mode["none"]["properties"]) == {"mode"}
    assert set(by_mode["window"]["properties"]) == {"mode", "window"}
    assert set(by_mode["comparison"]["properties"]) == {
        "mode",
        "baseline_period",
        "comparison_period",
    }
    causal_ref = root_cause["properties"]["causal_competition"]["$ref"]
    causal = schema["$defs"][causal_ref.rsplit("/", 1)[-1]]
    assert set(causal["properties"]["effect_semantic_id"]["enum"]) == {
        "metric.downtime",
        "metric.fault_count",
        "metric.performance",
    }
    assert set(
        causal["properties"]["diagnostic_dimension_ids"]["items"]["enum"]
    ) == {
        "dimension.department",
        "dimension.event_date",
        "dimension.machine_id",
    }

    breakdown = next(
        item
        for item in variants
        if item["properties"]["kind"]["enum"] == ["breakdown"]
    )
    legal_ids = {
        item.candidate_id for item in catalog().semantic_refs
    }
    assert set(
        breakdown["properties"]["subject_semantic_ids"]["items"]["enum"]
    ) == legal_ids
    assert set(
        breakdown["properties"]["related_semantic_ids"]["items"]["enum"]
    ) == legal_ids


def test_provider_intake_schema_is_terminal_payload_not_domain_kitchen_sink():
    schema = _intake_provider_schema(catalog())
    assert set(schema["properties"]) == {"result"}
    result_schema = schema["properties"]["result"]
    refs = {
        item["$ref"].rsplit("/", 1)[-1]
        for item in result_schema["anyOf"]
        if "$ref" in item
    }
    assert refs == {
        "ModelReadyResearchIntake",
        "ModelClarifyResearchIntake",
        "ModelUnsupportedResearchIntake",
    }

    ready = schema["$defs"]["ModelReadyResearchIntake"]
    ready_props = set(ready["properties"])
    assert "time_surfaces" not in ready_props
    assert "time_periods" not in ready_props
    assert "scope_mutation_kind" not in ready_props
    assert "clarification_question" not in ready_props
    assert "unsupported_reason" not in ready_props
    assert "native_verification_bindings" not in json.dumps(schema)
    assert "scope_version" not in json.dumps(schema)
    assert "lineage_id" not in json.dumps(schema)


def test_followup_scope_schema_exposes_patch_facets_not_mutation_kind():
    base = catalog()
    temporal = ResearchIntakeCatalog(
        context_version=base.context_version,
        semantic_refs=base.semantic_refs,
        allowed_relationships=base.allowed_relationships,
        supported_domains=base.supported_domains,
        temporal_dimension_ids=("dimension.event_date",),
    )
    schema = _followup_scope_provider_schema(temporal)
    ready = schema["$defs"]["ModelReadyFollowupScopePatch"]
    assert set(ready["properties"]) == {"terminal", "operations"}
    serialized = json.dumps(schema, sort_keys=True)
    assert "scope_mutation_kind" not in serialized
    assert "source_scope_version_id" not in serialized
    operation = schema["$defs"]["ModelScopePatchOperationDraft"]
    facets = {
        item["properties"]["facet"]["enum"][0]
        for item in operation["anyOf"]
    }
    assert facets == {"ENTITY", "PERIOD", "METRIC", "BREAKDOWN"}


def _r6_temporal_catalog() -> ResearchIntakeCatalog:
    base = catalog()
    return ResearchIntakeCatalog(
        context_version=base.context_version,
        semantic_refs=base.semantic_refs,
        allowed_relationships=base.allowed_relationships,
        supported_domains=base.supported_domains,
        temporal_dimension_ids=("dimension.event_date",),
    )


def _r6_period(
    source_text: str,
    start: str,
    end: str,
    *,
    dimension_id: str = "dimension.event_date",
    role: str = "material_window",
) -> dict:
    return {
        "source_text": source_text,
        "time_dimension_semantic_id": dimension_id,
        "start": start,
        "end": end,
        "role": role,
    }


def test_r6_single_bounded_period_derives_scope_surface_from_typed_period():
    payload = ready_payload()
    payload["time_periods"] = [
        _r6_period("June 2026", "2026-06-01", "2026-07-01")
    ]
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Inspect June downtime by department.",
        catalog=_r6_temporal_catalog(),
    )
    assert result.brief is not None
    assert result.brief.scope.time_surfaces == ("June 2026",)
    assert [
        (
            item.time_dimension_candidate_id,
            item.start,
            item.end,
        )
        for item in result.brief.scope.periods
    ] == [
        ("dimension.event_date", "2026-06-01", "2026-07-01")
    ]


def test_r6_multi_period_comparison_preserves_two_typed_half_open_periods():
    payload = ready_payload(
        kind="comparison",
        subject=("metric.downtime", "metric.fault_count"),
    )
    payload["goals"][0]["comparisons"] = [
        {
            "text": "May versus June",
            "role": "temporal_period",
            "semantic_id": None,
        }
    ]
    payload["time_periods"] = [
        _r6_period(
            "May 2026",
            "2026-05-01",
            "2026-06-01",
            role="baseline_period",
        ),
        _r6_period(
            "June 2026",
            "2026-06-01",
            "2026-07-01",
            role="comparison_period",
        ),
    ]
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Compare May and June 2026 downtime and faults.",
        catalog=_r6_temporal_catalog(),
    )
    assert result.brief is not None
    assert result.brief.scope.time_surfaces == (
        "May 2026",
        "June 2026",
    )
    assert [(x.start, x.end) for x in result.brief.scope.periods] == [
        ("2026-05-01", "2026-06-01"),
        ("2026-06-01", "2026-07-01"),
    ]
    assert [x.role for x in result.brief.scope.periods] == [
        TemporalRole.BASELINE_PERIOD,
        TemporalRole.COMPARISON_PERIOD,
    ]
    assert result.brief.questions[0].comparisons[0].role == (
        ComparisonRole.TEMPORAL_PERIOD
    )



@pytest.mark.parametrize(
    ("effect_id", "candidate_ids", "start", "end"),
    [
        (
            "metric.downtime",
            ("metric.fault_count", "metric.performance"),
            "2026-03-01",
            "2026-05-01",
        ),
        (
            "metric.fault_count",
            ("metric.downtime", "metric.performance"),
            "2026-07-01",
            "2026-09-01",
        ),
    ],
)
def test_root_causal_change_observation_is_durable_typed_authority(
    effect_id,
    candidate_ids,
    start,
    end,
):
    payload = ready_payload(
        kind="root_cause",
        subject=(effect_id, *candidate_ids),
        related=("dimension.department",),
    )
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": effect_id,
        "effect_observation": "change",
        "candidate_mechanism_semantic_ids": list(candidate_ids),
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    payload["goals"][0]["temporal_material"] = {
        "mode": "window",
        "window": _r6_period(
            "accepted bounded analysis window",
            start,
            end,
        ),
    }
    payload["time_periods"] = []

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Explain the governed change over the accepted bounded window.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    goal = result.brief.questions[0]
    assert goal.kind == ResearchGoalKind.ROOT_CAUSE
    assert goal.causal_competition is not None
    assert goal.causal_competition.effect_observation.value == "change"
    assert [(item.start, item.end) for item in result.brief.scope.periods] == [
        (start, end)
    ]


def test_root_causal_level_observation_does_not_invent_change_authority():
    payload = ready_payload(
        kind="root_cause",
        subject=("metric.downtime", "metric.fault_count"),
        related=("dimension.department",),
    )
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "effect_observation": "level",
        "candidate_mechanism_semantic_ids": ["metric.fault_count"],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    payload["goals"][0]["temporal_material"] = {
        "mode": "window",
        "window": _r6_period(
            "accepted bounded level window",
            "2026-08-01",
            "2026-09-01",
        ),
    }
    payload["time_periods"] = []

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Explain the governed level in the accepted bounded window.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    causal = result.brief.questions[0].causal_competition
    assert causal is not None
    assert causal.effect_observation.value == "level"


def test_root_temporal_material_lifts_comparison_periods_into_scope():
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": [
            "metric.fault_count",
            "metric.performance",
        ],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    payload["goals"][0]["temporal_material"] = {
        "mode": "comparison",
        "baseline_period": _r6_period(
            "earlier interval",
            "2026-05-01",
            "2026-06-01",
        ),
        "comparison_period": _r6_period(
            "later interval",
            "2026-06-01",
            "2026-07-01",
        ),
    }
    payload["time_periods"] = []

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Investigate the governed RCA over two accepted periods.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert len(result.brief.questions) == 1
    goal = result.brief.questions[0]
    assert goal.kind == ResearchGoalKind.ROOT_CAUSE
    assert [item.role for item in goal.comparisons] == [
        ComparisonRole.TEMPORAL_PERIOD
    ]
    assert [
        (item.start, item.end, item.role)
        for item in result.brief.scope.periods
    ] == [
        (
            "2026-05-01",
            "2026-06-01",
            TemporalRole.BASELINE_PERIOD,
        ),
        (
            "2026-06-01",
            "2026-07-01",
            TemporalRole.COMPARISON_PERIOD,
        ),
    ]


def test_root_temporal_comparison_shape_fails_closed_when_period_missing():
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": [
            "metric.fault_count",
            "metric.performance",
        ],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    payload["goals"][0]["temporal_material"] = {
        "mode": "comparison",
        "baseline_period": _r6_period(
            "earlier interval",
            "2026-05-01",
            "2026-06-01",
        ),
        "comparison_period": None,
    }

    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Investigate the governed comparison.",
            catalog=_r6_temporal_catalog(),
        )

    assert exc.value.code == "INTAKE_MODEL_OUTPUT_INVALID"


def test_root_temporal_window_lifts_one_material_window_without_comparison():
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": [
            "metric.fault_count",
            "metric.performance",
        ],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    payload["goals"][0]["temporal_material"] = {
        "mode": "window",
        "window": _r6_period(
            "pooled interval",
            "2026-05-01",
            "2026-07-01",
        ),
    }
    payload["time_periods"] = []

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Investigate within the governed pooled interval.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert result.brief.questions[0].comparisons == ()
    assert [
        (item.start, item.end, item.role)
        for item in result.brief.scope.periods
    ] == [
        (
            "2026-05-01",
            "2026-07-01",
            TemporalRole.MATERIAL_WINDOW,
        )
    ]


def test_coorigin_temporal_comparison_subgoal_merges_into_root_cause():
    fragment = "Investigate the same governed two-period causal comparison."
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-root",
            "source_text": fragment,
            "source_fragment_text": fragment,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-temporal-material",
            "kind": "comparison",
            "source_text": fragment,
            "source_fragment_text": fragment,
            "subject_semantic_ids": ["metric.downtime"],
            "related_semantic_ids": [],
            "ranking": None,
            "comparisons": [
                {
                    "text": "accepted two-period comparison",
                    "role": "temporal_period",
                    "semantic_id": None,
                }
            ],
            "causal_competition": None,
        }
    )
    payload["time_periods"] = [
        _r6_period("period later", "2026-06-01", "2026-07-01"),
        _r6_period("period earlier", "2026-05-01", "2026-06-01"),
    ]

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=fragment,
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert len(result.brief.questions) == 1
    goal = result.brief.questions[0]
    assert goal.kind == ResearchGoalKind.ROOT_CAUSE
    assert [item.role for item in goal.comparisons] == [
        ComparisonRole.TEMPORAL_PERIOD
    ]
    by_start = {
        item.start: item.role for item in result.brief.scope.periods
    }
    assert by_start == {
        "2026-05-01": TemporalRole.BASELINE_PERIOD,
        "2026-06-01": TemporalRole.COMPARISON_PERIOD,
    }



def test_typed_temporal_material_parent_merges_distinct_fragments_into_root_cause():
    root_fragment = "Evaluate the governed explanations for the observed change."
    material_fragment = "Compare the accepted earlier and later periods."
    question = root_fragment + " " + material_fragment
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-root",
            "source_text": root_fragment,
            "source_fragment_text": root_fragment,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
            "temporal_material": {
                "mode": "comparison",
                "baseline_period": _r6_period(
                    "earlier accepted interval",
                    "2026-03-01",
                    "2026-04-01",
                ),
                "comparison_period": _r6_period(
                    "later accepted interval",
                    "2026-04-01",
                    "2026-05-01",
                ),
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-temporal-material",
            "kind": "comparison",
            "source_text": material_fragment,
            "source_fragment_text": material_fragment,
            "material_parent_goal_key": "g-root",
            "subject_semantic_ids": ["metric.downtime"],
            "related_semantic_ids": [],
            "ranking": None,
            "comparisons": [
                {
                    "text": "accepted period comparison",
                    "role": "temporal_period",
                    "semantic_id": None,
                }
            ],
            "causal_competition": None,
        }
    )
    payload["time_periods"] = []

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=question,
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert len(result.brief.questions) == 1
    goal = result.brief.questions[0]
    assert goal.kind == ResearchGoalKind.ROOT_CAUSE
    assert [item.role for item in goal.comparisons] == [
        ComparisonRole.TEMPORAL_PERIOD
    ]
    assert [
        (item.start, item.end, item.role)
        for item in result.brief.scope.periods
    ] == [
        (
            "2026-03-01",
            "2026-04-01",
            TemporalRole.BASELINE_PERIOD,
        ),
        (
            "2026-04-01",
            "2026-05-01",
            TemporalRole.COMPARISON_PERIOD,
        ),
    ]


def test_typed_temporal_material_parent_is_not_wording_authority():
    root_fragment = "Assess competing governed mechanisms."
    material_fragment = "Contrast the two bounded windows as material."
    question = root_fragment + " " + material_fragment
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.fault_count",
            "metric.downtime",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-cause",
            "source_text": root_fragment,
            "source_fragment_text": root_fragment,
            "causal_competition": {
                "effect_semantic_id": "metric.fault_count",
                "candidate_mechanism_semantic_ids": [
                    "metric.downtime",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
            "temporal_material": {
                "mode": "comparison",
                "baseline_period": _r6_period(
                    "window alpha",
                    "2026-01-01",
                    "2026-02-01",
                ),
                "comparison_period": _r6_period(
                    "window beta",
                    "2026-02-01",
                    "2026-03-01",
                ),
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-material",
            "kind": "comparison",
            "source_text": material_fragment,
            "source_fragment_text": material_fragment,
            "material_parent_goal_key": "g-cause",
            "subject_semantic_ids": ["metric.fault_count"],
            "related_semantic_ids": [],
            "ranking": None,
            "comparisons": [
                {
                    "text": "bounded windows",
                    "role": "temporal_period",
                    "semantic_id": None,
                }
            ],
            "causal_competition": None,
        }
    )
    payload["time_periods"] = []

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=question,
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert len(result.brief.questions) == 1
    assert result.brief.questions[0].kind == ResearchGoalKind.ROOT_CAUSE
    assert {
        item.candidate_id
        for item in result.brief.questions[0].subject_refs
    } == {
        "metric.fault_count",
        "metric.downtime",
        "metric.performance",
    }


def test_comparison_provider_schema_exposes_typed_material_parent_key():
    schema = _intake_provider_schema(_r6_temporal_catalog())
    variants = schema["$defs"]["ModelGoalDraft"]["anyOf"]
    comparison = next(
        item
        for item in variants
        if item["properties"]["kind"]["enum"] == ["comparison"]
    )
    assert "material_parent_goal_key" in comparison["properties"]
    assert "material_parent_goal_key" in comparison["required"]


def test_distinct_fragment_temporal_comparison_remains_real_multi_intent():
    root_fragment = "Investigate the governed causal explanations."
    compare_fragment = "Separately compare the two accepted periods."
    question = root_fragment + " " + compare_fragment
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-root",
            "source_text": root_fragment,
            "source_fragment_text": root_fragment,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-independent-comparison",
            "kind": "comparison",
            "source_text": compare_fragment,
            "source_fragment_text": compare_fragment,
            "material_parent_goal_key": None,
            "subject_semantic_ids": ["metric.downtime"],
            "related_semantic_ids": [],
            "ranking": None,
            "comparisons": [
                {
                    "text": "accepted two-period comparison",
                    "role": "temporal_period",
                    "semantic_id": None,
                }
            ],
            "causal_competition": None,
        }
    )
    payload["time_periods"] = [
        _r6_period(
            "period earlier",
            "2026-05-01",
            "2026-06-01",
            role="baseline_period",
        ),
        _r6_period(
            "period later",
            "2026-06-01",
            "2026-07-01",
            role="comparison_period",
        ),
    ]

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=question,
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert tuple(item.kind for item in result.brief.questions) == (
        ResearchGoalKind.ROOT_CAUSE,
        ResearchGoalKind.COMPARISON,
    )



def test_typed_temporal_material_parent_rejects_unknown_owner():
    root_fragment = "Assess the governed causal alternatives."
    material_fragment = "Use the bounded period comparison as material."
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-root",
            "source_text": root_fragment,
            "source_fragment_text": root_fragment,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
            "temporal_material": {
                "mode": "comparison",
                "baseline_period": _r6_period(
                    "earlier", "2026-03-01", "2026-04-01"
                ),
                "comparison_period": _r6_period(
                    "later", "2026-04-01", "2026-05-01"
                ),
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-material",
            "kind": "comparison",
            "source_text": material_fragment,
            "source_fragment_text": material_fragment,
            "material_parent_goal_key": "g-missing-root",
            "subject_semantic_ids": ["metric.downtime"],
            "related_semantic_ids": [],
            "ranking": None,
            "comparisons": [
                {
                    "text": "bounded periods",
                    "role": "temporal_period",
                    "semantic_id": None,
                }
            ],
            "causal_competition": None,
        }
    )
    payload["time_periods"] = []

    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question=root_fragment + " " + material_fragment,
            catalog=_r6_temporal_catalog(),
        )

    assert exc.value.code == "INTAKE_TEMPORAL_MATERIAL_PARENT_INVALID"


def test_typed_temporal_material_parent_rejects_scope_escape():
    root_fragment = "Assess the governed causal alternatives."
    material_fragment = "Use a bounded comparison as material."
    payload = ready_payload(
        kind="root_cause",
        subject=("metric.downtime", "metric.fault_count"),
        related=("dimension.department",),
    )
    payload["goals"][0].update(
        {
            "goal_key": "g-root",
            "source_text": root_fragment,
            "source_fragment_text": root_fragment,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": ["metric.fault_count"],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
            "temporal_material": {
                "mode": "comparison",
                "baseline_period": _r6_period(
                    "earlier", "2026-03-01", "2026-04-01"
                ),
                "comparison_period": _r6_period(
                    "later", "2026-04-01", "2026-05-01"
                ),
            },
        }
    )
    payload["goals"].append(
        {
            "goal_key": "g-material",
            "kind": "comparison",
            "source_text": material_fragment,
            "source_fragment_text": material_fragment,
            "material_parent_goal_key": "g-root",
            "subject_semantic_ids": ["metric.performance"],
            "related_semantic_ids": [],
            "ranking": None,
            "comparisons": [
                {
                    "text": "bounded periods",
                    "role": "temporal_period",
                    "semantic_id": None,
                }
            ],
            "causal_competition": None,
        }
    )
    payload["time_periods"] = []

    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question=root_fragment + " " + material_fragment,
            catalog=_r6_temporal_catalog(),
        )

    assert exc.value.code == "INTAKE_TEMPORAL_MATERIAL_PARENT_SCOPE_ESCAPE"


def test_typed_temporal_comparison_canonicalizes_period_roles_without_prompt_semantics():
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": [
            "metric.fault_count",
            "metric.performance",
        ],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    payload["goals"][0]["comparisons"] = [
        {
            "text": "accepted two-period comparison",
            "role": "temporal_period",
            "semantic_id": None,
        }
    ]
    payload["time_periods"] = [
        _r6_period(
            "later accepted period",
            "2026-06-01",
            "2026-07-01",
            role="material_window",
        ),
        _r6_period(
            "earlier accepted period",
            "2026-05-01",
            "2026-06-01",
            role="material_window",
        ),
    ]

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Investigate the governed two-period causal comparison.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    by_start = {
        item.start: item.role for item in result.brief.scope.periods
    }
    assert by_start == {
        "2026-05-01": TemporalRole.BASELINE_PERIOD,
        "2026-06-01": TemporalRole.COMPARISON_PERIOD,
    }


def test_two_material_windows_without_typed_temporal_comparison_remain_windows():
    payload = ready_payload()
    payload["time_periods"] = [
        _r6_period("window A", "2026-05-01", "2026-06-01"),
        _r6_period("window B", "2026-06-01", "2026-07-01"),
    ]

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Inspect the accepted bounded evidence windows.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert [item.role for item in result.brief.scope.periods] == [
        TemporalRole.MATERIAL_WINDOW,
        TemporalRole.MATERIAL_WINDOW,
    ]


def test_r6_follow_up_narrowing_advances_scope_from_two_periods_to_one():
    initial_payload = ready_payload(
        kind="comparison",
        subject=("metric.downtime", "metric.fault_count"),
    )
    initial_payload["goals"][0]["comparisons"] = [
        {
            "text": "May versus June",
            "role": "temporal_period",
            "semantic_id": None,
        }
    ]
    initial_payload["time_periods"] = [
        _r6_period(
            "May 2026",
            "2026-05-01",
            "2026-06-01",
            role="baseline_period",
        ),
        _r6_period(
            "June 2026",
            "2026-06-01",
            "2026-07-01",
            role="comparison_period",
        ),
    ]
    initial = ResearchIntakeCompiler(
        transport=FakeTransport(initial_payload)
    ).compile(
        question="Compare May and June.",
        catalog=_r6_temporal_catalog(),
    )
    assert initial.brief is not None

    narrowed_payload = {
        "terminal": "READY",
        "operations": [
            {
                "facet": "PERIOD",
                "operation": "SET",
                "periods": [
                    _r6_period(
                        "June only",
                        "2026-06-01",
                        "2026-07-01",
                    )
                ],
                "source_fragment": "narrow to June only",
            }
        ],
    }
    narrowed = ResearchIntakeCompiler(
        transport=FakeTransport(narrowed_payload)
    ).compile(
        question="Now narrow to June only.",
        catalog=_r6_temporal_catalog(),
        prior_brief=initial.brief,
    )
    assert narrowed.brief is not None
    assert narrowed.scope_contract is not None
    assert narrowed.brief.scope.scope_version.version_id == "scope_v2"
    assert narrowed.brief.scope.scope_version.parent_version_id == "scope_v1"
    assert [(x.start, x.end) for x in narrowed.brief.scope.periods] == [
        ("2026-06-01", "2026-07-01")
    ]


def test_r6_different_legal_surface_wording_keeps_same_durable_period_identity():
    identities = []
    surfaces = []
    for wording in ("June 2026", "the June 2026 window"):
        payload = ready_payload()
        payload["time_periods"] = [
            _r6_period(wording, "2026-06-01", "2026-07-01")
        ]
        result = ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question=wording,
            catalog=_r6_temporal_catalog(),
        )
        assert result.brief is not None
        period = result.brief.scope.periods[0]
        identities.append(
            (
                period.time_dimension_candidate_id,
                period.start,
                period.end,
            )
        )
        surfaces.append(result.brief.scope.time_surfaces)
    assert identities[0] == identities[1]
    assert surfaces == [
        ("June 2026",),
        ("the June 2026 window",),
    ]


def test_r6_follow_up_surface_rewording_does_not_mint_new_scope_version():
    first_payload = ready_payload()
    first_payload["time_periods"] = [
        _r6_period("June 2026", "2026-06-01", "2026-07-01")
    ]
    first = ResearchIntakeCompiler(
        transport=FakeTransport(first_payload)
    ).compile(
        question="Inspect June 2026.",
        catalog=_r6_temporal_catalog(),
    )
    assert first.brief is not None

    reworded_payload = {
        "terminal": "READY",
        "operations": [
            {
                "facet": "PERIOD",
                "operation": "SET",
                "periods": [
                    _r6_period(
                        "the June 2026 window",
                        "2026-06-01",
                        "2026-07-01",
                    )
                ],
                "source_fragment": "June 2026 window",
            }
        ],
    }
    reworded = ResearchIntakeCompiler(
        transport=FakeTransport(reworded_payload)
    ).compile(
        question="Use the June 2026 window.",
        catalog=_r6_temporal_catalog(),
        prior_brief=first.brief,
    )
    assert reworded.brief is not None
    assert reworded.scope_contract is None
    assert (
        reworded.brief.scope.scope_version.version_id
        == first.brief.scope.scope_version.version_id
    )
    assert (
        reworded.brief.scope.time_surfaces
        == first.brief.scope.time_surfaces
    )
    assert [
        (
            item.time_dimension_candidate_id,
            item.start,
            item.end,
        )
        for item in reworded.brief.scope.periods
    ] == [
        ("dimension.event_date", "2026-06-01", "2026-07-01")
    ]


def test_r6_exact_structured_period_repeat_is_idempotent():
    payload = ready_payload()
    period = _r6_period("May-June 2026", "2026-05-01", "2026-07-01")
    payload["time_periods"] = [period, dict(period)]

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Inspect May-June 2026.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert len(result.brief.scope.periods) == 1
    accepted = result.brief.scope.periods[0]
    assert (
        accepted.time_dimension_candidate_id,
        accepted.start,
        accepted.end,
        accepted.role,
    ) == (
        "dimension.event_date",
        "2026-05-01",
        "2026-07-01",
        TemporalRole.MATERIAL_WINDOW,
    )


def test_r6_duplicate_typed_period_identity_is_rejected_even_with_new_wording():
    payload = ready_payload()
    payload["time_periods"] = [
        _r6_period("June 2026", "2026-06-01", "2026-07-01"),
        _r6_period("June window", "2026-06-01", "2026-07-01"),
    ]
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Inspect June.",
            catalog=_r6_temporal_catalog(),
        )
    assert exc.value.code == "INTAKE_TIME_PERIOD_DUPLICATE"


def test_r6_shared_surface_can_bind_distinct_typed_periods():
    payload = ready_payload()
    payload["time_periods"] = [
        _r6_period("May-June window", "2026-05-01", "2026-06-01"),
        _r6_period("May-June window", "2026-06-01", "2026-07-01"),
    ]

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Compare May and June.",
        catalog=_r6_temporal_catalog(),
    )

    assert result.brief is not None
    assert [
        (
            item.time_dimension_candidate_id,
            item.start,
            item.end,
        )
        for item in result.brief.scope.periods
    ] == [
        ("dimension.event_date", "2026-05-01", "2026-06-01"),
        ("dimension.event_date", "2026-06-01", "2026-07-01"),
    ]
    assert result.brief.scope.time_surfaces == ("May-June window",)


def test_r6_unauthorized_temporal_dimension_is_rejected():
    payload = ready_payload()
    payload["time_periods"] = [
        _r6_period(
            "June 2026",
            "2026-06-01",
            "2026-07-01",
            dimension_id="dimension.department",
        )
    ]
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Inspect June.",
            catalog=_r6_temporal_catalog(),
        )
    assert exc.value.code == "INTAKE_TIME_DIMENSION_UNAUTHORIZED"


def test_r6_invalid_interval_is_rejected():
    payload = ready_payload()
    payload["time_periods"] = [
        _r6_period("June 2026", "2026-07-01", "2026-06-01")
    ]
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Inspect June.",
            catalog=_r6_temporal_catalog(),
        )
    assert exc.value.code == "INTAKE_TIME_PERIOD_INVALID"


def test_r6_missing_typed_period_field_fails_closed():
    payload = ready_payload()
    payload["time_periods"] = [
        {
            "source_text": "June 2026",
            "time_dimension_semantic_id": "dimension.event_date",
            "start": "2026-06-01",
        }
    ]
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Inspect June.",
            catalog=_r6_temporal_catalog(),
        )
    assert exc.value.code == "INTAKE_MODEL_OUTPUT_INVALID"


def test_typed_causal_candidate_comparison_requires_goal_scoped_semantic_id():
    payload = ready_payload(
        kind="root_cause",
        subject=("metric.downtime", "metric.fault_count"),
        related=("dimension.department",),
    )
    payload["goals"][0]["comparisons"] = [
        {
            "text": "fault count",
            "role": "causal_candidate",
            "semantic_id": "metric.fault_count",
        }
    ]
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": ["metric.fault_count"],
        "diagnostic_dimension_ids": ["dimension.department"],
    }
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Test fault count as a candidate explanation for downtime.",
        catalog=catalog(),
    )
    assert result.brief is not None
    comparison = result.brief.questions[0].comparisons[0]
    assert comparison.role == ComparisonRole.CAUSAL_CANDIDATE
    assert comparison.semantic_id == "metric.fault_count"


def test_typed_causal_candidate_only_in_causal_surface_is_canonicalized_and_accepted():
    payload = ready_payload(
        kind="root_cause",
        subject=("metric.downtime",),
        related=("dimension.department",),
    )
    payload["goals"][0]["comparisons"] = [
        {
            "text": "fault count",
            "role": "causal_candidate",
            "semantic_id": "metric.fault_count",
        }
    ]
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": ["metric.fault_count"],
        "diagnostic_dimension_ids": ["dimension.department"],
    }

    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Test the requested explanation.",
        catalog=catalog(),
    )

    assert result.brief is not None
    goal = result.brief.questions[0]
    assert tuple(item.candidate_id for item in goal.subject_refs) == (
        "metric.downtime",
        "metric.fault_count",
    )
    assert goal.comparisons[0].semantic_id == "metric.fault_count"


def test_typed_causal_unknown_candidate_fails_closed():
    payload = ready_payload(
        kind="root_cause",
        subject=("metric.downtime",),
        related=("dimension.department",),
    )
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": ["metric.unknown_cause"],
        "diagnostic_dimension_ids": ["dimension.department"],
    }

    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Test the requested explanation.",
            catalog=catalog(),
        )

    assert exc.value.code == "INTAKE_UNKNOWN_SEMANTIC_REF"


def test_typed_causal_unrelated_comparison_expansion_fails_closed():
    payload = ready_payload(
        kind="root_cause",
        subject=("metric.downtime",),
        related=("dimension.department",),
    )
    payload["goals"][0]["comparisons"] = [
        {
            "text": "performance",
            "role": "causal_candidate",
            "semantic_id": "metric.performance",
        }
    ]
    payload["goals"][0]["causal_competition"] = {
        "effect_semantic_id": "metric.downtime",
        "candidate_mechanism_semantic_ids": ["metric.fault_count"],
        "diagnostic_dimension_ids": ["dimension.department"],
    }

    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Test the requested explanation.",
            catalog=catalog(),
        )

    assert exc.value.code == "INTAKE_COMPARISON_SEMANTIC_OUTSIDE_GOAL_SCOPE"


def test_relationship_provider_cannot_reconstruct_left_right_dimension_tuple():
    payload = ready_payload(
        kind="relationship",
        subject=("metric.downtime", "metric.fault_count"),
        related=("dimension.department",),
    )
    payload["goals"][0]["allowed_relationship_id"] = (
        "rel.downtime_fault_by_department"
    )
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Inspect the governed relationship.",
            catalog=catalog(),
        )
    assert exc.value.code == "INTAKE_RELATIONSHIP_RECONSTRUCTION_FORBIDDEN"


def test_catalog_reordering_preserves_authority_identity_and_relationship_expansion():
    original = catalog()
    reordered = ResearchIntakeCatalog(
        context_version=original.context_version,
        semantic_refs=tuple(reversed(original.semantic_refs)),
        allowed_relationships=tuple(reversed(original.allowed_relationships)),
        supported_domains=tuple(reversed(original.supported_domains)),
    )
    assert original.fingerprint == reordered.fingerprint

    payload = ready_payload(kind="relationship", subject=(), related=())
    payload["goals"][0]["allowed_relationship_id"] = (
        "rel.downtime_fault_by_department"
    )
    first = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Inspect downtime and faults by department.",
        catalog=original,
    )
    second = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Inspect downtime and faults by department.",
        catalog=reordered,
    )
    assert first.brief is not None and second.brief is not None
    assert first.brief.brief_id == second.brief.brief_id
    assert [
        ref.candidate_id
        for ref in first.brief.questions[0].subject_refs
    ] == [
        "metric.downtime",
        "metric.fault_count",
    ]
    assert [
        ref.candidate_id
        for ref in first.brief.questions[0].related_refs
    ] == ["dimension.department"]



def test_coorigin_source_fragment_provenance_is_exact_and_shared_across_goal_decomposition():
    fragment = "En yüksek downtime olan iki bölümü fault count ile birlikte incele."
    payload = ready_payload(
        kind="ranking",
        subject=("dimension.department", "metric.downtime"),
        related=(),
    )
    payload["goals"][0]["source_text"] = "En yüksek downtime olan iki bölümü incele."
    payload["goals"][0]["source_fragment_text"] = fragment
    payload["goals"][0]["ranking"] = {
        "direction": "desc",
        "limit": 2,
        "measure_semantic_id": "metric.downtime",
        "source_text": "En yüksek downtime olan iki bölüm",
    }
    payload["goals"].append(
        {
            "goal_key": "g-relationship",
            "kind": "relationship",
            "source_text": fragment,
            "source_fragment_text": fragment,
            "allowed_relationship_id": "rel.downtime_fault_by_department",
            "ranking": None,
            "comparison_texts": [],
        }
    )

    current = (
        "Şimdi yalnız Haziran 2026’ya daralt. "
        + fragment
        + " Önceki analizi tarihsel bağlam olarak koru."
    )
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question=current,
        catalog=catalog(),
    )
    assert result.brief is not None
    ranking, relationship = result.brief.questions
    assert ranking.source_text != relationship.source_text
    assert ranking.source_fragment_identity is not None
    assert ranking.source_fragment_identity == relationship.source_fragment_identity
    assert ranking.source_fragment_identity.startswith("fragment-sha256:")


def test_intake_rejects_nonverbatim_goal_fragment_provenance():
    payload = ready_payload()
    payload["goals"][0]["source_fragment_text"] = "a paraphrase not present in the message"
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Show machine downtime by department.",
            catalog=catalog(),
        )
    assert exc.value.code == "INTAKE_SOURCE_FRAGMENT_NOT_VERBATIM"

def test_relationship_intent_is_typed_and_observational_is_preserved():
    payload = ready_payload(
        kind="relationship",
        subject=(),
        related=(),
    )
    payload["goals"][0] = {
        "goal_key": "g-rel",
        "kind": "relationship",
        "source_text": "Compare downtime and fault count as an observational relationship.",
        "source_fragment_text": "Compare downtime and fault count as an observational relationship.",
        "allowed_relationship_id": "rel.downtime_fault_by_department",
        "relationship_intent": "observational",
        "ranking": None,
        "comparisons": [],
    }
    question = payload["goals"][0]["source_text"]
    transport = FakeTransport(payload)

    result = ResearchIntakeCompiler(transport=transport).compile(
        question=question,
        catalog=catalog(),
    )

    assert result.brief is not None
    goal = result.brief.questions[0]
    assert goal.kind == ResearchGoalKind.RELATIONSHIP
    assert goal.relationship_intent.value == "observational"
    schema = transport.calls[0]["schema"]
    variants = schema["$defs"]["ModelGoalDraft"]["anyOf"]
    relationship_variant = next(
        item
        for item in variants
        if item["properties"]["kind"].get("enum") == ["relationship"]
    )
    assert relationship_variant["properties"]["relationship_intent"]["enum"] == [
        "observational",
        "business_policy",
    ]


def test_relationship_intent_is_forbidden_on_non_relationship_goal():
    payload = ready_payload()
    payload["goals"][0]["relationship_intent"] = "observational"
    transport = FakeTransport(payload)

    with pytest.raises(Exception):
        ResearchIntakeCompiler(transport=transport).compile(
            question=payload["goals"][0]["source_text"],
            catalog=catalog(),
        )

def test_relationship_fixture_without_new_intent_defaults_fail_conservative_business_policy():
    payload = ready_payload(
        kind="relationship",
        subject=(),
        related=(),
    )
    payload["goals"][0].update(
        {
            "allowed_relationship_id": "rel.downtime_fault_by_department",
            "source_text": "Compare downtime and fault count.",
            "source_fragment_text": "Compare downtime and fault count.",
        }
    )
    payload["goals"][0].pop("relationship_intent", None)
    transport = FakeTransport(payload)

    result = ResearchIntakeCompiler(transport=transport).compile(
        question="Compare downtime and fault count.",
        catalog=catalog(),
    )

    assert result.brief is not None
    goal = result.brief.questions[0]
    assert goal.relationship_intent.value == "business_policy"

