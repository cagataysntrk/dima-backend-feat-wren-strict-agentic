"""Reference-only operational state for Dima Brain V2.

LangGraph owns orchestration progress only. Canonical Scope, Evidence, Hypothesis,
Report and Decision truth remains in the existing Dima domain stores.
"""
from __future__ import annotations

from enum import StrEnum
from typing import TypedDict

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BrainWorkflowStatus(StrEnum):
    NEW = "NEW"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    SUFFICIENT = "SUFFICIENT"
    INCONCLUSIVE = "INCONCLUSIVE"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class BrainP19Route(StrEnum):
    SUFFICIENT = "SUFFICIENT"
    NEXT_TEST_REQUIRED = "NEXT_TEST_REQUIRED"
    INCONCLUSIVE = "INCONCLUSIVE"


class BrainGraphState(BaseModel):
    """LangGraph checkpoint state containing refs/revisions, never domain truth bodies."""

    model_config = ConfigDict(extra="forbid")

    thread_id: str = Field(min_length=1, max_length=200)
    tenant_binding: str = Field(min_length=1, max_length=240)
    principal_ref: str = Field(min_length=1, max_length=240)

    # Only the current turn may be carried through orchestration. Historical
    # transcript remains outside graph state.
    current_user_input: str | None = Field(default=None, max_length=16000)

    research_session_id: str | None = Field(
        default=None, pattern=r"^rs_[a-f0-9]{24}$"
    )
    accepted_brief_ref: str | None = Field(default=None, min_length=1, max_length=240)
    scope_version_id: str | None = Field(
        default=None, pattern=r"^scope_v[1-9][0-9]*$"
    )

    open_requirement_ids: tuple[str, ...] = ()
    material_requirement_ids: tuple[str, ...] = ()
    material_group_ids: tuple[str, ...] = ()
    completed_material_group_ids: tuple[str, ...] = ()
    active_material_group_id: str | None = Field(
        default=None, pattern=r"^mg_[a-f0-9]{24}$"
    )
    active_requirement_id: str | None = Field(default=None, min_length=1)
    terminal_requirement_ids: tuple[str, ...] = ()
    direct_requirement_ids: tuple[str, ...] = ()
    relationship_requirement_ids: tuple[str, ...] = ()
    root_cause_requirement_ids: tuple[str, ...] = ()
    report_requirement_ids: tuple[str, ...] = ()
    investigation_requirement_ids: tuple[str, ...] = ()
    follow_verified_material_goal_ids: tuple[str, ...] = ()
    pending_evidence_ids: tuple[str, ...] = ()
    pending_receipt_refs: tuple[str, ...] = ()

    evidence_revision: int = Field(default=0, ge=0)
    evidence_ids: tuple[str, ...] = ()

    hypothesis_revision: int = Field(default=0, ge=0)
    hypothesis_ids: tuple[str, ...] = ()
    candidate_semantic_ids: tuple[str, ...] = ()
    discovery_required: bool = False
    discovery_turns: int = Field(default=0, ge=0)
    max_discovery_turns: int = Field(default=3, ge=1, le=6)

    latest_p19_assessment_ref: str | None = Field(
        default=None, pattern=r"^p19a_[a-f0-9]{24}$"
    )
    pending_next_test_ref: str | None = Field(
        default=None, pattern=r"^ntr_[a-f0-9]{24}$"
    )
    latest_p19_route: BrainP19Route | None = None
    adaptive_reentries: int = Field(default=0, ge=0)
    max_adaptive_reentries: int = Field(default=1, ge=0, le=4)

    p18_requirement_ids: tuple[str, ...] = ()
    p18_result_refs: tuple[str, ...] = ()
    p18_claim_refs: tuple[str, ...] = ()
    p18_policy_use_refs: tuple[str, ...] = ()
    completion_revision: int = Field(default=0, ge=0)
    presentation_revision: int = Field(default=0, ge=0)

    report_ref: str | None = Field(
        default=None, pattern=r"^p20r_[a-f0-9]{24}$"
    )

    workflow_status: BrainWorkflowStatus = BrainWorkflowStatus.NEW
    last_completed_node: str | None = Field(default=None, max_length=120)

    activity_fingerprints: tuple[str, ...] = ()
    telemetry_ref: str | None = Field(default=None, min_length=1, max_length=240)

    @model_validator(mode="after")
    def reference_state_is_coherent(self):
        unique_fields = {
            "open_requirement_ids": self.open_requirement_ids,
            "material_requirement_ids": self.material_requirement_ids,
            "material_group_ids": self.material_group_ids,
            "completed_material_group_ids": self.completed_material_group_ids,
            "terminal_requirement_ids": self.terminal_requirement_ids,
            "direct_requirement_ids": self.direct_requirement_ids,
            "relationship_requirement_ids": self.relationship_requirement_ids,
            "root_cause_requirement_ids": self.root_cause_requirement_ids,
            "report_requirement_ids": self.report_requirement_ids,
            "p18_requirement_ids": self.p18_requirement_ids,
            "p18_result_refs": self.p18_result_refs,
            "p18_claim_refs": self.p18_claim_refs,
            "p18_policy_use_refs": self.p18_policy_use_refs,
            "investigation_requirement_ids": self.investigation_requirement_ids,
            "follow_verified_material_goal_ids": (
                self.follow_verified_material_goal_ids
            ),
            "pending_evidence_ids": self.pending_evidence_ids,
            "pending_receipt_refs": self.pending_receipt_refs,
            "evidence_ids": self.evidence_ids,
            "hypothesis_ids": self.hypothesis_ids,
            "candidate_semantic_ids": self.candidate_semantic_ids,
            "activity_fingerprints": self.activity_fingerprints,
        }
        for name, values in unique_fields.items():
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must contain unique refs")

        if any(not value for value in self.open_requirement_ids):
            raise ValueError("open requirement refs must be non-empty")
        if any(not value for value in self.material_requirement_ids):
            raise ValueError("material requirement refs must be non-empty")
        if any(not value.startswith("mg_") for value in self.material_group_ids):
            raise ValueError("material group refs must use canonical identity")
        if any(
            value not in set(self.material_group_ids)
            for value in self.completed_material_group_ids
        ):
            raise ValueError("completed material group must belong to current plan")
        if (
            self.active_material_group_id is not None
            and self.active_material_group_id not in set(self.material_group_ids)
        ):
            raise ValueError("active material group must belong to current plan")
        analytical_families = (
            self.direct_requirement_ids,
            self.relationship_requirement_ids,
            self.root_cause_requirement_ids,
        )
        analytical_refs = tuple(
            item for family in analytical_families for item in family
        )
        if len(analytical_refs) != len(set(analytical_refs)):
            raise ValueError("analytical requirement owner refs must be disjoint")
        if not set(analytical_refs).issubset(set(self.open_requirement_ids)):
            raise ValueError("analytical owner refs must belong to current requirements")
        if not set(self.report_requirement_ids).issubset(
            set(self.open_requirement_ids)
        ):
            raise ValueError("report owner refs must belong to current requirements")
        if len(self.p18_requirement_ids) != len(self.p18_result_refs):
            raise ValueError("P18 requirement/result refs must be paired")
        if len(self.p18_requirement_ids) != len(self.p18_claim_refs):
            raise ValueError("P18 requirement/claim refs must be paired")
        if len(self.p18_requirement_ids) != len(self.p18_policy_use_refs):
            raise ValueError("P18 requirement/policy-use refs must be paired")
        if any(not value.startswith("p18r_") for value in self.p18_result_refs):
            raise ValueError("P18 result refs must use canonical identity")
        if any(not value.startswith("clm_") for value in self.p18_claim_refs):
            raise ValueError("P18 claim refs must use canonical identity")
        if any(not value.startswith("bru_") for value in self.p18_policy_use_refs):
            raise ValueError("P18 policy-use refs must use canonical identity")
        if len(self.pending_evidence_ids) != len(self.pending_receipt_refs):
            raise ValueError("pending Evidence/receipt refs must be paired")
        if any(not value.startswith("evi_") for value in self.evidence_ids):
            raise ValueError("evidence refs must use canonical Evidence identity")
        if any(not value for value in self.hypothesis_ids):
            raise ValueError("hypothesis refs must be non-empty")
        if any(not value for value in self.candidate_semantic_ids):
            raise ValueError("candidate semantic refs must be non-empty")
        if any(
            len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value)
            for value in self.activity_fingerprints
        ):
            raise ValueError("activity fingerprints must be sha256 hex")
        if self.adaptive_reentries > self.max_adaptive_reentries:
            raise ValueError("adaptive re-entry count exceeds configured bound")
        if self.discovery_turns > self.max_discovery_turns:
            raise ValueError("discovery turn count exceeds configured bound")
        return self


