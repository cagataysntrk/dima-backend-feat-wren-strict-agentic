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


# Integrated P14 proof: do not fake Dima trust/receipt ownership.
from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedPeriod,
    ResolvedSemanticRef,
)
from app.v3.execution_identity import (
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    RuntimeIdentity,
)
from app.v3.native_execution import NativeCandidateOutcome
from app.v3.native_standard.contracts import NativeAttestationEnvelope
from app.v3.native_standard.trust import NativeStandardTrustOrchestrator
from app.v3.security_identity import VerifiedExecutionSecurityFacts
from app.v3.semantic_spec import (
    DimensionSpec,
    DimaSemanticSpec,
    MetricSpec,
    SourceLineage,
    TimeSpec,
)
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    TemporalSemanticBinding,
)
from control_plane.authorize import Principal


P14_TABLE = "boyahane:satis_siparisleri"
P14_TIME = "boyahane:satis_siparisleri.acilis_tarihi"
P14_CHANNEL = "boyahane:satis_siparisleri.kanal"
P14_NATIVE_USER = "user-p14-native"
P14_NATIVE_CONTEXT = "ctx-p14-native-v1"
P14_NATIVE_OBLIGATION = "obl-p14-native"
P14_RUNTIME_INSTANCE = "00000000-0000-4000-8000-000000000314"
P14_IMAGE_IDENTITY = "sha256:" + "e" * 64


def _native_hash(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _native_snapshot() -> DimaExecutionBindingSnapshot:
    table = SourceLineage(
        source_id="source.satis_siparisleri",
        database_ref="boyahane",
        schema_name="main",
        table_name="satis_siparisleri",
    )
    opened = SourceLineage(
        source_id="source.satis_siparisleri.acilis_tarihi",
        database_ref="boyahane",
        schema_name="main",
        table_name="satis_siparisleri",
        column_name="acilis_tarihi",
    )
    channel = SourceLineage(
        source_id="source.satis_siparisleri.kanal",
        database_ref="boyahane",
        schema_name="main",
        table_name="satis_siparisleri",
        column_name="kanal",
    )
    spec = DimaSemanticSpec(
        semantic_context_version=P14_NATIVE_CONTEXT,
        metrics=(
            MetricSpec(
                metric_id="metric.sales_order_count",
                name="Sales Order Count",
                aggregation="count",
                semantic_version="1",
                compatibility_hash="a" * 64,
                source_lineage=(table,),
            ),
        ),
        dimensions=(
            DimensionSpec(
                dimension_id="dimension.sales_order_opened_at",
                name="Sales Order Opened At",
                data_type="datetime",
                semantic_version="1",
                source_lineage=(opened,),
            ),
            DimensionSpec(
                dimension_id="dimension.sales_order_channel",
                name="Sales Order Channel",
                data_type="string",
                semantic_version="1",
                source_lineage=(channel,),
            ),
        ),
        time_specs=(
            TimeSpec(
                time_id="time.sales_order_opened_at",
                dimension_ref="dimension.sales_order_opened_at",
                grain="day",
            ),
        ),
    )
    return DimaExecutionBindingSnapshot(
        semantic_context_version=P14_NATIVE_CONTEXT,
        semantic_spec=spec,
        candidate_bindings=(
            CandidateSemanticBinding(
                candidate_id="cand_sales_order_count",
                semantic_id="metric.sales_order_count",
                kind="metric",
            ),
            CandidateSemanticBinding(
                candidate_id="cand_sales_order_channel",
                semantic_id="dimension.sales_order_channel",
                kind="dimension",
            ),
        ),
        temporal_bindings=(
            TemporalSemanticBinding(
                compatibility_key="sales_orders.opened_at",
                dimension_id="dimension.sales_order_opened_at",
            ),
        ),
        current_catalog=CurrentCatalogSnapshot(
            catalog_version="boyahane-p14-v1",
            objects=(
                CurrentCatalogObject(
                    source_id=table.source_id,
                    database_ref="boyahane",
                    schema_name="main",
                    table_name="satis_siparisleri",
                    resource_entity_id=P14_TABLE,
                    resource_fingerprint="1" * 64,
                    metabase_database_id=1,
                    metabase_table_id=10,
                ),
                CurrentCatalogObject(
                    source_id=opened.source_id,
                    database_ref="boyahane",
                    schema_name="main",
                    table_name="satis_siparisleri",
                    column_name="acilis_tarihi",
                    resource_entity_id=P14_TIME,
                    resource_fingerprint="2" * 64,
                    metabase_database_id=1,
                    metabase_table_id=10,
                    metabase_field_id=11,
                ),
                CurrentCatalogObject(
                    source_id=channel.source_id,
                    database_ref="boyahane",
                    schema_name="main",
                    table_name="satis_siparisleri",
                    column_name="kanal",
                    resource_entity_id=P14_CHANNEL,
                    resource_fingerprint="3" * 64,
                    metabase_database_id=1,
                    metabase_table_id=10,
                    metabase_field_id=13,
                ),
            ),
        ),
    )


def _native_intent(authority_id: str) -> ResolvedAnalyticsIntent:
    return ResolvedAnalyticsIntent(
        authority_id=authority_id,
        request_ref="request:p14:native",
        source_message_hash="4" * 64,
        projection_hash="6" * 64,
        semantic_context_version=P14_NATIVE_CONTEXT,
        obligation_ids=(P14_NATIVE_OBLIGATION,),
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_count",
                source_candidate_id="cand_sales_order_count",
                kind="metric",
                canonical_name="Sales Order Count",
                source_scopes=("satis_siparisleri",),
            ),
        ),
        dimensions=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_channel",
                source_candidate_id="cand_sales_order_channel",
                kind="dimension",
                canonical_name="Sales Order Channel",
                source_scopes=("satis_siparisleri",),
            ),
        ),
        period=ResolvedPeriod(
            kind="absolute",
            source_text="Haziran 2026",
            time_dimension="sales_orders.opened_at",
            start="2026-06-01",
            end="2026-07-01",
        ),
        principal=PrincipalContextRef(
            tenant_binding=TENANT,
            principal_subject=P14_NATIVE_USER,
            roles=("analyst",),
        ),
    )


