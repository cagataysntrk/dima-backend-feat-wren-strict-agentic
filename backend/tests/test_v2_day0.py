"""Targeted Day 0 gates only — intentionally small and fast.

Full regression/corpus gates remain milestone/nightly responsibilities.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import yaml

from app.config import get_settings
from app.v2 import orchestrator
from app.v2.models import AskV2BootstrapRequest


def test_v2_hot_path_does_not_import_legacy_semantic_owners():
    from app.routers import ask_v2
    from app.v2 import models

    source = "\n".join(
        inspect.getsource(module)
        for module in (ask_v2, models, orchestrator)
    )
    forbidden = (
        "app.routers.ask",
        "cube_router",
        "uyum",
        "plan_tuketici",
        "plan_semasi",
        "followup",
        "generate_sql",
    )
    for token in forbidden:
        assert token not in source, f"V2 Day0 legacy semantic owner'a bağlandı: {token}"


def test_day0_orchestrator_cannot_execute_query_or_call_llm():
    source = inspect.getsource(orchestrator.V2BootstrapOrchestrator)
    for token in (".query(", ".dry_plan(", ".cube_sql(", ".generate_sql(", ".select_cube("):
        assert token not in source


def test_ask_v2_default_is_dark():
    assert get_settings().ask_v2_enabled is False


def test_day0_baseline_manifest_is_large_and_covers_known_silent_wrong_inventory():
    root = Path(__file__).resolve().parents[1]
    manifest = yaml.safe_load((root / "eval" / "v2_day0_cases.yaml").read_text(encoding="utf-8"))
    cases = yaml.safe_load((root / "eval" / "cases.yaml").read_text(encoding="utf-8"))

    existing = {case["id"] for case in cases}
    selected = set(manifest["eval_case_ids"])
    experience = set(manifest["experience_scenarios"])
    required = {
        case_id
        for group in manifest["known_silent_wrong_inventory"].values()
        for case_id in group
    }

    assert len(selected) + len(experience) >= manifest["minimum_units"] >= 30
    assert selected <= existing
    assert required <= selected
    assert manifest["real_world_source_anchors"]


def test_ask_v2_real_wren_bootstrap_and_rollback(client, monkeypatch):
    settings = get_settings()
    body = {"question": "day0 smoke", "session_id": "v2-day0"}

    monkeypatch.setattr(settings, "ask_v2_enabled", False)
    off = client.post("/ask-v2", json=body)
    assert off.status_code == 404

    monkeypatch.setattr(settings, "ask_v2_enabled", True)
    on = client.post("/ask-v2", json=body)
    assert on.status_code == 200, on.text

    data = on.json()
    assert data["status"] == "bootstrap_ready"
    assert data["stage"] == "day0_runtime_boundary"
    assert data["query_executed"] is False
    assert data["llm_called"] is False
    assert data["legacy_semantic_path_called"] is False
    assert data["runtime"]["principal_user_id"]
    assert data["runtime"]["tenant_slug"] == settings.company
    assert data["runtime"]["mdl_version"]
    assert data["next_stage"] == "turn_interpreter_day1"
