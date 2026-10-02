from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from hypothesis import settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from app.v3.business_relationship_v1 import RelationshipAnalyticalKind
from app.v3.claim_lineage import ClaimEvidenceRelation
from app.v3.p18_relationship_interpreter import (
    P18EvidenceDigest,
    P18RelationshipView,
    RelationshipMaterialMode,
    StructuredP18RelationshipInterpreter,
    interpretation_ref,
)
from app.v3.research_contracts import RelationshipIntent


EVIDENCE = "evi_" + "a" * 24
RECEIPT = "dqr_" + "b" * 24


class StaticTransport:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema, schema_name
        return json.dumps(self.payload)


def _view(
    *,
    mode: RelationshipMaterialMode,
    left: int,
    right: int,
) -> P18RelationshipView:
    return P18RelationshipView(
        requirement_id="g_relationship",
        relationship_intent=RelationshipIntent.OBSERVATIONAL,
        scope_version_id="scope_v1",
        material_group_id="mg_" + "c" * 24,
        material_mode=mode,
        source_semantic_id="metric.left",
        target_semantic_id="metric.right",
        dimension_semantic_ids=("dimension.entity",),
        evidence=(
            P18EvidenceDigest(
                evidence_id=EVIDENCE,
                receipt_id=RECEIPT,
                execution_link_id="execution-1",
                result_hash="d" * 64,
                executed_at=datetime(2026, 10, 2, tzinfo=timezone.utc),
                row_count=1,
                columns=("Entity", "Left", "Right"),
                rows=(("A", left, right),),
            ),
        ),
    )


def _payload(
    *,
    kind: str = "ASSOCIATION",
    relation: str = "SUPPORTS",
    salient: bool = True,
) -> dict:
    return {
        "analytical_kind": kind,
        "claim_text": "Bounded relationship interpretation over current Evidence.",
        "evidence_assessments": [
            {
                "evidence_id": EVIDENCE,
                "relation": relation,
            }
        ],
        "salient_cells": (
            [
                {
                    "evidence_id": EVIDENCE,
                    "row_index": 0,
                    "column_index": 1,
                },
                {
                    "evidence_id": EVIDENCE,
                    "row_index": 0,
                    "column_index": 2,
                },
            ]
            if salient
            else []
        ),
        "limitations": [
            "The bounded interpretation does not establish causality."
        ],
    }


class P18RelationshipStateMachine(RuleBasedStateMachine):
    """Sequence model for the normal P18-owned relationship boundary."""

    def __init__(self):
        super().__init__()
        self.p17_provider_calls = 0
        self.analytics_reentries = 0
        self.successful_interpretations = 0
        self.sealed_refs: set[str] = set()

    @rule(
        left=st.integers(min_value=-1_000_000, max_value=1_000_000),
        right=st.integers(min_value=-1_000_000, max_value=1_000_000),
    )
    def cross_sectional_supported(self, left, right):
        view = _view(
            mode=RelationshipMaterialMode.CROSS_SECTIONAL_ASSOCIATION,
            left=left,
            right=right,
        )
        draft = StructuredP18RelationshipInterpreter(
            transport=StaticTransport(_payload())
        ).interpret(view)
        assert draft.analytical_kind == RelationshipAnalyticalKind.ASSOCIATION
        assert {
            (item.evidence_id, item.row_index, item.column_index)
            for item in draft.salient_cells
        } == {
            (EVIDENCE, 0, 1),
            (EVIDENCE, 0, 2),
        }
        first = interpretation_ref(view=view, draft=draft)
        second = interpretation_ref(view=view, draft=draft)
        assert first == second
        self.sealed_refs.add(first)
        self.successful_interpretations += 1

    @rule(
        left=st.integers(min_value=-10_000, max_value=10_000),
        right=st.integers(min_value=-10_000, max_value=10_000),
    )
    def insufficient_material_stays_explicit(self, left, right):
        view = _view(
            mode=RelationshipMaterialMode.CROSS_SECTIONAL_ASSOCIATION,
            left=left,
            right=right,
        )
        draft = StructuredP18RelationshipInterpreter(
            transport=StaticTransport(
                _payload(
                    relation=ClaimEvidenceRelation.INSUFFICIENT.value,
                    salient=False,
                )
            )
        ).interpret(view)
        assert draft.salient_cells == ()
        assert draft.evidence_assessments[0].relation == ClaimEvidenceRelation.INSUFFICIENT
        self.successful_interpretations += 1

    @rule(
        left=st.integers(min_value=-10_000, max_value=10_000),
        right=st.integers(min_value=-10_000, max_value=10_000),
    )
    def temporal_material_can_express_bounded_comovement(self, left, right):
        view = _view(
            mode=RelationshipMaterialMode.TEMPORAL_CO_MOVEMENT,
            left=left,
            right=right,
        )
        draft = StructuredP18RelationshipInterpreter(
            transport=StaticTransport(_payload(kind="CO_MOVEMENT"))
        ).interpret(view)
        assert draft.analytical_kind == RelationshipAnalyticalKind.CO_MOVEMENT
        self.successful_interpretations += 1

    @rule()
    def cross_sectional_material_cannot_promote_comovement(self):
        view = _view(
            mode=RelationshipMaterialMode.CROSS_SECTIONAL_ASSOCIATION,
            left=10,
            right=5,
        )
        with pytest.raises(ValueError, match="cross-sectional"):
            StructuredP18RelationshipInterpreter(
                transport=StaticTransport(_payload(kind="CO_MOVEMENT"))
            ).interpret(view)

    @rule()
    def checkpoint_roundtrip_preserves_closed_view(self):
        view = _view(
            mode=RelationshipMaterialMode.CROSS_SECTIONAL_ASSOCIATION,
            left=7,
            right=3,
        )
        resumed = P18RelationshipView.model_validate(
            view.model_dump(mode="json")
        )
        assert resumed == view

    @invariant()
    def normal_relationship_never_routes_to_p17_or_analytics(self):
        assert self.p17_provider_calls == 0
        assert self.analytics_reentries == 0


TestP18RelationshipStateMachine = P18RelationshipStateMachine.TestCase
TestP18RelationshipStateMachine.settings = settings(
    max_examples=200,
    stateful_step_count=12,
    deadline=None,
)
