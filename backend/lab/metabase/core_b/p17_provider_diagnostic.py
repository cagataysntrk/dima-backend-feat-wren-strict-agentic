#!/usr/bin/env python3
"""One exact Core-B P17 structured-provider diagnostic probe.

This lab runner reuses the canonical root_cause_tr live composition path and stops
at the first P17 structured-provider rejection. It is diagnostic evidence only:
no schema fix, retry, fallback model, or P17 semantic change is permitted here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from app.v3.business_relationship_policy import BusinessRelationshipPolicyStore
from app.v3.claim_lineage import ClaimLineageStore
from app.v3.hypothesis_root_cause import HypothesisRootCauseStore
from app.v3.hypothesis_root_cause_provider import StructuredP19AssessmentManager
from app.v3.product.composition import HeadlessProductComposer
from app.v3.product.service import HeadlessProductService, ProductSources
from app.v3.report_document import ReportDocumentStore
from app.v3.research_exploration import NativeResearchExploration
from app.v3.research_followup import NativeResearchFollowupExecutor
from app.v3.research_intake import ResearchIntakeCompiler, ResearchIntakeTerminal
from app.v3.research_manager import ResearchInvestigationManager, ResearchReasoningStore
from app.v3.research_manager_provider import StructuredResearchProposalManager
from app.v3.research_native_gateway import (
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
)
from app.v3.research_product import NativeResearchOccurrenceRunner, ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from app.v3.structured_transport import (
    OpenRouterStructuredJSONTransport,
    StructuredProviderError,
)
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from lab.metabase.core_b.live_sentinel import (
    MODEL,
    _build_control_plane,
    _catalog,
    _load_cases,
    _login,
    _principal,
)


ROOT_CASE_ID = "root_cause_tr"
ENGINE_SHA = "cbe313af9ac2d5960f662068e433d328d896fb06"


def _write_receipt(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--control-db", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--runtime-image-digest", required=True)
    ap.add_argument("--build-identity", required=True)
    ap.add_argument("--image-identity", required=True)
    ap.add_argument("--platform-sha", required=True)
    args = ap.parse_args()

    if args.engine_sha != ENGINE_SHA:
        raise RuntimeError("diagnostic requires exact certified dima.6 engine")

    api_key = os.environ.get("DIMA_OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY is required")

    token, current = _login(args.base_url, args.email, args.password)
    db_engine = _build_control_plane(args.control_db, int(current["id"]))
    session_store = ResearchSessionStore(db_engine)
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
        store=session_store,
        expected_identity=expected,
    )
    orchestrator = ResearchAskOrchestrator(
        store=session_store,
        bridge_factory=subjects,
        material_executor=material_executor,
    )

    intake_transport = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
    )
    p17_transport = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
    )
    p19_transport = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
    )
    intake = ResearchIntakeCompiler(transport=intake_transport)
    product = HeadlessProductService(
        sources=ProductSources(
            research=orchestrator,
            intake=intake,
        )
    )

    reasoning = ResearchReasoningStore(db_engine)
    claim_store = ClaimLineageStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    occurrence_runner = NativeResearchOccurrenceRunner(
        store=session_store,
        bridge_factory=subjects,
        material_executor=material_executor,
    )
    exploration = NativeResearchExploration(
        research_store=session_store,
        subject_provider=subjects,
    )
    p17 = ResearchInvestigationManager(
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
    p17_manager = StructuredResearchProposalManager(
        transport=p17_transport,
    )
    p18 = BusinessRelationshipPolicyStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    p19 = HypothesisRootCauseStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    p19_manager = StructuredP19AssessmentManager(
        transport=p19_transport,
    )
    p20 = ReportDocumentStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    composer = HeadlessProductComposer(
        research=orchestrator,
        investigation=p17,
        investigation_manager=p17_manager,
        reasoning=reasoning,
        relationships=p18,
        epistemics=p19,
        epistemic_manager=p19_manager,
        reports=p20,
    )

    case = _load_cases(args.manifest)[ROOT_CASE_ID]
    question = str(case["platform_question"])
    intake_result = product.research_question(
        question=question,
        catalog=_catalog(),
        principal=_principal(),
    )
    if intake_result.terminal != ResearchIntakeTerminal.READY or intake_result.brief is None:
        raise RuntimeError(
            f"root_cause_tr intake did not reach READY: {intake_result.terminal.value}"
        )

    source_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()
    receipt: dict
    try:
        composer.compose(
            brief=intake_result.brief,
            principal=_principal(),
            request_ref=f"diagnostic:{ROOT_CASE_ID}",
            source_message_hash=source_hash,
            native_session_token=token,
        )
    except StructuredProviderError as exc:
        if exc.code != "COGNITION_PROVIDER_REJECTED":
            raise
        if exc.diagnostic is None:
            raise RuntimeError("provider rejection did not preserve diagnostic") from exc
        if p17_transport.call_count != 1:
            raise RuntimeError(
                f"diagnostic must stop after one P17 request, got {p17_transport.call_count}"
            )
        if p19_transport.call_count != 0:
            raise RuntimeError(
                f"diagnostic crossed into P19 unexpectedly: {p19_transport.call_count}"
            )
        diagnostic = exc.diagnostic
        receipt = {
            "schema_version": "core_b_p17_provider_diagnostic_v1",
            "platform_sha": args.platform_sha,
            "case_id": ROOT_CASE_ID,
            "model": diagnostic.model,
            "schema_name": diagnostic.schema_name,
            "schema_fingerprint": diagnostic.schema_fingerprint,
            "http_status": diagnostic.status_code,
            "provider_error_code": diagnostic.provider_error_code,
            "provider_error_message": diagnostic.provider_error_message,
            "provider_error_metadata": diagnostic.provider_error_metadata,
            "provider_request_id": diagnostic.provider_request_id,
            "response_format_family": diagnostic.response_format_family,
            "bounded_response_excerpt": diagnostic.bounded_response_excerpt,
            "diagnostic_classification": "UNKNOWN_PENDING_REVIEW",
            "p17_provider_call_count": p17_transport.call_count,
            "p19_provider_call_count": p19_transport.call_count,
            "intake_provider_call_count": intake_transport.call_count,
            "engine_sha": args.engine_sha,
            "engine_runtime_tag": args.runtime_tag,
            "full_sentinel_rerun": False,
            "automatic_retry": False,
        }
        _write_receipt(args.output, receipt)
        return 0
    finally:
        intake_transport.close()
        p17_transport.close()
        p19_transport.close()

    receipt = {
        "schema_version": "core_b_p17_provider_diagnostic_v1",
        "platform_sha": args.platform_sha,
        "case_id": ROOT_CASE_ID,
        "model": MODEL,
        "schema_name": None,
        "schema_fingerprint": None,
        "http_status": None,
        "provider_error_code": None,
        "provider_error_message": None,
        "provider_request_id": None,
        "diagnostic_classification": "NO_PROVIDER_REJECTION_OBSERVED",
        "p17_provider_call_count": p17_transport.call_count,
        "p19_provider_call_count": p19_transport.call_count,
        "intake_provider_call_count": intake_transport.call_count,
        "engine_sha": args.engine_sha,
        "engine_runtime_tag": args.runtime_tag,
        "full_sentinel_rerun": False,
        "automatic_retry": False,
    }
    _write_receipt(args.output, receipt)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
