# DIMA DAY 6.5 — PRE-FREEZE DECISION GATE: J1 + M0 + X0

**Date:** 2026-09-22  
**Branch:** `feat/ask-v2-mvp`  
**Status:** ACTIVE PHASE-LOCAL AUTHORITY  
**Canonical roadmap/report:** SEALED / UNCHANGED

This addendum supersedes the earlier Day 6.5 assumption that:
- D65-J1 only benchmarks semantic candidate selection; and
- Metabase D65-X begins only after DEV80 / engineering closure.

It does **not** renumber the canonical roadmap. Day 7–10 remain unchanged.

## 1. Current proven baseline

```text
D65-G anti-patch hardening         GREEN
provider-free family               35696652502 = 102/102 PASS
reference-floor canary             35697064833 = 16/16 PASS
Wren + Research sentinels          35697471863 = 2/2 PASS
production hybrid /ask-v2          OFF
```

Reference-floor exact tested code SHA:

```text
8dfde62d46d1418f05cce3ed44c26a8025b3b20e
```

Reference floor:

```text
RESEARCH_MANAGER = openai/gpt-5.6-sol
semantic/temporal structured model = openai/gpt-5.6-sol
workers = 1
```

The earlier run `35696811902` was 16/16 HARNESS_FAILURE due stale `resolver=`
constructor wiring in the evaluator. Classification: EVAL_ORACLE / HARNESS DRIFT.
Semantic conclusion: NONE. Product code was not changed for that failure.

These proofs are preserved. **Do not create ENGINEERING FREEZE CANDIDATE or run DEV80 yet.**

## 2. New pre-freeze decision topology

```text
                         CURRENT
                           │
             ┌─────────────┴─────────────┐
             │                           │
          D65-J1                      D65-M0
   decision-model bake-off      Metabase adoption audit
      ┌───────┴───────┐                  │
      │               │                  │
    J1S              J1T                 │
 semantic         temporal               │
 candidate        intent                 │
 decision         decision               │
      └───────┬───────┘                  │
              └─────────────┬─────────────┘
                            ↓
                         D65-X0
                thin Metabase feasibility
                            ↓
                     promising?
                     /        \
                   NO          YES
                   ↓            ↓
              Wren primary    full D65-X
                   \           /
                    └────┬─────┘
                         ↓
               ONE PRIMARY SUBSTRATE
                         ↓
              DAY 6.5 DECISIONS CLOSED
                         ↓
                    DAY 7–15 CODE
                         ↓
        FINAL INTEGRATED RELEASE GATE
                         ↓
             FINAL ENGINEERING FREEZE
                         ↓
                    DEV80 ONCE
```

D65-J1 and D65-M0 may proceed in parallel because both are isolated lab/research gates
and neither is allowed to mutate production authority semantics during the first stage.

## 3. D65-J1 — two independent tracks

Pinned challengers for both tracks:

```text
A = google/gemini-2.5-flash-lite
B = typesafe/jev-1.13
C = openai/gpt-5.6-sol
```

Forbidden:

```text
~typesafe/jev-latest
named-case tuning
hidden model cascade
Jev as a legacy resolver replacement
product semantic/temporal wiring during J1 lab stage
threshold tuning on the same evaluation set
```

Jev uses the native OpenRouter Decisions API / typed decision primitive.
Do not force Jev through Dima's current generic chat `structured_json()` abstraction.

### 3.1 D65-J1S — semantic candidate decision

Lab/eval only.

Frozen boundary:

```text
USER SURFACE
→ frozen CandidateSet[cand_*]
→ decision model
→ candidate_id | ABSTAIN
→ existing SemanticBindingGate remains the authority
```

Candidate cards are restricted to the existing LLM-safe bounded linker surface:

```text
candidate_id
target_kind
label
verified_aliases
cube_labels
```

Do not provide raw DB access, SQL, numeric truth, authority handles, or arbitrary canonical
targets to the decision model.

Required semantic strata:

```text
exact alias controls
non-exact Turkish paraphrases
synonym surfaces
multiple plausible candidates
true ambiguity
no-match / ABSTAIN
retrieval miss
bounded high-cardinality candidate sets
entity-value cases
sensitive-value exact-only controls
metric/dimension variation
permuted/metamorphic schema labels
cross-tenant candidate isolation
```

Output:

```text
supplied candidate_id | ABSTAIN
```

Metrics:

```text
candidate-selection accuracy
ABSTAIN precision/recall
ambiguity unsafe-pick
candidate escape
Turkish paraphrase robustness
metamorphic consistency
same-input repeated-run agreement
p50/p95 latency
cost
provider failures
Jev raw probabilities
Jev calibration (Brier/ECE or equivalent)
Jev high-confidence-wrong count
```

