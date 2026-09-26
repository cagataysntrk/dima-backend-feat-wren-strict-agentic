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

from app.v3.research_contracts import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.business_relationship_policy import (
    BusinessRelationshipPolicyStore,
    RelationshipPolicyRequirement,
    RelationshipPolicyResolutionStatus,
)
from app.v3.claim_lineage import (
    ClaimEvidenceRelation,
    ClaimFreshness,
    ClaimLineageStore,
)
from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    CandidateAssessment,
    CausalIdentificationKind,
    CausalIdentificationRef,
    CausalQualification,
    ContributionClass,
    EvidenceStrength,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
    HypothesisEpistemicClass,
    HypothesisRootCauseStore,
    IdentificationLimitation,
    MediationAnnotation,
    NumericAnalyticalKind,
    NumericProvenanceRef,
    P19EpistemicError,
    RootCauseAssessmentDraft,
)
from app.v3.research import EvidenceRef, ObligationState, ResearchManager
from app.v3.research_exploration import ResearchExplorationStore
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.models import (
    BusinessRelationshipPolicyUseRecord,
    HypothesisGroundingLink,
    HypothesisRecord,
    ResearchClaimRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
    ResearchReasoningStepRecord,
    RootCauseAssessment,
    Tenant,
    User,
)


TENANT = UUID("00000000-0000-4000-8000-000000001901")
USER = UUID("00000000-0000-4000-8000-000000001902")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000001911")
OTHER_USER = UUID("00000000-0000-4000-8000-000000001912")
STAMP = datetime(2026, 9, 25, 19, 0, tzinfo=timezone.utc)


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


def principal(
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p19",
) -> Principal:
    return Principal(
        user_id=str(user),
        tenant_id=str(tenant),
        tenant_slug=slug,
        roles=["analyst"],
    )


