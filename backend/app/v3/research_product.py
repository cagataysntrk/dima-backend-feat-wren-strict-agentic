"""P14 product Research/Ask orchestration.

This module owns durable Research lifecycle and exact native-occurrence correlation.
Metabot + Metabase own analytical cognition/execution; Dima owns Research,
lineage, receipt/Evidence correlation, and durable resume.
"""
from __future__ import annotations

import hashlib
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.v3.research_contracts import ResearchBrief, ResearchBriefStatus
from app.v3.authority import AcceptedResearchAuthority
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact
from app.v3.research import (
    ObligationState,
    ResearchManager,
    ResearchSession,
)
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from app.v3.substrate.metabase.native_engine import (
    NativeEngineBridge,
    NativeEngineBridgeError,
)
from app.v3.substrate.metabase.native_models import NativeEngineRequest
from control_plane.authorize import Principal


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchProductError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ResearchProductRuntimeUnavailable(ResearchProductError):
    pass


class ResearchMaterialLimitation(ResearchProductError):
    """One material execution failed closed without poisoning independent obligations."""


class ResearchMaterialOutcome(Frozen):
    native_conversation_id: UUID
    native_query_id: str = Field(min_length=1)
    attestation_id: str | None = None
    receipt: DimaQueryReceipt
    evidence: EvidenceArtifact
    satisfies_obligation: bool = True


class NativeBridgeFactory(Protocol):
    def open(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        native_session_token: str | None,
    ) -> AbstractContextManager[NativeEngineBridge]: ...


class ResearchMaterialExecutor(Protocol):
    def execute(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        obligation_id: str,
        bridge: NativeEngineBridge,
        native_conversation_id: UUID,
        native_query_id: str,
        native_query: dict[str, Any],
        query_fingerprint: str,
        execution_link_id: UUID,
    ) -> ResearchMaterialOutcome: ...


class ResearchAskResponse(Frozen):
    status: str = "research"
    stage: str = "p14_native_research"
    research_session_id: str
    research_session_revision: int
    obligation_id: str | None = None
    obligation_state: str | None = None
    stopping_status: str
    native_conversation_id: UUID | None = None
    native_query_id: str | None = None
    receipt_id: str | None = None
    evidence_id: str | None = None
    limitation_code: str | None = None
    limitation_detail: str | None = None
    resumed_exact_occurrence: bool = False


class NativeResearchOccurrenceResult(Frozen):
    execution_link_id: UUID
    native_query_id: str = Field(min_length=1)
    outcome: ResearchMaterialOutcome
    resumed_exact_occurrence: bool = False


class NativeResearchOccurrenceRunner:
    """Single native Metabot -> exact query -> dataset/receipt/Evidence occurrence path."""

    def __init__(
        self,
        *,
        store: ResearchSessionStore,
        bridge_factory: NativeBridgeFactory,
        material_executor: ResearchMaterialExecutor,
    ) -> None:
        self._store = store
        self._bridges = bridge_factory
        self._materials = material_executor

    def execute(
        self,
        *,
        session: ResearchSession,
        principal: Principal,
        obligation_id: str,
        link,
        request: NativeEngineRequest | None,
        native_session_token: str | None,
    ) -> NativeResearchOccurrenceResult:
        resumed_exact = False
        with self._bridges.open(
            principal=principal,
            session=session,
            native_session_token=native_session_token,
        ) as bridge:
            if link.native_query_id is None:
                if request is None:
                    raise ResearchPersistenceError(
                        "P14_NATIVE_DELEGATION_OUTCOME_UNKNOWN",
                        (
                            "a native turn was durably delegated but no query occurrence "
                            "was captured; unknown prior cognition is not replayed"
                        ),
                    )
                observation = bridge.invoke(request)
                produced = bridge.capture_produced_query(observation)
                link = self._store.mark_candidate(
                    link.id,
                    native_query_id=produced.native_query_id,
                    native_query=produced.query,
                    query_fingerprint=produced.query_fingerprint,
                )
                native_query = produced.query
                query_fingerprint = produced.query_fingerprint
            else:
                native_query, query_fingerprint = self._store.captured_query(
                    link
                )
                resumed_exact = True

            native_query_id = link.native_query_id
            assert native_query_id is not None
            outcome = self._materials.execute(
                principal=principal,
                session=session,
                obligation_id=obligation_id,
                bridge=bridge,
                native_conversation_id=link.native_conversation_id,
                native_query_id=native_query_id,
                native_query=native_query,
                query_fingerprint=query_fingerprint,
                execution_link_id=link.id,
            )

        if outcome.native_conversation_id != link.native_conversation_id:
            raise ResearchProductError(
                "P14_NATIVE_CONVERSATION_CORRELATION_MISMATCH",
                "material execution returned a different native conversation",
            )
        if outcome.native_query_id != native_query_id:
            raise ResearchProductError(
                "P14_NATIVE_QUERY_CORRELATION_MISMATCH",
                "material execution returned a different captured native occurrence",
            )
        return NativeResearchOccurrenceResult(
            execution_link_id=link.id,
            native_query_id=native_query_id,
            outcome=outcome,
            resumed_exact_occurrence=resumed_exact,
        )


