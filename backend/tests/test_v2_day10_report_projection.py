"""Provider-free D10-B deterministic research presentation/report projection."""

from __future__ import annotations

from app.v2.manager_executor import EvidenceStore
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    UserObligationLedger,
)
from app.v2.models import (
    EpistemicLabel,
    EvidenceArtifact,
    EvidenceLinkedFinding,
    HypothesisProvenance,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.report_builder import (
    ReportBlockKind,
    ReportBuildStatus,
    ReportBuilder,
    ReportClaimKind,
    ReportSourceProvenance,
)
from app.v2.research_report_projector import (
    ResearchReportProjectionStatus,
    ResearchReportProjector,
)
from app.v2.semantic_handles import SemanticHandleRegistry


TENANT = "tenant-day10"
CTX = "ctx-day10"
RUN = "mgr-day10"
CONTRACT = "atc-day10"
LINEAGE = "atl-day10"


def _handles():
    registry = SemanticHandleRegistry()
    metric = registry.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id="metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-candidate",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    dimension = registry.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id="dimension",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="dimension-candidate",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
    )
    return registry, metric.handle_id, dimension.handle_id


def _item(
    obligation_id: str,
    capability: ManagerCapabilityKey,
    handles: tuple[str, ...],
    *,
    status: ObligationStatus = ObligationStatus.VERIFIED,
    blocker: str | None = None,
):
    return ObligationLedgerItem(
        obligation_id=obligation_id,
        capability_key=capability,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=status,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=handles,
        introduced_in_version=1,
        blocker=blocker,
    )


def _execution_evidence(
    evidence_ref: str,
    obligation_id: str,
    metric: str,
    *,
    kind: str = "standard_analytics",
    value=125.0,
):
    return EvidenceArtifact(
        artifact_id=evidence_ref,
        task_id=f"seed:{obligation_id}",
        obligation_ids=(obligation_id,),
        query_contract_refs=(f"QC_{evidence_ref}",),
        evidence_kind=kind,
        verified=True,
        payload={
            "executions": (
                {
                    "execution_id": f"exec-{evidence_ref}",
                    "role": "primary",
                    "columns": (metric,),
                    "row_count": 1,
                    "rows": ({metric: value},),
                },
            ),
            "query_count": 1,
        },
    )


def _builder(registry, evidence, findings):
    store = EvidenceStore()
    for item in evidence:
        store.put(item)
    return ReportBuilder(
        evidence_store=store,
        current_evidence_refs=tuple(item.artifact_id for item in evidence),
        findings=findings,
        semantic_handles=registry,
        known_artifacts={},
        provenance=ReportSourceProvenance(
            accepted_contract_id=CONTRACT,
            lineage_id=LINEAGE,
            run_id=RUN,
            tenant_binding=TENANT,
            context_version=CTX,
        ),
    ), store


def test_verified_scalar_evidence_projects_to_kpi_without_semantic_guessing():
    registry, metric, _ = _handles()
    evidence = _execution_evidence("E1", "U1", metric, value=125.0)
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(_item("U1", ManagerCapabilityKey.PERFORMANCE, (metric,)),),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(ledger=ledger, evidence=(evidence,), findings=())

    assert projection.status == ResearchReportProjectionStatus.COMPLETE
    assert projection.omitted_evidence_refs == ()
    assert len(projection.artifacts) == 1
    assert projection.artifacts[0].artifact_kind == ReportBlockKind.KPI
    block = projection.request.sections[0].blocks[0]
    assert block.claim_kind == ReportClaimKind.NUMERIC
    assert block.content == "Sales.revenue: 125.0"
    assert metric not in block.content


