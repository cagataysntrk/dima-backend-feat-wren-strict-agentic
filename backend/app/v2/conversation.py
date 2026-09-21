"""Day 4 typed conversation state and deterministic IR delta application.

The coordinator never parses raw user text. It consumes TurnInterpreter output,
SemanticResolver hypotheses, prior canonical AnalyticsIR and current schema metadata.
"""

from __future__ import annotations

import hashlib
from datetime import date

from app.v2.cube_planner import StandardAnalyticsError
from app.v2.models import (
    AnalyticsIR,
    ClarificationState,
    ComparisonSurface,
    ConversationStateV2,
    ExecutionResultV0,
    FocusStateV0,
    MinimumQueryContract,
    PendingAnalyticalStateV0,
    RequirementKind,
    RequirementLedger,
    RequirementLedgerItem,
    RequirementState,
    ResolvedFilterRef,
    ResolvedRanking,
    ResolvedSemanticRef,
    ResolutionStatus,
    ResultAnchorV0,
    ResultExecutionAnchorV0,
    SemanticAnchor,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMentionKind,
    SemanticTargetKind,
    StandardAnalyticsFailure,
    TopicFrameV0,
    TurnAct,
    TurnInterpretation,
)
from app.v2.temporal import TemporalResolutionError, resolve_comparison, resolve_period

_RESULT_STATE_ROW_LIMIT = 200
_LEDGER_PREFIX = (
    RequirementState.DETECTED,
    RequirementState.RESOLVED,
    RequirementState.REPRESENTED_IN_IR,
)


def _failure(code: str, message: str) -> StandardAnalyticsFailure:
    return StandardAnalyticsFailure(code=code, stage="conversation", message=message)


def _resolved_candidate(hypothesis: SemanticHypothesis | None) -> SemanticCandidate | None:
    if (
        hypothesis is None
        or hypothesis.status != ResolutionStatus.RESOLVED
        or not hypothesis.resolved_candidate_id
    ):
        return None
    return next(
        (
            candidate
            for candidate in hypothesis.candidates
            if candidate.candidate_id == hypothesis.resolved_candidate_id
        ),
        None,
    )


def _hypothesis(
    hypotheses: tuple[SemanticHypothesis, ...],
    *,
    text: str,
    kind: SemanticMentionKind,
) -> SemanticHypothesis | None:
    matches = [
        item
        for item in hypotheses
        if item.source_mention == text and item.mention_kind == kind
    ]
    return matches[0] if len(matches) == 1 else None


def _cube_meta(schema: dict, cube_name: str) -> dict | None:
    matches = [
        cube
        for cube in (schema.get("cubes") or ())
        if str(cube.get("name")) == cube_name
    ]
    return matches[0] if len(matches) == 1 else None


def _time_axis(cube: dict, prior_ir: AnalyticsIR) -> str:
    axes = tuple(str(value) for value in (cube.get("time_dimensions") or ()) if value)
    if prior_ir.period is not None and prior_ir.period.time_dimension in axes:
        return prior_ir.period.time_dimension
    if len(axes) == 1:
        return axes[0]
    if not axes:
        raise StandardAnalyticsError(
            _failure(
                "followup_cube_incompatible",
                f"Cube {prior_ir.cube} follow-up time requirement için time axis taşımıyor.",
            )
        )
    raise StandardAnalyticsError(
        _failure(
            "followup_cube_incompatible",
            f"Cube {prior_ir.cube} birden fazla time axis taşıyor; follow-up ilkini seçmez.",
        )
    )


def _semantic_ref(
    *,
    text: str,
    kind: SemanticMentionKind,
    hypotheses: tuple[SemanticHypothesis, ...],
    expected: SemanticTargetKind,
) -> ResolvedSemanticRef:
    hypothesis = _hypothesis(hypotheses, text=text, kind=kind)
    candidate = _resolved_candidate(hypothesis)
    if candidate is None or candidate.target_kind != expected:
        raise StandardAnalyticsError(
            _failure(
                "semantic_not_resolved",
                f"Follow-up slot canonical olarak resolve edilmedi: {text}",
            )
        )
    return ResolvedSemanticRef(
        candidate_id=candidate.candidate_id,
        target_kind=candidate.target_kind,
        canonical_name=candidate.canonical_name,
        cube_names=candidate.cube_names,
    )


