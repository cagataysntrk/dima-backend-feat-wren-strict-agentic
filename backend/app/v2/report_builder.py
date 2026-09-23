"""Day9-A deterministic ReportDocument authority.

ReportBuilder is a pure projection over already-governed research truth. It never
executes analytics, resolves semantics, calls a model, or creates Evidence.

Authority split:
- EvidenceArtifact / EvidenceLinkedFinding / SemanticHandleRegistry remain truth owners.
- ReportDocument references those owners and carries presentation-only metadata.
- reference hydration / current-viewer permission checks stay outside this module.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Iterable, Mapping, Protocol

from pydantic import Field, model_validator

from app.v2.models import (
    EpistemicLabel,
    EvidenceArtifact,
    EvidenceLinkedFinding,
    FrozenModel,
)
from app.v2.semantic_handles import SemanticHandleRegistry


class ReportBuildStatus(StrEnum):
    COMPLETE = "COMPLETE"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
    REJECTED = "REJECTED"


class ReportIssueCode(StrEnum):
    EVIDENCE_REQUIRED = "EVIDENCE_REQUIRED"
    UNKNOWN_EVIDENCE = "UNKNOWN_EVIDENCE"
    UNVERIFIED_EVIDENCE = "UNVERIFIED_EVIDENCE"
    EVIDENCE_OUTSIDE_SOURCE_RUN = "EVIDENCE_OUTSIDE_SOURCE_RUN"
    EVIDENCE_LINEAGE_BROKEN = "EVIDENCE_LINEAGE_BROKEN"
    UNKNOWN_FINDING = "UNKNOWN_FINDING"
    FINDING_PROVENANCE_MISMATCH = "FINDING_PROVENANCE_MISMATCH"
    FINDING_EVIDENCE_REQUIRED = "FINDING_EVIDENCE_REQUIRED"
    FINDING_CLAIM_KIND_MISMATCH = "FINDING_CLAIM_KIND_MISMATCH"
    CONFIRMED_CAUSE_UNAVAILABLE = "CONFIRMED_CAUSE_UNAVAILABLE"
    INVALID_SEMANTIC_SCOPE = "INVALID_SEMANTIC_SCOPE"
    UNKNOWN_ARTIFACT = "UNKNOWN_ARTIFACT"
    ARTIFACT_KIND_MISMATCH = "ARTIFACT_KIND_MISMATCH"
    DUPLICATE_AUTHORITY_BLOCK = "DUPLICATE_AUTHORITY_BLOCK"
    DUPLICATE_AUTHORITY_SECTION = "DUPLICATE_AUTHORITY_SECTION"


class ReportBlockKind(StrEnum):
    TEXT = "TEXT"
    KPI = "KPI"
    TABLE = "TABLE"
    CHART = "CHART"
    COMPARISON = "COMPARISON"
    ROOT_CAUSE = "ROOT_CAUSE"
    CAVEAT = "CAVEAT"


class ReportClaimKind(StrEnum):
    NARRATIVE = "NARRATIVE"
    ANALYTICAL = "ANALYTICAL"
    NUMERIC = "NUMERIC"
    EPISTEMIC = "EPISTEMIC"
    LIMITATION = "LIMITATION"


class ReportAccessPolicy(StrEnum):
    CURRENT_RUN_ONLY_REAUTHORIZE_ON_REPLAY = (
        "CURRENT_RUN_ONLY_REAUTHORIZE_ON_REPLAY"
    )


class ReportResultColumn(FrozenModel):
    """Presentation-support metadata supplied by an existing governed result shape."""

    name: str = Field(min_length=1)
    data_type: str | None = None
    unit: str | None = None
    semantic_role: str | None = None


class ReportResultShape(FrozenModel):
    columns: tuple[ReportResultColumn, ...] = ()
    row_count: int = Field(default=0, ge=0)
    truncated: bool = False

    @model_validator(mode="after")
    def _unique_columns(self):
        names = [column.name for column in self.columns]
        if len(names) != len(set(names)):
            raise ValueError("result-shape column names must be unique")
        return self


class ReportRenderSpec(FrozenModel):
    """Presentation only. It cannot alter Evidence, semantics, or epistemic labels."""

    presentation_kind: ReportBlockKind
    result_shape: ReportResultShape | None = None
    options: tuple[tuple[str, str], ...] = ()

    @model_validator(mode="after")
    def _unique_options(self):
        keys = [key for key, _ in self.options]
        if len(keys) != len(set(keys)):
            raise ValueError("render option keys must be unique")
        return self


class ReportEvidenceRef(FrozenModel):
    evidence_ref: str = Field(min_length=1)
    query_contract_refs: tuple[str, ...] = Field(min_length=1)


class ReportFindingRef(FrozenModel):
    finding_ref: str = Field(min_length=1)


class ReportArtifactRef(FrozenModel):
    artifact_ref: str = Field(min_length=1)
    artifact_kind: ReportBlockKind


class ReportSourceProvenance(FrozenModel):
    accepted_contract_id: str = Field(min_length=1)
    lineage_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    tenant_binding: str = Field(min_length=1)
    context_version: str = Field(min_length=1)
    access_policy: ReportAccessPolicy = (
        ReportAccessPolicy.CURRENT_RUN_ONLY_REAUTHORIZE_ON_REPLAY
    )


class ReportBlockSpec(FrozenModel):
    """Server-internal composition input; contains no canonical Report identity."""

    block_kind: ReportBlockKind
    claim_kind: ReportClaimKind
    content: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()
    finding_refs: tuple[str, ...] = ()
    artifact_ref: str | None = None
    render_spec: ReportRenderSpec | None = None
    limitations: tuple[str, ...] = ()


class ReportSectionSpec(FrozenModel):
    title: str = Field(min_length=1)
    blocks: tuple[ReportBlockSpec, ...] = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()
    semantic_scope: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class ReportBuildRequest(FrozenModel):
    title: str = Field(min_length=1)
    sections: tuple[ReportSectionSpec, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = ()


class ReportBlock(FrozenModel):
    block_id: str = Field(pattern=r"^rblk_[a-f0-9]{24}$")
    block_kind: ReportBlockKind
    claim_kind: ReportClaimKind
    content: str = Field(min_length=1)
    evidence_refs: tuple[ReportEvidenceRef, ...] = ()
    finding_refs: tuple[ReportFindingRef, ...] = ()
    artifact_ref: ReportArtifactRef | None = None
    render_spec: ReportRenderSpec | None = None
    epistemic_label: EpistemicLabel | None = None
    hypothesis_ref: str | None = None
    limitations: tuple[str, ...] = ()


class ReportSection(FrozenModel):
    section_id: str = Field(pattern=r"^rsec_[a-f0-9]{24}$")
    title: str = Field(min_length=1)
    blocks: tuple[ReportBlock, ...] = Field(min_length=1)
    evidence_refs: tuple[ReportEvidenceRef, ...] = ()
    semantic_scope: tuple[str, ...] = ()
    followup_context_ref: str = Field(pattern=r"^rctx_[a-f0-9]{24}$")
    limitations: tuple[str, ...] = ()


class ReportDocument(FrozenModel):
    report_id: str = Field(pattern=r"^rpt_[a-f0-9]{24}$")
    title: str = Field(min_length=1)
    sections: tuple[ReportSection, ...] = Field(min_length=1)
    evidence_index: tuple[ReportEvidenceRef, ...] = ()
    limitations: tuple[str, ...] = ()
    provenance: ReportSourceProvenance


class ReportBuildIssue(FrozenModel):
    code: ReportIssueCode
    path: str = Field(min_length=1)
    ref: str | None = None
    reason: str = Field(min_length=1)


class ReportBuildResult(FrozenModel):
    status: ReportBuildStatus
    report: ReportDocument | None = None
    issues: tuple[ReportBuildIssue, ...] = ()

    @model_validator(mode="after")
    def _status_shape(self):
        if self.status == ReportBuildStatus.COMPLETE:
            if self.report is None or self.issues:
                raise ValueError("COMPLETE report result requires report and no issues")
        elif self.report is not None:
            raise ValueError("non-COMPLETE report result cannot carry a report")
        return self


class EvidenceLookup(Protocol):
    def get(self, artifact_id: str) -> EvidenceArtifact: ...


def _stable_id(prefix: str, payload: object) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _clean_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                value.strip()
                for value in values
                if isinstance(value, str) and value.strip()
            }
        )
    )


class ReportBuilder:
    """Pure deterministic projection over supplied governed authorities.

    The caller supplies already-authorized in-memory registries/views. This builder
    performs validation and composition only; it has no DB/Wren/LLM/resolver dependency.
    """

    def __init__(
        self,
        *,
        evidence_store: EvidenceLookup,
        current_evidence_refs: Iterable[str],
        findings: Iterable[EvidenceLinkedFinding],
        semantic_handles: SemanticHandleRegistry,
        known_artifacts: Mapping[str, ReportBlockKind] | None,
        provenance: ReportSourceProvenance,
    ) -> None:
        self._evidence_store = evidence_store
        self._current_evidence_refs = frozenset(current_evidence_refs)
        self._findings = {finding.finding_id: finding for finding in findings}
        self._semantic_handles = semantic_handles
        self._known_artifacts = dict(known_artifacts or {})
        self._provenance = provenance
        self._validated_evidence: dict[str, EvidenceArtifact] = {}

    def build(self, request: ReportBuildRequest) -> ReportBuildResult:
        issues: list[ReportBuildIssue] = []
        section_rows: list[ReportSection] = []

        for section_index, section in enumerate(request.sections):
            section_path = f"sections[{section_index}]"
            semantic_scope = _clean_unique(section.semantic_scope)
            self._validate_semantic_scope(
                semantic_scope,
                path=f"{section_path}.semantic_scope",
                issues=issues,
            )

            built_blocks: list[ReportBlock] = []
            for block_index, block in enumerate(section.blocks):
                built = self._build_block(
                    block,
                    path=f"{section_path}.blocks[{block_index}]",
                    issues=issues,
                )
                if built is not None:
                    built_blocks.append(built)

            explicit_section_evidence = _clean_unique(section.evidence_refs)
            for ref in explicit_section_evidence:
                self._require_evidence(
                    ref,
                    path=f"{section_path}.evidence_refs",
                    issues=issues,
                )

            if issues:
                continue

            block_ids = [block.block_id for block in built_blocks]
            if len(block_ids) != len(set(block_ids)):
                issues.append(
                    ReportBuildIssue(
                        code=ReportIssueCode.DUPLICATE_AUTHORITY_BLOCK,
                        path=f"{section_path}.blocks",
                        reason=(
                            "two report blocks have the same authoritative identity; "
                            "presentation text cannot disambiguate authority"
                        ),
                    )
                )
                continue

            built_blocks.sort(key=lambda item: item.block_id)
            evidence_ids = _clean_unique(
                (
                    *explicit_section_evidence,
                    *(
                        ref.evidence_ref
                        for block in built_blocks
                        for ref in block.evidence_refs
                    ),
                )
            )
            evidence_refs = tuple(
                self._evidence_ref(ref)
                for ref in evidence_ids
            )
            limitations = _clean_unique(
                (
                    *section.limitations,
                    *(limitation for block in built_blocks for limitation in block.limitations),
                )
            )

            section_authority = {
                "provenance": self._authority_provenance(),
                "semantic_scope": semantic_scope,
                "evidence_refs": evidence_ids,
                "block_ids": [block.block_id for block in built_blocks],
            }
            section_id = _stable_id("rsec_", section_authority)
            followup_context_ref = _stable_id(
                "rctx_",
                {
                    "run_id": self._provenance.run_id,
                    "section_id": section_id,
                    "semantic_scope": semantic_scope,
                    "evidence_refs": evidence_ids,
                },
            )
            section_rows.append(
                ReportSection(
                    section_id=section_id,
                    title=section.title.strip(),
                    blocks=tuple(built_blocks),
                    evidence_refs=evidence_refs,
                    semantic_scope=semantic_scope,
                    followup_context_ref=followup_context_ref,
                    limitations=limitations,
                )
            )

        if issues:
            status = (
                ReportBuildStatus.NEEDS_EVIDENCE
                if all(
                    issue.code
                    in {
                        ReportIssueCode.EVIDENCE_REQUIRED,
                        ReportIssueCode.UNKNOWN_EVIDENCE,
                        ReportIssueCode.UNVERIFIED_EVIDENCE,
                        ReportIssueCode.EVIDENCE_OUTSIDE_SOURCE_RUN,
                        ReportIssueCode.EVIDENCE_LINEAGE_BROKEN,
                        ReportIssueCode.FINDING_EVIDENCE_REQUIRED,
                    }
                    for issue in issues
                )
                else ReportBuildStatus.REJECTED
            )
            return ReportBuildResult(
                status=status,
                issues=tuple(issues),
            )

        section_ids = [section.section_id for section in section_rows]
        if len(section_ids) != len(set(section_ids)):
            return ReportBuildResult(
                status=ReportBuildStatus.REJECTED,
                issues=(
                    ReportBuildIssue(
                        code=ReportIssueCode.DUPLICATE_AUTHORITY_SECTION,
                        path="sections",
                        reason=(
                            "two report sections have the same authoritative identity; "
                            "title/order cannot create a second semantic section"
                        ),
                    ),
                ),
            )

        section_rows.sort(key=lambda item: item.section_id)
        evidence_ids = _clean_unique(
            ref.evidence_ref
            for section in section_rows
            for ref in section.evidence_refs
        )
        evidence_index = tuple(self._evidence_ref(ref) for ref in evidence_ids)
        limitations = _clean_unique(
            (
                *request.limitations,
                *(limitation for section in section_rows for limitation in section.limitations),
            )
        )
        report_id = _stable_id(
            "rpt_",
            {
                "provenance": self._authority_provenance(),
                "section_ids": [section.section_id for section in section_rows],
                "evidence_refs": evidence_ids,
            },
        )
        return ReportBuildResult(
            status=ReportBuildStatus.COMPLETE,
            report=ReportDocument(
                report_id=report_id,
                title=request.title.strip(),
                sections=tuple(section_rows),
                evidence_index=evidence_index,
                limitations=limitations,
                provenance=self._provenance,
            ),
        )

    def _build_block(
        self,
        block: ReportBlockSpec,
        *,
        path: str,
        issues: list[ReportBuildIssue],
    ) -> ReportBlock | None:
        evidence_ids = list(_clean_unique(block.evidence_refs))
        finding_ids = _clean_unique(block.finding_refs)
        finding = None

        if block.claim_kind in {
            ReportClaimKind.NUMERIC,
            ReportClaimKind.ANALYTICAL,
        } and not evidence_ids:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.EVIDENCE_REQUIRED,
                    path=f"{path}.evidence_refs",
                    reason=(
                        f"{block.claim_kind.value} report claims require governed EvidenceRef"
                    ),
                )
            )

        if finding_ids and block.claim_kind != ReportClaimKind.EPISTEMIC:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.FINDING_CLAIM_KIND_MISMATCH,
                    path=f"{path}.finding_refs",
                    reason=(
                        "FindingRef may appear only on EPISTEMIC blocks so the canonical "
                        "finding label/limitations cannot be laundered into another claim class"
                    ),
                )
            )

        if block.claim_kind == ReportClaimKind.EPISTEMIC:
            if len(finding_ids) != 1:
                issues.append(
                    ReportBuildIssue(
                        code=ReportIssueCode.FINDING_EVIDENCE_REQUIRED,
                        path=f"{path}.finding_refs",
                        reason="EPISTEMIC report block requires exactly one canonical FindingRef",
                    )
                )
            else:
                finding = self._validate_finding(
                    finding_ids[0],
                    path=f"{path}.finding_refs",
                    issues=issues,
                )
                if finding is not None:
                    evidence_ids.extend(finding.evidence_refs)

        for ref in _clean_unique(evidence_ids):
            self._require_evidence(
                ref,
                path=f"{path}.evidence_refs",
                issues=issues,
            )

        artifact = self._validate_artifact(
            block,
            path=path,
            issues=issues,
        )

        if issues:
            return None

        evidence_ids_tuple = _clean_unique(evidence_ids)
        evidence_refs = tuple(
            self._evidence_ref(ref)
            for ref in evidence_ids_tuple
        )
        limitations = _clean_unique(
            (
                *block.limitations,
                *(finding.limitations if finding is not None else ()),
            )
        )
        authority = {
            "block_kind": block.block_kind.value,
            "claim_kind": block.claim_kind.value,
            "evidence_refs": evidence_ids_tuple,
            "finding_refs": finding_ids,
            "artifact_ref": None if artifact is None else artifact.artifact_ref,
            "epistemic_label": (
                None if finding is None else finding.epistemic_label.value
            ),
            "hypothesis_ref": None if finding is None else finding.hypothesis_ref,
        }
        return ReportBlock(
            block_id=_stable_id("rblk_", authority),
            block_kind=block.block_kind,
            claim_kind=block.claim_kind,
            content=block.content.strip(),
            evidence_refs=evidence_refs,
            finding_refs=tuple(
                ReportFindingRef(finding_ref=ref)
                for ref in finding_ids
            ),
            artifact_ref=artifact,
            render_spec=block.render_spec,
            epistemic_label=None if finding is None else finding.epistemic_label,
            hypothesis_ref=None if finding is None else finding.hypothesis_ref,
            limitations=limitations,
        )

    def _validate_finding(
        self,
        finding_ref: str,
        *,
        path: str,
        issues: list[ReportBuildIssue],
    ) -> EvidenceLinkedFinding | None:
        finding = self._findings.get(finding_ref)
        if finding is None:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.UNKNOWN_FINDING,
                    path=path,
                    ref=finding_ref,
                    reason="FindingRef does not resolve to a supplied canonical finding",
                )
            )
            return None

        provenance = finding.provenance
        if (
            provenance.accepted_contract_id != self._provenance.accepted_contract_id
            or provenance.lineage_id != self._provenance.lineage_id
            or provenance.run_id != self._provenance.run_id
        ):
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.FINDING_PROVENANCE_MISMATCH,
                    path=path,
                    ref=finding_ref,
                    reason="FindingRef belongs to a different accepted/run lineage",
                )
            )
            return None

        if finding.epistemic_label == EpistemicLabel.CONFIRMED_CAUSE:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.CONFIRMED_CAUSE_UNAVAILABLE,
                    path=path,
                    ref=finding_ref,
                    reason="Day9 cannot strengthen or surface unavailable CONFIRMED_CAUSE",
                )
            )
            return None

        before = len(issues)
        for evidence_ref in finding.evidence_refs:
            self._require_evidence(
                evidence_ref,
                path=f"{path}.{finding_ref}.evidence_refs",
                issues=issues,
            )
        if len(issues) != before:
            return None
        return finding

    def _require_evidence(
        self,
        evidence_ref: str,
        *,
        path: str,
        issues: list[ReportBuildIssue],
        _visiting: frozenset[str] = frozenset(),
    ) -> EvidenceArtifact | None:
        if evidence_ref in self._validated_evidence:
            return self._validated_evidence[evidence_ref]

        if evidence_ref in _visiting:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.EVIDENCE_LINEAGE_BROKEN,
                    path=path,
                    ref=evidence_ref,
                    reason="Evidence lineage contains a cycle",
                )
            )
            return None

        if evidence_ref not in self._current_evidence_refs:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.EVIDENCE_OUTSIDE_SOURCE_RUN,
                    path=path,
                    ref=evidence_ref,
                    reason="EvidenceRef is not in the current report source run",
                )
            )
            return None

        try:
            evidence = self._evidence_store.get(evidence_ref)
        except Exception:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.UNKNOWN_EVIDENCE,
                    path=path,
                    ref=evidence_ref,
                    reason="EvidenceRef does not resolve in the supplied Evidence authority",
                )
            )
            return None

        if not evidence.verified:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.UNVERIFIED_EVIDENCE,
                    path=path,
                    ref=evidence_ref,
                    reason="Report claims may reference VERIFIED Evidence only",
                )
            )
            return None

        if not evidence.query_contract_refs:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.EVIDENCE_LINEAGE_BROKEN,
                    path=path,
                    ref=evidence_ref,
                    reason="EvidenceRef has no QueryContract provenance",
                )
            )
            return None

        if evidence.source_kind == "DERIVED_ANALYTICAL":
            before_lineage = len(issues)
            next_visiting = frozenset((*_visiting, evidence_ref))
            for parent_ref in evidence.parent_evidence_refs:
                self._require_evidence(
                    parent_ref,
                    path=f"{path}.{evidence_ref}.parent_evidence_refs",
                    issues=issues,
                    _visiting=next_visiting,
                )
            if any(
                parent_qc not in evidence.query_contract_refs
                for parent_qc in evidence.parent_query_contract_refs
            ):
                issues.append(
                    ReportBuildIssue(
                        code=ReportIssueCode.EVIDENCE_LINEAGE_BROKEN,
                        path=path,
                        ref=evidence_ref,
                        reason=(
                            "derived Evidence does not preserve parent QueryContract lineage"
                        ),
                    )
                )
            if len(issues) != before_lineage:
                return None
        if any(issue.ref == evidence_ref for issue in issues):
            return None

        self._validated_evidence[evidence_ref] = evidence
        return evidence

    def _validate_semantic_scope(
        self,
        refs: tuple[str, ...],
        *,
        path: str,
        issues: list[ReportBuildIssue],
    ) -> None:
        for ref in refs:
            try:
                self._semantic_handles.validate(
                    ref,
                    tenant_binding=self._provenance.tenant_binding,
                    context_version=self._provenance.context_version,
                )
            except (KeyError, ValueError) as exc:
                issues.append(
                    ReportBuildIssue(
                        code=ReportIssueCode.INVALID_SEMANTIC_SCOPE,
                        path=path,
                        ref=ref,
                        reason=f"semantic scope must use existing governed handles: {exc}",
                    )
                )

    def _validate_artifact(
        self,
        block: ReportBlockSpec,
        *,
        path: str,
        issues: list[ReportBuildIssue],
    ) -> ReportArtifactRef | None:
        if block.artifact_ref is None:
            return None

        artifact_kind = self._known_artifacts.get(block.artifact_ref)
        if artifact_kind is None:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.UNKNOWN_ARTIFACT,
                    path=f"{path}.artifact_ref",
                    ref=block.artifact_ref,
                    reason="ArtifactRef is not present in the supplied presentation registry",
                )
            )
            return None

        if artifact_kind != block.block_kind:
            issues.append(
                ReportBuildIssue(
                    code=ReportIssueCode.ARTIFACT_KIND_MISMATCH,
                    path=f"{path}.artifact_ref",
                    ref=block.artifact_ref,
                    reason=(
                        f"artifact kind {artifact_kind.value} cannot back "
                        f"{block.block_kind.value} report block"
                    ),
                )
            )
            return None

        return ReportArtifactRef(
            artifact_ref=block.artifact_ref,
            artifact_kind=artifact_kind,
        )

    def _evidence_ref(self, evidence_ref: str) -> ReportEvidenceRef:
        evidence = self._validated_evidence[evidence_ref]
        return ReportEvidenceRef(
            evidence_ref=evidence.artifact_id,
            query_contract_refs=_clean_unique(evidence.query_contract_refs),
        )

    def _authority_provenance(self) -> dict[str, str]:
        return {
            "accepted_contract_id": self._provenance.accepted_contract_id,
            "lineage_id": self._provenance.lineage_id,
            "run_id": self._provenance.run_id,
            "tenant_binding": self._provenance.tenant_binding,
            "context_version": self._provenance.context_version,
        }
