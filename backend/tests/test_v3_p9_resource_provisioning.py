from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.v3 import resource_provisioning as provisioning_module
from app.v3.resource_provisioning import (
    ManagedResourceBinding,
    ObservedMetabaseResource,
    ProvisionAction,
    ProvisionActionKind,
    ProvisionSkipReason,
    ResourceInventorySnapshot,
    ResourceKind,
    ResourceProvisioningError,
    RollbackKind,
    SemanticResourceProvisionPlanner,
)
from app.v3.semantic_equivalence import (
    EquivalenceClassification,
    SemanticEquivalenceMatrixBuilder,
)
from app.v3.semantic_import import (
    SemanticImportResult,
    WrenSemanticSpecImporter,
)
from app.v3.semantic_spec import (
    DimaSemanticSpec,
    ManagedResourcePolicy,
    MetricSpec,
    SourceLineage,
)


HEX = "a" * 64
ROOT = Path(__file__).resolve().parents[1]


def _import_result(
    *,
    ownership="DIMA_MANAGED",
    reconciliation="OVERWRITE",
    formula=None,
):
    metric = MetricSpec(
        metric_id="metric.orders.revenue",
        name="revenue",
        formula=formula,
        aggregation="sum",
        semantic_version="metric-v1",
        compatibility_hash=HEX,
        source_lineage=(
            SourceLineage(
                source_id="orders.amount",
                database_ref="analytics",
                schema_name="public",
                table_name="orders",
                column_name="amount",
            ),
        ),
    )
    spec = DimaSemanticSpec(
        semantic_context_version="ctx-p9",
        metrics=(metric,),
        managed_resources=(
            ManagedResourcePolicy(
                semantic_ref=metric.metric_id,
                ownership=ownership,
                reconciliation=reconciliation,
            ),
        ),
    )
    return SemanticImportResult(
        source_fingerprint="b" * 64,
        spec=spec,
    )


def _plan(
    *,
    import_result=None,
    inventory=None,
    tenant="tenant-a",
):
    imported = import_result or _import_result()
    matrix = SemanticEquivalenceMatrixBuilder.build(imported)
    return SemanticResourceProvisionPlanner.plan(
        tenant_binding=tenant,
        import_result=imported,
        matrix=matrix,
        inventory=inventory or ResourceInventorySnapshot(),
    )


def _applied_inventory(
    desired,
    *,
    tenant="tenant-a",
    payload=None,
    ownership="DIMA_MANAGED",
):
    observed_payload = payload or desired.payload
    observed = ObservedMetabaseResource.from_payload(
        tenant_binding=tenant,
        resource_kind=desired.resource_kind,
        metabase_entity_id="entity-metric-revenue",
        metabase_local_id=101,
        display_name="revenue",
        managed_payload=observed_payload,
    )
    binding = ManagedResourceBinding(
        tenant_binding=tenant,
        canonical_id=desired.canonical_id,
        resource_kind=desired.resource_kind,
        semantic_context_version=desired.semantic_context_version,
        metabase_entity_id=observed.metabase_entity_id,
        metabase_local_id=observed.metabase_local_id,
        applied_version=desired.desired_version,
        applied_fingerprint=(
            desired.desired_fingerprint
            if payload is None
            else observed.resource_fingerprint
        ),
        ownership=ownership,
    )
    return ResourceInventorySnapshot(
        bindings=(binding,),
        resources=(observed,),
    )


def _drift_payload(desired):
    changed = dict(desired.payload)
    changed["display"] = ({"label": "manual edit"},)
    return changed


def test_p9a_explicit_dima_managed_native_semantic_creates_with_rollback():
    plan = _plan()
    assert len(plan.desired_resources) == 1
    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert action.action == ProvisionActionKind.CREATE
    assert action.canonical_id == "metric.orders.revenue"
    assert action.resource_kind == ResourceKind.METRIC
    assert action.rollback is not None
    assert action.rollback.kind == RollbackKind.ARCHIVE_CREATED_RESOURCE


def test_p9a_same_applied_state_is_noop_and_idempotent():
    first = _plan()
    desired = first.desired_resources[0]
    inventory = _applied_inventory(desired)

    second = _plan(inventory=inventory)
    third = _plan(inventory=inventory)
    assert second.actions[0].action == ProvisionActionKind.NOOP
    assert second.plan_fingerprint == third.plan_fingerprint
    assert second == third


