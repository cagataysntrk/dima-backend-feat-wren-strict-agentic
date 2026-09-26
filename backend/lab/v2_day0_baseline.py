"""P3 Day 0: reproducible legacy baseline runner for the V2 migration.

This is a measurement tool, not a new product path. It exercises the existing /ask
endpoint and existing experience scenarios, recording outcome/source/correctness/
failure_stage/latency without changing legacy behavior.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "eval" / "v2_day0_cases.yaml"
CASES = ROOT / "eval" / "cases.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day0_baseline.json"


def _prepare_env() -> None:
    os.environ["DIMA_LLM_PROVIDER"] = "rule"
    os.environ["DIMA_VQR_EMBEDDER"] = "off"
    os.environ["DIMA_INTERACTION_LOG"] = "false"
    os.environ["DIMA_SCHEDULER_ENABLED"] = "false"
    os.environ["DIMA_DATABASE_URL"] = "sqlite:///" + os.path.join(
        tempfile.mkdtemp(prefix="dima-v2-day0-cp-"), "control_plane.db"
    )
    os.environ.setdefault("DIMA_JWT_SECRET", "v2-day0-public-access-secret")
    os.environ.setdefault("DIMA_JWT_REFRESH_SECRET", "v2-day0-public-refresh-secret")


def _failure_stage(step: dict[str, Any], response: dict[str, Any], actual: str, correct: bool) -> str:
    if correct:
        return "none"
    if response.get("_http"):
        return "http"
    if actual != step["expect"]:
        return "outcome"
    from eval.run import shape_ok, source_ok

    if "expect_source" in step and not source_ok(response, str(step["expect_source"])):
        return "source"
    if "shape" in step and not shape_ok(response.get("cube_query"), step["shape"]):
        return "semantic_shape"
    if "note_contains" in step:
        return "note_contract"
    if "chip_labels_has" in step:
        return "clarification_contract"
    return "unknown"


def _run_eval_case(client, case: dict[str, Any]) -> list[dict[str, Any]]:
    from eval.run import step_result

    records: list[dict[str, Any]] = []
    steps = case.get("flow") or [case]
    cq: dict[str, Any] | None = None
    history: list[str] = []

    for index, step in enumerate(steps):
        payload: dict[str, Any] = {
            "question": step["q"],
            "execute": True,
            "session_id": f"v2-day0-{case['id']}",
        }
        if cq:
            payload["cube_query"] = cq
        if history:
            payload["history"] = history

        started = time.perf_counter()
        response = client.post("/ask", json=payload)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        data = response.json() if response.status_code == 200 else {"_http": response.status_code}
        if response.status_code == 200:
            actual, correct = step_result(data, step["expect"], step)
        else:
            # Transport/infrastructure failure is never a semantically correct refusal.
            actual, correct = "http_error", False

        records.append(
            {
                "unit": case["id"],
                "step": index,
                "question": step["q"],
                "family": list(case.get("tags") or []),
                "expected": step["expect"],
                "outcome": actual,
                "source": data.get("source"),
                "correct": bool(correct),
                "failure_stage": _failure_stage(step, data, actual, bool(correct)),
                "latency_ms": latency_ms,
            }
        )
        cq = data.get("cube_query") or cq
        history.append(step["q"])

    return records


def _run_experience(client, names: list[str]) -> list[dict[str, Any]]:
    from lab import deneyim

    by_name = {scenario["ad"]: scenario for scenario in deneyim.SENARYOLAR}
    missing = [name for name in names if name not in by_name]
    if missing:
        raise RuntimeError(f"Day0 experience scenario bulunamadı: {missing}")

    records: list[dict[str, Any]] = []
    for name in names:
        started = time.perf_counter()
        result = deneyim.kos(client, by_name[name], live=False)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        measured = {
            key: value
            for key, value in result["olcum"].items()
            if value != deneyim.KAPSAM_DISI
        }
        correct = all(value is True for value in measured.values())
        sources = [
            turn["cevap"].get("source")
            for turn in result["turlar"]
            if turn.get("cevap")
        ]
        records.append(
            {
                "unit": f"experience:{name}",
                "step": None,
                "question": " → ".join(
                    str(turn) for turn in by_name[name]["turlar"] if isinstance(turn, str)
                ),
                "family": ["experience", "conversation"],
                "expected": "scenario_contract",
                "outcome": "scenario",
                "source": sources,
                "correct": correct,
                "failure_stage": "none" if correct else "experience_contract",
                "latency_ms": latency_ms,
                "checks": measured,
            }
        )
    return records


def _validate_manifest(manifest: dict[str, Any], cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {case["id"]: case for case in cases}
    ids = list(manifest.get("eval_case_ids") or [])
    exp = list(manifest.get("experience_scenarios") or [])
    minimum = int(manifest.get("minimum_units") or 30)

    missing = [case_id for case_id in ids if case_id not in by_id]
    if missing:
        raise RuntimeError(f"Day0 eval case bulunamadı: {missing}")
    if len(ids) + len(exp) < minimum:
        raise RuntimeError(f"Day0 baseline yetersiz: {len(ids) + len(exp)} < {minimum}")

    inventory = manifest.get("known_silent_wrong_inventory") or {}
    required = {case_id for group in inventory.values() for case_id in group}
    uncovered = sorted(required - set(ids))
    if uncovered:
        raise RuntimeError(f"Known silent-wrong inventory baseline dışında: {uncovered}")

    return [by_id[case_id] for case_id in ids]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    _prepare_env()

    from fastapi.testclient import TestClient

    from app.compose import compose_and_build
    from app.config import get_settings
    from app.main import create_app
    from eval.run import _login_eval_user

    get_settings.cache_clear()
    compose_and_build(get_settings())

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    selected = _validate_manifest(manifest, cases)

    records: list[dict[str, Any]] = []
    with TestClient(create_app()) as client:
        _login_eval_user(client)
        for case in selected:
            records.extend(_run_eval_case(client, case))
        records.extend(_run_experience(client, list(manifest["experience_scenarios"])))

    incorrect = [record for record in records if not record["correct"]]
    output = {
        "kind": "dima_v2_day0_legacy_baseline",
        "source_head": manifest["source_head"],
        "execution_mode": manifest["execution_mode"],
        "selected_units": len(selected) + len(manifest["experience_scenarios"]),
        "records": len(records),
        "correct_records": len(records) - len(incorrect),
        "incorrect_records": len(incorrect),
        "known_silent_wrong_inventory_covered": True,
        "real_world_source_anchors": manifest.get("real_world_source_anchors") or [],
        "records_detail": records,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Day0 baseline: units={output['selected_units']} records={output['records']} "
        f"incorrect={output['incorrect_records']} → {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
