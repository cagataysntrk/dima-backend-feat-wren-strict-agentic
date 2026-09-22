# DIMA V2 — DAY 6.5 FAILURE TRIAGE RECEIPTS

> Amaç: live/canary/DEV/Validation/Hidden RED sonrasında semantic/product code değişmeden önce
> zorunlu owner/root-cause kaydı.
>
> Binding rule:
>
> ```text
> RED
> ↓
> NO PRODUCT/SEMANTIC CODE CHANGE
> ↓
> FAILURE TRIAGE RECEIPT
> ↓
> same-SHA A/B if needed
> ↓
> failure_class + single_owner + root_cause determined
> ↓
> only then allowed code change
> ↓
> focused proof
> ↓
> family/metamorphic proof
> ```
>
> ONE FAILURE ≠ ONE NEW RULE.
> Yeni mekanizma ancak aynı kök nedenle farklı wording/schema/tenant yüzeylerinde oluşabilecek
> failure family tanımlanabiliyorsa eklenebilir.

## Mandatory receipt schema

```text
run_id
tested_sha
observed_failure
failure_stage
failure_class
classification_evidence
single_owner
root_cause
failure_family
why_not_model_only
why_not_oracle
why_not_transport
forbidden_patch_alternatives
allowed_files_to_touch
files_not_to_touch
invariant_being_fixed
focused_proof
family_regression_proof
status
```

`failure_class` allowed values:

```text
MODEL_COGNITION
MODEL_CAPABILITY_FLOOR
CONTRACT/ARCHITECTURE
RESOLVER_TRUTH
EVAL_ORACLE
TRANSPORT/PROVIDER
```

Prompt change rule:

Allowed:
```text
root cause = generic contract representation gap
→ typed schema/contract changes
→ prompt changes only to describe the new generic contract
→ paraphrase/metamorphic proof
```

Forbidden:
```text
failed phrase/example copied into prompt
case-ID instruction
test wording taught to the model
keyword/regex patch
repeated prompt micro-patches in lieu of fixing the owner abstraction
```

---

## Receipt — D65-LIVE-026 — retrospective process closure

run_id: `35693815578`

tested_sha: `dea7ba673ba64280c3e58037705c31db99c733aa`

observed_failure: `d65-dev-026` — comparison surface had no explicit PERIOD surface; comparison remained unresolved.

failure_stage: `FINITE_PRE_ACCEPTANCE → AUTO_GROUND → typed temporal comparison binding`

failure_class: `CONTRACT/ARCHITECTURE`

classification_evidence:
- Manager draft correctly produced breakdown + comparison obligations.
- Metric/dimension bindings resolved.
- Comparison surface reached typed temporal path.
- Deterministic resolver required an externally supplied `base_period_handle`.
- Valid comparison surface could semantically determine a natural base interval, but typed comparison contract had no representation for it.
- Infra/provider/harness errors were zero.

single_owner: `app/v2/temporal_intent.py + app/v2/manager_semantics.py typed temporal contract boundary`

root_cause:
`TemporalNormalizationChoice(COMPARISON)` represented only reference-relation semantics and assumed an already-governed external base period. It could not represent a comparison surface that itself determines a natural base interval.

failure_family:
Any valid comparison wording/language/tenant where a typed temporal comparison has no separate explicit PERIOD surface but the comparison surface itself unambiguously determines its natural base interval.

why_not_model_only:
Changing the linker model could not create a base-period representation that did not exist in the typed contract.

why_not_oracle:
Expected STANDARD_LOSSLESS behavior matches intended product semantics; no evidence the case expectation was malformed.

why_not_transport:
measurement/model/grounding/harness transport counters were healthy.

forbidden_patch_alternatives:
- phrase-specific temporal rule
- regex/keyword temporal parser
- hidden fallback to legacy SemanticResolver
- case-derived prompt example

allowed_files_to_touch:
- `app/v2/temporal_intent.py`
- `app/v2/manager_semantics.py`
- typed temporal/provider-free tests
- generic contract description in temporal system prompt

