"""Typed follow-up scope patch semantics.

A follow-up turn is a delta over an accepted ResearchScope.  This module is the
single pure reducer allowed to compute scope_vN from scope_vN-1.  It performs no
provider, database, Metabase, prompt, regex, or fuzzy interpretation.
"""
from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field, model_validator

from app.v3.research_contracts import (
    FrozenModel,
    ResearchNativeVerificationBinding,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeMutation,
    ScopeMutationKind,
    ScopeVersion,
    SemanticTargetKind,
    TurnScopeContract,
)


class ScopePatchFacet(StrEnum):
    ENTITY = "ENTITY"
    PERIOD = "PERIOD"
    METRIC = "METRIC"
    BREAKDOWN = "BREAKDOWN"


class ScopePatchOperationKind(StrEnum):
    SET = "SET"
    ADD = "ADD"
    REMOVE = "REMOVE"
    CLEAR = "CLEAR"


class ScopePatchOperation(FrozenModel):
    facet: ScopePatchFacet
    operation: ScopePatchOperationKind
    semantic_refs: tuple[ResearchSemanticRef, ...] = ()
    periods: tuple[ResearchTimePeriod, ...] = ()
    native_verification_bindings: tuple[
        ResearchNativeVerificationBinding, ...
    ] = ()
    source_fragment: str = Field(min_length=1)

    @model_validator(mode="after")
    def coherent(self):
        ids = tuple(item.candidate_id for item in self.semantic_refs)
        if len(ids) != len(set(ids)):
            raise ValueError("scope patch semantic refs must be unique")
        binding_ids = tuple(
            item.candidate_id for item in self.native_verification_bindings
        )
        if len(binding_ids) != len(set(binding_ids)):
            raise ValueError("scope patch native bindings must be unique")
        if not set(binding_ids).issubset(set(ids)):
            raise ValueError(
                "scope patch native binding must belong to a patched semantic ref"
            )

        if self.operation == ScopePatchOperationKind.CLEAR:
            if self.semantic_refs or self.periods or self.native_verification_bindings:
                raise ValueError("CLEAR must not carry values")
            return self

        if self.facet == ScopePatchFacet.PERIOD:
            if not self.periods:
                raise ValueError("PERIOD patch requires typed period values")
            if any(
                item.target_kind != SemanticTargetKind.DIMENSION
                for item in self.semantic_refs
            ):
                raise ValueError("PERIOD patch refs must be dimensions")
            period_dimensions = {
                item.time_dimension_candidate_id for item in self.periods
            }
            if not period_dimensions.issubset(set(ids)):
                raise ValueError(
                    "PERIOD patch must bind every period time dimension"
                )
            return self

        if self.periods:
            raise ValueError("non-PERIOD patch cannot carry periods")
        if not self.semantic_refs:
            raise ValueError(
                f"{self.facet.value} {self.operation.value} requires governed values"
            )

        allowed = {
            ScopePatchFacet.ENTITY: {SemanticTargetKind.ENTITY_VALUE},
            ScopePatchFacet.METRIC: {
                SemanticTargetKind.METRIC,
                SemanticTargetKind.KPI,
            },
            ScopePatchFacet.BREAKDOWN: {SemanticTargetKind.DIMENSION},
        }[self.facet]
        if any(item.target_kind not in allowed for item in self.semantic_refs):
            raise ValueError(
                f"{self.facet.value} patch carries an incompatible semantic ref"
            )
        return self


class TurnScopePatch(FrozenModel):
    source_scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    operations: tuple[ScopePatchOperation, ...] = ()

    @model_validator(mode="after")
    def one_operation_per_facet(self):
        facets = tuple(item.facet for item in self.operations)
        if len(facets) != len(set(facets)):
            raise ValueError(
                "one follow-up turn may carry at most one operation per scope facet"
            )
        return self


class ResolvedScopeVersion(FrozenModel):
    previous_scope: ResearchScope
    current_scope: ResearchScope
    scope_contract: TurnScopeContract | None = None
    scope_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    changed_facets: tuple[ScopePatchFacet, ...] = ()
    derived_mutation_kind: ScopeMutationKind | None = None
    materially_changed: bool


