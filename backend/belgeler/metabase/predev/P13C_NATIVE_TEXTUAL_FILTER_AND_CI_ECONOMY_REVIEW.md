# P13C — PRE-DEVELOPMENT REVIEW / NATIVE TEXTUAL EQUALITY FILTER + CI ECONOMY

**Date:** 2026-09-23  
**Milestone:** CI economy + P13C first same-table low-cardinality textual equality Standard vertical  
**Supervisor authorization:** DIMA — P13B CLOSURE, CI ACCELERATION VE P13C NATIVE FILTER INTEGRATION  
**Status:** **SEALED / ENGINE ATTESTATION EXTENSION REQUIRED / BOUNDED IMPLEMENTATION AUTHORIZED**

## 1. Starting state

```text
Platform branch = feat/dima-metabase-platform
Platform HEAD   = 243b14d0d2efc078bafcfd0b1daee8e8053ecf40

Engine main     = 10960f7c36bb84425b1794b557b78211c14d7f5f
Engine release  = 0.63.18-dima.3
Upstream base   = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
```

P13B-3 remains sealed GREEN. It is not reopened and no second P13B model canary is authorized.

## 2. Provider-free gap proof

Current dima.3 engine `src/metabase/dima/native_attestation.clj` already obtains native filter
clauses through Metabase Lib:

```text
lib/atomic-filters
→ lib/filter-parts
→ QP desugar observation view
```

For non-temporal filters the emitted manifest currently exposes only:

```text
non_temporal_filter_count
```

It does not expose the physical field id, equality operator, literal scalar value or field type.
Platform `NativeExecutionManifest` mirrors the same limitation and P13B trust deliberately blocks
every non-temporal filter.

Therefore Dima cannot bind one native textual equality predicate to one accepted
`ResolvedFilterRef` without parsing pMBQL itself.

Conclusion:

```text
ENGINE FILTER ATTESTATION EXTENSION REQUIRED = YES
Python MBQL parsing                           = FORBIDDEN
Metabot cognition change                     = NOT REQUIRED
```

## 3. Bounded engine extension

The next real engine revision is derived from the current release history as
`0.63.18-dima.4`.

The engine may expose exactly one typed observed predicate shape needed by the first vertical:

```text
stage_number
field_id
operator
literal_value
field_type
```

Certified predicate surface:

```text
one physical field
exact equality
one literal scalar string
```

Unsupported non-temporal shapes remain observable by count but do not become guessed typed
predicates. Platform must BLOCK when the material non-temporal filter count is not exactly covered
by the bounded typed predicate set.

No generic filter AST, SQL conversion, Dima semantic id, display-name matching or custom query parser
is authorized in the engine.

## 4. P13C semantic mapping

The first P13C vertical remains:

```text
1 metric
0 breakout dimensions
1 accepted textual filter
optional accepted period
0 relationships
0 comparison
0 ranking
1 material query
```

Physical filter identity is mapped only through:

```text
engine field_id
→ CurrentCatalogSnapshot.object_for_metabase_field
→ exact SourceLineage
→ Dima DimensionSpec
→ accepted ResolvedFilterRef
```

The observed literal must be type-strictly and value-strictly equal to the accepted filter value.

## 5. P11/P10 integration without a second access identity

P11 production evidence must be bound to the existing P5/P10
`ExecutionAccessSnapshot.execution_access_fingerprint`.

No `p13c_lens_hash`, email-derived lens id or second permanent fingerprint is authorized.

To break the existing artifact-order circularity without duplicating security truth, P10 may gain one
bounded issuance path that constructs the existing `ExecutionAccessSnapshot` directly from:

```text
current principal
+ accepted ResolvedAnalyticsIntent
+ Dima-authorized expected resource refs
+ VerifiedExecutionSecurityFacts
```

using the same validation and the same P5 snapshot type/fingerprint algorithm as the existing
artifact-backed issuer.

P13C order is then:

```text
accepted Dima resources
→ P10 ExecutionAccessSnapshot (single durable lens identity)
→ current-user field-value evidence tagged with that exact execution_access_fingerprint
→ EntityValueAdoptionGate exact BIND
→ engine-attested physical predicate mapped to the same Dima filter
→ NativeCandidateAuthorizationGate
→ exact same pMBQL execution
```

The P13A gate must still prove that the final authorized artifact has exactly the same resource set.
No second access snapshot system is introduced.

## 6. P13A bounded filter authority hardening

P13A may be extended from zero filters to at most one already-accepted filter only if the native
candidate carries an exact Dima-owned filter-scope fingerprint derived from
`ResolvedAnalyticsIntent.filters`.

P13B no-filter behavior remains the zero-filter case and must regress GREEN.

This is not analytical planning. It is an engine-independent authority equality check.

## 7. First fixture/case selection

The frozen Boyahane schema proves `satis_siparisleri.kanal` exists and is textual.

The actual frozen value is **not selected from memory**. A provider-free fixture probe must prove:
- low cardinality;
- exact values present in the frozen DuckDB;
- restricted-current-user Metabase field-value retrieval contains the selected value;
- independent oracle for the selected metric/filter/period.

Only after that probe may one case be frozen.

## 8. CI economy is part of this engine revision

The same dima.4 candidate must establish:

```text
focused + patch-surface
→ cached source build exactly once
→ smoke
→ publish ghcr.io/upcytech/dima-metabase-engine
→ resolve immutable registry digest
→ pull exact digest
→ /api/dima/engine/v1/identity equality
→ DIMA_ENGINE_CERTIFIED_IMAGE.json
```

Platform active integration workflows then consume only the immutable digest and fail closed on
pull/digest/gitlink/runtime identity mismatch. No silent source-build fallback.

## 9. Test/model budget

Until provider-free P13C gates are GREEN:

```text
Luna = 0
Sol  = 0
C1   = 0
```

After provider-free GREEN, exactly one Luna P13C canary may run. If that first bounded live vertical
is GREEN, stop for supervisor audit. P13D and Research remain unauthorized.

## 10. Forbidden

No regex/fuzzy/stemming/morphology/translation semantic authority, nearest-value substitution,
display/physical-name guessing, Python MBQL parsing/repair, raw SQL fallback, Agent API analytical
fallback, Wren fallback, admin fallback, prompt-to-pass patch or case-specific product branch.
