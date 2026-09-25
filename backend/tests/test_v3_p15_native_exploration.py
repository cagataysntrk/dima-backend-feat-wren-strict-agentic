from __future__ import annotations

import base64
import hashlib
import inspect
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import unquote_plus
from uuid import UUID

import httpx
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

import app.v3.research_exploration as exploration_module
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
from app.v3.research import EvidenceRef, ObligationState, ResearchManager
from app.v3.research_exploration import (
    NativeResearchExploration,
    ResearchExplorationError,
    ResearchExplorationStore,
)
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_engine import (
    NativeEngineBridge,
    NativeExplorationError,
)
from app.v3.substrate.metabase.native_models import (
    NativeEngineIdentity,
    NativeExplorationObservation,
)
from control_plane.authorize import Principal
from control_plane.models import Tenant, User


ENGINE_SHA = "cbe313af9ac2d5960f662068e433d328d896fb06"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
TAG = "v0.63.18-dima.6"
TENANT = UUID("00000000-0000-4000-8000-000000001501")
USER = UUID("00000000-0000-4000-8000-000000001502")
STAMP = datetime(2026, 9, 25, 9, 0, tzinfo=timezone.utc)


def h(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def principal() -> Principal:
    return Principal(
        user_id=str(USER),
        tenant_id=str(TENANT),
        roles=["analyst"],
        tenant_slug="p15-native",
    )


def expected_identity() -> NativeEngineIdentity:
    return NativeEngineIdentity(
        engine_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=TAG,
    )


def brief() -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="satış siparişleri",
        candidate_id="native.sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    q = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.PERFORMANCE,
        source_text="Satış performansındaki ilginç örüntüleri araştır.",
        subject_refs=(metric,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p15-native",
        objective=q.source_text,
        scope=ResearchScope(semantic_refs=(metric,)),
        questions=(q,),
        must_requirement_ids=("g1",),
        context_version="ctx-p15-native-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def verified_fixture(db_engine):
    SQLModel.metadata.create_all(db_engine)
    with Session(db_engine) as db:
        db.add(Tenant(id=TENANT, slug="p15-native", name="P15", created_at=STAMP))
        db.add(
            User(
                id=USER,
                tenant_id=TENANT,
                email="p15@example.test",
                password_hash="unused",
                created_at=STAMP,
            )
        )
        db.commit()

    store = ResearchSessionStore(db_engine)
    product = ResearchAskOrchestrator(store=store)
    session = product.start_from_brief(
        brief=brief(),
        request_ref="p15-test",
        source_message_hash=hashlib.sha256(b"p15").hexdigest(),
        principal=principal(),
    )
    prepared = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g1",
    )
    session = store.save(prepared.session, expected_revision=session.revision)
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
        native_query_id="p15-native-query",
        native_query=query,
        query_fingerprint=h(query),
    )
    store.mark_execution_started(link.id, native_subject_ref="metabase-user:7")
    result = {"database_id": 1, "data": {"rows": [["Web", 4]]}, "row_count": 1}
    store.mark_executed(
        link.id,
        native_subject_ref="metabase-user:7",
        runtime_identity={
            "substrate": "metabase-native",
            "runtime_version": TAG,
            "image_digest": "sha256:" + "a" * 64,
            "database_id": "metabase:1",
        },
        result_payload=result,
        result_hash=h(result),
        executed_at=STAMP,
    )
    evidence_id = "evi_" + "1" * 24
    receipt_id = "dqr_" + "2" * 24
    store.mark_verified(
        link.id,
        receipt_id=receipt_id,
        evidence_id=evidence_id,
    )

    item = ResearchManager.obligation(session, "g1").model_copy(
        update={
            "state": ObligationState.VERIFIED,
            "evidence_refs": (evidence_id,),
        }
    )
    session = ResearchManager.advance(
        session,
        obligations=ResearchManager.replace(session, item),
        evidence_refs=(
            EvidenceRef(
                evidence_id=evidence_id,
                receipt_id=receipt_id,
                authority_id=session.authority_id,
                obligation_id="g1",
            ),
        ),
    )
    store.save(session, expected_revision=session.revision - 1)
    return store, session, store.execution_link(link.id), query


def test_native_automagic_transport_uses_same_session_and_exact_query():
    query = {
        "database": 1,
        "type": "query",
        "query": {"source-table": 10, "aggregation": [["count"]]},
    }
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["session"] = request.headers.get("X-Metabase-Session")
        raw_segment = request.url.raw_path.rsplit(b"/", 1)[-1].decode("ascii")
        encoded = unquote_plus(raw_segment)
        observed["query"] = json.loads(
            base64.b64decode(encoded).decode("utf-8")
        )
        return httpx.Response(
            200,
            json={"name": "Native exploration", "dashcards": [{"id": "x1"}]},
        )

    bridge = NativeEngineBridge(
        base_url="http://native.test",
        session_token="principal-session",
        expected_identity=expected_identity(),
        transport=httpx.MockTransport(handler),
    )
    result = bridge.explore_adhoc(query)
    bridge.close()

    assert observed["session"] == "principal-session"
    assert observed["query"] == query
    assert result.query_fingerprint == h(query)
    assert result.exploration_kind == "automagic_adhoc"


