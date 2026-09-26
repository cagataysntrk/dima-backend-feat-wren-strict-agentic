from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.v2.models import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.decision_intelligence import (
    ConstraintSource,
    DecisionAssumption,
    DecisionBriefCurrentness,
    DecisionBriefDraft,
    DecisionBriefStore,
    DecisionConstraint,
    DecisionLimitation,
    DecisionObjective,
    DecisionOption,
    DecisionPremiseRef,
    DecisionRecommendation,
    DecisionTradeoff,
    P21DecisionError,
    TradeoffSource,
    stable_decision_id,
)
from app.v3.report_document import (
    CoverageEntry,
    CoverageStatus,
    ReportDocumentStore,
    ReportStatement,
    ReportStatementKind,
)
from app.v3.research import ObligationState, ResearchManager
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.models import (
    BusinessRelationshipPolicyUseRecord,
    DecisionBriefRecord,
    DecisionRecord,
    HypothesisGroundingLink,
    HypothesisRecord,
    ReportDocumentRecord,
    ResearchClaimRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
    ResearchReasoningStepRecord,
    ResearchSessionRecord,
    RootCauseAssessment,
    Tenant,
    User,
)

TENANT = UUID("00000000-0000-4000-8000-000000002101")
USER = UUID("00000000-0000-4000-8000-000000002102")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000002103")
OTHER_USER = UUID("00000000-0000-4000-8000-000000002104")
STAMP = datetime(2026, 9, 26, 2, 0, tzinfo=timezone.utc)


def h(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def db_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal(
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p21",
) -> Principal:
    return Principal(
        user_id=str(user),
        tenant_id=str(tenant),
        tenant_slug=slug,
        roles=["analyst"],
    )


def ensure_identity_rows(
    db,
    *,
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p21",
):
    with Session(db) as s:
        if s.get(Tenant, tenant) is None:
            s.add(
                Tenant(
                    id=tenant,
                    slug=slug,
                    name=slug.upper(),
                    created_at=STAMP,
                )
            )
        if s.get(User, user) is None:
            s.add(
                User(
                    id=user,
                    tenant_id=tenant,
                    email=f"{user}@example.test",
                    password_hash="unused",
                    created_at=STAMP,
                )
            )
        s.commit()


def research_brief(
    suffix: str,
    *,
    context: str = "ctx-p21-v1",
) -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="orders",
        candidate_id="native.sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    question = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.PERFORMANCE,
        source_text="Provide governed decision context.",
        subject_refs=(metric,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id=f"rb-p21-{suffix}",
        objective=question.source_text,
        scope=ResearchScope(semantic_refs=(metric,)),
        questions=(question,),
        must_requirement_ids=("g1",),
        context_version=context,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def sealed_research(
    db,
    *,
    suffix: str,
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p21",
    context: str = "ctx-p21-v1",
):
    ensure_identity_rows(
        db,
        tenant=tenant,
        user=user,
        slug=slug,
    )
    p = principal(tenant, user, slug)
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=research_brief(suffix, context=context),
        request_ref=f"p21-{suffix}",
        source_message_hash=hashlib.sha256(
            f"p21-{suffix}".encode()
        ).hexdigest(),
        principal=p,
    )
    item = ResearchManager.obligation(
        session,
        "g1",
    ).model_copy(
        update={"state": ObligationState.VERIFIED},
    )
    session = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, item),
        now=STAMP + timedelta(minutes=1),
    )
    session = store.save(
        session,
        expected_revision=session.revision - 1,
    )
    return p, store, session


def p20_statement_id(suffix: str, kind: str) -> str:
    return "p20s_" + h({"suffix": suffix, "kind": kind})[:24]


