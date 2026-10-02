# P17 — RESEARCH MANAGER MATURATION PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-25  
**Status:** **SEALED / P17 RESEARCH MANAGER MATURATION IMPLEMENTATION AUTHORIZED / P17 FINAL GREEN / RECURSIVE AUTONOMOUS CERTIFICATION GREEN**  
**Forward authority:** DMP-DEC-0048 + DMP-DEC-0049 + DMP-DEC-0050 + DMP-DEC-0051 + DMP-DEC-0052 + DMP-DEC-0053  
**Consumes:** P14 Research/Evidence + P15 native material + P16 claims  
**UI/UX:** NOT AUTHORIZED  
**Engine change:** NOT AUTHORIZED BY DEFAULT


## FINAL P17 SEAL — DMP-DEC-0053

This section is current authority and overrides the historical RED disposition below.

```text
sealed product/code candidate          = 3664d3d706d70225323126cbc994b8c2c732aaf4
provider-free                           = 36158440330 SUCCESS
governance                              = 36158440319 SUCCESS
live dispatch SHA                       = 5595544fcd94f5250961b5ac3a158a1a9c02e9fb
live                                    = 36160559037 SUCCESS
dispatch governance                     = 36160559032 SUCCESS

family-aware authorization              = 30 PASS
provider schema/envelope                = 8 PASS
trajectory evaluator                    = 8 PASS
P17 legality/reasoning                  = 49 PASS
P16                                     = 6 PASS
P15                                     = 5 PASS
P14                                     = 17 PASS

manager Luna calls                      = 8
native P17 follow-ups                   = 3
VERIFIED native occurrences             = 4 including base
max observed depth                      = 3
terminal stop                           = NO_NEW_EVIDENCE
Sol / C1 / engine builds                = 0 / 0 / 0
```

All DMP-DEC-0050 trajectory-invariant gates are GREEN. DMP-DEC-0053 is the final P17 legality
boundary: the model chooses what to investigate from a state-derived legal move set; deterministic
Dima resolves topology exactly once; Metabase/Metabot own every analytical execution.

```text
P17 = SEALED
P18 = PREDEVELOPMENT REVIEW ONLY
P18 IMPLEMENTATION = NOT STARTED
```

## HISTORICAL EARLY LIVE CANARY DISPOSITION — 2026-09-25

```text
recursive provider-free = 36128262857 SUCCESS
governance              = 36128262891 SUCCESS
P17 focused             = 29 PASS
P16                     = 6 PASS
P15                     = 5 PASS
P14                     = 17 PASS

one Luna canary         = 36127753645 FAILURE
manager Luna calls      = 1
P17 follow-up occurrences before RED = 0
engine builds           = 0
Sol calls               = 0
```

The live RED is `DMP-P17-LIVE-RED-001`: transport schema permitted null
`expected_information_gain` but deterministic non-STOP `ManagerProposal` did not. The root fix is
provider-free GREEN and lower authorities remain GREEN.

This does not seal P17. A second paid canary is not authorized by default. P18 remains blocked until
an explicit supervisor decision authorizes the remaining live-cognition proof and that proof is
GREEN.

## 1. Goal

P17 turns the durable Research ledger into a bounded agentic investigation loop.

The manager's job is not to perform analytics. It reasons about:

```text
what remains unresolved
what Evidence/claims exist
what contradiction matters
what bounded investigation should happen next
when to seek counter-evidence
when to stop
```

Metabase/Metabot remain the analytical owners.

## 2. Permanent split

LLM/Research Manager may propose the next investigative step.

Deterministic Dima code owns:
- ResearchSession identity and revision;
- obligation identity/state;
- claim/Evidence eligibility;
- allowed proposal types and transitions;
- budget accounting;
- no-progress detection;
- counter-evidence requirement markers;
- stopping/completion;
- durable restart.

Forbidden deterministic replacement:

```text
if trend then breakdown
if breakdown then segment
if segment then compare
```

P17 must not become a hand-written analytics strategy tree.

## 3. Typed manager proposal

The initial bounded proposal contract should support a small set of Research actions, conceptually:

```text
EXPLORE_NATIVE
FORM_CLAIM
SEEK_COUNTER_EVIDENCE
STOP
```

