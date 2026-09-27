#!/usr/bin/env python3
"""Round-2 neutral 10x3 feature benchmark for the sealed Metabase/Metabot candidate."""
from __future__ import annotations
import argparse, hashlib, json, os, time
from pathlib import Path
from typing import Any

from lab.metabase.core_b import live_sentinel as sealed
from app.v3.research_intake import (
    AllowedRelationship, ResearchIntakeCatalog, ResearchIntakeTerminal,
)
from app.v3.research_contracts import ResearchSemanticRef, SemanticTargetKind
from control_plane.authorize import Principal

MODEL="openai/gpt-5.6-luna"
CONTEXT="round2-neutral-context-v1"
USER_ID="round2-user"
TENANT_ID="round2-tenant"

def metric(cid: str, name: str, mention: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=mention,candidate_id=cid,target_kind=SemanticTargetKind.METRIC,
        canonical_name=name,cube_names=("machine_operations",),
    )

def dim(cid: str, name: str, mention: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=mention,candidate_id=cid,target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=name,cube_names=("machine_operations",),
    )

def catalog() -> ResearchIntakeCatalog:
    refs=(
      metric("metric.machine_downtime_minutes","Machine Downtime Minutes","makine duruşları / duruş süresi / machine downtime"),
      metric("metric.fault_count","Fault Count","arıza sayısı / fault count"),
      metric("metric.performance_score","Performance Score","performans / performance"),
      metric("metric.maintenance_delay_hours","Maintenance Delay Hours","bakım gecikmesi / maintenance delay"),
      metric("metric.spare_part_delay_hours","Spare Part Delay Hours","yedek parça gecikmesi / spare part delay"),
      metric("metric.pm_compliance_pct","Preventive Maintenance Compliance","önleyici bakım uyumu / bakım uyumu / preventive maintenance compliance"),
      metric("metric.changeover_count","Changeover Count","changeover / değişim sayısı / setup değişimi"),
      metric("metric.operator_absence_hours","Operator Absence Hours","operatör devamsızlığı / operatör yokluğu / operator absence"),
      dim("dimension.department","Department","bölüm / departman / department"),
      dim("dimension.event_date","Event Date","tarih / date / Mayıs / Haziran"),
      dim("dimension.machine_id","Machine","makine / machine"),
    )
    rels=(
      AllowedRelationship(relationship_id="rel.downtime_fault.department",left_semantic_id="metric.machine_downtime_minutes",right_semantic_id="metric.fault_count",dimension_semantic_id="dimension.department"),
      AllowedRelationship(relationship_id="rel.downtime_performance.department",left_semantic_id="metric.machine_downtime_minutes",right_semantic_id="metric.performance_score",dimension_semantic_id="dimension.department"),
      AllowedRelationship(relationship_id="rel.downtime_maintenance.department",left_semantic_id="metric.machine_downtime_minutes",right_semantic_id="metric.maintenance_delay_hours",dimension_semantic_id="dimension.department"),
      AllowedRelationship(relationship_id="rel.downtime_spare.department",left_semantic_id="metric.machine_downtime_minutes",right_semantic_id="metric.spare_part_delay_hours",dimension_semantic_id="dimension.department"),
      AllowedRelationship(relationship_id="rel.downtime_pm.department",left_semantic_id="metric.machine_downtime_minutes",right_semantic_id="metric.pm_compliance_pct",dimension_semantic_id="dimension.department"),
      AllowedRelationship(relationship_id="rel.downtime_changeover.department",left_semantic_id="metric.machine_downtime_minutes",right_semantic_id="metric.changeover_count",dimension_semantic_id="dimension.department"),
      AllowedRelationship(relationship_id="rel.downtime_absence.department",left_semantic_id="metric.machine_downtime_minutes",right_semantic_id="metric.operator_absence_hours",dimension_semantic_id="dimension.department"),
    )
    return ResearchIntakeCatalog(context_version=CONTEXT,semantic_refs=refs,allowed_relationships=rels,supported_domains=("machine_operations",))

def principal() -> Principal:
    return sealed._principal()

def links(db_engine, session_ids: tuple[str,...]):
    out=[]
    for sid in session_ids:
        out.extend(sealed._links(db_engine,sid))
    return tuple(out)

