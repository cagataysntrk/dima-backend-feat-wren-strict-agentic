"""Day8 provider-free epistemic ledger.

This module is a structural trust boundary only. It validates that hypotheses,
Evidence links, semantic handles and next-test ResearchTasks belong to the current
accepted ROOT_CAUSE investigation. It never executes queries, infers causality or
decides semantic entailment.
"""

from __future__ import annotations

import hashlib
import json

from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationPolarity,
    ObligationStatus,
    UserObligationLedger,
)
from app.v2.models import (
    HypothesisEntry,
    HypothesisEvidenceLink,
    HypothesisEvidenceRelation,
    HypothesisLedgerState,
    HypothesisProvenance,
    HypothesisStatus,
)
from app.v2.obligation_ledger import UserObligationLedgerService
from app.v2.research_tasks import ResearchTaskLifecycleError, ResearchTaskRegistry
from app.v2.semantic_handles import SemanticHandleRegistry


class HypothesisLedgerError(RuntimeError):
    """Day8 structural epistemic-boundary violation."""


class HypothesisLedger:
    """Run-scoped owner for one accepted ROOT_CAUSE obligation.

    The ledger validates admissibility only. Whether Evidence semantically supports or
    contradicts a hypothesis remains a cognition proposal; this layer only proves that
    the referenced Evidence/semantic/task identities are governed and related to this
    investigation.
    """

    def __init__(
        self,
        *,
        parent_obligation_id: str,
        accepted_contract_id: str,
        lineage_id: str,
        run_id: str,
        obligation_ledger: UserObligationLedger,
        evidence_store,
        current_evidence_refs: tuple[str, ...],
        semantic_handles: SemanticHandleRegistry,
        research_tasks: ResearchTaskRegistry,
        tenant_binding: str,
        context_version: str,
    ) -> None:
        self._obligations = UserObligationLedgerService()
        self._obligation_ledger = obligation_ledger
        self._evidence = evidence_store
        self._current_evidence_refs = frozenset(current_evidence_refs)
        self._handles = semantic_handles
        self._tasks = research_tasks
        self._tenant_binding = tenant_binding
        self._context_version = context_version
        self._state = HypothesisLedgerState(
            parent_obligation_id=parent_obligation_id,
            accepted_contract_id=accepted_contract_id,
            lineage_id=lineage_id,
            run_id=run_id,
        )
        self._validate_root_authority()

    @property
    def state(self) -> HypothesisLedgerState:
        return self._state

    @property
    def open_hypotheses(self) -> tuple[HypothesisEntry, ...]:
        return tuple(
            item for item in self._state.entries
            if item.status == HypothesisStatus.OPEN
        )

    @property
    def accounted_hypotheses(self) -> tuple[HypothesisEntry, ...]:
        return tuple(
            item for item in self._state.entries
            if item.status != HypothesisStatus.OPEN
        )

    def get(self, hypothesis_id: str) -> HypothesisEntry:
        try:
            return next(
                item for item in self._state.entries
                if item.hypothesis_id == hypothesis_id
            )
        except StopIteration as exc:
            raise HypothesisLedgerError(
                f"unknown hypothesis: {hypothesis_id}"
            ) from exc

    def register(
        self,
        *,
        statement: str,
        semantic_handle_refs: tuple[str, ...],
        trigger_evidence_refs: tuple[str, ...],
        limitations: tuple[str, ...] = (),
    ) -> HypothesisEntry:
        clean_statement = statement.strip()
        if not clean_statement:
            raise HypothesisLedgerError("hypothesis statement cannot be empty")
        if not semantic_handle_refs:
            raise HypothesisLedgerError(
                "hypothesis requires governed semantic handles"
            )
        if not trigger_evidence_refs:
            raise HypothesisLedgerError(
                "hypothesis requires verified trigger Evidence"
            )

        self._validate_semantic_handles(semantic_handle_refs)
        for evidence_ref in trigger_evidence_refs:
            self._validate_evidence(evidence_ref)

        hypothesis_id = self._hypothesis_id(
            statement=clean_statement,
            semantic_handle_refs=semantic_handle_refs,
            trigger_evidence_refs=trigger_evidence_refs,
        )
        existing = next(
            (
                item for item in self._state.entries
                if item.hypothesis_id == hypothesis_id
            ),
            None,
        )
        if existing is not None:
            return existing

        entry = HypothesisEntry(
            hypothesis_id=hypothesis_id,
            parent_obligation_id=self._state.parent_obligation_id,
            statement=clean_statement,
            semantic_handle_refs=tuple(dict.fromkeys(semantic_handle_refs)),
            trigger_evidence_refs=tuple(dict.fromkeys(trigger_evidence_refs)),
            limitations=tuple(dict.fromkeys(x.strip() for x in limitations if x.strip())),
            provenance=HypothesisProvenance(
                accepted_contract_id=self._state.accepted_contract_id,
                lineage_id=self._state.lineage_id,
                run_id=self._state.run_id,
            ),
        )
        self._state = self._state.model_copy(
            update={"entries": (*self._state.entries, entry)}
        )
        return entry

    def attach_evidence(
        self,
        hypothesis_id: str,
        *,
        evidence_ref: str,
        relation: HypothesisEvidenceRelation,
    ) -> HypothesisEntry:
        entry = self.get(hypothesis_id)
        self._validate_evidence(evidence_ref)

        same_ref = [
            link for link in entry.evidence_links
            if link.evidence_ref == evidence_ref
        ]
        if same_ref:
            if same_ref[0].relation == relation:
                return entry
            raise HypothesisLedgerError(
                "same Evidence cannot SUPPORT and CONTRADICT one hypothesis"
            )

        updated = entry.model_copy(
            update={
                "evidence_links": (
                    *entry.evidence_links,
                    HypothesisEvidenceLink(
                        evidence_ref=evidence_ref,
                        relation=relation,
                    ),
                )
            }
        )
        self._replace(updated)
        return updated

    def link_next_test(
        self,
        hypothesis_id: str,
        *,
        task_ref: str,
    ) -> HypothesisEntry:
        entry = self.get(hypothesis_id)
        try:
            task = self._tasks.get(task_ref)
        except ResearchTaskLifecycleError as exc:
            raise HypothesisLedgerError(
                f"unknown/non-governed next-test ResearchTask: {task_ref}"
            ) from exc

        if task.origin != "AGENT_DERIVED":
            raise HypothesisLedgerError(
                "root-cause next test must be an AGENT_DERIVED ResearchTask"
            )
        if task.parent_obligation_id != self._state.parent_obligation_id:
            raise HypothesisLedgerError(
                "next-test ResearchTask belongs to another obligation"
            )

        admissible_triggers = {
            *entry.trigger_evidence_refs,
            *(link.evidence_ref for link in entry.evidence_links),
        }
        if task.trigger_evidence_ref not in admissible_triggers:
            raise HypothesisLedgerError(
                "next-test ResearchTask trigger is unrelated to hypothesis Evidence"
            )

        if task_ref in entry.next_test_task_refs:
            return entry
        updated = entry.model_copy(
            update={"next_test_task_refs": (*entry.next_test_task_refs, task_ref)}
        )
        self._replace(updated)
        return updated

    def transition(
        self,
        hypothesis_id: str,
        *,
        status: HypothesisStatus,
        limitation: str | None = None,
    ) -> HypothesisEntry:
        entry = self.get(hypothesis_id)
        if status == HypothesisStatus.OPEN:
            if entry.status == HypothesisStatus.OPEN:
                return entry
            raise HypothesisLedgerError("accounted hypothesis cannot reopen silently")

        if status == HypothesisStatus.SUPPORTED and not any(
            link.relation == HypothesisEvidenceRelation.SUPPORTS
            for link in entry.evidence_links
        ):
            raise HypothesisLedgerError(
                "SUPPORTED requires at least one valid SUPPORTS Evidence link"
            )

        if status == HypothesisStatus.REFUTED and not any(
            link.relation == HypothesisEvidenceRelation.CONTRADICTS
            for link in entry.evidence_links
        ):
            raise HypothesisLedgerError(
                "REFUTED requires at least one valid CONTRADICTS Evidence link"
            )

        limitations = list(entry.limitations)
        if limitation is not None and limitation.strip():
            limitations.append(limitation.strip())
        limitations = list(dict.fromkeys(limitations))

        if status == HypothesisStatus.INCONCLUSIVE:
            if not limitations:
                raise HypothesisLedgerError(
                    "INCONCLUSIVE requires an explicit limitation"
                )
            observed_or_attempted = bool(
                entry.trigger_evidence_refs
                or entry.evidence_links
                or entry.next_test_task_refs
            )
            if not observed_or_attempted:
                raise HypothesisLedgerError(
                    "INCONCLUSIVE requires an attempted/observed evidence state"
                )

        updated = entry.model_copy(
            update={
                "status": status,
                "limitations": tuple(limitations),
            }
        )
        self._replace(updated)
        return updated

    def _validate_root_authority(self) -> None:
        if self._obligation_ledger.lineage_id != self._state.lineage_id:
            raise HypothesisLedgerError(
                "hypothesis ledger lineage does not match obligation ledger"
            )
        try:
            parent = self._obligations.get(
                self._obligation_ledger,
                self._state.parent_obligation_id,
            )
        except Exception as exc:
            raise HypothesisLedgerError(
                "unknown ROOT_CAUSE parent obligation"
            ) from exc

        if parent.capability_key != ManagerCapabilityKey.ROOT_CAUSE:
            raise HypothesisLedgerError(
                "hypothesis ledger requires a ROOT_CAUSE parent obligation"
            )
        if parent.origin != ObligationOrigin.USER_MUST:
            raise HypothesisLedgerError(
                "Day8 root authority must be an accepted USER_MUST obligation"
            )
        if parent.polarity != ObligationPolarity.REQUIRED:
            raise HypothesisLedgerError(
                "excluded ROOT_CAUSE obligation cannot own hypotheses"
            )
        if parent.status == ObligationStatus.SUPERSEDED:
            raise HypothesisLedgerError(
                "superseded ROOT_CAUSE obligation cannot own hypotheses"
            )

    def _validate_semantic_handles(self, refs: tuple[str, ...]) -> None:
        for handle_id in refs:
            try:
                handle = self._handles.validate(
                    handle_id,
                    tenant_binding=self._tenant_binding,
                    context_version=self._context_version,
                )
            except (KeyError, ValueError) as exc:
                raise HypothesisLedgerError(
                    f"invalid/non-governed semantic handle: {handle_id}"
                ) from exc
            if (
                handle.parent_obligation_id is not None
                and handle.parent_obligation_id != self._state.parent_obligation_id
            ):
                raise HypothesisLedgerError(
                    "semantic handle belongs to another obligation"
                )

    def _validate_evidence(self, evidence_ref: str):
        if evidence_ref not in self._current_evidence_refs:
            raise HypothesisLedgerError(
                "Evidence is not attached to the current governed run"
            )
        try:
            evidence = self._evidence.get(evidence_ref)
        except Exception as exc:
            raise HypothesisLedgerError(
                f"unknown Evidence: {evidence_ref}"
            ) from exc

        if not evidence.verified:
            raise HypothesisLedgerError("hypothesis Evidence must be VERIFIED")
        if self._state.parent_obligation_id not in evidence.obligation_ids:
            raise HypothesisLedgerError(
                "Evidence belongs to an unrelated obligation"
            )
        if not evidence.query_contract_refs:
            raise HypothesisLedgerError(
                "hypothesis Evidence lacks QueryContract provenance"
            )

        try:
            task = self._tasks.get(evidence.task_id)
        except ResearchTaskLifecycleError as exc:
            raise HypothesisLedgerError(
                "Evidence task is not registered in the current ResearchTask registry"
            ) from exc

        if (
            task.origin == "AGENT_DERIVED"
            and task.parent_obligation_id != self._state.parent_obligation_id
        ):
            raise HypothesisLedgerError(
                "derived Evidence task belongs to another obligation"
            )

        if evidence.source_kind == "DERIVED_ANALYTICAL":
            if not evidence.parent_evidence_refs:
                raise HypothesisLedgerError(
                    "derived Evidence lacks parent Evidence lineage"
                )
            for parent_ref in evidence.parent_evidence_refs:
                if parent_ref not in self._current_evidence_refs:
                    raise HypothesisLedgerError(
                        "derived Evidence parent is outside current governed run"
                    )
                try:
                    parent = self._evidence.get(parent_ref)
                except Exception as exc:
                    raise HypothesisLedgerError(
                        "derived Evidence parent cannot be resolved"
                    ) from exc
                if not parent.verified:
                    raise HypothesisLedgerError(
                        "derived Evidence parent is not VERIFIED"
                    )
            if set(evidence.parent_query_contract_refs) - set(
                evidence.query_contract_refs
            ):
                raise HypothesisLedgerError(
                    "derived Evidence lost parent QueryContract lineage"
                )
        return evidence

    def _replace(self, entry: HypothesisEntry) -> None:
        items = tuple(
            entry if item.hypothesis_id == entry.hypothesis_id else item
            for item in self._state.entries
        )
        self._state = self._state.model_copy(update={"entries": items})

    def _hypothesis_id(
        self,
        *,
        statement: str,
        semantic_handle_refs: tuple[str, ...],
        trigger_evidence_refs: tuple[str, ...],
    ) -> str:
        payload = {
            "parent_obligation_id": self._state.parent_obligation_id,
            "statement": statement,
            "semantic_handle_refs": list(dict.fromkeys(semantic_handle_refs)),
            "trigger_evidence_refs": list(dict.fromkeys(trigger_evidence_refs)),
            "provenance": {
                "accepted_contract_id": self._state.accepted_contract_id,
                "lineage_id": self._state.lineage_id,
                "run_id": self._state.run_id,
            },
        }
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return "hyp_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