A proposal must carry:
- proposal id / source Research revision;
- target obligation;
- action;
- rationale;
- bounded objective or claim target where relevant;
- Evidence/claim refs inspected;
- expected information gain or explicit gap;
- stop reason where relevant.

The deterministic layer validates references and action preconditions. It does not decide which
analytical operator to run.

## 4. Durable reasoning step

Every accepted manager proposal must become a durable reasoning-step record before any subsequent
external/native/model action.

Minimum identity:

```text
step_id
research_session_id
source_revision
target obligation
proposal/action
rationale
inspected Evidence refs
inspected claim refs
gap/objective
status
result refs
created_at / completed_at
```

Restart resumes from the durable step; it does not reinterpret original user authority.

## 5. No-progress

P17 needs explicit no-progress detection that is independent of prose quality.

Examples of deterministic no-progress signals:
- same normalized bounded proposal identity repeats without new Evidence/claim material;
- manager proposes a step already completed against the same authority/revision inputs;
- budget is exhausted;
- all material obligations are terminal;
- repeated counter-evidence attempt yields no eligible new material.

No-progress handling may stop or mark an explicit limitation. It must not silently loop.

## 6. Counter-evidence

For material claims/hypotheses, P17 must be able to request a counter-evidence step.

Research cannot close an important conclusion merely because confirming Evidence exists.

Allowed final epistemic outcomes include:

```text
SUPPORTED
CHALLENGED
CONTESTED
INCONCLUSIVE
INSUFFICIENT_EVIDENCE
```

No forced answer.

## 7. Provider-free first slice

Provider-free implementation should use a scripted/fake manager that emits typed proposals and prove:
1. current Research/Evidence/claim snapshot is the proposal input;
2. invalid refs/actions fail closed;
3. accepted proposal is persisted before follow-on work;
4. budget is consumed deterministically;
5. duplicate/no-progress proposal is detected;
6. counter-evidence proposal is first-class;
7. STOP proposal creates explicit stopping rationale;
8. restart restores reasoning step without reparsing original user language;
9. no analytical operator/parser/scorer is implemented in P17.

This proves the state machine/authority boundary, not LLM quality.

## 8. Live cognition gate

A single bounded Luna Research Manager canary is allowed only after provider-free GREEN if actual
manager cognition is a decision-changing uncertainty.

No broad corpus. No Sol by default.

The canary should prove one coherent case:

```text
objective
→ multiple obligations/material
→ inspect Evidence/claims
→ identify gap
→ propose bounded next step
→ counter-evidence attempt
→ replan or stop
```

The live model proposes investigation. It must not become analytical truth owner.

## 9. P17 exit

P17 closes when one coherent Research case proves:

```text
initial objective
→ obligations
→ native work/material
→ Evidence/claims
→ gap identification
→ durable proposal
→ replan
→ counter-evidence attempt
→ bounded completion / explicit inconclusive stop
```

with restart durability and no giant deterministic analytics strategy engine.

Then P18 may add only materially business-specific relationship policy; physical join mechanics remain
native Metabase-owned.

---

## RECURSIVE INVESTIGATION AUTHORITY ADDENDUM — DMP-DEC-0049

The bounded P17 foundation is provider-free GREEN, but P17 is not sealed until recursive
investigation topology and one bounded real Luna cognition canary are GREEN.

The existing `ResearchReasoningStep`, `ResearchInvestigationTask`, proposal-before-action,
no-progress, budget, counter-evidence, `P17_FOLLOWUP`, shared
`NativeResearchOccurrenceRunner`, P15 material reuse, P16 lineage reuse, single receipt family,
and restart durability are preserved.

Recursive implementation must add only minimal investigation topology to the existing durable
ledger. Any InvestigationGraph is a projection, not a second truth store. Parent→child means "we
chose to investigate deeper", never causal truth. P19 remains the future causal/contribution owner.

At every depth:

```text
Dima chooses WHAT analytical question to investigate next
→ Metabot/Metabase perform native analytical work
→ Dima records what the resulting Evidence changed
```

P18 remains blocked until recursive provider-free proof and the single decision-changing Luna P17
canary are GREEN.

status:
`SEALED PREDEVELOPMENT + RECURSIVE ADDENDUM / P17 RECURSIVE IMPLEMENTATION AUTHORIZED / P18 BLOCKED`.

