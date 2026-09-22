# DIMA FAST TRACK — DENETİM

Status: NORMATIVE AUDIT CHECKLIST

## A. Branch safety

- [x] Fast Track exact SHA'dan açıldı.
- [x] Dima+Metabase source branch read-only.
- [x] Ask-v2 source branch read-only.
- [x] merge/rebase/cherry-pick source sync forbidden.
- [x] source-lock exists.
- [x] F0 branch-isolation receipt sealed.

## B. Backend architecture

Required:
- Metabase = analytics substrate.
- Dima = orchestration/evidence/research/decision owner.
- DB/tool result = numeric truth.
- Wren hot path = 0.
- V2 semantic/manager hot path = 0.
- V3 semantic compiler hot path = 0.
- Fast-owned Gateway is the only Fast Metabase transport owner.

F0A:
- [x] exact pinned Metabase booted.
- [x] Agent API live.
- [x] search/read/construct/execute/query live.
- [x] pagination 200 + continuation verified.
- [x] raw SQL disabled.
- [x] restart proof.
- [x] app DB backup/restore proof.

FT-002B:
- [ ] provider-free Gateway gate.
- [ ] no V2/V3/Wren import guard.
- [ ] live Fast Gateway proof.
- [ ] Gateway receipt.

## C. UI/product architecture

Required:
- Metabase BI workspace owner.
- Dima intelligence owner.
- no Metabase frontend fork.
- no Metabase source patch.
- no raw DOM context scraping.
- no service/admin secret in browser.
- typed current-resource identity.
- Dima backend works without embed.
- Dima evidence/decision state is not Metabase-only.

FT-UI-001:
- [x] feasibility review completed.
- [x] old/new decisions reconciled.
- [x] Model A/B/C compared.
- [x] full-app classified as accelerator, not permanent architecture.
- [x] modular composition classified as strategic context target.

FT-UI-002:
- [ ] exact embedding-capable runtime pin.
- [ ] exact matching SDK pin.
- [ ] native Metabase UX baseline.
- [ ] Dima parent frame POC.
- [ ] Dima sidecar coexistence.
- [ ] typed context bridge.
- [ ] auth/permission proof.
- [ ] responsive proof.

## D. Stop-the-line

Stop development if any occurs:
- source branch write;
- cross-tenant leak;
- permission bypass;
- numeric claim outside tool result;
- invented resource ID;
- material ambiguity silent auto-pick;
- hidden native SQL fallback;
- unbounded agent loop;
- missing principal -> admin/service authority;
- browser service secret;
- iframe DOM scraping for analytics context;
- Metabase frontend source fork/patch;
- phrase-specific patch before root-cause receipt.

## E. Security gate

Internal alpha:
- isolated single-tenant/dev identity allowed.

External pilot requires:
- per-user/principal identity;
- tenant isolation;
- permission denial;
- revocation;
- evidence/history current-viewer auth;
- cache isolation;
- no browser service secret;
- embed/SDK identity mapped to the same intended principal class.

## F. Reliability families

Backend:
- Metabase unavailable;
- Agent API disabled;
- auth failed;
- permission denied;
- no/ambiguous resource;
- construct failed;
- execution timeout;
- pagination/truncation;
- stale resource;
- cancel race;
- duplicate delivery;
- backend restart;
- asset idempotency.

UI:
- embed unavailable;
- SSO failure;
- SDK/runtime mismatch;
- iframe cookie/SameSite failure;
- context desync;
- navigation desync;
- save/edit permission mismatch;
- responsive failure.

## G. Product correctness

Zero tolerance:
- silent numeric wrong;
- resource hallucination;
- finding without evidence;
- tenant leak;
- permission bypass;
- silent fallback;
- hidden identity/context guess.

## H. Root-cause integrity

Metric types:
- ADDITIVE
- SEMI_ADDITIVE
- RATIO
- DISTINCT_COUNT
- NON_ADDITIVE
- UNKNOWN

UNKNOWN / unsupported decomposition -> explicit limitation.

## I. Release progression

```text
F0       governance
F0A      pinned Metabase capability
FT-002B  Fast-owned Gateway
FT-UI-001 architecture reconciliation
FT-UI-002 workspace/context POC
F1       Ask vertical slice
F1A      temporal/resource safety
F2       conversation
F3       evidence
F4       analyst
F5       root cause
F6       Metabase-first assets/dashboard integration
F7       decision/report
F8       polish
F9       pilot security
F10      benchmark
F11      pilot readiness
F12      production candidate
```

## J. Audit seal

BRANCH_ISOLATION: GREEN
METABASE_SUBSTRATE_F0A: GREEN
FAST_GATEWAY: IN PROGRESS / NOT CERTIFIED
UI_ARCHITECTURE_RECONCILIATION: GREEN
UI_WORKSPACE_POC: NOT STARTED
FRONTEND_PRODUCT_IMPLEMENTATION: PAUSED
SECURITY_MODEL: GATED
PRODUCTION: NOT CERTIFIED
