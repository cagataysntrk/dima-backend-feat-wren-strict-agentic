"""Governed executor boundary for the bounded Day 6.5 Manager.

Only declared Manager tools are executable. Standard analytics reuses the existing Core
trust plane. Manager proposals never become semantic/execution/completion truth by
themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_core_adapter import (
    ManagerCoreAdapterError,
    ManagerCoreAnalyticsAdapter,
)
from app.v2.manager_errors import (
    ManagerAuthorityViolation,
    ManagerProjectionIncomplete,
    ManagerSemanticGap,
    ManagerUnsupportedCapability,
)
from app.v2.manager_models import (
    ObligationStatus,
    RepresentabilityDecision,
)
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry
from app.v2.obligation_ledger import UserObligationLedgerService
from app.v2.obligation_verifier import StandardObligationVerifier
from app.v2.representability import RepresentabilityGate
from app.v2.standard_authority import AcceptedAuthorityFamily
from app.v2.manager_tools import (
    InspectEvidenceArgs,
    ManagerAnalyticsObservation,
    ManagerRelationshipObservation,
    ManagerToolCall,
    ManagerToolName,
    ProposeAcceptanceArgs,
    RequestClarificationArgs,
    ResolveSemanticsArgs,
    RunAnalyticsArgs,
    RunRelationshipArgs,
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
            raise ManagerSemanticGap(f"unknown evidence artifact: {artifact_id}") from exc

    @property
    def count(self) -> int:
        return len(self._items)


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
        representability: RepresentabilityGate | None = None,
        obligation_verifier: StandardObligationVerifier | None = None,
    ) -> None:
        self._acceptance = acceptance
        self._core = core_analytics
        self._context = context
        self._evidence = evidence or EvidenceStore()
        self._semantic_resolution = semantic_resolution
        self._relationship = relationship
        self._obligations = obligation_ledger or UserObligationLedgerService()
        self._capabilities = capabilities or ManagerCapabilityRegistry()
        self._representability = representability or RepresentabilityGate(self._capabilities)
        self._obligation_verifier = obligation_verifier or StandardObligationVerifier()

    @property
    def evidence_store(self) -> EvidenceStore:
        return self._evidence

    @property
    def principal(self):
        """Verified request identity used by governed execution; may be None only in tests/miswire."""
        return self._context.principal

    @property
    def tenant_binding(self) -> str:
        """Tenant authority bound into this governed execution context."""
        return self._context.tenant_binding

    @property
    def tenant_runtime(self):
        """Typed tenant/runtime identity; authorization compares like-for-like fields."""
        return self._context.tenant_runtime

    def _validate_derived_semantic_provenance(
        self,
        args: ResolveSemanticsArgs,
        runtime,
    ) -> None:
        if args.provenance != "AGENT_DERIVED":
            return
        if runtime.accepted_contract is None or runtime.ledger is None:
            raise ManagerAuthorityViolation(
                "AGENT_DERIVED semantic resolution requires accepted contract"
            )
        parent = self._obligations.get(runtime.ledger, args.parent_obligation_id)
        if parent.status == ObligationStatus.SUPERSEDED:
            raise ManagerAuthorityViolation("derived semantic proposal parent is superseded")
        evidence = self._evidence.get(args.evidence_ref)
        if args.evidence_ref not in runtime.snapshot.evidence_refs:
            raise ManagerAuthorityViolation(
                "derived semantic proposal evidence is not attached to current run"
            )
        if not evidence.verified:
            raise ManagerSemanticGap(
                "derived semantic proposal requires verified execution evidence"
            )

    def execute(
        self,
        call: ManagerToolCall,
        validated_args: Any,
        runtime,
        *,
        commit_guard: Callable[[], None] | None = None,
    ) -> Any:
        if call.name == ManagerToolName.PROPOSE_ACCEPTANCE:
            assert isinstance(validated_args, ProposeAcceptanceArgs)
            return self._acceptance.evaluate(
                envelope=validated_args.envelope,
                tenant_binding=self._context.tenant_binding,
                context_version=self._context.context_version,
                active_contract=runtime.accepted_contract,
                active_ledger=runtime.ledger,
                semantic_receipts=runtime.semantic_resolution_receipts,
            )

        if call.name == ManagerToolName.RESOLVE_SEMANTICS:
            assert isinstance(validated_args, ResolveSemanticsArgs)
            if self._semantic_resolution is None:
                raise ManagerSemanticGap("resolve_semantics adapter not configured")
            self._validate_derived_semantic_provenance(validated_args, runtime)
            return self._semantic_resolution.resolve(validated_args, runtime)

        if call.name == ManagerToolName.RUN_ANALYTICS:
            assert isinstance(validated_args, RunAnalyticsArgs)
            contract = runtime.accepted_contract
            ledger = runtime.ledger
            if contract is None or ledger is None:
                raise ManagerAuthorityViolation(
                    "run_analytics requires accepted contract + obligation ledger"
                )

            effective_args = validated_args
            if validated_args.derived_task_id is not None:
                assert validated_args.derived_parent_obligation_id is not None
                assert validated_args.derived_capability_key is not None
                assert validated_args.derived_evidence_ref is not None

                parent = self._obligations.get(
                    ledger,
                    validated_args.derived_parent_obligation_id,
                )
                if parent.status == ObligationStatus.SUPERSEDED:
                    raise ManagerAuthorityViolation(
                        "derived analytics parent obligation is superseded"
                    )

                evidence = self._evidence.get(validated_args.derived_evidence_ref)
                if validated_args.derived_evidence_ref not in runtime.snapshot.evidence_refs:
                    raise ManagerAuthorityViolation(
                        "derived analytics evidence is not attached to current run"
                    )
                if not evidence.verified:
                    raise ManagerSemanticGap(
                        "derived analytics requires verified execution evidence"
                    )
                if validated_args.derived_parent_obligation_id not in evidence.obligation_ids:
                    raise ManagerAuthorityViolation(
                        "derived analytics evidence does not support declared parent obligation"
                    )

                derived_spec = self._capabilities.get(
                    validated_args.derived_capability_key
                )
                if derived_spec.lane != ManagerCapabilityLane.STANDARD:
                    raise ManagerUnsupportedCapability(
                        "run_analytics derived branch supports STANDARD capability only"
                    )

                derived_handles = tuple(
                    dict.fromkeys(
                        (
                            *validated_args.metric_handles,
                            *validated_args.dimension_handles,
                            *validated_args.filter_handles,
                            *(() if validated_args.period_handle is None else (validated_args.period_handle,)),
                            *(() if validated_args.comparison_handle is None else (validated_args.comparison_handle,)),
                        )
                    )
                )
                ledger = self._obligations.add_agent_derived(
                    ledger,
                    obligation_id=validated_args.derived_task_id,
                    parent_obligation_id=validated_args.derived_parent_obligation_id,
                    capability_key=validated_args.derived_capability_key,
                    source_refs=(),
                    semantic_handle_refs=derived_handles,
                )
                runtime.replace_ledger(ledger)
                effective_args = validated_args.model_copy(
                    update={"obligation_ids": (validated_args.derived_task_id,)}
                )

            allowed_ids = {item.obligation_id for item in runtime.ledger.items}
            unknown_ids = set(effective_args.obligation_ids) - allowed_ids
            if unknown_ids:
                raise ManagerAuthorityViolation(
                    "run_analytics obligation outside ledger: "
                    + ", ".join(sorted(unknown_ids))
                )

            # Wire RepresentabilityGate into real execution. A pure-standard accepted
            # contract may execute only if this exact projection is lossless. Research
            # contracts may still run standard sub-analyses inside the Manager loop.
            projection = effective_args.to_standard_projection()
            accepted_authority = runtime.authority_registry.accepted(contract.turn_id)
            is_research_authority = (
                accepted_authority is not None
                and accepted_authority[0] == AcceptedAuthorityFamily.RESEARCH
            )
            if is_research_authority and validated_args.derived_task_id is None:
                representation = self._representability.decide_execution_slice(
                    contract=contract,
                    ledger=runtime.ledger,
                    obligation_ids=effective_args.obligation_ids,
                    projection=projection,
                )
            else:
                representation = self._representability.decide(
                    contract=contract,
                    ledger=runtime.ledger,
                    projection=projection,
                )
            if (
                not representation.research_capability_keys
                and representation.decision != RepresentabilityDecision.STANDARD_LOSSLESS
                and validated_args.derived_task_id is None
            ):
                raise ManagerProjectionIncomplete(
                    "; ".join(representation.reasons)
                    or "standard projection is not lossless"
                )

            ledger = runtime.ledger
            for obligation_id in effective_args.obligation_ids:
                item = self._obligations.get(ledger, obligation_id)
                if item.status in {ObligationStatus.ACCEPTED, ObligationStatus.READY}:
                    ledger = self._obligations.start(ledger, obligation_id)
            runtime.replace_ledger(ledger)

            try:
                result = self._core.run(
                    effective_args,
                    task_id=(
                        effective_args.research_task_id
                        or f"task:{runtime.snapshot.tool_calls}"
                    ),
                    accepted_contract=contract,
                    tenant_binding=self._context.tenant_binding,
                    principal=self._context.principal,
                    service=self._context.service,
                    runtime=self._context.tenant_runtime,
                    contract_store=self._context.contract_store,
                    session_id=self._context.session_id,
                    allowed_obligation_ids=allowed_ids
                    | set(effective_args.obligation_ids),
                )
            except ManagerCoreAdapterError as exc:
                raise ManagerSemanticGap(str(exc)) from exc

            if result.query_count > 1:
                runtime.note_additional_data_queries(result.query_count - 1)

            # Day7 lifecycle seam: the ResearchTaskRegistry remains the owner of
            # delivery/cancel state.  A late result must be rejected BEFORE it can
            # become accepted Evidence or verify an obligation.
            if commit_guard is not None:
                commit_guard()

            self._evidence.put(result.evidence)
            runtime.attach_evidence(result.evidence.artifact_id)

            ledger = runtime.ledger
            verified_ids: list[str] = []
            unverified_ids: list[str] = []
            for obligation_id in effective_args.obligation_ids:
                item = self._obligations.get(ledger, obligation_id)
                spec = self._capabilities.get(item.capability_key)
                if spec.lane != ManagerCapabilityLane.STANDARD:
                    unverified_ids.append(obligation_id)
                    continue
                proof = self._obligation_verifier.verify(
                    obligation=item,
                    projection=projection,
                    ir=result.analytics_ir,
                    evidence=result.evidence,
                )
                if proof.verified:
                    ledger = self._obligations.verify(
                        ledger,
                        obligation_id,
                        evidence_refs=(result.evidence.artifact_id,),
                        verdict=(
                            "capability-specific StandardProjection + AnalyticsIR + "
                            "sealed QueryContract verified"
                        ),
                    )
                    verified_ids.append(obligation_id)
                else:
                    unverified_ids.append(obligation_id)

            runtime.replace_ledger(ledger)
            row_count = sum(
                int(item.get("row_count") or 0)
                for item in (result.evidence.payload.get("executions") or ())
            )
            return ManagerAnalyticsObservation(
                evidence_ref=result.evidence.artifact_id,
                evidence_verified=result.evidence.verified,
                query_count=result.query_count,
                row_count=row_count,
                obligations_verified=tuple(verified_ids),
                obligations_unverified=tuple(unverified_ids),
                limitations=result.evidence.limitations,
            )

        if call.name == ManagerToolName.RUN_RELATIONSHIP:
            assert isinstance(validated_args, RunRelationshipArgs)
            ledger = runtime.ledger
            if ledger is None:
                raise ManagerAuthorityViolation("run_relationship requires obligation ledger")
            item = self._obligations.get(ledger, validated_args.obligation_id)
            if item.capability_key.value != "relationship":
                raise ManagerAuthorityViolation(
                    "run_relationship requires accepted RELATIONSHIP obligation"
                )

            if self._relationship is None:
                ledger = self._obligations.block(
                    ledger,
                    validated_args.obligation_id,
                    status=ObligationStatus.UNSUPPORTED,
                    reason=(
                        "verified relationship execution path is not available yet; "
                        "CrossDomainJoinGate required"
                    ),
                )
                runtime.replace_ledger(ledger)
                return ManagerRelationshipObservation(
                    obligation_id=validated_args.obligation_id,
                    available=False,
                    status="UNSUPPORTED",
                    reason="relationship trust-plane adapter unavailable",
                )

            result = self._relationship.run(validated_args, runtime)
            artifact = getattr(result, "evidence", None)
            available = bool(getattr(result, "available", False))
            reason = getattr(result, "reason", None)

            if not available or not isinstance(artifact, EvidenceArtifact):
                ledger = self._obligations.block(
                    runtime.ledger,
                    validated_args.obligation_id,
                    status=ObligationStatus.BLOCKED_DATA_GAP,
                    reason=reason or "governed relationship facts/execution unavailable",
                )
                runtime.replace_ledger(ledger)
                return ManagerRelationshipObservation(
                    obligation_id=validated_args.obligation_id,
                    available=False,
                    status="UNSUPPORTED",
                    reason=reason or "governed relationship execution denied",
                )

            if not artifact.verified or not artifact.query_contract_refs:
                raise ManagerSemanticGap(
                    "relationship execution requires verified Evidence + QueryContract"
                )
            if artifact.evidence_kind != "relationship_analytics":
                raise ManagerSemanticGap(
                    "relationship execution returned unexpected evidence kind"
                )

            query_count = int(getattr(result, "query_count", 0) or 0)
            if query_count > 1:
                runtime.note_additional_data_queries(query_count - 1)

            # Same atomic boundary as standard analytics: cancelled/expired Research
            # task may leave low-level audit receipts, but may never enter accepted
            # Evidence/UOL truth.
            if commit_guard is not None:
                commit_guard()

            self._evidence.put(artifact)
            runtime.attach_evidence(artifact.artifact_id)
            ledger = self._obligations.verify(
                runtime.ledger,
                validated_args.obligation_id,
                evidence_refs=(artifact.artifact_id,),
                verdict=(
                    "governed CrossDomainJoinFacts + CrossDomainJoinGate + "
                    "sealed Wren QueryContract verified"
                ),
            )
            runtime.replace_ledger(ledger)
            return ManagerRelationshipObservation(
                obligation_id=validated_args.obligation_id,
                available=True,
                status="EXECUTED",
                evidence_ref=artifact.artifact_id,
            )

        if call.name == ManagerToolName.INSPECT_EVIDENCE:
            assert isinstance(validated_args, InspectEvidenceArgs)
            if validated_args.evidence_ref not in runtime.snapshot.evidence_refs:
                raise ManagerAuthorityViolation(
                    "inspect_evidence requires evidence attached to current Research run"
                )
            artifact = self._evidence.get(validated_args.evidence_ref)
            runtime.mark_evidence_inspected(validated_args.evidence_ref)
            return artifact

        if call.name == ManagerToolName.REQUEST_CLARIFICATION:
            assert isinstance(validated_args, RequestClarificationArgs)
            return validated_args

        raise ManagerAuthorityViolation(
            f"undeclared Manager tool reached executor: {call.name}"
        )
