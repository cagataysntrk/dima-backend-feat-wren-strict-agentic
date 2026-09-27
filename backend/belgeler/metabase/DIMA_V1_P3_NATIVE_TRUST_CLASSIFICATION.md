# DIMA V1 — P3 NATIVE TRUST CLASSIFICATION

Status: WAVE-A OWNER CLASSIFICATION  
Engine remains pinned: `cbe313af9ac2d5960f662068e433d328d896fb06`

Purpose: prevent `AnalyticalRequestContract` from becoming a second query planner while
preserving sealed trust/security/provenance authority.

## 1. KEEP — SECURITY / AUTHORITY / PROVENANCE

The following existing native trust responsibilities remain forward-critical:

- exact execution occurrence/artifact identity and fingerprint integrity;
- engine repository/SHA/upstream/runtime pin;
- authenticated native subject and current Dima principal/tenant binding;
- verified execution-security facts and access identity;
- semantic resource/catalog binding identity;
- exact receipt/result provenance and execution correlation;
- permission provenance and fail-closed native authorization;
- tenant/principal non-oracle behavior.

These facts answer **who/what exact execution is trusted**, not **how Metabase should
implement the analytical query**.

## 2. V1 REQUEST AUTHORITY — MATERIAL INVARIANTS ONLY

`app.v3.analytical_request_contract` owns only the accepted material request:

- metric;
- dimension;
- time scope;
- filters;
- comparison intent;
- ranking basis;
- grain;
- requested output surfaces;
- scope identity = lineage + scope version.

The module is structurally forbidden from importing SQL/SQLModel/SQLAlchemy,
native-query-plan or Metabase substrate evaluators.

## 3. HISTORICAL IMPLEMENTATION CERTIFICATION — NOT V1 REQUEST AUTHORITY

Existing P13D checks such as the following remain valid historical/certification proof,
but are not permitted to define V1 request correctness:

- exact `COUNT(*)` implementation shape;
- exact lower/upper temporal operator representation;
- exact breakout implementation;
- exact order-by implementation;
- one-stage/one-query implementation constraints when not security requirements;
- explicit/implicit join-shape quality rules;
- query implementation optimality.

Wave A does **not** delete these checks blindly. Their historical tests remain regression
evidence. Any future forward-path removal or demotion requires an owner-scoped change after
the material request-invariant seam has equivalent semantic observation support.

## 4. Forbidden interpretation

The following is permanently invalid:

```text
AnalyticalRequestContract
→ parse SQL/MBQL
→ judge joins
→ judge aggregation implementation
→ judge temporal operators
→ score query quality
```

That would recreate a Dima-side analytical planner.

Canonical boundary:

```text
accepted request invariants
→ Metabot/Metabase implementation
→ exact execution/security/provenance trust
→ semantic invariant observation/admission
→ Evidence
```

No engine selection or engine release is reopened by this classification.