### 3.2 D65-J1T — typed temporal normalization

Do not assume Jev can or cannot solve temporal intent. Measure it.

Jev is not asked to calculate dates.

Boundary:

```text
exact temporal surface
→ decision model
→ typed TemporalNormalizationChoice-equivalent
→ deterministic shape validation
→ TemporalBindingEngine
→ actual dates
```

The benchmark question is language → closed temporal ontology.

Required strata include:

```text
THIS_MONTH
PREVIOUS_MONTH
THIS_YEAR
PREVIOUS_YEAR
LAST_N_DAYS
LAST_N_WEEKS
LAST_N_MONTHS
PREVIOUS_PERIOD
SAME_PERIOD_PREVIOUS_YEAR
explicit-base comparison
implicit-base comparison
Turkish paraphrases
ambiguous temporal phrase
unsupported temporal request
```

Jev may use typed `choice` / `noul` / `score` primitives only when they faithfully
represent the existing temporal contract. If a current temporal field cannot be expressed
natively, record that as benchmark evidence; do not add regex/prompt workarounds.

Jev must not perform date arithmetic. Deterministic calendar math remains owned by
`TemporalBindingEngine`.

### 3.3 J1 P0 invariants

```text
candidate outside supplied set = 0
silent ambiguity auto-pick = 0
cross-tenant semantic leak = 0
semantic authority minted by model = 0
hidden fallback/cascade = 0
case-derived prompt/rule = 0
```

For Jev, raw probability/calibration is measurement only during J1.
No production confidence threshold is activated in this phase.

### 3.4 J1 decision rule

If Jev is clearly poor or Turkish/temporal robustness is inadequate:

```text
REJECT JEV
→ product code NO CHANGE
→ preserve existing architecture
```

If Jev is promising in one or both bounded decision contracts:

```text
STOP AT DECISION GATE
→ consult before integration
→ open D65-J1B only after explicit approval
```

D65-J1B target, if approved:

```text
SemanticLinkDecisionProvider
  ├─ StructuredLLMDecisionProvider
  └─ JevDecisionProvider

and physical cognition-role separation:

SEMANTIC_LINKER
= bounded catalog candidate decision

TEMPORAL_NORMALIZER
= temporal language → typed TemporalNormalizationChoice
```

No hidden fallback. Every provider/model attempt is explicit in telemetry.

## 4. D65-M0 — Metabase architecture extraction/adoption audit

D65-M0 is a **read/research gate**, not product integration.

Canonical upstream:

```text
metabase/metabase
historical pinned snapshot:
74216b30981d8310c4cf724d63ca282e2e63529d

current upstream master verified 2026-09-22:
fff70175e0b5f82dc0eb267593c717c4a6130206
```

The current upstream head is exactly one commit ahead of the historical pinned snapshot.
Git comparison shows **no changes in the relevant `src/metabase/metabot/agent`,
`src/metabase/agent_api`, or `src/metabase/mcp/v2` families** between these two SHAs.

Mandatory source families:

```text
src/metabase/metabot/agent/core.clj
src/metabase/metabot/agent/profiles.clj

src/metabase/agent_api/reference.md
src/metabase/agent_api/api.clj
src/metabase/agent_api/query_guards.clj

src/metabase/mcp/v2/...
relevant query/search/resource tools

Metabase native NLQ / exploration / profile surfaces
```

Source copy / transliteration / vendoring remains forbidden.

Create and maintain:

```text
DIMA_DAY6_5_METABASE_ADOPTION_MATRIX.md
```

Each row records:

```text
Metabase mechanism
exact source evidence
problem solved
Dima equivalent
already adopted?
gap?
adopt?
timing = NOW | D65-X | DAY7-10 | POST-MVP
reason
risk
license/API dependency
```

Audit at minimum:

```text
generic agent loop mechanics
profile-specific behavior
max iterations / budgets
successful terminal tools
failed-terminal self-correction
terminal permission errors
capability-scoped tools
user permission scoping

search/retrieve entities
read-resource
metrics
field inspection

construct-query
validation
repair
resolution
opaque query / query handle
execute
permission revalidation
native SQL separation / kill switch

saved questions
charts
dashboards
collections
explorations / research plan
dashboard/workspace UX
```

Primary question:

> Is Dima re-inventing a mechanism Metabase already solves, and can we adopt the pattern or
> supported API without weakening Dima's authority/trust model?

## 5. D65-X0 — thin Metabase feasibility before freeze

D65-X0 starts after enough M0 source/audit work exists to define a bounded spike.

Separate Metabase service only.

Representative setup:

```text
same DB
same representative tenant/principal
5–10 representative StandardProjection examples
```

