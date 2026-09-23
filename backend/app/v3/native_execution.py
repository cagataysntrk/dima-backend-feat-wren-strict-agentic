"""P13A native Metabot candidate trust-boundary contracts.

Native Metabot authors analytical query candidates. This module does not plan analytics,
resolve user language, choose metrics/joins, execute queries, or promote Evidence.
It binds an exact native candidate artifact to already-accepted Dima semantic authority
and emits the single engine-independent execution-artifact identity consumed by P10/P5.
"""
from __future__ import annotations

import copy
import hashlib
import json
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.analytics_contract import ResolvedAnalyticsIntent, ResolvedPeriod
from app.v3.substrate.metabase.canonical import CanonicalProjection
from app.v3.substrate.metabase.native_models import NativeEngineIdentity


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class NativeExecutionTrustError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _sha256_json(value: Any, *, code: str) -> str:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise NativeExecutionTrustError(
            code,
            "artifact is not deterministic canonical JSON",
        ) from exc
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _unique_nonempty(values: tuple[str, ...], *, field_name: str) -> None:
    if not values:
        raise ValueError(f"{field_name} must not be empty")
    if any(not value.strip() for value in values):
        raise ValueError(f"{field_name} contains an empty value")
    if len(values) != len(set(values)):
        raise ValueError(f"{field_name} contains duplicates")


class ExecutionResourceBinding(FrozenModel):
    resource_id: str = Field(min_length=1)
    resource_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class ExecutionSubstrateIdentity(FrozenModel):
    substrate: str = Field(min_length=1)
    repository: str | None = None
    revision_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    upstream_base_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    runtime_tag: str | None = None
    runtime_image_digest: str | None = None


class ExecutionArtifactStep(FrozenModel):
    role: Literal["primary", "base", "reference"]
    artifact_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    artifact_representation: dict[str, Any]

    @model_validator(mode="after")
    def _fingerprint_matches_representation(self):
        actual = _sha256_json(
            self.artifact_representation,
            code="EXECUTION_ARTIFACT_NOT_SERIALIZABLE",
        )
        if actual != self.artifact_fingerprint:
            raise ValueError(
                "artifact_fingerprint does not match exact artifact_representation"
            )
        return self

    def assert_intact(self) -> None:
        actual = _sha256_json(
            self.artifact_representation,
            code="EXECUTION_ARTIFACT_NOT_SERIALIZABLE",
        )
        if actual != self.artifact_fingerprint:
            raise NativeExecutionTrustError(
                "EXECUTION_ARTIFACT_MUTATED",
                "authorized execution artifact changed after fingerprinting",
            )


class AuthorizedExecutionArtifact(FrozenModel):
    """Engine-independent identity of the exact material execution Dima authorized."""

    authority_id: str = Field(min_length=1)
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    resolved_intent_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    semantic_context_version: str = Field(min_length=1)
    semantic_refs: tuple[str, ...] = Field(min_length=1)
    resource_bindings: tuple[ExecutionResourceBinding, ...] = Field(min_length=1)
    steps: tuple[ExecutionArtifactStep, ...] = Field(min_length=1)
    query_count: int = Field(ge=1)
    engine_identity: ExecutionSubstrateIdentity
    provenance_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_identity_sets(self):
        _unique_nonempty(self.semantic_refs, field_name="semantic_refs")
        resource_ids = tuple(item.resource_id for item in self.resource_bindings)
        _unique_nonempty(resource_ids, field_name="resource_bindings.resource_id")
        step_roles = tuple(item.role for item in self.steps)
        if len(step_roles) != len(set(step_roles)):
            raise ValueError("execution step roles must be unique")
        if self.query_count != len(self.steps):
            raise ValueError("query_count must exactly match execution steps")
        if any(not ref.strip() for ref in self.provenance_refs):
            raise ValueError("provenance_refs contains an empty value")
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("provenance_refs contains duplicates")
        return self

    @property
    def resource_entity_ids(self) -> tuple[str, ...]:
        return tuple(item.resource_id for item in self.resource_bindings)

    @property
    def resource_fingerprints(self) -> tuple[str, ...]:
        return tuple(item.resource_fingerprint for item in self.resource_bindings)

    def assert_intact(self) -> None:
        for step in self.steps:
            step.assert_intact()

    def assert_execution_matches(
        self,
        *,
        role: Literal["primary", "base", "reference"],
        artifact_representation: dict[str, Any],
    ) -> None:
        self.assert_intact()
        step = next((item for item in self.steps if item.role == role), None)
        if step is None:
            raise NativeExecutionTrustError(
                "EXECUTION_ARTIFACT_ROLE_MISSING",
                f"authorized execution has no {role!r} step",
            )
        actual = _sha256_json(
            artifact_representation,
            code="EXECUTION_ARTIFACT_NOT_SERIALIZABLE",
        )
        if actual != step.artifact_fingerprint:
            raise NativeExecutionTrustError(
                "EXECUTION_ARTIFACT_MISMATCH",
                "artifact presented for execution differs from the artifact Dima authorized",
            )


