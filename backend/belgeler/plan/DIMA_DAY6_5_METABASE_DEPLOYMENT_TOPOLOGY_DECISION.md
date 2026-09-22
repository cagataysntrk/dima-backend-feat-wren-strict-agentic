# DIMA DAY 6.5 — METABASE DEPLOYMENT TOPOLOGY DECISION

**Date:** 2026-09-22  
**Status:** CONSULTATION REQUIRED / NO PRODUCT WIRING AUTHORIZED  
**Phase:** D65-M0 → X0 preparation  
**Canonical source:** `metabase/metabase`

## 1. Clarification: Agent API does not imply Metabase Cloud

Metabase Agent API is an HTTP API exposed by a Metabase runtime.

Two materially different deployments exist:

```text
A) Metabase Cloud / vendor-hosted
Dima → internet/vendor Metabase service

B) Self-hosted Metabase
Dima → private network → our Metabase container/JAR
```

D65-X0 does **not** require sending customer data to Metabase's hosted cloud.

The default Dima evaluation topology should be:

```text
Dima backend
   │
private service network
   ↓
self-hosted Metabase
   │
   ├─ Metabase application DB (PostgreSQL in production)
   └─ customer analytical DB / warehouse
```

No public internet hop is required between Dima and Metabase in this topology.

## 2. Deployment options

### Option A — Metabase Cloud

Advantages:
- lowest operational burden;
- upgrades/HA/monitoring handled by vendor.

Costs/risks:
- customer metadata/query/result traffic crosses into vendor-hosted infrastructure subject to
  the selected cloud architecture and contracts;
- external dependency/latency;
- lower infrastructure control;
- not appropriate as the default X0 assumption for Dima's trust-plane experiment.

Current status:
`NOT SELECTED / NOT X0 DEFAULT`.

### Option B — self-hosted Metabase as an internal service

Deployment forms:
- pinned Docker image;
- pinned JAR/service;
- Kubernetes/container service if the rest of Dima moves there.

Dima calls the Agent API over a private service address.

Advantages:
- analytical data path remains inside infrastructure we operate;
- official/supported Agent API boundary;
- source/runtime can be pinned independently;
- Metabase can be horizontally scaled behind a load balancer when required;
- cleaner upgrade/rollback boundary than a source fork.

Operational cost:
- JVM/Metabase process;
- dedicated production Metabase application database;
- health checks/monitoring;
- migrations/upgrades/backups;
- runtime memory/CPU;
- one more deployable service and network boundary.

This is the **default D65-X0 topology** unless user decides otherwise.

### Option C — package self-hosted Metabase inside the same product deployment

This is still Option B architecturally but packaged as one Dima stack:

```text
docker compose / deployment bundle
  dima-api
  metabase
  metabase-app-postgres
  chosen analytical DB connections
```

To the customer/operator it can look like one installation, while preserving process isolation.

Advantages:
- no vendor cloud;
- repeatable one-command deployment;
- pinned runtime/image digest;
- easier local/on-prem installation.

Tradeoff:
- still multiple processes/services; "one package" does not mean "one Python process".

This is likely the most practical production packaging **if Metabase wins the substrate decision**.

### Option D — run Metabase in-process / import it as a Python library

Not a realistic supported integration surface.

Reasons:
- Metabase backend is JVM/Clojure software, while Dima backend is Python;
- the supported headless integration boundary is Agent API, not an embeddable Python library;
- starting a JAR as a child process still creates a separate runtime/process and does not remove
  operations/upgrade concerns.

Status:
`REJECT AS DEFAULT ARCHITECTURE`.

### Option E — vendor/copy/port Metabase source into Dima

Technically possible only as a fork/port/rewrite, not as a simple import.

Costs:
- very high maintenance;
- upstream changes become manual merges;
- Clojure/JVM → Python transliteration would become our own analytics engine;
- difficult security/permission parity;
- test burden and upgrade drift;
- source-copy/port would violate the current Dima architecture protocol;
- Metabase OSS code is AGPL-licensed, so direct copying/modification/distribution/network use
  introduces copyleft obligations requiring explicit licensing/legal review.

