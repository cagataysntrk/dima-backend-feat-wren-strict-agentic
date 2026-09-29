from __future__ import annotations

import hashlib
import json

import pytest

from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedSemanticRef,
)
from app.v3.entity_value_gate import CurrentLensValueEvidence
from app.v3.native_execution import NativeCandidateOutcome, NativeExecutionTrustError
from app.v3.native_standard.contracts import NativeAttestationEnvelope
from app.v3.native_standard.trust import NativeStandardTrustOrchestrator
from app.v3.security_identity import (
    ExecutionAccessSnapshotIssuer,
    VerifiedExecutionSecurityFacts,
)
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


ENGINE_SHA = "4" * 40
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
RUNTIME_TAG = "v0.63.18-dima.4"
INSTANCE_ID = "00000000-0000-4000-8000-000000000134"
IMAGE_ID = "sha256:" + "7" * 64

TABLE_RESOURCE = "boyahane:satis_siparisleri"
TIME_RESOURCE = "boyahane:satis_siparisleri.acilis_tarihi"
CHANNEL_RESOURCE = "boyahane:satis_siparisleri.kanal"


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
    channel = SourceLineage(
        source_id="source.satis_siparisleri.kanal",
        database_ref="boyahane",
        schema_name="main",
        table_name="satis_siparisleri",
        column_name="kanal",
    )
    spec = DimaSemanticSpec(
        semantic_context_version="ctx-p13c-v1",
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
    catalog = CurrentCatalogSnapshot(
        catalog_version="boyahane-p13c-v1",
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
                source_id=channel.source_id,
                database_ref="boyahane",
                schema_name="main",
                table_name="satis_siparisleri",
                column_name="kanal",
                resource_entity_id=CHANNEL_RESOURCE,
                resource_fingerprint="3" * 64,
                metabase_database_id=1,
                metabase_table_id=10,
                metabase_field_id=13,
            ),
        ),
    )
    return DimaExecutionBindingSnapshot(
        semantic_context_version="ctx-p13c-v1",
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
                kind="filter",
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


def _intent(*, with_filter: bool = True) -> ResolvedAnalyticsIntent:
    filters = ()
    if with_filter:
        filters = (
            ResolvedFilterRef(
                semantic_ref="handle.sales_order_channel.web",
                source_candidate_id="cand_sales_order_channel",
                dimension_name="Sales Order Channel",
                value="Web",
                source_scopes=("satis_siparisleri",),
                sensitive=False,
            ),
        )
    return ResolvedAnalyticsIntent(
        authority_id="auth-p13c",
        request_ref="req-p13c",
        source_message_hash="5" * 64,
        projection_hash="6" * 64,
        semantic_context_version="ctx-p13c-v1",
        obligation_ids=("obl-p13c",),
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_count",
                source_candidate_id="cand_sales_order_count",
                kind="metric",
                canonical_name="Sales Order Count",
                source_scopes=("satis_siparisleri",),
            ),
        ),
        filters=filters,
        period=ResolvedPeriod(
            kind="absolute",
            source_text="Haziran 2026",
            time_dimension="sales_orders.opened_at",
            start="2026-06-01",
            end="2026-07-01",
        ),
        principal=PrincipalContextRef(
            tenant_binding="tenant-boyahane",
            principal_subject="user-p13c",
            roles=("analyst",),
        ),
    )


def _engine() -> NativeEngineIdentity:
    return NativeEngineIdentity(
        repository="UpcyTech/dima-metabase-engine",
        engine_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=RUNTIME_TAG,
        build_identity="github-actions:test:" + ENGINE_SHA,
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
                "aggregation": [["count", {"lib/uuid": "00000000-0000-4000-8000-000000000021"}]],
                "filters": [
                    [
                        ">=",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000022"},
                        ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000023"}, 11],
                        "2026-06-01",
                    ],
                    [
                        "<",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000024"},
                        ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000025"}, 11],
                        "2026-07-01",
                    ],
                    [
                        "=",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000026"},
                        ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000027"}, 13],
                        "Web",
                    ],
                ],
            }
        ],
    }


