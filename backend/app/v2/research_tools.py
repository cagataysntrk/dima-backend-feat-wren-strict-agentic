"""Day 7 declarative Research tool contracts and the first governed vertical.

This module is intentionally not an agent kernel. It sits in front of the existing
ManagerRuntime/GovernedManagerExecutor boundary and answers only:

    is this typed ResearchTask allowed to invoke this declared governed tool?

Numeric/query truth remains ManagerCoreAnalyticsAdapter -> CubePlanner -> Wren ->
QueryContract/Evidence.  Missing principal fails closed before execution.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import Field

from app.v2.manager_tools import (
    ManagerAnalyticsObservation,
    ManagerToolCall,
    ManagerToolName,
    RunAnalyticsArgs,
)
from app.v2.models import EvidenceArtifact, FrozenModel, ResearchTask
from control_plane.authorize import AuthzError, Principal, authorize


class ResearchTaskKind(StrEnum):
    QUERY = "QUERY"
    COMPARE = "COMPARE"
    TREND = "TREND"
    BREAKDOWN = "BREAKDOWN"
    RANK = "RANK"
    RELATIONSHIP = "RELATIONSHIP"
    CONTRIBUTION = "CONTRIBUTION"
    PEER_COMPARE = "PEER_COMPARE"


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
    evidence: EvidenceArtifact
    elapsed_ms: float


class ResearchToolContractError(RuntimeError):
    pass


class ResearchToolRegistry:
    """Closed Day 7 tool registry.

    The first vertical intentionally exposes ONE analytical family only. More families
    are added after this one proves the full governed evidence loop.
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

        if isinstance(validated, RunAnalyticsArgs):
            # The typed task must already carry every opaque semantic input the worker
            # sends to the governed executor.  No raw-prompt or hidden-handle guessing.
            undeclared_handles = self._used_handles(validated) - set(task.input_refs)
            if undeclared_handles:
                raise ResearchToolContractError(
                    "Research task did not declare semantic inputs: "
                    + ", ".join(sorted(undeclared_handles))
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


class ResearchToolRunner:
    """Thin contract/permission gate over the existing official Manager execution path."""

    def __init__(self, registry: ResearchToolRegistry | None = None) -> None:
        self._registry = registry or ResearchToolRegistry()

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
    ) -> ResearchToolExecution:
        spec, validated = self._registry.validate_invocation(
            task=task,
            tool_id=tool_id,
            call=call,
            principal=principal,
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

        # Inject only execution identity. Semantic/tool inputs remain exactly the
        # contract-validated call supplied above.
        effective_call = call
        if isinstance(validated, RunAnalyticsArgs):
            effective_call = call.model_copy(
                update={
                    "args": {
                        **call.args,
                        "research_task_id": task.task_id,
                    }
                }
            )

        started = time.monotonic()
        step = runtime.call_tool(effective_call, executor=executor)
        elapsed_ms = (time.monotonic() - started) * 1000.0
        if elapsed_ms > spec.contract.timeout_ms:
            raise ResearchToolContractError(
                f"Research tool {tool_id} exceeded timeout policy "
                f"({elapsed_ms:.1f}ms > {spec.contract.timeout_ms}ms)"
            )

        observation = self._registry.validate_output(
            spec=spec,
            value=step.tool_result,
        )
        evidence_ref = getattr(observation, "evidence_ref", None)
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
        return ResearchToolExecution(
            task=completed,
            contract=spec.contract,
            observation=observation,
            evidence=evidence,
            elapsed_ms=elapsed_ms,
        )
