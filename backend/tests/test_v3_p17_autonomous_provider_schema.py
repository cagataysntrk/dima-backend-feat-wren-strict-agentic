from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

from app.v3.research_manager import InvestigationIntent
from app.v3.research_manager_provider import (
    ResearchManagerProposalDraft,
    StructuredResearchProposalManager,
    _draft_payload_from_transport,
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
            props = node.get("properties")
            if isinstance(props, dict):
                assert set(node.get("required") or ()) == set(props)
        for child in node.values():
            _assert_provider_strict_objects(child)
    elif isinstance(node, list):
        for child in node:
            _assert_provider_strict_objects(child)


def _variants(schema):
    proposal = schema["properties"]["proposal"]
    return proposal["anyOf"]


def _variant_by_intent(schema, intent: InvestigationIntent):
    for variant in _variants(schema):
        enum = variant["properties"]["intent"]["enum"]
        if intent.value in enum:
            return variant
    raise AssertionError(f"missing variant for {intent.value}")


def test_autonomous_mixed_vocabulary_uses_strict_semantic_envelope():
    schema = _schema_for_intents(AUTONOMOUS_INTENTS)

    assert set(schema["properties"]) == {"proposal"}
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["proposal"]
    assert len(_variants(schema)) == len(AUTONOMOUS_INTENTS)
    _assert_provider_strict_objects(schema)

    serialized = json.dumps(schema, sort_keys=True)
    assert "ProposedClaimDraft" not in serialized
    assert "ClaimFreshness" not in serialized


def test_regular_non_stop_variant_cannot_emit_null_information_gain():
    schema = _schema_for_intents(AUTONOMOUS_INTENTS)
    regular = _variant_by_intent(
        schema,
        InvestigationIntent.INVESTIGATE_GAP,
    )
    props = regular["properties"]

    assert props["bounded_objective"] == {"type": "string"}
    assert props["expected_information_gain"] == {"type": "string"}
    assert "stop_reason" not in props
    assert "counter_to_claim_id" not in props


def test_counter_evidence_variant_requires_counter_target_as_string():
    schema = _schema_for_intents(AUTONOMOUS_INTENTS)
    counter = _variant_by_intent(
        schema,
        InvestigationIntent.SEEK_COUNTER_EVIDENCE,
    )
    props = counter["properties"]

    assert props["intent"]["enum"] == ["SEEK_COUNTER_EVIDENCE"]
    assert props["counter_to_claim_id"] == {"type": "string"}
    assert props["bounded_objective"] == {"type": "string"}
    assert props["expected_information_gain"] == {"type": "string"}
    assert "stop_reason" not in props


def test_stop_variant_requires_stop_reason_without_non_stop_payload():
    schema = _schema_for_intents(AUTONOMOUS_INTENTS)
    stop = _variant_by_intent(
        schema,
        InvestigationIntent.STOP_INVESTIGATION,
    )
    props = stop["properties"]

    assert props["intent"]["enum"] == ["STOP_INVESTIGATION"]
    assert "stop_reason" in props
    assert "bounded_objective" not in props
    assert "expected_information_gain" not in props
    assert "counter_to_claim_id" not in props

    stop_reason = props["stop_reason"]
    assert not (
        stop_reason.get("type") == "null"
        or any(
            choice.get("type") == "null"
            for choice in stop_reason.get("anyOf", [])
            if isinstance(choice, dict)
        )
    )


def test_semantic_envelope_unwrap_preserves_runtime_pydantic_authority():
    schema = _schema_for_intents(AUTONOMOUS_INTENTS)
    raw = json.dumps(
        {
            "proposal": {
                "proposal_id": "p17-generic-001",
                "source_revision": 1,
                "target_parent_obligation": "g1",
                "intent": "INVESTIGATE_GAP",
                "parent_step_id": None,
                "branch_key": None,
                "target_kind": "GAP",
                "target_ref": None,
                "objective_key": "gap.generic",
                "bounded_objective": "Inspect the unresolved gap.",
                "rationale": "A bounded question can change investigation state.",
                "inspected_evidence_refs": [],
                "inspected_claim_refs": [],
                "inspected_material_refs": [],
                "expected_information_gain": "Distinguishes whether deeper work is useful.",
            }
        }
    )

    payload = _draft_payload_from_transport(raw, schema)
    draft = ResearchManagerProposalDraft.model_validate(payload)

    assert draft.intent == InvestigationIntent.INVESTIGATE_GAP
    assert draft.expected_information_gain


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


def test_transport_schema_code_contains_no_business_example_special_cases():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "v3"
        / "research_manager_provider.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "Boyahane",
        "Haziran 2026",
        "candidate-a",
        "candidate-b",
        'branch == "Web"',
    ):
        assert forbidden not in source
