#!/usr/bin/env python3
"""Provider-free P13C runtime/P10/P11 integration proof. No model calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.v3.entity_value_gate import (
    CurrentLensValueEvidence,
    EntityValueAdoptionGate,
    EntityValueDecision,
    EntityValueProposal,
)
from app.v3.native_standard.contracts import NativeAttestedRuntimeIdentity
from app.v3.security_identity import (
    ExecutionAccessSnapshotIssuer,
    VerifiedExecutionSecurityFacts,
)
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal

from lab.metabase.p13c.common import (
    CONTEXT_VERSION,
    FILTER_RESOURCE,
    FILTER_SEMANTIC_REF,
    FILTER_VALUE,
    PRINCIPAL,
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--restricted-email", required=True)
    ap.add_argument("--restricted-password", required=True)
    ap.add_argument("--duckdb", type=Path, required=True)
    ap.add_argument("--semantic-availability-report", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--build-identity", required=True)
    ap.add_argument("--image-identity", required=True)
    ap.add_argument("--platform-sha", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    token = login(args.base_url, args.restricted_email, args.restricted_password)
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
    _, intent = authority_and_intent()
    principal = Principal(
        user_id=PRINCIPAL,
        tenant_id=TENANT,
        tenant_slug=TENANT,
        roles=["analyst"],
    )
    metric_binding = managed_metric_binding(
        args.semantic_availability_report,
        engine_sha=args.engine_sha,
        platform_sha=args.platform_sha,
    )

    expected_engine = NativeEngineIdentity(
        repository="UpcyTech/dima-metabase-engine",
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_sha,
        runtime_tag=args.runtime_tag,
    )
    with NativeEngineBridge(
        base_url=args.base_url,
        session_token=token,
        expected_identity=expected_engine,
        timeout_seconds=120,
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

    resources = (TABLE_RESOURCE, TIME_RESOURCE, FILTER_RESOURCE)
    security = VerifiedExecutionSecurityFacts(
        tenant_binding=TENANT,
        principal_subject=PRINCIPAL,
        roles=("analyst",),
        attribute_policy_digest=h({"subject": mb_user_id, "policy": "p13c-provider-free"}),
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
        attestation_refs=("attestation:p13c-provider-free:runtime",),
        evidence_refs=("evidence:metabase-restricted-field-values:p13c",),
    )
    access = ExecutionAccessSnapshotIssuer.issue_for_expected_resources(
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
    if not values or len(set(values)) > 20:
        raise RuntimeError(f"P13C field is not low-cardinality: {values!r}")
    if FILTER_VALUE not in values:
        raise RuntimeError(
            f"frozen value {FILTER_VALUE!r} absent from restricted current-user evidence"
        )
    evidence = CurrentLensValueEvidence(
        semantic_ref=FILTER_SEMANTIC_REF,
        values=values,
        access_lens_ref=access.execution_access_fingerprint,
        freshness="CURRENT_USER_RETRIEVAL",
    )
    adopted = EntityValueAdoptionGate.adjudicate(
        proposal=EntityValueProposal(
            decision="BIND",
            semantic_ref=FILTER_SEMANTIC_REF,
            value=FILTER_VALUE,
        ),
        allowed_semantic_scopes=(FILTER_SEMANTIC_REF,),
        evidence=(evidence,),
        expected_access_lens_ref=access.execution_access_fingerprint,
    )
    if adopted.decision != EntityValueDecision.BIND:
        raise RuntimeError(f"P11 current-lens adoption did not bind: {adopted}")

    oracle = independent_oracle(args.duckdb)
    if oracle != 27:
        raise RuntimeError(f"frozen P13C oracle changed: expected 27 observed {oracle}")

    report = {
        "schema_version": "p13c_provider_free_integration_v1",
        "status": "GREEN",
        "model_calls": 0,
        "platform_sha": args.platform_sha,
        "engine_sha": args.engine_sha,
        "runtime_identity": identity.model_dump(mode="json"),
        "semantic_context_version": CONTEXT_VERSION,
        "managed_metric_binding": metric_binding.model_dump(mode="json"),
        "filter": {
            "semantic_ref": FILTER_SEMANTIC_REF,
            "physical_field": "satis_siparisleri.kanal",
            "metabase_field_id": filter_field_id,
            "frozen_value": FILTER_VALUE,
            "current_user_values": list(values),
            "current_user_contains_frozen_value": True,
            "freshness": "CURRENT_USER_RETRIEVAL",
            "access_lens_ref": access.execution_access_fingerprint,
            "p11_decision": adopted.decision.value,
            "p11_reason": adopted.reason_code,
        },
        "oracle": oracle,
        "new_resolver_framework": False,
        "fallbacks": {
            "agent_api_analytical": 0,
            "wren": 0,
            "raw_sql": 0,
            "admin_analytical": 0,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
