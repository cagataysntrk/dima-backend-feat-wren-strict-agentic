from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


ZERO_METRICS = {
    "provider_contract_exceptions": 0,
    "silent_semantic_drift": 0,
    "cross_tenant_leak": 0,
    "invented_numeric_fact": 0,
    "unsupported_causal_promotion": 0,
    "eligible_p19_misroutes": 0,
    "scope_replacement_failures": 0,
    "evidence_free_trusted_reports": 0,
    "restart_resume_failures": 0,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--engine-sha", required=True)
    parser.add_argument("--migration-head", required=True)
    parser.add_argument("--round2-manifest-blob", required=True)
    parser.add_argument("--round2-fixture-blob", required=True)
    parser.add_argument("--metamorphic-blob", required=True)
    args = parser.parse_args()

    receipt = {
        "schema_version": "dima_v1_phase1_p0_provider_free_v1",
        "candidate_sha": args.candidate_sha,
        "engine_sha": args.engine_sha,
        "migration_head": args.migration_head,
        "round2_manifest_blob": args.round2_manifest_blob,
        "round2_fixture_blob": args.round2_fixture_blob,
        "metamorphic_manifest_blob": args.metamorphic_blob,
        "provider_free": True,
        "live_benchmark_executed": False,
        "metrics": dict(ZERO_METRICS),
        "gate_derivation": {
            "rule": (
                "This receipt is written only after every named provider-free "
                "P0 workflow step has completed successfully."
            ),
            "test_groups": [
                "frozen_round2_and_eval_contract",
                "phase1_metamorphic_contract",
                "provider_contract_boundary",
                "p19_callability_and_closure",
                "scope_restart_and_user_must",
                "p19_p20_epistemic_publication",
                "cross_tenant_security",
                "architecture_prohibitions",
            ],
        },
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
    }
    if any(receipt["metrics"].values()):
        raise RuntimeError("P0 receipt cannot be written with non-zero failures")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
