from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

import httpx
import pytest

from app.v3.authority import AcceptedResearchAuthority
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.research import (
    EvidenceRelation,
    HypothesisState,
    ResearchBudget,
    ResearchManager,
    ObligationState,
    ResearchStateError,
    StoppingStatus,
)
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity


NOW = datetime(2026, 9, 24, 20, 0, tzinfo=timezone.utc)
ENGINE_SHA = "cbe313af9ac2d5960f662068e433d328d896fb06"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
RUNTIME_TAG = "v0.63.18-dima.6"
TENANT = "tenant-boyahane"
PRINCIPAL = "analyst-p14"
CONTEXT = "ctx-p14-v1"


def _authority(*obligation_ids: str) -> AcceptedResearchAuthority:
    return AcceptedResearchAuthority(
        contract_id="research-contract-p14-1",
        lineage_id="research-lineage-p14-1",
        version=1,
        turn_id="turn-p14-1",
        request_ref="request:p14:1",
        source_message_hash=hashlib.sha256(b"p14 research request").hexdigest(),
        accepted_attempt_id="attempt-p14-1",
        model_role="research-manager",
        obligation_ids=obligation_ids,
        context_version=CONTEXT,
        accepted_at_iso=NOW.isoformat(),
    )


def _session(*obligation_ids: str):
    authority = _authority(*obligation_ids)
    return ResearchManager.start(
        authority=authority,
        objective="Satış performansındaki değişimi kanıtlarla araştır.",
        obligation_objectives={
            item: f"Investigate accepted obligation {item} using native analytics."
            for item in obligation_ids
        },
        tenant_binding=TENANT,
        principal_subject=PRINCIPAL,
        budget=ResearchBudget(max_native_turns=4, max_material_executions=4),
        now=NOW,
        session_id="rs_" + "1" * 24,
    )


def _receipt(obligation_id: str) -> DimaQueryReceipt:
    return DimaQueryReceipt(
        receipt_id="dqr_" + "2" * 24,
        receipt_fingerprint="3" * 64,
        execution_id="exec-p14-1",
        step_role="primary",
        authority_id="asa_" + "4" * 24,
        obligation_ids=(obligation_id,),
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        semantic_refs=("sem_sales_order_count",),
        projection_hash="5" * 64,
        resolved_intent_hash="6" * 64,
        canonical_query_fingerprint="7" * 64,
        canonical_query_representation={"lib/type": "mbql/query", "stages": []},
        principal_fingerprint="8" * 64,
        execution_access_fingerprint="9" * 64,
        access_attestation_refs=("attestation:p14:1",),
        semantic_context_version=CONTEXT,
        resource_entity_ids=("boyahane:satis_siparisleri",),
        resource_fingerprints=("a" * 64,),
        substrate="metabase-native",
        substrate_runtime_version=RUNTIME_TAG,
        substrate_image_digest="sha256:" + "b" * 64,
        engine_repository="UpcyTech/dima-metabase-engine",
        engine_revision_sha=ENGINE_SHA,
        engine_upstream_base_sha=UPSTREAM_SHA,
        engine_runtime_tag=RUNTIME_TAG,
        engine_build_identity=f"github-actions:36042062775:{ENGINE_SHA}",
        engine_image_identity="ghcr.io/upcytech/dima-metabase-engine@sha256:" + "b" * 64,
        engine_runtime_instance_id=UUID("00000000-0000-4000-8000-000000000214"),
        database_id="metabase:1",
        executed_at=NOW,
        result_hash="c" * 64,
        row_count=1,
    )


def _evidence(obligation_id: str, *, state: EvidenceState = EvidenceState.VERIFIED):
    receipt = _receipt(obligation_id)
    return receipt, EvidenceArtifact(
        artifact_id="evi_" + "d" * 24,
        authority_id=receipt.authority_id,
        obligation_ids=(obligation_id,),
        query_receipt_refs=(receipt.receipt_id,),
        evidence_kind="p14_native_research",
        state=state,
        payload={"claim": "native receipted result"},
    )


def test_p14_durable_state_delegates_objective_to_real_native_bridge_without_query_planner():
    session = _session("obl-p14-1")
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="obl-p14-1",
        now=NOW,
    )

    assert prepared.request.message == session.obligations[0].objective
    assert prepared.request.context == {}
    assert prepared.request.state == {}
    assert prepared.session.obligations[0].state == ObligationState.DELEGATED
    assert prepared.session.budget.native_turns_used == 1
    assert prepared.session.native_conversation is not None

    checkpoint = ResearchManager.checkpoint(prepared.session)
    restored = ResearchManager.restore_checkpoint(checkpoint.model_dump_json())
    assert restored == prepared.session
    assert restored.fingerprint == checkpoint.fingerprint

    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path == "/api/session/properties":
            return httpx.Response(200, json={"version": {"tag": RUNTIME_TAG}})
        if request.method == "POST" and request.url.path == "/api/metabot/agent-streaming":
            captured.update(json.loads(request.content.decode("utf-8")))
            return httpx.Response(
                202,
                text=(
                    '0:"delegated"\n'
                    '2:{"type":"state","value":{"status":"done"}}\n'
                    'd:{"finishReason":"stop"}\n'
                ),
            )
        raise AssertionError(f"unexpected native request: {request.method} {request.url.path}")

    engine = NativeEngineIdentity(
        engine_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=RUNTIME_TAG,
    )
    with NativeEngineBridge(
        base_url="http://native.test",
        session_token="restricted-session",
        expected_identity=engine,
        transport=httpx.MockTransport(handler),
    ) as bridge:
        observation = ResearchManager.invoke_native(prepared, bridge=bridge)

    assert observation.status_code == 202
    assert not observation.errors
    assert captured["message"] == session.obligations[0].objective
    assert captured["context"] == {}
    assert captured["state"] == {}
    assert "query" not in captured
    assert "sql" not in captured
    assert "mbql" not in captured