def brief(*, suffix: str, context: str = "ctx-p19-v1") -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="siparişler",
        candidate_id="native.sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    question = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.PERFORMANCE,
        source_text="Kanal farkının açıklamalarını epistemik olarak değerlendir.",
        subject_refs=(metric,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id=f"rb-p19-{suffix}",
        objective=question.source_text,
        scope=ResearchScope(semantic_refs=(metric,)),
        questions=(question,),
        must_requirement_ids=("g1",),
        context_version=context,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def ensure_identity_rows(
    db,
    *,
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p19",
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


def make_state(
    db,
    *,
    suffix: str = "base",
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p19",
    context: str = "ctx-p19-v1",
):
    SQLModel.metadata.create_all(db)
    ensure_identity_rows(db, tenant=tenant, user=user, slug=slug)
    p = principal(tenant, user, slug)
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=brief(suffix=suffix, context=context),
        request_ref=f"p19-{suffix}",
        source_message_hash=hashlib.sha256(
            f"p19-{suffix}".encode()
        ).hexdigest(),
        principal=p,
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
        native_query_id=f"p19-{suffix}-query",
        native_query=query,
        query_fingerprint=h(query),
    )
    store.mark_execution_started(
        link.id,
        native_subject_ref="metabase-user:19",
    )
    result = {
        "database_id": 1,
        "row_count": 2,
        "data": {"rows": [["Web", 34], ["Partner", 12]]},
        "statistics": {
            "association": 0.72,
        },
        "decomposition": {
            "kind": "DIRECT_INDIRECT_DECOMPOSITION",
            "direct_effect": 0.31,
            "indirect_effect": 0.14,
        },
        "identification": {
            "kind": "NATIVE_CAUSAL_IDENTIFICATION",
        },
    }
    store.mark_executed(
        link.id,
        native_subject_ref="metabase-user:19",
        runtime_identity={
            "substrate": "metabase-native",
            "runtime_version": "v0.63.18-dima.6",
            "image_digest": "sha256:" + "c" * 64,
            "database_id": "metabase:1",
        },
        result_payload=result,
        result_hash=h(result),
        executed_at=STAMP,
    )
    evidence_id = "evi_" + h({"suffix": suffix, "kind": "evidence"})[:24]
    receipt_id = "dqr_" + h({"suffix": suffix, "kind": "receipt"})[:24]
    link = store.mark_verified(
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
        now=STAMP + timedelta(minutes=1),
    )
    session = store.save(
        session,
        expected_revision=session.revision - 1,
    )
    link = store.execution_link(link.id)

    material = ResearchExplorationStore(db).persist(
        session_id=session.session_id,
        obligation_id="g1",
        execution_link_id=link.id,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        query_fingerprint=link.native_query_fingerprint,
        source_evidence_refs=(evidence_id,),
        material={
            "name": "P19 native material",
            "observations": [{"channel": "Web", "orders": 34}],
            "statistics": {"association": 0.72},
        },
        now=STAMP + timedelta(minutes=2),
    )

    claims = ClaimLineageStore(
        research_store=store,
        db_engine=db,
    )
    claim = claims.create_claim(
        session_id=session.session_id,
        obligation_id="g1",
        principal=p,
        claim_text="Web kanalı gözlenen kapsamda daha yüksek sipariş sayısına sahip.",
        proposition={
            "subject": "channel:Web",
            "predicate": "has_higher_order_count_than",
            "object": "channel:Partner",
        },
        scope={"period": "2026-06", "population": "sales_orders"},
        freshness=ClaimFreshness(
            as_of=STAMP,
            stale_after=STAMP + timedelta(days=30),
        ),
        origin_material_refs=(material.lead_id,),
    )
    claim = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id=evidence_id,
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=p,
    )

    step_id = "rrs_" + h(
        {"session": session.session_id, "suffix": suffix}
    )[:24]
    with Session(db) as s:
        s.add(
            ResearchReasoningStepRecord(
                step_id=step_id,
                session_id=session.session_id,
                source_revision=session.revision,
                source_snapshot_fingerprint=session.fingerprint,
                parent_obligation_id="g1",
                parent_step_id=None,
                depth=0,
                branch_id="ibr_" + h(step_id)[:20],
                intent="STOP_INVESTIGATION",
                target_kind="GAP",
                target_ref=None,
                stop_scope="INVESTIGATION",
                proposal_id=f"proposal-{suffix}",
                proposal_json=json.dumps(
                    {"kind": "provider-free-p19-fixture"},
                    sort_keys=True,
                ),
                action="STOP",
                objective_key=f"p19.{suffix}",
                bounded_objective=None,
                rationale="Sealed provider-free P17 fixture.",
                inspected_evidence_refs_json=json.dumps([evidence_id]),
                inspected_claim_refs_json=json.dumps([claim.claim_id]),
                inspected_material_refs_json=json.dumps([material.lead_id]),
                proposal_fingerprint=h(
                    {"step": step_id, "claim": claim.claim_id}
                ),
                status="STOPPED",
                stop_reason="INCONCLUSIVE",
                result_refs_json="[]",
                created_at=STAMP + timedelta(minutes=3),
                completed_at=STAMP + timedelta(minutes=3),
            )
        )
        s.commit()

    p18 = BusinessRelationshipPolicyStore(
        research_store=store,
        db_engine=db,
    )
    scope = {"period": "2026-06", "population": "sales_orders"}
    policy = p18.create_policy(
        principal=p,
        semantic_context_version=session.context_version,
        policy_key="sales-order-customer-attribution",
        source_business_ref="business:sales-order",
        target_business_ref="business:customer",
        business_relationship_statement=(
            "Sales orders may be attributed to governed customer identity."
        ),
        applicability_scope=scope,
        provenance_ref=f"policy-manual:{suffix}",
        now=STAMP + timedelta(minutes=4),
    )
    satisfied = p18.resolve(
        requirement=RelationshipPolicyRequirement(
            research_session_id=session.session_id,
            obligation_id="g1",
            claim_id=claim.claim_id,
            reasoning_step_id=step_id,
            policy_key=policy.policy_key,
            source_business_ref=policy.source_business_ref,
            target_business_ref=policy.target_business_ref,
            semantic_context_version=session.context_version,
            applicability_scope=scope,
            required=True,
        ),
        principal=p,
        now=STAMP + timedelta(minutes=5),
    )
    assert (
        satisfied.resolution_status
        == RelationshipPolicyResolutionStatus.SATISFIED
    )

    blocked = p18.resolve(
        requirement=RelationshipPolicyRequirement(
            research_session_id=session.session_id,
            obligation_id="g1",
            claim_id=claim.claim_id,
            reasoning_step_id=step_id,
            policy_key="missing-required-policy",
            source_business_ref="business:customer",
            target_business_ref="business:margin",
            semantic_context_version=session.context_version,
            applicability_scope=scope,
            required=True,
        ),
        principal=p,
        now=STAMP + timedelta(minutes=6),
    )
    assert (
        blocked.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_MISSING
    )

    p19 = HypothesisRootCauseStore(
        research_store=store,
        db_engine=db,
    )
    return {
        "principal": p,
        "store": store,
        "session": session,
        "link": link,
        "evidence_id": evidence_id,
        "receipt_id": receipt_id,
        "material": material,
        "claims": claims,
        "claim": claim,
        "step_id": step_id,
        "p18": p18,
        "policy": policy,
        "p18_satisfied": satisfied,
        "p18_blocked": blocked,
        "p19": p19,
    }


