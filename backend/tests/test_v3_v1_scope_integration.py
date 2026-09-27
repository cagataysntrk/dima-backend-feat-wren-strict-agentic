from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.authority import AcceptedResearchAuthority
from app.v3.claim_lineage import ClaimFreshness, ClaimLineageStore
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.hypothesis_root_cause import (
    GroundingRelation,
    GroundingSourceKind,
    HypothesisRootCauseStore,
    P19EpistemicError,
)
from app.v3.product.service import HeadlessProductService, ProductSources
from app.v3.research import (
    EvidenceRef,
    ObligationState,
    ResearchManager,
    ResearchStateError,
)
from app.v3.research_contracts import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ScopeMutation,
    ScopeMutationKind,
    SemanticTargetKind,
    apply_scope_mutation,
)
from app.v3.research_intake import (
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
)
from app.v3.report_document import CoverageStatus, ReportDocumentStore
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from control_plane.authorize import Principal


NOW = datetime(2026, 9, 27, 17, 0, tzinfo=timezone.utc)
TENANT = UUID("00000000-0000-4000-8000-00000000b201")
USER = UUID("00000000-0000-4000-8000-00000000b202")


def principal():
    return Principal(
        user_id=str(USER),
        tenant_id=str(TENANT),
        tenant_slug="scope-integration",
        roles=["analyst"],
    )


def sem(cid, kind, name):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=kind,
        canonical_name=name,
        cube_names=("operations",),
    )


METRIC = sem("metric.downtime", SemanticTargetKind.METRIC, "Downtime")
METRIC_2 = sem("metric.faults", SemanticTargetKind.METRIC, "Faults")
DIM = sem("dimension.machine", SemanticTargetKind.DIMENSION, "Machine")
DIM_2 = sem("dimension.shift", SemanticTargetKind.DIMENSION, "Shift")
ASSEMBLY = sem("entity.assembly", SemanticTargetKind.ENTITY_VALUE, "Assembly")
PAINT = sem("entity.paint", SemanticTargetKind.ENTITY_VALUE, "Paint")


def db_engine():
    value = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(value)
    return value


def catalog():
    return ResearchIntakeCatalog(
        context_version="ctx-scope-production-v1",
        semantic_refs=(METRIC, METRIC_2, DIM, DIM_2, ASSEMBLY, PAINT),
        supported_domains=("operations",),
    )


