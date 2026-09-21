"""Focused P6 tests: IR completeness, deterministic planning, official execution and seal."""

from __future__ import annotations

import inspect
import json
import time
from datetime import date
from types import SimpleNamespace

import pytest

from app import mali_takvim
from app.contracts import ContractStore, result_hash
from app.v2.cube_planner import (
    AnalyticsIRBuilder,
    CubePlanner,
    ResultValidator,
    StandardAnalyticsError,
)
from app.v2.models import (
    AnalyticalRequest,
    AskV2Request,
    CandidateSource,
    ComparisonSurface,
    ContextVersionV0,
    RankingSurface,
    RequirementKind,
    RequirementLedger,
    RequirementLedgerItem,
    RequirementState,
    ResolvedPeriod,
    ResolutionStatus,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMention,
    SemanticMentionKind,
    SemanticTargetKind,
    TurnAct,
    TurnInterpretation,
)
from app.v2.orchestrator import V2Orchestrator
from app.v2.temporal import period_filters, resolve_comparison, resolve_period
from control_plane.authorize import Principal


REAL_DEMO_LATENCIES: list[float] = []


CTX = ContextVersionV0(
    version="ctx-day3",
    mdl_version="mdl-day3",
    compact_catalog_builder_version="v0.1",
    business_rules_hash="rules",
    prompt_context_policy_version="v0.1",
)


def fake_schema(*, duplicate_parti: bool = False, time_axes=("tarih",)) -> dict:
    cubes = [
        {
            "name": "parti",
            "display": "Parti",
            "measures": ["toplam_ciro", "toplam_fire_kg"],
            "dimensions": ["musteri", "makine", "renk"],
            "time_dimensions": list(time_axes),
            "measure_synonyms": {
                "toplam_ciro": ["ciro"],
                "toplam_fire_kg": ["fire"],
            },
            "measure_synonyms_display": {
                "toplam_ciro": "Ciro",
                "toplam_fire_kg": "Fire",
            },
            "dimension_synonyms": {
                "musteri": ["müşteri"],
                "makine": ["makine"],
                "renk": ["renk"],
            },
            "dimension_labels": {
                "musteri": "Müşteri",
                "makine": "Makine",
                "renk": "Renk",
            },
            "dimension_values": {
                "renk": ["Siyah", "Mavi"],
                "makine": ["RAM-3", "RAM-4"],
            },
            "units": {"toplam_ciro": "TRY", "toplam_fire_kg": "kg"},
        }
    ]
    if duplicate_parti:
        cubes.append(
            {
                **cubes[0],
                "name": "parti_clone",
            }
        )
    return {
        "catalog": "demo",
        "schema_name": "main",
        "models": [
            {
                "name": "partiler",
                "columns": [
                    {"name": "renk", "type": "VARCHAR"},
                    {"name": "makine", "type": "VARCHAR"},
                    {"name": "musteri", "type": "VARCHAR"},
                ],
            }
        ],
        "cubes": cubes,
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


def candidate(
    *,
    cid: str,
    target: SemanticTargetKind,
    canonical: str,
    cubes=("parti",),
    dimension: str | None = None,
    value: str | None = None,
) -> SemanticCandidate:
    return SemanticCandidate(
        candidate_id=cid,
        target_kind=target,
        canonical_name=canonical,
        dimension_name=dimension,
        value=value,
        cube_names=tuple(cubes),
        display_label=canonical,
        provenance=(CandidateSource.CANONICAL_NAME,),
        score=1.0,
        material=True,
        selection_aliases=(canonical,),
    )


def hypothesis(
    *,
    text: str,
    kind: SemanticMentionKind,
    cand: SemanticCandidate,
    resolved_surface_value: str | None = None,
) -> SemanticHypothesis:
    return SemanticHypothesis(
        source_mention=text,
        mention_kind=kind,
        status=ResolutionStatus.RESOLVED,
        candidates=(cand,),
        resolved_candidate_id=cand.candidate_id,
        resolved_surface_value=resolved_surface_value,
    )


def analytic_turn(
    *,
    metric="ciro",
    dimension: str | None = None,
    filter_text: str | None = None,
    time_text: str | None = None,
    ranking: RankingSurface | None = None,
    comparison: str | None = None,
) -> TurnInterpretation:
    return TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_NEW,
        analytical_request=AnalyticalRequest(
            metric_mentions=(
                SemanticMention(text=metric, kind=SemanticMentionKind.METRIC),
            ),
            dimension_mentions=(
                (SemanticMention(text=dimension, kind=SemanticMentionKind.DIMENSION),)
                if dimension
                else ()
            ),
            filter_mentions=(
                (SemanticMention(text=filter_text, kind=SemanticMentionKind.FILTER),)
                if filter_text
                else ()
            ),
            time_mentions=(
                (SemanticMention(text=time_text, kind=SemanticMentionKind.TIME),)
                if time_text
                else ()
            ),
            ranking=ranking,
            comparisons=(
                (ComparisonSurface(text=comparison),)
                if comparison
                else ()
            ),
        ),
    )