def make_hypotheses(state):
    a = state["p19"].create_hypothesis(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        statement="Kanal karışımı gözlenen sipariş farkını açıklıyor olabilir.",
        principal=state["principal"],
        now=STAMP + timedelta(minutes=10),
    )
    b = state["p19"].create_hypothesis(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        statement="Müşteri kompozisyonu gözlenen sipariş farkını açıklıyor olabilir.",
        principal=state["principal"],
        now=STAMP + timedelta(minutes=11),
    )
    return a, b


def grounding(
    state,
    hypothesis,
    *,
    kind,
    ref,
    relation,
    receipt=None,
    minute=12,
):
    return state["p19"].create_grounding(
        hypothesis_id=hypothesis.hypothesis_id,
        source_kind=kind,
        source_ref=ref,
        source_receipt_id=receipt,
        relation=relation,
        principal=state["principal"],
        now=STAMP + timedelta(minutes=minute),
    )


def standard_groundings(state, a, b, *, blocked_policy=False):
    a_evidence = grounding(
        state,
        a,
        kind=GroundingSourceKind.P14_EVIDENCE,
        ref=state["evidence_id"],
        receipt=state["receipt_id"],
        relation=GroundingRelation.SUPPORTS,
        minute=12,
    )
    a_policy = grounding(
        state,
        a,
        kind=GroundingSourceKind.P18_POLICY_USE,
        ref=(
            state["p18_blocked"].policy_use_id
            if blocked_policy
            else state["p18_satisfied"].policy_use_id
        ),
        relation=GroundingRelation.CONTEXT,
        minute=13,
    )
    b_material = grounding(
        state,
        b,
        kind=GroundingSourceKind.P15_MATERIAL,
        ref=state["material"].lead_id,
        relation=GroundingRelation.SUPPORTS,
        minute=14,
    )
    b_challenge = grounding(
        state,
        b,
        kind=GroundingSourceKind.P16_CLAIM,
        ref=state["claim"].claim_id,
        relation=GroundingRelation.CHALLENGES,
        minute=15,
    )
    return a_evidence, a_policy, b_material, b_challenge


def candidate(
    hypothesis,
    links,
    *,
    disposition=HypothesisDisposition.RETAINED,
    epistemic=HypothesisEpistemicClass.CONTRIBUTION,
    contribution=ContributionClass.MATERIAL,
    evidence=EvidenceStrength.MODERATE,
    causal=CausalQualification.NOT_CLAIMED,
    relationship_dependent=False,
    policy_use_id=None,
    limitations=(),
    numeric=(),
    causal_refs=(),
):
    return CandidateAssessment(
        hypothesis_id=hypothesis.hypothesis_id,
        grounding_link_ids=tuple(x.grounding_link_id for x in links),
        disposition=disposition,
        epistemic_class=epistemic,
        contribution_class=contribution,
        evidence_strength=evidence,
        causal_qualification=causal,
        relationship_dependent=relationship_dependent,
        relationship_policy_use_id=policy_use_id,
        identification_limitations=limitations,
        numeric_provenance=numeric,
        causal_identification_refs=causal_refs,
    )


def test_p19_hypothesis_identity_is_exact_canonical_and_idempotent():
    db = db_engine()
    state = make_state(db)
    first, _ = make_hypotheses(state)
    second = state["p19"].create_hypothesis(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        statement=first.statement,
        principal=state["principal"],
    )
    assert first == second
    assert first.hypothesis_id == "p19h_" + first.identity_fingerprint[:24]


