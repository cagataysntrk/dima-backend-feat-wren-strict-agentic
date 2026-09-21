"""Focused P7 tests.

The primary correctness proof is intentionally NOT the repository demo database:
- two schema-permuted synthetic tenants exercise the same natural conversation,
- canonical names differ from user language,
- real Wren is a secondary dynamic-schema boundary smoke only.
"""

from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

import pytest

from app.contracts import result_hash
from app.v2.context_provider import ContextProviderV0
from app.v2.conversation import ConversationCoordinatorV0, ledger_from_ir
from app.v2.cube_planner import CubePlanner, ResultValidator
from app.v2.interpreter import TurnInterpreter
from app.v2.models import (
    AnalyticalRequest,
    AnalyticsIR,
    AskV2Request,
    CandidateSource,
    ConversationStateV2,
    DialogueAction,
    FocusStateV0,
    ResolvedFilterRef,
    ResolvedSemanticRef,
    ResolutionStatus,
    ResultAnchorV0,
    ResultExecutionAnchorV0,
    SemanticAnchor,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMention,
    SemanticMentionKind,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
    TurnAct,
    TurnInterpretation,
    UserRepair,
)
from app.v2.orchestrator import V2Orchestrator
from app.v2.temporal import resolve_period
from control_plane.authorize import Principal


SPECS = (
    {
        "cube": "fact_alpha",
        "metric": "efficiency_score_z",
        "metric_display": "Hat Verimliliği",
        "metric_surface": "verimlilik",
        "dimension": "asset_axis_q",
        "dimension_display": "Hat",
        "dimension_surface": "hat",
        "entity": "AX-17",
        "time_axis": "event_clock_v2",
        "q1": "bu sene hatlara göre verimlilik nasıl gidiyor?",
        "q2": "yalnız AX-17 olsun",
    },
    {
        "cube": "ledger_beta",
        "metric": "net_value_k",
        "metric_display": "Net Satış",
        "metric_surface": "net gelir",
        "dimension": "region_axis_m",
        "dimension_display": "Bölge",
        "dimension_surface": "bölge",
        "entity": "Kuzey-4",
        "time_axis": "booked_on_z",
        "q1": "bu sene bölgelerde net gelir nasıl gidiyor?",
        "q2": "yalnız Kuzey-4 olsun",
    },
)


