"""Engine-independent canonical semantic contract shells for Dima v3.

M1 defines ownership and stable shapes. Wren MDL import and full semantic-equivalence
work remain P7/P8; no substrate-specific object is authoritative here.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceLineage(FrozenModel):
    """Portable source provenance. Physical names are data, never semantic authority."""

    source_id: str = Field(min_length=1)
    database_ref: str | None = None
    schema_name: str | None = None
    table_name: str | None = None
    column_name: str | None = None


class MetricSpec(FrozenModel):
    metric_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    formula: str | None = None
    aggregation: str = Field(min_length=1)
    unit: str | None = None
    format: str | None = None
    grain: str | None = None
    additive_kind: Literal["additive", "semi_additive", "non_additive", "unknown"] = "unknown"
    time_dimension: str | None = None
    provenance: tuple[str, ...] = ()
    semantic_version: str = Field(min_length=1)
    compatibility_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_lineage: tuple[SourceLineage, ...] = ()


class DimensionSpec(FrozenModel):
    dimension_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    data_type: str = Field(min_length=1)
    entity_value_policy: str | None = None
    sensitivity_policy: str | None = None
    cardinality_policy: str | None = None
    semantic_version: str = Field(min_length=1)
    source_lineage: tuple[SourceLineage, ...] = ()


class JoinKeySpec(FrozenModel):
    left_ref: str = Field(min_length=1)
    right_ref: str = Field(min_length=1)


class RelationshipSpec(FrozenModel):
    relationship_id: str = Field(min_length=1)
    from_ref: str = Field(min_length=1)
    to_ref: str = Field(min_length=1)
    cardinality: str = Field(min_length=1)
    join_keys: tuple[JoinKeySpec, ...] = Field(min_length=1)
    allowed_grains: tuple[str, ...] = ()
    path_policy: str | None = None
    semantic_version: str = Field(min_length=1)


class TimeSpec(FrozenModel):
    time_id: str = Field(min_length=1)
    dimension_ref: str = Field(min_length=1)
    calendar: str = "gregorian"
    timezone: str | None = None
    grain: str | None = None


class BusinessRule(FrozenModel):
    rule_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    semantic_refs: tuple[str, ...] = ()


class DisplaySpec(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    label: str | None = None
    unit: str | None = None
    format: str | None = None


class SecurityTag(FrozenModel):
    tag_id: str = Field(min_length=1)
    semantic_ref: str = Field(min_length=1)
    policy: str = Field(min_length=1)


class ManagedResourcePolicy(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    ownership: Literal["DIMA_MANAGED", "USER_MANAGED", "EXTERNAL"]
    reconciliation: Literal["OVERWRITE", "REJECT", "IMPORT_AS_NEW_VERSION"] | None = None


class DimaSemanticSpec(FrozenModel):
    """Dima-owned business meaning; no Wren or Metabase identity is canonical."""

    spec_version: Literal["dima-semantic-v1"] = "dima-semantic-v1"
    semantic_context_version: str = Field(min_length=1)
    metrics: tuple[MetricSpec, ...] = ()
    dimensions: tuple[DimensionSpec, ...] = ()
    relationships: tuple[RelationshipSpec, ...] = ()
    time_specs: tuple[TimeSpec, ...] = ()
    business_rules: tuple[BusinessRule, ...] = ()
    display_specs: tuple[DisplaySpec, ...] = ()
    security_tags: tuple[SecurityTag, ...] = ()
    managed_resources: tuple[ManagedResourcePolicy, ...] = ()

    @model_validator(mode="after")
    def _unique_ids(self):
        groups = {
            "metric": [item.metric_id for item in self.metrics],
            "dimension": [item.dimension_id for item in self.dimensions],
            "relationship": [item.relationship_id for item in self.relationships],
            "time": [item.time_id for item in self.time_specs],
            "business_rule": [item.rule_id for item in self.business_rules],
            "security_tag": [item.tag_id for item in self.security_tags],
        }
        for name, values in groups.items():
            if len(values) != len(set(values)):
                raise ValueError(f"duplicate {name} id")
        return self