def test_p19_has_exactly_three_durable_record_types():
    tables = {
        table.name
        for table in SQLModel.metadata.tables.values()
        if table.name.startswith("p19_")
    }
    assert tables == {
        "p19_hypothesis",
        "p19_hypothesis_grounding",
        "p19_root_cause_assessment",
    }


@pytest.mark.parametrize(
    ("kind", "ref", "receipt", "code"),
    [
        (
            GroundingSourceKind.P14_EVIDENCE,
            "evi_" + "f" * 24,
            "dqr_" + "f" * 24,
            "P19_EVIDENCE_SOURCE_NOT_FOUND",
        ),
        (
            GroundingSourceKind.P15_MATERIAL,
            "rxm_" + "f" * 24,
            None,
            "P19_MATERIAL_SOURCE_NOT_FOUND",
        ),
        (
            GroundingSourceKind.P16_CLAIM,
            "clm_" + "f" * 24,
            None,
            "P19_CLAIM_SOURCE_NOT_FOUND",
        ),
        (
            GroundingSourceKind.P17_REASONING_STEP,
            "rrs_" + "f" * 24,
            None,
            "P19_REASONING_SOURCE_NOT_FOUND",
        ),
        (
            GroundingSourceKind.P18_POLICY_USE,
            "bru_" + "f" * 24,
            None,
            "P19_POLICY_USE_SOURCE_NOT_FOUND",
        ),
    ],
)
def test_unknown_source_refs_are_rejected(kind, ref, receipt, code):
    db = db_engine()
    state = make_state(db)
    a, _ = make_hypotheses(state)
    with pytest.raises(P19EpistemicError) as exc:
        grounding(
            state,
            a,
            kind=kind,
            ref=ref,
            receipt=receipt,
            relation=GroundingRelation.CONTEXT,
        )
    assert exc.value.code == code


def test_foreign_session_source_refs_are_rejected():
    db = db_engine()
    state = make_state(db, suffix="a")
    other = make_state(
        db,
        suffix="b",
        tenant=OTHER_TENANT,
        user=OTHER_USER,
        slug="p19-other",
    )
    a, _ = make_hypotheses(state)

    with pytest.raises(P19EpistemicError) as evidence:
        grounding(
            state,
            a,
            kind=GroundingSourceKind.P14_EVIDENCE,
            ref=other["evidence_id"],
            receipt=other["receipt_id"],
            relation=GroundingRelation.CONTEXT,
        )
    assert evidence.value.code == "P19_EVIDENCE_SOURCE_NOT_FOUND"

    with pytest.raises(P19EpistemicError) as claim:
        grounding(
            state,
            a,
            kind=GroundingSourceKind.P16_CLAIM,
            ref=other["claim"].claim_id,
            relation=GroundingRelation.CONTEXT,
        )
    assert claim.value.code == "P19_CLAIM_SOURCE_SCOPE_MISMATCH"

    with pytest.raises(P19EpistemicError) as policy:
        grounding(
            state,
            a,
            kind=GroundingSourceKind.P18_POLICY_USE,
            ref=other["p18_satisfied"].policy_use_id,
            relation=GroundingRelation.CONTEXT,
        )
    assert policy.value.code == "P19_POLICY_USE_SOURCE_SCOPE_MISMATCH"


def test_support_and_challenge_coexist_without_overwrite():
    db = db_engine()
    state = make_state(db)
    a, _ = make_hypotheses(state)
    support = grounding(
        state,
        a,
        kind=GroundingSourceKind.P14_EVIDENCE,
        ref=state["evidence_id"],
        receipt=state["receipt_id"],
        relation=GroundingRelation.SUPPORTS,
    )
    challenge = grounding(
        state,
        a,
        kind=GroundingSourceKind.P16_CLAIM,
        ref=state["claim"].claim_id,
        relation=GroundingRelation.CHALLENGES,
        minute=13,
    )
    snap = state["p19"].snapshot(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        principal=state["principal"],
    )
    links = next(
        x.groundings
        for x in snap.hypotheses
        if x.hypothesis.hypothesis_id == a.hypothesis_id
    )
    assert {x.grounding_link_id for x in links} == {
        support.grounding_link_id,
        challenge.grounding_link_id,
    }
    assert {x.relation for x in links} == {
        GroundingRelation.SUPPORTS,
        GroundingRelation.CHALLENGES,
    }


