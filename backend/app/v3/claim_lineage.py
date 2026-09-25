"""P16 durable claim/Evidence lineage.

P16 never re-runs analytics and never upgrades native exploration into truth. It binds
explicit claims to already-governed P14 Evidence and keeps P15 material as origin only.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.research import ObligationState, ResearchManager
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import (
    ClaimEvidenceLinkRecord,
    ResearchClaimRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ClaimLineageError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ClaimEvidenceRelation(StrEnum):
    SUPPORTS = "SUPPORTS"
    CHALLENGES = "CHALLENGES"
    CONTEXTUALIZES = "CONTEXTUALIZES"
    INSUFFICIENT = "INSUFFICIENT"


class ClaimEpistemicState(StrEnum):
    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    CHALLENGED = "CHALLENGED"
    CONTESTED = "CONTESTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ClaimFreshness(Frozen):
    as_of: datetime
    stale_after: datetime | None = None

    @model_validator(mode="after")
    def aware_and_ordered(self):
        for value in (self.as_of, self.stale_after):
            if value is not None and (
                value.tzinfo is None or value.utcoffset() is None
            ):
                raise ValueError("claim freshness timestamps must be timezone-aware")
        if self.stale_after is not None and self.stale_after <= self.as_of:
            raise ValueError("stale_after must be later than as_of")
        return self


class ClaimEvidenceLink(Frozen):
    link_id: str = Field(pattern=r"^cel_[a-f0-9]{24}$")
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")
    execution_link_id: str = Field(min_length=1)
    relation: ClaimEvidenceRelation
    created_at: datetime


class ResearchClaim(Frozen):
    claim_id: str = Field(pattern=r"^clm_[a-f0-9]{24}$")
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    tenant_binding: str = Field(min_length=1)
    principal_subject: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    proposition: dict[str, Any]
    scope: dict[str, Any]
    freshness: ClaimFreshness
    origin_material_refs: tuple[str, ...] = ()
    epistemic_state: ClaimEpistemicState
    limitations: tuple[str, ...] = ()
    claim_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    evidence_links: tuple[ClaimEvidenceLink, ...] = ()
    created_at: datetime
    updated_at: datetime


def _json(value: Any, *, code: str) -> tuple[str, str]:
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
        raise ClaimLineageError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_json(raw: str, *, code: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ClaimLineageError(code, "persisted claim lineage JSON is invalid") from exc


def _id(prefix: str, value: Any) -> str:
    _, fingerprint = _json(value, code="P16_IDENTITY_NOT_CANONICAL")
    return prefix + fingerprint[:24]


class ClaimLineageStore:
    """Single P16 owner for claim state and eligible Evidence edges."""

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
        raise ClaimLineageError(
            "P16_TENANT_REQUIRED",
            "claim lineage requires an explicit tenant binding",
        )

    def _session(self, session_id: str, principal: Principal):
        return self._research.load(
            session_id,
            tenant=self._tenant(principal),
            principal=str(principal.user_id),
        )

    @staticmethod
    def _claim_static_payload(
        *,
        session,
        obligation_id: str,
        claim_text: str,
        proposition: dict[str, Any],
        scope: dict[str, Any],
        freshness: ClaimFreshness,
        origin_material_refs: tuple[str, ...],
        limitations: tuple[str, ...],
    ) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "obligation_id": obligation_id,
            "tenant_binding": session.tenant_binding,
            "principal_subject": session.principal_subject,
            "semantic_context_version": session.context_version,
            "claim_text": claim_text,
            "proposition": proposition,
            "scope": scope,
            "freshness": freshness.model_dump(mode="json"),
            "origin_material_refs": list(origin_material_refs),
            "limitations": list(limitations),
        }

    def _validate_origins(
        self,
        *,
        session_id: str,
        obligation_id: str,
        refs: tuple[str, ...],
    ) -> None:
        if len(refs) != len(set(refs)):
            raise ClaimLineageError(
                "P16_ORIGIN_MATERIAL_DUPLICATE",
                "claim origin material refs contain duplicates",
            )
        if not refs:
            return
        with Session(self._engine) as db:
            rows = db.exec(
                select(ResearchExplorationMaterial).where(
                    ResearchExplorationMaterial.lead_id.in_(refs)
                )
            ).all()
        by_id = {row.lead_id: row for row in rows}
        if set(by_id) != set(refs):
            raise ClaimLineageError(
                "P16_ORIGIN_MATERIAL_UNKNOWN",
                "claim references unknown P15 Research material",
            )
        for ref in refs:
            row = by_id[ref]
            if (
                row.session_id != session_id
                or row.obligation_id != obligation_id
                or row.epistemic_state != "RESEARCH_MATERIAL"
            ):
                raise ClaimLineageError(
                    "P16_ORIGIN_MATERIAL_SCOPE_MISMATCH",
                    "P15 origin material belongs to another Research scope or was promoted",
                )

    def create_claim(
        self,
        *,
        session_id: str,
        obligation_id: str,
        principal: Principal,
        claim_text: str,
        proposition: dict[str, Any],
        scope: dict[str, Any],
        freshness: ClaimFreshness,
        origin_material_refs: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
    ) -> ResearchClaim:
        session = self._session(session_id, principal)
        obligation = ResearchManager.obligation(session, obligation_id)
        if obligation.state != ObligationState.VERIFIED:
            raise ClaimLineageError(
                "P16_VERIFIED_RESEARCH_OBLIGATION_REQUIRED",
                "P16 claims consume a VERIFIED Research obligation",
            )
        text = claim_text.strip()
        if not text:
            raise ClaimLineageError("P16_CLAIM_TEXT_REQUIRED", "claim text is empty")
        if not proposition:
            raise ClaimLineageError(
                "P16_STRUCTURED_PROPOSITION_REQUIRED",
                "claim requires a non-empty structured proposition",
            )
        if not scope:
            raise ClaimLineageError(
                "P16_CLAIM_SCOPE_REQUIRED",
                "claim requires an explicit scope",
            )
        if len(limitations) != len(set(limitations)) or any(
            not item.strip() for item in limitations
        ):
            raise ClaimLineageError(
                "P16_CLAIM_LIMITATIONS_INVALID",
                "claim limitations must be unique non-empty strings",
            )
        self._validate_origins(
            session_id=session_id,
            obligation_id=obligation_id,
            refs=origin_material_refs,
        )
        static = self._claim_static_payload(
            session=session,
            obligation_id=obligation_id,
            claim_text=text,
            proposition=proposition,
            scope=scope,
            freshness=freshness,
            origin_material_refs=origin_material_refs,
            limitations=limitations,
        )
        _, fingerprint = _json(static, code="P16_CLAIM_NOT_CANONICAL")
        claim_id = "clm_" + fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(ResearchClaimRecord, claim_id)
            if existing is not None:
                if existing.claim_fingerprint != fingerprint:
                    raise ClaimLineageError(
                        "P16_CLAIM_IDENTITY_CONFLICT",
                        "existing claim id has different immutable content",
                    )
                return self._hydrate(existing, db)

            now = datetime.now(timezone.utc)
            db.add(
                ResearchClaimRecord(
                    claim_id=claim_id,
                    session_id=session.session_id,
                    obligation_id=obligation_id,
                    tenant_binding=session.tenant_binding,
                    principal_subject=session.principal_subject,
                    semantic_context_version=session.context_version,
                    claim_text=text,
                    proposition_json=_json(
                        proposition, code="P16_PROPOSITION_NOT_CANONICAL"
                    )[0],
                    scope_json=_json(scope, code="P16_SCOPE_NOT_CANONICAL")[0],
                    freshness_json=_json(
                        freshness.model_dump(mode="json"),
                        code="P16_FRESHNESS_NOT_CANONICAL",
                    )[0],
                    origin_material_refs_json=_json(
                        list(origin_material_refs),
                        code="P16_ORIGIN_MATERIAL_NOT_CANONICAL",
                    )[0],
                    epistemic_state=ClaimEpistemicState.PROPOSED.value,
                    limitations_json=_json(
                        list(limitations),
                        code="P16_LIMITATIONS_NOT_CANONICAL",
                    )[0],
                    claim_fingerprint=fingerprint,
                    created_at=now,
                    updated_at=now,
                )
            )
            db.commit()
            record = db.get(ResearchClaimRecord, claim_id)
            assert record is not None
            return self._hydrate(record, db)

    @staticmethod
    def _derive_state(
        links: tuple[ClaimEvidenceLinkRecord, ...],
    ) -> ClaimEpistemicState:
        relations = {ClaimEvidenceRelation(item.relation) for item in links}
        if (
            ClaimEvidenceRelation.SUPPORTS in relations
            and ClaimEvidenceRelation.CHALLENGES in relations
        ):
            return ClaimEpistemicState.CONTESTED
        if ClaimEvidenceRelation.SUPPORTS in relations:
            return ClaimEpistemicState.SUPPORTED
        if ClaimEvidenceRelation.CHALLENGES in relations:
            return ClaimEpistemicState.CHALLENGED
        if ClaimEvidenceRelation.INSUFFICIENT in relations:
            return ClaimEpistemicState.INSUFFICIENT_EVIDENCE
        return ClaimEpistemicState.PROPOSED

    def _hydrate(
        self,
        record: ResearchClaimRecord,
        db: Session,
    ) -> ResearchClaim:
        proposition = _load_json(
            record.proposition_json, code="P16_PROPOSITION_INVALID"
        )
        scope = _load_json(record.scope_json, code="P16_SCOPE_INVALID")
        freshness_raw = _load_json(
            record.freshness_json, code="P16_FRESHNESS_INVALID"
        )
        origins = _load_json(
            record.origin_material_refs_json,
            code="P16_ORIGIN_MATERIAL_INVALID",
        )
        limitations = _load_json(
            record.limitations_json, code="P16_LIMITATIONS_INVALID"
        )
        if (
            not isinstance(proposition, dict)
            or not isinstance(scope, dict)
            or not isinstance(origins, list)
            or not isinstance(limitations, list)
        ):
            raise ClaimLineageError(
                "P16_CLAIM_PERSISTENCE_INVALID",
                "persisted claim fields have invalid shape",
            )
        freshness = ClaimFreshness.model_validate(freshness_raw)
        static = {
            "session_id": record.session_id,
            "obligation_id": record.obligation_id,
            "tenant_binding": record.tenant_binding,
            "principal_subject": record.principal_subject,
            "semantic_context_version": record.semantic_context_version,
            "claim_text": record.claim_text,
            "proposition": proposition,
            "scope": scope,
            "freshness": freshness.model_dump(mode="json"),
            "origin_material_refs": origins,
            "limitations": limitations,
        }
        _, observed = _json(static, code="P16_CLAIM_NOT_CANONICAL")
        if observed != record.claim_fingerprint:
            raise ClaimLineageError(
                "P16_CLAIM_FINGERPRINT_MISMATCH",
                "persisted claim immutable content changed",
            )
        raw_links = tuple(
            db.exec(
                select(ClaimEvidenceLinkRecord)
                .where(ClaimEvidenceLinkRecord.claim_id == record.claim_id)
                .order_by(ClaimEvidenceLinkRecord.created_at, ClaimEvidenceLinkRecord.link_id)
            ).all()
        )
        derived = self._derive_state(raw_links)
        if record.epistemic_state != derived.value:
            raise ClaimLineageError(
                "P16_EPISTEMIC_STATE_DRIFT",
                "persisted claim state differs from its Evidence edges",
            )
        links = tuple(
            ClaimEvidenceLink(
                link_id=item.link_id,
                evidence_id=item.evidence_id,
                receipt_id=item.receipt_id,
                execution_link_id=str(item.execution_link_id),
                relation=ClaimEvidenceRelation(item.relation),
                created_at=item.created_at,
            )
            for item in raw_links
        )
        return ResearchClaim(
            claim_id=record.claim_id,
            research_session_id=record.session_id,
            obligation_id=record.obligation_id,
            tenant_binding=record.tenant_binding,
            principal_subject=record.principal_subject,
            semantic_context_version=record.semantic_context_version,
            claim_text=record.claim_text,
            proposition=proposition,
            scope=scope,
            freshness=freshness,
            origin_material_refs=tuple(origins),
            epistemic_state=derived,
            limitations=tuple(limitations),
            claim_fingerprint=record.claim_fingerprint,
            evidence_links=links,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def load_claim(
        self,
        *,
        session_id: str,
        claim_id: str,
        principal: Principal,
    ) -> ResearchClaim:
        session = self._session(session_id, principal)
        with Session(self._engine) as db:
            record = db.get(ResearchClaimRecord, claim_id)
            if record is None or record.session_id != session.session_id:
                raise ClaimLineageError(
                    "P16_CLAIM_NOT_FOUND",
                    "claim does not exist in the current Research session",
                )
            if (
                record.tenant_binding != session.tenant_binding
                or record.principal_subject != session.principal_subject
                or record.semantic_context_version != session.context_version
            ):
                raise ClaimLineageError(
                    "P16_CLAIM_SCOPE_MISMATCH",
                    "claim belongs to another principal/context lens",
                )
            return self._hydrate(record, db)

    def link_evidence(
        self,
        *,
        session_id: str,
        claim_id: str,
        evidence_id: str,
        relation: ClaimEvidenceRelation,
        principal: Principal,
    ) -> ResearchClaim:
        session = self._session(session_id, principal)
        claim = self.load_claim(
            session_id=session_id,
            claim_id=claim_id,
            principal=principal,
        )
        refs = tuple(x for x in session.evidence_refs if x.evidence_id == evidence_id)
        if len(refs) != 1:
            raise ClaimLineageError(
                "P16_EVIDENCE_NOT_IN_SESSION",
                "Evidence is not uniquely present in the current Research session",
            )
        evidence_ref = refs[0]
        if (
            evidence_ref.obligation_id != claim.obligation_id
            or evidence_ref.authority_id != session.authority_id
        ):
            raise ClaimLineageError(
                "P16_EVIDENCE_SCOPE_MISMATCH",
                "Evidence belongs to another obligation or Research authority",
            )

        with Session(self._engine) as db:
            executions = db.exec(
                select(ResearchExecutionLink)
                .where(ResearchExecutionLink.session_id == session_id)
                .where(ResearchExecutionLink.obligation_id == claim.obligation_id)
                .where(ResearchExecutionLink.evidence_id == evidence_id)
                .where(ResearchExecutionLink.receipt_id == evidence_ref.receipt_id)
                .where(ResearchExecutionLink.status == "VERIFIED")
            ).all()
            if len(executions) != 1:
                raise ClaimLineageError(
                    "P16_EVIDENCE_EXECUTION_PROVENANCE_INVALID",
                    "Evidence does not resolve to exactly one VERIFIED execution/receipt",
                )
            execution = executions[0]
            prior = db.exec(
                select(ClaimEvidenceLinkRecord)
                .where(ClaimEvidenceLinkRecord.claim_id == claim_id)
                .where(ClaimEvidenceLinkRecord.evidence_id == evidence_id)
            ).first()
            if prior is not None:
                if prior.relation != relation.value:
                    raise ClaimLineageError(
                        "P16_EVIDENCE_RELATION_IMMUTABLE",
                        "Evidence is already linked to this claim with another relation",
                    )
                return self._hydrate(
                    db.get(ResearchClaimRecord, claim_id),
                    db,
                )

            link_id = _id(
                "cel_",
                {
                    "claim_id": claim_id,
                    "evidence_id": evidence_id,
                    "receipt_id": evidence_ref.receipt_id,
                    "execution_link_id": str(execution.id),
                    "relation": relation.value,
                },
            )
            db.add(
                ClaimEvidenceLinkRecord(
                    link_id=link_id,
                    claim_id=claim_id,
                    evidence_id=evidence_id,
                    receipt_id=evidence_ref.receipt_id,
                    execution_link_id=execution.id,
                    relation=relation.value,
                    created_at=datetime.now(timezone.utc),
                )
            )
            db.flush()
            all_links = tuple(
                db.exec(
                    select(ClaimEvidenceLinkRecord).where(
                        ClaimEvidenceLinkRecord.claim_id == claim_id
                    )
                ).all()
            )
            state = self._derive_state(all_links)
            record = db.get(ResearchClaimRecord, claim_id)
            assert record is not None
            record.epistemic_state = state.value
            record.updated_at = datetime.now(timezone.utc)
            db.add(record)
            db.commit()
            db.refresh(record)
            return self._hydrate(record, db)
