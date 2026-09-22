from __future__ import annotations

import copy
import hashlib
import json
import os

import httpx
import pytest

from app.v3.security_identity import (
    ExecutionAccessSnapshotIssuer,
    VerifiedExecutionSecurityFacts,
)
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.errors import (
    MetabaseClientError,
    MetabaseErrorCode,
)
from app.v3.substrate.metabase.models import MetabaseRuntimePolicy
from app.v3.substrate.metabase.p3a_fixture import build_cases, build_snapshot
from control_plane.authorize import Principal


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_METABASE_P10B1_LIVE") != "1",
    reason="isolated pinned Metabase P10B1 lab required",
)


WAREHOUSE_NAME = "Dima Analytics Lab"
RUNTIME_IMAGE = (
    "sha256:1160b570cb11c107bce00e71293552df"
    "8a8363e01a32c2c7a048cee002dc8a73"
)


def _login(base_url: str, *, email: str, password: str) -> str:
    response = httpx.post(
        base_url + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("id")
    assert isinstance(token, str) and token
    return token


def _policy() -> MetabaseRuntimePolicy:
    return MetabaseRuntimePolicy(
        runtime_version="v0.63.18",
        runtime_image_digest=RUNTIME_IMAGE,
        raw_sql_policy="disabled",
        observed_page_size=200,
        observed_total_row_cap=2000,
    )


def _items(body):
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ("data", "items"):
            value = body.get(key)
            if isinstance(value, list):
                return value
    raise AssertionError(f"unexpected list payload: {type(body).__name__}")


def _canonical_digest(value) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _map_key(mapping: dict, numeric_id: int) -> str | int:
    if str(numeric_id) in mapping:
        return str(numeric_id)
    if numeric_id in mapping:
        return numeric_id
    raise AssertionError(f"missing exact numeric key {numeric_id}")


def _group_db_entry(
    graph: dict,
    *,
    group_id: int,
    database_id: int,
) -> dict:
    groups = graph.get("groups")
    assert isinstance(groups, dict)
    group_key = _map_key(groups, group_id)
    dbs = groups[group_key]
    assert isinstance(dbs, dict)
    db_key = _map_key(dbs, database_id)
    entry = dbs[db_key]
    assert isinstance(entry, dict)
    return entry


def _set_create_queries(
    graph: dict,
    *,
    group_id: int,
    database_id: int,
    value: str,
) -> None:
    entry = _group_db_entry(
        graph,
        group_id=group_id,
        database_id=database_id,
    )
    entry["create-queries"] = value


def _current_user(client: httpx.Client) -> dict:
    response = client.get("/api/user/current")
    response.raise_for_status()
    body = response.json()
    assert isinstance(body, dict)
    assert isinstance(body.get("id"), int)
    return body


def _permission_graph(client: httpx.Client) -> dict:
    response = client.get("/api/permissions/graph")
    response.raise_for_status()
    body = response.json()
    assert isinstance(body, dict)
    assert isinstance(body.get("revision"), int)
    assert isinstance(body.get("groups"), dict)
    return body


def _restore_graph(
    client: httpx.Client,
    original: dict,
) -> dict:
    current = _permission_graph(client)
    restored = copy.deepcopy(original)
    restored["revision"] = current["revision"]
    response = client.put("/api/permissions/graph", json=restored)
    response.raise_for_status()
    body = response.json()
    assert isinstance(body, dict)
    return _permission_graph(client)


def test_p10b1_same_session_permission_revocation_and_restore():
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    admin_token = _login(
        base_url,
        email=os.environ["MB_ADMIN_EMAIL"],
        password=os.environ["MB_ADMIN_PASSWORD"],
    )
    restricted_token = _login(
        base_url,
        email=os.environ["MB_RESTRICTED_EMAIL"],
        password=os.environ["MB_RESTRICTED_PASSWORD"],
    )
    headers_admin = {
        "Accept": "application/json",
        "X-Metabase-Session": admin_token,
    }
    headers_restricted = {
        "Accept": "application/json",
        "X-Metabase-Session": restricted_token,
    }

    snapshot = build_snapshot()
    _, intent = build_cases()[0]
    original_graph: dict | None = None
    restored_graph: dict | None = None

    with httpx.Client(
        base_url=base_url,
        headers=headers_admin,
        timeout=30,
    ) as admin_http, httpx.Client(
        base_url=base_url,
        headers=headers_restricted,
        timeout=30,
    ) as restricted_http, MetabaseAgentClient(
        base_url=base_url,
        session_token=restricted_token,
        policy=_policy(),
    ) as restricted_agent:
        restricted_user = _current_user(restricted_http)
        restricted_user_id = int(restricted_user["id"])
        assert restricted_user.get("email") == os.environ["MB_RESTRICTED_EMAIL"]
        assert restricted_user.get("is_superuser") is False

        groups_response = admin_http.get("/api/permissions/group")
        groups_response.raise_for_status()
        groups = _items(groups_response.json())

        all_users = [
            item
            for item in groups
            if item.get("magic_group_type") == "all-internal-users"
        ]
        restricted_groups = [
            item
            for item in groups
            if item.get("name") == os.environ["MB_RESTRICTED_GROUP"]
        ]
        assert len(all_users) == 1
        assert len(restricted_groups) == 1
        all_users_id = int(all_users[0]["id"])
        restricted_group_id = int(restricted_groups[0]["id"])

        current_group_ids = {
            int(value)
            for value in (restricted_user.get("group_ids") or [])
        }
        assert all_users_id in current_group_ids
        assert restricted_group_id in current_group_ids

        db_response = admin_http.get("/api/database")
        db_response.raise_for_status()
        databases = [
            item
            for item in _items(db_response.json())
            if item.get("name") == WAREHOUSE_NAME
        ]
        assert len(databases) == 1
        database_id = int(databases[0]["id"])

        plan = MetabaseProjectionCompiler.compile(
            intent=intent,
            snapshot=snapshot,
        )
        canonical = MetabaseCanonicalizer(
            client=restricted_agent
        ).canonicalize(plan)
        assert len(canonical.steps) == 1
        query = canonical.steps[0]

        before = restricted_agent.execute_serialized(
            query.model_copy(
                include={"serialized_query"}
            )
            if False
            else __import__(
                "app.v3.substrate.metabase.models",
                fromlist=["ConstructedQuery"],
            ).ConstructedQuery(
                serialized_query=query.serialized_query,
            )
        )
        assert before.status.value == "completed"

        original_graph = _permission_graph(admin_http)
        revoked = copy.deepcopy(original_graph)
        for group_id in (all_users_id, restricted_group_id):
            _set_create_queries(
                revoked,
                group_id=group_id,
                database_id=database_id,
                value="no",
            )

        revoke_response = admin_http.put(
            "/api/permissions/graph",
            json=revoked,
        )
        revoke_response.raise_for_status()

        same_user_after_revoke = _current_user(restricted_http)
        assert int(same_user_after_revoke["id"]) == restricted_user_id
        assert same_user_after_revoke.get("is_superuser") is False

        from app.v3.substrate.metabase.models import ConstructedQuery

        same_query = ConstructedQuery(
            serialized_query=query.serialized_query,
        )
        with pytest.raises(MetabaseClientError) as exc:
            restricted_agent.execute_serialized(same_query)
        assert exc.value.code == MetabaseErrorCode.PERMISSION
        assert exc.value.status_code == 403

        restored_graph = _restore_graph(
            admin_http,
            original_graph,
        )

        same_user_after_restore = _current_user(restricted_http)
        assert int(same_user_after_restore["id"]) == restricted_user_id
        restored_execution = restricted_agent.execute_serialized(
            same_query
        )
        assert restored_execution.status.value == "completed"

        relevant_permissions = {
            str(group_id): _group_db_entry(
                restored_graph,
                group_id=group_id,
                database_id=database_id,
            )
            for group_id in (all_users_id, restricted_group_id)
        }
        policy_digest = _canonical_digest(
            {
                "revision": restored_graph["revision"],
                "database_id": database_id,
                "permissions": relevant_permissions,
            }
        )
        security_digest = _canonical_digest(
            {
                "metabase_user_id": restricted_user_id,
                "group_ids": sorted(current_group_ids),
                "database_id": database_id,
                "permissions": relevant_permissions,
            }
        )

        current_principal = Principal(
            user_id=intent.principal.principal_subject,
            tenant_id=intent.principal.tenant_binding,
            roles=list(intent.principal.roles),
            tenant_slug=intent.principal.tenant_binding,
        )
        facts = VerifiedExecutionSecurityFacts(
            tenant_binding=intent.principal.tenant_binding,
            principal_subject=intent.principal.principal_subject,
            roles=intent.principal.roles,
            attribute_policy_digest=policy_digest,
            policy_version=(
                f"metabase-permissions-revision:{restored_graph['revision']}"
            ),
            rls_versions=(),
            cls_versions=(),
            database_route=f"metabase:database:{database_id}",
            database_destination=f"metabase:database:{database_id}",
            impersonation_role=None,
            semantic_context_version=intent.semantic_context_version,
            source_object_refs=canonical.manifest.resource_entity_ids,
            security_parameter_digest=security_digest,
            metabase_subject_ref=f"metabase:user:{restricted_user_id}",
            attestation_refs=(
                f"metabase:permissions:revision:{restored_graph['revision']}",
            ),
            evidence_refs=(
                f"metabase:user:{restricted_user_id}",
                f"metabase:database:{database_id}",
            ),
        )
        access = ExecutionAccessSnapshotIssuer.issue(
            current_principal=current_principal,
            accepted_intent=intent,
            canonical_projection=canonical,
            verified_security_facts=facts,
        )
        assert access.tenant_binding == intent.principal.tenant_binding
        assert (
            f"metabase:user:{restricted_user_id}"
            in access.attestation_refs
        )

    if original_graph is not None and restored_graph is None:
        # Defensive recovery if a failure happened after revocation but before normal restore.
        with httpx.Client(
            base_url=base_url,
            headers=headers_admin,
            timeout=30,
        ) as recovery:
            _restore_graph(recovery, original_graph)
