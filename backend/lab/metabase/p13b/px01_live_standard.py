#!/usr/bin/env python3
"""P13B-3 single-instance pinned-live Standard proof for frozen PX-01."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx

from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedPeriod,
    ResolvedSemanticRef,
    StandardProjection,
    projection_hash,
)
from app.v3.authority import AcceptedStandardAuthority, StandardWorkMode
from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.execution_identity import (
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    RuntimeIdentity,
)
from app.v3.native_execution import NativeCandidateOutcome
from app.v3.resource_provisioning import ManagedResourceBinding, ResourceKind
from app.v3.native_standard.contracts import (
    NativeAttestationEnvelope,
    NativeAttestedRuntimeIdentity,
)
from app.v3.native_standard.trust import NativeStandardTrustOrchestrator
from app.v3.security_identity import VerifiedExecutionSecurityFacts
from app.v3.semantic_spec import (
    DimensionSpec,
    DimaSemanticSpec,
    ManagedResourcePolicy,
    MetricSpec,
    SourceLineage,
    TimeSpec,
)
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    TemporalSemanticBinding,
)
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity, NativeEngineRequest
from control_plane.authorize import Principal


QUESTION = "Haziran 2026'da kaç satış siparişi açıldı?"
CASE_ID = "PX-01"
WAREHOUSE_NAME = "Dima Analytics Lab"
TABLE = "satis_siparisleri"
TIME_FIELD = "acilis_tarihi"
TABLE_RESOURCE = "boyahane:satis_siparisleri"
TIME_RESOURCE = "boyahane:satis_siparisleri.acilis_tarihi"
CONTEXT_VERSION = "ctx-px01-v1"
TENANT = "tenant-boyahane"
PRINCIPAL = "user-px01"


def h(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def login(base_url: str, email: str, password: str) -> str:
    response = httpx.post(
        base_url.rstrip("/") + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = str((response.json() or {}).get("id") or "")
    if not token:
        raise RuntimeError("restricted Metabase session token missing")
    return token


def _items(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return [x for x in body if isinstance(x, dict)]
    if isinstance(body, dict):
        for key in ("data", "items"):
            if isinstance(body.get(key), list):
                return [x for x in body[key] if isinstance(x, dict)]
    return []


def discover_catalog(
    base_url: str, token: str, *, timeout_seconds: int = 240
) -> tuple[int, int, int, str, int]:
    with httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={"X-Metabase-Session": token},
        timeout=30,
    ) as client:
        current = client.get("/api/user/current")
        current.raise_for_status()
        subject_id = int(current.json()["id"])

        response = client.get("/api/database")
        response.raise_for_status()
        dbs = [x for x in _items(response.json()) if x.get("name") == WAREHOUSE_NAME]
        if len(dbs) != 1:
            raise RuntimeError(f"expected one analytics database, observed {len(dbs)}")
        database_id = int(dbs[0]["id"])

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = client.get(
                f"/api/database/{database_id}/metadata",
                params={"include_hidden": "true"},
            )
            if response.status_code == 200:
                body = response.json()
                tables = body.get("tables") if isinstance(body, dict) else None
                if isinstance(tables, list):
                    table_matches = [
                        x for x in tables
                        if isinstance(x, dict) and x.get("name") == TABLE
                    ]
                    if len(table_matches) == 1:
                        table = table_matches[0]
                        fields = table.get("fields") or []
                        field_matches = [
                            x for x in fields
                            if isinstance(x, dict) and x.get("name") == TIME_FIELD
                        ]
                        if len(field_matches) == 1:
                            return (
                                database_id,
                                int(table["id"]),
                                int(field_matches[0]["id"]),
                                str(table.get("schema") or "public"),
                                subject_id,
                            )
            time.sleep(2)
    raise RuntimeError("Metabase metadata sync did not expose PX-01 source/time field")


def binding_snapshot(
    database_id: int,
    table_id: int,
    field_id: int,
    schema_name: str,
) -> DimaExecutionBindingSnapshot:
    table = SourceLineage(
        source_id="source.satis_siparisleri",
        database_ref=WAREHOUSE_NAME,
        schema_name=schema_name,
        table_name=TABLE,
    )
    opened = SourceLineage(
        source_id="source.satis_siparisleri.acilis_tarihi",
        database_ref=WAREHOUSE_NAME,
        schema_name=schema_name,
        table_name=TABLE,
        column_name=TIME_FIELD,
    )
    table_fp = h({"db": "boyahane", "schema": schema_name, "table": TABLE})
    time_fp = h(
        {"db": "boyahane", "schema": schema_name, "table": TABLE, "column": TIME_FIELD}
    )
    spec = DimaSemanticSpec(
        semantic_context_version=CONTEXT_VERSION,
        metrics=(
            MetricSpec(
                metric_id="metric.sales_order_count",
                name="Sales Order Count",
                aggregation="count",
                semantic_version="1",
                compatibility_hash=h(
                    {"metric": "metric.sales_order_count", "source": table.model_dump()}
                ),
                source_lineage=(table,),
            ),
        ),
        dimensions=(
            DimensionSpec(
                dimension_id="dimension.sales_order_opened_at",
                name="Sales Order Opened At",
                data_type="datetime",
                semantic_version="1",
                source_lineage=(opened,),
            ),
        ),
        time_specs=(
            TimeSpec(
                time_id="time.sales_order_opened_at",
                dimension_ref="dimension.sales_order_opened_at",
                grain="day",
            ),
        ),
        managed_resources=(
            ManagedResourcePolicy(
                semantic_ref="metric.sales_order_count",
                ownership="DIMA_MANAGED",
                reconciliation="OVERWRITE",
            ),
        ),
    )
    return DimaExecutionBindingSnapshot(
        semantic_context_version=CONTEXT_VERSION,
        semantic_spec=spec,
        candidate_bindings=(
            CandidateSemanticBinding(
                candidate_id="cand_sales_order_count",
                semantic_id="metric.sales_order_count",
                kind="metric",
            ),
        ),
        temporal_bindings=(
            TemporalSemanticBinding(
                compatibility_key="sales_orders.opened_at",
                dimension_id="dimension.sales_order_opened_at",
            ),
        ),
        current_catalog=CurrentCatalogSnapshot(
            catalog_version="boyahane-px01-live-" + table_fp[:16],
            objects=(
                CurrentCatalogObject(
                    source_id=table.source_id,
                    database_ref=WAREHOUSE_NAME,
                    schema_name=schema_name,
                    table_name=TABLE,
                    resource_entity_id=TABLE_RESOURCE,
                    resource_fingerprint=table_fp,
                    metabase_database_id=database_id,
                    metabase_table_id=table_id,
                ),
                CurrentCatalogObject(
                    source_id=opened.source_id,
                    database_ref=WAREHOUSE_NAME,
                    schema_name=schema_name,
                    table_name=TABLE,
                    column_name=TIME_FIELD,
                    resource_entity_id=TIME_RESOURCE,
                    resource_fingerprint=time_fp,
                    metabase_database_id=database_id,
                    metabase_table_id=table_id,
                    metabase_field_id=field_id,
                ),
            ),
        ),
    )


def authority_and_intent() -> tuple[AcceptedStandardAuthority, ResolvedAnalyticsIntent]:
    source_hash = hashlib.sha256(QUESTION.encode("utf-8")).hexdigest()
    projection = StandardProjection(
        obligation_ids=("obl-px01",),
        metric_handles=("handle.sales_order_count",),
        period_handle="handle.period.june_2026",
    )
    p_hash = projection_hash(projection)
    authority_id = "asa_" + h(
        {"case": CASE_ID, "source": source_hash, "projection": p_hash}
    )[:24]
    authority = AcceptedStandardAuthority(
        authority_id=authority_id,
        turn_id="p13b-px01-live",
        request_ref="p13b:px01",
        source_message_hash=source_hash,
        context_version=CONTEXT_VERSION,
        projection_hash=p_hash,
        semantic_handle_refs=(
            "handle.sales_order_count",
            "handle.period.june_2026",
        ),
        accepted_attempt_id="p13b-px01-live-attempt-1",
        model_role="native-metabot",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
        created_at_iso=datetime.now(timezone.utc).isoformat(),
    )
    intent = ResolvedAnalyticsIntent(
        authority_id=authority.authority_id,
        request_ref=authority.request_ref,
        source_message_hash=authority.source_message_hash,
        projection_hash=authority.projection_hash,
        semantic_context_version=authority.context_version,
        obligation_ids=projection.obligation_ids,
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="handle.sales_order_count",
                source_candidate_id="cand_sales_order_count",
                kind="metric",
                canonical_name="Sales Order Count",
                source_scopes=(TABLE,),
            ),
        ),
        period=ResolvedPeriod(
            kind="absolute",
            source_text="Haziran 2026",
            time_dimension="sales_orders.opened_at",
            start="2026-06-01",
            end="2026-07-01",
        ),
        principal=PrincipalContextRef(
            tenant_binding=TENANT,
            principal_subject=PRINCIPAL,
            roles=("analyst",),
        ),
    )
    return authority, intent


def metric_definition_intent() -> ResolvedAnalyticsIntent:
    """P9/P9B metric-definition projection from the same PX-01 canonical metric."""
    _, live_intent = authority_and_intent()
    projection = StandardProjection(
        obligation_ids=("obl-px01-metric-definition",),
        metric_handles=("handle.sales_order_count",),
    )
    return live_intent.model_copy(
        update={
            "authority_id": "p9b:metric.sales_order_count",
            "request_ref": "p9b:metric.sales_order_count",
            "source_message_hash": h(
                {
                    "canonical_metric": "metric.sales_order_count",
                    "semantic_context_version": CONTEXT_VERSION,
                }
            ),
            "projection_hash": projection_hash(projection),
            "obligation_ids": projection.obligation_ids,
            "period": None,
        }
    )


def query_id_from_stream(data_parts: tuple[Any, ...]) -> str:
    ids: set[str] = set()
    for part in data_parts:
        if not isinstance(part, dict) or part.get("type") != "generated_entity":
            continue
        value = part.get("value")
        query_ref = value.get("query") if isinstance(value, dict) else None
        query_id = query_ref.get("id") if isinstance(query_ref, dict) else None
        if query_id:
            ids.add(str(query_id))
    if len(ids) != 1:
        raise RuntimeError(f"expected one generated native query id, observed {sorted(ids)!r}")
    return next(iter(ids))


def scalar(payload: dict[str, Any]) -> tuple[Any, list[list[Any]]]:
    rows = (payload.get("data") or {}).get("rows")
    if not (
        isinstance(rows, list)
        and len(rows) == 1
        and isinstance(rows[0], list)
        and len(rows[0]) == 1
    ):
        raise RuntimeError(f"PX-01 result is not scalar: {rows!r}")
    return rows[0][0], rows


def managed_metric_binding(
    path: Path,
    *,
    engine_sha: str,
    platform_sha: str,
) -> ManagedResourceBinding:
    body = json.loads(path.read_text(encoding="utf-8"))
    if body.get("status") != "GREEN":
        raise RuntimeError("semantic availability proof is not GREEN")
    if body.get("engine_sha") != engine_sha:
        raise RuntimeError("semantic availability engine SHA differs from live engine")
    if body.get("platform_sha") != platform_sha:
        raise RuntimeError("semantic availability Platform SHA differs from live occurrence")
    binding = ManagedResourceBinding.model_validate(body.get("binding"))
    if (
        binding.tenant_binding != TENANT
        or binding.canonical_id != "metric.sales_order_count"
        or binding.resource_kind != ResourceKind.METRIC
        or binding.semantic_context_version != CONTEXT_VERSION
        or binding.applied_version != "1"
        or binding.ownership != "DIMA_MANAGED"
        or binding.metabase_local_id is None
        or binding.metabase_entity_id is None
    ):
        raise RuntimeError("semantic availability binding is not the frozen PX-01 metric")
    native_resource = body.get("native_metric_resource")
    if not isinstance(native_resource, dict):
        raise RuntimeError("semantic availability proof lacks native metric resource")
    if (
        int(native_resource.get("metabase_local_id") or -1) != binding.metabase_local_id
        or str(native_resource.get("portable_entity_id") or "")
        != binding.metabase_entity_id
        or str(native_resource.get("semantic_context_version") or "")
        != binding.semantic_context_version
    ):
        raise RuntimeError("native metric resource identity differs from P9 binding")
    return binding


def oracle(path: Path) -> Any:
    body = json.loads(path.read_text(encoding="utf-8"))
    matches = [
        x for x in body.get("results") or []
        if isinstance(x, dict) and x.get("id") == CASE_ID
    ]
    if len(matches) != 1:
        raise RuntimeError("PX-01 oracle missing")
    return matches[0]["rows"][0][0]


def assert_identity(
    identity: NativeAttestedRuntimeIdentity,
    *,
    engine_sha: str,
    upstream_sha: str,
    runtime_tag: str,
    build_identity: str,
    image_identity: str,
) -> None:
    expected = {
        "repository": "UpcyTech/dima-metabase-engine",
        "revision_sha": engine_sha,
        "upstream_base_sha": upstream_sha,
        "runtime_tag": runtime_tag,
        "build_identity": build_identity,
        "image_identity": image_identity,
    }
    actual = identity.model_dump(mode="json")
    for key, value in expected.items():
        if actual[key] != value:
            raise RuntimeError(
                f"runtime identity mismatch {key}: expected={value!r} actual={actual[key]!r}"
            )



def _diagnostic_usage(observation: Any | None) -> dict[str, Any]:
    if observation is None:
        return {}
    finish_parts = getattr(observation, "finish_parts", ()) or ()
    finish = finish_parts[-1] if finish_parts else {}
    usage = finish.get("usage") if isinstance(finish, dict) else {}
    return usage if isinstance(usage, dict) else {}


def _diagnostic_error_code(exc: Exception) -> str:
    message = str(exc)
    marker = ": {"
    if marker in message:
        candidate = "{" + message.split(marker, 1)[1]
        try:
            body = json.loads(candidate)
            via = body.get("via") if isinstance(body, dict) else None
            if isinstance(via, list) and via and isinstance(via[0], dict):
                data = via[0].get("data")
                if isinstance(data, dict):
                    code = data.get("dima/error-code")
                    if code:
                        return str(code)
        except Exception:
            pass
    return type(exc).__name__


def _write_failure_receipt(
    output: Path,
    state: dict[str, Any],
    exc: Exception,
    started: float,
) -> None:
    receipt = dict(state)
    receipt.update(
        {
            "status": "RED",
            "error_type": type(exc).__name__,
            "error_code": _diagnostic_error_code(exc),
            "error_message": str(exc)[:2000],
            "elapsed_ms": max(0, int((time.monotonic() - started) * 1000)),
        }
    )
    if receipt.get("exact_serialized_pmbql") is None:
        receipt.pop("exact_serialized_pmbql", None)
    path = output.with_name("P13B_PX01_LIVE_FAILURE.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--oracle", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--runtime-image-digest", required=True)
    ap.add_argument("--build-identity", required=True)
    ap.add_argument("--image-identity", required=True)
    ap.add_argument("--model-identifier", required=True)
    ap.add_argument("--platform-sha", required=True)
    ap.add_argument("--live-attempt-id", required=True)
    ap.add_argument("--semantic-availability-report", type=Path, required=True)
    args = ap.parse_args()

    failure_started = time.monotonic()
    failure_state: dict[str, Any] = {
        "schema_version": "p13b_px01_live_failure_v1",
        "case_id": CASE_ID,
        "question": QUESTION,
        "platform_sha": args.platform_sha,
        "engine_sha": args.engine_sha,
        "runtime_tag": args.runtime_tag,
        "model_identifier": args.model_identifier,
        "live_attempt_id": args.live_attempt_id,
        "conversation_id": None,
        "native_query_id": None,
        "failure_owner": "bootstrap",
        "runtime_identity": None,
        "native_tool_call_count": 0,
        "native_agent_latency_ms": None,
        "provider_usage": {},
        "exact_serialized_pmbql": None,
        "managed_metric_binding": None,
    }

    try:
        token = login(args.base_url, args.email, args.password)
        failure_state["failure_owner"] = "catalog-bootstrap"
        database_id, table_id, field_id, schema_name, mb_user_id = discover_catalog(
            args.base_url, token
        )
        snapshot = binding_snapshot(database_id, table_id, field_id, schema_name)
        metric_binding = managed_metric_binding(
            args.semantic_availability_report,
            engine_sha=args.engine_sha,
            platform_sha=args.platform_sha,
        )
        failure_state["managed_metric_binding"] = metric_binding.model_dump(mode="json")
        authority, intent = authority_and_intent()
        principal = Principal(
            user_id=PRINCIPAL,
            tenant_id=TENANT,
            tenant_slug=TENANT,
            roles=["analyst"],
        )
        expected_bootstrap = NativeEngineIdentity(
            repository="UpcyTech/dima-metabase-engine",
            engine_sha=args.engine_sha,
            upstream_base_sha=args.upstream_sha,
            runtime_tag=args.runtime_tag,
        )
        conversation_id = uuid4()
        failure_state["conversation_id"] = str(conversation_id)
        request_id = "p13b-px01-" + conversation_id.hex[:12]
        started = time.monotonic()

        with NativeEngineBridge(
            base_url=args.base_url,
            session_token=token,
            expected_identity=expected_bootstrap,
            timeout_seconds=300,
        ) as client:
            failure_state["failure_owner"] = "engine-identity"
            identity = NativeAttestedRuntimeIdentity.model_validate(client.engine_identity())
            failure_state["runtime_identity"] = identity.model_dump(mode="json")
            assert_identity(
                identity,
                engine_sha=args.engine_sha,
                upstream_sha=args.upstream_sha,
                runtime_tag=args.runtime_tag,
                build_identity=args.build_identity,
                image_identity=args.image_identity,
            )
            failure_state["failure_owner"] = "native-metabot-invoke"
            observation = client.invoke(
                NativeEngineRequest(
                    message=QUESTION,
                    conversation_id=conversation_id,
                    dima_request_id=request_id,
                    dima_trace_id=request_id + "-trace",
                )
            )
            failure_state["native_tool_call_count"] = len(observation.tool_calls)
            failure_state["native_agent_latency_ms"] = observation.latency_ms
            failure_state["provider_usage"] = _diagnostic_usage(observation)
            failure_state["failure_owner"] = "native-query-id"
            native_query_id = query_id_from_stream(observation.data_parts)
            failure_state["native_query_id"] = native_query_id
            failure_state["failure_owner"] = "native-query-attestation"
            attestation = NativeAttestationEnvelope.model_validate(
                client.attest_native_query(
                    conversation_id=conversation_id,
                    native_query_id=native_query_id,
                )
            )
            failure_state["exact_serialized_pmbql"] = attestation.exact_serialized_pmbql
            if attestation.manifest.runtime_identity != identity:
                raise RuntimeError("attestation runtime identity differs from live identity")

            engine = NativeEngineIdentity(
                repository=identity.repository,
                engine_sha=identity.revision_sha,
                upstream_base_sha=identity.upstream_base_sha,
                runtime_tag=identity.runtime_tag,
                build_identity=identity.build_identity,
                runtime_image_identity=identity.image_identity,
                runtime_instance_id=identity.runtime_instance_id,
            )
            security = VerifiedExecutionSecurityFacts(
                tenant_binding=TENANT,
                principal_subject=PRINCIPAL,
                roles=("analyst",),
                attribute_policy_digest=h({"subject": mb_user_id, "policy": "px01-live"}),
                policy_version="p13b-px01-v1",
                rls_versions=(),
                cls_versions=(),
                database_route="analytics-primary",
                database_destination="boyahane",
                impersonation_role=None,
                semantic_context_version=CONTEXT_VERSION,
                source_object_refs=(TABLE_RESOURCE, TIME_RESOURCE),
                security_parameter_digest=h(
                    {
                        "metabase_subject": mb_user_id,
                        "database_id": database_id,
                        "table_id": table_id,
                        "field_id": field_id,
                    }
                ),
                metabase_subject_ref=f"metabase-user:{mb_user_id}",
                attestation_refs=(attestation.manifest.attestation_id,),
                evidence_refs=("evidence:metabase-restricted-session:px01",),
            )
            failure_state["failure_owner"] = "dima-trust-authorization"
            authz = NativeStandardTrustOrchestrator.authorize(
                intent=intent,
                snapshot=snapshot,
                attestation=attestation,
                expected_engine=engine,
                current_principal=principal,
                verified_security_facts=security,
                dima_request_id=request_id,
                dima_trace_id=request_id + "-trace",
                managed_resource_bindings=(metric_binding,),
            )
            if authz.authorization.outcome != NativeCandidateOutcome.ALLOW:
                raise RuntimeError(
                    f"PX-01 blocked: {authz.authorization.code}: {authz.authorization.detail}"
                )
            artifact = authz.authorization.authorized_artifact
            if artifact is None or authz.access_snapshot is None:
                raise RuntimeError("ALLOW missing artifact/access snapshot")
            execution_request = NativeStandardTrustOrchestrator.execution_request(
                result=authz, attestation=attestation
            )
            fingerprints = {
                "attested": attestation.manifest.exact_pmbql_fingerprint,
                "authorized": artifact.steps[0].artifact_fingerprint,
            }
            if len(set(fingerprints.values())) != 1:
                raise RuntimeError(f"pre-execution fingerprint mismatch: {fingerprints}")

            before = NativeAttestedRuntimeIdentity.model_validate(client.engine_identity())
            if before != identity:
                raise RuntimeError("runtime changed before /api/dima/engine/v1/native-query-execution")
            failure_state["failure_owner"] = "exact-occurrence-execution"
            execution = client.execute_native_query(
                conversation_id=execution_request.native_conversation_id,
                native_query_id=execution_request.native_query_id,
                expected_pmbql_fingerprint=execution_request.expected_pmbql_fingerprint,
                expected_attestation_id=execution_request.expected_attestation_id,
            )
            fingerprints["executed"] = execution.executed_pmbql_fingerprint
            if len(set(fingerprints.values())) != 1:
                raise RuntimeError(f"PX-01: executed fingerprint mismatch: {fingerprints}")
            execution_identity = NativeAttestedRuntimeIdentity.model_validate(
                execution.runtime_identity
            )
            if execution_identity != identity:
                raise RuntimeError("PX-01: runtime identity changed in exact-occurrence execution")
            execution_attestation = NativeAttestationEnvelope.model_validate(execution.attestation)
            if execution_attestation != attestation:
                raise RuntimeError("PX-01: execution re-attestation differs from authorized occurrence")
            observed, rows = scalar(execution.payload)
            after = NativeAttestedRuntimeIdentity.model_validate(client.engine_identity())
            if after != identity:
                raise RuntimeError("runtime changed across /api/dima/engine/v1/native-query-execution")

        failure_state["failure_owner"] = "receipt-sealing"
        receipt = NativeStandardTrustOrchestrator.seal_receipt(
            intent=intent,
            result=authz,
            execution_request=execution_request,

            attestation=attestation,

            executed_pmbql_fingerprint=execution.executed_pmbql_fingerprint,

            executed_attestation_id=execution.attestation_id,
            runtime=RuntimeIdentity(
                substrate="metabase-native",
                runtime_version=identity.runtime_tag,
                image_digest=args.runtime_image_digest,
                database_id=f"metabase:{database_id}",
                repository=identity.repository,
                revision_sha=identity.revision_sha,
                upstream_base_sha=identity.upstream_base_sha,
                runtime_tag=identity.runtime_tag,
                build_identity=identity.build_identity,
                image_identity=identity.image_identity,
                runtime_instance_id=identity.runtime_instance_id,
            ),
            execution_result=ExecutionResultSnapshot(payload={"rows": rows}, row_count=1),
            execution_event=ExecutionEventIdentity(
                execution_id="exec-px01-" + conversation_id.hex[:16],
                executed_at=datetime.now(timezone.utc),
            ),
        )
        fingerprints["receipt"] = receipt.canonical_query_fingerprint
        if len(set(fingerprints.values())) != 1:
            raise RuntimeError(f"receipt fingerprint mismatch: {fingerprints}")

        engine_shas = {
            args.engine_sha,
            identity.revision_sha,
            attestation.manifest.runtime_identity.revision_sha,
            receipt.engine_revision_sha,
        }
        instances = {
            str(identity.runtime_instance_id),
            str(attestation.manifest.runtime_identity.runtime_instance_id),
            str(receipt.engine_runtime_instance_id),
        }
        if len(engine_shas) != 1 or len(instances) != 1:
            raise RuntimeError("runtime identity chain mismatch")

        failure_state["failure_owner"] = "independent-oracle"
        expected = oracle(args.oracle)
        if observed != expected:
            raise RuntimeError(f"receipted result {observed!r} != oracle {expected!r}")

        failure_state["failure_owner"] = "evidence-promotion"
        evidence = EvidenceArtifact(
            artifact_id="evi_" + h(
                {"receipt": receipt.receipt_id, "observed": observed, "oracle": expected}
            )[:24],
            authority_id=authority.authority_id,
            obligation_ids=intent.obligation_ids,
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="p13b_px01_standard_scalar",
            state=EvidenceState.VERIFIED,
            payload={"case_id": CASE_ID, "official_answer": observed, "oracle": expected},
        )
        if not evidence.verified:
            raise RuntimeError("Evidence is not VERIFIED")

        finish = observation.finish_parts[-1] if observation.finish_parts else {}
        usage = finish.get("usage") if isinstance(finish, dict) else {}
        usage = usage if isinstance(usage, dict) else {}
        report = {
            "schema_version": "p13b_px01_live_standard_v1",
            "status": "GREEN",
            "case_id": CASE_ID,
            "question": QUESTION,
            "official_answer": observed,
            "oracle": expected,
            "counts": {
                "authority": 1,
                "native_material_query": attestation.manifest.material_query_count,
                "attestation": 1,
                "authorized_artifact": 1,
                "execution_access_snapshot": 1,
                "db_execution": 1,
                "dima_query_receipt": 1,
                "verified_evidence": 1,
            },
            "fingerprint_chain": fingerprints,
            "runtime_identity": identity.model_dump(mode="json"),
            "managed_metric_binding": metric_binding.model_dump(mode="json"),
            "native_metric_references": [
                item.model_dump(mode="json")
                for item in attestation.manifest.native_metric_references
            ],
            "receipt": receipt.model_dump(mode="json"),
            "evidence": evidence.model_dump(mode="json"),
            "economics": {
                "provider_model_identifier": args.model_identifier,
                "agent_iterations": None,
                "agent_iterations_measurement": "NOT_EXPOSED_BY_NATIVE_STREAM",
                "provider_model_call_count": None,
                "provider_model_call_count_measurement": "NOT_EXPOSED_BY_NATIVE_STREAM",
                "native_tool_call_count": len(observation.tool_calls),
                "analytical_query_count": attestation.manifest.material_query_count,
                "native_agent_latency_ms": observation.latency_ms,
                "exact_occurrence_execution_latency_ms": execution.latency_ms,
                "end_to_end_ms": max(0, int((time.monotonic() - started) * 1000)),
                "prompt_tokens": usage.get("promptTokens"),
                "completion_tokens": usage.get("completionTokens"),
                "provider_cost": usage.get("cost"),
                "raw_usage": usage,
            },
            "silent_wrong": 0,
            "agent_api_analytical_fallback": 0,
            "wren_fallback": 0,
            "raw_sql_fallback": 0,
            "admin_analytical_fallback": 0,
        }
        if tuple(report["counts"].values()) != (1, 1, 1, 1, 1, 1, 1, 1):
            raise RuntimeError(f"P13B-3 cardinality failure: {report['counts']}")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        failure_state["failure_owner"] = "complete"
        return 0
    except Exception as exc:
        _write_failure_receipt(args.output, failure_state, exc, failure_started)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
