"""Shared scripted-manager adapter for provider-free tests.

Tests may describe intent using the historical ManagerDecisionTransport shape, but the
Product only receives the current ManagerActionSet action_ref + cognitive payload.
This module is test-only and must never be imported by app/v2.
"""

from __future__ import annotations

from typing import Any


def _cards(payload: dict[str, Any], action: str) -> list[dict[str, Any]]:
    action_set = payload.get("MANAGER_ACTION_SET") or {}
    rows = action_set.get("action_instances") or []
    return [row for row in rows if row.get("action") == action]


def adapt_legacy_manager_intent(
    payload: dict[str, Any],
    legacy: dict[str, Any],
) -> dict[str, Any]:
    action = str(legacy["action"])
    cards = _cards(payload, action)
    if not cards:
        raise AssertionError(f"scripted intent action is not executable: {action}")

    # Narrow genuinely different legal instances using non-canonical cognition context.
    task_family = legacy.get("next_test_task_kind")
    if task_family is not None:
        matching = [
            row
            for row in cards
            if (row.get("context") or {}).get("task_family") == task_family
        ]
        if matching:
            cards = matching

    capability = legacy.get("derived_capability_key")
    if capability is not None:
        matching = [
            row
            for row in cards
            if (row.get("context") or {}).get("capability") == capability
        ]
        if matching:
            cards = matching

    if action == "propose_branches":
        requested = {
            str(item.get("capability_key"))
            for item in (legacy.get("branch_candidates") or ())
        }
        matching = [
            row
            for row in cards
            if requested.issubset(
                set((row.get("context") or {}).get("capability_choices") or ())
            )
        ]
        if matching:
            cards = matching

    cards = sorted(cards, key=lambda row: str(row["action_ref"]))
    card = cards[0]
    fields = set(card.get("cognitive_fields") or ())
    choice: dict[str, Any] = {"action_ref": card["action_ref"]}

    if "semantic_proposal" in fields:
        choice["semantic_proposal"] = legacy["semantic_proposal"]
    if "target_kind_hint" in fields:
        hints = legacy.get("target_kind_hints") or ()
        if len(hints) != 1:
            raise AssertionError("scripted semantic intent requires one target kind")
        choice["target_kind_hint"] = hints[0]
    if "branch_candidates" in fields:
        choice["branch_candidates"] = [
            {
                "capability_key": item["capability_key"],
                "material_reason": item["material_reason"],
            }
            for item in (legacy.get("branch_candidates") or ())
        ]
    if "directive_reason" in fields:
        choice["directive_reason"] = legacy["directive_reason"]
    if "hypothesis_statement" in fields:
        choice["hypothesis_statement"] = legacy["hypothesis_statement"]
    if "hypothesis_limitations" in fields:
        choice["hypothesis_limitations"] = list(
            legacy.get("hypothesis_limitations") or ()
        )
    if "hypothesis_relation" in fields:
        choice["hypothesis_relation"] = legacy["hypothesis_relation"]
    if "next_test_material_reason" in fields:
        choice["next_test_material_reason"] = legacy[
            "next_test_material_reason"
        ]
    if "next_test_ranking_direction" in fields:
        choice["next_test_ranking_direction"] = legacy.get(
            "next_test_ranking_direction"
        )
    if "next_test_ranking_limit" in fields:
        choice["next_test_ranking_limit"] = legacy.get(
            "next_test_ranking_limit"
        )
    if "ranking_direction" in fields:
        choice["ranking_direction"] = legacy.get("ranking_direction")
    if "ranking_limit" in fields:
        choice["ranking_limit"] = legacy.get("limit")
    if "clarification_reason" in fields:
        choice["clarification_reason"] = legacy["clarification_reason"]

    if set(choice) != {"action_ref", *fields}:
        missing = fields - set(choice)
        raise AssertionError(
            f"scripted intent adapter missing cognitive fields: {sorted(missing)}"
        )
    return {"choice": choice}


def choose_action(
    payload: dict[str, Any],
    action: str,
    **cognitive: Any,
) -> dict[str, Any]:
    legacy = {"action": action, **cognitive}
    return adapt_legacy_manager_intent(payload, legacy)
