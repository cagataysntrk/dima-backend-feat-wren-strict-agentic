import json
from datetime import datetime, timezone

import pytest

from app.v3.business_relationship_v1 import RelationshipAnalyticalKind
from app.v3.claim_lineage import ClaimEvidenceRelation
from app.v3.p18_relationship_interpreter import (
    P18EvidenceDigest,
    P18RelationshipView,
    RelationshipMaterialMode,
    StructuredP18RelationshipInterpreter,
)
from app.v3.research_contracts import RelationshipIntent


EVIDENCE = "evi_" + "a" * 24


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


def view(mode=RelationshipMaterialMode.CROSS_SECTIONAL_ASSOCIATION):
    return P18RelationshipView(
        requirement_id="g_relationship",
        relationship_intent=RelationshipIntent.OBSERVATIONAL,
        scope_version_id="scope_v1",
        material_group_id="mg_" + "b" * 24,
        material_mode=mode,
        source_semantic_id="metric.downtime",
        target_semantic_id="metric.fault_count",
        dimension_semantic_ids=("dimension.department",),
        evidence=(
            P18EvidenceDigest(
                evidence_id=EVIDENCE,
                receipt_id="dqr_" + "c" * 24,
                execution_link_id="exec-1",
                result_hash="d" * 64,
                executed_at=datetime(2026, 10, 2, tzinfo=timezone.utc),
                row_count=2,
                columns=("Department", "Downtime", "Faults"),
                rows=(("A", 10, 3), ("B", 4, 1)),
            ),
        ),
    )


def payload(kind="ASSOCIATION", evidence_id=EVIDENCE):
    return {
        "analytical_kind": kind,
        "claim_text": "The observed cross-sectional values support an association.",
        "evidence_assessments": [
            {
                "evidence_id": evidence_id,
                "relation": ClaimEvidenceRelation.SUPPORTS.value,
            }
        ],
        "salient_cells": [
            {
                "evidence_id": evidence_id,
                "row_index": 0,
                "column_index": 1,
            },
            {
                "evidence_id": evidence_id,
                "row_index": 0,
                "column_index": 2,
            },
        ],
        "limitations": [
            "Cross-sectional evidence does not establish temporal order or causality."
        ],
    }


def test_p18_interpreter_accepts_closed_cross_sectional_association():
    transport = FakeTransport(payload())
    manager = StructuredP18RelationshipInterpreter(transport=transport)

    result = manager.interpret(view())

    assert result.analytical_kind == RelationshipAnalyticalKind.ASSOCIATION
    assert result.evidence_assessments[0].evidence_id == EVIDENCE
    assert {(x.row_index, x.column_index) for x in result.salient_cells} == {
        (0, 1),
        (0, 2),
    }
    assert manager.call_count == 1
    schema = transport.calls[0]["schema"]
    assert schema["properties"]["analytical_kind"]["enum"] == ["ASSOCIATION"]


def test_cross_sectional_material_cannot_promote_temporal_co_movement():
    manager = StructuredP18RelationshipInterpreter(
        transport=FakeTransport(payload(kind="CO_MOVEMENT"))
    )

    with pytest.raises(ValueError, match="cross-sectional"):
        manager.interpret(view())


def test_p18_interpreter_rejects_foreign_evidence_identity():
    manager = StructuredP18RelationshipInterpreter(
        transport=FakeTransport(payload(evidence_id="evi_" + "f" * 24))
    )

    with pytest.raises(ValueError):
        manager.interpret(view())


def test_temporal_material_schema_may_express_co_movement():
    transport = FakeTransport(payload(kind="CO_MOVEMENT"))
    manager = StructuredP18RelationshipInterpreter(transport=transport)

    result = manager.interpret(
        view(RelationshipMaterialMode.TEMPORAL_CO_MOVEMENT)
    )

    assert result.analytical_kind == RelationshipAnalyticalKind.CO_MOVEMENT
    assert set(transport.calls[0]["schema"]["properties"]["analytical_kind"]["enum"]) == {
        "ASSOCIATION",
        "CO_MOVEMENT",
    }



def test_p18_interpreter_rejects_out_of_bounds_salient_cell():
    bad = payload()
    bad["salient_cells"][1]["row_index"] = 99
    manager = StructuredP18RelationshipInterpreter(transport=FakeTransport(bad))

    with pytest.raises(ValueError, match="outside Evidence"):
        manager.interpret(view())


def test_p18_interpreter_rejects_non_numeric_salient_cell():
    bad = payload()
    bad["salient_cells"][0]["column_index"] = 0
    manager = StructuredP18RelationshipInterpreter(transport=FakeTransport(bad))

    with pytest.raises(ValueError, match="exact numeric"):
        manager.interpret(view())


def test_supported_numeric_relationship_requires_two_observed_metric_columns():
    bad = payload()
    bad["salient_cells"] = bad["salient_cells"][:1]
    manager = StructuredP18RelationshipInterpreter(transport=FakeTransport(bad))

    with pytest.raises(ValueError, match="at least two observed numeric columns"):
        manager.interpret(view())


def test_p18_interpreter_module_cannot_open_analytics():
    from pathlib import Path

    source = Path("app/v3/p18_relationship_interpreter.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "NativeEngineBridge",
        "NativeResearchMaterialExecutor",
        "NativeSubjectSessionProvider",
        "research_native_gateway",
        "substrate.metabase",
        "ResearchInvestigationManager",
        "StructuredResearchProposalManager",
        "execute_native",
        "explore_adhoc",
    ):
        assert forbidden not in source


def test_salient_schema_enumerates_only_existing_numeric_cells():
    transport = FakeTransport(payload())
    manager = StructuredP18RelationshipInterpreter(transport=transport)

    manager.interpret(view())

    salient = transport.calls[0]["schema"]["$defs"]["P18SalientCell"]
    assert salient["enum"] == [
        {"evidence_id": EVIDENCE, "row_index": 0, "column_index": 1},
        {"evidence_id": EVIDENCE, "row_index": 0, "column_index": 2},
        {"evidence_id": EVIDENCE, "row_index": 1, "column_index": 1},
        {"evidence_id": EVIDENCE, "row_index": 1, "column_index": 2},
    ]
