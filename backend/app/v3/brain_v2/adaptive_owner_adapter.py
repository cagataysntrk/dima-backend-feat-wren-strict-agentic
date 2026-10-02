"""Adaptive P19 -> P17 owner composition for Brain V2.

The base Brain V2 owner adapter remains the canonical composition surface. This
specialization changes only the discriminating-test seam: P19 supplies the
typed NextTestRequest, existing P17 cognition designs one bounded analytical
question inside the closed obligation/Evidence vocabulary, and the sealed P17
manager/native path validates and executes it.
"""
from __future__ import annotations

from app.v3.hypothesis_root_cause import (
    GroundingRelation,
    GroundingSourceKind,
)
from app.v3.hypothesis_root_cause_v1 import (
    discriminating_test_is_callable,
)
from app.v3.research_analytical_scope import analytical_scope_contract
from app.v3.research_manager import InvestigationIntent

from .activities import P17ActivityResult, P17NextTestDisposition
from .adaptive_test_design import (
    AdaptiveTestDesignError,
    NextTestMaterialDisposition,
    TypedNextTestProposalManager,
    evaluate_next_test_material_delta,
)
from .keys import CognitionPurpose
from .owner_adapter import BrainV2OwnerError, DimaBrainV2Activities
from .state import BrainGraphState


class AdaptiveDimaBrainV2Activities(DimaBrainV2Activities):
    """Use the existing P17 owner to design one typed adaptive re-entry."""

    def _inconclusive_next_test(
        self,
        *,
        state: BrainGraphState,
        request,
        snapshot,
        reason_code: str,
    ) -> P17ActivityResult:
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
            material_requirement_ids=(),
            discovery_required=False,
            produced_evidence_ids=(),
            produced_receipt_refs=(),
            next_test_disposition=P17NextTestDisposition.INCONCLUSIVE,
            next_test_reason_code=reason_code,
            activity_fingerprint=key.fingerprint,
        )

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
            return self._inconclusive_next_test(
                state=state,
                request=request,
                snapshot=snapshot,
                reason_code="NEXT_TEST_NOT_CALLABLE",
            )

        before_evidence_pairs = tuple(
            self._durable_evidence_pairs(
                session=session,
                obligation_id=goal.goal_id,
            )
        )
        before_pairs = set(before_evidence_pairs)
        before_result_hashes = {
            item.result_hash for item in snapshot.evidence_results
        }
        try:
            parent_scope = analytical_scope_contract(
                session=session,
                obligation_id=goal.goal_id,
            )
            brief = session.accepted_brief
            if brief is None:
                raise AdaptiveTestDesignError(
                    "adaptive child material requires accepted ResearchBrief"
                )
            decision = evaluate_next_test_material_delta(
                parent=parent_scope,
                request=request,
                governed_semantic_refs=tuple(
                    item.candidate_id for item in brief.scope.semantic_refs
                ),
            )
            if decision.disposition == NextTestMaterialDisposition.INCONCLUSIVE:
                return self._inconclusive_next_test(
                    state=state,
                    request=request,
                    snapshot=snapshot,
                    reason_code=decision.reason_code or "NO_LEGAL_MATERIAL_DELTA",
                )
            assert decision.delta is not None
            child_scope = decision.delta.child_contract
            manager = TypedNextTestProposalManager(
                inner=self._investigation_manager,
                request=request,
                obligation_id=goal.goal_id,
                evidence_refs=tuple(
                    item[0] for item in before_evidence_pairs
                ),
            )
            step, _ = self._investigation.run_one(
                session_id=session.session_id,
                principal=self._principal,
                manager=manager,
                native_session_token=self._native_session_token,
                downstream_reentry_intent=(
                    InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
                ),
                downstream_reentry_obligation_id=goal.goal_id,
                child_analytical_scope=child_scope,
            )
        except AdaptiveTestDesignError as exc:
            raise BrainV2OwnerError(
                "BRAIN_V2_NEXT_TEST_DESIGN_INVALID",
                str(exc),
            ) from exc

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
            return self._inconclusive_next_test(
                state=state,
                request=request,
                snapshot=snapshot,
                reason_code="NO_NEW_EVIDENCE",
            )

        after_snapshot = self._investigation.snapshot(
            session_id=current.session_id,
            principal=self._principal,
        )
        new_pair_set = set(new_pairs)
        new_result_hashes = {
            item.result_hash
            for item in after_snapshot.evidence_results
            if (item.evidence_id, item.receipt_id) in new_pair_set
        }
        if (
            not new_result_hashes
            or new_result_hashes.issubset(before_result_hashes)
        ):
            return self._inconclusive_next_test(
                state=state,
                request=request,
                snapshot=snapshot,
                reason_code="NO_INFORMATION_GAIN",
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
            next_test_disposition=P17NextTestDisposition.EXECUTED,
            activity_fingerprint=key.fingerprint,
        )
