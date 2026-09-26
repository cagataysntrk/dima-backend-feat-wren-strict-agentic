from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.v3.action_authorization import (
    ActionAuthorityError,
    ActionAuthorizationStore,
    ActionCapabilityRegistry,
    ActionCapabilitySpec,
    ActionPlanDraft,
    ActionRiskClass,
    AuthorizationCurrentness,
    ConfirmationRequirement,
    DEFAULT_ACTION_CAPABILITY_REGISTRY,
    Reversibility,
)
from app.v3.decision_adoption import (
    AdoptionCurrentness,
    AdoptionDisposition,
    AdoptionError,
    DecisionAdoption,
)
from app.v3.decision_intelligence import (
    DecisionBrief,
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
    ActionAuthorizationRecord,
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

TENANT = UUID("00000000-0000-4000-8000-000000005901")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000005902")
ADOPTER = UUID("00000000-0000-4000-8000-000000005903")
AUTHORIZER = UUID("00000000-0000-4000-8000-000000005904")
STAMP = datetime(2026, 9, 26, 6, 10, tzinfo=timezone.utc)


class LowRiskParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record_id: str = Field(min_length=1)
    enabled: bool


class MaterialParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record_id: str


def db_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal(role="admin", *, user=AUTHORIZER, tenant=TENANT):
    return Principal(
        user_id=str(user),
        tenant_id=str(tenant),
        tenant_slug="action",
        roles=[role],
    )


def oid(ch: str) -> str:
    return "p21x_" + ch * 24


def make_brief(*, tenant=TENANT, fingerprint="b" * 64):
    premise = DecisionPremiseRef(
        premise_id="p21p_" + "c" * 24,
        statement_id="p20s_" + "d" * 24,
        statement_kind=ReportStatementKind.ANALYTICAL_FACT,
        upstream_epistemic_ceiling="SUPPORTED",
    )
    return DecisionBrief(
        decision_brief_id="p21b_" + "e" * 24,
        report_id="p20r_" + "f" * 24,
        tenant_binding=f"id:{tenant}",
        semantic_context_version="ctx-action-v1",
        brief_key="action-brief",
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
                text="Prefer reversible changes.",
            ),
        ),
        premises=(premise,),
        options=(
            DecisionOption(option_id=oid("a"), proposal_text="Option A"),
            DecisionOption(option_id=oid("b"), proposal_text="Option B"),
        ),
        tradeoffs=(),
        assumptions=(),
        limitations=(),
        recommendation=DecisionRecommendation(
            recommended_option_ids=(oid("a"),),
            premise_refs=(premise.premise_id,),
        ),
        model_provenance=None,
        source_report_fingerprint="3" * 64,
        decision_source_fingerprint="4" * 64,
        brief_fingerprint=fingerprint,
        created_at=STAMP,
    )


def make_adoption(
    brief: DecisionBrief,
    *,
    disposition=AdoptionDisposition.ACCEPTED,
    selected=(oid("a"),),
    fingerprint="5" * 64,
):
    return DecisionAdoption(
        adoption_id="adp_" + "6" * 24,
        decision_brief_id=brief.decision_brief_id,
        source_brief_fingerprint=brief.brief_fingerprint,
        tenant_binding=brief.tenant_binding,
        actor_user_id=str(ADOPTER),
        actor_authorization_context={
            "user_id": str(ADOPTER),
            "tenant_binding": brief.tenant_binding,
            "roles": ["analyst"],
            "authorization_action": "decision:adopt",
        },
        disposition=disposition,
        selected_option_ids=tuple(selected),
        human_rationale="Human decision.",
        human_conditions=(),
        supersedes_adoption_id=None,
        recorded_at=STAMP - timedelta(minutes=5),
        adoption_fingerprint=fingerprint,
    )


class FakeDecisionStore:
    def __init__(self, brief):
        self.brief = brief

    def load(self, *, decision_brief_id, principal):
        if (
            decision_brief_id != self.brief.decision_brief_id
            or self.brief.tenant_binding != f"id:{principal.tenant_id}"
        ):
            raise P21DecisionError(
                "P21_DECISION_BRIEF_UNAVAILABLE",
                "decision brief unavailable in caller scope",
            )
        return self.brief


