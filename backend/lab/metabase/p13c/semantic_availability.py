#!/usr/bin/env python3
"""Provider-free P13C semantic availability proof under the new semantic context."""
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

from lab.metabase.p13c.common import (
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
        raise RuntimeError("expected exactly one P9 metric CREATE")
    desired = actions[0].desired
    if desired is None:
        raise RuntimeError("P9 CREATE has no desired resource")
    return imported, matrix, actions[0], desired


def _search_exact(agent: MetabaseAgentClient, *, local_id: int, name: str) -> dict[str, Any]:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        response = agent.search(term_queries=(name,))
        matches = [
            item for item in response.data
            if str(item.get("type") or "").lower() == "metric"
            and int(item.get("id") or -1) == local_id
        ]
        if len(matches) == 1:
            return matches[0]
        time.sleep(1)
    raise RuntimeError("restricted native search did not discover P13C metric")


def _resource_payload(agent: MetabaseAgentClient, local_id: int) -> dict[str, Any]:
    item = agent.read_resource((f"metabase://metric/{local_id}",)).resources[0]
    if item.failed or item.content is None:
        raise RuntimeError("restricted read_resource failed")
    structured = item.content.structured_output
    if not isinstance(structured, dict):
        raise RuntimeError("restricted metric read_resource lacks structured output")
    return structured


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
    restricted_token = login(args.base_url, args.restricted_email, args.restricted_password)
    database_id, table_id, time_field_id, filter_field_id, schema_name, _ = discover_catalog(
        args.base_url, restricted_token
    )
    snapshot = binding_snapshot(
        database_id, table_id, time_field_id, filter_field_id, schema_name
    )
    metric = snapshot.semantic_spec.metrics[0]
    imported, matrix, action, desired = _desired(snapshot)
    policy = _policy(args.runtime_tag, args.runtime_image_digest)

    with (
        httpx.Client(
            base_url=args.base_url.rstrip("/"),
            headers={"X-Metabase-Session": admin_token, "Accept": "application/json"},
            timeout=30,
        ) as admin_raw,
        httpx.Client(
            base_url=args.base_url.rstrip("/"),
            headers={"X-Metabase-Session": restricted_token, "Accept": "application/json"},
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
        collection = admin_raw.post(
            "/api/collection",
            json={
                "name": "Dima P13C Managed Semantics " + uuid4().hex[:12],
                "description": "P13C provider-free metric availability",
            },
        )
        collection.raise_for_status()
        collection_id = int(collection.json()["id"])

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
        metric_local_id = int(create.json()["id"])

        admin_card = admin_raw.get(f"/api/card/{metric_local_id}")
        admin_card.raise_for_status()
        admin_body = admin_card.json()
        entity_id = str(admin_body.get("entity_id") or "")
        if not entity_id:
            raise RuntimeError("P13C managed metric has no portable entity id")

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
            display_name=str(admin_body["name"]),
            managed_payload=desired.payload,
        )
        replanned = SemanticResourceProvisionPlanner.plan(
            tenant_binding=TENANT,
            import_result=imported,
            matrix=matrix,
            inventory=ResourceInventorySnapshot(
                bindings=(binding,),
                resources=(observed,),
            ),
        )
        if len(replanned.actions) != 1 or replanned.actions[0].action != ProvisionActionKind.NOOP:
            raise RuntimeError("P13C P9 reconciliation is not NOOP after exact create")

        search = _search_exact(
            restricted_agent,
            local_id=metric_local_id,
            name=metric.name,
        )
        if str(search.get("portable_entity_id") or "") != entity_id:
            raise RuntimeError("restricted metric search identity mismatch")
        resource = _resource_payload(restricted_agent, metric_local_id)
        if (
            int(resource.get("id") or -1) != metric_local_id
            or str(resource.get("portable_entity_id") or "") != entity_id
            or str(resource.get("base_table_name") or "") != TABLE
        ):
            raise RuntimeError("restricted metric resource identity mismatch")

        restricted_card = restricted_raw.get(f"/api/card/{metric_local_id}")
        restricted_card.raise_for_status()
        persisted = restricted_card.json().get("dataset_query")
        if not isinstance(persisted, dict):
            raise RuntimeError("restricted principal cannot read persisted metric definition")
        persisted_stable, _ = MetabaseCanonicalizer._strip_runtime_volatility(persisted)
        if persisted_stable != projection.steps[0].decoded_query:
            raise RuntimeError("P13C native metric persisted definition mismatch")

        report = {
            "schema_version": "p13c_semantic_availability_v1",
            "status": "GREEN",
            "platform_sha": args.platform_sha,
            "engine_sha": args.engine_sha,
            "runtime_tag": args.runtime_tag,
            "model_calls": 0,
            "canonical_metric": {
                "id": metric.metric_id,
                "name": metric.name,
                "aggregation": metric.aggregation,
                "semantic_context_version": CONTEXT_VERSION,
                "base_table": TABLE,
            },
            "binding": binding.model_dump(mode="json"),
            "native_metric_resource": {
                "metabase_local_id": metric_local_id,
                "portable_entity_id": entity_id,
            },
            "p9_reconcile": replanned.actions[0].action.value,
            "definition_query": projection.steps[0].decoded_query,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
