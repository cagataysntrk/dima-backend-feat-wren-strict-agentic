from __future__ import annotations

import os

import httpx
import pytest

from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.models import MetabaseRuntimePolicy
from app.v3.substrate.metabase.p3a_fixture import build_cases, build_snapshot
from app.v3.substrate.metabase.p3a_models import P3AResult
from app.v3.substrate.metabase.p3a_preflight import MetabaseBridgePreflightCompiler


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_METABASE_P3A_LIVE") != "1",
    reason="pinned M2 Metabase lab required",
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


def test_all_eight_family_plans_construct_and_execute_on_pinned_runtime():
    cases = build_cases()
    snapshot = build_snapshot()
    report = MetabaseBridgePreflightCompiler.audit(
        cases=cases,
        snapshot=snapshot,
    )
    assert report.result == P3AResult.PASS_B_SEAM

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

    executed_steps = 0
    with MetabaseAgentClient(
        base_url=base_url,
        session_token=_login(base_url),
        policy=policy,
    ) as client:
        for family, intent in cases:
            plan = MetabaseBridgePreflightCompiler.compile(
                family=family,
                intent=intent,
                snapshot=snapshot,
            )
            for step in plan.query_steps:
                stage = step.query["stages"][0]
                assert "joins" not in stage
                constructed = client.construct_query(step.query)
                result = client.execute_serialized(constructed)
                assert result.status.value == "completed"
                executed_steps += 1

    assert executed_steps == 9