def schema_for(spec: dict) -> dict:
    return {
        "catalog": "synthetic",
        "schema_name": "main",
        "models": [
            {
                "name": f"{spec['cube']}_source",
                "columns": [
                    {"name": spec["dimension"], "type": "VARCHAR"},
                    {"name": spec["time_axis"], "type": "DATE"},
                ],
            }
        ],
        "cubes": [
            {
                "name": spec["cube"],
                "display": "Synthetic Business Fact",
                "synonyms": ["operasyon"],
                "measures": [spec["metric"]],
                "measure_synonyms": {
                    spec["metric"]: [spec["metric_surface"]],
                },
                "measure_synonyms_display": {
                    spec["metric"]: spec["metric_display"],
                },
                "units": {spec["metric"]: "%"},
                "dimensions": [spec["dimension"]],
                "dimension_labels": {
                    spec["dimension"]: spec["dimension_display"],
                },
                "dimension_synonyms": {
                    spec["dimension"]: [spec["dimension_surface"]],
                },
                "dimension_values": {
                    spec["dimension"]: [spec["entity"], "OTHER-92"],
                },
                "time_dimensions": [spec["time_axis"]],
            }
        ],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


class SyntheticService:
    def __init__(self, spec: dict):
        self.spec = spec
        self.mdl_version = f"mdl-{spec['cube']}"
        self.query_calls = 0
        self.dry_calls = 0
        self.principals = []

    def schema(self):
        return schema_for(self.spec)

    def cube_sql(self, cube_query: dict) -> str:
        return "CQ:" + json.dumps(cube_query, ensure_ascii=False, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        self.dry_calls += 1
        self.principals.append(("dry", principal))
        assert sql.startswith("CQ:")
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        self.principals.append(("query", principal))
        cq = json.loads(sql[3:])
        dims = list(cq.get("dimensions") or ())
        measures = list(cq.get("measures") or ())
        columns = [*dims, *measures]

        values = list(
            self.schema()["cubes"][0]["dimension_values"].get(dims[0], [])
        ) if dims else [None]
        for flt in cq.get("filters") or ():
            if dims and flt.get("dimension") == dims[0] and flt.get("operator") == "eq":
                values = [flt.get("value")]

        rows = []
        for idx, value in enumerate(values or [None]):
            row = {}
            if dims:
                row[dims[0]] = value
            for metric in measures:
                row[metric] = float(100 - idx * 10)
            rows.append(row)

        order = cq.get("order") or {}
        measure = order.get("measure")
        if measure:
            rows.sort(
                key=lambda row: row.get(measure, 0),
                reverse=order.get("direction") == "desc",
            )
        if cq.get("limit") is not None:
            rows = rows[: int(cq["limit"])]

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "column_types": ["VARCHAR" if c in dims else "DOUBLE" for c in columns],
        }


class SequenceLLM:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = 0
        self.users = []

    def structured_text(self, system: str, user: str) -> str:
        self.calls += 1
        self.users.append(user)
        if not self.outputs:
            raise AssertionError("unexpected LLM call")
        return json.dumps(self.outputs.pop(0), ensure_ascii=False)


class FakeContracts:
    def __init__(self):
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {
            "id": f"c-synth-{self.n}",
            "result_hash": result_hash(kwargs["result"]),
            "durability": "db",
            "sealed": True,
        }


def outputs_for(spec: dict):
    return [
        {
            "dialogue_act": "ANALYTIC_NEW",
            "analytical_request": {
                "metric_mentions": [
                    {"text": spec["metric_surface"], "kind": "metric"},
                ],
                "dimension_mentions": [
                    {"text": spec["dimension_surface"], "kind": "dimension"},
                ],
                "time_mentions": [{"text": "bu sene", "kind": "time"}],
            },
        },
        {
            "dialogue_act": "ANALYTIC_REFINE",
            "analytical_request": {
                "filter_mentions": [
                    {"text": spec["entity"], "kind": "filter"},
                ],
            },
        },
        {
            "dialogue_act": "USER_REPAIR",
            "analytical_request": {
                "time_mentions": [{"text": "son üç ay", "kind": "time"}],
            },
            "user_repair": {
                "correction_spans": ["yok", "son üç ay"],
            },
        },
        {
            "dialogue_act": "RESULT_EXPLAIN",
            "references": [{"text": "bu sonucu", "kind": "prior_result"}],
            "presentation_request": "explain",
        },
        {"dialogue_act": "SOCIAL"},
    ]


def principal():
    return Principal(
        user_id="user-synthetic",
        tenant_id="tenant-synthetic",
        roles=["owner"],
        tenant_slug="synthetic",
    )


def request_for(llm, contracts):
    return SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                llm=llm,
                contracts=contracts,
            )
        )
    )


def run_turn(orchestrator, request, p, q, conversation):
    return orchestrator.handle(
        request,
        AskV2Request(
            question=q,
            session_id="session-natural",
            thread_id="thread-natural",
            conversation=conversation,
        ),
        p,
    )


