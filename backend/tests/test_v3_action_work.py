from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.v3.core_a.action_work import (
    ActionWorkCurrentness,
    ActionWorkDraft,
    ActionWorkError,
    ActionWorkStatus,
    ActionWorkStore,
)
from app.v3.decision_adoption import (
    AdoptionCurrentness,
    AdoptionDisposition,
    AdoptionError,
    DecisionAdoption,
)
from control_plane.authorize import Principal, permissions_for
from control_plane.models import (
    ActionAuthorizationRecord,
    ActionWorkRecord,
    DecisionAdoptionRecord,
    DecisionBriefRecord,
)

TENANT = UUID("00000000-0000-4000-8000-000000006101")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000006102")
USER = UUID("00000000-0000-4000-8000-000000006103")
STAMP = datetime(2026, 9, 26, 7, 30, tzinfo=timezone.utc)


def db_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal(role="analyst", *, tenant=TENANT, user=USER):
    return Principal(
        user_id=str(user),
        tenant_id=str(tenant),
        tenant_slug="core-a",
        roles=[role],
    )


def adoption(*, disposition=AdoptionDisposition.ACCEPTED, tenant=TENANT):
    return DecisionAdoption(
        adoption_id="adp_" + "a" * 24,
        decision_brief_id="p21b_" + "b" * 24,
        source_brief_fingerprint="c" * 64,
        tenant_binding=f"id:{tenant}",
        actor_user_id=str(USER),
        actor_authorization_context={
            "user_id": str(USER),
            "tenant_binding": f"id:{tenant}",
            "roles": ["analyst"],
            "authorization_action": "decision:adopt",
        },
        disposition=disposition,
        selected_option_ids=("p21x_" + "d" * 24,),
        human_rationale="Committed by authenticated operator.",
        human_conditions=(),
        supersedes_adoption_id=None,
        recorded_at=STAMP - timedelta(minutes=10),
        adoption_fingerprint="e" * 64,
    )


class FakeAdoptionStore:
    def __init__(self, item, state=AdoptionCurrentness.CURRENT):
        self.item = item
        self.state = state

    def load(self, *, adoption_id, principal):
        if (
            adoption_id != self.item.adoption_id
            or self.item.tenant_binding != f"id:{principal.tenant_id}"
        ):
            raise AdoptionError("ADOPTION_UNAVAILABLE", "unavailable")
        return self.item

    def currentness(self, *, adoption_id, principal):
        self.load(adoption_id=adoption_id, principal=principal)
        return self.state


class FakeAuthorizationStore:
    def __init__(self, item):
        self.item = item

    def load(self, *, authorization_id, principal):
        if (
            authorization_id != self.item.authorization_id
            or self.item.tenant_binding != f"id:{principal.tenant_id}"
        ):
            raise RuntimeError("unavailable")
        return self.item


def make_store(
    db,
    *,
    disposition=AdoptionDisposition.ACCEPTED,
    state=AdoptionCurrentness.CURRENT,
    with_authorization=False,
):
    SQLModel.metadata.create_all(db)
    item = adoption(disposition=disposition)
    authz = None
    authz_store = None
    if with_authorization:
        authz = SimpleNamespace(
            authorization_id="authz_" + "f" * 24,
            authorization_fingerprint="1" * 64,
            tenant_binding=item.tenant_binding,
            decision_adoption_id=item.adoption_id,
            decision_adoption_fingerprint=item.adoption_fingerprint,
            decision_brief_id=item.decision_brief_id,
            decision_brief_fingerprint=item.source_brief_fingerprint,
        )
        authz_store = FakeAuthorizationStore(authz)
    return (
        ActionWorkStore(
            adoption_store=FakeAdoptionStore(item, state),
            authorization_store=authz_store,
            db_engine=db,
        ),
        item,
        authz,
    )


def draft(item, authz=None):
    return ActionWorkDraft(
        decision_adoption_id=item.adoption_id,
        decision_adoption_fingerprint=item.adoption_fingerprint,
        action_authorization_id=(
            authz.authorization_id if authz is not None else None
        ),
        action_authorization_fingerprint=(
            authz.authorization_fingerprint if authz is not None else None
        ),
        title="Reconcile overdue customer balances",
        work_intent={"kind": "internal_followup", "scope": "collections"},
        due_at=STAMP + timedelta(days=5),
    )


