#!/usr/bin/env python3
"""P13C-01 one-Luna native Standard proof with one governed textual equality filter."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.v3.entity_value_gate import CurrentLensValueEvidence
from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.execution_identity import ExecutionEventIdentity, ExecutionResultSnapshot, RuntimeIdentity
from app.v3.native_execution import NativeCandidateOutcome
from app.v3.native_standard.contracts import (
    NativeAttestationEnvelope,
    NativeAttestedRuntimeIdentity,
)
from app.v3.native_standard.trust import NativeStandardTrustOrchestrator
from app.v3.security_identity import ExecutionAccessSnapshotIssuer, VerifiedExecutionSecurityFacts
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity, NativeEngineRequest
from control_plane.authorize import Principal

from lab.metabase.p13b.px01_live_standard import (
    _diagnostic_error_code,
    _diagnostic_usage,
    query_id_from_stream,
    scalar,
)
from lab.metabase.p13c.common import (
    CASE_ID,
    CONTEXT_VERSION,
    FILTER_RESOURCE,
    FILTER_SEMANTIC_REF,
    FILTER_VALUE,
    PRINCIPAL,
    QUESTION,
    TABLE_RESOURCE,
    TENANT,
    TIME_RESOURCE,
    assert_identity,
    authority_and_intent,
    binding_snapshot,
    current_user_values,
    discover_catalog,
    h,
    independent_oracle,
    login,
    managed_metric_binding,
)


def _write_failure(output: Path, state: dict, exc: Exception, started: float) -> None:
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
    path = output.with_name("P13C_01_LIVE_FAILURE.json")
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
    state = {
        "schema_version": "p13c_01_live_failure_v1",
        "case_id": CASE_ID,
        "question": QUESTION,
        "frozen_filter_value": FILTER_VALUE,
        "platform_sha": args.platform_sha,
        "engine_sha": args.engine_sha,
        "model_identifier": args.model_identifier,
        "live_attempt_id": args.live_attempt_id,
        "failure_owner": "bootstrap",
    }

    try:
        oracle = independent_oracle(args.duckdb)
        if oracle != 27:
            raise RuntimeError(f"frozen oracle changed: expected 27 observed {oracle}")

        token = login(args.base_url, args.email, args.password)
        (
            database_id,
            table_id,
            time_field_id,
            filter_field_id,
            schema_name,
            mb_user_id,
        ) = discover_catalog(args.base_url, token)
        snapshot = binding_snapshot(
            database_id, table_id, time_field_id, filter_field_id, schema_name
        )
        metric_binding = managed_metric_binding(
            args.semantic_availability_report,
            engine_sha=args.engine_sha,
            platform_sha=args.platform_sha,
        )
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
        request_id = "p13c-01-" + conversation_id.hex[:12]
        started = time.monotonic()

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

            # Current-lens evidence is established before native cognition. The P10/P5
            # fingerprint deliberately excludes proof-record refs, so the later native
            # attestation can be appended without creating a second access identity.
            resources = (TABLE_RESOURCE, TIME_RESOURCE, FILTER_RESOURCE)
            security = VerifiedExecutionSecurityFacts(
                tenant_binding=TENANT,
                principal_subject=PRINCIPAL,
                roles=("analyst",),
                attribute_policy_digest=h({"subject": mb_user_id, "policy": "p13c-live"}),
                policy_version="p13c-v1",
                rls_versions=(),
                cls_versions=(),
                database_route="analytics-primary",
                database_destination="boyahane",
                impersonation_role=None,
                semantic_context_version=CONTEXT_VERSION,
                source_object_refs=resources,
                security_parameter_digest=h(
                    {
                        "metabase_subject": mb_user_id,
                        "database_id": database_id,
                        "table_id": table_id,
                        "time_field_id": time_field_id,
                        "filter_field_id": filter_field_id,
                    }
                ),
                metabase_subject_ref=f"metabase-user:{mb_user_id}",
                attestation_refs=(
                    f"engine-identity:{identity.runtime_instance_id}",
                    f"metabase-current-subject:{mb_user_id}",
                ),
                evidence_refs=(
                    f"metabase-current-user:{mb_user_id}",
                ),
            )
            pre_access = ExecutionAccessSnapshotIssuer.issue_for_expected_resources(
                current_principal=principal,
                accepted_intent=intent,
                verified_security_facts=security,
                expected_source_object_refs=resources,
            )
            values = current_user_values(
                args.base_url,
                token,
                field_id=filter_field_id,
            )
            if FILTER_VALUE not in values:
                raise RuntimeError("frozen filter value absent from current-user evidence")
            current_evidence = CurrentLensValueEvidence(
                semantic_ref=FILTER_SEMANTIC_REF,
                values=values,
                access_lens_ref=pre_access.execution_access_fingerprint,
                freshness="CURRENT_USER_RETRIEVAL",
            )

            state["failure_owner"] = "native-metabot-invoke"
            observation = client.invoke(
                NativeEngineRequest(
                    message=QUESTION,
                    conversation_id=conversation_id,
                    dima_request_id=request_id,
                    dima_trace_id=request_id + "-trace",
                )
            )
            native_query_id = query_id_from_stream(observation.data_parts)
            state["native_query_id"] = native_query_id
            state["native_tool_call_count"] = len(observation.tool_calls)
            state["native_agent_latency_ms"] = observation.latency_ms
            state["provider_usage"] = _diagnostic_usage(observation)

            state["failure_owner"] = "native-query-attestation"
            attestation = NativeAttestationEnvelope.model_validate(
                client.attest_native_query(
                    conversation_id=conversation_id,
                    native_query_id=native_query_id,
                )
            )
            if attestation.manifest.runtime_identity != identity:
                raise RuntimeError("attestation runtime identity differs from live identity")

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

            engine = NativeEngineIdentity(
                repository=identity.repository,
                engine_sha=identity.revision_sha,
                upstream_base_sha=identity.upstream_base_sha,
                runtime_tag=identity.runtime_tag,
                build_identity=identity.build_identity,
                runtime_image_identity=identity.image_identity,
                runtime_instance_id=identity.runtime_instance_id,
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
                current_lens_value_evidence=(current_evidence,),
            )
            if authz.authorization.outcome != NativeCandidateOutcome.ALLOW:
                raise RuntimeError(
                    f"P13C-01 blocked: {authz.authorization.code}: {authz.authorization.detail}"
                )
            artifact = authz.authorization.authorized_artifact
            if artifact is None or authz.access_snapshot is None:
                raise RuntimeError("ALLOW missing artifact/access snapshot")
            if (
                authz.access_snapshot.execution_access_fingerprint
                != pre_access.execution_access_fingerprint
            ):
                raise RuntimeError("P10 current-lens fingerprint changed after authorization")

            execution_request = NativeStandardTrustOrchestrator.execution_request(
                result=authz,
                attestation=attestation,
            )
            fingerprints = {
                "attested": attestation.manifest.exact_pmbql_fingerprint,
                "authorized": artifact.steps[0].artifact_fingerprint,
            }
            if len(set(fingerprints.values())) != 1:
                raise RuntimeError(f"pre-execution fingerprint mismatch: {fingerprints}")

            state["failure_owner"] = "exact-occurrence-execution"
            execution = client.execute_native_query(
                conversation_id=execution_request.native_conversation_id,
                native_query_id=execution_request.native_query_id,
                expected_pmbql_fingerprint=execution_request.expected_pmbql_fingerprint,
                expected_attestation_id=execution_request.expected_attestation_id,
            )
            fingerprints["executed"] = execution.executed_pmbql_fingerprint
            if len(set(fingerprints.values())) != 1:
                raise RuntimeError(f"P13C-01: executed fingerprint mismatch: {fingerprints}")
            execution_identity = NativeAttestedRuntimeIdentity.model_validate(
                execution.runtime_identity
            )
            if execution_identity != identity:
                raise RuntimeError("P13C-01: runtime identity changed in exact-occurrence execution")
            execution_attestation = NativeAttestationEnvelope.model_validate(execution.attestation)
            if execution_attestation != attestation:
                raise RuntimeError("P13C-01: execution re-attestation differs from authorized occurrence")
            observed, rows = scalar(execution.payload)
            after = NativeAttestedRuntimeIdentity.model_validate(client.engine_identity())
            if after != identity:
                raise RuntimeError("runtime changed across exact exact-occurrence execution")

        state["failure_owner"] = "receipt-sealing"
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
                execution_id="exec-p13c-" + conversation_id.hex[:16],
                executed_at=datetime.now(timezone.utc),
            ),
        )
        fingerprints["receipt"] = receipt.canonical_query_fingerprint
        if len(set(fingerprints.values())) != 1:
            raise RuntimeError(f"receipt fingerprint mismatch: {fingerprints}")
        if observed != oracle:
            raise RuntimeError(f"receipted result {observed!r} != oracle {oracle!r}")

        evidence = EvidenceArtifact(
            artifact_id="evi_" + h(
                {"receipt": receipt.receipt_id, "observed": observed, "oracle": oracle}
            )[:24],
            authority_id=authority.authority_id,
            obligation_ids=intent.obligation_ids,
            query_receipt_refs=(receipt.receipt_id,),
            evidence_kind="p13c_textual_equality_standard_scalar",
            state=EvidenceState.VERIFIED,
            payload={
                "case_id": CASE_ID,
                "official_answer": observed,
                "oracle": oracle,
                "filter": {"field": "kanal", "value": FILTER_VALUE},
            },
        )
        if not evidence.verified:
            raise RuntimeError("Evidence is not VERIFIED")

        usage = _diagnostic_usage(observation)
        report = {
            "schema_version": "p13c_01_live_standard_v1",
            "status": "GREEN",
            "case_id": CASE_ID,
            "question": QUESTION,
            "official_answer": observed,
            "oracle": oracle,
            "primary_user_turns": 1,
            "filter": {
                "semantic_ref": FILTER_SEMANTIC_REF,
                "physical_field": "satis_siparisleri.kanal",
                "value": FILTER_VALUE,
                "current_user_values": list(values),
                "access_lens_ref": authz.access_snapshot.execution_access_fingerprint,
                "typed_native_predicates": [
                    item.model_dump(mode="json")
                    for item in attestation.manifest.textual_equality_predicates
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
            "runtime_identity": identity.model_dump(mode="json"),
            "managed_metric_binding": metric_binding.model_dump(mode="json"),
            "receipt": receipt.model_dump(mode="json"),
            "evidence": evidence.model_dump(mode="json"),
            "economics": {
                "provider_model_identifier": args.model_identifier,
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
            raise RuntimeError(f"P13C cardinality failure: {report['counts']}")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        _write_failure(args.output, state, exc, started_all)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
