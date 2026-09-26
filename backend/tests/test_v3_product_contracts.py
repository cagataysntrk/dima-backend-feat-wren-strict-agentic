from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.v3.product.capabilities import capability_discovery, company_context
from app.v3.product.contracts import (
    ArtifactKind,
    ArtifactRef,
    CapabilityStatus,
    PRODUCT_CONTRACT_VERSION,
    ProductCurrentness,
    ProductErrorCode,
)
from app.v3.product.errors import ProductError, normalize_owner_error
from app.v3.product.service import HeadlessProductService, ProductSources
from control_plane.authorize import Principal

STAMP=datetime(2026,9,26,8,0,tzinfo=timezone.utc)
TENANT="00000000-0000-4000-8000-000000006201"
OTHER="00000000-0000-4000-8000-000000006202"
USER="00000000-0000-4000-8000-000000006203"


def enum(value):
    return SimpleNamespace(value=value)


def principal(*,tenant=TENANT,roles=("analyst",),user=USER):
    return Principal(user_id=user,tenant_id=tenant,tenant_slug="core-b",roles=list(roles))


class OwnerError(RuntimeError):
    def __init__(self,code,detail="owner error"):
        super().__init__(f"{code}: {detail}")
        self.code=code
        self.detail=detail


def research_session():
    return SimpleNamespace(
        session_id="rs_"+"1"*24,
        tenant_binding=f"id:{TENANT}",
        revision=4,
        objective="Explain margin deterioration and decide what to do.",
        stopping=SimpleNamespace(status=enum("COMPLETE"),reason="all obligations VERIFIED"),
        obligations=(SimpleNamespace(obligation_id="must-1",state=enum("VERIFIED")),),
        evidence_refs=(SimpleNamespace(evidence_id="evi_"+"2"*24,receipt_id="dqr_"+"3"*24,authority_id="auth-r",obligation_id="must-1"),),
        limitations=(),
        created_at=STAMP+timedelta(minutes=2),
        updated_at=STAMP+timedelta(minutes=5),
        fingerprint="4"*64,
    )


def watch():
    return SimpleNamespace(
        watch_id="wat_"+"5"*24,
        tenant_binding=f"id:{TENANT}",
        kind=enum("THRESHOLD_CONTEXT"),
        title="Margin watch",
        source_contract_ref="metric:gross-margin",
        criterion_ref="policy:margin-watch",
        entity_refs=("company:acme",),
        metric_refs=("metric:gross-margin",),
        watch_fingerprint="6"*64,
        created_at=STAMP,
    )


def signal():
    return SimpleNamespace(
        signal_id="sig_"+"7"*24,
        root_signal_id="sig_"+"7"*24,
        revision=2,
        tenant_binding=f"id:{TENANT}",
        watch_id=watch().watch_id,
        severity=enum("MATERIAL"),
        status=enum("INVESTIGATING"),
        business_significance="Margin deterioration requires investigation.",
        source_ref="occurrence:margin-2026-09",
        research_session_id=research_session().session_id,
        action_work_id=None,
        memory_entry_id=None,
        signal_fingerprint="8"*64,
        created_at=STAMP+timedelta(minutes=1),
    )


def reasoning_steps():
    return (
        SimpleNamespace(
            step_id="rrs_"+"9"*24,
            status=enum("COMPLETED"),
            stop_reason=None,
            created_at=STAMP+timedelta(minutes=3),
        ),
    )


def tasks():
    return (
        SimpleNamespace(
            task_id="rit_"+"a"*24,
            status=enum("COMPLETED"),
        ),
    )


def epistemic():
    return SimpleNamespace(
        assessment_id="p19a_"+"b"*24,
        research_session_id=research_session().session_id,
        obligation_id="must-1",
        tenant_binding=f"id:{TENANT}",
        candidates=(SimpleNamespace(hypothesis_id="p19h_"+"c"*24),),
        root_cause_hypothesis_ids=("p19h_"+"c"*24,),
        aggregate_outcome=enum("ROOT_CAUSE_ESTABLISHED"),
        limitations=(),
        assessment_fingerprint="d"*64,
        created_at=STAMP+timedelta(minutes=6),
    )


def report():
    return SimpleNamespace(
        report_id="p20r_"+"e"*24,
        research_session_id=research_session().session_id,
        tenant_binding=f"id:{TENANT}",
        report_key="margin-review",
        revision=1,
        statements=(SimpleNamespace(statement_id="p20s_"+"f"*24),),
        limitations=(),
        coverage=(SimpleNamespace(obligation_id="must-1",coverage_status=enum("REPRESENTED")),),
        report_fingerprint="0"*64,
        created_at=STAMP+timedelta(minutes=7),
    )


