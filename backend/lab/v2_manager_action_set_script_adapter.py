"""Shared scripted-manager adapter for provider-free lab/tests.

Tests may describe intent using the historical ManagerDecisionTransport shape, but the
Product only receives the current ManagerActionSet action_ref + cognitive payload.
This module is lab/test-only and must never be imported by app/v2.
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
        if not matching:
            raise AssertionError(
                f"scripted intent task family is not executable: {task_family}"
            )
        cards = matching

    capability = legacy.get("derived_capability_key")
    if capability is not None:
        matching = [
            row
            for row in cards
            if (row.get("context") or {}).get("capability") == capability
        ]
        if not matching:
            raise AssertionError(
                f"scripted intent capability is not executable: {capability}"
            )
        cards = matching

    def ledger_capability(obligation_id: str | None) -> str | None:
        if not obligation_id:
            return None
        for item in payload.get("OBLIGATION_LEDGER") or ():
            if str(item.get("obligation_id")) == str(obligation_id):
                value = item.get("capability")
                return str(value) if value is not None else None
        return None

    if action == "inspect_evidence" and legacy.get("evidence_ref"):
        requested_ref = str(legacy["evidence_ref"])
        requested_caps = {
            str(item.get("capability"))
            for item in payload.get("OBLIGATION_LEDGER") or ()
            if requested_ref in set(item.get("evidence_refs") or ())
            and item.get("capability") is not None
        }
        if requested_caps:
            matching = [
                row
                for row in cards
                if requested_caps.intersection(
                    set((row.get("context") or {}).get("capabilities") or ())
                )
            ]
            if not matching:
                raise AssertionError(
                    f"scripted evidence intent is not executable: {requested_ref}"
                )
            cards = matching

    if action in {"propose_branches", "resolve_semantics"}:
        parent_id = (
            legacy.get("branch_parent_obligation_id")
            if action == "propose_branches"
            else legacy.get("semantic_parent_obligation_id")
        )
        parent_capability = ledger_capability(parent_id)
        if parent_capability is not None:
            matching = [
                row
                for row in cards
                if (row.get("context") or {}).get("parent_capability")
                == parent_capability
            ]
            if not matching:
                raise AssertionError(
                    "scripted parent capability has no legal ActionInstance: "
                    f"{parent_capability}"
                )
            cards = matching

    if action in {"run_analytics", "run_relationship"}:
        requested_ids = (
            legacy.get("obligation_ids")
            if action == "run_analytics"
            else [legacy.get("relationship_obligation_id")]
        ) or []
        requested_id = str(requested_ids[0]) if len(requested_ids) == 1 else None
        if requested_id:
            ledger_item = next(
                (
                    item
                    for item in payload.get("OBLIGATION_LEDGER") or ()
                    if str(item.get("obligation_id")) == requested_id
                ),
                None,
            )
            if ledger_item is not None:
                target_aliases = {
                    str(value)
                    for value in (ledger_item.get("semantic_handle_refs") or ())
                }
                target_surfaces: set[str] = set()
                for row in payload.get("GOVERNED_SEMANTIC_INVENTORY") or ():
                    if str(row.get("handle_ref")) not in target_aliases:
                        continue
                    target_surfaces.update(
                        str(value)
                        for value in (row.get("source_surfaces") or ())
                        if str(value).strip()
                    )
                if target_surfaces:
                    matching = [
                        row
                        for row in cards
                        if target_surfaces.intersection(
                            {
                                str(value)
                                for value in (
                                    (row.get("context") or {}).get(
                                        "semantic_context"
                                    ) or ()
                                )
                            }
                        )
                    ]
                    if not matching:
                        raise AssertionError(
                            "scripted analytical intent has no matching semantic context"
                        )
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
        if not matching:
            raise AssertionError(
                "scripted branch capability set is not executable: "
                + ",".join(sorted(requested))
            )
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
