from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.v3.decision_adoption import (
    AdoptionCurrentness,
    AdoptionDisposition,
    AdoptionError,
    DecisionAdoptionDraft,
    DecisionAdoptionStore,
)
from app.v3.decision_intelligence import (
    DecisionBrief,
    DecisionBriefCurrentness,
    DecisionConstraint,
    DecisionObjective,
    DecisionOption,
    DecisionPremiseRef,
    DecisionRecommendation,
    P21DecisionError,
)
from app.v3.report_document import ReportStatementKind
from control_plane.authorize import Principal, permissions_for
from control_plane.models import (
    BusinessRelationshipPolicyUseRecord,
    DecisionAdoptionRecord,
    DecisionBriefRecord,
    DecisionRecord,
    HypothesisGroundingLink,
    HypothesisRecord,
    ReportDocumentRecord,
    ResearchClaimRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
    ResearchReasoningStepRecord,
    ResearchSessionRecord,
    RootCauseAssessment,
)

TENANT = UUID("00000000-0000-4000-8000-000000005801")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000005802")
USER = UUID("00000000-0000-4000-8000-000000005803")
OTHER_USER = UUID("00000000-0000-4000-8000-000000005804")
STAMP = datetime(2026, 9, 26, 5, 40, tzinfo=timezone.utc)


def engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal(role: str = "analyst", *, user=USER, tenant=TENANT) -> Principal:
    return Principal(
        user_id=str(user),
        tenant_id=str(tenant),
        tenant_slug="adoption",
        roles=[role],
    )


def oid(ch: str) -> str:
    return "p21x_" + ch * 24


def make_brief(*, recommended=(oid("a"),), tenant=TENANT, fingerprint="b" * 64):
    premise = DecisionPremiseRef(
        premise_id="p21p_" + "c" * 24,
        statement_id="p20s_" + "d" * 24,
        statement_kind=ReportStatementKind.ANALYTICAL_FACT,
        upstream_epistemic_ceiling="SUPPORTED",
    )
    options = (
        DecisionOption(option_id=oid("a"), proposal_text="Option A"),
        DecisionOption(option_id=oid("b"), proposal_text="Option B"),
        DecisionOption(option_id=oid("c"), proposal_text="Option C"),
    )
    return DecisionBrief(
        decision_brief_id="p21b_" + "e" * 24,
        report_id="p20r_" + "f" * 24,
        tenant_binding=f"id:{tenant}",
        semantic_context_version="ctx-adoption-v1",
        brief_key="adoption-brief",
        revision=1,
        parent_decision_brief_id=None,
        objective=DecisionObjective(
            objective_id="p21o_" + "1" * 24,
            objective_text="Choose a governed option.",
        ),
        constraints=(
            DecisionConstraint(
                constraint_id="p21c_" + "2" * 24,
                source_kind="USER_DECLARED",
                text="Keep the decision reversible.",
            ),
        ),
        premises=(premise,),
        options=options,
        tradeoffs=(),
        assumptions=(),
        limitations=(),
        recommendation=DecisionRecommendation(
            recommended_option_ids=tuple(recommended),
            premise_refs=(premise.premise_id,),
        ),
        model_provenance=None,
        source_report_fingerprint="3" * 64,
        decision_source_fingerprint="4" * 64,
        brief_fingerprint=fingerprint,
        created_at=STAMP,
    )


class FakeDecisionStore:
    def __init__(self, brief: DecisionBrief, currentness=DecisionBriefCurrentness.CURRENT):
        self.brief = brief
        self.state = currentness

    def load(self, *, decision_brief_id: str, principal: Principal):
        if (
            decision_brief_id != self.brief.decision_brief_id
            or self.brief.tenant_binding != f"id:{principal.tenant_id}"
        ):
            raise P21DecisionError(
                "P21_DECISION_BRIEF_UNAVAILABLE",
                "decision brief unavailable in caller scope",
            )
        return self.brief

    def currentness(self, *, decision_brief_id: str, principal: Principal):
        self.load(decision_brief_id=decision_brief_id, principal=principal)
        return self.state


def draft(
    brief: DecisionBrief,
    disposition=AdoptionDisposition.ACCEPTED,
    selected=None,
    *,
    rationale="Human decision.",
    conditions=("Review after one cycle.",),
    supersedes=None,
):
    if selected is None:
        selected = tuple(brief.recommendation.recommended_option_ids)
    return DecisionAdoptionDraft(
        decision_brief_id=brief.decision_brief_id,
        source_brief_fingerprint=brief.brief_fingerprint,
        disposition=disposition,
        selected_option_ids=tuple(selected),
        human_rationale=rationale,
        human_conditions=tuple(conditions),
        supersedes_adoption_id=supersedes,
    )


