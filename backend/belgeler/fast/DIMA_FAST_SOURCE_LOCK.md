# DIMA FAST TRACK — SOURCE LOCK

Status: IMMUTABLE INPUT LOCK
Created: 2026-09-22
UI reconciliation added: 2026-09-22

## Fast Track

FAST_BRANCH = feat/dima-metabase-product-fast-track
FAST_PARENT_SNAPSHOT_SHA = 352205f112fe735d8f80065c7d255d78905398b9
FAST_PARENT_BRANCH = feat/dima-metabase-platform

## Read-only references

DIMA_METABASE_REFERENCE_BRANCH = feat/dima-metabase-platform
DIMA_METABASE_REFERENCE_SHA = 352205f112fe735d8f80065c7d255d78905398b9

ASK_V2_REFERENCE_BRANCH = feat/ask-v2-mvp
ASK_V2_REFERENCE_SHA = 6d65600842731112f2362261a30660217cbde05d

These are READ-ONLY references.
They are not synchronization parents after branch creation.

## Metabase backend runtime pin

METABASE_RUNTIME_VERSION = v0.63.18
METABASE_RUNTIME_IMAGE_REF = metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
METABASE_SOURCE_AUDIT_SHA = 74216b30981d8310c4cf724d63ca282e2e63529d

This F0A pin remains authoritative for backend substrate certification.

Do NOT replace it merely to enable an embedding POC.

## Postgres lab pin

POSTGRES_VERSION = 17.11
POSTGRES_IMAGE_REF = postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675

## UI integration lock

METABASE_FRONTEND_FORK = FORBIDDEN
METABASE_FRONTEND_SOURCE_PATCH = FORBIDDEN
METABASE_INTERNAL_REACT_COPY = FORBIDDEN

The Fast Track UI may use only supported integration surfaces:
- native Metabase UI for baseline;
- supported full-app embedding;
- supported modular web components;
- supported React embedding SDK.

Authenticated full-app/modular POC is a capability-gated runtime.

Current F0A OSS runtime proves Agent API only.
It is NOT treated as proof that authenticated embedding is enabled.

Before FT-UI-002 implementation, create a POC lock recording:
- exact Metabase POC version;
- exact container image digest;
- exact embedding capability surface;
- exact SDK package version/resolution;
- Node/React compatibility;
- auth mode;
- origin/CORS/SameSite assumptions.

SDK rule:
Metabase major and SDK major must be compatible.
For pinned Metabase major 63, resolve the major-63 stable SDK line and then pin the exact package in the POC lock/lockfile.
Do not ship unpinned `latest`.

## Upgrade rule

No `latest`.

Backend runtime/source upgrade requires dedicated ticket:
1. exact tag;
2. exact digest;
3. release/source delta review;
4. backup;
5. app DB migration rehearsal;
6. Agent API probe;
7. permission negative suite;
8. pagination suite;
9. asset suite;
10. rollback restore rehearsal;
11. source-lock update.

Embedding POC runtime change is also isolated and separately pinned.

Product feature + substrate upgrade in the same commit is forbidden.

## Source branch safety

Forbidden:
- write;
- merge;
- rebase;
- cherry-pick;
- force push;
- moving-HEAD auto sync.

Allowed:
- read;
- diff;
- architecture study;
- explicit branch-local re-derivation;
- receipt-controlled port.
