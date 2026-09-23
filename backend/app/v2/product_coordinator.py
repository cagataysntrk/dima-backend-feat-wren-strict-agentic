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
    ProductLane,
    ProductRequestContext,
    ProductResponse,
    ProductStatus,
    ProductTerminalReceipt,
)
from app.v2.research_lane import ResearchLaneResult, ResearchLaneService
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


class ProductCoordinator:
    """Single product core used by sync and future stream adapters."""

    def __init__(
        self,
        *,
        standard_lane: StandardLaneEngine | None = None,
        standard_model_role: str | None = None,
        research_lane: ResearchLaneService | None = None,
    ) -> None:
        self._standard_lane = standard_lane
        self._standard_model_role = standard_model_role
        self._research_lane = research_lane

    def _ensure_lanes(self) -> None:
        settings = get_settings()
        if self._standard_lane is None:
            lane, role = build_standard_lane(settings)
            self._standard_lane = lane
            self._standard_model_role = role
        if self._research_lane is None:
            self._research_lane = ResearchLaneService.from_settings(settings)

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
    ) -> ProductResponse:
        self._ensure_lanes()
        assert self._standard_lane is not None
        assert self._research_lane is not None

        context = self._bind_context(
            request=request,
            body=body,
            principal=principal,
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
            return self._standard_response(context=context, outcome=standard)

        if standard.status == StandardLaneStatus.RESEARCH_REQUIRED:
            # Isolation invariant: no StandardProjection, Standard semantic handles,
            # obligations or accepted Standard authority cross this call boundary.
            research = self._research_lane.run(
                context=context,
                body=body,
            )
            return self._research_response(
                context=context,
                result=research,
            )

        if standard.status == StandardLaneStatus.CLARIFICATION_REQUIRED:
            return self._terminal_standard(
                context=context,
                status=ProductStatus.CLARIFY,
                reasons=standard.reasons,
            )
        if standard.status == StandardLaneStatus.UNSUPPORTED:
            return self._terminal_standard(
                context=context,
                status=ProductStatus.UNSUPPORTED,
                reasons=standard.reasons,
            )
        return self._terminal_standard(
            context=context,
            status=ProductStatus.FAILED,
            reasons=standard.reasons
            or (f"standard lane terminal={standard.status.value}",),
        )

    @staticmethod
    def _standard_response(
        *,
        context: ProductRequestContext,
        outcome: StandardLaneOutcome,
    ) -> ProductResponse:
        assert outcome.execution is not None
        evidence = outcome.execution.evidence
        return ProductResponse(
            request_ref=context.request_ref,
            lane=ProductLane.STANDARD,
            status=ProductStatus.ANSWER,
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
    ) -> ProductResponse:
        return ProductResponse(
            request_ref=context.request_ref,
            lane=ProductLane.STANDARD,
            status=status,
            limitations=reasons,
            terminal_receipt=ProductTerminalReceipt(
                lane=ProductLane.STANDARD,
                status=status,
                verified_complete=False,
                terminal_status=status.value,
                reasons=reasons,
            ),
        )

    @staticmethod
    def _research_response(
        *,
        context: ProductRequestContext,
        result: ResearchLaneResult,
    ) -> ProductResponse:
        snapshot = result.runtime.snapshot
        evidence = tuple(_product_evidence(item) for item in result.evidence)
        limitations = tuple(
            dict.fromkeys(
                limitation
                for item in result.evidence
                for limitation in item.limitations
            )
        )

        if result.outcome.clarification_required:
            status = ProductStatus.CLARIFY
        elif result.verified_complete:
            # D10-B upgrades a completed Research lane to REPORT after deterministic
            # artifact/report projection. Until then this is explicitly partial product
            # integration, never a fake report.
            status = ProductStatus.PARTIAL
        elif result.outcome.terminal_status is not None:
            status = ProductStatus.PARTIAL
        else:
            status = ProductStatus.FAILED

        return ProductResponse(
            request_ref=context.request_ref,
            lane=ProductLane.RESEARCH,
            status=status,
            evidence_refs=evidence,
            limitations=limitations,
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
