"""Provider-free Day9-A attacks for deterministic ReportDocument authority."""

from __future__ import annotations

import ast
import inspect

import pytest
from pydantic import ValidationError

import app.v2.report_builder as report_builder_module
from app.v2.manager_executor import EvidenceStore
from app.v2.models import (
    EpistemicLabel,
    EvidenceArtifact,
    EvidenceLinkedFinding,
    HypothesisProvenance,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.report_builder import (
    ReportAccessPolicy,
    ReportBlockKind,
    ReportBlockSpec,
    ReportBuildRequest,
    ReportBuildStatus,
    ReportBuilder,
    ReportClaimKind,
    ReportIssueCode,
    ReportRenderSpec,
    ReportResultColumn,
    ReportResultShape,
    ReportSectionSpec,
    ReportSourceProvenance,
)
from app.v2.semantic_handles import SemanticHandleRegistry


TENANT = "tenant-day9"
CTX = "ctx-day9"
RUN = "mgr-day9"
CONTRACT = "contract-day9"
LINEAGE = "lineage-day9"


def _provenance() -> ReportSourceProvenance:
    return ReportSourceProvenance(
        accepted_contract_id=CONTRACT,
        lineage_id=LINEAGE,
        run_id=RUN,
        tenant_binding=TENANT,
        context_version=CTX,
    )


def _evidence(
    ref: str,
    *,
    verified: bool = True,
    query_contract_refs: tuple[str, ...] = ("QC1",),
    source_kind: str = "EXECUTION",
    parent_evidence_refs: tuple[str, ...] = (),
    parent_query_contract_refs: tuple[str, ...] = (),
    transformation: str | None = None,
) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=ref,
        task_id=f"task-{ref}",
        obligation_ids=("U1",),
        query_contract_refs=query_contract_refs,
        evidence_kind="standard_analytics",
        verified=verified,
        payload={"columns": ("Sales.revenue",), "row_count": 1},
        source_kind=source_kind,
        parent_evidence_refs=parent_evidence_refs,
        parent_query_contract_refs=parent_query_contract_refs,
        transformation=transformation,
    )


def _finding(
    ref: str,
    *,
    evidence_refs: tuple[str, ...] = ("E1",),
    label: EpistemicLabel = EpistemicLabel.CANDIDATE_CAUSE,
    limitations: tuple[str, ...] = ("Gözlemsel kanıt nedensellik ispatı değildir.",),
    run_id: str = RUN,
) -> EvidenceLinkedFinding:
    return EvidenceLinkedFinding(
        finding_id=ref,
        parent_obligation_id="U_ROOT",
        statement="Gelir düşüşü aday açıklama ile uyumludur.",
        epistemic_label=label,
        evidence_refs=evidence_refs,
        hypothesis_ref="hyp_day9" if label in {
            EpistemicLabel.CANDIDATE_CAUSE,
            EpistemicLabel.CONFIRMED_CAUSE,
        } else None,
        limitations=limitations,
        provenance=HypothesisProvenance(
            accepted_contract_id=CONTRACT,
            lineage_id=LINEAGE,
            run_id=run_id,
        ),
    )


def _handles() -> tuple[SemanticHandleRegistry, str]:
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id="day9-metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day9-revenue",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
        parent_obligation_id="U1",
    )
    return handles, metric.handle_id


def _builder(
    *,
    evidence: tuple[EvidenceArtifact, ...] = (_evidence("E1"),),
    current_refs: tuple[str, ...] | None = None,
    findings: tuple[EvidenceLinkedFinding, ...] = (),
    known_artifacts=None,
):
    store = EvidenceStore()
    for item in evidence:
        store.put(item)
    handles, metric_ref = _handles()
    return (
        ReportBuilder(
            evidence_store=store,
            current_evidence_refs=(
                tuple(item.artifact_id for item in evidence)
                if current_refs is None
                else current_refs
            ),
            findings=findings,
            semantic_handles=handles,
            known_artifacts=known_artifacts or {},
            provenance=_provenance(),
        ),
        store,
        metric_ref,
    )


