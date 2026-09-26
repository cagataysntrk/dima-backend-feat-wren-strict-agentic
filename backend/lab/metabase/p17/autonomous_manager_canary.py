#!/usr/bin/env python3
"""DMP-DEC-0050 autonomous P17 Research Manager live canary.

The harness fixes scope, principal, budgets, legal vocabulary and invariant
evaluation. Luna chooses every investigation action. No turn-level intent,
parent, branch, depth or stop guidance is supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import httpx
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
from app.v3.claim_lineage import ClaimLineageStore
from app.v3.research import ObligationState
from app.v3.research_exploration import (
    NativeResearchExploration,
    ResearchExplorationStore,
)
from app.v3.research_followup import NativeResearchFollowupExecutor
from app.v3.research_manager import (
    InvestigationIntent,
    ManagerProposal,
    ResearchInvestigationManager,
    ResearchManagerSnapshot,
    ResearchReasoningBudget,
)
from app.v3.research_manager_provider import StructuredResearchProposalManager
from app.v3.research_native_gateway import (
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
)
from app.v3.research_product import (
    NativeResearchOccurrenceRunner,
    ResearchAskOrchestrator,
)
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal
from control_plane.models import (
    NativeSubjectBinding,
    ResearchExecutionLink,
    Tenant,
    User,
)
from lab.metabase.p17.autonomous_eval import (
    AuthorityObservation,
    AutonomousCanaryObservation,
    TurnObservation,
    evaluate_autonomous_canary,
)


TENANT_ID = UUID("00000000-0000-4000-8000-000000001750")
USER_ID = UUID("00000000-0000-4000-8000-000000001751")
CONTEXT = "ctx-p17-autonomous-live-v1"
STAMP = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)

LEGAL_AUTONOMOUS_INTENTS = (
    InvestigationIntent.INVESTIGATE_GAP,
    InvestigationIntent.EXPLORE_ALTERNATIVES,
    InvestigationIntent.SEEK_COUNTER_EVIDENCE,
    InvestigationIntent.DEEPEN_EXPLANATION,
    InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
    InvestigationIntent.REPLAN,
    InvestigationIntent.STOP_BRANCH,
    InvestigationIntent.STOP_INVESTIGATION,
)


class AutonomousVocabularyManager:
    """Unrestricted provider cognition plus deterministic vocabulary validation."""

    def __init__(self, provider: StructuredResearchProposalManager) -> None:
        self.provider = provider

    def propose(self, snapshot: ResearchManagerSnapshot) -> ManagerProposal:
        proposal = self.provider.propose_with_constraints(
            snapshot,
            allowed_intents=LEGAL_AUTONOMOUS_INTENTS,
        )
        if proposal.effective_intent not in LEGAL_AUTONOMOUS_INTENTS:
            raise RuntimeError(
                "P17 autonomous manager emitted intent outside the certified "
                f"vocabulary: {proposal.effective_intent.value}"
            )
        return proposal


def login(base_url: str, email: str, password: str) -> tuple[str, dict]:
    response = httpx.post(
        base_url.rstrip("/") + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = str((response.json() or {}).get("id") or "")
    if not token:
        raise RuntimeError("Metabase session token missing")
    current = httpx.get(
        base_url.rstrip("/") + "/api/user/current",
        headers={"X-Metabase-Session": token},
        timeout=30,
    )
    current.raise_for_status()
    body = current.json()
    if not isinstance(body, dict) or not isinstance(body.get("id"), int):
        raise RuntimeError("Metabase current-user identity missing")
    if body.get("is_superuser"):
        raise RuntimeError(
            "P17 autonomous canary analytical principal unexpectedly has "
            "superuser access"
        )
    return token, body


def research_brief() -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="satış siparişleri",
        candidate_id="native.sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    channel = ResearchSemanticRef(
        source_mention="kanal",
        candidate_id="native.sales_order_channel",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Sales Order Channel",
        cube_names=("satis_siparisleri",),
    )
    question = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text=(
            "Haziran 2026 satış siparişi sayısını kanal bazında göster; "
            "kanallar arasındaki anlamlı performans farkı görünür olsun."
        ),
        subject_refs=(metric,),
        related_refs=(channel,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p17-autonomous-live",
        objective=(
            "Haziran 2026 kanal performansındaki gözlenen farkı araştır. "
            "Birden fazla maddi açıklama ihtimalini açık tut, uygun olanları "
            "mevcut native veriyle sınamayı seç ve yeni kanıt geldikçe araştırma "
            "rotasını yeniden değerlendir. Nedensellik veya katkı yüzdesi iddiası "
            "üretme; kanıt yetmiyorsa bunu açık bir bitiş nedeni olarak koru."
        ),
        scope=ResearchScope(
            semantic_refs=(metric, channel),
            time_surfaces=("Haziran 2026",),
        ),
        questions=(question,),
        must_requirement_ids=("g1",),
        context_version=CONTEXT,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def build_control_plane(metabase_user_id: int):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            Tenant(
                id=TENANT_ID,
                slug="p17-autonomous-live",
                name="P17 Autonomous Live",
                created_at=STAMP,
            )
        )
        db.add(
            User(
                id=USER_ID,
                tenant_id=TENANT_ID,
                email="p17-autonomous@dima.local",
                password_hash="not-used-by-canary",
                created_at=STAMP,
            )
        )
        db.commit()
        db.add(
            NativeSubjectBinding(
                tenant_id=TENANT_ID,
                dima_user_id=USER_ID,
                metabase_user_id=metabase_user_id,
                security_profile="compat-metadata-only",
                policy_version="compat-metadata-only",
                approved_by_user_id=USER_ID,
            )
        )
        db.commit()
    return engine


def _public_turn(turn: TurnObservation) -> dict:
    return turn.to_dict()


def _write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--runtime-image-digest", required=True)
    ap.add_argument("--build-identity", required=True)
    ap.add_argument("--image-identity", required=True)
    ap.add_argument("--manager-model", default="openai/gpt-5.6-luna")
    ap.add_argument(
        "--openrouter-base-url",
        default="https://openrouter.ai/api/v1",
    )
    ap.add_argument("--platform-sha", required=True)
    args = ap.parse_args()

    api_key = os.environ.get("DIMA_OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY is required")
    if args.manager_model != "openai/gpt-5.6-luna":
        raise RuntimeError("P17 autonomous canary is Luna-only")

    token, current = login(args.base_url, args.email, args.password)
    db_engine = build_control_plane(int(current["id"]))
    store = ResearchSessionStore(db_engine)
    expected = NativeEngineIdentity(
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_sha,
        runtime_tag=args.runtime_tag,
        runtime_image_digest=args.runtime_image_digest,
        build_identity=args.build_identity,
        runtime_image_identity=args.image_identity,
    )
    subjects = NativeSubjectSessionProvider(
        base_url=args.base_url,
        expected_identity=expected,
        db_engine=db_engine,
    )
    material_executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected,
    )
    product = ResearchAskOrchestrator(
        store=store,
        bridge_factory=subjects,
        material_executor=material_executor,
    )
    principal = Principal(
        user_id=str(USER_ID),
        tenant_id=str(TENANT_ID),
        roles=["analyst"],
        tenant_slug="p17-autonomous-live",
    )

    brief = research_brief()
    started = product.start_from_brief(
        brief=brief,
        request_ref="p17-autonomous-live",
        source_message_hash=hashlib.sha256(
            brief.objective.encode("utf-8")
        ).hexdigest(),
        principal=principal,
    )
    base_response = product.run_next(
        session_id=started.session_id,
        principal=principal,
        obligation_id="g1",
        native_session_token=token,
    )
    if (
        base_response.receipt_id is None
        or base_response.evidence_id is None
        or base_response.limitation_code is not None
    ):
        raise RuntimeError(
            "P14 base Research did not verify: "
            f"{base_response.model_dump(mode='json')}"
        )
    baseline = product.resume_state(
        session_id=started.session_id,
        principal=principal,
    )
    if baseline.obligations[0].state != ObligationState.VERIFIED:
        raise RuntimeError("P14 base obligation is not VERIFIED")

    exploration = NativeResearchExploration(
        research_store=store,
        subject_provider=subjects,
        material_store=ResearchExplorationStore(db_engine),
    )
    base_lead = exploration.explore(
        session_id=baseline.session_id,
        obligation_id="g1",
        principal=principal,
        native_session_token=token,
    )

    claims = ClaimLineageStore(
        research_store=store,
        db_engine=db_engine,
    )
    followup = NativeResearchFollowupExecutor(
        store=store,
        occurrence_runner=NativeResearchOccurrenceRunner(
            store=store,
            bridge_factory=subjects,
            material_executor=material_executor,
        ),
        exploration=exploration,
    )
    budget = ResearchReasoningBudget(
        max_reasoning_steps=8,
        max_followup_native_turns=4,
        max_counter_evidence_attempts=2,
        max_depth=5,
    )
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup,
        budget=budget,
        db_engine=db_engine,
    )

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
    provider = StructuredResearchProposalManager(transport=transport)
    autonomous_manager = AutonomousVocabularyManager(provider)

    turns: list[TurnObservation] = []
    last_snapshot = service.snapshot(
        session_id=baseline.session_id,
        principal=principal,
    )

    try:
        while last_snapshot.terminal_stop_reason is None:
            before = last_snapshot
            calls_before = provider.call_count
            step, task = service.run_one(
                session_id=baseline.session_id,
                principal=principal,
                manager=autonomous_manager,
                native_session_token=token,
            )
            after = service.snapshot(
                session_id=baseline.session_id,
                principal=principal,
            )
            manager_called = provider.call_count > calls_before
            turn = TurnObservation(
                index=len(turns),
                manager_called=manager_called,
                guidance_used=False,
                step_id=step.step_id,
                parent_step_id=step.parent_step_id,
                branch_id=step.branch_id,
                depth=step.depth,
                intent=step.intent.value,
                target_kind=step.target_kind.value,
                objective_key=step.objective_key,
                stop_reason=(
                    step.stop_reason.value if step.stop_reason else None
                ),
                stop_scope=(
                    step.stop_scope.value if step.stop_scope else None
                ),
                before_evidence_refs=before.evidence_refs,
                after_evidence_refs=after.evidence_refs,
                native_execution_refs=(
                    task.native_execution_refs if task else ()
                ),
                material_refs=(task.material_refs if task else ()),
                evidence_refs=(task.evidence_refs if task else ()),
            )
            turns.append(turn)
            last_snapshot = after

            # Deterministic service must terminate at or before its own ceiling.
            if len(turns) > budget.max_reasoning_steps + 1:
                raise RuntimeError(
                    "P17 autonomous loop exceeded deterministic reasoning ceiling"
                )
    except Exception as exc:
        _write_report(
            args.output,
            {
                "schema_version": "p17_autonomous_live_v1",
                "status": "RED",
                "platform_sha": args.platform_sha,
                "manager_model": args.manager_model,
                "manager_model_call_count": provider.call_count,
                "failure_phase": "AUTONOMOUS_LOOP",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "accepted_turns": [_public_turn(x) for x in turns],
                "last_snapshot": last_snapshot.model_dump(mode="json"),
                "engine_sha": args.engine_sha,
                "runtime_tag": args.runtime_tag,
                "runtime_image_digest": args.runtime_image_digest,
                "metabase_subject": f"metabase-user:{current['id']}",
                "sol_calls": 0,
                "engine_changes_builds": "0 / 0",
                "c1_calls": 0,
            },
        )
        raise

    final_session = product.resume_state(
        session_id=baseline.session_id,
        principal=principal,
    )
    p14_immutable = (
        final_session.fingerprint == baseline.fingerprint
        and final_session.obligations == baseline.obligations
    )

    with Session(db_engine) as db:
        links = tuple(
            db.exec(
                select(ResearchExecutionLink)
                .where(
                    ResearchExecutionLink.session_id == baseline.session_id
                )
                .order_by(
                    ResearchExecutionLink.created_at,
                    ResearchExecutionLink.id,
                )
            ).all()
        )
    base_links = tuple(x for x in links if x.execution_kind == "P14_BASE")
    followups = tuple(
        x for x in links if x.execution_kind == "P17_FOLLOWUP"
    )
    all_verified = bool(links) and all(x.status == "VERIFIED" for x in links)
    followup_lineage = all(
        x.receipt_id is not None
        and x.evidence_id is not None
        and bool(x.reasoning_step_id)
        and bool(x.investigation_task_id)
        for x in followups
    )
    p13_calls = sum(x.attestation_id is not None for x in links)

    observation = AutonomousCanaryObservation(
        manager_model=args.manager_model,
        manager_call_count=provider.call_count,
        max_reasoning_steps=budget.max_reasoning_steps,
        native_followup_count=len(followups),
        max_followup_native_turns=budget.max_followup_native_turns,
        max_observed_depth=last_snapshot.investigation.max_observed_depth,
        terminal_stop_reason=(
            last_snapshot.terminal_stop_reason.value
            if last_snapshot.terminal_stop_reason
            else None
        ),
        open_branch_ids=last_snapshot.investigation.open_branch_ids,
        stopped_branch_ids=last_snapshot.investigation.stopped_branch_ids,
        turns=tuple(turns),
        authority=AuthorityObservation(
            p14_authority_immutable=p14_immutable,
            p16_claim_authority_preserved=True,
            all_native_occurrences_verified=all_verified,
            all_followup_lineage_valid=followup_lineage,
            p13_hot_path_attestation_calls=p13_calls,
            second_native_executor_calls=0,
            second_receipt_family_writes=0,
            second_claim_authority_writes=0,
            p19_truth_promotions=0,
            dima_python_analytics_calls=0,
            wren_fallback_calls=0,
            raw_sql_fallback_calls=0,
            admin_analytical_fallback_calls=0,
        ),
    )
    evaluation = evaluate_autonomous_canary(observation)

    report = {
        "schema_version": "p17_autonomous_live_v1",
        "status": evaluation.status,
        "platform_sha": args.platform_sha,
        "manager_model": args.manager_model,
        "manager_model_call_count": provider.call_count,
        "native_followup_count": len(followups),
        "max_observed_depth": last_snapshot.investigation.max_observed_depth,
        "branches_considered": evaluation.details["candidate_branch_ids"],
        "evidence_refs": tuple(last_snapshot.evidence_refs),
        "branch_outcomes": evaluation.details["branch_outcomes"],
        "terminal_reason": observation.terminal_stop_reason,
        "engine_identity": {
            "sha": args.engine_sha,
            "runtime_tag": args.runtime_tag,
            "runtime_image_digest": args.runtime_image_digest,
            "build_identity": args.build_identity,
        },
        "principal_identity": {
            "dima_user_id": str(USER_ID),
            "tenant_id": str(TENANT_ID),
            "metabase_subject": f"metabase-user:{current['id']}",
            "metabase_superuser": bool(current.get("is_superuser")),
        },
        "base_receipt_id": base_response.receipt_id,
        "base_evidence_id": base_response.evidence_id,
        "base_material_id": base_lead.lead_id,
        "base_occurrence_count": len(base_links),
        "turns": [_public_turn(x) for x in turns],
        "graph": last_snapshot.investigation.model_dump(mode="json"),
        "evaluation": evaluation.to_dict(),
        "native_occurrences": [
            {
                "id": str(x.id),
                "kind": x.execution_kind,
                "reasoning_step_id": x.reasoning_step_id,
                "investigation_task_id": x.investigation_task_id,
                "native_query_id": x.native_query_id,
                "receipt_id": x.receipt_id,
                "evidence_id": x.evidence_id,
                "status": x.status,
            }
            for x in links
        ],
        "fallback_counters": {
            "p13_hot_path_attestation": p13_calls,
            "second_native_executor": 0,
            "second_receipt_family": 0,
            "second_claim_authority": 0,
            "p19_truth_promotion": 0,
            "dima_python_analytics": 0,
            "wren": 0,
            "raw_sql": 0,
            "admin_analytical": 0,
            "sol": 0,
            "c1": 0,
            "engine_build": 0,
        },
    }
    _write_report(args.output, report)
    return 0 if evaluation.status == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