class FakeAdoptionStore:
    def __init__(self, adoption, state=AdoptionCurrentness.CURRENT):
        self.adoption = adoption
        self.state = state

    def load(self, *, adoption_id, principal):
        if (
            adoption_id != self.adoption.adoption_id
            or self.adoption.tenant_binding != f"id:{principal.tenant_id}"
        ):
            raise AdoptionError(
                "ADOPTION_UNAVAILABLE",
                "adoption unavailable in caller scope",
            )
        return self.adoption

    def currentness(self, *, adoption_id, principal):
        self.load(adoption_id=adoption_id, principal=principal)
        return self.state


def capability(
    *,
    version="1",
    risk=ActionRiskClass.REVERSIBLE_LOW_RISK,
    ttl=600,
    target_system="fixture-system",
    model=LowRiskParams,
):
    return ActionCapabilitySpec(
        capability_key="fixture.set-enabled",
        action_kind="fixture.set_enabled",
        version=version,
        target_system=target_system,
        parameter_model=model,
        risk_class=risk,
        reversibility=(
            Reversibility.REVERSIBLE
            if risk != ActionRiskClass.IRREVERSIBLE_EXTERNAL_COMMIT
            else Reversibility.IRREVERSIBLE
        ),
        confirmation_requirement=(
            ConfirmationRequirement.EXPLICIT_AUTHORIZATION
            if risk == ActionRiskClass.REVERSIBLE_LOW_RISK
            else ConfirmationRequirement.DUAL_APPROVAL
        ),
        authorization_policy_id="low-risk-admin",
        authorization_policy_version="1",
        idempotency_strategy="target-resource-plus-plan-fingerprint",
        authorization_ttl_seconds=ttl,
    )


def registry(spec=None):
    return ActionCapabilityRegistry((spec or capability(),))


def plan_draft(brief, adoption, *, params=None, source_options=(oid("a"),)):
    return ActionPlanDraft(
        action_kind="fixture.set_enabled",
        target_system="fixture-system",
        target_resource="record/42",
        typed_parameters=params or {"record_id": "42", "enabled": True},
        source_option_ids=tuple(source_options),
        decision_adoption_id=adoption.adoption_id,
        decision_adoption_fingerprint=adoption.adoption_fingerprint,
        decision_brief_id=brief.decision_brief_id,
        decision_brief_fingerprint=brief.brief_fingerprint,
        report_id=brief.report_id,
        report_fingerprint=brief.source_report_fingerprint,
    )


def store(
    db,
    *,
    brief=None,
    adoption=None,
    adoption_state=AdoptionCurrentness.CURRENT,
    reg=None,
):
    SQLModel.metadata.create_all(db)
    brief = brief or make_brief()
    adoption = adoption or make_adoption(brief)
    decision_store = FakeDecisionStore(brief)
    adoption_store = FakeAdoptionStore(adoption, adoption_state)
    auth_store = ActionAuthorizationStore(
        adoption_store=adoption_store,
        decision_store=decision_store,
        registry=reg or registry(),
        db_engine=db,
    )
    return auth_store, decision_store, adoption_store, brief, adoption


def test_default_production_registry_contains_no_capability():
    with pytest.raises(ActionAuthorityError) as exc:
        DEFAULT_ACTION_CAPABILITY_REGISTRY.require("fixture.set_enabled")
    assert exc.value.code == "ACTION_CAPABILITY_UNAVAILABLE"


def test_current_accepted_adoption_can_authorize_legal_plan():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    authz = s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal("admin"),
        now=STAMP,
    )
    assert authz.risk_class == ActionRiskClass.REVERSIBLE_LOW_RISK
    assert authz.canonical_plan.plan_fingerprint == authz.plan_fingerprint
    assert authz.decision_adoption_id == adoption.adoption_id


@pytest.mark.parametrize(
    "state",
    [AdoptionCurrentness.SOURCE_BRIEF_STALE, AdoptionCurrentness.SUPERSEDED],
)
def test_noncurrent_adoption_rejects(state):
    db = db_engine()
    s, _, _, brief, adoption = store(db, adoption_state=state)
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=plan_draft(brief, adoption),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_SOURCE_ADOPTION_NOT_CURRENT"


