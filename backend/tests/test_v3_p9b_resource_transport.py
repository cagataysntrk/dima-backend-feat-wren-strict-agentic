from __future__ import annotations

import ast
import base64
import copy
import inspect
import json

import pytest
from pydantic import ValidationError

from app.v3 import resource_transport as transport_module
from app.v3.resource_provisioning import (
    ProvisionActionKind,
    ResourceInventorySnapshot,
    SemanticResourceProvisionPlanner,
)
from app.v3.resource_transport import (
    MetricCreateContractBuilder,
    MetricCreateTarget,
    ResourceTransportError,
)
from app.v3.semantic_equivalence import SemanticEquivalenceMatrixBuilder
from app.v3.semantic_import import SemanticImportResult
from app.v3.semantic_spec import ManagedResourcePolicy
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import ConstructedQuery
from app.v3.substrate.metabase.p3a_fixture import (
    build_cases,
    build_snapshot,
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


def _fixture(case_index=0):
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
        source_fingerprint="c" * 64,
        spec=spec,
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(imported)
    p9 = SemanticResourceProvisionPlanner.plan(
        tenant_binding="tenant-p9b",
        import_result=imported,
        matrix=matrix,
        inventory=ResourceInventorySnapshot(),
    )
    action = p9.actions[0]
    assert action.action == ProvisionActionKind.CREATE

    _, intent = build_cases()[case_index]
    plan = MetabaseProjectionCompiler.compile(
        intent=intent,
        snapshot=snapshot,
    )
    projection = MetabaseCanonicalizer(
        client=DeterministicClient()
    ).canonicalize(plan)
    return action, projection


def test_p9b1_builds_exact_agent_metric_create_request_from_certified_query():
    action, projection = _fixture()
    contract = MetricCreateContractBuilder.build(
        action=action,
        projection=projection,
        target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
    )

    assert contract.tenant_binding == "tenant-p9b"
    assert contract.canonical_id == "metric.revenue"
    assert contract.collection_id == 17
    assert contract.projection_hash == projection.projection_hash
    assert contract.resolved_intent_hash == projection.resolved_intent_hash
    assert (
        contract.current_catalog_fingerprint
        == projection.current_catalog_fingerprint
    )
    assert contract.request.model_dump(mode="json") == {
        "name": "Revenue",
        "query": projection.steps[0].serialized_query,
        "display": "scalar",
        "collection_id": 17,
        "visualization_settings": {},
    }
    assert (
        contract.canonical_query_fingerprint
        == projection.steps[0].canonical_query_fingerprint
    )
    assert len(contract.contract_fingerprint) == 64


def test_p9b1_contract_is_deterministic():
    action, projection = _fixture()
    first = MetricCreateContractBuilder.build(
        action=action,
        projection=projection,
        target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
    )
    second = MetricCreateContractBuilder.build(
        action=action,
        projection=copy.deepcopy(projection),
        target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
    )
    assert first == second


@pytest.mark.parametrize("collection_id", [0, -1])
def test_p9b1_requires_explicit_positive_collection_id(collection_id):
    with pytest.raises(ValidationError):
        MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=collection_id)


def test_p9b1_rejects_projection_semantic_identity_mismatch():
    action, projection = _fixture()
    broken = projection.model_copy(
        update={
            "manifest": projection.manifest.model_copy(
                update={"semantic_ids": ("metric.other",)}
            )
        }
    )
    with pytest.raises(ResourceTransportError) as exc:
        MetricCreateContractBuilder.build(
            action=action,
            projection=broken,
            target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
        )
    assert exc.value.code == "P9B1_PROJECTION_SEMANTIC_ID_MISMATCH"


def test_p9b1_rejects_projection_context_mismatch():
    action, projection = _fixture()
    broken = projection.model_copy(
        update={"semantic_context_version": "other-context"}
    )
    with pytest.raises(ResourceTransportError) as exc:
        MetricCreateContractBuilder.build(
            action=action,
            projection=broken,
            target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
        )
    assert exc.value.code == "P9B1_PROJECTION_CONTEXT_MISMATCH"


def test_p9b1_rejects_comparison_multi_step_projection():
    action, projection = _fixture(case_index=4)
    with pytest.raises(ResourceTransportError) as exc:
        MetricCreateContractBuilder.build(
            action=action,
            projection=projection,
            target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
        )
    assert exc.value.code == "P9B1_QUERY_CARDINALITY"


