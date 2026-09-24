"""Provider-free contract for the manual D10-G17/G18 paid harness."""

from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.v2.product_models import ProductLane, ProductStatus
from app.v2.standard_lane import StandardLaneStatus
from lab import v2_day10_product_mvp_live as paid


def test_paid_harness_role_and_global_ceiling_are_hard_and_explicit():
    assert paid.MAX_HARNESS_TOTAL_CALLS == 20
    assert paid.ROLE_LIMITS == {
        "FAST_LANGUAGE": 2,
        "RESEARCH_MANAGER": 12,
        "SEMANTIC_LINKER": 3,
        "TEMPORAL_NORMALIZER": 1,
        "REPORT_NARRATOR": 2,
    }
    assert sum(paid.ROLE_LIMITS.values()) == paid.MAX_HARNESS_TOTAL_CALLS

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


def test_paid_harness_requires_final_root_directive_and_turn_contracts():
    source = inspect.getsource(paid.run_paid)

    assert "doğrulanmış sonuçlar yeni bir maddi" in paid.INITIAL_QUESTION
    assert '"adaptive_branch_executed"' in source
    assert "ProductEventKind.RELATIONSHIP_CHECKED" in source
    assert '"ADAPT_ON_EVIDENCE"' in source
    assert '"APPLIED"' in source
    assert "directive_accounting_evidence_ref" in source
    assert "directive_branch_task_refs" in source
    assert "initial_turn_ref" in source
    assert "continuation_turn_ref" in source
    assert "confirmed_cause_count != 0" in source
    assert "initial_evidence < 4" in source

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

    snapshot = paid._diagnostic_snapshot(
        product=product,
        standard_lane=standard_lane,
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
    assert snapshot["structured_standard_outputs"][0]["schema_name"] == (
        "dima_standard_intent_draft_v1"
    )
    assert snapshot["wren"] == {
        "query_calls": 0,
        "dry_plan_calls": 0,
        "cube_sql_calls": 0,
    }


def test_counting_structured_captures_only_controlled_standard_outputs():
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
        schema_name="not-a-controlled-standard-schema",
    )

    assert len(captured) == 1
    assert captured[0]["schema_name"] == "dima_standard_coverage_v1"
    assert captured[0]["validated_output"] == {"status": "PASS"}
    assert [item["sequence"] for item in budget.calls] == [1, 2]


def test_paid_failure_artifact_contract_includes_diagnostics():
    source = inspect.getsource(paid.main)
    assert '"diagnostics": getattr(exc, "diagnostics", {})' in source
    assert "CapturingStandardLane" in inspect.getsource(paid._build_product)

