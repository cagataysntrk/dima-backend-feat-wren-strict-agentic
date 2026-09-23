from __future__ import annotations

import base64
import json

from app.v3.resource_provisioning import (
    ProvisionActionKind,
    ResourceInventorySnapshot,
    SemanticResourceProvisionPlanner,
)
from app.v3.resource_transport import MetricCreateContractBuilder, MetricCreateTarget
from app.v3.semantic_equivalence import SemanticEquivalenceMatrixBuilder
from app.v3.semantic_import import SemanticImportResult
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import ConstructedQuery
from lab.metabase.p13b.px01_live_standard import (
    CONTEXT_VERSION,
    TABLE,
    TENANT,
    WAREHOUSE_NAME,
    binding_snapshot,
    h,
    metric_definition_intent,
)


class DeterministicClient:
    def construct_query(self, portable_query):
        raw = json.dumps(
            portable_query,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return ConstructedQuery(
            serialized_query=base64.b64encode(raw).decode("ascii")
        )


def _proof():
    snapshot = binding_snapshot(1, 57, 521, "public")
    imported = SemanticImportResult(
        source_fingerprint=h(
            {"semantic_spec": snapshot.semantic_spec.model_dump(mode="json")}
        ),
        spec=snapshot.semantic_spec,
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(imported)
    provision = SemanticResourceProvisionPlanner.plan(
        tenant_binding=TENANT,
        import_result=imported,
        matrix=matrix,
        inventory=ResourceInventorySnapshot(),
    )
    actions = [
        action
        for action in provision.actions
        if action.canonical_id == "metric.sales_order_count"
    ]
    assert len(actions) == 1
    action = actions[0]
    assert action.action == ProvisionActionKind.CREATE

    projection_plan = MetabaseProjectionCompiler.compile(
        intent=metric_definition_intent(),
        snapshot=snapshot,
    )
    projection = MetabaseCanonicalizer(
        client=DeterministicClient()
    ).canonicalize(projection_plan)
    desired = action.desired
    assert desired is not None
    contract = MetricCreateContractBuilder.build(
        action=action,
        projection=projection,
        target=MetricCreateTarget(
            tenant_binding=TENANT,
            collection_id=17,
        ),
    )
    return snapshot, desired, projection, contract


def test_px01_metric_is_one_dima_managed_p9_resource():
    snapshot, desired, _, _ = _proof()
    metric = snapshot.semantic_spec.metrics[0]
    assert metric.metric_id == "metric.sales_order_count"
    assert metric.name == "Sales Order Count"
    assert metric.aggregation == "count"
    assert metric.formula is None
    assert metric.source_lineage[0].table_name == TABLE
    assert metric.source_lineage[0].database_ref == WAREHOUSE_NAME

    policies = snapshot.semantic_spec.managed_resources
    assert len(policies) == 1
    assert policies[0].semantic_ref == metric.metric_id
    assert policies[0].ownership == "DIMA_MANAGED"
    assert desired.canonical_id == metric.metric_id
    assert desired.semantic_context_version == CONTEXT_VERSION
    assert desired.payload["semantic"]["aggregation"] == "count"


def test_px01_metric_definition_uses_existing_p4_and_p9b_without_semantic_duplicate():
    _, desired, projection, contract = _proof()
    stage = projection.steps[0].decoded_query["stages"][0]

    assert projection.manifest.semantic_ids == ("metric.sales_order_count",)
    assert stage["source-table"] == [WAREHOUSE_NAME, "public", TABLE]
    assert stage["aggregation"] == [["count", {}]]
    assert "filters" not in stage
    assert "breakout" not in stage
    assert "order-by" not in stage
    assert "limit" not in stage

    assert contract.canonical_id == desired.canonical_id
    assert contract.semantic_context_version == desired.semantic_context_version
    assert contract.request.name == "Sales Order Count"
    assert contract.request.query == projection.steps[0].serialized_query
    assert contract.canonical_query_fingerprint == (
        projection.steps[0].canonical_query_fingerprint
    )
