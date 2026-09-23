"""Provider-free D10-D signed section continuation boundary attacks."""

from __future__ import annotations

import base64
import json

import pytest

from app.v2.report_builder import (
    ReportBlock,
    ReportBlockKind,
    ReportClaimKind,
    ReportDocument,
    ReportSection,
    ReportSourceProvenance,
)
from app.v2.report_continuation import (
    ReportContextRegistry,
    ReportSectionContinuationSigner,
    StaleReportContinuationError,
)


RPT = "rpt_" + "1" * 24
SEC = "rsec_" + "2" * 24
BLK = "rblk_" + "3" * 24
CTX_REF = "rctx_" + "4" * 24


def _report() -> ReportDocument:
    block = ReportBlock(
        block_id=BLK,
        block_kind=ReportBlockKind.TEXT,
        claim_kind=ReportClaimKind.NARRATIVE,
        content="Canonical presentation text.",
    )
    section = ReportSection(
        section_id=SEC,
        title="Section title is presentation only",
        blocks=(block,),
        semantic_scope=("sem_" + "a" * 24,),
        followup_context_ref=CTX_REF,
    )
    return ReportDocument(
        report_id=RPT,
        title="Report",
        sections=(section,),
        provenance=ReportSourceProvenance(
            accepted_contract_id="atc-1",
            lineage_id="atl-1",
            run_id="mgr-1",
            tenant_binding="tenant-a",
            context_version="ctx-a",
        ),
    )


def _signer():
    return ReportSectionContinuationSigner(signing_key=b"day10-test-key")


def _token():
    return _signer().mint(
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        report_id=RPT,
        section_id=SEC,
        followup_context_ref=CTX_REF,
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
    )


def test_section_token_contains_only_opaque_control_identity():
    token = _token()
    encoded = token.split(".", 1)[0]
    encoded += "=" * (-len(encoded) % 4)
    payload = json.loads(base64.urlsafe_b64decode(encoded))

    assert set(payload) == {
        "version",
        "tenant_binding",
        "context_version",
        "flow_binding",
        "report_id",
        "section_id",
        "followup_context_ref",
        "source_run_ref",
        "lineage_ref",
    }
    raw = json.dumps(payload)
    assert "sem_" not in raw
    assert "Evidence" not in raw
    assert "canonical" not in raw
    assert "formula" not in raw
    assert "Section title" not in raw


def test_tampered_and_foreign_context_tokens_fail_closed():
    signer = _signer()
    token = _token()
    body, signature = token.split(".", 1)
    tampered = ("A" if body[0] != "A" else "B") + body[1:] + "." + signature

    with pytest.raises(StaleReportContinuationError, match="signature|format"):
        signer.verify(
            tampered,
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )

    for kwargs, message in (
        ({"tenant_binding": "tenant-b"}, "tenant"),
        ({"context_version": "ctx-b"}, "context"),
        ({"session_id": "session-b"}, "session/thread"),
        ({"thread_id": "thread-b"}, "session/thread"),
    ):
        params = {
            "tenant_binding": "tenant-a",
            "context_version": "ctx-a",
            "session_id": "session-a",
            "thread_id": "thread-a",
        }
        params.update(kwargs)
        with pytest.raises(StaleReportContinuationError, match=message):
            signer.verify(token, **params)


def test_registry_revalidates_current_principal_and_exact_section_identity():
    report = _report()
    registry = ReportContextRegistry(max_entries=4)
    research_result = object()
    registry.register(
        report=report,
        research_result=research_result,
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
        report_version=1,
    )
    payload = _signer().verify(
        _token(),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
    )

    entry = registry.resolve(
        payload,
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
    )
    assert entry.report is report
    assert entry.research_result is research_result
    assert entry.section.section_id == SEC

    with pytest.raises(StaleReportContinuationError, match="principal"):
        registry.resolve(
            payload,
            principal_subject="user-b",
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )

    wrong_section = payload.model_copy(
        update={"section_id": "rsec_" + "f" * 24}
    )
    with pytest.raises(StaleReportContinuationError, match="section"):
        registry.resolve(
            wrong_section,
            principal_subject="user-a",
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )


def test_evicted_or_missing_registry_context_requires_rebind():
    report = _report()
    registry = ReportContextRegistry(max_entries=1)
    registry.register(
        report=report,
        research_result=object(),
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
        report_version=1,
    )
    payload = _signer().verify(
        _token(),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
    )

    # A new report/section evicts the sole bounded entry.
    new_section = report.sections[0].model_copy(
        update={
            "section_id": "rsec_" + "5" * 24,
            "followup_context_ref": "rctx_" + "6" * 24,
        }
    )
    new_report = report.model_copy(
        update={
            "report_id": "rpt_" + "7" * 24,
            "sections": (new_section,),
        }
    )
    registry.register(
        report=new_report,
        research_result=object(),
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
        report_version=2,
    )

    with pytest.raises(StaleReportContinuationError, match="rebind"):
        registry.resolve(
            payload,
            principal_subject="user-a",
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )



def test_stream_adapter_uses_same_product_coordinator_and_existing_cancel_signal():
    import inspect
    import app.routers.ask_v2 as route

    source = inspect.getsource(route.ask_v2_stream)
    assert "_coordinator.handle(" in source
    assert "ProductCoordinator(" not in source
    assert "cancel_check=cancelled.is_set" in source
    assert "ProductEventKind.KEEPALIVE" in source
    assert "cancelled.set()" in source
