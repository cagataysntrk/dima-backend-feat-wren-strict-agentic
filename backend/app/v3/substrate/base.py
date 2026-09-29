"""Analytics substrate protocol.

A substrate executes Dima-owned ResolvedAnalyticsIntent. It is not a semantic compiler
and receives no raw user-language contract.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from app.v3.analytics_contract import ResolvedAnalyticsIntent
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SubstrateCapabilities(FrozenModel):
    substrate: str
    construct_query: bool
    validate_query: bool
    execute_query: bool
    inspect_execution: bool
    supports_ranking: bool = False
    supports_comparison: bool = False
    supports_filters: bool = False
    supports_time: bool = False


class ExecutionIntentValidation(FrozenModel):
    valid: bool
    reasons: tuple[str, ...] = ()


class SubstrateExecutionResult(FrozenModel):
    substrate: str
    analytics_ir_snapshot: dict
    query_count: int
    query_receipts: tuple[DimaQueryReceipt, ...]
    evidence: EvidenceArtifact
    legacy_query_contract_refs: tuple[str, ...] = ()


class ExecutionInspection(FrozenModel):
    verified: bool
    reasons: tuple[str, ...] = ()
    query_count: int = 0


@runtime_checkable
class QueryReceiptWriter(Protocol):
    """Dima-owned persistence/receipt seam; raw audit context stays outside substrate."""

    def record(
        self,
        *,
        intent: ResolvedAnalyticsIntent,
        execution_id: str,
        cube_query: dict,
        sql: str,
        result: dict[str, Any],
        provenance: dict[str, Any],
        substrate: str,
        substrate_runtime_version: str | None,
    ) -> DimaQueryReceipt:
        ...


@runtime_checkable
class AnalyticsSubstrate(Protocol):
    def inspect_capabilities(self) -> SubstrateCapabilities:
        ...

    def validate_execution_intent(
        self,
        intent: ResolvedAnalyticsIntent,
    ) -> ExecutionIntentValidation:
        ...

    def execute_execution_intent(
        self,
        intent: ResolvedAnalyticsIntent,
    ) -> SubstrateExecutionResult:
        ...

    def inspect_execution(
        self,
        execution: SubstrateExecutionResult,
    ) -> ExecutionInspection:
        ...
