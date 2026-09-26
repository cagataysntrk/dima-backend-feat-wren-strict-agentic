from __future__ import annotations

from pathlib import Path

from lab.metabase.core_b.p17_request_differential import (
    HISTORICAL_DIAGNOSTIC_REQUEST_REF,
    SENTINEL_REQUEST_REF,
    run_differential,
)


def test_historical_isolated_diagnostic_was_not_the_frozen_sentinel_request():
    result = run_differential()
    diff = result["historical_vs_frozen_sentinel"]

    assert HISTORICAL_DIAGNOSTIC_REQUEST_REF == "diagnostic:root_cause_tr"
    assert SENTINEL_REQUEST_REF == "sentinel:root_cause_tr"
    assert diff["authority_id_equal"] is False
    assert diff["session_id_equal"] is False
    assert diff["schema_fingerprint_equal"] is True
    assert diff["system_prompt_hash_equal"] is True
    assert diff["user_prompt_hash_equal"] is False
    assert diff["request_envelope_fingerprint_equal"] is False
    assert diff["state_action_profile_fingerprint_equal"] is False
    assert result["historical_first_divergence_owner"] == (
        "diagnostic_request_ref_namespace"
    )


def test_corrected_diagnostic_namespace_matches_pre_root_provider_envelope():
    result = run_differential()
    isolated = result["corrected_isolated"]
    pre_root = result["pre_root_topology"]

    assert result["classification"] == "IDENTICAL"
    assert result["provider_calls"] == 0
    assert result["full_sentinel_rerun"] is False
    assert (
        isolated["state_identity"]["state_action_profile_fingerprint"]
        == pre_root["state_identity"]["state_action_profile_fingerprint"]
    )

    for field in result["comparison_fields"]:
        assert isolated["trace"][field] == pre_root["trace"][field]

    assert isolated["trace"]["call_ordinal_by_role"] == 1
    assert pre_root["trace"]["call_ordinal_by_role"] == 8
    assert (
        isolated["trace"]["request_envelope_fingerprint"]
        == pre_root["trace"]["request_envelope_fingerprint"]
    )


def test_diagnostic_runner_uses_frozen_sentinel_request_ref_namespace():
    source = (
        Path(__file__).parents[1]
        / "lab"
        / "metabase"
        / "core_b"
        / "p17_provider_diagnostic.py"
    ).read_text(encoding="utf-8")

    assert 'request_ref=f"sentinel:{ROOT_CASE_ID}"' in source
    assert 'request_ref=f"diagnostic:{ROOT_CASE_ID}"' not in source
