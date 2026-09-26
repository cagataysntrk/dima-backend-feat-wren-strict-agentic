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

from app.v3.core_a.action_work import ActionWorkError
from app.v3.core_a.institutional_memory import MemoryError
from app.v3.core_a.watch_signal import (
    SignalCurrentness,
    SignalEvidenceRef,
    SignalOccurrence,
    SignalSeverity,
    SignalStatus,
    WatchDraft,
    WatchKind,
    WatchSignalError,
    WatchSignalStore,
)
from app.v3.research_store import ResearchPersistenceError
from control_plane.authorize import Principal, permissions_for
from control_plane.models import SignalRecord, WatchRecord

TENANT = UUID("00000000-0000-4000-8000-000000006401")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000006402")
USER = UUID("00000000-0000-4000-8000-000000006403")
STAMP = datetime(2026, 9, 26, 9, 0, tzinfo=timezone.utc)
MEMORY_ID = "mem_" + "a" * 24
WORK_ID = "wrk_" + "b" * 24
RESEARCH_ID = "rs_" + "c" * 24


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
        tenant_slug="core-a-watch",
        roles=[role],
    )


class FakeResearchStore:
    def __init__(self, valid=True):
        self.valid = valid
        self.load_calls = 0

    def load(self, session_id, *, tenant, principal):
        self.load_calls += 1
        if (
            not self.valid
            or session_id != RESEARCH_ID
            or tenant != f"id:{TENANT}"
            or principal != str(USER)
        ):
            raise ResearchPersistenceError("P14_SESSION_NOT_FOUND", "unavailable")
        return SimpleNamespace(session_id=session_id)

    def verified_link(self, *, session_id, obligation_id):
        if not self.valid:
            raise ResearchPersistenceError("P15_VERIFIED_NATIVE_OCCURRENCE_REQUIRED", "unavailable")
        return SimpleNamespace(
            evidence_id="evi_" + "d" * 24,
            receipt_id="dqr_" + "e" * 24,
        )


class FakeMemoryStore:
    def load(self, *, memory_id, principal):
        if memory_id != MEMORY_ID or f"id:{principal.tenant_id}" != f"id:{TENANT}":
            raise MemoryError("MEMORY_UNAVAILABLE", "unavailable")
        return SimpleNamespace(memory_id=MEMORY_ID)


class FakeWorkStore:
    def load(self, *, action_work_id, principal):
        if action_work_id != WORK_ID or f"id:{principal.tenant_id}" != f"id:{TENANT}":
            raise ActionWorkError("WORK_UNAVAILABLE", "unavailable")
        return SimpleNamespace(action_work_id=WORK_ID)


def make_store(db, *, research=None, with_context=True):
    SQLModel.metadata.create_all(db)
    return WatchSignalStore(
        research_store=research,
        memory_store=FakeMemoryStore() if with_context else None,
        work_store=FakeWorkStore() if with_context else None,
        db_engine=db,
    )


def watch_draft(**overrides):
    data = {
        "kind": WatchKind.METRIC_THRESHOLD,
        "title": "Collections material-change watch",
        "source_contract_ref": "metabase-alert://collections/dso",
        "criterion_ref": "governed-threshold://collections/dso-v1",
        "entity_refs": ("company:demo",),
        "metric_refs": ("metric:dso",),
        "context_refs": ("decision-assumption:collections-v1",),
    }
    data.update(overrides)
    return WatchDraft(**data)


def evidence():
    return SignalEvidenceRef(
        research_session_id=RESEARCH_ID,
        obligation_id="must-1",
        evidence_id="evi_" + "d" * 24,
        receipt_id="dqr_" + "e" * 24,
    )


def occurrence(*, occurrence_id="occ-1", with_evidence=False, observed_at=STAMP):
    return SignalOccurrence(
        source_occurrence_id=occurrence_id,
        source_kind="METABASE_ALERT_OCCURRENCE",
        source_ref=f"metabase-alert-occurrence://{occurrence_id}",
        observed_at=observed_at,
        evidence=evidence() if with_evidence else None,
        entity_refs=("company:demo",),
        metric_refs=("metric:dso",),
    )


def test_watch_permission_is_analyst_plus():
    assert "watch:manage" not in permissions_for(principal("viewer"))
    assert "watch:manage" in permissions_for(principal("analyst"))


def test_watch_is_definition_only_and_idempotent():
    db = db_engine()
    store = make_store(db)
    first = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    retry = store.create_watch(
        draft=watch_draft(),
        principal=principal(),
        now=STAMP + timedelta(days=1),
    )
    assert retry.watch_id == first.watch_id
    with Session(db) as session:
        assert len(session.exec(select(WatchRecord)).all()) == 1


def test_watch_contract_cannot_accept_observed_metric_result():
    raw = watch_draft().model_dump(mode="json")
    raw["observed_value"] = 42.0
    with pytest.raises(ValidationError):
        WatchDraft.model_validate(raw)


def test_same_occurrence_dedupes():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    first = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.MATERIAL,
        business_significance="Collections assumption may require investigation.",
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    retry = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.MATERIAL,
        business_significance="Same source occurrence replayed.",
        principal=principal(),
        now=STAMP + timedelta(minutes=2),
    )
    assert retry.signal_id == first.signal_id
    with Session(db) as session:
        assert len(session.exec(select(SignalRecord)).all()) == 1


