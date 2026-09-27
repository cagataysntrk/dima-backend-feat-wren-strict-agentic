"""Deterministic Research scheduling for already-authorized, fully-bound work.

This module never reads user language and never creates semantic authority.  It compiles
one existing ResearchTask + accepted obligation + governed CapabilityBinding into the
already-sealed Manager tool argument types, then executes through ResearchToolRunner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.v2.capability_bindings import CapabilityBinding
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationLedgerItem,
)
from app.v2.manager_tools import (
    ManagerToolCall,
    ManagerToolName,
    RunAnalyticsArgs,
    RunRelationshipArgs,
)
from app.v2.models import ResearchTask, ResearchTaskKind
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.research_tools import (
    ResearchToolExecution,
    ResearchToolRegistry,
    ResearchToolRunner,
)


class ResearchTaskInvocationCompileError(RuntimeError):
    """Typed fail-closed result when accepted authority is not losslessly executable."""


@dataclass(frozen=True)
class CompiledResearchInvocation:
    task: ResearchTask
    tool_id: str
    call: ManagerToolCall
    capability_key: ManagerCapabilityKey


class ResearchTaskInvocationCompiler:
    """Compile typed authority to existing tool args with zero language interpretation."""

    def __init__(
        self,
        *,
        tool_registry: ResearchToolRegistry | None = None,
    ) -> None:
        self._tools = tool_registry or ResearchToolRegistry()

    @staticmethod
    def _single(
        refs: tuple[str, ...],
        *,
        label: str,
        required: bool = False,
    ) -> str | None:
        if not refs:
            if required:
                raise ResearchTaskInvocationCompileError(
                    f"{label} requires exactly one governed handle"
                )
            return None
        if len(refs) != 1:
            raise ResearchTaskInvocationCompileError(
                f"{label} requires exactly one governed handle; got {len(refs)}"
            )
        return refs[0]

    def compile(
        self,
        *,
        task: ResearchTask,
        obligation: ObligationLedgerItem,
        binding: CapabilityBinding,
    ) -> CompiledResearchInvocation:
        if binding.obligation_id != obligation.obligation_id:
            raise ResearchTaskInvocationCompileError(
                "CapabilityBinding belongs to another obligation"
            )
        if task.origin == "USER_SEED":
            if task.question_id != obligation.obligation_id:
                raise ResearchTaskInvocationCompileError(
                    "USER_SEED task/obligation identity mismatch"
                )
        else:
            if task.parent_obligation_id != obligation.obligation_id:
                raise ResearchTaskInvocationCompileError(
                    "derived task parent/obligation identity mismatch"
                )

        try:
            task_kind = ResearchTaskKind(task.task_kind)
        except ValueError as exc:
            raise ResearchTaskInvocationCompileError(
                f"unknown ResearchTask kind: {task.task_kind}"
            ) from exc

        try:
            tool_id = self._tools.tool_id_for_task_kind(task_kind)
        except Exception as exc:
            raise ResearchTaskInvocationCompileError(
                f"task kind has no single declared tool: {task_kind.value}"
            ) from exc

        handles = dict(binding.handles_by_kind)
        declared = set(task.input_refs)
        used = {
            ref
            for refs in handles.values()
            for ref in refs
        }
        if used != declared:
            raise ResearchTaskInvocationCompileError(
                "governed binding must exactly account for ResearchTask input_refs"
            )

        params = dict(binding.params)
        capability = binding.spec.key

        if task_kind == ResearchTaskKind.RELATIONSHIP:
            focus = tuple(handles.get("metric", ()))
            counterpart = tuple(handles.get("dimension", ()))
            if not focus or not counterpart:
                raise ResearchTaskInvocationCompileError(
                    "RELATIONSHIP requires governed metric + dimension handles"
                )
            args = RunRelationshipArgs(
                obligation_id=obligation.obligation_id,
                focus_handles=focus,
                counterpart_handles=counterpart,
            )
            return CompiledResearchInvocation(
                task=task,
                tool_id=tool_id,
                call=ManagerToolCall(
                    name=ManagerToolName.RUN_RELATIONSHIP,
                    args=args.model_dump(mode="json"),
                ),
                capability_key=capability,
            )

        if task_kind not in {
            ResearchTaskKind.QUERY,
            ResearchTaskKind.BREAKDOWN,
            ResearchTaskKind.COMPARE,
            ResearchTaskKind.RANK,
        }:
            raise ResearchTaskInvocationCompileError(
                f"{task_kind.value} is not a declared lossless scheduler family"
            )

        ranking_direction = params.get("ranking_direction")
        ranking_limit = params.get("ranking_limit")
        limit = int(ranking_limit) if ranking_limit is not None else None
        args = RunAnalyticsArgs(
            obligation_ids=(obligation.obligation_id,),
            metric_handles=tuple(handles.get("metric", ())),
            dimension_handles=tuple(handles.get("dimension", ())),
            filter_handles=tuple(handles.get("filter", ())),
            period_handle=self._single(
                tuple(handles.get("period", ())),
                label="period",
            ),
            comparison_handle=self._single(
                tuple(handles.get("comparison", ())),
                label="comparison",
            ),
            ranking_direction=ranking_direction,
            limit=limit,
            derived_task_id=(task.task_id if task.origin == "AGENT_DERIVED" else None),
            derived_parent_obligation_id=(
                task.parent_obligation_id
                if task.origin == "AGENT_DERIVED"
                else None
            ),
            derived_capability_key=(
                capability if task.origin == "AGENT_DERIVED" else None
            ),
            derived_evidence_ref=(
                task.trigger_evidence_ref
                if task.origin == "AGENT_DERIVED"
                else None
            ),
        )
        return CompiledResearchInvocation(
            task=task,
            tool_id=tool_id,
            call=ManagerToolCall(
                name=ManagerToolName.RUN_ANALYTICS,
                args=args.model_dump(mode="json"),
            ),
            capability_key=capability,
        )


class DeterministicResearchScheduler:
    """Execute one already-compiled task through the existing Day7 trust plane."""

    def __init__(
        self,
        *,
        runner: ResearchToolRunner,
        compiler: ResearchTaskInvocationCompiler | None = None,
    ) -> None:
        self._runner = runner
        self._compiler = compiler or ResearchTaskInvocationCompiler()

    def execute(
        self,
        *,
        task: ResearchTask,
        obligation: ObligationLedgerItem,
        binding: CapabilityBinding,
        runtime,
        executor,
        principal,
        task_registry: ResearchTaskRegistry,
        cancel_check: Callable[[], bool] | None = None,
    ) -> ResearchToolExecution:
        compiled = self._compiler.compile(
            task=task,
            obligation=obligation,
            binding=binding,
        )
        return self._runner.execute(
            task=task,
            tool_id=compiled.tool_id,
            call=compiled.call,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=task_registry,
            cancel_check=cancel_check,
        )
