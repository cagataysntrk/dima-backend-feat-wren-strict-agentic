"""Provider-free Day9-B attacks for bounded report narration."""

from __future__ import annotations

import ast
import inspect
import json

import pytest
from pydantic import ValidationError

import app.v2.report_narration as narration_module
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
    NarrationPacket,
    NarrationPlanCode,
    NarrationPlanError,
    NarrationPlanGate,
    NarrationPlanProposal,
    NarrationProviderStatus,
    ReportNarrationRenderer,
    ReportNarrator,
    SectionNarrationPlanProposal,
    build_overlay,
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

SEM_PRIVATE = "sem_" + "a" * 24
ART_PRIVATE = "art_private_chart"
FINDING_PRIVATE = "find_private_cause"
E_NUM = "E_NUM"
E_CHART = "E_CHART"
E_COMPARE = "E_COMPARE"
E_CAUSE = "E_CAUSE"


def _eref(ref: str, qc: str) -> ReportEvidenceRef:
    return ReportEvidenceRef(evidence_ref=ref, query_contract_refs=(qc,))


def _report(*, title: str = "Canonical report") -> ReportDocument:
    numeric = ReportBlock(
        block_id=B1,
        block_kind=ReportBlockKind.KPI,
        claim_kind=ReportClaimKind.NUMERIC,
        content="Net gelir 100 birimdir.",
        evidence_refs=(_eref(E_NUM, "QC_NUM"),),
    )
    chart = ReportBlock(
        block_id=B2,
        block_kind=ReportBlockKind.CHART,
        claim_kind=ReportClaimKind.ANALYTICAL,
        content="Gelir serisi önceki dönemin altındadır.",
        evidence_refs=(_eref(E_CHART, "QC_CHART"),),
        artifact_ref=ReportArtifactRef(
            artifact_ref=ART_PRIVATE,
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
        evidence_refs=(_eref(E_COMPARE, "QC_COMPARE"),),
    )
    root = ReportBlock(
        block_id=B4,
        block_kind=ReportBlockKind.ROOT_CAUSE,
        claim_kind=ReportClaimKind.EPISTEMIC,
        content="Bakım düzeni gözlenen düşüş için aday açıklamadır.",
        evidence_refs=(_eref(E_CAUSE, "QC_CAUSE"),),
        finding_refs=(ReportFindingRef(finding_ref=FINDING_PRIVATE),),
        epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
        hypothesis_ref="hyp_private",
        limitations=("Gözlemsel kanıt nedenselliği doğrulamaz.",),
    )

    s1 = ReportSection(
        section_id=SEC1,
        title="Performans",
        blocks=(numeric, chart),
        evidence_refs=(
            _eref(E_NUM, "QC_NUM"),
            _eref(E_CHART, "QC_CHART"),
        ),
        semantic_scope=(SEM_PRIVATE,),
        followup_context_ref=CTX1,
        limitations=("KPI dönemi sınırlıdır.",),
    )
    s2 = ReportSection(
        section_id=SEC2,
        title="Karşılaştırma ve aday neden",
        blocks=(comparison, root),
        evidence_refs=(
            _eref(E_COMPARE, "QC_COMPARE"),
            _eref(E_CAUSE, "QC_CAUSE"),
        ),
        semantic_scope=(SEM_PRIVATE,),
        followup_context_ref=CTX2,
        limitations=("Kök neden deneysel olarak tanımlanmamıştır.",),
    )
    return ReportDocument(
        report_id=RPT,
        title=title,
        sections=(s1, s2),
        evidence_index=(
            _eref(E_NUM, "QC_NUM"),
            _eref(E_CHART, "QC_CHART"),
            _eref(E_COMPARE, "QC_COMPARE"),
            _eref(E_CAUSE, "QC_CAUSE"),
        ),
        limitations=("Rapor yalnız mevcut doğrulanmış kanıtı yansıtır.",),
        provenance=ReportSourceProvenance(
            accepted_contract_id="contract-day9",
            lineage_id="lineage-day9",
            run_id="run-day9",
            tenant_binding="tenant-day9",
            context_version="ctx-day9",
            access_policy=ReportAccessPolicy.CURRENT_RUN_ONLY_REAUTHORIZE_ON_REPLAY,
        ),
    )


def _valid_proposal(
    *,
    sec1_order=(B2, B1),
    sec2_order=(B4, B3),
    executive=(B1, B4),
) -> NarrationPlanProposal:
    return NarrationPlanProposal(
        report_ref=RPT,
        executive_highlight_block_refs=executive,
        section_plans=(
            SectionNarrationPlanProposal(
                section_ref=SEC1,
                ordered_block_refs=sec1_order,
                emphasis_block_refs=(B2,),
            ),
            SectionNarrationPlanProposal(
                section_ref=SEC2,
                ordered_block_refs=sec2_order,
                emphasis_block_refs=(B4,),
            ),
        ),
    )


def _code(exc: pytest.ExceptionInfo[NarrationPlanError]) -> str:
    return str(exc.value).split(":", 1)[0]


def test_narration_packet_is_minimum_presentation_safe_projection():
    packet = NarrationPacket.from_report(_report())
    payload = packet.model_dump(mode="json")
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    assert payload["report_ref"] == RPT
    assert [s["section_ref"] for s in payload["sections"]] == [SEC1, SEC2]
    assert ART_PRIVATE not in raw
    assert FINDING_PRIVATE not in raw
    assert E_NUM not in raw
    assert "QC_NUM" not in raw
    assert SEM_PRIVATE not in raw
    assert "semantic_scope" not in raw
    assert "evidence_refs" not in raw
    assert "finding_refs" not in raw
    assert "query_contract" not in raw.lower()
    assert "sql" not in {key.lower() for key in payload}


def test_output_schema_has_no_free_form_factual_prose_or_authority_fields():
    strict_schema = narration_module._strict_native_schema(
        NarrationPlanProposal.model_json_schema()
    )
    schema = json.dumps(
        strict_schema,
        ensure_ascii=False,
        sort_keys=True,
    )

    def assert_strict(node):
        if isinstance(node, dict):
            if node.get("type") == "object" or "properties" in node:
                props = node.get("properties") or {}
                assert node.get("additionalProperties") is False
                assert node.get("required") == list(props.keys())
            assert "default" not in node
            for value in node.values():
                assert_strict(value)
        elif isinstance(node, list):
            for value in node:
                assert_strict(value)

    assert_strict(strict_schema)
    for forbidden in (
        "summary_text",
        "analysis",
        "explanation",
        "cause",
        "numeric_statement",
        "rewritten_claim",
        "evidence_ref",
        "finding_ref",
        "artifact_ref",
        "overlay_id",
        "followup_context_ref",
    ):
        assert f'"{forbidden}"' not in schema

    with pytest.raises(ValidationError):
        NarrationPlanProposal.model_validate(
            {
                **_valid_proposal().model_dump(mode="json"),
                "summary_text": "Invented summary",
            }
        )


def test_unknown_report_ref_is_rejected():
    proposal = _valid_proposal().model_copy(
        update={"report_ref": "rpt_" + "f" * 24}
    )
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=proposal)
    assert _code(exc) == NarrationPlanCode.REPORT_REF_MISMATCH.value


