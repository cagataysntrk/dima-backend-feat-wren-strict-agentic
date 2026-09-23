"""Server-authored Day10 ProductEvent sink.

Events describe governed state transitions only. They never contain model reasoning,
raw tool payloads, SQL, or provider messages.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable

from app.v2.product_models import ProductEvent, ProductEventKind


_DISPLAY = {
    ProductEventKind.REQUEST_ACCEPTED: "İstek kabul edildi",
    ProductEventKind.LANE_SELECTED: "Analiz yolu seçildi",
    ProductEventKind.RESEARCH_STARTED: "Analiz başladı",
    ProductEventKind.EVIDENCE_VERIFIED: "Doğrulanmış sonuç hazır",
    ProductEventKind.ADAPTIVE_BRANCH_OPENED: "Yeni analiz dalı açıldı",
    ProductEventKind.RELATIONSHIP_CHECKED: "İlişki analizi tamamlandı",
    ProductEventKind.ROOT_CAUSE_CANDIDATE: "Aday neden araştırması doğrulandı",
    ProductEventKind.ARTIFACT_READY: "Rapor bileşeni hazır",
    ProductEventKind.DATA_GAP: "Veri kısıtı kaydedildi",
    ProductEventKind.REPORT_READY: "Rapor hazır",
    ProductEventKind.PARTIAL_READY: "Mevcut doğrulanmış sonuçlar hazır",
    ProductEventKind.KEEPALIVE: "İşlem devam ediyor",
    ProductEventKind.TERMINAL: "İşlem tamamlandı",
}


def _event_id(
    *,
    request_ref: str,
    kind: ProductEventKind,
    refs: tuple[str, ...],
    transition_ref: str,
) -> str:
    raw = json.dumps(
        {
            "request_ref": request_ref,
            "kind": kind.value,
            "refs": refs,
            "transition_ref": transition_ref,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return "pevt_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class ProductEventSink:
    """Idempotent in-memory event accumulator for one product request."""

    def __init__(
        self,
        *,
        request_ref: str,
        clock: Callable[[], float] = time.monotonic,
        on_event: Callable[[ProductEvent], None] | None = None,
    ) -> None:
        self._request_ref = request_ref
        self._clock = clock
        self._started = clock()
        self._on_event = on_event
        self._events: list[ProductEvent] = []
        self._by_id: dict[str, ProductEvent] = {}

    @property
    def events(self) -> tuple[ProductEvent, ...]:
        return tuple(self._events)

    def emit(
        self,
        kind: ProductEventKind,
        *,
        refs: tuple[str, ...] = (),
        transition_ref: str,
    ) -> ProductEvent:
        canonical_refs = tuple(dict.fromkeys(str(ref) for ref in refs if ref))
        event_id = _event_id(
            request_ref=self._request_ref,
            kind=kind,
            refs=canonical_refs,
            transition_ref=transition_ref,
        )
        prior = self._by_id.get(event_id)
        if prior is not None:
            return prior

        event = ProductEvent(
            event_id=event_id,
            sequence=len(self._events) + 1,
            kind=kind,
            elapsed_ms=max(0, int((self._clock() - self._started) * 1000)),
            refs=canonical_refs,
            display_text=_DISPLAY[kind],
        )
        self._events.append(event)
        self._by_id[event_id] = event
        if self._on_event is not None:
            self._on_event(event)
        return event
