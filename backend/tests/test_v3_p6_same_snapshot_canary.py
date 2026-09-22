from __future__ import annotations

import base64
import hashlib
import json
import os
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

import httpx
import psycopg
import pytest
from wren import WrenEngine
from wren.model.data_source import DataSource

from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedPeriod,
    ResolvedSemanticRef,
)
from app.v3.semantic_spec import (
    DimensionSpec,
    DimaSemanticSpec,
    MetricSpec,
    SourceLineage,
    TimeSpec,
)
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    TemporalSemanticBinding,
)
from app.v3.substrate.metabase.models import ConstructedQuery, MetabaseRuntimePolicy


ROOT = Path(__file__).resolve().parents[1]
P6 = ROOT / "lab" / "metabase" / "p6"
FIXTURE = json.loads((P6 / "fixture.json").read_text(encoding="utf-8"))
WREN_MANIFEST = json.loads((P6 / "wren_manifest.json").read_text(encoding="utf-8"))

CTX = "p6-shared-v1"
TIME_KEY = "p6/p6_orders.order_date"
HEX_A = "a" * 64
HEX_B = "b" * 64


def _json_hash(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _fixture_manifest_fingerprint() -> str:
    return _json_hash(
        {
            "fixture_version": FIXTURE["fixture_version"],
            "schema": FIXTURE["schema"],
        }
    )


def _fixture_content_checksum() -> str:
    return _json_hash(
        {
            "customers": FIXTURE["customers"],
            "orders": FIXTURE["orders"],
        }
    )


def _expected_anchors():
    total = sum(int(row["amount"]) for row in FIXTURE["orders"])
    breakdown: dict[str, int] = defaultdict(int)
    for row in FIXTURE["orders"]:
        breakdown[str(row["region"])] += int(row["amount"])
    january = sum(
        int(row["amount"])
        for row in FIXTURE["orders"]
        if "2026-01-01" <= str(row["order_date"]) <= "2026-01-31"
    )
    return total, dict(sorted(breakdown.items())), january


def test_p6_fixture_manifest_and_three_canary_anchors_are_deterministic():
    assert FIXTURE["fixture_version"] == "p6-shared-v1"
    assert len(FIXTURE["orders"]) == 8
    assert len(FIXTURE["customers"]) == 4
    assert _expected_anchors() == (
        2000,
        {"East": 400, "North": 650, "South": 700, "West": 250},
        750,
    )
    assert len(_fixture_manifest_fingerprint()) == 64
    assert len(_fixture_content_checksum()) == 64


def _db_kwargs():
    return {
        "host": "127.0.0.1",
        "port": int(os.getenv("P6_ANALYTICS_DB_PORT", "55432")),
        "dbname": os.getenv("ANALYTICS_DB_NAME", "dima_analytics"),
        "user": os.getenv("ANALYTICS_DB_USER", "dima_analytics"),
        "password": os.getenv("ANALYTICS_DB_PASSWORD", "dima-analytics-lab"),
    }


def _actual_snapshot_identity():
    actual_schema: dict[str, list[list[str]]] = {}
    actual_content: dict[str, list[dict]] = {}

    with psycopg.connect(**_db_kwargs()) as conn:
        with conn.cursor() as cur:
            for table in ("p6_customers", "p6_orders"):
                cur.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (table,),
                )
                actual_schema[table] = [
                    [str(name), str(data_type)]
                    for name, data_type in cur.fetchall()
                ]

            cur.execute(
                "SELECT id, name, segment FROM p6_customers ORDER BY id"
            )
            actual_content["customers"] = [
                {"id": row[0], "name": row[1], "segment": row[2]}
                for row in cur.fetchall()
            ]
            cur.execute(
                """
                SELECT id, customer_id, order_date, region, channel, amount
                FROM p6_orders
                ORDER BY id
                """
            )
            actual_content["orders"] = [
                {
                    "id": row[0],
                    "customer_id": row[1],
                    "order_date": row[2].isoformat(),
                    "region": row[3],
                    "channel": row[4],
                    "amount": row[5],
                }
                for row in cur.fetchall()
            ]

    assert actual_schema == FIXTURE["schema"]
    assert actual_content == {
        "customers": FIXTURE["customers"],
        "orders": FIXTURE["orders"],
    }

    content_checksum = _json_hash(actual_content)
    assert content_checksum == _fixture_content_checksum()
    identity = {
        "fixture_version": FIXTURE["fixture_version"],
        "schema": actual_schema,
        "row_counts": {
            "p6_customers": len(actual_content["customers"]),
            "p6_orders": len(actual_content["orders"]),
        },
        "fixture_manifest_fingerprint": _fixture_manifest_fingerprint(),
        "content_checksum": content_checksum,
    }
    return identity, _json_hash(identity)


