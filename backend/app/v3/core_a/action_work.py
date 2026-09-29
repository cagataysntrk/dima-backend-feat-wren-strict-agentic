"""Core Closure A1 — internal ActionWork lifecycle.

ActionWork tracks an authenticated organizational commitment. It never executes
external actions and completion never proves a business Outcome.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.action_authorization import ActionAuthorizationStore, ActionAuthorityError
from app.v3.decision_adoption import (
    AdoptionCurrentness,
    AdoptionDisposition,
    AdoptionError,
    DecisionAdoptionStore,
)
from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.db import engine as control_plane_engine
from control_plane.models import ActionWorkRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ActionWorkError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ActionWorkStatus(StrEnum):
    PLANNED = "PLANNED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ActionWorkCurrentness(StrEnum):
    CURRENT = "CURRENT"
    SOURCE_ADOPTION_STALE = "SOURCE_ADOPTION_STALE"
    SUPERSEDED = "SUPERSEDED"


class ActionWorkTransition(Frozen):
    from_status: ActionWorkStatus | None
    to_status: ActionWorkStatus
    actor_user_id: str = Field(min_length=1)
    occurred_at: datetime
    blocker_reason: str | None = None
    completion_reference: str | None = None


class ActionWorkDraft(Frozen):
    decision_adoption_id: str = Field(pattern=r"^adp_[a-f0-9]{24}$")
    decision_adoption_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    action_authorization_id: str | None = Field(
        default=None,
        pattern=r"^authz_[a-f0-9]{24}$",
    )
    action_authorization_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    title: str = Field(min_length=1, max_length=500)
    work_intent: dict[str, Any]
    due_at: datetime | None = None

    @model_validator(mode="after")
    def coherent_authorization_pair(self):
        if (self.action_authorization_id is None) != (
            self.action_authorization_fingerprint is None
        ):
            raise ValueError(
                "ActionAuthorization id/fingerprint must be supplied together"
            )
        if self.due_at is not None and (
            self.due_at.tzinfo is None or self.due_at.utcoffset() is None
        ):
            raise ValueError("due_at must be timezone-aware")
        return self


class ActionWork(Frozen):
    action_work_id: str = Field(pattern=r"^wrk_[a-f0-9]{24}$")
    root_action_work_id: str = Field(pattern=r"^wrk_[a-f0-9]{24}$")
    revision: int = Field(ge=1)
    parent_action_work_id: str | None = None

    tenant_binding: str
    decision_brief_id: str
    decision_brief_fingerprint: str
    decision_adoption_id: str
    decision_adoption_fingerprint: str
    action_authorization_id: str | None = None
    action_authorization_fingerprint: str | None = None

    title: str
    work_intent: dict[str, Any]
    owner_user_id: str
    owner_context: dict[str, Any]
    due_at: datetime | None = None

    status: ActionWorkStatus
    blocker_reason: str | None = None
    completion_reference: str | None = None
    transition_history: tuple[ActionWorkTransition, ...]

    source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    work_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


_TRANSITIONS: dict[ActionWorkStatus, frozenset[ActionWorkStatus]] = {
    ActionWorkStatus.PLANNED: frozenset(
        {
            ActionWorkStatus.ACKNOWLEDGED,
            ActionWorkStatus.CANCELLED,
        }
    ),
    ActionWorkStatus.ACKNOWLEDGED: frozenset(
        {
            ActionWorkStatus.IN_PROGRESS,
            ActionWorkStatus.BLOCKED,
            ActionWorkStatus.CANCELLED,
        }
    ),
    ActionWorkStatus.IN_PROGRESS: frozenset(
        {
            ActionWorkStatus.BLOCKED,
            ActionWorkStatus.COMPLETED,
            ActionWorkStatus.CANCELLED,
        }
    ),
    ActionWorkStatus.BLOCKED: frozenset(
        {
            ActionWorkStatus.IN_PROGRESS,
            ActionWorkStatus.CANCELLED,
        }
    ),
    ActionWorkStatus.COMPLETED: frozenset(),
    ActionWorkStatus.CANCELLED: frozenset(),
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
        raise ActionWorkError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ActionWorkError("WORK_TIMEZONE_REQUIRED", "timestamp must be timezone-aware")
    return stamp


def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise ActionWorkError("WORK_TENANT_REQUIRED", "tenant binding is required")


def _owner_context(principal: Principal) -> dict[str, Any]:
    user_id = str(principal.user_id).strip()
    if not user_id:
        raise ActionWorkError("WORK_OWNER_REQUIRED", "authenticated principal is required")
    return {
        "user_id": user_id,
        "tenant_binding": _tenant(principal),
        "roles": sorted(set(principal.roles)),
        "is_superadmin": bool(principal.is_superadmin),
        "authorization_action": "work:manage",
    }


class ActionWorkStore:
    def __init__(
        self,
        *,
        adoption_store: DecisionAdoptionStore,
        authorization_store: ActionAuthorizationStore | None = None,
        db_engine=None,
    ) -> None:
        self._adoptions = adoption_store
        self._authorizations = authorization_store
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _hydrate(row: ActionWorkRecord) -> ActionWork:
        try:
            work_intent = json.loads(row.work_intent_json)
            owner_context = json.loads(row.owner_context_json)
            transitions = json.loads(row.transition_history_json)
        except json.JSONDecodeError as exc:
            raise ActionWorkError(
                "WORK_PERSISTENCE_INVALID",
                row.action_work_id,
            ) from exc
        return ActionWork(
            action_work_id=row.action_work_id,
            root_action_work_id=row.root_action_work_id,
            revision=row.revision,
            parent_action_work_id=row.parent_action_work_id,
            tenant_binding=row.tenant_binding,
            decision_brief_id=row.decision_brief_id,
            decision_brief_fingerprint=row.decision_brief_fingerprint,
            decision_adoption_id=row.decision_adoption_id,
            decision_adoption_fingerprint=row.decision_adoption_fingerprint,
            action_authorization_id=row.action_authorization_id,
            action_authorization_fingerprint=row.action_authorization_fingerprint,
            title=row.title,
            work_intent=work_intent,
            owner_user_id=row.owner_user_id,
            owner_context=owner_context,
            due_at=row.due_at,
            status=ActionWorkStatus(row.status),
            blocker_reason=row.blocker_reason,
            completion_reference=row.completion_reference,
            transition_history=tuple(
                ActionWorkTransition.model_validate(item) for item in transitions
            ),
            source_fingerprint=row.source_fingerprint,
            work_fingerprint=row.work_fingerprint,
            created_at=row.created_at,
        )

    @staticmethod
    def _authorize(principal: Principal) -> None:
        try:
            authorize(principal, "work:manage", "action-work")
        except AuthzError as exc:
            raise ActionWorkError(
                "WORK_FORBIDDEN",
                "principal cannot manage ActionWork",
            ) from exc

    def _validate_source(
        self,
        *,
        draft: ActionWorkDraft,
        principal: Principal,
    ):
        try:
            adoption = self._adoptions.load(
                adoption_id=draft.decision_adoption_id,
                principal=principal,
            )
            currentness = self._adoptions.currentness(
                adoption_id=draft.decision_adoption_id,
                principal=principal,
            )
        except AdoptionError as exc:
            raise ActionWorkError(
                "WORK_SOURCE_UNAVAILABLE",
                "DecisionAdoption unavailable in caller scope",
            ) from exc
        if currentness != AdoptionCurrentness.CURRENT:
            raise ActionWorkError(
                "WORK_SOURCE_ADOPTION_STALE",
                currentness.value,
            )
        if adoption.disposition not in {
            AdoptionDisposition.ACCEPTED,
            AdoptionDisposition.MODIFIED,
        }:
            raise ActionWorkError(
                "WORK_SOURCE_ADOPTION_NOT_COMMITTED",
                adoption.disposition.value,
            )
        if adoption.adoption_fingerprint != draft.decision_adoption_fingerprint:
            raise ActionWorkError(
                "WORK_ADOPTION_FINGERPRINT_MISMATCH",
                adoption.adoption_id,
            )

        authorization = None
        if draft.action_authorization_id is not None:
            if self._authorizations is None:
                raise ActionWorkError(
                    "WORK_AUTHORIZATION_STORE_REQUIRED",
                    "ActionAuthorization source cannot be verified",
                )
            try:
                authorization = self._authorizations.load(
                    authorization_id=draft.action_authorization_id,
                    principal=principal,
                )
            except ActionAuthorityError as exc:
                raise ActionWorkError(
                    "WORK_ACTION_AUTHORIZATION_UNAVAILABLE",
                    "ActionAuthorization unavailable in caller scope",
                ) from exc
            if (
                authorization.authorization_fingerprint
                != draft.action_authorization_fingerprint
                or authorization.decision_adoption_id != adoption.adoption_id
                or authorization.decision_adoption_fingerprint
                != adoption.adoption_fingerprint
                or authorization.decision_brief_id != adoption.decision_brief_id
                or authorization.decision_brief_fingerprint
                != adoption.source_brief_fingerprint
            ):
                raise ActionWorkError(
                    "WORK_ACTION_AUTHORIZATION_LINEAGE_MISMATCH",
                    authorization.authorization_id,
                )
        return adoption, authorization

    def create(
        self,
        *,
        draft: ActionWorkDraft,
        principal: Principal,
        now: datetime | None = None,
    ) -> ActionWork:
        self._authorize(principal)
        stamp = _aware(now)
        tenant_binding = _tenant(principal)
        adoption, authorization = self._validate_source(
            draft=draft,
            principal=principal,
        )
        owner_context = _owner_context(principal)

        source_identity = {
            "tenant_binding": tenant_binding,
            "decision_brief_id": adoption.decision_brief_id,
            "decision_brief_fingerprint": adoption.source_brief_fingerprint,
            "decision_adoption_id": adoption.adoption_id,
            "decision_adoption_fingerprint": adoption.adoption_fingerprint,
            "action_authorization_id": (
                authorization.authorization_id if authorization is not None else None
            ),
            "action_authorization_fingerprint": (
                authorization.authorization_fingerprint
                if authorization is not None
                else None
            ),
        }
        source_fingerprint = _canonical(
            source_identity,
            code="WORK_SOURCE_NOT_CANONICAL",
        )[1]
        initial_identity = {
            **source_identity,
            "title": draft.title.strip(),
            "work_intent": draft.work_intent,
            "owner_user_id": str(principal.user_id),
            "due_at": draft.due_at.isoformat() if draft.due_at is not None else None,
        }
        root_digest = _canonical(
            initial_identity,
            code="WORK_IDENTITY_NOT_CANONICAL",
        )[1]
        root_id = "wrk_" + root_digest[:24]

        transition = ActionWorkTransition(
            from_status=None,
            to_status=ActionWorkStatus.PLANNED,
            actor_user_id=str(principal.user_id),
            occurred_at=stamp,
        )
        payload = {
            **initial_identity,
            "root_action_work_id": root_id,
            "revision": 1,
            "parent_action_work_id": None,
            "status": ActionWorkStatus.PLANNED.value,
            "blocker_reason": None,
            "completion_reference": None,
            "transition_history": [transition.model_dump(mode="json")],
            "source_fingerprint": source_fingerprint,
        }
        work_fingerprint = _canonical(
            payload,
            code="WORK_NOT_CANONICAL",
        )[1]
        action_work_id = root_id

        with Session(self._engine) as db:
            existing = db.get(ActionWorkRecord, action_work_id)
            if existing is not None:
                hydrated = self._hydrate(existing)
                if hydrated.work_fingerprint != work_fingerprint:
                    raise ActionWorkError(
                        "WORK_IDENTITY_COLLISION",
                        action_work_id,
                    )
                return hydrated

            row = ActionWorkRecord(
                action_work_id=action_work_id,
                root_action_work_id=root_id,
                revision=1,
                parent_action_work_id=None,
                tenant_binding=tenant_binding,
                decision_brief_id=adoption.decision_brief_id,
                decision_brief_fingerprint=adoption.source_brief_fingerprint,
                decision_adoption_id=adoption.adoption_id,
                decision_adoption_fingerprint=adoption.adoption_fingerprint,
                action_authorization_id=(
                    authorization.authorization_id
                    if authorization is not None
                    else None
                ),
                action_authorization_fingerprint=(
                    authorization.authorization_fingerprint
                    if authorization is not None
                    else None
                ),
                title=draft.title.strip(),
                work_intent_json=_canonical(
                    draft.work_intent,
                    code="WORK_INTENT_NOT_CANONICAL",
                )[0],
                owner_user_id=str(principal.user_id),
                owner_context_json=_canonical(
                    owner_context,
                    code="WORK_OWNER_CONTEXT_NOT_CANONICAL",
                )[0],
                due_at=draft.due_at,
                status=ActionWorkStatus.PLANNED.value,
                blocker_reason=None,
                completion_reference=None,
                transition_history_json=_canonical(
                    [transition.model_dump(mode="json")],
                    code="WORK_HISTORY_NOT_CANONICAL",
                )[0],
                source_fingerprint=source_fingerprint,
                work_fingerprint=work_fingerprint,
                created_at=stamp,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(
        self,
        *,
        action_work_id: str,
        principal: Principal,
    ) -> ActionWork:
        tenant_binding = _tenant(principal)
        with Session(self._engine) as db:
            row = db.get(ActionWorkRecord, action_work_id)
            if row is None or row.tenant_binding != tenant_binding:
                raise ActionWorkError(
                    "WORK_UNAVAILABLE",
                    "ActionWork unavailable in caller scope",
                )
            return self._hydrate(row)

    def latest(
        self,
        *,
        root_action_work_id: str,
        principal: Principal,
    ) -> ActionWork:
        tenant_binding = _tenant(principal)
        with Session(self._engine) as db:
            row = db.exec(
                select(ActionWorkRecord)
                .where(ActionWorkRecord.root_action_work_id == root_action_work_id)
                .where(ActionWorkRecord.tenant_binding == tenant_binding)
                .order_by(ActionWorkRecord.revision.desc())
            ).first()
        if row is None:
            raise ActionWorkError(
                "WORK_UNAVAILABLE",
                "ActionWork unavailable in caller scope",
            )
        return self._hydrate(row)

    def transition(
        self,
        *,
        action_work_id: str,
        to_status: ActionWorkStatus,
        principal: Principal,
        blocker_reason: str | None = None,
        completion_reference: str | None = None,
        now: datetime | None = None,
    ) -> ActionWork:
        self._authorize(principal)
        stamp = _aware(now)
        source = self.load(action_work_id=action_work_id, principal=principal)
        latest = self.latest(
            root_action_work_id=source.root_action_work_id,
            principal=principal,
        )

        if latest.status == to_status:
            if (
                latest.blocker_reason == blocker_reason
                and latest.completion_reference == completion_reference
            ):
                return latest
            raise ActionWorkError(
                "WORK_TRANSITION_METADATA_MISMATCH",
                "same status was already recorded with different metadata",
            )
        if latest.action_work_id != source.action_work_id:
            raise ActionWorkError(
                "WORK_SUPERSEDED",
                latest.action_work_id,
            )
        if to_status not in _TRANSITIONS[latest.status]:
            raise ActionWorkError(
                "WORK_ILLEGAL_TRANSITION",
                f"{latest.status.value}->{to_status.value}",
            )
        if to_status == ActionWorkStatus.BLOCKED and not (blocker_reason or "").strip():
            raise ActionWorkError(
                "WORK_BLOCKER_REQUIRED",
                "BLOCKED transition requires blocker reason",
            )
        if to_status != ActionWorkStatus.BLOCKED and blocker_reason is not None:
            raise ActionWorkError(
                "WORK_BLOCKER_NOT_ALLOWED",
                "blocker reason is only legal for BLOCKED state",
            )
        if to_status == ActionWorkStatus.COMPLETED and not (
            completion_reference or ""
        ).strip():
            raise ActionWorkError(
                "WORK_COMPLETION_REFERENCE_REQUIRED",
                "COMPLETED transition requires internal completion reference",
            )
        if to_status != ActionWorkStatus.COMPLETED and completion_reference is not None:
            raise ActionWorkError(
                "WORK_COMPLETION_REFERENCE_NOT_ALLOWED",
                "completion reference is only legal for COMPLETED state",
            )

        transition = ActionWorkTransition(
            from_status=latest.status,
            to_status=to_status,
            actor_user_id=str(principal.user_id),
            occurred_at=stamp,
            blocker_reason=blocker_reason.strip() if blocker_reason else None,
            completion_reference=(
                completion_reference.strip() if completion_reference else None
            ),
        )
        history = (*latest.transition_history, transition)
        revision = latest.revision + 1
        identity = {
            "root_action_work_id": latest.root_action_work_id,
            "revision": revision,
            "parent_action_work_id": latest.action_work_id,
            "source_fingerprint": latest.source_fingerprint,
            "title": latest.title,
            "work_intent": latest.work_intent,
            "owner_user_id": latest.owner_user_id,
            "due_at": latest.due_at.isoformat() if latest.due_at else None,
            "status": to_status.value,
            "blocker_reason": transition.blocker_reason,
            "completion_reference": transition.completion_reference,
            "transition_history": [
                item.model_dump(mode="json") for item in history
            ],
        }
        work_fingerprint = _canonical(
            identity,
            code="WORK_NOT_CANONICAL",
        )[1]
        action_work_id_new = "wrk_" + work_fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(ActionWorkRecord, action_work_id_new)
            if existing is not None:
                return self._hydrate(existing)
            row = ActionWorkRecord(
                action_work_id=action_work_id_new,
                root_action_work_id=latest.root_action_work_id,
                revision=revision,
                parent_action_work_id=latest.action_work_id,
                tenant_binding=latest.tenant_binding,
                decision_brief_id=latest.decision_brief_id,
                decision_brief_fingerprint=latest.decision_brief_fingerprint,
                decision_adoption_id=latest.decision_adoption_id,
                decision_adoption_fingerprint=latest.decision_adoption_fingerprint,
                action_authorization_id=latest.action_authorization_id,
                action_authorization_fingerprint=latest.action_authorization_fingerprint,
                title=latest.title,
                work_intent_json=_canonical(
                    latest.work_intent,
                    code="WORK_INTENT_NOT_CANONICAL",
                )[0],
                owner_user_id=latest.owner_user_id,
                owner_context_json=_canonical(
                    latest.owner_context,
                    code="WORK_OWNER_CONTEXT_NOT_CANONICAL",
                )[0],
                due_at=latest.due_at,
                status=to_status.value,
                blocker_reason=transition.blocker_reason,
                completion_reference=transition.completion_reference,
                transition_history_json=_canonical(
                    [item.model_dump(mode="json") for item in history],
                    code="WORK_HISTORY_NOT_CANONICAL",
                )[0],
                source_fingerprint=latest.source_fingerprint,
                work_fingerprint=work_fingerprint,
                created_at=stamp,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def currentness(
        self,
        *,
        action_work_id: str,
        principal: Principal,
    ) -> ActionWorkCurrentness:
        work = self.load(action_work_id=action_work_id, principal=principal)
        latest = self.latest(
            root_action_work_id=work.root_action_work_id,
            principal=principal,
        )
        if latest.action_work_id != work.action_work_id:
            return ActionWorkCurrentness.SUPERSEDED
        try:
            adoption_state = self._adoptions.currentness(
                adoption_id=work.decision_adoption_id,
                principal=principal,
            )
        except AdoptionError:
            return ActionWorkCurrentness.SOURCE_ADOPTION_STALE
        if adoption_state != AdoptionCurrentness.CURRENT:
            return ActionWorkCurrentness.SOURCE_ADOPTION_STALE
        return ActionWorkCurrentness.CURRENT