def hypotheses_for(
    *,
    metric_name="toplam_ciro",
    dimension_name: str | None = None,
    filter_dimension: str | None = None,
    filter_value: str | None = None,
    cubes=("parti",),
) -> tuple[SemanticHypothesis, ...]:
    out = [
        hypothesis(
            text="ciro",
            kind=SemanticMentionKind.METRIC,
            cand=candidate(
                cid="m1",
                target=SemanticTargetKind.METRIC,
                canonical=metric_name,
                cubes=cubes,
            ),
        )
    ]
    if dimension_name:
        out.append(
            hypothesis(
                text="müşteri" if dimension_name == "musteri" else dimension_name,
                kind=SemanticMentionKind.DIMENSION,
                cand=candidate(
                    cid="d1",
                    target=SemanticTargetKind.DIMENSION,
                    canonical=dimension_name,
                    cubes=cubes,
                ),
            )
        )
    if filter_dimension and filter_value:
        out.append(
            hypothesis(
                text=filter_value,
                kind=SemanticMentionKind.FILTER,
                cand=candidate(
                    cid="f1",
                    target=SemanticTargetKind.ENTITY_VALUE,
                    canonical=filter_dimension,
                    dimension=filter_dimension,
                    value=filter_value,
                    cubes=cubes,
                ),
            )
        )
    return tuple(out)


class FakeCompileService:
    def cube_sql(self, cube_query: dict) -> str:
        return "SQL " + json.dumps(cube_query, ensure_ascii=False, sort_keys=True)


def test_temporal_resolver_consumes_only_typed_span_and_preserves_fiscal_owner():
    this_month = resolve_period(
        (SemanticMention(text="bu ay", kind="time"),),
        time_dimension="tarih",
        today=date(2026, 9, 21),
    )
    this_year = resolve_period(
        (SemanticMention(text="bu yıl", kind="time"),),
        time_dimension="tarih",
        today=date(2026, 9, 21),
    )
    last_three = resolve_period(
        (SemanticMention(text="son üç ay", kind="time"),),
        time_dimension="tarih",
        today=date(2026, 9, 21),
    )

    assert this_month.start == "2026-09-01"
    assert this_month.end == "2026-09-21"
    assert this_year.start == mali_takvim.yil_basi(date(2026, 9, 21)).isoformat()
    assert this_year.end == "2026-09-21"
    assert last_three.n == 3
    assert last_three.end == "2026-09-21"

    sig = inspect.signature(resolve_period)
    assert "question" not in sig.parameters


