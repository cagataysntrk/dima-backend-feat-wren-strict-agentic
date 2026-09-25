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
    InvestigationIntent,
    InvestigationTargetKind,
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

    def execute(
        self,
        *,
        session,
        step,
        task,
        principal,
        native_session_token=None,
    ):
        del native_session_token
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


class LineagedFollowup:
    """Provider-free test double that persists a real P17 follow-up occurrence."""

    def __init__(self, db, store):
        self.db = db
        self.store = store
        self.link = None
        self.lead = None

    def execute(
        self,
        *,
        session,
        step,
        task,
        principal,
        native_session_token=None,
    ):
        del principal, native_session_token
        request_id = f"p17-test-{step.step_id}-{task.task_id}"
        conversation = session.native_conversation
        assert conversation is not None
        link = self.store.begin_delegation(
            session=session,
            obligation_id=task.parent_obligation_id,
            dima_request_id=request_id,
            dima_trace_id=request_id + "-trace",
            native_conversation_id=conversation.conversation_id,
            execution_kind="P17_FOLLOWUP",
            reasoning_step_id=step.step_id,
            investigation_task_id=task.task_id,
        )
        query = {
            "database": 1,
            "type": "query",
            "query": {
                "source-table": 10,
                "aggregation": [["count"]],
                "filter": ["=", ["field", 20, None], "Partner"],
            },
        }
        link = self.store.mark_candidate(
            link.id,
            native_query_id="p17-followup-query",
            native_query=query,
            query_fingerprint=h(query),
        )
        self.store.mark_execution_started(
            link.id,
            native_subject_ref="metabase-user:7",
        )
        result = {
            "database_id": 1,
            "row_count": 1,
            "data": {"rows": [["Partner", 41]]},
        }
        self.store.mark_executed(
            link.id,
            native_subject_ref="metabase-user:7",
            runtime_identity={
                "substrate": "metabase-native",
                "runtime_version": "v0.63.18-dima.6",
                "image_digest": "sha256:" + "b" * 64,
                "database_id": "metabase:1",
            },
            result_payload=result,
            result_hash=h(result),
            executed_at=STAMP + timedelta(minutes=1),
        )
        evidence_id = "evi_" + "2" * 24
        receipt_id = "dqr_" + "2" * 24
        link = self.store.mark_verified(
            link.id,
            receipt_id=receipt_id,
            evidence_id=evidence_id,
        )
        lead = ResearchExplorationStore(self.db).persist(
            session_id=session.session_id,
            obligation_id=task.parent_obligation_id,
            execution_link_id=link.id,
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            query_fingerprint=link.native_query_fingerprint,
            source_evidence_refs=(evidence_id,),
            material={
                "name": "P17 counter-evidence material",
                "observations": [{"channel": "Partner", "orders": 41}],
            },
            now=STAMP + timedelta(minutes=2),
        )
        self.link = link
        self.lead = lead
        return FollowupResult(
            native_execution_refs=(str(link.id),),
            material_refs=(lead.lead_id,),
            evidence_refs=(evidence_id,),
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

def test_followup_lineage_preserves_p15_base_and_can_challenge_claim_via_p16():
    db = db_engine()
    store, session, base_link, _, claims, claim = setup_state(db)
    followup = LineagedFollowup(db, store)

    def counter(snapshot):
        return ManagerProposal(
            proposal_id="counter-lineage",
            source_revision=snapshot.source_revision,
            target_parent_obligation="g1",
            action=ManagerAction.SEEK_COUNTER_EVIDENCE,
            objective_key="claim.counter.partner-orders",
            bounded_objective=(
                "Check whether Partner can exceed Web in a bounded native slice."
            ),
            rationale="Seek a material challenge to the supported channel claim.",
            inspected_evidence_refs=snapshot.evidence_refs,
            inspected_claim_refs=(claim.claim_id,),
            inspected_material_refs=snapshot.material_refs,
            expected_information_gain=(
                "Determine whether the current supported claim becomes contested."
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
    assert followup.link is not None
    assert followup.link.execution_kind == "P17_FOLLOWUP"
    assert followup.link.reasoning_step_id == step.step_id
    assert followup.link.investigation_task_id == task.task_id

    still_base = store.verified_link(
        session_id=session.session_id,
        obligation_id="g1",
    )
    assert still_base.id == base_link.id
    assert still_base.execution_kind == "P14_BASE"

    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert "evi_" + "2" * 24 in snap.evidence_refs
    assert followup.lead is not None
    assert followup.lead.lead_id in snap.material_refs
    material = next(
        x for x in snap.materials if x.lead_id == followup.lead.lead_id
    )
    assert material.native_name == "P17 counter-evidence material"
    assert not hasattr(material, "material")

    contested = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id="evi_" + "2" * 24,
        relation=ClaimEvidenceRelation.CHALLENGES,
        principal=principal(),
    )
    assert contested.epistemic_state == ClaimEpistemicState.CONTESTED
    assert {x.relation for x in contested.evidence_links} == {
        ClaimEvidenceRelation.SUPPORTS,
        ClaimEvidenceRelation.CHALLENGES,
    }

    restored = store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert restored.stopping.status.value == "COMPLETE"


def test_followup_adapter_delegates_to_shared_occurrence_runner_only():
    import app.v3.research_followup as followup_module

    source = inspect.getsource(followup_module)
    assert "NativeResearchOccurrenceRunner" in source
    assert "self._runner.execute" in source
    for forbidden in (
        "execute_dataset(",
        "bridge.invoke(",
        "DimaQueryReceiptSealer",
        "MetabaseProjectionCompiler",
        "MetabaseCanonicalizer",
    ):
        assert forbidden not in source

def recursive_proposal(
    snapshot,
    *,
    proposal_id,
    objective_key,
    intent,
    parent_step_id=None,
    branch_key=None,
    target_kind=InvestigationTargetKind.GAP,
    target_ref=None,
    rationale="bounded recursive investigation",
    wording="Investigate the bounded recursive question.",
):
    action = (
        ManagerAction.SEEK_COUNTER_EVIDENCE
        if intent == InvestigationIntent.SEEK_COUNTER_EVIDENCE
        else ManagerAction.STOP
        if intent
        in {
            InvestigationIntent.STOP_BRANCH,
            InvestigationIntent.STOP_INVESTIGATION,
        }
        else ManagerAction.RECORD_INVESTIGATION
        if intent
        in {
            InvestigationIntent.EXPLORE_ALTERNATIVES,
            InvestigationIntent.DEEPEN_EXPLANATION,
            InvestigationIntent.REPLAN,
        }
        else ManagerAction.EXPLORE_NATIVE
    )
    kwargs = dict(
        proposal_id=proposal_id,
        source_revision=snapshot.source_revision,
        target_parent_obligation="g1",
        action=action,
        intent=intent,
        parent_step_id=parent_step_id,
        branch_key=branch_key,
        target_kind=target_kind,
        target_ref=target_ref,
        objective_key=objective_key,
        bounded_objective=(
            None
            if action == ManagerAction.STOP
            else wording
        ),
        rationale=rationale,
        inspected_evidence_refs=snapshot.evidence_refs,
        inspected_claim_refs=tuple(x.claim_id for x in snapshot.claims),
        inspected_material_refs=snapshot.material_refs,
        expected_information_gain=(
            None
            if action == ManagerAction.STOP
            else "A bounded branch may materially change the investigation."
        ),
        stop_reason=(
            ManagerStopReason.NO_MEANINGFUL_GAIN
            if intent == InvestigationIntent.STOP_BRANCH
            else ManagerStopReason.INCONCLUSIVE
            if intent == InvestigationIntent.STOP_INVESTIGATION
            else None
        ),
    )
    if intent == InvestigationIntent.SEEK_COUNTER_EVIDENCE:
        claim = snapshot.claims[0]
        kwargs["counter_to_claim_id"] = claim.claim_id
        kwargs["target_kind"] = InvestigationTargetKind.CLAIM
        kwargs["target_ref"] = claim.claim_id
    return ManagerProposal(**kwargs)


def test_recursive_root_child_and_restart_reconstruct_exact_topology():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    followup = PersistedFirstFollowup(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup,
        db_engine=db,
    )

    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="root-gap",
                objective_key="orders.issue",
                intent=InvestigationIntent.INVESTIGATE_GAP,
                target_kind=InvestigationTargetKind.EFFECT,
                target_ref="orders-down",
            )
        ),
    )
    child, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="child-explanation",
                objective_key="orders.issue.web",
                intent=InvestigationIntent.DEEPEN_EXPLANATION,
                parent_step_id=root.step_id,
                target_kind=InvestigationTargetKind.EXPLANATION,
                target_ref="web-orders-down",
            )
        ),
    )

    assert root.parent_step_id is None
    assert root.depth == 0
    assert child.parent_step_id == root.step_id
    assert child.depth == 1
    assert child.branch_id == root.branch_id

    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    root_node = next(
        x for x in snap.investigation.nodes if x.step_id == root.step_id
    )
    child_node = next(
        x for x in snap.investigation.nodes if x.step_id == child.step_id
    )
    assert root_node.child_step_ids == (child.step_id,)
    assert child_node.parent_step_id == root.step_id
    assert snap.investigation.max_observed_depth == 1

    restarted_store = ResearchSessionStore(db)
    restarted = ResearchInvestigationManager(
        research_store=restarted_store,
        claim_store=ClaimLineageStore(
            research_store=restarted_store,
            db_engine=db,
        ),
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    restored = restarted.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert restored.investigation == snap.investigation


def test_multiple_sibling_branches_and_branch_local_stop_preserve_other_branch():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="root-multi",
                objective_key="orders.multi",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )

    branch_a, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="alt-a",
                objective_key="orders.alt.web",
                intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
                parent_step_id=root.step_id,
                branch_key="web-conversion",
                target_kind=InvestigationTargetKind.ALTERNATIVE,
                target_ref="web-conversion",
            )
        ),
    )
    branch_b, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="alt-b",
                objective_key="orders.alt.inventory",
                intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
                parent_step_id=root.step_id,
                branch_key="inventory",
                target_kind=InvestigationTargetKind.ALTERNATIVE,
                target_ref="inventory",
            )
        ),
    )
    assert branch_a.branch_id != branch_b.branch_id
    assert branch_a.parent_step_id == branch_b.parent_step_id == root.step_id

    stopped, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="stop-a",
                objective_key="orders.alt.web.stop",
                intent=InvestigationIntent.STOP_BRANCH,
                parent_step_id=branch_a.step_id,
                target_kind=InvestigationTargetKind.ALTERNATIVE,
                target_ref="web-conversion",
            )
        ),
    )
    assert task is None
    assert stopped.stop_scope.value == "BRANCH"
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert branch_a.branch_id in snap.investigation.stopped_branch_ids
    assert branch_b.branch_id in snap.investigation.open_branch_ids
    assert snap.terminal_stop_reason is None

    deeper_b, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="deepen-b",
                objective_key="orders.alt.inventory.deep",
                intent=InvestigationIntent.DEEPEN_EXPLANATION,
                parent_step_id=branch_b.step_id,
                target_kind=InvestigationTargetKind.EXPLANATION,
                target_ref="inventory-availability",
            )
        ),
    )
    assert deeper_b.branch_id == branch_b.branch_id
    assert deeper_b.depth == branch_b.depth + 1