def _lineage(column: str):
    return (
        SourceLineage(
            source_id=f"p6_orders.{column}",
            database_ref="Dima Analytics Lab",
            schema_name="public",
            table_name="p6_orders",
            column_name=column,
        ),
    )


def _catalog_object(column: str) -> CurrentCatalogObject:
    entity_id = f"p6:p6_orders.{column}"
    return CurrentCatalogObject(
        source_id=f"p6_orders.{column}",
        database_ref="Dima Analytics Lab",
        schema_name="public",
        table_name="p6_orders",
        column_name=column,
        resource_entity_id=entity_id,
        resource_fingerprint=_json_hash(
            {
                "database": "Dima Analytics Lab",
                "schema": "public",
                "table": "p6_orders",
                "column": column,
                "entity_id": entity_id,
            }
        ),
    )


def _binding_snapshot() -> DimaExecutionBindingSnapshot:
    spec = DimaSemanticSpec(
        semantic_context_version=CTX,
        metrics=(
            MetricSpec(
                metric_id="metric.p6_revenue",
                name="P6 Revenue",
                aggregation="sum",
                semantic_version="1",
                compatibility_hash=HEX_A,
                source_lineage=_lineage("amount"),
            ),
        ),
        dimensions=(
            DimensionSpec(
                dimension_id="dimension.p6_region",
                name="P6 Region",
                data_type="text",
                semantic_version="1",
                source_lineage=_lineage("region"),
            ),
            DimensionSpec(
                dimension_id="dimension.p6_order_date",
                name="P6 Order Date",
                data_type="date",
                semantic_version="1",
                source_lineage=_lineage("order_date"),
            ),
        ),
        time_specs=(
            TimeSpec(
                time_id="time.p6_order_date",
                dimension_ref="dimension.p6_order_date",
                grain="day",
            ),
        ),
    )
    return DimaExecutionBindingSnapshot(
        semantic_context_version=CTX,
        semantic_spec=spec,
        candidate_bindings=(
            CandidateSemanticBinding(
                candidate_id="p6_metric",
                semantic_id="metric.p6_revenue",
                kind="metric",
            ),
            CandidateSemanticBinding(
                candidate_id="p6_region",
                semantic_id="dimension.p6_region",
                kind="dimension",
            ),
        ),
        temporal_bindings=(
            TemporalSemanticBinding(
                compatibility_key=TIME_KEY,
                dimension_id="dimension.p6_order_date",
            ),
        ),
        current_catalog=CurrentCatalogSnapshot(
            catalog_version="p6-shared-catalog-v1",
            objects=tuple(
                _catalog_object(column)
                for column in ("amount", "region", "order_date")
            ),
        ),
    )


def _metric_ref():
    return ResolvedSemanticRef(
        semantic_ref="p6_handle_metric",
        source_candidate_id="p6_metric",
        kind="metric",
        canonical_name="P6 Revenue",
        source_scopes=("p6_orders",),
    )


def _region_ref():
    return ResolvedSemanticRef(
        semantic_ref="p6_handle_region",
        source_candidate_id="p6_region",
        kind="dimension",
        canonical_name="P6 Region",
        source_scopes=("p6_orders",),
    )


def _intent(*, breakdown=False, period=False) -> ResolvedAnalyticsIntent:
    return ResolvedAnalyticsIntent(
        authority_id="auth-p6-canary",
        request_ref="p6-canary-post-authority",
        source_message_hash=HEX_A,
        projection_hash=HEX_B,
        semantic_context_version=CTX,
        obligation_ids=("obl-p6-canary",),
        metrics=(_metric_ref(),),
        dimensions=(_region_ref(),) if breakdown else (),
        period=(
            ResolvedPeriod(
                kind="absolute",
                source_text="p6-fixture-january",
                time_dimension=TIME_KEY,
                start="2026-01-01",
                end="2026-01-31",
            )
            if period
            else None
        ),
        principal=PrincipalContextRef(
            tenant_binding="tenant-p6-fixture",
            principal_subject="p6-canary-user",
            roles=("analyst",),
        ),
    )


