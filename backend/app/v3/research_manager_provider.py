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
    def coherent_live_semantics(self):
        if self.intent == InvestigationIntent.LEGACY:
            raise ValueError("live manager cannot emit LEGACY intent")

        stop_intents = {
            InvestigationIntent.STOP_BRANCH,
            InvestigationIntent.STOP_INVESTIGATION,
        }
        if self.intent in stop_intents:
            if self.stop_reason is None:
                raise ValueError("live STOP intent requires stop_reason")
            return self

        if (
            not self.bounded_objective
            or not self.bounded_objective.strip()
        ):
            raise ValueError(
                "live non-STOP intent requires bounded_objective"
            )
        if (
            not self.expected_information_gain
            or not self.expected_information_gain.strip()
        ):
            raise ValueError(
                "live non-STOP intent requires expected_information_gain"
            )
        if self.stop_reason is not None:
            raise ValueError(
                "live non-STOP intent cannot carry stop_reason"
            )
        if (
            self.intent == InvestigationIntent.SEEK_COUNTER_EVIDENCE
            and not self.counter_to_claim_id
        ):
            raise ValueError(
                "live SEEK_COUNTER_EVIDENCE requires counter_to_claim_id"
            )
        if (
            self.intent == InvestigationIntent.FORM_CLAIM
            and self.claim is None
        ):
            raise ValueError("live FORM_CLAIM requires claim")
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


_STOP_INTENTS = {
    InvestigationIntent.STOP_BRANCH,
    InvestigationIntent.STOP_INVESTIGATION,
}
_COMMON_TRANSPORT_FIELDS = (
    "proposal_id",
    "source_revision",
    "target_parent_obligation",
    "intent",
    "parent_step_id",
    "branch_key",
    "target_kind",
    "target_ref",
    "objective_key",
    "rationale",
    "inspected_evidence_refs",
    "inspected_claim_refs",
    "inspected_material_refs",
)


def _semantic_family(intent: InvestigationIntent) -> str:
    if intent in _STOP_INTENTS:
        return "stop"
    if intent == InvestigationIntent.SEEK_COUNTER_EVIDENCE:
        return "counter"
    if intent == InvestigationIntent.FORM_CLAIM:
        return "claim"
    return "regular"


def _non_null_schema(node: dict[str, Any]) -> dict[str, Any]:
    choices = node.get("anyOf")
    if isinstance(choices, list):
        non_null = [
            copy.deepcopy(choice)
            for choice in choices
            if not (
                isinstance(choice, dict)
                and choice.get("type") == "null"
            )
        ]
        if len(non_null) == 1:
            return non_null[0]
    return copy.deepcopy(node)


def _variant_schema(
    raw_schema: dict[str, Any],
    intents: tuple[InvestigationIntent, ...],
) -> dict[str, Any]:
    props = raw_schema.get("properties") or {}
    family = {_semantic_family(intent) for intent in intents}
    if len(family) != 1:
        raise ValueError("transport variant must contain one semantic family")
    family_name = next(iter(family))

    selected = {
        key: copy.deepcopy(props[key])
        for key in _COMMON_TRANSPORT_FIELDS
    }
    selected["intent"] = {
        "type": "string",
        "enum": [intent.value for intent in intents],
    }

    if family_name == "stop":
        selected["stop_reason"] = _non_null_schema(
            props["stop_reason"]
        )
    else:
        selected["bounded_objective"] = {"type": "string"}
        selected["expected_information_gain"] = {"type": "string"}
        if family_name == "counter":
            selected["counter_to_claim_id"] = {"type": "string"}
        elif family_name == "claim":
            selected["claim"] = _non_null_schema(props["claim"])

    return {
        "type": "object",
        "properties": selected,
    }


def _schema_for_intents(
    intents: tuple[InvestigationIntent, ...] | None,
) -> dict[str, Any]:
    """Build provider schema without weakening Pydantic semantic authority.

    A flat schema is sufficient when every permitted intent has the same
    conditional payload requirements. Mixed semantic families use one nested
    discriminated transport envelope so invalid cross-field combinations are
    not representable merely because nullable Pydantic fields share one model.
    """

    raw = ResearchManagerProposalDraft.model_json_schema()
    effective = intents or tuple(_ACTION_FOR_INTENT)
    if not effective:
        raise ValueError("at least one live intent is required")

    grouped: dict[str, list[InvestigationIntent]] = {}
    for intent in effective:
        if intent not in _ACTION_FOR_INTENT:
            raise ValueError(
                f"unsupported P17 live intent: {intent.value}"
            )
        grouped.setdefault(_semantic_family(intent), []).append(intent)

    variants = [
        _variant_schema(raw, tuple(grouped[name]))
        for name in ("regular", "counter", "claim", "stop")
        if name in grouped
    ]
    if len(variants) == 1:
        schema = variants[0]
        schema["$defs"] = copy.deepcopy(raw.get("$defs") or {})
        return _strict_json_schema(schema)

    schema = {
        "type": "object",
        "properties": {
            "proposal": {
                "anyOf": variants,
            }
        },
        "$defs": copy.deepcopy(raw.get("$defs") or {}),
    }
    return _strict_json_schema(schema)


