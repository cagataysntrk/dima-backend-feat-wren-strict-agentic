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


def project_completion_evidence_terminals(
    *,
    session,
    material_groups,
    completed_material_group_ids: tuple[str, ...],
    terminal_requirement_ids: tuple[str, ...],
    direct_requirement_ids: tuple[str, ...],
) -> tuple[CompletionEvidenceTerminal, ...]:
    """Project Completion-owned direct terminals to exact anchor Evidence.

    The function never decides that a requirement is terminal. It only projects
    terminal ids already emitted by Completion through completed MaterialGroups
    to the exact durable P14 Evidence occurrence that supplied their material.
    """

    completed = set(completed_material_group_ids)
    terminal = set(terminal_requirement_ids)
    direct = set(direct_requirement_ids)
    evidence_by_obligation: dict[str, list[object]] = {}
    for item in session.evidence_refs:
        evidence_by_obligation.setdefault(item.obligation_id, []).append(item)

    output: dict[str, CompletionEvidenceTerminal] = {}
    for group in material_groups:
        if group.material_group_id not in completed:
            continue
        source_refs = evidence_by_obligation.get(group.anchor_requirement_id, [])
        if not source_refs:
            # A completed LIMITED group has no Evidence; limitation projection is
            # owned separately and must not be disguised as successful Evidence.
            continue
        source = source_refs[-1]
        for requirement_id in group.consumer_requirement_ids:
            if (
                requirement_id == group.anchor_requirement_id
                or requirement_id not in terminal
                or requirement_id not in direct
            ):
                continue
            output[requirement_id] = CompletionEvidenceTerminal(
                requirement_id=requirement_id,
                source_obligation_id=group.anchor_requirement_id,
                evidence_id=source.evidence_id,
                receipt_id=source.receipt_id,
                material_group_id=group.material_group_id,
                material_fingerprint=group.material_fingerprint,
                scope_version_id=group.scope_version_id,
            )
    return tuple(output[key] for key in sorted(output))