@pytest.mark.parametrize("spec", SPECS)
def test_natural_five_turn_thread_is_schema_permutation_invariant(spec, monkeypatch):
    """Same user-level invariant must survive unrelated canonical schema names."""
    import app.v2.orchestrator as module

    service = SyntheticService(spec)
    llm = SequenceLLM(outputs_for(spec))
    contracts = FakeContracts()
    monkeypatch.setattr(module, "wren_for_request", lambda request: service)

    orchestrator = V2Orchestrator()
    p = principal()
    req = request_for(llm, contracts)
    state = ConversationStateV2()

    first = run_turn(orchestrator, req, p, spec["q1"], state)
    assert first.dialogue_action == DialogueAction.ANALYTIC_STANDARD
    assert first.official_verified is True
    assert first.query_execution_count == 1
    state = first.conversation

    assert state.last_ir is not None
    first_ir = state.last_ir
    assert first_ir.cube == spec["cube"]
    assert first_ir.metrics[0].canonical_name == spec["metric"]
    assert first_ir.dimensions[0].canonical_name == spec["dimension"]
    assert first_ir.period is not None
    assert first_ir.period.kind.value == "this_year"

    second = run_turn(orchestrator, req, p, spec["q2"], state)
    assert second.dialogue_action == DialogueAction.ANALYTIC_STANDARD
    assert second.query_execution_count == 1
    state = second.conversation
    second_ir = state.last_ir
    assert second_ir.metrics == first_ir.metrics
    assert second_ir.dimensions == first_ir.dimensions
    assert second_ir.period == first_ir.period
    assert len(second_ir.filters) == 1
    assert second_ir.filters[0].dimension_name == spec["dimension"]
    assert second_ir.filters[0].value == spec["entity"]

    third = run_turn(
        orchestrator,
        req,
        p,
        "yok, son üç ay olsun",
        state,
    )
    assert third.dialogue_action == DialogueAction.ANALYTIC_STANDARD
    assert third.query_execution_count == 1
    state = third.conversation
    third_ir = state.last_ir
    assert third_ir.metrics == second_ir.metrics
    assert third_ir.dimensions == second_ir.dimensions
    assert third_ir.filters == second_ir.filters
    assert third_ir.period is not None
    assert third_ir.period.kind.value == "last_n_months"
    assert third_ir.period.n == 3

    before_explain_queries = service.query_calls
    fourth = run_turn(
        orchestrator,
        req,
        p,
        "bu sonucu biraz yorumlar mısın?",
        state,
    )
    assert fourth.dialogue_action == DialogueAction.EXPLAIN_EXISTING
    assert fourth.query_execution_count == 0
    assert fourth.used_existing_result is True
    assert fourth.existing_result is not None
    assert service.query_calls == before_explain_queries

    fifth = run_turn(orchestrator, req, p, "sağ ol", fourth.conversation)
    assert fifth.dialogue_action == DialogueAction.TALK
    assert fifth.query_execution_count == 0
    assert service.query_calls == before_explain_queries

    # Three analytical turns only. Explain/social cannot touch data.
    assert service.query_calls == 3
    assert service.dry_calls == 3
    assert all(bound is p for _, bound in service.principals)

    # Day4 delta contract: current message only, no replay of prior surface slots by LLM.
    repair_turn = third.turn
    assert repair_turn is not None
    assert repair_turn.dialogue_act == TurnAct.USER_REPAIR
    assert repair_turn.analytical_request.metric_mentions == ()
    assert repair_turn.analytical_request.dimension_mentions == ()
    assert repair_turn.analytical_request.filter_mentions == ()
    assert repair_turn.analytical_request.time_mentions[0].text == "son üç ay"


