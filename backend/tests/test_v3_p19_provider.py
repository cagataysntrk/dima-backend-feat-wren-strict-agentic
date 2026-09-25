from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.v3.hypothesis_root_cause import (
    GroundingRelation,
    GroundingSourceKind,
    HypothesisSnapshot,
    P19CaseSnapshot,
    P19GroundingLink,
    P19Hypothesis,
)
from app.v3.hypothesis_root_cause_provider import (
    ModelAssessmentDraft,
    StructuredP19AssessmentManager,
    provider_schema,
)


STAMP = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)


def hypothesis(char: str, statement: str) -> P19Hypothesis:
    return P19Hypothesis(
        hypothesis_id="p19h_" + char * 24,
        research_session_id="rs_" + "1" * 24,
        obligation_id="g1",
        tenant_binding="id:tenant",
        semantic_context_version="ctx-p19-live-v1",
        statement=statement,
        identity_fingerprint=char * 64,
        created_at=STAMP,
    )


def link(
    hypothesis_id: str,
    char: str,
    *,
    source_kind: GroundingSourceKind,
    source_ref: str,
    relation: GroundingRelation,
    receipt: str | None = None,
) -> P19GroundingLink:
    return P19GroundingLink(
        grounding_link_id="p19g_" + char * 24,
        hypothesis_id=hypothesis_id,
        source_kind=source_kind,
        source_ref=source_ref,
        source_receipt_id=receipt,
        relation=relation,
        link_fingerprint=char * 64,
        created_at=STAMP,
    )


def snapshot() -> P19CaseSnapshot:
    a = hypothesis("a", "Channel mix may explain the observed difference.")
    b = hypothesis("b", "Customer composition may explain the observed difference.")
    ae = link(
        a.hypothesis_id,
        "c",
        source_kind=GroundingSourceKind.P14_EVIDENCE,
        source_ref="evi_" + "1" * 24,
        receipt="dqr_" + "1" * 24,
        relation=GroundingRelation.SUPPORTS,
    )
    ap = link(
        a.hypothesis_id,
        "d",
        source_kind=GroundingSourceKind.P18_POLICY_USE,
        source_ref="bru_" + "1" * 24,
        relation=GroundingRelation.CONTEXT,
    )
    bm = link(
        b.hypothesis_id,
        "e",
        source_kind=GroundingSourceKind.P15_MATERIAL,
        source_ref="rle_" + "2" * 24,
        relation=GroundingRelation.SUPPORTS,
    )
    bc = link(
        b.hypothesis_id,
        "f",
        source_kind=GroundingSourceKind.P16_CLAIM,
        source_ref="clm_" + "3" * 24,
        relation=GroundingRelation.CHALLENGES,
    )
    return P19CaseSnapshot(
        research_session_id=a.research_session_id,
        obligation_id="g1",
        tenant_binding=a.tenant_binding,
        semantic_context_version=a.semantic_context_version,
        hypotheses=(
            HypothesisSnapshot(hypothesis=a, groundings=(ae, ap)),
            HypothesisSnapshot(hypothesis=b, groundings=(bm, bc)),
        ),
    )


def assert_strict_objects(node):
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict):
            assert node.get("additionalProperties") is False
            assert set(node.get("required", [])) == set(props)
        for child in node.values():
            assert_strict_objects(child)
    elif isinstance(node, list):
        for child in node:
            assert_strict_objects(child)


class FakeTransport:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def structured_json(self, system, user, *, schema, schema_name):
        self.calls.append(
            {
                "system": system,
                "user": user,
                "schema": schema,
                "schema_name": schema_name,
            }
        )
        return json.dumps(self.payload)


