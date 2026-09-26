"""Day12 diagnostic execution receipts layered on existing QueryContract authority.

Receipts are audit/observability material only. They never authorize execution, mint
semantic truth, or replace ContractStore / QueryContract / Evidence owners.
"""

from __future__ import annotations

from typing import Any


def _dump(value: Any) -> Any:
    if value is None:
        return None
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json")
    return value


def _canonical_name(value: Any) -> str | None:
    if value is None:
        return None
    return str(
        getattr(value, "canonical_name", None)
        or getattr(value, "dimension_name", None)
        or ""
    ) or None


def build_query_contract_audit_receipt(
    *,
    execution_id: str,
    accepted_authority_ref: str,
    obligation_ids: tuple[str, ...],
    requested_capabilities: tuple[str, ...],
    semantic_handle_refs: tuple[str, ...],
    analytics_ir: Any,
    tenant_binding: str,
    principal_subject: str,
    context_version: str,
    planner_id: str,
    planner_version: str,
    research_run_id: str | None = None,
    research_task_id: str | None = None,
    relationship_join_authority: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a complete, secret-minimized audit view of one sealed execution.

    The executable SQL/result hash remain owned by ContractStore. This receipt makes
    the governing intent/semantic/execution lineage explicit next to that seal.
    """

    metrics = tuple(
        item
        for item in (
            _canonical_name(value)
            for value in tuple(getattr(analytics_ir, "metrics", ()) or ())
        )
        if item
    )
    dimensions = tuple(
        item
        for item in (
            _canonical_name(value)
            for value in tuple(getattr(analytics_ir, "dimensions", ()) or ())
        )
        if item
    )
    filters = tuple(
        _dump(value)
        for value in tuple(getattr(analytics_ir, "filters", ()) or ())
    )
    cube = str(getattr(analytics_ir, "cube", "") or "")
    period = _dump(getattr(analytics_ir, "period", None))
    comparison = _dump(getattr(analytics_ir, "comparison", None))
    ranking = _dump(getattr(analytics_ir, "ranking", None))

    return {
        "receipt_version": "v2-day12-query-contract-audit-v1",
        "accepted_authority_ref": accepted_authority_ref,
        "requested_capabilities": list(dict.fromkeys(requested_capabilities)),
        "obligation_ids": list(dict.fromkeys(obligation_ids)),
        "canonical_semantic_refs": {
            "opaque_handles": list(dict.fromkeys(semantic_handle_refs)),
            "metrics": list(metrics),
            "dimensions": list(dimensions),
        },
        "model_cube_authority": cube,
        "grain": list(dimensions),
        "filters": list(filters),
        "period": period,
        "comparison": comparison,
        "ranking": ranking,
        "relationship_join_authority": relationship_join_authority,
        "execution_identity": {
            "execution_id": execution_id,
            "research_run_id": research_run_id,
            "research_task_id": research_task_id,
        },
        "tenant_principal_context": {
            "tenant_binding": tenant_binding,
            "principal_subject": principal_subject,
            "context_version": context_version,
        },
        "planner": {
            "planner_id": planner_id,
            "planner_version": planner_version,
        },
    }


def build_development_performance_receipt(
    *,
    first_status_ms: int | None,
    first_verified_evidence_ms: int | None,
    report_ready_ms: int | None,
    total_ms: int,
    provider_calls_by_role: dict[str, int],
    wren_query_calls: int,
    wren_dry_plan_calls: int,
    wren_cube_sql_calls: int,
    manager_turns: int,
) -> dict[str, Any]:
    """Comparison-ready diagnostic sample; never an authority or p95 claim."""

    if total_ms < 0 or manager_turns < 0:
        raise ValueError("performance receipt counters must be non-negative")
    for label, value in (
        ("wren_query_calls", wren_query_calls),
        ("wren_dry_plan_calls", wren_dry_plan_calls),
        ("wren_cube_sql_calls", wren_cube_sql_calls),
    ):
        if value < 0:
            raise ValueError(f"{label} must be non-negative")
    normalized_calls = {
        str(role): int(count)
        for role, count in sorted(provider_calls_by_role.items())
        if int(count) >= 0
    }
    return {
        "receipt_version": "v2-day12-performance-sample-v1",
        "first_status_ms": first_status_ms,
        "first_verified_evidence_ms": first_verified_evidence_ms,
        "report_ready_ms": report_ready_ms,
        "total_ms": total_ms,
        "provider_calls_by_role": normalized_calls,
        "wren_calls": {
            "query": wren_query_calls,
            "dry_plan": wren_dry_plan_calls,
            "cube_sql": wren_cube_sql_calls,
        },
        "manager_turns": manager_turns,
        "sample_count": 1,
        "p95_claim": False,
        "diagnostic_only": True,
    }
