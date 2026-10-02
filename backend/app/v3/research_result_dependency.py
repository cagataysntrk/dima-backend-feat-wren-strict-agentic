"""Governed upstream-result -> execution-local material dependency.

This module owns no analytics and never mutates accepted Research scope. It
projects one already-VERIFIED ranked entity value into an exact transient
AnalyticalRequestContract filter for downstream Metabot work.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytical_request_contract import (
    AnalyticalFilterInvariant,
    AnalyticalRequestContract,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResultDependencyProjectionError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ResultSelectionResolution(FrozenModel):
    source_goal_id: str = Field(min_length=1)
    source_execution_obligation_id: str = Field(min_length=1)
    source_evidence_id: str = Field(min_length=1)
    source_receipt_id: str = Field(min_length=1)
    source_result_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    dimension_semantic_id: str = Field(min_length=1)
    native_field_id: int = Field(gt=0)
    selected_value: str = Field(min_length=1)
    contract: AnalyticalRequestContract


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def _matches_field(column: Any, native_field_id: int) -> bool:
    if not isinstance(column, dict):
        return False
    if column.get("id") == native_field_id:
        return True
    field_ref = column.get("field_ref")
    return bool(
        isinstance(field_ref, (list, tuple))
        and len(field_ref) >= 2
        and field_ref[0] == "field"
        and field_ref[1] == native_field_id
    )


def resolve_first_ranked_entity(
    *,
    base_contract: AnalyticalRequestContract,
    source_goal_id: str,
    source_evidence_id: str,
    source_receipt_id: str,
    source_result_hash: str,
    dimension_semantic_id: str,
    native_field_id: int,
    parent_result: dict[str, Any],
    dimension_name: str | None = None,
    source_execution_obligation_id: str | None = None,
) -> ResultSelectionResolution:
    """Bind the first source-backed ranked row without re-ranking or recalculation."""

    execution_obligation_id = source_execution_obligation_id or source_goal_id

    data = parent_result.get("data")
    if not isinstance(data, dict):
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_RESULT_SHAPE_INVALID",
            "verified parent result has no data object",
        )
    columns = data.get("cols")
    rows = data.get("rows")
    if not isinstance(columns, list) or not isinstance(rows, list):
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_RESULT_SHAPE_INVALID",
            "verified parent result must expose cols and rows",
        )

    matching = [
        index
        for index, column in enumerate(columns)
        if _matches_field(column, native_field_id)
    ]
    if len(matching) != 1:
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_DIMENSION_COLUMN_AMBIGUOUS",
            "verified parent result must expose exactly one governed dependency dimension",
        )
    if not rows:
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_PARENT_EMPTY",
            "verified parent ranking returned no selectable entity",
        )
    first = rows[0]
    index = matching[0]
    if not isinstance(first, (list, tuple)) or index >= len(first):
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_RESULT_SHAPE_INVALID",
            "first ranked row does not contain the governed dependency dimension",
        )
    selected = first[index]
    if not isinstance(selected, str) or not selected.strip():
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_ENTITY_VALUE_INVALID",
            "ranked dependency entity must be one non-empty governed string value",
        )
    selected = selected.strip()

    same_dimension = tuple(
        item
        for item in base_contract.filters
        if item.source_candidate_id == dimension_semantic_id
    )
    if any(item.value != selected for item in same_dimension):
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_SCOPE_CONFLICT",
            "ranked result conflicts with an already accepted filter on that dimension",
        )

    projected = base_contract
    if not any(item.value == selected for item in same_dimension):
        provenance = {
            "source_goal_id": source_goal_id,
            "source_execution_obligation_id": execution_obligation_id,
            "source_evidence_id": source_evidence_id,
            "source_receipt_id": source_receipt_id,
            "source_result_hash": source_result_hash,
            "dimension_semantic_id": dimension_semantic_id,
            "native_field_id": native_field_id,
            "selected_value": selected,
        }
        digest = hashlib.sha256(_canonical(provenance).encode("utf-8")).hexdigest()
        dependency_filter = AnalyticalFilterInvariant(
            semantic_ref="result-selection:" + digest,
            source_candidate_id=dimension_semantic_id,
            dimension_name=(dimension_name or dimension_semantic_id),
            value=selected,
        )
        projected = base_contract.model_copy(
            update={"filters": (*base_contract.filters, dependency_filter)}
        )

    if projected.scope_identity != base_contract.scope_identity:
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_SCOPE_MUTATION_FORBIDDEN",
            "execution-local dependency changed accepted scope identity",
        )
    if projected.scope_fingerprint != base_contract.scope_fingerprint:
        raise ResultDependencyProjectionError(
            "R1_RESULT_DEPENDENCY_SCOPE_MUTATION_FORBIDDEN",
            "execution-local dependency changed accepted scope fingerprint",
        )

    return ResultSelectionResolution(
        source_goal_id=source_goal_id,
        source_execution_obligation_id=execution_obligation_id,
        source_evidence_id=source_evidence_id,
        source_receipt_id=source_receipt_id,
        source_result_hash=source_result_hash,
        dimension_semantic_id=dimension_semantic_id,
        native_field_id=native_field_id,
        selected_value=selected,
        contract=projected,
    )