def test_verified_receipted_evidence_updates_obligation_hypothesis_and_stopping_state():
    session = _session("obl-p14-1")
    session = ResearchManager.add_hypothesis(
        session,
        statement="Kanal karması sipariş değişimini açıklıyor olabilir.",
        obligation_ids=("obl-p14-1",),
        now=NOW,
    )
    hypothesis_id = session.hypotheses[0].hypothesis_id
    receipt, evidence = _evidence("obl-p14-1")

    updated = ResearchManager.admit_receipted_evidence(
        session,
        obligation_id="obl-p14-1",
        receipt=receipt,
        evidence=evidence,
        satisfies_obligation=True,
        hypothesis_id=hypothesis_id,
        relation=EvidenceRelation.SUPPORTS,
        now=NOW,
    )

    assert updated.obligations[0].state == ObligationState.VERIFIED
    assert updated.obligations[0].evidence_refs == (evidence.artifact_id,)
    assert updated.evidence_refs[0].receipt_id == receipt.receipt_id
    assert updated.evidence_refs[0].obligation_id == "obl-p14-1"
    assert updated.hypotheses[0].state == HypothesisState.SUPPORTED
    assert updated.hypotheses[0].supporting_refs == (evidence.artifact_id,)
    assert updated.budget.material_executions_used == 1
    assert updated.stopping.status == StoppingStatus.COMPLETE


def test_unverified_or_unreceipted_material_result_cannot_enter_research_epistemics():
    session = _session("obl-p14-1")
    receipt, evidence = _evidence("obl-p14-1", state=EvidenceState.EXECUTED)
    with pytest.raises(ResearchStateError) as exc:
        ResearchManager.admit_receipted_evidence(
            session,
            obligation_id="obl-p14-1",
            receipt=receipt,
            evidence=evidence,
            satisfies_obligation=True,
        )
    assert exc.value.code == "P14_EVIDENCE_NOT_VERIFIED"

    verified = evidence.model_copy(
        update={"state": EvidenceState.VERIFIED, "query_receipt_refs": ()}
    )
    with pytest.raises(ResearchStateError) as exc:
        ResearchManager.admit_receipted_evidence(
            session,
            obligation_id="obl-p14-1",
            receipt=receipt,
            evidence=verified,
            satisfies_obligation=True,
        )
    assert exc.value.code == "P14_EVIDENCE_RECEIPT_LINK_MISSING"


def test_fail_closed_limitation_does_not_block_unrelated_research_obligations():
    session = _session("obl-p14-a", "obl-p14-b")
    updated = ResearchManager.record_limitation(
        session,
        obligation_id="obl-p14-a",
        code="NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED",
        detail="exact native representation is unsupported by the current Dima compatibility seam",
        now=NOW,
    )

    states = {item.obligation_id: item.state for item in updated.obligations}
    assert states == {
        "obl-p14-a": ObligationState.LIMITED,
        "obl-p14-b": ObligationState.READY,
    }
    assert updated.stopping.status == StoppingStatus.ACTIVE
    assert len(updated.limitations) == 1
    assert updated.limitations[0].code == "NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED"


def test_counter_evidence_is_explicit_and_never_silently_promotes_a_hypothesis():
    session = _session("obl-p14-1")
    session = ResearchManager.add_hypothesis(
        session,
        statement="Kanal karması sipariş değişimini açıklıyor olabilir.",
        obligation_ids=("obl-p14-1",),
        now=NOW,
    )
    receipt, evidence = _evidence("obl-p14-1")
    hypothesis_id = session.hypotheses[0].hypothesis_id

    updated = ResearchManager.admit_receipted_evidence(
        session,
        obligation_id="obl-p14-1",
        receipt=receipt,
        evidence=evidence,
        satisfies_obligation=False,
        hypothesis_id=hypothesis_id,
        relation=EvidenceRelation.CONTRADICTS,
        now=NOW,
    )

    assert updated.hypotheses[0].state == HypothesisState.CHALLENGED
    assert updated.hypotheses[0].supporting_refs == ()
    assert updated.hypotheses[0].counter_refs == (evidence.artifact_id,)
    assert updated.counter_evidence_refs[0].hypothesis_id == hypothesis_id
    assert updated.obligations[0].state == ObligationState.DELEGATED
    assert updated.stopping.status == StoppingStatus.ACTIVE
