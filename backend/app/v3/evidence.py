"""Dima-owned receipt and evidence contracts for v3."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class EvidenceState(StrEnum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    VERIFIED = "VERIFIED"
    INVALIDATED = "INVALIDATED"
    STALE = "STALE"


class DimaQueryReceipt(FrozenModel):
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")
    authority_id: str = Field(min_length=1)
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    resolved_intent_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    canonical_query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    canonical_query_representation: dict[str, Any] | None = None
    ephemeral_query_handle: str | None = None
    principal_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    execution_access_fingerprint: str | None = None
    semantic_context_version: str = Field(min_length=1)
    resource_entity_ids: tuple[str, ...] = ()
    resource_fingerprints: tuple[str, ...] = ()
    substrate: str = Field(min_length=1)
    substrate_runtime_version: str | None = None
    substrate_image_digest: str | None = None
    legacy_query_contract_ref: str | None = None
    result_hash: str | None = None
    row_count: int = Field(ge=0)
    warnings: tuple[str, ...] = ()


class EvidenceArtifact(FrozenModel):
    artifact_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    authority_id: str = Field(min_length=1)
    obligation_ids: tuple[str, ...] = ()
    query_receipt_refs: tuple[str, ...] = ()
    legacy_query_contract_refs: tuple[str, ...] = ()
    evidence_kind: str = Field(min_length=1)
    state: EvidenceState = EvidenceState.PENDING
    payload: dict[str, Any] = Field(default_factory=dict)
    limitations: tuple[str, ...] = ()

    @property
    def verified(self) -> bool:
        return self.state == EvidenceState.VERIFIED
