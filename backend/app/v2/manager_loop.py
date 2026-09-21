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
from app.v2.manager_runtime import (
    ManagerBudgetError,
    ManagerRuntime,
    ManagerStateError,
)
from app.v2.manager_tools import (
    ManagerToolCall,
    ManagerToolName,
)
from app.v2.models import FrozenModel
from app.v2.source_spans import SourceSpanRegistry


class ManagerActionKind(StrEnum):
    RESOLVE_SEMANTICS = "resolve_semantics"
    PROPOSE_ACCEPTANCE = "propose_acceptance"
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
    semantic_handle_refs: tuple[str, ...] = ()
    open_questions: tuple[str, ...] = ()


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
    temporal_anchor_handle: str | None = None
    base_period_handle: str | None = None
    semantic_parent_obligation_id: str | None = None
    semantic_evidence_ref: str | None = None
    semantic_proposal: str | None = Field(default=None, max_length=240)

    obligations: tuple[ManagerObligationProposal, ...] = ()

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
        return self


@dataclass(frozen=True)
class ManagerLoopOutcome:
    snapshot: Any
    run_finished: bool
    verified_complete: bool
    terminal_status: ResearchRunTerminal | None
    clarification_required: bool
    observations: tuple[dict[str, Any], ...]


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


_SYSTEM = """You are Dima's bounded RESEARCH_MANAGER.

Return exactly ONE next action using the provided JSON schema. Do not reveal or emit
private chain-of-thought. Do not write SQL. Do not invent canonical metric/dimension
identifiers. Canonical semantics are owned by resolve_semantics and appear only as
opaque sem_* handles.

Rules:
- Human-language understanding may be iterative.
- USER_SOURCE source_surfaces MUST be literal substrings of USER_MESSAGE.
- AGENT_DERIVED semantic discovery MUST cite parent_obligation_id + evidence_ref + proposal.
- Before data execution, propose_acceptance must succeed.
- Rejected attempts leave no semantic fields to merge.
- run_analytics/run_relationship may reference only accepted/derived obligation IDs.
- Use inspect_evidence before making result-dependent next decisions when needed.
- Semantic ambiguity is NOT Manager authority. If a tenant term may be ambiguous, call
  resolve_semantics first. Before acceptance, request_clarification is valid only after
  SemanticResolver returned unresolved/clarification or AcceptanceGate returned
  NEEDS_CLARIFICATION. Never stop on your own guess that a business word is ambiguous.
- If governed ambiguity blocks a MUST, request_clarification rather than guessing.
- finish is a proposal; deterministic CompletionGate decides whether completion is true.
- One action per turn. No prose outside the schema.
- The native schema is strict: emit EVERY field. Use [] for unused arrays and null for
  unused nullable scalar fields. Never omit a field.
- Ranking is an OPERATION, not a semantic concept: resolve only the metric/dimension/filter
  concepts, then send ranking_direction + limit in run_analytics. Never send top/highest/
  lowest wording to resolve_semantics.
- Time/comparison are governed normalization kinds: tag the base-period surface as "time"
  and the reference/comparison surface as "comparison". They may be resolved together
  with metric/dimension surfaces; the runtime derives the temporal anchor/base safely.
- A standard USER_MUST must be accepted only after its required sem_* handles exist.
- If a research obligation becomes UNSUPPORTED, BLOCKED_DATA_GAP or LIMITED with an
  explicit blocker, do not ask the user to choose a different task merely to avoid a
  partial result. Propose finish; CompletionGate will truthfully return PARTIAL.
"""


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


