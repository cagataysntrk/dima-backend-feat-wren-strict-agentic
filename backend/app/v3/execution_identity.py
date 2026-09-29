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
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.analytics_contract import ResolvedAnalyticsIntent
from app.v3.evidence import DimaQueryReceipt
from app.v3.substrate.metabase.canonical import CanonicalProjection
from app.v3.native_execution import (
    AuthorizedExecutionArtifact,
    NativeExecutionTrustError,
    authorized_artifact_from_canonical_projection,
)


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
    repository: str | None = None
    revision_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    upstream_base_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    runtime_tag: str | None = None
    build_identity: str | None = None
    image_identity: str | None = None
    runtime_instance_id: UUID | None = None


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
            ("AUTHORITY_MISMATCH", intent.authority_id, projection.authority_id),
            ("PROJECTION_MISMATCH", intent.projection_hash, projection.projection_hash),
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
    def _resource_bindings_from_projection(
        projection: CanonicalProjection,
    ) -> tuple[tuple[str, str], ...]:
        entity_ids = projection.manifest.resource_entity_ids
        fingerprints = projection.manifest.resource_fingerprints
        if len(entity_ids) != len(fingerprints):
            raise ReceiptSealError(
                "RESOURCE_IDENTITY_CARDINALITY_MISMATCH",
                f"entity_ids={len(entity_ids)} fingerprints={len(fingerprints)}",
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
    def _assert_artifact_matches(
        *,
        intent: ResolvedAnalyticsIntent,
        artifact: AuthorizedExecutionArtifact,
    ) -> None:
        try:
            artifact.assert_intact()
        except NativeExecutionTrustError as exc:
            raise ReceiptSealError(exc.code, exc.detail) from exc

        checks = (
            ("AUTHORITY_MISMATCH", intent.authority_id, artifact.authority_id),
            ("PROJECTION_MISMATCH", intent.projection_hash, artifact.projection_hash),
            (
                "RESOLVED_INTENT_MISMATCH",
                intent.resolved_intent_hash,
                artifact.resolved_intent_hash,
            ),
            (
                "SEMANTIC_CONTEXT_MISMATCH",
                intent.semantic_context_version,
                artifact.semantic_context_version,
            ),
        )
        for code, expected, actual in checks:
            if expected != actual:
                raise ReceiptSealError(
                    code,
                    f"intent={expected!r} artifact={actual!r}",
                )

    @classmethod
    def _execution_artifact(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        projection: CanonicalProjection | None,
        execution_artifact: AuthorizedExecutionArtifact | None,
    ) -> AuthorizedExecutionArtifact:
        if projection is not None and execution_artifact is not None:
            raise ReceiptSealError(
                "EXECUTION_ARTIFACT_AMBIGUOUS",
                "supply projection or execution_artifact, not both",
            )
        if projection is None and execution_artifact is None:
            raise ReceiptSealError(
                "EXECUTION_ARTIFACT_REQUIRED",
                "official receipt requires the exact authorized execution artifact",
            )
        if projection is not None:
            cls._assert_projection_matches(intent=intent, projection=projection)
            cls._resource_bindings_from_projection(projection)
            try:
                artifact = authorized_artifact_from_canonical_projection(projection)
            except NativeExecutionTrustError as exc:
                raise ReceiptSealError(exc.code, exc.detail) from exc
        else:
            artifact = execution_artifact
            assert artifact is not None
        cls._assert_artifact_matches(intent=intent, artifact=artifact)
        return artifact

    @staticmethod
    def _resource_bindings(
        artifact: AuthorizedExecutionArtifact,
    ) -> tuple[tuple[str, str], ...]:
        return tuple(
            (item.resource_id, item.resource_fingerprint)
            for item in artifact.resource_bindings
        )

    @staticmethod
    def _assert_access_matches(
        *,
        intent: ResolvedAnalyticsIntent,
        artifact: AuthorizedExecutionArtifact,
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
        entity_ids = artifact.resource_entity_ids
        if tuple(sorted(access.source_object_refs)) != tuple(sorted(entity_ids)):
            raise ReceiptSealError(
                "SOURCE_RESOURCE_MISMATCH",
                "access source-object refs do not exactly cover authorized resource ids",
            )

    @staticmethod
    def _assert_runtime_matches_artifact(
        *,
        artifact: AuthorizedExecutionArtifact,
        runtime: RuntimeIdentity,
    ) -> None:
        if runtime.substrate != "metabase-native":
            return
        engine = artifact.engine_identity
        if engine.substrate != runtime.substrate:
            raise ReceiptSealError(
                "NATIVE_RUNTIME_SUBSTRATE_MISMATCH",
                "authorized artifact and executing runtime use different substrates",
            )
        required = {
            "artifact.repository": engine.repository,
            "artifact.revision_sha": engine.revision_sha,
            "artifact.upstream_base_sha": engine.upstream_base_sha,
            "artifact.runtime_tag": engine.runtime_tag,
            "artifact.build_identity": engine.build_identity,
            "artifact.runtime_image_identity": engine.runtime_image_identity,
            "artifact.runtime_instance_id": engine.runtime_instance_id,
            "runtime.repository": runtime.repository,
            "runtime.revision_sha": runtime.revision_sha,
            "runtime.upstream_base_sha": runtime.upstream_base_sha,
            "runtime.runtime_tag": runtime.runtime_tag,
            "runtime.build_identity": runtime.build_identity,
            "runtime.image_identity": runtime.image_identity,
            "runtime.runtime_instance_id": runtime.runtime_instance_id,
        }
        missing = sorted(name for name, value in required.items() if value is None)
        if missing:
            raise ReceiptSealError(
                "NATIVE_RUNTIME_IDENTITY_REQUIRED",
                "missing exact native runtime identity: " + ", ".join(missing),
            )
        checks = (
            ("NATIVE_RUNTIME_REPOSITORY_MISMATCH", engine.repository, runtime.repository),
            ("NATIVE_RUNTIME_REVISION_MISMATCH", engine.revision_sha, runtime.revision_sha),
            ("NATIVE_RUNTIME_UPSTREAM_MISMATCH", engine.upstream_base_sha, runtime.upstream_base_sha),
            ("NATIVE_RUNTIME_TAG_MISMATCH", engine.runtime_tag, runtime.runtime_tag),
            ("NATIVE_RUNTIME_BUILD_MISMATCH", engine.build_identity, runtime.build_identity),
            ("NATIVE_RUNTIME_IMAGE_IDENTITY_MISMATCH", engine.runtime_image_identity, runtime.image_identity),
            ("NATIVE_RUNTIME_INSTANCE_MISMATCH", str(engine.runtime_instance_id), str(runtime.runtime_instance_id)),
        )
        for code, expected, actual in checks:
            if expected != actual:
                raise ReceiptSealError(code, f"authorized={expected!r} runtime={actual!r}")
        if runtime.runtime_version != runtime.runtime_tag:
            raise ReceiptSealError(
                "NATIVE_RUNTIME_VERSION_TAG_MISMATCH",
                "runtime_version must equal the attested native runtime tag",
            )
        if engine.runtime_image_digest is not None and engine.runtime_image_digest != runtime.image_digest:
            raise ReceiptSealError(
                "NATIVE_RUNTIME_IMAGE_DIGEST_MISMATCH",
                "authorized image digest differs from executing runtime digest",
            )

    @classmethod
    def _receipt_fingerprint(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        artifact: AuthorizedExecutionArtifact,
        step_fingerprint: str,
        step_role: str,
        access: ExecutionAccessSnapshot,
        runtime: RuntimeIdentity,
        result: ExecutionResultSnapshot,
    ) -> str:
        resource_bindings = cls._resource_bindings(artifact)
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
            "engine_repository": runtime.repository,
            "engine_revision_sha": runtime.revision_sha,
            "engine_upstream_base_sha": runtime.upstream_base_sha,
            "engine_runtime_tag": runtime.runtime_tag,
            "engine_build_identity": runtime.build_identity,
            "engine_image_identity": runtime.image_identity,
            "engine_runtime_instance_id": (
                str(runtime.runtime_instance_id)
                if runtime.runtime_instance_id is not None
                else None
            ),
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

    @staticmethod
    def _assert_research_runtime(runtime: RuntimeIdentity) -> None:
        if runtime.substrate != "metabase-native":
            raise ReceiptSealError(
                "NATIVE_RUNTIME_SUBSTRATE_MISMATCH",
                "P14 native Research receipt requires metabase-native substrate",
            )
        required = {
            "repository": runtime.repository,
            "revision_sha": runtime.revision_sha,
            "upstream_base_sha": runtime.upstream_base_sha,
            "runtime_tag": runtime.runtime_tag,
            "build_identity": runtime.build_identity,
            "image_identity": runtime.image_identity,
            "runtime_instance_id": runtime.runtime_instance_id,
        }
        missing = sorted(name for name, value in required.items() if value is None)
        if missing:
            raise ReceiptSealError(
                "NATIVE_RUNTIME_IDENTITY_REQUIRED",
                "missing exact native runtime identity: " + ", ".join(missing),
            )
        if runtime.runtime_version != runtime.runtime_tag:
            raise ReceiptSealError(
                "NATIVE_RUNTIME_VERSION_TAG_MISMATCH",
                "runtime_version must equal the attested native runtime tag",
            )

    @classmethod
    def seal_research_execution(
        cls,
        *,
        authority_id: str,
        research_session_id: str,
        obligation_ids: tuple[str, ...],
        tenant_binding: str,
        principal_subject: str,
        roles: tuple[str, ...],
        native_subject_ref: str,
        native_conversation_id: UUID,
        native_query_id: str,
        native_query_provenance_ref: str,
        native_result_provenance_ref: str,
        query_fingerprint: str,
        semantic_context_version: str,
        runtime: RuntimeIdentity | None,
        result: ExecutionResultSnapshot,
        event: ExecutionEventIdentity,
        resource_entity_ids: tuple[str, ...] = (),
        resource_fingerprints: tuple[str, ...] = (),
        semantic_refs: tuple[str, ...] = (),
    ) -> DimaQueryReceipt:
        """Seal direct native Research provenance through the single P5 receipt family.

        This path does not create a Standard projection, ResolvedAnalyticsIntent,
        AuthorizedExecutionArtifact, or P10 access snapshot.
        """
        if runtime is None:
            raise ReceiptSealError(
                "RUNTIME_IDENTITY_REQUIRED",
                "Research receipt requires exact native runtime identity",
            )
        cls._assert_research_runtime(runtime)
        if not obligation_ids:
            raise ReceiptSealError(
                "RESEARCH_OBLIGATION_REQUIRED",
                "Research material receipt requires an obligation",
            )
        if not native_subject_ref.strip():
            raise ReceiptSealError(
                "NATIVE_SUBJECT_REQUIRED",
                "Research material receipt requires the authenticated native subject",
            )
        if not native_query_id.strip():
            raise ReceiptSealError(
                "NATIVE_QUERY_ID_REQUIRED",
                "Research material receipt requires the captured native query id",
            )
        if len(resource_entity_ids) != len(resource_fingerprints):
            raise ReceiptSealError(
                "RESOURCE_IDENTITY_CARDINALITY_MISMATCH",
                "optional Research resource ids/fingerprints differ in cardinality",
            )
        if len(resource_entity_ids) != len(set(resource_entity_ids)):
            raise ReceiptSealError(
                "RESOURCE_IDENTITY_DUPLICATE",
                "Research receipt contains duplicate resource ids",
            )

        principal_fingerprint = _sha256_json(
            {
                "tenant_binding": tenant_binding,
                "principal_subject": principal_subject,
                "roles": sorted(roles),
            },
            error_code="PRINCIPAL_NOT_SERIALIZABLE",
        )
        receipt_fingerprint = _sha256_json(
            {
                "authority_kind": "research_material",
                "authority_id": authority_id,
                "research_session_id": research_session_id,
                "obligation_ids": sorted(obligation_ids),
                "tenant_binding": tenant_binding,
                "principal_subject": principal_subject,
                "native_subject_ref": native_subject_ref,
                "native_conversation_id": str(native_conversation_id),
                "native_query_id": native_query_id,
                "native_query_provenance_ref": native_query_provenance_ref,
                "native_result_provenance_ref": native_result_provenance_ref,
                "canonical_query_fingerprint": query_fingerprint,
                "semantic_context_version": semantic_context_version,
                "semantic_refs": sorted(semantic_refs),
                "resource_bindings": sorted(
                    zip(resource_entity_ids, resource_fingerprints, strict=True)
                ),
                "substrate": runtime.substrate,
                "substrate_runtime_version": runtime.runtime_version,
                "substrate_image_digest": runtime.image_digest,
                "engine_repository": runtime.repository,
                "engine_revision_sha": runtime.revision_sha,
                "engine_upstream_base_sha": runtime.upstream_base_sha,
                "engine_runtime_tag": runtime.runtime_tag,
                "engine_build_identity": runtime.build_identity,
                "engine_image_identity": runtime.image_identity,
                "engine_runtime_instance_id": str(runtime.runtime_instance_id),
                "database_id": runtime.database_id,
                "result_hash": result.result_hash,
                "row_count": result.row_count,
                "warnings": result.warnings,
                "limitations": result.limitations,
            },
            error_code="RECEIPT_CONTENT_NOT_SERIALIZABLE",
        )
        return DimaQueryReceipt(
            receipt_id=cls._receipt_id(
                receipt_fingerprint=receipt_fingerprint,
                execution_id=event.execution_id,
            ),
            receipt_fingerprint=receipt_fingerprint,
            execution_id=event.execution_id,
            step_role="primary",
            authority_kind="research_material",
            authority_id=authority_id,
            obligation_ids=obligation_ids,
            tenant_id=tenant_binding,
            principal_id=principal_subject,
            semantic_refs=semantic_refs,
            projection_hash=None,
            resolved_intent_hash=None,
            research_session_id=research_session_id,
            native_subject_ref=native_subject_ref,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            native_query_provenance_ref=native_query_provenance_ref,
            native_result_provenance_ref=native_result_provenance_ref,
            canonical_query_fingerprint=query_fingerprint,
            canonical_query_representation=None,
            ephemeral_query_handle=None,
            principal_fingerprint=principal_fingerprint,
            execution_access_fingerprint=None,
            access_attestation_refs=(),
            semantic_context_version=semantic_context_version,
            resource_entity_ids=resource_entity_ids,
            resource_fingerprints=resource_fingerprints,
            substrate=runtime.substrate,
            substrate_runtime_version=runtime.runtime_version,
            substrate_image_digest=runtime.image_digest,
            engine_repository=runtime.repository,
            engine_revision_sha=runtime.revision_sha,
            engine_upstream_base_sha=runtime.upstream_base_sha,
            engine_runtime_tag=runtime.runtime_tag,
            engine_build_identity=runtime.build_identity,
            engine_image_identity=runtime.image_identity,
            engine_runtime_instance_id=runtime.runtime_instance_id,
            database_id=runtime.database_id,
            executed_at=event.executed_at,
            result_hash=result.result_hash,
            row_count=result.row_count,
            warnings=result.warnings,
            limitations=result.limitations,
        )

    @classmethod
    def seal_execution(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        projection: CanonicalProjection | None = None,
        execution_artifact: AuthorizedExecutionArtifact | None = None,
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

        artifact = cls._execution_artifact(
            intent=intent,
            projection=projection,
            execution_artifact=execution_artifact,
        )
        cls._assert_access_matches(
            intent=intent,
            artifact=artifact,
            access=access_snapshot,
        )
        cls._assert_runtime_matches_artifact(
            artifact=artifact,
            runtime=runtime,
        )

        query_count = artifact.query_count
        if len(results) != query_count or len(events) != query_count:
            raise ReceiptSealError(
                "QUERY_RESULT_CARDINALITY_MISMATCH",
                f"queries={query_count} results={len(results)} events={len(events)}",
            )
        execution_ids = tuple(event.execution_id for event in events)
        if len(execution_ids) != len(set(execution_ids)):
            raise ReceiptSealError(
                "DUPLICATE_EXECUTION_ID",
                "each executed query step requires a distinct execution occurrence id",
            )

        principal_fingerprint = intent.principal.fingerprint
        access_fingerprint = access_snapshot.execution_access_fingerprint
        semantic_refs = artifact.semantic_refs
        resource_entity_ids = artifact.resource_entity_ids
        resource_fingerprints = artifact.resource_fingerprints

        receipts: list[DimaQueryReceipt] = []
        for step, result, event in zip(
            artifact.steps,
            results,
            events,
            strict=True,
        ):
            step.assert_intact()
            receipt_fingerprint = cls._receipt_fingerprint(
                intent=intent,
                artifact=artifact,
                step_fingerprint=step.artifact_fingerprint,
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
                    canonical_query_fingerprint=step.artifact_fingerprint,
                    canonical_query_representation=step.artifact_representation,
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
                    engine_repository=runtime.repository,
                    engine_revision_sha=runtime.revision_sha,
                    engine_upstream_base_sha=runtime.upstream_base_sha,
                    engine_runtime_tag=runtime.runtime_tag,
                    engine_build_identity=runtime.build_identity,
                    engine_image_identity=runtime.image_identity,
                    engine_runtime_instance_id=runtime.runtime_instance_id,
                    database_id=runtime.database_id,
                    executed_at=event.executed_at,
                    result_hash=result.result_hash,
                    row_count=result.row_count,
                    warnings=result.warnings,
                    limitations=result.limitations,
                )
            )
        return tuple(receipts)
