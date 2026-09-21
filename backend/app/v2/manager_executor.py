"""Governed executor boundary for the bounded Day 6.5 Manager.

Only declared Manager tools are executable. Standard analytics reuses the existing Core
trust plane. Relationship/semantic adapters are injected explicitly; no hidden fallback
or raw SQL path exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry
from app.v2.obligation_ledger import UserObligationLedgerService
from app.v2.manager_tools import (
    ManagerToolCall,
    ManagerToolName,
    ProposeAcceptanceArgs,
    RequestClarificationArgs,
    ResolveSemanticsArgs,
    RunAnalyticsArgs,
    RunRelationshipArgs,
    InspectEvidenceArgs,
    ManagerAnalyticsObservation,
)
from app.v2.models import EvidenceArtifact


class SemanticResolutionExecutor(Protocol):
    def resolve(self, args: ResolveSemanticsArgs, runtime) -> Any: ...


class RelationshipToolExecutor(Protocol):
    def run(self, args: RunRelationshipArgs, runtime) -> Any: ...


class EvidenceStore:
    def __init__(self) -> None:
        self._items: dict[str, EvidenceArtifact] = {}

    def put(self, artifact: EvidenceArtifact) -> None:
        self._items[artifact.artifact_id] = artifact

    def get(self, artifact_id: str) -> EvidenceArtifact:
        try:
            return self._items[artifact_id]
        except KeyError as exc:
            raise KeyError(f"unknown evidence artifact: {artifact_id}") from exc


@dataclass(frozen=True)
class GovernedManagerExecutionContext:
    tenant_binding: str
    context_version: str
    principal: Any
    service: Any
    tenant_runtime: Any
    contract_store: Any
    session_id: str | None = None


class GovernedManagerExecutor:
    def __init__(
        self,
        *,
        acceptance: IntentAcceptanceGate,
        core_analytics: ManagerCoreAnalyticsAdapter,
        context: GovernedManagerExecutionContext,
        evidence: EvidenceStore | None = None,
        semantic_resolution: SemanticResolutionExecutor | None = None,
        relationship: RelationshipToolExecutor | None = None,
        obligation_ledger: UserObligationLedgerService | None = None,
        capabilities: ManagerCapabilityRegistry | None = None,
    ) -> None:
        self._acceptance = acceptance
        self._core = core_analytics
        self._context = context
        self._evidence = evidence or EvidenceStore()
        self._semantic_resolution = semantic_resolution
        self._relationship = relationship
        self._obligations = obligation_ledger or UserObligationLedgerService()
        self._capabilities = capabilities or ManagerCapabilityRegistry()

    @property
    def evidence_store(self) -> EvidenceStore:
        return self._evidence

    def execute(self, call: ManagerToolCall, validated_args: Any, runtime) -> Any:
        if call.name == ManagerToolName.PROPOSE_ACCEPTANCE:
            assert isinstance(validated_args, ProposeAcceptanceArgs)
            return self._acceptance.evaluate(
                envelope=validated_args.envelope,
                tenant_binding=self._context.tenant_binding,
                context_version=self._context.context_version,
                active_contract=runtime.accepted_contract,
            )

        if call.name == ManagerToolName.RESOLVE_SEMANTICS:
            assert isinstance(validated_args, ResolveSemanticsArgs)
            if self._semantic_resolution is None:
                raise RuntimeError("resolve_semantics adapter not configured")
            return self._semantic_resolution.resolve(validated_args, runtime)

        if call.name == ManagerToolName.RUN_ANALYTICS:
            assert isinstance(validated_args, RunAnalyticsArgs)
            contract = runtime.accepted_contract
            if contract is None:
                raise RuntimeError("run_analytics requires accepted contract")
            result = self._core.run(
                validated_args,
                task_id=f"task:{runtime.snapshot.tool_calls}",
                accepted_contract=contract,
                tenant_binding=self._context.tenant_binding,
                principal=self._context.principal,
                service=self._context.service,
                runtime=self._context.tenant_runtime,
                contract_store=self._context.contract_store,
                session_id=self._context.session_id,
            )
            if result.query_count > 1:
                runtime.note_additional_data_queries(result.query_count - 1)
            self._evidence.put(result.evidence)
            runtime.attach_evidence(result.evidence.artifact_id)

            ledger = runtime.ledger
            if ledger is None:
                raise RuntimeError("run_analytics completed without obligation ledger")
            for obligation_id in validated_args.obligation_ids:
                item = self._obligations.get(ledger, obligation_id)
                spec = self._capabilities.get(item.capability_key)
                if (
                    spec.lane == ManagerCapabilityLane.STANDARD
                    and result.evidence.verified
                ):
                    ledger = self._obligations.verify(
                        ledger,
                        obligation_id,
                        evidence_refs=(result.evidence.artifact_id,),
                        verdict="governed standard analytics + QueryContract verified",
                    )
            runtime.replace_ledger(ledger)
            row_count = sum(
                int(item.get("row_count") or 0)
                for item in (result.evidence.payload.get("executions") or ())
            )
            return ManagerAnalyticsObservation(
                evidence_ref=result.evidence.artifact_id,
                verified=result.evidence.verified,
                query_count=result.query_count,
                row_count=row_count,
                limitations=result.evidence.limitations,
            )

        if call.name == ManagerToolName.RUN_RELATIONSHIP:
            assert isinstance(validated_args, RunRelationshipArgs)
            if self._relationship is None:
                raise RuntimeError("run_relationship adapter not configured")
            result = self._relationship.run(validated_args, runtime)
            artifact = getattr(result, "evidence", None)
            if isinstance(artifact, EvidenceArtifact):
                self._evidence.put(artifact)
                runtime.attach_evidence(artifact.artifact_id)
            return result

        if call.name == ManagerToolName.INSPECT_EVIDENCE:
            assert isinstance(validated_args, InspectEvidenceArgs)
            return self._evidence.get(validated_args.evidence_ref)

        if call.name == ManagerToolName.REQUEST_CLARIFICATION:
            assert isinstance(validated_args, RequestClarificationArgs)
            return validated_args

        raise RuntimeError(f"undeclared Manager tool reached executor: {call.name}")
