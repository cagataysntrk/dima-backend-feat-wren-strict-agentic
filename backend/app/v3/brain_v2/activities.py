"""Typed Brain V2 activity contracts.

Activities are the only graph boundary allowed to call current Dima owners,
providers or Metabase/Metabot. Results contain refs/revisions only.
"""
from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .state import BrainGraphState, BrainP19Route


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ActivityResult(Frozen):
    activity_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class IntakeActivityResult(ActivityResult):
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    accepted_brief_ref: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    open_requirement_ids: tuple[str, ...] = ()
    material_requirement_ids: tuple[str, ...] = ()
    discovery_required: bool = False


class CanonicalizeActivityResult(ActivityResult):
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    open_requirement_ids: tuple[str, ...] = ()
    material_requirement_ids: tuple[str, ...] = ()
    hypothesis_ids: tuple[str, ...] = ()
    discovery_required: bool = False

    @model_validator(mode="after")
    def discovery_matches_hypotheses(self):
        if self.discovery_required and self.hypothesis_ids:
            raise ValueError("discovery cannot be required when hypotheses already exist")
        return self


class MaterialActivityResult(ActivityResult):
    material_requirement_ids: tuple[str, ...] = ()
    produced_evidence_ids: tuple[str, ...] = ()
    produced_receipt_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def evidence_has_receipt_provenance(self):
        if len(self.produced_evidence_ids) != len(self.produced_receipt_refs):
            raise ValueError("produced Evidence/receipt refs must be paired")
        return self


class EvidenceActivityResult(ActivityResult):
    evidence_revision: int = Field(ge=1)
    evidence_ids: tuple[str, ...] = Field(min_length=1)
    hypothesis_revision: int = Field(ge=0)
    hypothesis_ids: tuple[str, ...] = ()
    discovery_required: bool = False

    @model_validator(mode="after")
    def discovery_matches_hypotheses(self):
        if self.discovery_required and self.hypothesis_ids:
            raise ValueError("discovery cannot remain required after hypotheses exist")
        return self


class P19ActivityResult(ActivityResult):
    assessment_ref: str = Field(pattern=r"^p19a_[a-f0-9]{24}$")
    route: BrainP19Route
    hypothesis_revision: int = Field(ge=0)
    hypothesis_ids: tuple[str, ...] = Field(min_length=1)
    pending_next_test_ref: str | None = Field(
        default=None, pattern=r"^ntr_[a-f0-9]{24}$"
    )

    @model_validator(mode="after")
    def next_test_is_typed(self):
        if self.route == BrainP19Route.NEXT_TEST_REQUIRED:
            if self.pending_next_test_ref is None:
                raise ValueError("NEXT_TEST_REQUIRED requires a typed next-test ref")
        elif self.pending_next_test_ref is not None:
            raise ValueError("non-next-test P19 route must not carry next-test ref")
        return self


class P17ActivityResult(ActivityResult):
    hypothesis_revision: int = Field(ge=0)
    hypothesis_ids: tuple[str, ...] = Field(min_length=1)
    material_requirement_ids: tuple[str, ...] = ()
    discovery_required: bool = False


class ReportActivityResult(ActivityResult):
    report_ref: str = Field(pattern=r"^p20r_[a-f0-9]{24}$")


class BrainActivities(Protocol):
    """Owner adapter surface used by the LangGraph runtime."""

    def intake(self, state: BrainGraphState) -> IntakeActivityResult: ...

    def canonicalize(self, state: BrainGraphState) -> CanonicalizeActivityResult: ...

    def acquire_material(self, state: BrainGraphState) -> MaterialActivityResult: ...

    def admit_evidence(self, state: BrainGraphState) -> EvidenceActivityResult: ...

    def assess_p19(self, state: BrainGraphState) -> P19ActivityResult: ...

    def discover_hypotheses(self, state: BrainGraphState) -> P17ActivityResult: ...

    def design_next_test(self, state: BrainGraphState) -> P17ActivityResult: ...

    def synthesize_report(self, state: BrainGraphState) -> ReportActivityResult: ...
