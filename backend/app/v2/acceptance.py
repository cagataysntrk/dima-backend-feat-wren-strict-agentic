"""Deterministic acceptance boundary for Day 6.5 Manager proposals."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.v2.manager_models import (
    AcceptedTurnContract,
    AcceptanceResult,
    AcceptanceStatus,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    UserIntentEnvelope,
    UserObligationLedger,
)
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


class AcceptedAuthorityConflict(RuntimeError):
    pass


class AcceptedContractRegistry:
    """Exactly-one accepted semantic authority per non-clarification turn."""

    def __init__(self) -> None:
        self._by_turn: dict[str, AcceptedTurnContract] = {}
        self._active_by_lineage: dict[str, AcceptedTurnContract] = {}

    def commit(self, contract: AcceptedTurnContract) -> None:
        existing_turn = self._by_turn.get(contract.turn_id)
        if existing_turn is not None:
            if existing_turn.contract_id == contract.contract_id:
                return  # idempotent retry of the same accepted authority
            raise AcceptedAuthorityConflict(
                f"turn {contract.turn_id} already has accepted contract {existing_turn.contract_id}"
            )
        current = self._active_by_lineage.get(contract.lineage_id)
        if current is not None:
            if contract.supersedes_contract_id != current.contract_id:
                raise AcceptedAuthorityConflict("new contract version must supersede active lineage head")
            if contract.version != current.version + 1:
                raise AcceptedAuthorityConflict("contract version must increase monotonically")
        elif contract.version != 1 or contract.supersedes_contract_id is not None:
            raise AcceptedAuthorityConflict("new lineage must start at version 1")

        self._by_turn[contract.turn_id] = contract
        self._active_by_lineage[contract.lineage_id] = contract

    def active(self, lineage_id: str) -> AcceptedTurnContract | None:
        return self._active_by_lineage.get(lineage_id)


class IntentAcceptanceGate:
    """Verify source/provenance/authority facts; never judge human intent by heuristics."""

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

    def evaluate(
        self,
        *,
        envelope: UserIntentEnvelope,
        tenant_binding: str,
        context_version: str,
        active_contract: AcceptedTurnContract | None = None,
        active_ledger: UserObligationLedger | None = None,
        lineage_id: str | None = None,
    ) -> AcceptanceResult:
        reject: list[str] = []
        clarify: list[str] = []

        if active_contract is not None and active_contract.turn_id == envelope.turn_id:
            reject.append("same turn already has accepted semantic authority")

        if envelope.unresolved_source_refs:
            clarify.append("unresolved source refs remain")

        seen_polarity: dict[tuple[str, str], ObligationPolarity] = {}
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
                reject.append("active contract versioning requires active obligation ledger")
            elif (
                active_ledger.lineage_id != active_contract.lineage_id
                or active_ledger.version != active_contract.version
            ):
                reject.append("active obligation ledger does not match active contract head")
        elif active_ledger is not None:
            reject.append("active obligation ledger cannot exist without active contract")

        for item in envelope.obligations:
            if not self._capabilities.registered(item.capability_key):
                reject.append(f"unregistered capability: {item.capability_key.value}")

            if item.origin == ObligationOrigin.USER_MUST and item.priority != ObligationPriority.MUST:
                reject.append(f"USER_MUST {item.obligation_id} must use MUST priority")

            if item.origin == ObligationOrigin.AGENT_DERIVED:
                # Derived investigations are research-state additions, not user-intent acceptance.
                reject.append("AGENT_DERIVED obligation cannot enter initial accepted user contract")

            if item.parent_obligation_id and item.parent_obligation_id not in candidate_ids:
                reject.append(f"unknown parent obligation: {item.parent_obligation_id}")

            for source_ref in item.source_refs:
                try:
                    span = self._source_spans.validate(source_ref)
                except (KeyError, ValueError) as exc:
                    reject.append(f"invalid source ref {source_ref}: {exc}")
                    continue
                if (
                    item.origin in {ObligationOrigin.USER_MUST, ObligationOrigin.USER_OPTIONAL}
                    and span.message_hash != envelope.source_message_hash
                ):
                    reject.append(
                        f"user obligation {item.obligation_id} is not grounded in current source hash"
                    )

            for handle_id in item.semantic_handle_refs:
                try:
                    self._semantic_handles.validate(
                        handle_id,
                        tenant_binding=tenant_binding,
                        context_version=context_version,
                    )
                except (KeyError, ValueError) as exc:
                    reject.append(f"invalid semantic handle {handle_id}: {exc}")

            spec = self._capabilities.get(item.capability_key)
            if (
                item.origin == ObligationOrigin.USER_MUST
                and item.priority == ObligationPriority.MUST
                and item.polarity == ObligationPolarity.REQUIRED
                and spec.executable
                and spec.lane == ManagerCapabilityLane.STANDARD
                and not item.semantic_handle_refs
            ):
                reject.append(
                    f"standard USER_MUST {item.obligation_id} requires Resolver-issued semantic handles before acceptance"
                )

            if item.open_questions and item.priority == ObligationPriority.MUST:
                clarify.append(f"MUST obligation {item.obligation_id} has open questions")

            polarity_key = (item.capability_key.value, "|".join(sorted(item.source_refs)))
            previous = seen_polarity.get(polarity_key)
            if previous is not None and previous != item.polarity:
                clarify.append(
                    f"conflicting polarity for {item.capability_key.value} on same source"
                )
            else:
                seen_polarity[polarity_key] = item.polarity

        has_required_user_must = any(
            item.origin == ObligationOrigin.USER_MUST
            and item.priority == ObligationPriority.MUST
            and item.polarity == ObligationPolarity.REQUIRED
            for item in envelope.obligations
        )
        if not has_required_user_must:
            reject.append(
                "analytical contract requires at least one REQUIRED USER_MUST obligation"
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
            else "atl_" + hashlib.sha256(envelope.request_ref.encode("utf-8")).hexdigest()[:20]
        )
        version = active_contract.version + 1 if active_contract is not None else 1
        supersedes = active_contract.contract_id if active_contract is not None else None

        contract_payload = (
            f"{lineage}\x1f{version}\x1f{envelope.turn_id}\x1f{envelope.attempt_id}"
            f"\x1f{context_version}\x1f{envelope.source_message_hash}"
        )
        contract_id = "atc_" + hashlib.sha256(contract_payload.encode("utf-8")).hexdigest()[:24]

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
                introduced_in_version=version,
            )
            for item in envelope.obligations
        )
        replaced_ids = {item.obligation_id for item in current_items}
        carried_items = tuple(
            item
            for item in (active_ledger.items if active_ledger is not None else ())
            if item.obligation_id not in replaced_ids
            and item.status != ObligationStatus.SUPERSEDED
        )
        effective_items = (*carried_items, *current_items)

        obligation_ids = tuple(
            item.obligation_id
            for item in effective_items
            if item.polarity == ObligationPolarity.REQUIRED
        )
        exclusion_ids = tuple(
            item.obligation_id
            for item in effective_items
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
            unresolved_ids=(),
            context_version=context_version,
            accepted_at_iso=datetime.now(timezone.utc).isoformat(),
        )

        ledger = UserObligationLedger(
            lineage_id=lineage,
            version=version,
            items=effective_items,
        )

        return AcceptanceResult(
            status=AcceptanceStatus.ACCEPTED,
            contract=contract,
            ledger=ledger,
        )
