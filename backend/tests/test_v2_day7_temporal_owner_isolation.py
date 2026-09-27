"""Day7 provider-free temporal owner-isolation attacks.

This file proves that USER_MUST temporal authority is obligation-local.  It does not
test Turkish wording and uses a deterministic typed temporal provider.
"""

from __future__ import annotations

from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    ResolvedComparison,
    ResolvedPeriod,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.temporal_intent import (
    ComparisonIntentKind,
    TemporalIntentKind,
    TemporalNormalizationBatch,
    TemporalNormalizationChoice,
)


TENANT = "id:day7-temporal-owner-isolation"


class _TypedTemporalProvider:
    """Closed typed intent provider; no language parsing or calendar arithmetic."""

    def normalize(self, requests):
        choices = []
        for request_id, _surface, target in requests:
            if target == "PERIOD":
                choices.append(
                    TemporalNormalizationChoice(
                        request_id=request_id,
                        target="PERIOD",
                        decision="NORMALIZED",
                        period_kind=TemporalIntentKind.THIS_MONTH,
                    )
                )
            else:
                choices.append(
                    TemporalNormalizationChoice(
                        request_id=request_id,
                        target="COMPARISON",
                        decision="NORMALIZED",
                        comparison_kind=ComparisonIntentKind.PREVIOUS_PERIOD,
                    )
                )
        return TemporalNormalizationBatch(choices=tuple(choices))


def _context():
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-temporal-owner-v1",
            mdl_version="mdl-temporal-owner-v1",
            compact_catalog_builder_version="day7",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="day7",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales_cube",
                display="Sales",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="sales_metric",
                        display="Sales Metric",
                        synonyms=("sales metric",),
                    ),
                ),
                time_dimensions=("Sales.date",),
            ),
            CompactCubeContextV0(
                canonical_name="ops_cube",
                display="Operations",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="ops_metric",
                        display="Ops Metric",
                        synonyms=("ops metric",),
                    ),
                ),
                time_dimensions=("Ops.date",),
            ),
        ),
    )


def _schema():
    return {
        "models": [],
        "cubes": [
            {
                "name": "sales_cube",
                "measures": ["sales_metric"],
                "dimensions": [],
                "dimension_values": {},
            },
            {
                "name": "ops_cube",
                "measures": ["ops_metric"],
                "dimensions": [],
                "dimension_values": {},
            },
        ],
        "company_vocabulary": [],
    }


def _fixture():
    spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    context = _context()
    adapter = ManagerSemanticResolutionAdapter(
        source_spans=spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema=_schema(),
        tenant_binding=TENANT,
        session_id="temporal-owner",
        thread_id="temporal-owner",
        semantic_decision_provider=None,
        temporal_normalization_provider=_TypedTemporalProvider(),
    )
    return spans, handles, context, adapter


def _resolve(adapter, spans, *, text, entries):
    """entries = (owner_id, exact_surface, kind_hint)."""
    message_id = "turn-temporal-owner"
    spans.register_message(message_id=message_id, text=text)
    refs = tuple(
        spans.mint_exact(message_id=message_id, surface=surface).source_ref
        for _, surface, _ in entries
    )
    result = adapter.resolve(
        ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            source_refs=refs,
            source_obligation_ids=tuple(owner for owner, _, _ in entries),
            target_kind_hints=tuple(kind for _, _, kind in entries),
        )
    )
    return result, refs


def _target(handles, context, handle_id):
    return handles.binding_for_execution(
        handle_id,
        tenant_binding=TENANT,
        context_version=context.context_version.version,
    ).canonical_target


def test_each_obligation_period_uses_only_its_own_semantic_anchor():
    spans, handles, context, adapter = _fixture()
    result, refs = _resolve(
        adapter,
        spans,
        text="Sales Metric sales window; Ops Metric ops window.",
        entries=(
            ("U_SALES", "Sales Metric", "metric"),
            ("U_SALES", "sales window", "time"),
            ("U_OPS", "Ops Metric", "metric"),
            ("U_OPS", "ops window", "time"),
        ),
    )

    by_owner_ref = {
        (item.owner_id, item.source_ref): _target(
            handles,
            context,
            item.handle.handle_id,
        )
        for item in result.resolved
    }

    sales_period = by_owner_ref[("U_SALES", refs[1])]
    ops_period = by_owner_ref[("U_OPS", refs[3])]
    assert isinstance(sales_period, ResolvedPeriod)
    assert isinstance(ops_period, ResolvedPeriod)
    assert sales_period.time_dimension == "Sales.date"
    assert ops_period.time_dimension == "Ops.date"
    assert result.unresolved_source_refs == ()


def test_comparison_cannot_inherit_another_obligations_explicit_base_period():
    spans, handles, context, adapter = _fixture()
    result, refs = _resolve(
        adapter,
        spans,
        text="Sales Metric sales window; Ops Metric compare window.",
        entries=(
            ("U_SALES", "Sales Metric", "metric"),
            ("U_SALES", "sales window", "time"),
            ("U_OPS", "Ops Metric", "metric"),
            ("U_OPS", "compare window", "comparison"),
        ),
    )

    # U_OPS has no owner-local explicit period and the typed comparison choice has no
    # implicit base.  It must remain unresolved instead of laundering U_SALES period.
    assert refs[3] in result.unresolved_source_refs

    for item in result.resolved:
        if item.owner_id != "U_OPS":
            continue
        target = _target(handles, context, item.handle.handle_id)
        assert not isinstance(target, ResolvedComparison)
