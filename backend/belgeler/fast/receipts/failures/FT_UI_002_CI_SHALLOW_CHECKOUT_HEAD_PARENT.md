# FT-UI-002 FAILURE RECEIPT — CI_SHALLOW_CHECKOUT_HEAD_PARENT

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

FAILURE_ID:
`FT_UI_002_CI_SHALLOW_CHECKOUT_HEAD_PARENT`

OBSERVED_SHA:
`9217a99c1e09ebf422ece74cc78caca23bcb4eb9`

WORKFLOW_RUN:
`35767219787`

FAILED_STEP:
`Verify isolated Fast UI scope`

FAILURE_CLASS:
`CI_RUNTIME_FAILURE`

## Observed failure

```text
fatal: ambiguous argument 'HEAD^': unknown revision or path not in the working tree
```

## Root cause

`actions/checkout@v4` used the default shallow checkout.

The workflow then attempted:

```bash
git diff --name-only HEAD^ HEAD
```

but the parent commit was not present locally.

This is not:
- a product failure;
- a rendering failure;
- a Metabase failure;
- a Fast Gateway failure;
- a branch-scope violation.

## Single owner

`.github/workflows/dima-fast-ui-rendering-poc.yml`

## Allowed patch

Set checkout history sufficient for the parent diff:

```yaml
with:
  fetch-depth: 2
```

or equivalent deterministic parent availability.

No product code changes are authorized by this failure.

## Forbidden patches

- remove scope guard;
- widen product file allowlist;
- change Fast POC UI code;
- change Metabase lab;
- change Gateway;
- touch source branches.

## Focused proof

Re-run the same workflow.

Expected:
1. checkout succeeds;
2. HEAD^ resolves;
3. scope guard passes;
4. live Metabase fixture proof executes;
5. frontend build/browser proof executes.

## Family proof

The scope guard must remain fail-closed for unexpected paths after the checkout fix.
