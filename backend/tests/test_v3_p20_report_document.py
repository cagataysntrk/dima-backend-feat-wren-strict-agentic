from __future__ import annotations
import ast
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select
from app.v3.research_contracts import RankingSurface, ResearchBrief, ResearchBriefStatus, ResearchGoalKind, ResearchGoalStatus, ResearchQuestion, ResearchScope, ResearchSemanticRef, SemanticTargetKind
from app.v3.business_relationship_policy import BusinessRelationshipPolicyStore, RelationshipPolicyRequirement
from app.v3.business_relationship_v1 import project_relationship_result
from app.v3.claim_lineage import ClaimEvidenceRelation, ClaimFreshness, ClaimLineageStore
from app.v3.hypothesis_root_cause import AggregateOutcome, CandidateAssessment, CausalQualification, ContributionClass, EvidenceStrength, GroundingRelation, GroundingSourceKind, HypothesisDisposition, HypothesisEpistemicClass, HypothesisRootCauseStore, IdentificationLimitation, NumericAnalyticalKind, NumericProvenanceRef, RootCauseAssessmentDraft
from app.v3.report_document import CoverageEntry, CoverageStatus, P20ReportError, ReportCurrentness, ReportDocumentStore, ReportDraft, ReportLimitation, ReportSourceKind, ReportStatement, ReportStatementKind, SourceReference, stable_limitation_id, stable_statement_id
from app.v3.research import EvidenceRef, ObligationState, ResearchManager
from app.v3.research_exploration import ResearchExplorationStore
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.models import BusinessRelationshipPolicyUseRecord, ClaimEvidenceLinkRecord, HypothesisGroundingLink, HypothesisRecord, ReportDocumentRecord, ResearchClaimRecord, ResearchExecutionLink, ResearchExplorationMaterial, ResearchReasoningStepRecord, RootCauseAssessment, Tenant, User
TENANT = UUID('00000000-0000-4000-8000-000000002001')
USER = UUID('00000000-0000-4000-8000-000000002002')
STAMP = datetime(2026, 9, 25, 21, 0, tzinfo=timezone.utc)

def h(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()

def db_engine():
    return create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)

def principal() -> Principal:
    return Principal(user_id=str(USER), tenant_id=str(TENANT), tenant_slug='p20', roles=['analyst'])

def brief(suffix: str='base') -> ResearchBrief:
    metric = ResearchSemanticRef(source_mention='siparişler', candidate_id='native.sales_order_count', target_kind=SemanticTargetKind.METRIC, canonical_name='Sales Order Count', cube_names=('satis_siparisleri',))
    question = ResearchQuestion(goal_id='g1', kind=ResearchGoalKind.PERFORMANCE, source_text='Kanal farkını yönetişimli biçimde raporla.', subject_refs=(metric,), status=ResearchGoalStatus.RESOLVED)
    return ResearchBrief(brief_id=f'rb-p20-{suffix}', objective=question.source_text, scope=ResearchScope(semantic_refs=(metric,)), questions=(question,), must_requirement_ids=('g1',), context_version='ctx-p20-v1', status=ResearchBriefStatus.READY_FOR_RESEARCH)

