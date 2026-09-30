from __future__ import annotations

import hashlib
import json
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from uuid import UUID

import httpx
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.brain_v2.owner_adapter import DimaBrainV2Activities
from app.v3.brain_v2.service import BrainV2Service, BrainV2ThreadError
from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    CandidateAssessment,
    CausalQualification,
    ContributionClass,
    EvidenceStrength,
    HypothesisDisposition,
    HypothesisEpistemicClass,
    HypothesisRootCauseStore,
    RootCauseAssessmentDraft,
)
from app.v3.report_document import ReportDocumentStore
from app.v3.research_contracts import (
    CausalCompetitionSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ScopeVersion,
    SemanticTargetKind,
)
from app.v3.research_intake import (
    ResearchIntakeCatalog,
    ResearchIntakeResult,
    ResearchIntakeTerminal,
)
from app.v3.research_product import (
    ResearchAskOrchestrator,
    ResearchMaterialOutcome,
)
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal


NOW = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)
ENGINE_SHA = "0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
RUNTIME_TAG = "v0.63.18-dima.8"
ENGINE_IDENTITY = f"{RUNTIME_TAG}@{ENGINE_SHA}"
TENANT_ID = "00000000-0000-4000-8000-000000008201"
USER_ID = "00000000-0000-4000-8000-000000008202"
CONTEXT = "ctx-brain-v2-provider-free"


def _engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _principal() -> Principal:
    return Principal(
        user_id=USER_ID,
        tenant_id=TENANT_ID,
        tenant_slug="brain-v2-test",
        roles=["analyst"],
    )


def _semantic_refs(*, narrowed: bool = False):
    effect = ResearchSemanticRef(
        source_mention="duruş",
        candidate_id="metric.downtime",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Downtime Minutes",
        cube_names=("machine_operations",),
    )
    maintenance = ResearchSemanticRef(
        source_mention="bakım gecikmesi",
        candidate_id="metric.maintenance_delay",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Maintenance Delay",
        cube_names=("machine_operations",),
    )
    spare = ResearchSemanticRef(
        source_mention="yedek parça gecikmesi",
        candidate_id="metric.spare_part_delay",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Spare Part Delay",
        cube_names=("machine_operations",),
    )
    department = ResearchSemanticRef(
        source_mention="bölüm",
        candidate_id="dimension.department",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Department",
        cube_names=("machine_operations",),
    )
    refs = [effect, maintenance, spare, department]
    if narrowed:
        refs.append(
            ResearchSemanticRef(
                source_mention="Boyahane",
                candidate_id="entity.department.paint",
                target_kind=SemanticTargetKind.ENTITY_VALUE,
                canonical_name="Boyahane",
                dimension_name="Department",
                value="Boyahane",
                cube_names=("machine_operations",),
            )
        )
    return tuple(refs)


