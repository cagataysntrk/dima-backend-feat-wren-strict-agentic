"""Provider-free contract for the manual D10-G17/G18 paid harness."""

from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    ResearchDirective,
    ResearchDirectiveCondition,
    ResearchDirectiveDisposition,
    ResearchDirectiveDispositionStatus,
    ResearchDirectiveType,
    SemanticResolutionReceipt,
    UserObligationLedger,
)
from app.v2.models import EvidenceArtifact
from lab.v2_certification_oracle import (
    certify_adaptive_lifecycle,
    certify_day8_root_live_debt,
    evidence_belongs_to_parent_lineage,
)
from app.v2.product_models import ProductLane, ProductStatus
from app.v2.standard_lane import StandardLaneStatus
from lab import v2_day10_product_mvp_live as paid


def test_paid_harness_role_and_global_ceiling_are_hard_and_explicit():
    assert paid.MAX_HARNESS_TOTAL_CALLS == 20
    assert paid.ROLE_LIMITS == {
        "FAST_LANGUAGE": 2,
        "RESEARCH_MANAGER": 12,
        "SEMANTIC_LINKER": 4,
        "TEMPORAL_NORMALIZER": 1,
        "REPORT_NARRATOR": 2,
    }
    # Per-role ceilings are independent anti-waste guards. Their sum may exceed
    # the hard global ceiling; MAX_HARNESS_TOTAL_CALLS remains the final cap.
    assert sum(paid.ROLE_LIMITS.values()) > paid.MAX_HARNESS_TOTAL_CALLS

    budget = paid.RoleCallBudget(
        max_total=2,
        role_limits={**paid.ROLE_LIMITS, "FAST_LANGUAGE": 1},
    )
    budget.reserve(
        role="FAST_LANGUAGE",
        model=paid.FAST_MODEL,
        schema_name="x",
    )
    with pytest.raises(paid.PaidBudgetExceeded):
        budget.reserve(
            role="FAST_LANGUAGE",
            model=paid.FAST_MODEL,
            schema_name="y",
        )

    global_budget = paid.RoleCallBudget(
        max_total=1,
        role_limits=paid.ROLE_LIMITS,
    )
    global_budget.reserve(
        role="SEMANTIC_LINKER",
        model=paid.SEMANTIC_MODEL,
        schema_name="first",
    )
    with pytest.raises(
        paid.PaidBudgetExceeded,
        match="global paid-call ceiling exhausted",
    ):
        global_budget.reserve(
            role="RESEARCH_MANAGER",
            model=paid.RESEARCH_MODEL,
            schema_name="second",
        )


def test_blank_or_unknown_scope_fails_before_settings_or_provider_construction(monkeypatch):
    touched = {"settings": False}

    def forbidden_settings():
        touched["settings"] = True
        raise AssertionError("settings/provider construction must not occur")

    monkeypatch.setattr(paid, "get_settings", forbidden_settings)
    for scope in ("", "ALL", "NS4", "anything"):
        with pytest.raises(paid.PaidHarnessError, match="explicit scope"):
            paid.run_paid(scope=scope, max_total_model_calls=1)

    assert touched["settings"] is False


def test_paid_topology_is_exact_and_has_no_provider_cascade():
    assert paid.RESEARCH_MODEL == "openai/gpt-5.6-sol"
    assert paid.SEMANTIC_MODEL == "openai/gpt-5.6-luna"
    assert paid.TEMPORAL_MODEL == "openai/gpt-5.6-sol"
    assert paid.NARRATOR_MODEL == "openai/gpt-5.6-sol"
    assert paid.MAX_PRODUCT_TURNS == 2