def ambiguity_schema() -> dict:
    return {
        "catalog": "synthetic",
        "schema_name": "main",
        "models": [
            {
                "name": "fact_gamma_source",
                "columns": [
                    {"name": "tier_axis_a", "type": "VARCHAR"},
                    {"name": "account_axis_b", "type": "VARCHAR"},
                ],
            }
        ],
        "cubes": [
            {
                "name": "fact_gamma",
                "display": "Risk Fact",
                "measures": ["loss_score_x"],
                "measure_synonyms": {"loss_score_x": ["kayıp"]},
                "measure_synonyms_display": {"loss_score_x": "Kayıp"},
                "units": {"loss_score_x": "kg"},
                "dimensions": ["tier_axis_a", "account_axis_b"],
                "dimension_labels": {
                    "tier_axis_a": "Segment",
                    "account_axis_b": "Hesap",
                },
                "dimension_synonyms": {
                    "tier_axis_a": ["segment"],
                    "account_axis_b": ["hesap"],
                },
                "dimension_values": {
                    "tier_axis_a": ["Prime"],
                    "account_axis_b": ["Prime"],
                },
                "time_dimensions": ["event_day_c"],
            }
        ],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


class AmbiguityService(SyntheticService):
    def __init__(self):
        self.spec = {
            "cube": "fact_gamma",
            "metric": "loss_score_x",
            "dimension": "tier_axis_a",
            "time_axis": "event_day_c",
        }
        self.mdl_version = "mdl-fact-gamma"
        self.query_calls = 0
        self.dry_calls = 0
        self.principals = []

    def schema(self):
        return ambiguity_schema()


def initial_ambiguity_output():
    return {
        "dialogue_act": "ANALYTIC_NEW",
        "analytical_request": {
            "metric_mentions": [{"text": "kayıp", "kind": "metric"}],
            "filter_mentions": [{"text": "Prime", "kind": "filter"}],
        },
    }


def test_signed_clarification_resume_preserves_sibling_metric_and_executes_once(monkeypatch):
    import app.v2.orchestrator as module

    service = AmbiguityService()
    llm = SequenceLLM([initial_ambiguity_output()])
    monkeypatch.setattr(module, "wren_for_request", lambda request: service)
    orchestrator = V2Orchestrator()
    req = request_for(llm, FakeContracts())
    p = principal()

    first = run_turn(
        orchestrator,
        req,
        p,
        "Prime için kayıp ne durumda?",
        ConversationStateV2(),
    )
    assert first.dialogue_action == DialogueAction.CLARIFY
    assert first.query_execution_count == 0
    assert first.conversation.pending_analytical is not None

    chip = next(
        item for item in first.clarification.chips
        if item.label.startswith("Segment")
    )
    resumed = orchestrator.handle(
        req,
        AskV2Request(
            question="segment olanı seç",
            session_id="session-natural",
            thread_id="thread-natural",
            conversation=first.conversation,
            clarification_token=chip.token,
        ),
        p,
    )

    assert resumed.official_verified is True
    assert resumed.resumed_by == "signed_chip"
    assert resumed.query_execution_count == 1
    assert resumed.analytics_ir.metrics[0].canonical_name == "loss_score_x"
    assert resumed.analytics_ir.filters[0].dimension_name == "tier_axis_a"
    assert resumed.analytics_ir.filters[0].value == "Prime"
    assert resumed.conversation.pending_analytical is None
    assert service.query_calls == 1


def test_free_text_clarification_resume_preserves_original_request(monkeypatch):
    import app.v2.orchestrator as module

    service = AmbiguityService()
    llm = SequenceLLM(
        [
            initial_ambiguity_output(),
            {
                "dialogue_act": "CLARIFICATION_ANSWER",
                "analytical_request": {
                    "filter_mentions": [{"text": "segment", "kind": "filter"}],
                },
            },
        ]
    )
    monkeypatch.setattr(module, "wren_for_request", lambda request: service)
    orchestrator = V2Orchestrator()
    req = request_for(llm, FakeContracts())
    p = principal()

    first = run_turn(
        orchestrator,
        req,
        p,
        "Prime için kayıp ne durumda?",
        ConversationStateV2(),
    )
    resumed = run_turn(
        orchestrator,
        req,
        p,
        "segment olan",
        first.conversation,
    )

    assert resumed.official_verified is True
    assert resumed.resumed_by == "free_text"
    assert resumed.analytics_ir.metrics[0].canonical_name == "loss_score_x"
    assert resumed.analytics_ir.filters[0].dimension_name == "tier_axis_a"
    assert service.query_calls == 1


def test_same_dimension_filter_replaces_only_that_slot():
    coordinator = ConversationCoordinatorV0()
    prior = AnalyticsIR(
        cube="fact_delta",
        metrics=(
            ResolvedSemanticRef(
                candidate_id="m",
                target_kind=SemanticTargetKind.METRIC,
                canonical_name="measure_delta",
                cube_names=("fact_delta",),
            ),
        ),
        filters=(
            ResolvedFilterRef(
                candidate_id="f-region-old",
                dimension_name="region_delta",
                value="North",
                cube_names=("fact_delta",),
            ),
            ResolvedFilterRef(
                candidate_id="f-channel",
                dimension_name="channel_delta",
                value="Web",
                cube_names=("fact_delta",),
            ),
        ),
        context_version="ctx-delta",
    )
    turn = TurnInterpretation(
        dialogue_act=TurnAct.USER_REPAIR,
        analytical_request=AnalyticalRequest(
            filter_mentions=(
                SemanticMention(text="South", kind=SemanticMentionKind.FILTER),
            )
        ),
        user_repair=UserRepair(correction_spans=("South",)),
    )
    cand = SemanticCandidate(
        candidate_id="f-region-new",
        target_kind=SemanticTargetKind.ENTITY_VALUE,
        canonical_name="region_delta",
        dimension_name="region_delta",
        value="South",
        cube_names=("fact_delta",),
        display_label="Region = South",
        provenance=(CandidateSource.EXACT_ENTITY_VALUE,),
        score=1.0,
        material=True,
    )
    hyp = SemanticHypothesis(
        source_mention="South",
        mention_kind=SemanticMentionKind.FILTER,
        status=ResolutionStatus.RESOLVED,
        candidates=(cand,),
        resolved_candidate_id=cand.candidate_id,
        resolved_surface_value="South",
    )
    schema = {
        "cubes": [
            {
                "name": "fact_delta",
                "measures": ["measure_delta"],
                "dimensions": ["region_delta", "channel_delta"],
                "time_dimensions": ["event_delta"],
            }
        ]
    }
    updated = coordinator.apply_delta(
        prior_ir=prior,
        turn=turn,
        hypotheses=(hyp,),
        schema=schema,
        context_version="ctx-delta",
    )
    values = {(item.dimension_name, item.value) for item in updated.filters}
    assert values == {("region_delta", "South"), ("channel_delta", "Web")}
    assert updated.metrics == prior.metrics


def test_interpreter_prompt_does_not_dump_prior_result_rows_or_sensitive_filter_values():
    secret = "PRIVATE-ENTITY-9471"
    state = ConversationStateV2(
        has_prior_analytical_request=True,
        has_active_result=True,
        focus=FocusStateV0(
            filters=(
                ResolvedFilterRef(
                    candidate_id="sensitive",
                    dimension_name="person_axis_x",
                    value=secret,
                    sensitive=True,
                ),
            )
        ),
        focus_anchors=(
            SemanticAnchor(
                target_kind=SemanticTargetKind.ENTITY_VALUE,
                canonical_name="person_axis_x",
                dimension_name="person_axis_x",
                value=secret,
                display_label="Person",
                sensitive=True,
            ),
        ),
        last_ir=AnalyticsIR(
            cube="fact_private",
            filters=(
                ResolvedFilterRef(
                    candidate_id="sensitive",
                    dimension_name="person_axis_x",
                    value=secret,
                    sensitive=True,
                ),
            ),
            context_version="ctx-private",
        ),
        last_result=ResultAnchorV0(
            contract_refs=("c-private",),
            result_hashes=("hash",),
            executions=(
                ResultExecutionAnchorV0(
                    execution_id="x-private",
                    role="primary",
                    columns=("person_axis_x",),
                    rows=({"person_axis_x": secret},),
                    row_count=1,
                ),
            ),
            verified=True,
        ),
    )

    class CaptureLLM:
        def __init__(self):
            self.user = ""

        def structured_text(self, system, user):
            self.user = user
            return json.dumps({"dialogue_act": "SOCIAL"})

    llm = CaptureLLM()
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id="t",
        tenant_slug="synthetic",
        principal_user_id="u",
        roles=("owner",),
        mdl_version="mdl-safe",
        catalog="synthetic",
        schema_name="main",
        db_online=True,
    )

    class SafeService:
        mdl_version = "mdl-safe"

        def schema(self):
            return {
                "catalog": "synthetic",
                "schema_name": "main",
                "cubes": [],
                "kpis": [],
                "relationships": [],
                "business_rules": "",
                "db_online": True,
            }

    context = ContextProviderV0().build(SafeService(), runtime)
    TurnInterpreter().interpret(
        question="sağ ol",
        semantic_context=context,
        conversation=state,
        llm=llm,
    )
    assert secret not in llm.user
    assert "rows" not in llm.user
    assert "person_axis_x" in llm.user


