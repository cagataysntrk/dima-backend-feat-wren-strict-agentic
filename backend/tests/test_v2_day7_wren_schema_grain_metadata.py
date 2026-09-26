"""Day7 current-HEAD certification for governed Wren row-grain metadata.

Uses the actual composed demo MDL behind the real Wren fixture.  The boundary must
preserve declared Wren truth; it must not infer grain from names or physical FKs.
"""

from __future__ import annotations

import json


def test_real_wren_schema_preserves_declared_primary_key_and_relationship_metadata(
    wren,
):
    raw = json.loads(wren.mdl_path.read_text(encoding="utf-8"))
    schema = wren.schema()

    raw_models = {
        str(model.get("name")): model
        for model in raw.get("models", [])
        if model.get("name")
    }
    schema_models = {
        str(model.get("name")): model
        for model in schema.get("models", [])
        if model.get("name")
    }

    declared_pk_models = [
        model
        for model in raw_models.values()
        if model.get("primaryKey") or model.get("primary_key")
    ]
    assert declared_pk_models, "demo composed MDL must contain declared model primaryKey"

    for model in declared_pk_models:
        name = str(model["name"])
        exported = schema_models[name]
        assert exported.get("primary_key") == (
            model.get("primaryKey") or model.get("primary_key")
        )

    declared_pk_columns = []
    declared_non_pk_columns = []
    for model in raw_models.values():
        for column in model.get("columns", []):
            pair = (str(model["name"]), str(column.get("name")))
            if column.get("isPrimaryKey") or column.get("is_primary_key"):
                declared_pk_columns.append(pair)
            else:
                declared_non_pk_columns.append(pair)

    assert declared_pk_columns, "demo composed MDL must expose at least one declared PK column"
    for model_name, column_name in declared_pk_columns:
        exported = next(
            column
            for column in schema_models[model_name]["columns"]
            if column.get("name") == column_name
        )
        assert exported.get("is_primary_key") is True

    # Negative proof: names and physical shape are not promoted to row-grain authority.
    assert declared_non_pk_columns
    for model_name, column_name in declared_non_pk_columns:
        exported = next(
            column
            for column in schema_models[model_name]["columns"]
            if column.get("name") == column_name
        )
        assert "is_primary_key" not in exported

    undeclared_pk_models = [
        model
        for model in raw_models.values()
        if not (model.get("primaryKey") or model.get("primary_key"))
    ]
    for model in undeclared_pk_models:
        assert not schema_models[str(model["name"])].get("primary_key")

    raw_relationships = {
        str(rel.get("name")): rel
        for rel in raw.get("relationships", [])
        if rel.get("name")
    }
    exported_relationships = {
        str(rel.get("name")): rel
        for rel in schema.get("relationships", [])
        if rel.get("name")
    }
    assert raw_relationships

    for name, rel in raw_relationships.items():
        exported = exported_relationships[name]
        assert exported.get("name") == name
        assert tuple(exported.get("models") or ()) == tuple(rel.get("models") or ())
        assert exported.get("join_type") == rel.get("joinType", "")
        assert exported.get("condition") == rel.get("condition", "")
        # Certification may be enriched from the fanout certificate, but it must remain
        # explicit rather than silently assumed healthy.
        assert "certified" in exported
        assert exported["certified"] in {
            "olculmedi",
            "olculdu:saglikli",
            "olculdu:riskli",
        }
