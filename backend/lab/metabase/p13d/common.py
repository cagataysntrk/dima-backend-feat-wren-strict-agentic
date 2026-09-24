"""Frozen P13D cohesive Standard cases and shared live/runtime helpers."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedRanking,
    ResolvedSemanticRef,
    StandardProjection,
    projection_hash,
    projection_handles,
)
from app.v3.authority import AcceptedStandardAuthority, StandardWorkMode
from app.v3.substrate.metabase.execution_binding import CandidateSemanticBinding

from lab.metabase.p13c.common import (
    CONTEXT_VERSION,
    FILTER_RESOURCE as CHANNEL_RESOURCE,
    PRINCIPAL,
    TABLE_RESOURCE,
    TENANT,
    TIME_RESOURCE,
    assert_identity,
    binding_snapshot as p13c_binding_snapshot,
    discover_catalog,
    h,
    login,
    managed_metric_binding,
)

BREAKDOWN_CASE = "P13D-BREAKDOWN"
RANKING_CASE = "P13D-RANKING"
COMPARISON_CASE = "P13D-COMPARISON"

BREAKDOWN_QUESTION = "Haziran 2026'da satış siparişlerini kanala göre dağıt."
RANKING_QUESTION = "Haziran 2026'da en çok satış siparişi açılan 2 kanal hangileri?"
COMPARISON_QUESTION = "Haziran 2026 ile Mayıs 2026 satış siparişi sayısını karşılaştır."

METRIC_HANDLE = "handle.sales_order_count"
DIMENSION_HANDLE = "handle.sales_order_channel"
PERIOD_HANDLE = "handle.period.june_2026"
COMPARISON_HANDLE = "handle.comparison.june_2026_vs_may_2026"


def binding_snapshot(
    database_id: int,
    table_id: int,
    time_field_id: int,
    channel_field_id: int,
    schema_name: str,
):
    """Reuse the P13C semantic catalog; only bind channel as a dimension for P13D."""
    snapshot = p13c_binding_snapshot(
        database_id,
        table_id,
        time_field_id,
        channel_field_id,
        schema_name,
    )
    return snapshot.model_copy(
        update={
            "candidate_bindings": (
                CandidateSemanticBinding(
                    candidate_id="cand_sales_order_count",
                    semantic_id="metric.sales_order_count",
                    kind="metric",
                ),
                CandidateSemanticBinding(
                    candidate_id="cand_sales_order_channel",
                    semantic_id="dimension.sales_order_channel",
                    kind="dimension",
                ),
            )
        }
    )


def _accepted(
    *,
    case_id: str,
    question: str,
    projection: StandardProjection,
) -> AcceptedStandardAuthority:
    source_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()
    p_hash = projection_hash(projection)
    return AcceptedStandardAuthority(
        authority_id="asa_" + h(
            {"case": case_id, "source": source_hash, "projection": p_hash}
        )[:24],
        turn_id=case_id.lower(),
        request_ref=f"p13d:{case_id.lower()}",
        source_message_hash=source_hash,
        context_version=CONTEXT_VERSION,
        projection_hash=p_hash,
        semantic_handle_refs=projection_handles(projection),
        accepted_attempt_id=f"{case_id.lower()}-attempt-1",
        model_role="native-metabot",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
        created_at_iso=datetime.now(timezone.utc).isoformat(),
    )


def _metric() -> ResolvedSemanticRef:
    return ResolvedSemanticRef(
        semantic_ref=METRIC_HANDLE,
        source_candidate_id="cand_sales_order_count",
        kind="metric",
        canonical_name="Sales Order Count",
        source_scopes=("satis_siparisleri",),
    )


def _dimension() -> ResolvedSemanticRef:
    return ResolvedSemanticRef(
        semantic_ref=DIMENSION_HANDLE,
        source_candidate_id="cand_sales_order_channel",
        kind="dimension",
        canonical_name="Sales Order Channel",
        source_scopes=("satis_siparisleri",),
    )


def _june() -> ResolvedPeriod:
    return ResolvedPeriod(
        kind="absolute",
        source_text="Haziran 2026",
        time_dimension="sales_orders.opened_at",
        start="2026-06-01",
        end="2026-07-01",
    )


def _may() -> ResolvedPeriod:
    return ResolvedPeriod(
        kind="absolute",
        source_text="Mayıs 2026",
        time_dimension="sales_orders.opened_at",
        start="2026-05-01",
        end="2026-06-01",
    )


def _principal() -> PrincipalContextRef:
    return PrincipalContextRef(
        tenant_binding=TENANT,
        principal_subject=PRINCIPAL,
        roles=("analyst",),
    )


def breakdown_authority_and_intent() -> tuple[AcceptedStandardAuthority, ResolvedAnalyticsIntent]:
    projection = StandardProjection(
        obligation_ids=("obl-p13d-breakdown",),
        metric_handles=(METRIC_HANDLE,),
        dimension_handles=(DIMENSION_HANDLE,),
        period_handle=PERIOD_HANDLE,
    )
    authority = _accepted(
        case_id=BREAKDOWN_CASE,
        question=BREAKDOWN_QUESTION,
        projection=projection,
    )
    return authority, ResolvedAnalyticsIntent(
        authority_id=authority.authority_id,
        request_ref=authority.request_ref,
        source_message_hash=authority.source_message_hash,
        projection_hash=authority.projection_hash,
        semantic_context_version=CONTEXT_VERSION,
        obligation_ids=projection.obligation_ids,
        metrics=(_metric(),),
        dimensions=(_dimension(),),
        period=_june(),
        principal=_principal(),
    )


def ranking_authority_and_intent() -> tuple[AcceptedStandardAuthority, ResolvedAnalyticsIntent]:
    projection = StandardProjection(
        obligation_ids=("obl-p13d-ranking",),
        metric_handles=(METRIC_HANDLE,),
        dimension_handles=(DIMENSION_HANDLE,),
        period_handle=PERIOD_HANDLE,
        ranking_direction="desc",
        limit=2,
    )
    authority = _accepted(
        case_id=RANKING_CASE,
        question=RANKING_QUESTION,
        projection=projection,
    )
    return authority, ResolvedAnalyticsIntent(
        authority_id=authority.authority_id,
        request_ref=authority.request_ref,
        source_message_hash=authority.source_message_hash,
        projection_hash=authority.projection_hash,
        semantic_context_version=CONTEXT_VERSION,
        obligation_ids=projection.obligation_ids,
        metrics=(_metric(),),
        dimensions=(_dimension(),),
        period=_june(),
        ranking=ResolvedRanking(
            measure="Sales Order Count",
            direction="desc",
            limit=2,
        ),
        principal=_principal(),
    )


def comparison_authority_and_intent() -> tuple[AcceptedStandardAuthority, ResolvedAnalyticsIntent]:
    projection = StandardProjection(
        obligation_ids=("obl-p13d-comparison",),
        metric_handles=(METRIC_HANDLE,),
        comparison_handle=COMPARISON_HANDLE,
    )
    authority = _accepted(
        case_id=COMPARISON_CASE,
        question=COMPARISON_QUESTION,
        projection=projection,
    )
    return authority, ResolvedAnalyticsIntent(
        authority_id=authority.authority_id,
        request_ref=authority.request_ref,
        source_message_hash=authority.source_message_hash,
        projection_hash=authority.projection_hash,
        semantic_context_version=CONTEXT_VERSION,
        obligation_ids=projection.obligation_ids,
        metrics=(_metric(),),
        comparison=ResolvedComparison(
            mode="previous_period",
            source_text="Haziran 2026 ile Mayıs 2026",
            base_period=_june(),
            reference_period=_may(),
        ),
        principal=_principal(),
    )


def cases():
    return (
        (
            BREAKDOWN_CASE,
            BREAKDOWN_QUESTION,
            breakdown_authority_and_intent,
            (TABLE_RESOURCE, TIME_RESOURCE, CHANNEL_RESOURCE),
        ),
        (
            RANKING_CASE,
            RANKING_QUESTION,
            ranking_authority_and_intent,
            (TABLE_RESOURCE, TIME_RESOURCE, CHANNEL_RESOURCE),
        ),
        (
            COMPARISON_CASE,
            COMPARISON_QUESTION,
            comparison_authority_and_intent,
            (TABLE_RESOURCE, TIME_RESOURCE),
        ),
    )


def independent_oracles(path: Path) -> dict[str, Any]:
    con = duckdb.connect(str(path), read_only=True)
    breakdown_rows = con.execute(
        """
        SELECT kanal, COUNT(*)::BIGINT AS n
        FROM satis_siparisleri
        WHERE acilis_tarihi >= DATE '2026-06-01'
          AND acilis_tarihi < DATE '2026-07-01'
        GROUP BY kanal
        ORDER BY kanal
        """
    ).fetchall()
    ranking_rows = con.execute(
        """
        SELECT kanal, COUNT(*)::BIGINT AS n
        FROM satis_siparisleri
        WHERE acilis_tarihi >= DATE '2026-06-01'
          AND acilis_tarihi < DATE '2026-07-01'
        GROUP BY kanal
        ORDER BY n DESC, kanal ASC
        LIMIT 3
        """
    ).fetchall()
    comparison_rows = con.execute(
        """
        SELECT strftime(acilis_tarihi, '%Y-%m') AS month, COUNT(*)::BIGINT AS n
        FROM satis_siparisleri
        WHERE acilis_tarihi >= DATE '2026-05-01'
          AND acilis_tarihi < DATE '2026-07-01'
        GROUP BY 1
        ORDER BY 1
        """
    ).fetchall()
    if len(ranking_rows) < 2:
        raise RuntimeError("P13D ranking oracle has fewer than two channels")
    top_counts = [int(row[1]) for row in ranking_rows[:2]]
    if len(set(top_counts)) != 2:
        raise RuntimeError("P13D top-2 counts are tied; frozen ranking order is ambiguous")
    if len(ranking_rows) > 2 and int(ranking_rows[1][1]) == int(ranking_rows[2][1]):
        raise RuntimeError("P13D top-2 boundary is tied; frozen ranking case is ambiguous")
    comparison = {str(month): int(n) for month, n in comparison_rows}
    if set(comparison) != {"2026-05", "2026-06"}:
        raise RuntimeError(f"P13D comparison oracle months drifted: {comparison!r}")
    return {
        BREAKDOWN_CASE: {str(channel): int(n) for channel, n in breakdown_rows},
        RANKING_CASE: [
            [str(channel), int(n)]
            for channel, n in ranking_rows[:2]
        ],
        COMPARISON_CASE: comparison,
    }
