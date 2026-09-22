"""Provider-free invariants for Standard lane CoverageVeto."""

from __future__ import annotations

import json

import pytest

from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationPolarity,
)
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_coverage import (
    StandardCoverageError,
    StandardCoverageIssueKind,
    StandardCoverageVeto,
)


class _Scripted:
    def __init__(self, response):
        self.response = response
        self.calls = 0
        self.payload = None
        self.system = None

    def structured_json(self, system, user, *, schema, schema_name):
        del schema
        assert schema_name == "dima_standard_coverage_v1"
        self.calls += 1
        self.system = system
        self.payload = json.loads(user)
        return self.response


def _fixture(text="net geliri göster"):
    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id="m1", text=text)
    source = spans.mint_exact(message_id="m1", surface="net geliri")
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(source.source_ref,),
        semantic_handle_refs=("sem_" + "1" * 24,),
    )
    return spans, source_hash, obligation


def test_pass_view_exposes_no_semantic_handle_or_canonical_identifier():
    spans, source_hash, obligation = _fixture()
    scripted = _Scripted({"status": "PASS", "issues": []})

    audit = StandardCoverageVeto(
        structured=scripted.structured_json,
        source_spans=spans,
    ).audit(
        question="net geliri göster",
        obligations=(obligation,),
        source_message_hash=source_hash,
    )

    assert audit.status == "PASS"
    assert scripted.calls == 1
    dumped = json.dumps(scripted.payload, ensure_ascii=False)
    assert "sem_" not in dumped
    assert "canonical" not in dumped.lower()
    assert scripted.payload["STANDARD_INTENT_VIEW"][0]["capability_key"] == "performance"


def test_veto_can_only_report_bounded_coverage_issue_with_exact_source_text():
    text = "net geliri göster ama bölge kırılımı yapma"
    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id="m1", text=text)
    source = spans.mint_exact(message_id="m1", surface="net geliri")
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(source.source_ref,),
        semantic_handle_refs=("sem_" + "1" * 24,),
    )
    scripted = _Scripted(
        {
            "status": "VETO",
            "issues": [
                {
                    "kind": "EXCLUSION_OMITTED_OR_WRONG_POLARITY",
                    "source_surfaces": ["bölge kırılımı yapma"],
                    "note": "explicit exclusion is absent from Standard intent view",
                }
            ],
        }
    )

    audit = StandardCoverageVeto(
        structured=scripted.structured_json,
        source_spans=spans,
    ).audit(
        question=text,
        obligations=(obligation,),
        source_message_hash=source_hash,
    )

    assert audit.status == "VETO"
    assert audit.issues[0].kind == (
        StandardCoverageIssueKind.EXCLUSION_OMITTED_OR_WRONG_POLARITY
    )


def test_research_need_may_veto_standard_seal_without_creating_research_authority():
    text = "net geliri göster ve düşüşün kök nedenini araştır"
    spans, source_hash, obligation = _fixture(text)
    scripted = _Scripted(
        {
            "status": "VETO",
            "issues": [
                {
                    "kind": "RESEARCH_NEED_OMITTED",
                    "source_surfaces": ["düşüşün kök nedenini araştır"],
                    "note": "material investigation request is absent",
                }
            ],
        }
    )

    audit = StandardCoverageVeto(
        structured=scripted.structured_json,
        source_spans=spans,
    ).audit(
        question=text,
        obligations=(obligation,),
        source_message_hash=source_hash,
    )

    assert audit.status == "VETO"
    assert not hasattr(audit, "research_contract")
    assert not hasattr(audit.issues[0], "capability_key")


def test_coverage_cannot_fabricate_source_evidence():
    spans, source_hash, obligation = _fixture()
    scripted = _Scripted(
        {
            "status": "VETO",
            "issues": [
                {
                    "kind": "MATERIAL_REQUEST_OMITTED",
                    "source_surfaces": ["uydurulmuş istek"],
                    "note": "fabricated",
                }
            ],
        }
    )

    with pytest.raises(StandardCoverageError, match="exact user-message evidence"):
        StandardCoverageVeto(
            structured=scripted.structured_json,
            source_spans=spans,
        ).audit(
            question="net geliri göster",
            obligations=(obligation,),
            source_message_hash=source_hash,
        )


def test_intent_view_source_refs_are_runtime_validated():
    spans, source_hash, obligation = _fixture()
    fabricated = obligation.model_copy(
        update={"source_refs": ("src_" + "f" * 24,)}
    )
    scripted = _Scripted({"status": "PASS", "issues": []})

    with pytest.raises(KeyError, match="unknown/fabricated"):
        StandardCoverageVeto(
            structured=scripted.structured_json,
            source_spans=spans,
        ).audit(
            question="net geliri göster",
            obligations=(fabricated,),
            source_message_hash=source_hash,
        )
