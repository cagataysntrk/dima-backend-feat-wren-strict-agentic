# DIMA FAST TRACK — SOURCE LOCK

Status: IMMUTABLE INPUT LOCK
Created: 2026-09-22

## Fast Track

FAST_BRANCH = feat/dima-metabase-product-fast-track
FAST_PARENT_SNAPSHOT_SHA = 352205f112fe735d8f80065c7d255d78905398b9
FAST_PARENT_BRANCH = feat/dima-metabase-platform

## Read-only references

DIMA_METABASE_REFERENCE_BRANCH = feat/dima-metabase-platform
DIMA_METABASE_REFERENCE_SHA = 352205f112fe735d8f80065c7d255d78905398b9

ASK_V2_REFERENCE_BRANCH = feat/ask-v2-mvp
ASK_V2_REFERENCE_SHA = 6d65600842731112f2362261a30660217cbde05d

These are READ-ONLY references. They are not synchronization parents after branch creation.

## Metabase runtime pin

METABASE_RUNTIME_VERSION = v0.63.18
METABASE_RUNTIME_IMAGE_REF = metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73

METABASE_SOURCE_AUDIT_SHA = 74216b30981d8310c4cf724d63ca282e2e63529d

## Postgres lab pin

POSTGRES_VERSION = 17.11
POSTGRES_IMAGE_REF = postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675

## Upgrade rule

No `latest`.
Runtime/source upgrades require dedicated ticket:
1. exact tag
2. exact digest
3. release/source delta review
4. backup
5. app DB migration rehearsal
6. Agent API probe
7. permission negative suite
8. pagination suite
9. asset suite
10. rollback restore rehearsal
11. source-lock update

Product feature + substrate upgrade in the same commit is forbidden.

## Source branch safety

Forbidden:
- write
- merge
- rebase
- cherry-pick
- force push
- moving-HEAD auto sync

Allowed:
- read
- diff
- architecture study
- explicit branch-local re-derivation
- receipt-controlled port
