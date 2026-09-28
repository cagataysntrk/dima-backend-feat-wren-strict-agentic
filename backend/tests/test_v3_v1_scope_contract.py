from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.v3.analytical_request_contract import (
    AnalyticalFilterInvariant,
    AnalyticalRequestMismatch,
    assert_child_request_scope,
    observation_from_contract,
    assert_request_invariants,
)
from app.v3.native_standard.contracts import (
    NativeAggregationFact,
    NativeAttestationEnvelope,
    NativeAttestedRuntimeIdentity,
    NativeBreakoutFact,
    NativeExecutionManifest,
    NativeOrderByFact,
    NativePermissionProvenance,
    NativeTemporalPredicate,
    NativeTextualEqualityPredicate,
    NativeValidationProvenance,
)
from app.v3.research import (
    NativeMetabotConversationRef,
    ResearchObligation,
    ResearchSession,
    ResearchManager,
)
from app.v3.research_analytical_scope import (
    NativeFieldLocator,
    NativeTableLocator,
    ResearchAnalyticalScopeError,
    analytical_scope_contract,
    assert_attested_native_scope,
)
from app.v3.research_contracts import (
    ComparisonSurface,
    RankingSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchNativeVerificationBinding,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeMutation,
    ScopeMutationKind,
    ScopeVersion,
    SemanticTargetKind,
    apply_scope_mutation,
)
from app.v3.research_followup import NativeResearchFollowupExecutor
from app.v3.research_intake import (
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
    ResearchIntakeError,
    _intake_provider_schema,
)
from app.v3.substrate.metabase.native_models import NativeEngineIdentity


NOW = datetime(2026, 9, 28, 3, 30, tzinfo=timezone.utc)
CONVERSATION = UUID("00000000-0000-4000-8000-000000006901")
ENGINE = NativeEngineIdentity(
    engine_sha="cbe313af9ac2d5960f662068e433d328d896fb06",
    upstream_base_sha="2ba2485c78d7e00a9a25f82c00fc201da71590c4",
    runtime_tag="0.63.18-dima.6",
    runtime_image_digest="sha256:" + "4" * 64,
    build_identity="test-build",
    runtime_image_identity="test-image",
)


def binding(candidate_id, column=None, *, aggregation=None, argument_kind=None):
    return ResearchNativeVerificationBinding(
        candidate_id=candidate_id,
        table_name="machine_operations",
        column_name=column,
        aggregation=aggregation,
        argument_kind=argument_kind,
    )


DOWNTIME = ResearchSemanticRef(
    source_mention="downtime",
    candidate_id="metric.downtime",
    target_kind=SemanticTargetKind.METRIC,
    canonical_name="Downtime",
    cube_names=("machine_operations",),
)
FAULTS = ResearchSemanticRef(
    source_mention="faults",
    candidate_id="metric.faults",
    target_kind=SemanticTargetKind.METRIC,
    canonical_name="Faults",
    cube_names=("machine_operations",),
)
DEPARTMENT = ResearchSemanticRef(
    source_mention="department",
    candidate_id="dimension.department",
    target_kind=SemanticTargetKind.DIMENSION,
    canonical_name="Department",
    cube_names=("machine_operations",),
)
EVENT_DATE = ResearchSemanticRef(
    source_mention="event date",
    candidate_id="dimension.event_date",
    target_kind=SemanticTargetKind.DIMENSION,
    canonical_name="Event Date",
    cube_names=("machine_operations",),
)
ASSEMBLY = ResearchSemanticRef(
    source_mention="Assembly",
    candidate_id="entity.department.assembly",
    target_kind=SemanticTargetKind.ENTITY_VALUE,
    canonical_name="Assembly",
    dimension_name="department",
    value="Assembly",
    cube_names=("machine_operations",),
)
PACKAGING = ResearchSemanticRef(
    source_mention="Packaging",
    candidate_id="entity.department.packaging",
    target_kind=SemanticTargetKind.ENTITY_VALUE,
    canonical_name="Packaging",
    dimension_name="department",
    value="Packaging",
    cube_names=("machine_operations",),
)

