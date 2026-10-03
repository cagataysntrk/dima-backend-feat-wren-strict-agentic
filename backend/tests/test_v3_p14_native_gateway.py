from __future__ import annotations

import hashlib
import inspect
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

import app.v3.research_analytical_scope as scope_module
import app.v3.research_native_gateway as gateway_module
from app.v3.analytical_request_contract import (
    AnalyticalFilterInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
)
from app.v3.native_standard.contracts import NativeAttestationEnvelope
from app.v3.research_contracts import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchNativeVerificationBinding,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResultSelectionDependency,
    SemanticTargetKind,
)
from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
)
from app.v3.research import ObligationState, ResearchManager
from app.v3.research_native_gateway import (
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
)
from app.v3.research_product import (
    ResearchAskOrchestrator,
    ResearchMaterialLimitation,
    ResearchMaterialObservationUnavailable,
)
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from app.v3.substrate.metabase.native_engine import (
    NativeDatasetExecutionError,
    NativeEngineBridgeError,
)
from app.v3.substrate.metabase.native_models import (
    NativeDatasetExecutionObservation,
    NativeEngineIdentity,
    NativeMaterialDimension,
    NativeMaterialMetric,
    NativeMaterialObservation,
)
from control_plane.authorize import Principal
from control_plane.models import NativeResourceBinding, NativeSubjectBinding, Tenant, User
from lab.metabase.p14.native_direct_research_canary import (
    FROZEN_BOYAHANE_CHANNEL_COUNTS,
    channel_counts,
)


ENGINE_SHA = "14323cdde4f258c65c63bbd88f1034f814a7ecb3"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
TAG = "v0.63.18-dima.7"
DIGEST = "sha256:75a96218bb6a881d792ec13895e438aa5fa897d06a7743c0c3416fa244d13b30"
BUILD = f"github-actions:36532842632:{ENGINE_SHA}"
IMAGE = DIGEST
INSTANCE = UUID("00000000-0000-4000-8000-000000000777")
TENANT = UUID("00000000-0000-4000-8000-000000000701")
USER = UUID("00000000-0000-4000-8000-000000000702")
CONTEXT = "ctx-p14-native-direct-v1"
STAMP = datetime(2026, 9, 25, 5, 0, tzinfo=timezone.utc)


def h(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def principal() -> Principal:
    return Principal(
        user_id=str(USER),
        tenant_id=str(TENANT),
        roles=["analyst"],
        tenant_slug="native-direct",
    )


def expected_identity() -> NativeEngineIdentity:
    return NativeEngineIdentity(
        engine_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=TAG,
        runtime_image_digest=DIGEST,
        build_identity=BUILD,
        runtime_image_identity=IMAGE,
    )


def identity_payload() -> dict:
    return {
        "repository": "UpcyTech/dima-metabase-engine",
        "revision_sha": ENGINE_SHA,
        "upstream_base_sha": UPSTREAM_SHA,
        "runtime_tag": TAG,
        "build_identity": BUILD,
        "image_identity": IMAGE,
        "runtime_instance_id": str(INSTANCE),
    }


def brief() -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="satış siparişleri",
        candidate_id="cand_sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    channel = ResearchSemanticRef(
        source_mention="kanal",
        candidate_id="cand_sales_order_channel",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Sales Order Channel",
        cube_names=("satis_siparisleri",),
    )
    q = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Satış siparişlerini kanala göre incele.",
        subject_refs=(metric,),
        related_refs=(channel,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p14-native-direct",
        objective=q.source_text,
        scope=ResearchScope(
            semantic_refs=(metric, channel),
            native_verification_bindings=(
                ResearchNativeVerificationBinding(
                    candidate_id=metric.candidate_id,
                    table_name="sales_orders",
                    aggregation="count",
                    argument_kind="all_rows",
                    native_metric_entity_id="metric-sales-order-count-v1",
                ),
                ResearchNativeVerificationBinding(
                    candidate_id=channel.candidate_id,
                    table_name="sales_orders",
                    column_name="channel",
                ),
            ),
        ),
        questions=(q,),
        must_requirement_ids=("g1",),
        context_version=CONTEXT,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def seed(engine):
    with Session(engine) as db:
        db.add(
            Tenant(
                id=TENANT,
                slug="native-direct",
                name="Native Direct",
                created_at=STAMP,
            )
        )
        db.add(
            User(
                id=USER,
                tenant_id=TENANT,
                email="p14-native@example.test",
                password_hash="not-used",
                created_at=STAMP,
            )
        )
        db.commit()
        db.add(
            NativeSubjectBinding(
                tenant_id=TENANT,
                dima_user_id=USER,
                metabase_user_id=7,
                # Transitional columns intentionally remain non-authoritative metadata.
                security_profile="legacy-metadata",
                policy_version="legacy-metadata",
                approved_by_user_id=USER,
            )
        )
        db.commit()
        db.add(
            NativeResourceBinding(
                tenant_id=TENANT,
                semantic_context_version=CONTEXT,
                candidate_id="cand_sales_order_count",
                candidate_kind="metric",
                semantic_id="metric.sales_order_count",
                canonical_name="Sales Order Count",
                locator_kind="metric",
                metabase_database_id=1,
                metabase_table_id=10,
                metabase_metric_id=501,
                metabase_entity_id="metric-sales-order-count-v1",
                resource_entity_id="metabase:metric:metric-sales-order-count-v1",
                resource_fingerprint="1" * 64,
                resource_version="native-direct-test-v1",
            )
        )
        db.add(
            NativeResourceBinding(
                tenant_id=TENANT,
                semantic_context_version=CONTEXT,
                candidate_id="cand_sales_order_channel",
                candidate_kind="dimension",
                semantic_id="dimension.sales_order_channel",
                canonical_name="Sales Order Channel",
                locator_kind="field",
                metabase_database_id=1,
                metabase_table_id=10,
                metabase_field_id=20,
                resource_entity_id="metabase:field:20",
                resource_fingerprint="2" * 64,
                resource_version="native-direct-test-v1",
            )
        )
        db.commit()


def test_result_dependency_projects_exact_parent_row_as_execution_local_filter():
    import importlib

    dependency_module = importlib.import_module(
        "app.v3.research_result_dependency"
    )
    base = AnalyticalRequestContract(
        authority_id="authority-result-dependency",
        request_ref="request-result-dependency",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-result-dependency",
            version_id="scope_v1",
        ),
        scope_fingerprint="a" * 64,
        metric_refs=("cand_sales_order_count",),
        dimension_refs=("cand_sales_order_channel",),
    )
    parent_result = {
        "data": {
            "cols": [
                {
                    "id": 20,
                    "table_id": 10,
                    "name": "sales_order_channel",
                    "field_ref": ["field", 20, None],
                },
                {
                    "name": "sum",
                    "field_ref": ["aggregation", 0],
                },
            ],
            "rows": [["Web", 41], ["Direct", 33]],
        }
    }
    resolution = dependency_module.resolve_first_ranked_entity(
        base_contract=base,
        source_goal_id="g-parent",
        source_evidence_id="evidence-parent",
        source_receipt_id="receipt-parent",
        source_result_hash="b" * 64,
        dimension_semantic_id="cand_sales_order_channel",
        native_field_id=20,
        parent_result=parent_result,
    )

    assert resolution.selected_value == "Web"
    assert resolution.contract.scope_identity == base.scope_identity
    assert resolution.contract.scope_fingerprint == base.scope_fingerprint
    assert resolution.contract.metric_refs == base.metric_refs
    assert resolution.contract.filters[-1].source_candidate_id == (
        "cand_sales_order_channel"
    )
    assert resolution.contract.filters[-1].value == "Web"
    assert resolution.contract.filters[-1].semantic_ref.startswith(
        "result-selection:"
    )
    assert resolution.contract.material_fingerprint != base.material_fingerprint


