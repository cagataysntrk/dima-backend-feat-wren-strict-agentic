"""P14 product Research/Ask orchestration.

This module owns durable Research lifecycle and exact native-occurrence correlation.
Metabot + Metabase own analytical cognition/execution; Dima owns Research,
lineage, receipt/Evidence correlation, and durable resume.
"""
from __future__ import annotations

import hashlib
import json
import time
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytical_request_contract import AnalyticalRequestContract
from app.v3.research_contracts import ResearchBrief, ResearchBriefStatus
from app.v3.authority import AcceptedResearchAuthority
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact
from app.v3.research import (
    ObligationState,
    ResearchManager,
    ResearchSession,
)
from app.v3.research_analytical_scope import (
    ResearchAnalyticalScopeError,
    analytical_scope_contract,
)
from app.v3.research_scope_patch import scope_fingerprint
from app.v3.research_material_repair import (
    MaterialRepairDisposition,
    decide_material_repair,
    material_repair_feedback,
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
    def __init__(
        self,
        code: str,
        detail: str,
        *,
        last_valid_boundary: str | None = None,
        first_invalid_boundary: str | None = None,
        expected_fingerprint: str | None = None,
        observed_fingerprint: str | None = None,
        scope_fingerprint: str | None = None,
        material_fingerprint: str | None = None,
        expected_semantic_shape: dict[str, Any] | None = None,
        observed_semantic_shape: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.last_valid_boundary = last_valid_boundary
        self.first_invalid_boundary = first_invalid_boundary
        self.expected_fingerprint = expected_fingerprint
        self.observed_fingerprint = observed_fingerprint
        self.scope_fingerprint = scope_fingerprint
        self.material_fingerprint = material_fingerprint
        self.expected_semantic_shape = expected_semantic_shape
        self.observed_semantic_shape = observed_semantic_shape


class ResearchProductRuntimeUnavailable(ResearchProductError):
    pass


class ResearchMaterialLimitation(ResearchProductError):
    """One material execution failed closed without poisoning independent obligations."""


class ResearchMaterialObservationUnavailable(ResearchMaterialLimitation):
    """Pre-execution occurrence readiness/observation is temporarily unavailable."""


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
        analytical_scope: AnalyticalRequestContract | None = None,
        consumer_obligation_ids: tuple[str, ...] | None = None,
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
    last_valid_boundary: str | None = None
    first_invalid_boundary: str | None = None
    expected_fingerprint: str | None = None
    observed_fingerprint: str | None = None
    scope_fingerprint: str | None = None
    material_fingerprint: str | None = None
    expected_semantic_shape: dict[str, Any] | None = None
    observed_semantic_shape: dict[str, Any] | None = None
    resumed_exact_occurrence: bool = False


class NativeResearchOccurrenceResult(Frozen):
    execution_link_id: UUID
    native_query_id: str = Field(min_length=1)
    outcome: ResearchMaterialOutcome
    resumed_exact_occurrence: bool = False


class NativeResearchOccurrenceRunner:
    """Single Metabot capture -> observe -> exact execute -> Evidence occurrence path."""

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
        analytical_scope: AnalyticalRequestContract | None = None,
        consumer_obligation_ids: tuple[str, ...] | None = None,
        repair_parent_link_id: UUID | None = None,
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
                enrich_request = getattr(
                    self._materials,
                    "enrich_native_request",
                    None,
                )
                if callable(enrich_request):
                    request = enrich_request(
                        principal=principal,
                        session=session,
                        obligation_id=obligation_id,
                        request=request,
                        analytical_scope=analytical_scope,
                    )
                if link.execution_kind == "P17_FOLLOWUP":
                    if request.state or request.history is not None:
                        raise ResearchPersistenceError(
                            "P17_NATIVE_CONTINUATION_CALLER_FORBIDDEN",
                            (
                                "P17 follow-up state/history are Dima-owned "
                                "source-backed continuation provenance"
                            ),
                        )
                    continuation_state, _ = (
                        self._store.latest_verified_agent_state(
                            session_id=session.session_id,
                            obligation_id=obligation_id,
                            native_conversation_id=link.native_conversation_id,
                        )
                    )
                    continuation_history = bridge.conversation_history(
                        link.native_conversation_id
                    )
                    if not continuation_history:
                        raise ResearchPersistenceError(
                            "P17_NATIVE_CONTINUATION_HISTORY_REQUIRED",
                            (
                                "verified parent native conversation has no "
                                "source-backed cognition history"
                            ),
                        )
                    request = request.model_copy(
                        update={
                            "state": continuation_state,
                            "history": continuation_history,
                        }
                    )
                elif link.execution_kind == "P14_REPAIR":
                    if request.state or request.history is not None:
                        raise ResearchPersistenceError(
                            "P14_REPAIR_CONTINUATION_CALLER_FORBIDDEN",
                            (
                                "P14 repair state/history are Dima-owned "
                                "source-backed continuation provenance"
                            ),
                        )
                    if repair_parent_link_id is None:
                        raise ResearchPersistenceError(
                            "P14_REPAIR_PARENT_REQUIRED",
                            "material repair requires the failed parent occurrence",
                        )
                    parent = self._store.execution_link(repair_parent_link_id)
                    if (
                        parent.session_id != session.session_id
                        or parent.obligation_id != obligation_id
                        or parent.native_conversation_id
                        != link.native_conversation_id
                        or parent.status != "LIMITED"
                    ):
                        raise ResearchPersistenceError(
                            "P14_REPAIR_PARENT_SCOPE_INVALID",
                            "repair parent must be the same limited Research occurrence",
                        )
                    captured = self._store.captured_agent_state(parent)
                    if captured is None:
                        raise ResearchPersistenceError(
                            "P14_REPAIR_PARENT_STATE_REQUIRED",
                            "limited parent occurrence has no durable Metabot state",
                        )
                    continuation_state, _ = captured
                    continuation_history = bridge.conversation_history(
                        link.native_conversation_id
                    )
                    if not continuation_history:
                        raise ResearchPersistenceError(
                            "P14_REPAIR_CONTINUATION_HISTORY_REQUIRED",
                            (
                                "limited parent native conversation has no "
                                "source-backed cognition history"
                            ),
                        )
                    request = request.model_copy(
                        update={
                            "state": continuation_state,
                            "history": continuation_history,
                        }
                    )
                observation = bridge.invoke(request)
                produced = bridge.capture_produced_query(
                    observation,
                    prior_state=request.state,
                )
                if link.execution_kind == "P14_REPAIR":
                    assert repair_parent_link_id is not None
                    parent = self._store.execution_link(repair_parent_link_id)
                    if (
                        parent.native_query_fingerprint is not None
                        and produced.query_fingerprint
                        == parent.native_query_fingerprint
                    ):
                        raise ResearchMaterialLimitation(
                            "P14_REPAIR_REPEATED_NATIVE_QUERY",
                            (
                                "Metabot repair reproduced the exact failed "
                                "native query fingerprint"
                            ),
                            last_valid_boundary="dima.native.generate",
                            first_invalid_boundary="dima.native.repair",
                        )
                link = self._store.mark_candidate(
                    link.id,
                    native_query_id=produced.native_query_id,
                    native_query=produced.query,
                    query_fingerprint=produced.query_fingerprint,
                    native_agent_state=observation.final_state,
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
            material_kwargs = {
                "principal": principal,
                "session": session,
                "obligation_id": obligation_id,
                "bridge": bridge,
                "native_conversation_id": link.native_conversation_id,
                "native_query_id": native_query_id,
                "native_query": native_query,
                "query_fingerprint": query_fingerprint,
                "execution_link_id": link.id,
            }
            if analytical_scope is not None:
                material_kwargs["analytical_scope"] = analytical_scope
            if (
                consumer_obligation_ids is not None
                and len(consumer_obligation_ids) > 1
            ):
                material_kwargs["consumer_obligation_ids"] = consumer_obligation_ids
            outcome = self._materials.execute(**material_kwargs)

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
        prior_session: ResearchSession | None = None,
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
        scope_version = brief.scope.scope_version
        if prior_session is None:
            if (
                scope_version.ordinal != 1
                or scope_version.parent_version_id is not None
            ):
                raise ResearchProductError(
                    "P14_SCOPE_LINEAGE_REQUIRED",
                    "mutated scope requires the exact prior Research session",
                )
            lineage_id = (
                "atl_"
                + hashlib.sha256(request_ref.encode("utf-8")).hexdigest()[:20]
            )
            authority_version = 1
            supersedes = None
        else:
            prior_brief = prior_session.accepted_brief
            if prior_brief is None:
                raise ResearchProductError(
                    "P14_PRIOR_ACCEPTED_BRIEF_MISSING",
                    "follow-up authority requires the prior immutable ResearchBrief",
                )
            prior_scope = prior_brief.scope.scope_version
            if (
                prior_session.context_version != brief.context_version
                or prior_brief.context_version != brief.context_version
            ):
                raise ResearchProductError(
                    "P14_SCOPE_CONTEXT_MISMATCH",
                    "follow-up scope cannot silently switch semantic context",
                )
            same_scope = (
                scope_version == prior_scope
                and scope_fingerprint(
                    brief.scope,
                    context_version=brief.context_version,
                )
                == scope_fingerprint(
                    prior_brief.scope,
                    context_version=prior_brief.context_version,
                )
            )
            scope_mutation = (
                scope_version.ordinal == prior_scope.ordinal + 1
                and scope_version.parent_version_id == prior_scope.version_id
            )
            if not same_scope and not scope_mutation:
                raise ResearchProductError(
                    "P14_SCOPE_VERSION_MISMATCH",
                    (
                        "follow-up must preserve the exact current ScopeVersion "
                        "or advance exactly one version for a real ScopeMutation"
                    ),
                )
            if same_scope and brief.scope.scope_version != prior_scope:
                raise ResearchProductError(
                    "P14_SCOPE_VERSION_MISMATCH",
                    "same-scope continuation changed ScopeVersion identity",
                )
            lineage_id = prior_session.lineage_id
            authority_version = prior_session.authority_revision + 1
            supersedes = prior_session.authority_id

        raw = "\x1f".join(
            (
                request_ref,
                source_message_hash,
                brief.brief_id,
                brief.context_version,
                lineage_id,
                str(authority_version),
                supersedes or "",
            )
        )
        contract_id = "atc_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
        return AcceptedResearchAuthority(
            contract_id=contract_id,
            lineage_id=lineage_id,
            version=authority_version,
            supersedes_contract_id=supersedes,
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
        prior_session_id: str | None = None,
        business_question: str | None = None,
    ) -> ResearchSession:
        tenant = self.tenant_binding_for(principal)
        subject = self._principal_subject(principal)
        prior_session = (
            self._store.assert_lineage_head(
                self._store.load(
                    prior_session_id,
                    tenant=tenant,
                    principal=subject,
                )
            )
            if prior_session_id is not None
            else None
        )
        authority = ResearchBriefAuthoritySealer.seal(
            brief=brief,
            request_ref=request_ref,
            source_message_hash=source_message_hash,
            prior_session=prior_session,
        )
        # P14 executes analytical Research questions only. Presentation deliverables
        # remain in the immutable accepted ResearchBrief and total USER_MUST authority
        # for product-level fulfillment after the relevant owner (for example P20) seals.
        descriptive_question = (business_question or "").strip()
        objectives = {
            item.goal_id: (
                descriptive_question
                if descriptive_question
                else item.source_text
            )
            for item in brief.questions
        }
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

    def current_scope_state(
        self,
        *,
        session_id: str,
        principal: Principal,
    ) -> ResearchSession:
        session = self.resume_state(
            session_id=session_id,
            principal=principal,
        )
        return self._store.assert_lineage_head(session)

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
        last_valid_boundary: str | None = None,
        first_invalid_boundary: str | None = None,
        expected_fingerprint: str | None = None,
        observed_fingerprint: str | None = None,
        scope_fingerprint: str | None = None,
        material_fingerprint: str | None = None,
        expected_semantic_shape: dict[str, Any] | None = None,
        observed_semantic_shape: dict[str, Any] | None = None,
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
            last_valid_boundary=last_valid_boundary,
            first_invalid_boundary=first_invalid_boundary,
            expected_fingerprint=expected_fingerprint,
            observed_fingerprint=observed_fingerprint,
            scope_fingerprint=scope_fingerprint,
            material_fingerprint=material_fingerprint,
            expected_semantic_shape=expected_semantic_shape,
            observed_semantic_shape=observed_semantic_shape,
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

    def _prepare_material_repair(
        self,
        *,
        session: ResearchSession,
        obligation_id: str,
        parent_link,
        failure: ResearchMaterialLimitation,
        analytical_scope: AnalyticalRequestContract | None = None,
    ):
        """Open at most two P14-owned repair occurrences for material-shape misses.

        The failed exact occurrence stays durable and is never overwritten.
        Repair preserves the accepted analytical contract and delegates query
        regeneration to the same Metabot conversation.
        """

        attempts = self._store.material_repair_attempt_count(
            session_id=session.session_id,
            obligation_id=obligation_id,
        )
        expected_shape = failure.expected_semantic_shape
        if expected_shape is None and analytical_scope is not None:
            # Repair feedback is a deterministic projection of the already
            # accepted WHAT. It is not a second semantic judge and contains no
            # MBQL/SQL/query-shape prescription; Metabot still owns HOW.
            expected_shape = {
                "metric_refs": list(analytical_scope.metric_refs),
                "dimension_refs": list(analytical_scope.dimension_refs),
                "filters": [
                    item.model_dump(mode="json")
                    for item in analytical_scope.filters
                ],
                "period": (
                    analytical_scope.period.model_dump(mode="json")
                    if analytical_scope.period is not None
                    else None
                ),
                "comparison": (
                    analytical_scope.comparison.model_dump(mode="json")
                    if analytical_scope.comparison is not None
                    else None
                ),
                "temporal_observation": (
                    analytical_scope.temporal_observation.model_dump(mode="json")
                    if analytical_scope.temporal_observation is not None
                    else None
                ),
                "temporal_change_frame": (
                    analytical_scope.temporal_change_frame.model_dump(mode="json")
                    if analytical_scope.temporal_change_frame is not None
                    else None
                ),
                "ranking": (
                    analytical_scope.ranking.model_dump(mode="json")
                    if analytical_scope.ranking is not None
                    else None
                ),
                "grain_constraints": list(analytical_scope.grain_constraints),
            }
        decision = decide_material_repair(
            validation_code=failure.code,
            validation_detail=failure.detail,
            prior_repair_attempts=attempts,
            expected_semantic_shape=expected_shape,
            observed_semantic_shape=failure.observed_semantic_shape,
        )
        if decision.disposition != MaterialRepairDisposition.REPAIR:
            return None
        if session.budget.native_turns_used >= session.budget.max_native_turns:
            return None

        self._store.mark_limited(
            parent_link.id,
            code=failure.code,
            detail=failure.detail,
        )
        before = session.revision
        prepared = ResearchManager.prepare_native_delegation(
            session,
            obligation_id=obligation_id,
            analytical_scope=analytical_scope,
        )
        feedback = material_repair_feedback(decision)
        context = dict(prepared.request.context)
        context["dima_material_repair_feedback"] = feedback
        repair_message = "\n".join(
            (
                prepared.request.message,
                "[DIMA MATERIAL REPAIR FEEDBACK JSON]",
                json.dumps(
                    {"dima_material_repair_feedback": feedback},
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "[DIMA MATERIAL REPAIR BOUNDARY]",
                "- regenerate exactly one new native analytical query",
                "- preserve the accepted material requirement, ScopeVersion, principal, tenant, filters, and periods",
                "- correct only the validation mismatch described above",
                "- do not broaden scope or perform downstream investigation/reporting",
            )
        )
        request = prepared.request.model_copy(
            update={"context": context, "message": repair_message}
        )
        updated = self._store.save(
            prepared.session,
            expected_revision=before,
        )
        conversation = updated.native_conversation
        assert conversation is not None
        link = self._store.begin_delegation(
            session=updated,
            obligation_id=obligation_id,
            dima_request_id=request.dima_request_id,
            dima_trace_id=request.dima_trace_id,
            native_conversation_id=conversation.conversation_id,
            execution_kind="P14_REPAIR",
        )
        return updated, request, link

    def _limit(
        self,
        *,
        session: ResearchSession,
        obligation_id: str,
        code: str,
        detail: str,
        link_id=None,
        last_valid_boundary: str | None = None,
        first_invalid_boundary: str | None = None,
        expected_fingerprint: str | None = None,
        observed_fingerprint: str | None = None,
        scope_fingerprint: str | None = None,
        material_fingerprint: str | None = None,
        expected_semantic_shape: dict[str, Any] | None = None,
        observed_semantic_shape: dict[str, Any] | None = None,
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
            last_valid_boundary=last_valid_boundary,
            first_invalid_boundary=first_invalid_boundary,
            expected_fingerprint=expected_fingerprint,
            observed_fingerprint=observed_fingerprint,
            scope_fingerprint=scope_fingerprint,
            material_fingerprint=material_fingerprint,
            expected_semantic_shape=expected_semantic_shape,
            observed_semantic_shape=observed_semantic_shape,
        )

    def _retryable_observation_limit(
        self,
        *,
        session: ResearchSession,
        obligation_id: str,
        code: str,
        detail: str,
    ) -> ResearchAskResponse:
        prior_revision = session.revision
        updated = ResearchManager.record_retryable_limitation(
            session,
            obligation_id=obligation_id,
            code=code,
            detail=detail,
        )
        self._store.save(updated, expected_revision=prior_revision)
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
        consumer_obligation_ids: tuple[str, ...] | None = None,
        analytical_scope: AnalyticalRequestContract | None = None,
        native_session_token: str | None = None,
        result_dependency_source_obligation_id: str | None = None,
    ) -> ResearchAskResponse:
        bridge_factory, material_executor = self._runtime()
        tenant = self.tenant_binding_for(principal)
        subject = self._principal_subject(principal)
        # Every analytical execution must run only on the canonical lineage head.
        # This is a currentness gate, not a SelectionBinding-specific rule: an old
        # scope version must never acquire fresh native material after a follow-up
        # has superseded it.
        session = self._store.assert_lineage_head(
            self._store.load(session_id, tenant=tenant, principal=subject)
        )
        delegatable = self._store.delegatable_ids(
            session_id,
            tenant=tenant,
            principal=subject,
        )
        selected = self._select_obligation(session, delegatable, obligation_id)
        question = self.accepted_material_question(session, selected)
        consumer_ids = tuple(
            dict.fromkeys(consumer_obligation_ids or (selected,))
        )
        if selected not in set(consumer_ids):
            raise ResearchProductError(
                "P14_SHARED_ANCHOR_REQUIRED",
                "shared material consumers must include the execution anchor",
            )
        if not set(consumer_ids).issubset(set(delegatable)):
            raise ResearchProductError(
                "P14_SHARED_CONSUMER_NOT_DELEGATABLE",
                "shared consumers must be accepted analytical obligations",
            )
        consumer_questions = tuple(
            self.accepted_material_question(session, item)
            for item in consumer_ids
        )
        if len(consumer_ids) > 1 and any(
            item.result_dependency is not None
            for item in consumer_questions
        ):
            raise ResearchProductError(
                "P14_SHARED_RESULT_DEPENDENCY_FORBIDDEN",
                "result-dependent child material requires a later occurrence",
            )
        execution_analytical_scope: AnalyticalRequestContract | None = analytical_scope
        canonical_analytical_scope: AnalyticalRequestContract | None = analytical_scope
        if question.result_dependency is not None:
            resolver = getattr(material_executor, "resolve_result_dependency", None)
            if not callable(resolver):
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code="P14_RESULT_DEPENDENCY_RESOLVER_REQUIRED",
                    detail=(
                        "result-dependent material requires the governed P14 "
                        "dependency resolver"
                    ),
                )
            try:
                resolution = resolver(
                    principal=principal,
                    session=session,
                    obligation_id=selected,
                    source_execution_obligation_id=(
                        result_dependency_source_obligation_id
                    ),
                )
            except ResearchPersistenceError as exc:
                if exc.code == "P14_RESULT_DEPENDENCY_PARENT_PENDING":
                    return self._retryable_observation_limit(
                        session=session,
                        obligation_id=selected,
                        code=exc.code,
                        detail=exc.detail,
                    )
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code=exc.code,
                    detail=exc.detail,
                )
            except ResearchMaterialLimitation as exc:
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code=exc.code,
                    detail=exc.detail,
                    last_valid_boundary=exc.last_valid_boundary,
                    first_invalid_boundary=exc.first_invalid_boundary,
                    expected_fingerprint=exc.expected_fingerprint,
                    observed_fingerprint=exc.observed_fingerprint,
                    scope_fingerprint=exc.scope_fingerprint,
                    material_fingerprint=exc.material_fingerprint,
                    expected_semantic_shape=exc.expected_semantic_shape,
                    observed_semantic_shape=exc.observed_semantic_shape,
                )
            if resolution is None:
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code="P14_RESULT_DEPENDENCY_RESOLUTION_MISSING",
                    detail="declared result dependency produced no execution-local binding",
                )
            execution_analytical_scope = resolution.contract
            canonical_analytical_scope = resolution.contract

        if canonical_analytical_scope is None:
            try:
                canonical_analytical_scope = analytical_scope_contract(
                    session=session,
                    obligation_id=selected,
                )
            except ResearchAnalyticalScopeError as exc:
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code=exc.code,
                    detail=exc.detail,
                    last_valid_boundary=exc.last_valid_boundary,
                    first_invalid_boundary=exc.first_invalid_boundary,
                    expected_fingerprint=exc.expected_fingerprint,
                    observed_fingerprint=exc.observed_fingerprint,
                    scope_fingerprint=exc.scope_fingerprint,
                    material_fingerprint=exc.material_fingerprint,
                    expected_semantic_shape=exc.expected_semantic_shape,
                    observed_semantic_shape=exc.observed_semantic_shape,
                )

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
                analytical_scope=execution_analytical_scope,
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

        def execute_occurrence_with_observation_resume(
            *,
            link,
            request,
            repair_parent_link_id=None,
        ):
            """Bounded readiness/observation retry over one durable occurrence.

            Native cognition is never replayed. A CANDIDATE_CAPTURED occurrence
            has not executed yet; retries only attest/observe that same locator.
            If a prior process reached EXECUTED, retries remain read-only and
            exact execution is never replayed.
            """

            try:
                return runner.execute(
                    session=session,
                    principal=principal,
                    obligation_id=selected,
                    link=link,
                    request=request,
                    native_session_token=native_session_token,
                    analytical_scope=execution_analytical_scope,
                    consumer_obligation_ids=consumer_ids,
                    repair_parent_link_id=repair_parent_link_id,
                )
            except ResearchMaterialObservationUnavailable as first_exc:
                last_exc = first_exc

            persisted = self._store.execution_link(link.id)
            if persisted.status not in {"CANDIDATE_CAPTURED", "EXECUTED"}:
                raise last_exc

            # Retry only exact-occurrence readiness/material observation. A
            # CANDIDATE_CAPTURED link has zero analytical execution side effect;
            # an EXECUTED link already owns one durable result. Neither path
            # reopens Metabot cognition or submits a second native execution.
            for delay_seconds in (0.2, 0.6, 1.2, 2.4):
                time.sleep(delay_seconds)
                try:
                    return runner.execute(
                        session=session,
                        principal=principal,
                        obligation_id=selected,
                        link=persisted,
                        request=None,
                        native_session_token=native_session_token,
                        analytical_scope=execution_analytical_scope,
                        consumer_obligation_ids=consumer_ids,
                        repair_parent_link_id=repair_parent_link_id,
                    )
                except ResearchMaterialObservationUnavailable as retry_exc:
                    last_exc = retry_exc
                    persisted = self._store.execution_link(link.id)
                    if persisted.status not in {"CANDIDATE_CAPTURED", "EXECUTED"}:
                        raise

            raise last_exc

        try:
            occurrence = execute_occurrence_with_observation_resume(
                link=pending,
                request=(prepared.request if prepared is not None else None),
            )
        except ResearchMaterialObservationUnavailable as exc:
            return self._retryable_observation_limit(
                session=session,
                obligation_id=selected,
                code=exc.code,
                detail=exc.detail,
            )
        except ResearchMaterialLimitation as exc:
            repair = self._prepare_material_repair(
                session=session,
                obligation_id=selected,
                parent_link=pending,
                failure=exc,
                analytical_scope=canonical_analytical_scope,
            )
            if repair is None:
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code=exc.code,
                    detail=exc.detail,
                    link_id=pending.id,
                    last_valid_boundary=exc.last_valid_boundary,
                    first_invalid_boundary=exc.first_invalid_boundary,
                    expected_fingerprint=exc.expected_fingerprint,
                    observed_fingerprint=exc.observed_fingerprint,
                    scope_fingerprint=exc.scope_fingerprint,
                    material_fingerprint=exc.material_fingerprint,
                    expected_semantic_shape=exc.expected_semantic_shape,
                    observed_semantic_shape=exc.observed_semantic_shape,
                )
            session, repair_request, repair_link = repair
            try:
                occurrence = execute_occurrence_with_observation_resume(
                    link=repair_link,
                    request=repair_request,
                    repair_parent_link_id=pending.id,
                )
            except ResearchMaterialObservationUnavailable as repair_exc:
                return self._retryable_observation_limit(
                    session=session,
                    obligation_id=selected,
                    code=repair_exc.code,
                    detail=repair_exc.detail,
                )
            except ResearchMaterialLimitation as repair_exc:
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code=repair_exc.code,
                    detail=repair_exc.detail,
                    link_id=repair_link.id,
                    last_valid_boundary=repair_exc.last_valid_boundary,
                    first_invalid_boundary=repair_exc.first_invalid_boundary,
                    expected_fingerprint=repair_exc.expected_fingerprint,
                    observed_fingerprint=repair_exc.observed_fingerprint,
                    scope_fingerprint=repair_exc.scope_fingerprint,
                    material_fingerprint=repair_exc.material_fingerprint,
                    expected_semantic_shape=repair_exc.expected_semantic_shape,
                    observed_semantic_shape=repair_exc.observed_semantic_shape,
                )
            except NativeEngineBridgeError as repair_exc:
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code="P14_NATIVE_TRANSPORT_FAILED",
                    detail=str(repair_exc),
                    link_id=repair_link.id,
                )
            except ResearchPersistenceError as repair_exc:
                return self._limit(
                    session=session,
                    obligation_id=selected,
                    code=repair_exc.code,
                    detail=repair_exc.detail,
                    link_id=repair_link.id,
                )
            pending = repair_link
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
        if len(consumer_ids) > 1:
            updated = ResearchManager.admit_shared_receipted_evidence(
                session,
                obligation_ids=consumer_ids,
                receipt=outcome.receipt,
                evidence=outcome.evidence,
                satisfies_obligation=outcome.satisfies_obligation,
            )
        else:
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
            attestation_id=outcome.attestation_id,
        )
        return self._response(
            updated,
            obligation_id=selected,
            native_query_id=native_query_id,
            receipt_id=outcome.receipt.receipt_id,
            evidence_id=outcome.evidence.artifact_id,
            resumed_exact_occurrence=resumed_exact,
        )
