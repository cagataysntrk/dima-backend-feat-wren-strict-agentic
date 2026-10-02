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
    investigation_requirement_ids: tuple[str, ...] = ()
    follow_verified_material_goal_ids: tuple[str, ...] = ()
    discovery_required: bool = False


class CanonicalizeActivityResult(ActivityResult):
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    open_requirement_ids: tuple[str, ...] = ()
    material_requirement_ids: tuple[str, ...] = ()
    hypothesis_ids: tuple[str, ...] = ()
    discovery_required: bool = False



class RequirementPlanActivityResult(ActivityResult):
    material_group_ids: tuple[str, ...] = ()
    direct_requirement_ids: tuple[str, ...] = ()
    relationship_requirement_ids: tuple[str, ...] = ()
    root_cause_requirement_ids: tuple[str, ...] = ()
    report_requirement_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def analytical_owners_are_disjoint(self):
        families = (
            self.direct_requirement_ids,
            self.relationship_requirement_ids,
            self.root_cause_requirement_ids,
        )
        flattened = tuple(item for family in families for item in family)
        if len(flattened) != len(set(flattened)):
            raise ValueError("analytical requirement owner families must be disjoint")
        if len(self.material_group_ids) != len(set(self.material_group_ids)):
            raise ValueError("material group refs must be unique")
        return self


class MaterialGroupActivityResult(ActivityResult):
    material_group_id: str = Field(pattern=r"^mg_[a-f0-9]{24}$")
    consumer_requirement_ids: tuple[str, ...] = Field(min_length=1)
    produced_evidence_ids: tuple[str, ...] = ()
    produced_receipt_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def evidence_has_receipt_provenance(self):
        if len(self.produced_evidence_ids) != len(self.produced_receipt_refs):
            raise ValueError("MaterialGroup Evidence/receipt refs must be paired")
        if len(self.consumer_requirement_ids) != len(
            set(self.consumer_requirement_ids)
        ):
            raise ValueError("MaterialGroup consumer refs must be unique")
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



class CandidateProjectionActivityResult(ActivityResult):
    """Deterministic candidate identities materialized into canonical P19 hypotheses."""

    hypothesis_revision: int = Field(ge=0)
    hypothesis_ids: tuple[str, ...] = ()
    candidate_semantic_ids: tuple[str, ...] = ()
    candidate_count: int = Field(ge=0)

    @model_validator(mode="after")
    def count_matches_identity_set(self):
        if len(self.hypothesis_ids) != len(set(self.hypothesis_ids)):
            raise ValueError("projected hypothesis refs must be unique")
        if len(self.candidate_semantic_ids) != len(set(self.candidate_semantic_ids)):
            raise ValueError("projected candidate semantic refs must be unique")
        if any(not value for value in self.candidate_semantic_ids):
            raise ValueError("projected candidate semantic refs must be non-empty")
        if self.candidate_count != len(self.hypothesis_ids):
            raise ValueError("candidate count must match projected hypothesis refs")
        if self.candidate_count != len(self.candidate_semantic_ids):
            raise ValueError("candidate count must match projected semantic refs")
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
    hypothesis_ids: tuple[str, ...] = ()
    material_requirement_ids: tuple[str, ...] = ()
    discovery_required: bool = False
    produced_evidence_ids: tuple[str, ...] = ()
    produced_receipt_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def coherent_transition(self):
        if len(self.produced_evidence_ids) != len(self.produced_receipt_refs):
            raise ValueError("P17 produced Evidence/receipt refs must be paired")
        return self


class P18ActivityResult(ActivityResult):
    requirement_id: str = Field(min_length=1)
    claim_ref: str = Field(pattern=r"^clm_[a-f0-9]{24}$")
    policy_use_ref: str = Field(pattern=r"^bru_[a-f0-9]{24}$")


class CompletionActivityResult(ActivityResult):
    completion_revision: int = Field(ge=1)
    terminal_requirement_ids: tuple[str, ...] = ()
    requirement_complete: bool
    report_required: bool

    @model_validator(mode="after")
    def terminal_refs_are_unique(self):
        if len(self.terminal_requirement_ids) != len(
            set(self.terminal_requirement_ids)
        ):
            raise ValueError("terminal requirement refs must be unique")
        return self


class ReportActivityResult(ActivityResult):
    report_ref: str = Field(pattern=r"^p20r_[a-f0-9]{24}$")


class BrainActivities(Protocol):
    """Owner adapter surface used by the LangGraph runtime."""

    def intake(self, state: BrainGraphState) -> IntakeActivityResult: ...

    def canonicalize(self, state: BrainGraphState) -> CanonicalizeActivityResult: ...

    def plan_requirements(
        self, state: BrainGraphState
    ) -> RequirementPlanActivityResult: ...

    def acquire_material_group(
        self, state: BrainGraphState
    ) -> MaterialGroupActivityResult: ...

    def acquire_material(self, state: BrainGraphState) -> MaterialActivityResult: ...

    def admit_evidence(self, state: BrainGraphState) -> EvidenceActivityResult: ...

    def adjudicate_relationship(
        self, state: BrainGraphState
    ) -> P18ActivityResult: ...

    def evaluate_completion(
        self, state: BrainGraphState
    ) -> CompletionActivityResult: ...

    def project_candidates(
        self, state: BrainGraphState
    ) -> CandidateProjectionActivityResult: ...

    def assess_p19(self, state: BrainGraphState) -> P19ActivityResult: ...

    def discover_hypotheses(self, state: BrainGraphState) -> P17ActivityResult: ...

    def design_next_test(self, state: BrainGraphState) -> P17ActivityResult: ...

    def synthesize_report(self, state: BrainGraphState) -> ReportActivityResult: ...