files_not_to_touch:
- legacy `app/v2/resolver.py`
- Research Manager loop/tool/completion semantics
- DEV expected label for `d65-dev-026`

invariant_being_fixed:
A valid comparison must be representable without inventing semantic truth; language normalization remains bounded/model-based while calendar arithmetic remains deterministic.

focused_proof: `35694536321 = 45/45 PASS`

family_regression_proof: `35694712657 = 97/97 PASS`

status:
`CLOSED — root fix implemented; process receipt added retrospectively because original receipt ordering was violated.`

Process note:
The original implementation occurred before this formal receipt was committed. That ordering was a process violation even though the technical root fix was architecture-level. It must not be repeated.

---

## Receipt — D65-CANARY-019

run_id: `35695029547`

tested_sha: `f5ca942f83aaee0806d7119957c543ab17a59a37`

observed_failure:
`d65-dev-019` — explicit base period resolved; comparison surface remained unresolved; terminal CLARIFICATION_REQUIRED.

failure_stage: `FINITE_PRE_ACCEPTANCE → AUTO_GROUND → typed temporal comparison binding`

failure_class: `MODEL_CAPABILITY_FLOOR`

classification_evidence:
- Manager draft correctly produced one comparison obligation.
- Metric resolved.
- Explicit PERIOD surface `son 12 ay` resolved to a governed period handle.
- Comparison surface remained unresolved.
- Typed temporal normalizer uses SEMANTIC_LINKER role, currently `google/gemini-2.5-flash-lite`.
- Infra/provider/harness failures are zero.

single_owner: `SEMANTIC_LINKER model-role capability floor for typed temporal normalization`

root_cause: `google/gemini-2.5-flash-lite is below the demonstrated capability floor for this explicit-base typed comparison; openai/gpt-5.6-sol passes on the exact same backend SHA.`

failure_family:
Explicit-base comparison surfaces where base period is already governed but bounded temporal normalization of the reference relation may abstain or mis-normalize.

why_not_model_only: `It IS model-floor: exact-same-SHA diagnostic run 35695366379 failed with flash-lite linker and passed with Sol linker.`

why_not_oracle:
Expected comparison semantics are coherent and an explicit base period exists.

why_not_transport:
measurement/model/grounding/harness infrastructure counters are zero.

forbidden_patch_alternatives:
- comparison keyword/regex rules
- phrase-specific prompt example
- DEV expected-output weakening
- legacy resolver fallback
- changing deterministic date arithmetic before owner classification

allowed_files_to_touch: `No semantic/product correctness patch. Model-role policy/eval documentation only if a floor is formally changed.`

files_not_to_touch: `typed temporal contract, resolver/binding logic, prompts, DEV oracle; no correctness patch justified by this case.`

invariant_being_fixed: `Architecture remains unchanged; the measured model floor is recorded instead of patching code to compensate for a weaker model.`

focused_proof: `35695366379 — d65-dev-019: flash-lite linker FAIL, Sol linker PASS on exact f5ca942 SHA.`

family_regression_proof: `No code change; existing 97/97 provider-free family proof remains applicable to the tested semantic SHA.`

status: `CLOSED — MODEL_CAPABILITY_FLOOR; no product correctness patch.`

---

## Receipt — D65-CANARY-073

run_id: `35695029547`

tested_sha: `f5ca942f83aaee0806d7119957c543ab17a59a37`

observed_failure:
`d65-dev-073` — corrective turn ended CLARIFICATION_REQUIRED after CoverageVeto forced an exclusion rewrite.

failure_stage: `FINITE_PRE_ACCEPTANCE → CoverageVeto / repair-versioning interaction`

failure_class: `CONTRACT/ARCHITECTURE`