class ResearchBriefAuthoritySealer:
    """Seal already-grounded ResearchBrief identity; never re-interpret user language."""

    @staticmethod
    def seal(
        *,
        brief: ResearchBrief,
        request_ref: str,
        source_message_hash: str,
    ) -> AcceptedResearchAuthority:
        if brief.status != ResearchBriefStatus.READY_FOR_RESEARCH:
            raise ResearchProductError(
                "P14_RESEARCH_BRIEF_NOT_READY",
                "only a fully resolved ResearchBrief can enter product Research",
            )
        if brief.blocking_goal_ids or any(
            item.status.value != "RESOLVED" or item.unresolved
            for item in brief.questions
        ):
            raise ResearchProductError(
                "P14_RESEARCH_BRIEF_BLOCKED",
                "blocked Research goals cannot be sealed",
            )
        question_ids = tuple(item.goal_id for item in brief.questions)
        deliverable_ids = tuple(item.requirement_id for item in brief.deliverables)
        expected = (*question_ids, *deliverable_ids)
        if not question_ids or brief.must_requirement_ids != expected:
            raise ResearchProductError(
                "P14_RESEARCH_BRIEF_OBLIGATION_DRIFT",
                "ResearchBrief MUST obligations differ from its resolved questions/deliverables",
            )
        if len(expected) != len(set(expected)):
            raise ResearchProductError(
                "P14_RESEARCH_BRIEF_OBLIGATION_DUPLICATE",
                "ResearchBrief contains duplicate obligation identifiers",
            )
        raw = "\x1f".join(
            (request_ref, source_message_hash, brief.brief_id, brief.context_version)
        )
        contract_id = "atc_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
        return AcceptedResearchAuthority(
            contract_id=contract_id,
            lineage_id="atl_"
            + hashlib.sha256(request_ref.encode("utf-8")).hexdigest()[:20],
            version=1,
            turn_id=f"research:{brief.brief_id}",
            request_ref=request_ref,
            source_message_hash=source_message_hash,
            accepted_attempt_id=brief.brief_id,
            model_role="research-brief-product",
            obligation_ids=expected,
            context_version=brief.context_version,
            accepted_at_iso=datetime.now(timezone.utc).isoformat(),
        )


