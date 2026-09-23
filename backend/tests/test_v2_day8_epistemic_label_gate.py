"""Provider-free Day8 A2 attacks for epistemic claim-class gates."""

from __future__ import annotations

import pytest
from types import SimpleNamespace

from app.v2.epistemics import (
    CurrentRunEvidenceView,
    EpistemicFindingError,
    EpistemicLabelGate,
    EvidenceLinkedFindingBuilder,
    HypothesisLedger,
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
    EpistemicGateCode,
    EpistemicLabel,
    EvidenceArtifact,
    HypothesisEvidenceRelation,
    HypothesisProvenance,
    HypothesisEntry,
    ResearchTask,
)
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.semantic_handles import SemanticHandleRegistry


ROOT = "U_RC"
TENANT = "tenant-binding"
CTX = "ctx-v1"


def _obligations() -> UserObligationLedger:
    return UserObligationLedger(
        lineage_id="lin-1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id=ROOT,
                capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.ACCEPTED,
                source_refs=("src:why",),
                introduced_in_version=1,
            ),
        ),
    )


def _execution_evidence(
    artifact_id: str,
    *,
    kind: str = "standard_analytics",
    verified: bool = True,
) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        task_id="seed:U_RC",
        obligation_ids=(ROOT,),
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


def _contribution_evidence() -> tuple[EvidenceArtifact, EvidenceArtifact]:
    parent = _execution_evidence("E_BASE")
    derived = EvidenceArtifact(
        artifact_id="E_CONTRIB",
        task_id="D_CONTRIB",
        obligation_ids=(ROOT,),
        query_contract_refs=("QC1",),
        evidence_kind="derived_analytical",
        verified=True,
        payload={
            "claim_semantics": "observed_change_decomposition_noncausal",
            "segments": ({"segment": "A", "share": 0.6},),
        },
        source_kind="DERIVED_ANALYTICAL",
        parent_evidence_refs=("E_BASE",),
        parent_query_contract_refs=("QC1",),
        transformation="CONTRIBUTION",
    )
    return parent, derived


