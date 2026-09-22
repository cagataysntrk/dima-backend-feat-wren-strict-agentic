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

failure_class: `PENDING: MODEL_CAPABILITY_FLOOR vs CONTRACT/ARCHITECTURE`

classification_evidence:
- Manager draft correctly produced one comparison obligation.
- Metric resolved.
- Explicit PERIOD surface `son 12 ay` resolved to a governed period handle.
- Comparison surface remained unresolved.
- Typed temporal normalizer uses SEMANTIC_LINKER role, currently `google/gemini-2.5-flash-lite`.
- Infra/provider/harness failures are zero.

single_owner: `PENDING A/B — typed temporal normalizer / SEMANTIC_LINKER model-role boundary`

root_cause: `PENDING exact-same-SHA semantic-linker model-floor A/B`

failure_family:
Explicit-base comparison surfaces where base period is already governed but bounded temporal normalization of the reference relation may abstain or mis-normalize.

why_not_model_only: `Not yet proven; same-SHA stronger linker A/B required.`

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

allowed_files_to_touch: `NONE until A/B classification closes`

files_not_to_touch: `all semantic/product files until classification`

invariant_being_fixed: `PENDING`

focused_proof: `PENDING`

family_regression_proof: `PENDING`

status: `OPEN — NO PRODUCT PATCH ALLOWED`

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

status: `CLASSIFIED — patch allowed only at stated owner after current hardening/sequence decision`
