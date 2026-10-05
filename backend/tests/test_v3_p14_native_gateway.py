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
    NativeEngineBridgeError,
    NativeEngineEndpointError,
    NativeEngineTransportError,
)
from app.v3.substrate.metabase.native_models import (
    NativeEngineIdentity,
    NativeExactOccurrenceExecutionObservation,
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
        result_hash=h(parent_result),
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
        result_hash=h(parent_result),
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


def test_native_request_context_preloads_only_required_governed_resources():
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
        {"type": "metric", "id": 501},
    ]
    assert 20 not in {
        item.get("id")
        for item in enriched.context["user_is_viewing"]
    }
    assert enriched.message == prepared.request.message
    assert enriched.state == prepared.request.state
    assert enriched.history == prepared.request.history


def test_native_request_metric_anchor_is_idempotent_and_preserves_repair_feedback():
    engine = db_engine()
    seed(engine)
    store = ResearchSessionStore(engine)
    product = ResearchAskOrchestrator(store=store)
    session = product.start_from_brief(
        brief=brief(),
        request_ref="p14-native-repair-anchor-test",
        source_message_hash=hashlib.sha256(b"native repair anchor").hexdigest(),
        principal=principal(),
    )
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g1",
    )
    repair_feedback = {
        "schema": "dima_material_repair_feedback_v1",
        "validation_code": "R1_NATIVE_RANKING_BASIS_MISMATCH",
        "repair_attempt": 1,
    }
    request = prepared.request.model_copy(
        update={
            "context": {
                **prepared.request.context,
                "user_is_viewing": [{"type": "metric", "id": 501}],
                "dima_material_repair_feedback": repair_feedback,
            }
        }
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
        request=request,
    )

    assert enriched.context["user_is_viewing"] == [
        {"type": "metric", "id": 501},
    ]
    assert enriched.context["dima_material_repair_feedback"] == repair_feedback


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
        attestation_error=None,
    ):
        self.calls = []
        self.forbidden = forbidden
        self.fail_on_execute = fail_on_execute
        self.observation_error = observation_error
        self.observation_update = observation_update or {}
        self.attestation_error = attestation_error
        self.attestation_calls = []
        self.material_observation_calls = []
        self.call_order = []

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
        raise AssertionError("/api/dataset is not a canonical P14 execution path")

    def engine_identity(self):
        return identity_payload()

    def attest_native_query(self, *, conversation_id, native_query_id):
        self.call_order.append("attest")
        self.attestation_calls.append((conversation_id, native_query_id))
        if self.attestation_error is not None:
            raise self.attestation_error
        payload = attestation_payload(self._query())
        payload["manifest"]["native_conversation_id"] = str(conversation_id)
        payload["manifest"]["native_query_id"] = native_query_id
        return payload

    def observe_native_query_material(self, *, conversation_id, native_query_id):
        self.call_order.append("observe")
        self.material_observation_calls.append((conversation_id, native_query_id))
        if self.observation_error:
            if isinstance(self.observation_error, Exception):
                raise self.observation_error
            raise NativeEngineTransportError(
                "native material observation",
                "symbolic temporary observer unavailable",
            )
        payload = material_observation_payload(
            self._query(),
            conversation_id=conversation_id,
            native_query_id=native_query_id,
        )
        payload.update(self.observation_update)
        return NativeMaterialObservation.model_validate(payload)

    def execute_native_query(
        self,
        *,
        conversation_id,
        native_query_id,
        expected_pmbql_fingerprint,
        expected_attestation_id,
    ):
        self.call_order.append("execute")
        if self.fail_on_execute:
            raise AssertionError("exact native occurrence was executed twice")
        query = self._query()
        self.calls.append(query)
        if self.forbidden:
            raise NativeEngineEndpointError(
                operation="native exact-occurrence execution",
                status_code=403,
                error_code="NATIVE_QUERY_EXECUTION_PERMISSION_DENIED",
                detail="You do not have permissions to run this query.",
                payload={
                    "dima/error-code": "NATIVE_QUERY_EXECUTION_PERMISSION_DENIED"
                },
            )
        return NativeExactOccurrenceExecutionObservation(
            status_code=200,
            latency_ms=3,
            native_conversation_id=conversation_id,
            native_query_id=native_query_id,
            attestation_id=expected_attestation_id,
            executed_pmbql_fingerprint=expected_pmbql_fingerprint,
            runtime_identity=identity_payload(),
            payload={
                "status": "completed",
                "database_id": 1,
                "row_count": 1,
                "data": {"rows": [["Web", 4]], "cols": []},
            },
            attestation=self.attest_native_query(
                conversation_id=conversation_id,
                native_query_id=native_query_id,
            ),
        )


@pytest.mark.parametrize(
    "error_code",
    (
        "NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED",
        "NATIVE_METRIC_EXPANSION_UNSUPPORTED",
    ),
)
def test_attestation_422_is_deterministic_limitation_before_execution(error_code):
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
    bridge = MaterialBridge(
        attestation_error=NativeEngineEndpointError(
            operation="native attestation",
            status_code=422,
            error_code=error_code,
            detail="deterministic unsupported attestation shape",
            payload={"dima/error-code": error_code},
        )
    )

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

    assert exc.value.code == error_code
    assert "HTTP 422" in exc.value.detail
    assert bridge.calls == []
    assert bridge.material_observation_calls == []
    assert store.execution_link(link.id).status == "CANDIDATE_CAPTURED"


def test_p14_architecture_observes_before_exact_occurrence_execution():
    execute_source = inspect.getsource(NativeResearchMaterialExecutor.execute)
    observe_source = inspect.getsource(NativeResearchMaterialExecutor._observe_scope)
    attest_source = inspect.getsource(NativeResearchMaterialExecutor._attest_occurrence)

    assert "attest_native_query" in attest_source
    assert "observe_native_query_material" in observe_source
    assert "execute_native_query" in execute_source
    assert "execute_dataset" not in execute_source
    assert execute_source.index("_attest_occurrence(") < execute_source.index(
        "_observe_scope("
    )
    assert execute_source.index("_observe_scope(") < execute_source.index(
        "mark_execution_started("
    )
    assert execute_source.index("mark_execution_started(") < execute_source.index(
        "execute_native_query("
    )


