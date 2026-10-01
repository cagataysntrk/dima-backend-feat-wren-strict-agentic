from __future__ import annotations

import hashlib
import json
import os
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from uuid import UUID

import httpx
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.brain_v2.adaptive_owner_adapter import (
    AdaptiveDimaBrainV2Activities as DimaBrainV2Activities,
)
from app.v3.brain_v2.service import BrainV2Service, BrainV2ThreadError
from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus
from app.v3.brain_v2.owner_adapter import BrainV2OwnerError
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.business_relationship_policy import BusinessRelationshipPolicyStore
from app.v3.claim_lineage import (
    ClaimEvidenceRelation,
    ClaimFreshness,
    ClaimLineageStore,
)
from app.v3.product.composition import HeadlessProductComposer
from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.research_manager import (
    InvestigationIntent,
    InvestigationTargetKind,
    ManagerAction,
    ManagerProposal,
    ManagerStopReason,
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
    IdentificationLimitation,
    RootCauseAssessmentDraft,
)
from app.v3.report_document import (
    ReportDocumentStore,
    ReportSourceKind,
    ReportStatementKind,
)
from app.v3.research_contracts import (
    CausalCompetitionSurface,
    CausalEffectObservation,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchDeliverableRequirement,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeVersion,
    TemporalRole,
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


def _postgres_engine():
    dsn = os.environ.get("DIMA_BRAIN_V2_TEST_POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("provider-free Postgres DSN is not configured")
    sqlalchemy_dsn = (
        "postgresql+psycopg://" + dsn.removeprefix("postgresql://")
        if dsn.startswith("postgresql://")
        else dsn
    )
    engine = create_engine(sqlalchemy_dsn, pool_pre_ping=True)
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


class AdaptiveIntake(DeterministicIntake):
    """Provider-free typed adaptive intent emitted by the canonical Intake contract."""

    def compile(self, *, question, catalog, prior_brief=None):
        result = super().compile(
            question=question,
            catalog=catalog,
            prior_brief=prior_brief,
        )
        assert result.brief is not None
        brief = result.brief
        goal = brief.questions[0]
        time_ref = ResearchSemanticRef(
            source_mention="accepted event time",
            candidate_id="dimension.event_date",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Event Date",
            cube_names=("machine_operations",),
        )
        causal = goal.causal_competition
        assert causal is not None
        goal = goal.model_copy(
            update={
                "causal_competition": causal.model_copy(
                    update={
                        "effect_observation": CausalEffectObservation.LEVEL,
                    }
                )
            }
        )
        scope = brief.scope.model_copy(
            update={
                "semantic_refs": (*brief.scope.semantic_refs, time_ref),
                "time_surfaces": ("accepted May-June window",),
                "periods": (
                    ResearchTimePeriod(
                        source_text="accepted May-June window",
                        time_dimension_candidate_id="dimension.event_date",
                        start="2026-05-01",
                        end="2026-07-01",
                        role=TemporalRole.MATERIAL_WINDOW,
                    ),
                ),
                "temporal_dimension_ids": ("dimension.event_date",),
            }
        )
        brief = brief.model_copy(
            update={
                "questions": (goal,),
                "scope": scope,
            }
        )
        goal_id = goal.goal_id
        return result.model_copy(
            update={
                "brief": brief,
                "investigation_requirements": (
                    ProductInvestigationRequirement(
                        requirement_id="pir_" + "a" * 20,
                        kind=(
                            ProductInvestigationRequirementKind
                            .FOLLOW_VERIFIED_MATERIAL
                        ),
                        source_goal_id=goal_id,
                        source_text=(
                            "If verified Evidence remains ambiguous, follow one "
                            "material discriminating direction."
                        ),
                    ),
                )
            }
        )


class BridgeFactory:
    def __init__(self) -> None:
        self.metabot_posts = 0
        self.metabot_requests: list[dict] = []

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
                request.method == "GET"
                and request.url.path.startswith("/api/metabot/conversations/")
            ):
                assert self.metabot_requests, (
                    "conversation history is legal only after a native turn"
                )
                first = self.metabot_requests[0]
                parent_query_id = (
                    f"native-{session.session_id}-1"
                )
                return httpx.Response(
                    200,
                    json={
                        "conversation_id": first["conversation_id"],
                        "chat_messages": [
                            {
                                "id": "pf-user-1",
                                "role": "user",
                                "type": "text",
                                "message": first["message"],
                            },
                            {
                                "id": "pf-tool-1",
                                "role": "agent",
                                "type": "tool_call",
                                "name": "construct_notebook_query",
                                "args": "{}",
                                "result": json.dumps(
                                    {"query-id": parent_query_id},
                                    separators=(",", ":"),
                                ),
                                "status": "ended",
                                "is_error": False,
                            },
                        ],
                    },
                )
            if (
                request.method == "POST"
                and request.url.path == "/api/metabot/agent-streaming"
            ):
                payload = json.loads(request.content.decode("utf-8"))
                self.metabot_requests.append(payload)
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
                native_state = {
                    "queries": {query_id: native_query},
                    "charts": {},
                    "todos": [],
                    "transforms": {},
                    "link-registry": {},
                }
                return httpx.Response(
                    202,
                    text=(
                        "2:"
                        + json.dumps(generated, separators=(",", ":"))
                        + "\n2:"
                        + json.dumps(
                            {"type": "state", "value": native_state},
                            separators=(",", ":"),
                        )
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
    def __init__(
        self,
        store: ResearchSessionStore,
        *,
        repeat_followup_result: bool = False,
    ) -> None:
        self.store = store
        self.calls = 0
        self.repeat_followup_result = repeat_followup_result

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
        del principal, bridge, native_query
        self.calls += 1
        self.store.mark_execution_started(
            execution_link_id,
            native_subject_ref="metabase-user:82",
        )
        analytical_scope = kwargs.get("analytical_scope")
        temporal_discrimination = (
            analytical_scope is not None
            and "dimension.event_date"
            in set(analytical_scope.dimension_refs)
        )
        result = {
            "database_id": 1,
            "row_count": 2,
            "data": {
                "rows": (
                    [
                        ["maintenance_delay", 41],
                        ["spare_part_delay", 33],
                    ]
                    if (
                        temporal_discrimination
                        and self.repeat_followup_result
                    )
                    else (
                        [
                            ["2026-05-15", "maintenance_delay", 18],
                            ["2026-06-15", "spare_part_delay", 29],
                        ]
                        if temporal_discrimination
                        else [
                            ["maintenance_delay", 41],
                            ["spare_part_delay", 33],
                        ]
                    )
                )
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


class ScopeAwareP19Manager(DeterministicP19Manager):
    """Capture the typed current-scope authority presented to P19."""

    def __init__(self) -> None:
        super().__init__()
        self.context_calls = []

    def propose_with_context(
        self,
        snapshot,
        *,
        objective,
        scope_authority,
        discriminating_test_available,
        policy_statuses=None,
        deterministic_feedback_code=None,
    ):
        self.context_calls.append(
            {
                "objective": objective,
                "scope_authority": scope_authority,
                "discriminating_test_available": discriminating_test_available,
                "deterministic_feedback_code": deterministic_feedback_code,
            }
        )
        return self.propose(
            snapshot,
            policy_statuses=policy_statuses,
            deterministic_feedback_code=deterministic_feedback_code,
        )


class UncertainP19Manager:
    """Terminal P19 assessment with exact epistemic limitations."""

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
                epistemic_class=HypothesisEpistemicClass.ASSOCIATION,
                contribution_class=ContributionClass.UNKNOWN,
                evidence_strength=EvidenceStrength.WEAK,
                causal_qualification=CausalQualification.IDENTIFICATION_LIMITED,
                identification_limitations=(
                    IdentificationLimitation.ASSOCIATION_ONLY,
                    IdentificationLimitation.TEMPORAL_ORDER_UNESTABLISHED,
                    IdentificationLimitation.CONFOUNDING_NOT_RESOLVED,
                ),
            )
            for item in snapshot.hypotheses
        )
        return RootCauseAssessmentDraft(
            research_session_id=snapshot.research_session_id,
            obligation_id=snapshot.obligation_id,
            candidates=candidates,
            aggregate_outcome=AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED,
            root_cause_hypothesis_ids=(),
            limitations=(
                "Observed material is associative only.",
                "Temporal order and confounding remain unresolved.",
            ),
        )


class AdaptiveP19Manager:
    """First assessment requests discrimination; second terminates safely."""

    def __init__(self) -> None:
        self.call_count = 0

        self.context_calls = []

    def propose_with_context(
        self,
        snapshot,
        *,
        objective,
        scope_authority=None,
        discriminating_test_available,
        policy_statuses=None,
        deterministic_feedback_code=None,
    ):
        self.context_calls.append(
            {
                "objective": objective,
                "scope_authority": scope_authority,
                "discriminating_test_available": discriminating_test_available,
                "deterministic_feedback_code": deterministic_feedback_code,
            }
        )
        return self.propose(
            snapshot,
            policy_statuses=policy_statuses,
            deterministic_feedback_code=deterministic_feedback_code,
        )

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
        assert InvestigationIntent.FORM_CLAIM in allowed_intents
        assert set(allowed_intents).issubset(
            {
                InvestigationIntent.FORM_CLAIM,
                InvestigationIntent.STOP_INVESTIGATION,
            }
        )
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



class GreedyFirstDiscoveryManager(DeterministicDiscoveryManager):
    """Always choose the first currently authorized governed mechanism."""

    def __init__(self) -> None:
        super().__init__()
        self.allowed_history: list[tuple[str, ...]] = []

    def propose_root_candidate_for_obligation_with_constraints(
        self,
        snapshot,
        *,
        target_parent_obligation,
        allowed_evidence_refs,
        allowed_mechanism_refs,
        allowed_intents,
    ):
        self.allowed_history.append(tuple(allowed_mechanism_refs))
        assert allowed_mechanism_refs
        assert InvestigationIntent.FORM_CLAIM in allowed_intents
        self.call_count += 1
        mechanism = allowed_mechanism_refs[0]
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
            proposal_id=f"greedy-discovery-{self.call_count}",
            source_revision=snapshot.source_revision,
            target_parent_obligation=target_parent_obligation,
            action=ManagerAction.FORM_CLAIM,
            intent=InvestigationIntent.FORM_CLAIM,
            parent_step_id=parent,
            branch_key=None,
            target_kind=InvestigationTargetKind.EXPLANATION,
            target_ref=mechanism,
            objective_key=f"greedy.discover.{self.call_count}",
            bounded_objective="Form one governed explanatory candidate.",
            rationale="Choose one currently authorized governed candidate.",
            inspected_evidence_refs=(evidence_id,),
            inspected_claim_refs=(),
            inspected_material_refs=(),
            expected_information_gain="Add one distinct governed alternative.",
            claim=ProposedClaimDraft(
                claim_text=f"Greedy governed candidate {self.call_count}.",
                proposition={"mechanism_ref": mechanism},
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


class DeterministicDiscoveryStopManager:
    """Provider-free P17 stand-in for honest discovery exhaustion."""

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
        assert InvestigationIntent.FORM_CLAIM in allowed_intents
        assert InvestigationIntent.STOP_INVESTIGATION in allowed_intents
        assert allowed_evidence_refs
        assert allowed_mechanism_refs
        self.call_count += 1
        return ManagerProposal(
            proposal_id=f"discovery-stop-{self.call_count}",
            source_revision=snapshot.source_revision,
            target_parent_obligation=target_parent_obligation,
            action=ManagerAction.STOP,
            intent=InvestigationIntent.STOP_INVESTIGATION,
            parent_step_id=None,
            target_kind=InvestigationTargetKind.EXPLANATION,
            target_ref=None,
            objective_key=f"discover.stop.{self.call_count}",
            rationale="No additional governed candidate can be justified.",
            inspected_evidence_refs=(allowed_evidence_refs[0],),
            inspected_claim_refs=(),
            inspected_material_refs=(),
            stop_reason=ManagerStopReason.NO_MEANINGFUL_GAIN,
        )


class DeterministicNextTestManager:
    """Provider-free P17 stand-in that must design the ADAPTIVE test."""

    def __init__(self) -> None:
        self.call_count = 0
        self.calls = []

    def propose_for_obligation_with_constraints(
        self,
        snapshot,
        *,
        target_parent_obligation,
        allowed_evidence_refs,
        allowed_intents,
    ):
        assert allowed_intents == (
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
        )
        assert allowed_evidence_refs
        self.call_count += 1
        self.calls.append(
            {
                "target_parent_obligation": target_parent_obligation,
                "allowed_evidence_refs": tuple(allowed_evidence_refs),
                "allowed_intents": tuple(allowed_intents),
            }
        )
        rule = snapshot.action_profile.rule_for(
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
        )
        assert rule is not None
        parent = (
            rule.legal_parent_step_ids[-1]
            if rule.legal_parent_step_ids
            else None
        )
        assert parent is not None or rule.allow_parentless
        return ManagerProposal(
            proposal_id=f"adaptive-next-{self.call_count}",
            source_revision=snapshot.source_revision,
            target_parent_obligation=target_parent_obligation,
            action=ManagerAction.EXPLORE_NATIVE,
            intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            parent_step_id=parent,
            branch_key=None,
            target_kind=InvestigationTargetKind.EXPLANATION,
            target_ref="typed-next-test",
            objective_key=f"adaptive.discrimination.{self.call_count}",
            bounded_objective=(
                "Test the temporal ordering that can distinguish the governed "
                "competing hypotheses inside the accepted analytical scope."
            ),
            rationale="One bounded high-information discrimination step.",
            inspected_evidence_refs=tuple(allowed_evidence_refs),
            inspected_claim_refs=(),
            inspected_material_refs=(),
            expected_information_gain=(
                "Resolve one typed ambiguity with materially new Evidence."
            ),
        )


class BombP17:
    def __getattr__(self, name):
        raise AssertionError(f"ONE_PASS must not invoke P17: {name}")


def _stack(*, epistemic_manager=None, db=None):
    if db is None:
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
    p19_manager = epistemic_manager or DeterministicP19Manager()
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


def test_real_owner_one_pass_postgres_timestamp_boundary_is_timezone_safe() -> None:
    db = _postgres_engine()
    try:
        _, store, bridge, material, p19, p19_manager, activities = _stack(db=db)
        result = BrainV2Service(activities=activities).run(
            BrainGraphState(
                thread_id="real-one-pass-postgres-timezone",
                tenant_binding=f"id:{TENANT_ID}",
                principal_ref=USER_ID,
                current_user_input="Provider-free Postgres ONE_PASS RCA.",
            )
        )

        assert result.workflow_status == BrainWorkflowStatus.COMPLETE
        assert bridge.metabot_posts == 1
        assert material.calls == 1
        assert p19_manager.call_count == 1
        assert result.latest_p19_assessment_ref is not None
        assert result.report_ref is not None

        session = store.load(
            result.research_session_id,
            tenant=f"id:{TENANT_ID}",
            principal=USER_ID,
        )
        assert session.updated_at.tzinfo is not None
        assessment = p19.load_assessment(
            assessment_id=result.latest_p19_assessment_ref,
            principal=_principal(),
        )
        assert assessment.created_at.tzinfo is not None
        report = ReportDocumentStore(
            research_store=store,
            db_engine=db,
        ).load(
            report_id=result.report_ref,
            principal=_principal(),
        )
        assert report.created_at.tzinfo is not None
    finally:
        db.dispose()


def test_real_owner_one_pass_uses_one_native_and_zero_p17() -> None:
    db, store, bridge, material, p19, p19_manager, activities = _stack()
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
    report = ReportDocumentStore(
        research_store=store,
        db_engine=db,
    ).load(
        report_id=result.report_ref,
        principal=_principal(),
    )
    contribution = tuple(
        item
        for item in report.statements
        if item.statement_kind == ReportStatementKind.CONTRIBUTION
    )
    assert len(contribution) == 1
    assert tuple(
        ref.source_kind for ref in contribution[0].source_refs
    ) == (ReportSourceKind.P19_ASSESSMENT,)

    # Exact current-session material is safely reusable without another native call.
    before = bridge.metabot_posts
    replay = activities.acquire_material(result)
    assert replay.produced_evidence_ids == result.evidence_ids
    assert bridge.metabot_posts == before

    # Exact same epistemic input reuses the durable P19 assessment rather than
    # paying for cognition again.
    before_p19 = p19_manager.call_count
    replayed_assessment = activities.assess_p19(result)
    assert replayed_assessment.assessment_ref == result.latest_p19_assessment_ref
    assert p19_manager.call_count == before_p19





def test_real_owner_report_preserves_p19_uncertainty_and_limitations() -> None:
    manager = UncertainP19Manager()
    db, store, _, _, _, _, activities = _stack(epistemic_manager=manager)
    result = BrainV2Service(activities=activities).run(
        BrainGraphState(
            thread_id="real-one-pass-uncertain",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Provider-free uncertain ONE_PASS RCA.",
        )
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert result.report_ref is not None
    report = ReportDocumentStore(
        research_store=store,
        db_engine=db,
    ).load(
        report_id=result.report_ref,
        principal=_principal(),
    )

    uncertainty = tuple(
        item
        for item in report.statements
        if item.statement_kind == ReportStatementKind.UNCERTAINTY
    )
    limitations = tuple(
        item
        for item in report.statements
        if item.statement_kind == ReportStatementKind.LIMITATION
    )
    assert len(uncertainty) == 1
    assert uncertainty[0].text.startswith(
        "No defensible root cause established. Retained candidates: "
    )
    assert "epistemic=ASSOCIATION" in uncertainty[0].text
    assert "evidence=WEAK" in uncertainty[0].text
    assert tuple(
        ref.source_kind for ref in uncertainty[0].source_refs
    ) == (ReportSourceKind.P19_ASSESSMENT,)
    assert len(limitations) == 2
    assert {
        item.detail for item in report.limitations
    } == {
        "Observed material is associative only.",
        "Temporal order and confounding remain unresolved.",
    }


def test_p19_followup_context_uses_resolved_scope_not_stale_goal_text() -> None:
    manager = ScopeAwareP19Manager()
    _, store, _, _, _, _, activities = _stack(epistemic_manager=manager)
    service = BrainV2Service(activities=activities)

    first = service.run(
        BrainGraphState(
            thread_id="p19-current-scope-authority",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Initial governed RCA across the accepted broad scope.",
        )
    )
    second = service.continue_turn(
        thread_id="p19-current-scope-authority",
        tenant_binding=f"id:{TENANT_ID}",
        principal_ref=USER_ID,
        user_input="Boyahane ile sınırla.",
    )

    assert first.scope_version_id == "scope_v1"
    assert second.scope_version_id == "scope_v2"
    assert len(manager.context_calls) == 2

    current = manager.context_calls[-1]
    assert current["objective"] is None
    scope = current["scope_authority"]
    assert scope["scope_version_id"] == "scope_v2"
    assert scope["scope_fingerprint"]
    assert scope["entity_filters"] == [
        {
            "candidate_id": "entity.department.paint",
            "dimension_name": "Department",
            "value": "Boyahane",
        }
    ]
    assert scope["periods"] == []
    assert "all" not in json.dumps(scope).lower()

    second_session = store.load(
        second.research_session_id,
        tenant=f"id:{TENANT_ID}",
        principal=USER_ID,
    )
    # The historical/broad goal prose may remain immutable for provenance, but
    # it must not be the current P19 scope authority.
    assert second_session.accepted_brief.questions[0].source_text.startswith(
        "Duruş artışını"
    )


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
    # Canonical analytical truth stays in the accepted brief, while the native
    # business-question surface reflects only the CURRENT follow-up turn. A
    # follow-up delta must not send stale broad natural language beside a
    # narrowed authoritative material contract.
    assert first_session.obligations[0].objective == (
        "Duruş artışını bakım gecikmesi mi yedek parça gecikmesi mi "
        "daha iyi açıklıyor?"
    )
    assert second_session.obligations[0].objective == "Boyahane ile sınırla."
    followup_message = bridge.metabot_requests[1]["message"]
    assert "[USER OBLIGATION]\nBoyahane ile sınırla.\n" in followup_message
    assert (
        "[USER OBLIGATION]\nDuruş artışını bakım gecikmesi mi "
        "yedek parça gecikmesi mi daha iyi açıklıyor?\n"
        not in followup_message
    )
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



def _adaptive_stack(
    *,
    discovery: bool = False,
    p19_manager_override=None,
    discovery_manager_override=None,
    repeat_followup_result: bool = False,
):
    db = _engine()
    store = ResearchSessionStore(db)
    bridge = BridgeFactory()
    material = DurableMaterialExecutor(
        store,
        repeat_followup_result=repeat_followup_result,
    )
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
        p19_manager_override
        if p19_manager_override is not None
        else (
            DeterministicP19Manager()
            if discovery
            else AdaptiveP19Manager()
        )
    )
    discovery_manager = (
        discovery_manager_override
        if discovery_manager_override is not None
        else (
            DeterministicDiscoveryManager()
            if discovery
            else DeterministicNextTestManager()
        )
    )
    activities = DimaBrainV2Activities(
        principal=principal,
        catalog=_catalog(),
        intake=(DiscoveryIntake() if discovery else AdaptiveIntake()),
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
        next_test_manager,
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
    assert len(bridge.metabot_requests) == 2
    first_state = bridge.metabot_requests[0]["state"]
    second_state = bridge.metabot_requests[1]["state"]
    first_history = bridge.metabot_requests[0]["history"]
    second_history = bridge.metabot_requests[1]["history"]
    assert first_state == {}
    assert first_history is None
    assert second_state != {}
    assert second_history == [
        {
            "role": "user",
            "content": bridge.metabot_requests[0]["message"],
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "pf-tool-1",
                    "name": "construct_notebook_query",
                    "arguments": "{}",
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "pf-tool-1",
            "content": json.dumps(
                {
                    "query-id": (
                        f"native-{result.research_session_id}-1"
                    )
                },
                separators=(",", ":"),
            ),
        },
    ]
    assert set(second_state.get("queries") or ()) == {
        f"native-{result.research_session_id}-1"
    }
    assert p19_manager.call_count == 2
    assert next_test_manager.call_count == 1
    assert next_test_manager.calls[0]["allowed_intents"] == (
        InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
    )
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
    assert next_test_steps[0].bounded_objective == (
        "Test the temporal ordering that can distinguish the governed "
        "competing hypotheses inside the accepted analytical scope."
    )
    assert len(snapshot.evidence_results) == 2
    assert (
        snapshot.evidence_results[0].result_hash
        != snapshot.evidence_results[1].result_hash
    )
    initial_scope = bridge.metabot_requests[0]["context"]["dima_analytical_scope"]
    followup_scope = bridge.metabot_requests[1]["context"]["dima_analytical_scope"]
    assert "dimension.event_date" not in initial_scope["dimension_refs"]
    assert set(followup_scope["dimension_refs"]) == (
        set(initial_scope["dimension_refs"]) | {"dimension.event_date"}
    )
    assert followup_scope["grain_constraints"] == followup_scope["dimension_refs"]
    followup_message = bridge.metabot_requests[1]["message"]
    assert followup_message.startswith("[DIMA ACCEPTED ANALYTICAL CONTRACT]\n")
    assert "dimensions:" in followup_message
    assert "\n- dimension.event_date\n" in followup_message
    assert "grain_constraints:" in followup_message
    assert "[USER OBLIGATION]" in followup_message
    assert next_test_steps[0].bounded_objective in followup_message
    assert "[MATERIAL TURN BOUNDARY]" in followup_message
    assert (
        "- produce exactly one executable native analytical query satisfying that contract"
        in followup_message
    )
    assert len(p19_manager.context_calls) == 2
    assert p19_manager.context_calls[0][
        "discriminating_test_available"
    ] is True
    assert p19_manager.context_calls[0][
        "deterministic_feedback_code"
    ] == "P19_DISCRIMINATING_TEST_AVAILABLE"
    assert p19_manager.context_calls[0]["objective"] is None
    assert p19_manager.context_calls[0]["scope_authority"]["scope_version_id"] == "scope_v1"
    assert p19_manager.context_calls[0]["scope_authority"]["scope_fingerprint"]
    assert p19_manager.context_calls[1][
        "discriminating_test_available"
    ] is False
    assert p19_manager.context_calls[1][
        "deterministic_feedback_code"
    ] == "P19_NO_CALLABLE_DISCRIMINATING_TEST"




def test_adaptive_same_result_hash_never_becomes_fake_information_gain() -> None:
    (
        _,
        _,
        bridge,
        material,
        investigation,
        _,
        p19_manager,
        next_test_manager,
        activities,
    ) = _adaptive_stack(repeat_followup_result=True)
    service = BrainV2Service(activities=activities)

    with pytest.raises(BrainV2OwnerError) as exc:
        service.run(
            BrainGraphState(
                thread_id="adaptive-no-gain",
                tenant_binding=f"id:{TENANT_ID}",
                principal_ref=USER_ID,
                current_user_input="Provider-free ADAPTIVE RCA.",
            )
        )

    assert exc.value.code == "BRAIN_V2_NEXT_TEST_NO_INFORMATION_GAIN"
    assert bridge.metabot_posts == 2
    assert material.calls == 2
    assert p19_manager.call_count == 1
    assert next_test_manager.call_count == 1

def test_discovery_honest_stop_is_governed_terminal_not_intent_mismatch() -> None:
    stop_manager = DeterministicDiscoveryStopManager()
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
    ) = _adaptive_stack(
        discovery=True,
        discovery_manager_override=stop_manager,
    )
    service = BrainV2Service(activities=activities)

    result = service.run(
        BrainGraphState(
            thread_id="real-discovery-honest-stop",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Provider-free discovery with no justified candidate.",
        )
    )

    assert result.workflow_status == BrainWorkflowStatus.INCONCLUSIVE
    assert result.last_completed_node == "HONEST_STOP"
    assert result.hypothesis_ids == ()
    assert result.discovery_required is False
    assert result.discovery_turns == 1
    assert discovery_manager.call_count == 1
    assert bridge.metabot_posts == 1
    assert material.calls == 1
    assert p19_manager.call_count == 0
    assert investigation.snapshot(
        session_id=result.research_session_id,
        principal=_principal(),
    ).terminal_stop_reason == ManagerStopReason.NO_MEANINGFUL_GAIN
    assert p19.snapshot(
        research_session_id=result.research_session_id,
        obligation_id="g_root",
        principal=_principal(),
    ).hypotheses == ()



def test_discovery_candidate_vocabulary_consumes_durable_candidate_identity() -> None:
    manager = GreedyFirstDiscoveryManager()
    (
        _,
        _,
        bridge,
        material,
        investigation,
        p19,
        p19_manager,
        _,
        activities,
    ) = _adaptive_stack(
        discovery=True,
        discovery_manager_override=manager,
    )
    service = BrainV2Service(activities=activities)

    result = service.run(
        BrainGraphState(
            thread_id="real-discovery-consumes-candidate",
            tenant_binding=f"id:{TENANT_ID}",
            principal_ref=USER_ID,
            current_user_input="Provider-free governed discovery.",
        )
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert manager.call_count == 2
    assert len(manager.allowed_history) == 2
    first, second = manager.allowed_history
    assert len(first) >= 2
    assert first[0] not in second
    assert set(second).issubset(set(first))
    assert len(result.hypothesis_ids) == 2
    assert bridge.metabot_posts == 1
    assert material.calls == 1
    assert p19_manager.call_count == 1

    snapshot = investigation.snapshot(
        session_id=result.research_session_id,
        principal=_principal(),
    )
    mechanism_refs = []
    for claim in snapshot.claims:
        semantics = decode_root_cause_candidate_semantics(
            claim.proposition or {}
        )
        assert semantics is not None
        mechanism_refs.append(semantics.mechanism_ref)
    assert len(mechanism_refs) == 2
    assert len(set(mechanism_refs)) == 2

    epistemic = p19.snapshot(
        research_session_id=result.research_session_id,
        obligation_id="g_root",
        principal=_principal(),
    )
    assert len(epistemic.hypotheses) == 2


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
