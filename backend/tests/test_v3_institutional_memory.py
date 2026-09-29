from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.v3.core_a.action_work import ActionWorkCurrentness, ActionWorkError
from app.v3.core_a.institutional_memory import (
    InstitutionalMemoryDraft,
    InstitutionalMemoryStore,
    MemoryCurrentness,
    MemoryError,
    MemoryRole,
    MemorySourceKind,
    MemorySourceRef,
)
from app.v3.core_a.outcome_observation import OutcomeCurrentness, OutcomeError
from control_plane.authorize import Principal, permissions_for
from control_plane.models import InstitutionalMemoryEntryRecord

TENANT = UUID("00000000-0000-4000-8000-000000006301")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000006302")
USER = UUID("00000000-0000-4000-8000-000000006303")
STAMP = datetime(2026, 9, 26, 8, 30, tzinfo=timezone.utc)

WORK_ID = "wrk_" + "a" * 24
WORK_FP = "b" * 64
OUTCOME_ID = "out_" + "c" * 24
OUTCOME_FP = "d" * 64


def db_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal(role="analyst", *, tenant=TENANT):
    return Principal(
        user_id=str(USER),
        tenant_id=str(tenant),
        tenant_slug="core-a-memory",
        roles=[role],
    )


class FakeWorkStore:
    def __init__(self, state=ActionWorkCurrentness.CURRENT):
        self.state = state

    def load(self, *, action_work_id, principal):
        if action_work_id != WORK_ID or f"id:{principal.tenant_id}" != f"id:{TENANT}":
            raise ActionWorkError("WORK_UNAVAILABLE", "unavailable")
        return SimpleNamespace(
            action_work_id=WORK_ID,
            work_fingerprint=WORK_FP,
            tenant_binding=f"id:{TENANT}",
        )

    def currentness(self, *, action_work_id, principal):
        self.load(action_work_id=action_work_id, principal=principal)
        return self.state


class FakeOutcomeStore:
    def __init__(self, state=OutcomeCurrentness.CURRENT):
        self.state = state

    def load(self, *, outcome_id, principal):
        if outcome_id != OUTCOME_ID or f"id:{principal.tenant_id}" != f"id:{TENANT}":
            raise OutcomeError("OUTCOME_UNAVAILABLE", "unavailable")
        return SimpleNamespace(
            outcome_id=OUTCOME_ID,
            outcome_fingerprint=OUTCOME_FP,
            tenant_binding=f"id:{TENANT}",
        )

    def currentness(self, *, outcome_id, principal):
        self.load(outcome_id=outcome_id, principal=principal)
        return self.state


def source_refs():
    return (
        MemorySourceRef(
            kind=MemorySourceKind.ACTION_WORK,
            artifact_id=WORK_ID,
            artifact_fingerprint=WORK_FP,
        ),
        MemorySourceRef(
            kind=MemorySourceKind.OUTCOME,
            artifact_id=OUTCOME_ID,
            artifact_fingerprint=OUTCOME_FP,
        ),
    )


def draft(*, role=MemoryRole.CURRENT_CONTEXT, **overrides):
    data = {
        "role": role,
        "problem_type": "collections-delay",
        "domain": "finance",
        "entity_refs": ("customer:42",),
        "metric_refs": ("metric:dso",),
        "source_refs": source_refs(),
        "summary": "Prior governed work and Outcome are relevant precedent.",
        "limitations": ("Summary is explanatory; exact sources remain authority.",),
        "precedent_of_memory_id": None,
    }
    data.update(overrides)
    return InstitutionalMemoryDraft(**data)


def make_store(db, *, work_state=ActionWorkCurrentness.CURRENT, outcome_state=OutcomeCurrentness.CURRENT):
    SQLModel.metadata.create_all(db)
    return InstitutionalMemoryStore(
        work_store=FakeWorkStore(work_state),
        outcome_store=FakeOutcomeStore(outcome_state),
        db_engine=db,
    )


def test_memory_permissions_are_read_viewer_write_analyst():
    assert "memory:read" in permissions_for(principal("viewer"))
    assert "memory:write" not in permissions_for(principal("viewer"))
    assert "memory:write" in permissions_for(principal("analyst"))


def test_memory_requires_at_least_one_traceable_source():
    raw = draft().model_dump(mode="json")
    raw["source_refs"] = []
    with pytest.raises(ValidationError):
        InstitutionalMemoryDraft.model_validate(raw)


def test_index_preserves_exact_source_identity():
    db = db_engine()
    store = make_store(db)
    entry = store.index(draft=draft(), principal=principal(), now=STAMP)
    assert entry.source_refs == source_refs()
    assert entry.role == MemoryRole.CURRENT_CONTEXT
    assert (
        store.currentness(memory_id=entry.memory_id, principal=principal())
        == MemoryCurrentness.CURRENT_CONTEXT
    )


