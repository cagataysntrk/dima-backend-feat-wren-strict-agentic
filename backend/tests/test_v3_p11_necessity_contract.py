from __future__ import annotations

import json
from pathlib import Path

from lab.metabase.p11.run_eval import canonical_hash, normalized_decision, accepted, silent_wrong


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "lab" / "metabase" / "p11" / "corpus_v1.json"


def _corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_p11_v1_freeze_has_exactly_four_runnable_and_three_blocked_cases():
    corpus = _corpus()
    runnable = [c["id"] for c in corpus["cases"] if c["state"] == "RUNNABLE"]
    blocked = {c["id"]: c["blocker"] for c in corpus["cases"] if c["state"] == "BLOCKED"}
    assert runnable == ["EV-01", "EV-02", "EV-03", "EV-04"]
    assert blocked == {
        "EV-05": "FIXTURE_EXTENSION_REQUIRED",
        "EV-06": "STALE_INDEX_FIXTURE_REQUIRED",
        "EV-07": "P10B2_SECURITY_LENS_REQUIRED",
    }


def test_p11_model_profiles_are_exact_and_prompt_contract_is_identical():
    corpus = _corpus()
    assert corpus["model_policy"]["luna"]["requested_model"] == "openai/gpt-5.6-luna"
    assert corpus["model_policy"]["sol"]["requested_model"] == "openai/gpt-5.6-sol"
    assert corpus["model_policy"]["prompt_variant"] == "identical_for_luna_and_sol"
    assert corpus["model_policy"]["reasoning_config"] == "provider_default"


def test_p11_logical_tool_contract_never_exposes_physical_field_ids_to_model():
    corpus = _corpus()
    contract = corpus["retrieval_contract"]
    assert contract["logical_tool"] == "lookup_dimension_values"
    assert contract["model_receives_physical_field_ids"] is False
    for spec in corpus["semantic_context"]["scopes"].values():
        assert set(spec["locator"]) == {"database", "schema", "table", "field"}


def test_p11_fingerprint_is_deterministic_and_covers_truth_contract():
    corpus = _corpus()
    first = canonical_hash(corpus)
    second = canonical_hash(json.loads(json.dumps(corpus)))
    assert first == second
    changed = json.loads(json.dumps(corpus))
    changed["cases"][0]["oracle"]["accepted"][0]["value"] = "South"
    assert canonical_hash(changed) != first


def test_p11_oracle_flags_wrong_bind_as_silent_wrong():
    corpus = _corpus()
    ev4 = next(c for c in corpus["cases"] if c["id"] == "EV-04")
    wrong = {
        "decision": "BIND",
        "semantic_ref": "dimension.region",
        "value": "Central",
    }
    assert accepted(ev4, wrong) is False
    assert silent_wrong(ev4, wrong) is True
    assert normalized_decision(wrong) == wrong


def test_p11_ambiguity_and_no_match_oracles_are_conservative():
    corpus = _corpus()
    ev3 = next(c for c in corpus["cases"] if c["id"] == "EV-03")
    ev4 = next(c for c in corpus["cases"] if c["id"] == "EV-04")
    assert accepted(ev3, {"decision": "CLARIFY", "semantic_ref": None, "value": None})
    assert accepted(ev4, {"decision": "NO_MATCH", "semantic_ref": None, "value": None})
    assert accepted(ev4, {"decision": "CLARIFY", "semantic_ref": None, "value": None})
