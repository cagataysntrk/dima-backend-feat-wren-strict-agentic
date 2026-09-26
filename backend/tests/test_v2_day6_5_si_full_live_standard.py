"""Workers=1 full-live Day6.5 Standard composition proof.

Explicitly skipped outside the one-shot SI workflow.
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
from app.v2.standard_lane import StandardLaneStatus
from control_plane.authorize import Principal
from lab.si_standard_eval import install_standard_eval_trace, new_case_trace


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_D65_SI_FULL_LIVE") != "1",
    reason="manual-only paid/live SI composition gate",
)

CORPUS = (
    Path(__file__).resolve().parents[1]
    / "eval"
    / "v2_day6_5_si_full_live_frozen.json"
)


def _runtime(wren, schema):
    principal = Principal(
        user_id="si-live-user",
        tenant_id="si-live-tenant",
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


def _validate_case(case, outcome, *, before, after, authority_registry, turn_id):
    mismatches = []
    if outcome.status.value != case["expected_status"]:
        mismatches.append(
            f"status expected={case['expected_status']} actual={outcome.status.value}"
        )

    if case["expected_status"] == "ACCEPTED":
        if outcome.authority is None:
            mismatches.append("accepted case missing authority")
        if outcome.execution is None:
            mismatches.append("accepted case missing execution")
        if after <= before:
            mismatches.append("accepted case persisted no QueryContract")

        if outcome.execution is not None:
            if outcome.execution.evidence.verified is not True:
                mismatches.append("accepted case evidence not verified")
            if not outcome.execution.query_contract_refs:
                mismatches.append("accepted case missing query_contract_refs")
            ir = outcome.execution.analytics_ir
            if ir.cube != case["expected_cube"]:
                mismatches.append(
                    f"cube expected={case['expected_cube']} actual={ir.cube}"
                )
            actual_metric = (
                ir.metrics[0].canonical_name if ir.metrics else None
            )
            if actual_metric != case["expected_metric"]:
                mismatches.append(
                    f"metric expected={case['expected_metric']} actual={actual_metric}"
                )
            actual_dimensions = [
                item.canonical_name for item in ir.dimensions
            ]
            if actual_dimensions != case["expected_dimensions"]:
                mismatches.append(
                    "dimensions expected="
                    f"{case['expected_dimensions']} actual={actual_dimensions}"
                )
            if (ir.period is not None) is not case["expected_period"]:
                mismatches.append("period presence mismatch")
            if (ir.comparison is not None) is not case["expected_comparison"]:
                mismatches.append("comparison presence mismatch")
            expected_ranking = case["expected_ranking"]
            if expected_ranking is None:
                if ir.ranking is not None:
                    mismatches.append("unexpected ranking")
            elif ir.ranking is None:
                mismatches.append("expected ranking missing")
            else:
                if ir.ranking.direction != expected_ranking["direction"]:
                    mismatches.append("ranking direction mismatch")
                if ir.ranking.limit != expected_ranking["limit"]:
                    mismatches.append("ranking limit mismatch")

        if authority_registry.accepted(turn_id) is None:
            mismatches.append("shared authority registry missing accepted turn")
    else:
        if outcome.authority is not None:
            mismatches.append("clarification case minted authority")
        if outcome.execution is not None:
            mismatches.append("clarification case executed query")
        if after != before:
            mismatches.append("clarification case persisted QueryContract")
        if authority_registry.accepted(turn_id) is not None:
            mismatches.append("clarification case committed authority")

    return mismatches


def test_workers1_full_live_standard_composition(wren, schema, monkeypatch):
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert corpus["frozen"] is True
    assert corpus["workers"] == 1
    assert len(corpus["cases"]) == 6

    get_settings.cache_clear()
    settings = get_settings()
    harness = StandardLabHarness(settings=settings)
    telemetry = harness.telemetry

    assert telemetry["standard_cognition"]["role"] == "REFERENCE_LANGUAGE"
    assert telemetry["standard_cognition"]["model"] == "openai/gpt-5.6-sol"
    assert telemetry["semantic_linker"]["role"] == "SEMANTIC_LINKER"
    assert telemetry["semantic_linker"]["model"] == "openai/gpt-5.6-luna"
    assert telemetry["temporal_normalizer"]["role"] == "TEMPORAL_NORMALIZER"
    assert telemetry["temporal_normalizer"]["model"] == "openai/gpt-5.6-sol"
    assert (
        telemetry["semantic_linker"]["model"]
        != telemetry["temporal_normalizer"]["model"]
    )

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
    report_path = (
        Path(__file__).resolve().parents[1]
        / "lab"
        / "reports"
        / "v2_day6_5_si_full_live_standard.json"
    )

    try:
        for index, case in enumerate(corpus["cases"], start=1):
            before = len(persisted)
            turn_id = f"si-live-turn-{index}"
            trace = new_case_trace(case)
            trace_ref["current"] = trace

            try:
                outcome = harness.run(
                    question=case["question"],
                    turn_id=turn_id,
                    request_ref=f"si-live-request-{index}",
                    semantic_context=context,
                    schema=schema,
                    conversation=ConversationStateV2(),
                    tenant_binding="id:si-live-tenant",
                    principal=principal,
                    service=wren,
                    tenant_runtime=runtime,
                    contract_store=contract_store,
                    session_id="d65-si-full-live",
                )
                after = len(persisted)
                mismatches = _validate_case(
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
                        "material_gaps": [
                            reason
                            for reason in outcome.reasons
                            if "semantic" in reason.lower()
                            or "missing" in reason.lower()
                            or "unresolved" in reason.lower()
                        ],
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
                        "material_gaps": [],
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
        report = {
            "kind": "d65_si_full_live_standard_composition",
            "corpus_version": corpus["version"],
            "workers": 1,
            "telemetry": telemetry,
            "records": records,
            "completed_cases": len(records),
            "failed_case_ids": failed_ids,
            "accepted": sum(
                r.get("final_status") == "ACCEPTED" for r in records
            ),
            "clarified": sum(
                r.get("final_status") == "CLARIFICATION_REQUIRED"
                for r in records
            ),
            "query_contract_rows": len(persisted),
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    assert len(records) == len(corpus["cases"])
    assert not failed_ids, (
        "full-live Standard failures: "
        + ", ".join(failed_ids)
        + "; inspect uploaded JSON report"
    )