def test_global_stop_is_distinct_from_branch_stop_and_blocks_future_manager_turns():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="root-global",
                objective_key="orders.global",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )
    stopped, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="global-stop",
                objective_key="investigation.stop",
                intent=InvestigationIntent.STOP_INVESTIGATION,
                parent_step_id=root.step_id,
            )
        ),
    )
    assert stopped.stop_scope.value == "INVESTIGATION"
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert snap.terminal_stop_reason == ManagerStopReason.INCONCLUSIVE

    never = NeverCalledManager()
    with pytest.raises(ResearchManagerMaturationError) as exc:
        service.run_one(
            session_id=session.session_id,
            principal=principal(),
            manager=never,
        )
    assert exc.value.code == "P17_INVESTIGATION_TERMINAL"
    assert never.calls == 0


def test_recursive_depth_budget_is_bounded_and_not_a_target():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        budget=ResearchReasoningBudget(
            max_reasoning_steps=12,
            max_followup_native_turns=12,
            max_counter_evidence_attempts=4,
            max_depth=1,
        ),
        db_engine=db,
    )
    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="depth-root",
                objective_key="depth.root",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )
    child, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="depth-child",
                objective_key="depth.child",
                intent=InvestigationIntent.DEEPEN_EXPLANATION,
                parent_step_id=root.step_id,
            )
        ),
    )
    assert child.depth == 1

    with pytest.raises(ResearchManagerMaturationError) as exc:
        service.run_one(
            session_id=session.session_id,
            principal=principal(),
            manager=ScriptedManager(
                lambda snap: recursive_proposal(
                    snap,
                    proposal_id="depth-grandchild",
                    objective_key="depth.grandchild",
                    intent=InvestigationIntent.DEEPEN_EXPLANATION,
                    parent_step_id=child.step_id,
                )
            ),
        )
    assert exc.value.code == "P17_DEPTH_BUDGET_EXHAUSTED"
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert snap.investigation.max_observed_depth == 1