def test_verified_parent_result_dependency_resolves_through_p14_executor(monkeypatch):
    base_brief = brief()
    metric, channel = base_brief.scope.semantic_refs
    child = ResearchQuestion(
        goal_id="g-child",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect the selected governed channel.",
        subject_refs=(metric,),
        related_refs=(channel,),
        result_dependency=ResultSelectionDependency(
            source_goal_id="g-parent",
            dimension_semantic_id=channel.candidate_id,
            selection="first_ranked_entity",
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    session = SimpleNamespace(
        session_id="rs-result-dependency",
        accepted_brief=SimpleNamespace(
            questions=(child,),
            scope=base_brief.scope,
        ),
    )
    parent_result = {
        "data": {
            "cols": [
                {
                    "id": 20,
                    "table_id": 10,
                    "name": "sales_order_channel",
                    "field_ref": ["field", 20, None],
                },
                {"name": "count", "field_ref": ["aggregation", 0]},
            ],
            "rows": [["Web", 41], ["Direct", 33]],
        }
    }
    parent_link = SimpleNamespace(
        evidence_id="evidence-parent",
        receipt_id="receipt-parent",
        result_hash="b" * 64,
    )

    class ParentStore:
        def __init__(self):
            self.calls = 0

        def verified_material_result(self, *, session_id, obligation_id):
            self.calls += 1
            assert session_id == "rs-result-dependency"
            assert obligation_id == "g-parent"
            return parent_link, parent_result

    store = ParentStore()
    executor = NativeResearchMaterialExecutor(
        subject_provider=SimpleNamespace(db_engine=None),
        store=store,
        expected_identity=expected_identity(),
    )
    monkeypatch.setattr(
        executor,
        "_material_bindings",
        lambda **_: {
            channel.candidate_id: scope_module.NativeMaterialBinding(
                candidate_id=channel.candidate_id,
                candidate_kind="dimension",
                database_id=1,
                table_id=10,
                field_id=20,
            )
        },
    )
    base = AnalyticalRequestContract(
        authority_id="authority-result-dependency",
        request_ref="request-result-dependency",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-result-dependency",
            version_id="scope_v1",
        ),
        scope_fingerprint=base_brief.scope_fingerprint,
        metric_refs=(metric.candidate_id,),
        dimension_refs=(channel.candidate_id,),
    )

    resolution = executor.resolve_result_dependency(
        principal=principal(),
        session=session,
        obligation_id=child.goal_id,
        analytical_scope=base,
    )

    assert resolution is not None
    assert store.calls == 1
    assert resolution.selected_value == "Web"
    assert resolution.contract.scope_identity == base.scope_identity
    assert resolution.contract.scope_fingerprint == base.scope_fingerprint
    assert resolution.contract.filters[-1].value == "Web"
    assert resolution.contract.filters[-1].source_candidate_id == channel.candidate_id


def test_result_dependency_preserves_semantic_source_and_uses_execution_anchor(monkeypatch):
    base_brief = brief()
    metric, channel = base_brief.scope.semantic_refs
    child = ResearchQuestion(
        goal_id="g-child-shared",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect the selected governed channel.",
        subject_refs=(metric,),
        related_refs=(channel,),
        result_dependency=ResultSelectionDependency(
            source_goal_id="g-semantic-parent",
            dimension_semantic_id=channel.candidate_id,
            selection="first_ranked_entity",
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    session = SimpleNamespace(
        session_id="rs-shared-result-dependency",
        accepted_brief=SimpleNamespace(
            questions=(child,),
            scope=base_brief.scope,
        ),
    )
    parent_result = {
        "data": {
            "cols": [
                {
                    "id": 20,
                    "table_id": 10,
                    "name": "sales_order_channel",
                    "field_ref": ["field", 20, None],
                },
                {"name": "count", "field_ref": ["aggregation", 0]},
            ],
            "rows": [["Web", 41], ["Direct", 33]],
        }
    }
    parent_link = SimpleNamespace(
        evidence_id="evidence-shared",
        receipt_id="receipt-shared",
        result_hash="e" * 64,
    )

    class SharedOccurrenceStore:
        def __init__(self):
            self.requested_obligation_ids = []

        def verified_material_result(self, *, session_id, obligation_id):
            assert session_id == "rs-shared-result-dependency"
            self.requested_obligation_ids.append(obligation_id)
            assert obligation_id == "g-execution-anchor"
            return parent_link, parent_result

    store = SharedOccurrenceStore()
    executor = NativeResearchMaterialExecutor(
        subject_provider=SimpleNamespace(db_engine=None),
        store=store,
        expected_identity=expected_identity(),
    )
    monkeypatch.setattr(
        executor,
        "_material_bindings",
        lambda **_: {
            channel.candidate_id: scope_module.NativeMaterialBinding(
                candidate_id=channel.candidate_id,
                candidate_kind="dimension",
                database_id=1,
                table_id=10,
                field_id=20,
            )
        },
    )
    base = AnalyticalRequestContract(
        authority_id="authority-shared-result-dependency",
        request_ref="request-shared-result-dependency",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-shared-result-dependency",
            version_id="scope_v1",
        ),
        scope_fingerprint=base_brief.scope_fingerprint,
        metric_refs=(metric.candidate_id,),
        dimension_refs=(channel.candidate_id,),
    )

    resolution = executor.resolve_result_dependency(
        principal=principal(),
        session=session,
        obligation_id=child.goal_id,
        analytical_scope=base,
        source_execution_obligation_id="g-execution-anchor",
    )

    assert resolution is not None
    assert store.requested_obligation_ids == ["g-execution-anchor"]
    assert resolution.source_goal_id == "g-semantic-parent"
    assert resolution.source_execution_obligation_id == "g-execution-anchor"
    assert resolution.selected_value == "Web"
    assert resolution.contract.scope_identity == base.scope_identity
    assert resolution.contract.scope_fingerprint == base.scope_fingerprint
    assert resolution.contract.filters[-1].value == "Web"


def test_execution_local_overlay_reaches_metabot_contract_projection():
    engine = db_engine()
    seed(engine)
    store = ResearchSessionStore(engine)
    product = ResearchAskOrchestrator(store=store)
    session = product.start_from_brief(
        brief=brief(),
        request_ref="p14-result-overlay-message",
        source_message_hash=hashlib.sha256(b"result overlay message").hexdigest(),
        principal=principal(),
    )
    base = scope_module.analytical_scope_contract(
        session=session,
        obligation_id="g1",
    )
    overlay = base.model_copy(
        update={
            "filters": (
                *base.filters,
                AnalyticalFilterInvariant(
                    semantic_ref="result-selection:" + "c" * 64,
                    source_candidate_id="cand_sales_order_channel",
                    dimension_name="Sales Order Channel",
                    value="Web",
                ),
            )
        }
    )

    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g1",
        analytical_scope=overlay,
    )

    projected = prepared.request.context["dima_analytical_scope"]
    assert projected["scope_identity"] == base.scope_identity.model_dump(mode="json")
    assert projected["scope_fingerprint"] == base.scope_fingerprint
    assert projected["filters"][-1]["value"] == "Web"
    assert projected["filters"][-1]["source_candidate_id"] == "cand_sales_order_channel"
    assert "Sales Order Channel = \"Web\"" in prepared.request.message


def test_verified_material_result_reports_parent_pending_without_replay():
    store = ResearchSessionStore(db_engine())

    with pytest.raises(ResearchPersistenceError) as exc:
        store.verified_material_result(
            session_id="rs-pending-parent",
            obligation_id="g-parent",
        )

    assert exc.value.code == "P14_RESULT_DEPENDENCY_PARENT_PENDING"


def test_result_dependency_provenance_changes_execution_material_identity():
    import app.v3.research_result_dependency as dependency_module

    base = AnalyticalRequestContract(
        authority_id="authority-result-provenance",
        request_ref="request-result-provenance",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-result-provenance",
            version_id="scope_v1",
        ),
        scope_fingerprint="d" * 64,
        metric_refs=("cand_sales_order_count",),
        dimension_refs=("cand_sales_order_channel",),
    )
    parent_result = {
        "data": {
            "cols": [
                {"id": 20, "field_ref": ["field", 20, None]},
                {"field_ref": ["aggregation", 0]},
            ],
            "rows": [["Web", 41]],
        }
    }
    common = {
        "base_contract": base,
        "source_goal_id": "g-parent",
        "source_evidence_id": "evidence-parent",
        "source_receipt_id": "receipt-parent",
        "dimension_semantic_id": "cand_sales_order_channel",
        "native_field_id": 20,
        "parent_result": parent_result,
    }

    first = dependency_module.resolve_first_ranked_entity(
        source_result_hash="1" * 64,
        **common,
    )
    second = dependency_module.resolve_first_ranked_entity(
        source_result_hash="2" * 64,
        **common,
    )

    assert first.selected_value == second.selected_value == "Web"
    assert first.contract.scope_identity == second.contract.scope_identity
    assert first.contract.scope_fingerprint == second.contract.scope_fingerprint
    assert first.contract.filters[-1].semantic_ref != second.contract.filters[-1].semantic_ref
    assert first.contract.material_fingerprint != second.contract.material_fingerprint


