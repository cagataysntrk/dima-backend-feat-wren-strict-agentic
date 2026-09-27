# DIMA METABASE — NEUTRAL COMPARISON DOSSIER

Status: COMPLETE / PLATFORM COMPARISON-READY  
Date: 2026-09-27  
Platform candidate SHA: `72641b39159f11b08757048ae96644438badcc20`

This dossier describes the sealed Dima Metabase Platform candidate. It does not evaluate Wren, define a winner, or define the external comparison scoring formula.

## 1. Candidate identity

- Branch at freeze: `feat/dima-metabase-platform`
- Platform candidate SHA: `72641b39159f11b08757048ae96644438badcc20`
- Product contract: `core-b-product-v1`
- UX foundation matrix: `wave-1-comparison-ready-v2`
- Alembic head: `fc8a1d0e3b42`
- Engine SHA: `cbe313af9ac2d5960f662068e433d328d896fb06`
- Engine release: `0.63.18-dima.6`
- Engine digest: `sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353`
- Engine build identity: `github-actions:36042062775:cbe313af9ac2d5960f662068e433d328d896fb06`
- Candidate artifact: `dima-metabase-comparison-candidate`
- Candidate artifact digest: `sha256:c842390a1d3850f58805411d0c3b0c50731acf56eed51a4405e0a740bcae0dcf`

## 2. Architecture summary

The Platform is a headless organizational-intelligence product over sealed Dima authorities and a pinned Metabase/Metabot analytical runtime.

The Product facade is projection/orchestration only. It does not own a second analytics engine, a second Evidence authority, a second root-cause engine, or a second Decision authority.

Canonical headless consumer surface:

- `CompanyContext` and `CapabilityDiscovery`
- `HeadlessProductService.research_question`
- `HeadlessProductService.resume`
- deterministic `page`
- read-only `timeline`
- `OperationTrace`
- `ClosedLoopProjection`

Canonical artifact families exposed through immutable DTOs:

`WATCH → SIGNAL → RESEARCH / INVESTIGATION → EVIDENCE → EPISTEMIC_ASSESSMENT → REPORT → DECISION → ADOPTION → ACTION_WORK → OUTCOME → MEMORY`.

A missing or unjustified stronger artifact is represented as a governed limitation, inconclusive state, insufficient evidence, or another typed failure. The facade does not manufacture downstream authority artifacts for presentation completeness.

## 3. Authority ownership map

- Analytical execution: pinned Metabase / Metabot engine.
- Research contract and obligations: P14 Research.
- Exploration material: P15.
- Claim / Evidence epistemics: P16.
- Bounded investigation cognition and durable reasoning: P17.
- Business relationship interpretation: P18.
- Root-cause epistemic authority: P19.
- Report publication legality: P20.
- DecisionBrief advisory authority: P21.
- Human decision adoption: DecisionAdoption.
- External-action permission boundary: ActionAuthorization.
- Internal work lifecycle: Core A ActionWork.
- Outcome observation: Core A OutcomeObservation.
- Institutional precedent/reference memory: Core A InstitutionalMemory.
- Watch / Signal lifecycle: Core A WatchSignal.
- Product facade: projection and orchestration only.

## 4. Analytical and model topology

Analytical owner is Metabase / Metabot, pinned to dima.6.

Cognition topology for the frozen candidate:

- `openai/gpt-5.6-luna`
- no Sol
- no C1
- no model cascade

Closed-world provider schemas and typed authority IDs remain the legality boundary. Product does not add model-facing shadow turn budgets or output quotas to P17.

## 5. Research, Evidence and root-cause architecture

Research Intake compiles raw user language into closed legal semantic authority choices; arbitrary authority IDs are not accepted.

P17 exposes a typed legal action profile. Model selection is bounded by legal intents, parents and governed references. Investigation state is durable and restart-safe. Branch terminality governs branch-scoped transitions only; GLOBAL_CONTROL is not invalidated by a storage-only compatibility branch ID.

Evidence and claim lineage remain owned by sealed authorities. P19 root-cause assessment is evidence-gated and may lawfully terminate without a defensible root cause. Unsupported causal promotion is a failure, not a limitation to be hidden.

## 6. Report, Decision and closed loop

P20 controls legal report publication over the accepted analytical obligations. P21 produces advisory DecisionBrief artifacts from governed upstream material. Human Adoption is a separate authenticated human authority.

The sealed headless closed loop can project:

`WATCH → SIGNAL → INVESTIGATION → EVIDENCE → EPISTEMIC STATE → REPORT → DECISION → ADOPTION → ACTION WORK → OUTCOME → MEMORY`.

External side-effect execution is not part of the candidate. The default external Action capability registry is empty and `action:execute` is absent.

## 7. Resume, persistence and currentness

The candidate preserves durable artifact identity across restart and resume.

Verified contract properties include:

- resume reauthorizes the current principal;
- restart reconstructs the same product projection from durable identity;
- raw prompt text is not reinterpreted as durable authority during resume;
- stale source state remains visible;
- superseded artifacts remain readable as historical state where the owning contract permits;
- timeline projection is deterministic and read-only;
- pagination is deterministic;
- cross-tenant artifact access is non-oracle.

## 8. Tenant and security model

Product calls require explicit tenant binding and authenticated principal identity. Sealed owners remain the authorization source.

Foreign and missing artifacts are intentionally non-oracle where tested. The Platform comparison contract requires identical tenant/security assumptions for every candidate.

No UI/frontend layer exists in this candidate, so no UI-side authority is relied upon for security.

## 9. Headless contract inventory

Comparison-facing stable headless inventory:

- Company Context
- Capability Discovery
- Ask / Research intake
- Research resume
- Watch
- Signal
- Investigation
- Evidence
- Epistemic assessment / root-cause result
- Report
- DecisionBrief
- DecisionAdoption
- ActionWork
- OutcomeObservation
- Institutional Memory
- Artifact pagination
- Artifact Timeline / lineage navigation
- operation correlation / trace
- closed-loop projection

The contract is a Python headless service/DTO contract. A new HTTP or UI facade was deliberately not introduced merely for comparison symmetry.

## 10. UX foundation matrix

The 50-descriptor Wave-1 matrix is frozen as `wave-1-comparison-ready-v2`.

Distribution:

- HEADLESS_READY: 4
- FOUNDATION_ONLY: 2
- DATA_DEPENDENT: 27
- SPECIAL_ENGINE_DEFERRED: 15
- PRODUCTIZATION_DEFERRED: 2

This distribution is deliberately conservative. It is not a product score.

The 15 specialized-engine-deferred surfaces are:

- Smart Payment Planner — constraint optimizer
- Duplicate / Suspicious Payment and Accounting Anomaly Radar — advanced anomaly model
- 13-Week Cash Forecast — forecast service
- Customer Risk / Collection Behavior Engine — risk model
- Financial Cause-Effect / contribution investigation surface — causal contribution model
- Capacity / Bottleneck Desk — constraint optimizer
- Maintenance Prioritization / Asset Health — predictive asset model
- Energy / resource-per-unit optimization surface — resource optimizer
- Recipe Recommendation / Correction Desk — recipe matching optimizer
- Dyeing Cycle-Time Optimizer surface — cycle-time optimizer
- Color Sequence / Machine Scheduling surface — scheduling solver
- Stenter / Finishing Optimization surface — process optimizer
- Cycle Time / Throughput Optimizer surface — throughput optimizer
- Material / Color / Mold Changeover surface — changeover scheduler
- Recycled / Regrind Blend Optimizer surface — blend optimizer

These engines were not implemented to improve comparison optics.

## 11. Provider-free final closure

Final integrated provider-free run:

`36313727354 = SUCCESS`

Exact assertion counts from that run:

- repository/control-plane security: 25
- headless Product closure: 111
- Core A closed-loop + UX freeze: 70
- ActionAuthorization: 38
- Human Adoption: 29
- P21: 25
- P20: 19
- P19: 44
- P18: 24
- P17: 116
- P16: 6
- P15: 5
- P14: 15

Total: 527 passing assertions.

Canonical governance for the frozen candidate:

`36313727413 = SUCCESS`.

## 12. Live and latency evidence already available

The candidate reuses already-certified live cognition behavior because comparison-readiness work introduced no new cognition behavior.

Core-B active integrated Closure-v2:

- run `36311996172 = SUCCESS`
- 6 / 6 GREEN
- observable model-boundary units: 19
- Metabase analytical calls: 8
- silent wrong: 0
- security violations: 0
- causal overclaim: 0
- invented numeric truth: 0

Existing live receipts contain per-case timing/operational evidence suitable as historical Platform evidence. No new paid campaign was run after the current Core-B seal.

## 13. Operational dependencies

The frozen candidate depends on:

- Python 3.12 backend runtime;
- SQLModel/Alembic-backed control-plane persistence;
- pinned Metabase/Metabot dima.6 analytical runtime;
- the immutable engine image digest above;
- explicit tenant/principal setup;
- Luna cognition provider credentials only when live cognition is exercised;
- neutral analytical data fixture/database supplied by the external comparison harness.

No frontend runtime is part of this candidate.

## 14. Maintenance footprint

Primary maintained surfaces are:

- Dima backend owner modules and control-plane persistence;
- product DTO/projection/orchestration package;
- Core A closed-loop stores;
- pinned Metabase engine gitlink/runtime lock;
- Alembic migrations;
- provider-free CI/governance workflows;
- neutral comparison contract and candidate metadata.

There is no second shared analytical engine inside Product and no frontend codebase in this candidate.

## 15. Known limitations and technical debt

Known limitations/debt are explicit rather than hidden:

- connector onboarding / first Company Map remains foundation-only;
- some UX surfaces are data-dependent and require the appropriate company/domain data;
- dashboard/scheduled-intelligence productization remains deferred;
- 15 specialized-engine surfaces remain deferred;
- external side-effect execution remains productization debt;
- Resend live, Slack/ERP mutation and generic tool execution are outside this candidate;
- comparison uses the headless Python contract rather than a newly added public HTTP/UI surface;
- DEV80, Validation50 and Hidden50 were not run and are not part of this Platform comparison-ready seal.

## 16. Neutral comparison interface

Canonical input/output/environment/measurement contract:

`backend/belgeler/metabase/DIMA_METABASE_NEUTRAL_COMPARISON_INPUT_CONTRACT.md`

The external comparison authority owns the common corpus, scoring methodology and winner decision. Platform exposes measurable latency, provider calls, Metabase calls, terminal states, exceptions and artifact lineage but defines no winner formula.

## 17. Counterpart identity only

Observed Wren counterpart at Platform handoff:

- branch: `feat/ask-v2-mvp`
- observed HEAD: `8f472fb252f1f81d7357c6edcdbedf89bf60f666`

No Wren source was modified, imported or tuned for this Platform seal, and this dossier contains no comparative verdict.

## 18. Exit state

`PLATFORM INTERNAL CLOSURE = SEALED`

`PLATFORM COMPARISON CANDIDATE = SEALED`

`NEUTRAL COMPARISON = PENDING EXTERNAL AUTHORITY`

`NO WINNER WAS SELECTED HERE`

`UI IMPLEMENTATION NOT STARTED`

`PLATFORM IS READY FOR NEUTRAL COMPARISON`