def make_state(db, suffix: str='base'):
    SQLModel.metadata.create_all(db)
    with Session(db) as s:
        s.add(Tenant(id=TENANT, slug='p20', name='P20', created_at=STAMP))
        s.add(User(id=USER, tenant_id=TENANT, email='p20@example.test', password_hash='unused', created_at=STAMP))
        s.commit()
    p = principal()
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(brief=brief(suffix), request_ref=f'p20-{suffix}', source_message_hash=hashlib.sha256(f'p20-{suffix}'.encode()).hexdigest(), principal=p)
    prepared = ResearchManager.prepare_native_delegation(session, obligation_id='g1')
    session = store.save(prepared.session, expected_revision=session.revision)
    link = store.begin_delegation(session=session, obligation_id='g1', dima_request_id=prepared.request.dima_request_id, dima_trace_id=prepared.request.dima_trace_id, native_conversation_id=prepared.request.conversation_id)
    query = {'database': 1, 'type': 'query', 'query': {'source-table': 10, 'aggregation': [['count']], 'breakout': [['field', 20, None]]}}
    link = store.mark_candidate(link.id, native_query_id=f'p20-{suffix}-query', native_query=query, query_fingerprint=h(query))
    store.mark_execution_started(link.id, native_subject_ref='metabase-user:20')
    result = {'database_id': 1, 'row_count': 2, 'data': {'rows': [['Web', 34], ['Partner', 12]]}, 'statistics': {'association': 0.72}, 'identification': {'kind': 'NATIVE_CAUSAL_IDENTIFICATION'}}
    store.mark_executed(link.id, native_subject_ref='metabase-user:20', runtime_identity={'substrate': 'metabase-native', 'runtime_version': 'v0.63.18-dima.6', 'image_digest': 'sha256:' + 'd' * 64, 'database_id': 'metabase:1'}, result_payload=result, result_hash=h(result), executed_at=STAMP)
    evidence_id = 'evi_' + h({'suffix': suffix, 'kind': 'evidence'})[:24]
    receipt_id = 'dqr_' + h({'suffix': suffix, 'kind': 'receipt'})[:24]
    link = store.mark_verified(link.id, receipt_id=receipt_id, evidence_id=evidence_id)
    item = ResearchManager.obligation(session, 'g1').model_copy(update={'state': ObligationState.VERIFIED, 'evidence_refs': (evidence_id,)})
    session = ResearchManager.advance(session, obligations=ResearchManager.replace(session, item), evidence_refs=(EvidenceRef(evidence_id=evidence_id, receipt_id=receipt_id, authority_id=session.authority_id, obligation_id='g1'),), now=STAMP + timedelta(minutes=1))
    session = store.save(session, expected_revision=session.revision - 1)
    link = store.execution_link(link.id)
    material = ResearchExplorationStore(db).persist(session_id=session.session_id, obligation_id='g1', execution_link_id=link.id, native_conversation_id=link.native_conversation_id, native_query_id=link.native_query_id, query_fingerprint=link.native_query_fingerprint, source_evidence_refs=(evidence_id,), material={'name': 'P20 governed material', 'observations': [{'channel': 'Web', 'orders': 34}], 'statistics': {'association': 0.72}}, now=STAMP + timedelta(minutes=2))
    claims = ClaimLineageStore(research_store=store, db_engine=db)
    claim = claims.create_claim(session_id=session.session_id, obligation_id='g1', principal=p, claim_text='Web kanalı gözlenen kapsamda daha yüksek sipariş sayısına sahip.', proposition={'subject': 'channel:Web', 'predicate': 'has_higher_order_count_than', 'object': 'channel:Partner'}, scope={'period': '2026-06', 'population': 'sales_orders'}, freshness=ClaimFreshness(as_of=STAMP, stale_after=STAMP + timedelta(days=30)), origin_material_refs=(material.lead_id,))
    claim = claims.link_evidence(session_id=session.session_id, claim_id=claim.claim_id, evidence_id=evidence_id, relation=ClaimEvidenceRelation.SUPPORTS, principal=p)
    weak_claim = claims.create_claim(session_id=session.session_id, obligation_id='g1', principal=p, claim_text='Müşteri bileşimi farkı açıklıyor.', proposition={'subject': 'customer_mix', 'predicate': 'explains', 'object': 'order_gap'}, scope={'period': '2026-06', 'population': 'sales_orders'}, freshness=ClaimFreshness(as_of=STAMP, stale_after=STAMP + timedelta(days=30)), origin_material_refs=(material.lead_id,))
    weak_claim = claims.link_evidence(session_id=session.session_id, claim_id=weak_claim.claim_id, evidence_id=evidence_id, relation=ClaimEvidenceRelation.INSUFFICIENT, principal=p)
    step_id = 'rrs_' + h({'session': session.session_id, 'suffix': suffix})[:24]
    with Session(db) as s:
        s.add(ResearchReasoningStepRecord(step_id=step_id, session_id=session.session_id, source_revision=session.revision, source_snapshot_fingerprint=session.fingerprint, parent_obligation_id='g1', parent_step_id=None, depth=0, branch_id='ibr_' + h(step_id)[:20], intent='STOP_INVESTIGATION', target_kind='GAP', target_ref=None, stop_scope='INVESTIGATION', proposal_id=f'proposal-{suffix}', proposal_json=json.dumps({'kind': 'p20-fixture'}, sort_keys=True), action='STOP', objective_key=f'p20.{suffix}', bounded_objective=None, rationale='Provider-free P20 fixture.', inspected_evidence_refs_json=json.dumps([evidence_id]), inspected_claim_refs_json=json.dumps([claim.claim_id]), inspected_material_refs_json=json.dumps([material.lead_id]), proposal_fingerprint=h({'step': step_id, 'claim': claim.claim_id}), status='STOPPED', stop_reason='INCONCLUSIVE', result_refs_json='[]', created_at=STAMP + timedelta(minutes=3), completed_at=STAMP + timedelta(minutes=3)))
        s.commit()
    p18 = BusinessRelationshipPolicyStore(research_store=store, db_engine=db)
    scope = {'period': '2026-06', 'population': 'sales_orders'}
    policy = p18.create_policy(principal=p, semantic_context_version=session.context_version, policy_key='sales-order-customer-attribution', source_business_ref='business:sales-order', target_business_ref='business:customer', business_relationship_statement='Sales orders may map to governed customer identity.', applicability_scope=scope, provenance_ref=f'policy-manual:{suffix}', now=STAMP + timedelta(minutes=4))
    policy_use = p18.resolve(requirement=RelationshipPolicyRequirement(research_session_id=session.session_id, obligation_id='g1', claim_id=claim.claim_id, reasoning_step_id=step_id, policy_key=policy.policy_key, source_business_ref=policy.source_business_ref, target_business_ref=policy.target_business_ref, semantic_context_version=session.context_version, applicability_scope=scope, required=True), principal=p, now=STAMP + timedelta(minutes=5))
    p19 = HypothesisRootCauseStore(research_store=store, db_engine=db)
    a = p19.create_hypothesis(research_session_id=session.session_id, obligation_id='g1', statement='Kanal karışımı gözlenen sipariş farkına katkı sağlıyor olabilir.', principal=p, now=STAMP + timedelta(minutes=10))
    b = p19.create_hypothesis(research_session_id=session.session_id, obligation_id='g1', statement='Müşteri kompozisyonu gözlenen sipariş farkına katkı sağlıyor olabilir.', principal=p, now=STAMP + timedelta(minutes=11))
    ae = p19.create_grounding(hypothesis_id=a.hypothesis_id, source_kind=GroundingSourceKind.P14_EVIDENCE, source_ref=evidence_id, source_receipt_id=receipt_id, relation=GroundingRelation.SUPPORTS, principal=p, now=STAMP + timedelta(minutes=12))
    ap = p19.create_grounding(hypothesis_id=a.hypothesis_id, source_kind=GroundingSourceKind.P18_POLICY_USE, source_ref=policy_use.policy_use_id, relation=GroundingRelation.CONTEXT, principal=p, now=STAMP + timedelta(minutes=13))
    bm = p19.create_grounding(hypothesis_id=b.hypothesis_id, source_kind=GroundingSourceKind.P15_MATERIAL, source_ref=material.lead_id, relation=GroundingRelation.SUPPORTS, principal=p, now=STAMP + timedelta(minutes=14))
    bc = p19.create_grounding(hypothesis_id=b.hypothesis_id, source_kind=GroundingSourceKind.P16_CLAIM, source_ref=weak_claim.claim_id, relation=GroundingRelation.CHALLENGES, principal=p, now=STAMP + timedelta(minutes=15))
    no_root = p19.assess(draft=RootCauseAssessmentDraft(research_session_id=session.session_id, obligation_id='g1', candidates=(CandidateAssessment(hypothesis_id=a.hypothesis_id, grounding_link_ids=(ae.grounding_link_id, ap.grounding_link_id), disposition=HypothesisDisposition.RETAINED, epistemic_class=HypothesisEpistemicClass.ASSOCIATION, contribution_class=ContributionClass.UNKNOWN, evidence_strength=EvidenceStrength.WEAK, causal_qualification=CausalQualification.IDENTIFICATION_LIMITED, identification_limitations=(IdentificationLimitation.ASSOCIATION_ONLY,)), CandidateAssessment(hypothesis_id=b.hypothesis_id, grounding_link_ids=(bm.grounding_link_id, bc.grounding_link_id), disposition=HypothesisDisposition.RETAINED, epistemic_class=HypothesisEpistemicClass.COMPETING_HYPOTHESIS, contribution_class=ContributionClass.UNKNOWN, evidence_strength=EvidenceStrength.INSUFFICIENT, causal_qualification=CausalQualification.IDENTIFICATION_LIMITED, identification_limitations=(IdentificationLimitation.CONFOUNDING_NOT_RESOLVED,))), aggregate_outcome=AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED, limitations=('Causal identification is insufficient.',)), principal=p, now=STAMP + timedelta(minutes=16))
    return {'principal': p, 'store': store, 'session': session, 'link': link, 'evidence_id': evidence_id, 'receipt_id': receipt_id, 'material': material, 'claims': claims, 'claim': claim, 'weak_claim': weak_claim, 'step_id': step_id, 'policy_use': policy_use, 'p19': p19, 'a': a, 'b': b, 'ae': ae, 'ap': ap, 'bm': bm, 'bc': bc, 'no_root': no_root}