def test_two_hypotheses_can_remain_retained_and_material():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    draft = RootCauseAssessmentDraft(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        candidates=(
            candidate(a, (ae, ap)),
            candidate(b, (bm, bc)),
        ),
        aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
    )
    assessment = state["p19"].assess(
        draft=draft,
        principal=state["principal"],
    )
    assert (
        assessment.aggregate_outcome
        == AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS
    )
    assert all(
        item.disposition == HypothesisDisposition.RETAINED
        for item in assessment.candidates
    )
    assert all(
        item.contribution_class == ContributionClass.MATERIAL
        for item in assessment.candidates
    )


def test_correlation_only_source_cannot_be_promoted_to_root_cause():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    draft = RootCauseAssessmentDraft(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        candidates=(
            candidate(
                a,
                (ae, ap),
                epistemic=HypothesisEpistemicClass.CANDIDATE_CAUSE,
                evidence=EvidenceStrength.STRONG,
                causal=CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION,
                relationship_dependent=True,
                policy_use_id=state["p18_satisfied"].policy_use_id,
            ),
            candidate(
                b,
                (bm, bc),
                disposition=HypothesisDisposition.WEAKENED,
                epistemic=HypothesisEpistemicClass.COMPETING_HYPOTHESIS,
                contribution=ContributionClass.LOW,
                evidence=EvidenceStrength.WEAK,
            ),
        ),
        aggregate_outcome=AggregateOutcome.ROOT_CAUSE_ESTABLISHED,
        root_cause_hypothesis_ids=(a.hypothesis_id,),
    )
    with pytest.raises(P19EpistemicError) as exc:
        state["p19"].assess(
            draft=draft,
            principal=state["principal"],
        )
    assert exc.value.code == "P19_CAUSAL_PROMOTION_GATE_FAILED"


def test_exact_native_causal_identification_can_pass_root_gate():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    causal_ref = CausalIdentificationRef(
        source_kind=GroundingSourceKind.P14_EVIDENCE,
        source_ref=state["evidence_id"],
        source_receipt_id=state["receipt_id"],
        source_path="identification.kind",
        identification_kind=CausalIdentificationKind.NATIVE_CAUSAL_IDENTIFICATION,
    )
    assessment = state["p19"].assess(
        draft=RootCauseAssessmentDraft(
            research_session_id=state["session"].session_id,
            obligation_id="g1",
            candidates=(
                candidate(
                    a,
                    (ae, ap),
                    epistemic=HypothesisEpistemicClass.CANDIDATE_CAUSE,
                    contribution=ContributionClass.MATERIAL,
                    evidence=EvidenceStrength.STRONG,
                    causal=CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION,
                    relationship_dependent=True,
                    policy_use_id=state["p18_satisfied"].policy_use_id,
                    causal_refs=(causal_ref,),
                ),
                candidate(
                    b,
                    (bm, bc),
                    disposition=HypothesisDisposition.WEAKENED,
                    epistemic=HypothesisEpistemicClass.COMPETING_HYPOTHESIS,
                    contribution=ContributionClass.LOW,
                    evidence=EvidenceStrength.WEAK,
                ),
            ),
            aggregate_outcome=AggregateOutcome.ROOT_CAUSE_ESTABLISHED,
            root_cause_hypothesis_ids=(a.hypothesis_id,),
        ),
        principal=state["principal"],
    )
    assert assessment.aggregate_outcome == AggregateOutcome.ROOT_CAUSE_ESTABLISHED
    assert assessment.root_cause_hypothesis_ids == (a.hypothesis_id,)


