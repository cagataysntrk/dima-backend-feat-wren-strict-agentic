"""Day 7 Research state projection for result-aware cognition.

This module is a read-model only.  It does not mint authority, semantic handles,
obligations or evidence.  Its sole purpose is to keep accumulated Research state
separate from the latest execution delta shown to the Manager.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from app.v2.manager_models import (
    ObligationOrigin,
    ObligationStatus,
    ResearchRunTerminal,
)
from app.v2.models import EvidenceArtifact, FrozenModel


class ResearchDeltaAvailability(StrEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class ResearchEvidenceDelta(FrozenModel):
    evidence_ref: str
    availability: ResearchDeltaAvailability
    inspected: bool
    verified: bool | None = None
    task_id: str | None = None
    obligation_ids: tuple[str, ...] = ()
    evidence_kind: str | None = None
    query_contract_refs: tuple[str, ...] = ()
    query_count: int | None = None
    row_count: int | None = None
    limitations: tuple[str, ...] = ()


class ResearchObligationState(FrozenModel):
    obligation_id: str
    origin: str
    capability: str
    status: str
    evidence_refs: tuple[str, ...] = ()
    blocker: str | None = None


class ResearchStateView(FrozenModel):
    run_id: str
    accepted_contract_id: str | None = None
    lineage_id: str | None = None
    terminal_status: ResearchRunTerminal | None = None
    obligations: tuple[ResearchObligationState, ...] = ()
    verified_user_must_ids: tuple[str, ...] = ()
    remaining_user_must_ids: tuple[str, ...] = ()
    accumulated_evidence_refs: tuple[str, ...] = ()
    inspected_evidence_refs: tuple[str, ...] = ()
    latest_delta: ResearchEvidenceDelta | None = None


def _bounded_counts(evidence: EvidenceArtifact) -> tuple[int | None, int | None]:
    payload: dict[str, Any] = evidence.payload or {}
    query_count = payload.get("query_count")
    executions = tuple(payload.get("executions") or ())
    row_count = (
        sum(int(item.get("row_count") or 0) for item in executions)
        if executions
        else None
    )
    return (
        int(query_count) if isinstance(query_count, int) else None,
        row_count,
    )


def build_research_state_view(*, runtime, evidence_store=None) -> ResearchStateView:
    """Project current authoritative runtime into accumulated state + latest delta.

    Evidence-store failure is represented as UNAVAILABLE. It is never converted into
    "no evidence" or a semantic gap.
    """

    ledger = runtime.ledger
    obligations: list[ResearchObligationState] = []
    verified_user_must: list[str] = []
    remaining_user_must: list[str] = []

    if ledger is not None:
        for item in ledger.items:
            obligations.append(
                ResearchObligationState(
                    obligation_id=item.obligation_id,
                    origin=item.origin.value,
                    capability=item.capability_key.value,
                    status=item.status.value,
                    evidence_refs=item.evidence_refs,
                    blocker=item.blocker,
                )
            )
            if (
                item.origin == ObligationOrigin.USER_MUST
                and item.status != ObligationStatus.SUPERSEDED
            ):
                if item.status == ObligationStatus.VERIFIED:
                    verified_user_must.append(item.obligation_id)
                elif item.status not in {
                    ObligationStatus.BLOCKED_DATA_GAP,
                    ObligationStatus.LIMITED,
                    ObligationStatus.UNSUPPORTED,
                }:
                    remaining_user_must.append(item.obligation_id)

    latest_ref = getattr(runtime.snapshot, "latest_evidence_ref", None)
    inspected_refs = tuple(
        getattr(runtime.snapshot, "inspected_evidence_refs", ()) or ()
    )
    latest_delta = None

    if latest_ref is not None:
        artifact = None
        if evidence_store is not None:
            try:
                artifact = evidence_store.get(latest_ref)
            except Exception:
                artifact = None

        if isinstance(artifact, EvidenceArtifact):
            query_count, row_count = _bounded_counts(artifact)
            latest_delta = ResearchEvidenceDelta(
                evidence_ref=latest_ref,
                availability=ResearchDeltaAvailability.AVAILABLE,
                inspected=latest_ref in inspected_refs,
                verified=artifact.verified,
                task_id=artifact.task_id,
                obligation_ids=artifact.obligation_ids,
                evidence_kind=artifact.evidence_kind,
                query_contract_refs=artifact.query_contract_refs,
                query_count=query_count,
                row_count=row_count,
                limitations=artifact.limitations,
            )
        else:
            latest_delta = ResearchEvidenceDelta(
                evidence_ref=latest_ref,
                availability=ResearchDeltaAvailability.UNAVAILABLE,
                inspected=latest_ref in inspected_refs,
            )

    return ResearchStateView(
        run_id=runtime.snapshot.run_id,
        accepted_contract_id=runtime.snapshot.accepted_contract_id,
        lineage_id=runtime.snapshot.lineage_id,
        terminal_status=runtime.snapshot.terminal_status,
        obligations=tuple(obligations),
        verified_user_must_ids=tuple(verified_user_must),
        remaining_user_must_ids=tuple(remaining_user_must),
        accumulated_evidence_refs=runtime.snapshot.evidence_refs,
        inspected_evidence_refs=inspected_refs,
        latest_delta=latest_delta,
    )
