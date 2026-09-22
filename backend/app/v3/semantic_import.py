"""P7 structured Wren MDL -> DimaSemanticSpec importer.

The importer consumes an already-composed MDL mapping. It never resolves user language,
searches a substrate, parses SQL/formula text, or reimplements pack/customer composition.
Unsupported source richness is surfaced as typed import gaps.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

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
        models = _named_index(manifest.get("models"), owner="models")
        views = _named_index(manifest.get("views"), owner="views")
        cubes = _named_index(manifest.get("cubes"), owner="cubes")
        relationships = _named_index(
            manifest.get("relationships"),
            owner="relationships",
        )

        gaps: list[SemanticImportGap] = []
        metrics: list[MetricSpec] = []
        dimensions: list[DimensionSpec] = []
        time_specs: list[TimeSpec] = []
        display_specs: list[DisplaySpec] = []

        for model_name, model in models.items():
            for column_name, column in _column_index(model).items():
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

        for view_name in views:
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

            cube_unowned = [
                key
                for key in ("label", "synonyms", "defaultMeasure")
                if cube.get(key) not in (None, [], "")
            ]
            if cube_unowned:
                _add_gap(
                    gaps,
                    code="CUBE_SEMANTIC_ENTITY_GAP",
                    source_ref=f"cube:{cube_name}",
                    detail=(
                        "current DimaSemanticSpec has no cube semantic entity "
                        f"for fields: {', '.join(cube_unowned)}"
                    ),
                )

            measure_index = _named_index(
                cube.get("measures"),
                owner=f"cube:{cube_name}.measures",
            )
            for measure_name, measure in measure_index.items():
                source_ref = f"cube:{cube_name}.measure:{measure_name}"
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
                origin = (
                    properties.get("origin")
                    if isinstance(properties, dict)
                    else None
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