@pytest.mark.parametrize(
    ("reconciliation", "action_kind", "rollback_kind"),
    [
        ("OVERWRITE", ProvisionActionKind.UPDATE, RollbackKind.RESTORE_PREVIOUS_SNAPSHOT),
        ("REJECT", ProvisionActionKind.REJECT_DRIFT, None),
        (
            "IMPORT_AS_NEW_VERSION",
            ProvisionActionKind.IMPORT_AS_NEW_VERSION,
            RollbackKind.RESTORE_PREVIOUS_BINDING,
        ),
    ],
)
def test_p9a_drift_uses_only_explicit_reconciliation_policy(
    reconciliation,
    action_kind,
    rollback_kind,
):
    imported = _import_result(reconciliation=reconciliation)
    base = _plan(import_result=imported)
    desired = base.desired_resources[0]
    inventory = _applied_inventory(
        desired,
        payload=_drift_payload(desired),
    )
    plan = _plan(
        import_result=imported,
        inventory=inventory,
    )
    action = plan.actions[0]
    assert action.action == action_kind
    if rollback_kind is None:
        assert action.rollback is None
        assert action.mutating is False
    else:
        assert action.rollback is not None
        assert action.rollback.kind == rollback_kind
        assert action.mutating is True
        assert action.rollback.prior_payload is not None


@pytest.mark.parametrize(
    ("ownership", "reason"),
    [
        ("USER_MANAGED", ProvisionSkipReason.USER_MANAGED),
        ("EXTERNAL", ProvisionSkipReason.EXTERNAL),
    ],
)
def test_p9a_unmanaged_semantic_policy_never_mutates(ownership, reason):
    imported = _import_result(
        ownership=ownership,
        reconciliation=None,
    )
    plan = _plan(import_result=imported)
    assert plan.desired_resources == ()
    assert plan.actions == ()
    assert len(plan.skips) == 1
    assert plan.skips[0].reason == reason


def test_p9a_same_name_unbound_metabase_resource_is_never_adopted():
    create = _plan()
    desired = create.desired_resources[0]
    unrelated = ObservedMetabaseResource.from_payload(
        tenant_binding="tenant-a",
        resource_kind=ResourceKind.METRIC,
        metabase_entity_id="entity-unmanaged",
        metabase_local_id=999,
        display_name="revenue",
        managed_payload={"name": "revenue", "owner": "user"},
    )
    plan = _plan(
        inventory=ResourceInventorySnapshot(
            resources=(unrelated,),
        )
    )
    assert plan.actions[0].action == ProvisionActionKind.CREATE
    assert plan.actions[0].binding is None
    assert desired.canonical_id == plan.actions[0].canonical_id


def test_p9a_cross_tenant_binding_is_never_reused():
    first = _plan()
    desired = first.desired_resources[0]
    tenant_b_inventory = _applied_inventory(
        desired,
        tenant="tenant-b",
    )
    plan = _plan(
        tenant="tenant-a",
        inventory=tenant_b_inventory,
    )
    assert plan.actions[0].action == ProvisionActionKind.CREATE


def test_p9a_missing_bound_resource_is_typed_reject_not_silent_recreate():
    first = _plan()
    desired = first.desired_resources[0]
    binding = ManagedResourceBinding(
        tenant_binding="tenant-a",
        canonical_id=desired.canonical_id,
        resource_kind=desired.resource_kind,
        semantic_context_version=desired.semantic_context_version,
        metabase_entity_id="entity-missing",
        applied_version=desired.desired_version,
        applied_fingerprint=desired.desired_fingerprint,
        ownership="DIMA_MANAGED",
    )
    plan = _plan(
        inventory=ResourceInventorySnapshot(
            bindings=(binding,),
        )
    )
    action = plan.actions[0]
    assert action.action == ProvisionActionKind.REJECT_DRIFT
    assert action.reason_code == "BOUND_RESOURCE_MISSING"
    assert action.mutating is False


def test_p9a_wren_only_formula_metric_is_not_provisioned():
    imported = _import_result(formula="SUM(amount)")
    plan = _plan(import_result=imported)
    assert plan.desired_resources == ()
    assert plan.actions == ()
    assert plan.skips[0].reason == ProvisionSkipReason.WREN_ONLY_GAP