def initial_brief():
    q = ResearchQuestion(
        goal_id="g_initial",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect downtime for Assembly and Paint by machine.",
        subject_refs=(METRIC, ASSEMBLY, PAINT),
        related_refs=(DIM,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb_scope_initial",
        objective="Inspect scoped downtime.",
        scope=ResearchScope(
            semantic_refs=(METRIC, ASSEMBLY, PAINT, DIM),
            time_surfaces=("2026-H1",),
        ),
        questions=(q,),
        must_requirement_ids=(q.goal_id,),
        context_version="ctx-scope-production-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


class FakeTransport:
    def __init__(self, payload):
        self.payload = payload
        self.call_count = 0

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema, schema_name
        self.call_count += 1
        return json.dumps(self.payload)


def narrowed_payload():
    return {
        "terminal": "READY",
        "objective": "Inspect Assembly downtime only.",
        "goals": [
            {
                "goal_key": "assembly-current",
                "kind": "breakdown",
                "source_text": "Inspect Assembly downtime by machine.",
                "allowed_relationship_id": None,
                "subject_semantic_ids": ["metric.downtime", "entity.assembly"],
                "related_semantic_ids": ["dimension.machine"],
                "ranking": None,
                "comparison_texts": [],
            }
        ],
        "deliverables": [],
        "investigation_directives": [],
        "time_surfaces": ["2026-H1"],
        "required_domains": ["operations"],
        "scope_mutation_kind": "NARROW_ENTITY",
        "clarification_question": None,
        "unsupported_reason": None,
    }


def start_v1(db):
    store = ResearchSessionStore(db)
    research = ResearchAskOrchestrator(store=store)
    brief = initial_brief()
    session = research.start_from_brief(
        brief=brief,
        request_ref="scope-turn-1",
        source_message_hash="a" * 64,
        principal=principal(),
    )
    return store, research, brief, session


def verify_without_evidence(store, session):
    obligation = session.obligations[0].model_copy(
        update={"state": ObligationState.VERIFIED}
    )
    updated = ResearchManager.advance(
        session,
        obligations=(obligation,),
        now=NOW,
    )
    return store.save(updated, expected_revision=session.revision)


def test_real_follow_up_path_mints_new_scope_authority_and_preserves_lineage():
    db = db_engine()
    store, research, brief_v1, session_v1 = start_v1(db)
    transport = FakeTransport(narrowed_payload())
    service = HeadlessProductService(
        sources=ProductSources(
            research=research,
            intake=ResearchIntakeCompiler(transport=transport),
        )
    )

    intake = service.research_follow_up_question(
        question="Assembly only; keep the same period.",
        catalog=catalog(),
        prior_session_id=session_v1.session_id,
        principal=principal(),
    )
    assert intake.brief is not None
    assert intake.scope_contract is not None
    assert intake.brief.scope.scope_version.version_id == "scope_v2"
    assert intake.brief.scope.scope_version.parent_version_id == "scope_v1"

    session_v2 = research.start_from_brief(
        brief=intake.brief,
        request_ref="scope-turn-2",
        source_message_hash="b" * 64,
        principal=principal(),
        prior_session_id=session_v1.session_id,
    )
    assert session_v2.lineage_id == session_v1.lineage_id
    assert session_v2.authority_id != session_v1.authority_id
    assert session_v2.accepted_brief.scope.scope_version.version_id == "scope_v2"

    restarted = ResearchSessionStore(db)
    old = restarted.load(
        session_v1.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    current = restarted.load(
        session_v2.session_id,
        tenant=f"id:{TENANT}",
        principal=str(USER),
    )
    assert old.accepted_brief == brief_v1
    assert old.accepted_brief.scope.scope_version.version_id == "scope_v1"
    assert current.accepted_brief.scope.scope_version.version_id == "scope_v2"
    assert current.lineage_id == old.lineage_id


def test_scope_v1_evidence_cannot_satisfy_scope_v2_obligation():
    db = db_engine()
    store, research, _, session_v1 = start_v1(db)
    compiler = ResearchIntakeCompiler(transport=FakeTransport(narrowed_payload()))
    brief_v2 = compiler.compile(
        question="Assembly only.",
        catalog=catalog(),
        prior_brief=session_v1.accepted_brief,
    ).brief
    session_v2 = research.start_from_brief(
        brief=brief_v2,
        request_ref="scope-turn-2-evidence",
        source_message_hash="c" * 64,
        principal=principal(),
        prior_session_id=session_v1.session_id,
    )
    old_obligation = session_v1.obligations[0].obligation_id
    new_obligation = session_v2.obligations[0].obligation_id
    receipt = DimaQueryReceipt(
        receipt_id="dqr_" + "1" * 24,
        receipt_fingerprint="1" * 64,
        execution_id="native:old-scope",
        step_role="primary",
        authority_kind="research_material",
        authority_id=session_v1.authority_id,
        obligation_ids=(old_obligation,),
        tenant_id=session_v1.tenant_binding,
        principal_id=session_v1.principal_subject,
        research_session_id=session_v1.session_id,
        native_subject_ref="metabase-user:1",
        native_conversation_id=UUID("00000000-0000-4000-8000-00000000b211"),
        native_query_id="old-scope-query",
        native_query_provenance_ref="old:query",
        native_result_provenance_ref="old:result",
        canonical_query_fingerprint="2" * 64,
        principal_fingerprint="3" * 64,
        semantic_context_version=session_v1.context_version,
        substrate="metabase-native",
        executed_at=NOW,
        result_hash="4" * 64,
        row_count=1,
    )
    evidence = EvidenceArtifact(
        artifact_id="evi_" + "5" * 24,
        authority_id=session_v1.authority_id,
        obligation_ids=(old_obligation,),
        query_receipt_refs=(receipt.receipt_id,),
        evidence_kind="native_result",
        state=EvidenceState.VERIFIED,
    )
    with pytest.raises(ResearchStateError) as exc:
        ResearchManager.admit_receipted_evidence(
            session_v2,
            obligation_id=new_obligation,
            receipt=receipt,
            evidence=evidence,
            satisfies_obligation=True,
        )
    assert exc.value.code == "P14_EVIDENCE_SESSION_AUTHORITY_MISMATCH"


def test_scope_v1_claim_cannot_ground_scope_v2_p19_candidate():
    db = db_engine()
    store, research, _, session_v1 = start_v1(db)
    session_v1 = verify_without_evidence(store, session_v1)
    claims = ClaimLineageStore(research_store=store, db_engine=db)
    old_claim = claims.create_claim(
        session_id=session_v1.session_id,
        obligation_id=session_v1.obligations[0].obligation_id,
        principal=principal(),
        claim_text="Old-scope candidate explanation.",
        proposition={"mechanism": "old-scope"},
        scope={"department": ["Assembly", "Paint"]},
        freshness=ClaimFreshness(as_of=NOW),
    )

    brief_v2 = ResearchIntakeCompiler(
        transport=FakeTransport(narrowed_payload())
    ).compile(
        question="Assembly only.",
        catalog=catalog(),
        prior_brief=session_v1.accepted_brief,
    ).brief
    session_v2 = research.start_from_brief(
        brief=brief_v2,
        request_ref="scope-turn-2-claim",
        source_message_hash="d" * 64,
        principal=principal(),
        prior_session_id=session_v1.session_id,
    )
    p19 = HypothesisRootCauseStore(research_store=store, db_engine=db)
    hypothesis = p19.create_hypothesis(
        research_session_id=session_v2.session_id,
        obligation_id=session_v2.obligations[0].obligation_id,
        statement="Current-scope candidate.",
        principal=principal(),
        now=NOW,
    )
    with pytest.raises(P19EpistemicError) as exc:
        p19.create_grounding(
            hypothesis_id=hypothesis.hypothesis_id,
            source_kind=GroundingSourceKind.P16_CLAIM,
            source_ref=old_claim.claim_id,
            relation=GroundingRelation.SUPPORTS,
            principal=principal(),
            now=NOW,
        )
    assert exc.value.code == "P19_CLAIM_SOURCE_SCOPE_MISMATCH"


@pytest.mark.parametrize(
    ("kind", "old_refs", "new_refs", "old_time", "new_time"),
    [
        (ScopeMutationKind.ADD, (METRIC, DIM), (METRIC, DIM, ASSEMBLY), ("H1",), ("H1",)),
        (ScopeMutationKind.REMOVE, (METRIC, DIM, ASSEMBLY), (METRIC, DIM), ("H1",), ("H1",)),
        (ScopeMutationKind.REPLACE, (METRIC, DIM), (METRIC_2, DIM_2), ("H1",), ("H2",)),
        (ScopeMutationKind.NARROW_ENTITY, (METRIC, DIM, ASSEMBLY, PAINT), (METRIC, DIM, ASSEMBLY), ("H1",), ("H1",)),
        (ScopeMutationKind.EXPAND_ENTITY, (METRIC, DIM, ASSEMBLY), (METRIC, DIM, ASSEMBLY, PAINT), ("H1",), ("H1",)),
        (ScopeMutationKind.CHANGE_PERIOD, (METRIC, DIM), (METRIC, DIM), ("H1",), ("H2",)),
        (ScopeMutationKind.CHANGE_METRIC, (METRIC, DIM), (METRIC_2, DIM), ("H1",), ("H1",)),
        (ScopeMutationKind.CHANGE_BREAKDOWN, (METRIC, DIM), (METRIC, DIM_2), ("H1",), ("H1",)),
        (ScopeMutationKind.RESET, (METRIC, DIM, ASSEMBLY), (METRIC_2, DIM_2), ("H1",), ()),
    ],
)
def test_all_roadmap_scope_mutations_are_semantically_validated(
    kind, old_refs, new_refs, old_time, new_time
):
    current = ResearchScope(
        semantic_refs=old_refs,
        time_surfaces=old_time,
    )
    contract = apply_scope_mutation(
        current,
        ScopeMutation(
            kind=kind,
            source_version_id="scope_v1",
            target_semantic_refs=new_refs,
            target_time_surfaces=new_time,
            reason=f"typed {kind.value} mutation",
        ),
    )
    assert contract.current_scope.scope_version.version_id == "scope_v2"
    assert contract.current_scope.scope_version.parent_version_id == "scope_v1"


def test_stale_scope_v1_cannot_be_reused_after_scope_v2_is_persisted():
    db = db_engine()
    _, research, _, session_v1 = start_v1(db)
    brief_v2 = ResearchIntakeCompiler(
        transport=FakeTransport(narrowed_payload())
    ).compile(
        question="Assembly only.",
        catalog=catalog(),
        prior_brief=session_v1.accepted_brief,
    ).brief
    session_v2 = research.start_from_brief(
        brief=brief_v2,
        request_ref="scope-turn-2-stale",
        source_message_hash="e" * 64,
        principal=principal(),
        prior_session_id=session_v1.session_id,
    )
    assert research.current_scope_state(
        session_id=session_v2.session_id,
        principal=principal(),
    ).session_id == session_v2.session_id

    with pytest.raises(ResearchPersistenceError) as exc:
        research.current_scope_state(
            session_id=session_v1.session_id,
            principal=principal(),
        )
    assert exc.value.code == "P14_RESEARCH_SCOPE_SUPERSEDED"

    transport = FakeTransport(narrowed_payload())
    service = HeadlessProductService(
        sources=ProductSources(
            research=research,
            intake=ResearchIntakeCompiler(transport=transport),
        )
    )
    with pytest.raises(Exception):
        service.research_follow_up_question(
            question="Try to branch from stale scope_v1.",
            catalog=catalog(),
            prior_session_id=session_v1.session_id,
            principal=principal(),
        )
    assert transport.call_count == 0


def test_scope_v1_material_cannot_become_scope_v2_report_evidence():
    db = db_engine()
    store, research, _, session_v1 = start_v1(db)
    old_ref = EvidenceRef(
        evidence_id="evi_" + "a" * 24,
        receipt_id="dqr_" + "b" * 24,
        authority_id=session_v1.authority_id,
        obligation_id=session_v1.obligations[0].obligation_id,
    )
    v1_obligation = session_v1.obligations[0].model_copy(
        update={
            "state": ObligationState.VERIFIED,
            "evidence_refs": (old_ref.evidence_id,),
        }
    )
    session_v1 = ResearchManager.advance(
        session_v1,
        obligations=(v1_obligation,),
        evidence_refs=(old_ref,),
        now=NOW,
    )
    session_v1 = store.save(
        session_v1,
        expected_revision=session_v1.revision - 1,
    )

    brief_v2 = ResearchIntakeCompiler(
        transport=FakeTransport(narrowed_payload())
    ).compile(
        question="Assembly only.",
        catalog=catalog(),
        prior_brief=session_v1.accepted_brief,
    ).brief
    session_v2 = research.start_from_brief(
        brief=brief_v2,
        request_ref="scope-turn-2-report",
        source_message_hash="f" * 64,
        principal=principal(),
        prior_session_id=session_v1.session_id,
    )
    session_v2 = verify_without_evidence(store, session_v2)

    reports = ReportDocumentStore(research_store=store, db_engine=db)
    draft = reports.draft_from_governed_research(
        research_session_id=session_v2.session_id,
        report_key="scope-v2-report",
        principal=principal(),
    )
    assert draft.statements == ()
    assert draft.coverage[0].coverage_status == CoverageStatus.LIMITED
    assert draft.limitations[0].code == "P20_NO_GOVERNED_PUBLISHABLE_FACT"
    assert old_ref.evidence_id not in {
        ref.source_ref
        for statement in draft.statements
        for ref in statement.source_refs
    }