def test_native_request_context_preloads_only_required_governed_metrics():
    engine = db_engine()
    seed(engine)
    store = ResearchSessionStore(engine)
    product = ResearchAskOrchestrator(store=store)
    session = product.start_from_brief(
        brief=brief(),
        request_ref="p14-native-preload-test",
        source_message_hash=hashlib.sha256(b"native preload").hexdigest(),
        principal=principal(),
    )
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g1",
    )
    subjects = NativeSubjectSessionProvider(
        base_url="http://metabase.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )

    enriched = executor.enrich_native_request(
        principal=principal(),
        session=session,
        obligation_id="g1",
        request=prepared.request,
    )

    assert enriched.context["dima_analytical_scope"] == (
        prepared.request.context["dima_analytical_scope"]
    )
    assert enriched.context["user_is_viewing"] == [
        {"type": "metric", "id": 501}
    ]
    assert 20 not in {
        item.get("id")
        for item in enriched.context["user_is_viewing"]
    }
    assert enriched.message == prepared.request.message
    assert enriched.state == prepared.request.state
    assert enriched.history == prepared.request.history



def test_native_request_rejects_scope_fingerprint_drift_before_native_work():
    engine = db_engine()
    seed(engine)
    store = ResearchSessionStore(engine)
    product = ResearchAskOrchestrator(store=store)
    session = product.start_from_brief(
        brief=brief(),
        request_ref="p14-native-scope-fp-test",
        source_message_hash=hashlib.sha256(b"native scope fp").hexdigest(),
        principal=principal(),
    )
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g1",
    )
    subjects = NativeSubjectSessionProvider(
        base_url="http://metabase.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    contract = scope_module.analytical_scope_contract(
        session=session,
        obligation_id="g1",
    )
    assert session.accepted_brief is not None
    assert contract.scope_fingerprint == session.accepted_brief.scope_fingerprint
    bad = contract.model_copy(
        update={"scope_fingerprint": "f" * 64}
    )

    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor.enrich_native_request(
            principal=principal(),
            session=session,
            obligation_id="g1",
            request=prepared.request,
            analytical_scope=bad,
        )

    assert exc.value.code == "R1_MATERIAL_SCOPE_FINGERPRINT_MISMATCH"



def session_and_link(engine):
    store = ResearchSessionStore(engine)
    product = ResearchAskOrchestrator(store=store)
    session = product.start_from_brief(
        brief=brief(),
        request_ref="p14-native-direct-test",
        source_message_hash=hashlib.sha256(b"native direct").hexdigest(),
        principal=principal(),
    )
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g1",
    )
    session = store.save(
        prepared.session,
        expected_revision=session.revision,
    )
    assert session.native_conversation is not None
    link = store.begin_delegation(
        session=session,
        obligation_id="g1",
        dima_request_id=prepared.request.dima_request_id,
        dima_trace_id=prepared.request.dima_trace_id,
        native_conversation_id=session.native_conversation.conversation_id,
    )
    query = {
        "database": 1,
        "type": "query",
        "query": {
            "source-table": 10,
            "aggregation": [["count"]],
            "breakout": [["field", 20, None]],
        },
    }
    link = store.mark_candidate(
        link.id,
        native_query_id="native-query-1",
        native_query=query,
        query_fingerprint=h(query),
    )
    return store, session, link, query


def attestation_payload(query):
    return {
        "exact_serialized_pmbql": query,
        "manifest": {
            "attestation_id": "att-p14-test",
            "native_conversation_id": str(
                UUID("00000000-0000-4000-8000-000000000778")
            ),
            "native_assistant_message_id": 1,
            "native_tool_call_id": "tool-p14-test",
            "native_query_id": "native-query-1",
            "producer_tool": "construct_notebook_query",
            "exact_pmbql_fingerprint": h(query),
            "database_id": 1,
            "primary_source_table_id": 10,
            "referenced_source_table_ids": [10],
            "aggregation_count": 1,
            "aggregations": [
                {
                    "operator": "count",
                    "argument_kind": "all_rows",
                    "referenced_field_ids": [],
                    "distinct": False,
                }
            ],
            "native_metric_references": [
                {
                    "stage_number": 0,
                    "aggregation_index": 0,
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-sales-order-count-v1",
                }
            ],
            "breakout_count": 1,
            "breakouts": [
                {
                    "stage_number": 0,
                    "breakout_index": 0,
                    "field_id": 20,
                    "field_type": "type/Text",
                    "temporal_unit": None,
                }
            ],
            "material_filter_count": 0,
            "non_temporal_filter_count": 0,
            "temporal_predicates": [],
            "textual_equality_predicates": [],
            "explicit_join_count": 0,
            "implicit_join_count": 0,
            "implicit_joined_table_ids": [],
            "order_by_count": 0,
            "order_bys": [],
            "limit": None,
            "stage_count": 1,
            "material_query_count": 1,
            "authenticated_metabase_subject": 7,
            "validation_provenance": {
                "producer_structured_output": "PASSED",
                "pmbql_schema": "PASSED",
                "producer_query_id_match": "PASSED",
                "producer_state_match": "PASSED",
            },
            "permission_provenance": {
                "current_metabase_user_id": 7,
                "permission_check": "PASSED",
                "checked_source_table_ids": [10],
            },
            "runtime_identity": identity_payload(),
        },
    }


def material_observation_payload(
    query,
    *,
    conversation_id=UUID("00000000-0000-4000-8000-000000000778"),
    native_query_id="native-query-1",
    metrics=None,
    dimensions=None,
    filters=None,
    temporal_scopes=None,
    ranking=None,
    runtime_identity=None,
    subject=7,
):
    return {
        "schema_version": "dima_native_material_observation_v1",
        "conversation_id": str(conversation_id),
        "native_query_id": native_query_id,
        "assistant_message_id": 1,
        "tool_call_id": "tool-p14-test",
        "query_fingerprint": h(query),
        "authenticated_metabase_subject": subject,
        "database_id": 1,
        "runtime_identity": runtime_identity or identity_payload(),
        "native_metrics": metrics if metrics is not None else [
            {
                "stage_number": 0,
                "aggregation_index": 0,
                "metabase_metric_id": 501,
                "metabase_metric_entity_id": "metric-sales-order-count-v1",
            }
        ],
        "dimensions": dimensions if dimensions is not None else [
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 20,
                "table_id": 10,
            }
        ],
        "filters": filters if filters is not None else [],
        "temporal_scopes": temporal_scopes if temporal_scopes is not None else [],
        "ranking": ranking if ranking is not None else [],
    }


def test_forward_scope_accepts_same_governed_metric_with_different_physical_plan():
    engine = db_engine()
    seed(engine)
    _, session, _, query = session_and_link(engine)
    base = NativeAttestationEnvelope.model_validate(attestation_payload(query))

    physical_variant = base.manifest.model_copy(
        update={
            "aggregation_count": 2,
            "aggregations": (
                base.manifest.aggregations[0].model_copy(
                    update={
                        "operator": "sum",
                        "argument_kind": "field_or_expression",
                        "referenced_field_ids": (20,),
                    }
                ),
                base.manifest.aggregations[0],
            ),
            "native_metric_references": (
                base.manifest.native_metric_references[0].model_copy(
                    update={"aggregation_index": 0}
                ),
            ),
            "material_query_count": 2,
        }
    )
    attestation = base.model_copy(update={"manifest": physical_variant})
    contract = scope_module.analytical_scope_contract(
        session=session,
        obligation_id="g1",
    )

    observed = scope_module.assert_attested_native_scope(
        session=session,
        obligation_id="g1",
        contract=contract,
        attestation=attestation,
        field_locators={
            20: scope_module.NativeFieldLocator(
                field_id=20,
                table_id=10,
                table_name="sales_orders",
                column_name="channel",
            )
        },
        table_locators={
            10: scope_module.NativeTableLocator(
                table_id=10,
                table_name="sales_orders",
            )
        },
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.request.metric_refs == ("cand_sales_order_count",)
    assert observed.request.scope_identity.version_id == "scope_v1"


def test_research_forward_scope_is_not_a_query_implementation_validator():
    metric_source = inspect.getsource(scope_module._assert_metric_scope)
    ranking_source = inspect.getsource(scope_module._assert_breakout_and_ranking)
    forward_source = inspect.getsource(scope_module.assert_attested_native_scope)
    module_source = inspect.getsource(scope_module)

    for forbidden in ("aggregation_count", "argument_kind", ".operator"):
        assert forbidden not in metric_source
    assert "material_query_count" not in forward_source
    assert 'target_kind != "aggregation"' not in ranking_source
    for forbidden in ("sqlparse", "parse_mbql", "query_optimizer"):
        assert forbidden not in module_source


class MaterialBridge:
    def __init__(
        self,
        *,
        forbidden=False,
        fail_on_execute=False,
        observation_error=False,
        observation_update=None,
    ):
        self.calls = []
        self.forbidden = forbidden
        self.fail_on_execute = fail_on_execute
        self.observation_error = observation_error
        self.observation_update = observation_update or {}
        self.attestation_calls = []
        self.material_observation_calls = []

    @staticmethod
    def _query():
        return {
            "database": 1,
            "type": "query",
            "query": {
                "source-table": 10,
                "aggregation": [["count"]],
                "breakout": [["field", 20, None]],
            },
        }

    def execute_dataset(self, query):
        if self.fail_on_execute:
            raise AssertionError("persisted EXECUTED occurrence was executed twice")
        self.calls.append(query)
        if self.forbidden:
            raise NativeDatasetExecutionError(
                status_code=403,
                detail="You do not have permissions to run this query.",
            )
        return NativeDatasetExecutionObservation(
            status_code=202,
            latency_ms=3,
            query_fingerprint=h(query),
            payload={
                "status": "completed",
                "database_id": 1,
                "row_count": 1,
                "data": {"rows": [["Web", 4]], "cols": []},
            },
        )

    def engine_identity(self):
        return identity_payload()

    def attest_native_query(self, *, conversation_id, native_query_id):
        self.attestation_calls.append((conversation_id, native_query_id))
        raise AssertionError("ordinary R5 Research must not call P13 attestation")

    def observe_native_query_material(self, *, conversation_id, native_query_id):
        self.material_observation_calls.append((conversation_id, native_query_id))
        if self.observation_error:
            raise NativeEngineBridgeError("material observation unavailable")
        query = self.calls[-1] if self.calls else self._query()
        payload = material_observation_payload(
            query,
            conversation_id=conversation_id,
            native_query_id=native_query_id,
        )
        payload.update(self.observation_update)
        return NativeMaterialObservation.model_validate(payload)


class P13RejectingButDatasetLegalBridge(MaterialBridge):
    """P13 may reject the physical shape; ordinary R5 never asks it."""

    def __init__(self, *, p13_detail: str):
        super().__init__()
        self.p13_detail = p13_detail

    def attest_native_query(self, *, conversation_id, native_query_id):
        self.attestation_calls.append((conversation_id, native_query_id))
        raise NativeEngineBridgeError(self.p13_detail)


@pytest.mark.parametrize(
    "p13_detail",
    (
        (
            "native attestation returned HTTP 422: "
            "NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED "
            "clause-tag=absolute-datetime"
        ),
        (
            "native attestation returned HTTP 422: "
            "NATIVE_METRIC_EXPANSION_UNSUPPORTED "
            "native-metric-reference-count=1 "
            "original-aggregation-count=3 expanded-aggregation-count=3"
        ),
    ),
)
def test_r5_p13_rejection_does_not_block_legal_native_execution(p13_detail):
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    bridge = P13RejectingButDatasetLegalBridge(p13_detail=p13_detail)

    outcome = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=bridge,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )

    assert outcome.evidence.verified
    assert session.accepted_brief is not None
    assert (
        outcome.receipt.scope_fingerprint
        == session.accepted_brief.scope_fingerprint
    )
    assert (
        outcome.evidence.payload["scope_fingerprint"]
        == session.accepted_brief.scope_fingerprint
    )
    assert bridge.attestation_calls == []
    assert bridge.calls == [query]
    assert bridge.material_observation_calls == [
        (link.native_conversation_id, link.native_query_id)
    ]
    assert store.execution_link(link.id).status == "EXECUTED"