def test_legacy_direct_dataset_path_is_not_canonical_p14():
    source = inspect.getsource(NativeResearchMaterialExecutor.execute)
    assert "execute_dataset" not in source
    assert "execute_native_query" in source
    assert "attest_native_query" not in source  # delegated to _attest_occurrence


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

    assert outcome.attestation_id == "att-p14-test"
    assert outcome.evidence.verified
    assert bridge.calls == [query]
    assert bridge.attestation_calls
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

    assert exc.value.code == "ANALYTICAL_V1_EXECUTION_RANKING_UNREPRESENTABLE"


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


def _span_change_ranking_contract():
    span = scope_module.AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension="time.event_date",
        start="2026-05-01",
        end="2026-07-01",
    )
    return rich_material_contract().model_copy(
        update={
            "period": span,
            "comparison": None,
            "temporal_change_frame": scope_module.AnalyticalTemporalChangeFrame(
                mode=scope_module.TemporalChangeFrameMode.SPAN,
                time_dimension="time.event_date",
                span_period=span,
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

    projected = scope_module._project_material_ranking_observation(
        observation,
        rich_material_bindings(),
    )
    assert projected is not None
    assert projected.measure == "metric.downtime"
    assert projected.basis == scope_module.RankingBasis.CHANGE


def test_dima10_level_basis_is_projected_and_rejected_only_by_canonical_verifier() -> None:
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

    projected = scope_module._project_material_ranking_observation(
        observation,
        rich_material_bindings(),
    )
    assert projected is not None
    assert projected.basis == scope_module.RankingBasis.LEVEL


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
    def execute_native_query(self, **kwargs):
        observed = super().execute_native_query(**kwargs)
        return observed.model_copy(
            update={"executed_pmbql_fingerprint": "0" * 64}
        )


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

    assert exc.value.code == "P14_NATIVE_EXECUTION_FINGERPRINT_MISMATCH"
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
    assert store.execution_link(link.id).status == "CANDIDATE_CAPTURED"


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
    assert outcome.attestation_id == "att-p14-test"
    assert outcome.evidence.verified
    assert outcome.evidence.payload["material_observation_schema"] == (
        "dima_native_material_observation_v1"
    )
    assert outcome.evidence.payload["observed_query_fingerprint"] == h(query)
    assert outcome.evidence.payload["scope_identity"]["version_id"] == "scope_v1"
    assert len(bridge.attestation_calls) == 2
    assert bridge.call_order[:3] == ["attest", "observe", "execute"]
    assert len(bridge.calls) == 1

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
    assert exc.value.code == "NATIVE_QUERY_EXECUTION_PERMISSION_DENIED"
    assert "HTTP 403" in exc.value.detail
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


def test_observation_not_ready_waits_before_execution_then_reuses_same_candidate():
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
    first_bridge = MaterialBridge(
        observation_error=NativeEngineEndpointError(
            operation="native material observation",
            status_code=404,
            error_code="NATIVE_QUERY_OCCURRENCE_NOT_FOUND",
            detail="producer occurrence is not visible yet",
            payload={"dima/error-code": "NATIVE_QUERY_OCCURRENCE_NOT_FOUND"},
        )
    )

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
    assert exc.value.code == "NATIVE_QUERY_OCCURRENCE_NOT_FOUND"
    persisted = store.execution_link(link.id)
    assert persisted.status == "CANDIDATE_CAPTURED"
    assert persisted.native_result_json is None
    assert first_bridge.calls == []
    assert first_bridge.call_order == ["attest", "observe"]

    retry_session = ResearchManager.record_retryable_limitation(
        session,
        obligation_id="g1",
        code=exc.value.code,
        detail=exc.value.detail,
    )
    assert retry_session.obligations[0].state == ObligationState.DELEGATED

    second_bridge = MaterialBridge()
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
    assert second_bridge.calls == [query]
    assert second_bridge.call_order[:3] == ["attest", "observe", "execute"]
    assert store.execution_link(link.id).status == "EXECUTED"


def test_observer_422_and_state_mismatch_are_deterministic_no_retry():
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

    for status, code in (
        (422, "NATIVE_MATERIAL_CHANGE_RANKING_UNPROVABLE"),
        (409, "NATIVE_QUERY_STATE_MISMATCH"),
    ):
        bridge = MaterialBridge(
            observation_error=NativeEngineEndpointError(
                operation="native material observation",
                status_code=status,
                error_code=code,
                detail="deterministic observer failure",
                payload={"dima/error-code": code},
            )
        )
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
        assert exc.value.code == code
        assert f"HTTP {status}" in exc.value.detail
        assert bridge.calls == []
        assert store.execution_link(link.id).status == "CANDIDATE_CAPTURED"


def test_gateway_p14_has_no_second_planner_or_direct_dataset_escape():
    source = inspect.getsource(gateway_module)
    for forbidden in (
        "AuthorizedExecutionArtifact",
        "ExecutionAccessSnapshotIssuer",
        "VerifiedExecutionSecurityFacts",
        "NativeResourceBindingProvider",
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
    assert "attest_native_query" in source
    assert "observe_native_query_material" in source
    assert "execute_native_query" in source
    assert "execute_dataset" not in inspect.getsource(
        NativeResearchMaterialExecutor.execute
    )


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


def test_execution_started_unknown_outcome_never_blind_retries_exact_execution():
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
    assert requirement["required_breakout_refs"] == [
        "dimension.department",
        "time.event_date",
    ]
    assert requirement["required_temporal_dimension"] == "time.event_date"
    assert requirement["ranking"] == {
        "kind": "native_metric",
        "measure": "metric.downtime",
        "direction": "desc",
        "limit": 5,
        "basis": "change",
    }
    assert requirement["comparison"] == contract.comparison.model_dump(mode="json")
    assert requirement["temporal_change_frame"] == {
        "mode": "PAIR",
        "time_dimension": "time.event_date",
        "span_period": None,
        "baseline_period": contract.comparison.reference_period.model_dump(mode="json"),
        "comparison_period": contract.comparison.base_period.model_dump(mode="json"),
    }
    assert requirement["change_semantics"] == {
        "frame_mode": "PAIR",
        "operation": "comparison_minus_baseline",
        "metric_ref": "metric.downtime",
        "entity_breakout_refs": ["dimension.department"],
        "time_dimension": "time.event_date",
        "baseline_period": contract.comparison.reference_period.model_dump(mode="json"),
        "comparison_period": contract.comparison.base_period.model_dump(mode="json"),
        "ranking_direction": "desc",
        "ranking_limit": 5,
    }

    message = ResearchManager.native_material_message(
        objective="symbolic period-over-period ranking",
        analytical_scope=contract,
    )
    marker = "[DIMA MATERIAL REQUIREMENT JSON]\n"
    assert marker in message
    encoded = message.split(marker, 1)[1].splitlines()[0]
    visible = json.loads(encoded)["dima_material_requirement"]
    assert visible == requirement
    assert "accepted PAIR change frame" in message
    assert "accepted baseline and comparison periods" in message
    assert "CHANGE material law" in message
    assert "rank by the governed CHANGE quantity" in message
    assert "do not order by the raw metric level" in message
    assert "dimension.department" in message
    lowered = message.lower()
    for forbidden in ("select ", "group by", "sum-where", "aggregation-options", "lib/uuid"):
        assert forbidden not in lowered


def test_span_change_material_requirement_is_typed_without_hidden_pair() -> None:
    contract = _span_change_ranking_contract()
    requirement = scope_module.native_material_requirement(contract)

    assert requirement["comparison"] is None
    assert requirement["period"] == contract.period.model_dump(mode="json")
    assert requirement["required_temporal_dimension"] == "time.event_date"
    assert requirement["temporal_change_frame"] == {
        "mode": "SPAN",
        "time_dimension": "time.event_date",
        "span_period": contract.period.model_dump(mode="json"),
        "baseline_period": None,
        "comparison_period": None,
    }
    assert requirement["change_semantics"] == {
        "frame_mode": "SPAN",
        "operation": "change_over_span",
        "metric_ref": "metric.downtime",
        "entity_breakout_refs": ["dimension.department"],
        "time_dimension": "time.event_date",
        "ranking_direction": "desc",
        "ranking_limit": 5,
        "span_period": contract.period.model_dump(mode="json"),
    }

    message = ResearchManager.native_material_message(
        objective="symbolic bounded deterioration ranking",
        analytical_scope=contract,
    )
    assert "accepted SPAN change frame" in message
    assert "do not invent hidden baseline/comparison roles" in message
    assert "Metabot-owned analytical realization" in message
    assert "do not order by the raw metric level" in message
    lowered = message.lower()
    for forbidden in ("select ", "group by", "sum-where", "aggregation-options", "lib/uuid"):
        assert forbidden not in lowered


def test_span_change_basis_mismatch_is_terminal_at_canonical_owner() -> None:
    from app.v3.research_material_repair import (
        MaterialRepairDisposition,
        decide_material_repair,
    )

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
    projected = scope_module._project_material_ranking_observation(
        observation,
        rich_material_bindings(),
    )
    assert projected is not None
    assert projected.basis == scope_module.RankingBasis.LEVEL

    decision = decide_material_repair(
        validation_code="ANALYTICAL_V1_RANKING_MISMATCH",
        validation_detail="ranking basis/metric/direction/top-k differs",
        prior_repair_attempts=0,
    )
    assert decision.disposition == MaterialRepairDisposition.TERMINAL_LIMIT
    assert decision.repair_attempt == 0


def test_dima10_missing_native_ranking_projects_none_for_canonical_verifier() -> None:
    observation = rich_material_observation(ranking=[])

    projected = scope_module._project_material_ranking_observation(
        observation,
        rich_material_bindings(),
    )

    assert projected is None


def test_dima10_nonrestrictive_field_order_projects_no_business_ranking() -> None:
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

    assert (
        scope_module._project_material_ranking_observation(
            observation,
            rich_material_bindings(),
        )
        is None
    )


def test_dima10_row_limiting_field_order_remains_nonrepairable_scope_mismatch() -> None:
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
                "limit": 5,
                "basis": "level",
            }
        ]
    )

    with pytest.raises(scope_module.ResearchAnalyticalScopeError) as exc:
        scope_module._project_material_ranking_observation(
            observation,
            rich_material_bindings(),
        )

    assert exc.value.code == "ANALYTICAL_V1_EXECUTION_RANKING_UNREPRESENTABLE"


def test_dima10_wrong_direction_is_preserved_for_canonical_verifier() -> None:
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

    projected = scope_module._project_material_ranking_observation(
        observation,
        rich_material_bindings(),
    )
    assert projected is not None
    assert projected.direction == "asc"
    assert projected.basis == scope_module.RankingBasis.CHANGE



def test_change_level_and_change_basis_are_projected_without_hidden_repair() -> None:
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
    level = scope_module._project_material_ranking_observation(
        level_observation,
        rich_material_bindings(),
    )
    assert level is not None
    assert level.basis == scope_module.RankingBasis.LEVEL

    change_observation = rich_material_observation(
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
    change = scope_module._project_material_ranking_observation(
        change_observation,
        rich_material_bindings(),
    )
    assert change is not None
    assert change.basis == scope_module.RankingBasis.CHANGE



def test_level_material_requirement_has_no_change_semantics() -> None:
    contract = _change_ranking_contract().model_copy(
        update={
            "ranking": scope_module.AnalyticalRankingInvariant(
                measure="metric.downtime",
                direction="desc",
                limit=5,
                basis=scope_module.RankingBasis.LEVEL,
            ),
            "temporal_observation": None,
        }
    )
    requirement = scope_module.native_material_requirement(contract)
    assert requirement["ranking"]["basis"] == "level"
    assert requirement["temporal_change_frame"] is None
    assert requirement["change_semantics"] is None


def test_canonical_ranking_mismatch_is_not_repaired_after_execution() -> None:
    from app.v3.research_material_repair import (
        MaterialRepairDisposition,
        decide_material_repair,
    )

    decision = decide_material_repair(
        validation_code="ANALYTICAL_V1_RANKING_MISMATCH",
        validation_detail="ranking basis/metric/direction/top-k differs",
        prior_repair_attempts=0,
    )

    assert decision.disposition == MaterialRepairDisposition.TERMINAL_LIMIT
    assert decision.repair_attempt == 0



# Phase-1A 30-case readiness: result dependency is execution-local FILTER authority.
def test_result_dependency_filter_only_loads_binding_from_accepted_scope() -> None:
    engine = db_engine()
    seed(engine)
    base_brief = brief()
    metric, dependency_dimension = base_brief.scope.semantic_refs
    child = ResearchQuestion(
        goal_id="g-child-filter-only",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect the selected governed channel without returning channel.",
        subject_refs=(metric,),
        related_refs=(),
        result_dependency=ResultSelectionDependency(
            source_goal_id="g-parent-ranking",
            dimension_semantic_id=dependency_dimension.candidate_id,
            selection="first_ranked_entity",
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    session = SimpleNamespace(
        session_id="rs-result-dependency-filter-only",
        context_version=CONTEXT,
        tenant_binding=f"id:{TENANT}",
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
        evidence_id="evidence-filter-only",
        receipt_id="receipt-filter-only",
        result_hash=h(parent_result),
    )

    class ParentStore:
        def verified_material_result(self, *, session_id, obligation_id):
            assert session_id == session.session_id
            assert obligation_id == "g-parent-ranking"
            return parent_link, parent_result

    executor = NativeResearchMaterialExecutor(
        subject_provider=SimpleNamespace(db_engine=engine),
        store=ParentStore(),
        expected_identity=expected_identity(),
    )
    base = AnalyticalRequestContract(
        authority_id="authority-filter-only",
        request_ref="request-filter-only",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-filter-only",
            version_id="scope_v1",
        ),
        scope_fingerprint=base_brief.scope_fingerprint,
        metric_refs=(metric.candidate_id,),
        dimension_refs=(),
    )

    resolution = executor.resolve_result_dependency(
        principal=principal(),
        session=session,
        obligation_id=child.goal_id,
        analytical_scope=base,
    )

    assert resolution is not None
    assert resolution.selected_value == "Web"
    assert resolution.contract.dimension_refs == ()
    assert resolution.contract.filters[-1].source_candidate_id == (
        dependency_dimension.candidate_id
    )
    assert resolution.contract.filters[-1].value == "Web"
    assert resolution.contract.scope_identity == base.scope_identity
    assert resolution.contract.scope_fingerprint == base.scope_fingerprint


def test_result_dependency_parent_empty_fails_closed() -> None:
    import app.v3.research_result_dependency as dependency_module

    base = AnalyticalRequestContract(
        authority_id="authority-parent-empty",
        request_ref="request-parent-empty",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-parent-empty",
            version_id="scope_v1",
        ),
        scope_fingerprint="c" * 64,
        metric_refs=("cand_sales_order_count",),
        dimension_refs=(),
    )
    with pytest.raises(dependency_module.ResultDependencyProjectionError) as exc:
        dependency_module.resolve_first_ranked_entity(
            base_contract=base,
            source_goal_id="g-parent",
            source_evidence_id="e-parent",
            source_receipt_id="r-parent",
            source_result_hash="d" * 64,
            dimension_semantic_id="cand_sales_order_channel",
            native_field_id=20,
            parent_result={
                "data": {
                    "cols": [{"id": 20, "field_ref": ["field", 20, None]}],
                    "rows": [],
                }
            },
        )
    assert exc.value.code == "R1_RESULT_DEPENDENCY_PARENT_EMPTY"


def test_result_dependency_missing_governed_column_fails_closed() -> None:
    import app.v3.research_result_dependency as dependency_module

    base = AnalyticalRequestContract(
        authority_id="authority-column-missing",
        request_ref="request-column-missing",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-column-missing",
            version_id="scope_v1",
        ),
        scope_fingerprint="e" * 64,
        metric_refs=("cand_sales_order_count",),
        dimension_refs=(),
    )
    with pytest.raises(dependency_module.ResultDependencyProjectionError) as exc:
        dependency_module.resolve_first_ranked_entity(
            base_contract=base,
            source_goal_id="g-parent",
            source_evidence_id="e-parent",
            source_receipt_id="r-parent",
            source_result_hash="f" * 64,
            dimension_semantic_id="cand_sales_order_channel",
            native_field_id=20,
            parent_result={
                "data": {
                    "cols": [{"id": 21, "field_ref": ["field", 21, None]}],
                    "rows": [["Web"]],
                }
            },
        )
    assert exc.value.code == "R1_RESULT_DEPENDENCY_DIMENSION_COLUMN_AMBIGUOUS"


def test_result_dependency_non_string_selected_value_fails_closed() -> None:
    import app.v3.research_result_dependency as dependency_module

    base = AnalyticalRequestContract(
        authority_id="authority-value-invalid",
        request_ref="request-value-invalid",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-value-invalid",
            version_id="scope_v1",
        ),
        scope_fingerprint="1" * 64,
        metric_refs=("cand_sales_order_count",),
        dimension_refs=(),
    )
    with pytest.raises(dependency_module.ResultDependencyProjectionError) as exc:
        dependency_module.resolve_first_ranked_entity(
            base_contract=base,
            source_goal_id="g-parent",
            source_evidence_id="e-parent",
            source_receipt_id="r-parent",
            source_result_hash="2" * 64,
            dimension_semantic_id="cand_sales_order_channel",
            native_field_id=20,
            parent_result={
                "data": {
                    "cols": [{"id": 20, "field_ref": ["field", 20, None]}],
                    "rows": [[123]],
                }
            },
        )
    assert exc.value.code == "R1_RESULT_DEPENDENCY_ENTITY_VALUE_INVALID"


