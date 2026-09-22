# DIMA FAST TRACK — DENETİM

Status: NORMATIVE AUDIT CHECKLIST

## A. Branch safety

- [x] Fast Track branch exact SHA'dan açıldı.
- [x] Dima+Metabase source branch read-only.
- [x] Ask-v2 source branch read-only.
- [x] merge/rebase/cherry-pick source sync yasak.
- [x] source-lock mevcut.
- [ ] CI forbidden-import guard implementation aşamasında eklenecek.
- [ ] Fast flag OFF legacy baseline proof F0 implementation sonunda kaydedilecek.

## B. Architecture

Required:
- Metabase = analytics substrate.
- Dima = product/orchestration/evidence/decision owner.
- DB/tool result = numeric truth.
- Wren hot path = 0.
- V2 semantic/manager hot path = 0.
- V3 semantic compiler hot path = 0.

## C. Stop-the-line

Aşağıdakiler görülürse geliştirme durur:
- source branch'e write
- cross-tenant leak
- permission bypass
- numeric claim tool result dışında
- invented resource ID
- material ambiguity silent auto-pick
- hidden native SQL fallback
- unbounded agent loop
- missing principal -> admin/service authority fallback
- phrase-specific patch before root-cause receipt

## D. Security gate

Internal alpha:
- single tenant + dev key izinli.

External pilot:
- F9 bitmeden YASAK.

Pilot zorunluları:
- per-user/principal identity
- tenant isolation
- permission denial
- revocation
- evidence/history current-viewer auth
- cache isolation
- no browser service secret

## E. Reliability

Zorunlu failure aileleri:
- Metabase unavailable
- Agent API disabled
- auth failed
- permission denied
- no resource / ambiguous resource
- construct failed
- execution timeout
- pagination/truncation
- stale resource
- cancel race
- duplicate delivery
- backend restart
- asset idempotency

## F. Product correctness

Hard blockers:
- silent numeric wrong = 0 tolerated
- resource hallucination = 0 tolerated
- finding without evidence = 0 tolerated
- tenant leak = 0 tolerated
- permission bypass = 0 tolerated

## G. Root cause integrity

Metric type sınıflandır:
- ADDITIVE
- SEMI_ADDITIVE
- RATIO
- DISTINCT_COUNT
- NON_ADDITIVE
- UNKNOWN

UNKNOWN / unsupported decomposition -> limitation, fake cause değil.

## H. Release progression

F0 governance
F0A Metabase capability
F1 real Ask
F1A temporal/resource safety
F2 conversation
F3 evidence
F4 analyst
F5 root cause
F6 dashboards/assets
F7 decision/report
F8 polish
F9 pilot security
F10 benchmark
F11 pilot readiness
F12 production candidate

## I. Audit seal

BRANCH_ISOLATION: READY
METABASE_SUBSTRATE: PINNED / needs branch-local F0A receipt
PRODUCT_ARCHITECTURE: READY
DEVELOPER_HANDOFF: READY
SECURITY_MODEL: GATED
PRODUCTION: NOT CERTIFIED
