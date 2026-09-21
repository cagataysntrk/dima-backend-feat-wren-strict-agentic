"""V2 conversation + standard analytics orchestrator.

Day 3 canonical path:
runtime → bounded context → TurnInterpreter → SemanticResolver → AnalyticsIR/ledger
→ CubePlanner → explicit-principal dry-plan/query → ResultValidator → strict contract seal.

There is no legacy /ask or raw-SQL fallback.
"""

from __future__ import annotations

import hashlib
import json

from control_plane.authorize import Principal
from control_plane.security import derive_hmac_key

from app.company_registry import wren_for_request
from app.v2.context_provider import ContextProviderV0
from app.v2.cube_planner import (
    AnalyticsIRBuilder,
    CubePlanner,
    ResultValidator,
    StandardAnalyticsError,
)
from app.v2.interpreter import TurnInterpreter
from app.v2.models import (
    AskV2BootstrapRequest,
    AskV2BootstrapResponse,
    AskV2Day3Response,
    AskV2Request,
    ExecutionResultV0,
    MinimumQueryContract,
    StandardAnalyticsFailure,
    TenantAnalyticsRuntimeV0,
    TurnAct,
)
from app.v2.resolver import SemanticResolver


class V2Orchestrator:
    def __init__(self) -> None:
        self._context_provider = ContextProviderV0()
        self._interpreter = TurnInterpreter()
        self._resolver = SemanticResolver(
            signing_key=derive_hmac_key("v2-clarification-chip-v1")
        )
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
        """Historical Day 0 boundary probe; not the Day 3 product path."""
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
    ) -> AskV2Day3Response:
        service, schema, runtime = self._bind_runtime(request, principal)
        semantic_context = self._context_provider.build(service, runtime)
        tenant_binding = self._tenant_binding(runtime)

        if semantic_context.context_version.mdl_version != runtime.mdl_version:
            return self._response_failure(
                runtime=runtime,
                context_version=semantic_context.context_version,
                body=body,
                semantic_status="not_applicable",
                failure=self._failure(
                    "context_version_mismatch",
                    "policy",
                    "Bounded semantic context ve runtime farklı MDL version taşıyor.",
                ),
            )

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
            turn = None
            resumed_by = "signed_chip"
        else:
            turn = self._interpreter.interpret(
                question=body.question,
                semantic_context=semantic_context,
                conversation=body.conversation,
                llm=request.app.state.llm,
            )
            pending = body.conversation.clarification_state
            if (
                turn.dialogue_act == TurnAct.CLARIFICATION_ANSWER
                and pending is not None
                and pending.pending
            ):
                bundle = self._resolver.resume_free_text(
                    turn=turn,
                    pending=pending,
                    schema=schema,
                    semantic_context=semantic_context,
                    conversation=body.conversation,
                    tenant_binding=tenant_binding,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                )
                resumed_by = "free_text"
            else:
                bundle = self._resolver.resolve_turn(
                    turn=turn,
                    schema=schema,
                    semantic_context=semantic_context,
                    conversation=body.conversation,
                    tenant_binding=tenant_binding,
                    session_id=body.session_id,
                    thread_id=body.thread_id,
                )
                resumed_by = None

        if not bundle.hypotheses and bundle.clarification is None:
            return AskV2Day3Response(
                semantic_status="not_applicable",
                analytics_status="not_applicable",
                runtime=runtime,
                context_version=semantic_context.context_version,
                turn=turn,
                resumed_by=resumed_by,
                session_id=body.session_id,
                thread_id=body.thread_id,
                next_stage="conversation_day4",
            )

        semantic_status = bundle.semantic_status
        if semantic_status != "resolved":
            return AskV2Day3Response(
                semantic_status=semantic_status,
                analytics_status="not_applicable",
                runtime=runtime,
                context_version=semantic_context.context_version,
                turn=turn,
                hypotheses=bundle.hypotheses,
                clarification=bundle.clarification,
                resumed_by=resumed_by,
                session_id=body.session_id,
                thread_id=body.thread_id,
                next_stage="clarification_resume_day2",
            )

        # Signed-chip grounding itself is deterministic and deliberately does not invoke
        # TurnInterpreter again. Full prior-request slot preservation belongs to Day 4.
        if turn is None:
            return self._response_failure(
                runtime=runtime,
                context_version=semantic_context.context_version,
                body=body,
                semantic_status="resolved",
                hypotheses=bundle.hypotheses,
                resumed_by=resumed_by,
                failure=self._failure(
                    "not_analytic_turn",
                    "policy",
                    "Signed clarification slot çözüldü; tam prior analytical request "
                    "Day4 conversation state olmadan yeniden kurulup execute edilmez.",
                ),
            )

        if turn.dialogue_act not in {TurnAct.ANALYTIC_NEW, TurnAct.ANALYTIC_REFINE}:
            return AskV2Day3Response(
                semantic_status="resolved",
                analytics_status="not_applicable",
                runtime=runtime,
                context_version=semantic_context.context_version,
                turn=turn,
                hypotheses=bundle.hypotheses,
                resumed_by=resumed_by,
                session_id=body.session_id,
                thread_id=body.thread_id,
                next_stage="conversation_day4",
            )

        try:
            built = self._ir_builder.build(
                turn=turn,
                hypotheses=bundle.hypotheses,
                schema=schema,
                context_version=semantic_context.context_version.version,
            )
            plans, ledger = self._planner.plan(
                ir=built.ir,
                ledger=built.ledger,
                service=service,
            )
        except StandardAnalyticsError as exc:
            return self._response_failure(
                runtime=runtime,
                context_version=semantic_context.context_version,
                body=body,
                semantic_status="resolved",
                turn=turn,
                hypotheses=bundle.hypotheses,
                resumed_by=resumed_by,
                analytics_ir=getattr(locals().get("built", None), "ir", None),
                ledger=exc.ledger,
                failure=exc.failure,
                status="not_executable",
            )

        raw_results: list[dict] = []
        for plan in plans:
            try:
                service.dry_plan(plan.sql, principal=principal)
            except Exception as exc:
                return self._response_failure(
                    runtime=runtime,
                    context_version=semantic_context.context_version,
                    body=body,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=bundle.hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=built.ir,
                    ledger=ledger,
                    failure=self._failure(
                        "dry_plan_failed",
                        "dry_plan",
                        f"Official dry-plan reddetti: {exc}",
                    ),
                    status="failed",
                )
            try:
                raw_results.append(service.query(plan.sql, principal=principal))
            except Exception as exc:
                return self._response_failure(
                    runtime=runtime,
                    context_version=semantic_context.context_version,
                    body=body,
                    semantic_status="resolved",
                    turn=turn,
                    hypotheses=bundle.hypotheses,
                    resumed_by=resumed_by,
                    analytics_ir=built.ir,
                    ledger=ledger,
                    failure=self._failure(
                        "query_failed",
                        "execution",
                        f"Official Wren execution başarısız: {exc}",
                    ),
                    status="failed",
                )

        try:
            ledger, validation_errors = self._result_validator.validate(
                ir=built.ir,
                ledger=ledger,
                plans=plans,
                results=tuple(raw_results),
            )
        except StandardAnalyticsError as exc:
            return self._response_failure(
                runtime=runtime,
                context_version=semantic_context.context_version,
                body=body,
                semantic_status="resolved",
                turn=turn,
                hypotheses=bundle.hypotheses,
                resumed_by=resumed_by,
                analytics_ir=built.ir,
                ledger=exc.ledger,
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
            return self._response_failure(
                runtime=runtime,
                context_version=semantic_context.context_version,
                body=body,
                semantic_status="resolved",
                turn=turn,
                hypotheses=bundle.hypotheses,
                resumed_by=resumed_by,
                analytics_ir=built.ir,
                ledger=ledger,
                executions=execution_results,
                failure=self._failure(
                    "contract_seal_failed",
                    "contract",
                    "V2 strict ContractStore runtime'da yok; data sonucu official mühürlenmedi.",
                ),
                status="failed",
            )

        request_ref = self._request_ref(body)
        ir_snapshot = built.ir.model_dump(mode="json")
        for plan, result in zip(plans, raw_results):
            provenance = {
                "v2_minimum_query_contract": {
                    "request_ref": request_ref,
                    "analytics_ir": ir_snapshot,
                    "planner_id": self._planner.planner_id,
                    "planner_version": self._planner.planner_version,
                    "mdl_version": runtime.mdl_version,
                    "context_version": semantic_context.context_version.version,
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
                    context_version=semantic_context.context_version.version,
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
            return self._response_failure(
                runtime=runtime,
                context_version=semantic_context.context_version,
                body=body,
                semantic_status="resolved",
                turn=turn,
                hypotheses=bundle.hypotheses,
                resumed_by=resumed_by,
                analytics_ir=built.ir,
                ledger=ledger,
                executions=execution_results,
                contracts=tuple(contracts),
                failure=self._failure(
                    "contract_seal_failed",
                    "contract",
                    "En az bir execution contract DB/spool'a mühürlenemedi; sonuç official değil.",
                ),
                status="failed",
            )

        official = ledger.all_must_verified and all(
            result.verified for result in execution_results
        ) and all(contract.sealed for contract in contracts)

        return AskV2Day3Response(
            semantic_status="resolved",
            analytics_status="verified" if official else "failed",
            official_verified=official,
            runtime=runtime,
            context_version=semantic_context.context_version,
            turn=turn,
            hypotheses=bundle.hypotheses,
            analytics_ir=built.ir,
            ledger=ledger,
            executions=execution_results,
            query_contracts=tuple(contracts),
            resumed_by=resumed_by,
            session_id=body.session_id,
            thread_id=body.thread_id,
            next_stage="conversation_day4" if official else "standard_analytics_retry",
        )

    def _response_failure(
        self,
        *,
        runtime,
        context_version,
        body,
        semantic_status,
        failure,
        turn=None,
        hypotheses=(),
        resumed_by=None,
        analytics_ir=None,
        ledger=None,
        executions=(),
        contracts=(),
        status="not_executable",
    ) -> AskV2Day3Response:
        return AskV2Day3Response(
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
            failure=failure,
            resumed_by=resumed_by,
            session_id=body.session_id,
            thread_id=body.thread_id,
            next_stage="standard_analytics_retry",
        )

    # Compatibility name for earlier callers; semantics now continue through Day 3.
    interpret = handle


V2BootstrapOrchestrator = V2Orchestrator
