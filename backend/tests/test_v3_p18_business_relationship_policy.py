from __future__ import annotations

import ast
import hashlib
import inspect
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

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
from app.v3.business_relationship_policy import (
    BusinessRelationshipPolicyError,
    BusinessRelationshipPolicyStatus,
    BusinessRelationshipPolicyStore,
    RelationshipPolicyRequirement,
    RelationshipPolicyResolutionStatus,
)
from app.v3.claim_lineage import ClaimFreshness, ClaimLineageStore
from app.v3.research import ObligationState, ResearchManager
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.models import (
    BusinessRelationshipPolicyRecord,
    BusinessRelationshipPolicyUseRecord,
    ResearchReasoningStepRecord,
    Tenant,
    User,
)


TENANT = UUID("00000000-0000-4000-8000-000000001801")
USER = UUID("00000000-0000-4000-8000-000000001802")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000001811")
OTHER_USER = UUID("00000000-0000-4000-8000-000000001812")
STAMP = datetime(2026, 9, 25, 17, 0, tzinfo=timezone.utc)


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


def principal(
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p18",
) -> Principal:
    return Principal(
        user_id=str(user),
        tenant_id=str(tenant),
        tenant_slug=slug,
        roles=["analyst"],
    )


def brief(
    *,
    suffix: str,
    context: str = "ctx-p18-v1",
    obligations: tuple[str, ...] = ("g1",),
) -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="siparişler",
        candidate_id="native.sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    questions = tuple(
        ResearchQuestion(
            goal_id=oid,
            kind=ResearchGoalKind.PERFORMANCE,
            source_text=f"{oid} için sınırlandırılmış araştırma.",
            subject_refs=(metric,),
            status=ResearchGoalStatus.RESOLVED,
        )
        for oid in obligations
    )
    return ResearchBrief(
        brief_id=f"rb-p18-{suffix}",
        objective=questions[0].source_text,
        scope=ResearchScope(semantic_refs=(metric,)),
        questions=questions,
        must_requirement_ids=obligations,
        context_version=context,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def ensure_identity_rows(
    db,
    *,
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p18",
):
    with Session(db) as s:
        if s.get(Tenant, tenant) is None:
            s.add(
                Tenant(
                    id=tenant,
                    slug=slug,
                    name=slug.upper(),
                    created_at=STAMP,
                )
            )
        if s.get(User, user) is None:
            s.add(
                User(
                    id=user,
                    tenant_id=tenant,
                    email=f"{user}@example.test",
                    password_hash="unused",
                    created_at=STAMP,
                )
            )
        s.commit()


def make_state(
    db,
    *,
    suffix: str = "base",
    tenant: UUID = TENANT,
    user: UUID = USER,
    slug: str = "p18",
    context: str = "ctx-p18-v1",
    obligations: tuple[str, ...] = ("g1",),
    claim_obligation: str = "g1",
    step_obligation: str = "g1",
):
    SQLModel.metadata.create_all(db)
    ensure_identity_rows(db, tenant=tenant, user=user, slug=slug)
    p = principal(tenant, user, slug)
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=brief(
            suffix=suffix,
            context=context,
            obligations=obligations,
        ),
        request_ref=f"p18-{suffix}",
        source_message_hash=hashlib.sha256(
            f"p18-{suffix}".encode()
        ).hexdigest(),
        principal=p,
    )
    verified = tuple(
        item.model_copy(update={"state": ObligationState.VERIFIED})
        for item in session.obligations
    )
    advanced = ResearchManager.advance(
        session,
        obligations=verified,
        now=STAMP + timedelta(minutes=1),
    )
    session = store.save(
        advanced,
        expected_revision=session.revision,
    )

    claims = ClaimLineageStore(
        research_store=store,
        db_engine=db,
    )
    claim = claims.create_claim(
        session_id=session.session_id,
        obligation_id=claim_obligation,
        principal=p,
        claim_text=(
            f"{claim_obligation} için governed provider-free P18 test claim."
        ),
        proposition={
            "subject": f"business:{claim_obligation}",
            "predicate": "has_governed_interpretation",
            "object": True,
        },
        scope={"period": "2026-06", "population": "sales_orders"},
        freshness=ClaimFreshness(
            as_of=STAMP,
            stale_after=STAMP + timedelta(days=30),
        ),
    )

    step_id = "rrs_" + h(
        {
            "session": session.session_id,
            "obligation": step_obligation,
            "suffix": suffix,
        }
    )[:24]
    with Session(db) as s:
        s.add(
            ResearchReasoningStepRecord(
                step_id=step_id,
                session_id=session.session_id,
                source_revision=session.revision,
                source_snapshot_fingerprint=session.fingerprint,
                parent_obligation_id=step_obligation,
                parent_step_id=None,
                depth=0,
                branch_id="ibr_" + h(step_id)[:20],
                intent="STOP_INVESTIGATION",
                target_kind="GAP",
                target_ref=None,
                stop_scope="INVESTIGATION",
                proposal_id=f"proposal-{suffix}",
                proposal_json=json.dumps(
                    {"kind": "provider-free-p18-fixture"},
                    sort_keys=True,
                ),
                action="STOP",
                objective_key=f"p18.{suffix}",
                bounded_objective=None,
                rationale="Provider-free sealed P17 fixture.",
                inspected_evidence_refs_json="[]",
                inspected_claim_refs_json=json.dumps([claim.claim_id]),
                inspected_material_refs_json="[]",
                proposal_fingerprint=h(
                    {"step": step_id, "claim": claim.claim_id}
                ),
                status="STOPPED",
                stop_reason="INCONCLUSIVE",
                result_refs_json="[]",
                created_at=STAMP + timedelta(minutes=2),
                completed_at=STAMP + timedelta(minutes=2),
            )
        )
        s.commit()

    p18 = BusinessRelationshipPolicyStore(
        research_store=store,
        db_engine=db,
    )
    return {
        "principal": p,
        "store": store,
        "session": session,
        "claim": claim,
        "step_id": step_id,
        "p18": p18,
    }


