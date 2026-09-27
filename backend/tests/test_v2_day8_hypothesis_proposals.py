"""Provider-free D8-B attacks for bounded hypothesis cognition proposals."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v2.epistemics import CurrentRunEvidenceView, HypothesisLedger
from app.v2.hypothesis_proposals import (
    HypothesisProposalBoundary,
    HypothesisProposalError,
)
from app.v2.manager_executor import EvidenceStore
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ManagerRunSnapshot,
    ManagerState,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    UserObligationLedger,
)
from app.v2.models import (
    EvidenceArtifact,
    HypothesisEvidenceRelation,
    HypothesisEvidenceRelationProposal,
    HypothesisProposal,
    ResearchTask,
)
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.semantic_handles import SemanticHandleRegistry


ROOT = "U_RC"
TENANT = "tenant-binding"
CTX = "ctx-v1"


def _evidence(
    artifact_id: str,
    *,
    verified: bool = True,
    kind: str = "standard_analytics",
    obligation_ids=(ROOT,),
) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        task_id="seed:U_RC",
        obligation_ids=tuple(obligation_ids),
        query_contract_refs=("QC1",),
        evidence_kind=kind,
        verified=verified,
        payload={
            "query_count": 1,
            "executions": (
                {
                    "execution_id": f"exec:{artifact_id}",
                    "role": "primary",
                    "columns": ("metric",),
                    "row_count": 1,
                    "rows": ({"metric": 10.0},),
                },
            ),
        },
    )


def _fixture(
    *,
    evidence: tuple[EvidenceArtifact, ...] | None = None,
    current_refs: tuple[str, ...] | None = None,
    inspected_refs: tuple[str, ...] = ("E1",),
):
    evidence = evidence or (_evidence("E1"), _evidence("E2"))
    store = EvidenceStore()
    for item in evidence:
        store.put(item)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id="resolver:metric",
        target_kind="metric",
        canonical_target={"metric": "oee"},
        parent_obligation_id=ROOT,
    )

    tasks = ResearchTaskRegistry()
    tasks.register(
        ResearchTask(
            task_id="seed:U_RC",
            question_id=ROOT,
            task_kind="BREAKDOWN",
            input_refs=(metric.handle_id,),
            origin="USER_SEED",
        )
    )

    runtime = SimpleNamespace(
        snapshot=ManagerRunSnapshot(
            run_id="run-1",
            state=ManagerState.INVESTIGATING,
            evidence_refs=(
                tuple(item.artifact_id for item in evidence)
                if current_refs is None
                else current_refs
            ),
            inspected_evidence_refs=inspected_refs,
        )
    )
    obligations = UserObligationLedger(
        lineage_id="lin-1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id=ROOT,
                capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.IN_PROGRESS,
                source_refs=("src:why",),
                introduced_in_version=1,
            ),
        ),
    )
    ledger = HypothesisLedger(
        parent_obligation_id=ROOT,
        accepted_contract_id="act-1",
        lineage_id="lin-1",
        run_id="run-1",
        obligation_ledger=obligations,
        evidence_store=store,
        evidence_view=CurrentRunEvidenceView(runtime),
        semantic_handles=handles,
        research_tasks=tasks,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    return HypothesisProposalBoundary(ledger=ledger), ledger, metric.handle_id


def _proposal(metric: str, *, trigger: str = "E1") -> HypothesisProposal:
    return HypothesisProposal(
        statement="Gece vardiyası hız kaybının aday açıklaması olabilir.",
        semantic_handle_refs=(metric,),
        trigger_evidence_refs=(trigger,),
        limitations=("Gözlemsel kanıt nedenselliği tek başına kurmaz.",),
    )


def test_valid_inspected_trigger_registers_hypothesis():
    boundary, ledger, metric = _fixture()
    hypothesis = boundary.register(_proposal(metric))

    assert hypothesis.hypothesis_id.startswith("hyp_")
    assert hypothesis.trigger_evidence_refs == ("E1",)
    assert hypothesis.evidence_links == ()
    assert ledger.get(hypothesis.hypothesis_id) == hypothesis


def test_uninspected_trigger_is_rejected():
    boundary, _, metric = _fixture(inspected_refs=())
    with pytest.raises(HypothesisProposalError, match="INSPECTION_REQUIRED"):
        boundary.register(_proposal(metric))


def test_foreign_run_evidence_is_rejected_even_if_marked_inspected():
    boundary, _, metric = _fixture(
        evidence=(_evidence("E1"), _evidence("E_FOREIGN")),
        current_refs=("E1",),
        inspected_refs=("E1", "E_FOREIGN"),
    )
    with pytest.raises(HypothesisProposalError, match="current governed run"):
        boundary.register(_proposal(metric, trigger="E_FOREIGN"))


def test_unverified_trigger_is_rejected():
    boundary, _, metric = _fixture(
        evidence=(_evidence("E_BAD", verified=False),),
        inspected_refs=("E_BAD",),
    )
    with pytest.raises(HypothesisProposalError, match="VERIFIED"):
        boundary.register(_proposal(metric, trigger="E_BAD"))


def test_model_minted_semantic_handle_is_rejected():
    boundary, _, _ = _fixture()
    with pytest.raises(HypothesisProposalError, match="semantic handle"):
        boundary.register(
            HypothesisProposal(
                statement="candidate",
                semantic_handle_refs=("sem_model_fake",),
                trigger_evidence_refs=("E1",),
                limitations=("limit",),
            )
        )


def test_duplicate_identical_proposal_is_idempotent_and_server_mints_id():
    boundary, ledger, metric = _fixture()
    first = boundary.register(_proposal(metric))
    second = boundary.register(_proposal(metric))

    assert first == second
    assert len(ledger.state.entries) == 1
    assert first.hypothesis_id.startswith("hyp_")


def test_explicit_supports_relation_with_inspected_evidence_is_admitted():
    boundary, _, metric = _fixture(inspected_refs=("E1", "E2"))
    hypothesis = boundary.register(_proposal(metric))

    updated = boundary.attach_relation(
        HypothesisEvidenceRelationProposal(
            hypothesis_ref=hypothesis.hypothesis_id,
            evidence_ref="E2",
            relation=HypothesisEvidenceRelation.SUPPORTS,
        )
    )
    assert [(x.evidence_ref, x.relation.value) for x in updated.evidence_links] == [
        ("E2", "SUPPORTS")
    ]


def test_trigger_evidence_does_not_auto_convert_to_support():
    boundary, _, metric = _fixture()
    hypothesis = boundary.register(_proposal(metric))

    assert hypothesis.trigger_evidence_refs == ("E1",)
    assert hypothesis.evidence_links == ()


def test_supports_then_contradicts_same_evidence_is_rejected():
    boundary, _, metric = _fixture(inspected_refs=("E1", "E2"))
    hypothesis = boundary.register(_proposal(metric))
    boundary.attach_relation(
        HypothesisEvidenceRelationProposal(
            hypothesis_ref=hypothesis.hypothesis_id,
            evidence_ref="E2",
            relation=HypothesisEvidenceRelation.SUPPORTS,
        )
    )

    with pytest.raises(HypothesisProposalError, match="SUPPORT and CONTRADICT"):
        boundary.attach_relation(
            HypothesisEvidenceRelationProposal(
                hypothesis_ref=hypothesis.hypothesis_id,
                evidence_ref="E2",
                relation=HypothesisEvidenceRelation.CONTRADICTS,
            )
        )


def test_priority_only_evidence_cannot_become_causal_support():
    priority = _evidence("E_PRIORITY", kind="interestingness_score")
    boundary, _, metric = _fixture(
        evidence=(_evidence("E1"), priority),
        inspected_refs=("E1", "E_PRIORITY"),
    )
    hypothesis = boundary.register(_proposal(metric))

    with pytest.raises(HypothesisProposalError, match="PRIORITIZATION_NOT_TRUTH"):
        boundary.attach_relation(
            HypothesisEvidenceRelationProposal(
                hypothesis_ref=hypothesis.hypothesis_id,
                evidence_ref="E_PRIORITY",
                relation=HypothesisEvidenceRelation.SUPPORTS,
            )
        )