class BrainStatePayload(TypedDict, total=False):
    """LangGraph transport schema. BrainGraphState remains the validator."""

    thread_id: str
    tenant_binding: str
    principal_ref: str
    current_user_input: str | None
    research_session_id: str | None
    accepted_brief_ref: str | None
    scope_version_id: str | None
    open_requirement_ids: tuple[str, ...]
    material_requirement_ids: tuple[str, ...]
    material_group_ids: tuple[str, ...]
    completed_material_group_ids: tuple[str, ...]
    active_material_group_id: str | None
    active_requirement_id: str | None
    terminal_requirement_ids: tuple[str, ...]
    direct_requirement_ids: tuple[str, ...]
    relationship_requirement_ids: tuple[str, ...]
    root_cause_requirement_ids: tuple[str, ...]
    report_requirement_ids: tuple[str, ...]
    investigation_requirement_ids: tuple[str, ...]
    follow_verified_material_goal_ids: tuple[str, ...]
    pending_evidence_ids: tuple[str, ...]
    pending_receipt_refs: tuple[str, ...]
    evidence_revision: int
    evidence_ids: tuple[str, ...]
    hypothesis_revision: int
    hypothesis_ids: tuple[str, ...]
    candidate_semantic_ids: tuple[str, ...]
    discovery_required: bool
    discovery_turns: int
    max_discovery_turns: int
    latest_p19_assessment_ref: str | None
    pending_next_test_ref: str | None
    latest_p19_route: BrainP19Route | None
    adaptive_reentries: int
    max_adaptive_reentries: int
    p18_requirement_ids: tuple[str, ...]
    p18_result_refs: tuple[str, ...]
    p18_claim_refs: tuple[str, ...]
    p18_policy_use_refs: tuple[str, ...]
    completion_revision: int
    presentation_revision: int
    report_ref: str | None
    workflow_status: BrainWorkflowStatus
    last_completed_node: str | None
    activity_fingerprints: tuple[str, ...]
    telemetry_ref: str | None