classification_evidence:
- Attempt 1 drafted expected required performance obligation for `brüt gelirdi`.
- Metric binding resolved.
- CoverageVeto asserted prior `Net Gelir` rejection was missing.
- Attempt 2 added a new EXCLUDED performance obligation sourced only from corrective discourse.
- That EXCLUDED obligation had no semantic metric surface and failed required-kind grounding.
- Expected corpus contract contains one required performance obligation and no exclusion.
- No provider/harness/grounding infrastructure failure occurred.

single_owner: `manager_preacceptance CoverageVeto policy at the user-repair / exclusion boundary`

root_cause:
Coverage treats a corrective discourse act that supersedes a prior focus as if it must become a new explicit business exclusion obligation. This conflates conversation repair/versioning with immutable current-turn exclusion semantics.

failure_family:
Multi-turn corrective utterances where the user replaces/corrects a prior semantic focus without issuing an independent business exclusion requirement.

why_not_model_only:
Attempt 1 cognition already produced the expected replacement obligation. Failure was introduced after that by veto policy.

why_not_oracle:
Corpus expectation matches repair semantics: replace prior focus; do not invent a new excluded business obligation from bare corrective discourse.

why_not_transport:
measurement/model/grounding/harness infrastructure counters are zero.

forbidden_patch_alternatives:
- special-case corrective keyword logic
- prompt example containing failing phrase
- case-ID branch
- silently ignoring all exclusions
- legacy resolver fallback

allowed_files_to_touch:
- `app/v2/manager_preacceptance.py` only at generic repair-vs-exclusion contract boundary
- generic repair/coverage provider-free tests
- conversation/repair contract types only if proven necessary

files_not_to_touch:
- semantic linker/resolver truth
- temporal engine
- StandardBuilder runtime kernel
- Research Manager execution/evidence/completion
- DEV expected label for `d65-dev-073`

invariant_being_fixed:
Coverage is veto-only for omitted user obligations/exclusions; it may not transform a conversation repair/supersession cue into a new semantic business exclusion.

focused_proof: `PENDING`

family_regression_proof: `PENDING`

status: `CLASSIFIED — CONTRACT/ARCHITECTURE; patch allowed only at repair/coverage owner after D65-G hardening.`

Additional same-SHA diagnostic evidence:
- run `35695366379`, exact `f5ca942...`, same Sol Manager: `FAIL / PASS / FAIL` across three repeats.
- Repeat 1: first draft correct; CoverageVeto demanded preservation of prior-focus rejection, then revision emitted an EXCLUDED obligation.
- Repeat 2: passed.
- Repeat 3: first draft itself emitted required `brüt gelir` plus an EXCLUDED obligation sourced only from corrective discourse.
- Semantic-linker calls were zero in these runs; resolver/linker truth is not the owner.

This stochastic split is itself evidence of a representation/policy ambiguity: current finite pre-acceptance draft has obligations/directives/control requests but no first-class repair/supersession semantic. Corrective conversation state is therefore probabilistically forced into either ordinary replacement or business EXCLUDED obligation.

---

## Receipt — D65-REPAIR-FOCUSED-STALE-FIXTURE

run_id: `35695921829`

tested_sha/workflow head: `8ec2b86bb01e159eb80a272afb591612a36ff48b`

observed_failure:
`13 failed, 34 passed`; every failure raised `TypeError: ManagerSemanticResolutionAdapter.__init__() got an unexpected keyword argument 'resolver'` from the shared preacceptance test fixture.

failure_stage: `TEST HARNESS / provider-free fixture construction before semantic assertions`

failure_class: `EVAL_ORACLE`

classification_evidence:
- D65-G intentionally removed the inert `resolver` constructor seam from Manager semantics.
- All 13 failed tests stop at the same fixture constructor call.
- No tested repair/coverage assertion is reached.
- Compile passed.
- 34 sibling tests passed.

single_owner: `tests/test_v2_day6_5_preacceptance_protocol.py shared fixture`

root_cause:
Test fixture still encoded the superseded ManagerSemanticResolutionAdapter constructor contract after D65-G physically removed the legacy resolver dependency.

failure_family:
Provider-free tests/fixtures that construct the Manager semantic adapter using the removed legacy resolver injection seam.

