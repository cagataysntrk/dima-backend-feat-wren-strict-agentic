"""Deterministic Requirement -> MaterialGroup execution projection.

Accepted ResearchBrief/AnalyticalRequestContract remain semantic authority.
MaterialGroup is transient execution metadata only: it binds one minimum
governed native material need to the USER_MUST analytical requirements that
consume it. No SQL/MBQL planning or second semantic truth lives here.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.research_analytical_scope import (
    analytical_scope_contract,
    coorigin_material_requirements,
)
from app.v3.research_contracts import ResearchGoalKind


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MaterialPeriodRef(Frozen):
    role: Literal["PERIOD", "BASE", "REFERENCE"]
    time_dimension_ref: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str | None = None


class MaterialFilterRef(Frozen):
    semantic_ref: str = Field(min_length=1)
    dimension_name: str = Field(min_length=1)
    value: str


class MaterialGroup(Frozen):
    """Thin deterministic execution projection, never semantic authority."""

    material_group_id: str = Field(pattern=r"^mg_[a-f0-9]{24}$")
    anchor_requirement_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    consumer_requirement_ids: tuple[str, ...] = Field(min_length=1)
    dependency_requirement_ids: tuple[str, ...] = ()
    required_metric_refs: tuple[str, ...] = Field(min_length=1)
    required_dimension_refs: tuple[str, ...] = ()
    required_periods: tuple[MaterialPeriodRef, ...] = ()
    required_filters: tuple[MaterialFilterRef, ...] = ()
    material_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def coherent_identity(self):
        if len(self.consumer_requirement_ids) != len(
            set(self.consumer_requirement_ids)
        ):
            raise ValueError("MaterialGroup consumer requirement refs must be unique")
        if len(self.dependency_requirement_ids) != len(
            set(self.dependency_requirement_ids)
        ):
            raise ValueError("MaterialGroup dependency refs must be unique")
        if set(self.dependency_requirement_ids).intersection(
            self.consumer_requirement_ids
        ):
            raise ValueError("MaterialGroup cannot depend on one of its own consumers")
        if len(self.required_metric_refs) != len(set(self.required_metric_refs)):
            raise ValueError("MaterialGroup metric refs must be unique")
        if len(self.required_dimension_refs) != len(
            set(self.required_dimension_refs)
        ):
            raise ValueError("MaterialGroup dimension refs must be unique")
        if self.anchor_requirement_id not in set(self.consumer_requirement_ids):
            raise ValueError("MaterialGroup anchor must be one of its consumers")
        return self


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def _periods(contract) -> tuple[MaterialPeriodRef, ...]:
    if contract.comparison is not None:
        return (
            MaterialPeriodRef(
                role="BASE",
                time_dimension_ref=contract.comparison.base_period.time_dimension,
                start=contract.comparison.base_period.start,
                end=contract.comparison.base_period.end,
            ),
            MaterialPeriodRef(
                role="REFERENCE",
                time_dimension_ref=(
                    contract.comparison.reference_period.time_dimension
                ),
                start=contract.comparison.reference_period.start,
                end=contract.comparison.reference_period.end,
            ),
        )
    if contract.period is not None:
        return (
            MaterialPeriodRef(
                role="PERIOD",
                time_dimension_ref=contract.period.time_dimension,
                start=contract.period.start,
                end=contract.period.end,
            ),
        )
    return ()


def _filters(contract) -> tuple[MaterialFilterRef, ...]:
    return tuple(
        MaterialFilterRef(
            semantic_ref=item.semantic_ref,
            dimension_name=item.dimension_name,
            value=item.value,
        )
        for item in contract.filters
    )


def _execution_contract(*, session, obligation_id: str):
    return analytical_scope_contract(
        session=session,
        obligation_id=obligation_id,
    ).model_copy(update={"requested_output_surfaces": ()})


def _acquisition_base(contract) -> str:
    """Identity of one governed acquisition before consumer ranking facets."""

    payload = {
        "semantic_context_version": contract.semantic_context_version,
        "scope_identity": contract.scope_identity.model_dump(mode="json"),
        "scope_fingerprint": contract.scope_fingerprint,
        "metric_refs": sorted(contract.metric_refs),
        "dimension_refs": sorted(contract.dimension_refs),
        "filters": sorted(
            (item.model_dump(mode="json") for item in contract.filters),
            key=lambda item: (
                item["semantic_ref"],
                item["source_candidate_id"],
                item["dimension_name"],
                item["value"],
            ),
        ),
        "period": (
            contract.period.model_dump(mode="json")
            if contract.period is not None else None
        ),
        "comparison": (
            contract.comparison.model_dump(mode="json")
            if contract.comparison is not None else None
        ),
        "temporal_observation": (
            contract.temporal_observation.model_dump(mode="json")
            if contract.temporal_observation is not None else None
        ),
        "grain_constraints": sorted(contract.grain_constraints),
    }
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _ranking_family(contract) -> str | None:
    ranking = contract.ranking
    if ranking is None or getattr(ranking, "kind", None) != "native_metric":
        return None
    value = ranking.model_dump(mode="json")
    value["limit"] = None
    payload = {
        "ranking": value,
        "temporal_change_frame": (
            contract.temporal_change_frame.model_dump(mode="json")
            if contract.temporal_change_frame is not None else None
        ),
    }
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _shared_direct_clusters(session) -> tuple[tuple[str, ...], ...]:
    """Find exact comparison/ranking siblings that can share one acquisition."""

    brief = session.accepted_brief
    assert brief is not None
    by_base: dict[str, list[tuple[str, str | None]]] = {}
    for question in brief.questions:
        if (
            question.kind not in {ResearchGoalKind.COMPARISON, ResearchGoalKind.RANKING}
            or question.result_dependency is not None
        ):
            continue
        contract = _execution_contract(
            session=session,
            obligation_id=question.goal_id,
        )
        family = _ranking_family(contract)
        if question.kind == ResearchGoalKind.RANKING and family is None:
            continue
        by_base.setdefault(_acquisition_base(contract), []).append(
            (question.goal_id, family)
        )

    clusters: list[tuple[str, ...]] = []
    for items in by_base.values():
        families = {family for _, family in items if family is not None}
        comparisons = tuple(goal_id for goal_id, family in items if family is None)
        if len(families) == 1:
            (family,) = tuple(families)
            members = tuple(
                sorted(
                    goal_id
                    for goal_id, item_family in items
                    if item_family in {None, family}
                )
            )
            if len(members) > 1:
                clusters.append(members)
            continue
        # Ambiguous ranking families never borrow comparison authority.
        for family in sorted(families):
            members = tuple(
                sorted(
                    goal_id
                    for goal_id, item_family in items
                    if item_family == family
                )
            )
            if len(members) > 1:
                clusters.append(members)
        del comparisons
    return tuple(sorted(clusters))


def _shared_acquisition_contract(*, session, consumers: tuple[str, ...]):
    brief = session.accepted_brief
    assert brief is not None
    by_id = {item.goal_id: item for item in brief.questions}
    questions = tuple(by_id[item] for item in consumers)
    if not questions or any(
        item.kind not in {ResearchGoalKind.COMPARISON, ResearchGoalKind.RANKING}
        or item.result_dependency is not None
        for item in questions
    ):
        return None, None

    contracts = {
        item.goal_id: _execution_contract(
            session=session,
            obligation_id=item.goal_id,
        )
        for item in questions
    }
    if len({_acquisition_base(item) for item in contracts.values()}) != 1:
        return None, None

    ranked = tuple(
        (goal_id, contract)
        for goal_id, contract in contracts.items()
        if _ranking_family(contract) is not None
    )
    if not ranked or len({_ranking_family(item) for _, item in ranked}) != 1:
        return None, None

    # Prefer an unbounded ranking contract. Otherwise choose the widest top-k.
    def priority(item):
        goal_id, contract = item
        limit = contract.ranking.limit
        return (0 if limit is None else 1, -(limit or 0), goal_id)

    anchor, base = sorted(ranked, key=priority)[0]
    limits = tuple(contract.ranking.limit for _, contract in ranked)
    comparison_present = any(
        item.kind == ResearchGoalKind.COMPARISON for item in questions
    )
    limit = (
        None
        if comparison_present or any(value is None for value in limits)
        else max(value for value in limits if value is not None)
    )
    return anchor, base.model_copy(
        update={"ranking": base.ranking.model_copy(update={"limit": limit})}
    )


def _group(*, session, anchor_requirement_id: str, consumers: tuple[str, ...]):
    brief = session.accepted_brief
    if brief is None:
        raise ValueError("MaterialGroup projection requires accepted ResearchBrief")
    consumer_ids = tuple(sorted(dict.fromkeys(consumers)))
    questions_by_id = {item.goal_id: item for item in brief.questions}
    dependency_ids = tuple(
        sorted(
            {
                question.result_dependency.source_goal_id
                for consumer_id in consumer_ids
                if (question := questions_by_id.get(consumer_id)) is not None
                and question.result_dependency is not None
            }
        )
    )
    shared_anchor, shared_contract = _shared_acquisition_contract(
        session=session,
        consumers=consumer_ids,
    )
    if shared_contract is not None:
        anchor_requirement_id = shared_anchor
        execution_contract = shared_contract
    else:
        execution_contract = _execution_contract(
            session=session,
            obligation_id=anchor_requirement_id,
        )
    material_fingerprint = execution_contract.material_fingerprint
    identity = {
        "tenant_binding": getattr(session, "tenant_binding", ""),
        "principal_subject": getattr(session, "principal_subject", ""),
        "lineage_id": getattr(session, "lineage_id", ""),
        "authority_revision": getattr(session, "authority_revision", 1),
        "semantic_context_version": execution_contract.semantic_context_version,
        "scope_version_id": brief.scope.scope_version.version_id,
        "scope_fingerprint": execution_contract.scope_fingerprint,
        "material_fingerprint": material_fingerprint,
        "dependency_requirement_ids": list(dependency_ids),
    }
    digest = hashlib.sha256(_canonical(identity).encode("utf-8")).hexdigest()
    return MaterialGroup(
        material_group_id="mg_" + digest[:24],
        anchor_requirement_id=anchor_requirement_id,
        scope_version_id=brief.scope.scope_version.version_id,
        consumer_requirement_ids=consumer_ids,
        dependency_requirement_ids=dependency_ids,
        required_metric_refs=tuple(dict.fromkeys(execution_contract.metric_refs)),
        required_dimension_refs=tuple(dict.fromkeys(execution_contract.dimension_refs)),
        required_periods=_periods(execution_contract),
        required_filters=_filters(execution_contract),
        material_fingerprint=material_fingerprint,
    )


def material_group_acquisition_contract(*, session, group: MaterialGroup):
    """Re-project the exact accepted-WHAT acquisition envelope for a group."""

    _, shared = _shared_acquisition_contract(
        session=session,
        consumers=group.consumer_requirement_ids,
    )
    contract = shared or _execution_contract(
        session=session,
        obligation_id=group.anchor_requirement_id,
    )
    if contract.material_fingerprint != group.material_fingerprint:
        raise ValueError("MaterialGroup acquisition contract fingerprint drift")
    return contract


def project_material_groups(session) -> tuple[MaterialGroup, ...]:
    """Project analytical USER_MUSTs into minimum governed acquisitions.

    Acquisition identity is distinct from consumer fulfillment identity.
    Ranking/top-k facets may share one acquisition only when canonical metric,
    filters, periods, grain, scope/currentness and dependency boundary match.
    """

    brief = session.accepted_brief
    if brief is None:
        raise ValueError("MaterialGroup projection requires accepted ResearchBrief")

    questions_by_id = {item.goal_id: item for item in brief.questions}
    assigned: set[str] = set()
    projected: list[MaterialGroup] = []

    for consumers in _shared_direct_clusters(session):
        group = _group(
            session=session,
            anchor_requirement_id=consumers[0],
            consumers=consumers,
        )
        projected.append(group)
        assigned.update(consumers)

    for requirement in coorigin_material_requirements(session):
        consumers = tuple(
            item for item in requirement.source_goal_ids
            if item in questions_by_id
        )
        if not consumers or assigned.intersection(consumers):
            continue
        if any(
            question.result_dependency is not None
            and question.result_dependency.source_goal_id in set(consumers)
            for consumer_id in consumers
            if (question := questions_by_id.get(consumer_id)) is not None
        ):
            continue
        projected.append(
            _group(
                session=session,
                anchor_requirement_id=requirement.anchor_goal_id,
                consumers=consumers,
            )
        )
        assigned.update(consumers)

    for question in brief.questions:
        if question.goal_id in assigned:
            continue
        projected.append(
            _group(
                session=session,
                anchor_requirement_id=question.goal_id,
                consumers=(question.goal_id,),
            )
        )
        assigned.add(question.goal_id)

    by_identity: dict[tuple[str, str, tuple[str, ...]], MaterialGroup] = {}
    for group in projected:
        key = (
            group.scope_version_id,
            group.material_fingerprint,
            group.dependency_requirement_ids,
        )
        prior = by_identity.get(key)
        if prior is None:
            by_identity[key] = group
            continue
        consumers = tuple(
            sorted(
                dict.fromkeys(
                    (*prior.consumer_requirement_ids, *group.consumer_requirement_ids)
                )
            )
        )
        merged = _group(
            session=session,
            anchor_requirement_id=min(
                prior.anchor_requirement_id,
                group.anchor_requirement_id,
            ),
            consumers=consumers,
        )
        if merged.material_fingerprint != group.material_fingerprint:
            raise ValueError("MaterialGroup exact-identity merge changed acquisition")
        by_identity[key] = merged

    output = tuple(
        sorted(
            by_identity.values(),
            key=lambda item: (
                item.scope_version_id,
                item.material_fingerprint,
                item.material_group_id,
            ),
        )
    )
    consumer_ids = tuple(
        item
        for group in output
        for item in group.consumer_requirement_ids
    )
    expected = tuple(sorted(questions_by_id))
    if tuple(sorted(consumer_ids)) != expected:
        raise ValueError("MaterialGroup projection lost or duplicated analytical requirements")
    return output


class MaterialGroupDependencyError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def material_execution_anchor_for_requirement(
    groups: tuple[MaterialGroup, ...],
    *,
    requirement_id: str,
) -> str:
    """Resolve one analytical requirement to its exact shared execution anchor."""

    matches = tuple(
        group
        for group in groups
        if requirement_id in set(group.consumer_requirement_ids)
    )
    if not matches:
        raise MaterialGroupDependencyError(
            "BRAIN_V2_MATERIAL_DEPENDENCY_SOURCE_UNKNOWN",
            requirement_id,
        )
    if len(matches) != 1:
        raise MaterialGroupDependencyError(
            "BRAIN_V2_MATERIAL_DEPENDENCY_SOURCE_AMBIGUOUS",
            requirement_id,
        )
    return matches[0].anchor_requirement_id


def result_dependency_execution_anchor(
    *,
    session,
    groups: tuple[MaterialGroup, ...],
    requirement_id: str,
) -> str | None:
    """Map a declared result dependency to the durable P14 occurrence anchor."""

    brief = session.accepted_brief
    if brief is None:
        raise MaterialGroupDependencyError(
            "BRAIN_V2_MATERIAL_DEPENDENCY_BRIEF_REQUIRED",
            requirement_id,
        )
    matches = tuple(
        item for item in brief.questions if item.goal_id == requirement_id
    )
    if len(matches) != 1:
        raise MaterialGroupDependencyError(
            "BRAIN_V2_MATERIAL_DEPENDENCY_REQUIREMENT_UNKNOWN",
            requirement_id,
        )
    dependency = matches[0].result_dependency
    if dependency is None:
        return None
    return material_execution_anchor_for_requirement(
        groups,
        requirement_id=dependency.source_goal_id,
    )


def select_pending_material_group(
    groups: tuple[MaterialGroup, ...],
    *,
    completed_material_group_ids: tuple[str, ...],
    active_material_group_id: str | None = None,
) -> MaterialGroup | None:
    """Select one dependency-ready group without inventing semantic work."""

    by_id = {item.material_group_id: item for item in groups}
    if len(by_id) != len(groups):
        raise MaterialGroupDependencyError(
            "BRAIN_V2_MATERIAL_GROUP_DUPLICATE",
            "material group ids must be unique",
        )
    requirement_group = {
        requirement_id: group.material_group_id
        for group in groups
        for requirement_id in group.consumer_requirement_ids
    }
    completed = set(completed_material_group_ids)

    def ready(group: MaterialGroup) -> bool:
        for requirement_id in group.dependency_requirement_ids:
            source_group_id = requirement_group.get(requirement_id)
            if source_group_id is None:
                raise MaterialGroupDependencyError(
                    "BRAIN_V2_MATERIAL_DEPENDENCY_SOURCE_UNKNOWN",
                    requirement_id,
                )
            if source_group_id == group.material_group_id:
                raise MaterialGroupDependencyError(
                    "BRAIN_V2_MATERIAL_DEPENDENCY_SELF_GROUP",
                    requirement_id,
                )
            if source_group_id not in completed:
                return False
        return True

    if active_material_group_id is not None:
        active = by_id.get(active_material_group_id)
        if active is None:
            raise MaterialGroupDependencyError(
                "BRAIN_V2_MATERIAL_GROUP_UNKNOWN",
                active_material_group_id,
            )
        if not ready(active):
            raise MaterialGroupDependencyError(
                "BRAIN_V2_MATERIAL_DEPENDENCY_NOT_READY",
                active_material_group_id,
            )
        return active

    pending = tuple(
        item for item in groups
        if item.material_group_id not in completed
    )
    if not pending:
        return None
    runnable = tuple(item for item in pending if ready(item))
    if not runnable:
        raise MaterialGroupDependencyError(
            "BRAIN_V2_MATERIAL_DEPENDENCY_DEADLOCK",
            "pending material groups have no dependency-ready member",
        )
    return sorted(
        runnable,
        key=lambda item: (
            item.material_fingerprint,
            item.material_group_id,
        ),
    )[0]
