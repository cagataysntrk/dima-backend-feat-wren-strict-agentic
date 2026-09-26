"""Deterministic Day10 Research -> presentation/report projection.

This layer owns presentation structure only. It references canonical Evidence and
Findings and never executes analytics, resolves new semantics, or asks an LLM to author
claims.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Iterable

from pydantic import Field

from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityRegistry,
)
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationStatus,
    UserObligationLedger,
)
from app.v2.models import (
    EpistemicLabel,
    EvidenceArtifact,
    EvidenceLinkedFinding,
    FrozenModel,
    ResolvedSemanticRef,
)
from app.v2.report_builder import (
    ReportBlockKind,
    ReportBlockSpec,
    ReportBuildRequest,
    ReportClaimKind,
    ReportRenderSpec,
    ReportResultColumn,
    ReportResultShape,
    ReportSectionSpec,
)
from app.v2.semantic_handles import SemanticHandleRegistry


class ResearchReportProjectionStatus(StrEnum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class PresentationArtifact(FrozenModel):
    """Non-authoritative presentation object backed by canonical Evidence references."""

    artifact_id: str = Field(pattern=r"^part_[a-f0-9]{24}$")
    artifact_kind: ReportBlockKind
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    render_spec: ReportRenderSpec
    result_shape: ReportResultShape


class ResearchReportProjection(FrozenModel):
    status: ResearchReportProjectionStatus
    request: ReportBuildRequest | None = None
    artifacts: tuple[PresentationArtifact, ...] = ()
    accounted_evidence_refs: tuple[str, ...] = ()
    omitted_evidence_refs: tuple[str, ...] = ()
    issues: tuple[str, ...] = ()


_SECTION_TITLES = {
    ManagerCapabilityKey.PERFORMANCE: "Performans",
    ManagerCapabilityKey.BREAKDOWN: "Kırılım",
    ManagerCapabilityKey.RANKING: "Sıralama",
    ManagerCapabilityKey.COMPARISON: "Karşılaştırma",
    ManagerCapabilityKey.RELATIONSHIP: "İlişki Analizi",
    ManagerCapabilityKey.ROOT_CAUSE: "Aday Nedenler",
    ManagerCapabilityKey.TREND: "Trend",
    ManagerCapabilityKey.REPORT: "Rapor",
    ManagerCapabilityKey.TABLE: "Tablo",
    ManagerCapabilityKey.CHART: "Görsel",
    ManagerCapabilityKey.EXPLAIN: "Açıklama",
}


def _stable_id(prefix: str, payload: object) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


class ResearchReportProjector:
    """Project governed research truth into D9-A ReportBuildRequest."""

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        tenant_binding: str,
        context_version: str,
        capabilities: ManagerCapabilityRegistry | None = None,
    ) -> None:
        self._handles = semantic_handles
        self._tenant = tenant_binding
        self._context = context_version
        self._capabilities = capabilities or ManagerCapabilityRegistry()

    def project(
        self,
        *,
        ledger: UserObligationLedger,
        evidence: tuple[EvidenceArtifact, ...],
        findings: tuple[EvidenceLinkedFinding, ...],
        allow_partial: bool = False,
    ) -> ResearchReportProjection:
        verified = tuple(item for item in evidence if item.verified)
        if allow_partial and not verified:
            return ResearchReportProjection(
                status=ResearchReportProjectionStatus.INCOMPLETE,
                issues=(
                    "answer-now partial requires at least one VERIFIED EvidenceArtifact",
                ),
            )
        evidence_by_id = {item.artifact_id: item for item in verified}
        # Presentation USER_MUST authority remains in the accepted ledger, but it is
        # not an Evidence-producing analytical obligation. REPORT delivery is fulfilled
        # by the ReportDocument built from the completed analytical projection below.
        # Keeping presentation items out of Evidence completeness prevents a circular
        # requirement (Research cannot produce the report before Product projection).
        active = tuple(
            item
            for item in ledger.active_user_must
            if self._capabilities.get(item.capability_key).execution_mode
            != ManagerCapabilityExecutionMode.PRESENTATION
        )
        presentation = tuple(
            item
            for item in ledger.active_user_must
            if self._capabilities.get(item.capability_key).execution_mode
            == ManagerCapabilityExecutionMode.PRESENTATION
        )
        active_by_id = {item.obligation_id: item for item in active}
        issues: list[str] = []
        if not active:
            issues.append("research report has no analytical USER_MUST authority")

        artifacts = tuple(self._artifact(item) for item in verified)
        artifact_by_evidence = {
            artifact.evidence_refs[0]: artifact
            for artifact in artifacts
        }

        evidence_for_obligation: dict[str, list[EvidenceArtifact]] = {
            item.obligation_id: [] for item in active
        }
        unassigned: list[EvidenceArtifact] = []
        assigned_evidence: set[str] = set()

        for item in verified:
            owners = [
                obligation_id
                for obligation_id in item.obligation_ids
                if obligation_id in active_by_id
            ]
            if owners:
                # One material block has one section owner. The Evidence itself may
                # still satisfy multiple obligations in the completeness accounting.
                evidence_for_obligation[owners[0]].append(item)
                assigned_evidence.add(item.artifact_id)
            else:
                unassigned.append(item)

        findings_for_obligation: dict[str, list[EvidenceLinkedFinding]] = {
            item.obligation_id: [] for item in active
        }
        for finding in findings:
            if finding.epistemic_label == EpistemicLabel.CONFIRMED_CAUSE:
                issues.append(
                    f"{finding.finding_id}: CONFIRMED_CAUSE is unavailable"
                )
                continue
            if finding.parent_obligation_id not in active_by_id:
                issues.append(
                    f"{finding.finding_id}: finding parent is outside active USER_MUST"
                )
                continue
            if any(ref not in evidence_by_id for ref in finding.evidence_refs):
                issues.append(
                    f"{finding.finding_id}: finding Evidence is outside current verified set"
                )
                continue
            findings_for_obligation[finding.parent_obligation_id].append(finding)

        sections: list[ReportSectionSpec] = []
        for obligation in active:
            owned_evidence = evidence_for_obligation[obligation.obligation_id]
            owned_findings = findings_for_obligation[obligation.obligation_id]
            all_support = tuple(
                item
                for item in verified
                if obligation.obligation_id in item.obligation_ids
            )
            explicit_gap = obligation.status in {
                ObligationStatus.BLOCKED_DATA_GAP,
                ObligationStatus.LIMITED,
                ObligationStatus.UNSUPPORTED,
            } or bool(obligation.blocker)

            pending_partial = (
                allow_partial
                and not all_support
                and not owned_findings
                and not explicit_gap
            )
            if (
                not all_support
                and not owned_findings
                and not explicit_gap
                and not pending_partial
            ):
                issues.append(
                    f"{obligation.obligation_id}: USER_MUST has no Evidence/Finding/data-gap"
                )
                continue

            blocks: list[ReportBlockSpec] = []
            section_evidence: list[str] = []
            semantic_scope: list[str] = list(obligation.semantic_handle_refs)
            limitations: list[str] = []

            for item in owned_evidence:
                artifact = artifact_by_evidence[item.artifact_id]
                blocks.append(
                    self._evidence_block(
                        item,
                        artifact=artifact,
                    )
                )
                section_evidence.append(item.artifact_id)
                semantic_scope.extend(self._evidence_handles(item))
                limitations.extend(item.limitations)

            for finding in owned_findings:
                blocks.append(
                    ReportBlockSpec(
                        block_kind=ReportBlockKind.ROOT_CAUSE,
                        claim_kind=ReportClaimKind.EPISTEMIC,
                        content=finding.statement,
                        finding_refs=(finding.finding_id,),
                        limitations=finding.limitations,
                    )
                )
                section_evidence.extend(finding.evidence_refs)
                limitations.extend(finding.limitations)

            if not blocks and explicit_gap:
                limitation = (
                    obligation.blocker
                    or obligation.verdict
                    or f"{obligation.capability_key.value}: {obligation.status.value}"
                )
                blocks.append(
                    ReportBlockSpec(
                        block_kind=ReportBlockKind.CAVEAT,
                        claim_kind=ReportClaimKind.LIMITATION,
                        content=limitation,
                        limitations=(limitation,),
                    )
                )
                limitations.append(limitation)

            if not blocks and pending_partial:
                limitation = (
                    f"{obligation.capability_key.value}: "
                    "bu USER_MUST için henüz VERIFIED Evidence yok; araştırma tamamlanmadı."
                )
                blocks.append(
                    ReportBlockSpec(
                        block_kind=ReportBlockKind.CAVEAT,
                        claim_kind=ReportClaimKind.LIMITATION,
                        content=limitation,
                        limitations=(limitation,),
                    )
                )
                limitations.append(limitation)

            if blocks:
                sections.append(
                    ReportSectionSpec(
                        title=_SECTION_TITLES.get(
                            obligation.capability_key,
                            obligation.capability_key.value,
                        ),
                        blocks=tuple(blocks),
                        evidence_refs=_unique(section_evidence),
                        semantic_scope=_unique(semantic_scope),
                        limitations=_unique(limitations),
                    )
                )

        if unassigned:
            blocks = []
            scope: list[str] = []
            limitations: list[str] = []
            for item in unassigned:
                artifact = artifact_by_evidence[item.artifact_id]
                blocks.append(self._evidence_block(item, artifact=artifact))
                scope.extend(self._evidence_handles(item))
                limitations.extend(item.limitations)
                assigned_evidence.add(item.artifact_id)
            sections.append(
                ReportSectionSpec(
                    title="Ek Doğrulanmış Kanıt",
                    blocks=tuple(blocks),
                    evidence_refs=tuple(item.artifact_id for item in unassigned),
                    semantic_scope=_unique(scope),
                    limitations=_unique(limitations),
                )
            )

        # Findings reference Evidence that may already belong to another section; this is
        # legitimate cross-section citation and not material Evidence omission.
        accounted = set(assigned_evidence)
        accounted.update(
            ref
            for finding in findings
            for ref in finding.evidence_refs
            if ref in evidence_by_id
        )
        omitted = tuple(
            item.artifact_id
            for item in verified
            if item.artifact_id not in accounted
        )
        if omitted:
            issues.append(
                "material verified Evidence omitted from report projection: "
                + ", ".join(omitted)
            )

        if issues or not sections:
            if not sections and not issues:
                issues.append("research report has no material section")
            return ResearchReportProjection(
                status=ResearchReportProjectionStatus.INCOMPLETE,
                artifacts=artifacts,
                accounted_evidence_refs=tuple(sorted(accounted)),
                omitted_evidence_refs=omitted,
                issues=tuple(issues),
            )

        report_limitations = [
            limitation
            for item in verified
            for limitation in item.limitations
        ]
        if allow_partial:
            report_limitations.append(
                "Kısmi yanıt: yalnız mevcut VERIFIED Evidence raporlandı; "
                "CAVEAT bölümleri tamamlanmamış USER_MUST çalışmalarını gösterir."
            )

        requested_report = any(
            item.capability_key == ManagerCapabilityKey.REPORT
            for item in presentation
        )
        return ResearchReportProjection(
            status=ResearchReportProjectionStatus.COMPLETE,
            request=ReportBuildRequest(
                title=(
                    "Araştırma Raporu — Kısmi"
                    if allow_partial
                    else (
                        "Araştırma Raporu"
                        if requested_report or sections
                        else "Araştırma Sonuçları"
                    )
                ),
                sections=tuple(sections),
                limitations=_unique(report_limitations),
            ),
            artifacts=artifacts,
            accounted_evidence_refs=tuple(sorted(accounted)),
            omitted_evidence_refs=(),
        )

    def _artifact(self, evidence: EvidenceArtifact) -> PresentationArtifact:
        kind = self._artifact_kind(evidence)
        shape = self._result_shape(evidence)
        render_spec = ReportRenderSpec(
            presentation_kind=kind,
            result_shape=shape,
        )
        return PresentationArtifact(
            artifact_id=_stable_id(
                "part_",
                {
                    "evidence_ref": evidence.artifact_id,
                    "kind": kind.value,
                    "query_contract_refs": evidence.query_contract_refs,
                },
            ),
            artifact_kind=kind,
            evidence_refs=(evidence.artifact_id,),
            render_spec=render_spec,
            result_shape=shape,
        )

    def _artifact_kind(self, evidence: EvidenceArtifact) -> ReportBlockKind:
        if evidence.evidence_kind == "relationship_analytics":
            return ReportBlockKind.COMPARISON
        if evidence.source_kind == "DERIVED_ANALYTICAL":
            if evidence.transformation in {"CONTRIBUTION", "PEER_COMPARE"}:
                return ReportBlockKind.COMPARISON
            return ReportBlockKind.TABLE

        executions = tuple(evidence.payload.get("executions") or ())
        if any(
            str(item.get("role") or "") == "comparison_reference"
            for item in executions
        ):
            return ReportBlockKind.COMPARISON
        if len(executions) == 1:
            rows = tuple(executions[0].get("rows") or ())
            columns = tuple(executions[0].get("columns") or ())
            if (
                len(rows) == 1
                and len(columns) == 1
                and isinstance(rows[0].get(columns[0]), (int, float))
                and not isinstance(rows[0].get(columns[0]), bool)
            ):
                return ReportBlockKind.KPI
        return ReportBlockKind.TABLE

    def _result_shape(self, evidence: EvidenceArtifact) -> ReportResultShape:
        handles = self._evidence_handles(evidence)
        row_count = 0
        if evidence.source_kind == "DERIVED_ANALYTICAL":
            if evidence.transformation == "TREND":
                row_count = int(evidence.payload.get("sample_count") or 0)
            elif evidence.transformation == "CONTRIBUTION":
                row_count = int(evidence.payload.get("segment_count") or 0)
            elif evidence.transformation == "PEER_COMPARE":
                row_count = 1
        else:
            row_count = sum(
                int(item.get("row_count") or 0)
                for item in tuple(evidence.payload.get("executions") or ())
            )

        return ReportResultShape(
            columns=tuple(
                ReportResultColumn(
                    name=self._handle_label(handle),
                    semantic_role=self._handle_kind(handle),
                )
                for handle in handles
            ),
            row_count=row_count,
            truncated=bool(evidence.limitations),
        )

    def _evidence_block(
        self,
        evidence: EvidenceArtifact,
        *,
        artifact: PresentationArtifact,
    ) -> ReportBlockSpec:
        kind = artifact.artifact_kind
        claim = (
            ReportClaimKind.NUMERIC
            if kind == ReportBlockKind.KPI
            else ReportClaimKind.ANALYTICAL
        )
        return ReportBlockSpec(
            block_kind=kind,
            claim_kind=claim,
            content=self._evidence_content(evidence),
            evidence_refs=(evidence.artifact_id,),
            artifact_ref=artifact.artifact_id,
            render_spec=artifact.render_spec,
            limitations=evidence.limitations,
        )

    def _evidence_content(self, evidence: EvidenceArtifact) -> str:
        if evidence.source_kind == "DERIVED_ANALYTICAL":
            if evidence.transformation == "TREND":
                trend = evidence.payload.get("trend") or {}
                metric = self._handle_label(str(evidence.payload.get("metric_handle") or ""))
                return (
                    f"{metric} trendi: yön={trend.get('yon')}, "
                    f"eğim={trend.get('egim')}, r2={trend.get('r2')}, "
                    f"n={trend.get('n')}."
                )
            if evidence.transformation == "CONTRIBUTION":
                metric = self._handle_label(str(evidence.payload.get("metric_handle") or ""))
                dimension = self._handle_label(str(evidence.payload.get("dimension_handle") or ""))
                return (
                    f"{metric} / {dimension} gözlenen değişim katkı ayrıştırması: "
                    f"{int(evidence.payload.get('segment_count') or 0)} segment."
                )
            if evidence.transformation == "PEER_COMPARE":
                metric = self._handle_label(str(evidence.payload.get("metric_handle") or ""))
                comparison = evidence.payload.get("comparison") or {}
                return (
                    f"{metric} akran karşılaştırması: "
                    f"hedef={comparison.get('hedef_deger')}, "
                    f"akran_ortalaması={comparison.get('akran_ortalamasi')}, "
                    f"fark={comparison.get('fark')}, "
                    f"fark_yüzde={comparison.get('fark_yuzde')}, "
                    f"akran_sayısı={comparison.get('akran_sayisi')}."
                )

        executions = tuple(evidence.payload.get("executions") or ())
        if artifact_kind := self._artifact_kind(evidence):
            if artifact_kind == ReportBlockKind.KPI and len(executions) == 1:
                execution = executions[0]
                columns = tuple(execution.get("columns") or ())
                rows = tuple(execution.get("rows") or ())
                if columns and rows:
                    label = self._handle_label(str(columns[0]))
                    return f"{label}: {rows[0].get(columns[0])}"

        labels = _unique(
            self._handle_label(str(handle))
            for execution in executions
            for handle in tuple(execution.get("columns") or ())
        )
        row_count = sum(
            int(execution.get("row_count") or 0)
            for execution in executions
        )
        prefix = (
            "Doğrulanmış ilişki analizi"
            if evidence.evidence_kind == "relationship_analytics"
            else (
                "Doğrulanmış karşılaştırma"
                if artifact_kind == ReportBlockKind.COMPARISON
                else "Doğrulanmış analitik sonuç"
            )
        )
        label_text = ", ".join(labels) if labels else "governed sonuç"
        return f"{prefix}: {label_text}; {row_count} sonuç satırı."

    def _evidence_handles(self, evidence: EvidenceArtifact) -> tuple[str, ...]:
        candidates: list[str] = []
        for execution in tuple(evidence.payload.get("executions") or ()):
            candidates.extend(str(x) for x in tuple(execution.get("columns") or ()))
        for key in ("metric_handle", "dimension_handle", "time_axis_handle"):
            value = evidence.payload.get(key)
            if isinstance(value, str):
                candidates.append(value)

        valid: list[str] = []
        for ref in _unique(candidates):
            try:
                self._handles.validate(
                    ref,
                    tenant_binding=self._tenant,
                    context_version=self._context,
                )
            except (KeyError, ValueError):
                continue
            valid.append(ref)
        return tuple(valid)

    def _handle_label(self, handle_id: str) -> str:
        binding = self._handles.binding_for_execution(
            handle_id,
            tenant_binding=self._tenant,
            context_version=self._context,
        )
        target = binding.canonical_target
        if isinstance(target, ResolvedSemanticRef):
            return target.canonical_name
        # This is server-governed typed metadata, never a string-derived guess.
        return binding.handle.target_kind

    def _handle_kind(self, handle_id: str) -> str:
        return self._handles.validate(
            handle_id,
            tenant_binding=self._tenant,
            context_version=self._context,
        ).target_kind
