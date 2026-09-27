"""Assemble neutral Wren pre-comparison evidence package; provider-free."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IDENTITY = ROOT / "lab" / "reports" / "v2_precomparison_engineering_identity.json"
DEFAULT_RECEIPTS = ROOT / "eval" / "v2_precomparison_receipts.json"
DEFAULT_BENCHMARK = ROOT / "eval" / "v2_precomparison_common_benchmark_manifest.json"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_precomparison_comparison_package.json"

REQUIRED_RECEIPTS = {
    "day11",
    "day12",
    "day13",
    "day14",
    "day15",
    "day7_focused",
    "day8_focused",
    "day10_focused",
    "canary",
    "development_rehearsal",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity", type=Path, default=DEFAULT_IDENTITY)
    parser.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    identity = json.loads(args.identity.read_text(encoding="utf-8"))
    receipts = json.loads(args.receipts.read_text(encoding="utf-8"))
    benchmark = json.loads(args.benchmark.read_text(encoding="utf-8"))

    actual = set(receipts["runs"])
    missing = REQUIRED_RECEIPTS - actual
    if missing:
        raise SystemExit(f"missing comparison receipts: {sorted(missing)}")
    not_green = {
        key: value
        for key, value in receipts["runs"].items()
        if value.get("result") != "GREEN"
    }
    if not_green:
        raise SystemExit(f"non-green comparison receipts: {not_green}")
    if identity["feature_flag"]["pilot_enabled"]:
        raise SystemExit("pilot flag must remain OFF")
    if any(
        value != "DEFERRED" and "DEFERRED" not in value
        for value in identity["large_certification"].values()
    ):
        raise SystemExit("large certification must remain deferred")

    package = {
        "package_version": "v2-wren-precomparison-package-v1",
        "status": "WREN_PRE_COMPARISON_ENGINEERING_SEALED",
        "identity": identity,
        "test_receipts": receipts,
        "benchmark_manifest": benchmark,
        "architecture_summary": {
            "dima_role": "control / research / evidence / decision plane",
            "wren_role": "governed analytical execution truth",
            "semantic_truth_owner": "SemanticResolver / SemanticBindingGate",
            "execution_contract_owner": "QueryContract / ContractStore",
            "evidence_owner": "EvidenceStore",
            "epistemic_owner": "HypothesisLedger / EpistemicLabelGate",
            "completion_owner": "CompletionGate",
            "relationship_safety_owner": "CrossDomainJoinGate",
        },
        "known_limitations": [
            "Large DEV80 / Validation50 / Hidden50 certification is intentionally deferred until substrate winner selection.",
            "Pilot activation is intentionally OFF.",
            "Durable checkpoint storage currently uses the canonical filesystem CAS adapter contract; production storage adapter selection remains deployment work.",
            "Performance receipts before comparison are development samples, not p95 claims.",
        ],
        "day11_15_docs": [
            "backend/belgeler/plan/DIMA_DAY11_EVAL_EXPANSION.md",
            "backend/belgeler/plan/DIMA_DAY12_CONTRACT_EVIDENCE_TELEMETRY.md",
            "backend/belgeler/plan/DIMA_DAY13_SECURITY_CLOSURE.md",
            "backend/belgeler/plan/DIMA_DAY13_SECURITY_THREAT_MODEL.md",
            "backend/belgeler/plan/DIMA_DAY14_PERSISTENCE_RESUME.md",
            "backend/belgeler/plan/DIMA_DAY15_PILOT_ROLLBACK.md",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(package, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(package, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
