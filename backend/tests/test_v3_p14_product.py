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
    CausalCompetitionSurface,
    CausalEffectObservation,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    RankingSurface,
    ScopeVersion,
    SemanticTargetKind,
)
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.research import ObligationState, ResearchManager, StoppingStatus
from app.v3.research_product import (
    ResearchAskOrchestrator,
    ResearchMaterialLimitation,
    ResearchMaterialObservationUnavailable,
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
    event_date = ResearchSemanticRef(
        source_mention="tarih",
        candidate_id="cand_sales_order_date",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Sales Order Date",
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
            semantic_refs=(metric, channel, event_date),
            time_surfaces=("Haziran 2026",),
            periods=(
                ResearchTimePeriod(
                    source_text="Haziran 2026",
                    time_dimension_candidate_id=event_date.candidate_id,
                    start="2026-06-01",
                    end="2026-07-01",
                ),
            ),
            temporal_dimension_ids=(event_date.candidate_id,),
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
    def __init__(self, *, repeat_query_on_repair: bool = False) -> None:
        self.metabot_posts = 0
        self.query_ids: list[str] = []
        self.metabot_bodies: list[dict] = []
        self.repeat_query_on_repair = repeat_query_on_repair

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
                self.metabot_bodies.append(body)
                assert session.native_conversation is not None
                assert body["conversation_id"] == str(
                    session.native_conversation.conversation_id
                )
                self.query_ids.append(query_id)
                source_table = (
                    10
                    if self.repeat_query_on_repair and self.metabot_posts > 1
                    else 10 + self.metabot_posts - 1
                )
                native_query = {
                    "database": 1,
                    "type": "query",
                    "query": {"source-table": source_table},
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
                state = {
                    "type": "state",
                    "value": {"queries": {query_id: native_query}},
                }
                return httpx.Response(
                    202,
                    text=(
                        "2:"
                        + json.dumps(generated, separators=(",", ":"))
                        + "\n2:"
                        + json.dumps(state, separators=(",", ":"))
                        + "\n"
                        + 'd:{"finishReason":"stop"}\n'
                    ),
                )
            if (
                request.method == "GET"
                and request.url.path.startswith("/api/metabot/conversations/")
            ):
                assert session.native_conversation is not None
                return httpx.Response(
                    200,
                    json={
                        "conversation_id": str(
                            session.native_conversation.conversation_id
                        ),
                        "chat_messages": [
                            {
                                "role": "user",
                                "type": "text",
                                "message": "prior governed material turn",
                            }
                        ],
                    },
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
        repairable_failures: int = 0,
        observation_unavailable_failures: int = 0,
        store: ResearchSessionStore | None = None,
    ) -> None:
        self.crash_once = crash_once
        self.limit_first = limit_first
        self.repairable_failures = repairable_failures
        self.observation_unavailable_failures = observation_unavailable_failures
        self.store = store
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
        if self.repairable_failures > 0:
            self.repairable_failures -= 1
            raise ResearchMaterialLimitation(
                "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
                "symbolic_reference_period",
            )
        if self.observation_unavailable_failures > 0:
            self.observation_unavailable_failures -= 1
            raise ResearchMaterialObservationUnavailable(
                "NATIVE_QUERY_OCCURRENCE_NOT_FOUND",
                "HTTP 404 NATIVE_QUERY_OCCURRENCE_NOT_FOUND: "
                "symbolic transient observer unavailable",
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


def test_evidence_synthesis_ranking_delegates_unranked_governed_material():
    engine = _db_engine()
    product = _product(engine)
    base = _brief(two=True)
    second_metric = ResearchSemanticRef(
        source_mention="iade adedi",
        candidate_id="cand_return_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Return Count",
        cube_names=("satis_siparisleri",),
    )
    ranking_question = base.questions[1].model_copy(
        update={
            "source_text": "Kanallardaki kötüleşmeyi iki metriğin kanıtıyla değerlendir.",
            "subject_refs": (
                base.questions[0].subject_refs[0],
                second_metric,
            ),
            "ranking": RankingSurface(
                text="iki metrikteki kötüleşmeyi değerlendir",
                direction="desc",
                limit=None,
                measure_semantic_id=None,
            ),
        }
    )
    brief = base.model_copy(
        update={
            "scope": base.scope.model_copy(
                update={
                    "semantic_refs": (
                        *base.scope.semantic_refs,
                        second_metric,
                    )
                }
            ),
            "questions": (base.questions[0], ranking_question),
        }
    )
    session = product.start_from_brief(
        brief=brief,
        request_ref="r-p14-evidence-synthesis",
        source_message_hash=hashlib.sha256(
            b"multi metric evidence synthesis"
        ).hexdigest(),
        principal=_principal(),
    )

    delegation = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g2",
    )

    requirement = delegation.request.context["dima_material_requirement"]
    ranking = requirement["ranking"]
    assert ranking["kind"] == "evidence_synthesis"
    assert ranking["limit"] is None
    assert "dima_analytical_scope" not in delegation.request.context
    assert "cand_sales_order_count" in requirement["metrics"]
    assert "cand_return_count" in requirement["metrics"]
    assert delegation.request.message.count("[DIMA MATERIAL REQUIREMENT JSON]") == 1
    assert ranking_question.source_text in delegation.request.message
    assert "[MATERIAL TURN BOUNDARY]" in delegation.request.message
    assert delegation.request.message.index(ranking_question.source_text) < (
        delegation.request.message.index("[MATERIAL TURN BOUNDARY]")
    )
    assert delegation.request.message.endswith(
        "- do not perform downstream investigation, hypothesis adjudication, next-test planning, reporting, or workflow orchestration in this turn"
    )
    assert (
        "- produce exactly one executable native analytical query satisfying that requirement"
        in delegation.request.message
    )



def test_causal_change_authority_projects_to_native_material_contract():
    engine = _db_engine()
    product = _product(engine)
    base = _brief(two=False)
    effect = base.questions[0].subject_refs[0]
    time_ref = next(
        item
        for item in base.scope.semantic_refs
        if item.candidate_id == "cand_sales_order_date"
    )
    candidate = ResearchSemanticRef(
        source_mention="iadeler",
        candidate_id="cand_return_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Return Count",
        cube_names=("satis_siparisleri",),
    )
    question = ResearchQuestion(
        goal_id="g-change",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Accepted window içindeki satış siparişi değişimini iadelerle değerlendir.",
        subject_refs=(effect, candidate),
        related_refs=(),
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id=effect.candidate_id,
            effect_observation=CausalEffectObservation.CHANGE,
            candidate_mechanism_semantic_ids=(candidate.candidate_id,),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = base.model_copy(
        update={
            "scope": base.scope.model_copy(
                update={
                    "semantic_refs": (
                        effect,
                        candidate,
                        time_ref,
                    ),
                    "time_surfaces": ("accepted two-month window",),
                    "periods": (
                        ResearchTimePeriod(
                            source_text="accepted two-month window",
                            time_dimension_candidate_id=time_ref.candidate_id,
                            start="2026-05-01",
                            end="2026-07-01",
                        ),
                    ),
                }
            ),
            "questions": (question,),
            "must_requirement_ids": ("g-change",),
        }
    )
    session = product.start_from_brief(
        brief=brief,
        request_ref="r-p14-change-authority",
        source_message_hash=hashlib.sha256(b"change authority").hexdigest(),
        principal=_principal(),
    )

    delegation = ResearchManager.prepare_native_delegation(
        session,
        obligation_id="g-change",
    )
    scope = delegation.request.context["dima_material_requirement"]

    assert scope["temporal_periods"] == [
        {
            "role": "material_window",
            "time_dimension_semantic_id": "cand_sales_order_date",
            "start": "2026-05-01",
            "end": "2026-07-01",
        }
    ]
    assert scope["temporal_observation_dimension"] == "cand_sales_order_date"
    assert "comparison" not in scope
    assert "period" not in scope
    assert "change_semantics" not in scope




def test_run_next_rejects_superseded_scope_before_any_native_work():
    engine = _db_engine()
    factory = BridgeFactory()
    executor = MaterialExecutor()
    product = _product(engine, factory, executor)

    original_brief = _brief(two=False)
    original = product.start_from_brief(
        brief=original_brief,
        request_ref="r-p14-stale-v1",
        source_message_hash=hashlib.sha256(b"stale v1").hexdigest(),
        principal=_principal(),
    )
    next_brief = original_brief.model_copy(
        update={
            "brief_id": "rb-product-p14-v2",
            "scope": original_brief.scope.model_copy(
                update={
                    "scope_version": ScopeVersion(
                        version_id="scope_v2",
                        ordinal=2,
                        parent_version_id="scope_v1",
                    )
                }
            ),
        }
    )
    newer = product.start_from_brief(
        brief=next_brief,
        request_ref="r-p14-stale-v2",
        source_message_hash=hashlib.sha256(b"stale v2").hexdigest(),
        principal=_principal(),
        prior_session_id=original.session_id,
    )
    assert newer.lineage_id == original.lineage_id
    assert newer.accepted_brief is not None
    assert newer.accepted_brief.scope.scope_version.version_id == "scope_v2"

    with pytest.raises(ResearchPersistenceError) as exc:
        product.run_next(
            session_id=original.session_id,
            principal=_principal(),
        )

    assert exc.value.code == "P14_RESEARCH_SCOPE_SUPERSEDED"
    assert factory.metabot_posts == 0
    assert executor.calls == []


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


def test_repairable_material_miss_uses_one_durable_same_metabot_repair():
    engine = _db_engine()
    factory = BridgeFactory()
    executor = MaterialExecutor(repairable_failures=1)
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
    store = ResearchSessionStore(engine)

    assert response.evidence_id is not None
    assert response.limitation_code is None
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert factory.metabot_posts == 2
    assert len(executor.calls) == 2
    assert executor.calls[0][3] != executor.calls[1][3]
    assert store.material_repair_attempt_count(
        session_id=session.session_id,
        obligation_id="g1",
    ) == 1
    verified = store.verified_link(
        session_id=session.session_id,
        obligation_id="g1",
    )
    assert verified.execution_kind == "P14_REPAIR"

    first, second = factory.metabot_bodies
    assert second["conversation_id"] == first["conversation_id"]
    assert second["history"]
    assert second["state"]
    assert "dima_analytical_scope" not in first["context"]
    assert "dima_analytical_scope" not in second["context"]
    assert (
        second["context"]["dima_material_requirement"]
        == first["context"]["dima_material_requirement"]
    )
    assert "[DIMA MATERIAL REQUIREMENT JSON]" in first["message"]
    assert "[DIMA MATERIAL REQUIREMENT JSON]" in second["message"]
    assert "[DIMA MATERIAL REPAIR FEEDBACK JSON]" in second["message"]
    assert "[DIMA MATERIAL REPAIR BOUNDARY]" in second["message"]
    assert "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE" in second["message"]
    assert second["context"]["dima_material_repair_feedback"] == {
        "schema": "dima_material_repair_feedback_v1",
        "validation_code": "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
        "validation_detail": "symbolic_reference_period",
        "repair_attempt": 1,
        "required_action": "REGENERATE_NATIVE_QUERY",
        "require_new_query_fingerprint": True,
        "preserve_scope_identity": True,
        "preserve_material_contract": True,
        "expected_semantic_shape": {
            "metric_refs": ["cand_sales_order_count"],
            "dimension_refs": ["cand_sales_order_channel"],
            "filters": [],
            "period": {
                "kind": "explicit_half_open",
                "time_dimension": "cand_sales_order_date",
                "start": "2026-06-01",
                "end": "2026-07-01",
            },
            "comparison": None,
            "temporal_observation": None,
            "temporal_change_frame": None,
            "ranking": None,
            "grain_constraints": ["cand_sales_order_channel"],
        },
    }


def test_second_repairable_material_miss_uses_final_bounded_regeneration():
    engine = _db_engine()
    factory = BridgeFactory()
    executor = MaterialExecutor(repairable_failures=2)
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
    store = ResearchSessionStore(engine)

    assert response.evidence_id is not None
    assert response.limitation_code is None
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert factory.metabot_posts == 3
    assert len(executor.calls) == 3
    assert len({call[3] for call in executor.calls}) == 3
    assert store.material_repair_attempt_count(
        session_id=session.session_id,
        obligation_id="g1",
    ) == 2


def test_third_repairable_material_miss_is_terminal_without_fourth_turn():
    engine = _db_engine()
    factory = BridgeFactory()
    executor = MaterialExecutor(repairable_failures=3)
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

    assert response.evidence_id is None
    assert (
        response.limitation_code
        == "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE"
    )
    assert restored.obligations[0].state == ObligationState.LIMITED
    assert factory.metabot_posts == 3
    assert len(executor.calls) == 3


def test_repair_must_generate_new_query_fingerprint():
    engine = _db_engine()
    factory = BridgeFactory(repeat_query_on_repair=True)
    executor = MaterialExecutor(repairable_failures=1)
    product = _product(engine, factory, executor)
    session = _start(product, two=False)

    response = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert response.evidence_id is None
    assert response.limitation_code == "P14_REPAIR_REPEATED_NATIVE_QUERY"
    assert factory.metabot_posts == 2
    assert len(executor.calls) == 1


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




def test_transient_observation_unavailable_resumes_same_occurrence_without_replaying_metabot():
    engine = _db_engine()
    store = ResearchSessionStore(engine)
    factory = BridgeFactory()
    executor = MaterialExecutor(
        observation_unavailable_failures=1,
        store=store,
    )
    product = ResearchAskOrchestrator(
        store=store,
        bridge_factory=factory,
        material_executor=executor,
    )
    session = _start(product, two=False)

    response = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )
    restored = product.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert response.evidence_id is not None
    assert response.limitation_code is None
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert factory.metabot_posts == 1
    assert len(executor.calls) == 2
    assert executor.calls[0][1] == executor.calls[1][1]
    assert executor.calls[0][2] == executor.calls[1][2]


def test_two_transient_observation_misses_resume_same_occurrence_without_replaying_metabot():
    engine = _db_engine()
    store = ResearchSessionStore(engine)
    factory = BridgeFactory()
    executor = MaterialExecutor(
        observation_unavailable_failures=2,
        store=store,
    )
    product = ResearchAskOrchestrator(
        store=store,
        bridge_factory=factory,
        material_executor=executor,
    )
    session = _start(product, two=False)

    response = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )
    restored = product.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert response.evidence_id is not None
    assert response.limitation_code is None
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert factory.metabot_posts == 1
    assert len(executor.calls) == 3
    assert len({item[1] for item in executor.calls}) == 1
    assert len({json.dumps(item[2], sort_keys=True) for item in executor.calls}) == 1


def test_three_observation_misses_recover_same_captured_occurrence_without_replay():
    engine = _db_engine()
    store = ResearchSessionStore(engine)
    factory = BridgeFactory()
    executor = MaterialExecutor(
        observation_unavailable_failures=3,
        store=store,
    )
    product = ResearchAskOrchestrator(
        store=store,
        bridge_factory=factory,
        material_executor=executor,
    )
    session = _start(product, two=False)

    response = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )
    restored = product.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert response.evidence_id is not None
    assert response.limitation_code is None
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert factory.metabot_posts == 1
    assert len(executor.calls) == 4
    assert len({item[1] for item in executor.calls}) == 1
    assert len({json.dumps(item[2], sort_keys=True) for item in executor.calls}) == 1


def test_five_observation_misses_stay_waiting_without_replaying_metabot():
    engine = _db_engine()
    store = ResearchSessionStore(engine)
    factory = BridgeFactory()
    executor = MaterialExecutor(
        observation_unavailable_failures=5,
        store=store,
    )
    product = ResearchAskOrchestrator(
        store=store,
        bridge_factory=factory,
        material_executor=executor,
    )
    session = _start(product, two=False)

    response = product.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )
    restored = product.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert response.evidence_id is None
    assert response.limitation_code == "NATIVE_QUERY_OCCURRENCE_NOT_FOUND"
    assert restored.obligations[0].state == ObligationState.DELEGATED
    assert factory.metabot_posts == 1
    assert len(executor.calls) == 5
    assert len({item[1] for item in executor.calls}) == 1
    assert len({json.dumps(item[2], sort_keys=True) for item in executor.calls}) == 1

