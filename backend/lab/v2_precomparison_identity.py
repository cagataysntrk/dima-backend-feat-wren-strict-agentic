"""Generate exact machine-readable Wren pre-comparison engineering identity.

Provider-free: reads git/source/config only and performs no model or Wren query call.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from app.config import get_settings
from app.v2.pilot import configuration_receipt
from lab.v2_day10_product_mvp_live import (
    FAST_MODEL,
    NARRATOR_MODEL,
    RESEARCH_MODEL,
    SEMANTIC_MODEL,
    TEMPORAL_MODEL,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_precomparison_engineering_identity.json"


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT.parent,
        text=True,
    ).strip()


def build_identity() -> dict:
    settings = get_settings()
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    head = _git("rev-parse", "HEAD")
    product = _git(
        "log",
        "-1",
        "--format=%H",
        "--",
        "backend/app/v2",
        "backend/app/routers/ask_v2.py",
        "backend/app/config.py",
    )
    wren_blob = _git("rev-parse", "HEAD:backend/app/wren_service.py")
    migration_tree = _git("rev-parse", "HEAD:backend/migrations/versions")
    pilot = configuration_receipt(settings).model_dump(mode="json")

    return {
        "identity_version": "v2-precomparison-engineering-identity-v1",
        "status": "WREN_PRE_COMPARISON_ENGINEERING_CANDIDATE",
        "branch": branch,
        "engineering_head": head,
        "product_behavior_sha": product,
        "migration_schema_tree": migration_tree,
        "wren_runtime_source_blob": wren_blob,
        "provider_topology": {
            "FAST_LANGUAGE": FAST_MODEL,
            "RESEARCH_MANAGER": RESEARCH_MODEL,
            "SEMANTIC_LINKER": SEMANTIC_MODEL,
            "TEMPORAL_NORMALIZER": TEMPORAL_MODEL,
            "REPORT_NARRATOR": NARRATOR_MODEL,
        },
        "manager_budget": {
            "max_preacceptance_turns": 4,
            "max_research_manager_turns": 4,
            "max_total_manager_turns": 8,
        },
        "feature_flag": pilot,
        "large_certification": {
            "DEV80": "DEFERRED_UNTIL_WINNER_SELECTED",
            "Validation50": "DEFERRED",
            "Hidden50": "DEFERRED",
        },
        "benchmark_manifest": "backend/eval/v2_precomparison_common_benchmark_manifest.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    identity = build_identity()
    if identity["feature_flag"]["pilot_enabled"]:
        raise SystemExit("pilot flag must remain OFF at pre-comparison seal")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(identity, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(identity, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
