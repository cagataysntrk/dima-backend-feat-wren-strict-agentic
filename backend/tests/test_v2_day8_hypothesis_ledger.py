"""Provider-free Day8 A1 attacks for the HypothesisLedger."""

from __future__ import annotations

import pytest
from types import SimpleNamespace

from app.v2.epistemics import CurrentRunEvidenceView, HypothesisLedger, HypothesisLedgerError
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
    HypothesisStatus,
    ResearchTask,
)
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.semantic_handles import SemanticHandleRegistry


ROOT = "U_RC"
TENANT = "tenant-binding"
CTX = "ctx-v1"


def _obligation_ledger(
    capability: ManagerCapabilityKey = ManagerCapabilityKey.ROOT_CAUSE,
    status: ObligationStatus = ObligationStatus.ACCEPTED,
) -> UserObligationLedger:
    return UserObligationLedger(
        lineage_id="lin-1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id=ROOT,
                capability_key=capability,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=status,
                source_refs=("src:why",),
                introduced_in_version=1,
            ),
        ),
    )


def _evidence(
    artifact_id: str,
    *,
    verified: bool = True,
    obligation_ids=(ROOT,),
    qrefs=("QC1",),
) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        task_id="seed:U_RC",
        obligation_ids=tuple(obligation_ids),
        query_contract_refs=tuple(qrefs),
        evidence_kind="standard_analytics",
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
    capability: ManagerCapabilityKey = ManagerCapabilityKey.ROOT_CAUSE,
    status: ObligationStatus = ObligationStatus.ACCEPTED,
    evidence: tuple[EvidenceArtifact, ...] | None = None,
    current_refs: tuple[str, ...] | None = None,
    inspected_refs: tuple[str, ...] = (),
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
    ledger = HypothesisLedger(
        parent_obligation_id=ROOT,
        accepted_contract_id="act-1",
        lineage_id="lin-1",
        run_id="run-1",
        obligation_ledger=_obligation_ledger(capability, status),
        evidence_store=store,
        evidence_view=CurrentRunEvidenceView(runtime),
        semantic_handles=handles,
        research_tasks=tasks,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    return ledger, metric.handle_id, store, tasks, runtime


def _register(ledger: HypothesisLedger, metric: str):
    return ledger.register(
        statement="Gece vardiyası hız kaybının aday açıklaması olabilir.",
        semantic_handle_refs=(metric,),
        trigger_evidence_refs=("E1",),
    )


def test_create_hypothesis_without_root_cause_parent_is_rejected():
    with pytest.raises(HypothesisLedgerError, match="ROOT_CAUSE"):
        _fixture(capability=ManagerCapabilityKey.PERFORMANCE)


def test_trigger_evidence_missing_is_rejected():
    ledger, metric, _, _, _ = _fixture()
    with pytest.raises(HypothesisLedgerError, match="current governed run"):
        ledger.register(
            statement="candidate",
            semantic_handle_refs=(metric,),
            trigger_evidence_refs=("E_MISSING",),
        )


def test_trigger_evidence_unverified_is_rejected():
    ledger, metric, _, _, _ = _fixture(
        evidence=(_evidence("E_BAD", verified=False),)
    )
    with pytest.raises(HypothesisLedgerError, match="VERIFIED"):
        ledger.register(
            statement="candidate",
            semantic_handle_refs=(metric,),
            trigger_evidence_refs=("E_BAD",),
        )


def test_unrelated_obligation_evidence_is_rejected():
    ledger, metric, _, _, _ = _fixture(
        evidence=(_evidence("E_OTHER", obligation_ids=("U_OTHER",)),)
    )
    with pytest.raises(HypothesisLedgerError, match="unrelated obligation"):
        ledger.register(
            statement="candidate",
            semantic_handle_refs=(metric,),
            trigger_evidence_refs=("E_OTHER",),
        )


def test_model_minted_fake_semantic_handle_is_rejected():
    ledger, _, _, _, _ = _fixture()
    with pytest.raises(HypothesisLedgerError, match="semantic handle"):
        ledger.register(
            statement="candidate",
            semantic_handle_refs=("sem_model_minted_fake",),
            trigger_evidence_refs=("E1",),
        )


def test_valid_supporting_and_contradicting_evidence_attach():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)

    hypothesis = ledger.attach_evidence(
        hypothesis.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    hypothesis = ledger.attach_evidence(
        hypothesis.hypothesis_id,
        evidence_ref="E2",
        relation=HypothesisEvidenceRelation.CONTRADICTS,
    )

    assert [(x.evidence_ref, x.relation.value) for x in hypothesis.evidence_links] == [
        ("E1", "SUPPORTS"),
        ("E2", "CONTRADICTS"),
    ]


def test_unknown_evidence_ref_is_rejected_on_attachment():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    with pytest.raises(HypothesisLedgerError, match="current governed run"):
        ledger.attach_evidence(
            hypothesis.hypothesis_id,
            evidence_ref="E_UNKNOWN",
            relation=HypothesisEvidenceRelation.SUPPORTS,
        )


def test_unverified_evidence_is_rejected_on_attachment():
    ledger, metric, _, _, _ = _fixture(
        evidence=(_evidence("E1"), _evidence("E_BAD", verified=False))
    )
    hypothesis = _register(ledger, metric)
    with pytest.raises(HypothesisLedgerError, match="VERIFIED"):
        ledger.attach_evidence(
            hypothesis.hypothesis_id,
            evidence_ref="E_BAD",
            relation=HypothesisEvidenceRelation.SUPPORTS,
        )


def test_same_evidence_conflicting_relation_is_rejected():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    ledger.attach_evidence(
        hypothesis.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )

    with pytest.raises(HypothesisLedgerError, match="SUPPORT and CONTRADICT"):
        ledger.attach_evidence(
            hypothesis.hypothesis_id,
            evidence_ref="E1",
            relation=HypothesisEvidenceRelation.CONTRADICTS,
        )


def test_duplicate_same_relation_is_idempotent():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    first = ledger.attach_evidence(
        hypothesis.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    second = ledger.attach_evidence(
        hypothesis.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )

    assert second == first
    assert len(second.evidence_links) == 1


def test_supported_without_support_evidence_is_rejected():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    with pytest.raises(HypothesisLedgerError, match="SUPPORTED requires"):
        ledger.transition(
            hypothesis.hypothesis_id,
            status=HypothesisStatus.SUPPORTED,
        )


def test_refuted_without_contradicting_evidence_is_rejected():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    with pytest.raises(HypothesisLedgerError, match="REFUTED requires"):
        ledger.transition(
            hypothesis.hypothesis_id,
            status=HypothesisStatus.REFUTED,
        )


def test_inconclusive_without_limitation_is_rejected():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    with pytest.raises(HypothesisLedgerError, match="explicit limitation"):
        ledger.transition(
            hypothesis.hypothesis_id,
            status=HypothesisStatus.INCONCLUSIVE,
        )


def test_status_transition_uses_structural_admission_not_vote_counting():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    hypothesis = ledger.attach_evidence(
        hypothesis.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    hypothesis = ledger.transition(
        hypothesis.hypothesis_id,
        status=HypothesisStatus.SUPPORTED,
    )

    assert hypothesis.status == HypothesisStatus.SUPPORTED


def test_model_minted_fake_next_test_task_ref_is_rejected():
    ledger, metric, _, _, _ = _fixture()
    hypothesis = _register(ledger, metric)
    with pytest.raises(HypothesisLedgerError, match="next-test ResearchTask"):
        ledger.link_next_test(
            hypothesis.hypothesis_id,
            task_ref="task_model_minted_fake",
        )


def test_registered_governed_next_test_can_be_linked():
    ledger, metric, _, tasks, _ = _fixture()
    hypothesis = _register(ledger, metric)
    tasks.register(
        ResearchTask(
            task_id="D1",
            question_id=ROOT,
            task_kind="COMPARE",
            input_refs=(metric,),
            origin="AGENT_DERIVED",
            parent_task_id="seed:U_RC",
            parent_obligation_id=ROOT,
            trigger_evidence_ref="E1",
            branch_depth=1,
        )
    )

    updated = ledger.link_next_test(hypothesis.hypothesis_id, task_ref="D1")
    assert updated.next_test_task_refs == ("D1",)


@pytest.mark.parametrize(
    "status",
    [
        ObligationStatus.PROPOSED,
        ObligationStatus.NEEDS_CLARIFICATION,
        ObligationStatus.BLOCKED_DATA_GAP,
        ObligationStatus.LIMITED,
        ObligationStatus.UNSUPPORTED,
        ObligationStatus.SUPERSEDED,
        ObligationStatus.VERIFIED,
    ],
)
def test_root_cause_inactive_or_terminal_authority_cannot_create_ledger(status):
    with pytest.raises(HypothesisLedgerError, match="must be active"):
        _fixture(status=status)


@pytest.mark.parametrize(
    "status",
    [
        ObligationStatus.ACCEPTED,
        ObligationStatus.READY,
        ObligationStatus.IN_PROGRESS,
    ],
)
def test_root_cause_active_authority_can_create_ledger(status):
    ledger, metric, _, _, _ = _fixture(status=status)
    hypothesis = _register(ledger, metric)
    assert hypothesis.status == HypothesisStatus.OPEN


def test_current_evidence_view_observes_new_same_run_evidence_without_rebuilding_ledger():
    ledger, metric, store, _, runtime = _fixture(
        evidence=(_evidence("E1"),),
        current_refs=("E1",),
    )
    hypothesis = _register(ledger, metric)

    store.put(_evidence("E_NEW"))
    runtime.snapshot = runtime.snapshot.model_copy(
        update={"evidence_refs": ("E1", "E_NEW")}
    )

    updated = ledger.attach_evidence(
        hypothesis.hypothesis_id,
        evidence_ref="E_NEW",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    assert updated.evidence_links[0].evidence_ref == "E_NEW"


def test_evidence_in_store_but_not_current_run_remains_invisible():
    ledger, metric, store, _, _ = _fixture(
        evidence=(_evidence("E1"),),
        current_refs=("E1",),
    )
    hypothesis = _register(ledger, metric)
    store.put(_evidence("E_FOREIGN"))

    with pytest.raises(HypothesisLedgerError, match="current governed run"):
        ledger.attach_evidence(
            hypothesis.hypothesis_id,
            evidence_ref="E_FOREIGN",
            relation=HypothesisEvidenceRelation.SUPPORTS,
        )


def test_current_evidence_view_run_must_match_ledger_run():
    _, _, store, tasks, runtime = _fixture()
    runtime.snapshot = runtime.snapshot.model_copy(update={"run_id": "other-run"})

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id="resolver:other",
        target_kind="metric",
        canonical_target={"metric": "oee"},
        parent_obligation_id=ROOT,
    )
    with pytest.raises(HypothesisLedgerError, match="another Manager run"):
        HypothesisLedger(
            parent_obligation_id=ROOT,
            accepted_contract_id="act-1",
            lineage_id="lin-1",
            run_id="run-1",
            obligation_ledger=_obligation_ledger(),
            evidence_store=store,
            evidence_view=CurrentRunEvidenceView(runtime),
            semantic_handles=handles,
            research_tasks=tasks,
            tenant_binding=TENANT,
            context_version=CTX,
        )
