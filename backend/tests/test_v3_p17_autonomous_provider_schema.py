from __future__ import annotations

import json

import pytest
from pathlib import Path
from unittest.mock import Mock

from app.v3.research_manager import (
    ClaimView,
    InvestigationGraph,
    InvestigationIntent,
    InvestigationNodeView,
    InvestigationTargetKind,
    ManagerAction,
    ManagerStopReason,
    MaterialCognitionView,
    ParentObligationView,
    ReasoningStepStatus,
    ResearchManagerSnapshot,
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

    freshness_schema = schema["$defs"]["ClaimFreshness"]["properties"]
    assert freshness_schema["as_of"] == {
        "format": "date-time",
        "type": "string",
    }
    stale_after = freshness_schema["stale_after"]["anyOf"]
    assert {
        "format": "date-time",
        "type": "string",
    } in stale_after

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
    assert "mechanism_semantic_ref" in claim_variant["properties"]
    assert '"additionalProperties": true' not in json.dumps(
        claim_variant,
        sort_keys=True,
    )

    # The old live turn-2 fingerprint is preserved as historical failure
    # identity. The corrected closed representation intentionally changes it.
    assert len(HISTORICAL_REJECTED_TURN2_SCHEMA_FP) == 64



class _CaptureTransport:
    def __init__(self):
        self.schema = None
        self.user = None

    def structured_json(self, system, user, *, schema, schema_name):
        del system, schema_name
        self.schema = schema
        self.user = user
        raise RuntimeError("captured-before-provider-call")


def _scoped_snapshot():
    source = InvestigationNodeView(
        step_id="rrs_" + "1" * 24,
        parent_step_id=None,
        root_obligation_id="g_source",
        depth=0,
        branch_id="branch:g_source",
        intent=InvestigationIntent.INVESTIGATE_GAP,
        target_kind=InvestigationTargetKind.GAP,
        target_ref=None,
        objective_key="gap.source",
        bounded_objective="Inspect source.",
        status=ReasoningStepStatus.COMPLETED,
        evidence_refs=("evi_source",),
        counter_evidence_refs=(),
        native_material_refs=("lead_source",),
        child_step_ids=(),
        stop_reason=None,
        stop_scope=None,
    )
    other = InvestigationNodeView(
        step_id="rrs_" + "2" * 24,
        parent_step_id=None,
        root_obligation_id="g_other",
        depth=0,
        branch_id="branch:g_other",
        intent=InvestigationIntent.INVESTIGATE_GAP,
        target_kind=InvestigationTargetKind.GAP,
        target_ref=None,
        objective_key="gap.other",
        bounded_objective="Inspect other.",
        status=ReasoningStepStatus.COMPLETED,
        evidence_refs=("evi_other",),
        counter_evidence_refs=(),
        native_material_refs=("lead_other",),
        child_step_ids=(),
        stop_reason=None,
        stop_scope=None,
    )
    graph = InvestigationGraph(
        nodes=(source, other),
        root_step_ids=(source.step_id, other.step_id),
        open_branch_ids=(source.branch_id, other.branch_id),
        stopped_branch_ids=(),
        max_observed_depth=0,
    )
    materials = (
        MaterialCognitionView(
            lead_id="lead_source",
            obligation_id="g_source",
            execution_link_id="rex_source",
            native_conversation_id="conv_source",
            native_query_id="query_source",
            query_fingerprint="1" * 64,
            material_fingerprint="2" * 64,
            source_evidence_refs=("evi_source",),
            exploration_kind="FOLLOWUP",
        ),
        MaterialCognitionView(
            lead_id="lead_other",
            obligation_id="g_other",
            execution_link_id="rex_other",
            native_conversation_id="conv_other",
            native_query_id="query_other",
            query_fingerprint="3" * 64,
            material_fingerprint="4" * 64,
            source_evidence_refs=("evi_other",),
            exploration_kind="FOLLOWUP",
        ),
    )
    claims = (
        ClaimView(
            claim_id="clm_" + "a" * 24,
            obligation_id="g_source",
            claim_text="Source claim.",
            proposition={"subject": "source"},
            scope={"scope": "source"},
            epistemic_state="SUPPORTED",
            origin_material_refs=("lead_source",),
        ),
        ClaimView(
            claim_id="clm_" + "b" * 24,
            obligation_id="g_other",
            claim_text="Other claim.",
            proposition={"subject": "other"},
            scope={"scope": "other"},
            epistemic_state="SUPPORTED",
            origin_material_refs=("lead_other",),
        ),
    )
    profile = _build_action_profile(
        graph=graph,
        claims=claims,
        materials=materials,
        remaining_followup_native_turns=3,
        remaining_counter_evidence_attempts=2,
        max_depth=5,
    )
    return ResearchManagerSnapshot(
        research_session_id="rs_" + "c" * 24,
        research_authority_id="authority-source",
        source_revision=3,
        objective="Scoped investigation.",
        parent_obligations=(
            ParentObligationView(
                obligation_id="g_source",
                objective="Source objective.",
                state="VERIFIED",
            ),
            ParentObligationView(
                obligation_id="g_other",
                objective="Other objective.",
                state="VERIFIED",
            ),
        ),
        evidence_refs=("evi_source", "evi_other"),
        material_refs=("lead_source", "lead_other"),
        materials=materials,
        action_profile=profile,
        claims=claims,
        investigation=graph,
        limitation_refs=(),
        completed_reasoning_steps=(source.step_id, other.step_id),
        pending_reasoning_steps=(),
        remaining_reasoning_steps=4,
        remaining_followup_native_turns=3,
        remaining_counter_evidence_attempts=2,
        terminal_stop_reason=None,
    )


def test_obligation_scoped_provider_view_exposes_no_cross_obligation_refs():
    transport = _CaptureTransport()
    manager = StructuredResearchProposalManager(transport=transport)
    snapshot = _scoped_snapshot()

    with pytest.raises(RuntimeError, match="captured-before-provider-call"):
        manager.propose_for_obligation(
            snapshot,
            target_parent_obligation="g_source",
            allowed_evidence_refs=("evi_source",),
        )

    assert transport.schema is not None
    assert transport.user is not None
    provider_view = json.loads(
        transport.user.split("GOVERNED SNAPSHOT JSON:\n", 1)[1]
    )
    assert {
        item["obligation_id"]
        for item in provider_view["parent_obligations"]
    } == {"g_source"}
    assert provider_view["evidence_refs"] == ["evi_source"]
    assert {item["claim_id"] for item in provider_view["claims"]} == {
        "clm_" + "a" * 24
    }
    assert {item["lead_id"] for item in provider_view["materials"]} == {
        "lead_source"
    }
    assert {
        item["root_obligation_id"]
        for item in provider_view["investigation"]["nodes"]
    } == {"g_source"}

    serialized_schema = json.dumps(transport.schema, sort_keys=True)
    serialized_view = json.dumps(provider_view, sort_keys=True)
    for forbidden in (
        "g_other",
        "evi_other",
        "clm_" + "b" * 24,
        "lead_other",
    ):
        assert forbidden not in serialized_schema
        assert forbidden not in serialized_view

    forbidden_outputs = {
        "proposal_id",
        "source_revision",
        "target_parent_obligation",
        "parent_step_id",
        "branch_key",
        "objective_key",
        "task_id",
        "scope_version",
        "hypothesis_id",
    }
    for variant in _variants(transport.schema):
        props = variant["properties"]
        assert not forbidden_outputs.intersection(props)
        assert props["target_objective"]["enum"] == ["Source objective."]
        assert props["inspected_evidence_refs"]["items"]["enum"] == [
            "evi_source"
        ]
        assert props["inspected_claim_refs"]["items"]["enum"] == [
            "clm_" + "a" * 24
        ]
        assert props["inspected_material_refs"]["items"]["enum"] == [
            "lead_source"
        ]


def test_root_candidate_provider_exposes_closed_governed_mechanism_refs_only():
    transport = _CaptureTransport()
    manager = StructuredResearchProposalManager(transport=transport)
    snapshot = _scoped_snapshot()

    with pytest.raises(RuntimeError, match="captured-before-provider-call"):
        manager.propose_root_candidate_for_obligation(
            snapshot,
            target_parent_obligation="g_source",
            allowed_evidence_refs=("evi_source",),
            allowed_mechanism_refs=(
                "metric.maintenance_delay_hours",
                "metric.spare_part_delay_hours",
            ),
        )

    claim_variant = _variant_by_intent(
        transport.schema,
        InvestigationIntent.FORM_CLAIM,
    )
    assert claim_variant["properties"]["mechanism_semantic_ref"] == {
        "type": "string",
        "enum": [
            "metric.maintenance_delay_hours",
            "metric.spare_part_delay_hours",
        ],
    }


def test_root_candidate_without_governed_mechanism_cannot_expose_form_claim():
    transport = _CaptureTransport()
    manager = StructuredResearchProposalManager(transport=transport)
    snapshot = _scoped_snapshot()

    with pytest.raises(RuntimeError, match="captured-before-provider-call"):
        manager.propose_root_candidate_for_obligation(
            snapshot,
            target_parent_obligation="g_source",
            allowed_evidence_refs=("evi_source",),
            allowed_mechanism_refs=(),
        )

    intents = {
        value
        for variant in _variants(transport.schema)
        for value in variant["properties"]["intent"]["enum"]
    }
    assert InvestigationIntent.FORM_CLAIM.value not in intents


class _SequenceTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.users = []
        self.schemas = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, schema_name
        self.users.append(user)
        self.schemas.append(schema)
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


def _semantic_response(*, objective="Source objective."):
    return json.dumps(
        {
            "proposal": {
                "target_objective": objective,
                "intent": "DEEPEN_EXPLANATION",
                "branch_concept": None,
                "target_kind": "EXPLANATION",
                "target_concept": "governed source mechanism",
                "rationale": "The current material leaves one bounded explanation gap.",
                "inspected_evidence_refs": ["evi_source"],
                "inspected_claim_refs": ["clm_" + "a" * 24],
                "inspected_material_refs": ["lead_source"],
                "bounded_objective": "Deepen the governed source explanation.",
                "expected_information_gain": "Distinguishes whether the explanation remains material.",
            }
        }
    )


def test_scoped_constraint_seam_can_expose_only_form_claim_for_verified_relationship_handoff():
    transport = _CaptureTransport()
    manager = StructuredResearchProposalManager(transport=transport)
    snapshot = _scoped_snapshot()

    with pytest.raises(RuntimeError, match="captured-before-provider-call"):
        manager.propose_for_obligation_with_constraints(
            snapshot,
            target_parent_obligation="g_source",
            allowed_evidence_refs=("evi_source",),
            allowed_intents=(InvestigationIntent.FORM_CLAIM,),
        )

    assert transport.schema is not None
    if "proposal" in transport.schema.get("properties", {}):
        intents = {
            value
            for variant in _variants(transport.schema)
            for value in variant["properties"]["intent"]["enum"]
        }
    else:
        intents = set(
            transport.schema["properties"]["intent"]["enum"]
        )
    assert intents == {InvestigationIntent.FORM_CLAIM.value}
    provider_view = json.loads(
        transport.user.split("GOVERNED SNAPSHOT JSON:\n", 1)[1]
    )
    assert provider_view["evidence_refs"] == ["evi_source"]
    assert {
        item["obligation_id"]
        for item in provider_view["parent_obligations"]
    } == {"g_source"}


def test_v1_provider_binds_machine_identities_deterministically():
    snapshot = _scoped_snapshot()
    transport = _SequenceTransport([_semantic_response()])
    manager = StructuredResearchProposalManager(transport=transport)

    proposal = manager.propose_for_obligation(
        snapshot,
        target_parent_obligation="g_source",
        allowed_evidence_refs=("evi_source",),
    )

    source_step = "rrs_" + "1" * 24
    assert proposal.source_revision == snapshot.source_revision
    assert proposal.target_parent_obligation == "g_source"
    assert proposal.parent_step_id == source_step
    assert proposal.branch_key is None
    assert proposal.proposal_id.startswith("p17-sem-")
    assert proposal.objective_key.startswith("v1.deepen_explanation.")
    assert manager.call_count == 1

    props = _variant_by_intent(
        transport.schemas[0],
        InvestigationIntent.DEEPEN_EXPLANATION,
    )["properties"]
    for forbidden in (
        "proposal_id",
        "source_revision",
        "target_parent_obligation",
        "parent_step_id",
        "branch_key",
        "objective_key",
        "task_id",
        "scope_version",
        "hypothesis_id",
    ):
        assert forbidden not in props


def test_v1_provider_gets_exactly_one_generic_contract_repair():
    snapshot = _scoped_snapshot()
    transport = _SequenceTransport(["{}", _semantic_response()])
    manager = StructuredResearchProposalManager(transport=transport)

    proposal = manager.propose_for_obligation(
        snapshot,
        target_parent_obligation="g_source",
        allowed_evidence_refs=("evi_source",),
    )

    assert proposal.intent == InvestigationIntent.DEEPEN_EXPLANATION
    assert manager.call_count == 2
    assert len(transport.users) == 2
    assert "PROVIDER-CONTRACT REPAIR" not in transport.users[0]
    assert "PROVIDER-CONTRACT REPAIR" in transport.users[1]


def test_v1_provider_exhausted_contract_repair_is_governed_inconclusive():
    snapshot = _scoped_snapshot()
    transport = _SequenceTransport(["{}", "{}"])
    manager = StructuredResearchProposalManager(transport=transport)

    proposal = manager.propose_for_obligation(
        snapshot,
        target_parent_obligation="g_source",
        allowed_evidence_refs=("evi_source",),
    )

    assert proposal.action == ManagerAction.STOP
    assert proposal.intent == InvestigationIntent.STOP_INVESTIGATION
    assert proposal.stop_reason == ManagerStopReason.INCONCLUSIVE
    assert proposal.target_parent_obligation == "g_source"
    assert manager.call_count == 2


def test_v1_internal_parent_resolution_defect_is_not_provider_repaired(monkeypatch):
    snapshot = _scoped_snapshot()
    transport = _SequenceTransport([_semantic_response(), _semantic_response()])
    manager = StructuredResearchProposalManager(transport=transport)

    def broken_parent(*args, **kwargs):
        raise ValueError("deterministic parent resolution defect")

    monkeypatch.setattr(
        StructuredResearchProposalManager,
        "_deterministic_parent_step",
        staticmethod(broken_parent),
    )
    with pytest.raises(ValueError, match="deterministic parent resolution defect"):
        manager.propose_for_obligation(
            snapshot,
            target_parent_obligation="g_source",
            allowed_evidence_refs=("evi_source",),
        )
    assert manager.call_count == 1
    assert len(transport.users) == 1


def test_v1_state_profile_contradiction_is_not_converted_to_inconclusive(monkeypatch):
    snapshot = _scoped_snapshot()
    transport = _SequenceTransport([_semantic_response(), _semantic_response()])
    manager = StructuredResearchProposalManager(transport=transport)

    def broken_binding(*args, **kwargs):
        raise RuntimeError("state/action-profile contradiction")

    monkeypatch.setattr(
        StructuredResearchProposalManager,
        "_proposal_from_semantic",
        classmethod(broken_binding),
    )
    with pytest.raises(RuntimeError, match="state/action-profile contradiction"):
        manager.propose_for_obligation(
            snapshot,
            target_parent_obligation="g_source",
            allowed_evidence_refs=("evi_source",),
        )
    assert manager.call_count == 1
    assert len(transport.users) == 1


def test_v1_internal_machine_identity_binding_defect_is_not_provider_repaired(monkeypatch):
    snapshot = _scoped_snapshot()
    transport = _SequenceTransport([_semantic_response(), _semantic_response()])
    manager = StructuredResearchProposalManager(transport=transport)

    def broken_stable(*args, **kwargs):
        raise ValueError("machine identity binding defect")

    monkeypatch.setattr(
        StructuredResearchProposalManager,
        "_stable",
        staticmethod(broken_stable),
    )
    with pytest.raises(ValueError, match="machine identity binding defect"):
        manager.propose_for_obligation(
            snapshot,
            target_parent_obligation="g_source",
            allowed_evidence_refs=("evi_source",),
        )
    assert manager.call_count == 1
    assert len(transport.users) == 1


def test_v1_provider_closed_choice_violation_repairs_once():
    snapshot = _scoped_snapshot()
    transport = _SequenceTransport(
        [
            _semantic_response(objective="not-a-governed-objective"),
            _semantic_response(),
        ]
    )
    manager = StructuredResearchProposalManager(transport=transport)

    proposal = manager.propose_for_obligation(
        snapshot,
        target_parent_obligation="g_source",
        allowed_evidence_refs=("evi_source",),
    )

    assert proposal.intent == InvestigationIntent.DEEPEN_EXPLANATION
    assert manager.call_count == 2
    assert len(transport.users) == 2
    assert "PROVIDER-CONTRACT REPAIR" in transport.users[1]