def test_r5_architecture_removes_p13_from_ordinary_research_permission_path():
    source = inspect.getsource(gateway_module)
    execute_source = inspect.getsource(NativeResearchMaterialExecutor.execute)
    observe_source = inspect.getsource(NativeResearchMaterialExecutor._observe_scope)
    assert "attest_native_query" not in source
    assert "_attest_scope" not in source
    assert "observe_native_query_material" in observe_source
    assert execute_source.index("mark_executed(") < execute_source.index(
        "_observe_scope("
    )


def test_r5_historical_dmp_dec_0048_path_executes_and_seals_without_p13():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    bridge = P13RejectingButDatasetLegalBridge(
        p13_detail="P13 must not be touched by historical native-direct execution"
    )
    binding = subjects.binding_for(principal=principal(), session=session)
    native_subject_ref = f"metabase-user:{binding.metabase_user_id}"

    store.mark_execution_started(
        link.id,
        native_subject_ref=native_subject_ref,
    )
    assert store.execution_link(link.id).status == "EXECUTION_STARTED"

    observed = bridge.execute_dataset(query)
    assert observed.query_fingerprint == link.native_query_fingerprint
    result = ExecutionResultSnapshot(
        payload=observed.payload,
        row_count=1,
    )
    runtime = executor._runtime_identity(
        raw=bridge.engine_identity(),
        database_id=observed.payload["database_id"],
    )
    executed_at = STAMP
    store.mark_executed(
        link.id,
        native_subject_ref=native_subject_ref,
        runtime_identity=runtime.model_dump(mode="json"),
        result_payload=result.payload,
        result_hash=result.result_hash,
        executed_at=executed_at,
    )

    receipt = DimaQueryReceiptSealer.seal_research_execution(
        authority_id=session.authority_id,
        research_session_id=session.session_id,
        obligation_ids=("g1",),
        tenant_binding=session.tenant_binding,
        principal_subject=session.principal_subject,
        roles=tuple(sorted(principal().roles)),
        native_subject_ref=native_subject_ref,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query_provenance_ref=f"research-execution-link:{link.id}:query",
        native_result_provenance_ref=f"research-execution-link:{link.id}:result",
        query_fingerprint=link.native_query_fingerprint,
        semantic_context_version=session.context_version,
        runtime=runtime,
        result=result,
        event=ExecutionEventIdentity(
            execution_id=f"native-dataset:{link.id}",
            executed_at=executed_at,
        ),
    )

    persisted = store.execution_link(link.id)
    assert persisted.status == "EXECUTED"
    assert persisted.native_result_json is not None
    assert persisted.runtime_identity_json is not None
    assert receipt.authority_kind == "research_material"
    assert receipt.canonical_query_fingerprint == link.native_query_fingerprint
    assert receipt.native_subject_ref == native_subject_ref
    assert bridge.calls == [query]
    assert bridge.attestation_calls == []


class NativeContractBridge(MaterialBridge):
    """Provider-free double exposing only execution + R5 material observation."""


def test_r5_material_binding_uses_governed_stable_ids_not_private_metadata():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    bridge = NativeContractBridge()

    outcome = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=bridge,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )

    assert outcome.attestation_id is None
    assert outcome.evidence.verified
    assert bridge.calls == [query]
    assert bridge.attestation_calls == []
    assert len(bridge.material_observation_calls) == 1
    assert not hasattr(bridge, "table_metadata")
    assert not hasattr(bridge, "field_metadata")


def rich_material_contract():
    return scope_module.AnalyticalRequestContract(
        authority_id="arc-r5-negative",
        request_ref="r5-negative",
        semantic_context_version=CONTEXT,
        scope_identity=scope_module.AnalyticalScopeIdentity(
            lineage_id="scope-line-r5",
            version_id="scope_v2",
        ),
        metric_refs=("metric.downtime",),
        dimension_refs=("dimension.department",),
        filters=(
            scope_module.AnalyticalFilterInvariant(
                semantic_ref="entity.assembly",
                source_candidate_id="entity.assembly",
                dimension_name="Department",
                value="Assembly",
            ),
        ),
        period=scope_module.AnalyticalPeriodInvariant(
            kind="explicit_half_open",
            time_dimension="time.event_date",
            start="2026-06-01",
            end="2026-07-01",
        ),
        ranking=scope_module.AnalyticalRankingInvariant(
            measure="metric.downtime",
            direction="desc",
            limit=5,
        ),
        grain_constraints=("dimension.department",),
    )


def rich_material_bindings():
    return {
        "metric.downtime": scope_module.NativeMaterialBinding(
            candidate_id="metric.downtime",
            candidate_kind="metric",
            database_id=1,
            table_id=10,
            metric_id=501,
            metric_entity_id="metric-downtime-v1",
        ),
        "dimension.department": scope_module.NativeMaterialBinding(
            candidate_id="dimension.department",
            candidate_kind="dimension",
            database_id=1,
            table_id=10,
            field_id=20,
        ),
        "entity.assembly": scope_module.NativeMaterialBinding(
            candidate_id="entity.assembly",
            candidate_kind="entity_value",
            database_id=1,
            table_id=10,
            field_id=20,
        ),
        "time.event_date": scope_module.NativeMaterialBinding(
            candidate_id="time.event_date",
            candidate_kind="dimension",
            database_id=1,
            table_id=10,
            field_id=30,
        ),
    }


def rich_material_observation(**updates):
    payload = {
        "schema_version": "dima_native_material_observation_v1",
        "conversation_id": "00000000-0000-4000-8000-000000000778",
        "native_query_id": "native-query-rich",
        "assistant_message_id": 1,
        "tool_call_id": "tool-rich",
        "query_fingerprint": "a" * 64,
        "authenticated_metabase_subject": 7,
        "database_id": 1,
        "runtime_identity": identity_payload(),
        "native_metrics": [
            {
                "stage_number": 0,
                "aggregation_index": 0,
                "metabase_metric_id": 501,
                "metabase_metric_entity_id": "metric-downtime-v1",
            }
        ],
        "dimensions": [
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
        "filters": [
            {
                "stage_number": 0,
                "operator": "=",
                "values": ["Assembly"],
                "field_id": 20,
                "table_id": 10,
            }
        ],
        "temporal_scopes": [
            {
                "time_field_id": 30,
                "table_id": 10,
                "lower_bound": "2026-06-01",
                "lower_inclusive": True,
                "upper_bound": "2026-07-01",
                "upper_inclusive": False,
            }
        ],
        "ranking": [
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "metric",
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-downtime-v1",
                },
                "direction": "desc",
                "limit": 5,
                "basis": "level",
            }
        ],
    }
    payload.update(updates)
    return NativeMaterialObservation.model_validate(payload)


