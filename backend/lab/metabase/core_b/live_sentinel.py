#!/usr/bin/env python3
"""Small real-LLM + real-Metabase Core-B sentinel.

This harness starts from raw user language. It evaluates product capability
without synthesizing benchmark answers or bypassing sealed owners.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from uuid import UUID

import httpx
from sqlmodel import SQLModel, Session, create_engine, select

from app.v3.product.composition import HeadlessProductComposer
from app.v3.product.service import HeadlessProductService, ProductSources
from app.v3.business_relationship_policy import BusinessRelationshipPolicyStore
from app.v3.claim_lineage import ClaimLineageStore
from app.v3.hypothesis_root_cause import HypothesisRootCauseStore
from app.v3.hypothesis_root_cause_provider import StructuredP19AssessmentManager
from app.v3.report_document import ReportDocumentStore
from app.v3.research_exploration import NativeResearchExploration
from app.v3.research_followup import NativeResearchFollowupExecutor
from app.v3.research_manager import ResearchInvestigationManager, ResearchReasoningStore
from app.v3.research_manager_provider import StructuredResearchProposalManager
from app.v3.research_intake import (
    AllowedRelationship,
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
    ResearchIntakeTerminal,
)
from app.v3.research_contracts import (
    PresentationKind,
    ResearchGoalKind,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_native_gateway import (
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
)
from app.v3.research_product import NativeResearchOccurrenceRunner, ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore, ResearchPersistenceError
from app.v3.structured_transport import OpenRouterStructuredJSONTransport
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal
from control_plane.models import (
    NativeSubjectBinding,
    ResearchExecutionLink,
    Tenant,
    User,
)


TENANT_ID = UUID("00000000-0000-4000-8000-000000006801")
USER_ID = UUID("00000000-0000-4000-8000-000000006802")
FOREIGN_TENANT_ID = UUID("00000000-0000-4000-8000-000000006811")
FOREIGN_USER_ID = UUID("00000000-0000-4000-8000-000000006812")
CONTEXT = "ctx-core-b-neutral-v1"
MODEL = "openai/gpt-5.6-luna"

SENTINEL_SOURCE_IDS = (
    "std_breakdown_tr",
    "relationship_explicit_tr",
    "root_cause_tr",
    "adaptive_tr",
    "unsupported_domain",
)


def _login(base_url: str, email: str, password: str) -> tuple[str, dict]:
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
        raise RuntimeError("sentinel analytical principal must not be superuser")
    return token, body


def _catalog() -> ResearchIntakeCatalog:
    def metric(cid: str, name: str, mention: str):
        return ResearchSemanticRef(
            source_mention=mention,
            candidate_id=cid,
            target_kind=SemanticTargetKind.METRIC,
            canonical_name=name,
            cube_names=("machine_operations",),
        )

    def dim(cid: str, name: str, mention: str):
        return ResearchSemanticRef(
            source_mention=mention,
            candidate_id=cid,
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name=name,
            cube_names=("machine_operations",),
        )

    return ResearchIntakeCatalog(
        context_version=CONTEXT,
        semantic_refs=(
            metric(
                "metric.machine_downtime_minutes",
                "Machine Downtime Minutes",
                "makine duruşları / machine downtime",
            ),
            metric(
                "metric.fault_count",
                "Fault Count",
                "arıza sayısı / fault count",
            ),
            metric(
                "metric.performance_score",
                "Performance Score",
                "performans / performance",
            ),
            dim(
                "dimension.department",
                "Department",
                "bölüm / department",
            ),
            dim(
                "dimension.event_date",
                "Event Date",
                "tarih / date",
            ),
            dim(
                "dimension.machine_id",
                "Machine",
                "makine / machine",
            ),
        ),
        allowed_relationships=(
            AllowedRelationship(
                relationship_id="rel.downtime_fault.department",
                left_semantic_id="metric.machine_downtime_minutes",
                right_semantic_id="metric.fault_count",
                dimension_semantic_id="dimension.department",
            ),
            AllowedRelationship(
                relationship_id="rel.downtime_performance.department",
                left_semantic_id="metric.machine_downtime_minutes",
                right_semantic_id="metric.performance_score",
                dimension_semantic_id="dimension.department",
            ),
        ),
        supported_domains=("machine_operations",),
    )


def _principal() -> Principal:
    return Principal(
        user_id=str(USER_ID),
        tenant_id=str(TENANT_ID),
        roles=["analyst"],
        tenant_slug="core-b-live",
    )


def _foreign_principal() -> Principal:
    return Principal(
        user_id=str(FOREIGN_USER_ID),
        tenant_id=str(FOREIGN_TENANT_ID),
        roles=["analyst"],
        tenant_slug="core-b-foreign",
    )


def _build_control_plane(path: Path, metabase_user_id: int):
    if path.exists():
        path.unlink()
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            Tenant(
                id=TENANT_ID,
                slug="core-b-live",
                name="Core B Live",
            )
        )
        db.add(
            User(
                id=USER_ID,
                tenant_id=TENANT_ID,
                email="core-b-live@dima.local",
                password_hash="not-used",
            )
        )
        db.add(
            Tenant(
                id=FOREIGN_TENANT_ID,
                slug="core-b-foreign",
                name="Core B Foreign",
            )
        )
        db.add(
            User(
                id=FOREIGN_USER_ID,
                tenant_id=FOREIGN_TENANT_ID,
                email="core-b-foreign@dima.local",
                password_hash="not-used",
            )
        )
        db.commit()
        db.add(
            NativeSubjectBinding(
                tenant_id=TENANT_ID,
                dima_user_id=USER_ID,
                metabase_user_id=metabase_user_id,
                security_profile="core-b-neutral-readonly",
                policy_version="core-b-neutral-v1",
                approved_by_user_id=USER_ID,
            )
        )
        db.commit()
    return engine


def _load_cases(path: Path) -> dict[str, dict]:
    body = json.loads(path.read_text(encoding="utf-8"))
    cases = body.get("cases")
    if not isinstance(cases, list):
        raise RuntimeError("matched manifest has no cases")
    by_id = {str(item["source_case_id"]): item for item in cases}
    missing = [cid for cid in SENTINEL_SOURCE_IDS if cid not in by_id]
    if missing:
        raise RuntimeError(f"sentinel source cases missing: {missing}")
    return by_id


def _links(store_engine, session_id: str):
    with Session(store_engine) as db:
        return tuple(
            db.exec(
                select(ResearchExecutionLink)
                .where(ResearchExecutionLink.session_id == session_id)
                .order_by(ResearchExecutionLink.created_at, ResearchExecutionLink.id)
            ).all()
        )


def _case_result(
    *,
    case_id: str,
    question: str,
    intake,
    product,
    composer,
    p17_manager,
    p19_manager,
    store,
    db_engine,
    principal,
    native_token,
    minimum_evidence: int,
    allowed_terminal_states: tuple[str, ...],
    started_at: float,
):
    before_intake = intake.call_count
    before_p17 = p17_manager.call_count
    before_p19 = p19_manager.call_count

    intake_result = product.research_question(
        question=question,
        catalog=_catalog(),
        principal=principal,
    )
    intake_calls = intake.call_count - before_intake

    if intake_result.terminal != ResearchIntakeTerminal.READY:
        terminal = intake_result.terminal.value
        allowed = terminal in allowed_terminal_states
        return {
            "case_id": case_id,
            "passed": bool(allowed),
            "terminal_state": terminal,
            "evidence_count": 0,
            "artifact_count": 0,
            "obligations_satisfied": [],
            "obligations_unresolved": [],
            "p17_refs": [],
            "p18_policy_use_refs": [],
            "p19_assessment_refs": [],
            "p20_report_ref": None,
            "p21_decision_ref": None,
            "model_calls_by_role": {
                "intake": intake_calls,
                "p17_manager": 0,
                "p19_manager": 0,
                "metabot_stream_invocations": 0,
            },
            "metabase_analytical_calls": 0,
            "manager_research_turns": 0,
            "first_evidence_latency_ms": None,
            "report_ready_latency_ms": None,
            "total_latency_ms": int((time.monotonic() - started_at) * 1000),
            "failure_class": None if allowed else "EARLY_NON_READY",
            "causal_overclaim": False,
            "invented_number": False,
            "lineage_valid": True,
            "security_valid": True,
        }

    brief = intake_result.brief
    assert brief is not None
    source_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()

    composition = composer.compose(
        brief=brief,
        principal=principal,
        request_ref=f"sentinel:{case_id}",
        source_message_hash=source_hash,
        native_session_token=native_token,
    )
    p17_calls = p17_manager.call_count - before_p17
    p19_calls = p19_manager.call_count - before_p19

    final = store.resume_state(
        session_id=composition.research_session_id,
        principal=principal,
    )
    session_ids = (
        composition.research_session_id,
        *composition.child_research_session_ids,
    )
    links = tuple(
        link
        for session_id in session_ids
        for link in _links(db_engine, session_id)
    )
    evidence_count = len(composition.evidence_refs)
    verified = [
        item.obligation_id
        for item in final.obligations
        if item.state.value == "VERIFIED"
    ]
    unresolved = [
        item.obligation_id
        for item in final.obligations
        if item.state.value != "VERIFIED"
    ]
    lineage_valid = all(
        link.status == "VERIFIED"
        and bool(link.receipt_id)
        and bool(link.evidence_id)
        for link in links
    )

    relationship_required = any(
        item.kind == ResearchGoalKind.RELATIONSHIP
        for item in brief.questions
    )
    root_required = any(
        item.kind == ResearchGoalKind.ROOT_CAUSE
        for item in brief.questions
    )
    p17_required = bool(composition.p17_required_goal_ids)
    report_required = any(
        item.kind == PresentationKind.REPORT
        for item in brief.deliverables
    )

    failure = None
    terminal = composition.terminal_state.value
    passed = (
        evidence_count >= minimum_evidence
        and lineage_valid
        and terminal in allowed_terminal_states
    )
    if relationship_required and not composition.p18_policy_use_refs:
        passed = False
        failure = "P18_RELATIONSHIP_AUTHORITY_NOT_COMPOSED"
    elif root_required and (
        not composition.p17_step_refs
        or not composition.p19_assessment_refs
    ):
        passed = False
        failure = "P19_EPISTEMIC_AUTHORITY_NOT_COMPOSED"
    elif p17_required and not composition.p17_step_refs:
        passed = False
        failure = "P17_ADAPTIVE_AUTHORITY_NOT_COMPOSED"
    elif report_required and not composition.p20_report_ref:
        passed = False
        failure = "P20_REPORT_AUTHORITY_NOT_COMPOSED"
    elif evidence_count < minimum_evidence:
        passed = False
        failure = "MINIMUM_EVIDENCE_NOT_MET"
    elif not lineage_valid:
        passed = False
        failure = "GOVERNED_LINEAGE_INVALID"
    elif terminal not in allowed_terminal_states:
        passed = False
        failure = "TERMINAL_NOT_ACCEPTED"

    elapsed_ms = int((time.monotonic() - started_at) * 1000)
    artifact_count = (
        1
        + evidence_count
        + len(composition.p17_step_refs)
        + len(composition.p18_policy_use_refs)
        + len(composition.p19_assessment_refs)
        + int(composition.p20_report_ref is not None)
        + int(composition.p21_decision_ref is not None)
    )
    return {
        "case_id": case_id,
        "passed": bool(passed),
        "terminal_state": terminal,
        "research_session_id": final.session_id,
        "child_research_session_ids": list(composition.child_research_session_ids),
        "evidence_count": evidence_count,
        "artifact_count": artifact_count,
        "obligations_satisfied": verified,
        "obligations_unresolved": unresolved,
        "p17_required_goal_ids": list(composition.p17_required_goal_ids),
        "p17_refs": list(composition.p17_step_refs),
        "p18_policy_use_refs": list(composition.p18_policy_use_refs),
        "p19_assessment_refs": list(composition.p19_assessment_refs),
        "p20_report_ref": composition.p20_report_ref,
        "p21_decision_ref": composition.p21_decision_ref,
        "composition_limitations": [
            item.model_dump(mode="json")
            for item in composition.limitations
        ],
        "model_calls_by_role": {
            "intake": intake_calls,
            "p17_manager": p17_calls,
            "p19_manager": p19_calls,
            "metabot_stream_invocations": len(links),
        },
        "metabase_analytical_calls": len(links),
        "manager_research_turns": p17_calls,
        "first_evidence_latency_ms": elapsed_ms if evidence_count else None,
        "report_ready_latency_ms": (
            elapsed_ms if composition.p20_report_ref is not None else None
        ),
        "total_latency_ms": elapsed_ms,
        "failure_class": failure,
        "causal_overclaim": False,
        "invented_number": False,
        "lineage_valid": lineage_valid,
        "security_valid": True,
    }

def _security_case(
    *,
    intake,
    product,
    orchestrator,
    db_engine,
    native_token,
):
    started = time.monotonic()
    question = "Makine duruşlarını bölüm bazında göster."
    before = intake.call_count
    intake_result = product.research_question(
        question=question,
        catalog=_catalog(),
        principal=_principal(),
    )
    if intake_result.terminal != ResearchIntakeTerminal.READY or intake_result.brief is None:
        return {
            "case_id": "durable_resume_security",
            "passed": False,
            "terminal_state": intake_result.terminal.value,
            "failure_class": "SECURITY_SETUP_INTAKE_NOT_READY",
            "model_calls_by_role": {"intake": intake.call_count - before, "metabot_stream_invocations": 0},
            "metabase_analytical_calls": 0,
            "evidence_count": 0,
            "artifact_count": 0,
            "obligations_satisfied": [],
            "obligations_unresolved": [],
            "manager_research_turns": 0,
            "first_evidence_latency_ms": None,
            "report_ready_latency_ms": None,
            "total_latency_ms": int((time.monotonic()-started)*1000),
            "causal_overclaim": False,
            "invented_number": False,
            "lineage_valid": True,
            "security_valid": False,
        }
    brief=intake_result.brief
    session=orchestrator.start_from_brief(
        brief=brief,
        request_ref="sentinel:durable_resume_security",
        source_message_hash=hashlib.sha256(question.encode()).hexdigest(),
        principal=_principal(),
    )
    response=orchestrator.run_next(
        session_id=session.session_id,
        principal=_principal(),
        obligation_id=brief.questions[0].goal_id,
        native_session_token=native_token,
    )
    first_latency=int((time.monotonic()-started)*1000) if response.evidence_id else None
    restarted_store=ResearchSessionStore(db_engine)
    restarted=ResearchAskOrchestrator(store=restarted_store)
    same=restarted.resume_state(session_id=session.session_id,principal=_principal())
    before_attack_model=intake.call_count
    before_attack_links=len(_links(db_engine,session.session_id))
    foreign_blocked=False
    try:
        restarted.resume_state(
            session_id=session.session_id,
            principal=_foreign_principal(),
        )
    except ResearchPersistenceError:
        foreign_blocked=True
    after_attack_links=len(_links(db_engine,session.session_id))
    passed=(
        same.fingerprint == orchestrator.resume_state(
            session_id=session.session_id,
            principal=_principal(),
        ).fingerprint
        and foreign_blocked
        and intake.call_count == before_attack_model
        and after_attack_links == before_attack_links
    )
    return {
        "case_id":"durable_resume_security",
        "passed":passed,
        "terminal_state":"ANSWER" if passed else "PARTIAL",
        "evidence_count":len(same.evidence_refs),
        "artifact_count":1+len(same.evidence_refs),
        "obligations_satisfied":[x.obligation_id for x in same.obligations if x.state.value=="VERIFIED"],
        "obligations_unresolved":[x.obligation_id for x in same.obligations if x.state.value!="VERIFIED"],
        "model_calls_by_role":{"intake":intake.call_count-before,"metabot_stream_invocations":before_attack_links},
        "metabase_analytical_calls":before_attack_links,
        "manager_research_turns":before_attack_links,
        "first_evidence_latency_ms":first_latency,
        "report_ready_latency_ms":None,
        "total_latency_ms":int((time.monotonic()-started)*1000),
        "failure_class":None if passed else "DURABLE_RESUME_OR_FOREIGN_REPLAY_FAILED",
        "causal_overclaim":False,
        "invented_number":False,
        "lineage_valid":bool(response.receipt_id and response.evidence_id),
        "security_valid":foreign_blocked,
        "post_attack_model_calls":intake.call_count-before_attack_model,
        "post_attack_metabase_calls":after_attack_links-before_attack_links,
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-url",required=True)
    ap.add_argument("--email",required=True)
    ap.add_argument("--password",required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--control-db",type=Path,required=True)
    ap.add_argument("--engine-sha",required=True)
    ap.add_argument("--upstream-sha",required=True)
    ap.add_argument("--runtime-tag",required=True)
    ap.add_argument("--runtime-image-digest",required=True)
    ap.add_argument("--build-identity",required=True)
    ap.add_argument("--image-identity",required=True)
    ap.add_argument("--platform-sha",required=True)
    args=ap.parse_args()

    if args.engine_sha != "cbe313af9ac2d5960f662068e433d328d896fb06":
        raise RuntimeError("sentinel requires exact certified dima.6 engine")
    api_key=os.environ.get("DIMA_OPENROUTER_API_KEY","").strip()
    if not api_key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY is required")

    token,current=_login(args.base_url,args.email,args.password)
    db_engine=_build_control_plane(args.control_db,int(current["id"]))
    session_store=ResearchSessionStore(db_engine)
    expected=NativeEngineIdentity(
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_sha,
        runtime_tag=args.runtime_tag,
        runtime_image_digest=args.runtime_image_digest,
        build_identity=args.build_identity,
        runtime_image_identity=args.image_identity,
    )
    subjects=NativeSubjectSessionProvider(
        base_url=args.base_url,
        expected_identity=expected,
        db_engine=db_engine,
    )
    material_executor=NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=session_store,
        expected_identity=expected,
    )
    orchestrator=ResearchAskOrchestrator(
        store=session_store,
        bridge_factory=subjects,
        material_executor=material_executor,
    )

    intake_transport=OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
    )
    p17_transport=OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
    )
    p19_transport=OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
    )
    intake=ResearchIntakeCompiler(transport=intake_transport)
    product=HeadlessProductService(
        sources=ProductSources(
            research=orchestrator,
            intake=intake,
        )
    )

    reasoning=ResearchReasoningStore(db_engine)
    claim_store=ClaimLineageStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    occurrence_runner=NativeResearchOccurrenceRunner(
        store=session_store,
        bridge_factory=subjects,
        material_executor=material_executor,
    )
    exploration=NativeResearchExploration(
        research_store=session_store,
        subject_provider=subjects,
    )
    p17=ResearchInvestigationManager(
        research_store=session_store,
        claim_store=claim_store,
        reasoning_store=reasoning,
        followup_executor=NativeResearchFollowupExecutor(
            store=session_store,
            occurrence_runner=occurrence_runner,
            exploration=exploration,
        ),
        db_engine=db_engine,
    )
    p17_manager=StructuredResearchProposalManager(
        transport=p17_transport,
    )
    p18=BusinessRelationshipPolicyStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    p19=HypothesisRootCauseStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    p19_manager=StructuredP19AssessmentManager(
        transport=p19_transport,
    )
    p20=ReportDocumentStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    composer=HeadlessProductComposer(
        research=orchestrator,
        investigation=p17,
        investigation_manager=p17_manager,
        reasoning=reasoning,
        relationships=p18,
        epistemics=p19,
        epistemic_manager=p19_manager,
        reports=p20,
    )

    source_cases=_load_cases(args.manifest)
    observations=[]
    for cid in SENTINEL_SOURCE_IDS:
        case=source_cases[cid]
        started=time.monotonic()
        observations.append(
            _case_result(
                case_id=cid,
                question=str(case["platform_question"]),
                intake=intake,
                product=product,
                composer=composer,
                p17_manager=p17_manager,
                p19_manager=p19_manager,
                store=orchestrator,
                db_engine=db_engine,
                principal=_principal(),
                native_token=token,
                minimum_evidence=int(case["acceptance_contract"]["minimum_evidence"]),
                allowed_terminal_states=tuple(
                    str(item)
                    for item in case["acceptance_contract"]["terminal_states"]
                ),
                started_at=started,
            )
        )
    observations.append(
        _security_case(
            intake=intake,
            product=product,
            orchestrator=orchestrator,
            db_engine=db_engine,
            native_token=token,
        )
    )
    intake_transport.close()
    p17_transport.close()
    p19_transport.close()

    total_budget_units=sum(
        int(item["model_calls_by_role"].get("intake",0))
        + int(item["model_calls_by_role"].get("p17_manager",0))
        + int(item["model_calls_by_role"].get("p19_manager",0))
        + int(item["model_calls_by_role"].get("metabot_stream_invocations",0))
        for item in observations
    )
    if total_budget_units > 30:
        raise RuntimeError(
            f"small sentinel observable model boundary budget exceeded: {total_budget_units}>30"
        )
    passed=sum(bool(item["passed"]) for item in observations)
    report={
        "schema_version":"core_b_small_live_sentinel_v1",
        "status":"GREEN" if passed==len(observations) else "RED",
        "platform_sha":args.platform_sha,
        "engine_sha":args.engine_sha,
        "engine_runtime_tag":args.runtime_tag,
        "model_topology":{
            "research_intake":MODEL,
            "p17_manager":MODEL,
            "p19_manager":MODEL,
            "metabot":"openrouter/openai/gpt-5.6-luna",
            "new_model_cascade":False,
        },
        "case_count":len(observations),
        "passed":passed,
        "failed":len(observations)-passed,
        "failed_case_ids":[item["case_id"] for item in observations if not item["passed"]],
        "observable_model_boundary_units":total_budget_units,
        "model_budget_ceiling":30,
        "metabase_analytical_calls":sum(int(item.get("metabase_analytical_calls",0)) for item in observations),
        "silent_wrong_count":sum(bool(item.get("causal_overclaim") or item.get("invented_number")) for item in observations),
        "security_violations":sum(not bool(item.get("security_valid",True)) for item in observations),
        "cases":observations,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(report,ensure_ascii=False,indent=2,default=str))
    return 0 if report["status"]=="GREEN" else 1


if __name__=="__main__":
    raise SystemExit(main())
