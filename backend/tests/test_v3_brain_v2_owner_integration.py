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
from app.v3.business_relationship_policy import BusinessRelationshipPolicyStore
from app.v3.claim_lineage import (
    ClaimEvidenceRelation,
    ClaimFreshness,
    ClaimLineageStore,
)
from app.v3.product.composition import HeadlessProductComposer
from app.v3.research_manager import (
    InvestigationIntent,
    InvestigationTargetKind,
    ManagerAction,
    ManagerProposal,
    ProposedClaimDraft,
    ProposedClaimEvidenceLink,
    ResearchInvestigationManager,
    ResearchReasoningStore,
)

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
    ResearchDeliverableRequirement,
    ResearchScope,
    ResearchSemanticRef,
    ScopeVersion,
    SemanticTargetKind,
    PresentationKind,
)
from app.v3.research_intake import (
    ResearchIntakeCatalog,
    ResearchIntakeResult,
    ResearchIntakeTerminal,
)
from app.v3.research_product import (
    NativeResearchOccurrenceRunner,
    ResearchAskOrchestrator,
    ResearchMaterialOutcome,
)
from app.v3.research_followup import NativeResearchFollowupExecutor
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


def _brief(
    *,
    ordinal: int = 1,
    narrowed: bool = False,
    user_seeded: bool = True,
) -> ResearchBrief:
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
                (
                    "metric.maintenance_delay",
                    "metric.spare_part_delay",
                )
                if user_seeded
                else ()
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
        deliverables=(
            ResearchDeliverableRequirement(
                requirement_id="r_report",
                kind=PresentationKind.REPORT,
                source_text="Yönetim raporu olarak sun.",
            ),
        ),
        must_requirement_ids=(question.goal_id, "r_report"),
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
            f"{session.session_id}:{obligation_id}:{self.calls}".encode()
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
            limitations=(),
        )


class AdaptiveP19Manager:
    """First assessment requests discrimination; second terminates safely."""

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
        candidates = tuple(
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
            for item in snapshot.hypotheses
        )
        return RootCauseAssessmentDraft(
            research_session_id=snapshot.research_session_id,
            obligation_id=snapshot.obligation_id,
            candidates=candidates,
            aggregate_outcome=(
                AggregateOutcome.IN_PROGRESS
                if self.call_count == 1
                else AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS
            ),
            root_cause_hypothesis_ids=(),
            limitations=(),
        )


class DiscoveryIntake:
    def __init__(self) -> None:
        self.call_count = 0

    def compile(self, *, question, catalog, prior_brief=None):
        del question
        self.call_count += 1
        ordinal = (
            1
            if prior_brief is None
            else prior_brief.scope.scope_version.ordinal + 1
        )
        brief = _brief(
            ordinal=ordinal,
            narrowed=prior_brief is not None,
            user_seeded=False,
        )
        return ResearchIntakeResult(
            terminal=ResearchIntakeTerminal.READY,
            brief=brief,
            catalog_fingerprint=catalog.fingerprint,
            model_calls=1,
        )


