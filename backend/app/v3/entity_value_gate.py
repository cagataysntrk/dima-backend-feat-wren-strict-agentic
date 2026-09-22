"""P11 minimum entity-value adoption gate.

This module is deliberately not an entity resolver. It performs no language
interpretation, candidate retrieval, fuzzy matching, translation, stemming,
morphology, SQL parsing, or physical-field discovery.

It only decides whether an already-proposed value BIND is safe to adopt as
Dima truth under an already-governed semantic scope and current access lens.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class EntityValueDecision(StrEnum):
    BIND = "BIND"
    CLARIFY = "CLARIFY"
    NO_MATCH = "NO_MATCH"
    BLOCKED = "BLOCKED"


ScalarValue = str | int | float | bool


class EntityValueProposal(FrozenModel):
    decision: Literal["BIND", "CLARIFY", "NO_MATCH"]
    semantic_ref: str | None = None
    value: ScalarValue | None = None

    @model_validator(mode="after")
    def _coherent_shape(self):
        if self.decision == "BIND":
            if not self.semantic_ref or self.value is None:
                raise ValueError("BIND requires semantic_ref and value")
        elif self.semantic_ref is not None or self.value is not None:
            raise ValueError(
                "CLARIFY/NO_MATCH proposal must not carry semantic_ref/value"
            )
        return self


class CurrentLensValueEvidence(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    values: tuple[ScalarValue, ...]
    access_lens_ref: str = Field(min_length=1)
    freshness: Literal["CURRENT_USER_RETRIEVAL"]


class EntityValueGateResult(FrozenModel):
    decision: EntityValueDecision
    semantic_ref: str | None = None
    value: ScalarValue | None = None
    reason_code: str = Field(min_length=1)
    model_proposal: EntityValueProposal

    @model_validator(mode="after")
    def _official_shape(self):
        if self.decision == EntityValueDecision.BIND:
            if not self.semantic_ref or self.value is None:
                raise ValueError("official BIND requires semantic_ref and value")
        elif self.semantic_ref is not None or self.value is not None:
            raise ValueError(
                "non-BIND official decision must not carry semantic_ref/value"
            )
        return self


class EntityValueAdoptionGate:
    """Fail-closed adoption boundary for model-proposed value bindings."""

    @classmethod
    def adjudicate(
        cls,
        *,
        proposal: EntityValueProposal,
        allowed_semantic_scopes: tuple[str, ...],
        evidence: tuple[CurrentLensValueEvidence, ...],
        expected_access_lens_ref: str,
    ) -> EntityValueGateResult:
        scopes = tuple(dict.fromkeys(allowed_semantic_scopes))
        if (
            not scopes
            or len(scopes) != len(allowed_semantic_scopes)
            or any(not scope.strip() for scope in scopes)
        ):
            return cls._blocked(proposal, "INVALID_ALLOWED_SCOPE_SET")

        if not expected_access_lens_ref.strip():
            return cls._blocked(proposal, "ACCESS_LENS_REQUIRED")

        evidence_by_scope: dict[str, CurrentLensValueEvidence] = {}
        for item in evidence:
            if item.semantic_ref in evidence_by_scope:
                return cls._blocked(proposal, "DUPLICATE_SCOPE_EVIDENCE")
            if item.access_lens_ref != expected_access_lens_ref:
                return cls._blocked(proposal, "ACCESS_LENS_MISMATCH")
            # The type itself restricts freshness to CURRENT_USER_RETRIEVAL.
            evidence_by_scope[item.semantic_ref] = item

        if set(evidence_by_scope) != set(scopes):
            return cls._blocked(proposal, "SCOPE_EVIDENCE_MISMATCH")

        if proposal.decision == "CLARIFY":
            return EntityValueGateResult(
                decision=EntityValueDecision.CLARIFY,
                reason_code="MODEL_CLARIFICATION",
                model_proposal=proposal,
            )
        if proposal.decision == "NO_MATCH":
            return EntityValueGateResult(
                decision=EntityValueDecision.NO_MATCH,
                reason_code="MODEL_NO_MATCH",
                model_proposal=proposal,
            )

        # DMP-DEC-0027: cognition may propose, but unresolved business scope
        # cannot silently become canonical value authority.
        if len(scopes) != 1:
            return EntityValueGateResult(
                decision=EntityValueDecision.CLARIFY,
                reason_code="AMBIGUOUS_SEMANTIC_SCOPE",
                model_proposal=proposal,
            )

        sole_scope = scopes[0]
        if proposal.semantic_ref != sole_scope:
            return cls._blocked(proposal, "UNAPPROVED_SEMANTIC_SCOPE")

        scoped_evidence = evidence_by_scope[sole_scope]
        if not any(proposal.value == candidate for candidate in scoped_evidence.values):
            return cls._blocked(proposal, "VALUE_NOT_IN_CURRENT_EVIDENCE")

        return EntityValueGateResult(
            decision=EntityValueDecision.BIND,
            semantic_ref=sole_scope,
            value=proposal.value,
            reason_code="EXACT_CURRENT_LENS_EVIDENCE",
            model_proposal=proposal,
        )

    @staticmethod
    def _blocked(
        proposal: EntityValueProposal,
        reason_code: str,
    ) -> EntityValueGateResult:
        return EntityValueGateResult(
            decision=EntityValueDecision.BLOCKED,
            reason_code=reason_code,
            model_proposal=proposal,
        )
