from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.authority import AcceptedResearchAuthority
from app.v3.research import ResearchManager
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
from app.v3.research_store import ResearchSessionStore


NOW = datetime(2026, 9, 27, 16, 30, tzinfo=timezone.utc)
TENANT = "00000000-0000-4000-8000-00000000a101"
USER = "scope-contract-user"


def sem(candidate_id, kind, name):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=candidate_id,
        target_kind=kind,
        canonical_name=name,
        cube_names=("operations",),
    )


METRIC = sem("metric_downtime", SemanticTargetKind.METRIC, "Downtime")
DIM = sem("dim_machine", SemanticTargetKind.DIMENSION, "Machine")
ASSEMBLY = sem("entity_assembly", SemanticTargetKind.ENTITY_VALUE, "Assembly")
PAINT = sem("entity_paint", SemanticTargetKind.ENTITY_VALUE, "Paint")


def make_brief(scope, brief_id):
    question = ResearchQuestion(
        goal_id="g_scope",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect downtime by machine.",
        subject_refs=(METRIC,),
        related_refs=(DIM,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id=brief_id,
        objective="Inspect governed downtime scope.",
        scope=scope,
        questions=(question,),
        must_requirement_ids=("g_scope",),
        context_version="ctx-scope-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def make_authority(brief):
    ordinal = brief.scope.scope_version.ordinal
    return AcceptedResearchAuthority(
        contract_id=f"ara-{brief.brief_id}",
        lineage_id="scope-lineage",
        version=ordinal,
        turn_id=f"turn-{ordinal}",
        request_ref=f"request-{ordinal}",
        source_message_hash="a" * 64,
        accepted_attempt_id=f"attempt-{ordinal}",
        model_role="research-intake",
        obligation_ids=brief.must_requirement_ids,
        context_version=brief.context_version,
        accepted_at_iso=NOW.isoformat(),
    )


def test_initial_scope_is_versioned():
    scope = ResearchScope(
        semantic_refs=(METRIC, DIM),
        time_surfaces=("2026-H1",),
    )
    assert scope.scope_version.version_id == "scope_v1"
    assert scope.scope_version.ordinal == 1
    assert scope.scope_version.parent_version_id is None


def test_narrow_entity_creates_scope_v2_and_preserves_v1():
    scope = ResearchScope(
        semantic_refs=(METRIC, DIM, ASSEMBLY, PAINT),
        time_surfaces=("2026-H1",),
    )
    contract = apply_scope_mutation(
        scope,
        ScopeMutation(
            kind=ScopeMutationKind.NARROW_ENTITY,
            source_version_id="scope_v1",
            target_semantic_refs=(METRIC, DIM, ASSEMBLY),
            target_time_surfaces=("2026-H1",),
            reason="Assembly only.",
        ),
    )
    assert scope.scope_version.version_id == "scope_v1"
    assert contract.current_scope.scope_version.version_id == "scope_v2"
    assert contract.current_scope.scope_version.parent_version_id == "scope_v1"
    assert PAINT in scope.semantic_refs
    assert PAINT not in contract.current_scope.semantic_refs


def test_change_period_cannot_smuggle_entity_change():
    scope = ResearchScope(
        semantic_refs=(METRIC, DIM),
        time_surfaces=("2026-H1",),
    )
    with pytest.raises(ValueError, match="CHANGE_PERIOD"):
        apply_scope_mutation(
            scope,
            ScopeMutation(
                kind=ScopeMutationKind.CHANGE_PERIOD,
                source_version_id="scope_v1",
                target_semantic_refs=(METRIC, DIM, ASSEMBLY),
                target_time_surfaces=("2026-H2",),
                reason="Invalid mixed mutation.",
            ),
        )


def test_stale_scope_mutation_is_rejected():
    scope = ResearchScope(
        semantic_refs=(METRIC, DIM),
        time_surfaces=("2026-H1",),
    )
    with pytest.raises(ValueError, match="another scope version"):
        apply_scope_mutation(
            scope,
            ScopeMutation(
                kind=ScopeMutationKind.CHANGE_PERIOD,
                source_version_id="scope_v2",
                target_semantic_refs=(METRIC, DIM),
                target_time_surfaces=("2026-H2",),
                reason="Stale request.",
            ),
        )


def test_scope_version_survives_restart_and_new_scope_starts_without_old_evidence():
    db = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(db)
    store = ResearchSessionStore(db)

    v1_scope = ResearchScope(
        semantic_refs=(METRIC, DIM, ASSEMBLY, PAINT),
        time_surfaces=("2026-H1",),
    )
    v1_brief = make_brief(v1_scope, "rb_scope_v1")
    v1 = ResearchManager.start(
        authority=make_authority(v1_brief),
        objective=v1_brief.objective,
        obligation_objectives={"g_scope": "Inspect downtime by machine."},
        tenant_binding=TENANT,
        principal_subject=USER,
        accepted_brief=v1_brief,
        now=NOW,
        session_id="rs_" + "1" * 24,
    )
    store.create(v1, delegatable_ids=("g_scope",))

    transition = apply_scope_mutation(
        v1_scope,
        ScopeMutation(
            kind=ScopeMutationKind.NARROW_ENTITY,
            source_version_id="scope_v1",
            target_semantic_refs=(METRIC, DIM, ASSEMBLY),
            target_time_surfaces=("2026-H1",),
            reason="Assembly only.",
        ),
    )
    v2_brief = make_brief(transition.current_scope, "rb_scope_v2")
    v2 = ResearchManager.start(
        authority=make_authority(v2_brief),
        objective=v2_brief.objective,
        obligation_objectives={"g_scope": "Inspect downtime by machine."},
        tenant_binding=TENANT,
        principal_subject=USER,
        accepted_brief=v2_brief,
        now=NOW,
        session_id="rs_" + "2" * 24,
    )
    store.create(v2, delegatable_ids=("g_scope",))

    restored_v1 = store.load(v1.session_id, tenant=TENANT, principal=USER)
    restored_v2 = store.load(v2.session_id, tenant=TENANT, principal=USER)
    assert restored_v1.accepted_brief.scope.scope_version.version_id == "scope_v1"
    assert restored_v2.accepted_brief.scope.scope_version.version_id == "scope_v2"
    assert restored_v2.accepted_brief.scope.scope_version.parent_version_id == "scope_v1"
    assert restored_v1.session_id != restored_v2.session_id
    assert restored_v2.evidence_refs == ()
    assert restored_v1.fingerprint != restored_v2.fingerprint