why_not_model_only: `No model call owns this TypeError.`

why_not_oracle: `It IS EVAL_ORACLE/test-harness drift; product contract deliberately changed.`

why_not_transport: `No provider/transport path is reached.`

forbidden_patch_alternatives:
- re-add resolver parameter to production for test compatibility
- optional ignored resolver shim
- legacy fallback restoration

allowed_files_to_touch:
- `tests/test_v2_day6_5_preacceptance_protocol.py` fixture/import cleanup
- other provider-free fixtures only if they pass the removed constructor argument

files_not_to_touch:
- `manager_preacceptance.py` behavior
- `manager_semantics.py` production constructor
- resolver/linker truth
- eval expected semantic labels

invariant_being_fixed:
Tests must consume the same no-legacy-resolver Manager hot-path contract as production.

focused_proof: `35696222877 = 59/59 PASS after fixture alignment`

family_regression_proof: `35696652502 = 102/102 PASS on exact ffbdc224...`

status: `CLOSED — EVAL_ORACLE fixture drift removed; production no-resolver seam retained.`

---

## Receipt — D65-G-FOCUSED-STALE-FIXTURE

run_id: `35695990688`

workflow head: `63b84ad47b76d5326a365318ccdb03d01e76e690`

observed_failure:
`13 failed, 36 passed`; all 13 failures are the same removed-constructor TypeError from `tests/test_v2_day6_5_preacceptance_protocol.py`.

failure_stage: `TEST HARNESS fixture construction`

failure_class: `EVAL_ORACLE`

classification_evidence:
- D65-G compile passed.
- Anti-legacy architecture test was reached; failures listed only preacceptance fixture tests.
- Every failed test stops at `resolver=SemanticResolver(...)` before semantic assertions.
- Same stale fixture family already classified by `D65-REPAIR-FOCUSED-STALE-FIXTURE`.

single_owner: `tests/test_v2_day6_5_preacceptance_protocol.py shared _loop fixture`

root_cause:
Provider-free test fixture encoded the intentionally removed legacy resolver constructor seam.

failure_family:
All tests instantiating ManagerSemanticResolutionAdapter with the superseded `resolver=` dependency.

why_not_model_only: `No model call owns constructor TypeError.`

why_not_oracle: `It IS EVAL_ORACLE/test fixture drift.`

why_not_transport: `Provider path is not reached.`

forbidden_patch_alternatives:
- restore production resolver parameter
- accept-and-ignore compatibility shim
- fallback to legacy resolver

allowed_files_to_touch: `provider-free fixture/import cleanup only`

files_not_to_touch:
- `manager_semantics.py` no-resolver production contract
- `manager_preacceptance.py` semantics
- semantic linker/resolver truth

invariant_being_fixed:
Test code must exercise the physically isolated Manager authority boundary.

focused_proof: `35696222877 = 59/59 PASS`

family_regression_proof: `35696652502 = 102/102 PASS`

status: `CLOSED — fixture-only fix applied; production no-resolver seam retained.`

---

## Receipt — D65-G-FAMILY-STALE-FIXTURES

run_id: `35696376312`

tested_sha: `5834b0acae315afa94741c409f07bfe448c0c316`

observed_failure:
`2 failed, 100 passed, 5 warnings`; both failures are removed-constructor TypeErrors.

failure_stage: `provider-free test fixture construction`

failure_class: `EVAL_ORACLE`

classification_evidence:
- Compile passed.
- 100 provider-free tests passed.
- `test_v2_day6_5_correctness_closure.py` passed obsolete `resolver=SemanticResolver(...)`.
- `test_v2_day6_5_adaptive_branch.py` passed obsolete `resolver=SemanticResolver(...)`.
- Both stop before semantic assertions.

single_owner: `provider-free test fixtures that still encode the removed Manager resolver seam`

root_cause:
D65-G intentionally removed the inert legacy resolver dependency, while two broader family fixtures still constructed the old adapter signature.