def authorized_artifact_from_canonical_projection(
    projection: CanonicalProjection,
) -> AuthorizedExecutionArtifact:
    """Compatibility adapter for the historical Agent-API CanonicalProjection."""

    if len(projection.manifest.resource_entity_ids) != len(
        projection.manifest.resource_fingerprints
    ):
        raise NativeExecutionTrustError(
            "RESOURCE_IDENTITY_CARDINALITY_MISMATCH",
            "canonical projection resource ids/fingerprints differ in cardinality",
        )

    resource_bindings = tuple(
        ExecutionResourceBinding(
            resource_id=resource_id,
            resource_fingerprint=fingerprint,
        )
        for resource_id, fingerprint in zip(
            projection.manifest.resource_entity_ids,
            projection.manifest.resource_fingerprints,
            strict=True,
        )
    )
    steps = tuple(
        ExecutionArtifactStep(
            role=step.role,
            artifact_fingerprint=step.canonical_query_fingerprint,
            artifact_representation=copy.deepcopy(step.decoded_query),
        )
        for step in projection.steps
    )
    return AuthorizedExecutionArtifact(
        authority_id=projection.authority_id,
        projection_hash=projection.projection_hash,
        resolved_intent_hash=projection.resolved_intent_hash,
        semantic_context_version=projection.semantic_context_version,
        semantic_refs=projection.manifest.semantic_ids,
        resource_bindings=resource_bindings,
        steps=steps,
        query_count=len(steps),
        engine_identity=ExecutionSubstrateIdentity(
            substrate="metabase-agent-api",
        ),
    )


def period_scope_fingerprint(period: ResolvedPeriod | None) -> str | None:
    if period is None:
        return None
    return _sha256_json(
        period.model_dump(mode="json"),
        code="TIME_SCOPE_NOT_SERIALIZABLE",
    )


