"""Generic progress accounting and dynamic action frontier for Manager loops."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _plain(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return _plain(value.model_dump(mode="json"))
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _digest(value: Any) -> str:
    blob = json.dumps(
        _plain(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def action_fingerprint(action: Any) -> str:
    return "act_" + _digest(action)[:20]


def result_fingerprint(result: Any) -> str:
    return "res_" + _digest(result)[:20]


def progress_fingerprint(runtime, *, knowledge_fingerprints: set[str]) -> str:
    ledger = runtime.ledger
    contract = runtime.accepted_contract
    payload = {
        "state": runtime.snapshot.state.value,
        "terminal_status": (
            runtime.snapshot.terminal_status.value
            if runtime.snapshot.terminal_status is not None
            else None
        ),
        "accepted_contract_id": runtime.snapshot.accepted_contract_id,
        "contract_version": getattr(contract, "version", None),
        "ledger": (
            ledger.model_dump(mode="json")
            if ledger is not None
            else None
        ),
        "evidence_refs": list(runtime.snapshot.evidence_refs),
        "semantic_receipts": [
            item.model_dump(mode="json")
            for item in runtime.semantic_resolution_receipts
        ],
        "knowledge": sorted(knowledge_fingerprints),
    }
    return "prog_" + _digest(payload)[:20]


@dataclass
class DynamicActionFrontier:
    """Block only exact actions proven to make no progress in the current epoch."""

    known_results: set[str] = field(default_factory=set)
    blocked_by_progress: dict[str, dict[str, dict[str, Any]]] = field(
        default_factory=dict
    )

    def progress(self, runtime) -> str:
        return progress_fingerprint(
            runtime,
            knowledge_fingerprints=self.known_results,
        )

    def blocked(self, *, progress: str, action: Any) -> bool:
        fingerprint = action_fingerprint(action)
        return fingerprint in self.blocked_by_progress.get(progress, {})

    def observe(
        self,
        *,
        progress_before: str,
        action: Any,
        runtime,
        result: Any,
    ) -> bool:
        """Return True when state/knowledge progressed; otherwise block exact action."""
        action_fp = action_fingerprint(action)
        result_fp = result_fingerprint(result)
        result_was_known = result_fp in self.known_results
        self.known_results.add(result_fp)
        progress_after = self.progress(runtime)
        progressed = progress_after != progress_before
        if not progressed and result_was_known:
            self.blocked_by_progress.setdefault(progress_after, {})[action_fp] = {
                "fingerprint": action_fp,
                "action": _plain(action),
            }
            return False
        return True

    def view(self, runtime) -> dict[str, Any]:
        progress = self.progress(runtime)
        blocked = list(self.blocked_by_progress.get(progress, {}).values())
        return {
            "progress_fingerprint": progress,
            "blocked_exact_actions": blocked,
        }
