#!/usr/bin/env python3
"""P13D digest-backed provider-free runtime identity/oracle proof. No model calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.v3.native_standard.contracts import NativeAttestedRuntimeIdentity
from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity

from lab.metabase.p13d.common import (
    binding_snapshot,
    discover_catalog,
    independent_oracles,
    login,
    managed_metric_binding,
    assert_identity,
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
    database_id, table_id, time_field_id, channel_field_id, schema_name, _ = discover_catalog(
        args.base_url, token
    )
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
    expected = NativeEngineIdentity(
        repository="UpcyTech/dima-metabase-engine",
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_sha,
        runtime_tag=args.runtime_tag,
    )
    with NativeEngineBridge(
        base_url=args.base_url,
        session_token=token,
        expected_identity=expected,
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
    oracles = independent_oracles(args.duckdb)
    kinds = {item.candidate_id: item.kind for item in snapshot.candidate_bindings}
    if kinds != {
        "cand_sales_order_count": "metric",
        "cand_sales_order_channel": "dimension",
    }:
        raise RuntimeError(f"P13D candidate bindings drifted: {kinds!r}")

    report = {
        "schema_version": "p13d_provider_free_runtime_v1",
        "status": "GREEN",
        "model_calls": 0,
        "platform_sha": args.platform_sha,
        "engine_sha": args.engine_sha,
        "runtime_identity": identity.model_dump(mode="json"),
        "semantic_context_version": snapshot.semantic_context_version,
        "managed_metric_binding": metric_binding.model_dump(mode="json"),
        "candidate_binding_kinds": kinds,
        "independent_oracles": oracles,
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