class NativeQueryCandidate(FrozenModel):
    """One exact native Metabot query occurrence plus Dima-inspection facts."""

    engine_identity: NativeEngineIdentity
    dima_request_id: str = Field(min_length=1)
    dima_trace_id: str = Field(min_length=1)
    native_conversation_id: UUID
    native_query_id: str = Field(min_length=1)
    resolved_pmbql: dict[str, Any]
    portable_query: dict[str, Any] | None = None
    semantic_refs: tuple[str, ...] = Field(min_length=1)
    resource_bindings: tuple[ExecutionResourceBinding, ...] = Field(min_length=1)
    native_validation_refs: tuple[str, ...] = Field(min_length=1)
    time_scope_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    material_filter_count: int = Field(default=0, ge=0)
    material_join_count: int = Field(default=0, ge=0)
    query_count: int = Field(default=1, ge=1)
    candidate_artifact_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def _validate_candidate(self):
        _unique_nonempty(self.semantic_refs, field_name="semantic_refs")
        _unique_nonempty(
            self.native_validation_refs,
            field_name="native_validation_refs",
        )
        resource_ids = tuple(item.resource_id for item in self.resource_bindings)
        _unique_nonempty(resource_ids, field_name="resource_bindings.resource_id")
        actual = _sha256_json(
            self.resolved_pmbql,
            code="NATIVE_CANDIDATE_NOT_SERIALIZABLE",
        )
        if actual != self.candidate_artifact_fingerprint:
            raise ValueError(
                "candidate_artifact_fingerprint does not match exact resolved_pmbql"
            )
        return self

    @classmethod
    def build(
        cls,
        *,
        engine_identity: NativeEngineIdentity,
        dima_request_id: str,
        dima_trace_id: str,
        native_conversation_id: UUID | str,
        native_query_id: str,
        resolved_pmbql: dict[str, Any],
        portable_query: dict[str, Any] | None,
        semantic_refs: tuple[str, ...],
        resource_bindings: tuple[ExecutionResourceBinding, ...],
        native_validation_refs: tuple[str, ...],
        time_scope_fingerprint: str | None = None,
        material_filter_count: int = 0,
        material_join_count: int = 0,
        query_count: int = 1,
    ) -> "NativeQueryCandidate":
        artifact = copy.deepcopy(resolved_pmbql)
        return cls(
            engine_identity=engine_identity,
            dima_request_id=dima_request_id,
            dima_trace_id=dima_trace_id,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            resolved_pmbql=artifact,
            portable_query=copy.deepcopy(portable_query),
            semantic_refs=semantic_refs,
            resource_bindings=resource_bindings,
            native_validation_refs=native_validation_refs,
            time_scope_fingerprint=time_scope_fingerprint,
            material_filter_count=material_filter_count,
            material_join_count=material_join_count,
            query_count=query_count,
            candidate_artifact_fingerprint=_sha256_json(
                artifact,
                code="NATIVE_CANDIDATE_NOT_SERIALIZABLE",
            ),
        )

    def assert_intact(self) -> None:
        actual = _sha256_json(
            self.resolved_pmbql,
            code="NATIVE_CANDIDATE_NOT_SERIALIZABLE",
        )
        if actual != self.candidate_artifact_fingerprint:
            raise NativeExecutionTrustError(
                "NATIVE_CANDIDATE_ARTIFACT_MUTATED",
                "native candidate changed after its exact-artifact fingerprint was created",
            )


class NativeCandidateOutcome(StrEnum):
    ALLOW = "ALLOW"
    CLARIFY_REPLAN = "CLARIFY_REPLAN"
    BLOCK = "BLOCK"


class NativeCandidateAuthorization(FrozenModel):
    outcome: NativeCandidateOutcome
    code: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    authorized_artifact: AuthorizedExecutionArtifact | None = None

    @model_validator(mode="after")
    def _artifact_only_on_allow(self):
        if self.outcome == NativeCandidateOutcome.ALLOW:
            if self.authorized_artifact is None:
                raise ValueError("ALLOW requires authorized_artifact")
        elif self.authorized_artifact is not None:
            raise ValueError("non-ALLOW decision must not carry authorized_artifact")
        return self


