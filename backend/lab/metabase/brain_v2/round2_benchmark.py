#!/usr/bin/env python3
"""Frozen Round-2 30-case benchmark for Dima Brain V2.1 / LangGraph.

This harness intentionally preserves the exact 2026-09-27 Round-2 prompt corpus
and neutral fixture while executing only the accepted BrainV2Service runtime.
It records raw governed outputs, provenance, provider telemetry, latency, and
mechanical safety signals. Final Product Quality scoring is manual and happens
from the artifact; harness PASS is never the final score.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from app.v3.brain_v2.checkpoint import postgres_checkpoint_saver
from app.v3.brain_v2.adaptive_owner_adapter import AdaptiveDimaBrainV2Activities
from app.v3.brain_v2.service import BrainV2Service
from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus
from app.v3.business_relationship_policy import BusinessRelationshipPolicyStore
from app.v3.claim_lineage import ClaimLineageStore
from app.v3.hypothesis_root_cause import HypothesisRootCauseStore
from app.v3.hypothesis_root_cause_provider import StructuredP19AssessmentManager
from app.v3.p18_relationship_interpreter import StructuredP18RelationshipInterpreter
from app.v3.report_document import ReportDocumentStore
from app.v3.research_exploration import NativeResearchExploration
from app.v3.research_followup import NativeResearchFollowupExecutor
from app.v3.research_intake import ResearchIntakeCompiler
from app.v3.research_manager import ResearchInvestigationManager, ResearchReasoningStore
from app.v3.research_manager_provider import StructuredResearchProposalManager
from app.v3.research_product import NativeResearchOccurrenceRunner, ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from app.v3.structured_transport import OpenRouterStructuredJSONTransport

from lab.metabase.brain_v2.live_support import (
    BoundedMaterialExecutor,
    BoundedStructuredTransport,
    METABOT_MODEL,
    MODEL,
    NativeEngineIdentity,
    NativeRequestAudit,
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
    ORCHESTRATION_EFFICIENCY_SLO_UNITS,
    OrchestrationEfficiencyTracker,
    build_catalog,
    build_control_plane,
    execution_links,
    load_binding_manifest,
    login,
    principal,
    seed_native_resource_bindings,
)

USER_ID = "round2-brain-v21"
TENANT_ID = "round2-brain-v21"


def _safe(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _read_provider(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "actual_provider_request_count": 0,
            "blocked_request_count": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "provider_reported_cost": 0.0,
            "provider_requests_by_source": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "actual_provider_request_count",
        "blocked_request_count",
        "prompt_tokens",
        "completion_tokens",
        "reasoning_tokens",
        "provider_reported_cost",
    )
    out: dict[str, Any] = {}
    for key in keys:
        av = after.get(key, 0) or 0
        bv = before.get(key, 0) or 0
        out[key] = av - bv
    a_sources = after.get("provider_requests_by_source") or {}
    b_sources = before.get("provider_requests_by_source") or {}
    names = sorted(set(a_sources) | set(b_sources))
    out["provider_requests_by_source"] = {
        name: int(a_sources.get(name, 0) or 0) - int(b_sources.get(name, 0) or 0)
        for name in names
        if int(a_sources.get(name, 0) or 0) - int(b_sources.get(name, 0) or 0)
    }
    return out


def _native_result(link: Any) -> Any:
    raw = getattr(link, "native_result_json", None)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return {"_invalid_native_result_json": True}


def _derived_terminal(state: BrainGraphState, *, report_present: bool) -> str:
    if report_present:
        return "REPORT"
    if state.workflow_status == BrainWorkflowStatus.COMPLETE:
        return "ANSWER"
    if state.evidence_ids:
        return "PARTIAL"
    if state.workflow_status in {BrainWorkflowStatus.BLOCKED, BrainWorkflowStatus.INCONCLUSIVE}:
        return "UNSUPPORTED"
    return str(state.workflow_status.value)


def _case_runtime(
    *,
    case_id: str,
    catalog: Any,
    token: str,
    db_engine: Any,
    store: ResearchSessionStore,
    subjects: NativeSubjectSessionProvider,
    expected: NativeEngineIdentity,
    proxy: str,
    checkpointer: Any,
    model_budget: int,
):
    tracker = OrchestrationEfficiencyTracker(ORCHESTRATION_EFFICIENCY_SLO_UNITS)
    raw_material = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected,
    )
    material = BoundedMaterialExecutor(raw_material, tracker=tracker)
    research = ResearchAskOrchestrator(
        store=store,
        bridge_factory=subjects,
        material_executor=material,
    )

    raw_intake = OpenRouterStructuredJSONTransport(
        api_key=os.environ["DIMA_OPENROUTER_API_KEY"],
        model=MODEL,
        base_url=proxy + "/source/research_intake/v1",
        owner="research_intake",
    )
    raw_p17 = OpenRouterStructuredJSONTransport(
        api_key=os.environ["DIMA_OPENROUTER_API_KEY"],
        model=MODEL,
        base_url=proxy + "/source/p17_manager/v1",
        owner="p17_manager",
    )
    raw_p18 = OpenRouterStructuredJSONTransport(
        api_key=os.environ["DIMA_OPENROUTER_API_KEY"],
        model=MODEL,
        base_url=proxy + "/source/p18_manager/v1",
        owner="p18_manager",
    )
    raw_p19 = OpenRouterStructuredJSONTransport(
        api_key=os.environ["DIMA_OPENROUTER_API_KEY"],
        model=MODEL,
        base_url=proxy + "/source/p19_manager/v1",
        owner="p19_manager",
    )
    intake_transport = BoundedStructuredTransport(raw_intake, tracker=tracker, owner="research_intake")
    p17_transport = BoundedStructuredTransport(raw_p17, tracker=tracker, owner="p17_manager")
    p18_transport = BoundedStructuredTransport(raw_p18, tracker=tracker, owner="p18_manager")
    p19_transport = BoundedStructuredTransport(raw_p19, tracker=tracker, owner="p19_manager")

    intake = ResearchIntakeCompiler(transport=intake_transport)
    claims = ClaimLineageStore(research_store=store, db_engine=db_engine)
    reasoning = ResearchReasoningStore(db_engine)
    occurrence = NativeResearchOccurrenceRunner(
        store=store,
        bridge_factory=subjects,
        material_executor=material,
    )
    exploration = NativeResearchExploration(
        research_store=store,
        subject_provider=subjects,
    )
    investigation = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        reasoning_store=reasoning,
        followup_executor=NativeResearchFollowupExecutor(
            store=store,
            occurrence_runner=occurrence,
            exploration=exploration,
        ),
        db_engine=db_engine,
    )
    p17_manager = StructuredResearchProposalManager(transport=p17_transport)
    p18_manager = StructuredP18RelationshipInterpreter(transport=p18_transport)
    epistemics = HypothesisRootCauseStore(research_store=store, db_engine=db_engine)
    p19_manager = StructuredP19AssessmentManager(transport=p19_transport)
    reports = ReportDocumentStore(research_store=store, db_engine=db_engine)
    relationships = BusinessRelationshipPolicyStore(research_store=store, db_engine=db_engine)

    current_principal = principal()
    activities = AdaptiveDimaBrainV2Activities(
        principal=current_principal,
        catalog=catalog,
        intake=intake,
        research=research,
        investigation=investigation,
        investigation_manager=p17_manager,
        epistemics=epistemics,
        epistemic_manager=p19_manager,
        reports=reports,
        relationships=relationships,
        relationship_interpreter=p18_manager,
        native_session_token=token,
        engine_identity=f"{expected.engine_sha}@{expected.runtime_image_digest}",
        model_profile=MODEL,
        request_ref_prefix=f"round2-brain-v21:{case_id}",
    )
    service = BrainV2Service(activities=activities, checkpointer=checkpointer)
    return {
        "service": service,
        "activities": activities,
        "research": research,
        "investigation": investigation,
        "epistemics": epistemics,
        "reports": reports,
        "relationships": relationships,
        "tracker": tracker,
        "transports": (raw_intake, raw_p17, raw_p18, raw_p19),
        "principal": current_principal,
    }


def _collect_turn(
    *,
    turn_no: int,
    question: str,
    state: BrainGraphState,
    runtime: dict[str, Any],
    db_engine: Any,
) -> dict[str, Any]:
    research = runtime["research"]
    current_principal = runtime["principal"]
    session = None
    brief = None
    links = ()
    report_doc = None
    p18_uses = ()
    p19_assessment = None
    p19_snapshot = None
    p17_snapshot = None
    if state.research_session_id:
        session = research.resume_state(
            session_id=state.research_session_id,
            principal=current_principal,
        )
        brief = session.accepted_brief
        links = tuple(execution_links(db_engine, session.session_id))
        p17_snapshot = runtime["investigation"].snapshot(
            session_id=session.session_id,
            principal=current_principal,
        )
        if state.latest_p19_assessment_ref:
            p19_assessment = runtime["epistemics"].load_assessment(
                assessment_id=state.latest_p19_assessment_ref,
                principal=current_principal,
            )
        if brief is not None:
            root_goals = tuple(
                goal for goal in brief.questions
                if str(getattr(goal.kind, "value", goal.kind)) == "root_cause"
            )
            if len(root_goals) == 1:
                p19_snapshot = runtime["epistemics"].snapshot(
                    research_session_id=session.session_id,
                    obligation_id=root_goals[0].goal_id,
                    principal=current_principal,
                )
        p18_uses = tuple(
            runtime["relationships"].load_use(
                session_id=session.session_id,
                policy_use_id=ref,
                principal=current_principal,
            )
            for ref in state.p18_policy_use_refs
        )
        if state.report_ref:
            report_doc = runtime["reports"].load(
                report_id=state.report_ref,
                principal=current_principal,
            )

    verified_links = tuple(x for x in links if getattr(x, "status", None) == "VERIFIED")
    fingerprints = tuple(
        str(getattr(x, "native_query_fingerprint", "") or "")
        for x in verified_links
        if getattr(x, "native_query_fingerprint", None)
    )
    current_evidence = {
        item.evidence_id for item in getattr(session, "evidence_refs", ())
    } if session is not None else set()
    stale = len(set(state.evidence_ids) - current_evidence)
    terminal_requirements = set(state.terminal_requirement_ids)
    requirement_complete = bool(state.open_requirement_ids) and set(state.open_requirement_ids).issubset(terminal_requirements)
    return {
        "turn": turn_no,
        "question": question,
        "workflow_status": state.workflow_status.value,
        "last_completed_node": state.last_completed_node,
        "derived_terminal": _derived_terminal(state, report_present=report_doc is not None),
        "scope_version_id": state.scope_version_id,
        "research_session_id": state.research_session_id,
        "open_requirement_ids": list(state.open_requirement_ids),
        "terminal_requirement_ids": list(state.terminal_requirement_ids),
        "requirement_complete": requirement_complete,
        "evidence_ids": list(state.evidence_ids),
        "candidate_semantic_ids": list(state.candidate_semantic_ids),
        "p18_result_refs": list(state.p18_result_refs),
        "p19_assessment_ref": state.latest_p19_assessment_ref,
        "report_ref": state.report_ref,
        "accepted_brief": _safe(brief),
        "research": {
            "session_id": getattr(session, "session_id", None),
            "lineage_id": getattr(session, "lineage_id", None),
            "obligations": [_safe(x) for x in getattr(session, "obligations", ())],
            "evidence_refs": [_safe(x) for x in getattr(session, "evidence_refs", ())],
        } if session is not None else None,
        "native_occurrences": [
            {
                "execution_link_id": str(x.id),
                "obligation_id": x.obligation_id,
                "status": x.status,
                "native_query_id": x.native_query_id,
                "query_fingerprint": x.native_query_fingerprint,
                "receipt_id": x.receipt_id,
                "evidence_id": x.evidence_id,
                "execution_kind": x.execution_kind,
                "native_result": _native_result(x),
            }
            for x in links
        ],
        "p17": {
            "claims": [_safe(x) for x in getattr(p17_snapshot, "claims", ())],
            "investigation": _safe(getattr(p17_snapshot, "investigation", None)),
            "evidence_results": [_safe(x) for x in getattr(p17_snapshot, "evidence_results", ())],
        } if p17_snapshot is not None else None,
        "p18": [_safe(x) for x in p18_uses],
        "p19": {
            "assessment": _safe(p19_assessment),
            "snapshot": _safe(p19_snapshot),
        } if (p19_assessment is not None or p19_snapshot is not None) else None,
        "p20": _safe(report_doc),
        "native_acquisitions": len(verified_links),
        "duplicate_native": len(fingerprints) - len(set(fingerprints)),
        "stale_evidence_count": stale,
    }


def _run_case(
    *,
    case: dict[str, Any],
    catalog: Any,
    token: str,
    db_engine: Any,
    store: ResearchSessionStore,
    subjects: NativeSubjectSessionProvider,
    expected: NativeEngineIdentity,
    proxy: str,
    provider_receipt: Path,
    checkpointer: Any,
) -> dict[str, Any]:
    started = time.monotonic()
    before_provider = _read_provider(provider_receipt)
    runtime = _case_runtime(
        case_id=case["id"],
        catalog=catalog,
        token=token,
        db_engine=db_engine,
        store=store,
        subjects=subjects,
        expected=expected,
        proxy=proxy,
        checkpointer=checkpointer,
        model_budget=int(case.get("max_model_calls", 14)),
    )
    service: BrainV2Service = runtime["service"]
    current_principal = runtime["principal"]
    turns = list(case.get("turns") or [case["question"]])
    turn_records: list[dict[str, Any]] = []
    exception = None
    state = None
    try:
        for index, question in enumerate(turns, start=1):
            if index == 1:
                initial = BrainGraphState(
                    thread_id=f"round2:{case['id']}",
                    tenant_binding=ResearchAskOrchestrator.tenant_binding_for(current_principal),
                    principal_ref=str(current_principal.user_id),
                    current_user_input=question,
                )
                state = service.run(initial)
            else:
                assert state is not None
                state = service.continue_turn(
                    thread_id=state.thread_id,
                    tenant_binding=state.tenant_binding,
                    principal_ref=state.principal_ref,
                    user_input=question,
                )

            # Product-legal durable lifecycle: a retryable material WAIT is not a
            # new user turn. Give the same checkpointed thread two bounded
            # read-only resume opportunities, matching the certified live
            # sentinel contract. No Metabot/native replay is authorized here.
            for _resume_attempt in range(2):
                if (
                    state.workflow_status != BrainWorkflowStatus.WAITING
                    or state.last_completed_node
                    not in {"MATERIAL_GROUP_WAITING", "MATERIAL_WAITING"}
                ):
                    break
                time.sleep(1.0)
                service = BrainV2Service(
                    activities=runtime["activities"],
                    checkpointer=checkpointer,
                )
                state = service.resume_waiting(
                    thread_id=state.thread_id,
                    tenant_binding=state.tenant_binding,
                    principal_ref=state.principal_ref,
                )

            turn_records.append(
                _collect_turn(
                    turn_no=index,
                    question=question,
                    state=state,
                    runtime=runtime,
                    db_engine=db_engine,
                )
            )
    except Exception as exc:
        exception = {
            "type": type(exc).__name__,
            "code": getattr(getattr(exc, "code", None), "value", getattr(exc, "code", None)),
            "detail": str(exc),
            "last_valid_boundary": getattr(exc, "last_valid_boundary", None),
            "first_invalid_boundary": getattr(exc, "first_invalid_boundary", None),
        }
    finally:
        for transport in runtime["transports"]:
            transport.close()

    after_provider = _read_provider(provider_receipt)
    provider = _provider_delta(before_provider, after_provider)
    final = turn_records[-1] if turn_records else None
    all_turns = len(turn_records) == len(turns)
    accepted_status = bool(
        final is not None
        and final["derived_terminal"] in set(case.get("statuses") or ())
    )
    min_evidence = int(case.get("min_evidence", 0))
    evidence_count = len(final["evidence_ids"]) if final else 0
    mechanical_safety = bool(
        exception is None
        and all_turns
        and all((x["duplicate_native"] == 0 and x["stale_evidence_count"] == 0) for x in turn_records)
        and int(provider.get("blocked_request_count") or 0) == 0
    )
    raw_harness_pass = bool(
        mechanical_safety
        and accepted_status
        and evidence_count >= min_evidence
    )
    return {
        "id": case["id"],
        "feature_id": case["feature_id"],
        "feature_name": case["feature_name"],
        "difficulty": case["difficulty"],
        "kind": case["kind"],
        "question": case["question"],
        "expected": case.get("expected", {}),
        "legacy_case_model_call_ceiling": case.get("max_model_calls"),
        "turn_count_expected": len(turns),
        "turn_count_executed": len(turn_records),
        "turns": turn_records,
        "terminal_state": final["derived_terminal"] if final else "EXCEPTION",
        "workflow_status": final["workflow_status"] if final else None,
        "evidence_count": evidence_count,
        "native_acquisitions": sum(int(x["native_acquisitions"]) for x in turn_records),
        "duplicate_native": sum(int(x["duplicate_native"]) for x in turn_records),
        "stale_evidence_count": sum(int(x["stale_evidence_count"]) for x in turn_records),
        "requirement_complete": bool(final and final["requirement_complete"]),
        "provider": provider,
        "orchestration_efficiency": runtime["tracker"].receipt(),
        "latency_ms": int((time.monotonic() - started) * 1000),
        "all_turns_executed": all_turns,
        "accepted_terminal": accepted_status,
        "mechanical_safety": mechanical_safety,
        "raw_harness_pass": raw_harness_pass,
        "exception": exception,
        "manual_quality_score": None,
        "manual_quality_status": "PENDING",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--binding-manifest", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--control-db", type=Path, required=True)
    ap.add_argument("--checkpoint-dsn", required=True)
    ap.add_argument("--provider-proxy-base-url", required=True)
    ap.add_argument("--provider-receipt", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--runtime-image-digest", required=True)
    ap.add_argument("--build-identity", required=True)
    ap.add_argument("--image-identity", required=True)
    ap.add_argument("--candidate-product-sha", required=True)
    ap.add_argument("--checkout-sha", required=True)
    args = ap.parse_args()

    if not os.environ.get("DIMA_OPENROUTER_API_KEY", "").strip():
        raise RuntimeError("DIMA_OPENROUTER_API_KEY required")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    cases = list(manifest["cases"])
    if len(cases) != 30:
        raise RuntimeError("Round-2 requires exactly 30 frozen cases")

    binding_manifest = load_binding_manifest(args.binding_manifest)
    catalog = build_catalog(binding_manifest)
    token, current = login(args.base_url, args.email, args.password)
    db_engine = build_control_plane(args.control_db, int(current["id"]))
    seed_native_resource_bindings(db_engine, binding_manifest)
    store = ResearchSessionStore(db_engine)
    expected = NativeEngineIdentity(
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_sha,
        runtime_tag=args.runtime_tag,
        runtime_image_digest=args.runtime_image_digest,
        build_identity=args.build_identity,
        runtime_image_identity=args.image_identity,
    )
    request_audit = NativeRequestAudit()
    subjects = NativeSubjectSessionProvider(
        base_url=args.base_url,
        expected_identity=expected,
        db_engine=db_engine,
        request_observer=request_audit.observe,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    observations: list[dict[str, Any]] = []
    started = time.monotonic()
    with postgres_checkpoint_saver(args.checkpoint_dsn, setup=True) as checkpointer:
        for case in cases:
            result = _run_case(
                case=case,
                catalog=catalog,
                token=token,
                db_engine=db_engine,
                store=store,
                subjects=subjects,
                expected=expected,
                proxy=args.provider_proxy_base_url.rstrip("/"),
                provider_receipt=args.provider_receipt,
                checkpointer=checkpointer,
            )
            observations.append(result)
            checkpoint = {
                "schema_version": "dima_brain_v2_1_round2_checkpoint_v1",
                "candidate_product_sha": args.candidate_product_sha,
                "checkout_sha": args.checkout_sha,
                "completed_case_count": len(observations),
                "cases": observations,
            }
            args.output.write_text(
                json.dumps(checkpoint, ensure_ascii=False, indent=2, default=str) + "\n",
                encoding="utf-8",
            )
            print(json.dumps({
                "case": result["id"],
                "raw_harness_pass": result["raw_harness_pass"],
                "provider_requests": result["provider"]["actual_provider_request_count"],
                "prompt_tokens": result["provider"]["prompt_tokens"],
                "latency_ms": result["latency_ms"],
                "exception": (result.get("exception") or {}).get("code"),
            }, ensure_ascii=False, sort_keys=True), flush=True)

    provider_total = _read_provider(args.provider_receipt)
    latencies = [int(x["latency_ms"]) for x in observations]
    ordered = sorted(latencies)
    report = {
        "schema_version": "dima_brain_v2_1_round2_benchmark_v1",
        "system": "DIMA_BRAIN_V2_1_LANGGRAPH",
        "candidate_product_sha": args.candidate_product_sha,
        "checkout_sha": args.checkout_sha,
        "engine_sha": args.engine_sha,
        "engine_release": args.runtime_tag,
        "engine_image_digest": args.runtime_image_digest,
        "model_topology": {
            "dima_cognition": MODEL,
            "metabot": METABOT_MODEL,
            "cascade": "NONE",
        },
        "manifest_version": manifest["version"],
        "fixture": manifest["fixture"],
        "case_count": len(observations),
        "raw_harness_passed": sum(bool(x["raw_harness_pass"]) for x in observations),
        "raw_harness_failed": sum(not bool(x["raw_harness_pass"]) for x in observations),
        "case_exceptions": sum(x["exception"] is not None for x in observations),
        "duplicate_native": sum(int(x["duplicate_native"]) for x in observations),
        "stale_evidence": sum(int(x["stale_evidence_count"]) for x in observations),
        "agent_api_request_count": request_audit.agent_api_request_count,
        "total_latency_ms": int((time.monotonic() - started) * 1000),
        "latency": {
            "sum_case_ms": sum(latencies),
            "mean_case_ms": round(sum(latencies) / len(latencies), 2),
            "median_case_ms": ordered[len(ordered)//2],
            "p90_case_ms": ordered[min(len(ordered)-1, int(len(ordered)*0.9))],
            "max_case_ms": max(latencies),
        },
        "provider_total": provider_total,
        "manual_scoring": {
            "rubric": "0 FAIL / 1 LOW_UTILITY / 2 PARTIAL / 3 STRONG_PARTIAL / 4 FULL",
            "principle": "Judge correctness, scope fidelity, task fulfillment, governed evidence/provenance, causal restraint, and user utility. Do not penalize absence of a specific internal loop when the user obligation is safely satisfied. Efficiency is reported separately.",
            "status": "PENDING",
        },
        "cases": observations,
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "case_count": report["case_count"],
        "raw_harness_passed": report["raw_harness_passed"],
        "exceptions": report["case_exceptions"],
        "provider_requests": provider_total.get("actual_provider_request_count"),
        "prompt_tokens": provider_total.get("prompt_tokens"),
        "provider_cost": provider_total.get("provider_reported_cost"),
        "total_latency_ms": report["total_latency_ms"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
