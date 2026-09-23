"""One paid Day8-C cognition sentinel for ROOT_CAUSE.

This is intentionally NOT another Wren correctness test. The real-Wren deterministic
vertical is already covered by tests/test_v2_day8_real_wren_root_cause.py.

The live uncertainty is narrower:
  inspected VERIFIED Evidence
  -> Sol proposes a bounded hypothesis
  -> Sol selects one governed next test (without minting task identity)
  -> existing trust plane executes it and produces VERIFIED Evidence
  -> Sol inspects that Evidence
  -> Sol explicitly proposes SUPPORTS or CONTRADICTS
  -> deterministic epistemic gate keeps the public ceiling <= CANDIDATE_CAUSE.

No semantic-linker or temporal-model call is made in this sentinel.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Seal the live role before importing model/config construction.
LIVE_MANAGER_MODEL = "openai/gpt-5.6-sol"
MAX_AUTHORIZED_MODEL_CALLS = 8
SCENARIO_COUNT = 1

os.environ.setdefault("DIMA_LLM_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_RESEARCH_MANAGER_PROVIDER", "openrouter")
os.environ["DIMA_V2_RESEARCH_MANAGER_MODEL"] = LIVE_MANAGER_MODEL
os.environ.setdefault("DIMA_V2_SEMANTIC_LINKER_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_SEMANTIC_LINKER_MODEL", "openai/gpt-5.6-luna")
os.environ.setdefault("DIMA_V2_TEMPORAL_NORMALIZER_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_TEMPORAL_NORMALIZER_MODEL", "openai/gpt-5.6-sol")
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")

from app.config import get_settings
from app.v2.acceptance import IntentAcceptanceGate
from app.v2.epistemics import (
    CurrentRunEvidenceView,
    CurrentRunObligationView,
    EpistemicLabelGate,
    HypothesisLedger,
)
from app.v2.hypothesis_proposals import HypothesisProposalBoundary
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_lab import _build_role_scoped_manager_models
from app.v2.manager_loop import ManagerActionKind, ResearchManagerLoop
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    UserIntentEnvelope,
)
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityRegistry,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    EpistemicGateCode,
    EpistemicLabel,
    HypothesisEvidenceRelation,
    HypothesisEvidenceRelationProposal,
    HypothesisNextTestProposal,
    HypothesisProposal,
    ResearchTaskKind,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_state import build_research_state_view
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.research_tools import ResearchToolRunner
from app.v2.root_cause_orchestration import (
    HypothesisNextTestBoundary,
    RootCauseBootstrapPolicy,
    RootCauseBootstrapStatus,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class LiveBudgetExceeded(RuntimeError):
    pass


class LiveBehaviorFailure(RuntimeError):
    pass


class LiveCallBudget:
    """Hard paid-call ceiling for this one-scenario sentinel."""

    def __init__(self, max_calls: int) -> None:
        if max_calls < 1 or max_calls > MAX_AUTHORIZED_MODEL_CALLS:
            raise ValueError(
                f"max_model_calls must be between 1 and {MAX_AUTHORIZED_MODEL_CALLS}"
            )
        self.max_calls = max_calls
        self.manager_calls = 0

    def reserve(self) -> None:
        if self.manager_calls >= self.max_calls:
            raise LiveBudgetExceeded(
                f"Day8 live model-call ceiling exhausted "
                f"({self.manager_calls}/{self.max_calls})"
            )
        self.manager_calls += 1

    def receipt(self) -> dict[str, int]:
        return {
            "manager_model_calls": self.manager_calls,
            "semantic_linker_calls": 0,
            "temporal_model_calls": 0,
            "total_model_calls": self.manager_calls,
            "model_calls_budget": self.max_calls,
        }


class CountingManagerLLM:
    def __init__(self, inner, budget: LiveCallBudget) -> None:
        self._inner = inner
        self._budget = budget

    def __getattr__(self, name: str):
        return getattr(self._inner, name)

    def structured_json(self, *args, **kwargs):
        self._budget.reserve()
        return self._inner.structured_json(*args, **kwargs)


class ScriptedSentinelLLM:
    """Provider-free harness oracle for the exact live state machine."""

    def __init__(self) -> None:
        self.calls = 0

    def structured_json(self, _system, user, **_kwargs):
        self.calls += 1
        payload = json.loads(user)
        ledgers = payload.get("HYPOTHESIS_LEDGERS") or []
        entries = ledgers[0]["entries"] if ledgers else []
        ready = payload.get("READY_RESEARCH_TASKS") or []
        delta = payload.get("CURRENT_RESULT_DELTA")

        if not entries:
            evidence_refs = payload.get("EVIDENCE_REFS") or []
            return {
                "action": "propose_hypothesis",
                "hypothesis_parent_obligation_id": "U_ROOT",
                "hypothesis_statement": (
                    "Gözlenen düşüşün ölçüm seviyesindeki devamlılığı aday açıklama olabilir."
                ),
                "hypothesis_semantic_handles": ["h1"],
                "hypothesis_trigger_evidence_refs": [evidence_refs[-1]],
                "hypothesis_limitations": [
                    "Gözlemsel analitik sonuç tek başına nedenselliği doğrulamaz."
                ],
            }

        hypothesis = entries[0]
        if not hypothesis.get("next_test_task_refs"):
            return {
                "action": "propose_hypothesis_next_test",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "next_test_task_kind": "QUERY",
                "next_test_input_handles": ["h1"],
                "next_test_trigger_evidence_ref": hypothesis["trigger_evidence_refs"][-1],
                "next_test_material_reason": (
                    "Aday açıklamayı aynı governed metric üzerinde ayrı bir gözlemsel "
                    "ölçümle sınamak."
                ),
            }

        if ready:
            task = ready[0]
            return {
                "action": "run_analytics",
                "obligation_ids": ["U_ROOT"],
                "metric_handles": ["h1"],
                "derived_task_id": task["task_id"],
                "derived_parent_obligation_id": "U_ROOT",
                "derived_capability_key": "performance",
                "derived_evidence_ref": task["trigger_evidence_ref"],
                "derived_reason": "Materialized hypothesis next testini yürüt.",
            }

        if delta and not delta.get("inspected"):
            return {
                "action": "inspect_evidence",
                "evidence_ref": delta["evidence_ref"],
            }

        if not hypothesis.get("evidence_links"):
            assert delta is not None and delta.get("inspected")
            return {
                "action": "propose_hypothesis_evidence_relation",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "hypothesis_relation_evidence_ref": delta["evidence_ref"],
                "hypothesis_relation": "SUPPORTS",
            }

        raise AssertionError("scripted sentinel received an unexpected sixth cognition step")


class SyntheticGovernedService:
    """Deterministic warehouse stand-in; paid test does not re-test Wren."""

    mdl_version = "mdl-day8-live-sol-v1"

    def __init__(self) -> None:
        self.query_calls = 0

    def cube_sql(self, cube_query: dict) -> str:
        return "D8LIVESOL:" + json.dumps(cube_query, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        if principal is None:
            raise AssertionError("governed dry-plan requires principal")
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        if principal is None:
            raise AssertionError("governed query requires principal")
        self.query_calls += 1
        query = json.loads(sql.removeprefix("D8LIVESOL:"))
        measures = list(query.get("measures") or ())
        # Stable, non-empty observational result. The live oracle does not grade
        # whether SUPPORTS or CONTRADICTS is substantively correct; it grades that
        # the relation is explicit and Evidence-backed.
        value = 100.0 if self.query_calls == 1 else 96.0
        return {
            "columns": measures,
            "rows": [{metric: value for metric in measures}],
            "row_count": 1,
            "column_types": ["DOUBLE" for _ in measures],
        }


class ContractStore:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **_kwargs):
        self.n += 1
        return {"id": f"d8-live-qc-{self.n}", "sealed": True}


@dataclass
class SentinelFixture:
    question: str
    message_id: str
    request_ref: str
    tenant: str
    context_version: str
    spans: SourceSpanRegistry
    handles: SemanticHandleRegistry
    metric_handle: str
    principal: Principal
    service: SyntheticGovernedService
    contracts: ContractStore
    executor: GovernedManagerExecutor
    runtime: ManagerRuntime
    registry: ResearchTaskRegistry
    runner: ResearchToolRunner
    ledger: HypothesisLedger
    initial_evidence_ref: str


def _provider_failure_class(message: str) -> str | None:
    text = str(message or "").lower()
    quota = (
        "key limit exceeded",
        "quota",
        "rate limit",
        "rate_limit",
        "insufficient credits",
        "insufficient credit",
        "payment required",
        "402 client error",
        "429 client error",
    )
    if any(marker in text for marker in quota):
        return "PROVIDER_QUOTA_FAILURE"
    auth = ("401 client error", "403 client error", "unauthorized", "forbidden")
    if any(marker in text for marker in auth):
        return "PROVIDER_AUTH_FAILURE"
    unavailable = (
        "timed out",
        "timeout",
        "connection error",
        "connectionerror",
        "service unavailable",
        "bad gateway",
        "gateway timeout",
        "500 server error",
        "502 server error",
        "503 server error",
        "504 server error",
    )
    if any(marker in text for marker in unavailable):
        return "PROVIDER_UNAVAILABLE"
    return None


def _build_fixture() -> SentinelFixture:
    tenant = "day8-live-sol-tenant"
    context_version = "ctx-day8-live-sol-v1"
    message_id = "turn-day8-live-sol"
    request_ref = "req-day8-live-sol"
    root_id = "U_ROOT"
    question = (
        "Net gelirdeki düşüşün nedenini araştır. İlk gözlemsel kanıttan bir aday "
        "açıklama kur; onu governed bir takip testiyle sınamadan nedensel kesinlik verme."
    )

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface=question)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day8-live-sol:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day8-live-sol-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
        parent_obligation_id=root_id,
    )

    principal = Principal(
        user_id="day8-live-sol-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="day8-live-sol",
    )
    service = SyntheticGovernedService()
    contracts = ContractStore()
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(
            source_spans=spans,
            semantic_handles=handles,
        ),
        core_analytics=ManagerCoreAnalyticsAdapter(semantic_handles=handles),
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant,
            context_version=context_version,
            principal=principal,
            service=service,
            tenant_runtime=TenantAnalyticsRuntimeV0(
                tenant_id=tenant,
                tenant_slug="day8-live-sol",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=service.mdl_version,
                catalog="day8-live-sol",
                schema_name="main",
                db_online=True,
            ),
            contract_store=contracts,
            session_id="day8-live-sol-session",
        ),
    )

    runtime = ManagerRuntime(request_ref=request_ref)
    runtime.begin_understanding()
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id="day8-live-sol-attempt",
                    turn_id=message_id,
                    request_ref=request_ref,
                    source_message_hash=source_hash,
                    model_role="RESEARCH_MANAGER",
                    obligations=(
                        CandidateObligation(
                            obligation_id=root_id,
                            capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                            origin=ObligationOrigin.USER_MUST,
                            source_refs=(source.source_ref,),
                            semantic_handle_refs=(metric.handle_id,),
                        ),
                    ),
                ).model_dump(mode="json")
            },
        ),
        executor=executor,
    )

    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()
    bootstrap = RootCauseBootstrapPolicy(
        semantic_handles=handles,
    ).prepare(
        runtime=runtime,
        evidence_store=executor.evidence_store,
        task_registry=registry,
        root_obligation_id=root_id,
        tenant_binding=tenant,
        context_version=context_version,
    )
    if bootstrap.status != RootCauseBootstrapStatus.TASK_READY or bootstrap.task is None:
        raise RuntimeError(f"live sentinel bootstrap failed: {bootstrap}")

    first = runner.execute(
        task=bootstrap.task,
        tool_id=runner.tool_id_for_task(bootstrap.task),
        call=ManagerToolCall(
            name=ManagerToolName.RUN_ANALYTICS,
            args={
                "obligation_ids": (root_id,),
                "metric_handles": (metric.handle_id,),
            },
        ),
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    if not first.evidence.verified:
        raise RuntimeError("initial sentinel Evidence must be VERIFIED")
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.INSPECT_EVIDENCE,
            args={"evidence_ref": first.evidence.artifact_id},
        ),
        executor=executor,
    )

    ledger = HypothesisLedger(
        parent_obligation_id=root_id,
        accepted_contract_id=runtime.accepted_contract.contract_id,
        lineage_id=runtime.ledger.lineage_id,
        run_id=runtime.snapshot.run_id,
        obligation_ledger=runtime.ledger,
        evidence_store=executor.evidence_store,
        evidence_view=CurrentRunEvidenceView(runtime),
        obligation_view=CurrentRunObligationView(runtime),
        semantic_handles=handles,
        research_tasks=registry,
        tenant_binding=tenant,
        context_version=context_version,
    )

    return SentinelFixture(
        question=question,
        message_id=message_id,
        request_ref=request_ref,
        tenant=tenant,
        context_version=context_version,
        spans=spans,
        handles=handles,
        metric_handle=metric.handle_id,
        principal=principal,
        service=service,
        contracts=contracts,
        executor=executor,
        runtime=runtime,
        registry=registry,
        runner=runner,
        ledger=ledger,
        initial_evidence_ref=first.evidence.artifact_id,
    )


def _decide(
    *,
    loop: ResearchManagerLoop,
    fixture: SentinelFixture,
    observations: list[dict[str, Any]],
):
    return loop._decision(
        question=fixture.question,
        runtime=fixture.runtime,
        observations=observations,
        action_frontier={},
        research_state=build_research_state_view(
            runtime=fixture.runtime,
            evidence_store=fixture.executor.evidence_store,
        ),
        ready_tasks=fixture.registry.tasks,
        hypothesis_ledgers={"U_ROOT": fixture.ledger},
    )


def run_scenario(manager_llm) -> dict[str, Any]:
    fixture = _build_fixture()
    loop = ResearchManagerLoop(
        llm=manager_llm,
        source_spans=fixture.spans,
        research_tool_runner=fixture.runner,
    )
    observations: list[dict[str, Any]] = []
    action_sequence: list[str] = []

    # 1) Inspected VERIFIED Evidence -> bounded hypothesis.
    d1 = _decide(loop=loop, fixture=fixture, observations=observations)
    action_sequence.append(d1.action.value)
    if d1.action != ManagerActionKind.PROPOSE_HYPOTHESIS:
        raise LiveBehaviorFailure(
            f"expected propose_hypothesis first, got {d1.action.value}"
        )
    if not d1.hypothesis_limitations:
        raise LiveBehaviorFailure("live hypothesis must state an explicit limitation")
    hypothesis = HypothesisProposalBoundary(ledger=fixture.ledger).register(
        HypothesisProposal(
            statement=d1.hypothesis_statement,
            semantic_handle_refs=loop._decode_handles(d1.hypothesis_semantic_handles),
            trigger_evidence_refs=d1.hypothesis_trigger_evidence_refs,
            limitations=d1.hypothesis_limitations,
        )
    )
    observations.append(
        {
            "kind": "hypothesis_registered",
            "result": {
                "hypothesis_id": hypothesis.hypothesis_id,
                "trigger_evidence_refs": list(hypothesis.trigger_evidence_refs),
            },
        }
    )

    # 2) Hypothesis -> governed next-test proposal; server mints task identity.
    d2 = _decide(loop=loop, fixture=fixture, observations=observations)
    action_sequence.append(d2.action.value)
    if d2.action != ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST:
        raise LiveBehaviorFailure(
            f"expected propose_hypothesis_next_test second, got {d2.action.value}"
        )
    next_task = HypothesisNextTestBoundary(
        ledger=fixture.ledger,
        runtime=fixture.runtime,
        evidence_store=fixture.executor.evidence_store,
        semantic_handles=fixture.handles,
        task_registry=fixture.registry,
        tenant_binding=fixture.tenant,
        context_version=fixture.context_version,
    ).materialize(
        HypothesisNextTestProposal(
            hypothesis_ref=d2.hypothesis_ref,
            task_kind=d2.next_test_task_kind,
            input_refs=loop._decode_handles(d2.next_test_input_handles),
            trigger_evidence_ref=d2.next_test_trigger_evidence_ref,
            material_reason=d2.next_test_material_reason,
            ranking_direction=d2.next_test_ranking_direction,
            ranking_limit=d2.next_test_ranking_limit,
        )
    )
    if not next_task.task_id.startswith("rt_"):
        raise LiveBehaviorFailure("server-owned next-test identity is not canonical rt_*")
    observations.append(
        {
            "kind": "hypothesis_next_test_registered",
            "result": {
                "hypothesis_id": hypothesis.hypothesis_id,
                "task_id": next_task.task_id,
                "task_kind": next_task.task_kind,
                "trigger_evidence_ref": next_task.trigger_evidence_ref,
            },
        }
    )

    # 3) Model selects the already-materialized task; trust plane executes it.
    d3 = _decide(loop=loop, fixture=fixture, observations=observations)
    action_sequence.append(d3.action.value)
    if d3.action != ManagerActionKind.RUN_ANALYTICS:
        raise LiveBehaviorFailure(
            f"expected run_analytics third, got {d3.action.value}"
        )
    if d3.derived_task_id != next_task.task_id:
        raise LiveBehaviorFailure("model did not select the server-materialized next-test task")
    call = loop._compile_tool(
        decision=d3,
        message_id=fixture.message_id,
        source_hash="0" * 64,
        request_ref=fixture.request_ref,
        runtime=fixture.runtime,
    )
    if call is None:
        raise LiveBehaviorFailure("run_analytics did not compile to governed tool call")
    second = fixture.runner.execute(
        task=next_task,
        tool_id=fixture.runner.tool_id_for_task(next_task),
        call=call,
        runtime=fixture.runtime,
        executor=fixture.executor,
        principal=fixture.principal,
        task_registry=fixture.registry,
    )
    if not second.evidence.verified:
        raise LiveBehaviorFailure("follow-up next test did not produce VERIFIED Evidence")
    observations.append(
        {
            "kind": "tool",
            "tool": call.name.value,
            "research_task_id": next_task.task_id,
            "result": {
                "evidence_ref": second.evidence.artifact_id,
                "verified": second.evidence.verified,
            },
        }
    )

    # 4) VERIFIED result must be inspected before epistemic use.
    d4 = _decide(loop=loop, fixture=fixture, observations=observations)
    action_sequence.append(d4.action.value)
    if d4.action != ManagerActionKind.INSPECT_EVIDENCE:
        raise LiveBehaviorFailure(
            f"expected inspect_evidence fourth, got {d4.action.value}"
        )
    if d4.evidence_ref != second.evidence.artifact_id:
        raise LiveBehaviorFailure("model inspected a stale/non-follow-up Evidence artifact")
    inspect_call = loop._compile_tool(
        decision=d4,
        message_id=fixture.message_id,
        source_hash="0" * 64,
        request_ref=fixture.request_ref,
        runtime=fixture.runtime,
    )
    fixture.runtime.call_tool(inspect_call, executor=fixture.executor)
    observations.append(
        {
            "kind": "evidence_inspected",
            "evidence_ref": second.evidence.artifact_id,
        }
    )

    # 5) Only after inspection may cognition propose SUPPORTS/CONTRADICTS.
    d5 = _decide(loop=loop, fixture=fixture, observations=observations)
    action_sequence.append(d5.action.value)
    if d5.action != ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION:
        raise LiveBehaviorFailure(
            "expected propose_hypothesis_evidence_relation fifth, "
            f"got {d5.action.value}"
        )
    if d5.hypothesis_relation_evidence_ref != second.evidence.artifact_id:
        raise LiveBehaviorFailure("epistemic relation did not use the inspected follow-up Evidence")
    updated = HypothesisProposalBoundary(ledger=fixture.ledger).attach_relation(
        HypothesisEvidenceRelationProposal(
            hypothesis_ref=d5.hypothesis_ref,
            evidence_ref=d5.hypothesis_relation_evidence_ref,
            relation=d5.hypothesis_relation,
        )
    )

    gate = EpistemicLabelGate()
    confirmed = gate.decide(
        requested_label=EpistemicLabel.CONFIRMED_CAUSE,
        evidence=(second.evidence,),
        hypothesis=updated,
        root_cause_authority=True,
    )
    if confirmed.allowed or confirmed.code != EpistemicGateCode.CAUSAL_NOT_IDENTIFIED:
        raise LiveBehaviorFailure("CONFIRMED_CAUSE ceiling was not enforced")

    candidate = gate.decide(
        requested_label=EpistemicLabel.CANDIDATE_CAUSE,
        evidence=(second.evidence,),
        hypothesis=updated,
        root_cause_authority=True,
    )

    root_spec = ManagerCapabilityRegistry().get(ManagerCapabilityKey.ROOT_CAUSE)
    if root_spec.execution_mode != ManagerCapabilityExecutionMode.ORCHESTRATED:
        raise LiveBehaviorFailure("ROOT_CAUSE execution mode drifted from ORCHESTRATED")
    if root_spec.executable:
        raise LiveBehaviorFailure("ROOT_CAUSE became directly executable")

    return {
        "status": "pass",
        "scenario_count": SCENARIO_COUNT,
        "workers": 1,
        "manager_model": LIVE_MANAGER_MODEL,
        "action_sequence": action_sequence,
        "initial_evidence_ref": fixture.initial_evidence_ref,
        "followup_evidence_ref": second.evidence.artifact_id,
        "followup_verified": second.evidence.verified,
        "followup_inspected": (
            second.evidence.artifact_id
            in fixture.runtime.snapshot.inspected_evidence_refs
        ),
        "relation": d5.hypothesis_relation.value,
        "candidate_cause_allowed": candidate.allowed,
        "confirmed_cause_allowed": confirmed.allowed,
        "confirmed_cause_code": confirmed.code.value,
        "root_cause_execution_mode": root_spec.execution_mode.value,
        "root_cause_direct_executable": root_spec.executable,
        "research_task_kind_root_cause_exists": hasattr(ResearchTaskKind, "ROOT_CAUSE"),
        "model_owned_next_test_task_id_field": (
            "task_id" in HypothesisNextTestProposal.model_fields
        ),
        "synthetic_governed_query_calls": fixture.service.query_calls,
        "query_contract_count": fixture.contracts.n,
    }


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-model-calls",
        type=int,
        default=MAX_AUTHORIZED_MODEL_CALLS,
    )
    parser.add_argument(
        "--output",
        default="lab/reports/v2_day8_root_cause_live_sol.json",
    )
    args = parser.parse_args()

    budget = LiveCallBudget(args.max_model_calls)
    output = Path(args.output)

    try:
        settings = get_settings()
        manager_llm, manager_profile, _linker, _linker_profile, _temporal, _temporal_profile = (
            _build_role_scoped_manager_models(settings)
        )
        if manager_profile.model != LIVE_MANAGER_MODEL:
            raise RuntimeError(
                f"live Manager model drift: {manager_profile.model} != {LIVE_MANAGER_MODEL}"
            )
        payload = run_scenario(CountingManagerLLM(manager_llm, budget))
        payload.update(
            {
                "measurement_valid": True,
                "measurement_validity": "VALID",
                **budget.receipt(),
            }
        )
        _write_report(output, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except LiveBehaviorFailure as exc:
        payload = {
            "status": "behavior_failure",
            "measurement_valid": True,
            "measurement_validity": "VALID",
            "scenario_count": SCENARIO_COUNT,
            "manager_model": LIVE_MANAGER_MODEL,
            "message": str(exc),
            **budget.receipt(),
        }
        _write_report(output, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1
    except LiveBudgetExceeded as exc:
        payload = {
            "status": "invalid_measurement",
            "measurement_valid": False,
            "measurement_validity": "EVAL_BUDGET_EXHAUSTED",
            "scenario_count": SCENARIO_COUNT,
            "manager_model": LIVE_MANAGER_MODEL,
            "message": str(exc),
            **budget.receipt(),
        }
        _write_report(output, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    except Exception as exc:
        provider_class = _provider_failure_class(str(exc))
        payload = {
            "status": "invalid_measurement" if provider_class else "harness_failure",
            "measurement_valid": False,
            "measurement_validity": provider_class or "HARNESS_FAILURE",
            "scenario_count": SCENARIO_COUNT,
            "manager_model": LIVE_MANAGER_MODEL,
            "message": str(exc),
            **budget.receipt(),
        }
        _write_report(output, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
