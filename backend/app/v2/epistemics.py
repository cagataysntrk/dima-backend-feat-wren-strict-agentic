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
    EpistemicGateCode,
    EpistemicLabel,
    EpistemicLabelDecision,
    EvidenceLinkedFinding,
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


class CurrentRunEvidenceView:
    """Read-only live view over Day7 ManagerRuntime Evidence membership.

    Membership is owned by the existing ManagerRuntime snapshot. This object exposes no
    mutator and therefore cannot add arbitrary Evidence IDs or create a second run
    registry.
    """

    def __init__(self, runtime) -> None:
        if not hasattr(runtime, "snapshot"):
            raise TypeError("CurrentRunEvidenceView requires a ManagerRuntime-like owner")
        self._runtime = runtime

    @property
    def run_id(self) -> str:
        return self._runtime.snapshot.run_id

    @property
    def current_refs(self) -> tuple[str, ...]:
        return tuple(self._runtime.snapshot.evidence_refs)

    @property
    def inspected_refs(self) -> tuple[str, ...]:
        return tuple(self._runtime.snapshot.inspected_evidence_refs)

    def contains_current(self, evidence_ref: str) -> bool:
        return evidence_ref in self.current_refs

    def contains_inspected(self, evidence_ref: str) -> bool:
        return evidence_ref in self.inspected_refs


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
        evidence_view: CurrentRunEvidenceView,
        semantic_handles: SemanticHandleRegistry,
        research_tasks: ResearchTaskRegistry,
        tenant_binding: str,
        context_version: str,
    ) -> None:
        self._obligations = UserObligationLedgerService()
        self._obligation_ledger = obligation_ledger
        self._evidence = evidence_store
        self._evidence_view = evidence_view
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
        if self._evidence_view.run_id != run_id:
            raise HypothesisLedgerError(
                "current Evidence view belongs to another Manager run"
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

    def validated_evidence(self, evidence_ref: str):
        """Return current-run governed Evidence after structural validation."""
        return self._validate_evidence(evidence_ref)

    def register(
        self,
        *,
        statement: str,
        semantic_handle_refs: tuple[str, ...],
        trigger_evidence_refs: tuple[str, ...],
        limitations: tuple[str, ...] = (),
    ) -> HypothesisEntry:
        self._validate_root_authority()
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
        self._validate_root_authority()
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
        self._validate_root_authority()
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
        self._validate_root_authority()
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
        active_statuses = {
            ObligationStatus.ACCEPTED,
            ObligationStatus.READY,
            ObligationStatus.IN_PROGRESS,
        }
        if parent.status not in active_statuses:
            raise HypothesisLedgerError(
                "ROOT_CAUSE obligation must be active "
                "(ACCEPTED, READY or IN_PROGRESS) to own mutable hypothesis state"
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
        if not self._evidence_view.contains_current(evidence_ref):
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
        if not any(
            self._obligation_belongs_to_root(obligation_id)
            for obligation_id in evidence.obligation_ids
        ):
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

        if task.origin == "AGENT_DERIVED":
            parent_id = task.parent_obligation_id
            if (
                parent_id is None
                or not self._obligation_belongs_to_root(parent_id)
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
                if not self._evidence_view.contains_current(parent_ref):
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

    def _obligation_belongs_to_root(self, obligation_id: str) -> bool:
        current_id = obligation_id
        seen: set[str] = set()
        while current_id not in seen:
            if current_id == self._state.parent_obligation_id:
                return True
            seen.add(current_id)
            try:
                item = self._obligations.get(self._obligation_ledger, current_id)
            except Exception:
                return False
            if item.parent_obligation_id is None:
                return False
            current_id = item.parent_obligation_id
        return False

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


class EpistemicFindingError(RuntimeError):
    """A requested finding label exceeds the structurally admissible Evidence class."""


class EpistemicLabelGate:
    """Validate claim-class ceilings without pretending to infer causal truth."""

    _PRIORITY_MARKERS = (
        "interestingness",
        "outlier",
        "anomaly",
        "priority",
        "salience",
    )

    @classmethod
    def _is_priority_only(cls, evidence) -> bool:
        kind = str(evidence.evidence_kind or "").lower()
        payload = evidence.payload or {}
        role = str(payload.get("epistemic_role") or "").upper()
        return (
            role == "PRIORITIZATION_ONLY"
            or any(marker in kind for marker in cls._PRIORITY_MARKERS)
        )

    @staticmethod
    def _has_comparison_contract(evidence) -> bool:
        if (
            evidence.source_kind == "DERIVED_ANALYTICAL"
            and evidence.transformation == "PEER_COMPARE"
        ):
            return True
        if "comparison" in str(evidence.evidence_kind or "").lower():
            return True
        roles = {
            str(item.get("role") or "")
            for item in tuple((evidence.payload or {}).get("executions") or ())
        }
        return "comparison_reference" in roles

    def decide(
        self,
        *,
        requested_label: EpistemicLabel,
        evidence: tuple,
        hypothesis: HypothesisEntry | None = None,
        root_cause_authority: bool = False,
    ) -> EpistemicLabelDecision:
        if requested_label == EpistemicLabel.CONFIRMED_CAUSE:
            return EpistemicLabelDecision(
                allowed=False,
                requested_label=requested_label,
                code=EpistemicGateCode.CAUSAL_NOT_IDENTIFIED,
                reason=(
                    "current Day8 has no proven mechanistic/interventional causal "
                    "identification contract"
                ),
            )

        if not evidence:
            return EpistemicLabelDecision(
                allowed=False,
                requested_label=requested_label,
                code=EpistemicGateCode.EVIDENCE_REQUIRED,
                reason="epistemic finding requires governed Evidence",
            )

        if requested_label == EpistemicLabel.OBSERVATION:
            return EpistemicLabelDecision(
                allowed=True,
                requested_label=requested_label,
                code=EpistemicGateCode.ALLOW,
                reason="verified governed Evidence permits an observational claim",
            )

        if requested_label == EpistemicLabel.COMPARISON:
            if any(self._has_comparison_contract(item) for item in evidence):
                return EpistemicLabelDecision(
                    allowed=True,
                    requested_label=requested_label,
                    code=EpistemicGateCode.ALLOW,
                    reason="governed comparison/peer Evidence with baseline is present",
                )
            return EpistemicLabelDecision(
                allowed=False,
                requested_label=requested_label,
                code=EpistemicGateCode.EVIDENCE_CLASS_MISMATCH,
                reason="COMPARISON requires governed comparison or peer Evidence",
            )

        if requested_label == EpistemicLabel.ASSOCIATION:
            if any(
                str(item.evidence_kind) == "relationship_analytics"
                for item in evidence
            ):
                return EpistemicLabelDecision(
                    allowed=True,
                    requested_label=requested_label,
                    code=EpistemicGateCode.ALLOW,
                    reason="governed relationship Evidence permits ASSOCIATION only",
                )
            return EpistemicLabelDecision(
                allowed=False,
                requested_label=requested_label,
                code=EpistemicGateCode.EVIDENCE_CLASS_MISMATCH,
                reason="ASSOCIATION requires governed relationship Evidence",
            )

        if requested_label == EpistemicLabel.CONTRIBUTION:
            if any(
                item.source_kind == "DERIVED_ANALYTICAL"
                and item.transformation == "CONTRIBUTION"
                for item in evidence
            ):
                return EpistemicLabelDecision(
                    allowed=True,
                    requested_label=requested_label,
                    code=EpistemicGateCode.ALLOW,
                    reason="governed contribution decomposition Evidence is present",
                )
            return EpistemicLabelDecision(
                allowed=False,
                requested_label=requested_label,
                code=EpistemicGateCode.EVIDENCE_CLASS_MISMATCH,
                reason="CONTRIBUTION requires governed contribution Evidence",
            )

        if requested_label == EpistemicLabel.CANDIDATE_CAUSE:
            if not root_cause_authority:
                return EpistemicLabelDecision(
                    allowed=False,
                    requested_label=requested_label,
                    code=EpistemicGateCode.ROOT_CAUSE_REQUIRED,
                    reason="CANDIDATE_CAUSE requires accepted ROOT_CAUSE authority",
                )
            if hypothesis is None:
                return EpistemicLabelDecision(
                    allowed=False,
                    requested_label=requested_label,
                    code=EpistemicGateCode.HYPOTHESIS_REQUIRED,
                    reason="CANDIDATE_CAUSE requires a typed hypothesis",
                )
            support_refs = {
                link.evidence_ref
                for link in hypothesis.evidence_links
                if link.relation == HypothesisEvidenceRelation.SUPPORTS
            }
            supplied = {item.artifact_id: item for item in evidence}
            usable_support = [
                supplied[ref]
                for ref in support_refs
                if ref in supplied and not self._is_priority_only(supplied[ref])
            ]
            if not usable_support:
                if support_refs and any(
                    ref in supplied and self._is_priority_only(supplied[ref])
                    for ref in support_refs
                ):
                    return EpistemicLabelDecision(
                        allowed=False,
                        requested_label=requested_label,
                        code=EpistemicGateCode.PRIORITIZATION_NOT_TRUTH,
                        reason=(
                            "interestingness/outlier/anomaly/priority signals may "
                            "schedule tests but cannot establish candidate-cause support"
                        ),
                    )
                return EpistemicLabelDecision(
                    allowed=False,
                    requested_label=requested_label,
                    code=EpistemicGateCode.HYPOTHESIS_SUPPORT_REQUIRED,
                    reason="CANDIDATE_CAUSE requires valid supporting Evidence",
                )
            if not hypothesis.limitations:
                return EpistemicLabelDecision(
                    allowed=False,
                    requested_label=requested_label,
                    code=EpistemicGateCode.LIMITATION_REQUIRED,
                    reason="CANDIDATE_CAUSE requires explicit limitations",
                )
            if not hypothesis.semantic_handle_refs:
                return EpistemicLabelDecision(
                    allowed=False,
                    requested_label=requested_label,
                    code=EpistemicGateCode.HYPOTHESIS_REQUIRED,
                    reason="candidate hypothesis lacks governed semantic authority",
                )
            return EpistemicLabelDecision(
                allowed=True,
                requested_label=requested_label,
                code=EpistemicGateCode.ALLOW,
                reason=(
                    "supported typed hypothesis with governed Evidence and explicit "
                    "limitations permits CANDIDATE_CAUSE, not confirmation"
                ),
            )

        return EpistemicLabelDecision(
            allowed=False,
            requested_label=requested_label,
            code=EpistemicGateCode.EVIDENCE_CLASS_MISMATCH,
            reason="unsupported epistemic label contract",
        )


class EvidenceLinkedFindingBuilder:
    """Build official Day8 findings only after Evidence + label admissibility proof."""

    def __init__(
        self,
        *,
        ledger: HypothesisLedger,
        gate: EpistemicLabelGate | None = None,
    ) -> None:
        self._ledger = ledger
        self._gate = gate or EpistemicLabelGate()

    def build(
        self,
        *,
        statement: str,
        epistemic_label: EpistemicLabel,
        evidence_refs: tuple[str, ...],
        hypothesis_ref: str | None = None,
        limitations: tuple[str, ...] = (),
    ) -> EvidenceLinkedFinding:
        clean_statement = statement.strip()
        if not clean_statement:
            raise EpistemicFindingError("finding statement cannot be empty")
        if not evidence_refs:
            raise EpistemicFindingError(
                f"{EpistemicGateCode.EVIDENCE_REQUIRED.value}: finding requires Evidence"
            )

        evidence = tuple(
            self._ledger.validated_evidence(ref)
            for ref in tuple(dict.fromkeys(evidence_refs))
        )
        hypothesis = (
            None
            if hypothesis_ref is None
            else self._ledger.get(hypothesis_ref)
        )
        decision = self._gate.decide(
            requested_label=epistemic_label,
            evidence=evidence,
            hypothesis=hypothesis,
            root_cause_authority=True,
        )
        if not decision.allowed:
            raise EpistemicFindingError(
                f"{decision.code.value}: {decision.reason}"
            )

        finding_limitations = list(limitations)
        if hypothesis is not None:
            finding_limitations.extend(hypothesis.limitations)
        finding_limitations = list(
            dict.fromkeys(x.strip() for x in finding_limitations if x.strip())
        )

        payload = {
            "parent_obligation_id": self._ledger.state.parent_obligation_id,
            "statement": clean_statement,
            "epistemic_label": epistemic_label.value,
            "evidence_refs": [item.artifact_id for item in evidence],
            "hypothesis_ref": hypothesis_ref,
            "provenance": {
                "accepted_contract_id": self._ledger.state.accepted_contract_id,
                "lineage_id": self._ledger.state.lineage_id,
                "run_id": self._ledger.state.run_id,
            },
        }
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return EvidenceLinkedFinding(
            finding_id="find_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24],
            parent_obligation_id=self._ledger.state.parent_obligation_id,
            statement=clean_statement,
            epistemic_label=epistemic_label,
            evidence_refs=tuple(item.artifact_id for item in evidence),
            hypothesis_ref=hypothesis_ref,
            limitations=tuple(finding_limitations),
            provenance=HypothesisProvenance(
                accepted_contract_id=self._ledger.state.accepted_contract_id,
                lineage_id=self._ledger.state.lineage_id,
                run_id=self._ledger.state.run_id,
            ),
        )
