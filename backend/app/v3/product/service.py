"""Headless Core B product service over sealed authority stores."""
from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, TypeVar

from control_plane.authorize import Principal

from app.v3.claim_lineage import ClaimLineageStore
from app.v3.core_a.action_work import ActionWorkStore
from app.v3.core_a.institutional_memory import InstitutionalMemoryStore
from app.v3.core_a.outcome_observation import OutcomeObservationStore
from app.v3.core_a.watch_signal import WatchSignalStore
from app.v3.decision_adoption import DecisionAdoptionStore
from app.v3.decision_intelligence import DecisionBriefStore
from app.v3.hypothesis_root_cause import HypothesisRootCauseStore
from app.v3.report_document import ReportDocumentStore
from app.v3.research_manager import ResearchReasoningStore
from app.v3.research_product import ResearchAskOrchestrator

from .capabilities import company_context
from .contracts import (
    ArtifactKind,
    ArtifactPage,
    ArtifactRef,
    ArtifactTimeline,
    ClosedLoopProjection,
    CompanyContext,
    OperationTrace,
    ProductArtifact,
    ProductErrorCode,
    TimelineItem,
)
from .errors import ProductError, normalize_owner_error
from . import projections

T = TypeVar("T")

_STAGE_ORDER: dict[ArtifactKind, int] = {
    ArtifactKind.WATCH: 10,
    ArtifactKind.SIGNAL: 20,
    ArtifactKind.RESEARCH: 30,
    ArtifactKind.INVESTIGATION: 40,
    ArtifactKind.EVIDENCE: 50,
    ArtifactKind.EPISTEMIC_ASSESSMENT: 60,
    ArtifactKind.REPORT: 70,
    ArtifactKind.DECISION: 80,
    ArtifactKind.ADOPTION: 90,
    ArtifactKind.ACTION_WORK: 100,
    ArtifactKind.OUTCOME: 110,
    ArtifactKind.MEMORY: 120,
}

_REQUIRED_LOOP = tuple(_STAGE_ORDER)


@dataclass(frozen=True)
class ProductSources:
    research: ResearchAskOrchestrator
    reasoning: ResearchReasoningStore | None = None
    claims: ClaimLineageStore | None = None
    epistemics: HypothesisRootCauseStore | None = None
    reports: ReportDocumentStore | None = None
    decisions: DecisionBriefStore | None = None
    adoptions: DecisionAdoptionStore | None = None
    action_work: ActionWorkStore | None = None
    outcomes: OutcomeObservationStore | None = None
    memory: InstitutionalMemoryStore | None = None
    watch_signal: WatchSignalStore | None = None


def _tenant(principal: Principal) -> str:
    return ResearchAskOrchestrator.tenant_binding_for(principal)


def _subject(principal: Principal) -> str:
    raw=str(principal.user_id).strip()
    if not raw:
        raise ProductError(ProductErrorCode.FORBIDDEN, "authenticated principal is required")
    return raw


def _owner_call(call: Callable[[], T]) -> T:
    try:
        return call()
    except ProductError:
        raise
    except Exception as exc:
        if not hasattr(exc, "code"):
            raise
        raise normalize_owner_error(exc) from exc


def _require(value: T | None, capability: str) -> T:
    if value is None:
        raise ProductError(
            ProductErrorCode.DEFERRED_CAPABILITY,
            f"{capability} owner is not configured in this product runtime",
        )
    return value


