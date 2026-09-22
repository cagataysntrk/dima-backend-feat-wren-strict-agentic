# P7 — PRE-DEVELOPMENT REVIEW

**Milestone:** P7 — DimaSemanticSpec V1 + Wren MDL importer  
**Branch:** `feat/dima-metabase-platform`  
**P6 closure candidate:** `03912a8702b27eca634e8411b151acdd56491d2c`  
**P6 workflow:** `35771661991 = SUCCESS`  
**P6 governance:** `35771661812 = SUCCESS`  
**Source branch observation:** `feat/ask-v2-mvp@5789e729115fe044b689739d5960021aba0aca32` — REFERENCE ONLY / READ ONLY

Status: **SEALED / P7 IMPORTER IMPLEMENTATION AUTHORIZED**

## 1. Normative objective

P7 migrates semantic ownership toward:

```text
final composed Wren MDL
        ↓
structured deterministic importer
        ↓
DimaSemanticSpec V1
```

`DimaSemanticSpec` is canonical business meaning. Wren remains a source substrate during migration,
not the long-term identity owner.

P7 is semantic migration, not Metabase provisioning and not P8 equivalence classification.

## 2. Input boundary

The first importer consumes the already-composed/pinned Wren MDL JSON object.

It does **not**:
- re-run pack composition;
- reimplement customer override precedence;
- parse raw user language;
- use Metabase discovery;
- mutate Wren source;
- infer missing meaning from display names.

Customer/pack overrides are observed through the final composed manifest. P7 does not create a second
composition owner.

## 3. Existing Dima contract owner

`backend/app/v3/semantic_spec.py` already owns:
- MetricSpec;
- DimensionSpec;
- RelationshipSpec;
- TimeSpec;
- BusinessRule;
- DisplaySpec;
- SecurityTag;
- ManagedResourcePolicy;
- SourceLineage;
- DimaSemanticSpec.

Initial P7 importer must use these existing types. Changing them requires a separately proven contract
gap; importer convenience is not sufficient reason.

## 4. Initial importer result

Authorized shape:

```text
SemanticImportResult
  source_fingerprint
  spec: DimaSemanticSpec
  gaps: tuple[SemanticImportGap, ...]

SemanticImportGap
  code
  source_ref
  detail
```

Unsupported Wren richness is explicit typed data, never silent loss.

## 5. Structured mappings

### Models / lineage

Exact `model.tableReference` fields may populate base SourceLineage.

A cube `baseObject` must resolve by exact key to a model or view. Missing/ambiguous base objects fail
closed or produce an exact typed import gap according to the feature owner.

For a dimension/time expression, column-level lineage may be attached only when the expression is
exactly equal to one structured base-model column name. No expression parsing is authorized.

### Measures

Preserve exact:
- measure name;
- explicit synonyms/aliases;
- expression as opaque `formula`;
- unit/format/grain when explicitly present;
- additivity when explicitly represented;
- display metadata.

Do not parse formula text to discover SUM/AVG/COUNT/DISTINCT/ratio semantics in P7. If no explicit
aggregation field exists, use a generic expression-owned aggregation classification rather than
guessing formula semantics. P8 owns equivalence/classification.

### Dimensions / time

Preserve exact name, aliases, type, display data and exact structured lineage when available.
Time dimensions become both a Dima dimension identity and TimeSpec reference.

### Relationships

Wren relationship metadata exposes name/models/joinType plus a textual condition in current manifests.
P7 must not regex/parse the condition to manufacture JoinKeySpec.

If exact structured join keys are not present, emit a typed `RELATIONSHIP_JOIN_KEY_GAP` and preserve
the relationship source reference for P8/P7 follow-up. Do not silently drop the feature and do not
invent keys from PK/FK similarity.

### Views / calculated columns

View statements and calculated expressions remain opaque source material. No SQL source-text parser is
authorized in the first importer. Missing portable physical lineage becomes a typed gap.

## 6. Deterministic identity

Imported Dima ids are deterministic and namespaced by semantic role/cube source. No random UUID.

`compatibility_hash` is SHA-256 over canonical structured semantic content.

Same composed MDL input must produce byte-equivalent normalized import output and the same source
fingerprint.

## 7. Additivity mapping

Only exact explicit tokens may map:

```text
additive/full/additive -> additive
semi                   -> semi_additive
non                    -> non_additive
absent                  -> unknown
unknown token           -> typed gap
```

No name/formula inference.

## 8. Required high-information fixtures

Provider-free initial gate covers at least:
- simple metric;
- computed metric;
- dimension;
- time dimension;
- relationship;
- explicit/absent additivity;
- distinct-count expression preserved opaque;
- ratio/derived expression preserved opaque;
- alias/synonym;
- final-composed customer override behavior;
- deterministic hashes/ids;
- unsupported feature -> typed gap.

No giant corpus.

## 9. Current real feature inventory

Observed in current repo:
- `bakim`: COUNT/SUM/AVG-style measures, explicit non-additivity, aliases, time dimension,
  relationship-derived dimension metadata;
- `oee`: multi-term ratio/derived measures, non-additivity, aliases, time dimension;
- `cari`: semi-additive balance;
- `karlilik`: ratio/derived metrics, semi-additive stock value, source-specific comparison caveat;
- relationship graph: MANY_TO_ONE / ONE_TO_ONE plus textual join conditions;
- final customer cube overrides exist under `demo/companies/**`.

These are evidence for fixture selection, not string-specific product branches.

## 10. Forbidden

```text
regex formula parsing
regex relationship-condition parsing
fuzzy/similar-name binding
stemming/morphology
SQL-text semantic parser
Metabase search
raw prompt
case-name product branches
silent unsupported-feature drop
custom Wren compiler
pack composition fork
ask-v2 merge/cherry-pick/rebase
backend/app/v3/substrate/wren.py modification
P4 compiler/canonical modification
P5 receipt modification
```

## 11. Authorized files

Initial implementation:
```text
backend/app/v3/semantic_import.py
backend/tests/test_v3_p7_semantic_import.py
.github/workflows/dima-metabase-p7.yml
backend/belgeler/metabase/predev/P7_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P7_DIMA_SEMANTIC_SPEC_IMPORTER.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

`semantic_spec.py` is not authorized for modification in the initial slice.

## 12. Gate

P7 first slice closes only when:
- focused representative import tests are GREEN;
- current composed demo MDL imports deterministically without crash;
- every unsupported material feature is surfaced as a typed gap;
- no regex/fuzzy/morphology/source-text semantic parser exists;
- duplicate ids fail closed through DimaSemanticSpec;
- P6/P5/P4 critical provider-free regressions remain GREEN;
- source branch remains read-only.

P7 does not claim Metabase equivalence. That is P8.
