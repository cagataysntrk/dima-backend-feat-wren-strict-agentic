#!/usr/bin/env python3
"""Historical deterministic P17 scenario / contract lab.

This scripted trajectory is retained as DMP-DEC-0049 contract evidence only.
It is not an autonomous cognition certification oracle under DMP-DEC-0050.
Turn-level guidance is intentional here because this file tests one scenario.
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
from app.v3.claim_lineage import ClaimLineageStore
from app.v3.research import ObligationState
from app.v3.research_exploration import (
    NativeResearchExploration,
    ResearchExplorationStore,
)
from app.v3.research_followup import NativeResearchFollowupExecutor
from app.v3.research_manager import (
    InvestigationIntent,
    ManagerStopReason,
    ResearchInvestigationManager,
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


TENANT_ID = UUID("00000000-0000-4000-8000-000000001701")
USER_ID = UUID("00000000-0000-4000-8000-000000001702")
CONTEXT = "ctx-p17-recursive-live-v1"
STAMP = datetime(2026, 9, 25, 10, 30, tzinfo=timezone.utc)


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
            "P17 canary analytical principal unexpectedly has superuser access"
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
        brief_id="rb-p17-recursive-live",
        objective=(
            "Haziran 2026 kanal performansındaki gözlenen farkı araştır; "
            "alternatif açıklamaları koru, native kanıtla test et ve nedensellik "
            "iddiası üretme."
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
                slug="p17-recursive-live",
                name="P17 Recursive Live",
                created_at=STAMP,
            )
        )
        db.add(
            User(
                id=USER_ID,
                tenant_id=TENANT_ID,
                email="p17-recursive@dima.local",
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


class GuidedTurn:
    def __init__(
        self,
        *,
        provider: StructuredResearchProposalManager,
        guidance: str,
        intent: InvestigationIntent,
        allowed_parent_step_ids: tuple[str | None, ...] | None = None,
        branch_key_mode: str | None = None,
    ) -> None:
        self._provider = provider
        self._guidance = guidance
        self._intent = intent
        self._allowed_parent_step_ids = allowed_parent_step_ids
        self._branch_key_mode = branch_key_mode

    def propose(self, snapshot):
        return self._provider.propose_with_guidance(
            snapshot,
            guidance=self._guidance,
            allowed_intents=(self._intent,),
            allowed_parent_step_ids=self._allowed_parent_step_ids,
            branch_key_mode=self._branch_key_mode,
        )


def stage(
    *,
    service: ResearchInvestigationManager,
    provider: StructuredResearchProposalManager,
    session_id: str,
    principal: Principal,
    token: str,
    name: str,
    intent: InvestigationIntent,
    guidance: str,
    allowed_parent_step_ids: tuple[str | None, ...] | None = None,
    branch_key_mode: str | None = None,
):
    before = service.snapshot(
        session_id=session_id,
        principal=principal,
    )
    step, task = service.run_one(
        session_id=session_id,
        principal=principal,
        manager=GuidedTurn(
            provider=provider,
            guidance=guidance,
            intent=intent,
            allowed_parent_step_ids=allowed_parent_step_ids,
            branch_key_mode=branch_key_mode,
        ),
        native_session_token=token,
    )
    after = service.snapshot(
        session_id=session_id,
        principal=principal,
    )
    return {
        "name": name,
        "intent": step.intent.value,
        "step_id": step.step_id,
        "parent_step_id": step.parent_step_id,
        "depth": step.depth,
        "branch_id": step.branch_id,
        "target_kind": step.target_kind.value,
        "target_ref": step.target_ref,
        "objective_key": step.objective_key,
        "bounded_objective": step.bounded_objective,
        "rationale": step.rationale,
        "status": step.status.value,
        "stop_reason": step.stop_reason.value if step.stop_reason else None,
        "stop_scope": step.stop_scope.value if step.stop_scope else None,
        "task_id": task.task_id if task else None,
        "native_execution_refs": (
            list(task.native_execution_refs) if task else []
        ),
        "material_refs": list(task.material_refs) if task else [],
        "evidence_refs": list(task.evidence_refs) if task else [],
        "open_branches_before": list(
            before.investigation.open_branch_ids
        ),
        "open_branches_after": list(
            after.investigation.open_branch_ids
        ),
        "_step": step,
        "_task": task,
    }


def public_stage(record: dict) -> dict:
    return {
        key: value
        for key, value in record.items()
        if not key.startswith("_")
    }


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
    ap.add_argument(
        "--manager-model",
        default="openai/gpt-5.6-luna",
    )
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
        raise RuntimeError("P17 live canary is Luna-only")

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
        tenant_slug="p17-recursive-live",
    )
    brief = research_brief()
    started = product.start_from_brief(
        brief=brief,
        request_ref="p17-recursive-live",
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
            f"P14 base Research did not verify: {base_response.model_dump(mode='json')}"
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
    service = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        followup_executor=followup,
        budget=ResearchReasoningBudget(
            max_reasoning_steps=8,
            max_followup_native_turns=4,
            max_counter_evidence_attempts=2,
            max_depth=5,
        ),
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
    manager = StructuredResearchProposalManager(
        transport=transport,
    )

    records = []

    root = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="root-observed-gap",
        intent=InvestigationIntent.INVESTIGATE_GAP,
        guidance=(
            "Create the depth-0 investigation for the observed June 2026 "
            "channel-order performance gap. parent_step_id must be null. "
            "Ask one concrete bounded analytical question that Metabase can "
            "answer natively using the current Research scope. Do not assert "
            "a cause and do not invent fields."
        ),
        allowed_parent_step_ids=(None,),
        branch_key_mode="null",
    )
    records.append(root)
    root_step = root["_step"]
    if root_step.depth != 0 or root_step.parent_step_id is not None:
        raise RuntimeError("root investigation topology is invalid")
    if root["_task"] is None:
        raise RuntimeError("root INVESTIGATE_GAP produced no native follow-up")

    alt_a = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="candidate-branch-a",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        guidance=(
            f"Open the first candidate explanation branch under parent_step_id "
            f"{root_step.step_id}. Use a stable non-empty branch_key. The "
            "candidate must be investigable from the current business/analytical "
            "scope, but do not claim it is causal and do not execute analytics "
            "in this topology-only step."
        ),
        allowed_parent_step_ids=(root_step.step_id,),
        branch_key_mode="string",
    )
    records.append(alt_a)
    alt_a_step = alt_a["_step"]
    if alt_a_step.parent_step_id != root_step.step_id:
        raise RuntimeError("candidate A did not attach to root")

    alt_b = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="candidate-branch-b",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        guidance=(
            f"Open a SECOND, materially different candidate explanation branch "
            f"under parent_step_id {root_step.step_id}. It must use a different "
            "stable branch_key from existing alternatives. Preserve both "
            "alternatives; do not rank a winner and do not assert causality."
        ),
        allowed_parent_step_ids=(root_step.step_id,),
        branch_key_mode="string",
    )
    records.append(alt_b)
    alt_b_step = alt_b["_step"]
    if alt_b_step.parent_step_id != root_step.step_id:
        raise RuntimeError("candidate B did not attach to root")
    if alt_a_step.branch_id == alt_b_step.branch_id:
        raise RuntimeError("candidate branches collapsed into one branch")

    tested = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="manager-selected-discriminating-native-test",
        intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
        guidance=(
            "Choose WHICH ONE of the two currently open candidate branches is "
            "more useful to test next. parent_step_id MUST be exactly one of "
            f"{alt_a_step.step_id} or {alt_b_step.step_id}; omit branch_key so "
            "the selected branch identity continues. Ask one bounded native "
            "analytical question whose result could discriminate that candidate "
            "using only available Metabase semantics. Do not compute the answer "
            "yourself and do not rank a causal winner."
        ),
        allowed_parent_step_ids=(
            alt_a_step.step_id,
            alt_b_step.step_id,
        ),
        branch_key_mode="null",
    )
    records.append(tested)
    tested_step = tested["_step"]
    by_step = {
        alt_a_step.step_id: alt_a_step,
        alt_b_step.step_id: alt_b_step,
    }
    selected_parent = by_step.get(tested_step.parent_step_id or "")
    if selected_parent is None:
        raise RuntimeError(
            "manager did not select one of the two candidate branches for testing"
        )
    if tested_step.branch_id != selected_parent.branch_id:
        raise RuntimeError("native test escaped manager-selected candidate branch")
    if tested["_task"] is None or not tested["evidence_refs"]:
        raise RuntimeError("discriminating native test produced no Evidence")

    sibling = (
        alt_b_step if selected_parent.step_id == alt_a_step.step_id else alt_a_step
    )
    stopped_sibling = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="stop-untested-sibling",
        intent=InvestigationIntent.STOP_BRANCH,
        guidance=(
            f"Stop only the unselected sibling candidate at parent_step_id "
            f"{sibling.step_id}. Use a branch-local stop reason supported by the "
            "current bounded canary state. Do not stop the whole investigation "
            "and do not invent causal truth."
        ),
        allowed_parent_step_ids=(sibling.step_id,),
        branch_key_mode="null",
    )
    records.append(stopped_sibling)
    stopped_sibling_step = stopped_sibling["_step"]
    if (
        stopped_sibling_step.stop_scope is None
        or stopped_sibling_step.stop_scope.value != "BRANCH"
    ):
        raise RuntimeError("unselected sibling was not stopped branch-locally")

    deepened = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="deepen-manager-selected-branch",
        intent=InvestigationIntent.DEEPEN_EXPLANATION,
        guidance=(
            f"After inspecting the newly produced Evidence/material, create a "
            f"child investigation question under parent_step_id "
            f"{tested_step.step_id}. Omit branch_key to stay on the selected "
            "candidate branch. The child asks what should be investigated "
            "deeper; it must not calculate an analytical or causal answer."
        ),
        allowed_parent_step_ids=(tested_step.step_id,),
        branch_key_mode="null",
    )
    records.append(deepened)
    deep_step = deepened["_step"]
    if deep_step.branch_id != selected_parent.branch_id:
        raise RuntimeError("deepened node escaped manager-selected branch")
    if deep_step.depth <= tested_step.depth:
        raise RuntimeError("DEEPEN_EXPLANATION did not increase depth")

    replanned = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="replan-after-evidence",
        intent=InvestigationIntent.REPLAN,
        guidance=(
            f"Replan from parent_step_id {deep_step.step_id} after reviewing the "
            "current Evidence, material, stopped sibling and unresolved branch. "
            "Record the next bounded investigation target only; do not execute or "
            "compute analytics in this REPLAN step."
        ),
        allowed_parent_step_ids=(deep_step.step_id,),
        branch_key_mode="null",
    )
    records.append(replanned)
    replan_step = replanned["_step"]
    if replan_step.branch_id != selected_parent.branch_id:
        raise RuntimeError(
            "REPLAN lost manager-selected branch identity"
        )

    final_stop = stage(
        service=service,
        provider=manager,
        session_id=baseline.session_id,
        principal=principal,
        token=token,
        name="explicit-investigation-stop",
        intent=InvestigationIntent.STOP_INVESTIGATION,
        guidance=(
            f"End the bounded canary investigation from parent_step_id "
            f"{replan_step.step_id}. Choose an explicit honest global stop reason "
            "(objective satisfied, inconclusive, insufficient evidence, or another "
            "typed reason supported by the snapshot). Do not force a root cause."
        ),
        allowed_parent_step_ids=(replan_step.step_id,),
        branch_key_mode="null",
    )
    records.append(final_stop)

    final_snapshot = service.snapshot(
        session_id=baseline.session_id,
        principal=principal,
    )
    final_session = product.resume_state(
        session_id=baseline.session_id,
        principal=principal,
    )
    if final_snapshot.terminal_stop_reason is None:
        raise RuntimeError("P17 investigation did not reach explicit terminal state")
    if final_session.fingerprint != baseline.fingerprint:
        raise RuntimeError("P17 mutated sealed P14 ResearchSession authority")
    if final_session.obligations != baseline.obligations:
        raise RuntimeError("P17 mutated accepted P14 obligations")

    with Session(db_engine) as db:
        links = tuple(
            db.exec(
                select(ResearchExecutionLink)
                .where(
                    ResearchExecutionLink.session_id
                    == baseline.session_id
                )
                .order_by(
                    ResearchExecutionLink.created_at,
                    ResearchExecutionLink.id,
                )
            ).all()
        )
    base_links = [x for x in links if x.execution_kind == "P14_BASE"]
    followups = [x for x in links if x.execution_kind == "P17_FOLLOWUP"]
    if len(base_links) != 1:
        raise RuntimeError(f"expected one P14 base occurrence, got {len(base_links)}")
    if len(followups) != 2:
        raise RuntimeError(f"expected two P17 follow-up occurrences, got {len(followups)}")
    if any(x.status != "VERIFIED" for x in links):
        raise RuntimeError("not all native occurrences are VERIFIED")
    if any(x.attestation_id is not None for x in links):
        raise RuntimeError("P17 unexpectedly reopened P13 attestation")
    if any(
        not x.reasoning_step_id or not x.investigation_task_id
        for x in followups
    ):
        raise RuntimeError("P17 follow-up lineage is incomplete")

    graph = final_snapshot.investigation
    gates = {
        "manager_model_is_luna": args.manager_model == "openai/gpt-5.6-luna",
        "manager_model_calls": manager.call_count == 8,
        "root_exists": root_step.depth == 0,
        "multiple_sibling_branches": (
            alt_a_step.parent_step_id == root_step.step_id
            and alt_b_step.parent_step_id == root_step.step_id
            and alt_a_step.branch_id != alt_b_step.branch_id
        ),
        "native_discriminating_test": bool(tested["evidence_refs"]),
        "manager_selected_material_branch": (
            tested_step.parent_step_id
            in {alt_a_step.step_id, alt_b_step.step_id}
        ),
        "branch_local_stop": (
            sibling.branch_id in graph.stopped_branch_ids
        ),
        "selected_branch_remains_open": (
            selected_parent.branch_id in graph.open_branch_ids
        ),
        "deeper_same_branch": (
            deep_step.depth > tested_step.depth
            and deep_step.branch_id == tested_step.branch_id
        ),
        "replan_recorded": (
            replan_step.intent == InvestigationIntent.REPLAN
        ),
        "global_stop_recorded": (
            final_snapshot.terminal_stop_reason is not None
        ),
        "p14_authority_immutable": (
            final_session.fingerprint == baseline.fingerprint
        ),
        "p17_followups_exactly_two": len(followups) == 2,
        "p17_followups_are_separate_from_base": (
            all(x.execution_kind == "P17_FOLLOWUP" for x in followups)
        ),
        "p13_hot_path_attestation_zero": all(
            x.attestation_id is None for x in links
        ),
        "base_p15_material_exists": bool(base_lead.lead_id),
        "recursive_depth_real": graph.max_observed_depth >= 3,
        "no_forced_causal_terminal": final_snapshot.terminal_stop_reason
        in set(ManagerStopReason),
    }
    report = {
        "schema_version": "p17_recursive_live_v1",
        "status": "GREEN" if all(gates.values()) else "RED",
        "platform_sha": args.platform_sha,
        "manager_model": args.manager_model,
        "manager_model_call_count": manager.call_count,
        "engine_sha": args.engine_sha,
        "runtime_tag": args.runtime_tag,
        "runtime_image_digest": args.runtime_image_digest,
        "metabase_subject": f"metabase-user:{current['id']}",
        "metabase_superuser": bool(current.get("is_superuser")),
        "research_session_id": baseline.session_id,
        "base_receipt_id": base_response.receipt_id,
        "base_evidence_id": base_response.evidence_id,
        "base_material_id": base_lead.lead_id,
        "stages": [public_stage(x) for x in records],
        "graph": graph.model_dump(mode="json"),
        "terminal_stop_reason": final_snapshot.terminal_stop_reason.value,
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
        "gates": gates,
        "engine_changes_builds": "0 / 0",
        "p13_attestation_hot_path_calls": 0,
        "second_native_executor": 0,
        "second_receipt_family": 0,
        "second_claim_authority": 0,
        "sol_calls": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