def assert_rich_material(observation):
    _, session, _, _ = session_and_link(db_engine())
    return scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=rich_material_contract(),
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )



@pytest.mark.parametrize(
    ("lower_bound", "lower_inclusive", "upper_bound", "upper_inclusive"),
    (
        ("2026-06-01", True, "2026-06-30", True),
        ("2026-05-31", False, "2026-07-01", False),
    ),
)
def test_r5_material_date_scope_accepts_semantically_equivalent_half_open_bounds(
    lower_bound,
    lower_inclusive,
    upper_bound,
    upper_inclusive,
):
    observation = rich_material_observation(
        temporal_scopes=[
            {
                "time_field_id": 30,
                "table_id": 10,
                "lower_bound": lower_bound,
                "lower_inclusive": lower_inclusive,
                "upper_bound": upper_bound,
                "upper_inclusive": upper_inclusive,
            }
        ]
    )

    observed = assert_rich_material(observation)

    assert observed.scope_identity.version_id == "scope_v2"


def assert_rich_material_with_period(
    observation,
    *,
    start: str,
    end: str,
):
    _, session, _, _ = session_and_link(db_engine())
    contract = rich_material_contract().model_copy(
        update={
            "period": scope_module.AnalyticalPeriodInvariant(
                kind="explicit_half_open",
                time_dimension="time.event_date",
                start=start,
                end=end,
            )
        }
    )
    return scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=contract,
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )


@pytest.mark.parametrize(
    ("start", "end"),
    (
        ("2026-06-01T00:00:00", "2026-07-01T00:00:00"),
        ("2026-06-01T00:00:00Z", "2026-07-01T00:00:00Z"),
    ),
)
def test_r5_material_date_scope_accepts_midnight_datetime_calendar_boundaries(
    start,
    end,
):
    observed = assert_rich_material_with_period(
        rich_material_observation(),
        start=start,
        end=end,
    )

    assert observed.scope_identity.version_id == "scope_v2"


@pytest.mark.parametrize(
    ("start", "end"),
    (
        ("2026-06-01T00:00:01", "2026-07-01T00:00:00"),
        ("2026-06-01T00:00:00+03:00", "2026-07-01T00:00:00+03:00"),
    ),
)
def test_r5_material_date_scope_rejects_non_calendar_datetime_boundaries(
    start,
    end,
):
    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        assert_rich_material_with_period(
            rich_material_observation(),
            start=start,
            end=end,
        )

    assert exc.value.code == "R1_NATIVE_TIME_SCOPE_MISMATCH"
    assert exc.value.last_valid_boundary == "dima.material.compile"
    assert exc.value.first_invalid_boundary == "dima.native.observe"


@pytest.mark.parametrize(
    ("lower_bound", "lower_inclusive", "upper_bound", "upper_inclusive"),
    (
        ("2026-06-02", True, "2026-07-01", False),
        ("2026-06-01", True, "2026-06-29", True),
        ("2026-05-31", True, "2026-07-01", False),
        ("2026-06-01", True, "2026-07-01", True),
    ),
)
def test_r5_material_date_scope_rejects_non_equivalent_bounds(
    lower_bound,
    lower_inclusive,
    upper_bound,
    upper_inclusive,
):
    observation = rich_material_observation(
        temporal_scopes=[
            {
                "time_field_id": 30,
                "table_id": 10,
                "lower_bound": lower_bound,
                "lower_inclusive": lower_inclusive,
                "upper_bound": upper_bound,
                "upper_inclusive": upper_inclusive,
            }
        ]
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        assert_rich_material(observation)

    assert exc.value.code == "R1_NATIVE_TIME_SCOPE_MISMATCH"
    assert exc.value.last_valid_boundary == "dima.material.compile"
    assert exc.value.first_invalid_boundary == "dima.native.observe"
    assert exc.value.expected_fingerprint
    assert exc.value.observed_fingerprint
    assert exc.value.expected_fingerprint != exc.value.observed_fingerprint
    assert "expected_temporal_scope=" in exc.value.detail
    assert "observed_temporal_scope=" in exc.value.detail
    assert lower_bound in exc.value.detail
    assert upper_bound in exc.value.detail


def test_r5_material_semantics_matching_stable_ids_are_accepted():
    observed = assert_rich_material(rich_material_observation())
    assert observed.scope_identity.version_id == "scope_v2"
    assert observed.metric_refs == ("metric.downtime",)


def test_r5_unranked_material_allows_non_limiting_presentation_ordering():
    _, session, _, _ = session_and_link(db_engine())
    contract = rich_material_contract().model_copy(update={"ranking": None})
    observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "field",
                    "field_id": 30,
                    "table_id": 10,
                },
                "direction": "asc",
                "limit": None,
                "basis": "level",
            },
            {
                "stage_number": 0,
                "order_index": 1,
                "target": {
                    "kind": "field",
                    "field_id": 20,
                    "table_id": 10,
                },
                "direction": "asc",
                "limit": None,
                "basis": "level",
            },
        ]
    )

    observed = scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=contract,
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.ranking is None



def _change_material_contract():
    return rich_material_contract().model_copy(
        update={
            "ranking": None,
            "temporal_observation": (
                scope_module.AnalyticalTemporalObservationInvariant(
                    kind="change",
                    time_dimension="time.event_date",
                    minimum_distinct_values=2,
                )
            ),
        }
    )


def test_change_material_requires_governed_time_breakout() -> None:
    _, session, _, _ = session_and_link(db_engine())

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module.assert_material_native_scope(
            session=session,
            obligation_id="g1",
            contract=_change_material_contract(),
            observation=rich_material_observation(ranking=[]),
            bindings=rich_material_bindings(),
            expected_engine=expected_identity(),
            expected_metabase_subject=7,
        )

    assert exc.value.code == "R1_NATIVE_DIMENSION_SCOPE_MISMATCH"


