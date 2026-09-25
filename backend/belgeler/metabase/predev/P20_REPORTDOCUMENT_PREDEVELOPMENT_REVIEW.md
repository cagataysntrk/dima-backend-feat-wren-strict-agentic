# P20 — REPORTDOCUMENT / CLAIM-TO-EVIDENCE SYNTHESIS PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-25  
**Status:** **PRE-DEVELOPMENT REVIEW COMPLETE / DMP-DEC-0056 MINIMAL IMPLEMENTATION AUTHORIZED / PROVIDER-FREE FIRST**  
**Consumes:** sealed P14 + P15 + P16 + P17 + P18 + P19 authority  
**Production code in this directive:** 0  
**Tables/migrations in this directive:** 0  
**Paid model work in this directive:** Luna = 0 / Sol = 0 / C1 = 0  
**Engine/Metabase modification:** 0 / 0  
**UI/UX:** NOT AUTHORIZED

## 1. P20 exact owner boundary

P20 owns governed organizational reporting synthesis:

```text
accepted/user obligations
+ already-governed findings/claims/assessments
+ exact source lineage
+ explicit limitations
→ immutable/versioned ReportDocument
```

P20 does not own analytics, Research planning, Evidence creation, claim truth, root-cause truth,
decisions, recommendations or actions.

Permanent split:

```text
METABASE + METABOT = analytical computation/execution
P14                 = Evidence/receipt authority
P16                 = claim/evidence lineage
P17                 = investigation authority
P18                 = business-relationship eligibility policy
P19                 = epistemic/root-cause authority
P20                 = governed report synthesis / publication legality
P21                 = decisions / recommendations / actions
```

A ReportDocument may summarize upstream truth. It may never strengthen it.

## 2. Allowed input families

The first P20 vertical may reference only already-governed identities:

- accepted Research/user obligations and USER_MUST requirements;
- P14 Evidence ids plus DimaQueryReceipt provenance;
- P15 native material ids only where an upstream governed product has legally surfaced them;
- P16 claims and claim/evidence lineage;
- P17 reasoning/investigation ids only when needed to explain scope, investigation status or limits;
- P18 policy-use ids when they are part of the governed interpretation lineage;
- P19 RootCauseAssessment plus hypothesis/grounding ids;
- explicit upstream limitations.

P20 reads/references these authorities. It does not copy their truth into a new parallel authority.

## 3. Forbidden inputs and operations

P20 must not use:

```text
raw database access
SQL
MBQL
direct Metabase query execution
Metabot analytical execution
new analytical computation
trend/correlation/effect computation
join planning
relationship discovery
P17 replanning
P19 causal discovery
raw ungoverned model claims
```

If the report needs a fact that is absent from governed upstream authority, the report records an
explicit limitation. P20 does not fetch or calculate the missing fact.

## 4. Structured-first ReportClaimGate

The future first implementation should be **structured-first**. A provider, if later authorized, may
propose report organization/prose, but every publishable factual statement must be accompanied by a
typed assertion object. P20 must not infer assertion type from free prose with regex, fuzzy matching,
embeddings or another semantic classifier.

Conceptual transient statement contract:

```text
statement_id
statement_kind
text
source_refs
upstream_epistemic_ceiling
obligation_refs
limitation_refs
```

Initial statement kinds:

```text
NUMERIC
ANALYTICAL_FACT
CAUSAL
ROOT_CAUSE
CONTRIBUTION
UNCERTAINTY
LIMITATION
CONTEXT
```

The deterministic ReportClaimGate validates the declared assertion against exact upstream authority
before publication.

## 5. Numeric provenance rule

A numeric statement is publishable only when the number/unit is carried by an exact governed source
identity/path already authorized upstream.

```text
NUMERIC
→ exact P14 receipt/Evidence provenance
   OR exact governed native numeric provenance already retained by P19
→ exact value/path/unit identity
→ no P20 recomputation
```

P20 may format a governed value for presentation only when that formatting cannot change meaning.
It may not derive a percentage, delta, ranking, average, effect size or contribution share.

An LLM-generated number with no exact governed provenance is rejected.

## 6. Analytical factual statement rule

An analytical factual statement requires compatible governed claim/Evidence lineage.

```text
ANALYTICAL_FACT
→ P16 claim
→ eligible supporting/context Evidence lineage
→ no stronger wording than current P16/P19 state
```

A challenged, contested or insufficient claim remains visibly qualified. Report synthesis cannot
turn it into an established finding.

## 7. Causal wording compatibility rule

Causal language is never inferred from correlation, P17 topology or P18 policy direction.

