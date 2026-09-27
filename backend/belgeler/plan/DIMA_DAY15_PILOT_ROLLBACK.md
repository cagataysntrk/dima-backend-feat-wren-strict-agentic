# DIMA DAY15 — PILOT FLAG / ROLLBACK CLOSURE

## Status

```text
branch                         feat/ask-v2-mvp
Day10 FINAL                    SEALED
pilot default                  OFF
pilot activation               DEFERRED
request-level legacy fallback  FORBIDDEN
Day15 focused                  36231784784 = GREEN
Day15                          CLOSED / PROVIDER-FREE GREEN
```

## Pilot contract

The master Ask-V2 switch and tenant pilot switch are separate. Comparison-seal
configuration is dark by default. Tenant pilot admission requires exact allowlist
membership.

```text
ask_v2_enabled        = false by default
ask_v2_pilot_enabled  = false by default
pipeline fallback     = none
```

## Rollback

Disabling Ask-V2 blocks new V2 work. It does not delete immutable contracts,
Evidence, reports or durable checkpoints. Rollback is non-destructive and does
not silently reroute a request into a different analytical authority.

## Machine-readable configuration receipt

`PilotConfigurationReceipt` records master/pilot enablement, exact tenant
allowlist, contract version and rollback behavior.

Final engineering identity is produced by the pre-comparison seal package after
all Day11–15 and rehearsal receipts are known.

## Receipt

```text
workflow  v2-day15-pilot
run       36231784784 = GREEN
later regression after Day14 wiring 36232080128 = GREEN
```
