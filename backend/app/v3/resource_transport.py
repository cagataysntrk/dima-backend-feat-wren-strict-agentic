"""P9B1 provider-free Metabase metric persistence contracts.

This module does not perform HTTP I/O. It binds a P9 desired CREATE action to an
already-certified P4 canonical serialized query and produces the exact pinned
Metabase Agent API metric-create request shape.

It does not compile formulas, resolve names, search Metabase, or construct SQL.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.v3.resource_provisioning import (
    ProvisionAction,
    ProvisionActionKind,
    ResourceKind,
)
from app.v3.substrate.metabase.canonical import CanonicalProjection


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResourceTransportError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class MetricCreateTarget(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    collection_id: int = Field(ge=1)


class MetricAgentCreateRequest(FrozenModel):
    """Exact P9B1 subset of pinned POST /api/agent/v1/metric."""

    name: str = Field(min_length=1)
    query: str = Field(min_length=1)
    display: Literal["scalar"] = "scalar"
    collection_id: int = Field(ge=1)
    visualization_settings: dict[str, Any] = Field(default_factory=dict)


class MetricCreateContract(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    canonical_id: str = Field(min_length=1)
    desired_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    semantic_context_version: str = Field(min_length=1)
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    resolved_intent_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    current_catalog_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    canonical_query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    collection_id: int = Field(ge=1)
    request: MetricAgentCreateRequest
    contract_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class MetricCreateContractBuilder:
    """Bind P9 desired state to one certified P4 query without reinterpretation."""

    @staticmethod
    def _metric_payload(action: ProvisionAction) -> tuple[dict[str, Any], dict[str, Any]]:
        if action.action != ProvisionActionKind.CREATE:
            raise ResourceTransportError(
                "P9B1_ACTION_UNSUPPORTED",
                "initial P9B1 contract accepts CREATE only",
            )
        if action.resource_kind != ResourceKind.METRIC:
            raise ResourceTransportError(
                "P9B1_RESOURCE_KIND_UNSUPPORTED",
                "initial P9B1 contract accepts metric resources only",
            )
        desired = action.desired
        if desired is None:
            raise ResourceTransportError(
                "P9B1_DESIRED_RESOURCE_REQUIRED",
                "CREATE action must carry desired resource",
            )
        if desired.resource_kind != ResourceKind.METRIC:
            raise ResourceTransportError(
                "P9B1_RESOURCE_KIND_MISMATCH",
                "action and desired resource kinds differ",
            )
        if action.canonical_id != desired.canonical_id:
            raise ResourceTransportError(
                "P9B1_CANONICAL_ID_MISMATCH",
                "action and desired canonical ids differ",
            )

        payload = desired.payload
        if payload.get("canonical_id") != desired.canonical_id:
            raise ResourceTransportError(
                "P9B1_DESIRED_PAYLOAD_ID_MISMATCH",
                "desired payload canonical id does not match resource",
            )
        if payload.get("resource_kind") != ResourceKind.METRIC.value:
            raise ResourceTransportError(
                "P9B1_DESIRED_PAYLOAD_KIND_MISMATCH",
                "desired payload is not a metric resource",
            )
        if payload.get("semantic_context_version") != desired.semantic_context_version:
            raise ResourceTransportError(
                "P9B1_DESIRED_CONTEXT_MISMATCH",
                "desired payload semantic context does not match resource",
            )
        if payload.get("classification") != "NATIVE_METABASE":
            raise ResourceTransportError(
                "P9B1_CLASSIFICATION_UNSUPPORTED",
                "initial metric persistence requires P8 NATIVE_METABASE",
            )

        semantic = payload.get("semantic")
        if not isinstance(semantic, dict):
            raise ResourceTransportError(
                "P9B1_METRIC_PAYLOAD_MISSING",
                "desired payload lacks structured metric",
            )
        if semantic.get("metric_id") != desired.canonical_id:
            raise ResourceTransportError(
                "P9B1_METRIC_ID_MISMATCH",
                "structured metric id does not match desired canonical id",
            )
        if semantic.get("formula") is not None:
            raise ResourceTransportError(
                "P9B1_FORMULA_METRIC_UNSUPPORTED",
                "P9B1 does not persist arbitrary formula-backed metrics",
            )
        name = semantic.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ResourceTransportError(
                "P9B1_METRIC_NAME_MISSING",
                "structured metric name is required",
            )
        return payload, semantic

    @staticmethod
    def _step(projection: CanonicalProjection):
        if projection.manifest.query_count != 1 or len(projection.steps) != 1:
            raise ResourceTransportError(
                "P9B1_QUERY_CARDINALITY",
                "metric persistence requires exactly one canonical query step",
            )
        step = projection.steps[0]
        if step.role != "primary":
            raise ResourceTransportError(
                "P9B1_QUERY_ROLE",
                "metric persistence requires one primary step",
            )

        manifest = step.manifest
        if len(manifest.aggregation_operators) != 1:
            raise ResourceTransportError(
                "P9B1_METRIC_AGGREGATION_SHAPE",
                "metric persistence requires exactly one aggregation",
            )
        disallowed = {
            "breakout_count": manifest.breakout_count,
            "filter_leaf_count": manifest.filter_leaf_count,
            "time_predicate_count": manifest.time_predicate_count,
            "order_by_count": manifest.order_by_count,
            "explicit_join_count": manifest.explicit_join_count,
            "implicit_join_reference_count": manifest.implicit_join_reference_count,
        }
        active = {key: value for key, value in disallowed.items() if value}
        if manifest.limit is not None:
            active["limit"] = manifest.limit
        if active:
            raise ResourceTransportError(
                "P9B1_QUERY_SHAPE_UNSUPPORTED",
                f"initial persisted metric query contains unsupported clauses: {active!r}",
            )
        return step

    @classmethod
    def build(
        cls,
        *,
        action: ProvisionAction,
        projection: CanonicalProjection,
        target: MetricCreateTarget,
    ) -> MetricCreateContract:
        _, semantic = cls._metric_payload(action)
        desired = action.desired
        assert desired is not None

        if target.tenant_binding != desired.tenant_binding:
            raise ResourceTransportError(
                "P9B1_TARGET_TENANT_MISMATCH",
                "explicit persistence target tenant does not match desired resource tenant",
            )
        if desired.semantic_context_version != projection.semantic_context_version:
            raise ResourceTransportError(
                "P9B1_PROJECTION_CONTEXT_MISMATCH",
                "desired resource and canonical query contexts differ",
            )
        step = cls._step(projection)
        if projection.manifest.semantic_ids != (desired.canonical_id,):
            raise ResourceTransportError(
                "P9B1_PROJECTION_SEMANTIC_ID_MISMATCH",
                "canonical query does not represent exactly the desired metric",
            )
        request = MetricAgentCreateRequest(
            name=semantic["name"],
            query=step.serialized_query,
            display="scalar",
            collection_id=target.collection_id,
            visualization_settings={},
        )
        payload = {
            "tenant_binding": desired.tenant_binding,
            "canonical_id": desired.canonical_id,
            "desired_fingerprint": desired.desired_fingerprint,
            "semantic_context_version": desired.semantic_context_version,
            "projection_hash": projection.projection_hash,
            "resolved_intent_hash": projection.resolved_intent_hash,
            "current_catalog_fingerprint": projection.current_catalog_fingerprint,
            "canonical_query_fingerprint": step.canonical_query_fingerprint,
            "collection_id": target.collection_id,
            "request": request.model_dump(mode="json"),
        }
        return MetricCreateContract(
            tenant_binding=desired.tenant_binding,
            canonical_id=desired.canonical_id,
            desired_fingerprint=desired.desired_fingerprint,
            semantic_context_version=desired.semantic_context_version,
            projection_hash=projection.projection_hash,
            resolved_intent_hash=projection.resolved_intent_hash,
            current_catalog_fingerprint=projection.current_catalog_fingerprint,
            canonical_query_fingerprint=step.canonical_query_fingerprint,
            collection_id=target.collection_id,
            request=request,
            contract_fingerprint=_canonical_hash(payload),
        )
