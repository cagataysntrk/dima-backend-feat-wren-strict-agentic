# DIMA METABASE PLATFORM — HANDOFF POINTER

> **CURRENT CANONICAL ONBOARDING**
>
> Read `DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md` first.
>
> This pointer intentionally contains only the current authority. Historical P12/P13B snapshots in
> older revisions are not current implementation instructions.

Current audited product checkpoint before the docs-only DMP-DEC-0044 authority update:

```text
Platform branch          = feat/dima-metabase-platform
Platform checkpoint      = 77000d07da0af4d43688bf963880ebc5120c8f1f
engine main              = cbe313af9ac2d5960f662068e433d328d896fb06
engine release           = 0.63.18-dima.6
engine certification     = 36042062775 SUCCESS
immutable engine digest  = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
```

Current authority:

```text
DMP-DEC-0044                     = BINDING
P13 STANDARD TRUST BASELINE      = SEALED
P13 OPERATOR GENERALIZATION      = STOPPED
P13D BREAKDOWN / RANKING         = LIVE GREEN
P13D COMPARISON                  = DEFERRED COMPATIBILITY GAP / NOT GREEN
P14 NATIVE RESEARCH              = AUTHORIZED NOW
```

Permanent architecture:

```text
METABASE + METABOT
= native analytical definitions / cognition / execution

DIMA
= business ontology + engine mapping
+ Research / Evidence / Hypothesis / Decision / Action / Memory
+ product-level identity/policy binding
```

Reuse order:

```text
USE_NATIVE → COMPOSE_NATIVE → WRAP_NATIVE → HOOK_NATIVE → DIMA_OWNS
```

Do not:
- reopen P13 operator-family certification;
- create P13E/P13F by default;
- cut dima.7 merely to make the old comparison test green;
- patch Metabot/QP/drivers/Lib;
- build Python MBQL/filter/ranking/temporal/query-repair substitutes;
- duplicate Metric/Model formula ownership;
- add Wren/raw-SQL/Agent-API/admin analytical fallback.

New developer starts directly with the P14 work order in the canonical onboarding file.
