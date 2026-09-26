"""Provider-free ActionPlan + ActionAuthorization authority (DMP-DEC-0059).

This module authorizes an exact canonical side-effect artifact. It never executes
that artifact and owns no analytics, connector transport, or external calls.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from sqlmodel import Session, select

from app.v3.decision_adoption import (
    AdoptionCurrentness,
    AdoptionDisposition,
    AdoptionError,
    DecisionAdoption,
    DecisionAdoptionStore,
)
from app.v3.decision_intelligence import DecisionBrief, DecisionBriefStore, P21DecisionError
from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.db import engine as control_plane_engine
from control_plane.models import ActionAuthorizationRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ActionAuthorityError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ActionRiskClass(StrEnum):
    REVERSIBLE_LOW_RISK = "REVERSIBLE_LOW_RISK"
    REVERSIBLE_MATERIAL = "REVERSIBLE_MATERIAL"
    IRREVERSIBLE_EXTERNAL_COMMIT = "IRREVERSIBLE_EXTERNAL_COMMIT"


class Reversibility(StrEnum):
    REVERSIBLE = "REVERSIBLE"
    COMPENSATABLE = "COMPENSATABLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class ConfirmationRequirement(StrEnum):
    EXPLICIT_AUTHORIZATION = "EXPLICIT_AUTHORIZATION"
    DUAL_APPROVAL = "DUAL_APPROVAL"


class AuthorizationCurrentness(StrEnum):
    CURRENT = "CURRENT"
    SOURCE_ADOPTION_STALE = "SOURCE_ADOPTION_STALE"
    EXPIRED = "EXPIRED"
    CAPABILITY_STALE = "CAPABILITY_STALE"
    SUPERSEDED = "SUPERSEDED"


@dataclass(frozen=True)
class ActionCapabilitySpec:
    capability_key: str
    action_kind: str
    version: str
    target_system: str
    parameter_model: type[BaseModel]
    risk_class: ActionRiskClass
    reversibility: Reversibility
    confirmation_requirement: ConfirmationRequirement
    authorization_policy_id: str
    authorization_policy_version: str
    idempotency_strategy: str
    authorization_ttl_seconds: int

    def __post_init__(self) -> None:
        for value in (
            self.capability_key,
            self.action_kind,
            self.version,
            self.target_system,
            self.authorization_policy_id,
            self.authorization_policy_version,
            self.idempotency_strategy,
        ):
            if not str(value).strip():
                raise ValueError("capability metadata cannot be blank")
        if not issubclass(self.parameter_model, BaseModel):
            raise TypeError("parameter_model must be a Pydantic BaseModel")
        if self.authorization_ttl_seconds <= 0:
            raise ValueError("authorization_ttl_seconds must be positive")

    @property
    def fingerprint(self) -> str:
        identity = {
            "capability_key": self.capability_key,
            "action_kind": self.action_kind,
            "version": self.version,
            "target_system": self.target_system,
            "parameter_schema": self.parameter_model.model_json_schema(),
            "risk_class": self.risk_class.value,
            "reversibility": self.reversibility.value,
            "confirmation_requirement": self.confirmation_requirement.value,
            "authorization_policy_id": self.authorization_policy_id,
            "authorization_policy_version": self.authorization_policy_version,
            "idempotency_strategy": self.idempotency_strategy,
            "authorization_ttl_seconds": self.authorization_ttl_seconds,
        }
        return _canonical_json(
            identity,
            code="ACTION_CAPABILITY_NOT_CANONICAL",
        )[1]


class ActionCapabilityRegistry:
    """Trusted server-side allowlist. Production default intentionally starts empty."""

    def __init__(self, capabilities: tuple[ActionCapabilitySpec, ...] = ()) -> None:
        by_kind: dict[str, ActionCapabilitySpec] = {}
        for item in capabilities:
            if item.action_kind in by_kind:
                raise ValueError(f"duplicate action kind: {item.action_kind}")
            by_kind[item.action_kind] = item
        self._by_kind = by_kind

    def require(self, action_kind: str) -> ActionCapabilitySpec:
        spec = self._by_kind.get(action_kind)
        if spec is None:
            raise ActionAuthorityError(
                "ACTION_CAPABILITY_UNAVAILABLE",
                "action kind is not registered",
            )
        return spec

    def get(self, action_kind: str) -> ActionCapabilitySpec | None:
        return self._by_kind.get(action_kind)


DEFAULT_ACTION_CAPABILITY_REGISTRY = ActionCapabilityRegistry()


class ActionPlanDraft(Frozen):
    action_kind: str = Field(min_length=1, max_length=160)
    target_system: str = Field(min_length=1, max_length=160)
    target_resource: str = Field(min_length=1, max_length=500)
    typed_parameters: dict[str, Any]
    source_option_ids: tuple[str, ...] = Field(min_length=1)

    decision_adoption_id: str = Field(pattern=r"^adp_[a-f0-9]{24}$")
    decision_adoption_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")

    decision_brief_id: str = Field(pattern=r"^p21b_[a-f0-9]{24}$")
    decision_brief_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")

    report_id: str = Field(pattern=r"^p20r_[a-f0-9]{24}$")
    report_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def unique_option_ids(self):
        if len(self.source_option_ids) != len(set(self.source_option_ids)):
            raise ValueError("source option ids must be unique")
        return self


class ActionPlan(Frozen):
    action_kind: str
    target_system: str
    target_resource: str
    typed_parameters: dict[str, Any]
    source_option_ids: tuple[str, ...]

    decision_adoption_id: str
    decision_adoption_fingerprint: str
    decision_brief_id: str
    decision_brief_fingerprint: str
    report_id: str
    report_fingerprint: str

    capability_key: str
    capability_version: str
    capability_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")

    risk_class: ActionRiskClass
    reversibility: Reversibility
    confirmation_requirement: ConfirmationRequirement
    idempotency_strategy: str
    authorization_policy_id: str
    authorization_policy_version: str

    plan_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class ActionAuthorization(Frozen):
    authorization_id: str = Field(pattern=r"^authz_[a-f0-9]{24}$")
    tenant_binding: str = Field(min_length=1)

    decision_brief_id: str
    decision_brief_fingerprint: str
    decision_adoption_id: str
    decision_adoption_fingerprint: str
    report_id: str
    report_fingerprint: str

    action_kind: str
    target_system: str
    target_resource: str
    canonical_plan: ActionPlan
    plan_fingerprint: str

    capability_key: str
    capability_version: str
    capability_fingerprint: str

    risk_class: ActionRiskClass
    reversibility: Reversibility
    confirmation_requirement: ConfirmationRequirement
    idempotency_strategy: str

    authorization_policy_id: str
    authorization_policy_version: str

    authorizer_user_id: str
    authorizer_context: dict[str, Any]

    issued_at: datetime
    expires_at: datetime
    supersedes_authorization_id: str | None = None
    authorization_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


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
        raise ActionAuthorityError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ActionAuthorityError(
            "ACTION_TIMEZONE_REQUIRED",
            "timestamp must be timezone-aware",
        )
    return stamp


def _tenant_binding(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise ActionAuthorityError(
        "ACTION_TENANT_REQUIRED",
        "explicit tenant binding is required",
    )


def _authorizer_context(principal: Principal) -> dict[str, Any]:
    user_id = str(principal.user_id).strip()
    if not user_id:
        raise ActionAuthorityError(
            "ACTION_AUTHORIZER_REQUIRED",
            "authenticated authorizer is required",
        )
    return {
        "user_id": user_id,
        "tenant_binding": _tenant_binding(principal),
        "roles": sorted(set(principal.roles)),
        "is_superadmin": bool(principal.is_superadmin),
        "authorization_action": "action:authorize",
    }


class ActionPlanLegalityGate:
    """Builds one canonical non-executing ActionPlan from trusted authority."""

    def __init__(
        self,
        *,
        adoption_store: DecisionAdoptionStore,
        decision_store: DecisionBriefStore,
        registry: ActionCapabilityRegistry = DEFAULT_ACTION_CAPABILITY_REGISTRY,
    ) -> None:
        self._adoptions = adoption_store
        self._decisions = decision_store
        self._registry = registry

    def _sources(
        self,
        *,
        draft: ActionPlanDraft,
        principal: Principal,
    ) -> tuple[DecisionAdoption, DecisionBrief]:
        try:
            adoption = self._adoptions.load(
                adoption_id=draft.decision_adoption_id,
                principal=principal,
            )
            adoption_currentness = self._adoptions.currentness(
                adoption_id=draft.decision_adoption_id,
                principal=principal,
            )
        except AdoptionError as exc:
            raise ActionAuthorityError(
                "ACTION_SOURCE_ADOPTION_UNAVAILABLE",
                "source adoption unavailable in caller scope",
            ) from exc
        if adoption_currentness != AdoptionCurrentness.CURRENT:
            raise ActionAuthorityError(
                "ACTION_SOURCE_ADOPTION_NOT_CURRENT",
                adoption_currentness.value,
            )
        if adoption.disposition != AdoptionDisposition.ACCEPTED:
            raise ActionAuthorityError(
                "ACTION_SOURCE_ADOPTION_NOT_ACCEPTED",
                adoption.disposition.value,
            )
        if adoption.adoption_fingerprint != draft.decision_adoption_fingerprint:
            raise ActionAuthorityError(
                "ACTION_ADOPTION_FINGERPRINT_MISMATCH",
                adoption.adoption_id,
            )
        if adoption.decision_brief_id != draft.decision_brief_id:
            raise ActionAuthorityError(
                "ACTION_DECISION_BRIEF_MISMATCH",
                adoption.adoption_id,
            )

        try:
            brief = self._decisions.load(
                decision_brief_id=adoption.decision_brief_id,
                principal=principal,
            )
        except P21DecisionError as exc:
            raise ActionAuthorityError(
                "ACTION_SOURCE_DECISION_UNAVAILABLE",
                "source decision unavailable in caller scope",
            ) from exc
        if brief.brief_fingerprint != draft.decision_brief_fingerprint:
            raise ActionAuthorityError(
                "ACTION_DECISION_FINGERPRINT_MISMATCH",
                brief.decision_brief_id,
            )
        if brief.report_id != draft.report_id:
            raise ActionAuthorityError(
                "ACTION_REPORT_ID_MISMATCH",
                brief.decision_brief_id,
            )
        if brief.source_report_fingerprint != draft.report_fingerprint:
            raise ActionAuthorityError(
                "ACTION_REPORT_FINGERPRINT_MISMATCH",
                brief.decision_brief_id,
            )
        if adoption.tenant_binding != _tenant_binding(principal) or brief.tenant_binding != adoption.tenant_binding:
            raise ActionAuthorityError(
                "ACTION_SOURCE_ADOPTION_UNAVAILABLE",
                "source adoption unavailable in caller scope",
            )
        return adoption, brief

    @staticmethod
    def _validate_source_options(
        adoption: DecisionAdoption,
        source_option_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        selected = tuple(adoption.selected_option_ids)
        selected_set = set(selected)
        unknown = tuple(item for item in source_option_ids if item not in selected_set)
        if unknown:
            raise ActionAuthorityError(
                "ACTION_SOURCE_OPTION_NOT_ADOPTED",
                ",".join(unknown),
            )
        return tuple(item for item in selected if item in set(source_option_ids))

    @staticmethod
    def _validate_parameters(
        spec: ActionCapabilitySpec,
        raw: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            model = spec.parameter_model.model_validate(raw)
        except ValidationError as exc:
            raise ActionAuthorityError(
                "ACTION_PARAMETERS_INVALID",
                "parameters failed trusted capability schema",
            ) from exc
        value = model.model_dump(mode="json")
        _canonical_json(value, code="ACTION_PARAMETERS_NOT_CANONICAL")
        return value

    def build(
        self,
        *,
        draft: ActionPlanDraft,
        principal: Principal,
    ) -> ActionPlan:
        adoption, brief = self._sources(draft=draft, principal=principal)
        spec = self._registry.require(draft.action_kind)
        if spec.target_system != draft.target_system:
            raise ActionAuthorityError(
                "ACTION_TARGET_SYSTEM_MISMATCH",
                draft.target_system,
            )
        if spec.risk_class != ActionRiskClass.REVERSIBLE_LOW_RISK:
            raise ActionAuthorityError(
                "ACTION_RISK_NOT_SUPPORTED_IN_FIRST_SLICE",
                spec.risk_class.value,
            )
        if spec.confirmation_requirement != ConfirmationRequirement.EXPLICIT_AUTHORIZATION:
            raise ActionAuthorityError(
                "ACTION_CONFIRMATION_NOT_SUPPORTED_IN_FIRST_SLICE",
                spec.confirmation_requirement.value,
            )

        parameters = self._validate_parameters(spec, draft.typed_parameters)
        source_option_ids = self._validate_source_options(
            adoption,
            draft.source_option_ids,
        )

        identity = {
            "action_kind": spec.action_kind,
            "target_system": spec.target_system,
            "target_resource": draft.target_resource,
            "typed_parameters": parameters,
            "source_option_ids": list(source_option_ids),
            "decision_adoption_id": adoption.adoption_id,
            "decision_adoption_fingerprint": adoption.adoption_fingerprint,
            "decision_brief_id": brief.decision_brief_id,
            "decision_brief_fingerprint": brief.brief_fingerprint,
            "report_id": brief.report_id,
            "report_fingerprint": brief.source_report_fingerprint,
            "capability_key": spec.capability_key,
            "capability_version": spec.version,
            "capability_fingerprint": spec.fingerprint,
            "risk_class": spec.risk_class.value,
            "reversibility": spec.reversibility.value,
            "confirmation_requirement": spec.confirmation_requirement.value,
            "idempotency_strategy": spec.idempotency_strategy,
            "authorization_policy_id": spec.authorization_policy_id,
            "authorization_policy_version": spec.authorization_policy_version,
        }
        plan_fingerprint = _canonical_json(
            identity,
            code="ACTION_PLAN_NOT_CANONICAL",
        )[1]
        return ActionPlan(
            **identity,
            plan_fingerprint=plan_fingerprint,
        )


class ActionAuthorizationGate:
    """Adds Principal authorization and trusted lifetime/policy to a legal plan."""

    def __init__(
        self,
        *,
        plan_gate: ActionPlanLegalityGate,
        registry: ActionCapabilityRegistry = DEFAULT_ACTION_CAPABILITY_REGISTRY,
    ) -> None:
        self._plan_gate = plan_gate
        self._registry = registry

    def validate(
        self,
        *,
        draft: ActionPlanDraft,
        principal: Principal,
    ) -> tuple[ActionPlan, ActionCapabilitySpec, dict[str, Any]]:
        try:
            authorize(
                principal,
                "action:authorize",
                f"action:{draft.action_kind}",
            )
        except AuthzError as exc:
            raise ActionAuthorityError(
                "ACTION_AUTHORIZATION_FORBIDDEN",
                "principal cannot authorize actions",
            ) from exc
        plan = self._plan_gate.build(draft=draft, principal=principal)
        spec = self._registry.require(plan.action_kind)
        if spec.fingerprint != plan.capability_fingerprint:
            raise ActionAuthorityError(
                "ACTION_CAPABILITY_STALE",
                plan.action_kind,
            )
        return plan, spec, _authorizer_context(principal)


class ActionAuthorizationStore:
    """Single durable owner for immutable authorization of exact ActionPlans."""

    def __init__(
        self,
        *,
        adoption_store: DecisionAdoptionStore,
        decision_store: DecisionBriefStore,
        registry: ActionCapabilityRegistry = DEFAULT_ACTION_CAPABILITY_REGISTRY,
        db_engine=None,
    ) -> None:
        self._adoptions = adoption_store
        self._decisions = decision_store
        self._registry = registry
        self._engine = db_engine or control_plane_engine
        self._plan_gate = ActionPlanLegalityGate(
            adoption_store=adoption_store,
            decision_store=decision_store,
            registry=registry,
        )
        self._gate = ActionAuthorizationGate(
            plan_gate=self._plan_gate,
            registry=registry,
        )

    @staticmethod
    def _hydrate(row: ActionAuthorizationRecord) -> ActionAuthorization:
        try:
            plan_raw = json.loads(row.canonical_plan_json)
            authorizer_context = json.loads(row.authorizer_context_json)
        except json.JSONDecodeError as exc:
            raise ActionAuthorityError(
                "ACTION_AUTHORIZATION_PERSISTENCE_INVALID",
                row.authorization_id,
            ) from exc
        if not isinstance(plan_raw, dict) or not isinstance(authorizer_context, dict):
            raise ActionAuthorityError(
                "ACTION_AUTHORIZATION_PERSISTENCE_INVALID",
                row.authorization_id,
            )
        plan = ActionPlan.model_validate(plan_raw)
        if plan.plan_fingerprint != row.plan_fingerprint:
            raise ActionAuthorityError(
                "ACTION_PLAN_SNAPSHOT_MISMATCH",
                row.authorization_id,
            )
        return ActionAuthorization(
            authorization_id=row.authorization_id,
            tenant_binding=row.tenant_binding,
            decision_brief_id=row.decision_brief_id,
            decision_brief_fingerprint=row.decision_brief_fingerprint,
            decision_adoption_id=row.decision_adoption_id,
            decision_adoption_fingerprint=row.decision_adoption_fingerprint,
            report_id=row.report_id,
            report_fingerprint=row.report_fingerprint,
            action_kind=row.action_kind,
            target_system=row.target_system,
            target_resource=row.target_resource,
            canonical_plan=plan,
            plan_fingerprint=row.plan_fingerprint,
            capability_key=row.capability_key,
            capability_version=row.capability_version,
            capability_fingerprint=row.capability_fingerprint,
            risk_class=ActionRiskClass(row.risk_class),
            reversibility=Reversibility(row.reversibility),
            confirmation_requirement=ConfirmationRequirement(row.confirmation_requirement),
            idempotency_strategy=row.idempotency_strategy,
            authorization_policy_id=row.authorization_policy_id,
            authorization_policy_version=row.authorization_policy_version,
            authorizer_user_id=row.authorizer_user_id,
            authorizer_context=authorizer_context,
            issued_at=row.issued_at,
            expires_at=row.expires_at,
            supersedes_authorization_id=row.supersedes_authorization_id,
            authorization_fingerprint=row.authorization_fingerprint,
        )

    def _latest_stream(
        self,
        *,
        tenant_binding: str,
        adoption_id: str,
        action_kind: str,
        target_system: str,
        target_resource: str,
        authorizer_user_id: str,
    ) -> ActionAuthorizationRecord | None:
        with Session(self._engine) as db:
            return db.exec(
                select(ActionAuthorizationRecord)
                .where(ActionAuthorizationRecord.tenant_binding == tenant_binding)
                .where(ActionAuthorizationRecord.decision_adoption_id == adoption_id)
                .where(ActionAuthorizationRecord.action_kind == action_kind)
                .where(ActionAuthorizationRecord.target_system == target_system)
                .where(ActionAuthorizationRecord.target_resource == target_resource)
                .where(ActionAuthorizationRecord.authorizer_user_id == authorizer_user_id)
                .order_by(ActionAuthorizationRecord.issued_at.desc())
            ).first()

    def authorize(
        self,
        *,
        draft: ActionPlanDraft,
        principal: Principal,
        supersedes_authorization_id: str | None = None,
        now: datetime | None = None,
    ) -> ActionAuthorization:
        plan, spec, authorizer_context = self._gate.validate(
            draft=draft,
            principal=principal,
        )
        issued_at = _aware(now)
        tenant_binding = _tenant_binding(principal)
        authorizer_user_id = str(principal.user_id)

        identity = {
            "tenant_binding": tenant_binding,
            "plan_fingerprint": plan.plan_fingerprint,
            "authorizer_user_id": authorizer_user_id,
            "capability_key": spec.capability_key,
            "capability_version": spec.version,
            "capability_fingerprint": spec.fingerprint,
            "authorization_policy_id": spec.authorization_policy_id,
            "authorization_policy_version": spec.authorization_policy_version,
            "supersedes_authorization_id": supersedes_authorization_id,
        }
        authorization_fingerprint = _canonical_json(
            identity,
            code="ACTION_AUTHORIZATION_NOT_CANONICAL",
        )[1]
        authorization_id = "authz_" + authorization_fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(ActionAuthorizationRecord, authorization_id)
        if existing is not None:
            hydrated = self._hydrate(existing)
            if self.currentness(
                authorization_id=hydrated.authorization_id,
                principal=principal,
                now=issued_at,
            ) == AuthorizationCurrentness.CURRENT:
                return hydrated
            raise ActionAuthorityError(
                "ACTION_REAUTHORIZATION_REQUIRED",
                hydrated.authorization_id,
            )

        latest = self._latest_stream(
            tenant_binding=tenant_binding,
            adoption_id=plan.decision_adoption_id,
            action_kind=plan.action_kind,
            target_system=plan.target_system,
            target_resource=plan.target_resource,
            authorizer_user_id=authorizer_user_id,
        )
        if latest is None:
            if supersedes_authorization_id is not None:
                raise ActionAuthorityError(
                    "ACTION_SUPERSESSION_INVALID",
                    "no prior authorization exists for this stream",
                )
        elif supersedes_authorization_id != latest.authorization_id:
            raise ActionAuthorityError(
                "ACTION_SUPERSESSION_REQUIRED",
                latest.authorization_id,
            )

        if supersedes_authorization_id is not None:
            with Session(self._engine) as db:
                prior = db.get(ActionAuthorizationRecord, supersedes_authorization_id)
            if (
                prior is None
                or prior.tenant_binding != tenant_binding
                or prior.decision_adoption_id != plan.decision_adoption_id
                or prior.action_kind != plan.action_kind
                or prior.target_system != plan.target_system
                or prior.target_resource != plan.target_resource
                or prior.authorizer_user_id != authorizer_user_id
                or latest is None
                or latest.authorization_id != prior.authorization_id
            ):
                raise ActionAuthorityError(
                    "ACTION_SUPERSESSION_INVALID",
                    "prior authorization is outside the same action stream",
                )

        expires_at = issued_at + timedelta(seconds=spec.authorization_ttl_seconds)
        canonical_plan_json = _canonical_json(
            plan.model_dump(mode="json"),
            code="ACTION_PLAN_SNAPSHOT_NOT_CANONICAL",
        )[0]
        authorizer_context_json = _canonical_json(
            authorizer_context,
            code="ACTION_AUTHORIZER_CONTEXT_NOT_CANONICAL",
        )[0]
        row = ActionAuthorizationRecord(
            authorization_id=authorization_id,
            tenant_binding=tenant_binding,
            decision_brief_id=plan.decision_brief_id,
            decision_brief_fingerprint=plan.decision_brief_fingerprint,
            decision_adoption_id=plan.decision_adoption_id,
            decision_adoption_fingerprint=plan.decision_adoption_fingerprint,
            report_id=plan.report_id,
            report_fingerprint=plan.report_fingerprint,
            action_kind=plan.action_kind,
            target_system=plan.target_system,
            target_resource=plan.target_resource,
            canonical_plan_json=canonical_plan_json,
            plan_fingerprint=plan.plan_fingerprint,
            capability_key=plan.capability_key,
            capability_version=plan.capability_version,
            capability_fingerprint=plan.capability_fingerprint,
            risk_class=plan.risk_class.value,
            reversibility=plan.reversibility.value,
            confirmation_requirement=plan.confirmation_requirement.value,
            idempotency_strategy=plan.idempotency_strategy,
            authorization_policy_id=plan.authorization_policy_id,
            authorization_policy_version=plan.authorization_policy_version,
            authorizer_user_id=authorizer_user_id,
            authorizer_context_json=authorizer_context_json,
            issued_at=issued_at,
            expires_at=expires_at,
            supersedes_authorization_id=supersedes_authorization_id,
            authorization_fingerprint=authorization_fingerprint,
        )
        with Session(self._engine) as db:
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(
        self,
        *,
        authorization_id: str,
        principal: Principal,
    ) -> ActionAuthorization:
        tenant_binding = _tenant_binding(principal)
        with Session(self._engine) as db:
            row = db.get(ActionAuthorizationRecord, authorization_id)
            if row is None or row.tenant_binding != tenant_binding:
                raise ActionAuthorityError(
                    "ACTION_AUTHORIZATION_UNAVAILABLE",
                    "authorization unavailable in caller scope",
                )
            return self._hydrate(row)

    def currentness(
        self,
        *,
        authorization_id: str,
        principal: Principal,
        now: datetime | None = None,
    ) -> AuthorizationCurrentness:
        authz = self.load(authorization_id=authorization_id, principal=principal)
        stamp = _aware(now)
        if stamp >= authz.expires_at:
            return AuthorizationCurrentness.EXPIRED
        try:
            adoption_state = self._adoptions.currentness(
                adoption_id=authz.decision_adoption_id,
                principal=principal,
            )
        except AdoptionError:
            return AuthorizationCurrentness.SOURCE_ADOPTION_STALE
        if adoption_state != AdoptionCurrentness.CURRENT:
            return AuthorizationCurrentness.SOURCE_ADOPTION_STALE

        spec = self._registry.get(authz.action_kind)
        if (
            spec is None
            or spec.version != authz.capability_version
            or spec.fingerprint != authz.capability_fingerprint
        ):
            return AuthorizationCurrentness.CAPABILITY_STALE

        latest = self._latest_stream(
            tenant_binding=authz.tenant_binding,
            adoption_id=authz.decision_adoption_id,
            action_kind=authz.action_kind,
            target_system=authz.target_system,
            target_resource=authz.target_resource,
            authorizer_user_id=authz.authorizer_user_id,
        )
        if latest is None or latest.authorization_id != authz.authorization_id:
            return AuthorizationCurrentness.SUPERSEDED
        return AuthorizationCurrentness.CURRENT