def test_required_report_is_delivery_authority_not_separate_evidence_requirement():
    registry, metric, _ = _handles()
    evidence = _execution_evidence("E_REPORT", "U_ANALYTICAL", metric, value=42.0)
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item("U_ANALYTICAL", ManagerCapabilityKey.PERFORMANCE, (metric,)),
            _item(
                "U_REPORT",
                ManagerCapabilityKey.REPORT,
                (),
                status=ObligationStatus.ACCEPTED,
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(
        ledger=ledger,
        evidence=(evidence,),
        findings=(),
    )

    assert projection.status == ResearchReportProjectionStatus.COMPLETE
    assert projection.request is not None
    assert projection.request.title == "Araştırma Raporu"
    assert projection.omitted_evidence_refs == ()
    assert not any("U_REPORT" in issue for issue in projection.issues)


def test_relationship_evidence_stays_noncausal_and_uses_comparison_artifact():
    registry, metric, dimension = _handles()
    evidence = EvidenceArtifact(
        artifact_id="E_REL",
        task_id="seed:U_REL",
        obligation_ids=("U_REL",),
        query_contract_refs=("QC_REL",),
        evidence_kind="relationship_analytics",
        verified=True,
        payload={
            "executions": (
                {
                    "execution_id": "rel",
                    "role": "primary",
                    "columns": (metric, dimension),
                    "row_count": 2,
                    "rows": (
                        {metric: 10.0, dimension: "A"},
                        {metric: 12.0, dimension: "B"},
                    ),
                },
            ),
            "query_count": 1,
        },
    )
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item(
                "U_REL",
                ManagerCapabilityKey.RELATIONSHIP,
                (metric, dimension),
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(ledger=ledger, evidence=(evidence,), findings=())

    artifact = projection.artifacts[0]
    block = projection.request.sections[0].blocks[0]
    assert artifact.artifact_kind == ReportBlockKind.COMPARISON
    assert block.claim_kind == ReportClaimKind.ANALYTICAL
    assert "ilişki analizi" in block.content.lower()
    assert "neden" not in block.content.lower()
    assert "cause" not in block.content.lower()


def test_every_verified_evidence_is_accounted_even_without_active_obligation_owner():
    registry, metric, _ = _handles()
    owned = _execution_evidence("E1", "U1", metric)
    extra = _execution_evidence("E_EXTRA", "OLD", metric, value=50.0)
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(_item("U1", ManagerCapabilityKey.PERFORMANCE, (metric,)),),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(
        ledger=ledger,
        evidence=(owned, extra),
        findings=(),
    )

    assert projection.status == ResearchReportProjectionStatus.COMPLETE
    assert projection.omitted_evidence_refs == ()
    assert set(projection.accounted_evidence_refs) == {"E1", "E_EXTRA"}
    assert any(section.title == "Ek Doğrulanmış Kanıt" for section in projection.request.sections)


def test_uncovered_user_must_fails_report_completeness_instead_of_inventing_content():
    registry, metric, _ = _handles()
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item(
                "U_MISSING",
                ManagerCapabilityKey.PERFORMANCE,
                (metric,),
                status=ObligationStatus.IN_PROGRESS,
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(ledger=ledger, evidence=(), findings=())

    assert projection.status == ResearchReportProjectionStatus.INCOMPLETE
    assert projection.request is None
    assert any("U_MISSING" in issue for issue in projection.issues)


def test_data_gap_is_explicit_caveat_not_fake_evidence():
    registry, metric, _ = _handles()
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item(
                "U_GAP",
                ManagerCapabilityKey.RELATIONSHIP,
                (metric,),
                status=ObligationStatus.BLOCKED_DATA_GAP,
                blocker="Güvenli ilişki yolu mevcut değil.",
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(ledger=ledger, evidence=(), findings=())

    assert projection.status == ResearchReportProjectionStatus.COMPLETE
    block = projection.request.sections[0].blocks[0]
    assert block.block_kind == ReportBlockKind.CAVEAT
    assert block.claim_kind == ReportClaimKind.LIMITATION
    assert block.evidence_refs == ()
    assert block.content == "Güvenli ilişki yolu mevcut değil."


def test_canonical_candidate_cause_flows_through_frozen_report_builder():
    registry, metric, _ = _handles()
    evidence = _execution_evidence("E_CAUSE", "U_ROOT", metric)
    finding = EvidenceLinkedFinding(
        finding_id="find_" + "a" * 24,
        parent_obligation_id="U_ROOT",
        statement="Bakım düzeni gözlenen düşüş için aday açıklamadır.",
        epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
        evidence_refs=("E_CAUSE",),
        hypothesis_ref="hyp_" + "b" * 24,
        limitations=("Gözlemsel kanıt nedenselliği doğrulamaz.",),
        provenance=HypothesisProvenance(
            accepted_contract_id=CONTRACT,
            lineage_id=LINEAGE,
            run_id=RUN,
        ),
    )
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item(
                "U_ROOT",
                ManagerCapabilityKey.ROOT_CAUSE,
                (metric,),
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(
        ledger=ledger,
        evidence=(evidence,),
        findings=(finding,),
    )
    assert projection.status == ResearchReportProjectionStatus.COMPLETE

    store = EvidenceStore()
    store.put(evidence)
    result = ReportBuilder(
        evidence_store=store,
        current_evidence_refs=("E_CAUSE",),
        findings=(finding,),
        semantic_handles=registry,
        known_artifacts={
            item.artifact_id: item.artifact_kind
            for item in projection.artifacts
        },
        provenance=ReportSourceProvenance(
            accepted_contract_id=CONTRACT,
            lineage_id=LINEAGE,
            run_id=RUN,
            tenant_binding=TENANT,
            context_version=CTX,
        ),
    ).build(projection.request)

    assert result.status == ReportBuildStatus.COMPLETE
    root_blocks = [
        block
        for section in result.report.sections
        for block in section.blocks
        if block.claim_kind == ReportClaimKind.EPISTEMIC
    ]
    assert len(root_blocks) == 1
    assert root_blocks[0].epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
    assert root_blocks[0].content == finding.statement
    assert finding.limitations[0] in root_blocks[0].limitations


def test_projector_api_has_no_observation_or_freeform_manager_truth_input():
    names = ResearchReportProjector.project.__annotations__
    signature_text = str(names)
    assert "observations" not in signature_text
    assert "manager_prompt" not in signature_text


def test_answer_now_partial_keeps_verified_evidence_and_marks_pending_must_as_caveat():
    registry, metric, dimension = _handles()
    evidence = _execution_evidence("E_PARTIAL", "U_DONE", metric, value=88.0)
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item("U_DONE", ManagerCapabilityKey.PERFORMANCE, (metric,)),
            _item(
                "U_PENDING",
                ManagerCapabilityKey.RELATIONSHIP,
                (metric, dimension),
                status=ObligationStatus.IN_PROGRESS,
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(
        ledger=ledger,
        evidence=(evidence,),
        findings=(),
        allow_partial=True,
    )

    assert projection.status == ResearchReportProjectionStatus.COMPLETE
    assert projection.request is not None
    assert projection.request.title.endswith("Kısmi")
    assert projection.omitted_evidence_refs == ()
    assert "E_PARTIAL" in projection.accounted_evidence_refs

    pending = next(
        section
        for section in projection.request.sections
        if section.title == "İlişki Analizi"
    )
    assert len(pending.blocks) == 1
    block = pending.blocks[0]
    assert block.block_kind == ReportBlockKind.CAVEAT
    assert block.claim_kind == ReportClaimKind.LIMITATION
    assert block.evidence_refs == ()
    assert "henüz VERIFIED Evidence yok" in block.content
    assert any("Kısmi yanıt" in item for item in projection.request.limitations)


def test_answer_now_partial_without_verified_evidence_fails_closed():
    registry, metric, _ = _handles()
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item(
                "U_PENDING",
                ManagerCapabilityKey.PERFORMANCE,
                (metric,),
                status=ObligationStatus.IN_PROGRESS,
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(
        ledger=ledger,
        evidence=(),
        findings=(),
        allow_partial=True,
    )

    assert projection.status == ResearchReportProjectionStatus.INCOMPLETE
    assert projection.request is None
    assert projection.artifacts == ()
    assert projection.issues == (
        "answer-now partial requires at least one VERIFIED EvidenceArtifact",
    )


def test_full_report_mode_still_rejects_uncovered_pending_must():
    registry, metric, dimension = _handles()
    evidence = _execution_evidence("E_DONE", "U_DONE", metric, value=10.0)
    ledger = UserObligationLedger(
        lineage_id=LINEAGE,
        version=1,
        items=(
            _item("U_DONE", ManagerCapabilityKey.PERFORMANCE, (metric,)),
            _item(
                "U_PENDING",
                ManagerCapabilityKey.RELATIONSHIP,
                (metric, dimension),
                status=ObligationStatus.IN_PROGRESS,
            ),
        ),
    )

    projection = ResearchReportProjector(
        semantic_handles=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    ).project(
        ledger=ledger,
        evidence=(evidence,),
        findings=(),
    )

    assert projection.status == ResearchReportProjectionStatus.INCOMPLETE
    assert projection.request is None
    assert any("U_PENDING" in issue for issue in projection.issues)