def test_child_counter_evidence_is_first_class_in_graph_projection():
    db = db_engine()
    store, session, _, _, claims, claim = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="counter-root",
                objective_key="counter.root",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )
    counter, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="counter-child",
                objective_key="counter.child",
                intent=InvestigationIntent.SEEK_COUNTER_EVIDENCE,
                parent_step_id=root.step_id,
                target_ref=claim.claim_id,
            )
        ),
    )
    assert task is not None
    node = next(
        x
        for x in service.snapshot(
            session_id=session.session_id,
            principal=principal(),
        ).investigation.nodes
        if x.step_id == counter.step_id
    )
    assert node.counter_evidence_refs == task.evidence_refs
    assert node.target_kind == InvestigationTargetKind.CLAIM


def test_replan_is_investigation_semantics_and_never_mutates_p14_authority():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    baseline = store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="replan-root",
                objective_key="replan.root",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )
    replanned, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="replan-child",
                objective_key="replan.next-question",
                intent=InvestigationIntent.REPLAN,
                parent_step_id=root.step_id,
                target_kind=InvestigationTargetKind.QUESTION,
                target_ref="next-question",
            )
        ),
    )
    assert replanned.intent == InvestigationIntent.REPLAN
    restored = store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    assert restored.obligations == baseline.obligations
    assert restored.stopping == baseline.stopping
    assert restored.fingerprint == baseline.fingerprint


def test_same_recursive_proposal_without_new_material_becomes_branch_no_progress():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="np-root",
                objective_key="np.root",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )
    first, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="np-first",
                objective_key="np.same",
                intent=InvestigationIntent.DEEPEN_EXPLANATION,
                parent_step_id=root.step_id,
                rationale="first prose",
                wording="First phrasing of the same bounded question.",
            )
        ),
    )
    repeated, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="np-second",
                objective_key="np.same",
                intent=InvestigationIntent.DEEPEN_EXPLANATION,
                parent_step_id=root.step_id,
                rationale="different prose",
                wording="Different words, same normalized investigation identity.",
            )
        ),
    )
    assert task is None
    assert repeated.status == ReasoningStepStatus.NO_PROGRESS
    assert repeated.stop_reason == ManagerStopReason.NO_PROGRESS
    assert repeated.stop_scope.value == "BRANCH"
    assert repeated.branch_id == first.branch_id
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert first.branch_id in snap.investigation.stopped_branch_ids
    assert snap.terminal_stop_reason is None


def test_cross_session_parent_expansion_fails_closed():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )
    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="scope-root",
                objective_key="scope.root",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )

    second = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=brief().model_copy(update={"brief_id": "rb-p17-second"}),
        request_ref="p17-second",
        source_message_hash=hashlib.sha256(b"p17-second").hexdigest(),
        principal=principal(),
    )
    with pytest.raises(ResearchManagerMaturationError) as exc:
        service.run_one(
            session_id=second.session_id,
            principal=principal(),
            manager=ScriptedManager(
                lambda snap: recursive_proposal(
                    snap,
                    proposal_id="scope-child",
                    objective_key="scope.child",
                    intent=InvestigationIntent.DEEPEN_EXPLANATION,
                    parent_step_id=root.step_id,
                )
            ),
        )
    assert exc.value.code == "P17_PARENT_STEP_NOT_LEGAL"


