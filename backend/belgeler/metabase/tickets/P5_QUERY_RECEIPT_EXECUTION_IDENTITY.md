# P5 — QUERY RECEIPT + EXECUTION IDENTITY

**Milestone:** P5  
**Owner:** Dima durable query/result/access identity  
**Branch:** `feat/dima-metabase-platform`  
**Status:** CLOSED GREEN — CONTRACT; PRODUCTION ISSUER PENDING P10

## Goal

Build one strict Dima receipt seal that binds:
```text
accepted authority
+ resolved intent
+ P4 canonical query identity
+ complete effective access snapshot
+ substrate runtime identity
+ result identity
```

without treating runtime-local or compatibility-only identifiers as durable proof.

## P5A deliverables

- complete `DimaQueryReceipt` R9 identity fields while preserving explicit M1 compatibility;
- `ExecutionAccessSnapshot` deterministic fingerprint contract;
- strict `DimaQueryReceiptSealer`;
- deterministic result fingerprint;
- authority/query/access/resource/runtime cardinality gates;
- focused provider-free tests;
- dedicated P5 workflow.

## Production issuer blocker

DMP-P5-BLOCK-001 is P10-owned. P5 may certify the contract/sealer using explicit complete attested
snapshots, but production official receipt issuance is forbidden until P10 proves the real issuer.
Current `intent.principal.fingerprint` and M1 legacy writer remain insufficient.

## Stop conditions

- any attempt to derive missing policy/RLS/CLS/database security fields from guesses;
- any service/admin fallback on missing principal;
- any modification to P4 canonical identity to make P5 easier;
- any product routing change;
- any v2/source-branch write.

## Required closure evidence

See `predev/P5_PREDEVELOPMENT_REVIEW.md` §13.


## Closure candidate proof

Implementation SHA `c8be6720f8f0f908b3cc6459fb817d760d417c8e`:
- P5 workflow `35759329146 = SUCCESS`;
- focused P5 = 34 PASS;
- provider-free P4 = 44 PASS;
- M1 critical = 15 PASS;
- full M1/Wren workflow `35759329091 = SUCCESS`;
- governance `35759329034 = SUCCESS`.

One closure-candidate live P3/P3A/P4 regression remains before P5 CONTRACT GREEN.


---

## Closure receipt

```text
implementation SHA              c8be6720f8f0f908b3cc6459fb817d760d417c8e
closure candidate SHA           94e9b3da892a80253495324b2a256f128b037d1b
P5 workflow                     35759691357 = SUCCESS
governance                      35759691408 = SUCCESS
focused P5                      35 passed
provider-free P4               44 passed
M1 critical                     15 passed
full M1/Wren                    35759329091 = SUCCESS
pinned-live P3/P3A/P4           3 passed
```

Exit gate: **P5 CONTRACT GREEN**.

DMP-P5-BLOCK-001 remains OPEN at P10. Production official receipt issuance is still prohibited until
the production effective-access issuer/mapping is certified.