def _filter_ref(
    *,
    text: str,
    hypotheses: tuple[SemanticHypothesis, ...],
) -> ResolvedFilterRef:
    hypothesis = _hypothesis(
        hypotheses,
        text=text,
        kind=SemanticMentionKind.FILTER,
    )
    candidate = _resolved_candidate(hypothesis)
    if (
        candidate is None
        or candidate.target_kind != SemanticTargetKind.ENTITY_VALUE
        or not candidate.dimension_name
    ):
        raise StandardAnalyticsError(
            _failure(
                "semantic_not_resolved",
                f"Follow-up filter exact entity-value olarak resolve edilmedi: {text}",
            )
        )
    value = candidate.value or (hypothesis.resolved_surface_value if hypothesis else None)
    if not value:
        raise StandardAnalyticsError(
            _failure("semantic_not_resolved", f"Follow-up filter değeri kayıp: {text}")
        )
    return ResolvedFilterRef(
        candidate_id=candidate.candidate_id,
        dimension_name=candidate.dimension_name,
        value=value,
        cube_names=candidate.cube_names,
        sensitive=candidate.sensitive,
    )


def _assert_cube_compatible(ir: AnalyticsIR, schema: dict) -> None:
    cube = _cube_meta(schema, ir.cube)
    if cube is None:
        raise StandardAnalyticsError(
            _failure("followup_cube_incompatible", f"Prior cube current schema'da yok: {ir.cube}")
        )
    measures = set(str(x) for x in (cube.get("measures") or ()))
    dimensions = set(str(x) for x in (cube.get("dimensions") or ()))
    missing = [
        *(f"metric:{ref.canonical_name}" for ref in ir.metrics if ref.canonical_name not in measures),
        *(
            f"dimension:{ref.canonical_name}"
            for ref in ir.dimensions
            if ref.canonical_name not in dimensions
        ),
        *(
            f"filter:{ref.dimension_name}"
            for ref in ir.filters
            if ref.dimension_name not in dimensions
        ),
    ]
    if ir.period is not None:
        axes = set(str(x) for x in (cube.get("time_dimensions") or ()))
        if ir.period.time_dimension not in axes:
            missing.append(f"time:{ir.period.time_dimension}")
    if missing:
        raise StandardAnalyticsError(
            _failure(
                "followup_cube_incompatible",
                "Prior cube current delta'yı taşıyamıyor; silent cross-cube coercion yok: "
                + ", ".join(missing),
            )
        )


def ledger_from_ir(ir: AnalyticsIR) -> RequirementLedger:
    """Create a full effective-request ledger after deterministic conversation patching."""
    items: list[RequirementLedgerItem] = []

    def add(requirement_id: str, kind: RequirementKind, source: str) -> None:
        items.append(
            RequirementLedgerItem(
                requirement_id=requirement_id,
                kind=kind,
                source_text=source,
                state=RequirementState.REPRESENTED_IN_IR,
                history=_LEDGER_PREFIX,
                detail="conversation effective IR",
            )
        )

    for i, metric in enumerate(ir.metrics):
        add(f"metric:{i}", RequirementKind.METRIC, metric.canonical_name)
    for i, dimension in enumerate(ir.dimensions):
        add(f"dimension:{i}", RequirementKind.DIMENSION, dimension.canonical_name)
    for i, filter_ref in enumerate(ir.filters):
        add(
            f"filter:{i}",
            RequirementKind.FILTER,
            f"{filter_ref.dimension_name}=<bound-value>",
        )
    if ir.period is not None:
        add("time:0", RequirementKind.TIME, ir.period.source_text)
    if ir.ranking is not None:
        add("ranking:direction", RequirementKind.RANKING_DIRECTION, ir.ranking.direction)
        add("ranking:limit", RequirementKind.LIMIT, str(ir.ranking.limit))
    if ir.comparison is not None:
        add("comparison:0", RequirementKind.COMPARISON, ir.comparison.source_text)
    return RequirementLedger(items=tuple(items))


