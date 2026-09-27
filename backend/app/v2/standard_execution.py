"""Pure Standard governed execution seam for Day 6.5.

Input authority is AcceptedStandardAuthority + the exact StandardProjection it seals.
No AcceptedTurnContract, UserObligationLedger, ResearchManagerLoop, raw prompt semantic
interpretation, or model-specific behavior is allowed here.

This is also the narrow future D65-X substrate seam:
    StandardProjection + AcceptedStandardAuthority -> governed execution -> Evidence
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.v2.cube_planner import (
    CubePlanner,
    ResultValidator,
    StandardAnalyticsError,
    ledger_from_canonical_ir,
)
from app.v2.manager_models import StandardProjection
from app.v2.execution_receipts import build_query_contract_audit_receipt
from app.v2.models import (
    AnalyticsIR,
    EvidenceArtifact,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedRanking,
    ResolvedSemanticRef,
    TenantAnalyticsRuntimeV0,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_authority import AcceptedStandardAuthority


class StandardExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class StandardExecutionResult:
    evidence: EvidenceArtifact
    analytics_ir: AnalyticsIR
    query_count: int
    query_contract_refs: tuple[str, ...]


class WrenStandardExecutionAdapter:
    """Execute one sealed StandardProjection through the current Wren trust plane."""

    adapter_id = "wren_standard_v1"

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        planner: CubePlanner | None = None,
        validator: ResultValidator | None = None,
        sample_rows: int = 20,
    ) -> None:
        self._handles = semantic_handles
        self._planner = planner or CubePlanner()
        self._validator = validator or ResultValidator()
        self._sample_rows = max(1, int(sample_rows))

    @staticmethod
    def _projection_hash(projection: StandardProjection) -> str:
        raw = json.dumps(
            projection.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _projection_handles(projection: StandardProjection) -> tuple[str, ...]:
        values = [
            *projection.metric_handles,
            *projection.dimension_handles,
            *projection.filter_handles,
        ]
        if projection.period_handle is not None:
            values.append(projection.period_handle)
        if projection.comparison_handle is not None:
            values.append(projection.comparison_handle)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _single_cube(refs: tuple[Any, ...]) -> str:
        scopes = [
            set(ref.cube_names)
            for ref in refs
            if getattr(ref, "cube_names", ())
        ]
        if not scopes:
            raise StandardExecutionError(
                "standard semantic handles carry no cube scope"
            )
        common = set.intersection(*scopes)
        if len(common) != 1:
            raise StandardExecutionError(
                "standard execution requires exactly one governed cube; "
                f"candidates={sorted(common)}"
            )
        return next(iter(common))

    def _binding(
        self,
        handle_id: str,
        *,
        tenant_binding: str,
        context_version: str,
        expected_type,
    ):
        binding = self._handles.binding_for_execution(
            handle_id,
            tenant_binding=tenant_binding,
            context_version=context_version,
        )
        target = binding.canonical_target
        if not isinstance(target, expected_type):
            raise StandardExecutionError(
                f"semantic handle {handle_id} has unexpected target "
                f"{type(target).__name__}"
            )
        return target

    def _verify_authority(
        self,
        *,
        projection: StandardProjection,
        authority: AcceptedStandardAuthority,
        tenant_binding: str,
    ) -> None:
        if self._projection_hash(projection) != authority.projection_hash:
            raise StandardExecutionError(
                "StandardProjection does not match sealed Standard authority"
            )
        projection_handles = self._projection_handles(projection)
        if projection_handles != authority.semantic_handle_refs:
            raise StandardExecutionError(
                "sealed Standard authority handle set does not match projection"
            )
        for handle_id in projection_handles:
            self._handles.validate(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=authority.context_version,
            )

    def resolve_authorized_ir(
        self,
        *,
        projection: StandardProjection,
        authority: AcceptedStandardAuthority,
        tenant_binding: str,
    ) -> AnalyticsIR:
        """Resolve sealed sem_* authority exactly once into canonical Dima AnalyticsIR.

        This is the substrate-neutral branch point for Day 6.5 bridge preflight.
        It performs no SQL generation, provider call, Metabase lookup, or execution.
        """
        self._verify_authority(
            projection=projection,
            authority=authority,
            tenant_binding=tenant_binding,
        )
        context_version = authority.context_version

        metrics = tuple(
            self._binding(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedSemanticRef,
            )
            for handle_id in projection.metric_handles
        )
        dimensions = tuple(
            self._binding(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedSemanticRef,
            )
            for handle_id in projection.dimension_handles
        )
        filters = tuple(
            self._binding(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedFilterRef,
            )
            for handle_id in projection.filter_handles
        )
        period = (
            self._binding(
                projection.period_handle,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedPeriod,
            )
            if projection.period_handle is not None
            else None
        )
        comparison = (
            self._binding(
                projection.comparison_handle,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedComparison,
            )
            if projection.comparison_handle is not None
            else None
        )

        if (projection.ranking_direction is None) != (projection.limit is None):
            raise StandardExecutionError(
                "ranking direction and limit must be supplied together"
            )
        ranking = None
        if projection.ranking_direction is not None:
            if len(metrics) != 1 or not dimensions:
                raise StandardExecutionError(
                    "ranking requires exactly one metric and at least one dimension"
                )
            ranking = ResolvedRanking(
                measure=metrics[0].canonical_name,
                direction=projection.ranking_direction,
                limit=projection.limit,
            )

        cube = self._single_cube((*metrics, *dimensions, *filters))
        ir = AnalyticsIR(
            cube=cube,
            metrics=metrics,
            dimensions=dimensions,
            filters=filters,
            period=period,
            ranking=ranking,
            comparison=comparison,
            context_version=context_version,
        )
        return ir

    def execute(
        self,
        *,
        projection: StandardProjection,
        authority: AcceptedStandardAuthority,
        tenant_binding: str,
        principal,
        service,
        runtime: TenantAnalyticsRuntimeV0,
        contract_store,
        session_id: str | None,
        question: str,
    ) -> StandardExecutionResult:
        ir = self.resolve_authorized_ir(
            projection=projection,
            authority=authority,
            tenant_binding=tenant_binding,
        )
        ledger = ledger_from_canonical_ir(ir)

        try:
            plans, ledger = self._planner.plan(
                ir=ir,
                ledger=ledger,
                service=service,
            )
        except StandardAnalyticsError as exc:
            raise StandardExecutionError(str(exc)) from exc

        raw_results: list[dict] = []
        query_count = 0
        for plan in plans:
            service.dry_plan(plan.sql, principal=principal)
            raw_results.append(service.query(plan.sql, principal=principal))
            query_count += 1

        if ir.ranking is not None and ir.comparison is not None:
            if len(plans) != 1 or len(raw_results) != 1:
                raise StandardExecutionError(
                    "ranked comparison primary cardinality invalid"
                )
            reference_plan, ledger = self._planner.plan_ranked_comparison_reference(
                ir=ir,
                ledger=ledger,
                primary_result=raw_results[0],
                service=service,
            )
            service.dry_plan(reference_plan.sql, principal=principal)
            raw_results.append(
                service.query(reference_plan.sql, principal=principal)
            )
            query_count += 1
            plans = (*plans, reference_plan)

        try:
            ledger, validation_errors = self._validator.validate(
                ir=ir,
                ledger=ledger,
                plans=plans,
                results=tuple(raw_results),
            )
        except StandardAnalyticsError as exc:
            raise StandardExecutionError(str(exc)) from exc

        if not ledger.all_must_verified:
            raise StandardExecutionError(
                "query-level MUST ledger is not VERIFIED"
            )
        if contract_store is None or not callable(
            getattr(contract_store, "record_v2_minimum", None)
        ):
            raise StandardExecutionError("strict ContractStore unavailable")

        exposed_columns = {
            binding.canonical_target.canonical_name: handle_id
            for handle_id in (
                *projection.metric_handles,
                *projection.dimension_handles,
            )
            for binding in (
                self._handles.binding_for_execution(
                    handle_id,
                    tenant_binding=tenant_binding,
                    context_version=ir.context_version,
                ),
            )
            if isinstance(binding.canonical_target, ResolvedSemanticRef)
        }

        contract_refs: list[str] = []
        bounded_results: list[dict[str, Any]] = []
        limitations: list[str] = []
        ir_snapshot = ir.model_dump(mode="json")

        for plan, result, errors in zip(
            plans,
            raw_results,
            validation_errors,
            strict=True,
        ):
            if errors:
                raise StandardExecutionError(
                    "verified result contains validation errors"
                )
            projected_capabilities: list[str] = ["performance"]
            if projection.dimension_handles:
                projected_capabilities.append("breakdown")
            if projection.comparison_handle is not None:
                projected_capabilities.append("comparison")
            if projection.ranking_direction is not None:
                projected_capabilities.append("ranking")
            audit_receipt = build_query_contract_audit_receipt(
                execution_id=plan.execution_id,
                accepted_authority_ref=authority.authority_id,
                obligation_ids=projection.obligation_ids,
                requested_capabilities=tuple(projected_capabilities),
                semantic_handle_refs=tuple(
                    dict.fromkeys(
                        (
                            *projection.metric_handles,
                            *projection.dimension_handles,
                            *projection.filter_handles,
                            *((projection.period_handle,) if projection.period_handle else ()),
                            *((projection.comparison_handle,) if projection.comparison_handle else ()),
                        )
                    )
                ),
                analytics_ir=ir,
                tenant_binding=tenant_binding,
                principal_subject=runtime.principal_user_id,
                context_version=ir.context_version,
                planner_id=self._planner.planner_id,
                planner_version=self._planner.planner_version,
                research_run_id=None,
                research_task_id=None,
                relationship_join_authority=None,
            )
            sealed = contract_store.record_v2_minimum(
                session_id=session_id,
                question=question,
                cube_query=plan.cube_query,
                sql=plan.sql,
                result=result,
                schema_version=runtime.mdl_version,
                tenant_id=runtime.tenant_id,
                provenance={
                    "v2_standard": {
                        "adapter_id": self.adapter_id,
                        "accepted_standard_authority_id": authority.authority_id,
                        "projection_hash": authority.projection_hash,
                        "obligation_ids": list(projection.obligation_ids),
                        "analytics_ir": ir_snapshot,
                        "planner_id": self._planner.planner_id,
                        "planner_version": self._planner.planner_version,
                        "context_version": ir.context_version,
                        "principal_user_id": runtime.principal_user_id,
                        "principal_roles": list(runtime.roles),
                        "audit_receipt": audit_receipt,
                    }
                },
            )
            if not bool(sealed.get("sealed")):
                raise StandardExecutionError("QueryContract seal failed")
            contract_refs.append(str(sealed["id"]))

            rows = tuple(dict(row) for row in (result.get("rows") or ()))
            if len(rows) > self._sample_rows:
                limitations.append(
                    f"{plan.execution_id}: evidence sample limited to "
                    f"{self._sample_rows} rows"
                )
            safe_rows = tuple(
                {
                    exposed_columns[key]: value
                    for key, value in row.items()
                    if key in exposed_columns
                }
                for row in rows[: self._sample_rows]
            )
            bounded_results.append(
                {
                    "execution_id": plan.execution_id,
                    "role": plan.role,
                    "columns": tuple(
                        exposed_columns[str(column)]
                        for column in (result.get("columns") or ())
                        if str(column) in exposed_columns
                    ),
                    "row_count": int(result.get("row_count") or 0),
                    "rows": safe_rows,
                }
            )

        artifact_payload = (
            f"{authority.authority_id}\x1f{authority.projection_hash}\x1f"
            + "|".join(contract_refs)
        )
        evidence = EvidenceArtifact(
            artifact_id=(
                "evi_"
                + hashlib.sha256(
                    artifact_payload.encode("utf-8")
                ).hexdigest()[:24]
            ),
            task_id=f"standard:{authority.authority_id}",
            obligation_ids=projection.obligation_ids,
            query_contract_refs=tuple(contract_refs),
            evidence_kind="standard_analytics",
            verified=True,
            tenant_binding=tenant_binding,
            principal_subject=runtime.principal_user_id,
            context_version=ir.context_version,
            run_id=f"standard:{authority.authority_id}",
            lineage_id=authority.authority_id,
            accepted_contract_id=authority.authority_id,
            payload={
                "executions": bounded_results,
                "query_count": query_count,
                "accepted_standard_authority_id": authority.authority_id,
                "projection_hash": authority.projection_hash,
            },
            limitations=tuple(limitations),
        )
        return StandardExecutionResult(
            evidence=evidence,
            analytics_ir=ir,
            query_count=query_count,
            query_contract_refs=tuple(contract_refs),
        )