def test_day4_production_conversation_code_contains_no_fixture_literal_dependencies():
    import app.v2.conversation as conversation_module
    import app.v2.dialogue_policy as policy_module
    import app.v2.orchestrator as orchestrator_module

    source = "\n".join(
        inspect.getsource(module).casefold()
        for module in (conversation_module, policy_module, orchestrator_module)
    )
    for literal in (
        "demo-boyahane",
        "ram-3",
        "toplam_ciro",
        "ort_oee",
        "fact_alpha",
        "efficiency_score_z",
        "ax-17",
    ):
        assert literal not in source


def test_dynamic_real_wren_time_repair_smoke_has_no_demo_literal_assumption(
    wren, schema, _test_kimligi
):
    """Secondary boundary smoke: choose capability from schema instead of naming demo fields."""
    eligible = next(
        (
            cube
            for cube in schema.get("cubes") or ()
            if cube.get("measures") and len(cube.get("time_dimensions") or ()) == 1
        ),
        None,
    )
    assert eligible is not None, "real demo schema has no basic metric+time capability"

    cube_name = str(eligible["name"])
    metric_name = str(eligible["measures"][0])
    time_axis = str(eligible["time_dimensions"][0])
    ctx = "ctx-dynamic-real"

    prior = AnalyticsIR(
        cube=cube_name,
        metrics=(
            ResolvedSemanticRef(
                candidate_id="dynamic-metric",
                target_kind=SemanticTargetKind.METRIC,
                canonical_name=metric_name,
                cube_names=(cube_name,),
            ),
        ),
        period=resolve_period(
            (SemanticMention(text="bu yıl", kind=SemanticMentionKind.TIME),),
            time_dimension=time_axis,
        ),
        context_version=ctx,
    )
    repair = TurnInterpretation(
        dialogue_act=TurnAct.USER_REPAIR,
        analytical_request=AnalyticalRequest(
            time_mentions=(
                SemanticMention(text="son üç ay", kind=SemanticMentionKind.TIME),
            )
        ),
        user_repair=UserRepair(correction_spans=("son üç ay",)),
    )
    ir = ConversationCoordinatorV0().apply_delta(
        prior_ir=prior,
        turn=repair,
        hypotheses=(),
        schema=schema,
        context_version=ctx,
    )
    ledger = ledger_from_ir(ir)
    plans, ledger = CubePlanner().plan(ir=ir, ledger=ledger, service=wren)
    assert len(plans) == 1

    wren.dry_plan(plans[0].sql, principal=_test_kimligi)
    result = wren.query(plans[0].sql, principal=_test_kimligi)
    ledger, errors = ResultValidator().validate(
        ir=ir,
        ledger=ledger,
        plans=plans,
        results=(result,),
    )
    assert errors == ((),)
    assert ledger.all_must_verified



