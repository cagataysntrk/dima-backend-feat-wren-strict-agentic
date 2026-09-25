"""Deterministic post-acceptance Manager action availability.

This module is intentionally language-blind. It does not choose an action, interpret a
user phrase, mint semantic identity, execute work, mutate Evidence, or decide completion.
It projects already-governed runtime state into the smallest cognition action surface
that remains structurally useful. Runtime gates remain final authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json


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
    POST_TEST_EVIDENCE_RELATION_PENDING = "POST_TEST_EVIDENCE_RELATION_PENDING"
    INSUFFICIENT_HEADROOM_FOR_SEPARATE_HYPOTHESIS = (
        "INSUFFICIENT_RESEARCH_HEADROOM_FOR_SEPARATE_HYPOTHESIS"
    )
    INSUFFICIENT_HEADROOM_FOR_COMPOSITE = (
        "INSUFFICIENT_RESEARCH_HEADROOM_FOR_COMPOSITE"
    )
    NO_OPEN_ADAPTIVE_DIRECTIVE = "NO_OPEN_ADAPTIVE_DIRECTIVE"
    NO_ELIGIBLE_ADAPTIVE_DIRECTIVE_EVIDENCE = (
        "NO_ELIGIBLE_ADAPTIVE_DIRECTIVE_EVIDENCE"
    )
    NO_APPLICABLE_SCOPE = "NO_APPLICABLE_SCOPE"


@dataclass(frozen=True)
class RootActionState:
    root_id: str
    hypothesis_count: int
    root_handle_kinds: tuple[str, ...]
    next_test_required_kind_sets: tuple[tuple[str, ...], ...]
    root_handle_refs: tuple[str, ...] = ()
    hypothesis_refs: tuple[str, ...] = ()
    effective_inspected_verified_evidence_refs: tuple[str, ...] = ()
    pending_relation_hypothesis_refs: tuple[str, ...] = ()
    pending_relation_evidence_refs: tuple[str, ...] = ()

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
class AdaptiveDirectiveDispositionState:
    """One accepted OPEN adaptive directive and its Product-validated Evidence domain."""

    directive_id: str
    parent_obligation_id: str
    eligible_evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActionScopeSeed:
    """Authority-projected correlated identity domain for one model action.

    Seeds contain no language interpretation and grant no authority. They are direct
    projections of identities already owned by AcceptedTurnContract/UOL/Evidence/
    ResearchTask/Hypothesis/SemanticHandle runtime owners. ManagerActionAvailability
    decides whether the action is currently advertisable and mints the versioned
    model-facing scope.
    """

    action: str
    parent_obligation_id: str | None = None
    directive_id: str | None = None
    hypothesis_ref: str | None = None
    task_id: str | None = None
    capability_key: str | None = None
    obligation_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    handle_refs: tuple[str, ...] = ()
    task_kinds: tuple[str, ...] = ()
    metric_handles: tuple[str, ...] = ()
    dimension_handles: tuple[str, ...] = ()
    filter_handles: tuple[str, ...] = ()
    period_handles: tuple[str, ...] = ()
    comparison_handles: tuple[str, ...] = ()
    focus_handles: tuple[str, ...] = ()
    counterpart_handles: tuple[str, ...] = ()
    ranking_direction: str | None = None
    ranking_limit: int | None = None
    reason_codes: tuple[str, ...] = ()

    def payload(self) -> dict[str, object]:
        return {
            "action": self.action,
            "parent_obligation_id": self.parent_obligation_id,
            "directive_id": self.directive_id,
            "hypothesis_ref": self.hypothesis_ref,
            "task_id": self.task_id,
            "capability_key": self.capability_key,
            "obligation_ids": list(self.obligation_ids),
            "evidence_refs": list(self.evidence_refs),
            "handle_refs": list(self.handle_refs),
            "task_kinds": list(self.task_kinds),
            "metric_handles": list(self.metric_handles),
            "dimension_handles": list(self.dimension_handles),
            "filter_handles": list(self.filter_handles),
            "period_handles": list(self.period_handles),
            "comparison_handles": list(self.comparison_handles),
            "focus_handles": list(self.focus_handles),
            "counterpart_handles": list(self.counterpart_handles),
            "ranking_direction": self.ranking_direction,
            "ranking_limit": self.ranking_limit,
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class ActionApplicabilityScope:
    """One server-minted correlated model-facing applicability scope."""

    scope_ref: str
    state_version: str
    action: str
    parent_obligation_id: str | None = None
    directive_id: str | None = None
    hypothesis_ref: str | None = None
    task_id: str | None = None
    capability_key: str | None = None
    obligation_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    handle_refs: tuple[str, ...] = ()
    task_kinds: tuple[str, ...] = ()
    metric_handles: tuple[str, ...] = ()
    dimension_handles: tuple[str, ...] = ()
    filter_handles: tuple[str, ...] = ()
    period_handles: tuple[str, ...] = ()
    comparison_handles: tuple[str, ...] = ()
    focus_handles: tuple[str, ...] = ()
    counterpart_handles: tuple[str, ...] = ()
    ranking_direction: str | None = None
    ranking_limit: int | None = None
    reason_codes: tuple[str, ...] = ()

    def model_view(self) -> dict[str, object]:
        return {
            "scope_ref": self.scope_ref,
            "action": self.action,
            "state_version": self.state_version,
            "parent_obligation_id": self.parent_obligation_id,
            "directive_id": self.directive_id,
            "hypothesis_ref": self.hypothesis_ref,
            "task_id": self.task_id,
            "capability_key": self.capability_key,
            "obligation_ids": list(self.obligation_ids),
            "eligible_evidence_refs": list(self.evidence_refs),
            "eligible_handle_refs": list(self.handle_refs),
            "eligible_task_kinds": list(self.task_kinds),
            "metric_handles": list(self.metric_handles),
            "dimension_handles": list(self.dimension_handles),
            "filter_handles": list(self.filter_handles),
            "period_handles": list(self.period_handles),
            "comparison_handles": list(self.comparison_handles),
            "focus_handles": list(self.focus_handles),
            "counterpart_handles": list(self.counterpart_handles),
            "ranking_direction": self.ranking_direction,
            "ranking_limit": self.ranking_limit,
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class ActionApplicabilitySnapshot:
    """Versioned VIEW over current applicability; never a semantic authority."""

    snapshot_ref: str
    state_version: str
    scopes: tuple[ActionApplicabilityScope, ...]

    def scope(self, scope_ref: str) -> ActionApplicabilityScope:
        matches = tuple(item for item in self.scopes if item.scope_ref == scope_ref)
        if len(matches) != 1:
            raise KeyError(f"unknown applicability scope: {scope_ref}")
        return matches[0]

    def scopes_for(self, action: str) -> tuple[ActionApplicabilityScope, ...]:
        return tuple(item for item in self.scopes if item.action == action)

    def model_view(self) -> dict[str, object]:
        return {
            "snapshot_ref": self.snapshot_ref,
            "state_version": self.state_version,
            "scopes": [item.model_view() for item in self.scopes],
        }


def _scope_from_seed(
    *,
    state_version: str,
    seed: ActionScopeSeed,
) -> ActionApplicabilityScope:
    canonical = json.dumps(
        {
            "state_version": state_version,
            **seed.payload(),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    scope_ref = "aps_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
    return ActionApplicabilityScope(
        scope_ref=scope_ref,
        state_version=state_version,
        action=seed.action,
        parent_obligation_id=seed.parent_obligation_id,
        directive_id=seed.directive_id,
        hypothesis_ref=seed.hypothesis_ref,
        task_id=seed.task_id,
        capability_key=seed.capability_key,
        obligation_ids=tuple(dict.fromkeys(seed.obligation_ids)),
        evidence_refs=tuple(dict.fromkeys(seed.evidence_refs)),
        handle_refs=tuple(dict.fromkeys(seed.handle_refs)),
        task_kinds=tuple(dict.fromkeys(seed.task_kinds)),
        metric_handles=tuple(dict.fromkeys(seed.metric_handles)),
        dimension_handles=tuple(dict.fromkeys(seed.dimension_handles)),
        filter_handles=tuple(dict.fromkeys(seed.filter_handles)),
        period_handles=tuple(dict.fromkeys(seed.period_handles)),
        comparison_handles=tuple(dict.fromkeys(seed.comparison_handles)),
        focus_handles=tuple(dict.fromkeys(seed.focus_handles)),
        counterpart_handles=tuple(dict.fromkeys(seed.counterpart_handles)),
        ranking_direction=seed.ranking_direction,
        ranking_limit=seed.ranking_limit,
        reason_codes=tuple(dict.fromkeys(seed.reason_codes)),
    )


def _snapshot(
    *,
    state_version: str,
    seeds: tuple[ActionScopeSeed, ...],
) -> ActionApplicabilitySnapshot:
    scopes = tuple(
        _scope_from_seed(state_version=state_version, seed=seed)
        for seed in seeds
    )
    canonical = json.dumps(
        {
            "state_version": state_version,
            "scope_refs": [item.scope_ref for item in scopes],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    snapshot_ref = (
        "apsnap_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
    )
    return ActionApplicabilitySnapshot(
        snapshot_ref=snapshot_ref,
        state_version=state_version,
        scopes=scopes,
    )


@dataclass(frozen=True)
class ManagerActionAvailabilityContext:
    root_states: tuple[RootActionState, ...] = ()
    state_version: str | None = None
    scope_seeds: tuple[ActionScopeSeed, ...] = ()
    inspectable_old_evidence_refs: tuple[str, ...] = ()
    effective_inspected_verified_evidence_refs: tuple[str, ...] = ()
    fresh_disclosed_evidence_ref: str | None = None
    fresh_disclosed_verified: bool = False
    open_adaptive_directive_count: int = 0
    open_adaptive_parent_obligation_ids: tuple[str, ...] = ()
    adaptive_disposition_states: tuple[AdaptiveDirectiveDispositionState, ...] = ()
    evidence_grounded_parent_obligation_ids: tuple[str, ...] = ()
    remaining_research_turns: int = 0


@dataclass(frozen=True)
class ManagerActionAvailabilityProfile:
    available_actions: tuple[str, ...]
    unavailable_actions: tuple[tuple[str, tuple[str, ...]], ...]
    available_reasons: tuple[tuple[str, tuple[str, ...]], ...]
    inspectable_evidence_refs: tuple[str, ...]
    inspection_required_for_current_delta: bool
    remaining_research_turns: int
    resolve_semantics_parent_obligation_ids: tuple[str, ...]
    root_parent_obligation_ids: tuple[str, ...]
    root_action_handle_refs: tuple[str, ...]
    root_evidence_refs: tuple[str, ...]
    hypothesis_refs: tuple[str, ...]
    pending_relation_hypothesis_refs: tuple[str, ...]
    pending_relation_evidence_refs: tuple[str, ...]
    directive_disposition_id: str | None = None
    directive_disposition_parent_obligation_id: str | None = None
    directive_disposition_evidence_refs: tuple[str, ...] = ()
    post_acceptance_resolve_provenance: tuple[str, ...] = ("AGENT_DERIVED",)
    applicability_snapshot: ActionApplicabilitySnapshot | None = None

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
            "resolve_semantics_parent_obligation_ids": list(
                self.resolve_semantics_parent_obligation_ids
            ),
            "root_parent_obligation_ids": list(self.root_parent_obligation_ids),
            "root_action_handle_refs": list(self.root_action_handle_refs),
            "root_evidence_refs": list(self.root_evidence_refs),
            "hypothesis_refs": list(self.hypothesis_refs),
            "pending_relation_hypothesis_refs": list(
                self.pending_relation_hypothesis_refs
            ),
            "pending_relation_evidence_refs": list(
                self.pending_relation_evidence_refs
            ),
            "directive_disposition_target": (
                {
                    "directive_id": self.directive_disposition_id,
                    "parent_obligation_id": (
                        self.directive_disposition_parent_obligation_id
                    ),
                    "eligible_evidence_refs": list(
                        self.directive_disposition_evidence_refs
                    ),
                }
                if self.directive_disposition_id is not None
                else None
            ),
            "remaining_research_turns": self.remaining_research_turns,
            "applicability_snapshot": (
                None
                if self.applicability_snapshot is None
                else self.applicability_snapshot.model_view()
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

        actionable_dispositions = tuple(
            item
            for item in context.adaptive_disposition_states
            if item.eligible_evidence_refs
        )
        selected_disposition = (
            actionable_dispositions[0] if actionable_dispositions else None
        )
        if context.open_adaptive_directive_count <= 0:
            remove(
                "disposition_research_directive",
                ActionAvailabilityReason.NO_OPEN_ADAPTIVE_DIRECTIVE,
            )
        elif selected_disposition is None:
            remove(
                "disposition_research_directive",
                ActionAvailabilityReason.NO_ELIGIBLE_ADAPTIVE_DIRECTIVE_EVIDENCE,
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
        # AGENT_DERIVED availability is parent-scoped and policy-owned here:
        # - an active ROOT parent is eligible only while governed handles cannot satisfy
        #   any material next-test contract;
        # - a non-root parent is eligible only when accepted authority still has an OPEN
        #   ADAPT_ON_EVIDENCE directive for that parent and current VERIFIED Evidence
        #   belongs to that lineage.
        # A server-owned derived ResearchTask obligation is therefore never promoted to
        # semantic authority merely because it produced Evidence.
        grounded_parent_ids = frozenset(
            context.evidence_grounded_parent_obligation_ids
        )
        open_adaptive_parent_ids = frozenset(
            context.open_adaptive_parent_obligation_ids
        )
        semantic_parent_rows: list[str] = []
        feasible_root_ids = {
            root.root_id for root in roots if root.feasible_next_test
        }
        for root in roots:
            if root.evidence_ready and not root.feasible_next_test:
                semantic_parent_rows.append(root.root_id)
        semantic_parent_rows.extend(
            parent_id
            for parent_id in context.open_adaptive_parent_obligation_ids
            if (
                parent_id in grounded_parent_ids
                and parent_id not in feasible_root_ids
            )
        )
        semantic_parents = tuple(dict.fromkeys(semantic_parent_rows))

        if not effective_evidence:
            remove(
                "resolve_semantics",
                ActionAvailabilityReason.NO_INSPECTED_VERIFIED_EVIDENCE,
            )
        elif not semantic_parents:
            remove(
                "resolve_semantics",
                ActionAvailabilityReason.EXISTING_GOVERNED_HANDLES_SATISFY_NEXT_TEST,
            )
        else:
            reason(
                "resolve_semantics",
                ActionAvailabilityReason.DERIVED_SEMANTIC_EXPANSION_POTENTIALLY_REQUIRED,
            )

        root_parent_ids = tuple(root.root_id for root in roots)
        root_action_handles = tuple(
            dict.fromkeys(
                handle_ref
                for root in roots
                for handle_ref in root.root_handle_refs
            )
        )
        root_evidence_refs = tuple(
            dict.fromkeys(
                evidence_ref
                for root in roots
                for evidence_ref in root.effective_inspected_verified_evidence_refs
            )
        )
        hypothesis_refs = tuple(
            dict.fromkeys(
                hypothesis_ref
                for root in roots
                for hypothesis_ref in root.hypothesis_refs
            )
        )
        pending_relation_hypothesis_refs = tuple(
            dict.fromkeys(
                hypothesis_ref
                for root in roots
                for hypothesis_ref in root.pending_relation_hypothesis_refs
            )
        )
        pending_relation_evidence_refs = tuple(
            dict.fromkeys(
                evidence_ref
                for root in roots
                for evidence_ref in root.pending_relation_evidence_refs
            )
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
            elif context.remaining_research_turns < 1:
                remove(
                    "propose_hypothesis_with_next_test",
                    ActionAvailabilityReason.INSUFFICIENT_HEADROOM_FOR_COMPOSITE,
                )
            else:
                reason(
                    "propose_hypothesis_with_next_test",
                    ActionAvailabilityReason.ROOT_EVIDENCE_AND_EXISTING_HANDLES_READY,
                )
                # Separate hypothesis + next-test + relation needs two future turns
                # after this cognition turn. When only one remains, the existing
                # composite proposal is the only bounded architecture that can still
                # reach Evidence relation without raising the frozen Manager ceiling.
                if (
                    context.remaining_research_turns < 2
                    and "propose_hypothesis" in allowed
                ):
                    remove(
                        "propose_hypothesis",
                        ActionAvailabilityReason.INSUFFICIENT_HEADROOM_FOR_SEPARATE_HYPOTHESIS,
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
            elif pending_relation_evidence_refs:
                # A completed governed next-test has produced VERIFIED Evidence that has
                # not yet been admitted into hypothesis state. Account that epistemic
                # relation before advertising another next-test; otherwise the next
                # proposal's trigger is structurally unrelated by existing authority.
                remove(
                    "propose_hypothesis_next_test",
                    ActionAvailabilityReason.POST_TEST_EVIDENCE_RELATION_PENDING,
                )

        inspection_required = not (
            context.fresh_disclosed_evidence_ref is not None
            and context.fresh_disclosed_verified
        )

        applicability_snapshot = None
        if context.state_version is not None:
            candidate_seeds = tuple(
                seed
                for seed in context.scope_seeds
                if seed.action in allowed
            )
            scoped_actions = {seed.action for seed in candidate_seeds}
            for action in tuple(allowed):
                if action not in scoped_actions:
                    remove(action, ActionAvailabilityReason.NO_APPLICABLE_SCOPE)
            candidate_seeds = tuple(
                seed
                for seed in candidate_seeds
                if seed.action in allowed
            )
            applicability_snapshot = _snapshot(
                state_version=context.state_version,
                seeds=candidate_seeds,
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
            remaining_research_turns=context.remaining_research_turns,
            resolve_semantics_parent_obligation_ids=semantic_parents,
            root_parent_obligation_ids=root_parent_ids,
            root_action_handle_refs=root_action_handles,
            root_evidence_refs=root_evidence_refs,
            hypothesis_refs=hypothesis_refs,
            pending_relation_hypothesis_refs=pending_relation_hypothesis_refs,
            pending_relation_evidence_refs=pending_relation_evidence_refs,
            directive_disposition_id=(
                selected_disposition.directive_id
                if selected_disposition is not None
                else None
            ),
            directive_disposition_parent_obligation_id=(
                selected_disposition.parent_obligation_id
                if selected_disposition is not None
                else None
            ),
            directive_disposition_evidence_refs=(
                tuple(dict.fromkeys(selected_disposition.eligible_evidence_refs))
                if selected_disposition is not None
                else ()
            ),
            applicability_snapshot=applicability_snapshot,
        )
