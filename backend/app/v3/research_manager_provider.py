"""Typed P17 Research Manager model adapter.

The provider chooses only the next investigation intent/question. It never computes
analytics, executes queries, mutates Research authority, or sets P16/P19 truth state.
"""
from __future__ import annotations

import copy
import json
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.research_manager import (
    InvestigationIntent,
    InvestigationTargetKind,
    ManagerAction,
    ManagerProposal,
    ManagerStopReason,
    ProposedClaimDraft,
    ResearchManagerSnapshot,
)


class StructuredJSONTransport(Protocol):
    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str: ...


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchManagerProposalDraft(_Frozen):
    """Model-owned semantics before deterministic compatibility mapping."""

    proposal_id: str = Field(min_length=1, max_length=160)
    source_revision: int = Field(ge=1)
    target_parent_obligation: str = Field(min_length=1)
    intent: InvestigationIntent
    parent_step_id: str | None = Field(
        default=None,
        pattern=r"^rrs_[a-f0-9]{24}$",
    )
    branch_key: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$",
    )
    target_kind: InvestigationTargetKind = InvestigationTargetKind.GAP
    target_ref: str | None = Field(default=None, max_length=512)
    objective_key: str = Field(
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"
    )
    bounded_objective: str | None = Field(default=None, max_length=2000)
    rationale: str = Field(min_length=1, max_length=4000)
    inspected_evidence_refs: tuple[str, ...] = ()
    inspected_claim_refs: tuple[str, ...] = ()
    inspected_material_refs: tuple[str, ...] = ()
    expected_information_gain: str | None = Field(
        default=None,
        max_length=2000,
    )
    stop_reason: ManagerStopReason | None = None
    counter_to_claim_id: str | None = None
    claim: ProposedClaimDraft | None = None

    @model_validator(mode="after")
    def no_legacy_intent(self):
        if self.intent == InvestigationIntent.LEGACY:
            raise ValueError("live manager cannot emit LEGACY intent")
        return self


_ACTION_FOR_INTENT = {
    InvestigationIntent.INVESTIGATE_GAP: ManagerAction.EXPLORE_NATIVE,
    InvestigationIntent.EXPLORE_ALTERNATIVES: (
        ManagerAction.RECORD_INVESTIGATION
    ),
    InvestigationIntent.SEEK_COUNTER_EVIDENCE: (
        ManagerAction.SEEK_COUNTER_EVIDENCE
    ),
    InvestigationIntent.DEEPEN_EXPLANATION: (
        ManagerAction.RECORD_INVESTIGATION
    ),
    InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE: (
        ManagerAction.EXPLORE_NATIVE
    ),
    InvestigationIntent.REPLAN: ManagerAction.RECORD_INVESTIGATION,
    InvestigationIntent.FORM_CLAIM: ManagerAction.FORM_CLAIM,
    InvestigationIntent.STOP_BRANCH: ManagerAction.STOP,
    InvestigationIntent.STOP_INVESTIGATION: ManagerAction.STOP,
}


_SYSTEM = """You are Dima's bounded P17 Research Manager.

Architecture:
- METABASE + METABOT = analytical engine.
- DIMA = investigation + epistemics + decision brain.
- You decide WHAT analytical question should be investigated next.
- You do NOT calculate breakdowns, trends, rankings, comparisons, contributions,
  causal effects, probabilities, SQL, MBQL, joins, or temporal semantics.
- Recursive depth belongs to Dima; analytical execution at every depth belongs
  to Metabase.
- Investigation parent/child edges mean only "we chose to investigate deeper".
  They never assert causal truth.
- Preserve multiple candidate branches. Do not force a single winner.
- Counter-evidence and inconclusive/branch-stop outcomes are first-class.
- Do not invent numerical confidence or information-gain scores.
- P19 causal/contribution truth is outside your authority.
- Return exactly one typed next proposal. Keep rationale concise and factual.
"""