def _native_query() -> dict:
    return {
        "lib/type": "mbql/query",
        "database": 1,
        "stages": [
            {
                "lib/type": "mbql.stage/mbql",
                "source-table": 10,
                "aggregation": [
                    [
                        "count",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000401"},
                    ]
                ],
                "breakout": [
                    [
                        "field",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000402"},
                        13,
                    ]
                ],
                "filters": [
                    [
                        ">=",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000403"},
                        [
                            "field",
                            {"lib/uuid": "00000000-0000-4000-8000-000000000404"},
                            11,
                        ],
                        "2026-06-01",
                    ],
                    [
                        "<",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000405"},
                        [
                            "field",
                            {"lib/uuid": "00000000-0000-4000-8000-000000000406"},
                            11,
                        ],
                        "2026-07-01",
                    ],
                ],
            }
        ],
    }


def _native_attestation() -> NativeAttestationEnvelope:
    query = _native_query()
    return NativeAttestationEnvelope(
        exact_serialized_pmbql=query,
        manifest={
            "attestation_id": "dima_att_" + "f" * 24,
            "native_conversation_id": "00000000-0000-4000-8000-000000000331",
            "native_assistant_message_id": 301,
            "native_tool_call_id": "call-p14",
            "native_query_id": "native-p14",
            "producer_tool": "construct_notebook_query",
            "exact_pmbql_fingerprint": _native_hash(query),
            "database_id": 1,
            "primary_source_table_id": 10,
            "referenced_source_table_ids": (10,),
            "aggregation_count": 1,
            "aggregations": (
                {
                    "operator": "count",
                    "argument_kind": "all_rows",
                    "referenced_field_ids": (),
                    "distinct": False,
                },
            ),
            "native_metric_references": (),
            "breakout_count": 1,
            "breakouts": (
                {
                    "stage_number": 0,
                    "breakout_index": 0,
                    "field_id": 13,
                    "field_type": "type/Text",
                    "temporal_unit": None,
                },
            ),
            "material_filter_count": 2,
            "non_temporal_filter_count": 0,
            "temporal_predicates": (
                {
                    "time_field_id": 11,
                    "operator": ">=",
                    "lower_bound": "2026-06-01",
                    "upper_bound": None,
                    "lower_inclusive": True,
                    "upper_inclusive": None,
                    "field_temporal_type": "type/DateTime",
                    "temporal_unit": None,
                },
                {
                    "time_field_id": 11,
                    "operator": "<",
                    "lower_bound": None,
                    "upper_bound": "2026-07-01",
                    "lower_inclusive": None,
                    "upper_inclusive": False,
                    "field_temporal_type": "type/DateTime",
                    "temporal_unit": None,
                },
            ),
            "textual_equality_predicates": (),
            "explicit_join_count": 0,
            "implicit_join_count": 0,
            "implicit_joined_table_ids": (),
            "order_by_count": 0,
            "order_bys": (),
            "limit": None,
            "stage_count": 1,
            "material_query_count": 1,
            "authenticated_metabase_subject": 42,
            "validation_provenance": {
                "producer_structured_output": "PASSED",
                "pmbql_schema": "PASSED",
                "producer_query_id_match": "PASSED",
                "producer_state_match": "PASSED",
            },
            "permission_provenance": {
                "current_metabase_user_id": 42,
                "permission_check": "PASSED",
                "checked_source_table_ids": (10,),
            },
            "runtime_identity": {
                "repository": "UpcyTech/dima-metabase-engine",
                "revision_sha": ENGINE_SHA,
                "upstream_base_sha": UPSTREAM_SHA,
                "runtime_tag": RUNTIME_TAG,
                "build_identity": "github-actions:test:" + ENGINE_SHA,
                "image_identity": P14_IMAGE_IDENTITY,
                "runtime_instance_id": P14_RUNTIME_INSTANCE,
            },
        },
    )


