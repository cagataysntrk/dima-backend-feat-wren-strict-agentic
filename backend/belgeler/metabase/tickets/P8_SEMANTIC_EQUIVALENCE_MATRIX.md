# P8-001 — Semantic equivalence matrix

**Milestone:** P8  
**Review:** `backend/belgeler/metabase/predev/P8_PREDEVELOPMENT_REVIEW.md`  
**Status:** IMPLEMENTATION AUTHORIZED AFTER PREDEV SEAL

## Deliverable

Pure provider-free classifier:

```text
SemanticEquivalenceMatrix.build(import_result)
→ rows
→ deterministic fingerprint
```

Rows classify each represented semantic surface and each material typed import gap into exactly one:
`NATIVE_METABASE`, `DIMA_COMPILED`, `DIMA_RUNTIME`, `WREN_ONLY_GAP`, `UNSUPPORTED`.

No formula/join-condition parsing. Unknown gap code is a hard failure.

## First matrix purpose

Expose where Wren semantics can already map to the Metabase-era architecture and where Dima needs a
canonical/runtime/compiler capability before Wren can be retired. It is not a parity score.
