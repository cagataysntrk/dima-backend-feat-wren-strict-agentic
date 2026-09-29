"""Thin P6 Metabase execution substrate.

This adapter orchestrates already-resolved Dima contracts. It does not resolve semantics,
search Metabase, issue access snapshots, inspect raw language, guess fields, select
relationships, or retry with altered meaning.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

from app.v3.analytics_contract import ResolvedAnalyticsIntent
from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionAccessSnapshot,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    RuntimeIdentity,
)
from app.v3.substrate.base import (
    ExecutionInspection,
    ExecutionIntentValidation,
    SubstrateCapabilities,
    SubstrateExecutionResult,
)
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.execution_binding import (
    DimaExecutionBindingSnapshot,
    MetabaseCompilationBlocked,
)
from app.v3.substrate.metabase.models import ConstructedQuery


class MetabaseSubstrateError(RuntimeError):
    pass


class MetabaseSubstrateAdapter:
    """Orchestrate compile -> canonicalize -> execute -> P5 seal."""

    adapter_id = "metabase_standard_v1"

    def __init__(
        self,
        *,
        client: MetabaseAgentClient,
        binding_snapshot: DimaExecutionBindingSnapshot,
        access_snapshot: ExecutionAccessSnapshot,
        runtime: RuntimeIdentity,
    ) -> None:
        self._client = client
        self._binding_snapshot = binding_snapshot
        self._access_snapshot = access_snapshot
        self._runtime = runtime

    def inspect_capabilities(self) -> SubstrateCapabilities:
        return SubstrateCapabilities(
            substrate="metabase",
            construct_query=True,
            validate_query=True,
            execute_query=True,
            inspect_execution=True,
            supports_ranking=True,
            supports_comparison=True,
            supports_filters=True,
            supports_time=True,
        )

    def _runtime_reasons(self) -> tuple[str, ...]:
        reasons: list[str] = []
        policy = self._client.policy
        if self._runtime.substrate != "metabase":
            reasons.append("runtime substrate is not metabase")
        if self._runtime.runtime_version != policy.runtime_version:
            reasons.append("runtime version does not match pinned Metabase client policy")
        if self._runtime.image_digest != policy.runtime_image_digest:
            reasons.append("runtime image digest does not match pinned Metabase client policy")
        return tuple(reasons)

    def validate_execution_intent(
        self,
        intent: ResolvedAnalyticsIntent,
    ) -> ExecutionIntentValidation:
        reasons = list(self._runtime_reasons())
        try:
            if not reasons:
                MetabaseProjectionCompiler.compile(
                    intent=intent,
                    snapshot=self._binding_snapshot,
                )
        except MetabaseCompilationBlocked as exc:
            reasons.append(f"{exc.code}: {exc.detail}")
        return ExecutionIntentValidation(
            valid=not reasons,
            reasons=tuple(reasons),
        )

    def execute_execution_intent(
        self,
        intent: ResolvedAnalyticsIntent,
    ) -> SubstrateExecutionResult:
        validation = self.validate_execution_intent(intent)
        if not validation.valid:
            raise MetabaseSubstrateError("; ".join(validation.reasons))

        plan = MetabaseProjectionCompiler.compile(
            intent=intent,
            snapshot=self._binding_snapshot,
        )
        canonical = MetabaseCanonicalizer(
            client=self._client
        ).canonicalize(plan)

        result_snapshots: list[ExecutionResultSnapshot] = []
        events: list[ExecutionEventIdentity] = []
        executions: list[dict] = []

        for step in canonical.steps:
            response = self._client.execute_serialized(
                ConstructedQuery(
                    serialized_query=step.serialized_query,
                )
            )
            if response.status.value != "completed":
                raise MetabaseSubstrateError(
                    f"Metabase step {step.role} did not complete"
                )

            payload = response.data
            rows = payload.get("rows") if isinstance(payload, dict) else None
            cols = payload.get("cols") if isinstance(payload, dict) else None
            if not isinstance(rows, list) or not isinstance(cols, list):
                raise MetabaseSubstrateError(
                    "Metabase execution payload must expose list rows and cols"
                )

            result_snapshot = ExecutionResultSnapshot(
                payload=payload,
                row_count=response.row_count,
            )
            result_snapshots.append(result_snapshot)
            execution_id = "mbx-" + uuid.uuid4().hex
            events.append(
                ExecutionEventIdentity(
                    execution_id=execution_id,
                    executed_at=datetime.now(timezone.utc),
                )
            )
            executions.append(
                {
                    "execution_id": execution_id,
                    "role": step.role,
                    "columns": tuple(cols),
                    "rows": tuple(tuple(row) for row in rows),
                    "row_count": response.row_count,
                    "canonical_query_fingerprint": (
                        step.canonical_query_fingerprint
                    ),
                }
            )

        receipts = DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            projection=canonical,
            access_snapshot=self._access_snapshot,
            runtime=self._runtime,
            results=tuple(result_snapshots),
            events=tuple(events),
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
            query_receipt_refs=tuple(
                item.receipt_id for item in receipts
            ),
            evidence_kind="standard_analytics",
            state=EvidenceState.VERIFIED,
            payload={
                "executions": tuple(executions),
                "query_count": len(executions),
                "accepted_standard_authority_id": intent.authority_id,
                "projection_hash": intent.projection_hash,
                "resolved_intent_hash": intent.resolved_intent_hash,
                "adapter_id": self.adapter_id,
            },
        )
        return SubstrateExecutionResult(
            substrate="metabase",
            analytics_ir_snapshot={
                "resolved_intent_hash": intent.resolved_intent_hash,
                "canonical_query_fingerprints": tuple(
                    step.canonical_query_fingerprint
                    for step in canonical.steps
                ),
                "current_catalog_fingerprint": (
                    canonical.current_catalog_fingerprint
                ),
            },
            query_count=len(canonical.steps),
            query_receipts=receipts,
            evidence=evidence,
        )

    def inspect_execution(
        self,
        execution: SubstrateExecutionResult,
    ) -> ExecutionInspection:
        reasons: list[str] = []
        if execution.substrate != "metabase":
            reasons.append("execution substrate mismatch")
        if not execution.evidence.verified:
            reasons.append("evidence is not VERIFIED")
        if len(execution.query_receipts) != execution.query_count:
            reasons.append("query receipt count does not match query count")
        if any(
            receipt.receipt_fingerprint is None
            for receipt in execution.query_receipts
        ):
            reasons.append("strict P5 receipt fingerprint missing")
        return ExecutionInspection(
            verified=not reasons,
            reasons=tuple(reasons),
            query_count=execution.query_count,
        )