def safe_dump(value: Any):
    if value is None: return None
    if hasattr(value,"model_dump"): return value.model_dump(mode="json")
    return value

def result_payload(link):
    raw=getattr(link,"native_result_json",None)
    if not raw: return None
    try: return json.loads(raw)
    except Exception: return {"_invalid_native_result_json":True}

def execute_turn(*,case,turn_no,question,prior_brief,intake,product,composer,p17_manager,p19_manager,reasoning,orchestrator,db_engine,native_token):
    started=time.monotonic()
    before=(intake.call_count,p17_manager.call_count,p19_manager.call_count)
    intake_result=product.research_question(question=question,catalog=catalog(),principal=principal(),prior_brief=prior_brief)
    intake_calls=intake.call_count-before[0]
    if intake_result.terminal != ResearchIntakeTerminal.READY:
        elapsed=int((time.monotonic()-started)*1000)
        terminal=intake_result.terminal.value
        units=intake_calls
        return {
          "turn":turn_no,"question":question,"terminal_state":terminal,"ready":False,
          "passed_turn":terminal in set(case["statuses"]),
          "model_calls_by_role":{"intake":intake_calls,"p17_manager":0,"p19_manager":0,"metabot_stream_invocations":0},
          "observable_model_boundary_units":units,"metabase_analytical_calls":0,
          "evidence_count":0,"lineage_valid":True,"total_latency_ms":elapsed,
          "intake_payload":safe_dump(intake_result),"brief_payload":None,"composition_payload":None,
          "research_payload":None,"reasoning_steps":[],"native_results":[],"report_payload":None,"epistemic_payloads":[],
        }, None
    brief=intake_result.brief
    assert brief is not None
    composition=composer.compose(
      brief=brief,principal=principal(),request_ref=f"round2:{case['id']}:{turn_no}",
      source_message_hash=hashlib.sha256(question.encode("utf-8")).hexdigest(),
      native_session_token=native_token,
      investigation_requirements=intake_result.investigation_requirements,
    )
    final=orchestrator.resume_state(session_id=composition.research_session_id,principal=principal())
    session_ids=(composition.research_session_id,*composition.child_research_session_ids)
    all_links=links(db_engine,session_ids)
    lineage_valid=all(x.status=="VERIFIED" and bool(x.receipt_id) and bool(x.evidence_id) for x in all_links if x.status=="VERIFIED") and not any(x.status=="FAILED" for x in all_links)
    p17_calls=p17_manager.call_count-before[1]
    p19_calls=p19_manager.call_count-before[2]
    metabot_calls=len(all_links)
    units=intake_calls+p17_calls+p19_calls+metabot_calls
    report_payload=None
    if composition.p20_report_ref:
        report_payload=safe_dump(composer._reports.load(report_id=composition.p20_report_ref,principal=principal()))
    epistemic_payloads=[]
    for ref in composition.p19_assessment_refs:
        try: epistemic_payloads.append(safe_dump(composer._epistemics.load_assessment(assessment_id=ref,principal=principal())))
        except Exception as exc: epistemic_payloads.append({"assessment_id":ref,"load_error":type(exc).__name__})
    reasoning_payload=[]
    for sid in session_ids:
        reasoning_payload.extend(safe_dump(x) for x in reasoning.steps(sid))
    elapsed=int((time.monotonic()-started)*1000)
    terminal=composition.terminal_state.value
    evidence_count=len(composition.evidence_refs)
    return {
      "turn":turn_no,"question":question,"terminal_state":terminal,"ready":True,
      "passed_turn":terminal in set(case["statuses"]) and evidence_count>=int(case.get("min_evidence",0)) and lineage_valid,
      "model_calls_by_role":{"intake":intake_calls,"p17_manager":p17_calls,"p19_manager":p19_calls,"metabot_stream_invocations":metabot_calls},
      "observable_model_boundary_units":units,"metabase_analytical_calls":metabot_calls,
      "evidence_count":evidence_count,"lineage_valid":lineage_valid,"total_latency_ms":elapsed,
      "intake_payload":safe_dump(intake_result),"brief_payload":safe_dump(brief),
      "composition_payload":safe_dump(composition),"research_payload":safe_dump(final),
      "reasoning_steps":reasoning_payload,"native_results":[result_payload(x) for x in all_links if result_payload(x) is not None],
      "report_payload":report_payload,"epistemic_payloads":epistemic_payloads,
      "p18_policy_use_refs":list(composition.p18_policy_use_refs),
      "p19_assessment_refs":list(composition.p19_assessment_refs),
      "p20_report_ref":composition.p20_report_ref,
      "limitations":[safe_dump(x) for x in composition.limitations],
    }, brief