def test_new_occurrence_creates_new_signal():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    first = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(occurrence_id="occ-1"),
        severity=SignalSeverity.MATERIAL,
        business_significance="First occurrence.",
        principal=principal(),
        now=STAMP,
    )
    second = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(occurrence_id="occ-2", observed_at=STAMP + timedelta(hours=1)),
        severity=SignalSeverity.MATERIAL,
        business_significance="Second occurrence.",
        principal=principal(),
        now=STAMP + timedelta(hours=1),
    )
    assert first.signal_id != second.signal_id


def test_signal_can_bind_exact_governed_evidence():
    db = db_engine()
    research = FakeResearchStore()
    store = make_store(db, research=research)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    signal = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(with_evidence=True),
        severity=SignalSeverity.CRITICAL,
        business_significance="Verified analytical occurrence requires review.",
        principal=principal(),
        now=STAMP,
    )
    assert signal.evidence == evidence()


def test_signal_can_attach_memory_and_existing_action_work_context():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    signal = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.INFO,
        business_significance="Existing work and precedent provide context.",
        memory_entry_id=MEMORY_ID,
        action_work_id=WORK_ID,
        principal=principal(),
        now=STAMP,
    )
    assert signal.memory_entry_id == MEMORY_ID
    assert signal.action_work_id == WORK_ID


def test_investigating_links_existing_research_session_without_creating_one():
    db = db_engine()
    research = FakeResearchStore()
    store = make_store(db, research=research)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    signal = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.MATERIAL,
        business_significance="Open governed Research.",
        principal=principal(),
        now=STAMP,
    )
    investigating = store.transition(
        signal_id=signal.signal_id,
        to_status=SignalStatus.INVESTIGATING,
        research_session_id=RESEARCH_ID,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    assert investigating.research_session_id == RESEARCH_ID
    assert research.load_calls == 1


def test_investigating_requires_existing_research():
    db = db_engine()
    research = FakeResearchStore(valid=False)
    store = make_store(db, research=research)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    signal = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.MATERIAL,
        business_significance="Investigate.",
        principal=principal(),
        now=STAMP,
    )
    with pytest.raises(WatchSignalError) as exc:
        store.transition(
            signal_id=signal.signal_id,
            to_status=SignalStatus.INVESTIGATING,
            research_session_id=RESEARCH_ID,
            principal=principal(),
            now=STAMP + timedelta(minutes=1),
        )
    assert exc.value.code == "SIGNAL_RESEARCH_UNAVAILABLE"


def test_signal_lifecycle_is_append_only_and_resolved_requires_ref():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    new = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.INFO,
        business_significance="Acknowledge and resolve.",
        principal=principal(),
        now=STAMP,
    )
    ack = store.transition(
        signal_id=new.signal_id,
        to_status=SignalStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    with pytest.raises(WatchSignalError) as exc:
        store.transition(
            signal_id=ack.signal_id,
            to_status=SignalStatus.RESOLVED,
            principal=principal(),
            now=STAMP + timedelta(minutes=2),
        )
    assert exc.value.code == "SIGNAL_RESOLUTION_REQUIRED"
    resolved = store.transition(
        signal_id=ack.signal_id,
        to_status=SignalStatus.RESOLVED,
        resolution_ref="internal://resolution/42",
        principal=principal(),
        now=STAMP + timedelta(minutes=2),
    )
    assert resolved.status == SignalStatus.RESOLVED
    assert resolved.revision == 3
    assert store.load_signal(signal_id=new.signal_id, principal=principal()).status == SignalStatus.NEW


def test_same_transition_is_idempotent():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    new = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.INFO,
        business_significance="Acknowledge.",
        principal=principal(),
        now=STAMP,
    )
    first = store.transition(
        signal_id=new.signal_id,
        to_status=SignalStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    retry = store.transition(
        signal_id=new.signal_id,
        to_status=SignalStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=5),
    )
    assert retry.signal_id == first.signal_id


def test_superseded_signal_revision_is_visible():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    new = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.INFO,
        business_significance="Acknowledge.",
        principal=principal(),
        now=STAMP,
    )
    store.transition(
        signal_id=new.signal_id,
        to_status=SignalStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    assert store.currentness(signal_id=new.signal_id, principal=principal()) == SignalCurrentness.SUPERSEDED


def test_cross_tenant_watch_and_signal_are_non_oracle():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    signal = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.INFO,
        business_significance="Tenant proof.",
        principal=principal(),
        now=STAMP,
    )
    with pytest.raises(WatchSignalError) as foreign:
        store.load_signal(signal_id=signal.signal_id, principal=principal(tenant=OTHER_TENANT))
    with pytest.raises(WatchSignalError) as missing:
        store.load_signal(signal_id="sig_" + "0" * 24, principal=principal())
    assert foreign.value.code == missing.value.code == "SIGNAL_UNAVAILABLE"


def test_restart_persistence():
    db = db_engine()
    store = make_store(db)
    watch = store.create_watch(draft=watch_draft(), principal=principal(), now=STAMP)
    signal = store.observe(
        watch_id=watch.watch_id,
        occurrence=occurrence(),
        severity=SignalSeverity.MATERIAL,
        business_significance="Persist.",
        principal=principal(),
        now=STAMP,
    )
    restarted = make_store(db)
    assert restarted.load_watch(watch_id=watch.watch_id, principal=principal()).watch_fingerprint == watch.watch_fingerprint
    assert restarted.load_signal(signal_id=signal.signal_id, principal=principal()).signal_fingerprint == signal.signal_fingerprint


def test_watch_signal_owner_has_no_analytics_or_external_execution():
    source = Path("app/v3/core_a/watch_signal.py").read_text(encoding="utf-8")
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
        "action:execute",
        "forecast",
        "optimizer",
        "aggregate(",
        "variance",
        "mean(",
        "execute_query",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
    ):
        assert token not in source
