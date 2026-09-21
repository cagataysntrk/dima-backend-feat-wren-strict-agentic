"""Day 3 canonical AnalyticsIR builder, RequirementLedger and CubePlanner.

No raw user question is accepted here. Language understanding belongs to TurnInterpreter;
semantic binding belongs to SemanticResolver; computational truth remains the current
cube/MDL schema and Wren compiler.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from app.v2.models import (
    AnalyticsIR,
    PlannedExecution,
    RequirementKind,
    RequirementLedger,
    RequirementLedgerItem,
    RequirementState,
    ResolvedFilterRef,
    ResolvedRanking,
    ResolvedSemanticRef,
    ResolutionStatus,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMentionKind,
    SemanticTargetKind,
    StandardAnalyticsFailure,
    TurnInterpretation,
)
from app.v2.temporal import (
    TemporalResolutionError,
    period_filters,
    resolve_comparison,
    resolve_period,
)

PLANNER_ID = "cube_planner"
PLANNER_VERSION = "v0.1-day3"

_LIFECYCLE = (
    RequirementState.DETECTED,
    RequirementState.RESOLVED,
    RequirementState.REPRESENTED_IN_IR,
    RequirementState.REPRESENTED_IN_PLAN,
    RequirementState.VERIFIED,
)


class StandardAnalyticsError(ValueError):
    def __init__(
        self,
        failure: StandardAnalyticsFailure,
        *,
        ledger: RequirementLedger | None = None,
    ):
        super().__init__(failure.message)
        self.failure = failure
        self.ledger = ledger


def _failure(code: str, stage: str, message: str) -> StandardAnalyticsFailure:
    return StandardAnalyticsFailure(code=code, stage=stage, message=message)


def _advance(
    ledger: RequirementLedger,
    requirement_ids: Iterable[str],
    state: RequirementState,
    *,
    detail: str | None = None,
) -> RequirementLedger:
    wanted = set(requirement_ids)
    items = []
    for item in ledger.items:
        if item.requirement_id not in wanted:
            items.append(item)
            continue
        history = item.history
        if not history:
            history = (RequirementState.DETECTED,)
        current_idx = _LIFECYCLE.index(history[-1]) if history[-1] in _LIFECYCLE else -1
        target_idx = _LIFECYCLE.index(state) if state in _LIFECYCLE else -1
        if state == RequirementState.BLOCKED:
            history = (*history, state)
        elif target_idx == current_idx + 1:
            history = (*history, state)
        elif target_idx == current_idx:
            pass
        else:
            raise StandardAnalyticsError(
                _failure(
                    "plan_validation_failed",
                    "ir",
                    f"Requirement lifecycle sırası atlandı: {item.requirement_id} "
                    f"{history[-1].value}->{state.value}",
                ),
                ledger=ledger,
            )
        items.append(
            item.model_copy(
                update={
                    "state": state,
                    "history": history,
                    "detail": detail if detail is not None else item.detail,
                }
            )
        )
    return RequirementLedger(items=tuple(items))


def _block(
    ledger: RequirementLedger,
    requirement_ids: Iterable[str],
    detail: str,
) -> RequirementLedger:
    wanted = set(requirement_ids)
    items = []
    for item in ledger.items:
        if item.requirement_id in wanted:
            items.append(
                item.model_copy(
                    update={
                        "state": RequirementState.BLOCKED,
                        "history": (*item.history, RequirementState.BLOCKED),
                        "detail": detail,
                    }
                )
            )
        else:
            items.append(item)
    return RequirementLedger(items=tuple(items))


def _ledger_from_turn(turn: TurnInterpretation) -> RequirementLedger:
    request = turn.analytical_request
    if request is None:
        return RequirementLedger()

    items: list[RequirementLedgerItem] = []
    for i, mention in enumerate(request.metric_mentions):
        items.append(
            RequirementLedgerItem(
                requirement_id=f"metric:{i}",
                kind=RequirementKind.METRIC,
                source_text=mention.text,
            )
        )
    for i, mention in enumerate(request.dimension_mentions):
        items.append(
            RequirementLedgerItem(
                requirement_id=f"dimension:{i}",
                kind=RequirementKind.DIMENSION,
                source_text=mention.text,
            )
        )
    for i, mention in enumerate(request.filter_mentions):
        items.append(
            RequirementLedgerItem(
                requirement_id=f"filter:{i}",
                kind=RequirementKind.FILTER,
                source_text=mention.text,
            )
        )
    for i, mention in enumerate(request.time_mentions):
        items.append(
            RequirementLedgerItem(
                requirement_id=f"time:{i}",
                kind=RequirementKind.TIME,
                source_text=mention.text,
            )
        )
    if request.ranking is not None:
        items.extend(
            (
                RequirementLedgerItem(
                    requirement_id="ranking:direction",
                    kind=RequirementKind.RANKING_DIRECTION,
                    source_text=request.ranking.text,
                ),
                RequirementLedgerItem(
                    requirement_id="ranking:limit",
                    kind=RequirementKind.LIMIT,
                    source_text=request.ranking.text,
                ),
            )
        )
    for i, comparison in enumerate(request.comparisons):
        items.append(
            RequirementLedgerItem(
                requirement_id=f"comparison:{i}",
                kind=RequirementKind.COMPARISON,
                source_text=comparison.text,
            )
        )
    return RequirementLedger(items=tuple(items))


def _resolved_candidate(hypothesis: SemanticHypothesis) -> SemanticCandidate | None:
    if (
        hypothesis.status != ResolutionStatus.RESOLVED
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


def _hypothesis_for(
    hypotheses: tuple[SemanticHypothesis, ...],
    *,
    source_text: str,
    mention_kind: SemanticMentionKind,
) -> SemanticHypothesis | None:
    exact = [
        hypothesis
        for hypothesis in hypotheses
        if hypothesis.source_mention == source_text
        and hypothesis.mention_kind == mention_kind
    ]
    return exact[0] if len(exact) == 1 else None


def _cube_index(schema: dict) -> dict[str, dict]:
    return {
        str(cube.get("name")): cube
        for cube in (schema.get("cubes") or ())
        if cube.get("name")
    }


def _supports(candidate: SemanticCandidate, cube: dict) -> bool:
    if candidate.target_kind == SemanticTargetKind.METRIC:
        return candidate.canonical_name in (cube.get("measures") or ())
    if candidate.target_kind == SemanticTargetKind.DIMENSION:
        return candidate.canonical_name in (cube.get("dimensions") or ())
    if candidate.target_kind == SemanticTargetKind.ENTITY_VALUE:
        return bool(candidate.dimension_name) and candidate.dimension_name in (
            cube.get("dimensions") or ()
        )
    return False


def _candidate_cubes(candidate: SemanticCandidate, schema: dict) -> set[str]:
    index = _cube_index(schema)
    declared = {name for name in candidate.cube_names if name in index}
    pool = declared or set(index)
    return {
        name
        for name in pool
        if _supports(candidate, index[name])
    }


def _single_viable_cube(
    candidates: Iterable[SemanticCandidate],
    schema: dict,
) -> tuple[str, dict]:
    index = _cube_index(schema)
    constraints: list[set[str]] = []
    for candidate in candidates:
        if candidate.target_kind == SemanticTargetKind.KPI:
            raise StandardAnalyticsError(
                _failure(
                    "unsupported_kpi",
                    "planner",
                    f"Cross-cube KPI Day3 tek-cube planner kapsamı dışında: "
                    f"{candidate.canonical_name}",
                )
            )
        cubes = _candidate_cubes(candidate, schema)
        if not cubes:
            raise StandardAnalyticsError(
                _failure(
                    "no_viable_cube",
                    "planner",
                    f"Resolved semantic ref current schema'da hiçbir cube tarafından "
                    f"taşınmıyor: {candidate.canonical_name}",
                )
            )
        constraints.append(cubes)

    viable = set(index)
    for constraint in constraints:
        viable &= constraint

    if not viable:
        raise StandardAnalyticsError(
            _failure(
                "no_viable_cube",
                "planner",
                "İstenen metric/dimension/filter requirement'larının tamamını taşıyan "
                "tek bir standard cube yok.",
            )
        )
    if len(viable) != 1:
        raise StandardAnalyticsError(
            _failure(
                "ambiguous_cube",
                "planner",
                "Birden fazla eşdeğer viable cube var; CubePlanner ilk adayı "
                "sessizce seçmez: " + ", ".join(sorted(viable)),
            )
        )

    name = next(iter(viable))
    return name, index[name]


def _require_time_axis(cube: dict) -> str:
    axes = tuple(str(x) for x in (cube.get("time_dimensions") or ()) if x)
    if not axes:
        raise StandardAnalyticsError(
            _failure(
                "missing_time_axis",
                "temporal",
                f"Cube {cube.get('name')} period/comparison için canonical time axis taşımıyor.",
            )
        )
    if len(axes) != 1:
        raise StandardAnalyticsError(
            _failure(
                "ambiguous_time_axis",
                "temporal",
                f"Cube {cube.get('name')} birden fazla time axis taşıyor; Day3 planner "
                "ilkini tahmin etmez: " + ", ".join(axes),
            )
        )
    return axes[0]


@dataclass(frozen=True)
class BuildOutput:
    ir: AnalyticsIR
    ledger: RequirementLedger


class AnalyticsIRBuilder:
    def build(
        self,
        *,
        turn: TurnInterpretation,
        hypotheses: tuple[SemanticHypothesis, ...],
        schema: dict,
        context_version: str,
        today: date | None = None,
    ) -> BuildOutput:
        request = turn.analytical_request
        ledger = _ledger_from_turn(turn)
        if request is None:
            raise StandardAnalyticsError(
                _failure("missing_metric", "ir", "AnalyticalRequest yok."),
                ledger=ledger,
            )
        if not request.metric_mentions:
            raise StandardAnalyticsError(
                _failure("missing_metric", "ir", "Standard analytics en az bir metric ister."),
                ledger=ledger,
            )

        chosen: list[tuple[str, SemanticCandidate, SemanticHypothesis]] = []

        def bind(
            requirement_id: str,
            source_text: str,
            kind: SemanticMentionKind,
        ) -> tuple[SemanticCandidate, SemanticHypothesis]:
            nonlocal ledger
            hypothesis = _hypothesis_for(
                hypotheses,
                source_text=source_text,
                mention_kind=kind,
            )
            candidate = _resolved_candidate(hypothesis) if hypothesis is not None else None
            if candidate is None:
                ledger = _block(
                    ledger,
                    (requirement_id,),
                    "SemanticResolver requirement'ı tek canonical candidate'a bağlamadı.",
                )
                raise StandardAnalyticsError(
                    _failure(
                        "semantic_not_resolved",
                        "ir",
                        f"Requirement canonical olarak resolve edilmedi: {source_text}",
                    ),
                    ledger=ledger,
                )
            ledger = _advance(
                ledger,
                (requirement_id,),
                RequirementState.RESOLVED,
                detail=f"candidate={candidate.candidate_id}",
            )
            chosen.append((requirement_id, candidate, hypothesis))
            return candidate, hypothesis

        metric_refs: list[ResolvedSemanticRef] = []
        metric_candidates: list[SemanticCandidate] = []
        for i, mention in enumerate(request.metric_mentions):
            candidate, _ = bind(f"metric:{i}", mention.text, SemanticMentionKind.METRIC)
            if candidate.target_kind == SemanticTargetKind.KPI:
                raise StandardAnalyticsError(
                    _failure(
                        "unsupported_kpi",
                        "planner",
                        f"KPI {candidate.canonical_name} Day3 standard CubePlanner kapsamı dışında.",
                    ),
                    ledger=ledger,
                )
            if candidate.target_kind != SemanticTargetKind.METRIC:
                raise StandardAnalyticsError(
                    _failure(
                        "plan_validation_failed",
                        "ir",
                        f"Metric mention metric candidate'a bağlanmadı: {candidate.target_kind}",
                    ),
                    ledger=ledger,
                )
            metric_candidates.append(candidate)
            metric_refs.append(
                ResolvedSemanticRef(
                    candidate_id=candidate.candidate_id,
                    target_kind=candidate.target_kind,
                    canonical_name=candidate.canonical_name,
                    cube_names=candidate.cube_names,
                )
            )

        dimension_refs: list[ResolvedSemanticRef] = []
        dimension_candidates: list[SemanticCandidate] = []
        for i, mention in enumerate(request.dimension_mentions):
            candidate, _ = bind(
                f"dimension:{i}",
                mention.text,
                SemanticMentionKind.DIMENSION,
            )
            if candidate.target_kind != SemanticTargetKind.DIMENSION:
                raise StandardAnalyticsError(
                    _failure(
                        "plan_validation_failed",
                        "ir",
                        f"Dimension mention dimension candidate'a bağlanmadı: "
                        f"{candidate.target_kind}",
                    ),
                    ledger=ledger,
                )
            dimension_candidates.append(candidate)
            dimension_refs.append(
                ResolvedSemanticRef(
                    candidate_id=candidate.candidate_id,
                    target_kind=candidate.target_kind,
                    canonical_name=candidate.canonical_name,
                    cube_names=candidate.cube_names,
                )
            )

        filter_refs: list[ResolvedFilterRef] = []
        filter_candidates: list[SemanticCandidate] = []
        for i, mention in enumerate(request.filter_mentions):
            candidate, hypothesis = bind(
                f"filter:{i}",
                mention.text,
                SemanticMentionKind.FILTER,
            )
            if (
                candidate.target_kind != SemanticTargetKind.ENTITY_VALUE
                or not candidate.dimension_name
            ):
                raise StandardAnalyticsError(
                    _failure(
                        "plan_validation_failed",
                        "ir",
                        f"Filter mention exact entity-value candidate'a bağlanmadı: "
                        f"{mention.text}",
                    ),
                    ledger=ledger,
                )
            value = candidate.value or hypothesis.resolved_surface_value
            if not value:
                raise StandardAnalyticsError(
                    _failure(
                        "plan_validation_failed",
                        "ir",
                        f"Resolved filter value taşınmıyor: {mention.text}",
                    ),
                    ledger=ledger,
                )
            filter_candidates.append(candidate)
            filter_refs.append(
                ResolvedFilterRef(
                    candidate_id=candidate.candidate_id,
                    dimension_name=candidate.dimension_name,
                    value=value,
                    cube_names=candidate.cube_names,
                    sensitive=candidate.sensitive,
                )
            )

        cube_name, cube_meta = _single_viable_cube(
            [*metric_candidates, *dimension_candidates, *filter_candidates],
            schema,
        )

        needs_time = bool(request.time_mentions or request.comparisons)
        time_dimension = _require_time_axis(cube_meta) if needs_time else ""

        try:
            period = resolve_period(
                request.time_mentions,
                time_dimension=time_dimension,
                today=today,
            )
            if request.time_mentions:
                for i in range(len(request.time_mentions)):
                    ledger = _advance(
                        ledger,
                        (f"time:{i}",),
                        RequirementState.RESOLVED,
                        detail=f"time_dimension={time_dimension}",
                    )

            comparison = resolve_comparison(
                request.comparisons,
                base_period=period,
                time_dimension=time_dimension,
                today=today,
            )
        except TemporalResolutionError as exc:
            relevant = [
                item.requirement_id
                for item in ledger.items
                if item.kind in {RequirementKind.TIME, RequirementKind.COMPARISON}
                and item.state != RequirementState.RESOLVED
            ]
            ledger = _block(ledger, relevant, str(exc))
            code = (
                "unsupported_comparison"
                if request.comparisons
                else "unsupported_time"
            )
            raise StandardAnalyticsError(
                _failure(code, "temporal", str(exc)),
                ledger=ledger,
            ) from exc

        if request.comparisons:
            for i in range(len(request.comparisons)):
                ledger = _advance(
                    ledger,
                    (f"comparison:{i}",),
                    RequirementState.RESOLVED,
                    detail="typed previous-period comparison",
                )
            if period is None and comparison is not None:
                period = comparison.base_period
                implicit = RequirementLedgerItem(
                    requirement_id="time:comparison-base",
                    kind=RequirementKind.TIME,
                    source_text=comparison.base_period.source_text,
                    state=RequirementState.RESOLVED,
                    history=(
                        RequirementState.DETECTED,
                        RequirementState.RESOLVED,
                    ),
                    detail="comparison semantics requires explicit base period",
                )
                ledger = RequirementLedger(items=(*ledger.items, implicit))

        ranking = None
        if request.ranking is not None:
            ranking_ids = ("ranking:direction", "ranking:limit")
            if (
                request.ranking.direction == "unspecified"
                or request.ranking.limit is None
                or len(metric_refs) != 1
                or not dimension_refs
            ):
                ledger = _block(
                    ledger,
                    ranking_ids,
                    "Ranking direction+limit ve tek metric + breakdown birlikte gerekir.",
                )
                raise StandardAnalyticsError(
                    _failure(
                        "ranking_incomplete",
                        "ir",
                        "Ranking semantiği eksik; direction/limit/criterion/breakdown "
                        "tahmin edilmeyecek.",
                    ),
                    ledger=ledger,
                )
            ledger = _advance(
                ledger,
                ranking_ids,
                RequirementState.RESOLVED,
                detail="ranking surface complete",
            )
            ranking = ResolvedRanking(
                measure=metric_refs[0].canonical_name,
                direction=request.ranking.direction,
                limit=request.ranking.limit,
            )

        ir = AnalyticsIR(
            cube=cube_name,
            metrics=tuple(metric_refs),
            dimensions=tuple(dimension_refs),
            filters=tuple(filter_refs),
            period=period,
            ranking=ranking,
            comparison=comparison,
            context_version=context_version,
        )

        ids = [
            item.requirement_id
            for item in ledger.items
            if item.state == RequirementState.RESOLVED
        ]
        ledger = _advance(
            ledger,
            ids,
            RequirementState.REPRESENTED_IN_IR,
            detail="canonical AnalyticsIR",
        )
        return BuildOutput(ir=ir, ledger=ledger)


def _cube_query(
    ir: AnalyticsIR,
    *,
    reference: bool = False,
    include_ranking: bool = True,
) -> dict:
    period = (
        ir.comparison.reference_period
        if reference and ir.comparison is not None
        else ir.period
    )
    query: dict = {
        "cube": ir.cube,
        "measures": [ref.canonical_name for ref in ir.metrics],
        "dimensions": [ref.canonical_name for ref in ir.dimensions],
        "filters": [
            {
                "dimension": ref.dimension_name,
                "operator": "eq",
                "value": ref.value,
            }
            for ref in ir.filters
        ]
        + period_filters(period),
    }
    if ir.ranking is not None and include_ranking:
        query["order"] = {
            "measure": ir.ranking.measure,
            "direction": ir.ranking.direction,
        }
        query["limit"] = ir.ranking.limit
    return query


def _execution_id(ir: AnalyticsIR, role: str, cube_query: dict) -> str:
    payload = repr((ir.context_version, role, cube_query)).encode("utf-8")
    return "x-" + hashlib.sha256(payload).hexdigest()[:16]


class CubePlanner:
    planner_id = PLANNER_ID
    planner_version = PLANNER_VERSION

    def plan(
        self,
        *,
        ir: AnalyticsIR,
        ledger: RequirementLedger,
        service,
    ) -> tuple[tuple[PlannedExecution, ...], RequirementLedger]:
        ranked_comparison = ir.comparison is not None and ir.ranking is not None
        queries = [("primary", _cube_query(ir, reference=False))]
        if ir.comparison is not None and not ranked_comparison:
            queries.append(
                (
                    "comparison_reference",
                    _cube_query(ir, reference=True, include_ranking=False),
                )
            )

        plans: list[PlannedExecution] = []
        for role, cube_query in queries:
            try:
                sql = service.cube_sql(cube_query)
            except Exception as exc:
                raise StandardAnalyticsError(
                    _failure(
                        "plan_validation_failed",
                        "planner",
                        f"Wren CubeQuery compile başarısız: {exc}",
                    ),
                    ledger=ledger,
                ) from exc
            plans.append(
                PlannedExecution(
                    execution_id=_execution_id(ir, role, cube_query),
                    role=role,
                    cube_query=cube_query,
                    sql=sql,
                )
            )

        represented = self._represented_requirements(ir, ledger, tuple(plans))
        deferred = {
            item.requirement_id
            for item in ledger.items
            if ranked_comparison and item.kind == RequirementKind.COMPARISON
        }
        missing = [
            item.requirement_id
            for item in ledger.items
            if item.must
            and item.requirement_id not in represented
            and item.requirement_id not in deferred
        ]
        if missing:
            ledger = _block(
                ledger,
                missing,
                "Requirement generated plan'da temsil edilmiyor.",
            )
            raise StandardAnalyticsError(
                _failure(
                    "plan_validation_failed",
                    "planner",
                    "MUST requirement plan'da kayboldu: " + ", ".join(missing),
                ),
                ledger=ledger,
            )

        active = [
            item.requirement_id
            for item in ledger.items
            if item.state == RequirementState.REPRESENTED_IN_IR
            and item.requirement_id in represented
        ]
        ledger = _advance(
            ledger,
            active,
            RequirementState.REPRESENTED_IN_PLAN,
            detail=f"{len(plans)} deterministic CubeQuery execution",
        )
        return tuple(plans), ledger

    def plan_ranked_comparison_reference(
        self,
        *,
        ir: AnalyticsIR,
        ledger: RequirementLedger,
        primary_result: dict,
        service,
    ) -> tuple[PlannedExecution, RequirementLedger]:
        """Plan the reference period against the exact base top-N member set.

        Ranking decides the member set on the base period. Running an independent top-N on
        the reference period would compare different entities and is therefore forbidden.
        The reference query is compiled only after the verified-shape base result exposes
        the selected member values.
        """
        if ir.ranking is None or ir.comparison is None:
            raise StandardAnalyticsError(
                _failure(
                    "plan_validation_failed",
                    "planner",
                    "Dependent comparison plan requires both ranking and comparison.",
                ),
                ledger=ledger,
            )
        if len(ir.dimensions) != 1:
            raise StandardAnalyticsError(
                _failure(
                    "plan_validation_failed",
                    "planner",
                    "Ranked comparison Core MVP requires exactly one breakdown dimension; "
                    "multi-dimensional tuple alignment is not guessed.",
                ),
                ledger=ledger,
            )

        dimension = ir.dimensions[0].canonical_name
        rows = tuple(primary_result.get("rows") or ())
        selected: list[object] = []
        seen: set[object] = set()
        for row in rows:
            if dimension not in row:
                raise StandardAnalyticsError(
                    _failure(
                        "plan_validation_failed",
                        "planner",
                        f"Base top-N result alignment dimension missing: {dimension}",
                    ),
                    ledger=ledger,
                )
            value = row.get(dimension)
            if value is None or value in seen:
                continue
            seen.add(value)
            selected.append(value)

        if not selected:
            raise StandardAnalyticsError(
                _failure(
                    "plan_validation_failed",
                    "planner",
                    "Base top-N result returned no alignable members; reference comparison "
                    "is not executed against an invented entity set.",
                ),
                ledger=ledger,
            )

        cube_query = _cube_query(ir, reference=True, include_ranking=False)
        cube_query["filters"] = [
            *(cube_query.get("filters") or ()),
            {
                "dimension": dimension,
                "operator": "in",
                "value": selected,
            },
        ]
        try:
            sql = service.cube_sql(cube_query)
        except Exception as exc:
            raise StandardAnalyticsError(
                _failure(
                    "plan_validation_failed",
                    "planner",
                    f"Wren aligned comparison CubeQuery compile başarısız: {exc}",
                ),
                ledger=ledger,
            ) from exc

        plan = PlannedExecution(
            execution_id=_execution_id(ir, "comparison_reference", cube_query),
            role="comparison_reference",
            cube_query=cube_query,
            sql=sql,
        )
        comparison_ids = [
            item.requirement_id
            for item in ledger.items
            if item.kind == RequirementKind.COMPARISON
            and item.state == RequirementState.REPRESENTED_IN_IR
        ]
        ledger = _advance(
            ledger,
            comparison_ids,
            RequirementState.REPRESENTED_IN_PLAN,
            detail="reference period aligned to base ranked member set",
        )
        return plan, ledger

    def _represented_requirements(
        self,
        ir: AnalyticsIR,
        ledger: RequirementLedger,
        plans: tuple[PlannedExecution, ...],
    ) -> set[str]:
        if not plans:
            return set()
        primary = plans[0].cube_query
        represented: set[str] = set()

        def index_of(requirement_id: str) -> int | None:
            try:
                return int(requirement_id.rsplit(":", 1)[1])
            except (TypeError, ValueError):
                return None

        actual_eq = {
            (str(f.get("dimension")), str(f.get("value")))
            for f in (primary.get("filters") or ())
            if f.get("operator") == "eq"
        }
        actual_filters = tuple(primary.get("filters") or ())

        for item in ledger.items:
            idx = index_of(item.requirement_id)

            if item.kind == RequirementKind.METRIC and idx is not None:
                if (
                    idx < len(ir.metrics)
                    and ir.metrics[idx].canonical_name in (primary.get("measures") or ())
                ):
                    represented.add(item.requirement_id)

            elif item.kind == RequirementKind.DIMENSION and idx is not None:
                if (
                    idx < len(ir.dimensions)
                    and ir.dimensions[idx].canonical_name in (primary.get("dimensions") or ())
                ):
                    represented.add(item.requirement_id)

            elif item.kind == RequirementKind.FILTER and idx is not None:
                if idx < len(ir.filters):
                    expected = ir.filters[idx]
                    if (expected.dimension_name, expected.value) in actual_eq:
                        represented.add(item.requirement_id)

            elif item.kind == RequirementKind.TIME:
                target = ir.period
                if target is not None and all(
                    expected in actual_filters for expected in period_filters(target)
                ):
                    represented.add(item.requirement_id)

            elif item.kind == RequirementKind.RANKING_DIRECTION:
                order = primary.get("order") or {}
                if (
                    ir.ranking is not None
                    and order.get("direction") == ir.ranking.direction
                    and order.get("measure") == ir.ranking.measure
                ):
                    represented.add(item.requirement_id)

            elif item.kind == RequirementKind.LIMIT:
                if ir.ranking is not None and primary.get("limit") == ir.ranking.limit:
                    represented.add(item.requirement_id)

            elif item.kind == RequirementKind.COMPARISON:
                if ir.comparison is not None and len(plans) == 2:
                    reference_filters = tuple(plans[1].cube_query.get("filters") or ())
                    if all(
                        expected in reference_filters
                        for expected in period_filters(ir.comparison.reference_period)
                    ):
                        represented.add(item.requirement_id)

        return represented



class ResultValidator:
    def validate(
        self,
        *,
        ir: AnalyticsIR,
        ledger: RequirementLedger,
        plans: tuple[PlannedExecution, ...],
        results: tuple[dict, ...],
    ) -> tuple[RequirementLedger, tuple[tuple[str, ...], ...]]:
        if len(plans) != len(results):
            raise StandardAnalyticsError(
                _failure(
                    "result_validation_failed",
                    "result_validation",
                    "Plan/result execution sayısı uyuşmuyor.",
                ),
                ledger=ledger,
            )

        errors_by_result: list[tuple[str, ...]] = []
        for plan, result in zip(plans, results):
            errors: list[str] = []
            columns = set(str(c) for c in (result.get("columns") or ()))
            expected_columns = {
                *(metric.canonical_name for metric in ir.metrics),
                *(dimension.canonical_name for dimension in ir.dimensions),
            }
            missing_columns = expected_columns - columns
            if missing_columns:
                errors.append("missing columns: " + ", ".join(sorted(missing_columns)))

            if ir.ranking is not None and plan.role == "primary":
                if int(result.get("row_count") or 0) > ir.ranking.limit:
                    errors.append("semantic top-N limit exceeded")
                values = [
                    row.get(ir.ranking.measure)
                    for row in (result.get("rows") or ())
                    if isinstance(row.get(ir.ranking.measure), (int, float))
                ]
                if len(values) >= 2:
                    pairs = zip(values, values[1:])
                    ordered = (
                        all(a <= b for a, b in pairs)
                        if ir.ranking.direction == "asc"
                        else all(a >= b for a, b in pairs)
                    )
                    if not ordered:
                        errors.append("ranking direction not preserved in result")

            errors_by_result.append(tuple(errors))

        if (
            ir.ranking is not None
            and ir.comparison is not None
            and len(plans) == 2
            and len(results) == 2
            and len(ir.dimensions) == 1
        ):
            dimension = ir.dimensions[0].canonical_name
            base_members = {
                row.get(dimension)
                for row in (results[0].get("rows") or ())
                if row.get(dimension) is not None
            }
            reference_members = {
                row.get(dimension)
                for row in (results[1].get("rows") or ())
                if row.get(dimension) is not None
            }
            leaked_members = reference_members - base_members
            if leaked_members:
                errors_by_result[1] = (
                    *errors_by_result[1],
                    "ranked comparison reference contains members outside base top-N",
                )

        global_errors = [error for errors in errors_by_result for error in errors]
        if global_errors:
            raise StandardAnalyticsError(
                _failure(
                    "result_validation_failed",
                    "result_validation",
                    "; ".join(global_errors),
                ),
                ledger=ledger,
            )

        active = [
            item.requirement_id
            for item in ledger.items
            if item.state == RequirementState.REPRESENTED_IN_PLAN
        ]
        ledger = _advance(
            ledger,
            active,
            RequirementState.VERIFIED,
            detail="plan + Wren result validated",
        )
        if not ledger.all_must_verified:
            raise StandardAnalyticsError(
                _failure(
                    "result_validation_failed",
                    "result_validation",
                    "Tüm MUST requirement'lar VERIFIED durumuna ulaşmadı.",
                ),
                ledger=ledger,
            )
        return ledger, tuple(errors_by_result)
