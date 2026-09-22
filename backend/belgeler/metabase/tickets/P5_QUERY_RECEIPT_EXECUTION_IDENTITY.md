# P5 — QUERY RECEIPT + EXECUTION IDENTITY

**Milestone:** P5  
**Owner:** Dima durable query/result/access identity  
**Branch:** `feat/dima-metabase-platform`  
**Status:** PREDEV SEALED / P5A CONTRACT IMPLEMENTATION PENDING GOVERNANCE

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

## P5B blocker

No official Metabase receipt may be certified until the real effective-access snapshot issuer is
proven. Current `intent.principal.fingerprint` and M1 legacy writer are insufficient.

## Stop conditions

- any attempt to derive missing policy/RLS/CLS/database security fields from guesses;
- any service/admin fallback on missing principal;
- any modification to P4 canonical identity to make P5 easier;
- any product routing change;
- any v2/source-branch write.

## Required closure evidence

See `predev/P5_PREDEVELOPMENT_REVIEW.md` §13.