def _schema_property_maps(
    schema: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    props = schema.get("properties") or {}
    proposal = props.get("proposal")
    if isinstance(proposal, dict):
        variants = proposal.get("anyOf")
        if isinstance(variants, list):
            maps = tuple(
                variant["properties"]
                for variant in variants
                if isinstance(variant, dict)
                and isinstance(variant.get("properties"), dict)
            )
            if len(maps) != len(variants):
                raise ValueError(
                    "invalid semantic transport envelope"
                )
            return maps
    return (props,)


def _draft_payload_from_transport(
    raw: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    decoded = json.loads(raw)
    if not isinstance(decoded, dict):
        raise ValueError("manager structured output must be an object")
    if "proposal" not in (schema.get("properties") or {}):
        return decoded
    if set(decoded) != {"proposal"}:
        raise ValueError(
            "semantic transport envelope must contain only proposal"
        )
    proposal = decoded.get("proposal")
    if not isinstance(proposal, dict):
        raise ValueError("semantic transport proposal must be an object")
    return proposal


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
        allowed_parent_step_ids: tuple[str | None, ...] | None = None,
        branch_key_mode: str | None = None,
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
        property_maps = _schema_property_maps(schema)
        for props in property_maps:
            props["source_revision"] = {
                "type": "integer",
                "enum": [snapshot.source_revision],
            }
            props["target_parent_obligation"] = {
                "type": "string",
                "enum": [
                    x.obligation_id for x in snapshot.parent_obligations
                ],
            }
        if allowed_parent_step_ids is not None:
            values = list(allowed_parent_step_ids)
            for props in property_maps:
                if values == [None]:
                    props["parent_step_id"] = {"type": "null"}
                elif all(isinstance(x, str) for x in values):
                    props["parent_step_id"] = {
                        "type": "string",
                        "enum": values,
                    }
                else:
                    props["parent_step_id"] = {
                        "anyOf": [
                            {"type": "null"},
                            {
                                "type": "string",
                                "enum": [
                                    x for x in values if x is not None
                                ],
                            },
                        ]
                    }
        if branch_key_mode in {"null", "string"}:
            for props in property_maps:
                props["branch_key"] = {"type": branch_key_mode}
        elif branch_key_mode is not None:
            raise ValueError(
                f"unknown branch_key_mode: {branch_key_mode}"
            )
        raw = self._transport.structured_json(
            _SYSTEM,
            user,
            schema=schema,
            schema_name=self._schema_name,
        )
        self.call_count += 1
        draft = ResearchManagerProposalDraft.model_validate(
            _draft_payload_from_transport(raw, schema)
        )
        if allowed_intents and draft.intent not in allowed_intents:
            raise ValueError(
                f"manager emitted {draft.intent.value} outside bounded canary intent set"
            )
        return self._proposal(draft)

    def propose(self, snapshot: ResearchManagerSnapshot) -> ManagerProposal:
        return self._propose(snapshot)

    def propose_with_constraints(
        self,
        snapshot: ResearchManagerSnapshot,
        *,
        allowed_intents: tuple[InvestigationIntent, ...],
    ) -> ManagerProposal:
        """Constrain only the legal intent vocabulary, never investigation content.

        This seam is for autonomous certification/product surfaces whose authority
        already excludes some payload families. It supplies no guidance, parent,
        branch, target, or trajectory choice to the model.
        """
        if not allowed_intents:
            raise ValueError("allowed_intents must not be empty")
        return self._propose(
            snapshot,
            allowed_intents=allowed_intents,
        )

    def propose_with_guidance(
        self,
        snapshot: ResearchManagerSnapshot,
        *,
        guidance: str,
        allowed_intents: tuple[InvestigationIntent, ...] | None = None,
        allowed_parent_step_ids: tuple[str | None, ...] | None = None,
        branch_key_mode: str | None = None,
    ) -> ManagerProposal:
        """Canary/evaluation seam: constrain authority shape, never the answer."""
        return self._propose(
            snapshot,
            guidance=guidance,
            allowed_intents=allowed_intents,
            allowed_parent_step_ids=allowed_parent_step_ids,
            branch_key_mode=branch_key_mode,
        )