def test_change_material_accepts_governed_time_breakout() -> None:
    _, session, _, _ = session_and_link(db_engine())
    observation = rich_material_observation(
        ranking=[],
        dimensions=[
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 30,
                "table_id": 10,
                "temporal_grain": "month",
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
    )

    observed = scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=_change_material_contract(),
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.temporal_observation is not None
    assert observed.temporal_observation.kind == "change"


def test_r5_bounded_period_allows_same_governed_time_field_as_optional_breakout():
    _, session, _, _ = session_and_link(db_engine())
    observation = rich_material_observation(
        dimensions=[
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 30,
                "table_id": 10,
                "temporal_grain": "month",
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ]
    )

    observed = scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=rich_material_contract(),
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.dimension_refs == ("dimension.department",)


def _entity_filtered_material_contract():
    return rich_material_contract().model_copy(
        update={
            "dimension_refs": (),
            "grain_constraints": (),
            "ranking": None,
        }
    )


def test_entity_equality_filter_allows_same_governed_field_as_redundant_breakout():
    """Exact accepted equality fixes scope; repeating that field cannot broaden it."""
    _, session, _, _ = session_and_link(db_engine())
    observation = rich_material_observation(ranking=[])

    observed = scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=_entity_filtered_material_contract(),
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.dimension_refs == ()
    assert observed.filters[0].value == "Assembly"


def test_entity_equality_filter_does_not_require_redundant_breakout():
    _, session, _, _ = session_and_link(db_engine())
    observation = rich_material_observation(
        ranking=[],
        dimensions=[
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
    )

    observed = scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=_entity_filtered_material_contract(),
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.dimension_refs == ()



def test_filtered_dimension_in_contract_is_not_required_as_redundant_breakout():
    _, session, _, _ = session_and_link(db_engine())
    contract = rich_material_contract().model_copy(
        update={
            "dimension_refs": (
                "dimension.department",
                "time.event_date",
            ),
            "grain_constraints": (
                "dimension.department",
                "time.event_date",
            ),
            "ranking": None,
            "temporal_observation": (
                scope_module.AnalyticalTemporalObservationInvariant(
                    kind="change",
                    time_dimension="time.event_date",
                    minimum_distinct_values=2,
                )
            ),
        }
    )
    observation = rich_material_observation(
        ranking=[],
        dimensions=[
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 30,
                "table_id": 10,
                "temporal_grain": "month",
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
    )

    observed = scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=contract,
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.dimension_refs == (
        "dimension.department",
        "time.event_date",
    )


def test_filtered_dimension_does_not_hide_an_unfiltered_required_breakout():
    _, session, _, _ = session_and_link(db_engine())
    bindings = {
        **rich_material_bindings(),
        "dimension.machine": scope_module.NativeMaterialBinding(
            candidate_id="dimension.machine",
            candidate_kind="dimension",
            database_id=1,
            table_id=10,
            field_id=40,
        ),
    }
    contract = rich_material_contract().model_copy(
        update={
            "dimension_refs": (
                "dimension.department",
                "dimension.machine",
                "time.event_date",
            ),
            "grain_constraints": (
                "dimension.department",
                "dimension.machine",
                "time.event_date",
            ),
            "ranking": None,
            "temporal_observation": (
                scope_module.AnalyticalTemporalObservationInvariant(
                    kind="change",
                    time_dimension="time.event_date",
                    minimum_distinct_values=2,
                )
            ),
        }
    )
    observation = rich_material_observation(
        ranking=[],
        dimensions=[
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 30,
                "table_id": 10,
                "temporal_grain": "month",
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module.assert_material_native_scope(
            session=session,
            obligation_id="g1",
            contract=contract,
            observation=observation,
            bindings=bindings,
            expected_engine=expected_identity(),
            expected_metabase_subject=7,
        )

    assert exc.value.code == "R1_NATIVE_DIMENSION_SCOPE_MISMATCH"


def test_entity_equality_filter_still_rejects_unaccepted_extra_breakout():
    _, session, _, _ = session_and_link(db_engine())
    bindings = {
        **rich_material_bindings(),
        "dimension.machine": scope_module.NativeMaterialBinding(
            candidate_id="dimension.machine",
            candidate_kind="dimension",
            database_id=1,
            table_id=10,
            field_id=40,
        ),
    }
    observation = rich_material_observation(
        ranking=[],
        dimensions=[
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 40,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module.assert_material_native_scope(
            session=session,
            obligation_id="g1",
            contract=_entity_filtered_material_contract(),
            observation=observation,
            bindings=bindings,
            expected_engine=expected_identity(),
            expected_metabase_subject=7,
        )

    assert exc.value.code == "R1_NATIVE_DIMENSION_SCOPE_MISMATCH"



def test_t3_dimension_mismatch_receipt_exposes_required_allowed_and_observed_breakouts():
    """Provider-free family reproducer for live 36909399128.

    The live artifact proved the DIMENSION_SCOPE family but did not preserve the
    observed semantic shape. This fixture recreates the same governed surface:
    exact department equality + bounded time, while native material introduces
    an unrelated machine breakout. The boundary receipt must make the first
    wrong transition diagnosable without prompt/query text.
    """
    _, session, _, _ = session_and_link(db_engine())
    bindings = {
        **rich_material_bindings(),
        "dimension.machine": scope_module.NativeMaterialBinding(
            candidate_id="dimension.machine",
            candidate_kind="dimension",
            database_id=1,
            table_id=10,
            field_id=40,
        ),
    }
    contract = _entity_filtered_material_contract()
    observation = rich_material_observation(
        ranking=[],
        dimensions=[
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 40,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 30,
                "table_id": 10,
                "temporal_grain": "month",
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module.assert_material_native_scope(
            session=session,
            obligation_id="g1",
            contract=contract,
            observation=observation,
            bindings=bindings,
            expected_engine=expected_identity(),
            expected_metabase_subject=7,
        )

    error = exc.value
    assert error.code == "R1_NATIVE_DIMENSION_SCOPE_MISMATCH"
    assert error.last_valid_boundary == "dima.material.compile"
    assert error.first_invalid_boundary == "dima.native.observe"
    assert error.scope_fingerprint == contract.scope_fingerprint
    assert error.material_fingerprint == contract.material_fingerprint
    assert error.expected_semantic_shape == {
        "axis": "DIMENSION",
        "required_breakouts": [],
        "allowed_breakouts": [
            "dimension.department",
            "time.event_date",
        ],
    }
    assert error.observed_semantic_shape == {
        "axis": "DIMENSION",
        "observed_breakouts": [
            "dimension.department",
            "dimension.machine",
            "time.event_date",
        ],
    }
    assert error.expected_fingerprint
    assert error.observed_fingerprint
    assert error.expected_fingerprint != error.observed_fingerprint


def test_change_material_allows_filtered_field_but_still_requires_time_breakout():
    _, session, _, _ = session_and_link(db_engine())
    contract = _entity_filtered_material_contract().model_copy(
        update={
            "temporal_observation": (
                scope_module.AnalyticalTemporalObservationInvariant(
                    kind="change",
                    time_dimension="time.event_date",
                    minimum_distinct_values=2,
                )
            ),
        }
    )
    observation = rich_material_observation(
        ranking=[],
        dimensions=[
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "breakout",
                "field_id": 30,
                "table_id": 10,
                "temporal_grain": "month",
            },
            {
                "stage_number": 0,
                "role": "filter",
                "field_id": 20,
                "table_id": 10,
            },
            {
                "stage_number": 0,
                "role": "temporal",
                "field_id": 30,
                "table_id": 10,
            },
        ],
    )

    observed = scope_module.assert_material_native_scope(
        session=session,
        obligation_id="g1",
        contract=contract,
        observation=observation,
        bindings=rich_material_bindings(),
        expected_engine=expected_identity(),
        expected_metabase_subject=7,
    )

    assert observed.temporal_observation is not None


def test_r5_unranked_material_still_blocks_unaccepted_row_limiting_order():
    _, session, _, _ = session_and_link(db_engine())
    contract = rich_material_contract().model_copy(update={"ranking": None})
    observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "field",
                    "field_id": 20,
                    "table_id": 10,
                },
                "direction": "desc",
                "limit": 2,
                "basis": "level",
            },
        ]
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module.assert_material_native_scope(
            session=session,
            obligation_id="g1",
            contract=contract,
            observation=observation,
            bindings=rich_material_bindings(),
            expected_engine=expected_identity(),
            expected_metabase_subject=7,
        )

    assert exc.value.code == "R1_NATIVE_RANKING_SCOPE_MISMATCH"


# Provider-free A3 RCA: dima.10 ranking basis must survive transport unchanged.
# Candidate verification: exact dima.10 basis is now typed and admission-checked.
# Verification rerun uses explicit dima.10 basis on every ranking fixture.
def _change_ranking_contract():
    return rich_material_contract().model_copy(
        update={
            "period": None,
            "comparison": scope_module.AnalyticalComparisonInvariant(
                mode="explicit_periods",
                reference_period=scope_module.AnalyticalPeriodInvariant(
                    kind="explicit_half_open",
                    time_dimension="time.event_date",
                    start="2026-05-01",
                    end="2026-06-01",
                ),
                base_period=scope_module.AnalyticalPeriodInvariant(
                    kind="explicit_half_open",
                    time_dimension="time.event_date",
                    start="2026-06-01",
                    end="2026-07-01",
                ),
            ),
            "ranking": scope_module.AnalyticalRankingInvariant(
                measure="metric.downtime",
                direction="desc",
                limit=5,
                basis=scope_module.RankingBasis.CHANGE,
            ),
        }
    )


def test_dima10_material_transport_preserves_observed_change_ranking_basis() -> None:
    observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "metric",
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-downtime-v1",
                },
                "direction": "desc",
                "limit": 5,
                "basis": "change",
            }
        ]
    )

    assert observation.ranking[0].basis == "change"


def test_dima10_observed_change_basis_satisfies_typed_change_ranking() -> None:
    observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "metric",
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-downtime-v1",
                },
                "direction": "desc",
                "limit": 5,
                "basis": "change",
            }
        ]
    )

    scope_module._assert_material_ranking_scope(
        _change_ranking_contract(),
        observation,
        rich_material_bindings(),
    )


def test_dima10_level_basis_cannot_satisfy_typed_change_ranking() -> None:
    observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "metric",
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-downtime-v1",
                },
                "direction": "desc",
                "limit": 5,
                "basis": "level",
            }
        ]
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module._assert_material_ranking_scope(
            _change_ranking_contract(),
            observation,
            rich_material_bindings(),
        )
    assert exc.value.code == "R1_NATIVE_RANKING_BASIS_MISMATCH"


