from __future__ import annotations

import ast
import copy
import inspect
import json
from pathlib import Path

import pytest

from app.v3 import semantic_equivalence as equivalence_module
from app.v3.semantic_equivalence import (
    DimaRepresentationState,
    EquivalenceClassification,
    SemanticEquivalenceError,
    SemanticEquivalenceMatrixBuilder,
)
from app.v3.semantic_import import (
    SemanticImportGap,
    SemanticImportResult,
    WrenSemanticSpecImporter,
)
from app.v3.semantic_spec import (
    DimaSemanticSpec,
    JoinKeySpec,
    MetricSpec,
    RelationshipSpec,
    SourceLineage,
)


ROOT = Path(__file__).resolve().parents[1]
HEX = "a" * 64


def _base_manifest():
    return {
        "models": [
            {
                "name": "orders",
                "tableReference": {
                    "catalog": "analytics",
                    "schema": "public",
                    "table": "orders",
                },
                "columns": [
                    {"name": "amount", "type": "double"},
                    {"name": "region", "type": "varchar"},
                    {"name": "order_date", "type": "date"},
                ],
            }
        ],
        "relationships": [
            {
                "name": "orders_customer",
                "models": ["orders", "customers"],
                "joinType": "MANY_TO_ONE",
                "condition": "orders.customer_id = customers.id",
            }
        ],
        "cubes": [
            {
                "name": "sales",
                "label": "Sales",
                "baseObject": "orders",
                "measures": [
                    {
                        "name": "revenue",
                        "expression": "SUM(amount)",
                        "type": "double",
                    }
                ],
                "dimensions": [
                    {
                        "name": "region",
                        "expression": "region",
                        "type": "varchar",
                    }
                ],
                "timeDimensions": [
                    {
                        "name": "order_date",
                        "expression": "order_date",
                        "type": "date",
                    }
                ],
            }
        ],
        "views": [],
    }


def _build_from_manifest(manifest=None):
    imported = WrenSemanticSpecImporter.import_manifest(
        manifest or _base_manifest(),
        semantic_context_version="ctx-p8",
    )
    return imported, SemanticEquivalenceMatrixBuilder.build(imported)


def test_p8_exact_physical_dimension_and_time_are_native_metabase():
    _, matrix = _build_from_manifest()
    by_ref = {item.feature_ref: item for item in matrix.rows}
    assert (
        by_ref["dimension.sales.region"].classification
        == EquivalenceClassification.NATIVE_METABASE
    )
    assert (
        by_ref["time.sales.order_date"].classification
        == EquivalenceClassification.NATIVE_METABASE
    )


def test_p8_opaque_formula_metric_is_not_text_parsed_into_false_native():
    imported, matrix = _build_from_manifest()
    metric = imported.spec.metrics[0]
    assert metric.formula == "SUM(amount)"
    row = next(
        item
        for item in matrix.rows
        if item.feature_ref == metric.metric_id
    )
    assert row.classification == EquivalenceClassification.WREN_ONLY_GAP
    assert row.reason_code == "OPAQUE_METRIC_FORMULA_NOT_STRUCTURALLY_EQUIVALENT"


