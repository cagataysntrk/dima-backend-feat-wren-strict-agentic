"""Durable P14 Research checkpoints and native-occurrence correlation.

This store persists Dima-owned Research state only. It does not own analytical
semantics, Metabase permissions, execution authorization, QueryReceipt sealing,
or Evidence promotion.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import update
from sqlmodel import Session, select

from app.v3.research import ResearchManager, ResearchSession
from control_plane.db import engine as control_plane_engine
from control_plane.models import ResearchExecutionLink, ResearchSessionRecord


class ResearchPersistenceError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _checkpoint_payload(session: ResearchSession) -> tuple[str, str]:
    checkpoint = ResearchManager.checkpoint(session)
    return checkpoint.model_dump_json(), checkpoint.fingerprint


def _query_payload(query: dict) -> tuple[str, str]:
    try:
        raw = json.dumps(
            query,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ResearchPersistenceError(
            "P14_NATIVE_QUERY_NOT_CANONICAL_JSON",
            "captured native query is not deterministic JSON",
        ) from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ResearchSessionStore:
    """Single durable store for P14 state and native correlation."""

    def __init__(self, db_engine=None) -> None:
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _scope(record: ResearchSessionRecord, tenant: str, principal: str) -> None:
        if record.tenant_binding != tenant or record.principal_subject != principal:
            raise ResearchPersistenceError(
                "P14_RESEARCH_SESSION_NOT_FOUND",
                "Research session is absent from the current tenant/principal scope",
            )

    def create(
        self,
        session: ResearchSession,
        *,
        delegatable_ids: tuple[str, ...],
    ) -> ResearchSession:
        known = {item.obligation_id for item in session.obligations}
        if (
            len(delegatable_ids) != len(set(delegatable_ids))
            or not set(delegatable_ids).issubset(known)
        ):
            raise ResearchPersistenceError(
                "P14_RESEARCH_DELEGATION_SET_INVALID",
                "delegatable obligations must be unique members of the Research session",
            )
        payload, fingerprint = _checkpoint_payload(session)
        now = _now()
        with Session(self._engine) as db:
            existing = db.get(ResearchSessionRecord, session.session_id)
            if existing is not None:
                self._scope(existing, session.tenant_binding, session.principal_subject)
                restored = ResearchManager.restore_checkpoint(existing.checkpoint_json)
                if restored.authority_id != session.authority_id:
                    raise ResearchPersistenceError(
                        "P14_RESEARCH_SESSION_ID_CONFLICT",
                        "existing Research session belongs to another accepted authority",
                    )
                return restored
            db.add(
                ResearchSessionRecord(
                    session_id=session.session_id,
                    tenant_binding=session.tenant_binding,
                    principal_subject=session.principal_subject,
                    authority_id=session.authority_id,
                    context_version=session.context_version,
                    revision=session.revision,
                    checkpoint_json=payload,
                    checkpoint_fingerprint=fingerprint,
                    delegatable_ids_json=json.dumps(list(delegatable_ids)),
                    created_at=now,
                    updated_at=now,
                )
            )
            db.commit()
        return session

    def load(self, session_id: str, *, tenant: str, principal: str) -> ResearchSession:
        with Session(self._engine) as db:
            record = db.get(ResearchSessionRecord, session_id)
            if record is None:
                raise ResearchPersistenceError(
                    "P14_RESEARCH_SESSION_NOT_FOUND",
                    "Research session does not exist",
                )
            self._scope(record, tenant, principal)
            session = ResearchManager.restore_checkpoint(record.checkpoint_json)
            if session.fingerprint != record.checkpoint_fingerprint:
                raise ResearchPersistenceError(
                    "P14_RESEARCH_CHECKPOINT_FINGERPRINT_MISMATCH",
                    "persisted Research checkpoint does not match its fingerprint",
                )
            if session.revision != record.revision:
                raise ResearchPersistenceError(
                    "P14_RESEARCH_CHECKPOINT_REVISION_MISMATCH",
                    "persisted Research revision metadata drifted",
                )
            return session

    def delegatable_ids(
        self,
        session_id: str,
        *,
        tenant: str,
        principal: str,
    ) -> tuple[str, ...]:
        with Session(self._engine) as db:
            record = db.get(ResearchSessionRecord, session_id)
            if record is None:
                raise ResearchPersistenceError(
                    "P14_RESEARCH_SESSION_NOT_FOUND",
                    "Research session does not exist",
                )
            self._scope(record, tenant, principal)
            values = json.loads(record.delegatable_ids_json)
            if not isinstance(values, list) or any(
                not isinstance(item, str) for item in values
            ):
                raise ResearchPersistenceError(
                    "P14_RESEARCH_DELEGATION_SET_INVALID",
                    "persisted delegatable obligation set is invalid",
                )
            return tuple(values)

    def save(self, session: ResearchSession, *, expected_revision: int) -> ResearchSession:
        if session.revision != expected_revision + 1:
            raise ResearchPersistenceError(
                "P14_RESEARCH_REVISION_STEP_INVALID",
                "Research persistence accepts exactly one state transition per save",
            )
        payload, fingerprint = _checkpoint_payload(session)
        with Session(self._engine) as db:
            statement = (
                update(ResearchSessionRecord)
                .where(ResearchSessionRecord.session_id == session.session_id)
                .where(ResearchSessionRecord.tenant_binding == session.tenant_binding)
                .where(ResearchSessionRecord.principal_subject == session.principal_subject)
                .where(ResearchSessionRecord.revision == expected_revision)
                .values(
                    revision=session.revision,
                    checkpoint_json=payload,
                    checkpoint_fingerprint=fingerprint,
                    context_version=session.context_version,
                    updated_at=_now(),
                )
            )
            result = db.exec(statement)
            if result.rowcount != 1:
                db.rollback()
                raise ResearchPersistenceError(
                    "P14_RESEARCH_REVISION_CONFLICT",
                    "Research session changed concurrently or left the current scope",
                )
            db.commit()
        return session

    def begin_delegation(
        self,
        *,
        session: ResearchSession,
        obligation_id: str,
        dima_request_id: str,
        dima_trace_id: str,
        native_conversation_id: uuid.UUID,
    ) -> ResearchExecutionLink:
        now = _now()
        link = ResearchExecutionLink(
            session_id=session.session_id,
            obligation_id=obligation_id,
            dima_request_id=dima_request_id,
            dima_trace_id=dima_trace_id,
            native_conversation_id=native_conversation_id,
            status="DELEGATED",
            created_at=now,
            updated_at=now,
        )
        with Session(self._engine) as db:
            existing = db.exec(
                select(ResearchExecutionLink).where(
                    ResearchExecutionLink.dima_request_id == dima_request_id
                )
            ).first()
            if existing is not None:
                return existing
            db.add(link)
            db.commit()
            db.refresh(link)
            return link

    def pending_link(
        self,
        *,
        session_id: str,
        obligation_id: str,
    ) -> ResearchExecutionLink | None:
        with Session(self._engine) as db:
            return db.exec(
                select(ResearchExecutionLink)
                .where(ResearchExecutionLink.session_id == session_id)
                .where(ResearchExecutionLink.obligation_id == obligation_id)
                .where(
                    ResearchExecutionLink.status.in_(
                        ("DELEGATED", "CANDIDATE_CAPTURED")
                    )
                )
                .order_by(ResearchExecutionLink.created_at.desc())
            ).first()

    def _update_link(self, link_id: uuid.UUID, **values) -> ResearchExecutionLink:
        values["updated_at"] = _now()
        with Session(self._engine) as db:
            link = db.get(ResearchExecutionLink, link_id)
            if link is None:
                raise ResearchPersistenceError(
                    "P14_RESEARCH_EXECUTION_LINK_NOT_FOUND",
                    str(link_id),
                )
            for key, value in values.items():
                setattr(link, key, value)
            db.add(link)
            db.commit()
            db.refresh(link)
            return link

    def mark_candidate(
        self,
        link_id: uuid.UUID,
        *,
        native_query_id: str,
        native_query: dict,
        query_fingerprint: str,
    ) -> ResearchExecutionLink:
        raw, observed = _query_payload(native_query)
        if observed != query_fingerprint:
            raise ResearchPersistenceError(
                "P14_NATIVE_QUERY_FINGERPRINT_MISMATCH",
                "captured query payload differs from its claimed fingerprint",
            )
        return self._update_link(
            link_id,
            native_query_id=native_query_id,
            native_query_json=raw,
            native_query_fingerprint=query_fingerprint,
            status="CANDIDATE_CAPTURED",
        )

    @staticmethod
    def captured_query(link: ResearchExecutionLink) -> tuple[dict, str]:
        if not link.native_query_json or not link.native_query_fingerprint:
            raise ResearchPersistenceError(
                "P14_NATIVE_QUERY_PAYLOAD_MISSING",
                "captured native occurrence has no durable executable query payload",
            )
        try:
            query = json.loads(link.native_query_json)
        except json.JSONDecodeError as exc:
            raise ResearchPersistenceError(
                "P14_NATIVE_QUERY_PAYLOAD_INVALID",
                "persisted native query payload is invalid JSON",
            ) from exc
        if not isinstance(query, dict):
            raise ResearchPersistenceError(
                "P14_NATIVE_QUERY_PAYLOAD_INVALID",
                "persisted native query payload is not an object",
            )
        _, observed = _query_payload(query)
        if observed != link.native_query_fingerprint:
            raise ResearchPersistenceError(
                "P14_NATIVE_QUERY_FINGERPRINT_MISMATCH",
                "persisted native query payload changed after capture",
            )
        return query, observed

    def mark_verified(
        self,
        link_id: uuid.UUID,
        *,
        receipt_id: str,
        evidence_id: str,
        native_subject_ref: str,
        runtime_identity: dict,
        result_hash: str,
        executed_at: datetime,
        attestation_id: str | None = None,
    ) -> ResearchExecutionLink:
        runtime_json = json.dumps(
            runtime_identity,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
        return self._update_link(
            link_id,
            attestation_id=attestation_id,
            receipt_id=receipt_id,
            evidence_id=evidence_id,
            native_subject_ref=native_subject_ref,
            runtime_identity_json=runtime_json,
            result_hash=result_hash,
            executed_at=executed_at,
            status="VERIFIED",
        )

    def mark_limited(
        self,
        link_id: uuid.UUID,
        *,
        code: str,
        detail: str,
    ) -> ResearchExecutionLink:
        return self._update_link(
            link_id,
            limitation_code=code,
            limitation_detail=detail,
            status="LIMITED",
        )
