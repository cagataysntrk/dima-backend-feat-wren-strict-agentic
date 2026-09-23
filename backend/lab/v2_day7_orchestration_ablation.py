"""Day7 post-acceptance orchestration shadow ablation.

Both arms start from the exact same typed AcceptedTurnContract fixture and use the
same governed semantic/execution trust plane. Only orchestration ergonomics differ.

FREE_COGNITION:
- no initial ResearchTask pre-materialization,
- evidence from governed data tools is marked inspected immediately,
- explicit inspect_evidence is not exposed,
- derived fanout registration remains because it protects hard task/fanout/idempotency
  safety rather than scheduling ergonomics.

GOVERNED_ORCHESTRATION:
- current Day7 seed/READY/inspect/frontier path unchanged.

This deliberately does not benchmark language interpretation, semantic linking, or
temporal normalization. Those are held fixed so the result answers the orchestration
question only.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "eval" / "v2_day7_orchestration_ablation.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day7_orchestration_ablation.json"

os.environ.setdefault(
    "DIMA_DATABASE_URL",
    "sqlite:///" + str(Path(tempfile.gettempdir()) / "dima-v2-day7-ablation.db"),
)
os.environ.setdefault("DIMA_LLM_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_RESEARCH_MANAGER_PROVIDER", "openrouter")
os.environ["DIMA_V2_RESEARCH_MANAGER_MODEL"] = os.getenv(
    "DIMA_DAY7_LIVE_MANAGER_MODEL", "openai/gpt-5.6-sol"
)
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")

from app.config import get_settings
from app.v2.acceptance import AcceptedContractRegistry, IntentAcceptanceGate
from app.v2.context_provider import ContextProviderV0
from app.v2.cross_domain_facts import CrossDomainJoinFactBuilder
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_lab import _build_role_scoped_manager_models
from app.v2.manager_loop import (
    ManagerActionKind,
    ManagerDecisionTransport,
    ResearchManagerLoop,
    _SYSTEM,
    _post_acceptance_native_schema,
)
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ResearchDirective,
    ResearchDirectiveCondition,
    ResearchDirectiveType,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    ConversationStateV2,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.relationship_adapter import (
    GovernedRelationshipAdapter,
    GovernedRelationshipExecutionContext,
)
from app.v2.research_tasks import ResearchSeedSet, ResearchTaskService
from app.v2.research_tools import ResearchToolRunner
from app.v2.runtime_boundary import tenant_binding
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_authority import AcceptedAuthorityRegistry
from control_plane.authorize import Principal

from lab.v2_day7_manager_live_sol import (
    Day7LiveSyntheticService,
    LiveContracts,
    semantic_schema,
)


class EvalBudgetExhausted(RuntimeError):
    pass


class PaidCallGuard:
    """Ablation-wide hard stop checked before every paid model request."""

    def __init__(self, max_calls: int) -> None:
        if max_calls < 1:
            raise ValueError("max_model_calls must be >= 1")
        self.max_calls = max_calls
        self.used = 0
        self.exhausted = False

    def reserve(self) -> None:
        if self.used >= self.max_calls:
            self.exhausted = True
            raise EvalBudgetExhausted(
                f"ablation model-call budget exhausted ({self.used}/{self.max_calls})"
            )
        self.used += 1


class CountingLLM:
    def __init__(self, inner, *, call_guard: PaidCallGuard) -> None:
        self.inner = inner
        self.call_guard = call_guard
        self.calls = 0
        self.latency_s = 0.0

    def structured_json(self, system, user, **kwargs):
        self.call_guard.reserve()
        started = time.perf_counter()
        self.calls += 1
        try:
            return self.inner.structured_json(system, user, **kwargs)
        finally:
            self.latency_s += time.perf_counter() - started


class NoPreseedResearchTaskService(ResearchTaskService):
    """Ablation-only: keep JIT lifecycle safety but remove initial scheduling scaffold."""

    def seed_initial_user_must(
        self,
        *,
        runtime,
        task_registry,
        executable_task_kinds,
        max_seed_tasks: int = 4,
    ) -> ResearchSeedSet:
        del task_registry, executable_task_kinds, max_seed_tasks
        ledger = runtime.ledger
        considered = (
            tuple(item.obligation_id for item in ledger.active_user_must)
            if ledger is not None
            else ()
        )
        return ResearchSeedSet(
            considered_obligation_ids=considered,
            registered_tasks=(),
            deferred_obligation_ids=(),
            already_accounted_obligation_ids=(),
        )


class AutoInspectResearchToolRunner(ResearchToolRunner):
    """Ablation-only observation barrier without spending a separate model turn."""

    def execute(self, **kwargs):
        execution = super().execute(**kwargs)
        runtime = kwargs["runtime"]
        evidence_ref = getattr(execution.observation, "evidence_ref", None)
        if evidence_ref and evidence_ref in runtime.snapshot.evidence_refs:
            runtime.mark_evidence_inspected(evidence_ref)
        return execution


def _free_action_schema() -> dict[str, Any]:
    schema = copy.deepcopy(_post_acceptance_native_schema())

    def remove_inspect(node: Any) -> None:
        if isinstance(node, dict):
            values = node.get("enum")
            if isinstance(values, list) and ManagerActionKind.INSPECT_EVIDENCE.value in values:
                node["enum"] = [
                    value
                    for value in values
                    if value != ManagerActionKind.INSPECT_EVIDENCE.value
                ]
            for value in node.values():
                remove_inspect(value)
        elif isinstance(node, list):
            for value in node:
                remove_inspect(value)

    remove_inspect(schema)
    return schema


_FREE_SYSTEM = _SYSTEM.replace(
    "- Use inspect_evidence before result-dependent replanning.",
    (
        "- This FREE_COGNITION shadow arm automatically marks governed data-tool Evidence "
        "as inspected; inspect_evidence is not exposed. Use CURRENT_RESULT_DELTA directly "
        "for result-dependent replanning."
    ),
) + (
    "\n- FREE_COGNITION does not pre-materialize initial READY tasks. "
    "Accepted USER_MUST analytics may be called directly; the runtime binds a JIT "
    "ResearchTask lease for hard idempotency/timeout safety."
)


class FreeCognitionLoop(ResearchManagerLoop):
    def _decision(
        self,
        *,
        question: str,
        runtime: ManagerRuntime,
        observations,
        conversation: ConversationStateV2 | None = None,
        action_frontier: dict[str, Any] | None = None,
        research_state=None,
        ready_tasks=(),
    ):
        user = self._prompt(
            question=question,
            runtime=runtime,
            observations=observations,
            conversation=conversation,
            action_frontier=action_frontier,
            research_state=research_state,
            ready_tasks=ready_tasks,
        )
        schema = _free_action_schema()
        kwargs = {
            "schema": schema,
            "schema_name": "dima_research_manager_free_cognition_action_v1",
        }
        raw = self._structured(_FREE_SYSTEM, user, **kwargs)
        try:
            return self._parse_decision(raw)
        except Exception as first_error:
            repair_system = (
                _FREE_SYSTEM
                + "\n\nFORMAT_REPAIR_ONLY: Previous output failed the application schema. "
                "Keep the SAME next action and semantic decision. Only fill/fix schema "
                "fields. Do not add/remove obligations, change polarity, or choose another tool."
            )
            repair_user = (
                user
                + "\n\nPREVIOUS_INVALID_OUTPUT:\n"
                + (raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False))
                + "\n\nFORMAT_ERROR:\n"
                + str(first_error)[:1200]
            )
            repaired = self._structured(repair_system, repair_user, **kwargs)
            return self._parse_decision(repaired)


def _runtime_identity(principal: Principal, service) -> TenantAnalyticsRuntimeV0:
    schema = service.schema()
    return TenantAnalyticsRuntimeV0(
        tenant_id=str(principal.tenant_id) if principal.tenant_id else None,
        tenant_slug=principal.tenant_slug,
        principal_user_id=str(principal.user_id),
        roles=tuple(sorted(str(role) for role in (principal.roles or []))),
        mdl_version=str(service.mdl_version),
        catalog=schema.get("catalog"),
        schema_name=schema.get("schema_name"),
        db_online=bool(schema.get("db_online", True)),
    )


def _target_kind(kind: str) -> SemanticTargetKind:
    if kind == "metric":
        return SemanticTargetKind.METRIC
    if kind == "dimension":
        return SemanticTargetKind.DIMENSION
    raise ValueError(f"unsupported ablation semantic kind: {kind}")


def _build_case_runtime(*, case: dict[str, Any], arm: str, llm):
    service = Day7LiveSyntheticService()
    principal = Principal(
        user_id="day7-ablation-user",
        tenant_id="day7-ablation-tenant",
        roles=["owner"],
        tenant_slug="day7-ablation",
    )
    tenant_runtime = _runtime_identity(principal, service)
    binding = tenant_binding(tenant_runtime)
    context = ContextProviderV0().build(service, tenant_runtime)
    context_version = context.context_version.version

    spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    question = str(case["question"])
    message_id = f"ablation:{case['id']}:turn"
    request_ref = f"ablation:{case['id']}"
    source_hash = spans.register_message(message_id=message_id, text=question)

    obligations: list[CandidateObligation] = []
    for obligation in case["obligations"]:
        source = spans.mint_exact(
            message_id=message_id,
            surface=str(obligation["source"]),
        )
        handle_ids: list[str] = []
        for index, semantic in enumerate(obligation.get("semantics") or ()):
            kind = str(semantic["kind"])
            target_kind = _target_kind(kind)
            handle = handles.mint_from_resolver(
                tenant_binding=binding,
                context_version=context_version,
                resolver_provenance_id=(
                    f"ablation:{case['id']}:{obligation['id']}:{index}"
                ),
                target_kind=kind,
                canonical_target=ResolvedSemanticRef(
                    candidate_id=(
                        f"ablation-{case['id']}-{obligation['id']}-{index}"
                    ),
                    target_kind=target_kind,
                    canonical_name=str(semantic["canonical"]),
                    cube_names=(str(semantic["cube"]),),
                ),
            )
            handle_ids.append(handle.handle_id)

        obligations.append(
            CandidateObligation(
                obligation_id=str(obligation["id"]),
                capability_key=ManagerCapabilityKey(str(obligation["capability"])),
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=tuple(handle_ids),
                ranking_direction=obligation.get("ranking_direction"),
                ranking_limit=obligation.get("ranking_limit"),
            )
        )

    directives: list[ResearchDirective] = []
    for directive in case.get("directives") or ():
        source = spans.mint_exact(
            message_id=message_id,
            surface=str(directive["source"]),
        )
        directive_type = ResearchDirectiveType(str(directive["type"]))
        condition = {
            ResearchDirectiveType.ADAPT_ON_EVIDENCE:
                ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION,
            ResearchDirectiveType.BROADEN_WITHIN_BUDGET:
                ResearchDirectiveCondition.WITHIN_SYSTEM_BUDGET,
        }[directive_type]
        directives.append(
            ResearchDirective(
                directive_id=str(directive["id"]),
                directive_type=directive_type,
                parent_obligation_id=str(directive["parent"]),
                condition=condition,
                source_refs=(source.source_ref,),
            )
        )

    acceptance = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    )
    core = ManagerCoreAnalyticsAdapter(semantic_handles=handles)
    contracts = LiveContracts()

    semantic_adapter = ManagerSemanticResolutionAdapter(
        source_spans=spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema=semantic_schema(),
        tenant_binding=binding,
        session_id=f"ablation-{case['id']}-{arm}",
        thread_id=f"ablation-{case['id']}",
        semantic_decision_provider=None,
        temporal_normalization_provider=None,
    )
    relationship = GovernedRelationshipAdapter(
        fact_builder=CrossDomainJoinFactBuilder(
            semantic_handles=handles,
            tenant_binding=binding,
            context_version=context_version,
        ),
        core_analytics=core,
        context=GovernedRelationshipExecutionContext(
            tenant_binding=binding,
            principal=principal,
            service=service,
            tenant_runtime=tenant_runtime,
            contract_store=contracts,
            session_id=f"ablation-{case['id']}-{arm}",
        ),
    )
    executor = GovernedManagerExecutor(
        acceptance=acceptance,
        core_analytics=core,
        context=GovernedManagerExecutionContext(
            tenant_binding=binding,
            context_version=context_version,
            principal=principal,
            service=service,
            tenant_runtime=tenant_runtime,
            contract_store=contracts,
            session_id=f"ablation-{case['id']}-{arm}",
        ),
        semantic_resolution=semantic_adapter,
        relationship=relationship,
    )

    runtime = ManagerRuntime(
        request_ref=request_ref,
        contract_registry=AcceptedContractRegistry(),
        authority_registry=AcceptedAuthorityRegistry(),
    )
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id=f"ablation:{case['id']}:typed",
        turn_id=message_id,
        request_ref=request_ref,
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=tuple(obligations),
        research_directives=tuple(directives),
    )
    step = runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={"envelope": envelope.model_dump(mode="json")},
        ),
        executor=executor,
    )
    result = step.tool_result
    if getattr(result, "status", None).value != "ACCEPTED":
        raise RuntimeError(
            f"typed ablation fixture failed acceptance: {getattr(result, 'reasons', ())}"
        )

    if arm == "GOVERNED_ORCHESTRATION":
        loop = ResearchManagerLoop(
            llm=llm,
            source_spans=spans,
            research_tool_runner=ResearchToolRunner(),
        )
    elif arm == "FREE_COGNITION":
        loop = FreeCognitionLoop(
            llm=llm,
            source_spans=spans,
            research_tool_runner=AutoInspectResearchToolRunner(),
            research_task_service=NoPreseedResearchTaskService(),
        )
    else:
        raise ValueError(f"unknown arm: {arm}")

    return {
        "loop": loop,
        "runtime": runtime,
        "executor": executor,
        "service": service,
        "question": question,
        "message_id": message_id,
        "request_ref": request_ref,
        "contract_id": runtime.snapshot.accepted_contract_id,
    }


def _record_case(
    *,
    case: dict[str, Any],
    arm: str,
    manager_llm,
    call_guard: PaidCallGuard,
) -> dict[str, Any]:
    counting = CountingLLM(manager_llm, call_guard=call_guard)
    fixture = _build_case_runtime(case=case, arm=arm, llm=counting)
    runtime = fixture["runtime"]
    service = fixture["service"]
    started = time.perf_counter()

    outcome = fixture["loop"].run(
        question=fixture["question"],
        message_id=fixture["message_id"],
        request_ref=fixture["request_ref"],
        runtime=runtime,
        executor=fixture["executor"],
        conversation=ConversationStateV2(),
    )
    elapsed = time.perf_counter() - started
    ledger = runtime.ledger
    user_must = list(ledger.active_user_must if ledger is not None else ())
    terminal_statuses = {"VERIFIED", "BLOCKED_DATA_GAP", "LIMITED", "UNSUPPORTED"}
    accounted = [
        item.obligation_id
        for item in user_must
        if item.status.value in terminal_statuses
    ]
    observations = list(outcome.observations)
    tool_rows = [
        item for item in observations
        if item.get("kind") == "tool"
        and item.get("tool") in {"run_analytics", "run_relationship"}
    ]
    task_ids = [
        str(item.get("research_task_id"))
        for item in tool_rows
        if item.get("research_task_id")
    ]
    repeated_or_no_progress = sum(
        1
        for item in observations
        if item.get("kind") in {"no_progress", "no_progress_blocked"}
    )
    fanout_selected = max(
        [
            len((item.get("result") or {}).get("selected_task_ids") or [])
            for item in observations
            if item.get("kind") == "fanout_registered"
        ]
        or [0]
    )

    safety_failures: list[str] = []
    if runtime.snapshot.accepted_contract_id is None:
        safety_failures.append("accepted_contract_absent")
    if runtime.snapshot.state.value == "FAILED":
        safety_failures.append("runtime_failed")
    if service.query_calls > int(case.get("max_queries", 8)):
        safety_failures.append("query_budget_case_cap")
    if len(set(task_ids)) < len(task_ids):
        safety_failures.append("duplicate_task_side_effect")
    if runtime.snapshot.data_queries > runtime.budget.max_data_queries:
        safety_failures.append("hard_data_query_budget")
    if runtime.snapshot.tool_calls > runtime.budget.max_tool_calls:
        safety_failures.append("hard_tool_budget")

    quality_success = (
        len(accounted) == len(user_must)
        and runtime.snapshot.state.value != "FAILED"
        and not safety_failures
    )

    return {
        "case_id": case["id"],
        "arm": arm,
        "accepted_contract_id": fixture["contract_id"],
        "quality_success": quality_success,
        "run_finished": outcome.run_finished,
        "terminal_status": (
            outcome.terminal_status.value if outcome.terminal_status is not None else None
        ),
        "state": runtime.snapshot.state.value,
        "user_must_count": len(user_must),
        "accounted_user_must_count": len(accounted),
        "manager_model_calls": counting.calls,
        "manager_model_latency_s": round(counting.latency_s, 4),
        "wall_latency_s": round(elapsed, 4),
        "service_queries": service.query_calls,
        "tool_calls": runtime.snapshot.tool_calls,
        "data_queries": runtime.snapshot.data_queries,
        "evidence_count": len(runtime.snapshot.evidence_refs),
        "inspected_evidence_count": len(runtime.snapshot.inspected_evidence_refs),
        "fanout_selected_max": fanout_selected,
        "repeated_or_no_progress_actions": repeated_or_no_progress,
        "safety_failures": safety_failures,
        "observations": observations,
    }


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    arms: dict[str, dict[str, Any]] = {}
    for arm in ("FREE_COGNITION", "GOVERNED_ORCHESTRATION"):
        rows = [row for row in records if row["arm"] == arm]
        arms[arm] = {
            "cases": len(rows),
            "quality_successes": sum(int(row["quality_success"]) for row in rows),
            "safety_failures": [
                {"case_id": row["case_id"], "failures": row["safety_failures"]}
                for row in rows if row["safety_failures"]
            ],
            "manager_model_calls": sum(row["manager_model_calls"] for row in rows),
            "manager_model_latency_s": round(
                sum(row["manager_model_latency_s"] for row in rows), 4
            ),
            "wall_latency_s": round(sum(row["wall_latency_s"] for row in rows), 4),
            "service_queries": sum(row["service_queries"] for row in rows),
            "tool_calls": sum(row["tool_calls"] for row in rows),
            "repeated_or_no_progress_actions": sum(
                row["repeated_or_no_progress_actions"] for row in rows
            ),
            "provider_billed_cost_usd": None,
            "cost_observability": (
                "current structured_json transport does not expose provider billed usage; "
                "manager_model_calls + latency are recorded as cost proxies"
            ),
        }

    by_case: list[dict[str, Any]] = []
    for case_id in sorted({row["case_id"] for row in records}):
        pair = {row["arm"]: row for row in records if row["case_id"] == case_id}
        if len(pair) == 2:
            if (
                pair["FREE_COGNITION"]["accepted_contract_id"]
                != pair["GOVERNED_ORCHESTRATION"]["accepted_contract_id"]
            ):
                raise RuntimeError(
                    f"accepted authority drift between arms: {case_id}"
                )
            by_case.append(
                {
                    "case_id": case_id,
                    "accepted_contract_id": pair["FREE_COGNITION"]["accepted_contract_id"],
                    "free_quality": pair["FREE_COGNITION"]["quality_success"],
                    "governed_quality": pair["GOVERNED_ORCHESTRATION"]["quality_success"],
                    "free_calls": pair["FREE_COGNITION"]["manager_model_calls"],
                    "governed_calls": pair["GOVERNED_ORCHESTRATION"]["manager_model_calls"],
                    "free_queries": pair["FREE_COGNITION"]["service_queries"],
                    "governed_queries": pair["GOVERNED_ORCHESTRATION"]["service_queries"],
                }
            )

    return {"arms": arms, "by_case": by_case}


def _parse_case_ids(values: list[str]) -> list[str]:
    selected: list[str] = []
    for raw in values:
        for item in str(raw).split(","):
            clean = item.strip()
            if clean and clean not in selected:
                selected.append(clean)
    return selected


def _select_cases(
    document: dict[str, Any],
    requested_values: list[str],
) -> list[dict[str, Any]]:
    requested = _parse_case_ids(requested_values)
    if not requested:
        raise ValueError(
            "explicit --case-id is required; broad Day7 ablation is forbidden by default"
        )
    by_id = {str(case["id"]): case for case in document.get("cases") or ()}
    unknown = [case_id for case_id in requested if case_id not in by_id]
    if unknown:
        raise ValueError(f"unknown ablation case ids: {unknown}")
    return [by_id[case_id] for case_id in requested]


def _dry_run_receipt(
    *,
    cases: list[dict[str, Any]],
    max_model_calls: int,
) -> dict[str, Any]:
    from app.v2.manager_models import ManagerBudget

    return {
        "kind": "dima_v2_day7_orchestration_shadow_ablation_dry_run",
        "selected_case_ids": [str(case["id"]) for case in cases],
        "selected_cases": len(cases),
        "arms": ["FREE_COGNITION", "GOVERNED_ORCHESTRATION"],
        "maximum_loop_records": len(cases) * 2,
        "configured_manager_hard_turn_cap": ManagerBudget().max_total_manager_turns,
        "model_calls_budget": max_model_calls,
        "provider_requests_made": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Explicit case id; repeat or pass comma-separated ids.",
    )
    parser.add_argument(
        "--max-model-calls",
        type=int,
        required=True,
        help="Ablation-wide hard paid-call ceiling checked before provider requests.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected scope/cost receipt without constructing provider clients.",
    )
    args = parser.parse_args()

    if args.max_model_calls < 1:
        raise SystemExit("--max-model-calls must be >= 1")

    document = yaml.safe_load(args.cases.read_text(encoding="utf-8"))
    try:
        cases = _select_cases(document, list(args.case_id or ()))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    dry_receipt = _dry_run_receipt(
        cases=cases,
        max_model_calls=args.max_model_calls,
    )
    if args.dry_run:
        print(json.dumps(dry_receipt, ensure_ascii=False))
        return 0

    settings = get_settings()
    (
        manager_llm,
        manager_profile,
        _linker_llm,
        _linker_profile,
        _temporal_llm,
        _temporal_profile,
    ) = _build_role_scoped_manager_models(settings)

    call_guard = PaidCallGuard(args.max_model_calls)
    records: list[dict[str, Any]] = []
    measurement_valid = True
    measurement_validity = "VALID"
    error = None
    try:
        for case in cases:
            for arm in ("FREE_COGNITION", "GOVERNED_ORCHESTRATION"):
                records.append(
                    _record_case(
                        case=case,
                        arm=arm,
                        manager_llm=manager_llm,
                        call_guard=call_guard,
                    )
                )
    except EvalBudgetExhausted as exc:
        measurement_valid = False
        measurement_validity = "EVAL_BUDGET_EXHAUSTED"
        error = f"{type(exc).__name__}: {exc}"
    except Exception as exc:
        measurement_valid = False
        measurement_validity = "HARNESS_FAILURE"
        error = f"{type(exc).__name__}: {exc}"

    aggregate = _aggregate(records) if records else {"arms": {}, "by_case": []}
    service_queries = sum(int(row.get("service_queries") or 0) for row in records)
    evaluable_cases = len(aggregate.get("by_case") or ())
    payload = {
        "kind": "dima_v2_day7_orchestration_shadow_ablation",
        "version": document.get("version"),
        "measurement_valid": measurement_valid and len(records) == len(cases) * 2,
        "measurement_validity": measurement_validity,
        "manager_model": manager_profile.model,
        "provider": manager_profile.provider,
        "workers": 1,
        "selected_case_ids": [str(case["id"]) for case in cases],
        "selected_cases": len(cases),
        "evaluable_cases": evaluable_cases,
        "completed_records": len(records),
        "maximum_loop_records": len(cases) * 2,
        "shared_accepted_authority_verified": (
            bool(aggregate["by_case"])
            and len(aggregate["by_case"]) == len(cases)
        ),
        "manager_model_calls": call_guard.used,
        "semantic_linker_calls": 0,
        "temporal_model_calls": 0,
        "total_model_calls": call_guard.used,
        "service_queries": service_queries,
        "model_calls_budget": call_guard.max_calls,
        "budget_exhausted": call_guard.exhausted,
        **aggregate,
        "error": error,
        "records": records,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False))

    # Quality differences are measurements. Invalid evaluator/provider budget is not.
    return 0 if payload["measurement_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