def _wren_engine():
    manifest = base64.b64encode(
        json.dumps(
            WREN_MANIFEST,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).decode("ascii")
    return WrenEngine(
        manifest,
        DataSource.postgres,
        _db_kwargs(),
        fallback=False,
    )


def _login_metabase(base_url: str) -> str:
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
    assert token
    return str(token)


def _metabase_client():
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    return MetabaseAgentClient(
        base_url=base_url,
        session_token=_login_metabase(base_url),
        policy=MetabaseRuntimePolicy(
            runtime_version="v0.63.18",
            runtime_image_digest=(
                "sha256:1160b570cb11c107bce00e71293552df"
                "8a8363e01a32c2c7a048cee002dc8a73"
            ),
            raw_sql_policy="disabled",
            observed_page_size=200,
            observed_total_row_cap=2000,
        ),
    )


def _execute_metabase(client, canonicalizer, intent):
    plan = MetabaseProjectionCompiler.compile(
        intent=intent,
        snapshot=_binding_snapshot(),
    )
    canonical = canonicalizer.canonicalize(plan)
    assert len(canonical.steps) == 1
    response = client.execute_serialized(
        ConstructedQuery(
            serialized_query=canonical.steps[0].serialized_query
        )
    )
    assert response.status.value == "completed"
    rows = response.data.get("rows")
    assert isinstance(rows, list)
    return rows


def _metric_value(rows) -> Decimal:
    assert len(rows) == 1 and len(rows[0]) == 1
    return Decimal(str(rows[0][0]))


def _breakdown_values(rows) -> dict[str, Decimal]:
    values: dict[str, Decimal] = {}
    for row in rows:
        assert isinstance(row, list) and len(row) == 2
        text_values = [item for item in row if isinstance(item, str)]
        number_values = [
            item
            for item in row
            if isinstance(item, (int, float)) and not isinstance(item, bool)
        ]
        assert len(text_values) == 1 and len(number_values) == 1
        values[text_values[0]] = Decimal(str(number_values[0]))
    return dict(sorted(values.items()))


@pytest.mark.skipif(
    os.getenv("DIMA_METABASE_P6A_LIVE") != "1",
    reason="P6A shared PostgreSQL + pinned Metabase lab required",
)
def test_p6a_same_physical_postgres_snapshot_three_case_canary():
    snapshot, snapshot_id = _actual_snapshot_identity()
    expected_total, expected_breakdown, expected_january = _expected_anchors()

    with _wren_engine() as wren:
        wren_total = wren.query(
            'SELECT SUM(amount) AS revenue FROM "p6_orders"'
        )
        wren_breakdown = wren.query(
            'SELECT region, SUM(amount) AS revenue FROM "p6_orders" '
            'GROUP BY region ORDER BY region'
        )
        wren_period = wren.query(
            'SELECT SUM(amount) AS revenue FROM "p6_orders" '
            "WHERE order_date >= DATE '2026-01-01' "
            "AND order_date <= DATE '2026-01-31'"
        )

    assert Decimal(str(wren_total["revenue"][0].as_py())) == Decimal(
        str(expected_total)
    )
    assert {
        str(row["region"]): Decimal(str(row["revenue"]))
        for row in wren_breakdown.to_pylist()
    } == {
        key: Decimal(str(value))
        for key, value in expected_breakdown.items()
    }
    assert Decimal(str(wren_period["revenue"][0].as_py())) == Decimal(
        str(expected_january)
    )

    with _metabase_client() as client:
        canonicalizer = MetabaseCanonicalizer(client=client)
        mb_total = _metric_value(
            _execute_metabase(client, canonicalizer, _intent())
        )
        mb_breakdown = _breakdown_values(
            _execute_metabase(
                client,
                canonicalizer,
                _intent(breakdown=True),
            )
        )
        mb_period = _metric_value(
            _execute_metabase(
                client,
                canonicalizer,
                _intent(period=True),
            )
        )

    assert mb_total == Decimal(str(expected_total))
    assert mb_breakdown == {
        key: Decimal(str(value))
        for key, value in expected_breakdown.items()
    }
    assert mb_period == Decimal(str(expected_january))

    print(
        json.dumps(
            {
                "p6a": "same-snapshot-canary-green",
                "snapshot": snapshot,
                "snapshot_id": snapshot_id,
                "canaries": {
                    "metric": str(mb_total),
                    "breakdown": {
                        key: str(value)
                        for key, value in mb_breakdown.items()
                    },
                    "period": str(mb_period),
                },
            },
            sort_keys=True,
        )
    )