def _fixture(*evidence: EvidenceArtifact):
    if not evidence:
        evidence = (
            _execution_evidence("E_OBS"),
            _execution_evidence("E_REL", kind="relationship_analytics"),
        )

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
    if any(item.task_id == "D_CONTRIB" for item in evidence):
        tasks.register(
            ResearchTask(
                task_id="D_CONTRIB",
                question_id=ROOT,
                task_kind="CONTRIBUTION",
                input_refs=(metric.handle_id,),
                origin="AGENT_DERIVED",
                parent_task_id="seed:U_RC",
                parent_obligation_id=ROOT,
                trigger_evidence_ref="E_BASE",
                branch_depth=1,
            )
        )

    runtime = SimpleNamespace(
        snapshot=ManagerRunSnapshot(
            run_id="run-1",
            state=ManagerState.INVESTIGATING,
            evidence_refs=tuple(item.artifact_id for item in evidence),
            inspected_evidence_refs=tuple(item.artifact_id for item in evidence),
        )
    )
    ledger = HypothesisLedger(
        parent_obligation_id=ROOT,
        accepted_contract_id="act-1",
        lineage_id="lin-1",
        run_id="run-1",
        obligation_ledger=_obligations(),
        evidence_store=store,
        evidence_view=CurrentRunEvidenceView(runtime),
        semantic_handles=handles,
        research_tasks=tasks,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    return ledger, metric.handle_id


def _candidate(
    ledger: HypothesisLedger,
    metric: str,
    *,
    trigger: str,
    limitations=("Gözlemsel kanıt nedenselliği tek başına kurmaz.",),
):
    return ledger.register(
        statement="Gece vardiyası hız kaybının aday nedeni olabilir.",
        semantic_handle_refs=(metric,),
        trigger_evidence_refs=(trigger,),
        limitations=tuple(limitations),
    )


def test_finding_without_evidence_is_rejected():
    ledger, _ = _fixture()
    with pytest.raises(EpistemicFindingError, match="EVIDENCE_REQUIRED"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="ölçüm",
            epistemic_label=EpistemicLabel.OBSERVATION,
            evidence_refs=(),
        )


def test_unverified_evidence_is_rejected_before_labeling():
    bad = _execution_evidence("E_BAD", verified=False)
    ledger, _ = _fixture(bad)
    with pytest.raises(Exception, match="VERIFIED"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="ölçüm",
            epistemic_label=EpistemicLabel.OBSERVATION,
            evidence_refs=("E_BAD",),
        )


def test_relationship_evidence_allows_association():
    rel = _execution_evidence("E_REL", kind="relationship_analytics")
    ledger, _ = _fixture(rel)
    finding = EvidenceLinkedFindingBuilder(ledger=ledger).build(
        statement="Duruş süresi ile bölüm arasında ilişki gözlendi.",
        epistemic_label=EpistemicLabel.ASSOCIATION,
        evidence_refs=("E_REL",),
    )
    assert finding.epistemic_label == EpistemicLabel.ASSOCIATION


def test_relationship_evidence_cannot_confirm_cause():
    rel = _execution_evidence("E_REL", kind="relationship_analytics")
    ledger, metric = _fixture(rel)
    hyp = _candidate(ledger, metric, trigger="E_REL")
    hyp = ledger.attach_evidence(
        hyp.hypothesis_id,
        evidence_ref="E_REL",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )

    with pytest.raises(EpistemicFindingError, match="CAUSAL_NOT_IDENTIFIED"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="Kesin neden budur.",
            epistemic_label=EpistemicLabel.CONFIRMED_CAUSE,
            evidence_refs=("E_REL",),
            hypothesis_ref=hyp.hypothesis_id,
        )


def test_contribution_evidence_allows_contribution_label():
    parent, contribution = _contribution_evidence()
    ledger, _ = _fixture(parent, contribution)
    finding = EvidenceLinkedFindingBuilder(ledger=ledger).build(
        statement="Gözlenen değişimin büyük bölümü A segmentindeki değişimle ayrışıyor.",
        epistemic_label=EpistemicLabel.CONTRIBUTION,
        evidence_refs=("E_CONTRIB",),
    )
    assert finding.epistemic_label == EpistemicLabel.CONTRIBUTION


def test_contribution_evidence_cannot_confirm_cause():
    parent, contribution = _contribution_evidence()
    ledger, metric = _fixture(parent, contribution)
    hyp = _candidate(ledger, metric, trigger="E_BASE")
    hyp = ledger.attach_evidence(
        hyp.hypothesis_id,
        evidence_ref="E_CONTRIB",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )

    with pytest.raises(EpistemicFindingError, match="CAUSAL_NOT_IDENTIFIED"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="A kesin nedendir.",
            epistemic_label=EpistemicLabel.CONFIRMED_CAUSE,
            evidence_refs=("E_CONTRIB",),
            hypothesis_ref=hyp.hypothesis_id,
        )


def test_priority_signal_alone_cannot_create_candidate_cause():
    priority = _execution_evidence(
        "E_PRIORITY",
        kind="interestingness_score",
    )
    ledger, metric = _fixture(priority)
    hyp = _candidate(ledger, metric, trigger="E_PRIORITY")
    hyp = ledger.attach_evidence(
        hyp.hypothesis_id,
        evidence_ref="E_PRIORITY",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )

    with pytest.raises(EpistemicFindingError, match="PRIORITIZATION_NOT_TRUTH"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="En ilginç sinyal aday nedendir.",
            epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
            evidence_refs=("E_PRIORITY",),
            hypothesis_ref=hyp.hypothesis_id,
        )


def test_candidate_cause_without_root_authority_is_rejected():
    evidence = (_execution_evidence("E1"),)
    hypothesis = HypothesisEntry(
        hypothesis_id="H1",
        parent_obligation_id=ROOT,
        statement="candidate",
        semantic_handle_refs=("sem_governed",),
        trigger_evidence_refs=("E1",),
        evidence_links=(),
        limitations=("limitation",),
        provenance=HypothesisProvenance(
            accepted_contract_id="act-1",
            lineage_id="lin-1",
            run_id="run-1",
        ),
    )
    decision = EpistemicLabelGate().decide(
        requested_label=EpistemicLabel.CANDIDATE_CAUSE,
        evidence=evidence,
        hypothesis=hypothesis,
        root_cause_authority=False,
    )
    assert decision.allowed is False
    assert decision.code == EpistemicGateCode.ROOT_CAUSE_REQUIRED


def test_candidate_cause_without_support_evidence_is_rejected():
    obs = _execution_evidence("E_OBS")
    ledger, metric = _fixture(obs)
    hyp = _candidate(ledger, metric, trigger="E_OBS")

    with pytest.raises(EpistemicFindingError, match="HYPOTHESIS_SUPPORT_REQUIRED"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="Aday neden.",
            epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
            evidence_refs=("E_OBS",),
            hypothesis_ref=hyp.hypothesis_id,
        )


def test_candidate_cause_without_limitations_is_rejected():
    rel = _execution_evidence("E_REL", kind="relationship_analytics")
    ledger, metric = _fixture(rel)
    hyp = _candidate(ledger, metric, trigger="E_REL", limitations=())
    hyp = ledger.attach_evidence(
        hyp.hypothesis_id,
        evidence_ref="E_REL",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )

    with pytest.raises(EpistemicFindingError, match="LIMITATION_REQUIRED"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="Aday neden.",
            epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
            evidence_refs=("E_REL",),
            hypothesis_ref=hyp.hypothesis_id,
        )


def test_supported_candidate_cause_is_allowed_but_not_confirmed():
    rel = _execution_evidence("E_REL", kind="relationship_analytics")
    ledger, metric = _fixture(rel)
    hyp = _candidate(ledger, metric, trigger="E_REL")
    hyp = ledger.attach_evidence(
        hyp.hypothesis_id,
        evidence_ref="E_REL",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )

    finding = EvidenceLinkedFindingBuilder(ledger=ledger).build(
        statement="Gece vardiyası hız kaybı desteklenen bir aday nedendir.",
        epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
        evidence_refs=("E_REL",),
        hypothesis_ref=hyp.hypothesis_id,
    )
    assert finding.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
    assert finding.hypothesis_ref == hyp.hypothesis_id
    assert finding.limitations


def test_confirmed_cause_is_always_typed_deny_in_day8():
    decision = EpistemicLabelGate().decide(
        requested_label=EpistemicLabel.CONFIRMED_CAUSE,
        evidence=(_execution_evidence("E1"),),
        root_cause_authority=True,
    )
    assert decision.allowed is False
    assert decision.code == EpistemicGateCode.CAUSAL_NOT_IDENTIFIED
