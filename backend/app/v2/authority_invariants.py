"""Pure shared authority invariants used by Product and certification.

These helpers project existing typed authority only. They do not create semantic,
Evidence, obligation, completion, or epistemic truth.
"""

from __future__ import annotations


def evidence_belongs_to_parent_lineage(
    *,
    ledger,
    evidence,
    parent_obligation_id: str,
) -> bool:
    """Return whether Evidence belongs to parent or one of its derived descendants."""

    if ledger is None or evidence is None:
        return False
    by_id = {
        str(item.obligation_id): item
        for item in (getattr(ledger, "items", ()) or ())
        if getattr(item, "obligation_id", None)
    }
    for obligation_id in (getattr(evidence, "obligation_ids", ()) or ()):
        current = str(obligation_id)
        seen: set[str] = set()
        while current not in seen:
            if current == str(parent_obligation_id):
                return True
            seen.add(current)
            item = by_id.get(current)
            if item is None:
                break
            parent = getattr(item, "parent_obligation_id", None)
            if parent is None:
                break
            current = str(parent)
    return False