def _canonical(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def scope_fingerprint(
    scope: ResearchScope,
    *,
    context_version: str,
    tenant_binding: str | None = None,
    principal_ref: str | None = None,
) -> str:
    """Fingerprint semantic scope, independent of tuple order and wording.

    Scope version/ordinal and source wording are deliberately excluded so the
    same semantic scope has the same fingerprint across replay/idempotency.
    Tenant/principal may be included where the caller is crossing a security
    boundary; the canonical Research reducer itself does not require them.
    """

    semantic = [
        {
            "candidate_id": item.candidate_id,
            "target_kind": item.target_kind.value,
            "dimension_name": item.dimension_name,
            "value": item.value,
        }
        for item in sorted(
            scope.semantic_refs,
            key=lambda value: (
                value.target_kind.value,
                value.candidate_id,
            ),
        )
    ]
    periods = [
        {
            "time_dimension_candidate_id": item.time_dimension_candidate_id,
            "start": item.start,
            "end": item.end,
            "role": item.role.value,
        }
        for item in sorted(
            scope.periods,
            key=lambda value: (
                value.time_dimension_candidate_id,
                value.start,
                value.end,
                value.role.value,
            ),
        )
    ]
    payload = {
        "context_version": context_version,
        "semantic_refs": semantic,
        "periods": periods,
        "temporal_dimension_ids": sorted(scope.temporal_dimension_ids),
    }
    if tenant_binding is not None:
        payload["tenant_binding"] = tenant_binding
    if principal_ref is not None:
        payload["principal_ref"] = principal_ref
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _ref_map(values: tuple[ResearchSemanticRef, ...]) -> dict[str, ResearchSemanticRef]:
    return {item.candidate_id: item for item in values}


def _binding_map(
    values: tuple[ResearchNativeVerificationBinding, ...],
) -> dict[str, ResearchNativeVerificationBinding]:
    return {item.candidate_id: item for item in values}


def _period_identity(value: ResearchTimePeriod) -> tuple[str, str, str, str]:
    return (
        value.time_dimension_candidate_id,
        value.start,
        value.end,
        value.role.value,
    )


def _apply_ref_operation(
    current: dict[str, ResearchSemanticRef],
    operation: ScopePatchOperation,
) -> dict[str, ResearchSemanticRef]:
    incoming = _ref_map(operation.semantic_refs)
    if operation.operation == ScopePatchOperationKind.SET:
        return incoming
    if operation.operation == ScopePatchOperationKind.ADD:
        return {**current, **incoming}
    if operation.operation == ScopePatchOperationKind.REMOVE:
        return {
            key: value
            for key, value in current.items()
            if key not in incoming
        }
    if operation.operation == ScopePatchOperationKind.CLEAR:
        return {}
    raise AssertionError(operation.operation)


def _apply_period_operation(
    current: dict[tuple[str, str, str, str], ResearchTimePeriod],
    operation: ScopePatchOperation,
) -> dict[tuple[str, str, str, str], ResearchTimePeriod]:
    incoming = {_period_identity(item): item for item in operation.periods}
    if operation.operation == ScopePatchOperationKind.SET:
        return incoming
    if operation.operation == ScopePatchOperationKind.ADD:
        return {**current, **incoming}
    if operation.operation == ScopePatchOperationKind.REMOVE:
        return {
            key: value
            for key, value in current.items()
            if key not in incoming
        }
    if operation.operation == ScopePatchOperationKind.CLEAR:
        return {}
    raise AssertionError(operation.operation)


def _derive_mutation_kind(
    *,
    changed_facets: tuple[ScopePatchFacet, ...],
    old_entities: set[str],
    new_entities: set[str],
) -> ScopeMutationKind | None:
    if not changed_facets:
        return None
    if len(changed_facets) != 1:
        return ScopeMutationKind.REPLACE
    facet = changed_facets[0]
    if facet == ScopePatchFacet.PERIOD:
        return ScopeMutationKind.CHANGE_PERIOD
    if facet == ScopePatchFacet.METRIC:
        return ScopeMutationKind.CHANGE_METRIC
    if facet == ScopePatchFacet.BREAKDOWN:
        return ScopeMutationKind.CHANGE_BREAKDOWN

    if not old_entities and new_entities:
        return ScopeMutationKind.NARROW_ENTITY
    if old_entities and not new_entities:
        return ScopeMutationKind.EXPAND_ENTITY
    if new_entities < old_entities:
        return ScopeMutationKind.NARROW_ENTITY
    if old_entities < new_entities:
        return ScopeMutationKind.EXPAND_ENTITY
    return ScopeMutationKind.REPLACE


def resolve_scope_patch(
    prior_scope: ResearchScope,
    patch: TurnScopePatch,
    *,
    context_version: str,
    tenant_binding: str | None = None,
    principal_ref: str | None = None,
) -> ResolvedScopeVersion:
    """Pure FieldMask-style reducer for one follow-up scope delta."""

    if patch.source_scope_version_id != prior_scope.scope_version.version_id:
        raise ValueError("scope patch was formed against another scope version")

    prior_refs = tuple(prior_scope.semantic_refs)
    prior_temporal_ids = set(prior_scope.temporal_dimension_ids)

    entities = _ref_map(
        tuple(
            item
            for item in prior_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        )
    )
    metrics = _ref_map(
        tuple(
            item
            for item in prior_refs
            if item.target_kind
            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
    )
    temporal_refs = _ref_map(
        tuple(
            item
            for item in prior_refs
            if item.candidate_id in prior_temporal_ids
        )
    )
    breakdowns = _ref_map(
        tuple(
            item
            for item in prior_refs
            if (
                item.target_kind == SemanticTargetKind.DIMENSION
                and item.candidate_id not in prior_temporal_ids
            )
        )
    )
    other_refs = _ref_map(
        tuple(
            item
            for item in prior_refs
            if item.target_kind == SemanticTargetKind.CUBE
        )
    )

    periods = {
        _period_identity(item): item
        for item in prior_scope.periods
    }
    bindings = _binding_map(prior_scope.native_verification_bindings)

    old_entities = set(entities)
    old_metrics = set(metrics)
    old_breakdowns = set(breakdowns)
    old_periods = set(periods)

    operation_bindings: dict[str, ResearchNativeVerificationBinding] = {}
    for operation in patch.operations:
        operation_bindings.update(
            _binding_map(operation.native_verification_bindings)
        )
        if operation.facet == ScopePatchFacet.ENTITY:
            entities = _apply_ref_operation(entities, operation)
        elif operation.facet == ScopePatchFacet.METRIC:
            metrics = _apply_ref_operation(metrics, operation)
        elif operation.facet == ScopePatchFacet.BREAKDOWN:
            breakdowns = _apply_ref_operation(breakdowns, operation)
        elif operation.facet == ScopePatchFacet.PERIOD:
            periods = _apply_period_operation(periods, operation)
            if operation.operation == ScopePatchOperationKind.CLEAR:
                temporal_refs = {}
            elif operation.operation == ScopePatchOperationKind.SET:
                temporal_refs = _ref_map(operation.semantic_refs)
            elif operation.operation == ScopePatchOperationKind.ADD:
                temporal_refs.update(_ref_map(operation.semantic_refs))
            elif operation.operation == ScopePatchOperationKind.REMOVE:
                required_temporal_ids = {
                    item.time_dimension_candidate_id
                    for item in periods.values()
                }
                temporal_refs = {
                    key: value
                    for key, value in temporal_refs.items()
                    if key in required_temporal_ids
                }
        else:
            raise AssertionError(operation.facet)

    changed: list[ScopePatchFacet] = []
    if old_entities != set(entities):
        changed.append(ScopePatchFacet.ENTITY)
    if old_periods != set(periods):
        changed.append(ScopePatchFacet.PERIOD)
    if old_metrics != set(metrics):
        changed.append(ScopePatchFacet.METRIC)
    if old_breakdowns != set(breakdowns):
        changed.append(ScopePatchFacet.BREAKDOWN)
    changed_facets = tuple(changed)

    if not changed_facets:
        return ResolvedScopeVersion(
            previous_scope=prior_scope,
            current_scope=prior_scope,
            scope_contract=None,
            scope_fingerprint=scope_fingerprint(
                prior_scope,
                context_version=context_version,
                tenant_binding=tenant_binding,
                principal_ref=principal_ref,
            ),
            changed_facets=(),
            derived_mutation_kind=None,
            materially_changed=False,
        )

    final_refs = {
        **other_refs,
        **metrics,
        **breakdowns,
        **temporal_refs,
        **entities,
    }
    accepted_ids = set(final_refs)
    final_bindings: dict[str, ResearchNativeVerificationBinding] = {}
    for candidate_id in sorted(accepted_ids):
        value = operation_bindings.get(candidate_id) or bindings.get(candidate_id)
        if value is not None:
            final_bindings[candidate_id] = value

    ordered_periods = tuple(
        periods[key] for key in sorted(periods)
    )
    time_surfaces = tuple(
        dict.fromkeys(item.source_text for item in ordered_periods)
    )
    next_ordinal = prior_scope.scope_version.ordinal + 1
    current_scope = ResearchScope(
        semantic_refs=tuple(
            final_refs[key] for key in sorted(final_refs)
        ),
        time_surfaces=time_surfaces,
        periods=ordered_periods,
        temporal_dimension_ids=tuple(sorted(temporal_refs)),
        native_verification_bindings=tuple(
            final_bindings[key] for key in sorted(final_bindings)
        ),
        scope_version=ScopeVersion(
            version_id=f"scope_v{next_ordinal}",
            ordinal=next_ordinal,
            parent_version_id=prior_scope.scope_version.version_id,
        ),
    )

    kind = _derive_mutation_kind(
        changed_facets=changed_facets,
        old_entities=old_entities,
        new_entities=set(entities),
    )
    assert kind is not None
    reason = " | ".join(
        item.source_fragment for item in patch.operations
    )
    mutation = ScopeMutation(
        kind=kind,
        source_version_id=prior_scope.scope_version.version_id,
        target_semantic_refs=current_scope.semantic_refs,
        target_time_surfaces=current_scope.time_surfaces,
        target_periods=current_scope.periods,
        target_temporal_dimension_ids=current_scope.temporal_dimension_ids,
        target_native_verification_bindings=(
            current_scope.native_verification_bindings
        ),
        reason=reason,
    )
    contract = TurnScopeContract(
        previous_scope=prior_scope,
        current_scope=current_scope,
        mutation=mutation,
    )
    return ResolvedScopeVersion(
        previous_scope=prior_scope,
        current_scope=current_scope,
        scope_contract=contract,
        scope_fingerprint=scope_fingerprint(
            current_scope,
            context_version=context_version,
            tenant_binding=tenant_binding,
            principal_ref=principal_ref,
        ),
        changed_facets=changed_facets,
        derived_mutation_kind=kind,
        materially_changed=True,
    )
