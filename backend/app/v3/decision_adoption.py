"""Provider-free Human Adoption authority (DMP-DEC-0058).

Records what an authenticated, authorized human decided about one exact
CURRENT P21 DecisionBrief. It owns no analytics, recommendation generation,
Action authorization, execution, external side effects, or legacy DecisionRecord writes.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.decision_intelligence import (
    DecisionBrief,
    DecisionBriefCurrentness,
    DecisionBriefStore,
    P21DecisionError,
)
from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.db import engine as control_plane_engine
from control_plane.models import DecisionAdoptionRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AdoptionError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class AdoptionDisposition(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    DEFERRED = "DEFERRED"


class AdoptionCurrentness(StrEnum):
    CURRENT = "CURRENT"
    SOURCE_BRIEF_STALE = "SOURCE_BRIEF_STALE"
    SUPERSEDED = "SUPERSEDED"


class DecisionAdoptionDraft(Frozen):
    decision_brief_id: str = Field(pattern=r"^p21b_[a-f0-9]{24}$")
    source_brief_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    disposition: AdoptionDisposition
    selected_option_ids: tuple[str, ...] = ()
    human_rationale: str | None = Field(default=None, max_length=4000)
    human_conditions: tuple[str, ...] = ()
    supersedes_adoption_id: str | None = Field(
        default=None,
        pattern=r"^adp_[a-f0-9]{24}$",
    )

    @model_validator(mode="after")
    def canonical_human_metadata(self):
        if len(self.selected_option_ids) != len(set(self.selected_option_ids)):
            raise ValueError("selected option ids must be unique")
        if any(not item.strip() for item in self.human_conditions):
            raise ValueError("human conditions cannot contain blank values")
        if len(self.human_conditions) != len(set(self.human_conditions)):
            raise ValueError("human conditions must be unique")
        if self.human_rationale is not None and not self.human_rationale.strip():
            raise ValueError("human rationale cannot be blank")
        return self


class DecisionAdoption(Frozen):
    adoption_id: str = Field(pattern=r"^adp_[a-f0-9]{24}$")
    decision_brief_id: str = Field(pattern=r"^p21b_[a-f0-9]{24}$")
    source_brief_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    tenant_binding: str = Field(min_length=1)
    actor_user_id: str = Field(min_length=1)
    actor_authorization_context: dict[str, Any]
    disposition: AdoptionDisposition
    selected_option_ids: tuple[str, ...]
    human_rationale: str | None
    human_conditions: tuple[str, ...]
    supersedes_adoption_id: str | None = Field(
        default=None,
        pattern=r"^adp_[a-f0-9]{24}$",
    )
    recorded_at: datetime
    adoption_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


def _canonical_json(value: Any, *, code: str) -> tuple[str, str]:
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
        raise AdoptionError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise AdoptionError(
            "ADOPTION_TIMEZONE_REQUIRED",
            "recorded_at must be timezone-aware",
        )
    return stamp


def _tenant_binding(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise AdoptionError(
        "ADOPTION_TENANT_REQUIRED",
        "explicit tenant binding is required",
    )


def _actor_context(principal: Principal) -> dict[str, Any]:
    user_id = str(principal.user_id).strip()
    if not user_id:
        raise AdoptionError(
            "ADOPTION_ACTOR_REQUIRED",
            "authenticated actor is required",
        )
    return {
        "user_id": user_id,
        "tenant_binding": _tenant_binding(principal),
        "roles": sorted(set(principal.roles)),
        "is_superadmin": bool(principal.is_superadmin),
        "authorization_action": "decision:adopt",
    }


class AdoptionLegalityGate:
    """Deterministic legality gate over one exact CURRENT DecisionBrief."""

    def __init__(self, *, decision_store: DecisionBriefStore, db_engine=None) -> None:
        self._decisions = decision_store
        self._engine = db_engine or control_plane_engine

    def _authorize(self, principal: Principal, decision_brief_id: str) -> None:
        try:
            authorize(
                principal,
                "decision:adopt",
                f"decision-brief:{decision_brief_id}",
            )
        except AuthzError as exc:
            raise AdoptionError(
                "ADOPTION_FORBIDDEN",
                "principal is not authorized to adopt decisions",
            ) from exc

    def _brief(
        self,
        *,
        draft: DecisionAdoptionDraft,
        principal: Principal,
    ) -> DecisionBrief:
        self._authorize(principal, draft.decision_brief_id)
        try:
            brief = self._decisions.load(
                decision_brief_id=draft.decision_brief_id,
                principal=principal,
            )
            currentness = self._decisions.currentness(
                decision_brief_id=draft.decision_brief_id,
                principal=principal,
            )
        except P21DecisionError as exc:
            raise AdoptionError(
                "ADOPTION_DECISION_BRIEF_UNAVAILABLE",
                "decision brief unavailable in caller scope",
            ) from exc
        if currentness != DecisionBriefCurrentness.CURRENT:
            raise AdoptionError(
                "ADOPTION_DECISION_BRIEF_NOT_CURRENT",
                currentness.value,
            )
        if brief.brief_fingerprint != draft.source_brief_fingerprint:
            raise AdoptionError(
                "ADOPTION_SOURCE_FINGERPRINT_MISMATCH",
                draft.decision_brief_id,
            )
        if brief.tenant_binding != _tenant_binding(principal):
            raise AdoptionError(
                "ADOPTION_DECISION_BRIEF_UNAVAILABLE",
                "decision brief unavailable in caller scope",
            )
        return brief

    @staticmethod
    def _normalize_selected(
        brief: DecisionBrief,
        selected_option_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        option_ids = tuple(item.option_id for item in brief.options)
        known = set(option_ids)
        unknown = tuple(item for item in selected_option_ids if item not in known)
        if unknown:
            raise AdoptionError(
                "ADOPTION_OPTION_UNKNOWN",
                ",".join(unknown),
            )
        selected = set(selected_option_ids)
        return tuple(item for item in option_ids if item in selected)

    @staticmethod
    def _validate_disposition(
        *,
        brief: DecisionBrief,
        disposition: AdoptionDisposition,
        selected: tuple[str, ...],
    ) -> None:
        recommended = tuple(brief.recommendation.recommended_option_ids)
        if disposition == AdoptionDisposition.ACCEPTED:
            if set(selected) != set(recommended) or len(selected) != len(recommended):
                raise AdoptionError(
                    "ADOPTION_ACCEPTED_OPTIONS_MISMATCH",
                    brief.decision_brief_id,
                )
            return
        if disposition in {
            AdoptionDisposition.REJECTED,
            AdoptionDisposition.DEFERRED,
        }:
            if selected:
                raise AdoptionError(
                    "ADOPTION_EMPTY_SELECTION_REQUIRED",
                    disposition.value,
                )
            return
        if disposition == AdoptionDisposition.MODIFIED:
            if not selected:
                raise AdoptionError(
                    "ADOPTION_MODIFIED_SELECTION_REQUIRED",
                    brief.decision_brief_id,
                )
            if set(selected) == set(recommended) and len(selected) == len(recommended):
                raise AdoptionError(
                    "ADOPTION_MODIFIED_MUST_DIFFER",
                    brief.decision_brief_id,
                )
            return
        raise AdoptionError(
            "ADOPTION_DISPOSITION_UNSUPPORTED",
            str(disposition),
        )

    def _latest_for_stream(
        self,
        *,
        tenant_binding: str,
        decision_brief_id: str,
        actor_user_id: str,
    ) -> DecisionAdoptionRecord | None:
        with Session(self._engine) as db:
            return db.exec(
                select(DecisionAdoptionRecord)
                .where(
                    DecisionAdoptionRecord.tenant_binding
                    == tenant_binding
                )
                .where(
                    DecisionAdoptionRecord.decision_brief_id
                    == decision_brief_id
                )
                .where(
                    DecisionAdoptionRecord.actor_user_id
                    == actor_user_id
                )
                .order_by(DecisionAdoptionRecord.recorded_at.desc())
            ).first()

    def validate(
        self,
        *,
        draft: DecisionAdoptionDraft,
        principal: Principal,
    ) -> tuple[
        DecisionBrief,
        tuple[str, ...],
        dict[str, Any],
        DecisionAdoptionRecord | None,
        str,
    ]:
        brief = self._brief(draft=draft, principal=principal)
        selected = self._normalize_selected(
            brief,
            draft.selected_option_ids,
        )
        self._validate_disposition(
            brief=brief,
            disposition=draft.disposition,
            selected=selected,
        )
        actor_context = _actor_context(principal)
        tenant_binding = actor_context["tenant_binding"]
        actor_user_id = actor_context["user_id"]
        identity = {
            "decision_brief_id": brief.decision_brief_id,
            "source_brief_fingerprint": brief.brief_fingerprint,
            "tenant_binding": tenant_binding,
            "actor_user_id": actor_user_id,
            "disposition": draft.disposition.value,
            "selected_option_ids": list(selected),
            "human_rationale": draft.human_rationale,
            "human_conditions": list(draft.human_conditions),
            "supersedes_adoption_id": draft.supersedes_adoption_id,
        }
        adoption_fingerprint = _canonical_json(
            identity,
            code="ADOPTION_IDENTITY_NOT_CANONICAL",
        )[1]

        latest = self._latest_for_stream(
            tenant_binding=tenant_binding,
            decision_brief_id=brief.decision_brief_id,
            actor_user_id=actor_user_id,
        )

        # Exact canonical retry is idempotent even though a latest event now exists.
        if latest is not None and latest.adoption_fingerprint == adoption_fingerprint:
            return (
                brief,
                selected,
                actor_context,
                latest,
                adoption_fingerprint,
            )

        if latest is None:
            if draft.supersedes_adoption_id is not None:
                raise AdoptionError(
                    "ADOPTION_SUPERSESSION_INVALID",
                    "no prior adoption exists for this stream",
                )
        elif draft.supersedes_adoption_id != latest.adoption_id:
            raise AdoptionError(
                "ADOPTION_SUPERSESSION_REQUIRED",
                latest.adoption_id,
            )

        if draft.supersedes_adoption_id is not None:
            with Session(self._engine) as db:
                prior = db.get(
                    DecisionAdoptionRecord,
                    draft.supersedes_adoption_id,
                )
            if (
                prior is None
                or prior.tenant_binding != tenant_binding
                or prior.decision_brief_id != brief.decision_brief_id
                or prior.actor_user_id != actor_user_id
                or latest is None
                or latest.adoption_id != prior.adoption_id
            ):
                raise AdoptionError(
                    "ADOPTION_SUPERSESSION_INVALID",
                    "prior adoption is unavailable or outside the actor/brief stream",
                )
        return (
            brief,
            selected,
            actor_context,
            latest,
            adoption_fingerprint,
        )


class DecisionAdoptionStore:
    """Single durable Human Adoption owner."""

    def __init__(
        self,
        *,
        decision_store: DecisionBriefStore,
        db_engine=None,
    ) -> None:
        self._decisions = decision_store
        self._engine = db_engine or control_plane_engine
        self._gate = AdoptionLegalityGate(
            decision_store=decision_store,
            db_engine=self._engine,
        )

    @staticmethod
    def _hydrate(row: DecisionAdoptionRecord) -> DecisionAdoption:
        try:
            actor_context = json.loads(row.actor_authorization_context_json)
            selected = json.loads(row.selected_option_ids_json)
            conditions = json.loads(row.human_conditions_json)
        except json.JSONDecodeError as exc:
            raise AdoptionError(
                "ADOPTION_PERSISTENCE_INVALID",
                row.adoption_id,
            ) from exc
        if (
            not isinstance(actor_context, dict)
            or not isinstance(selected, list)
            or not isinstance(conditions, list)
        ):
            raise AdoptionError(
                "ADOPTION_PERSISTENCE_INVALID",
                row.adoption_id,
            )
        return DecisionAdoption(
            adoption_id=row.adoption_id,
            decision_brief_id=row.decision_brief_id,
            source_brief_fingerprint=row.source_brief_fingerprint,
            tenant_binding=row.tenant_binding,
            actor_user_id=row.actor_user_id,
            actor_authorization_context=actor_context,
            disposition=AdoptionDisposition(row.disposition),
            selected_option_ids=tuple(selected),
            human_rationale=row.human_rationale,
            human_conditions=tuple(conditions),
            supersedes_adoption_id=row.supersedes_adoption_id,
            recorded_at=row.recorded_at,
            adoption_fingerprint=row.adoption_fingerprint,
        )

    def record(
        self,
        *,
        draft: DecisionAdoptionDraft,
        principal: Principal,
        now: datetime | None = None,
    ) -> DecisionAdoption:
        (
            brief,
            selected,
            actor_context,
            _latest,
            adoption_fingerprint,
        ) = self._gate.validate(
            draft=draft,
            principal=principal,
        )
        adoption_id = "adp_" + adoption_fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(DecisionAdoptionRecord, adoption_id)
            if existing is not None:
                if existing.adoption_fingerprint != adoption_fingerprint:
                    raise AdoptionError(
                        "ADOPTION_IDENTITY_CONFLICT",
                        adoption_id,
                    )
                return self._hydrate(existing)

            row = DecisionAdoptionRecord(
                adoption_id=adoption_id,
                decision_brief_id=brief.decision_brief_id,
                source_brief_fingerprint=brief.brief_fingerprint,
                tenant_binding=brief.tenant_binding,
                actor_user_id=str(principal.user_id),
                actor_authorization_context_json=_canonical_json(
                    actor_context,
                    code="ADOPTION_ACTOR_CONTEXT_NOT_CANONICAL",
                )[0],
                disposition=draft.disposition.value,
                selected_option_ids_json=_canonical_json(
                    list(selected),
                    code="ADOPTION_OPTIONS_NOT_CANONICAL",
                )[0],
                human_rationale=draft.human_rationale,
                human_conditions_json=_canonical_json(
                    list(draft.human_conditions),
                    code="ADOPTION_CONDITIONS_NOT_CANONICAL",
                )[0],
                supersedes_adoption_id=draft.supersedes_adoption_id,
                recorded_at=_aware(now),
                adoption_fingerprint=adoption_fingerprint,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(
        self,
        *,
        adoption_id: str,
        principal: Principal,
    ) -> DecisionAdoption:
        try:
            tenant_binding = _tenant_binding(principal)
        except AdoptionError as exc:
            raise AdoptionError(
                "ADOPTION_UNAVAILABLE",
                "adoption unavailable in caller scope",
            ) from exc
        with Session(self._engine) as db:
            row = db.get(DecisionAdoptionRecord, adoption_id)
            if row is None or row.tenant_binding != tenant_binding:
                raise AdoptionError(
                    "ADOPTION_UNAVAILABLE",
                    "adoption unavailable in caller scope",
                )
            return self._hydrate(row)

    def currentness(
        self,
        *,
        adoption_id: str,
        principal: Principal,
    ) -> AdoptionCurrentness:
        adoption = self.load(
            adoption_id=adoption_id,
            principal=principal,
        )
        try:
            brief = self._decisions.load(
                decision_brief_id=adoption.decision_brief_id,
                principal=principal,
            )
            brief_currentness = self._decisions.currentness(
                decision_brief_id=adoption.decision_brief_id,
                principal=principal,
            )
        except P21DecisionError:
            return AdoptionCurrentness.SOURCE_BRIEF_STALE
        if (
            brief_currentness != DecisionBriefCurrentness.CURRENT
            or brief.brief_fingerprint != adoption.source_brief_fingerprint
        ):
            return AdoptionCurrentness.SOURCE_BRIEF_STALE
        with Session(self._engine) as db:
            latest = db.exec(
                select(DecisionAdoptionRecord)
                .where(
                    DecisionAdoptionRecord.tenant_binding
                    == adoption.tenant_binding
                )
                .where(
                    DecisionAdoptionRecord.decision_brief_id
                    == adoption.decision_brief_id
                )
                .where(
                    DecisionAdoptionRecord.actor_user_id
                    == adoption.actor_user_id
                )
                .order_by(DecisionAdoptionRecord.recorded_at.desc())
            ).first()
        if latest is None or latest.adoption_id != adoption.adoption_id:
            return AdoptionCurrentness.SUPERSEDED
        return AdoptionCurrentness.CURRENT
