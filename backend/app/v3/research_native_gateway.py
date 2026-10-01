"""DMP-DEC-0048 native-direct P14 Research gateway.

Metabot + Metabase own analytical truth and execution. This module owns only
Dima-principal/native-subject correlation, native session/runtime identity,
direct execution of the exact captured Metabot query, result provenance,
the single DimaQueryReceipt family, Evidence, and Research correlation.

No analytical planner, MBQL parser, semantic guesser, re-execution dependency,
P10 access-snapshot synthesis, or resource-planning authority lives here.
The dima.7 material-observation seam reports stable material native semantics
after durable execution; Dima compares them to the accepted analytical contract
before a native result may become governed Evidence. P13 attestation is forensic only.
"""
from __future__ import annotations

import hashlib
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

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
    ResearchAnalyticalScopeError,
    analytical_scope_contract,
    assert_material_native_scope,
)
from app.v3.research_product import (
    ResearchMaterialLimitation,
    ResearchMaterialObservationUnavailable,
    ResearchMaterialOutcome,
)
from app.v3.research_material_coverage import (
    ResearchMaterialCoverageError,
    assert_material_result_coverage,
)
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_engine import (
    NativeDatasetExecutionError,
    NativeEngineBridge,
    NativeEngineBridgeError,
)
from app.v3.substrate.metabase.native_models import (
    NativeEngineIdentity,
    NativeEngineRequest,
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
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._expected = expected_identity
        self._engine = db_engine or control_plane_engine
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
        contract,
    ) -> dict[str, NativeMaterialBinding]:
        """Load exact stable native ids for accepted semantic candidates only."""
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
        required = self._contract_candidate_ids(contract)
        if not required.issubset(accepted_refs):
            raise ResearchMaterialLimitation(
                "R1_SEMANTIC_REF_OUTSIDE_ACCEPTED_SCOPE",
                "material contract references a candidate outside accepted Research scope",
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

    def enrich_native_request(
        self,
        *,
        principal: Principal,
        session: ResearchSession,
        obligation_id: str,
        request: NativeEngineRequest,
        analytical_scope: AnalyticalRequestContract | None = None,
    ) -> NativeEngineRequest:
        """Preload accepted governed metric resources through Metabot context.

        This is native resource correlation, not analytical planning. Only exact
        metric ids already required by the accepted AnalyticalRequestContract are
        projected to Metabot's supported user_is_viewing context. SQL, MBQL,
        filters, joins, grouping and query-repair strategy remain entirely native.
        """

        contract = analytical_scope or analytical_scope_contract(
            session=session,
            obligation_id=obligation_id,
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


    def _observe_scope(
        self,
        *,
        principal: Principal,
        bridge: NativeEngineBridge,
        session: ResearchSession,
        obligation_id: str,
        native_conversation_id: uuid.UUID,
        native_query_id: str,
        query_fingerprint: str,
        metabase_user_id: int,
        analytical_scope: AnalyticalRequestContract | None = None,
    ):
        contract = analytical_scope or analytical_scope_contract(
            session=session,
            obligation_id=obligation_id,
        )
        bindings = self._material_bindings(
            principal=principal,
            session=session,
            contract=contract,
        )
        try:
            observation = bridge.observe_native_query_material(
                conversation_id=native_conversation_id,
                native_query_id=native_query_id,
            )
        except NativeEngineBridgeError as exc:
            raise ResearchMaterialObservationUnavailable(
                "R1_NATIVE_MATERIAL_OBSERVATION_UNAVAILABLE",
                str(exc),
            ) from exc
        if (
            observation.conversation_id != native_conversation_id
            or observation.native_query_id != native_query_id
        ):
            raise ResearchMaterialLimitation(
                "R1_NATIVE_OCCURRENCE_SCOPE_MISMATCH",
                "material observation belongs to another native occurrence",
            )
        # The execution fingerprint and the material-observation fingerprint are
        # exact identities in different representation domains:
        #   - query_fingerprint: raw generated query A, proven unchanged at /api/dataset
        #   - observation.query_fingerprint: the same persisted occurrence after
        #     Metabase's own Lib restore/exact-serialization boundary.
        # Do not compare those byte hashes across domains. Occurrence identity remains
        # fail-closed through conversation_id + native_query_id, authenticated subject,
        # engine identity, and the engine's producer/state equality checks.
        try:
            request = assert_material_native_scope(
                session=session,
                obligation_id=obligation_id,
                contract=contract,
                observation=observation,
                bindings=bindings,
                expected_engine=self._expected,
                expected_metabase_subject=metabase_user_id,
            )
        except ResearchAnalyticalScopeError as exc:
            raise ResearchMaterialLimitation(exc.code, exc.detail) from exc
        return request, observation

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
    ) -> ResearchMaterialOutcome:
        binding = self._subjects.binding_for(principal=principal, session=session)
        native_subject_ref = f"metabase-user:{binding.metabase_user_id}"
        link = self._store.execution_link(execution_link_id)
        if link.session_id != session.session_id or link.obligation_id != obligation_id:
            raise ResearchMaterialLimitation(
                "P14_NATIVE_OBLIGATION_CORRELATION_MISMATCH",
                "execution link belongs to another Research session or obligation",
            )

        if link.status == "EXECUTION_STARTED":
            raise ResearchMaterialLimitation(
                "P14_NATIVE_EXECUTION_OUTCOME_UNKNOWN",
                (
                    "native execution was durably started but no result was persisted; "
                    "blind retry is forbidden"
                ),
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
        else:
            if link.status != "CANDIDATE_CAPTURED":
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_EXECUTION_STATE_INVALID",
                    f"native execution cannot start from {link.status}",
                )
            self._store.mark_execution_started(
                execution_link_id,
                native_subject_ref=native_subject_ref,
            )
            try:
                observed = bridge.execute_dataset(native_query)
            except NativeDatasetExecutionError as exc:
                raise ResearchMaterialLimitation(
                    f"P14_NATIVE_DATASET_HTTP_{exc.status_code}",
                    exc.detail,
                ) from exc
            except NativeEngineBridgeError as exc:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_DATASET_TRANSPORT_FAILED",
                    str(exc),
                ) from exc

            if observed.query_fingerprint != query_fingerprint:
                raise ResearchMaterialLimitation(
                    "P14_NATIVE_QUERY_FINGERPRINT_MISMATCH",
                    "dataset execution did not receive the exact captured query payload",
                )
            result_payload = observed.payload
            result = ExecutionResultSnapshot(
                payload=result_payload,
                row_count=self._row_count(result_payload),
            )
            raw_runtime = bridge.engine_identity()
            database_id = result_payload.get("database_id")
            if database_id is None:
                database_id = native_query.get("database")
            runtime = self._runtime_identity(
                raw=raw_runtime,
                database_id=database_id,
            )
            executed_at = datetime.now(timezone.utc)
            self._store.mark_executed(
                execution_link_id,
                native_subject_ref=native_subject_ref,
                runtime_identity=runtime.model_dump(mode="json"),
                result_payload=result_payload,
                result_hash=result.result_hash,
                executed_at=executed_at,
            )

        contract = analytical_scope or analytical_scope_contract(
            session=session,
            obligation_id=obligation_id,
        )
        scope_observation, material_observation = self._observe_scope(
            principal=principal,
            bridge=bridge,
            session=session,
            obligation_id=obligation_id,
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            query_fingerprint=query_fingerprint,
            metabase_user_id=int(binding.metabase_user_id),
            analytical_scope=contract,
        )
        coverage_bindings = self._material_bindings(
            principal=principal,
            session=session,
            contract=contract,
        )
        try:
            result_coverage = assert_material_result_coverage(
                contract=contract,
                result_payload=result_payload,
                bindings=coverage_bindings,
            )
        except ResearchMaterialCoverageError as exc:
            raise ResearchMaterialLimitation(exc.code, exc.detail) from exc

        provenance_base = f"research-execution-link:{execution_link_id}"
        event = ExecutionEventIdentity(
            execution_id=f"native-dataset:{execution_link_id}",
            executed_at=executed_at,
        )
        receipt = DimaQueryReceiptSealer.seal_research_execution(
            authority_id=session.authority_id,
            research_session_id=session.session_id,
            obligation_ids=(obligation_id,),
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
            runtime=runtime,
            result=result,
            event=event,
        )
        evidence = EvidenceArtifact(
            artifact_id="evi_" + hashlib.sha256(
                receipt.receipt_id.encode("utf-8")
            ).hexdigest()[:24],
            authority_id=receipt.authority_id,
            obligation_ids=(obligation_id,),
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="p14_native_research_material",
            state=EvidenceState.VERIFIED,
            payload={
                "native_conversation_id": str(native_conversation_id),
                "native_query_id": native_query_id,
                "query_fingerprint": query_fingerprint,
                "material_observation_schema": material_observation.schema_version,
                "observed_query_fingerprint": material_observation.query_fingerprint,
                "scope_identity": scope_observation.scope_identity.model_dump(
                    mode="json"
                ),
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
                "material_result_coverage": result_coverage.model_dump(
                    mode="json"
                ),
                "native_subject_ref": native_subject_ref,
                "result_hash": result.result_hash,
                "row_count": result.row_count,
                "result": result.payload,
            },
        )
        return ResearchMaterialOutcome(
            native_conversation_id=native_conversation_id,
            native_query_id=native_query_id,
            attestation_id=None,
            receipt=receipt,
            evidence=evidence,
        )