def test_blocked_p18_policy_blocks_relationship_dependent_cause():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, blocked, bm, bc = standard_groundings(
        state,
        a,
        b,
        blocked_policy=True,
    )
    causal_ref = CausalIdentificationRef(
        source_kind=GroundingSourceKind.P14_EVIDENCE,
        source_ref=state["evidence_id"],
        source_receipt_id=state["receipt_id"],
        source_path="identification.kind",
        identification_kind=CausalIdentificationKind.NATIVE_CAUSAL_IDENTIFICATION,
    )
    draft = RootCauseAssessmentDraft(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        candidates=(
            candidate(
                a,
                (ae, blocked),
                epistemic=HypothesisEpistemicClass.CANDIDATE_CAUSE,
                evidence=EvidenceStrength.STRONG,
                causal=CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION,
                relationship_dependent=True,
                policy_use_id=state["p18_blocked"].policy_use_id,
                causal_refs=(causal_ref,),
            ),
            candidate(
                b,
                (bm, bc),
                disposition=HypothesisDisposition.WEAKENED,
                epistemic=HypothesisEpistemicClass.COMPETING_HYPOTHESIS,
                contribution=ContributionClass.LOW,
            ),
        ),
        aggregate_outcome=AggregateOutcome.ROOT_CAUSE_ESTABLISHED,
        root_cause_hypothesis_ids=(a.hypothesis_id,),
    )
    with pytest.raises(P19EpistemicError) as exc:
        state["p19"].assess(draft=draft, principal=state["principal"])
    assert exc.value.code == "P19_P18_POLICY_BLOCKS_CAUSAL_PROMOTION"


def test_p18_satisfied_does_not_itself_prove_causation():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    draft = RootCauseAssessmentDraft(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        candidates=(
            candidate(
                a,
                (ae, ap),
                epistemic=HypothesisEpistemicClass.CANDIDATE_CAUSE,
                evidence=EvidenceStrength.STRONG,
                causal=CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION,
                relationship_dependent=True,
                policy_use_id=state["p18_satisfied"].policy_use_id,
            ),
            candidate(
                b,
                (bm, bc),
                disposition=HypothesisDisposition.WEAKENED,
                epistemic=HypothesisEpistemicClass.COMPETING_HYPOTHESIS,
                contribution=ContributionClass.LOW,
            ),
        ),
        aggregate_outcome=AggregateOutcome.ROOT_CAUSE_ESTABLISHED,
        root_cause_hypothesis_ids=(a.hypothesis_id,),
    )
    with pytest.raises(P19EpistemicError) as exc:
        state["p19"].assess(draft=draft, principal=state["principal"])
    assert exc.value.code == "P19_CAUSAL_PROMOTION_GATE_FAILED"


def test_no_defensible_root_cause_is_legal_terminal_success():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    assessment = state["p19"].assess(
        draft=RootCauseAssessmentDraft(
            research_session_id=state["session"].session_id,
            obligation_id="g1",
            candidates=(
                candidate(
                    a,
                    (ae, ap),
                    contribution=ContributionClass.UNKNOWN,
                    evidence=EvidenceStrength.WEAK,
                    causal=CausalQualification.IDENTIFICATION_LIMITED,
                    limitations=(IdentificationLimitation.ASSOCIATION_ONLY,),
                ),
                candidate(
                    b,
                    (bm, bc),
                    contribution=ContributionClass.UNKNOWN,
                    evidence=EvidenceStrength.INSUFFICIENT,
                    causal=CausalQualification.IDENTIFICATION_LIMITED,
                    limitations=(
                        IdentificationLimitation.CONFOUNDING_NOT_RESOLVED,
                    ),
                ),
            ),
            aggregate_outcome=(
                AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
            ),
            limitations=("Causal identification is insufficient.",),
        ),
        principal=state["principal"],
    )
    assert (
        assessment.aggregate_outcome
        == AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
    )


def test_fake_numeric_confidence_is_rejected_by_typed_contract():
    with pytest.raises(ValidationError):
        CandidateAssessment.model_validate(
            {
                "hypothesis_id": "p19h_" + "a" * 24,
                "grounding_link_ids": ("p19g_" + "b" * 24,),
                "disposition": "RETAINED",
                "epistemic_class": "ASSOCIATION",
                "contribution_class": "UNKNOWN",
                "evidence_strength": "WEAK",
                "causal_qualification": "NOT_CLAIMED",
                "confidence_percent": 83,
            }
        )


def test_native_numeric_provenance_is_referenced_without_recomputation():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    numeric = NumericProvenanceRef(
        source_kind=GroundingSourceKind.P15_MATERIAL,
        source_ref=state["material"].lead_id,
        source_path="observations.0.orders",
        analytical_kind=NumericAnalyticalKind.NATIVE_NUMERIC_RESULT,
    )
    assessment = state["p19"].assess(
        draft=RootCauseAssessmentDraft(
            research_session_id=state["session"].session_id,
            obligation_id="g1",
            candidates=(
                candidate(a, (ae, ap)),
                candidate(b, (bm, bc), numeric=(numeric,)),
            ),
            aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
        ),
        principal=state["principal"],
    )
    b_view = next(
        x for x in assessment.candidates if x.hypothesis_id == b.hypothesis_id
    )
    assert b_view.numeric_provenance == (numeric,)
    assert not hasattr(numeric, "value")


