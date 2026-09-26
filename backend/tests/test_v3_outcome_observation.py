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

from app.v3.core_a.action_work import (
    ActionWorkCurrentness,
    ActionWorkError,
    ActionWorkStatus,
)
from app.v3.core_a.outcome_observation import (
    GovernedEvidenceRef,
    OutcomeClassification,
    OutcomeCurrentness,
    OutcomeError,
    OutcomeObservationDraft,
    OutcomeObservationStore,
)
from control_plane.authorize import Principal, permissions_for
from control_plane.models import (
    ClaimEvidenceLinkRecord,
    OutcomeObservationRecord,
    ResearchClaimRecord,
    RootCauseAssessment,
)

TENANT = UUID("00000000-0000-4000-8000-000000006201")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000006202")
USER = UUID("00000000-0000-4000-8000-000000006203")
STAMP = datetime(2026, 9, 26, 8, 0, tzinfo=timezone.utc)


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
        tenant_slug="core-a-outcome",
        roles=[role],
    )


def work(*, status=ActionWorkStatus.COMPLETED, fingerprint="a" * 64):
    return SimpleNamespace(
        action_work_id="wrk_" + "b" * 24,
        work_fingerprint=fingerprint,
        status=status,
        tenant_binding=f"id:{TENANT}",
        decision_brief_id="p21b_" + "c" * 24,
        decision_adoption_id="adp_" + "d" * 24,
    )


class FakeWorkStore:
    def __init__(
        self,
        item,
        state=ActionWorkCurrentness.CURRENT,
    ):
        self.item = item
        self.state = state

    def load(self, *, action_work_id, principal):
        if (
            action_work_id != self.item.action_work_id
            or self.item.tenant_binding != f"id:{principal.tenant_id}"
        ):
            raise ActionWorkError("WORK_UNAVAILABLE", "unavailable")
        return self.item

    def currentness(self, *, action_work_id, principal):
        self.load(action_work_id=action_work_id, principal=principal)
        return self.state


class FakeResearchStore:
    def __init__(self, *, evidence_id=None, receipt_id=None, stale=False):
        self.evidence_id = evidence_id or ("evi_" + "e" * 24)
        self.receipt_id = receipt_id or ("dqr_" + "f" * 24)
        self.stale = stale

    def load(self, session_id, *, tenant, principal):
        if self.stale or tenant != f"id:{TENANT}" or principal != str(USER):
            from app.v3.research_store import ResearchPersistenceError
            raise ResearchPersistenceError("P14_SESSION_NOT_FOUND", "unavailable")
        return SimpleNamespace(session_id=session_id)

    def verified_link(self, *, session_id, obligation_id):
        if self.stale:
            from app.v3.research_store import ResearchPersistenceError
            raise ResearchPersistenceError("P15_VERIFIED_NATIVE_OCCURRENCE_REQUIRED", "stale")
        return SimpleNamespace(
            id=UUID("00000000-0000-4000-8000-000000006204"),
            evidence_id=self.evidence_id,
            receipt_id=self.receipt_id,
            native_query_fingerprint="1" * 64,
            native_result_hash="2" * 64,
        )


def evidence():
    return GovernedEvidenceRef(
        research_session_id="rs_" + "3" * 24,
        obligation_id="must-1",
        evidence_id="evi_" + "e" * 24,
        receipt_id="dqr_" + "f" * 24,
    )


def draft(item=None, **overrides):
    item = item or work()
    data = {
        "action_work_id": item.action_work_id,
        "action_work_fingerprint": item.work_fingerprint,
        "evidence": (evidence(),),
        "claim_ids": (),
        "report_id": None,
        "baseline_definition": "Governed collections baseline reference.",
        "baseline_window": "baseline-window:v1",
        "observation_window": "observation-window:v1",
        "expected_target_ref": "target://collections-policy/v1",
        "observed_result_refs": ("metric-result://native/42",),
        "limitations": ("Association only; no causal attribution.",),
        "classification": OutcomeClassification.IMPROVED,
    }
    data.update(overrides)
    return OutcomeObservationDraft(**data)


def make_store(db, *, item=None, work_state=ActionWorkCurrentness.CURRENT, research=None):
    SQLModel.metadata.create_all(db)
    item = item or work()
    return (
        OutcomeObservationStore(
            work_store=FakeWorkStore(item, work_state),
            research_store=research or FakeResearchStore(),
            db_engine=db,
        ),
        item,
    )


def test_analyst_plus_can_record_outcome():
    assert "outcome:record" not in permissions_for(principal("viewer"))
    assert "outcome:record" in permissions_for(principal("analyst"))
    assert "outcome:record" in permissions_for(principal("admin"))


def test_exact_verified_evidence_provenance_is_required():
    db = db_engine()
    store, item = make_store(db)
    observed = store.record(
        draft=draft(item),
        principal=principal(),
        now=STAMP,
    )
    assert observed.classification == OutcomeClassification.IMPROVED
    assert observed.evidence[0].evidence_id == "evi_" + "e" * 24
    assert observed.observed_result_refs == ("metric-result://native/42",)


