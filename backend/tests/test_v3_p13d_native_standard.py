from __future__ import annotations

import hashlib
import json

import pytest

from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedRanking,
    ResolvedSemanticRef,
)
from app.v3.native_execution import NativeCandidateOutcome
from app.v3.native_standard.contracts import NativeAttestationEnvelope
from app.v3.native_standard.trust import NativeStandardTrustOrchestrator
from app.v3.security_identity import VerifiedExecutionSecurityFacts
from app.v3.semantic_spec import DimensionSpec, DimaSemanticSpec, MetricSpec, SourceLineage, TimeSpec
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    TemporalSemanticBinding,
)
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal


ENGINE_SHA = "5" * 40
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
RUNTIME_TAG = "v0.63.18-dima.5"
INSTANCE_ID = "00000000-0000-4000-8000-000000000135"
IMAGE_ID = "sha256:" + "8" * 64

TABLE = "boyahane:satis_siparisleri"
TIME = "boyahane:satis_siparisleri.acilis_tarihi"
CHANNEL = "boyahane:satis_siparisleri.kanal"


def _hash(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
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
        semantic_context_version="ctx-p13d-v1",
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
        semantic_context_version="ctx-p13d-v1",
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
            catalog_version="boyahane-p13d-v1",
            objects=(
                CurrentCatalogObject(
                    source_id=table.source_id,
                    database_ref="boyahane",
                    schema_name="main",
                    table_name="satis_siparisleri",
                    resource_entity_id=TABLE,
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
                    resource_entity_id=TIME,
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
                    resource_entity_id=CHANNEL,
                    resource_fingerprint="3" * 64,
                    metabase_database_id=1,
                    metabase_table_id=10,
                    metabase_field_id=13,
                ),
            ),
        ),
    )


def _intent(*, ranking: bool = False, dimension: bool = True) -> ResolvedAnalyticsIntent:
    dimensions = ()
    if dimension:
        dimensions = (
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_channel",
                source_candidate_id="cand_sales_order_channel",
                kind="dimension",
                canonical_name="Sales Order Channel",
                source_scopes=("satis_siparisleri",),
            ),
        )
    return ResolvedAnalyticsIntent(
        authority_id="asa-p13d",
        request_ref="req-p13d",
        source_message_hash="4" * 64,
        projection_hash="6" * 64,
        semantic_context_version="ctx-p13d-v1",
        obligation_ids=("obl-p13d",),
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_count",
                source_candidate_id="cand_sales_order_count",
                kind="metric",
                canonical_name="Sales Order Count",
                source_scopes=("satis_siparisleri",),
            ),
        ),
        dimensions=dimensions,
        period=ResolvedPeriod(
            kind="absolute",
            source_text="Haziran 2026",
            time_dimension="sales_orders.opened_at",
            start="2026-06-01",
            end="2026-07-01",
        ),
        ranking=(
            ResolvedRanking(measure="Sales Order Count", direction="desc", limit=2)
            if ranking
            else None
        ),
        principal=PrincipalContextRef(
            tenant_binding="tenant-boyahane",
            principal_subject="user-p13d",
            roles=("analyst",),
        ),
    )


def _query(*, ranking: bool = False) -> dict:
    stage = {
        "lib/type": "mbql.stage/mbql",
        "source-table": 10,
        "aggregation": [["count", {"lib/uuid": "00000000-0000-4000-8000-000000000201"}]],
        "breakout": [
            ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000202"}, 13]
        ],
        "filters": [
            [
                ">=",
                {"lib/uuid": "00000000-0000-4000-8000-000000000203"},
                ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000204"}, 11],
                "2026-06-01",
            ],
            [
                "<",
                {"lib/uuid": "00000000-0000-4000-8000-000000000205"},
                ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000206"}, 11],
                "2026-07-01",
            ],
        ],
    }
    if ranking:
        stage["order-by"] = [
            [
                "desc",
                {"lib/uuid": "00000000-0000-4000-8000-000000000207"},
                ["aggregation", {"lib/uuid": "00000000-0000-4000-8000-000000000208"}, "00000000-0000-4000-8000-000000000201"],
            ]
        ]
        stage["limit"] = 2
    return {"lib/type": "mbql/query", "database": 1, "stages": [stage]}


