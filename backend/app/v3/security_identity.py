"""P10A provider-free production access-snapshot issuer contract.

This module does not discover permissions, log in to Metabase, inspect policy stores,
query databases, or widen access. It only proves that already-verified security facts
belong to the current Dima principal, accepted analytics intent, and canonical projection,
then issues the existing P5 ExecutionAccessSnapshot.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.analytics_contract import ResolvedAnalyticsIntent
from app.v3.execution_identity import ExecutionAccessSnapshot
from app.v3.substrate.metabase.canonical import CanonicalProjection
from app.v3.native_execution import (
    AuthorizedExecutionArtifact,
    NativeExecutionTrustError,
    authorized_artifact_from_canonical_projection,
)
from control_plane.authorize import Principal


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SecurityIdentityError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _validate_unique_refs(
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


class VerifiedExecutionSecurityFacts(FrozenModel):
    """Explicit attested facts supplied by future P10 production security owners.

    This envelope has deliberately no fingerprint property. Durable access identity remains
    P5 ExecutionAccessSnapshot.execution_access_fingerprint.
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
    metabase_subject_ref: str = Field(min_length=1)
    attestation_refs: tuple[str, ...] = Field(min_length=1)
    evidence_refs: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_sets(self):
        _validate_unique_refs(
            field_name="roles",
            values=self.roles,
            allow_empty=True,
        )
        _validate_unique_refs(
            field_name="rls_versions",
            values=self.rls_versions,
            allow_empty=True,
        )
        _validate_unique_refs(
            field_name="cls_versions",
            values=self.cls_versions,
            allow_empty=True,
        )
        _validate_unique_refs(
            field_name="source_object_refs",
            values=self.source_object_refs,
            allow_empty=False,
        )
        _validate_unique_refs(
            field_name="attestation_refs",
            values=self.attestation_refs,
            allow_empty=False,
        )
        _validate_unique_refs(
            field_name="evidence_refs",
            values=self.evidence_refs,
            allow_empty=False,
        )
        if self.impersonation_role is not None and not self.impersonation_role.strip():
            raise ValueError("impersonation_role must be null or non-empty")
        return self