failure_family:
Any test-only ManagerSemanticResolutionAdapter constructor still injecting `SemanticResolver` after the hot-path seam removal.

why_not_model_only: `No model/provider path owns constructor TypeError.`

why_not_oracle: `It IS EVAL_ORACLE/test fixture drift.`

why_not_transport: `No transport failure; provider-free test setup fails locally.`

forbidden_patch_alternatives:
- restore production resolver arg
- compatibility shim that accepts/ignores resolver
- reintroduce legacy fallback

allowed_files_to_touch:
- test files containing obsolete ManagerSemanticResolutionAdapter resolver injection
- test-only obsolete SemanticResolver imports used solely for that injection

files_not_to_touch:
- Manager production no-resolver contract
- semantic linker/resolver behavior
- repair/temporal/product semantics

invariant_being_fixed:
All test surfaces must exercise the same physically isolated Manager semantic authority boundary.

focused_proof: `59/59 PASS on combined focused closure 35696222877`

family_regression_proof: `35696652502 = 102/102 PASS on exact ffbdc224066dc4c85a9e46b510ae3535f83f3416`

status: `CLOSED — remaining stale family fixtures removed; no production compatibility shim added.`

---

## Receipt — D65-CANARY16-HARNESS-STALE-RESOLVER

run_id: `35696811902`

tested_sha: `ffbdc224066dc4c85a9e46b510ae3535f83f3416`

observed_failure:
`16 selected / 0 evaluable / 16 HARNESS_FAILURE`; every case failed before model invocation with `TypeError: ManagerSemanticResolutionAdapter.__init__() got an unexpected keyword argument 'resolver'`.

failure_stage: `live evaluator harness construction`

failure_class: `EVAL_ORACLE`

classification_evidence:
- `model_failures = 0`
- `grounding_failures = 0`
- `harness_failures = 16`
- `total_model_calls = 0`
- all 16 cases share identical constructor TypeError
- provider-free product family at same semantic code state already passed 102/102

single_owner: `backend/lab/v2_day6_5_manager_eval.py live harness adapter construction`

root_cause:
D65-G physically removed the legacy resolver constructor seam from Manager semantics, but the live eval harness still encoded the superseded constructor.

failure_family:
Any non-production lab/eval harness instantiating ManagerSemanticResolutionAdapter with the removed `resolver=` dependency.

why_not_model_only: `No model calls occurred.`

why_not_oracle: `It IS evaluator/harness drift.`

why_not_transport: `Provider transport was never reached.`

forbidden_patch_alternatives:
- restore resolver arg in production
- compatibility shim
- semantic testcase weakening

allowed_files_to_touch:
- `backend/lab/v2_day6_5_manager_eval.py` stale constructor/import cleanup
- other lab-only harnesses if scan finds same obsolete injection

files_not_to_touch:
- Manager semantic production contract
- temporal/linker/repair behavior
- DEV expected labels

invariant_being_fixed:
Live evaluator must exercise the same physically isolated no-legacy-resolver Manager path as production/lab HTTP harness.

focused_proof: `PENDING rerun`

family_regression_proof: `102/102 provider-free product family already GREEN on ffbdc224`

status: `CLASSIFIED — harness-only cleanup allowed`


---

## Receipt — D65-J1-FULL-001 — corrected primary full bakeoff RED

run_id: `35705668833`

tested_sha: `bde3e5a21c159243002ef600ece007256d8482d0`

observed_failure:
Workflow concluded RED because J1T contract-fidelity harness reported 6 Gemini and 2 Luna
records as `provider_failure_count`.

failure_stage:
`lab/v2_day6_5_j1_benchmark.py::_chat_temporal_contract → TemporalNormalizationChoice.model_validate`

failure_class: `EVAL_ORACLE`

classification_evidence:
- All J1S/J1T choice runs completed with provider_failure_count = 0.
- The eight contract-fidelity records labeled HARNESS_OR_TRANSPORT_FAILURE carry Pydantic
  `ValidationError`, not HTTP/network/provider errors.