def decision():
    return SimpleNamespace(
        decision_brief_id="p21b_"+"1"*24,
        report_id=report().report_id,
        tenant_binding=f"id:{TENANT}",
        brief_key="margin-action",
        revision=1,
        objective=SimpleNamespace(objective_text="Choose a bounded response."),
        options=(SimpleNamespace(option_id="p21x_"+"2"*24),SimpleNamespace(option_id="p21x_"+"3"*24)),
        recommendation=SimpleNamespace(recommended_option_ids=("p21x_"+"2"*24,)),
        limitations=(),
        brief_fingerprint="4"*64,
        created_at=STAMP+timedelta(minutes=8),
    )


def adoption():
    return SimpleNamespace(
        adoption_id="adp_"+"5"*24,
        decision_brief_id=decision().decision_brief_id,
        tenant_binding=f"id:{TENANT}",
        disposition=enum("ACCEPTED"),
        selected_option_ids=("p21x_"+"2"*24,),
        actor_user_id=USER,
        human_conditions=(),
        adoption_fingerprint="6"*64,
        recorded_at=STAMP+timedelta(minutes=9),
    )


def work():
    return SimpleNamespace(
        action_work_id="wrk_"+"7"*24,
        tenant_binding=f"id:{TENANT}",
        decision_brief_id=decision().decision_brief_id,
        decision_adoption_id=adoption().adoption_id,
        title="Run collections intervention",
        owner_user_id=USER,
        due_at=STAMP+timedelta(days=5),
        status=enum("COMPLETED"),
        blocker_reason=None,
        completion_reference="internal://work/42",
        work_fingerprint="8"*64,
        revision=4,
        created_at=STAMP+timedelta(minutes=10),
    )


def outcome():
    return SimpleNamespace(
        outcome_id="out_"+"9"*24,
        tenant_binding=f"id:{TENANT}",
        action_work_id=work().action_work_id,
        decision_brief_id=decision().decision_brief_id,
        decision_adoption_id=adoption().adoption_id,
        classification=enum("IMPROVED"),
        baseline_definition="Prior comparable period.",
        baseline_window="2026-08",
        observation_window="2026-09",
        evidence=(SimpleNamespace(evidence_id="evi_"+"2"*24),),
        claim_ids=("clm_"+"a"*24,),
        report_id=report().report_id,
        limitations=("Observed improvement does not establish causality.",),
        outcome_fingerprint="b"*64,
        observed_at=STAMP+timedelta(minutes=11),
    )


def memory():
    return SimpleNamespace(
        memory_id="mem_"+"c"*24,
        tenant_binding=f"id:{TENANT}",
        role=enum("CURRENT_CONTEXT"),
        problem_type="margin deterioration",
        domain="finance",
        entity_refs=("company:acme",),
        metric_refs=("metric:gross-margin",),
        source_refs=(
            SimpleNamespace(kind=enum("OUTCOME"),artifact_id=outcome().outcome_id),
        ),
        summary="A bounded collections intervention preceded an observed improvement; causality is not claimed.",
        limitations=("Outcome is observational.",),
        memory_fingerprint="d"*64,
        created_at=STAMP+timedelta(minutes=12),
    )


class FakeResearch:
    def __init__(self):
        self.calls=[]
    def resume_state(self,*,session_id,principal):
        self.calls.append((session_id,principal.tenant_id,tuple(principal.roles)))
        if session_id!=research_session().session_id or str(principal.tenant_id)!=TENANT or "viewer" in principal.roles:
            raise OwnerError("P14_RESEARCH_UNAVAILABLE")
        return research_session()


class FakeReasoning:
    def steps(self,session_id):
        assert session_id==research_session().session_id
        return reasoning_steps()
    def tasks(self,session_id):
        assert session_id==research_session().session_id
        return tasks()


