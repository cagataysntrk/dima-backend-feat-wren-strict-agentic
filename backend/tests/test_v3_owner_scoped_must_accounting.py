from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductRequirementState,
)
from app.v3.report_document import (
    CoverageStatus,
    P20ReportError,
    ReportDocumentStore,
)
from app.v3.research import (
    EvidenceRef,
    ObligationState,
    ResearchManager,
    StoppingStatus,
)
from app.v3.research_contracts import (
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
)
from app.v3.research_product import (
    ResearchAskOrchestrator,
    ResearchBriefAuthoritySealer,
)
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal

TENANT = UUID("00000000-0000-4000-8000-000000007101")
USER = UUID("00000000-0000-4000-8000-000000007102")
STAMP = datetime(2026, 9, 26, 15, 0, tzinfo=timezone.utc)


def db_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal():
    return Principal(
        user_id=str(USER),
        tenant_id=str(TENANT),
        tenant_slug="must-accounting",
        roles=["analyst"],
    )


def brief(*, report: bool, count: int = 1) -> ResearchBrief:
    questions = tuple(
        ResearchQuestion(
            goal_id=f"g_{index}",
            kind=ResearchGoalKind.BREAKDOWN,
            source_text=f"Governed analytical question {index}.",
            status=ResearchGoalStatus.RESOLVED,
        )
        for index in range(1, count + 1)
    )
    deliverables = (
        (
            ResearchDeliverableRequirement(
                requirement_id="d_report",
                kind=PresentationKind.REPORT,
                source_text="Produce a governed report.",
            ),
        )
        if report
        else ()
    )
    return ResearchBrief(
        brief_id=f"rb-owner-scope-{count}-{'report' if report else 'plain'}",
        objective="Preserve owner-scoped USER_MUST accounting.",
        scope=ResearchScope(),
        questions=questions,
        deliverables=deliverables,
        must_requirement_ids=tuple(
            [item.goal_id for item in questions]
            + [item.requirement_id for item in deliverables]
        ),
        context_version="ctx-owner-scope-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def start(db, item: ResearchBrief):
    SQLModel.metadata.create_all(db)
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=item,
        request_ref=f"owner-scope:{item.brief_id}",
        source_message_hash=hashlib.sha256(item.brief_id.encode()).hexdigest(),
        principal=principal(),
    )
    return store, session


def _hash(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def verify(db, store: ResearchSessionStore, session, obligation_id: str, value: int):
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id=obligation_id,
    )
    session = store.save(
        prepared.session,
        expected_revision=session.revision,
    )
    link = store.begin_delegation(
        session=session,
        obligation_id=obligation_id,
        dima_request_id=prepared.request.dima_request_id,
        dima_trace_id=prepared.request.dima_trace_id,
        native_conversation_id=prepared.request.conversation_id,
    )
    query = {
        "database": 1,
        "type": "query",
        "query": {"source-table": 10, "aggregation": [["sum", 20]]},
    }
    link = store.mark_candidate(
        link.id,
        native_query_id=f"owner-{obligation_id}",
        native_query=query,
        query_fingerprint=_hash(query),
    )
    store.mark_execution_started(link.id, native_subject_ref="metabase-user:2")
    result = {
        "database_id": 1,
        "data": {"rows": [[f"segment-{obligation_id}", value]]},
    }
    store.mark_executed(
        link.id,
        native_subject_ref="metabase-user:2",
        runtime_identity={
            "substrate": "metabase-native",
            "runtime_version": "v0.63.18-dima.6",
            "image_digest": "sha256:" + "d" * 64,
            "database_id": "metabase:1",
        },
        result_payload=result,
        result_hash=_hash(result),
        executed_at=STAMP,
    )
    evidence_id = "evi_" + hashlib.sha256(
        f"{obligation_id}:evidence".encode()
    ).hexdigest()[:24]
    receipt_id = "dqr_" + hashlib.sha256(
        f"{obligation_id}:receipt".encode()
    ).hexdigest()[:24]
    store.mark_verified(
        link.id,
        receipt_id=receipt_id,
        evidence_id=evidence_id,
    )
    current = ResearchManager.obligation(session, obligation_id)
    current = current.model_copy(
        update={
            "state": ObligationState.VERIFIED,
            "evidence_refs": (evidence_id,),
        }
    )
    session = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, current),
        evidence_refs=(
            *session.evidence_refs,
            EvidenceRef(
                evidence_id=evidence_id,
                receipt_id=receipt_id,
                authority_id=session.authority_id,
                obligation_id=obligation_id,
            ),
        ),
        now=STAMP + timedelta(minutes=value),
    )
    return store.save(session, expected_revision=session.revision - 1)


