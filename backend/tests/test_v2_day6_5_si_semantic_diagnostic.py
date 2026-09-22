"""One-case paid diagnostic for D65-SI-FULL-LIVE-001.

This intentionally observes only the already-failed frozen case. It does not assert a
root cause; the uploaded trace is the evidence used to classify the pre-linker failure.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from app import contracts as contracts_module
from app.config import get_settings
from app.v2.context_provider import ContextProviderV0
from app.v2.models import ConversationStateV2
from app.v2.standard_lab import StandardLabHarness
from lab.si_standard_eval import install_standard_eval_trace, new_case_trace
from tests.test_v2_day6_5_si_full_live_standard import CORPUS, _runtime


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_D65_SI_DIAGNOSTIC") != "1",
    reason="manual-only paid SI semantic diagnostic",
)


def test_same_product_semantics_diagnostic_case_001(wren, schema, monkeypatch):
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    case = next(item for item in corpus["cases"] if item["id"] == "si-live-001")

    get_settings.cache_clear()
    harness = StandardLabHarness(settings=get_settings())
    principal, runtime = _runtime(wren, schema)
    context = ContextProviderV0().build(wren, runtime)

    persisted = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted.append(row),
    )
    contract_store = contracts_module.ContractStore()

    trace_ref = {"current": new_case_trace(case)}
    install_standard_eval_trace(monkeypatch, harness, trace_ref)

    outcome = harness.run(
        question=case["question"],
        turn_id="si-diagnostic-turn-001",
        request_ref="si-diagnostic-request-001",
        semantic_context=context,
        schema=schema,
        conversation=ConversationStateV2(),
        tenant_binding="id:si-live-tenant",
        principal=principal,
        service=wren,
        tenant_runtime=runtime,
        contract_store=contract_store,
        session_id="d65-si-diagnostic",
    )
    trace = trace_ref["current"]
    trace.update(
        {
            "final_status": outcome.status.value,
            "reasons": list(outcome.reasons),
            "material_gaps": [
                reason
                for reason in outcome.reasons
                if "semantic" in reason.lower()
                or "missing" in reason.lower()
                or "unresolved" in reason.lower()
            ],
            "authority_id": (
                outcome.authority.authority_id if outcome.authority else None
            ),
            "query_count": (
                outcome.execution.query_count if outcome.execution else 0
            ),
            "role_telemetry": harness.telemetry,
        }
    )

    report_path = (
        Path(__file__).resolve().parents[1]
        / "lab"
        / "reports"
        / "v2_day6_5_si_semantic_diagnostic_001.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(trace, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # This diagnostic proves facts, not the desired product outcome.
    assert trace["draft_attempts"]
    assert trace["candidate_retrieval"]
    assert trace["semantic_selections"]
