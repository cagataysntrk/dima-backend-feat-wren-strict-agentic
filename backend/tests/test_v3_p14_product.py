from __future__ import annotations

import hashlib
import json
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import httpx
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.research_contracts import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    RankingSurface,
    SemanticTargetKind,
)
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.research import ObligationState, StoppingStatus
from app.v3.research_product import (
    ResearchAskOrchestrator,
    ResearchMaterialLimitation,
    ResearchMaterialOutcome,
    ResearchProductRuntimeUnavailable,
)
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal


NOW = datetime(2026, 9, 24, 20, 30, tzinfo=timezone.utc)
ENGINE_SHA = "cbe313af9ac2d5960f662068e433d328d896fb06"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
RUNTIME_TAG = "v0.63.18-dima.6"
TENANT_ID = "00000000-0000-4000-8000-000000000901"
PRINCIPAL_ID = "user-p14-product"
CONTEXT = "ctx-p14-product-v1"


def _db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _principal() -> Principal:
    return Principal(
        user_id=PRINCIPAL_ID,
        tenant_id=TENANT_ID,
        roles=["analyst"],
        tenant_slug="boyahane",
    )


def _brief(two: bool = True) -> ResearchBrief:
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
    questions = [
        ResearchQuestion(
            goal_id="g1",
            kind=ResearchGoalKind.BREAKDOWN,
            source_text="Haziran satış siparişlerini kanala göre incele.",
            subject_refs=(metric,),
            related_refs=(channel,),
            status=ResearchGoalStatus.RESOLVED,
        )
    ]
    if two:
        questions.append(
            ResearchQuestion(
                goal_id="g2",
                kind=ResearchGoalKind.RANKING,
                source_text="En güçlü iki kanalı sırala.",
                subject_refs=(metric,),
                related_refs=(channel,),
                ranking=RankingSurface(
                    text="en güçlü iki kanal",
                    direction="desc",
                    limit=2,
                ),
                status=ResearchGoalStatus.RESOLVED,
            )
        )
    return ResearchBrief(
        brief_id="rb-product-p14",
        objective="Satış performansındaki değişimi kanıtlarla araştır.",
        scope=ResearchScope(
            semantic_refs=(metric, channel),
            time_surfaces=("Haziran 2026",),
        ),
        questions=tuple(questions),
        must_requirement_ids=tuple(item.goal_id for item in questions),
        context_version=CONTEXT,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _receipt(
    session,
    obligation_id: str,
    suffix: str,
    *,
    native_conversation_id: UUID,
    native_query_id: str,
    query_fingerprint: str,
    execution_link_id,
) -> DimaQueryReceipt:
    return DimaQueryReceipt(
        receipt_id="dqr_" + suffix * 24,
        receipt_fingerprint=suffix * 64,
        execution_id=f"native-dataset:{execution_link_id}",
        step_role="primary",
        authority_kind="research_material",
        authority_id=session.authority_id,
        obligation_ids=(obligation_id,),
        tenant_id=session.tenant_binding,
        principal_id=session.principal_subject,
        semantic_refs=(),
        projection_hash=None,
        resolved_intent_hash=None,
        research_session_id=session.session_id,
        native_subject_ref="metabase-user:7",
        native_conversation_id=native_conversation_id,
        native_query_id=native_query_id,
        native_query_provenance_ref=(
            f"research-execution-link:{execution_link_id}:query"
        ),
        native_result_provenance_ref=(
            f"research-execution-link:{execution_link_id}:result"
        ),
        canonical_query_fingerprint=query_fingerprint,
        canonical_query_representation=None,
        principal_fingerprint="e" * 64,
        execution_access_fingerprint=None,
        access_attestation_refs=(),
        semantic_context_version=session.context_version,
        resource_entity_ids=(),
        resource_fingerprints=(),
        substrate="metabase-native",
        substrate_runtime_version=RUNTIME_TAG,
        substrate_image_digest="sha256:" + "2" * 64,
        engine_repository="UpcyTech/dima-metabase-engine",
        engine_revision_sha=ENGINE_SHA,
        engine_upstream_base_sha=UPSTREAM_SHA,
        engine_runtime_tag=RUNTIME_TAG,
        engine_build_identity=f"github-actions:36042062775:{ENGINE_SHA}",
        engine_image_identity=(
            "ghcr.io/upcytech/dima-metabase-engine@sha256:" + "2" * 64
        ),
        engine_runtime_instance_id=UUID(
            "00000000-0000-4000-8000-000000000902"
        ),
        database_id="metabase:1",
        executed_at=NOW,
        result_hash="3" * 64,
        row_count=1,
    )


class BridgeFactory:
    def __init__(self) -> None:
        self.metabot_posts = 0
        self.query_ids: list[str] = []

    def open(
        self,
        *,
        principal,
        session,
        native_session_token=None,
    ) -> AbstractContextManager[NativeEngineBridge]:
        del principal, native_session_token
        query_id = f"native-{session.session_id}-{self.metabot_posts + 1}"

        def handler(request: httpx.Request) -> httpx.Response:
            if (
                request.method == "GET"
                and request.url.path == "/api/session/properties"
            ):
                return httpx.Response(
                    200,
                    json={"version": {"tag": RUNTIME_TAG}},
                )
            if (
                request.method == "POST"
                and request.url.path == "/api/metabot/agent-streaming"
            ):
                self.metabot_posts += 1
                body = json.loads(request.content.decode("utf-8"))
                assert session.native_conversation is not None
                assert body["conversation_id"] == str(
                    session.native_conversation.conversation_id
                )
                self.query_ids.append(query_id)
                native_query = {
                    "database": 1,
                    "type": "query",
                    "query": {"source-table": 10},
                }
                generated = {
                    "type": "generated_entity",
                    "value": {
                        "query": {
                            "id": query_id,
                            "query": native_query,
                        }
                    },
                }
                return httpx.Response(
                    202,
                    text=(
                        "2:"
                        + json.dumps(generated, separators=(",", ":"))
                        + "\n"
                        + 'd:{"finishReason":"stop"}\n'
                    ),
                )
            raise AssertionError(
                f"unexpected native call: {request.method} {request.url.path}"
            )

        return NativeEngineBridge(
            base_url="http://native.test",
            session_token="principal-scoped-test-session",
            expected_identity=NativeEngineIdentity(
                engine_sha=ENGINE_SHA,
                upstream_base_sha=UPSTREAM_SHA,
                runtime_tag=RUNTIME_TAG,
            ),
            transport=httpx.MockTransport(handler),
        )


class MaterialExecutor:
    def __init__(
        self,
        *,
        crash_once: bool = False,
        limit_first: bool = False,
    ) -> None:
        self.crash_once = crash_once
        self.limit_first = limit_first
        self.calls: list[tuple[str, str, dict, str]] = []

    def execute(
        self,
        *,
        principal,
        session,
        obligation_id,
        bridge,
        native_conversation_id,
        native_query_id,
        native_query,
        query_fingerprint,
        execution_link_id,
    ) -> ResearchMaterialOutcome:
        del principal, bridge
        self.calls.append(
            (
                obligation_id,
                native_query_id,
                native_query,
                query_fingerprint,
            )
        )
        if self.crash_once:
            self.crash_once = False
            raise RuntimeError(
                "simulated process loss after exact native occurrence capture"
            )
        if self.limit_first and obligation_id == "g1":
            raise ResearchMaterialLimitation(
                "NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED",
                "captured native representation is unavailable",
            )
        suffix = "4" if obligation_id == "g1" else "5"
        receipt = _receipt(
            session,
            obligation_id,
            suffix,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            query_fingerprint=query_fingerprint,
            execution_link_id=execution_link_id,
        )
        evidence = EvidenceArtifact(
            artifact_id="evi_" + suffix * 24,
            authority_id=receipt.authority_id,
            obligation_ids=(obligation_id,),
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="p14_product_native_research",
            state=EvidenceState.VERIFIED,
            payload={"claim": f"receipted {obligation_id}"},
        )
        return ResearchMaterialOutcome(
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            attestation_id=None,
            receipt=receipt,
            evidence=evidence,
        )

def _product(engine, factory=None, executor=None):
    return ResearchAskOrchestrator(
        store=ResearchSessionStore(engine),
        bridge_factory=factory,
        material_executor=executor,
    )


def _start(product: ResearchAskOrchestrator, *, two: bool = True):
    return product.start_from_brief(
        brief=_brief(two=two),
        request_ref="r-p14-product",
        source_message_hash=hashlib.sha256(b"research request").hexdigest(),
        principal=_principal(),
    )


def test_accepted_research_material_context_survives_restart_without_reparse():
    engine = _db_engine()
    product = _product(engine)
    brief = _brief(two=True)
    session = product.start_from_brief(
        brief=brief,
        request_ref="r-p14-product",
        source_message_hash=hashlib.sha256(b"research request").hexdigest(),
        principal=_principal(),
    )
    restored = ResearchSessionStore(engine).load(
        session.session_id,
        tenant=session.tenant_binding,
        principal=session.principal_subject,
    )

    assert restored.accepted_brief == brief
    assert restored.accepted_brief is not None
    assert restored.accepted_brief.scope.time_surfaces == ("Haziran 2026",)
    ranking = product.accepted_material_question(restored, "g2")
    assert ranking.ranking is not None
    assert ranking.ranking.direction == "desc"
    assert ranking.ranking.limit == 2
    assert tuple(ref.candidate_id for ref in ranking.subject_refs) == (
        "cand_sales_order_count",
    )
    assert tuple(ref.candidate_id for ref in ranking.related_refs) == (
        "cand_sales_order_channel",
    )


def test_product_research_entry_persists_session_and_requires_native_runtime():
    engine = _db_engine()
    product = _product(engine)
    session = _start(product, two=False)
    restored = ResearchSessionStore(engine).load(
        session.session_id,
        tenant=session.tenant_binding,
        principal=session.principal_subject,
    )
    assert restored == session
    with pytest.raises(ResearchProductRuntimeUnavailable) as exc:
        product.run_next(
            session_id=session.session_id,
            principal=_principal(),
        )
    assert exc.value.code == "P14_NATIVE_RUNTIME_NOT_CONFIGURED"


def test_product_research_runs_native_turn_and_persists_receipted_evidence():
    engine = _db_engine()
    factory = BridgeFactory()
    executor = MaterialExecutor()
    product = _product(engine, factory, executor)
    session = _start(product, two=False)

    response = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )
    restored = product.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert factory.metabot_posts == 1
    assert response.native_query_id == factory.query_ids[0]
    assert executor.calls[0][2] == {
        "database": 1,
        "type": "query",
        "query": {"source-table": 10},
    }
    assert len(executor.calls[0][3]) == 64
    assert response.receipt_id is not None
    assert response.evidence_id is not None
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert restored.stopping.status == StoppingStatus.COMPLETE
    assert restored.native_conversation is not None
    assert response.native_conversation_id == restored.native_conversation.conversation_id