class ResearchAskOrchestrator:
    """Durable product boundary. Research owns WHAT; native Metabot owns HOW."""

    def __init__(
        self,
        *,
        store: ResearchSessionStore,
        bridge_factory: NativeBridgeFactory | None = None,
        material_executor: ResearchMaterialExecutor | None = None,
    ) -> None:
        self._store = store
        self._bridge_factory = bridge_factory
        self._material_executor = material_executor

    def configure_native_runtime(
        self,
        *,
        bridge_factory: NativeBridgeFactory,
        material_executor: ResearchMaterialExecutor,
    ) -> None:
        """Install principal-scoped native Metabot/Metabase runtime; never mint auth here."""
        self._bridge_factory = bridge_factory
        self._material_executor = material_executor

    @staticmethod
    def tenant_binding_for(principal: Principal) -> str:
        if principal.tenant_id is not None:
            return f"id:{principal.tenant_id}"
        if principal.tenant_slug:
            return f"slug:{principal.tenant_slug}"
        raise ResearchProductError(
            "P14_RESEARCH_TENANT_REQUIRED",
            "Research requires an explicit tenant binding",
        )

    @staticmethod
    def _principal_subject(principal: Principal) -> str:
        if not str(principal.user_id).strip():
            raise ResearchProductError(
                "P14_RESEARCH_PRINCIPAL_REQUIRED",
                "Research requires a principal subject",
            )
        return str(principal.user_id)

    @staticmethod
    def _session_id(authority_id: str, tenant: str, principal: str) -> str:
        raw = f"{authority_id}\x1f{tenant}\x1f{principal}"
        return "rs_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def start_from_brief(
        self,
        *,
        brief: ResearchBrief,
        request_ref: str,
        source_message_hash: str,
        principal: Principal,
    ) -> ResearchSession:
        authority = ResearchBriefAuthoritySealer.seal(
            brief=brief,
            request_ref=request_ref,
            source_message_hash=source_message_hash,
        )
        tenant = self.tenant_binding_for(principal)
        subject = self._principal_subject(principal)
        objectives = {item.goal_id: item.source_text for item in brief.questions}
        objectives.update(
            {item.requirement_id: item.source_text for item in brief.deliverables}
        )
        session = ResearchManager.start(
            authority=authority,
            objective=brief.objective,
            obligation_objectives=objectives,
            tenant_binding=tenant,
            principal_subject=subject,
            session_id=self._session_id(authority.contract_id, tenant, subject),
            accepted_brief=brief,
        )
        return self._store.create(
            session,
            delegatable_ids=tuple(item.goal_id for item in brief.questions),
        )

    def resume_state(
        self,
        *,
        session_id: str,
        principal: Principal,
    ) -> ResearchSession:
        return self._store.load(
            session_id,
            tenant=self.tenant_binding_for(principal),
            principal=self._principal_subject(principal),
        )

    @staticmethod
    def _response(
        session: ResearchSession,
        *,
        obligation_id: str | None = None,
        native_query_id: str | None = None,
        receipt_id: str | None = None,
        evidence_id: str | None = None,
        limitation_code: str | None = None,
        limitation_detail: str | None = None,
        resumed_exact_occurrence: bool = False,
    ) -> ResearchAskResponse:
        obligation = (
            ResearchManager.obligation(session, obligation_id)
            if obligation_id is not None
            else None
        )
        conversation = session.native_conversation
        return ResearchAskResponse(
            research_session_id=session.session_id,
            research_session_revision=session.revision,
            obligation_id=obligation_id,
            obligation_state=obligation.state.value if obligation else None,
            stopping_status=session.stopping.status.value,
            native_conversation_id=(
                conversation.conversation_id if conversation else None
            ),
            native_query_id=native_query_id,
            receipt_id=receipt_id,
            evidence_id=evidence_id,
            limitation_code=limitation_code,
            limitation_detail=limitation_detail,
            resumed_exact_occurrence=resumed_exact_occurrence,
        )

    @staticmethod
    def accepted_material_question(
        session: ResearchSession,
        obligation_id: str,
    ):
        brief = session.accepted_brief
        if brief is None:
            raise ResearchProductError(
                "P14_ACCEPTED_RESEARCH_CONTEXT_MISSING",
                "product Research session has no persisted accepted ResearchBrief",
            )
        matches = tuple(
            item for item in brief.questions if item.goal_id == obligation_id
        )
        if len(matches) != 1:
            raise ResearchProductError(
                "P14_ACCEPTED_RESEARCH_OBLIGATION_MISMATCH",
                "accepted ResearchBrief does not contain exactly one matching question",
            )
        return matches[0]

    def _runtime(self) -> tuple[NativeBridgeFactory, ResearchMaterialExecutor]:
        if self._bridge_factory is None or self._material_executor is None:
            raise ResearchProductRuntimeUnavailable(
                "P14_NATIVE_RUNTIME_NOT_CONFIGURED",
                "principal-scoped native Metabot/Metabase runtime is not installed",
            )
        return self._bridge_factory, self._material_executor

    def _select_obligation(
        self,
        session: ResearchSession,
        delegatable_ids: tuple[str, ...],
        requested: str | None,
    ) -> str:
        allowed = set(delegatable_ids)
        if requested is not None:
            if requested not in allowed:
                raise ResearchProductError(
                    "P14_OBLIGATION_NOT_DELEGATABLE",
                    "requested obligation is not a native analytical Research question",
                )
            item = ResearchManager.obligation(session, requested)
            if item.state in ResearchManager.terminal:
                raise ResearchProductError(
                    "P14_OBLIGATION_TERMINAL",
                    requested,
                )
            return requested
        for obligation_id in delegatable_ids:
            item = ResearchManager.obligation(session, obligation_id)
            if item.state not in ResearchManager.terminal:
                return obligation_id
        raise ResearchProductError(
            "P14_NO_OPEN_NATIVE_OBLIGATION",
            "Research has no open native analytical obligation",
        )

    def _limit(
        self,
        *,
        session: ResearchSession,
        obligation_id: str,
        code: str,
        detail: str,
        link_id=None,
    ) -> ResearchAskResponse:
        prior_revision = session.revision
        updated = ResearchManager.record_limitation(
            session,
            obligation_id=obligation_id,
            code=code,
            detail=detail,
        )
        self._store.save(updated, expected_revision=prior_revision)
        if link_id is not None:
            self._store.mark_limited(link_id, code=code, detail=detail)
        return self._response(
            updated,
            obligation_id=obligation_id,
            limitation_code=code,
            limitation_detail=detail,
        )

    def run_next(
        self,
        *,
        session_id: str,
        principal: Principal,
        obligation_id: str | None = None,
        native_session_token: str | None = None,
    ) -> ResearchAskResponse:
        bridge_factory, material_executor = self._runtime()
        tenant = self.tenant_binding_for(principal)
        subject = self._principal_subject(principal)
        session = self._store.load(session_id, tenant=tenant, principal=subject)
        delegatable = self._store.delegatable_ids(
            session_id,
            tenant=tenant,
            principal=subject,
        )
        selected = self._select_obligation(session, delegatable, obligation_id)
        self.accepted_material_question(session, selected)
        pending = self._store.pending_link(
            session_id=session.session_id,
            obligation_id=selected,
        )
        resumed_exact = False

        item = ResearchManager.obligation(session, selected)
        if pending is None and item.state == ObligationState.DELEGATED:
            return self._limit(
                session=session,
                obligation_id=selected,
                code="P14_NATIVE_CORRELATION_MISSING",
                detail=(
                    "Research state says DELEGATED but its durable native correlation "
                    "record is missing; the native turn is not replayed"
                ),
            )

        if pending is not None and pending.native_query_id is None:
            return self._limit(
                session=session,
                obligation_id=selected,
                code="P14_NATIVE_DELEGATION_OUTCOME_UNKNOWN",
                detail=(
                    "a native turn was durably delegated but no query occurrence was "
                    "successfully captured; unknown prior cognition is not replayed"
                ),
                link_id=pending.id,
            )

        prepared = None
        if pending is None:
            before = session.revision
            prepared = ResearchManager.prepare_native_delegation(
                session,
                obligation_id=selected,
            )
            session = self._store.save(
                prepared.session,
                expected_revision=before,
            )
            conversation = session.native_conversation
            assert conversation is not None
            pending = self._store.begin_delegation(
                session=session,
                obligation_id=selected,
                dima_request_id=prepared.request.dima_request_id,
                dima_trace_id=prepared.request.dima_trace_id,
                native_conversation_id=conversation.conversation_id,
            )

        runner = NativeResearchOccurrenceRunner(
            store=self._store,
            bridge_factory=bridge_factory,
            material_executor=material_executor,
        )
        try:
            occurrence = runner.execute(
                session=session,
                principal=principal,
                obligation_id=selected,
                link=pending,
                request=(prepared.request if prepared is not None else None),
                native_session_token=native_session_token,
            )
        except ResearchMaterialLimitation as exc:
            return self._limit(
                session=session,
                obligation_id=selected,
                code=exc.code,
                detail=exc.detail,
                link_id=pending.id,
            )
        except NativeEngineBridgeError as exc:
            return self._limit(
                session=session,
                obligation_id=selected,
                code="P14_NATIVE_TRANSPORT_FAILED",
                detail=str(exc),
                link_id=pending.id,
            )
        except ResearchPersistenceError as exc:
            return self._limit(
                session=session,
                obligation_id=selected,
                code=exc.code,
                detail=exc.detail,
                link_id=pending.id,
            )

        pending = self._store.execution_link(
            occurrence.execution_link_id
        )
        outcome = occurrence.outcome
        native_query_id = occurrence.native_query_id
        resumed_exact = occurrence.resumed_exact_occurrence

        before = session.revision
        updated = ResearchManager.admit_receipted_evidence(
            session,
            obligation_id=selected,
            receipt=outcome.receipt,
            evidence=outcome.evidence,
            satisfies_obligation=outcome.satisfies_obligation,
        )
        self._store.save(updated, expected_revision=before)
        self._store.mark_verified(
            pending.id,
            receipt_id=outcome.receipt.receipt_id,
            evidence_id=outcome.evidence.artifact_id,
        )
        return self._response(
            updated,
            obligation_id=selected,
            native_query_id=native_query_id,
            receipt_id=outcome.receipt.receipt_id,
            evidence_id=outcome.evidence.artifact_id,
            resumed_exact_occurrence=resumed_exact,
        )