def test_recursive_vocabulary_contains_no_causal_or_contribution_authority():
    assert {
        InvestigationIntent.INVESTIGATE_GAP,
        InvestigationIntent.EXPLORE_ALTERNATIVES,
        InvestigationIntent.SEEK_COUNTER_EVIDENCE,
        InvestigationIntent.DEEPEN_EXPLANATION,
        InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
        InvestigationIntent.REPLAN,
        InvestigationIntent.STOP_BRANCH,
        InvestigationIntent.STOP_INVESTIGATION,
    }.issubset(set(InvestigationIntent))

    source = inspect.getsource(manager_module)
    forbidden = (
        "causal_confidence",
        "causal_score",
        "direct_effect",
        "indirect_effect",
        "path_strength",
        "bayesian",
        "contribution_calculator",
    )
    assert not any(token in source.lower() for token in forbidden)

def test_child_depth_reuses_p15_material_and_single_p16_claim_authority():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        db_engine=db,
    )

    root, root_task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="material-root-gap",
                objective_key="material.root.gap",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )
    assert root_task is not None
    assert root.depth == 0

    candidate, candidate_task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="material-candidate",
                objective_key="material.candidate",
                intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
                parent_step_id=root.step_id,
                branch_key="material-candidate",
                target_kind=InvestigationTargetKind.ALTERNATIVE,
                target_ref="candidate-root",
            )
        ),
    )
    assert candidate_task is None
    assert candidate.depth == 1
    assert candidate.branch_id != root.branch_id

    followup = LineagedFollowup(db, store)
    service._followup = followup
    child, child_task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="material-child",
                objective_key="material.child.test",
                intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
                parent_step_id=candidate.step_id,
                target_kind=InvestigationTargetKind.EXPLANATION,
                target_ref="partner-orders",
            )
        ),
    )
    assert child_task is not None
    assert child.depth == 2
    assert child.branch_id == candidate.branch_id
    assert followup.lead is not None
    assert followup.link is not None
    assert followup.link.execution_kind == "P17_FOLLOWUP"

    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    node = next(
        x for x in snap.investigation.nodes if x.step_id == child.step_id
    )
    assert followup.lead.lead_id in node.native_material_refs
    assert followup.lead.lead_id in snap.material_refs

    claim = claims.create_claim(
        session_id=session.session_id,
        obligation_id="g1",
        principal=principal(),
        claim_text=(
            "Partner kanalı child-depth native material içinde 41 sipariş gösteriyor."
        ),
        proposition={
            "subject": "channel:Partner",
            "predicate": "has_order_count",
            "object": 41,
        },
        scope={
            "period": "P17 recursive child material",
            "population": "sales_orders",
        },
        freshness=freshness(),
        origin_material_refs=(followup.lead.lead_id,),
    )
    assert claim.epistemic_state == ClaimEpistemicState.PROPOSED

    supported = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id="evi_" + "2" * 24,
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=principal(),
    )
    assert supported.epistemic_state == ClaimEpistemicState.SUPPORTED
    assert supported.origin_material_refs == (followup.lead.lead_id,)

def test_structured_live_manager_adapter_is_typed_provider_free():
    from app.v3.research_manager_provider import (
        StructuredResearchProposalManager,
    )

    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    snapshot = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        db_engine=db,
    ).snapshot(
        session_id=session.session_id,
        principal=principal(),
    )

    class FakeStructured:
        calls = 0

        def structured_json(
            self,
            system,
            user,
            *,
            schema,
            schema_name,
        ):
            self.calls += 1
            assert "METABASE + METABOT = analytical engine" in system
            assert "GOVERNED SNAPSHOT JSON" in user
            assert schema_name == "dima_p17_research_manager_proposal"
            assert schema["type"] == "object"
            payload = {
                "proposal_id": "live-fake-1",
                "source_revision": snapshot.source_revision,
                "target_parent_obligation": "g1",
                "intent": "INVESTIGATE_GAP",
                "parent_step_id": None,
                "branch_key": None,
                "target_kind": "GAP",
                "target_ref": "observed-gap",
                "objective_key": "live.gap.root",
                "bounded_objective": (
                    "Investigate the unresolved bounded gap."
                ),
                "rationale": "The root gap remains unresolved.",
                "inspected_evidence_refs": list(snapshot.evidence_refs),
                "inspected_claim_refs": [
                    x.claim_id for x in snapshot.claims
                ],
                "inspected_material_refs": list(snapshot.material_refs),
                "expected_information_gain": (
                    "It may distinguish a channel-specific explanation."
                ),
            }
            assert set(schema["properties"]) == {"proposal"}
            return json.dumps({"proposal": payload})

    transport = FakeStructured()
    manager = StructuredResearchProposalManager(transport=transport)
    proposal = manager.propose(snapshot)
    assert transport.calls == 1
    assert manager.call_count == 1
    assert proposal.intent == InvestigationIntent.INVESTIGATE_GAP
    assert proposal.action == ManagerAction.EXPLORE_NATIVE
    assert proposal.branch_key is None


def test_structured_live_manager_cannot_emit_legacy_intent():
    from app.v3.research_manager_provider import (
        StructuredResearchProposalManager,
    )

    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    snapshot = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        db_engine=db,
    ).snapshot(
        session_id=session.session_id,
        principal=principal(),
    )

    class LegacyTransport:
        def structured_json(self, *args, **kwargs):
            schema = kwargs["schema"]
            payload = {
                "proposal_id": "legacy-not-allowed",
                "source_revision": snapshot.source_revision,
                "target_parent_obligation": "g1",
                "intent": "LEGACY",
                "parent_step_id": None,
                "branch_key": None,
                "target_kind": "GAP",
                "target_ref": None,
                "objective_key": "legacy.bad",
                "bounded_objective": "bad",
                "rationale": "bad",
                "inspected_evidence_refs": [],
                "inspected_claim_refs": [],
                "inspected_material_refs": [],
                "expected_information_gain": "bad",
            }
            assert set(schema["properties"]) == {"proposal"}
            return json.dumps({"proposal": payload})

    with pytest.raises(ValueError, match="LEGACY"):
        StructuredResearchProposalManager(
            transport=LegacyTransport()
        ).propose(snapshot)

