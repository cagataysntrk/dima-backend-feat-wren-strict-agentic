"""Bounded structured-action loop for the Day 6.5 Research Manager.

One model call proposes one next action. Runtime/gates/tools remain authoritative.
No chain-of-thought is requested, persisted or returned.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, model_validator

from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ManagerState,
    ResearchRunTerminal,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    UserIntentEnvelope,
)
from app.v2.manager_policy import ManagerCapabilityRegistry
from app.v2.manager_preacceptance import (
    FiniteAcceptanceStatus,
    PreAcceptanceController,
)
from app.v2.manager_progress import DynamicActionFrontier
from app.v2.manager_runtime import (
    ManagerBudgetError,
    ManagerRuntime,
    ManagerStateError,
)
from app.v2.research_state import ResearchStateView, build_research_state_view
from app.v2.research_tasks import (
    DerivedResearchTaskProposal,
    ResearchTaskMaterializationError,
    ResearchTaskRegistry,
    ResearchTaskService,
)
from app.v2.research_tools import ResearchToolRunner
from app.v2.manager_tools import (
    ManagerToolCall,
    ManagerToolName,
)
from app.v2.models import ConversationStateV2, FrozenModel
from app.v2.source_spans import SourceSpanRegistry


class ManagerActionKind(StrEnum):
    RESOLVE_SEMANTICS = "resolve_semantics"
    PROPOSE_ACCEPTANCE = "propose_acceptance"
    PROPOSE_BRANCHES = "propose_branches"
    RUN_ANALYTICS = "run_analytics"
    RUN_RELATIONSHIP = "run_relationship"
    INSPECT_EVIDENCE = "inspect_evidence"
    REQUEST_CLARIFICATION = "request_clarification"
    FINISH = "finish"


class ManagerObligationProposal(FrozenModel):
    obligation_id: str
    capability_key: ManagerCapabilityKey
    origin: Literal["USER_MUST", "USER_OPTIONAL", "SYSTEM_REQUIRED"]
    priority: ObligationPriority
    polarity: ObligationPolarity
    source_surfaces: tuple[str, ...] = Field(min_length=1)
    semantic_handle_refs: tuple[str, ...] = Field(
        default=(),
        description="Use only runtime-issued h1/h2/... aliases from resolve_semantics.",
    )
    open_questions: tuple[str, ...] = ()
    ranking_direction: Literal["asc", "desc"] | None = Field(
        default=None,
        description="Required only for ranking obligation.",
    )
    ranking_limit: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Required only for ranking obligation.",
    )

    @model_validator(mode="after")
    def _ranking_contract(self):
        if (self.ranking_direction is None) != (self.ranking_limit is None):
            raise ValueError("ranking direction + limit together")
        if (
            self.capability_key == ManagerCapabilityKey.RANKING
            and self.polarity == ObligationPolarity.REQUIRED
        ):
            if self.ranking_direction is None or self.ranking_limit is None:
                raise ValueError("required ranking proposal requires direction + limit")
        elif self.capability_key != ManagerCapabilityKey.RANKING and (
            self.ranking_direction is not None or self.ranking_limit is not None
        ):
            raise ValueError("ranking params only valid for ranking proposal")
        return self


class ManagerBranchCandidateProposal(FrozenModel):
    task_id: str = Field(min_length=1)
    capability_key: ManagerCapabilityKey
    input_handles: tuple[str, ...] = Field(
        min_length=1,
        description="Runtime-issued h* aliases only; no raw sem_* identifiers.",
    )
    material_reason: str = Field(min_length=1, max_length=500)


class ManagerDecisionTransport(FrozenModel):
    action: ManagerActionKind

    resolve_provenance: Literal["USER_SOURCE", "AGENT_DERIVED"] = "USER_SOURCE"
    source_surfaces: tuple[str, ...] = ()
    target_kind_hints: tuple[
        Literal["metric", "dimension", "filter", "time", "comparison", "unknown"], ...
    ] = Field(
        default=(),
        description=(
            "Aligned with source_surfaces. metric/dimension/filter are tenant catalog "
            "concepts; time is a base period phrase; comparison is a reference-period/"
            "comparison phrase. Ranking words/numbers are never semantic hints."
        ),
    )
    temporal_anchor_handle: str | None = Field(
        default=None,
        description="Optional runtime-issued h* alias used only as temporal anchor.",
    )
    base_period_handle: str | None = Field(
        default=None,
        description="Optional runtime-issued h* alias for a resolved base period.",
    )
    semantic_parent_obligation_id: str | None = None
    semantic_evidence_ref: str | None = None
    semantic_proposal: str | None = Field(default=None, max_length=240)

    obligations: tuple[ManagerObligationProposal, ...] = ()

    branch_parent_obligation_id: str | None = None
    branch_evidence_ref: str | None = None
    branch_candidates: tuple[ManagerBranchCandidateProposal, ...] = Field(
        default=(),
        max_length=12,
    )

    obligation_ids: tuple[str, ...] = ()
    metric_handles: tuple[str, ...] = ()
    dimension_handles: tuple[str, ...] = ()
    filter_handles: tuple[str, ...] = ()
    period_handle: str | None = None
    comparison_handle: str | None = None
    ranking_direction: Literal["asc", "desc"] | None = Field(
        default=None,
        description="Operation parameter for ranking; do not resolve ranking wording semantically.",
    )
    limit: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Top/bottom N operation parameter; do not resolve this number as semantics.",
    )
    derived_task_id: str | None = None
    derived_parent_obligation_id: str | None = None
    derived_capability_key: ManagerCapabilityKey | None = None
    derived_evidence_ref: str | None = None
    derived_reason: str | None = Field(default=None, min_length=1, max_length=500)

    relationship_obligation_id: str | None = None
    focus_handles: tuple[str, ...] = ()
    counterpart_handles: tuple[str, ...] = ()

    evidence_ref: str | None = None
    clarification_reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _action_shape(self):
        if self.action == ManagerActionKind.RESOLVE_SEMANTICS:
            if self.resolve_provenance == "USER_SOURCE":
                if not self.source_surfaces:
                    raise ValueError("USER_SOURCE resolve source_surfaces gerektirir")
                if self.target_kind_hints and len(self.target_kind_hints) != len(self.source_surfaces):
                    raise ValueError("semantic hints source_surfaces ile aynı uzunlukta olmalı")
            else:
                if (
                    not self.semantic_parent_obligation_id
                    or not self.semantic_evidence_ref
                    or not self.semantic_proposal
                    or len(self.target_kind_hints) != 1
                ):
                    raise ValueError(
                        "AGENT_DERIVED resolve parent obligation + evidence + proposal + one kind hint gerektirir"
                    )
        elif self.action == ManagerActionKind.PROPOSE_ACCEPTANCE:
            if not self.obligations:
                raise ValueError("propose_acceptance obligations gerektirir")
        elif self.action == ManagerActionKind.PROPOSE_BRANCHES:
            if (
                not self.branch_parent_obligation_id
                or not self.branch_evidence_ref
                or not self.branch_candidates
            ):
                raise ValueError(
                    "propose_branches parent obligation + evidence + candidates gerektirir"
                )
        elif self.action == ManagerActionKind.RUN_ANALYTICS:
            if not self.obligation_ids or not self.metric_handles:
                raise ValueError("run_analytics obligation_ids + metric_handles gerektirir")
        elif self.action == ManagerActionKind.RUN_RELATIONSHIP:
            if (
                not self.relationship_obligation_id
                or not self.focus_handles
                or not self.counterpart_handles
            ):
                raise ValueError("run_relationship obligation/focus/counterpart gerektirir")
        elif self.action == ManagerActionKind.INSPECT_EVIDENCE:
            if not self.evidence_ref:
                raise ValueError("inspect_evidence evidence_ref gerektirir")
        elif self.action == ManagerActionKind.REQUEST_CLARIFICATION:
            if not self.clarification_reason:
                raise ValueError("request_clarification reason gerektirir")

        branch_values = (
            self.branch_parent_obligation_id,
            self.branch_evidence_ref,
            self.branch_candidates,
        )
        if self.action != ManagerActionKind.PROPOSE_BRANCHES and (
            self.branch_parent_obligation_id is not None
            or self.branch_evidence_ref is not None
            or bool(self.branch_candidates)
        ):
            raise ValueError("branch fields are valid only for propose_branches")

        derived_values = (
            self.derived_task_id,
            self.derived_parent_obligation_id,
            self.derived_capability_key,
            self.derived_evidence_ref,
            self.derived_reason,
        )
        if any(value is not None for value in derived_values):
            if self.action != ManagerActionKind.RUN_ANALYTICS:
                raise ValueError("derived task fields are valid only for run_analytics")
            if not all(value is not None for value in derived_values):
                raise ValueError(
                    "derived task id/parent/capability/evidence_ref/reason birlikte verilmelidir"
                )
        return self


@dataclass(frozen=True)
class ManagerLoopOutcome:
    snapshot: Any
    run_finished: bool
    verified_complete: bool
    terminal_status: ResearchRunTerminal | None
    clarification_required: bool
    observations: tuple[dict[str, Any], ...]
    preacceptance_status: FiniteAcceptanceStatus | None = None


def _strict_native_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Pydantic JSON Schema to OpenAI/OpenRouter strict-native rules.

    Strict providers require every object property to appear in `required`. Optional
    semantics are represented by nullable types, not by omitting keys. Defaults are
    application conveniences and are removed from the provider contract.
    """
    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties") or {}
                node["required"] = list(properties.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


def _post_acceptance_native_schema() -> dict[str, Any]:
    """Expose only actions that are legal after AcceptedTurnContract commit.

    Pre-acceptance is owned by PreAcceptanceController.  Leaving
    propose_acceptance in the post-acceptance provider schema creates a deterministic
    dead end: the model can select an action the runtime must reject.  Runtime policy
    remains defense-in-depth; this function narrows only the advertised cognition
    surface.
    """
    schema = _strict_native_schema(ManagerDecisionTransport.model_json_schema())

    def remove_value(node: Any) -> None:
        if isinstance(node, dict):
            enum_values = node.get("enum")
            if isinstance(enum_values, list) and ManagerActionKind.PROPOSE_ACCEPTANCE.value in enum_values:
                node["enum"] = [
                    value
                    for value in enum_values
                    if value != ManagerActionKind.PROPOSE_ACCEPTANCE.value
                ]
            for value in node.values():
                remove_value(value)
        elif isinstance(node, list):
            for value in node:
                remove_value(value)

    remove_value(schema)
    return schema


_SYSTEM = """You are Dima's bounded post-acceptance RESEARCH_MANAGER.

AcceptedTurnContract is already the only semantic authority. Use typed governed tools to
investigate accepted obligations, inspect evidence, open evidence-grounded derived work,
and propose finish. Do not write SQL. Do not invent canonical identifiers or semantic
handles. Capability meanings and semantic shapes come only from CAPABILITY_BINDING_CONTRACT.

Rules:
- Never mutate, reinterpret, drop or replace accepted USER_MUST obligations.
- Research directives are policy/authorization, not user obligations.
- AGENT_DERIVED semantic discovery requires accepted parent + inspected verified evidence.
- Rejected attempts leave no semantic authority to merge.
- run_analytics/run_relationship may reference only accepted/derived obligation IDs.
- Evidence-grounded executable branches MUST first be proposed with propose_branches.
- propose_branches registers bounded typed candidates only; it NEVER executes data work.
- Every derived run_analytics must select a task already listed in READY_RESEARCH_TASKS.
- Every derived branch must cite parent obligation + inspected evidence.
- Use inspect_evidence before result-dependent replanning.
- Follow ACTION_FRONTIER. Never repeat an exact action listed in blocked_exact_actions.
- Semantic ambiguity is Resolver authority; do not guess canonical truth.
- finish is only a proposal; deterministic CompletionGate decides completion truth.
- One action per turn. No prose outside the strict schema.
- Emit every schema field; use []/null for unused fields.
"""


def _conversation_surface_view(
    conversation: ConversationStateV2 | None,
) -> dict[str, Any]:
    """Expose only bounded surface context; canonical IR/anchors never reach Manager."""
    if conversation is None:
        return {
            "has_prior_analytical_request": False,
            "has_active_result": False,
            "pending_clarification": False,
            "topic_labels": [],
            "focus_labels": [],
            "selected_anchor_label": None,
            "pending_source_mention": None,
        }
    clarification = conversation.clarification_state
    return {
        "has_prior_analytical_request": conversation.has_prior_analytical_request,
        "has_active_result": conversation.has_active_result,
        "pending_clarification": conversation.pending_clarification,
        "topic_labels": list(conversation.topic_labels[:8]),
        "focus_labels": list(conversation.focus_labels[:8]),
        "selected_anchor_label": conversation.selected_anchor_label,
        "pending_source_mention": (
            clarification.source_mention if clarification is not None else None
        ),
    }


def _evidence_was_inspected(
    observations: list[dict[str, Any]],
    evidence_ref: str | None,
) -> bool:
    if not evidence_ref:
        return False
    return any(
        observation.get("kind") == "tool"
        and observation.get("tool") == ManagerToolName.INSPECT_EVIDENCE.value
        and (observation.get("result") or {}).get("artifact_id") == evidence_ref
        for observation in observations
    )


def _zero_row_completion_candidate(
    *,
    runtime: ManagerRuntime,
    evidence_store,
    task_registry: ResearchTaskRegistry,
) -> bool:
    """Return True only when another Manager turn cannot open grounded data work.

    A zero-row current result contains no material row-level direction for an
    evidence-grounded branch. If every registered ResearchTask is already terminal,
    CompletionGate is the only remaining authority: the loop may attempt finish
    without spending another probabilistic Manager turn.
    """
    state = build_research_state_view(
        runtime=runtime,
        evidence_store=evidence_store,
    )
    delta = state.latest_delta
    if (
        delta is None
        or delta.availability.value != "AVAILABLE"
        or not delta.inspected
        or delta.row_count != 0
    ):
        return False
    if any(task.state == "pending" for task in task_registry.tasks):
        return False
    return True


def _clarification_has_governed_grounding(
    observations: list[dict[str, Any]],
    *,
    accepted_contract_present: bool,
) -> bool:
    """Clarification must be grounded by deterministic authority, not Manager intuition.

    After acceptance, blockers in the canonical ledger are sufficient grounding. Before
    acceptance, either SemanticResolver or AcceptanceGate must have produced a concrete
    clarification/unresolved state first.
    """
    if accepted_contract_present:
        return True

    for observation in reversed(observations):
        if observation.get("kind") != "tool":
            continue
        tool = observation.get("tool")
        result = observation.get("result") or {}
        if tool == ManagerToolName.RESOLVE_SEMANTICS.value:
            if (
                result.get("clarification")
                or result.get("unresolved_source_refs")
                or result.get("unresolved_proposals")
            ):
                return True
        if tool == ManagerToolName.PROPOSE_ACCEPTANCE.value:
            if result.get("status") == "NEEDS_CLARIFICATION":
                return True
            if result.get("status") == "REJECTED":
                reasons = tuple(str(reason) for reason in (result.get("reasons") or ()))
                if reasons and all(
                    "missing Resolver semantic kinds:" in reason
                    for reason in reasons
                ):
                    return True
    return False


def _safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "__dict__"):
        return {
            key: _safe(item)
            for key, item in vars(value).items()
            if not key.startswith("_") and key not in {"analytics_ir"}
        }
    if isinstance(value, dict):
        return {str(k): _safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


@dataclass(frozen=True)
class ManagerUnderstandingOutcome:
    snapshot: ManagerRunSnapshot
    status: FiniteAcceptanceStatus
    accepted: bool
    clarification_required: bool
    observations: tuple[dict[str, Any], ...]


class ResearchManagerLoop:
    def __init__(
        self,
        *,
        llm,
        source_spans: SourceSpanRegistry,
        research_tool_runner: ResearchToolRunner | None = None,
        research_task_service: ResearchTaskService | None = None,
    ) -> None:
        structured = getattr(llm, "structured_json", None)
        if not callable(structured):
            raise ValueError("RESEARCH_MANAGER provider native structured_json desteklemiyor")
        self._structured = structured
        self._source_spans = source_spans
        self._capabilities = ManagerCapabilityRegistry()
        self._research_tool_runner = research_tool_runner
        self._research_tasks = research_task_service or ResearchTaskService()
        self._alias_by_handle: dict[str, str] = {}
        self._handle_by_alias: dict[str, str] = {}

    def _handle_alias(self, handle_id: str) -> str:
        if not str(handle_id).startswith("sem_"):
            return str(handle_id)
        existing = self._alias_by_handle.get(handle_id)
        if existing is not None:
            return existing
        alias = f"h{len(self._alias_by_handle) + 1}"
        self._alias_by_handle[handle_id] = alias
        self._handle_by_alias[alias] = handle_id
        return alias

    def _manager_safe(self, value: Any) -> Any:
        """Serialize tool/runtime state for the Manager without exposing raw sem_* ids."""
        if hasattr(value, "model_dump"):
            return self._manager_safe(value.model_dump(mode="json"))
        if hasattr(value, "__dict__"):
            return {
                key: self._manager_safe(item)
                for key, item in vars(value).items()
                if not key.startswith("_") and key not in {"analytics_ir"}
            }
        if isinstance(value, dict):
            return {str(k): self._manager_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._manager_safe(item) for item in value]
        if isinstance(value, str) and value.startswith("sem_"):
            return self._handle_alias(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    def _decode_handle(self, ref: str | None) -> str | None:
        if ref is None:
            return None
        raw = str(ref)
        if raw.startswith("sem_"):
            raise ValueError(
                "Manager raw sem_* id kullanamaz; resolve_semantics tarafından verilen h* aliasını kullanın"
            )
        if raw.startswith("h"):
            try:
                return self._handle_by_alias[raw]
            except KeyError as exc:
                raise ValueError(f"unknown/unissued Manager handle alias: {raw}") from exc
        raise ValueError(f"invalid Manager handle reference: {raw}")

    def _decode_handles(self, refs: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(self._decode_handle(ref) for ref in refs)

    def _prompt(
        self,
        *,
        question: str,
        runtime: ManagerRuntime,
        observations: list[dict[str, Any]],
        conversation: ConversationStateV2 | None = None,
        action_frontier: dict[str, Any] | None = None,
        research_state: ResearchStateView | None = None,
        ready_tasks: tuple[Any, ...] = (),
    ) -> str:
        ledger = runtime.ledger
        ledger_view = []
        if ledger is not None:
            ledger_view = [
                {
                    "obligation_id": item.obligation_id,
                    "capability": item.capability_key.value,
                    "origin": item.origin.value,
                    "priority": item.priority.value,
                    "polarity": item.polarity.value,
                    "status": item.status.value,
                    "semantic_handle_refs": [
                        self._handle_alias(handle_id)
                        for handle_id in item.semantic_handle_refs
                    ],
                    "evidence_refs": list(item.evidence_refs),
                    "blocker": item.blocker,
                }
                for item in ledger.items
            ]
        payload = {
            "USER_MESSAGE": question,
            "MANAGER_STATE": runtime.snapshot.state.value,
            "ACCEPTED_CONTRACT_ID": runtime.snapshot.accepted_contract_id,
            "OBLIGATION_LEDGER": ledger_view,
            "EVIDENCE_REFS": list(runtime.snapshot.evidence_refs),
            "CONVERSATION_SURFACE": _conversation_surface_view(conversation),
            "CAPABILITY_BINDING_CONTRACT": self._capabilities.manager_contract(),
            "ACCEPTED_RESEARCH_DIRECTIVES": (
                [
                    item.model_dump(mode="json")
                    for item in runtime.accepted_contract.research_directives
                ]
                if runtime.accepted_contract is not None
                else []
            ),
            "ACTION_FRONTIER": action_frontier or {},
            "READY_RESEARCH_TASKS": [
                {
                    "task_id": task.task_id,
                    "question_id": task.question_id,
                    "task_kind": task.task_kind,
                    "input_refs": [
                        self._handle_alias(handle_id)
                        for handle_id in task.input_refs
                    ],
                    "parent_task_id": task.parent_task_id,
                    "parent_obligation_id": task.parent_obligation_id,
                    "trigger_evidence_ref": task.trigger_evidence_ref,
                    "branch_depth": task.branch_depth,
                }
                for task in ready_tasks
                if task.state == "pending"
            ],
            "ACCUMULATED_RESEARCH_STATE": (
                None
                if research_state is None
                else research_state.model_copy(update={"latest_delta": None}).model_dump(mode="json")
            ),
            "CURRENT_RESULT_DELTA": (
                None
                if research_state is None or research_state.latest_delta is None
                else research_state.latest_delta.model_dump(mode="json")
            ),
            # Diagnostic tail only. It is never the sole Research state authority.
            "RECENT_OBSERVATIONS": observations[-4:],
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _parse_decision(raw: Any) -> ManagerDecisionTransport:
        data = json.loads(raw) if isinstance(raw, str) else raw
        return ManagerDecisionTransport.model_validate(data)

    def _decision(
        self,
        *,
        question: str,
        runtime: ManagerRuntime,
        observations,
        conversation: ConversationStateV2 | None = None,
        action_frontier: dict[str, Any] | None = None,
        research_state: ResearchStateView | None = None,
        ready_tasks: tuple[Any, ...] = (),
    ):
        user = self._prompt(
            question=question,
            runtime=runtime,
            observations=observations,
            conversation=conversation,
            action_frontier=action_frontier,
            research_state=research_state,
            ready_tasks=ready_tasks,
        )
        schema = _post_acceptance_native_schema()
        kwargs = {
            "schema": schema,
            "schema_name": "dima_research_manager_action_v1",
        }
        raw = self._structured(_SYSTEM, user, **kwargs)
        try:
            return self._parse_decision(raw)
        except Exception as first_error:
            repair_system = (
                _SYSTEM
                + "\n\nFORMAT_REPAIR_ONLY: Previous output failed the application schema. "
                  "Keep the SAME next action and semantic decision. Only fill/fix schema "
                  "fields. Do not add/remove obligations, change polarity, or choose another tool."
            )
            repair_user = (
                user
                + "\n\nPREVIOUS_INVALID_OUTPUT:\n"
                + (raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False))
                + "\n\nFORMAT_ERROR:\n"
                + str(first_error)[:1200]
            )
            repaired = self._structured(repair_system, repair_user, **kwargs)
            try:
                return self._parse_decision(repaired)
            except Exception as exc:
                raise RuntimeError(
                    f"RESEARCH_MANAGER structured action invalid after one format retry: {exc}"
                ) from exc

    def _source_refs(self, *, message_id: str, surfaces: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(
            self._source_spans.mint_exact(message_id=message_id, surface=surface).source_ref
            for surface in surfaces
        )

    def _compile_tool(
        self,
        *,
        decision: ManagerDecisionTransport,
        message_id: str,
        source_hash: str,
        request_ref: str,
        runtime: ManagerRuntime,
    ) -> ManagerToolCall | None:
        if decision.action in {
            ManagerActionKind.FINISH,
            ManagerActionKind.PROPOSE_BRANCHES,
        }:
            return None

        if decision.action == ManagerActionKind.RESOLVE_SEMANTICS:
            if decision.resolve_provenance == "USER_SOURCE":
                refs = self._source_refs(
                    message_id=message_id,
                    surfaces=decision.source_surfaces,
                )
                args = {
                    "provenance": "USER_SOURCE",
                    "source_refs": refs,
                    "target_kind_hints": decision.target_kind_hints,
                    "temporal_anchor_handle": self._decode_handle(decision.temporal_anchor_handle),
                    "base_period_handle": self._decode_handle(decision.base_period_handle),
                }
            else:
                args = {
                    "provenance": "AGENT_DERIVED",
                    "source_refs": (),
                    "target_kind_hints": decision.target_kind_hints,
                    "temporal_anchor_handle": self._decode_handle(decision.temporal_anchor_handle),
                    "base_period_handle": self._decode_handle(decision.base_period_handle),
                    "parent_obligation_id": decision.semantic_parent_obligation_id,
                    "evidence_ref": decision.semantic_evidence_ref,
                    "natural_language_proposal": decision.semantic_proposal,
                }
            return ManagerToolCall(
                name=ManagerToolName.RESOLVE_SEMANTICS,
                args=args,
            )

        if decision.action == ManagerActionKind.PROPOSE_ACCEPTANCE:
            obligations = []
            for item in decision.obligations:
                refs = self._source_refs(
                    message_id=message_id,
                    surfaces=item.source_surfaces,
                )
                obligations.append(
                    CandidateObligation(
                        obligation_id=item.obligation_id,
                        capability_key=item.capability_key,
                        origin=ObligationOrigin(item.origin),
                        priority=item.priority,
                        polarity=item.polarity,
                        source_refs=refs,
                        semantic_handle_refs=self._decode_handles(item.semantic_handle_refs),
                        open_questions=item.open_questions,
                        ranking_direction=item.ranking_direction,
                        ranking_limit=item.ranking_limit,
                    )
                )
            envelope = UserIntentEnvelope(
                attempt_id=f"{runtime.snapshot.run_id}:attempt:{runtime.snapshot.manager_turns}",
                turn_id=message_id,
                request_ref=request_ref,
                source_message_hash=source_hash,
                model_role="RESEARCH_MANAGER",
                obligations=tuple(obligations),
            )
            return ManagerToolCall(
                name=ManagerToolName.PROPOSE_ACCEPTANCE,
                args={"envelope": envelope.model_dump(mode="json")},
            )

        if decision.action == ManagerActionKind.RUN_ANALYTICS:
            return ManagerToolCall(
                name=ManagerToolName.RUN_ANALYTICS,
                args={
                    "obligation_ids": decision.obligation_ids,
                    "metric_handles": self._decode_handles(decision.metric_handles),
                    "dimension_handles": self._decode_handles(decision.dimension_handles),
                    "filter_handles": self._decode_handles(decision.filter_handles),
                    "period_handle": self._decode_handle(decision.period_handle),
                    "comparison_handle": self._decode_handle(decision.comparison_handle),
                    "ranking_direction": decision.ranking_direction,
                    "limit": decision.limit,
                    "derived_task_id": decision.derived_task_id,
                    "derived_parent_obligation_id": decision.derived_parent_obligation_id,
                    "derived_capability_key": (
                        decision.derived_capability_key.value
                        if decision.derived_capability_key is not None
                        else None
                    ),
                    "derived_evidence_ref": decision.derived_evidence_ref,
                },
            )

        if decision.action == ManagerActionKind.RUN_RELATIONSHIP:
            return ManagerToolCall(
                name=ManagerToolName.RUN_RELATIONSHIP,
                args={
                    "obligation_id": decision.relationship_obligation_id,
                    "focus_handles": self._decode_handles(decision.focus_handles),
                    "counterpart_handles": self._decode_handles(decision.counterpart_handles),
                },
            )

        if decision.action == ManagerActionKind.INSPECT_EVIDENCE:
            return ManagerToolCall(
                name=ManagerToolName.INSPECT_EVIDENCE,
                args={"evidence_ref": decision.evidence_ref},
            )

        if decision.action == ManagerActionKind.REQUEST_CLARIFICATION:
            return ManagerToolCall(
                name=ManagerToolName.REQUEST_CLARIFICATION,
                args={
                    "obligation_ids": decision.obligation_ids,
                    "reason": decision.clarification_reason,
                },
            )

        raise RuntimeError(f"unsupported Manager action: {decision.action}")

    def understand(
        self,
        *,
        question: str,
        message_id: str,
        request_ref: str,
        runtime: ManagerRuntime,
        executor,
        conversation: ConversationStateV2 | None = None,
    ) -> ManagerUnderstandingOutcome:
        """Finite pre-acceptance boundary; Manager never chooses grounding tools."""

        source_hash = self._source_spans.register_message(
            message_id=message_id,
            text=question,
        )
        if runtime.snapshot.state == ManagerState.INITIAL:
            runtime.begin_understanding()

        controller = PreAcceptanceController(
            structured=self._structured,
            source_spans=self._source_spans,
            capabilities=self._capabilities,
        )
        try:
            outcome = controller.run(
                question=question,
                message_id=message_id,
                request_ref=request_ref,
                source_hash=source_hash,
                runtime=runtime,
                executor=executor,
                conversation=conversation,
            )
        except ManagerBudgetError as exc:
            return ManagerUnderstandingOutcome(
                snapshot=runtime.snapshot,
                status=FiniteAcceptanceStatus.MODEL_FAILURE,
                accepted=False,
                clarification_required=False,
                observations=({"kind": "budget", "message": str(exc)},),
            )

        return ManagerUnderstandingOutcome(
            snapshot=runtime.snapshot,
            status=outcome.status,
            accepted=outcome.accepted,
            clarification_required=outcome.clarification_required,
            observations=outcome.observations,
        )

    def run(
        self,
        *,
        question: str,
        message_id: str,
        request_ref: str,
        runtime: ManagerRuntime,
        executor,
        conversation: ConversationStateV2 | None = None,
    ) -> ManagerLoopOutcome:
        observations: list[dict[str, Any]] = []

        if runtime.accepted_contract is None:
            understanding = self.understand(
                question=question,
                message_id=message_id,
                request_ref=request_ref,
                runtime=runtime,
                executor=executor,
                conversation=conversation,
            )
            observations.extend(understanding.observations)
            if not understanding.accepted:
                return ManagerLoopOutcome(
                    snapshot=runtime.snapshot,
                    run_finished=False,
                    verified_complete=False,
                    terminal_status=runtime.snapshot.terminal_status,
                    clarification_required=understanding.clarification_required,
                    observations=tuple(observations),
                    preacceptance_status=understanding.status,
                )

        source_hash = self._source_spans.register_message(
            message_id=message_id,
            text=question,
        )
        frontier = DynamicActionFrontier()
        task_registry = ResearchTaskRegistry()

        if self._research_tool_runner is not None:
            seed_set = self._research_tasks.seed_initial_user_must(
                runtime=runtime,
                task_registry=task_registry,
                executable_task_kinds=self._research_tool_runner.declared_task_kinds,
            )
            observations.append(
                {
                    "kind": "seed_tasks_registered",
                    "considered_obligation_ids": list(
                        seed_set.considered_obligation_ids
                    ),
                    "ready_task_ids": [
                        task.task_id for task in seed_set.registered_tasks
                    ],
                    "deferred_obligation_ids": list(
                        seed_set.deferred_obligation_ids
                    ),
                    "already_accounted_obligation_ids": list(
                        seed_set.already_accounted_obligation_ids
                    ),
                }
            )

        while runtime.snapshot.state not in {
            ManagerState.COMPLETED,
            ManagerState.FAILED,
            ManagerState.BUDGET_EXHAUSTED,
            ManagerState.NEEDS_CLARIFICATION,
        }:
            try:
                runtime.note_manager_turn(phase="research")
            except ManagerBudgetError as exc:
                observations.append({"kind": "budget", "message": str(exc)})
                break

            frontier_view = frontier.view(runtime)
            research_state = build_research_state_view(
                runtime=runtime,
                evidence_store=getattr(executor, "evidence_store", None),
            )
            try:
                decision = self._decision(
                    question=question,
                    runtime=runtime,
                    observations=observations,
                    conversation=conversation,
                    action_frontier=frontier_view,
                    research_state=research_state,
                    ready_tasks=task_registry.tasks,
                )
            except Exception as exc:
                observations.append({"kind": "model_error", "message": str(exc)})
                break

            progress_before = frontier.progress(runtime)
            if frontier.blocked(progress=progress_before, action=decision):
                observations.append(
                    {
                        "kind": "no_progress_blocked",
                        "action": self._manager_safe(decision),
                        "progress_fingerprint": progress_before,
                    }
                )
                continue

            if (
                decision.action == ManagerActionKind.RESOLVE_SEMANTICS
                and decision.resolve_provenance == "USER_SOURCE"
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": (
                            "post-acceptance USER_SOURCE semantic reparsing is forbidden; "
                            "use accepted authority or AGENT_DERIVED evidence-grounded discovery"
                        ),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "post_acceptance_user_source_reparse"},
                )
                continue

            if (
                decision.action == ManagerActionKind.RESOLVE_SEMANTICS
                and decision.resolve_provenance == "AGENT_DERIVED"
                and decision.semantic_evidence_ref
                not in runtime.snapshot.inspected_evidence_refs
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": (
                            "AGENT_DERIVED semantic discovery requires inspected evidence "
                            "from the current run"
                        ),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "derived_semantic_requires_inspected_evidence"},
                )
                continue

            if (
                decision.action == ManagerActionKind.RUN_ANALYTICS
                and decision.derived_task_id is not None
                and decision.derived_evidence_ref
                not in runtime.snapshot.inspected_evidence_refs
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": (
                            "derived analytics branch requires inspect_evidence on "
                            "derived_evidence_ref first"
                        ),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "derived_run_requires_inspected_evidence"},
                )
                continue

            if (
                decision.action == ManagerActionKind.PROPOSE_BRANCHES
                and decision.branch_evidence_ref
                not in runtime.snapshot.inspected_evidence_refs
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": "branch proposal requires inspected current-run evidence",
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "branch_requires_inspected_evidence"},
                )
                continue

            if (
                decision.action == ManagerActionKind.REQUEST_CLARIFICATION
                and not _clarification_has_governed_grounding(
                    observations,
                    accepted_contract_present=True,
                )
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": "clarification lacks governed grounding",
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "clarification_ungrounded"},
                )
                continue

            if decision.action == ManagerActionKind.PROPOSE_BRANCHES:
                try:
                    evidence = executor.evidence_store.get(
                        decision.branch_evidence_ref
                    )
                    parent_task = task_registry.get(evidence.task_id)
                    proposals = tuple(
                        DerivedResearchTaskProposal(
                            task_id=item.task_id,
                            task_kind=self._research_tasks.task_kind_for_capability(
                                item.capability_key
                            ),
                            parent_task_id=parent_task.task_id,
                            parent_obligation_id=decision.branch_parent_obligation_id,
                            trigger_evidence_ref=decision.branch_evidence_ref,
                            input_refs=self._decode_handles(item.input_handles),
                            material_reason=item.material_reason,
                        )
                        for item in decision.branch_candidates
                    )
                    materialized = self._research_tasks.materialize_derived_candidates(
                        runtime=runtime,
                        evidence_store=executor.evidence_store,
                        task_registry=task_registry,
                        parent_task=parent_task,
                        proposals=proposals,
                    )
                    result_view = {
                        "strategy": materialized.decision.strategy.value,
                        "classification": materialized.decision.classification.value,
                        "allowed_children": materialized.decision.allowed_children,
                        "selected_task_ids": [
                            task.task_id for task in materialized.registered_tasks
                        ],
                        "remaining_query_budget": runtime.remaining_data_queries,
                        "cardinality_source": "UNKNOWN",
                    }
                    observations.append(
                        {
                            "kind": "fanout_registered",
                            "result": result_view,
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result=result_view,
                    )
                except Exception as exc:
                    observations.append(
                        {
                            "kind": "tool_rejected",
                            "action": decision.action.value,
                            "message": str(exc),
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result={
                            "branch_error": type(exc).__name__,
                            "message": str(exc),
                        },
                    )
                continue

            if decision.action == ManagerActionKind.FINISH:
                try:
                    runtime.finish()
                    observations.append({"kind": "finish", "status": "accepted"})
                    break
                except ManagerStateError as exc:
                    observations.append(
                        {"kind": "finish_rejected", "message": str(exc)}
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result={"finish_rejected": str(exc)},
                    )
                    continue

            try:
                call = self._compile_tool(
                    decision=decision,
                    message_id=message_id,
                    source_hash=source_hash,
                    request_ref=request_ref,
                    runtime=runtime,
                )
                assert call is not None

                research_execution = None
                if (
                    self._research_tool_runner is not None
                    and decision.action in {
                        ManagerActionKind.RUN_ANALYTICS,
                        ManagerActionKind.RUN_RELATIONSHIP,
                    }
                ):
                    if decision.action == ManagerActionKind.RUN_RELATIONSHIP:
                        obligation_id = decision.relationship_obligation_id
                        task_id = f"seed:{obligation_id}"
                        try:
                            task = task_registry.get(task_id)
                        except Exception:
                            task = self._research_tasks.seed_for_obligation(
                                runtime=runtime,
                                obligation_id=obligation_id,
                                task_id=task_id,
                            )
                            task_registry.register(task)
                    elif decision.derived_task_id is None:
                        if len(decision.obligation_ids) != 1:
                            raise ResearchTaskMaterializationError(
                                "Day7 one tool invocation maps to exactly one ResearchTask"
                            )
                        obligation_id = decision.obligation_ids[0]
                        task_id = f"seed:{obligation_id}"
                        try:
                            task = task_registry.get(task_id)
                        except ResearchTaskMaterializationError:
                            raise
                        except Exception:
                            task = self._research_tasks.seed_for_obligation(
                                runtime=runtime,
                                obligation_id=obligation_id,
                                task_id=task_id,
                            )
                    else:
                        try:
                            task = task_registry.get(decision.derived_task_id)
                        except Exception as exc:
                            raise ResearchTaskMaterializationError(
                                "derived execution requires pre-registered READY ResearchTask; "
                                "use propose_branches first"
                            ) from exc
                        if task.state != "pending":
                            raise ResearchTaskMaterializationError(
                                "derived execution requires pending READY ResearchTask"
                            )

                    tool_id = self._research_tool_runner.tool_id_for_task(task)
                    research_execution = self._research_tool_runner.execute(
                        task=task,
                        tool_id=tool_id,
                        call=call,
                        runtime=runtime,
                        executor=executor,
                        principal=getattr(executor, "principal", None),
                        task_registry=task_registry,
                    )
                    manager_result = self._manager_safe(
                        research_execution.observation
                    )
                else:
                    result = runtime.call_tool(call, executor=executor)
                    manager_result = self._manager_safe(result.tool_result)

                observations.append(
                    {
                        "kind": "tool",
                        "tool": call.name.value,
                        "research_task_id": (
                            None
                            if research_execution is None
                            else research_execution.task.task_id
                        ),
                        "result": manager_result,
                    }
                )

                if (
                    call.name == ManagerToolName.INSPECT_EVIDENCE
                    and _zero_row_completion_candidate(
                        runtime=runtime,
                        evidence_store=getattr(executor, "evidence_store", None),
                        task_registry=task_registry,
                    )
                ):
                    try:
                        runtime.finish()
                        observations.append(
                            {
                                "kind": "finish",
                                "status": "accepted",
                                "reason": "inspected_zero_row_no_material_branch",
                            }
                        )
                        break
                    except ManagerStateError:
                        # CompletionGate remains the sole completion authority.
                        # If it rejects, the bounded Manager loop may continue.
                        pass

                progressed = frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result=manager_result,
                )
                if not progressed:
                    observations.append(
                        {
                            "kind": "no_progress",
                            "action": self._manager_safe(decision),
                            "progress_fingerprint": frontier.progress(runtime),
                        }
                    )
            except Exception as exc:
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": str(exc),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"tool_error": type(exc).__name__, "message": str(exc)},
                )
                if runtime.snapshot.state == ManagerState.FAILED:
                    break
                continue

        return ManagerLoopOutcome(
            snapshot=runtime.snapshot,
            run_finished=runtime.snapshot.state == ManagerState.COMPLETED,
            verified_complete=(
                runtime.snapshot.terminal_status == ResearchRunTerminal.VERIFIED_COMPLETE
            ),
            terminal_status=runtime.snapshot.terminal_status,
            clarification_required=(
                runtime.snapshot.state == ManagerState.NEEDS_CLARIFICATION
            ),
            observations=tuple(observations),
            preacceptance_status=FiniteAcceptanceStatus.ACCEPTED,
        )