def source_evidence(state, path: str | None=None) -> SourceReference:
    return SourceReference(source_kind=ReportSourceKind.P14_EVIDENCE, source_ref=state['evidence_id'], source_receipt_id=state['receipt_id'], obligation_id='g1', source_path=path)

def source_claim(state, claim=None) -> SourceReference:
    claim = claim or state['claim']
    return SourceReference(source_kind=ReportSourceKind.P16_CLAIM, source_ref=claim.claim_id, obligation_id='g1')

def source_p19(state, assessment=None) -> SourceReference:
    assessment = assessment or state['no_root']
    return SourceReference(source_kind=ReportSourceKind.P19_ASSESSMENT, source_ref=assessment.assessment_id, obligation_id='g1')

def statement(kind, *, sources=(), payload=None, ceiling, text=None, seed=None):
    payload = payload or {}
    identity = {'kind': kind.value, 'payload': payload, 'seed': seed or kind.value}
    return ReportStatement(statement_id=stable_statement_id(identity), statement_kind=kind, source_refs=tuple(sources), obligation_refs=('g1',), limitation_refs=(), upstream_epistemic_ceiling=ceiling, payload=payload, text=text)

def report_draft(state, statement_item, *, key='report-main', limitations=()):
    return ReportDraft(research_session_id=state['session'].session_id, report_key=key, coverage=(CoverageEntry(obligation_id='g1', coverage_status=CoverageStatus.REPRESENTED, statement_ids=(statement_item.statement_id,)),), statements=(statement_item,), limitations=tuple(limitations))

