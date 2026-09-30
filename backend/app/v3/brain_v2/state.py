"""Reference-only operational state for Dima Brain V2.

LangGraph owns orchestration progress only. Canonical Scope, Evidence, Hypothesis,
Report and Decision truth remains in the existing Dima domain stores.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BrainWorkflowStatus(StrEnum):
    NEW = "NEW"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    SUFFICIENT = "SUFFICIENT"
    INCONCLUSIVE = "INCONCLUSIVE"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


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

    evidence_revision: int = Field(default=0, ge=0)
    evidence_ids: tuple[str, ...] = ()

    hypothesis_revision: int = Field(default=0, ge=0)
    hypothesis_ids: tuple[str, ...] = ()

    latest_p19_assessment_ref: str | None = Field(
        default=None, pattern=r"^p19a_[a-f0-9]{24}$"
    )
    pending_next_test_ref: str | None = Field(
        default=None, pattern=r"^ntr_[a-f0-9]{24}$"
    )
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
            "evidence_ids": self.evidence_ids,
            "hypothesis_ids": self.hypothesis_ids,
            "activity_fingerprints": self.activity_fingerprints,
        }
        for name, values in unique_fields.items():
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must contain unique refs")

        if any(not value for value in self.open_requirement_ids):
            raise ValueError("open requirement refs must be non-empty")
        if any(not value for value in self.material_requirement_ids):
            raise ValueError("material requirement refs must be non-empty")
        if any(not value.startswith("evi_") for value in self.evidence_ids):
            raise ValueError("evidence refs must use canonical Evidence identity")
        if any(not value for value in self.hypothesis_ids):
            raise ValueError("hypothesis refs must be non-empty")
        if any(
            len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value)
            for value in self.activity_fingerprints
        ):
            raise ValueError("activity fingerprints must be sha256 hex")
        return self