def test_result_dependency_conflicting_child_filter_fails_closed() -> None:
    import app.v3.research_result_dependency as dependency_module

    base = AnalyticalRequestContract(
        authority_id="authority-filter-conflict",
        request_ref="request-filter-conflict",
        semantic_context_version=CONTEXT,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-filter-conflict",
            version_id="scope_v1",
        ),
        scope_fingerprint="3" * 64,
        metric_refs=("cand_sales_order_count",),
        dimension_refs=(),
        filters=(
            AnalyticalFilterInvariant(
                semantic_ref="accepted-filter",
                source_candidate_id="cand_sales_order_channel",
                dimension_name="Sales Order Channel",
                value="Direct",
            ),
        ),
    )
    with pytest.raises(dependency_module.ResultDependencyProjectionError) as exc:
        dependency_module.resolve_first_ranked_entity(
            base_contract=base,
            source_goal_id="g-parent",
            source_evidence_id="e-parent",
            source_receipt_id="r-parent",
            source_result_hash="4" * 64,
            dimension_semantic_id="cand_sales_order_channel",
            native_field_id=20,
            parent_result={
                "data": {
                    "cols": [{"id": 20, "field_ref": ["field", 20, None]}],
                    "rows": [["Web"]],
                }
            },
        )
    assert exc.value.code == "R1_RESULT_DEPENDENCY_SCOPE_CONFLICT"


