"""Bounded StandardBuilder state machine for Day 6.5.

STANDARD_DIRECT is not a second engine. It is the first-attempt successful path of this
same builder. The builder only constructs one governed StandardProjection; it does not
perform research, execute SQL, query data, or decide research completion.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from app.v2.manager_models import (
    CandidateObligation,
    RepresentabilityDecision,
    StandardProjection,
)
from app.v2.models import FrozenModel
from app.v2.representability import RepresentabilityGate
from app.v2.standard_projection import StandardProjectionCompiler


class StandardBuilderState(StrEnum):
    INITIAL = "INITIAL"
    NEEDS_REPAIR = "NEEDS_REPAIR"
    PROJECTION_READY = "PROJECTION_READY"
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"
    NO_PROGRESS = "NO_PROGRESS"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    FAILED = "FAILED"


class StandardWorkMode(StrEnum):
    STANDARD_DIRECT = "STANDARD_DIRECT"
    STANDARD_BUILDER = "STANDARD_BUILDER"


class StandardBuilderOutcome(FrozenModel):
    state: StandardBuilderState
    work_mode: StandardWorkMode | None = None
    projection: StandardProjection | None = None
    reasons: tuple[str, ...] = ()
    proposal_executions: int = 0
    action_fingerprint: str | None = None
    state_fingerprint: str | None = None

    @property
    def projection_ready(self) -> bool:
        return (
            self.state == StandardBuilderState.PROJECTION_READY
            and self.projection is not None
        )

    @property
    def terminal(self) -> bool:
        return self.state in {
            StandardBuilderState.PROJECTION_READY,
            StandardBuilderState.RESEARCH_REQUIRED,
            StandardBuilderState.CLARIFICATION_REQUIRED,
            StandardBuilderState.UNSUPPORTED,
            StandardBuilderState.NO_PROGRESS,
            StandardBuilderState.BUDGET_EXHAUSTED,
            StandardBuilderState.FAILED,
        }


class StandardBuilderSession:
    """Finite proposal/validation loop with deterministic no-progress protection."""

    def __init__(
        self,
        *,
        compiler: StandardProjectionCompiler,
        representability: RepresentabilityGate | None = None,
        tenant_binding: str,
        context_version: str,
        max_model_turns: int = 4,
    ) -> None:
        self._compiler = compiler
        self._representability = representability or RepresentabilityGate()
        self._tenant = tenant_binding
        self._context = context_version
        self._max_model_turns = max(1, int(max_model_turns))
        self._proposal_executions = 0
        self._last_action_fingerprint: str | None = None
        self._current_state_fingerprint = self._fingerprint(
            {"state": StandardBuilderState.INITIAL.value}
        )
        self._last_outcome = StandardBuilderOutcome(
            state=StandardBuilderState.INITIAL,
            proposal_executions=0,
            state_fingerprint=self._current_state_fingerprint,
        )

    @staticmethod
    def _fingerprint(payload: object) -> str:
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def _action_fingerprint(
        cls,
        obligations: tuple[CandidateObligation, ...],
    ) -> str:
        return cls._fingerprint(
            {
                "action": "PROPOSE_STANDARD_BINDINGS",
                "obligations": [
                    item.model_dump(mode="json")
                    for item in obligations
                ],
            }
        )

    @classmethod
    def _result_state_fingerprint(
        cls,
        *,
        state: StandardBuilderState,
        reasons: tuple[str, ...],
        projection: StandardProjection | None,
    ) -> str:
        return cls._fingerprint(
            {
                "state": state.value,
                "reasons": list(reasons),
                "projection": (
                    projection.model_dump(mode="json")
                    if projection is not None
                    else None
                ),
            }
        )

    @property
    def snapshot(self) -> StandardBuilderOutcome:
        return self._last_outcome

    def submit(
        self,
        obligations: tuple[CandidateObligation, ...],
    ) -> StandardBuilderOutcome:
        if self._last_outcome.terminal:
            return self._last_outcome

        action_fingerprint = self._action_fingerprint(obligations)

        # Same proposal against unchanged validation state would execute the same action
        # twice. That is deterministic NO_PROGRESS, not another model/tool retry.
        if (
            self._last_action_fingerprint == action_fingerprint
            and self._last_outcome.state == StandardBuilderState.NEEDS_REPAIR
        ):
            return self._finish(
                state=StandardBuilderState.NO_PROGRESS,
                reasons=(
                    "same standard proposal repeated without state progress",
                ),
                projection=None,
                action_fingerprint=action_fingerprint,
            )

        if self._proposal_executions >= self._max_model_turns:
            return self._finish(
                state=StandardBuilderState.BUDGET_EXHAUSTED,
                reasons=("standard builder proposal budget exhausted",),
                projection=None,
                action_fingerprint=action_fingerprint,
            )

        self._proposal_executions += 1
        self._last_action_fingerprint = action_fingerprint

        initial = self._representability.decide_bound(
            obligations=obligations,
            projection=None,
        )
        if initial.decision == RepresentabilityDecision.RESEARCH_REQUIRED:
            return self._finish(
                state=StandardBuilderState.RESEARCH_REQUIRED,
                reasons=initial.reasons,
                projection=None,
                action_fingerprint=action_fingerprint,
            )
        if initial.decision == RepresentabilityDecision.CLARIFICATION_REQUIRED:
            return self._finish(
                state=StandardBuilderState.CLARIFICATION_REQUIRED,
                reasons=initial.reasons,
                projection=None,
                action_fingerprint=action_fingerprint,
            )
        if initial.decision == RepresentabilityDecision.UNSUPPORTED:
            return self._finish(
                state=StandardBuilderState.UNSUPPORTED,
                reasons=initial.reasons,
                projection=None,
                action_fingerprint=action_fingerprint,
            )

        compiled = self._compiler.compile_bound(
            obligations=obligations,
            tenant_binding=self._tenant,
            context_version=self._context,
        )
        if not compiled.compiled or compiled.projection is None:
            return self._finish(
                state=StandardBuilderState.NEEDS_REPAIR,
                reasons=compiled.reasons,
                projection=None,
                action_fingerprint=action_fingerprint,
            )

        proof = self._representability.decide_bound(
            obligations=obligations,
            projection=compiled.projection,
        )
        if proof.decision == RepresentabilityDecision.STANDARD_LOSSLESS:
            mode = (
                StandardWorkMode.STANDARD_DIRECT
                if self._proposal_executions == 1
                else StandardWorkMode.STANDARD_BUILDER
            )
            return self._finish(
                state=StandardBuilderState.PROJECTION_READY,
                work_mode=mode,
                reasons=proof.reasons,
                projection=compiled.projection,
                action_fingerprint=action_fingerprint,
            )
        if proof.decision == RepresentabilityDecision.RESEARCH_REQUIRED:
            return self._finish(
                state=StandardBuilderState.RESEARCH_REQUIRED,
                reasons=proof.reasons,
                projection=None,
                action_fingerprint=action_fingerprint,
            )
        if proof.decision == RepresentabilityDecision.CLARIFICATION_REQUIRED:
            return self._finish(
                state=StandardBuilderState.CLARIFICATION_REQUIRED,
                reasons=proof.reasons,
                projection=None,
                action_fingerprint=action_fingerprint,
            )
        if proof.decision == RepresentabilityDecision.UNSUPPORTED:
            return self._finish(
                state=StandardBuilderState.UNSUPPORTED,
                reasons=proof.reasons,
                projection=None,
                action_fingerprint=action_fingerprint,
            )

        return self._finish(
            state=StandardBuilderState.NEEDS_REPAIR,
            reasons=proof.reasons,
            projection=None,
            action_fingerprint=action_fingerprint,
        )

    def _finish(
        self,
        *,
        state: StandardBuilderState,
        reasons: tuple[str, ...],
        projection: StandardProjection | None,
        action_fingerprint: str | None,
        work_mode: StandardWorkMode | None = None,
    ) -> StandardBuilderOutcome:
        state_fingerprint = self._result_state_fingerprint(
            state=state,
            reasons=reasons,
            projection=projection,
        )
        outcome = StandardBuilderOutcome(
            state=state,
            work_mode=work_mode,
            projection=projection,
            reasons=reasons,
            proposal_executions=self._proposal_executions,
            action_fingerprint=action_fingerprint,
            state_fingerprint=state_fingerprint,
        )
        self._current_state_fingerprint = state_fingerprint
        self._last_outcome = outcome
        return outcome