def test_live_manager_schema_is_strict_transport_safe():
    from app.v3.research_manager_provider import _schema_for_intents

    schema = _schema_for_intents(
        (InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,)
    )

    def walk(node):
        if isinstance(node, dict):
            for forbidden_key in (
                "default",
                "minLength",
                "maxLength",
                "pattern",
                "minimum",
                "maximum",
                "format",
            ):
                assert forbidden_key not in node
            props = node.get("properties")
            if isinstance(props, dict):
                assert node.get("additionalProperties") is False
                assert set(node.get("required") or ()) == set(props)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
    props = schema["properties"]
    assert props["intent"]["enum"] == [
        "TEST_DISCRIMINATING_EVIDENCE"
    ]
    assert "claim" not in props
    assert "counter_to_claim_id" not in props
    assert "stop_reason" not in props
    assert "ProposedClaimDraft" not in (schema.get("$defs") or {})
    assert "ClaimFreshness" not in (schema.get("$defs") or {})
    assert props["bounded_objective"] == {"type": "string"}
    assert props["expected_information_gain"] == {"type": "string"}

def test_live_manager_guidance_cannot_broaden_state_derived_legality():
    from app.v3.research_manager_provider import (
        StructuredResearchProposalManager,
    )

    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    snapshot = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        db_engine=db,
    ).snapshot(
        session_id=session.session_id,
        principal=principal(),
    )

    class NeverTransport:
        def structured_json(self, *args, **kwargs):
            raise AssertionError(
                "illegal screenplay constraint must fail before provider call"
            )

    with pytest.raises(ValueError, match="no state-legal"):
        StructuredResearchProposalManager(
            transport=NeverTransport()
        ).propose_with_guidance(
            snapshot,
            guidance="Open one candidate branch.",
            allowed_intents=(InvestigationIntent.EXPLORE_ALTERNATIVES,),
            allowed_parent_step_ids=(None,),
            branch_key_mode="string",
        )

def test_live_manager_draft_rejects_null_information_gain_before_authority_mapping():
    from app.v3.research_manager_provider import ResearchManagerProposalDraft

    with pytest.raises(
        ValueError,
        match="expected_information_gain",
    ):
        ResearchManagerProposalDraft.model_validate(
            {
                "proposal_id": "live-null-ig",
                "source_revision": 1,
                "target_parent_obligation": "g1",
                "intent": "INVESTIGATE_GAP",
                "target_kind": "GAP",
                "objective_key": "gap.null-ig",
                "bounded_objective": "Investigate the observed gap.",
                "rationale": "A bounded next question is needed.",
                "expected_information_gain": None,
            }
        )


def test_live_stop_draft_requires_explicit_stop_reason():
    from app.v3.research_manager_provider import ResearchManagerProposalDraft

    with pytest.raises(ValueError, match="stop_reason"):
        ResearchManagerProposalDraft.model_validate(
            {
                "proposal_id": "live-stop-no-reason",
                "source_revision": 1,
                "target_parent_obligation": "g1",
                "intent": "STOP_INVESTIGATION",
                "target_kind": "GAP",
                "objective_key": "stop.no-reason",
                "rationale": "Stop was requested.",
            }
        )

def test_replan_continues_manager_selected_second_sibling_branch():
    """Regression for corrected-live HARNESS RED: selection may be sibling B."""

    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=PersistedFirstFollowup(db),
        budget=ResearchReasoningBudget(
            max_reasoning_steps=10,
            max_followup_native_turns=4,
            max_counter_evidence_attempts=2,
            max_depth=5,
        ),
        db_engine=db,
    )

    root, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="selected-b-root",
                objective_key="selected-b.root",
                intent=InvestigationIntent.INVESTIGATE_GAP,
            )
        ),
    )
    alt_a, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="selected-b-alt-a",
                objective_key="selected-b.alt-a",
                intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
                parent_step_id=root.step_id,
                branch_key="candidate-a",
                target_kind=InvestigationTargetKind.ALTERNATIVE,
                target_ref="candidate-a",
            )
        ),
    )
    alt_b, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="selected-b-alt-b",
                objective_key="selected-b.alt-b",
                intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
                parent_step_id=root.step_id,
                branch_key="candidate-b",
                target_kind=InvestigationTargetKind.ALTERNATIVE,
                target_ref="candidate-b",
            )
        ),
    )
    assert alt_a.branch_id != alt_b.branch_id

    tested_b, task = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="selected-b-test",
                objective_key="selected-b.test",
                intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
                parent_step_id=alt_b.step_id,
                target_kind=InvestigationTargetKind.EXPLANATION,
                target_ref="candidate-b",
            )
        ),
    )
    assert task is not None
    assert tested_b.branch_id == alt_b.branch_id

    deep_b, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="selected-b-deepen",
                objective_key="selected-b.deepen",
                intent=InvestigationIntent.DEEPEN_EXPLANATION,
                parent_step_id=tested_b.step_id,
                target_kind=InvestigationTargetKind.EXPLANATION,
                target_ref="candidate-b-child",
            )
        ),
    )
    assert deep_b.branch_id == alt_b.branch_id

    replan_b, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(
                snap,
                proposal_id="selected-b-replan",
                objective_key="selected-b.replan",
                intent=InvestigationIntent.REPLAN,
                parent_step_id=deep_b.step_id,
                target_kind=InvestigationTargetKind.QUESTION,
                target_ref="candidate-b-next",
            )
        ),
    )
    assert replan_b.branch_id == alt_b.branch_id
    assert replan_b.branch_id != alt_a.branch_id


