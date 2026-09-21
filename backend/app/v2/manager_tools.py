"""Closed governed tool contracts for the Day 6.5 Manager.

No raw SQL, direct DB, arbitrary Python or generic join tools exist in this registry.
The runtime validates state + accepted-authority requirements before any executor is
invoked.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, model_validator

from app.v2.manager_models import (
    ManagerState,
    UserIntentEnvelope,
)
from app.v2.models import FrozenModel


class ManagerToolName(StrEnum):
    RESOLVE_SEMANTICS = "resolve_semantics"
    PROPOSE_ACCEPTANCE = "propose_acceptance"
    RUN_ANALYTICS = "run_analytics"
    RUN_RELATIONSHIP = "run_relationship"
    INSPECT_EVIDENCE = "inspect_evidence"
    REQUEST_CLARIFICATION = "request_clarification"


class ResolveSemanticsArgs(FrozenModel):
    source_refs: tuple[str, ...] = Field(min_length=1)
    target_kind_hints: tuple[
        Literal["metric", "dimension", "filter", "unknown"], ...
    ] = ()

    @model_validator(mode="after")
    def _hint_cardinality(self):
        if self.target_kind_hints and len(self.target_kind_hints) != len(self.source_refs):
            raise ValueError("target_kind_hints boş olmalı veya source_refs ile aynı uzunlukta olmalı")
        return self


class ProposeAcceptanceArgs(FrozenModel):
    envelope: UserIntentEnvelope


class RunAnalyticsArgs(FrozenModel):
    obligation_ids: tuple[str, ...] = Field(min_length=1)
    metric_handles: tuple[str, ...] = Field(min_length=1)
    dimension_handles: tuple[str, ...] = ()
    filter_handles: tuple[str, ...] = ()
    period_handle: str | None = None
    comparison_handle: str | None = None
    ranking_direction: Literal["asc", "desc"] | None = None
    limit: int | None = Field(default=None, ge=1, le=1000)


class RunRelationshipArgs(FrozenModel):
    obligation_id: str
    focus_handles: tuple[str, ...] = Field(min_length=1)
    counterpart_handles: tuple[str, ...] = Field(min_length=1)


class InspectEvidenceArgs(FrozenModel):
    evidence_ref: str


class RequestClarificationArgs(FrozenModel):
    obligation_ids: tuple[str, ...] = ()
    reason: str = Field(min_length=1, max_length=500)


class ManagerToolCall(FrozenModel):
    name: ManagerToolName
    args: dict[str, Any]


@dataclass(frozen=True)
class ManagerToolSpec:
    name: ManagerToolName
    requires_contract: bool
    data_query: bool
    allowed_states: frozenset[ManagerState]
    args_model: type[FrozenModel]


class ManagerToolPolicyError(RuntimeError):
    pass


class ManagerToolRegistry:
    _SPECS = {
        ManagerToolName.RESOLVE_SEMANTICS: ManagerToolSpec(
            name=ManagerToolName.RESOLVE_SEMANTICS,
            requires_contract=False,
            data_query=False,
            allowed_states=frozenset(
                {ManagerState.INITIAL, ManagerState.UNDERSTANDING}
            ),
            args_model=ResolveSemanticsArgs,
        ),
        ManagerToolName.PROPOSE_ACCEPTANCE: ManagerToolSpec(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            requires_contract=False,
            data_query=False,
            allowed_states=frozenset(
                {ManagerState.INITIAL, ManagerState.UNDERSTANDING}
            ),
            args_model=ProposeAcceptanceArgs,
        ),
        ManagerToolName.RUN_ANALYTICS: ManagerToolSpec(
            name=ManagerToolName.RUN_ANALYTICS,
            requires_contract=True,
            data_query=True,
            allowed_states=frozenset(
                {ManagerState.CONTRACT_ACCEPTED, ManagerState.INVESTIGATING}
            ),
            args_model=RunAnalyticsArgs,
        ),
        ManagerToolName.RUN_RELATIONSHIP: ManagerToolSpec(
            name=ManagerToolName.RUN_RELATIONSHIP,
            requires_contract=True,
            data_query=True,
            allowed_states=frozenset(
                {ManagerState.CONTRACT_ACCEPTED, ManagerState.INVESTIGATING}
            ),
            args_model=RunRelationshipArgs,
        ),
        ManagerToolName.INSPECT_EVIDENCE: ManagerToolSpec(
            name=ManagerToolName.INSPECT_EVIDENCE,
            requires_contract=True,
            data_query=False,
            allowed_states=frozenset(
                {ManagerState.CONTRACT_ACCEPTED, ManagerState.INVESTIGATING}
            ),
            args_model=InspectEvidenceArgs,
        ),
        ManagerToolName.REQUEST_CLARIFICATION: ManagerToolSpec(
            name=ManagerToolName.REQUEST_CLARIFICATION,
            requires_contract=False,
            data_query=False,
            allowed_states=frozenset(
                {
                    ManagerState.INITIAL,
                    ManagerState.UNDERSTANDING,
                    ManagerState.CONTRACT_ACCEPTED,
                    ManagerState.INVESTIGATING,
                }
            ),
            args_model=RequestClarificationArgs,
        ),
    }

    def spec(self, name: ManagerToolName) -> ManagerToolSpec:
        try:
            return self._SPECS[name]
        except KeyError as exc:
            raise ManagerToolPolicyError(f"undeclared Manager tool: {name}") from exc

    def validate(
        self,
        call: ManagerToolCall,
        *,
        state: ManagerState,
        has_accepted_contract: bool,
    ) -> FrozenModel:
        spec = self.spec(call.name)
        if state not in spec.allowed_states:
            raise ManagerToolPolicyError(
                f"tool {call.name.value} not allowed in state {state.value}"
            )
        if spec.requires_contract and not has_accepted_contract:
            raise ManagerToolPolicyError(
                f"tool {call.name.value} requires AcceptedTurnContract"
            )
        try:
            return spec.args_model.model_validate(call.args)
        except Exception as exc:
            raise ManagerToolPolicyError(
                f"invalid args for {call.name.value}: {exc}"
            ) from exc

    @property
    def declared_tools(self) -> tuple[str, ...]:
        return tuple(item.value for item in self._SPECS)
