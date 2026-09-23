"""Day10 product-facing contracts for the authoritative /ask-v2 front door.

These models compose existing V2 authorities. They do not own semantic, analytical,
Evidence, epistemic, or completion truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import Field

from app.v2.models import (
    BoundedSemanticContextV0,
    FrozenModel,
    TenantAnalyticsRuntimeV0,
)
from app.v2.report_builder import ReportDocument
from app.v2.report_narration import ReportNarrationOverlay


class ProductLane(StrEnum):
    STANDARD = "STANDARD"
    RESEARCH = "RESEARCH"


class ProductStatus(StrEnum):
    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    PARTIAL = "PARTIAL"
    REPORT = "REPORT"
    UNSUPPORTED = "UNSUPPORTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class ProductEventKind(StrEnum):
    REQUEST_ACCEPTED = "REQUEST_ACCEPTED"
    LANE_SELECTED = "LANE_SELECTED"
    RESEARCH_STARTED = "RESEARCH_STARTED"
    EVIDENCE_VERIFIED = "EVIDENCE_VERIFIED"
    ADAPTIVE_BRANCH_OPENED = "ADAPTIVE_BRANCH_OPENED"
    RELATIONSHIP_CHECKED = "RELATIONSHIP_CHECKED"
    ROOT_CAUSE_CANDIDATE = "ROOT_CAUSE_CANDIDATE"
    ARTIFACT_READY = "ARTIFACT_READY"
    DATA_GAP = "DATA_GAP"
    REPORT_READY = "REPORT_READY"
    PARTIAL_READY = "PARTIAL_READY"
    KEEPALIVE = "KEEPALIVE"
    TERMINAL = "TERMINAL"


class ProductEvent(FrozenModel):
    event_id: str = Field(pattern=r"^pevt_[a-f0-9]{24}$")
    sequence: int = Field(ge=1)
    kind: ProductEventKind
    elapsed_ms: int = Field(ge=0)
    refs: tuple[str, ...] = ()
    display_text: str | None = None


class ProductEvidenceRef(FrozenModel):
    evidence_ref: str = Field(min_length=1)
    query_contract_refs: tuple[str, ...] = ()
    evidence_kind: str = Field(min_length=1)
    verified: bool


class ProductTerminalReceipt(FrozenModel):
    lane: ProductLane
    status: ProductStatus
    verified_complete: bool = False
    terminal_status: str | None = None
    reasons: tuple[str, ...] = ()
    manager_turns: int = Field(default=0, ge=0)
    tool_calls: int = Field(default=0, ge=0)
    data_queries: int = Field(default=0, ge=0)


class ProductResponse(FrozenModel):
    request_ref: str = Field(min_length=1)
    lane: ProductLane
    status: ProductStatus
    events: tuple[ProductEvent, ...] = ()
    evidence_refs: tuple[ProductEvidenceRef, ...] = ()
    artifact_refs: tuple[str, ...] = ()
    report: ReportDocument | None = None
    narration: ReportNarrationOverlay | None = None
    limitations: tuple[str, ...] = ()
    terminal_receipt: ProductTerminalReceipt
    continuation: str | None = None


@dataclass(frozen=True)
class ProductRequestContext:
    """Server-internal infrastructure context bound exactly once at the front door."""

    request_ref: str
    tenant_binding: str
    principal: Any
    tenant_runtime: TenantAnalyticsRuntimeV0
    service: Any
    schema: dict[str, Any]
    semantic_context: BoundedSemanticContextV0
    contract_store: Any
    session_id: str | None
    thread_id: str | None