class FakeSingleOwner:
    def __init__(self,item,id_name,state="CURRENT",unavailable_code="OWNER_UNAVAILABLE"):
        self.item=item
        self.id_name=id_name
        self.state=state
        self.unavailable_code=unavailable_code
        self.calls=[]
    def _check(self,value,principal):
        self.calls.append((value,principal.tenant_id,tuple(principal.roles)))
        expected=getattr(self.item,self.id_name)
        if value!=expected or str(principal.tenant_id)!=TENANT or "viewer" in principal.roles:
            raise OwnerError(self.unavailable_code)
    def load_watch(self,*,watch_id,principal):
        self._check(watch_id,principal); return self.item
    def load_signal(self,*,signal_id,principal):
        self._check(signal_id,principal); return self.item
    def currentness(self,**kwargs):
        principal=kwargs["principal"]
        key=next(v for k,v in kwargs.items() if k!="principal")
        self._check(key,principal); return enum(self.state)
    def load_assessment(self,*,assessment_id,principal):
        self._check(assessment_id,principal); return self.item
    def load(self,**kwargs):
        principal=kwargs["principal"]
        key=next(v for k,v in kwargs.items() if k!="principal")
        self._check(key,principal); return self.item


def sources(*,signal_state="CURRENT",report_state="CURRENT",decision_state="CURRENT",work_state="CURRENT",outcome_state="CURRENT",memory_state="CURRENT"):
    return ProductSources(
        research=FakeResearch(),
        reasoning=FakeReasoning(),
        epistemics=FakeSingleOwner(epistemic(),"assessment_id"),
        reports=FakeSingleOwner(report(),"report_id",report_state),
        decisions=FakeSingleOwner(decision(),"decision_brief_id",decision_state),
        adoptions=FakeSingleOwner(adoption(),"adoption_id"),
        action_work=FakeSingleOwner(work(),"action_work_id",work_state),
        outcomes=FakeSingleOwner(outcome(),"outcome_id",outcome_state),
        memory=FakeSingleOwner(memory(),"memory_id",memory_state),
        watch_signal=CombinedWatchSignal(signal_state),
    )


class CombinedWatchSignal:
    def __init__(self,state="CURRENT"):
        self.w=FakeSingleOwner(watch(),"watch_id")
        self.s=FakeSingleOwner(signal(),"signal_id",state)
    def load_watch(self,**kwargs): return self.w.load_watch(**kwargs)
    def load_signal(self,**kwargs): return self.s.load_signal(**kwargs)
    def currentness(self,**kwargs): return self.s.currentness(**kwargs)


def refs():
    rs=research_session()
    return (
        ArtifactRef(kind=ArtifactKind.WATCH,artifact_id=watch().watch_id),
        ArtifactRef(kind=ArtifactKind.SIGNAL,artifact_id=signal().signal_id),
        ArtifactRef(kind=ArtifactKind.RESEARCH,artifact_id=rs.session_id),
        ArtifactRef(kind=ArtifactKind.INVESTIGATION,artifact_id=rs.session_id),
        ArtifactRef(kind=ArtifactKind.EVIDENCE,artifact_id=rs.evidence_refs[0].evidence_id,scope_id=rs.session_id),
        ArtifactRef(kind=ArtifactKind.EPISTEMIC_ASSESSMENT,artifact_id=epistemic().assessment_id),
        ArtifactRef(kind=ArtifactKind.REPORT,artifact_id=report().report_id),
        ArtifactRef(kind=ArtifactKind.DECISION,artifact_id=decision().decision_brief_id),
        ArtifactRef(kind=ArtifactKind.ADOPTION,artifact_id=adoption().adoption_id),
        ArtifactRef(kind=ArtifactKind.ACTION_WORK,artifact_id=work().action_work_id),
        ArtifactRef(kind=ArtifactKind.OUTCOME,artifact_id=outcome().outcome_id),
        ArtifactRef(kind=ArtifactKind.MEMORY,artifact_id=memory().memory_id),
    )


def test_contract_version_is_explicit():
    assert PRODUCT_CONTRACT_VERSION=="core-b-product-v1"


def test_company_context_is_stable_and_has_no_company_table_requirement():
    a=company_context(principal=principal(),analytical_context_available=True,entity_refs=("company:acme",),sector_pack_refs=("domain-pack:finance",))
    b=company_context(principal=principal(),analytical_context_available=True,entity_refs=("company:acme",),sector_pack_refs=("domain-pack:finance",))
    assert a==b
    assert a.company_identity==f"id:{TENANT}"
    assert a.deep_link_id==f"context:{a.context_id}"


def test_capability_discovery_exposes_deferred_capabilities():
    c=capability_discovery(principal=principal(),analytical_context_available=False)
    by_id={x.capability_id:x.status for x in c.capabilities}
    assert by_id["research.ask"]==CapabilityStatus.DATA_DEPENDENT
    assert by_id["cash_forecast"]==CapabilityStatus.SPECIAL_ENGINE_DEFERRED
    assert by_id["external_action_execution"]==CapabilityStatus.PRODUCTIZATION_DEFERRED
    assert by_id["company_map"]==CapabilityStatus.FOUNDATION_ONLY