@pytest.mark.parametrize("case_index", [1, 2, 3, 5])
def test_p9b1_initial_slice_rejects_non_metric_definition_clauses(case_index):
    action, projection = _fixture(case_index=case_index)
    with pytest.raises(ResourceTransportError) as exc:
        MetricCreateContractBuilder.build(
            action=action,
            projection=projection,
            target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
        )
    assert exc.value.code == "P9B1_QUERY_SHAPE_UNSUPPORTED"


def test_p9b1_rejects_non_native_or_formula_payload_without_parsing_formula():
    action, projection = _fixture()
    desired = action.desired
    assert desired is not None

    for updates, expected in (
        ({"classification": "WREN_ONLY_GAP"}, "P9B1_CLASSIFICATION_UNSUPPORTED"),
        (
            {
                "semantic": {
                    **desired.payload["semantic"],
                    "formula": "SUM(amount)",
                }
            },
            "P9B1_FORMULA_METRIC_UNSUPPORTED",
        ),
    ):
        payload = {**desired.payload, **updates}
        # DesiredResource validates payload fingerprint only; preserve all other P9 identity.
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        changed = desired.model_copy(
            update={
                "payload": payload,
                "desired_fingerprint": __import__("hashlib").sha256(
                    raw.encode("utf-8")
                ).hexdigest(),
            }
        )
        broken = action.model_copy(update={"desired": changed})
        with pytest.raises(ResourceTransportError) as exc:
            MetricCreateContractBuilder.build(
                action=broken,
                projection=projection,
                target=MetricCreateTarget(tenant_binding="tenant-p9b", collection_id=17),
            )
        assert exc.value.code == expected


def test_p9b1_transport_contract_has_no_http_search_regex_fuzzy_or_sql_builder():
    tree = ast.parse(inspect.getsource(transport_module))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    assert imported.isdisjoint(
        {
            "httpx",
            "requests",
            "re",
            "regex",
            "sqlglot",
            "difflib",
            "rapidfuzz",
            "fuzzywuzzy",
            "Levenshtein",
        }
    )
    source = inspect.getsource(transport_module).lower()
    for forbidden in (
        ".search(",
        ".read_resource(",
        "raw sql",
        "select ",
        "where ",
        "formula parser",
        "construct_query(",
    ):
        assert forbidden not in source



def test_p9b1_target_tenant_mismatch_hard_fails():
    action, projection = _fixture()
    with pytest.raises(ResourceTransportError) as exc:
        MetricCreateContractBuilder.build(
            action=action,
            projection=projection,
            target=MetricCreateTarget(
                tenant_binding="tenant-other",
                collection_id=17,
            ),
        )
    assert exc.value.code == "P9B1_TARGET_TENANT_MISMATCH"


def test_p9b1_tenant_changes_transport_contract_fingerprint():
    action, projection = _fixture()
    first = MetricCreateContractBuilder.build(
        action=action,
        projection=projection,
        target=MetricCreateTarget(
            tenant_binding="tenant-p9b",
            collection_id=17,
        ),
    )
    desired = action.desired
    assert desired is not None
    other_desired = desired.model_copy(
        update={"tenant_binding": "tenant-other"}
    )
    other_action = action.model_copy(
        update={"desired": other_desired}
    )
    second = MetricCreateContractBuilder.build(
        action=other_action,
        projection=projection,
        target=MetricCreateTarget(
            tenant_binding="tenant-other",
            collection_id=17,
        ),
    )
    assert first.contract_fingerprint != second.contract_fingerprint


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("projection_hash", "d" * 64),
        ("current_catalog_fingerprint", "e" * 64),
        ("resolved_intent_hash", "f" * 64),
    ],
)
def test_p9b1_projection_provenance_changes_contract_fingerprint(field, value):
    action, projection = _fixture()
    first = MetricCreateContractBuilder.build(
        action=action,
        projection=projection,
        target=MetricCreateTarget(
            tenant_binding="tenant-p9b",
            collection_id=17,
        ),
    )
    changed_projection = projection.model_copy(
        update={field: value}
    )
    second = MetricCreateContractBuilder.build(
        action=action,
        projection=changed_projection,
        target=MetricCreateTarget(
            tenant_binding="tenant-p9b",
            collection_id=17,
        ),
    )
    assert first.contract_fingerprint != second.contract_fingerprint
