"""Dima V2 Day 4 conversation orchestrator.

Canonical path:
runtime → bounded context → TurnInterpreter → DialoguePolicy → SemanticResolver
→ ConversationCoordinator (prior IR + typed delta) → AnalyticsIR/ledger → CubePlanner
→ explicit-principal Wren execution → ResultValidator → immutable contract seal
→ updated typed ConversationState.

No legacy /ask, raw-SQL memory, or request-level semantic fallback exists here.
"""

from __future__ import annotations

import hashlib
import json

from control_plane.authorize import Principal
from control_plane.security import derive_hmac_key

from app.company_registry import wren_for_request
from app.v2.context_provider import ContextProviderV0
from app.v2.conversation import ConversationCoordinatorV0, ledger_from_ir
from app.v2.cube_planner import (
    AnalyticsIRBuilder,
    CubePlanner,
    ResultValidator,
    StandardAnalyticsError,
)
from app.v2.dialogue_policy import DialoguePolicyV0
from app.v2.interpreter import TurnInterpreter
from app.v2.models import (
    AnalyticsIR,
    AskV2BootstrapRequest,
    AskV2BootstrapResponse,
    AskV2Day4Response,
    AskV2Request,
    DialogueAction,
    ExecutionResultV0,
    MinimumQueryContract,
    RequirementLedger,
    SemanticHypothesis,
    StandardAnalyticsFailure,
    TenantAnalyticsRuntimeV0,
    TurnAct,
    TurnInterpretation,
)
from app.v2.resolver import SemanticResolver