def policy_scope():
    return {"period": "2026-06", "population": "sales_orders"}


def create_policy(
    state,
    *,
    principal_override=None,
    context="ctx-p18-v1",
    scope=None,
    source="business:sales-order",
    target="business:customer",
    statement="Sales orders may be attributed to governed customer identity.",
    provenance="policy-manual:p18-v1",
):
    return state["p18"].create_policy(
        principal=principal_override or state["principal"],
        semantic_context_version=context,
        policy_key="sales-order-customer-attribution",
        source_business_ref=source,
        target_business_ref=target,
        business_relationship_statement=statement,
        applicability_scope=scope or policy_scope(),
        provenance_ref=provenance,
        now=STAMP + timedelta(minutes=3),
    )


def requirement(
    state,
    *,
    required=True,
    context=None,
    scope=None,
    source="business:sales-order",
    target="business:customer",
    claim_id=None,
    step_id=None,
    obligation="g1",
):
    return RelationshipPolicyRequirement(
        research_session_id=state["session"].session_id,
        obligation_id=obligation,
        claim_id=claim_id or state["claim"].claim_id,
        reasoning_step_id=step_id or state["step_id"],
        policy_key="sales-order-customer-attribution",
        source_business_ref=source,
        target_business_ref=target,
        semantic_context_version=(
            context or state["session"].context_version
        ),
        applicability_scope=scope or policy_scope(),
        required=required,
    )


def test_create_and_load_exact_active_policy_is_canonical_and_idempotent():
    db = db_engine()
    state = make_state(db)
    first = create_policy(
        state,
        scope={"population": "sales_orders", "period": "2026-06"},
    )
    second = create_policy(
        state,
        scope={"period": "2026-06", "population": "sales_orders"},
    )
    loaded = state["p18"].load_policy(
        policy_id=first.policy_id,
        principal=state["principal"],
    )

    assert first == second == loaded
    assert first.status == BusinessRelationshipPolicyStatus.ACTIVE
    assert first.applicability_scope_fingerprint == h(policy_scope())
    assert first.policy_id == "brp_" + first.policy_fingerprint[:24]


def test_changed_meaning_requires_retiring_current_exact_policy():
    db = db_engine()
    state = make_state(db)
    create_policy(state)

    with pytest.raises(
        BusinessRelationshipPolicyError,
        match="P18_ACTIVE_POLICY_CONFLICT",
    ):
        create_policy(
            state,
            statement="Changed governed business meaning.",
            provenance="policy-manual:p18-v2",
        )


def test_required_exact_active_policy_is_satisfied():
    db = db_engine()
    state = make_state(db)
    policy = create_policy(state)
    decision = state["p18"].resolve(
        requirement=requirement(state),
        principal=state["principal"],
        now=STAMP + timedelta(minutes=4),
    )

    assert decision.required is True
    assert decision.eligible is True
    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.SATISFIED
    )
    assert decision.policy_id == policy.policy_id
    assert decision.limitation_code is None