@pytest.mark.parametrize(
    "disposition",
    [
        AdoptionDisposition.REJECTED,
        AdoptionDisposition.DEFERRED,
        AdoptionDisposition.MODIFIED,
    ],
)
def test_nonaccepted_adoption_rejects(disposition):
    db = db_engine()
    brief = make_brief()
    adoption = make_adoption(
        brief,
        disposition=disposition,
        selected=(() if disposition != AdoptionDisposition.MODIFIED else (oid("b"),)),
    )
    s, _, _, _, _ = store(db, brief=brief, adoption=adoption)
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=plan_draft(brief, adoption, source_options=adoption.selected_option_ids or (oid("a"),)),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_SOURCE_ADOPTION_NOT_ACCEPTED"


def test_foreign_tenant_source_rejects():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=plan_draft(brief, adoption),
            principal=principal(tenant=OTHER_TENANT),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_SOURCE_ADOPTION_UNAVAILABLE"


def test_unknown_action_kind_rejects():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    raw = plan_draft(brief, adoption).model_dump(mode="json")
    raw["action_kind"] = "unknown.action"
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=ActionPlanDraft.model_validate(raw),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_CAPABILITY_UNAVAILABLE"


@pytest.mark.parametrize(
    "field,value",
    [
        ("risk_class", "REVERSIBLE_LOW_RISK"),
        ("authorization_policy_id", "client-policy"),
        ("idempotency_strategy", "client-strategy"),
        ("capability_version", "999"),
    ],
)
def test_client_cannot_override_trusted_policy_metadata(field, value):
    brief = make_brief()
    adoption = make_adoption(brief)
    raw = plan_draft(brief, adoption).model_dump(mode="json")
    raw[field] = value
    with pytest.raises(ValidationError):
        ActionPlanDraft.model_validate(raw)


@pytest.mark.parametrize("role", ["viewer", "analyst"])
def test_viewer_and_analyst_cannot_authorize(role):
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    assert "action:authorize" not in permissions_for(principal(role))
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=plan_draft(brief, adoption),
            principal=principal(role),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_AUTHORIZATION_FORBIDDEN"


@pytest.mark.parametrize("role", ["admin", "owner"])
def test_admin_and_owner_can_authorize(role):
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    assert "action:authorize" in permissions_for(principal(role))
    authz = s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal(role),
        now=STAMP,
    )
    assert authz.authorizer_user_id == str(AUTHORIZER)


@pytest.mark.parametrize(
    "risk",
    [
        ActionRiskClass.REVERSIBLE_MATERIAL,
        ActionRiskClass.IRREVERSIBLE_EXTERNAL_COMMIT,
    ],
)
def test_unsupported_risk_classes_fail_closed(risk):
    db = db_engine()
    spec = capability(risk=risk, model=MaterialParams)
    s, _, _, brief, adoption = store(db, reg=registry(spec))
    raw = plan_draft(
        brief,
        adoption,
        params={"record_id": "42"},
    ).model_dump(mode="json")
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=ActionPlanDraft.model_validate(raw),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_RISK_NOT_SUPPORTED_IN_FIRST_SLICE"


def test_typed_valid_parameters_are_canonicalized():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    authz = s.authorize(
        draft=plan_draft(brief, adoption, params={"enabled": True, "record_id": "42"}),
        principal=principal(),
        now=STAMP,
    )
    assert authz.canonical_plan.typed_parameters == {
        "record_id": "42",
        "enabled": True,
    }


@pytest.mark.parametrize(
    "params",
    [
        {"record_id": "42"},
        {"record_id": "42", "enabled": True, "extra": "x"},
        {"record_id": 42, "enabled": True},
    ],
)
def test_missing_extra_or_wrong_type_parameters_reject(params):
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=plan_draft(brief, adoption, params=params),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_PARAMETERS_INVALID"


def test_source_option_ids_must_belong_to_accepted_adoption():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=plan_draft(brief, adoption, source_options=(oid("b"),)),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_SOURCE_OPTION_NOT_ADOPTED"


