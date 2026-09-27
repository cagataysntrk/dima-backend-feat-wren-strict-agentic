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

from app.v2.manager_models import (
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
)
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityLane,
    ManagerCapabilityRegistry,
)
from app.v2.models import (
    ConversationStateV2,
    FocusStateV0,
    FrozenModel,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TopicFrameV0,
)
from app.v2.report_builder import ReportDocument, ReportSection


_TOKEN_VERSION = 1


class ReportContinuationError(ValueError):
    pass


class StaleReportContinuationError(ReportContinuationError):
    pass


class MissingReportContinuationContextError(StaleReportContinuationError):
    """Ephemeral registry miss that may be rehydrated from durable canonical state."""


class ReportContinuationNotAdmissibleError(ReportContinuationError):
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


@dataclass(frozen=True)
class ContinuationAnalyticalAuthority:
    """Pure selected-section view over prior accepted analytical authority.

    This is never a second authority store.  It contains only canonical parent
    references already present in the prior immutable ledger and proven, through
    typed report provenance, to belong to the selected signed section.
    """

    lineage_id: str
    contract_id: str
    ledger_version: int
    admitted_parent_refs: tuple[str, ...]
    section_evidence_refs: tuple[str, ...]
    section_finding_refs: tuple[str, ...]


def continuation_analytical_authority(
    entry: ReportContextEntry,
) -> ContinuationAnalyticalAuthority:
    """Derive section-local inherited analytical parents without label matching.

    Strong provenance comes from selected-section Finding parents first.  When no
    Finding is present, exact selected-section Evidence ownership is used.  The
    result is intersected with exact semantic-scope membership when that scope can
    identify prior obligations.  Ambiguity is preserved as cardinality; callers
    must never choose one parent by order or similarity.
    """

    prior = entry.research_result
    contract = getattr(prior, "accepted_contract", None)
    ledger = getattr(prior, "ledger", None)
    if contract is None or ledger is None:
        raise ReportContinuationNotAdmissibleError(
            "signed continuation requires prior accepted contract + ledger"
        )
    if (
        contract.lineage_id != entry.lineage_ref
        or ledger.lineage_id != contract.lineage_id
        or ledger.version != contract.version
    ):
        raise ReportContinuationNotAdmissibleError(
            "signed continuation prior authority lineage/version mismatch"
        )
    provenance = entry.report.provenance
    if (
        provenance.accepted_contract_id != contract.contract_id
        or provenance.lineage_id != contract.lineage_id
        or provenance.tenant_binding != entry.tenant_binding
        or provenance.context_version != entry.context_version
    ):
        raise ReportContinuationNotAdmissibleError(
            "signed continuation report provenance does not match prior authority"
        )

    capability_registry = ManagerCapabilityRegistry()
    eligible: dict[str, Any] = {}
    for item in ledger.items:
        if (
            item.origin != ObligationOrigin.USER_MUST
            or item.priority != ObligationPriority.MUST
            or item.polarity != ObligationPolarity.REQUIRED
            or item.status == ObligationStatus.SUPERSEDED
        ):
            continue
        try:
            spec = capability_registry.get(item.capability_key)
        except KeyError:
            continue
        if (
            spec.execution_mode
            not in {
                ManagerCapabilityExecutionMode.DIRECT,
                ManagerCapabilityExecutionMode.ORCHESTRATED,
            }
            or spec.lane
            not in {
                ManagerCapabilityLane.STANDARD,
                ManagerCapabilityLane.RESEARCH,
            }
        ):
            continue
        eligible[item.obligation_id] = item

    section_evidence_refs = tuple(
        dict.fromkeys(ref.evidence_ref for ref in entry.section.evidence_refs)
    )
    section_finding_refs = tuple(
        dict.fromkeys(
            ref.finding_ref
            for block in entry.section.blocks
            for ref in block.finding_refs
        )
    )
    evidence_by_id = {
        item.artifact_id: item
        for item in tuple(getattr(prior, "evidence", ()) or ())
    }
    finding_by_id = {
        item.finding_id: item
        for item in tuple(getattr(prior, "findings", ()) or ())
    }

    finding_parents = {
        finding.parent_obligation_id
        for ref in section_finding_refs
        if (finding := finding_by_id.get(ref)) is not None
        and finding.parent_obligation_id in eligible
    }

    evidence_parents: set[str] = set()
    for ref in section_evidence_refs:
        evidence = evidence_by_id.get(ref)
        if evidence is not None:
            evidence_parents.update(
                obligation_id
                for obligation_id in evidence.obligation_ids
                if obligation_id in eligible
            )
    section_evidence_set = set(section_evidence_refs)
    evidence_parents.update(
        item.obligation_id
        for item in eligible.values()
        if section_evidence_set.intersection(item.evidence_refs)
    )

    section_scope = set(entry.section.semantic_scope)
    scope_parents = {
        item.obligation_id
        for item in eligible.values()
        if item.semantic_handle_refs
        and set(item.semantic_handle_refs).issubset(section_scope)
    }

    provenance_parents = finding_parents or evidence_parents
    if provenance_parents:
        represented = set(provenance_parents)
        if scope_parents:
            represented.intersection_update(scope_parents)
    else:
        represented = set(scope_parents)

    return ContinuationAnalyticalAuthority(
        lineage_id=contract.lineage_id,
        contract_id=contract.contract_id,
        ledger_version=ledger.version,
        admitted_parent_refs=tuple(sorted(represented)),
        section_evidence_refs=section_evidence_refs,
        section_finding_refs=section_finding_refs,
    )


