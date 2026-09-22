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

## 2. Current Day 6.5 decision topology

```text
                 CURRENT
                    │
          ┌─────────┴─────────┐
          │                   │
     J1 decision              M0
   model-role evidence    source/adoption audit
          │                   │
          └─────────┬─────────┘
                    ↓
                  D65-SI
        Standard Integration Closure
                    ↓
        real Standard Wren sentinel
                    ↓
                   X0
       private self-hosted Metabase
          feasibility experiment
                    ↓
               promising?
              /          \
            NO            YES
            ↓              ↓
       Wren remains     STOP / CONSULT
          primary       before full D65-X
                    │
                    ↓
                Day 7–15
                    ↓
        final integrated release gate
                    ↓
          FINAL FREEZE → DEV80 once
```

J1 and M0 evidence may be developed independently, but X0 execution is no longer reachable
directly from them. The mandatory bridge is:

```text
J1 topology decision
+ M0
→ D65-SI
→ real Standard Wren sentinel
→ X0
```

Production semantic/temporal authority does not move during the J1 lab stage.

## 3. D65-J1 — two independent tracks

Current model-role authority:

```text
PRIMARY:
A = google/gemini-2.5-flash-lite
B = typesafe/jev-1.13
C = openai/gpt-5.6-luna

REFERENCE_CEILING:
openai/gpt-5.6-sol

CONDITIONAL:
openai/gpt-5.6-terra
```

Sol is not a cheap-tier peer. Terra is not automatic; the current consultation explicitly
authorizes one J1T-only conditional frozen run.

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

### 3.4 J1 decision / consultation state

Measured result:

```text
Jev universal provider                   = REJECT
Jev temporal provider                    = REJECT / capability floor
Jev bounded semantic decision primitive  = PROMISING / NOT PRODUCTION-ACCEPTED

Luna temporal typed provider             = PROMISING / NOT SEALED
```

Consultation is complete for the following bounded work:

```text
eval-oracle harness classification fix
authority-document cleanup
one frozen J1T-only Terra conditional run
D65-J1B narrow engineering experiment after Terra
D65-SI if J1B P0/architecture is GREEN
self-hosted private X0 after D65-SI + real Wren sentinel GREEN
```

D65-J1B is an engineering experiment, not production activation. Its purpose is to test whether
role-specialized providers preserve their standalone advantage inside the real Dima semantic /
temporal flow.

Still requires STOP/CONSULT:
- production confidence threshold or fresh calibration design;
- hidden fallback/cascade;
- production Jev activation;
- production Luna/Terra seal;
- architecture redesign exposed by J1B or D65-SI.

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

## 5. D65-X0 — thin Metabase feasibility after D65-SI

D65-X0 may execute only after D65-SI and the real Standard Wren sentinel are GREEN.
M0 being sufficient permits preparation, not execution.

Experiment deployment default = pinned self-hosted Metabase on a private network with an ephemeral/test app DB where useful. Cloud is not the default. Production Metabase dependency remains NOT APPROVED.

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
eval/docs cleanup
→ Terra J1T conditional frozen run
→ D65-J1B narrow real-flow experiment
→ focused provider-free / failure-family / temporal / metamorphic proofs
→ workers=1 focused real-LLM
→ small representative canary
→ D65-SI
→ real Standard Wren sentinel
→ self-hosted private X0
→ if X0 promising: STOP / CONSULT for full D65-X
→ otherwise Wren remains primary
→ Day 7–15
→ final rehearsal
→ FINAL FREEZE
→ DEV80 once
→ Validation50
→ Hidden50
```

Broad DEV80/Validation/Hidden are not development loops.

## 9. STOP-THE-LINE / consultation gates

Current consultation authorizes the bounded sequence through X0.

STOP and consult before:

```text
J1B requires production threshold / calibration or material architecture redesign
D65-SI reveals authority/integration redesign
starting full D65-X after X0 looks promising
choosing Metabase over Wren as primary substrate
adopting a Metabase mechanism that changes Dima authority/security/trust boundaries
creating FINAL ENGINEERING FREEZE
starting DEV80
pilot activation
```

Hard prohibitions remain:

```text
production Jev activation without a later seal
production confidence threshold derived from J1/J1B set
hidden provider cascade/fallback
production Luna/Terra seal
Metabase source copy/port/vendor
equal Wren + Metabase production truth engines
case-specific regex/prompt patch
model or Metabase as semantic/numeric authority beyond existing gates
X0 before D65-SI + real Standard Wren sentinel
DEV80 before final release gate
```

## 10. Next exact work

Without reopening frozen corpora or touching product authority during eval cleanup:

1. Fix `D65-J1-FULL-001`: invalid typed model output must not be labeled provider failure.
2. Recompute stored J1 contract-fidelity classification/metrics from existing artifacts; no paid rerun.
3. Run one frozen **J1T-only** Terra conditional benchmark: CHOICE + CONTRACT-FIDELITY + repeated/metamorphic evidence.
4. Open D65-J1B narrow role-specialized provider experiment.
5. If J1B P0/architecture is GREEN, execute D65-SI.
6. Prove the real Standard Wren sentinel.
7. Execute private self-hosted X0.
8. Stop/consult if the defined next consultation condition is reached.

## 11. Release-level timing override

`DIMA_RELEASE_FINAL_INTEGRATED_GATE.md` supersedes every DEV80/final-freeze timing statement in this file.

This file decides J1/M0/X0 architecture choices. It does **not** authorize DEV80.

After J1B + D65-SI + X0 resolve:
```text
close Day6.5 architecture decisions
→ continue Day7–15
→ final integration rehearsal
→ final release freeze
→ DEV80 once
```

Day6.5 may record an architecture checkpoint SHA, but that is not the release FINAL ENGINEERING FREEZE CANDIDATE.


## D65-SI STANDARD INTEGRATION CLOSURE — inserted gate

Current required order is now:

```text
J1 decision
→ chosen semantic/temporal topology known
→ D65-SI Standard Integration Closure
→ real Standard Wren vertical sentinel
→ D65-X0
```

Authority:
`DIMA_DAY6_5_STANDARD_INTEGRATION_CLOSURE.md`.

X0 must compare the real
`AcceptedStandardAuthority → StandardProjection → execution substrate` chain, never a surrogate
Research `AcceptedTurnContract` path.
