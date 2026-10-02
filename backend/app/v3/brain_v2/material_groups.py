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
    digest = hashlib.sha256(_canonical(identity).encode("utf-8")).hexdigest()
    return MaterialGroup(
        material_group_id="mg_" + digest[:24],
        anchor_requirement_id=anchor_requirement_id,
        scope_version_id=brief.scope.scope_version.version_id,
        consumer_requirement_ids=consumer_ids,
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
    by_identity: dict[tuple[str, str], MaterialGroup] = {}
    for group in projected:
        key = (group.scope_version_id, group.material_fingerprint)
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
