# UPSTREAM ENGINE HARVEST MAP

**Phase:** P12X source architecture review  
**Status:** SOURCE RESEARCH / NOT IMPLEMENTATION AUTHORIZATION  
**Pinned control:** Metabase `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`

Allowed dispositions:
`USE_NATIVE | HOOK_NATIVE | WRAP_NATIVE | DIMA_OWNS | IGNORE`.

| Capability | Initial disposition | Reason |
|---|---|---|
| native `run-agent-loop` | USE_NATIVE candidate | iterative Metabot cognition/runtime should not be reimplemented before seam measurement |
| Metabot profiles | USE_NATIVE candidate | profile prompt/model/tools/max-iterations are native engine behavior |
| skills catalog/loading | USE_NATIVE candidate | part of native orchestration capability |
| query/chart/tool turn state | USE_NATIVE candidate | engine-local state, distinct from durable Dima conversation |
| native tool registry | USE_NATIVE candidate | permission/scope-filtered engine tool surface |
| MBQL/query construction | USE_NATIVE candidate | Metabase-native analytical/query machinery |
| Metabase query processor | USE_NATIVE candidate | substrate execution engine |
| drivers/connectivity | USE_NATIVE | commodity native substrate capability |
| permission-aware query execution | WRAP_NATIVE / HOOK_NATIVE candidate | native enforcement must remain; Dima trust identity must bind around it |
| Metabot engine-local memory | USE_NATIVE candidate | turn/query/chart state stays engine-local |
| Dima durable conversation lineage | DIMA_OWNS | product/business context and cross-turn lineage |
| DimaSemanticSpec | DIMA_OWNS | canonical business semantic truth |
| approved relationships/grain/additivity | DIMA_OWNS | business truth, never inferred solely from physical FK/native labels |
| ExecutionAccessSnapshot | DIMA_OWNS | sole durable execution-access identity |
| QueryReceipt | DIMA_OWNS | durable Dima execution/provenance identity |
| Evidence truth/status | DIMA_OWNS | epistemic promotion is not native interestingness |
| durable research memory | DIMA_OWNS | product research/evidence lineage |
| decision records/skills/business policy | DIMA_OWNS | decision-intelligence layer |
| native interestingness | USE_NATIVE AS SIGNAL candidate | attention signal only; never truth/finding/cause |

Current upstream-master Explorations research is reference-only and not the P12X runtime baseline.
No native implementation is ported into Python during P12X.


---

## DMP-DEC-0031 authoritative initial direction

Allowed dispositions remain exactly `USE_NATIVE | WRAP_NATIVE | HOOK_NATIVE | DIMA_OWNS | IGNORE`.

```text
native run-agent-loop               = USE_NATIVE
profiles                            = USE_NATIVE
skills                              = USE_NATIVE
engine-local query/chart/tool state = USE_NATIVE
native tool registry                = USE_NATIVE
MBQL                                = USE_NATIVE
query construction / repair         = USE_NATIVE
Query Processor                     = USE_NATIVE
drivers                             = USE_NATIVE
native BI primitives                = USE_NATIVE
permission-aware execution          = WRAP_NATIVE / HOOK_NATIVE
Explorations mechanical variants    = USE_NATIVE candidate
StoredResult lifecycle              = USE_NATIVE / HOOK_NATIVE candidate
native interestingness              = USE_NATIVE AS SIGNAL / NEVER EVIDENCE TRUTH

DimaSemanticSpec                    = DIMA_OWNS
ExecutionAccessSnapshot             = DIMA_OWNS
QueryReceipt                        = DIMA_OWNS
Evidence lifecycle                  = DIMA_OWNS
durable conversation/research/
decision lineage                    = DIMA_OWNS
Decision Skills / Sector Packs      = DIMA_OWNS
```

Default decision order: `USE_NATIVE → WRAP_NATIVE → HOOK_NATIVE → DIMA_OWNS`. Burden of proof increases downward.

Upstream master `6ec07f75184dd7f06d84c551d57c58687cf4b859` is research-only. Initial engine base remains v0.63.18. Do not manually port newer Explorations algorithms into Dima Python.