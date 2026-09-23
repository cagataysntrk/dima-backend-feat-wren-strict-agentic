# FT-005N FAILURE RECEIPT — NATIVE_STREAM_FIXTURE_ESCAPE_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-23

Observed run:
`35821123681`

Observed SHA:
`8ba96258f5291caa4adc177f53b2d1117e68e14c`

Failed gate:
`provider-free / Lock native stream parser`

Live A1 job:
`SKIPPED`

Failure class:
`EVAL_ORACLE_FIXTURE_CONTRACT`

## Evidence

Three provider-free parser tests passed.

One failed:

`test_native_stream_parser_recovers_text_tools_state_and_finish`

The test fixture encoded a tool-call stream line with an `args` string whose inner JSON quotes
were consumed by the Python string literal before the parser saw it.

Runtime fixture effectively became malformed JSON:

```text
9:{"toolCallId":"tc1","toolName":"nlq_search","args":"{"query":"sales"}"}
```

The parser correctly rejected that line, therefore no tool was appended.

## Root cause

Test fixture escaping, not:
- native stream parser semantics;
- Metabase;
- OpenRouter;
- native endpoint;
- Fast product code.

No live model or Metabase native behavior was measured by this run.

## Authorized patch

Owner:
`backend/tests/test_ft005n_native_stream.py`

Replace the malformed fixture with a valid AI-stream tool-call line.

Do not change:
- parser behavior;
- production Fast code;
- native endpoint payload;
- corpus;
- Metabase config.

## Re-proof

Provider-free parser must be 4/4 GREEN before the A1 live job executes.
