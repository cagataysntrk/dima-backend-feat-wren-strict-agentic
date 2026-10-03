"""Typed Completion -> downstream-owner terminal authority projections.

Completion owns USER_MUST terminal accounting.  These immutable projections carry
only the already-governed source identity needed by a downstream owner such as
P20; they do not execute analytics or manufacture Evidence.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CompletionEvidenceTerminal(Frozen):
    """One direct USER_MUST terminalized from a completed shared MaterialGroup."""

    requirement_id: str = Field(min_length=1)
    source_obligation_id: str = Field(min_length=1)
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")
    material_group_id: str = Field(pattern=r"^mg_[a-f0-9]{24}$")
    material_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")

    @model_validator(mode="after")
    def source_is_explicit(self):
        if self.requirement_id == self.source_obligation_id:
            raise ValueError(
                "shared-material completion projection requires a distinct source obligation"
            )
        return self