def test_same_plan_canonicalizes_identically():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    gate = s._plan_gate
    a = gate.build(
        draft=plan_draft(brief, adoption, params={"record_id": "42", "enabled": True}),
        principal=principal(),
    )
    b = gate.build(
        draft=plan_draft(brief, adoption, params={"enabled": True, "record_id": "42"}),
        principal=principal(),
    )
    assert a.plan_fingerprint == b.plan_fingerprint
    assert a.model_dump(mode="json") == b.model_dump(mode="json")


def test_parameter_change_changes_plan_fingerprint():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    gate = s._plan_gate
    a = gate.build(
        draft=plan_draft(brief, adoption, params={"record_id": "42", "enabled": True}),
        principal=principal(),
    )
    b = gate.build(
        draft=plan_draft(brief, adoption, params={"record_id": "42", "enabled": False}),
        principal=principal(),
    )
    assert a.plan_fingerprint != b.plan_fingerprint


def test_exact_same_authorization_is_idempotent_while_current():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    d = plan_draft(brief, adoption)
    first = s.authorize(draft=d, principal=principal(), now=STAMP)
    retry = s.authorize(
        draft=d,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    )
    assert retry.authorization_id == first.authorization_id
    assert retry.issued_at == first.issued_at
    with Session(db) as session:
        assert len(session.exec(select(ActionAuthorizationRecord)).all()) == 1


def test_authorization_stores_exact_plan_snapshot():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    authz = s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal(),
        now=STAMP,
    )
    with Session(db) as session:
        row = session.get(ActionAuthorizationRecord, authz.authorization_id)
        assert row is not None
        assert row.plan_fingerprint == authz.canonical_plan.plan_fingerprint
        assert '"typed_parameters"' in row.canonical_plan_json
        assert '"record_id":"42"' in row.canonical_plan_json


def test_authorization_expires_deterministically():
    db = db_engine()
    s, _, _, brief, adoption = store(db, reg=registry(capability(ttl=60)))
    authz = s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal(),
        now=STAMP,
    )
    assert s.currentness(
        authorization_id=authz.authorization_id,
        principal=principal(),
        now=STAMP + timedelta(seconds=59),
    ) == AuthorizationCurrentness.CURRENT
    assert s.currentness(
        authorization_id=authz.authorization_id,
        principal=principal(),
        now=STAMP + timedelta(seconds=60),
    ) == AuthorizationCurrentness.EXPIRED


def test_capability_version_change_makes_old_authorization_stale():
    db = db_engine()
    old_registry = registry(capability(version="1"))
    s, decision_store, adoption_store, brief, adoption = store(db, reg=old_registry)
    authz = s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal(),
        now=STAMP,
    )
    changed = ActionAuthorizationStore(
        adoption_store=adoption_store,
        decision_store=decision_store,
        registry=registry(capability(version="2")),
        db_engine=db,
    )
    assert changed.currentness(
        authorization_id=authz.authorization_id,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    ) == AuthorizationCurrentness.CAPABILITY_STALE


def test_changed_plan_creates_new_immutable_superseding_authorization():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    first = s.authorize(
        draft=plan_draft(brief, adoption, params={"record_id": "42", "enabled": True}),
        principal=principal(),
        now=STAMP,
    )
    second = s.authorize(
        draft=plan_draft(brief, adoption, params={"record_id": "42", "enabled": False}),
        principal=principal(),
        supersedes_authorization_id=first.authorization_id,
        now=STAMP + timedelta(minutes=1),
    )
    assert second.authorization_id != first.authorization_id
    assert second.supersedes_authorization_id == first.authorization_id
    assert s.currentness(
        authorization_id=first.authorization_id,
        principal=principal(),
        now=STAMP + timedelta(minutes=1),
    ) == AuthorizationCurrentness.SUPERSEDED
    loaded = s.load(authorization_id=first.authorization_id, principal=principal())
    assert loaded.plan_fingerprint == first.plan_fingerprint


def test_changed_plan_without_supersession_rejects():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    first = s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal(),
        now=STAMP,
    )
    assert first
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=plan_draft(brief, adoption, params={"record_id": "42", "enabled": False}),
            principal=principal(),
            now=STAMP + timedelta(minutes=1),
        )
    assert exc.value.code == "ACTION_SUPERSESSION_REQUIRED"