def test_source_fingerprint_mismatch_rejects():
    db = db_engine()
    store = make_store(db)
    bad = list(source_refs())
    bad[0] = bad[0].model_copy(update={"artifact_fingerprint": "9" * 64})
    with pytest.raises(MemoryError) as exc:
        store.index(
            draft=draft(source_refs=tuple(bad)),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "MEMORY_SOURCE_FINGERPRINT_MISMATCH"


def test_historical_precedent_remains_historical_when_source_later_stale():
    db = db_engine()
    store = make_store(
        db,
        work_state=ActionWorkCurrentness.SOURCE_ADOPTION_STALE,
        outcome_state=OutcomeCurrentness.SOURCE_EVIDENCE_STALE,
    )
    entry = store.index(
        draft=draft(role=MemoryRole.HISTORICAL_PRECEDENT),
        principal=principal(),
        now=STAMP,
    )
    assert (
        store.currentness(memory_id=entry.memory_id, principal=principal())
        == MemoryCurrentness.HISTORICAL_PRECEDENT
    )


def test_current_context_exposes_stale_source():
    db = db_engine()
    store = make_store(
        db,
        outcome_state=OutcomeCurrentness.SOURCE_EVIDENCE_STALE,
    )
    entry = store.index(draft=draft(), principal=principal(), now=STAMP)
    assert (
        store.currentness(memory_id=entry.memory_id, principal=principal())
        == MemoryCurrentness.STALE_CONTEXT
    )


def test_summary_cannot_add_untraceable_truth_fields():
    raw = draft().model_dump(mode="json")
    raw["facts"] = [{"claim": "new ungoverned fact"}]
    with pytest.raises(ValidationError):
        InstitutionalMemoryDraft.model_validate(raw)


def test_indexing_is_idempotent():
    db = db_engine()
    store = make_store(db)
    first = store.index(draft=draft(), principal=principal(), now=STAMP)
    retry = store.index(
        draft=draft(),
        principal=principal(),
        now=STAMP + timedelta(days=10),
    )
    assert retry.memory_id == first.memory_id
    assert retry.created_at == first.created_at
    with Session(db) as session:
        assert len(session.exec(select(InstitutionalMemoryEntryRecord)).all()) == 1


def test_restart_persistence():
    db = db_engine()
    store = make_store(db)
    entry = store.index(draft=draft(), principal=principal(), now=STAMP)
    restarted = make_store(db)
    loaded = restarted.load(memory_id=entry.memory_id, principal=principal())
    assert loaded.memory_fingerprint == entry.memory_fingerprint


def test_cross_tenant_memory_is_non_oracle():
    db = db_engine()
    store = make_store(db)
    entry = store.index(draft=draft(), principal=principal(), now=STAMP)
    with pytest.raises(MemoryError) as foreign:
        store.load(memory_id=entry.memory_id, principal=principal(tenant=OTHER_TENANT))
    with pytest.raises(MemoryError) as missing:
        store.load(memory_id="mem_" + "0" * 24, principal=principal())
    assert foreign.value.code == missing.value.code == "MEMORY_UNAVAILABLE"


def test_exact_context_listing_is_deterministic():
    db = db_engine()
    store = make_store(db)
    entry = store.index(draft=draft(), principal=principal(), now=STAMP)
    rows = store.list_context(
        principal=principal(),
        domain="finance",
        problem_type="collections-delay",
        limit=10,
        offset=0,
    )
    assert [item.memory_id for item in rows] == [entry.memory_id]
    assert store.list_context(
        principal=principal(),
        domain="manufacturing",
    ) == ()


def test_memory_retrieval_never_mutates_sources():
    work_store = FakeWorkStore()
    outcome_store = FakeOutcomeStore()
    db = db_engine()
    SQLModel.metadata.create_all(db)
    store = InstitutionalMemoryStore(
        work_store=work_store,
        outcome_store=outcome_store,
        db_engine=db,
    )
    before = (work_store.state, outcome_store.state)
    entry = store.index(draft=draft(), principal=principal(), now=STAMP)
    store.load(memory_id=entry.memory_id, principal=principal())
    store.currentness(memory_id=entry.memory_id, principal=principal())
    store.list_context(principal=principal())
    assert (work_store.state, outcome_store.state) == before


def test_memory_owner_has_no_truth_creation_analytics_or_execution():
    source = Path("app/v3/core_a/institutional_memory.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    forbidden = (
        "httpx",
        "requests",
        "urllib",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
        "app.v3.substrate.metabase",
        "app.v3.action_connectors",
    )
    assert not any(name.startswith(forbidden) for name in imports)
    for token in (
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
        "RootCauseAssessment(",
        "ReportDocumentRecord(",
        "DecisionBriefRecord(",
        "OutcomeObservationRecord(",
        "action:execute",
    ):
        assert token not in source
