from __future__ import annotations

import hashlib
import inspect
import json
from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

import app.v3.research_analytical_scope as scope_module
import app.v3.research_native_gateway as gateway_module
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
from app.v3.research_store import ResearchSessionStore
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