def test_expired_same_plan_requires_explicit_reauthorization_lineage():
    db = db_engine()
    s, _, _, brief, adoption = store(db, reg=registry(capability(ttl=60)))
    d = plan_draft(brief, adoption)
    first = s.authorize(draft=d, principal=principal(), now=STAMP)
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=d,
            principal=principal(),
            now=STAMP + timedelta(seconds=61),
        )
    assert exc.value.code == "ACTION_REAUTHORIZATION_REQUIRED"
    second = s.authorize(
        draft=d,
        principal=principal(),
        supersedes_authorization_id=first.authorization_id,
        now=STAMP + timedelta(seconds=61),
    )
    assert second.authorization_id != first.authorization_id


def test_authorization_lookup_is_cross_tenant_non_oracle():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    authz = s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal(),
        now=STAMP,
    )
    with pytest.raises(ActionAuthorityError) as foreign:
        s.load(
            authorization_id=authz.authorization_id,
            principal=principal(tenant=OTHER_TENANT),
        )
    with pytest.raises(ActionAuthorityError) as missing:
        s.load(
            authorization_id="authz_" + "0" * 24,
            principal=principal(),
        )
    assert foreign.value.code == "ACTION_AUTHORIZATION_UNAVAILABLE"
    assert missing.value.code == foreign.value.code


def test_source_fingerprint_mismatch_rejects():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    raw = plan_draft(brief, adoption).model_dump(mode="json")
    raw["decision_adoption_fingerprint"] = "9" * 64
    with pytest.raises(ActionAuthorityError) as exc:
        s.authorize(
            draft=ActionPlanDraft.model_validate(raw),
            principal=principal(),
            now=STAMP,
        )
    assert exc.value.code == "ACTION_ADOPTION_FINGERPRINT_MISMATCH"


def test_legacy_and_sealed_owner_rows_are_unchanged():
    db = db_engine()
    s, _, _, brief, adoption = store(db)
    with Session(db) as session:
        legacy = DecisionRecord(
            id="legacy-action-proof",
            ts=STAMP,
            tenant_id=str(TENANT),
            user_id=str(ADOPTER),
            note="historical",
        )
        session.add(legacy)
        session.commit()

    models = (
        DecisionRecord,
        DecisionAdoptionRecord,
        DecisionBriefRecord,
        ReportDocumentRecord,
        ResearchSessionRecord,
        ResearchExecutionLink,
        ResearchExplorationMaterial,
        ResearchClaimRecord,
        ResearchReasoningStepRecord,
        BusinessRelationshipPolicyUseRecord,
        HypothesisRecord,
        HypothesisGroundingLink,
        RootCauseAssessment,
    )
    with Session(db) as session:
        before = {
            model.__name__: [row.model_dump() for row in session.exec(select(model)).all()]
            for model in models
        }

    s.authorize(
        draft=plan_draft(brief, adoption),
        principal=principal(),
        now=STAMP,
    )

    with Session(db) as session:
        after = {
            model.__name__: [row.model_dump() for row in session.exec(select(model)).all()]
            for model in models
        }
    assert after == before


def test_exactly_one_action_authority_table_and_no_plan_or_execution_tables():
    names = set(SQLModel.metadata.tables)
    assert "action_authorization" in names
    assert "action_plan" not in names
    assert "action_execution_receipt" not in names
    assert "action_attempt" not in names


def test_action_authorization_owner_has_zero_execution_analytics_or_connectors():
    source = Path("app/v3/action_authorization.py").read_text(encoding="utf-8")
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
        "app.wren",
        "requests",
        "httpx",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
    )
    assert not any(name.startswith(forbidden_imports) for name in imports)
    assert "DecisionRecord" not in imported
    assert "DecisionAdoptionRecord" not in imported
    assert "DecisionBriefRecord" not in imported

    for token in (
        "requests.post",
        "httpx.",
        "send_email",
        "Slack",
        "erp_client",
        "ticket",
        "notification",
        "execute_action",
        "ActionExecutionReceipt",
        "ActionAttempt",
        "DimaQueryReceipt(",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
        "RootCauseAssessment(",
        "ReportDocumentRecord(",
        "DecisionBriefRecord(",
        "DecisionAdoptionRecord(",
        "DecisionRecord(",
    ):
        assert token not in source