def create_sealed_p20_report(
    db,
    *,
    suffix: str = "base",
    value: int = 34,
    stale: bool = False,
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p21",
):
    SQLModel.metadata.create_all(db)
    p, research_store, session = sealed_research(
        db,
        suffix=suffix,
        tenant=tenant,
        user=user,
        slug=slug,
    )
    numeric = ReportStatement(
        statement_id=p20_statement_id(suffix, "numeric"),
        statement_kind=ReportStatementKind.NUMERIC,
        source_refs=(),
        obligation_refs=("g1",),
        limitation_refs=(),
        upstream_epistemic_ceiling="EXACT_GOVERNED_NUMERIC",
        payload={"value": value, "unit": "orders"},
        text=f"Numeric result: {value} orders",
    )
    fact = ReportStatement(
        statement_id=p20_statement_id(suffix, "fact"),
        statement_kind=ReportStatementKind.ANALYTICAL_FACT,
        source_refs=(),
        obligation_refs=("g1",),
        limitation_refs=(),
        upstream_epistemic_ceiling="SUPPORTED",
        payload={"claim_id": "sealed-p20-fixture", "epistemic_state": "SUPPORTED"},
        text="Observed channel performance differs in the governed report scope.",
    )
    uncertainty = ReportStatement(
        statement_id=p20_statement_id(suffix, "uncertainty"),
        statement_kind=ReportStatementKind.UNCERTAINTY,
        source_refs=(),
        obligation_refs=("g1",),
        limitation_refs=(),
        upstream_epistemic_ceiling="NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED",
        payload={},
        text="No defensible root cause established.",
    )
    statements = (numeric, fact, uncertainty)
    coverage = (
        CoverageEntry(
            obligation_id="g1",
            coverage_status=CoverageStatus.REPRESENTED,
            statement_ids=tuple(item.statement_id for item in statements),
        ),
    )
    source_identity = {
        "research_authority_id": session.authority_id,
        "research_session_id": session.session_id,
        "semantic_context_version": session.context_version,
        "mandatory_obligation_ids": ["g1"],
        "sources": [],
    }
    source_set_fingerprint = h(source_identity)
    if stale:
        source_set_fingerprint = h(
            {"stale": source_set_fingerprint}
        )
    report_fingerprint = h(
        {
            "session": session.session_id,
            "suffix": suffix,
            "value": value,
            "coverage": [
                item.model_dump(mode="json")
                for item in coverage
            ],
            "statements": [
                item.model_dump(mode="json")
                for item in statements
            ],
        }
    )
    report_id = "p20r_" + report_fingerprint[:24]
    with Session(db) as s:
        s.add(
            ReportDocumentRecord(
                report_id=report_id,
                research_session_id=session.session_id,
                tenant_binding=session.tenant_binding,
                semantic_context_version=session.context_version,
                report_key=f"p21-source-{suffix}",
                revision=1,
                parent_report_id=None,
                coverage_json=json.dumps(
                    [
                        item.model_dump(mode="json")
                        for item in coverage
                    ],
                    sort_keys=True,
                ),
                statements_json=json.dumps(
                    [
                        item.model_dump(mode="json")
                        for item in statements
                    ],
                    sort_keys=True,
                ),
                source_refs_json="[]",
                limitations_json="[]",
                source_set_fingerprint=source_set_fingerprint,
                report_fingerprint=report_fingerprint,
                created_at=STAMP + timedelta(minutes=2),
            )
        )
        s.commit()
    report_store = ReportDocumentStore(
        research_store=research_store,
        db_engine=db,
    )
    return {
        "principal": p,
        "research_store": research_store,
        "session": session,
        "report_store": report_store,
        "report_id": report_id,
        "report_fingerprint": report_fingerprint,
        "numeric": numeric,
        "fact": fact,
        "uncertainty": uncertainty,
    }