def _strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Pydantic schema to portable strict structured-output semantics.

    Runtime Pydantic validation remains authoritative for field constraints. The
    transport schema intentionally keeps only the portable structural subset.
    """

    value = copy.deepcopy(schema)
    unsupported = {
        "default",
        "title",
        "description",
        "minLength",
        "maxLength",
        "pattern",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "format",
    }

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key in unsupported:
                node.pop(key, None)
            props = node.get("properties")
            if isinstance(props, dict):
                node["additionalProperties"] = False
                node["required"] = list(props)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)

    defs = value.get("$defs")
    if isinstance(defs, dict):
        referenced: set[str] = set()

        def collect(node: Any) -> None:
            if isinstance(node, dict):
                ref = node.get("$ref")
                if (
                    isinstance(ref, str)
                    and ref.startswith("#/$defs/")
                ):
                    referenced.add(ref.removeprefix("#/$defs/"))
                for key, child in node.items():
                    if key != "$defs":
                        collect(child)
            elif isinstance(node, list):
                for child in node:
                    collect(child)

        collect(value)
        pending = list(referenced)
        while pending:
            name = pending.pop()
            definition = defs.get(name)
            if definition is None:
                continue
            before = set(referenced)
            collect(definition)
            pending.extend(sorted(referenced - before))
        value["$defs"] = {
            name: definition
            for name, definition in defs.items()
            if name in referenced
        }
        if not value["$defs"]:
            value.pop("$defs", None)
    return value


def _schema_for_intents(
    intents: tuple[InvestigationIntent, ...] | None,
) -> dict[str, Any]:
    schema = ResearchManagerProposalDraft.model_json_schema()
    if intents:
        props = schema.get("properties") or {}
        props["intent"] = {
            "type": "string",
            "enum": [x.value for x in intents],
        }
        # Canary/eval intent constraints can remove semantically impossible
        # payload families. This changes only transport shape, never authority.
        if InvestigationIntent.FORM_CLAIM not in intents:
            props.pop("claim", None)
        if InvestigationIntent.SEEK_COUNTER_EVIDENCE not in intents:
            props.pop("counter_to_claim_id", None)
        if not any(
            x
            in {
                InvestigationIntent.STOP_BRANCH,
                InvestigationIntent.STOP_INVESTIGATION,
            }
            for x in intents
        ):
            props.pop("stop_reason", None)
    return _strict_json_schema(schema)


class StructuredResearchProposalManager:
    """One real model cognition turn -> one validated ManagerProposal."""

    def __init__(
        self,
        *,
        transport: StructuredJSONTransport,
        schema_name: str = "dima_p17_research_manager_proposal",
    ) -> None:
        self._transport = transport
        self._schema_name = schema_name
        self.call_count = 0

    @staticmethod
    def _snapshot_payload(snapshot: ResearchManagerSnapshot) -> str:
        return json.dumps(
            snapshot.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    @staticmethod
    def _proposal(draft: ResearchManagerProposalDraft) -> ManagerProposal:
        action = _ACTION_FOR_INTENT.get(draft.intent)
        if action is None:
            raise ValueError(
                f"unsupported P17 live intent: {draft.intent.value}"
            )
        payload = draft.model_dump()
        payload["action"] = action
        return ManagerProposal.model_validate(payload)

    def _propose(
        self,
        snapshot: ResearchManagerSnapshot,
        *,
        guidance: str | None = None,
        allowed_intents: tuple[InvestigationIntent, ...] | None = None,
    ) -> ManagerProposal:
        user = (
            "Choose exactly one next bounded investigation step from this "
            "governed snapshot. Reference only IDs present in the snapshot. "
            "If a new sibling alternative is opened, use a stable branch_key. "
            "Use STOP_BRANCH for one exhausted/contradicted branch and "
            "STOP_INVESTIGATION only when the whole investigation should end."
        )
        if guidance:
            user += (
                "\n\nBOUNDARY-SHAPE GUIDANCE (does not supply the analytical "
                "answer):\n" + guidance.strip()
            )
        user += (
            "\n\nGOVERNED SNAPSHOT JSON:\n"
            + self._snapshot_payload(snapshot)
        )
        schema = _schema_for_intents(allowed_intents)
        raw = self._transport.structured_json(
            _SYSTEM,
            user,
            schema=schema,
            schema_name=self._schema_name,
        )
        self.call_count += 1
        draft = ResearchManagerProposalDraft.model_validate_json(raw)
        if allowed_intents and draft.intent not in allowed_intents:
            raise ValueError(
                f"manager emitted {draft.intent.value} outside bounded canary intent set"
            )
        return self._proposal(draft)

    def propose(self, snapshot: ResearchManagerSnapshot) -> ManagerProposal:
        return self._propose(snapshot)

    def propose_with_guidance(
        self,
        snapshot: ResearchManagerSnapshot,
        *,
        guidance: str,
        allowed_intents: tuple[InvestigationIntent, ...] | None = None,
    ) -> ManagerProposal:
        """Canary/evaluation seam: constrain authority shape, never the answer."""
        return self._propose(
            snapshot,
            guidance=guidance,
            allowed_intents=allowed_intents,
        )
