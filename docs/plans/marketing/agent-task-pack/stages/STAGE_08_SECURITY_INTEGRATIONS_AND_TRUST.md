# Stage 08 — Security, Integrations, and Trust Pages

## Objective

Remove buying friction with accurate, inspectable explanations of security and integration boundaries.

## Security page

Cover only verified behavior:

- session/authentication boundary;
- permission-aware access;
- tenant isolation;
- read-only/select-only query guards;
- dry-plan and provenance visibility;
- auditability where available;
- deployment architecture and status;
- responsible disclosure/contact path.

Do not add SOC 2, ISO, GDPR/KVKK, “bank-grade”, “military-grade”, zero-risk, or data-residency claims without approved evidence.

## Integrations page

Organize by verified status:

- current Dima-supported connections;
- pilot/controlled support;
- engine or architecture capability that is not a Dima production guarantee;
- planned deployment/connectors.

A connector is not “available” because another competitor or underlying project advertises it.

## Tasks

1. Create a trust pipeline visual that remains legible as text.
2. Add evidence labels tied to actual product behavior.
3. Add FAQ handling the most common objections: permissions, schema changes, deployment, SQL visibility, and existing BI.
4. Use one primary CTA per page.
5. Add clear links to How It Works and Contact.
6. Keep external security/legal documents separate from marketing claims unless approved.

## Acceptance criteria

- No unsupported security badge or certification appears.
- Integration list has explicit status and source notes.
- Security language describes controls without promising outcomes the code cannot support.
- Page copy is useful to a technical buyer and a non-security buyer.
- All visuals have accessible equivalents.

## Verification

Run claim review, route metadata checks, keyboard/contrast tests, link checks, and auth/product smoke if shared layout code changed.

