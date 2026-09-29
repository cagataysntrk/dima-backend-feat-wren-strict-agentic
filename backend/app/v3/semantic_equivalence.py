"""P8 provider-free semantic equivalence matrix.

Classifications are derived only from typed Dima/P7 state and the certified P4 capability
boundary. No formula SQL, relationship condition, display name, or raw language is parsed.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.semantic_import import SemanticImportGap, SemanticImportResult
from app.v3.semantic_spec import (
    DimensionSpec,
    DimaSemanticSpec,
    MetricSpec,
    RelationshipSpec,
)
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SemanticEquivalenceError(RuntimeError):
    pass


class EquivalenceClassification(StrEnum):
    NATIVE_METABASE = "NATIVE_METABASE"
    DIMA_COMPILED = "DIMA_COMPILED"
    DIMA_RUNTIME = "DIMA_RUNTIME"
    WREN_ONLY_GAP = "WREN_ONLY_GAP"
    UNSUPPORTED = "UNSUPPORTED"


class DimaRepresentationState(StrEnum):
    REPRESENTED = "REPRESENTED"
    TYPED_GAP = "TYPED_GAP"


class SemanticEquivalenceRow(FrozenModel):
    feature_ref: str = Field(min_length=1)
    feature_kind: str = Field(min_length=1)
    dima_state: DimaRepresentationState
    classification: EquivalenceClassification
    reason_code: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()


class SemanticEquivalenceMatrix(FrozenModel):
    source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    rows: tuple[SemanticEquivalenceRow, ...]
    matrix_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def _unique_rows(self):
        keys = [
            (item.feature_kind, item.feature_ref, item.reason_code)
            for item in self.rows
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate semantic equivalence row")
        return self


def _fingerprint(
    *,
    source_fingerprint: str,
    rows: tuple[SemanticEquivalenceRow, ...],
) -> str:
    raw = json.dumps(
        {
            "source_fingerprint": source_fingerprint,
            "rows": [item.model_dump(mode="json") for item in rows],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _exact_lineage(item: MetricSpec | DimensionSpec, *, require_column: bool) -> bool:
    if len(item.source_lineage) != 1:
        return False
    lineage = item.source_lineage[0]
    if not lineage.database_ref or not lineage.table_name:
        return False
    if require_column and not lineage.column_name:
        return False
    return True


_RUNTIME_GAP_CODES = frozenset(
    {
        "CUBE_SEMANTIC_ENTITY_GAP",
        "COLUMN_SECURITY_DEFERRED_TO_P10",
        "ROW_SECURITY_DEFERRED_TO_P10",
        "SECURITY_METADATA_DEFERRED_TO_P10",
        "METRIC_DIRECTIONALITY_METADATA_GAP",
        "METRIC_NL_METADATA_GAP",
        "CUBE_DOMAIN_METADATA_GAP",
    }
)

_WREN_ONLY_GAP_CODES = frozenset(
    {
        "CALCULATED_MODEL_COLUMN_GAP",
        "CALCULATED_DIMENSION_LINEAGE_GAP",
        "CALCULATED_DIMENSION_EXPRESSION_GAP",
        "RELATIONSHIP_JOIN_KEY_GAP",
        "VIEW_DEFINITION_GAP",
        "VIEW_PHYSICAL_LINEAGE_GAP",
        "GRAIN_KEY_METADATA_GAP",
        "RELATIONSHIP_METADATA_GAP",
        "RELATIONSHIP_PATH_METADATA_GAP",
        "RELATIONSHIP_CARDINALITY_METADATA_GAP",
        "RELATIONSHIP_EXPOSE_METADATA_GAP",
        "METRIC_TYPE_METADATA_GAP",
        "CUBE_GRAIN_METADATA_GAP",
        "CUBE_PVM_METADATA_GAP",
        "VIEW_COLUMN_METADATA_GAP",
    }
)

_UNSUPPORTED_GAP_CODES = frozenset(
    {
        "RELATIONSHIP_SHAPE_GAP",
        "CUBE_BASE_OBJECT_MISSING",
        "BASE_OBJECT_NOT_FOUND",
        "MODEL_TABLE_REFERENCE_GAP",
        "ORIGIN_LINEAGE_GAP",
        "METRIC_SEMANTICS_MISSING",
        "DIMENSION_TYPE_MISSING",
        "UNSUPPORTED_ADDITIVITY_TOKEN",
    }
)


def _gap_classification(gap: SemanticImportGap) -> EquivalenceClassification:
    if gap.code in _RUNTIME_GAP_CODES:
        return EquivalenceClassification.DIMA_RUNTIME
    if gap.code in _WREN_ONLY_GAP_CODES:
        return EquivalenceClassification.WREN_ONLY_GAP
    if gap.code in _UNSUPPORTED_GAP_CODES:
        return EquivalenceClassification.UNSUPPORTED
    raise SemanticEquivalenceError(
        f"unknown P7 semantic import gap code: {gap.code}"
    )


class SemanticEquivalenceMatrixBuilder:
    """Build one deterministic conservative P8 capability matrix."""

    @staticmethod
    def _metric_row(metric: MetricSpec) -> SemanticEquivalenceRow:
        evidence = tuple(
            dict.fromkeys(
                (
                    *metric.provenance,
                    *(item.source_id for item in metric.source_lineage),
                )
            )
        )
        if metric.formula is not None:
            classification = EquivalenceClassification.WREN_ONLY_GAP
            reason = "OPAQUE_METRIC_FORMULA_NOT_STRUCTURALLY_EQUIVALENT"
        else:
            aggregation = metric.aggregation.strip().lower()
            p4_supported = aggregation in MetabaseProjectionCompiler._AGGREGATIONS
            require_column = (
                MetabaseProjectionCompiler._AGGREGATIONS.get(aggregation)
                != "count"
            )
            if p4_supported and _exact_lineage(
                metric,
                require_column=require_column,
            ):
                classification = EquivalenceClassification.NATIVE_METABASE
                reason = "P4_MECHANICAL_AGGREGATION_WITH_EXACT_LINEAGE"
            elif not p4_supported:
                classification = EquivalenceClassification.WREN_ONLY_GAP
                reason = "P4_MECHANICAL_AGGREGATION_UNSUPPORTED"
            else:
                classification = EquivalenceClassification.WREN_ONLY_GAP
                reason = "METRIC_PHYSICAL_LINEAGE_INCOMPLETE"
        return SemanticEquivalenceRow(
            feature_ref=metric.metric_id,
            feature_kind="metric",
            dima_state=DimaRepresentationState.REPRESENTED,
            classification=classification,
            reason_code=reason,
            evidence_refs=evidence,
        )

    @staticmethod
    def _dimension_row(
        dimension: DimensionSpec,
    ) -> SemanticEquivalenceRow:
        native = _exact_lineage(dimension, require_column=True)
        return SemanticEquivalenceRow(
            feature_ref=dimension.dimension_id,
            feature_kind="dimension",
            dima_state=DimaRepresentationState.REPRESENTED,
            classification=(
                EquivalenceClassification.NATIVE_METABASE
                if native
                else EquivalenceClassification.WREN_ONLY_GAP
            ),
            reason_code=(
                "EXACT_PHYSICAL_DIMENSION_LINEAGE"
                if native
                else "DIMENSION_PHYSICAL_LINEAGE_INCOMPLETE"
            ),
            evidence_refs=tuple(
                item.source_id for item in dimension.source_lineage
            ),
        )

    @staticmethod
    def _relationship_row(
        relationship: RelationshipSpec,
    ) -> SemanticEquivalenceRow:
        return SemanticEquivalenceRow(
            feature_ref=relationship.relationship_id,
            feature_kind="relationship",
            dima_state=DimaRepresentationState.REPRESENTED,
            classification=EquivalenceClassification.DIMA_COMPILED,
            reason_code="STRUCTURED_DIMA_RELATIONSHIP_REQUIRES_COMPILER",
            evidence_refs=tuple(
                f"{item.left_ref}->{item.right_ref}"
                for item in relationship.join_keys
            ),
        )

    @staticmethod
    def _time_rows(
        spec: DimaSemanticSpec,
    ) -> list[SemanticEquivalenceRow]:
        dimensions = {
            item.dimension_id: item
            for item in spec.dimensions
        }
        rows: list[SemanticEquivalenceRow] = []
        for time in spec.time_specs:
            dimension = dimensions.get(time.dimension_ref)
            if dimension is None:
                raise SemanticEquivalenceError(
                    f"time spec {time.time_id} references unknown dimension"
                )
            native = _exact_lineage(
                dimension,
                require_column=True,
            )
            rows.append(
                SemanticEquivalenceRow(
                    feature_ref=time.time_id,
                    feature_kind="time",
                    dima_state=DimaRepresentationState.REPRESENTED,
                    classification=(
                        EquivalenceClassification.NATIVE_METABASE
                        if native
                        else EquivalenceClassification.WREN_ONLY_GAP
                    ),
                    reason_code=(
                        "EXACT_PHYSICAL_TIME_LINEAGE"
                        if native
                        else "TIME_PHYSICAL_LINEAGE_INCOMPLETE"
                    ),
                    evidence_refs=(time.dimension_ref,),
                )
            )
        return rows

    @staticmethod
    def _gap_row(gap: SemanticImportGap) -> SemanticEquivalenceRow:
        classification = _gap_classification(gap)
        return SemanticEquivalenceRow(
            feature_ref=f"{gap.source_ref}#gap:{gap.code}",
            feature_kind="import_gap",
            dima_state=DimaRepresentationState.TYPED_GAP,
            classification=classification,
            reason_code=gap.code,
            evidence_refs=(gap.source_ref,),
        )

    @classmethod
    def build(
        cls,
        import_result: SemanticImportResult,
    ) -> SemanticEquivalenceMatrix:
        rows: list[SemanticEquivalenceRow] = []
        rows.extend(
            cls._metric_row(item)
            for item in import_result.spec.metrics
        )
        rows.extend(
            cls._dimension_row(item)
            for item in import_result.spec.dimensions
        )
        rows.extend(
            cls._relationship_row(item)
            for item in import_result.spec.relationships
        )
        rows.extend(cls._time_rows(import_result.spec))
        rows.extend(
            cls._gap_row(item)
            for item in import_result.gaps
        )
        ordered = tuple(
            sorted(
                rows,
                key=lambda item: (
                    item.feature_kind,
                    item.feature_ref,
                    item.reason_code,
                ),
            )
        )
        return SemanticEquivalenceMatrix(
            source_fingerprint=import_result.source_fingerprint,
            rows=ordered,
            matrix_fingerprint=_fingerprint(
                source_fingerprint=import_result.source_fingerprint,
                rows=ordered,
            ),
        )
