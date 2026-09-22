from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

from app.v2.temporal_intent import TemporalBindingEngine, TemporalNormalizationChoice

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
LAB = ROOT / "lab"


def _load(name: str):
    return json.loads((EVAL / name).read_text(encoding="utf-8"))


def _git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def test_j1_freeze_manifest_matches_frozen_corpora():
    manifest = _load("v2_day6_5_j1_freeze_manifest.json")
    assert manifest["frozen_before_any_benchmark_result"] is True
    assert manifest["challengers"] == [
        "google/gemini-2.5-flash-lite",
        "typesafe/jev-1.13",
        "openai/gpt-5.6-luna",
    ]
    assert manifest["version"] == "d65-j1-freeze-v2"
    assert manifest["amendment"]["reason"] == "PRE_RESULT_CHALLENGER_ROLE_CORRECTION"
    assert manifest["amendment"]["corpus_changed"] is False
    assert manifest["model_roles"]["reference_ceiling"] == "openai/gpt-5.6-sol"
    assert manifest["model_roles"]["conditional_second_stage"] == "openai/gpt-5.6-terra"
    assert manifest["jev_transport"]["endpoint"] == "https://openrouter.ai/api/alpha/decisions"
    assert manifest["jev_transport"]["pinned_model"] == "typesafe/jev-1.13"
    assert manifest["jev_transport"]["generic_chat_or_structured_json_forbidden"] is True

    j1s_path = EVAL / "v2_day6_5_j1s_frozen.json"
    j1t_path = EVAL / "v2_day6_5_j1t_frozen.json"
    assert _git_blob_sha(j1s_path) == manifest["corpus_blob_shas"]["j1s"]
    assert _git_blob_sha(j1t_path) == manifest["corpus_blob_shas"]["j1t"]

    j1s = json.loads(j1s_path.read_text(encoding="utf-8"))
    j1t = json.loads(j1t_path.read_text(encoding="utf-8"))
    assert len(j1s["cases"]) == manifest["case_counts"]["j1s"] == 36
    assert len(j1t["cases"]) == manifest["case_counts"]["j1t"] == 34


def test_j1s_frozen_cases_are_bounded_and_self_consistent():
    doc = _load("v2_day6_5_j1s_frozen.json")
    ids = [case["id"] for case in doc["cases"]]
    assert len(ids) == len(set(ids))

    by_id = {case["id"]: case for case in doc["cases"]}
    manifest = _load("v2_day6_5_j1_freeze_manifest.json")
    for case in doc["cases"]:
        candidate_ids = [card["candidate_id"] for card in case["candidates"]]
        assert candidate_ids
        assert len(candidate_ids) == len(set(candidate_ids))
        assert all(cid.startswith("cand_") and len(cid) == 29 for cid in candidate_ids)
        assert case["expected"] == "ABSTAIN" or case["expected"] in candidate_ids
        assert all(
            set(card) == {
                "candidate_id",
                "target_kind",
                "label",
                "verified_aliases",
                "cube_labels",
            }
            for card in case["candidates"]
        )

    for case_id in manifest["repeated_run"]["j1s_ids"]:
        assert case_id in by_id

    for group_ids in manifest["metamorphic_groups"]["j1s"].values():
        expected = {by_id[case_id]["expected"] for case_id in group_ids}
        assert len(expected) == 1


def _choice_from_option(case: dict, option: dict) -> TemporalNormalizationChoice:
    if option["option_id"] == "ABSTAIN":
        return TemporalNormalizationChoice(
            request_id=case["id"],
            target=case["target"],
            decision="ABSTAIN",
            reason=case["abstain_reason"] or "INSUFFICIENT_CONTEXT",
        )
    return TemporalNormalizationChoice(
        request_id=case["id"],
        target=option["target"],
        decision="NORMALIZED",
        period_kind=option.get("period_kind"),
        comparison_kind=option.get("comparison_kind"),
        n=option.get("n"),
        implicit_base_period_kind=option.get("implicit_base_period_kind"),
        implicit_base_n=option.get("implicit_base_n"),
    )


