#!/usr/bin/env python3
"""Surgical paid/live certification harness for Dima Brain V2 Phase 1.

Exactly one RCA mode is executed per invocation. This harness owns no Product
semantics and reuses the exact certified engine runtime lock, current Dima domain owners,
and the privacy-safe OpenRouter counting proxy.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from app.v3.brain_v2.checkpoint import postgres_checkpoint_saver
from app.v3.brain_v2.adaptive_owner_adapter import (
    AdaptiveDimaBrainV2Activities as DimaBrainV2Activities,
)
from app.v3.brain_v2.service import BrainV2Service
from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus
from app.v3.brain_v2.telemetry import (
    BoundaryName,
    BoundaryTrace,
    BoundaryTraceEvent,
)
from app.v3.hypothesis_root_cause_provider import StructuredP19AssessmentManager
from app.v3.business_relationship_policy import BusinessRelationshipPolicyStore
from app.v3.p18_relationship_interpreter import StructuredP18RelationshipInterpreter
from app.v3.report_document import ReportDocumentStore
from app.v3.research_exploration import NativeResearchExploration
from app.v3.research_followup import NativeResearchFollowupExecutor
from app.v3.research_intake import ResearchIntakeCompiler
from app.v3.research_analytical_scope import analytical_scope_contract
from app.v3.brain_v2.material_groups import project_material_groups
from app.v3.research_manager import ResearchInvestigationManager, ResearchReasoningStore
from app.v3.research_manager_provider import StructuredResearchProposalManager
from app.v3.research_product import NativeResearchOccurrenceRunner, ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from app.v3.structured_transport import OpenRouterStructuredJSONTransport
from app.v3.hypothesis_root_cause import HypothesisRootCauseStore
from app.v3.claim_lineage import ClaimLineageStore


ENGINE_RUNTIME_LOCK = (
    Path(__file__).resolve().parents[1]
    / "core_b"
    / "runtime"
    / "engine_runtime_lock.json"
)


def _require_locked_engine_runtime(args: Any) -> None:
    lock = json.loads(ENGINE_RUNTIME_LOCK.read_text(encoding="utf-8"))
    expected = {
        "engine_sha": str(lock["engine_sha"]),
        "upstream_sha": str(lock["upstream_sha"]),
        "runtime_tag": str(lock["runtime_tag"]),
        "runtime_image_digest": str(lock["registry_digest"]),
        "build_identity": str(lock["build_identity"]),
        "image_identity": str(lock["registry_digest"]),
    }
    actual = {
        "engine_sha": str(args.engine_sha),
        "upstream_sha": str(args.upstream_sha),
        "runtime_tag": str(args.runtime_tag),
        "runtime_image_digest": str(args.runtime_image_digest),
        "build_identity": str(args.build_identity),
        "image_identity": str(args.image_identity),
    }
    if actual != expected:
        raise RuntimeError(
            "Brain V2 live engine arguments do not match certified runtime lock"
        )


from lab.metabase.brain_v2.final_probes import PROBES
from lab.metabase.brain_v2.final_mechanical import (
    MULTI_INTENT,
    RELATIONSHIP_REPORT,
    phase2_mechanical,
)
from lab.metabase.brain_v2.live_support import (
    BoundedMaterialExecutor,
    BoundedStructuredTransport,
    MAX_ORCHESTRATION_BOUNDARY_UNITS,
    MODEL,
    METABOT_MODEL,
    NativeEngineIdentity,
    NativeRequestAudit,
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
    OrchestrationBudget,
    build_catalog,
    build_control_plane,
    execution_links,
    load_binding_manifest,
    login,
    principal,
    seed_native_resource_bindings,
)

SCOPE_RESUME_PROBE = "R_LIVE_4_SCOPE_RESUME"
SCOPE_RESUME_TURNS = (
    (
        "Mayıs-Haziran 2026 dönemi genelinde tüm bölümlerde machine downtime "
        "seviyesini maintenance delay ile spare-part delay adayları arasında araştır."
    ),
    "Aynı araştırmayı yalnız Assembly bölümüyle sınırla.",
)
DISCOVERY_MANUAL_CONTRACT = (
    "user supplies no candidate mechanism identities",
    "CandidateSetProjector emits only governed candidate identities from VERIFIED material",
    "normal discovery makes zero P17 provider calls",
    "no fabricated semantic identity or free-text mechanism authority",
    "projected candidates are Evidence-grounded as CONTEXT before one P19 assessment",
    "candidate set is decision-useful or insufficiency is stated honestly",
    "no redundant native acquisition or causal overclaim",
)

SCOPE_RESUME_MANUAL_CONTRACT = (
    "scope_v1 advances to scope_v2 on the same logical lineage",
    "prior Research/Evidence is historical and not reused as current",
    "the narrowed turn produces new current governed Evidence",
    "checkpoint continuation preserves thread identity",
    "completed provider/native work is not duplicated",
    "new reasoning uses only the current narrowed scope",
)

LIVE_PROBES = (
    "R_LIVE_1_ONE_PASS",
    "R_LIVE_2_ADAPTIVE",
    "R_LIVE_3_DISCOVERY",
    SCOPE_RESUME_PROBE,
    RELATIONSHIP_REPORT,
    MULTI_INTENT,
)


def _safe(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _exception(exc: Exception) -> dict[str, Any]:
    cause = getattr(exc, "__cause__", None)
    return {
        "error_type": type(exc).__name__,
        "error_code": getattr(getattr(exc, "code", None), "value", getattr(exc, "code", None)),
        "detail": str(exc),
        "cause_type": type(cause).__name__ if cause is not None else None,
        "cause_code": getattr(cause, "code", None) if cause is not None else None,
        "last_valid_boundary": getattr(exc, "last_valid_boundary", None),
        "first_invalid_boundary": getattr(exc, "first_invalid_boundary", None),
        "expected_fingerprint": getattr(exc, "expected_fingerprint", None),
        "observed_fingerprint": getattr(exc, "observed_fingerprint", None),
        "scope_fingerprint": getattr(exc, "scope_fingerprint", None),
        "material_fingerprint": getattr(exc, "material_fingerprint", None),
        "expected_semantic_shape": getattr(
            exc, "expected_semantic_shape", None
        ),
        "observed_semantic_shape": getattr(
            exc, "observed_semantic_shape", None
        ),
        "requirement_id": getattr(exc, "requirement_id", None),
        "material_group_id": getattr(exc, "material_group_id", None),
        "expected_owner": getattr(exc, "expected_owner", None),
        "observed_owner": getattr(exc, "observed_owner", None),
    }


def _provider_receipt(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != "dima_openrouter_counting_proxy_v1":
        raise RuntimeError("unexpected provider receipt schema")
    return value


def _links(db_engine, session_id: str):
    return tuple(execution_links(db_engine, session_id))


def _native_occurrence_projection(links) -> list[dict[str, Any]]:
    """Sanitized exact native occurrence receipt over canonical persisted fields."""

    return [
        {
            "execution_link_id": str(item.id),
            "obligation_id": item.obligation_id,
            "status": item.status,
            "native_query_id": item.native_query_id,
            "query_fingerprint": item.native_query_fingerprint,
            "receipt_id": item.receipt_id,
            "evidence_id": item.evidence_id,
            "execution_kind": item.execution_kind,
        }
        for item in links
    ]


def _mechanical(
    *,
    probe_id: str,
    state: BrainGraphState,
    provider: dict[str, Any],
    links,
    p17_snapshot,
    p19_snapshot,
    report_doc,
    scope_resume: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sources = provider.get("provider_requests_by_source") or {}
    verified_links = tuple(
        item for item in links
        if getattr(item, "status", None) == "VERIFIED"
    )
    query_fingerprints = tuple(
        str(getattr(item, "native_query_fingerprint", "") or "")
        for item in verified_links
        if getattr(item, "native_query_fingerprint", None)
    )
    duplicate_native = len(query_fingerprints) - len(set(query_fingerprints))
    p17_test_steps = tuple(
        node for node in p17_snapshot.investigation.nodes
        if str(getattr(node.intent, "value", node.intent))
        == "TEST_DISCRIMINATING_EVIDENCE"
    )
    p17_claims = tuple(p17_snapshot.claims)
    hypotheses = tuple(p19_snapshot.hypotheses)
    evidence_grounded = tuple(
        item for item in hypotheses
        if any(
            str(getattr(link.source_kind, "value", link.source_kind))
            in {"P14_EVIDENCE", "P17_REASONING_STEP"}
            for link in item.groundings
        )
    )
    candidate_ids = tuple(state.candidate_semantic_ids)
    presentation_required = bool(state.report_requirement_ids)
    report_exists = report_doc is not None
    report_contract_coherent = report_exists == presentation_required
    p17_provider_requests = int(sources.get("p17_manager") or 0)
    p19_provider_requests = int(sources.get("p19_manager") or 0)
    candidate_projection_coherent = (
        len(candidate_ids) == len(set(candidate_ids))
        and len(candidate_ids) == len(hypotheses)
        and len(evidence_grounded) == len(hypotheses)
    )
    discovery_candidate_path = (
        state.workflow_status == BrainWorkflowStatus.COMPLETE
        and bool(candidate_ids)
        and candidate_projection_coherent
        and p17_provider_requests == 0
        and p19_provider_requests == 1
        and state.latest_p19_assessment_ref is not None
        and report_contract_coherent
    )
    zero_candidate_stop = (
        not candidate_ids
        and not hypotheses
        and not evidence_grounded
        and p19_provider_requests == 0
        and state.latest_p19_assessment_ref is None
    )
    assessed_candidate_stop = (
        bool(candidate_ids)
        and candidate_projection_coherent
        and p19_provider_requests == 1
        and state.latest_p19_assessment_ref is not None
    )
    discovery_honest_stop = (
        state.workflow_status == BrainWorkflowStatus.INCONCLUSIVE
        and state.last_completed_node == "HONEST_STOP"
        and not state.discovery_required
        and p17_provider_requests == 0
        and report_doc is None
        and (zero_candidate_stop or assessed_candidate_stop)
    )
    common = {
        "terminal_complete": state.workflow_status == BrainWorkflowStatus.COMPLETE,
        "scope_current": state.scope_version_id == (
            "scope_v2" if probe_id == SCOPE_RESUME_PROBE else "scope_v1"
        ),
        "governed_evidence_present": bool(state.evidence_ids),
        "p19_assessment_exists": state.latest_p19_assessment_ref is not None,
        "presentation_required": presentation_required,
        "report_exists": report_exists,
        "report_contract_coherent": report_contract_coherent,
        "blocked_provider_requests_zero": int(provider.get("blocked_request_count") or 0) == 0,
        "duplicate_native_execution_zero": duplicate_native == 0,
        "provider_requests": int(provider.get("actual_provider_request_count") or 0),
        "prompt_tokens": int(provider.get("prompt_tokens") or 0),
        "native_acquisitions": len(verified_links),
        "p17_provider_requests": p17_provider_requests,
        "p19_provider_requests": p19_provider_requests,
        "intake_provider_requests": int(sources.get("research_intake") or 0),
        "metabase_provider_requests": int(sources.get("metabase") or 0),
        "candidate_count": len(candidate_ids),
        "candidate_projection_coherent": candidate_projection_coherent,
        "hypothesis_count": len(hypotheses),
        "evidence_grounded_hypothesis_count": len(evidence_grounded),
        "p17_claim_count": len(p17_claims),
        "p17_discriminating_test_count": len(p17_test_steps),
        "discovery_candidate_path": discovery_candidate_path,
        "discovery_honest_stop": discovery_honest_stop,
    }
    checks: dict[str, bool] = {
        "scope_current": bool(common["scope_current"]),
        "governed_evidence_present": bool(common["governed_evidence_present"]),
        "blocked_provider_requests_zero": bool(common["blocked_provider_requests_zero"]),
        "duplicate_native_execution_zero": bool(common["duplicate_native_execution_zero"]),
        "intake_cardinality": (
            common["intake_provider_requests"] == 2
            if probe_id == SCOPE_RESUME_PROBE
            else common["intake_provider_requests"] <= 1
        ),
    }
    if probe_id != "R_LIVE_3_DISCOVERY":
        checks.update(
            {
                "terminal_complete": bool(common["terminal_complete"]),
                "p19_assessment_exists": bool(common["p19_assessment_exists"]),
                "report_contract_coherent": bool(common["report_contract_coherent"]),
            }
        )

    if probe_id == "R_LIVE_1_ONE_PASS":
        checks.update(
            {
                "one_native_acquisition": common["native_acquisitions"] == 1,
                "p17_provider_calls_zero": common["p17_provider_requests"] == 0,
                "no_discriminating_reentry": common["p17_discriminating_test_count"] == 0,
                "two_competing_hypotheses": common["hypothesis_count"] >= 2,
                "hypotheses_grounded": common["evidence_grounded_hypothesis_count"] >= 2,
                "provider_slo": common["provider_requests"] <= 8,
                "prompt_slo": common["prompt_tokens"] <= 150000,
            }
        )
    elif probe_id == "R_LIVE_2_ADAPTIVE":
        checks.update(
            {
                "initial_plus_one_native": common["native_acquisitions"] == 2,
                "exactly_one_discriminating_reentry": common["p17_discriminating_test_count"] == 1,
                "two_competing_hypotheses": common["hypothesis_count"] >= 2,
                "hypotheses_grounded": common["evidence_grounded_hypothesis_count"] >= 2,
                "provider_slo": common["provider_requests"] <= 12,
            }
        )
    elif probe_id == "R_LIVE_3_DISCOVERY":
        expected_p19_calls = 1 if common["candidate_count"] > 0 else 0
        checks.update(
            {
                "one_initial_native_acquisition": common["native_acquisitions"] == 1,
                "p17_discovery_provider_calls_zero": (
                    common["p17_provider_requests"] == 0
                ),
                "candidate_projection_coherent": bool(
                    common["candidate_projection_coherent"]
                ),
                "report_contract_coherent": bool(
                    common["report_contract_coherent"]
                ),
                "p19_initial_assessment_cardinality": (
                    common["p19_provider_requests"] == expected_p19_calls
                ),
                "no_discriminating_reentry": (
                    common["p17_discriminating_test_count"] == 0
                ),
                "typed_discovery_terminal": (
                    common["discovery_candidate_path"]
                    or common["discovery_honest_stop"]
                ),
                "provider_slo": common["provider_requests"] <= 12,
            }
        )
    else:
        scope = scope_resume or {}
        checks.update(
            {
                "scope_version_advanced": (
                    scope.get("first_scope_version_id") == "scope_v1"
                    and scope.get("second_scope_version_id") == "scope_v2"
                ),
                "same_logical_lineage": bool(scope.get("same_lineage")),
                "prior_session_historical": bool(scope.get("prior_historical")),
                "evidence_disjoint": bool(scope.get("evidence_disjoint")),
                "checkpoint_resume": bool(scope.get("checkpoint_resume")),
                "two_native_acquisitions": common["native_acquisitions"] == 2,
                "two_intake_calls": common["intake_provider_requests"] == 2,
                "p17_provider_calls_zero": common["p17_provider_requests"] == 0,
                "no_discriminating_reentry": common["p17_discriminating_test_count"] == 0,
                "provider_slo": common["provider_requests"] <= 12,
            }
        )

    return {
        **common,
        "checks": checks,
        "mechanical_green": all(checks.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-id", required=True, choices=LIVE_PROBES)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--binding-manifest", type=Path, required=True)
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

    api_key = os.environ.get("DIMA_OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY required")
    _require_locked_engine_runtime(args)

    is_scope_resume = args.probe_id == SCOPE_RESUME_PROBE
    question = (
        SCOPE_RESUME_TURNS[0]
        if is_scope_resume
        else str(PROBES[args.probe_id]["turns"][0])
    )
    manual_contract = (
        SCOPE_RESUME_MANUAL_CONTRACT
        if is_scope_resume
        else (
            DISCOVERY_MANUAL_CONTRACT
            if args.probe_id == "R_LIVE_3_DISCOVERY"
            else tuple(PROBES[args.probe_id]["manual_contract"])
        )
    )
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

    budget = OrchestrationBudget(MAX_ORCHESTRATION_BOUNDARY_UNITS)
    raw_material = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected,
    )
    material = BoundedMaterialExecutor(raw_material, budget=budget)
    research = ResearchAskOrchestrator(
        store=store,
        bridge_factory=subjects,
        material_executor=material,
    )

    proxy = args.provider_proxy_base_url.rstrip("/")
    raw_intake = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
        base_url=proxy + "/source/research_intake/v1",
        owner="research_intake",
    )
    raw_p17 = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
        base_url=proxy + "/source/p17_manager/v1",
        owner="p17_manager",
    )
    raw_p18 = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
        base_url=proxy + "/source/p18_manager/v1",
        owner="p18_manager",
    )
    raw_p19 = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
        base_url=proxy + "/source/p19_manager/v1",
        owner="p19_manager",
    )
    intake_transport = BoundedStructuredTransport(
        raw_intake, budget=budget, owner="research_intake"
    )
    p17_transport = BoundedStructuredTransport(
        raw_p17, budget=budget, owner="p17_manager"
    )
    p18_transport = BoundedStructuredTransport(
        raw_p18, budget=budget, owner="p18_manager"
    )
    p19_transport = BoundedStructuredTransport(
        raw_p19, budget=budget, owner="p19_manager"
    )

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
    relationships = BusinessRelationshipPolicyStore(
        research_store=store,
        db_engine=db_engine,
    )

    current_principal = principal()
    activities = DimaBrainV2Activities(
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
        engine_identity=f"{args.engine_sha}@{args.runtime_image_digest}",
        model_profile=MODEL,
        request_ref_prefix=f"brain-v2-live:{args.probe_id}",
    )

    report: dict[str, Any] = {
        "schema_version": "dima_brain_v2_phase1_live_v1",
        "probe_id": args.probe_id,
        "candidate_product_sha": args.candidate_product_sha,
        "checkout_sha": args.checkout_sha,
        "engine_sha": args.engine_sha,
        "engine_release": args.runtime_tag,
        "engine_image_digest": args.runtime_image_digest,
        "langgraph_model_policy": MODEL,
        "metabot_model": METABOT_MODEL,
        "question": question,
        "manual_contract": list(manual_contract),
        "manual_quality_score": None,
        "manual_quality_status": "PENDING",
        "runtime": "BRAIN_V2_LANGGRAPH",
    }
    legacy_modules = (
        "lab.metabase.core_b.live_sentinel",
        "lab.metabase.core_b.phase1_pinpoint_live",
        "app.v3.product.composition",
    )
    loaded_legacy_modules = tuple(
        name for name in legacy_modules if name in sys.modules
    )
    if loaded_legacy_modules:
        raise RuntimeError(
            "BRAIN_V2_LEGACY_RUNTIME_IMPORTED:"
            + ",".join(loaded_legacy_modules)
        )
    report["legacy_composer_calls"] = 0
    started = time.monotonic()
    state = None
    try:
        with postgres_checkpoint_saver(
            args.checkpoint_dsn,
            setup=True,
        ) as checkpointer:
            service = BrainV2Service(
                activities=activities,
                checkpointer=checkpointer,
            )
            initial = BrainGraphState(
                thread_id=f"live:{args.probe_id}:{args.candidate_product_sha[:12]}",
                tenant_binding=ResearchAskOrchestrator.tenant_binding_for(current_principal),
                principal_ref=str(current_principal.user_id),
                current_user_input=question,
            )
            first_state = service.run(initial)
            first_checkpointed = service.state(thread_id=first_state.thread_id)
            first_checkpoint_roundtrip = (
                first_checkpointed is not None
                and first_checkpointed.model_dump(mode="json")
                == first_state.model_dump(mode="json")
            )
            first_budget_by_owner = dict(budget.by_owner)
            first_native_count = len(
                tuple(
                    item for item in _links(db_engine, first_state.research_session_id)
                    if getattr(item, "status", None) == "VERIFIED"
                )
            )
            if is_scope_resume:
                state = service.continue_turn(
                    thread_id=first_state.thread_id,
                    tenant_binding=first_state.tenant_binding,
                    principal_ref=first_state.principal_ref,
                    user_input=SCOPE_RESUME_TURNS[1],
                )
            elif args.probe_id == RELATIONSHIP_REPORT:
                state = service.continue_report_turn(
                    thread_id=first_state.thread_id,
                    tenant_binding=first_state.tenant_binding,
                    principal_ref=first_state.principal_ref,
                    user_input=str(PROBES[args.probe_id]["turns"][1]),
                )
            else:
                state = first_state
            second_checkpointed = service.state(thread_id=state.thread_id)
            second_checkpoint_roundtrip = (
                second_checkpointed is not None
                and second_checkpointed.model_dump(mode="json")
                == state.model_dump(mode="json")
            )
            report["checkpoint_roundtrip_equal"] = (
                first_checkpoint_roundtrip and second_checkpoint_roundtrip
            )
            if state is not first_state:
                report["first_brain_state"] = first_state.model_dump(mode="json")
            report["brain_state"] = state.model_dump(mode="json")

        assert state is not None
        session = research.resume_state(
            session_id=state.research_session_id,
            principal=current_principal,
        )
        brief = session.accepted_brief
        if brief is None:
            raise RuntimeError("live Brain V2 session has no accepted brief")
        goals = tuple(brief.questions)
        root_goals = tuple(
            item for item in goals if item.kind.value == "root_cause"
        )
        material_groups = project_material_groups(session)
        material_contracts = {
            item.goal_id: _safe(
                analytical_scope_contract(
                    session=session,
                    obligation_id=item.goal_id,
                )
            )
            for item in goals
        }
        report["accepted_intent"] = {
            "goals": [_safe(item) for item in goals],
            "scope": _safe(brief.scope),
            "material_groups": [_safe(item) for item in material_groups],
            "material_contracts": material_contracts,
        }
        p17_snapshot = investigation.snapshot(
            session_id=session.session_id,
            principal=current_principal,
        )
        root_goal = root_goals[0] if len(root_goals) == 1 else None
        p19_snapshot = (
            epistemics.snapshot(
                research_session_id=session.session_id,
                obligation_id=root_goal.goal_id,
                principal=current_principal,
            )
            if root_goal is not None
            else None
        )
        assessment = (
            epistemics.load_assessment(
                assessment_id=state.latest_p19_assessment_ref,
                principal=current_principal,
            )
            if state.latest_p19_assessment_ref
            else None
        )
        p18_uses = tuple(
            relationships.load_use(
                session_id=session.session_id,
                policy_use_id=policy_use_id,
                principal=current_principal,
            )
            for policy_use_id in state.p18_policy_use_refs
        )
        report_doc = (
            reports.load(report_id=state.report_ref, principal=current_principal)
            if state.report_ref
            else None
        )
        scope_resume = None
        if is_scope_resume:
            first_session = research.resume_state(
                session_id=first_state.research_session_id,
                principal=current_principal,
            )
            prior_historical = False
            try:
                store.assert_lineage_head(first_session)
            except Exception:
                prior_historical = True
            first_links = _links(db_engine, first_session.session_id)
            current_links = _links(db_engine, session.session_id)
            links = tuple((*first_links, *current_links))
            first_evidence_ids = tuple(first_state.evidence_ids)
            current_evidence_ids = tuple(state.evidence_ids)
            scope_resume = {
                "first_session_id": first_session.session_id,
                "second_session_id": session.session_id,
                "first_scope_version_id": first_state.scope_version_id,
                "second_scope_version_id": state.scope_version_id,
                "first_lineage_id": first_session.lineage_id,
                "second_lineage_id": session.lineage_id,
                "same_lineage": first_session.lineage_id == session.lineage_id,
                "prior_historical": prior_historical,
                "first_evidence_ids": list(first_evidence_ids),
                "second_evidence_ids": list(current_evidence_ids),
                "evidence_disjoint": set(first_evidence_ids).isdisjoint(
                    current_evidence_ids
                ),
                "checkpoint_resume": bool(
                    report.get("checkpoint_roundtrip_equal")
                ),
            }
            report["scope_resume"] = scope_resume
        else:
            links = _links(db_engine, session.session_id)
        provider = _provider_receipt(args.provider_receipt)
        report["agent_api_request_count"] = request_audit.agent_api_request_count
        report["native_http_requests"] = [
            {"method": method, "path": path}
            for method, path in request_audit.requests
        ]
        current_evidence_ids = {
            item.evidence_id for item in session.evidence_refs
        }
        stale_evidence_count = len(
            set(state.evidence_ids) - current_evidence_ids
        )
        expected_tenant_binding = ResearchAskOrchestrator.tenant_binding_for(
            current_principal
        )
        cross_tenant_violation_count = int(
            state.tenant_binding != expected_tenant_binding
            or session.tenant_binding != expected_tenant_binding
            or state.principal_ref != str(current_principal.user_id)
        )
        causal_overclaim_count = (
            sum(
                1
                for statement in getattr(report_doc, "statements", ())
                if str(
                    getattr(
                        getattr(statement, "statement_kind", None),
                        "value",
                        getattr(statement, "statement_kind", ""),
                    )
                )
                in {"CAUSAL", "ROOT_CAUSE"}
            )
            if args.probe_id in {RELATIONSHIP_REPORT, MULTI_INTENT}
            and report_doc is not None
            else 0
        )
        report["stale_evidence_count"] = stale_evidence_count
        report["cross_tenant_violation_count"] = cross_tenant_violation_count
        report["causal_overclaim_count"] = causal_overclaim_count
        native_occurrences = _native_occurrence_projection(links)

        report["research"] = {
            "session_id": session.session_id,
            "lineage_id": session.lineage_id,
            "scope_version_id": brief.scope.scope_version.version_id,
            "obligations": [_safe(item) for item in session.obligations],
            "evidence_refs": [_safe(item) for item in session.evidence_refs],
        }
        report["p17"] = {
            "claims": [_safe(item) for item in p17_snapshot.claims],
            "investigation": _safe(p17_snapshot.investigation),
            "evidence_results": [_safe(item) for item in p17_snapshot.evidence_results],
        }
        report["p18"] = {
            "requirement_ids": list(state.p18_requirement_ids),
            "policy_uses": [_safe(item) for item in p18_uses],
        }
        report["p19"] = {
            "assessment": _safe(assessment),
            "snapshot": _safe(p19_snapshot),
        }
        report["p20"] = _safe(report_doc)
        report["native_occurrences"] = native_occurrences
        report["provider_receipt"] = provider
        report["orchestration_boundary_units"] = budget.used
        report["orchestration_boundary_units_by_owner"] = dict(
            sorted(budget.by_owner.items())
        )

        if args.probe_id in {RELATIONSHIP_REPORT, MULTI_INTENT}:
            first_same_session = (
                first_state.research_session_id == state.research_session_id
            )
            first_same_scope = (
                first_state.scope_version_id == state.scope_version_id
            )
            report["mechanical"] = phase2_mechanical(
                probe_id=args.probe_id,
                state=state,
                first_state=(first_state if args.probe_id == RELATIONSHIP_REPORT else None),
                native_occurrences=tuple(native_occurrences),
                first_native_count=(
                    first_native_count
                    if args.probe_id == RELATIONSHIP_REPORT
                    else None
                ),
                p18_uses=p18_uses,
                report_present=report_doc is not None,
                budget_before_report=(
                    first_budget_by_owner
                    if args.probe_id == RELATIONSHIP_REPORT
                    else None
                ),
                budget_after=dict(budget.by_owner),
                same_research_session=first_same_session,
                same_scope_version=first_same_scope,
                checkpoint_roundtrip=bool(
                    report.get("checkpoint_roundtrip_equal")
                ),
                legacy_composer_calls=int(
                    report.get("legacy_composer_calls") or 0
                ),
                agent_api_request_count=int(
                    report.get("agent_api_request_count") or 0
                ),
                stale_evidence_count=stale_evidence_count,
                cross_tenant_violation_count=cross_tenant_violation_count,
                causal_overclaim_count=causal_overclaim_count,
            )
            report["boundary_trace"] = {
                "runtime": "BRAIN_V2_LANGGRAPH",
                "events": [
                    "dima.intent.interpret",
                    "dima.scope.resolve",
                    "dima.requirements.plan",
                    "dima.material.group",
                    "dima.native.execute",
                    "dima.evidence.admit",
                    "dima.requirement.dispatch",
                    "dima.p18.adjudicate",
                    "dima.completion.evaluate",
                    "dima.p20.report",
                ],
            }
        else:
            if root_goal is None or p19_snapshot is None:
                raise RuntimeError("RCA live probe requires exactly one root-cause goal")
            material_contract = analytical_scope_contract(
                session=session,
                obligation_id=root_goal.goal_id,
            )
            scope_fingerprint = brief.scope_fingerprint
            material_fingerprint = material_contract.fingerprint
            trace_events = [
                BoundaryTraceEvent(
                    boundary=BoundaryName.INTENT_INTERPRET,
                    owner="ResearchIntake",
                    thread_id=state.thread_id,
                    scope_version_id=state.scope_version_id,
                    scope_fingerprint=scope_fingerprint,
                    provider_call_count=int(
                        (provider.get("by_owner") or {})
                        .get("research_intake", {})
                        .get("requests", 0)
                    ),
                ),
                BoundaryTraceEvent(
                    boundary=BoundaryName.SCOPE_RESOLVE,
                    owner="ResearchScope",
                    thread_id=state.thread_id,
                    scope_version_id=state.scope_version_id,
                    scope_fingerprint=scope_fingerprint,
                ),
                BoundaryTraceEvent(
                    boundary=BoundaryName.MATERIAL_COMPILE,
                    owner="ResearchAnalyticalScope",
                    thread_id=state.thread_id,
                    scope_version_id=state.scope_version_id,
                    scope_fingerprint=scope_fingerprint,
                    material_fingerprint=material_fingerprint,
                ),
                BoundaryTraceEvent(
                    boundary=BoundaryName.NATIVE_EXECUTE,
                    owner="Metabase",
                    thread_id=state.thread_id,
                    scope_version_id=state.scope_version_id,
                    scope_fingerprint=scope_fingerprint,
                    material_fingerprint=material_fingerprint,
                    native_acquisition_count=len(links),
                ),
                BoundaryTraceEvent(
                    boundary=BoundaryName.EVIDENCE_ADMIT,
                    owner="Evidence",
                    thread_id=state.thread_id,
                    scope_version_id=state.scope_version_id,
                    scope_fingerprint=scope_fingerprint,
                    material_fingerprint=material_fingerprint,
                    evidence_revision=state.evidence_revision,
                ),
                BoundaryTraceEvent(
                    boundary=BoundaryName.P19_ASSESS,
                    owner="P19",
                    thread_id=state.thread_id,
                    scope_version_id=state.scope_version_id,
                    scope_fingerprint=scope_fingerprint,
                    evidence_revision=state.evidence_revision,
                    hypothesis_revision=state.hypothesis_revision,
                ),
            ]
            if report_doc is not None:
                trace_events.append(
                    BoundaryTraceEvent(
                        boundary=BoundaryName.P20_REPORT,
                        owner="P20",
                        thread_id=state.thread_id,
                        scope_version_id=state.scope_version_id,
                        scope_fingerprint=scope_fingerprint,
                        evidence_revision=state.evidence_revision,
                        hypothesis_revision=state.hypothesis_revision,
                    )
                )
            report["boundary_trace"] = BoundaryTrace(
                events=tuple(trace_events)
            ).public_receipt()
            report["mechanical"] = _mechanical(
                probe_id=args.probe_id,
                state=state,
                provider=provider,
                links=links,
                p17_snapshot=p17_snapshot,
                p19_snapshot=p19_snapshot,
                report_doc=report_doc,
                scope_resume=scope_resume,
            )

        report["mechanical_verdict"] = (
            "GREEN" if report["mechanical"]["mechanical_green"] else "RED"
        )
    except Exception as exc:
        report["exception"] = _exception(exc)
        if (
            report["exception"].get("first_invalid_boundary") is not None
            or report["exception"].get("last_valid_boundary") is not None
        ):
            report["boundary_trace"] = {
                "last_valid_boundary": report["exception"].get(
                    "last_valid_boundary"
                ),
                "first_invalid_boundary": report["exception"].get(
                    "first_invalid_boundary"
                ),
                "expected_fingerprint": report["exception"].get(
                    "expected_fingerprint"
                ),
                "observed_fingerprint": report["exception"].get(
                    "observed_fingerprint"
                ),
                "scope_fingerprint": report["exception"].get(
                    "scope_fingerprint"
                ),
                "material_fingerprint": report["exception"].get(
                    "material_fingerprint"
                ),
                "expected_semantic_shape": report["exception"].get(
                    "expected_semantic_shape"
                ),
                "observed_semantic_shape": report["exception"].get(
                    "observed_semantic_shape"
                ),
                "events": [],
            }
        report["mechanical_verdict"] = "RED"
    finally:
        report["latency_ms"] = int((time.monotonic() - started) * 1000)
        for transport in (raw_intake, raw_p17, raw_p19):
            transport.close()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "probe_id": args.probe_id,
                "mechanical_verdict": report.get("mechanical_verdict"),
                "provider_requests": (report.get("provider_receipt") or {}).get(
                    "actual_provider_request_count"
                ),
                "prompt_tokens": (report.get("provider_receipt") or {}).get(
                    "prompt_tokens"
                ),
                "latency_ms": report.get("latency_ms"),
                "exception": (report.get("exception") or {}).get("error_code"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