def test_native_context_promotes_research_capability_only():
    c=capability_discovery(principal=principal(),analytical_context_available=True)
    by_id={x.capability_id:x.status for x in c.capabilities}
    assert by_id["research.ask"]==CapabilityStatus.SUPPORTED
    assert by_id["cash_forecast"]==CapabilityStatus.SPECIAL_ENGINE_DEFERRED


def test_resume_reauthorizes_current_principal():
    src=sources()
    service=HeadlessProductService(sources=src)
    ref=ArtifactRef(kind=ArtifactKind.RESEARCH,artifact_id=research_session().session_id)
    item=service.resume(ref=ref,principal=principal())
    assert item.header.kind==ArtifactKind.RESEARCH
    with pytest.raises(ProductError) as exc:
        service.resume(ref=ref,principal=principal(roles=("viewer",)))
    assert exc.value.code==ProductErrorCode.UNAVAILABLE
    assert len(src.research.calls)==2


def test_foreign_and_missing_are_non_oracle():
    service=HeadlessProductService(sources=sources())
    real=ArtifactRef(kind=ArtifactKind.REPORT,artifact_id=report().report_id)
    missing=ArtifactRef(kind=ArtifactKind.REPORT,artifact_id="p20r_"+"0"*24)
    with pytest.raises(ProductError) as foreign:
        service.resume(ref=real,principal=principal(tenant=OTHER))
    with pytest.raises(ProductError) as absent:
        service.resume(ref=missing,principal=principal())
    assert foreign.value.code==absent.value.code==ProductErrorCode.UNAVAILABLE
    assert foreign.value.detail==absent.value.detail


def test_evidence_resume_requires_durable_session_scope():
    service=HeadlessProductService(sources=sources())
    with pytest.raises(ProductError) as exc:
        service.resume(ref=ArtifactRef(kind=ArtifactKind.EVIDENCE,artifact_id="evi_"+"2"*24),principal=principal())
    assert exc.value.code==ProductErrorCode.UNAVAILABLE


def test_evidence_resume_uses_session_lineage():
    service=HeadlessProductService(sources=sources())
    dto=service.resume(ref=refs()[4],principal=principal())
    assert dto.header.kind==ArtifactKind.EVIDENCE
    assert dto.state=="VERIFIED"
    assert dto.receipt_refs==("dqr_"+"3"*24,)


@pytest.mark.parametrize(
    "index,state,expected",
    [
        (1,"SUPERSEDED",ProductCurrentness.SUPERSEDED),
        (6,"STALE_SOURCE_SET",ProductCurrentness.STALE),
        (7,"SUPERSEDED",ProductCurrentness.SUPERSEDED),
        (9,"SOURCE_ADOPTION_STALE",ProductCurrentness.STALE),
        (10,"SOURCE_WORK_STALE",ProductCurrentness.STALE),
        (11,"HISTORICAL_PRECEDENT",ProductCurrentness.HISTORICAL),
    ],
)
def test_currentness_is_visible(index,state,expected):
    kwargs={}
    if index==1: kwargs["signal_state"]=state
    elif index==6: kwargs["report_state"]=state
    elif index==7: kwargs["decision_state"]=state
    elif index==9: kwargs["work_state"]=state
    elif index==10: kwargs["outcome_state"]=state
    elif index==11: kwargs["memory_state"]=state
    service=HeadlessProductService(sources=sources(**kwargs))
    dto=service.resume(ref=refs()[index],principal=principal())
    assert dto.header.currentness==expected


def test_pagination_is_deterministic():
    service=HeadlessProductService(sources=sources())
    first=service.page(refs=refs()[:4],principal=principal(),limit=2)
    second=service.page(refs=refs()[:4],principal=principal(),limit=2,cursor=first.next_cursor)
    assert [x.header.kind for x in first.items]==[ArtifactKind.WATCH,ArtifactKind.SIGNAL]
    assert [x.header.kind for x in second.items]==[ArtifactKind.RESEARCH,ArtifactKind.INVESTIGATION]
    assert second.next_cursor is None


