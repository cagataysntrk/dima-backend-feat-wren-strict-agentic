"""Pure product projections over sealed Dima domain objects."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.v3.claim_lineage import ResearchClaim
from app.v3.core_a.action_work import ActionWork
from app.v3.core_a.institutional_memory import InstitutionalMemoryEntry
from app.v3.core_a.outcome_observation import OutcomeObservation
from app.v3.core_a.watch_signal import Signal, Watch
from app.v3.decision_adoption import DecisionAdoption
from app.v3.decision_intelligence import DecisionBrief
from app.v3.evidence import EvidenceArtifact
from app.v3.hypothesis_root_cause import RootCauseAssessmentView
from app.v3.report_document import ReportDocument
from app.v3.research import EvidenceRef, ResearchSession
from app.v3.research_manager import ResearchInvestigationTask, ResearchReasoningStep

from .contracts import (
    ActionWorkDTO,
    AdoptionDTO,
    ArtifactHeader,
    ArtifactKind,
    ArtifactRef,
    DecisionDTO,
    EpistemicAssessmentDTO,
    EvidenceDTO,
    InvestigationDTO,
    MemoryDTO,
    OutcomeDTO,
    ProductCurrentness,
    ReportDTO,
    ResearchDTO,
    SignalDTO,
    WatchDTO,
)


def currentness(value: object | None) -> ProductCurrentness:
    if value is None:
        return ProductCurrentness.CURRENT
    raw = str(getattr(value, "value", value)).upper()
    if "SUPERSEDED" in raw:
        return ProductCurrentness.SUPERSEDED
    if "STALE" in raw:
        return ProductCurrentness.STALE
    if "HISTORICAL" in raw:
        return ProductCurrentness.HISTORICAL
    if "INCONCLUSIVE" in raw:
        return ProductCurrentness.INCONCLUSIVE
    if raw in {"CURRENT", "CURRENT_CONTEXT"}:
        return ProductCurrentness.CURRENT
    return ProductCurrentness.UNKNOWN


def _ref(kind: ArtifactKind, artifact_id: str, scope_id: str | None = None) -> ArtifactRef:
    return ArtifactRef(kind=kind, artifact_id=artifact_id, scope_id=scope_id)


def _header(
    *,
    kind: ArtifactKind,
    artifact_id: str,
    tenant_binding: str,
    state: object | None = None,
    created_at: datetime | None = None,
    revision: int | None = None,
    lineage_refs: Iterable[ArtifactRef] = (),
    terminal_state: str | None = None,
    fingerprint: str | None = None,
) -> ArtifactHeader:
    return ArtifactHeader(
        kind=kind,
        artifact_id=artifact_id,
        tenant_binding=tenant_binding,
        currentness=currentness(state),
        deep_link_id=f"artifact:{kind.value.lower()}:{artifact_id}",
        created_at=created_at,
        revision=revision,
        lineage_refs=tuple(lineage_refs),
        terminal_state=terminal_state,
        fingerprint=fingerprint,
    )


def research(session: ResearchSession) -> ResearchDTO:
    return ResearchDTO(
        header=_header(
            kind=ArtifactKind.RESEARCH,
            artifact_id=session.session_id,
            tenant_binding=session.tenant_binding,
            created_at=session.created_at,
            revision=session.revision,
            terminal_state=session.stopping.status.value,
            fingerprint=session.fingerprint,
        ),
        objective=session.objective,
        stopping_status=session.stopping.status.value,
        stopping_reason=session.stopping.reason,
        obligation_states=tuple(
            (item.obligation_id, item.state.value) for item in session.obligations
        ),
        evidence_ids=tuple(item.evidence_id for item in session.evidence_refs),
        limitation_codes=tuple(item.code for item in session.limitations),
    )


def watch(item: Watch) -> WatchDTO:
    return WatchDTO(
        header=_header(
            kind=ArtifactKind.WATCH,
            artifact_id=item.watch_id,
            tenant_binding=item.tenant_binding,
            created_at=item.created_at,
            fingerprint=item.watch_fingerprint,
        ),
        title=item.title,
        kind=item.kind.value,
        source_contract_ref=item.source_contract_ref,
        criterion_ref=item.criterion_ref,
        entity_refs=item.entity_refs,
        metric_refs=item.metric_refs,
    )


def signal(item: Signal, state: object | None = None) -> SignalDTO:
    lineage = [_ref(ArtifactKind.WATCH, item.watch_id)]
    if item.research_session_id:
        lineage.append(_ref(ArtifactKind.RESEARCH, item.research_session_id))
    if item.action_work_id:
        lineage.append(_ref(ArtifactKind.ACTION_WORK, item.action_work_id))
    if item.memory_entry_id:
        lineage.append(_ref(ArtifactKind.MEMORY, item.memory_entry_id))
    return SignalDTO(
        header=_header(
            kind=ArtifactKind.SIGNAL,
            artifact_id=item.signal_id,
            tenant_binding=item.tenant_binding,
            state=state,
            created_at=item.created_at,
            revision=item.revision,
            lineage_refs=lineage,
            terminal_state=item.status.value,
            fingerprint=item.signal_fingerprint,
        ),
        watch_id=item.watch_id,
        severity=item.severity.value,
        status=item.status.value,
        business_significance=item.business_significance,
        source_ref=item.source_ref,
        research_session_id=item.research_session_id,
        action_work_id=item.action_work_id,
        memory_entry_id=item.memory_entry_id,
    )


def investigation(
    *,
    session: ResearchSession,
    steps: tuple[ResearchReasoningStep, ...],
    tasks: tuple[ResearchInvestigationTask, ...],
) -> InvestigationDTO:
    active = tuple(
        item.task_id
        for item in tasks
        if str(item.status.value) not in {"COMPLETED", "CANCELLED"}
    )
    stops = tuple(
        str(item.stop_reason.value)
        for item in steps
        if item.stop_reason is not None
    )
    return InvestigationDTO(
        header=_header(
            kind=ArtifactKind.INVESTIGATION,
            artifact_id=session.session_id,
            tenant_binding=session.tenant_binding,
            created_at=steps[0].created_at if steps else session.created_at,
            revision=session.revision,
            lineage_refs=(_ref(ArtifactKind.RESEARCH, session.session_id),),
            terminal_state=session.stopping.status.value,
        ),
        research_session_id=session.session_id,
        reasoning_step_ids=tuple(item.step_id for item in steps),
        task_ids=tuple(item.task_id for item in tasks),
        active_task_ids=active,
        stop_reasons=stops,
    )


def evidence_from_ref(
    *,
    ref: EvidenceRef,
    tenant_binding: str,
    research_session_id: str,
    created_at: datetime | None = None,
) -> EvidenceDTO:
    return EvidenceDTO(
        header=_header(
            kind=ArtifactKind.EVIDENCE,
            artifact_id=ref.evidence_id,
            tenant_binding=tenant_binding,
            created_at=created_at,
            lineage_refs=(
                _ref(ArtifactKind.RESEARCH, research_session_id),
            ),
            terminal_state="VERIFIED",
        ),
        authority_id=ref.authority_id,
        obligation_ids=(ref.obligation_id,),
        evidence_kind="VERIFIED_RESEARCH_EVIDENCE",
        state="VERIFIED",
        receipt_refs=(ref.receipt_id,),
        limitations=(),
    )


def evidence_artifact(
    *,
    item: EvidenceArtifact,
    tenant_binding: str,
    research_session_id: str | None = None,
    created_at: datetime | None = None,
) -> EvidenceDTO:
    lineage = (
        (_ref(ArtifactKind.RESEARCH, research_session_id),)
        if research_session_id
        else ()
    )
    return EvidenceDTO(
        header=_header(
            kind=ArtifactKind.EVIDENCE,
            artifact_id=item.artifact_id,
            tenant_binding=tenant_binding,
            created_at=created_at,
            lineage_refs=lineage,
            terminal_state=item.state.value,
        ),
        authority_id=item.authority_id,
        obligation_ids=item.obligation_ids,
        evidence_kind=item.evidence_kind,
        state=item.state.value,
        receipt_refs=item.query_receipt_refs,
        limitations=item.limitations,
    )


def epistemic(item: RootCauseAssessmentView) -> EpistemicAssessmentDTO:
    return EpistemicAssessmentDTO(
        header=_header(
            kind=ArtifactKind.EPISTEMIC_ASSESSMENT,
            artifact_id=item.assessment_id,
            tenant_binding=item.tenant_binding,
            created_at=item.created_at,
            lineage_refs=(
                _ref(ArtifactKind.RESEARCH, item.research_session_id),
            ),
            terminal_state=item.aggregate_outcome.value,
            fingerprint=item.assessment_fingerprint,
        ),
        research_session_id=item.research_session_id,
        obligation_id=item.obligation_id,
        aggregate_outcome=item.aggregate_outcome.value,
        root_cause_hypothesis_ids=item.root_cause_hypothesis_ids,
        candidate_hypothesis_ids=tuple(x.hypothesis_id for x in item.candidates),
        limitations=item.limitations,
    )


def report(item: ReportDocument, state: object | None = None) -> ReportDTO:
    return ReportDTO(
        header=_header(
            kind=ArtifactKind.REPORT,
            artifact_id=item.report_id,
            tenant_binding=item.tenant_binding,
            state=state,
            created_at=item.created_at,
            revision=item.revision,
            lineage_refs=(
                _ref(ArtifactKind.RESEARCH, item.research_session_id),
            ),
            fingerprint=item.report_fingerprint,
        ),
        research_session_id=item.research_session_id,
        report_key=item.report_key,
        statement_ids=tuple(x.statement_id for x in item.statements),
        limitation_ids=tuple(x.limitation_id for x in item.limitations),
        coverage=tuple(
            (x.obligation_id, x.coverage_status.value) for x in item.coverage
        ),
    )


def decision(item: DecisionBrief, state: object | None = None) -> DecisionDTO:
    return DecisionDTO(
        header=_header(
            kind=ArtifactKind.DECISION,
            artifact_id=item.decision_brief_id,
            tenant_binding=item.tenant_binding,
            state=state,
            created_at=item.created_at,
            revision=item.revision,
            lineage_refs=(_ref(ArtifactKind.REPORT, item.report_id),),
            fingerprint=item.brief_fingerprint,
        ),
        report_id=item.report_id,
        brief_key=item.brief_key,
        objective_text=item.objective.objective_text,
        option_ids=tuple(x.option_id for x in item.options),
        recommended_option_ids=item.recommendation.recommended_option_ids,
        limitation_ids=tuple(x.limitation_id for x in item.limitations),
    )


def adoption(item: DecisionAdoption, state: object | None = None) -> AdoptionDTO:
    return AdoptionDTO(
        header=_header(
            kind=ArtifactKind.ADOPTION,
            artifact_id=item.adoption_id,
            tenant_binding=item.tenant_binding,
            state=state,
            created_at=item.recorded_at,
            lineage_refs=(
                _ref(ArtifactKind.DECISION, item.decision_brief_id),
            ),
            terminal_state=item.disposition.value,
            fingerprint=item.adoption_fingerprint,
        ),
        decision_brief_id=item.decision_brief_id,
        disposition=item.disposition.value,
        selected_option_ids=item.selected_option_ids,
        actor_user_id=item.actor_user_id,
        human_conditions=item.human_conditions,
    )


def action_work(item: ActionWork, state: object | None = None) -> ActionWorkDTO:
    return ActionWorkDTO(
        header=_header(
            kind=ArtifactKind.ACTION_WORK,
            artifact_id=item.action_work_id,
            tenant_binding=item.tenant_binding,
            state=state,
            created_at=item.created_at,
            revision=item.revision,
            lineage_refs=(
                _ref(ArtifactKind.ADOPTION, item.decision_adoption_id),
                _ref(ArtifactKind.DECISION, item.decision_brief_id),
            ),
            terminal_state=item.status.value,
            fingerprint=item.work_fingerprint,
        ),
        decision_adoption_id=item.decision_adoption_id,
        title=item.title,
        owner_user_id=item.owner_user_id,
        due_at=item.due_at,
        status=item.status.value,
        blocker_reason=item.blocker_reason,
        completion_reference=item.completion_reference,
    )


def outcome(item: OutcomeObservation, state: object | None = None) -> OutcomeDTO:
    lineage = [
        _ref(ArtifactKind.ACTION_WORK, item.action_work_id),
        _ref(ArtifactKind.DECISION, item.decision_brief_id),
        _ref(ArtifactKind.ADOPTION, item.decision_adoption_id),
    ]
    if item.report_id:
        lineage.append(_ref(ArtifactKind.REPORT, item.report_id))
    return OutcomeDTO(
        header=_header(
            kind=ArtifactKind.OUTCOME,
            artifact_id=item.outcome_id,
            tenant_binding=item.tenant_binding,
            state=state,
            created_at=item.observed_at,
            lineage_refs=lineage,
            terminal_state=item.classification.value,
            fingerprint=item.outcome_fingerprint,
        ),
        action_work_id=item.action_work_id,
        classification=item.classification.value,
        baseline_definition=item.baseline_definition,
        baseline_window=item.baseline_window,
        observation_window=item.observation_window,
        evidence_ids=tuple(x.evidence_id for x in item.evidence),
        claim_ids=item.claim_ids,
        report_id=item.report_id,
        limitations=item.limitations,
    )


def memory(item: InstitutionalMemoryEntry, state: object | None = None) -> MemoryDTO:
    kind_map = {
        "ACTION_WORK": ArtifactKind.ACTION_WORK,
        "OUTCOME": ArtifactKind.OUTCOME,
        "DECISION_ADOPTION": ArtifactKind.ADOPTION,
        "DECISION_BRIEF": ArtifactKind.DECISION,
        "REPORT": ArtifactKind.REPORT,
    }
    lineage = tuple(
        ArtifactRef(kind=kind_map[ref.kind.value], artifact_id=ref.artifact_id)
        for ref in item.source_refs
        if ref.kind.value in kind_map
    )
    return MemoryDTO(
        header=_header(
            kind=ArtifactKind.MEMORY,
            artifact_id=item.memory_id,
            tenant_binding=item.tenant_binding,
            state=state,
            created_at=item.created_at,
            lineage_refs=lineage,
            fingerprint=item.memory_fingerprint,
        ),
        role=item.role.value,
        problem_type=item.problem_type,
        domain=item.domain,
        entity_refs=item.entity_refs,
        metric_refs=item.metric_refs,
        summary=item.summary,
        limitations=item.limitations,
    )
