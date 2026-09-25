from __future__ import annotations

import hashlib
import inspect
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

import app.v3.research_manager as manager_module
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
from app.v3.claim_lineage import (
    ClaimEpistemicState,
    ClaimEvidenceRelation,
    ClaimFreshness,
    ClaimLineageStore,
)
from app.v3.research import EvidenceRef, ObligationState, ResearchManager
from app.v3.research_exploration import ResearchExplorationStore
from app.v3.research_manager import (
    FollowupResult,
    ManagerAction,
    ManagerProposal,
    ManagerStopReason,
    ProposedClaimDraft,
    ReasoningStepStatus,
    ResearchInvestigationManager,
    ResearchManagerMaturationError,
    ResearchReasoningBudget,
)
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.models import (
    ResearchExecutionLink,
    ResearchInvestigationTaskRecord,
    ResearchReasoningStepRecord,
    Tenant,
    User,
)


TENANT = UUID("00000000-0000-4000-8000-000000001701")
USER = UUID("00000000-0000-4000-8000-000000001702")
STAMP = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)


def h(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def db_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal() -> Principal:
    return Principal(
        user_id=str(USER),
        tenant_id=str(TENANT),
        tenant_slug="p17",
        roles=["analyst"],
    )


def brief() -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="siparişler",
        candidate_id="native.sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    q = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.PERFORMANCE,
        source_text="Kanal performansındaki anlamlı farkı araştır.",
        subject_refs=(metric,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p17",
        objective=q.source_text,
        scope=ResearchScope(semantic_refs=(metric,)),
        questions=(q,),
        must_requirement_ids=("g1",),
        context_version="ctx-p17-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def freshness() -> ClaimFreshness:
    return ClaimFreshness(
        as_of=STAMP,
        stale_after=STAMP + timedelta(days=30),
    )


def setup_state(db):
    SQLModel.metadata.create_all(db)
    with Session(db) as s:
        s.add(Tenant(id=TENANT, slug="p17", name="P17", created_at=STAMP))
        s.add(
            User(
                id=USER,
                tenant_id=TENANT,
                email="p17@example.test",
                password_hash="unused",
                created_at=STAMP,
            )
        )
        s.commit()

    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=brief(),
        request_ref="p17-base",
        source_message_hash=hashlib.sha256(b"p17-base").hexdigest(),
        principal=principal(),
    )
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g1",
    )
    session = store.save(
        prepared.session,
        expected_revision=session.revision,
    )
    link = store.begin_delegation(
        session=session,
        obligation_id="g1",
        dima_request_id=prepared.request.dima_request_id,
        dima_trace_id=prepared.request.dima_trace_id,
        native_conversation_id=prepared.request.conversation_id,
    )
    query = {
        "database": 1,
        "type": "query",
        "query": {
            "source-table": 10,
            "aggregation": [["count"]],
            "breakout": [["field", 20, None]],
        },
    }
    link = store.mark_candidate(
        link.id,
        native_query_id="p17-base-query",
        native_query=query,
        query_fingerprint=h(query),
    )
    store.mark_execution_started(
        link.id,
        native_subject_ref="metabase-user:7",
    )
    result = {
        "database_id": 1,
        "row_count": 2,
        "data": {"rows": [["Web", 34], ["Partner", 12]]},
    }
    store.mark_executed(
        link.id,
        native_subject_ref="metabase-user:7",
        runtime_identity={
            "substrate": "metabase-native",
            "runtime_version": "v0.63.18-dima.6",
            "image_digest": "sha256:" + "a" * 64,
            "database_id": "metabase:1",
        },
        result_payload=result,
        result_hash=h(result),
        executed_at=STAMP,
    )
    evidence_id = "evi_" + "1" * 24
    receipt_id = "dqr_" + "1" * 24
    store.mark_verified(
        link.id,
        receipt_id=receipt_id,
        evidence_id=evidence_id,
    )

    item = ResearchManager.obligation(session, "g1").model_copy(
        update={
            "state": ObligationState.VERIFIED,
            "evidence_refs": (evidence_id,),
        }
    )
    session = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, item),
        evidence_refs=(
            EvidenceRef(
                evidence_id=evidence_id,
                receipt_id=receipt_id,
                authority_id=session.authority_id,
                obligation_id="g1",
            ),
        ),
    )
    session = store.save(
        session,
        expected_revision=session.revision - 1,
    )
    link = store.execution_link(link.id)

    lead = ResearchExplorationStore(db).persist(
        session_id=session.session_id,
        obligation_id="g1",
        execution_link_id=link.id,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        query_fingerprint=link.native_query_fingerprint,
        source_evidence_refs=(evidence_id,),
        material={
            "name": "Native channel exploration",
            "observations": [{"channel": "Web", "orders": 34}],
        },
        now=STAMP,
    )

    claims = ClaimLineageStore(
        research_store=store,
        db_engine=db,
    )
    claim = claims.create_claim(
        session_id=session.session_id,
        obligation_id="g1",
        principal=principal(),
        claim_text=(
            "Web kanalı incelenen kapsamda daha yüksek sipariş sayısına sahip."
        ),
        proposition={
            "subject": "channel:Web",
            "predicate": "has_higher_order_count_than",
            "object": "channel:Partner",
        },
        scope={
            "period": "Haziran 2026",
            "population": "sales_orders",
        },
        freshness=freshness(),
        origin_material_refs=(lead.lead_id,),
    )
    claim = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id=evidence_id,
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=principal(),
    )
    assert claim.epistemic_state == ClaimEpistemicState.SUPPORTED
    return store, session, link, lead, claims, claim


