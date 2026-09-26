"""Authoritative Day10 /ask-v2 product coordinator.

There are exactly two analytical product lanes:
STANDARD -> StandardLaneEngine
RESEARCH -> ResearchLaneService

Only an explicit StandardLaneStatus.RESEARCH_REQUIRED transition may enter Research.
No failed/clarification/unsupported Standard state is reinterpreted as Research.
"""

from __future__ import annotations

from typing import Any, Callable

from app.config import get_settings
from app.llm import build_generator
from app.v2.context_provider import ContextProviderV0
from app.v2.model_policy import ModelRole, ModelRolePolicy
from app.v2.models import EvidenceArtifact
from app.v2.product_models import (
    ProductAskRequest,
    ProductEvidenceRef,
    ProductEventKind,
    ProductLane,
    ProductRequestContext,
    ProductResponse,
    ProductSectionContinuation,
    ProductStatus,
    ProductTerminalReceipt,
    VersionedReport,
    mint_product_turn_ref,
)
from app.v2.persistence import (
    CheckpointScope,
    DurableCheckpointStore,
    restore_research_context,
    state_from_research_result,
)
from app.v2.product_events import ProductEventSink
from app.v2.research_lane import ResearchLaneResult, ResearchLaneService
from app.v2.research_report_projector import (
    ResearchReportProjectionStatus,
    ResearchReportProjector,
)
from app.v2.report_builder import (
    ReportBuildStatus,
    ReportBuilder,
    ReportSourceProvenance,
)
from app.v2.report_narration import ReportNarrator
from app.v2.report_continuation import (
    MissingReportContinuationContextError,
    ReportContextRegistry,
    ReportSectionContinuationSigner,
    StaleReportContinuationError,
    continuation_analytical_authority,
    continuation_conversation,
    continuation_scope_by_kind,
)
from app.v2.runtime_boundary import bind_runtime, request_ref, tenant_binding
from app.v2.standard_authority import AcceptedAuthorityRegistry
from app.v2.semantic_linker import StructuredSemanticCandidateDecisionProvider
from app.v2.standard_lane import (
    StandardLaneEngine,
    StandardLaneOutcome,
    StandardLaneStatus,
)
from app.v2.temporal_intent import StructuredTemporalNormalizationProvider
from control_plane.security import derive_hmac_key


def _product_evidence(item: EvidenceArtifact) -> ProductEvidenceRef:
    return ProductEvidenceRef(
        evidence_ref=item.artifact_id,
        query_contract_refs=item.query_contract_refs,
        evidence_kind=item.evidence_kind,
        verified=item.verified,
    )


def build_standard_lane(
    settings,
    *,
    authority_registry: AcceptedAuthorityRegistry | None = None,
) -> tuple[StandardLaneEngine, str]:
    """Resolve the sealed Standard cognition profile without introducing a router model."""

    policy = ModelRolePolicy(settings)
    fast_settings, fast_profile = policy.scoped_settings(ModelRole.FAST_LANGUAGE)
    semantic_settings, _ = policy.scoped_settings(ModelRole.SEMANTIC_LINKER)
    temporal_settings, _ = policy.scoped_settings(ModelRole.TEMPORAL_NORMALIZER)

    fast_llm = build_generator(fast_settings)
    semantic_llm = build_generator(semantic_settings)
    temporal_llm = build_generator(temporal_settings)

    semantic_structured = getattr(semantic_llm, "structured_json", None)
    temporal_structured = getattr(temporal_llm, "structured_json", None)
    return (
        StandardLaneEngine(
            intent_structured=fast_llm.structured_json,
            coverage_structured=fast_llm.structured_json,
            semantic_provider=(
                StructuredSemanticCandidateDecisionProvider(
                    structured=semantic_structured
                )
                if callable(semantic_structured)
                else None
            ),
            temporal_provider=(
                StructuredTemporalNormalizationProvider(
                    structured=temporal_structured
                )
                if callable(temporal_structured)
                else None
            ),
            authority_registry=authority_registry,
        ),
        fast_profile.role.value,
    )