def store(db, brief, currentness=DecisionBriefCurrentness.CURRENT):
    SQLModel.metadata.create_all(db)
    return DecisionAdoptionStore(
        decision_store=FakeDecisionStore(brief, currentness),
        db_engine=db,
    )


def test_current_decision_brief_adopts_successfully():
    db = engine()
    brief = make_brief()
    adoption = store(db, brief).record(
        draft=draft(brief),
        principal=principal(),
        now=STAMP,
    )
    assert adoption.disposition == AdoptionDisposition.ACCEPTED
    assert adoption.selected_option_ids == brief.recommendation.recommended_option_ids
    assert adoption.actor_user_id == str(USER)
    assert adoption.actor_authorization_context["authorization_action"] == "decision:adopt"


@pytest.mark.parametrize(
    "state",
    [DecisionBriefCurrentness.STALE_SOURCE_REPORT, DecisionBriefCurrentness.SUPERSEDED],
)
def test_noncurrent_decision_brief_rejects(state):
    db = engine()
    brief = make_brief()
    with pytest.raises(AdoptionError) as exc:
        store(db, brief, state).record(
            draft=draft(brief),
            principal=principal(),
        )
    assert exc.value.code == "ADOPTION_DECISION_BRIEF_NOT_CURRENT"


def test_foreign_and_missing_brief_share_unavailable_error():
    db = engine()
    brief = make_brief()
    s = store(db, brief)
    with pytest.raises(AdoptionError) as foreign:
        s.record(draft=draft(brief), principal=principal(tenant=OTHER_TENANT))
    missing = draft(brief).model_copy(
        update={"decision_brief_id": "p21b_" + "0" * 24},
    )
    with pytest.raises(AdoptionError) as absent:
        s.record(draft=missing, principal=principal())
    assert foreign.value.code == "ADOPTION_DECISION_BRIEF_UNAVAILABLE"
    assert absent.value.code == foreign.value.code


def test_payload_cannot_spoof_actor_or_tenant():
    brief = make_brief()
    raw = draft(brief).model_dump(mode="json")
    raw["actor_user_id"] = str(OTHER_USER)
    raw["tenant_id"] = str(OTHER_TENANT)
    with pytest.raises(ValidationError):
        DecisionAdoptionDraft.model_validate(raw)


def test_source_fingerprint_must_match_exact_brief():
    db = engine()
    brief = make_brief()
    bad = draft(brief).model_copy(
        update={"source_brief_fingerprint": "9" * 64},
    )
    with pytest.raises(AdoptionError) as exc:
        store(db, brief).record(draft=bad, principal=principal())
    assert exc.value.code == "ADOPTION_SOURCE_FINGERPRINT_MISMATCH"


def test_viewer_cannot_adopt():
    db = engine()
    brief = make_brief()
    assert "decision:adopt" not in permissions_for(principal("viewer"))
    with pytest.raises(AdoptionError) as exc:
        store(db, brief).record(draft=draft(brief), principal=principal("viewer"))
    assert exc.value.code == "ADOPTION_FORBIDDEN"


@pytest.mark.parametrize("role", ["analyst", "admin", "owner"])
def test_analyst_plus_can_adopt(role):
    db = engine()
    brief = make_brief()
    assert "decision:adopt" in permissions_for(principal(role))
    adoption = store(db, brief).record(
        draft=draft(brief),
        principal=principal(role),
        now=STAMP,
    )
    assert adoption.actor_user_id == str(USER)


def test_accepted_requires_exact_recommended_options():
    db = engine()
    brief = make_brief(recommended=(oid("a"), oid("b")))
    with pytest.raises(AdoptionError) as exc:
        store(db, brief).record(
            draft=draft(brief, selected=(oid("a"),)),
            principal=principal(),
        )
    assert exc.value.code == "ADOPTION_ACCEPTED_OPTIONS_MISMATCH"


@pytest.mark.parametrize("disposition", [AdoptionDisposition.REJECTED, AdoptionDisposition.DEFERRED])
def test_rejected_and_deferred_require_empty_selection(disposition):
    db = engine()
    brief = make_brief()
    s = store(db, brief)
    good = s.record(
        draft=draft(brief, disposition, selected=()),
        principal=principal(),
        now=STAMP,
    )
    assert good.selected_option_ids == ()


def test_rejected_nonempty_selection_rejects():
    db = engine()
    brief = make_brief()
    with pytest.raises(AdoptionError) as exc:
        store(db, brief).record(
            draft=draft(brief, AdoptionDisposition.REJECTED, selected=(oid("a"),)),
            principal=principal(),
        )
    assert exc.value.code == "ADOPTION_EMPTY_SELECTION_REQUIRED"