def test_workflow_is_manual_only_single_job_and_explicit_scope():
    workflow = Path("../.github/workflows/v2-day10-product-mvp-paid-once.yml")
    text = workflow.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "\npush:" not in text
    assert "\npull_request:" not in text
    assert "CANONICAL_NS4" in text
    assert "DAY10_PAID_ONCE" in text
    assert "max_total_model_calls > 0" in text
    assert "max_total_model_calls <= 20" in text
    assert "ONE supervised paid Product-MVP gate" in text
    assert "matrix:" not in text
    assert "strategy:" not in text
    assert "workers" not in text.lower()


def test_paid_harness_uses_authoritative_lifecycle_oracles():
    assert "doğrulanmış sonuçlar yeni bir maddi" in paid.INITIAL_QUESTION
    assert paid.certify_adaptive_lifecycle is certify_adaptive_lifecycle
    assert paid.certify_day8_root_live_debt is certify_day8_root_live_debt
    assert paid.MAX_PRODUCT_TURNS == 2

@pytest.mark.parametrize(
    ("product_status", "standard_status"),
    (
        (ProductStatus.ANSWER, StandardLaneStatus.ACCEPTED),
        (ProductStatus.CLARIFY, StandardLaneStatus.CLARIFICATION_REQUIRED),
        (ProductStatus.UNSUPPORTED, StandardLaneStatus.UNSUPPORTED),
        (ProductStatus.FAILED, StandardLaneStatus.FAILED),
    ),
)
def test_paid_failure_diagnostics_preserve_exact_standard_terminal_family(
    product_status,
    standard_status,
):
    budget = paid.RoleCallBudget(
        max_total=paid.MAX_HARNESS_TOTAL_CALLS,
        role_limits=dict(paid.ROLE_LIMITS),
    )
    budget.reserve(
        role="FAST_LANGUAGE",
        model=paid.FAST_MODEL,
        schema_name="dima_standard_intent_draft_v1",
    )
    standard_lane = SimpleNamespace(
        last_outcome=SimpleNamespace(
            status=standard_status,
            reasons=("typed-standard-terminal",),
            attempts=1,
            coverage_status=None,
            work_mode=None,
            obligations=(),
        )
    )
    service = SimpleNamespace(query_calls=0, dry_plan_calls=0, cube_sql_calls=0)
    product = SimpleNamespace(
        lane=ProductLane.STANDARD,
        status=product_status,
        turn_ref="turn_diagnostic",
        terminal_receipt=SimpleNamespace(
            terminal_status=standard_status.value,
            reasons=("typed-product-terminal",),
        ),
        events=(),
    )

    research_lane = SimpleNamespace(last_result=None)
    snapshot = paid._diagnostic_snapshot(
        product=product,
        standard_lane=standard_lane,
        research_lane=research_lane,
        budget=budget,
        service=service,
        structured_outputs=[
            {
                "sequence": 1,
                "role": "FAST_LANGUAGE",
                "model": paid.FAST_MODEL,
                "schema_name": "dima_standard_intent_draft_v1",
                "validated_output": {"obligations": []},
            }
        ],
    )

    assert snapshot["product"]["lane"] == "STANDARD"
    assert snapshot["product"]["status"] == product_status.value
    assert snapshot["product"]["terminal_status"] == standard_status.value
    assert snapshot["product"]["terminal_reasons"] == ["typed-product-terminal"]
    assert snapshot["standard"]["status"] == standard_status.value
    assert snapshot["standard"]["reasons"] == ["typed-standard-terminal"]
    assert snapshot["standard"]["attempts"] == 1
    assert snapshot["model_calls"]["total"] == 1
    assert snapshot["model_calls"]["calls"][0]["schema_name"] == "dima_standard_intent_draft_v1"
    assert snapshot["structured_outputs"][0]["schema_name"] == (
        "dima_standard_intent_draft_v1"
    )
    assert snapshot["wren"] == {
        "query_calls": 0,
        "dry_plan_calls": 0,
        "cube_sql_calls": 0,
    }


