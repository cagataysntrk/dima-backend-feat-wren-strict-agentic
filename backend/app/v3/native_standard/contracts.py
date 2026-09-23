"""P13B/P13C native Standard attestation contracts.

These models mirror bounded facts emitted by the certified Dima Metabase engine seam.
They carry observed execution/provenance only; Dima semantic authority lives elsewhere.
"""
from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class NativeAttestedRuntimeIdentity(FrozenModel):
    repository: str = Field(min_length=1)
    revision_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    upstream_base_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    runtime_tag: str = Field(min_length=1)
    build_identity: str = Field(min_length=1)
    image_identity: str = Field(min_length=1)
    runtime_instance_id: UUID


class NativeAggregationFact(FrozenModel):
    operator: str = Field(min_length=1)
    argument_kind: str = Field(min_length=1)
    referenced_field_ids: tuple[int, ...] = ()
    distinct: bool


class NativeMetricReferenceFact(FrozenModel):
    stage_number: int = Field(ge=0)
    aggregation_index: int = Field(ge=0)
    metabase_metric_id: int = Field(gt=0)
    metabase_metric_entity_id: str = Field(min_length=1)


class NativeTemporalPredicate(FrozenModel):
    time_field_id: int = Field(gt=0)
    operator: str = Field(min_length=1)
    lower_bound: str | None = None
    upper_bound: str | None = None
    lower_inclusive: bool | None = None
    upper_inclusive: bool | None = None
    field_temporal_type: str = Field(min_length=1)
    temporal_unit: str | None = None


class NativeTextualEqualityPredicate(FrozenModel):
    """One engine-observed scalar textual equality predicate; no Dima semantics."""

    stage_number: int = Field(ge=0)
    field_id: int = Field(gt=0)
    operator: Literal["="]
    literal_value: str
    field_type: str = Field(min_length=1)


class NativeValidationProvenance(FrozenModel):
    producer_structured_output: Literal["PASSED"]
    pmbql_schema: Literal["PASSED"]
    producer_query_id_match: Literal["PASSED"]
    producer_state_match: Literal["PASSED"]


class NativePermissionProvenance(FrozenModel):
    current_metabase_user_id: int = Field(gt=0)
    permission_check: Literal["PASSED"]
    checked_source_table_ids: tuple[int, ...]


class NativeExecutionManifest(FrozenModel):
    attestation_id: str = Field(min_length=1)
    native_conversation_id: UUID
    native_assistant_message_id: int = Field(gt=0)
    native_tool_call_id: str = Field(min_length=1)
    native_query_id: str = Field(min_length=1)
    producer_tool: Literal["construct_notebook_query"]
    exact_pmbql_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    database_id: int = Field(gt=0)
    primary_source_table_id: int | None = Field(default=None, gt=0)
    referenced_source_table_ids: tuple[int, ...]
    aggregation_count: int = Field(ge=0)
    aggregations: tuple[NativeAggregationFact, ...]
    native_metric_references: tuple[NativeMetricReferenceFact, ...] = ()
    breakout_count: int = Field(ge=0)
    material_filter_count: int = Field(ge=0)
    non_temporal_filter_count: int = Field(ge=0)
    temporal_predicates: tuple[NativeTemporalPredicate, ...]
    textual_equality_predicates: tuple[NativeTextualEqualityPredicate, ...] = ()
    explicit_join_count: int = Field(ge=0)
    implicit_join_count: int = Field(ge=0)
    implicit_joined_table_ids: tuple[int, ...]
    order_by_count: int = Field(ge=0)
    limit: int | None = Field(default=None, ge=0)
    stage_count: int = Field(ge=0)
    material_query_count: int = Field(ge=0)
    authenticated_metabase_subject: int = Field(gt=0)
    validation_provenance: NativeValidationProvenance
    permission_provenance: NativePermissionProvenance
    runtime_identity: NativeAttestedRuntimeIdentity

    @model_validator(mode="after")
    def _internal_consistency(self):
        if self.aggregation_count != len(self.aggregations):
            raise ValueError("aggregation_count does not match aggregations")
        metric_ref_locations = [
            (item.stage_number, item.aggregation_index)
            for item in self.native_metric_references
        ]
        if len(metric_ref_locations) != len(set(metric_ref_locations)):
            raise ValueError("duplicate native metric reference location")
        if len(self.native_metric_references) > self.aggregation_count:
            raise ValueError("native metric references exceed aggregation count")
        if self.material_filter_count != (
            self.non_temporal_filter_count + len(self.temporal_predicates)
        ):
            raise ValueError(
                "material_filter_count must equal non-temporal filters plus temporal predicates"
            )
        if len(self.textual_equality_predicates) > self.non_temporal_filter_count:
            raise ValueError(
                "typed textual predicates cannot exceed non-temporal filter count"
            )
        if (
            self.permission_provenance.current_metabase_user_id
            != self.authenticated_metabase_subject
        ):
            raise ValueError("permission subject does not match authenticated subject")
        if tuple(sorted(self.permission_provenance.checked_source_table_ids)) != tuple(
            sorted(self.referenced_source_table_ids)
        ):
            raise ValueError("permission source set does not match referenced source set")
        if self.implicit_join_count != len(self.implicit_joined_table_ids):
            raise ValueError("implicit_join_count does not match joined table ids")
        return self


class NativeAttestationEnvelope(FrozenModel):
    exact_serialized_pmbql: dict[str, Any]
    manifest: NativeExecutionManifest


class NativeDatasetExecutionRequest(FrozenModel):
    artifact_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    database_id: int = Field(gt=0)
    exact_serialized_pmbql: dict[str, Any]
