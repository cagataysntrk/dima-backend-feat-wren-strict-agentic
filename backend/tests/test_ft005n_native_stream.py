from __future__ import annotations

import importlib.util
import json
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "lab"
    / "ft005n"
    / "native_stream.py"
)
SPEC = importlib.util.spec_from_file_location("ft005n_native_stream", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

NativeTurn = MODULE.NativeTurn
NativeMetabotSession = MODULE.NativeMetabotSession
apply_stream_line = MODULE.apply_stream_line
digest = MODULE.digest


def make_turn():
    return NativeTurn(
        question="Q",
        conversation_id="00000000-0000-0000-0000-000000000001",
        profile_id="nlq",
        input_history_count=0,
        input_state_digest=digest({}),
    )


def test_native_stream_parser_recovers_text_tools_state_and_finish():
    turn = make_turn()
    lines = [
        'f:{"messageId":"m1"}',
        '0:"Analiz "',
        '9:{"toolCallId":"tc1","toolName":"nlq_search","args":"{\"query\":\"sales\"}"}',
        'a:{"toolCallId":"tc1","result":{"ok":true}}',
        '2:{"type":"state","version":1,"value":{"query":{"id":"q1"}}}',
        '0:"tamam."',
        'd:{"finishReason":"stop"}',
    ]
    for line in lines:
        apply_stream_line(turn, line)

    assert turn.text == "Analiz tamam."
    assert turn.tool_sequence == ["nlq_search"]
    assert len(turn.tool_calls) == 1
    assert len(turn.tool_results) == 1
    assert turn.state == {"query": {"id": "q1"}}
    assert turn.finish_reason == "stop"
    assert turn.errors == []
    assert turn.response_history == [
        {"role": "assistant", "content": "Analiz "},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "tc1",
                    "name": "nlq_search",
                    "arguments": '{"query":"sales"}',
                }
            ],
        },
        {
            "role": "tool",
            "content": {"ok": True},
            "tool_call_id": "tc1",
        },
        {"role": "assistant", "content": "tamam."},
    ]


def test_native_stream_parser_records_invalid_json_without_reasoning_capture():
    turn = make_turn()
    apply_stream_line(turn, "2:not-json")
    assert turn.errors[0]["class"] == "STREAM_PARSE_ERROR"
    assert "not-json" not in json.dumps(turn.receipt())
    assert turn.receipt()["private_reasoning_recorded"] is False


def test_frontend_style_history_carry_forward_contract():
    prior = [
        {"role": "user", "content": "Q1"},
        {"role": "assistant", "content": "A1"},
    ]
    response_history = [
        {"role": "assistant", "content": "A2"},
    ]
    question = "Q2"
    expected = [
        *prior,
        {"role": "user", "content": question},
        *response_history,
    ]
    assert expected[-2:] == [
        {"role": "user", "content": "Q2"},
        {"role": "assistant", "content": "A2"},
    ]


def test_unknown_stream_prefix_is_ignored():
    turn = make_turn()
    apply_stream_line(turn, 'x:{"private":"ignored"}')
    assert turn.receipt()["tool_call_count"] == 0
    assert turn.text == ""
    assert turn.errors == []
