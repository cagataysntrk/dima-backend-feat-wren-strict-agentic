"""Provider-free D10-C typed product event contracts."""

from __future__ import annotations

from app.v2.product_events import ProductEventSink
from app.v2.product_models import ProductEventKind


class _Clock:
    def __init__(self):
        self.value = 100.0

    def __call__(self):
        return self.value

    def advance(self, seconds: float):
        self.value += seconds


def test_equivalent_governed_transition_replays_same_event_identity():
    clock = _Clock()
    sink = ProductEventSink(request_ref="req-1", turn_ref="turn-1", clock=clock)

    first = sink.emit(
        ProductEventKind.EVIDENCE_VERIFIED,
        refs=("E1",),
        transition_ref="evidence:E1",
    )
    clock.advance(5)
    replay = sink.emit(
        ProductEventKind.EVIDENCE_VERIFIED,
        refs=("E1",),
        transition_ref="evidence:E1",
    )

    assert replay == first
    assert replay.event_id == first.event_id
    assert replay.sequence == 1
    assert replay.elapsed_ms == first.elapsed_ms
    assert len(sink.events) == 1


def test_product_event_sequence_is_server_authored_and_monotonic():
    clock = _Clock()
    seen = []
    sink = ProductEventSink(
        request_ref="req-2",
        turn_ref="turn-2",
        clock=clock,
        on_event=seen.append,
    )

    accepted = sink.emit(
        ProductEventKind.REQUEST_ACCEPTED,
        refs=("req-2",),
        transition_ref="frontdoor:bound",
    )
    clock.advance(0.25)
    evidence = sink.emit(
        ProductEventKind.EVIDENCE_VERIFIED,
        refs=("E1",),
        transition_ref="evidence:E1",
    )
    clock.advance(0.5)
    terminal = sink.emit(
        ProductEventKind.TERMINAL,
        refs=("REPORT",),
        transition_ref="terminal:REPORT",
    )

    assert [item.sequence for item in sink.events] == [1, 2, 3]
    assert [item.kind for item in seen] == [
        ProductEventKind.REQUEST_ACCEPTED,
        ProductEventKind.EVIDENCE_VERIFIED,
        ProductEventKind.TERMINAL,
    ]
    assert accepted.elapsed_ms == 0
    assert evidence.elapsed_ms == 250
    assert terminal.elapsed_ms == 750


def test_event_surface_contains_no_reasoning_or_raw_tool_payload_fields():
    fields = set(ProductEventSink(
        request_ref="req-3",
        turn_ref="turn-3",
    ).emit(
        ProductEventKind.KEEPALIVE,
        transition_ref="keepalive:1",
    ).model_dump())

    assert fields == {
        "event_id",
        "sequence",
        "kind",
        "elapsed_ms",
        "refs",
        "display_text",
    }
    assert "reasoning" not in fields
    assert "sql" not in fields
    assert "tool_payload" not in fields
    assert "provider_message" not in fields


def test_same_correlation_fingerprint_has_distinct_turn_scoped_event_identity():
    first = ProductEventSink(
        request_ref="same-request-fingerprint",
        turn_ref="turn-first",
    )
    second = ProductEventSink(
        request_ref="same-request-fingerprint",
        turn_ref="turn-second",
    )

    a = first.emit(
        ProductEventKind.REQUEST_ACCEPTED,
        refs=("same-request-fingerprint",),
        transition_ref="frontdoor:bound",
    )
    b = second.emit(
        ProductEventKind.REQUEST_ACCEPTED,
        refs=("same-request-fingerprint",),
        transition_ref="frontdoor:bound",
    )

    assert first.request_ref == second.request_ref
    assert first.turn_ref != second.turn_ref
    assert a.event_id != b.event_id

    replay = first.emit(
        ProductEventKind.REQUEST_ACCEPTED,
        refs=("same-request-fingerprint",),
        transition_ref="frontdoor:bound",
    )
    assert replay.event_id == a.event_id
    assert replay.sequence == a.sequence