- The model returned a parseable structured object; the object violated product cross-field
  invariants (for example COMPARISON without comparison_kind).
- The harness broad exception branch mapped both transport exceptions and product-model
  validation failures to `TRANSPORT/PROVIDER`.
- Therefore workflow RED is measurement classification drift.
- Underlying invalid typed outputs remain real `MODEL_COGNITION / INVALID_TYPED_CONTRACT`
  evidence and must count as wrong contract answers, not disappear from the denominator.

single_owner:
`backend/lab/v2_day6_5_j1_benchmark.py::_chat_temporal_contract` measurement/error classifier.

root_cause:
The eval boundary does not distinguish provider transport failure from a model response that is
JSON-decodable / provider-schema-accepted but rejected by Pydantic's cross-field validator.

failure_family:
Any structured model response that passes provider JSON shape but violates a Pydantic
`model_validator` / cross-field product invariant.

why_not_model_only:
The invalid model outputs themselves are model cognition failures, but they should produce an
evaluable wrong answer. The reason the *run* became infrastructure-incomplete/RED is the harness
misclassification.

why_not_oracle:
N/A — this receipt explicitly classifies the run-level failure as `EVAL_ORACLE`.

why_not_transport:
No failing record contains an HTTP status, timeout, connection error or provider rejection.
Every reported "transport" record contains a local Pydantic `ValidationError`.

forbidden_patch_alternatives:
- product temporal enum change
- product `TemporalNormalizationChoice` weakening
- case-specific expected-output change
- prompt micro-patch
- regex/keyword temporal parser
- removing invalid cases from denominator
- counting invalid contract output as provider failure

allowed_files_to_touch:
- `backend/lab/v2_day6_5_j1_benchmark.py`
- `backend/tests/test_v2_day6_5_j1_benchmark.py`
- J1 eval/receipt documentation

files_not_to_touch:
- `app/v2/temporal_intent.py`
- `app/v2/semantic_linker.py`
- BindingGate / authority models
- frozen J1S/J1T corpora
- production model topology

invariant_being_fixed:
`transport/provider failure != invalid typed model answer`.
Invalid typed model output stays in the semantic/contract denominator.

focused_proof:
`35709387862 = 8/8 PASS`; `python -m py_compile lab/v2_day6_5_j1_benchmark.py` PASS.

family_regression_proof:
The frozen J1 provider-free contract suite is the relevant eval-family proof: `35709387862 = 8/8 PASS`. Primary paid J1 was deliberately NOT rerun; historical artifacts were deterministically reclassified.

status:
`CLOSED — eval-only classifier fixed at ebf229545ae91b9b0e202810ed8acb17eee62f86; provider-free run 35709387862 = 8/8 PASS; stored full-run artifacts reclassified without paid rerun; product semantic/temporal/authority code untouched.`


---

## Receipt — D65-J1T-TERRA-001 — conditional run transport RED

run_id: `35709612688`

tested_sha: `4a66d979a47cca4e7f499aabf383d2b0b7e26dfc`

observed_failure:
All Terra J1T-CHOICE calls failed before semantic evaluation; contract-fidelity did not start.

failure_stage:
`OpenRouter chat request → HTTP 402`

failure_class: `TRANSPORT/PROVIDER`

classification_evidence:
- 58/58 J1T choice attempts returned HTTP 402.
- OpenRouter error states the request reserved up to 65536 output tokens while the API-key
  spend limit could fund only a smaller maximum.
- No Terra choice was returned; evaluable_case_count = 0.
- Corpus, prompt, ontology and product code were not implicated.

single_owner:
`backend/lab/v2_day6_5_j1_benchmark.py` chat transport output-token budget.

root_cause:
The bounded-decision lab request omitted an explicit output token cap, allowing provider/model
defaults to advertise an economically irrelevant 65536-token maximum for a tiny JSON schema.

