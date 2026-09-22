# P10B2-001 — Advanced security capability matrix

**Milestone:** P10B2  
**Status:** CLASSIFICATION COMPLETE / IMPLEMENTATION NOT AUTHORIZED

This ticket records which advanced security capabilities have a real owner/proof and which remain
profile-dependent gaps.

Key rule:
`NOT_CONFIGURED` is valid only for genuine configured absence. A profile requiring the capability
turns an unproven owner into `BLOCKING_FOR_PROFILE`.

No fake RLS/CLS versions, sandbox identity, impersonation role or database-route lens may be emitted
to close P10.