def valid_payload():
    snap = snapshot()
    a, b = snap.hypotheses
    return {
        "candidates": [
            {
                "hypothesis_id": a.hypothesis.hypothesis_id,
                "grounding_link_ids": [
                    x.grounding_link_id for x in a.groundings
                ],
                "disposition": "RETAINED",
                "epistemic_class": "CONTRIBUTION",
                "contribution_class": "MATERIAL",
                "evidence_strength": "MODERATE",
                "causal_qualification": "IDENTIFICATION_LIMITED",
                "relationship_dependent": True,
                "relationship_policy_use_id": "bru_" + "1" * 24,
                "identification_limitations": ["ASSOCIATION_ONLY"],
            },
            {
                "hypothesis_id": b.hypothesis.hypothesis_id,
                "grounding_link_ids": [
                    x.grounding_link_id for x in b.groundings
                ],
                "disposition": "RETAINED",
                "epistemic_class": "COMPETING_HYPOTHESIS",
                "contribution_class": "MATERIAL",
                "evidence_strength": "WEAK",
                "causal_qualification": "IDENTIFICATION_LIMITED",
                "relationship_dependent": False,
                "relationship_policy_use_id": None,
                "identification_limitations": [
                    "CONFOUNDING_NOT_RESOLVED"
                ],
            },
        ],
        "aggregate_outcome": "MULTIPLE_MATERIAL_CONTRIBUTORS",
        "root_cause_hypothesis_ids": [],
        "limitations": ["Causal identification remains limited."],
    }


def test_provider_schema_is_portable_strict_and_has_no_numeric_confidence_field():
    schema = provider_schema()
    assert_strict_objects(schema)
    raw = json.dumps(schema, sort_keys=True)
    for forbidden in (
        "confidence_percent",
        "causal_probability",
        "contribution_percent",
        "effect_percent",
    ):
        assert forbidden not in raw


def test_typed_provider_maps_qualitative_complete_assessment():
    transport = FakeTransport(valid_payload())
    manager = StructuredP19AssessmentManager(transport=transport)
    draft = manager.propose(
        snapshot(),
        policy_statuses={"bru_" + "1" * 24: "SATISFIED"},
    )

    assert manager.call_count == 1
    assert len(draft.candidates) == 2
    assert draft.aggregate_outcome.value == "MULTIPLE_MATERIAL_CONTRIBUTORS"
    assert all(not x.numeric_provenance for x in draft.candidates)
    assert all(not x.causal_identification_refs for x in draft.candidates)
    assert "numeric_values_exposed_to_model" in transport.calls[0]["user"]


def test_provider_rejects_missing_competing_hypothesis():
    payload = valid_payload()
    payload["candidates"] = payload["candidates"][:1]
    manager = StructuredP19AssessmentManager(
        transport=FakeTransport(payload)
    )
    with pytest.raises(ValueError, match="complete hypothesis set"):
        manager.propose(snapshot())


def test_provider_rejects_foreign_grounding_assignment():
    payload = valid_payload()
    payload["candidates"][0]["grounding_link_ids"] = [
        payload["candidates"][1]["grounding_link_ids"][0]
    ]
    manager = StructuredP19AssessmentManager(
        transport=FakeTransport(payload)
    )
    with pytest.raises(ValueError, match="unknown/foreign grounding"):
        manager.propose(snapshot())


def test_provider_contract_rejects_model_invented_numeric_confidence():
    payload = valid_payload()
    payload["candidates"][0]["confidence_percent"] = 83
    transport = FakeTransport(payload)
    manager = StructuredP19AssessmentManager(transport=transport)
    with pytest.raises(ValidationError):
        manager.propose(snapshot())


def test_feedback_code_is_visible_without_prescribing_winner():
    transport = FakeTransport(valid_payload())
    manager = StructuredP19AssessmentManager(transport=transport)
    manager.propose(
        snapshot(),
        deterministic_feedback_code="P19_CAUSAL_PROMOTION_GATE_FAILED",
    )
    user = transport.calls[0]["user"]
    assert "P19_CAUSAL_PROMOTION_GATE_FAILED" in user
    assert "candidate A must win" not in user.lower()


def test_provider_module_has_no_analytical_executor_dependency():
    path = Path("app/v3/hypothesis_root_cause_provider.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")

    forbidden = (
        "app.v3.substrate.metabase",
        "app.v3.research_native_gateway",
        "app.v3.research_followup",
        "app.wren",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
    )
    assert not any(name.startswith(forbidden) for name in imports)


def test_model_draft_has_no_numeric_or_causal_source_authority_fields():
    fields = set(ModelAssessmentDraft.model_fields)
    assert "confidence" not in fields
    assert "numeric_provenance" not in fields
    assert "causal_identification_refs" not in fields
