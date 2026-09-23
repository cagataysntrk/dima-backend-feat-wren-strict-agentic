#!/usr/bin/env python3
"""P12X-C2 direct-native vs typed-bridge parity scorer."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c1_score_parity as c1  # noqa: E402

EXPECTED_CORPUS = "fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0"
REPEAT_COUNT = 2


def load(path: Path) -> dict[str, Any]:
    return c1.load(path)


def bridge_transport_contract(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "single_native_agent_invocation": artifact.get("native_agent_invocation_count") == 1,
        "agent_api_analytical_fallback_zero": artifact.get("agent_api_analytical_fallback") == 0,
        "wren_fallback_zero": artifact.get("wren_fallback") == 0,
        "raw_sql_fallback_zero": artifact.get("raw_sql_fallback") == 0,
    }


def evaluate_pair(
    direct_art: dict[str, Any],
    bridge_art: dict[str, Any],
    oracle: dict[str, Any],
) -> dict[str, Any]:
    base = c1.evaluate_pair(direct_art, bridge_art, oracle)
    transport = bridge_transport_contract(bridge_art)
    return {
        "direct": base["stock"],
        "bridge": base["fork"],
        "permissions_equal": base["permissions_equal"],
        "direct_scope_ok": base["stock_scope_ok"],
        "bridge_scope_ok": base["fork_scope_ok"],
        "direct_pass_bridge_fail": base["stock_pass_fork_fail"],
        "new_bridge_silent_wrong": base["new_fork_silent_wrong"],
        "permission_regression": base["permission_regression"],
        "dataset_scope_drift": base["dataset_scope_drift"],
        "bridge_transport_contract": transport,
        "bridge_transport_contract_ok": all(transport.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--oracle", type=Path, required=True)
    ap.add_argument("--direct-dir", type=Path, required=True)
    ap.add_argument("--bridge-dir", type=Path, required=True)
    ap.add_argument("--repeat-root", type=Path)
    ap.add_argument("--phase", choices=["discover", "final"], default="final")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    cases = load(args.cases)
    oracle_all = load(args.oracle)
    if (
        cases.get("corpus_fingerprint") != EXPECTED_CORPUS
        or oracle_all.get("corpus_fingerprint") != EXPECTED_CORPUS
    ):
        raise SystemExit("C2 frozen corpus fingerprint drift")

    oracle_by = {x["id"]: x for x in oracle_all.get("results") or [] if isinstance(x, dict)}
    rows: list[dict[str, Any]] = []
    divergent: list[str] = []
    transport_contract_failures: list[str] = []

    for case_id in cases["case_ids"]:
        oracle = oracle_by[case_id]
        if oracle.get("kind") != "query":
            raise SystemExit(f"{case_id} must have executable query oracle")
        pair = evaluate_pair(
            load(args.direct_dir / f"{case_id}.json"),
            load(args.bridge_dir / f"{case_id}.json"),
            oracle,
        )
        if bool(pair["direct"]["pass"]) != bool(pair["bridge"]["pass"]):
            divergent.append(case_id)
        if not pair["bridge_transport_contract_ok"]:
            transport_contract_failures.append(case_id)
        rows.append({"case_id": case_id, "family": oracle.get("family"), **pair})

    if args.phase == "discover":
        report = {
            "schema_version": "p12x_c2_bridge_parity_discovery_v1",
            "corpus_fingerprint": EXPECTED_CORPUS,
            "status": "DIVERGENCE_DISCOVERED" if divergent else "NO_DIVERGENCE",
            "divergent_case_ids": divergent,
            "bridge_transport_contract_failures": transport_contract_failures,
            "cases": rows,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    repeats: dict[str, Any] = {}
    reproducible_regressions: list[str] = []
    reproducible_permission_regressions: list[str] = []
    reproducible_scope_drifts: list[str] = []
    reproducible_silent_wrong: list[str] = []
    stochastic_variance: list[str] = []

    if divergent:
        if args.repeat_root is None:
            raise SystemExit("divergence exists but --repeat-root is missing")
        for case_id in divergent:
            oracle = oracle_by[case_id]
            attempts = []
            for attempt in range(1, REPEAT_COUNT + 1):
                direct_path = args.repeat_root / "direct" / f"{case_id}-{attempt}.json"
                bridge_path = args.repeat_root / "bridge" / f"{case_id}-{attempt}.json"
                if not direct_path.exists() or not bridge_path.exists():
                    raise SystemExit(f"missing C2 repeat evidence: {case_id} attempt {attempt}")
                pair = evaluate_pair(load(direct_path), load(bridge_path), oracle)
                attempts.append({"attempt": attempt, **pair})
            repeats[case_id] = attempts

            if all(x["direct_pass_bridge_fail"] for x in attempts):
                reproducible_regressions.append(case_id)
            if all(x["permission_regression"] for x in attempts):
                reproducible_permission_regressions.append(case_id)
            if all(x["dataset_scope_drift"] for x in attempts):
                reproducible_scope_drifts.append(case_id)
            if all(x["new_bridge_silent_wrong"] for x in attempts):
                reproducible_silent_wrong.append(case_id)
            if not any([
                case_id in reproducible_regressions,
                case_id in reproducible_permission_regressions,
                case_id in reproducible_scope_drifts,
                case_id in reproducible_silent_wrong,
            ]):
                stochastic_variance.append(case_id)

    initial_direct_pass = [
        row["case_id"] for row in rows if row["direct"]["pass"]
    ]
    initial_retained = [
        row["case_id"] for row in rows if row["direct"]["pass"] and row["bridge"]["pass"]
    ]

    green = not (
        reproducible_regressions
        or reproducible_permission_regressions
        or reproducible_scope_drifts
        or reproducible_silent_wrong
        or transport_contract_failures
    )

    report = {
        "schema_version": "p12x_c2_bridge_parity_v1",
        "corpus_fingerprint": EXPECTED_CORPUS,
        "status": "GREEN" if green else "RED",
        "closure": {
            "selected_cases": cases["case_ids"],
            "initial_direct_pass": initial_direct_pass,
            "initial_bridge_retained_direct_pass": initial_retained,
            "initial_capability_retention": (
                len(initial_retained) / len(initial_direct_pass)
                if initial_direct_pass else 0.0
            ),
            "material_divergence_cases": divergent,
            "required_repeat_count_per_side": REPEAT_COUNT,
            "reproducible_direct_pass_bridge_fail": reproducible_regressions,
            "reproducible_new_bridge_silent_wrong": reproducible_silent_wrong,
            "reproducible_permission_regression": reproducible_permission_regressions,
            "reproducible_dataset_scope_drift": reproducible_scope_drifts,
            "bridge_transport_contract_failures": transport_contract_failures,
            "stochastic_variance_cases": stochastic_variance,
        },
        "cases": rows,
        "divergence_repeats": repeats,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["closure"], ensure_ascii=False, indent=2))
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