def premise_for(statement: ReportStatement) -> DecisionPremiseRef:
    numeric_value = None
    numeric_unit = None
    if statement.statement_kind == ReportStatementKind.NUMERIC:
        numeric_value = statement.payload["value"]
        numeric_unit = statement.payload.get("unit")
    return DecisionPremiseRef(
        premise_id=stable_decision_id(
            "p21p_",
            {"statement": statement.statement_id},
        ),
        statement_id=statement.statement_id,
        statement_kind=statement.statement_kind,
        upstream_epistemic_ceiling=statement.upstream_epistemic_ceiling,
        numeric_value=numeric_value,
        numeric_unit=numeric_unit,
    )


def make_draft(
    state,
    *,
    brief_key: str = "channel-decision",
    recommendation_rationale: str | None = None,
):
    p_num = premise_for(state["numeric"])
    p_fact = premise_for(state["fact"])
    p_unc = premise_for(state["uncertainty"])

    objective = DecisionObjective(
        objective_id=stable_decision_id(
            "p21o_",
            {"objective": "Choose a reversible next step"},
        ),
        objective_text="Choose a reversible next step.",
    )
    user_constraint = DecisionConstraint(
        constraint_id=stable_decision_id(
            "p21c_",
            {"constraint": "risk"},
        ),
        source_kind=ConstraintSource.USER_DECLARED,
        text="Avoid irreversible operational changes.",
        premise_refs=(),
    )
    governed_constraint = DecisionConstraint(
        constraint_id=stable_decision_id(
            "p21c_",
            {"constraint": "numeric"},
        ),
        source_kind=ConstraintSource.P20_PREMISE,
        text=f"Governed constraint premises: {p_num.premise_id}",
        premise_refs=(p_num.premise_id,),
    )
    option_a = DecisionOption(
        option_id=stable_decision_id(
            "p21x_",
            {"option": "experiment"},
        ),
        proposal_text="Run a bounded reversible experiment.",
    )
    option_b = DecisionOption(
        option_id=stable_decision_id(
            "p21x_",
            {"option": "evidence"},
        ),
        proposal_text="Collect additional governed evidence first.",
    )
    assumption = DecisionAssumption(
        assumption_id=stable_decision_id(
            "p21a_",
            {"assumption": "reversible"},
        ),
        assumption_text="The experiment can be reversed operationally.",
    )
    limitation = DecisionLimitation(
        limitation_id=stable_decision_id(
            "p21l_",
            {"limitation": "no-root"},
        ),
        detail="The governed report establishes no defensible root cause.",
        premise_refs=(p_unc.premise_id,),
    )
    governed_tradeoff = DecisionTradeoff(
        tradeoff_id=stable_decision_id(
            "p21t_",
            {"tradeoff": "numeric"},
        ),
        option_id=option_a.option_id,
        source_kind=TradeoffSource.P20_PREMISE,
        text=f"Governed tradeoff premises: {p_num.premise_id}",
        premise_refs=(p_num.premise_id,),
        assumption_refs=(),
        limitation_refs=(limitation.limitation_id,),
    )
    judgment_tradeoff = DecisionTradeoff(
        tradeoff_id=stable_decision_id(
            "p21t_",
            {"tradeoff": "judgment"},
        ),
        option_id=option_b.option_id,
        source_kind=TradeoffSource.USER_JUDGMENT,
        text="Waiting may reduce immediate operational learning.",
        premise_refs=(),
        assumption_refs=(assumption.assumption_id,),
        limitation_refs=(),
    )
    recommendation = DecisionRecommendation(
        recommended_option_ids=(option_a.option_id,),
        premise_refs=(p_fact.premise_id, p_unc.premise_id),
        assumption_refs=(assumption.assumption_id,),
        limitation_refs=(limitation.limitation_id,),
        rationale=recommendation_rationale,
    )
    return DecisionBriefDraft(
        report_id=state["report_id"],
        brief_key=brief_key,
        objective=objective,
        constraints=(user_constraint, governed_constraint),
        premises=(p_num, p_fact, p_unc),
        options=(option_a, option_b),
        tradeoffs=(governed_tradeoff, judgment_tradeoff),
        assumptions=(assumption,),
        limitations=(limitation,),
        recommendation=recommendation,
        model_provenance=None,
    )