def test_p8_explicit_mechanical_metric_with_exact_lineage_is_native():
    metric = MetricSpec(
        metric_id="metric.orders.amount",
        name="amount",
        formula=None,
        aggregation="sum",
        semantic_version="1",
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
    result = SemanticImportResult(
        source_fingerprint=HEX,
        spec=DimaSemanticSpec(
            semantic_context_version="ctx-p8",
            metrics=(metric,),
        ),
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(result)
    assert matrix.rows[0].classification == EquivalenceClassification.NATIVE_METABASE
    assert matrix.rows[0].reason_code == "P4_MECHANICAL_AGGREGATION_WITH_EXACT_LINEAGE"


def test_p8_structured_relationship_is_dima_compiled():
    relationship = RelationshipSpec(
        relationship_id="relationship.orders.customer",
        from_ref="model.orders",
        to_ref="model.customers",
        cardinality="many_to_one",
        join_keys=(
            JoinKeySpec(
                left_ref="orders.customer_id",
                right_ref="customers.id",
            ),
        ),
        semantic_version="1",
    )
    result = SemanticImportResult(
        source_fingerprint=HEX,
        spec=DimaSemanticSpec(
            semantic_context_version="ctx-p8",
            relationships=(relationship,),
        ),
    )
    row = SemanticEquivalenceMatrixBuilder.build(result).rows[0]
    assert row.classification == EquivalenceClassification.DIMA_COMPILED


@pytest.mark.parametrize(
    ("code", "classification"),
    [
        ("RELATIONSHIP_JOIN_KEY_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("CALCULATED_DIMENSION_EXPRESSION_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("VIEW_DEFINITION_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("CUBE_SEMANTIC_ENTITY_GAP", EquivalenceClassification.DIMA_RUNTIME),
        ("ROW_SECURITY_DEFERRED_TO_P10", EquivalenceClassification.DIMA_RUNTIME),
        ("SECURITY_METADATA_DEFERRED_TO_P10", EquivalenceClassification.DIMA_RUNTIME),
        ("METRIC_DIRECTIONALITY_METADATA_GAP", EquivalenceClassification.DIMA_RUNTIME),
        ("METRIC_NL_METADATA_GAP", EquivalenceClassification.DIMA_RUNTIME),
        ("CUBE_DOMAIN_METADATA_GAP", EquivalenceClassification.DIMA_RUNTIME),
        ("GRAIN_KEY_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("RELATIONSHIP_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("RELATIONSHIP_PATH_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("RELATIONSHIP_CARDINALITY_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("RELATIONSHIP_EXPOSE_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("METRIC_TYPE_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("CUBE_GRAIN_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("CUBE_PVM_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("VIEW_COLUMN_METADATA_GAP", EquivalenceClassification.WREN_ONLY_GAP),
        ("CUBE_BASE_OBJECT_MISSING", EquivalenceClassification.UNSUPPORTED),
    ],
)
def test_p8_known_typed_gap_classification_is_exact(code, classification):
    result = SemanticImportResult(
        source_fingerprint=HEX,
        spec=DimaSemanticSpec(semantic_context_version="ctx-p8"),
        gaps=(
            SemanticImportGap(
                code=code,
                source_ref="fixture:one",
                detail="fixture",
            ),
        ),
    )
    row = SemanticEquivalenceMatrixBuilder.build(result).rows[0]
    assert row.dima_state == DimaRepresentationState.TYPED_GAP
    assert row.classification == classification
    assert row.reason_code == code


def test_p8_unknown_gap_code_is_hard_red():
    result = SemanticImportResult(
        source_fingerprint=HEX,
        spec=DimaSemanticSpec(semantic_context_version="ctx-p8"),
        gaps=(
            SemanticImportGap(
                code="NEW_UNREVIEWED_GAP",
                source_ref="fixture:unknown",
                detail="must not default",
            ),
        ),
    )
    with pytest.raises(SemanticEquivalenceError, match="unknown P7"):
        SemanticEquivalenceMatrixBuilder.build(result)


def test_p8_matrix_order_and_fingerprint_are_deterministic():
    imported = WrenSemanticSpecImporter.import_manifest(
        _base_manifest(),
        semantic_context_version="ctx-p8",
    )
    first = SemanticEquivalenceMatrixBuilder.build(imported)
    reordered = imported.model_copy(
        update={
            "gaps": tuple(reversed(imported.gaps)),
            "spec": imported.spec.model_copy(
                update={
                    "dimensions": tuple(reversed(imported.spec.dimensions)),
                    "metrics": tuple(reversed(imported.spec.metrics)),
                }
            ),
        }
    )
    second = SemanticEquivalenceMatrixBuilder.build(reordered)
    assert first.rows == second.rows
    assert first.matrix_fingerprint == second.matrix_fingerprint


def test_p8_has_no_formula_regex_sql_parser_or_fuzzy_dependency():
    tree = ast.parse(inspect.getsource(equivalence_module))
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
            "sqlglot",
            "difflib",
            "rapidfuzz",
            "fuzzywuzzy",
            "Levenshtein",
        }
    )


def test_p8_current_real_composed_manifest_classifies_without_unknown_gap():
    path = ROOT / "demo" / "wren-engine-proje" / "target" / "mdl.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    imported = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="demo-composed-p8",
    )
    matrix = SemanticEquivalenceMatrixBuilder.build(imported)

    assert matrix.rows
    assert len(matrix.matrix_fingerprint) == 64
    classifications = {item.classification for item in matrix.rows}
    assert EquivalenceClassification.NATIVE_METABASE in classifications
    assert EquivalenceClassification.WREN_ONLY_GAP in classifications
    assert EquivalenceClassification.DIMA_RUNTIME in classifications

    repeated = SemanticEquivalenceMatrixBuilder.build(
        WrenSemanticSpecImporter.import_manifest(
            copy.deepcopy(manifest),
            semantic_context_version="demo-composed-p8",
        )
    )
    assert repeated.matrix_fingerprint == matrix.matrix_fingerprint



def test_p8_unmapped_structured_field_remains_hard_red():
    result = SemanticImportResult(
        source_fingerprint=HEX,
        spec=DimaSemanticSpec(semantic_context_version="ctx-p8"),
        gaps=(
            SemanticImportGap(
                code="UNMAPPED_STRUCTURED_FIELD",
                source_ref="cube:x.field:newThing",
                detail="future structured field",
            ),
        ),
    )
    with pytest.raises(SemanticEquivalenceError, match="unknown P7"):
        SemanticEquivalenceMatrixBuilder.build(result)
