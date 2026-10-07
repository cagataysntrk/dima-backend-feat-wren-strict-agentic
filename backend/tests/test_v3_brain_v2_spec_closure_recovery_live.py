from lab.metabase.brain_v2.spec_closure_recovery_live import (
    _case_with_question_override,
    _case_with_turns_override,
    _raw_harness_gate,
    _recovery_terminal_accepted,
)


def test_recovery_answer_terminal_is_not_rejected_by_legacy_broad_label() -> None:
    assert _recovery_terminal_accepted(
        "ANSWER",
        ("REPORT", "PARTIAL"),
    )
    assert _recovery_terminal_accepted(
        "PARTIAL",
        ("REPORT",),
    )
    assert not _recovery_terminal_accepted(
        "UNSUPPORTED",
        ("REPORT", "PARTIAL"),
    )


def test_multimetric_single_evidence_is_not_failed_by_legacy_cardinality_proxy() -> None:
    assert _raw_harness_gate(
        mechanical_safety=True,
        accepted_terminal=True,
        requirement_complete=True,
        terminal_state="REPORT",
        evidence_count=1,
        legacy_min_evidence=2,
    )


def test_supported_report_requires_governed_requirement_completion() -> None:
    assert not _raw_harness_gate(
        mechanical_safety=True,
        accepted_terminal=True,
        requirement_complete=False,
        terminal_state="REPORT",
        evidence_count=3,
        legacy_min_evidence=2,
    )


def test_clarify_terminal_does_not_require_evidence_cardinality() -> None:
    assert _raw_harness_gate(
        mechanical_safety=True,
        accepted_terminal=True,
        requirement_complete=False,
        terminal_state="CLARIFY",
        evidence_count=0,
        legacy_min_evidence=2,
    )



def test_semantic_sibling_override_does_not_mutate_frozen_case() -> None:
    frozen = {
        "id": "F06_M",
        "question": "original governed obligation",
        "max_model_calls": 8,
    }
    sibling = _case_with_question_override(
        frozen,
        "alternate wording of the same governed obligation",
    )

    assert frozen["question"] == "original governed obligation"
    assert sibling["id"] == "F06_M"
    assert sibling["max_model_calls"] == 8
    assert sibling["question"] == (
        "alternate wording of the same governed obligation"
    )


def test_semantic_sibling_override_rejects_multiturn_rewrite() -> None:
    frozen = {
        "id": "F10_H",
        "question": "turn one",
        "turns": ["turn one", "turn two"],
    }

    try:
        _case_with_question_override(frozen, "alternate wording")
    except RuntimeError as exc:
        assert "one-turn" in str(exc)
    else:
        raise AssertionError("multi-turn sibling override must fail closed")


def test_multiturn_recovery_sibling_override_is_eval_only() -> None:
    frozen = {
        "id": "F10_S",
        "question": "turn one",
        "turns": ["turn one", "scope mutation"],
        "max_model_calls": 8,
    }
    sibling = _case_with_turns_override(
        frozen,
        (
            "turn one",
            "same scope report only; do not execute new analytics",
        ),
    )

    assert frozen["turns"] == ["turn one", "scope mutation"]
    assert sibling["id"] == "F10_S"
    assert sibling["max_model_calls"] == 8
    assert sibling["question"] == "turn one"
    assert sibling["turns"] == [
        "turn one",
        "same scope report only; do not execute new analytics",
    ]