class NativeCandidateAuthorizationGate:
    """P13A bounded verifier. It never writes or repairs a query."""

    @staticmethod
    def _decision(
        outcome: NativeCandidateOutcome,
        code: str,
        detail: str,
    ) -> NativeCandidateAuthorization:
        return NativeCandidateAuthorization(
            outcome=outcome,
            code=code,
            detail=detail,
        )

    @staticmethod
    def _binding_pairs(
        bindings: tuple[ExecutionResourceBinding, ...],
    ) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted(
                (
                    item.resource_id,
                    item.resource_fingerprint,
                )
                for item in bindings
            )
        )

    @classmethod
    def authorize(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        candidate: NativeQueryCandidate,
        authorized_resource_bindings: tuple[ExecutionResourceBinding, ...],
    ) -> NativeCandidateAuthorization:
        try:
            candidate.assert_intact()
        except NativeExecutionTrustError as exc:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                exc.code,
                exc.detail,
            )

        if (
            len(intent.metrics) != 1
            or intent.dimensions
            or intent.filters
            or intent.comparison is not None
            or intent.ranking is not None
            or intent.approved_relationship_paths
            or intent.grain_constraints
        ):
            return cls._decision(
                NativeCandidateOutcome.CLARIFY_REPLAN,
                "P13A_CAPABILITY_UNSUPPORTED",
                "P13A certifies one metric/source with optional period only",
            )

        expected_semantic_refs = tuple(
            item.semantic_ref for item in intent.metrics
        )
        if tuple(candidate.semantic_refs) != expected_semantic_refs:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "SEMANTIC_SCOPE_VIOLATION",
                "native candidate semantic refs exceed or differ from accepted intent",
            )

        if cls._binding_pairs(candidate.resource_bindings) != cls._binding_pairs(
            authorized_resource_bindings
        ):
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "RESOURCE_PROVENANCE_MISMATCH",
                "native candidate resource bindings differ from Dima-authorized resources",
            )

        if candidate.query_count != 1:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "QUERY_COUNT_VIOLATION",
                "P13A authorizes exactly one material query",
            )

        if candidate.material_filter_count:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "SEMANTIC_SCOPE_VIOLATION",
                "P13A candidate introduced an unaccepted material filter",
            )

        if candidate.material_join_count:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "RELATIONSHIP_GRAIN_VIOLATION",
                "P13A candidate introduced an unapproved join",
            )

        expected_time = period_scope_fingerprint(intent.period)
        if candidate.time_scope_fingerprint != expected_time:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "TIME_SCOPE_VIOLATION",
                "native candidate time scope differs from accepted intent",
            )

        step = ExecutionArtifactStep(
            role="primary",
            artifact_fingerprint=candidate.candidate_artifact_fingerprint,
            artifact_representation=copy.deepcopy(candidate.resolved_pmbql),
        )
        artifact = AuthorizedExecutionArtifact(
            authority_id=intent.authority_id,
            projection_hash=intent.projection_hash,
            resolved_intent_hash=intent.resolved_intent_hash,
            semantic_context_version=intent.semantic_context_version,
            semantic_refs=expected_semantic_refs,
            resource_bindings=tuple(
                copy.deepcopy(authorized_resource_bindings)
            ),
            steps=(step,),
            query_count=1,
            engine_identity=ExecutionSubstrateIdentity(
                substrate="metabase-native",
                repository=candidate.engine_identity.repository,
                revision_sha=candidate.engine_identity.engine_sha,
                upstream_base_sha=candidate.engine_identity.upstream_base_sha,
                runtime_tag=candidate.engine_identity.runtime_tag,
                runtime_image_digest=candidate.engine_identity.runtime_image_digest,
            ),
            provenance_refs=tuple(candidate.native_validation_refs),
        )
        return NativeCandidateAuthorization(
            outcome=NativeCandidateOutcome.ALLOW,
            code="P13A_NATIVE_CANDIDATE_AUTHORIZED",
            detail="exact native artifact is within the certified P13A authority surface",
            authorized_artifact=artifact,
        )

    @classmethod
    def revalidate_candidate(
        cls,
        *,
        candidate: NativeQueryCandidate,
        authorized_artifact: AuthorizedExecutionArtifact,
    ) -> NativeCandidateAuthorization:
        try:
            candidate.assert_intact()
            authorized_artifact.assert_intact()
        except NativeExecutionTrustError as exc:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                exc.code,
                exc.detail,
            )

        if authorized_artifact.query_count != 1:
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "EXECUTION_ARTIFACT_MISMATCH",
                "authorized P13A artifact is not single-query",
            )
        if (
            authorized_artifact.steps[0].artifact_fingerprint
            != candidate.candidate_artifact_fingerprint
        ):
            return cls._decision(
                NativeCandidateOutcome.BLOCK,
                "EXECUTION_ARTIFACT_MISMATCH",
                "candidate changed after authorization",
            )
        return NativeCandidateAuthorization(
            outcome=NativeCandidateOutcome.ALLOW,
            code="P13A_NATIVE_CANDIDATE_REVALIDATED",
            detail="candidate still matches the exact authorized artifact",
            authorized_artifact=authorized_artifact,
        )