class ConversationCoordinatorV0:
    def capture_pending(
        self,
        *,
        conversation: ConversationStateV2,
        turn: TurnInterpretation,
        hypotheses: tuple[SemanticHypothesis, ...],
        clarification: ClarificationState,
        context_version: str,
    ) -> ConversationStateV2:
        if turn.analytical_request is None:
            return conversation.model_copy(
                update={
                    "pending_clarification": True,
                    "clarification_state": clarification,
                }
            )
        pending = PendingAnalyticalStateV0(
            dialogue_act=turn.dialogue_act,
            analytical_request=turn.analytical_request,
            user_repair=turn.user_repair,
            hypotheses=hypotheses,
            clarification=clarification,
            base_ir=conversation.last_ir,
            context_version=context_version,
        )
        return conversation.model_copy(
            update={
                "pending_clarification": True,
                "clarification_state": clarification,
                "pending_analytical": pending,
            }
        )

    def refresh_pending_clarification(
        self,
        *,
        conversation: ConversationStateV2,
        clarification: ClarificationState,
    ) -> ConversationStateV2:
        pending = conversation.pending_analytical
        return conversation.model_copy(
            update={
                "pending_clarification": True,
                "clarification_state": clarification,
                "pending_analytical": (
                    pending.model_copy(update={"clarification": clarification})
                    if pending is not None
                    else None
                ),
            }
        )

    def restore_pending(
        self,
        *,
        conversation: ConversationStateV2,
        resumed_hypotheses: tuple[SemanticHypothesis, ...],
        context_version: str,
    ) -> tuple[TurnInterpretation, tuple[SemanticHypothesis, ...], AnalyticsIR | None]:
        pending = conversation.pending_analytical
        if pending is None:
            raise StandardAnalyticsError(
                _failure(
                    "pending_analytical_state_missing",
                    "Clarification semantic slot çözüldü ama original analytical state yok.",
                )
            )
        if pending.context_version != context_version:
            raise StandardAnalyticsError(
                _failure(
                    "clarification_state_mismatch",
                    "Pending analytical state current context_version ile uyuşmuyor.",
                )
            )

        replacements = {
            (item.source_mention, item.mention_kind): item
            for item in resumed_hypotheses
            if item.status == ResolutionStatus.RESOLVED
        }
        merged: list[SemanticHypothesis] = []
        replaced: set[tuple[str, SemanticMentionKind]] = set()
        for item in pending.hypotheses:
            key = (item.source_mention, item.mention_kind)
            if key in replacements:
                merged.append(replacements[key])
                replaced.add(key)
            else:
                merged.append(item)
        for key, item in replacements.items():
            if key not in replaced:
                merged.append(item)

        if not resumed_hypotheses or not all(
            item.status == ResolutionStatus.RESOLVED for item in resumed_hypotheses
        ):
            raise StandardAnalyticsError(
                _failure(
                    "clarification_state_mismatch",
                    "Clarification resume resolved hypothesis üretmedi.",
                )
            )

        turn = TurnInterpretation(
            dialogue_act=pending.dialogue_act,
            analytical_request=pending.analytical_request,
            user_repair=pending.user_repair,
        )
        return turn, tuple(merged), pending.base_ir

    def apply_delta(
        self,
        *,
        prior_ir: AnalyticsIR | None,
        turn: TurnInterpretation,
        hypotheses: tuple[SemanticHypothesis, ...],
        schema: dict,
        context_version: str,
        today: date | None = None,
    ) -> AnalyticsIR:
        if prior_ir is None:
            raise StandardAnalyticsError(
                _failure("no_prior_ir", "Follow-up/refinement için prior canonical IR yok.")
            )
        if prior_ir.context_version != context_version:
            raise StandardAnalyticsError(
                _failure(
                    "context_version_mismatch",
                    "Prior IR başka context_version ile üretildi; sessiz replay yapılmaz.",
                )
            )
        request = turn.analytical_request
        if request is None:
            raise StandardAnalyticsError(
                _failure(
                    "empty_refinement_delta",
                    "Refine/repair turunda typed analytical delta yok.",
                )
            )

        changed = False
        metrics = prior_ir.metrics
        dimensions = prior_ir.dimensions
        filters = prior_ir.filters
        period = prior_ir.period
        ranking = prior_ir.ranking
        comparison = prior_ir.comparison

        old_metrics = metrics
        if request.metric_mentions:
            metrics = tuple(
                _semantic_ref(
                    text=mention.text,
                    kind=SemanticMentionKind.METRIC,
                    hypotheses=hypotheses,
                    expected=SemanticTargetKind.METRIC,
                )
                for mention in request.metric_mentions
            )
            changed = True

        if request.dimension_mentions:
            dimensions = tuple(
                _semantic_ref(
                    text=mention.text,
                    kind=SemanticMentionKind.DIMENSION,
                    hypotheses=hypotheses,
                    expected=SemanticTargetKind.DIMENSION,
                )
                for mention in request.dimension_mentions
            )
            changed = True

        if request.filter_mentions:
            incoming = tuple(
                _filter_ref(text=mention.text, hypotheses=hypotheses)
                for mention in request.filter_mentions
            )
            replaced_dimensions = {item.dimension_name for item in incoming}
            filters = tuple(
                item for item in prior_ir.filters if item.dimension_name not in replaced_dimensions
            ) + incoming
            changed = True

        cube = _cube_meta(schema, prior_ir.cube)
        if cube is None:
            raise StandardAnalyticsError(
                _failure(
                    "followup_cube_incompatible",
                    f"Prior cube current schema'da yok: {prior_ir.cube}",
                )
            )

        time_changed = False
        if request.time_mentions:
            axis = _time_axis(cube, prior_ir)
            try:
                period = resolve_period(
                    request.time_mentions,
                    time_dimension=axis,
                    today=today,
                )
            except TemporalResolutionError as exc:
                raise StandardAnalyticsError(
                    _failure("unsupported_time", str(exc))
                ) from exc
            time_changed = True
            changed = True

        if request.ranking is not None:
            if (
                request.ranking.direction == "unspecified"
                or request.ranking.limit is None
                or len(metrics) != 1
                or not dimensions
            ):
                raise StandardAnalyticsError(
                    _failure(
                        "ranking_incomplete",
                        "Follow-up ranking direction+limit ve tek metric + breakdown ister.",
                    )
                )
            ranking = ResolvedRanking(
                measure=metrics[0].canonical_name,
                direction=request.ranking.direction,
                limit=request.ranking.limit,
            )
            changed = True
        elif metrics != old_metrics and ranking is not None:
            if len(old_metrics) == 1 and len(metrics) == 1 and ranking.measure == old_metrics[0].canonical_name:
                ranking = ranking.model_copy(update={"measure": metrics[0].canonical_name})
            else:
                raise StandardAnalyticsError(
                    _failure(
                        "empty_refinement_delta",
                        "Metric değişti fakat mevcut ranking criterion güvenle taşınamıyor.",
                    )
                )

        if request.comparisons:
            axis = _time_axis(cube, prior_ir)
            try:
                comparison = resolve_comparison(
                    request.comparisons,
                    base_period=period,
                    time_dimension=axis,
                    today=today,
                )
            except TemporalResolutionError as exc:
                raise StandardAnalyticsError(
                    _failure("unsupported_comparison", str(exc))
                ) from exc
            if comparison is not None:
                period = comparison.base_period
            changed = True
        elif time_changed and comparison is not None:
            try:
                comparison = resolve_comparison(
                    (ComparisonSurface(text=comparison.source_text),),
                    base_period=period,
                    time_dimension=_time_axis(cube, prior_ir),
                    today=today,
                )
            except TemporalResolutionError as exc:
                raise StandardAnalyticsError(
                    _failure(
                        "unsupported_comparison",
                        "Time repair mevcut comparison ile deterministic yeniden hizalanamadı: "
                        + str(exc),
                    )
                ) from exc

        if not changed:
            raise StandardAnalyticsError(
                _failure(
                    "empty_refinement_delta",
                    "Current turn prior IR üzerinde değiştirilecek typed slot taşımıyor.",
                )
            )

        updated = prior_ir.model_copy(
            update={
                "metrics": metrics,
                "dimensions": dimensions,
                "filters": filters,
                "period": period,
                "ranking": ranking,
                "comparison": comparison,
                "context_version": context_version,
            }
        )
        _assert_cube_compatible(updated, schema)
        return updated

    def state_after_verified(
        self,
        *,
        prior: ConversationStateV2,
        ir: AnalyticsIR,
        executions: tuple[ExecutionResultV0, ...],
        contracts: tuple[MinimumQueryContract, ...],
    ) -> ConversationStateV2:
        contract_refs = tuple(contract.contract_id for contract in contracts)
        topic_id = "topic-" + hashlib.sha256(
            f"{ir.context_version}|{ir.cube}".encode("utf-8")
        ).hexdigest()[:16]

        anchors: list[SemanticAnchor] = []
        anchors.extend(
            SemanticAnchor(
                target_kind=SemanticTargetKind.METRIC,
                canonical_name=item.canonical_name,
                display_label=item.canonical_name,
            )
            for item in ir.metrics
        )
        anchors.extend(
            SemanticAnchor(
                target_kind=SemanticTargetKind.DIMENSION,
                canonical_name=item.canonical_name,
                display_label=item.canonical_name,
            )
            for item in ir.dimensions
        )
        anchors.extend(
            SemanticAnchor(
                target_kind=SemanticTargetKind.ENTITY_VALUE,
                canonical_name=item.dimension_name,
                dimension_name=item.dimension_name,
                value=None if item.sensitive else item.value,
                display_label=item.dimension_name if item.sensitive else item.value,
                aliases=() if item.sensitive else (item.value,),
                sensitive=item.sensitive,
            )
            for item in ir.filters
        )

        result_anchor = ResultAnchorV0(
            contract_refs=contract_refs,
            result_hashes=tuple(
                contract.result_hash or "" for contract in contracts
            ),
            executions=tuple(
                ResultExecutionAnchorV0(
                    execution_id=result.execution_id,
                    role=result.role,
                    columns=result.columns,
                    rows=tuple(result.rows[:_RESULT_STATE_ROW_LIMIT]),
                    row_count=result.row_count,
                    truncated=result.row_count > _RESULT_STATE_ROW_LIMIT,
                )
                for result in executions
            ),
            verified=bool(contracts)
            and all(contract.sealed for contract in contracts)
            and all(result.verified for result in executions),
        )

        return prior.model_copy(
            update={
                "has_prior_analytical_request": True,
                "has_active_result": result_anchor.verified,
                "pending_clarification": False,
                "topic_labels": (ir.cube,),
                "focus_labels": tuple(
                    [
                        *(item.canonical_name for item in ir.metrics),
                        *(item.canonical_name for item in ir.dimensions),
                    ]
                ),
                "focus_anchors": tuple(anchors),
                "clarification_state": None,
                "topic": TopicFrameV0(
                    topic_id=topic_id,
                    cube=ir.cube,
                    context_version=ir.context_version,
                ),
                "focus": FocusStateV0(
                    metrics=ir.metrics,
                    dimensions=ir.dimensions,
                    filters=ir.filters,
                    period=ir.period,
                    last_contract_refs=contract_refs,
                ),
                "last_ir": ir,
                "last_result": result_anchor,
                "pending_analytical": None,
            }
        )

    def clear_pending(self, conversation: ConversationStateV2) -> ConversationStateV2:
        return conversation.model_copy(
            update={
                "pending_clarification": False,
                "clarification_state": None,
                "pending_analytical": None,
            }
        )