def _native_engine() -> NativeEngineIdentity:
    return NativeEngineIdentity(
        repository="UpcyTech/dima-metabase-engine",
        engine_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=RUNTIME_TAG,
        build_identity="github-actions:test:" + ENGINE_SHA,
        runtime_image_identity=P14_IMAGE_IDENTITY,
        runtime_instance_id=P14_RUNTIME_INSTANCE,
    )


def _native_security(attestation: NativeAttestationEnvelope) -> VerifiedExecutionSecurityFacts:
    return VerifiedExecutionSecurityFacts(
        tenant_binding=TENANT,
        principal_subject=P14_NATIVE_USER,
        roles=("analyst",),
        attribute_policy_digest="9" * 64,
        policy_version="policy-p14-v1",
        rls_versions=(),
        cls_versions=(),
        database_route="analytics-primary",
        database_destination="boyahane",
        impersonation_role=None,
        semantic_context_version=P14_NATIVE_CONTEXT,
        source_object_refs=(P14_TABLE, P14_TIME, P14_CHANNEL),
        security_parameter_digest="a" * 64,
        metabase_subject_ref="metabase-user:42",
        attestation_refs=(attestation.manifest.attestation_id,),
        evidence_refs=("evidence:metabase-session:p14",),
    )


def _native_research_session() -> tuple[ResearchManager, object]:
    authority = AcceptedResearchAuthority(
        contract_id="research-contract-p14-native",
        lineage_id="research-lineage-p14-native",
        version=1,
        turn_id="turn-p14-native",
        request_ref="request:p14:native",
        source_message_hash="4" * 64,
        accepted_attempt_id="attempt-p14-native",
        model_role="research-manager",
        obligation_ids=(P14_NATIVE_OBLIGATION,),
        context_version=P14_NATIVE_CONTEXT,
        accepted_at_iso=NOW.isoformat(),
    )
    session = ResearchManager.start(
        authority=authority,
        objective="Haziran satış siparişlerini kanala göre araştır.",
        obligation_objectives={
            P14_NATIVE_OBLIGATION: "Haziran satış siparişlerini kanala göre incele."
        },
        tenant_binding=TENANT,
        principal_subject=P14_NATIVE_USER,
        now=NOW,
        session_id="rs_" + "7" * 24,
    )
    return ResearchManager, session