@pytest.mark.parametrize(
    ("updates", "code"),
    (
        ({"temporal_scopes": []}, "R1_NATIVE_TIME_SCOPE_MISMATCH"),
        ({"filters": []}, "R1_NATIVE_FILTER_SCOPE_MISMATCH"),
        (
            {
                "native_metrics": [
                    {
                        "stage_number": 0,
                        "aggregation_index": 0,
                        "metabase_metric_id": 502,
                        "metabase_metric_entity_id": "metric-faults-v1",
                    }
                ]
            },
            "R1_NATIVE_METRIC_IDENTITY_MISMATCH",
        ),
        (
            {
                "dimensions": [
                    {
                        "stage_number": 0,
                        "role": "breakout",
                        "field_id": 21,
                        "table_id": 10,
                    }
                ]
            },
            "R1_NATIVE_DIMENSION_SCOPE_MISMATCH",
        ),
        (
            {
                "ranking": [
                    {
                        "stage_number": 0,
                        "order_index": 0,
                        "target": {
                            "kind": "metric",
                            "metabase_metric_id": 502,
                            "metabase_metric_entity_id": "metric-changeover-v1",
                        },
                        "direction": "desc",
                        "limit": 5,
                        "basis": "level",
                    }
                ]
            },
            "R1_NATIVE_RANKING_SCOPE_MISMATCH",
        ),
        (
            {
                "ranking": [
                    {
                        "stage_number": 0,
                        "order_index": 0,
                        "target": {
                            "kind": "metric",
                            "metabase_metric_id": 501,
                            "metabase_metric_entity_id": "metric-downtime-v1",
                        },
                        "direction": "asc",
                        "limit": 5,
                        "basis": "level",
                    }
                ]
            },
            "R1_NATIVE_RANKING_SCOPE_MISMATCH",
        ),
        (
            {
                "ranking": [
                    {
                        "stage_number": 0,
                        "order_index": 0,
                        "target": {
                            "kind": "metric",
                            "metabase_metric_id": 501,
                            "metabase_metric_entity_id": "metric-downtime-v1",
                        },
                        "direction": "desc",
                        "limit": 10,
                        "basis": "level",
                    }
                ]
            },
            "R1_NATIVE_RANKING_SCOPE_MISMATCH",
        ),
        ({"authenticated_metabase_subject": 8}, "R1_NATIVE_SUBJECT_MISMATCH"),
    ),
)
def test_r5_material_semantic_drift_blocks_verified_evidence(updates, code):
    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        assert_rich_material(rich_material_observation(**updates))
    assert exc.value.code == code


@pytest.mark.parametrize(
    ("identity_kind", "code"),
    (
        ("tenant", "P14_NATIVE_TENANT_MISMATCH"),
        ("principal", "P14_NATIVE_PRINCIPAL_MISMATCH"),
    ),
)
def test_r5_wrong_dima_tenant_or_principal_blocks_before_native_work(
    identity_kind, code
):
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    if identity_kind == "tenant":
        bad_principal = Principal(
            user_id=str(USER),
            tenant_id="00000000-0000-4000-8000-000000000799",
            roles=["analyst"],
            tenant_slug="wrong-tenant",
        )
    else:
        bad_principal = Principal(
            user_id="00000000-0000-4000-8000-000000000798",
            tenant_id=str(TENANT),
            roles=["analyst"],
            tenant_slug="native-direct",
        )
    bridge = MaterialBridge(fail_on_execute=True)

    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor.execute(
            principal=bad_principal,
            session=session,
            obligation_id="g1",
            bridge=bridge,
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            native_query=query,
            query_fingerprint=link.native_query_fingerprint,
            execution_link_id=link.id,
        )

    assert exc.value.code == code
    assert bridge.calls == []
    assert bridge.material_observation_calls == []
    assert store.execution_link(link.id).status == "CANDIDATE_CAPTURED"


def test_r5_material_wrong_engine_blocks_verified_evidence():
    runtime = identity_payload()
    runtime["revision_sha"] = "f" * 40
    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        assert_rich_material(rich_material_observation(runtime_identity=runtime))
    assert exc.value.code == "R1_NATIVE_ENGINE_IDENTITY_MISMATCH"


def test_r5_material_observation_fingerprint_is_separate_exact_provenance_domain():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    material_fingerprint = "0" * 64
    bridge = MaterialBridge(
        observation_update={"query_fingerprint": material_fingerprint}
    )

    outcome = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=bridge,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )

    # Raw query A remains exact execution provenance.
    assert outcome.receipt.canonical_query_fingerprint == h(query)
    # The engine's persisted/Lib occurrence fingerprint is retained separately.
    assert outcome.evidence.payload["observed_query_fingerprint"] == material_fingerprint
    assert outcome.evidence.verified
    assert store.execution_link(link.id).status == "EXECUTED"


class TamperedExecutionFingerprintBridge(MaterialBridge):
    def execute_dataset(self, query):
        observed = super().execute_dataset(query)
        return observed.model_copy(update={"query_fingerprint": "0" * 64})


def test_r5_raw_execution_query_fingerprint_mismatch_still_fails_closed():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )

    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor.execute(
            principal=principal(),
            session=session,
            obligation_id="g1",
            bridge=TamperedExecutionFingerprintBridge(),
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            native_query=query,
            query_fingerprint=link.native_query_fingerprint,
            execution_link_id=link.id,
        )

    assert exc.value.code == "P14_NATIVE_QUERY_FINGERPRINT_MISMATCH"
    assert store.execution_link(link.id).status == "EXECUTION_STARTED"


@pytest.mark.parametrize(
    "observation_update",
    (
        {"conversation_id": "00000000-0000-4000-8000-000000000999"},
        {"native_query_id": "another-native-query"},
    ),
)
def test_r5_material_occurrence_locator_mismatch_still_blocks_verified_evidence(
    observation_update,
):
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )

    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor.execute(
            principal=principal(),
            session=session,
            obligation_id="g1",
            bridge=MaterialBridge(observation_update=observation_update),
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            native_query=query,
            query_fingerprint=link.native_query_fingerprint,
            execution_link_id=link.id,
        )

    assert exc.value.code == "R1_NATIVE_OCCURRENCE_SCOPE_MISMATCH"
    assert store.execution_link(link.id).status == "EXECUTED"


def test_r5_stale_scope_occurrence_cannot_cross_research_session_identity():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    stale = session.model_copy(update={"session_id": "rs_stale_scope_v1"})
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor.execute(
            principal=principal(),
            session=stale,
            obligation_id="g1",
            bridge=MaterialBridge(),
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            native_query=query,
            query_fingerprint=link.native_query_fingerprint,
            execution_link_id=link.id,
        )
    assert exc.value.code == "P14_NATIVE_OBLIGATION_CORRELATION_MISMATCH"


def test_new_p14_binding_timestamp_is_timezone_aware_and_metadata_is_not_permission_truth():
    engine = db_engine()
    seed(engine)
    with Session(engine) as db:
        binding = db.exec(select(NativeSubjectBinding)).one()
        assert binding.created_at.tzinfo is not None
        assert binding.updated_at.tzinfo is not None
        assert binding.security_profile == "legacy-metadata"
        assert binding.policy_version == "legacy-metadata"


def test_subject_provider_correlates_exact_user_and_rejects_wrong_admin_or_missing_session(monkeypatch):
    engine = db_engine()
    seed(engine)
    store, session, _, _ = session_and_link(engine)
    del store
    state = {"id": 7, "is_superuser": False}

    class FakeBridge:
        def __init__(self, **kwargs):
            assert kwargs["session_token"] == "principal-session"

        def current_user(self):
            return dict(state)

        def engine_identity(self):
            return identity_payload()

        def close(self):
            pass

    monkeypatch.setattr(gateway_module, "NativeEngineBridge", FakeBridge)
    provider = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )

    with provider.open(
        principal=principal(),
        session=session,
        native_session_token="principal-session",
    ):
        pass

    state["id"] = 8
    with pytest.raises(ResearchMaterialLimitation) as wrong:
        with provider.open(
            principal=principal(),
            session=session,
            native_session_token="principal-session",
        ):
            pass
    assert wrong.value.code == "P14_NATIVE_SUBJECT_MISMATCH"

    state.update(id=7, is_superuser=True)
    with pytest.raises(ResearchMaterialLimitation) as admin:
        with provider.open(
            principal=principal(),
            session=session,
            native_session_token="principal-session",
        ):
            pass
    assert admin.value.code == "P14_NATIVE_ADMIN_SESSION_FORBIDDEN"

    state.update(id=7, is_superuser=False)
    with pytest.raises(ResearchMaterialLimitation) as missing:
        with provider.open(
            principal=principal(),
            session=session,
            native_session_token=None,
        ):
            pass
    assert missing.value.code == "P14_NATIVE_SESSION_REQUIRED"


def test_direct_native_result_seals_one_research_receipt_without_resource_or_operator_authority():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    bridge = MaterialBridge()
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    outcome = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=bridge,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )

    assert bridge.calls == [query]
    assert outcome.receipt.authority_kind == "research_material"
    assert outcome.receipt.projection_hash is None
    assert outcome.receipt.resolved_intent_hash is None
    assert outcome.receipt.execution_access_fingerprint is None
    assert outcome.receipt.native_subject_ref == "metabase-user:7"
    assert outcome.receipt.native_query_id == "native-query-1"
    assert outcome.receipt.canonical_query_fingerprint == h(query)
    assert outcome.receipt.resource_entity_ids == ()
    assert outcome.attestation_id is None
    assert outcome.evidence.verified
    assert outcome.evidence.payload["material_observation_schema"] == (
        "dima_native_material_observation_v1"
    )
    assert outcome.evidence.payload["observed_query_fingerprint"] == h(query)
    assert outcome.evidence.payload["scope_identity"]["version_id"] == "scope_v1"
    assert bridge.attestation_calls == []

    updated = ResearchManager.admit_receipted_evidence(
        session,
        obligation_id="g1",
        receipt=outcome.receipt,
        evidence=outcome.evidence,
        satisfies_obligation=True,
    )
    assert updated.obligations[0].state == ObligationState.VERIFIED


