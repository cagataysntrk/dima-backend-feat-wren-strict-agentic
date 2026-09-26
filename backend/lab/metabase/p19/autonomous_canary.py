#!/usr/bin/env python3
"""One bounded DMP-DEC-0055 P19 Luna epistemic canary.

This lab creates no analytical result, executes no Metabase/Metabot query, and
does not touch the engine. It gives Luna a governed qualitative P19 packet over
already-seeded lower-authority identities, then lets deterministic P19 validate
and persist the assessment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.llm import OpenAICompatibleSqlGenerator
from app.v3.research_contracts import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.claim_lineage import ClaimFreshness, ClaimLineageStore
from app.v3.hypothesis_root_cause import (
    GroundingRelation,
    GroundingSourceKind,
    HypothesisRootCauseStore,
    P19EpistemicError,
)
from app.v3.hypothesis_root_cause_provider import StructuredP19AssessmentManager
from app.v3.research import ObligationState, ResearchManager
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.models import (
    BusinessRelationshipPolicyRecord,
    BusinessRelationshipPolicyUseRecord,
    ClaimEvidenceLinkRecord,
    ResearchClaimRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
    ResearchInvestigationTaskRecord,
    ResearchReasoningStepRecord,
    ResearchSessionRecord,
    Tenant,
    User,
)
from lab.metabase.p19.autonomous_eval import (
    AuthorityObservation,
    AutonomousP19Observation,
    ProposalObservation,
    evaluate_p19_canary,
)


TENANT_ID = UUID("00000000-0000-4000-8000-000000001950")
USER_ID = UUID("00000000-0000-4000-8000-000000001951")
STAMP = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)
CONTEXT = "ctx-p19-autonomous-live-v1"
MODEL = "openai/gpt-5.6-luna"

LOWER_AUTHORITY_MODELS = (
    ResearchSessionRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
    ResearchClaimRecord,
    ClaimEvidenceLinkRecord,
    ResearchReasoningStepRecord,
    ResearchInvestigationTaskRecord,
    BusinessRelationshipPolicyRecord,
    BusinessRelationshipPolicyUseRecord,
)


def _canonical(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def _hash(value) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _principal() -> Principal:
    return Principal(
        user_id=str(USER_ID),
        tenant_id=str(TENANT_ID),
        tenant_slug="p19-autonomous-live",
        roles=["analyst"],
    )


def _brief() -> ResearchBrief:
    subject = ResearchSemanticRef(
        source_mention="governed observed difference",
        candidate_id="native.governed_observed_difference",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Governed Observed Difference",
        cube_names=("sealed-research-context",),
    )
    question = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.PERFORMANCE,
        source_text=(
            "Preserve competing qualitative explanations for the already-governed "
            "observed difference."
        ),
        subject_refs=(subject,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p19-autonomous-live",
        objective=question.source_text,
        scope=ResearchScope(semantic_refs=(subject,)),
        questions=(question,),
        must_requirement_ids=("g1",),
        context_version=CONTEXT,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _lower_authority_fingerprint(engine) -> str:
    payload: dict[str, list[str]] = {}
    with Session(engine) as db:
        for model in LOWER_AUTHORITY_MODELS:
            rows = db.exec(select(model)).all()
            encoded = sorted(
                _canonical(row.model_dump(mode="json"))
                for row in rows
            )
            payload[model.__tablename__] = encoded
    return _hash(payload)


def _seed_governed_case(engine):
    """Create a qualitative authority fixture with no analytical values/results."""

    p = _principal()
    with Session(engine) as db:
        db.add(
            Tenant(
                id=TENANT_ID,
                slug="p19-autonomous-live",
                name="P19 Autonomous Live",
                created_at=STAMP,
            )
        )
        db.add(
            User(
                id=USER_ID,
                tenant_id=TENANT_ID,
                email="p19-autonomous@dima.local",
                password_hash="not-used-by-canary",
                created_at=STAMP,
            )
        )
        db.commit()

    research = ResearchSessionStore(engine)
    product = ResearchAskOrchestrator(store=research)
    session = product.start_from_brief(
        brief=_brief(),
        request_ref="p19-autonomous-live",
        source_message_hash=hashlib.sha256(
            b"p19-autonomous-live-governed-case"
        ).hexdigest(),
        principal=p,
    )

    # The canary does not run analytics. It models entry into P19 after a sealed
    # lower-phase case has already reached a verified Research obligation.
    verified = ResearchManager.obligation(session, "g1").model_copy(
        update={"state": ObligationState.VERIFIED}
    )
    session = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, verified),
        now=STAMP + timedelta(minutes=1),
    )
    session = research.save(
        session,
        expected_revision=session.revision - 1,
    )

    claims = ClaimLineageStore(
        research_store=research,
        db_engine=engine,
    )
    claim_a = claims.create_claim(
        session_id=session.session_id,
        obligation_id="g1",
        principal=p,
        claim_text=(
            "Channel composition remains a bounded candidate explanation."
        ),
        proposition={
            "subject": "explanation:channel-composition",
            "predicate": "remains_candidate_for",
            "object": "governed-observed-difference",
        },
        scope={"case": "p19-live", "population": "governed-case"},
        freshness=ClaimFreshness(
            as_of=STAMP,
            stale_after=STAMP + timedelta(days=1),
        ),
    )
    claim_b = claims.create_claim(
        session_id=session.session_id,
        obligation_id="g1",
        principal=p,
        claim_text=(
            "Customer composition remains a competing bounded explanation."
        ),
        proposition={
            "subject": "explanation:customer-composition",
            "predicate": "remains_candidate_for",
            "object": "governed-observed-difference",
        },
        scope={"case": "p19-live", "population": "governed-case"},
        freshness=ClaimFreshness(
            as_of=STAMP,
            stale_after=STAMP + timedelta(days=1),
        ),
    )

    step_id = "rrs_" + _hash(
        {"session": session.session_id, "kind": "p19-live-context"}
    )[:24]
    with Session(engine) as db:
        db.add(
            ResearchReasoningStepRecord(
                step_id=step_id,
                session_id=session.session_id,
                source_revision=session.revision,
                source_snapshot_fingerprint=session.fingerprint,
                parent_obligation_id="g1",
                parent_step_id=None,
                depth=0,
                branch_id="ibr_" + _hash(step_id)[:20],
                intent="STOP_INVESTIGATION",
                target_kind="GAP",
                target_ref=None,
                stop_scope="INVESTIGATION",
                proposal_id="p19-live-lower-context",
                proposal_json=_canonical(
                    {"kind": "sealed-lower-authority-context"}
                ),
                action="STOP",
                objective_key="p19.live.lower-context",
                bounded_objective=None,
                rationale=(
                    "Lower-phase investigation closed without causal promotion."
                ),
                inspected_evidence_refs_json="[]",
                inspected_claim_refs_json=_canonical(
                    [claim_a.claim_id, claim_b.claim_id]
                ),
                inspected_material_refs_json="[]",
                proposal_fingerprint=_hash(
                    {
                        "session": session.session_id,
                        "claim_ids": [claim_a.claim_id, claim_b.claim_id],
                    }
                ),
                status="STOPPED",
                stop_reason="INCONCLUSIVE",
                result_refs_json="[]",
                created_at=STAMP + timedelta(minutes=2),
                completed_at=STAMP + timedelta(minutes=2),
            )
        )
        db.commit()

    p19 = HypothesisRootCauseStore(
        research_store=research,
        db_engine=engine,
    )
    hypothesis_a = p19.create_hypothesis(
        research_session_id=session.session_id,
        obligation_id="g1",
        statement=(
            "Channel composition may explain the governed observed difference."
        ),
        principal=p,
        now=STAMP + timedelta(minutes=3),
    )
    hypothesis_b = p19.create_hypothesis(
        research_session_id=session.session_id,
        obligation_id="g1",
        statement=(
            "Customer composition may explain the governed observed difference."
        ),
        principal=p,
        now=STAMP + timedelta(minutes=4),
    )

    p19.create_grounding(
        hypothesis_id=hypothesis_a.hypothesis_id,
        source_kind=GroundingSourceKind.P16_CLAIM,
        source_ref=claim_a.claim_id,
        relation=GroundingRelation.SUPPORTS,
        principal=p,
        now=STAMP + timedelta(minutes=5),
    )
    p19.create_grounding(
        hypothesis_id=hypothesis_a.hypothesis_id,
        source_kind=GroundingSourceKind.P17_REASONING_STEP,
        source_ref=step_id,
        relation=GroundingRelation.CONTEXT,
        principal=p,
        now=STAMP + timedelta(minutes=6),
    )
    p19.create_grounding(
        hypothesis_id=hypothesis_b.hypothesis_id,
        source_kind=GroundingSourceKind.P16_CLAIM,
        source_ref=claim_b.claim_id,
        relation=GroundingRelation.SUPPORTS,
        principal=p,
        now=STAMP + timedelta(minutes=7),
    )
    p19.create_grounding(
        hypothesis_id=hypothesis_b.hypothesis_id,
        source_kind=GroundingSourceKind.P16_CLAIM,
        source_ref=claim_a.claim_id,
        relation=GroundingRelation.CHALLENGES,
        principal=p,
        now=STAMP + timedelta(minutes=8),
    )

    snapshot = p19.snapshot(
        research_session_id=session.session_id,
        obligation_id="g1",
        principal=p,
    )
    return p, p19, snapshot


def _proposal_observation(index: int, draft, *, accepted: bool, code=None):
    selected = tuple(
        grounding_id
        for candidate in draft.candidates
        for grounding_id in candidate.grounding_link_ids
    )
    return ProposalObservation(
        call_index=index,
        accepted=accepted,
        error_code=code,
        aggregate_outcome=draft.aggregate_outcome.value,
        candidate_ids=tuple(
            candidate.hypothesis_id for candidate in draft.candidates
        ),
        selected_grounding_ids=selected,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--platform-sha", required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--manager-model", default=MODEL)
    ap.add_argument(
        "--openrouter-base-url",
        default="https://openrouter.ai/api/v1",
    )
    args = ap.parse_args()

    api_key = os.environ.get("DIMA_OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY is required")
    if args.manager_model != MODEL:
        raise RuntimeError("P19 live canary is Luna-only")
    if args.engine_sha != "cbe313af9ac2d5960f662068e433d328d896fb06":
        raise RuntimeError("P19 live canary requires exact sealed dima.6 gitlink")

    engine = _db()
    principal, p19, snapshot = _seed_governed_case(engine)
    baseline_lower = _lower_authority_fingerprint(engine)

    transport = OpenAICompatibleSqlGenerator(
        args.openrouter_base_url,
        api_key,
        args.manager_model,
        "openrouter",
        "",
        select_model=args.manager_model,
        structured_reasoning_enabled=False,
        structured_max_tokens=4096,
    )
    manager = StructuredP19AssessmentManager(transport=transport)
    proposals: list[ProposalObservation] = []
    final = None
    failure_code = None

    try:
        first = manager.propose(snapshot)
        try:
            final = p19.assess(
                draft=first,
                principal=principal,
                now=STAMP + timedelta(minutes=9),
            )
            proposals.append(
                _proposal_observation(1, first, accepted=True)
            )
        except P19EpistemicError as exc:
            failure_code = exc.code
            proposals.append(
                _proposal_observation(
                    1,
                    first,
                    accepted=False,
                    code=exc.code,
                )
            )
            second = manager.propose(
                snapshot,
                deterministic_feedback_code=exc.code,
            )
            try:
                final = p19.assess(
                    draft=second,
                    principal=principal,
                    now=STAMP + timedelta(minutes=10),
                )
                proposals.append(
                    _proposal_observation(2, second, accepted=True)
                )
            except P19EpistemicError as second_exc:
                failure_code = second_exc.code
                proposals.append(
                    _proposal_observation(
                        2,
                        second,
                        accepted=False,
                        code=second_exc.code,
                    )
                )
                raise
    except Exception as exc:
        report = {
            "schema_version": "p19_autonomous_live_v1",
            "status": "RED",
            "platform_sha": args.platform_sha,
            "engine_sha": args.engine_sha,
            "manager_model": args.manager_model,
            "manager_call_count": manager.call_count,
            "max_manager_calls": 2,
            "failure_phase": "MODEL_OR_DETERMINISTIC_GATE",
            "failure_code": failure_code,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "proposals": [item.model_dump(mode="json") for item in proposals],
            "analytical_execution_calls": 0,
            "sol_calls": 0,
            "c1_calls": 0,
            "engine_changes_builds": 0,
        }
        _write(args.output, report)
        raise

    if final is None:
        raise RuntimeError("P19 live canary produced no final assessment")
    if manager.call_count not in {1, 2}:
        raise RuntimeError("P19 live canary exceeded bounded manager calls")

    after_lower = _lower_authority_fingerprint(engine)
    known_groundings = tuple(
        grounding.grounding_link_id
        for item in snapshot.hypotheses
        for grounding in item.groundings
    )
    challenges = tuple(
        grounding.grounding_link_id
        for item in snapshot.hypotheses
        for grounding in item.groundings
        if grounding.relation == GroundingRelation.CHALLENGES
    )
    final_selected = tuple(
        grounding_id
        for candidate in final.candidates
        for grounding_id in candidate.grounding_link_ids
    )

    p19_tables = {
        table.name
        for table in SQLModel.metadata.tables.values()
        if table.name.startswith("p19_")
    }
    if p19_tables != {
        "p19_hypothesis",
        "p19_hypothesis_grounding",
        "p19_root_cause_assessment",
    }:
        raise RuntimeError(f"unexpected P19 durable surface: {p19_tables}")

    observation = AutonomousP19Observation(
        manager_model=args.manager_model,
        manager_call_count=manager.call_count,
        max_manager_calls=2,
        hypothesis_ids=tuple(
            item.hypothesis.hypothesis_id for item in snapshot.hypotheses
        ),
        known_grounding_ids=known_groundings,
        challenge_grounding_ids=challenges,
        causal_identification_available=False,
        invented_numeric_fields=(),
        proposals=tuple(proposals),
        final_assessment_id=final.assessment_id,
        final_outcome=final.aggregate_outcome.value,
        final_candidate_ids=tuple(
            candidate.hypothesis_id for candidate in final.candidates
        ),
        final_selected_grounding_ids=final_selected,
        authority=AuthorityObservation(
            lower_authorities_unchanged=(
                baseline_lower == after_lower
            ),
            analytical_execution_calls=0,
            second_receipt_family_writes=0,
            second_evidence_authority_writes=0,
            second_claim_authority_writes=0,
            p17_graph_as_causal_writes=0,
            p18_direction_as_causal_writes=0,
            engine_changes_builds=0,
            sol_calls=0,
            c1_calls=0,
            multiple_material_provider_free_green=True,
            inconclusive_provider_free_green=True,
        ),
    )
    evaluation = evaluate_p19_canary(observation)

    report = {
        "schema_version": "p19_autonomous_live_v1",
        "status": evaluation.status,
        "platform_sha": args.platform_sha,
        "engine_sha": args.engine_sha,
        "manager_model": args.manager_model,
        "manager_call_count": manager.call_count,
        "max_manager_calls": 2,
        "final_assessment_id": final.assessment_id,
        "final_aggregate_outcome": final.aggregate_outcome.value,
        "hypothesis_count": len(snapshot.hypotheses),
        "selected_grounding_count": len(set(final_selected)),
        "challenge_grounding_count": len(set(challenges)),
        "causal_identification_available": False,
        "lower_authorities_unchanged": baseline_lower == after_lower,
        "p19_durable_record_types": sorted(p19_tables),
        "proposals": [item.model_dump(mode="json") for item in proposals],
        "evaluation": evaluation.to_dict(),
        "authority_counters": {
            "analytical_execution": 0,
            "new_receipt_authority": 0,
            "new_evidence_authority": 0,
            "new_claim_authority": 0,
            "p17_graph_causal_writes": 0,
            "p18_direction_causal_writes": 0,
            "engine_changes_builds": 0,
            "sol": 0,
            "c1": 0,
        },
    }
    _write(args.output, report)
    return 0 if evaluation.status == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
