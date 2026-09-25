"""Day 7 declarative Research tool contracts and the first governed vertical.

This module is intentionally not an agent kernel. It sits in front of the existing
ManagerRuntime/GovernedManagerExecutor boundary and answers only:

    is this typed ResearchTask allowed to invoke this declared governed tool?

Numeric/query truth remains ManagerCoreAnalyticsAdapter -> CubePlanner -> Wren ->
QueryContract/Evidence.  Missing principal fails closed before execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable

from pydantic import Field

from app.v2.manager_tools import (
    ManagerAnalyticsObservation,
    ManagerRelationshipObservation,
    ManagerToolCall,
    ManagerToolName,
    RunAnalyticsArgs,
    RunRelationshipArgs,
)
from app.v2.manager_progress import action_fingerprint
from app.v2.models import EvidenceArtifact, FrozenModel, ResearchTask, ResearchTaskKind
from app.v2.research_tasks import ResearchTaskRegistry
from control_plane.authorize import AuthzError, Principal, authorize


class ResearchToolAuthority(StrEnum):
    ACCEPTED_RESEARCH = "ACCEPTED_RESEARCH_AUTHORITY"


class ResearchToolCostClass(StrEnum):
    ZERO = "ZERO"
    CHEAP = "CHEAP"
    MODERATE = "MODERATE"
    EXPENSIVE = "EXPENSIVE"


class ResearchToolContract(FrozenModel):
    tool_id: str = Field(min_length=1)
    accepted_task_kinds: tuple[ResearchTaskKind, ...] = Field(min_length=1)
    input_schema: str = Field(min_length=1)
    output_schema: str = Field(min_length=1)
    authority: ResearchToolAuthority
    evidence_kind: str = Field(min_length=1)
    max_rows: int = Field(ge=1)
    timeout_ms: int = Field(ge=1)
    cost_class: ResearchToolCostClass
    required_permissions: tuple[str, ...] = Field(min_length=1)


@dataclass(frozen=True)
class ResearchToolSpec:
    contract: ResearchToolContract
    manager_tool: ManagerToolName
    args_model: type[FrozenModel]
    output_model: type[FrozenModel]


@dataclass(frozen=True)
class ResearchToolExecution:
    task: ResearchTask
    contract: ResearchToolContract
    observation: FrozenModel
    evidence: EvidenceArtifact | None
    elapsed_ms: float


class ResearchToolContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class ResearchExecutionOutcome:
    """Generic terminal projection for governed Research execution.

    Consumers must not infer success merely because a tool returned. Exactly two
    terminal shapes are admissible here:

    - COMPLETE with VERIFIED Evidence
    - BLOCKED with no Evidence

    Any third shape is a contract violation and fails closed.
    """

    execution: ResearchToolExecution
    blocked: bool

    @classmethod
    def project(cls, execution: ResearchToolExecution) -> "ResearchExecutionOutcome":
        evidence = execution.evidence
        if evidence is not None:
            if execution.task.state != "complete":
                raise ResearchToolContractError(
                    "Research execution with Evidence must be COMPLETE"
                )
            if not evidence.verified:
                raise ResearchToolContractError(
                    "Research execution success requires VERIFIED Evidence"
                )
            return cls(execution=execution, blocked=False)

        if execution.task.state == "blocked":
            return cls(execution=execution, blocked=True)

        raise ResearchToolContractError(
            "Research execution must terminate as COMPLETE + VERIFIED Evidence "
            "or governed BLOCKED + no Evidence"
        )

    def require_evidence(self) -> EvidenceArtifact:
        if self.blocked or self.execution.evidence is None:
            raise ResearchToolContractError(
                "governed BLOCKED Research execution has no Evidence"
            )
        return self.execution.evidence


class ResearchToolRegistry:
    """Closed Day 7 tool registry.

    Families are declared only after an existing governed Dima/Wren primitive is
    proven to produce verified Evidence/QueryContract output.
    """

    _SPECS = {
        "wren.query": ResearchToolSpec(
            contract=ResearchToolContract(
                tool_id="wren.query",
                accepted_task_kinds=(ResearchTaskKind.QUERY,),
                input_schema="RunAnalyticsArgs@v1",
                output_schema="ManagerAnalyticsObservation@v1",
                authority=ResearchToolAuthority.ACCEPTED_RESEARCH,
                evidence_kind="standard_analytics",
                max_rows=20,
                timeout_ms=15_000,
                cost_class=ResearchToolCostClass.CHEAP,
                required_permissions=("query:run",),
            ),
            manager_tool=ManagerToolName.RUN_ANALYTICS,
            args_model=RunAnalyticsArgs,
            output_model=ManagerAnalyticsObservation,
        ),
        "wren.breakdown": ResearchToolSpec(
            contract=ResearchToolContract(
                tool_id="wren.breakdown",
                accepted_task_kinds=(ResearchTaskKind.BREAKDOWN,),
                input_schema="RunAnalyticsArgs@v1",
                output_schema="ManagerAnalyticsObservation@v1",
                authority=ResearchToolAuthority.ACCEPTED_RESEARCH,
                evidence_kind="standard_analytics",
                max_rows=20,
                timeout_ms=15_000,
                cost_class=ResearchToolCostClass.CHEAP,
                required_permissions=("query:run",),
            ),
            manager_tool=ManagerToolName.RUN_ANALYTICS,
            args_model=RunAnalyticsArgs,
            output_model=ManagerAnalyticsObservation,
        ),
        "wren.compare": ResearchToolSpec(
            contract=ResearchToolContract(
                tool_id="wren.compare",
                accepted_task_kinds=(ResearchTaskKind.COMPARE,),
                input_schema="RunAnalyticsArgs@v1",
                output_schema="ManagerAnalyticsObservation@v1",
                authority=ResearchToolAuthority.ACCEPTED_RESEARCH,
                evidence_kind="standard_analytics",
                max_rows=20,
                timeout_ms=15_000,
                cost_class=ResearchToolCostClass.MODERATE,
                required_permissions=("query:run",),
            ),
            manager_tool=ManagerToolName.RUN_ANALYTICS,
            args_model=RunAnalyticsArgs,
            output_model=ManagerAnalyticsObservation,
        ),
        "wren.rank": ResearchToolSpec(
            contract=ResearchToolContract(
                tool_id="wren.rank",
                accepted_task_kinds=(ResearchTaskKind.RANK,),
                input_schema="RunAnalyticsArgs@v1",
                output_schema="ManagerAnalyticsObservation@v1",
                authority=ResearchToolAuthority.ACCEPTED_RESEARCH,
                evidence_kind="standard_analytics",
                max_rows=20,
                timeout_ms=15_000,
                cost_class=ResearchToolCostClass.CHEAP,
                required_permissions=("query:run",),
            ),
            manager_tool=ManagerToolName.RUN_ANALYTICS,
            args_model=RunAnalyticsArgs,
            output_model=ManagerAnalyticsObservation,
        ),
        "wren.relationship": ResearchToolSpec(
            contract=ResearchToolContract(
                tool_id="wren.relationship",
                accepted_task_kinds=(ResearchTaskKind.RELATIONSHIP,),
                input_schema="RunRelationshipArgs@v1",
                output_schema="ManagerRelationshipObservation@v1",
                authority=ResearchToolAuthority.ACCEPTED_RESEARCH,
                evidence_kind="relationship_analytics",
                max_rows=20,
                timeout_ms=15_000,
                cost_class=ResearchToolCostClass.MODERATE,
                required_permissions=("query:run",),
            ),
            manager_tool=ManagerToolName.RUN_RELATIONSHIP,
            args_model=RunRelationshipArgs,
            output_model=ManagerRelationshipObservation,
        ),
    }

    def spec(self, tool_id: str) -> ResearchToolSpec:
        try:
            return self._SPECS[tool_id]
        except KeyError as exc:
            raise ResearchToolContractError(
                f"undeclared Research tool: {tool_id}"
            ) from exc

    def tool_id_for_task_kind(self, task_kind: ResearchTaskKind) -> str:
        matches = [
            tool_id
            for tool_id, spec in self._SPECS.items()
            if task_kind in spec.contract.accepted_task_kinds
        ]
        if len(matches) != 1:
            raise ResearchToolContractError(
                f"Research task kind {task_kind.value} has {len(matches)} declared tools"
            )
        return matches[0]

    @staticmethod
    def _task_kind(task: ResearchTask) -> ResearchTaskKind:
        try:
            return ResearchTaskKind(task.task_kind)
        except ValueError as exc:
            raise ResearchToolContractError(
                f"unregistered Research task kind: {task.task_kind}"
            ) from exc

    @staticmethod
    def _used_handles(args: RunAnalyticsArgs) -> set[str]:
        values = {
            *args.metric_handles,
            *args.dimension_handles,
            *args.filter_handles,
        }
        if args.period_handle is not None:
            values.add(args.period_handle)
        if args.comparison_handle is not None:
            values.add(args.comparison_handle)
        return values

    def validate_invocation(
        self,
        *,
        task: ResearchTask,
        tool_id: str,
        call: ManagerToolCall,
        principal: Principal | None,
    ) -> tuple[ResearchToolSpec, FrozenModel]:
        spec = self.spec(tool_id)
        task_kind = self._task_kind(task)

        if task.state not in {"pending", "running"}:
            raise ResearchToolContractError(
                f"Research task {task.task_id} state {task.state} execute edilemez"
            )
        if task_kind not in spec.contract.accepted_task_kinds:
            raise ResearchToolContractError(
                f"tool {tool_id} task kind {task_kind.value} kabul etmiyor"
            )
        if call.name != spec.manager_tool:
            raise ResearchToolContractError(
                f"tool {tool_id} Manager tool mismatch: {call.name.value}"
            )
        if principal is None:
            raise ResearchToolContractError(
                "missing principal: Research execution fail-closed"
            )

        for permission in spec.contract.required_permissions:
            try:
                authorize(principal, permission, f"research:{tool_id}")
            except AuthzError as exc:
                raise ResearchToolContractError(
                    f"Research permission denied for {permission}: {exc}"
                ) from exc

        try:
            validated = spec.args_model.model_validate(call.args)
        except Exception as exc:
            raise ResearchToolContractError(
                f"Research tool input schema mismatch for {tool_id}: {exc}"
            ) from exc

        if isinstance(validated, RunRelationshipArgs):
            undeclared_handles = {
                *validated.focus_handles,
                *validated.counterpart_handles,
            } - set(task.input_refs)
            if undeclared_handles:
                raise ResearchToolContractError(
                    "Research relationship task did not declare semantic inputs: "
                    + ", ".join(sorted(undeclared_handles))
                )
            if task_kind != ResearchTaskKind.RELATIONSHIP:
                raise ResearchToolContractError(
                    "RunRelationshipArgs requires RELATIONSHIP task kind"
                )
            if task.question_id != validated.obligation_id:
                raise ResearchToolContractError(
                    "RELATIONSHIP task must bind to its accepted obligation"
                )
            if validated.research_task_id is not None:
                raise ResearchToolContractError(
                    "Manager cannot self-assign relationship research_task_id"
                )

        if isinstance(validated, RunAnalyticsArgs):
            # The typed task must already carry every opaque semantic input the worker
            # sends to the governed executor.  No raw-prompt or hidden-handle guessing.
            undeclared_handles = self._used_handles(validated) - set(task.input_refs)
            if undeclared_handles:
                raise ResearchToolContractError(
                    "Research task did not declare semantic inputs: "
                    + ", ".join(sorted(undeclared_handles))
                )

            # Tool-family shape is deterministic contract truth.  A tool name alone
            # never upgrades a generic query into a comparison/ranking/breakdown.
            if task_kind == ResearchTaskKind.QUERY:
                if validated.dimension_handles or validated.comparison_handle is not None or validated.ranking_direction is not None:
                    raise ResearchToolContractError(
                        "QUERY task cannot carry breakdown/comparison/ranking semantics"
                    )
            elif task_kind == ResearchTaskKind.BREAKDOWN:
                if not validated.dimension_handles:
                    raise ResearchToolContractError(
                        "BREAKDOWN task requires governed dimension handles"
                    )
                if validated.comparison_handle is not None or validated.ranking_direction is not None:
                    raise ResearchToolContractError(
                        "BREAKDOWN task cannot smuggle comparison/ranking semantics"
                    )
            elif task_kind == ResearchTaskKind.COMPARE:
                if validated.comparison_handle is None:
                    raise ResearchToolContractError(
                        "COMPARE task requires governed comparison handle"
                    )
                if validated.ranking_direction is not None:
                    raise ResearchToolContractError(
                        "COMPARE task does not implicitly become ranked comparison"
                    )
            elif task_kind == ResearchTaskKind.RANK:
                if (
                    not validated.dimension_handles
                    or validated.ranking_direction is None
                    or validated.limit is None
                ):
                    raise ResearchToolContractError(
                        "RANK task requires dimension + ranking direction + limit"
                    )
                if validated.comparison_handle is not None:
                    raise ResearchToolContractError(
                        "RANK task does not implicitly become ranked comparison"
                    )

            if task.origin == "USER_SEED":
                if validated.derived_task_id is not None:
                    raise ResearchToolContractError(
                        "USER_SEED task cannot execute as AGENT_DERIVED"
                    )
                if task.question_id not in validated.obligation_ids:
                    raise ResearchToolContractError(
                        "Research QUERY task must bind to its accepted obligation"
                    )
            else:
                if validated.derived_task_id != task.task_id:
                    raise ResearchToolContractError(
                        "derived execution task_id does not match ResearchTask"
                    )
                if validated.derived_parent_obligation_id != task.parent_obligation_id:
                    raise ResearchToolContractError(
                        "derived execution parent obligation does not match ResearchTask"
                    )
                if validated.derived_evidence_ref != task.trigger_evidence_ref:
                    raise ResearchToolContractError(
                        "derived execution evidence does not match ResearchTask"
                    )
                if task.question_id != task.parent_obligation_id:
                    raise ResearchToolContractError(
                        "derived ResearchTask question/parent authority mismatch"
                    )

        return spec, validated

    def validate_output(
        self,
        *,
        spec: ResearchToolSpec,
        value: Any,
    ) -> FrozenModel:
        if not isinstance(value, spec.output_model):
            raise ResearchToolContractError(
                f"Research tool output schema mismatch for {spec.contract.tool_id}: "
                f"{type(value).__name__}"
            )
        return value

    @property
    def declared_tools(self) -> tuple[str, ...]:
        return tuple(self._SPECS)

    @property
    def declared_task_kinds(self) -> tuple[ResearchTaskKind, ...]:
        kinds: list[ResearchTaskKind] = []
        for spec in self._SPECS.values():
            for kind in spec.contract.accepted_task_kinds:
                if kind not in kinds:
                    kinds.append(kind)
        return tuple(kinds)


class ResearchToolRunner:
    """Thin contract/permission gate over the existing official Manager execution path."""

    def __init__(self, registry: ResearchToolRegistry | None = None) -> None:
        self._registry = registry or ResearchToolRegistry()

    @staticmethod
    def _execution_identity(*, principal: Principal, executor) -> dict[str, object]:
        governed = getattr(executor, "principal", None)
        tenant_binding = str(getattr(executor, "tenant_binding", "") or "")
        tenant_runtime = getattr(executor, "tenant_runtime", None)
        if governed is None:
            raise ResearchToolContractError(
                "missing governed executor principal: Research execution fail-closed"
            )
        if not tenant_binding:
            raise ResearchToolContractError(
                "missing governed executor tenant binding: Research execution fail-closed"
            )
        if tenant_runtime is None:
            raise ResearchToolContractError(
                "missing governed tenant runtime: Research execution fail-closed"
            )

        # Principal substitution protection compares the same identity representation
        # on both sides. Opaque tenant_binding strings are namespace identifiers, not
        # raw tenant ids.
        if (
            principal.user_id != governed.user_id
            or principal.is_superadmin != governed.is_superadmin
            or principal.tenant_id != governed.tenant_id
            or (
                principal.tenant_id is None
                and principal.tenant_slug != governed.tenant_slug
            )
        ):
            raise ResearchToolContractError(
                "Research principal mismatch between runner and governed executor"
            )

        if not principal.is_superadmin:
            runtime_tenant_id = getattr(tenant_runtime, "tenant_id", None)
            runtime_tenant_slug = getattr(tenant_runtime, "tenant_slug", None)
            if runtime_tenant_id is not None:
                if principal.tenant_id != runtime_tenant_id:
                    raise ResearchToolContractError(
                        "Research principal tenant does not match governed execution tenant"
                    )
            elif (
                principal.tenant_id is not None
                or principal.tenant_slug != runtime_tenant_slug
            ):
                raise ResearchToolContractError(
                    "Research principal tenant does not match governed execution tenant"
                )

        return {
            "principal_subject": principal.user_id,
            "tenant_binding": tenant_binding,
            "superadmin": bool(principal.is_superadmin),
        }

    @property
    def declared_task_kinds(self) -> tuple[ResearchTaskKind, ...]:
        return self._registry.declared_task_kinds

    def tool_id_for_task(self, task: ResearchTask) -> str:
        try:
            kind = ResearchTaskKind(task.task_kind)
        except ValueError as exc:
            raise ResearchToolContractError(
                f"unregistered Research task kind: {task.task_kind}"
            ) from exc
        return self._registry.tool_id_for_task_kind(kind)

    def execute(
        self,
        *,
        task: ResearchTask,
        tool_id: str,
        call: ManagerToolCall,
        runtime,
        executor,
        principal: Principal | None,
        task_registry: ResearchTaskRegistry | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> ResearchToolExecution:
        spec, validated = self._registry.validate_invocation(
            task=task,
            tool_id=tool_id,
            call=call,
            principal=principal,
        )
        assert principal is not None
        execution_identity = self._execution_identity(
            principal=principal,
            executor=executor,
        )

        accepted = runtime.accepted_contract
        if accepted is None:
            raise ResearchToolContractError(
                "Research execution requires accepted Research authority"
            )
        accepted_family = runtime.authority_registry.accepted(accepted.turn_id)
        if accepted_family is None or accepted_family[0].value != "RESEARCH":
            raise ResearchToolContractError(
                "Research execution requires accepted Research authority family"
            )

        delivery_fingerprint = action_fingerprint(
            {
                "tool_id": tool_id,
                "call": call.model_dump(mode="json"),
                "execution_identity": execution_identity,
            }
        )
        # Every executable Research task gets a lifecycle/deadline lease.  The Manager
        # loop supplies its run-scoped registry; direct single-call harnesses receive an
        # ephemeral one rather than bypassing timeout atomicity.
        active_registry = task_registry or ResearchTaskRegistry()
        prior = active_registry.begin_execution(
            task=task,
            tool_id=tool_id,
            action_fingerprint=delivery_fingerprint,
            timeout_ms=spec.contract.timeout_ms,
        )
        if prior is not None:
            if not isinstance(prior, ResearchToolExecution):
                raise ResearchToolContractError(
                    "ResearchTask receipt type mismatch"
                )
            return prior
        lease = active_registry.execution_lease(task.task_id)

        # Inject only execution identity. Semantic/tool inputs remain exactly the
        # contract-validated call supplied above.
        effective_call = call
        if isinstance(validated, (RunAnalyticsArgs, RunRelationshipArgs)):
            effective_call = call.model_copy(
                update={
                    "args": {
                        **call.args,
                        "research_task_id": task.task_id,
                    }
                }
            )

        registry = active_registry

        class _LifecycleBoundExecutor:
            def execute(self, bound_call, validated_args, bound_runtime):
                def commit_guard() -> None:
                    if cancel_check is not None and cancel_check():
                        registry.cancel(task.task_id)
                    registry.assert_execution_active(
                        task_id=task.task_id,
                        tool_id=tool_id,
                        action_fingerprint=delivery_fingerprint,
                    )

                return executor.execute(
                    bound_call,
                    validated_args,
                    bound_runtime,
                    commit_guard=commit_guard,
                )

        try:
            step = runtime.call_tool(
                effective_call,
                executor=_LifecycleBoundExecutor(),
            )
        except Exception:
            current = active_registry.get(task.task_id)
            if current.state not in {"cancelled", "failed", "blocked"}:
                active_registry.fail(task.task_id)
            raise

        # Deadline was already enforced atomically at the accepted-Evidence commit
        # boundary.  This elapsed value is telemetry only; it must never turn a
        # successfully committed result into an external timeout afterwards.
        elapsed_ms = max(0.0, (active_registry.now() - lease.started_at) * 1000.0)

        observation = self._registry.validate_output(
            spec=spec,
            value=step.tool_result,
        )
        evidence_ref = getattr(observation, "evidence_ref", None)

        # RELATIONSHIP has an explicit fail-closed terminal shape in the governed
        # executor: unavailable/UNSUPPORTED blocks its USER_MUST obligation and returns
        # no Evidence. That is not a malformed tool response and must not be laundered
        # into synthetic Evidence merely to satisfy the Research runner contract.
        if (
            isinstance(observation, ManagerRelationshipObservation)
            and not observation.available
        ):
            execution = ResearchToolExecution(
                task=task.model_copy(update={"state": "blocked"}),
                contract=spec.contract,
                observation=observation,
                evidence=None,
                elapsed_ms=elapsed_ms,
            )
            try:
                active_registry.block_execution(
                    task_id=task.task_id,
                    tool_id=tool_id,
                    action_fingerprint=delivery_fingerprint,
                    result=execution,
                )
            except Exception:
                current = active_registry.get(task.task_id)
                if current.state not in {"cancelled", "failed", "blocked"}:
                    active_registry.fail(task.task_id)
                raise
            return execution

        if not evidence_ref:
            raise ResearchToolContractError(
                f"Research tool {tool_id} returned no evidence reference"
            )

        evidence = executor.evidence_store.get(evidence_ref)
        if not evidence.verified:
            raise ResearchToolContractError(
                f"Research tool {tool_id} evidence is not verified"
            )
        if evidence.evidence_kind != spec.contract.evidence_kind:
            raise ResearchToolContractError(
                f"Research evidence kind mismatch: {evidence.evidence_kind}"
            )
        if evidence.task_id != task.task_id:
            raise ResearchToolContractError(
                f"Research evidence task mismatch: {evidence.task_id} != {task.task_id}"
            )

        for execution in tuple(evidence.payload.get("executions") or ()):
            rows = tuple(execution.get("rows") or ())
            if len(rows) > spec.contract.max_rows:
                raise ResearchToolContractError(
                    f"Research evidence exceeds exposed-row contract: {len(rows)}"
                )

        completed = task.model_copy(update={"state": "complete"})
        execution = ResearchToolExecution(
            task=completed,
            contract=spec.contract,
            observation=observation,
            evidence=evidence,
            elapsed_ms=elapsed_ms,
        )
        try:
            active_registry.complete_execution(
                task_id=task.task_id,
                tool_id=tool_id,
                action_fingerprint=delivery_fingerprint,
                result=execution,
            )
        except Exception:
            current = active_registry.get(task.task_id)
            if current.state not in {"cancelled", "failed", "blocked"}:
                active_registry.fail(task.task_id)
            raise
        return execution
