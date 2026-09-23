"""Authoritative Day10 /ask-v2 product coordinator.

There are exactly two analytical product lanes:
STANDARD -> StandardLaneEngine
RESEARCH -> ResearchLaneService

Only an explicit StandardLaneStatus.RESEARCH_REQUIRED transition may enter Research.
No failed/clarification/unsupported Standard state is reinterpreted as Research.
"""

from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.llm import build_generator
from app.v2.context_provider import ContextProviderV0
from app.v2.model_policy import ModelRole, ModelRolePolicy
from app.v2.models import AskV2Request, EvidenceArtifact
from app.v2.product_models import (
    ProductEvidenceRef,
    ProductEventKind,
    ProductLane,
    ProductRequestContext,
    ProductResponse,
    ProductStatus,
    ProductTerminalReceipt,
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
from app.v2.runtime_boundary import bind_runtime, request_ref, tenant_binding
from app.v2.semantic_linker import StructuredSemanticCandidateDecisionProvider
from app.v2.standard_lane import (
    StandardLaneEngine,
    StandardLaneOutcome,
    StandardLaneStatus,
)
from app.v2.temporal_intent import StructuredTemporalNormalizationProvider


def _product_evidence(item: EvidenceArtifact) -> ProductEvidenceRef:
    return ProductEvidenceRef(
        evidence_ref=item.artifact_id,
        query_contract_refs=item.query_contract_refs,
        evidence_kind=item.evidence_kind,
        verified=item.verified,
    )


def build_standard_lane(settings) -> tuple[StandardLaneEngine, str]:
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
    ) -> None:
        self._standard_lane = standard_lane
        self._standard_model_role = standard_model_role
        self._research_lane = research_lane
        self._report_narrator = report_narrator

    def _ensure_standard_lane(self) -> None:
        if self._standard_lane is None:
            lane, role = build_standard_lane(get_settings())
            self._standard_lane = lane
            self._standard_model_role = role

    def _ensure_research_lane(self) -> None:
        if self._research_lane is None:
            self._research_lane = ResearchLaneService.from_settings(get_settings())

    def _ensure_report_narrator(self) -> None:
        if self._report_narrator is None:
            self._report_narrator = build_report_narrator(get_settings())

    @staticmethod
    def _bind_context(
        *,
        request,
        body: AskV2Request,
        principal,
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
        )

    def handle(
        self,
        *,
        request,
        body: AskV2Request,
        principal,
        event_sink: ProductEventSink | None = None,
    ) -> ProductResponse:
        self._ensure_standard_lane()
        assert self._standard_lane is not None

        context = self._bind_context(
            request=request,
            body=body,
            principal=principal,
        )
        sink = event_sink or ProductEventSink(request_ref=context.request_ref)
        sink.emit(
            ProductEventKind.REQUEST_ACCEPTED,
            refs=(context.request_ref,),
            transition_ref="frontdoor:bound",
        )
        standard = self._standard_lane.run(
            question=body.question,
            turn_id=f"turn:{context.request_ref}",
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
            )
            return self._research_response(
                context=context,
                result=research,
                sink=sink,
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
            if result.verified_complete
            else ProductStatus.PARTIAL
        )
        sink.emit(
            ProductEventKind.TERMINAL,
            refs=(status.value,),
            transition_ref=f"terminal:{status.value}",
        )
        return ProductResponse(
            request_ref=context.request_ref,
            lane=ProductLane.RESEARCH,
            status=status,
            events=sink.events,
            evidence_refs=evidence,
            artifact_refs=tuple(
                item.artifact_id for item in projection.artifacts
            ),
            report=build.report,
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
                    result.outcome.terminal_status.value
                    if result.outcome.terminal_status is not None
                    else None
                ),
                manager_turns=snapshot.manager_turns,
                tool_calls=snapshot.tool_calls,
                data_queries=snapshot.data_queries,
            ),
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