def test_unknown_and_missing_section_refs_are_rejected():
    unknown = _valid_proposal().model_copy(
        update={
            "section_plans": (
                _valid_proposal().section_plans[0],
                SectionNarrationPlanProposal(
                    section_ref="rsec_" + "f" * 24,
                    ordered_block_refs=(B3, B4),
                ),
            )
        }
    )
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=unknown)
    assert _code(exc) == NarrationPlanCode.UNKNOWN_SECTION_REF.value

    missing = _valid_proposal().model_copy(
        update={"section_plans": (_valid_proposal().section_plans[0],)}
    )
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=missing)
    assert _code(exc) == NarrationPlanCode.SECTION_COVERAGE_MISMATCH.value


def test_unknown_block_ref_is_rejected():
    bad = "rblk_" + "f" * 24
    proposal = _valid_proposal().model_copy(
        update={"executive_highlight_block_refs": (bad,)}
    )
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=proposal)
    assert _code(exc) == NarrationPlanCode.UNKNOWN_BLOCK_REF.value


def test_foreign_section_block_ref_is_rejected():
    proposal = _valid_proposal(
        sec1_order=(B1, B3),
    )
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=proposal)
    assert _code(exc) == NarrationPlanCode.FOREIGN_SECTION_BLOCK_REF.value