def test_counting_structured_captures_only_controlled_diagnostic_outputs():
    class Inner:
        def structured_json(self, *args, **kwargs):
            return {"status": "PASS"}

    captured = []
    budget = paid.RoleCallBudget(
        max_total=paid.MAX_HARNESS_TOTAL_CALLS,
        role_limits=dict(paid.ROLE_LIMITS),
    )
    wrapper = paid.CountingStructured(
        inner=Inner(),
        budget=budget,
        role="FAST_LANGUAGE",
        model=paid.FAST_MODEL,
        captured_outputs=captured,
    )

    wrapper.structured_json(
        "system",
        "user",
        schema={},
        schema_name="dima_standard_coverage_v1",
    )
    wrapper.structured_json(
        "system",
        "user",
        schema={},
        schema_name="not-a-controlled-diagnostic-schema",
    )

    assert len(captured) == 1
    assert captured[0]["schema_name"] == "dima_standard_coverage_v1"
    assert captured[0]["validated_output"] == {"status": "PASS"}
    assert [item["sequence"] for item in budget.calls] == [1, 2]




def test_paid_failure_diagnostics_preserve_research_preacceptance_receipt():
    runtime = SimpleNamespace(
        semantic_resolution_receipts=(
            SemanticResolutionReceipt(
                source_ref="src_" + "a" * 24,
                handle_id="sem_" + "b" * 24,
                target_kind="metric",
            ),
        )
    )
    outcome = SimpleNamespace(
        preacceptance_status=SimpleNamespace(value="CLARIFICATION_REQUIRED"),
        observations=(
            {"kind": "intent_draft", "draft": {"obligations": [{"obligation_id": "U1"}]}},
            {"kind": "grounding", "summary": {"unresolved_source_refs": ["src_gap"]}},
            {
                "kind": "material_grounding_gap",
                "gaps": [{"obligation_id": "U1", "missing_required_kinds": ["metric"]}],
            },
        ),
    )
    research_lane = SimpleNamespace(
        last_result=SimpleNamespace(
            outcome=outcome,
            accepted_contract=None,
            ledger=None,
            runtime=runtime,
        )
    )
    standard_lane = SimpleNamespace(last_outcome=None)
    service = SimpleNamespace(query_calls=0, dry_plan_calls=0, cube_sql_calls=0)
    budget = paid.RoleCallBudget(
        max_total=paid.MAX_HARNESS_TOTAL_CALLS,
        role_limits=dict(paid.ROLE_LIMITS),
    )

    snapshot = paid._diagnostic_snapshot(
        product=None,
        standard_lane=standard_lane,
        research_lane=research_lane,
        budget=budget,
        service=service,
        structured_outputs=[],
    )

    assert snapshot["research"]["preacceptance_status"] == "CLARIFICATION_REQUIRED"
    assert [item["kind"] for item in snapshot["research"]["observations"]] == [
        "intent_draft",
        "grounding",
        "material_grounding_gap",
    ]
    assert snapshot["research"]["accepted_contract"] is None
    assert snapshot["research"]["ledger"] is None
    assert snapshot["research"]["semantic_resolution_receipts"][0]["target_kind"] == "metric"


def test_counting_structured_captures_research_and_semantic_schemas():
    class Inner:
        def structured_json(self, *args, **kwargs):
            return {"ok": True}

    captured = []
    budget = paid.RoleCallBudget(
        max_total=paid.MAX_HARNESS_TOTAL_CALLS,
        role_limits=dict(paid.ROLE_LIMITS),
    )
    for role, model, schema_name in (
        ("RESEARCH_MANAGER", paid.RESEARCH_MODEL, "dima_intent_draft_v1"),
        ("RESEARCH_MANAGER", paid.RESEARCH_MODEL, "dima_intent_coverage_v1"),
        ("RESEARCH_MANAGER", paid.RESEARCH_MODEL, "dima_research_manager_action_v1"),
        ("SEMANTIC_LINKER", paid.SEMANTIC_MODEL, "dima_bounded_semantic_link_v1"),
    ):
        paid.CountingStructured(
            inner=Inner(),
            budget=budget,
            role=role,
            model=model,
            captured_outputs=captured,
        ).structured_json("system", "user", schema={}, schema_name=schema_name)

    assert [item["schema_name"] for item in captured] == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
        "dima_research_manager_action_v1",
        "dima_bounded_semantic_link_v1",
    ]