def limit(store: ResearchSessionStore, session, obligation_id: str):
    updated = ResearchManager.record_limitation(
        session,
        obligation_id=obligation_id,
        code="UPSTREAM_TRUTH_INSUFFICIENT",
        detail="Governed upstream truth is insufficient for this analytical requirement.",
        now=STAMP + timedelta(minutes=30),
    )
    return store.save(updated, expected_revision=session.revision)


def verified_without_evidence(store: ResearchSessionStore, session, obligation_id: str):
    current = ResearchManager.obligation(session, obligation_id)
    current = current.model_copy(update={"state": ObligationState.VERIFIED})
    updated = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, current),
        now=STAMP + timedelta(minutes=40),
    )
    return store.save(updated, expected_revision=session.revision)


def seal_report(db, store, session):
    reports = ReportDocumentStore(research_store=store, db_engine=db)
    draft = reports.draft_from_governed_research(
        research_session_id=session.session_id,
        report_key="owner-scoped-accounting",
        principal=principal(),
    )
    report = reports.seal(
        draft=draft,
        principal=principal(),
        now=STAMP + timedelta(hours=1),
    )
    return reports, draft, report


def test_a_question_only_p14_terminal_and_no_p20_required():
    db = db_engine()
    item = brief(report=False)
    store, session = start(db, item)
    session = verify(db, store, session, "g_1", 11)
    assert session.stopping.status == StoppingStatus.COMPLETE
    assert tuple(x.obligation_id for x in session.obligations) == ("g_1",)
    assert session.accepted_brief == item
    projection = HeadlessProductComposer._project_user_must(
        brief=item,
        session=session,
        report=None,
    )
    assert projection[1:] == (1, 1, 1)


def test_b_question_plus_report_p14_terminal_then_report_fulfills_deliverable():
    db = db_engine()
    item = brief(report=True)
    store, session = start(db, item)
    session = verify(db, store, session, "g_1", 12)
    assert session.stopping.status == StoppingStatus.COMPLETE
    assert tuple(x.obligation_id for x in session.obligations) == ("g_1",)
    assert session.accepted_brief.must_requirement_ids == ("g_1", "d_report")

    _, draft, report = seal_report(db, store, session)
    assert tuple(x.obligation_id for x in draft.coverage) == ("g_1",)
    projection, total, accounted, fulfilled = HeadlessProductComposer._project_user_must(
        brief=item,
        session=session,
        report=report,
    )
    by_id = {x.requirement_id: x for x in projection}
    assert by_id["g_1"].state == ProductRequirementState.VERIFIED
    assert by_id["d_report"].state == ProductRequirementState.FULFILLED
    assert by_id["d_report"].fulfilled_by_ref == report.report_id
    assert (total, accounted, fulfilled) == (2, 2, 2)


def test_c_nonterminal_question_plus_report_rejected_by_p20():
    db = db_engine()
    item = brief(report=True)
    store, session = start(db, item)
    reports = ReportDocumentStore(research_store=store, db_engine=db)
    with pytest.raises(P20ReportError) as exc:
        reports.draft_from_governed_research(
            research_session_id=session.session_id,
            report_key="not-terminal",
            principal=principal(),
        )
    assert exc.value.code == "P20_RESEARCH_SESSION_NOT_SEALED"


