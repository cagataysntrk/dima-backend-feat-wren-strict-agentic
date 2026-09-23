#!/usr/bin/env python3
"""Provider-free P13B semantic availability proof for the frozen PX-01 metric."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx

from app.v3.resource_provisioning import (
    ManagedResourceBinding,
    ObservedMetabaseResource,
    ProvisionActionKind,
    ResourceInventorySnapshot,
    SemanticResourceProvisionPlanner,
)
from app.v3.resource_transport import MetricCreateContractBuilder, MetricCreateTarget
from app.v3.semantic_equivalence import SemanticEquivalenceMatrixBuilder
from app.v3.semantic_import import SemanticImportResult
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import MetabaseRuntimePolicy
from lab.metabase.p13b.px01_live_standard import (
    CONTEXT_VERSION,
    TABLE,
    TENANT,
    binding_snapshot,
    discover_catalog,
    h,
    login,
    metric_definition_intent,
)


def _policy(runtime_tag: str, image_digest: str) -> MetabaseRuntimePolicy:
    return MetabaseRuntimePolicy(
        runtime_version=runtime_tag,
        runtime_image_digest=image_digest,
        raw_sql_policy="disabled",
        observed_page_size=200,
        observed_total_row_cap=2000,
    )


def _desired(snapshot):
    imported = SemanticImportResult(
        source_fingerprint=h(
            {"semantic_spec": snapshot.semantic_spec.model_dump(mode="json")}
        ),
        spec=snapshot.semantic_spec,
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(imported)
    plan = SemanticResourceProvisionPlanner.plan(
        tenant_binding=TENANT,
        import_result=imported,
        matrix=matrix,
        inventory=ResourceInventorySnapshot(),
    )
    metric_id = snapshot.semantic_spec.metrics[0].metric_id
    actions = [x for x in plan.actions if x.canonical_id == metric_id]
    if len(actions) != 1 or actions[0].action != ProvisionActionKind.CREATE:
        raise RuntimeError(
            f"expected one P9 CREATE for {metric_id}, got "
            f"{[(x.canonical_id, x.action.value) for x in actions]!r}"
        )
    desired = actions[0].desired
    if desired is None:
        raise RuntimeError("P9 CREATE has no desired resource")
    return imported, matrix, actions[0], desired


def _create_collection(raw: httpx.Client) -> int:
    response = raw.post(
        "/api/collection",
        json={
            "name": "Dima Managed Semantics " + uuid4().hex[:12],
            "description": "P13B provider-free semantic availability proof",
        },
    )
    response.raise_for_status()
    return int(response.json()["id"])


def _search_exact(
    agent: MetabaseAgentClient,
    *,
    local_id: int,
    name: str,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last: tuple[dict[str, Any], ...] = ()
    while time.monotonic() < deadline:
        response = agent.search(term_queries=(name,))
        last = response.data
        matches = [
            item
            for item in last
            if str(item.get("type") or "").lower() == "metric"
            and int(item.get("id") or -1) == local_id
        ]
        if len(matches) == 1:
            return matches[0]
        time.sleep(1)
    raise RuntimeError(
        f"restricted native search did not discover metric {local_id}; "
        f"last results={last!r}"
    )


def _resource_payload(agent: MetabaseAgentClient, local_id: int) -> tuple[dict[str, Any], str]:
    uri = f"metabase://metric/{local_id}"
    response = agent.read_resource((uri,))
    item = response.resources[0]
    if item.failed or item.content is None:
        raise RuntimeError(f"restricted read_resource failed for {uri}: {item.error!r}")
    structured = item.content.structured_output
    if not isinstance(structured, dict):
        raise RuntimeError("restricted metric read_resource has no structured output")
    return structured, response.output


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--admin-email", required=True)
    ap.add_argument("--admin-password", required=True)
    ap.add_argument("--restricted-email", required=True)
    ap.add_argument("--restricted-password", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--runtime-image-digest", required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--platform-sha", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    admin_token = login(args.base_url, args.admin_email, args.admin_password)
    restricted_token = login(
        args.base_url, args.restricted_email, args.restricted_password
    )
    database_id, table_id, field_id, schema_name, restricted_user_id = discover_catalog(
        args.base_url, restricted_token
    )
    snapshot = binding_snapshot(database_id, table_id, field_id, schema_name)
    metric = snapshot.semantic_spec.metrics[0]
    imported, matrix, action, desired = _desired(snapshot)

    admin_headers = {
        "Accept": "application/json",
        "X-Metabase-Session": admin_token,
    }
    restricted_headers = {
        "Accept": "application/json",
        "X-Metabase-Session": restricted_token,
    }
    policy = _policy(args.runtime_tag, args.runtime_image_digest)

    with (
        httpx.Client(
            base_url=args.base_url.rstrip("/"),
            headers=admin_headers,
            timeout=30,
        ) as admin_raw,
        httpx.Client(
            base_url=args.base_url.rstrip("/"),
            headers=restricted_headers,
            timeout=30,
        ) as restricted_raw,
        MetabaseAgentClient(
            base_url=args.base_url,
            session_token=admin_token,
            policy=policy,
        ) as admin_agent,
        MetabaseAgentClient(
            base_url=args.base_url,
            session_token=restricted_token,
            policy=policy,
        ) as restricted_agent,
    ):
        collection_id = _create_collection(admin_raw)

        plan = MetabaseProjectionCompiler.compile(
            intent=metric_definition_intent(),
            snapshot=snapshot,
        )
        projection = MetabaseCanonicalizer(client=admin_agent).canonicalize(plan)
        contract = MetricCreateContractBuilder.build(
            action=action,
            projection=projection,
            target=MetricCreateTarget(
                tenant_binding=TENANT,
                collection_id=collection_id,
            ),
        )
        create = admin_raw.post(
            "/api/agent/v1/metric",
            json=contract.request.model_dump(mode="json"),
        )
        create.raise_for_status()
        created = create.json()
        metric_local_id = int(created["id"])

        admin_card_response = admin_raw.get(f"/api/card/{metric_local_id}")
        admin_card_response.raise_for_status()
        admin_card = admin_card_response.json()
        entity_id = str(admin_card.get("entity_id") or "")
        if not entity_id:
            raise RuntimeError("created Dima-managed metric has no portable entity id")

        binding = ManagedResourceBinding(
            tenant_binding=desired.tenant_binding,
            canonical_id=desired.canonical_id,
            resource_kind=desired.resource_kind,
            semantic_context_version=desired.semantic_context_version,
            metabase_entity_id=entity_id,
            metabase_local_id=metric_local_id,
            applied_version=desired.desired_version,
            applied_fingerprint=desired.desired_fingerprint,
            ownership="DIMA_MANAGED",
        )
        observed = ObservedMetabaseResource.from_payload(
            tenant_binding=desired.tenant_binding,
            resource_kind=desired.resource_kind,
            metabase_entity_id=entity_id,
            metabase_local_id=metric_local_id,
            display_name=str(admin_card["name"]),
            managed_payload=desired.payload,
        )
        inventory = ResourceInventorySnapshot(
            bindings=(binding,),
            resources=(observed,),
        )
        replanned = SemanticResourceProvisionPlanner.plan(
            tenant_binding=TENANT,
            import_result=imported,
            matrix=matrix,
            inventory=inventory,
        )
        if (
            len(replanned.actions) != 1
            or replanned.actions[0].action != ProvisionActionKind.NOOP
        ):
            raise RuntimeError(
                "P9 reconciliation did not recognize exact created metric binding"
            )

        search_hit = _search_exact(
            restricted_agent,
            local_id=metric_local_id,
            name=metric.name,
        )
        search_entity_id = str(search_hit.get("portable_entity_id") or "")
        if search_entity_id != entity_id:
            raise RuntimeError(
                "restricted search metric portable entity id differs from P9 binding"
            )

        resource, formatted = _resource_payload(restricted_agent, metric_local_id)
        resource_id = int(resource.get("id") or -1)
        resource_entity_id = str(resource.get("portable_entity_id") or "")
        if resource_id != metric_local_id or resource_entity_id != entity_id:
            raise RuntimeError(
                "restricted read_resource metric identity differs from P9 binding"
            )
        if str(resource.get("base_table_name") or "") != TABLE:
            raise RuntimeError("restricted read_resource metric base table mismatch")

        restricted_card_response = restricted_raw.get(f"/api/card/{metric_local_id}")
        restricted_card_response.raise_for_status()
        restricted_card = restricted_card_response.json()
        persisted_definition = restricted_card.get("dataset_query")
        if not isinstance(persisted_definition, dict):
            raise RuntimeError("restricted principal cannot read persisted metric definition")

        definition_keys = (
            "definition",
            "query",
            "query_json",
            "dataset_query",
            "dataset-query",
        )
        read_resource_definition = next(
            (resource[key] for key in definition_keys if resource.get(key) is not None),
            None,
        )
        definition_exposed = read_resource_definition is not None

        report = {
            "schema_version": "p13b_px01_semantic_availability_v1",
            "status": "GREEN" if definition_exposed else "RED",
            "platform_sha": args.platform_sha,
            "engine_sha": args.engine_sha,
            "runtime_tag": args.runtime_tag,
            "model_calls": 0,
            "canonical_metric": {
                "id": metric.metric_id,
                "name": metric.name,
                "aggregation": metric.aggregation,
                "formula": metric.formula,
                "semantic_version": metric.semantic_version,
                "semantic_context_version": CONTEXT_VERSION,
                "base_table": TABLE,
            },
            "p9": {
                "reused": True,
                "ownership": desired.ownership,
                "desired_version": desired.desired_version,
                "desired_fingerprint": desired.desired_fingerprint,
                "reconcile_after_create": replanned.actions[0].action.value,
            },
            "p9b": {
                "reused": True,
                "contract_fingerprint": contract.contract_fingerprint,
                "canonical_query_fingerprint": contract.canonical_query_fingerprint,
                "definition_query": projection.steps[0].decoded_query,
            },
            "binding": binding.model_dump(mode="json"),
            "restricted_principal": {
                "metabase_user_id": restricted_user_id,
                "search_discovered": True,
                "search_hit": search_hit,
                "read_resource_readable": True,
                "read_resource": resource,
                "read_resource_formatted": formatted,
                "read_resource_definition_exposed": definition_exposed,
                "persisted_card_readable": True,
                "persisted_card_dataset_query": persisted_definition,
            },
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))

        if not definition_exposed:
            raise RuntimeError(
                "P13B_SEMANTIC_RESOURCE_DEFINITION_NOT_EXPOSED: "
                "restricted read_resource exposes metric identity/base table but not definition"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
