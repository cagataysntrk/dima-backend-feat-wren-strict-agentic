"""Day 6.5 external holdout attestation contract tests."""

from __future__ import annotations

import json

import pytest

from lab.v2_day6_5_freeze_holdout import _load_attestation


def _write(tmp_path, payload):
    path = tmp_path / "attestation.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_valid_external_attestation_is_accepted(tmp_path):
    payload = {
        "status": "ATTESTED_EXTERNAL",
        "independent_evaluator": True,
        "development_model_generated": False,
        "prompt_text_committed": False,
        "prompt_text_shared_with_implementation": False,
        "development_corpus_seen": False,
        "development_failure_outputs_seen": False,
        "frozen_before_architecture_seal_run": True,
    }

    assert _load_attestation(_write(tmp_path, payload)) == payload


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("independent_evaluator", False),
        ("development_model_generated", True),
        ("prompt_text_committed", True),
        ("prompt_text_shared_with_implementation", True),
        ("development_corpus_seen", True),
        ("development_failure_outputs_seen", True),
        ("frozen_before_architecture_seal_run", False),
    ],
)
def test_invalid_external_attestation_is_rejected(tmp_path, field, bad_value):
    payload = {
        "status": "ATTESTED_EXTERNAL",
        "independent_evaluator": True,
        "development_model_generated": False,
        "prompt_text_committed": False,
        "prompt_text_shared_with_implementation": False,
        "development_corpus_seen": False,
        "development_failure_outputs_seen": False,
        "frozen_before_architecture_seal_run": True,
    }
    payload[field] = bad_value

    with pytest.raises(SystemExit):
        _load_attestation(_write(tmp_path, payload))


def test_attestation_status_must_be_external(tmp_path):
    payload = {
        "status": "SELF_ASSERTED",
        "independent_evaluator": True,
        "development_model_generated": False,
        "prompt_text_committed": False,
        "prompt_text_shared_with_implementation": False,
        "frozen_before_implementation": True,
    }

    with pytest.raises(SystemExit):
        _load_attestation(_write(tmp_path, payload))