```text
CAUSAL wording
→ compatible P19 causal qualification
→ exact P19 hypothesis/assessment grounding
→ P19 limitations preserved

ROOT_CAUSE wording
→ P19 aggregate_outcome == ROOT_CAUSE_ESTABLISHED
→ referenced root-cause hypothesis id is explicitly present in that immutable assessment
```

If P19 concludes `NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED`, P20 must preserve that conclusion or a
semantically weaker formulation. It may not write “probably X is the root cause.”

The current sealed P19 live canary itself ended
`NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED`; this is a first-class reportable result, not text to polish
away.

## 8. Contribution wording rule

Contribution and causation remain distinct.

```text
CONTRIBUTION wording
→ exact P19 CandidateAssessment
→ compatible contribution_class
→ compatible evidence_strength
→ all identification limitations retained
```

`MATERIAL` contributor does not become “root cause.” `STRONG` evidence does not become a
contribution percentage. Numeric contribution requires exact governed native numeric provenance; P20
never invents or computes one.

## 9. Uncertainty and inconclusive results

P20 must preserve:

- challenged/contested/insufficient claim status;
- P19 identification limitations;
- `MULTIPLE_MATERIAL_CONTRIBUTORS`;
- `NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED`;
- missing-required-Evidence limitations;
- stale-source limitations.

A report may improve readability. It may not remove epistemic qualifiers to sound more decisive.

## 10. USER_MUST coverage rule

Every accepted USER_MUST / mandatory obligation must have exactly one explicit report coverage
outcome:

```text
REPRESENTED
→ one or more legal report statement ids

LIMITED
→ explicit report limitation with reason/source context
```

No USER_MUST may silently disappear.

A future ReportDraft must include a deterministic coverage map:

```text
obligation_id
coverage_status = REPRESENTED | LIMITED
statement_ids
limitation_ids
```

The ReportDocument cannot seal if any mandatory obligation is unaccounted for.

## 11. Minimum durability recommendation

Default recommendation for the first P20 implementation: **one durable immutable/versioned
ReportDocument record is sufficient**.

Do not pre-authorize separate report-section, report-claim, citation-edge, report-graph or
presentation tables.

Conceptual minimum identity:

```text
report_id
research_session_id
tenant_binding
semantic_context_version
report_key
revision
parent_report_id nullable
coverage_json
statements_json
source_refs_json
limitations_json
source_set_fingerprint
report_fingerprint
created_at
```

Sections and statement/source references may remain canonical embedded JSON in the immutable report
snapshot. They reference existing truth; they are not a new claim/Evidence graph.

A separate table is justified later only by a concrete durability/query/update requirement that
cannot be satisfied by one immutable snapshot. Default answer: fewer owners, fewer tables.

No P20 table or migration is created by this directive.

## 12. Revision and immutability semantics

A sealed ReportDocument snapshot is immutable.

A new governed source set, changed mandatory obligation set, newer P19 assessment, claim state change
or source-version change does not rewrite the old report:

```text
old report = immutable historical snapshot
changed governed source set
→ prior report currentness = STALE_SOURCE_SET
→ new synthesis requires a new report revision
```

Future report identity should include a deterministic fingerprint over:
- Research authority/session;
- semantic context version;
- mandatory obligation ids;
- exact source authority ids/fingerprints/revisions;
- coverage map;
- typed statements and limitations.

No arbitrary TTL is needed. Staleness is authority-version/fingerprint based.

## 13. Source invalidation behavior

If an upstream source becomes unavailable, superseded, challenged, retired or context-incompatible:
- historical report remains readable as historical evidence of what was published;
- it cannot be silently revalidated;
- current publication eligibility fails closed or requires a new revision;
- the exact affected statement/coverage item receives an explicit limitation.

P20 does not mutate P14/P16/P18/P19 to “fix” a stale report.

## 14. P20 ReportDocument versus P21 DecisionBrief

P20 answers:

```text
What governed facts, assessments and limitations can the organization report?
```

P21 answers:

```text
Given that governed report, what should the organization decide/recommend/do?
```

P20 must not contain:
- action recommendation;
- preferred intervention;
- priority ranking for action;
- decision owner;
- execution plan;
- approval/action workflow;
- expected intervention impact invented by Dima.

Those are P21 concerns.

## 15. Provider/model role

P20 authority must be certifiable provider-free first.

A future model may be useful for:
- section ordering;
- concise connective prose;
- stylistic condensation of already-approved typed statements;
- title/summary drafting that references only legal statement ids.

The model may not decide factual legality, causal strength, numeric truth, USER_MUST coverage or
source eligibility.