def test_restart_resumes_exact_occurrence_without_replaying_metabot_turn():
    engine = _db_engine()
    factory = BridgeFactory()
    executor = MaterialExecutor(crash_once=True)
    first = _product(engine, factory, executor)
    session = _start(first, two=False)

    with pytest.raises(RuntimeError, match="simulated process loss"):
        first.run_next(
            session_id=session.session_id,
            principal=_principal(),
        )
    assert factory.metabot_posts == 1
    captured_query_id = executor.calls[0][1]

    resumed = _product(engine, factory, executor)
    response = resumed.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert factory.metabot_posts == 1
    assert executor.calls[-1][1] == captured_query_id
    assert response.native_query_id == captured_query_id
    assert response.resumed_exact_occurrence is True
    assert response.evidence_id is not None


def test_material_limitation_is_scoped_and_independent_work_continues():
    engine = _db_engine()
    factory = BridgeFactory()
    executor = MaterialExecutor(limit_first=True)
    product = _product(engine, factory, executor)
    session = _start(product, two=True)

    first = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
        obligation_id="g1",
    )
    after_first = product.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )
    assert (
        first.limitation_code
        == "NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED"
    )
    assert {item.obligation_id: item.state for item in after_first.obligations} == {
        "g1": ObligationState.LIMITED,
        "g2": ObligationState.READY,
    }
    assert after_first.stopping.status == StoppingStatus.ACTIVE

    second = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
        obligation_id="g2",
    )
    assert second.evidence_id is not None
    final = product.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )
    assert final.stopping.status == StoppingStatus.PARTIAL


def test_resume_is_scope_bound_and_does_not_require_old_raw_prompt():
    engine = _db_engine()
    product = _product(engine)
    session = _start(product, two=False)

    other = Principal(
        user_id="different-user",
        tenant_id=TENANT_ID,
        roles=["analyst"],
        tenant_slug="boyahane",
    )
    with pytest.raises(ResearchPersistenceError) as exc:
        product.resume_state(
            session_id=session.session_id,
            principal=other,
        )
    assert exc.value.code == "P14_RESEARCH_SESSION_NOT_FOUND"