def _request(
    block: ReportBlockSpec,
    *,
    semantic_scope: tuple[str, ...] = (),
    title: str = "Gelir Raporu",
) -> ReportBuildRequest:
    return ReportBuildRequest(
        title=title,
        sections=(
            ReportSectionSpec(
                title="Özet",
                blocks=(block,),
                semantic_scope=semantic_scope,
            ),
        ),
    )


def _analytical_block(*, evidence_refs=("E1",), content="Gelir önceki döneme göre düştü."):
    return ReportBlockSpec(
        block_kind=ReportBlockKind.TEXT,
        claim_kind=ReportClaimKind.ANALYTICAL,
        content=content,
        evidence_refs=evidence_refs,
    )


def test_numeric_claim_without_evidence_returns_needs_evidence():
    builder, _, _ = _builder()
    result = builder.build(
        _request(
            ReportBlockSpec(
                block_kind=ReportBlockKind.KPI,
                claim_kind=ReportClaimKind.NUMERIC,
                content="Net gelir: 100",
            )
        )
    )
    assert result.status == ReportBuildStatus.NEEDS_EVIDENCE
    assert result.report is None
    assert result.issues[0].code == ReportIssueCode.EVIDENCE_REQUIRED


def test_analytical_claim_without_evidence_returns_needs_evidence():
    builder, _, _ = _builder()
    result = builder.build(_request(_analytical_block(evidence_refs=())))
    assert result.status == ReportBuildStatus.NEEDS_EVIDENCE
    assert result.issues[0].code == ReportIssueCode.EVIDENCE_REQUIRED


def test_unknown_evidence_ref_is_not_magically_true():
    builder, _, _ = _builder(current_refs=("E_UNKNOWN",))
    result = builder.build(_request(_analytical_block(evidence_refs=("E_UNKNOWN",))))
    assert result.status == ReportBuildStatus.NEEDS_EVIDENCE
    assert result.issues[0].code == ReportIssueCode.UNKNOWN_EVIDENCE


def test_unverified_evidence_is_rejected_as_report_support():
    builder, _, _ = _builder(evidence=(_evidence("E1", verified=False),))
    result = builder.build(_request(_analytical_block()))
    assert result.status == ReportBuildStatus.NEEDS_EVIDENCE
    assert result.issues[0].code == ReportIssueCode.UNVERIFIED_EVIDENCE


def test_verified_evidence_backed_claim_builds_canonical_report():
    builder, _, metric_ref = _builder()
    result = builder.build(
        _request(_analytical_block(), semantic_scope=(metric_ref,))
    )
    assert result.status == ReportBuildStatus.COMPLETE
    report = result.report
    assert report is not None
    assert report.report_id.startswith("rpt_")
    assert report.sections[0].section_id.startswith("rsec_")
    assert report.sections[0].followup_context_ref.startswith("rctx_")
    assert report.evidence_index[0].evidence_ref == "E1"
    assert report.evidence_index[0].query_contract_refs == ("QC1",)
    assert (
        report.provenance.access_policy
        == ReportAccessPolicy.CURRENT_RUN_ONLY_REAUTHORIZE_ON_REPLAY
    )


def test_finding_with_missing_derived_parent_lineage_never_becomes_cached_truth():
    child = _evidence(
        "E_CHILD",
        query_contract_refs=("QC_PARENT", "QC_CHILD"),
        source_kind="DERIVED_ANALYTICAL",
        parent_evidence_refs=("E_PARENT",),
        parent_query_contract_refs=("QC_PARENT",),
        transformation="TREND",
    )
    finding = _finding("F1", evidence_refs=("E_CHILD",))
    builder, _, _ = _builder(
        evidence=(child,),
        current_refs=("E_CHILD", "E_PARENT"),
        findings=(finding,),
    )
    request = _request(
        ReportBlockSpec(
            block_kind=ReportBlockKind.ROOT_CAUSE,
            claim_kind=ReportClaimKind.EPISTEMIC,
            content="Aday neden.",
            finding_refs=("F1",),
        )
    )

    first = builder.build(request)
    second = builder.build(request)

    assert first.status == second.status == ReportBuildStatus.NEEDS_EVIDENCE
    assert any(issue.code == ReportIssueCode.UNKNOWN_EVIDENCE for issue in first.issues)
    assert any(issue.ref == "E_PARENT" for issue in second.issues)