class ResearchManagerLoop:
    def __init__(self, *, llm, source_spans: SourceSpanRegistry) -> None:
        structured = getattr(llm, "structured_json", None)
        if not callable(structured):
            raise ValueError("RESEARCH_MANAGER provider native structured_json desteklemiyor")
        self._structured = structured
        self._source_spans = source_spans

    def _prompt(
        self,
        *,
        question: str,
        runtime: ManagerRuntime,
        observations: list[dict[str, Any]],
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
                    "semantic_handle_refs": list(item.semantic_handle_refs),
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
            "RECENT_OBSERVATIONS": observations[-6:],
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _parse_decision(raw: Any) -> ManagerDecisionTransport:
        data = json.loads(raw) if isinstance(raw, str) else raw
        return ManagerDecisionTransport.model_validate(data)

    def _decision(self, *, question: str, runtime: ManagerRuntime, observations):
        user = self._prompt(
            question=question,
            runtime=runtime,
            observations=observations,
        )
        schema = _strict_native_schema(ManagerDecisionTransport.model_json_schema())
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
        if decision.action == ManagerActionKind.FINISH:
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
                    "temporal_anchor_handle": decision.temporal_anchor_handle,
                    "base_period_handle": decision.base_period_handle,
                }
            else:
                args = {
                    "provenance": "AGENT_DERIVED",
                    "source_refs": (),
                    "target_kind_hints": decision.target_kind_hints,
                    "temporal_anchor_handle": decision.temporal_anchor_handle,
                    "base_period_handle": decision.base_period_handle,
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
                        semantic_handle_refs=item.semantic_handle_refs,
                        open_questions=item.open_questions,
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
                    "metric_handles": decision.metric_handles,
                    "dimension_handles": decision.dimension_handles,
                    "filter_handles": decision.filter_handles,
                    "period_handle": decision.period_handle,
                    "comparison_handle": decision.comparison_handle,
                    "ranking_direction": decision.ranking_direction,
                    "limit": decision.limit,
                    "derived_task_id": decision.derived_task_id,
                    "derived_parent_obligation_id": decision.derived_parent_obligation_id,
                    "derived_capability_key": (
                        decision.derived_capability_key.value
                        if decision.derived_capability_key is not None
                        else None
                    ),
                },
            )

        if decision.action == ManagerActionKind.RUN_RELATIONSHIP:
            return ManagerToolCall(
                name=ManagerToolName.RUN_RELATIONSHIP,
                args={
                    "obligation_id": decision.relationship_obligation_id,
                    "focus_handles": decision.focus_handles,
                    "counterpart_handles": decision.counterpart_handles,
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

    def run(
        self,
        *,
        question: str,
        message_id: str,
        request_ref: str,
        runtime: ManagerRuntime,
        executor,
    ) -> ManagerLoopOutcome:
        source_hash = self._source_spans.register_message(
            message_id=message_id,
            text=question,
        )
        if runtime.snapshot.state == ManagerState.INITIAL:
            runtime.begin_understanding()

        observations: list[dict[str, Any]] = []

        while runtime.snapshot.state not in {
            ManagerState.COMPLETED,
            ManagerState.FAILED,
            ManagerState.BUDGET_EXHAUSTED,
        }:
            try:
                runtime.note_manager_turn()
            except ManagerBudgetError as exc:
                observations.append({"kind": "budget", "message": str(exc)})
                break

            try:
                decision = self._decision(
                    question=question,
                    runtime=runtime,
                    observations=observations,
                )
            except Exception as exc:
                observations.append({"kind": "model_error", "message": str(exc)})
                break

            if (
                decision.action == ManagerActionKind.REQUEST_CLARIFICATION
                and not _clarification_has_governed_grounding(
                    observations,
                    accepted_contract_present=runtime.accepted_contract is not None,
                )
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": (
                            "pre-acceptance clarification requires governed grounding; "
                            "use resolve_semantics or AcceptanceGate first"
                        ),
                    }
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
                result = runtime.call_tool(call, executor=executor)
                observations.append(
                    {
                        "kind": "tool",
                        "tool": call.name.value,
                        "result": _safe(result.tool_result),
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
                if runtime.snapshot.state == ManagerState.FAILED:
                    break
                continue

            if runtime.snapshot.state == ManagerState.NEEDS_CLARIFICATION:
                break

        return ManagerLoopOutcome(
            snapshot=runtime.snapshot,
            run_finished=runtime.snapshot.state == ManagerState.COMPLETED,
            verified_complete=(
                runtime.snapshot.terminal_status == ResearchRunTerminal.VERIFIED_COMPLETE
            ),
            terminal_status=runtime.snapshot.terminal_status,
            clarification_required=runtime.snapshot.state == ManagerState.NEEDS_CLARIFICATION,
            observations=tuple(observations),
        )
