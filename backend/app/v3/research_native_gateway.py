"""DMP-DEC-0048 native-direct P14 Research gateway.

Metabot + Metabase own analytical truth and execution. This module owns only
Dima-principal/native-subject correlation, native session/runtime identity,
exact-occurrence readiness/observation/execution ordering, result provenance,
the single DimaQueryReceipt family, Evidence, and Research correlation.

No analytical planner, MBQL parser, semantic guesser, re-execution dependency,
P10 access-snapshot synthesis, or resource-planning authority lives here.
P14 observes and attests the persisted Metabot occurrence before any analytical
side effect, then executes that exact occurrence through the certified engine
primitive and admits only covered results as governed Evidence.
"""
from __future__ import annotations

import hashlib
import uuid
from contextlib import contextmanager
from calendar import monthrange
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Callable

from sqlmodel import Session, select

from app.v3.analytical_boundary import (
    AnalyticalBoundaryError,
    AnalyticalEngineIdentityV1,
    AnalyticalFilterV1,
    AnalyticalObservedTemporalScopeV1,
    AnalyticalRankingV1,
    project_analytical_intent_v1,
    project_execution_manifest_v1,
    verify_analytical_fulfillment_v1,
)
from app.v3.analytical_request_contract import AnalyticalRequestContract
from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    RuntimeIdentity,
)
from app.v3.research import ResearchSession
from app.v3.research_analytical_scope import (
    NativeMaterialBinding,
    analytical_scope_contract,
)
from app.v3.research_product import (
    ResearchMaterialLimitation,
    ResearchMaterialObservationUnavailable,
    ResearchMaterialOutcome,
)
from app.v3.research_material_repair import (
    is_repairable_material_validation_code,
)
from app.v3.research_result_dependency import (
    ResultDependencyProjectionError,
    ResultSelectionResolution,
    resolve_selection_binding_v1,
)
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_engine import (
    NativeEngineBridge,
    NativeEngineBridgeError,
    NativeEngineEndpointError,
    NativeEngineTransportError,
)
from app.v3.substrate.metabase.native_models import (
    NativeEngineIdentity,
    NativeEngineRequest,
    NativeMaterialObservation,
)
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import NativeResourceBinding, NativeSubjectBinding


def _uuid(value: str, code: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ResearchMaterialLimitation(
            code,
            "native Research binding requires stable UUID Dima identity",
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
    """Identity correlation only; Metabase remains permission authority."""

    def __init__(
        self,
        *,
        base_url: str,
        expected_identity: NativeEngineIdentity,
        db_engine=None,
        request_observer: Callable[[str, str], None] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._expected = expected_identity
        self._engine = db_engine or control_plane_engine
        self._request_observer = request_observer
        if not self._base_url:
            raise ValueError("native Metabase base_url is required")

    @property
    def db_engine(self):
        """Control-plane store used for identity/resource correlation only."""
        return self._engine

    def binding_for(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
    ) -> NativeSubjectBinding:
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
                .where(NativeSubjectBinding.enabled == True)  # noqa: E712
            ).all()
        if len(rows) != 1:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_SUBJECT_BINDING_MISSING",
                "exactly one enabled Dima-to-Metabase subject correlation is required",
            )
        return rows[0]

    def assert_engine_identity(self, observed: dict[str, Any]) -> None:
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
        if not observed.get("runtime_instance_id"):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_ENGINE_IDENTITY_MISSING",
                "native runtime instance identity is missing",
            )

    @contextmanager
    def open(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        native_session_token: str | None,
    ):
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
            request_observer=self._request_observer,
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
            self.assert_engine_identity(bridge.engine_identity())
            yield bridge
        finally:
            bridge.close()


