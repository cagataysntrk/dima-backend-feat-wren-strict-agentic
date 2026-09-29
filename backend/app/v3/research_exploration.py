"""P15 native Metabase Exploration over sealed P14 Research occurrences.

This module owns Research-material provenance only. Native Metabase owns exploration,
analytical semantics, selection and permissions. P15 material is not a verified claim.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from app.v3.research import ObligationState, ResearchManager
from app.v3.research_native_gateway import NativeSubjectSessionProvider
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from app.v3.substrate.metabase.native_engine import (
    NativeEngineBridgeError,
    NativeExplorationError,
)
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import ResearchExplorationMaterial


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchExplorationError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ResearchLead(Frozen):
    lead_id: str = Field(pattern=r"^lead_[a-f0-9]{24}$")
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    execution_link_id: uuid.UUID
    native_conversation_id: uuid.UUID
    native_query_id: str = Field(min_length=1)
    query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_evidence_refs: tuple[str, ...] = Field(min_length=1)
    exploration_kind: Literal["automagic_adhoc"] = "automagic_adhoc"
    material_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    epistemic_state: Literal["RESEARCH_MATERIAL"] = "RESEARCH_MATERIAL"
    material: dict[str, Any]
    created_at: datetime


def _canonical(value: Any, *, code: str) -> tuple[str, str]:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ResearchExplorationError(
            code,
            "native exploration material is not deterministic JSON",
        ) from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _lead_id(execution_link_id: uuid.UUID, material_fingerprint: str) -> str:
    raw = f"{execution_link_id}\x1f{material_fingerprint}"
    return "lead_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class ResearchExplorationStore:
    def __init__(self, db_engine=None) -> None:
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _source_refs(record: ResearchExplorationMaterial) -> tuple[str, ...]:
        try:
            refs = json.loads(record.source_evidence_refs_json)
        except json.JSONDecodeError as exc:
            raise ResearchExplorationError(
                "P15_SOURCE_EVIDENCE_PROVENANCE_INVALID",
                "persisted source Evidence refs are invalid JSON",
            ) from exc
        if (
            not isinstance(refs, list)
            or not refs
            or any(not isinstance(item, str) or not item for item in refs)
            or len(refs) != len(set(refs))
        ):
            raise ResearchExplorationError(
                "P15_SOURCE_EVIDENCE_PROVENANCE_INVALID",
                "persisted source Evidence refs are invalid",
            )
        return tuple(refs)

    @classmethod
    def _lead(cls, record: ResearchExplorationMaterial) -> ResearchLead:
        try:
            material = json.loads(record.native_payload_json)
        except json.JSONDecodeError as exc:
            raise ResearchExplorationError(
                "P15_NATIVE_EXPLORATION_MATERIAL_INVALID",
                "persisted native exploration material is invalid JSON",
            ) from exc
        if not isinstance(material, dict):
            raise ResearchExplorationError(
                "P15_NATIVE_EXPLORATION_MATERIAL_INVALID",
                "persisted native exploration material is not an object",
            )
        _, observed = _canonical(
            material,
            code="P15_NATIVE_EXPLORATION_MATERIAL_INVALID",
        )
        if observed != record.payload_fingerprint:
            raise ResearchExplorationError(
                "P15_NATIVE_EXPLORATION_FINGERPRINT_MISMATCH",
                "persisted native exploration material changed after capture",
            )
        if record.epistemic_state != "RESEARCH_MATERIAL":
            raise ResearchExplorationError(
                "P15_EPISTEMIC_STATE_INVALID",
                "native exploration material was promoted outside P16 governance",
            )
        return ResearchLead(
            lead_id=record.lead_id,
            research_session_id=record.session_id,
            obligation_id=record.obligation_id,
            execution_link_id=record.execution_link_id,
            native_conversation_id=record.native_conversation_id,
            native_query_id=record.native_query_id,
            query_fingerprint=record.query_fingerprint,
            source_evidence_refs=cls._source_refs(record),
            exploration_kind="automagic_adhoc",
            material_fingerprint=record.payload_fingerprint,
            material=material,
            created_at=record.created_at,
        )

    def for_execution_link(
        self,
        execution_link_id: uuid.UUID,
    ) -> ResearchLead | None:
        with Session(self._engine) as db:
            rows = db.exec(
                select(ResearchExplorationMaterial).where(
                    ResearchExplorationMaterial.execution_link_id
                    == execution_link_id
                )
            ).all()
        if not rows:
            return None
        if len(rows) != 1:
            raise ResearchExplorationError(
                "P15_NATIVE_EXPLORATION_DUPLICATE",
                "one P14 occurrence maps to multiple P15 material records",
            )
        return self._lead(rows[0])

    def persist(
        self,
        *,
        session_id: str,
        obligation_id: str,
        execution_link_id: uuid.UUID,
        native_conversation_id: uuid.UUID,
        native_query_id: str,
        query_fingerprint: str,
        source_evidence_refs: tuple[str, ...],
        material: dict[str, Any],
        now: datetime | None = None,
    ) -> ResearchLead:
        if (
            not source_evidence_refs
            or len(source_evidence_refs) != len(set(source_evidence_refs))
        ):
            raise ResearchExplorationError(
                "P15_SOURCE_EVIDENCE_REQUIRED",
                "P15 material requires unique source Evidence refs",
            )
        raw, fingerprint = _canonical(
            material,
            code="P15_NATIVE_EXPLORATION_MATERIAL_INVALID",
        )
        lead_id = _lead_id(execution_link_id, fingerprint)
        existing = self.for_execution_link(execution_link_id)
        if existing is not None:
            if (
                existing.lead_id != lead_id
                or existing.query_fingerprint != query_fingerprint
                or existing.source_evidence_refs != source_evidence_refs
            ):
                raise ResearchExplorationError(
                    "P15_NATIVE_EXPLORATION_IDEMPOTENCY_CONFLICT",
                    "existing exploration material differs from the proposed identity",
                )
            return existing

        record = ResearchExplorationMaterial(
            lead_id=lead_id,
            session_id=session_id,
            obligation_id=obligation_id,
            execution_link_id=execution_link_id,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            query_fingerprint=query_fingerprint,
            source_evidence_refs_json=json.dumps(
                list(source_evidence_refs),
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            exploration_kind="automagic_adhoc",
            native_payload_json=raw,
            payload_fingerprint=fingerprint,
            epistemic_state="RESEARCH_MATERIAL",
            created_at=now or datetime.now(timezone.utc),
        )
        with Session(self._engine) as db:
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._lead(record)


class NativeResearchExploration:
    """Consume native exploration without becoming an analytical authority."""

    def __init__(
        self,
        *,
        research_store: ResearchSessionStore,
        subject_provider: NativeSubjectSessionProvider,
        material_store: ResearchExplorationStore | None = None,
    ) -> None:
        self._research = research_store
        self._subjects = subject_provider
        self._materials = material_store or ResearchExplorationStore(
            research_store._engine
        )

    @staticmethod
    def _tenant(principal: Principal) -> str:
        if principal.tenant_id is not None:
            return f"id:{principal.tenant_id}"
        if principal.tenant_slug:
            return f"slug:{principal.tenant_slug}"
        raise ResearchExplorationError(
            "P15_RESEARCH_TENANT_REQUIRED",
            "P15 exploration requires an explicit tenant binding",
        )

    def _explore_verified_link(
        self,
        *,
        session,
        link,
        principal: Principal,
        native_session_token: str | None,
        require_base_evidence_membership: bool,
    ) -> ResearchLead:
        obligation = ResearchManager.obligation(
            session,
            link.obligation_id,
        )
        if obligation.state != ObligationState.VERIFIED:
            raise ResearchExplorationError(
                "P15_VERIFIED_RESEARCH_OBLIGATION_REQUIRED",
                "P15 exploration consumes a VERIFIED Research obligation",
            )
        if link.status != "VERIFIED":
            raise ResearchExplorationError(
                "P15_VERIFIED_NATIVE_OCCURRENCE_REQUIRED",
                "native exploration requires a VERIFIED occurrence",
            )
        if (
            not link.native_query_id
            or not link.native_query_fingerprint
            or not link.evidence_id
            or not link.receipt_id
        ):
            raise ResearchExplorationError(
                "P15_VERIFIED_NATIVE_PROVENANCE_INCOMPLETE",
                "verified occurrence lacks query/receipt/Evidence provenance",
            )
        if (
            require_base_evidence_membership
            and link.evidence_id not in obligation.evidence_refs
        ):
            raise ResearchExplorationError(
                "P15_SOURCE_EVIDENCE_MISMATCH",
                (
                    "verified P14 base occurrence is not linked to the "
                    "Research obligation Evidence"
                ),
            )

        existing = self._materials.for_execution_link(link.id)
        if existing is not None:
            return existing

        try:
            query, fingerprint = self._research.captured_query(link)
        except ResearchPersistenceError as exc:
            raise ResearchExplorationError(exc.code, exc.detail) from exc

        try:
            with self._subjects.open(
                principal=principal,
                session=session,
                native_session_token=native_session_token,
            ) as bridge:
                observation = bridge.explore_adhoc(query)
        except NativeExplorationError as exc:
            raise ResearchExplorationError(
                f"P15_NATIVE_EXPLORATION_HTTP_{exc.status_code}",
                exc.detail,
            ) from exc
        except NativeEngineBridgeError as exc:
            raise ResearchExplorationError(
                "P15_NATIVE_EXPLORATION_TRANSPORT_FAILED",
                str(exc),
            ) from exc

        if observation.query_fingerprint != fingerprint:
            raise ResearchExplorationError(
                "P15_NATIVE_EXPLORATION_QUERY_MISMATCH",
                "native exploration did not consume exact captured query A",
            )
        return self._materials.persist(
            session_id=session.session_id,
            obligation_id=link.obligation_id,
            execution_link_id=link.id,
            native_conversation_id=link.native_conversation_id,
            native_query_id=link.native_query_id,
            query_fingerprint=fingerprint,
            source_evidence_refs=(link.evidence_id,),
            material=observation.payload,
        )

    def explore(
        self,
        *,
        session_id: str,
        obligation_id: str,
        principal: Principal,
        native_session_token: str | None,
    ) -> ResearchLead:
        session = self._research.load(
            session_id,
            tenant=self._tenant(principal),
            principal=str(principal.user_id),
        )
        obligation = ResearchManager.obligation(session, obligation_id)
        if obligation.state != ObligationState.VERIFIED:
            raise ResearchExplorationError(
                "P15_VERIFIED_RESEARCH_OBLIGATION_REQUIRED",
                "P15 exploration consumes a VERIFIED P14 Research obligation",
            )
        try:
            link = self._research.verified_link(
                session_id=session_id,
                obligation_id=obligation_id,
            )
        except ResearchPersistenceError as exc:
            raise ResearchExplorationError(exc.code, exc.detail) from exc
        if link.execution_kind != "P14_BASE":
            raise ResearchExplorationError(
                "P15_BASE_OCCURRENCE_KIND_INVALID",
                "sealed P15 base lookup resolved a non-base occurrence",
            )
        return self._explore_verified_link(
            session=session,
            link=link,
            principal=principal,
            native_session_token=native_session_token,
            require_base_evidence_membership=True,
        )

    def explore_followup(
        self,
        *,
        session_id: str,
        execution_link_id: uuid.UUID,
        principal: Principal,
        native_session_token: str | None,
    ) -> ResearchLead:
        """Explore one explicit P17 follow-up without changing P15 base lookup."""

        session = self._research.load(
            session_id,
            tenant=self._tenant(principal),
            principal=str(principal.user_id),
        )
        link = self._research.execution_link(execution_link_id)
        if link.session_id != session.session_id:
            raise ResearchExplorationError(
                "P15_FOLLOWUP_SESSION_MISMATCH",
                "follow-up occurrence belongs to another Research session",
            )
        if (
            link.execution_kind != "P17_FOLLOWUP"
            or not link.reasoning_step_id
            or not link.investigation_task_id
        ):
            raise ResearchExplorationError(
                "P15_FOLLOWUP_LINEAGE_INVALID",
                "P17 follow-up must carry reasoning/task identity",
            )
        return self._explore_verified_link(
            session=session,
            link=link,
            principal=principal,
            native_session_token=native_session_token,
            require_base_evidence_membership=False,
        )