def test_candidate_cause_label_and_limitations_are_preserved():
    finding = _finding("F1")
    builder, _, _ = _builder(findings=(finding,))
    result = builder.build(
        _request(
            ReportBlockSpec(
                block_kind=ReportBlockKind.ROOT_CAUSE,
                claim_kind=ReportClaimKind.EPISTEMIC,
                content="Gelir düşüşü için aday açıklama.",
                finding_refs=("F1",),
            )
        )
    )
    assert result.status == ReportBuildStatus.COMPLETE
    block = result.report.sections[0].blocks[0]
    assert block.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
    assert block.hypothesis_ref == "hyp_day9"
    assert finding.limitations[0] in block.limitations
    assert block.finding_refs[0].finding_ref == "F1"
    assert block.evidence_refs[0].evidence_ref == "E1"


def test_finding_ref_cannot_be_hidden_inside_non_epistemic_claim():
    finding = _finding("F1")
    builder, _, _ = _builder(findings=(finding,))
    result = builder.build(
        _request(
            ReportBlockSpec(
                block_kind=ReportBlockKind.TEXT,
                claim_kind=ReportClaimKind.ANALYTICAL,
                content="Analitik yorum.",
                evidence_refs=("E1",),
                finding_refs=("F1",),
            )
        )
    )
    assert result.status == ReportBuildStatus.REJECTED
    assert result.issues[0].code == ReportIssueCode.FINDING_CLAIM_KIND_MISMATCH


def test_confirmed_cause_cannot_be_laundered_into_report():
    finding = _finding("F_BAD", label=EpistemicLabel.CONFIRMED_CAUSE)
    builder, _, _ = _builder(findings=(finding,))
    result = builder.build(
        _request(
            ReportBlockSpec(
                block_kind=ReportBlockKind.ROOT_CAUSE,
                claim_kind=ReportClaimKind.EPISTEMIC,
                content="Kesin neden.",
                finding_refs=("F_BAD",),
            )
        )
    )
    assert result.status == ReportBuildStatus.REJECTED
    assert result.issues[0].code == ReportIssueCode.CONFIRMED_CAUSE_UNAVAILABLE


def test_section_semantic_scope_accepts_existing_governed_refs_only():
    builder, _, metric_ref = _builder()
    ok = builder.build(
        _request(_analytical_block(), semantic_scope=(metric_ref,))
    )
    assert ok.status == ReportBuildStatus.COMPLETE
    assert ok.report.sections[0].semantic_scope == (metric_ref,)

    bad = builder.build(
        _request(
            _analytical_block(),
            semantic_scope=("sem_" + "f" * 24,),
        )
    )
    assert bad.status == ReportBuildStatus.REJECTED
    assert bad.issues[0].code == ReportIssueCode.INVALID_SEMANTIC_SCOPE


def test_followup_context_is_server_owned_and_stable():
    builder, _, metric_ref = _builder()
    first = builder.build(
        _request(_analytical_block(), semantic_scope=(metric_ref,))
    )
    second = builder.build(
        _request(
            _analytical_block(content="Presentation wording changed."),
            semantic_scope=(metric_ref,),
            title="Different presentation title",
        )
    )
    assert first.status == second.status == ReportBuildStatus.COMPLETE
    assert first.report.report_id == second.report.report_id
    assert first.report.sections[0].section_id == second.report.sections[0].section_id
    assert (
        first.report.sections[0].followup_context_ref
        == second.report.sections[0].followup_context_ref
    )


def test_broken_artifact_ref_rejects_report_without_mutating_evidence():
    builder, store, _ = _builder(known_artifacts={"art_ok": ReportBlockKind.CHART})
    before = store.get("E1")
    result = builder.build(
        _request(
            ReportBlockSpec(
                block_kind=ReportBlockKind.CHART,
                claim_kind=ReportClaimKind.ANALYTICAL,
                content="Gelir grafiği.",
                evidence_refs=("E1",),
                artifact_ref="art_missing",
            )
        )
    )
    assert result.status == ReportBuildStatus.REJECTED
    assert result.issues[0].code == ReportIssueCode.UNKNOWN_ARTIFACT
    assert store.get("E1") == before
    assert store.get("E1").verified is True


