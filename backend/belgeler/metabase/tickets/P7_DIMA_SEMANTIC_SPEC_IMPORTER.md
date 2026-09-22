# P7-001 — DimaSemanticSpec V1 structured Wren MDL importer

**Milestone:** P7  
**Review:** `backend/belgeler/metabase/predev/P7_PREDEVELOPMENT_REVIEW.md`  
**Status:** IMPLEMENTATION AUTHORIZED AFTER PREDEV SEAL

## Goal

Import the final composed Wren MDL JSON into the existing engine-independent `DimaSemanticSpec`
contract without creating a second semantic resolver or parsing semantic meaning from free text.

## Initial deliverable

```text
WrenSemanticSpecImporter.import_manifest(manifest, semantic_context_version)
  -> SemanticImportResult(
       source_fingerprint,
       spec,
       gaps,
     )
```

The importer is pure/provider-free and performs no external I/O.

## Key rules

- exact structured fields only;
- formulas preserved opaque;
- relationship condition text is not parsed;
- exact baseObject/model/view lookup only;
- exact column-name equality may establish column lineage;
- missing portable relationship join keys -> typed gap;
- unknown additivity token -> typed gap;
- no silent drop of material unsupported semantics;
- deterministic ids and SHA-256 compatibility hashes;
- final composed manifest already contains pack/customer override outcome.

## Representative proof

At minimum:
simple metric, computed metric, dimension, time dimension, relationship gap, additivity, distinct-count
opaque formula, ratio opaque formula, aliases, composed override, deterministic repeat import, invalid
duplicate/ambiguous source and real demo target import.

## Out of scope

Metabase resource provisioning, P8 equivalence matrix, P9 reconciliation, P10 security issuer, Wren
runtime bug fixes, absolute-period compatibility repair, broad live parity.
