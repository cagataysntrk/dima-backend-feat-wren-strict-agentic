import lab.v2_day7_relationship_action_diagnostic as diag


def test_relationship_receipt_separates_first_owner_from_downstream_model_symptoms():
    diag._RAW_CALLS.clear()
    diag._RAW_CALLS.extend(
        [
            {
                "case_id": "relationship-safe",
                "schema_name": "dima_research_manager_action_v1",
                "raw_output": {
                    "action": "resolve_semantics",
                    "resolve_provenance": "USER_SOURCE",
                    "source_surfaces": ["bölümlerle"],
                },
            },
            {
                "case_id": "relationship-safe",
                "schema_name": "dima_research_manager_action_v1",
                "raw_output": {
                    "action": "run_relationship",
                    "relationship_obligation_id": "obligation_1",
                    "focus_handles": ["h1"],
                    "counterpart_handles": ["h2"],
                    "derived_task_id": "derived:bad",
                    "derived_parent_obligation_id": "obligation_1",
                    "derived_capability_key": "relationship",
                    "derived_evidence_ref": "evi_bad",
                    "derived_reason": "bad cross-action carryover",
                },
            },
        ]
    )

    body = {
        "snapshot": {
            "accepted_contract_id": "atc_test",
            "data_queries": 0,
            "evidence_refs": [],
        },
        "observations": [
            {
                "kind": "intent_draft",
                "draft": {
                    "obligations": [
                        {
                            "obligation_id": "obligation_1",
                            "capability_key": "relationship",
                            "semantic_surfaces": [
                                {"surface": "Duruş süresinin", "kind_hint": "metric"},
                                {"surface": "bölümlerle", "kind_hint": "dimension"},
                            ],
                        }
                    ]
                },
            },
            {
                "kind": "grounding",
                "summary": {
                    "requested": [
                        {
                            "owner_id": "obligation_1",
                            "capability": "relationship",
                            "surface": "Duruş süresinin",
                            "kind_hint": "metric",
                            "resolved": True,
                        },
                        {
                            "owner_id": "obligation_1",
                            "capability": "relationship",
                            "surface": "bölümlerle",
                            "kind_hint": "dimension",
                            "resolved": False,
                        },
                    ],
                    "unresolved_source_refs": ["src_missing"],
                },
            },
            {
                "kind": "seed_tasks_registered",
                "ready_task_ids": ["seed:obligation_1"],
            },
            {
                "kind": "tool_rejected",
                "action": "resolve_semantics",
                "message": (
                    "post-acceptance USER_SOURCE semantic reparsing is forbidden; "
                    "use accepted authority or AGENT_DERIVED evidence-grounded discovery"
                ),
            },
            {
                "kind": "model_error",
                "message": "derived task fields are valid only for run_analytics",
            },
        ],
        "ledger": {
            "items": [
                {
                    "obligation_id": "obligation_1",
                    "capability_key": "relationship",
                    "semantic_handle_refs": ["sem_metric"],
                    "semantic_bindings": [
                        {"handle_id": "sem_metric", "target_kind": "metric"}
                    ],
                }
            ]
        },
    }

    receipt = diag._case_receipt(
        {
            "case_id": "relationship-safe",
            "question": "Duruş süresinin bölümlerle ilişkisini incele.",
        },
        body,
    )

    assert receipt["first_owner"] == "PREACCEPTANCE_COMPLETENESS"
    assert receipt["attempted_postacceptance_user_source_reparse"] is True
    assert receipt["accepted_semantic_handles"] == ["sem_metric"]
    assert receipt["derived_fields_on_run_relationship"][0]["derived_task_id"] == "derived:bad"
    assert (
        "MODEL_COGNITION_INVALID_DERIVED_FIELDS_ON_RUN_RELATIONSHIP"
        in receipt["secondary_observations"]
    )
