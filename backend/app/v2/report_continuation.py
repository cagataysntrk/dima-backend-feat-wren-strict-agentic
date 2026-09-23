"""Day10 signed report-section continuation and bounded ephemeral context registry.

Tokens are locators plus integrity proof. They contain no semantic truth, Evidence
payload, formula, join path, or raw sem_* value.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any

from pydantic import Field

from app.v2.models import FrozenModel
from app.v2.report_builder import ReportDocument, ReportSection


_TOKEN_VERSION = 1


class ReportContinuationError(ValueError):
    pass


class StaleReportContinuationError(ReportContinuationError):
    pass


class ReportSectionContinuationPayload(FrozenModel):
    version: int = Field(ge=1)
    tenant_binding: str = Field(min_length=1)
    context_version: str = Field(min_length=1)
    flow_binding: str = Field(min_length=1)
    report_id: str = Field(pattern=r"^rpt_[a-f0-9]{24}$")
    section_id: str = Field(pattern=r"^rsec_[a-f0-9]{24}$")
    followup_context_ref: str = Field(pattern=r"^rctx_[a-f0-9]{24}$")
    source_run_ref: str = Field(min_length=1)
    lineage_ref: str = Field(min_length=1)


@dataclass(frozen=True)
class ReportContextEntry:
    """Same-process reference bundle. No authority is deep-copied."""

    report: ReportDocument
    section: ReportSection
    research_result: Any
    principal_subject: str
    tenant_binding: str
    context_version: str
    flow_binding: str
    source_run_ref: str
    lineage_ref: str
    report_version: int


def _b64e(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64d(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _flow_binding(session_id: str | None, thread_id: str | None) -> str:
    raw = json.dumps(
        {"session": session_id, "thread": thread_id},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ReportSectionContinuationSigner:
    def __init__(self, *, signing_key: bytes) -> None:
        if not signing_key:
            raise ValueError("report continuation signing key cannot be empty")
        self._key = bytes(signing_key)

    def mint(
        self,
        *,
        tenant_binding: str,
        context_version: str,
        session_id: str | None,
        thread_id: str | None,
        report_id: str,
        section_id: str,
        followup_context_ref: str,
        source_run_ref: str,
        lineage_ref: str,
    ) -> str:
        payload = ReportSectionContinuationPayload(
            version=_TOKEN_VERSION,
            tenant_binding=tenant_binding,
            context_version=context_version,
            flow_binding=_flow_binding(session_id, thread_id),
            report_id=report_id,
            section_id=section_id,
            followup_context_ref=followup_context_ref,
            source_run_ref=source_run_ref,
            lineage_ref=lineage_ref,
        )
        body = json.dumps(
            payload.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        encoded = _b64e(body)
        signature = hmac.new(
            self._key,
            encoded.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return f"{encoded}.{_b64e(signature)}"

    def verify(
        self,
        token: str,
        *,
        tenant_binding: str,
        context_version: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> ReportSectionContinuationPayload:
        try:
            encoded, signature_text = token.split(".", 1)
            expected = hmac.new(
                self._key,
                encoded.encode("ascii"),
                hashlib.sha256,
            ).digest()
            actual = _b64d(signature_text)
            if not hmac.compare_digest(expected, actual):
                raise StaleReportContinuationError(
                    "report continuation signature invalid"
                )
            payload = ReportSectionContinuationPayload.model_validate_json(
                _b64d(encoded)
            )
        except ReportContinuationError:
            raise
        except Exception as exc:
            raise StaleReportContinuationError(
                "report continuation format invalid"
            ) from exc

        if payload.version != _TOKEN_VERSION:
            raise StaleReportContinuationError(
                "report continuation version stale"
            )
        if payload.tenant_binding != tenant_binding:
            raise StaleReportContinuationError(
                "report continuation tenant mismatch"
            )
        if payload.context_version != context_version:
            raise StaleReportContinuationError(
                "report continuation context stale"
            )
        if payload.flow_binding != _flow_binding(session_id, thread_id):
            raise StaleReportContinuationError(
                "report continuation session/thread mismatch"
            )
        return payload


class ReportContextRegistry:
    """Bounded ephemeral same-process registry for Day10 section follow-up."""

    def __init__(self, *, max_entries: int = 128) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max_entries = max_entries
        self._entries: dict[str, ReportContextEntry] = {}
        self._order: list[str] = []

    def register(
        self,
        *,
        report: ReportDocument,
        research_result: Any,
        principal_subject: str,
        tenant_binding: str,
        context_version: str,
        session_id: str | None,
        thread_id: str | None,
        source_run_ref: str,
        lineage_ref: str,
        report_version: int,
    ) -> tuple[ReportContextEntry, ...]:
        entries: list[ReportContextEntry] = []
        flow = _flow_binding(session_id, thread_id)
        for section in report.sections:
            entry = ReportContextEntry(
                report=report,
                section=section,
                research_result=research_result,
                principal_subject=principal_subject,
                tenant_binding=tenant_binding,
                context_version=context_version,
                flow_binding=flow,
                source_run_ref=source_run_ref,
                lineage_ref=lineage_ref,
                report_version=report_version,
            )
            ref = section.followup_context_ref
            if ref not in self._entries:
                self._order.append(ref)
            self._entries[ref] = entry
            entries.append(entry)

        while len(self._order) > self._max_entries:
            stale_ref = self._order.pop(0)
            self._entries.pop(stale_ref, None)
        return tuple(entries)

    def resolve(
        self,
        payload: ReportSectionContinuationPayload,
        *,
        principal_subject: str,
        tenant_binding: str,
        context_version: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> ReportContextEntry:
        entry = self._entries.get(payload.followup_context_ref)
        if entry is None:
            raise StaleReportContinuationError(
                "report continuation context missing; rebind required"
            )
        if not principal_subject:
            raise StaleReportContinuationError(
                "current principal missing"
            )
        if entry.principal_subject != principal_subject:
            raise StaleReportContinuationError(
                "report continuation principal mismatch"
            )
        if (
            entry.tenant_binding != tenant_binding
            or payload.tenant_binding != tenant_binding
        ):
            raise StaleReportContinuationError(
                "report continuation tenant mismatch"
            )
        if (
            entry.context_version != context_version
            or payload.context_version != context_version
        ):
            raise StaleReportContinuationError(
                "report continuation context stale"
            )
        flow = _flow_binding(session_id, thread_id)
        if entry.flow_binding != flow or payload.flow_binding != flow:
            raise StaleReportContinuationError(
                "report continuation session/thread mismatch"
            )
        if entry.report.report_id != payload.report_id:
            raise StaleReportContinuationError(
                "report continuation report mismatch"
            )
        if entry.section.section_id != payload.section_id:
            raise StaleReportContinuationError(
                "report continuation section mismatch"
            )
        if entry.source_run_ref != payload.source_run_ref:
            raise StaleReportContinuationError(
                "report continuation run mismatch"
            )
        if entry.lineage_ref != payload.lineage_ref:
            raise StaleReportContinuationError(
                "report continuation lineage mismatch"
            )
        return entry