def test_p9a_inventory_order_does_not_change_plan_fingerprint():
    first = _plan()
    desired = first.desired_resources[0]
    applied = _applied_inventory(desired)
    unrelated_a = ObservedMetabaseResource.from_payload(
        tenant_binding="tenant-a",
        resource_kind=ResourceKind.DIMENSION,
        metabase_entity_id="entity-u1",
        managed_payload={"x": 1},
    )
    unrelated_b = ObservedMetabaseResource.from_payload(
        tenant_binding="tenant-b",
        resource_kind=ResourceKind.DIMENSION,
        metabase_entity_id="entity-u2",
        managed_payload={"x": 2},
    )
    inventory_a = ResourceInventorySnapshot(
        bindings=applied.bindings,
        resources=(
            unrelated_a,
            applied.resources[0],
            unrelated_b,
        ),
    )
    inventory_b = ResourceInventorySnapshot(
        bindings=tuple(reversed(applied.bindings)),
        resources=tuple(reversed(inventory_a.resources)),
    )
    assert _plan(inventory=inventory_a).plan_fingerprint == _plan(
        inventory=inventory_b
    ).plan_fingerprint


def test_p9a_duplicate_binding_key_hard_fails():
    desired = _plan().desired_resources[0]
    binding = _applied_inventory(desired).bindings[0]
    with pytest.raises(ValidationError, match="duplicate managed resource"):
        ResourceInventorySnapshot(
            bindings=(binding, binding),
        )


def test_p9a_dima_managed_requires_explicit_reconciliation():
    imported = _import_result(reconciliation=None)
    with pytest.raises(
        ResourceProvisioningError,
        match="lacks reconciliation",
    ):
        _plan(import_result=imported)


def test_p9a_matrix_must_belong_to_same_p7_source():
    imported = _import_result()
    matrix = SemanticEquivalenceMatrixBuilder.build(imported).model_copy(
        update={"source_fingerprint": "c" * 64}
    )
    with pytest.raises(
        ResourceProvisioningError,
        match="source fingerprint",
    ):
        SemanticResourceProvisionPlanner.plan(
            tenant_binding="tenant-a",
            import_result=imported,
            matrix=matrix,
            inventory=ResourceInventorySnapshot(),
        )


def test_p9a_has_no_search_fuzzy_regex_or_external_transport_dependency():
    tree = ast.parse(inspect.getsource(provisioning_module))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(
        {
            "re",
            "regex",
            "httpx",
            "requests",
            "difflib",
            "rapidfuzz",
            "fuzzywuzzy",
            "Levenshtein",
        }
    )
    source = inspect.getsource(provisioning_module).lower()
    for forbidden in (
        ".search(",
        "metabaseagentclient",
        "canonical_name lookup",
        "similar-name",
        "raw prompt",
    ):
        assert forbidden not in source



def test_p9a_mutating_action_contract_requires_rollback_descriptor():
    with pytest.raises(
        ValidationError,
        match="mutating provision action requires rollback",
    ):
        ProvisionAction(
            action=ProvisionActionKind.CREATE,
            canonical_id="metric.x",
            resource_kind=ResourceKind.METRIC,
            reason_code="fixture",
        )

    action = ProvisionAction(
        action=ProvisionActionKind.REJECT_DRIFT,
        canonical_id="metric.x",
        resource_kind=ResourceKind.METRIC,
        reason_code="fixture",
    )
    assert action.rollback is None
    assert action.mutating is False


