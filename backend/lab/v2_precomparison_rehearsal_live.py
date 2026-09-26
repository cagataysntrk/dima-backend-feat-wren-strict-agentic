"""Manual pre-comparison development rehearsal: 20 real-LLM cases on real Wren.

This is development evidence, not DEV80/Validation50/Hidden50 certification.
Importing this module performs zero provider calls.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any

from app import fanout
from app.config import get_settings
from app.compose import compose_and_build
from app.v2.execution_receipts import build_development_performance_receipt
from app.v2.persistence import DurableCheckpointStore
from app.v2.product_events import ProductEventSink
from app.v2.product_models import ProductAskRequest, ProductLane, ProductStatus, mint_product_turn_ref
from app.v2.report_builder import ReportBlockKind
from app.wren_service import WrenService
from control_plane.authorize import Principal
from lab.v2_day10_product_mvp_live import (
    CountingWren,
    RoleCallBudget,
    _build_product,
    _candidate_section_token,
    _event_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_precomparison_rehearsal_cases.json"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_precomparison_rehearsal.json"

ROLE_LIMITS = {
    "FAST_LANGUAGE": 50,
    "RESEARCH_MANAGER": 120,
    "SEMANTIC_LINKER": 50,
    "TEMPORAL_NORMALIZER": 30,
    "REPORT_NARRATOR": 50,
}


def _value(value: Any) -> Any:
    return getattr(value, "value", value)


def _confirmed_cause_count(response) -> int:
    report = getattr(response, "report", None)
    if report is None:
        return 0
    return sum(
        1
        for section in report.report.sections
        for block in section.blocks
        if getattr(block, "epistemic_label", None) is not None
        and _value(block.epistemic_label) == "CONFIRMED_CAUSE"
    )


def _role_delta(calls: list[dict[str, Any]], start: int) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in calls[start:]:
        role = str(item["role"])
        out[role] = out.get(role, 0) + 1
    return out


def _base_checks(case: dict[str, Any], response) -> dict[str, bool]:
    lane = _value(response.lane)
    status = _value(response.status)
    checks = {
        "lane_allowed": lane in set(case["lanes"]),
        "status_allowed": status in set(case["statuses"]),
        "evidence_floor": len(response.evidence_refs) >= int(case.get("min_evidence", 0)),
        "confirmed_cause_forbidden": _confirmed_cause_count(response) == 0,
    }
    if bool(case.get("verified")):
        checks["verified_complete"] = bool(response.terminal_receipt.verified_complete)
    return checks


def _first_section_token(response) -> str:
    continuations = tuple(response.section_continuations or ())
    if not continuations:
        raise RuntimeError("report exposes no signed section continuation")
    return continuations[0].token


def _coordinator(
    *,
    settings,
    budget,
    service,
    principal,
    checkpoint_store=None,
):
    coordinator, research_lane, standard_lane, structured = _build_product(
        settings=settings,
        budget=budget,
        service=service,
        principal=principal,
        checkpoint_store=checkpoint_store,
    )
    return coordinator, research_lane, standard_lane, structured


def _handle(
    coordinator,
    *,
    principal,
    question: str,
    session_id: str,
    thread_id: str,
    token: str | None = None,
):
    turn_ref = mint_product_turn_ref()
    return coordinator.handle(
        request=object(),
        body=ProductAskRequest(
            question=question,
            session_id=session_id,
            thread_id=thread_id,
            report_section_token=token,
        ),
        principal=principal,
        event_sink=ProductEventSink(
            request_ref=f"rehearsal:{session_id}:{time.time_ns()}",
            turn_ref=turn_ref,
        ),
        turn_ref=turn_ref,
    )


def _case_receipt(
    *,
    case: dict[str, Any],
    response,
    elapsed_ms: int,
    budget: RoleCallBudget,
    budget_start: int,
    service: CountingWren,
    wren_start: tuple[int, int, int],
    checks: dict[str, bool],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = _event_metrics(response.events)
    role_calls = _role_delta(budget.calls, budget_start)
    wren_query = service.query_calls - wren_start[0]
    wren_dry = service.dry_plan_calls - wren_start[1]
    wren_cube = service.cube_sql_calls - wren_start[2]
    performance = build_development_performance_receipt(
        first_status_ms=metrics["first_status_ms"],
        first_verified_evidence_ms=metrics["first_verified_evidence_ms"],
        report_ready_ms=metrics["report_ready_ms"],
        total_ms=elapsed_ms,
        provider_calls_by_role=role_calls,
        wren_query_calls=wren_query,
        wren_dry_plan_calls=wren_dry,
        wren_cube_sql_calls=wren_cube,
        manager_turns=int(response.terminal_receipt.manager_turns),
    )
    terminal_receipt = getattr(response, "terminal_receipt", None)
    events = tuple(getattr(response, "events", ()) or ())
    diagnostics = {
        "terminal_reasons": list(
            getattr(terminal_receipt, "reasons", ()) or ()
        ),
        "terminal_status": getattr(terminal_receipt, "terminal_status", None),
        "manager_turns": int(
            getattr(terminal_receipt, "manager_turns", 0) or 0
        ),
        "event_kinds": [
            _value(getattr(item, "kind", None))
            for item in events
        ],
        "event_refs": [
            list(getattr(item, "refs", ()) or ())
            for item in events
        ],
    }
    return {
        "id": case["id"],
        "kind": case["kind"],
        "category": case["category"],
        "question": case["question"],
        "lane": _value(response.lane),
        "status": _value(response.status),
        "verified_complete": bool(response.terminal_receipt.verified_complete),
        "evidence_count": len(response.evidence_refs),
        "artifact_count": len(response.artifact_refs),
        "checks": checks,
        "pass": all(checks.values()),
        "performance": performance,
        "diagnostics": diagnostics,
        "extra": extra or {},
    }


def _run_prompt(case, *, settings, budget, service, principal, checkpoint_root):
    coordinator, _, _, _ = _coordinator(
        settings=settings,
        budget=budget,
        service=service,
        principal=principal,
    )
    session = f"rehearsal:{case['id']}"
    budget_start = len(budget.calls)
    wren_start = (service.query_calls, service.dry_plan_calls, service.cube_sql_calls)
    started = time.monotonic()
    response = _handle(
        coordinator,
        principal=principal,
        question=case["question"],
        session_id=session,
        thread_id=session,
    )
    elapsed_ms = int((time.monotonic() - started) * 1000)
    checks = _base_checks(case, response)
    return _case_receipt(
        case=case,
        response=response,
        elapsed_ms=elapsed_ms,
        budget=budget,
        budget_start=budget_start,
        service=service,
        wren_start=wren_start,
        checks=checks,
    )


def _run_signed_continuation(case, *, settings, budget, service, principal, checkpoint_root):
    coordinator, _, _, _ = _coordinator(
        settings=settings,
        budget=budget,
        service=service,
        principal=principal,
    )
    session = f"rehearsal:{case['id']}"
    budget_start = len(budget.calls)
    wren_start = (service.query_calls, service.dry_plan_calls, service.cube_sql_calls)
    started = time.monotonic()
    initial = _handle(
        coordinator,
        principal=principal,
        question=case["question"],
        session_id=session,
        thread_id=session,
    )
    initial_checks = _base_checks(case, initial)
    token = _first_section_token(initial)
    initial_dump = initial.report.model_dump(mode="json") if initial.report else None
    continuation = _handle(
        coordinator,
        principal=principal,
        question=case["followup"],
        session_id=session,
        thread_id=session,
        token=token,
    )
    elapsed_ms = int((time.monotonic() - started) * 1000)
    checks = {
        **initial_checks,
        "continuation_report": continuation.status == ProductStatus.REPORT,
        "continuation_verified": bool(continuation.terminal_receipt.verified_complete),
        "version_incremented": bool(
            initial.report
            and continuation.report
            and continuation.report.version == initial.report.version + 1
        ),
        "v1_immutable": bool(
            initial.report
            and initial.report.model_dump(mode="json") == initial_dump
        ),
    }
    return _case_receipt(
        case=case,
        response=continuation,
        elapsed_ms=elapsed_ms,
        budget=budget,
        budget_start=budget_start,
        service=service,
        wren_start=wren_start,
        checks=checks,
        extra={
            "initial_status": _value(initial.status),
            "continuation_status": _value(continuation.status),
        },
    )


def _run_restart(case, *, settings, budget, service, principal, checkpoint_root):
    store = DurableCheckpointStore(checkpoint_root / case["id"])
    first, _, _, _ = _coordinator(
        settings=settings,
        budget=budget,
        service=service,
        principal=principal,
        checkpoint_store=store,
    )
    session = f"rehearsal:{case['id']}"
    budget_start = len(budget.calls)
    wren_start = (service.query_calls, service.dry_plan_calls, service.cube_sql_calls)
    started = time.monotonic()
    initial = _handle(
        first,
        principal=principal,
        question=case["question"],
        session_id=session,
        thread_id=session,
    )
    initial_checks = _base_checks(case, initial)
    token = _first_section_token(initial)
    initial_dump = initial.report.model_dump(mode="json") if initial.report else None

    # Process-restart simulation: new coordinator and empty in-memory continuation
    # registry, same durable checkpoint repository and canonical Wren context.
    restarted, _, _, _ = _coordinator(
        settings=settings,
        budget=budget,
        service=service,
        principal=principal,
        checkpoint_store=store,
    )
    continuation = _handle(
        restarted,
        principal=principal,
        question=case["followup"],
        session_id=session,
        thread_id=session,
        token=token,
    )
    elapsed_ms = int((time.monotonic() - started) * 1000)
    checks = {
        **initial_checks,
        "restart_continuation_report": continuation.status == ProductStatus.REPORT,
        "restart_continuation_verified": bool(
            continuation.terminal_receipt.verified_complete
        ),
        "version_incremented": bool(
            initial.report
            and continuation.report
            and continuation.report.version == initial.report.version + 1
        ),
        "supersedes_v1": bool(
            initial.report
            and continuation.report
            and continuation.report.supersedes_report_ref
            == initial.report.report.report_id
        ),
        "v1_immutable": bool(
            initial.report
            and initial.report.model_dump(mode="json") == initial_dump
        ),
    }
    return _case_receipt(
        case=case,
        response=continuation,
        elapsed_ms=elapsed_ms,
        budget=budget,
        budget_start=budget_start,
        service=service,
        wren_start=wren_start,
        checks=checks,
        extra={
            "initial_status": _value(initial.status),
            "initial_report_version": initial.report.version if initial.report else None,
            "continuation_report_version": (
                continuation.report.version if continuation.report else None
            ),
        },
    )


def _run_foreign_principal(case, *, settings, budget, service, principal, checkpoint_root):
    coordinator, _, _, _ = _coordinator(
        settings=settings,
        budget=budget,
        service=service,
        principal=principal,
    )
    session = f"rehearsal:{case['id']}"
    budget_start = len(budget.calls)
    wren_start = (service.query_calls, service.dry_plan_calls, service.cube_sql_calls)
    started = time.monotonic()
    initial = _handle(
        coordinator,
        principal=principal,
        question=case["question"],
        session_id=session,
        thread_id=session,
    )
    checks = _base_checks(case, initial)
    token = _first_section_token(initial)
    attack_budget_start = len(budget.calls)
    foreign = Principal(
        user_id="rehearsal-foreign-user",
        tenant_id=principal.tenant_id,
        roles=["owner"],
        tenant_slug=principal.tenant_slug,
    )
    rejected = False
    error_type = None
    try:
        _handle(
            coordinator,
            principal=foreign,
            question=case["followup"],
            session_id=session,
            thread_id=session,
            token=token,
        )
    except Exception as exc:  # exact owner may raise typed continuation/authority error
        rejected = True
        error_type = type(exc).__name__
    checks["foreign_principal_rejected"] = rejected
    checks["attack_used_zero_provider_calls"] = len(budget.calls) == attack_budget_start
    elapsed_ms = int((time.monotonic() - started) * 1000)
    return _case_receipt(
        case=case,
        response=initial,
        elapsed_ms=elapsed_ms,
        budget=budget,
        budget_start=budget_start,
        service=service,
        wren_start=wren_start,
        checks=checks,
        extra={"foreign_replay_error_type": error_type},
    )


def run(
    *,
    max_total_model_calls: int,
    output: Path,
    case_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    manifest = json.loads(CASES.read_text(encoding="utf-8"))
    all_cases = list(manifest["cases"])
    if not 20 <= len(all_cases) <= 25:
        raise RuntimeError("development rehearsal must contain 20..25 cases")
    selected = set(case_ids)
    cases = [
        case for case in all_cases
        if not selected or str(case["id"]) in selected
    ]
    missing = selected - {str(case["id"]) for case in cases}
    if missing:
        raise RuntimeError(f"unknown rehearsal case ids: {sorted(missing)}")
    if not cases:
        raise RuntimeError("no rehearsal cases selected")
    if not manifest.get("real_llm_required") or not manifest.get("real_wren_required"):
        raise RuntimeError("rehearsal manifest must require real LLM and real Wren")

    settings = get_settings()
    # A clean CI checkout has no compiled tenant project. Build the governed project
    # deterministically before measuring real Wren; this performs zero provider calls.
    compose_and_build(settings)
    inner = WrenService(
        project_dir=settings.resolved_project_dir(),
        datasource=settings.datasource,
        connection_info=settings.connection_dict(),
    )
    _, fanout_receipt = fanout.refresh_wren_service_certificate(inner)
    if fanout_receipt.get("mdl_version") != inner.mdl_version:
        raise RuntimeError("current-MDL fanout certificate mismatch")
    service = CountingWren(inner)
    budget = RoleCallBudget(
        max_total=max_total_model_calls,
        role_limits=ROLE_LIMITS,
    )
    principal = Principal(
        user_id="precomparison-rehearsal-user",
        tenant_id="precomparison-rehearsal-tenant",
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )

    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="dima-v2-precomparison-") as tmp:
        checkpoint_root = Path(tmp)
        for case in cases:
            try:
                if case["kind"] == "prompt":
                    record = _run_prompt(
                        case,
                        settings=settings,
                        budget=budget,
                        service=service,
                        principal=principal,
                        checkpoint_root=checkpoint_root,
                    )
                elif case["kind"] == "signed_continuation":
                    record = _run_signed_continuation(
                        case,
                        settings=settings,
                        budget=budget,
                        service=service,
                        principal=principal,
                        checkpoint_root=checkpoint_root,
                    )
                elif case["kind"] == "restart_continuation":
                    record = _run_restart(
                        case,
                        settings=settings,
                        budget=budget,
                        service=service,
                        principal=principal,
                        checkpoint_root=checkpoint_root,
                    )
                elif case["kind"] == "foreign_principal_replay":
                    record = _run_foreign_principal(
                        case,
                        settings=settings,
                        budget=budget,
                        service=service,
                        principal=principal,
                        checkpoint_root=checkpoint_root,
                    )
                else:
                    raise RuntimeError(f"unknown rehearsal kind: {case['kind']}")
            except Exception as exc:
                record = {
                    "id": case["id"],
                    "kind": case["kind"],
                    "category": case["category"],
                    "question": case["question"],
                    "pass": False,
                    "checks": {},
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            records.append(record)

    passed = sum(1 for item in records if item.get("pass"))
    payload = {
        "kind": "v2_precomparison_development_rehearsal",
        "status": "pass" if passed == len(records) else "fail",
        "case_count": len(records),
        "full_manifest_case_count": len(all_cases),
        "selected_case_ids": [str(item["id"]) for item in cases],
        "passed": passed,
        "failed": len(records) - passed,
        "real_llm": True,
        "real_wren": True,
        "large_certification_corpus": False,
        "provider_budget": budget.receipt(),
        "wren_calls": {
            "query": service.query_calls,
            "dry_plan": service.dry_plan_calls,
            "cube_sql": service.cube_sql_calls,
        },
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-total-model-calls", type=int, default=180)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--case-id", action="append", default=[])
    args = parser.parse_args()
    if not 1 <= args.max_total_model_calls <= 200:
        raise SystemExit("--max-total-model-calls must be 1..200")
    payload = run(
        max_total_model_calls=args.max_total_model_calls,
        output=args.output,
        case_ids=tuple(args.case_id),
    )
    print(
        f"precomparison rehearsal: {payload['passed']}/{payload['case_count']} "
        f"provider_calls={payload['provider_budget']['total']} "
        f"wren_queries={payload['wren_calls']['query']}"
    )
    for item in payload["records"]:
        if not item.get("pass"):
            print(
                f"RED {item['id']}: {item.get('error_type') or item.get('checks')} "
                f"{item.get('error') or ''}"
            )
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