def _manifest(*, ranking: bool = False, query: dict | None = None, **updates) -> dict:
    query = query or _query(ranking=ranking)
    values = {
        "attestation_id": "dima_att_" + "d" * 24,
        "native_conversation_id": "00000000-0000-4000-8000-000000000231",
        "native_assistant_message_id": 201,
        "native_tool_call_id": "call-p13d",
        "native_query_id": "native-p13d",
        "producer_tool": "construct_notebook_query",
        "exact_pmbql_fingerprint": _hash(query),
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
        "order_by_count": 1 if ranking else 0,
        "order_bys": (
            (
                {
                    "stage_number": 0,
                    "order_index": 0,
                    "direction": "desc",
                    "target_kind": "aggregation",
                    "aggregation_index": 0,
                },
            )
            if ranking
            else ()
        ),
        "limit": 2 if ranking else None,
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


def _attestation(*, ranking: bool = False, **updates) -> NativeAttestationEnvelope:
    query = _query(ranking=ranking)
    return NativeAttestationEnvelope(
        exact_serialized_pmbql=query,
        manifest=_manifest(ranking=ranking, query=query, **updates),
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


def _principal() -> Principal:
    return Principal(
        user_id="user-p13d",
        tenant_id="tenant-boyahane",
        tenant_slug="tenant-boyahane",
        roles=["analyst"],
    )


def _security(
    attestation: NativeAttestationEnvelope,
    *,
    source_object_refs: tuple[str, ...] = (TABLE, TIME, CHANNEL),
) -> VerifiedExecutionSecurityFacts:
    return VerifiedExecutionSecurityFacts(
        tenant_binding="tenant-boyahane",
        principal_subject="user-p13d",
        roles=("analyst",),
        attribute_policy_digest="9" * 64,
        policy_version="policy-v1",
        rls_versions=(),
        cls_versions=(),
        database_route="analytics-primary",
        database_destination="boyahane",
        impersonation_role=None,
        semantic_context_version="ctx-p13d-v1",
        source_object_refs=source_object_refs,
        security_parameter_digest="a" * 64,
        metabase_subject_ref="metabase-user:42",
        attestation_refs=(attestation.manifest.attestation_id,),
        evidence_refs=("evidence:metabase-session:p13d",),
    )


def _authorize(*, ranking: bool = False, intent=None, attestation=None):
    intent = intent or _intent(ranking=ranking)
    attestation = attestation or _attestation(ranking=ranking)
    return NativeStandardTrustOrchestrator.authorize(
        intent=intent,
        snapshot=_snapshot(),
        attestation=attestation,
        expected_engine=_engine(),
        current_principal=_principal(),
        verified_security_facts=_security(attestation),
        dima_request_id="dima-req-p13d",
        dima_trace_id="dima-trace-p13d",
    )


def test_breakdown_exact_dimension_authorizes():
    result = _authorize()
    assert result.authorization.outcome == NativeCandidateOutcome.ALLOW
    artifact = result.authorization.authorized_artifact
    assert artifact is not None
    assert set(artifact.semantic_refs) == {
        "handle.sales_order_count",
        "handle.sales_order_channel",
    }
    assert set(artifact.resource_entity_ids) == {TABLE, TIME, CHANNEL}


def test_ranking_exact_metric_desc_top2_authorizes():
    result = _authorize(ranking=True)
    assert result.authorization.outcome == NativeCandidateOutcome.ALLOW


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"breakout_count": 0, "breakouts": ()}, "P13D_BREAKOUT_SCOPE_VIOLATION"),
        (
            {
                "breakouts": (
                    {
                        "stage_number": 0,
                        "breakout_index": 0,
                        "field_id": 11,
                        "field_type": "type/DateTime",
                    },
                ),
            },
            "P13D_BREAKOUT_FIELD_MISMATCH",
        ),
        (
            {
                "breakout_count": 2,
                "breakouts": (
                    {"stage_number": 0, "breakout_index": 0, "field_id": 13, "field_type": "type/Text", "temporal_unit": None},
                    {"stage_number": 0, "breakout_index": 1, "field_id": 11, "field_type": "type/DateTime", "temporal_unit": None},
                ),
            },
            "P13D_BREAKOUT_SCOPE_VIOLATION",
        ),
    ],
)
def test_breakout_attacks_block(updates, code):
    result = _authorize(attestation=_attestation(**updates))
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == code


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        (
            {
                "order_bys": (
                    {
                        "stage_number": 0,
                        "order_index": 0,
                        "direction": "asc",
                        "target_kind": "aggregation",
                        "aggregation_index": 0,
                    },
                ),
            },
            "P13D_RANKING_DIRECTION_MISMATCH",
        ),
        (
            {
                "order_bys": (
                    {
                        "stage_number": 0,
                        "order_index": 0,
                        "direction": "desc",
                        "target_kind": "field",
                        "field_id": 13,
                        "field_type": "type/Text",
                    },
                ),
            },
            "P13D_RANKING_TARGET_MISMATCH",
        ),
        ({"limit": 5}, "P13D_RANKING_LIMIT_MISMATCH"),
        ({"order_by_count": 0, "order_bys": ()}, "P13D_RANKING_SCOPE_VIOLATION"),
    ],
)
def test_ranking_attacks_block(updates, code):
    result = _authorize(
        ranking=True,
        attestation=_attestation(ranking=True, **updates),
    )
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == code


