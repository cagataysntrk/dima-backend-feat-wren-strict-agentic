"""Frozen P13C-01 same-table textual equality case and shared provider-free/live helpers."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import httpx

from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedSemanticRef,
    StandardProjection,
    projection_hash,
)
from app.v3.authority import AcceptedStandardAuthority, StandardWorkMode
from app.v3.resource_provisioning import ManagedResourceBinding, ResourceKind
from app.v3.semantic_spec import (
    DimensionSpec,
    DimaSemanticSpec,
    ManagedResourcePolicy,
    MetricSpec,
    SourceLineage,
    TimeSpec,
)
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    TemporalSemanticBinding,
)
from app.v3.native_standard.contracts import NativeAttestedRuntimeIdentity


QUESTION = "Haziran 2026'da Web kanalından kaç satış siparişi açıldı?"
CASE_ID = "P13C-01"
WAREHOUSE_NAME = "Dima Analytics Lab"
TABLE = "satis_siparisleri"
TIME_FIELD = "acilis_tarihi"
FILTER_FIELD = "kanal"
FILTER_VALUE = "Web"
TABLE_RESOURCE = "boyahane:satis_siparisleri"
TIME_RESOURCE = "boyahane:satis_siparisleri.acilis_tarihi"
FILTER_RESOURCE = "boyahane:satis_siparisleri.kanal"
CONTEXT_VERSION = "ctx-p13c-v1"
TENANT = "tenant-boyahane"
PRINCIPAL = "user-p13c"
FILTER_SEMANTIC_REF = "handle.sales_order_channel.web"


def h(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def login(base_url: str, email: str, password: str) -> str:
    response = httpx.post(
        base_url.rstrip("/") + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = str((response.json() or {}).get("id") or "")
    if not token:
        raise RuntimeError("Metabase session token missing")
    return token


def _items(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return [x for x in body if isinstance(x, dict)]
    if isinstance(body, dict):
        for key in ("data", "items"):
            if isinstance(body.get(key), list):
                return [x for x in body[key] if isinstance(x, dict)]
    return []


def discover_catalog(
    base_url: str,
    token: str,
    *,
    timeout_seconds: int = 240,
) -> tuple[int, int, int, int, str, int]:
    with httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={"X-Metabase-Session": token},
        timeout=30,
    ) as client:
        current = client.get("/api/user/current")
        current.raise_for_status()
        subject_id = int(current.json()["id"])

        response = client.get("/api/database")
        response.raise_for_status()
        dbs = [x for x in _items(response.json()) if x.get("name") == WAREHOUSE_NAME]
        if len(dbs) != 1:
            raise RuntimeError(f"expected one analytics database, observed {len(dbs)}")
        database_id = int(dbs[0]["id"])

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = client.get(
                f"/api/database/{database_id}/metadata",
                params={"include_hidden": "true"},
            )
            if response.status_code == 200:
                body = response.json()
                tables = body.get("tables") if isinstance(body, dict) else None
                if isinstance(tables, list):
                    matches = [
                        x for x in tables
                        if isinstance(x, dict) and x.get("name") == TABLE
                    ]
                    if len(matches) == 1:
                        table = matches[0]
                        fields = table.get("fields") or []
                        by_name = {
                            str(x.get("name")): x
                            for x in fields
                            if isinstance(x, dict) and x.get("name")
                        }
                        if TIME_FIELD in by_name and FILTER_FIELD in by_name:
                            return (
                                database_id,
                                int(table["id"]),
                                int(by_name[TIME_FIELD]["id"]),
                                int(by_name[FILTER_FIELD]["id"]),
                                str(table.get("schema") or "public"),
                                subject_id,
                            )
            time.sleep(2)
    raise RuntimeError("Metabase metadata sync did not expose P13C source/time/filter fields")


def binding_snapshot(
    database_id: int,
    table_id: int,
    time_field_id: int,
    filter_field_id: int,
    schema_name: str,
) -> DimaExecutionBindingSnapshot:
    table = SourceLineage(
        source_id="source.satis_siparisleri",
        database_ref=WAREHOUSE_NAME,
        schema_name=schema_name,
        table_name=TABLE,
    )
    opened = SourceLineage(
        source_id="source.satis_siparisleri.acilis_tarihi",
        database_ref=WAREHOUSE_NAME,
        schema_name=schema_name,
        table_name=TABLE,
        column_name=TIME_FIELD,
    )
    channel = SourceLineage(
        source_id="source.satis_siparisleri.kanal",
        database_ref=WAREHOUSE_NAME,
        schema_name=schema_name,
        table_name=TABLE,
        column_name=FILTER_FIELD,
    )
    table_fp = h({"db": "boyahane", "schema": schema_name, "table": TABLE})
    time_fp = h(
        {"db": "boyahane", "schema": schema_name, "table": TABLE, "column": TIME_FIELD}
    )
    filter_fp = h(
        {"db": "boyahane", "schema": schema_name, "table": TABLE, "column": FILTER_FIELD}
    )
    spec = DimaSemanticSpec(
        semantic_context_version=CONTEXT_VERSION,
        metrics=(
            MetricSpec(
                metric_id="metric.sales_order_count",
                name="Sales Order Count",
                aggregation="count",
                semantic_version="1",
                compatibility_hash=h(
                    {"metric": "metric.sales_order_count", "source": table.model_dump()}
                ),
                source_lineage=(table,),
            ),
        ),
        dimensions=(
            DimensionSpec(
                dimension_id="dimension.sales_order_opened_at",
                name="Sales Order Opened At",
                data_type="datetime",
                semantic_version="1",
                source_lineage=(opened,),
            ),
            DimensionSpec(
                dimension_id="dimension.sales_order_channel",
                name="Sales Order Channel",
                data_type="string",
                semantic_version="1",
                source_lineage=(channel,),
            ),
        ),
        time_specs=(
            TimeSpec(
                time_id="time.sales_order_opened_at",
                dimension_ref="dimension.sales_order_opened_at",
                grain="day",
            ),
        ),
        managed_resources=(
            ManagedResourcePolicy(
                semantic_ref="metric.sales_order_count",
                ownership="DIMA_MANAGED",
                reconciliation="OVERWRITE",
            ),
        ),
    )
    return DimaExecutionBindingSnapshot(
        semantic_context_version=CONTEXT_VERSION,
        semantic_spec=spec,
        candidate_bindings=(
            CandidateSemanticBinding(
                candidate_id="cand_sales_order_count",
                semantic_id="metric.sales_order_count",
                kind="metric",
            ),
            CandidateSemanticBinding(
                candidate_id="cand_sales_order_channel",
                semantic_id="dimension.sales_order_channel",
                kind="filter",
            ),
        ),
        temporal_bindings=(
            TemporalSemanticBinding(
                compatibility_key="sales_orders.opened_at",
                dimension_id="dimension.sales_order_opened_at",
            ),
        ),
        current_catalog=CurrentCatalogSnapshot(
            catalog_version="boyahane-p13c-live-" + table_fp[:16],
            objects=(
                CurrentCatalogObject(
                    source_id=table.source_id,
                    database_ref=WAREHOUSE_NAME,
                    schema_name=schema_name,
                    table_name=TABLE,
                    resource_entity_id=TABLE_RESOURCE,
                    resource_fingerprint=table_fp,
                    metabase_database_id=database_id,
                    metabase_table_id=table_id,
                ),
                CurrentCatalogObject(
                    source_id=opened.source_id,
                    database_ref=WAREHOUSE_NAME,
                    schema_name=schema_name,
                    table_name=TABLE,
                    column_name=TIME_FIELD,
                    resource_entity_id=TIME_RESOURCE,
                    resource_fingerprint=time_fp,
                    metabase_database_id=database_id,
                    metabase_table_id=table_id,
                    metabase_field_id=time_field_id,
                ),
                CurrentCatalogObject(
                    source_id=channel.source_id,
                    database_ref=WAREHOUSE_NAME,
                    schema_name=schema_name,
                    table_name=TABLE,
                    column_name=FILTER_FIELD,
                    resource_entity_id=FILTER_RESOURCE,
                    resource_fingerprint=filter_fp,
                    metabase_database_id=database_id,
                    metabase_table_id=table_id,
                    metabase_field_id=filter_field_id,
                ),
            ),
        ),
    )


def authority_and_intent() -> tuple[AcceptedStandardAuthority, ResolvedAnalyticsIntent]:
    source_hash = hashlib.sha256(QUESTION.encode("utf-8")).hexdigest()
    projection = StandardProjection(
        obligation_ids=("obl-p13c-01",),
        metric_handles=("handle.sales_order_count",),
        filter_handles=(FILTER_SEMANTIC_REF,),
        period_handle="handle.period.june_2026",
    )
    p_hash = projection_hash(projection)
    authority_id = "asa_" + h(
        {"case": CASE_ID, "source": source_hash, "projection": p_hash}
    )[:24]
    authority = AcceptedStandardAuthority(
        authority_id=authority_id,
        turn_id="p13c-01-live",
        request_ref="p13c:01",
        source_message_hash=source_hash,
        context_version=CONTEXT_VERSION,
        projection_hash=p_hash,
        semantic_handle_refs=(
            "handle.sales_order_count",
            FILTER_SEMANTIC_REF,
            "handle.period.june_2026",
        ),
        accepted_attempt_id="p13c-01-live-attempt-1",
        model_role="native-metabot",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
        created_at_iso=datetime.now(timezone.utc).isoformat(),
    )
    intent = ResolvedAnalyticsIntent(
        authority_id=authority.authority_id,
        request_ref=authority.request_ref,
        source_message_hash=authority.source_message_hash,
        projection_hash=authority.projection_hash,
        semantic_context_version=authority.context_version,
        obligation_ids=projection.obligation_ids,
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_count",
                source_candidate_id="cand_sales_order_count",
                kind="metric",
                canonical_name="Sales Order Count",
                source_scopes=(TABLE,),
            ),
        ),
        filters=(
            ResolvedFilterRef(
                semantic_ref=FILTER_SEMANTIC_REF,
                source_candidate_id="cand_sales_order_channel",
                dimension_name="Sales Order Channel",
                value=FILTER_VALUE,
                source_scopes=(TABLE,),
                sensitive=False,
            ),
        ),
        period=ResolvedPeriod(
            kind="absolute",
            source_text="Haziran 2026",
            time_dimension="sales_orders.opened_at",
            start="2026-06-01",
            end="2026-07-01",
        ),
        principal=PrincipalContextRef(
            tenant_binding=TENANT,
            principal_subject=PRINCIPAL,
            roles=("analyst",),
        ),
    )
    return authority, intent


def metric_definition_intent() -> ResolvedAnalyticsIntent:
    _, live_intent = authority_and_intent()
    projection = StandardProjection(
        obligation_ids=("obl-p13c-metric-definition",),
        metric_handles=("handle.sales_order_count",),
    )
    return live_intent.model_copy(
        update={
            "authority_id": "p9b:metric.sales_order_count:p13c",
            "request_ref": "p9b:metric.sales_order_count:p13c",
            "source_message_hash": h(
                {
                    "canonical_metric": "metric.sales_order_count",
                    "semantic_context_version": CONTEXT_VERSION,
                }
            ),
            "projection_hash": projection_hash(projection),
            "obligation_ids": projection.obligation_ids,
            "filters": (),
            "period": None,
        }
    )


def current_user_values(
    base_url: str,
    token: str,
    *,
    field_id: int,
) -> tuple[Any, ...]:
    response = httpx.get(
        base_url.rstrip("/") + f"/api/field/{field_id}/values",
        headers={"X-Metabase-Session": token, "Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    rows = body.get("values") if isinstance(body, dict) else None
    if not isinstance(rows, list):
        raise RuntimeError("restricted field-values response has no values list")
    return tuple(
        row[0]
        for row in rows
        if isinstance(row, list) and row
    )


def independent_oracle(duckdb_path: Path) -> int:
    con = duckdb.connect(str(duckdb_path), read_only=True)
    row = con.execute(
        """
        SELECT COUNT(*)::BIGINT
        FROM satis_siparisleri
        WHERE acilis_tarihi >= DATE '2026-06-01'
          AND acilis_tarihi < DATE '2026-07-01'
          AND kanal = ?
        """,
        [FILTER_VALUE],
    ).fetchone()
    if row is None:
        raise RuntimeError("P13C independent oracle returned no row")
    return int(row[0])


def managed_metric_binding(
    path: Path,
    *,
    engine_sha: str,
    platform_sha: str,
) -> ManagedResourceBinding:
    body = json.loads(path.read_text(encoding="utf-8"))
    if body.get("status") != "GREEN":
        raise RuntimeError("P13C semantic availability proof is not GREEN")
    if body.get("engine_sha") != engine_sha or body.get("platform_sha") != platform_sha:
        raise RuntimeError("P13C semantic availability identity differs from live occurrence")
    binding = ManagedResourceBinding.model_validate(body.get("binding"))
    if (
        binding.tenant_binding != TENANT
        or binding.canonical_id != "metric.sales_order_count"
        or binding.resource_kind != ResourceKind.METRIC
        or binding.semantic_context_version != CONTEXT_VERSION
        or binding.applied_version != "1"
        or binding.ownership != "DIMA_MANAGED"
        or binding.metabase_local_id is None
        or binding.metabase_entity_id is None
    ):
        raise RuntimeError("P13C semantic availability binding is not the frozen metric")
    return binding


def assert_identity(
    identity: NativeAttestedRuntimeIdentity,
    *,
    engine_sha: str,
    upstream_sha: str,
    runtime_tag: str,
    build_identity: str,
    image_identity: str,
) -> None:
    expected = {
        "repository": "UpcyTech/dima-metabase-engine",
        "revision_sha": engine_sha,
        "upstream_base_sha": upstream_sha,
        "runtime_tag": runtime_tag,
        "build_identity": build_identity,
        "image_identity": image_identity,
    }
    actual = identity.model_dump(mode="json")
    for key, value in expected.items():
        if actual[key] != value:
            raise RuntimeError(
                f"runtime identity mismatch {key}: expected={value!r} actual={actual[key]!r}"
            )
