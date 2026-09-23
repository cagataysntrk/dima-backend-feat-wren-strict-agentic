from __future__ import annotations

from app.v3.entity_value_gate import (
    CurrentLensValueEvidence,
    EntityValueAdoptionGate,
    EntityValueDecision,
    EntityValueProposal,
)


LENS = "lens:p11"


def _evidence(scope: str, *values):
    return CurrentLensValueEvidence(
        semantic_ref=scope,
        values=values,
        access_lens_ref=LENS,
        freshness="CURRENT_USER_RETRIEVAL",
    )


def _bind(scope: str, value):
    return EntityValueProposal(
        decision="BIND",
        semantic_ref=scope,
        value=value,
    )


def test_p11_gate_allows_exact_bind_in_single_approved_scope():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.region", "North"),
        allowed_semantic_scopes=("dimension.region",),
        evidence=(_evidence("dimension.region", "North", "South"),),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BIND
    assert result.semantic_ref == "dimension.region"
    assert result.value == "North"
    assert result.reason_code == "EXACT_CURRENT_LENS_EVIDENCE"


def test_p11_gate_vetoes_model_bind_when_semantic_scope_is_unresolved():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.region", "North"),
        allowed_semantic_scopes=(
            "dimension.region",
            "dimension.customer_name",
        ),
        evidence=(
            _evidence("dimension.region", "North", "South"),
            _evidence("dimension.customer_name", "Acme North", "Bravo South"),
        ),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.CLARIFY
    assert result.semantic_ref is None
    assert result.value is None
    assert result.reason_code == "AMBIGUOUS_SEMANTIC_SCOPE"


def test_p11_gate_blocks_unapproved_scope_without_name_guessing():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.customer_name", "North"),
        allowed_semantic_scopes=("dimension.region",),
        evidence=(_evidence("dimension.region", "North"),),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BLOCKED
    assert result.reason_code == "UNAPPROVED_SEMANTIC_SCOPE"


def test_p11_gate_blocks_invented_or_similar_value_exactly():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.region", "north"),
        allowed_semantic_scopes=("dimension.region",),
        evidence=(_evidence("dimension.region", "North"),),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BLOCKED
    assert result.reason_code == "VALUE_NOT_IN_CURRENT_EVIDENCE"


def test_p11_gate_blocks_access_lens_mismatch():
    bad = CurrentLensValueEvidence(
        semantic_ref="dimension.region",
        values=("North",),
        access_lens_ref="lens:other",
        freshness="CURRENT_USER_RETRIEVAL",
    )
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.region", "North"),
        allowed_semantic_scopes=("dimension.region",),
        evidence=(bad,),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BLOCKED
    assert result.reason_code == "ACCESS_LENS_MISMATCH"


def test_p11_gate_preserves_safe_non_bind_cognition():
    for proposal, expected in (
        (
            EntityValueProposal(
                decision="CLARIFY",
                semantic_ref=None,
                value=None,
            ),
            EntityValueDecision.CLARIFY,
        ),
        (
            EntityValueProposal(
                decision="NO_MATCH",
                semantic_ref=None,
                value=None,
            ),
            EntityValueDecision.NO_MATCH,
        ),
    ):
        result = EntityValueAdoptionGate.adjudicate(
            proposal=proposal,
            allowed_semantic_scopes=("dimension.region",),
            evidence=(_evidence("dimension.region", "North"),),
            expected_access_lens_ref=LENS,
        )
        assert result.decision == expected



def test_p11_gate_blocks_bool_true_against_int_one():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.flag", True),
        allowed_semantic_scopes=("dimension.flag",),
        evidence=(_evidence("dimension.flag", 1),),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BLOCKED
    assert result.reason_code == "VALUE_NOT_IN_CURRENT_EVIDENCE"


def test_p11_gate_blocks_int_one_against_bool_true():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.count", 1),
        allowed_semantic_scopes=("dimension.count",),
        evidence=(_evidence("dimension.count", True),),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BLOCKED
    assert result.reason_code == "VALUE_NOT_IN_CURRENT_EVIDENCE"


def test_p11_gate_blocks_int_one_against_float_one():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.count", 1),
        allowed_semantic_scopes=("dimension.count",),
        evidence=(_evidence("dimension.count", 1.0),),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BLOCKED
    assert result.reason_code == "VALUE_NOT_IN_CURRENT_EVIDENCE"


def test_p11_gate_blocks_float_one_against_int_one():
    result = EntityValueAdoptionGate.adjudicate(
        proposal=_bind("dimension.ratio", 1.0),
        allowed_semantic_scopes=("dimension.ratio",),
        evidence=(_evidence("dimension.ratio", 1),),
        expected_access_lens_ref=LENS,
    )
    assert result.decision == EntityValueDecision.BLOCKED
    assert result.reason_code == "VALUE_NOT_IN_CURRENT_EVIDENCE"
