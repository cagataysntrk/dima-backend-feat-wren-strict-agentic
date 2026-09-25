"""P17 durable Research investigation manager.

P17 owns bounded investigation reasoning and restart durability only. Metabase/Metabot
remain the analytical owners; P14/P15/P16 remain sealed authorities for execution,
Research material, and claim/Evidence epistemics.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.claim_lineage import ClaimFreshness, ClaimLineageStore
from app.v3.research import ResearchManager, ResearchSession
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import (
    ResearchClaimRecord,
    ResearchExplorationMaterial,
    ResearchInvestigationTaskRecord,
    ResearchReasoningStepRecord,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchManagerMaturationError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ManagerAction(StrEnum):
    EXPLORE_NATIVE = "EXPLORE_NATIVE"
    FORM_CLAIM = "FORM_CLAIM"
    SEEK_COUNTER_EVIDENCE = "SEEK_COUNTER_EVIDENCE"
    STOP = "STOP"


class ManagerStopReason(StrEnum):
    OBJECTIVE_SATISFIED = "OBJECTIVE_SATISFIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    NO_PROGRESS = "NO_PROGRESS"
    BLOCKED = "BLOCKED"


class ReasoningStepStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    NO_PROGRESS = "NO_PROGRESS"


class InvestigationTaskStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    LIMITED = "LIMITED"


class ResearchReasoningBudget(Frozen):
    max_reasoning_steps: int = Field(default=8, ge=1, le=64)
    max_followup_native_turns: int = Field(default=4, ge=0, le=32)
    max_counter_evidence_attempts: int = Field(default=2, ge=0, le=16)


class ProposedClaimDraft(Frozen):
    claim_text: str = Field(min_length=1)
    proposition: dict[str, Any]
    scope: dict[str, Any]
    freshness: ClaimFreshness
    origin_material_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def structured(self):
        if not self.proposition:
            raise ValueError("FORM_CLAIM requires a structured proposition")
        if not self.scope:
            raise ValueError("FORM_CLAIM requires an explicit scope")
        return self


class ManagerProposal(Frozen):
    proposal_id: str = Field(min_length=1, max_length=160)
    source_revision: int = Field(ge=1)
    target_parent_obligation: str = Field(min_length=1)
    action: ManagerAction
    # Stable manager-supplied identity for the bounded investigative target.
    # This, rather than free-form prose, participates in no-progress identity.
    objective_key: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
    bounded_objective: str | None = Field(default=None, max_length=2000)
    rationale: str = Field(min_length=1, max_length=4000)
    inspected_evidence_refs: tuple[str, ...] = ()
    inspected_claim_refs: tuple[str, ...] = ()
    inspected_material_refs: tuple[str, ...] = ()
    expected_information_gain: str | None = Field(default=None, max_length=2000)
    stop_reason: ManagerStopReason | None = None
    counter_to_claim_id: str | None = None
    claim: ProposedClaimDraft | None = None

    @model_validator(mode="after")
    def coherent(self):
        for name, refs in (
            ("Evidence", self.inspected_evidence_refs),
            ("claim", self.inspected_claim_refs),
            ("material", self.inspected_material_refs),
        ):
            if len(refs) != len(set(refs)):
                raise ValueError(f"{name} refs must be unique")

        if self.action == ManagerAction.STOP:
            if self.stop_reason is None:
                raise ValueError("STOP requires stop_reason")
            if self.claim is not None or self.counter_to_claim_id is not None:
                raise ValueError("STOP cannot carry follow-up payload")
            return self

        if not self.bounded_objective or not self.bounded_objective.strip():
            raise ValueError("non-STOP proposal requires bounded_objective")
        if (
            not self.expected_information_gain
            or not self.expected_information_gain.strip()
        ):
            raise ValueError("non-STOP proposal requires expected_information_gain")
        if self.stop_reason is not None:
            raise ValueError("non-STOP proposal cannot carry stop_reason")

        if self.action == ManagerAction.FORM_CLAIM and self.claim is None:
            raise ValueError("FORM_CLAIM requires claim draft")
        if self.action != ManagerAction.FORM_CLAIM and self.claim is not None:
            raise ValueError("claim draft is only valid for FORM_CLAIM")

        if self.action == ManagerAction.SEEK_COUNTER_EVIDENCE:
            if self.counter_to_claim_id is None:
                raise ValueError(
                    "SEEK_COUNTER_EVIDENCE requires counter_to_claim_id"
                )
        elif self.counter_to_claim_id is not None:
            raise ValueError(
                "counter_to_claim_id is only valid for SEEK_COUNTER_EVIDENCE"
            )
        return self


class ParentObligationView(Frozen):
    obligation_id: str
    objective: str
    state: str


class ClaimView(Frozen):
    claim_id: str
    obligation_id: str
    epistemic_state: str
    origin_material_refs: tuple[str, ...] = ()
    evidence_relations: tuple[str, ...] = ()


class ResearchManagerSnapshot(Frozen):
    research_session_id: str
    research_authority_id: str
    source_revision: int
    objective: str
    parent_obligations: tuple[ParentObligationView, ...]
    evidence_refs: tuple[str, ...]
    material_refs: tuple[str, ...]
    claims: tuple[ClaimView, ...]
    limitation_refs: tuple[str, ...]
    completed_reasoning_steps: tuple[str, ...]
    pending_reasoning_steps: tuple[str, ...]
    remaining_reasoning_steps: int = Field(ge=0)
    remaining_followup_native_turns: int = Field(ge=0)
    remaining_counter_evidence_attempts: int = Field(ge=0)
    terminal_stop_reason: ManagerStopReason | None = None

    @property
    def fingerprint(self) -> str:
        return _json(
            self.model_dump(mode="json"),
            code="P17_SNAPSHOT_NOT_CANONICAL",
        )[1]


class ResearchReasoningStep(Frozen):
    step_id: str = Field(pattern=r"^rrs_[a-f0-9]{24}$")
    research_session_id: str
    source_revision: int
    source_snapshot_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    parent_obligation_id: str
    proposal_id: str
    action: ManagerAction
    objective_key: str
    bounded_objective: str | None
    rationale: str
    inspected_evidence_refs: tuple[str, ...]
    inspected_claim_refs: tuple[str, ...]
    inspected_material_refs: tuple[str, ...]
    proposal_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    status: ReasoningStepStatus
    stop_reason: ManagerStopReason | None = None
    result_refs: tuple[str, ...] = ()
    created_at: datetime
    completed_at: datetime | None = None


class ResearchInvestigationTask(Frozen):
    task_id: str = Field(pattern=r"^rit_[a-f0-9]{24}$")
    research_session_id: str
    reasoning_step_id: str
    parent_obligation_id: str
    bounded_objective: str
    counter_to_claim_id: str | None = None
    status: InvestigationTaskStatus
    native_execution_refs: tuple[str, ...] = ()
    material_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    created_at: datetime
    completed_at: datetime | None = None


class FollowupResult(Frozen):
    native_execution_refs: tuple[str, ...] = ()
    material_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


class ResearchProposalManager(Protocol):
    def propose(self, snapshot: ResearchManagerSnapshot) -> ManagerProposal: ...


class ResearchFollowupExecutor(Protocol):
    """Adapter seam to the single sealed P14 native-direct mechanics."""

    def execute(
        self,
        *,
        session: ResearchSession,
        step: ResearchReasoningStep,
        task: ResearchInvestigationTask,
        principal: Principal,
    ) -> FollowupResult: ...


def _now(value: datetime | None = None) -> datetime:
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("P17 timestamps must be timezone-aware")
    return value


def _json(value: Any, *, code: str) -> tuple[str, str]:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
    except (TypeError, ValueError) as exc:
        raise ResearchManagerMaturationError(
            code,
            "value is not deterministic JSON",
        ) from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_list(raw: str, *, code: str) -> tuple[str, ...]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ResearchManagerMaturationError(
            code,
            "persisted JSON is invalid",
        ) from exc
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise ResearchManagerMaturationError(
            code,
            "persisted list has invalid shape",
        )
    return tuple(value)


def _id(prefix: str) -> str:
    return prefix + uuid4().hex[:24]


def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise ResearchManagerMaturationError(
        "P17_TENANT_REQUIRED",
        "Research reasoning requires an explicit tenant binding",
    )


class ResearchReasoningStore:
    """Durable P17 reasoning/task ledger. It never mutates P14 obligations."""

    def __init__(self, db_engine=None) -> None:
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _step(record: ResearchReasoningStepRecord) -> ResearchReasoningStep:
        return ResearchReasoningStep(
            step_id=record.step_id,
            research_session_id=record.session_id,
            source_revision=record.source_revision,
            source_snapshot_fingerprint=record.source_snapshot_fingerprint,
            parent_obligation_id=record.parent_obligation_id,
            proposal_id=record.proposal_id,
            action=ManagerAction(record.action),
            objective_key=record.objective_key,
            bounded_objective=record.bounded_objective,
            rationale=record.rationale,
            inspected_evidence_refs=_load_list(
                record.inspected_evidence_refs_json,
                code="P17_EVIDENCE_REFS_INVALID",
            ),
            inspected_claim_refs=_load_list(
                record.inspected_claim_refs_json,
                code="P17_CLAIM_REFS_INVALID",
            ),
            inspected_material_refs=_load_list(
                record.inspected_material_refs_json,
                code="P17_MATERIAL_REFS_INVALID",
            ),
            proposal_fingerprint=record.proposal_fingerprint,
            status=ReasoningStepStatus(record.status),
            stop_reason=(
                ManagerStopReason(record.stop_reason)
                if record.stop_reason is not None
                else None
            ),
            result_refs=_load_list(
                record.result_refs_json,
                code="P17_RESULT_REFS_INVALID",
            ),
            created_at=record.created_at,
            completed_at=record.completed_at,
        )

    @staticmethod
    def _task(
        record: ResearchInvestigationTaskRecord,
    ) -> ResearchInvestigationTask:
        return ResearchInvestigationTask(
            task_id=record.task_id,
            research_session_id=record.session_id,
            reasoning_step_id=record.reasoning_step_id,
            parent_obligation_id=record.parent_obligation_id,
            bounded_objective=record.bounded_objective,
            counter_to_claim_id=record.counter_to_claim_id,
            status=InvestigationTaskStatus(record.status),
            native_execution_refs=_load_list(
                record.native_execution_refs_json,
                code="P17_NATIVE_REFS_INVALID",
            ),
            material_refs=_load_list(
                record.material_refs_json,
                code="P17_TASK_MATERIAL_REFS_INVALID",
            ),
            evidence_refs=_load_list(
                record.evidence_refs_json,
                code="P17_TASK_EVIDENCE_REFS_INVALID",
            ),
            created_at=record.created_at,
            completed_at=record.completed_at,
        )

    def proposal(self, step_id: str) -> ManagerProposal:
        with Session(self._engine) as db:
            record = db.get(ResearchReasoningStepRecord, step_id)
            if record is None:
                raise ResearchManagerMaturationError(
                    "P17_STEP_NOT_FOUND",
                    step_id,
                )
            try:
                return ManagerProposal.model_validate_json(record.proposal_json)
            except ValueError as exc:
                raise ResearchManagerMaturationError(
                    "P17_PROPOSAL_PERSISTENCE_INVALID",
                    step_id,
                ) from exc

    def steps(self, session_id: str) -> tuple[ResearchReasoningStep, ...]:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(ResearchReasoningStepRecord)
                    .where(ResearchReasoningStepRecord.session_id == session_id)
                    .order_by(
                        ResearchReasoningStepRecord.created_at,
                        ResearchReasoningStepRecord.step_id,
                    )
                ).all()
            )
        return tuple(self._step(x) for x in rows)

    def tasks(self, session_id: str) -> tuple[ResearchInvestigationTask, ...]:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(ResearchInvestigationTaskRecord)
                    .where(
                        ResearchInvestigationTaskRecord.session_id == session_id
                    )
                    .order_by(
                        ResearchInvestigationTaskRecord.created_at,
                        ResearchInvestigationTaskRecord.task_id,
                    )
                ).all()
            )
        return tuple(self._task(x) for x in rows)

    def task_for_step(self, step_id: str) -> ResearchInvestigationTask | None:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(ResearchInvestigationTaskRecord).where(
                        ResearchInvestigationTaskRecord.reasoning_step_id
                        == step_id
                    )
                ).all()
            )
        if len(rows) > 1:
            raise ResearchManagerMaturationError(
                "P17_STEP_TASK_DUPLICATE",
                step_id,
            )
        return self._task(rows[0]) if rows else None

    def create_step(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        proposal: ManagerProposal,
        proposal_fingerprint: str,
        status: ReasoningStepStatus = ReasoningStepStatus.PENDING,
        stop_reason: ManagerStopReason | None = None,
        now: datetime | None = None,
    ) -> ResearchReasoningStep:
        when = _now(now)
        evidence_json, _ = _json(
            sorted(proposal.inspected_evidence_refs),
            code="P17_EVIDENCE_REFS_NOT_CANONICAL",
        )
        claim_json, _ = _json(
            sorted(proposal.inspected_claim_refs),
            code="P17_CLAIM_REFS_NOT_CANONICAL",
        )
        material_json, _ = _json(
            sorted(proposal.inspected_material_refs),
            code="P17_MATERIAL_REFS_NOT_CANONICAL",
        )
        result_json, _ = _json(
            [],
            code="P17_RESULT_REFS_NOT_CANONICAL",
        )
        record = ResearchReasoningStepRecord(
            step_id=_id("rrs_"),
            session_id=session.session_id,
            source_revision=proposal.source_revision,
            source_snapshot_fingerprint=snapshot.fingerprint,
            parent_obligation_id=proposal.target_parent_obligation,
            proposal_id=proposal.proposal_id,
            proposal_json=proposal.model_dump_json(),
            action=proposal.action.value,
            objective_key=proposal.objective_key,
            bounded_objective=proposal.bounded_objective,
            rationale=proposal.rationale,
            inspected_evidence_refs_json=evidence_json,
            inspected_claim_refs_json=claim_json,
            inspected_material_refs_json=material_json,
            proposal_fingerprint=proposal_fingerprint,
            status=status.value,
            stop_reason=(
                stop_reason.value if stop_reason is not None else None
            ),
            result_refs_json=result_json,
            created_at=when,
            completed_at=(
                when if status != ReasoningStepStatus.PENDING else None
            ),
        )
        with Session(self._engine) as db:
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._step(record)

    def create_task(
        self,
        *,
        session: ResearchSession,
        step: ResearchReasoningStep,
        proposal: ManagerProposal,
        now: datetime | None = None,
    ) -> ResearchInvestigationTask:
        if not proposal.bounded_objective:
            raise ResearchManagerMaturationError(
                "P17_TASK_OBJECTIVE_REQUIRED",
                "follow-up task requires bounded objective",
            )
        empty, _ = _json([], code="P17_TASK_REFS_NOT_CANONICAL")
        record = ResearchInvestigationTaskRecord(
            task_id=_id("rit_"),
            session_id=session.session_id,
            reasoning_step_id=step.step_id,
            parent_obligation_id=proposal.target_parent_obligation,
            bounded_objective=proposal.bounded_objective,
            counter_to_claim_id=proposal.counter_to_claim_id,
            status=InvestigationTaskStatus.PENDING.value,
            native_execution_refs_json=empty,
            material_refs_json=empty,
            evidence_refs_json=empty,
            created_at=_now(now),
            completed_at=None,
        )
        with Session(self._engine) as db:
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._task(record)

    def complete_task(
        self,
        task_id: str,
        *,
        result: FollowupResult,
        now: datetime | None = None,
    ) -> ResearchInvestigationTask:
        native, _ = _json(
            sorted(set(result.native_execution_refs)),
            code="P17_NATIVE_REFS_NOT_CANONICAL",
        )
        material, _ = _json(
            sorted(set(result.material_refs)),
            code="P17_TASK_MATERIAL_REFS_NOT_CANONICAL",
        )
        evidence, _ = _json(
            sorted(set(result.evidence_refs)),
            code="P17_TASK_EVIDENCE_REFS_NOT_CANONICAL",
        )
        with Session(self._engine) as db:
            record = db.get(ResearchInvestigationTaskRecord, task_id)
            if record is None:
                raise ResearchManagerMaturationError(
                    "P17_TASK_NOT_FOUND",
                    task_id,
                )
            if record.status != InvestigationTaskStatus.PENDING.value:
                raise ResearchManagerMaturationError(
                    "P17_TASK_NOT_PENDING",
                    task_id,
                )
            record.status = InvestigationTaskStatus.COMPLETED.value
            record.native_execution_refs_json = native
            record.material_refs_json = material
            record.evidence_refs_json = evidence
            record.completed_at = _now(now)
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._task(record)

    def complete_step(
        self,
        step_id: str,
        *,
        result_refs: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> ResearchReasoningStep:
        raw, _ = _json(
            sorted(set(result_refs)),
            code="P17_RESULT_REFS_NOT_CANONICAL",
        )
        with Session(self._engine) as db:
            record = db.get(ResearchReasoningStepRecord, step_id)
            if record is None:
                raise ResearchManagerMaturationError(
                    "P17_STEP_NOT_FOUND",
                    step_id,
                )
            if record.status != ReasoningStepStatus.PENDING.value:
                raise ResearchManagerMaturationError(
                    "P17_STEP_NOT_PENDING",
                    step_id,
                )
            record.status = ReasoningStepStatus.COMPLETED.value
            record.result_refs_json = raw
            record.completed_at = _now(now)
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._step(record)

    def prior_fingerprint(
        self,
        *,
        session_id: str,
        proposal_fingerprint: str,
    ) -> ResearchReasoningStep | None:
        with Session(self._engine) as db:
            record = db.exec(
                select(ResearchReasoningStepRecord)
                .where(ResearchReasoningStepRecord.session_id == session_id)
                .where(
                    ResearchReasoningStepRecord.proposal_fingerprint
                    == proposal_fingerprint
                )
                .order_by(ResearchReasoningStepRecord.created_at.desc())
            ).first()
        return self._step(record) if record is not None else None


class ResearchInvestigationManager:
    """Validate, persist, and execute one bounded P17 investigation transition."""

    def __init__(
        self,
        *,
        research_store: ResearchSessionStore,
        claim_store: ClaimLineageStore,
        reasoning_store: ResearchReasoningStore | None = None,
        followup_executor: ResearchFollowupExecutor | None = None,
        budget: ResearchReasoningBudget | None = None,
        db_engine=None,
    ) -> None:
        self._research = research_store
        self._claims = claim_store
        self._engine = db_engine or control_plane_engine
        self._ledger = reasoning_store or ResearchReasoningStore(self._engine)
        self._followup = followup_executor
        self._budget = budget or ResearchReasoningBudget()

    def _session(
        self,
        session_id: str,
        principal: Principal,
    ) -> ResearchSession:
        return self._research.load(
            session_id,
            tenant=_tenant(principal),
            principal=str(principal.user_id),
        )

    def _claim_views(
        self,
        session: ResearchSession,
        principal: Principal,
    ) -> tuple[ClaimView, ...]:
        with Session(self._engine) as db:
            claim_ids = tuple(
                x.claim_id
                for x in db.exec(
                    select(ResearchClaimRecord)
                    .where(
                        ResearchClaimRecord.session_id == session.session_id
                    )
                    .where(
                        ResearchClaimRecord.tenant_binding
                        == session.tenant_binding
                    )
                    .where(
                        ResearchClaimRecord.principal_subject
                        == session.principal_subject
                    )
                    .where(
                        ResearchClaimRecord.semantic_context_version
                        == session.context_version
                    )
                    .order_by(
                        ResearchClaimRecord.created_at,
                        ResearchClaimRecord.claim_id,
                    )
                ).all()
            )

        views = []
        for claim_id in claim_ids:
            claim = self._claims.load_claim(
                session_id=session.session_id,
                claim_id=claim_id,
                principal=principal,
            )
            views.append(
                ClaimView(
                    claim_id=claim.claim_id,
                    obligation_id=claim.obligation_id,
                    epistemic_state=claim.epistemic_state.value,
                    origin_material_refs=claim.origin_material_refs,
                    evidence_relations=tuple(
                        x.relation.value for x in claim.evidence_links
                    ),
                )
            )
        return tuple(views)

    def snapshot(
        self,
        *,
        session_id: str,
        principal: Principal,
    ) -> ResearchManagerSnapshot:
        session = self._session(session_id, principal)
        steps = self._ledger.steps(session.session_id)
        tasks = self._ledger.tasks(session.session_id)

        with Session(self._engine) as db:
            material_rows = tuple(
                db.exec(
                    select(ResearchExplorationMaterial)
                    .where(
                        ResearchExplorationMaterial.session_id
                        == session.session_id
                    )
                    .where(
                        ResearchExplorationMaterial.epistemic_state
                        == "RESEARCH_MATERIAL"
                    )
                    .order_by(
                        ResearchExplorationMaterial.created_at,
                        ResearchExplorationMaterial.lead_id,
                    )
                ).all()
            )

        claims = self._claim_views(session, principal)
        completed = tuple(
            x.step_id
            for x in steps
            if x.status
            in {
                ReasoningStepStatus.COMPLETED,
                ReasoningStepStatus.STOPPED,
                ReasoningStepStatus.NO_PROGRESS,
            }
        )
        pending = tuple(
            x.step_id
            for x in steps
            if x.status == ReasoningStepStatus.PENDING
        )
        followups = len(tasks)
        counters = sum(
            1 for x in tasks if x.counter_to_claim_id is not None
        )
        terminal = next(
            (
                x.stop_reason
                for x in reversed(steps)
                if x.status
                in {
                    ReasoningStepStatus.STOPPED,
                    ReasoningStepStatus.NO_PROGRESS,
                }
            ),
            None,
        )
        return ResearchManagerSnapshot(
            research_session_id=session.session_id,
            research_authority_id=session.authority_id,
            source_revision=session.revision,
            objective=session.objective,
            parent_obligations=tuple(
                ParentObligationView(
                    obligation_id=x.obligation_id,
                    objective=x.objective,
                    state=x.state.value,
                )
                for x in session.obligations
            ),
            evidence_refs=tuple(
                sorted(x.evidence_id for x in session.evidence_refs)
            ),
            material_refs=tuple(
                sorted(x.lead_id for x in material_rows)
            ),
            claims=claims,
            limitation_refs=tuple(
                sorted(x.limitation_id for x in session.limitations)
            ),
            completed_reasoning_steps=completed,
            pending_reasoning_steps=pending,
            remaining_reasoning_steps=max(
                0,
                self._budget.max_reasoning_steps - len(steps),
            ),
            remaining_followup_native_turns=max(
                0,
                self._budget.max_followup_native_turns - followups,
            ),
            remaining_counter_evidence_attempts=max(
                0,
                self._budget.max_counter_evidence_attempts - counters,
            ),
            terminal_stop_reason=terminal,
        )

    @staticmethod
    def _fingerprint(
        session: ResearchSession,
        proposal: ManagerProposal,
    ) -> str:
        claim_identity = None
        if proposal.claim is not None:
            claim_identity = {
                "proposition": proposal.claim.proposition,
                "scope": proposal.claim.scope,
                "freshness": proposal.claim.freshness.model_dump(mode="json"),
                "origin_material_refs": sorted(
                    proposal.claim.origin_material_refs
                ),
                "limitations": sorted(proposal.claim.limitations),
            }
        identity = {
            "research_authority_id": session.authority_id,
            "research_session_id": session.session_id,
            "parent_obligation_id": proposal.target_parent_obligation,
            "action": proposal.action.value,
            # objective_key is the normalized bounded target identity.
            # rationale/bounded_objective prose is intentionally excluded.
            "objective_key": proposal.objective_key,
            "counter_to_claim_id": proposal.counter_to_claim_id,
            "inspected_evidence_refs": sorted(
                proposal.inspected_evidence_refs
            ),
            "inspected_claim_refs": sorted(proposal.inspected_claim_refs),
            "inspected_material_refs": sorted(
                proposal.inspected_material_refs
            ),
            "claim_identity": claim_identity,
            "stop_reason": (
                proposal.stop_reason.value
                if proposal.stop_reason is not None
                else None
            ),
        }
        return _json(
            identity,
            code="P17_PROPOSAL_NOT_CANONICAL",
        )[1]

    def _validate(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        proposal: ManagerProposal,
    ) -> None:
        if proposal.source_revision != session.revision:
            raise ResearchManagerMaturationError(
                "P17_SOURCE_REVISION_MISMATCH",
                "manager proposal was formed against another Research revision",
            )

        obligation = next(
            (
                x
                for x in session.obligations
                if x.obligation_id == proposal.target_parent_obligation
            ),
            None,
        )
        if obligation is None:
            raise ResearchManagerMaturationError(
                "P17_PARENT_OBLIGATION_OUT_OF_SCOPE",
                proposal.target_parent_obligation,
            )

        evidence_by_id = {
            x.evidence_id: x for x in session.evidence_refs
        }
        claim_by_id = {x.claim_id: x for x in snapshot.claims}
        with Session(self._engine) as db:
            material_rows = tuple(
                db.exec(
                    select(ResearchExplorationMaterial)
                    .where(
                        ResearchExplorationMaterial.session_id
                        == session.session_id
                    )
                    .where(
                        ResearchExplorationMaterial.epistemic_state
                        == "RESEARCH_MATERIAL"
                    )
                ).all()
            )
        material_by_id = {x.lead_id: x for x in material_rows}

        for evidence_id in proposal.inspected_evidence_refs:
            ref = evidence_by_id.get(evidence_id)
            if ref is None:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_REF_UNKNOWN",
                    evidence_id,
                )
            if ref.obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_REF_SCOPE_MISMATCH",
                    evidence_id,
                )

        for claim_id in proposal.inspected_claim_refs:
            claim = claim_by_id.get(claim_id)
            if claim is None:
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_REF_UNKNOWN",
                    claim_id,
                )
            if claim.obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_REF_SCOPE_MISMATCH",
                    claim_id,
                )

        for material_id in proposal.inspected_material_refs:
            material = material_by_id.get(material_id)
            if material is None:
                raise ResearchManagerMaturationError(
                    "P17_MATERIAL_REF_UNKNOWN",
                    material_id,
                )
            if material.obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_MATERIAL_REF_SCOPE_MISMATCH",
                    material_id,
                )

        if proposal.action == ManagerAction.SEEK_COUNTER_EVIDENCE:
            claim = claim_by_id.get(proposal.counter_to_claim_id or "")
            if claim is None:
                raise ResearchManagerMaturationError(
                    "P17_COUNTER_CLAIM_UNKNOWN",
                    proposal.counter_to_claim_id or "",
                )
            if claim.obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_COUNTER_CLAIM_SCOPE_MISMATCH",
                    claim.claim_id,
                )
            if claim.claim_id not in proposal.inspected_claim_refs:
                raise ResearchManagerMaturationError(
                    "P17_COUNTER_CLAIM_NOT_INSPECTED",
                    claim.claim_id,
                )

        if (
            proposal.action == ManagerAction.FORM_CLAIM
            and proposal.claim is not None
        ):
            if any(
                ref not in material_by_id
                for ref in proposal.claim.origin_material_refs
            ):
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_ORIGIN_UNKNOWN",
                    "FORM_CLAIM references unknown P15 material",
                )
            if any(
                material_by_id[ref].obligation_id
                != proposal.target_parent_obligation
                for ref in proposal.claim.origin_material_refs
            ):
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_ORIGIN_SCOPE_MISMATCH",
                    "FORM_CLAIM origin belongs to another obligation",
                )

    def _system_stop(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        reason: ManagerStopReason,
        detail: str,
    ) -> ResearchReasoningStep:
        proposal = ManagerProposal(
            proposal_id=f"p17-system-{reason.value.lower()}",
            source_revision=session.revision,
            target_parent_obligation=session.obligations[0].obligation_id,
            action=ManagerAction.STOP,
            objective_key=f"system.{reason.value.lower()}",
            rationale=detail,
            stop_reason=reason,
        )
        fingerprint = self._fingerprint(session, proposal)
        return self._ledger.create_step(
            session=session,
            snapshot=snapshot,
            proposal=proposal,
            proposal_fingerprint=fingerprint,
            status=(
                ReasoningStepStatus.NO_PROGRESS
                if reason == ManagerStopReason.NO_PROGRESS
                else ReasoningStepStatus.STOPPED
            ),
            stop_reason=reason,
        )

    def _resume_pending(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        step: ResearchReasoningStep,
        principal: Principal,
    ) -> tuple[ResearchReasoningStep, ResearchInvestigationTask | None]:
        proposal = self._ledger.proposal(step.step_id)
        if proposal.source_revision != session.revision:
            raise ResearchManagerMaturationError(
                "P17_PENDING_STEP_REVISION_DRIFT",
                step.step_id,
            )

        if proposal.action == ManagerAction.FORM_CLAIM:
            assert proposal.claim is not None
            claim = self._claims.create_claim(
                session_id=session.session_id,
                obligation_id=proposal.target_parent_obligation,
                principal=principal,
                claim_text=proposal.claim.claim_text,
                proposition=proposal.claim.proposition,
                scope=proposal.claim.scope,
                freshness=proposal.claim.freshness,
                origin_material_refs=proposal.claim.origin_material_refs,
                limitations=proposal.claim.limitations,
            )
            return (
                self._ledger.complete_step(
                    step.step_id,
                    result_refs=(claim.claim_id,),
                ),
                None,
            )

        if proposal.action not in {
            ManagerAction.EXPLORE_NATIVE,
            ManagerAction.SEEK_COUNTER_EVIDENCE,
        }:
            raise ResearchManagerMaturationError(
                "P17_PENDING_ACTION_INVALID",
                proposal.action.value,
            )
        if self._followup is None:
            raise ResearchManagerMaturationError(
                "P17_FOLLOWUP_EXECUTOR_REQUIRED",
                "pending follow-up requires the single sealed native-direct adapter",
            )

        task = self._ledger.task_for_step(step.step_id)
        if task is None:
            task = self._ledger.create_task(
                session=session,
                step=step,
                proposal=proposal,
            )

        if task.status == InvestigationTaskStatus.PENDING:
            result = self._followup.execute(
                session=session,
                step=step,
                task=task,
                principal=principal,
            )
            task = self._ledger.complete_task(
                task.task_id,
                result=result,
            )

        result_refs = tuple(
            dict.fromkeys(
                (
                    *task.native_execution_refs,
                    *task.material_refs,
                    *task.evidence_refs,
                )
            )
        )
        return (
            self._ledger.complete_step(
                step.step_id,
                result_refs=result_refs,
            ),
            task,
        )

    def run_one(
        self,
        *,
        session_id: str,
        principal: Principal,
        manager: ResearchProposalManager,
    ) -> tuple[ResearchReasoningStep, ResearchInvestigationTask | None]:
        session = self._session(session_id, principal)
        snapshot = self.snapshot(
            session_id=session_id,
            principal=principal,
        )

        if snapshot.terminal_stop_reason is not None:
            raise ResearchManagerMaturationError(
                "P17_INVESTIGATION_TERMINAL",
                snapshot.terminal_stop_reason.value,
            )

        if len(snapshot.pending_reasoning_steps) > 1:
            raise ResearchManagerMaturationError(
                "P17_MULTIPLE_PENDING_STEPS",
                "bounded manager permits at most one pending reasoning step",
            )

        if snapshot.pending_reasoning_steps:
            pending = next(
                x
                for x in self._ledger.steps(session.session_id)
                if x.step_id == snapshot.pending_reasoning_steps[0]
            )
            return self._resume_pending(
                session=session,
                snapshot=snapshot,
                step=pending,
                principal=principal,
            )

        if snapshot.remaining_reasoning_steps == 0:
            return (
                self._system_stop(
                    session=session,
                    snapshot=snapshot,
                    reason=ManagerStopReason.BUDGET_EXHAUSTED,
                    detail="P17 reasoning budget exhausted",
                ),
                None,
            )

        proposal = manager.propose(snapshot)
        self._validate(
            session=session,
            snapshot=snapshot,
            proposal=proposal,
        )
        fingerprint = self._fingerprint(session, proposal)
        prior = self._ledger.prior_fingerprint(
            session_id=session.session_id,
            proposal_fingerprint=fingerprint,
        )
        if prior is not None:
            step = self._ledger.create_step(
                session=session,
                snapshot=snapshot,
                proposal=proposal,
                proposal_fingerprint=fingerprint,
                status=ReasoningStepStatus.NO_PROGRESS,
                stop_reason=ManagerStopReason.NO_PROGRESS,
            )
            return step, None

        if proposal.action == ManagerAction.STOP:
            step = self._ledger.create_step(
                session=session,
                snapshot=snapshot,
                proposal=proposal,
                proposal_fingerprint=fingerprint,
                status=ReasoningStepStatus.STOPPED,
                stop_reason=proposal.stop_reason,
            )
            return step, None

        if (
            proposal.action
            in {
                ManagerAction.EXPLORE_NATIVE,
                ManagerAction.SEEK_COUNTER_EVIDENCE,
            }
            and snapshot.remaining_followup_native_turns == 0
        ):
            return (
                self._system_stop(
                    session=session,
                    snapshot=snapshot,
                    reason=ManagerStopReason.BUDGET_EXHAUSTED,
                    detail="P17 native follow-up budget exhausted",
                ),
                None,
            )

        if (
            proposal.action == ManagerAction.SEEK_COUNTER_EVIDENCE
            and snapshot.remaining_counter_evidence_attempts == 0
        ):
            return (
                self._system_stop(
                    session=session,
                    snapshot=snapshot,
                    reason=ManagerStopReason.BUDGET_EXHAUSTED,
                    detail="P17 counter-evidence budget exhausted",
                ),
                None,
            )

        if (
            proposal.action
            in {
                ManagerAction.EXPLORE_NATIVE,
                ManagerAction.SEEK_COUNTER_EVIDENCE,
            }
            and self._followup is None
        ):
            raise ResearchManagerMaturationError(
                "P17_FOLLOWUP_EXECUTOR_REQUIRED",
                "native follow-up proposal requires the single sealed native-direct adapter",
            )

        # Persist the accepted manager proposal before any follow-on work.
        step = self._ledger.create_step(
            session=session,
            snapshot=snapshot,
            proposal=proposal,
            proposal_fingerprint=fingerprint,
        )
        return self._resume_pending(
            session=session,
            snapshot=snapshot,
            step=step,
            principal=principal,
        )
