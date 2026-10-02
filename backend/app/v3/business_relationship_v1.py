"""Dima V1 P18 relationship-result authority.

P18 projects governed P16 claim/Evidence lineage plus the sealed P18 policy-use
decision, then may seal that exact projection as one immutable terminal artifact.
It performs no analytics, join discovery, correlation calculation or causal
identification.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session

from app.v3.business_relationship_policy import (
    RelationshipPolicyDecision,
    RelationshipPolicyResolutionStatus,
)
from app.v3.claim_lineage import ClaimEpistemicState
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import P18RelationshipResultRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RelationshipAnalyticalKind(StrEnum):
    ASSOCIATION = "ASSOCIATION"
    CO_MOVEMENT = "CO_MOVEMENT"


class RelationshipTerminalDisposition(StrEnum):
    FULFILLED = "FULFILLED"
    LIMITED = "LIMITED"


class RelationshipLayerState(StrEnum):
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    SUPPORTED = "SUPPORTED"
    CHALLENGED = "CHALLENGED"
    CONTESTED = "CONTESTED"
    INSUFFICIENT = "INSUFFICIENT"
    SATISFIED = "SATISFIED"
    BLOCKED = "BLOCKED"


class RelationshipResultProjection(Frozen):
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    claim_id: str = Field(pattern=r"^clm_[a-f0-9]{24}$")
    policy_use_id: str = Field(pattern=r"^bru_[a-f0-9]{24}$")
    policy_id: str | None = Field(default=None, pattern=r"^brp_[a-f0-9]{24}$")
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    applicability_scope: dict[str, Any]
    analytical_kind: RelationshipAnalyticalKind | None = None
    association_state: RelationshipLayerState
    co_movement_state: RelationshipLayerState
    business_relationship_state: RelationshipLayerState
    policy_required: bool = True
    contribution_state: RelationshipLayerState = RelationshipLayerState.NOT_ESTABLISHED
    causality_state: RelationshipLayerState = RelationshipLayerState.NOT_ESTABLISHED
    supporting_evidence_refs: tuple[str, ...] = ()
    challenging_evidence_refs: tuple[str, ...] = ()
    contextual_evidence_refs: tuple[str, ...] = ()
    insufficient_evidence_refs: tuple[str, ...] = ()
    limitation_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def p9_cannot_promote_causality_or_contribution(self):
        if self.contribution_state != RelationshipLayerState.NOT_ESTABLISHED:
            raise ValueError("P9 contribution requires governed P19 authority")
        if self.causality_state != RelationshipLayerState.NOT_ESTABLISHED:
            raise ValueError("P9 causality requires governed P19 authority")
        if not self.applicability_scope:
            raise ValueError("P9 relationship projection requires exact scope")
        return self


class SealedRelationshipResult(Frozen):
    result_id: str = Field(pattern=r"^p18r_[a-f0-9]{24}$")
    tenant_binding: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    disposition: RelationshipTerminalDisposition
    projection: RelationshipResultProjection
    result_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


class RelationshipResultStoreError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _claim_layer_state(claim) -> RelationshipLayerState:
    state = _value(claim.epistemic_state)
    mapping = {
        ClaimEpistemicState.PROPOSED.value: RelationshipLayerState.NOT_ESTABLISHED,
        ClaimEpistemicState.SUPPORTED.value: RelationshipLayerState.SUPPORTED,
        ClaimEpistemicState.CHALLENGED.value: RelationshipLayerState.CHALLENGED,
        ClaimEpistemicState.CONTESTED.value: RelationshipLayerState.CONTESTED,
        ClaimEpistemicState.INSUFFICIENT_EVIDENCE.value: RelationshipLayerState.INSUFFICIENT,
    }
    try:
        return mapping[state]
    except KeyError as exc:
        raise ValueError(f"P9_UNKNOWN_CLAIM_EPISTEMIC_STATE:{state}") from exc


def _analytical_kind(claim) -> RelationshipAnalyticalKind | None:
    raw = (getattr(claim, "proposition", {}) or {}).get("relationship_kind")
    if raw is None:
        return None
    try:
        return RelationshipAnalyticalKind(str(raw))
    except ValueError as exc:
        raise ValueError(
            "P9_RELATIONSHIP_KIND_REQUIRES_OTHER_GOVERNED_AUTHORITY"
        ) from exc


def project_relationship_result(
    *,
    research_session_id: str,
    claim,
    decision: RelationshipPolicyDecision,
    scope_lineage_id: str,
    scope_version_id: str,
    applicability_scope: dict[str, Any],
) -> RelationshipResultProjection:
    """Project existing authority; never infer a stronger relationship."""

    links = tuple(getattr(claim, "evidence_links", ()) or ())
    by_relation: dict[str, list[str]] = {
        "SUPPORTS": [],
        "CHALLENGES": [],
        "CONTEXTUALIZES": [],
        "INSUFFICIENT": [],
    }
    for link in links:
        relation = _value(link.relation)
        if relation not in by_relation:
            raise ValueError(f"P9_UNKNOWN_EVIDENCE_RELATION:{relation}")
        by_relation[relation].append(link.evidence_id)

    claim_state = _claim_layer_state(claim)
    kind = _analytical_kind(claim)
    co_movement = (
        claim_state
        if kind == RelationshipAnalyticalKind.CO_MOVEMENT
        else RelationshipLayerState.NOT_ESTABLISHED
    )
    if decision.resolution_status == RelationshipPolicyResolutionStatus.SATISFIED:
        business_state = RelationshipLayerState.SATISFIED
    elif (
        not bool(getattr(decision, "required", True))
        and decision.resolution_status
        == RelationshipPolicyResolutionStatus.NOT_REQUIRED
    ):
        business_state = RelationshipLayerState.NOT_ESTABLISHED
    else:
        business_state = RelationshipLayerState.BLOCKED
    limitations = list(getattr(claim, "limitations", ()) or ())
    if decision.limitation_code:
        limitations.append(decision.limitation_code)

    return RelationshipResultProjection(
        research_session_id=research_session_id,
        obligation_id=claim.obligation_id,
        claim_id=claim.claim_id,
        policy_use_id=decision.policy_use_id,
        policy_id=decision.policy_id,
        scope_lineage_id=scope_lineage_id,
        scope_version_id=scope_version_id,
        applicability_scope=applicability_scope,
        analytical_kind=kind,
        association_state=claim_state,
        co_movement_state=co_movement,
        business_relationship_state=business_state,
        policy_required=bool(getattr(decision, "required", True)),
        supporting_evidence_refs=tuple(dict.fromkeys(by_relation["SUPPORTS"])),
        challenging_evidence_refs=tuple(dict.fromkeys(by_relation["CHALLENGES"])),
        contextual_evidence_refs=tuple(dict.fromkeys(by_relation["CONTEXTUALIZES"])),
        insufficient_evidence_refs=tuple(dict.fromkeys(by_relation["INSUFFICIENT"])),
        limitation_codes=tuple(dict.fromkeys(limitations)),
    )


def relationship_terminal_disposition(
    projection: RelationshipResultProjection,
) -> RelationshipTerminalDisposition:
    """Classify only the already-governed P18 result; never reopen analytics."""

    if not projection.policy_required:
        return (
            RelationshipTerminalDisposition.FULFILLED
            if projection.association_state
            in {
                RelationshipLayerState.SUPPORTED,
                RelationshipLayerState.CHALLENGED,
                RelationshipLayerState.CONTESTED,
            }
            else RelationshipTerminalDisposition.LIMITED
        )
    if (
        projection.business_relationship_state == RelationshipLayerState.SATISFIED
        and not projection.limitation_codes
    ):
        return RelationshipTerminalDisposition.FULFILLED
    return RelationshipTerminalDisposition.LIMITED


def _canonical_projection(
    projection: RelationshipResultProjection,
) -> tuple[str, str]:
    body = json.dumps(
        projection.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return body, hashlib.sha256(body.encode("utf-8")).hexdigest()


class RelationshipResultStore:
    """Immutable P18 terminal-artifact store.

    The stored body is the exact typed P18 projection. Loading it never reads
    P16 claims or P18 policy internals, so downstream owners cannot re-adjudicate
    relationship meaning.
    """

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
        raise RelationshipResultStoreError(
            "P18_RESULT_TENANT_REQUIRED",
            "P18 result requires an explicit tenant binding",
        )

    @staticmethod
    def _subject(principal: Principal) -> str:
        value = str(principal.user_id or "").strip()
        if not value:
            raise RelationshipResultStoreError(
                "P18_RESULT_PRINCIPAL_REQUIRED",
                "P18 result requires a stable principal subject",
            )
        return value

    def _session(self, session_id: str, principal: Principal):
        try:
            return self._research.load(
                session_id,
                tenant=self._tenant(principal),
                principal=self._subject(principal),
            )
        except ResearchPersistenceError as exc:
            raise RelationshipResultStoreError(
                "P18_RESULT_RESEARCH_SCOPE_INVALID",
                exc.code,
            ) from exc

    @staticmethod
    def _hydrate(row: P18RelationshipResultRecord) -> SealedRelationshipResult:
        try:
            body = json.loads(row.projection_json)
        except json.JSONDecodeError as exc:
            raise RelationshipResultStoreError(
                "P18_RESULT_PERSISTENCE_INVALID",
                row.result_id,
            ) from exc
        projection = RelationshipResultProjection.model_validate(body)
        canonical, observed = _canonical_projection(projection)
        if canonical != row.projection_json or observed != row.result_fingerprint:
            raise RelationshipResultStoreError(
                "P18_RESULT_FINGERPRINT_MISMATCH",
                row.result_id,
            )
        return SealedRelationshipResult(
            result_id=row.result_id,
            tenant_binding=row.tenant_binding,
            semantic_context_version=row.semantic_context_version,
            disposition=RelationshipTerminalDisposition(row.disposition),
            projection=projection,
            result_fingerprint=row.result_fingerprint,
            created_at=row.created_at,
        )

    def seal(
        self,
        *,
        projection: RelationshipResultProjection,
        principal: Principal,
        now: datetime | None = None,
    ) -> SealedRelationshipResult:
        session = self._session(projection.research_session_id, principal)
        brief = session.accepted_brief
        if brief is None:
            raise RelationshipResultStoreError(
                "P18_RESULT_ACCEPTED_BRIEF_REQUIRED",
                projection.research_session_id,
            )
        if (
            session.lineage_id != projection.scope_lineage_id
            or brief.scope.scope_version.version_id != projection.scope_version_id
            or session.context_version == ""
        ):
            raise RelationshipResultStoreError(
                "P18_RESULT_SCOPE_AUTHORITY_MISMATCH",
                projection.obligation_id,
            )
        if projection.obligation_id not in {
            item.goal_id for item in brief.questions
        }:
            raise RelationshipResultStoreError(
                "P18_RESULT_REQUIREMENT_UNKNOWN",
                projection.obligation_id,
            )
        tenant = self._tenant(principal)
        if session.tenant_binding != tenant:
            raise RelationshipResultStoreError(
                "P18_RESULT_TENANT_MISMATCH",
                projection.research_session_id,
            )
        projection_json, projection_fingerprint = _canonical_projection(
            projection
        )
        meaning = json.dumps(
            {
                "tenant_binding": tenant,
                "semantic_context_version": session.context_version,
                "projection_fingerprint": projection_fingerprint,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(meaning.encode("utf-8")).hexdigest()
        result_id = "p18r_" + fingerprint[:24]
        disposition = relationship_terminal_disposition(projection)
        stamp = now or datetime.now(timezone.utc)
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise RelationshipResultStoreError(
                "P18_RESULT_TIMEZONE_REQUIRED",
                result_id,
            )
        with Session(self._engine) as db:
            existing = db.get(P18RelationshipResultRecord, result_id)
            if existing is not None:
                if existing.result_fingerprint != fingerprint:
                    raise RelationshipResultStoreError(
                        "P18_RESULT_IDENTITY_CONFLICT",
                        result_id,
                    )
                return self._hydrate(existing)
            row = P18RelationshipResultRecord(
                result_id=result_id,
                research_session_id=projection.research_session_id,
                obligation_id=projection.obligation_id,
                tenant_binding=tenant,
                semantic_context_version=session.context_version,
                scope_lineage_id=projection.scope_lineage_id,
                scope_version_id=projection.scope_version_id,
                disposition=disposition.value,
                projection_json=projection_json,
                result_fingerprint=fingerprint,
                created_at=stamp,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(
        self,
        *,
        result_id: str,
        principal: Principal,
    ) -> SealedRelationshipResult:
        tenant = self._tenant(principal)
        with Session(self._engine) as db:
            row = db.get(P18RelationshipResultRecord, result_id)
            if row is None:
                raise RelationshipResultStoreError(
                    "P18_RESULT_NOT_FOUND",
                    result_id,
                )
            if row.tenant_binding != tenant:
                raise RelationshipResultStoreError(
                    "P18_RESULT_TENANT_MISMATCH",
                    result_id,
                )
            artifact = self._hydrate(row)
        session = self._session(
            artifact.projection.research_session_id,
            principal,
        )
        if (
            session.context_version != artifact.semantic_context_version
            or session.tenant_binding != artifact.tenant_binding
        ):
            raise RelationshipResultStoreError(
                "P18_RESULT_CONTEXT_MISMATCH",
                result_id,
            )
        return artifact