class V2Orchestrator:
    def __init__(self) -> None:
        self._context_provider = ContextProviderV0()
        self._interpreter = TurnInterpreter()
        self._resolver = SemanticResolver(
            signing_key=derive_hmac_key("v2-clarification-chip-v1")
        )
        self._dialogue_policy = DialoguePolicyV0()
        self._conversation = ConversationCoordinatorV0()
        self._ir_builder = AnalyticsIRBuilder()
        self._planner = CubePlanner()
        self._result_validator = ResultValidator()

    @staticmethod
    def _bind_runtime(request, principal: Principal):
        service = wren_for_request(request)
        schema = service.schema()
        runtime = TenantAnalyticsRuntimeV0(
            tenant_id=str(principal.tenant_id) if principal.tenant_id else None,
            tenant_slug=principal.tenant_slug,
            principal_user_id=str(principal.user_id),
            roles=tuple(sorted(str(role) for role in (principal.roles or []))),
            mdl_version=str(service.mdl_version),
            catalog=schema.get("catalog"),
            schema_name=schema.get("schema_name"),
            db_online=bool(schema.get("db_online", True)),
        )
        return service, schema, runtime

    @staticmethod
    def _tenant_binding(runtime: TenantAnalyticsRuntimeV0) -> str:
        if runtime.tenant_id:
            return f"id:{runtime.tenant_id}"
        return f"slug:{runtime.tenant_slug or ''}"

    @staticmethod
    def _request_ref(body: AskV2Request) -> str:
        payload = json.dumps(
            {
                "question": body.question,
                "session_id": body.session_id,
                "thread_id": body.thread_id,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return "r-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]

    @staticmethod
    def _failure(code: str, stage: str, message: str) -> StandardAnalyticsFailure:
        return StandardAnalyticsFailure(code=code, stage=stage, message=message)

    def bootstrap(
        self,
        request,
        body: AskV2BootstrapRequest,
        principal: Principal,
    ) -> AskV2BootstrapResponse:
        _, _, runtime = self._bind_runtime(request, principal)
        return AskV2BootstrapResponse(
            runtime=runtime,
            session_id=body.session_id,
            thread_id=body.thread_id,
        )

    def handle(
        self,
        request,
        body: AskV2Request,
        principal: Principal,
    ) -> AskV2Day4Response:
        service, schema, runtime = self._bind_runtime(request, principal)
        semantic_context = self._context_provider.build(service, runtime)
        context_version = semantic_context.context_version
        tenant_binding = self._tenant_binding(runtime)

        if context_version.mdl_version != runtime.mdl_version:
            return self._failure_response(
                runtime=runtime,
                context_version=context_version,
                body=body,
                conversation=body.conversation,
                dialogue_action=DialogueAction.UNSUPPORTED,
                semantic_status="not_applicable",
                failure=self._failure(
                    "context_version_mismatch",
                    "policy",
                    "Bounded semantic context ve runtime farklı MDL version taşıyor.",
                ),
            )

        response_turn: TurnInterpretation | None = None
        effective_turn: TurnInterpretation | None = None
        hypotheses: tuple[SemanticHypothesis, ...] = ()
        resumed_by = None
        base_ir_override: AnalyticsIR | None = None
        working_conversation = body.conversation

        if body.clarification_token:
            bundle = self._resolver.resume_signed(
                token=body.clarification_token,
                schema=schema,
                semantic_context=semantic_context,
                conversation=body.conversation,
                tenant_binding=tenant_binding,
                session_id=body.session_id,
                thread_id=body.thread_id,
            )
            resumed_by = "signed_chip"
            try:
                effective_turn, hypotheses, base_ir_override = self._conversation.restore_pending(
                    conversation=body.conversation,
                    resumed_hypotheses=bundle.hypotheses,
                    context_version=context_version.version,
                )
            except StandardAnalyticsError as exc:
                return self._failure_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=body.conversation,
                    dialogue_action=DialogueAction.UNSUPPORTED,
                    semantic_status="resolved",
                    hypotheses=bundle.hypotheses,
                    resumed_by=resumed_by,
                    failure=exc.failure,
                )
            working_conversation = self._conversation.clear_pending(body.conversation)
        else:
            response_turn = self._interpreter.interpret(
                question=body.question,
                semantic_context=semantic_context,
                conversation=body.conversation,
                llm=request.app.state.llm,
            )

            early_action = self._dialogue_policy.before_grounding(
                turn=response_turn,
                conversation=body.conversation,
            )
            if early_action == DialogueAction.TALK:
                return self._nonquery_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=body.conversation,
                    turn=response_turn,
                    dialogue_action=DialogueAction.TALK,
                )
            if early_action == DialogueAction.EXPLAIN_EXISTING:
                return self._nonquery_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=body.conversation,
                    turn=response_turn,
                    dialogue_action=DialogueAction.EXPLAIN_EXISTING,
                    existing_result=body.conversation.last_result,
                    used_existing_result=True,
                )
            if early_action == DialogueAction.UNSUPPORTED:
                failure = None
                analytics_status = "not_applicable"
                if response_turn.dialogue_act == TurnAct.RESULT_EXPLAIN:
                    failure = self._failure(
                        "no_active_result",
                        "conversation",
                        "Açıklanacak verified active result yok; yeni query tahminle açılmadı.",
                    )
                    analytics_status = "not_executable"
                return self._nonquery_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=body.conversation,
                    turn=response_turn,
                    dialogue_action=DialogueAction.UNSUPPORTED,
                    failure=failure,
                    analytics_status=analytics_status,
                )

            pending = body.conversation.clarification_state
            if response_turn.dialogue_act == TurnAct.CLARIFICATION_ANSWER:
                bundle = self._resolver.resume_free_text(
                    turn=response_turn,
                    pending=pending,
                    schema=schema,
                    semantic_context=semantic_context,
                    conversation=body.conversation,
                    tenant_binding=tenant_binding,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                )
                resumed_by = "free_text"
                if bundle.clarification is None:
                    try:
                        effective_turn, hypotheses, base_ir_override = (
                            self._conversation.restore_pending(
                                conversation=body.conversation,
                                resumed_hypotheses=bundle.hypotheses,
                                context_version=context_version.version,
                            )
                        )
                    except StandardAnalyticsError as exc:
                        return self._failure_response(
                            runtime=runtime,
                            context_version=context_version,
                            body=body,
                            conversation=body.conversation,
                            dialogue_action=DialogueAction.UNSUPPORTED,
                            semantic_status="resolved",
                            turn=response_turn,
                            hypotheses=bundle.hypotheses,
                            resumed_by=resumed_by,
                            failure=exc.failure,
                        )
                    working_conversation = self._conversation.clear_pending(
                        body.conversation
                    )
                else:
                    hypotheses = bundle.hypotheses
            else:
                effective_turn = response_turn
                bundle = self._resolver.resolve_turn(
                    turn=response_turn,
                    schema=schema,
                    semantic_context=semantic_context,
                    conversation=body.conversation,
                    tenant_binding=tenant_binding,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                )
                hypotheses = bundle.hypotheses

            action = self._dialogue_policy.after_grounding(
                turn=response_turn,
                bundle=bundle,
            )
            if action == DialogueAction.CLARIFY:
                if bundle.clarification is None:
                    raise RuntimeError("DialoguePolicy CLARIFY without ClarificationState")
                if resumed_by == "free_text" and body.conversation.pending_analytical is not None:
                    next_conversation = self._conversation.refresh_pending_clarification(
                        conversation=body.conversation,
                        clarification=bundle.clarification,
                    )
                else:
                    next_conversation = self._conversation.capture_pending(
                        conversation=body.conversation,
                        turn=response_turn,
                        hypotheses=bundle.hypotheses,
                        clarification=bundle.clarification,
                        context_version=context_version.version,
                    )
                return AskV2Day4Response(
                    dialogue_action=DialogueAction.CLARIFY,
                    semantic_status=bundle.semantic_status,
                    analytics_status="not_applicable",
                    runtime=runtime,
                    context_version=context_version,
                    turn=response_turn,
                    hypotheses=bundle.hypotheses,
                    clarification=bundle.clarification,
                    conversation=next_conversation,
                    resumed_by=resumed_by,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                    query_execution_count=0,
                    next_stage="clarification_resume_day4",
                )
            if effective_turn is None:
                effective_turn = response_turn

        if effective_turn is None:
            return self._failure_response(
                runtime=runtime,
                context_version=context_version,
                body=body,
                conversation=working_conversation,
                dialogue_action=DialogueAction.UNSUPPORTED,
                semantic_status="not_applicable",
                turn=response_turn,
                hypotheses=hypotheses,
                resumed_by=resumed_by,
                failure=self._failure(
                    "not_analytic_turn",
                    "conversation",
                    "Standard analytics'e taşınacak typed turn yok.",
                ),
            )

        try:
            ir, ledger = self._effective_ir(
                turn=effective_turn,
                hypotheses=hypotheses,
                schema=schema,
                context_version=context_version.version,
                prior_ir=base_ir_override or working_conversation.last_ir,
            )
        except StandardAnalyticsError as exc:
            return self._failure_response(
                runtime=runtime,
                context_version=context_version,
                body=body,
                conversation=working_conversation,
                dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                semantic_status="resolved",
                turn=response_turn,
                hypotheses=hypotheses,
                resumed_by=resumed_by,
                ledger=exc.ledger,
                failure=exc.failure,
                status="not_executable",
            )

        return self._execute_standard(
            request=request,
            body=body,
            principal=principal,
            service=service,
            runtime=runtime,
            context_version=context_version,
            turn=response_turn,
            hypotheses=hypotheses,
            resumed_by=resumed_by,
            conversation=working_conversation,
            ir=ir,
            ledger=ledger,
        )

    def _effective_ir(
        self,
        *,
        turn: TurnInterpretation,
        hypotheses: tuple[SemanticHypothesis, ...],
        schema: dict,
        context_version: str,
        prior_ir: AnalyticsIR | None,
    ) -> tuple[AnalyticsIR, RequirementLedger]:
        if turn.dialogue_act == TurnAct.ANALYTIC_NEW:
            built = self._ir_builder.build(
                turn=turn,
                hypotheses=hypotheses,
                schema=schema,
                context_version=context_version,
            )
            return built.ir, built.ledger

        if turn.dialogue_act in {TurnAct.ANALYTIC_REFINE, TurnAct.USER_REPAIR}:
            ir = self._conversation.apply_delta(
                prior_ir=prior_ir,
                turn=turn,
                hypotheses=hypotheses,
                schema=schema,
                context_version=context_version,
            )
            return ir, ledger_from_ir(ir)

        raise StandardAnalyticsError(
            self._failure(
                "not_analytic_turn",
                "conversation",
                f"Dialogue act standard analytics delta değildir: {turn.dialogue_act.value}",
            )
        )

    def _execute_standard(
        self,
        *,
        request,
        body: AskV2Request,
        principal: Principal,
        service,
        runtime: TenantAnalyticsRuntimeV0,
        context_version,
        turn: TurnInterpretation | None,
        hypotheses: tuple[SemanticHypothesis, ...],
        resumed_by,
        conversation,
        ir: AnalyticsIR,
        ledger: RequirementLedger,
    ) -> AskV2Day4Response:
        try:
            plans, ledger = self._planner.plan(
                ir=ir,
                ledger=ledger,
                service=service,
            )
        except StandardAnalyticsError as exc:
            return self._failure_response(
                runtime=runtime,
                context_version=context_version,
                body=body,
                conversation=conversation,
                dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                semantic_status="resolved",
                turn=turn,
                hypotheses=hypotheses,
                resumed_by=resumed_by,
                analytics_ir=ir,
                ledger=exc.ledger,
                failure=exc.failure,
                status="not_executable",
            )

        raw_results: list[dict] = []
        query_count = 0
        for plan in plans:
            try:
                service.dry_plan(plan.sql, principal=principal)
            except Exception as exc:
                return self._failure_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=conversation,
                    dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=ir,
                    ledger=ledger,
                    query_execution_count=query_count,
                    failure=self._failure(
                        "dry_plan_failed",
                        "dry_plan",
                        f"Official dry-plan reddetti: {exc}",
                    ),
                    status="failed",
                )
            try:
                raw_results.append(service.query(plan.sql, principal=principal))
                query_count += 1
            except Exception as exc:
                return self._failure_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=conversation,
                    dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=ir,
                    ledger=ledger,
                    query_execution_count=query_count,
                    failure=self._failure(
                        "query_failed",
                        "execution",
                        f"Official Wren execution başarısız: {exc}",
                    ),
                    status="failed",
                )

        if ir.ranking is not None and ir.comparison is not None:
            if len(plans) != 1 or len(raw_results) != 1:
                return self._failure_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=conversation,
                    dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=ir,
                    ledger=ledger,
                    query_execution_count=query_count,
                    failure=self._failure(
                        "plan_validation_failed",
                        "planner",
                        "Ranked comparison base execution cardinality invalid.",
                    ),
                    status="failed",
                )
            try:
                reference_plan, ledger = self._planner.plan_ranked_comparison_reference(
                    ir=ir,
                    ledger=ledger,
                    primary_result=raw_results[0],
                    service=service,
                )
            except StandardAnalyticsError as exc:
                return self._failure_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=conversation,
                    dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=ir,
                    ledger=exc.ledger,
                    query_execution_count=query_count,
                    failure=exc.failure,
                    status="not_executable",
                )
            try:
                service.dry_plan(reference_plan.sql, principal=principal)
            except Exception as exc:
                return self._failure_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=conversation,
                    dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=ir,
                    ledger=ledger,
                    query_execution_count=query_count,
                    failure=self._failure(
                        "dry_plan_failed",
                        "dry_plan",
                        f"Official aligned comparison dry-plan reddetti: {exc}",
                    ),
                    status="failed",
                )
            try:
                reference_result = service.query(
                    reference_plan.sql,
                    principal=principal,
                )
                query_count += 1
            except Exception as exc:
                return self._failure_response(
                    runtime=runtime,
                    context_version=context_version,
                    body=body,
                    conversation=conversation,
                    dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=ir,
                    ledger=ledger,
                    query_execution_count=query_count,
                    failure=self._failure(
                        "query_failed",
                        "execution",
                        f"Official aligned comparison execution başarısız: {exc}",
                    ),
                    status="failed",
                )
            plans = (*plans, reference_plan)
            raw_results.append(reference_result)

        try:
            ledger, validation_errors = self._result_validator.validate(
                ir=ir,
                ledger=ledger,
                plans=plans,
                results=tuple(raw_results),
            )
        except StandardAnalyticsError as exc:
            return self._failure_response(
                runtime=runtime,
                context_version=context_version,
                body=body,
                conversation=conversation,
                dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                semantic_status="resolved",
                turn=turn,
                hypotheses=hypotheses,
                resumed_by=resumed_by,
                analytics_ir=ir,
                ledger=exc.ledger,
                query_execution_count=query_count,
                failure=exc.failure,
                status="failed",
            )

        execution_results = tuple(
            ExecutionResultV0(
                execution_id=plan.execution_id,
                role=plan.role,
                columns=tuple(str(column) for column in (result.get("columns") or ())),
                rows=tuple(dict(row) for row in (result.get("rows") or ())),
                row_count=int(result.get("row_count") or 0),
                column_types=tuple(str(t) for t in (result.get("column_types") or ())),
                verified=not bool(errors),
                verification_errors=errors,
            )
            for plan, result, errors in zip(plans, raw_results, validation_errors)
        )

        contracts: list[MinimumQueryContract] = []
        store = getattr(request.app.state, "contracts", None)
        if store is None or not callable(getattr(store, "record_v2_minimum", None)):
            return self._failure_response(
                runtime=runtime,
                context_version=context_version,
                body=body,
                conversation=conversation,
                dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                semantic_status="resolved",
                turn=turn,
                hypotheses=hypotheses,
                resumed_by=resumed_by,
                analytics_ir=ir,
                ledger=ledger,
                executions=execution_results,
                query_execution_count=query_count,
                failure=self._failure(
                    "contract_seal_failed",
                    "contract",
                    "V2 strict ContractStore runtime'da yok; data sonucu official mühürlenmedi.",
                ),
                status="failed",
            )

        request_ref = self._request_ref(body)
        ir_snapshot = ir.model_dump(mode="json")
        for plan, result in zip(plans, raw_results):
            provenance = {
                "v2_minimum_query_contract": {
                    "request_ref": request_ref,
                    "analytics_ir": ir_snapshot,
                    "planner_id": self._planner.planner_id,
                    "planner_version": self._planner.planner_version,
                    "mdl_version": runtime.mdl_version,
                    "context_version": context_version.version,
                    "execution_id": plan.execution_id,
                    "tenant_id": runtime.tenant_id,
                    "principal_user_id": runtime.principal_user_id,
                    "principal_roles": list(runtime.roles),
                    "verification": {
                        "ledger_all_must_verified": ledger.all_must_verified,
                        "result_verified": True,
                    },
                }
            }
            sealed = store.record_v2_minimum(
                session_id=body.session_id,
                question=body.question,
                cube_query=plan.cube_query,
                sql=plan.sql,
                result=result,
                schema_version=runtime.mdl_version,
                tenant_id=runtime.tenant_id,
                provenance=provenance,
            )
            contracts.append(
                MinimumQueryContract(
                    contract_id=str(sealed["id"]),
                    execution_id=plan.execution_id,
                    request_ref=request_ref,
                    planner_id=self._planner.planner_id,
                    planner_version=self._planner.planner_version,
                    mdl_version=runtime.mdl_version,
                    context_version=context_version.version,
                    executed_sql=plan.sql,
                    result_hash=sealed.get("result_hash"),
                    tenant_id=runtime.tenant_id,
                    principal_user_id=runtime.principal_user_id,
                    principal_roles=runtime.roles,
                    cube_query=plan.cube_query,
                    analytics_ir=ir_snapshot,
                    durability=sealed.get("durability", "none"),
                    sealed=bool(sealed.get("sealed")),
                )
            )

        if not contracts or not all(contract.sealed for contract in contracts):
            return self._failure_response(
                runtime=runtime,
                context_version=context_version,
                body=body,
                conversation=conversation,
                dialogue_action=DialogueAction.ANALYTIC_STANDARD,
                semantic_status="resolved",
                turn=turn,
                hypotheses=hypotheses,
                resumed_by=resumed_by,
                analytics_ir=ir,
                ledger=ledger,
                executions=execution_results,
                contracts=tuple(contracts),
                query_execution_count=query_count,
                failure=self._failure(
                    "contract_seal_failed",
                    "contract",
                    "En az bir execution contract DB/spool'a mühürlenemedi; sonuç official değil.",
                ),
                status="failed",
            )

        contract_tuple = tuple(contracts)
        official = (
            ledger.all_must_verified
            and all(result.verified for result in execution_results)
            and all(contract.sealed for contract in contract_tuple)
        )
        next_conversation = self._conversation.state_after_verified(
            prior=conversation,
            ir=ir,
            executions=execution_results,
            contracts=contract_tuple,
        )

        return AskV2Day4Response(
            dialogue_action=DialogueAction.ANALYTIC_STANDARD,
            semantic_status="resolved",
            analytics_status="verified" if official else "failed",
            official_verified=official,
            runtime=runtime,
            context_version=context_version,
            turn=turn,
            hypotheses=hypotheses,
            analytics_ir=ir,
            ledger=ledger,
            executions=execution_results,
            query_contracts=contract_tuple,
            conversation=next_conversation,
            resumed_by=resumed_by,
            session_id=body.session_id,
            thread_id=body.thread_id,
            query_execution_count=query_count,
            next_stage="core_mvp_day5" if official else "standard_analytics_retry",
        )

    def _nonquery_response(
        self,
        *,
        runtime,
        context_version,
        body,
        conversation,
        turn,
        dialogue_action,
        existing_result=None,
        used_existing_result=False,
        failure=None,
        analytics_status="not_applicable",
    ) -> AskV2Day4Response:
        return AskV2Day4Response(
            dialogue_action=dialogue_action,
            semantic_status="not_applicable",
            analytics_status=analytics_status,
            official_verified=False,
            runtime=runtime,
            context_version=context_version,
            turn=turn,
            existing_result=existing_result,
            conversation=conversation,
            failure=failure,
            session_id=body.session_id,
            thread_id=body.thread_id,
            query_execution_count=0,
            used_existing_result=used_existing_result,
            next_stage="conversation_day4",
        )

    def _failure_response(
        self,
        *,
        runtime,
        context_version,
        body,
        conversation,
        dialogue_action,
        semantic_status,
        failure,
        turn=None,
        hypotheses=(),
        resumed_by=None,
        analytics_ir=None,
        ledger=None,
        executions=(),
        contracts=(),
        query_execution_count=0,
        status="not_executable",
    ) -> AskV2Day4Response:
        return AskV2Day4Response(
            dialogue_action=dialogue_action,
            semantic_status=semantic_status,
            analytics_status=status,
            official_verified=False,
            runtime=runtime,
            context_version=context_version,
            turn=turn,
            hypotheses=hypotheses,
            analytics_ir=analytics_ir,
            ledger=ledger,
            executions=executions,
            query_contracts=contracts,
            conversation=conversation,
            failure=failure,
            resumed_by=resumed_by,
            session_id=body.session_id,
            thread_id=body.thread_id,
            query_execution_count=query_execution_count,
            next_stage="standard_analytics_retry",
        )

    interpret = handle


V2BootstrapOrchestrator = V2Orchestrator