VERIFICATION_BINDINGS = (
    binding(
        DOWNTIME.candidate_id,
        "machine_downtime_minutes",
        aggregation="sum",
        argument_kind="field_or_expression",
    ),
    binding(
        FAULTS.candidate_id,
        "fault_count",
        aggregation="sum",
        argument_kind="field_or_expression",
    ),
    binding(DEPARTMENT.candidate_id, "department"),
    binding(EVENT_DATE.candidate_id, "event_date"),
    binding(ASSEMBLY.candidate_id, "department"),
    binding(PACKAGING.candidate_id, "department"),
)
MAY = ResearchTimePeriod(
    source_text="May 2026",
    time_dimension_candidate_id=EVENT_DATE.candidate_id,
    start="2026-05-01",
    end="2026-06-01",
)
JUNE = ResearchTimePeriod(
    source_text="June 2026",
    time_dimension_candidate_id=EVENT_DATE.candidate_id,
    start="2026-06-01",
    end="2026-07-01",
)


def session(
    *,
    metrics=(DOWNTIME,),
    entities=(),
    periods=(JUNE,),
    comparison=False,
    ranking=False,
    version=1,
):
    related=(DEPARTMENT, EVENT_DATE)
    question=ResearchQuestion(
        goal_id="g_scope",
        kind=(
            ResearchGoalKind.COMPARISON
            if comparison
            else ResearchGoalKind.RANKING
            if ranking
            else ResearchGoalKind.BREAKDOWN
        ),
        source_text="Accepted analytical task.",
        subject_refs=tuple(metrics),
        related_refs=related,
        ranking=(
            RankingSurface(
                text="top downtime",
                direction="desc",
                limit=3,
            )
            if ranking
            else None
        ),
        comparisons=(
            (ComparisonSurface(text="May vs June"),)
            if comparison
            else ()
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    refs=tuple(dict.fromkeys(
        (*metrics, *related, *entities)
    ))
    brief=ResearchBrief(
        brief_id="rb_scope",
        objective="accepted scope",
        scope=ResearchScope(
            semantic_refs=refs,
            time_surfaces=tuple(x.source_text for x in periods),
            periods=tuple(periods),
            temporal_dimension_ids=(EVENT_DATE.candidate_id,),
            native_verification_bindings=tuple(
                item
                for item in VERIFICATION_BINDINGS
                if item.candidate_id in {ref.candidate_id for ref in refs}
            ),
            scope_version=ScopeVersion(
                version_id=f"scope_v{version}",
                ordinal=version,
                parent_version_id=(
                    None if version == 1 else f"scope_v{version-1}"
                ),
            ),
        ),
        questions=(question,),
        must_requirement_ids=(question.goal_id,),
        context_version="ctx-r1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    return ResearchSession(
        session_id="rs_" + "1" * 24,
        revision=1,
        authority_id="atc_r1",
        lineage_id="atl_r1",
        source_message_hash="a" * 64,
        context_version="ctx-r1",
        tenant_binding="id:tenant-r1",
        principal_subject="user-r1",
        objective=brief.objective,
        accepted_brief=brief,
        obligations=(
            ResearchObligation(
                obligation_id=question.goal_id,
                objective=question.source_text,
            ),
        ),
        native_conversation=NativeMetabotConversationRef(
            conversation_id=CONVERSATION,
        ),
        created_at=NOW,
        updated_at=NOW,
    )


TABLE_LOCATORS = {
    10: NativeTableLocator(
        table_id=10,
        table_name="machine_operations",
    ),
}


LOCATORS = {
    101: NativeFieldLocator(
        field_id=101, table_id=10, table_name="machine_operations",
        column_name="machine_downtime_minutes",
    ),
    102: NativeFieldLocator(
        field_id=102, table_id=10, table_name="machine_operations",
        column_name="fault_count",
    ),
    201: NativeFieldLocator(
        field_id=201, table_id=10, table_name="machine_operations",
        column_name="department",
    ),
    301: NativeFieldLocator(
        field_id=301, table_id=10, table_name="machine_operations",
        column_name="event_date",
    ),
}


def attestation(
    *,
    metric_field_ids=(101,),
    breakout_field_ids=(201,),
    entity_value=None,
    start="2026-06-01",
    end="2026-07-01",
    time=True,
    ranking=False,
):
    aggregations=tuple(
        NativeAggregationFact(
            operator="sum",
            argument_kind="field_or_expression",
            referenced_field_ids=(field_id,),
            distinct=False,
        )
        for field_id in metric_field_ids
    )
    breakouts=tuple(
        NativeBreakoutFact(
            stage_number=0,
            breakout_index=index,
            field_id=field_id,
            field_type="type/Text" if field_id == 201 else "type/Date",
            temporal_unit=("month" if field_id == 301 else None),
        )
        for index,field_id in enumerate(breakout_field_ids)
    )
    temporal=(
        (
            NativeTemporalPredicate(
                time_field_id=301,
                operator=">=",
                lower_bound=start,
                lower_inclusive=True,
                field_temporal_type="type/Date",
            ),
            NativeTemporalPredicate(
                time_field_id=301,
                operator="<",
                upper_bound=end,
                upper_inclusive=False,
                field_temporal_type="type/Date",
            ),
        )
        if time
        else ()
    )
    textual=(
        (
            NativeTextualEqualityPredicate(
                stage_number=0,
                field_id=201,
                operator="=",
                literal_value=entity_value,
                field_type="type/Text",
            ),
        )
        if entity_value is not None
        else ()
    )
    orders=(
        (
            NativeOrderByFact(
                stage_number=0,
                order_index=0,
                direction="desc",
                target_kind="aggregation",
                aggregation_index=0,
            ),
        )
        if ranking
        else ()
    )
    manifest=NativeExecutionManifest(
        attestation_id="att-r1",
        native_conversation_id=CONVERSATION,
        native_assistant_message_id=1,
        native_tool_call_id="tool-r1",
        native_query_id="query-r1",
        producer_tool="construct_notebook_query",
        exact_pmbql_fingerprint="b" * 64,
        database_id=1,
        primary_source_table_id=10,
        referenced_source_table_ids=(10,),
        aggregation_count=len(aggregations),
        aggregations=aggregations,
        breakout_count=len(breakouts),
        breakouts=breakouts,
        material_filter_count=len(temporal)+len(textual),
        non_temporal_filter_count=len(textual),
        temporal_predicates=temporal,
        textual_equality_predicates=textual,
        explicit_join_count=0,
        implicit_join_count=0,
        implicit_joined_table_ids=(),
        order_by_count=len(orders),
        order_bys=orders,
        limit=(3 if ranking else None),
        stage_count=1,
        material_query_count=1,
        authenticated_metabase_subject=77,
        validation_provenance=NativeValidationProvenance(
            producer_structured_output="PASSED",
            pmbql_schema="PASSED",
            producer_query_id_match="PASSED",
            producer_state_match="PASSED",
        ),
        permission_provenance=NativePermissionProvenance(
            current_metabase_user_id=77,
            permission_check="PASSED",
            checked_source_table_ids=(10,),
        ),
        runtime_identity=NativeAttestedRuntimeIdentity(
            repository="UpcyTech/dima-metabase-engine",
            revision_sha=ENGINE.engine_sha,
            upstream_base_sha=ENGINE.upstream_base_sha,
            runtime_tag=ENGINE.runtime_tag,
            build_identity=ENGINE.build_identity,
            image_identity=ENGINE.runtime_image_identity,
            runtime_instance_id=UUID(
                "00000000-0000-4000-8000-000000006902"
            ),
        ),
    )
    return NativeAttestationEnvelope(
        exact_serialized_pmbql={"database":1},
        manifest=manifest,
    )


def test_r1_p14_and_p17_use_same_accepted_scope_envelope():
    original=session()
    delegation=ResearchManager.prepare_native_delegation(
        original,
        obligation_id="g_scope",
    )
    p14=delegation.request.context["dima_analytical_scope"]
    assert p14["period"]["start"] == "2026-06-01"
    assert p14["period"]["end"] == "2026-07-01"
    assert p14["dimension_refs"] == ["dimension.department"]

    step=SimpleNamespace(step_id="rrs_"+"1"*24)
    task=SimpleNamespace(
        task_id="rit_"+"2"*24,
        parent_obligation_id="g_scope",
        bounded_objective="Investigate the accepted material direction.",
        analytical_scope=analytical_scope_contract(
            session=delegation.session,
            obligation_id="g_scope",
        ).model_copy(
            update={"request_ref": "p17-child-scope"}
        ),
    )
    p17=NativeResearchFollowupExecutor._request(
        session=delegation.session,
        step=step,
        task=task,
    ).context["dima_analytical_scope"]
    assert p17["request_ref"] != p14["request_ref"]
    assert {
        key: value for key, value in p17.items()
        if key != "request_ref"
    } == {
        key: value for key, value in p14.items()
        if key != "request_ref"
    }


def test_r1_p17_child_contract_accepts_one_typed_entity_narrowing_and_keeps_june():
    parent=analytical_scope_contract(
        session=session(),
        obligation_id="g_scope",
    )
    child=parent.model_copy(
        update={
            "request_ref":"p17-child-assembly",
            "filters":(
                AnalyticalFilterInvariant(
                    semantic_ref=DEPARTMENT.candidate_id,
                    source_candidate_id=DEPARTMENT.candidate_id,
                    dimension_name="department",
                    value="Assembly",
                ),
            ),
        }
    )
    assert_child_request_scope(parent,child)
    assert child.period == parent.period
    assert child.period is not None
    assert child.period.start == "2026-06-01"
    assert child.period.end == "2026-07-01"


def test_r1_p17_child_contract_rejects_filter_narrowing_plus_time_broadening():
    parent=analytical_scope_contract(
        session=session(),
        obligation_id="g_scope",
    )
    child=parent.model_copy(
        update={
            "request_ref":"p17-child-illegal",
            "filters":(
                AnalyticalFilterInvariant(
                    semantic_ref=DEPARTMENT.candidate_id,
                    source_candidate_id=DEPARTMENT.candidate_id,
                    dimension_name="department",
                    value="Assembly",
                ),
            ),
            "period":None,
        }
    )
    with pytest.raises(
        AnalyticalRequestMismatch,
        match="TIME_MUTATION_FORBIDDEN",
    ):
        assert_child_request_scope(parent,child)


def test_r1_legal_entity_narrowing_preserves_period_contract():
    current=ResearchScope(
        semantic_refs=(DOWNTIME,DEPARTMENT,EVENT_DATE,ASSEMBLY,PACKAGING),
        time_surfaces=("June 2026",),
        periods=(JUNE,),
        temporal_dimension_ids=(EVENT_DATE.candidate_id,),
        native_verification_bindings=tuple(
            item
            for item in VERIFICATION_BINDINGS
            if item.candidate_id
            in {
                DOWNTIME.candidate_id,
                DEPARTMENT.candidate_id,
                EVENT_DATE.candidate_id,
                ASSEMBLY.candidate_id,
                PACKAGING.candidate_id,
            }
        ),
    )
    narrowed=apply_scope_mutation(
        current,
        ScopeMutation(
            kind=ScopeMutationKind.NARROW_ENTITY,
            source_version_id="scope_v1",
            target_semantic_refs=(DOWNTIME,DEPARTMENT,EVENT_DATE,ASSEMBLY),
            target_time_surfaces=("June 2026",),
            target_periods=(JUNE,),
            target_temporal_dimension_ids=(EVENT_DATE.candidate_id,),
            target_native_verification_bindings=tuple(
                item
                for item in VERIFICATION_BINDINGS
                if item.candidate_id
                in {
                    DOWNTIME.candidate_id,
                    DEPARTMENT.candidate_id,
                    EVENT_DATE.candidate_id,
                    ASSEMBLY.candidate_id,
                }
            ),
            reason="Narrow to Assembly.",
        ),
    )
    assert narrowed.current_scope.periods == (JUNE,)
    assert narrowed.current_scope.scope_version.version_id == "scope_v2"


def test_r1_entity_narrowing_cannot_silently_drop_period():
    current=ResearchScope(
        semantic_refs=(DOWNTIME,DEPARTMENT,EVENT_DATE,ASSEMBLY,PACKAGING),
        time_surfaces=("June 2026",),
        periods=(JUNE,),
        temporal_dimension_ids=(EVENT_DATE.candidate_id,),
        native_verification_bindings=tuple(
            item
            for item in VERIFICATION_BINDINGS
            if item.candidate_id
            in {
                DOWNTIME.candidate_id,
                DEPARTMENT.candidate_id,
                EVENT_DATE.candidate_id,
                ASSEMBLY.candidate_id,
                PACKAGING.candidate_id,
            }
        ),
    )
    with pytest.raises(ValueError, match="typed period authority"):
        apply_scope_mutation(
            current,
            ScopeMutation(
                kind=ScopeMutationKind.NARROW_ENTITY,
                source_version_id="scope_v1",
                target_semantic_refs=(DOWNTIME,DEPARTMENT,EVENT_DATE,ASSEMBLY),
                target_time_surfaces=("June 2026",),
                target_periods=(),
                target_temporal_dimension_ids=(EVENT_DATE.candidate_id,),
                target_native_verification_bindings=tuple(
                    item
                    for item in VERIFICATION_BINDINGS
                    if item.candidate_id
                    in {
                        DOWNTIME.candidate_id,
                        DEPARTMENT.candidate_id,
                        EVENT_DATE.candidate_id,
                        ASSEMBLY.candidate_id,
                    }
                ),
                reason="Illegal scope broadening by period loss.",
            ),
        )


def test_r1_ranking_comparison_and_multi_metric_survive_projection():
    ranked=analytical_scope_contract(
        session=session(ranking=True),
        obligation_id="g_scope",
    )
    assert ranked.ranking is not None
    assert ranked.ranking.measure == "metric.downtime"
    assert ranked.ranking.direction == "desc"
    assert ranked.ranking.limit == 3

    compared=analytical_scope_contract(
        session=session(
            metrics=(DOWNTIME,FAULTS),
            periods=(MAY,JUNE),
            comparison=True,
        ),
        obligation_id="g_scope",
    )
    assert compared.metric_refs == ("metric.downtime","metric.faults")
    assert compared.comparison is not None
    assert compared.comparison.reference_period.start == "2026-05-01"
    assert compared.comparison.base_period.end == "2026-07-01"


def test_r1_scope_v1_material_cannot_satisfy_scope_v2_contract():
    v1=analytical_scope_contract(session=session(version=1),obligation_id="g_scope")
    v2=analytical_scope_contract(session=session(version=2),obligation_id="g_scope")
    with pytest.raises(AnalyticalRequestMismatch,match="SCOPE"):
        assert_request_invariants(v2,observation_from_contract(v1))


def test_r1_attested_native_scope_accepts_exact_june_department_request():
    current=session()
    contract=analytical_scope_contract(session=current,obligation_id="g_scope")
    observed=assert_attested_native_scope(
        session=current,
        obligation_id="g_scope",
        contract=contract,
        attestation=attestation(),
        field_locators=LOCATORS,
        table_locators=TABLE_LOCATORS,
        expected_engine=ENGINE,
        expected_metabase_subject=77,
    )
    assert observed.request.period == contract.period
    assert observed.request.dimension_refs == ("dimension.department",)


def test_r1_attested_native_scope_rejects_implicit_time_broadening():
    current=session()
    contract=analytical_scope_contract(session=current,obligation_id="g_scope")
    with pytest.raises(
        ResearchAnalyticalScopeError,
        match="R1_NATIVE_TIME_SCOPE_MISMATCH",
    ):
        assert_attested_native_scope(
            session=current,
            obligation_id="g_scope",
            contract=contract,
            attestation=attestation(time=False),
            field_locators=LOCATORS,
            table_locators=TABLE_LOCATORS,
            expected_engine=ENGINE,
            expected_metabase_subject=77,
        )


def test_r1_attested_native_scope_rejects_entity_filter_loss():
    current=session(entities=(ASSEMBLY,))
    contract=analytical_scope_contract(session=current,obligation_id="g_scope")
    with pytest.raises(
        ResearchAnalyticalScopeError,
        match="R1_NATIVE_FILTER_SCOPE_MISMATCH",
    ):
        assert_attested_native_scope(
            session=current,
            obligation_id="g_scope",
            contract=contract,
            attestation=attestation(),
            field_locators=LOCATORS,
            table_locators=TABLE_LOCATORS,
            expected_engine=ENGINE,
            expected_metabase_subject=77,
        )


def test_r1_comparison_attestation_preserves_period_coverage_and_multi_metric():
    current=session(
        metrics=(DOWNTIME,FAULTS),
        periods=(MAY,JUNE),
        comparison=True,
    )
    contract=analytical_scope_contract(session=current,obligation_id="g_scope")
    observed=assert_attested_native_scope(
        session=current,
        obligation_id="g_scope",
        contract=contract,
        attestation=attestation(
            metric_field_ids=(101,102),
            breakout_field_ids=(201,301),
            start="2026-05-01",
            end="2026-07-01",
        ),
        field_locators=LOCATORS,
        table_locators=TABLE_LOCATORS,
        expected_engine=ENGINE,
        expected_metabase_subject=77,
    )
    assert observed.request.metric_refs == ("metric.downtime","metric.faults")
    assert observed.request.comparison is not None


class FakeTransport:
    def __init__(self,payload):
        self.payload=payload
        self.call_count=0
        self.last=None

    def structured_json(self,system,user,*,schema,schema_name):
        self.call_count+=1
        self.last={"system":system,"user":json.loads(user),"schema":schema}
        return json.dumps(self.payload)


def test_r1_intake_freezes_typed_period_and_hides_native_binding_from_cognition():
    payload={
        "terminal":"READY",
        "objective":"June downtime.",
        "goals":[{
            "goal_key":"g1",
            "kind":"breakdown",
            "source_text":"June downtime by department.",
            "allowed_relationship_id":None,
            "subject_semantic_ids":["metric.downtime"],
            "related_semantic_ids":["dimension.department"],
            "ranking":None,
            "comparison_texts":[],
        }],
        "deliverables":[],
        "investigation_directives":[],
        "time_surfaces":["June 2026"],
        "time_periods":[{
            "source_text":"June 2026",
            "time_dimension_semantic_id":"dimension.event_date",
            "start":"2026-06-01",
            "end":"2026-07-01",
        }],
        "required_domains":["machine_operations"],
        "scope_mutation_kind":None,
        "clarification_question":None,
        "unsupported_reason":None,
    }
    transport=FakeTransport(payload)
    catalog=ResearchIntakeCatalog(
        context_version="ctx-r1",
        semantic_refs=(DOWNTIME,DEPARTMENT,EVENT_DATE),
        allowed_relationships=(),
        supported_domains=("machine_operations",),
        temporal_dimension_ids=(EVENT_DATE.candidate_id,),
        native_verification_bindings=tuple(
            item
            for item in VERIFICATION_BINDINGS
            if item.candidate_id
            in {
                DOWNTIME.candidate_id,
                DEPARTMENT.candidate_id,
                EVENT_DATE.candidate_id,
            }
        ),
    )
    result=ResearchIntakeCompiler(transport=transport).compile(
        question="June downtime by department.",
        catalog=catalog,
    )
    assert result.brief is not None
    assert result.brief.scope.periods == (JUNE,)
    provider_payload=json.dumps(transport.last["user"])
    assert "native_verification_bindings" not in provider_payload

    schema=_intake_provider_schema(catalog)
    period=schema["$defs"]["ModelTimePeriodDraft"]
    assert set(
        period["properties"]["time_dimension_semantic_id"]["enum"]
    ) == {"dimension.event_date"}


def test_r1_intake_rejects_text_time_without_typed_period():
    payload={
        "terminal":"READY",
        "objective":"June downtime.",
        "goals":[{
            "goal_key":"g1",
            "kind":"breakdown",
            "source_text":"June downtime.",
            "allowed_relationship_id":None,
            "subject_semantic_ids":["metric.downtime"],
            "related_semantic_ids":["dimension.department"],
            "ranking":None,
            "comparison_texts":[],
        }],
        "deliverables":[],
        "investigation_directives":[],
        "time_surfaces":["June 2026"],
        "time_periods":[],
        "required_domains":["machine_operations"],
        "scope_mutation_kind":None,
        "clarification_question":None,
        "unsupported_reason":None,
    }
    catalog=ResearchIntakeCatalog(
        context_version="ctx-r1",
        semantic_refs=(DOWNTIME,DEPARTMENT,EVENT_DATE),
        allowed_relationships=(),
        supported_domains=("machine_operations",),
        temporal_dimension_ids=(EVENT_DATE.candidate_id,),
        native_verification_bindings=tuple(
            item
            for item in VERIFICATION_BINDINGS
            if item.candidate_id
            in {
                DOWNTIME.candidate_id,
                DEPARTMENT.candidate_id,
                EVENT_DATE.candidate_id,
            }
        ),
    )
    with pytest.raises(
        ResearchIntakeError,
        match="INTAKE_TIME_SCOPE_BINDING_REQUIRED",
    ):
        ResearchIntakeCompiler(transport=FakeTransport(payload)).compile(
            question="June downtime.",
            catalog=catalog,
        )