def test_shared_relationship_completion_seals_without_forging_p14_terminal_state():
    db = db_engine()
    SQLModel.metadata.create_all(db)
    with Session(db) as s:
        s.add(Tenant(id=TENANT, slug='p20', name='P20', created_at=STAMP))
        s.add(User(id=USER, tenant_id=TENANT, email='p20@example.test', password_hash='unused', created_at=STAMP))
        s.commit()

    p = principal()
    downtime = ResearchSemanticRef(
        source_mention='downtime',
        candidate_id='metric.downtime',
        target_kind=SemanticTargetKind.METRIC,
        canonical_name='Downtime',
        cube_names=('machine_operations',),
    )
    faults = ResearchSemanticRef(
        source_mention='faults',
        candidate_id='metric.faults',
        target_kind=SemanticTargetKind.METRIC,
        canonical_name='Fault Count',
        cube_names=('machine_operations',),
    )
    department = ResearchSemanticRef(
        source_mention='department',
        candidate_id='dimension.department',
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name='Department',
        cube_names=('machine_operations',),
    )
    fragment = 'fragment-sha256:' + 'b' * 64
    ranking = ResearchQuestion(
        goal_id='g_rank',
        kind=ResearchGoalKind.RANKING,
        source_text='Rank downtime by department.',
        source_fragment_identity=fragment,
        subject_refs=(department, downtime),
        ranking=RankingSurface(
            text='rank downtime',
            direction='desc',
            limit=None,
            measure_semantic_id=downtime.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    relationship = ResearchQuestion(
        goal_id='g_relationship',
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text='Assess downtime with faults by department.',
        source_fragment_identity=fragment,
        subject_refs=(downtime, faults),
        related_refs=(department,),
        status=ResearchGoalStatus.RESOLVED,
    )
    accepted = ResearchBrief(
        brief_id='rb-p20-shared-relationship',
        objective='Reuse one governed analytical occurrence.',
        scope=ResearchScope(
            semantic_refs=(department, downtime, faults),
        ),
        questions=(ranking, relationship),
        must_requirement_ids=(ranking.goal_id, relationship.goal_id),
        context_version='ctx-p20-v1',
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=accepted,
        request_ref='p20-shared-relationship',
        source_message_hash='b' * 64,
        principal=p,
    )

    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id=ranking.goal_id,
    )
    session = store.save(
        prepared.session,
        expected_revision=session.revision,
    )
    link = store.begin_delegation(
        session=session,
        obligation_id=ranking.goal_id,
        dima_request_id=prepared.request.dima_request_id,
        dima_trace_id=prepared.request.dima_trace_id,
        native_conversation_id=prepared.request.conversation_id,
    )
    query = {
        'database': 1,
        'type': 'query',
        'query': {
            'source-table': 10,
            'aggregation': [['sum', ['field', 20, None]]],
            'breakout': [['field', 21, None]],
        },
    }
    link = store.mark_candidate(
        link.id,
        native_query_id='p20-shared-query',
        native_query=query,
        query_fingerprint=h(query),
    )
    store.mark_execution_started(
        link.id,
        native_subject_ref='metabase-user:20',
    )
    result_payload = {
        'database_id': 1,
        'row_count': 2,
        'data': {
            'rows': [
                ['Assembly', 100, 10],
                ['Quality', 50, 3],
            ]
        },
    }
    store.mark_executed(
        link.id,
        native_subject_ref='metabase-user:20',
        runtime_identity={
            'substrate': 'metabase-native',
            'runtime_version': 'v0.63.18-dima.9',
            'image_digest': 'sha256:' + 'e' * 64,
            'database_id': 'metabase:1',
        },
        result_payload=result_payload,
        result_hash=h(result_payload),
        executed_at=STAMP,
    )
    evidence_id = 'evi_' + h({'shared': 'evidence'})[:24]
    receipt_id = 'dqr_' + h({'shared': 'receipt'})[:24]
    store.mark_verified(
        link.id,
        receipt_id=receipt_id,
        evidence_id=evidence_id,
    )
    verified = ResearchManager.obligation(
        session,
        ranking.goal_id,
    ).model_copy(
        update={
            'state': ObligationState.VERIFIED,
            'evidence_refs': (evidence_id,),
        }
    )
    session = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, verified),
        evidence_refs=(
            EvidenceRef(
                evidence_id=evidence_id,
                receipt_id=receipt_id,
                authority_id=session.authority_id,
                obligation_id=ranking.goal_id,
            ),
        ),
        now=STAMP + timedelta(minutes=1),
    )
    session = store.save(
        session,
        expected_revision=session.revision - 1,
    )

    claims = ClaimLineageStore(research_store=store, db_engine=db)
    claim = claims.create_claim(
        session_id=session.session_id,
        obligation_id=ranking.goal_id,
        principal=p,
        claim_text='Downtime and fault count move together in the governed departmental slice.',
        proposition={'relationship_kind': 'ASSOCIATION'},
        scope={'dimension': department.candidate_id},
        freshness=ClaimFreshness(
            as_of=STAMP,
            stale_after=STAMP + timedelta(days=30),
        ),
        origin_material_refs=(),
    )
    claim = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id=evidence_id,
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=p,
    )
    step_id = 'rrs_' + h({'shared': session.session_id})[:24]
    with Session(db) as s:
        s.add(
            ResearchReasoningStepRecord(
                step_id=step_id,
                session_id=session.session_id,
                source_revision=session.revision,
                source_snapshot_fingerprint=session.fingerprint,
                parent_obligation_id=ranking.goal_id,
                parent_step_id=None,
                depth=0,
                branch_id='ibr_' + h(step_id)[:20],
                intent='FORM_CLAIM',
                target_kind='CLAIM',
                target_ref=claim.claim_id,
                stop_scope=None,
                proposal_id='proposal-shared',
                proposal_json=json.dumps({'kind': 'shared-relationship'}, sort_keys=True),
                action='FORM_CLAIM',
                objective_key='p20.shared.relationship',
                bounded_objective='Assess one governed relationship from shared material.',
                rationale='Provider-free shared material fixture.',
                inspected_evidence_refs_json=json.dumps([evidence_id]),
                inspected_claim_refs_json=json.dumps([claim.claim_id]),
                inspected_material_refs_json='[]',
                proposal_fingerprint=h({'step': step_id, 'claim': claim.claim_id}),
                status='COMPLETED',
                stop_reason=None,
                result_refs_json=json.dumps([claim.claim_id]),
                created_at=STAMP + timedelta(minutes=2),
                completed_at=STAMP + timedelta(minutes=2),
            )
        )
        s.commit()

    applicability = {
        'accepted_relationship_goal_id': relationship.goal_id,
        'semantic_ref_ids': [
            department.candidate_id,
            downtime.candidate_id,
            faults.candidate_id,
        ],
    }
    decision = BusinessRelationshipPolicyStore(
        research_store=store,
        db_engine=db,
    ).resolve(
        requirement=RelationshipPolicyRequirement(
            research_session_id=session.session_id,
            obligation_id=ranking.goal_id,
            claim_id=claim.claim_id,
            reasoning_step_id=step_id,
            policy_key='observational-only',
            source_business_ref='metric:downtime',
            target_business_ref='metric:faults',
            semantic_context_version=session.context_version,
            applicability_scope=applicability,
            required=False,
        ),
        principal=p,
        now=STAMP + timedelta(minutes=3),
    )
    relationship_result = project_relationship_result(
        research_session_id=session.session_id,
        claim=claim,
        decision=decision,
        requirement_id=relationship.goal_id,
        scope_lineage_id=session.lineage_id,
        scope_version_id=accepted.scope.scope_version.version_id,
        applicability_scope=applicability,
    )
    assert relationship_result.obligation_id == relationship.goal_id
    assert claim.obligation_id == ranking.goal_id

    # The relationship P14 obligation intentionally stays READY. P18 terminalizes
    # the accepted relationship at Product level without forging duplicate Evidence.
    persisted = store.load(
        session.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    relationship_obligation = ResearchManager.obligation(
        persisted,
        relationship.goal_id,
    )
    assert relationship_obligation.state == ObligationState.READY

    reports = ReportDocumentStore(research_store=store, db_engine=db)
    draft = reports.draft_from_governed_research(
        research_session_id=session.session_id,
        report_key='shared-relationship-report',
        principal=p,
        relationship_results=(relationship_result,),
    )
    report = reports.seal(draft=draft, principal=p)

    coverage = {item.obligation_id: item for item in report.coverage}
    assert coverage[ranking.goal_id].coverage_status == CoverageStatus.REPRESENTED
    assert coverage[relationship.goal_id].coverage_status == CoverageStatus.REPRESENTED
    relationship_statements = [
        item
        for item in report.statements
        if relationship.goal_id in item.obligation_refs
    ]
    assert len(relationship_statements) == 1
    assert relationship_statements[0].payload['claim_id'] == claim.claim_id
    assert {
        item.source_kind for item in relationship_statements[0].source_refs
    } == {
        ReportSourceKind.P16_CLAIM,
        ReportSourceKind.P18_POLICY_USE,
    }
    assert reports.currentness(
        report_id=report.report_id,
        principal=p,
    ) == ReportCurrentness.CURRENT

    # Metamorphic sibling: an upstream material/source obligation may not
    # impersonate the accepted relationship USER_MUST terminal identity.
    wrong_terminal_identity = relationship_result.model_copy(
        update={"obligation_id": ranking.goal_id}
    )
    with pytest.raises(P20ReportError) as exc:
        reports.draft_from_governed_research(
            research_session_id=session.session_id,
            report_key='shared-relationship-wrong-terminal',
            principal=p,
            relationship_results=(wrong_terminal_identity,),
        )
    assert exc.value.code == 'P20_RELATIONSHIP_RESULT_TARGET_INVALID'


def test_auto_draft_projects_governed_claim_policy_provenance_and_limitations():
    db = db_engine()
    state = make_state(db)
    claims = state["claims"]
    limited = claims.create_claim(
        session_id=state["session"].session_id,
        obligation_id="g1",
        principal=state["principal"],
        claim_text="Partner kanalı için örneklem sınırlı olsa da gözlemsel fark korunur.",
        proposition={
            "subject": "channel:Partner",
            "predicate": "observed_order_difference",
            "object": "channel:Web",
        },
        scope={"period": "2026-06", "population": "sales_orders"},
        freshness=ClaimFreshness(
            as_of=STAMP,
            stale_after=STAMP + timedelta(days=30),
        ),
        origin_material_refs=(state["material"].lead_id,),
        limitations=("Örneklem yalnız mevcut governed dönemle sınırlıdır.",),
    )
    limited = claims.link_evidence(
        session_id=state["session"].session_id,
        claim_id=limited.claim_id,
        evidence_id=state["evidence_id"],
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=state["principal"],
    )

    store = ReportDocumentStore(research_store=state["store"], db_engine=db)
    draft = store.draft_from_governed_research(
        research_session_id=state["session"].session_id,
        report_key="auto-contextual",
        principal=state["principal"],
    )

    analytical = [
        item
        for item in draft.statements
        if item.statement_kind == ReportStatementKind.ANALYTICAL_FACT
    ]
    assert {item.payload["claim_id"] for item in analytical} >= {
        state["claim"].claim_id,
        limited.claim_id,
    }
    governed = next(
        item for item in analytical
        if item.payload["claim_id"] == state["claim"].claim_id
    )
    assert any(
        ref.source_kind == ReportSourceKind.P16_CLAIM
        and ref.source_ref == state["claim"].claim_id
        for ref in governed.source_refs
    )
    assert any(
        ref.source_kind == ReportSourceKind.P18_POLICY_USE
        and ref.source_ref == state["policy_use"].policy_use_id
        for ref in governed.source_refs
    )

    limited_statement = next(
        item for item in analytical
        if item.payload["claim_id"] == limited.claim_id
    )
    assert len(limited_statement.limitation_refs) == 1
    limitation = next(
        item for item in draft.limitations
        if item.limitation_id == limited_statement.limitation_refs[0]
    )
    assert limitation.detail == "Örneklem yalnız mevcut governed dönemle sınırlıdır."
    assert any(
        item.statement_kind == ReportStatementKind.NUMERIC
        for item in draft.statements
    )

    report = store.seal(
        draft=draft,
        principal=state["principal"],
        now=STAMP + timedelta(minutes=30),
    )
    texts = {item.text for item in report.statements}
    assert state["claim"].claim_text in texts
    assert limited.claim_text in texts


def test_user_must_is_100_percent_accounted_and_seals_one_report():
    db = db_engine()
    state = make_state(db)
    item = statement(ReportStatementKind.ANALYTICAL_FACT, sources=(source_claim(state),), payload={'claim_id': state['claim'].claim_id, 'epistemic_state': state['claim'].epistemic_state.value}, ceiling=state['claim'].epistemic_state.value)
    report = ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'], now=STAMP)
    assert report.coverage[0].coverage_status == CoverageStatus.REPRESENTED
    assert report.statements[0].text == state['claim'].claim_text
    with Session(db) as s:
        assert len(s.exec(select(ReportDocumentRecord)).all()) == 1

def test_missing_user_must_coverage_rejects():
    db = db_engine()
    state = make_state(db)
    lim = ReportLimitation(limitation_id=stable_limitation_id({'g1': 'missing'}), obligation_id='g1', code='MISSING', detail='Required report material is unavailable.')
    bad = ReportDraft(research_session_id=state['session'].session_id, report_key='missing', coverage=(CoverageEntry(obligation_id='wrong', coverage_status=CoverageStatus.LIMITED, limitation_ids=(lim.limitation_id,)),), limitations=(lim,))
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=bad, principal=state['principal'])
    assert exc.value.code == 'P20_USER_MUST_COVERAGE_INCOMPLETE'