High-risk numeric/causal/root-cause/contribution statements should be rendered from the approved typed
statement payload/source semantics rather than trusting free-form model wording to self-classify.

### Is a live model canary necessary?

**Not for the first P20 authority/state implementation.**

The deterministic ReportClaimGate, immutability, coverage and source-lineage contracts can and should
be proven provider-free. A later bounded model canary is justified only if a model-backed prose
realizer is actually added and its behavior cannot be fully certified through structured fixtures.
No paid model run is authorized by this review.

## 16. Provider-free test plan

A future authorized P20 implementation should prove at least:

1. every USER_MUST represented or explicitly limited;
2. missing mandatory coverage rejects report seal;
3. numeric statement without exact governed numeric provenance rejects;
4. numeric statement with exact governed provenance preserves exact value/source identity;
5. P16 challenged/contested/insufficient state cannot be strengthened;
6. correlation/association cannot become causal wording;
7. P18 SATISFIED alone cannot authorize causal wording;
8. P17 topology cannot authorize causal wording;
9. ROOT_CAUSE wording rejects unless P19 outcome is `ROOT_CAUSE_ESTABLISHED`;
10. `NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED` remains legally reportable and cannot be upgraded;
11. `MULTIPLE_MATERIAL_CONTRIBUTORS` remains plural and cannot be collapsed to a winner;
12. contribution wording remains within P19 contribution/evidence state;
13. stale source-set fingerprint makes prior report non-current without mutation;
14. exact same source/coverage/statement set reproduces report identity after restart;
15. new governed source set creates a new revision, not a rewrite;
16. P14/P16/P17/P18/P19 rows remain unchanged;
17. analytical execution calls = 0;
18. new DimaQueryReceipt writes = 0;
19. new Evidence authority writes = 0;
20. new claim/root-cause authority writes = 0;
21. engine changes/builds = 0;
22. UI/UX = 0.

## 17. Static governance plan

Future P20 production module should be statically forbidden from importing or invoking:
- Metabase/native analytical bridge/executor;
- query/MBQL/SQL planners;
- Wren/Agent API analytical execution;
- numpy/pandas/scipy/statistics as analytical shortcuts;
- P17 manager execution;
- P19 assessment mutation/creation as a side effect of reporting;
- Evidence/receipt creation APIs;
- P21 decision/action modules.

The production owner should consume typed read authority only.

## 18. STOP conditions

Return to supervisor before P20 implementation if a proposed design appears to require:

```text
raw DB analytics
SQL / MBQL generation
direct Metabase/Metabot execution
new analytical executor
new receipt family
new Evidence authority
new claim authority
new root-cause authority
P17 reopening
P18 reopening
P19 redesign
causal graph / knowledge graph
Python analytics
regex/fuzzy/morph semantic claim classification
LLM-generated numeric truth
LLM semantic self-certification of causal strength
multiple new report tables without concrete durability need
P21 decision/recommendation logic
UI / UX
Metabase core or engine modification
```

## 19. Recommended first implementation boundary

If a future supervisor authorizes P20 implementation, the smallest useful slice is:

```text
one sealed ResearchSession
+ mandatory obligation set
+ selected governed P16/P19 authority refs
+ explicit limitations
→ typed ReportDraft
→ deterministic ReportClaimGate
→ complete USER_MUST coverage
→ one immutable/versioned ReportDocument snapshot
→ provider-free restart/idempotency proof
```

No model is required for this first slice.

## 20. Current return point

```text
P19 = SEALED
P20 PRE-DEVELOPMENT = COMPLETE
P20 IMPLEMENTATION = NOT AUTHORIZED
P21 = NOT STARTED
UI / UX = FORBIDDEN UNTIL P21 SEALED
```

This review is the complete requested P20 pre-development output. It contains no production P20 code,
table, migration, model dispatch or UI work.


## 21. DMP-DEC-0056 implementation authorization

Supervisor authority on 2026-09-26 authorizes exactly the minimal provider-free vertical already
defined by this review. The design boundary is unchanged:

```text
one sealed ResearchSession
+ accepted USER_MUST obligations
+ governed P14/P16/P19 identities
+ exact source provenance
+ explicit limitations
→ typed ReportDraft
→ deterministic ReportClaimGate
→ USER_MUST accounting = 100%
→ one immutable/versioned ReportDocument
→ restart/idempotency proof
```

Authorization does not open a router, UI, model-backed prose, analytical execution, a second
Evidence/claim/root-cause authority, or any engine/Metabase core modification.

After deterministic GREEN, P20 may be sealed and P21 DECISION INTELLIGENCE pre-development review
must begin immediately. P21 implementation remains unauthorized.