def _brief(*, ordinal: int = 1, narrowed: bool = False) -> ResearchBrief:
    refs = _semantic_refs(narrowed=narrowed)
    by_id = {item.candidate_id: item for item in refs}
    question = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text=(
            "Duruş artışını bakım gecikmesi mi yedek parça gecikmesi mi "
            "daha iyi açıklıyor?"
        ),
        subject_refs=(by_id["metric.downtime"],),
        related_refs=(
            by_id["metric.maintenance_delay"],
            by_id["metric.spare_part_delay"],
            by_id["dimension.department"],
        ),
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id="metric.downtime",
            candidate_mechanism_semantic_ids=(
                "metric.maintenance_delay",
                "metric.spare_part_delay",
            ),
            diagnostic_dimension_ids=("dimension.department",),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    version = ScopeVersion(
        version_id=f"scope_v{ordinal}",
        ordinal=ordinal,
        parent_version_id=(None if ordinal == 1 else f"scope_v{ordinal - 1}"),
    )
    return ResearchBrief(
        brief_id=f"rb-brain-v2-{ordinal}-{'paint' if narrowed else 'all'}",
        objective=question.source_text,
        scope=ResearchScope(
            semantic_refs=refs,
            scope_version=version,
        ),
        questions=(question,),
        must_requirement_ids=(question.goal_id,),
        context_version=CONTEXT,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _catalog() -> ResearchIntakeCatalog:
    return ResearchIntakeCatalog(
        context_version=CONTEXT,
        semantic_refs=_semantic_refs(narrowed=True),
        supported_domains=("machine_operations",),
    )


class DeterministicIntake:
    def __init__(self) -> None:
        self.call_count = 0

    def compile(self, *, question, catalog, prior_brief=None):
        del question
        self.call_count += 1
        ordinal = 1 if prior_brief is None else prior_brief.scope.scope_version.ordinal + 1
        brief = _brief(
            ordinal=ordinal,
            narrowed=prior_brief is not None,
        )
        return ResearchIntakeResult(
            terminal=ResearchIntakeTerminal.READY,
            brief=brief,
            catalog_fingerprint=catalog.fingerprint,
            model_calls=1,
        )


class BridgeFactory:
    def __init__(self) -> None:
        self.metabot_posts = 0

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
                return httpx.Response(200, json={"version": {"tag": RUNTIME_TAG}})
            if (
                request.method == "POST"
                and request.url.path == "/api/metabot/agent-streaming"
            ):
                self.metabot_posts += 1
                native_query = {
                    "database": 1,
                    "type": "query",
                    "query": {
                        "source-table": 10,
                        "aggregation": [["sum", ["field", 20, None]]],
                        "breakout": [["field", 30, None]],
                    },
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
            session_token="provider-free-native-session",
            expected_identity=NativeEngineIdentity(
                engine_sha=ENGINE_SHA,
                upstream_base_sha=UPSTREAM_SHA,
                runtime_tag=RUNTIME_TAG,
            ),
            transport=httpx.MockTransport(handler),
        )


class DurableMaterialExecutor:
    def __init__(self, store: ResearchSessionStore) -> None:
        self.store = store
        self.calls = 0

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
        **kwargs,
    ) -> ResearchMaterialOutcome:
        del principal, bridge, native_query, kwargs
        self.calls += 1
        self.store.mark_execution_started(
            execution_link_id,
            native_subject_ref="metabase-user:82",
        )
        result = {
            "database_id": 1,
            "row_count": 2,
            "data": {
                "rows": [
                    ["maintenance_delay", 41],
                    ["spare_part_delay", 33],
                ]
            },
        }
        raw = json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        result_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        self.store.mark_executed(
            execution_link_id,
            native_subject_ref="metabase-user:82",
            runtime_identity={
                "substrate": "metabase-native",
                "runtime_version": RUNTIME_TAG,
                "image_digest": "sha256:" + "8" * 64,
                "database_id": "metabase:1",
            },
            result_payload=result,
            result_hash=result_hash,
            executed_at=NOW,
        )

        suffix = hashlib.sha256(
            f"{session.session_id}:{obligation_id}".encode()
        ).hexdigest()[:24]
        receipt = DimaQueryReceipt(
            receipt_id="dqr_" + suffix,
            receipt_fingerprint=hashlib.sha256(
                f"receipt:{suffix}".encode()
            ).hexdigest(),
            execution_id=f"native-dataset:{execution_link_id}",
            step_role="primary",
            authority_kind="research_material",
            authority_id=session.authority_id,
            obligation_ids=(obligation_id,),
            tenant_id=session.tenant_binding,
            principal_id=session.principal_subject,
            semantic_refs=(),
            research_session_id=session.session_id,
            native_subject_ref="metabase-user:82",
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            native_query_provenance_ref=(
                f"research-execution-link:{execution_link_id}:query"
            ),
            native_result_provenance_ref=(
                f"research-execution-link:{execution_link_id}:result"
            ),
            canonical_query_fingerprint=query_fingerprint,
            principal_fingerprint="8" * 64,
            semantic_context_version=session.context_version,
            substrate="metabase-native",
            substrate_runtime_version=RUNTIME_TAG,
            substrate_image_digest="sha256:" + "8" * 64,
            engine_repository="UpcyTech/dima-metabase-engine",
            engine_revision_sha=ENGINE_SHA,
            engine_upstream_base_sha=UPSTREAM_SHA,
            engine_runtime_tag=RUNTIME_TAG,
            engine_build_identity=f"github-actions:36610103287:{ENGINE_SHA}",
            engine_image_identity=(
                "ghcr.io/upcytech/dima-metabase-engine@sha256:" + "8" * 64
            ),
            engine_runtime_instance_id=UUID(
                "00000000-0000-4000-8000-000000008203"
            ),
            database_id="metabase:1",
            executed_at=NOW,
            result_hash=result_hash,
            row_count=2,
        )
        evidence = EvidenceArtifact(
            artifact_id="evi_" + suffix,
            authority_id=session.authority_id,
            obligation_ids=(obligation_id,),
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="brain_v2_provider_free_native",
            state=EvidenceState.VERIFIED,
            payload={"result_hash": result_hash},
        )
        return ResearchMaterialOutcome(
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            receipt=receipt,
            evidence=evidence,
        )


class DeterministicP19Manager:
    def __init__(self) -> None:
        self.call_count = 0

    def propose(
        self,
        snapshot,
        *,
        policy_statuses=None,
        deterministic_feedback_code=None,
    ):
        del policy_statuses, deterministic_feedback_code
        self.call_count += 1
        candidates = []
        for item in snapshot.hypotheses:
            candidates.append(
                CandidateAssessment(
                    hypothesis_id=item.hypothesis.hypothesis_id,
                    grounding_link_ids=tuple(
                        link.grounding_link_id for link in item.groundings
                    ),
                    disposition=HypothesisDisposition.RETAINED,
                    epistemic_class=HypothesisEpistemicClass.CONTRIBUTION,
                    contribution_class=ContributionClass.MATERIAL,
                    evidence_strength=EvidenceStrength.MODERATE,
                    causal_qualification=CausalQualification.NOT_CLAIMED,
                    identification_limitations=(),
                )
            )
        return RootCauseAssessmentDraft(
            research_session_id=snapshot.research_session_id,
            obligation_id=snapshot.obligation_id,
            candidates=tuple(candidates),
            aggregate_outcome=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
            root_cause_hypothesis_ids=(),
            limitations=("Provider-free fixture preserves causal ceiling.",),
        )