def test_comparison_is_two_explicit_periods_not_one_wide_range():
    base = resolve_period(
        (SemanticMention(text="bu ay", kind="time"),),
        time_dimension="tarih",
        today=date(2026, 9, 21),
    )
    comparison = resolve_comparison(
        (ComparisonSurface(text="geçen ayla kıyasla"),),
        base_period=base,
        time_dimension="tarih",
        today=date(2026, 9, 21),
    )

    assert comparison is not None
    assert comparison.base_period.start == "2026-09-01"
    assert comparison.base_period.end == "2026-09-21"
    assert comparison.reference_period.start == "2026-08-01"
    assert comparison.reference_period.end == "2026-08-21"
    assert period_filters(comparison.base_period) != period_filters(comparison.reference_period)


def test_ir_ledger_ranking_direction_and_limit_survive_to_plan_and_verification():
    turn = analytic_turn(
        dimension="müşteri",
        time_text="son üç ay",
        ranking=RankingSurface(text="en çok 5", direction="desc", limit=5),
    )
    built = AnalyticsIRBuilder().build(
        turn=turn,
        hypotheses=hypotheses_for(dimension_name="musteri"),
        schema=fake_schema(),
        context_version=CTX.version,
        today=date(2026, 9, 21),
    )

    plans, ledger = CubePlanner().plan(
        ir=built.ir,
        ledger=built.ledger,
        service=FakeCompileService(),
    )
    query = plans[0].cube_query

    assert query["order"] == {"measure": "toplam_ciro", "direction": "desc"}
    assert query["limit"] == 5
    assert query["dimensions"] == ["musteri"]

    result = {
        "columns": ["musteri", "toplam_ciro"],
        "rows": [
            {"musteri": "A", "toplam_ciro": 50},
            {"musteri": "B", "toplam_ciro": 40},
        ],
        "row_count": 2,
        "column_types": ["VARCHAR", "DOUBLE"],
    }
    ledger, errors = ResultValidator().validate(
        ir=built.ir,
        ledger=ledger,
        plans=plans,
        results=(result,),
    )
    assert errors == ((),)
    assert ledger.all_must_verified
    for item in ledger.items:
        assert item.history == (
            RequirementState.DETECTED,
            RequirementState.RESOLVED,
            RequirementState.REPRESENTED_IN_IR,
            RequirementState.REPRESENTED_IN_PLAN,
            RequirementState.VERIFIED,
        )


def test_missing_ranking_direction_is_blocked_not_guessed():
    turn = analytic_turn(
        dimension="müşteri",
        ranking=RankingSurface(text="ilk 5", direction="unspecified", limit=5),
    )
    with pytest.raises(StandardAnalyticsError) as exc:
        AnalyticsIRBuilder().build(
            turn=turn,
            hypotheses=hypotheses_for(dimension_name="musteri"),
            schema=fake_schema(),
            context_version=CTX.version,
        )

    assert exc.value.failure.code == "ranking_incomplete"
    assert any(item.state == RequirementState.BLOCKED for item in exc.value.ledger.items)


def test_filter_is_canonical_eq_and_never_silently_dropped():
    turn = analytic_turn(filter_text="RAM-3")
    built = AnalyticsIRBuilder().build(
        turn=turn,
        hypotheses=hypotheses_for(
            filter_dimension="makine",
            filter_value="RAM-3",
        ),
        schema=fake_schema(),
        context_version=CTX.version,
    )
    plans, ledger = CubePlanner().plan(
        ir=built.ir,
        ledger=built.ledger,
        service=FakeCompileService(),
    )
    assert {"dimension": "makine", "operator": "eq", "value": "RAM-3"} in plans[0].cube_query["filters"]
    assert next(x for x in ledger.items if x.kind == RequirementKind.FILTER).state == RequirementState.REPRESENTED_IN_PLAN


def test_multiple_viable_cubes_fail_instead_of_first_candidate_selection():
    turn = analytic_turn()
    hyp = hypotheses_for(cubes=("parti", "parti_clone"))
    with pytest.raises(StandardAnalyticsError) as exc:
        AnalyticsIRBuilder().build(
            turn=turn,
            hypotheses=hyp,
            schema=fake_schema(duplicate_parti=True),
            context_version=CTX.version,
        )
    assert exc.value.failure.code == "ambiguous_cube"