def test_analyst_plus_has_internal_work_permission():
    assert "work:manage" not in permissions_for(principal("viewer"))
    assert "work:manage" in permissions_for(principal("analyst"))
    assert "work:manage" in permissions_for(principal("admin"))


def test_legal_creation_binds_tenant_owner_and_decision_lineage():
    db = db_engine()
    store, item, _ = make_store(db)
    work = store.create(draft=draft(item), principal=principal(), now=STAMP)
    assert work.status == ActionWorkStatus.PLANNED
    assert work.tenant_binding == f"id:{TENANT}"
    assert work.owner_user_id == str(USER)
    assert work.decision_adoption_id == item.adoption_id
    assert work.decision_brief_id == item.decision_brief_id
    assert work.revision == 1
    assert len(work.transition_history) == 1


def test_optional_action_authorization_lineage_is_exact():
    db = db_engine()
    store, item, authz = make_store(db, with_authorization=True)
    work = store.create(
        draft=draft(item, authz),
        principal=principal(),
        now=STAMP,
    )
    assert work.action_authorization_id == authz.authorization_id
    assert (
        work.action_authorization_fingerprint
        == authz.authorization_fingerprint
    )


@pytest.mark.parametrize(
    "disposition",
    [AdoptionDisposition.REJECTED, AdoptionDisposition.DEFERRED],
)
def test_noncommitted_adoption_rejects(disposition):
    db = db_engine()
    store, item, _ = make_store(db, disposition=disposition)
    with pytest.raises(ActionWorkError) as exc:
        store.create(draft=draft(item), principal=principal(), now=STAMP)
    assert exc.value.code == "WORK_SOURCE_ADOPTION_NOT_COMMITTED"


def test_modified_adoption_can_create_internal_work_without_execution():
    db = db_engine()
    store, item, _ = make_store(
        db,
        disposition=AdoptionDisposition.MODIFIED,
    )
    work = store.create(draft=draft(item), principal=principal(), now=STAMP)
    assert work.status == ActionWorkStatus.PLANNED
    assert work.action_authorization_id is None


def test_stale_adoption_rejects_creation():
    db = db_engine()
    store, item, _ = make_store(
        db,
        state=AdoptionCurrentness.SOURCE_BRIEF_STALE,
    )
    with pytest.raises(ActionWorkError) as exc:
        store.create(draft=draft(item), principal=principal(), now=STAMP)
    assert exc.value.code == "WORK_SOURCE_ADOPTION_STALE"


def test_cross_tenant_is_non_oracle():
    db = db_engine()
    store, item, _ = make_store(db)
    work = store.create(draft=draft(item), principal=principal(), now=STAMP)
    with pytest.raises(ActionWorkError) as foreign:
        store.load(
            action_work_id=work.action_work_id,
            principal=principal(tenant=OTHER_TENANT),
        )
    with pytest.raises(ActionWorkError) as missing:
        store.load(
            action_work_id="wrk_" + "0" * 24,
            principal=principal(),
        )
    assert foreign.value.code == missing.value.code == "WORK_UNAVAILABLE"


def test_illegal_transition_rejects():
    db = db_engine()
    store, item, _ = make_store(db)
    work = store.create(draft=draft(item), principal=principal(), now=STAMP)
    with pytest.raises(ActionWorkError) as exc:
        store.transition(
            action_work_id=work.action_work_id,
            to_status=ActionWorkStatus.COMPLETED,
            completion_reference="done",
            principal=principal(),
            now=STAMP + timedelta(minutes=1),
        )
    assert exc.value.code == "WORK_ILLEGAL_TRANSITION"


