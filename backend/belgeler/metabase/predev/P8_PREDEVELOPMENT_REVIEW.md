# P8 — PRE-DEVELOPMENT REVIEW

**Milestone:** P8 — Semantic equivalence matrix  
**Branch:** `feat/dima-metabase-platform`  
**P7 implementation:** `2e233ea6122c9cc0ccc18ebe2978e2e896ebb41c`  
**P7 workflow:** `35772646640 = SUCCESS`  
**Source branch observation:** `feat/ask-v2-mvp@5789e729115fe044b689739d5960021aba0aca32` — REFERENCE ONLY

Status: **SEALED / P8 EQUIVALENCE MATRIX IMPLEMENTATION AUTHORIZED**

## 1. Goal

For each material Wren semantic capability, record:

```text
Wren feature
→ DimaSemanticSpec representation state
→ Metabase representation strategy
→ typed classification
```

Allowed classifications:
```text
NATIVE_METABASE
DIMA_COMPILED
DIMA_RUNTIME
WREN_ONLY_GAP
UNSUPPORTED
```

P8 is classification/equivalence analysis. It does not patch Wren or expand product semantics merely
to improve a score.

## 2. Inputs

Provider-free:
- P7 `SemanticImportResult`;
- existing DimaSemanticSpec typed fields;
- P7 typed gap codes;
- certified P4 Metabase compiler capability boundary.

No raw prompt, Metabase discovery or live stack is required for the initial matrix.

## 3. Conservative rules

- Exact physical dimensions/time dimensions with structured lineage can be `NATIVE_METABASE`.
- A Dima metric is `NATIVE_METABASE` only when it has no arbitrary formula and carries an explicit
  P4-supported mechanical aggregation.
- Formula-backed Wren metrics imported only as opaque expression text are **not** declared native by
  inspecting/parsing the formula. Initial classification is `WREN_ONLY_GAP` until a structured
  formula/aggregation contract exists.
- Relationship conditions lacking structured join keys are `WREN_ONLY_GAP`.
- Calculated dimensions/model columns whose expression is opaque are `WREN_ONLY_GAP`.
- Security metadata explicitly deferred to P10 is `DIMA_RUNTIME`.
- Cube-level terminology/alias ownership that belongs to Dima cognition/runtime rather than Metabase
  query execution is `DIMA_RUNTIME`, but current missing canonical ownership remains visible in the
  reason code.
- View SQL without structured lineage is `WREN_ONLY_GAP` until P9/resource strategy proves an
  executable canonical representation.
- Unknown gap code or ambiguous feature mapping is RED, never defaulted.

## 4. Matrix row

```text
SemanticEquivalenceRow
  feature_ref
  feature_kind
  dima_state
  classification
  reason_code
  evidence_refs
```

`dima_state` is one of:
`REPRESENTED`, `TYPED_GAP`.

## 5. High-information tests

At minimum:
- exact physical dimension -> NATIVE_METABASE;
- exact time dimension -> NATIVE_METABASE;
- explicit mechanical metric fixture -> NATIVE_METABASE;
- opaque formula metric -> WREN_ONLY_GAP;
- relationship join-key gap -> WREN_ONLY_GAP;
- calculated dimension gap -> WREN_ONLY_GAP;
- cube semantic entity gap -> DIMA_RUNTIME;
- security-deferred gap -> DIMA_RUNTIME;
- view definition gap -> WREN_ONLY_GAP;
- unknown gap code -> hard RED;
- deterministic matrix ordering/fingerprint.

No broad live parity suite.

## 6. Forbidden

```text
formula regex parsing
SQL expression parser
relationship condition parser
fuzzy/similar-name mapping
case-specific product branches
automatic Wren patch
semantic_spec.py expansion without a separate proven P8 contract need
Metabase search/discovery
raw language
```

## 7. Authorized files

```text
backend/app/v3/semantic_equivalence.py
backend/tests/test_v3_p8_semantic_equivalence.py
.github/workflows/dima-metabase-p8.yml
backend/belgeler/metabase/predev/P8_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P8_SEMANTIC_EQUIVALENCE_MATRIX.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

Initial slice does not modify semantic_spec.py, Wren, P4 compiler, P5 receipt or routing.

## 8. Exit

P8 initial matrix is GREEN when:
- every representative imported feature/gap receives exactly one allowed classification;
- unknown material gap codes fail closed;
- matrix fingerprint is deterministic;
- current real P7 result can be classified without source-text parsing;
- no Wren/Metabase equivalence is claimed beyond the row classifications.
