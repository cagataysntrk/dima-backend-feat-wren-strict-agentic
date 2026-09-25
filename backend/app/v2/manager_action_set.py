"""Canonical post-acceptance executable action projection.

D10-U control-plane compression:

authoritative Product facts -> ONE ManagerActionSet -> provider choice -> deterministic
hydration -> existing runtime authority.

This module is deliberately language-blind and non-authoritative for semantic, Evidence,
epistemic, join, task, or completion truth. It only projects executable action instances
from facts already owned by those authorities.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.v2.manager_models import ManagerCapabilityKey
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityRegistry,
)


@dataclass(frozen=True)
class SemanticActionRef:
    ref: str
    kind: str


@dataclass(frozen=True)
class NextTestContractState:
    task_kind: str
    capability_key: str
    required_kinds: tuple[str, ...]
    allowed_kinds: tuple[str, ...]
    required_params: tuple[str, ...] = ()


@dataclass(frozen=True)
class HypothesisActionState:
    hypothesis_ref: str
    semantic_refs: tuple[SemanticActionRef, ...]
    admissible_evidence_refs: tuple[str, ...]
    pending_relation_evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class RootActionState:
    root_id: str
    semantic_refs: tuple[SemanticActionRef, ...]
    evidence_refs: tuple[str, ...]
    hypotheses: tuple[HypothesisActionState, ...]
    next_test_contracts: tuple[NextTestContractState, ...]


@dataclass(frozen=True)
class DirectiveActionState:
    directive_id: str
    parent_obligation_id: str
    eligible_evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ParentEvidenceActionState:
    parent_obligation_id: str
    capability_key: str
    evidence_ref: str
    semantic_refs: tuple[SemanticActionRef, ...]
    branch_eligible: bool = True


@dataclass(frozen=True)
class InspectableEvidenceState:
    evidence_ref: str
    capability_keys: tuple[str, ...] = ()
    evidence_kind: str | None = None
    lifecycle_relevance: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaskActionState:
    task_id: str
    question_id: str
    task_kind: str
    capability_key: str
    origin: str
    semantic_refs: tuple[SemanticActionRef, ...]
    parent_obligation_id: str | None = None
    trigger_evidence_ref: str | None = None
    ranking_direction: str | None = None
    ranking_limit: int | None = None


@dataclass(frozen=True)
class ManagerActionSetContext:
    state_version: str
    root_states: tuple[RootActionState, ...] = ()
    directive_states: tuple[DirectiveActionState, ...] = ()
    parent_evidence_states: tuple[ParentEvidenceActionState, ...] = ()
    ready_tasks: tuple[TaskActionState, ...] = ()
    inspectable_evidence: tuple[InspectableEvidenceState, ...] = ()
    fresh_disclosed_evidence_ref: str | None = None
    fresh_disclosed_verified: bool = False
    remaining_research_turns: int = 0
    clarification_obligation_ids: tuple[str, ...] = ()
    clarification_grounded: bool = False


@dataclass(frozen=True)
class ActionInstance:
    action_ref: str
    action_kind: str
    state_version: str
    bindings: tuple[tuple[str, Any], ...]
    cognitive_schema: tuple[tuple[str, dict[str, Any]], ...] = ()
    reason_codes: tuple[str, ...] = ()
    cognitive_context: tuple[tuple[str, Any], ...] = ()

    def binding(self, name: str, default: Any = None) -> Any:
        return dict(self.bindings).get(name, default)

    def context(self, name: str, default: Any = None) -> Any:
        return dict(self.cognitive_context).get(name, default)

    @property
    def cognitive_fields(self) -> tuple[str, ...]:
        return tuple(name for name, _schema in self.cognitive_schema)

    def provider_variant(self) -> dict[str, Any]:
        properties: dict[str, Any] = {
            "action_ref": {
                "type": "string",
                "enum": [self.action_ref],
            }
        }
        for name, schema in self.cognitive_schema:
            properties[name] = copy.deepcopy(schema)
        return {
            "type": "object",
            "properties": properties,
            "required": list(properties.keys()),
            "additionalProperties": False,
        }

    def model_card(self) -> dict[str, Any]:
        return {
            "action_ref": self.action_ref,
            "action": self.action_kind,
            "cognitive_fields": list(self.cognitive_fields),
            "reason_codes": list(self.reason_codes),
            "context": dict(self.cognitive_context),
        }


@dataclass(frozen=True)
class ManagerActionSet:
    state_version: str
    action_instances: tuple[ActionInstance, ...]

    def by_ref(self, action_ref: str) -> ActionInstance:
        matches = [
            item for item in self.action_instances if item.action_ref == action_ref
        ]
        if len(matches) != 1:
            raise KeyError(f"unknown ManagerActionSet action_ref: {action_ref}")
        return matches[0]

    @property
    def available_actions(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(item.action_kind for item in self.action_instances)
        )

    def model_view(self) -> dict[str, Any]:
        return {
            "state_version": self.state_version,
            "action_instances": [
                item.model_card() for item in self.action_instances
            ],
        }

    def provider_schema(self) -> dict[str, Any]:
        variants = [item.provider_variant() for item in self.action_instances]
        if not variants:
            raise RuntimeError("ManagerActionSet has no executable action instances")
        return {
            "type": "object",
            "properties": {
                "choice": {
                    "anyOf": variants,
                }
            },
            "required": ["choice"],
            "additionalProperties": False,
        }

    def resolve_choice(self, raw: Any) -> tuple[ActionInstance, dict[str, Any]]:
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict) or set(data) != {"choice"}:
            raise ValueError("Manager action output must contain exactly one choice")
        choice = data["choice"]
        if not isinstance(choice, dict):
            raise ValueError("Manager action choice must be an object")
        action_ref = choice.get("action_ref")
        if not isinstance(action_ref, str):
            raise ValueError("Manager action choice requires action_ref")
        instance = self.by_ref(action_ref)
        expected = {"action_ref", *instance.cognitive_fields}
        if set(choice) != expected:
            raise ValueError(
                "Manager action cognitive payload does not match selected action_ref"
            )
        payload = {key: value for key, value in choice.items() if key != "action_ref"}
        return instance, payload


_STRING_REASON = {
    "type": "string",
    "minLength": 1,
    "maxLength": 500,
}
_HYPOTHESIS_STATEMENT = {
    "type": "string",
    "minLength": 1,
    "maxLength": 1000,
}
_LIMITATIONS = {
    "type": "array",
    "items": {"type": "string"},
}
_TARGET_KIND = {
    "type": "string",
    "enum": ["metric", "dimension", "filter", "time", "comparison", "unknown"],
}
_RELATION = {
    "type": "string",
    "enum": ["SUPPORTS", "CONTRADICTS"],
}
_RANKING_DIRECTION = {
    "anyOf": [
        {"type": "string", "enum": ["asc", "desc"]},
        {"type": "null"},
    ]
}
_RANKING_LIMIT = {
    "anyOf": [
        {"type": "integer", "minimum": 1, "maximum": 1000},
        {"type": "null"},
    ]
}


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _digest(value: Any) -> str:
    blob = json.dumps(
        _plain(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _group_refs(refs: tuple[SemanticActionRef, ...]) -> dict[str, tuple[str, ...]]:
    rows: dict[str, list[str]] = {}
    for item in refs:
        rows.setdefault(str(item.kind), []).append(str(item.ref))
    return {
        kind: tuple(dict.fromkeys(values))
        for kind, values in rows.items()
    }


def _contract_handles(
    refs: tuple[SemanticActionRef, ...],
    contract: NextTestContractState,
) -> tuple[str, ...] | None:
    by_kind = _group_refs(refs)
    if not set(contract.required_kinds).issubset(by_kind):
        return None
    allowed = set(contract.allowed_kinds)
    selected = tuple(
        item.ref
        for item in refs
        if item.kind in allowed
    )
    return tuple(dict.fromkeys(selected)) or None


def _instance(
    *,
    state_version: str,
    action_kind: str,
    bindings: dict[str, Any] | None = None,
    cognitive_schema: dict[str, dict[str, Any]] | None = None,
    reason_codes: tuple[str, ...] = (),
    cognitive_context: dict[str, Any] | None = None,
) -> ActionInstance:
    bindings = bindings or {}
    cognitive_schema = cognitive_schema or {}
    cognitive_context = cognitive_context or {}
    identity = {
        "state_version": state_version,
        "action_kind": action_kind,
        "bindings": bindings,
        "cognitive_fields": sorted(cognitive_schema),
        "cognitive_context": cognitive_context,
    }
    action_ref = "act_" + _digest(identity)[:20]
    return ActionInstance(
        action_ref=action_ref,
        action_kind=action_kind,
        state_version=state_version,
        bindings=tuple(sorted(bindings.items())),
        cognitive_schema=tuple(
            (name, copy.deepcopy(schema))
            for name, schema in sorted(cognitive_schema.items())
        ),
        reason_codes=reason_codes,
        cognitive_context=tuple(sorted(cognitive_context.items())),
    )


def _branch_capabilities(
    semantic_refs: tuple[SemanticActionRef, ...],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    by_kind = _group_refs(semantic_refs)
    registry = ManagerCapabilityRegistry()
    rows: list[tuple[str, tuple[str, ...]]] = []
    for key in ManagerCapabilityKey:
        spec = registry.get(key)
        if spec.execution_mode != ManagerCapabilityExecutionMode.DIRECT:
            continue
        if key in {
            ManagerCapabilityKey.REPORT,
            ManagerCapabilityKey.TABLE,
            ManagerCapabilityKey.CHART,
            ManagerCapabilityKey.EXPLAIN,
        }:
            continue
        if not set(spec.required_kinds).issubset(by_kind):
            continue
        selected = tuple(
            item.ref for item in semantic_refs if item.kind in spec.allowed_kinds
        )
        if not selected:
            continue
        rows.append((key.value, tuple(dict.fromkeys(selected))))
    return tuple(rows)


class ManagerActionSetBuilder:
    """Single pure owner for post-acceptance executable action projection."""

    @classmethod
    def build(cls, context: ManagerActionSetContext) -> ManagerActionSet:
        instances: list[ActionInstance] = []
        state_version = str(context.state_version)

        root_by_id = {item.root_id: item for item in context.root_states}
        feasible_root_ids: set[str] = set()

        # ROOT cognition: identities are server-bound; model owns only hypothesis text,
        # epistemic relation, material reason, and genuinely cognitive operation params.
        for root in context.root_states:
            root_contracts: list[tuple[NextTestContractState, tuple[str, ...]]] = []
            for contract in root.next_test_contracts:
                handles = _contract_handles(root.semantic_refs, contract)
                if handles is not None:
                    root_contracts.append((contract, handles))
            if root_contracts:
                feasible_root_ids.add(root.root_id)

            if not root.hypotheses and root.evidence_refs:
                if root_contracts and context.remaining_research_turns >= 1:
                    for evidence_ref in root.evidence_refs:
                        for contract, handles in root_contracts:
                            instances.append(
                                _instance(
                                    state_version=state_version,
                                    action_kind="propose_hypothesis_with_next_test",
                                    bindings={
                                        "parent_obligation_id": root.root_id,
                                        "semantic_handles": handles,
                                        "trigger_evidence_ref": evidence_ref,
                                        "next_test_task_kind": contract.task_kind,
                                        "next_test_input_handles": handles,
                                    },
                                    cognitive_schema={
                                        "hypothesis_statement": _HYPOTHESIS_STATEMENT,
                                        "hypothesis_limitations": _LIMITATIONS,
                                        "next_test_material_reason": _STRING_REASON,
                                        "next_test_ranking_direction": _RANKING_DIRECTION,
                                        "next_test_ranking_limit": _RANKING_LIMIT,
                                    },
                                    reason_codes=("ROOT_COMPOSITE_EXECUTABLE",),
                                    cognitive_context={
                                        "task_family": contract.task_kind,
                                        "required_semantic_kinds": list(
                                            contract.required_kinds
                                        ),
                                    },
                                )
                            )

                # Separate hypothesis remains useful only if bounded headroom can still
                # reach a next test + relation, or no composite path exists.
                if (
                    context.remaining_research_turns >= 2
                    or not root_contracts
                ):
                    for evidence_ref in root.evidence_refs:
                        instances.append(
                            _instance(
                                state_version=state_version,
                                action_kind="propose_hypothesis",
                                bindings={
                                    "parent_obligation_id": root.root_id,
                                    "semantic_handles": tuple(
                                        item.ref for item in root.semantic_refs
                                    ),
                                    "trigger_evidence_ref": evidence_ref,
                                },
                                cognitive_schema={
                                    "hypothesis_statement": _HYPOTHESIS_STATEMENT,
                                    "hypothesis_limitations": _LIMITATIONS,
                                },
                                reason_codes=("ROOT_HYPOTHESIS_EXECUTABLE",),
                            )
                        )

            for hypothesis in root.hypotheses:
                if hypothesis.pending_relation_evidence_refs:
                    for evidence_ref in hypothesis.pending_relation_evidence_refs:
                        instances.append(
                            _instance(
                                state_version=state_version,
                                action_kind="propose_hypothesis_evidence_relation",
                                bindings={
                                    "hypothesis_ref": hypothesis.hypothesis_ref,
                                    "evidence_ref": evidence_ref,
                                },
                                cognitive_schema={
                                    "hypothesis_relation": _RELATION,
                                },
                                reason_codes=("POST_TEST_EVIDENCE_RELATION_PENDING",),
                            )
                        )
                    continue

                if context.remaining_research_turns <= 0:
                    continue
                for contract in root.next_test_contracts:
                    handles = _contract_handles(
                        hypothesis.semantic_refs,
                        contract,
                    )
                    if handles is None:
                        continue
                    for evidence_ref in hypothesis.admissible_evidence_refs:
                        instances.append(
                            _instance(
                                state_version=state_version,
                                action_kind="propose_hypothesis_next_test",
                                bindings={
                                    "hypothesis_ref": hypothesis.hypothesis_ref,
                                    "next_test_task_kind": contract.task_kind,
                                    "next_test_input_handles": handles,
                                    "trigger_evidence_ref": evidence_ref,
                                },
                                cognitive_schema={
                                    "next_test_material_reason": _STRING_REASON,
                                    "next_test_ranking_direction": _RANKING_DIRECTION,
                                    "next_test_ranking_limit": _RANKING_LIMIT,
                                },
                                reason_codes=("ROOT_NEXT_TEST_EXECUTABLE",),
                                cognitive_context={
                                    "task_family": contract.task_kind,
                                    "required_semantic_kinds": list(
                                        contract.required_kinds
                                    ),
                                },
                            )
                        )

        # Conditional directives are independent concrete action instances. No
        # directive/evidence Cartesian product reaches cognition.
        for directive in context.directive_states:
            for evidence_ref in directive.eligible_evidence_refs:
                instances.append(
                    _instance(
                        state_version=state_version,
                        action_kind="disposition_research_directive",
                        bindings={
                            "directive_id": directive.directive_id,
                            "parent_obligation_id": directive.parent_obligation_id,
                            "evidence_ref": evidence_ref,
                        },
                        cognitive_schema={
                            "directive_reason": _STRING_REASON,
                        },
                        reason_codes=("ADAPTIVE_DIRECTIVE_EVIDENCE_ACCOUNTABLE",),
                    )
                )

        # Parent/Evidence facts are already lineage-validated authority projections.
        # Resolve semantics only when an active parent still lacks an executable shape.
        directive_parents = {
            item.parent_obligation_id for item in context.directive_states
        }
        for parent in context.parent_evidence_states:
            root = root_by_id.get(parent.parent_obligation_id)
            needs_semantics = (
                root is not None
                and parent.parent_obligation_id not in feasible_root_ids
            ) or (
                parent.parent_obligation_id in directive_parents
                and parent.parent_obligation_id not in feasible_root_ids
            )
            if needs_semantics:
                instances.append(
                    _instance(
                        state_version=state_version,
                        action_kind="resolve_semantics",
                        bindings={
                            "parent_obligation_id": parent.parent_obligation_id,
                            "evidence_ref": parent.evidence_ref,
                        },
                        cognitive_schema={
                            "semantic_proposal": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 240,
                            },
                            "target_kind_hint": _TARGET_KIND,
                        },
                        reason_codes=("DERIVED_SEMANTIC_EXPANSION_EXECUTABLE",),
                        cognitive_context={
                            "parent_capability": parent.capability_key,
                        },
                    )
                )

            # Branch proposal is a bounded cognition choice over capabilities only.
            # Parent/Evidence/handles remain server-bound.
            branches = (
                _branch_capabilities(parent.semantic_refs)
                if parent.branch_eligible
                else ()
            )
            if branches:
                branch_caps = [capability for capability, _handles in branches]
                instances.append(
                    _instance(
                        state_version=state_version,
                        action_kind="propose_branches",
                        bindings={
                            "parent_obligation_id": parent.parent_obligation_id,
                            "evidence_ref": parent.evidence_ref,
                            "branch_handles_by_capability": branches,
                        },
                        cognitive_schema={
                            "branch_candidates": {
                                "type": "array",
                                "minItems": 1,
                                "maxItems": min(4, len(branch_caps)),
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "capability_key": {
                                            "type": "string",
                                            "enum": branch_caps,
                                        },
                                        "material_reason": copy.deepcopy(
                                            _STRING_REASON
                                        ),
                                    },
                                    "required": [
                                        "capability_key",
                                        "material_reason",
                                    ],
                                    "additionalProperties": False,
                                },
                            }
                        },
                        reason_codes=("EVIDENCE_GROUNDED_BRANCH_EXECUTABLE",),
                        cognitive_context={
                            "parent_capability": parent.capability_key,
                            "capability_choices": branch_caps,
                        },
                    )
                )

        # Existing pending ResearchTasks become exact executable actions. Model never
        # reconstructs task/parent/Evidence/handle joins.
        registry = ManagerCapabilityRegistry()
        for task in context.ready_tasks:
            try:
                key = ManagerCapabilityKey(task.capability_key)
                spec = registry.get(key)
            except (KeyError, ValueError):
                continue
            by_kind = _group_refs(task.semantic_refs)
            if not set(spec.required_kinds).issubset(by_kind):
                continue
            selected_handles = {
                kind: tuple(
                    item.ref
                    for item in task.semantic_refs
                    if item.kind == kind and kind in spec.allowed_kinds
                )
                for kind in ("metric", "dimension", "filter", "period", "comparison")
            }
            selected_handles = {
                kind: tuple(dict.fromkeys(values))
                for kind, values in selected_handles.items()
                if values
            }

            if key == ManagerCapabilityKey.RELATIONSHIP:
                metrics = selected_handles.get("metric", ())
                dimensions = selected_handles.get("dimension", ())
                if not metrics or len(dimensions) != 1:
                    continue
                instances.append(
                    _instance(
                        state_version=state_version,
                        action_kind="run_relationship",
                        bindings={
                            "obligation_id": (
                                task.parent_obligation_id
                                or task.question_id
                            ),
                            "task_id": task.task_id,
                            "focus_handles": metrics,
                            "counterpart_handles": dimensions,
                        },
                        reason_codes=("READY_RESEARCH_TASK",),
                        cognitive_context={"capability": key.value},
                    )
                )
                continue

            cognitive_schema: dict[str, dict[str, Any]] = {}
            bindings: dict[str, Any] = {
                "obligation_ids": (
                    task.parent_obligation_id or task.question_id,
                ),
                "metric_handles": selected_handles.get("metric", ()),
                "dimension_handles": selected_handles.get("dimension", ()),
                "filter_handles": selected_handles.get("filter", ()),
                "period_handle": (
                    selected_handles.get("period", (None,))[0]
                    if selected_handles.get("period")
                    else None
                ),
                "comparison_handle": (
                    selected_handles.get("comparison", (None,))[0]
                    if selected_handles.get("comparison")
                    else None
                ),
                "derived_task_id": (
                    task.task_id if task.origin == "AGENT_DERIVED" else None
                ),
                "derived_parent_obligation_id": (
                    task.parent_obligation_id
                    if task.origin == "AGENT_DERIVED"
                    else None
                ),
                "derived_capability_key": (
                    key.value if task.origin == "AGENT_DERIVED" else None
                ),
                "derived_evidence_ref": (
                    task.trigger_evidence_ref
                    if task.origin == "AGENT_DERIVED"
                    else None
                ),
                "ranking_direction": task.ranking_direction,
                "ranking_limit": task.ranking_limit,
            }
            if "ranking_direction" in spec.required_params and task.ranking_direction is None:
                cognitive_schema["ranking_direction"] = _RANKING_DIRECTION
                cognitive_schema["ranking_limit"] = _RANKING_LIMIT
            instances.append(
                _instance(
                    state_version=state_version,
                    action_kind="run_analytics",
                    bindings=bindings,
                    cognitive_schema=cognitive_schema,
                    reason_codes=("READY_RESEARCH_TASK",),
                    cognitive_context={
                        "capability": key.value,
                        "task_family": task.task_kind,
                    },
                )
            )

        for evidence in context.inspectable_evidence:
            instances.append(
                _instance(
                    state_version=state_version,
                    action_kind="inspect_evidence",
                    bindings={"evidence_ref": evidence.evidence_ref},
                    reason_codes=("UNDISCLOSED_VERIFIED_EVIDENCE",),
                    cognitive_context={
                        "capabilities": list(evidence.capability_keys),
                        "evidence_kind": evidence.evidence_kind,
                        "lifecycle_relevance": list(evidence.lifecycle_relevance),
                    },
                )
            )

        if context.clarification_grounded:
            instances.append(
                _instance(
                    state_version=state_version,
                    action_kind="request_clarification",
                    bindings={
                        "obligation_ids": context.clarification_obligation_ids,
                    },
                    cognitive_schema={
                        "clarification_reason": _STRING_REASON,
                    },
                    reason_codes=("GOVERNED_CLARIFICATION_AVAILABLE",),
                )
            )

        # finish remains an admissible proposal; CompletionGate remains final authority.
        instances.append(
            _instance(
                state_version=state_version,
                action_kind="finish",
                reason_codes=("COMPLETION_PROPOSAL",),
            )
        )

        # A candidate-order permutation must not change the externally visible set.
        instances = sorted(
            {
                item.action_ref: item
                for item in instances
            }.values(),
            key=lambda item: (item.action_kind, item.action_ref),
        )
        return ManagerActionSet(
            state_version=state_version,
            action_instances=tuple(instances),
        )
