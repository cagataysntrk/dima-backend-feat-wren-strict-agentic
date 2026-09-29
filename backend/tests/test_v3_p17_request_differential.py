from __future__ import annotations

from pathlib import Path

import pytest

from lab.metabase.core_b.p17_provider_diagnostic import (
    _BoundedP17Transport,
    _DiagnosticBoundaryReached,
)
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



class _FakeInnerTransport:
    def __init__(self):
        self.call_count = 0
        self.trace_log = ()
        self.last_trace = None
        self.closed = False

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema, schema_name
        self.call_count += 1
        return '{"ok":true}'

    def close(self):
        self.closed = True


def test_live_diagnostic_bound_allows_two_semantic_turns_and_blocks_third_before_provider():
    inner = _FakeInnerTransport()
    bounded = _BoundedP17Transport(inner, max_provider_calls=2)

    assert bounded.structured_json("s","u",schema={},schema_name="x") == '{"ok":true}'
    assert bounded.structured_json("s","u",schema={},schema_name="x") == '{"ok":true}'
    assert bounded.call_count == 2

    with pytest.raises(_DiagnosticBoundaryReached):
        bounded.structured_json("s","u",schema={},schema_name="x")

    assert bounded.call_count == 2
    bounded.close()
    assert inner.closed is True