def test_numeric_without_governed_provenance_rejects():
    db = db_engine()
    state = make_state(db)
    item = statement(ReportStatementKind.NUMERIC, payload={'value': 34}, ceiling='EXACT_GOVERNED_NUMERIC')
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert exc.value.code == 'P20_NUMERIC_PROVENANCE_REQUIRED'

def test_numeric_exact_governed_value_and_source_identity_are_preserved():
    db = db_engine()
    state = make_state(db)
    ref = source_evidence(state, 'data.rows.0.1')
    item = statement(ReportStatementKind.NUMERIC, sources=(ref,), payload={'value': 34}, ceiling='EXACT_GOVERNED_NUMERIC')
    report = ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert report.statements[0].payload == {'value': 34}
    assert report.statements[0].source_refs == (ref,)
    assert report.statements[0].text == 'Numeric result: 34'

def test_p16_insufficient_claim_cannot_be_strengthened():
    db = db_engine()
    state = make_state(db)
    weak = state['weak_claim']
    item = statement(ReportStatementKind.ANALYTICAL_FACT, sources=(source_claim(state, weak),), payload={'claim_id': weak.claim_id, 'epistemic_state': weak.epistemic_state.value}, ceiling=weak.epistemic_state.value, text=weak.claim_text)
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert exc.value.code == 'P20_TEXT_NOT_CANONICAL'

