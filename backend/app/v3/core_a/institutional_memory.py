"""Core Closure A3 — institutional precedent memory.

Memory indexes exact sealed artifacts plus context. It owns no Evidence, Claim,
RootCause, Report, Decision, or Outcome truth.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.core_a.action_work import ActionWorkCurrentness, ActionWorkError, ActionWorkStore
from app.v3.core_a.outcome_observation import OutcomeCurrentness, OutcomeError, OutcomeObservationStore
from app.v3.decision_adoption import AdoptionCurrentness, AdoptionError, DecisionAdoptionStore
from app.v3.decision_intelligence import DecisionBriefCurrentness, DecisionBriefStore, P21DecisionError
from app.v3.report_document import P20ReportError, ReportCurrentness, ReportDocumentStore
from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.db import engine as control_plane_engine
from control_plane.models import InstitutionalMemoryEntryRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MemoryError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class MemoryRole(StrEnum):
    CURRENT_CONTEXT = "CURRENT_CONTEXT"
    HISTORICAL_PRECEDENT = "HISTORICAL_PRECEDENT"


class MemoryCurrentness(StrEnum):
    CURRENT_CONTEXT = "CURRENT_CONTEXT"
    STALE_CONTEXT = "STALE_CONTEXT"
    HISTORICAL_PRECEDENT = "HISTORICAL_PRECEDENT"


class MemorySourceKind(StrEnum):
    ACTION_WORK = "ACTION_WORK"
    OUTCOME = "OUTCOME"
    DECISION_ADOPTION = "DECISION_ADOPTION"
    DECISION_BRIEF = "DECISION_BRIEF"
    REPORT = "REPORT"


class MemorySourceRef(Frozen):
    kind: MemorySourceKind
    artifact_id: str = Field(min_length=1)
    artifact_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class InstitutionalMemoryDraft(Frozen):
    role: MemoryRole
    problem_type: str = Field(min_length=1, max_length=300)
    domain: str = Field(min_length=1, max_length=300)
    entity_refs: tuple[str, ...] = ()
    metric_refs: tuple[str, ...] = ()
    source_refs: tuple[MemorySourceRef, ...] = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=10000)
    limitations: tuple[str, ...] = ()
    precedent_of_memory_id: str | None = Field(
        default=None,
        pattern=r"^mem_[a-f0-9]{24}$",
    )

    @model_validator(mode="after")
    def unique_refs(self):
        identities = [(item.kind.value, item.artifact_id) for item in self.source_refs]
        if len(identities) != len(set(identities)):
            raise ValueError("duplicate memory source references are not allowed")
        if len(self.entity_refs) != len(set(self.entity_refs)):
            raise ValueError("duplicate entity refs are not allowed")
        if len(self.metric_refs) != len(set(self.metric_refs)):
            raise ValueError("duplicate metric refs are not allowed")
        return self


class InstitutionalMemoryEntry(Frozen):
    memory_id: str = Field(pattern=r"^mem_[a-f0-9]{24}$")
    tenant_binding: str
    role: MemoryRole
    problem_type: str
    domain: str
    entity_refs: tuple[str, ...]
    metric_refs: tuple[str, ...]
    source_refs: tuple[MemorySourceRef, ...]
    summary: str
    limitations: tuple[str, ...]
    precedent_of_memory_id: str | None = None
    source_set_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    memory_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime
    indexed_by_user_id: str


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
        raise MemoryError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise MemoryError("MEMORY_TENANT_REQUIRED", "tenant binding is required")


def _subject(principal: Principal) -> str:
    value = str(principal.user_id).strip()
    if not value:
        raise MemoryError("MEMORY_PRINCIPAL_REQUIRED", "principal identity is required")
    return value


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise MemoryError("MEMORY_TIMEZONE_REQUIRED", "timestamp must be timezone-aware")
    return stamp


class InstitutionalMemoryStore:
    def __init__(
        self,
        *,
        work_store: ActionWorkStore | None = None,
        outcome_store: OutcomeObservationStore | None = None,
        adoption_store: DecisionAdoptionStore | None = None,
        decision_store: DecisionBriefStore | None = None,
        report_store: ReportDocumentStore | None = None,
        db_engine=None,
    ) -> None:
        self._work = work_store
        self._outcomes = outcome_store
        self._adoptions = adoption_store
        self._decisions = decision_store
        self._reports = report_store
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _authorize_write(principal: Principal) -> None:
        try:
            authorize(principal, "memory:write", "institutional-memory")
        except AuthzError as exc:
            raise MemoryError("MEMORY_FORBIDDEN", "principal cannot index memory") from exc

    @staticmethod
    def _authorize_read(principal: Principal) -> None:
        try:
            authorize(principal, "memory:read", "institutional-memory")
        except AuthzError as exc:
            raise MemoryError("MEMORY_FORBIDDEN", "principal cannot read memory") from exc

    @staticmethod
    def _hydrate(row: InstitutionalMemoryEntryRecord) -> InstitutionalMemoryEntry:
        try:
            entity_refs = json.loads(row.entity_refs_json)
            metric_refs = json.loads(row.metric_refs_json)
            source_refs = json.loads(row.source_refs_json)
            limitations = json.loads(row.limitations_json)
        except json.JSONDecodeError as exc:
            raise MemoryError("MEMORY_PERSISTENCE_INVALID", row.memory_id) from exc
        return InstitutionalMemoryEntry(
            memory_id=row.memory_id,
            tenant_binding=row.tenant_binding,
            role=MemoryRole(row.role),
            problem_type=row.problem_type,
            domain=row.domain,
            entity_refs=tuple(entity_refs),
            metric_refs=tuple(metric_refs),
            source_refs=tuple(MemorySourceRef.model_validate(item) for item in source_refs),
            summary=row.summary,
            limitations=tuple(limitations),
            precedent_of_memory_id=row.precedent_of_memory_id,
            source_set_fingerprint=row.source_set_fingerprint,
            memory_fingerprint=row.memory_fingerprint,
            created_at=row.created_at,
            indexed_by_user_id=row.indexed_by_user_id,
        )

    def _resolve_source(
        self,
        ref: MemorySourceRef,
        *,
        principal: Principal,
    ) -> tuple[str, bool]:
        if ref.kind == MemorySourceKind.ACTION_WORK:
            if self._work is None:
                raise MemoryError("MEMORY_SOURCE_STORE_REQUIRED", ref.kind.value)
            try:
                item = self._work.load(action_work_id=ref.artifact_id, principal=principal)
                state = self._work.currentness(
                    action_work_id=ref.artifact_id,
                    principal=principal,
                )
            except ActionWorkError as exc:
                raise MemoryError("MEMORY_SOURCE_UNAVAILABLE", ref.artifact_id) from exc
            if item.work_fingerprint != ref.artifact_fingerprint:
                raise MemoryError("MEMORY_SOURCE_FINGERPRINT_MISMATCH", ref.artifact_id)
            return item.work_fingerprint, state == ActionWorkCurrentness.CURRENT

        if ref.kind == MemorySourceKind.OUTCOME:
            if self._outcomes is None:
                raise MemoryError("MEMORY_SOURCE_STORE_REQUIRED", ref.kind.value)
            try:
                item = self._outcomes.load(outcome_id=ref.artifact_id, principal=principal)
                state = self._outcomes.currentness(
                    outcome_id=ref.artifact_id,
                    principal=principal,
                )
            except OutcomeError as exc:
                raise MemoryError("MEMORY_SOURCE_UNAVAILABLE", ref.artifact_id) from exc
            if item.outcome_fingerprint != ref.artifact_fingerprint:
                raise MemoryError("MEMORY_SOURCE_FINGERPRINT_MISMATCH", ref.artifact_id)
            return item.outcome_fingerprint, state == OutcomeCurrentness.CURRENT

        if ref.kind == MemorySourceKind.DECISION_ADOPTION:
            if self._adoptions is None:
                raise MemoryError("MEMORY_SOURCE_STORE_REQUIRED", ref.kind.value)
            try:
                item = self._adoptions.load(adoption_id=ref.artifact_id, principal=principal)
                state = self._adoptions.currentness(
                    adoption_id=ref.artifact_id,
                    principal=principal,
                )
            except AdoptionError as exc:
                raise MemoryError("MEMORY_SOURCE_UNAVAILABLE", ref.artifact_id) from exc
            if item.adoption_fingerprint != ref.artifact_fingerprint:
                raise MemoryError("MEMORY_SOURCE_FINGERPRINT_MISMATCH", ref.artifact_id)
            return item.adoption_fingerprint, state == AdoptionCurrentness.CURRENT

        if ref.kind == MemorySourceKind.DECISION_BRIEF:
            if self._decisions is None:
                raise MemoryError("MEMORY_SOURCE_STORE_REQUIRED", ref.kind.value)
            try:
                item = self._decisions.load(decision_brief_id=ref.artifact_id, principal=principal)
                state = self._decisions.currentness(
                    decision_brief_id=ref.artifact_id,
                    principal=principal,
                )
            except P21DecisionError as exc:
                raise MemoryError("MEMORY_SOURCE_UNAVAILABLE", ref.artifact_id) from exc
            if item.brief_fingerprint != ref.artifact_fingerprint:
                raise MemoryError("MEMORY_SOURCE_FINGERPRINT_MISMATCH", ref.artifact_id)
            return item.brief_fingerprint, state == DecisionBriefCurrentness.CURRENT

        if ref.kind == MemorySourceKind.REPORT:
            if self._reports is None:
                raise MemoryError("MEMORY_SOURCE_STORE_REQUIRED", ref.kind.value)
            try:
                item = self._reports.load(report_id=ref.artifact_id, principal=principal)
                state = self._reports.currentness(
                    report_id=ref.artifact_id,
                    principal=principal,
                )
            except P20ReportError as exc:
                raise MemoryError("MEMORY_SOURCE_UNAVAILABLE", ref.artifact_id) from exc
            if item.report_fingerprint != ref.artifact_fingerprint:
                raise MemoryError("MEMORY_SOURCE_FINGERPRINT_MISMATCH", ref.artifact_id)
            return item.report_fingerprint, state == ReportCurrentness.CURRENT

        raise MemoryError("MEMORY_SOURCE_KIND_UNSUPPORTED", ref.kind.value)

    def index(
        self,
        *,
        draft: InstitutionalMemoryDraft,
        principal: Principal,
        now: datetime | None = None,
    ) -> InstitutionalMemoryEntry:
        self._authorize_write(principal)
        stamp = _aware(now)
        tenant_binding = _tenant(principal)

        validated_sources: list[dict[str, str]] = []
        for ref in draft.source_refs:
            fingerprint, _ = self._resolve_source(ref, principal=principal)
            validated_sources.append(
                {
                    "kind": ref.kind.value,
                    "artifact_id": ref.artifact_id,
                    "artifact_fingerprint": fingerprint,
                }
            )

        if draft.precedent_of_memory_id is not None:
            self.load(memory_id=draft.precedent_of_memory_id, principal=principal)

        source_set_fingerprint = _canonical(
            sorted(
                validated_sources,
                key=lambda item: (item["kind"], item["artifact_id"]),
            ),
            code="MEMORY_SOURCE_SET_NOT_CANONICAL",
        )[1]
        identity = {
            "tenant_binding": tenant_binding,
            "role": draft.role.value,
            "problem_type": draft.problem_type.strip(),
            "domain": draft.domain.strip(),
            "entity_refs": sorted(draft.entity_refs),
            "metric_refs": sorted(draft.metric_refs),
            "source_set_fingerprint": source_set_fingerprint,
            "summary": draft.summary.strip(),
            "limitations": list(draft.limitations),
            "precedent_of_memory_id": draft.precedent_of_memory_id,
        }
        memory_fingerprint = _canonical(
            identity,
            code="MEMORY_NOT_CANONICAL",
        )[1]
        memory_id = "mem_" + memory_fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(InstitutionalMemoryEntryRecord, memory_id)
            if existing is not None:
                return self._hydrate(existing)
            row = InstitutionalMemoryEntryRecord(
                memory_id=memory_id,
                tenant_binding=tenant_binding,
                role=draft.role.value,
                problem_type=draft.problem_type.strip(),
                domain=draft.domain.strip(),
                entity_refs_json=_canonical(
                    sorted(draft.entity_refs),
                    code="MEMORY_ENTITY_REFS_NOT_CANONICAL",
                )[0],
                metric_refs_json=_canonical(
                    sorted(draft.metric_refs),
                    code="MEMORY_METRIC_REFS_NOT_CANONICAL",
                )[0],
                source_refs_json=_canonical(
                    [item.model_dump(mode="json") for item in draft.source_refs],
                    code="MEMORY_SOURCE_REFS_NOT_CANONICAL",
                )[0],
                summary=draft.summary.strip(),
                limitations_json=_canonical(
                    list(draft.limitations),
                    code="MEMORY_LIMITATIONS_NOT_CANONICAL",
                )[0],
                precedent_of_memory_id=draft.precedent_of_memory_id,
                source_set_fingerprint=source_set_fingerprint,
                memory_fingerprint=memory_fingerprint,
                created_at=stamp,
                indexed_by_user_id=_subject(principal),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(
        self,
        *,
        memory_id: str,
        principal: Principal,
    ) -> InstitutionalMemoryEntry:
        self._authorize_read(principal)
        tenant_binding = _tenant(principal)
        with Session(self._engine) as db:
            row = db.get(InstitutionalMemoryEntryRecord, memory_id)
            if row is None or row.tenant_binding != tenant_binding:
                raise MemoryError(
                    "MEMORY_UNAVAILABLE",
                    "memory unavailable in caller scope",
                )
            return self._hydrate(row)

    def currentness(
        self,
        *,
        memory_id: str,
        principal: Principal,
    ) -> MemoryCurrentness:
        entry = self.load(memory_id=memory_id, principal=principal)
        if entry.role == MemoryRole.HISTORICAL_PRECEDENT:
            return MemoryCurrentness.HISTORICAL_PRECEDENT
        for ref in entry.source_refs:
            try:
                _, current = self._resolve_source(ref, principal=principal)
            except MemoryError:
                return MemoryCurrentness.STALE_CONTEXT
            if not current:
                return MemoryCurrentness.STALE_CONTEXT
        return MemoryCurrentness.CURRENT_CONTEXT

    def list_context(
        self,
        *,
        principal: Principal,
        domain: str | None = None,
        problem_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[InstitutionalMemoryEntry, ...]:
        self._authorize_read(principal)
        if limit < 1 or limit > 200 or offset < 0:
            raise MemoryError("MEMORY_PAGINATION_INVALID", "invalid limit/offset")
        tenant_binding = _tenant(principal)
        stmt = select(InstitutionalMemoryEntryRecord).where(
            InstitutionalMemoryEntryRecord.tenant_binding == tenant_binding
        )
        if domain is not None:
            stmt = stmt.where(InstitutionalMemoryEntryRecord.domain == domain)
        if problem_type is not None:
            stmt = stmt.where(
                InstitutionalMemoryEntryRecord.problem_type == problem_type
            )
        stmt = (
            stmt.order_by(
                InstitutionalMemoryEntryRecord.created_at.desc(),
                InstitutionalMemoryEntryRecord.memory_id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )
        with Session(self._engine) as db:
            rows = db.exec(stmt).all()
        return tuple(self._hydrate(row) for row in rows)
