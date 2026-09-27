"""Typed P17 Research Manager model adapter.

The provider chooses only the next investigation intent/question. It never computes
analytics, executes queries, mutates Research authority, or sets P16/P19 truth state.
"""
from __future__ import annotations

import copy
import json
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.claim_lineage import ClaimFreshness
from app.v3.product.contracts import ProductInvestigationOutputNeed
from app.v3.structured_transport import validate_provider_strict_schema
from app.v3.research_manager import (
    InvestigationBranchKeyPolicy,
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


ProviderJSONKind = Literal[
    "STRING",
    "INTEGER",
    "NUMBER",
    "BOOLEAN",
    "NULL",
    "OBJECT",
    "ARRAY",
]


class ProviderJSONValue(_Frozen):
    """Closed recursive JSON value for strict provider transport only."""

    kind: ProviderJSONKind
    string_value: str | None = None
    integer_value: int | None = None
    number_value: float | None = None
    boolean_value: bool | None = None
    object_entries: tuple["ProviderObjectEntry", ...] = ()
    array_items: tuple["ProviderJSONValue", ...] = ()

    @model_validator(mode="after")
    def coherent_value(self):
        scalar_fields = {
            "STRING": self.string_value,
            "INTEGER": self.integer_value,
            "NUMBER": self.number_value,
            "BOOLEAN": self.boolean_value,
        }
        active = scalar_fields.get(self.kind)
        if self.kind in scalar_fields:
            if active is None:
                raise ValueError(f"{self.kind} requires its typed value")
            for kind, value in scalar_fields.items():
                if kind != self.kind and value is not None:
                    raise ValueError("provider JSON scalar fields are mutually exclusive")
            if self.object_entries or self.array_items:
                raise ValueError("scalar provider JSON value cannot carry containers")
            return self

        if any(value is not None for value in scalar_fields.values()):
            raise ValueError("container/null provider JSON value cannot carry scalar fields")

        if self.kind == "NULL":
            if self.object_entries or self.array_items:
                raise ValueError("NULL provider JSON value cannot carry containers")
            return self
        if self.kind == "OBJECT":
            if self.array_items:
                raise ValueError("OBJECT provider JSON value cannot carry array items")
            keys = [entry.key for entry in self.object_entries]
            if len(keys) != len(set(keys)):
                raise ValueError("provider JSON object keys must be unique")
            return self
        if self.kind == "ARRAY":
            if self.object_entries:
                raise ValueError("ARRAY provider JSON value cannot carry object entries")
            return self
        raise ValueError(f"unsupported provider JSON kind: {self.kind}")


class ProviderObjectEntry(_Frozen):
    key: str = Field(min_length=1, max_length=256)
    value: ProviderJSONValue


ProviderJSONValue.model_rebuild()


class ProviderClosedObject(_Frozen):
    entries: tuple[ProviderObjectEntry, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_keys(self):
        keys = [entry.key for entry in self.entries]
        if len(keys) != len(set(keys)):
            raise ValueError("provider object keys must be unique")
        return self


class ProviderClaimDraft(_Frozen):
    """Strict provider DTO; mapped deterministically into domain claim shape."""

    claim_text: str = Field(min_length=1)
    proposition: ProviderClosedObject
    scope: ProviderClosedObject
    freshness: ClaimFreshness
    origin_material_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


def _provider_json_value(value: ProviderJSONValue) -> Any:
    if value.kind == "STRING":
        return value.string_value
    if value.kind == "INTEGER":
        return value.integer_value
    if value.kind == "NUMBER":
        return value.number_value
    if value.kind == "BOOLEAN":
        return value.boolean_value
    if value.kind == "NULL":
        return None
    if value.kind == "OBJECT":
        return {
            entry.key: _provider_json_value(entry.value)
            for entry in value.object_entries
        }
    if value.kind == "ARRAY":
        return [_provider_json_value(item) for item in value.array_items]
    raise ValueError(f"unsupported provider JSON kind: {value.kind}")


def _provider_object(value: ProviderClosedObject) -> dict[str, Any]:
    return {
        entry.key: _provider_json_value(entry.value)
        for entry in value.entries
    }


def _domain_claim(value: ProviderClaimDraft) -> ProposedClaimDraft:
    return ProposedClaimDraft(
        claim_text=value.claim_text,
        proposition=_provider_object(value.proposition),
        scope=_provider_object(value.scope),
        freshness=value.freshness,
        origin_material_refs=value.origin_material_refs,
        limitations=value.limitations,
    )


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
    claim: ProviderClaimDraft | None = None

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


ResearchManagerProposalDraft.model_rebuild()


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


_OUTPUT_NEED_GUIDANCE: dict[ProductInvestigationOutputNeed, str] = {
    ProductInvestigationOutputNeed.RELATIONSHIP_INTERPRETATION_INPUT: (
        "Downstream composition can call relationship interpretation only after "
        "this exact obligation has at least one governed claim and one completed "
        "reasoning step. Continue only through state-legal P17 moves. If legal "
        "support cannot be established, use the existing legal stop vocabulary. "
        "Do not invent a claim or relationship."
    ),
    ProductInvestigationOutputNeed.COMPETING_EXPLANATION_INPUTS: (
        "Downstream root-cause epistemics can be called only after this exact "
        "obligation has at least two distinct governed candidate claims. Preserve "
        "competing branches and counter-evidence. Continue only through state-legal "
        "P17 moves; stop legally rather than fabricate a second candidate."
    ),
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
        "minItems",
        "maxItems",
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
    validate_provider_strict_schema(value)
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

    variants = []
    for intent in effective:
        if intent not in _ACTION_FOR_INTENT:
            raise ValueError(
                f"unsupported P17 live intent: {intent.value}"
            )
        # One variant per legal move lets the provider see the state-derived
        # parent/branch contract without becoming final authority.
        variants.append(_variant_schema(raw, (intent,)))
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


def _parent_schema(
    *,
    legal_parent_step_ids: tuple[str, ...],
    allow_parentless: bool,
) -> dict[str, Any]:
    ids = list(legal_parent_step_ids)
    if allow_parentless and not ids:
        return {"type": "null"}
    if not allow_parentless:
        return {"type": "string", "enum": ids}
    return {
        "anyOf": [
            {"type": "null"},
            {"type": "string", "enum": ids},
        ]
    }


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
    def _snapshot_payload(
        snapshot: ResearchManagerSnapshot,
        *,
        target_parent_obligation: str | None = None,
        allowed_evidence_refs: tuple[str, ...] | None = None,
    ) -> str:
        payload = snapshot.model_dump(mode="json")
        if target_parent_obligation is not None:
            known = {
                item.obligation_id for item in snapshot.parent_obligations
            }
            if target_parent_obligation not in known:
                raise ValueError(
                    "provider target obligation must exist in governed snapshot"
                )
            scoped_nodes = tuple(
                node
                for node in snapshot.investigation.nodes
                if node.root_obligation_id == target_parent_obligation
            )
            scoped_step_ids = {node.step_id for node in scoped_nodes}
            scoped_branch_ids = {node.branch_id for node in scoped_nodes}
            evidence = set(allowed_evidence_refs or ())
            for node in scoped_nodes:
                evidence.update(node.evidence_refs)
                evidence.update(node.counter_evidence_refs)
            scoped_claims = tuple(
                item
                for item in snapshot.claims
                if item.obligation_id == target_parent_obligation
            )
            scoped_materials = tuple(
                item
                for item in snapshot.materials
                if item.obligation_id == target_parent_obligation
            )
            payload["parent_obligations"] = [
                item
                for item in payload["parent_obligations"]
                if item["obligation_id"] == target_parent_obligation
            ]
            payload["evidence_refs"] = sorted(
                ref for ref in snapshot.evidence_refs if ref in evidence
            )
            payload["claims"] = [
                item.model_dump(mode="json") for item in scoped_claims
            ]
            payload["materials"] = [
                item.model_dump(mode="json") for item in scoped_materials
            ]
            payload["material_refs"] = sorted(
                item.lead_id for item in scoped_materials
            )
            graph = payload["investigation"]
            graph["nodes"] = [
                node.model_dump(mode="json") for node in scoped_nodes
            ]
            graph["root_step_ids"] = [
                step_id
                for step_id in graph["root_step_ids"]
                if step_id in scoped_step_ids
            ]
            graph["open_branch_ids"] = [
                branch_id
                for branch_id in graph["open_branch_ids"]
                if branch_id in scoped_branch_ids
            ]
            graph["stopped_branch_ids"] = [
                branch_id
                for branch_id in graph["stopped_branch_ids"]
                if branch_id in scoped_branch_ids
            ]
            graph["max_observed_depth"] = max(
                (node.depth for node in scoped_nodes),
                default=0,
            )
            payload["completed_reasoning_steps"] = [
                step_id
                for step_id in payload["completed_reasoning_steps"]
                if step_id in scoped_step_ids
            ]
            payload["pending_reasoning_steps"] = [
                step_id
                for step_id in payload["pending_reasoning_steps"]
                if step_id in scoped_step_ids
            ]
            for rule in payload["action_profile"]["rules"]:
                rule["legal_parent_step_ids"] = [
                    step_id
                    for step_id in rule["legal_parent_step_ids"]
                    if step_id in scoped_step_ids
                ]
        return json.dumps(
            payload,
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
        if draft.claim is not None:
            payload["claim"] = _domain_claim(draft.claim).model_dump()
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
        target_parent_obligation: str | None = None,
        allowed_evidence_refs: tuple[str, ...] | None = None,
        output_need: ProductInvestigationOutputNeed | None = None,
    ) -> ManagerProposal:
        user = (
            "Choose exactly one next bounded investigation step from this "
            "governed snapshot. Reference only IDs present in the snapshot. "
            "Choose only an intent/parent/branch-key combination exposed by "
            "the state-derived action_profile. branch_key never creates a "
            "branch unless that legal move explicitly requires it. "
            "Use STOP_BRANCH for one exhausted/contradicted branch and "
            "STOP_INVESTIGATION only when the whole investigation should end."
        )
        if output_need is not None:
            user += (
                "\n\nPRODUCT ORCHESTRATION OUTPUT NEED JSON "
                "(closed typed metadata; not analytical truth):\n"
                + json.dumps(
                    {"kind": output_need.value},
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
                + _OUTPUT_NEED_GUIDANCE[output_need]
            )
        if guidance:
            user += (
                "\n\nBOUNDARY-SHAPE GUIDANCE (does not supply the analytical "
                "answer):\n" + guidance.strip()
            )
        state_legal = snapshot.action_profile.legal_intents
        scoped_step_ids: set[str] | None = None
        scoped_claim_ids: tuple[str, ...] | None = None
        scoped_material_ids: tuple[str, ...] | None = None
        scoped_evidence_ids: tuple[str, ...] | None = None
        if target_parent_obligation is not None:
            if target_parent_obligation not in {
                item.obligation_id for item in snapshot.parent_obligations
            }:
                raise ValueError(
                    "provider target obligation must exist in governed snapshot"
                )
            scoped_nodes = tuple(
                node
                for node in snapshot.investigation.nodes
                if node.root_obligation_id == target_parent_obligation
            )
            scoped_step_ids = {node.step_id for node in scoped_nodes}
            evidence = set(allowed_evidence_refs or ())
            for node in scoped_nodes:
                evidence.update(node.evidence_refs)
                evidence.update(node.counter_evidence_refs)
            scoped_evidence_ids = tuple(
                sorted(
                    ref for ref in snapshot.evidence_refs
                    if ref in evidence
                )
            )
            scoped_claim_ids = tuple(
                sorted(
                    item.claim_id for item in snapshot.claims
                    if item.obligation_id == target_parent_obligation
                )
            )
            scoped_material_ids = tuple(
                sorted(
                    item.lead_id for item in snapshot.materials
                    if item.obligation_id == target_parent_obligation
                )
            )
        user += (
            "\n\nGOVERNED SNAPSHOT JSON:\n"
            + self._snapshot_payload(
                snapshot,
                target_parent_obligation=target_parent_obligation,
                allowed_evidence_refs=allowed_evidence_refs,
            )
        )
        effective_intents = (
            tuple(
                intent
                for intent in allowed_intents
                if intent in state_legal
            )
            if allowed_intents is not None
            else state_legal
        )
        if target_parent_obligation is not None:
            narrowed_intents: list[InvestigationIntent] = []
            for intent in effective_intents:
                rule = snapshot.action_profile.rule_for(intent)
                if rule is None:
                    continue
                legal_scoped_parents = tuple(
                    step_id
                    for step_id in rule.legal_parent_step_ids
                    if scoped_step_ids is not None
                    and step_id in scoped_step_ids
                )
                if rule.allow_parentless or legal_scoped_parents:
                    if (
                        intent == InvestigationIntent.SEEK_COUNTER_EVIDENCE
                        and not scoped_claim_ids
                    ):
                        continue
                    narrowed_intents.append(intent)
            effective_intents = tuple(narrowed_intents)
        if not effective_intents:
            raise ValueError(
                "no state-legal P17 intent remains in the requested vocabulary"
            )

        schema = _schema_for_intents(effective_intents)
        property_maps = _schema_property_maps(schema)
        for props in property_maps:
            intent_values = props["intent"].get("enum") or []
            if len(intent_values) != 1:
                raise ValueError(
                    "state-derived provider variant must represent one intent"
                )
            intent = InvestigationIntent(intent_values[0])
            rule = snapshot.action_profile.rule_for(intent)
            if rule is None:
                raise ValueError(
                    f"missing action-profile rule for {intent.value}"
                )
            props["source_revision"] = {
                "type": "integer",
                "enum": [snapshot.source_revision],
            }
            target_ids = (
                [target_parent_obligation]
                if target_parent_obligation is not None
                else [
                    x.obligation_id for x in snapshot.parent_obligations
                ]
            )
            props["target_parent_obligation"] = {
                "type": "string",
                "enum": target_ids,
            }
            legal_parent_step_ids = rule.legal_parent_step_ids
            if scoped_step_ids is not None:
                legal_parent_step_ids = tuple(
                    step_id
                    for step_id in legal_parent_step_ids
                    if step_id in scoped_step_ids
                )
            props["parent_step_id"] = _parent_schema(
                legal_parent_step_ids=legal_parent_step_ids,
                allow_parentless=rule.allow_parentless,
            )
            if scoped_evidence_ids is not None:
                props["inspected_evidence_refs"] = {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": list(scoped_evidence_ids),
                    },
                }
            if scoped_claim_ids:
                props["inspected_claim_refs"] = {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": list(scoped_claim_ids),
                    },
                }
                if "counter_to_claim_id" in props:
                    props["counter_to_claim_id"] = {
                        "type": "string",
                        "enum": list(scoped_claim_ids),
                    }
            if scoped_material_ids:
                props["inspected_material_refs"] = {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": list(scoped_material_ids),
                    },
                }
            props["branch_key"] = (
                {"type": "string"}
                if rule.branch_key_policy
                == InvestigationBranchKeyPolicy.REQUIRED
                else {"type": "null"}
            )
        if allowed_parent_step_ids is not None:
            requested = set(allowed_parent_step_ids)
            for props in property_maps:
                intent = InvestigationIntent(props["intent"]["enum"][0])
                rule = snapshot.action_profile.rule_for(intent)
                assert rule is not None
                legal = set(rule.legal_parent_step_ids)
                if rule.allow_parentless:
                    legal.add(None)
                narrowed = tuple(
                    value
                    for value in allowed_parent_step_ids
                    if value in legal
                )
                if set(narrowed) != requested:
                    raise ValueError(
                        "provider parent constraint cannot broaden action-profile legality"
                    )
                props["parent_step_id"] = _parent_schema(
                    legal_parent_step_ids=tuple(
                        x for x in narrowed if isinstance(x, str)
                    ),
                    allow_parentless=None in narrowed,
                )
        if branch_key_mode is not None:
            expected = (
                "string"
                if all(
                    snapshot.action_profile.rule_for(
                        InvestigationIntent(props["intent"]["enum"][0])
                    ).branch_key_policy
                    == InvestigationBranchKeyPolicy.REQUIRED
                    for props in property_maps
                )
                else "null"
                if all(
                    snapshot.action_profile.rule_for(
                        InvestigationIntent(props["intent"]["enum"][0])
                    ).branch_key_policy
                    == InvestigationBranchKeyPolicy.FORBIDDEN
                    for props in property_maps
                )
                else None
            )
            if branch_key_mode != expected:
                raise ValueError(
                    "provider branch-key constraint cannot broaden action-profile legality"
                )

        if scoped_material_ids:
            for definition in (schema.get("$defs") or {}).values():
                if not isinstance(definition, dict):
                    continue
                props = definition.get("properties")
                if (
                    isinstance(props, dict)
                    and "origin_material_refs" in props
                ):
                    props["origin_material_refs"] = {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": list(scoped_material_ids),
                        },
                    }

        # Dynamic action-profile narrowing mutates scalar constraints after
        # schema construction. Re-validate the final provider representation
        # immediately before transport so no reachable state can emit an open
        # strict-schema object.
        validate_provider_strict_schema(schema)

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
        if draft.intent not in effective_intents:
            raise ValueError(
                f"manager emitted {draft.intent.value} outside state-legal bounded intent set"            )
        return self._proposal(draft)

    def propose(self, snapshot: ResearchManagerSnapshot) -> ManagerProposal:
        return self._propose(snapshot)

    def propose_with_constraints(
        self,
        snapshot: ResearchManagerSnapshot,
        *,
        allowed_intents: tuple[InvestigationIntent, ...],
    ) -> ManagerProposal:
        """Narrow certification vocabulary inside state-derived move legality.

        The state action profile owns dynamic legality. This seam can only remove
        intents from that legal set; it never selects a parent, branch, target,
        business explanation, or trajectory.
        """
        if not allowed_intents:
            raise ValueError("allowed_intents must not be empty")
        return self._propose(
            snapshot,
            allowed_intents=allowed_intents,
        )

    def propose_for_obligation(
        self,
        snapshot: ResearchManagerSnapshot,
        *,
        target_parent_obligation: str,
        allowed_evidence_refs: tuple[str, ...],
        output_need: ProductInvestigationOutputNeed | None = None,
    ) -> ManagerProposal:
        """Narrow provider representation to one legally rooted obligation.

        This method cannot broaden P17 legality. The domain validator in
        research_manager.py remains final authority for every returned ref.
        """
        return self._propose(
            snapshot,
            target_parent_obligation=target_parent_obligation,
            allowed_evidence_refs=allowed_evidence_refs,
            output_need=output_need,
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
