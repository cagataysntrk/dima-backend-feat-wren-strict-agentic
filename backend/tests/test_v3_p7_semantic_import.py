from __future__ import annotations

import ast
import copy
import inspect
import json
from pathlib import Path

import pytest

from app.v3 import semantic_import as semantic_import_module
from app.v3.semantic_import import (
    SemanticImportError,
    WrenSemanticSpecImporter,
)


ROOT = Path(__file__).resolve().parents[1]


def _manifest():
    return {
        "catalog": "wren",
        "schema": "public",
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
                    {"name": "customer_id", "type": "integer"},
                    {
                        "name": "derived_bucket",
                        "type": "varchar",
                        "isCalculated": True,
                        "expression": "CASE ... END",
                    },
                ],
            },
            {
                "name": "customers",
                "tableReference": {
                    "catalog": "analytics",
                    "schema": "public",
                    "table": "customers",
                },
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "segment", "type": "varchar"},
                ],
            },
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
                "synonyms": ["revenue analytics"],
                "baseObject": "orders",
                "measures": [
                    {
                        "name": "revenue",
                        "expression": "SUM(amount)",
                        "type": "double",
                        "unit": "USD",
                        "synonyms": ["sales", "turnover"],
                    },
                    {
                        "name": "avg_ticket",
                        "expression": "SUM(amount) / NULLIF(COUNT(*), 0)",
                        "type": "double",
                        "additive": "non",
                    },
                    {
                        "name": "distinct_customers",
                        "expression": "COUNT(DISTINCT customer_id)",
                        "type": "double",
                    },
                    {
                        "name": "balance",
                        "expression": "SUM(amount)",
                        "type": "double",
                        "additive": "semi",
                    },
                ],
                "dimensions": [
                    {
                        "name": "region",
                        "expression": "region",
                        "type": "varchar",
                        "label": "Region",
                        "synonyms": ["area"],
                    },
                    {
                        "name": "bucket",
                        "expression": "CASE WHEN amount > 100 THEN 'high' ELSE 'low' END",
                        "type": "varchar",
                    },
                ],
                "timeDimensions": [
                    {
                        "name": "order_date",
                        "expression": "order_date",
                        "type": "date",
                        "grain": "day",
                    }
                ],
            }
        ],
        "views": [],
    }


def _metric(result, name):
    return next(item for item in result.spec.metrics if item.name == name)


def _dimension(result, name):
    return next(item for item in result.spec.dimensions if item.name == name)


def test_p7_imports_metric_formula_alias_additivity_and_display_exactly():
    result = WrenSemanticSpecImporter.import_manifest(
        _manifest(),
        semantic_context_version="ctx-p7",
    )

    revenue = _metric(result, "revenue")
    assert revenue.metric_id == "metric.sales.revenue"
    assert revenue.formula == "SUM(amount)"
    assert revenue.aggregation == "expression"
    assert revenue.aliases == ("sales", "turnover")
    assert revenue.unit == "USD"
    assert revenue.additive_kind == "unknown"
    assert revenue.source_lineage[0].table_name == "orders"

    ratio = _metric(result, "avg_ticket")
    assert ratio.formula == "SUM(amount) / NULLIF(COUNT(*), 0)"
    assert ratio.additive_kind == "non_additive"

    distinct = _metric(result, "distinct_customers")
    assert distinct.formula == "COUNT(DISTINCT customer_id)"
    assert distinct.aggregation == "expression"

    balance = _metric(result, "balance")
    assert balance.additive_kind == "semi_additive"

    display = next(
        item
        for item in result.spec.display_specs
        if item.semantic_ref == revenue.metric_id
    )
    assert display.unit == "USD"


def test_p7_exact_column_lineage_and_time_dimension_are_structural():
    result = WrenSemanticSpecImporter.import_manifest(
        _manifest(),
        semantic_context_version="ctx-p7",
    )
    region = _dimension(result, "region")
    assert region.aliases == ("area",)
    assert region.source_lineage[0].table_name == "orders"
    assert region.source_lineage[0].column_name == "region"

    order_date = _dimension(result, "order_date")
    assert order_date.source_lineage[0].column_name == "order_date"
    time = result.spec.time_specs[0]
    assert time.dimension_ref == order_date.dimension_id
    assert time.grain == "day"


def test_p7_does_not_parse_calculated_dimension_or_relationship_condition():
    result = WrenSemanticSpecImporter.import_manifest(
        _manifest(),
        semantic_context_version="ctx-p7",
    )
    codes = {gap.code for gap in result.gaps}
    assert "CALCULATED_MODEL_COLUMN_GAP" in codes
    assert "CALCULATED_DIMENSION_EXPRESSION_GAP" in codes
    assert "RELATIONSHIP_JOIN_KEY_GAP" in codes
    assert result.spec.relationships == ()


def test_p7_final_composed_override_changes_spec_without_override_parser():
    original = _manifest()
    overridden = copy.deepcopy(original)
    overridden["cubes"][0]["measures"][0]["unit"] = "EUR"
    overridden["cubes"][0]["measures"][0]["synonyms"] = [
        "sales",
        "net turnover",
    ]

    base = WrenSemanticSpecImporter.import_manifest(
        original,
        semantic_context_version="ctx-p7",
    )
    changed = WrenSemanticSpecImporter.import_manifest(
        overridden,
        semantic_context_version="ctx-p7",
    )

    assert _metric(base, "revenue").unit == "USD"
    assert _metric(changed, "revenue").unit == "EUR"
    assert _metric(changed, "revenue").aliases == (
        "sales",
        "net turnover",
    )
    assert (
        _metric(base, "revenue").compatibility_hash
        != _metric(changed, "revenue").compatibility_hash
    )
    assert base.source_fingerprint != changed.source_fingerprint