def test_unexpected_ranking_without_authority_blocks():
    result = _authorize(
        attestation=_attestation(ranking=True),
        intent=_intent(ranking=False),
    )
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "P13D_RANKING_SCOPE_VIOLATION"


def test_limit_without_ranking_authority_blocks():
    result = _authorize(attestation=_attestation(limit=2))
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "P13D_RANKING_SCOPE_VIOLATION"


def test_join_introduction_still_blocks():
    result = _authorize(attestation=_attestation(explicit_join_count=1))
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "RELATIONSHIP_GRAIN_VIOLATION"


def test_ranking_without_dimension_is_not_authorized():
    result = _authorize(
        intent=_intent(ranking=False, dimension=False).model_copy(
            update={"ranking": ResolvedRanking(measure="Sales Order Count", direction="desc", limit=2)}
        ),
        attestation=_attestation(ranking=True),
    )
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "P13D_RANKING_REQUIRES_DIMENSION"


def _comparison_intent() -> ResolvedAnalyticsIntent:
    return ResolvedAnalyticsIntent(
        authority_id="asa-p13d-comparison",
        request_ref="req-p13d-comparison",
        source_message_hash="7" * 64,
        projection_hash="8" * 64,
        semantic_context_version="ctx-p13d-v1",
        obligation_ids=("obl-p13d-comparison",),
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_count",
                source_candidate_id="cand_sales_order_count",
                kind="metric",
                canonical_name="Sales Order Count",
                source_scopes=("satis_siparisleri",),
            ),
        ),
        comparison=ResolvedComparison(
            mode="previous_period",
            source_text="Haziran 2026 ile Mayıs 2026'yı karşılaştır",
            base_period=ResolvedPeriod(
                kind="absolute",
                source_text="Haziran 2026",
                time_dimension="sales_orders.opened_at",
                start="2026-06-01",
                end="2026-07-01",
            ),
            reference_period=ResolvedPeriod(
                kind="absolute",
                source_text="Mayıs 2026",
                time_dimension="sales_orders.opened_at",
                start="2026-05-01",
                end="2026-06-01",
            ),
        ),
        principal=PrincipalContextRef(
            tenant_binding="tenant-boyahane",
            principal_subject="user-p13d",
            roles=("analyst",),
        ),
    )