def test_render_shape_is_presentation_support_not_semantic_inference():
    builder, _, _ = _builder(known_artifacts={"art_chart": ReportBlockKind.CHART})
    render = ReportRenderSpec(
        presentation_kind=ReportBlockKind.CHART,
        result_shape=ReportResultShape(
            columns=(
                ReportResultColumn(
                    name="opaque_col_1",
                    data_type="DOUBLE",
                    unit="TRY",
                    semantic_role="measure",
                ),
            ),
            row_count=1,
            truncated=False,
        ),
        options=(("display", "bar"),),
    )
    result = builder.build(
        _request(
            ReportBlockSpec(
                block_kind=ReportBlockKind.CHART,
                claim_kind=ReportClaimKind.ANALYTICAL,
                content="Gelir görünümü.",
                evidence_refs=("E1",),
                artifact_ref="art_chart",
                render_spec=render,
            )
        )
    )
    assert result.status == ReportBuildStatus.COMPLETE
    block = result.report.sections[0].blocks[0]
    assert block.render_spec == render
    assert block.evidence_refs[0].evidence_ref == "E1"


def test_raw_tool_payload_cannot_become_authoritative_report_content():
    with pytest.raises(ValidationError):
        ReportBlockSpec.model_validate(
            {
                "block_kind": "TABLE",
                "claim_kind": "ANALYTICAL",
                "content": {"columns": ["x"], "rows": [{"x": 1}]},
                "evidence_refs": ["E1"],
            }
        )


def test_reference_order_permutations_normalize_to_same_report_and_section_order():
    e1 = _evidence("E1", query_contract_refs=("QC2", "QC1"))
    e2 = _evidence("E2", query_contract_refs=("QC3",))
    builder, _, metric_ref = _builder(evidence=(e1, e2))

    s1 = ReportSectionSpec(
        title="Bir",
        semantic_scope=(metric_ref,),
        evidence_refs=("E2", "E1", "E2"),
        blocks=(
            ReportBlockSpec(
                block_kind=ReportBlockKind.TABLE,
                claim_kind=ReportClaimKind.ANALYTICAL,
                content="Birinci.",
                evidence_refs=("E2",),
            ),
        ),
    )
    s2 = ReportSectionSpec(
        title="İki",
        semantic_scope=(metric_ref,),
        blocks=(
            ReportBlockSpec(
                block_kind=ReportBlockKind.KPI,
                claim_kind=ReportClaimKind.NUMERIC,
                content="İkinci.",
                evidence_refs=("E1",),
            ),
        ),
    )

    first = builder.build(ReportBuildRequest(title="R", sections=(s1, s2)))
    second = builder.build(ReportBuildRequest(title="R2", sections=(s2, s1)))
    assert first.status == second.status == ReportBuildStatus.COMPLETE
    assert first.report.report_id == second.report.report_id
    assert [s.section_id for s in first.report.sections] == [
        s.section_id for s in second.report.sections
    ]
    assert [ref.evidence_ref for ref in first.report.evidence_index] == ["E1", "E2"]
    assert first.report.evidence_index[0].query_contract_refs == ("QC1", "QC2")


def test_report_builder_has_no_analytics_or_probabilistic_runtime_dependency():
    source = inspect.getsource(report_builder_module)
    tree = ast.parse(source)

    imported = set()
    forbidden_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {
                "cube_sql",
                "query",
                "structured_json",
                "resolve",
                "recommend",
            }:
                forbidden_calls.append(node.func.attr)

    assert not any(
        name.startswith(
            (
                "app.wren",
                "app.report",
                "app.viz",
                "app.llm",
                "app.v2.semantic_linker",
                "app.v2.semantic_retriever",
            )
        )
        for name in imported
    )
    assert forbidden_calls == []
