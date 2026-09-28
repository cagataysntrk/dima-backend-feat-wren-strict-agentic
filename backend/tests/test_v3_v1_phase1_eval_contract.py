from __future__ import annotations

import json
from pathlib import Path


ROUND2 = Path("eval/dima_neutral_feature_benchmark_round2.json")
FIXTURE = Path("eval/round2_neutral_machine_fixture.json")
METAMORPHIC = Path("eval/v1/phase1_metamorphic_manifest.json")


def test_round2_frozen_manifest_is_exact_shape_and_eval_only_data():
    manifest = json.loads(ROUND2.read_text(encoding="utf-8"))
    assert manifest["version"] == "dima-neutral-feature-benchmark-round2-v2"
    assert manifest["case_count"] == 30
    assert manifest["common_feature_count"] == 10
    assert manifest["same_prompt_required"] is True
    assert manifest["same_fixture_required"] is True
    cases = manifest["cases"]
    assert len(cases) == 30
    assert len({item["id"] for item in cases}) == 30
    assert {
        (item["feature_id"], item["difficulty"])
        for item in cases
    } == {
        (f"F{feature:02d}", difficulty)
        for feature in range(1, 11)
        for difficulty in ("simple", "medium", "hard")
    }
    serialized = json.dumps(manifest, ensure_ascii=False).lower()
    for forbidden_key in (
        '"sql"',
        '"mbql"',
        '"dataset_query"',
        '"join_plan"',
        '"query_plan"',
    ):
        assert forbidden_key not in serialized


def test_round2_neutral_fixture_is_frozen_substrate_neutral_40_rows():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["schema_version"] == "round2_neutral_machine_fixture_v1"
    assert len(fixture["rows"]) == 40
    serialized = json.dumps(fixture, ensure_ascii=False).lower()
    assert "wren_mdl" not in serialized
    assert "expected_sql" not in serialized
    assert "mbql" not in serialized
    assert {row[1] for row in fixture["rows"]} == {
        "Assembly",
        "Packaging",
        "Utilities",
        "Maintenance",
        "Quality",
    }


def test_phase1_metamorphic_manifest_is_structural_not_prose_scoring():
    manifest = json.loads(METAMORPHIC.read_text(encoding="utf-8"))
    assert manifest["authority"] == "EVAL_ONLY"
    assert len(manifest["cases"]) == 12
    text = json.dumps(manifest, ensure_ascii=False).lower()
    for forbidden in (
        "winner",
        "score threshold",
        "exact answer prose",
        "prompt-specific patch",
        "sql planner",
        "mbql planner",
    ):
        assert forbidden not in text