failure_family:
Bounded structured eval calls to higher-cost chat models where provider billing/credit checks use
the maximum possible output reservation rather than expected tiny JSON output.

why_not_model_only:
No model response exists.

why_not_oracle:
Expected labels were never evaluated.

why_not_transport:
It IS transport/provider/environment; HTTP 402 is explicit.

forbidden_patch_alternatives:
- adding Terra-specific prompt wording
- removing frozen cases
- changing expected outputs
- increasing semantic authority
- running J1S Terra
- changing product temporal code

allowed_files_to_touch:
- `backend/lab/v2_day6_5_j1_benchmark.py`
- focused J1 benchmark tests
- eval receipts/workflow only

files_not_to_touch:
- J1S/J1T frozen corpora
- `app/v2/temporal_intent.py`
- `app/v2/semantic_linker.py`
- BindingGate / authority code
- production topology

invariant_being_fixed:
Bounded decision JSON transport uses an explicit small output budget independent of model price.

focused_proof:
`35709903058 = 9/9 PASS`; harness compile PASS.

family_regression_proof:
Frozen J1 provider-free eval family `35709903058 = 9/9 PASS`.

status:
`CLOSED — generic bounded chat output cap added at 26ac500eb9cef53c50e4cfc2128b18ca2105a0b3; provider-free run 35709903058 = 9/9 PASS; no corpus/prompt/product semantic change.`


---

## Receipt — D65-J1B-REALFLOW-001 — silent semantic wrong / temporal instability

run_id: `35713785149`

tested_sha: `09c9128bd385a83c099b18855636b703d73bec48`

failure_class:
- semantic = `MODEL_COGNITION`
- temporal = `MODEL_COGNITION / REAL_FLOW_TEMPORAL_INSTABILITY`
- architecture/security = no breach observed
- transport/provider = clean

single_owner:
- Jev bounded semantic decision cognition for semantic RED.
- Terra typed temporal cognition for the two real-flow unresolved comparisons.

root_cause:
Jev safely stays inside the candidate set but over-selects on under-specified / multiply-plausible
surfaces. BindingGate cannot infer intent ambiguity after a valid in-set selection. Terra's
comparison normalization also failed twice in the real adapter flow despite earlier frozen J1T
success.

failure_family:
- ambiguous generic metric surfaces;
- multiple plausible candidate surfaces;
- under-specified measure names;
- temporal previous-period comparison under a separately resolved base period.

forbidden_patch_alternatives:
- case-specific keyword/regex logic;
- prompt sentence describing these failed examples;
- threshold derived from J1/J1B;
- silent Jev→Gemini/Luna fallback;
- Terra→Sol fallback;
- weakening BindingGate/temporal authority;
- modifying frozen corpora after result.

status:
`STOP / CONSULTATION REQUIRED`.



---

## Receipt — D65-POSTJ1B-LUNA-001 — semantic GREEN / temporal RED

run_id: `35716056419`

tested_sha: `c256ebfda765ac35f1d3b51f59d53d1018dd695e`

frozen corpus:
`eval/v2_day6_5_j1b_real_flow_frozen.json`
blob `cc68f87271dcaada1443d2cf9e48024b85bff9f3`

provider-free:
`31/31 PASS`; compile PASS.

semantic result:
```text
model                        openai/gpt-5.6-luna
cases                        20/20 correct
silent_semantic_wrong        0
unsafe_ambiguity_auto_pick   0
candidate_escape             0
cross_tenant_leak            0
provider_failure             0
invalid_typed_contract       0
hidden_fallback              0
```

semantic classification:
`GREEN / engineering candidate`.
No semantic Sol ceiling is authorized/needed.

temporal result:
```text
model                        openai/gpt-5.6-luna
scenarios                    6/8 correct
real_flow_temporal_wrong     2
invalid_typed_contract       0
provider_failure             0
hidden_fallback              0
```

failed family:
- `tf-001` — "bu ay" + "önceki dönemle karşılaştır": period bound, comparison unresolved.
- `tf-002` — "son 30 günü" + "önceki dönemle karşılaştır": period bound, comparison unresolved.

