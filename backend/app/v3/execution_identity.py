"""P5 execution/access identity and strict Dima query receipt sealing.

P5 defines immutable identity contracts only. It does not discover principals, inspect
Metabase permissions, inspect databases, map tenants, choose roles, or issue production
access snapshots. The production access issuer is P10-owned.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.analytics_contract import ResolvedAnalyticsIntent
from app.v3.evidence import DimaQueryReceipt
from app.v3.substrate.metabase.canonical import CanonicalProjection


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReceiptSealError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _sha256_json(value: Any, *, error_code: str) -> str:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ReceiptSealError(
            error_code,
            "value is not deterministic canonical JSON",
        ) from exc
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_unique_strings(
    *,
    field_name: str,
    values: tuple[str, ...],
    allow_empty: bool,
) -> None:
    if not allow_empty and not values:
        raise ValueError(f"{field_name} must not be empty")
    if any(not value.strip() for value in values):
        raise ValueError(f"{field_name} contains an empty value")
    if len(values) != len(set(values)):
        raise ValueError(f"{field_name} contains duplicates")


class ExecutionAccessSnapshot(FrozenModel):
    """Attested non-secret effective-access statement.

    Facts are supplied by an external issuer. This model only validates and fingerprints
    them. It deliberately has no defaults for security-bearing fields.
    """

    tenant_binding: str = Field(min_length=1)
    principal_subject: str = Field(min_length=1)
    roles: tuple[str, ...]
    attribute_policy_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    policy_version: str = Field(min_length=1)
    rls_versions: tuple[str, ...]
    cls_versions: tuple[str, ...]
    database_route: str = Field(min_length=1)
    database_destination: str = Field(min_length=1)
    impersonation_role: str | None
    semantic_context_version: str = Field(min_length=1)
    source_object_refs: tuple[str, ...] = Field(min_length=1)
    security_parameter_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    attestation_refs: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_sets(self):
        _validate_unique_strings(
            field_name="roles",
            values=self.roles,
            allow_empty=True,
        )
        _validate_unique_strings(
            field_name="rls_versions",
            values=self.rls_versions,
            allow_empty=True,
        )
        _validate_unique_strings(
            field_name="cls_versions",
            values=self.cls_versions,
            allow_empty=True,
        )
        _validate_unique_strings(
            field_name="source_object_refs",
            values=self.source_object_refs,
            allow_empty=False,
        )
        _validate_unique_strings(
            field_name="attestation_refs",
            values=self.attestation_refs,
            allow_empty=False,
        )
        if self.impersonation_role is not None and not self.impersonation_role.strip():
            raise ValueError("impersonation_role must be null or non-empty")
        return self

    @property
    def role_set_digest(self) -> str:
        return _sha256_json(
            sorted(self.roles),
            error_code="ROLE_SET_NOT_SERIALIZABLE",
        )

    @property
    def execution_access_fingerprint(self) -> str:
        # attestation_refs identify the proof records, not the effective access lens itself.
        payload = {
            "tenant_binding": self.tenant_binding,
            "principal_subject": self.principal_subject,
            "role_set_digest": self.role_set_digest,
            "attribute_policy_digest": self.attribute_policy_digest,
            "policy_version": self.policy_version,
            "rls_versions": sorted(self.rls_versions),
            "cls_versions": sorted(self.cls_versions),
            "database_route": self.database_route,
            "database_destination": self.database_destination,
            "impersonation_role": self.impersonation_role,
            "semantic_context_version": self.semantic_context_version,
            "source_object_refs": sorted(self.source_object_refs),
            "security_parameter_digest": self.security_parameter_digest,
        }
        return _sha256_json(
            payload,
            error_code="ACCESS_SNAPSHOT_NOT_SERIALIZABLE",
        )


class RuntimeIdentity(FrozenModel):
    substrate: str = Field(min_length=1)
    runtime_version: str = Field(min_length=1)
    image_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    database_id: str = Field(min_length=1)


class ExecutionEventIdentity(FrozenModel):
    execution_id: str = Field(min_length=1)
    executed_at: datetime

    @model_validator(mode="after")
    def _timezone_aware(self):
        if self.executed_at.tzinfo is None or self.executed_at.utcoffset() is None:
            raise ValueError("executed_at must be timezone-aware")
        return self


class ExecutionResultSnapshot(FrozenModel):
    payload: Any
    row_count: int = Field(ge=0)
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @property
    def result_hash(self) -> str:
        return _sha256_json(
            self.payload,
            error_code="RESULT_NOT_CANONICAL_JSON",
        )


class DimaQueryReceiptSealer:
    """Single strict P5 seal point. No semantic interpretation or external I/O."""

    @staticmethod
    def _assert_projection_matches(
        *,
        intent: ResolvedAnalyticsIntent,
        projection: CanonicalProjection,
    ) -> None:
        checks = (
            (
                "AUTHORITY_MISMATCH",
                intent.authority_id,
                projection.authority_id,
            ),
            (
                "PROJECTION_MISMATCH",
                intent.projection_hash,
                projection.projection_hash,
            ),
            (
                "RESOLVED_INTENT_MISMATCH",
                intent.resolved_intent_hash,
                projection.resolved_intent_hash,
            ),
            (
                "SEMANTIC_CONTEXT_MISMATCH",
                intent.semantic_context_version,
                projection.semantic_context_version,
            ),
        )
        for code, expected, actual in checks:
            if expected != actual:
                raise ReceiptSealError(
                    code,
                    f"intent={expected!r} canonical={actual!r}",
                )

    @staticmethod
    def _resource_bindings(
        projection: CanonicalProjection,
    ) -> tuple[tuple[str, str], ...]:
        entity_ids = projection.manifest.resource_entity_ids
        fingerprints = projection.manifest.resource_fingerprints

        if len(entity_ids) != len(fingerprints):
            raise ReceiptSealError(
                "RESOURCE_IDENTITY_CARDINALITY_MISMATCH",
                (
                    f"entity_ids={len(entity_ids)} "
                    f"fingerprints={len(fingerprints)}"
                ),
            )
        if not entity_ids:
            raise ReceiptSealError(
                "RESOURCE_IDENTITY_MISSING",
                "canonical projection has no stable resource entity ids",
            )
        if len(entity_ids) != len(set(entity_ids)):
            raise ReceiptSealError(
                "RESOURCE_IDENTITY_DUPLICATE",
                "canonical projection has duplicate resource entity ids",
            )

        return tuple(zip(entity_ids, fingerprints, strict=True))

    @staticmethod
    def _assert_access_matches(
        *,
        intent: ResolvedAnalyticsIntent,
        projection: CanonicalProjection,
        access: ExecutionAccessSnapshot,
    ) -> None:
        principal = intent.principal
        if access.tenant_binding != principal.tenant_binding:
            raise ReceiptSealError(
                "TENANT_MISMATCH",
                "access tenant does not match resolved intent principal",
            )
        if access.principal_subject != principal.principal_subject:
            raise ReceiptSealError(
                "PRINCIPAL_MISMATCH",
                "access subject does not match resolved intent principal",
            )
        if tuple(sorted(access.roles)) != tuple(sorted(principal.roles)):
            raise ReceiptSealError(
                "ROLE_SET_MISMATCH",
                "access roles do not match resolved intent principal roles",
            )
        if access.semantic_context_version != intent.semantic_context_version:
            raise ReceiptSealError(
                "ACCESS_SEMANTIC_CONTEXT_MISMATCH",
                "access snapshot belongs to a different semantic context",
            )

        resource_bindings = DimaQueryReceiptSealer._resource_bindings(
            projection
        )
        entity_ids = tuple(entity_id for entity_id, _ in resource_bindings)
        if tuple(sorted(access.source_object_refs)) != tuple(sorted(entity_ids)):
            raise ReceiptSealError(
                "SOURCE_RESOURCE_MISMATCH",
                "access source-object refs do not exactly cover canonical resource ids",
            )

    @classmethod
    def _receipt_fingerprint(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        projection: CanonicalProjection,
        step_fingerprint: str,
        step_role: str,
        access: ExecutionAccessSnapshot,
        runtime: RuntimeIdentity,
        result: ExecutionResultSnapshot,
    ) -> str:
        resource_bindings = cls._resource_bindings(projection)
        payload = {
            "authority_id": intent.authority_id,
            "projection_hash": intent.projection_hash,
            "resolved_intent_hash": intent.resolved_intent_hash,
            "canonical_query_fingerprint": step_fingerprint,
            "execution_access_fingerprint": access.execution_access_fingerprint,
            "access_attestation_refs": sorted(access.attestation_refs),
            "semantic_context_version": intent.semantic_context_version,
            "resource_bindings": sorted(
                resource_bindings,
                key=lambda item: (item[0], item[1]),
            ),
            "substrate": runtime.substrate,
            "substrate_runtime_version": runtime.runtime_version,
            "substrate_image_digest": runtime.image_digest,
            "database_id": runtime.database_id,
            "result_hash": result.result_hash,
            "row_count": result.row_count,
            "step_role": step_role,
            "warnings": result.warnings,
            "limitations": result.limitations,
        }
        return _sha256_json(
            payload,
            error_code="RECEIPT_CONTENT_NOT_SERIALIZABLE",
        )

    @staticmethod
    def _receipt_id(
        *,
        receipt_fingerprint: str,
        execution_id: str,
    ) -> str:
        raw = f"{receipt_fingerprint}\x1f{execution_id}"
        return "dqr_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    @classmethod
    def seal_execution(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        projection: CanonicalProjection,
        access_snapshot: ExecutionAccessSnapshot | None,
        runtime: RuntimeIdentity | None,
        results: tuple[ExecutionResultSnapshot, ...],
        events: tuple[ExecutionEventIdentity, ...],
    ) -> tuple[DimaQueryReceipt, ...]:
        if access_snapshot is None:
            raise ReceiptSealError(
                "ACCESS_SNAPSHOT_REQUIRED",
                "official P5 receipt requires an explicit attested access snapshot",
            )
        if runtime is None:
            raise ReceiptSealError(
                "RUNTIME_IDENTITY_REQUIRED",
                "official P5 receipt requires exact runtime identity",
            )

        cls._assert_projection_matches(
            intent=intent,
            projection=projection,
        )
        cls._assert_access_matches(
            intent=intent,
            projection=projection,
            access=access_snapshot,
        )

        query_count = len(projection.steps)
        if len(results) != query_count or len(events) != query_count:
            raise ReceiptSealError(
                "QUERY_RESULT_CARDINALITY_MISMATCH",
                (
                    f"queries={query_count} results={len(results)} "
                    f"events={len(events)}"
                ),
            )
        execution_ids = tuple(event.execution_id for event in events)
        if len(execution_ids) != len(set(execution_ids)):
            raise ReceiptSealError(
                "DUPLICATE_EXECUTION_ID",
                "each executed query step requires a distinct execution occurrence id",
            )

        principal_fingerprint = intent.principal.fingerprint
        access_fingerprint = access_snapshot.execution_access_fingerprint
        semantic_refs = projection.manifest.semantic_ids
        resource_entity_ids = projection.manifest.resource_entity_ids
        resource_fingerprints = projection.manifest.resource_fingerprints

        receipts: list[DimaQueryReceipt] = []
        for step, result, event in zip(
            projection.steps,
            results,
            events,
            strict=True,
        ):
            receipt_fingerprint = cls._receipt_fingerprint(
                intent=intent,
                projection=projection,
                step_fingerprint=step.canonical_query_fingerprint,
                step_role=step.role,
                access=access_snapshot,
                runtime=runtime,
                result=result,
            )
            receipts.append(
                DimaQueryReceipt(
                    receipt_id=cls._receipt_id(
                        receipt_fingerprint=receipt_fingerprint,
                        execution_id=event.execution_id,
                    ),
                    receipt_fingerprint=receipt_fingerprint,
                    execution_id=event.execution_id,
                    step_role=step.role,
                    authority_id=intent.authority_id,
                    obligation_ids=intent.obligation_ids,
                    tenant_id=intent.principal.tenant_binding,
                    principal_id=intent.principal.principal_subject,
                    semantic_refs=semantic_refs,
                    projection_hash=intent.projection_hash,
                    resolved_intent_hash=intent.resolved_intent_hash,
                    canonical_query_fingerprint=step.canonical_query_fingerprint,
                    canonical_query_representation=step.decoded_query,
                    ephemeral_query_handle=None,
                    principal_fingerprint=principal_fingerprint,
                    execution_access_fingerprint=access_fingerprint,
                    access_attestation_refs=access_snapshot.attestation_refs,
                    semantic_context_version=intent.semantic_context_version,
                    resource_entity_ids=resource_entity_ids,
                    resource_fingerprints=resource_fingerprints,
                    substrate=runtime.substrate,
                    substrate_runtime_version=runtime.runtime_version,
                    substrate_image_digest=runtime.image_digest,
                    database_id=runtime.database_id,
                    executed_at=event.executed_at,
                    result_hash=result.result_hash,
                    row_count=result.row_count,
                    warnings=result.warnings,
                    limitations=result.limitations,
                )
            )

        return tuple(receipts)