def test_duplicate_refs_and_non_permutation_are_rejected():
    duplicate = _valid_proposal(sec1_order=(B1, B1))
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=duplicate)
    assert _code(exc) == NarrationPlanCode.DUPLICATE_BLOCK_REF.value

    missing_block = _valid_proposal(sec1_order=(B1,))
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=missing_block)
    assert _code(exc) == NarrationPlanCode.BLOCK_PERMUTATION_REQUIRED.value


def test_executive_highlight_is_bounded_and_unique():
    with pytest.raises(ValidationError):
        NarrationPlanProposal(
            report_ref=RPT,
            executive_highlight_block_refs=(B1, B2, B3, B4),
            section_plans=_valid_proposal().section_plans,
        )

    duplicate = _valid_proposal(executive=(B1, B1))
    with pytest.raises(NarrationPlanError) as exc:
        NarrationPlanGate().admit(report=_report(), proposal=duplicate)
    assert _code(exc) == NarrationPlanCode.DUPLICATE_BLOCK_REF.value


def test_gate_accepts_valid_plan_and_server_owns_overlay_identity():
    report = _report()
    proposal = _valid_proposal()
    plan = NarrationPlanGate().admit(report=report, proposal=proposal)

    class Receipt:
        pass

    from app.v2.report_narration import NarrationProviderReceipt

    receipt = NarrationProviderReceipt(
        provider="rule-test",
        model="scripted",
        status=NarrationProviderStatus.VALIDATED,
    )
    first = build_overlay(report=report, plan=plan, receipt=receipt)
    second = build_overlay(report=report, plan=plan, receipt=receipt)

    assert first.overlay_id.startswith("rnov_")
    assert first.overlay_id == second.overlay_id
    assert first.report_ref == report.report_id
    assert not hasattr(proposal, "overlay_id")


def test_renderer_preserves_candidate_cause_label_and_all_limitations():
    report = _report()
    plan = NarrationPlanGate().admit(report=report, proposal=_valid_proposal())

    from app.v2.report_narration import NarrationProviderReceipt

    overlay = build_overlay(
        report=report,
        plan=plan,
        receipt=NarrationProviderReceipt(
            provider="rule-test",
            model="scripted",
            status=NarrationProviderStatus.VALIDATED,
        ),
    )
    rendered = ReportNarrationRenderer().render(report=report, overlay=overlay)

    root = next(
        block
        for section in rendered.sections
        for block in section.blocks
        if block.block_ref == B4
    )
    assert root.content == "Bakım düzeni gözlenen düşüş için aday açıklamadır."
    assert root.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
    assert root.epistemic_display_label == "Aday neden"
    assert root.limitations == ("Gözlemsel kanıt nedenselliği doğrulamaz.",)
    assert rendered.sections[1].limitations == (
        "Kök neden deneysel olarak tanımlanmamıştır.",
    )
    assert rendered.limitations == (
        "Rapor yalnız mevcut doğrulanmış kanıtı yansıtır.",
    )


