"""P9A deterministic Dima-managed semantic resource planning.

This module owns provider-free desired-state identity, explicit ownership, drift
classification, reconciliation and rollback planning. It performs no Metabase I/O,
resource search, semantic interpretation or permission mapping.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.semantic_equivalence import (
    DimaRepresentationState,
    EquivalenceClassification,
    SemanticEquivalenceMatrix,
)
from app.v3.semantic_import import SemanticImportResult
from app.v3.semantic_spec import (
    DimensionSpec,
    ManagedResourcePolicy,
    MetricSpec,
    RelationshipSpec,
    TimeSpec,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResourceProvisioningError(RuntimeError):
    pass


class ResourceKind(StrEnum):
    METRIC = "metric"
    DIMENSION = "dimension"
    TIME = "time"
    RELATIONSHIP = "relationship"


class ProvisionActionKind(StrEnum):
    CREATE = "CREATE"
    NOOP = "NOOP"
    UPDATE = "UPDATE"
    REJECT_DRIFT = "REJECT_DRIFT"
    IMPORT_AS_NEW_VERSION = "IMPORT_AS_NEW_VERSION"
    RETIRE_STALE = "RETIRE_STALE"


class RollbackKind(StrEnum):
    ARCHIVE_CREATED_RESOURCE = "ARCHIVE_CREATED_RESOURCE"
    RESTORE_PREVIOUS_SNAPSHOT = "RESTORE_PREVIOUS_SNAPSHOT"
    RESTORE_PREVIOUS_BINDING = "RESTORE_PREVIOUS_BINDING"
    RETIRE_NEW_VERSION = "RETIRE_NEW_VERSION"


class ProvisionSkipReason(StrEnum):
    USER_MANAGED = "USER_MANAGED"
    EXTERNAL = "EXTERNAL"
    DIMA_RUNTIME = "DIMA_RUNTIME"
    WREN_ONLY_GAP = "WREN_ONLY_GAP"
    UNSUPPORTED = "UNSUPPORTED"


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
        raise ResourceProvisioningError(
            "resource state must be deterministic canonical JSON"
        ) from exc
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class DesiredResource(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    canonical_id: str = Field(min_length=1)
    resource_kind: ResourceKind
    semantic_context_version: str = Field(min_length=1)
    desired_version: str = Field(min_length=1)
    desired_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    payload: dict[str, Any]
    ownership: Literal["DIMA_MANAGED"] = "DIMA_MANAGED"
    reconciliation: Literal[
        "OVERWRITE",
        "REJECT",
        "IMPORT_AS_NEW_VERSION",
    ]

    @model_validator(mode="after")
    def _fingerprint_matches_payload(self):
        if self.desired_fingerprint != _canonical_hash(self.payload):
            raise ValueError("desired resource fingerprint/payload mismatch")
        return self


class ManagedResourceBinding(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    canonical_id: str = Field(min_length=1)
    resource_kind: ResourceKind
    semantic_context_version: str = Field(min_length=1)
    metabase_entity_id: str | None = None
    metabase_local_id: int | None = Field(default=None, ge=1)
    applied_version: str = Field(min_length=1)
    applied_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    ownership: Literal[
        "DIMA_MANAGED",
        "USER_MANAGED",
        "EXTERNAL",
    ]

    @model_validator(mode="after")
    def _has_exact_external_locator(self):
        if self.metabase_entity_id is None and self.metabase_local_id is None:
            raise ValueError("managed resource binding requires an external locator")
        if (
            self.metabase_entity_id is not None
            and not self.metabase_entity_id.strip()
        ):
            raise ValueError("metabase_entity_id must be null or non-empty")
        return self

    @property
    def binding_key(self) -> tuple[str, str, str]:
        return (
            self.tenant_binding,
            self.resource_kind.value,
            self.canonical_id,
        )


class ObservedMetabaseResource(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    resource_kind: ResourceKind
    metabase_entity_id: str | None = None
    metabase_local_id: int | None = Field(default=None, ge=1)
    display_name: str | None = None
    resource_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    managed_payload: dict[str, Any]

    @model_validator(mode="after")
    def _validate_observed_identity(self):
        if self.metabase_entity_id is None and self.metabase_local_id is None:
            raise ValueError("observed resource requires an external locator")
        if self.resource_fingerprint != _canonical_hash(self.managed_payload):
            raise ValueError("observed resource fingerprint/payload mismatch")
        return self

    @classmethod
    def from_payload(
        cls,
        *,
        tenant_binding: str,
        resource_kind: ResourceKind,
        managed_payload: dict[str, Any],
        metabase_entity_id: str | None = None,
        metabase_local_id: int | None = None,
        display_name: str | None = None,
    ) -> "ObservedMetabaseResource":
        return cls(
            tenant_binding=tenant_binding,
            resource_kind=resource_kind,
            metabase_entity_id=metabase_entity_id,
            metabase_local_id=metabase_local_id,
            display_name=display_name,
            resource_fingerprint=_canonical_hash(managed_payload),
            managed_payload=managed_payload,
        )


class ResourceInventorySnapshot(FrozenModel):
    bindings: tuple[ManagedResourceBinding, ...] = ()
    resources: tuple[ObservedMetabaseResource, ...] = ()

    @model_validator(mode="after")
    def _unique_inventory_keys(self):
        binding_keys = [item.binding_key for item in self.bindings]
        if len(binding_keys) != len(set(binding_keys)):
            raise ValueError("duplicate managed resource binding key")

        entity_keys = [
            (
                item.tenant_binding,
                item.resource_kind.value,
                item.metabase_entity_id,
            )
            for item in self.resources
            if item.metabase_entity_id is not None
        ]
        if len(entity_keys) != len(set(entity_keys)):
            raise ValueError("duplicate observed Metabase entity locator")

        local_keys = [
            (
                item.tenant_binding,
                item.resource_kind.value,
                item.metabase_local_id,
            )
            for item in self.resources
            if item.metabase_local_id is not None
        ]
        if len(local_keys) != len(set(local_keys)):
            raise ValueError("duplicate observed Metabase local locator")
        return self

    def binding_for(
        self,
        *,
        tenant_binding: str,
        canonical_id: str,
        resource_kind: ResourceKind,
    ) -> ManagedResourceBinding | None:
        for item in self.bindings:
            if item.binding_key == (
                tenant_binding,
                resource_kind.value,
                canonical_id,
            ):
                return item
        return None

    def resource_for_binding(
        self,
        binding: ManagedResourceBinding,
    ) -> ObservedMetabaseResource | None:
        matches: list[ObservedMetabaseResource] = []
        for item in self.resources:
            if (
                item.tenant_binding != binding.tenant_binding
                or item.resource_kind != binding.resource_kind
            ):
                continue
            if (
                binding.metabase_entity_id is not None
                and item.metabase_entity_id == binding.metabase_entity_id
            ):
                matches.append(item)
                continue
            if (
                binding.metabase_entity_id is None
                and binding.metabase_local_id is not None
                and item.metabase_local_id == binding.metabase_local_id
            ):
                matches.append(item)

        if not matches:
            return None
        if len(matches) != 1:
            raise ResourceProvisioningError(
                "binding resolves to multiple observed Metabase resources"
            )
        match = matches[0]
        if (
            binding.metabase_local_id is not None
            and match.metabase_local_id != binding.metabase_local_id
        ):
            raise ResourceProvisioningError(
                "binding entity/local locators disagree"
            )
        return match


class RollbackDescriptor(FrozenModel):
    kind: RollbackKind
    prior_binding: ManagedResourceBinding | None = None
    prior_payload: dict[str, Any] | None = None


class ProvisionAction(FrozenModel):
    action: ProvisionActionKind
    canonical_id: str = Field(min_length=1)
    resource_kind: ResourceKind
    reason_code: str = Field(min_length=1)
    desired: DesiredResource | None = None
    binding: ManagedResourceBinding | None = None
    observed_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    rollback: RollbackDescriptor | None = None

    @model_validator(mode="after")
    def _mutating_action_requires_rollback(self):
        if self.action in {
            ProvisionActionKind.CREATE,
            ProvisionActionKind.UPDATE,
            ProvisionActionKind.IMPORT_AS_NEW_VERSION,
            ProvisionActionKind.RETIRE_STALE,
        } and self.rollback is None:
            raise ValueError("mutating provision action requires rollback descriptor")
        return self

    @property
    def mutating(self) -> bool:
        return self.action in {
            ProvisionActionKind.CREATE,
            ProvisionActionKind.UPDATE,
            ProvisionActionKind.IMPORT_AS_NEW_VERSION,
            ProvisionActionKind.RETIRE_STALE,
        }


class ProvisionSkip(FrozenModel):
    canonical_id: str = Field(min_length=1)
    resource_kind: ResourceKind
    reason: ProvisionSkipReason
    detail: str = Field(min_length=1)


class ProvisionPlan(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    desired_resources: tuple[DesiredResource, ...]
    actions: tuple[ProvisionAction, ...]
    skips: tuple[ProvisionSkip, ...]
    plan_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class SemanticResourceProvisionPlanner:
    """P9A planner. No external I/O and no implicit resource adoption."""

    _PROVISIONABLE = frozenset(
        {
            EquivalenceClassification.NATIVE_METABASE,
            EquivalenceClassification.DIMA_COMPILED,
        }
    )

    @staticmethod
    def _semantic_index(import_result: SemanticImportResult):
        spec = import_result.spec
        values: dict[str, tuple[ResourceKind, Any]] = {}

        def add(ref: str, kind: ResourceKind, value: Any) -> None:
            if ref in values:
                raise ResourceProvisioningError(
                    f"duplicate semantic resource id across kinds: {ref}"
                )
            values[ref] = (kind, value)

        for item in spec.metrics:
            add(item.metric_id, ResourceKind.METRIC, item)
        for item in spec.dimensions:
            add(item.dimension_id, ResourceKind.DIMENSION, item)
        for item in spec.time_specs:
            add(item.time_id, ResourceKind.TIME, item)
        for item in spec.relationships:
            add(item.relationship_id, ResourceKind.RELATIONSHIP, item)
        return values

    @staticmethod
    def _policy_index(
        policies: tuple[ManagedResourcePolicy, ...],
    ) -> dict[str, ManagedResourcePolicy]:
        output: dict[str, ManagedResourcePolicy] = {}
        for policy in policies:
            if policy.semantic_ref in output:
                raise ResourceProvisioningError(
                    f"duplicate managed resource policy: {policy.semantic_ref}"
                )
            output[policy.semantic_ref] = policy
        return output

    @staticmethod
    def _matrix_row(matrix: SemanticEquivalenceMatrix, semantic_ref: str):
        rows = [
            item
            for item in matrix.rows
            if item.feature_ref == semantic_ref
            and item.dima_state == DimaRepresentationState.REPRESENTED
        ]
        if len(rows) != 1:
            raise ResourceProvisioningError(
                f"semantic ref {semantic_ref} must have exactly one represented P8 row"
            )
        return rows[0]

    @staticmethod
    def _display_payload(spec, semantic_ref: str) -> tuple[dict[str, Any], ...]:
        return tuple(
            item.model_dump(mode="json")
            for item in spec.display_specs
            if item.semantic_ref == semantic_ref
        )

    @classmethod
    def _payload(
        cls,
        *,
        spec,
        semantic_ref: str,
        resource_kind: ResourceKind,
        semantic_object: Any,
        classification: EquivalenceClassification,
    ) -> dict[str, Any]:
        return {
            "canonical_id": semantic_ref,
            "resource_kind": resource_kind.value,
            "semantic_context_version": spec.semantic_context_version,
            "classification": classification.value,
            "semantic": semantic_object.model_dump(mode="json"),
            "display": cls._display_payload(spec, semantic_ref),
        }

    @staticmethod
    def _semantic_version(
        semantic_object: MetricSpec | DimensionSpec | TimeSpec | RelationshipSpec,
        *,
        semantic_context_version: str,
    ) -> str:
        value = getattr(semantic_object, "semantic_version", None)
        return (
            str(value)
            if isinstance(value, str) and value
            else semantic_context_version
        )

    @classmethod
    def _desired_and_skips(
        cls,
        *,
        tenant_binding: str,
        import_result: SemanticImportResult,
        matrix: SemanticEquivalenceMatrix,
    ) -> tuple[tuple[DesiredResource, ...], tuple[ProvisionSkip, ...]]:
        if matrix.source_fingerprint != import_result.source_fingerprint:
            raise ResourceProvisioningError(
                "P8 matrix source fingerprint does not match P7 import result"
            )

        spec = import_result.spec
        semantic_index = cls._semantic_index(import_result)
        policies = cls._policy_index(spec.managed_resources)
        desired: list[DesiredResource] = []
        skips: list[ProvisionSkip] = []

        for semantic_ref, policy in sorted(policies.items()):
            indexed = semantic_index.get(semantic_ref)
            if indexed is None:
                raise ResourceProvisioningError(
                    f"managed resource policy references unknown semantic id: {semantic_ref}"
                )
            resource_kind, semantic_object = indexed
            row = cls._matrix_row(matrix, semantic_ref)

            if policy.ownership != "DIMA_MANAGED":
                skips.append(
                    ProvisionSkip(
                        canonical_id=semantic_ref,
                        resource_kind=resource_kind,
                        reason=ProvisionSkipReason(policy.ownership),
                        detail="resource ownership is not DIMA_MANAGED",
                    )
                )
                continue

            if policy.reconciliation is None:
                raise ResourceProvisioningError(
                    f"DIMA_MANAGED policy lacks reconciliation: {semantic_ref}"
                )

            if row.classification not in cls._PROVISIONABLE:
                skips.append(
                    ProvisionSkip(
                        canonical_id=semantic_ref,
                        resource_kind=resource_kind,
                        reason=ProvisionSkipReason(
                            row.classification.value
                        ),
                        detail=(
                            "P8 classification is not provisionable in P9A"
                        ),
                    )
                )
                continue

            payload = cls._payload(
                spec=spec,
                semantic_ref=semantic_ref,
                resource_kind=resource_kind,
                semantic_object=semantic_object,
                classification=row.classification,
            )
            desired.append(
                DesiredResource(
                    tenant_binding=tenant_binding,
                    canonical_id=semantic_ref,
                    resource_kind=resource_kind,
                    semantic_context_version=spec.semantic_context_version,
                    desired_version=cls._semantic_version(
                        semantic_object,
                        semantic_context_version=spec.semantic_context_version,
                    ),
                    desired_fingerprint=_canonical_hash(payload),
                    payload=payload,
                    reconciliation=policy.reconciliation,
                )
            )

        return (
            tuple(
                sorted(
                    desired,
                    key=lambda item: (
                        item.resource_kind.value,
                        item.canonical_id,
                    ),
                )
            ),
            tuple(
                sorted(
                    skips,
                    key=lambda item: (
                        item.resource_kind.value,
                        item.canonical_id,
                    ),
                )
            ),
        )

    @staticmethod
    def _rollback_for_update(
        *,
        binding: ManagedResourceBinding,
        observed: ObservedMetabaseResource,
    ) -> RollbackDescriptor:
        return RollbackDescriptor(
            kind=RollbackKind.RESTORE_PREVIOUS_SNAPSHOT,
            prior_binding=binding,
            prior_payload=observed.managed_payload,
        )

    @classmethod
    def _action_for(
        cls,
        *,
        desired: DesiredResource,
        inventory: ResourceInventorySnapshot,
    ) -> ProvisionAction:
        binding = inventory.binding_for(
            tenant_binding=desired.tenant_binding,
            canonical_id=desired.canonical_id,
            resource_kind=desired.resource_kind,
        )

        if binding is None:
            return ProvisionAction(
                action=ProvisionActionKind.CREATE,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="UNBOUND_DIMA_MANAGED_RESOURCE",
                desired=desired,
                rollback=RollbackDescriptor(
                    kind=RollbackKind.ARCHIVE_CREATED_RESOURCE,
                ),
            )

        if binding.ownership != "DIMA_MANAGED":
            return ProvisionAction(
                action=ProvisionActionKind.REJECT_DRIFT,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="BOUND_RESOURCE_OWNERSHIP_CONFLICT",
                desired=desired,
                binding=binding,
            )

        observed = inventory.resource_for_binding(binding)
        if observed is None:
            return ProvisionAction(
                action=ProvisionActionKind.REJECT_DRIFT,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="BOUND_RESOURCE_MISSING",
                desired=desired,
                binding=binding,
            )

        if (
            observed.resource_fingerprint
            == desired.desired_fingerprint
            == binding.applied_fingerprint
        ):
            if (
                binding.semantic_context_version
                != desired.semantic_context_version
            ):
                return ProvisionAction(
                    action=ProvisionActionKind.REJECT_DRIFT,
                    canonical_id=desired.canonical_id,
                    resource_kind=desired.resource_kind,
                    reason_code="BINDING_CONTEXT_VERSION_DRIFT",
                    desired=desired,
                    binding=binding,
                    observed_fingerprint=observed.resource_fingerprint,
                )
            if binding.applied_version != desired.desired_version:
                return ProvisionAction(
                    action=ProvisionActionKind.REJECT_DRIFT,
                    canonical_id=desired.canonical_id,
                    resource_kind=desired.resource_kind,
                    reason_code="BINDING_APPLIED_VERSION_DRIFT",
                    desired=desired,
                    binding=binding,
                    observed_fingerprint=observed.resource_fingerprint,
                )
            return ProvisionAction(
                action=ProvisionActionKind.NOOP,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="DESIRED_STATE_ALREADY_APPLIED",
                desired=desired,
                binding=binding,
                observed_fingerprint=observed.resource_fingerprint,
            )

        if (
            observed.resource_fingerprint == desired.desired_fingerprint
            and binding.applied_fingerprint != desired.desired_fingerprint
        ):
            return ProvisionAction(
                action=ProvisionActionKind.REJECT_DRIFT,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="BINDING_FINGERPRINT_INCONSISTENT",
                desired=desired,
                binding=binding,
                observed_fingerprint=observed.resource_fingerprint,
            )

        if desired.reconciliation == "REJECT":
            return ProvisionAction(
                action=ProvisionActionKind.REJECT_DRIFT,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="RESOURCE_DRIFT_REJECTED_BY_POLICY",
                desired=desired,
                binding=binding,
                observed_fingerprint=observed.resource_fingerprint,
            )

        if desired.reconciliation == "OVERWRITE":
            return ProvisionAction(
                action=ProvisionActionKind.UPDATE,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="RESOURCE_DRIFT_OVERWRITE_POLICY",
                desired=desired,
                binding=binding,
                observed_fingerprint=observed.resource_fingerprint,
                rollback=cls._rollback_for_update(
                    binding=binding,
                    observed=observed,
                ),
            )

        if desired.reconciliation == "IMPORT_AS_NEW_VERSION":
            return ProvisionAction(
                action=ProvisionActionKind.IMPORT_AS_NEW_VERSION,
                canonical_id=desired.canonical_id,
                resource_kind=desired.resource_kind,
                reason_code="RESOURCE_DRIFT_IMPORT_NEW_VERSION_POLICY",
                desired=desired,
                binding=binding,
                observed_fingerprint=observed.resource_fingerprint,
                rollback=RollbackDescriptor(
                    kind=RollbackKind.RESTORE_PREVIOUS_BINDING,
                    prior_binding=binding,
                    prior_payload=observed.managed_payload,
                ),
            )

        raise AssertionError("validated reconciliation policy lost")

    @classmethod
    def _stale_actions(
        cls,
        *,
        tenant_binding: str,
        import_result: SemanticImportResult,
        matrix: SemanticEquivalenceMatrix,
        inventory: ResourceInventorySnapshot,
        desired: tuple[DesiredResource, ...],
    ) -> tuple[ProvisionAction, ...]:
        semantic_index = cls._semantic_index(import_result)
        policies = cls._policy_index(import_result.spec.managed_resources)
        desired_keys = {
            (
                item.tenant_binding,
                item.resource_kind.value,
                item.canonical_id,
            )
            for item in desired
        }

        actions: list[ProvisionAction] = []
        for binding in sorted(
            inventory.bindings,
            key=lambda item: (
                item.tenant_binding,
                item.resource_kind.value,
                item.canonical_id,
            ),
        ):
            if (
                binding.tenant_binding != tenant_binding
                or binding.ownership != "DIMA_MANAGED"
                or binding.binding_key in desired_keys
            ):
                continue

            indexed = semantic_index.get(binding.canonical_id)
            if indexed is None:
                observed = inventory.resource_for_binding(binding)
                actions.append(
                    ProvisionAction(
                        action=ProvisionActionKind.RETIRE_STALE,
                        canonical_id=binding.canonical_id,
                        resource_kind=binding.resource_kind,
                        reason_code="SEMANTIC_REMOVED_FROM_DESIRED_STATE",
                        binding=binding,
                        observed_fingerprint=(
                            observed.resource_fingerprint
                            if observed is not None
                            else None
                        ),
                        rollback=RollbackDescriptor(
                            kind=RollbackKind.RESTORE_PREVIOUS_BINDING,
                            prior_binding=binding,
                            prior_payload=(
                                observed.managed_payload
                                if observed is not None
                                else None
                            ),
                        ),
                    )
                )
                continue

            current_kind, _ = indexed
            if current_kind != binding.resource_kind:
                actions.append(
                    ProvisionAction(
                        action=ProvisionActionKind.REJECT_DRIFT,
                        canonical_id=binding.canonical_id,
                        resource_kind=binding.resource_kind,
                        reason_code="BINDING_RESOURCE_KIND_DRIFT",
                        binding=binding,
                    )
                )
                continue

            policy = policies.get(binding.canonical_id)
            if policy is None:
                actions.append(
                    ProvisionAction(
                        action=ProvisionActionKind.REJECT_DRIFT,
                        canonical_id=binding.canonical_id,
                        resource_kind=binding.resource_kind,
                        reason_code=(
                            "MANAGEMENT_POLICY_REMOVED_REQUIRES_EXPLICIT_DECISION"
                        ),
                        binding=binding,
                    )
                )
                continue

            if policy.ownership != "DIMA_MANAGED":
                actions.append(
                    ProvisionAction(
                        action=ProvisionActionKind.REJECT_DRIFT,
                        canonical_id=binding.canonical_id,
                        resource_kind=binding.resource_kind,
                        reason_code=(
                            "OWNERSHIP_TRANSFER_REQUIRES_EXPLICIT_DECISION"
                        ),
                        binding=binding,
                    )
                )
                continue

            row = cls._matrix_row(matrix, binding.canonical_id)
            if row.classification not in cls._PROVISIONABLE:
                actions.append(
                    ProvisionAction(
                        action=ProvisionActionKind.REJECT_DRIFT,
                        canonical_id=binding.canonical_id,
                        resource_kind=binding.resource_kind,
                        reason_code="REPRESENTATION_NO_LONGER_PROVISIONABLE",
                        binding=binding,
                    )
                )
                continue

            raise ResourceProvisioningError(
                "DIMA-managed provisionable binding disappeared from desired resources"
            )

        return tuple(actions)

    @classmethod
    def plan(
        cls,
        *,
        tenant_binding: str,
        import_result: SemanticImportResult,
        matrix: SemanticEquivalenceMatrix,
        inventory: ResourceInventorySnapshot,
    ) -> ProvisionPlan:
        if not tenant_binding.strip():
            raise ResourceProvisioningError("tenant_binding is required")

        desired, skips = cls._desired_and_skips(
            tenant_binding=tenant_binding,
            import_result=import_result,
            matrix=matrix,
        )
        desired_actions = [
            cls._action_for(
                desired=item,
                inventory=inventory,
            )
            for item in desired
        ]
        stale_actions = cls._stale_actions(
            tenant_binding=tenant_binding,
            import_result=import_result,
            matrix=matrix,
            inventory=inventory,
            desired=desired,
        )
        actions = tuple(
            sorted(
                (*desired_actions, *stale_actions),
                key=lambda item: (
                    item.resource_kind.value,
                    item.canonical_id,
                    item.action.value,
                ),
            )
        )
        payload = {
            "tenant_binding": tenant_binding,
            "semantic_context_version": (
                import_result.spec.semantic_context_version
            ),
            "desired_resources": [
                item.model_dump(mode="json")
                for item in desired
            ],
            "actions": [
                item.model_dump(mode="json")
                for item in actions
            ],
            "skips": [
                item.model_dump(mode="json")
                for item in skips
            ],
        }
        return ProvisionPlan(
            tenant_binding=tenant_binding,
            semantic_context_version=(
                import_result.spec.semantic_context_version
            ),
            desired_resources=desired,
            actions=actions,
            skips=skips,
            plan_fingerprint=_canonical_hash(payload),
        )
