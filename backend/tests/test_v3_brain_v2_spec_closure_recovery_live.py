from lab.metabase.brain_v2.spec_closure_recovery_live import _raw_harness_gate


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
