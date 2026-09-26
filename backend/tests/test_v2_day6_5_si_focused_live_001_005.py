"""Focused paid Day6.5 Standard composition: frozen 001 + 005 only.

This is a cost-control gate before the final frozen six-case SI closure.
It reads the exact frozen full-live corpus and does not define new user questions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from app import contracts as contracts_module
from app.config import get_settings
from app.v2.context_provider import ContextProviderV0
from app.v2.models import ConversationStateV2, TenantAnalyticsRuntimeV0
from app.v2.standard_lab import StandardLabHarness
from control_plane.authorize import Principal
from lab.si_standard_eval import install_standard_eval_trace, new_case_trace


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_D65_SI_FOCUSED_LIVE") != "1",
    reason="manual-only paid 001+005 SI gate",
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "eval" / "v2_day6_5_si_full_live_frozen.json"
REPORT = ROOT / "lab" / "reports" / "v2_day6_5_si_focused_live_001_005.json"
SELECTED = ("si-live-001", "si-live-005")


def _runtime(wren, schema):
    principal = Principal(
        user_id="si-focused-live-user",
        tenant_id="si-focused-live-tenant",
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id=str(principal.tenant_id),
        tenant_slug=principal.tenant_slug,
        principal_user_id=str(principal.user_id),
        roles=tuple(principal.roles),
        mdl_version=wren.mdl_version,
        catalog=schema.get("catalog"),
        schema_name=schema.get("schema_name"),
        db_online=bool(schema.get("db_online", True)),
    )
    return principal, runtime


def _mismatches(case, outcome, *, before, after, authority_registry, turn_id):
    out = []
    if outcome.status.value != case["expected_status"]:
        out.append(
            f"status expected={case['expected_status']} actual={outcome.status.value}"
        )
    if case["expected_status"] == "ACCEPTED":
        if not outcome.accepted:
            out.append("accepted case did not produce complete accepted outcome")
        if outcome.authority is None:
            out.append("accepted case missing authority")
        if outcome.execution is None:
            out.append("accepted case missing execution")
        if after <= before:
            out.append("accepted case persisted no QueryContract")
        if authority_registry.accepted(turn_id) is None:
            out.append("shared authority registry missing accepted turn")
        if outcome.execution is not None:
            ir = outcome.execution.analytics_ir
            if ir.cube != case["expected_cube"]:
                out.append(
                    f"cube expected={case['expected_cube']} actual={ir.cube}"
                )
            if not ir.metrics or ir.metrics[0].canonical_name != case["expected_metric"]:
                actual = ir.metrics[0].canonical_name if ir.metrics else None
                out.append(
                    f"metric expected={case['expected_metric']} actual={actual}"
                )
            actual_dimensions = [d.canonical_name for d in ir.dimensions]
            if actual_dimensions != case["expected_dimensions"]:
                out.append(
                    "dimensions expected="
                    f"{case['expected_dimensions']} actual={actual_dimensions}"
                )
            expected_ranking = case.get("expected_ranking")
            if expected_ranking is None and ir.ranking is not None:
                out.append("unexpected ranking")
            elif expected_ranking is not None:
                if ir.ranking is None:
                    out.append("expected ranking missing")
                else:
                    if ir.ranking.direction != expected_ranking["direction"]:
                        out.append("ranking direction mismatch")
                    if ir.ranking.limit != expected_ranking["limit"]:
                        out.append("ranking limit mismatch")
    return out


def test_focused_paid_frozen_001_005(wren, schema, monkeypatch):
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert corpus["frozen"] is True
    by_id = {case["id"]: case for case in corpus["cases"]}
    cases = [by_id[case_id] for case_id in SELECTED]
    assert [case["id"] for case in cases] == list(SELECTED)

    get_settings.cache_clear()
    settings = get_settings()
    harness = StandardLabHarness(settings=settings)
    telemetry = harness.telemetry

    assert telemetry["standard_cognition"]["model"] == "openai/gpt-5.6-sol"
    assert telemetry["semantic_linker"]["model"] == "openai/gpt-5.6-luna"
    assert telemetry["temporal_normalizer"]["model"] == "openai/gpt-5.6-sol"

    principal, runtime = _runtime(wren, schema)
    context = ContextProviderV0().build(wren, runtime)

    persisted = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted.append(row),
    )
    contract_store = contracts_module.ContractStore()

    trace_ref = {"current": None}
    install_standard_eval_trace(monkeypatch, harness, trace_ref)

    records = []
    failed_ids = []
    try:
        for index, case in enumerate(cases, start=1):
            before = len(persisted)
            turn_id = f"si-focused-live-turn-{index}"
            trace = new_case_trace(case)
            trace_ref["current"] = trace

            try:
                outcome = harness.run(
                    question=case["question"],
                    turn_id=turn_id,
                    request_ref=f"si-focused-live-request-{index}",
                    semantic_context=context,
                    schema=schema,
                    conversation=ConversationStateV2(),
                    tenant_binding="id:si-focused-live-tenant",
                    principal=principal,
                    service=wren,
                    tenant_runtime=runtime,
                    contract_store=contract_store,
                    session_id="d65-si-focused-live",
                )
                after = len(persisted)
                mismatches = _mismatches(
                    case,
                    outcome,
                    before=before,
                    after=after,
                    authority_registry=harness.authority_registry,
                    turn_id=turn_id,
                )
                trace.update(
                    {
                        "final_status": outcome.status.value,
                        "reasons": list(outcome.reasons),
                        "authority_id": (
                            outcome.authority.authority_id
                            if outcome.authority
                            else None
                        ),
                        "query_count": (
                            outcome.execution.query_count
                            if outcome.execution
                            else 0
                        ),
                        "mismatches": mismatches,
                    }
                )
            except Exception as exc:
                after = len(persisted)
                trace.update(
                    {
                        "final_status": "EXCEPTION",
                        "reasons": [],
                        "authority_id": None,
                        "query_count": max(0, after - before),
                        "mismatches": [
                            f"unexpected {type(exc).__name__}: {exc}"
                        ],
                        "exception": f"{type(exc).__name__}: {exc}",
                    }
                )

            if trace["mismatches"]:
                failed_ids.append(case["id"])
            records.append(trace)
            trace_ref["current"] = None
    finally:
        trace_ref["current"] = None
        payload = {
            "kind": "d65_si_focused_live_001_005",
            "source_corpus_version": corpus["version"],
            "selected_case_ids": list(SELECTED),
            "workers": 1,
            "telemetry": telemetry,
            "records": records,
            "failed_case_ids": failed_ids,
            "query_contract_rows": len(persisted),
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    assert len(records) == 2
    assert not failed_ids, (
        "focused live failures: "
        + ", ".join(failed_ids)
        + "; inspect uploaded JSON report"
    )