def test_modified_accepts_existing_different_option():
    db = engine()
    brief = make_brief()
    adoption = store(db, brief).record(
        draft=draft(
            brief,
            AdoptionDisposition.MODIFIED,
            selected=(oid("b"),),
            rationale="Human chooses B instead.",
        ),
        principal=principal(),
        now=STAMP,
    )
    assert adoption.selected_option_ids == (oid("b"),)
    assert adoption.human_rationale == "Human chooses B instead."


def test_modified_accepts_different_subset_of_existing_options():
    db = engine()
    brief = make_brief(recommended=(oid("a"), oid("b")))
    adoption = store(db, brief).record(
        draft=draft(
            brief,
            AdoptionDisposition.MODIFIED,
            selected=(oid("a"),),
        ),
        principal=principal(),
        now=STAMP,
    )
    assert adoption.selected_option_ids == (oid("a"),)


def test_modified_rejects_unknown_option():
    db = engine()
    brief = make_brief()
    with pytest.raises(AdoptionError) as exc:
        store(db, brief).record(
            draft=draft(
                brief,
                AdoptionDisposition.MODIFIED,
                selected=(oid("9"),),
            ),
            principal=principal(),
        )
    assert exc.value.code == "ADOPTION_OPTION_UNKNOWN"


def test_modified_cannot_smuggle_new_premise_or_action_payload():
    brief = make_brief()
    raw = draft(
        brief,
        AdoptionDisposition.MODIFIED,
        selected=(oid("b"),),
    ).model_dump(mode="json")
    raw["new_factual_premise"] = {"revenue": 99}
    raw["action_payload"] = {"send_email": True}
    with pytest.raises(ValidationError):
        DecisionAdoptionDraft.model_validate(raw)


def test_human_rationale_and_conditions_remain_human_metadata():
    db = engine()
    brief = make_brief()
    before = brief.model_dump(mode="json")
    adoption = store(db, brief).record(
        draft=draft(
            brief,
            rationale="Human prefers staged rollout.",
            conditions=("Stop if customer complaints rise.",),
        ),
        principal=principal(),
        now=STAMP,
    )
    assert adoption.human_rationale == "Human prefers staged rollout."
    assert adoption.human_conditions == ("Stop if customer complaints rise.",)
    assert brief.model_dump(mode="json") == before


def test_same_canonical_event_is_idempotent():
    db = engine()
    brief = make_brief()
    s = store(db, brief)
    event = draft(brief)
    first = s.record(draft=event, principal=principal(), now=STAMP)
    retry = s.record(
        draft=event,
        principal=principal(),
        now=STAMP + timedelta(minutes=5),
    )
    assert retry.adoption_id == first.adoption_id
    assert retry.recorded_at == first.recorded_at
    with Session(db) as session:
        assert len(session.exec(select(DecisionAdoptionRecord)).all()) == 1


