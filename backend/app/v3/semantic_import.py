"""P7 structured Wren MDL -> DimaSemanticSpec importer.

The importer consumes an already-composed MDL mapping. It never resolves user language,
searches a substrate, parses SQL/formula text, or reimplements pack/customer composition.
Unsupported source richness is surfaced as typed import gaps.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.semantic_spec import (
    DimensionSpec,
    DimaSemanticSpec,
    DisplaySpec,
    MetricSpec,
    SourceLineage,
    TimeSpec,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SemanticImportError(ValueError):
    pass


class SemanticImportGap(FrozenModel):
    code: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)
    detail: str = Field(min_length=1)


class SemanticImportResult(FrozenModel):
    source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    spec: DimaSemanticSpec
    gaps: tuple[SemanticImportGap, ...] = ()


class StructuredFieldDisposition(StrEnum):
    CONSUMED = "CONSUMED"
    GAP_OWNED = "GAP_OWNED"
    IGNORED_OPERATIONAL_METADATA = "IGNORED_OPERATIONAL_METADATA"


class StructuredFieldRule(FrozenModel):
    disposition: StructuredFieldDisposition
    gap_code: str | None = None
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def _gap_code_coherence(self):
        if (
            self.disposition == StructuredFieldDisposition.GAP_OWNED
            and self.gap_code is None
        ):
            raise ValueError("gap-owned structured field requires gap_code")
        if (
            self.disposition != StructuredFieldDisposition.GAP_OWNED
            and self.gap_code is not None
        ):
            raise ValueError("only gap-owned structured field may define gap_code")
        return self


def _consumed(rationale: str) -> StructuredFieldRule:
    return StructuredFieldRule(
        disposition=StructuredFieldDisposition.CONSUMED,
        rationale=rationale,
    )


def _gap(code: str, rationale: str) -> StructuredFieldRule:
    return StructuredFieldRule(
        disposition=StructuredFieldDisposition.GAP_OWNED,
        gap_code=code,
        rationale=rationale,
    )


def _operational(rationale: str) -> StructuredFieldRule:
    return StructuredFieldRule(
        disposition=StructuredFieldDisposition.IGNORED_OPERATIONAL_METADATA,
        rationale=rationale,
    )


# Exact-key ownership contract. A non-empty key absent from this table is never ignored:
# it becomes UNMAPPED_STRUCTURED_FIELD. This is a coverage guard, not a semantic parser.
_STRUCTURED_FIELD_RULES: dict[str, dict[str, StructuredFieldRule]] = {
    "top_level": {
        "models": _consumed("structured model collection"),
        "relationships": _consumed("structured relationship collection"),
        "cubes": _consumed("structured cube collection"),
        "views": _consumed("structured view collection"),
        "catalog": _operational(
            "global Wren namespace is not used as a fallback; canonical lineage comes from exact model tableReference"
        ),
        "schema": _operational(
            "global Wren namespace is not used as a fallback; canonical lineage comes from exact model tableReference"
        ),
        "dataSource": _operational("transport/runtime datasource metadata"),
        "layoutVersion": _operational("Wren layout/schema transport version"),
    },
    "model": {
        "name": _consumed("exact model identity"),
        "columns": _consumed("structured column collection"),
        "tableReference": _consumed("exact physical model lineage"),
        "primaryKey": _gap(
            "GRAIN_KEY_METADATA_GAP",
            "primary-key/grain metadata has no canonical Dima owner yet",
        ),
        "rowLevelAccessControls": _consumed(
            "dedicated P10 security gap logic owns row-level access metadata"
        ),
    },
    "table_reference": {
        "catalog": _consumed("exact physical catalog lineage"),
        "schema": _consumed("exact physical schema lineage"),
        "table": _consumed("exact physical table lineage"),
    },
    "column": {
        "name": _consumed("exact structured column identity"),
        "expression": _consumed(
            "observed only as opaque calculated-column metadata; never parsed"
        ),
        "isCalculated": _consumed(
            "drives explicit calculated-model-column typed gap"
        ),
        "type": _operational(
            "physical model-column type is not promoted to business meaning; semantic dimension type is owned by DimensionSpec"
        ),
        "notNull": _operational(
            "physical nullability constraint; catalog/resource concern, not Dima business meaning"
        ),
        "isPrimaryKey": _gap(
            "GRAIN_KEY_METADATA_GAP",
            "primary-key/grain metadata has no canonical Dima owner yet",
        ),
        "relationship": _gap(
            "RELATIONSHIP_METADATA_GAP",
            "column relationship metadata has no portable canonical relationship representation yet",
        ),
        "sensitivity": _gap(
            "SECURITY_METADATA_DEFERRED_TO_P10",
            "structured sensitivity metadata requires the P10 security owner",
        ),
        "columnLevelAccessControl": _consumed(
            "dedicated P10 security gap logic owns column access metadata"
        ),
    },
    "cube": {
        "name": _consumed("exact cube source identity"),
        "baseObject": _consumed("exact model/view base lookup"),
        "measures": _consumed("structured measure collection"),
        "dimensions": _consumed("structured dimension collection"),
        "timeDimensions": _consumed("structured time-dimension collection"),
        "label": _gap(
            "CUBE_SEMANTIC_ENTITY_GAP",
            "cube-level terminology has no canonical semantic-entity owner yet",
        ),
        "synonyms": _gap(
            "CUBE_SEMANTIC_ENTITY_GAP",
            "cube-level terminology has no canonical semantic-entity owner yet",
        ),
        "defaultMeasure": _gap(
            "CUBE_SEMANTIC_ENTITY_GAP",
            "cube default-measure behavior has no canonical semantic-entity owner yet",
        ),
        "ayniGrain": _gap(
            "CUBE_GRAIN_METADATA_GAP",
            "cube grain metadata has no canonical Dima representation yet",
        ),
        "departman": _gap(
            "CUBE_DOMAIN_METADATA_GAP",
            "cube domain metadata has no canonical Dima representation yet",
        ),
        "pvm": _gap(
            "CUBE_PVM_METADATA_GAP",
            "cube PVM metadata is preserved as an explicit representation gap",
        ),
    },
    "measure": {
        "name": _consumed("exact metric identity"),
        "expression": _consumed("opaque formula preservation; never parsed"),
        "label": _consumed("DisplaySpec label"),
        "synonyms": _consumed("MetricSpec aliases"),
        "unit": _consumed("MetricSpec unit"),
        "format": _consumed("MetricSpec format"),
        "grain": _consumed("MetricSpec grain when explicitly present"),
        "timeDimension": _consumed("MetricSpec time dimension when explicitly present"),
        "time_dimension": _consumed("MetricSpec time dimension compatibility spelling"),
        "aggregation": _consumed("explicit mechanical aggregation when present"),
        "additive": _consumed("exact explicit additivity token mapping"),
        "type": _gap(
            "METRIC_TYPE_METADATA_GAP",
            "Wren measure type has no canonical MetricSpec data-type field",
        ),
        "lowerIsBetter": _gap(
            "METRIC_DIRECTIONALITY_METADATA_GAP",
            "metric business directionality has no canonical owner yet",
        ),
        "nl": _gap(
            "METRIC_NL_METADATA_GAP",
            "metric natural-language metadata has no canonical owner yet",
        ),
    },
    "dimension": {
        "name": _consumed("exact dimension identity"),
        "expression": _consumed("exact-column lineage or explicit calculated-expression gap"),
        "label": _consumed("DisplaySpec label"),
        "synonyms": _consumed("DimensionSpec aliases"),
        "type": _consumed("DimensionSpec data_type"),
        "properties": _consumed("structured dimension properties audited separately"),
        "sensitivity": _gap(
            "SECURITY_METADATA_DEFERRED_TO_P10",
            "structured sensitivity metadata requires the P10 security owner",
        ),
    },
    "time": {
        "name": _consumed("exact time-dimension identity"),
        "expression": _consumed("exact-column lineage or explicit calculated-expression gap"),
        "label": _consumed("DisplaySpec label"),
        "synonyms": _consumed("DimensionSpec aliases"),
        "type": _consumed("DimensionSpec data_type"),
        "properties": _consumed("structured time properties audited separately"),
        "sensitivity": _gap(
            "SECURITY_METADATA_DEFERRED_TO_P10",
            "structured sensitivity metadata requires the P10 security owner",
        ),
        "calendar": _consumed("TimeSpec calendar"),
        "timezone": _consumed("TimeSpec timezone"),
        "grain": _consumed("TimeSpec grain"),
    },
    "dimension_properties": {
        "origin": _consumed("structured relationship-origin metadata audited separately"),
    },
    "origin": {
        "model": _consumed("exact origin model lookup"),
        "column": _consumed("exact origin column lookup"),
        "relationship": _gap(
            "RELATIONSHIP_METADATA_GAP",
            "origin relationship identity has no canonical relationship binding yet",
        ),
        "hops": _gap(
            "RELATIONSHIP_PATH_METADATA_GAP",
            "origin relationship-path depth has no canonical path representation yet",
        ),
    },
    "relationship": {
        "name": _consumed("exact relationship identity"),
        "models": _consumed("exact two-model relationship shape validation"),
        "condition": _consumed(
            "textual join condition is observed by RELATIONSHIP_JOIN_KEY_GAP logic but never parsed"
        ),
        "joinType": _gap(
            "RELATIONSHIP_CARDINALITY_METADATA_GAP",
            "Wren relationship cardinality has no portable RelationshipSpec without exact join keys",
        ),
        "expose": _gap(
            "RELATIONSHIP_EXPOSE_METADATA_GAP",
            "relationship expose metadata has no canonical portable representation yet",
        ),
    },
    "view": {
        "name": _consumed("exact view identity"),
        "statement": _consumed(
            "view definition is owned by VIEW_DEFINITION_GAP and never SQL-parsed"
        ),
        "columns": _gap(
            "VIEW_COLUMN_METADATA_GAP",
            "structured view-column metadata has no canonical portable lineage representation yet",
        ),
    },
}


def _has_structured_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    # False/0 are material explicit values and must be accounted for.
    return True


def _audit_structured_fields(
    node: dict[str, Any],
    *,
    node_type: str,
    source_ref: str,
    gaps: list[SemanticImportGap],
) -> None:
    rules = _STRUCTURED_FIELD_RULES.get(node_type)
    if rules is None:
        raise SemanticImportError(f"unknown structured field node type: {node_type}")

    for field_name in sorted(node):
        value = node[field_name]
        if not _has_structured_value(value):
            continue
        rule = rules.get(field_name)
        field_ref = f"{source_ref}.field:{field_name}"
        if rule is None:
            _add_gap(
                gaps,
                code="UNMAPPED_STRUCTURED_FIELD",
                source_ref=field_ref,
                detail=(
                    f"non-empty structured {node_type} field {field_name!r} "
                    "has no explicit consumed/gap/operational disposition"
                ),
            )
            continue
        if rule.disposition == StructuredFieldDisposition.GAP_OWNED:
            assert rule.gap_code is not None
            _add_gap(
                gaps,
                code=rule.gap_code,
                source_ref=field_ref,
                detail=rule.rationale,
            )


def _canonical_hash(value: Any) -> str:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise SemanticImportError(
            "Wren MDL input must be deterministic JSON"
        ) from exc
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _nonempty_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None


def _string_tuple(value: Any, *, field_ref: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise SemanticImportError(f"{field_ref} must be a list")
    output: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise SemanticImportError(
                f"{field_ref} must contain non-empty strings"
            )
        if item not in seen:
            output.append(item)
            seen.add(item)
    return tuple(output)


def _named_index(value: Any, *, owner: str) -> dict[str, dict[str, Any]]:
    if value is None:
        return {}
    if not isinstance(value, list):
        raise SemanticImportError(f"{owner} must be a list")
    output: dict[str, dict[str, Any]] = {}
    for item in value:
        if not isinstance(item, dict):
            raise SemanticImportError(f"{owner} entries must be objects")
        name = _nonempty_string(item.get("name"))
        if name is None:
            raise SemanticImportError(f"{owner} entry missing name")
        if name in output:
            raise SemanticImportError(f"duplicate {owner} name: {name}")
        output[name] = item
    return output


def _add_gap(
    gaps: list[SemanticImportGap],
    *,
    code: str,
    source_ref: str,
    detail: str,
) -> None:
    gaps.append(
        SemanticImportGap(
            code=code,
            source_ref=source_ref,
            detail=detail,
        )
    )


def _semantic_version(payload: Any) -> tuple[str, str]:
    compatibility_hash = _canonical_hash(payload)
    return compatibility_hash[:16], compatibility_hash


def _additive_kind(
    value: Any,
    *,
    source_ref: str,
    gaps: list[SemanticImportGap],
) -> str:
    if value is None:
        return "unknown"
    mapping = {
        "additive": "additive",
        "full": "additive",
        "semi": "semi_additive",
        "non": "non_additive",
    }
    if isinstance(value, str) and value in mapping:
        return mapping[value]
    _add_gap(
        gaps,
        code="UNSUPPORTED_ADDITIVITY_TOKEN",
        source_ref=source_ref,
        detail=f"unsupported explicit additivity token: {value!r}",
    )
    return "unknown"


def _model_lineage(
    model_name: str,
    model: dict[str, Any],
) -> SourceLineage:
    table_ref = model.get("tableReference")
    if not isinstance(table_ref, dict):
        table_ref = {}
    return SourceLineage(
        source_id=f"model:{model_name}",
        database_ref=_nonempty_string(table_ref.get("catalog")),
        schema_name=_nonempty_string(table_ref.get("schema")),
        table_name=_nonempty_string(table_ref.get("table")),
        column_name=None,
    )


def _column_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return _named_index(model.get("columns"), owner="model columns")


class WrenSemanticSpecImporter:
    """Pure structured importer. Formula/condition strings are never interpreted."""

    @classmethod
    def import_manifest(
        cls,
        manifest: dict[str, Any],
        *,
        semantic_context_version: str,
    ) -> SemanticImportResult:
        if not isinstance(manifest, dict):
            raise SemanticImportError("Wren MDL manifest must be an object")
        if not semantic_context_version.strip():
            raise SemanticImportError("semantic_context_version is required")

        source_fingerprint = _canonical_hash(manifest)
        gaps: list[SemanticImportGap] = []
        _audit_structured_fields(
            manifest,
            node_type="top_level",
            source_ref="manifest",
            gaps=gaps,
        )
        models = _named_index(manifest.get("models"), owner="models")
        views = _named_index(manifest.get("views"), owner="views")
        cubes = _named_index(manifest.get("cubes"), owner="cubes")
        relationships = _named_index(
            manifest.get("relationships"),
            owner="relationships",
        )

        metrics: list[MetricSpec] = []
        dimensions: list[DimensionSpec] = []
        time_specs: list[TimeSpec] = []
        display_specs: list[DisplaySpec] = []

        for model_name, model in models.items():
            _audit_structured_fields(
                model,
                node_type="model",
                source_ref=f"model:{model_name}",
                gaps=gaps,
            )
            table_ref = model.get("tableReference")
            if isinstance(table_ref, dict):
                _audit_structured_fields(
                    table_ref,
                    node_type="table_reference",
                    source_ref=f"model:{model_name}.tableReference",
                    gaps=gaps,
                )
            for column_name, column in _column_index(model).items():
                _audit_structured_fields(
                    column,
                    node_type="column",
                    source_ref=f"model:{model_name}.column:{column_name}",
                    gaps=gaps,
                )
                if bool(column.get("isCalculated")):
                    _add_gap(
                        gaps,
                        code="CALCULATED_MODEL_COLUMN_GAP",
                        source_ref=f"model:{model_name}.column:{column_name}",
                        detail=(
                            "calculated model-column expression is opaque in "
                            "the initial DimaSemanticSpec importer"
                        ),
                    )
                if column.get("columnLevelAccessControl") is not None:
                    _add_gap(
                        gaps,
                        code="COLUMN_SECURITY_DEFERRED_TO_P10",
                        source_ref=f"model:{model_name}.column:{column_name}",
                        detail="column-level access metadata is owned by P10",
                    )
            if model.get("rowLevelAccessControls"):
                _add_gap(
                    gaps,
                    code="ROW_SECURITY_DEFERRED_TO_P10",
                    source_ref=f"model:{model_name}",
                    detail="row-level access metadata is owned by P10",
                )

        for view_name, view in views.items():
            _audit_structured_fields(
                view,
                node_type="view",
                source_ref=f"view:{view_name}",
                gaps=gaps,
            )
            _add_gap(
                gaps,
                code="VIEW_DEFINITION_GAP",
                source_ref=f"view:{view_name}",
                detail=(
                    "view SQL statement is intentionally not parsed by the "
                    "initial structured importer"
                ),
            )

        for relationship_name, relationship in relationships.items():
            _audit_structured_fields(
                relationship,
                node_type="relationship",
                source_ref=f"relationship:{relationship_name}",
                gaps=gaps,
            )
            model_refs = relationship.get("models")
            if not (
                isinstance(model_refs, list)
                and len(model_refs) == 2
                and all(
                    isinstance(item, str) and item.strip()
                    for item in model_refs
                )
            ):
                _add_gap(
                    gaps,
                    code="RELATIONSHIP_SHAPE_GAP",
                    source_ref=f"relationship:{relationship_name}",
                    detail="relationship models must be an exact two-item string list",
                )
            else:
                _add_gap(
                    gaps,
                    code="RELATIONSHIP_JOIN_KEY_GAP",
                    source_ref=f"relationship:{relationship_name}",
                    detail=(
                        "current Wren relationship exposes textual condition, "
                        "not structured join keys; condition text is not parsed"
                    ),
                )

        for cube_name, cube in cubes.items():
            _audit_structured_fields(
                cube,
                node_type="cube",
                source_ref=f"cube:{cube_name}",
                gaps=gaps,
            )
            base_object = _nonempty_string(cube.get("baseObject"))
            base_lineage: tuple[SourceLineage, ...] = ()
            base_columns: dict[str, dict[str, Any]] = {}

            if base_object is None:
                _add_gap(
                    gaps,
                    code="CUBE_BASE_OBJECT_MISSING",
                    source_ref=f"cube:{cube_name}",
                    detail="cube has no structured baseObject",
                )
            elif base_object in models:
                base_model = models[base_object]
                base_lineage = (
                    _model_lineage(base_object, base_model),
                )
                base_columns = _column_index(base_model)
                if base_lineage[0].table_name is None:
                    _add_gap(
                        gaps,
                        code="MODEL_TABLE_REFERENCE_GAP",
                        source_ref=f"model:{base_object}",
                        detail="base model has no physical tableReference.table",
                    )
            elif base_object in views:
                base_lineage = (
                    SourceLineage(source_id=f"view:{base_object}"),
                )
                _add_gap(
                    gaps,
                    code="VIEW_PHYSICAL_LINEAGE_GAP",
                    source_ref=f"cube:{cube_name}",
                    detail=(
                        f"baseObject {base_object!r} is a view; view SQL is "
                        "not parsed for physical lineage"
                    ),
                )
            else:
                _add_gap(
                    gaps,
                    code="BASE_OBJECT_NOT_FOUND",
                    source_ref=f"cube:{cube_name}",
                    detail=f"baseObject {base_object!r} is absent from models/views",
                )

            measure_index = _named_index(
                cube.get("measures"),
                owner=f"cube:{cube_name}.measures",
            )
            for measure_name, measure in measure_index.items():
                source_ref = f"cube:{cube_name}.measure:{measure_name}"
                _audit_structured_fields(
                    measure,
                    node_type="measure",
                    source_ref=source_ref,
                    gaps=gaps,
                )
                aliases = _string_tuple(
                    measure.get("synonyms"),
                    field_ref=f"{source_ref}.synonyms",
                )
                formula = _nonempty_string(measure.get("expression"))
                explicit_aggregation = _nonempty_string(
                    measure.get("aggregation")
                )
                aggregation = (
                    explicit_aggregation
                    or ("expression" if formula is not None else "unknown")
                )
                if formula is None and explicit_aggregation is None:
                    _add_gap(
                        gaps,
                        code="METRIC_SEMANTICS_MISSING",
                        source_ref=source_ref,
                        detail="metric has neither expression nor aggregation",
                    )

                additive_kind = _additive_kind(
                    measure.get("additive"),
                    source_ref=source_ref,
                    gaps=gaps,
                )
                unit = _nonempty_string(measure.get("unit"))
                fmt = _nonempty_string(measure.get("format"))
                grain = _nonempty_string(measure.get("grain"))
                time_dimension = (
                    _nonempty_string(measure.get("timeDimension"))
                    or _nonempty_string(measure.get("time_dimension"))
                )
                metric_id = f"metric.{cube_name}.{measure_name}"
                payload = {
                    "metric_id": metric_id,
                    "name": measure_name,
                    "aliases": aliases,
                    "formula": formula,
                    "aggregation": aggregation,
                    "unit": unit,
                    "format": fmt,
                    "grain": grain,
                    "additive_kind": additive_kind,
                    "time_dimension": time_dimension,
                    "source_lineage": [
                        item.model_dump(mode="json")
                        for item in base_lineage
                    ],
                }
                semantic_version, compatibility_hash = _semantic_version(
                    payload
                )
                metrics.append(
                    MetricSpec(
                        metric_id=metric_id,
                        name=measure_name,
                        aliases=aliases,
                        formula=formula,
                        aggregation=aggregation,
                        unit=unit,
                        format=fmt,
                        grain=grain,
                        additive_kind=additive_kind,
                        time_dimension=time_dimension,
                        provenance=(source_ref,),
                        semantic_version=semantic_version,
                        compatibility_hash=compatibility_hash,
                        source_lineage=base_lineage,
                    )
                )
                label = _nonempty_string(measure.get("label"))
                if any(value is not None for value in (label, unit, fmt)):
                    display_specs.append(
                        DisplaySpec(
                            semantic_ref=metric_id,
                            label=label,
                            unit=unit,
                            format=fmt,
                        )
                    )

            dimension_index = _named_index(
                cube.get("dimensions"),
                owner=f"cube:{cube_name}.dimensions",
            )
            time_index = _named_index(
                cube.get("timeDimensions"),
                owner=f"cube:{cube_name}.timeDimensions",
            )

            for dimension_name, dimension in (
                *dimension_index.items(),
                *time_index.items(),
            ):
                is_time = dimension_name in time_index
                source_kind = "time" if is_time else "dimension"
                source_ref = (
                    f"cube:{cube_name}.{source_kind}:{dimension_name}"
                )
                _audit_structured_fields(
                    dimension,
                    node_type="time" if is_time else "dimension",
                    source_ref=source_ref,
                    gaps=gaps,
                )
                dimension_id = f"dimension.{cube_name}.{dimension_name}"
                aliases = _string_tuple(
                    dimension.get("synonyms"),
                    field_ref=f"{source_ref}.synonyms",
                )
                data_type = (
                    _nonempty_string(dimension.get("type")) or "unknown"
                )
                if data_type == "unknown":
                    _add_gap(
                        gaps,
                        code="DIMENSION_TYPE_MISSING",
                        source_ref=source_ref,
                        detail="dimension has no explicit type",
                    )

                lineage = base_lineage
                properties = dimension.get("properties")
                if isinstance(properties, dict):
                    _audit_structured_fields(
                        properties,
                        node_type="dimension_properties",
                        source_ref=f"{source_ref}.properties",
                        gaps=gaps,
                    )
                origin = (
                    properties.get("origin")
                    if isinstance(properties, dict)
                    else None
                )
                if isinstance(origin, dict):
                    _audit_structured_fields(
                        origin,
                        node_type="origin",
                        source_ref=f"{source_ref}.properties.origin",
                        gaps=gaps,
                    )
                if isinstance(origin, dict):
                    origin_model_name = _nonempty_string(origin.get("model"))
                    origin_column_name = _nonempty_string(origin.get("column"))
                    if (
                        origin_model_name in models
                        and origin_column_name is not None
                        and origin_column_name
                        in _column_index(models[origin_model_name])
                    ):
                        origin_lineage = _model_lineage(
                            origin_model_name,
                            models[origin_model_name],
                        )
                        lineage = (
                            origin_lineage.model_copy(
                                update={"column_name": origin_column_name}
                            ),
                        )
                    else:
                        _add_gap(
                            gaps,
                            code="ORIGIN_LINEAGE_GAP",
                            source_ref=source_ref,
                            detail=(
                                "structured origin model/column cannot be "
                                "resolved exactly"
                            ),
                        )
                else:
                    expression = _nonempty_string(
                        dimension.get("expression")
                    )
                    if (
                        expression is not None
                        and expression in base_columns
                        and base_lineage
                    ):
                        column = base_columns[expression]
                        if bool(column.get("isCalculated")):
                            _add_gap(
                                gaps,
                                code="CALCULATED_DIMENSION_LINEAGE_GAP",
                                source_ref=source_ref,
                                detail=(
                                    "dimension references a calculated model "
                                    "column; expression is not parsed"
                                ),
                            )
                        else:
                            lineage = (
                                base_lineage[0].model_copy(
                                    update={"column_name": expression}
                                ),
                            )
                    elif expression is not None:
                        _add_gap(
                            gaps,
                            code="CALCULATED_DIMENSION_EXPRESSION_GAP",
                            source_ref=source_ref,
                            detail=(
                                "dimension expression is not an exact "
                                "base-model column; expression is not parsed"
                            ),
                        )

                dim_payload = {
                    "dimension_id": dimension_id,
                    "name": dimension_name,
                    "aliases": aliases,
                    "data_type": data_type,
                    "source_lineage": [
                        item.model_dump(mode="json")
                        for item in lineage
                    ],
                }
                semantic_version, _ = _semantic_version(dim_payload)
                dimensions.append(
                    DimensionSpec(
                        dimension_id=dimension_id,
                        name=dimension_name,
                        aliases=aliases,
                        data_type=data_type,
                        semantic_version=semantic_version,
                        source_lineage=lineage,
                    )
                )
                label = _nonempty_string(dimension.get("label"))
                if label is not None:
                    display_specs.append(
                        DisplaySpec(
                            semantic_ref=dimension_id,
                            label=label,
                        )
                    )
                if is_time:
                    time_specs.append(
                        TimeSpec(
                            time_id=f"time.{cube_name}.{dimension_name}",
                            dimension_ref=dimension_id,
                            calendar=(
                                _nonempty_string(
                                    dimension.get("calendar")
                                )
                                or "gregorian"
                            ),
                            timezone=_nonempty_string(
                                dimension.get("timezone")
                            ),
                            grain=_nonempty_string(
                                dimension.get("grain")
                            ),
                        )
                    )

        spec = DimaSemanticSpec(
            semantic_context_version=semantic_context_version,
            metrics=tuple(metrics),
            dimensions=tuple(dimensions),
            relationships=(),
            time_specs=tuple(time_specs),
            display_specs=tuple(display_specs),
        )
        return SemanticImportResult(
            source_fingerprint=source_fingerprint,
            spec=spec,
            gaps=tuple(gaps),
        )
