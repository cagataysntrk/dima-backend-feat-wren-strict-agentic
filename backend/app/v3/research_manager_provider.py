"""Typed P17 Research Manager model adapter.

The provider chooses only the next investigation intent/question. It never computes
analytics, executes queries, mutates Research authority, or sets P16/P19 truth state.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.claim_lineage import ClaimFreshness
from app.v3.structured_transport import (
    StructuredProviderError,
    validate_provider_strict_schema,
)
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


class ResearchManagerSemanticDraft(_Frozen):
    """V1 provider-owned cognition only; Dima binds all machine identities."""

    target_objective: str = Field(min_length=1, max_length=2000)
    intent: InvestigationIntent
    branch_concept: str | None = Field(default=None, max_length=512)
    target_kind: InvestigationTargetKind = InvestigationTargetKind.GAP
    target_concept: str | None = Field(default=None, max_length=512)
    bounded_objective: str | None = Field(default=None, max_length=2000)
    rationale: str = Field(min_length=1, max_length=4000)
    inspected_evidence_refs: tuple[str, ...] = ()
    inspected_claim_refs: tuple[str, ...] = ()
    inspected_material_refs: tuple[str, ...] = ()
    expected_information_gain: str | None = Field(default=None, max_length=2000)
    stop_reason: ManagerStopReason | None = None
    counter_to_claim_id: str | None = None
    claim: ProviderClaimDraft | None = None

    @model_validator(mode="after")
    def coherent_live_semantics(self):
        if self.intent == InvestigationIntent.LEGACY:
            raise ValueError("live manager cannot emit LEGACY intent")
        for name, refs in (
            ("Evidence", self.inspected_evidence_refs),
            ("claim", self.inspected_claim_refs),
            ("material", self.inspected_material_refs),
        ):
            if len(refs) != len(set(refs)):
                raise ValueError(f"{name} refs must be unique")

        if self.intent == InvestigationIntent.EXPLORE_ALTERNATIVES:
            if not self.branch_concept or not self.branch_concept.strip():
                raise ValueError("EXPLORE_ALTERNATIVES requires branch_concept")
        elif self.branch_concept is not None:
            raise ValueError("branch_concept is only valid for EXPLORE_ALTERNATIVES")

        stop_intents = {
            InvestigationIntent.STOP_BRANCH,
            InvestigationIntent.STOP_INVESTIGATION,
        }
        if self.intent in stop_intents:
            if self.stop_reason is None:
                raise ValueError("live STOP intent requires stop_reason")
            if self.claim is not None or self.counter_to_claim_id is not None:
                raise ValueError("live STOP intent cannot carry follow-up payload")
            return self

        if not self.bounded_objective or not self.bounded_objective.strip():
            raise ValueError("live non-STOP intent requires bounded_objective")
        if (
            not self.expected_information_gain
            or not self.expected_information_gain.strip()
        ):
            raise ValueError(
                "live non-STOP intent requires expected_information_gain"
            )
        if self.stop_reason is not None:
            raise ValueError("live non-STOP intent cannot carry stop_reason")
        if (
            self.intent == InvestigationIntent.SEEK_COUNTER_EVIDENCE
            and not self.counter_to_claim_id
        ):
            raise ValueError(
                "live SEEK_COUNTER_EVIDENCE requires counter_to_claim_id"
            )
        if (
            self.intent != InvestigationIntent.SEEK_COUNTER_EVIDENCE
            and self.counter_to_claim_id is not None
        ):
            raise ValueError(
                "counter_to_claim_id is only valid for SEEK_COUNTER_EVIDENCE"
            )
        if self.intent == InvestigationIntent.FORM_CLAIM and self.claim is None:
            raise ValueError("live FORM_CLAIM requires claim")
        if self.intent != InvestigationIntent.FORM_CLAIM and self.claim is not None:
            raise ValueError("claim is only valid for FORM_CLAIM")
        return self


ResearchManagerSemanticDraft.model_rebuild()


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
- Return exactly one typed next proposal. Keep rationale concise and factual.\n- Never create or echo proposal/step/branch/task/scope/hypothesis IDs; Dima binds machine identities.\n- Existing governed Evidence/claim/material refs may be selected only from closed legal choices exposed by the schema.\n"""


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
    "target_objective",
    "intent",
    "branch_concept",
    "target_kind",
    "target_concept",
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

    raw = ResearchManagerSemanticDraft.model_json_schema()
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
        """Historical/internal compatibility mapper; not provider-facing in V1."""
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

    @staticmethod
    def _stable(prefix: str, value: Any, *, length: int = 24) -> str:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
        return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]

    @staticmethod
    def _target_obligation(
        snapshot: ResearchManagerSnapshot,
        draft: ResearchManagerSemanticDraft,
        *,
        target_parent_obligation: str | None,
    ) -> str:
        candidates = tuple(
            item
            for item in snapshot.parent_obligations
            if (
                target_parent_obligation is None
                or item.obligation_id == target_parent_obligation
            )
        )
        matches = tuple(
            item for item in candidates
            if item.objective == draft.target_objective
        )
        if len(matches) != 1:
            raise ValueError(
                "provider target_objective must identify exactly one governed obligation"
            )
        return matches[0].obligation_id

    @staticmethod
    def _deterministic_parent_step(
        snapshot: ResearchManagerSnapshot,
        *,
        intent: InvestigationIntent,
        target_obligation_id: str,
        allowed_parent_step_ids: tuple[str | None, ...] | None,
    ) -> str | None:
        rule = snapshot.action_profile.rule_for(intent)
        if rule is None:
            raise ValueError("intent is not legal in current P17 action profile")

        legal = list(rule.legal_parent_step_ids)
        if allowed_parent_step_ids is not None:
            allowed = {item for item in allowed_parent_step_ids if item is not None}
            legal = [step_id for step_id in legal if step_id in allowed]

        node_by_id = {
            node.step_id: node for node in snapshot.investigation.nodes
        }
        legal = [
            step_id for step_id in legal
            if (
                step_id in node_by_id
                and node_by_id[step_id].root_obligation_id
                == target_obligation_id
            )
        ]

        if (
            intent == InvestigationIntent.STOP_INVESTIGATION
            and rule.allow_parentless
            and (
                allowed_parent_step_ids is None
                or None in allowed_parent_step_ids
            )
        ):
            return None
        if legal:
            order = {
                node.step_id: index
                for index, node in enumerate(snapshot.investigation.nodes)
            }
            return max(legal, key=lambda step_id: order.get(step_id, -1))
        if rule.allow_parentless and (
            allowed_parent_step_ids is None
            or None in allowed_parent_step_ids
        ):
            return None
        raise ValueError(
            "no deterministic legal parent remains for provider semantic proposal"
        )

    @classmethod
    def _proposal_from_semantic(
        cls,
        draft: ResearchManagerSemanticDraft,
        *,
        snapshot: ResearchManagerSnapshot,
        target_parent_obligation: str | None,
        allowed_parent_step_ids: tuple[str | None, ...] | None,
    ) -> ManagerProposal:
        target_obligation_id = cls._target_obligation(
            snapshot,
            draft,
            target_parent_obligation=target_parent_obligation,
        )
        parent_step_id = cls._deterministic_parent_step(
            snapshot,
            intent=draft.intent,
            target_obligation_id=target_obligation_id,
            allowed_parent_step_ids=allowed_parent_step_ids,
        )
        rule = snapshot.action_profile.rule_for(draft.intent)
        if rule is None:
            raise ValueError("semantic proposal intent is not state-legal")

        branch_key = None
        if rule.branch_key_policy == InvestigationBranchKeyPolicy.REQUIRED:
            if not draft.branch_concept:
                raise ValueError("state-legal child branch requires branch_concept")
            branch_key = cls._stable(
                "branch.",
                {
                    "session": snapshot.research_session_id,
                    "obligation": target_obligation_id,
                    "parent": parent_step_id,
                    "concept": draft.branch_concept,
                },
                length=20,
            )
        elif draft.branch_concept is not None:
            raise ValueError("branch_concept supplied for non-branching move")

        semantic_identity = {
            "snapshot": snapshot.fingerprint,
            "target_obligation": target_obligation_id,
            "parent_step": parent_step_id,
            "intent": draft.intent.value,
            "target_kind": draft.target_kind.value,
            "target_concept": draft.target_concept,
            "bounded_objective": draft.bounded_objective,
            "branch_concept": draft.branch_concept,
            "counter_to_claim_id": draft.counter_to_claim_id,
            "claim": (
                draft.claim.model_dump(mode="json")
                if draft.claim is not None
                else None
            ),
        }
        legacy = ResearchManagerProposalDraft(
            proposal_id=cls._stable("p17-sem-", semantic_identity),
            source_revision=snapshot.source_revision,
            target_parent_obligation=target_obligation_id,
            intent=draft.intent,
            parent_step_id=parent_step_id,
            branch_key=branch_key,
            target_kind=draft.target_kind,
            target_ref=draft.target_concept,
            objective_key=cls._stable(
                f"v1.{draft.intent.value.lower()}.",
                semantic_identity,
                length=16,
            ),
            bounded_objective=draft.bounded_objective,
            rationale=draft.rationale,
            inspected_evidence_refs=draft.inspected_evidence_refs,
            inspected_claim_refs=draft.inspected_claim_refs,
            inspected_material_refs=draft.inspected_material_refs,
            expected_information_gain=draft.expected_information_gain,
            stop_reason=draft.stop_reason,
            counter_to_claim_id=draft.counter_to_claim_id,
            claim=draft.claim,
        )
        return cls._proposal(legacy)

    @classmethod
    def _provider_inconclusive(
        cls,
        snapshot: ResearchManagerSnapshot,
        *,
        target_parent_obligation: str | None,
    ) -> ManagerProposal:
        target = target_parent_obligation
        if target is None:
            if not snapshot.parent_obligations:
                raise ValueError("P17 snapshot has no parent obligation")
            target = snapshot.parent_obligations[0].obligation_id
        return ManagerProposal(
            proposal_id=cls._stable(
                "p17-provider-inconclusive-",
                {
                    "snapshot": snapshot.fingerprint,
                    "target": target,
                },
                length=16,
            ),
            source_revision=snapshot.source_revision,
            target_parent_obligation=target,
            action=ManagerAction.STOP,
            intent=InvestigationIntent.STOP_INVESTIGATION,
            parent_step_id=None,
            branch_key=None,
            target_kind=InvestigationTargetKind.GAP,
            target_ref=None,
            objective_key="provider_contract.inconclusive",
            bounded_objective=None,
            rationale=(
                "Provider output remained invalid after the single bounded repair."
            ),
            inspected_evidence_refs=(),
            inspected_claim_refs=(),
            inspected_material_refs=(),
            expected_information_gain=None,
            stop_reason=ManagerStopReason.INCONCLUSIVE,
            counter_to_claim_id=None,
            claim=None,
        )

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

        target_rows = tuple(
            item
            for item in snapshot.parent_obligations
            if (
                target_parent_obligation is None
                or item.obligation_id == target_parent_obligation
            )
        )
        target_objectives = tuple(item.objective for item in target_rows)
        if not target_objectives or len(target_objectives) != len(set(target_objectives)):
            raise ValueError(
                "provider target objectives must be present and unambiguous"
            )

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
            props["target_objective"] = {
                "type": "string",
                "enum": list(target_objectives),
            }
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
            props["branch_concept"] = (
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
                if not requested.issubset(legal):
                    raise ValueError(
                        "provider parent constraint cannot broaden action-profile legality"
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

        repair_guidance = (
            "\n\nPROVIDER-CONTRACT REPAIR: the previous structured response "
            "was invalid. Return exactly one schema-valid semantic proposal. "
            "Use only the governed snapshot and closed legal choices. Do not "
            "invent or echo machine identities."
        )
        for attempt in range(2):
            try:
                raw = self._transport.structured_json(
                    _SYSTEM,
                    user if attempt == 0 else user + repair_guidance,
                    schema=schema,
                    schema_name=self._schema_name,
                )
                self.call_count += 1
                draft = ResearchManagerSemanticDraft.model_validate(
                    _draft_payload_from_transport(raw, schema)
                )
                if draft.intent not in effective_intents:
                    raise ValueError(
                        f"manager emitted {draft.intent.value} outside "
                        "state-legal bounded intent set"
                    )
                return self._proposal_from_semantic(
                    draft,
                    snapshot=snapshot,
                    target_parent_obligation=target_parent_obligation,
                    allowed_parent_step_ids=allowed_parent_step_ids,
                )
            except StructuredProviderError as exc:
                self.call_count += 1
                if exc.code not in {
                    "COGNITION_RESPONSE_INVALID",
                    "COGNITION_RESPONSE_EMPTY",
                }:
                    raise
                if attempt == 1:
                    return self._provider_inconclusive(
                        snapshot,
                        target_parent_obligation=target_parent_obligation,
                    )
            except (json.JSONDecodeError, ValueError):
                if attempt == 1:
                    return self._provider_inconclusive(
                        snapshot,
                        target_parent_obligation=target_parent_obligation,
                    )
        raise AssertionError("bounded P17 provider loop exhausted unexpectedly")

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
    ) -> ManagerProposal:
        """Narrow provider representation to one legally rooted obligation.

        This method cannot broaden P17 legality. The domain validator in
        research_manager.py remains final authority for every returned ref.
        """
        return self._propose(
            snapshot,
            target_parent_obligation=target_parent_obligation,
            allowed_evidence_refs=allowed_evidence_refs,
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
