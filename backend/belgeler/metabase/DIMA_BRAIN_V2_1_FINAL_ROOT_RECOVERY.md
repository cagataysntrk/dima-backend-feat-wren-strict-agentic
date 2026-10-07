# Dima Brain V2.1 — Final Root Recovery

> **FINAL STATUS — 2026-10-07:** R1-R7 are complete and provider-free GREEN. The single authorized paid recovery wave `37533803018` completed **RED** because R10 and R11 failed with `R1_METRIC_SCOPE_REQUIRED`. R9 is blocked. `30-CASE EXECUTION READY = NO`. The broad 30-case was not run. The immutable adjudication receipt is `DIMA_BRAIN_V2_1_ROOT_RECOVERY_PANEL_2026-10-07.md`.


Date: 2026-10-06  
Branch: `feat/dima-brain-v2-1-specification-closure`  
Recovery baseline: `505caec6e7c3fbd5346dc6a4c310e8f656d324ae`  
Previous Product baseline: `ae4e0348601774082b0270f23d6de126e71e6055`  
Frozen engine: `686671fa7e55f715e4fb5ac155f9e66019fd12d8` / `0.63.18-dima.11.2`

## Why this development exists

The frozen 30-case corpus completed successfully at the workflow level, but fair Product quality was 68.25/100. The remaining failures are not to be repaired as benchmark cases. They expose one shared architectural defect: Dima still owns too much analytical admission and turn semantics.

The recovery therefore removes duplicate business-semantic authority while preserving every security, provenance, currentness and epistemic guardrail.

Canonical law:

> **DIMA OWNS WHAT + GOVERNANCE.**  
> **METABASE OWNS HOW.**

Dima accepts governed semantic intent and protects authority. Metabase/Metabot decides how a legal governed analytical request is realized. Dima must not predict Metabase capability with a small closed runtime grammar.

## Non-negotiable constraints

- No new branch.
- Engine frozen.
- Metabot frozen.
- No engine build.
- No prompt-wording patch.
- No regex or morphology routing.
- No benchmark/case ID in Product code.
- No metric-specific, month-specific, language-specific or family-specific branch.
- P17 discovery remains retired.
- P17 remains the only NextTest designer.
- Duplicate native execution remains forbidden.
- Security, tenant/principal isolation, exact currentness, Evidence lineage, query/result fingerprints, engine identity and causal restraint remain fail-closed.
- Frontend/UI work is not authorized.
- The actual broad 30-case corpus is not run in this recovery round.

## Root-recovery workstreams

### R1 — Thin semantic admission

Status: IMPLEMENTED

- Remove closed V1 analytical grammar from Product admission.
- Keep grammar helpers only as conformance/test/telemetry surfaces.
- A grounded ResearchBrief must not become UNSUPPORTED only because its operation composition is absent from `V1_LEGAL_COMPOSITIONS`.
- `ResearchGoalKind.OTHER` is not a capability failure when governed material refs exist. It receives a generic OBSERVE/material-acquisition routing floor.

### R2 — Canonical scope-level temporal authority

Status: IMPLEMENTED

- Remove goal-local duplicate semantic membership checks for accepted comparison refs.
- Accepted `ResearchScope` is the semantic authority.
- Coalesce repeated identical temporal frames.
- Distinguish true PAIR semantics from bounded SPAN_CHANGE semantics.
- Clarify only when two genuinely different simultaneous temporal frames cannot be represented safely.
- One typed temporal resolver must feed Intake -> ScopePatch -> AnalyticalRequestContract -> AnalyticalIntentV1.

### R3 — Turn transition != ScopeVersion transition

Status: IMPLEMENTED

Introduce exactly two generic turn transitions:

- `SCOPE_MUTATION`
- `SAME_SCOPE_CONTINUATION`

Rules:

- Real scope mutation => exactly `scope_vN -> scope_vN+1`.
- Same-scope continuation => ScopeVersion delta 0.
- Presentation-only continuation => ScopeVersion delta 0 and native delta 0.
- Research/authority turn revision is independent from ScopeVersion.
- Exact tenant/principal/context/scope fingerprint/Evidence currentness remains enforced.