@pytest.mark.parametrize("row_count", [0, 2])
def test_result_dependency_binding_cardinality_fails_closed(
    monkeypatch,
    row_count: int,
) -> None:
    base_brief = brief()
    _, dependency_dimension = base_brief.scope.semantic_refs
    session = SimpleNamespace(
        context_version=CONTEXT,
        tenant_binding=f"id:{TENANT}",
        accepted_brief=SimpleNamespace(scope=base_brief.scope),
    )

    class FakeRows:
        def all(self):
            return [SimpleNamespace()] * row_count

    class FakeDB:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def exec(self, _statement):
            return FakeRows()

    monkeypatch.setattr(gateway_module, "Session", lambda *_: FakeDB())
    executor = NativeResearchMaterialExecutor(
        subject_provider=SimpleNamespace(db_engine=object()),
        store=SimpleNamespace(),
        expected_identity=expected_identity(),
    )

    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor._material_bindings(
            principal=principal(),
            session=session,
            candidate_ids=(dependency_dimension.candidate_id,),
        )

    assert exc.value.code == "R1_NATIVE_RESOURCE_BINDING_MISSING"


def test_result_dependency_foreign_scope_binding_fails_closed() -> None:
    base_brief = brief()
    session = SimpleNamespace(
        context_version=CONTEXT,
        tenant_binding=f"id:{TENANT}",
        accepted_brief=SimpleNamespace(scope=base_brief.scope),
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=SimpleNamespace(db_engine=object()),
        store=SimpleNamespace(),
        expected_identity=expected_identity(),
    )

    with pytest.raises(ResearchMaterialLimitation) as exc:
        executor._material_bindings(
            principal=principal(),
            session=session,
            candidate_ids=("dimension.foreign",),
        )

    assert exc.value.code == "R1_SEMANTIC_REF_OUTSIDE_ACCEPTED_SCOPE"