def test_required_missing_policy_persists_blocked_lineage():
    db = db_engine()
    state = make_state(db)
    decision = state["p18"].resolve(
        requirement=requirement(state),
        principal=state["principal"],
    )
    use = state["p18"].load_use(
        session_id=state["session"].session_id,
        policy_use_id=decision.policy_use_id,
        principal=state["principal"],
    )

    assert decision.eligible is False
    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_MISSING
    )
    assert use.resolution_status == decision.resolution_status
    assert use.policy_id is None
    assert use.limitation_code == "P18_RELATIONSHIP_POLICY_MISSING"


def test_retired_exact_policy_blocks_new_resolution():
    db = db_engine()
    state = make_state(db)
    policy = create_policy(state)
    retired = state["p18"].retire_policy(
        policy_id=policy.policy_id,
        principal=state["principal"],
        now=STAMP + timedelta(minutes=5),
    )
    decision = state["p18"].resolve(
        requirement=requirement(state),
        principal=state["principal"],
    )

    assert retired.status == BusinessRelationshipPolicyStatus.RETIRED
    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_RETIRED
    )
    assert decision.eligible is False


def test_not_required_returns_without_policy_lookup():
    db = db_engine()
    state = make_state(db)
    decision = state["p18"].resolve(
        requirement=requirement(state, required=False),
        principal=state["principal"],
    )

    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.NOT_REQUIRED
    )
    assert decision.eligible is True
    assert decision.policy_id is None
    with Session(db) as s:
        assert s.exec(select(BusinessRelationshipPolicyRecord)).all() == []


def test_foreign_tenant_policy_is_distinguished_and_blocked():
    db = db_engine()
    state = make_state(db)
    foreign = principal(OTHER_TENANT, OTHER_USER, "p18-other")
    create_policy(state, principal_override=foreign)

    decision = state["p18"].resolve(
        requirement=requirement(state),
        principal=state["principal"],
    )
    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_TENANT
    )
    assert decision.limitation_code == (
        "P18_RELATIONSHIP_POLICY_TENANT_MISMATCH"
    )


def test_wrong_policy_context_is_distinguished_and_blocked():
    db = db_engine()
    state = make_state(db)
    create_policy(state, context="ctx-p18-old")

    decision = state["p18"].resolve(
        requirement=requirement(state),
        principal=state["principal"],
    )
    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_CONTEXT
    )


def test_wrong_exact_scope_is_distinguished_and_blocked():
    db = db_engine()
    state = make_state(db)
    create_policy(
        state,
        scope={"period": "2026-05", "population": "sales_orders"},
    )

    decision = state["p18"].resolve(
        requirement=requirement(state),
        principal=state["principal"],
    )
    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_SCOPE
    )


def test_wrong_source_target_business_refs_are_rejected_not_fuzzily_matched():
    db = db_engine()
    state = make_state(db)
    create_policy(state)

    with pytest.raises(
        BusinessRelationshipPolicyError,
        match="P18_POLICY_BUSINESS_REF_MISMATCH",
    ):
        state["p18"].resolve(
            requirement=requirement(
                state,
                source="business:invoice",
            ),
            principal=state["principal"],
        )


def test_requirement_context_must_match_sealed_research_context():
    db = db_engine()
    state = make_state(db)

    with pytest.raises(
        BusinessRelationshipPolicyError,
        match="P18_REQUIREMENT_CONTEXT_MISMATCH",
    ):
        state["p18"].resolve(
            requirement=requirement(state, context="ctx-other"),
            principal=state["principal"],
        )


def test_claim_from_another_session_is_rejected():
    db = db_engine()
    state = make_state(db, suffix="a")
    other = make_state(db, suffix="b")

    with pytest.raises(
        BusinessRelationshipPolicyError,
        match="P18_CLAIM_SESSION_MISMATCH",
    ):
        state["p18"].resolve(
            requirement=requirement(
                state,
                claim_id=other["claim"].claim_id,
            ),
            principal=state["principal"],
        )


def test_reasoning_step_from_another_session_is_rejected():
    db = db_engine()
    state = make_state(db, suffix="a")
    other = make_state(db, suffix="b")

    with pytest.raises(
        BusinessRelationshipPolicyError,
        match="P18_REASONING_SESSION_MISMATCH",
    ):
        state["p18"].resolve(
            requirement=requirement(
                state,
                step_id=other["step_id"],
            ),
            principal=state["principal"],
        )


def test_reasoning_step_from_another_obligation_is_rejected():
    db = db_engine()
    state = make_state(
        db,
        obligations=("g1", "g2"),
        step_obligation="g2",
    )

    with pytest.raises(
        BusinessRelationshipPolicyError,
        match="P18_REASONING_OBLIGATION_MISMATCH",
    ):
        state["p18"].resolve(
            requirement=requirement(state, obligation="g1"),
            principal=state["principal"],
        )