class ScriptedManager:
    def __init__(self, factory):
        self.factory = factory
        self.snapshots = []
        self.calls = 0

    def propose(self, snapshot):
        self.calls += 1
        self.snapshots.append(snapshot)
        return self.factory(snapshot)


class NeverCalledManager:
    def __init__(self):
        self.calls = 0

    def propose(self, snapshot):
        self.calls += 1
        raise AssertionError(
            "manager must not be called while durable work is pending"
        )


class PersistedFirstFollowup:
    def __init__(self, db):
        self.db = db
        self.calls = 0

    def execute(self, *, session, step, task, principal):
        self.calls += 1
        with Session(self.db) as s:
            step_row = s.get(ResearchReasoningStepRecord, step.step_id)
            task_row = s.get(
                ResearchInvestigationTaskRecord,
                task.task_id,
            )
            assert step_row is not None
            assert step_row.status == "PENDING"
            assert task_row is not None
            assert task_row.status == "PENDING"
        return FollowupResult(
            native_execution_refs=(f"native:{task.task_id}",),
            material_refs=(f"material:{task.task_id}",),
            evidence_refs=(f"evidence:{task.task_id}",),
        )


class FailOnceFollowup(PersistedFirstFollowup):
    def __init__(self, db):
        super().__init__(db)
        self.failed = False

    def execute(self, **kwargs):
        result = super().execute(**kwargs)
        if not self.failed:
            self.failed = True
            raise RuntimeError(
                "simulated process loss after durable task creation"
            )
        return result


def explore_proposal(
    snapshot,
    *,
    proposal_id="px",
    rationale="inspect gap",
    wording="Inspect the unresolved channel gap",
):
    return ManagerProposal(
        proposal_id=proposal_id,
        source_revision=snapshot.source_revision,
        target_parent_obligation="g1",
        action=ManagerAction.EXPLORE_NATIVE,
        objective_key="channel-gap.followup",
        bounded_objective=wording,
        rationale=rationale,
        inspected_evidence_refs=snapshot.evidence_refs,
        inspected_claim_refs=tuple(
            x.claim_id for x in snapshot.claims
        ),
        inspected_material_refs=snapshot.material_refs,
        expected_information_gain=(
            "Determine whether more native material changes the supported claim."
        ),
    )


