from __future__ import annotations

import hashlib
import inspect
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

import app.v3.claim_lineage as claim_module
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
    ClaimLineageError,
    ClaimLineageStore,
)
from app.v3.research import EvidenceRef, ObligationState, ResearchManager
from app.v3.research_exploration import ResearchExplorationStore
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.models import ResearchExecutionLink, Tenant, User


TENANT = UUID("00000000-0000-4000-8000-000000001601")
USER = UUID("00000000-0000-4000-8000-000000001602")
STAMP = datetime(2026, 9, 25, 10, 0, tzinfo=timezone.utc)


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
        tenant_slug="p16",
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
        source_text="Kanal performansını araştır.",
        subject_refs=(metric,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p16",
        objective=q.source_text,
        scope=ResearchScope(semantic_refs=(metric,)),
        questions=(q,),
        must_requirement_ids=("g1",),
        context_version="ctx-p16-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def setup_verified(db, *, request_ref="p16", evidence_suffix="1"):
    SQLModel.metadata.create_all(db)
    with Session(db) as s:
        if s.get(Tenant, TENANT) is None:
            s.add(Tenant(id=TENANT, slug="p16", name="P16", created_at=STAMP))
            s.add(
                User(
                    id=USER,
                    tenant_id=TENANT,
                    email="p16@example.test",
                    password_hash="unused",
                    created_at=STAMP,
                )
            )
            s.commit()
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=brief(),
        request_ref=request_ref,
        source_message_hash=hashlib.sha256(request_ref.encode()).hexdigest(),
        principal=principal(),
    )
    prepared = ResearchManager.prepare_native_delegation(session, obligation_id="g1")
    session = store.save(prepared.session, expected_revision=session.revision)
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
        "query": {"source-table": 10, "aggregation": [["count"]]},
    }
    link = store.mark_candidate(
        link.id,
        native_query_id=f"query-{evidence_suffix}",
        native_query=query,
        query_fingerprint=h(query),
    )
    store.mark_execution_started(
        link.id,
        native_subject_ref="metabase-user:7",
    )
    result = {"database_id": 1, "row_count": 1, "data": {"rows": [[34]]}}
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
    evidence_id = "evi_" + evidence_suffix * 24
    receipt_id = "dqr_" + evidence_suffix * 24
    store.mark_verified(link.id, receipt_id=receipt_id, evidence_id=evidence_id)

    item = ResearchManager.obligation(session, "g1").model_copy(
        update={"state": ObligationState.VERIFIED, "evidence_refs": (evidence_id,)}
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
    store.save(session, expected_revision=session.revision - 1)
    return store, session, store.execution_link(link.id)


def add_second_evidence(store, session, *, suffix="2"):
    link = store.begin_delegation(
        session=session,
        obligation_id="g1",
        dima_request_id=f"p16-extra-{suffix}",
        dima_trace_id=f"p16-extra-{suffix}-trace",
        native_conversation_id=uuid4(),
    )
    query = {"database": 1, "type": "query", "query": {"source-table": 11}}
    link = store.mark_candidate(
        link.id,
        native_query_id=f"query-{suffix}",
        native_query=query,
        query_fingerprint=h(query),
    )
    store.mark_execution_started(link.id, native_subject_ref="metabase-user:7")
    result = {"database_id": 1, "row_count": 1, "data": {"rows": [[22]]}}
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
    evidence_id = "evi_" + suffix * 24
    receipt_id = "dqr_" + suffix * 24
    store.mark_verified(link.id, receipt_id=receipt_id, evidence_id=evidence_id)
    item = ResearchManager.obligation(session, "g1")
    item = item.model_copy(
        update={"evidence_refs": (*item.evidence_refs, evidence_id)}
    )
    session = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, item),
        evidence_refs=(
            *session.evidence_refs,
            EvidenceRef(
                evidence_id=evidence_id,
                receipt_id=receipt_id,
                authority_id=session.authority_id,
                obligation_id="g1",
            ),
        ),
    )
    store.save(session, expected_revision=session.revision - 1)
    return session, store.execution_link(link.id), evidence_id


def freshness():
    return ClaimFreshness(
        as_of=STAMP,
        stale_after=STAMP + timedelta(days=30),
    )


def create_claim(service, session, **kwargs):
    return service.create_claim(
        session_id=session.session_id,
        obligation_id="g1",
        principal=principal(),
        claim_text=kwargs.pop(
            "claim_text",
            "Mevcut Müşteri kanalı incelenen kapsamda en yüksek sipariş sayısına sahip.",
        ),
        proposition=kwargs.pop(
            "proposition",
            {
                "subject": "channel:Mevcut Müşteri",
                "predicate": "has_highest_order_count",
                "object": "examined_channel_set",
            },
        ),
        scope=kwargs.pop(
            "scope",
            {"period": "Haziran 2026", "population": "sales_orders"},
        ),
        freshness=kwargs.pop("freshness", freshness()),
        **kwargs,
    )


def test_p15_origin_material_does_not_promote_claim_until_eligible_evidence_is_linked():
    db = db_engine()
    store, session, link = setup_verified(db)
    lead = ResearchExplorationStore(db).persist(
        session_id=session.session_id,
        obligation_id="g1",
        execution_link_id=link.id,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        query_fingerprint=link.native_query_fingerprint,
        source_evidence_refs=(link.evidence_id,),
        material={"name": "Native lead", "dashcards": [{"id": "x1"}]},
        now=STAMP,
    )
    claims = ClaimLineageStore(research_store=store, db_engine=db)
    claim = create_claim(
        claims,
        session,
        origin_material_refs=(lead.lead_id,),
    )
    assert claim.epistemic_state == ClaimEpistemicState.PROPOSED
    assert claim.evidence_links == ()
    assert claim.origin_material_refs == (lead.lead_id,)

    supported = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id=link.evidence_id,
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=principal(),
    )
    assert supported.epistemic_state == ClaimEpistemicState.SUPPORTED
    assert supported.evidence_links[0].execution_link_id == str(link.id)


