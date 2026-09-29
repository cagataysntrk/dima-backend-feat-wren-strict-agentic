"""Core Closure A4 — governed Watch and Signal core.

Watch describes what governed occurrence to observe. Signal records an occurrence
and organizational significance. Neither performs analytical computation.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.core_a.action_work import ActionWorkError, ActionWorkStore
from app.v3.core_a.institutional_memory import InstitutionalMemoryStore, MemoryError
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.db import engine as control_plane_engine
from control_plane.models import SignalRecord, WatchRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class WatchSignalError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class WatchKind(StrEnum):
    METRIC_THRESHOLD = "METRIC_THRESHOLD"
    MATERIAL_CHANGE = "MATERIAL_CHANGE"
    ENTITY_STATE_CHANGE = "ENTITY_STATE_CHANGE"
    DECISION_ASSUMPTION = "DECISION_ASSUMPTION"
    DUE_DATE = "DUE_DATE"
    ACTION_WORK_BLOCKER = "ACTION_WORK_BLOCKER"
    OUTCOME_REOBSERVATION = "OUTCOME_REOBSERVATION"
    SCHEDULED_CONTROL = "SCHEDULED_CONTROL"


class SignalSeverity(StrEnum):
    INFO = "INFO"
    MATERIAL = "MATERIAL"
    CRITICAL = "CRITICAL"


class SignalStatus(StrEnum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class SignalCurrentness(StrEnum):
    CURRENT = "CURRENT"
    SUPERSEDED = "SUPERSEDED"


class WatchDraft(Frozen):
    kind: WatchKind
    title: str = Field(min_length=1, max_length=500)
    source_contract_ref: str = Field(min_length=1, max_length=1000)
    criterion_ref: str = Field(min_length=1, max_length=1000)
    entity_refs: tuple[str, ...] = ()
    metric_refs: tuple[str, ...] = ()
    context_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def unique_refs(self):
        for values in (self.entity_refs, self.metric_refs, self.context_refs):
            if len(values) != len(set(values)):
                raise ValueError("Watch references must be unique")
        return self


class Watch(Frozen):
    watch_id: str = Field(pattern=r"^wat_[a-f0-9]{24}$")
    tenant_binding: str
    kind: WatchKind
    title: str
    source_contract_ref: str
    criterion_ref: str
    entity_refs: tuple[str, ...]
    metric_refs: tuple[str, ...]
    context_refs: tuple[str, ...]
    watch_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime
    created_by_user_id: str


class SignalEvidenceRef(Frozen):
    research_session_id: str = Field(min_length=1)
    obligation_id: str = Field(min_length=1)
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")


class SignalOccurrence(Frozen):
    source_occurrence_id: str = Field(min_length=1, max_length=1000)
    source_kind: str = Field(min_length=1, max_length=200)
    source_ref: str = Field(min_length=1, max_length=1000)
    observed_at: datetime
    evidence: SignalEvidenceRef | None = None
    entity_refs: tuple[str, ...] = ()
    metric_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def coherent(self):
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if len(self.entity_refs) != len(set(self.entity_refs)):
            raise ValueError("duplicate entity refs are not allowed")
        if len(self.metric_refs) != len(set(self.metric_refs)):
            raise ValueError("duplicate metric refs are not allowed")
        return self


class SignalTransition(Frozen):
    from_status: SignalStatus | None
    to_status: SignalStatus
    actor_user_id: str
    occurred_at: datetime
    research_session_id: str | None = None
    resolution_ref: str | None = None


class Signal(Frozen):
    signal_id: str = Field(pattern=r"^sig_[a-f0-9]{24}$")
    root_signal_id: str = Field(pattern=r"^sig_[a-f0-9]{24}$")
    revision: int = Field(ge=1)
    parent_signal_id: str | None = None
    tenant_binding: str
    watch_id: str
    source_occurrence_id: str
    occurrence_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_kind: str
    source_ref: str
    evidence: SignalEvidenceRef | None = None
    entity_refs: tuple[str, ...]
    metric_refs: tuple[str, ...]
    observed_at: datetime
    severity: SignalSeverity
    business_significance: str
    memory_entry_id: str | None = None
    action_work_id: str | None = None
    status: SignalStatus
    research_session_id: str | None = None
    resolution_ref: str | None = None
    transition_history: tuple[SignalTransition, ...]
    signal_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


_TRANSITIONS: dict[SignalStatus, frozenset[SignalStatus]] = {
    SignalStatus.NEW: frozenset(
        {
            SignalStatus.ACKNOWLEDGED,
            SignalStatus.INVESTIGATING,
            SignalStatus.DISMISSED,
        }
    ),
    SignalStatus.ACKNOWLEDGED: frozenset(
        {
            SignalStatus.INVESTIGATING,
            SignalStatus.RESOLVED,
            SignalStatus.DISMISSED,
        }
    ),
    SignalStatus.INVESTIGATING: frozenset(
        {
            SignalStatus.RESOLVED,
            SignalStatus.DISMISSED,
        }
    ),
    SignalStatus.RESOLVED: frozenset(),
    SignalStatus.DISMISSED: frozenset(),
}


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
        raise WatchSignalError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise WatchSignalError("WATCH_SIGNAL_TENANT_REQUIRED", "tenant binding is required")


def _subject(principal: Principal) -> str:
    value = str(principal.user_id).strip()
    if not value:
        raise WatchSignalError("WATCH_SIGNAL_PRINCIPAL_REQUIRED", "principal identity is required")
    return value


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise WatchSignalError("WATCH_SIGNAL_TIMEZONE_REQUIRED", "timestamp must be timezone-aware")
    return stamp


class WatchSignalStore:
    def __init__(
        self,
        *,
        research_store: ResearchSessionStore | None = None,
        memory_store: InstitutionalMemoryStore | None = None,
        work_store: ActionWorkStore | None = None,
        db_engine=None,
    ) -> None:
        self._research = research_store
        self._memory = memory_store
        self._work = work_store
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _authorize(principal: Principal) -> None:
        try:
            authorize(principal, "watch:manage", "watch-signal")
        except AuthzError as exc:
            raise WatchSignalError(
                "WATCH_SIGNAL_FORBIDDEN",
                "principal cannot manage Watch/Signal",
            ) from exc

    @staticmethod
    def _hydrate_watch(row: WatchRecord) -> Watch:
        try:
            entity_refs = json.loads(row.entity_refs_json)
            metric_refs = json.loads(row.metric_refs_json)
            context_refs = json.loads(row.context_refs_json)
        except json.JSONDecodeError as exc:
            raise WatchSignalError("WATCH_PERSISTENCE_INVALID", row.watch_id) from exc
        return Watch(
            watch_id=row.watch_id,
            tenant_binding=row.tenant_binding,
            kind=WatchKind(row.kind),
            title=row.title,
            source_contract_ref=row.source_contract_ref,
            criterion_ref=row.criterion_ref,
            entity_refs=tuple(entity_refs),
            metric_refs=tuple(metric_refs),
            context_refs=tuple(context_refs),
            watch_fingerprint=row.watch_fingerprint,
            created_at=row.created_at,
            created_by_user_id=row.created_by_user_id,
        )

    @staticmethod
    def _hydrate_signal(row: SignalRecord) -> Signal:
        try:
            evidence_raw = json.loads(row.evidence_ref_json) if row.evidence_ref_json else None
            entity_refs = json.loads(row.entity_refs_json)
            metric_refs = json.loads(row.metric_refs_json)
            history = json.loads(row.transition_history_json)
        except json.JSONDecodeError as exc:
            raise WatchSignalError("SIGNAL_PERSISTENCE_INVALID", row.signal_id) from exc
        return Signal(
            signal_id=row.signal_id,
            root_signal_id=row.root_signal_id,
            revision=row.revision,
            parent_signal_id=row.parent_signal_id,
            tenant_binding=row.tenant_binding,
            watch_id=row.watch_id,
            source_occurrence_id=row.source_occurrence_id,
            occurrence_fingerprint=row.occurrence_fingerprint,
            source_kind=row.source_kind,
            source_ref=row.source_ref,
            evidence=(
                SignalEvidenceRef.model_validate(evidence_raw)
                if evidence_raw is not None
                else None
            ),
            entity_refs=tuple(entity_refs),
            metric_refs=tuple(metric_refs),
            observed_at=row.observed_at,
            severity=SignalSeverity(row.severity),
            business_significance=row.business_significance,
            memory_entry_id=row.memory_entry_id,
            action_work_id=row.action_work_id,
            status=SignalStatus(row.status),
            research_session_id=row.research_session_id,
            resolution_ref=row.resolution_ref,
            transition_history=tuple(
                SignalTransition.model_validate(item) for item in history
            ),
            signal_fingerprint=row.signal_fingerprint,
            created_at=row.created_at,
        )

    def create_watch(
        self,
        *,
        draft: WatchDraft,
        principal: Principal,
        now: datetime | None = None,
    ) -> Watch:
        self._authorize(principal)
        stamp = _aware(now)
        identity = {
            "tenant_binding": _tenant(principal),
            "kind": draft.kind.value,
            "title": draft.title.strip(),
            "source_contract_ref": draft.source_contract_ref.strip(),
            "criterion_ref": draft.criterion_ref.strip(),
            "entity_refs": sorted(draft.entity_refs),
            "metric_refs": sorted(draft.metric_refs),
            "context_refs": sorted(draft.context_refs),
        }
        fingerprint = _canonical(identity, code="WATCH_NOT_CANONICAL")[1]
        watch_id = "wat_" + fingerprint[:24]
        with Session(self._engine) as db:
            existing = db.get(WatchRecord, watch_id)
            if existing is not None:
                return self._hydrate_watch(existing)
            row = WatchRecord(
                watch_id=watch_id,
                tenant_binding=identity["tenant_binding"],
                kind=draft.kind.value,
                title=draft.title.strip(),
                source_contract_ref=draft.source_contract_ref.strip(),
                criterion_ref=draft.criterion_ref.strip(),
                entity_refs_json=_canonical(
                    sorted(draft.entity_refs),
                    code="WATCH_ENTITY_REFS_NOT_CANONICAL",
                )[0],
                metric_refs_json=_canonical(
                    sorted(draft.metric_refs),
                    code="WATCH_METRIC_REFS_NOT_CANONICAL",
                )[0],
                context_refs_json=_canonical(
                    sorted(draft.context_refs),
                    code="WATCH_CONTEXT_REFS_NOT_CANONICAL",
                )[0],
                watch_fingerprint=fingerprint,
                created_at=stamp,
                created_by_user_id=_subject(principal),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_watch(row)

    def load_watch(self, *, watch_id: str, principal: Principal) -> Watch:
        tenant_binding = _tenant(principal)
        with Session(self._engine) as db:
            row = db.get(WatchRecord, watch_id)
            if row is None or row.tenant_binding != tenant_binding:
                raise WatchSignalError(
                    "WATCH_UNAVAILABLE",
                    "Watch unavailable in caller scope",
                )
            return self._hydrate_watch(row)

    def _validate_evidence(
        self,
        ref: SignalEvidenceRef,
        *,
        principal: Principal,
    ) -> None:
        if self._research is None:
            raise WatchSignalError(
                "SIGNAL_RESEARCH_STORE_REQUIRED",
                "Evidence-linked occurrence requires Research store",
            )
        try:
            self._research.load(
                ref.research_session_id,
                tenant=_tenant(principal),
                principal=_subject(principal),
            )
            link = self._research.verified_link(
                session_id=ref.research_session_id,
                obligation_id=ref.obligation_id,
            )
        except ResearchPersistenceError as exc:
            raise WatchSignalError(
                "SIGNAL_EVIDENCE_UNAVAILABLE",
                "verified Evidence occurrence unavailable",
            ) from exc
        if link.evidence_id != ref.evidence_id or link.receipt_id != ref.receipt_id:
            raise WatchSignalError(
                "SIGNAL_EVIDENCE_PROVENANCE_MISMATCH",
                ref.evidence_id,
            )

    def observe(
        self,
        *,
        watch_id: str,
        occurrence: SignalOccurrence,
        severity: SignalSeverity,
        business_significance: str,
        principal: Principal,
        memory_entry_id: str | None = None,
        action_work_id: str | None = None,
        now: datetime | None = None,
    ) -> Signal:
        self._authorize(principal)
        stamp = _aware(now)
        watch = self.load_watch(watch_id=watch_id, principal=principal)
        if occurrence.evidence is not None:
            self._validate_evidence(occurrence.evidence, principal=principal)
        if memory_entry_id is not None:
            if self._memory is None:
                raise WatchSignalError("SIGNAL_MEMORY_STORE_REQUIRED", memory_entry_id)
            try:
                self._memory.load(memory_id=memory_entry_id, principal=principal)
            except MemoryError as exc:
                raise WatchSignalError("SIGNAL_MEMORY_UNAVAILABLE", memory_entry_id) from exc
        if action_work_id is not None:
            if self._work is None:
                raise WatchSignalError("SIGNAL_WORK_STORE_REQUIRED", action_work_id)
            try:
                self._work.load(action_work_id=action_work_id, principal=principal)
            except ActionWorkError as exc:
                raise WatchSignalError("SIGNAL_WORK_UNAVAILABLE", action_work_id) from exc

        occurrence_identity = {
            "tenant_binding": watch.tenant_binding,
            "watch_id": watch.watch_id,
            "source_occurrence_id": occurrence.source_occurrence_id,
            "source_kind": occurrence.source_kind,
            "source_ref": occurrence.source_ref,
            "evidence": (
                occurrence.evidence.model_dump(mode="json")
                if occurrence.evidence is not None
                else None
            ),
            "entity_refs": sorted(occurrence.entity_refs),
            "metric_refs": sorted(occurrence.metric_refs),
            "observed_at": occurrence.observed_at.isoformat(),
        }
        occurrence_fingerprint = _canonical(
            occurrence_identity,
            code="SIGNAL_OCCURRENCE_NOT_CANONICAL",
        )[1]
        root_id = "sig_" + occurrence_fingerprint[:24]
        transition = SignalTransition(
            from_status=None,
            to_status=SignalStatus.NEW,
            actor_user_id=_subject(principal),
            occurred_at=stamp,
        )
        signal_identity = {
            **occurrence_identity,
            "severity": severity.value,
            "business_significance": business_significance.strip(),
            "memory_entry_id": memory_entry_id,
            "action_work_id": action_work_id,
            "status": SignalStatus.NEW.value,
            "transition_history": [transition.model_dump(mode="json")],
        }
        signal_fingerprint = _canonical(
            signal_identity,
            code="SIGNAL_NOT_CANONICAL",
        )[1]

        with Session(self._engine) as db:
            existing = db.get(SignalRecord, root_id)
            if existing is not None:
                hydrated = self._hydrate_signal(existing)
                if hydrated.occurrence_fingerprint != occurrence_fingerprint:
                    raise WatchSignalError("SIGNAL_IDENTITY_COLLISION", root_id)
                return hydrated
            row = SignalRecord(
                signal_id=root_id,
                root_signal_id=root_id,
                revision=1,
                parent_signal_id=None,
                tenant_binding=watch.tenant_binding,
                watch_id=watch.watch_id,
                source_occurrence_id=occurrence.source_occurrence_id,
                occurrence_fingerprint=occurrence_fingerprint,
                source_kind=occurrence.source_kind,
                source_ref=occurrence.source_ref,
                evidence_ref_json=(
                    _canonical(
                        occurrence.evidence.model_dump(mode="json"),
                        code="SIGNAL_EVIDENCE_REF_NOT_CANONICAL",
                    )[0]
                    if occurrence.evidence is not None
                    else None
                ),
                entity_refs_json=_canonical(
                    sorted(occurrence.entity_refs),
                    code="SIGNAL_ENTITY_REFS_NOT_CANONICAL",
                )[0],
                metric_refs_json=_canonical(
                    sorted(occurrence.metric_refs),
                    code="SIGNAL_METRIC_REFS_NOT_CANONICAL",
                )[0],
                observed_at=occurrence.observed_at,
                severity=severity.value,
                business_significance=business_significance.strip(),
                memory_entry_id=memory_entry_id,
                action_work_id=action_work_id,
                status=SignalStatus.NEW.value,
                research_session_id=None,
                resolution_ref=None,
                transition_history_json=_canonical(
                    [transition.model_dump(mode="json")],
                    code="SIGNAL_HISTORY_NOT_CANONICAL",
                )[0],
                signal_fingerprint=signal_fingerprint,
                created_at=stamp,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_signal(row)

    def load_signal(self, *, signal_id: str, principal: Principal) -> Signal:
        tenant_binding = _tenant(principal)
        with Session(self._engine) as db:
            row = db.get(SignalRecord, signal_id)
            if row is None or row.tenant_binding != tenant_binding:
                raise WatchSignalError(
                    "SIGNAL_UNAVAILABLE",
                    "Signal unavailable in caller scope",
                )
            return self._hydrate_signal(row)

    def latest_signal(self, *, root_signal_id: str, principal: Principal) -> Signal:
        tenant_binding = _tenant(principal)
        with Session(self._engine) as db:
            row = db.exec(
                select(SignalRecord)
                .where(SignalRecord.root_signal_id == root_signal_id)
                .where(SignalRecord.tenant_binding == tenant_binding)
                .order_by(SignalRecord.revision.desc())
            ).first()
        if row is None:
            raise WatchSignalError("SIGNAL_UNAVAILABLE", "Signal unavailable in caller scope")
        return self._hydrate_signal(row)

    def transition(
        self,
        *,
        signal_id: str,
        to_status: SignalStatus,
        principal: Principal,
        research_session_id: str | None = None,
        resolution_ref: str | None = None,
        now: datetime | None = None,
    ) -> Signal:
        self._authorize(principal)
        stamp = _aware(now)
        source = self.load_signal(signal_id=signal_id, principal=principal)
        latest = self.latest_signal(root_signal_id=source.root_signal_id, principal=principal)

        if latest.status == to_status:
            if (
                latest.research_session_id == research_session_id
                and latest.resolution_ref == resolution_ref
            ):
                return latest
            raise WatchSignalError(
                "SIGNAL_TRANSITION_METADATA_MISMATCH",
                "same state already exists with different metadata",
            )
        if latest.signal_id != source.signal_id:
            raise WatchSignalError("SIGNAL_SUPERSEDED", latest.signal_id)
        if to_status not in _TRANSITIONS[latest.status]:
            raise WatchSignalError(
                "SIGNAL_ILLEGAL_TRANSITION",
                f"{latest.status.value}->{to_status.value}",
            )

        if to_status == SignalStatus.INVESTIGATING:
            if not research_session_id:
                raise WatchSignalError(
                    "SIGNAL_RESEARCH_SESSION_REQUIRED",
                    "INVESTIGATING requires an existing ResearchSession",
                )
            if self._research is None:
                raise WatchSignalError(
                    "SIGNAL_RESEARCH_STORE_REQUIRED",
                    research_session_id,
                )
            try:
                self._research.load(
                    research_session_id,
                    tenant=_tenant(principal),
                    principal=_subject(principal),
                )
            except ResearchPersistenceError as exc:
                raise WatchSignalError(
                    "SIGNAL_RESEARCH_UNAVAILABLE",
                    research_session_id,
                ) from exc
        elif research_session_id is not None:
            raise WatchSignalError(
                "SIGNAL_RESEARCH_SESSION_NOT_ALLOWED",
                "ResearchSession is only bound at INVESTIGATING transition",
            )

        if to_status == SignalStatus.RESOLVED and not (resolution_ref or "").strip():
            raise WatchSignalError(
                "SIGNAL_RESOLUTION_REQUIRED",
                "RESOLVED requires resolution reference",
            )
        if to_status != SignalStatus.RESOLVED and resolution_ref is not None:
            raise WatchSignalError(
                "SIGNAL_RESOLUTION_NOT_ALLOWED",
                "resolution reference is only legal for RESOLVED",
            )

        next_research = research_session_id or latest.research_session_id
        transition = SignalTransition(
            from_status=latest.status,
            to_status=to_status,
            actor_user_id=_subject(principal),
            occurred_at=stamp,
            research_session_id=(
                research_session_id if to_status == SignalStatus.INVESTIGATING else None
            ),
            resolution_ref=(
                resolution_ref.strip() if resolution_ref and to_status == SignalStatus.RESOLVED else None
            ),
        )
        history = (*latest.transition_history, transition)
        revision = latest.revision + 1
        identity = {
            "root_signal_id": latest.root_signal_id,
            "revision": revision,
            "parent_signal_id": latest.signal_id,
            "occurrence_fingerprint": latest.occurrence_fingerprint,
            "severity": latest.severity.value,
            "business_significance": latest.business_significance,
            "memory_entry_id": latest.memory_entry_id,
            "action_work_id": latest.action_work_id,
            "status": to_status.value,
            "research_session_id": next_research,
            "resolution_ref": transition.resolution_ref,
            "transition_history": [item.model_dump(mode="json") for item in history],
        }
        signal_fingerprint = _canonical(
            identity,
            code="SIGNAL_NOT_CANONICAL",
        )[1]
        next_id = "sig_" + signal_fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(SignalRecord, next_id)
            if existing is not None:
                return self._hydrate_signal(existing)
            row = SignalRecord(
                signal_id=next_id,
                root_signal_id=latest.root_signal_id,
                revision=revision,
                parent_signal_id=latest.signal_id,
                tenant_binding=latest.tenant_binding,
                watch_id=latest.watch_id,
                source_occurrence_id=latest.source_occurrence_id,
                occurrence_fingerprint=latest.occurrence_fingerprint,
                source_kind=latest.source_kind,
                source_ref=latest.source_ref,
                evidence_ref_json=(
                    _canonical(
                        latest.evidence.model_dump(mode="json"),
                        code="SIGNAL_EVIDENCE_REF_NOT_CANONICAL",
                    )[0]
                    if latest.evidence is not None
                    else None
                ),
                entity_refs_json=_canonical(
                    list(latest.entity_refs),
                    code="SIGNAL_ENTITY_REFS_NOT_CANONICAL",
                )[0],
                metric_refs_json=_canonical(
                    list(latest.metric_refs),
                    code="SIGNAL_METRIC_REFS_NOT_CANONICAL",
                )[0],
                observed_at=latest.observed_at,
                severity=latest.severity.value,
                business_significance=latest.business_significance,
                memory_entry_id=latest.memory_entry_id,
                action_work_id=latest.action_work_id,
                status=to_status.value,
                research_session_id=next_research,
                resolution_ref=transition.resolution_ref,
                transition_history_json=_canonical(
                    [item.model_dump(mode="json") for item in history],
                    code="SIGNAL_HISTORY_NOT_CANONICAL",
                )[0],
                signal_fingerprint=signal_fingerprint,
                created_at=stamp,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_signal(row)

    def currentness(
        self,
        *,
        signal_id: str,
        principal: Principal,
    ) -> SignalCurrentness:
        signal = self.load_signal(signal_id=signal_id, principal=principal)
        latest = self.latest_signal(root_signal_id=signal.root_signal_id, principal=principal)
        return (
            SignalCurrentness.CURRENT
            if latest.signal_id == signal.signal_id
            else SignalCurrentness.SUPERSEDED
        )