def test_snapshot_is_governed_and_step_task_persist_before_followup_without_mutating_p14():
    db = db_engine()
    store, session, _, lead, claims, claim = setup_state(db)
    baseline = store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    followup = PersistedFirstFollowup(db)
    scripted = ScriptedManager(explore_proposal)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup,
        db_engine=db,
    )

    step, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=scripted,
    )

    snap = scripted.snapshots[0]
    assert snap.objective == session.objective
    assert snap.evidence_refs == ("evi_" + "1" * 24,)
    assert snap.material_refs == (lead.lead_id,)
    assert tuple(x.claim_id for x in snap.claims) == (
        claim.claim_id,
    )
    assert snap.claims[0].epistemic_state == "SUPPORTED"
    assert step.status == ReasoningStepStatus.COMPLETED
    assert task is not None
    assert task.status.value == "COMPLETED"
    assert followup.calls == 1

    restored = store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    assert restored.obligations == baseline.obligations
    assert restored.stopping == baseline.stopping
    assert restored.fingerprint == baseline.fingerprint

    with Session(db) as s:
        links = s.exec(
            select(ResearchExecutionLink).where(
                ResearchExecutionLink.session_id
                == session.session_id
            )
        ).all()
    assert len(links) == 1


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("evidence", "P17_EVIDENCE_REF_UNKNOWN"),
        ("claim", "P17_CLAIM_REF_UNKNOWN"),
        ("obligation", "P17_PARENT_OBLIGATION_OUT_OF_SCOPE"),
    ],
)
def test_invalid_refs_and_parent_scope_fail_closed(kind, expected):
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)

    def factory(snapshot):
        kwargs = dict(
            proposal_id=f"bad-{kind}",
            source_revision=snapshot.source_revision,
            target_parent_obligation="g1",
            action=ManagerAction.EXPLORE_NATIVE,
            objective_key=f"bad.{kind}",
            bounded_objective="Bounded invalid proposal",
            rationale="exercise fail-closed validation",
            inspected_evidence_refs=snapshot.evidence_refs,
            inspected_claim_refs=tuple(
                x.claim_id for x in snapshot.claims
            ),
            inspected_material_refs=snapshot.material_refs,
            expected_information_gain="none",
        )
        if kind == "evidence":
            kwargs["inspected_evidence_refs"] = (
                "evi_" + "9" * 24,
            )
        elif kind == "claim":
            kwargs["inspected_claim_refs"] = (
                "clm_" + "9" * 24,
            )
        else:
            kwargs["target_parent_obligation"] = "g-outside"
        return ManagerProposal(**kwargs)

    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    with pytest.raises(ResearchManagerMaturationError) as exc:
        service.run_one(
            session_id=session.session_id,
            principal=principal(),
            manager=ScriptedManager(factory),
        )
    assert exc.value.code == expected

    with Session(db) as s:
        assert s.exec(select(ResearchReasoningStepRecord)).all() == []


def test_same_material_identity_with_reworded_proposal_stops_as_no_progress():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    followup = PersistedFirstFollowup(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup,
        db_engine=db,
    )

    service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: explore_proposal(
                snap,
                proposal_id="first",
                rationale="first wording",
                wording="Inspect the channel gap.",
            )
        ),
    )

    step, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: explore_proposal(
                snap,
                proposal_id="second",
                rationale="completely different prose",
                wording=(
                    "Take another look at the same unresolved gap."
                ),
            )
        ),
    )
    assert task is None
    assert step.status == ReasoningStepStatus.NO_PROGRESS
    assert step.stop_reason == ManagerStopReason.NO_PROGRESS
    assert followup.calls == 1


def test_pending_step_resumes_after_restart_without_another_manager_turn():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    failing = FailOnceFollowup(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=failing,
        db_engine=db,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated process loss",
    ):
        service.run_one(
            session_id=session.session_id,
            principal=principal(),
            manager=ScriptedManager(explore_proposal),
        )

    with Session(db) as s:
        steps = s.exec(select(ResearchReasoningStepRecord)).all()
        tasks = s.exec(select(ResearchInvestigationTaskRecord)).all()
    assert len(steps) == 1
    assert steps[0].status == "PENDING"
    assert len(tasks) == 1
    assert tasks[0].status == "PENDING"

    resumed_store = ResearchSessionStore(db)
    resumed = ResearchInvestigationManager(
        research_store=resumed_store,
        claim_store=ClaimLineageStore(
            research_store=resumed_store,
            db_engine=db,
        ),
        followup_executor=failing,
        db_engine=db,
    )
    never = NeverCalledManager()
    step, task = resumed.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=never,
    )
    assert never.calls == 0
    assert failing.calls == 2
    assert step.status == ReasoningStepStatus.COMPLETED
    assert task is not None
    assert task.status.value == "COMPLETED"


def test_counter_evidence_is_first_class_child_task():
    db = db_engine()
    store, session, _, _, claims, claim = setup_state(db)
    followup = PersistedFirstFollowup(db)

    def counter(snapshot):
        return ManagerProposal(
            proposal_id="counter-1",
            source_revision=snapshot.source_revision,
            target_parent_obligation="g1",
            action=ManagerAction.SEEK_COUNTER_EVIDENCE,
            objective_key="claim.counter.channel-web",
            bounded_objective=(
                "Seek evidence that could challenge the supported Web-channel claim."
            ),
            rationale=(
                "A material supported claim should be challengeable."
            ),
            inspected_evidence_refs=snapshot.evidence_refs,
            inspected_claim_refs=(claim.claim_id,),
            inspected_material_refs=snapshot.material_refs,
            expected_information_gain=(
                "Learn whether the claim remains supported under a bounded challenge."
            ),
            counter_to_claim_id=claim.claim_id,
        )

    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup,
        db_engine=db,
    )
    step, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(counter),
    )
    assert step.status == ReasoningStepStatus.COMPLETED
    assert task is not None
    assert task.counter_to_claim_id == claim.claim_id