def test_live_canary_replan_assertion_uses_runtime_selected_parent():
    """Provider-free guard against reintroducing candidate-A hard coding."""

    from pathlib import Path

    source = (
        Path(__file__).parents[1]
        / "lab"
        / "metabase"
        / "p17"
        / "recursive_manager_scenario_lab.py"
    ).read_text(encoding="utf-8")
    start = source.index("    replanned = stage(")
    end = source.index("    final_stop = stage(", start)
    replan_slice = source[start:end]
    assert "replan_step.branch_id != selected_parent.branch_id" in replan_slice
    assert "replan_step.branch_id != alt_a_step.branch_id" not in replan_slice



# --- DMP-DEC-0053: thin investigation language / state-derived legality ---


def _dmp0053_service(db, *, max_depth=5, followup=None):
    store, session, _, lead, claims, claim = setup_state(db)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup or PersistedFirstFollowup(db),
        budget=ResearchReasoningBudget(
            max_reasoning_steps=12,
            max_followup_native_turns=6,
            max_counter_evidence_attempts=3,
            max_depth=max_depth,
        ),
        db_engine=db,
    )
    return store, session, lead, claims, claim, service


def _dmp0053_run(service, session, **proposal_kwargs):
    return service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(
            lambda snap: recursive_proposal(snap, **proposal_kwargs)
        ),
    )


def test_dmp0053_initial_action_profile_is_state_projection_not_plan():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    snapshot = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert snapshot.action_profile.legal_intents == (
        InvestigationIntent.INVESTIGATE_GAP,
        InvestigationIntent.STOP_INVESTIGATION,
    )
    source = inspect.getsource(manager_module._build_action_profile).lower()
    for forbidden in (
        "best",
        "interestingness",
        "rank",
        "score",
        "winner",
        "breakdown",
        "dimension",
    ):
        assert forbidden not in source


def test_dmp0053_branch_key_on_investigate_gap_rejected_before_persistence():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    before = service._ledger.steps(session.session_id)
    with pytest.raises(ResearchManagerMaturationError) as exc:
        _dmp0053_run(
            service,
            session,
            proposal_id="illegal-root-key",
            objective_key="root.illegal-key",
            intent=InvestigationIntent.INVESTIGATE_GAP,
            branch_key="must-not-mint",
        )
    assert exc.value.code == "P17_BRANCH_KEY_FORBIDDEN"
    assert service._ledger.steps(session.session_id) == before


def test_dmp0053_parentless_explore_alternatives_rejected_before_persistence():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    with pytest.raises(ResearchManagerMaturationError) as exc:
        _dmp0053_run(
            service,
            session,
            proposal_id="floating-alt",
            objective_key="alt.floating",
            intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
            branch_key="floating",
            target_kind=InvestigationTargetKind.ALTERNATIVE,
        )
    assert exc.value.code == "P17_INTENT_NOT_LEGAL_IN_STATE"
    assert service._ledger.steps(session.session_id) == ()


def test_dmp0053_explore_open_parent_mints_one_child_branch():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="root",
        objective_key="root.gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    alt, task = _dmp0053_run(
        service,
        session,
        proposal_id="alt",
        objective_key="alt.one",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id,
        branch_key="candidate-one",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    assert task is None
    assert alt.parent_step_id == root.step_id
    assert alt.depth == root.depth + 1
    assert alt.branch_id != root.branch_id


def test_dmp0053_deepen_requires_open_parent_forbids_branch_key_and_inherits():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="root",
        objective_key="root.gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    with pytest.raises(ResearchManagerMaturationError) as no_parent:
        _dmp0053_run(
            service,
            session,
            proposal_id="deep-none",
            objective_key="deep.none",
            intent=InvestigationIntent.DEEPEN_EXPLANATION,
        )
    assert no_parent.value.code == "P17_PARENT_STEP_REQUIRED"

    with pytest.raises(ResearchManagerMaturationError) as keyed:
        _dmp0053_run(
            service,
            session,
            proposal_id="deep-keyed",
            objective_key="deep.keyed",
            intent=InvestigationIntent.DEEPEN_EXPLANATION,
            parent_step_id=root.step_id,
            branch_key="illegal-new-branch",
        )
    assert keyed.value.code == "P17_BRANCH_KEY_FORBIDDEN"

    deep, _ = _dmp0053_run(
        service,
        session,
        proposal_id="deep-good",
        objective_key="deep.good",
        intent=InvestigationIntent.DEEPEN_EXPLANATION,
        parent_step_id=root.step_id,
    )
    assert deep.branch_id == root.branch_id
    assert deep.depth == root.depth + 1