def test_a3_frozen_artifact_vertical_replay_is_part_of_phase1_gate():
    """Execute the immutable A3 replay inside the canonical Phase-1 suite."""

    import runpy
    from pathlib import Path

    replay = runpy.run_path(
        str(Path(__file__).with_name("test_v3_brain_v2_a3_vertical_replay.py"))
    )
    replay[
        "test_a3_frozen_artifact_replays_through_evidence_dependency_and_child_readiness"
    ]()


def test_a3_frozen_artifact_vertical_replay_opens_result_dependent_child():
    """Replay run 37237863865 / artifact 11315439520 without any provider call."""

    from app.v3.authority import AcceptedResearchAuthority
    from app.v3.brain_v2.material_groups import (
        project_material_groups,
        result_dependency_execution_anchor,
        select_pending_material_group,
    )
    from app.v3.evidence import EvidenceArtifact, EvidenceState
    from app.v3.execution_identity import RuntimeIdentity
    from app.v3.research_analytical_scope import (
        NativeMaterialBinding,
        analytical_scope_contract,
    )
    from app.v3.research_material_coverage import assert_material_result_coverage
    from app.v3.research_result_dependency import resolve_first_ranked_entity

    source_run_id = 37237863865
    source_artifact_id = 11315439520
    comparison_id = "g_ce4372699197a8ea8167"
    ranking_id = "g_2fe6e7df18e5a9299821"
    child_id = "g_af46dc6ed8a2c6455c8d"

    semantic = {
        "metric.machine_downtime_minutes": {
            "source_mention": "makine duruşları / duruş süresi / machine downtime",
            "candidate_id": "metric.machine_downtime_minutes",
            "target_kind": "metric",
            "canonical_name": "Machine Downtime Minutes",
            "cube_names": ["machine_operations"],
        },
        "dimension.department": {
            "source_mention": "bölüm / departman / department",
            "candidate_id": "dimension.department",
            "target_kind": "dimension",
            "canonical_name": "Department",
            "cube_names": ["machine_operations"],
        },
        "dimension.machine_id": {
            "source_mention": "makine / machine",
            "candidate_id": "dimension.machine_id",
            "target_kind": "dimension",
            "canonical_name": "Machine",
            "cube_names": ["machine_operations"],
        },
        "metric.fault_count": {
            "source_mention": "arıza sayısı / fault count",
            "candidate_id": "metric.fault_count",
            "target_kind": "metric",
            "canonical_name": "Fault Count",
            "cube_names": ["machine_operations"],
        },
        "metric.maintenance_delay_hours": {
            "source_mention": "bakım gecikmesi / maintenance delay",
            "candidate_id": "metric.maintenance_delay_hours",
            "target_kind": "metric",
            "canonical_name": "Maintenance Delay Hours",
            "cube_names": ["machine_operations"],
        },
        "metric.performance_score": {
            "source_mention": "performans / performance",
            "candidate_id": "metric.performance_score",
            "target_kind": "metric",
            "canonical_name": "Performance Score",
            "cube_names": ["machine_operations"],
        },
        "metric.spare_part_delay_hours": {
            "source_mention": "yedek parça gecikmesi / spare part delay",
            "candidate_id": "metric.spare_part_delay_hours",
            "target_kind": "metric",
            "canonical_name": "Spare Part Delay Hours",
            "cube_names": ["machine_operations"],
        },
        "dimension.event_date": {
            "source_mention": "tarih / date / Mayıs / Haziran",
            "candidate_id": "dimension.event_date",
            "target_kind": "dimension",
            "canonical_name": "Event Date",
            "cube_names": ["machine_operations"],
        },
    }

    def ref(candidate_id):
        return semantic[candidate_id]

    brief = ResearchBrief.model_validate(
        {
            "brief_id": "rb_c0990d3b2e58d80fdf407e29",
            "objective": (
                "Mayıs-Haziran dönemindeki makine duruş değişimini incelemek, "
                "en çok bozulan bölümü belirlemek ve bu bölüm içinde makine veya "
                "ilgili operasyonel faktör bazında bir seviye daha derinleşerek "
                "seçimi kanıtlamak."
            ),
            "scope": {
                "semantic_refs": list(semantic.values()),
                "time_surfaces": ["Mayıs", "Haziran"],
                "periods": [
                    {
                        "source_text": "Mayıs",
                        "time_dimension_candidate_id": "dimension.event_date",
                        "start": "2026-05-01",
                        "end": "2026-06-01",
                        "role": "baseline_period",
                    },
                    {
                        "source_text": "Haziran",
                        "time_dimension_candidate_id": "dimension.event_date",
                        "start": "2026-06-01",
                        "end": "2026-07-01",
                        "role": "comparison_period",
                    },
                ],
                "temporal_dimension_ids": ["dimension.event_date"],
                "native_verification_bindings": [
                    {
                        "candidate_id": "metric.fault_count",
                        "table_name": "machine_operations",
                        "column_name": "fault_count",
                        "native_metric_entity_id": "oZwzWEN33R_yhDKzOCh-y",
                    },
                    {
                        "candidate_id": "metric.machine_downtime_minutes",
                        "table_name": "machine_operations",
                        "column_name": "machine_downtime_minutes",
                        "native_metric_entity_id": "3BV5uQyad1P8ZjF8MF412",
                    },
                    {
                        "candidate_id": "metric.maintenance_delay_hours",
                        "table_name": "machine_operations",
                        "column_name": "maintenance_delay_hours",
                        "native_metric_entity_id": "Ncs9eO5OvrvG4eQtGpwBd",
                    },
                    {
                        "candidate_id": "metric.performance_score",
                        "table_name": "machine_operations",
                        "column_name": "performance_score",
                        "native_metric_entity_id": "GJHHx_OhZZ2ufay3MjO8i",
                    },
                    {
                        "candidate_id": "metric.spare_part_delay_hours",
                        "table_name": "machine_operations",
                        "column_name": "spare_part_delay_hours",
                        "native_metric_entity_id": "mgg3vPU4kq25ZjOZzwB9s",
                    },
                    {
                        "candidate_id": "dimension.department",
                        "table_name": "machine_operations",
                        "column_name": "department",
                    },
                    {
                        "candidate_id": "dimension.event_date",
                        "table_name": "machine_operations",
                        "column_name": "event_date",
                    },
                    {
                        "candidate_id": "dimension.machine_id",
                        "table_name": "machine_operations",
                        "column_name": "machine_id",
                    },
                ],
                "scope_version": {"version_id": "scope_v1", "ordinal": 1},
            },
            "required_domains": ["machine_operations"],
            "questions": [
                {
                    "goal_id": comparison_id,
                    "kind": "comparison",
                    "source_text": "Mayıs-Haziran duruş değişimini araştır",
                    "source_fragment_identity": (
                        "fragment-sha256:"
                        "ffc5f2e8e8ec1bf6bc31b153fdf93749e41d1f649ee2c88c936360208494ce75"
                    ),
                    "subject_refs": [ref("metric.machine_downtime_minutes")],
                    "related_refs": [ref("metric.machine_downtime_minutes")],
                    "comparisons": [
                        {
                            "text": "Mayıs-Haziran duruş değişimini araştır",
                            "role": "temporal_period",
                        }
                    ],
                    "status": "RESOLVED",
                },
                {
                    "goal_id": ranking_id,
                    "kind": "ranking",
                    "source_text": "en çok bozulan bölümü bul",
                    "source_fragment_identity": (
                        "fragment-sha256:"
                        "38de9155a9810538095694d73296d3665c98296e45eb0d6d1c063d20eed75608"
                    ),
                    "subject_refs": [ref("dimension.department")],
                    "related_refs": [
                        ref("dimension.department"),
                        ref("metric.machine_downtime_minutes"),
                    ],
                    "ranking": {
                        "text": "en çok bozulan bölümü bul",
                        "direction": "desc",
                        "limit": None,
                        "measure_semantic_id": "metric.machine_downtime_minutes",
                        "basis": "change",
                    },
                    "status": "RESOLVED",
                },
                {
                    "goal_id": child_id,
                    "kind": "breakdown",
                    "source_text": (
                        "sonra o bölüm içinde makine veya ilgili operasyonel faktör "
                        "bazında bir seviye daha derinleş ve seçimini kanıtla"
                    ),
                    "source_fragment_identity": (
                        "fragment-sha256:"
                        "b1c2dbeef8a738b775fd2ca816f191a3aefe996ed0a93c8b063680b540dd8df9"
                    ),
                    "subject_refs": [ref("dimension.machine_id")],
                    "related_refs": [
                        ref("dimension.machine_id"),
                        ref("metric.machine_downtime_minutes"),
                        ref("metric.fault_count"),
                        ref("metric.maintenance_delay_hours"),
                        ref("metric.performance_score"),
                        ref("metric.spare_part_delay_hours"),
                    ],
                    "result_dependency": {
                        "source_goal_id": ranking_id,
                        "dimension_semantic_id": "dimension.department",
                        "selection": "first_ranked_entity",
                    },
                    "status": "RESOLVED",
                },
            ],
            "deliverables": [
                {
                    "requirement_id": "d_9c0daca25878ff79967f",
                    "kind": "report",
                    "source_text": "seçimini kanıtla",
                }
            ],
            "must_requirement_ids": [
                comparison_id,
                ranking_id,
                child_id,
                "d_9c0daca25878ff79967f",
            ],
            "context_version": "phase1-final-pinpoint-v1",
            "status": "READY_FOR_RESEARCH",
        }
    )
    authority = AcceptedResearchAuthority(
        contract_id="atc_7bc0bc597893a6d503f5f57e",
        lineage_id="atl_1564ca7d2a9c1a11bb2f",
        turn_id="research:a3-frozen-replay",
        request_ref="artifact:11315439520",
        source_message_hash=hashlib.sha256(
            b"a3 frozen vertical replay"
        ).hexdigest(),
        accepted_attempt_id=brief.brief_id,
        model_role="research-brief-product",
        obligation_ids=brief.must_requirement_ids,
        context_version=brief.context_version,
        accepted_at_iso="2026-10-04T21:53:06+00:00",
    )
    session = ResearchManager.start(
        authority=authority,
        objective=brief.objective,
        obligation_objectives={
            item.goal_id: item.source_text for item in brief.questions
        },
        tenant_binding="id:a3-replay-tenant",
        principal_subject="a3-replay-user",
        accepted_brief=brief,
        session_id="rs_5ba010c46f20f6f9e980d0a2",
        now=STAMP,
    )

    bindings = {
        "dimension.event_date": NativeMaterialBinding(
            candidate_id="dimension.event_date",
            candidate_kind="dimension",
            database_id=1,
            table_id=1,
            field_id=1,
        ),
        "dimension.department": NativeMaterialBinding(
            candidate_id="dimension.department",
            candidate_kind="dimension",
            database_id=1,
            table_id=1,
            field_id=2,
        ),
    }
    runtime = RuntimeIdentity(
        substrate="metabase-native",
        runtime_version="v0.63.18-dima.11.1.1",
        image_digest=(
            "sha256:"
            "0ff1e378b532cc986d871ed3945e677a7a6d0bfb28686b344dfa4ec8d397327d"
        ),
        database_id="1",
        repository="UpcyTech/dima-metabase-engine",
        revision_sha="4c49b8da6b424b0fa4d8ef340ca1b238d12980c1",
        upstream_base_sha="2ba2485c78d7e00a9a25f82c00fc201da71590c4",
        runtime_tag="v0.63.18-dima.11.1.1",
        build_identity=(
            "github-actions:37176179588:"
            "4c49b8da6b424b0fa4d8ef340ca1b238d12980c1"
        ),
        image_identity=(
            "sha256:"
            "0ff1e378b532cc986d871ed3945e677a7a6d0bfb28686b344dfa4ec8d397327d"
        ),
        runtime_instance_id=UUID("00000000-0000-4000-8000-000000001131"),
    )
    conversation_id = UUID("00000000-0000-4000-8000-000000001132")

    def admit_frozen_occurrence(
        current,
        *,
        obligation_id,
        native_query_id,
        query_fingerprint,
        result_payload,
        evidence_id,
        attested_native_material,
    ):
        contract = analytical_scope_contract(
            session=current,
            obligation_id=obligation_id,
        )
        prepared = ResearchManager.prepare_native_delegation(
            current,
            obligation_id=obligation_id,
            analytical_scope=contract,
        )
        delegated = prepared.session
        assert (
            ResearchManager.obligation(delegated, obligation_id).state
            == ObligationState.DELEGATED
        )
        coverage = assert_material_result_coverage(
            contract=contract,
            result_payload=result_payload,
            bindings=bindings,
            attested_native_material=attested_native_material,
        )
        assert coverage.status == "FULL"
        snapshot = ExecutionResultSnapshot(
            payload=result_payload,
            row_count=len(result_payload["data"]["rows"]),
        )
        receipt = DimaQueryReceiptSealer.seal_research_execution(
            authority_id=delegated.authority_id,
            research_session_id=delegated.session_id,
            obligation_ids=(obligation_id,),
            tenant_binding=delegated.tenant_binding,
            principal_subject=delegated.principal_subject,
            roles=("analyst",),
            native_subject_ref="metabase-user:7",
            native_conversation_id=conversation_id,
            native_query_id=native_query_id,
            native_query_provenance_ref=(
                f"github-actions:{source_run_id}:artifact:{source_artifact_id}:query"
            ),
            native_result_provenance_ref=(
                f"github-actions:{source_run_id}:artifact:{source_artifact_id}:result"
            ),
            query_fingerprint=query_fingerprint,
            semantic_context_version=delegated.context_version,
            scope_fingerprint=brief.scope_fingerprint,
            runtime=runtime,
            result=snapshot,
            event=ExecutionEventIdentity(
                execution_id=f"a3-replay:{obligation_id}",
                executed_at=STAMP,
            ),
        )
        evidence = EvidenceArtifact(
            artifact_id=evidence_id,
            authority_id=delegated.authority_id,
            obligation_ids=(obligation_id,),
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="a3_frozen_artifact_vertical_replay",
            state=EvidenceState.VERIFIED,
            payload={
                "source_run_id": source_run_id,
                "source_artifact_id": source_artifact_id,
                "result_hash": snapshot.result_hash,
                "result": result_payload,
            },
        )
        admitted = ResearchManager.admit_receipted_evidence(
            delegated,
            obligation_id=obligation_id,
            receipt=receipt,
            evidence=evidence,
            satisfies_obligation=True,
            now=STAMP,
        )
        assert (
            ResearchManager.obligation(admitted, obligation_id).state
            == ObligationState.VERIFIED
        )
        assert receipt.receipt_id
        assert evidence.artifact_id
        return admitted, contract, receipt, evidence, snapshot

    comparison_result = {
        "data": {
            "cols": [
                {
                    "id": 1,
                    "name": "event_date",
                    "display_name": "Event Date: Month",
                    "field_ref": ["field", 1, {"temporal-unit": "month"}],
                },
                {
                    "name": "sum",
                    "display_name": "Machine Downtime Minutes",
                    "field_ref": ["aggregation", 0],
                },
            ],
            "rows": [
                ["2026-05-01T00:00:00Z", 1224],
                ["2026-06-01T00:00:00Z", 1625],
            ],
        }
    }
    session, _, _, _, _ = admit_frozen_occurrence(
        session,
        obligation_id=comparison_id,
        native_query_id="mdjcw91DQhwHz58uqLJ4B",
        query_fingerprint=(
            "395cce76f5847079a0d9f6c674f56749d30cddf02504a7545e78f5189785a764"
        ),
        result_payload=comparison_result,
        evidence_id="evi_e235b1bfbe327943ed5e0a83",
        attested_native_material=False,
    )

    ranking_result = {
        "data": {
            "cols": [
                {
                    "id": 2,
                    "name": "department",
                    "display_name": "Department",
                    "field_ref": [
                        "field",
                        "department",
                        {"base-type": "type/Text"},
                    ],
                },
                {
                    "name": "Change (Jun minus May)",
                    "display_name": "Change (Jun minus May)",
                    "field_ref": ["expression", "Change (Jun minus May)"],
                },
            ],
            "rows": [
                ["Assembly", 267.0],
                ["Packaging", 74.0],
                ["Utilities", 34.0],
                ["Maintenance", 18.0],
                ["Quality", 8.0],
            ],
        }
    }
    (
        session,
        ranking_contract,
        ranking_receipt,
        ranking_evidence,
        ranking_snapshot,
    ) = admit_frozen_occurrence(
        session,
        obligation_id=ranking_id,
        native_query_id="pHptOIaZo05ThIon0JKg5",
        query_fingerprint=(
            "854758dad443fdc595bb4055c2046323f1cae775570c6bb1348fad86aa8369cc"
        ),
        result_payload=ranking_result,
        evidence_id="evi_111111111111111111111111",
        attested_native_material=True,
    )
    assert ranking_contract.ranking is not None
    assert ranking_contract.ranking.basis.value == "change"
    assert ranking_receipt.receipt_id is not None
    assert ranking_evidence.artifact_id is not None
    assert (
        ResearchManager.obligation(session, ranking_id).state
        == ObligationState.VERIFIED
    )

    child_contract = analytical_scope_contract(
        session=session,
        obligation_id=child_id,
    )
    dependency = resolve_first_ranked_entity(
        base_contract=child_contract,
        source_goal_id=ranking_id,
        source_execution_obligation_id=ranking_id,
        source_evidence_id=ranking_evidence.artifact_id,
        source_receipt_id=ranking_receipt.receipt_id,
        source_result_hash=ranking_snapshot.result_hash,
        dimension_semantic_id="dimension.department",
        native_field_id=2,
        parent_result=ranking_result,
        dimension_name="Department",
    )
    assert dependency.selected_value == "Assembly"
    assert dependency.contract.scope_identity == child_contract.scope_identity
    assert dependency.contract.scope_fingerprint == child_contract.scope_fingerprint
    assert dependency.contract.filters[-1].source_candidate_id == (
        "dimension.department"
    )
    assert dependency.contract.filters[-1].value == "Assembly"

    groups = project_material_groups(session)
    comparison_group = next(
        item for item in groups if comparison_id in item.consumer_requirement_ids
    )
    ranking_group = next(
        item for item in groups if ranking_id in item.consumer_requirement_ids
    )
    child_group = next(
        item for item in groups if child_id in item.consumer_requirement_ids
    )
    execution_anchor = result_dependency_execution_anchor(
        session=session,
        groups=groups,
        requirement_id=child_id,
    )
    assert execution_anchor == ranking_group.anchor_requirement_id
    completed = tuple(
        dict.fromkeys(
            (
                comparison_group.material_group_id,
                ranking_group.material_group_id,
            )
        )
    )
    next_group = select_pending_material_group(
        groups,
        completed_material_group_ids=completed,
    )
    assert next_group is not None
    assert next_group.material_group_id == child_group.material_group_id
    assert child_id in next_group.consumer_requirement_ids
    assert ranking_id in next_group.dependency_requirement_ids
