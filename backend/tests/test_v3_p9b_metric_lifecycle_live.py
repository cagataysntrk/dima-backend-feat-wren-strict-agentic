from __future__ import annotations

import os
import uuid

import httpx
import pytest

from app.v3.resource_provisioning import (
    ManagedResourceBinding,
    ObservedMetabaseResource,
    ProvisionActionKind,
    ResourceInventorySnapshot,
    SemanticResourceProvisionPlanner,
)
from app.v3.resource_transport import (
    MetricCreateContractBuilder,
    MetricCreateTarget,
)
from app.v3.semantic_equivalence import SemanticEquivalenceMatrixBuilder
from app.v3.semantic_import import SemanticImportResult
from app.v3.semantic_spec import ManagedResourcePolicy
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import MetabaseRuntimePolicy
from app.v3.substrate.metabase.p3a_fixture import (
    build_cases,
    build_snapshot,
)


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_METABASE_P9B_LIVE") != "1",
    reason="isolated pinned Metabase P9B lifecycle lab required",
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
    assert isinstance(token, str) and token
    return token


def _policy() -> MetabaseRuntimePolicy:
    return MetabaseRuntimePolicy(
        runtime_version="v0.63.18",
        runtime_image_digest=(
            "sha256:1160b570cb11c107bce00e71293552df"
            "8a8363e01a32c2c7a048cee002dc8a73"
        ),
        raw_sql_policy="disabled",
        observed_page_size=200,
        observed_total_row_cap=2000,
    )


def _p9_create_action():
    snapshot = build_snapshot()
    metric_id = snapshot.semantic_spec.metrics[0].metric_id
    policy = ManagedResourcePolicy(
        semantic_ref=metric_id,
        ownership="DIMA_MANAGED",
        reconciliation="OVERWRITE",
    )
    spec = snapshot.semantic_spec.model_copy(
        update={"managed_resources": (policy,)}
    )
    imported = SemanticImportResult(
        source_fingerprint="9" * 64,
        spec=spec,
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(imported)
    plan = SemanticResourceProvisionPlanner.plan(
        tenant_binding="tenant-p9b-live",
        import_result=imported,
        matrix=matrix,
        inventory=ResourceInventorySnapshot(),
    )
    assert len(plan.actions) == 1
    assert plan.actions[0].action == ProvisionActionKind.CREATE
    return snapshot, imported, matrix, plan.actions[0]


def _fresh_projection(client: MetabaseAgentClient, snapshot):
    _, intent = build_cases()[0]
    plan = MetabaseProjectionCompiler.compile(
        intent=intent,
        snapshot=snapshot,
    )
    return MetabaseCanonicalizer(client=client).canonicalize(plan)


def _assert_exact_card(
    card: dict,
    *,
    card_id: int,
    expected_name: str,
    collection_id: int,
    archived: bool,
) -> str:
    assert int(card["id"]) == card_id
    assert card["type"] == "metric"
    assert card["name"] == expected_name
    assert int(card["collection_id"]) == collection_id
    assert bool(card["archived"]) is archived
    entity_id = card.get("entity_id")
    assert isinstance(entity_id, str) and entity_id.strip()
    return entity_id


def test_p9b_single_pinned_metric_lifecycle_canary():
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    token = _login(base_url)
    headers = {
        "Accept": "application/json",
        "X-Metabase-Session": token,
    }
    snapshot, imported, matrix, action = _p9_create_action()
    desired = action.desired
    assert desired is not None

    collection_id: int | None = None
    metric_id: int | None = None

    with httpx.Client(
        base_url=base_url,
        headers=headers,
        timeout=30,
    ) as raw, MetabaseAgentClient(
        base_url=base_url,
        session_token=token,
        policy=_policy(),
    ) as agent:
        try:
            collection_response = raw.post(
                "/api/collection",
                json={
                    "name": (
                        "Dima P9B Lifecycle "
                        + uuid.uuid4().hex[:12]
                    ),
                    "description": "isolated P9B lifecycle canary",
                },
            )
            collection_response.raise_for_status()
            collection = collection_response.json()
            collection_id = int(collection["id"])

            projection = _fresh_projection(agent, snapshot)
            contract = MetricCreateContractBuilder.build(
                action=action,
                projection=projection,
                target=MetricCreateTarget(
                    tenant_binding=desired.tenant_binding,
                    collection_id=collection_id,
                ),
            )
            assert contract.tenant_binding == desired.tenant_binding
            assert contract.collection_id == collection_id

            create_response = raw.post(
                "/api/agent/v1/metric",
                json=contract.request.model_dump(mode="json"),
            )
            create_response.raise_for_status()
            created = create_response.json()
            metric_id = int(created["id"])
            assert created["name"] == contract.request.name
            assert int(created["collection_id"]) == collection_id

            read_created = raw.get(f"/api/card/{metric_id}")
            read_created.raise_for_status()
            card = read_created.json()
            entity_id = _assert_exact_card(
                card,
                card_id=metric_id,
                expected_name=contract.request.name,
                collection_id=collection_id,
                archived=False,
            )

            binding = ManagedResourceBinding(
                tenant_binding=desired.tenant_binding,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                semantic_context_version=desired.semantic_context_version,
                metabase_entity_id=entity_id,
                metabase_local_id=metric_id,
                applied_version=desired.desired_version,
                applied_fingerprint=desired.desired_fingerprint,
                ownership="DIMA_MANAGED",
            )
            observed = ObservedMetabaseResource.from_payload(
                tenant_binding=desired.tenant_binding,
                resource_kind=desired.resource_kind,
                metabase_entity_id=entity_id,
                metabase_local_id=metric_id,
                display_name=card["name"],
                managed_payload=desired.payload,
            )
            inventory = ResourceInventorySnapshot(
                bindings=(binding,),
                resources=(observed,),
            )
            replanned = SemanticResourceProvisionPlanner.plan(
                tenant_binding=desired.tenant_binding,
                import_result=imported,
                matrix=matrix,
                inventory=inventory,
            )
            assert len(replanned.actions) == 1
            assert replanned.actions[0].action == ProvisionActionKind.NOOP

            archived_response = raw.put(
                f"/api/agent/v1/metric/{metric_id}",
                json={"archived": True},
            )
            archived_response.raise_for_status()
            assert archived_response.json()["archived"] is True

            read_archived = raw.get(f"/api/card/{metric_id}")
            read_archived.raise_for_status()
            archived_card = read_archived.json()
            _assert_exact_card(
                archived_card,
                card_id=metric_id,
                expected_name=contract.request.name,
                collection_id=collection_id,
                archived=True,
            )

            restored_response = raw.put(
                f"/api/agent/v1/metric/{metric_id}",
                json={"archived": False},
            )
            restored_response.raise_for_status()
            assert restored_response.json()["archived"] is False

            read_restored = raw.get(f"/api/card/{metric_id}")
            read_restored.raise_for_status()
            restored_card = read_restored.json()
            restored_entity_id = _assert_exact_card(
                restored_card,
                card_id=metric_id,
                expected_name=contract.request.name,
                collection_id=collection_id,
                archived=False,
            )
            assert restored_entity_id == entity_id

            delete_response = raw.delete(f"/api/card/{metric_id}")
            assert delete_response.status_code == 204
            metric_id = None
        finally:
            if metric_id is not None:
                raw.delete(f"/api/card/{metric_id}")
            if collection_id is not None:
                raw.put(
                    f"/api/collection/{collection_id}",
                    json={"archived": True},
                )
