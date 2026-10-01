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
from app.v3.research_manager import InvestigationIntent

from .activities import P17ActivityResult
from .adaptive_test_design import (
    AdaptiveTestDesignError,
    TypedNextTestProposalManager,
)
from .keys import CognitionPurpose
from .owner_adapter import BrainV2OwnerError, DimaBrainV2Activities
from .state import BrainGraphState


class AdaptiveDimaBrainV2Activities(DimaBrainV2Activities):
    """Use the existing P17 owner to design one typed adaptive re-entry."""

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

        before_evidence_pairs = tuple(
            self._durable_evidence_pairs(
                session=session,
                obligation_id=goal.goal_id,
            )
        )
        before_pairs = set(before_evidence_pairs)
        try:
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