def test_evidence_mismatch_rejects():
    db = db_engine()
    research = FakeResearchStore(evidence_id="evi_" + "9" * 24)
    store, item = make_store(db, research=research)
    with pytest.raises(OutcomeError) as exc:
        store.record(draft=draft(item), principal=principal(), now=STAMP)
    assert exc.value.code == "OUTCOME_EVIDENCE_PROVENANCE_MISMATCH"


def test_invented_numeric_truth_fields_are_rejected_by_contract():
    raw = draft().model_dump(mode="json")
    raw["effect_size"] = 0.42
    with pytest.raises(ValidationError):
        OutcomeObservationDraft.model_validate(raw)
    raw = draft().model_dump(mode="json")
    raw["roi"] = 3.1
    with pytest.raises(ValidationError):
        OutcomeObservationDraft.model_validate(raw)


@pytest.mark.parametrize(
    "classification",
    [
        OutcomeClassification.IMPROVED,
        OutcomeClassification.MIXED,
        OutcomeClassification.WORSENED,
        OutcomeClassification.NO_MATERIAL_CHANGE,
        OutcomeClassification.INCONCLUSIVE,
    ],
)
def test_typed_classification_is_preserved_without_causal_promotion(classification):
    db = db_engine()
    store, item = make_store(db)
    observed = store.record(
        draft=draft(item, classification=classification),
        principal=principal(),
        now=STAMP,
    )
    assert observed.classification == classification
    assert not hasattr(observed, "caused_by_action")
    assert not hasattr(observed, "effect_size")


def test_source_work_must_be_completed():
    db = db_engine()
    item = work(status=ActionWorkStatus.IN_PROGRESS)
    store, item = make_store(db, item=item)
    with pytest.raises(OutcomeError) as exc:
        store.record(draft=draft(item), principal=principal(), now=STAMP)
    assert exc.value.code == "OUTCOME_SOURCE_WORK_NOT_COMPLETED"


def test_stale_source_work_rejects_new_observation():
    db = db_engine()
    store, item = make_store(
        db,
        work_state=ActionWorkCurrentness.SOURCE_ADOPTION_STALE,
    )
    with pytest.raises(OutcomeError) as exc:
        store.record(draft=draft(item), principal=principal(), now=STAMP)
    assert exc.value.code == "OUTCOME_SOURCE_WORK_STALE"


def test_stale_evidence_is_visible_after_record():
    db = db_engine()
    research = FakeResearchStore()
    store, item = make_store(db, research=research)
    observed = store.record(
        draft=draft(item),
        principal=principal(),
        now=STAMP,
    )
    research.stale = True
    assert (
        store.currentness(outcome_id=observed.outcome_id, principal=principal())
        == OutcomeCurrentness.SOURCE_EVIDENCE_STALE
    )


def test_same_observation_is_idempotent():
    db = db_engine()
    store, item = make_store(db)
    first = store.record(draft=draft(item), principal=principal(), now=STAMP)
    retry = store.record(
        draft=draft(item),
        principal=principal(),
        now=STAMP + timedelta(hours=2),
    )
    assert retry.outcome_id == first.outcome_id
    assert retry.observed_at == first.observed_at
    with Session(db) as session:
        assert len(session.exec(select(OutcomeObservationRecord)).all()) == 1


def test_historical_observation_is_immutable():
    db = db_engine()
    store, item = make_store(db)
    first = store.record(draft=draft(item), principal=principal(), now=STAMP)
    second = store.record(
        draft=draft(
            item,
            classification=OutcomeClassification.INCONCLUSIVE,
            limitations=("Later governed observation is inconclusive.",),
        ),
        principal=principal(),
        now=STAMP + timedelta(days=1),
    )
    assert first.outcome_id != second.outcome_id
    assert store.load(outcome_id=first.outcome_id, principal=principal()).classification == OutcomeClassification.IMPROVED


def test_cross_tenant_outcome_is_non_oracle():
    db = db_engine()
    store, item = make_store(db)
    observed = store.record(draft=draft(item), principal=principal(), now=STAMP)
    with pytest.raises(OutcomeError) as foreign:
        store.load(outcome_id=observed.outcome_id, principal=principal(tenant=OTHER_TENANT))
    with pytest.raises(OutcomeError) as missing:
        store.load(outcome_id="out_" + "0" * 24, principal=principal())
    assert foreign.value.code == missing.value.code == "OUTCOME_UNAVAILABLE"


def test_outcome_does_not_write_claim_evidence_or_p19_authority():
    db = db_engine()
    store, item = make_store(db)
    with Session(db) as session:
        before = {
            model.__name__: len(session.exec(select(model)).all())
            for model in (ResearchClaimRecord, ClaimEvidenceLinkRecord, RootCauseAssessment)
        }
    store.record(draft=draft(item), principal=principal(), now=STAMP)
    with Session(db) as session:
        after = {
            model.__name__: len(session.exec(select(model)).all())
            for model in (ResearchClaimRecord, ClaimEvidenceLinkRecord, RootCauseAssessment)
        }
    assert before == after


def test_outcome_owner_has_no_analytics_or_execution_surface():
    source = Path("app/v3/core_a/outcome_observation.py").read_text(encoding="utf-8")
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
        "effect_size =",
        "roi =",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
        "RootCauseAssessment(",
    ):
        assert token not in source