def build_report_narrator(settings) -> ReportNarrator:
    """Reuse the approved Research/Reference-capable structured provider for presentation."""

    policy = ModelRolePolicy(settings)
    scoped, profile = policy.scoped_settings(ModelRole.RESEARCH_MANAGER)
    llm = build_generator(scoped)
    return ReportNarrator(
        llm=llm,
        provider=profile.provider,
        model=profile.model,
    )


class ProductCoordinator:
    """Single product core used by sync and future stream adapters."""

    def __init__(
        self,
        *,
        standard_lane: StandardLaneEngine | None = None,
        standard_model_role: str | None = None,
        research_lane: ResearchLaneService | None = None,
        report_narrator: ReportNarrator | None = None,
        report_contexts: ReportContextRegistry | None = None,
        continuation_signer: ReportSectionContinuationSigner | None = None,
        authority_registry: AcceptedAuthorityRegistry | None = None,
        checkpoint_store: DurableCheckpointStore | None = None,
    ) -> None:
        self._authority_registry = authority_registry or AcceptedAuthorityRegistry()
        self._standard_lane = standard_lane
        self._standard_model_role = standard_model_role
        self._research_lane = research_lane
        self._report_narrator = report_narrator
        self._report_contexts = report_contexts or ReportContextRegistry()
        self._checkpoint_store = checkpoint_store
        self._continuation_signer = continuation_signer or ReportSectionContinuationSigner(
            signing_key=derive_hmac_key("v2-report-section-continuation-v1")
        )
        if self._standard_lane is not None:
            self._standard_lane.bind_authority_registry(self._authority_registry)
        if self._research_lane is not None:
            self._research_lane.bind_authority_registry(self._authority_registry)

    @staticmethod
    def _checkpoint_scope(
        *,
        context: ProductRequestContext,
        lineage_id: str,
    ) -> CheckpointScope:
        principal_subject = str(
            getattr(context.principal, "user_id", "") or ""
        )
        return CheckpointScope(
            tenant_binding=context.tenant_binding,
            principal_subject=principal_subject,
            session_id=context.session_id,
            thread_id=context.thread_id,
            context_version=context.semantic_context.context_version.version,
            lineage_id=lineage_id,
        )

    def _rehydrate_continuation_entry(
        self,
        *,
        payload,
        context: ProductRequestContext,
    ):
        if self._checkpoint_store is None:
            raise MissingReportContinuationContextError(
                "report continuation context missing; durable store unavailable"
            )
        scope = self._checkpoint_scope(
            context=context,
            lineage_id=payload.lineage_ref,
        )
        checkpoint = self._checkpoint_store.load(scope)
        if checkpoint is None:
            raise MissingReportContinuationContextError(
                "report continuation durable checkpoint missing"
            )
        prior = restore_research_context(checkpoint)
        versioned = next(
            (
                item
                for item in checkpoint.state.reports
                if item.report.report_id == payload.report_id
            ),
            None,
        )
        if versioned is None:
            raise MissingReportContinuationContextError(
                "signed report is absent from durable checkpoint"
            )
        if versioned.source_run_ref != payload.source_run_ref:
            raise StaleReportContinuationError(
                "signed report source run does not match durable checkpoint"
            )
        self._report_contexts.register(
            report=versioned.report,
            research_result=prior,
            principal_subject=scope.principal_subject,
            tenant_binding=scope.tenant_binding,
            context_version=scope.context_version,
            session_id=scope.session_id,
            thread_id=scope.thread_id,
            source_run_ref=versioned.source_run_ref,
            lineage_ref=scope.lineage_id,
            report_version=versioned.version,
        )
        return self._report_contexts.resolve(
            payload,
            principal_subject=scope.principal_subject,
            tenant_binding=scope.tenant_binding,
            context_version=scope.context_version,
            session_id=scope.session_id,
            thread_id=scope.thread_id,
        )

    def _ensure_standard_lane(self) -> None:
        if self._standard_lane is None:
            lane, role = build_standard_lane(
                get_settings(),
                authority_registry=self._authority_registry,
            )
            self._standard_lane = lane
            self._standard_model_role = role

    def _ensure_research_lane(self) -> None:
        if self._research_lane is None:
            self._research_lane = ResearchLaneService.from_settings(
                get_settings(),
                authority_registry=self._authority_registry,
            )

    def _ensure_report_narrator(self) -> None:
        if self._report_narrator is None:
            self._report_narrator = build_report_narrator(get_settings())

    @staticmethod
    def _bind_context(
        *,
        request,
        body: ProductAskRequest,
        principal,
        turn_ref: str | None = None,
    ) -> ProductRequestContext:
        service, schema, runtime = bind_runtime(request, principal)
        semantic_context = ContextProviderV0().build(service, runtime)
        binding = tenant_binding(runtime)
        return ProductRequestContext(
            request_ref=request_ref(body),
            tenant_binding=binding,
            principal=principal,
            tenant_runtime=runtime,
            service=service,
            schema=schema,
            semantic_context=semantic_context,
            contract_store=getattr(request.app.state, "contracts", None),
            session_id=body.session_id,
            thread_id=body.thread_id,
            turn_ref=turn_ref or mint_product_turn_ref(),
        )

    def handle(
        self,
        *,
        request,
        body: ProductAskRequest,
        principal,
        event_sink: ProductEventSink | None = None,
        turn_ref: str | None = None,
        cancel_check: Callable[[], bool] | None = None,
        answer_now_check: Callable[[], bool] | None = None,
    ) -> ProductResponse:
        effective_turn_ref = turn_ref
        if event_sink is not None:
            if turn_ref is not None and event_sink.turn_ref != turn_ref:
                raise RuntimeError(
                    "explicit Product turn_ref does not match ProductEventSink"
                )
            effective_turn_ref = event_sink.turn_ref

        context = self._bind_context(
            request=request,
            body=body,
            principal=principal,
            turn_ref=effective_turn_ref,
        )
        sink = event_sink or ProductEventSink(
            request_ref=context.request_ref,
            turn_ref=context.turn_ref,
        )
        if sink.turn_ref != context.turn_ref:
            raise RuntimeError("ProductEventSink turn_ref does not match Product turn")
        sink.emit(
            ProductEventKind.REQUEST_ACCEPTED,
            refs=(context.request_ref,),
            transition_ref="frontdoor:bound",
        )

        if body.report_section_token is not None:
            payload = self._continuation_signer.verify(
                body.report_section_token,
                tenant_binding=context.tenant_binding,
                context_version=context.semantic_context.context_version.version,
                session_id=body.session_id,
                thread_id=body.thread_id,
            )
            principal_subject = str(getattr(context.principal, "user_id", "") or "")
            try:
                entry = self._report_contexts.resolve(
                    payload,
                    principal_subject=principal_subject,
                    tenant_binding=context.tenant_binding,
                    context_version=context.semantic_context.context_version.version,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                )
            except MissingReportContinuationContextError:
                entry = self._rehydrate_continuation_entry(
                    payload=payload,
                    context=context,
                )
            continuation_authority = continuation_analytical_authority(entry)

            sink.emit(
                ProductEventKind.LANE_SELECTED,
                refs=(ProductLane.RESEARCH.value,),
                transition_ref="lane:RESEARCH:section-continuation",
            )
            sink.emit(
                ProductEventKind.RESEARCH_STARTED,
                refs=(context.request_ref, entry.section.section_id),
                transition_ref=f"research:section:{entry.section.section_id}",
            )
            self._ensure_research_lane()
            assert self._research_lane is not None

            transition_map = {
                "evidence_verified": ProductEventKind.EVIDENCE_VERIFIED,
                "adaptive_branch_opened": ProductEventKind.ADAPTIVE_BRANCH_OPENED,
                "relationship_checked": ProductEventKind.RELATIONSHIP_CHECKED,
                "root_cause_candidate": ProductEventKind.ROOT_CAUSE_CANDIDATE,
            }

            def on_continuation_progress(kind: str, refs: tuple[str, ...]) -> None:
                event_kind = transition_map.get(kind)
                if event_kind is None:
                    return
                sink.emit(
                    event_kind,
                    refs=refs,
                    transition_ref=f"continuation:{kind}:" + "|".join(refs),
                )

            continuation_state = continuation_conversation(entry)
            research = self._research_lane.continue_run(
                context=context,
                body=body,
                prior=entry.research_result,
                conversation=continuation_state,
                section_scope_refs=entry.section.semantic_scope,
                context_scope_by_kind=continuation_scope_by_kind(entry),
                allowed_continuation_parent_refs=(
                    continuation_authority.admitted_parent_refs
                ),
                progress_callback=on_continuation_progress,
                cancel_check=cancel_check,
                answer_now_check=answer_now_check,
            )
            return self._research_response(
                context=context,
                result=research,
                sink=sink,
                report_version=entry.report_version + 1,
                supersedes_report_ref=entry.report.report_id,
                conversation=continuation_state,
            )

        self._ensure_standard_lane()
        assert self._standard_lane is not None
        standard = self._standard_lane.run(
            question=body.question,
            turn_id=context.turn_ref,
            request_ref=context.request_ref,
            semantic_context=context.semantic_context,
            schema=context.schema,
            conversation=body.conversation,
            tenant_binding=context.tenant_binding,
            cognition_model_role=self._standard_model_role or "FAST_LANGUAGE",
            principal=context.principal,
            service=context.service,
            tenant_runtime=context.tenant_runtime,
            contract_store=context.contract_store,
            session_id=body.session_id,
        )

        if standard.status == StandardLaneStatus.ACCEPTED:
            sink.emit(
                ProductEventKind.LANE_SELECTED,
                refs=(ProductLane.STANDARD.value,),
                transition_ref="lane:STANDARD",
            )
            return self._standard_response(
                context=context,
                outcome=standard,
                sink=sink,
            )

        if standard.status == StandardLaneStatus.RESEARCH_REQUIRED:
            # Isolation invariant: no StandardProjection, Standard semantic handles,
            # obligations or accepted Standard authority cross this call boundary.
            sink.emit(
                ProductEventKind.LANE_SELECTED,
                refs=(ProductLane.RESEARCH.value,),
                transition_ref="lane:RESEARCH",
            )
            sink.emit(
                ProductEventKind.RESEARCH_STARTED,
                refs=(context.request_ref,),
                transition_ref="research:started",
            )
            self._ensure_research_lane()
            assert self._research_lane is not None

            transition_map = {
                "evidence_verified": ProductEventKind.EVIDENCE_VERIFIED,
                "adaptive_branch_opened": ProductEventKind.ADAPTIVE_BRANCH_OPENED,
                "relationship_checked": ProductEventKind.RELATIONSHIP_CHECKED,
                "root_cause_candidate": ProductEventKind.ROOT_CAUSE_CANDIDATE,
            }

            def on_progress(kind: str, refs: tuple[str, ...]) -> None:
                event_kind = transition_map.get(kind)
                if event_kind is None:
                    return
                sink.emit(
                    event_kind,
                    refs=refs,
                    transition_ref=f"{kind}:" + "|".join(refs),
                )

            research = self._research_lane.run(
                context=context,
                body=body,
                progress_callback=on_progress,
                cancel_check=cancel_check,
                answer_now_check=answer_now_check,
            )
            return self._research_response(
                context=context,
                result=research,
                sink=sink,
                report_version=1,
                supersedes_report_ref=None,
                conversation=body.conversation,
            )

        if standard.status == StandardLaneStatus.CLARIFICATION_REQUIRED:
            sink.emit(
                ProductEventKind.LANE_SELECTED,
                refs=(ProductLane.STANDARD.value,),
                transition_ref="lane:STANDARD",
            )
            return self._terminal_standard(
                context=context,
                status=ProductStatus.CLARIFY,
                reasons=standard.reasons,
                sink=sink,
            )
        if standard.status == StandardLaneStatus.UNSUPPORTED:
            sink.emit(
                ProductEventKind.LANE_SELECTED,
                refs=(ProductLane.STANDARD.value,),
                transition_ref="lane:STANDARD",
            )
            return self._terminal_standard(
                context=context,
                status=ProductStatus.UNSUPPORTED,
                reasons=standard.reasons,
                sink=sink,
            )
        sink.emit(
            ProductEventKind.LANE_SELECTED,
            refs=(ProductLane.STANDARD.value,),
            transition_ref="lane:STANDARD",
        )
        return self._terminal_standard(
            context=context,
            status=ProductStatus.FAILED,
            reasons=standard.reasons
            or (f"standard lane terminal={standard.status.value}",),
            sink=sink,
        )

    @staticmethod
    def _standard_response(
        *,
        context: ProductRequestContext,
        outcome: StandardLaneOutcome,
        sink: ProductEventSink,
    ) -> ProductResponse:
        assert outcome.execution is not None
        evidence = outcome.execution.evidence
        sink.emit(
            ProductEventKind.EVIDENCE_VERIFIED,
            refs=(evidence.artifact_id,),
            transition_ref=f"standard-evidence:{evidence.artifact_id}",
        )
        sink.emit(
            ProductEventKind.TERMINAL,
            refs=("STANDARD_ACCEPTED",),
            transition_ref="terminal:STANDARD_ACCEPTED",
        )
        return ProductResponse(
            request_ref=context.request_ref,
            turn_ref=context.turn_ref,
            lane=ProductLane.STANDARD,
            status=ProductStatus.ANSWER,
            events=sink.events,
            evidence_refs=(_product_evidence(evidence),),
            limitations=evidence.limitations,
            terminal_receipt=ProductTerminalReceipt(
                lane=ProductLane.STANDARD,
                status=ProductStatus.ANSWER,
                verified_complete=True,
                terminal_status="STANDARD_ACCEPTED",
                data_queries=outcome.execution.query_count,
            ),
        )

    @staticmethod
    def _terminal_standard(
        *,
        context: ProductRequestContext,
        status: ProductStatus,
        reasons: tuple[str, ...],
        sink: ProductEventSink,
    ) -> ProductResponse:
        sink.emit(
            ProductEventKind.TERMINAL,
            refs=(status.value,),
            transition_ref=f"terminal:{status.value}",
        )
        return ProductResponse(
            request_ref=context.request_ref,
            turn_ref=context.turn_ref,
            lane=ProductLane.STANDARD,
            status=status,
            events=sink.events,
            limitations=reasons,
            terminal_receipt=ProductTerminalReceipt(
                lane=ProductLane.STANDARD,
                status=status,
                verified_complete=False,
                terminal_status=status.value,
                reasons=reasons,
            ),
        )

    def _research_response(
        self,
        *,
        context: ProductRequestContext,
        result: ResearchLaneResult,
        sink: ProductEventSink,
        report_version: int,
        supersedes_report_ref: str | None,
        conversation=None,
    ) -> ProductResponse:
        snapshot = result.runtime.snapshot
        evidence = tuple(_product_evidence(item) for item in result.evidence)
        base_limitations = tuple(
            dict.fromkeys(
                limitation
                for item in result.evidence
                for limitation in item.limitations
            )
        )

        if result.outcome.cancelled:
            return self._research_terminal(
                context=context,
                result=result,
                status=ProductStatus.CANCELLED,
                evidence=evidence,
                limitations=base_limitations,
                sink=sink,
            )
        if result.outcome.clarification_required:
            return self._research_terminal(
                context=context,
                result=result,
                status=ProductStatus.CLARIFY,
                evidence=evidence,
                limitations=base_limitations,
                sink=sink,
            )
        if result.accepted_contract is None or result.ledger is None:
            return self._research_terminal(
                context=context,
                result=result,
                status=ProductStatus.FAILED,
                evidence=evidence,
                limitations=(
                    *base_limitations,
                    "accepted Research authority unavailable",
                ),
                sink=sink,
            )

        projection = ResearchReportProjector(
            semantic_handles=result.semantic_handles,
            tenant_binding=context.tenant_binding,
            context_version=context.semantic_context.context_version.version,
        ).project(
            ledger=result.ledger,
            evidence=result.evidence,
            findings=result.findings,
            allow_partial=result.outcome.answer_now_requested,
        )
        if (
            projection.status != ResearchReportProjectionStatus.COMPLETE
            or projection.request is None
        ):
            return self._research_terminal(
                context=context,
                result=result,
                status=ProductStatus.PARTIAL,
                evidence=evidence,
                artifact_refs=tuple(
                    item.artifact_id for item in projection.artifacts
                ),
                limitations=tuple(
                    dict.fromkeys((*base_limitations, *projection.issues))
                ),
                sink=sink,
            )

        provenance = ReportSourceProvenance(
            accepted_contract_id=result.accepted_contract.contract_id,
            lineage_id=result.accepted_contract.lineage_id,
            run_id=snapshot.run_id,
            tenant_binding=context.tenant_binding,
            context_version=context.semantic_context.context_version.version,
        )
        build = ReportBuilder(
            evidence_store=result.evidence_store,
            current_evidence_refs=snapshot.evidence_refs,
            findings=result.findings,
            semantic_handles=result.semantic_handles,
            known_artifacts={
                item.artifact_id: item.artifact_kind
                for item in projection.artifacts
            },
            provenance=provenance,
        ).build(projection.request)

        if build.status != ReportBuildStatus.COMPLETE or build.report is None:
            return self._research_terminal(
                context=context,
                result=result,
                status=ProductStatus.PARTIAL,
                evidence=evidence,
                artifact_refs=tuple(
                    item.artifact_id for item in projection.artifacts
                ),
                limitations=tuple(
                    dict.fromkeys(
                        (
                            *base_limitations,
                            *(
                                f"{issue.code.value}: {issue.reason}"
                                for issue in build.issues
                            ),
                        )
                    )
                ),
                sink=sink,
            )

        for artifact in projection.artifacts:
            sink.emit(
                ProductEventKind.ARTIFACT_READY,
                refs=(artifact.artifact_id,),
                transition_ref=f"artifact:{artifact.artifact_id}",
            )
        if result.outcome.answer_now_requested:
            sink.emit(
                ProductEventKind.PARTIAL_READY,
                refs=(build.report.report_id,),
                transition_ref=f"partial-report:{build.report.report_id}",
            )
        else:
            sink.emit(
                ProductEventKind.REPORT_READY,
                refs=(build.report.report_id,),
                transition_ref=f"report:{build.report.report_id}",
            )
        self._ensure_report_narrator()
        assert self._report_narrator is not None
        overlay = self._report_narrator.compose(build.report)
        status = (
            ProductStatus.REPORT
            if result.verified_complete and not result.outcome.answer_now_requested
            else ProductStatus.PARTIAL
        )
        sink.emit(
            ProductEventKind.TERMINAL,
            refs=(status.value,),
            transition_ref=f"terminal:{status.value}",
        )

        principal_subject = str(getattr(context.principal, "user_id", "") or "")
        versioned_report = VersionedReport(
            version=report_version,
            report=build.report,
            supersedes_report_ref=supersedes_report_ref,
            source_run_ref=snapshot.run_id,
        )
        if self._checkpoint_store is not None:
            scope = self._checkpoint_scope(
                context=context,
                lineage_id=result.accepted_contract.lineage_id,
            )
            prior_checkpoint = self._checkpoint_store.load(scope)
            prior_reports = (
                ()
                if prior_checkpoint is None
                else prior_checkpoint.state.reports
            )
            reports_by_id = {
                item.report.report_id: item
                for item in prior_reports
            }
            reports_by_id[versioned_report.report.report_id] = versioned_report
            durable_state = state_from_research_result(
                result=result,
                scope=scope,
                reports=tuple(
                    sorted(
                        reports_by_id.values(),
                        key=lambda item: item.version,
                    )
                ),
                conversation=conversation,
            )
            self._checkpoint_store.commit(
                scope=scope,
                state=durable_state,
                expected_revision=(
                    0
                    if prior_checkpoint is None
                    else prior_checkpoint.revision
                ),
            )

        self._report_contexts.register(
            report=build.report,
            research_result=result,
            principal_subject=principal_subject,
            tenant_binding=context.tenant_binding,
            context_version=context.semantic_context.context_version.version,
            session_id=context.session_id,
            thread_id=context.thread_id,
            source_run_ref=snapshot.run_id,
            lineage_ref=result.accepted_contract.lineage_id,
            report_version=report_version,
        )
        continuations = tuple(
            ProductSectionContinuation(
                section_ref=section.section_id,
                followup_context_ref=section.followup_context_ref,
                token=self._continuation_signer.mint(
                    tenant_binding=context.tenant_binding,
                    context_version=context.semantic_context.context_version.version,
                    session_id=context.session_id,
                    thread_id=context.thread_id,
                    report_id=build.report.report_id,
                    section_id=section.section_id,
                    followup_context_ref=section.followup_context_ref,
                    source_run_ref=snapshot.run_id,
                    lineage_ref=result.accepted_contract.lineage_id,
                ),
            )
            for section in build.report.sections
        )

        return ProductResponse(
            request_ref=context.request_ref,
            turn_ref=context.turn_ref,
            lane=ProductLane.RESEARCH,
            status=status,
            events=sink.events,
            evidence_refs=evidence,
            artifact_refs=tuple(
                item.artifact_id for item in projection.artifacts
            ),
            report=versioned_report,
            narration=overlay,
            limitations=tuple(
                dict.fromkeys(
                    (*base_limitations, *build.report.limitations)
                )
            ),
            terminal_receipt=ProductTerminalReceipt(
                lane=ProductLane.RESEARCH,
                status=status,
                verified_complete=result.verified_complete,
                terminal_status=(
                    "ANSWER_NOW_PARTIAL"
                    if result.outcome.answer_now_requested
                    else (
                        result.outcome.terminal_status.value
                        if result.outcome.terminal_status is not None
                        else None
                    )
                ),
                manager_turns=snapshot.manager_turns,
                tool_calls=snapshot.tool_calls,
                data_queries=snapshot.data_queries,
            ),
            section_continuations=continuations,
        )

    @staticmethod
    def _research_terminal(
        *,
        context: ProductRequestContext,
        result: ResearchLaneResult,
        status: ProductStatus,
        evidence: tuple[ProductEvidenceRef, ...],
        limitations: tuple[str, ...],
        sink: ProductEventSink,
        artifact_refs: tuple[str, ...] = (),
    ) -> ProductResponse:
        snapshot = result.runtime.snapshot
        if status == ProductStatus.PARTIAL:
            sink.emit(
                ProductEventKind.PARTIAL_READY,
                refs=tuple(item.evidence_ref for item in evidence),
                transition_ref="partial:verified-evidence",
            )
        sink.emit(
            ProductEventKind.TERMINAL,
            refs=(status.value,),
            transition_ref=f"terminal:{status.value}",
        )
        return ProductResponse(
            request_ref=context.request_ref,
            turn_ref=context.turn_ref,
            lane=ProductLane.RESEARCH,
            status=status,
            events=sink.events,
            evidence_refs=evidence,
            artifact_refs=artifact_refs,
            limitations=limitations,
            terminal_receipt=ProductTerminalReceipt(
                lane=ProductLane.RESEARCH,
                status=status,
                verified_complete=False,
                terminal_status=(
                    result.outcome.terminal_status.value
                    if result.outcome.terminal_status is not None
                    else None
                ),
                manager_turns=snapshot.manager_turns,
                tool_calls=snapshot.tool_calls,
                data_queries=snapshot.data_queries,
            ),
        )