def test_multiple_time_axes_fail_instead_of_first_axis_selection():
    turn = analytic_turn(time_text="bu ay")
    with pytest.raises(StandardAnalyticsError) as exc:
        AnalyticsIRBuilder().build(
            turn=turn,
            hypotheses=hypotheses_for(),
            schema=fake_schema(time_axes=("created_at", "closed_at")),
            context_version=CTX.version,
        )
    assert exc.value.failure.code == "ambiguous_time_axis"


def test_simple_comparison_plans_two_immutable_executions():
    turn = analytic_turn(time_text="bu ay", comparison="geçen ayla kıyasla")
    built = AnalyticsIRBuilder().build(
        turn=turn,
        hypotheses=hypotheses_for(),
        schema=fake_schema(),
        context_version=CTX.version,
        today=date(2026, 9, 21),
    )
    plans, ledger = CubePlanner().plan(
        ir=built.ir,
        ledger=built.ledger,
        service=FakeCompileService(),
    )

    assert [plan.role for plan in plans] == ["primary", "comparison_reference"]
    assert plans[0].execution_id != plans[1].execution_id
    assert period_filters(built.ir.comparison.base_period) == [
        f for f in plans[0].cube_query["filters"] if f["dimension"] == "tarih"
    ]
    assert period_filters(built.ir.comparison.reference_period) == [
        f for f in plans[1].cube_query["filters"] if f["dimension"] == "tarih"
    ]
    assert next(x for x in ledger.items if x.kind == RequirementKind.COMPARISON).state == RequirementState.REPRESENTED_IN_PLAN


def test_strict_contract_seal_reports_db_spool_or_none(monkeypatch):
    import app.contracts as contracts

    store = ContractStore()
    base_kwargs = dict(
        session_id="s1",
        question="bu ay ciro",
        cube_query={"cube": "parti", "measures": ["toplam_ciro"]},
        sql="SELECT 1",
        result={"columns": ["toplam_ciro"], "rows": [{"toplam_ciro": 1}], "row_count": 1},
        schema_version="mdl",
        tenant_id="t1",
        provenance={"v2_minimum_query_contract": {"execution_id": "x1"}},
    )

    monkeypatch.setattr(contracts, "_persist", lambda row: None)
    db = store.record_v2_minimum(**base_kwargs)
    assert db["sealed"] is True and db["durability"] == "db"

    def fail_db(row):
        raise RuntimeError("db down")

    monkeypatch.setattr(contracts, "_persist", fail_db)
    monkeypatch.setattr(contracts, "_spool_append", lambda payload: None)
    spool = store.record_v2_minimum(**base_kwargs)
    assert spool["sealed"] is True and spool["durability"] == "spool_pending"

    def fail_spool(payload):
        raise RuntimeError("disk down")

    monkeypatch.setattr(contracts, "_spool_append", fail_spool)
    none = store.record_v2_minimum(**base_kwargs)
    assert none["sealed"] is False and none["durability"] == "none"


def test_day3_modules_do_not_import_legacy_semantic_owners_or_accept_raw_question():
    import app.v2.cube_planner as planner_module
    import app.v2.temporal as temporal_module

    source = (inspect.getsource(planner_module) + inspect.getsource(temporal_module)).casefold()
    for token in (
        "app.routers.ask",
        "cube_router",
        "uyum",
        "plan_tuketici",
        "plan_semasi",
        "followup",
        "intent_semasi",
        "generate_sql(",
        "select_cube(",
    ):
        assert token not in source

    assert "question" not in inspect.signature(AnalyticsIRBuilder.build).parameters
    assert "question" not in inspect.signature(CubePlanner.plan).parameters