def test_p7_import_is_deterministic_and_duplicate_source_names_fail_closed():
    manifest = _manifest()
    first = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="ctx-p7",
    )
    second = WrenSemanticSpecImporter.import_manifest(
        copy.deepcopy(manifest),
        semantic_context_version="ctx-p7",
    )
    assert first.model_dump(mode="json") == second.model_dump(mode="json")

    broken = copy.deepcopy(manifest)
    broken["models"].append(copy.deepcopy(broken["models"][0]))
    with pytest.raises(SemanticImportError, match="duplicate models name"):
        WrenSemanticSpecImporter.import_manifest(
            broken,
            semantic_context_version="ctx-p7",
        )


def test_p7_unknown_additivity_is_typed_gap_not_guess():
    manifest = _manifest()
    manifest["cubes"][0]["measures"][0]["additive"] = "sometimes"
    result = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="ctx-p7",
    )
    revenue = _metric(result, "revenue")
    assert revenue.additive_kind == "unknown"
    assert any(
        gap.code == "UNSUPPORTED_ADDITIVITY_TOKEN"
        and gap.source_ref == "cube:sales.measure:revenue"
        for gap in result.gaps
    )


def test_p7_importer_has_no_regex_fuzzy_sql_parser_or_substrate_search_dependency():
    tree = ast.parse(inspect.getsource(semantic_import_module))
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
    source = inspect.getsource(semantic_import_module).lower()
    for forbidden in (
        ".search(",
        ".read_resource(",
        "metabaseagentclient",
        "semantic_handles",
        "source_message",
        "request_ref",
    ):
        assert forbidden not in source


def test_p7_current_composed_demo_mdl_imports_deterministically_with_typed_gaps():
    path = ROOT / "demo" / "wren-engine-proje" / "target" / "mdl.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))

    first = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="demo-composed-p7",
    )
    second = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="demo-composed-p7",
    )

    assert first.source_fingerprint == second.source_fingerprint
    assert first.spec.model_dump(mode="json") == second.spec.model_dump(mode="json")
    assert len(first.spec.metrics) > 10
    assert len(first.spec.dimensions) > 10
    assert len(first.spec.time_specs) > 0
    assert all(gap.code and gap.source_ref for gap in first.gaps)
    assert any(
        gap.code == "RELATIONSHIP_JOIN_KEY_GAP"
        for gap in first.gaps
    )



def test_p7_real_manifest_structured_field_coverage_is_complete_and_loss_visible():
    path = ROOT / "demo" / "wren-engine-proje" / "target" / "mdl.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    result = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="demo-composed-p7-coverage",
    )
    codes = [gap.code for gap in result.gaps]

    assert "UNMAPPED_STRUCTURED_FIELD" not in codes
    expected_counts = {
        "METRIC_DIRECTIONALITY_METADATA_GAP": 104,
        "METRIC_NL_METADATA_GAP": 1,
        "METRIC_TYPE_METADATA_GAP": 136,
        "SECURITY_METADATA_DEFERRED_TO_P10": 24,
        "GRAIN_KEY_METADATA_GAP": 76,
        "RELATIONSHIP_METADATA_GAP": 20,
        "RELATIONSHIP_PATH_METADATA_GAP": 9,
        "RELATIONSHIP_CARDINALITY_METADATA_GAP": 31,
        "RELATIONSHIP_EXPOSE_METADATA_GAP": 9,
        "CUBE_GRAIN_METADATA_GAP": 1,
        "CUBE_DOMAIN_METADATA_GAP": 1,
        "CUBE_PVM_METADATA_GAP": 3,
        "VIEW_COLUMN_METADATA_GAP": 1,
    }
    for code, expected in expected_counts.items():
        assert codes.count(code) == expected


def test_p7_unknown_nonempty_structured_field_is_never_silently_ignored():
    manifest = _manifest()
    manifest["cubes"][0]["futureSemanticKnob"] = {"mode": "new"}
    result = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="ctx-p7-unknown-field",
    )
    gap = next(
        item
        for item in result.gaps
        if item.code == "UNMAPPED_STRUCTURED_FIELD"
    )
    assert gap.source_ref == "cube:sales.field:futureSemanticKnob"


def test_p7_explicit_operational_and_physical_constraints_do_not_emit_noise_gaps():
    manifest = _manifest()
    manifest["dataSource"] = "postgres"
    manifest["layoutVersion"] = 1
    manifest["catalog"] = "wren"
    manifest["schema"] = "public"
    manifest["models"][0]["columns"][0]["notNull"] = False
    manifest["models"][0]["columns"][0]["type"] = "double"

    result = WrenSemanticSpecImporter.import_manifest(
        manifest,
        semantic_context_version="ctx-p7-operational",
    )
    refs = {item.source_ref for item in result.gaps}
    assert "manifest.field:dataSource" not in refs
    assert "manifest.field:layoutVersion" not in refs
    assert "model:orders.column:amount.field:notNull" not in refs
    assert "model:orders.column:amount.field:type" not in refs
