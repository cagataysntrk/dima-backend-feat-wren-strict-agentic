# DIMA BRAIN V2.1 — CURRENT HANDOFF

Updated: 2026-10-06

## 0. Final freeze status

This specification-closure candidate is now frozen for actual 30-case evaluation.

Canonical semantic Product:

`ae4e0348601774082b0270f23d6de126e71e6055`

Certified engine:

- SHA: `a54a13be978985b58aa53b3ca70a6a51ecb3de3b`
- release: `0.63.18-dima.11.2`
- runtime tag: `v0.63.18-dima.11.2.1`
- digest: `sha256:34a3acec8d9cd8743c894f3ef4314b406eaeee08c67526328a55ed8e639be763`
- certification run: `37383555448`

Acceptance-baseline backend HEAD before documentation-only freeze commits:

`5bbf02f9d088d1060ab5e388f41629337ef4e770`

Current readiness terminology:

`30-CASE EXECUTION READY = YES`

`90+ HIGH-CONFIDENCE QUALITY READY = NOT DECLARED`

`90+ PROVEN = NO`

These statements are intentionally different.

“30-CASE EXECUTION READY” means that one immutable Product+engine candidate exists, the required provider-free closure is GREEN, certified engine identity is pinned, security/currentness/dedup infrastructure is GREEN, and the evaluation infrastructure is ready to run the actual frozen 30-case.

It does **not** mean that 90+ quality has already been demonstrated.

## 1. Freeze law

From this point:

- do not change Product semantic code;
- do not change engine code/build;
- do not fix S3;
- do not add semantic families;
- do not run another sentinel panel;
- do not change prompts, grammar, LangGraph semantics, Metabot behavior or provider ceilings;
- do not run the 30-case without separate explicit user authorization.

Paid/broad authorization remains OFF.

Frontend remains NOT AUTHORIZED.

The pre-30-case perfection loop is closed.

## 2. Provider-free closure

Final accepted provider-free runs under the frozen Product plus certified dima.11.2 runtime:

- focused Brain V2: `37391242111` — GREEN
- Phase-2/headless: `37391242219` — GREEN
- Phase-1 aggregate: `37391242264` — GREEN
- frozen-family closure: `37391441309` — GREEN
- semantic conformance: `37391441484` — GREEN
  - main conformance GREEN
  - Wave A GREEN
  - independent Wave B GREEN
  - mutation canaries GREEN

Migration remains single-head:

`ff5b8e2c1a73`

## 3. Known open release-validation risk — S3

The known S3 risk is **not hidden and is not called PASS**.

Diagnostic:

- run: `37391843531`
- job: `112038501786`
- probe: `CHANGE_DEPENDENT_DRILLDOWN_V1`
- Product quality: `2/4 PARTIAL`
- mechanical verdict: RED

Observed state:

- workflow status: `WAITING`
- last node: `MATERIAL_GROUP_WAITING`
- parent obligation: `LIMITED`
- child obligation: `READY`
- native occurrence count: 1
- native occurrence status: `LIMITED`
- native acquisitions: 0
- VERIFIED Evidence: absent
- SelectionBinding: absent
- child machine drilldown: not completed

Observed safety for that diagnostic:

- exception: 0
- blocked provider requests: 0
- duplicate native: 0
- scope current: yes
- P17 provider calls: 0
- P19 provider calls: 0

This S3 result is an explicit release-validation risk. It is accepted only as an unresolved risk going into the actual frozen 30-case. It must remain visible in final adjudication.

Canonical machine-readable record:

`backend/lab/metabase/brain_v2/release_validation_manifest.json`

## 4. Authorization state

Final sentinel authorization:

OFF.

Broad paid:

OFF.

Actual frozen 30-case:

NOT AUTHORIZED YET.

Frontend:

NOT AUTHORIZED.

The difference between “execution ready” and “authorized to execute” is deliberate:

- execution readiness = technical/evaluation readiness of the frozen candidate;
- authorization = explicit permission to spend/run the actual 30-case.

## 5. Actual frozen 30-case protocol

When and only when the user explicitly authorizes it, execute exactly one frozen 30-case using the exact Product+engine identity above.

Required rules:

1. `fail-fast = false`;
2. all 30 cases must complete;
3. no fix, commit, semantic change or engine change during the corpus;
4. raw mechanical results and manual adjudication remain separate;
5. produce per-case scores;
6. produce per-family scores;
7. separately report:
   - exception;
   - silent-wrong;
   - security;
   - causal overclaim;
   - duplicate-native;
8. do not hide the known S3 risk;
9. do not mix older sentinel scores into the frozen 30-case score.

If final score is `>=90` and safety invariants are clean:

`90+ PROVEN = YES`

Then this specification-closure program closes and STOP.

If final score is `<90`:

- do not immediately start another broad fix loop;
- adjudicate all 30 cases as one corpus;
- extract only the small number of genuine root architecture families;
- wait for a separate user decision before opening implementation work.

## 6. Canonical release identity

Product semantics:

`ae4e0348601774082b0270f23d6de126e71e6055`

Engine:

`a54a13be978985b58aa53b3ca70a6a51ecb3de3b`

Release:

`0.63.18-dima.11.2`

Digest:

`sha256:34a3acec8d9cd8743c894f3ef4314b406eaeee08c67526328a55ed8e639be763`

Grammar:

`dima_analytical_grammar_v1`

AnalyticalIntent:

`dima_analytical_intent_v1`

ExecutionManifest:

`dima_analytical_execution_manifest_v1`

SelectionBinding:

`dima_selection_binding_v1`

Model topology:

- Dima cognition: `openai/gpt-5.6-luna`
- Metabot: `openrouter/openai/gpt-5.6-luna`
- cascade: NONE

## 7. One-line handoff

`FROZEN: Product ae4e0348... + certified dima.11.2; provider-free closure GREEN; known S3 = 2/4 PARTIAL and explicitly recorded; 30-CASE EXECUTION READY = YES; 90+ PROVEN = NO; all paid/broad authorization OFF; actual frozen 30-case requires separate explicit user permission; STOP.`
