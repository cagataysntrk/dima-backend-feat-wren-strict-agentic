# FT-UI-002 FAILURE RECEIPT — E2E_AUTH_GUARD_REDIRECT

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

FAILURE_ID:
`FT_UI_002_E2E_AUTH_GUARD_REDIRECT`

OBSERVED_SHA:
`14f3749795c639dd448b6c2345463467776cefc1`

WORKFLOW_RUN:
`35767610177`

FAILED_STEP:
`Browser rendering + responsive proof`

FAILURE_CLASS:
`EVAL_ORACLE`

## Evidence already GREEN before the browser step

- isolated Fast UI scope = PASS
- pinned Metabase OSS bootstrap = PASS
- real Fast Gateway fixture regeneration = PASS
- committed fixture equality = PASS
- Node 22 = PASS
- pnpm 10.12.1 = PASS
- frozen install = PASS
- Next production build = PASS
- isolated Next server start = PASS

## Observed browser failure

```text
Error: timeout: POC heading
```

Next diagnostics simultaneously show the app attempted:

```text
/auth/refresh -> backend localhost:8000 -> ECONNREFUSED
```

## Root cause

The existing production `src/proxy.ts` guards every page except `/login`.

Without the normal `dima_refresh` cookie, the headless test browser is redirected from:

`/fast-poc`

to:

`/login?next=/fast-poc`

before it can observe the isolated POC heading.

This is expected production auth behavior and MUST NOT be weakened for the POC.

The page itself compiled successfully; this RED does not prove a rendering defect.

## Single owner

`dima-frontend-demo-master/e2e/fast-poc-e2e.mjs`

## Allowed patch

Make the browser oracle enter the already-protected route with a synthetic test-only page-session cookie:

1. launch browser at `about:blank`;
2. use CDP `Network.setCookie` for the existing session-cookie name on localhost;
3. navigate to `/fast-poc`;
4. keep production `proxy.ts` unchanged.

The cookie is only a route-guard fixture. It does NOT create backend/API authority.

API calls from global chrome may still fail closed because the backend is intentionally not running in this frontend-only browser proof.

## Forbidden patches

- change/bypass production `proxy.ts`;
- exempt `/fast-poc` in production route guard;
- start a fake auth backend;
- change POC rendering code before evidence;
- weaken auth;
- source branch write.

## Focused proof

Re-run:
- page remains on `/fast-poc`;
- POC heading visible;
- chart canvas visible;
- table toggle yields 12 rows;
- 390x844 has no horizontal overflow.
