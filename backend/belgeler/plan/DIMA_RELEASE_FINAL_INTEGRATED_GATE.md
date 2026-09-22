# DIMA V2 — FINAL INTEGRATED RELEASE GATE

**Date:** 2026-09-22  
**Branch:** `feat/ask-v2-mvp`  
**Status:** ACTIVE RELEASE-LEVEL AUTHORITY  
**Canonical roadmap/report:** SEALED / UNCHANGED

This document is the release-level timing authority for expensive broad evaluation.

It supersedes any older phase-local wording that schedules DEV80:
- at the end of Day 6.5,
- before Day 7–15 backend work,
- before Jev/Metabase production-role decisions,
- or before the final integrated code candidate exists.

It does NOT renumber or rewrite the sealed canonical roadmap.

## 1. Binding economic rule

```text
DEV80 may run exactly ONCE for this release.
```

Therefore DEV80 is **not** an exploratory development test and is no longer a Day 6.5
engineering gate.

New meaning:

```text
DEV80 = FINAL BROAD ENGINEERING GATE
```

It runs only after all architecture-changing and correctness-sensitive backend work for
this release is complete and the final integrated candidate is frozen.

## 2. Current proven baseline

```text
D65-G anti-patch hardening         GREEN
provider-free family               35696652502 = 102/102 PASS
reference-floor canary             35697064833 = 16/16 PASS
Wren + Research sentinels          35697471863 = 2/2 PASS
production hybrid /ask-v2          OFF
final release freeze               NOT CREATED
DEV80                              NOT STARTED
```

Exact reference-tested semantic SHA:
`8dfde62d46d1418f05cce3ed44c26a8025b3b20e`.

These proofs are preserved as development evidence. They do not authorize final freeze.

## 3. Development testing vs final broad evaluation

### 3.1 Development loop — continuous

During implementation we continuously use small, diagnostic, high-information tests:

```text
code / architecture change
↓
focused provider-free
↓
focused REAL LLM scenario
↓
failure-family / metamorphic proof
↓
small realistic scenario set
↓
8–16 case canary when material
↓
relevant real sentinel
↓
feature accepted
↓
next feature
```

Purpose:

```text
focused provider-free = contract / invariant
focused real LLM      = real language/model behavior
failure-family        = root fix or phrase patch?
metamorphic           = generalization across wording/schema/tenant
A/B                   = model floor vs architecture owner
small canary          = nearby regression
sentinel              = critical real vertical still alive
```

These remain normal development tools.

### 3.2 Final broad gates — end only

```text
DEV80
= final broad engineering confirmation over the integrated candidate

VALIDATION50
= final unseen validation, no tuning

HIDDEN50
= final externally sealed certification, no tuning
```

DEV80 / Validation50 / Hidden50 are not debugging loops.

## 4. Updated binding release sequence

```text
CURRENT GREEN BASELINE
│
├─ D65-J1S
│    Gemini vs Jev vs Sol
│    semantic candidate decision
│
├─ D65-J1T
│    Gemini vs Jev vs Sol
│    typed temporal intent decision
│
└─ D65-M0
     Metabase adoption/source audit
         ↓
D65-X0 thin Metabase Agent API feasibility
         ↓
if promising: consult → full D65-X
         ↓
choose exactly ONE primary analytics substrate
         ↓
complete any explicitly-approved Jev / Metabase production integration
         ↓
────────────────────────────
DAY 7
Result-Aware Research Loop
+ ToolContract
+ CrossDomainJoinGate
────────────────────────────
DAY 8
HypothesisLedger / root-cause
────────────────────────────
DAY 9
ReportDocument + evidence linkage
────────────────────────────
DAY 10
Product MVP end-to-end integration
────────────────────────────
DAY 11
real-language / metamorphic eval expansion
────────────────────────────
DAY 12
QueryContract / evidence / telemetry hardening
────────────────────────────
DAY 13
tenant / PII / principal security hardening
────────────────────────────
DAY 14
persistence / resume contracts
────────────────────────────
DAY 15 CODE
pilot feature flag + rollback mechanism IMPLEMENTED
BUT FLAG REMAINS OFF
────────────────────────────
all cheap/provider-free/focused/live/metamorphic/canary/sentinel gates GREEN
         ↓
FINAL INTEGRATION REHEARSAL
20–25 hardest representative REAL LLM scenarios
+ real chosen analytics substrate execution
+ Research complex scenarios
         ↓
GREEN?
  NO  → do not start DEV80; return to normal triage/development loop
  YES ↓
FINAL ENGINEERING FREEZE CANDIDATE
         ↓
DEV80
EXACTLY ONCE
         ↓
CODE FREEZE
         ↓
VALIDATION50
NO TUNING
         ↓
external fresh HIDDEN50
NO TUNING
         ↓
CERTIFICATION SEALED
         ↓
pilot flag ACTIVATE
```

## 5. Decisions that must be closed before final freeze

Before DEV80, all of the following must be final for this release:

```text
production cognition/model roles
Jev use/reject decision
semantic decision provider topology
temporal normalization provider topology

Wren vs Metabase substrate decision
Metabase production adapter if selected

Standard / Research authority boundary
Research runtime and ToolContracts
CrossDomainJoinGate
Evidence / Completion behavior
Hypothesis / root-cause contracts
ReportDocument evidence linkage
QueryContract semantics and provenance
telemetry contracts
tenant/principal/permission propagation
PII handling
persistence / resume
pilot feature flag / rollback code
```