def test_association_cannot_become_causal():
    db = db_engine()
    state = make_state(db)
    item = statement(ReportStatementKind.CAUSAL, sources=(source_p19(state),), payload={'hypothesis_id': state['a'].hypothesis_id}, ceiling=CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION.value)
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert exc.value.code == 'P20_CAUSAL_AUTHORITY_INSUFFICIENT'

@pytest.mark.parametrize('ref', [lambda s: SourceReference(source_kind=ReportSourceKind.P18_POLICY_USE, source_ref=s['policy_use'].policy_use_id, obligation_id='g1'), lambda s: SourceReference(source_kind=ReportSourceKind.P17_REASONING_STEP, source_ref=s['step_id'], obligation_id='g1')])
def test_p18_or_p17_alone_cannot_authorize_causal_wording(ref):
    db = db_engine()
    state = make_state(db)
    item = statement(ReportStatementKind.CAUSAL, sources=(ref(state),), payload={'hypothesis_id': state['a'].hypothesis_id}, ceiling=CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION.value)
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert exc.value.code == 'P20_STATEMENT_SOURCE_CARDINALITY_INVALID'

def test_root_cause_rejects_when_p19_did_not_establish_one():
    db = db_engine()
    state = make_state(db)
    item = statement(ReportStatementKind.ROOT_CAUSE, sources=(source_p19(state),), payload={'hypothesis_id': state['a'].hypothesis_id}, ceiling=AggregateOutcome.ROOT_CAUSE_ESTABLISHED.value)
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert exc.value.code == 'P20_ROOT_CAUSE_NOT_ESTABLISHED'

def test_no_defensible_root_cause_is_reportable_without_upgrade():
    db = db_engine()
    state = make_state(db)
    item = statement(ReportStatementKind.UNCERTAINTY, sources=(source_p19(state),), payload={}, ceiling=AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED.value)
    report = ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    text = report.statements[0].text
    assert text.startswith('No defensible root cause established. Retained candidates: ')
    assert state['a'].statement in text
    assert state['b'].statement in text
    assert 'epistemic=ASSOCIATION' in text
    assert 'evidence=WEAK' in text
    assert 'epistemic=COMPETING_HYPOTHESIS' in text
    assert 'evidence=INSUFFICIENT' in text

def make_multiple_assessment(state):
    numeric = NumericProvenanceRef(source_kind=GroundingSourceKind.P15_MATERIAL, source_ref=state['material'].lead_id, source_path='observations.0.orders', analytical_kind=NumericAnalyticalKind.NATIVE_NUMERIC_RESULT)
    return state['p19'].assess(draft=RootCauseAssessmentDraft(research_session_id=state['session'].session_id, obligation_id='g1', candidates=(CandidateAssessment(hypothesis_id=state['a'].hypothesis_id, grounding_link_ids=(state['ae'].grounding_link_id, state['ap'].grounding_link_id), disposition=HypothesisDisposition.RETAINED, epistemic_class=HypothesisEpistemicClass.CONTRIBUTION, contribution_class=ContributionClass.MATERIAL, evidence_strength=EvidenceStrength.STRONG), CandidateAssessment(hypothesis_id=state['b'].hypothesis_id, grounding_link_ids=(state['bm'].grounding_link_id, state['bc'].grounding_link_id), disposition=HypothesisDisposition.RETAINED, epistemic_class=HypothesisEpistemicClass.CONTRIBUTION, contribution_class=ContributionClass.MATERIAL, evidence_strength=EvidenceStrength.MODERATE, numeric_provenance=(numeric,))), aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS), principal=state['principal'], now=STAMP + timedelta(minutes=20))