def _comparison_query() -> dict:
    return {
        "lib/type": "mbql/query",
        "database": 1,
        "stages": [
            {
                "lib/type": "mbql.stage/mbql",
                "source-table": 10,
                "aggregation": [
                    ["count", {"lib/uuid": "00000000-0000-4000-8000-000000000301"}]
                ],
                "breakout": [
                    [
                        "field",
                        {
                            "lib/uuid": "00000000-0000-4000-8000-000000000302",
                            "temporal-unit": "month",
                        },
                        11,
                    ]
                ],
                "filters": [
                    [
                        ">=",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000303"},
                        ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000304"}, 11],
                        "2026-05-01",
                    ],
                    [
                        "<",
                        {"lib/uuid": "00000000-0000-4000-8000-000000000305"},
                        ["field", {"lib/uuid": "00000000-0000-4000-8000-000000000306"}, 11],
                        "2026-07-01",
                    ],
                ],
            }
        ],
    }


def _comparison_attestation(**updates) -> NativeAttestationEnvelope:
    query = _comparison_query()
    manifest = _manifest(query=query)
    manifest.update(
        {
            "exact_pmbql_fingerprint": _hash(query),
            "breakout_count": 1,
            "breakouts": (
                {
                    "stage_number": 0,
                    "breakout_index": 0,
                    "field_id": 11,
                    "field_type": "type/DateTime",
                    "temporal_unit": "month",
                },
            ),
            "temporal_predicates": (
                {
                    "time_field_id": 11,
                    "operator": ">=",
                    "lower_bound": "2026-05-01",
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
        }
    )
    manifest.update(updates)
    return NativeAttestationEnvelope(
        exact_serialized_pmbql=query,
        manifest=manifest,
    )


def _authorize_comparison(attestation=None, intent=None):
    attestation = attestation or _comparison_attestation()
    intent = intent or _comparison_intent()
    return NativeStandardTrustOrchestrator.authorize(
        intent=intent,
        snapshot=_snapshot(),
        attestation=attestation,
        expected_engine=_engine(),
        current_principal=_principal(),
        verified_security_facts=_security(
            attestation,
            source_object_refs=(TABLE, TIME),
        ),
        dima_request_id="dima-req-p13d-comparison",
        dima_trace_id="dima-trace-p13d-comparison",
    )


def test_previous_period_comparison_exact_single_native_query_authorizes():
    result = _authorize_comparison()
    assert result.authorization.outcome == NativeCandidateOutcome.ALLOW
    artifact = result.authorization.authorized_artifact
    assert artifact is not None
    assert artifact.query_count == 1
    assert set(artifact.resource_entity_ids) == {TABLE, TIME}


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        (
            {
                "breakouts": (
                    {
                        "stage_number": 0,
                        "breakout_index": 0,
                        "field_id": 11,
                        "field_type": "type/DateTime",
                        "temporal_unit": "day",
                    },
                ),
            },
            "P13D_COMPARISON_GRAIN_MISMATCH",
        ),
        (
            {"breakout_count": 0, "breakouts": ()},
            "P13D_BREAKOUT_SCOPE_VIOLATION",
        ),
        (
            {
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
            },
            "TIME_SCOPE_VIOLATION",
        ),
    ],
)
def test_comparison_attacks_block(updates, code):
    result = _authorize_comparison(_comparison_attestation(**updates))
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == code


def test_non_contiguous_comparison_authority_blocks():
    intent = _comparison_intent()
    bad = intent.model_copy(
        update={
            "comparison": intent.comparison.model_copy(
                update={
                    "reference_period": intent.comparison.reference_period.model_copy(
                        update={"end": "2026-05-31"}
                    )
                }
            )
        }
    )
    result = _authorize_comparison(intent=bad)
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "P13D_COMPARISON_PERIODS_UNSUPPORTED"
