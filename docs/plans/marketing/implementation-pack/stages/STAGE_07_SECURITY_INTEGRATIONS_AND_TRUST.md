# STAGE 07 — Security, Integrations and Trust

## Objective

Build `/security` and `/integrations` with precise, non-inflated technical communication.

## `/security`

Recommended sections:
1. Security philosophy
2. Read-only query controls
3. Session security
4. Tenant and permission boundary
5. Auditability
6. Data flow
7. Deployment status/options
8. Responsible security contact
9. FAQ/CTA

## Security claim review

Before publishing each claim, find exact code/doc evidence.

Do not publish:
- SOC 2/ISO badges,
- “fully KVKK/GDPR compliant,”
- “military-grade,”
- “zero trust” unless architecture formally supports it,
- “data never leaves premises” before thin-agent deployment is ready.

Use language like:
- “designed to”
- “the current architecture”
- “available in the current deployment”
- “planned”
where appropriate.

## `/integrations`

Distinguish:
1. Current tested Dima connectors.
2. Engine-level capabilities.
3. Planned/partner integrations.
4. Generic onboarding process.

Show:
- source connection,
- schema discovery,
- semantic modeling,
- validation,
- tenant scoping.

Do not display vendor logos without right/need. Plain text list is acceptable.

## Architecture visual

Create an accessible data-flow diagram:
User → Dima UI → Dima API → semantic model/Wren → guarded query → customer DB.

If showing cloud/on-prem modes, status-label each.

## Contact CTA

Security/integration inquiry route to `/contact` with safe query parameter only if form supports it.

## Validation

```bash
pnpm lint
pnpm build
```

Plus:
- security copy technical review,
- no secret/internal hostname,
- no admin link,
- no customer credentials,
- external links safe,
- diagram alt.

## Acceptance criteria

- Technical reader can understand trust boundaries.
- No absolute or unverified security claim.
- Connector support accurately segmented.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.