class DeterministicDiscoveryManager:
    """Provider-free stand-in for governed P17 root-candidate cognition."""

    def __init__(self) -> None:
        self.call_count = 0

    def propose_root_candidate_for_obligation_with_constraints(
        self,
        snapshot,
        *,
        target_parent_obligation,
        allowed_evidence_refs,
        allowed_mechanism_refs,
        allowed_intents,
    ):
        assert allowed_intents == (InvestigationIntent.FORM_CLAIM,)
        assert len(allowed_mechanism_refs) >= 2
        self.call_count += 1
        mechanism = allowed_mechanism_refs[self.call_count - 1]
        rule = snapshot.action_profile.rule_for(
            InvestigationIntent.FORM_CLAIM
        )
        assert rule is not None
        parent = (
            rule.legal_parent_step_ids[-1]
            if rule.legal_parent_step_ids
            else None
        )
        assert parent is not None or rule.allow_parentless

        evidence_id = allowed_evidence_refs[0]
        return ManagerProposal(
            proposal_id=f"discovery-{self.call_count}",
            source_revision=snapshot.source_revision,
            target_parent_obligation=target_parent_obligation,
            action=ManagerAction.FORM_CLAIM,
            intent=InvestigationIntent.FORM_CLAIM,
            parent_step_id=parent,
            branch_key=None,
            target_kind=InvestigationTargetKind.EXPLANATION,
            target_ref=mechanism,
            objective_key=f"discover.{self.call_count}",
            bounded_objective=(
                "Form one governed explanatory candidate from existing "
                "verified Evidence."
            ),
            rationale="Bounded governed candidate discovery.",
            inspected_evidence_refs=(evidence_id,),
            inspected_claim_refs=(),
            inspected_material_refs=(),
            expected_information_gain="Add one distinct governed alternative.",
            claim=ProposedClaimDraft(
                claim_text=f"Governed explanatory candidate {self.call_count}.",
                proposition={
                    "candidate_index": self.call_count,
                    "mechanism_ref": mechanism,
                },
                scope={"scope_version_id": "scope_v1"},
                freshness=ClaimFreshness(as_of=NOW),
                evidence_links=(
                    ProposedClaimEvidenceLink(
                        evidence_id=evidence_id,
                        relation=ClaimEvidenceRelation.CONTEXTUALIZES,
                    ),
                ),
            ),
            mechanism_semantic_ref=mechanism,
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



def test_legacy_v2_shadow_replay_preserves_semantic_product_outcome() -> None:
    question = "Provider-free ONE_PASS RCA."
    thread_id = "shadow-one-pass"

    # Brain V2 path.
    _, v2_store, _, _, v2_p19, _, v2_activities = _stack()
    v2 = BrainV2Service(activities=v2_activities).run(
        BrainGraphState(
            thread_id=thread_id,
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input=question,
        )
    )
    v2_session = v2_store.load(
        v2.research_session_id,
        tenant=f"id:{TENANT_ID}",
        principal=USER_ID,
    )
    v2_assessment = v2_p19.load_assessment(
        assessment_id=v2.latest_p19_assessment_ref,
        principal=_principal(),
    )
    v2_report = ReportDocumentStore(
        research_store=v2_store,
        db_engine=v2_store._engine,
    ).load(
        report_id=v2.report_ref,
        principal=_principal(),
    )

    # Frozen legacy semantic reference over the same typed fixture.
    legacy_db = _engine()
    legacy_store = ResearchSessionStore(legacy_db)
    legacy_bridge = BridgeFactory()
    legacy_material = DurableMaterialExecutor(legacy_store)
    legacy_research = ResearchAskOrchestrator(
        store=legacy_store,
        bridge_factory=legacy_bridge,
        material_executor=legacy_material,
    )
    legacy_claims = ClaimLineageStore(
        research_store=legacy_store,
        db_engine=legacy_db,
    )
    legacy_reasoning = ResearchReasoningStore(legacy_db)
    legacy_investigation = ResearchInvestigationManager(
        research_store=legacy_store,
        claim_store=legacy_claims,
        reasoning_store=legacy_reasoning,
        db_engine=legacy_db,
    )
    legacy_p19 = HypothesisRootCauseStore(
        research_store=legacy_store,
        db_engine=legacy_db,
    )
    legacy_reports = ReportDocumentStore(
        research_store=legacy_store,
        db_engine=legacy_db,
    )
    legacy = HeadlessProductComposer(
        research=legacy_research,
        investigation=legacy_investigation,
        investigation_manager=BombP17(),
        reasoning=legacy_reasoning,
        relationships=BusinessRelationshipPolicyStore(
            research_store=legacy_store,
            db_engine=legacy_db,
        ),
        epistemics=legacy_p19,
        epistemic_manager=DeterministicP19Manager(),
        reports=legacy_reports,
    ).compose(
        brief=_brief(),
        principal=_principal(),
        request_ref=f"brain-v2:{thread_id}:{_brief().brief_id}",
        source_message_hash=hashlib.sha256(question.encode("utf-8")).hexdigest(),
        native_session_token="provider-free-native-session",
    )

    legacy_session = legacy_store.load(
        legacy.research_session_id,
        tenant=f"id:{TENANT_ID}",
        principal=USER_ID,
    )
    assert len(legacy.p19_assessment_refs) == 1
    legacy_assessment = legacy_p19.load_assessment(
        assessment_id=legacy.p19_assessment_refs[0],
        principal=_principal(),
    )
    assert legacy.p20_report_ref is not None
    legacy_report = legacy_reports.load(
        report_id=legacy.p20_report_ref,
        principal=_principal(),
    )

    assert v2_session.accepted_brief.scope == legacy_session.accepted_brief.scope
    assert tuple(x.evidence_id for x in v2_session.evidence_refs) == tuple(
        x.evidence_id for x in legacy_session.evidence_refs
    )
    assert v2.hypothesis_ids == tuple(
        item.hypothesis.hypothesis_id
        for item in legacy_p19.snapshot(
            research_session_id=legacy_session.session_id,
            obligation_id="g_root",
            principal=_principal(),
        ).hypotheses
    )
    assert v2_assessment.aggregate_outcome == legacy_assessment.aggregate_outcome
    assert v2_assessment.root_cause_hypothesis_ids == (
        legacy_assessment.root_cause_hypothesis_ids
    )
    assert tuple(x.coverage_status for x in v2_report.coverage) == tuple(
        x.coverage_status for x in legacy_report.coverage
    )
    assert tuple(x.obligation_id for x in v2_report.coverage) == tuple(
        x.obligation_id for x in legacy_report.coverage
    )
    assert legacy_bridge.metabot_posts == 1



def _adaptive_stack(*, discovery: bool = False):
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
    claims = ClaimLineageStore(
        research_store=store,
        db_engine=db,
    )
    reasoning = ResearchReasoningStore(db)
    occurrence = NativeResearchOccurrenceRunner(
        store=store,
        bridge_factory=bridge,
        material_executor=material,
    )
    investigation = ResearchInvestigationManager(
        research_store=store,
        claim_store=claims,
        reasoning_store=reasoning,
        followup_executor=NativeResearchFollowupExecutor(
            store=store,
            occurrence_runner=occurrence,
        ),
        db_engine=db,
    )
    p19 = HypothesisRootCauseStore(
        research_store=store,
        db_engine=db,
    )
    p19_manager = (
        DeterministicP19Manager()
        if discovery
        else AdaptiveP19Manager()
    )
    discovery_manager = (
        DeterministicDiscoveryManager()
        if discovery
        else BombP17()
    )
    activities = DimaBrainV2Activities(
        principal=principal,
        catalog=_catalog(),
        intake=(DiscoveryIntake() if discovery else DeterministicIntake()),
        research=research,
        investigation=investigation,
        investigation_manager=discovery_manager,
        epistemics=p19,
        epistemic_manager=p19_manager,
        reports=ReportDocumentStore(
            research_store=store,
            db_engine=db,
        ),
        native_session_token="provider-free-native-session",
        engine_identity=ENGINE_IDENTITY,
    )
    return (
        db,
        store,
        bridge,
        material,
        investigation,
        p19,
        p19_manager,
        discovery_manager,
        activities,
    )


def test_real_owner_adaptive_runs_one_typed_followup_without_duplicate_native() -> None:
    (
        _,
        _,
        bridge,
        material,
        investigation,
        _,
        p19_manager,
        _,
        activities,
    ) = _adaptive_stack()
    service = BrainV2Service(activities=activities)

    result = service.run(
        BrainGraphState(
            thread_id="real-adaptive",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Provider-free ADAPTIVE RCA.",
        )
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert result.adaptive_reentries == 1
    assert bridge.metabot_posts == 2
    assert material.calls == 2
    assert p19_manager.call_count == 2
    assert len(result.evidence_ids) == 2
    snapshot = investigation.snapshot(
        session_id=result.research_session_id,
        principal=_principal(),
    )
    next_test_steps = tuple(
        node
        for node in snapshot.investigation.nodes
        if node.intent == InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
    )
    assert len(next_test_steps) == 1
    assert len(snapshot.evidence_results) == 2


def test_real_owner_discovery_forms_governed_candidates_without_extra_native() -> None:
    (
        _,
        _,
        bridge,
        material,
        investigation,
        p19,
        p19_manager,
        discovery_manager,
        activities,
    ) = _adaptive_stack(discovery=True)
    service = BrainV2Service(activities=activities)

    result = service.run(
        BrainGraphState(
            thread_id="real-discovery",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Provider-free DISCOVERY RCA.",
        )
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert bridge.metabot_posts == 1
    assert material.calls == 1
    assert discovery_manager.call_count == 2
    assert p19_manager.call_count == 1
    assert result.discovery_turns == 2
    assert len(result.hypothesis_ids) == 2

    snapshot = investigation.snapshot(
        session_id=result.research_session_id,
        principal=_principal(),
    )
    assert len(snapshot.claims) == 2
    assert all(claim.evidence_links for claim in snapshot.claims)
    epistemic = p19.snapshot(
        research_session_id=result.research_session_id,
        obligation_id="g_root",
        principal=_principal(),
    )
    assert len(epistemic.hypotheses) == 2
    assert all(item.groundings for item in epistemic.hypotheses)