def test_paid_failure_artifact_contract_includes_diagnostics():
    source = inspect.getsource(paid.main)
    assert '"diagnostics": getattr(exc, "diagnostics", {})' in source
    assert "CapturingStandardLane" in inspect.getsource(paid._build_product)



# ---------------------------------------------------------------------------
# Final/integrated certification oracle behavior. These cases intentionally do
# not assert one model/event trajectory; they certify typed lifecycle state.
# ---------------------------------------------------------------------------


def _adaptive_authority(
    *,
    trigger_verified=True,
    trigger_obligation="U1",
    branch_task="D1",
    parent_status=ObligationStatus.VERIFIED,
    parent_evidence_refs=("E1",),
):
    directive = ResearchDirective(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        condition=ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION,
        source_refs=("src_" + "1" * 24,),
    )
    ledger = UserObligationLedger(
        lineage_id="atl-oracle",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=parent_status,
                source_refs=("src_" + "1" * 24,),
                evidence_refs=tuple(parent_evidence_refs),
                introduced_in_version=1,
            ),
        ),
    )
    trigger = EvidenceArtifact(
        artifact_id="E1",
        task_id="seed:U1",
        obligation_ids=(trigger_obligation,),
        query_contract_refs=("QC1",),
        evidence_kind="standard_analytics",
        verified=trigger_verified,
    )
    branch = EvidenceArtifact(
        artifact_id="E2",
        task_id=branch_task,
        obligation_ids=("U1",),
        query_contract_refs=("QC2",),
        evidence_kind="standard_analytics",
        verified=True,
    )
    return directive, ledger, trigger, branch


@pytest.mark.parametrize("branch_task", ("D_INLINE", "D_MANAGER_SELECTED"))
def test_adaptive_applied_valid_for_multiple_execution_transports(branch_task):
    directive, ledger, trigger, branch = _adaptive_authority(branch_task=branch_task)
    disposition = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.APPLIED,
        evidence_ref="E1",
        branch_task_refs=(branch_task,),
        reason="governed material branch completed",
    )
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger, branch),
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
        diagnostic_observations=(),
    )
    assert certification.valid is True
    assert certification.lifecycle_outcome == "VALIDLY_ACCOUNTED"
    assert certification.certification_coverage == "COMPLETE"


def test_adaptive_no_material_direction_with_inspected_verified_parent_evidence_passes():
    directive, ledger, trigger, _ = _adaptive_authority()
    disposition = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION,
        evidence_ref="E1",
        reason="Verified evidence exposes no new material governed direction.",
    )
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger,),
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
    )
    assert certification.valid is True
    assert certification.branch_task_refs == ()
    assert certification.lifecycle_outcome == "VALIDLY_ACCOUNTED"


def test_adaptive_open_plus_verified_complete_is_genuine_failure():
    directive, ledger, trigger, _ = _adaptive_authority()
    disposition = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.OPEN,
    )
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger,),
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
    )
    assert certification.valid is False
    assert any("remained OPEN" in item for item in certification.errors)


def test_adaptive_applied_without_branch_refs_fails_even_if_shape_is_untyped():
    directive, ledger, trigger, _ = _adaptive_authority()
    disposition = SimpleNamespace(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.APPLIED,
        evidence_ref="E1",
        branch_task_refs=(),
        reason="invalid missing branch accounting",
    )
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger,),
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
    )
    assert certification.valid is False
    assert "APPLIED disposition lacks branch_task_refs" in certification.errors