def test_form_claim_creates_only_p16_proposed_claim():
    db = db_engine()
    store, session, _, lead, claims, _ = setup_state(db)

    def form(snapshot):
        return ManagerProposal(
            proposal_id="form-1",
            source_revision=snapshot.source_revision,
            target_parent_obligation="g1",
            action=ManagerAction.FORM_CLAIM,
            objective_key="claim.form.channel-share",
            bounded_objective=(
                "Form a bounded claim from existing native material."
            ),
            rationale=(
                "The material is claim-shaped but has not yet been asserted."
            ),
            inspected_evidence_refs=snapshot.evidence_refs,
            inspected_claim_refs=tuple(
                x.claim_id for x in snapshot.claims
            ),
            inspected_material_refs=(lead.lead_id,),
            expected_information_gain=(
                "Expose the proposition for explicit Evidence linking."
            ),
            claim=ProposedClaimDraft(
                claim_text=(
                    "Web kanalı incelenen kapsamda sipariş hacminin çoğunu oluşturuyor."
                ),
                proposition={
                    "subject": "channel:Web",
                    "predicate": "has_majority_share",
                    "object": "sales_orders",
                },
                scope={
                    "period": "Haziran 2026",
                    "population": "sales_orders",
                },
                freshness=freshness(),
                origin_material_refs=(lead.lead_id,),
            ),
        )

    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        db_engine=db,
    )
    step, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(form),
    )
    assert task is None
    assert step.status == ReasoningStepStatus.COMPLETED
    assert len(step.result_refs) == 1

    created = claims.load_claim(
        session_id=session.session_id,
        claim_id=step.result_refs[0],
        principal=principal(),
    )
    assert created.epistemic_state == ClaimEpistemicState.PROPOSED
    assert created.evidence_links == ()


def test_stop_is_durable_and_does_not_force_a_result():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)

    def stop(snapshot):
        return ManagerProposal(
            proposal_id="stop-1",
            source_revision=snapshot.source_revision,
            target_parent_obligation="g1",
            action=ManagerAction.STOP,
            objective_key="stop.inconclusive",
            rationale=(
                "Available governed material does not support a stronger conclusion."
            ),
            stop_reason=ManagerStopReason.INCONCLUSIVE,
        )

    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        db_engine=db,
    )
    step, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(stop),
    )
    assert task is None
    assert step.status == ReasoningStepStatus.STOPPED
    assert step.stop_reason == ManagerStopReason.INCONCLUSIVE

    never = NeverCalledManager()
    with pytest.raises(ResearchManagerMaturationError) as exc:
        service.run_one(
            session_id=session.session_id,
            principal=principal(),
            manager=never,
        )
    assert never.calls == 0
    assert exc.value.code == "P17_INVESTIGATION_TERMINAL"


def test_reasoning_budget_is_separate_from_sealed_p14_completion():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        budget=ResearchReasoningBudget(
            max_reasoning_steps=1,
            max_followup_native_turns=1,
            max_counter_evidence_attempts=1,
        ),
        db_engine=db,
    )
    service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(explore_proposal),
    )

    never = NeverCalledManager()
    step, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=never,
    )
    assert never.calls == 0
    assert task is None
    assert step.status == ReasoningStepStatus.STOPPED
    assert step.stop_reason == ManagerStopReason.BUDGET_EXHAUSTED

    restored = store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    assert restored.stopping.status.value == "COMPLETE"
    assert restored.obligations[0].state == ObligationState.VERIFIED


def test_p17_has_no_second_analytics_planner_or_forbidden_analytical_dependencies():
    source = inspect.getsource(manager_module)
    for forbidden in (
        "NativeStandardTrustOrchestrator",
        "ResolvedAnalyticsIntent",
        "TemporalBindingEngine",
        "MetabaseProjectionCompiler",
        "MetabaseCanonicalizer",
        "attest_native_query",
        "execute_native_query",
        "app.wren",
        "wren_service",
        "breakdown(",
        "trend(",
        "rank(",
        "compare(",
    ):
        assert forbidden not in source

    imported_roots = set()
    tree = __import__("ast").parse(source)
    for node in __import__("ast").walk(tree):
        if isinstance(node, __import__("ast").Import):
            imported_roots.update(
                alias.name.split(".")[0] for alias in node.names
            )
        elif (
            isinstance(node, __import__("ast").ImportFrom)
            and node.module
        ):
            imported_roots.add(node.module.split(".")[0])

    assert imported_roots.isdisjoint(
        {"numpy", "pandas", "scipy", "statistics"}
    )