Target chain:

```text
Dima AcceptedStandardAuthority
→ StandardProjection
→ thin experimental Metabase adapter
→ Metabase Agent API
→ search/read if required
→ construct-query
→ execute
→ result
→ Dima receipt
```

Measure:

```text
query correctness
result correctness
construct/repair behavior
latency
permissions
tenant identity
executed query identity
QueryContract bindability
EvidenceArtifact compatibility
integration complexity
```

Forbidden:

```text
raw SQL shortcut
remove Wren
production Metabase routing
copy/port/vendor source
equal Wren + Metabase production truth engines
```

If X0 is not promising:

```text
Wren remains primary substrate
→ freeze sequence may resume
```

If X0 is promising:

```text
STOP AT DECISION GATE
→ consult
→ full D65-X Wren-vs-Metabase substrate bake-off
→ choose exactly ONE primary execution substrate
→ only then freeze
```

## 6. Metabase patterns already adopted vs still open

Already substantially adopted as architecture direction:

```text
generic agent loop mechanics + domain profile concept
→ BoundedAgentRuntimeKernel direction

bounded budgets / progress
→ current Dima runtime discipline

tool/profile separation
→ Dima profile/tool boundaries
```

Still requires systematic audit / real feasibility:

```text
successful vs failed terminal semantics
capability/permission-scoped tool registry
search → read-resource → construct-query pipeline
query validation/repair/resolution
opaque query handles
execute separation
permission revalidation
native SQL guards
native NLQ behavior
resource retrieval
saved questions/charts/dashboards/collections/explorations/workspace UX
```

Do not write “everything valuable from Metabase has already been adopted.”

## 7. D65-X vs Metabase product/UX

Primary D65-X:

```text
same Dima cognition
same authority
same StandardProjection

Wren substrate
vs
Metabase substrate
```

Secondary experiment, separate from substrate winner:

```text
Dima STANDARD agent
vs
Metabase native NLQ / Metabot
```

Product/UX adoption candidates such as collections, saved questions, dashboards, charts,
explorations and BI workspace remain independently valuable even if Metabase loses the
execution-substrate bake-off.

## 8. Updated binding sequence

```text
CURRENT GREEN PROOFS
↓
D65-J1S + D65-J1T LAB BENCHMARKS
+
D65-M0 ADOPTION AUDIT
↓
decision receipts
↓
D65-X0 THIN FEASIBILITY
↓
Metabase not promising
  → Wren primary
or
Metabase promising
  → consult
  → full D65-X
  → ONE primary substrate
↓
ENGINEERING FREEZE CANDIDATE
↓
DEV80 once per candidate
↓
engineering closure
↓
VALIDATION50
↓
fresh external HIDDEN50
↓
certification seal
↓
production hybrid activation
```

If J1 is promising and requires J1B product integration, affected focused/provider-free/live/
canary/sentinel gates must re-run before X0/freeze as required.

## 9. STOP-THE-LINE / consultation gates

STOP and consult before:

```text
opening D65-J1B product integration
choosing a Jev/Gemini/Sol production policy or cascade
setting a production Jev confidence threshold
starting full D65-X after X0 looks promising
choosing Metabase over Wren as primary substrate
adopting a Metabase mechanism that changes Dima authority/security/trust boundaries
creating ENGINEERING FREEZE CANDIDATE
starting DEV80
```

Hard prohibitions remain:

```text
Metabase source copy/port/vendor
equal Wren + Metabase production truth engines
Jev as named-case patch
hidden model cascade
case-specific regex/prompt
model or Metabase as semantic/numeric authority beyond existing gates
freeze/DEV80 before J1 + M0/X0 decisions are resolved
```

## 10. Next exact work

Without changing product semantic/temporal/authority code:

1. Finalize J1S frozen benchmark corpus + lab runner.
2. Finalize J1T frozen temporal-intent corpus + lab runner.
3. Start D65-M0 source audit and populate the adoption matrix.
4. Produce separate J1 and M0 receipts.
5. Then prepare D65-X0 feasibility ticket.
6. Stop and consult at any promising integration/substrate decision.

## 11. Release-level timing override

`DIMA_RELEASE_FINAL_INTEGRATED_GATE.md` supersedes every DEV80/final-freeze timing statement in this file.

This file decides J1/M0/X0 architecture choices. It does **not** authorize DEV80.

After J1/M0/X0 resolve:
```text
close Day6.5 architecture decisions
→ continue Day7–15
→ final integration rehearsal
→ final release freeze
→ DEV80 once
```

Day6.5 may record an architecture checkpoint SHA, but that is not the release FINAL ENGINEERING FREEZE CANDIDATE.