@pytest.mark.parametrize("include_result,result_verified", ((False, True), (True, False)))
def test_adaptive_applied_missing_or_unverified_result_evidence_fails(
    include_result, result_verified
):
    directive, ledger, trigger, branch = _adaptive_authority()
    if not result_verified:
        branch = branch.model_copy(update={"verified": False})
    disposition = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.APPLIED,
        evidence_ref="E1",
        branch_task_refs=("D1",),
        reason="branch accounting",
    )
    items = (trigger, branch) if include_result else (trigger,)
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=items,
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
    )
    assert certification.valid is False


def test_adaptive_no_material_direction_with_branch_refs_fails():
    directive, ledger, trigger, branch = _adaptive_authority()
    disposition = SimpleNamespace(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION,
        evidence_ref="E1",
        branch_task_refs=("D1",),
        reason="invalid branch refs",
    )
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger, branch),
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
    )
    assert certification.valid is False
    assert "NO_MATERIAL_DIRECTION cannot carry branch_task_refs" in certification.errors


@pytest.mark.parametrize(
    ("trigger_verified", "trigger_obligation", "inspected"),
    (
        (False, "U1", ("E1",)),
        (True, "U_FOREIGN", ("E1",)),
        (True, "U1", ()),
    ),
)
def test_adaptive_no_material_direction_rejects_bad_evidence_provenance(
    trigger_verified, trigger_obligation, inspected
):
    directive, ledger, trigger, _ = _adaptive_authority(
        trigger_verified=trigger_verified,
        trigger_obligation=trigger_obligation,
    )
    disposition = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION,
        evidence_ref="E1",
        reason="bounded reason",
    )
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger,),
        ledger=ledger,
        inspected_evidence_refs=inspected,
        product_verified_complete=True,
    )
    assert certification.valid is False


def test_adaptive_blocked_is_typed_product_terminal_not_fake_applied():
    directive, ledger, _trigger, _ = _adaptive_authority(
        parent_status=ObligationStatus.BLOCKED_DATA_GAP,
        parent_evidence_refs=(),
    )
    disposition = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.BLOCKED,
        evidence_ref=None,
        reason="authoritative parent is blocked by governed data gap",
    )
    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(),
        ledger=ledger,
        inspected_evidence_refs=(),
        product_verified_complete=False,
    )
    assert certification.valid is True
    assert certification.lifecycle_outcome == "VALID_PRODUCT_TERMINAL"
    assert certification.certification_coverage == "CERTIFICATION_COVERAGE_INCOMPLETE"
    assert certification.disposition_status == "BLOCKED"
    assert certification.evidence_ref is None


def test_adaptive_diagnostic_event_names_do_not_change_authoritative_verdict():
    directive, ledger, trigger, _ = _adaptive_authority()
    disposition = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION,
        evidence_ref="E1",
        reason="no material new direction",
    )
    without_events = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger,),
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
        diagnostic_observations=(),
    )
    with_path_events = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(trigger,),
        ledger=ledger,
        inspected_evidence_refs=("E1",),
        product_verified_complete=True,
        diagnostic_observations=(
            {"kind": "adaptive_branch_executed"},
            {"kind": "adaptive_branch_opened"},
        ),
    )
    assert without_events.valid == with_path_events.valid
    assert without_events.lifecycle_outcome == with_path_events.lifecycle_outcome
    assert without_events.certification_coverage == with_path_events.certification_coverage


