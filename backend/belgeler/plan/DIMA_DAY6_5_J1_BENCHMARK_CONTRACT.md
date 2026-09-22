# DIMA DAY 6.5 — J1S / J1T BENCHMARK CONTRACT

**Status:** READY FOR EXECUTION AFTER USER APPROVAL  
**Mode:** LAB / EVAL ONLY  
**Product semantic/temporal/authority code:** NO-TOUCH

## 1. Purpose

Measure whether the pinned Jev decision model adds real value to Dima's two bounded
language-decision contracts without using it as a named-case patch.

Challengers:

```text
A = google/gemini-2.5-flash-lite
B = typesafe/jev-1.13
C = openai/gpt-5.6-sol
```

Moving alias `~typesafe/jev-latest` is forbidden.

Jev uses the native OpenRouter Decisions API. It is not wrapped as a normal chat LLM and
is not routed through Dima's current generic `structured_json()` transport.

## 2. Frozen architecture rule

J1 does not confer authority.

```text
decision model = bounded proposal only
SemanticBindingGate = semantic authority
TemporalBindingEngine = deterministic date arithmetic
DB/Wren = numeric truth
```

No model may:
- mint `sem_*`,
- escape a supplied candidate/ontology set,
- write SQL,
- see raw DB/numeric truth,
- bypass tenant/context boundaries,
- silently trigger another model/provider.

## 3. J1S — semantic candidate decision

Frozen input:

```text
user surface
candidate cards[]
```

Candidate-card fields:

```text
candidate_id
target_kind
label
verified_aliases
cube_labels
```

No canonical DB identifier is supplied unless a later separately-approved experiment proves
it necessary.

Output:

```text
supplied candidate_id | ABSTAIN
```

Required strata:

```text
exact alias controls
non-exact Turkish paraphrases
synonym surfaces
multiple plausible candidates
true ambiguity
no-match / ABSTAIN
retrieval miss
bounded high-cardinality sets
entity-value cases
sensitive-value exact-only controls
metric/dimension variation
permuted/metamorphic schema labels
cross-tenant candidate isolation
```

## 4. J1T — typed temporal intent decision

Question:

> Given this exact temporal surface, which closed typed temporal intent does it express?

Jev/LLM does not calculate dates.

Required PERIOD ontology coverage:

```text
THIS_MONTH
PREVIOUS_MONTH
THIS_YEAR
PREVIOUS_YEAR
LAST_N_DAYS
LAST_N_WEEKS
LAST_N_MONTHS
NONE / ABSTAIN
```

Required COMPARISON ontology coverage:

```text
PREVIOUS_PERIOD
SAME_PERIOD_PREVIOUS_YEAR
NONE / ABSTAIN
```

Required scenario families:

```text
explicit-base comparison
implicit-base comparison
Turkish paraphrases
ambiguous temporal phrase
unsupported temporal request
different N values
different surface ordering
metamorphic equivalents
```

If Jev native decision primitives cannot faithfully represent an existing typed field, record
that as benchmark evidence. Do not add regex/prompt workaround.

After a valid typed decision, any date/calendar resolution remains deterministic through the
existing temporal engine.

## 5. Fairness / frozen-case rules

- same logical case and same bounded choices across all three challengers;
- no model-specific testcase wording except transport syntax required by the provider API;
- no named-case prompt tuning;
- no Validation50 / Hidden50 content;
- no production threshold tuning;
- repeated-run subset is frozen before results;
- metamorphic pairs/groups are declared before results;
- provider failures are separated from semantic wrongs.

## 6. Measurements

Shared:

```text
accuracy
ABSTAIN precision
ABSTAIN recall
unsafe ambiguity pick
choice/candidate escape
Turkish paraphrase accuracy
metamorphic consistency
same-input repeated-run agreement
p50 latency
p95 latency
cost
provider failures
```

Jev additionally:

```text
raw choice probabilities
Brier score or equivalent
ECE or equivalent
high-confidence wrong count
```

No J1 result activates a confidence threshold.

## 7. P0

```text
choice outside supplied set = 0
silent ambiguity auto-pick = 0
cross-tenant semantic leak = 0
semantic authority minted by model = 0
hidden fallback/cascade = 0
case-derived rule = 0
```

## 8. Decision rule

Jev poor / materially weaker:
```text
REJECT
→ product code no change
```

Jev promising:
```text
STOP
→ present J1S/J1T results
→ consult user
→ only if approved open D65-J1B
```

D65-J1B is not pre-authorized by this document.

## 9. Execution order after approval

```text
freeze J1S/J1T corpora
→ provider-free harness/schema tests
→ small transport smoke for each provider
→ J1S bake-off
→ J1T bake-off
→ repeated/metamorphic subsets
→ compute metrics/calibration
→ write separate receipts
→ STOP and present decision
```

No product integration follows automatically.