def test_changed_decision_requires_and_creates_immutable_supersession():
    db = engine()
    brief = make_brief()
    s = store(db, brief)
    first = s.record(draft=draft(brief), principal=principal(), now=STAMP)
    changed = draft(
        brief,
        AdoptionDisposition.MODIFIED,
        selected=(oid("b"),),
        rationale="Changed human decision.",
        supersedes=first.adoption_id,
    )
    second = s.record(
        draft=changed,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    assert second.adoption_id != first.adoption_id
    assert second.supersedes_adoption_id == first.adoption_id
    assert s.load(adoption_id=first.adoption_id, principal=principal()).adoption_id == first.adoption_id
    assert s.currentness(
        adoption_id=first.adoption_id,
        principal=principal(),
    ) == AdoptionCurrentness.SUPERSEDED
    assert s.currentness(
        adoption_id=second.adoption_id,
        principal=principal(),
    ) == AdoptionCurrentness.CURRENT


def test_changed_decision_without_supersedes_rejects():
    db = engine()
    brief = make_brief()
    s = store(db, brief)
    first = s.record(draft=draft(brief), principal=principal(), now=STAMP)
    assert first
    with pytest.raises(AdoptionError) as exc:
        s.record(
            draft=draft(
                brief,
                AdoptionDisposition.MODIFIED,
                selected=(oid("b"),),
                rationale="Changed.",
            ),
            principal=principal(),
            now=STAMP + timedelta(minutes=1),
        )
    assert exc.value.code == "ADOPTION_SUPERSESSION_REQUIRED"


def test_cross_actor_supersession_rejects():
    db = engine()
    brief = make_brief()
    s = store(db, brief)
    first = s.record(draft=draft(brief), principal=principal(), now=STAMP)
    with pytest.raises(AdoptionError) as exc:
        s.record(
            draft=draft(
                brief,
                AdoptionDisposition.MODIFIED,
                selected=(oid("b"),),
                supersedes=first.adoption_id,
            ),
            principal=principal(user=OTHER_USER),
            now=STAMP + timedelta(minutes=1),
        )
    assert exc.value.code == "ADOPTION_SUPERSESSION_INVALID"


def test_historical_adoption_remains_after_brief_becomes_stale():
    db = engine()
    brief = make_brief()
    fake = FakeDecisionStore(brief)
    SQLModel.metadata.create_all(db)
    s = DecisionAdoptionStore(decision_store=fake, db_engine=db)
    adoption = s.record(draft=draft(brief), principal=principal(), now=STAMP)
    fake.state = DecisionBriefCurrentness.STALE_SOURCE_REPORT
    assert s.load(adoption_id=adoption.adoption_id, principal=principal()).adoption_id == adoption.adoption_id
    assert s.currentness(
        adoption_id=adoption.adoption_id,
        principal=principal(),
    ) == AdoptionCurrentness.SOURCE_BRIEF_STALE


def test_adoption_lookup_is_cross_tenant_non_oracle():
    db = engine()
    brief = make_brief()
    s = store(db, brief)
    adoption = s.record(draft=draft(brief), principal=principal(), now=STAMP)
    with pytest.raises(AdoptionError) as foreign:
        s.load(adoption_id=adoption.adoption_id, principal=principal(tenant=OTHER_TENANT))
    with pytest.raises(AdoptionError) as missing:
        s.load(adoption_id="adp_" + "0" * 24, principal=principal())
    assert foreign.value.code == "ADOPTION_UNAVAILABLE"
    assert missing.value.code == foreign.value.code


def test_legacy_decision_record_is_unchanged():
    db = engine()
    brief = make_brief()
    SQLModel.metadata.create_all(db)
    with Session(db) as session:
        row = DecisionRecord(
            id="legacy-adoption-proof",
            ts=STAMP,
            tenant_id=str(TENANT),
            user_id=str(USER),
            note="historical",
        )
        session.add(row)
        session.commit()
        before = session.get(DecisionRecord, row.id).model_dump()
    DecisionAdoptionStore(
        decision_store=FakeDecisionStore(brief),
        db_engine=db,
    ).record(draft=draft(brief), principal=principal(), now=STAMP)
    with Session(db) as session:
        after = session.get(DecisionRecord, "legacy-adoption-proof").model_dump()
    assert after == before


def test_p14_through_p21_authority_rows_are_unchanged():
    db = engine()
    brief = make_brief()
    SQLModel.metadata.create_all(db)
    models = (
        ResearchSessionRecord,
        ResearchExecutionLink,
        ResearchExplorationMaterial,
        ResearchClaimRecord,
        ResearchReasoningStepRecord,
        BusinessRelationshipPolicyUseRecord,
        HypothesisRecord,
        HypothesisGroundingLink,
        RootCauseAssessment,
        ReportDocumentRecord,
        DecisionBriefRecord,
    )
    with Session(db) as session:
        before = {
            model.__name__: len(session.exec(select(model)).all())
            for model in models
        }
    DecisionAdoptionStore(
        decision_store=FakeDecisionStore(brief),
        db_engine=db,
    ).record(draft=draft(brief), principal=principal(), now=STAMP)
    with Session(db) as session:
        after = {
            model.__name__: len(session.exec(select(model)).all())
            for model in models
        }
    assert after == before


def test_exactly_one_modern_adoption_table_exists():
    tables = {
        table.name
        for table in SQLModel.metadata.tables.values()
        if table.name == "decision_adoption"
    }
    assert tables == {"decision_adoption"}


def test_adoption_owner_has_zero_analytics_action_or_legacy_writes():
    source = Path("app/v3/decision_adoption.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
            imported.update(alias.name for alias in node.names)

    forbidden_imports = (
        "app.v3.substrate.metabase",
        "app.v3.research",
        "app.v3.claim_lineage",
        "app.v3.hypothesis_root_cause",
        "app.v3.business_relationship_policy",
        "app.v3.action",
        "app.wren",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
    )
    assert not any(name.startswith(forbidden_imports) for name in imports)
    assert "DecisionRecord" not in imported
    assert "DecisionBriefRecord" not in imported
    for token in (
        "execute_dataset",
        "execute_native_query",
        "cube_query",
        "sablon_json",
        "contract_ids_json",
        "send_email",
        "Slack",
        "workflow",
        "ActionPlan",
        "ActionAuthorization",
        "DimaQueryReceipt(",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
        "RootCauseAssessment(",
        "ReportDocumentRecord(",
        "DecisionBriefRecord(",
        "DecisionRecord(",
    ):
        assert token not in source
