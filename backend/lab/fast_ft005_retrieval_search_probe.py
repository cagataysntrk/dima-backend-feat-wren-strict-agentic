"""FT-005 real pinned-Metabase retrieval-language probe.

Measurement only. It does not patch product semantics and it does not treat string
equality as evidence of retrieval quality.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import httpx

from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import FastMetabaseRuntimePolicy
from app.fast.resource_registry import discover_resource_registry


OUT = Path(
    os.getenv(
        "DIMA_FAST_FT005_RETRIEVAL_PROBE_RECEIPT",
        "lab/metabase/artifacts/ft005-retrieval-search-probe.json",
    )
)

QUESTION = "Son 30 günde sipariş tutarı ne kadar?"


def _login(base_url: str) -> str:
    response = httpx.post(
        base_url + "/api/session",
        json={
            "username": os.environ["MB_ADMIN_EMAIL"],
            "password": os.environ["MB_ADMIN_PASSWORD"],
        },
        timeout=30,
    )
    response.raise_for_status()
    session = str(response.json().get("id") or "")
    if not session:
        raise RuntimeError("Metabase session missing")
    return session


def _table_rows(response) -> list[dict]:
    rows = []
    for item in response.data:
        if str(item.get("type") or "").lower() != "table":
            continue
        rows.append(
            {
                "name": item.get("name"),
                "display_name": item.get("display_name") or item.get("display-name"),
                "uri": item.get("uri"),
                "id": item.get("id"),
            }
        )
    return rows


def _orders_hit(rows: list[dict]) -> bool:
    return any(
        str(row.get("name") or "").strip().lower() == "orders"
        or str(row.get("uri") or "").startswith("metabase://table/")
        and str(row.get("display_name") or "").strip().lower() == "orders"
        for row in rows
    )


def main() -> int:
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    session = _login(base_url)

    cases = (
        ("turkish_order_singular", ("sipariş",)),
        ("turkish_order_plural", ("siparişler",)),
        ("turkish_order_pair", ("sipariş", "siparişler")),
        ("mixed_luna", ("sipariş", "order")),
        ("english_order", ("order",)),
        ("english_orders", ("orders",)),
        ("metric_phrase", ("sipariş tutarı",)),
    )

    receipt = {
        "status": "RED",
        "question": QUESTION,
        "target_table": "orders",
        "cases": [],
        "failures": [],
    }

    auth = FastMetabaseAuthContext(
        tenant_id="__superadmin__",
        dima_user_id="ft005-retrieval-probe",
        principal_id="metabase-lab-admin",
        mode=FastMetabaseAuthMode.SESSION,
        secret=session,
        role_scope_digest="ft005-retrieval-probe",
    )

    try:
        with FastMetabaseGateway(
            base_url=base_url,
            auth=auth,
            policy=FastMetabaseRuntimePolicy(
                max_page_rows=200,
                max_total_rows_per_run=1000,
            ),
        ) as gateway:
            for name, terms in cases:
                case = {
                    "name": name,
                    "term_queries": list(terms),
                    "passed_transport": False,
                }
                try:
                    direct = gateway.search(
                        term_queries=terms,
                        semantic_queries=(),
                    )
                    direct_rows = _table_rows(direct)

                    combined = gateway.search(
                        term_queries=terms,
                        semantic_queries=(QUESTION,),
                    )
                    combined_rows = _table_rows(combined)

                    registry, mode = discover_resource_registry(
                        gateway,
                        term_queries=terms,
                        semantic_query=QUESTION,
                        max_candidates=8,
                    )
                    candidates = [
                        {
                            "handle": item.handle,
                            "name": item.name,
                            "display_name": item.display_name,
                        }
                        for item in registry.candidates
                    ]

                    case.update(
                        {
                            "passed_transport": True,
                            "direct_search": {
                                "total_count": direct.total_count,
                                "tables": direct_rows,
                                "orders_hit": _orders_hit(direct_rows),
                            },
                            "combined_search": {
                                "total_count": combined.total_count,
                                "tables": combined_rows,
                                "orders_hit": _orders_hit(combined_rows),
                            },
                            "fast_discovery": {
                                "mode": mode,
                                "candidates": candidates,
                                "orders_candidate": any(
                                    item["name"].strip().lower() == "orders"
                                    for item in candidates
                                ),
                            },
                        }
                    )
                except Exception as exc:
                    case["error"] = f"{type(exc).__name__}: {exc}"
                    receipt["failures"].append(name)
                receipt["cases"].append(case)

        receipt["summary"] = {
            item["name"]: {
                "direct_orders_hit": item.get("direct_search", {}).get("orders_hit"),
                "combined_orders_hit": item.get("combined_search", {}).get("orders_hit"),
                "fast_discovery_mode": item.get("fast_discovery", {}).get("mode"),
                "fast_orders_candidate": item.get("fast_discovery", {}).get("orders_candidate"),
            }
            for item in receipt["cases"]
        }
        receipt["status"] = "GREEN" if not receipt["failures"] else "RED"
    except Exception as exc:
        receipt["failures"].append(f"setup:{type(exc).__name__}:{exc}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
