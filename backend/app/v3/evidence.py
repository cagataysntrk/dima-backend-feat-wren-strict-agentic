"""Dima-owned receipt and evidence contracts for v3."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

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
    receipt_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    execution_id: str | None = None
    step_role: Literal["primary", "base", "reference"] | None = None
    authority_id: str = Field(min_length=1)
    obligation_ids: tuple[str, ...] = ()
    tenant_id: str | None = None
    principal_id: str | None = None
    semantic_refs: tuple[str, ...] = ()
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    resolved_intent_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    canonical_query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    canonical_query_representation: dict[str, Any] | None = None
    ephemeral_query_handle: str | None = None
    principal_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    execution_access_fingerprint: str | None = None
    access_attestation_refs: tuple[str, ...] = ()
    semantic_context_version: str = Field(min_length=1)
    resource_entity_ids: tuple[str, ...] = ()
    resource_fingerprints: tuple[str, ...] = ()
    substrate: str = Field(min_length=1)
    substrate_runtime_version: str | None = None
    substrate_image_digest: str | None = None
    database_id: str | None = None
    executed_at: datetime | None = None
    legacy_query_contract_ref: str | None = None
    result_hash: str | None = None
    row_count: int = Field(ge=0)
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


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
