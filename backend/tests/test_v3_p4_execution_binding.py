from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.v3.semantic_spec import SourceLineage
from app.v3.substrate.metabase import execution_binding, p3a_models
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    MetabaseCompilationBlocked,
    TemporalSemanticBinding,
)
from app.v3.substrate.metabase.p3a_fixture import build_snapshot


def _metric_lineage(snapshot):
    return snapshot.semantic_spec.metrics[0].source_lineage[0]


def _replace_catalog_object(snapshot, source_id: str, **updates):
    objects = tuple(
        item.model_copy(update=updates) if item.source_id == source_id else item
        for item in snapshot.current_catalog.objects
    )
    return CurrentCatalogSnapshot(
        catalog_version=snapshot.current_catalog.catalog_version,
        objects=objects,
    )


def test_binding_contract_has_single_exact_owner():
    assert p3a_models.CandidateSemanticBinding is execution_binding.CandidateSemanticBinding
    assert p3a_models.TemporalSemanticBinding is execution_binding.TemporalSemanticBinding
    assert p3a_models.DimaExecutionBindingSnapshot is execution_binding.DimaExecutionBindingSnapshot
    assert p3a_models.CurrentCatalogObject is execution_binding.CurrentCatalogObject
    assert p3a_models.CurrentCatalogSnapshot is execution_binding.CurrentCatalogSnapshot
    assert p3a_models.P3ABridgeBlocked is execution_binding.MetabaseCompilationBlocked


def test_semantic_context_identity_is_enforced():
    base = build_snapshot()
    with pytest.raises(ValidationError, match="semantic spec/snapshot context mismatch"):
        DimaExecutionBindingSnapshot(
            semantic_context_version="other-context",
            semantic_spec=base.semantic_spec,
            candidate_bindings=base.candidate_bindings,
            temporal_bindings=base.temporal_bindings,
            current_catalog=base.current_catalog,
        )


@pytest.mark.parametrize(
    ("kind", "semantic_id"),
    [
        ("metric", "metric.unknown"),
        ("dimension", "dimension.unknown"),
        ("filter", "dimension.unknown"),
    ],
)
def test_candidate_binding_must_reference_existing_semantic_id(kind, semantic_id):
    base = build_snapshot()
    with pytest.raises(ValidationError, match="references unknown Dima"):
        DimaExecutionBindingSnapshot(
            semantic_context_version=base.semantic_context_version,
            semantic_spec=base.semantic_spec,
            candidate_bindings=(
                CandidateSemanticBinding(
                    candidate_id=f"unknown-{kind}",
                    semantic_id=semantic_id,
                    kind=kind,
                ),
            ),
            temporal_bindings=base.temporal_bindings,
            current_catalog=base.current_catalog,
        )


def test_candidate_lookup_and_duplicate_candidate_fail_closed():
    base = build_snapshot()
    assert base.candidate("cand_metric", kind="metric") == "metric.revenue"
    assert base.candidate("cand_region", kind="dimension") == "dimension.region"
    assert base.candidate("cand_filter_north", kind="filter") == "dimension.region"

    duplicate = CandidateSemanticBinding(
        candidate_id=base.candidate_bindings[0].candidate_id,
        semantic_id=base.candidate_bindings[0].semantic_id,
        kind=base.candidate_bindings[0].kind,
    )
    with pytest.raises(ValidationError, match="duplicate candidate binding"):
        DimaExecutionBindingSnapshot(
            semantic_context_version=base.semantic_context_version,
            semantic_spec=base.semantic_spec,
            candidate_bindings=(*base.candidate_bindings, duplicate),
            temporal_bindings=base.temporal_bindings,
            current_catalog=base.current_catalog,
        )


def test_temporal_binding_unknown_and_duplicate_fail_closed():
    base = build_snapshot()

    with pytest.raises(ValidationError, match="unknown Dima dimension"):
        DimaExecutionBindingSnapshot(
            semantic_context_version=base.semantic_context_version,
            semantic_spec=base.semantic_spec,
            candidate_bindings=base.candidate_bindings,
            temporal_bindings=(
                TemporalSemanticBinding(
                    compatibility_key="unknown-time",
                    dimension_id="dimension.unknown",
                ),
            ),
            current_catalog=base.current_catalog,
        )

    duplicate = TemporalSemanticBinding(
        compatibility_key=base.temporal_bindings[0].compatibility_key,
        dimension_id=base.temporal_bindings[0].dimension_id,
    )
    with pytest.raises(ValidationError, match="duplicate temporal compatibility binding"):
        DimaExecutionBindingSnapshot(
            semantic_context_version=base.semantic_context_version,
            semantic_spec=base.semantic_spec,
            candidate_bindings=base.candidate_bindings,
            temporal_bindings=(*base.temporal_bindings, duplicate),
            current_catalog=base.current_catalog,
        )


