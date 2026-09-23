from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import pytest

from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedPeriod,
    ResolvedSemanticRef,
)
from app.v3.execution_identity import (
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    ReceiptSealError,
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
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal


ENGINE_SHA = "3ac50a0ad1c2fb53d538c9fccf621db816c305e1"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
RUNTIME_TAG = "v0.63.18-dima.1"
INSTANCE_ID = "00000000-0000-4000-8000-000000000131"
IMAGE_ID = "ghcr.io/upcytech/dima-metabase-engine@" + "sha256:" + "7" * 64
TABLE_RESOURCE = "boyahane:satis_siparisleri"
TIME_RESOURCE = "boyahane:satis_siparisleri.acilis_tarihi"


def _hash(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _snapshot() -> DimaExecutionBindingSnapshot:
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
    closed = SourceLineage(
        source_id="source.satis_siparisleri.kapanis_tarihi",
        database_ref="boyahane",
        schema_name="main",
        table_name="satis_siparisleri",
        column_name="kapanis_tarihi",
    )
    complaints = SourceLineage(
        source_id="source.musteri_sikayetleri",
        database_ref="boyahane",
        schema_name="main",
        table_name="musteri_sikayetleri",
    )
    spec = DimaSemanticSpec(
        semantic_context_version="ctx-px01-v1",
        metrics=(
            MetricSpec(
                metric_id="metric.sales_order_count",
                name="Sales Order Count",
                aggregation="count",
                semantic_version="1",
                compatibility_hash="a" * 64,
                source_lineage=(table,),
            ),
            MetricSpec(
                metric_id="metric.complaint_count",
                name="Complaint Count",
                aggregation="count",
                semantic_version="1",
                compatibility_hash="b" * 64,
                source_lineage=(complaints,),
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
                dimension_id="dimension.sales_order_closed_at",
                name="Sales Order Closed At",
                data_type="datetime",
                semantic_version="1",
                source_lineage=(closed,),
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
    catalog = CurrentCatalogSnapshot(
        catalog_version="boyahane-px01-v1",
        objects=(
            CurrentCatalogObject(
                source_id=table.source_id,
                database_ref="boyahane",
                schema_name="main",
                table_name="satis_siparisleri",
                resource_entity_id=TABLE_RESOURCE,
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
                resource_entity_id=TIME_RESOURCE,
                resource_fingerprint="2" * 64,
                metabase_database_id=1,
                metabase_table_id=10,
                metabase_field_id=11,
            ),
            CurrentCatalogObject(
                source_id=closed.source_id,
                database_ref="boyahane",
                schema_name="main",
                table_name="satis_siparisleri",
                column_name="kapanis_tarihi",
                resource_entity_id="boyahane:satis_siparisleri.kapanis_tarihi",
                resource_fingerprint="3" * 64,
                metabase_database_id=1,
                metabase_table_id=10,
                metabase_field_id=12,
            ),
            CurrentCatalogObject(
                source_id=complaints.source_id,
                database_ref="boyahane",
                schema_name="main",
                table_name="musteri_sikayetleri",
                resource_entity_id="boyahane:musteri_sikayetleri",
                resource_fingerprint="4" * 64,
                metabase_database_id=1,
                metabase_table_id=20,
            ),
        ),
    )
    return DimaExecutionBindingSnapshot(
        semantic_context_version="ctx-px01-v1",
        semantic_spec=spec,
        candidate_bindings=(
            CandidateSemanticBinding(
                candidate_id="cand_sales_order_count",
                semantic_id="metric.sales_order_count",
                kind="metric",
            ),
        ),
        temporal_bindings=(
            TemporalSemanticBinding(
                compatibility_key="sales_orders.opened_at",
                dimension_id="dimension.sales_order_opened_at",
            ),
        ),
        current_catalog=catalog,
    )


def _intent() -> ResolvedAnalyticsIntent:
    return ResolvedAnalyticsIntent(
        authority_id="auth-px01",
        request_ref="req-px01",
        source_message_hash="5" * 64,
        projection_hash="6" * 64,
        semantic_context_version="ctx-px01-v1",
        obligation_ids=("obl-px01",),
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_count",
                source_candidate_id="cand_sales_order_count",
                kind="metric",
                canonical_name="Sales Order Count",
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
            tenant_binding="tenant-boyahane",
            principal_subject="user-px01",
            roles=("analyst",),
        ),
    )


def _engine() -> NativeEngineIdentity:
    return NativeEngineIdentity(
        repository="UpcyTech/dima-metabase-engine",
        engine_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=RUNTIME_TAG,
        build_identity="github-actions:final:" + ENGINE_SHA,
        runtime_image_identity=IMAGE_ID,
        runtime_instance_id=INSTANCE_ID,
    )


def _query() -> dict:
    return {
        "lib/type": "mbql/query",
        "database": 1,
        "stages": [
            {
                "lib/type": "mbql.stage/mbql",
                "source-table": 10,
                "aggregation": [
                    ["count", {"lib/uuid": "00000000-0000-4000-8000-000000000001"}]
                ],
                "filters": [
                    [
                        ">=",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000002"},
                        ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000003"}, 11],
                        "2026-06-01",
                    ],
                    [
                        "<",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000004"},
                        ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000005"}, 11],
                        "2026-07-01",
                    ],
                ],
            }
        ],
    }


def _manifest(**updates) -> dict:
    values = {
        "attestation_id": "dima_att_" + "1" * 24,
        "native_conversation_id": "00000000-0000-4000-8000-000000000101",
        "native_assistant_message_id": 91,
        "native_tool_call_id": "call-px01",
        "native_query_id": "native-px01",
        "producer_tool": "construct_notebook_query",
        "exact_pmbql_fingerprint": _hash(_query()),
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
        "breakout_count": 0,
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
        "explicit_join_count": 0,
        "implicit_join_count": 0,
        "implicit_joined_table_ids": (),
        "order_by_count": 0,
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
            "build_identity": "github-actions:final:" + ENGINE_SHA,
            "image_identity": IMAGE_ID,
            "runtime_instance_id": INSTANCE_ID,
        },
    }
    values.update(updates)
    return values


def _attestation(**updates) -> NativeAttestationEnvelope:
    return NativeAttestationEnvelope(
        exact_serialized_pmbql=_query(),
        manifest=_manifest(**updates),
    )


def _principal() -> Principal:
    return Principal(
        user_id="user-px01",
        tenant_id="tenant-boyahane",
        tenant_slug="tenant-boyahane",
        roles=["analyst"],
    )


def _security(attestation: NativeAttestationEnvelope) -> VerifiedExecutionSecurityFacts:
    return VerifiedExecutionSecurityFacts(
        tenant_binding="tenant-boyahane",
        principal_subject="user-px01",
        roles=("analyst",),
        attribute_policy_digest="9" * 64,
        policy_version="policy-v1",
        rls_versions=(),
        cls_versions=(),
        database_route="analytics-primary",
        database_destination="boyahane",
        impersonation_role=None,
        semantic_context_version="ctx-px01-v1",
        source_object_refs=(TABLE_RESOURCE, TIME_RESOURCE),
        security_parameter_digest="a" * 64,
        metabase_subject_ref="metabase-user:42",
        attestation_refs=(attestation.manifest.attestation_id,),
        evidence_refs=("evidence:metabase-session:px01",),
    )


def _authorize(attestation: NativeAttestationEnvelope | None = None):
    attestation = attestation or _attestation()
    return NativeStandardTrustOrchestrator.authorize(
        intent=_intent(),
        snapshot=_snapshot(),
        attestation=attestation,
        expected_engine=_engine(),
        current_principal=_principal(),
        verified_security_facts=_security(attestation),
        dima_request_id="dima-req-px01",
        dima_trace_id="dima-trace-px01",
    )


def test_px01_exact_manifest_authorizes_and_issues_existing_p10_snapshot():
    result = _authorize()
    assert result.authorization.outcome == NativeCandidateOutcome.ALLOW
    artifact = result.authorization.authorized_artifact
    assert artifact is not None
    assert artifact.engine_identity.revision_sha == ENGINE_SHA
    assert str(artifact.engine_identity.runtime_instance_id) == INSTANCE_ID
    assert artifact.resource_entity_ids == (TABLE_RESOURCE, TIME_RESOURCE)
    assert result.access_snapshot is not None
    assert result.access_snapshot.source_object_refs == (TABLE_RESOURCE, TIME_RESOURCE)


@pytest.mark.parametrize(
    "attestation",
    [
        _attestation(
            aggregations=(
                {
                    "operator": "count",
                    "argument_kind": "field",
                    "referenced_field_ids": (11,),
                    "distinct": False,
                },
            )
        ),
        _attestation(
            primary_source_table_id=20,
            referenced_source_table_ids=(20,),
            permission_provenance={
                "current_metabase_user_id": 42,
                "permission_check": "PASSED",
                "checked_source_table_ids": (20,),
            },
        ),
        _attestation(
            temporal_predicates=(
                {
                    "time_field_id": 12,
                    "operator": ">=",
                    "lower_bound": "2026-06-01",
                    "upper_bound": None,
                    "lower_inclusive": True,
                    "upper_inclusive": None,
                    "field_temporal_type": "type/DateTime",
                    "temporal_unit": None,
                },
                {
                    "time_field_id": 12,
                    "operator": "<",
                    "lower_bound": None,
                    "upper_bound": "2026-07-01",
                    "lower_inclusive": None,
                    "upper_inclusive": False,
                    "field_temporal_type": "type/DateTime",
                    "temporal_unit": None,
                },
            ),
        ),
        _attestation(
            temporal_predicates=(
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
                    "upper_bound": "2026-08-01",
                    "lower_inclusive": None,
                    "upper_inclusive": False,
                    "field_temporal_type": "type/DateTime",
                    "temporal_unit": None,
                },
            ),
        ),
        _attestation(material_filter_count=3, non_temporal_filter_count=1),
        _attestation(explicit_join_count=1),
        _attestation(implicit_join_count=1, implicit_joined_table_ids=(20,)),
        _attestation(material_query_count=2),
    ],
)
def test_px01_negative_observed_facts_block_without_model_calls(attestation):
    result = _authorize(attestation)
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.authorized_artifact is None
    assert result.access_snapshot is None


def test_exact_attested_authorized_execution_and_receipt_artifact_are_identical():
    attestation = _attestation()
    result = _authorize(attestation)
    request = NativeStandardTrustOrchestrator.execution_request(
        result=result,
        attestation=attestation,
    )
    artifact = result.authorization.authorized_artifact
    assert artifact is not None
    assert request.exact_serialized_pmbql == attestation.exact_serialized_pmbql
    assert request.artifact_fingerprint == attestation.manifest.exact_pmbql_fingerprint
    assert request.artifact_fingerprint == artifact.steps[0].artifact_fingerprint

    runtime = RuntimeIdentity(
        substrate="metabase-native",
        runtime_version=RUNTIME_TAG,
        image_digest="sha256:" + "7" * 64,
        database_id="metabase:1",
        repository="UpcyTech/dima-metabase-engine",
        revision_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=RUNTIME_TAG,
        build_identity="github-actions:final:" + ENGINE_SHA,
        image_identity=IMAGE_ID,
        runtime_instance_id=INSTANCE_ID,
    )
    receipt = NativeStandardTrustOrchestrator.seal_receipt(
        intent=_intent(),
        result=result,
        execution_request=request,
        runtime=runtime,
        execution_result=ExecutionResultSnapshot(
            payload={"rows": [[126]]},
            row_count=1,
        ),
        execution_event=ExecutionEventIdentity(
            execution_id="exec-px01",
            executed_at=datetime.now(timezone.utc),
        ),
    )
    assert receipt.canonical_query_fingerprint == request.artifact_fingerprint
    assert receipt.canonical_query_representation == request.exact_serialized_pmbql
    assert receipt.engine_revision_sha == ENGINE_SHA
    assert str(receipt.engine_runtime_instance_id) == INSTANCE_ID


def test_metabase_native_runtime_revision_mismatch_hard_fails_in_existing_p5():
    attestation = _attestation()
    result = _authorize(attestation)
    request = NativeStandardTrustOrchestrator.execution_request(
        result=result,
        attestation=attestation,
    )
    runtime = RuntimeIdentity(
        substrate="metabase-native",
        runtime_version=RUNTIME_TAG,
        image_digest="sha256:" + "7" * 64,
        database_id="metabase:1",
        repository="UpcyTech/dima-metabase-engine",
        revision_sha="f" * 40,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=RUNTIME_TAG,
        build_identity="github-actions:final:" + ENGINE_SHA,
        image_identity=IMAGE_ID,
        runtime_instance_id=INSTANCE_ID,
    )
    with pytest.raises(ReceiptSealError) as exc:
        NativeStandardTrustOrchestrator.seal_receipt(
            intent=_intent(),
            result=result,
            execution_request=request,
            runtime=runtime,
            execution_result=ExecutionResultSnapshot(
                payload={"rows": [[126]]},
                row_count=1,
            ),
            execution_event=ExecutionEventIdentity(
                execution_id="exec-px01-runtime-mismatch",
                executed_at=datetime.now(timezone.utc),
            ),
        )
    assert exc.value.code == "NATIVE_RUNTIME_REVISION_MISMATCH"


def test_engine_pin_mismatch_blocks_before_candidate_authorization():
    attestation = _attestation(
        runtime_identity={
            **_manifest()["runtime_identity"],
            "revision_sha": "e" * 40,
        }
    )
    result = _authorize(attestation)
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "NATIVE_ENGINE_PIN_MISMATCH"
    assert result.candidate is None