Status:
`FORBIDDEN UNDER CURRENT D65-M0/X0 PROTOCOL`.

### Option F — reimplement selected *patterns* natively in Dima

This means learning from behavior/design, not copying source.

Examples:
- construct vs execute separation;
- opaque query handle identity;
- permission revalidation on replay;
- terminal tool semantics;
- search/read-resource → construct-query flow.

Advantages:
- one Dima runtime;
- no Metabase operational dependency;
- full control.

Costs:
- we own every bug/edge case;
- risk of re-inventing a mature BI substrate;
- may duplicate exactly what X0 is meant to compare.

Status:
`ALLOWED AS PATTERN ADOPTION AFTER SOURCE AUDIT; NOT SOURCE PORTING`.

## 3. Scalability / operations decision criteria

X0 must score deployment burden in addition to query correctness.

Required operational metrics/observations:

```text
cold start
steady memory
CPU under representative query load
Metabase app-DB requirement
connection pool behavior
startup/migration behavior
health endpoint
upgrade/rollback procedure
horizontal scaling feasibility
load balancer readiness
session/auth propagation
tenant isolation implications
observability/logging
backup requirement
failure blast radius
network latency Dima↔Metabase
per-tenant vs shared Metabase topology
```

Production Metabase should use a dedicated relational application DB, preferably PostgreSQL,
not the embedded H2 demo database.

If scale is required, multiple Metabase app instances may share the application DB behind a
load balancer. Dima must still keep one governed execution authority and explicit principal
mapping.

## 4. Multi-tenant topology questions

Before any production selection:

```text
shared Metabase instance across tenants?
or
per-enterprise deployment?
or
per-environment shared runtime with permission-scoped identities?
```

Dima must prove:
- tenant A cannot discover/query tenant B resources;
- API-key/service identity does not accidentally collapse per-user permission semantics;
- query/replay permission is revalidated for current principal;
- Dima QueryContract can bind Metabase query identity/provenance;
- a Metabase outage has a typed failure boundary, not silent fallback.

No answer is assumed before X0.

## 5. Licensing boundary

Current external verification:
- Metabase Open Source Edition is AGPL.
- Self-hosting is supported.
- Metabase Cloud and commercial/Enterprise licensing are separate options.

Architecture separation does not by itself settle every licensing obligation.

Rules:
- no source copy/vendor/port in D65-X0;
- use official artifacts/API for feasibility;
- if production would ship or modify Metabase OSS with Dima, perform explicit license/legal review;
- if commercial embedding/features are required, evaluate Metabase commercial terms separately.

This document is an engineering risk record, not legal advice.

## 6. X0 default deployment recommendation

For a fair engineering experiment:

```text
self-hosted pinned Metabase container
+ private network
+ ephemeral/test application DB for X0 only
+ same representative analytical DB
+ explicit test users/principals
+ Agent API
```

For a production candidate, if Metabase wins:

```text
pinned self-hosted image/JAR
+ dedicated PostgreSQL application DB
+ private service networking
+ health/readiness monitoring
+ explicit upgrade/rollback policy
+ image digest/version receipt
+ scalable to N app instances if needed
```

Do not use Metabase Cloud for X0 unless the user explicitly chooses vendor-hosted evaluation.

## 7. Current decision gate

No production deployment topology is selected yet.

Required user decision after reviewing J1 and this topology:

1. Approve narrow D65-J1B experiment?
2. Keep X0 default as self-hosted internal Metabase service?
3. Keep source-copy/port/vendor forbidden?
4. If X0 shows Metabase wins materially, prefer:
   - bundled internal service,
   - managed cloud,
   - or reject operational dependency and adopt only patterns?

Until consultation:
```text
J1B = CLOSED
D65-SI = WAITING
X0 execution = CLOSED
product Metabase dependency = 0
```
