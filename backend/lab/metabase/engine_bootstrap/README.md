# Dima Metabase Engine bootstrap kit

This directory is a **Platform-side bootstrap kit** for the authorized thin-engine sequence in
`DMP-DEC-0031`.

It is not product runtime code and is not imported by `backend/app/**`.

Target:
```text
repository      = UpcyTech/dima-metabase-engine
upstream        = metabase/metabase
base tag        = v0.63.18
base SHA        = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
engine version  = 0.63.18-dima.0
```

Order:
1. `bootstrap_fork.sh` — create/verify a **real GitHub fork**, preserve upstream ancestry, and create
   immutable `upstream/base-v0.63.18` plus Dima integration branch `main` at the exact base.
2. Copy only the files under `engine-overlay/` into the fork as **new files**.
3. Run C0 build workflow from fork source.
4. Generate `DIMA_PATCH_SURFACE`; C0 requires zero modified/deleted pre-existing upstream files.
5. After C0 build GREEN, run stock-vs-fork native parity.
6. Upstream releases enter only through the candidate-only sync workflow; never auto-promote.

The bootstrap script requires authenticated `gh` + `git` on a machine with permission to create
repositories/forks in `UpcyTech`.

Blank-repository source copying is forbidden. The script uses GitHub's fork endpoint and then verifies
`fork=true` and `parent.full_name=metabase/metabase`.