def test_current_catalog_rejects_duplicate_source_id():
    base = build_snapshot()
    with pytest.raises(ValidationError, match="duplicate current catalog source_id"):
        CurrentCatalogSnapshot(
            catalog_version=base.current_catalog.catalog_version,
            objects=(
                *base.current_catalog.objects,
                base.current_catalog.objects[0],
            ),
        )


def test_missing_current_catalog_source_fails_closed():
    base = build_snapshot()
    lineage = _metric_lineage(base)
    catalog = CurrentCatalogSnapshot(
        catalog_version=base.current_catalog.catalog_version,
        objects=tuple(
            item
            for item in base.current_catalog.objects
            if item.source_id != lineage.source_id
        ),
    )
    broken = base.model_copy(update={"current_catalog": catalog})

    with pytest.raises(MetabaseCompilationBlocked) as exc:
        broken.current_lineage(lineage)
    assert exc.value.code == "CURRENT_CATALOG_BINDING_MISSING"


def test_exact_expected_lineage_matches_current_catalog():
    base = build_snapshot()
    lineage = _metric_lineage(base)
    current = base.current_lineage(lineage)
    assert current.portable_field == (
        "Dima Analytics Lab",
        "public",
        "orders",
        "amount",
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("database_ref", "Other DB"),
        ("schema_name", "other_schema"),
        ("table_name", "orders_v2"),
        ("column_name", "amount_v2"),
    ],
)
def test_each_physical_lineage_drift_dimension_fails_closed(field, value):
    base = build_snapshot()
    lineage = _metric_lineage(base)
    catalog = _replace_catalog_object(base, lineage.source_id, **{field: value})
    broken = base.model_copy(update={"current_catalog": catalog})

    with pytest.raises(MetabaseCompilationBlocked) as exc:
        broken.current_lineage(lineage)
    assert exc.value.code == "SOURCE_LINEAGE_DRIFT"


@pytest.mark.parametrize(
    "lineage",
    [
        SourceLineage(
            source_id="incomplete.db",
            database_ref=None,
            schema_name="public",
            table_name="orders",
            column_name="amount",
        ),
        SourceLineage(
            source_id="incomplete.table",
            database_ref="Dima Analytics Lab",
            schema_name="public",
            table_name=None,
            column_name="amount",
        ),
    ],
)
def test_incomplete_database_or_table_lineage_fails_closed(lineage):
    base = build_snapshot()
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        base.current_lineage(lineage)
    assert exc.value.code == "INCOMPLETE_SOURCE_LINEAGE"


def test_column_required_contract_fails_closed():
    item = CurrentCatalogObject(
        source_id="orders",
        database_ref="Dima Analytics Lab",
        schema_name="public",
        table_name="orders",
        column_name=None,
        resource_entity_id="lab:orders",
        resource_fingerprint="d" * 64,
    )
    assert item.portable_table == ("Dima Analytics Lab", "public", "orders")
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        _ = item.portable_field
    assert exc.value.code == "CATALOG_OBJECT_HAS_NO_COLUMN"


def test_catalog_fingerprint_is_order_independent_and_change_sensitive():
    base = build_snapshot()
    catalog = base.current_catalog
    reordered = CurrentCatalogSnapshot(
        catalog_version=catalog.catalog_version,
        objects=tuple(reversed(catalog.objects)),
    )
    assert reordered.fingerprint == catalog.fingerprint

    first = catalog.objects[0]
    changed_resource = first.model_copy(update={"resource_fingerprint": "e" * 64})
    changed = CurrentCatalogSnapshot(
        catalog_version=catalog.catalog_version,
        objects=(changed_resource, *catalog.objects[1:]),
    )
    assert changed.fingerprint != catalog.fingerprint

    changed_physical = first.model_copy(update={"column_name": first.column_name + "_v2"})
    changed2 = CurrentCatalogSnapshot(
        catalog_version=catalog.catalog_version,
        objects=(changed_physical, *catalog.objects[1:]),
    )
    assert changed2.fingerprint != catalog.fingerprint