### R4 — Adaptive authorization collapse

Status: IMPLEMENTED

- ROOT_CAUSE already authorizes bounded investigation.
- ROOT_CAUSE + unresolved competing hypotheses + legal information gain may open P19 -> P17 NextTest without a duplicate FOLLOW_VERIFIED_MATERIAL requirement.
- Ordinary direct analysis still requires explicit FOLLOW_VERIFIED_MATERIAL for adaptive deepening.
- `max_adaptive_reentries = 2` is allowed, but the second re-entry requires new information gain.
- Budget remaining alone never opens another query.

### R5 — Governed P20 synthesis

Status: IMPLEMENTED

P20 becomes the presentation synthesis owner, not a row serializer.

Allowed:
- at most one bounded synthesis cognition call when needed;
- accepted deliverables, current ScopeVersion, governed Evidence digests, P18/P19 results and limitations as input;
- typed observation/finding/relationship/epistemic/limitation/management-implication output with Evidence refs.

Forbidden:
- native query;
- Metabase call;
- new analytics;
- new numeric computation;
- new metric;
- causal-strength upgrade;
- claims absent from governed Evidence.

### R6 — Deliverable-aware completion

Status: IMPLEMENTED

- `report_ref != None` is not sufficient proof that a report MUST is fulfilled.
- P20 must emit typed deliverable coverage:
  - `requirement_id -> FULFILLED | LIMITED`
- Missing presentation quality is not an exception. P20 either synthesizes from sufficient governed Evidence or returns explicit LIMITED.

### R7 — Metamorphic anti-new-family closure

Status: GREEN — 192 generated scenarios + Wave A/B + mutation

Before any paid validation, run >=100 deterministic/generated provider-free scenarios spanning:

- multiple metrics/dimensions and 1/2/3 metric shapes;
- PAIR and SPAN change;
- ranking + comparison;
- direct adaptive and RCA adaptive;
- report-only continuation;
- same-scope continuation;
- true scope narrowing;
- 2-turn and 3-turn continuation;
- metric/entity permutation.

Required invariants:

- equivalent semantics => equivalent canonical intent;
- metric ordering does not change acceptance;
- repeated identical temporal frame across goals is not ambiguous;
- governed legal request is not rejected by closed grammar;
- same-scope continuation => ScopeVersion delta 0;
- real scope mutation => exactly +1;
- report-only continuation => native delta 0;
- P20 synthesis => new analytics 0;
- adaptive native work requires information gain;
- duplicate native = 0;
- stale Evidence = 0.

### R8 — One independent paid recovery panel

Status: RED — paid recovery run `37533803018`

Only after provider-free closure:

- 12 cases total;
- four failing architecture families;
- original semantic shape + independent semantic sibling + wording/mutation sibling;
- no Product visibility into case IDs.

Acceptance:

- 12/12 answerable cases exception-free;
- every case >=3/4;
- >=8 FULL;
- security/silent-wrong/causal-overclaim/stale-Evidence/duplicate-native = 0;
- P20 presentation-only native delta = 0.

No second paid correction wave except a proven harness defect.

### R9 — Final same-SHA freeze

Status: BLOCKED — R8 is RED

After the recovery panel is GREEN:

- freeze the Product SHA;
- engine identity remains unchanged;
- run full provider-free closure on the same Product SHA:
  - Phase-1
  - Phase-2
  - semantic conformance
  - Wave A/B
  - mutation
  - frozen-family
- update canonical handoff/progress documentation;
- seal:

`30-CASE EXECUTION READY = YES`

Then STOP. The actual 30-case corpus requires separate user authorization.

## External pattern basis

The recovery uses standards and upstream architecture as design constraints, not as code to copy:

- Google AIP-134 / FieldMask: explicit partial update; untouched state remains untouched.
- RFC 7396 JSON Merge Patch: patch semantics are distinct from replacement semantics.
- Wren AI architecture: governed context is distinct from planning/execution.
- Metabase/Metabot: analytics/query realization stays in the analytics substrate.
- LangGraph: graph/checkpoint state is orchestration state, not a second semantic authority.
- OpenTelemetry: first-wrong-boundary telemetry remains mandatory when a new failure is discovered.
- Property/stateful testing patterns: regression closure is metamorphic, not benchmark memorization.

## Current position

As of this file's creation, branch HEAD equals the recovery baseline `505caec...`. No recovery Product patch has yet been applied.

Next action: R1 thin semantic admission.


## Recovery execution ledger — 2026-10-06

Current candidate Product SHA at this checkpoint: `de4c03f288b62ffcad4aece57f0bebf102b381bd`.

Implemented root changes:

- R1 thin semantic admission: IMPLEMENTED. Closed V1 grammar no longer rejects an otherwise governed ResearchBrief; `OTHER` routes to governed `OBSERVE`.
- R2 scope-level comparison/temporal authority: IMPLEMENTED. Goal-local comparison membership was removed; repeated identical frames coalesce; neutral material windows are not promoted to CHANGE; PAIR is not manufactured from chronology; Intake/ScopePatch/material/intent use the canonical temporal resolver/projection path.
- R3 turn transition vs ScopeVersion: IMPLEMENTED. `SCOPE_MUTATION` and `SAME_SCOPE_CONTINUATION` are separate; same-scope turns preserve ScopeVersion and advance independent authority revision; currentness remains exact.
- R4 adaptive authorization collapse: IMPLEMENTED. ROOT_CAUSE is sufficient bounded investigation authority; ordinary direct deepening still requires explicit FOLLOW_VERIFIED_MATERIAL; P17 remains sole NextTest designer; max adaptive reentries=2; P17 state is not consulted before P19 emits a NextTest.
- R5 governed P20 synthesis: IMPLEMENTED. P20 has one bounded typed synthesis cognition seam, receives only governed publication-gated material, has no native/Metabase capability, cannot author numeric synthesis text, and degrades presentation to LIMITED when synthesis cannot be safely completed.
- R6 deliverable-aware completion: IMPLEMENTED. `report_ref` existence is not fulfillment; current sealed report deliverable coverage is the completion authority.
- R7 metamorphic anti-new-family closure: IN VALIDATION. 192 deterministic generated scenarios are wired as a mandatory provider-free gate. Semantic conformance + all 192 scenarios are GREEN in run `37525079655`; Wave A/B and mutation steps are still completing in that same run.

Provider-free receipts already GREEN on candidate SHA `de4c03f...`:

- focused Brain V2: run `37525079508` — GREEN.
- frozen-family closure: run `37525079621` — GREEN.
- semantic conformance core + 192 generated scenarios: run `37525079655` — GREEN through metamorphic receipt; saturation/mutation remainder pending at this checkpoint.

Security/provenance status:

- certified engine gitlink remains `686671fa7e55f715e4fb5ac155f9e66019fd12d8`;
- no engine build was performed;
- P17 discovery was not restored;
- production boundary audits contain no benchmark-family IDs;
- tenant/principal/currentness/Evidence lineage/native identity gates remain fail-closed.

Paid validation remains BLOCKED until the entire provider-free closure, including Wave A/B and mutation canaries, is GREEN. The frozen 30-case corpus remains unauthorized and unexecuted.


## Final recovery closure — 2026-10-07

- R1 thin semantic admission: COMPLETE.
- R2 canonical scope-level temporal authority: COMPLETE.
- R3 turn transition / ScopeVersion separation: COMPLETE.
- R4 adaptive duplicate-authorization collapse: COMPLETE.
- R5 governed P20 synthesis owner: IMPLEMENTED; live typed closure remains a quality weakness in several report cases.
- R6 deliverable-aware completion: COMPLETE.
- R7 provider-free/metamorphic closure: GREEN — focused `37525079508`, frozen-family `37525079621`, semantic/Wave A/Wave B/mutation `37525079655`, 192 generated scenarios.
- R8 single 12-shape paid recovery panel: **RED** — `37533803018`.
- R9 final same-SHA readiness seal: **BLOCKED**.