Any item still architecture-open means DEV80 is not allowed.

## 6. DEV80 entry gate

DEV80 is expensive final confirmation, not a discovery tool.

Required before starting:

```text
J1S/J1T resolved
M0/X0 resolved
full D65-X resolved if X0 was promising
exactly one primary analytics substrate
Day7–15 release code complete
all relevant provider-free suites GREEN
all material focused REAL LLM scenarios GREEN
failure-family / metamorphic proofs GREEN
current material 8–16 canaries GREEN
chosen substrate real sentinel GREEN
Research real sentinel GREEN
security / tenant sentinels GREEN
final 20–25 case integrated rehearsal near-perfect / accepted
final candidate SHA selected
no known architecture/correctness debt marked release-blocking
```

If the rehearsal is not strong enough:

> DEV80 DOES NOT START.

## 7. DEV80 failure rule

Normal engineering would fix a real DEV80 root cause and run a new DEV80 on a new candidate.

This release has a hard economic constraint:

```text
second DEV80 is not budgeted
```

Therefore:
- do not enter DEV80 until cheap/medium gates provide very high confidence;
- if DEV80 is RED, perform mandatory failure triage;
- do not silently patch and pretend the original DEV80 certifies changed code;
- any architecture/correctness code change after DEV80 invalidates that candidate's DEV80 proof.

Because a second DEV80 is not available for this release, a post-DEV80 correctness change is
a **release STOP condition**, not an ordinary tuning loop.

## 8. Post-DEV80 code freeze

After DEV80 starts/completes, the tested path is frozen.

Forbidden post-DEV80 changes:

```text
semantic behavior
temporal behavior
prompt / typed cognition contracts
model/provider policy
Jev policy
Gemini/Sol role policy
Wren/Metabase substrate
Retriever behavior
BindingGate authority
Standard/Research routing
Research ToolContracts
CrossDomainJoinGate
QueryContract semantics
Evidence/Completion semantics
Hypothesis/root-cause contracts
permission/tenant execution semantics
PII behavior
persistence/resume semantics
feature-flag routing semantics
```

Allowed post-DEV80:

```text
Validation50 execution
Hidden50 execution
certification receipts
deployment mechanics that do not change behavior
already-implemented feature flag activation
monitoring / observation
log analysis
non-behavioral docs
non-behavioral UI copy/polish
```

Operational config changes that alter semantic/execution behavior are not allowed.

## 9. Validation50 and Hidden50

### Validation50

```text
FINAL UNSEEN VALIDATION
```

A separate distribution that was not used to tune the implementation.

Rules:
- one final run;
- no case-driven tuning;
- no prompt/regex/model/substrate patch.

### Hidden50

```text
FINAL SEALED CERTIFICATION
```

Externally sealed/unseen distribution.

Rules:
- final certification only;
- no development access to hidden prompts;
- no tuning after results.

A RED result may block release, but does not convert the set into a development corpus.

## 10. Final integration rehearsal

Before spending DEV80 budget, run a smaller but difficult final rehearsal.

Target:

```text
20–25 cases
real LLM
highly stratified
hardest known failure families
multi-intent
ambiguity
implicit comparison
explicit comparison
follow-up
conversation repair
cross-domain relationship
unsupported request
adaptive Research branch
root-cause
report/evidence linkage
tenant/security boundary
chosen Wren/Metabase real execution
persistence/resume where relevant
```

Vary:
- Turkish wording,
- metric/dimension names,
- schema labels,
- tenant,
- paraphrases.

This rehearsal is allowed to find bugs because it is still development.
DEV80 is not.

## 11. Consultation gates

STOP and consult before:

```text
D65-J1B product integration
production model cascade or confidence threshold
full D65-X after promising X0
primary analytics substrate switch
authority/security model adoption from Metabase
moving from Day6.5 decisions into Day7 implementation if architecture choice is still open
FINAL ENGINEERING FREEZE CANDIDATE
DEV80 start
any post-DEV80 behavior-changing code/config proposal
pilot activation
```

When a material architectural choice has multiple viable paths, do not choose silently.

## 12. Relationship to current Day 6.5 authority

`DIMA_DAY6_5_PREFREEZE_DECISION_GATE_J1_M0_X0.md` remains the current authority for:
- J1S/J1T,
- M0,
- X0,
- pre-freeze cognition/substrate decisions.

This release-level document changes only the timing of **final freeze / DEV80 / validation /
certification**.

Day 6.5 may close its architecture decision work without running DEV80.
DEV80 belongs to the **final integrated release candidate after Day15 code**.

## 13. Exact next work

Current next development work after documentation approval:

```text
1. D65-J1S benchmark contract + isolated lab runner
2. D65-J1T benchmark contract + isolated lab runner
3. D65-M0 Metabase adoption matrix/source audit
4. separate J1S/J1T/M0 receipts
5. D65-X0 thin feasibility ticket
6. consult on promising J1 or X0 results before integration
7. after decisions close, continue Day7 onward
```

No product implementation starts from this document update alone.
