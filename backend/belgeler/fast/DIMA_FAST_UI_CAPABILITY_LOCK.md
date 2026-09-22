# DIMA FAST UI — CAPABILITY LOCK

Status: POC-A INPUT LOCK / PRE-IMPLEMENTATION
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Backend substrate — immutable

POC_METABASE_MAJOR=63
POC_METABASE_RUNTIME=v0.63.18
POC_METABASE_IMAGE_DIGEST=sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73

F0A_SUBSTRATE_MUTATION_FOR_UI=FORBIDDEN

## Modular SDK

POC_SDK_PACKAGE=@metabase/embedding-sdk-react
POC_SDK_DIST_TAG=@63-stable
POC_SDK_RESOLVED_VERSION=0.63.1
POC_SDK_PACKAGE_INTEGRITY=TO_BE_SEALED_FROM_COMMITTED_LOCKFILE

Rule:
- functional POC commit must pin exact 0.63.1;
- do not leave latest or 63-stable floating in package.json;
- commit package-manager lock;
- copy integrity/resolution evidence back into this capability lock when sealing POC.

## POC capability

POC_AUTH_MODE=LOCAL_EVALUATION_AUTH
POC_DATA_CLASS=synthetic_or_non_sensitive_dev
POC_ALLOWED_ORIGIN=localhost_only

ADMIN_OR_SERVICE_CREDENTIAL_IN_BROWSER=FORBIDDEN
REAL_CUSTOMER_DATA=FORBIDDEN
COMMITTED_API_KEY=FORBIDDEN
RAW_DOM_CONTEXT_SCRAPING=FORBIDDEN
GUESSED_RESOURCE_IDENTITY=FORBIDDEN

## Production capability

PRODUCTION_EMBED_RUNTIME=UNQUALIFIED
PRODUCTION_AUTH_MODE=UNQUALIFIED
PRODUCTION_JWT_SSO=UNQUALIFIED
PRODUCTION_PRINCIPAL_MAPPING=UNQUALIFIED
PRODUCTION_PERMISSION_MAPPING=UNQUALIFIED
PRODUCTION_ORIGIN_SESSION_MODEL=UNQUALIFIED

These are POC-B/F9 prerequisites, not POC-A blockers.

## Evaluation rule

POC-A first attempts Model C against the existing pinned major-63 substrate.

If the pinned OSS runtime does not expose the required modular SDK capability:
- record `EMBED_CAPABILITY_UNAVAILABLE`;
- do not mutate F0A;
- do not fake a GREEN;
- apply the architecture decision rule.

## Compatibility notes

Dima frontend baseline:
- Next.js 16.2.10;
- React 19.2.4;
- package manager: pnpm 10.12.1.

Metabase SDK documented prerequisites include React 18/19 and Node 20+.

SDK components are client-side; do not make SSR responsible for the embedded component runtime.