def p21_store(db, state) -> DecisionBriefStore:
    return DecisionBriefStore(
        report_store=state["report_store"],
        db_engine=db,
    )


def test_current_p20_report_seals_one_advisory_decision_brief():
    db = db_engine()
    state = create_sealed_p20_report(db)
    store = p21_store(db, state)
    brief = store.seal(
        draft=make_draft(state),
        principal=state["principal"],
        now=STAMP + timedelta(minutes=3),
    )
    assert brief.revision == 1
    assert brief.parent_decision_brief_id is None
    assert brief.recommendation.recommendation_kind == "ADVISORY_CONSIDERATION"
    assert brief.model_provenance is None
    assert store.currentness(
        decision_brief_id=brief.decision_brief_id,
        principal=state["principal"],
    ) == DecisionBriefCurrentness.CURRENT
    with Session(db) as s:
        assert len(s.exec(select(DecisionBriefRecord)).all()) == 1


def test_stale_p20_report_rejects_new_decision_brief():
    db = db_engine()
    state = create_sealed_p20_report(db, stale=True)
    with pytest.raises(P21DecisionError) as exc:
        p21_store(db, state).seal(
            draft=make_draft(state),
            principal=state["principal"],
        )
    assert exc.value.code == "P21_SOURCE_REPORT_STALE"


def test_foreign_tenant_and_unknown_report_share_non_oracle_error():
    db = db_engine()
    state = create_sealed_p20_report(db)
    other = principal(OTHER_TENANT, OTHER_USER, "other")
    with pytest.raises(P21DecisionError) as foreign:
        p21_store(db, state).seal(
            draft=make_draft(state),
            principal=other,
        )
    fake = make_draft(state).model_copy(
        update={"report_id": "p20r_" + "f" * 24},
    )
    with pytest.raises(P21DecisionError) as missing:
        p21_store(db, state).seal(
            draft=fake,
            principal=state["principal"],
        )
    assert foreign.value.code == "P21_SOURCE_REPORT_UNAVAILABLE"
    assert missing.value.code == foreign.value.code


def test_unknown_p20_statement_premise_rejects():
    db = db_engine()
    state = create_sealed_p20_report(db)
    draft = make_draft(state)
    bad = draft.premises[1].model_copy(
        update={"statement_id": "p20s_" + "f" * 24},
    )
    broken = draft.model_copy(
        update={
            "premises": (
                draft.premises[0],
                bad,
                draft.premises[2],
            )
        }
    )
    with pytest.raises(P21DecisionError) as exc:
        p21_store(db, state).seal(
            draft=broken,
            principal=state["principal"],
        )
    assert exc.value.code == "P21_PREMISE_NOT_IN_REPORT"


def test_exact_p20_numeric_value_and_unit_are_preserved():
    db = db_engine()
    state = create_sealed_p20_report(db, value=34)
    brief = p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    numeric = next(
        item
        for item in brief.premises
        if item.statement_kind == ReportStatementKind.NUMERIC
    )
    assert numeric.numeric_value == 34
    assert numeric.numeric_unit == "orders"


def test_new_numeric_calculation_rejects():
    db = db_engine()
    state = create_sealed_p20_report(db, value=34)
    draft = make_draft(state)
    changed = draft.premises[0].model_copy(
        update={"numeric_value": 68},
    )
    broken = draft.model_copy(
        update={
            "premises": (
                changed,
                draft.premises[1],
                draft.premises[2],
            )
        }
    )
    with pytest.raises(P21DecisionError) as exc:
        p21_store(db, state).seal(
            draft=broken,
            principal=state["principal"],
        )
    assert exc.value.code == "P21_NUMERIC_PREMISE_MISMATCH"


