# FT-UI-002 FAILURE RECEIPT — SETUP_NODE_PNPM_CACHE_ORDER

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

FAILURE_ID:
`FT_UI_002_SETUP_NODE_PNPM_CACHE_ORDER`

OBSERVED_SHA:
`1752706cf23893cd0817675617b1b5508591c130`

WORKFLOW_RUN:
`35767315055`

FAILED_STEP:
`Run actions/setup-node@v4`

FAILURE_CLASS:
`CI_RUNTIME_FAILURE`

## Observed failure

```text
Unable to locate executable file: pnpm.
```

## Root cause

`actions/setup-node@v4` was configured with:

```yaml
cache: pnpm
cache-dependency-path: dima-frontend-demo-master/pnpm-lock.yaml
```

before the later `corepack prepare pnpm@10.12.1 --activate` step.

The action attempted pnpm cache discovery before pnpm existed on PATH.

## Evidence already GREEN in the same run

Before this CI-ordering failure:
- pinned Metabase OSS boot = GREEN
- Fast Gateway real-result regeneration = GREEN
- committed fixture match = GREEN
- provenance artifact upload = GREEN

Therefore this is not:
- a product/rendering failure;
- a fixture failure;
- a Gateway failure;
- a Metabase failure.

## Single owner

`.github/workflows/dima-fast-ui-rendering-poc.yml`

## Allowed patch

Remove pnpm cache configuration from setup-node for this POC workflow.

Then:
1. setup Node 22;
2. enable Corepack;
3. activate pinned pnpm 10.12.1;
4. run frozen install.

Caching is not a correctness requirement for FT-UI-002.

## Forbidden patches

- product UI changes;
- package manager change;
- non-frozen install;
- Metabase/Gateway changes;
- source branch writes.

## Focused proof

Re-run same workflow.
Expected:
- setup-node GREEN;
- pinned pnpm activation GREEN;
- frozen install GREEN;
- build GREEN;
- browser proof executes.
