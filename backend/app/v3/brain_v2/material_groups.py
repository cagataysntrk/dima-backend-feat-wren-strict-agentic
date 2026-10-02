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


def _group(*, session, anchor_requirement_id: str, consumers: tuple[str, ...]):
    brief = session.accepted_brief
    if brief is None:
        raise ValueError("MaterialGroup projection requires accepted ResearchBrief")
    contract = analytical_scope_contract(
        session=session,
        obligation_id=anchor_requirement_id,
    )
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
    # Presentation belongs to the requirement/outcome plane, not the
    # material plane. Reuse the canonical AnalyticalRequestContract identity
    # with presentation surfaces erased so adding REPORT/EXPLAIN cannot mint a
    # second native material need.
    execution_contract = contract.model_copy(
        update={"requested_output_surfaces": ()}
    )
    material_fingerprint = execution_contract.material_fingerprint
    identity = {
        "scope_version_id": brief.scope.scope_version.version_id,
        "consumer_requirement_ids": list(consumer_ids),
        "material_fingerprint": material_fingerprint,
    }
    if dependency_ids:
        identity["dependency_requirement_ids"] = list(dependency_ids)
    digest = hashlib.sha256(_canonical(identity).encode("utf-8")).hexdigest()
    return MaterialGroup(
        material_group_id="mg_" + digest[:24],
        anchor_requirement_id=anchor_requirement_id,
        scope_version_id=brief.scope.scope_version.version_id,
        consumer_requirement_ids=consumer_ids,
        dependency_requirement_ids=dependency_ids,
        required_metric_refs=tuple(dict.fromkeys(contract.metric_refs)),
        required_dimension_refs=tuple(dict.fromkeys(contract.dimension_refs)),
        required_periods=_periods(contract),
        required_filters=_filters(contract),
        material_fingerprint=material_fingerprint,
    )


def project_material_groups(session) -> tuple[MaterialGroup, ...]:
    """Project every analytical requirement into minimum typed material groups.

    Exact co-origin compatibility from Research analytical authority is used
    first. Remaining analytical requirements receive one group each. Groups are
    merged only when their full material fingerprints and scope versions are
    identical. Presentation deliverables never create MaterialGroups.
    """

    brief = session.accepted_brief
    if brief is None:
        raise ValueError("MaterialGroup projection requires accepted ResearchBrief")

    questions_by_id = {item.goal_id: item for item in brief.questions}
    assigned: set[str] = set()
    projected: list[MaterialGroup] = []

    for requirement in coorigin_material_requirements(session):
        consumers = tuple(
            item for item in requirement.source_goal_ids
            if item in questions_by_id
        )
        if not consumers:
            continue
        if any(
            question.result_dependency is not None
            and question.result_dependency.source_goal_id in set(consumers)
            for consumer_id in consumers
            if (question := questions_by_id.get(consumer_id)) is not None
        ):
            # A result-dependent child needs a second occurrence after the
            # parent's governed result exists; it cannot co-origin-share that
            # occurrence even when static base material looks compatible.
            continue
        overlap = assigned.intersection(consumers)
        if overlap:
            raise ValueError(
                "analytical requirement belongs to multiple MaterialGroups: "
                + ",".join(sorted(overlap))
            )
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

    # Exact material identity is sufficient for sharing. This is not fuzzy
    # clause similarity: AnalyticalRequestContract already encodes the complete
    # typed material need including scope, filters, time, ranking and outputs.
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
        anchor = min(prior.anchor_requirement_id, group.anchor_requirement_id)
        by_identity[key] = _group(
            session=session,
            anchor_requirement_id=anchor,
            consumers=consumers,
        )

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