def test_support_and_challenge_become_contested_and_restart_preserves_lineage():
    db = db_engine()
    store, session, first_link = setup_verified(db)
    session, second_link, second_evidence = add_second_evidence(store, session)
    claims = ClaimLineageStore(research_store=store, db_engine=db)
    claim = create_claim(claims, session)
    claim = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id=first_link.evidence_id,
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=principal(),
    )
    assert claim.epistemic_state == ClaimEpistemicState.SUPPORTED

    claim = claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id=second_evidence,
        relation=ClaimEvidenceRelation.CHALLENGES,
        principal=principal(),
    )
    assert claim.epistemic_state == ClaimEpistemicState.CONTESTED
    assert {x.relation for x in claim.evidence_links} == {
        ClaimEvidenceRelation.SUPPORTS,
        ClaimEvidenceRelation.CHALLENGES,
    }

    restored = ClaimLineageStore(
        research_store=ResearchSessionStore(db),
        db_engine=db,
    ).load_claim(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        principal=principal(),
    )
    assert restored == claim
    assert {
        x.execution_link_id for x in restored.evidence_links
    } == {str(first_link.id), str(second_link.id)}


def test_contextualizes_does_not_promote_and_insufficient_is_explicit():
    db = db_engine()
    store, session, link = setup_verified(db)
    claims = ClaimLineageStore(research_store=store, db_engine=db)

    contextual = create_claim(
        claims,
        session,
        claim_text="Kanal dağılımı bu araştırmanın bağlamını oluşturuyor.",
        proposition={"subject": "channel_mix", "predicate": "context_for", "object": "research"},
    )
    contextual = claims.link_evidence(
        session_id=session.session_id,
        claim_id=contextual.claim_id,
        evidence_id=link.evidence_id,
        relation=ClaimEvidenceRelation.CONTEXTUALIZES,
        principal=principal(),
    )
    assert contextual.epistemic_state == ClaimEpistemicState.PROPOSED

    insufficient = create_claim(
        claims,
        session,
        claim_text="Kanal farkının nedeninin kampanya olduğu iddiası henüz kurulamadı.",
        proposition={"subject": "campaign", "predicate": "caused", "object": "channel_gap"},
    )
    insufficient = claims.link_evidence(
        session_id=session.session_id,
        claim_id=insufficient.claim_id,
        evidence_id=link.evidence_id,
        relation=ClaimEvidenceRelation.INSUFFICIENT,
        principal=principal(),
    )
    assert (
        insufficient.epistemic_state
        == ClaimEpistemicState.INSUFFICIENT_EVIDENCE
    )


def test_foreign_session_evidence_and_receipt_execution_mismatch_fail_closed():
    db = db_engine()
    store, session, link = setup_verified(db, request_ref="p16-main", evidence_suffix="3")
    claims = ClaimLineageStore(research_store=store, db_engine=db)
    claim = create_claim(claims, session)

    with pytest.raises(ClaimLineageError) as missing:
        claims.link_evidence(
            session_id=session.session_id,
            claim_id=claim.claim_id,
            evidence_id="evi_" + "9" * 24,
            relation=ClaimEvidenceRelation.SUPPORTS,
            principal=principal(),
        )
    assert missing.value.code == "P16_EVIDENCE_NOT_IN_SESSION"

    with Session(db) as s:
        execution = s.get(ResearchExecutionLink, link.id)
        execution.receipt_id = "dqr_" + "8" * 24
        s.add(execution)
        s.commit()

    with pytest.raises(ClaimLineageError) as broken:
        claims.link_evidence(
            session_id=session.session_id,
            claim_id=claim.claim_id,
            evidence_id=link.evidence_id,
            relation=ClaimEvidenceRelation.SUPPORTS,
            principal=principal(),
        )
    assert broken.value.code == "P16_EVIDENCE_EXECUTION_PROVENANCE_INVALID"


def test_claim_evidence_relation_is_immutable_for_same_evidence():
    db = db_engine()
    store, session, link = setup_verified(db, evidence_suffix="4")
    claims = ClaimLineageStore(research_store=store, db_engine=db)
    claim = create_claim(claims, session)
    claims.link_evidence(
        session_id=session.session_id,
        claim_id=claim.claim_id,
        evidence_id=link.evidence_id,
        relation=ClaimEvidenceRelation.SUPPORTS,
        principal=principal(),
    )
    with pytest.raises(ClaimLineageError) as exc:
        claims.link_evidence(
            session_id=session.session_id,
            claim_id=claim.claim_id,
            evidence_id=link.evidence_id,
            relation=ClaimEvidenceRelation.CHALLENGES,
            principal=principal(),
        )
    assert exc.value.code == "P16_EVIDENCE_RELATION_IMMUTABLE"


def test_p16_has_no_analytics_engine_model_call_or_numeric_confidence():
    source = inspect.getsource(claim_module)
    for forbidden in (
        "NativeStandardTrustOrchestrator",
        "ResolvedAnalyticsIntent",
        "MetabaseProjectionCompiler",
        "MetabaseCanonicalizer",
        "execute_dataset",
        "explore_adhoc",
        "llm",
        "confidence",
    ):
        assert forbidden not in source.lower() if forbidden == "llm" else forbidden not in source

    imported_roots = set()
    tree = __import__("ast").parse(source)
    for node in __import__("ast").walk(tree):
        if isinstance(node, __import__("ast").Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, __import__("ast").ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert imported_roots.isdisjoint({"numpy", "pandas", "scipy", "statistics"})