def test_blocked_and_cancelled_transitions_are_legal_and_append_only():
    db = db_engine()
    store, item, _ = make_store(db)
    planned = store.create(draft=draft(item), principal=principal(), now=STAMP)
    ack = store.transition(
        action_work_id=planned.action_work_id,
        to_status=ActionWorkStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    blocked = store.transition(
        action_work_id=ack.action_work_id,
        to_status=ActionWorkStatus.BLOCKED,
        blocker_reason="Awaiting customer document.",
        principal=principal(),
        now=STAMP + timedelta(minutes=2),
    )
    cancelled = store.transition(
        action_work_id=blocked.action_work_id,
        to_status=ActionWorkStatus.CANCELLED,
        principal=principal(),
        now=STAMP + timedelta(minutes=3),
    )
    assert [x.to_status for x in cancelled.transition_history] == [
        ActionWorkStatus.PLANNED,
        ActionWorkStatus.ACKNOWLEDGED,
        ActionWorkStatus.BLOCKED,
        ActionWorkStatus.CANCELLED,
    ]
    assert planned.revision == 1
    assert cancelled.revision == 4
    assert store.load(
        action_work_id=planned.action_work_id,
        principal=principal(),
    ).status == ActionWorkStatus.PLANNED


def test_completed_transition_requires_internal_completion_reference():
    db = db_engine()
    store, item, _ = make_store(db)
    planned = store.create(draft=draft(item), principal=principal(), now=STAMP)
    ack = store.transition(
        action_work_id=planned.action_work_id,
        to_status=ActionWorkStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    progress = store.transition(
        action_work_id=ack.action_work_id,
        to_status=ActionWorkStatus.IN_PROGRESS,
        principal=principal(),
        now=STAMP + timedelta(minutes=2),
    )
    with pytest.raises(ActionWorkError) as exc:
        store.transition(
            action_work_id=progress.action_work_id,
            to_status=ActionWorkStatus.COMPLETED,
            principal=principal(),
            now=STAMP + timedelta(minutes=3),
        )
    assert exc.value.code == "WORK_COMPLETION_REFERENCE_REQUIRED"
    completed = store.transition(
        action_work_id=progress.action_work_id,
        to_status=ActionWorkStatus.COMPLETED,
        completion_reference="internal://work-proof/42",
        principal=principal(),
        now=STAMP + timedelta(minutes=3),
    )
    assert completed.status == ActionWorkStatus.COMPLETED
    assert completed.completion_reference == "internal://work-proof/42"


def test_same_transition_is_idempotent():
    db = db_engine()
    store, item, _ = make_store(db)
    planned = store.create(draft=draft(item), principal=principal(), now=STAMP)
    first = store.transition(
        action_work_id=planned.action_work_id,
        to_status=ActionWorkStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    retry = store.transition(
        action_work_id=planned.action_work_id,
        to_status=ActionWorkStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=10),
    )
    assert retry.action_work_id == first.action_work_id
    with Session(db) as session:
        rows = session.exec(select(ActionWorkRecord)).all()
    assert len(rows) == 2


def test_restart_persistence_and_currentness():
    db = db_engine()
    store, item, _ = make_store(db)
    planned = store.create(draft=draft(item), principal=principal(), now=STAMP)
    restarted = ActionWorkStore(
        adoption_store=FakeAdoptionStore(item),
        db_engine=db,
    )
    loaded = restarted.load(
        action_work_id=planned.action_work_id,
        principal=principal(),
    )
    assert loaded.work_fingerprint == planned.work_fingerprint
    assert (
        restarted.currentness(
            action_work_id=planned.action_work_id,
            principal=principal(),
        )
        == ActionWorkCurrentness.CURRENT
    )


def test_superseded_revision_is_visible_as_superseded():
    db = db_engine()
    store, item, _ = make_store(db)
    planned = store.create(draft=draft(item), principal=principal(), now=STAMP)
    store.transition(
        action_work_id=planned.action_work_id,
        to_status=ActionWorkStatus.ACKNOWLEDGED,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    assert (
        store.currentness(
            action_work_id=planned.action_work_id,
            principal=principal(),
        )
        == ActionWorkCurrentness.SUPERSEDED
    )


def test_sealed_upstream_tables_are_not_written():
    db = db_engine()
    store, item, _ = make_store(db)
    with Session(db) as session:
        before = {
            model.__name__: len(session.exec(select(model)).all())
            for model in (
                DecisionAdoptionRecord,
                DecisionBriefRecord,
                ActionAuthorizationRecord,
            )
        }
    store.create(draft=draft(item), principal=principal(), now=STAMP)
    with Session(db) as session:
        after = {
            model.__name__: len(session.exec(select(model)).all())
            for model in (
                DecisionAdoptionRecord,
                DecisionBriefRecord,
                ActionAuthorizationRecord,
            )
        }
    assert before == after


def test_action_work_owner_has_zero_external_side_effect_surface():
    source = Path("app/v3/core_a/action_work.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    forbidden = (
        "httpx",
        "requests",
        "urllib",
        "app.v3.action_connectors",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
    )
    assert not any(name.startswith(forbidden) for name in imports)
    for token in (
        "action:execute",
        "send_email",
        "webhook",
        "Slack",
        "erp_client",
        "DimaQueryReceipt(",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
    ):
        assert token not in source
