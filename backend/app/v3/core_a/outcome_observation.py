"""Core Closure A2 — governed OutcomeObservation authority.

OutcomeObservation records organizational interpretation over already-governed
analytical provenance. It performs no metric computation and owns no causal truth.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.core_a.action_work import (
    ActionWorkCurrentness,
    ActionWorkError,
    ActionWorkStatus,
    ActionWorkStore,
)
from app.v3.report_document import P20ReportError, ReportCurrentness, ReportDocumentStore
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.db import engine as control_plane_engine
from control_plane.models import OutcomeObservationRecord, ResearchClaimRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class OutcomeError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class OutcomeClassification(StrEnum):
    IMPROVED = "IMPROVED"
    MIXED = "MIXED"
    WORSENED = "WORSENED"
    NO_MATERIAL_CHANGE = "NO_MATERIAL_CHANGE"
    INCONCLUSIVE = "INCONCLUSIVE"


class OutcomeCurrentness(StrEnum):
    CURRENT = "CURRENT"
    SOURCE_WORK_STALE = "SOURCE_WORK_STALE"
    SOURCE_EVIDENCE_STALE = "SOURCE_EVIDENCE_STALE"
    SOURCE_REPORT_STALE = "SOURCE_REPORT_STALE"


class GovernedEvidenceRef(Frozen):
    research_session_id: str = Field(min_length=1)
    obligation_id: str = Field(min_length=1)
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")


class OutcomeObservationDraft(Frozen):
    action_work_id: str = Field(pattern=r"^wrk_[a-f0-9]{24}$")
    action_work_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    evidence: tuple[GovernedEvidenceRef, ...] = Field(min_length=1)
    claim_ids: tuple[str, ...] = ()
    report_id: str | None = Field(default=None, pattern=r"^p20r_[a-f0-9]{24}$")
    baseline_definition: str = Field(min_length=1, max_length=2000)
    baseline_window: str = Field(min_length=1, max_length=500)
    observation_window: str = Field(min_length=1, max_length=500)
    expected_target_ref: str | None = Field(default=None, max_length=1000)
    observed_result_refs: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = ()
    classification: OutcomeClassification

    @model_validator(mode="after")
    def unique_references(self):
        evidence_ids = [item.evidence_id for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("duplicate Evidence references are not allowed")
        if len(self.claim_ids) != len(set(self.claim_ids)):
            raise ValueError("duplicate Claim references are not allowed")
        if len(self.observed_result_refs) != len(set(self.observed_result_refs)):
            raise ValueError("duplicate observed-result references are not allowed")
        return self


class OutcomeObservation(Frozen):
    outcome_id: str = Field(pattern=r"^out_[a-f0-9]{24}$")
    tenant_binding: str
    action_work_id: str
    action_work_fingerprint: str
    decision_brief_id: str
    decision_adoption_id: str
    evidence: tuple[GovernedEvidenceRef, ...]
    claim_ids: tuple[str, ...]
    report_id: str | None = None
    report_fingerprint: str | None = None
    baseline_definition: str
    baseline_window: str
    observation_window: str
    expected_target_ref: str | None = None
    observed_result_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    classification: OutcomeClassification
    source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    outcome_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    observed_at: datetime
    recorder_user_id: str


def _canonical(value: Any, *, code: str) -> tuple[str, str]:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
    except (TypeError, ValueError) as exc:
        raise OutcomeError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise OutcomeError("OUTCOME_TIMEZONE_REQUIRED", "timestamp must be timezone-aware")
    return stamp


def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise OutcomeError("OUTCOME_TENANT_REQUIRED", "tenant binding is required")


def _subject(principal: Principal) -> str:
    value = str(principal.user_id).strip()
    if not value:
        raise OutcomeError("OUTCOME_PRINCIPAL_REQUIRED", "principal identity is required")
    return value


class OutcomeObservationStore:
    def __init__(
        self,
        *,
        work_store: ActionWorkStore,
        research_store: ResearchSessionStore,
        report_store: ReportDocumentStore | None = None,
        db_engine=None,
    ) -> None:
        self._work = work_store
        self._research = research_store
        self._reports = report_store
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _authorize(principal: Principal) -> None:
        try:
            authorize(principal, "outcome:record", "outcome-observation")
        except AuthzError as exc:
            raise OutcomeError(
                "OUTCOME_FORBIDDEN",
                "principal cannot record OutcomeObservation",
            ) from exc

    @staticmethod
    def _hydrate(row: OutcomeObservationRecord) -> OutcomeObservation:
        try:
            evidence = json.loads(row.evidence_refs_json)
            claim_ids = json.loads(row.claim_ids_json)
            observed_refs = json.loads(row.observed_result_refs_json)
            limitations = json.loads(row.limitations_json)
        except json.JSONDecodeError as exc:
            raise OutcomeError("OUTCOME_PERSISTENCE_INVALID", row.outcome_id) from exc
        return OutcomeObservation(
            outcome_id=row.outcome_id,
            tenant_binding=row.tenant_binding,
            action_work_id=row.action_work_id,
            action_work_fingerprint=row.action_work_fingerprint,
            decision_brief_id=row.decision_brief_id,
            decision_adoption_id=row.decision_adoption_id,
            evidence=tuple(GovernedEvidenceRef.model_validate(x) for x in evidence),
            claim_ids=tuple(claim_ids),
            report_id=row.report_id,
            report_fingerprint=row.report_fingerprint,
            baseline_definition=row.baseline_definition,
            baseline_window=row.baseline_window,
            observation_window=row.observation_window,
            expected_target_ref=row.expected_target_ref,
            observed_result_refs=tuple(observed_refs),
            limitations=tuple(limitations),
            classification=OutcomeClassification(row.classification),
            source_fingerprint=row.source_fingerprint,
            outcome_fingerprint=row.outcome_fingerprint,
            observed_at=row.observed_at,
            recorder_user_id=row.recorder_user_id,
        )

    def _validated_sources(
        self,
        *,
        draft: OutcomeObservationDraft,
        principal: Principal,
    ):
        try:
            work = self._work.load(
                action_work_id=draft.action_work_id,
                principal=principal,
            )
            work_state = self._work.currentness(
                action_work_id=draft.action_work_id,
                principal=principal,
            )
        except ActionWorkError as exc:
            raise OutcomeError(
                "OUTCOME_SOURCE_WORK_UNAVAILABLE",
                "ActionWork unavailable in caller scope",
            ) from exc
        if work_state != ActionWorkCurrentness.CURRENT:
            raise OutcomeError("OUTCOME_SOURCE_WORK_STALE", work_state.value)
        if work.status != ActionWorkStatus.COMPLETED:
            raise OutcomeError(
                "OUTCOME_SOURCE_WORK_NOT_COMPLETED",
                work.status.value,
            )
        if work.work_fingerprint != draft.action_work_fingerprint:
            raise OutcomeError(
                "OUTCOME_WORK_FINGERPRINT_MISMATCH",
                work.action_work_id,
            )

        tenant_binding = _tenant(principal)
        principal_subject = _subject(principal)
        evidence_snapshots: list[dict[str, str]] = []
        for ref in draft.evidence:
            try:
                self._research.load(
                    ref.research_session_id,
                    tenant=tenant_binding,
                    principal=principal_subject,
                )
                link = self._research.verified_link(
                    session_id=ref.research_session_id,
                    obligation_id=ref.obligation_id,
                )
            except ResearchPersistenceError as exc:
                raise OutcomeError(
                    "OUTCOME_EVIDENCE_UNAVAILABLE",
                    "verified governed Evidence occurrence unavailable",
                ) from exc
            if link.evidence_id != ref.evidence_id or link.receipt_id != ref.receipt_id:
                raise OutcomeError(
                    "OUTCOME_EVIDENCE_PROVENANCE_MISMATCH",
                    ref.evidence_id,
                )
            evidence_snapshots.append(
                {
                    "research_session_id": ref.research_session_id,
                    "obligation_id": ref.obligation_id,
                    "evidence_id": ref.evidence_id,
                    "receipt_id": ref.receipt_id,
                    "execution_link_id": str(link.id),
                    "native_query_fingerprint": str(link.native_query_fingerprint),
                    "native_result_hash": str(link.native_result_hash),
                }
            )

        for claim_id in draft.claim_ids:
            with Session(self._engine) as db:
                claim = db.get(ResearchClaimRecord, claim_id)
            if claim is None or claim.tenant_binding != tenant_binding:
                raise OutcomeError(
                    "OUTCOME_CLAIM_UNAVAILABLE",
                    "Claim unavailable in caller scope",
                )
            if claim.session_id not in {item.research_session_id for item in draft.evidence}:
                raise OutcomeError(
                    "OUTCOME_CLAIM_LINEAGE_MISMATCH",
                    claim_id,
                )

        report = None
        if draft.report_id is not None:
            if self._reports is None:
                raise OutcomeError(
                    "OUTCOME_REPORT_STORE_REQUIRED",
                    "Report reference cannot be verified",
                )
            try:
                report = self._reports.load(
                    report_id=draft.report_id,
                    principal=principal,
                )
            except P20ReportError as exc:
                raise OutcomeError(
                    "OUTCOME_REPORT_UNAVAILABLE",
                    "Report unavailable in caller scope",
                ) from exc

        return work, evidence_snapshots, report

    def record(
        self,
        *,
        draft: OutcomeObservationDraft,
        principal: Principal,
        now: datetime | None = None,
    ) -> OutcomeObservation:
        self._authorize(principal)
        stamp = _aware(now)
        tenant_binding = _tenant(principal)
        work, evidence_snapshots, report = self._validated_sources(
            draft=draft,
            principal=principal,
        )

        source_identity = {
            "tenant_binding": tenant_binding,
            "action_work_id": work.action_work_id,
            "action_work_fingerprint": work.work_fingerprint,
            "decision_brief_id": work.decision_brief_id,
            "decision_adoption_id": work.decision_adoption_id,
            "evidence": evidence_snapshots,
            "claim_ids": list(draft.claim_ids),
            "report_id": report.report_id if report is not None else None,
            "report_fingerprint": (
                report.report_fingerprint if report is not None else None
            ),
        }
        source_fingerprint = _canonical(
            source_identity,
            code="OUTCOME_SOURCE_NOT_CANONICAL",
        )[1]
        identity = {
            **source_identity,
            "baseline_definition": draft.baseline_definition.strip(),
            "baseline_window": draft.baseline_window.strip(),
            "observation_window": draft.observation_window.strip(),
            "expected_target_ref": (
                draft.expected_target_ref.strip()
                if draft.expected_target_ref
                else None
            ),
            "observed_result_refs": list(draft.observed_result_refs),
            "limitations": list(draft.limitations),
            "classification": draft.classification.value,
        }
        outcome_fingerprint = _canonical(
            identity,
            code="OUTCOME_NOT_CANONICAL",
        )[1]
        outcome_id = "out_" + outcome_fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(OutcomeObservationRecord, outcome_id)
            if existing is not None:
                return self._hydrate(existing)
            row = OutcomeObservationRecord(
                outcome_id=outcome_id,
                tenant_binding=tenant_binding,
                action_work_id=work.action_work_id,
                action_work_fingerprint=work.work_fingerprint,
                decision_brief_id=work.decision_brief_id,
                decision_adoption_id=work.decision_adoption_id,
                evidence_refs_json=_canonical(
                    [item.model_dump(mode="json") for item in draft.evidence],
                    code="OUTCOME_EVIDENCE_REFS_NOT_CANONICAL",
                )[0],
                claim_ids_json=_canonical(
                    list(draft.claim_ids),
                    code="OUTCOME_CLAIM_REFS_NOT_CANONICAL",
                )[0],
                report_id=report.report_id if report is not None else None,
                report_fingerprint=(
                    report.report_fingerprint if report is not None else None
                ),
                baseline_definition=draft.baseline_definition.strip(),
                baseline_window=draft.baseline_window.strip(),
                observation_window=draft.observation_window.strip(),
                expected_target_ref=(
                    draft.expected_target_ref.strip()
                    if draft.expected_target_ref
                    else None
                ),
                observed_result_refs_json=_canonical(
                    list(draft.observed_result_refs),
                    code="OUTCOME_RESULT_REFS_NOT_CANONICAL",
                )[0],
                limitations_json=_canonical(
                    list(draft.limitations),
                    code="OUTCOME_LIMITATIONS_NOT_CANONICAL",
                )[0],
                classification=draft.classification.value,
                source_fingerprint=source_fingerprint,
                outcome_fingerprint=outcome_fingerprint,
                observed_at=stamp,
                recorder_user_id=_subject(principal),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(
        self,
        *,
        outcome_id: str,
        principal: Principal,
    ) -> OutcomeObservation:
        tenant_binding = _tenant(principal)
        with Session(self._engine) as db:
            row = db.get(OutcomeObservationRecord, outcome_id)
            if row is None or row.tenant_binding != tenant_binding:
                raise OutcomeError(
                    "OUTCOME_UNAVAILABLE",
                    "OutcomeObservation unavailable in caller scope",
                )
            return self._hydrate(row)

    def currentness(
        self,
        *,
        outcome_id: str,
        principal: Principal,
    ) -> OutcomeCurrentness:
        outcome = self.load(outcome_id=outcome_id, principal=principal)
        try:
            work_state = self._work.currentness(
                action_work_id=outcome.action_work_id,
                principal=principal,
            )
        except ActionWorkError:
            return OutcomeCurrentness.SOURCE_WORK_STALE
        if work_state != ActionWorkCurrentness.CURRENT:
            return OutcomeCurrentness.SOURCE_WORK_STALE

        tenant_binding = _tenant(principal)
        principal_subject = _subject(principal)
        for ref in outcome.evidence:
            try:
                self._research.load(
                    ref.research_session_id,
                    tenant=tenant_binding,
                    principal=principal_subject,
                )
                link = self._research.verified_link(
                    session_id=ref.research_session_id,
                    obligation_id=ref.obligation_id,
                )
            except ResearchPersistenceError:
                return OutcomeCurrentness.SOURCE_EVIDENCE_STALE
            if link.evidence_id != ref.evidence_id or link.receipt_id != ref.receipt_id:
                return OutcomeCurrentness.SOURCE_EVIDENCE_STALE

        if outcome.report_id is not None:
            if self._reports is None:
                return OutcomeCurrentness.SOURCE_REPORT_STALE
            try:
                state = self._reports.currentness(
                    report_id=outcome.report_id,
                    principal=principal,
                )
            except P20ReportError:
                return OutcomeCurrentness.SOURCE_REPORT_STALE
            if state != ReportCurrentness.CURRENT:
                return OutcomeCurrentness.SOURCE_REPORT_STALE

        return OutcomeCurrentness.CURRENT