def test_numeric_provenance_must_be_part_of_selected_grounding():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    numeric = NumericProvenanceRef(
        source_kind=GroundingSourceKind.P15_MATERIAL,
        source_ref=state["material"].lead_id,
        source_path="observations.0.orders",
        analytical_kind=NumericAnalyticalKind.NATIVE_NUMERIC_RESULT,
    )
    draft = RootCauseAssessmentDraft(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        candidates=(
            candidate(a, (ae, ap), numeric=(numeric,)),
            candidate(b, (bm, bc)),
        ),
        aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
    )
    with pytest.raises(P19EpistemicError) as exc:
        state["p19"].assess(draft=draft, principal=state["principal"])
    assert exc.value.code == "P19_PROVENANCE_GROUNDING_REQUIRED"


def test_mediation_without_direct_indirect_decomposition_rejects_double_count():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    draft = RootCauseAssessmentDraft(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        candidates=(
            candidate(a, (ae, ap)),
            candidate(b, (bm, bc)),
        ),
        aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
        mediation_annotations=(
            MediationAnnotation(
                ordered_hypothesis_ids=(a.hypothesis_id, b.hypothesis_id),
                outcome_scope="sales_orders",
                source_grounding_link_ids=(
                    ae.grounding_link_id,
                    bm.grounding_link_id,
                ),
            ),
        ),
    )
    with pytest.raises(P19EpistemicError) as exc:
        state["p19"].assess(draft=draft, principal=state["principal"])
    assert exc.value.code == "P19_MEDIATION_DOUBLE_COUNT_UNSAFE"


def test_native_direct_indirect_decomposition_can_remove_double_count_block():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    decomposition = NumericProvenanceRef(
        source_kind=GroundingSourceKind.P14_EVIDENCE,
        source_ref=state["evidence_id"],
        source_receipt_id=state["receipt_id"],
        source_path="decomposition.direct_effect",
        analytical_kind=NumericAnalyticalKind.DIRECT_INDIRECT_DECOMPOSITION,
        analytical_kind_path="decomposition.kind",
    )
    assessment = state["p19"].assess(
        draft=RootCauseAssessmentDraft(
            research_session_id=state["session"].session_id,
            obligation_id="g1",
            candidates=(
                candidate(a, (ae, ap), numeric=(decomposition,)),
                candidate(b, (bm, bc)),
            ),
            aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
            mediation_annotations=(
                MediationAnnotation(
                    ordered_hypothesis_ids=(a.hypothesis_id, b.hypothesis_id),
                    outcome_scope="sales_orders",
                    source_grounding_link_ids=(
                        ae.grounding_link_id,
                        bm.grounding_link_id,
                    ),
                    identification_limitation=None,
                ),
            ),
        ),
        principal=state["principal"],
    )
    assert (
        assessment.aggregate_outcome
        == AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS
    )


def test_exact_assessment_is_restart_idempotent():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    draft = RootCauseAssessmentDraft(
        research_session_id=state["session"].session_id,
        obligation_id="g1",
        candidates=(
            candidate(a, (ae, ap)),
            candidate(b, (bm, bc)),
        ),
        aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
    )
    first = state["p19"].assess(draft=draft, principal=state["principal"])
    restarted = HypothesisRootCauseStore(
        research_store=state["store"],
        db_engine=db,
    )
    second = restarted.assess(draft=draft, principal=state["principal"])
    assert first == second
    with Session(db) as s:
        rows = s.exec(select(RootCauseAssessment)).all()
    assert len(rows) == 1


