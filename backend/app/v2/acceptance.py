"""Deterministic acceptance boundary for Day 6.5 Manager proposals."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.v2.capability_bindings import CapabilityBinding, CapabilityBindingValidator
from app.v2.manager_models import (
    AcceptedTurnContract,
    AcceptanceResult,
    AcceptanceStatus,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    SemanticResolutionReceipt,
    UserIntentEnvelope,
    UserObligationLedger,
)
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityLane,
    ManagerCapabilityRegistry,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_authority import AcceptedAuthorityConflict


class AcceptedContractRegistry:
    """Exactly-one accepted semantic authority per non-clarification turn."""

    def __init__(self) -> None:
        self._by_turn: dict[str, AcceptedTurnContract] = {}
        self._active_by_lineage: dict[str, AcceptedTurnContract] = {}

    def validate(self, contract: AcceptedTurnContract) -> None:
        """Validate turn/lineage commit without mutating registry state."""
        existing_turn = self._by_turn.get(contract.turn_id)
        if existing_turn is not None:
            if existing_turn.contract_id == contract.contract_id:
                return
            raise AcceptedAuthorityConflict(
                f"turn {contract.turn_id} already has accepted contract "
                f"{existing_turn.contract_id}"
            )
        current = self._active_by_lineage.get(contract.lineage_id)
        if current is not None:
            if contract.supersedes_contract_id != current.contract_id:
                raise AcceptedAuthorityConflict(
                    "new contract version must supersede active lineage head"
                )
            if contract.version != current.version + 1:
                raise AcceptedAuthorityConflict(
                    "contract version must increase monotonically"
                )
        elif contract.version != 1 or contract.supersedes_contract_id is not None:
            raise AcceptedAuthorityConflict("new lineage must start at version 1")

    def commit(self, contract: AcceptedTurnContract) -> None:
        self.validate(contract)
        existing_turn = self._by_turn.get(contract.turn_id)
        if existing_turn is not None:
            # validate() guarantees an existing row is the exact idempotent retry.
            return
        self._by_turn[contract.turn_id] = contract
        self._active_by_lineage[contract.lineage_id] = contract

    def active(self, lineage_id: str) -> AcceptedTurnContract | None:
        return self._active_by_lineage.get(lineage_id)


class IntentAcceptanceGate:
    """Verify deterministic authority facts; never infer human intent heuristically."""

    def __init__(
        self,
        *,
        source_spans: SourceSpanRegistry,
        semantic_handles: SemanticHandleRegistry,
        capabilities: ManagerCapabilityRegistry | None = None,
    ) -> None:
        self._source_spans = source_spans
        self._semantic_handles = semantic_handles
        self._capabilities = capabilities or ManagerCapabilityRegistry()
        self._bindings = CapabilityBindingValidator(
            semantic_handles=semantic_handles,
            capabilities=self._capabilities,
        )

    def _validate_effect_conflicts(
        self,
        *,
        items,
        bindings: dict[str, CapabilityBinding],
    ) -> tuple[str, ...]:
        """Detect contradictory semantic effects, independent of capability wording."""
        conflicts: list[str] = []
        seen: list[tuple[object, ObligationPolarity, str]] = []
        for item in items:
            binding = bindings.get(item.obligation_id)
            if binding is None:
                continue
            for effect in binding.effects:
                for previous_effect, previous_polarity, previous_id in seen:
                    if (
                        previous_polarity != item.polarity
                        and effect.conflicts_with(previous_effect)
                    ):
                        conflicts.append(
                            "conflicting semantic effect "
                            f"{effect.family}/{effect.scope_kind}/{effect.scope_ref} "
                            f"between {previous_id} and {item.obligation_id}"
                        )
                seen.append((effect, item.polarity, item.obligation_id))
        return tuple(dict.fromkeys(conflicts))

    def _validate_semantic_binding_provenance(
        self,
        *,
        envelope: UserIntentEnvelope,
        semantic_receipts: tuple[SemanticResolutionReceipt, ...],
        tenant_binding: str,
        context_version: str,
    ) -> tuple[str, ...]:
        """Validate exact runtime-minted source->handle provenance edges.

        This is anti-laundering only, never intent-completeness inference. No containment
        or language heuristics are used. A current-turn runtime binding receipt is covered
        only by an exact SemanticBindingRef carried by an obligation, and every declared
        SemanticBindingRef must correspond to a current runtime binding receipt.
        """
        reasons: list[str] = []
        current_receipts: dict[tuple[str, str, str], SemanticResolutionReceipt] = {}
        for receipt in semantic_receipts:
            try:
                self._source_spans.validate(
                    receipt.source_ref,
                    expected_message_hash=envelope.source_message_hash,
                )
            except (KeyError, ValueError):
                continue
            current_receipts[
                (receipt.source_ref, receipt.handle_id, receipt.target_kind)
            ] = receipt

        declared_keys: set[tuple[str, str, str]] = set()
        for item in envelope.obligations:
            for binding in item.semantic_bindings:
                key = (
                    binding.source_ref,
                    binding.handle_id,
                    binding.target_kind,
                )
                declared_keys.add(key)
                try:
                    self._source_spans.validate(
                        binding.source_ref,
                        expected_message_hash=envelope.source_message_hash,
                    )
                except (KeyError, ValueError) as exc:
                    reasons.append(
                        f"invalid semantic binding source {binding.source_ref}: {exc}"
                    )
                    continue
                try:
                    handle = self._semantic_handles.validate(
                        binding.handle_id,
                        tenant_binding=tenant_binding,
                        context_version=context_version,
                    )
                except (KeyError, ValueError) as exc:
                    reasons.append(
                        f"invalid semantic binding handle {binding.handle_id}: {exc}"
                    )
                    continue
                if handle.target_kind != binding.target_kind:
                    reasons.append(
                        "semantic binding target kind mismatch: "
                        f"{binding.source_ref}/{binding.target_kind}"
                    )
                if binding.handle_id not in item.semantic_handle_refs:
                    reasons.append(
                        "semantic binding handle omitted from obligation handle refs: "
                        f"{item.obligation_id}/{binding.handle_id}"
                    )
                if key not in current_receipts:
                    reasons.append(
                        "semantic binding lacks current runtime semantic binding receipt: "
                        f"{binding.source_ref}/{binding.target_kind}"
                    )

        for key, receipt in current_receipts.items():
            if key not in declared_keys:
                reasons.append(
                    "runtime-bound user semantic source omitted from explicit binding graph: "
                    f"{receipt.source_ref}/{receipt.target_kind}"
                )

        return tuple(dict.fromkeys(reasons))

    def evaluate(
        self,
        *,
        envelope: UserIntentEnvelope,
        tenant_binding: str,
        context_version: str,
        active_contract: AcceptedTurnContract | None = None,
        active_ledger: UserObligationLedger | None = None,
        lineage_id: str | None = None,
        semantic_receipts: tuple[SemanticResolutionReceipt, ...] | None = None,
    ) -> AcceptanceResult:
        reject: list[str] = []
        clarify: list[str] = []

        if active_contract is not None and active_contract.turn_id == envelope.turn_id:
            reject.append("same turn already has accepted semantic authority")

        if envelope.unresolved_source_refs:
            clarify.append("unresolved source refs remain")

        active_ids = {
            item.obligation_id
            for item in (active_ledger.items if active_ledger is not None else ())
        }
        candidate_ids = {
            *active_ids,
            *(item.obligation_id for item in envelope.obligations),
        }

        if active_contract is not None:
            if active_ledger is None:
                reject.append(
                    "active contract versioning requires active obligation ledger"
                )
            elif (
                active_ledger.lineage_id != active_contract.lineage_id
                or active_ledger.version != active_contract.version
            ):
                reject.append(
                    "active obligation ledger does not match active contract head"
                )
        elif active_ledger is not None:
            reject.append("active obligation ledger cannot exist without active contract")

        current_bindings: dict[str, CapabilityBinding] = {}

        obligation_by_id = {item.obligation_id: item for item in envelope.obligations}
        for directive in envelope.research_directives:
            parent = obligation_by_id.get(directive.parent_obligation_id)
            if parent is None:
                reject.append(
                    f"research directive {directive.directive_id} parent obligation missing"
                )
                continue
            if parent.polarity != ObligationPolarity.REQUIRED:
                reject.append(
                    "research directive parent must be REQUIRED research obligation"
                )
            try:
                parent_spec = self._capabilities.get(parent.capability_key)
            except KeyError:
                parent_spec = None
            if parent_spec is None:
                reject.append(
                    "research directive parent capability is not registered"
                )
            elif (
                parent_spec.execution_mode
                not in {
                    ManagerCapabilityExecutionMode.DIRECT,
                    ManagerCapabilityExecutionMode.ORCHESTRATED,
                }
                or parent_spec.lane
                not in {
                    ManagerCapabilityLane.STANDARD,
                    ManagerCapabilityLane.RESEARCH,
                }
            ):
                reject.append(
                    "research directive parent must be active analytical authority"
                )
            for source_ref in directive.source_refs:
                try:
                    span = self._source_spans.validate(source_ref)
                except (KeyError, ValueError) as exc:
                    reject.append(
                        f"invalid research directive source ref {source_ref}: {exc}"
                    )
                    continue
                if span.message_hash != envelope.source_message_hash:
                    reject.append(
                        f"research directive {directive.directive_id} is not grounded "
                        "in current source hash"
                    )

        for item in envelope.obligations:
            if item.origin == ObligationOrigin.USER_MUST:
                if item.priority != ObligationPriority.MUST:
                    reject.append(
                        f"USER_MUST {item.obligation_id} must use MUST priority"
                    )

            if item.origin == ObligationOrigin.AGENT_DERIVED:
                reject.append(
                    "AGENT_DERIVED obligation cannot enter initial accepted user contract"
                )

            if (
                item.parent_obligation_id
                and item.parent_obligation_id not in candidate_ids
            ):
                reject.append(
                    f"unknown parent obligation: {item.parent_obligation_id}"
                )

            for source_ref in item.source_refs:
                try:
                    span = self._source_spans.validate(source_ref)
                except (KeyError, ValueError) as exc:
                    reject.append(f"invalid source ref {source_ref}: {exc}")
                    continue
                if (
                    item.origin
                    in {ObligationOrigin.USER_MUST, ObligationOrigin.USER_OPTIONAL}
                    and span.message_hash != envelope.source_message_hash
                ):
                    reject.append(
                        f"user obligation {item.obligation_id} is not grounded "
                        "in current source hash"
                    )

            binding_result = self._bindings.validate(
                item,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )
            if not binding_result.valid:
                reject.extend(binding_result.reasons)
            elif binding_result.binding is not None:
                current_bindings[item.obligation_id] = binding_result.binding

        if semantic_receipts is not None:
            reject.extend(
                self._validate_semantic_binding_provenance(
                    envelope=envelope,
                    semantic_receipts=semantic_receipts,
                    tenant_binding=tenant_binding,
                    context_version=context_version,
                )
            )

        replaced_ids = {item.obligation_id for item in envelope.obligations}
        carried_items = tuple(
            item
            for item in (active_ledger.items if active_ledger is not None else ())
            if item.obligation_id not in replaced_ids
            and item.status != ObligationStatus.SUPERSEDED
        )
        effective_items = (*carried_items, *envelope.obligations)

        # Revalidate carried authority defensively against the current contract algebra.
        effective_bindings = dict(current_bindings)
        for item in carried_items:
            result = self._bindings.validate(
                item,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )
            if not result.valid:
                reject.extend(
                    f"carried obligation {item.obligation_id}: {reason}"
                    for reason in result.reasons
                )
            elif result.binding is not None:
                effective_bindings[item.obligation_id] = result.binding

        has_required_user_must = any(
            item.origin == ObligationOrigin.USER_MUST
            and item.priority == ObligationPriority.MUST
            and item.polarity == ObligationPolarity.REQUIRED
            for item in effective_items
        )
        if not has_required_user_must:
            reject.append(
                "analytical contract requires at least one REQUIRED USER_MUST obligation"
            )

        clarify.extend(
            self._validate_effect_conflicts(
                items=effective_items,
                bindings=effective_bindings,
            )
        )

        if reject:
            return AcceptanceResult(
                status=AcceptanceStatus.REJECTED,
                reasons=tuple(dict.fromkeys(reject)),
            )
        if clarify:
            return AcceptanceResult(
                status=AcceptanceStatus.NEEDS_CLARIFICATION,
                reasons=tuple(dict.fromkeys(clarify)),
            )

        lineage = lineage_id or (
            active_contract.lineage_id
            if active_contract is not None
            else "atl_"
            + hashlib.sha256(envelope.request_ref.encode("utf-8")).hexdigest()[:20]
        )
        version = active_contract.version + 1 if active_contract is not None else 1
        supersedes = (
            active_contract.contract_id if active_contract is not None else None
        )

        contract_payload = (
            f"{lineage}\x1f{version}\x1f{envelope.turn_id}\x1f"
            f"{envelope.attempt_id}\x1f{context_version}\x1f"
            f"{envelope.source_message_hash}"
        )
        contract_id = (
            "atc_"
            + hashlib.sha256(contract_payload.encode("utf-8")).hexdigest()[:24]
        )

        current_items = tuple(
            ObligationLedgerItem(
                obligation_id=item.obligation_id,
                capability_key=item.capability_key,
                origin=item.origin,
                parent_obligation_id=item.parent_obligation_id,
                priority=item.priority,
                polarity=item.polarity,
                status=ObligationStatus.ACCEPTED,
                source_refs=item.source_refs,
                semantic_handle_refs=item.semantic_handle_refs,
                semantic_bindings=item.semantic_bindings,
                ranking_direction=item.ranking_direction,
                ranking_limit=item.ranking_limit,
                introduced_in_version=version,
            )
            for item in envelope.obligations
        )
        current_ids = {item.obligation_id for item in current_items}
        carried_ledger_items = tuple(
            item
            for item in (active_ledger.items if active_ledger is not None else ())
            if item.obligation_id not in current_ids
            and item.status != ObligationStatus.SUPERSEDED
        )
        committed_items = (*carried_ledger_items, *current_items)

        obligation_ids = tuple(
            item.obligation_id
            for item in committed_items
            if item.polarity == ObligationPolarity.REQUIRED
        )
        exclusion_ids = tuple(
            item.obligation_id
            for item in committed_items
            if item.polarity == ObligationPolarity.EXCLUDED
        )

        contract = AcceptedTurnContract(
            contract_id=contract_id,
            lineage_id=lineage,
            version=version,
            supersedes_contract_id=supersedes,
            turn_id=envelope.turn_id,
            request_ref=envelope.request_ref,
            source_message_hash=envelope.source_message_hash,
            accepted_attempt_id=envelope.attempt_id,
            model_role=envelope.model_role,
            obligation_ids=obligation_ids,
            exclusion_ids=exclusion_ids,
            research_directives=envelope.research_directives,
            unresolved_ids=(),
            context_version=context_version,
            accepted_at_iso=datetime.now(timezone.utc).isoformat(),
        )

        ledger = UserObligationLedger(
            lineage_id=lineage,
            version=version,
            items=committed_items,
        )

        return AcceptanceResult(
            status=AcceptanceStatus.ACCEPTED,
            contract=contract,
            ledger=ledger,
        )
