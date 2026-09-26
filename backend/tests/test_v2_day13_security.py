"""Day13 provider-free tenant/principal/PII security hardening."""

from __future__ import annotations

from app.v2.models import EvidenceArtifact
from app.v2.report_builder import (
    ReportBlock,
    ReportBlockKind,
    ReportClaimKind,
    ReportDocument,
    ReportSection,
    ReportSourceProvenance,
)
from app.v2.report_narration import NarrationPacket
from app.v2.research_state import _manager_bounded_payload


def _pii_evidence() -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id="evi_day13",
        task_id="task-day13",
        obligation_ids=("U1",),
        query_contract_refs=("c-day13",),
        evidence_kind="standard_analytics",
        verified=True,
        payload={
            "query_count": 1,
            "executions": [
                {
                    "execution_id": "exec-day13",
                    "role": "primary",
                    "columns": ("sem_email", "sem_phone", "sem_value"),
                    "row_count": 1,
                    "rows": (
                        {
                            "sem_email": "ayse@firma.com",
                            "sem_phone": "05551234567",
                            "sem_value": 42.5,
                        },
                    ),
                }
            ],
        },
    )


def _pii_report() -> ReportDocument:
    return ReportDocument(
        report_id="rpt_" + "1" * 24,
        title="Yönetim raporu",
        sections=(
            ReportSection(
                section_id="rsec_" + "2" * 24,
                title="Sorumlu ayse@firma.com",
                blocks=(
                    ReportBlock(
                        block_id="rblk_" + "3" * 24,
                        block_kind=ReportBlockKind.TEXT,
                        claim_kind=ReportClaimKind.NARRATIVE,
                        content="İletişim 05551234567; kanıt özeti hazır.",
                        limitations=("E-posta ayse@firma.com paylaşılmamalı.",),
                    ),
                ),
                followup_context_ref="rctx_" + "4" * 24,
                limitations=("Telefon 05551234567 gizlidir.",),
            ),
        ),
        limitations=("IBAN TR330006100519786457841326 dışarı çıkmaz.",),
        provenance=ReportSourceProvenance(
            accepted_contract_id="atc-day13",
            lineage_id="atl-day13",
            run_id="mgr-day13",
            tenant_binding="tenant:a",
            context_version="ctx-day13",
        ),
    )


def test_research_provider_delta_masks_pii_but_preserves_numeric_truth():
    payload = _manager_bounded_payload(_pii_evidence())
    row = payload["executions"][0]["rows"][0]

    assert row["sem_email"] != "ayse@firma.com"
    assert row["sem_phone"] != "05551234567"
    assert "*" in row["sem_email"]
    assert "*" in row["sem_phone"]
    assert row["sem_value"] == 42.5


def test_narration_provider_projection_masks_pii_without_mutating_report_truth():
    report = _pii_report()
    packet = NarrationPacket.from_report(report)

    assert "ayse@firma.com" not in packet.sections[0].title
    assert "05551234567" not in packet.sections[0].blocks[0].content
    assert "ayse@firma.com" not in packet.sections[0].blocks[0].limitations[0]
    assert "05551234567" not in packet.sections[0].limitations[0]
    assert "TR330006100519786457841326" not in packet.limitations[0]

    # Canonical ReportDocument remains immutable analytical/presentation truth.
    assert report.sections[0].title == "Sorumlu ayse@firma.com"
    assert report.sections[0].blocks[0].content.startswith("İletişim 05551234567")


def test_provider_safe_views_do_not_expose_query_contract_sql_or_raw_evidence_metadata():
    payload = _manager_bounded_payload(_pii_evidence())
    raw = repr(payload).lower()

    assert "select " not in raw
    assert "query_contract_refs" not in raw
    assert "tenant_binding" not in raw
    assert "principal_subject" not in raw
    assert "accepted_contract_id" not in raw
