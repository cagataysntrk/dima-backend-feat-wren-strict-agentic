# P3A-001 — RESOLVED INTENT → METABASE BRIDGE PREFLIGHT

**Milestone:** P3A  
**Predevelopment review:** `backend/belgeler/metabase/predev/P3_P3A_PREDEVELOPMENT_REVIEW.md`  
**Owner:** semantic-duplication feasibility gate  
**Status:** BLOCKED UNTIL P3 GREEN

## Question

Can `ResolvedAnalyticsIntent` plus governed Dima-owned lineage/spec data become Metabase portable
structured queries without creating a second semantic owner?

## Candidate

Only candidate B is authorized for prototype:
```text
ResolvedAnalyticsIntent
+ immutable Dima-owned lineage/execution snapshot
→ deterministic portable query representation
```

No raw language, label guessing, semantic-handle resolution or Metabase-side business meaning.

## Eight families

metric; metric+dimension; metric+filter; metric+period; previous-period comparison;
ranking/limit; two compatible dimensions; filter+period+dimension.

## Stop-the-line

If any family requires:
- manual Metabase metric redefinition;
- manual relationship redefinition;
- display/canonical label guessing;
- unapproved implicit join;
- raw prompt reinterpretation;
- second semantic authority;

then structured-execution arm is REJECTED or the Dima-owned upstream contract must be corrected under
a new explicit receipt before retry.

## Exit

P3A result is one of:
`PASS_B_SEAM`, `BLOCKED_DIMA_CONTRACT_GAP`, or `REJECT_METABASE_STRUCTURED_EXECUTION`.

No P4 implementation before a recorded P3A result.