def test_native_permission_denial_remains_native_failure():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor.execute(
            principal=principal(),
            session=session,
            obligation_id="g1",
            bridge=MaterialBridge(forbidden=True),
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            native_query=query,
            query_fingerprint=link.native_query_fingerprint,
            execution_link_id=link.id,
        )
    assert exc.value.code == "P14_NATIVE_DATASET_HTTP_403"
    assert "permissions" in exc.value.detail


def test_executed_occurrence_resumes_from_durable_result_without_second_dataset_call():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    first_bridge = MaterialBridge()
    first = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=first_bridge,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )
    persisted = store.execution_link(link.id)
    assert persisted.status == "EXECUTED"
    assert persisted.native_result_json is not None

    second_bridge = MaterialBridge(fail_on_execute=True)
    second = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=second_bridge,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )
    assert first.receipt.receipt_id == second.receipt.receipt_id
    assert first.receipt.result_hash == second.receipt.result_hash
    assert len(first_bridge.calls) == 1
    assert second_bridge.calls == []
    assert len(second_bridge.material_observation_calls) == 1


def test_observation_unavailable_preserves_executed_result_and_retry_does_not_reexecute():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    first_bridge = MaterialBridge(observation_error=True)

    with pytest.raises(ResearchMaterialObservationUnavailable) as exc:
        executor.execute(
            principal=principal(),
            session=session,
            obligation_id="g1",
            bridge=first_bridge,
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            native_query=query,
            query_fingerprint=link.native_query_fingerprint,
            execution_link_id=link.id,
        )
    assert exc.value.code == "R1_NATIVE_MATERIAL_OBSERVATION_UNAVAILABLE"
    persisted = store.execution_link(link.id)
    assert persisted.status == "EXECUTED"
    assert persisted.native_result_json is not None
    assert first_bridge.calls == [query]

    retry_session = ResearchManager.record_retryable_limitation(
        session,
        obligation_id="g1",
        code=exc.value.code,
        detail=exc.value.detail,
    )
    assert retry_session.obligations[0].state == ObligationState.DELEGATED

    second_bridge = MaterialBridge(fail_on_execute=True)
    outcome = executor.execute(
        principal=principal(),
        session=retry_session,
        obligation_id="g1",
        bridge=second_bridge,
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )
    assert outcome.evidence.verified
    assert second_bridge.calls == []
    assert len(second_bridge.material_observation_calls) == 1


def test_gateway_r5_has_no_p13_parser_or_second_planner_authority():
    source = inspect.getsource(gateway_module)
    for forbidden in (
        "AuthorizedExecutionArtifact",
        "ExecutionAccessSnapshotIssuer",
        "VerifiedExecutionSecurityFacts",
        "NativeResourceBindingProvider",
        "execute_native_query",
        "attest_native_query",
        "NativeAttestationEnvelope",
        "ResolvedAnalyticsIntent",
        "TemporalBindingEngine",
        "MetabaseProjectionCompiler",
        "MetabaseCanonicalizer",
        "sqlparse",
        "parse_mbql",
        "query_optimizer",
    ):
        assert forbidden not in source
    assert "observe_native_query_material" in source
    assert "execute_dataset" in source


def test_p14_runtime_defaults_match_certified_engine_lock_identity():
    from app.config import Settings

    fields = Settings.model_fields
    assert fields["metabase_engine_sha"].default == ENGINE_SHA
    assert fields["metabase_engine_upstream_sha"].default == UPSTREAM_SHA
    assert fields["metabase_engine_runtime_tag"].default == TAG
    assert fields["metabase_engine_image_digest"].default == DIGEST
    assert fields["metabase_engine_image_identity"].default == DIGEST
    assert fields["metabase_engine_build_identity"].default == BUILD


def test_p14_native_direct_transport_correctness_frozen_oracle_sentinel():
    rows = [
        ["Referans", 21],
        ["Mevcut Müşteri", 34],
        ["Saha Ziyareti", 22],
        ["Fuar", 22],
        ["Web", 27],
    ]
    assert channel_counts(rows) == FROZEN_BOYAHANE_CHANNEL_COUNTS


def test_execution_started_unknown_outcome_never_blind_retries_dataset():
    engine = db_engine()
    seed(engine)
    store, session, link, query = session_and_link(engine)
    store.mark_execution_started(
        link.id,
        native_subject_ref="metabase-user:7",
    )
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=store,
        expected_identity=expected_identity(),
    )
    bridge = MaterialBridge(fail_on_execute=True)

    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor.execute(
            principal=principal(),
            session=session,
            obligation_id="g1",
            bridge=bridge,
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            native_query=query,
            query_fingerprint=link.native_query_fingerprint,
            execution_link_id=link.id,
        )

    assert exc.value.code == "P14_NATIVE_EXECUTION_OUTCOME_UNKNOWN"
    assert bridge.calls == []
    assert store.execution_link(link.id).status == "EXECUTION_STARTED"



def test_change_material_requirement_projection_is_exact_and_planner_visible() -> None:
    contract = _change_ranking_contract()
    context = scope_module.native_request_context(contract)
    requirement = context["dima_material_requirement"]

    assert requirement["schema"] == "dima_material_requirement_v1"
    assert requirement["scope_version_id"] == contract.scope_identity.version_id
    assert requirement["material_fingerprint"] == contract.material_fingerprint
    assert requirement["metric_refs"] == ["metric.downtime"]
    assert requirement["required_metric_refs"] == ["metric.downtime"]
    assert requirement["required_breakout_refs"] == ["dimension.department"]
    assert requirement["required_temporal_dimension"] == "time.event_date"
    assert requirement["ranking"] == {
        "kind": "native_metric",
        "measure": "metric.downtime",
        "direction": "desc",
        "limit": 5,
        "basis": "change",
    }
    assert requirement["comparison"] == contract.comparison.model_dump(mode="json")

    message = ResearchManager.native_material_message(
        objective="symbolic period-over-period ranking",
        analytical_scope=contract,
    )
    marker = "[DIMA MATERIAL REQUIREMENT JSON]\n"
    assert marker in message
    encoded = message.split(marker, 1)[1].splitlines()[0]
    visible = json.loads(encoded)["dima_material_requirement"]
    assert visible == requirement


def test_dima10_missing_required_change_ranking_is_distinct_material_miss() -> None:
    observation = rich_material_observation(ranking=[])

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module._assert_material_ranking_scope(
            _change_ranking_contract(),
            observation,
            rich_material_bindings(),
        )

    assert exc.value.code == "R1_NATIVE_RANKING_REQUIRED_MISSING"
    assert exc.value.expected_semantic_shape["ranking"]["basis"] == "change"
    assert exc.value.observed_semantic_shape == {"ranking": []}


def test_dima10_wrong_direction_remains_nonrepairable_structural_mismatch() -> None:
    observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "metric",
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-downtime-v1",
                },
                "direction": "asc",
                "limit": 5,
                "basis": "change",
            }
        ]
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module._assert_material_ranking_scope(
            _change_ranking_contract(),
            observation,
            rich_material_bindings(),
        )

    assert exc.value.code == "R1_NATIVE_RANKING_SCOPE_MISMATCH"
    assert exc.value.expected_semantic_shape["ranking"]["direction"] == "desc"
    assert exc.value.observed_semantic_shape["ranking"][0]["direction"] == "asc"



def test_change_level_first_result_allows_one_repair_then_change_admits() -> None:
    from app.v3.research_material_repair import (
        MaterialRepairDisposition,
        decide_material_repair,
    )

    contract = _change_ranking_contract()
    level_observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "metric",
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-downtime-v1",
                },
                "direction": "desc",
                "limit": 5,
                "basis": "level",
            }
        ]
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as first:
        scope_module._assert_material_ranking_scope(
            contract,
            level_observation,
            rich_material_bindings(),
        )
    assert first.value.code == "R1_NATIVE_RANKING_BASIS_MISMATCH"

    decision = decide_material_repair(
        validation_code=first.value.code,
        validation_detail=first.value.detail,
        prior_repair_attempts=0,
        expected_semantic_shape=first.value.expected_semantic_shape,
        observed_semantic_shape=first.value.observed_semantic_shape,
    )
    assert decision.disposition == MaterialRepairDisposition.REPAIR
    assert decision.repair_attempt == 1

    repaired_observation = rich_material_observation(
        ranking=[
            {
                "stage_number": 0,
                "order_index": 0,
                "target": {
                    "kind": "metric",
                    "metabase_metric_id": 501,
                    "metabase_metric_entity_id": "metric-downtime-v1",
                },
                "direction": "desc",
                "limit": 5,
                "basis": "change",
            }
        ]
    )
    scope_module._assert_material_ranking_scope(
        contract,
        repaired_observation,
        rich_material_bindings(),
    )

    exhausted = decide_material_repair(
        validation_code="R1_NATIVE_RANKING_BASIS_MISMATCH",
        prior_repair_attempts=1,
    )
    assert exhausted.disposition == MaterialRepairDisposition.TERMINAL_LIMIT
