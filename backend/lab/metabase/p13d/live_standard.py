#!/usr/bin/env python3
"""One compact Luna proof for the cohesive P13D Standard slice."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.execution_identity import ExecutionEventIdentity, ExecutionResultSnapshot, RuntimeIdentity
from app.v3.native_execution import NativeCandidateOutcome
from app.v3.native_standard.contracts import (
    NativeAttestationEnvelope,
    NativeAttestedRuntimeIdentity,
)
from app.v3.native_standard.trust import NativeStandardTrustOrchestrator
from app.v3.security_identity import VerifiedExecutionSecurityFacts
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity, NativeEngineRequest
from control_plane.authorize import Principal

from lab.metabase.p13b.px01_live_standard import (
    _diagnostic_error_code,
    _diagnostic_usage,
    query_id_from_stream,
)
from lab.metabase.p13d.common import (
    BREAKDOWN_CASE,
    COMPARISON_CASE,
    PRINCIPAL,
    RANKING_CASE,
    TENANT,
    assert_identity,
    binding_snapshot,
    cases,
    discover_catalog,
    h,
    independent_oracles,
    login,
    managed_metric_binding,
)


def _failure(output: Path, state: dict[str, Any], exc: Exception, started: float) -> None:
    body = dict(state)
    body.update(
        {
            "status": "RED",
            "error_type": type(exc).__name__,
            "error_code": _diagnostic_error_code(exc),
            "error_message": str(exc)[:3000],
            "elapsed_ms": max(0, int((time.monotonic() - started) * 1000)),
        }
    )
    path = output.with_name("P13D_LIVE_FAILURE.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _rows(payload: dict[str, Any]) -> list[list[Any]]:
    rows = (payload.get("data") or {}).get("rows")
    if not isinstance(rows, list) or not all(isinstance(row, list) for row in rows):
        raise RuntimeError(f"P13D dataset result has invalid rows: {rows!r}")
    return rows


def _is_count(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _pairs(rows: list[list[Any]], *, temporal: bool = False) -> list[list[Any]]:
    result: list[list[Any]] = []
    for row in rows:
        if len(row) != 2:
            raise RuntimeError(f"P13D grouped result row is not two columns: {row!r}")
        numeric = [i for i, value in enumerate(row) if _is_count(value)]
        if len(numeric) != 1:
            raise RuntimeError(f"P13D grouped row has ambiguous count column: {row!r}")
        count_i = numeric[0]
        label_i = 1 - count_i
        count_value = row[count_i]
        if isinstance(count_value, float) and not count_value.is_integer():
            raise RuntimeError(f"P13D COUNT result is non-integral: {count_value!r}")
        label = row[label_i]
        if temporal:
            key = str(label)[:7]
            if len(key) != 7 or key[4] != "-":
                raise RuntimeError(f"P13D temporal breakout is not a month value: {label!r}")
        else:
            key = str(label)
        result.append([key, int(count_value)])
    return result


def _official(case_id: str, payload: dict[str, Any]) -> Any:
    rows = _rows(payload)
    if case_id == BREAKDOWN_CASE:
        pairs = _pairs(rows)
        return {label: count for label, count in pairs}
    if case_id == RANKING_CASE:
        return _pairs(rows)
    if case_id == COMPARISON_CASE:
        pairs = _pairs(rows, temporal=True)
        return {month: count for month, count in pairs}
    raise RuntimeError(f"unknown P13D case: {case_id}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--duckdb", type=Path, required=True)
    ap.add_argument("--semantic-availability-report", type=Path, required=True)
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
    args = ap.parse_args()

    started_all = time.monotonic()
    state: dict[str, Any] = {
        "schema_version": "p13d_live_failure_v1",
        "platform_sha": args.platform_sha,
        "engine_sha": args.engine_sha,
        "model_identifier": args.model_identifier,
        "live_attempt_id": args.live_attempt_id,
        "failure_owner": "bootstrap",
        "completed_cases": [],
    }

    try:
        oracles = independent_oracles(args.duckdb)
        token = login(args.base_url, args.email, args.password)
        (
            database_id,
            table_id,
            time_field_id,
            channel_field_id,
            schema_name,
            mb_user_id,
        ) = discover_catalog(args.base_url, token)
        snapshot = binding_snapshot(
            database_id,
            table_id,
            time_field_id,
            channel_field_id,
            schema_name,
        )
        metric_binding = managed_metric_binding(
            args.semantic_availability_report,
            engine_sha=args.engine_sha,
            platform_sha=args.platform_sha,
        )
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

        reports: list[dict[str, Any]] = []
        with NativeEngineBridge(
            base_url=args.base_url,
            session_token=token,
            expected_identity=expected_bootstrap,
            timeout_seconds=300,
        ) as client:
            identity = NativeAttestedRuntimeIdentity.model_validate(client.engine_identity())
            assert_identity(
                identity,
                engine_sha=args.engine_sha,
                upstream_sha=args.upstream_sha,
                runtime_tag=args.runtime_tag,
                build_identity=args.build_identity,
                image_identity=args.image_identity,
            )
            engine = NativeEngineIdentity(
                repository=identity.repository,
                engine_sha=identity.revision_sha,
                upstream_base_sha=identity.upstream_base_sha,
                runtime_tag=identity.runtime_tag,
                build_identity=identity.build_identity,
                runtime_image_identity=identity.image_identity,
                runtime_instance_id=identity.runtime_instance_id,
            )

            for case_id, question, intent_factory, resources in cases():
                case_started = time.monotonic()
                authority, intent = intent_factory()
                conversation_id = uuid4()
                request_id = f"p13d-{case_id.lower()}-" + conversation_id.hex[:10]
                state.update(
                    {
                        "case_id": case_id,
                        "question": question,
                        "failure_owner": "native-metabot-invoke",
                        "native_query_id": None,
                        "native_tool_call_count": None,
                        "exact_pmbql_fingerprint": None,
                        "exact_serialized_pmbql": None,
                        "breakouts": [],
                        "order_bys": [],
                        "limit": None,
                        "temporal_predicates": [],
                        "metric_references": [],
                        "trust_error_code": None,
                        "trust_error_detail": None,
                        "engine_runtime_identity": None,
                        "engine_attestation_state": None,
                    }
                )
                security = VerifiedExecutionSecurityFacts(
                    tenant_binding=TENANT,
                    principal_subject=PRINCIPAL,
                    roles=("analyst",),
                    attribute_policy_digest=h(
                        {"subject": mb_user_id, "policy": "p13d-live", "case": case_id}
                    ),
                    policy_version="p13d-v1",
                    rls_versions=(),
                    cls_versions=(),
                    database_route="analytics-primary",
                    database_destination="boyahane",
                    impersonation_role=None,
                    semantic_context_version=snapshot.semantic_context_version,
                    source_object_refs=resources,
                    security_parameter_digest=h(
                        {
                            "case": case_id,
                            "metabase_subject": mb_user_id,
                            "database_id": database_id,
                            "table_id": table_id,
                            "time_field_id": time_field_id,
                            "channel_field_id": channel_field_id,
                        }
                    ),
                    metabase_subject_ref=f"metabase-user:{mb_user_id}",
                    attestation_refs=(
                        f"engine-identity:{identity.runtime_instance_id}",
                        f"metabase-current-subject:{mb_user_id}",
                    ),
                    evidence_refs=(f"metabase-current-user:{mb_user_id}",),
                )

                observation = client.invoke(
                    NativeEngineRequest(
                        message=question,
                        conversation_id=conversation_id,
                        dima_request_id=request_id,
                        dima_trace_id=request_id + "-trace",
                    )
                )
                native_query_id = query_id_from_stream(observation.data_parts)
                state.update(
                    {
                        "native_query_id": native_query_id,
                        "native_tool_call_count": len(observation.tool_calls),
                    }
                )

                state["failure_owner"] = "native-query-attestation"
                attestation = NativeAttestationEnvelope.model_validate(
                    client.attest_native_query(
                        conversation_id=conversation_id,
                        native_query_id=native_query_id,
                    )
                )
                if attestation.manifest.runtime_identity != identity:
                    raise RuntimeError(
                        f"{case_id}: attestation runtime identity differs from live identity"
                    )
                state.update(
                    {
                        "exact_pmbql_fingerprint": attestation.manifest.exact_pmbql_fingerprint,
                        "exact_serialized_pmbql": attestation.exact_serialized_pmbql,
                        "breakouts": [
                            item.model_dump(mode="json") for item in attestation.manifest.breakouts
                        ],
                        "order_bys": [
                            item.model_dump(mode="json") for item in attestation.manifest.order_bys
                        ],
                        "limit": attestation.manifest.limit,
                        "temporal_predicates": [
                            item.model_dump(mode="json")
                            for item in attestation.manifest.temporal_predicates
                        ],
                        "metric_references": [
                            item.model_dump(mode="json")
                            for item in attestation.manifest.native_metric_references
                        ],
                        "engine_runtime_identity": identity.model_dump(mode="json"),
                        "engine_attestation_state": {
                            "status": "ATTESTED",
                            "attestation_id": attestation.manifest.attestation_id,
                        },
                    }
                )
                security = security.model_copy(
                    update={
                        "attestation_refs": tuple(
                            sorted(
                                {
                                    *security.attestation_refs,
                                    attestation.manifest.attestation_id,
                                }
                            )
                        )
                    }
                )

                state["failure_owner"] = "dima-trust-authorization"
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
                    state.update(
                        {
                            "trust_error_code": authz.authorization.code,
                            "trust_error_detail": authz.authorization.detail,
                        }
                    )
                    raise RuntimeError(
                        f"{case_id} blocked: {authz.authorization.code}: "
                        f"{authz.authorization.detail}"
                    )
                artifact = authz.authorization.authorized_artifact
                if artifact is None or authz.access_snapshot is None:
                    raise RuntimeError(f"{case_id}: ALLOW missing artifact/access snapshot")

                execution_request = NativeStandardTrustOrchestrator.execution_request(
                    result=authz,
                    attestation=attestation,
                )
                fingerprints = {
                    "attested": attestation.manifest.exact_pmbql_fingerprint,
                    "authorized": artifact.steps[0].artifact_fingerprint,
                    "submitted": h(execution_request.exact_serialized_pmbql),
                }
                if len(set(fingerprints.values())) != 1:
                    raise RuntimeError(
                        f"{case_id}: pre-execution fingerprint mismatch: {fingerprints}"
                    )

                state["failure_owner"] = "dataset-execution"
                execution = client.execute_dataset(execution_request.exact_serialized_pmbql)
                rows = _rows(execution.payload)
                observed = _official(case_id, execution.payload)
                after = NativeAttestedRuntimeIdentity.model_validate(client.engine_identity())
                if after != identity:
                    raise RuntimeError(f"{case_id}: runtime changed across dataset execution")

                state["failure_owner"] = "receipt-sealing"
                receipt = NativeStandardTrustOrchestrator.seal_receipt(
                    intent=intent,
                    result=authz,
                    execution_request=execution_request,
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
                    execution_result=ExecutionResultSnapshot(
                        payload={"rows": rows},
                        row_count=len(rows),
                    ),
                    execution_event=ExecutionEventIdentity(
                        execution_id=f"exec-{case_id.lower()}-" + conversation_id.hex[:12],
                        executed_at=datetime.now(timezone.utc),
                    ),
                )
                fingerprints["receipt"] = receipt.canonical_query_fingerprint
                if len(set(fingerprints.values())) != 1:
                    raise RuntimeError(
                        f"{case_id}: receipt fingerprint mismatch: {fingerprints}"
                    )

                oracle = oracles[case_id]
                if observed != oracle:
                    raise RuntimeError(
                        f"{case_id}: receipted result {observed!r} != oracle {oracle!r}"
                    )

                evidence = EvidenceArtifact(
                    artifact_id="evi_" + h(
                        {
                            "case": case_id,
                            "receipt": receipt.receipt_id,
                            "observed": observed,
                            "oracle": oracle,
                        }
                    )[:24],
                    authority_id=authority.authority_id,
                    obligation_ids=intent.obligation_ids,
                    query_receipt_refs=(receipt.receipt_id,),
                    evidence_kind="p13d_native_standard_" + case_id.lower(),
                    state=EvidenceState.VERIFIED,
                    payload={
                        "case_id": case_id,
                        "official_answer": observed,
                        "oracle": oracle,
                    },
                )
                if not evidence.verified:
                    raise RuntimeError(f"{case_id}: Evidence is not VERIFIED")

                usage = _diagnostic_usage(observation)
                reports.append(
                    {
                        "case_id": case_id,
                        "question": question,
                        "official_answer": observed,
                        "oracle": oracle,
                        "primary_user_turns": 1,
                        "native_query_id": native_query_id,
                        "manifest": {
                            "breakouts": [
                                item.model_dump(mode="json")
                                for item in attestation.manifest.breakouts
                            ],
                            "order_bys": [
                                item.model_dump(mode="json")
                                for item in attestation.manifest.order_bys
                            ],
                            "limit": attestation.manifest.limit,
                            "temporal_predicates": [
                                item.model_dump(mode="json")
                                for item in attestation.manifest.temporal_predicates
                            ],
                        },
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
                        "receipt": receipt.model_dump(mode="json"),
                        "evidence": evidence.model_dump(mode="json"),
                        "economics": {
                            "provider_model_identifier": args.model_identifier,
                            "native_tool_call_count": len(observation.tool_calls),
                            "analytical_query_count": attestation.manifest.material_query_count,
                            "native_agent_latency_ms": observation.latency_ms,
                            "dataset_latency_ms": execution.latency_ms,
                            "end_to_end_ms": max(
                                0, int((time.monotonic() - case_started) * 1000)
                            ),
                            "prompt_tokens": usage.get("promptTokens"),
                            "completion_tokens": usage.get("completionTokens"),
                            "provider_cost": usage.get("cost"),
                            "raw_usage": usage,
                        },
                    }
                )
                if tuple(reports[-1]["counts"].values()) != (1, 1, 1, 1, 1, 1, 1, 1):
                    raise RuntimeError(f"{case_id}: cardinality failure")
                state["completed_cases"].append(reports[-1])

        report = {
            "schema_version": "p13d_cohesive_live_v1",
            "status": "GREEN",
            "platform_sha": args.platform_sha,
            "engine_sha": args.engine_sha,
            "model_identifier": args.model_identifier,
            "live_attempt_id": args.live_attempt_id,
            "runtime_identity": identity.model_dump(mode="json"),
            "managed_metric_binding": metric_binding.model_dump(mode="json"),
            "primary_user_turns": 3,
            "cases": reports,
            "silent_wrong": 0,
            "agent_api_analytical_fallback": 0,
            "wren_fallback": 0,
            "raw_sql_fallback": 0,
            "admin_analytical_fallback": 0,
            "end_to_end_ms": max(0, int((time.monotonic() - started_all) * 1000)),
        }
        if len(reports) != 3:
            raise RuntimeError(f"P13D expected three certified cases, observed {len(reports)}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        _failure(args.output, state, exc, started_all)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
