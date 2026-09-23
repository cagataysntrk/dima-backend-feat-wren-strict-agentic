"""Day9-B bounded narration over immutable Day9-A ReportDocument authority.

The model is a presentation planner, never a fact writer. It receives only a narrow
presentation-safe projection and may select/order existing canonical report IDs.
Analytical truth remains exclusively in the frozen ReportDocument and its referenced
Evidence/Finding authorities.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field

from app.v2.models import EpistemicLabel, FrozenModel
from app.v2.report_builder import (
    ReportBlock,
    ReportBlockKind,
    ReportClaimKind,
    ReportDocument,
    ReportSection,
)


NARRATION_CONTRACT_VERSION = "d9b-narration-plan-v1"
NARRATION_SCHEMA_NAME = "dima_report_narration_plan"


class NarrationPlanError(RuntimeError):
    pass


class NarrationPlanCode(StrEnum):
    REPORT_REF_MISMATCH = "REPORT_REF_MISMATCH"
    SECTION_COVERAGE_MISMATCH = "SECTION_COVERAGE_MISMATCH"
    UNKNOWN_SECTION_REF = "UNKNOWN_SECTION_REF"
    DUPLICATE_SECTION_REF = "DUPLICATE_SECTION_REF"
    UNKNOWN_BLOCK_REF = "UNKNOWN_BLOCK_REF"
    FOREIGN_SECTION_BLOCK_REF = "FOREIGN_SECTION_BLOCK_REF"
    DUPLICATE_BLOCK_REF = "DUPLICATE_BLOCK_REF"
    BLOCK_PERMUTATION_REQUIRED = "BLOCK_PERMUTATION_REQUIRED"
    EXECUTIVE_LIMIT_EXCEEDED = "EXECUTIVE_LIMIT_EXCEEDED"


class NarrationProviderStatus(StrEnum):
    VALIDATED = "VALIDATED"
    FALLBACK_PROVIDER_FAILURE = "FALLBACK_PROVIDER_FAILURE"
    FALLBACK_SCHEMA_FAILURE = "FALLBACK_SCHEMA_FAILURE"
    FALLBACK_PLAN_FAILURE = "FALLBACK_PLAN_FAILURE"


class NarrationPacketBlock(FrozenModel):
    block_ref: str = Field(pattern=r"^rblk_[a-f0-9]{24}$")
    block_kind: ReportBlockKind
    claim_kind: ReportClaimKind
    content: str = Field(min_length=1)
    epistemic_label: EpistemicLabel | None = None
    has_artifact: bool
    artifact_kind: ReportBlockKind | None = None
    limitations: tuple[str, ...] = ()


class NarrationPacketSection(FrozenModel):
    section_ref: str = Field(pattern=r"^rsec_[a-f0-9]{24}$")
    title: str = Field(min_length=1)
    blocks: tuple[NarrationPacketBlock, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = ()


class NarrationPacket(FrozenModel):
    """Minimum presentation-safe context sent to probabilistic cognition."""

    report_ref: str = Field(pattern=r"^rpt_[a-f0-9]{24}$")
    sections: tuple[NarrationPacketSection, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = ()

    @classmethod
    def from_report(cls, report: ReportDocument) -> "NarrationPacket":
        return cls(
            report_ref=report.report_id,
            sections=tuple(
                NarrationPacketSection(
                    section_ref=section.section_id,
                    title=section.title,
                    blocks=tuple(
                        NarrationPacketBlock(
                            block_ref=block.block_id,
                            block_kind=block.block_kind,
                            claim_kind=block.claim_kind,
                            content=block.content,
                            epistemic_label=block.epistemic_label,
                            has_artifact=block.artifact_ref is not None,
                            artifact_kind=(
                                None
                                if block.artifact_ref is None
                                else block.artifact_ref.artifact_kind
                            ),
                            limitations=block.limitations,
                        )
                        for block in section.blocks
                    ),
                    limitations=section.limitations,
                )
                for section in report.sections
            ),
            limitations=report.limitations,
        )


class SectionNarrationPlanProposal(FrozenModel):
    section_ref: str = Field(pattern=r"^rsec_[a-f0-9]{24}$")
    ordered_block_refs: tuple[str, ...] = Field(min_length=1)
    emphasis_block_refs: tuple[str, ...] = ()


class NarrationPlanProposal(FrozenModel):
    """Probabilistic output: canonical-reference selection/order only, no prose."""

    report_ref: str = Field(pattern=r"^rpt_[a-f0-9]{24}$")
    executive_highlight_block_refs: tuple[str, ...] = Field(
        default=(),
        max_length=3,
    )
    section_plans: tuple[SectionNarrationPlanProposal, ...] = Field(min_length=1)


class NarrationSectionPresentation(FrozenModel):
    section_ref: str = Field(pattern=r"^rsec_[a-f0-9]{24}$")
    ordered_block_refs: tuple[str, ...] = Field(min_length=1)
    emphasis_block_refs: tuple[str, ...] = ()


class ValidatedNarrationPlan(FrozenModel):
    report_ref: str = Field(pattern=r"^rpt_[a-f0-9]{24}$")
    executive_highlight_block_refs: tuple[str, ...] = ()
    section_presentations: tuple[NarrationSectionPresentation, ...] = Field(min_length=1)


class NarrationProviderReceipt(FrozenModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    call_count: Literal[1] = 1
    status: NarrationProviderStatus
    contract_version: str = NARRATION_CONTRACT_VERSION


class ReportNarrationOverlay(FrozenModel):
    """Presentation-only server object. It owns no analytical identity."""

    overlay_id: str = Field(pattern=r"^rnov_[a-f0-9]{24}$")
    report_ref: str = Field(pattern=r"^rpt_[a-f0-9]{24}$")
    executive_highlight_refs: tuple[str, ...] = ()
    section_presentations: tuple[NarrationSectionPresentation, ...] = Field(min_length=1)
    provider_receipt: NarrationProviderReceipt
    contract_version: str = NARRATION_CONTRACT_VERSION


class RenderedNarrationBlock(FrozenModel):
    block_ref: str = Field(pattern=r"^rblk_[a-f0-9]{24}$")
    block_kind: ReportBlockKind
    claim_kind: ReportClaimKind
    content: str = Field(min_length=1)
    emphasized: bool = False
    epistemic_label: EpistemicLabel | None = None
    epistemic_display_label: str | None = None
    artifact_ref: str | None = None
    artifact_kind: ReportBlockKind | None = None
    limitations: tuple[str, ...] = ()


class RenderedNarrationSection(FrozenModel):
    section_ref: str = Field(pattern=r"^rsec_[a-f0-9]{24}$")
    title: str = Field(min_length=1)
    blocks: tuple[RenderedNarrationBlock, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = ()


class RenderedReportNarration(FrozenModel):
    report_ref: str = Field(pattern=r"^rpt_[a-f0-9]{24}$")
    overlay_ref: str = Field(pattern=r"^rnov_[a-f0-9]{24}$")
    executive_summary: tuple[RenderedNarrationBlock, ...] = ()
    sections: tuple[RenderedNarrationSection, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = ()


def _stable_id(prefix: str, payload: object) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _duplicates(values: tuple[str, ...]) -> bool:
    return len(values) != len(set(values))


def _report_indexes(
    report: ReportDocument,
) -> tuple[dict[str, ReportSection], dict[str, ReportBlock], dict[str, str]]:
    sections = {section.section_id: section for section in report.sections}
    blocks: dict[str, ReportBlock] = {}
    block_sections: dict[str, str] = {}
    for section in report.sections:
        for block in section.blocks:
            blocks[block.block_id] = block
            block_sections[block.block_id] = section.section_id
    return sections, blocks, block_sections


class NarrationPlanGate:
    """The only admission owner for probabilistic narration plans."""

    def admit(
        self,
        *,
        report: ReportDocument,
        proposal: NarrationPlanProposal,
    ) -> ValidatedNarrationPlan:
        if proposal.report_ref != report.report_id:
            self._deny(
                NarrationPlanCode.REPORT_REF_MISMATCH,
                "proposal report_ref does not match canonical ReportDocument",
            )

        sections, blocks, block_sections = _report_indexes(report)
        canonical_section_ids = tuple(section.section_id for section in report.sections)
        proposal_section_ids = tuple(plan.section_ref for plan in proposal.section_plans)

        if _duplicates(proposal_section_ids):
            self._deny(
                NarrationPlanCode.DUPLICATE_SECTION_REF,
                "each canonical report section must have exactly one narration plan",
            )
        unknown_sections = set(proposal_section_ids) - set(canonical_section_ids)
        if unknown_sections:
            self._deny(
                NarrationPlanCode.UNKNOWN_SECTION_REF,
                "narration plan references section outside canonical report",
            )
        if set(proposal_section_ids) != set(canonical_section_ids):
            self._deny(
                NarrationPlanCode.SECTION_COVERAGE_MISMATCH,
                "narration plan must cover every canonical report section exactly once",
            )

        executive = proposal.executive_highlight_block_refs
        if len(executive) > 3:
            self._deny(
                NarrationPlanCode.EXECUTIVE_LIMIT_EXCEEDED,
                "executive highlights may contain at most three canonical blocks",
            )
        if _duplicates(executive):
            self._deny(
                NarrationPlanCode.DUPLICATE_BLOCK_REF,
                "executive highlight refs must be unique",
            )
        if any(ref not in blocks for ref in executive):
            self._deny(
                NarrationPlanCode.UNKNOWN_BLOCK_REF,
                "executive highlights contain block outside canonical report",
            )

        proposed_by_section = {plan.section_ref: plan for plan in proposal.section_plans}
        validated_sections: list[NarrationSectionPresentation] = []
        for canonical_section in report.sections:
            plan = proposed_by_section[canonical_section.section_id]
            canonical_blocks = tuple(block.block_id for block in canonical_section.blocks)
            ordered = plan.ordered_block_refs
            emphasis = plan.emphasis_block_refs

            if _duplicates(ordered) or _duplicates(emphasis):
                self._deny(
                    NarrationPlanCode.DUPLICATE_BLOCK_REF,
                    "ordered/emphasis block refs must be unique",
                )
            if any(ref not in blocks for ref in (*ordered, *emphasis)):
                self._deny(
                    NarrationPlanCode.UNKNOWN_BLOCK_REF,
                    "narration section contains block outside canonical report",
                )
            if any(
                block_sections[ref] != canonical_section.section_id
                for ref in (*ordered, *emphasis)
            ):
                self._deny(
                    NarrationPlanCode.FOREIGN_SECTION_BLOCK_REF,
                    "section narration cannot import a block from another section",
                )
            if len(ordered) != len(canonical_blocks) or set(ordered) != set(canonical_blocks):
                self._deny(
                    NarrationPlanCode.BLOCK_PERMUTATION_REQUIRED,
                    "ordered_block_refs must be an exact permutation of canonical section blocks",
                )
            if not set(emphasis).issubset(set(canonical_blocks)):
                self._deny(
                    NarrationPlanCode.FOREIGN_SECTION_BLOCK_REF,
                    "emphasis refs must belong to the canonical section",
                )

            validated_sections.append(
                NarrationSectionPresentation(
                    section_ref=canonical_section.section_id,
                    ordered_block_refs=ordered,
                    emphasis_block_refs=tuple(sorted(emphasis)),
                )
            )

        return ValidatedNarrationPlan(
            report_ref=report.report_id,
            executive_highlight_block_refs=executive,
            section_presentations=tuple(validated_sections),
        )

    @staticmethod
    def _deny(code: NarrationPlanCode, reason: str) -> None:
        raise NarrationPlanError(f"{code.value}: {reason}")


def build_overlay(
    *,
    report: ReportDocument,
    plan: ValidatedNarrationPlan,
    receipt: NarrationProviderReceipt,
) -> ReportNarrationOverlay:
    if plan.report_ref != report.report_id:
        raise NarrationPlanError(
            f"{NarrationPlanCode.REPORT_REF_MISMATCH.value}: validated plan/report mismatch"
        )

    identity = {
        "report_ref": report.report_id,
        "executive_highlight_refs": plan.executive_highlight_block_refs,
        "section_presentations": [
            {
                "section_ref": item.section_ref,
                "ordered_block_refs": item.ordered_block_refs,
                "emphasis_block_refs": item.emphasis_block_refs,
            }
            for item in plan.section_presentations
        ],
        "contract_version": NARRATION_CONTRACT_VERSION,
    }
    return ReportNarrationOverlay(
        overlay_id=_stable_id("rnov_", identity),
        report_ref=report.report_id,
        executive_highlight_refs=plan.executive_highlight_block_refs,
        section_presentations=plan.section_presentations,
        provider_receipt=receipt,
    )


def deterministic_fallback_plan(report: ReportDocument) -> ValidatedNarrationPlan:
    """Safe presentation if probabilistic planning fails; no analytical fallback."""

    first_blocks = tuple(
        block.block_id
        for section in report.sections
        for block in section.blocks
    )[:3]
    return ValidatedNarrationPlan(
        report_ref=report.report_id,
        executive_highlight_block_refs=first_blocks,
        section_presentations=tuple(
            NarrationSectionPresentation(
                section_ref=section.section_id,
                ordered_block_refs=tuple(block.block_id for block in section.blocks),
                emphasis_block_refs=(),
            )
            for section in report.sections
        ),
    )


class ReportNarrator:
    """Exactly-one-call narration planner with deterministic fallback.

    structured_json is the only provider surface used. No tool registry/executor is
    accepted by this class, so narration cannot expand its own authority.
    """

    def __init__(
        self,
        *,
        llm: Any,
        provider: str,
        model: str,
        gate: NarrationPlanGate | None = None,
    ) -> None:
        self._llm = llm
        self._provider = provider
        self._model = model
        self._gate = gate or NarrationPlanGate()

    def compose(self, report: ReportDocument) -> ReportNarrationOverlay:
        packet = NarrationPacket.from_report(report)
        try:
            raw = self._llm.structured_json(
                _NARRATION_SYSTEM,
                json.dumps(
                    packet.model_dump(mode="json"),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                schema=NarrationPlanProposal.model_json_schema(),
                schema_name=NARRATION_SCHEMA_NAME,
            )
        except Exception:
            return self._fallback(
                report,
                status=NarrationProviderStatus.FALLBACK_PROVIDER_FAILURE,
            )

        try:
            proposal = (
                NarrationPlanProposal.model_validate_json(raw)
                if isinstance(raw, str)
                else NarrationPlanProposal.model_validate(raw)
            )
        except Exception:
            return self._fallback(
                report,
                status=NarrationProviderStatus.FALLBACK_SCHEMA_FAILURE,
            )

        try:
            plan = self._gate.admit(report=report, proposal=proposal)
        except NarrationPlanError:
            return self._fallback(
                report,
                status=NarrationProviderStatus.FALLBACK_PLAN_FAILURE,
            )

        return build_overlay(
            report=report,
            plan=plan,
            receipt=self._receipt(NarrationProviderStatus.VALIDATED),
        )

    def _fallback(
        self,
        report: ReportDocument,
        *,
        status: NarrationProviderStatus,
    ) -> ReportNarrationOverlay:
        return build_overlay(
            report=report,
            plan=deterministic_fallback_plan(report),
            receipt=self._receipt(status),
        )

    def _receipt(self, status: NarrationProviderStatus) -> NarrationProviderReceipt:
        return NarrationProviderReceipt(
            provider=self._provider,
            model=self._model,
            status=status,
        )


class ReportNarrationRenderer:
    """Deterministic renderer: canonical text in, canonical text out."""

    def render(
        self,
        *,
        report: ReportDocument,
        overlay: ReportNarrationOverlay,
    ) -> RenderedReportNarration:
        if overlay.report_ref != report.report_id:
            raise NarrationPlanError(
                f"{NarrationPlanCode.REPORT_REF_MISMATCH.value}: overlay/report mismatch"
            )

        sections, blocks, block_sections = _report_indexes(report)
        section_plans = {
            item.section_ref: item
            for item in overlay.section_presentations
        }
        if set(section_plans) != set(sections):
            raise NarrationPlanError(
                f"{NarrationPlanCode.SECTION_COVERAGE_MISMATCH.value}: overlay section mismatch"
            )

        executive = tuple(
            self._render_block(blocks[ref], emphasized=True)
            for ref in overlay.executive_highlight_refs
            if ref in blocks
        )
        if len(executive) != len(overlay.executive_highlight_refs):
            raise NarrationPlanError(
                f"{NarrationPlanCode.UNKNOWN_BLOCK_REF.value}: overlay executive ref missing"
            )

        rendered_sections: list[RenderedNarrationSection] = []
        for section in report.sections:
            plan = section_plans[section.section_id]
            canonical = tuple(block.block_id for block in section.blocks)
            if (
                len(plan.ordered_block_refs) != len(canonical)
                or set(plan.ordered_block_refs) != set(canonical)
                or any(
                    block_sections.get(ref) != section.section_id
                    for ref in (*plan.ordered_block_refs, *plan.emphasis_block_refs)
                )
            ):
                raise NarrationPlanError(
                    f"{NarrationPlanCode.BLOCK_PERMUTATION_REQUIRED.value}: "
                    "overlay cannot mutate canonical section membership"
                )
            emphasis = set(plan.emphasis_block_refs)
            rendered_sections.append(
                RenderedNarrationSection(
                    section_ref=section.section_id,
                    title=section.title,
                    blocks=tuple(
                        self._render_block(
                            blocks[ref],
                            emphasized=ref in emphasis,
                        )
                        for ref in plan.ordered_block_refs
                    ),
                    limitations=section.limitations,
                )
            )

        return RenderedReportNarration(
            report_ref=report.report_id,
            overlay_ref=overlay.overlay_id,
            executive_summary=executive,
            sections=tuple(rendered_sections),
            limitations=report.limitations,
        )

    @staticmethod
    def _render_block(
        block: ReportBlock,
        *,
        emphasized: bool,
    ) -> RenderedNarrationBlock:
        display_label = None
        if block.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE:
            display_label = "Aday neden"
        elif block.epistemic_label is not None:
            display_label = block.epistemic_label.value

        return RenderedNarrationBlock(
            block_ref=block.block_id,
            block_kind=block.block_kind,
            claim_kind=block.claim_kind,
            content=block.content,
            emphasized=emphasized,
            epistemic_label=block.epistemic_label,
            epistemic_display_label=display_label,
            artifact_ref=(
                None if block.artifact_ref is None else block.artifact_ref.artifact_ref
            ),
            artifact_kind=(
                None if block.artifact_ref is None else block.artifact_ref.artifact_kind
            ),
            limitations=block.limitations,
        )


_NARRATION_SYSTEM = """You are Dima's bounded report presentation planner.

Return only the native JSON-schema object requested by the caller.

You may ONLY:
- echo the supplied report_ref,
- include exactly one plan for every supplied section_ref,
- reorder each section's existing block_ref values as an exact permutation,
- select emphasis_block_refs from blocks already in that same section,
- select at most three executive_highlight_block_refs from existing report blocks.

You must NOT write or rewrite any factual prose, number, explanation, cause, recommendation,
semantic interpretation, Evidence reference, Finding reference, artifact identity, or new ID.
The canonical ReportDocument already owns all report truth. Your job is presentation ordering only.
"""
