# DIMA Day 6.5 — Cognition / Semantic Authority Boundary ADR

**Status:** ACCEPTED FOR DAY 6.5 IMPLEMENTATION — LIVE/DEV80 RECERTIFICATION PENDING  
**Date:** 2026-09-22  
**Scope:** V2 Manager pre-acceptance semantic + temporal interpretation boundary  
**Sealed roadmap/report:** unchanged. This ADR refines implementation ownership; it does not replace the sealed target architecture.

---

## 1. Decision trigger

DEV80 analysis showed a structural mismatch between high-level language cognition and
downstream acceptance:

- expected ACCEPTED: 66,
- final Manager draft with correct high-level capability set: 61/66,
- actually ACCEPTED: 46/66,
- expected clarification: 14,
- actual clarification: 31,
- 16 of 21 failed cases already had the correct high-level Manager intent shape.

The dominant failure class therefore was not simply “Manager cannot understand the user”.
Correctly understood intent was often blocked by two misplaced responsibilities:

1. deterministic natural-language interpretation inside SemanticResolver
   (fuzzy ratios, morphology/stemming, token/substring matching);
2. probabilistic Coverage critic deciding whether unresolved semantic material is a
   contract blocker.

This creates the same failure mode V2 was intended to eliminate: language heuristics become
hidden semantic authority and every new phrase invites another score/regex/case patch.

---

## 2. Canonical boundary

The permanent Day 6.5 rule is:

> **Models may interpret bounded language. Deterministic components verify and confer authority.**

Ownership:

```text
Semantic Catalog
  = truth about what concepts exist

Intent Drafter / Semantic Linker
  = probabilistic interpretation of what the user meant

Semantic Binding Gate
  = authority to accept a bounded interpretation

Capability Algebra / Conflict / Completeness Gates
  = authority over executable contract validity

Typed Temporal Normalizer
  = probabilistic language → closed temporal intent

Temporal Binding Engine
  = deterministic date arithmetic

Wren / DB
  = numerical truth

QueryContract / Evidence
  = proof

CompletionGate
  = completion truth
```

No model directly mints canonical truth, a `sem_*` handle, SQL, join authority, numeric
result, or completion verdict.

---

## 3. Regular semantic binding pipeline

Manager USER_SOURCE and AGENT_DERIVED regular semantics use:

```text
exact source span
   ↓
SemanticCandidateGenerator
   ↓
bounded cand_* cards
   ↓
[unique exact verified alias?]
   ├─ yes → no model call
   └─ no  → BoundedSemanticLinker → SELECT(cand_*) | ABSTAIN
                                      ↓
                              SemanticBindingGate
                                      ↓
                                  sem_*
```

### Candidate Generator

Deterministic, catalog-owned, non-authoritative.

It may enumerate only verified tenant/context concepts already present in the bounded
semantic context / verified company vocabulary.

It MUST NOT rank natural-language similarity using:
- regex parsing,
- fuzzy ratios,
- morphology/stemming,
- SequenceMatcher,
- case-derived phrase rules,
- language-specific score thresholds.

If the candidate set exceeds the bounded linker limit, current behavior is fail-closed:
`CANDIDATE_SET_TOO_BROAD`.

Future scale work may add semantic retrieval/indexing, but retrieval must remain candidate
discovery, not acceptance authority.

### Exact verified fast path

A single exact verified alias may bind without a model call.

Multiple exact verified candidates are a real ambiguity:
`AMBIGUOUS_EXACT` → no guess.

Sensitive entity values are exact-only; they are never exposed to probabilistic fallback
candidate discovery.

### Bounded Semantic Linker

The linker sees only:
- exact user surface,
- kind hint,
- opaque `cand_*`,
- human-safe candidate cards.

It may return:
- `SELECT(cand_*)`,
- `ABSTAIN`.

It may not:
- invent a candidate,
- emit canonical DB identifiers,
- emit/mint `sem_*`,
- write SQL,
- change capability/polarity,
- add obligations.

A candidate outside the exact supplied set is deterministically rejected.

### Semantic Binding Gate

The gate validates:
- candidate belongs to supplied set,
- tenant/context is current,
- target kind is valid,
- provenance is valid.

Only then may `SemanticHandleRegistry.mint_from_binding_gate()` create `sem_*`.

---

## 4. Temporal boundary

Manager temporal language no longer uses raw-language regex parsing as meaning authority.

```text
exact temporal surface
   ↓
TypedTemporalNormalizer
   ↓
closed TemporalIntent enum or ABSTAIN
   ↓
TemporalBindingEngine
   ↓
deterministic start/end arithmetic
   ↓
sem_period / sem_comparison
```

Model responsibilities:
- normalize language to a closed type only.

Deterministic responsibilities:
- choose/use governed time dimension,
- calculate concrete dates,
- construct `ResolvedPeriod` / `ResolvedComparison`,
- mint temporal authority.

Legacy `app/v2/temporal.py` remains for existing non-Manager V2 paths during migration.
It is not the target language-interpretation authority for the Day 6.5 Manager path.

---

## 5. Coverage boundary

Coverage is **veto-only cognition quality control**, not semantic or clarification truth.

