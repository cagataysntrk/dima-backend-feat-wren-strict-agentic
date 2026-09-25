"""Test import facade for the shared provider-free ManagerActionSet adapter."""

from lab.v2_manager_action_set_script_adapter import (  # noqa: F401
    adapt_legacy_manager_intent,
    choose_action,
)

__all__ = ["adapt_legacy_manager_intent", "choose_action"]