def _cursor_encode(offset: int) -> str:
    raw=json.dumps({"offset":offset},sort_keys=True,separators=(",",":"))
    return "cur_"+base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _cursor_decode(cursor: str | None) -> int:
    if cursor is None:
        return 0
    if not cursor.startswith("cur_"):
        raise ProductError(ProductErrorCode.UNAVAILABLE, "invalid product cursor")
    raw=cursor[4:]
    raw += "=" * (-len(raw) % 4)
    try:
        data=json.loads(base64.urlsafe_b64decode(raw.encode()).decode())
        offset=int(data["offset"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ProductError(ProductErrorCode.UNAVAILABLE, "invalid product cursor") from exc
    if offset < 0:
        raise ProductError(ProductErrorCode.UNAVAILABLE, "invalid product cursor")
    return offset


class HeadlessProductService:
    def __init__(self, *, sources: ProductSources) -> None:
        self._s=sources

    def company_context(
        self,
        *,
        principal: Principal,
        analytical_context_available: bool,
        sector_pack_refs: tuple[str, ...] = (),
        entity_refs: tuple[str, ...] = (),
    ) -> CompanyContext:
        return company_context(
            principal=principal,
            analytical_context_available=analytical_context_available,
            sector_pack_refs=sector_pack_refs,
            entity_refs=entity_refs,
        )

    def resume(self, *, ref: ArtifactRef, principal: Principal) -> ProductArtifact:
        kind=ref.kind

        if kind == ArtifactKind.RESEARCH:
            item=_owner_call(lambda: self._s.research.resume_state(session_id=ref.artifact_id,principal=principal))
            return projections.research(item)

        if kind == ArtifactKind.INVESTIGATION:
            reasoning=_require(self._s.reasoning,"investigation")
            session=_owner_call(lambda: self._s.research.resume_state(session_id=ref.artifact_id,principal=principal))
            # Principal was reauthorized on the Research owner before the ledger is projected.
            steps=reasoning.steps(session.session_id)
            tasks=reasoning.tasks(session.session_id)
            return projections.investigation(session=session,steps=steps,tasks=tasks)

        if kind == ArtifactKind.EVIDENCE:
            if not ref.scope_id:
                raise ProductError(
                    ProductErrorCode.UNAVAILABLE,
                    "Evidence resume requires durable Research session scope",
                )
            session=_owner_call(lambda: self._s.research.resume_state(session_id=ref.scope_id,principal=principal))
            matches=tuple(x for x in session.evidence_refs if x.evidence_id==ref.artifact_id)
            if len(matches)!=1:
                raise ProductError(ProductErrorCode.UNAVAILABLE,"artifact unavailable in caller scope")
            return projections.evidence_from_ref(
                ref=matches[0],
                tenant_binding=session.tenant_binding,
                research_session_id=session.session_id,
                created_at=session.updated_at,
            )

        if kind == ArtifactKind.WATCH:
            owner=_require(self._s.watch_signal,"watch")
            item=_owner_call(lambda: owner.load_watch(watch_id=ref.artifact_id,principal=principal))
            return projections.watch(item)

        if kind == ArtifactKind.SIGNAL:
            owner=_require(self._s.watch_signal,"signal")
            item=_owner_call(lambda: owner.load_signal(signal_id=ref.artifact_id,principal=principal))
            state=_owner_call(lambda: owner.currentness(signal_id=ref.artifact_id,principal=principal))
            return projections.signal(item,state)

        if kind == ArtifactKind.EPISTEMIC_ASSESSMENT:
            owner=_require(self._s.epistemics,"epistemic assessment")
            item=_owner_call(lambda: owner.load_assessment(assessment_id=ref.artifact_id,principal=principal))
            return projections.epistemic(item)

        if kind == ArtifactKind.REPORT:
            owner=_require(self._s.reports,"report")
            item=_owner_call(lambda: owner.load(report_id=ref.artifact_id,principal=principal))
            state=_owner_call(lambda: owner.currentness(report_id=ref.artifact_id,principal=principal))
            return projections.report(item,state)

        if kind == ArtifactKind.DECISION:
            owner=_require(self._s.decisions,"decision")
            item=_owner_call(lambda: owner.load(decision_brief_id=ref.artifact_id,principal=principal))
            state=_owner_call(lambda: owner.currentness(decision_brief_id=ref.artifact_id,principal=principal))
            return projections.decision(item,state)

        if kind == ArtifactKind.ADOPTION:
            owner=_require(self._s.adoptions,"adoption")
            item=_owner_call(lambda: owner.load(adoption_id=ref.artifact_id,principal=principal))
            state=_owner_call(lambda: owner.currentness(adoption_id=ref.artifact_id,principal=principal))
            return projections.adoption(item,state)

        if kind == ArtifactKind.ACTION_WORK:
            owner=_require(self._s.action_work,"action work")
            item=_owner_call(lambda: owner.load(action_work_id=ref.artifact_id,principal=principal))
            state=_owner_call(lambda: owner.currentness(action_work_id=ref.artifact_id,principal=principal))
            return projections.action_work(item,state)

        if kind == ArtifactKind.OUTCOME:
            owner=_require(self._s.outcomes,"outcome")
            item=_owner_call(lambda: owner.load(outcome_id=ref.artifact_id,principal=principal))
            state=_owner_call(lambda: owner.currentness(outcome_id=ref.artifact_id,principal=principal))
            return projections.outcome(item,state)

        if kind == ArtifactKind.MEMORY:
            owner=_require(self._s.memory,"memory")
            item=_owner_call(lambda: owner.load(memory_id=ref.artifact_id,principal=principal))
            state=_owner_call(lambda: owner.currentness(memory_id=ref.artifact_id,principal=principal))
            return projections.memory(item,state)

        raise ProductError(ProductErrorCode.UNAVAILABLE,"artifact unavailable in caller scope")

    def page(
        self,
        *,
        refs: tuple[ArtifactRef, ...],
        principal: Principal,
        limit: int = 25,
        cursor: str | None = None,
    ) -> ArtifactPage:
        if limit < 1 or limit > 100:
            raise ProductError(ProductErrorCode.UNAVAILABLE,"invalid product page size")
        start=_cursor_decode(cursor)
        visible=tuple(self.resume(ref=ref,principal=principal) for ref in refs)
        page=visible[start:start+limit]
        next_offset=start+len(page)
        next_cursor=_cursor_encode(next_offset) if next_offset < len(visible) else None
        return ArtifactPage(items=page,next_cursor=next_cursor,total_visible=len(visible))

    def timeline(
        self,
        *,
        context_id: str,
        refs: tuple[ArtifactRef, ...],
        principal: Principal,
        limit: int = 100,
        cursor: str | None = None,
    ) -> ArtifactTimeline:
        if limit < 1 or limit > 200:
            raise ProductError(ProductErrorCode.UNAVAILABLE,"invalid timeline page size")
        artifacts=tuple(self.resume(ref=ref,principal=principal) for ref in refs)
        artifacts=tuple(sorted(
            artifacts,
            key=lambda item:(
                item.header.created_at or datetime.min.replace(tzinfo=timezone.utc),
                _STAGE_ORDER[item.header.kind],
                item.header.artifact_id,
            ),
        ))
        items=tuple(
            TimelineItem(
                ordinal=index+1,
                ref=ArtifactRef(kind=item.header.kind,artifact_id=item.header.artifact_id),
                currentness=item.header.currentness,
                occurred_at=item.header.created_at,
                terminal_state=item.header.terminal_state,
                lineage_refs=item.header.lineage_refs,
            )
            for index,item in enumerate(artifacts)
        )
        start=_cursor_decode(cursor)
        page=items[start:start+limit]
        next_offset=start+len(page)
        return ArtifactTimeline(
            context_id=context_id,
            items=page,
            next_cursor=_cursor_encode(next_offset) if next_offset<len(items) else None,
        )

    def trace(
        self,
        *,
        principal: Principal,
        operation: str,
        owner_calls: tuple[str, ...],
        artifact_ids: tuple[str, ...],
        terminal_state: str,
        failure_class: ProductErrorCode | None = None,
        correlation_id: str | None = None,
    ) -> OperationTrace:
        tenant=_tenant(principal)
        subject=_subject(principal)
        if correlation_id is None:
            raw=json.dumps(
                {
                    "tenant":tenant,
                    "principal":subject,
                    "operation":operation,
                    "artifact_ids":artifact_ids,
                    "terminal_state":terminal_state,
                },
                sort_keys=True,
                separators=(",",":"),
            )
            correlation_id="corr_"+hashlib.sha256(raw.encode()).hexdigest()[:24]
        return OperationTrace(
            correlation_id=correlation_id,
            tenant_binding=tenant,
            principal_subject=subject,
            operation=operation,
            owner_calls=owner_calls,
            artifact_ids=artifact_ids,
            terminal_state=terminal_state,
            failure_class=failure_class,
        )

    def closed_loop(
        self,
        *,
        principal: Principal,
        analytical_context_available: bool,
        refs: tuple[ArtifactRef, ...],
        entity_refs: tuple[str, ...] = (),
        sector_pack_refs: tuple[str, ...] = (),
        correlation_id: str | None = None,
    ) -> ClosedLoopProjection:
        artifacts=tuple(self.resume(ref=ref,principal=principal) for ref in refs)
        kinds=tuple(dict.fromkeys(item.header.kind for item in artifacts))
        missing=tuple(kind for kind in _REQUIRED_LOOP if kind not in kinds)
        if missing:
            code=(
                ProductErrorCode.INSUFFICIENT_EVIDENCE
                if ArtifactKind.EVIDENCE in missing
                else ProductErrorCode.INCONCLUSIVE
            )
            raise ProductError(
                code,
                "closed-loop projection is incomplete: "
                + ",".join(kind.value for kind in missing),
            )
        context=self.company_context(
            principal=principal,
            analytical_context_available=analytical_context_available,
            sector_pack_refs=sector_pack_refs,
            entity_refs=entity_refs,
        )
        timeline=self.timeline(
            context_id=context.context_id,
            refs=refs,
            principal=principal,
        )
        trace=self.trace(
            principal=principal,
            operation="closed_loop_projection",
            owner_calls=tuple(item.header.kind.value for item in artifacts),
            artifact_ids=tuple(item.header.artifact_id for item in artifacts),
            terminal_state="GREEN",
            correlation_id=correlation_id,
        )
        return ClosedLoopProjection(
            context=context,
            stages=artifacts,
            timeline=timeline,
            trace=trace,
            complete_stage_kinds=kinds,
        )
