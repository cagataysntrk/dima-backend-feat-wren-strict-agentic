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
    assert telemetry["semantic_linker"]["model"] != telemetry["temporal_normalizer"]["model"]

    principal, runtime = _runtime(wren, schema)
    context = ContextProviderV0().build(wren, runtime)

    persisted = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted.append(row),
    )
    contract_store = contracts_module.ContractStore()

    records = []
    for index, case in enumerate(corpus["cases"], start=1):
        before = len(persisted)
        turn_id = f"si-live-turn-{index}"
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

        record = {
            "id": case["id"],
            "family": case["family"],
            "status": outcome.status.value,
            "authority_id": (
                outcome.authority.authority_id if outcome.authority else None
            ),
            "query_count": (
                outcome.execution.query_count if outcome.execution else 0
            ),
            "reasons": list(outcome.reasons),
        }

        assert outcome.status.value == case["expected_status"], record

        if case["expected_status"] == "ACCEPTED":
            assert outcome.accepted is True, record
            assert outcome.authority is not None
            assert outcome.execution is not None
            assert outcome.execution.evidence.verified is True
            assert outcome.execution.query_contract_refs
            assert after > before

            ir = outcome.execution.analytics_ir
            assert ir.cube == case["expected_cube"], record
            assert ir.metrics[0].canonical_name == case["expected_metric"], record
            assert [d.canonical_name for d in ir.dimensions] == case["expected_dimensions"], record
            assert (ir.period is not None) is case["expected_period"], record
            assert (ir.comparison is not None) is case["expected_comparison"], record
            expected_ranking = case["expected_ranking"]
            if expected_ranking is None:
                assert ir.ranking is None, record
            else:
                assert ir.ranking is not None, record
                assert ir.ranking.direction == expected_ranking["direction"], record
                assert ir.ranking.limit == expected_ranking["limit"], record

            assert harness.authority_registry.accepted(turn_id) is not None
        else:
            assert outcome.status == StandardLaneStatus.CLARIFICATION_REQUIRED
            assert outcome.authority is None
            assert outcome.execution is None
            assert after == before
            assert harness.authority_registry.accepted(turn_id) is None

        records.append(record)

    report = {
        "kind": "d65_si_full_live_standard_composition",
        "corpus_version": corpus["version"],
        "workers": 1,
        "telemetry": telemetry,
        "records": records,
        "accepted": sum(r["status"] == "ACCEPTED" for r in records),
        "clarified": sum(
            r["status"] == "CLARIFICATION_REQUIRED" for r in records
        ),
        "query_contract_rows": len(persisted),
    }
    report_path = (
        Path(__file__).resolve().parents[1]
        / "lab"
        / "reports"
        / "v2_day6_5_si_full_live_standard.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
