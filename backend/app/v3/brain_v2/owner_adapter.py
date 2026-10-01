"""Canonical Dima owner adapter for Brain V2 Phase 1.

This module contains orchestration glue only. It does not replace or duplicate
ResearchBrief/ScopeVersion, Evidence, P17 claims, P19 epistemics, or P20 reports.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    ContributionClass,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
    HypothesisRootCauseStore,
)
from app.v3.hypothesis_root_cause_v1 import (
    NextTestRequest,
    discriminating_test_capacity_available,
    discriminating_test_is_callable,
    next_test_request,
)
from app.v3.product.contracts import ProductInvestigationRequirementKind
from app.v3.report_document import (
    ReportDocumentStore,
    ReportDraft,
    ReportLimitation,
    ReportSourceKind,
    ReportStatement,
    ReportStatementKind,
    SourceReference,
    stable_limitation_id,
    stable_statement_id,
)
from app.v3.research_contracts import (
    ResearchGoalKind,
    ResearchQuestion,
    SemanticTargetKind,
)
from app.v3.research_intake import (
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
    ResearchIntakeTerminal,
)
from app.v3.research_analytical_scope import analytical_scope_contract
from app.v3.research_manager import (
    ClaimSemanticContract,
    InvestigationIntent,
    InvestigationTargetKind,
    ManagerAction,
    ManagerProposal,
    ResearchInvestigationManager,
)
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.root_cause_candidate_contract import (
    decode_root_cause_candidate_semantics,
)
from control_plane.authorize import Principal

from .discovery_candidate_design import (
    project_candidate_set,
    remaining_discovery_mechanism_refs,
)
from .activities import (
    BrainActivities,
    CandidateProjectionActivityResult,
    CanonicalizeActivityResult,
    EvidenceActivityResult,
    IntakeActivityResult,
    MaterialActivityResult,
    P17ActivityResult,
    P19ActivityResult,
    ReportActivityResult,
)
from .keys import CognitionPurpose, CognitionRequestKey, NativeMaterialRequestKey
from .p19_context import project_p19_scope_authority
from .state import BrainGraphState, BrainP19Route
from .telemetry import BoundaryName, OpenTelemetryBridge


class BrainV2OwnerError(RuntimeError):
    def __init__(
        self,
        code: str,
        detail: str,
        *,
        last_valid_boundary: str | None = None,
        first_invalid_boundary: str | None = None,
        expected_fingerprint: str | None = None,
        observed_fingerprint: str | None = None,
        scope_fingerprint: str | None = None,
        material_fingerprint: str | None = None,
        expected_semantic_shape: dict[str, Any] | None = None,
        observed_semantic_shape: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.last_valid_boundary = last_valid_boundary
        self.first_invalid_boundary = first_invalid_boundary
        self.expected_fingerprint = expected_fingerprint
        self.observed_fingerprint = observed_fingerprint
        self.scope_fingerprint = scope_fingerprint
        self.material_fingerprint = material_fingerprint
        self.expected_semantic_shape = expected_semantic_shape
        self.observed_semantic_shape = observed_semantic_shape


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class _DiscoveryProposalManager:
    """Narrow P17 provider cognition to governed candidate discovery only."""

    def __init__(
        self,
        *,
        inner,
        obligation_id: str,
        evidence_refs: tuple[str, ...],
        mechanism_refs: tuple[str, ...],
    ) -> None:
        self._inner = inner
        self._obligation_id = obligation_id
        self._evidence_refs = evidence_refs
        self._mechanism_refs = mechanism_refs

    def propose(self, snapshot):
        proposal = self._inner.propose_root_candidate_for_obligation_with_constraints(
            snapshot,
            target_parent_obligation=self._obligation_id,
            allowed_evidence_refs=self._evidence_refs,
            allowed_mechanism_refs=self._mechanism_refs,
            allowed_intents=(
                InvestigationIntent.FORM_CLAIM,
                InvestigationIntent.STOP_INVESTIGATION,
            ),
        )
        if (
            proposal.target_parent_obligation is not None
            and proposal.target_parent_obligation != self._obligation_id
        ):
            raise BrainV2OwnerError(
                "BRAIN_V2_P17_DISCOVERY_SCOPE_ESCAPE",
                proposal.target_parent_obligation,
            )
        if proposal.action == ManagerAction.FORM_CLAIM:
            if proposal.mechanism_semantic_ref not in set(self._mechanism_refs):
                raise BrainV2OwnerError(
                    "BRAIN_V2_P17_DISCOVERY_CANDIDATE_ESCAPE",
                    str(proposal.mechanism_semantic_ref),
                )
            proposal = proposal.model_copy(
                update={
                    "claim_semantic_contract": (
                        ClaimSemanticContract.ROOT_CAUSE_CANDIDATE
                    )
                }
            )
        return proposal


class _NextTestProposalManager:
    """Typed P19 NextTestRequest -> one legal P17 analytical transition."""

    def __init__(self, *, request: NextTestRequest, obligation_id: str) -> None:
        self._request = request
        self._obligation_id = obligation_id

    def propose(self, snapshot):
        rule = snapshot.action_profile.rule_for(
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
        )
        if rule is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_NEXT_TEST_NOT_STATE_LEGAL",
                self._request.request_id,
            )
        node_by_id = {
            node.step_id: node
            for node in snapshot.investigation.nodes
        }
        ordered = {
            node.step_id: index
            for index, node in enumerate(snapshot.investigation.nodes)
        }
        legal = tuple(
            step_id
            for step_id in rule.legal_parent_step_ids
            if (
                step_id in node_by_id
                and node_by_id[step_id].root_obligation_id == self._obligation_id
            )
        )
        if legal:
            parent = max(legal, key=lambda value: ordered[value])
        elif rule.allow_parentless:
            parent = None
        else:
            raise BrainV2OwnerError(
                "BRAIN_V2_NEXT_TEST_PARENT_MISSING",
                self._request.request_id,
            )
        return ManagerProposal(
            proposal_id="p17-next-" + self._request.request_id[4:],
            source_revision=snapshot.source_revision,
            target_parent_obligation=self._obligation_id,
            action=ManagerAction.EXPLORE_NATIVE,
            intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            parent_step_id=parent,
            branch_key=None,
            target_kind=InvestigationTargetKind.EXPLANATION,
            target_ref=self._request.request_id,
            objective_key="next_test." + self._request.request_id[4:],
            bounded_objective=self._request.bounded_objective(),
            rationale=(
                "P19 exposed one typed unresolved discrimination; execute only "
                "the governed high-information follow-up."
            ),
            inspected_evidence_refs=(),
            inspected_claim_refs=(),
            inspected_material_refs=(),
            expected_information_gain=(
                self._request.expected_discriminatory_value.value
            ),
        )


class DimaBrainV2Activities(BrainActivities):
    """Wrap the current Dima domain owners behind the Brain V2 graph."""

    def __init__(
        self,
        *,
        principal: Principal,
        catalog: ResearchIntakeCatalog,
        intake: ResearchIntakeCompiler,
        research: ResearchAskOrchestrator,
        investigation: ResearchInvestigationManager,
        investigation_manager,
        epistemics: HypothesisRootCauseStore,
        epistemic_manager,
        reports: ReportDocumentStore,
        native_session_token: str | None,
        engine_identity: str,
        model_profile: str = "openai/gpt-5.6-luna",
        request_ref_prefix: str = "brain-v2",
        otel_bridge: OpenTelemetryBridge | None = None,
    ) -> None:
        self._principal = principal
        self._catalog = catalog
        self._intake = intake
        self._research = research
        self._investigation = investigation
        self._investigation_manager = investigation_manager
        self._epistemics = epistemics
        self._epistemic_manager = epistemic_manager
        self._reports = reports
        self._native_session_token = native_session_token
        self._engine_identity = str(engine_identity or "").strip()
        self._model_profile = str(model_profile or "").strip()
        self._request_ref_prefix = str(request_ref_prefix or "").strip()
        self._otel_bridge = otel_bridge or OpenTelemetryBridge()
        if not self._engine_identity:
            raise ValueError("Brain V2 engine identity is required")
        if not self._model_profile:
            raise ValueError("Brain V2 model profile is required")

    @property
    def otel_bridge(self) -> OpenTelemetryBridge:
        return self._otel_bridge
        if not self._request_ref_prefix:
            raise ValueError("Brain V2 request-ref prefix is required")

    def _tenant(self) -> str:
        return ResearchAskOrchestrator.tenant_binding_for(self._principal)

    def _subject(self) -> str:
        value = str(self._principal.user_id).strip()
        if not value:
            raise BrainV2OwnerError(
                "BRAIN_V2_PRINCIPAL_REQUIRED",
                "current principal has no stable subject",
            )
        return value

    def _assert_graph_identity(self, state: BrainGraphState) -> None:
        if (
            state.tenant_binding != self._tenant()
            or state.principal_ref != self._subject()
        ):
            raise BrainV2OwnerError(
                "BRAIN_V2_GRAPH_IDENTITY_MISMATCH",
                "graph state is outside the bound tenant/principal",
            )

    def _session(self, state: BrainGraphState):
        self._assert_graph_identity(state)
        if state.research_session_id is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_RESEARCH_SESSION_REQUIRED",
                "current graph state has no Research session ref",
            )
        session = self._research.resume_state(
            session_id=state.research_session_id,
            principal=self._principal,
        )
        if session.accepted_brief is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_ACCEPTED_BRIEF_REQUIRED",
                state.research_session_id,
            )
        if (
            state.scope_version_id is not None
            and session.accepted_brief.scope.scope_version.version_id
            != state.scope_version_id
        ):
            raise BrainV2OwnerError(
                "BRAIN_V2_SCOPE_REF_MISMATCH",
                state.scope_version_id,
            )
        return session

    @staticmethod
    def _root_goal(session) -> ResearchQuestion:
        brief = session.accepted_brief
        assert brief is not None
        roots = tuple(
            item
            for item in brief.questions
            if item.kind == ResearchGoalKind.ROOT_CAUSE
        )
        if len(roots) != 1:
            raise BrainV2OwnerError(
                "BRAIN_V2_PHASE1_ROOT_SCOPE_INVALID",
                "Phase-1 graph requires exactly one ROOT_CAUSE analytical goal",
            )
        if len(brief.questions) != 1:
            raise BrainV2OwnerError(
                "BRAIN_V2_PHASE1_MULTI_ANALYTICAL_DEFERRED",
                "Phase-1 root certification does not compose multiple analytical goals",
            )
        return roots[0]

    @staticmethod
    def _mechanism_refs(
        *,
        goal: ResearchQuestion,
        session,
    ) -> tuple[tuple[str, ...], bool]:
        surface = goal.causal_competition
        refs = tuple((*goal.subject_refs, *goal.related_refs))
        if surface is not None:
            if surface.candidate_mechanism_semantic_ids:
                return surface.candidate_mechanism_semantic_ids, True
            return (
                tuple(
                    dict.fromkeys(
                        item.candidate_id
                        for item in refs
                        if (
                            item.target_kind
                            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                            and item.candidate_id != surface.effect_semantic_id
                        )
                    )
                ),
                False,
            )
        brief = session.accepted_brief
        subject_ids = {item.candidate_id for item in goal.subject_refs}
        return (
            tuple(
                sorted(
                    item.candidate_id
                    for item in brief.scope.semantic_refs
                    if (
                        item.target_kind
                        in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                        and item.candidate_id not in subject_ids
                    )
                )
            ),
            False,
        )

    @staticmethod
    def _evidence_pairs(session, obligation_id: str) -> tuple[tuple[str, str], ...]:
        """Canonical P14 Evidence refs already admitted to the Research session."""
        return tuple(
            (item.evidence_id, item.receipt_id)
            for item in session.evidence_refs
            if item.obligation_id == obligation_id
        )

    def _durable_evidence_pairs(
        self,
        *,
        session,
        obligation_id: str,
    ) -> tuple[tuple[str, str], ...]:
        """Project all VERIFIED canonical Evidence occurrences for one obligation.

        P17 follow-up Evidence is durably owned by the sealed ResearchExecutionLink
        path and intentionally does not mutate the already-VERIFIED parent P14
        session record. ResearchInvestigationManager.snapshot exposes that exact
        receipt/Evidence lineage without creating a second truth family.
        """
        base = self._evidence_pairs(session, obligation_id)
        snapshot = self._investigation.snapshot(
            session_id=session.session_id,
            principal=self._principal,
        )
        followups = tuple(
            (item.evidence_id, item.receipt_id)
            for item in snapshot.evidence_results
            if item.obligation_id == obligation_id
        )
        return tuple(dict.fromkeys((*base, *followups)))

    @staticmethod
    def _question_fingerprint(session, goal: ResearchQuestion) -> str:
        brief = session.accepted_brief
        assert brief is not None
        return _fingerprint(
            {
                "goal": goal.model_dump(mode="json"),
                "scope": brief.scope.model_dump(mode="json"),
            }
        )

    def _cognition_key(
        self,
        *,
        state: BrainGraphState,
        owner: str,
        purpose: CognitionPurpose,
        objective_id: str,
        legal_profile_hash: str,
    ) -> CognitionRequestKey:
        if state.scope_version_id is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_SCOPE_REQUIRED",
                owner,
            )
        return CognitionRequestKey(
            owner=owner,
            purpose=purpose,
            objective_id=objective_id,
            scope_version_id=state.scope_version_id,
            evidence_revision=state.evidence_revision,
            hypothesis_revision=state.hypothesis_revision,
            legal_action_profile_hash=legal_profile_hash,
            model_profile=self._model_profile,
        )

    def intake(self, state: BrainGraphState) -> IntakeActivityResult:
        self._assert_graph_identity(state)
        if not state.current_user_input:
            raise BrainV2OwnerError(
                "BRAIN_V2_CURRENT_INPUT_REQUIRED",
                state.thread_id,
            )

        prior_session = None
        prior_brief = None
        if state.research_session_id is not None:
            prior_session = self._research.current_scope_state(
                session_id=state.research_session_id,
                principal=self._principal,
            )
            prior_brief = prior_session.accepted_brief

        result = self._intake.compile(
            question=state.current_user_input,
            catalog=self._catalog,
            prior_brief=prior_brief,
        )
        if result.terminal != ResearchIntakeTerminal.READY or result.brief is None:
            detail = (
                result.clarification_question
                or result.unsupported_reason
                or result.terminal.value
            )
            raise BrainV2OwnerError(
                "BRAIN_V2_INTAKE_" + result.terminal.value,
                detail,
            )

        brief = result.brief
        source_hash = hashlib.sha256(
            state.current_user_input.encode("utf-8")
        ).hexdigest()
        session = self._research.start_from_brief(
            brief=brief,
            request_ref=(
                f"{self._request_ref_prefix}:{state.thread_id}:{brief.brief_id}"
            ),
            source_message_hash=source_hash,
            principal=self._principal,
            prior_session_id=(
                prior_session.session_id if prior_session is not None else None
            ),
            business_question=(
                state.current_user_input
                if prior_session is not None
                else None
            ),
        )
        goal = self._root_goal(session)
        _, user_seeded = self._mechanism_refs(goal=goal, session=session)
        fp = self._cognition_key(
            state=BrainGraphState.model_validate(
                state.model_copy(
                    update={
                        "scope_version_id": (
                            brief.scope.scope_version.version_id
                        )
                    }
                )
            ),
            owner="ResearchIntake",
            purpose=(
                CognitionPurpose.REPAIR_SCOPE
                if prior_brief is not None
                else CognitionPurpose.INTERPRET_NEW_INTENT
            ),
            objective_id=goal.goal_id,
            legal_profile_hash=self._catalog.fingerprint,
        ).fingerprint
        adaptive_requirements = tuple(
            item
            for item in result.investigation_requirements
            if item.kind
            == ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL
        )
        return IntakeActivityResult(
            research_session_id=session.session_id,
            accepted_brief_ref=brief.brief_id,
            scope_version_id=brief.scope.scope_version.version_id,
            open_requirement_ids=tuple(
                item.obligation_id for item in session.obligations
            ),
            material_requirement_ids=(goal.goal_id,),
            investigation_requirement_ids=tuple(
                item.requirement_id for item in result.investigation_requirements
            ),
            follow_verified_material_goal_ids=tuple(
                dict.fromkeys(
                    item.source_goal_id for item in adaptive_requirements
                )
            ),
            discovery_required=not user_seeded,
            activity_fingerprint=fp,
        )

    def canonicalize(self, state: BrainGraphState) -> CanonicalizeActivityResult:
        session = self._session(state)
        goal = self._root_goal(session)
        mechanism_refs, user_seeded = self._mechanism_refs(
            goal=goal,
            session=session,
        )
        hypothesis_ids: list[str] = []

        if user_seeded:
            brief = session.accepted_brief
            assert brief is not None
            semantic_by_id = {
                item.candidate_id: item for item in brief.scope.semantic_refs
            }
            surface = goal.causal_competition
            effect = (
                semantic_by_id.get(surface.effect_semantic_id)
                if surface is not None
                else None
            )
            effect_name = (
                effect.canonical_name if effect is not None else goal.source_text
            )
            for mechanism_ref in tuple(dict.fromkeys(mechanism_refs)):
                semantic = semantic_by_id.get(mechanism_ref)
                if semantic is None:
                    raise BrainV2OwnerError(
                        "BRAIN_V2_USER_CANDIDATE_OUTSIDE_SCOPE",
                        mechanism_ref,
                    )
                hypothesis = self._epistemics.create_hypothesis(
                    research_session_id=session.session_id,
                    obligation_id=goal.goal_id,
                    statement=(
                        f"{semantic.canonical_name} as a user-seeded explanatory "
                        f"candidate for {effect_name}"
                    ),
                    principal=self._principal,
                    candidate_identity_ref=mechanism_ref,
                )
                hypothesis_ids.append(hypothesis.hypothesis_id)

        fp = _fingerprint(
            {
                "activity": "CANONICALIZE",
                "session": session.session_id,
                "scope": state.scope_version_id,
                "mechanisms": list(mechanism_refs if user_seeded else ()),
            }
        )
        return CanonicalizeActivityResult(
            research_session_id=session.session_id,
            scope_version_id=state.scope_version_id or "scope_v1",
            open_requirement_ids=tuple(
                item.obligation_id
                for item in session.obligations
                if item.state.value not in {"VERIFIED", "LIMITED"}
            ),
            material_requirement_ids=(goal.goal_id,),
            hypothesis_ids=tuple(dict.fromkeys(hypothesis_ids)),
            discovery_required=not user_seeded,
            activity_fingerprint=fp,
        )

    def acquire_material(self, state: BrainGraphState) -> MaterialActivityResult:
        session = self._session(state)
        goal = self._root_goal(session)
        brief = session.accepted_brief
        if brief is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_ACCEPTED_BRIEF_REQUIRED",
                session.session_id,
            )
        state_scope_version = state.scope_version_id or "scope_v1"
        if state_scope_version != brief.scope.scope_version.version_id:
            raise BrainV2OwnerError(
                "BRAIN_V2_SCOPE_VERSION_MISMATCH",
                (
                    f"state={state_scope_version} "
                    f"brief={brief.scope.scope_version.version_id}"
                ),
            )
        material_contract = analytical_scope_contract(
            session=session,
            obligation_id=goal.goal_id,
        )
        if material_contract.scope_fingerprint != brief.scope_fingerprint:
            raise BrainV2OwnerError(
                "BRAIN_V2_MATERIAL_SCOPE_FINGERPRINT_MISMATCH",
                (
                    f"expected={brief.scope_fingerprint} "
                    f"observed={material_contract.scope_fingerprint}"
                ),
                last_valid_boundary="dima.scope.resolve",
                first_invalid_boundary="dima.material.compile",
                expected_fingerprint=brief.scope_fingerprint,
                observed_fingerprint=material_contract.scope_fingerprint,
            )
        existing = self._evidence_pairs(session, goal.goal_id)
        request_key = NativeMaterialRequestKey(
            tenant=self._tenant(),
            principal=self._subject(),
            scope_version_id=state_scope_version,
            scope_fingerprint=brief.scope_fingerprint,
            material_requirement_fingerprint=material_contract.fingerprint,
            engine_identity=self._engine_identity,
        )
        if existing:
            return MaterialActivityResult(
                material_requirement_ids=(goal.goal_id,),
                produced_evidence_ids=tuple(item[0] for item in existing),
                produced_receipt_refs=tuple(item[1] for item in existing),
                activity_fingerprint=request_key.fingerprint,
            )

        with self._otel_bridge.operation(
            BoundaryName.NATIVE_EXECUTE,
            state=state,
            scope_fingerprint=brief.scope_fingerprint,
            material_fingerprint=material_contract.fingerprint,
            native_acquisition_count=1,
            dedup_hit=False,
        ):
            response = self._research.run_next(
                session_id=session.session_id,
                principal=self._principal,
                obligation_id=goal.goal_id,
                native_session_token=self._native_session_token,
            )
        if not response.evidence_id or not response.receipt_id:
            raise BrainV2OwnerError(
                response.limitation_code or "BRAIN_V2_NATIVE_EVIDENCE_REQUIRED",
                response.limitation_detail or goal.goal_id,
                last_valid_boundary=response.last_valid_boundary,
                first_invalid_boundary=response.first_invalid_boundary,
                expected_fingerprint=response.expected_fingerprint,
                observed_fingerprint=response.observed_fingerprint,
                scope_fingerprint=response.scope_fingerprint,
                material_fingerprint=response.material_fingerprint,
                expected_semantic_shape=response.expected_semantic_shape,
                observed_semantic_shape=response.observed_semantic_shape,
            )
        return MaterialActivityResult(
            material_requirement_ids=(goal.goal_id,),
            produced_evidence_ids=(response.evidence_id,),
            produced_receipt_refs=(response.receipt_id,),
            activity_fingerprint=request_key.fingerprint,
        )

    def _ground_evidence(
        self,
        *,
        state: BrainGraphState,
        evidence_pairs: tuple[tuple[str, str], ...],
    ) -> tuple[str, ...]:
        session = self._session(state)
        goal = self._root_goal(session)
        snapshot = self._epistemics.snapshot(
            research_session_id=session.session_id,
            obligation_id=goal.goal_id,
            principal=self._principal,
        )
        ids: list[str] = []
        for item in snapshot.hypotheses:
            ids.append(item.hypothesis.hypothesis_id)
            for evidence_id, receipt_id in evidence_pairs:
                self._epistemics.create_grounding(
                    hypothesis_id=item.hypothesis.hypothesis_id,
                    source_kind=GroundingSourceKind.P14_EVIDENCE,
                    source_ref=evidence_id,
                    source_receipt_id=receipt_id,
                    relation=GroundingRelation.CONTEXT,
                    principal=self._principal,
                )
        return tuple(dict.fromkeys(ids))

    def admit_evidence(self, state: BrainGraphState) -> EvidenceActivityResult:
        session = self._session(state)
        goal = self._root_goal(session)
        pending = tuple(
            zip(
                state.pending_evidence_ids,
                state.pending_receipt_refs,
                strict=True,
            )
        )
        if not pending:
            raise BrainV2OwnerError(
                "BRAIN_V2_PENDING_EVIDENCE_REQUIRED",
                goal.goal_id,
            )

        # ONE_PASS initial material is already present in canonical P14 session
        # refs; do not touch P17 merely to rediscover that fact. Only consult
        # the P17 durable execution projection when pending refs are not in the
        # base P14 set (the ADAPTIVE follow-up case).
        base_pairs = self._evidence_pairs(session, goal.goal_id)
        if set(pending).issubset(set(base_pairs)):
            persisted_pairs = base_pairs
        else:
            persisted_pairs = self._durable_evidence_pairs(
                session=session,
                obligation_id=goal.goal_id,
            )
        if not set(pending).issubset(set(persisted_pairs)):
            raise BrainV2OwnerError(
                "BRAIN_V2_EVIDENCE_PROVENANCE_MISMATCH",
                goal.goal_id,
            )

        hypothesis_ids = self._ground_evidence(
            state=state,
            evidence_pairs=pending,
        )
        all_evidence = tuple(item[0] for item in persisted_pairs)
        discovery_required = not bool(hypothesis_ids)
        return EvidenceActivityResult(
            evidence_revision=len(tuple(dict.fromkeys(all_evidence))),
            evidence_ids=tuple(dict.fromkeys(all_evidence)),
            hypothesis_revision=state.hypothesis_revision,
            hypothesis_ids=hypothesis_ids,
            discovery_required=discovery_required,
            activity_fingerprint=_fingerprint(
                {
                    "activity": "ADMIT_EVIDENCE",
                    "session": session.session_id,
                    "scope": state.scope_version_id,
                    "pairs": list(pending),
                }
            ),
        )

    def project_candidates(
        self,
        state: BrainGraphState,
    ) -> CandidateProjectionActivityResult:
        """Project current VERIFIED analytical material into P19 candidate identity.

        This boundary is deliberately non-cognitive. P14 has already verified
        that the native occurrence satisfies the accepted analytical contract.
        We therefore intersect that verified material vocabulary with the
        accepted discovery surface/current scope and create only P19 identities
        grounded as CONTEXT. P19 remains the sole epistemic judge.
        """

        session = self._session(state)
        goal = self._root_goal(session)
        brief = session.accepted_brief
        assert brief is not None
        surface = goal.causal_competition
        if surface is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_DISCOVERY_SURFACE_REQUIRED",
                goal.goal_id,
            )

        allowed_mechanisms, user_seeded = self._mechanism_refs(
            goal=goal,
            session=session,
        )
        if user_seeded:
            raise BrainV2OwnerError(
                "BRAIN_V2_DISCOVERY_NOT_REQUIRED",
                goal.goal_id,
            )

        evidence_pairs = self._durable_evidence_pairs(
            session=session,
            obligation_id=goal.goal_id,
        )
        pair_by_evidence = dict(evidence_pairs)
        current_evidence = tuple(dict.fromkeys(state.evidence_ids))
        if not current_evidence:
            raise BrainV2OwnerError(
                "BRAIN_V2_DISCOVERY_EVIDENCE_REQUIRED",
                goal.goal_id,
            )
        if not set(current_evidence).issubset(set(pair_by_evidence)):
            raise BrainV2OwnerError(
                "BRAIN_V2_DISCOVERY_EVIDENCE_NOT_CURRENT",
                goal.goal_id,
                last_valid_boundary="dima.evidence.admit",
                first_invalid_boundary="dima.discovery.project_candidates",
            )

        material = analytical_scope_contract(
            session=session,
            obligation_id=goal.goal_id,
        )
        if material.scope_identity.version_id != brief.scope.scope_version.version_id:
            raise BrainV2OwnerError(
                "BRAIN_V2_DISCOVERY_MATERIAL_SCOPE_MISMATCH",
                goal.goal_id,
                last_valid_boundary="dima.material.compile",
                first_invalid_boundary="dima.discovery.project_candidates",
                expected_fingerprint=brief.scope_fingerprint,
                observed_fingerprint=material.scope_fingerprint,
            )

        current_scope_refs = tuple(
            item.candidate_id for item in brief.scope.semantic_refs
        )
        candidate_eligible_refs = tuple(
            item.candidate_id
            for item in brief.scope.semantic_refs
            if item.target_kind
            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
        projection = project_candidate_set(
            allowed_discovery_surface=allowed_mechanisms,
            current_scope_semantic_refs=current_scope_refs,
            # P14 VERIFIED Evidence can exist only after the native material
            # occurrence has been checked against this exact contract. These
            # metric refs are therefore governed observed-material bindings,
            # not a guess from prompt/result text.
            observed_material_semantic_refs=material.metric_refs,
            candidate_eligible_semantic_refs=candidate_eligible_refs,
            effect_semantic_id=surface.effect_semantic_id,
            scope_version_id=brief.scope.scope_version.version_id,
            evidence_refs=current_evidence,
            material_requirement_ref=goal.goal_id,
        )

        semantic_by_id = {
            item.candidate_id: item for item in brief.scope.semantic_refs
        }
        hypothesis_ids: list[str] = []
        for candidate in projection.candidates:
            semantic = semantic_by_id.get(candidate.semantic_id)
            if semantic is None:
                raise BrainV2OwnerError(
                    "BRAIN_V2_DISCOVERY_CANDIDATE_OUTSIDE_SCOPE",
                    candidate.semantic_id,
                )
            hypothesis = self._epistemics.create_hypothesis(
                research_session_id=session.session_id,
                obligation_id=goal.goal_id,
                statement=semantic.canonical_name,
                principal=self._principal,
                candidate_identity_ref=candidate.semantic_id,
            )
            for evidence_id in candidate.evidence_refs:
                receipt_id = pair_by_evidence[evidence_id]
                self._epistemics.create_grounding(
                    hypothesis_id=hypothesis.hypothesis_id,
                    source_kind=GroundingSourceKind.P14_EVIDENCE,
                    source_ref=evidence_id,
                    source_receipt_id=receipt_id,
                    relation=GroundingRelation.CONTEXT,
                    principal=self._principal,
                )
            hypothesis_ids.append(hypothesis.hypothesis_id)

        ids = tuple(dict.fromkeys(hypothesis_ids))
        key = _fingerprint(
            {
                "activity": "PROJECT_CANDIDATES",
                "session": session.session_id,
                "scope": state.scope_version_id,
                "material": material.fingerprint,
                "evidence": list(current_evidence),
                "candidate_semantic_ids": [
                    item.semantic_id for item in projection.candidates
                ],
            }
        )
        return CandidateProjectionActivityResult(
            hypothesis_revision=(
                state.hypothesis_revision + (1 if ids else 0)
            ),
            hypothesis_ids=ids,
            candidate_count=len(ids),
            activity_fingerprint=key,
        )

    def _sync_discovered_hypotheses(
        self,
        *,
        state: BrainGraphState,
        snapshot,
    ) -> tuple[str, ...]:
        session = self._session(state)
        goal = self._root_goal(session)
        brief = session.accepted_brief
        assert brief is not None
        allowed_mechanisms, _ = self._mechanism_refs(
            goal=goal,
            session=session,
        )
        allowed_set = set(allowed_mechanisms)
        semantic_by_id = {
            item.candidate_id: item for item in brief.scope.semantic_refs
        }
        relation_map = {
            "SUPPORTS": GroundingRelation.SUPPORTS,
            "CHALLENGES": GroundingRelation.CHALLENGES,
            "CONTEXTUALIZES": GroundingRelation.CONTEXT,
            "INSUFFICIENT": GroundingRelation.INSUFFICIENT,
        }
        hypothesis_ids: list[str] = []
        for claim in snapshot.claims:
            if claim.obligation_id != goal.goal_id:
                continue
            semantics = decode_root_cause_candidate_semantics(
                claim.proposition or {}
            )
            if semantics is None:
                continue
            if (
                semantics.explanatory_subject_ref != goal.goal_id
                or semantics.scope_lineage_id != session.lineage_id
                or semantics.scope_version_id
                != brief.scope.scope_version.version_id
                or semantics.mechanism_ref not in allowed_set
            ):
                continue
            if not claim.evidence_links:
                continue

            semantic = semantic_by_id.get(semantics.mechanism_ref)
            hypothesis = self._epistemics.create_hypothesis(
                research_session_id=session.session_id,
                obligation_id=goal.goal_id,
                statement=(
                    semantic.canonical_name
                    if semantic is not None
                    else semantics.mechanism_ref
                ),
                principal=self._principal,
                candidate_identity_ref=semantics.mechanism_ref,
            )
            self._epistemics.create_grounding(
                hypothesis_id=hypothesis.hypothesis_id,
                source_kind=GroundingSourceKind.P16_CLAIM,
                source_ref=claim.claim_id,
                relation=GroundingRelation.CONTEXT,
                principal=self._principal,
            )
            for link in claim.evidence_links:
                relation = relation_map.get(link.relation)
                if relation is None:
                    raise BrainV2OwnerError(
                        "BRAIN_V2_P16_RELATION_UNKNOWN",
                        link.relation,
                    )
                self._epistemics.create_grounding(
                    hypothesis_id=hypothesis.hypothesis_id,
                    source_kind=GroundingSourceKind.P14_EVIDENCE,
                    source_ref=link.evidence_id,
                    source_receipt_id=link.receipt_id,
                    relation=relation,
                    principal=self._principal,
                )
            hypothesis_ids.append(hypothesis.hypothesis_id)
        return tuple(dict.fromkeys(hypothesis_ids))

    def discover_hypotheses(self, state: BrainGraphState) -> P17ActivityResult:
        session = self._session(state)
        goal = self._root_goal(session)
        evidence_pairs = self._durable_evidence_pairs(
            session=session,
            obligation_id=goal.goal_id,
        )
        if not evidence_pairs:
            raise BrainV2OwnerError(
                "BRAIN_V2_DISCOVERY_EVIDENCE_REQUIRED",
                goal.goal_id,
            )
        mechanism_refs, user_seeded = self._mechanism_refs(
            goal=goal,
            session=session,
        )
        if user_seeded:
            raise BrainV2OwnerError(
                "BRAIN_V2_DISCOVERY_NOT_REQUIRED",
                goal.goal_id,
            )
        before = self._investigation.snapshot(
            session_id=session.session_id,
            principal=self._principal,
        )
        brief = session.accepted_brief
        assert brief is not None
        remaining_mechanism_refs = remaining_discovery_mechanism_refs(
            snapshot=before,
            obligation_id=goal.goal_id,
            scope_lineage_id=session.lineage_id,
            scope_version_id=brief.scope.scope_version.version_id,
            governed_mechanism_refs=mechanism_refs,
        )
        legal_hash = before.fingerprint
        manager = _DiscoveryProposalManager(
            inner=self._investigation_manager,
            obligation_id=goal.goal_id,
            evidence_refs=tuple(item[0] for item in evidence_pairs),
            mechanism_refs=remaining_mechanism_refs,
        )
        # Discovery prepares the verified-Evidence FORM_CLAIM re-entry
        # surface but permits either typed provider outcome: a governed claim
        # or an honest global stop. ResearchManager validates the exact set.
        self._investigation.run_one(
            session_id=session.session_id,
            principal=self._principal,
            manager=manager,
            native_session_token=self._native_session_token,
            downstream_reentry_intents=(
                InvestigationIntent.FORM_CLAIM,
                InvestigationIntent.STOP_INVESTIGATION,
            ),
            downstream_reentry_obligation_id=goal.goal_id,
        )
        after = self._investigation.snapshot(
            session_id=session.session_id,
            principal=self._principal,
        )
        hypothesis_ids = self._sync_discovered_hypotheses(
            state=state,
            snapshot=after,
        )
        complete = len(hypothesis_ids) >= 2
        terminal = (
            after.terminal_stop_reason is not None
            or after.remaining_reasoning_steps <= 0
        )
        key = self._cognition_key(
            state=state,
            owner="P17",
            purpose=CognitionPurpose.DISCOVER_HYPOTHESES,
            objective_id=goal.goal_id,
            legal_profile_hash=legal_hash,
        )
        return P17ActivityResult(
            hypothesis_revision=(
                state.hypothesis_revision + (1 if hypothesis_ids else 0)
            ),
            hypothesis_ids=hypothesis_ids,
            material_requirement_ids=(goal.goal_id,),
            discovery_required=not complete and not terminal,
            activity_fingerprint=key.fingerprint,
        )

    def assess_p19(self, state: BrainGraphState) -> P19ActivityResult:
        session = self._session(state)
        goal = self._root_goal(session)
        snapshot = self._epistemics.snapshot(
            research_session_id=session.session_id,
            obligation_id=goal.goal_id,
            principal=self._principal,
        )
        if len(snapshot.hypotheses) < 2:
            raise BrainV2OwnerError(
                "BRAIN_V2_P19_COMPETING_HYPOTHESES_REQUIRED",
                goal.goal_id,
            )

        # P19 may know whether a bounded analytical re-entry is potentially
        # available without touching P17 at all. This preserves the ONE_PASS
        # invariant: P17 is consulted only after P19 actually emits a typed
        # NextTestRequest. Final callability remains fail-closed below.
        parent_verified = any(
            item.obligation_id == goal.goal_id
            and str(getattr(item.state, "value", item.state)) == "VERIFIED"
            for item in session.obligations
        )
        typed_adaptive_intent = (
            goal.goal_id in set(state.follow_verified_material_goal_ids)
        )
        discrimination_capacity = (
            typed_adaptive_intent
            and state.adaptive_reentries < state.max_adaptive_reentries
            and bool(self._native_session_token)
            and parent_verified
            and bool(state.evidence_ids)
        )
        key = self._cognition_key(
            state=state,
            owner="P19",
            purpose=CognitionPurpose.ASSESS_NEW_EVIDENCE,
            objective_id=goal.goal_id,
            legal_profile_hash=_fingerprint(
                {
                    "hypotheses": [
                        item.hypothesis.hypothesis_id
                        for item in snapshot.hypotheses
                    ],
                    "scope": state.scope_version_id,
                    "typed_adaptive_intent": typed_adaptive_intent,
                    "discriminating_test_capacity": discrimination_capacity,
                }
            ),
        )

        assessment = None
        if (
            key.fingerprint in set(state.activity_fingerprints)
            and state.latest_p19_assessment_ref is not None
        ):
            prior = self._epistemics.load_assessment(
                assessment_id=state.latest_p19_assessment_ref,
                principal=self._principal,
            )
            if (
                prior.research_session_id == session.session_id
                and prior.obligation_id == goal.goal_id
            ):
                assessment = prior

        if assessment is None:
            feedback_code = (
                "P19_DISCRIMINATING_TEST_AVAILABLE"
                if discrimination_capacity
                else "P19_NO_CALLABLE_DISCRIMINATING_TEST"
            )
            propose_with_context = getattr(
                self._epistemic_manager,
                "propose_with_context",
                None,
            )
            if callable(propose_with_context):
                scope_authority = project_p19_scope_authority(
                    brief=session.accepted_brief,
                    scope_lineage_id=session.lineage_id,
                    expected_scope_fingerprint=snapshot.scope_fingerprint,
                )
                draft = propose_with_context(
                    snapshot,
                    objective=None,
                    scope_authority=scope_authority.model_dump(mode="json"),
                    discriminating_test_available=discrimination_capacity,
                    policy_statuses={},
                    deterministic_feedback_code=feedback_code,
                )
            else:
                draft = self._epistemic_manager.propose(
                    snapshot,
                    policy_statuses={},
                    deterministic_feedback_code=feedback_code,
                )
            assessment = self._epistemics.assess(
                draft=draft,
                principal=self._principal,
            )

        request = next_test_request(
            snapshot=snapshot,
            assessment=assessment,
            scope_lineage_id=session.lineage_id,
            scope_version_id=state.scope_version_id or "scope_v1",
        )
        if request is not None:
            investigation_snapshot = self._investigation.snapshot(
                session_id=session.session_id,
                principal=self._principal,
            )
        if request is not None and not discriminating_test_is_callable(
            snapshot=investigation_snapshot,
            request=request,
            evidence_surface_available=bool(self._native_session_token),
            target_obligation_id=goal.goal_id,
        ):
            # P19 asked for discrimination but the deterministic P17/native
            # boundary says it cannot be executed legally. P19, not LangGraph,
            # owns the honest terminal reassessment.
            propose_with_context = getattr(
                self._epistemic_manager,
                "propose_with_context",
                None,
            )
            if callable(propose_with_context):
                scope_authority = project_p19_scope_authority(
                    brief=session.accepted_brief,
                    scope_lineage_id=session.lineage_id,
                    expected_scope_fingerprint=snapshot.scope_fingerprint,
                )
                terminal_draft = propose_with_context(
                    snapshot,
                    objective=None,
                    scope_authority=scope_authority.model_dump(mode="json"),
                    discriminating_test_available=False,
                    policy_statuses={},
                    deterministic_feedback_code=(
                        "P19_NO_CALLABLE_DISCRIMINATING_TEST"
                    ),
                )
            else:
                terminal_draft = self._epistemic_manager.propose(
                    snapshot,
                    policy_statuses={},
                    deterministic_feedback_code=(
                        "P19_NO_CALLABLE_DISCRIMINATING_TEST"
                    ),
                )
            assessment = self._epistemics.assess(
                draft=terminal_draft,
                principal=self._principal,
            )
            request = next_test_request(
                snapshot=snapshot,
                assessment=assessment,
                scope_lineage_id=session.lineage_id,
                scope_version_id=state.scope_version_id or "scope_v1",
            )

        if assessment.aggregate_outcome != AggregateOutcome.IN_PROGRESS:
            route = BrainP19Route.SUFFICIENT
        elif request is not None:
            route = BrainP19Route.NEXT_TEST_REQUIRED
        else:
            route = BrainP19Route.INCONCLUSIVE
        return P19ActivityResult(
            assessment_ref=assessment.assessment_id,
            route=route,
            hypothesis_revision=state.hypothesis_revision,
            hypothesis_ids=tuple(
                item.hypothesis.hypothesis_id
                for item in snapshot.hypotheses
            ),
            pending_next_test_ref=(
                request.request_id if request is not None else None
            ),
            activity_fingerprint=key.fingerprint,
        )

    def _current_next_test(
        self,
        *,
        state: BrainGraphState,
    ) -> tuple[NextTestRequest, Any, Any]:
        session = self._session(state)
        goal = self._root_goal(session)
        if state.latest_p19_assessment_ref is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_P19_ASSESSMENT_REQUIRED",
                goal.goal_id,
            )
        snapshot = self._epistemics.snapshot(
            research_session_id=session.session_id,
            obligation_id=goal.goal_id,
            principal=self._principal,
        )
        assessment = self._epistemics.load_assessment(
            assessment_id=state.latest_p19_assessment_ref,
            principal=self._principal,
        )
        request = next_test_request(
            snapshot=snapshot,
            assessment=assessment,
            scope_lineage_id=session.lineage_id,
            scope_version_id=state.scope_version_id or "scope_v1",
        )
        if (
            request is None
            or request.request_id != state.pending_next_test_ref
        ):
            raise BrainV2OwnerError(
                "BRAIN_V2_NEXT_TEST_REF_MISMATCH",
                state.pending_next_test_ref or "none",
            )
        return request, session, goal

    def design_next_test(self, state: BrainGraphState) -> P17ActivityResult:
        request, session, goal = self._current_next_test(state=state)
        snapshot = self._investigation.snapshot(
            session_id=session.session_id,
            principal=self._principal,
        )
        if not discriminating_test_is_callable(
            snapshot=snapshot,
            request=request,
            evidence_surface_available=bool(self._native_session_token),
            target_obligation_id=goal.goal_id,
        ):
            raise BrainV2OwnerError(
                "BRAIN_V2_NEXT_TEST_NOT_CALLABLE",
                request.request_id,
            )

        before_pairs = set(
            self._durable_evidence_pairs(
                session=session,
                obligation_id=goal.goal_id,
            )
        )
        step, _ = self._investigation.run_one(
            session_id=session.session_id,
            principal=self._principal,
            manager=_NextTestProposalManager(
                request=request,
                obligation_id=goal.goal_id,
            ),
            native_session_token=self._native_session_token,
            downstream_reentry_intent=(
                InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
            ),
            downstream_reentry_obligation_id=goal.goal_id,
        )
        for hypothesis_id in request.hypothesis_ids:
            self._epistemics.create_grounding(
                hypothesis_id=hypothesis_id,
                source_kind=GroundingSourceKind.P17_REASONING_STEP,
                source_ref=step.step_id,
                relation=GroundingRelation.CONTEXT,
                principal=self._principal,
            )

        current = self._research.resume_state(
            session_id=session.session_id,
            principal=self._principal,
        )
        after_pairs = self._durable_evidence_pairs(
            session=current,
            obligation_id=goal.goal_id,
        )
        new_pairs = tuple(
            item for item in after_pairs
            if item not in before_pairs
        )
        if not new_pairs:
            raise BrainV2OwnerError(
                "BRAIN_V2_NEXT_TEST_NO_NEW_EVIDENCE",
                request.request_id,
            )
        self._ground_evidence(
            state=state,
            evidence_pairs=new_pairs,
        )

        key = self._cognition_key(
            state=state,
            owner="P17",
            purpose=CognitionPurpose.DESIGN_DISCRIMINATING_TEST,
            objective_id=request.request_id,
            legal_profile_hash=snapshot.fingerprint,
        )
        return P17ActivityResult(
            hypothesis_revision=state.hypothesis_revision,
            hypothesis_ids=state.hypothesis_ids,
            material_requirement_ids=(goal.goal_id,),
            discovery_required=False,
            produced_evidence_ids=tuple(item[0] for item in new_pairs),
            produced_receipt_refs=tuple(item[1] for item in new_pairs),
            activity_fingerprint=key.fingerprint,
        )

    def _report_with_epistemic_projection(
        self,
        *,
        state: BrainGraphState,
        session,
        base: ReportDraft,
    ) -> ReportDraft:
        """Add exact P19-governed judgment to the existing P20 draft.

        P20 remains the publication authority. This projection copies only
        canonical P19 assessment state and lets ReportDocumentStore.validate
        every resulting statement/source/limitation before sealing.
        """

        assessment_ref = state.latest_p19_assessment_ref
        if assessment_ref is None:
            raise BrainV2OwnerError(
                "BRAIN_V2_P20_P19_ASSESSMENT_REQUIRED",
                session.session_id,
            )
        goal = self._root_goal(session)
        assessment = self._epistemics.load_assessment(
            assessment_id=assessment_ref,
            principal=self._principal,
        )
        if (
            assessment.research_session_id != session.session_id
            or assessment.obligation_id != goal.goal_id
        ):
            raise BrainV2OwnerError(
                "BRAIN_V2_P20_P19_SCOPE_MISMATCH",
                assessment_ref,
            )

        source = SourceReference(
            source_kind=ReportSourceKind.P19_ASSESSMENT,
            source_ref=assessment.assessment_id,
            obligation_id=goal.goal_id,
        )
        extra_statements: list[ReportStatement] = []
        extra_limitations: list[ReportLimitation] = []

        if assessment.aggregate_outcome == AggregateOutcome.ROOT_CAUSE_ESTABLISHED:
            for hypothesis_id in assessment.root_cause_hypothesis_ids:
                sid = stable_statement_id(
                    {
                        "kind": ReportStatementKind.ROOT_CAUSE.value,
                        "source": source.model_dump(mode="json"),
                        "hypothesis_id": hypothesis_id,
                    }
                )
                extra_statements.append(
                    ReportStatement(
                        statement_id=sid,
                        statement_kind=ReportStatementKind.ROOT_CAUSE,
                        source_refs=(source,),
                        obligation_refs=(goal.goal_id,),
                        upstream_epistemic_ceiling=(
                            AggregateOutcome.ROOT_CAUSE_ESTABLISHED.value
                        ),
                        payload={"hypothesis_id": hypothesis_id},
                    )
                )
        elif (
            assessment.aggregate_outcome
            == AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS
        ):
            governed = [
                item.hypothesis_id
                for item in assessment.candidates
                if (
                    item.disposition == HypothesisDisposition.RETAINED
                    and item.contribution_class
                    in {ContributionClass.DOMINANT, ContributionClass.MATERIAL}
                )
            ]
            if not governed:
                raise BrainV2OwnerError(
                    "BRAIN_V2_P20_CONTRIBUTION_SET_EMPTY",
                    assessment.assessment_id,
                )
            sid = stable_statement_id(
                {
                    "kind": ReportStatementKind.CONTRIBUTION.value,
                    "source": source.model_dump(mode="json"),
                    "candidate_hypothesis_ids": governed,
                }
            )
            extra_statements.append(
                ReportStatement(
                    statement_id=sid,
                    statement_kind=ReportStatementKind.CONTRIBUTION,
                    source_refs=(source,),
                    obligation_refs=(goal.goal_id,),
                    upstream_epistemic_ceiling=assessment.aggregate_outcome.value,
                    payload={"candidate_hypothesis_ids": governed},
                )
            )
        elif (
            assessment.aggregate_outcome
            == AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
        ):
            sid = stable_statement_id(
                {
                    "kind": ReportStatementKind.UNCERTAINTY.value,
                    "source": source.model_dump(mode="json"),
                    "assessment": assessment.assessment_id,
                }
            )
            extra_statements.append(
                ReportStatement(
                    statement_id=sid,
                    statement_kind=ReportStatementKind.UNCERTAINTY,
                    source_refs=(source,),
                    obligation_refs=(goal.goal_id,),
                    upstream_epistemic_ceiling=assessment.aggregate_outcome.value,
                    payload={},
                )
            )
        else:
            raise BrainV2OwnerError(
                "BRAIN_V2_P20_NONTERMINAL_P19",
                assessment.aggregate_outcome.value,
            )

        for ordinal, detail in enumerate(assessment.limitations):
            limitation_id = stable_limitation_id(
                {
                    "assessment_id": assessment.assessment_id,
                    "obligation_id": goal.goal_id,
                    "ordinal": ordinal,
                    "detail": detail,
                }
            )
            limitation = ReportLimitation(
                limitation_id=limitation_id,
                obligation_id=goal.goal_id,
                code="P19_EPISTEMIC_LIMITATION",
                detail=detail,
                source_refs=(source,),
            )
            extra_limitations.append(limitation)
            sid = stable_statement_id(
                {
                    "kind": ReportStatementKind.LIMITATION.value,
                    "limitation_id": limitation_id,
                    "source": source.model_dump(mode="json"),
                }
            )
            extra_statements.append(
                ReportStatement(
                    statement_id=sid,
                    statement_kind=ReportStatementKind.LIMITATION,
                    source_refs=(source,),
                    obligation_refs=(goal.goal_id,),
                    limitation_refs=(limitation_id,),
                    upstream_epistemic_ceiling="LIMITATION",
                    payload={"limitation_id": limitation_id},
                )
            )

        extra_ids = tuple(item.statement_id for item in extra_statements)
        coverage = tuple(
            entry.model_copy(
                update={
                    "statement_ids": tuple(
                        dict.fromkeys((*entry.statement_ids, *extra_ids))
                    )
                }
            )
            if entry.obligation_id == goal.goal_id
            else entry
            for entry in base.coverage
        )
        return base.model_copy(
            update={
                "coverage": coverage,
                "statements": (*base.statements, *extra_statements),
                "limitations": (*base.limitations, *extra_limitations),
            }
        )

    def synthesize_report(self, state: BrainGraphState) -> ReportActivityResult:
        session = self._session(state)
        report_key = (
            f"brain-v2:{state.thread_id}:{state.scope_version_id or 'scope_v1'}"
        )
        base = self._reports.draft_from_governed_research(
            research_session_id=session.session_id,
            report_key=report_key,
            principal=self._principal,
        )
        draft = self._report_with_epistemic_projection(
            state=state,
            session=session,
            base=base,
        )
        report = self._reports.seal(
            draft=draft,
            principal=self._principal,
        )
        key = self._cognition_key(
            state=state,
            owner="P20",
            purpose=CognitionPurpose.SYNTHESIZE_REPORT,
            objective_id=report_key,
            legal_profile_hash=_fingerprint(
                {
                    "assessment": state.latest_p19_assessment_ref,
                    "evidence": list(state.evidence_ids),
                }
            ),
        )
        return ReportActivityResult(
            report_ref=report.report_id,
            activity_fingerprint=key.fingerprint,
        )