class ExecutionAccessSnapshotIssuer:
    """Fail-closed P10A assembler for the existing P5 access snapshot.

    P13A generalizes only the execution-resource descriptor. Principal, tenant, role,
    semantic-context and verified-source checks remain P10-owned and unchanged in strength.
    """

    @staticmethod
    def _current_principal(
        current_principal: Principal | None,
    ) -> Principal:
        if current_principal is None:
            raise SecurityIdentityError(
                "P10_CURRENT_PRINCIPAL_REQUIRED",
                "production access issuance requires the current authenticated Dima principal",
            )
        if not current_principal.user_id.strip():
            raise SecurityIdentityError(
                "P10_CURRENT_PRINCIPAL_SUBJECT_MISSING",
                "current Dima principal has no stable user subject",
            )
        return current_principal

    @staticmethod
    def _assert_projection(
        *,
        intent: ResolvedAnalyticsIntent,
        projection: CanonicalProjection,
    ) -> None:
        checks = (
            ("P10_AUTHORITY_MISMATCH", intent.authority_id, projection.authority_id),
            ("P10_PROJECTION_MISMATCH", intent.projection_hash, projection.projection_hash),
            (
                "P10_RESOLVED_INTENT_MISMATCH",
                intent.resolved_intent_hash,
                projection.resolved_intent_hash,
            ),
            (
                "P10_SEMANTIC_CONTEXT_MISMATCH",
                intent.semantic_context_version,
                projection.semantic_context_version,
            ),
        )
        for code, expected, actual in checks:
            if expected != actual:
                raise SecurityIdentityError(
                    code,
                    f"intent={expected!r} projection={actual!r}",
                )

    @staticmethod
    def _assert_execution_artifact(
        *,
        intent: ResolvedAnalyticsIntent,
        artifact: AuthorizedExecutionArtifact,
    ) -> None:
        try:
            artifact.assert_intact()
        except NativeExecutionTrustError as exc:
            raise SecurityIdentityError(exc.code, exc.detail) from exc

        checks = (
            ("P10_AUTHORITY_MISMATCH", intent.authority_id, artifact.authority_id),
            ("P10_PROJECTION_MISMATCH", intent.projection_hash, artifact.projection_hash),
            (
                "P10_RESOLVED_INTENT_MISMATCH",
                intent.resolved_intent_hash,
                artifact.resolved_intent_hash,
            ),
            (
                "P10_SEMANTIC_CONTEXT_MISMATCH",
                intent.semantic_context_version,
                artifact.semantic_context_version,
            ),
        )
        for code, expected, actual in checks:
            if expected != actual:
                raise SecurityIdentityError(
                    code,
                    f"intent={expected!r} artifact={actual!r}",
                )

    @classmethod
    def _execution_artifact(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        canonical_projection: CanonicalProjection | None,
        execution_artifact: AuthorizedExecutionArtifact | None,
    ) -> AuthorizedExecutionArtifact:
        if canonical_projection is not None and execution_artifact is not None:
            raise SecurityIdentityError(
                "P10_EXECUTION_ARTIFACT_AMBIGUOUS",
                "supply canonical_projection or execution_artifact, not both",
            )
        if canonical_projection is None and execution_artifact is None:
            raise SecurityIdentityError(
                "P10_EXECUTION_ARTIFACT_REQUIRED",
                "production access issuance requires an authorized execution artifact",
            )
        if canonical_projection is not None:
            cls._assert_projection(
                intent=intent,
                projection=canonical_projection,
            )
            resource_ids = canonical_projection.manifest.resource_entity_ids
            fingerprints = canonical_projection.manifest.resource_fingerprints
            if len(resource_ids) != len(fingerprints):
                raise SecurityIdentityError(
                    "P10_PROJECTION_RESOURCE_IDENTITY_CARDINALITY_MISMATCH",
                    "canonical projection resource ids/fingerprints differ in cardinality",
                )
            if not resource_ids:
                raise SecurityIdentityError(
                    "P10_PROJECTION_RESOURCE_IDENTITY_REQUIRED",
                    "canonical projection has no stable source-resource ids",
                )
            if len(resource_ids) != len(set(resource_ids)):
                raise SecurityIdentityError(
                    "P10_PROJECTION_RESOURCE_IDENTITY_DUPLICATE",
                    "canonical projection has duplicate source-resource ids",
                )
            try:
                artifact = authorized_artifact_from_canonical_projection(
                    canonical_projection
                )
            except NativeExecutionTrustError as exc:
                raise SecurityIdentityError(exc.code, exc.detail) from exc
        else:
            artifact = execution_artifact
            assert artifact is not None

        cls._assert_execution_artifact(intent=intent, artifact=artifact)
        return artifact

    @staticmethod
    def _assert_principal(
        *,
        principal: Principal,
        intent: ResolvedAnalyticsIntent,
        facts: VerifiedExecutionSecurityFacts,
    ) -> None:
        accepted = intent.principal

        if principal.user_id != accepted.principal_subject:
            raise SecurityIdentityError(
                "P10_CURRENT_ACCEPTED_PRINCIPAL_MISMATCH",
                "current Dima principal does not match accepted analytics principal",
            )
        if facts.principal_subject != accepted.principal_subject:
            raise SecurityIdentityError(
                "P10_FACTS_PRINCIPAL_MISMATCH",
                "verified security facts belong to a different principal",
            )

        current_roles = tuple(sorted(principal.roles))
        accepted_roles = tuple(sorted(accepted.roles))
        fact_roles = tuple(sorted(facts.roles))
        if current_roles != accepted_roles:
            raise SecurityIdentityError(
                "P10_CURRENT_ACCEPTED_ROLE_MISMATCH",
                "current Dima roles do not match accepted analytics roles",
            )
        if fact_roles != accepted_roles:
            raise SecurityIdentityError(
                "P10_FACTS_ROLE_MISMATCH",
                "verified security facts belong to a different role set",
            )

        accepted_tenant = accepted.tenant_binding
        if facts.tenant_binding != accepted_tenant:
            raise SecurityIdentityError(
                "P10_FACTS_TENANT_MISMATCH",
                "verified security facts belong to a different tenant lens",
            )

        if principal.is_superadmin:
            if principal.tenant_id is not None and principal.tenant_id != accepted_tenant:
                raise SecurityIdentityError(
                    "P10_SUPERADMIN_TENANT_MISMATCH",
                    "explicit superadmin tenant does not match accepted tenant lens",
                )
        else:
            if not principal.tenant_id:
                raise SecurityIdentityError(
                    "P10_CURRENT_TENANT_REQUIRED",
                    "non-superadmin production access issuance requires a tenant",
                )
            if principal.tenant_id != accepted_tenant:
                raise SecurityIdentityError(
                    "P10_CURRENT_ACCEPTED_TENANT_MISMATCH",
                    "current Dima tenant does not match accepted tenant lens",
                )

    @staticmethod
    def _assert_security_scope(
        *,
        intent: ResolvedAnalyticsIntent,
        resource_ids: tuple[str, ...],
        facts: VerifiedExecutionSecurityFacts,
    ) -> None:
        if facts.semantic_context_version != intent.semantic_context_version:
            raise SecurityIdentityError(
                "P10_FACTS_SEMANTIC_CONTEXT_MISMATCH",
                "verified security facts belong to a different semantic context",
            )

        if not resource_ids:
            raise SecurityIdentityError(
                "P10_PROJECTION_RESOURCE_IDENTITY_REQUIRED",
                "execution scope has no stable source-resource ids",
            )
        if any(not item.strip() for item in resource_ids):
            raise SecurityIdentityError(
                "P10_PROJECTION_RESOURCE_IDENTITY_REQUIRED",
                "execution scope contains an empty source-resource id",
            )
        if len(resource_ids) != len(set(resource_ids)):
            raise SecurityIdentityError(
                "P10_PROJECTION_RESOURCE_IDENTITY_DUPLICATE",
                "execution scope has duplicate source-resource ids",
            )
        if tuple(sorted(facts.source_object_refs)) != tuple(sorted(resource_ids)):
            raise SecurityIdentityError(
                "P10_SOURCE_OBJECT_MISMATCH",
                "verified security facts do not exactly cover Dima-authorized execution resources",
            )

        if not facts.metabase_subject_ref.strip():
            raise SecurityIdentityError(
                "P10_METABASE_SUBJECT_REQUIRED",
                "verified Metabase authenticated subject is required",
            )

    @staticmethod
    def _snapshot(
        *,
        accepted_intent: ResolvedAnalyticsIntent,
        verified_security_facts: VerifiedExecutionSecurityFacts,
    ) -> ExecutionAccessSnapshot:
        proof_refs = tuple(
            sorted(
                {
                    *verified_security_facts.attestation_refs,
                    *verified_security_facts.evidence_refs,
                    verified_security_facts.metabase_subject_ref,
                }
            )
        )
        return ExecutionAccessSnapshot(
            tenant_binding=accepted_intent.principal.tenant_binding,
            principal_subject=accepted_intent.principal.principal_subject,
            roles=tuple(sorted(accepted_intent.principal.roles)),
            attribute_policy_digest=verified_security_facts.attribute_policy_digest,
            policy_version=verified_security_facts.policy_version,
            rls_versions=tuple(sorted(verified_security_facts.rls_versions)),
            cls_versions=tuple(sorted(verified_security_facts.cls_versions)),
            database_route=verified_security_facts.database_route,
            database_destination=verified_security_facts.database_destination,
            impersonation_role=verified_security_facts.impersonation_role,
            semantic_context_version=accepted_intent.semantic_context_version,
            source_object_refs=tuple(sorted(verified_security_facts.source_object_refs)),
            security_parameter_digest=verified_security_facts.security_parameter_digest,
            attestation_refs=proof_refs,
        )

    @classmethod
    def issue_for_expected_resources(
        cls,
        *,
        current_principal: Principal | None,
        accepted_intent: ResolvedAnalyticsIntent,
        verified_security_facts: VerifiedExecutionSecurityFacts,
        expected_source_object_refs: tuple[str, ...],
    ) -> ExecutionAccessSnapshot:
        """Issue the same P5 access identity from accepted Dima resource truth.

        P13C uses this before native candidate authorization only to bind current-user
        value evidence to the durable P5/P10 execution_access_fingerprint. It creates
        no second fingerprint or access model.
        """

        principal = cls._current_principal(current_principal)
        cls._assert_principal(
            principal=principal,
            intent=accepted_intent,
            facts=verified_security_facts,
        )
        cls._assert_security_scope(
            intent=accepted_intent,
            resource_ids=expected_source_object_refs,
            facts=verified_security_facts,
        )
        return cls._snapshot(
            accepted_intent=accepted_intent,
            verified_security_facts=verified_security_facts,
        )

    @classmethod
    def issue(
        cls,
        *,
        current_principal: Principal | None,
        accepted_intent: ResolvedAnalyticsIntent,
        verified_security_facts: VerifiedExecutionSecurityFacts,
        canonical_projection: CanonicalProjection | None = None,
        execution_artifact: AuthorizedExecutionArtifact | None = None,
    ) -> ExecutionAccessSnapshot:
        principal = cls._current_principal(current_principal)
        artifact = cls._execution_artifact(
            intent=accepted_intent,
            canonical_projection=canonical_projection,
            execution_artifact=execution_artifact,
        )
        cls._assert_principal(
            principal=principal,
            intent=accepted_intent,
            facts=verified_security_facts,
        )
        cls._assert_security_scope(
            intent=accepted_intent,
            resource_ids=artifact.resource_entity_ids,
            facts=verified_security_facts,
        )
        return cls._snapshot(
            accepted_intent=accepted_intent,
            verified_security_facts=verified_security_facts,
        )
