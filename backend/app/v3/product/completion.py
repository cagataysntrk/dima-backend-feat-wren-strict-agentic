"""Shared Product completion contracts.

This module is orchestration-neutral. Legacy HeadlessProductComposer and the
Brain V2 LangGraph runtime both consume these exact contracts so completion
cannot fork into two truth families.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProductRequirementKind(StrEnum):
    ANALYTICAL = "ANALYTICAL"
    DELIVERABLE = "DELIVERABLE"


class ProductRequirementState(StrEnum):
    VERIFIED = "VERIFIED"
    LIMITED = "LIMITED"
    FULFILLED = "FULFILLED"
    PENDING = "PENDING"


class ProductRequirementDisposition(StrEnum):
    FULFILLED = "FULFILLED"
    LIMITED = "LIMITED"
    UNSUPPORTED = "UNSUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class ProductRequirementCompletion(Frozen):
    requirement_id: str = Field(min_length=1)
    disposition: ProductRequirementDisposition
    fulfilled_by_ref: str | None = None


class ProductCompletionLedger(Frozen):
    entries: tuple[ProductRequirementCompletion, ...]
    process_complete: bool
    requirement_complete: bool
    # Historical compatibility alias: terminal accounting, not fulfillment.
    trusted_complete: bool

    @model_validator(mode="after")
    def exact_identity(self):
        ids = tuple(item.requirement_id for item in self.entries)
        if len(ids) != len(set(ids)):
            raise ValueError("Completion Ledger requirement refs must be unique")
        if self.requirement_complete and not self.process_complete:
            raise ValueError("requirement_complete requires process_complete")
        if self.trusted_complete != self.process_complete:
            raise ValueError("trusted_complete is compatibility alias for process_complete")
        return self


class ProductRequirementFulfillment(Frozen):
    requirement_id: str = Field(min_length=1)
    requirement_kind: ProductRequirementKind
    state: ProductRequirementState
    fulfilled_by_ref: str | None = None
