# DIMA FAST TRACK — DENETİM

Status: NORMATIVE AUDIT CHECKLIST

## A. Branch safety

- [x] Fast Track exact SHA'dan açıldı.
- [x] source branches read-only.
- [x] merge/rebase/cherry-pick source sync forbidden.
- [x] source-lock exists.
- [x] F0 branch-isolation receipt sealed.

## B. Backend foundation

- [x] F0A pinned Metabase OSS live.
- [x] Agent API search/read/construct/execute/query live.
- [x] pagination 200 + continuation.
- [x] raw SQL disabled.
- [x] backup/restore proof.
- [x] FT-002B Fast-owned Gateway.
- [x] provider-free Gateway: 21 passed.
- [x] static Fast boundary: 3 passed.
- [x] live Gateway: 1 passed.
- [x] no V2/V3/Wren runtime import.

## C. Product boundary

- [x] Dima owns complete user-facing product.
- [x] Metabase hidden analytics/query/optional-rendering substrate.
- [x] zero-license core invariant.
- [x] no generic Metabase workspace requirement.
- [x] no paid embedding requirement.
- [x] no Metabase frontend fork/source patch.
- [x] no browser service/admin secret.

## D. FT-UI-002 rendering gate

- [x] corrected predev.
- [x] isolated /fast-poc analyst shell.
- [x] real pinned-Metabase result fixture proof.
- [x] simple chart path.
- [x] simple table path.
- [x] safe table fallback.
- [x] guest visualization evaluated as optional.
- [x] no Collections UI dependency.
- [x] no Query Builder dependency.
- [x] no native Metabase Search dependency.
- [x] no paid Metabase feature dependency.
- [x] frontend production build.
- [x] protected-route browser proof.
- [x] 390px responsive proof.
- [x] selected rendering strategy: Option A.
- [x] receipt sealed.

## E. Stop-the-line

- source branch write;
- cross-tenant leak;
- permission bypass;
- numeric claim outside tool result;
- invented resource ID;
- material ambiguity silent auto-pick;
- hidden native SQL fallback;
- unbounded loop;
- missing principal -> admin/service authority;
- browser service secret;
- Metabase frontend fork/patch;
- paid capability enters core critical path.

## F. Release progression

```text
F0       governance                         GREEN
F0A      pinned Metabase OSS                GREEN
FT-002B  Fast-owned Gateway                 GREEN
FT-UI-002 Dima-native rendering             GREEN
FT-003    First Real Ask                     OPEN
F2        conversation
F3        evidence expansion
F4        analyst
F5        root cause
F6        optional assets
F7        decision/report
F8        polish
F9        pilot security
F10       benchmark
F11       pilot readiness
F12       production candidate
```

## G. Audit seal

BRANCH_ISOLATION: GREEN
METABASE_OSS_SUBSTRATE: GREEN
FAST_GATEWAY: GREEN
UI_RENDERING_POC: GREEN
SELECTED_RENDERING: OPTION_A
FT_003: OPEN
PRODUCTION: NOT CERTIFIED