def test_p14_vertical_reuses_p13_exact_occurrence_p10_p5_and_evidence_without_second_authority():
    _, session = _native_research_session()
    attestation = _native_attestation()
    intent = _native_intent("asa-p14-native")
    principal = Principal(
        user_id=P14_NATIVE_USER,
        tenant_id=TENANT,
        tenant_slug=TENANT,
        roles=["analyst"],
    )
    authz = NativeStandardTrustOrchestrator.authorize(
        intent=intent,
        snapshot=_native_snapshot(),
        attestation=attestation,
        expected_engine=_native_engine(),
        current_principal=principal,
        verified_security_facts=_native_security(attestation),
        dima_request_id="dima-req-p14-native",
        dima_trace_id="dima-trace-p14-native",
    )
    assert authz.authorization.outcome == NativeCandidateOutcome.ALLOW
    assert authz.access_snapshot is not None

    execution_request = NativeStandardTrustOrchestrator.execution_request(
        result=authz,
        attestation=attestation,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/dima/engine/v1/native-query-execution"
        body = json.loads(request.content.decode("utf-8"))
        assert body == {
            "conversation_id": str(execution_request.native_conversation_id),
            "native_query_id": execution_request.native_query_id,
            "expected_pmbql_fingerprint": execution_request.expected_pmbql_fingerprint,
            "expected_attestation_id": execution_request.expected_attestation_id,
        }
        return httpx.Response(
            200,
            json={
                "native_conversation_id": str(execution_request.native_conversation_id),
                "native_query_id": execution_request.native_query_id,
                "attestation_id": execution_request.expected_attestation_id,
                "executed_pmbql_fingerprint": (
                    execution_request.expected_pmbql_fingerprint
                ),
                "runtime_identity": attestation.manifest.runtime_identity.model_dump(
                    mode="json"
                ),
                "result": {
                    "data": {
                        "rows": [["Web", 27], ["Mevcut Müşteri", 34]],
                    }
                },
                "attestation": attestation.model_dump(mode="json"),
            },
        )

    with NativeEngineBridge(
        base_url="http://native.test",
        session_token="restricted-session",
        expected_identity=_native_engine(),
        transport=httpx.MockTransport(handler),
    ) as bridge:
        execution = bridge.execute_native_query(
            conversation_id=execution_request.native_conversation_id,
            native_query_id=execution_request.native_query_id,
            expected_pmbql_fingerprint=execution_request.expected_pmbql_fingerprint,
            expected_attestation_id=execution_request.expected_attestation_id,
        )

    receipt = NativeStandardTrustOrchestrator.seal_receipt(
        intent=intent,
        result=authz,
        execution_request=execution_request,
        attestation=attestation,
        executed_pmbql_fingerprint=execution.executed_pmbql_fingerprint,
        executed_attestation_id=execution.attestation_id,
        runtime=RuntimeIdentity(
            substrate="metabase-native",
            runtime_version=RUNTIME_TAG,
            image_digest="sha256:" + "e" * 64,
            database_id="metabase:1",
            repository="UpcyTech/dima-metabase-engine",
            revision_sha=ENGINE_SHA,
            upstream_base_sha=UPSTREAM_SHA,
            runtime_tag=RUNTIME_TAG,
            build_identity="github-actions:test:" + ENGINE_SHA,
            image_identity=P14_IMAGE_IDENTITY,
            runtime_instance_id=UUID(P14_RUNTIME_INSTANCE),
        ),
        execution_result=ExecutionResultSnapshot(
            payload=execution.payload,
            row_count=2,
        ),
        execution_event=ExecutionEventIdentity(
            execution_id="exec-p14-native-1",
            executed_at=NOW,
        ),
    )
    assert receipt.execution_access_fingerprint == (
        authz.access_snapshot.execution_access_fingerprint
    )
    assert receipt.canonical_query_fingerprint == (
        execution.executed_pmbql_fingerprint
    )

    evidence = EvidenceArtifact(
        artifact_id="evi_" + "1" * 24,
        authority_id=receipt.authority_id,
        obligation_ids=(P14_NATIVE_OBLIGATION,),
        query_receipt_refs=(receipt.receipt_id,),
        evidence_kind="p14_native_exact_occurrence",
        state=EvidenceState.VERIFIED,
        payload={"native_result": execution.payload},
    )
    updated = ResearchManager.admit_receipted_evidence(
        session,
        obligation_id=P14_NATIVE_OBLIGATION,
        receipt=receipt,
        evidence=evidence,
        satisfies_obligation=True,
        now=NOW,
    )

    assert updated.obligations[0].state == ObligationState.VERIFIED
    assert updated.evidence_refs[0].receipt_id == receipt.receipt_id
    assert updated.stopping.status == StoppingStatus.COMPLETE
    assert receipt.substrate == "metabase-native"
    assert receipt.engine_revision_sha == ENGINE_SHA