def test_multiple_material_contributors_remain_plural():
    db = db_engine()
    state = make_state(db)
    assessment = make_multiple_assessment(state)
    governed = [state['a'].hypothesis_id, state['b'].hypothesis_id]
    item = statement(ReportStatementKind.CONTRIBUTION, sources=(source_p19(state, assessment),), payload={'candidate_hypothesis_ids': governed}, ceiling=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS.value)
    report = ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert state['a'].statement in report.statements[0].text
    assert state['b'].statement in report.statements[0].text
    collapsed = statement(ReportStatementKind.CONTRIBUTION, sources=(source_p19(state, assessment),), payload={'candidate_hypothesis_ids': governed[:1]}, ceiling=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS.value, seed='collapsed')
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, collapsed, key='collapsed'), principal=state['principal'])
    assert exc.value.code == 'P20_CONTRIBUTION_SET_MISMATCH'

def test_contribution_wording_cannot_invent_percentage():
    db = db_engine()
    state = make_state(db)
    assessment = make_multiple_assessment(state)
    item = statement(ReportStatementKind.CONTRIBUTION, sources=(source_p19(state, assessment),), payload={'candidate_hypothesis_ids': [state['a'].hypothesis_id, state['b'].hypothesis_id]}, ceiling=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS.value, text="Kanal karışımı etkinin %80'ini açıklıyor.")
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert exc.value.code == 'P20_TEXT_NOT_CANONICAL'

def test_relationship_report_renders_exact_salient_magnitudes_and_decision_use():
    db = db_engine()
    state = make_state(db, suffix='relationship-presentation')
    relationship = state['claims'].create_claim(
        session_id=state['session'].session_id,
        obligation_id='g1',
        principal=state['principal'],
        claim_text='Observed channel counts move in the same direction in this bounded view.',
        proposition={
            'relationship_kind': 'ASSOCIATION',
            'relationship_intent': 'observational',
            'material_mode': 'CROSS_SECTIONAL_ASSOCIATION',
            'source_semantic_id': 'metric.orders',
            'target_semantic_id': 'metric.orders_peer',
            'salient_cells': [
                {
                    'evidence_id': state['evidence_id'],
                    'row_index': 0,
                    'column_index': 1,
                },
                {
                    'evidence_id': state['evidence_id'],
                    'row_index': 1,
                    'column_index': 1,
                },
            ],
        },
        scope={'scope_version_id': 'scope_v1'},
        freshness=ClaimFreshness(as_of=STAMP),
        limitations=('Cross-sectional Evidence does not establish causality.',),
    )
    relationship = state['claims'].link_evidence(
        session_id=state['session'].session_id,
        claim_id=relationship.claim_id,
        evidence_id=state['evidence_id'],
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=state['principal'],
    )
    item = statement(
        ReportStatementKind.ANALYTICAL_FACT,
        sources=(source_claim(state, relationship),),
        payload={
            'claim_id': relationship.claim_id,
            'epistemic_state': 'SUPPORTED',
        },
        ceiling='SUPPORTED',
        seed='relationship-salient',
    )

    report = ReportDocumentStore(
        research_store=state['store'],
        db_engine=db,
    ).seal(
        draft=report_draft(state, item, key='relationship-salient'),
        principal=state['principal'],
    )

    text = report.statements[0].text or ''
    assert 'Observed magnitudes:' in text
    assert 'Web' in text and '34' in text
    assert 'Partner' in text and '12' in text
    assert 'Decision use:' in text
    assert 'not as causal evidence' in text


def test_relationship_salient_projection_fails_closed_on_stale_evidence_identity():
    db = db_engine()
    state = make_state(db, suffix='relationship-stale')
    relationship = state['claims'].create_claim(
        session_id=state['session'].session_id,
        obligation_id='g1',
        principal=state['principal'],
        claim_text='Bounded relationship.',
        proposition={
            'relationship_kind': 'ASSOCIATION',
            'salient_cells': [
                {
                    'evidence_id': 'evi_' + 'f' * 24,
                    'row_index': 0,
                    'column_index': 1,
                },
            ],
        },
        scope={'scope_version_id': 'scope_v1'},
        freshness=ClaimFreshness(as_of=STAMP),
    )
    # No Evidence edge can be created for the foreign identity. The report must
    # fail at the projection boundary rather than silently omit provenance.
    item = statement(
        ReportStatementKind.ANALYTICAL_FACT,
        sources=(source_claim(state, relationship),),
        payload={
            'claim_id': relationship.claim_id,
            'epistemic_state': 'PROPOSED',
        },
        ceiling='PROPOSED',
        seed='relationship-stale',
    )
    with pytest.raises(P20ReportError) as exc:
        ReportDocumentStore(
            research_store=state['store'],
            db_engine=db,
        ).seal(
            draft=report_draft(state, item, key='relationship-stale'),
            principal=state['principal'],
        )
    assert exc.value.code == 'P20_RELATIONSHIP_SALIENT_EVIDENCE_INVALID'


def test_p15_numeric_requires_exact_p19_retained_provenance():
    db = db_engine()
    state = make_state(db)
    assessment = make_multiple_assessment(state)
    ref = SourceReference(source_kind=ReportSourceKind.P15_MATERIAL, source_ref=state['material'].lead_id, obligation_id='g1', source_path='observations.0.orders')
    item = statement(ReportStatementKind.NUMERIC, sources=(ref, source_p19(state, assessment)), payload={'value': 34}, ceiling='EXACT_GOVERNED_NUMERIC')
    report = ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    assert report.statements[0].text == 'Numeric result: 34'