def test_self_contained_cross_cube_refine_rebases_without_topic_stack():
    old, new = SPECS
    old_metric = ResolvedSemanticRef(
        candidate_id="old-metric",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=old["metric"],
        cube_names=(old["cube"],),
    )
    old_dimension = ResolvedSemanticRef(
        candidate_id="old-dimension",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=old["dimension"],
        cube_names=(old["cube"],),
    )
    prior = AnalyticsIR(
        cube=old["cube"],
        metrics=(old_metric,),
        dimensions=(old_dimension,),
        context_version="ctx-switch",
    )
    turn = TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_REFINE,
        analytical_request=AnalyticalRequest(
            metric_mentions=(
                SemanticMention(
                    text=new["metric_surface"],
                    kind=SemanticMentionKind.METRIC,
                ),
            ),
            dimension_mentions=(
                SemanticMention(
                    text=new["dimension_surface"],
                    kind=SemanticMentionKind.DIMENSION,
                ),
            ),
            time_mentions=(
                SemanticMention(text="bu sene", kind=SemanticMentionKind.TIME),
            ),
        ),
    )

    metric_candidate = SemanticCandidate(
        candidate_id="new-metric",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=new["metric"],
        cube_names=(new["cube"],),
        display_label=new["metric_display"],
        provenance=(CandidateSource.VERIFIED_SYNONYM,),
        score=1.0,
        material=True,
    )
    dimension_candidate = SemanticCandidate(
        candidate_id="new-dimension",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=new["dimension"],
        cube_names=(new["cube"],),
        display_label=new["dimension_display"],
        provenance=(CandidateSource.VERIFIED_SYNONYM,),
        score=1.0,
        material=True,
    )
    hypotheses = (
        SemanticHypothesis(
            source_mention=new["metric_surface"],
            mention_kind=SemanticMentionKind.METRIC,
            status=ResolutionStatus.RESOLVED,
            candidates=(metric_candidate,),
            resolved_candidate_id=metric_candidate.candidate_id,
        ),
        SemanticHypothesis(
            source_mention=new["dimension_surface"],
            mention_kind=SemanticMentionKind.DIMENSION,
            status=ResolutionStatus.RESOLVED,
            candidates=(dimension_candidate,),
            resolved_candidate_id=dimension_candidate.candidate_id,
        ),
    )
    first = schema_for(old)
    second = schema_for(new)
    schema = {
        **first,
        "models": [*first["models"], *second["models"]],
        "cubes": [*first["cubes"], *second["cubes"]],
    }

    ir, ledger = V2Orchestrator()._effective_ir(
        turn=turn,
        hypotheses=hypotheses,
        schema=schema,
        context_version="ctx-switch",
        prior_ir=prior,
    )

    assert ir.cube == new["cube"]
    assert [item.canonical_name for item in ir.metrics] == [new["metric"]]
    assert [item.canonical_name for item in ir.dimensions] == [new["dimension"]]
    assert ir.period is not None and ir.period.kind == "this_year"
    assert ledger.all_must_verified is False


def test_empty_analytic_continuation_cannot_reach_query(monkeypatch):
    """Even a language-label miss with zero analytical delta is fail-closed before Wren."""
    import app.v2.orchestrator as module

    spec = SPECS[0]
    service = SyntheticService(spec)
    llm = SequenceLLM(
        [
            outputs_for(spec)[0],
            {
                "dialogue_act": "ANALYTIC_REFINE",
                "analytical_request": {},
            },
        ]
    )
    monkeypatch.setattr(module, "wren_for_request", lambda request: service)

    orchestrator = V2Orchestrator()
    req = request_for(llm, FakeContracts())
    p = principal()

    first = run_turn(
        orchestrator,
        req,
        p,
        spec["q1"],
        ConversationStateV2(),
    )
    assert first.official_verified is True
    assert service.query_calls == 1

    second = run_turn(
        orchestrator,
        req,
        p,
        "tamamdır",
        first.conversation,
    )
    assert second.official_verified is False
    assert second.analytics_status == "not_executable"
    assert second.failure is not None
    assert second.failure.code == "empty_refinement_delta"
    assert second.query_execution_count == 0
    assert service.query_calls == 1
