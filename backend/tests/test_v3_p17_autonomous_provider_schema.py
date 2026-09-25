from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from app.v3.research_manager import InvestigationIntent
from app.v3.research_manager_provider import (
    StructuredResearchProposalManager,
    _schema_for_intents,
)


AUTONOMOUS_INTENTS = (
    InvestigationIntent.INVESTIGATE_GAP,
    InvestigationIntent.EXPLORE_ALTERNATIVES,
    InvestigationIntent.SEEK_COUNTER_EVIDENCE,
    InvestigationIntent.DEEPEN_EXPLANATION,
    InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
    InvestigationIntent.REPLAN,
    InvestigationIntent.STOP_BRANCH,
    InvestigationIntent.STOP_INVESTIGATION,
)


def _assert_provider_strict_objects(node):
    if isinstance(node, dict):
        if node.get("type") == "object":
            assert node.get("additionalProperties") is False
        for child in node.values():
            _assert_provider_strict_objects(child)
    elif isinstance(node, list):
        for child in node:
            _assert_provider_strict_objects(child)


def test_autonomous_legal_vocabulary_prunes_unsupported_claim_payload_schema():
    schema = _schema_for_intents(AUTONOMOUS_INTENTS)

    props = schema["properties"]
    assert props["intent"]["enum"] == [x.value for x in AUTONOMOUS_INTENTS]
    assert "claim" not in props
    assert "ProposedClaimDraft" not in (schema.get("$defs") or {})
    assert "ClaimFreshness" not in (schema.get("$defs") or {})
    _assert_provider_strict_objects(schema)


def test_constraints_seam_supplies_no_guidance_or_trajectory_identity():
    transport = Mock()
    manager = StructuredResearchProposalManager(transport=transport)
    expected = object()
    manager._propose = Mock(return_value=expected)

    snapshot = object()
    result = manager.propose_with_constraints(
        snapshot,
        allowed_intents=AUTONOMOUS_INTENTS,
    )

    assert result is expected
    manager._propose.assert_called_once_with(
        snapshot,
        allowed_intents=AUTONOMOUS_INTENTS,
    )


def test_autonomous_canary_uses_constraint_seam_not_guided_screenplay():
    source = (
        Path(__file__).parents[1]
        / "lab"
        / "metabase"
        / "p17"
        / "autonomous_manager_canary.py"
    ).read_text(encoding="utf-8")

    assert "propose_with_constraints(" in source
    assert "allowed_intents=LEGAL_AUTONOMOUS_INTENTS" in source
    assert "propose_with_guidance(" not in source
    assert "self.provider.propose(snapshot)" not in source
