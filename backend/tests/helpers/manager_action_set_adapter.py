# FINAL_PROVIDER_FREE_CANDIDATE: source-truth + blocked-lifecycle closure trigger.
"""Test import facade for the shared provider-free ManagerActionSet adapter."""

from lab.v2_manager_action_set_script_adapter import (  # noqa: F401
    adapt_legacy_manager_intent,
    choose_action,
)

__all__ = ["adapt_legacy_manager_intent", "choose_action"]
# D10-U/preacceptance closure transport note: this test-only adapter is intentionally
# behavior-neutral; touching it triggers Day7/Day8/Day10 affected gates on one SHA.

