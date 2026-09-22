"""Governed Day7 RELATIONSHIP execution through existing Wren/Core analytics.

No SQL or join key is authored here. The adapter:
1) reconstructs CrossDomainJoinFacts from accepted handles + current Wren truth,
2) requires CrossDomainJoinGate ALLOW,
3) reuses ManagerCoreAnalyticsAdapter / CubePlanner / Wren / QueryContract,
4) returns verified relationship Evidence.

The initial executable primitive is a source metric grouped by a governed counterpart
dimension that already belongs to the source cube (local FK or Wren relationship-derived
attribute). This keeps execution inside the existing Wren semantic cube while the
cross-domain fact receipt proves what target business entity/attribute it represents.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.v2.cross_domain_facts import (
    CrossDomainJoinFactBuilder,
    CrossDomainJoinFactResult,
)
from app.v2.manager_core_adapter import (
    ManagerCoreAdapterError,
    ManagerCoreAnalyticsAdapter,
)
from app.v2.manager_tools import RunAnalyticsArgs, RunRelationshipArgs
from app.v2.models import EvidenceArtifact, TenantAnalyticsRuntimeV0


@dataclass(frozen=True)
class GovernedRelationshipExecutionContext:
    tenant_binding: str
    principal: object
    service: object
    tenant_runtime: TenantAnalyticsRuntimeV0
    contract_store: object
    session_id: str | None = None


@dataclass(frozen=True)
class GovernedRelationshipResult:
    available: bool
    evidence: EvidenceArtifact | None
    facts: CrossDomainJoinFactResult
    query_count: int = 0
    reason: str | None = None


class GovernedRelationshipAdapter:
    """Narrow Wren-native relationship primitive; never a generic join engine."""

    def __init__(
        self,
        *,
        fact_builder: CrossDomainJoinFactBuilder,
        core_analytics: ManagerCoreAnalyticsAdapter,
        context: GovernedRelationshipExecutionContext,
    ) -> None:
        self._facts = fact_builder
        self._core = core_analytics
        self._context = context

    @staticmethod
    def _obligation(runtime, obligation_id: str):
        ledger = runtime.ledger
        if ledger is None:
            return None
        return next(
            (
                item
                for item in ledger.items
                if item.obligation_id == obligation_id
            ),
            None,
        )

    def run(self, args: RunRelationshipArgs, runtime) -> GovernedRelationshipResult:
        contract = runtime.accepted_contract
        obligation = self._obligation(runtime, args.obligation_id)
        if contract is None or obligation is None:
            return GovernedRelationshipResult(
                available=False,
                evidence=None,
                facts=CrossDomainJoinFactResult(
                    ready=False,
                    code="INVALID_OBLIGATION",
                    reason="accepted Research contract/obligation is unavailable",
                ),
                reason="accepted Research contract/obligation is unavailable",
            )

        facts = self._facts.build(
            args=args,
            obligation=obligation,
            service=self._context.service,
        )
        if not facts.ready or facts.facts is None or facts.gate_decision is None:
            return GovernedRelationshipResult(
                available=False,
                evidence=None,
                facts=facts,
                reason=facts.reason,
            )

        # The counterpart handle is already an accepted source-cube dimension.  Wren
        # relationship provenance proves whether it denotes a target row key or target
        # analytical attribute.  Core analytics therefore needs no new SQL/join DSL.
        analytics_args = RunAnalyticsArgs(
            research_task_id=args.research_task_id,
            obligation_ids=(args.obligation_id,),
            metric_handles=args.focus_handles,
            dimension_handles=args.counterpart_handles,
        )
        try:
            result = self._core.run(
                analytics_args,
                task_id=(
                    args.research_task_id
                    or f"relationship:{args.obligation_id}"
                ),
                accepted_contract=contract,
                tenant_binding=self._context.tenant_binding,
                principal=self._context.principal,
                service=self._context.service,
                runtime=self._context.tenant_runtime,
                contract_store=self._context.contract_store,
                session_id=self._context.session_id,
                allowed_obligation_ids={args.obligation_id},
                provenance_extra={
                    "kind": "cross_domain_relationship",
                    "facts": facts.facts.model_dump(mode="json"),
                    "gate_decision": facts.gate_decision.model_dump(mode="json"),
                },
                evidence_kind="relationship_analytics",
            )
        except ManagerCoreAdapterError as exc:
            return GovernedRelationshipResult(
                available=False,
                evidence=None,
                facts=facts,
                reason=f"governed relationship analytics failed: {exc}",
            )

        return GovernedRelationshipResult(
            available=True,
            evidence=result.evidence,
            facts=facts,
            query_count=result.query_count,
        )