def _contest_claim(db, state):
    fake_evidence = 'evi_' + h({'contest': state['claim'].claim_id})[:24]
    with Session(db) as s:
        row = s.get(ResearchClaimRecord, state['claim'].claim_id)
        assert row is not None
        s.add(ClaimEvidenceLinkRecord(link_id='cel_' + h({'claim': row.claim_id, 'evidence': fake_evidence})[:24], claim_id=row.claim_id, evidence_id=fake_evidence, receipt_id=state['receipt_id'], execution_link_id=state['link'].id, relation=ClaimEvidenceRelation.CHALLENGES.value, created_at=STAMP + timedelta(minutes=30)))
        row.epistemic_state = 'CONTESTED'
        row.updated_at = STAMP + timedelta(minutes=30)
        s.add(row)
        s.commit()

def test_source_change_marks_old_report_stale_without_mutation():
    db = db_engine()
    state = make_state(db)
    item = statement(ReportStatementKind.ANALYTICAL_FACT, sources=(source_claim(state),), payload={'claim_id': state['claim'].claim_id, 'epistemic_state': 'SUPPORTED'}, ceiling='SUPPORTED')
    store = ReportDocumentStore(research_store=state['store'], db_engine=db)
    report = store.seal(draft=report_draft(state, item), principal=state['principal'])
    before = report.model_dump(mode='json')
    assert store.currentness(report_id=report.report_id, principal=state['principal']) == ReportCurrentness.CURRENT
    _contest_claim(db, state)
    assert store.currentness(report_id=report.report_id, principal=state['principal']) == ReportCurrentness.STALE_SOURCE_SET
    assert store.load(report_id=report.report_id, principal=state['principal']).model_dump(mode='json') == before

def test_restart_idempotency_and_new_source_set_revision():
    db = db_engine()
    state = make_state(db)
    first_item = statement(ReportStatementKind.ANALYTICAL_FACT, sources=(source_claim(state),), payload={'claim_id': state['claim'].claim_id, 'epistemic_state': 'SUPPORTED'}, ceiling='SUPPORTED')
    first_draft = report_draft(state, first_item)
    first = ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=first_draft, principal=state['principal'])
    restarted = ReportDocumentStore(research_store=state['store'], db_engine=db)
    same = restarted.seal(draft=first_draft, principal=state['principal'])
    assert same.report_id == first.report_id
    assert same.report_fingerprint == first.report_fingerprint
    assert same.revision == 1
    _contest_claim(db, state)
    second_item = statement(ReportStatementKind.ANALYTICAL_FACT, sources=(source_claim(state),), payload={'claim_id': state['claim'].claim_id, 'epistemic_state': 'CONTESTED'}, ceiling='CONTESTED', seed='revision-2')
    second = restarted.seal(draft=report_draft(state, second_item), principal=state['principal'])
    assert second.report_id != first.report_id
    assert second.revision == 2
    assert second.parent_report_id == first.report_id

def test_limited_user_must_is_explicitly_reportable():
    db = db_engine()
    state = make_state(db)
    lid = stable_limitation_id({'g1': 'cannot-publish'})
    limitation = ReportLimitation(limitation_id=lid, obligation_id='g1', code='UPSTREAM_INSUFFICIENT', detail='Governed upstream truth is insufficient for a factual statement.', source_refs=(source_p19(state),))
    draft = ReportDraft(research_session_id=state['session'].session_id, report_key='limited', coverage=(CoverageEntry(obligation_id='g1', coverage_status=CoverageStatus.LIMITED, limitation_ids=(lid,)),), statements=(), limitations=(limitation,))
    report = ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=draft, principal=state['principal'])
    assert report.coverage[0].coverage_status == CoverageStatus.LIMITED
    assert report.limitations == (limitation,)

def test_p14_to_p19_authorities_are_unchanged_by_report_seal():
    db = db_engine()
    state = make_state(db)
    before = {}
    with Session(db) as s:
        for model in (ResearchExecutionLink, ResearchExplorationMaterial, ResearchClaimRecord, ResearchReasoningStepRecord, BusinessRelationshipPolicyUseRecord, HypothesisRecord, HypothesisGroundingLink, RootCauseAssessment):
            before[model.__name__] = [x.model_dump() for x in s.exec(select(model)).all()]
    item = statement(ReportStatementKind.UNCERTAINTY, sources=(source_p19(state),), payload={}, ceiling=AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED.value)
    ReportDocumentStore(research_store=state['store'], db_engine=db).seal(draft=report_draft(state, item), principal=state['principal'])
    with Session(db) as s:
        for model in (ResearchExecutionLink, ResearchExplorationMaterial, ResearchClaimRecord, ResearchReasoningStepRecord, BusinessRelationshipPolicyUseRecord, HypothesisRecord, HypothesisGroundingLink, RootCauseAssessment):
            after = [x.model_dump() for x in s.exec(select(model)).all()]
            assert after == before[model.__name__]

def test_p20_has_exactly_one_durable_record_type():
    tables = {table.name for table in SQLModel.metadata.tables.values() if table.name.startswith('p20_')}
    assert tables == {'p20_report_document'}

def test_p20_production_owner_has_zero_analytics_or_duplicate_authority():
    path = Path('app/v3/report_document.py')
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update((alias.name for alias in node.names))
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or '')
    forbidden_imports = ('app.v3.substrate.metabase', 'app.v3.research_native_gateway', 'app.v3.research_followup', 'app.v3.native_execution', 'app.wren', 'numpy', 'pandas', 'scipy', 'statistics')
    assert not any((name.startswith(forbidden_imports) for name in imports))
    for forbidden in ('NativeEngineBridge', 'MetabaseAgentClient', 'execute_dataset', 'explore_adhoc', 'attest_native_query', 'execute_native_query', 'wren_service', 'DimaQueryReceipt(', 'EvidenceArtifact(', 'ResearchClaimRecord(', 'RootCauseAssessmentRecord(', '.assess('):
        assert forbidden not in source