class BombP17:
    def __getattr__(self, name):
        raise AssertionError(f"ONE_PASS must not invoke P17: {name}")


def _stack():
    db = _engine()
    store = ResearchSessionStore(db)
    bridge = BridgeFactory()
    material = DurableMaterialExecutor(store)
    research = ResearchAskOrchestrator(
        store=store,
        bridge_factory=bridge,
        material_executor=material,
    )
    principal = _principal()
    p19 = HypothesisRootCauseStore(
        research_store=store,
        db_engine=db,
    )
    p19_manager = DeterministicP19Manager()
    activities = DimaBrainV2Activities(
        principal=principal,
        catalog=_catalog(),
        intake=DeterministicIntake(),
        research=research,
        investigation=BombP17(),
        investigation_manager=BombP17(),
        epistemics=p19,
        epistemic_manager=p19_manager,
        reports=ReportDocumentStore(
            research_store=store,
            db_engine=db,
        ),
        native_session_token="provider-free-native-session",
        engine_identity=ENGINE_IDENTITY,
    )
    return db, store, bridge, material, p19, p19_manager, activities


def test_real_owner_one_pass_uses_one_native_and_zero_p17() -> None:
    _, store, bridge, material, p19, p19_manager, activities = _stack()
    service = BrainV2Service(activities=activities)

    result = service.run(
        BrainGraphState(
            thread_id="real-one-pass",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Provider-free ONE_PASS RCA.",
        )
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert result.scope_version_id == "scope_v1"
    assert bridge.metabot_posts == 1
    assert material.calls == 1
    assert p19_manager.call_count == 1
    assert len(result.evidence_ids) == 1
    assert len(result.hypothesis_ids) == 2
    assert result.latest_p19_assessment_ref is not None
    assert result.report_ref is not None

    session = store.load(
        result.research_session_id,
        tenant=f"id:{TENANT_ID}",
        principal=USER_ID,
    )
    assert session.stopping.status.value == "COMPLETE"
    assert len(session.evidence_refs) == 1
    assessment = p19.load_assessment(
        assessment_id=result.latest_p19_assessment_ref,
        principal=_principal(),
    )
    assert assessment.aggregate_outcome == AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS

    # Exact current-session material is safely reusable without another native call.
    before = bridge.metabot_posts
    replay = activities.acquire_material(result)
    assert replay.produced_evidence_ids == result.evidence_ids
    assert bridge.metabot_posts == before


def test_real_owner_scope_repair_creates_new_scope_without_stale_evidence_reuse() -> None:
    _, store, bridge, _, _, _, activities = _stack()
    service = BrainV2Service(activities=activities)
    first = service.run(
        BrainGraphState(
            thread_id="real-scope-repair",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Initial governed RCA.",
        )
    )
    second = service.continue_turn(
        thread_id="real-scope-repair",
        tenant_binding=f"id:{TENANT_ID}",
        principal_ref=USER_ID,
        user_input="Boyahane ile sınırla.",
    )

    assert first.scope_version_id == "scope_v1"
    assert second.scope_version_id == "scope_v2"
    assert first.research_session_id != second.research_session_id
    assert set(first.evidence_ids).isdisjoint(second.evidence_ids)
    assert bridge.metabot_posts == 2

    first_session = store.load(
        first.research_session_id,
        tenant=f"id:{TENANT_ID}",
        principal=USER_ID,
    )
    second_session = store.load(
        second.research_session_id,
        tenant=f"id:{TENANT_ID}",
        principal=USER_ID,
    )
    assert first_session.lineage_id == second_session.lineage_id
    assert first_session.accepted_brief.scope.scope_version.version_id == "scope_v1"
    assert second_session.accepted_brief.scope.scope_version.version_id == "scope_v2"
    assert store.assert_lineage_head(second_session) == second_session
    with pytest.raises(Exception):
        store.assert_lineage_head(first_session)


def test_real_owner_foreign_thread_replay_is_blocked_before_owner_work() -> None:
    _, _, bridge, material, _, p19_manager, activities = _stack()
    service = BrainV2Service(activities=activities)
    service.run(
        BrainGraphState(
            thread_id="real-security",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Initial governed RCA.",
        )
    )
    before = (bridge.metabot_posts, material.calls, p19_manager.call_count)

    with pytest.raises(BrainV2ThreadError):
        service.continue_turn(
            thread_id="real-security",
            tenant_binding="id:00000000-0000-4000-8000-000000009999",
            principal_ref="foreign-user",
            user_input="Replay foreign thread.",
        )

    assert (bridge.metabot_posts, material.calls, p19_manager.call_count) == before
