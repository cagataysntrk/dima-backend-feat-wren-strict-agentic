"""CI-only Fast Ask server for FT-003 browser proof.

The HTTP path, deterministic authority/query/evidence code, FastMetabaseGateway and
pinned Metabase DB are real. Only cognition is scripted so browser correctness is
not dependent on an external model provider.
"""

from __future__ import annotations

import os

import httpx
import uvicorn

from app.fast.application import create_fast_application
from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import (
    AggregationKind,
    AskDraft,
    DraftStatus,
    DraftTemporalIntent,
    SelectionDecision,
    SelectionPurpose,
    TemporalKind,
)
from app.fast.ask_service import FastAskService
from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import FastMetabaseRuntimePolicy


COUNT = "Son 30 günde kaç sipariş var?"
SUM = "Son 30 gündeki sipariş tutarı ne kadar?"
BREAKDOWN = "Son 30 günde bölgelere göre sipariş tutarı"
CLARIFICATION = "Siparişleri say."
UNSUPPORTED = "Siparişlerin ortalama tutarı nedir?"
FAILURE = "Hatalı alanla sipariş tutarı"


class BrowserCognition:
    def draft(self, *, question: str) -> AskDraft:
        if question == UNSUPPORTED:
            raise FastAskError(
                FastAskErrorCode.UNSUPPORTED,
                "FT-003 yalnız COUNT/SUM ve isteğe bağlı tek kırılımı destekliyor",
            )

        if question in (SUM, BREAKDOWN, FAILURE):
            aggregation = AggregationKind.SUM
            measure = "amount"
        else:
            aggregation = AggregationKind.COUNT
            measure = None

        return AskDraft(
            status=DraftStatus.SUPPORTED,
            unsupported_reason=None,
            search_terms=("orders",),
            aggregation=aggregation,
            measure_hint=measure,
            breakdown_hint="region" if question == BREAKDOWN else None,
            temporal=DraftTemporalIntent(
                kind=TemporalKind.LAST_N_DAYS,
                days=30,
                start_date=None,
                end_date=None,
            ),
        )

    def select_resource(self, *, question, candidates):
        if question == CLARIFICATION:
            return SelectionDecision(selected_handle=None)
        selected = next(item for item in candidates if item.name.lower() == "orders")
        return SelectionDecision(selected_handle=selected.handle)

    def select_field(self, *, question, purpose, hint, candidates):
        if question == FAILURE and purpose == SelectionPurpose.MEASURE:
            return SelectionDecision(selected_handle="fast_field_999")
        target = {
            SelectionPurpose.MEASURE: "amount",
            SelectionPurpose.TEMPORAL: "order_date",
            SelectionPurpose.BREAKDOWN: "region",
        }[purpose]
        selected = next(item for item in candidates if item.name.lower() == target)
        return SelectionDecision(selected_handle=selected.handle)


def metabase_session(base_url: str) -> str:
    response = httpx.post(
        base_url + "/api/session",
        json={
            "username": os.environ["MB_ADMIN_EMAIL"],
            "password": os.environ["MB_ADMIN_PASSWORD"],
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("id")
    if not token:
        raise RuntimeError("Metabase login returned no session")
    return str(token)


def build_app():
    base_url = f"http://127.0.0.1:{os.getenv('METABASE_PORT', '3300')}"
    session = metabase_session(base_url)

    def gateway_factory(principal):
        return FastMetabaseGateway(
            base_url=base_url,
            auth=FastMetabaseAuthContext(
                tenant_id=principal.tenant_id or "__superadmin__",
                dima_user_id=principal.user_id,
                principal_id="metabase-lab-admin",
                mode=FastMetabaseAuthMode.SESSION,
                secret=session,
                role_scope_digest="ft003-browser-synthetic-lab",
            ),
            policy=FastMetabaseRuntimePolicy(
                max_page_rows=200,
                max_total_rows_per_run=1000,
            ),
        )

    return create_fast_application(
        service=FastAskService(
            cognition=BrowserCognition(),
            gateway_factory=gateway_factory,
        )
    )


if __name__ == "__main__":
    uvicorn.run(build_app(), host="0.0.0.0", port=8000, log_level="info")
