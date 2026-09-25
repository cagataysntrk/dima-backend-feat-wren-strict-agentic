"""P14 Research state. Analytics stay on native P13 -> P10 -> P5 -> Evidence."""
from __future__ import annotations

import hashlib, json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v2.models import ResearchBrief, ResearchBriefStatus
from app.v3.authority import AcceptedResearchAuthority
from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact, EvidenceState
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineObservation, NativeEngineRequest


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchStateError(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}"); self.code, self.detail = code, detail


def _now(value=None):
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Research timestamps must be timezone-aware")
    return value


def _id(prefix, value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return prefix + hashlib.sha256(raw.encode()).hexdigest()[:24]


class ObligationState(StrEnum):
    READY="READY"; DELEGATED="DELEGATED"; VERIFIED="VERIFIED"; LIMITED="LIMITED"


class StoppingStatus(StrEnum):
    ACTIVE="ACTIVE"; COMPLETE="COMPLETE"; PARTIAL="PARTIAL"; BUDGET_EXHAUSTED="BUDGET_EXHAUSTED"


class HypothesisState(StrEnum):
    OPEN="OPEN"; SUPPORTED="SUPPORTED"; CHALLENGED="CHALLENGED"; CONTESTED="CONTESTED"


class EvidenceRelation(StrEnum):
    SUPPORTS="SUPPORTS"; CONTRADICTS="CONTRADICTS"


class ResearchBudget(Frozen):
    max_native_turns: int = Field(8, ge=1)
    max_material_executions: int = Field(8, ge=1)
    native_turns_used: int = Field(0, ge=0)
    material_executions_used: int = Field(0, ge=0)

    @model_validator(mode="after")
    def bounded(self):
        if self.native_turns_used > self.max_native_turns or self.material_executions_used > self.max_material_executions:
            raise ValueError("Research budget exceeded")
        return self


class StoppingState(Frozen):
    status: StoppingStatus = StoppingStatus.ACTIVE
    reason: str | None = None


class NativeMetabotConversationRef(Frozen):
    conversation_id: UUID
    profile_id: str = "nlq"
    metabot_id: str | None = None
    native_turns: int = 0
    last_request_id: str | None = None
    last_trace_id: str | None = None


class EvidenceRef(Frozen):
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")
    authority_id: str
    obligation_id: str


class CounterEvidenceRef(Frozen):
    hypothesis_id: str = Field(pattern=r"^hyp_[a-f0-9]{24}$")
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")
    obligation_id: str


class ResearchLimitation(Frozen):
    limitation_id: str = Field(pattern=r"^lim_[a-f0-9]{24}$")
    obligation_id: str
    code: str
    detail: str
    recorded_at: datetime


class ResearchObligation(Frozen):
    obligation_id: str
    objective: str
    state: ObligationState = ObligationState.READY
    evidence_refs: tuple[str, ...] = ()
    limitation_refs: tuple[str, ...] = ()


class Hypothesis(Frozen):
    hypothesis_id: str = Field(pattern=r"^hyp_[a-f0-9]{24}$")
    statement: str
    obligation_ids: tuple[str, ...]
    state: HypothesisState = HypothesisState.OPEN
    supporting_refs: tuple[str, ...] = ()
    counter_refs: tuple[str, ...] = ()


class ResearchSession(Frozen):
    schema_version: Literal["p14-research-v1"] = "p14-research-v1"
    session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    revision: int = 1
    authority_id: str
    lineage_id: str
    source_message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    context_version: str
    tenant_binding: str
    principal_subject: str
    objective: str
    # Immutable snapshot of the already-grounded ResearchBrief accepted at entry.
    # It is part of the checkpoint fingerprint; resume never reparses old language.
    accepted_brief: ResearchBrief | None = None
    obligations: tuple[ResearchObligation, ...]
    hypotheses: tuple[Hypothesis, ...] = ()
    evidence_refs: tuple[EvidenceRef, ...] = ()
    counter_evidence_refs: tuple[CounterEvidenceRef, ...] = ()
    limitations: tuple[ResearchLimitation, ...] = ()
    budget: ResearchBudget = Field(default_factory=ResearchBudget)
    stopping: StoppingState = Field(default_factory=StoppingState)
    native_conversation: NativeMetabotConversationRef | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def coherent(self):
        _now(self.created_at); _now(self.updated_at)
        ids = [x.obligation_id for x in self.obligations]
        if not ids or len(ids) != len(set(ids)): raise ValueError("invalid Research obligation ids")
        if self.accepted_brief is not None:
            brief = self.accepted_brief
            if brief.status != ResearchBriefStatus.READY_FOR_RESEARCH:
                raise ValueError("accepted ResearchBrief must be READY_FOR_RESEARCH")
            if brief.context_version != self.context_version:
                raise ValueError("accepted ResearchBrief context mismatch")
            if brief.objective != self.objective:
                raise ValueError("accepted ResearchBrief objective mismatch")
            if tuple(brief.must_requirement_ids) != tuple(ids):
                raise ValueError("accepted ResearchBrief obligation mismatch")
        if any(not set(h.obligation_ids).issubset(ids) for h in self.hypotheses):
            raise ValueError("hypothesis references unknown obligation")
        return self

    @property
    def fingerprint(self):
        raw=json.dumps(self.model_dump(mode="json"),sort_keys=True,separators=(",",":"),ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()


class ResearchCheckpoint(Frozen):
    session: ResearchSession
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    @model_validator(mode="after")
    def intact(self):
        if self.fingerprint != self.session.fingerprint: raise ValueError("Research checkpoint mismatch")
        return self


class NativeDelegation(Frozen):
    session: ResearchSession
    obligation_id: str
    request: NativeEngineRequest


class ResearchManager:
    """Owns WHAT/WHY/WHEN for Research; native Metabot owns HOW."""
    terminal={ObligationState.VERIFIED, ObligationState.LIMITED}

    @staticmethod
    def obligation(session, oid):
        item=next((x for x in session.obligations if x.obligation_id==oid),None)
        if item is None: raise ResearchStateError("P14_OBLIGATION_UNKNOWN",oid)
        return item

    @staticmethod
    def replace(session,item):
        return tuple(item if x.obligation_id==item.obligation_id else x for x in session.obligations)

    @classmethod
    def stopping(cls, obligations, budget):
        if all(x.state==ObligationState.VERIFIED for x in obligations):
            return StoppingState(status=StoppingStatus.COMPLETE,reason="all obligations VERIFIED")
        if all(x.state in cls.terminal for x in obligations):
            return StoppingState(status=StoppingStatus.PARTIAL,reason="terminal with explicit limitation")
        if budget.native_turns_used>=budget.max_native_turns or budget.material_executions_used>=budget.max_material_executions:
            return StoppingState(status=StoppingStatus.BUDGET_EXHAUSTED,reason="Research budget exhausted")
        return StoppingState()

    @classmethod
    def advance(cls,session,now=None,**updates):
        obligations=updates.get("obligations",session.obligations); budget=updates.get("budget",session.budget)
        updates.update(stopping=cls.stopping(obligations,budget),revision=session.revision+1,updated_at=_now(now))
        return ResearchSession.model_validate(session.model_copy(update=updates).model_dump(mode="json"))

    @classmethod
    def start(cls,*,authority:AcceptedResearchAuthority,objective,obligation_objectives,tenant_binding,principal_subject,budget=None,now=None,session_id=None,accepted_brief:ResearchBrief|None=None):
        accepted=tuple(authority.obligation_ids)
        if not accepted or set(accepted)!=set(obligation_objectives):
            raise ResearchStateError("P14_RESEARCH_OBLIGATION_AUTHORITY_MISMATCH","objectives must exactly cover accepted obligations")
        stamp=_now(now)
        return ResearchSession(
            session_id=session_id or "rs_"+uuid4().hex[:24], authority_id=authority.contract_id,
            lineage_id=authority.lineage_id, source_message_hash=authority.source_message_hash,
            context_version=authority.context_version, tenant_binding=tenant_binding,
            principal_subject=principal_subject, objective=objective.strip(),
            accepted_brief=accepted_brief,
            obligations=tuple(ResearchObligation(obligation_id=x,objective=obligation_objectives[x].strip()) for x in accepted),
            budget=budget or ResearchBudget(), created_at=stamp, updated_at=stamp,
        )

    @classmethod
    def add_hypothesis(cls,session,*,statement,obligation_ids,now=None):
        known={x.obligation_id for x in session.obligations}
        if not statement.strip() or not obligation_ids or not set(obligation_ids).issubset(known):
            raise ResearchStateError("P14_HYPOTHESIS_SCOPE_INVALID","invalid hypothesis scope")
        hid=_id("hyp_",{"session":session.session_id,"statement":statement,"ids":sorted(obligation_ids)})
        if any(x.hypothesis_id==hid for x in session.hypotheses): return session
        h=Hypothesis(hypothesis_id=hid,statement=statement.strip(),obligation_ids=tuple(dict.fromkeys(obligation_ids)))
        return cls.advance(session,now=now,hypotheses=(*session.hypotheses,h))

    @classmethod
    def prepare_native_delegation(cls,session,*,obligation_id,profile_id="nlq",metabot_id=None,now=None):
        if session.stopping.status!=StoppingStatus.ACTIVE: raise ResearchStateError("P14_RESEARCH_NOT_ACTIVE",session.stopping.status)
        item=cls.obligation(session,obligation_id)
        if item.state in cls.terminal: raise ResearchStateError("P14_OBLIGATION_TERMINAL",obligation_id)
        if session.budget.native_turns_used>=session.budget.max_native_turns: raise ResearchStateError("P14_NATIVE_BUDGET_EXHAUSTED","budget exhausted")
        conv=session.native_conversation or NativeMetabotConversationRef(conversation_id=uuid4(),profile_id=profile_id,metabot_id=metabot_id)
        if (conv.profile_id,conv.metabot_id)!=(profile_id,metabot_id): raise ResearchStateError("P14_NATIVE_CONVERSATION_IDENTITY_MISMATCH","profile/metabot changed")
        turn=session.budget.native_turns_used+1; rid=f"p14-{session.session_id}-{obligation_id}-t{turn}"
        req=NativeEngineRequest(profile_id=conv.profile_id,metabot_id=conv.metabot_id,message=item.objective,context={},conversation_id=conv.conversation_id,history=None,state={},dima_request_id=rid,dima_trace_id=rid+"-trace")
        conv=conv.model_copy(update={"native_turns":conv.native_turns+1,"last_request_id":rid,"last_trace_id":rid+"-trace"})
        item=item.model_copy(update={"state":ObligationState.DELEGATED})
        budget=session.budget.model_copy(update={"native_turns_used":turn})
        updated=cls.advance(session,now=now,obligations=cls.replace(session,item),budget=budget,native_conversation=conv)
        return NativeDelegation(session=updated,obligation_id=obligation_id,request=req)

    @staticmethod
    def invoke_native(delegation,*,bridge:NativeEngineBridge)->NativeEngineObservation:
        return bridge.invoke(delegation.request)

    @staticmethod
    def check_evidence(session,oid,receipt:DimaQueryReceipt,evidence:EvidenceArtifact):
        if evidence.state!=EvidenceState.VERIFIED: raise ResearchStateError("P14_EVIDENCE_NOT_VERIFIED","only VERIFIED Evidence is admissible")
        if evidence.authority_id!=receipt.authority_id: raise ResearchStateError("P14_EVIDENCE_RECEIPT_AUTHORITY_MISMATCH","authority mismatch")
        if receipt.receipt_id not in evidence.query_receipt_refs: raise ResearchStateError("P14_EVIDENCE_RECEIPT_LINK_MISSING","receipt link missing")
        if oid not in receipt.obligation_ids or oid not in evidence.obligation_ids: raise ResearchStateError("P14_EVIDENCE_OBLIGATION_MISMATCH","obligation mismatch")
        if (receipt.tenant_id,receipt.principal_id)!=(session.tenant_binding,session.principal_subject): raise ResearchStateError("P14_EVIDENCE_SECURITY_LENS_MISMATCH","security lens mismatch")
        if receipt.semantic_context_version!=session.context_version: raise ResearchStateError("P14_EVIDENCE_CONTEXT_MISMATCH","context mismatch")
        if any(x is None for x in (receipt.execution_id,receipt.receipt_fingerprint,receipt.execution_access_fingerprint,receipt.result_hash,receipt.executed_at)):
            raise ResearchStateError("P14_RECEIPT_EXECUTION_IDENTITY_INCOMPLETE","fully sealed QueryReceipt required")

    @classmethod
    def admit_receipted_evidence(cls,session,*,obligation_id,receipt,evidence,satisfies_obligation,hypothesis_id=None,relation=None,now=None):
        item=cls.obligation(session,obligation_id); cls.check_evidence(session,obligation_id,receipt,evidence)
        if (hypothesis_id is None)!=(relation is None): raise ResearchStateError("P14_HYPOTHESIS_EVIDENCE_RELATION_INCOMPLETE","pair required")
        if any(x.evidence_id==evidence.artifact_id for x in session.evidence_refs): return session
        if session.budget.material_executions_used>=session.budget.max_material_executions: raise ResearchStateError("P14_MATERIAL_EXECUTION_BUDGET_EXHAUSTED","budget exhausted")
        eref=EvidenceRef(evidence_id=evidence.artifact_id,receipt_id=receipt.receipt_id,authority_id=receipt.authority_id,obligation_id=obligation_id)
        hypotheses=list(session.hypotheses); counters=list(session.counter_evidence_refs)
        if hypothesis_id:
            idx=next((i for i,x in enumerate(hypotheses) if x.hypothesis_id==hypothesis_id),None)
            if idx is None: raise ResearchStateError("P14_HYPOTHESIS_UNKNOWN",hypothesis_id)
            h=hypotheses[idx]
            if obligation_id not in h.obligation_ids: raise ResearchStateError("P14_HYPOTHESIS_OBLIGATION_MISMATCH",obligation_id)
            support,counter=h.supporting_refs,h.counter_refs
            if relation==EvidenceRelation.SUPPORTS: support=tuple(dict.fromkeys((*support,evidence.artifact_id)))
            else:
                counter=tuple(dict.fromkeys((*counter,evidence.artifact_id)))
                counters.append(CounterEvidenceRef(hypothesis_id=hypothesis_id,evidence_id=evidence.artifact_id,receipt_id=receipt.receipt_id,obligation_id=obligation_id))
            state=HypothesisState.CONTESTED if support and counter else HypothesisState.SUPPORTED if support else HypothesisState.CHALLENGED
            hypotheses[idx]=h.model_copy(update={"supporting_refs":support,"counter_refs":counter,"state":state})
        item=item.model_copy(update={"state":ObligationState.VERIFIED if satisfies_obligation else ObligationState.DELEGATED,"evidence_refs":tuple(dict.fromkeys((*item.evidence_refs,evidence.artifact_id)))})
        budget=session.budget.model_copy(update={"material_executions_used":session.budget.material_executions_used+1})
        return cls.advance(session,now=now,obligations=cls.replace(session,item),hypotheses=tuple(hypotheses),evidence_refs=(*session.evidence_refs,eref),counter_evidence_refs=tuple(counters),budget=budget)

    @classmethod
    def record_limitation(cls,session,*,obligation_id,code,detail,now=None):
        item=cls.obligation(session,obligation_id)
        if item.state==ObligationState.VERIFIED: raise ResearchStateError("P14_VERIFIED_OBLIGATION_IMMUTABLE",obligation_id)
        stamp=_now(now); lid=_id("lim_",{"session":session.session_id,"obligation":obligation_id,"code":code,"detail":detail,"revision":session.revision+1})
        lim=ResearchLimitation(limitation_id=lid,obligation_id=obligation_id,code=code,detail=detail,recorded_at=stamp)
        item=item.model_copy(update={"state":ObligationState.LIMITED,"limitation_refs":(*item.limitation_refs,lid)})
        return cls.advance(session,now=stamp,obligations=cls.replace(session,item),limitations=(*session.limitations,lim))

    @staticmethod
    def checkpoint(session): return ResearchCheckpoint(session=session,fingerprint=session.fingerprint)

    @staticmethod
    def restore_checkpoint(raw): return ResearchCheckpoint.model_validate_json(raw).session