def test_later_run_next_observes_same_waiting_occurrence_without_replay():
    engine = _db_engine()
    store = ResearchSessionStore(engine)
    factory = BridgeFactory()
    executor = MaterialExecutor(
        observation_unavailable_failures=5,
        store=store,
    )
    first = ResearchAskOrchestrator(
        store=store,
        bridge_factory=factory,
        material_executor=executor,
    )
    session = _start(first, two=False)

    waiting = first.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )
    assert waiting.evidence_id is None
    assert waiting.limitation_code == "NATIVE_QUERY_OCCURRENCE_NOT_FOUND"
    assert factory.metabot_posts == 1
    assert len(executor.calls) == 5
    pending = store.pending_link(
        session_id=session.session_id,
        obligation_id="g1",
    )
    assert pending is not None
    assert pending.status == "CANDIDATE_CAPTURED"
    assert pending.native_result_json is None
    captured_query_ids = {item[1] for item in executor.calls}
    captured_payloads = {json.dumps(item[2], sort_keys=True) for item in executor.calls}
    assert len(captured_query_ids) == 1
    assert len(captured_payloads) == 1

    # A later orchestration resume reconstructs the Product facade but must
    # observe the durable CANDIDATE_CAPTURED occurrence rather than reopen
    # cognition; execution may happen only after observation becomes READY.
    restarted = ResearchAskOrchestrator(
        store=store,
        bridge_factory=factory,
        material_executor=executor,
    )
    recovered = restarted.run_next(
        session_id=session.session_id,
        principal=_principal(),
    )
    restored = restarted.resume_state(
        session_id=session.session_id,
        principal=_principal(),
    )

    assert recovered.evidence_id is not None
    assert recovered.receipt_id is not None
    assert recovered.resumed_exact_occurrence is True
    assert restored.obligations[0].state == ObligationState.VERIFIED
    assert store.pending_link(
        session_id=session.session_id,
        obligation_id="g1",
    ) is None
    verified = store.verified_link(
        session_id=session.session_id,
        obligation_id="g1",
    )
    assert verified.native_query_id in captured_query_ids
    assert verified.evidence_id == recovered.evidence_id
    assert factory.metabot_posts == 1
    assert len(executor.calls) == 6
    assert {item[1] for item in executor.calls} == captured_query_ids
    assert {
        json.dumps(item[2], sort_keys=True) for item in executor.calls
    } == captured_payloads

    calls_after_verified = len(executor.calls)
    with pytest.raises(Exception) as terminal:
        restarted.run_next(
            session_id=session.session_id,
            principal=_principal(),
        )
    assert getattr(terminal.value, "code", None) == "P14_NO_OPEN_NATIVE_OBLIGATION"
    assert factory.metabot_posts == 1
    assert len(executor.calls) == calls_after_verified


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


