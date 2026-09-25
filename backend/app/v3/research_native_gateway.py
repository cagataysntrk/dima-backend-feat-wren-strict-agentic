"""P14 thin native Research gateway authorized by DMP-DEC-0047.

Metabot/Metabase own analytical cognition. This module owns only product-material
identity, resource, runtime and exact-occurrence correlation.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    RuntimeIdentity,
)
from app.v3.native_execution import (
    AuthorizedExecutionArtifact,
    ExecutionArtifactStep,
    ExecutionResourceBinding,
)
from app.v3.native_standard.contracts import NativeAttestationEnvelope, NativeExecutionManifest
from app.v3.research import ResearchSession
from app.v3.research_product import ResearchMaterialLimitation, ResearchMaterialOutcome
from app.v3.security_identity import (
    ExecutionAccessSnapshotIssuer,
    SecurityIdentityError,
    VerifiedExecutionSecurityFacts,
)
from app.v3.substrate.metabase.native_engine import NativeEngineBridge, NativeEngineBridgeError
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import NativeResourceBinding, NativeSubjectBinding

BASIC_NATIVE = "BASIC_NATIVE"


def _hash(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False, default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _uuid(value: str, code: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ResearchMaterialLimitation(
            code, "native Research binding requires stable UUID Dima identity"
        ) from exc


def _tenant_uuid(principal: Principal, session: ResearchSession) -> uuid.UUID:
    if principal.is_superadmin or principal.tenant_id is None:
        raise ResearchMaterialLimitation(
            "P14_NATIVE_TENANT_USER_REQUIRED",
            "native Research does not use superadmin or tenantless analytical fallback",
        )
    tenant_id = _uuid(principal.tenant_id, "P14_NATIVE_TENANT_ID_INVALID")
    if session.tenant_binding != f"id:{tenant_id}":
        raise ResearchMaterialLimitation(
            "P14_NATIVE_TENANT_MISMATCH",
            "Research tenant differs from current Dima principal",
        )
    return tenant_id


class NativeSubjectSessionProvider:
    def __init__(self, *, base_url: str, expected_identity: NativeEngineIdentity, db_engine=None):
        self._base_url = base_url.rstrip("/")
        self._expected = expected_identity
        self._engine = db_engine or control_plane_engine
        if not self._base_url:
            raise ValueError("native Metabase base_url is required")

    def binding_for(self, *, principal: Principal, session: ResearchSession) -> NativeSubjectBinding:
        tenant_id = _tenant_uuid(principal, session)
        user_id = _uuid(principal.user_id, "P14_NATIVE_DIMA_USER_ID_INVALID")
        if session.principal_subject != str(principal.user_id):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_PRINCIPAL_MISMATCH",
                "Research principal differs from current Dima principal",
            )
        with Session(self._engine) as db:
            rows = db.exec(
                select(NativeSubjectBinding)
                .where(NativeSubjectBinding.tenant_id == tenant_id)
                .where(NativeSubjectBinding.dima_user_id == user_id)
                .where(NativeSubjectBinding.enabled == True)
            ).all()
        if len(rows) != 1:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_SUBJECT_BINDING_MISSING",
                "exactly one enabled Dima-to-Metabase subject binding is required",
            )
        binding = rows[0]
        if binding.security_profile != BASIC_NATIVE:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_SECURITY_PROFILE_UNSUPPORTED",
                "only explicitly configured BASIC_NATIVE is supported by this slice",
            )
        if not binding.policy_version.strip():
            raise ResearchMaterialLimitation(
                "P14_NATIVE_SECURITY_POLICY_VERSION_MISSING",
                "native subject binding requires an explicit policy version",
            )
        return binding

    def _assert_engine_identity(self, observed: dict[str, Any]) -> None:
        checks = [
            ("repository", self._expected.repository),
            ("revision_sha", self._expected.engine_sha),
            ("upstream_base_sha", self._expected.upstream_base_sha),
            ("runtime_tag", self._expected.runtime_tag),
        ]
        if self._expected.build_identity is not None:
            checks.append(("build_identity", self._expected.build_identity))
        if self._expected.runtime_image_identity is not None:
            checks.append(("image_identity", self._expected.runtime_image_identity))
        for field, expected in checks:
            if str(observed.get(field) or "") != str(expected):
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_ENGINE_IDENTITY_MISMATCH",
                    f"native engine {field} does not match pinned runtime",
                )

    @contextmanager
    def open(self, *, principal: Principal, session: ResearchSession, native_session_token: str | None):
        binding = self.binding_for(principal=principal, session=session)
        token = str(native_session_token or "").strip()
        if not token:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_SESSION_REQUIRED",
                "an already-authenticated principal-scoped Metabase session is required",
            )
        bridge = NativeEngineBridge(
            base_url=self._base_url,
            session_token=token,
            expected_identity=self._expected,
        )
        try:
            current = bridge.current_user()
            if int(current["id"]) != int(binding.metabase_user_id):
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_SUBJECT_MISMATCH",
                    "pass-through Metabase session belongs to another native subject",
                )
            if bool(current.get("is_superuser")):
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_ADMIN_SESSION_FORBIDDEN",
                    "native Research cannot use a Metabase superuser session",
                )
            self._assert_engine_identity(bridge.engine_identity())
            yield bridge
        finally:
            bridge.close()


class NativeResourceBindingProvider:
    def __init__(self, *, db_engine=None):
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _accepted_refs(session: ResearchSession, obligation_id: str):
        brief = session.accepted_brief
        if brief is None:
            raise ResearchMaterialLimitation(
                "P14_ACCEPTED_RESEARCH_CONTEXT_MISSING", "accepted ResearchBrief required"
            )
        matches = tuple(q for q in brief.questions if q.goal_id == obligation_id)
        if len(matches) != 1:
            raise ResearchMaterialLimitation(
                "P14_ACCEPTED_RESEARCH_OBLIGATION_MISMATCH", "accepted question mismatch"
            )
        seen = set()
        values = []
        for item in (*matches[0].subject_refs, *matches[0].related_refs):
            key = (item.candidate_id, item.target_kind.value)
            if key not in seen:
                seen.add(key)
                values.append(item)
        if not values:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_RESOURCE_CONTEXT_MISSING",
                "Research obligation has no resolver-proven business resource context",
            )
        return tuple(values)

    @staticmethod
    def _field_ids(manifest: NativeExecutionManifest) -> set[int]:
        values: set[int] = set()
        for item in manifest.aggregations:
            values.update(int(x) for x in item.referenced_field_ids)
        values.update(int(x.time_field_id) for x in manifest.temporal_predicates)
        values.update(int(x.field_id) for x in manifest.textual_equality_predicates)
        values.update(int(x.field_id) for x in manifest.breakouts)
        values.update(int(x.field_id) for x in manifest.order_bys if x.field_id is not None)
        return values

    @classmethod
    def _assert_locator(cls, binding: NativeResourceBinding, manifest: NativeExecutionManifest) -> None:
        if binding.metabase_database_id != manifest.database_id:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_RESOURCE_DATABASE_MISMATCH", "resource belongs to another database"
            )
        tables = set(int(x) for x in manifest.referenced_source_table_ids)
        fields = cls._field_ids(manifest)
        metrics = {
            int(x.metabase_metric_id): str(x.metabase_metric_entity_id)
            for x in manifest.native_metric_references
        }
        if binding.locator_kind == "table":
            ok = binding.metabase_table_id is not None and binding.metabase_table_id in tables
        elif binding.locator_kind == "field":
            ok = binding.metabase_field_id is not None and binding.metabase_field_id in fields
            if ok and binding.metabase_table_id is not None:
                ok = binding.metabase_table_id in tables
        elif binding.locator_kind == "metric":
            ok = binding.metabase_metric_id is not None and binding.metabase_metric_id in metrics
            if ok and binding.metabase_entity_id is not None:
                ok = metrics[binding.metabase_metric_id] == binding.metabase_entity_id
        else:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_RESOURCE_LOCATOR_KIND_UNSUPPORTED", binding.locator_kind
            )
        if not ok:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_RESOURCE_LOCATOR_MISMATCH",
                "mapped native locator is absent from the exact occurrence",
            )

    def resolve(self, *, principal: Principal, session: ResearchSession, obligation_id: str, manifest: NativeExecutionManifest):
        tenant_id = _tenant_uuid(principal, session)
        refs = self._accepted_refs(session, obligation_id)
        semantic_ids = []
        resources = {}
        provenance = []
        with Session(self._engine) as db:
            for ref in refs:
                rows = db.exec(
                    select(NativeResourceBinding)
                    .where(NativeResourceBinding.tenant_id == tenant_id)
                    .where(NativeResourceBinding.semantic_context_version == session.context_version)
                    .where(NativeResourceBinding.candidate_id == ref.candidate_id)
                    .where(NativeResourceBinding.candidate_kind == ref.target_kind.value)
                    .where(NativeResourceBinding.enabled == True)
                ).all()
                if len(rows) != 1:
                    raise ResearchMaterialLimitation(
                        "P14_NATIVE_RESOURCE_BINDING_MISSING",
                        f"exact resource binding missing for {ref.candidate_id}",
                    )
                binding = rows[0]
                if binding.canonical_name != ref.canonical_name:
                    raise ResearchMaterialLimitation(
                        "P14_NATIVE_RESOURCE_BINDING_STALE",
                        "accepted business concept differs from current explicit mapping",
                    )
                if not binding.semantic_id.strip() or not binding.resource_version.strip():
                    raise ResearchMaterialLimitation(
                        "P14_NATIVE_RESOURCE_BINDING_STALE",
                        "resource mapping has no durable semantic/version identity",
                    )
                if len(binding.resource_fingerprint) != 64 or any(
                    ch not in "0123456789abcdef" for ch in binding.resource_fingerprint
                ):
                    raise ResearchMaterialLimitation(
                        "P14_NATIVE_RESOURCE_FINGERPRINT_INVALID", "invalid resource fingerprint"
                    )
                self._assert_locator(binding, manifest)
                semantic_ids.append(binding.semantic_id)
                resource = ExecutionResourceBinding(
                    resource_id=binding.resource_entity_id,
                    resource_fingerprint=binding.resource_fingerprint,
                )
                prior = resources.get(resource.resource_id)
                if prior is not None and prior != resource:
                    raise ResearchMaterialLimitation(
                        "P14_NATIVE_RESOURCE_FINGERPRINT_CONFLICT",
                        "one resource id has conflicting fingerprints",
                    )
                resources[resource.resource_id] = resource
                provenance.append(f"native-resource-binding:{binding.id}:{binding.resource_version}")
        return (
            tuple(dict.fromkeys(semantic_ids)),
            tuple(resources[key] for key in sorted(resources)),
            tuple(provenance),
        )


class NativeResearchMaterialExecutor:
    def __init__(self, *, subject_provider, resource_provider, expected_identity: NativeEngineIdentity):
        self._subjects = subject_provider
        self._resources = resource_provider
        self._expected = expected_identity

    def _engine_pin(self, manifest: NativeExecutionManifest) -> None:
        runtime = manifest.runtime_identity
        checks = [
            (runtime.repository, self._expected.repository),
            (runtime.revision_sha, self._expected.engine_sha),
            (runtime.upstream_base_sha, self._expected.upstream_base_sha),
            (runtime.runtime_tag, self._expected.runtime_tag),
        ]
        if self._expected.build_identity is not None:
            checks.append((runtime.build_identity, self._expected.build_identity))
        if self._expected.runtime_image_identity is not None:
            checks.append((runtime.image_identity, self._expected.runtime_image_identity))
        if any(observed != expected for observed, expected in checks):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_ENGINE_IDENTITY_MISMATCH", "attested runtime differs from pin"
            )

    @staticmethod
    def _row_count(payload: dict[str, Any]) -> int:
        if isinstance(payload.get("row_count"), int):
            return max(0, int(payload["row_count"]))
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            return len(data["rows"])
        if isinstance(payload.get("rows"), list):
            return len(payload["rows"])
        return 0

    def execute(self, *, principal, session, obligation_id, bridge, native_conversation_id, native_query_id):
        binding = self._subjects.binding_for(principal=principal, session=session)
        try:
            attestation = NativeAttestationEnvelope.model_validate(
                bridge.attest_native_query(
                    conversation_id=native_conversation_id,
                    native_query_id=native_query_id,
                )
            )
        except (NativeEngineBridgeError, ValueError) as exc:
            raise ResearchMaterialLimitation("P14_NATIVE_ATTESTATION_FAILED", str(exc)) from exc
        manifest = attestation.manifest
        if manifest.native_conversation_id != native_conversation_id or manifest.native_query_id != native_query_id:
            raise ResearchMaterialLimitation("P14_NATIVE_OCCURRENCE_MISMATCH", "attestation occurrence mismatch")
        if manifest.material_query_count != 1:
            raise ResearchMaterialLimitation("P14_NATIVE_MATERIAL_QUERY_CARDINALITY", "expected one material query")
        self._engine_pin(manifest)
        if (
            manifest.authenticated_metabase_subject != binding.metabase_user_id
            or manifest.permission_provenance.current_metabase_user_id != binding.metabase_user_id
        ):
            raise ResearchMaterialLimitation("P14_NATIVE_SUBJECT_MISMATCH", "attested subject mismatch")

        semantic_refs, resources, mapping_refs = self._resources.resolve(
            principal=principal, session=session, obligation_id=obligation_id, manifest=manifest
        )
        brief = session.accepted_brief
        assert brief is not None
        question = next(item for item in brief.questions if item.goal_id == obligation_id)
        accepted_context_hash = _hash({
            "authority_id": session.authority_id,
            "brief_id": brief.brief_id,
            "obligation_id": obligation_id,
            "question": question.model_dump(mode="json"),
        })
        material_scope_hash = _hash({
            "semantic_refs": semantic_refs,
            "resources": [x.model_dump(mode="json") for x in resources],
        })
        artifact = AuthorizedExecutionArtifact(
            authority_id=session.authority_id,
            projection_hash=accepted_context_hash,
            resolved_intent_hash=material_scope_hash,
            semantic_context_version=session.context_version,
            semantic_refs=semantic_refs,
            resource_bindings=resources,
            steps=(ExecutionArtifactStep(
                role="primary",
                artifact_fingerprint=manifest.exact_pmbql_fingerprint,
                artifact_representation=attestation.exact_serialized_pmbql,
            ),),
            query_count=1,
            engine_identity={
                "substrate": "metabase-native",
                "repository": manifest.runtime_identity.repository,
                "revision_sha": manifest.runtime_identity.revision_sha,
                "upstream_base_sha": manifest.runtime_identity.upstream_base_sha,
                "runtime_tag": manifest.runtime_identity.runtime_tag,
                "runtime_image_digest": self._expected.runtime_image_digest,
                "build_identity": manifest.runtime_identity.build_identity,
                "runtime_image_identity": manifest.runtime_identity.image_identity,
                "runtime_instance_id": manifest.runtime_identity.runtime_instance_id,
            },
            provenance_refs=(
                manifest.attestation_id,
                f"metabase-user:{binding.metabase_user_id}",
                *mapping_refs,
            ),
        )
        source_refs = artifact.resource_entity_ids
        permission_payload = {
            "profile": binding.security_profile,
            "policy_version": binding.policy_version,
            "metabase_user_id": binding.metabase_user_id,
            "database_id": manifest.database_id,
            "checked_source_table_ids": sorted(manifest.permission_provenance.checked_source_table_ids),
            "permission_check": manifest.permission_provenance.permission_check,
        }
        facts = VerifiedExecutionSecurityFacts(
            tenant_binding=session.tenant_binding,
            principal_subject=session.principal_subject,
            roles=tuple(sorted(principal.roles)),
            attribute_policy_digest=_hash(permission_payload),
            policy_version=binding.policy_version,
            rls_versions=(),
            cls_versions=(),
            database_route=f"metabase:database:{manifest.database_id}",
            database_destination=f"metabase:database:{manifest.database_id}",
            impersonation_role=None,
            semantic_context_version=session.context_version,
            source_object_refs=source_refs,
            security_parameter_digest=_hash({
                **permission_payload, "material_resources": sorted(source_refs)
            }),
            metabase_subject_ref=f"metabase-user:{binding.metabase_user_id}",
            attestation_refs=(manifest.attestation_id, "native-permission:PASSED"),
            evidence_refs=(
                f"native-subject-binding:{binding.id}",
                f"metabase-user:{binding.metabase_user_id}",
                f"metabase:database:{manifest.database_id}",
            ),
        )
        try:
            access = ExecutionAccessSnapshotIssuer.issue_research_material(
                current_principal=principal,
                tenant_binding=session.tenant_binding,
                principal_subject=session.principal_subject,
                accepted_roles=tuple(sorted(principal.roles)),
                semantic_context_version=session.context_version,
                verified_security_facts=facts,
                expected_source_object_refs=source_refs,
            )
        except SecurityIdentityError as exc:
            raise ResearchMaterialLimitation(exc.code, exc.detail) from exc

        try:
            observed = bridge.execute_native_query(
                conversation_id=native_conversation_id,
                native_query_id=native_query_id,
                expected_pmbql_fingerprint=manifest.exact_pmbql_fingerprint,
                expected_attestation_id=manifest.attestation_id,
            )
        except NativeEngineBridgeError as exc:
            raise ResearchMaterialLimitation("P14_NATIVE_EXACT_EXECUTION_FAILED", str(exc)) from exc
        if observed.native_conversation_id != native_conversation_id or observed.native_query_id != native_query_id:
            raise ResearchMaterialLimitation("P14_NATIVE_EXECUTION_OCCURRENCE_MISMATCH", "executed occurrence mismatch")
        if observed.attestation_id != manifest.attestation_id:
            raise ResearchMaterialLimitation("P14_NATIVE_EXECUTION_ATTESTATION_MISMATCH", "attestation changed")
        if observed.executed_pmbql_fingerprint != manifest.exact_pmbql_fingerprint:
            raise ResearchMaterialLimitation("P14_NATIVE_EXECUTION_FINGERPRINT_MISMATCH", "native occurrence mutated")

        result = ExecutionResultSnapshot(payload=observed.payload, row_count=self._row_count(observed.payload))
        runtime = manifest.runtime_identity
        runtime_identity = RuntimeIdentity(
            substrate="metabase-native",
            runtime_version=runtime.runtime_tag,
            image_digest=str(self._expected.runtime_image_digest),
            database_id=f"metabase:{manifest.database_id}",
            repository=runtime.repository,
            revision_sha=runtime.revision_sha,
            upstream_base_sha=runtime.upstream_base_sha,
            runtime_tag=runtime.runtime_tag,
            build_identity=runtime.build_identity,
            image_identity=runtime.image_identity,
            runtime_instance_id=runtime.runtime_instance_id,
        )
        event = ExecutionEventIdentity(
            execution_id=f"native:{manifest.native_conversation_id}:{manifest.native_query_id}:{manifest.attestation_id}",
            executed_at=datetime.now(timezone.utc),
        )
        receipt = DimaQueryReceiptSealer.seal_research_execution(
            authority_id=session.authority_id,
            obligation_ids=(obligation_id,),
            tenant_binding=session.tenant_binding,
            principal_subject=session.principal_subject,
            roles=tuple(sorted(principal.roles)),
            semantic_refs=semantic_refs,
            accepted_context_hash=accepted_context_hash,
            material_scope_hash=material_scope_hash,
            semantic_context_version=session.context_version,
            execution_artifact=artifact,
            access_snapshot=access,
            runtime=runtime_identity,
            result=result,
            event=event,
        )
        evidence = EvidenceArtifact(
            artifact_id="evi_" + hashlib.sha256(receipt.receipt_id.encode()).hexdigest()[:24],
            authority_id=receipt.authority_id,
            obligation_ids=(obligation_id,),
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="p14_native_research_material",
            state=EvidenceState.VERIFIED,
            payload={
                "native_conversation_id": str(native_conversation_id),
                "native_query_id": native_query_id,
                "attestation_id": manifest.attestation_id,
                "result_hash": result.result_hash,
                "row_count": result.row_count,
                "result": observed.payload,
            },
        )
        return ResearchMaterialOutcome(
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            attestation_id=manifest.attestation_id,
            receipt=receipt,
            evidence=evidence,
        )
