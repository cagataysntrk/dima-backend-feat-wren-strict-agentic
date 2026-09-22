"""Dima-owned analytical execution contracts for v3.

The semantic plane resolves opaque semantic handles exactly once into
ResolvedAnalyticsIntent. Substrates receive that resolved intent and may not reparse
user language or resolve semantic handles.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v2.models import (
    ResolvedComparison as V2ResolvedComparison,
    ResolvedFilterRef as V2ResolvedFilterRef,
    ResolvedPeriod as V2ResolvedPeriod,
    ResolvedSemanticRef as V2ResolvedSemanticRef,
    SemanticTargetKind,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class StandardProjection(FrozenModel):
    """Sealable semantic body. Shape intentionally matches the certified v2 projection."""

    obligation_ids: tuple[str, ...] = Field(min_length=1)
    metric_handles: tuple[str, ...] = Field(min_length=1)
    dimension_handles: tuple[str, ...] = ()
    filter_handles: tuple[str, ...] = ()
    period_handle: str | None = None
    comparison_handle: str | None = None
    ranking_direction: Literal["asc", "desc"] | None = None
    limit: int | None = Field(default=None, ge=1, le=1000)

    @model_validator(mode="after")
    def _ranking_pair(self):
        if (self.ranking_direction is None) != (self.limit is None):
            raise ValueError("ranking direction and limit must be supplied together")
        return self


def projection_hash(projection: StandardProjection) -> str:
    raw = json.dumps(
        projection.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def projection_handles(projection: StandardProjection) -> tuple[str, ...]:
    values = [
        *projection.metric_handles,
        *projection.dimension_handles,
        *projection.filter_handles,
    ]
    if projection.period_handle is not None:
        values.append(projection.period_handle)
    if projection.comparison_handle is not None:
        values.append(projection.comparison_handle)
    return tuple(dict.fromkeys(values))


class ResolvedSemanticRef(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    source_candidate_id: str = Field(min_length=1)
    kind: Literal["metric", "dimension"]
    canonical_name: str = Field(min_length=1)
    source_scopes: tuple[str, ...] = ()


class ResolvedFilterRef(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    source_candidate_id: str = Field(min_length=1)
    dimension_name: str = Field(min_length=1)
    value: str
    source_scopes: tuple[str, ...] = ()
    sensitive: bool = False


class ResolvedPeriod(FrozenModel):
    kind: str = Field(min_length=1)
    source_text: str
    time_dimension: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str | None = None
    n: int | None = None


class ResolvedComparison(FrozenModel):
    mode: str = Field(min_length=1)
    source_text: str
    base_period: ResolvedPeriod
    reference_period: ResolvedPeriod


class ResolvedRanking(FrozenModel):
    measure: str = Field(min_length=1)
    direction: Literal["asc", "desc"]
    limit: int = Field(ge=1, le=1000)


class ApprovedRelationshipPath(FrozenModel):
    relationship_refs: tuple[str, ...] = Field(min_length=1)


class PrincipalContextRef(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    principal_subject: str = Field(min_length=1)
    roles: tuple[str, ...] = ()

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            {
                "tenant_binding": self.tenant_binding,
                "principal_subject": self.principal_subject,
                "roles": sorted(self.roles),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ResolvedAnalyticsIntent(FrozenModel):
    authority_id: str = Field(min_length=1)
    request_ref: str = Field(min_length=1)
    source_message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    semantic_context_version: str = Field(min_length=1)
    obligation_ids: tuple[str, ...] = Field(min_length=1)
    metrics: tuple[ResolvedSemanticRef, ...] = Field(min_length=1)
    dimensions: tuple[ResolvedSemanticRef, ...] = ()
    filters: tuple[ResolvedFilterRef, ...] = ()
    period: ResolvedPeriod | None = None
    comparison: ResolvedComparison | None = None
    ranking: ResolvedRanking | None = None
    approved_relationship_paths: tuple[ApprovedRelationshipPath, ...] = ()
    grain_constraints: tuple[str, ...] = ()
    principal: PrincipalContextRef

    @property
    def resolved_intent_hash(self) -> str:
        raw = json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class StandardAuthorityLike(Protocol):
    authority_id: str
    request_ref: str
    source_message_hash: str
    projection_hash: str
    semantic_handle_refs: tuple[str, ...]
    context_version: str


class SemanticHandleRegistryLike(Protocol):
    def binding_for_execution(
        self,
        handle_id: str,
        *,
        tenant_binding: str,
        context_version: str,
    ):
        ...


class SemanticHandleResolutionError(RuntimeError):
    pass


class ResolvedAnalyticsIntentBuilder:
    """Trusted Dima boundary: resolve each governed semantic handle exactly once."""

    def __init__(self, *, semantic_handles: SemanticHandleRegistryLike) -> None:
        self._handles = semantic_handles

    @staticmethod
    def _period(value: V2ResolvedPeriod) -> ResolvedPeriod:
        return ResolvedPeriod(
            kind=value.kind.value,
            source_text=value.source_text,
            time_dimension=value.time_dimension,
            start=value.start,
            end=value.end,
            n=value.n,
        )

    @classmethod
    def _comparison(cls, value: V2ResolvedComparison) -> ResolvedComparison:
        return ResolvedComparison(
            mode=value.mode,
            source_text=value.source_text,
            base_period=cls._period(value.base_period),
            reference_period=cls._period(value.reference_period),
        )

    def build(
        self,
        *,
        projection: StandardProjection,
        authority: StandardAuthorityLike,
        tenant_binding: str,
        principal_subject: str,
        principal_roles: tuple[str, ...] = (),
    ) -> ResolvedAnalyticsIntent:
        if projection_hash(projection) != authority.projection_hash:
            raise SemanticHandleResolutionError(
                "projection does not match accepted Standard authority"
            )
        handles = projection_handles(projection)
        if handles != authority.semantic_handle_refs:
            raise SemanticHandleResolutionError(
                "projection semantic handles do not match accepted authority"
            )

        resolved = {
            handle_id: self._handles.binding_for_execution(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=authority.context_version,
            ).canonical_target
            for handle_id in handles
        }

        metrics: list[ResolvedSemanticRef] = []
        for handle_id in projection.metric_handles:
            target = resolved[handle_id]
            if (
                not isinstance(target, V2ResolvedSemanticRef)
                or target.target_kind != SemanticTargetKind.METRIC
            ):
                raise SemanticHandleResolutionError(
                    f"{handle_id} is not a governed metric target"
                )
            metrics.append(
                ResolvedSemanticRef(
                    semantic_ref=handle_id,
                    source_candidate_id=target.candidate_id,
                    kind="metric",
                    canonical_name=target.canonical_name,
                    source_scopes=target.cube_names,
                )
            )

        dimensions: list[ResolvedSemanticRef] = []
        for handle_id in projection.dimension_handles:
            target = resolved[handle_id]
            if (
                not isinstance(target, V2ResolvedSemanticRef)
                or target.target_kind != SemanticTargetKind.DIMENSION
            ):
                raise SemanticHandleResolutionError(
                    f"{handle_id} is not a governed dimension target"
                )
            dimensions.append(
                ResolvedSemanticRef(
                    semantic_ref=handle_id,
                    source_candidate_id=target.candidate_id,
                    kind="dimension",
                    canonical_name=target.canonical_name,
                    source_scopes=target.cube_names,
                )
            )

        filters: list[ResolvedFilterRef] = []
        for handle_id in projection.filter_handles:
            target = resolved[handle_id]
            if not isinstance(target, V2ResolvedFilterRef):
                raise SemanticHandleResolutionError(
                    f"{handle_id} is not a governed filter target"
                )
            filters.append(
                ResolvedFilterRef(
                    semantic_ref=handle_id,
                    source_candidate_id=target.candidate_id,
                    dimension_name=target.dimension_name,
                    value=target.value,
                    source_scopes=target.cube_names,
                    sensitive=target.sensitive,
                )
            )

        period = None
        if projection.period_handle is not None:
            target = resolved[projection.period_handle]
            if not isinstance(target, V2ResolvedPeriod):
                raise SemanticHandleResolutionError(
                    f"{projection.period_handle} is not a governed period target"
                )
            period = self._period(target)

        comparison = None
        if projection.comparison_handle is not None:
            target = resolved[projection.comparison_handle]
            if not isinstance(target, V2ResolvedComparison):
                raise SemanticHandleResolutionError(
                    f"{projection.comparison_handle} is not a governed comparison target"
                )
            comparison = self._comparison(target)

        ranking = None
        if projection.ranking_direction is not None:
            if len(metrics) != 1 or not dimensions:
                raise SemanticHandleResolutionError(
                    "ranking requires exactly one metric and at least one dimension"
                )
            ranking = ResolvedRanking(
                measure=metrics[0].canonical_name,
                direction=projection.ranking_direction,
                limit=projection.limit,
            )

        return ResolvedAnalyticsIntent(
            authority_id=authority.authority_id,
            request_ref=authority.request_ref,
            source_message_hash=authority.source_message_hash,
            projection_hash=authority.projection_hash,
            semantic_context_version=authority.context_version,
            obligation_ids=projection.obligation_ids,
            metrics=tuple(metrics),
            dimensions=tuple(dimensions),
            filters=tuple(filters),
            period=period,
            comparison=comparison,
            ranking=ranking,
            principal=PrincipalContextRef(
                tenant_binding=tenant_binding,
                principal_subject=principal_subject,
                roles=principal_roles,
            ),
        )
