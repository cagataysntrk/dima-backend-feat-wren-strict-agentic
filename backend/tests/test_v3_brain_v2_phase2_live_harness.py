from lab.metabase.core_b.phase1_pinpoint_live import (
    PROBES,
    _mechanical_multi_intent,
    _mechanical_relationship_report_phase2,
)


def _completion():
    return {"completion_ledger": {"requirement_complete": True}}


def test_phase2_relationship_report_probe_is_exact_two_turn_contract():
    probe = PROBES["RELATIONSHIP_REPORT_PHASE2_V1"]
    assert len(probe["turns"]) == 2
    assert "association/co-movement" in probe["turns"][0]
    assert "Yeni analitik acquisition açma" in probe["turns"][1]


def test_phase2_relationship_report_mechanical_requires_reuse_not_requery():
    turns = [
        {
            "ready": True,
            "brief_payload": {
                "questions": [
                    {
                        "kind": "relationship",
                        "relationship_intent": "observational",
                    }
                ]
            },
            "p18_policy_use_refs": ["bru_" + "1" * 24],
            "p19_assessment_refs": [],
            "native_results": [{"query": "q1"}],
            "evidence_by_session": {"rs1": [{"evidence_id": "e1"}]},
            "scope_lineage_id": "atl1",
            "composition_payload": {
                **_completion(),
                "relationship_results": [
                    {
                        "policy_use_id": "bru_" + "1" * 24,
                        "policy_id": None,
                        "policy_required": False,
                        "association_state": "SUPPORTED",
                        "business_relationship_state": "NOT_ESTABLISHED",
                        "contribution_state": "NOT_ESTABLISHED",
                        "causality_state": "NOT_ESTABLISHED",
                    }
                ],
            },
        },
        {
            "ready": True,
            "native_results": [],
            "evidence_by_session": {"rs1": [{"evidence_id": "e1"}]},
            "scope_lineage_id": "atl1",
            "p20_report": {
                "document": {"report_id": "p20r1"},
                "currentness": "CURRENT",
            },
            "composition_payload": _completion(),
        },
    ]
    result = _mechanical_relationship_report_phase2(turns)
    assert result
    assert all(result.values())


def test_phase2_observational_relationship_accepts_not_required_p18_receipt():
    turn = {
        "ready": True,
        "brief_payload": {
            "questions": [
                {
                    "kind": "relationship",
                    "relationship_intent": "observational",
                }
            ]
        },
        # P18 persists a NOT_REQUIRED resolution receipt for auditability.
        # Its presence is not BUSINESS_POLICY use.
        "p18_policy_use_refs": ["bru_" + "1" * 24],
        "p19_assessment_refs": [],
        "native_results": [{"query": "q1"}],
        "evidence_by_session": {"rs1": [{"evidence_id": "e1"}]},
        "composition_payload": {
            **_completion(),
            "relationship_results": [
                {
                    "policy_use_id": "bru_" + "1" * 24,
                    "policy_id": None,
                    "policy_required": False,
                    "association_state": "SUPPORTED",
                    "business_relationship_state": "NOT_ESTABLISHED",
                    "contribution_state": "NOT_ESTABLISHED",
                    "causality_state": "NOT_ESTABLISHED",
                }
            ],
        },
    }

    from lab.metabase.core_b.phase1_pinpoint_live import (
        _mechanical_observational_relationship,
    )

    result = _mechanical_observational_relationship(turn)
    assert result["single_observational_relationship"] is True
    assert result["no_business_policy_use"] is True
    assert result["no_causal_assessment_for_observation"] is True


def test_phase2_multi_intent_mechanical_requires_shared_single_material():
    turn = {
        "ready": True,
        "brief_payload": {
            "questions": [
                {"kind": "ranking"},
                {"kind": "relationship"},
            ],
            "deliverables": [{"kind": "report"}],
            "must_requirement_ids": ["rank", "rel", "report"],
        },
        "native_results": [{"query": "shared-q"}],
        "evidence_by_session": {"rs1": [{"evidence_id": "e1"}]},
        "p20_report": {
            "document": {"report_id": "p20r1"},
            "currentness": "CURRENT",
        },
        "composition_payload": {
            "completion_ledger": {"requirement_complete": True},
            "user_must_fulfillment": [
                {"requirement_id": "rank"},
                {"requirement_id": "rel"},
                {"requirement_id": "report"},
            ],
        },
    }
    result = _mechanical_multi_intent(turn)
    assert result
    assert all(result.values())


def test_phase2_multi_intent_rejects_duplicate_native_material():
    turn = {
        "ready": True,
        "brief_payload": {
            "questions": [
                {"kind": "ranking"},
                {"kind": "relationship"},
            ],
            "deliverables": [{"kind": "report"}],
            "must_requirement_ids": ["rank", "rel", "report"],
        },
        "native_results": [{"query": "q1"}, {"query": "q2"}],
        "evidence_by_session": {"rs1": [{"evidence_id": "e1"}]},
        "p20_report": {"document": {"report_id": "p20r1"}},
        "composition_payload": {
            "completion_ledger": {"requirement_complete": True},
            "user_must_fulfillment": [
                {"requirement_id": "rank"},
                {"requirement_id": "rel"},
                {"requirement_id": "report"},
            ],
        },
    }
    result = _mechanical_multi_intent(turn)
    assert result["single_shared_native_material"] is False
