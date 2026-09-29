from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--min-pass-percent", type=float, default=90.0)
    parser.add_argument("--max-total-model-units", type=int, required=True)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    if report.get("schema_version") != "dima_neutral_feature_benchmark_round2_v2":
        raise RuntimeError("P12 live report schema mismatch")
    if report.get("case_count") != 30:
        raise RuntimeError("P12 live benchmark must contain exactly 30 cases")

    passed = int(report.get("passed", 0))
    pass_percent = passed / 30.0 * 100.0
    if pass_percent < args.min_pass_percent:
        raise RuntimeError(
            f"P12 benchmark below acceptance: {pass_percent:.2f}% < {args.min_pass_percent:.2f}%"
        )

    units = int(report.get("observable_model_boundary_units", 0))
    if units > args.max_total_model_units:
        raise RuntimeError(
            f"P12 model-boundary ceiling exceeded: {units} > {args.max_total_model_units}"
        )

    cases = report.get("cases") or []
    if len(cases) != 30:
        raise RuntimeError("P12 case payload count mismatch")

    bad = []
    for case in cases:
        if not case.get("budget_ok", False):
            bad.append((case.get("id"), "budget"))
        if not case.get("all_turns_executed", False):
            bad.append((case.get("id"), "turns"))
        if not case.get("lineage_valid", False):
            bad.append((case.get("id"), "lineage"))
        if case.get("failure_class") == "CASE_EXCEPTION":
            bad.append((case.get("id"), "exception"))
    if bad:
        raise RuntimeError(f"P12 live integrity failures: {bad}")

    summary = {
        "schema_version": "dima_v1_phase1_p12_live_acceptance_v1",
        "case_count": 30,
        "passed": passed,
        "failed": int(report.get("failed", 0)),
        "pass_percent": pass_percent,
        "observable_model_boundary_units": units,
        "metabase_analytical_calls": int(report.get("metabase_analytical_calls", 0)),
        "accepted": True,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
