"""Dima-owned receipt and evidence contracts for v3."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    authority_kind: Literal["standard_analytics", "research_material"] = "standard_analytics"
    authority_id: str = Field(min_length=1)
    obligation_ids: tuple[str, ...] = ()
    tenant_id: str | None = None
    principal_id: str | None = None
    semantic_refs: tuple[str, ...] = ()
    # Standard-only identities. Native Research deliberately does not pretend it
    # owns a Standard projection or ResolvedAnalyticsIntent.
    projection_hash: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    resolved_intent_hash: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    # Research-native occurrence provenance.
    research_session_id: str | None = Field(
        default=None,
        pattern=r"^rs_[a-f0-9]{24}$",
    )
    native_subject_ref: str | None = None
    native_conversation_id: UUID | None = None
    native_query_id: str | None = None
    native_query_provenance_ref: str | None = None
    native_result_provenance_ref: str | None = None
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
    engine_repository: str | None = None
    engine_revision_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    engine_upstream_base_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    engine_runtime_tag: str | None = None
    engine_build_identity: str | None = None
    engine_image_identity: str | None = None
    engine_runtime_instance_id: UUID | None = None
    database_id: str | None = None
    executed_at: datetime | None = None
    legacy_query_contract_ref: str | None = None
    result_hash: str | None = None
    row_count: int = Field(ge=0)
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _authority_specific_identity(self):
        if self.authority_kind == "standard_analytics":
            if self.projection_hash is None or self.resolved_intent_hash is None:
                raise ValueError(
                    "standard analytics receipt requires projection/resolved intent identity"
                )
            return self

        if self.projection_hash is not None or self.resolved_intent_hash is not None:
            raise ValueError(
                "research material receipt must not populate Standard projection/intent fields"
            )
        required = {
            "research_session_id": self.research_session_id,
            "native_subject_ref": self.native_subject_ref,
            "native_conversation_id": self.native_conversation_id,
            "native_query_id": self.native_query_id,
            "native_query_provenance_ref": self.native_query_provenance_ref,
            "native_result_provenance_ref": self.native_result_provenance_ref,
        }
        missing = sorted(name for name, value in required.items() if value is None or value == "")
        if missing:
            raise ValueError(
                "research material receipt missing native provenance: "
                + ", ".join(missing)
            )
        if self.execution_access_fingerprint is not None:
            raise ValueError(
                "research material receipt must not manufacture a P10 access fingerprint"
            )
        return self


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