def run_case(*,case,intake,product,composer,p17_manager,p19_manager,reasoning,orchestrator,db_engine,native_token):
    started=time.monotonic()
    turns=case.get("turns") if case.get("kind")=="multi_turn" else [case["question"]]
    prior=None; records=[]
    for i,q in enumerate(turns,start=1):
        rec, prior=execute_turn(
          case=case,turn_no=i,question=q,prior_brief=prior,intake=intake,product=product,composer=composer,
          p17_manager=p17_manager,p19_manager=p19_manager,reasoning=reasoning,orchestrator=orchestrator,
          db_engine=db_engine,native_token=native_token,
        )
        records.append(rec)
        if not rec["ready"] and i < len(turns):
            break
    total_units=sum(x["observable_model_boundary_units"] for x in records)
    final=records[-1]
    budget_ok=total_units<=int(case.get("max_model_calls",14))
    all_turns=len(records)==len(turns)
    passed=bool(final["passed_turn"] and budget_ok and all_turns)
    return {
      "id":case["id"],"feature_id":case["feature_id"],"feature_name":case["feature_name"],
      "difficulty":case["difficulty"],"kind":case["kind"],"question":case["question"],
      "turn_count_expected":len(turns),"turn_count_executed":len(records),"turns":records,
      "terminal_state":final["terminal_state"],"evidence_count":final["evidence_count"],
      "lineage_valid":final["lineage_valid"],"observable_model_boundary_units":total_units,
      "case_model_call_ceiling":case.get("max_model_calls"),
      "metabase_analytical_calls":sum(x["metabase_analytical_calls"] for x in records),
      "total_latency_ms":int((time.monotonic()-started)*1000),
      "budget_ok":budget_ok,"all_turns_executed":all_turns,"passed":passed,
      "expected":case.get("expected",{}),
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-url",required=True); ap.add_argument("--email",required=True); ap.add_argument("--password",required=True)
    ap.add_argument("--manifest",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--control-db",type=Path,required=True)
    ap.add_argument("--engine-sha",required=True); ap.add_argument("--upstream-sha",required=True); ap.add_argument("--runtime-tag",required=True)
    ap.add_argument("--runtime-image-digest",required=True); ap.add_argument("--build-identity",required=True); ap.add_argument("--image-identity",required=True); ap.add_argument("--platform-sha",required=True)
    ap.add_argument("--max-total-model-units",type=int,default=180)
    args=ap.parse_args()
    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    cases=list(manifest["cases"])
    if len(cases)!=30: raise RuntimeError("round2 benchmark requires exactly 30 cases")
    api_key=os.environ.get("DIMA_OPENROUTER_API_KEY","").strip()
    if not api_key: raise RuntimeError("DIMA_OPENROUTER_API_KEY required")
    token,current=sealed._login(args.base_url,args.email,args.password)
    db_engine=sealed._build_control_plane(args.control_db,int(current["id"]))
    session_store=sealed.ResearchSessionStore(db_engine)
    expected=sealed.NativeEngineIdentity(
      engine_sha=args.engine_sha,upstream_base_sha=args.upstream_sha,runtime_tag=args.runtime_tag,
      runtime_image_digest=args.runtime_image_digest,build_identity=args.build_identity,runtime_image_identity=args.image_identity,
    )
    subjects=sealed.NativeSubjectSessionProvider(base_url=args.base_url,expected_identity=expected,db_engine=db_engine)
    material_executor=sealed.NativeResearchMaterialExecutor(subject_provider=subjects,store=session_store,expected_identity=expected)
    orchestrator=sealed.ResearchAskOrchestrator(store=session_store,bridge_factory=subjects,material_executor=material_executor)
    intake_transport=sealed.OpenRouterStructuredJSONTransport(api_key=api_key,model=MODEL)
    p17_transport=sealed.OpenRouterStructuredJSONTransport(api_key=api_key,model=MODEL)
    p19_transport=sealed.OpenRouterStructuredJSONTransport(api_key=api_key,model=MODEL)
    intake=sealed.ResearchIntakeCompiler(transport=intake_transport)
    product=sealed.HeadlessProductService(sources=sealed.ProductSources(research=orchestrator,intake=intake))
    reasoning=sealed.ResearchReasoningStore(db_engine)
    claim_store=sealed.ClaimLineageStore(research_store=session_store,db_engine=db_engine)
    occurrence_runner=sealed.NativeResearchOccurrenceRunner(store=session_store,bridge_factory=subjects,material_executor=material_executor)
    exploration=sealed.NativeResearchExploration(research_store=session_store,subject_provider=subjects)
    p17=sealed.ResearchInvestigationManager(
      research_store=session_store,claim_store=claim_store,reasoning_store=reasoning,
      followup_executor=sealed.NativeResearchFollowupExecutor(store=session_store,occurrence_runner=occurrence_runner,exploration=exploration),
      db_engine=db_engine,
    )
    p17_manager=sealed.StructuredResearchProposalManager(transport=p17_transport)
    p18=sealed.BusinessRelationshipPolicyStore(research_store=session_store,db_engine=db_engine)
    p19=sealed.HypothesisRootCauseStore(research_store=session_store,db_engine=db_engine)
    p19_manager=sealed.StructuredP19AssessmentManager(transport=p19_transport)
    p20=sealed.ReportDocumentStore(research_store=session_store,db_engine=db_engine)
    routing=sealed.ProductInvestigationRequirementStore(db_engine)
    composer=sealed.HeadlessProductComposer(
      research=orchestrator,investigation=p17,investigation_manager=p17_manager,reasoning=reasoning,
      relationships=p18,epistemics=p19,epistemic_manager=p19_manager,reports=p20,investigation_requirements=routing,
    )
    observations=[]
    used_units=0
    try:
      for case in cases:
        if used_units + int(case.get("max_model_calls",14)) > args.max_total_model_units:
          observations.append({
            "id":case["id"],"feature_id":case["feature_id"],"feature_name":case["feature_name"],
            "difficulty":case["difficulty"],"kind":case["kind"],"question":case["question"],
            "turn_count_expected":len(case.get("turns") or [case["question"]]),"turn_count_executed":0,
            "turns":[],"terminal_state":"BUDGET_EXHAUSTED","evidence_count":0,"lineage_valid":True,
            "observable_model_boundary_units":0,"case_model_call_ceiling":case.get("max_model_calls"),
            "metabase_analytical_calls":0,"total_latency_ms":0,"budget_ok":False,
            "all_turns_executed":False,"passed":False,"expected":case.get("expected",{}),
            "failure_class":"GLOBAL_MODEL_BUDGET_EXHAUSTED",
          })
          continue
        result=run_case(
          case=case,intake=intake,product=product,composer=composer,p17_manager=p17_manager,p19_manager=p19_manager,
          reasoning=reasoning,orchestrator=orchestrator,db_engine=db_engine,native_token=token,
        )
        observations.append(result)
        used_units += int(result["observable_model_boundary_units"])
    finally:
      intake_transport.close(); p17_transport.close(); p19_transport.close()
    total_units=sum(x["observable_model_boundary_units"] for x in observations)
    report={
      "schema_version":"dima_neutral_feature_benchmark_round2_v2",
      "system":"metabase-platform","platform_sha":args.platform_sha,"engine_sha":args.engine_sha,
      "engine_runtime_tag":args.runtime_tag,"fixture":manifest["fixture"],"manifest_version":manifest["version"],
      "model_topology":{"research_intake":MODEL,"p17_manager":MODEL,"p19_manager":MODEL,"metabot":"openrouter/openai/gpt-5.6-luna"},
      "case_count":len(observations),"passed":sum(bool(x["passed"]) for x in observations),
      "failed":sum(not bool(x["passed"]) for x in observations),
      "observable_model_boundary_units":total_units,"model_budget_ceiling":args.max_total_model_units,
      "metabase_analytical_calls":sum(x["metabase_analytical_calls"] for x in observations),
      "cases":observations,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf-8")
    print(json.dumps({"passed":report["passed"],"failed":report["failed"],"units":total_units,"metabase_calls":report["metabase_analytical_calls"]},ensure_ascii=False))
    return 0
if __name__=="__main__": raise SystemExit(main())
