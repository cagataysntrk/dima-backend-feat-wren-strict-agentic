# DIMA DAY 6.5 — J1B REAL-FLOW RECEIPT

**Status:** RED / CONSULTATION REQUIRED  
**Run:** `35713785149`  
**Tested SHA:** `09c9128bd385a83c099b18855636b703d73bec48`  
**Corpus:** `eval/v2_day6_5_j1b_real_flow_frozen.json`  
**Corpus freeze commit:** `a4cdbd5c9d7054fa3823a75f91cced3c1df943d2`  
**Workers:** 1  
**Fallback/cascade/threshold:** NONE

## Provider-free precondition

The live workflow ran compile + focused provider-free proof first.

Prior J1B contract gate:
`35711431142 = 57/57 PASS`.

The real-flow workflow's provider-free step also passed before paid calls.

## Real governed path under test

Semantic:

```text
real source span
→ ManagerSemanticResolutionAdapter
→ SemanticCandidateGenerator
→ JevDecisionProvider
→ SemanticBindingGate
→ sem_* handle
```

Temporal:

```text
real temporal source span
→ ManagerSemanticResolutionAdapter
→ StructuredTemporalNormalizationProvider(Terra)
→ typed TemporalNormalizationChoice
→ TemporalBindingEngine
→ period/comparison sem_* handle
```

No production route was activated.

## Semantic result — Jev

```text
cases                       20
correct                     12
silent semantic wrong        8
unsafe ambiguity auto-pick   8
candidate escape             0
cross-tenant leak            0
provider failures            0
hidden fallback              0
```

Family accuracy:

```text
ambiguous_generic_metric          50.0%
multiple_plausible_candidate      33.3%
under_specified_measure           20.0%
partial_business_alias_unique    100.0%
unique_paraphrase                100.0%
```

Silent-wrong examples:

| Surface | Expected | Selected | Confidence |
|---|---|---|---:|
| gelir | ABSTAIN | sales.net_revenue | 0.49 |
| marj | ABSTAIN | finance.gross_margin | 0.45 |
| müşteri geliri | ABSTAIN | sales.avg_customer_revenue | **0.93** |
| satış geliri | ABSTAIN | sales.net_revenue | 0.44 |
| adet | ABSTAIN | sales.units_sold | 0.64 |
| miktar | ABSTAIN | sales.units_sold | 0.68 |
| ortalama | ABSTAIN | sales.avg_customer_revenue | 0.58 |
| net sonuç | ABSTAIN | sales.net_revenue | **0.86** |

This is not candidate escape; the model selected valid candidates inside the bounded set.
Therefore `SemanticBindingGate` correctly enforces authority shape but cannot detect these
candidate-set-internal semantic mistakes.

Important calibration evidence:
a simple confidence threshold cannot be inferred from this corpus and would not obviously solve
the problem because at least two silent wrongs are high-confidence (0.93 and 0.86).

Per authority:
`Jev production semantic provider = NOT ACCEPTABLE AS-IS`.

## Temporal result — Terra

```text
scenarios                   8
correct                     6
wrong                       2
provider failures           0
hidden fallback             0
Terra calls                10
measured cost              $0.020284
p50 call latency           ~1.563s
```

Failures:

```text
"bu ay" + "önceki dönemle karşılaştır"
→ period resolved; comparison unresolved

"son 30 günü" + "önceki dönemle karşılaştır"
→ period resolved; comparison unresolved
```

The same Terra candidate had previously achieved 34/34 J1T-CHOICE and 34/34 contract fidelity
on run `35710080143`. The real-flow failure has no transport/provider error and therefore is
provisionally classified:

```text
MODEL_COGNITION / REAL_FLOW_TEMPORAL_INSTABILITY
```

The current real-flow artifact does not retain the exact rejected typed choice payload, so exact
choice-level root cause is not asserted beyond that boundary.

## P0 result

```text
silent_semantic_wrong       8   FAIL
unsafe_ambiguity_auto_pick  8   FAIL
candidate_escape            0   PASS
cross_tenant_leak           0   PASS
hidden_fallback             0   PASS
provider_failure            0   PASS
temporal_wrong              2   FAIL
```

## Decision

```text
J1B = RED
D65-SI = BLOCKED
real Standard Wren sentinel = NOT STARTED
X0 execution = BLOCKED
production /ask-v2 = OFF
DEV80 = FORBIDDEN
```

No named-case patch, prompt micro-patch, regex, threshold, fallback, cascade or authority change
is authorized from this RED.

Next action requires consultation because the predefined gate was reached:
- reject Jev for semantic production role and retain/test another semantic provider; or
- explicitly open a fresh calibration/verification architecture ticket using a new independent
  corpus (not J1/J1B data) if Jev is still worth pursuing.

Any confidence threshold derived from this J1/J1B set is forbidden.