class NativeResearchMaterialExecutor:
    """Directly execute captured query A without reinterpreting analytical semantics."""

    def __init__(
        self,
        *,
        subject_provider: NativeSubjectSessionProvider,
        store: ResearchSessionStore,
        expected_identity: NativeEngineIdentity,
    ) -> None:
        self._subjects = subject_provider
        self._store = store
        self._expected = expected_identity

    @staticmethod
    def _assert_scope_fingerprint(
        *,
        session: ResearchSession,
        contract: AnalyticalRequestContract,
    ) -> str:
        brief = session.accepted_brief
        if brief is None:
            raise ResearchMaterialLimitation(
                "R1_ACCEPTED_BRIEF_REQUIRED",
                "scope fingerprint requires immutable accepted ResearchBrief",
            )
        expected = brief.scope_fingerprint
        observed = contract.scope_fingerprint
        if observed is None:
            raise ResearchMaterialLimitation(
                "R1_MATERIAL_SCOPE_FINGERPRINT_REQUIRED",
                expected,
                last_valid_boundary="dima.scope.resolve",
                first_invalid_boundary="dima.material.compile",
                expected_fingerprint=expected,
                observed_fingerprint=None,
            )
        if observed != expected:
            raise ResearchMaterialLimitation(
                "R1_MATERIAL_SCOPE_FINGERPRINT_MISMATCH",
                f"expected={expected} observed={observed}",
                last_valid_boundary="dima.scope.resolve",
                first_invalid_boundary="dima.material.compile",
                expected_fingerprint=expected,
                observed_fingerprint=observed,
            )
        if (
            contract.scope_identity.version_id
            != brief.scope.scope_version.version_id
        ):
            raise ResearchMaterialLimitation(
                "R1_MATERIAL_SCOPE_VERSION_MISMATCH",
                (
                    f"expected={brief.scope.scope_version.version_id} "
                    f"observed={contract.scope_identity.version_id}"
                ),
                last_valid_boundary="dima.scope.resolve",
                first_invalid_boundary="dima.material.compile",
                expected_fingerprint=expected,
                observed_fingerprint=observed,
            )
        return expected

    @staticmethod
    def _contract_candidate_ids(contract) -> set[str]:
        candidate_ids = set(contract.metric_refs)
        candidate_ids.update(contract.dimension_refs)
        candidate_ids.update(item.source_candidate_id for item in contract.filters)
        if contract.period is not None:
            candidate_ids.add(contract.period.time_dimension)
        if contract.comparison is not None:
            candidate_ids.add(contract.comparison.reference_period.time_dimension)
            candidate_ids.add(contract.comparison.base_period.time_dimension)
        ranking = contract.ranking
        if getattr(ranking, "kind", None) == "native_metric":
            candidate_ids.add(ranking.measure)
        return candidate_ids

    def _material_bindings(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        contract=None,
        candidate_ids: tuple[str, ...] | None = None,
    ) -> dict[str, NativeMaterialBinding]:
        """Load exact governed native bindings from immutable accepted scope.

        candidate_ids is used for execution-local material dependencies whose
        binding is required before that dimension is projected into the child
        contract. Ordinary execution supplies contract and therefore keeps
        the exact same canonical binding policy. There is one binding law;
        only the caller material role differs.
        """
        brief = session.accepted_brief
        if brief is None:
            raise ResearchMaterialLimitation(
                "R1_ACCEPTED_BRIEF_REQUIRED",
                "material observation requires the immutable accepted ResearchBrief",
            )
        tenant_id = _tenant_uuid(principal, session)
        accepted_refs = {
            item.candidate_id: item for item in brief.scope.semantic_refs
        }
        if candidate_ids is not None:
            required = set(candidate_ids)
        else:
            if contract is None:
                raise ResearchMaterialLimitation(
                    "R1_MATERIAL_CONTRACT_REQUIRED",
                    "native binding resolution requires a material contract or explicit candidate ids",
                )
            required = self._contract_candidate_ids(contract)
        if not required.issubset(accepted_refs):
            raise ResearchMaterialLimitation(
                "R1_SEMANTIC_REF_OUTSIDE_ACCEPTED_SCOPE",
                "material binding references a candidate outside accepted Research scope",
            )
        output: dict[str, NativeMaterialBinding] = {}
        with Session(self._subjects.db_engine) as db:
            for candidate_id in sorted(required):
                ref = accepted_refs[candidate_id]
                rows = db.exec(
                    select(NativeResourceBinding)
                    .where(NativeResourceBinding.tenant_id == tenant_id)
                    .where(
                        NativeResourceBinding.semantic_context_version
                        == session.context_version
                    )
                    .where(NativeResourceBinding.candidate_id == candidate_id)
                    .where(
                        NativeResourceBinding.candidate_kind
                        == ref.target_kind.value
                    )
                    .where(NativeResourceBinding.enabled == True)  # noqa: E712
                ).all()
                if len(rows) != 1:
                    raise ResearchMaterialLimitation(
                        "R1_NATIVE_RESOURCE_BINDING_MISSING",
                        f"exactly one governed native binding is required for {candidate_id}",
                    )
                binding = rows[0]
                if (
                    not str(binding.semantic_id or "").strip()
                    or not str(binding.resource_entity_id or "").strip()
                    or not str(binding.resource_version or "").strip()
                ):
                    raise ResearchMaterialLimitation(
                        "R1_NATIVE_RESOURCE_BINDING_STALE",
                        f"durable native resource identity is incomplete for {candidate_id}",
                    )
                fingerprint = str(binding.resource_fingerprint or "")
                if len(fingerprint) != 64 or any(
                    value not in "0123456789abcdef" for value in fingerprint
                ):
                    raise ResearchMaterialLimitation(
                        "R1_NATIVE_RESOURCE_FINGERPRINT_INVALID",
                        candidate_id,
                    )
                output[candidate_id] = NativeMaterialBinding(
                    candidate_id=candidate_id,
                    candidate_kind=ref.target_kind.value,
                    database_id=int(binding.metabase_database_id),
                    table_id=(
                        int(binding.metabase_table_id)
                        if binding.metabase_table_id is not None
                        else None
                    ),
                    field_id=(
                        int(binding.metabase_field_id)
                        if binding.metabase_field_id is not None
                        else None
                    ),
                    metric_id=(
                        int(binding.metabase_metric_id)
                        if binding.metabase_metric_id is not None
                        else None
                    ),
                    metric_entity_id=(
                        str(binding.metabase_entity_id)
                        if binding.metabase_entity_id is not None
                        else None
                    ),
                )
        return output

    def resolve_result_dependency(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        obligation_id: str,
        analytical_scope: AnalyticalRequestContract | None = None,
        source_execution_obligation_id: str | None = None,
    ) -> ResultSelectionResolution | None:
        """Project one VERIFIED parent ranking value into child execution material.

        This never replays parent native work and never mutates accepted user scope.
        The selected value comes only from the durable VERIFIED result bound to the
        declared result dependency.
        """

        contract = analytical_scope or analytical_scope_contract(
            session=session,
            obligation_id=obligation_id,
        )
        brief = session.accepted_brief
        if brief is None:
            raise ResearchMaterialLimitation(
                "R1_ACCEPTED_BRIEF_REQUIRED",
                "result dependency requires immutable accepted ResearchBrief",
            )
        matches = tuple(
            item for item in brief.questions if item.goal_id == obligation_id
        )
        if len(matches) != 1:
            raise ResearchMaterialLimitation(
                "R1_RESULT_DEPENDENCY_CHILD_REQUIRED",
                obligation_id,
            )
        question = matches[0]
        dependency = question.result_dependency
        if dependency is None:
            return None

        execution_source = (
            source_execution_obligation_id or dependency.source_goal_id
        )
        if execution_source == obligation_id:
            raise ResearchMaterialLimitation(
                "R1_RESULT_DEPENDENCY_EXECUTION_SELF_REFERENCE",
                execution_source,
                last_valid_boundary="dima.requirements.plan",
                first_invalid_boundary="dima.material.compile",
            )
        parent_link, parent_result = self._store.verified_material_result(
            session_id=session.session_id,
            obligation_id=execution_source,
        )
        semantic_ref = next(
            (
                item
                for item in brief.scope.semantic_refs
                if item.candidate_id == dependency.dimension_semantic_id
            ),
            None,
        )
        if semantic_ref is None:
            raise ResearchMaterialLimitation(
                "R1_RESULT_DEPENDENCY_DIMENSION_OUTSIDE_SCOPE",
                dependency.dimension_semantic_id,
                last_valid_boundary="dima.scope.resolve",
                first_invalid_boundary="dima.material.compile",
                scope_fingerprint=contract.scope_fingerprint,
                material_fingerprint=contract.material_fingerprint,
            )

        # A result-dependent dimension selects one VERIFIED parent entity
        # before it becomes child execution material. It need not be a child
        # output/breakout; accepted Research scope is its semantic authority.
        bindings = self._material_bindings(
            principal=principal,
            session=session,
            candidate_ids=(dependency.dimension_semantic_id,),
        )
        binding = bindings.get(dependency.dimension_semantic_id)
        if binding is None or binding.field_id is None:
            raise ResearchMaterialLimitation(
                "R1_RESULT_DEPENDENCY_NATIVE_FIELD_REQUIRED",
                dependency.dimension_semantic_id,
                last_valid_boundary="dima.evidence.admit",
                first_invalid_boundary="dima.material.compile",
                scope_fingerprint=contract.scope_fingerprint,
                material_fingerprint=contract.material_fingerprint,
            )

        parent_question = next(
            (
                item
                for item in brief.questions
                if item.goal_id == dependency.source_goal_id
            ),
            None,
        )
        parent_ranking = (
            parent_question.ranking
            if parent_question is not None
            else None
        )

        try:
            return resolve_selection_binding_v1(
                base_contract=contract,
                source_goal_id=dependency.source_goal_id,
                source_evidence_id=str(parent_link.evidence_id),
                source_receipt_id=str(parent_link.receipt_id),
                source_result_hash=str(parent_link.result_hash),
                parent_execution_id=str(
                    getattr(parent_link, "id", None)
                    or parent_link.receipt_id
                ),
                dimension_semantic_id=dependency.dimension_semantic_id,
                native_field_id=int(binding.field_id),
                parent_result=parent_result,
                selection=dependency.selection,
                ranking_basis=(
                    parent_ranking.basis
                    if parent_ranking is not None
                    else None
                ),
                ranking_direction=(
                    parent_ranking.direction
                    if parent_ranking is not None
                    else None
                ),
                top_k=(
                    parent_ranking.limit
                    if parent_ranking is not None
                    else None
                ),
                dimension_name=semantic_ref.canonical_name,
                source_execution_obligation_id=execution_source,
                expected_parent_result_hash=str(parent_link.result_hash),
            )
        except ResultDependencyProjectionError as exc:
            raise ResearchMaterialLimitation(
                exc.code,
                exc.detail,
                last_valid_boundary="dima.evidence.admit",
                first_invalid_boundary="dima.material.compile",
                scope_fingerprint=contract.scope_fingerprint,
                material_fingerprint=contract.material_fingerprint,
            ) from exc

    def enrich_native_request(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        obligation_id: str,
        request: NativeEngineRequest,
        analytical_scope: AnalyticalRequestContract | None = None,
    ) -> NativeEngineRequest:
        """Preload accepted governed native resources through Metabot context.

        This is native resource correlation, not analytical planning. Exact
        governed metric ids already required by the accepted
        AnalyticalRequestContract are projected to Metabot's supported
        user_is_viewing context. Certified Metabase does not accept "table" as a
        user_is_viewing item type, so table bindings remain durable verifier
        authority rather than transport payload. SQL, MBQL, filters, joins,
        grouping and query-repair strategy remain entirely native.
        """

        contract = analytical_scope or analytical_scope_contract(
            session=session,
            obligation_id=obligation_id,
        )
        self._assert_scope_fingerprint(
            session=session,
            contract=contract,
        )
        bindings = self._material_bindings(
            principal=principal,
            session=session,
            contract=contract,
        )
        context = dict(request.context)
        raw_viewing = context.get("user_is_viewing")
        if raw_viewing is None:
            viewing: list[dict[str, Any]] = []
        elif isinstance(raw_viewing, list):
            viewing = [dict(item) for item in raw_viewing if isinstance(item, dict)]
        else:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_VIEWING_CONTEXT_INVALID",
                "native viewing context must be a list",
            )

        seen = {
            (str(item.get("type") or ""), str(item.get("id") or ""))
            for item in viewing
        }

        for candidate_id in contract.metric_refs:
            binding = bindings[candidate_id]
            if binding.metric_id is None:
                continue
            identity = ("metric", str(binding.metric_id))
            if identity in seen:
                continue
            viewing.append({"type": "metric", "id": binding.metric_id})
            seen.add(identity)

        if viewing:
            context["user_is_viewing"] = viewing
        return request.model_copy(update={"context": context})


    @staticmethod
    def _engine_failure_detail(exc: NativeEngineEndpointError) -> str:
        code = f" {exc.error_code}" if exc.error_code else ""
        return f"HTTP {exc.status_code}{code}: {exc.detail}"

    @staticmethod
    def _raise_readiness_failure(
        exc: NativeEngineBridgeError,
        *,
        boundary: str,
    ) -> None:
        """Classify pre-execution engine failures without hiding typed status."""

        if isinstance(exc, NativeEngineTransportError):
            raise ResearchMaterialObservationUnavailable(
                "R1_NATIVE_OCCURRENCE_TEMPORARILY_UNAVAILABLE",
                str(exc),
                last_valid_boundary="dima.native.generate",
                first_invalid_boundary=boundary,
            ) from exc
        if isinstance(exc, NativeEngineEndpointError):
            detail = NativeResearchMaterialExecutor._engine_failure_detail(exc)
            if (
                exc.status_code == 404
                and exc.error_code == "NATIVE_QUERY_OCCURRENCE_NOT_FOUND"
            ):
                raise ResearchMaterialObservationUnavailable(
                    exc.error_code,
                    detail,
                    last_valid_boundary="dima.native.generate",
                    first_invalid_boundary=boundary,
                ) from exc
            raise ResearchMaterialLimitation(
                exc.error_code
                or f"P14_NATIVE_ENDPOINT_HTTP_{exc.status_code}",
                detail,
                last_valid_boundary="dima.native.generate",
                first_invalid_boundary=boundary,
            ) from exc
        raise ResearchMaterialLimitation(
            "P14_NATIVE_ENDPOINT_PROTOCOL_FAILED",
            str(exc),
            last_valid_boundary="dima.native.generate",
            first_invalid_boundary=boundary,
        ) from exc

    def _attest_occurrence(
        self,
        *,
        bridge: NativeEngineBridge,
        native_conversation_id: uuid.UUID,
        native_query_id: str,
        metabase_user_id: int,
    ) -> tuple[str, str, int]:
        try:
            envelope = bridge.attest_native_query(
                conversation_id=native_conversation_id,
                native_query_id=native_query_id,
            )
        except NativeEngineBridgeError as exc:
            self._raise_readiness_failure(
                exc,
                boundary="dima.native.attest",
            )
            raise AssertionError("unreachable")
        manifest = envelope.get("manifest")
        if not isinstance(manifest, dict):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_ATTESTATION_MANIFEST_REQUIRED",
                "native attestation response has no manifest object",
                last_valid_boundary="dima.native.generate",
                first_invalid_boundary="dima.native.attest",
            )
        if (
            str(manifest.get("native_conversation_id") or "")
            != str(native_conversation_id)
            or str(manifest.get("native_query_id") or "") != native_query_id
        ):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_ATTESTATION_OCCURRENCE_MISMATCH",
                "attestation belongs to another persisted native occurrence",
                last_valid_boundary="dima.native.generate",
                first_invalid_boundary="dima.native.attest",
            )
        if int(manifest.get("authenticated_metabase_subject") or 0) != int(
            metabase_user_id
        ):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_SUBJECT_MISMATCH",
                "attestation subject differs from the correlated Metabase principal",
                last_valid_boundary="dima.native.generate",
                first_invalid_boundary="dima.native.attest",
            )
        runtime = manifest.get("runtime_identity")
        if not isinstance(runtime, dict):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_ATTESTATION_RUNTIME_REQUIRED",
                "attestation has no runtime identity",
                last_valid_boundary="dima.native.generate",
                first_invalid_boundary="dima.native.attest",
            )
        self._subjects.assert_engine_identity(runtime)
        fingerprint = str(manifest.get("exact_pmbql_fingerprint") or "")
        attestation_id = str(manifest.get("attestation_id") or "")
        database_id = manifest.get("database_id")
        if (
            len(fingerprint) != 64
            or not attestation_id
            or not isinstance(database_id, int)
            or database_id <= 0
        ):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_ATTESTATION_IDENTITY_INCOMPLETE",
                "attestation lacks exact persisted fingerprint, attestation id, or database id",
                last_valid_boundary="dima.native.generate",
                first_invalid_boundary="dima.native.attest",
            )
        return fingerprint, attestation_id, database_id

    def _validate_execution_facts_provenance(
        self,
        *,
        observation: NativeMaterialObservation,
        native_conversation_id: uuid.UUID,
        native_query_id: str,
        metabase_user_id: int,
    ) -> NativeMaterialObservation:
        """Validate only occurrence/runtime provenance; never business meaning."""

        if (
            observation.conversation_id != native_conversation_id
            or observation.native_query_id != native_query_id
        ):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_EXECUTION_FACT_OCCURRENCE_MISMATCH",
                "execution facts belong to another native occurrence",
                last_valid_boundary="dima.native.execute",
                first_invalid_boundary="dima.native.observe",
            )
        if observation.authenticated_metabase_subject != int(metabase_user_id):
            raise ResearchMaterialLimitation(
                "P14_NATIVE_SUBJECT_MISMATCH",
                "execution facts belong to another native subject",
                last_valid_boundary="dima.native.execute",
                first_invalid_boundary="dima.native.observe",
            )
        self._subjects.assert_engine_identity(observation.runtime_identity)
        return observation

    def _observe_executed_occurrence(
        self,
        *,
        bridge: NativeEngineBridge,
        native_conversation_id: uuid.UUID,
        native_query_id: str,
        metabase_user_id: int,
    ) -> NativeMaterialObservation:
        """Read structural facts after exact execution; never execute analytics."""

        try:
            observation = bridge.observe_native_query_material(
                conversation_id=native_conversation_id,
                native_query_id=native_query_id,
            )
        except NativeEngineBridgeError as exc:
            if isinstance(exc, NativeEngineEndpointError):
                code = exc.error_code or f"P14_NATIVE_FACT_HTTP_{exc.status_code}"
                detail = self._engine_failure_detail(exc)
            else:
                code = "P14_NATIVE_EXECUTION_FACTS_UNAVAILABLE"
                detail = str(exc)
            raise ResearchMaterialObservationUnavailable(
                code,
                detail,
                last_valid_boundary="dima.native.execute",
                first_invalid_boundary="dima.native.observe",
            ) from exc
        return self._validate_execution_facts_provenance(
            observation=observation,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            metabase_user_id=metabase_user_id,
        )

    def _execution_fact_observation(
        self,
        *,
        bridge: NativeEngineBridge,
        execution_observation,
        native_conversation_id: uuid.UUID,
        native_query_id: str,
        metabase_user_id: int,
    ) -> NativeMaterialObservation:
        facts = execution_observation.execution_facts
        if isinstance(facts, dict):
            status = str(facts.get("status") or "")
            raw_observation = facts.get("observation")
            if status == "OBSERVED" and isinstance(raw_observation, dict):
                try:
                    observation = NativeMaterialObservation.model_validate(
                        raw_observation
                    )
                except ValueError as exc:
                    raise ResearchMaterialLimitation(
                        "P14_NATIVE_EXECUTION_FACTS_INVALID",
                        str(exc),
                        last_valid_boundary="dima.native.execute",
                        first_invalid_boundary="dima.native.observe",
                    ) from exc
                return self._validate_execution_facts_provenance(
                    observation=observation,
                    native_conversation_id=native_conversation_id,
                    native_query_id=native_query_id,
                    metabase_user_id=metabase_user_id,
                )
            if status == "UNAVAILABLE":
                code = str(
                    facts.get("error_code")
                    or "P14_NATIVE_EXECUTION_FACTS_UNAVAILABLE"
                )
                error_type = (
                    ResearchMaterialLimitation
                    if is_repairable_material_validation_code(code)
                    else ResearchMaterialObservationUnavailable
                )
                raise error_type(
                    code,
                    str(facts.get("detail") or "execution facts are unavailable"),
                    last_valid_boundary="dima.native.execute",
                    first_invalid_boundary="dima.native.observe",
                )
        # Backward-compatible seam for a pre-11.3 engine during provider-free
        # migration. It is still post-execution and read-only.
        return self._observe_executed_occurrence(
            bridge=bridge,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            metabase_user_id=metabase_user_id,
        )

    def _projection_bindings(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
    ) -> tuple[NativeResourceBinding, ...]:
        """Load accepted-scope native identities without selecting by intent."""

        brief = session.accepted_brief
        if brief is None:
            raise ResearchMaterialLimitation(
                "ANALYTICAL_V1_ACCEPTED_BRIEF_REQUIRED",
                "execution fact projection requires immutable accepted scope",
            )
        accepted_ids = {item.candidate_id for item in brief.scope.semantic_refs}
        tenant_id = _tenant_uuid(principal, session)
        with Session(self._subjects.db_engine) as db:
            rows = db.exec(
                select(NativeResourceBinding)
                .where(NativeResourceBinding.tenant_id == tenant_id)
                .where(
                    NativeResourceBinding.semantic_context_version
                    == session.context_version
                )
                .where(NativeResourceBinding.enabled == True)  # noqa: E712
            ).all()
        return tuple(row for row in rows if row.candidate_id in accepted_ids)

    @staticmethod
    def _one_projection_binding(
        matches: list[NativeResourceBinding],
        *,
        fact: str,
    ) -> NativeResourceBinding:
        if len(matches) != 1:
            raise ResearchMaterialLimitation(
                "ANALYTICAL_V1_EXECUTION_FACT_BINDING_AMBIGUOUS",
                f"{fact}: expected one governed native binding, observed {len(matches)}",
                last_valid_boundary="dima.native.observe",
                first_invalid_boundary="dima.execution_manifest.project",
            )
        return matches[0]

    @classmethod
    def _metric_projection_binding(
        cls,
        bindings: tuple[NativeResourceBinding, ...],
        *,
        metric_id: int | None,
        metric_entity_id: str | None,
    ) -> NativeResourceBinding:
        matches = [
            item
            for item in bindings
            if item.candidate_kind in {"metric", "kpi"}
            and (
                metric_id is None
                or item.metabase_metric_id == metric_id
            )
            and (
                not metric_entity_id
                or item.metabase_entity_id == metric_entity_id
            )
        ]
        return cls._one_projection_binding(matches, fact="native metric")

    @classmethod
    def _field_projection_binding(
        cls,
        bindings: tuple[NativeResourceBinding, ...],
        *,
        field_id: int,
        table_id: int | None,
        literal: object | None = None,
    ) -> NativeResourceBinding:
        matches = [
            item
            for item in bindings
            if item.metabase_field_id == field_id
            and (table_id is None or item.metabase_table_id == table_id)
        ]
        if literal is not None:
            literal_text = str(literal)
            entity_matches = [
                item
                for item in matches
                if item.candidate_kind == "entity_value"
                and (
                    item.canonical_name == literal_text
                    or item.candidate_id == literal_text
                )
            ]
            if len(entity_matches) == 1:
                return entity_matches[0]
        dimension_matches = [
            item for item in matches if item.candidate_kind == "dimension"
        ]
        if len(dimension_matches) == 1:
            return dimension_matches[0]
        return cls._one_projection_binding(matches, fact=f"native field:{field_id}")

    @staticmethod
    def _parse_temporal_value(value: object) -> datetime | None:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, date):
            parsed = datetime.combine(value, time.min)
        elif isinstance(value, str):
            raw = value.strip()
            try:
                if "T" not in raw:
                    parsed = datetime.combine(date.fromisoformat(raw), time.min)
                else:
                    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                return None
        else:
            return None
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _wire_temporal_value(value: object) -> str:
        parsed = NativeResearchMaterialExecutor._parse_temporal_value(value)
        if parsed is None:
            return str(value)
        return parsed.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _advance_temporal_bucket(value: datetime, grain: str) -> datetime | None:
        if grain == "minute":
            return value + timedelta(minutes=1)
        if grain == "hour":
            return value + timedelta(hours=1)
        if grain == "day":
            return value + timedelta(days=1)
        if grain == "week":
            return value + timedelta(weeks=1)
        months = {"month": 1, "quarter": 3, "year": 12}.get(grain)
        if months is None:
            return None
        ordinal = value.year * 12 + (value.month - 1) + months
        year, month0 = divmod(ordinal, 12)
        month = month0 + 1
        day = min(value.day, monthrange(year, month)[1])
        return value.replace(year=year, month=month, day=day)

    def _project_execution_manifest(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        contract: AnalyticalRequestContract,
        consumer_ids: tuple[str, ...],
        observation: NativeMaterialObservation,
        runtime: RuntimeIdentity,
        execution_link_id: uuid.UUID,
        query_fingerprint: str,
        result: ExecutionResultSnapshot,
    ):
        """Pure native-fact -> ExecutionManifest projection; no fulfillment verdict."""

        bindings = self._projection_bindings(
            principal=principal,
            session=session,
        )
        if any(
            item.metabase_database_id != observation.database_id
            for item in bindings
            if (
                item.metabase_metric_id is not None
                or item.metabase_field_id is not None
            )
        ):
            raise ResearchMaterialLimitation(
                "ANALYTICAL_V1_EXECUTION_DATABASE_MISMATCH",
                "observed native facts and accepted-scope bindings use different databases",
                last_valid_boundary="dima.native.observe",
                first_invalid_boundary="dima.execution_manifest.project",
            )

        metrics = tuple(
            dict.fromkeys(
                self._metric_projection_binding(
                    bindings,
                    metric_id=item.metabase_metric_id,
                    metric_entity_id=item.metabase_metric_entity_id,
                ).candidate_id
                for item in observation.native_metrics
            )
        )

        dimension_pairs: list[tuple[str, object]] = []
        for item in observation.dimensions:
            if item.role != "breakout":
                continue
            projected = self._field_projection_binding(
                bindings,
                field_id=item.field_id,
                table_id=item.table_id,
            )
            dimension_pairs.append((projected.candidate_id, item))
        dimensions = tuple(dict.fromkeys(item[0] for item in dimension_pairs))
        row_grain = dimensions

        filters: list[AnalyticalFilterV1] = []
        for item in observation.filters:
            if item.operator != "=" or len(item.values) != 1:
                raise ResearchMaterialLimitation(
                    "ANALYTICAL_V1_EXECUTION_FILTER_FACT_UNSUPPORTED",
                    "canonical filter projection requires one observed equality literal",
                    last_valid_boundary="dima.native.observe",
                    first_invalid_boundary="dima.execution_manifest.project",
                )
            projected = self._field_projection_binding(
                bindings,
                field_id=item.field_id,
                table_id=item.table_id,
                literal=item.values[0],
            )
            filters.append(
                AnalyticalFilterV1(
                    semantic_ref=f"native-field:{item.field_id}",
                    dimension_semantic_id=projected.candidate_id,
                    value=str(item.values[0]),
                )
            )

        temporal_scopes: list[AnalyticalObservedTemporalScopeV1] = []
        # A temporal scope constrains WHICH rows participated; it does not mean
        # the final result is observed at a temporal row grain. Keep scope facts
        # separate from the result-time-axis fact consumed by the sole verifier.
        temporal_observation_candidates: list[str] = []
        for item in observation.temporal_scopes:
            if item.lower_bound is None or item.upper_bound is None:
                continue
            projected = self._field_projection_binding(
                bindings,
                field_id=item.time_field_id,
                table_id=item.table_id,
            )
            temporal_scopes.append(
                AnalyticalObservedTemporalScopeV1(
                    time_dimension_semantic_id=projected.candidate_id,
                    start=self._wire_temporal_value(item.lower_bound),
                    end=self._wire_temporal_value(item.upper_bound),
                    source="native_filter",
                )
            )

        rankings: list[AnalyticalRankingV1] = []
        for item in observation.ranking:
            if item.target.kind != "metric":
                continue
            projected = self._metric_projection_binding(
                bindings,
                metric_id=item.target.metabase_metric_id,
                metric_entity_id=item.target.metabase_metric_entity_id,
            )
            rankings.append(
                AnalyticalRankingV1(
                    kind="native_metric",
                    metric=projected.candidate_id,
                    basis=item.basis,
                    direction=item.direction,
                    top_k=item.limit if item.limit and item.limit > 0 else None,
                )
            )
            if item.change_periods is not None:
                for source, scope in (
                    ("change_baseline", item.change_periods.baseline),
                    ("change_comparison", item.change_periods.comparison),
                ):
                    if scope.lower_bound is None or scope.upper_bound is None:
                        continue
                    time_binding = self._field_projection_binding(
                        bindings,
                        field_id=scope.time_field_id,
                        table_id=scope.table_id,
                    )
                    temporal_scopes.append(
                        AnalyticalObservedTemporalScopeV1(
                            time_dimension_semantic_id=time_binding.candidate_id,
                            start=self._wire_temporal_value(scope.lower_bound),
                            end=self._wire_temporal_value(scope.upper_bound),
                            source=source,
                        )
                    )

        data = result.payload.get("data")
        data = data if isinstance(data, dict) else {}
        columns = tuple(data.get("cols") or ())
        rows = tuple(data.get("rows") or ())
        for semantic_id, dimension in dimension_pairs:
            grain = getattr(dimension, "temporal_grain", None)
            if not grain:
                continue
            column_index = next(
                (
                    index
                    for index, column in enumerate(columns)
                    if isinstance(column, dict)
                    and column.get("id") == dimension.field_id
                    and (
                        dimension.table_id is None
                        or column.get("table_id") == dimension.table_id
                    )
                ),
                None,
            )
            if column_index is None:
                continue
            temporal_observation_candidates.append(semantic_id)
            seen_values: set[str] = set()
            for row in rows:
                if not isinstance(row, (list, tuple)) or column_index >= len(row):
                    continue
                start = self._parse_temporal_value(row[column_index])
                if start is None:
                    continue
                end = self._advance_temporal_bucket(start, grain)
                if end is None:
                    continue
                key = start.isoformat()
                if key in seen_values:
                    continue
                seen_values.add(key)
                temporal_scopes.append(
                    AnalyticalObservedTemporalScopeV1(
                        time_dimension_semantic_id=semantic_id,
                        start=self._wire_temporal_value(start),
                        end=self._wire_temporal_value(end),
                        source="result_bucket",
                    )
                )

        temporal_ids = tuple(dict.fromkeys(temporal_observation_candidates))
        temporal_observation_dimension = (
            temporal_ids[0] if len(temporal_ids) == 1 else None
        )
        currentness_token = (
            f"{session.lineage_id}:{contract.scope_identity.version_id}"
        )
        native_subject_ref = (
            f"metabase-user:{observation.authenticated_metabase_subject}"
        )
        security_fingerprint = hashlib.sha256(
            "|".join(
                (
                    session.tenant_binding,
                    session.principal_subject,
                    native_subject_ref,
                    ",".join(sorted(principal.roles)),
                )
            ).encode("utf-8")
        ).hexdigest()
        return project_execution_manifest_v1(
            execution_id=f"native-occurrence:{execution_link_id}",
            consumer_intent_ids=consumer_ids,
            metrics=metrics,
            dimensions=dimensions,
            filters=tuple(filters),
            observed_temporal_scopes=tuple(
                dict.fromkeys(temporal_scopes)
            ),
            temporal_observation_dimension=temporal_observation_dimension,
            rankings=tuple(rankings),
            row_grain=row_grain,
            semantic_context_version=contract.semantic_context_version,
            scope_lineage_id=contract.scope_identity.lineage_id,
            scope_version_id=contract.scope_identity.version_id,
            scope_fingerprint=contract.scope_fingerprint,
            tenant_id=session.tenant_binding,
            principal_id=session.principal_subject,
            currentness_token=currentness_token,
            security_fingerprint=security_fingerprint,
            query_fingerprint=query_fingerprint,
            result_hash=result.result_hash,
            engine_identity=AnalyticalEngineIdentityV1(
                repository=runtime.repository or self._expected.repository,
                revision_sha=runtime.revision_sha,
                runtime_tag=runtime.runtime_tag,
                image_digest=runtime.image_digest,
            ),
            data_columns=columns,
            data_rows=rows,
            metadata={
                "native_conversation_id": str(observation.conversation_id),
                "native_query_id": observation.native_query_id,
                "material_observation_schema": observation.schema_version,
                "observed_query_fingerprint": observation.query_fingerprint,
            },
        )


    @staticmethod
    def _row_count(payload: dict[str, Any]) -> int:
        value = payload.get("row_count")
        if isinstance(value, int):
            return max(0, value)
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            return len(data["rows"])
        return 0

    def _runtime_identity(
        self,
        *,
        raw: dict[str, Any],
        database_id: object,
    ) -> RuntimeIdentity:
        self._subjects.assert_engine_identity(raw)
        if database_id is None or str(database_id).strip() == "":
            raise ResearchMaterialLimitation(
                "P14_NATIVE_DATABASE_ID_MISSING",
                "native dataset result/query exposes no database identity",
            )
        if self._expected.runtime_image_digest is None:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_IMAGE_DIGEST_MISSING",
                "pinned native image digest is required for Research provenance",
            )
        return RuntimeIdentity(
            substrate="metabase-native",
            runtime_version=str(raw["runtime_tag"]),
            image_digest=self._expected.runtime_image_digest,
            database_id=f"metabase:{database_id}",
            repository=str(raw["repository"]),
            revision_sha=str(raw["revision_sha"]),
            upstream_base_sha=str(raw["upstream_base_sha"]),
            runtime_tag=str(raw["runtime_tag"]),
            build_identity=str(raw["build_identity"]),
            image_identity=str(raw["image_identity"]),
            runtime_instance_id=raw["runtime_instance_id"],
        )

    def execute(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        obligation_id: str,
        bridge: NativeEngineBridge,
        native_conversation_id: uuid.UUID,
        native_query_id: str,
        native_query: dict[str, Any],
        query_fingerprint: str,
        execution_link_id: uuid.UUID,
        analytical_scope: AnalyticalRequestContract | None = None,
        consumer_obligation_ids: tuple[str, ...] | None = None,
    ) -> ResearchMaterialOutcome:
        binding = self._subjects.binding_for(principal=principal, session=session)
        native_subject_ref = f"metabase-user:{binding.metabase_user_id}"
        link = self._store.execution_link(execution_link_id)
        if link.session_id != session.session_id or link.obligation_id != obligation_id:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_OBLIGATION_CORRELATION_MISMATCH",
                "execution link belongs to another Research session or obligation",
            )
        consumer_ids = tuple(
            dict.fromkeys(consumer_obligation_ids or (obligation_id,))
        )
        if obligation_id not in set(consumer_ids):
            raise ResearchMaterialLimitation(
                "ANALYTICAL_V1_SHARED_ANCHOR_REQUIRED",
                "shared analytical fulfillment must include the execution anchor",
            )

        if link.status == "EXECUTION_STARTED":
            raise ResearchMaterialLimitation(
                "P14_NATIVE_EXECUTION_OUTCOME_UNKNOWN",
                (
                    "native exact-occurrence execution was durably started but no "
                    "result was persisted; blind retry is forbidden"
                ),
            )
        if link.status not in {"CANDIDATE_CAPTURED", "EXECUTED"}:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_EXECUTION_STATE_INVALID",
                f"native occurrence cannot continue from {link.status}",
            )

        contract = analytical_scope or analytical_scope_contract(
            session=session,
            obligation_id=obligation_id,
        )
        self._assert_scope_fingerprint(
            session=session,
            contract=contract,
        )

        # Structural readiness is fail-closed before execution. Business
        # fulfillment is deliberately absent from this pre-execution boundary.
        (
            exact_pmbql_fingerprint,
            attestation_id,
            attested_database_id,
        ) = self._attest_occurrence(
            bridge=bridge,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            metabase_user_id=int(binding.metabase_user_id),
        )

        if link.status == "EXECUTED":
            (
                result_payload,
                runtime_payload,
                persisted_result_hash,
                persisted_subject_ref,
                executed_at,
            ) = self._store.captured_execution(link)
            if persisted_subject_ref != native_subject_ref:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_SUBJECT_MISMATCH",
                    "persisted native result belongs to another native subject",
                )
            result = ExecutionResultSnapshot(
                payload=result_payload,
                row_count=self._row_count(result_payload),
            )
            if result.result_hash != persisted_result_hash:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_RESULT_FINGERPRINT_MISMATCH",
                    "persisted native result hash no longer matches its payload",
                )
            runtime = RuntimeIdentity.model_validate(runtime_payload)
            material_observation = self._observe_executed_occurrence(
                bridge=bridge,
                native_conversation_id=native_conversation_id,
                native_query_id=native_query_id,
                metabase_user_id=int(binding.metabase_user_id),
            )
        else:
            self._store.mark_execution_started(
                execution_link_id,
                native_subject_ref=native_subject_ref,
            )
            try:
                observed = bridge.execute_native_query(
                    conversation_id=native_conversation_id,
                    native_query_id=native_query_id,
                    expected_pmbql_fingerprint=exact_pmbql_fingerprint,
                    expected_attestation_id=attestation_id,
                )
            except NativeEngineTransportError as exc:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_EXECUTION_OUTCOME_UNKNOWN",
                    str(exc),
                    last_valid_boundary="dima.native.attest",
                    first_invalid_boundary="dima.native.execute",
                ) from exc
            except NativeEngineEndpointError as exc:
                raise ResearchMaterialLimitation(
                    exc.error_code
                    or f"P14_NATIVE_EXECUTION_HTTP_{exc.status_code}",
                    self._engine_failure_detail(exc),
                    last_valid_boundary="dima.native.attest",
                    first_invalid_boundary="dima.native.execute",
                ) from exc
            except NativeEngineBridgeError as exc:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_EXECUTION_PROTOCOL_FAILED",
                    str(exc),
                    last_valid_boundary="dima.native.attest",
                    first_invalid_boundary="dima.native.execute",
                ) from exc

            if (
                observed.native_conversation_id != native_conversation_id
                or observed.native_query_id != native_query_id
            ):
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_EXECUTION_OCCURRENCE_MISMATCH",
                    "exact-occurrence execution returned another native occurrence",
                    last_valid_boundary="dima.native.attest",
                    first_invalid_boundary="dima.native.execute",
                )
            if observed.executed_pmbql_fingerprint != exact_pmbql_fingerprint:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_EXECUTION_FINGERPRINT_MISMATCH",
                    "executed pMBQL fingerprint differs from the authorized occurrence",
                    last_valid_boundary="dima.native.attest",
                    first_invalid_boundary="dima.native.execute",
                )
            if observed.attestation_id != attestation_id:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_EXECUTION_ATTESTATION_MISMATCH",
                    "execution attestation differs from the pre-execution attestation",
                    last_valid_boundary="dima.native.attest",
                    first_invalid_boundary="dima.native.execute",
                )

            result_payload = observed.payload
            result = ExecutionResultSnapshot(
                payload=result_payload,
                row_count=self._row_count(result_payload),
            )
            runtime = self._runtime_identity(
                raw=observed.runtime_identity,
                database_id=attested_database_id,
            )
            executed_at = datetime.now(timezone.utc)
            # Persist exact execution before any read-only fact extraction can
            # fail. Resume may re-observe facts but never replay native work.
            self._store.mark_executed(
                execution_link_id,
                native_subject_ref=native_subject_ref,
                runtime_identity=runtime.model_dump(mode="json"),
                result_payload=result_payload,
                result_hash=result.result_hash,
                executed_at=executed_at,
            )
            material_observation = self._execution_fact_observation(
                bridge=bridge,
                execution_observation=observed,
                native_conversation_id=native_conversation_id,
                native_query_id=native_query_id,
                metabase_user_id=int(binding.metabase_user_id),
            )

        # The ExecutionManifest is projected from observed native/result facts.
        # There is no material-scope or result-coverage business verdict here.
        execution_manifest = self._project_execution_manifest(
            principal=principal,
            session=session,
            contract=contract,
            consumer_ids=consumer_ids,
            observation=material_observation,
            runtime=runtime,
            execution_link_id=execution_link_id,
            query_fingerprint=query_fingerprint,
            result=result,
        )

        brief = session.accepted_brief
        if brief is None:
            raise ResearchMaterialLimitation(
                "ANALYTICAL_V1_ACCEPTED_BRIEF_REQUIRED",
                "final analytical admission requires the immutable accepted brief",
            )
        questions_by_id = {
            item.goal_id: item for item in brief.questions
        }
        if any(item not in questions_by_id for item in consumer_ids):
            raise ResearchMaterialLimitation(
                "ANALYTICAL_V1_INTENT_IDENTITY_MISMATCH",
                "shared fulfillment references an unknown accepted analytical goal",
            )
        currentness_token = (
            f"{session.lineage_id}:{contract.scope_identity.version_id}"
        )
        security_fingerprint = hashlib.sha256(
            "|".join(
                (
                    session.tenant_binding,
                    session.principal_subject,
                    native_subject_ref,
                    ",".join(sorted(principal.roles)),
                )
            ).encode("utf-8")
        ).hexdigest()
        try:
            consumer_intents = tuple(
                project_analytical_intent_v1(
                    question=questions_by_id[consumer_id],
                    scope=brief.scope,
                    contract=analytical_scope_contract(
                        session=session,
                        obligation_id=consumer_id,
                    ),
                    tenant_id=session.tenant_binding,
                    principal_id=session.principal_subject,
                    currentness_token=currentness_token,
                    security_fingerprint=security_fingerprint,
                )
                for consumer_id in consumer_ids
            )
            for consumer_intent in consumer_intents:
                verify_analytical_fulfillment_v1(
                    consumer_intent,
                    execution_manifest,
                )
        except AnalyticalBoundaryError as exc:
            raise ResearchMaterialLimitation(
                exc.code,
                exc.detail,
                last_valid_boundary="dima.execution_manifest.project",
                first_invalid_boundary="dima.evidence.admit",
                scope_fingerprint=contract.scope_fingerprint,
                material_fingerprint=contract.material_fingerprint,
            ) from exc

        provenance_base = f"research-execution-link:{execution_link_id}"
        event = ExecutionEventIdentity(
            execution_id=f"native-occurrence:{execution_link_id}",
            executed_at=executed_at,
        )
        receipt = DimaQueryReceiptSealer.seal_research_execution(
            authority_id=session.authority_id,
            research_session_id=session.session_id,
            obligation_ids=consumer_ids,
            tenant_binding=session.tenant_binding,
            principal_subject=session.principal_subject,
            roles=tuple(sorted(principal.roles)),
            native_subject_ref=native_subject_ref,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            native_query_provenance_ref=provenance_base + ":query",
            native_result_provenance_ref=provenance_base + ":result",
            query_fingerprint=query_fingerprint,
            semantic_context_version=session.context_version,
            scope_fingerprint=contract.scope_fingerprint,
            runtime=runtime,
            result=result,
            event=event,
        )
        evidence = EvidenceArtifact(
            artifact_id="evi_" + hashlib.sha256(
                receipt.receipt_id.encode("utf-8")
            ).hexdigest()[:24],
            authority_id=receipt.authority_id,
            obligation_ids=consumer_ids,
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="p14_native_research_material",
            state=EvidenceState.VERIFIED,
            payload={
                "scope_fingerprint": contract.scope_fingerprint,
                "native_conversation_id": str(native_conversation_id),
                "native_query_id": native_query_id,
                "query_fingerprint": query_fingerprint,
                "material_observation_schema": material_observation.schema_version,
                "attestation_id": attestation_id,
                "exact_pmbql_fingerprint": exact_pmbql_fingerprint,
                "observed_query_fingerprint": material_observation.query_fingerprint,
                "scope_identity": contract.scope_identity.model_dump(mode="json"),
                "material_native_metrics": [
                    item.model_dump(mode="json")
                    for item in material_observation.native_metrics
                ],
                "material_dimensions": [
                    item.model_dump(mode="json")
                    for item in material_observation.dimensions
                ],
                "material_filters": [
                    item.model_dump(mode="json")
                    for item in material_observation.filters
                ],
                "material_temporal_scopes": [
                    item.model_dump(mode="json")
                    for item in material_observation.temporal_scopes
                ],
                "material_ranking": [
                    item.model_dump(mode="json")
                    for item in material_observation.ranking
                ],
                "execution_manifest": execution_manifest.model_dump(mode="json"),
                "fulfilled_intent_ids": list(consumer_ids),
                "native_subject_ref": native_subject_ref,
                "result_hash": result.result_hash,
                "row_count": result.row_count,
                "result": result.payload,
            },
        )
        return ResearchMaterialOutcome(
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            attestation_id=attestation_id,
            receipt=receipt,
            evidence=evidence,
        )