class FakeDay3Service:
    mdl_version = "mdl-day3"

    def __init__(self):
        self.principals = []
        self.queries = []

    def schema(self):
        return fake_schema()

    def cube_sql(self, cube_query):
        self.queries.append(cube_query)
        return "SELECT musteri, toplam_ciro FROM safe_cube"

    def dry_plan(self, sql, *, principal=None):
        self.principals.append(("dry", principal))
        return sql

    def query(self, sql, limit=None, *, principal=None):
        self.principals.append(("query", principal))
        return {
            "columns": ["toplam_ciro"],
            "rows": [{"toplam_ciro": 123.0}],
            "row_count": 1,
            "column_types": ["DOUBLE"],
        }


class FakeDay3LLM:
    def structured_text(self, system, user):
        return json.dumps(
            {
                "dialogue_act": "ANALYTIC_NEW",
                "analytical_request": {
                    "metric_mentions": [{"text": "ciro", "kind": "metric"}]
                },
            },
            ensure_ascii=False,
        )


class FakeContracts:
    def record_v2_minimum(self, **kwargs):
        return {
            "id": "c-day3",
            "result_hash": result_hash(kwargs["result"]),
            "durability": "db",
            "sealed": True,
        }


def test_orchestrator_passes_explicit_principal_and_only_marks_sealed_result_official(monkeypatch):
    import app.v2.orchestrator as module

    service = FakeDay3Service()
    monkeypatch.setattr(module, "wren_for_request", lambda request: service)

    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                llm=FakeDay3LLM(),
                contracts=FakeContracts(),
            )
        )
    )
    principal = Principal(
        user_id="u1",
        tenant_id="t1",
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    response = V2Orchestrator().handle(
        request,
        AskV2Request(question="ciro", session_id="s1", thread_id="th1"),
        principal,
    )

    assert response.official_verified is True
    assert response.analytics_status == "verified"
    assert len(response.query_contracts) == 1
    assert response.query_contracts[0].sealed is True
    assert service.principals == [("dry", principal), ("query", principal)]


def test_contract_failure_keeps_result_non_official(monkeypatch):
    import app.v2.orchestrator as module

    service = FakeDay3Service()
    monkeypatch.setattr(module, "wren_for_request", lambda request: service)

    class BrokenContracts:
        def record_v2_minimum(self, **kwargs):
            return {
                "id": "c-unsealed",
                "result_hash": result_hash(kwargs["result"]),
                "durability": "none",
                "sealed": False,
            }

    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                llm=FakeDay3LLM(),
                contracts=BrokenContracts(),
            )
        )
    )
    principal = Principal(
        user_id="u1",
        tenant_id="t1",
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    response = V2Orchestrator().handle(
        request,
        AskV2Request(question="ciro"),
        principal,
    )

    assert response.official_verified is False
    assert response.analytics_status == "failed"
    assert response.failure.code == "contract_seal_failed"


def _real_hypotheses(
    *,
    metric_surface: str,
    metric_name: str,
    cube: str,
    dimension_surface: str | None = None,
    dimension_name: str | None = None,
):
    out = [
        hypothesis(
            text=metric_surface,
            kind=SemanticMentionKind.METRIC,
            cand=candidate(
                cid=f"real-m-{metric_name}",
                target=SemanticTargetKind.METRIC,
                canonical=metric_name,
                cubes=(cube,),
            ),
        )
    ]
    if dimension_surface and dimension_name:
        out.append(
            hypothesis(
                text=dimension_surface,
                kind=SemanticMentionKind.DIMENSION,
                cand=candidate(
                    cid=f"real-d-{dimension_name}",
                    target=SemanticTargetKind.DIMENSION,
                    canonical=dimension_name,
                    cubes=(cube,),
                ),
            )
        )
    return tuple(out)


@pytest.mark.parametrize(
    "case",
    [
        {
            "metric_surface": "ciro",
            "metric": "toplam_ciro",
            "cube": "parti",
            "time_text": "bu yıl",
        },
        {
            "metric_surface": "ciro",
            "metric": "toplam_ciro",
            "cube": "parti",
            "dimension_surface": "müşteri",
            "dimension": "musteri",
        },
        {
            "metric_surface": "oee",
            "metric": "ort_oee",
            "cube": "oee",
            "dimension_surface": "makine",
            "dimension": "makine",
        },
        {
            "metric_surface": "fire",
            "metric": "toplam_fire_kg",
            "cube": "parti",
            "dimension_surface": "aşama",
            "dimension": "asama",
        },
        {
            "metric_surface": "ciro",
            "metric": "toplam_ciro",
            "cube": "parti",
            "dimension_surface": "müşteri",
            "dimension": "musteri",
            "ranking": RankingSurface(text="en çok 5", direction="desc", limit=5),
        },
    ],
)
def test_real_demo_core_result_equivalence_focused(case, wren, schema, _test_kimligi):
    turn = analytic_turn(
        metric=case["metric_surface"],
        dimension=case.get("dimension_surface"),
        time_text=case.get("time_text"),
        ranking=case.get("ranking"),
    )
    built = AnalyticsIRBuilder().build(
        turn=turn,
        hypotheses=_real_hypotheses(
            metric_surface=case["metric_surface"],
            metric_name=case["metric"],
            cube=case["cube"],
            dimension_surface=case.get("dimension_surface"),
            dimension_name=case.get("dimension"),
        ),
        schema=schema,
        context_version=str(wren.mdl_version),
    )
    plans, _ = CubePlanner().plan(
        ir=built.ir,
        ledger=built.ledger,
        service=wren,
    )
    planned = plans[0].cube_query

    expected = {
        "cube": case["cube"],
        "measures": [case["metric"]],
        "dimensions": [case["dimension"]] if case.get("dimension") else [],
        "filters": period_filters(built.ir.period),
    }
    if case.get("ranking"):
        expected["order"] = {
            "measure": case["metric"],
            "direction": case["ranking"].direction,
        }
        expected["limit"] = case["ranking"].limit

    planned_sql = wren.cube_sql(planned)
    wren.dry_plan(planned_sql, principal=_test_kimligi)
    started = time.perf_counter()
    planned_result = wren.query(planned_sql, principal=_test_kimligi)
    REAL_DEMO_LATENCIES.append(time.perf_counter() - started)

    expected_sql = wren.cube_sql(expected)
    wren.dry_plan(expected_sql, principal=_test_kimligi)
    expected_result = wren.query(expected_sql, principal=_test_kimligi)
    assert result_hash(planned_result) == result_hash(expected_result)


def test_real_demo_simple_compare_executes_distinct_a_vs_b_periods(wren, schema, _test_kimligi):
    turn = analytic_turn(time_text="bu ay", comparison="geçen ayla kıyasla")
    built = AnalyticsIRBuilder().build(
        turn=turn,
        hypotheses=_real_hypotheses(
            metric_surface="ciro",
            metric_name="toplam_ciro",
            cube="parti",
        ),
        schema=schema,
        context_version=str(wren.mdl_version),
    )
    plans, ledger = CubePlanner().plan(
        ir=built.ir,
        ledger=built.ledger,
        service=wren,
    )
    assert len(plans) == 2
    assert plans[0].cube_query["filters"] != plans[1].cube_query["filters"]

    results = []
    for plan in plans:
        wren.dry_plan(plan.sql, principal=_test_kimligi)
        started = time.perf_counter()
        results.append(wren.query(plan.sql, principal=_test_kimligi))
        REAL_DEMO_LATENCIES.append(time.perf_counter() - started)

    ledger, errors = ResultValidator().validate(
        ir=built.ir,
        ledger=ledger,
        plans=plans,
        results=tuple(results),
    )
    assert errors == ((), ())
    assert ledger.all_must_verified


def test_zzz_real_demo_initial_standard_p95_is_under_10_seconds():
    assert len(REAL_DEMO_LATENCIES) >= 7
    samples = sorted(REAL_DEMO_LATENCIES)
    # Small focused demo set: nearest-rank p95 is effectively the max at n=7.
    p95 = samples[-1]
    assert p95 < 10.0