def test_old_assessment_remains_immutable_after_new_grounding():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)
    first = state["p19"].assess(
        draft=RootCauseAssessmentDraft(
            research_session_id=state["session"].session_id,
            obligation_id="g1",
            candidates=(
                candidate(a, (ae, ap)),
                candidate(b, (bm, bc)),
            ),
            aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
        ),
        principal=state["principal"],
    )
    extra = grounding(
        state,
        b,
        kind=GroundingSourceKind.P17_REASONING_STEP,
        ref=state["step_id"],
        relation=GroundingRelation.CONTEXT,
        minute=20,
    )
    second = state["p19"].assess(
        draft=RootCauseAssessmentDraft(
            research_session_id=state["session"].session_id,
            obligation_id="g1",
            candidates=(
                candidate(a, (ae, ap)),
                candidate(b, (bm, bc, extra)),
            ),
            aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
        ),
        principal=state["principal"],
    )
    historical = state["p19"].load_assessment(
        assessment_id=first.assessment_id,
        principal=state["principal"],
    )
    assert first.assessment_id != second.assessment_id
    assert historical == first
    old_b = next(
        x for x in historical.candidates if x.hypothesis_id == b.hypothesis_id
    )
    assert extra.grounding_link_id not in old_b.grounding_link_ids


def test_p14_to_p18_sealed_authorities_are_read_only_inputs():
    db = db_engine()
    state = make_state(db)
    a, b = make_hypotheses(state)
    ae, ap, bm, bc = standard_groundings(state, a, b)

    before_session = state["store"].load(
        state["session"].session_id,
        tenant=state["session"].tenant_binding,
        principal=state["session"].principal_subject,
    )
    before_claim = state["claims"].load_claim(
        session_id=state["session"].session_id,
        claim_id=state["claim"].claim_id,
        principal=state["principal"],
    )
    with Session(db) as s:
        before_step = s.get(ResearchReasoningStepRecord, state["step_id"])
        before_use = s.get(
            BusinessRelationshipPolicyUseRecord,
            state["p18_satisfied"].policy_use_id,
        )
        before_material = s.get(
            ResearchExplorationMaterial,
            state["material"].lead_id,
        )
        assert before_step and before_use and before_material
        step_payload = before_step.model_dump()
        use_payload = before_use.model_dump()
        material_payload = before_material.model_dump()

    state["p19"].assess(
        draft=RootCauseAssessmentDraft(
            research_session_id=state["session"].session_id,
            obligation_id="g1",
            candidates=(
                candidate(a, (ae, ap)),
                candidate(b, (bm, bc)),
            ),
            aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
        ),
        principal=state["principal"],
    )

    after_session = state["store"].load(
        state["session"].session_id,
        tenant=state["session"].tenant_binding,
        principal=state["session"].principal_subject,
    )
    after_claim = state["claims"].load_claim(
        session_id=state["session"].session_id,
        claim_id=state["claim"].claim_id,
        principal=state["principal"],
    )
    with Session(db) as s:
        after_step = s.get(ResearchReasoningStepRecord, state["step_id"])
        after_use = s.get(
            BusinessRelationshipPolicyUseRecord,
            state["p18_satisfied"].policy_use_id,
        )
        after_material = s.get(
            ResearchExplorationMaterial,
            state["material"].lead_id,
        )
    assert after_session.fingerprint == before_session.fingerprint
    assert after_claim == before_claim
    assert after_step.model_dump() == step_payload
    assert after_use.model_dump() == use_payload
    assert after_material.model_dump() == material_payload


def test_p19_production_owner_has_zero_analytical_executor_or_duplicate_authority():
    path = Path("app/v3/hypothesis_root_cause.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")

    forbidden_imports = (
        "app.v3.substrate.metabase",
        "app.v3.research_native_gateway",
        "app.v3.research_followup",
        "app.v3.native_execution",
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
    for forbidden in (
        "NativeEngineBridge",
        "MetabaseAgentClient",
        "execute_dataset",
        "explore_adhoc",
        "attest_native_query",
        "execute_native_query",
        "wren_service",
        "InvestigationGraph",
        "ResearchManager.add_hypothesis",
        "HypothesisState",
        "DimaQueryReceipt(",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
    ):
        assert forbidden not in source


def test_p19_records_reference_lower_truth_without_copying_it():
    hypothesis_fields = set(HypothesisRecord.model_fields)
    grounding_fields = set(HypothesisGroundingLink.model_fields)
    assessment_fields = set(RootCauseAssessment.model_fields)
    forbidden = {
        "claim_text",
        "evidence_payload",
        "native_material",
        "p17_topology",
        "policy_statement",
        "query_json",
        "sql",
        "mbql",
        "confidence_percent",
        "causal_probability",
    }
    assert forbidden.isdisjoint(
        hypothesis_fields | grounding_fields | assessment_fields
    )
