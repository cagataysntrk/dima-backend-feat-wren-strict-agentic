"""Deterministic post-acceptance Manager action availability.

This module is intentionally language-blind. It does not choose an action, interpret a
user phrase, mint semantic identity, execute work, mutate Evidence, or decide completion.
It projects already-governed runtime state into the smallest cognition action surface
that remains structurally useful. Runtime gates remain final authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


POST_ACCEPTANCE_ACTIONS = (
    "resolve_semantics",
    "propose_branches",
    "disposition_research_directive",
    "propose_hypothesis",
    "propose_hypothesis_with_next_test",
    "propose_hypothesis_evidence_relation",
    "propose_hypothesis_next_test",
    "run_analytics",
    "run_relationship",
    "inspect_evidence",
    "request_clarification",
    "finish",
)

ROOT_ONLY_ACTIONS = frozenset(
    {
        "propose_hypothesis",
        "propose_hypothesis_with_next_test",
        "propose_hypothesis_evidence_relation",
        "propose_hypothesis_next_test",
    }
)


class ActionAvailabilityReason(StrEnum):
    AVAILABLE_BY_RUNTIME = "AVAILABLE_BY_RUNTIME"
    ROOT_CAUSE_INACTIVE = "ROOT_CAUSE_INACTIVE"
    NO_INSPECTED_VERIFIED_EVIDENCE = "NO_INSPECTED_VERIFIED_EVIDENCE"
    NO_UNDISCLOSED_UNINSPECTED_EVIDENCE = "NO_UNDISCLOSED_UNINSPECTED_EVIDENCE"
    FRESH_EVIDENCE_ALREADY_DISCLOSED = "FRESH_EVIDENCE_ALREADY_DISCLOSED"
    POST_ACCEPTANCE_USER_SOURCE_FORBIDDEN = "POST_ACCEPTANCE_USER_SOURCE_FORBIDDEN"
    EXISTING_GOVERNED_HANDLES_SATISFY_NEXT_TEST = (
        "EXISTING_GOVERNED_HANDLES_SATISFY_NEXT_TEST"
    )
    DERIVED_SEMANTIC_EXPANSION_POTENTIALLY_REQUIRED = (
        "DERIVED_SEMANTIC_EXPANSION_POTENTIALLY_REQUIRED"
    )
    ROOT_EVIDENCE_AND_EXISTING_HANDLES_READY = (
        "ROOT_EVIDENCE_AND_EXISTING_HANDLES_READY"
    )
    ROOT_HYPOTHESIS_ALREADY_EXISTS = "ROOT_HYPOTHESIS_ALREADY_EXISTS"
    ROOT_HYPOTHESIS_REQUIRED = "ROOT_HYPOTHESIS_REQUIRED"
    ROOT_NEXT_TEST_NOT_FEASIBLE = "ROOT_NEXT_TEST_NOT_FEASIBLE"
    NO_OPEN_ADAPTIVE_DIRECTIVE = "NO_OPEN_ADAPTIVE_DIRECTIVE"


@dataclass(frozen=True)
class RootActionState:
    root_id: str
    hypothesis_count: int
    root_handle_kinds: tuple[str, ...]
    next_test_required_kind_sets: tuple[tuple[str, ...], ...]
    effective_inspected_verified_evidence_refs: tuple[str, ...] = ()

    @property
    def feasible_next_test(self) -> bool:
        available = frozenset(self.root_handle_kinds)
        return any(
            frozenset(required).issubset(available)
            for required in self.next_test_required_kind_sets
        )

    @property
    def evidence_ready(self) -> bool:
        return bool(self.effective_inspected_verified_evidence_refs)


@dataclass(frozen=True)
class ManagerActionAvailabilityContext:
    root_states: tuple[RootActionState, ...] = ()
    inspectable_old_evidence_refs: tuple[str, ...] = ()
    effective_inspected_verified_evidence_refs: tuple[str, ...] = ()
    fresh_disclosed_evidence_ref: str | None = None
    fresh_disclosed_verified: bool = False
    open_adaptive_directive_count: int = 0
    remaining_manager_turns: int = 0


@dataclass(frozen=True)
class ManagerActionAvailabilityProfile:
    available_actions: tuple[str, ...]
    unavailable_actions: tuple[tuple[str, tuple[str, ...]], ...]
    available_reasons: tuple[tuple[str, tuple[str, ...]], ...]
    inspectable_evidence_refs: tuple[str, ...]
    inspection_required_for_current_delta: bool
    post_acceptance_resolve_provenance: tuple[str, ...] = ("AGENT_DERIVED",)

    def allows(self, action: str) -> bool:
        return action in self.available_actions

    def reasons_for_unavailable(self, action: str) -> tuple[str, ...]:
        return dict(self.unavailable_actions).get(action, ())

    def model_view(self) -> dict[str, object]:
        return {
            "available_actions": list(self.available_actions),
            "unavailable_actions": [
                {"action": action, "reason_codes": list(reasons)}
                for action, reasons in self.unavailable_actions
            ],
            "available_reasons": [
                {"action": action, "reason_codes": list(reasons)}
                for action, reasons in self.available_reasons
            ],
            "inspectable_evidence_refs": list(self.inspectable_evidence_refs),
            "inspection_required_for_current_delta": (
                self.inspection_required_for_current_delta
            ),
            "resolve_semantics_provenance": list(
                self.post_acceptance_resolve_provenance
            ),
        }


class ManagerActionAvailability:
    """Pure projection from governed runtime facts to advertised cognition actions."""

    @staticmethod
    def evaluate(
        context: ManagerActionAvailabilityContext,
    ) -> ManagerActionAvailabilityProfile:
        allowed = set(POST_ACCEPTANCE_ACTIONS)
        unavailable: dict[str, list[str]] = {}
        available_reasons: dict[str, list[str]] = {
            action: [ActionAvailabilityReason.AVAILABLE_BY_RUNTIME.value]
            for action in POST_ACCEPTANCE_ACTIONS
        }

        def remove(action: str, reason: ActionAvailabilityReason) -> None:
            allowed.discard(action)
            available_reasons.pop(action, None)
            unavailable.setdefault(action, []).append(reason.value)

        def reason(action: str, value: ActionAvailabilityReason) -> None:
            if action in allowed:
                available_reasons.setdefault(action, []).append(value.value)

        roots = context.root_states
        if not roots:
            for action in ROOT_ONLY_ACTIONS:
                remove(action, ActionAvailabilityReason.ROOT_CAUSE_INACTIVE)

        effective_evidence = tuple(
            dict.fromkeys(context.effective_inspected_verified_evidence_refs)
        )
        if not effective_evidence:
            remove(
                "propose_branches",
                ActionAvailabilityReason.NO_INSPECTED_VERIFIED_EVIDENCE,
            )
            remove(
                "disposition_research_directive",
                ActionAvailabilityReason.NO_INSPECTED_VERIFIED_EVIDENCE,
            )

        if context.open_adaptive_directive_count <= 0:
            remove(
                "disposition_research_directive",
                ActionAvailabilityReason.NO_OPEN_ADAPTIVE_DIRECTIVE,
            )

        if context.inspectable_old_evidence_refs:
            reason(
                "inspect_evidence",
                ActionAvailabilityReason.AVAILABLE_BY_RUNTIME,
            )
        else:
            if (
                context.fresh_disclosed_evidence_ref is not None
                and context.fresh_disclosed_verified
            ):
                remove(
                    "inspect_evidence",
                    ActionAvailabilityReason.FRESH_EVIDENCE_ALREADY_DISCLOSED,
                )
            else:
                remove(
                    "inspect_evidence",
                    ActionAvailabilityReason.NO_UNDISCLOSED_UNINSPECTED_EVIDENCE,
                )

        # Post-acceptance USER_SOURCE re-resolution is never a legal cognition option.
        # The action itself remains only when AGENT_DERIVED expansion is potentially
        # required by governed state.
        if not effective_evidence:
            remove(
                "resolve_semantics",
                ActionAvailabilityReason.NO_INSPECTED_VERIFIED_EVIDENCE,
            )
        elif roots and all(root.feasible_next_test for root in roots):
            remove(
                "resolve_semantics",
                ActionAvailabilityReason.EXISTING_GOVERNED_HANDLES_SATISFY_NEXT_TEST,
            )
        else:
            reason(
                "resolve_semantics",
                ActionAvailabilityReason.DERIVED_SEMANTIC_EXPANSION_POTENTIALLY_REQUIRED,
            )

        if roots:
            initial_ready = tuple(
                root
                for root in roots
                if root.hypothesis_count == 0 and root.evidence_ready
            )
            composite_ready = tuple(
                root for root in initial_ready if root.feasible_next_test
            )
            any_hypothesis = any(root.hypothesis_count > 0 for root in roots)

            if not initial_ready:
                remove(
                    "propose_hypothesis",
                    (
                        ActionAvailabilityReason.ROOT_HYPOTHESIS_ALREADY_EXISTS
                        if any_hypothesis
                        else ActionAvailabilityReason.NO_INSPECTED_VERIFIED_EVIDENCE
                    ),
                )
            if not composite_ready:
                if any_hypothesis:
                    remove(
                        "propose_hypothesis_with_next_test",
                        ActionAvailabilityReason.ROOT_HYPOTHESIS_ALREADY_EXISTS,
                    )
                elif not initial_ready:
                    remove(
                        "propose_hypothesis_with_next_test",
                        ActionAvailabilityReason.NO_INSPECTED_VERIFIED_EVIDENCE,
                    )
                else:
                    remove(
                        "propose_hypothesis_with_next_test",
                        ActionAvailabilityReason.ROOT_NEXT_TEST_NOT_FEASIBLE,
                    )
            else:
                reason(
                    "propose_hypothesis_with_next_test",
                    ActionAvailabilityReason.ROOT_EVIDENCE_AND_EXISTING_HANDLES_READY,
                )

            if not any_hypothesis:
                remove(
                    "propose_hypothesis_next_test",
                    ActionAvailabilityReason.ROOT_HYPOTHESIS_REQUIRED,
                )
                remove(
                    "propose_hypothesis_evidence_relation",
                    ActionAvailabilityReason.ROOT_HYPOTHESIS_REQUIRED,
                )

        inspection_required = not (
            context.fresh_disclosed_evidence_ref is not None
            and context.fresh_disclosed_verified
        )

        return ManagerActionAvailabilityProfile(
            available_actions=tuple(
                action for action in POST_ACCEPTANCE_ACTIONS if action in allowed
            ),
            unavailable_actions=tuple(
                (action, tuple(dict.fromkeys(reasons)))
                for action, reasons in sorted(unavailable.items())
            ),
            available_reasons=tuple(
                (action, tuple(dict.fromkeys(reasons)))
                for action, reasons in sorted(available_reasons.items())
                if action in allowed
            ),
            inspectable_evidence_refs=tuple(
                dict.fromkeys(context.inspectable_old_evidence_refs)
            ),
            inspection_required_for_current_delta=inspection_required,
        )