def test_j1t_frozen_options_fit_current_closed_temporal_contract():
    doc = _load("v2_day6_5_j1t_frozen.json")
    ids = [case["id"] for case in doc["cases"]]
    assert len(ids) == len(set(ids))
    by_id = {case["id"]: case for case in doc["cases"]}
    manifest = _load("v2_day6_5_j1_freeze_manifest.json")

    for case in doc["cases"]:
        option_ids = [option["option_id"] for option in case["options"]]
        assert len(option_ids) == len(set(option_ids))
        assert "ABSTAIN" in option_ids
        assert case["expected"] in option_ids
        for option in case["options"]:
            choice = _choice_from_option(case, option)
            if option["option_id"] == "ABSTAIN":
                continue
            if option["target"] == "PERIOD":
                resolved = TemporalBindingEngine.period(
                    choice=choice,
                    source_text=case["surface"],
                    time_dimension="event_date",
                    today=date(2026, 9, 22),
                )
                assert resolved.start
            elif option.get("implicit_base_period_kind"):
                base = TemporalBindingEngine.implicit_base_period(
                    choice=choice,
                    source_text=case["surface"],
                    time_dimension="event_date",
                    today=date(2026, 9, 22),
                )
                resolved = TemporalBindingEngine.comparison(
                    choice=choice,
                    source_text=case["surface"],
                    time_dimension="event_date",
                    base_period=base,
                    today=date(2026, 9, 22),
                )
                assert resolved.reference_period.start

    for case_id in manifest["repeated_run"]["j1t_ids"]:
        assert case_id in by_id

    for group_ids in manifest["metamorphic_groups"]["j1t"].values():
        expected = {by_id[case_id]["expected"] for case_id in group_ids}
        assert len(expected) == 1


def test_j1_harness_transport_isolation_and_failure_semantics():
    path = LAB / "v2_day6_5_j1_benchmark.py"
    spec = importlib.util.spec_from_file_location("dima_j1_harness", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    assert module.PRIMARY_MODELS == (
        "google/gemini-2.5-flash-lite",
        "typesafe/jev-1.13",
        "openai/gpt-5.6-luna",
    )
    assert module.JEV_MODEL == "typesafe/jev-1.13"
    assert module.REFERENCE_MODEL == "openai/gpt-5.6-sol"
    assert module.CONDITIONAL_MODEL == "openai/gpt-5.6-terra"
    assert module._reasoning_policy("google/gemini-2.5-flash-lite") == "BOUNDED_DECISION_REASONING_DISABLED"
    assert module._reasoning_policy("openai/gpt-5.6-luna") == "BOUNDED_DECISION_REASONING_DISABLED"
    assert module._reasoning_policy("openai/gpt-5.6-sol") == "REFERENCE_CEILING_REASONING_ENABLED"
    assert module.DECISIONS_URL == "https://openrouter.ai/api/alpha/decisions"
    assert module.CHAT_URL == "https://openrouter.ai/api/v1/chat/completions"
    assert "~typesafe/jev-latest" not in path.read_text(encoding="utf-8")
    assert "TRANSPORT/PROVIDER" in path.read_text(encoding="utf-8")


def test_j1s_scoring_separates_product_bypass_from_model_needed():
    path = LAB / "v2_day6_5_j1_benchmark.py"
    spec = importlib.util.spec_from_file_location("dima_j1_routing", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    doc = _load("v2_day6_5_j1s_frozen.json")
    by_id = {case["id"]: case for case in doc["cases"]}
    assert module._j1s_route_bucket(by_id["j1s-001"]) == "DETERMINISTIC_BYPASS"
    assert module._j1s_route_bucket(by_id["j1s-006"]) == "MODEL_NEEDED"
    assert module._j1s_route_bucket(by_id["j1s-023"]) == "RETRIEVAL_MISS"
    assert module._j1s_route_bucket(by_id["j1s-025"]) == "SENSITIVE_EXACT_ONLY"


def test_jev_temporal_contract_fidelity_fails_closed_without_answer_enumeration():
    path = LAB / "v2_day6_5_j1_benchmark.py"
    spec = importlib.util.spec_from_file_location("dima_j1_fidelity", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    evidence = module._jev_temporal_contract_capability()
    assert evidence["status"] == "TEMPORAL_INTEGRATION_LIMITATION"
    assert evidence["native_primitives"] == ["choice", "noul", "score"]
    assert evidence["field_support"]["n"] == "NOT_DYNAMICALLY_REPRESENTABLE"
    assert evidence["field_support"]["implicit_base_n"] == "NOT_DYNAMICALLY_REPRESENTABLE"
    assert evidence["case_answer_pre_enumeration_required_for_n"] is True
    assert evidence["temporal_production_candidate"] is False
