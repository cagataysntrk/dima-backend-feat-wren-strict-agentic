# DIMA + METABASE — SOURCE LOCK

Status: SEALED FOR P0 BASELINE
Branch: `feat/dima-metabase-platform`
Created from immutable commit: `3774484167f1056d89da0e0609246fb4a05057ec`

## Immutable source identity

```text
DIMA_SOURCE_BRANCH              = feat/ask-v2-mvp            # READ-ONLY REFERENCE
DIMA_AUDIT_HEAD                 = 4ad8238c4fe8ada02a8a1a79e0682606a6fbfe1a
DIMA_BASE_CERTIFIED_SHA         = 3774484167f1056d89da0e0609246fb4a05057ec
WREN_REFERENCE_SHA              = 3774484167f1056d89da0e0609246fb4a05057ec
METABASE_SOURCE_AUDIT_SHA       = 74216b30981d8310c4cf724d63ca282e2e63529d
METABASE_UPSTREAM_OBSERVED_SHA  = fff70175e0b5f82dc0eb267593c717c4a6130206
METABASE_RUNTIME_VERSION        = v0.63.18
METABASE_RUNTIME_IMAGE_DIGEST   = sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
```

## Why this Dima base

Selected base `3774484167f1056d89da0e0609246fb4a05057ec` has explicit recorded real-Wren certification evidence:

- Actions run `35718883950`: **SUCCESS**
- pure Standard post-cognition Wren sentinel: PASS
- retained Research Wren sentinel: PASS
- total: **2/2 PASS**
- the focused/provider-free integration gate immediately preceding this checkpoint was recorded GREEN (`35718675540 = 25/25 PASS`, compile PASS).

The moving source branch HEAD observed during fork preparation was
`4ad8238c4fe8ada02a8a1a79e0682606a6fbfe1a`.
It was **not** selected as the certified base because Actions run `35724830736` failed the frozen full-live Standard composition:
`si-live-001 / metric_only_non_exact` returned `CLARIFICATION_REQUIRED` where `ACCEPTED` was expected.

This is deliberate isolation, not rollback of the source branch.

## Source branch isolation

`feat/ask-v2-mvp` is a read-only upstream/reference for this project.

Forbidden without a new explicit user instruction:
- commit, update_ref, force-push, merge, rebase or cherry-pick **into** `feat/ask-v2-mvp`;
- automatic sync/rebase/merge **from** moving `feat/ask-v2-mvp` into this branch;
- treating a later source HEAD as implicitly approved;
- copying a source-side patch without a Decision Receipt and focused proof on this branch.

Later source commits may be inspected. A useful source delta must be re-derived or deliberately ported on this branch and certified here.

## Known post-base source deltas — reference only, NOT inherited authority

At fork preparation time the source branch later contained, among others:
- `8f08af4...` partial semantic-surface fail-closed work,
- `5a0239d...` shared Standard/Research authority XOR work,
- `a36f1db...` distinct Research temporal-role wiring,
- `4a9a895...` / `4ad8238...` full-live Standard composition harness/run.

These are **not automatically part of the platform branch contract**. They may inform P1 work, but each must satisfy this branch's own roadmap and gates.

## Normative document source fingerprints

User-upload source SHA-256:
- roadmap source: `4c24bf485be5f5ec8a881d54810864f1358f994cd319646e66544af705077297`
- architecture report source: `8856eb8719e1facec03629606bac110b16e09d630af96b0ad622354586eb8763`

Repository sealed Git blobs:
- roadmap blob: `e74720455c44b92868d9ffd50b6c745f77405c55`
- architecture report blob: `0ccbfc502a812d098b2c758f41deaa4208d8b180`

The Git blob identities are the branch-local immutability check used by CI.


## M2 runtime artifact pins

```text
METABASE_RUNTIME_RELEASE_TAG    = v0.63.18
METABASE_RUNTIME_IMAGE_REF      = metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
METABASE_RUNTIME_AMD64_MANIFEST = sha256:3dd95de7e5dc6d62bfd8ac2c25245642861ab38b9c789b3eed3293f88cf163e9
METABASE_RUNTIME_ARM64_MANIFEST = sha256:2cb77c45b264380514fdd084decedb95787491548900dbfad9fc91f5cb300a9f

M2_POSTGRES_VERSION             = 17.11
M2_POSTGRES_IMAGE_REF           = postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675
```

Pin evidence observed 2026-09-22:
- official Metabase release: 63.18 / tag v0.63.18;
- official OSS Docker release line: v0.63.18.x;
- Docker Hub multi-platform index digest: sha256:1160...8a73;
- PostgreSQL supported 17 current minor: 17.11;
- Docker Official Image 17.11 index digest: sha256:67f417...5675.

Runtime pins are immutable artifact identities. They do not change `METABASE_SOURCE_AUDIT_SHA`.
