from __future__ import annotations

import hashlib
import inspect
import json
from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

import app.v3.research_native_gateway as gateway_module
from app.v2.models import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research import ObligationState, ResearchManager
from app.v3.research_native_gateway import (
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
)
from app.v3.research_product import ResearchAskOrchestrator, ResearchMaterialLimitation
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_engine import NativeDatasetExecutionError
from app.v3.substrate.metabase.native_models import (
    NativeDatasetExecutionObservation,
    NativeEngineIdentity,
)
from control_plane.authorize import Principal
from control_plane.models import NativeSubjectBinding, Tenant, User
from lab.metabase.p14.native_direct_research_canary import (
    FROZEN_BOYAHANE_CHANNEL_COUNTS,
    channel_counts,
)


ENGINE_SHA = "cbe313af9ac2d5960f662068e433d328d896fb06"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
TAG = "v0.63.18-dima.6"
DIGEST = "sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353"
BUILD = f"github-actions:36042062775:{ENGINE_SHA}"
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
        source_text="Haziran 2026 satış performansını kanala göre incele.",
        subject_refs=(metric,),
        related_refs=(channel,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p14-native-direct",
        objective=q.source_text,
        scope=ResearchScope(
            semantic_refs=(metric, channel),
            time_surfaces=("Haziran 2026",),
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


class MaterialBridge:
    def __init__(self, *, forbidden=False, fail_on_execute=False):
        self.calls = []
        self.forbidden = forbidden
        self.fail_on_execute = fail_on_execute

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
    assert outcome.evidence.verified

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

    second = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=MaterialBridge(fail_on_execute=True),
        native_conversation_id=link.native_conversation_id,
        native_query_id=link.native_query_id,
        native_query=query,
        query_fingerprint=link.native_query_fingerprint,
        execution_link_id=link.id,
    )
    assert first.receipt.receipt_id == second.receipt.receipt_id
    assert first.receipt.result_hash == second.receipt.result_hash
    assert len(first_bridge.calls) == 1


def test_gateway_has_no_p13_p10_operator_or_resource_authority():
    source = inspect.getsource(gateway_module)
    for forbidden in (
        "NativeAttestationEnvelope",
        "NativeExecutionManifest",
        "AuthorizedExecutionArtifact",
        "ExecutionAccessSnapshotIssuer",
        "VerifiedExecutionSecurityFacts",
        "NativeResourceBindingProvider",
        "attest_native_query",
        "execute_native_query",
        "_field_ids",
        "_assert_locator",
        "ResolvedAnalyticsIntent",
        "TemporalBindingEngine",
        "MetabaseProjectionCompiler",
        "MetabaseCanonicalizer",
    ):
        assert forbidden not in source
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