def test_numeric_unit_transformation_rejects():
    db = db_engine()
    state = create_sealed_p20_report(db)
    draft = make_draft(state)
    changed = draft.premises[0].model_copy(
        update={"numeric_unit": "thousands-of-orders"},
    )
    broken = draft.model_copy(
        update={
            "premises": (
                changed,
                draft.premises[1],
                draft.premises[2],
            )
        }
    )
    with pytest.raises(P21DecisionError) as exc:
        p21_store(db, state).seal(
            draft=broken,
            principal=state["principal"],
        )
    assert exc.value.code == "P21_NUMERIC_UNIT_MISMATCH"


def test_epistemic_ceiling_cannot_be_upgraded():
    db = db_engine()
    state = create_sealed_p20_report(db)
    draft = make_draft(state)
    changed = draft.premises[2].model_copy(
        update={"upstream_epistemic_ceiling": "ROOT_CAUSE_ESTABLISHED"},
    )
    broken = draft.model_copy(
        update={
            "premises": (
                draft.premises[0],
                draft.premises[1],
                changed,
            )
        }
    )
    with pytest.raises(P21DecisionError) as exc:
        p21_store(db, state).seal(
            draft=broken,
            principal=state["principal"],
        )
    assert exc.value.code == "P21_EPISTEMIC_CEILING_MISMATCH"


def test_no_defensible_root_cause_stays_advisory():
    db = db_engine()
    state = create_sealed_p20_report(db)
    brief = p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    unc = next(
        item
        for item in brief.premises
        if item.statement_kind == ReportStatementKind.UNCERTAINTY
    )
    assert (
        unc.upstream_epistemic_ceiling
        == "NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED"
    )
    assert brief.recommendation.recommendation_kind == "ADVISORY_CONSIDERATION"
    assert "root cause" not in brief.recommendation.rationale.lower()


def test_root_cause_fix_recommendation_kind_is_not_representable():
    with pytest.raises(ValidationError):
        DecisionRecommendation.model_validate(
            {
                "recommendation_kind": "ROOT_CAUSE_FIX",
                "recommended_option_ids": ["p21x_" + "a" * 24],
                "premise_refs": ["p21p_" + "b" * 24],
            }
        )


def test_multiple_options_remain_legal_without_ranking():
    db = db_engine()
    state = create_sealed_p20_report(db)
    brief = p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    assert len(brief.options) == 2
    assert {item.option_id for item in brief.options} == {
        stable_decision_id("p21x_", {"option": "experiment"}),
        stable_decision_id("p21x_", {"option": "evidence"}),
    }
    assert not hasattr(brief.options[0], "score")
    assert not hasattr(brief.options[0], "rank")
    assert not hasattr(brief.options[0], "expected_impact")


def test_arbitrary_factual_recommendation_rationale_rejects():
    db = db_engine()
    state = create_sealed_p20_report(db)
    draft = make_draft(
        state,
        recommendation_rationale="This option will increase revenue by 12%.",
    )
    with pytest.raises(P21DecisionError) as exc:
        p21_store(db, state).seal(
            draft=draft,
            principal=state["principal"],
        )
    assert exc.value.code == "P21_RECOMMENDATION_RATIONALE_NOT_CANONICAL"


def test_assumptions_remain_explicit_user_assumptions():
    db = db_engine()
    state = create_sealed_p20_report(db)
    brief = p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    assert len(brief.assumptions) == 1
    assert brief.assumptions[0].source_kind == "USER_ASSUMPTION"
    assert (
        brief.assumptions[0].assumption_id
        in brief.recommendation.assumption_refs
    )


def test_limitations_survive_seal():
    db = db_engine()
    state = create_sealed_p20_report(db)
    brief = p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    assert len(brief.limitations) == 1
    assert (
        "no defensible root cause"
        in brief.limitations[0].detail.lower()
    )
    assert (
        brief.limitations[0].limitation_id
        in brief.recommendation.limitation_refs
    )