def test_restart_same_satisfied_requirement_reuses_one_policy_use():
    db = db_engine()
    state = make_state(db)
    create_policy(state)
    req = requirement(state)
    first = state["p18"].resolve(
        requirement=req,
        principal=state["principal"],
    )
    second = state["p18"].resolve(
        requirement=req,
        principal=state["principal"],
    )

    assert first == second
    with Session(db) as s:
        uses = s.exec(select(BusinessRelationshipPolicyUseRecord)).all()
    assert len(uses) == 1


def test_restart_same_blocked_requirement_reuses_one_policy_use():
    db = db_engine()
    state = make_state(db)
    req = requirement(state)
    first = state["p18"].resolve(
        requirement=req,
        principal=state["principal"],
    )
    second = state["p18"].resolve(
        requirement=req,
        principal=state["principal"],
    )

    assert first == second
    with Session(db) as s:
        uses = s.exec(select(BusinessRelationshipPolicyUseRecord)).all()
    assert len(uses) == 1


def test_retirement_keeps_historical_satisfied_use_immutable():
    db = db_engine()
    state = make_state(db)
    policy = create_policy(state)
    req = requirement(state)
    satisfied = state["p18"].resolve(
        requirement=req,
        principal=state["principal"],
    )
    state["p18"].retire_policy(
        policy_id=policy.policy_id,
        principal=state["principal"],
    )
    blocked = state["p18"].resolve(
        requirement=req,
        principal=state["principal"],
    )
    historical = state["p18"].load_use(
        session_id=state["session"].session_id,
        policy_use_id=satisfied.policy_use_id,
        principal=state["principal"],
    )

    assert satisfied.policy_use_id != blocked.policy_use_id
    assert (
        historical.resolution_status
        == RelationshipPolicyResolutionStatus.SATISFIED
    )
    assert historical.policy_id == policy.policy_id
    assert (
        blocked.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_RETIRED
    )


def test_new_semantic_context_does_not_reuse_old_policy_authority():
    db = db_engine()
    old = make_state(db, suffix="old", context="ctx-p18-v1")
    create_policy(old)
    new = make_state(db, suffix="new", context="ctx-p18-v2")

    decision = new["p18"].resolve(
        requirement=requirement(new),
        principal=new["principal"],
    )
    assert (
        decision.resolution_status
        == RelationshipPolicyResolutionStatus.BLOCKED_CONTEXT
    )


def test_p18_records_reference_sealed_truth_without_copying_it():
    db = db_engine()
    state = make_state(db)
    create_policy(state)
    state["p18"].resolve(
        requirement=requirement(state),
        principal=state["principal"],
    )

    policy_fields = set(BusinessRelationshipPolicyRecord.model_fields)
    use_fields = set(BusinessRelationshipPolicyUseRecord.model_fields)
    forbidden_policy = {
        "metabase_table_id",
        "metabase_field_id",
        "foreign_key_field_id",
        "source_column",
        "target_column",
        "join_condition",
        "join_type",
        "preferred_join",
        "join_path",
        "cardinality",
    }
    forbidden_copy = {
        "claim_text",
        "p17_objective",
        "p17_topology",
        "evidence_payload",
        "native_material",
    }
    assert forbidden_policy.isdisjoint(policy_fields)
    assert forbidden_copy.isdisjoint(policy_fields | use_fields)
    assert "claim_id" in use_fields
    assert "reasoning_step_id" in use_fields
    assert "requirement_fingerprint" in use_fields


def test_p18_has_exactly_two_durable_tables_and_requirement_is_transient():
    p18_tables = {
        table.name
        for table in SQLModel.metadata.tables.values()
        if table.name.startswith("business_relationship_policy")
    }
    assert p18_tables == {
        "business_relationship_policy",
        "business_relationship_policy_use",
    }
    assert "relationship_policy_requirement" not in SQLModel.metadata.tables


def test_p18_production_module_has_no_analytical_or_causal_dependency():
    path = Path("app/v3/business_relationship_policy.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")

    forbidden_prefixes = (
        "app.v3.substrate.metabase",
        "app.v3.research_native_gateway",
        "app.v3.research_followup",
        "app.v3.native_execution",
        "app.wren",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
    )
    assert not any(
        name.startswith(forbidden_prefixes)
        for name in imported
    )
    for forbidden in (
        "NativeEngineBridge",
        "MetabaseAgentClient",
        "execute_dataset",
        "explore_adhoc",
        "attest_native_query",
        "execute_native_query",
        "wren_service",
        "causal_confidence",
        "root_cause",
    ):
        assert forbidden not in source