def test_day8_root_live_debt_oracle_does_not_require_adaptive_branch_trajectory():
    directive, ledger, bootstrap, next_test = _adaptive_authority(branch_task="D_NEXT")
    accepted_contract = SimpleNamespace(
        obligation_ids=("U1",),
        research_directives=(directive,),
    )
    finding = SimpleNamespace(
        finding_id="F1",
        parent_obligation_id="U1",
        epistemic_label=SimpleNamespace(value="CANDIDATE_CAUSE"),
        evidence_refs=("E2",),
        hypothesis_ref="H1",
    )
    observations = (
        {
            "kind": "hypothesis_registered",
            "result": {"hypothesis_id": "H1", "parent_obligation_id": "U1"},
        },
        {
            "kind": "hypothesis_next_test_executed",
            "result": {
                "hypothesis_id": "H1",
                "task_id": "D_NEXT",
                "evidence_ref": "E2",
            },
        },
        {
            "kind": "hypothesis_relation_admitted",
            "result": {
                "hypothesis_id": "H1",
                "evidence_links": [
                    {"evidence_ref": "E2", "relation": "SUPPORTS"}
                ],
            },
        },
    )
    certification = certify_day8_root_live_debt(
        accepted_contract=accepted_contract,
        ledger=ledger,
        evidence_items=(bootstrap, next_test),
        findings=(finding,),
        observations=observations,
    )
    assert certification.valid is True
    assert certification.root_obligation_id == "U1"
    assert certification.hypothesis_ref == "H1"
    assert certification.next_test_evidence_ref == "E2"
    assert certification.confirmed_cause_count == 0
    assert "adaptive_branch_executed" not in certification.diagnostic_observation_kinds



def _lineage_parity_ledger():
    src = "src_" + "9" * 24
    return UserObligationLedger(
        lineage_id="atl-lineage-parity",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U_PARENT",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=(src,),
                introduced_in_version=1,
            ),
            ObligationLedgerItem(
                obligation_id="U_CHILD",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.AGENT_DERIVED,
                parent_obligation_id="U_PARENT",
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=(src,),
                introduced_in_version=1,
            ),
            ObligationLedgerItem(
                obligation_id="U_GRANDCHILD",
                capability_key=ManagerCapabilityKey.COMPARISON,
                origin=ObligationOrigin.AGENT_DERIVED,
                parent_obligation_id="U_CHILD",
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=(src,),
                introduced_in_version=1,
            ),
            ObligationLedgerItem(
                obligation_id="U_SIBLING",
                capability_key=ManagerCapabilityKey.RELATIONSHIP,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=(src,),
                introduced_in_version=1,
            ),
            ObligationLedgerItem(
                obligation_id="U_OTHER_PARENT",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=(src,),
                introduced_in_version=1,
            ),
            ObligationLedgerItem(
                obligation_id="U_OTHER_CHILD",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.AGENT_DERIVED,
                parent_obligation_id="U_OTHER_PARENT",
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=(src,),
                introduced_in_version=1,
            ),
        ),
    )


@pytest.mark.parametrize(
    ("family", "evidence_obligation_ids", "expected"),
    (
        ("direct_parent", ("U_PARENT",), True),
        ("derived_child", ("U_CHILD",), True),
        ("multi_level_child", ("U_GRANDCHILD",), True),
        ("unrelated_sibling", ("U_SIBLING",), False),
        ("unknown_obligation", ("U_UNKNOWN",), False),
        ("wrong_parent", ("U_OTHER_CHILD",), False),
    ),
)
def test_eval_parent_lineage_mirror_has_exact_product_parity(
    family, evidence_obligation_ids, expected
):
    ledger = _lineage_parity_ledger()
    evidence = EvidenceArtifact(
        artifact_id=f"E_PARITY_{family}",
        task_id=f"T_PARITY_{family}",
        obligation_ids=evidence_obligation_ids,
        query_contract_refs=("QC_PARITY",),
        evidence_kind="standard_analytics",
        verified=True,
    )
    runtime = SimpleNamespace(ledger=ledger)

    product_answer = ResearchManagerLoop._evidence_belongs_to_parent_lineage(
        runtime=runtime,
        evidence=evidence,
        parent_obligation_id="U_PARENT",
    )
    eval_answer = evidence_belongs_to_parent_lineage(
        ledger=ledger,
        evidence=evidence,
        parent_obligation_id="U_PARENT",
    )

    assert product_answer is expected
    assert eval_answer is expected
    assert eval_answer is product_answer