It may detect:
- omitted business obligation,
- omitted/incorrect explicit exclusion,
- omitted supported research directive.

It may not:
- decide canonical semantics,
- decide whether an unresolved surface is “material”,
- require a semantic handle not required by capability algebra,
- mint obligations,
- mint handles,
- issue final user clarification authority.

Required semantic completeness is deterministic:
`CapabilityBindingValidator + material_grounding_gaps + IntentAcceptanceGate`.

User contradiction/semantic conflicts that deserve clarification are proven by deterministic
effect/binding gates, not by Coverage opinion.

---

## 6. open_questions

LLM `open_questions` is advisory metadata only.

It is not sufficient to produce user clarification.

A blocking clarification must be justified by deterministic reasons such as:
- required semantic binding missing,
- required operation parameter missing,
- conflicting deterministic effects,
- trusted previous authority missing,
- unsupported capability,
- bounded linker exact ambiguity / abstention on a required binding.

---

## 7. Semantic receipts

`SemanticResolutionReceipt` is retained for compatibility but semantically means:

> runtime anti-laundering proof that a specific current source span was bound to a specific
> approved semantic handle.

It is **not** an intent completeness oracle.

Receipt validation may prove:
- exact source/handle/kind edge existed,
- edge belongs to current message/context,
- declared binding graph did not omit or invent runtime-bound edges.

It may never infer:
- another user requirement was omitted,
- another semantic surface should have been proposed,
- a different capability should exist.

Rejected draft attempts reset their receipts.

---

## 8. Model roles

`SEMANTIC_LINKER` is a first-class model role.

Default configuration may fall back to `FAST_LANGUAGE`; model names never enter domain
logic.

`RESEARCH_MANAGER` remains the higher-level cognition/orchestration role.

A stronger Manager result must not be used as justification to give it semantic authority.
The same BindingGate invariants apply to every provider/model.

---

## 9. Failure semantics

Infrastructure/model transport failure is not a semantic verdict.

Pre-acceptance typed statuses distinguish:
- ACCEPTED,
- CLARIFICATION_REQUIRED,
- COGNITION_REJECTED,
- CONTRACT_REJECTED,
- MODEL_FAILURE,
- GROUNDING_FAILURE.

DEV evaluation must exclude MODEL_FAILURE/GROUNDING_FAILURE/HARNESS_FAILURE from semantic
success-rate denominators and mark the run `incomplete`.

Provider HTTP 402/timeout therefore cannot masquerade as NOT_ACCEPTED.

---

## 10. Verification

Provider-free cognition/authority boundary closure:

- run: `35660792599`
- tested code SHA: `e2b00eabff26c0e3ee93a7a2327b33f6615a048d`
- compile: PASS
- focused suite: **70 passed / 0 failed**
- includes real Wren trust-plane sentinel.

Protected invariants include:
- unique exact alias bypasses model,
- true exact ambiguity does not guess,
- linker cannot select outside bounded set,
- sensitive filter values remain exact-only,
- tenant/context crossing rejected,
- semantic linker production module contains no fuzzy/morphology/regex language matcher,
- typed temporal model does not calculate dates,
- temporal engine contains no language parser,
- Coverage has no semantic/clarification authority,
- model `open_questions` cannot force clarification,
- capability algebra / standard projection / evidence / adaptive branch regressions remain green.

---

## 11. Compatibility and rollback

This correction is intentionally local to Day 6.5 Manager semantics.

- Legacy `SemanticResolver` is preserved for existing non-Manager V2 paths.
- Legacy `temporal.py` is preserved for existing non-Manager V2 paths.
- Production hybrid `/ask-v2` route remains OFF until Day 6.5 certification gates close.
- The manual Manager Lab remains the integration surface.

Rollback can therefore disable/revert the Manager linker path without changing legacy
traffic.

---

## 12. Remaining Day 6.5 certification

Code correctness is not yet equivalent to architecture seal.

Next gates, without case-specific patching:

1. small bounded-linker live experiment / canary when provider capacity exists,
2. workers=1 stratified canary,
3. visible DEV80 recertification,
4. VALIDATION50,
5. external HIDDEN50 receipt,
6. only then architecture seal / production hybrid routing decision.

If a live corpus fails:
- first classify MODEL_COGNITION vs CONTRACT_UNDERCONSTRAINED vs BINDING/RESOLVER_TRUTH
  vs EVAL_ORACLE vs TRANSPORT/PROVIDER;
- do not change code until a repeated cross-case abstraction failure is demonstrated.

---

## 13. STOP-THE-LINE

The following are architecture regressions:

- adding a new language regex to make one semantic case pass,
- adding morphology/stemming/fuzzy thresholds as Manager semantic truth,
- adding case-derived examples/phrases to product prompts to pass a named eval case,
- letting Coverage choose canonical semantics or user clarification truth,
- letting model `open_questions` become automatic clarification,
- letting linker emit canonical identifiers or `sem_*`,
- accepting a candidate not supplied by the runtime candidate set,
- using receipts as a completeness parser,
- treating provider/model failure as semantic NOT_ACCEPTED,
- letting LLM perform temporal date arithmetic,
- modifying sealed roadmap/report to hide an implementation divergence.

