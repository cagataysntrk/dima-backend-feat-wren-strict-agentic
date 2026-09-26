"""One paid Day9-B live Sol sentinel for bounded ReportDocument narration.

This test does not execute analytics. The canonical ReportDocument already exists.
The only live uncertainty is whether Sol can select/order existing report IDs through
one strict structured call without inventing analytical truth or authority.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

LIVE_MODEL = "openai/gpt-5.6-sol"
MAX_MODEL_CALLS = 1

os.environ.setdefault("DIMA_LLM_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_RESEARCH_MANAGER_PROVIDER", "openrouter")
os.environ["DIMA_V2_RESEARCH_MANAGER_MODEL"] = LIVE_MODEL
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")

from app.config import get_settings
from app.llm import build_generator
from app.v2.model_policy import ModelRole, ModelRolePolicy
from app.v2.models import EpistemicLabel
from app.v2.report_builder import (
    ReportAccessPolicy,
    ReportArtifactRef,
    ReportBlock,
    ReportBlockKind,
    ReportClaimKind,
    ReportDocument,
    ReportEvidenceRef,
    ReportFindingRef,
    ReportRenderSpec,
    ReportSection,
    ReportSourceProvenance,
)
from app.v2.report_narration import (
    NarrationProviderStatus,
    ReportNarrationRenderer,
    ReportNarrator,
)


RPT = "rpt_" + "1" * 24
SEC1 = "rsec_" + "2" * 24
SEC2 = "rsec_" + "3" * 24
CTX1 = "rctx_" + "8" * 24
CTX2 = "rctx_" + "9" * 24
B1 = "rblk_" + "4" * 24
B2 = "rblk_" + "5" * 24
B3 = "rblk_" + "6" * 24
B4 = "rblk_" + "7" * 24


class LiveBudgetExceeded(RuntimeError):
    pass


class LiveBehaviorFailure(RuntimeError):
    pass


class CountingLLM:
    def __init__(self, inner) -> None:
        self._inner = inner
        self.calls = 0

    def structured_json(self, *args, **kwargs):
        if self.calls >= MAX_MODEL_CALLS:
            raise LiveBudgetExceeded("Day9-B live narration call ceiling exhausted")
        self.calls += 1
        return self._inner.structured_json(*args, **kwargs)


def _eref(ref: str, qc: str) -> ReportEvidenceRef:
    return ReportEvidenceRef(evidence_ref=ref, query_contract_refs=(qc,))


def build_fixture() -> ReportDocument:
    """Canonical in-memory report; no Evidence lookup, DB, Wren or Research call."""

    numeric = ReportBlock(
        block_id=B1,
        block_kind=ReportBlockKind.KPI,
        claim_kind=ReportClaimKind.NUMERIC,
        content="Net gelir 100 birimdir.",
        evidence_refs=(_eref("E_NUM", "QC_NUM"),),
    )
    chart = ReportBlock(
        block_id=B2,
        block_kind=ReportBlockKind.CHART,
        claim_kind=ReportClaimKind.ANALYTICAL,
        content="Gelir serisi önceki dönemin altındadır.",
        evidence_refs=(_eref("E_CHART", "QC_CHART"),),
        artifact_ref=ReportArtifactRef(
            artifact_ref="art_chart_live",
            artifact_kind=ReportBlockKind.CHART,
        ),
        render_spec=ReportRenderSpec(
            presentation_kind=ReportBlockKind.CHART,
            options=(("display", "bar"),),
        ),
    )
    comparison = ReportBlock(
        block_id=B3,
        block_kind=ReportBlockKind.COMPARISON,
        claim_kind=ReportClaimKind.ANALYTICAL,
        content="Karşılaştırma ikinci segmentin daha düşük olduğunu gösterir.",
        evidence_refs=(_eref("E_COMPARE", "QC_COMPARE"),),
    )
    candidate = ReportBlock(
        block_id=B4,
        block_kind=ReportBlockKind.ROOT_CAUSE,
        claim_kind=ReportClaimKind.EPISTEMIC,
        content="Bakım düzeni gözlenen düşüş için aday açıklamadır.",
        evidence_refs=(_eref("E_CAUSE", "QC_CAUSE"),),
        finding_refs=(ReportFindingRef(finding_ref="find_live_candidate"),),
        epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
        hypothesis_ref="hyp_live_candidate",
        limitations=("Gözlemsel kanıt nedenselliği doğrulamaz.",),
    )
    return ReportDocument(
        report_id=RPT,
        title="Day9 bounded narration live report",
        sections=(
            ReportSection(
                section_id=SEC1,
                title="Performans",
                blocks=(numeric, chart),
                evidence_refs=(
                    _eref("E_NUM", "QC_NUM"),
                    _eref("E_CHART", "QC_CHART"),
                ),
                semantic_scope=("sem_" + "a" * 24,),
                followup_context_ref=CTX1,
                limitations=("KPI dönemi sınırlıdır.",),
            ),
            ReportSection(
                section_id=SEC2,
                title="Karşılaştırma ve aday neden",
                blocks=(comparison, candidate),
                evidence_refs=(
                    _eref("E_COMPARE", "QC_COMPARE"),
                    _eref("E_CAUSE", "QC_CAUSE"),
                ),
                semantic_scope=("sem_" + "a" * 24,),
                followup_context_ref=CTX2,
                limitations=("Kök neden deneysel olarak tanımlanmamıştır.",),
            ),
        ),
        evidence_index=(
            _eref("E_NUM", "QC_NUM"),
            _eref("E_CHART", "QC_CHART"),
            _eref("E_COMPARE", "QC_COMPARE"),
            _eref("E_CAUSE", "QC_CAUSE"),
        ),
        limitations=("Rapor yalnız mevcut doğrulanmış kanıtı yansıtır.",),
        provenance=ReportSourceProvenance(
            accepted_contract_id="contract-day9-live",
            lineage_id="lineage-day9-live",
            run_id="run-day9-live",
            tenant_binding="tenant-day9-live",
            context_version="ctx-day9-live",
            access_policy=ReportAccessPolicy.CURRENT_RUN_ONLY_REAUTHORIZE_ON_REPLAY,
        ),
    )


def run_live() -> dict[str, object]:
    report = build_fixture()
    before = report.model_dump(mode="json")

    settings = get_settings()
    scoped, profile = ModelRolePolicy(settings).scoped_settings(
        ModelRole.RESEARCH_MANAGER,
        model_override=LIVE_MODEL,
    )
    if profile.provider != "openrouter" or profile.model != LIVE_MODEL:
        raise LiveBehaviorFailure(
            f"unexpected live provider/model: {profile.provider}/{profile.model}"
        )

    llm = CountingLLM(build_generator(scoped))
    overlay = ReportNarrator(
        llm=llm,
        provider=profile.provider,
        model=profile.model,
    ).compose(report)

    if llm.calls != 1:
        raise LiveBehaviorFailure(f"expected exactly 1 model call, got {llm.calls}")
    if overlay.provider_receipt.status != NarrationProviderStatus.VALIDATED:
        raise LiveBehaviorFailure(
            f"narration did not pass gate: {overlay.provider_receipt.status.value}"
        )

    rendered = ReportNarrationRenderer().render(report=report, overlay=overlay)
    after = report.model_dump(mode="json")
    if after != before:
        raise LiveBehaviorFailure("canonical ReportDocument mutated during narration")

    canonical_sections = {section.section_id: section for section in report.sections}
    canonical_blocks = {
        block.block_id: block
        for section in report.sections
        for block in section.blocks
    }
    if {item.section_ref for item in overlay.section_presentations} != set(canonical_sections):
        raise LiveBehaviorFailure("narration omitted or invented a canonical section")

    for plan in overlay.section_presentations:
        expected = {
            block.block_id
            for block in canonical_sections[plan.section_ref].blocks
        }
        if set(plan.ordered_block_refs) != expected:
            raise LiveBehaviorFailure("narration block order is not an exact permutation")
        if not set(plan.emphasis_block_refs).issubset(expected):
            raise LiveBehaviorFailure("narration emphasis contains foreign block")

    if not set(overlay.executive_highlight_refs).issubset(set(canonical_blocks)):
        raise LiveBehaviorFailure("executive summary contains invented block")
    if len(overlay.executive_highlight_refs) > 3:
        raise LiveBehaviorFailure("executive summary exceeds hard selection bound")

    canonical_text = {
        block.block_id: block.content
        for block in canonical_blocks.values()
    }
    for section in rendered.sections:
        for block in section.blocks:
            if block.content != canonical_text[block.block_ref]:
                raise LiveBehaviorFailure("renderer created or rewrote factual block text")
    for block in rendered.executive_summary:
        if block.content != canonical_text[block.block_ref]:
            raise LiveBehaviorFailure("executive summary created a new claim")

    candidate = next(
        block
        for section in rendered.sections
        for block in section.blocks
        if block.block_ref == B4
    )
    if candidate.epistemic_label != EpistemicLabel.CANDIDATE_CAUSE:
        raise LiveBehaviorFailure("candidate-cause epistemic label was not preserved")
    if candidate.epistemic_display_label != "Aday neden":
        raise LiveBehaviorFailure("candidate-cause renderer label is not deterministic")
    if candidate.limitations != ("Gözlemsel kanıt nedenselliği doğrulamaz.",):
        raise LiveBehaviorFailure("candidate-cause limitation was suppressed")
    if rendered.limitations != ("Rapor yalnız mevcut doğrulanmış kanıtı yansıtır.",):
        raise LiveBehaviorFailure("report limitation was suppressed")

    return {
        "status": "pass",
        "provider": profile.provider,
        "model": profile.model,
        "model_calls": llm.calls,
        "tool_calls": 0,
        "semantic_calls": 0,
        "wren_calls": 0,
        "db_calls": 0,
        "research_calls": 0,
        "report_ref": report.report_id,
        "overlay_ref": overlay.overlay_id,
        "executive_highlight_refs": list(overlay.executive_highlight_refs),
        "section_presentations": [
            item.model_dump(mode="json")
            for item in overlay.section_presentations
        ],
        "candidate_cause_retained": True,
        "limitations_retained": True,
        "report_authority_unchanged": True,
        "narration_contract_version": overlay.contract_version,
    }


def main() -> int:
    report_path = Path("lab/reports/v2_day9_report_narration_live_sol.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = run_live()
    except Exception as exc:
        result = {
            "status": "fail",
            "provider": "openrouter",
            "model": LIVE_MODEL,
            "model_calls_budget": MAX_MODEL_CALLS,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "tool_calls": 0,
            "semantic_calls": 0,
            "wren_calls": 0,
            "db_calls": 0,
            "research_calls": 0,
        }
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1

    report_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