def test_invalid_cursor_fails_closed():
    service=HeadlessProductService(sources=sources())
    with pytest.raises(ProductError) as exc:
        service.page(refs=refs()[:2],principal=principal(),cursor="evil")
    assert exc.value.code==ProductErrorCode.UNAVAILABLE


def test_timeline_is_read_only_projection_in_chronological_order():
    service=HeadlessProductService(sources=sources())
    context=service.company_context(principal=principal(),analytical_context_available=True)
    timeline=service.timeline(context_id=context.context_id,refs=refs(),principal=principal())
    kinds=[x.ref.kind for x in timeline.items]
    assert kinds==list(ArtifactKind)
    assert [x.ordinal for x in timeline.items]==list(range(1,13))


def test_full_headless_closed_loop_is_green():
    service=HeadlessProductService(sources=sources())
    result=service.closed_loop(
        principal=principal(),
        analytical_context_available=True,
        refs=refs(),
        entity_refs=("company:acme",),
        sector_pack_refs=("domain-pack:finance",),
        correlation_id="corr-test-full-loop",
    )
    assert len(result.stages)==12
    assert len(result.complete_stage_kinds)==12
    assert result.trace.terminal_state=="GREEN"
    assert result.trace.correlation_id=="corr-test-full-loop"
    assert result.stages[-1].header.kind==ArtifactKind.MEMORY


def test_missing_evidence_is_explicit_insufficient_evidence():
    service=HeadlessProductService(sources=sources())
    no_evidence=tuple(ref for ref in refs() if ref.kind!=ArtifactKind.EVIDENCE)
    with pytest.raises(ProductError) as exc:
        service.closed_loop(principal=principal(),analytical_context_available=True,refs=no_evidence)
    assert exc.value.code==ProductErrorCode.INSUFFICIENT_EVIDENCE


def test_restart_resume_reconstructs_same_product_projection():
    ref=ArtifactRef(kind=ArtifactKind.REPORT,artifact_id=report().report_id)
    first=HeadlessProductService(sources=sources()).resume(ref=ref,principal=principal())
    restarted=HeadlessProductService(sources=sources()).resume(ref=ref,principal=principal())
    assert restarted==first


def test_correlation_is_deterministic_when_not_supplied():
    service=HeadlessProductService(sources=sources())
    a=service.trace(principal=principal(),operation="resume",owner_calls=("P20",),artifact_ids=(report().report_id,),terminal_state="CURRENT")
    b=service.trace(principal=principal(),operation="resume",owner_calls=("P20",),artifact_ids=(report().report_id,),terminal_state="CURRENT")
    assert a.correlation_id==b.correlation_id
    assert a.correlation_id.startswith("corr_")


@pytest.mark.parametrize(
    "owner_code,expected",
    [
        ("P20_REPORT_NOT_FOUND",ProductErrorCode.UNAVAILABLE),
        ("P20_REPORT_TENANT_MISMATCH",ProductErrorCode.UNAVAILABLE),
        ("ACTION_FORBIDDEN",ProductErrorCode.FORBIDDEN),
        ("REPORT_STALE",ProductErrorCode.STALE),
        ("WORK_SUPERSEDED",ProductErrorCode.SUPERSEDED),
        ("WORK_ILLEGAL_TRANSITION",ProductErrorCode.INVALID_TRANSITION),
        ("EVIDENCE_REQUIRED",ProductErrorCode.INSUFFICIENT_EVIDENCE),
        ("NO_DEFENSIBLE_ROOT_CAUSE",ProductErrorCode.INCONCLUSIVE),
        ("SPECIAL_CAPABILITY_DEFERRED",ProductErrorCode.DEFERRED_CAPABILITY),
    ],
)
def test_stable_error_taxonomy(owner_code,expected):
    assert normalize_owner_error(OwnerError(owner_code)).code==expected


def test_product_package_has_no_sqlmodel_or_analytics_engine_implementation():
    root=Path("app/v3/product")
    forbidden_imports=("sqlmodel","sqlalchemy","numpy","pandas","scipy","statistics","app.v3.substrate.metabase")
    for path in root.glob("*.py"):
        source=path.read_text(encoding="utf-8")
        tree=ast.parse(source)
        imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                imports.update(a.name for a in node.names)
            elif isinstance(node,ast.ImportFrom):
                imports.add(node.module or "")
        assert not any(name.startswith(forbidden_imports) for name in imports),(path,imports)
        for token in ("select(","Session(","ActionWorkRecord","ReportDocumentRecord","DecisionBriefRecord","DimaQueryReceipt("):
            assert token not in source,(path,token)
