"""Bounded StandardBuilder state machine for Day 6.5.

STANDARD_DIRECT is not a second engine. It is the first-attempt successful outcome of
this same Standard engine. Generic loop mechanics live in BoundedAgentRuntimeKernel;
this module owns only Standard-domain state, projection construction, validation and
routing outcomes.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from app.v2.agent_runtime import (
    BoundedAgentRuntimeKernel,
    BoundedLoopBudget,
    LoopTerminalReason,
)
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
    """Standard-domain consumer of the generic bounded runtime kernel."""

    def __init__(
        self,
        *,
        compiler: StandardProjectionCompiler,
        representability: RepresentabilityGate | None = None,
        tenant_binding: str,
        context_version: str,
        max_model_turns: int = 4,
        max_tool_calls: int = 8,
    ) -> None:
        self._compiler = compiler
        self._representability = representability or RepresentabilityGate()
        self._tenant = tenant_binding
        self._context = context_version
        self._runtime = BoundedAgentRuntimeKernel(
            budget=BoundedLoopBudget(
                max_model_turns=max(1, int(max_model_turns)),
                max_tool_calls=max(0, int(max_tool_calls)),
                max_executions_per_action_state_pair=1,
            )
        )

        # The profile/domain owns the meaning of StateFingerprint. For the current
        # StandardBuilder vertical, authoritative execution state is the immutable
        # tenant/context + validator version. A changed proposal changes ActionFingerprint;
        # repeating the same proposal against this unchanged state is NO_PROGRESS.
        self._runtime_state_fingerprint = self._fingerprint(
            {
                "profile": "STANDARD",
                "tenant_binding": tenant_binding,
                "context_version": context_version,
                "validator": "standard_projection_v1",
            }
        )
        self._last_outcome = StandardBuilderOutcome(
            state=StandardBuilderState.INITIAL,
            proposal_executions=0,
            state_fingerprint=self._result_state_fingerprint(
                state=StandardBuilderState.INITIAL,
                reasons=(),
                projection=None,
            ),
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
        return "state_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]

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

    @property
    def runtime_telemetry(self) -> dict[str, object]:
        return self._runtime.telemetry()

    def submit(
        self,
        obligations: tuple[CandidateObligation, ...],
    ) -> StandardBuilderOutcome:
        if self._last_outcome.terminal:
            return self._last_outcome

        action = {
            "action": "PROPOSE_STANDARD_BINDINGS",
            "obligations": [
                item.model_dump(mode="json")
                for item in obligations
            ],
        }
        reservation = self._runtime.reserve_model_turn(
            action=action,
            state_fingerprint=self._runtime_state_fingerprint,
        )
        if not reservation.allowed:
            if reservation.terminal_reason == LoopTerminalReason.NO_PROGRESS:
                return self._finish_rejected(
                    state=StandardBuilderState.NO_PROGRESS,
                    reasons=(
                        "same standard proposal repeated without state progress",
                    ),
                    action_fingerprint=reservation.action_fingerprint,
                )
            if (
                reservation.terminal_reason
                == LoopTerminalReason.BUDGET_EXHAUSTED
            ):
                return self._finish_rejected(
                    state=StandardBuilderState.BUDGET_EXHAUSTED,
                    reasons=("standard builder proposal budget exhausted",),
                    action_fingerprint=reservation.action_fingerprint,
                )
            return self._finish_rejected(
                state=StandardBuilderState.FAILED,
                reasons=("standard runtime is already terminal",),
                action_fingerprint=reservation.action_fingerprint,
            )

        initial = self._representability.decide_bound(
            obligations=obligations,
            projection=None,
        )
        if initial.decision == RepresentabilityDecision.RESEARCH_REQUIRED:
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.RESEARCH_REQUIRED,
                reasons=initial.reasons,
                projection=None,
            )
        if initial.decision == RepresentabilityDecision.CLARIFICATION_REQUIRED:
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.CLARIFICATION_REQUIRED,
                reasons=initial.reasons,
                projection=None,
            )
        if initial.decision == RepresentabilityDecision.UNSUPPORTED:
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.UNSUPPORTED,
                reasons=initial.reasons,
                projection=None,
            )

        compiled = self._compiler.compile_bound(
            obligations=obligations,
            tenant_binding=self._tenant,
            context_version=self._context,
        )
        if not compiled.compiled or compiled.projection is None:
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.NEEDS_REPAIR,
                reasons=compiled.reasons,
                projection=None,
            )

        proof = self._representability.decide_bound(
            obligations=obligations,
            projection=compiled.projection,
        )
        if proof.decision == RepresentabilityDecision.STANDARD_LOSSLESS:
            mode = (
                StandardWorkMode.STANDARD_DIRECT
                if self._runtime.counters.model_turns == 1
                else StandardWorkMode.STANDARD_BUILDER
            )
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.PROJECTION_READY,
                work_mode=mode,
                reasons=proof.reasons,
                projection=compiled.projection,
            )
        if proof.decision == RepresentabilityDecision.RESEARCH_REQUIRED:
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.RESEARCH_REQUIRED,
                reasons=proof.reasons,
                projection=None,
            )
        if proof.decision == RepresentabilityDecision.CLARIFICATION_REQUIRED:
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.CLARIFICATION_REQUIRED,
                reasons=proof.reasons,
                projection=None,
            )
        if proof.decision == RepresentabilityDecision.UNSUPPORTED:
            return self._finish_allowed(
                reservation=reservation,
                state=StandardBuilderState.UNSUPPORTED,
                reasons=proof.reasons,
                projection=None,
            )

        return self._finish_allowed(
            reservation=reservation,
            state=StandardBuilderState.NEEDS_REPAIR,
            reasons=proof.reasons,
            projection=None,
        )

    def _finish_allowed(
        self,
        *,
        reservation,
        state: StandardBuilderState,
        reasons: tuple[str, ...],
        projection: StandardProjection | None,
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
            proposal_executions=self._runtime.counters.model_turns,
            action_fingerprint=reservation.action_fingerprint,
            state_fingerprint=state_fingerprint,
        )
        self._runtime.observe(
            reservation=reservation,
            result=outcome,
            state_after=state_fingerprint,
        )
        if outcome.terminal:
            self._runtime.terminate(
                LoopTerminalReason.FAILED
                if state == StandardBuilderState.FAILED
                else LoopTerminalReason.COMPLETED
            )
        self._last_outcome = outcome
        return outcome

    def _finish_rejected(
        self,
        *,
        state: StandardBuilderState,
        reasons: tuple[str, ...],
        action_fingerprint: str,
    ) -> StandardBuilderOutcome:
        state_fingerprint = self._result_state_fingerprint(
            state=state,
            reasons=reasons,
            projection=None,
        )
        outcome = StandardBuilderOutcome(
            state=state,
            reasons=reasons,
            proposal_executions=self._runtime.counters.model_turns,
            action_fingerprint=action_fingerprint,
            state_fingerprint=state_fingerprint,
        )
        self._last_outcome = outcome
        return outcome
