"""First real Fast Ask orchestration service.

Cognition is bounded. Resource/field authority, temporal arithmetic, query construction,
execution, evidence, and numeric answers remain deterministic.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from app.fast.ask_cognition import FastCognition
from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import (
    AggregationKind,
    AskOutcomeStatus,
    DraftStatus,
    FastAskErrorPayload,
    FastAskRequest,
    FastAskResponse,
    FieldCandidate,
    ResourceCandidate,
    SelectionPurpose,
    TemporalKind,
)
from app.fast.evidence import (
    build_evidence,
    deterministic_answer,
    normalize_execution,
)
from app.fast.metabase_errors import FastMetabaseError
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.query_builder import build_portable_query
from app.fast.resource_registry import ResourceRegistry
from app.fast.temporal import bind_temporal


class GatewayFactory(Protocol):
    def __call__(self, principal: Any) -> FastMetabaseGateway:
        ...


_CLARIFICATION_CODES = {
    FastAskErrorCode.CLARIFICATION_REQUIRED,
    FastAskErrorCode.NO_RESOURCE,
    FastAskErrorCode.AMBIGUOUS_RESOURCE,
    FastAskErrorCode.NO_MEASURE_FIELD,
    FastAskErrorCode.NO_TEMPORAL_FIELD,
    FastAskErrorCode.NO_BREAKDOWN_FIELD,
    FastAskErrorCode.TEMPORAL_ANCHOR_REQUIRED,
}


def _non_success(question: str, error: FastAskError) -> FastAskResponse:
    if error.code == FastAskErrorCode.UNSUPPORTED:
        status = AskOutcomeStatus.UNSUPPORTED
    elif error.code in _CLARIFICATION_CODES:
        status = AskOutcomeStatus.CLARIFICATION_REQUIRED
    else:
        status = AskOutcomeStatus.FAILED
    return FastAskResponse(
        status=status,
        question=question,
        error=FastAskErrorPayload(code=error.code.value, message=error.message),
    )


def _selected_handle(
    *,
    decision_handle: str | None,
    offered_handles: set[str],
    missing_code: FastAskErrorCode,
    missing_message: str,
) -> str:
    if decision_handle is None:
        raise FastAskError(missing_code, missing_message)
    if decision_handle not in offered_handles:
        raise FastAskError(
            FastAskErrorCode.COGNITION_INVALID,
            "cognition selected a handle that was not offered",
        )
    return decision_handle


class FastAskService:
    def __init__(
        self,
        *,
        cognition: FastCognition,
        gateway_factory: GatewayFactory,
        max_resource_candidates: int = 8,
    ) -> None:
        if max_resource_candidates < 1 or max_resource_candidates > 20:
            raise ValueError("max_resource_candidates must be in 1..20")
        self._cognition = cognition
        self._gateway_factory = gateway_factory
        self._max_resource_candidates = max_resource_candidates

    def ask(self, request: FastAskRequest, *, principal: Any) -> FastAskResponse:
        question = request.question.strip()
        try:
            draft = self._cognition.draft(question=question)
            if draft.status == DraftStatus.UNSUPPORTED:
                raise FastAskError(
                    FastAskErrorCode.UNSUPPORTED,
                    draft.unsupported_reason or "request is outside the FT-003 supported family",
                )
            temporal_window = bind_temporal(
                draft.temporal,
                as_of_date=request.as_of_date,
            )

            with self._gateway_factory(principal) as gateway:
                search = gateway.search(
                    term_queries=draft.search_terms,
                    semantic_queries=(question,),
                )
                registry = ResourceRegistry(
                    search.data,
                    max_candidates=self._max_resource_candidates,
                )
                if not registry.candidates:
                    raise FastAskError(
                        FastAskErrorCode.NO_RESOURCE,
                        "Metabase metadata search returned no supported table candidate",
                    )

                resource_decision = self._cognition.select_resource(
                    question=question,
                    candidates=registry.candidates,
                )
                offered_resources = {item.handle for item in registry.candidates}
                if (
                    resource_decision.selected_handle is not None
                    and resource_decision.selected_handle not in offered_resources
                ):
                    raise FastAskError(
                        FastAskErrorCode.COGNITION_INVALID,
                        "cognition selected a handle that was not offered",
                    )
                if len(registry.candidates) > 1:
                    raise FastAskError(
                        FastAskErrorCode.AMBIGUOUS_RESOURCE,
                        "multiple permitted resources remain plausible; clarification required",
                    )
                resource_handle = _selected_handle(
                    decision_handle=resource_decision.selected_handle,
                    offered_handles=offered_resources,
                    missing_code=FastAskErrorCode.CLARIFICATION_REQUIRED,
                    missing_message="resource selection requires clarification",
                )

                resource_uri = registry.resource_uri(resource_handle)
                details_response = gateway.read_resource((resource_uri + "/fields",))
                details_item = details_response.resources[0]
                if details_item.failed or details_item.content is None:
                    raise FastAskError(
                        FastAskErrorCode.NO_RESOURCE,
                        "selected Metabase resource cannot expose permitted fields",
                    )
                details = details_item.content.structured_output
                if not isinstance(details, dict):
                    raise FastAskError(
                        FastAskErrorCode.RESULT_CONTRACT_INVALID,
                        "Metabase fields resource has no structured output",
                    )
                fields = registry.bind_table_details(resource_handle, details)

                selected_fields: dict[str, Any] = {}
                measure = None
                if draft.aggregation == AggregationKind.SUM:
                    measure_candidates = fields.public_for_measure()
                    measure = self._choose_field(
                        question=question,
                        purpose=SelectionPurpose.MEASURE,
                        hint=draft.measure_hint or "",
                        candidates=measure_candidates,
                        fields=fields,
                        missing_code=FastAskErrorCode.NO_MEASURE_FIELD,
                    )
                    selected_fields["measure"] = measure

                temporal_field = None
                if draft.temporal.kind != TemporalKind.NONE:
                    temporal_candidates = fields.public_for_temporal()
                    temporal_field = self._choose_field(
                        question=question,
                        purpose=SelectionPurpose.TEMPORAL,
                        hint="date/time field relevant to the user's requested period",
                        candidates=temporal_candidates,
                        fields=fields,
                        missing_code=FastAskErrorCode.NO_TEMPORAL_FIELD,
                    )
                    selected_fields["temporal"] = temporal_field

                breakdown = None
                if (draft.breakdown_hint or "").strip():
                    breakdown_candidates = fields.public_for_breakdown()
                    breakdown = self._choose_field(
                        question=question,
                        purpose=SelectionPurpose.BREAKDOWN,
                        hint=draft.breakdown_hint or "",
                        candidates=breakdown_candidates,
                        fields=fields,
                        missing_code=FastAskErrorCode.NO_BREAKDOWN_FIELD,
                    )
                    selected_fields["breakdown"] = breakdown

                portable_query = build_portable_query(
                    draft=draft,
                    table=fields.table,
                    measure=measure,
                    temporal_field=temporal_field,
                    breakdown=breakdown,
                    temporal_window=temporal_window,
                )
                constructed = gateway.construct_query(portable_query)
                executed = gateway.execute_serialized(constructed)
                result = normalize_execution(executed)

                evidence = build_evidence(
                    question=question,
                    table=fields.table,
                    fields=selected_fields,
                    temporal_window=temporal_window,
                    portable_query=portable_query,
                    access_fingerprint=gateway.access_fingerprint.digest,
                    metabase_runtime_version=gateway.policy.runtime_version,
                    result=result,
                )
                answer = deterministic_answer(
                    aggregation=draft.aggregation,
                    breakdown=breakdown,
                    result=result,
                )
                return FastAskResponse(
                    status=AskOutcomeStatus.SUCCESS,
                    question=question,
                    answer=answer,
                    result=result,
                    evidence=evidence,
                )
        except FastAskError as error:
            return _non_success(question, error)
        except FastMetabaseError as error:
            return FastAskResponse(
                status=AskOutcomeStatus.FAILED,
                question=question,
                error=FastAskErrorPayload(
                    code=error.code.value,
                    message="analytics engine request failed",
                ),
            )

    def _choose_field(
        self,
        *,
        question: str,
        purpose: SelectionPurpose,
        hint: str,
        candidates: tuple[FieldCandidate, ...],
        fields,
        missing_code: FastAskErrorCode,
    ):
        if not candidates:
            raise FastAskError(missing_code, f"no permitted {purpose.value.lower()} field candidate")
        decision = self._cognition.select_field(
            question=question,
            purpose=purpose,
            hint=hint,
            candidates=candidates,
        )
        handle = _selected_handle(
            decision_handle=decision.selected_handle,
            offered_handles={item.handle for item in candidates},
            missing_code=missing_code,
            missing_message=f"{purpose.value.lower()} field selection requires clarification",
        )
        return fields.resolve(handle)