def test_dmp0053_test_candidate_inherits_branch_and_stopped_candidate_rejects():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="root",
        objective_key="root.gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    alt_a, _ = _dmp0053_run(
        service,
        session,
        proposal_id="alt-a",
        objective_key="alt.a",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id,
        branch_key="a",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    alt_b, _ = _dmp0053_run(
        service,
        session,
        proposal_id="alt-b",
        objective_key="alt.b",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id,
        branch_key="b",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    tested_b, task = _dmp0053_run(
        service,
        session,
        proposal_id="test-b",
        objective_key="test.b",
        intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
        parent_step_id=alt_b.step_id,
        target_kind=InvestigationTargetKind.EXPLANATION,
    )
    assert task is not None
    assert tested_b.branch_id == alt_b.branch_id

    stopped_a, _ = _dmp0053_run(
        service,
        session,
        proposal_id="stop-a",
        objective_key="stop.a",
        intent=InvestigationIntent.STOP_BRANCH,
        parent_step_id=alt_a.step_id,
    )
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert stopped_a.branch_id in snap.investigation.stopped_branch_ids
    assert alt_b.branch_id in snap.investigation.open_branch_ids

    with pytest.raises(ResearchManagerMaturationError) as exc:
        _dmp0053_run(
            service,
            session,
            proposal_id="test-stopped-a",
            objective_key="test.stopped.a",
            intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            parent_step_id=alt_a.step_id,
        )
    assert exc.value.code == "P17_PARENT_STEP_NOT_LEGAL"


def test_dmp0053_stop_branch_requires_open_parent_and_preserves_sibling():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    with pytest.raises(ResearchManagerMaturationError):
        _dmp0053_run(
            service,
            session,
            proposal_id="stop-floating",
            objective_key="stop.floating",
            intent=InvestigationIntent.STOP_BRANCH,
        )

    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="root",
        objective_key="root.gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    a, _ = _dmp0053_run(
        service,
        session,
        proposal_id="a",
        objective_key="a",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id,
        branch_key="a",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    b, _ = _dmp0053_run(
        service,
        session,
        proposal_id="b",
        objective_key="b",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id,
        branch_key="b",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    stopped, _ = _dmp0053_run(
        service,
        session,
        proposal_id="stop-a",
        objective_key="stop.a",
        intent=InvestigationIntent.STOP_BRANCH,
        parent_step_id=a.step_id,
    )
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert stopped.branch_id == a.branch_id
    assert a.branch_id in snap.investigation.stopped_branch_ids
    assert b.branch_id in snap.investigation.open_branch_ids

    with pytest.raises(ResearchManagerMaturationError) as again:
        _dmp0053_run(
            service,
            session,
            proposal_id="stop-a-again",
            objective_key="stop.a.again",
            intent=InvestigationIntent.STOP_BRANCH,
            parent_step_id=a.step_id,
        )
    assert again.value.code == "P17_PARENT_STEP_NOT_LEGAL"


def test_dmp0053_global_stop_and_replan_never_mint_branch():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="root",
        objective_key="root.gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    replanned, _ = _dmp0053_run(
        service,
        session,
        proposal_id="replan",
        objective_key="replan.root",
        intent=InvestigationIntent.REPLAN,
        parent_step_id=root.step_id,
    )
    assert replanned.branch_id == root.branch_id
    assert replanned.depth == root.depth

    stopped, _ = _dmp0053_run(
        service,
        session,
        proposal_id="stop-all",
        objective_key="stop.all",
        intent=InvestigationIntent.STOP_INVESTIGATION,
        parent_step_id=replanned.step_id,
    )
    assert stopped.branch_id == root.branch_id
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert snap.terminal_stop_reason == ManagerStopReason.INCONCLUSIVE
    assert set(snap.investigation.open_branch_ids) == {root.branch_id}


def test_dmp0053_early_global_stop_exposes_no_new_open_branch():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    stopped, _ = _dmp0053_run(
        service,
        session,
        proposal_id="early-stop",
        objective_key="stop.early",
        intent=InvestigationIntent.STOP_INVESTIGATION,
    )
    assert stopped.stop_scope.value == "INVESTIGATION"
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert snap.investigation.open_branch_ids == ()
    assert snap.investigation.stopped_branch_ids == ()


def test_dmp0053_foreign_obligation_parent_is_rejected():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="root",
        objective_key="root.gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    proposal = recursive_proposal(
        snap,
        proposal_id="foreign-obligation",
        objective_key="foreign.obligation",
        intent=InvestigationIntent.DEEPEN_EXPLANATION,
        parent_step_id=root.step_id,
    ).model_copy(update={"target_parent_obligation": "g2"})
    with pytest.raises(ResearchManagerMaturationError) as exc:
        manager_module.resolve_investigation_topology(
            snapshot=snap,
            proposal=proposal,
        )
    assert exc.value.code == "P17_PARENT_STEP_OBLIGATION_MISMATCH"


def test_dmp0053_max_depth_exhaustion_rejects_deeper_parent():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db, max_depth=1)
    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="root",
        objective_key="root.gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    deep, _ = _dmp0053_run(
        service,
        session,
        proposal_id="depth-one",
        objective_key="depth.one",
        intent=InvestigationIntent.DEEPEN_EXPLANATION,
        parent_step_id=root.step_id,
    )
    assert deep.depth == 1
    with pytest.raises(ResearchManagerMaturationError) as exc:
        _dmp0053_run(
            service,
            session,
            proposal_id="depth-two",
            objective_key="depth.two",
            intent=InvestigationIntent.DEEPEN_EXPLANATION,
            parent_step_id=deep.step_id,
        )
    assert exc.value.code == "P17_PARENT_STEP_NOT_LEGAL"


def test_dmp0053_live_red_structure_replay_rejects_floating_alternative():
    """Provider-free structural replay of 36149372671; no business literals."""

    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    parent = None
    for index in range(3):
        step, _ = _dmp0053_run(
            service,
            session,
            proposal_id=f"gap-{index}",
            objective_key=f"gap.{index}",
            intent=InvestigationIntent.INVESTIGATE_GAP,
            parent_step_id=(parent.step_id if parent else None),
        )
        parent = step
    _dmp0053_run(
        service,
        session,
        proposal_id="stop-current",
        objective_key="stop.current",
        intent=InvestigationIntent.STOP_BRANCH,
        parent_step_id=parent.step_id,
    )
    count_before = len(service._ledger.steps(session.session_id))
    with pytest.raises(ResearchManagerMaturationError) as exc:
        _dmp0053_run(
            service,
            session,
            proposal_id="floating-after-stop",
            objective_key="alternative.after.stop",
            intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
            branch_key="new-candidate",
            target_kind=InvestigationTargetKind.ALTERNATIVE,
        )
    assert exc.value.code == "P17_INTENT_NOT_LEGAL_IN_STATE"
    assert len(service._ledger.steps(session.session_id)) == count_before


