"""Provider-free canonical adaptive branch proof for Day 6.5.

This test uses the real Resolver -> SemanticHandle -> Manager executor -> Core planner/
validator -> QueryContract/Evidence path. Only the data source is synthetic.
"""

from __future__ import annotations

import json

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationStatus,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ManagerToolCall, ManagerToolName, ResolveSemanticsArgs
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    TenantAnalyticsRuntimeV0,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


class _SyntheticService:
    mdl_version = "mdl-adaptive-v1"

    def cube_sql(self, cube_query: dict) -> str:
        return "ADAPTIVE:" + json.dumps(
            cube_query,
            ensure_ascii=False,
            sort_keys=True,
        )

    def dry_plan(self, sql: str, *, principal=None):
        assert sql.startswith("ADAPTIVE:")
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        query = json.loads(sql.removeprefix("ADAPTIVE:"))
        dimensions = list(query.get("dimensions") or ())
        measures = list(query.get("measures") or ())
        columns = [*dimensions, *measures]

        if dimensions:
            rows = [
                {dimensions[0]: "Kuzey", **{metric: 120.0 for metric in measures}},
                {dimensions[0]: "Güney", **{metric: 95.0 for metric in measures}},
            ]
        else:
            rows = [{metric: 120.0 for metric in measures}]

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "column_types": [
                "VARCHAR" if name in dimensions else "DOUBLE"
                for name in columns
            ],
        }


class _ContractStore:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {
            "id": f"adaptive-qc-{self.n}",
            "sealed": True,
        }


def _context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-adaptive-v1",
            mdl_version="mdl-adaptive-v1",
            compact_catalog_builder_version="v1",
            business_rules_hash="none",
            prompt_context_policy_version="v1",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales_omega",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_value_x",
                        display="Net Gelir",
                        synonyms=("net gelir", "gelir"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="region_axis_m",
                        display="Bölge",
                        synonyms=("bölge", "region"),
                    ),
                ),
            ),
        ),
    )


def test_result_aware_agent_derived_branch_is_evidence_grounded_end_to_end():
    tenant = "tenant-adaptive"
    context = _context()
    spans = SourceSpanRegistry()
    source_hash = spans.register_message(
        message_id="turn-adaptive",
        text="net gelir ne durumda?",
    )
    metric_span = spans.mint_exact(
        message_id="turn-adaptive",
        surface="net gelir",
    )
    handles = SemanticHandleRegistry()
    semantic = ManagerSemanticResolutionAdapter(
        source_spans=spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema={
            "cubes": [
                {
                    "name": "sales_omega",
                    "measures": ["net_value_x"],
                    "dimensions": ["region_axis_m"],
                    "time_dimensions": [],
                }
            ]
        },
        tenant_binding=tenant,
        session_id=None,
        thread_id=None,
    )

    metric_result = semantic.resolve(
        ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            source_refs=(metric_span.source_ref,),
            target_kind_hints=("metric",),
        )
    )
    metric_handle = metric_result.resolved[0].handle.handle_id

    acceptance = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    )
    service = _SyntheticService()
    runtime_identity = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="adaptive",
        principal_user_id="adaptive-user",
        roles=("owner",),
        mdl_version=service.mdl_version,
        catalog="adaptive",
        schema_name="main",
        db_online=True,
    )
    executor = GovernedManagerExecutor(
        acceptance=acceptance,
        core_analytics=ManagerCoreAnalyticsAdapter(
            semantic_handles=handles,
        ),
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant,
            context_version=context.context_version.version,
            principal=None,
            service=service,
            tenant_runtime=runtime_identity,
            contract_store=_ContractStore(),
            session_id="adaptive-session",
        ),
        semantic_resolution=semantic,
    )
    runtime = ManagerRuntime(request_ref="adaptive-request")
    runtime.begin_understanding()

    envelope = UserIntentEnvelope(
        attempt_id="adaptive-attempt-1",
        turn_id="turn-adaptive",
        request_ref="adaptive-request",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(metric_span.source_ref,),
                semantic_handle_refs=(metric_handle,),
            ),
        ),
    )
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={"envelope": envelope.model_dump(mode="json")},
        ),
        executor=executor,
    )

    parent_step = runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.RUN_ANALYTICS,
            args={
                "obligation_ids": ("U1",),
                "metric_handles": (metric_handle,),
            },
        ),
        executor=executor,
    )
    parent_evidence_ref = parent_step.tool_result.evidence_ref
    parent_before = next(item for item in runtime.ledger.items if item.obligation_id == "U1")
    assert parent_before.status == ObligationStatus.VERIFIED
    assert parent_before.evidence_refs == (parent_evidence_ref,)

    # Result-aware means the evidence is explicitly inspected before branching.
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.INSPECT_EVIDENCE,
            args={"evidence_ref": parent_evidence_ref},
        ),
        executor=executor,
    )

    derived_semantic = runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.RESOLVE_SEMANTICS,
            args={
                "provenance": "AGENT_DERIVED",
                "source_refs": (),
                "target_kind_hints": ("dimension",),
                "parent_obligation_id": "U1",
                "evidence_ref": parent_evidence_ref,
                "natural_language_proposal": "bölge",
            },
        ),
        executor=executor,
    ).tool_result
    dimension_handle = derived_semantic.resolved[0].handle
    assert dimension_handle.provenance_type == "AGENT_DERIVED"
    assert dimension_handle.parent_obligation_id == "U1"
    assert dimension_handle.trigger_evidence_ref == parent_evidence_ref

    child_step = runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.RUN_ANALYTICS,
            args={
                "obligation_ids": ("U1",),
                "metric_handles": (metric_handle,),
                "dimension_handles": (dimension_handle.handle_id,),
                "derived_task_id": "D1",
                "derived_parent_obligation_id": "U1",
                "derived_capability_key": "breakdown",
                "derived_evidence_ref": parent_evidence_ref,
            },
        ),
        executor=executor,
    )
    assert child_step.tool_result.obligations_verified == ("D1",)

    parent_after = next(item for item in runtime.ledger.items if item.obligation_id == "U1")
    child = next(item for item in runtime.ledger.items if item.obligation_id == "D1")

    # The adaptive child is additive; the canonical USER_MUST is never rewritten.
    assert parent_after == parent_before
    assert child.origin.value == "AGENT_DERIVED"
    assert child.parent_obligation_id == "U1"
    assert child.capability_key == ManagerCapabilityKey.BREAKDOWN
    assert child.status == ObligationStatus.VERIFIED
    assert child.evidence_refs