def test_p9a_removed_semantic_retires_stale_dima_binding_with_rollback():
    prior = _plan()
    desired = prior.desired_resources[0]
    inventory = _applied_inventory(desired)

    current = SemanticImportResult(
        source_fingerprint="d" * 64,
        spec=DimaSemanticSpec(
            semantic_context_version="ctx-p9-next",
        ),
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(current)
    plan = SemanticResourceProvisionPlanner.plan(
        tenant_binding="tenant-a",
        import_result=current,
        matrix=matrix,
        inventory=inventory,
    )

    assert plan.desired_resources == ()
    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert action.action == ProvisionActionKind.RETIRE_STALE
    assert action.reason_code == "SEMANTIC_REMOVED_FROM_DESIRED_STATE"
    assert action.binding == inventory.bindings[0]
    assert action.rollback is not None
    assert action.rollback.kind == RollbackKind.RESTORE_PREVIOUS_BINDING
    assert action.rollback.prior_binding == inventory.bindings[0]
    assert action.rollback.prior_payload == inventory.resources[0].managed_payload


def test_p9a_semantic_still_exists_but_not_provisionable_rejects_stale_representation():
    prior = _plan()
    inventory = _applied_inventory(prior.desired_resources[0])
    current = _import_result(formula="SUM(amount)")
    plan = _plan(
        import_result=current,
        inventory=inventory,
    )
    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert action.action == ProvisionActionKind.REJECT_DRIFT
    assert action.reason_code == "REPRESENTATION_NO_LONGER_PROVISIONABLE"
    assert action.mutating is False


def test_p9a_ownership_transfer_never_auto_deletes_old_dima_resource():
    prior = _plan()
    inventory = _applied_inventory(prior.desired_resources[0])
    current = _import_result(
        ownership="USER_MANAGED",
        reconciliation=None,
    )
    plan = _plan(
        import_result=current,
        inventory=inventory,
    )
    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert action.action == ProvisionActionKind.REJECT_DRIFT
    assert (
        action.reason_code
        == "OWNERSHIP_TRANSFER_REQUIRES_EXPLICIT_DECISION"
    )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        (
            "semantic_context_version",
            "ctx-stale",
            "BINDING_CONTEXT_VERSION_DRIFT",
        ),
        (
            "applied_version",
            "metric-old",
            "BINDING_APPLIED_VERSION_DRIFT",
        ),
    ],
)
def test_p9a_matching_payload_is_not_noop_when_binding_metadata_drifts(
    field,
    value,
    reason,
):
    first = _plan()
    desired = first.desired_resources[0]
    inventory = _applied_inventory(desired)
    binding = inventory.bindings[0].model_copy(
        update={field: value}
    )
    drifted = inventory.model_copy(
        update={"bindings": (binding,)}
    )

    plan = _plan(inventory=drifted)
    assert plan.actions[0].action == ProvisionActionKind.REJECT_DRIFT
    assert plan.actions[0].reason_code == reason


def test_p9a_real_composed_p7_p8_explicit_policy_p9_chain_creates_one_stable_resource():
    manifest = json.loads(
        (
            ROOT
            / "demo"
            / "wren-engine-proje"
            / "target"
            / "mdl.json"
        ).read_text(encoding="utf-8")
    )
    imported = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="demo-real-chain-p9",
    )
    base_matrix = SemanticEquivalenceMatrixBuilder.build(imported)
    native = next(
        row
        for row in base_matrix.rows
        if (
            row.dima_state.value == "REPRESENTED"
            and row.classification
            == EquivalenceClassification.NATIVE_METABASE
            and row.feature_kind in {"dimension", "time"}
        )
    )
    policy = ManagedResourcePolicy(
        semantic_ref=native.feature_ref,
        ownership="DIMA_MANAGED",
        reconciliation="OVERWRITE",
    )
    with_policy = imported.model_copy(
        update={
            "spec": imported.spec.model_copy(
                update={"managed_resources": (policy,)}
            )
        }
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(with_policy)

    first = SemanticResourceProvisionPlanner.plan(
        tenant_binding="tenant-real-chain",
        import_result=with_policy,
        matrix=matrix,
        inventory=ResourceInventorySnapshot(),
    )
    second = SemanticResourceProvisionPlanner.plan(
        tenant_binding="tenant-real-chain",
        import_result=with_policy,
        matrix=matrix,
        inventory=ResourceInventorySnapshot(),
    )

    assert len(first.desired_resources) == 1
    assert len(first.actions) == 1
    assert first.actions[0].action == ProvisionActionKind.CREATE
    assert first.actions[0].canonical_id == native.feature_ref
    assert first.actions[0].rollback is not None
    assert first.actions[0].rollback.kind == RollbackKind.ARCHIVE_CREATED_RESOURCE
    assert first.plan_fingerprint == second.plan_fingerprint
    assert first.desired_resources[0].desired_fingerprint == (
        second.desired_resources[0].desired_fingerprint
    )
