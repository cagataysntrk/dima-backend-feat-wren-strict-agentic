"""P19 minimal hypothesis/root-cause epistemic authority.

P19 references sealed P14-P18 truth and governs what those sources justify
epistemically. It never executes analytics, creates Evidence/receipts/claims,
or turns investigation/policy structure into causal structure.
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
    BusinessRelationshipPolicyUseRecord,
    HypothesisGroundingLink as HypothesisGroundingLinkRecord,
    HypothesisRecord,
    ResearchClaimRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
    ResearchReasoningStepRecord,
    RootCauseAssessment as RootCauseAssessmentRecord,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class P19EpistemicError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class GroundingSourceKind(StrEnum):
    P14_EVIDENCE = "P14_EVIDENCE"
    P15_MATERIAL = "P15_MATERIAL"
    P16_CLAIM = "P16_CLAIM"
    P17_REASONING_STEP = "P17_REASONING_STEP"
    P18_POLICY_USE = "P18_POLICY_USE"


class GroundingRelation(StrEnum):
    SUPPORTS = "SUPPORTS"
    CHALLENGES = "CHALLENGES"
    CONTEXT = "CONTEXT"
    INSUFFICIENT = "INSUFFICIENT"


class HypothesisDisposition(StrEnum):
    OPEN = "OPEN"
    RETAINED = "RETAINED"
    WEAKENED = "WEAKENED"
    REJECTED = "REJECTED"


class HypothesisEpistemicClass(StrEnum):
    ASSOCIATION = "ASSOCIATION"
    CONTRIBUTION = "CONTRIBUTION"
    CANDIDATE_CAUSE = "CANDIDATE_CAUSE"
    COMPETING_HYPOTHESIS = "COMPETING_HYPOTHESIS"


class ContributionClass(StrEnum):
    DOMINANT = "DOMINANT"
    MATERIAL = "MATERIAL"
    SECONDARY = "SECONDARY"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class EvidenceStrength(StrEnum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"
    CONTRADICTED = "CONTRADICTED"


class CausalQualification(StrEnum):
    NOT_CLAIMED = "NOT_CLAIMED"
    CAUSAL_CANDIDATE = "CAUSAL_CANDIDATE"
    IDENTIFICATION_LIMITED = "IDENTIFICATION_LIMITED"
    DEFENSIBLE_CAUSAL_CONCLUSION = "DEFENSIBLE_CAUSAL_CONCLUSION"


class IdentificationLimitation(StrEnum):
    ASSOCIATION_ONLY = "ASSOCIATION_ONLY"
    TEMPORAL_ORDER_UNESTABLISHED = "TEMPORAL_ORDER_UNESTABLISHED"
    CONFOUNDING_NOT_RESOLVED = "CONFOUNDING_NOT_RESOLVED"
    MEDIATION_NOT_IDENTIFIED = "MEDIATION_NOT_IDENTIFIED"
    DATA_QUALITY_LIMITED = "DATA_QUALITY_LIMITED"
    SCOPE_INCONSISTENT = "SCOPE_INCONSISTENT"
    NUMERIC_PROVENANCE_MISSING = "NUMERIC_PROVENANCE_MISSING"
    P18_POLICY_BLOCKED = "P18_POLICY_BLOCKED"
    FATAL_CONTRADICTION = "FATAL_CONTRADICTION"


class AggregateOutcome(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    ROOT_CAUSE_ESTABLISHED = "ROOT_CAUSE_ESTABLISHED"
    MULTIPLE_MATERIAL_CONTRIBUTORS = "MULTIPLE_MATERIAL_CONTRIBUTORS"
    NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED = (
        "NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED"
    )


class NumericAnalyticalKind(StrEnum):
    NATIVE_NUMERIC_RESULT = "NATIVE_NUMERIC_RESULT"
    DIRECT_INDIRECT_DECOMPOSITION = "DIRECT_INDIRECT_DECOMPOSITION"


class CausalIdentificationKind(StrEnum):
    NATIVE_CAUSAL_IDENTIFICATION = "NATIVE_CAUSAL_IDENTIFICATION"
    EXPERIMENTAL = "EXPERIMENTAL"
    QUASI_EXPERIMENTAL = "QUASI_EXPERIMENTAL"


class P19Hypothesis(Frozen):
    hypothesis_id: str = Field(pattern=r"^p19h_[a-f0-9]{24}$")
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    tenant_binding: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    identity_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


class P19GroundingLink(Frozen):
    grounding_link_id: str = Field(pattern=r"^p19g_[a-f0-9]{24}$")
    hypothesis_id: str = Field(pattern=r"^p19h_[a-f0-9]{24}$")
    source_kind: GroundingSourceKind
    source_ref: str = Field(min_length=1)
    source_receipt_id: str | None = None
    relation: GroundingRelation
    link_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


class NumericProvenanceRef(Frozen):
    source_kind: GroundingSourceKind
    source_ref: str = Field(min_length=1)
    source_receipt_id: str | None = None
    source_path: str = Field(min_length=1, max_length=512)
    analytical_kind: NumericAnalyticalKind
    analytical_kind_path: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def native_numeric_only(self):
        if self.source_kind not in {
            GroundingSourceKind.P14_EVIDENCE,
            GroundingSourceKind.P15_MATERIAL,
        }:
            raise ValueError(
                "numeric provenance must reference P14 Evidence or P15 native material"
            )
        if (
            self.analytical_kind
            == NumericAnalyticalKind.DIRECT_INDIRECT_DECOMPOSITION
            and not self.analytical_kind_path
        ):
            raise ValueError(
                "direct/indirect decomposition requires exact source kind marker"
            )
        return self


class CausalIdentificationRef(Frozen):
    source_kind: GroundingSourceKind
    source_ref: str = Field(min_length=1)
    source_receipt_id: str | None = None
    source_path: str = Field(min_length=1, max_length=512)
    identification_kind: CausalIdentificationKind

    @model_validator(mode="after")
    def sealed_source_only(self):
        if self.source_kind not in {
            GroundingSourceKind.P14_EVIDENCE,
            GroundingSourceKind.P15_MATERIAL,
        }:
            raise ValueError(
                "causal identification must reference P14 Evidence or P15 material"
            )
        return self


class CandidateAssessment(Frozen):
    hypothesis_id: str = Field(pattern=r"^p19h_[a-f0-9]{24}$")
    grounding_link_ids: tuple[str, ...] = Field(min_length=1)
    disposition: HypothesisDisposition
    epistemic_class: HypothesisEpistemicClass
    contribution_class: ContributionClass
    evidence_strength: EvidenceStrength
    causal_qualification: CausalQualification = CausalQualification.NOT_CLAIMED
    relationship_dependent: bool = False
    relationship_policy_use_id: str | None = Field(
        default=None,
        pattern=r"^bru_[a-f0-9]{24}$",
    )
    identification_limitations: tuple[IdentificationLimitation, ...] = ()
    numeric_provenance: tuple[NumericProvenanceRef, ...] = ()
    causal_identification_refs: tuple[CausalIdentificationRef, ...] = ()

    @model_validator(mode="after")
    def coherent(self):
        if len(self.grounding_link_ids) != len(set(self.grounding_link_ids)):
            raise ValueError("candidate grounding refs must be unique")
        if len(self.identification_limitations) != len(
            set(self.identification_limitations)
        ):
            raise ValueError("identification limitations must be unique")
        if (
            self.epistemic_class == HypothesisEpistemicClass.ASSOCIATION
            and self.causal_qualification
            == CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION
        ):
            raise ValueError("association cannot be a defensible causal conclusion")
        if (
            self.relationship_dependent
            and self.relationship_policy_use_id is None
        ):
            raise ValueError(
                "relationship-dependent candidate requires P18 policy-use"
            )
        return self


class MediationAnnotation(Frozen):
    ordered_hypothesis_ids: tuple[str, ...] = Field(min_length=2)
    outcome_scope: str = Field(min_length=1)
    source_grounding_link_ids: tuple[str, ...] = Field(min_length=1)
    identification_limitation: IdentificationLimitation | None = (
        IdentificationLimitation.MEDIATION_NOT_IDENTIFIED
    )

    @model_validator(mode="after")
    def coherent(self):
        if len(self.ordered_hypothesis_ids) != len(
            set(self.ordered_hypothesis_ids)
        ):
            raise ValueError("mediation path hypothesis ids must be unique")
        if len(self.source_grounding_link_ids) != len(
            set(self.source_grounding_link_ids)
        ):
            raise ValueError("mediation grounding refs must be unique")
        return self


class RootCauseAssessmentDraft(Frozen):
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    candidates: tuple[CandidateAssessment, ...] = Field(min_length=1)
    aggregate_outcome: AggregateOutcome
    root_cause_hypothesis_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    mediation_annotations: tuple[MediationAnnotation, ...] = ()

    @model_validator(mode="after")
    def coherent(self):
        ids = tuple(x.hypothesis_id for x in self.candidates)
        if len(ids) != len(set(ids)):
            raise ValueError("assessment candidate hypothesis ids must be unique")
        if len(self.root_cause_hypothesis_ids) != len(
            set(self.root_cause_hypothesis_ids)
        ):
            raise ValueError("root-cause hypothesis ids must be unique")
        if not set(self.root_cause_hypothesis_ids).issubset(ids):
            raise ValueError("root-cause ids must be assessed candidates")
        if len(self.limitations) != len(set(self.limitations)):
            raise ValueError("assessment limitations must be unique")
        return self


class RootCauseAssessmentView(Frozen):
    assessment_id: str = Field(pattern=r"^p19a_[a-f0-9]{24}$")
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    tenant_binding: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    candidates: tuple[CandidateAssessment, ...]
    root_cause_hypothesis_ids: tuple[str, ...]
    aggregate_outcome: AggregateOutcome
    limitations: tuple[str, ...]
    mediation_annotations: tuple[MediationAnnotation, ...]
    assessment_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


class HypothesisSnapshot(Frozen):
    hypothesis: P19Hypothesis
    groundings: tuple[P19GroundingLink, ...]


class P19CaseSnapshot(Frozen):
    research_session_id: str
    obligation_id: str
    tenant_binding: str
    semantic_context_version: str
    hypotheses: tuple[HypothesisSnapshot, ...]


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
        raise P19EpistemicError(
            code,
            "value is not deterministic JSON",
        ) from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _id(prefix: str, value: Any) -> str:
    _, fingerprint = _canonical_json(value, code="P19_IDENTITY_NOT_CANONICAL")
    return prefix + fingerprint[:24]


def _clean(value: str, *, code: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise P19EpistemicError(code, "value is empty")
    return cleaned


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise P19EpistemicError(
            "P19_TIMEZONE_REQUIRED",
            "P19 timestamps must be timezone-aware",
        )
    return stamp


def _json_object(raw: str | None, *, code: str) -> Any:
    if raw is None:
        raise P19EpistemicError(code, "persisted source payload is absent")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise P19EpistemicError(code, "persisted source JSON is invalid") from exc


def _path_value(value: Any, path: str) -> Any:
    current = value
    for token in path.split("."):
        if token == "":
            raise P19EpistemicError(
                "P19_NUMERIC_SOURCE_PATH_INVALID",
                path,
            )
        if isinstance(current, list):
            if not token.isdigit():
                raise P19EpistemicError(
                    "P19_NUMERIC_SOURCE_PATH_INVALID",
                    path,
                )
            index = int(token)
            if index >= len(current):
                raise P19EpistemicError(
                    "P19_NUMERIC_SOURCE_PATH_INVALID",
                    path,
                )
            current = current[index]
        elif isinstance(current, dict):
            if token not in current:
                raise P19EpistemicError(
                    "P19_NUMERIC_SOURCE_PATH_INVALID",
                    path,
                )
            current = current[token]
        else:
            raise P19EpistemicError(
                "P19_NUMERIC_SOURCE_PATH_INVALID",
                path,
            )
    return current


class HypothesisRootCauseStore:
    """Single P19 owner for hypothesis identity, grounding and assessment snapshots."""

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
        raise P19EpistemicError(
            "P19_TENANT_REQUIRED",
            "P19 requires explicit tenant binding",
        )

    @staticmethod
    def _subject(principal: Principal) -> str:
        return _clean(str(principal.user_id), code="P19_PRINCIPAL_REQUIRED")

    def _session(self, session_id: str, principal: Principal):
        try:
            return self._research.load(
                session_id,
                tenant=self._tenant(principal),
                principal=self._subject(principal),
            )
        except ResearchPersistenceError as exc:
            raise P19EpistemicError(
                "P19_RESEARCH_SESSION_SCOPE_INVALID",
                exc.code,
            ) from exc

    def _case(
        self,
        *,
        session_id: str,
        obligation_id: str,
        principal: Principal,
    ):
        session = self._session(session_id, principal)
        try:
            ResearchManager.obligation(session, obligation_id)
        except ResearchStateError as exc:
            raise P19EpistemicError(
                "P19_OBLIGATION_INVALID",
                obligation_id,
            ) from exc
        return session

    @staticmethod
    def _hydrate_hypothesis(row: HypothesisRecord) -> P19Hypothesis:
        return P19Hypothesis(
            hypothesis_id=row.hypothesis_id,
            research_session_id=row.research_session_id,
            obligation_id=row.obligation_id,
            tenant_binding=row.tenant_binding,
            semantic_context_version=row.semantic_context_version,
            statement=row.statement,
            identity_fingerprint=row.identity_fingerprint,
            created_at=row.created_at,
        )

    @staticmethod
    def _hydrate_grounding(
        row: HypothesisGroundingLinkRecord,
    ) -> P19GroundingLink:
        return P19GroundingLink(
            grounding_link_id=row.grounding_link_id,
            hypothesis_id=row.hypothesis_id,
            source_kind=GroundingSourceKind(row.source_kind),
            source_ref=row.source_ref,
            source_receipt_id=row.source_receipt_id,
            relation=GroundingRelation(row.relation),
            link_fingerprint=row.link_fingerprint,
            created_at=row.created_at,
        )

    def create_hypothesis(
        self,
        *,
        research_session_id: str,
        obligation_id: str,
        statement: str,
        principal: Principal,
        now: datetime | None = None,
    ) -> P19Hypothesis:
        session = self._case(
            session_id=research_session_id,
            obligation_id=obligation_id,
            principal=principal,
        )
        text = _clean(statement, code="P19_HYPOTHESIS_STATEMENT_REQUIRED")
        identity = {
            "research_authority_id": session.authority_id,
            "research_session_id": session.session_id,
            "obligation_id": obligation_id,
            "tenant_binding": session.tenant_binding,
            "semantic_context_version": session.context_version,
            "statement": text,
        }
        _, fingerprint = _canonical_json(
            identity,
            code="P19_HYPOTHESIS_NOT_CANONICAL",
        )
        hypothesis_id = "p19h_" + fingerprint[:24]

        with Session(self._engine) as db:
            existing = db.get(HypothesisRecord, hypothesis_id)
            if existing is not None:
                if existing.identity_fingerprint != fingerprint:
                    raise P19EpistemicError(
                        "P19_HYPOTHESIS_IDENTITY_CONFLICT",
                        hypothesis_id,
                    )
                return self._hydrate_hypothesis(existing)
            row = HypothesisRecord(
                hypothesis_id=hypothesis_id,
                research_session_id=session.session_id,
                obligation_id=obligation_id,
                tenant_binding=session.tenant_binding,
                semantic_context_version=session.context_version,
                statement=text,
                identity_fingerprint=fingerprint,
                created_at=_aware(now),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_hypothesis(row)

    def load_hypothesis(
        self,
        *,
        hypothesis_id: str,
        principal: Principal,
    ) -> P19Hypothesis:
        tenant = self._tenant(principal)
        with Session(self._engine) as db:
            row = db.get(HypothesisRecord, hypothesis_id)
            if row is None:
                raise P19EpistemicError(
                    "P19_HYPOTHESIS_NOT_FOUND",
                    hypothesis_id,
                )
            if row.tenant_binding != tenant:
                raise P19EpistemicError(
                    "P19_HYPOTHESIS_TENANT_MISMATCH",
                    hypothesis_id,
                )
            hypothesis = self._hydrate_hypothesis(row)
        session = self._session(
            hypothesis.research_session_id,
            principal,
        )
        if (
            session.context_version != hypothesis.semantic_context_version
            or session.tenant_binding != hypothesis.tenant_binding
        ):
            raise P19EpistemicError(
                "P19_HYPOTHESIS_CONTEXT_MISMATCH",
                hypothesis_id,
            )
        return hypothesis

    def _source_authority(
        self,
        *,
        session_id: str,
        obligation_id: str,
        source_kind: GroundingSourceKind,
        source_ref: str,
        source_receipt_id: str | None,
    ) -> Any:
        with Session(self._engine) as db:
            if source_kind == GroundingSourceKind.P14_EVIDENCE:
                rows = tuple(
                    db.exec(
                        select(ResearchExecutionLink)
                        .where(ResearchExecutionLink.session_id == session_id)
                        .where(ResearchExecutionLink.obligation_id == obligation_id)
                        .where(ResearchExecutionLink.evidence_id == source_ref)
                        .where(ResearchExecutionLink.status == "VERIFIED")
                    ).all()
                )
                if len(rows) != 1:
                    raise P19EpistemicError(
                        "P19_EVIDENCE_SOURCE_NOT_FOUND",
                        source_ref,
                    )
                row = rows[0]
                if (
                    not source_receipt_id
                    or not row.receipt_id
                    or source_receipt_id != row.receipt_id
                ):
                    raise P19EpistemicError(
                        "P19_EVIDENCE_RECEIPT_MISMATCH",
                        source_ref,
                    )
                return row

            if source_receipt_id is not None:
                raise P19EpistemicError(
                    "P19_SOURCE_RECEIPT_NOT_ALLOWED",
                    source_kind.value,
                )

            if source_kind == GroundingSourceKind.P15_MATERIAL:
                row = db.get(ResearchExplorationMaterial, source_ref)
                if row is None:
                    raise P19EpistemicError(
                        "P19_MATERIAL_SOURCE_NOT_FOUND",
                        source_ref,
                    )
                if (
                    row.session_id != session_id
                    or row.obligation_id != obligation_id
                    or row.epistemic_state != "RESEARCH_MATERIAL"
                ):
                    raise P19EpistemicError(
                        "P19_MATERIAL_SOURCE_SCOPE_MISMATCH",
                        source_ref,
                    )
                return row

            if source_kind == GroundingSourceKind.P16_CLAIM:
                row = db.get(ResearchClaimRecord, source_ref)
                if row is None:
                    raise P19EpistemicError(
                        "P19_CLAIM_SOURCE_NOT_FOUND",
                        source_ref,
                    )
                if (
                    row.session_id != session_id
                    or row.obligation_id != obligation_id
                ):
                    raise P19EpistemicError(
                        "P19_CLAIM_SOURCE_SCOPE_MISMATCH",
                        source_ref,
                    )
                return row

            if source_kind == GroundingSourceKind.P17_REASONING_STEP:
                row = db.get(ResearchReasoningStepRecord, source_ref)
                if row is None:
                    raise P19EpistemicError(
                        "P19_REASONING_SOURCE_NOT_FOUND",
                        source_ref,
                    )
                if (
                    row.session_id != session_id
                    or row.parent_obligation_id != obligation_id
                ):
                    raise P19EpistemicError(
                        "P19_REASONING_SOURCE_SCOPE_MISMATCH",
                        source_ref,
                    )
                return row

            if source_kind == GroundingSourceKind.P18_POLICY_USE:
                row = db.get(BusinessRelationshipPolicyUseRecord, source_ref)
                if row is None:
                    raise P19EpistemicError(
                        "P19_POLICY_USE_SOURCE_NOT_FOUND",
                        source_ref,
                    )
                if (
                    row.research_session_id != session_id
                    or row.obligation_id != obligation_id
                ):
                    raise P19EpistemicError(
                        "P19_POLICY_USE_SOURCE_SCOPE_MISMATCH",
                        source_ref,
                    )
                return row

        raise P19EpistemicError(
            "P19_SOURCE_KIND_INVALID",
            source_kind.value,
        )

    def create_grounding(
        self,
        *,
        hypothesis_id: str,
        source_kind: GroundingSourceKind,
        source_ref: str,
        relation: GroundingRelation,
        principal: Principal,
        source_receipt_id: str | None = None,
        now: datetime | None = None,
    ) -> P19GroundingLink:
        hypothesis = self.load_hypothesis(
            hypothesis_id=hypothesis_id,
            principal=principal,
        )
        source = _clean(source_ref, code="P19_SOURCE_REF_REQUIRED")
        authority = self._source_authority(
            session_id=hypothesis.research_session_id,
            obligation_id=hypothesis.obligation_id,
            source_kind=source_kind,
            source_ref=source,
            source_receipt_id=source_receipt_id,
        )
        if source_kind == GroundingSourceKind.P16_CLAIM and (
            authority.tenant_binding != hypothesis.tenant_binding
            or authority.semantic_context_version
            != hypothesis.semantic_context_version
        ):
            raise P19EpistemicError(
                "P19_CLAIM_SOURCE_CONTEXT_MISMATCH",
                source,
            )
        identity = {
            "hypothesis_id": hypothesis.hypothesis_id,
            "source_kind": source_kind.value,
            "source_ref": source,
            "source_receipt_id": source_receipt_id,
            "relation": relation.value,
        }
        _, fingerprint = _canonical_json(
            identity,
            code="P19_GROUNDING_NOT_CANONICAL",
        )
        grounding_id = "p19g_" + fingerprint[:24]
        with Session(self._engine) as db:
            existing = db.get(
                HypothesisGroundingLinkRecord,
                grounding_id,
            )
            if existing is not None:
                if existing.link_fingerprint != fingerprint:
                    raise P19EpistemicError(
                        "P19_GROUNDING_IDENTITY_CONFLICT",
                        grounding_id,
                    )
                return self._hydrate_grounding(existing)
            row = HypothesisGroundingLinkRecord(
                grounding_link_id=grounding_id,
                hypothesis_id=hypothesis.hypothesis_id,
                source_kind=source_kind.value,
                source_ref=source,
                source_receipt_id=source_receipt_id,
                relation=relation.value,
                link_fingerprint=fingerprint,
                created_at=_aware(now),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_grounding(row)

    def _case_hypotheses(
        self,
        *,
        session_id: str,
        obligation_id: str,
    ) -> tuple[P19Hypothesis, ...]:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(HypothesisRecord)
                    .where(
                        HypothesisRecord.research_session_id == session_id
                    )
                    .where(HypothesisRecord.obligation_id == obligation_id)
                    .order_by(HypothesisRecord.created_at, HypothesisRecord.hypothesis_id)
                ).all()
            )
        return tuple(self._hydrate_hypothesis(row) for row in rows)

    def _groundings(
        self,
        hypothesis_id: str,
    ) -> tuple[P19GroundingLink, ...]:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(HypothesisGroundingLinkRecord)
                    .where(
                        HypothesisGroundingLinkRecord.hypothesis_id
                        == hypothesis_id
                    )
                    .order_by(
                        HypothesisGroundingLinkRecord.created_at,
                        HypothesisGroundingLinkRecord.grounding_link_id,
                    )
                ).all()
            )
        return tuple(self._hydrate_grounding(row) for row in rows)

    def snapshot(
        self,
        *,
        research_session_id: str,
        obligation_id: str,
        principal: Principal,
    ) -> P19CaseSnapshot:
        session = self._case(
            session_id=research_session_id,
            obligation_id=obligation_id,
            principal=principal,
        )
        hypotheses = self._case_hypotheses(
            session_id=session.session_id,
            obligation_id=obligation_id,
        )
        return P19CaseSnapshot(
            research_session_id=session.session_id,
            obligation_id=obligation_id,
            tenant_binding=session.tenant_binding,
            semantic_context_version=session.context_version,
            hypotheses=tuple(
                HypothesisSnapshot(
                    hypothesis=h,
                    groundings=self._groundings(h.hypothesis_id),
                )
                for h in hypotheses
            ),
        )

    def _validate_numeric(
        self,
        *,
        session_id: str,
        obligation_id: str,
        ref: NumericProvenanceRef,
    ) -> None:
        row = self._source_authority(
            session_id=session_id,
            obligation_id=obligation_id,
            source_kind=ref.source_kind,
            source_ref=ref.source_ref,
            source_receipt_id=ref.source_receipt_id,
        )
        if ref.source_kind == GroundingSourceKind.P14_EVIDENCE:
            payload = _json_object(
                row.native_result_json,
                code="P19_NUMERIC_SOURCE_PAYLOAD_INVALID",
            )
        else:
            payload = _json_object(
                row.native_payload_json,
                code="P19_NUMERIC_SOURCE_PAYLOAD_INVALID",
            )
        value = _path_value(payload, ref.source_path)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise P19EpistemicError(
                "P19_NUMERIC_SOURCE_NOT_NUMERIC",
                ref.source_path,
            )
        if (
            ref.analytical_kind
            == NumericAnalyticalKind.DIRECT_INDIRECT_DECOMPOSITION
        ):
            assert ref.analytical_kind_path is not None
            marker = _path_value(payload, ref.analytical_kind_path)
            if marker != ref.analytical_kind.value:
                raise P19EpistemicError(
                    "P19_NUMERIC_ANALYTICAL_KIND_MISMATCH",
                    ref.analytical_kind_path,
                )

    def _validate_causal_identification(
        self,
        *,
        session_id: str,
        obligation_id: str,
        ref: CausalIdentificationRef,
    ) -> None:
        row = self._source_authority(
            session_id=session_id,
            obligation_id=obligation_id,
            source_kind=ref.source_kind,
            source_ref=ref.source_ref,
            source_receipt_id=ref.source_receipt_id,
        )
        if ref.source_kind == GroundingSourceKind.P14_EVIDENCE:
            payload = _json_object(
                row.native_result_json,
                code="P19_CAUSAL_IDENTIFICATION_SOURCE_INVALID",
            )
        else:
            payload = _json_object(
                row.native_payload_json,
                code="P19_CAUSAL_IDENTIFICATION_SOURCE_INVALID",
            )
        value = _path_value(payload, ref.source_path)
        if value != ref.identification_kind.value:
            raise P19EpistemicError(
                "P19_CAUSAL_IDENTIFICATION_SOURCE_MISMATCH",
                ref.source_path,
            )

    def _p18_status(
        self,
        *,
        session_id: str,
        obligation_id: str,
        policy_use_id: str,
    ) -> str:
        row = self._source_authority(
            session_id=session_id,
            obligation_id=obligation_id,
            source_kind=GroundingSourceKind.P18_POLICY_USE,
            source_ref=policy_use_id,
            source_receipt_id=None,
        )
        return row.resolution_status

    @staticmethod
    def _candidate_payload(candidate: CandidateAssessment) -> dict[str, Any]:
        value = candidate.model_dump(mode="json")
        value.pop("numeric_provenance", None)
        return value

    @staticmethod
    def _numeric_payload(
        candidates: tuple[CandidateAssessment, ...],
    ) -> dict[str, Any]:
        return {
            item.hypothesis_id: [
                ref.model_dump(mode="json")
                for ref in item.numeric_provenance
            ]
            for item in candidates
            if item.numeric_provenance
        }

    @staticmethod
    def _hydrate_assessment(
        row: RootCauseAssessmentRecord,
    ) -> RootCauseAssessmentView:
        try:
            candidate_rows = json.loads(row.candidate_assessments_json)
            root_ids = json.loads(row.root_cause_hypothesis_ids_json)
            limitations = json.loads(row.limitations_json)
            numeric = json.loads(row.numeric_provenance_json)
            mediation = json.loads(row.mediation_annotations_json)
        except json.JSONDecodeError as exc:
            raise P19EpistemicError(
                "P19_ASSESSMENT_PERSISTENCE_INVALID",
                row.assessment_id,
            ) from exc
        if (
            not isinstance(candidate_rows, list)
            or not isinstance(root_ids, list)
            or not isinstance(limitations, list)
            or not isinstance(numeric, dict)
            or not isinstance(mediation, list)
        ):
            raise P19EpistemicError(
                "P19_ASSESSMENT_PERSISTENCE_INVALID",
                row.assessment_id,
            )
        candidates = []
        for item in candidate_rows:
            if not isinstance(item, dict):
                raise P19EpistemicError(
                    "P19_ASSESSMENT_PERSISTENCE_INVALID",
                    row.assessment_id,
                )
            hid = item.get("hypothesis_id")
            refs = numeric.get(hid, [])
            if not isinstance(refs, list):
                raise P19EpistemicError(
                    "P19_ASSESSMENT_PERSISTENCE_INVALID",
                    row.assessment_id,
                )
            candidates.append(
                CandidateAssessment.model_validate(
                    {**item, "numeric_provenance": refs}
                )
            )
        return RootCauseAssessmentView(
            assessment_id=row.assessment_id,
            research_session_id=row.research_session_id,
            obligation_id=row.obligation_id,
            tenant_binding=row.tenant_binding,
            semantic_context_version=row.semantic_context_version,
            candidates=tuple(candidates),
            root_cause_hypothesis_ids=tuple(root_ids),
            aggregate_outcome=AggregateOutcome(row.aggregate_outcome),
            limitations=tuple(limitations),
            mediation_annotations=tuple(
                MediationAnnotation.model_validate(item)
                for item in mediation
            ),
            assessment_fingerprint=row.assessment_fingerprint,
            created_at=row.created_at,
        )

    def _validate_assessment(
        self,
        *,
        session,
        draft: RootCauseAssessmentDraft,
    ) -> None:
        hypotheses = self._case_hypotheses(
            session_id=session.session_id,
            obligation_id=draft.obligation_id,
        )
        known = {item.hypothesis_id: item for item in hypotheses}
        assessed = {item.hypothesis_id for item in draft.candidates}
        if not known:
            raise P19EpistemicError(
                "P19_HYPOTHESES_REQUIRED",
                "case has no P19 hypotheses",
            )
        if assessed != set(known):
            raise P19EpistemicError(
                "P19_ALTERNATIVE_SET_INCOMPLETE",
                "assessment must preserve all current case hypotheses",
            )
        if (
            draft.aggregate_outcome != AggregateOutcome.IN_PROGRESS
            and len(known) < 2
        ):
            raise P19EpistemicError(
                "P19_COMPETING_ALTERNATIVES_REQUIRED",
                "terminal assessment requires at least two hypotheses",
            )

        candidate_map = {
            item.hypothesis_id: item for item in draft.candidates
        }
        grounding_map: dict[str, P19GroundingLink] = {}
        candidate_groundings: dict[str, tuple[P19GroundingLink, ...]] = {}
        for candidate in draft.candidates:
            all_links = {
                item.grounding_link_id: item
                for item in self._groundings(candidate.hypothesis_id)
            }
            if not set(candidate.grounding_link_ids).issubset(all_links):
                raise P19EpistemicError(
                    "P19_GROUNDING_REF_INVALID",
                    candidate.hypothesis_id,
                )
            selected = tuple(
                all_links[item] for item in candidate.grounding_link_ids
            )
            if not selected:
                raise P19EpistemicError(
                    "P19_GROUNDING_REQUIRED",
                    candidate.hypothesis_id,
                )
            candidate_groundings[candidate.hypothesis_id] = selected
            grounding_map.update(
                {item.grounding_link_id: item for item in selected}
            )
            selected_sources = {
                (
                    item.source_kind,
                    item.source_ref,
                    item.source_receipt_id,
                )
                for item in selected
            }
            for numeric in candidate.numeric_provenance:
                if (
                    numeric.source_kind,
                    numeric.source_ref,
                    numeric.source_receipt_id,
                ) not in selected_sources:
                    raise P19EpistemicError(
                        "P19_PROVENANCE_GROUNDING_REQUIRED",
                        candidate.hypothesis_id,
                    )
                self._validate_numeric(
                    session_id=session.session_id,
                    obligation_id=draft.obligation_id,
                    ref=numeric,
                )
            for causal_ref in candidate.causal_identification_refs:
                if (
                    causal_ref.source_kind,
                    causal_ref.source_ref,
                    causal_ref.source_receipt_id,
                ) not in selected_sources:
                    raise P19EpistemicError(
                        "P19_PROVENANCE_GROUNDING_REQUIRED",
                        candidate.hypothesis_id,
                    )
                self._validate_causal_identification(
                    session_id=session.session_id,
                    obligation_id=draft.obligation_id,
                    ref=causal_ref,
                )

            if (
                candidate.causal_qualification
                == CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION
                and candidate.epistemic_class
                != HypothesisEpistemicClass.CANDIDATE_CAUSE
            ):
                raise P19EpistemicError(
                    "P19_CAUSAL_CLASS_INVALID",
                    candidate.hypothesis_id,
                )

            if candidate.relationship_dependent:
                assert candidate.relationship_policy_use_id is not None
                p18_status = self._p18_status(
                    session_id=session.session_id,
                    obligation_id=draft.obligation_id,
                    policy_use_id=candidate.relationship_policy_use_id,
                )
                has_policy_grounding = any(
                    item.source_kind == GroundingSourceKind.P18_POLICY_USE
                    and item.source_ref == candidate.relationship_policy_use_id
                    for item in selected
                )
                if not has_policy_grounding:
                    raise P19EpistemicError(
                        "P19_P18_POLICY_GROUNDING_REQUIRED",
                        candidate.hypothesis_id,
                    )
                if (
                    p18_status != "SATISFIED"
                    and candidate.causal_qualification
                    == CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION
                ):
                    raise P19EpistemicError(
                        "P19_P18_POLICY_BLOCKS_CAUSAL_PROMOTION",
                        candidate.hypothesis_id,
                    )

        for annotation in draft.mediation_annotations:
            if not set(annotation.ordered_hypothesis_ids).issubset(known):
                raise P19EpistemicError(
                    "P19_MEDIATION_HYPOTHESIS_INVALID",
                    annotation.outcome_scope,
                )
            if not set(annotation.source_grounding_link_ids).issubset(
                grounding_map
            ):
                raise P19EpistemicError(
                    "P19_MEDIATION_GROUNDING_INVALID",
                    annotation.outcome_scope,
                )
            material_members = tuple(
                hid
                for hid in annotation.ordered_hypothesis_ids
                if candidate_map[hid].contribution_class
                in {ContributionClass.DOMINANT, ContributionClass.MATERIAL}
                and candidate_map[hid].disposition
                == HypothesisDisposition.RETAINED
            )
            direct_indirect = any(
                numeric.analytical_kind
                == NumericAnalyticalKind.DIRECT_INDIRECT_DECOMPOSITION
                for candidate in draft.candidates
                for numeric in candidate.numeric_provenance
            )
            if len(material_members) > 1 and not direct_indirect:
                raise P19EpistemicError(
                    "P19_MEDIATION_DOUBLE_COUNT_UNSAFE",
                    annotation.outcome_scope,
                )

        if draft.aggregate_outcome == AggregateOutcome.ROOT_CAUSE_ESTABLISHED:
            if not draft.root_cause_hypothesis_ids:
                raise P19EpistemicError(
                    "P19_ROOT_CAUSE_ID_REQUIRED",
                    "root cause outcome requires at least one hypothesis id",
                )
            counter_considered = any(
                link.relation
                in {GroundingRelation.CHALLENGES, GroundingRelation.INSUFFICIENT}
                for links in candidate_groundings.values()
                for link in links
            )
            if not counter_considered:
                raise P19EpistemicError(
                    "P19_COUNTER_EVIDENCE_NOT_CONSIDERED",
                    "root-cause promotion requires counter/insufficiency consideration",
                )
            for hid in draft.root_cause_hypothesis_ids:
                candidate = candidate_map[hid]
                links = candidate_groundings[hid]
                has_supporting_evidence = any(
                    link.source_kind == GroundingSourceKind.P14_EVIDENCE
                    and link.relation == GroundingRelation.SUPPORTS
                    for link in links
                )
                has_challenge = any(
                    link.relation == GroundingRelation.CHALLENGES
                    for link in links
                )
                if (
                    candidate.disposition != HypothesisDisposition.RETAINED
                    or candidate.epistemic_class
                    != HypothesisEpistemicClass.CANDIDATE_CAUSE
                    or candidate.causal_qualification
                    != CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION
                    or candidate.evidence_strength
                    not in {EvidenceStrength.STRONG, EvidenceStrength.MODERATE}
                    or candidate.contribution_class == ContributionClass.UNKNOWN
                    or candidate.identification_limitations
                    or not candidate.causal_identification_refs
                    or not has_supporting_evidence
                    or has_challenge
                ):
                    raise P19EpistemicError(
                        "P19_CAUSAL_PROMOTION_GATE_FAILED",
                        hid,
                    )
                if candidate.relationship_dependent:
                    assert candidate.relationship_policy_use_id is not None
                    if (
                        self._p18_status(
                            session_id=session.session_id,
                            obligation_id=draft.obligation_id,
                            policy_use_id=candidate.relationship_policy_use_id,
                        )
                        != "SATISFIED"
                    ):
                        raise P19EpistemicError(
                            "P19_CAUSAL_PROMOTION_GATE_FAILED",
                            hid,
                        )
        elif draft.root_cause_hypothesis_ids:
            raise P19EpistemicError(
                "P19_ROOT_CAUSE_IDS_OUTCOME_MISMATCH",
                draft.aggregate_outcome.value,
            )

        if (
            draft.aggregate_outcome
            == AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS
        ):
            material = tuple(
                item
                for item in draft.candidates
                if item.disposition == HypothesisDisposition.RETAINED
                and item.contribution_class
                in {ContributionClass.DOMINANT, ContributionClass.MATERIAL}
            )
            if len(material) < 2:
                raise P19EpistemicError(
                    "P19_MULTIPLE_MATERIAL_CONTRIBUTORS_REQUIRED",
                    "outcome requires at least two retained material contributors",
                )

    def assess(
        self,
        *,
        draft: RootCauseAssessmentDraft,
        principal: Principal,
        now: datetime | None = None,
    ) -> RootCauseAssessmentView:
        session = self._case(
            session_id=draft.research_session_id,
            obligation_id=draft.obligation_id,
            principal=principal,
        )
        self._validate_assessment(session=session, draft=draft)

        candidate_payload = [
            self._candidate_payload(item) for item in draft.candidates
        ]
        numeric_payload = self._numeric_payload(draft.candidates)
        mediation_payload = [
            item.model_dump(mode="json")
            for item in draft.mediation_annotations
        ]
        identity = {
            "research_authority_id": session.authority_id,
            "research_session_id": session.session_id,
            "obligation_id": draft.obligation_id,
            "tenant_binding": session.tenant_binding,
            "semantic_context_version": session.context_version,
            "candidates": candidate_payload,
            "numeric_provenance": numeric_payload,
            "root_cause_hypothesis_ids": list(
                draft.root_cause_hypothesis_ids
            ),
            "aggregate_outcome": draft.aggregate_outcome.value,
            "limitations": list(draft.limitations),
            "mediation_annotations": mediation_payload,
        }
        _, fingerprint = _canonical_json(
            identity,
            code="P19_ASSESSMENT_NOT_CANONICAL",
        )
        assessment_id = "p19a_" + fingerprint[:24]

        candidate_json = _canonical_json(
            candidate_payload,
            code="P19_CANDIDATES_NOT_CANONICAL",
        )[0]
        root_json = _canonical_json(
            list(draft.root_cause_hypothesis_ids),
            code="P19_ROOT_IDS_NOT_CANONICAL",
        )[0]
        limitations_json = _canonical_json(
            list(draft.limitations),
            code="P19_LIMITATIONS_NOT_CANONICAL",
        )[0]
        numeric_json = _canonical_json(
            numeric_payload,
            code="P19_NUMERIC_PROVENANCE_NOT_CANONICAL",
        )[0]
        mediation_json = _canonical_json(
            mediation_payload,
            code="P19_MEDIATION_NOT_CANONICAL",
        )[0]

        with Session(self._engine) as db:
            existing = db.get(RootCauseAssessmentRecord, assessment_id)
            if existing is not None:
                if existing.assessment_fingerprint != fingerprint:
                    raise P19EpistemicError(
                        "P19_ASSESSMENT_IDENTITY_CONFLICT",
                        assessment_id,
                    )
                return self._hydrate_assessment(existing)
            row = RootCauseAssessmentRecord(
                assessment_id=assessment_id,
                research_session_id=session.session_id,
                obligation_id=draft.obligation_id,
                tenant_binding=session.tenant_binding,
                semantic_context_version=session.context_version,
                candidate_assessments_json=candidate_json,
                root_cause_hypothesis_ids_json=root_json,
                aggregate_outcome=draft.aggregate_outcome.value,
                limitations_json=limitations_json,
                numeric_provenance_json=numeric_json,
                mediation_annotations_json=mediation_json,
                assessment_fingerprint=fingerprint,
                created_at=_aware(now),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate_assessment(row)

    def load_assessment(
        self,
        *,
        assessment_id: str,
        principal: Principal,
    ) -> RootCauseAssessmentView:
        tenant = self._tenant(principal)
        with Session(self._engine) as db:
            row = db.get(RootCauseAssessmentRecord, assessment_id)
            if row is None:
                raise P19EpistemicError(
                    "P19_ASSESSMENT_NOT_FOUND",
                    assessment_id,
                )
            if row.tenant_binding != tenant:
                raise P19EpistemicError(
                    "P19_ASSESSMENT_TENANT_MISMATCH",
                    assessment_id,
                )
            assessment = self._hydrate_assessment(row)
        session = self._session(
            assessment.research_session_id,
            principal,
        )
        if (
            session.context_version != assessment.semantic_context_version
            or session.tenant_binding != assessment.tenant_binding
        ):
            raise P19EpistemicError(
                "P19_ASSESSMENT_CONTEXT_MISMATCH",
                assessment_id,
            )
        return assessment