cross-model observation:
Terra J1B real-flow failed the exact same two scenarios with provider_failure=0.
This repeated failure across Terra and Luna raises a material
`CONTRACT/ARCHITECTURE vs MODEL_COGNITION` ownership question.

failure_class:
`UNRESOLVED — exact-same-SHA Sol temporal reference ceiling required`.

single_owner before A/B:
none assigned yet; do not patch temporal product/prompt/schema.

forbidden alternatives:
- temporal prompt micro-patch;
- special-case "önceki dönem" branch;
- regex/keyword temporal fallback;
- changing expected scenarios;
- running Gemini;
- retuning Terra;
- semantic-provider changes;
- confidence threshold/cascade/fallback.

authorized next proof:
Sol REFERENCE_CEILING, temporal role only, same frozen 8, same tested backend SHA
`c256ebf...`.

status:
`CLOSED — exact-same-SHA Sol temporal ceiling run 35716502261 = 8/8 P0=0. Luna/Terra temporal RED for this family classified MODEL_CAPABILITY_FLOOR / MODEL_COGNITION. No temporal patch.`.



---

## Receipt — D65-POSTJ1B-SOL-TEMPORAL-001 — exact-SHA model-floor closure

run_id: `35716502261`

tested_backend_sha:
`c256ebfda765ac35f1d3b51f59d53d1018dd695e`

same frozen J1B temporal scenarios:
`8`

result:
```text
correct                    8/8
real_flow_temporal_wrong   0
invalid_typed_contract     0
provider_failure           0
hidden_fallback            0
```

exact-same-SHA A/B:
```text
Luna 6/8
Sol  8/8
```

Terra had also produced 6/8 on the same failure family.

failure_class:
`MODEL_CAPABILITY_FLOOR / MODEL_COGNITION`.

No product temporal architecture patch is justified by this family.

status:
`CLOSED`.


---

## Receipt — D65-SI-FOCUSED-001 — focused provider-free oracle RED

run_id: `35718301249`

tested_sha: `99bd9935b972b8c04336e5ce53fe805ca491f7f1`

observed:
```text
compile                 PASS
focused tests           21 PASS / 4 FAIL
provider/LLM calls      0
```

failure_class: `EVAL_ORACLE`

failures:
1. `test_standard_lane_module_has_no_research_authority_dependencies`
   - raw `inspect.getsource()` searched forbidden class-name strings;
   - names occur only in the module docstring explaining the prohibition;
   - actual imports are clean.
2. `test_standard_execution_module_has_no_research_authority_dependency`
   - same raw-source/docstring false positive;
   - actual imports are clean.
3. `test_standard_intent_draft_is_closed_and_typed`
   - fixture supplied enum name `PERFORMANCE`;
   - Pydantic contract correctly requires enum value `performance`.
4. `test_research_capability_stops_without_standard_authority`
   - same stale fixture supplied `RELATIONSHIP` instead of `relationship`;
   - draft validation failed before the research-routing assertion.

single_owner:
`backend/tests/test_v2_day6_5_standard_lane.py` and
`backend/tests/test_v2_day6_5_standard_execution.py`.

root_cause:
New SI contract is correct; focused tests encoded source-text and enum-name assumptions instead of
import AST / actual enum values.

product/architecture evidence:
- all SI modules compiled;
- no provider/model/DB execution was involved;
- no evidence of Standard authority, builder, coverage or execution semantic failure.

allowed patch:
- test-only: inspect Python imports via AST instead of docstring/source substring;
- test fixtures use canonical enum values.

forbidden patch:
- editing `standard_lane.py` or `standard_execution.py` to hide words from docstrings;
- weakening Pydantic enums;
- changing capability registry;
- semantic/prompt/Resolver changes.

status:
`CLOSED — test-only oracle patch; rerun 35718675540 = 25/25 PASS, compile PASS; product SI code unchanged by the repair`.

