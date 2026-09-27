"""Day8-B provider-free cognition proposal admission boundary.

The model may propose text and select existing governed IDs. This boundary proves that
those IDs are current, verified and inspected before delegating structural state changes
to HypothesisLedger. It executes no query and owns no semantic/causal truth.
"""

from __future__ import annotations

from app.v2.epistemics import (
    EpistemicLabelGate,
    HypothesisLedger,
    HypothesisLedgerError,
)
from app.v2.models import (
    HypothesisEntry,
    HypothesisEvidenceRelation,
    HypothesisEvidenceRelationProposal,
    HypothesisProposal,
)


class HypothesisProposalError(RuntimeError):
    """A D8-B cognition proposal is structurally inadmissible."""


class HypothesisProposalBoundary:
    """Admit bounded hypothesis/relation proposals against Day7 run truth."""

    def __init__(self, *, ledger: HypothesisLedger) -> None:
        self._ledger = ledger

    def register(self, proposal: HypothesisProposal) -> HypothesisEntry:
        for evidence_ref in proposal.trigger_evidence_refs:
            self._require_inspected_evidence(evidence_ref)

        try:
            return self._ledger.register(
                statement=proposal.statement,
                semantic_handle_refs=proposal.semantic_handle_refs,
                trigger_evidence_refs=proposal.trigger_evidence_refs,
                limitations=proposal.limitations,
            )
        except HypothesisLedgerError as exc:
            raise HypothesisProposalError(str(exc)) from exc

    def attach_relation(
        self,
        proposal: HypothesisEvidenceRelationProposal,
    ) -> HypothesisEntry:
        evidence = self._require_inspected_evidence(proposal.evidence_ref)

        if (
            proposal.relation == HypothesisEvidenceRelation.SUPPORTS
            and EpistemicLabelGate.is_priority_only(evidence)
        ):
            raise HypothesisProposalError(
                "PRIORITIZATION_NOT_TRUTH: priority-only Evidence cannot become "
                "causal SUPPORTS Evidence"
            )

        try:
            # get() proves the model echoed an existing server-owned hypothesis ID.
            self._ledger.get(proposal.hypothesis_ref)
            return self._ledger.attach_evidence(
                proposal.hypothesis_ref,
                evidence_ref=proposal.evidence_ref,
                relation=proposal.relation,
            )
        except HypothesisLedgerError as exc:
            raise HypothesisProposalError(str(exc)) from exc

    def _require_inspected_evidence(self, evidence_ref: str):
        try:
            evidence = self._ledger.validated_evidence(evidence_ref)
        except HypothesisLedgerError as exc:
            raise HypothesisProposalError(str(exc)) from exc

        if not self._ledger.evidence_view.contains_inspected(evidence_ref):
            raise HypothesisProposalError(
                "INSPECTION_REQUIRED: cognition proposal may reference only "
                "Evidence inspected in the current governed run"
            )
        return evidence