def test_native_automagic_permission_failure_remains_native_http_failure():
    bridge = NativeEngineBridge(
        base_url="http://native.test",
        session_token="principal-session",
        expected_identity=expected_identity(),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(403, text="native permission denied")
        ),
    )
    with pytest.raises(NativeExplorationError) as exc:
        bridge.explore_adhoc({"database": 1, "type": "query", "query": {}})
    bridge.close()
    assert exc.value.status_code == 403
    assert "native permission denied" in exc.value.detail


class FakeBridge:
    def __init__(self, *, fail_on_call=False):
        self.calls = []
        self.fail_on_call = fail_on_call

    def explore_adhoc(self, query):
        if self.fail_on_call:
            raise AssertionError("persisted P15 material was explored twice")
        self.calls.append(query)
        return NativeExplorationObservation(
            status_code=200,
            latency_ms=2,
            query_fingerprint=h(query),
            payload={
                "name": "Native automagic analysis",
                "dashcards": [
                    {"id": "native-card-1", "name": "Orders by channel"},
                    {"id": "native-card-2", "name": "Orders over time"},
                ],
            },
        )


class FakeSubjects:
    def __init__(self, bridge):
        self.bridge = bridge
        self.tokens = []

    @contextmanager
    def open(self, *, principal, session, native_session_token):
        assert principal.user_id == session.principal_subject
        self.tokens.append(native_session_token)
        yield self.bridge


def test_p15_verified_p14_occurrence_becomes_durable_research_material_and_resumes():
    db = engine()
    research_store, session, link, query = verified_fixture(db)
    bridge = FakeBridge()
    service = NativeResearchExploration(
        research_store=research_store,
        subject_provider=FakeSubjects(bridge),
        material_store=ResearchExplorationStore(db),
    )

    first = service.explore(
        session_id=session.session_id,
        obligation_id="g1",
        principal=principal(),
        native_session_token="principal-session",
    )
    assert bridge.calls == [query]
    assert first.epistemic_state == "RESEARCH_MATERIAL"
    assert first.execution_link_id == link.id
    assert first.native_query_id == link.native_query_id
    assert first.query_fingerprint == link.native_query_fingerprint
    assert first.source_evidence_refs == (link.evidence_id,)
    assert first.material["name"] == "Native automagic analysis"

    resumed = NativeResearchExploration(
        research_store=research_store,
        subject_provider=FakeSubjects(FakeBridge(fail_on_call=True)),
        material_store=ResearchExplorationStore(db),
    ).explore(
        session_id=session.session_id,
        obligation_id="g1",
        principal=principal(),
        native_session_token=None,
    )
    assert resumed == first


def test_p15_rejects_unverified_research_obligation_before_native_exploration():
    db = engine()
    SQLModel.metadata.create_all(db)
    with Session(db) as s:
        s.add(Tenant(id=TENANT, slug="p15-native", name="P15", created_at=STAMP))
        s.add(
            User(
                id=USER,
                tenant_id=TENANT,
                email="p15@example.test",
                password_hash="unused",
                created_at=STAMP,
            )
        )
        s.commit()
    store = ResearchSessionStore(db)
    session = ResearchAskOrchestrator(store=store).start_from_brief(
        brief=brief(),
        request_ref="p15-unverified",
        source_message_hash=hashlib.sha256(b"p15-unverified").hexdigest(),
        principal=principal(),
    )
    service = NativeResearchExploration(
        research_store=store,
        subject_provider=FakeSubjects(FakeBridge()),
        material_store=ResearchExplorationStore(db),
    )
    with pytest.raises(ResearchExplorationError) as exc:
        service.explore(
            session_id=session.session_id,
            obligation_id="g1",
            principal=principal(),
            native_session_token="principal-session",
        )
    assert exc.value.code == "P15_VERIFIED_RESEARCH_OBLIGATION_REQUIRED"


def test_p15_product_module_has_no_python_analytical_primitive_or_p13_authority():
    source = inspect.getsource(exploration_module)
    for forbidden in (
        "NativeStandardTrustOrchestrator",
        "ResolvedAnalyticsIntent",
        "TemporalBindingEngine",
        "MetabaseProjectionCompiler",
        "MetabaseCanonicalizer",
        "attest_native_query",
        "execute_native_query",
        "compute_chart_stats",
        "chart_interest",
        "dimension_interest",
    ):
        assert forbidden not in source

    imported_roots = set()
    tree = __import__("ast").parse(source)
    for node in __import__("ast").walk(tree):
        if isinstance(node, __import__("ast").Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, __import__("ast").ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert imported_roots.isdisjoint({"numpy", "pandas", "scipy", "statistics"})