def test_dmp0053_thin_material_cognition_view_preserves_raw_p15_record():
    db = db_engine()
    store, session, lead, _, _, service = _dmp0053_service(db)
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    view = next(x for x in snap.materials if x.lead_id == lead.lead_id)
    assert view.native_name == "Native channel exploration"
    assert not hasattr(view, "material")
    serialized = snap.model_dump_json()
    assert '"observations"' not in serialized
    assert '"dataset_query"' not in serialized
    assert '"visualization_settings"' not in serialized

    raw = ResearchExplorationStore(db).for_execution_link(
        lead.execution_link_id
    )
    assert raw is not None
    assert raw.material["observations"][0]["orders"] == 34


def test_dmp0053_new_verified_evidence_is_visible_to_later_legal_replan():
    db = db_engine()
    store, session, _, _, claims, _ = setup_state(db)
    followup = LineagedFollowup(db, store)
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup,
        db_engine=db,
    )
    root, _ = _dmp0053_run(
        service,
        session,
        proposal_id="evidence-root",
        objective_key="evidence.root",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    after = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert "evi_" + "2" * 24 in after.evidence_refs
    replanned, _ = _dmp0053_run(
        service,
        session,
        proposal_id="evidence-replan",
        objective_key="evidence.replan",
        intent=InvestigationIntent.REPLAN,
        parent_step_id=root.step_id,
    )
    assert replanned.branch_id == root.branch_id


def test_dmp0053_fake_manager_trajectory_two_alternatives_second_tested():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, _ = _dmp0053_run(
        service, session, proposal_id="r", objective_key="r",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    a, _ = _dmp0053_run(
        service, session, proposal_id="a", objective_key="a",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id, branch_key="a",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    b, _ = _dmp0053_run(
        service, session, proposal_id="b", objective_key="b",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id, branch_key="b",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    tested, _ = _dmp0053_run(
        service, session, proposal_id="tb", objective_key="tb",
        intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
        parent_step_id=b.step_id,
    )
    deep, _ = _dmp0053_run(
        service, session, proposal_id="db", objective_key="db",
        intent=InvestigationIntent.DEEPEN_EXPLANATION,
        parent_step_id=tested.step_id,
    )
    _dmp0053_run(
        service, session, proposal_id="sa", objective_key="sa",
        intent=InvestigationIntent.STOP_BRANCH,
        parent_step_id=a.step_id,
    )
    _dmp0053_run(
        service, session, proposal_id="sg", objective_key="sg",
        intent=InvestigationIntent.STOP_INVESTIGATION,
        parent_step_id=deep.step_id,
    )
    assert tested.branch_id == deep.branch_id == b.branch_id


def test_dmp0053_fake_manager_counter_evidence_retains_sibling_until_stop():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, _ = _dmp0053_run(
        service, session, proposal_id="r", objective_key="r",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    a, _ = _dmp0053_run(
        service, session, proposal_id="a", objective_key="a",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id, branch_key="a",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    b, _ = _dmp0053_run(
        service, session, proposal_id="b", objective_key="b",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        parent_step_id=root.step_id, branch_key="b",
        target_kind=InvestigationTargetKind.ALTERNATIVE,
    )
    counter, _ = _dmp0053_run(
        service, session, proposal_id="counter", objective_key="counter",
        intent=InvestigationIntent.SEEK_COUNTER_EVIDENCE,
        parent_step_id=a.step_id,
    )
    mid = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    assert a.branch_id in mid.investigation.open_branch_ids
    assert b.branch_id in mid.investigation.open_branch_ids
    assert counter.branch_id == a.branch_id
    _dmp0053_run(
        service, session, proposal_id="stop", objective_key="stop",
        intent=InvestigationIntent.STOP_INVESTIGATION,
        parent_step_id=b.step_id,
    )


def test_dmp0053_fake_manager_honest_early_no_gain_stop():
    db = db_engine()
    _, session, _, _, _, service = _dmp0053_service(db)
    root, task = _dmp0053_run(
        service, session, proposal_id="r", objective_key="r",
        intent=InvestigationIntent.INVESTIGATE_GAP,
    )
    assert task is not None
    snap = service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    )
    proposal = ManagerProposal(
        proposal_id="early-no-gain",
        source_revision=snap.source_revision,
        target_parent_obligation="g1",
        action=ManagerAction.STOP,
        intent=InvestigationIntent.STOP_INVESTIGATION,
        parent_step_id=root.step_id,
        target_kind=InvestigationTargetKind.GAP,
        objective_key="stop.no-gain",
        rationale="No material information gain remains.",
        inspected_evidence_refs=snap.evidence_refs,
        inspected_claim_refs=tuple(x.claim_id for x in snap.claims),
        inspected_material_refs=snap.material_refs,
        stop_reason=ManagerStopReason.NO_MEANINGFUL_GAIN,
    )
    stopped, _ = service.run_one(
        session_id=session.session_id,
        principal=principal(),
        manager=ScriptedManager(lambda _: proposal),
    )
    assert stopped.stop_reason == ManagerStopReason.NO_MEANINGFUL_GAIN
    assert service.snapshot(
        session_id=session.session_id,
        principal=principal(),
    ).terminal_stop_reason == ManagerStopReason.NO_MEANINGFUL_GAIN


def test_dmp0053_store_persists_resolved_topology_without_reinterpreting_branch_key():
    source = inspect.getsource(manager_module.ResearchReasoningStore)
    assert "topology_for" not in source
    create = inspect.getsource(
        manager_module.ResearchReasoningStore.create_step
    )
    assert "topology: ResolvedInvestigationTopology" in create
    assert "proposal.branch_key" not in create