def test_user_constraint_remains_user_intent():
    db = db_engine()
    state = create_sealed_p20_report(db)
    brief = p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    item = next(
        value
        for value in brief.constraints
        if value.source_kind == ConstraintSource.USER_DECLARED
    )
    assert item.premise_refs == ()
    assert "irreversible" in item.text.lower()


def test_p20_constraint_text_cannot_strengthen_its_premise():
    db = db_engine()
    state = create_sealed_p20_report(db)
    draft = make_draft(state)
    governed = draft.constraints[1].model_copy(
        update={"text": "Revenue must increase by 12%."},
    )
    broken = draft.model_copy(
        update={"constraints": (draft.constraints[0], governed)}
    )
    with pytest.raises(P21DecisionError) as exc:
        p21_store(db, state).seal(
            draft=broken,
            principal=state["principal"],
        )
    assert exc.value.code == "P21_CONSTRAINT_TEXT_NOT_CANONICAL"


def test_restart_idempotency_reproduces_exact_identity():
    db = db_engine()
    state = create_sealed_p20_report(db)
    draft = make_draft(state)
    first = p21_store(db, state).seal(
        draft=draft,
        principal=state["principal"],
    )
    restarted = DecisionBriefStore(
        report_store=ReportDocumentStore(
            research_store=ResearchSessionStore(db),
            db_engine=db,
        ),
        db_engine=db,
    )
    same = restarted.seal(
        draft=draft,
        principal=state["principal"],
    )
    assert same.decision_brief_id == first.decision_brief_id
    assert same.brief_fingerprint == first.brief_fingerprint
    assert same.revision == 1


def test_new_governed_p20_report_creates_revision_not_rewrite():
    db = db_engine()
    first_state = create_sealed_p20_report(
        db,
        suffix="r1",
        value=34,
    )
    first = p21_store(db, first_state).seal(
        draft=make_draft(first_state),
        principal=first_state["principal"],
    )
    second_state = create_sealed_p20_report(
        db,
        suffix="r2",
        value=35,
    )
    second = p21_store(db, second_state).seal(
        draft=make_draft(second_state),
        principal=second_state["principal"],
    )
    assert second.decision_brief_id != first.decision_brief_id
    assert second.revision == 2
    assert second.parent_decision_brief_id == first.decision_brief_id
    loaded_first = p21_store(db, first_state).load(
        decision_brief_id=first.decision_brief_id,
        principal=first_state["principal"],
    )
    assert loaded_first.model_dump(mode="json") == first.model_dump(mode="json")


def test_old_decision_brief_becomes_superseded_without_mutation():
    db = db_engine()
    first_state = create_sealed_p20_report(
        db,
        suffix="s1",
        value=34,
    )
    store1 = p21_store(db, first_state)
    first = store1.seal(
        draft=make_draft(first_state),
        principal=first_state["principal"],
    )
    before = first.model_dump(mode="json")
    second_state = create_sealed_p20_report(
        db,
        suffix="s2",
        value=36,
    )
    p21_store(db, second_state).seal(
        draft=make_draft(second_state),
        principal=second_state["principal"],
    )
    assert store1.currentness(
        decision_brief_id=first.decision_brief_id,
        principal=first_state["principal"],
    ) == DecisionBriefCurrentness.SUPERSEDED
    assert store1.load(
        decision_brief_id=first.decision_brief_id,
        principal=first_state["principal"],
    ).model_dump(mode="json") == before


