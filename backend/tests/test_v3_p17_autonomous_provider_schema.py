from __future__ import annotations

import json

import pytest
from pathlib import Path
from unittest.mock import Mock

from app.v3.research_manager import (
    InvestigationGraph,
    InvestigationIntent,
    InvestigationNodeView,
    InvestigationTargetKind,
    MaterialCognitionView,
    ReasoningStepStatus,
    _build_action_profile,
)
from app.v3.research_manager_provider import (
    ResearchManagerProposalDraft,
    StructuredResearchProposalManager,
    _ACTION_FOR_INTENT,
    _draft_payload_from_transport,
    _schema_for_intents,
)


# Runtime source-of-truth: provider-free coverage must never drift from the
# actually reachable live vocabulary.
AUTONOMOUS_INTENTS = tuple(_ACTION_FOR_INTENT)

HISTORICAL_REJECTED_TURN2_SCHEMA_FP = (
    "80533318ccc154c2e183e66099bb1f42d4a055413a2fffec7939ee172cda9b11"
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
    assert "ProviderClaimDraft" in serialized
    assert "ClaimFreshness" in serialized
    assert '"additionalProperties": true' not in serialized


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



def _closed_value(kind, *, string=None, integer=None, number=None, boolean=None, entries=(), items=()):
    return {
        "kind": kind,
        "string_value": string,
        "integer_value": integer,
        "number_value": number,
        "boolean_value": boolean,
        "object_entries": list(entries),
        "array_items": list(items),
    }


def _closed_entry(key, value):
    return {"key": key, "value": value}


def test_runtime_reachable_provider_vocabulary_includes_form_claim():
    assert InvestigationIntent.FORM_CLAIM in AUTONOMOUS_INTENTS
    assert set(AUTONOMOUS_INTENTS) == set(_ACTION_FOR_INTENT)


@pytest.mark.parametrize("intent", AUTONOMOUS_INTENTS)
def test_every_runtime_reachable_intent_has_recursively_closed_provider_schema(intent):
    schema = _schema_for_intents((intent,))
    _assert_provider_strict_objects(schema)
    serialized = json.dumps(schema, sort_keys=True)
    assert '"additionalProperties": true' not in serialized


def test_form_claim_provider_transport_is_closed_and_maps_to_domain_claim():
    schema = _schema_for_intents((InvestigationIntent.FORM_CLAIM,))
    _assert_provider_strict_objects(schema)

    claim_variant = schema["properties"]
    claim_schema = claim_variant["claim"]
    serialized = json.dumps(claim_schema, sort_keys=True)
    assert "ProviderClaimDraft" in serialized or "$ref" in claim_schema
    assert '"additionalProperties": true' not in serialized

    raw = {
        "proposal_id": "p17-form-claim-transport-001",
        "source_revision": 2,
        "target_parent_obligation": "g1",
        "intent": "FORM_CLAIM",
        "parent_step_id": "rrs_" + "a" * 24,
        "branch_key": None,
        "target_kind": "CLAIM",
        "target_ref": None,
        "objective_key": "claim.form.machine-downtime",
        "bounded_objective": "Form one bounded claim from governed material.",
        "rationale": "Governed material can now support a claim-shaped proposition.",
        "inspected_evidence_refs": [],
        "inspected_claim_refs": [],
        "inspected_material_refs": ["lead_1"],
        "expected_information_gain": "Makes the proposition explicit for later Evidence linkage.",
        "claim": {
            "claim_text": "Department A has 41 downtime events in the governed scope.",
            "proposition": {
                "entries": [
                    _closed_entry(
                        "subject",
                        _closed_value("STRING", string="department:A"),
                    ),
                    _closed_entry(
                        "predicate",
                        _closed_value("STRING", string="has_downtime_events"),
                    ),
                    _closed_entry(
                        "object",
                        _closed_value("INTEGER", integer=41),
                    ),
                    _closed_entry(
                        "context",
                        _closed_value(
                            "OBJECT",
                            entries=(
                                _closed_entry(
                                    "basis",
                                    _closed_value("STRING", string="governed-material"),
                                ),
                            ),
                        ),
                    ),
                ]
            },
            "scope": {
                "entries": [
                    _closed_entry(
                        "period",
                        _closed_value("STRING", string="fixture-period"),
                    ),
                    _closed_entry(
                        "population",
                        _closed_value("STRING", string="machine_operations"),
                    ),
                ]
            },
            "freshness": {
                "as_of": "2026-09-26T00:00:00Z",
                "stale_after": None,
            },
            "origin_material_refs": ["lead_1"],
            "limitations": [],
        },
    }

    draft = ResearchManagerProposalDraft.model_validate(raw)
    proposal = StructuredResearchProposalManager._proposal(draft)

    assert proposal.intent == InvestigationIntent.FORM_CLAIM
    assert proposal.claim is not None
    assert proposal.claim.proposition == {
        "subject": "department:A",
        "predicate": "has_downtime_events",
        "object": 41,
        "context": {"basis": "governed-material"},
    }
    assert proposal.claim.scope == {
        "period": "fixture-period",
        "population": "machine_operations",
    }


def test_turn2_material_state_reproduces_form_claim_capable_profile_provider_free():
    root = InvestigationNodeView(
        step_id="rrs_" + "b" * 24,
        parent_step_id=None,
        root_obligation_id="g1",
        depth=0,
        branch_id="branch:g1",
        intent=InvestigationIntent.INVESTIGATE_GAP,
        target_kind=InvestigationTargetKind.GAP,
        target_ref=None,
        objective_key="gap.machine-downtime",
        bounded_objective="Investigate the first governed downtime gap.",
        status=ReasoningStepStatus.COMPLETED,
        evidence_refs=(),
        counter_evidence_refs=(),
        native_material_refs=("lead_turn1",),
        child_step_ids=(),
        stop_reason=None,
        stop_scope=None,
    )
    graph = InvestigationGraph(
        nodes=(root,),
        root_step_ids=(root.step_id,),
        open_branch_ids=(root.branch_id,),
        stopped_branch_ids=(),
        max_observed_depth=0,
    )
    material = MaterialCognitionView(
        lead_id="lead_turn1",
        obligation_id="g1",
        execution_link_id="rex_turn1",
        native_conversation_id="conv_turn1",
        native_query_id="query_turn1",
        query_fingerprint="1" * 64,
        material_fingerprint="2" * 64,
        source_evidence_refs=(),
        exploration_kind="FOLLOWUP",
    )
    profile = _build_action_profile(
        graph=graph,
        claims=(),
        materials=(material,),
        remaining_followup_native_turns=3,
        remaining_counter_evidence_attempts=2,
        max_depth=5,
    )

    assert profile.legal_intents == (
        InvestigationIntent.INVESTIGATE_GAP,
        InvestigationIntent.EXPLORE_ALTERNATIVES,
        InvestigationIntent.DEEPEN_EXPLANATION,
        InvestigationIntent.REPLAN,
        InvestigationIntent.FORM_CLAIM,
        InvestigationIntent.STOP_BRANCH,
        InvestigationIntent.STOP_INVESTIGATION,
    )

    schema = _schema_for_intents(profile.legal_intents)
    _assert_provider_strict_objects(schema)
    claim_variant = _variant_by_intent(schema, InvestigationIntent.FORM_CLAIM)
    assert "claim" in claim_variant["properties"]
    assert '"additionalProperties": true' not in json.dumps(
        claim_variant,
        sort_keys=True,
    )

    # The old live turn-2 fingerprint is preserved as historical failure
    # identity. The corrected closed representation intentionally changes it.
    assert len(HISTORICAL_REJECTED_TURN2_SCHEMA_FP) == 64
