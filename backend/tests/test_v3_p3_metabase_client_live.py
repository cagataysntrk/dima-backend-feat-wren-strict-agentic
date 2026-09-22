from __future__ import annotations

import os

import httpx
import pytest

from app.v3.substrate.metabase.adapter import MetabaseRuntimeAdapter
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.models import MetabaseRuntimePolicy


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_METABASE_P3_LIVE") != "1",
    reason="M2 pinned Metabase lab required",
)


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
    token = response.json().get("id")
    assert token
    return str(token)


def test_p3_client_crosses_pinned_agent_api_and_keeps_continuation_separate():
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    policy = MetabaseRuntimePolicy(
        runtime_version="v0.63.18",
        runtime_image_digest=(
            "sha256:1160b570cb11c107bce00e71293552df"
            "8a8363e01a32c2c7a048cee002dc8a73"
        ),
        raw_sql_policy="disabled",
        observed_page_size=200,
        observed_total_row_cap=2000,
    )

    with MetabaseAgentClient(
        base_url=base_url,
        session_token=_login(base_url),
        policy=policy,
    ) as client:
        search = client.search(term_queries=("orders",))
        table = next(
            item
            for item in search.data
            if item.get("type") == "table"
            and str(item.get("name", "")).lower() == "orders"
        )
        database_id = int(table["database_id"])
        database = client.read_resource(
            (f"metabase://database/{database_id}",)
        )
        content = database.resources[0]["content"]
        database_name = str(content["name"])
        schema = str(table.get("database_schema") or "public")
        table_name = str(table["name"])

        probe = {
            "lib/type": "mbql/query",
            "stages": [{
                "lib/type": "mbql.stage/mbql",
                "source-table": [database_name, schema, table_name],
                "limit": 1,
            }],
        }
        handshake = MetabaseRuntimeAdapter(client=client).inspect_runtime(
            portable_probe_query=probe,
        )
        assert handshake.ready is True
        assert handshake.verified_operations == (
            "health",
            "agent_ping",
            "construct_query",
            "execute",
            "combined_query",
        )

        paged = {
            "lib/type": "mbql/query",
            "stages": [{
                "lib/type": "mbql.stage/mbql",
                "source-table": [database_name, schema, table_name],
                "limit": 205,
            }],
        }
        first = client.query(paged)
        assert first.row_count == 200
        assert first.continuation is not None

        second = client.continue_query(first.continuation)
        assert second.row_count == 5
        assert second.continuation is None

        constructed = client.construct_query(probe)
        executed = client.execute_serialized(constructed)
        assert executed.status.value == "completed"

        assert not hasattr(client, "execute_sql")
