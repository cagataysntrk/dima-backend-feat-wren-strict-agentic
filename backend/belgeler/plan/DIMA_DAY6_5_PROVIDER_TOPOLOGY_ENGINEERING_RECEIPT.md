# DIMA DAY 6.5 — PROVIDER TOPOLOGY ENGINEERING RECEIPT

**Status:** ENGINEERING TOPOLOGY SELECTED / NOT PRODUCTION ACTIVATED  
**Date:** 2026-09-22  
**Frozen family corpus:** `eval/v2_day6_5_j1b_real_flow_frozen.json`  
**Frozen blob:** `cc68f87271dcaada1443d2cf9e48024b85bff9f3`

## Evidence

### Luna same-frozen control

Run `35716056419`, tested SHA
`c256ebfda765ac35f1d3b51f59d53d1018dd695e`.

```text
semantic 20/20
silent_semantic_wrong        0
unsafe_ambiguity_auto_pick   0
candidate_escape             0
cross_tenant_leak            0
provider_failure             0
invalid_typed_contract       0

temporal 6/8
real_flow_temporal_wrong     2
provider_failure             0
invalid_typed_contract       0
```

### Sol temporal exact-same-SHA ceiling

Run `35716502261`.

Workflow explicitly checked out the exact Luna-tested backend SHA
`c256ebfda765ac35f1d3b51f59d53d1018dd695e`.

```text
model                         openai/gpt-5.6-sol
reasoning                     enabled
same frozen scenarios         8
correct                       8/8
real_flow_temporal_wrong      0
invalid_typed_contract        0
provider_failure              0
hidden_fallback               0
calls                         10
measured cost                 $0.020918
p50 latency                   ~2.421s
```

## Failure classification closure

The two previous-period-comparison failures appeared under both Terra and Luna but disappeared
under Sol on the exact same backend SHA and same frozen scenarios.

Therefore for this measured family:

```text
primary owner =
MODEL_CAPABILITY_FLOOR / MODEL_COGNITION

shared temporal architecture bug =
NOT SUPPORTED by the exact-SHA A/B evidence
```

No temporal product/prompt/schema patch is authorized or required from this evidence.

## Chosen Day 6.5 engineering topology

```text
SEMANTIC_LINKER      = openai/gpt-5.6-luna
TEMPORAL_NORMALIZER  = openai/gpt-5.6-sol
RESEARCH_MANAGER     = openai/gpt-5.6-sol

SemanticBindingGate   = UNCHANGED deterministic authority
TemporalBindingEngine = UNCHANGED deterministic calendar authority
Wren semantic backbone= RETAIN
fallback              = NONE
cascade               = NONE
confidence threshold  = NONE
```

This topology is the input topology for D65-SI only.
It is **not** production activation or final release model seal.

## Deferred/rejected

```text
Jev AS-IS semantic             REJECT current critical path
Jev temporal                   REJECT
Jev verifier/calibration       POST-MVP candidate
Terra temporal                 NOT selected after real-flow RED
Gemini automatic rerun         NO
J1/J1B-derived threshold       FORBIDDEN
```

## Next gate

Provider topology P0 requirement is satisfied.

D65-SI may start only after the current M0E capability-exhaustion/build-vs-buy completion gate is
sufficiently closed according to its exit criteria.