def test_d_limited_question_plus_report_p14_partial_and_report_fulfills_deliverable():
    db = db_engine()
    item = brief(report=True)
    store, session = start(db, item)
    session = limit(store, session, "g_1")
    assert session.stopping.status == StoppingStatus.PARTIAL
    _, draft, report = seal_report(db, store, session)
    assert draft.coverage[0].coverage_status == CoverageStatus.LIMITED
    assert draft.limitations[0].code == "UPSTREAM_TRUTH_INSUFFICIENT"
    projection, total, accounted, fulfilled = HeadlessProductComposer._project_user_must(
        brief=item,
        session=session,
        report=report,
    )
    by_id = {x.requirement_id: x for x in projection}
    assert by_id["g_1"].state == ProductRequirementState.LIMITED
    assert by_id["d_report"].state == ProductRequirementState.FULFILLED
    assert (total, accounted, fulfilled) == (2, 2, 1)


def test_e_multiple_analytical_musts_are_terminal_before_publication():
    db = db_engine()
    item = brief(report=True, count=2)
    store, session = start(db, item)
    session = verify(db, store, session, "g_1", 13)
    assert session.stopping.status == StoppingStatus.ACTIVE
    reports = ReportDocumentStore(research_store=store, db_engine=db)
    with pytest.raises(P20ReportError):
        reports.draft_from_governed_research(
            research_session_id=session.session_id,
            report_key="half-done",
            principal=principal(),
        )
    session = verify(db, store, session, "g_2", 14)
    assert session.stopping.status == StoppingStatus.COMPLETE
    _, draft, _ = seal_report(db, store, session)
    assert {x.obligation_id for x in draft.coverage} == {"g_1", "g_2"}


def test_f_report_missing_governed_publishable_truth_is_explicit_limitation():
    db = db_engine()
    item = brief(report=True)
    store, session = start(db, item)
    session = verified_without_evidence(store, session, "g_1")
    _, draft, report = seal_report(db, store, session)
    assert report
    assert draft.statements == ()
    assert draft.coverage[0].coverage_status == CoverageStatus.LIMITED
    assert draft.limitations[0].code == "P20_NO_GOVERNED_PUBLISHABLE_FACT"


def test_g_restart_after_p14_before_p20_preserves_original_report_must():
    db = db_engine()
    item = brief(report=True)
    store, session = start(db, item)
    session = verify(db, store, session, "g_1", 15)
    restarted = ResearchSessionStore(db)
    restored = restarted.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    assert restored.accepted_brief.must_requirement_ids == ("g_1", "d_report")
    assert tuple(x.requirement_id for x in restored.accepted_brief.deliverables) == (
        "d_report",
    )
    _, _, report = seal_report(db, restarted, restored)
    assert report.report_id.startswith("p20r_")


def test_h_restart_after_p20_exact_report_artifact_fulfills_original_deliverable():
    db = db_engine()
    item = brief(report=True)
    store, session = start(db, item)
    session = verify(db, store, session, "g_1", 16)
    reports, _, report = seal_report(db, store, session)

    restarted_store = ResearchSessionStore(db)
    restarted_reports = ReportDocumentStore(
        research_store=restarted_store,
        db_engine=db,
    )
    restored_session = restarted_store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    restored_report = restarted_reports.load(
        report_id=report.report_id,
        principal=principal(),
    )
    projection, total, accounted, fulfilled = HeadlessProductComposer._project_user_must(
        brief=restored_session.accepted_brief,
        session=restored_session,
        report=restored_report,
    )
    by_id = {x.requirement_id: x for x in projection}
    assert by_id["d_report"].fulfilled_by_ref == report.report_id
    assert (total, accounted, fulfilled) == (2, 2, 2)


def test_i_no_report_historical_brief_behavior_remains_question_scoped():
    db = db_engine()
    item = brief(report=False)
    authority = ResearchBriefAuthoritySealer.seal(
        brief=item,
        request_ref="historical-no-report",
        source_message_hash="a" * 64,
    )
    assert authority.obligation_ids == ("g_1",)
    store, session = start(db, item)
    assert tuple(x.obligation_id for x in session.obligations) == ("g_1",)
    assert session.accepted_brief.must_requirement_ids == ("g_1",)
