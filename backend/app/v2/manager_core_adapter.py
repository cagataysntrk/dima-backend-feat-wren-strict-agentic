"""Governed Core analytics adapter for the Day 6.5 Manager.

The Manager supplies only opaque semantic handles. This adapter resolves them inside
the trust plane, builds canonical AnalyticsIR, reuses CubePlanner/Wren/result validation,
seals QueryContracts, and returns bounded verified EvidenceArtifact.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from app.v2.cube_planner import (
    CubePlanner,
    ResultValidator,
    StandardAnalyticsError,
    ledger_from_canonical_ir,
)
from app.v2.manager_models import AcceptedTurnContract
from app.v2.manager_tools import RunAnalyticsArgs
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


class ManagerCoreAdapterError(RuntimeError):
    pass


@dataclass(frozen=True)
class ManagerCoreAnalyticsResult:
    evidence: EvidenceArtifact
    analytics_ir: AnalyticsIR
    query_count: int


class ManagerCoreAnalyticsAdapter:
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
    def _single_cube(refs: tuple[Any, ...]) -> str:
        sets = [set(ref.cube_names) for ref in refs if getattr(ref, "cube_names", ())]
        if not sets:
            raise ManagerCoreAdapterError("semantic handles cube scope taşımıyor")
        common = set.intersection(*sets)
        if len(common) != 1:
            raise ManagerCoreAdapterError(
                f"governed standard analytics exactly one cube gerektirir; candidates={sorted(common)}"
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
        value = binding.canonical_target
        if not isinstance(value, expected_type):
            raise ManagerCoreAdapterError(
                f"semantic handle {handle_id} unexpected target type {type(value).__name__}"
            )
        return value

    def run(
        self,
        args: RunAnalyticsArgs,
        *,
        task_id: str,
        accepted_contract: AcceptedTurnContract,
        tenant_binding: str,
        principal,
        service,
        runtime: TenantAnalyticsRuntimeV0,
        contract_store,
        session_id: str | None,
    ) -> ManagerCoreAnalyticsResult:
        unknown_obligations = set(args.obligation_ids) - set(accepted_contract.obligation_ids)
        if unknown_obligations:
            raise ManagerCoreAdapterError(
                "run_analytics accepted contract dışında obligation kullanamaz: "
                + ", ".join(sorted(unknown_obligations))
            )

        context_version = accepted_contract.context_version
        metrics = tuple(
            self._binding(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedSemanticRef,
            )
            for handle_id in args.metric_handles
        )
        dimensions = tuple(
            self._binding(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedSemanticRef,
            )
            for handle_id in args.dimension_handles
        )
        filters = tuple(
            self._binding(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedFilterRef,
            )
            for handle_id in args.filter_handles
        )
        period = (
            self._binding(
                args.period_handle,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedPeriod,
            )
            if args.period_handle
            else None
        )
        comparison = (
            self._binding(
                args.comparison_handle,
                tenant_binding=tenant_binding,
                context_version=context_version,
                expected_type=ResolvedComparison,
            )
            if args.comparison_handle
            else None
        )

        if (args.ranking_direction is None) != (args.limit is None):
            raise ManagerCoreAdapterError("ranking direction ve limit birlikte verilmelidir")
        ranking = None
        if args.ranking_direction is not None:
            if len(metrics) != 1 or not dimensions:
                raise ManagerCoreAdapterError(
                    "ranking tek metric ve en az bir dimension gerektirir"
                )
            ranking = ResolvedRanking(
                measure=metrics[0].canonical_name,
                direction=args.ranking_direction,
                limit=args.limit,
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
        ledger = ledger_from_canonical_ir(ir)

        try:
            plans, ledger = self._planner.plan(ir=ir, ledger=ledger, service=service)
        except StandardAnalyticsError as exc:
            raise ManagerCoreAdapterError(str(exc)) from exc

        raw_results: list[dict] = []
        query_count = 0
        for plan in plans:
            service.dry_plan(plan.sql, principal=principal)
            raw_results.append(service.query(plan.sql, principal=principal))
            query_count += 1

        if ir.ranking is not None and ir.comparison is not None:
            if len(plans) != 1 or len(raw_results) != 1:
                raise ManagerCoreAdapterError("ranked comparison primary cardinality invalid")
            reference_plan, ledger = self._planner.plan_ranked_comparison_reference(
                ir=ir,
                ledger=ledger,
                primary_result=raw_results[0],
                service=service,
            )
            service.dry_plan(reference_plan.sql, principal=principal)
            reference_result = service.query(reference_plan.sql, principal=principal)
            query_count += 1
            plans = (*plans, reference_plan)
            raw_results.append(reference_result)

        try:
            ledger, validation_errors = self._validator.validate(
                ir=ir,
                ledger=ledger,
                plans=plans,
                results=tuple(raw_results),
            )
        except StandardAnalyticsError as exc:
            raise ManagerCoreAdapterError(str(exc)) from exc

        if not ledger.all_must_verified:
            raise ManagerCoreAdapterError("query-level MUST ledger VERIFIED değil")
        if contract_store is None or not callable(getattr(contract_store, "record_v2_minimum", None)):
            raise ManagerCoreAdapterError("strict ContractStore unavailable")

        contract_refs: list[str] = []
        bounded_results: list[dict[str, Any]] = []
        limitations: list[str] = []
        ir_snapshot = ir.model_dump(mode="json")

        for plan, result, errors in zip(plans, raw_results, validation_errors):
            if errors:
                raise ManagerCoreAdapterError("verified result contains validation errors")
            sealed = contract_store.record_v2_minimum(
                session_id=session_id,
                question=f"[v2-manager:{accepted_contract.contract_id}]",
                cube_query=plan.cube_query,
                sql=plan.sql,
                result=result,
                schema_version=runtime.mdl_version,
                tenant_id=runtime.tenant_id,
                provenance={
                    "v2_manager": {
                        "accepted_contract_id": accepted_contract.contract_id,
                        "obligation_ids": list(args.obligation_ids),
                        "analytics_ir": ir_snapshot,
                        "planner_id": self._planner.planner_id,
                        "planner_version": self._planner.planner_version,
                        "context_version": context_version,
                        "principal_user_id": runtime.principal_user_id,
                        "principal_roles": list(runtime.roles),
                    }
                },
            )
            if not bool(sealed.get("sealed")):
                raise ManagerCoreAdapterError("QueryContract seal başarısız")
            contract_refs.append(str(sealed["id"]))

            rows = tuple(dict(row) for row in (result.get("rows") or ()))
            if len(rows) > self._sample_rows:
                limitations.append(
                    f"{plan.execution_id}: Manager evidence sample {self._sample_rows} satırla sınırlandı"
                )
            bounded_results.append(
                {
                    "execution_id": plan.execution_id,
                    "role": plan.role,
                    "columns": tuple(str(col) for col in (result.get("columns") or ())),
                    "row_count": int(result.get("row_count") or 0),
                    "rows": rows[: self._sample_rows],
                }
            )

        artifact_payload = (
            f"{task_id}\x1f{accepted_contract.contract_id}\x1f{'|'.join(contract_refs)}"
        )
        evidence = EvidenceArtifact(
            artifact_id="evi_" + hashlib.sha256(artifact_payload.encode("utf-8")).hexdigest()[:24],
            task_id=task_id,
            obligation_ids=args.obligation_ids,
            query_contract_refs=tuple(contract_refs),
            evidence_kind="standard_analytics",
            verified=True,
            payload={
                "executions": bounded_results,
                "analytics_ir": ir_snapshot,
                "query_count": query_count,
            },
            limitations=tuple(limitations),
        )
        return ManagerCoreAnalyticsResult(
            evidence=evidence,
            analytics_ir=ir,
            query_count=query_count,
        )
