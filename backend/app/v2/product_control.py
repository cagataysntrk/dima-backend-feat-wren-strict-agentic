"""Ephemeral Day10 live-run control signals.

This is transport coordination only, never Research truth. ManagerRuntime/UOL/Evidence
remain the sole run/completion authorities. Entries exist only while a live stream is
attached to one process and are removed when that stream closes.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from enum import StrEnum


class ProductControlAction(StrEnum):
    ANSWER_NOW = "ANSWER_NOW"
    CANCEL = "CANCEL"


class ProductControlError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProductRunControl:
    control_ref: str
    principal_subject: str
    tenant_binding: str
    _answer_now: threading.Event
    _cancel: threading.Event

    def answer_now_requested(self) -> bool:
        return self._answer_now.is_set()

    def cancelled(self) -> bool:
        return self._cancel.is_set()

    def signal(self, action: ProductControlAction) -> None:
        if action == ProductControlAction.ANSWER_NOW:
            self._answer_now.set()
        elif action == ProductControlAction.CANCEL:
            self._cancel.set()
        else:  # pragma: no cover - enum validation owns external shape
            raise ProductControlError(f"unsupported Product control action: {action}")


class ProductRunControlRegistry:
    """Bounded live-signal registry with principal + tenant isolation."""

    def __init__(self, *, max_active: int = 128) -> None:
        if max_active < 1:
            raise ValueError("max_active must be >= 1")
        self._max_active = max_active
        self._lock = threading.Lock()
        self._items: dict[str, ProductRunControl] = {}

    def register(
        self,
        *,
        principal_subject: str,
        tenant_binding: str,
    ) -> ProductRunControl:
        if not principal_subject or not tenant_binding:
            raise ProductControlError("live Product control requires principal + tenant")
        with self._lock:
            if len(self._items) >= self._max_active:
                raise ProductControlError("live Product control capacity exhausted")
            while True:
                control_ref = "prun_" + uuid.uuid4().hex[:24]
                if control_ref not in self._items:
                    break
            entry = ProductRunControl(
                control_ref=control_ref,
                principal_subject=principal_subject,
                tenant_binding=tenant_binding,
                _answer_now=threading.Event(),
                _cancel=threading.Event(),
            )
            self._items[control_ref] = entry
            return entry

    def resolve(
        self,
        control_ref: str,
        *,
        principal_subject: str,
        tenant_binding: str,
    ) -> ProductRunControl:
        with self._lock:
            entry = self._items.get(control_ref)
        if entry is None:
            raise ProductControlError("live Product control not found")
        if (
            entry.principal_subject != principal_subject
            or entry.tenant_binding != tenant_binding
        ):
            # Do not disclose whether another principal/tenant owns this live control.
            raise ProductControlError("live Product control not found")
        return entry

    def signal(
        self,
        control_ref: str,
        *,
        principal_subject: str,
        tenant_binding: str,
        action: ProductControlAction,
    ) -> ProductRunControl:
        entry = self.resolve(
            control_ref,
            principal_subject=principal_subject,
            tenant_binding=tenant_binding,
        )
        entry.signal(action)
        return entry

    def release(self, control_ref: str) -> None:
        with self._lock:
            self._items.pop(control_ref, None)
