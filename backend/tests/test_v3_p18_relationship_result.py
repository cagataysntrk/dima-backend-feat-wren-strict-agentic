from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.v3.business_relationship_v1 import (
    RelationshipLayerState,
    RelationshipResultProjection,
    RelationshipResultStore,
    RelationshipResultStoreError,
    RelationshipTerminalDisposition,
)
from control_plane.authorize import Principal


SESSION_ID = "rs_" + "1" * 24
TENANT_ID = "00000000-0000-4000-8000-000000009911"
USER_ID = "00000000-0000-4000-8000-000000009912"


class FakeResearchStore:
    def __init__(self):
        self.session = SimpleNamespace(
            session_id=SESSION_ID,
            tenant_binding=f"id:{TENANT_ID}",
            principal_subject=USER_ID,
            context_version="ctx-p18-result",
            lineage_id="lineage-p18",
            accepted_brief=SimpleNamespace(
                scope=SimpleNamespace(
                    scope_version=SimpleNamespace(version_id="scope_v1")
                ),
                questions=(SimpleNamespace(goal_id="g_rel"),),
            ),
        )

    def load(self, session_id, *, tenant, principal):
        assert session_id == SESSION_ID
        if tenant != self.session.tenant_binding or principal != USER_ID:
            from app.v3.research_store import ResearchPersistenceError
            raise ResearchPersistenceError("TEST_SCOPE", "mismatch")
        return self.session


def _principal(tenant_id=TENANT_ID, user_id=USER_ID):
    return Principal(
        tenant_id=tenant_id,
        user_id=user_id,
        tenant_slug="p18-result",
        roles=["analyst"],
    )


def _projection(state=RelationshipLayerState.SUPPORTED):
    return RelationshipResultProjection(
        research_session_id=SESSION_ID,
        obligation_id="g_rel",
        claim_id="clm_" + "2" * 24,
        policy_use_id="bru_" + "3" * 24,
        scope_lineage_id="lineage-p18",
        scope_version_id="scope_v1",
        applicability_scope={"accepted_relationship_goal_id": "g_rel"},
        association_state=state,
        co_movement_state=RelationshipLayerState.NOT_ESTABLISHED,
        business_relationship_state=RelationshipLayerState.NOT_ESTABLISHED,
        policy_required=False,
        contextual_evidence_refs=("evi_" + "4" * 24,),
    )


def _store():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return RelationshipResultStore(
        research_store=FakeResearchStore(),
        db_engine=engine,
    )


def test_p18_result_seals_idempotent_terminal_artifact():
    store = _store()
    first = store.seal(
        projection=_projection(),
        principal=_principal(),
        now=datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc),
    )
    second = store.seal(
        projection=_projection(),
        principal=_principal(),
        now=datetime(2026, 10, 2, 10, 0, tzinfo=timezone.utc),
    )

    assert first.result_id == second.result_id
    assert first.disposition == RelationshipTerminalDisposition.FULFILLED
    assert first.projection == _projection()
    assert store.load(
        result_id=first.result_id,
        principal=_principal(),
    ) == first


def test_p18_result_marks_insufficient_observation_limited():
    artifact = _store().seal(
        projection=_projection(RelationshipLayerState.INSUFFICIENT),
        principal=_principal(),
    )
    assert artifact.disposition == RelationshipTerminalDisposition.LIMITED


def test_p18_result_is_tenant_scoped():
    store = _store()
    artifact = store.seal(
        projection=_projection(),
        principal=_principal(),
    )
    with pytest.raises(RelationshipResultStoreError, match="P18_RESULT_TENANT_MISMATCH"):
        store.load(
            result_id=artifact.result_id,
            principal=_principal(
                tenant_id="00000000-0000-4000-8000-000000009999"
            ),
        )