def test_presentation_reorder_never_mutates_canonical_report_authority():
    report = _report()
    before = report.model_dump(mode="json")

    gate = NarrationPlanGate()
    plan_a = gate.admit(report=report, proposal=_valid_proposal())
    plan_b = gate.admit(
        report=report,
        proposal=_valid_proposal(
            sec1_order=(B1, B2),
            sec2_order=(B3, B4),
            executive=(B3,),
        ),
    )

    from app.v2.report_narration import NarrationProviderReceipt

    receipt = NarrationProviderReceipt(
        provider="rule-test",
        model="scripted",
        status=NarrationProviderStatus.VALIDATED,
    )
    overlay_a = build_overlay(report=report, plan=plan_a, receipt=receipt)
    overlay_b = build_overlay(report=report, plan=plan_b, receipt=receipt)

    ReportNarrationRenderer().render(report=report, overlay=overlay_a)
    ReportNarrationRenderer().render(report=report, overlay=overlay_b)

    assert report.model_dump(mode="json") == before
    assert overlay_a.overlay_id != overlay_b.overlay_id
    assert report.report_id == RPT
    assert [section.section_id for section in report.sections] == [SEC1, SEC2]


class ScriptedLLM:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0
        self.system = None
        self.user = None
        self.schema = None

    def structured_json(self, system, user, *, schema, schema_name):
        self.calls += 1
        self.system = system
        self.user = user
        self.schema = schema
        assert schema_name == "dima_report_narration_plan"
        if isinstance(self.payload, Exception):
            raise self.payload
        return (
            self.payload
            if isinstance(self.payload, str)
            else json.dumps(self.payload)
        )


def test_fake_model_contract_uses_exactly_one_call_and_no_tools():
    report = _report()
    llm = ScriptedLLM(_valid_proposal().model_dump(mode="json"))
    before = report.model_dump(mode="json")

    overlay = ReportNarrator(
        llm=llm,
        provider="scripted",
        model="sol-shaped",
    ).compose(report)

    assert llm.calls == 1
    assert overlay.provider_receipt.status == NarrationProviderStatus.VALIDATED
    assert overlay.provider_receipt.call_count == 1
    assert report.model_dump(mode="json") == before
    assert "tools" not in json.dumps(llm.schema).lower()
    assert E_NUM not in llm.user
    assert SEM_PRIVATE not in llm.user
    assert ART_PRIVATE not in llm.user


def test_invalid_plan_falls_back_after_one_call_and_report_remains_valid():
    report = _report()
    invalid = _valid_proposal().model_copy(
        update={"section_plans": (_valid_proposal().section_plans[0],)}
    )
    llm = ScriptedLLM(invalid.model_dump(mode="json"))
    before = report.model_dump(mode="json")

    overlay = ReportNarrator(
        llm=llm,
        provider="scripted",
        model="sol-shaped",
    ).compose(report)
    rendered = ReportNarrationRenderer().render(report=report, overlay=overlay)

    assert llm.calls == 1
    assert overlay.provider_receipt.status == NarrationProviderStatus.FALLBACK_PLAN_FAILURE
    assert report.model_dump(mode="json") == before
    assert len(rendered.sections) == 2
    assert {
        block.block_ref
        for section in rendered.sections
        for block in section.blocks
    } == {B1, B2, B3, B4}


def test_schema_or_provider_failure_never_triggers_repair_call():
    for payload, expected in (
        ("not-json", NarrationProviderStatus.FALLBACK_SCHEMA_FAILURE),
        (RuntimeError("provider down"), NarrationProviderStatus.FALLBACK_PROVIDER_FAILURE),
    ):
        llm = ScriptedLLM(payload)
        overlay = ReportNarrator(
            llm=llm,
            provider="scripted",
            model="sol-shaped",
        ).compose(_report())
        assert llm.calls == 1
        assert overlay.provider_receipt.status == expected


def test_renderer_has_no_analytics_or_probabilistic_dependency():
    source = inspect.getsource(narration_module.ReportNarrationRenderer)
    tree = ast.parse(source)
    forbidden_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {
                "structured_json",
                "structured_text",
                "cube_sql",
                "query",
                "resolve",
                "recommend",
            }:
                forbidden_calls.append(node.func.attr)
    assert forbidden_calls == []