def test_legacy_decision_record_is_unchanged_and_not_written():
    db = db_engine()
    state = create_sealed_p20_report(db)
    expected_fields = {
        "id",
        "ts",
        "tenant_id",
        "user_id",
        "session_id",
        "question",
        "chosen_json",
        "options_json",
        "rationale",
        "note",
        "contract_ids_json",
        "content_hash",
        "supersedes",
        "sablon_json",
    }
    assert set(DecisionRecord.model_fields) == expected_fields
    with Session(db) as s:
        legacy = DecisionRecord(
            id="d-legacy-p21",
            tenant_id=str(TENANT),
            user_id=str(USER),
            note="historical compatibility",
        )
        s.add(legacy)
        s.commit()
        before = s.get(DecisionRecord, legacy.id).model_dump()
    p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    with Session(db) as s:
        after = s.get(DecisionRecord, "d-legacy-p21").model_dump()
        assert after == before
        assert len(s.exec(select(DecisionRecord)).all()) == 1


def test_p14_through_p20_authority_rows_are_unchanged_by_p21_seal():
    db = db_engine()
    state = create_sealed_p20_report(db)
    models = (
        ResearchSessionRecord,
        ResearchExecutionLink,
        ResearchExplorationMaterial,
        ResearchClaimRecord,
        ResearchReasoningStepRecord,
        BusinessRelationshipPolicyUseRecord,
        HypothesisRecord,
        HypothesisGroundingLink,
        RootCauseAssessment,
        ReportDocumentRecord,
    )
    with Session(db) as s:
        before = {
            model.__name__: [
                row.model_dump()
                for row in s.exec(select(model)).all()
            ]
            for model in models
        }
    p21_store(db, state).seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    with Session(db) as s:
        after = {
            model.__name__: [
                row.model_dump()
                for row in s.exec(select(model)).all()
            ]
            for model in models
        }
    assert after == before


def test_p21_has_exactly_one_durable_record_type():
    tables = {
        table.name
        for table in SQLModel.metadata.tables.values()
        if table.name.startswith("p21_")
    }
    assert tables == {"p21_decision_brief"}


def test_model_provenance_is_not_allowed_in_first_vertical():
    db = db_engine()
    state = create_sealed_p20_report(db)
    raw = make_draft(state).model_dump(mode="json")
    raw["model_provenance"] = {"model": "anything"}
    with pytest.raises(ValidationError):
        DecisionBriefDraft.model_validate(raw)


def test_decision_brief_load_is_cross_tenant_non_oracle():
    db = db_engine()
    state = create_sealed_p20_report(db)
    store = p21_store(db, state)
    brief = store.seal(
        draft=make_draft(state),
        principal=state["principal"],
    )
    other = principal(OTHER_TENANT, OTHER_USER, "other")
    with pytest.raises(P21DecisionError) as foreign:
        store.load(
            decision_brief_id=brief.decision_brief_id,
            principal=other,
        )
    with pytest.raises(P21DecisionError) as missing:
        store.load(
            decision_brief_id="p21b_" + "f" * 24,
            principal=state["principal"],
        )
    assert foreign.value.code == "P21_DECISION_BRIEF_UNAVAILABLE"
    assert missing.value.code == foreign.value.code


def test_p21_production_owner_has_zero_analytics_or_lower_authority_bypass():
    path = Path("app/v3/decision_intelligence.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    imported_symbols = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
            imported_symbols.update(alias.name for alias in node.names)

    forbidden_imports = (
        "app.v3.substrate.metabase",
        "app.v3.research",
        "app.v3.research_store",
        "app.v3.research_manager",
        "app.v3.research_native_gateway",
        "app.v3.claim_lineage",
        "app.v3.hypothesis_root_cause",
        "app.v3.business_relationship_policy",
        "app.wren",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
    )
    assert not any(
        name.startswith(forbidden_imports)
        for name in imports
    )
    assert "DecisionRecord" not in imported_symbols
    assert "ReportDocumentRecord" not in imported_symbols

    forbidden_text = (
        "NativeEngineBridge",
        "MetabaseAgentClient",
        "DimaQueryReceipt(",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
        "RootCauseAssessment(",
        "DecisionRecord(",
        "cube_query",
        "sablon_json",
        "expected_impact",
        "probability",
        "optimization",
        "forecast",
    )
    for token in forbidden_text:
        assert token not in source
