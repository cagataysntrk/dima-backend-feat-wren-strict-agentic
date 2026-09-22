from __future__ import annotations

import os

import httpx
import pytest

from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import FastMetabaseRuntimePolicy


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_FAST_METABASE_LIVE") != "1",
    reason="Fast Track pinned Metabase lab required",
)


def login(base_url: str) -> str:
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


def test_fast_gateway_crosses_pinned_agent_api_without_v3_or_raw_sql():
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    auth = FastMetabaseAuthContext(
        tenant_id="fast-live-tenant",
        dima_user_id="fast-live-user",
        principal_id="metabase-admin-1",
        mode=FastMetabaseAuthMode.SESSION,
        secret=login(base_url),
        role_scope_digest="fast-live-admin",
    )
    policy = FastMetabaseRuntimePolicy(
        max_page_rows=200,
        max_total_rows_per_run=1000,
    )

    with FastMetabaseGateway(
        base_url=base_url,
        auth=auth,
        policy=policy,
    ) as gateway:
        found = gateway.search(term_queries=("orders",))
        table = next(
            item
            for item in found.data
            if item.get("type") == "table"
            and str(item.get("name", "")).lower() == "orders"
        )

        database_id = int(table["database_id"])
        database_uri = f"metabase://database/{database_id}"
        resource = gateway.read_resource((database_uri,)).resources[0]
        assert resource.failed is False
        assert resource.content is not None
        structured = resource.content.structured_output
        assert structured is not None

        database_name = str(structured["name"])
        schema = str(table.get("database_schema") or "public")
        table_name = str(table["name"])

        one_row = {
            "lib/type": "mbql/query",
            "stages": [{
                "lib/type": "mbql.stage/mbql",
                "source-table": [database_name, schema, table_name],
                "limit": 1,
            }],
        }

        handshake = gateway.startup_handshake(
            portable_probe_query=one_row,
            resource_probe_uri=database_uri,
        )
        assert handshake.ready is True
        assert handshake.runtime_version == "v0.63.18"
        assert handshake.observed_page_limit == 200

        paged = {
            "lib/type": "mbql/query",
            "stages": [{
                "lib/type": "mbql.stage/mbql",
                "source-table": [database_name, schema, table_name],
                "limit": 205,
            }],
        }

        first = gateway.query(paged)
        assert first.row_count == 200
        assert first.continuation is not None

        second = gateway.continue_query(first.continuation)
        assert second.row_count == 5
        assert second.continuation is None

        constructed = gateway.construct_query(one_row)
        executed = gateway.execute_serialized(constructed)
        assert executed.status.value == "completed"

        fingerprint = gateway.access_fingerprint
        assert fingerprint.tenant_id == "fast-live-tenant"
        assert len(fingerprint.digest) == 64

        assert not hasattr(gateway, "execute_sql")
        assert not hasattr(gateway, "raw_sql")
