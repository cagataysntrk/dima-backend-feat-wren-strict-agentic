from __future__ import annotations

import os

import httpx
import pytest

from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import (
    ConstructedQuery,
    MetabaseRuntimePolicy,
)
from app.v3.substrate.metabase.p3a_fixture import build_cases, build_snapshot


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_METABASE_P4_LIVE") != "1",
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


def test_p4_all_eight_families_canonicalize_deterministically_and_execute():
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
    snapshot = build_snapshot()
    executed = 0
    observed_runtime_uuids = 0

    with MetabaseAgentClient(
        base_url=base_url,
        session_token=_login(base_url),
        policy=policy,
    ) as client:
        canonicalizer = MetabaseCanonicalizer(client=client)
        for _, intent in build_cases():
            plan = MetabaseProjectionCompiler.compile(
                intent=intent,
                snapshot=snapshot,
            )
            canonical = canonicalizer.canonicalize(plan)
            repeated = canonicalizer.canonicalize(plan)

            assert canonical.projection_hash == intent.projection_hash
            assert canonical.resolved_intent_hash == intent.resolved_intent_hash
            assert canonical.manifest.query_count == len(canonical.steps)
            assert (
                canonical.canonical_query_fingerprint
                == repeated.canonical_query_fingerprint
            )
            assert [
                item.canonical_query_fingerprint for item in canonical.steps
            ] == [
                item.canonical_query_fingerprint for item in repeated.steps
            ]
            assert all(
                item.manifest.explicit_join_count == 0
                and item.manifest.implicit_join_reference_count == 0
                for item in canonical.steps
            )
            observed_runtime_uuids += sum(
                item.volatile_lib_uuid_count for item in canonical.steps
            )

            for item in canonical.steps:
                result = client.execute_serialized(
                    ConstructedQuery(serialized_query=item.serialized_query)
                )
                assert result.status.value == "completed"
                executed += 1

    assert executed == 9
    assert observed_runtime_uuids > 0