def _b64e(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64d(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _normalized_scope_kind(target_kind: str) -> str | None:
    return {
        "metric": "metric",
        "kpi": "metric",
        "dimension": "dimension",
        "entity_value": "filter",
        "filter": "filter",
        "period": "period",
        "time": "period",
        "comparison": "comparison",
    }.get(str(target_kind))


def continuation_scope_by_kind(
    entry: ReportContextEntry,
) -> dict[str, tuple[str, ...]]:
    """Revalidate the signed section's opaque semantic scope against its original registry."""

    registry = entry.research_result.semantic_handles
    out: dict[str, list[str]] = {}
    for handle_ref in entry.section.semantic_scope:
        handle = registry.validate(
            handle_ref,
            tenant_binding=entry.tenant_binding,
            context_version=entry.context_version,
        )
        kind = _normalized_scope_kind(handle.target_kind)
        if kind is not None:
            out.setdefault(kind, []).append(handle_ref)
    return {
        kind: tuple(dict.fromkeys(refs))
        for kind, refs in out.items()
    }


def continuation_conversation(entry: ReportContextEntry) -> ConversationStateV2:
    """Project only the selected report section into typed conversation focus."""

    registry = entry.research_result.semantic_handles
    metrics: list[ResolvedSemanticRef] = []
    dimensions: list[ResolvedSemanticRef] = []
    filters: list[ResolvedFilterRef] = []
    periods: list[ResolvedPeriod] = []
    labels: list[str] = []
    cubes: set[str] = set()

    for handle_ref in entry.section.semantic_scope:
        binding = registry.binding_for_execution(
            handle_ref,
            tenant_binding=entry.tenant_binding,
            context_version=entry.context_version,
        )
        target = binding.canonical_target
        if isinstance(target, ResolvedSemanticRef):
            cubes.update(target.cube_names)
            labels.append(target.canonical_name)
            if target.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}:
                metrics.append(target)
            elif target.target_kind == SemanticTargetKind.DIMENSION:
                dimensions.append(target)
        elif isinstance(target, ResolvedFilterRef):
            cubes.update(target.cube_names)
            labels.append(f"{target.dimension_name}={target.value}")
            filters.append(target)
        elif isinstance(target, ResolvedPeriod):
            labels.append(target.source_text)
            periods.append(target)
        elif isinstance(target, ResolvedComparison):
            labels.append(target.source_text)
            periods.append(target.base_period)

    unique_metrics = tuple(dict.fromkeys(metrics))
    unique_dimensions = tuple(dict.fromkeys(dimensions))
    unique_filters = tuple(dict.fromkeys(filters))
    unique_periods = tuple(dict.fromkeys(periods))
    topic = None
    if len(cubes) == 1:
        cube = next(iter(cubes))
        topic = TopicFrameV0(
            topic_id=f"report-section:{entry.section.section_id}",
            cube=cube,
            context_version=entry.context_version,
        )

    return ConversationStateV2(
        has_prior_analytical_request=True,
        has_active_result=True,
        topic_labels=tuple(sorted(cubes)),
        focus_labels=tuple(dict.fromkeys(labels)),
        topic=topic,
        focus=FocusStateV0(
            metrics=unique_metrics,
            dimensions=unique_dimensions,
            filters=unique_filters,
            period=unique_periods[0] if len(unique_periods) == 1 else None,
            last_contract_refs=tuple(
                dict.fromkeys(
                    ref
                    for evidence in entry.section.evidence_refs
                    for ref in evidence.query_contract_refs
                )
            ),
        ),
    )


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
            raise MissingReportContinuationContextError(
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
