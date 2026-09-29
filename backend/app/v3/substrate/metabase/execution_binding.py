"""Production Dima-owned execution bindings for the Metabase substrate.

This module promotes the P3A seam into one production contract. Context-bound semantic
candidate ids are lookup keys only; durable semantic identity stays in DimaSemanticSpec.
Physical locators are accepted only after exact SourceLineage/current-catalog agreement.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.semantic_spec import DimaSemanticSpec, SourceLineage


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MetabaseCompilationBlocked(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class CandidateSemanticBinding(FrozenModel):
    candidate_id: str = Field(min_length=1)
    semantic_id: str = Field(min_length=1)
    kind: Literal["metric", "dimension", "filter"]


class TemporalSemanticBinding(FrozenModel):
    compatibility_key: str = Field(min_length=1)
    dimension_id: str = Field(min_length=1)


class CurrentCatalogObject(FrozenModel):
    """Current physical object identity under a known Dima source_id."""

    source_id: str = Field(min_length=1)
    database_ref: str = Field(min_length=1)
    schema_name: str | None = None
    table_name: str = Field(min_length=1)
    column_name: str | None = None
    resource_entity_id: str | None = None
    resource_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    metabase_database_id: int | None = Field(default=None, ge=1)
    metabase_table_id: int | None = Field(default=None, ge=1)
    metabase_field_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _physical_locator_integrity(self):
        if self.metabase_field_id is not None and (
            self.metabase_database_id is None or self.metabase_table_id is None
        ):
            raise ValueError("Metabase field identity requires database and table ids")
        if self.metabase_table_id is not None and self.metabase_database_id is None:
            raise ValueError("Metabase table identity requires database id")
        return self

    @property
    def portable_table(self) -> tuple[str, str | None, str]:
        return (self.database_ref, self.schema_name, self.table_name)

    @property
    def portable_field(self) -> tuple[str, str | None, str, str]:
        if self.column_name is None:
            raise MetabaseCompilationBlocked(
                "CATALOG_OBJECT_HAS_NO_COLUMN",
                f"{self.source_id} has no current column binding",
            )
        return (
            self.database_ref,
            self.schema_name,
            self.table_name,
            self.column_name,
        )


class CurrentCatalogSnapshot(FrozenModel):
    catalog_version: str = Field(min_length=1)
    objects: tuple[CurrentCatalogObject, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_source_ids(self):
        ids = [item.source_id for item in self.objects]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate current catalog source_id")
        return self

    @property
    def fingerprint(self) -> str:
        raw = json.dumps(
            {
                "catalog_version": self.catalog_version,
                "objects": [
                    item.model_dump(mode="json")
                    for item in sorted(self.objects, key=lambda value: value.source_id)
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def object_for(self, source_id: str) -> CurrentCatalogObject:
        for item in self.objects:
            if item.source_id == source_id:
                return item
        raise MetabaseCompilationBlocked(
            "CURRENT_CATALOG_BINDING_MISSING",
            f"no current catalog object for Dima source_id {source_id}",
        )

    def object_for_metabase_table(
        self,
        *,
        database_id: int,
        table_id: int,
    ) -> CurrentCatalogObject:
        matches = [
            item
            for item in self.objects
            if item.metabase_database_id == database_id
            and item.metabase_table_id == table_id
            and item.column_name is None
        ]
        if len(matches) != 1:
            raise MetabaseCompilationBlocked(
                "CURRENT_CATALOG_METABASE_TABLE_BINDING_INVALID",
                f"Metabase database/table {database_id}/{table_id} maps to {len(matches)} Dima table objects",
            )
        return matches[0]

    def object_for_metabase_field(
        self,
        *,
        database_id: int,
        field_id: int,
    ) -> CurrentCatalogObject:
        matches = [
            item
            for item in self.objects
            if item.metabase_database_id == database_id
            and item.metabase_field_id == field_id
        ]
        if len(matches) != 1:
            raise MetabaseCompilationBlocked(
                "CURRENT_CATALOG_METABASE_FIELD_BINDING_INVALID",
                f"Metabase database/field {database_id}/{field_id} maps to {len(matches)} Dima field objects",
            )
        return matches[0]


class DimaExecutionBindingSnapshot(FrozenModel):
    """Immutable execution snapshot for one Dima semantic context."""

    semantic_context_version: str = Field(min_length=1)
    semantic_spec: DimaSemanticSpec
    candidate_bindings: tuple[CandidateSemanticBinding, ...] = ()
    temporal_bindings: tuple[TemporalSemanticBinding, ...] = ()
    current_catalog: CurrentCatalogSnapshot

    @model_validator(mode="after")
    def _integrity(self):
        if self.semantic_spec.semantic_context_version != self.semantic_context_version:
            raise ValueError("semantic spec/snapshot context mismatch")

        candidate_ids = [item.candidate_id for item in self.candidate_bindings]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("duplicate candidate binding")

        temporal_keys = [item.compatibility_key for item in self.temporal_bindings]
        if len(temporal_keys) != len(set(temporal_keys)):
            raise ValueError("duplicate temporal compatibility binding")

        metric_ids = {item.metric_id for item in self.semantic_spec.metrics}
        dimension_ids = {item.dimension_id for item in self.semantic_spec.dimensions}
        for item in self.candidate_bindings:
            if item.kind == "metric" and item.semantic_id not in metric_ids:
                raise ValueError("candidate metric binding references unknown Dima metric")
            if item.kind in {"dimension", "filter"} and item.semantic_id not in dimension_ids:
                raise ValueError("candidate dimension/filter binding references unknown Dima dimension")
        for item in self.temporal_bindings:
            if item.dimension_id not in dimension_ids:
                raise ValueError("temporal binding references unknown Dima dimension")
        return self

    def candidate(self, candidate_id: str, *, kind: str) -> str:
        for item in self.candidate_bindings:
            if item.candidate_id == candidate_id and item.kind == kind:
                return item.semantic_id
        raise MetabaseCompilationBlocked(
            "MISSING_STABLE_CANDIDATE_BINDING",
            f"no Dima-owned {kind} binding for candidate {candidate_id}",
        )

    def temporal_dimension(self, compatibility_key: str) -> str:
        for item in self.temporal_bindings:
            if item.compatibility_key == compatibility_key:
                return item.dimension_id
        raise MetabaseCompilationBlocked(
            "MISSING_STABLE_TIME_BINDING",
            "time dimension has no explicit Dima-owned compatibility binding",
        )

    def current_lineage(self, lineage: SourceLineage) -> CurrentCatalogObject:
        if not lineage.database_ref or not lineage.table_name:
            raise MetabaseCompilationBlocked(
                "INCOMPLETE_SOURCE_LINEAGE",
                f"{lineage.source_id} lacks explicit database/table lineage",
            )
        current = self.current_catalog.object_for(lineage.source_id)
        expected = (
            lineage.database_ref,
            lineage.schema_name,
            lineage.table_name,
            lineage.column_name,
        )
        observed = (
            current.database_ref,
            current.schema_name,
            current.table_name,
            current.column_name,
        )
        if expected != observed:
            raise MetabaseCompilationBlocked(
                "SOURCE_LINEAGE_DRIFT",
                f"{lineage.source_id} expected {expected!r}, current {observed!r}",
            )
        return current