First remaining Product boundary: follow-up refinement/deepening can lose executable metric authority and fail with `R1_METRIC_SCOPE_REQUIRED`. Separate quality weakness: P20 bounded synthesis frequently returns explicit LIMITED after post-provider typed closure failure. Adaptive information-gain deepening is also not demonstrated consistently.

Supervisor stop law is active: the single paid correction wave has been consumed and the failures are Product failures, not a proven harness defect. No second paid correction wave, no broad 30-case, and no `30-CASE EXECUTION READY = YES` seal are legal in this round.


## User-authorized recovery cycle 2 — 2026-10-07

This section supersedes the prior RED stop receipt as the **current recovery state**.
The earlier run `37533803018` remains immutable historical evidence; it is not
rewritten or hidden.

Purpose of this cycle:

- close the shared semantic-authority defects exposed by the first recovery wave;
- preserve the frozen engine/Metabot boundary;
- re-establish the independent 12-shape recovery acceptance gate;
- if GREEN, run the final same-Product provider-free closure and seal
  `30-CASE EXECUTION READY = YES`;
- do **not** execute the actual broad 30-case corpus.

Current semantic Product candidate:

`a8d3d68ff03696231eca05b23b345df660853629`

Engine remains frozen:

`686671fa7e55f715e4fb5ac155f9e66019fd12d8` / `0.63.18-dima.11.2`

Generic root closures added after the first RED wave:

1. Same-scope metric authority: an omitted metric facet inherits exact accepted
   ResearchScope authority instead of becoming `R1_METRIC_SCOPE_REQUIRED`.
2. Native ranking repair: canonical AnalyticalRequestContract authority is now
   available to bounded repair without widening the executor interface.
3. P20 identity closure: provider-selected deliverable/statement refs are closed
   by JSON Schema to the exact accepted governed ID set.
4. P20 numeric provenance: numeric synthesis is legal only when every numeric
   token is already present in supporting governed material; new numbers remain
   forbidden.
5. Direct TABLE/CHART coverage: fully represented governed analytical material
   can satisfy tabular/chart presentation without an unnecessary cognition call;
   REPORT/EXPLAIN still require bounded P20 synthesis.
6. Temporal CHANGE authority: a single adjacent shared bounded change frame can
   remain SPAN when no typed temporal-comparison owner exists; explicit
   comparison remains PAIR.
7. ScopePatch temporal authority: ScopePatch now projects the already-resolved
   current-turn canonical period authority instead of reinterpreting the same
   temporal meaning a second time.
8. Same-scope analytical continuation: provider-local `qN` refs can select an
   exact prior accepted analytical goal through the typed `CONTINUE` DTO.
   CONTINUE cannot mint a new semantic ref or ScopeVersion.

Provider-free evidence for the Product candidate:

- semantic conformance + 192 generated metamorphic scenarios + Wave A/B +
  mutation: run `37581832437` — GREEN;
- frozen-family closure: run `37581832390` — GREEN;
- the test-only continuation HEAD also passed semantic conformance + generated
  metamorphic closure in run `37581893679`.

Paid evidence in this cycle:

- diagnostic 12-shape run `37579997277` completed all 12 slots and exposed four
  first-wrong boundaries. Each boundary is covered by the generic fixes above;
  it is diagnostic evidence, not the final R8 seal.
- targeted continuation pinpoint `37582138826` is the current live validation
  of typed same-scope continuation.

Current gate:

- R1-R7: implemented / provider-free GREEN.
- R8 final independent 12-shape recovery panel: PENDING after pinpoint.
- R9 final same-Product closure: PENDING R8 GREEN.
- broad 30-case: NOT RUN and NOT authorized by this recovery cycle.
