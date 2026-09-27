from __future__ import annotations

from app.v3.research_manager import (
    InvestigationGainRequirement,
    ResearchReasoningBudget,
)


def test_v1_p17_depth_contract_is_one_based_and_hard_capped():
    budget = ResearchReasoningBudget()
    assert budget.max_depth == 3
    assert ResearchReasoningBudget.model_fields["max_depth"].metadata


def test_v1_gain_requirement_is_typed_not_numeric_confidence():
    assert tuple(InvestigationGainRequirement) == (
        InvestigationGainRequirement.NONE,
        InvestigationGainRequirement.POSITIVE_EXPECTED_GAIN,
    )
