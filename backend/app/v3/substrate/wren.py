"""Wren compatibility substrate for Dima v3 M1.

This adapter receives only ResolvedAnalyticsIntent. It does not import or consult the
semantic-handle registry, does not see raw user language, and does not create semantic
authority. Query planning/execution mirrors the certified v2 Wren Standard path.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.v2.cube_planner import (
    CubePlanner,
    ResultValidator,
    StandardAnalyticsError,
    ledger_from_canonical_ir,
)
from app.v2.models import (
    AnalyticsIR,
    PeriodKind,
    ResolvedComparison as V2ResolvedComparison,
    ResolvedFilterRef as V2ResolvedFilterRef,
    ResolvedPeriod as V2ResolvedPeriod,
    ResolvedRanking as V2ResolvedRanking,
    ResolvedSemanticRef as V2ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v3.analytics_contract import (
    ResolvedAnalyticsIntent,
    ResolvedComparison,
    ResolvedPeriod,
)
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.substrate.base import (
    ExecutionInspection,
    ExecutionIntentValidation,
    SubstrateCapabilities,
    SubstrateExecutionResult,
)


class WrenSubstrateError(RuntimeError):
    pass


class WrenSubstrateAdapter:
    """Current Wren execution behavior behind the new engine-independent seam."""

    adapter_id = "wren_standard_v1"

    def __init__(
        self,
        *,
        service,
        principal,
        runtime: TenantAnalyticsRuntimeV0,
        contract_store,
        session_id: str | None = None,
        planner: CubePlanner | None = None,
        validator: ResultValidator | None = None,
        sample_rows: int = 20,
    ) -> None:
        self._service = service
        self._principal = principal
        self._runtime = runtime
        self._contract_store = contract_store
        self._session_id = session_id
        self._planner = planner or CubePlanner()
        self._validator = validator or ResultValidator()
        self._sample_rows = max(1, int(sample_rows))

    def inspect_capabilities(self) -> SubstrateCapabilities:
        return SubstrateCapabilities(
            substrate="wren",
            construct_query=True,
            validate_query=True,
            execute_query=True,
            inspect_execution=True,
            supports_ranking=True,
            supports_comparison=True,
            supports_filters=True,
            supports_time=True,
        )

    @staticmethod
    def _single_cube(refs: tuple[Any, ...]) -> str:
        scopes = [
            set(ref.source_scopes)
            for ref in refs
            if getattr(ref, "source_scopes", ())
        ]
        if not scopes:
            raise WrenSubstrateError("resolved intent carries no Wren-compatible source scope")
        common = set.intersection(*scopes)
        if len(common) != 1:
            raise WrenSubstrateError(
                "Wren execution requires exactly one governed source scope; "
                f"candidates={sorted(common)}"
            )
        return next(iter(common))

    @staticmethod
    def _period(value: ResolvedPeriod) -> V2ResolvedPeriod:
        try:
            kind = PeriodKind(value.kind)
        except ValueError as exc:
            raise WrenSubstrateError(f"unsupported Wren period kind: {value.kind}") from exc
        return V2ResolvedPeriod(
            kind=kind,
            source_text=value.source_text,
            time_dimension=value.time_dimension,
            start=value.start,
            end=value.end,
            n=value.n,
        )

    @classmethod
    def _comparison(cls, value: ResolvedComparison) -> V2ResolvedComparison:
        if value.mode != "previous_period":
            raise WrenSubstrateError(
                f"unsupported Wren comparison mode: {value.mode}"
            )
        return V2ResolvedComparison(
            mode="previous_period",
            source_text=value.source_text,
            base_period=cls._period(value.base_period),
            reference_period=cls._period(value.reference_period),
        )

    def _to_ir(self, intent: ResolvedAnalyticsIntent) -> AnalyticsIR:
        metric_refs = tuple(
            V2ResolvedSemanticRef(
                candidate_id=item.semantic_ref,
                target_kind=SemanticTargetKind.METRIC,
                canonical_name=item.canonical_name,
                cube_names=item.source_scopes,
            )
            for item in intent.metrics
        )
        dimension_refs = tuple(
            V2ResolvedSemanticRef(
                candidate_id=item.semantic_ref,
                target_kind=SemanticTargetKind.DIMENSION,
                canonical_name=item.canonical_name,
                cube_names=item.source_scopes,
            )
            for item in intent.dimensions
        )
        filter_refs = tuple(
            V2ResolvedFilterRef(
                candidate_id=item.semantic_ref,
                dimension_name=item.dimension_name,
                value=item.value,
                cube_names=item.source_scopes,
                sensitive=item.sensitive,
            )
            for item in intent.filters
        )
        period = self._period(intent.period) if intent.period is not None else None
        comparison = (
            self._comparison(intent.comparison)
            if intent.comparison is not None
            else None
        )
        ranking = (
            V2ResolvedRanking(
                measure=intent.ranking.measure,
                direction=intent.ranking.direction,
                limit=intent.ranking.limit,
            )
            if intent.ranking is not None
            else None
        )

        cube = self._single_cube(
            (*intent.metrics, *intent.dimensions, *intent.filters)
        )
        return AnalyticsIR(
            cube=cube,
            metrics=metric_refs,
            dimensions=dimension_refs,
            filters=filter_refs,
            period=period,
            ranking=ranking,
            comparison=comparison,
            context_version=intent.semantic_context_version,
        )

    def validate_execution_intent(
        self,
        intent: ResolvedAnalyticsIntent,
    ) -> ExecutionIntentValidation:
        reasons: list[str] = []
        if not intent.metrics:
            reasons.append("Wren Standard execution requires at least one metric")
        if intent.approved_relationship_paths:
            reasons.append("M1 Wren compatibility adapter does not execute relationship paths")
        try:
            if not reasons:
                self._to_ir(intent)
        except WrenSubstrateError as exc:
            reasons.append(str(exc))
        return ExecutionIntentValidation(valid=not reasons, reasons=tuple(reasons))

    @staticmethod
    def _query_fingerprint(*, cube_query: dict, sql: str) -> str:
        raw = json.dumps(
            {"cube_query": cube_query, "sql": " ".join(sql.split())},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _receipt_id(
        *,
        authority_id: str,
        intent_hash: str,
        query_fingerprint: str,
        execution_id: str,
    ) -> str:
        raw = f"{authority_id}\x1f{intent_hash}\x1f{query_fingerprint}\x1f{execution_id}"
        return "dqr_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def execute_execution_intent(
        self,
        intent: ResolvedAnalyticsIntent,
    ) -> SubstrateExecutionResult:
        validation = self.validate_execution_intent(intent)
        if not validation.valid:
            raise WrenSubstrateError("; ".join(validation.reasons))

        ir = self._to_ir(intent)
        ledger = ledger_from_canonical_ir(ir)

        try:
            plans, ledger = self._planner.plan(
                ir=ir,
                ledger=ledger,
                service=self._service,
            )
        except StandardAnalyticsError as exc:
            raise WrenSubstrateError(str(exc)) from exc

        raw_results: list[dict] = []
        query_count = 0
        for plan in plans:
            self._service.dry_plan(plan.sql, principal=self._principal)
            raw_results.append(
                self._service.query(plan.sql, principal=self._principal)
            )
            query_count += 1

        if ir.ranking is not None and ir.comparison is not None:
            if len(plans) != 1 or len(raw_results) != 1:
                raise WrenSubstrateError(
                    "ranked comparison primary cardinality invalid"
                )
            reference_plan, ledger = self._planner.plan_ranked_comparison_reference(
                ir=ir,
                ledger=ledger,
                primary_result=raw_results[0],
                service=self._service,
            )
            self._service.dry_plan(reference_plan.sql, principal=self._principal)
            raw_results.append(
                self._service.query(reference_plan.sql, principal=self._principal)
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
            raise WrenSubstrateError(str(exc)) from exc

        if not ledger.all_must_verified:
            raise WrenSubstrateError("query-level MUST ledger is not VERIFIED")
        if self._contract_store is None or not callable(
            getattr(self._contract_store, "record_v2_minimum", None)
        ):
            raise WrenSubstrateError("strict ContractStore unavailable")

        exposed_columns = {
            item.canonical_name: item.semantic_ref
            for item in (*intent.metrics, *intent.dimensions)
        }

        legacy_contract_refs: list[str] = []
        receipts: list[DimaQueryReceipt] = []
        bounded_results: list[dict[str, Any]] = []
        limitations: list[str] = []
        intent_hash = intent.resolved_intent_hash
        ir_snapshot = ir.model_dump(mode="json")

        for plan, result, errors in zip(
            plans,
            raw_results,
            validation_errors,
            strict=True,
        ):
            if errors:
                raise WrenSubstrateError(
                    "verified result contains validation errors"
                )

            sealed = self._contract_store.record_v2_minimum(
                session_id=self._session_id,
                question=intent.request_ref,
                cube_query=plan.cube_query,
                sql=plan.sql,
                result=result,
                schema_version=self._runtime.mdl_version,
                tenant_id=self._runtime.tenant_id,
                provenance={
                    "v2_standard": {
                        "adapter_id": self.adapter_id,
                        "accepted_standard_authority_id": intent.authority_id,
                        "projection_hash": intent.projection_hash,
                        "obligation_ids": list(intent.obligation_ids),
                        "analytics_ir": ir_snapshot,
                        "planner_id": self._planner.planner_id,
                        "planner_version": self._planner.planner_version,
                        "context_version": intent.semantic_context_version,
                        "principal_user_id": self._runtime.principal_user_id,
                        "principal_roles": list(self._runtime.roles),
                    },
                    "v3_dima": {
                        "resolved_intent_hash": intent_hash,
                        "semantic_resolution_inside_substrate": False,
                    },
                },
            )
            if not bool(sealed.get("sealed")):
                raise WrenSubstrateError("QueryContract seal failed")

            contract_ref = str(sealed["id"])
            legacy_contract_refs.append(contract_ref)
            query_fingerprint = self._query_fingerprint(
                cube_query=plan.cube_query,
                sql=plan.sql,
            )
            receipts.append(
                DimaQueryReceipt(
                    receipt_id=self._receipt_id(
                        authority_id=intent.authority_id,
                        intent_hash=intent_hash,
                        query_fingerprint=query_fingerprint,
                        execution_id=plan.execution_id,
                    ),
                    authority_id=intent.authority_id,
                    projection_hash=intent.projection_hash,
                    resolved_intent_hash=intent_hash,
                    canonical_query_fingerprint=query_fingerprint,
                    canonical_query_representation={
                        "cube_query": plan.cube_query,
                        "sql": plan.sql,
                    },
                    principal_fingerprint=intent.principal.fingerprint,
                    execution_access_fingerprint=intent.principal.fingerprint,
                    semantic_context_version=intent.semantic_context_version,
                    substrate="wren",
                    substrate_runtime_version=self._runtime.mdl_version,
                    legacy_query_contract_ref=contract_ref,
                    result_hash=sealed.get("result_hash"),
                    row_count=int(result.get("row_count") or 0),
                )
            )

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
            f"{intent.authority_id}\x1f{intent.projection_hash}\x1f"
            + "|".join(item.receipt_id for item in receipts)
        )
        evidence = EvidenceArtifact(
            artifact_id=(
                "evi_"
                + hashlib.sha256(
                    artifact_payload.encode("utf-8")
                ).hexdigest()[:24]
            ),
            authority_id=intent.authority_id,
            obligation_ids=intent.obligation_ids,
            query_receipt_refs=tuple(item.receipt_id for item in receipts),
            legacy_query_contract_refs=tuple(legacy_contract_refs),
            evidence_kind="standard_analytics",
            state=EvidenceState.VERIFIED,
            payload={
                "executions": bounded_results,
                "query_count": query_count,
                "accepted_standard_authority_id": intent.authority_id,
                "projection_hash": intent.projection_hash,
                "resolved_intent_hash": intent_hash,
            },
            limitations=tuple(limitations),
        )
        return SubstrateExecutionResult(
            substrate="wren",
            analytics_ir_snapshot=ir_snapshot,
            query_count=query_count,
            query_receipts=tuple(receipts),
            evidence=evidence,
            legacy_query_contract_refs=tuple(legacy_contract_refs),
        )

    def inspect_execution(
        self,
        execution: SubstrateExecutionResult,
    ) -> ExecutionInspection:
        reasons: list[str] = []
        if execution.substrate != "wren":
            reasons.append("execution substrate mismatch")
        if not execution.evidence.verified:
            reasons.append("evidence is not VERIFIED")
        if len(execution.query_receipts) != execution.query_count:
            reasons.append("query receipt count does not match query count")
        return ExecutionInspection(
            verified=not reasons,
            reasons=tuple(reasons),
            query_count=execution.query_count,
        )
