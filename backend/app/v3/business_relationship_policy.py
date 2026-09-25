"""P18 minimal material-business-relationship policy authority.

P18 validates an explicit typed business-interpretation requirement against one
governed policy. It never discovers joins, executes analytics, creates Evidence,
or owns causal semantics.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.research import ResearchManager, ResearchStateError
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import (
    BusinessRelationshipPolicyRecord,
    BusinessRelationshipPolicyUseRecord,
    ResearchClaimRecord,
    ResearchReasoningStepRecord,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class BusinessRelationshipPolicyError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class BusinessRelationshipPolicyStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class RelationshipPolicyResolutionStatus(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    SATISFIED = "SATISFIED"
    BLOCKED_MISSING = "BLOCKED_MISSING"
    BLOCKED_RETIRED = "BLOCKED_RETIRED"
    BLOCKED_TENANT = "BLOCKED_TENANT"
    BLOCKED_CONTEXT = "BLOCKED_CONTEXT"
    BLOCKED_SCOPE = "BLOCKED_SCOPE"


class RelationshipPolicyRequirement(Frozen):
    """Transient P18 input contract; never persisted as its own authority."""

    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    claim_id: str = Field(pattern=r"^clm_[a-f0-9]{24}$")
    reasoning_step_id: str = Field(pattern=r"^rrs_[a-f0-9]{24}$")
    policy_key: str = Field(min_length=1)
    source_business_ref: str = Field(min_length=1)
    target_business_ref: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    applicability_scope: dict[str, Any]
    required: bool = True

    @model_validator(mode="after")
    def exact_scope_required(self):
        if not self.applicability_scope:
            raise ValueError("P18 requires a non-empty exact applicability scope")
        return self


class BusinessRelationshipPolicy(Frozen):
    policy_id: str = Field(pattern=r"^brp_[a-f0-9]{24}$")
    tenant_binding: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    policy_key: str = Field(min_length=1)
    source_business_ref: str = Field(min_length=1)
    target_business_ref: str = Field(min_length=1)
    business_relationship_statement: str = Field(min_length=1)
    applicability_scope: dict[str, Any]
    applicability_scope_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    policy_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance_ref: str = Field(min_length=1)
    approved_by_subject: str = Field(min_length=1)
    status: BusinessRelationshipPolicyStatus
    created_at: datetime
    retired_at: datetime | None = None


class BusinessRelationshipPolicyUse(Frozen):
    policy_use_id: str = Field(pattern=r"^bru_[a-f0-9]{24}$")
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    claim_id: str = Field(pattern=r"^clm_[a-f0-9]{24}$")
    reasoning_step_id: str = Field(pattern=r"^rrs_[a-f0-9]{24}$")
    requirement_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    policy_id: str | None = Field(
        default=None,
        pattern=r"^brp_[a-f0-9]{24}$",
    )
    policy_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    resolution_status: RelationshipPolicyResolutionStatus
    limitation_code: str | None = None
    created_at: datetime


class RelationshipPolicyDecision(Frozen):
    required: bool
    eligible: bool
    resolution_status: RelationshipPolicyResolutionStatus
    policy_use_id: str = Field(pattern=r"^bru_[a-f0-9]{24}$")
    policy_id: str | None = Field(
        default=None,
        pattern=r"^brp_[a-f0-9]{24}$",
    )
    limitation_code: str | None = None

    @model_validator(mode="after")
    def coherent(self):
        eligible = self.resolution_status in {
            RelationshipPolicyResolutionStatus.NOT_REQUIRED,
            RelationshipPolicyResolutionStatus.SATISFIED,
        }
        if self.eligible != eligible:
            raise ValueError("P18 eligibility must follow deterministic resolution status")
        if self.resolution_status == RelationshipPolicyResolutionStatus.SATISFIED:
            if not self.required or self.policy_id is None or self.limitation_code is not None:
                raise ValueError("SATISFIED requires one policy and no limitation")
        elif self.resolution_status == RelationshipPolicyResolutionStatus.NOT_REQUIRED:
            if self.required or self.policy_id is not None or self.limitation_code is not None:
                raise ValueError("NOT_REQUIRED cannot carry policy or limitation")
        elif self.policy_id is not None or not self.limitation_code:
            raise ValueError("blocked P18 decision requires limitation and no policy")
        return self


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
        raise BusinessRelationshipPolicyError(
            code,
            "value is not deterministic JSON",
        ) from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _id(prefix: str, value: Any) -> str:
    _, fingerprint = _canonical_json(value, code="P18_IDENTITY_NOT_CANONICAL")
    return prefix + fingerprint[:24]


def _clean(value: str, *, code: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise BusinessRelationshipPolicyError(code, "value is empty")
    return cleaned


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise BusinessRelationshipPolicyError(
            "P18_TIMEZONE_REQUIRED",
            "P18 lifecycle timestamps must be timezone-aware",
        )
    return stamp


class BusinessRelationshipPolicyStore:
    """Single P18 owner for policy authority and immutable policy-use lineage."""

    def __init__(
        self,
        *,
        research_store: ResearchSessionStore,
        db_engine=None,
    ) -> None:
        self._research = research_store
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _tenant(principal: Principal) -> str:
        if principal.tenant_id is not None:
            return f"id:{principal.tenant_id}"
        if principal.tenant_slug:
            return f"slug:{principal.tenant_slug}"
        raise BusinessRelationshipPolicyError(
            "P18_TENANT_REQUIRED",
            "P18 requires an explicit tenant binding",
        )

    @staticmethod
    def _subject(principal: Principal) -> str:
        return _clean(
            str(principal.user_id),
            code="P18_PRINCIPAL_REQUIRED",
        )

    def _session(self, session_id: str, principal: Principal):
        try:
            return self._research.load(
                session_id,
                tenant=self._tenant(principal),
                principal=self._subject(principal),
            )
        except ResearchPersistenceError as exc:
            raise BusinessRelationshipPolicyError(
                "P18_RESEARCH_SESSION_SCOPE_INVALID",
                exc.code,
            ) from exc

    @staticmethod
    def _hydrate_policy(
        row: BusinessRelationshipPolicyRecord,
    ) -> BusinessRelationshipPolicy:
        try:
            scope = json.loads(row.applicability_scope_json)
        except json.JSONDecodeError as exc:
            raise BusinessRelationshipPolicyError(
                "P18_POLICY_PERSISTENCE_INVALID",
                row.policy_id,
            ) from exc
        if not isinstance(scope, dict):
            raise BusinessRelationshipPolicyError(
                "P18_POLICY_PERSISTENCE_INVALID",
                row.policy_id,
            )
        _, observed_scope = _canonical_json(
            scope,
            code="P18_POLICY_SCOPE_NOT_CANONICAL",
        )
        if observed_scope != row.applicability_scope_fingerprint:
            raise BusinessRelationshipPolicyError(
                "P18_POLICY_SCOPE_FINGERPRINT_MISMATCH",
                row.policy_id,
            )
        return BusinessRelationshipPolicy(
            policy_id=row.policy_id,
            tenant_binding=row.tenant_binding,
            semantic_context_version=row.semantic_context_version,
            policy_key=row.policy_key,
            source_business_ref=row.source_business_ref,
            target_business_ref=row.target_business_ref,
            business_relationship_statement=row.business_relationship_statement,
            applicability_scope=scope,
            applicability_scope_fingerprint=row.applicability_scope_fingerprint,
            policy_fingerprint=row.policy_fingerprint,
            provenance_ref=row.provenance_ref,
            approved_by_subject=row.approved_by_subject,
            status=BusinessRelationshipPolicyStatus(row.status),
            created_at=row.created_at,
            retired_at=row.retired_at,
        )

    @staticmethod
    def _hydrate_use(
        row: BusinessRelationshipPolicyUseRecord,
    ) -> BusinessRelationshipPolicyUse:
        return BusinessRelationshipPolicyUse(
            policy_use_id=row.policy_use_id,
            research_session_id=row.research_session_id,
            obligation_id=row.obligation_id,
            claim_id=row.claim_id,
            reasoning_step_id=row.reasoning_step_id,
            requirement_fingerprint=row.requirement_fingerprint,
            policy_id=row.policy_id,
            policy_fingerprint=row.policy_fingerprint,
            resolution_status=RelationshipPolicyResolutionStatus(
                row.resolution_status
            ),
            limitation_code=row.limitation_code,
            created_at=row.created_at,
        )

    def create_policy(
        self,
        *,
        principal: Principal,
        semantic_context_version: str,
        policy_key: str,
        source_business_ref: str,
        target_business_ref: str,
        business_relationship_statement: str,
        applicability_scope: dict[str, Any],
        provenance_ref: str,
        now: datetime | None = None,
    ) -> BusinessRelationshipPolicy:
        tenant = self._tenant(principal)
        subject = self._subject(principal)
        context = _clean(
            semantic_context_version,
            code="P18_POLICY_CONTEXT_REQUIRED",
        )
        key = _clean(policy_key, code="P18_POLICY_KEY_REQUIRED")
        source_ref = _clean(
            source_business_ref,
            code="P18_POLICY_SOURCE_REF_REQUIRED",
        )
        target_ref = _clean(
            target_business_ref,
            code="P18_POLICY_TARGET_REF_REQUIRED",
        )
        statement = _clean(
            business_relationship_statement,
            code="P18_POLICY_STATEMENT_REQUIRED",
        )
        provenance = _clean(
            provenance_ref,
            code="P18_POLICY_PROVENANCE_REQUIRED",
        )
        if not applicability_scope:
            raise BusinessRelationshipPolicyError(
                "P18_POLICY_SCOPE_REQUIRED",
                "policy requires an explicit exact applicability scope",
            )
        scope_json, scope_fingerprint = _canonical_json(
            applicability_scope,
            code="P18_POLICY_SCOPE_NOT_CANONICAL",
        )
        meaning = {
            "tenant_binding": tenant,
            "semantic_context_version": context,
            "policy_key": key,
            "source_business_ref": source_ref,
            "target_business_ref": target_ref,
            "business_relationship_statement": statement,
            "applicability_scope": json.loads(scope_json),
            "provenance_ref": provenance,
        }
        _, policy_fingerprint = _canonical_json(
            meaning,
            code="P18_POLICY_NOT_CANONICAL",
        )
        policy_id = "brp_" + policy_fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(BusinessRelationshipPolicyRecord, policy_id)
            if existing is not None:
                if existing.policy_fingerprint != policy_fingerprint:
                    raise BusinessRelationshipPolicyError(
                        "P18_POLICY_IDENTITY_CONFLICT",
                        policy_id,
                    )
                return self._hydrate_policy(existing)

            active = db.exec(
                select(BusinessRelationshipPolicyRecord)
                .where(
                    BusinessRelationshipPolicyRecord.tenant_binding == tenant
                )
                .where(
                    BusinessRelationshipPolicyRecord.semantic_context_version
                    == context
                )
                .where(BusinessRelationshipPolicyRecord.policy_key == key)
                .where(
                    BusinessRelationshipPolicyRecord.source_business_ref
                    == source_ref
                )
                .where(
                    BusinessRelationshipPolicyRecord.target_business_ref
                    == target_ref
                )
                .where(
                    BusinessRelationshipPolicyRecord.applicability_scope_fingerprint
                    == scope_fingerprint
                )
                .where(
                    BusinessRelationshipPolicyRecord.status
                    == BusinessRelationshipPolicyStatus.ACTIVE.value
                )
            ).all()
            if active:
                if (
                    len(active) == 1
                    and active[0].policy_fingerprint == policy_fingerprint
                ):
                    return self._hydrate_policy(active[0])
                raise BusinessRelationshipPolicyError(
                    "P18_ACTIVE_POLICY_CONFLICT",
                    (
                        "retire the current exact policy before introducing "
                        "changed governed meaning"
                    ),
                )

            row = BusinessRelationshipPolicyRecord(
                policy_id=policy_id,
                tenant_binding=tenant,
                semantic_context_version=context,
                policy_key=key,
                source_business_ref=source_ref,
                target_business_ref=target_ref,
                business_relationship_statement=statement,
                applicability_scope_json=scope_json,
                applicability_scope_fingerprint=scope_fingerprint,
                policy_fingerprint=policy_fingerprint,
                provenance_ref=provenance,
                approved_by_subject=subject,
                status=BusinessRelationshipPolicyStatus.ACTIVE.value,
                created_at=_aware(now),
                retired_at=None,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_policy(row)

    def load_policy(
        self,
        *,
        policy_id: str,
        principal: Principal,
    ) -> BusinessRelationshipPolicy:
        tenant = self._tenant(principal)
        with Session(self._engine) as db:
            row = db.get(BusinessRelationshipPolicyRecord, policy_id)
            if row is None:
                raise BusinessRelationshipPolicyError(
                    "P18_POLICY_NOT_FOUND",
                    policy_id,
                )
            if row.tenant_binding != tenant:
                raise BusinessRelationshipPolicyError(
                    "P18_POLICY_TENANT_MISMATCH",
                    policy_id,
                )
            return self._hydrate_policy(row)

    def retire_policy(
        self,
        *,
        policy_id: str,
        principal: Principal,
        now: datetime | None = None,
    ) -> BusinessRelationshipPolicy:
        tenant = self._tenant(principal)
        with Session(self._engine) as db:
            row = db.get(BusinessRelationshipPolicyRecord, policy_id)
            if row is None:
                raise BusinessRelationshipPolicyError(
                    "P18_POLICY_NOT_FOUND",
                    policy_id,
                )
            if row.tenant_binding != tenant:
                raise BusinessRelationshipPolicyError(
                    "P18_POLICY_TENANT_MISMATCH",
                    policy_id,
                )
            if row.status == BusinessRelationshipPolicyStatus.RETIRED.value:
                return self._hydrate_policy(row)
            if row.status != BusinessRelationshipPolicyStatus.ACTIVE.value:
                raise BusinessRelationshipPolicyError(
                    "P18_POLICY_LIFECYCLE_INVALID",
                    row.status,
                )
            row.status = BusinessRelationshipPolicyStatus.RETIRED.value
            row.retired_at = _aware(now)
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_policy(row)

    def _validate_requirement_authority(
        self,
        requirement: RelationshipPolicyRequirement,
        principal: Principal,
    ):
        session = self._session(
            requirement.research_session_id,
            principal,
        )
        if requirement.semantic_context_version != session.context_version:
            raise BusinessRelationshipPolicyError(
                "P18_REQUIREMENT_CONTEXT_MISMATCH",
                "typed requirement does not match sealed Research context",
            )
        try:
            ResearchManager.obligation(session, requirement.obligation_id)
        except ResearchStateError as exc:
            raise BusinessRelationshipPolicyError(
                "P18_REQUIREMENT_OBLIGATION_INVALID",
                requirement.obligation_id,
            ) from exc

        with Session(self._engine) as db:
            claim = db.get(ResearchClaimRecord, requirement.claim_id)
            step = db.get(
                ResearchReasoningStepRecord,
                requirement.reasoning_step_id,
            )
        if claim is None:
            raise BusinessRelationshipPolicyError(
                "P18_CLAIM_NOT_FOUND",
                requirement.claim_id,
            )
        if step is None:
            raise BusinessRelationshipPolicyError(
                "P18_REASONING_STEP_NOT_FOUND",
                requirement.reasoning_step_id,
            )
        if claim.session_id != session.session_id:
            raise BusinessRelationshipPolicyError(
                "P18_CLAIM_SESSION_MISMATCH",
                requirement.claim_id,
            )
        if step.session_id != session.session_id:
            raise BusinessRelationshipPolicyError(
                "P18_REASONING_SESSION_MISMATCH",
                requirement.reasoning_step_id,
            )
        if claim.obligation_id != requirement.obligation_id:
            raise BusinessRelationshipPolicyError(
                "P18_CLAIM_OBLIGATION_MISMATCH",
                requirement.claim_id,
            )
        if step.parent_obligation_id != requirement.obligation_id:
            raise BusinessRelationshipPolicyError(
                "P18_REASONING_OBLIGATION_MISMATCH",
                requirement.reasoning_step_id,
            )
        if (
            claim.tenant_binding != session.tenant_binding
            or claim.principal_subject != session.principal_subject
            or claim.semantic_context_version != session.context_version
        ):
            raise BusinessRelationshipPolicyError(
                "P18_CLAIM_AUTHORITY_MISMATCH",
                requirement.claim_id,
            )
        return session

    @staticmethod
    def _requirement_fingerprint(
        requirement: RelationshipPolicyRequirement,
        *,
        research_authority_id: str,
    ) -> str:
        _, fingerprint = _canonical_json(
            {
                "research_authority_id": research_authority_id,
                "research_session_id": requirement.research_session_id,
                "obligation_id": requirement.obligation_id,
                "claim_id": requirement.claim_id,
                "reasoning_step_id": requirement.reasoning_step_id,
                "policy_key": requirement.policy_key,
                "source_business_ref": requirement.source_business_ref,
                "target_business_ref": requirement.target_business_ref,
                "semantic_context_version": requirement.semantic_context_version,
                "applicability_scope": requirement.applicability_scope,
                "required": requirement.required,
            },
            code="P18_REQUIREMENT_NOT_CANONICAL",
        )
        return fingerprint

    def _persist_use(
        self,
        *,
        requirement: RelationshipPolicyRequirement,
        requirement_fingerprint: str,
        resolution_status: RelationshipPolicyResolutionStatus,
        policy: BusinessRelationshipPolicy | None,
        limitation_code: str | None,
        now: datetime | None,
    ) -> BusinessRelationshipPolicyUse:
        identity = {
            "requirement_fingerprint": requirement_fingerprint,
            "resolution_status": resolution_status.value,
            "policy_id": policy.policy_id if policy else None,
            "policy_fingerprint": (
                policy.policy_fingerprint if policy else None
            ),
            "limitation_code": limitation_code,
        }
        policy_use_id = _id("bru_", identity)
        with Session(self._engine) as db:
            existing = db.get(
                BusinessRelationshipPolicyUseRecord,
                policy_use_id,
            )
            if existing is not None:
                expected = (
                    requirement.research_session_id,
                    requirement.obligation_id,
                    requirement.claim_id,
                    requirement.reasoning_step_id,
                    requirement_fingerprint,
                    policy.policy_id if policy else None,
                    policy.policy_fingerprint if policy else None,
                    resolution_status.value,
                    limitation_code,
                )
                observed = (
                    existing.research_session_id,
                    existing.obligation_id,
                    existing.claim_id,
                    existing.reasoning_step_id,
                    existing.requirement_fingerprint,
                    existing.policy_id,
                    existing.policy_fingerprint,
                    existing.resolution_status,
                    existing.limitation_code,
                )
                if observed != expected:
                    raise BusinessRelationshipPolicyError(
                        "P18_POLICY_USE_IDENTITY_CONFLICT",
                        policy_use_id,
                    )
                return self._hydrate_use(existing)

            row = BusinessRelationshipPolicyUseRecord(
                policy_use_id=policy_use_id,
                research_session_id=requirement.research_session_id,
                obligation_id=requirement.obligation_id,
                claim_id=requirement.claim_id,
                reasoning_step_id=requirement.reasoning_step_id,
                requirement_fingerprint=requirement_fingerprint,
                policy_id=policy.policy_id if policy else None,
                policy_fingerprint=(
                    policy.policy_fingerprint if policy else None
                ),
                resolution_status=resolution_status.value,
                limitation_code=limitation_code,
                created_at=_aware(now),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_use(row)

    def _blocked(
        self,
        *,
        requirement: RelationshipPolicyRequirement,
        requirement_fingerprint: str,
        status: RelationshipPolicyResolutionStatus,
        limitation_code: str,
        now: datetime | None,
    ) -> RelationshipPolicyDecision:
        use = self._persist_use(
            requirement=requirement,
            requirement_fingerprint=requirement_fingerprint,
            resolution_status=status,
            policy=None,
            limitation_code=limitation_code,
            now=now,
        )
        return RelationshipPolicyDecision(
            required=True,
            eligible=False,
            resolution_status=status,
            policy_use_id=use.policy_use_id,
            policy_id=None,
            limitation_code=limitation_code,
        )

    def resolve(
        self,
        *,
        requirement: RelationshipPolicyRequirement,
        principal: Principal,
        now: datetime | None = None,
    ) -> RelationshipPolicyDecision:
        session = self._validate_requirement_authority(
            requirement,
            principal,
        )
        requirement_fingerprint = self._requirement_fingerprint(
            requirement,
            research_authority_id=session.authority_id,
        )

        if not requirement.required:
            use = self._persist_use(
                requirement=requirement,
                requirement_fingerprint=requirement_fingerprint,
                resolution_status=RelationshipPolicyResolutionStatus.NOT_REQUIRED,
                policy=None,
                limitation_code=None,
                now=now,
            )
            return RelationshipPolicyDecision(
                required=False,
                eligible=True,
                resolution_status=(
                    RelationshipPolicyResolutionStatus.NOT_REQUIRED
                ),
                policy_use_id=use.policy_use_id,
                policy_id=None,
                limitation_code=None,
            )

        _, scope_fingerprint = _canonical_json(
            requirement.applicability_scope,
            code="P18_REQUIREMENT_SCOPE_NOT_CANONICAL",
        )
        tenant = session.tenant_binding

        with Session(self._engine) as db:
            keyed = db.exec(
                select(BusinessRelationshipPolicyRecord).where(
                    BusinessRelationshipPolicyRecord.policy_key
                    == requirement.policy_key
                )
            ).all()

        if not keyed:
            return self._blocked(
                requirement=requirement,
                requirement_fingerprint=requirement_fingerprint,
                status=RelationshipPolicyResolutionStatus.BLOCKED_MISSING,
                limitation_code="P18_RELATIONSHIP_POLICY_MISSING",
                now=now,
            )

        ref_matched = tuple(
            row
            for row in keyed
            if row.source_business_ref == requirement.source_business_ref
            and row.target_business_ref == requirement.target_business_ref
        )
        if not ref_matched:
            raise BusinessRelationshipPolicyError(
                "P18_POLICY_BUSINESS_REF_MISMATCH",
                (
                    "policy key exists but does not govern the explicit "
                    "source/target business refs"
                ),
            )

        tenant_matched = tuple(
            row for row in ref_matched if row.tenant_binding == tenant
        )
        if not tenant_matched:
            return self._blocked(
                requirement=requirement,
                requirement_fingerprint=requirement_fingerprint,
                status=RelationshipPolicyResolutionStatus.BLOCKED_TENANT,
                limitation_code="P18_RELATIONSHIP_POLICY_TENANT_MISMATCH",
                now=now,
            )

        context_matched = tuple(
            row
            for row in tenant_matched
            if row.semantic_context_version
            == requirement.semantic_context_version
        )
        if not context_matched:
            return self._blocked(
                requirement=requirement,
                requirement_fingerprint=requirement_fingerprint,
                status=RelationshipPolicyResolutionStatus.BLOCKED_CONTEXT,
                limitation_code="P18_RELATIONSHIP_POLICY_CONTEXT_MISMATCH",
                now=now,
            )

        scope_matched = tuple(
            row
            for row in context_matched
            if row.applicability_scope_fingerprint == scope_fingerprint
        )
        if not scope_matched:
            return self._blocked(
                requirement=requirement,
                requirement_fingerprint=requirement_fingerprint,
                status=RelationshipPolicyResolutionStatus.BLOCKED_SCOPE,
                limitation_code="P18_RELATIONSHIP_POLICY_SCOPE_MISMATCH",
                now=now,
            )

        active = tuple(
            row
            for row in scope_matched
            if row.status == BusinessRelationshipPolicyStatus.ACTIVE.value
        )
        if len(active) > 1:
            raise BusinessRelationshipPolicyError(
                "P18_POLICY_AUTHORITY_AMBIGUOUS",
                "multiple ACTIVE exact policies exist",
            )
        if len(active) == 1:
            policy = self._hydrate_policy(active[0])
            use = self._persist_use(
                requirement=requirement,
                requirement_fingerprint=requirement_fingerprint,
                resolution_status=RelationshipPolicyResolutionStatus.SATISFIED,
                policy=policy,
                limitation_code=None,
                now=now,
            )
            return RelationshipPolicyDecision(
                required=True,
                eligible=True,
                resolution_status=RelationshipPolicyResolutionStatus.SATISFIED,
                policy_use_id=use.policy_use_id,
                policy_id=policy.policy_id,
                limitation_code=None,
            )

        retired = tuple(
            row
            for row in scope_matched
            if row.status == BusinessRelationshipPolicyStatus.RETIRED.value
        )
        if retired:
            return self._blocked(
                requirement=requirement,
                requirement_fingerprint=requirement_fingerprint,
                status=RelationshipPolicyResolutionStatus.BLOCKED_RETIRED,
                limitation_code="P18_RELATIONSHIP_POLICY_RETIRED",
                now=now,
            )

        raise BusinessRelationshipPolicyError(
            "P18_POLICY_LIFECYCLE_INVALID",
            "exact policy has an unsupported lifecycle state",
        )

    def load_use(
        self,
        *,
        session_id: str,
        policy_use_id: str,
        principal: Principal,
    ) -> BusinessRelationshipPolicyUse:
        session = self._session(session_id, principal)
        with Session(self._engine) as db:
            row = db.get(
                BusinessRelationshipPolicyUseRecord,
                policy_use_id,
            )
            if row is None or row.research_session_id != session.session_id:
                raise BusinessRelationshipPolicyError(
                    "P18_POLICY_USE_NOT_FOUND",
                    policy_use_id,
                )
            return self._hydrate_use(row)