def _manifest(**updates) -> dict:
    values = {
        "attestation_id": "dima_att_" + "c" * 24,
        "native_conversation_id": "00000000-0000-4000-8000-000000000131",
        "native_assistant_message_id": 101,
        "native_tool_call_id": "call-p13c",
        "native_query_id": "native-p13c",
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
        "native_metric_references": (),
        "breakout_count": 0,
        "material_filter_count": 3,
        "non_temporal_filter_count": 1,
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
        "textual_equality_predicates": (
            {
                "stage_number": 0,
                "field_id": 13,
                "operator": "=",
                "literal_value": "Web",
                "field_type": "type/Text",
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
            "build_identity": "github-actions:test:" + ENGINE_SHA,
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
        user_id="user-p13c",
        tenant_id="tenant-boyahane",
        tenant_slug="tenant-boyahane",
        roles=["analyst"],
    )


def _security(attestation: NativeAttestationEnvelope) -> VerifiedExecutionSecurityFacts:
    return VerifiedExecutionSecurityFacts(
        tenant_binding="tenant-boyahane",
        principal_subject="user-p13c",
        roles=("analyst",),
        attribute_policy_digest="9" * 64,
        policy_version="policy-v1",
        rls_versions=(),
        cls_versions=(),
        database_route="analytics-primary",
        database_destination="boyahane",
        impersonation_role=None,
        semantic_context_version="ctx-p13c-v1",
        source_object_refs=(TABLE_RESOURCE, TIME_RESOURCE, CHANNEL_RESOURCE),
        security_parameter_digest="a" * 64,
        metabase_subject_ref="metabase-user:42",
        attestation_refs=(attestation.manifest.attestation_id,),
        evidence_refs=("evidence:metabase-session:p13c",),
    )


def _expected_access(attestation: NativeAttestationEnvelope):
    return ExecutionAccessSnapshotIssuer.issue_for_expected_resources(
        current_principal=_principal(),
        accepted_intent=_intent(),
        verified_security_facts=_security(attestation),
        expected_source_object_refs=(TABLE_RESOURCE, TIME_RESOURCE, CHANNEL_RESOURCE),
    )


def _evidence(
    attestation: NativeAttestationEnvelope,
    *,
    values=("Fuar", "Web"),
    access_lens_ref: str | None = None,
):
    lens = access_lens_ref or _expected_access(attestation).execution_access_fingerprint
    return (
        CurrentLensValueEvidence(
            semantic_ref="handle.sales_order_channel.web",
            values=values,
            access_lens_ref=lens,
            freshness="CURRENT_USER_RETRIEVAL",
        ),
    )


def _authorize(
    attestation: NativeAttestationEnvelope | None = None,
    *,
    intent: ResolvedAnalyticsIntent | None = None,
    evidence=None,
):
    attestation = attestation or _attestation()
    intent = intent or _intent()
    if evidence is None and intent.filters:
        evidence = _evidence(attestation)
    return NativeStandardTrustOrchestrator.authorize(
        intent=intent,
        snapshot=_snapshot(),
        attestation=attestation,
        expected_engine=_engine(),
        current_principal=_principal(),
        verified_security_facts=_security(attestation),
        dima_request_id="dima-req-p13c",
        dima_trace_id="dima-trace-p13c",
        current_lens_value_evidence=tuple(evidence or ()),
    )


def test_p13c_exact_field_value_and_current_lens_evidence_authorize():
    attestation = _attestation()
    result = _authorize(attestation)
    assert result.authorization.outcome == NativeCandidateOutcome.ALLOW
    assert result.access_snapshot is not None
    assert result.access_snapshot.execution_access_fingerprint == (
        _expected_access(attestation).execution_access_fingerprint
    )
    artifact = result.authorization.authorized_artifact
    assert artifact is not None
    assert set(artifact.semantic_refs) == {
        "handle.sales_order_count",
        "handle.sales_order_channel.web",
    }
    assert set(artifact.resource_entity_ids) == {
        TABLE_RESOURCE,
        TIME_RESOURCE,
        CHANNEL_RESOURCE,
    }


@pytest.mark.parametrize(
    ("attestation", "code"),
    [
        (
            _attestation(
                textual_equality_predicates=(
                    {
                        "stage_number": 0,
                        "field_id": 13,
                        "operator": "=",
                        "literal_value": "Fuar",
                        "field_type": "type/Text",
                    },
                ),
            ),
            "NATIVE_TEXTUAL_FILTER_VALUE_MISMATCH",
        ),
        (
            _attestation(
                textual_equality_predicates=(
                    {
                        "stage_number": 0,
                        "field_id": 999,
                        "operator": "=",
                        "literal_value": "Web",
                        "field_type": "type/Text",
                    },
                ),
            ),
            "CURRENT_CATALOG_METABASE_FIELD_BINDING_INVALID",
        ),
        (
            _attestation(
                material_filter_count=4,
                non_temporal_filter_count=2,
                textual_equality_predicates=(
                    {
                        "stage_number": 0,
                        "field_id": 13,
                        "operator": "=",
                        "literal_value": "Web",
                        "field_type": "type/Text",
                    },
                    {
                        "stage_number": 0,
                        "field_id": 13,
                        "operator": "=",
                        "literal_value": "Fuar",
                        "field_type": "type/Text",
                    },
                ),
            ),
            "P13C_FILTER_SCOPE_VIOLATION",
        ),
        (
            _attestation(textual_equality_predicates=()),
            "NATIVE_TEXTUAL_FILTER_ATTESTATION_GAP",
        ),
        (
            _attestation(
                material_filter_count=2,
                non_temporal_filter_count=0,
                textual_equality_predicates=(),
            ),
            "P13C_FILTER_SCOPE_VIOLATION",
        ),
        (
            _attestation(explicit_join_count=1),
            "RELATIONSHIP_GRAIN_VIOLATION",
        ),
    ],
)
def test_p13c_native_filter_scope_attacks_block(attestation, code):
    result = _authorize(attestation)
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == code


def test_p13c_case_changed_native_literal_blocks_without_normalization():
    attestation = _attestation(
        textual_equality_predicates=(
            {
                "stage_number": 0,
                "field_id": 13,
                "operator": "=",
                "literal_value": "web",
                "field_type": "type/Text",
            },
        ),
    )
    result = _authorize(attestation)
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "NATIVE_TEXTUAL_FILTER_VALUE_MISMATCH"


def test_p13c_value_not_in_current_user_evidence_blocks():
    attestation = _attestation()
    result = _authorize(attestation, evidence=_evidence(attestation, values=("Fuar",)))
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "P13C_VALUE_NOT_IN_CURRENT_EVIDENCE"


def test_p13c_access_lens_mismatch_blocks():
    attestation = _attestation()
    result = _authorize(
        attestation,
        evidence=_evidence(attestation, access_lens_ref="wrong-lens"),
    )
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "P13C_ACCESS_LENS_MISMATCH"


def test_p13c_missing_current_user_evidence_blocks():
    result = _authorize(_attestation(), evidence=())
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "P13C_SCOPE_EVIDENCE_MISMATCH"


def test_p13c_native_filter_without_accepted_filter_blocks():
    result = _authorize(_attestation(), intent=_intent(with_filter=False), evidence=())
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "SEMANTIC_SCOPE_VIOLATION"


def test_p13c_exact_artifact_mutation_after_authorization_hard_fails():
    attestation = _attestation()
    result = _authorize(attestation)
    assert result.authorization.outcome == NativeCandidateOutcome.ALLOW
    attestation.exact_serialized_pmbql["stages"][0]["limit"] = 999
    with pytest.raises(NativeExecutionTrustError) as exc:
        NativeStandardTrustOrchestrator.execution_request(
            result=result,
            attestation=attestation,
        )
    assert exc.value.code == "EXECUTION_ARTIFACT_MISMATCH"
