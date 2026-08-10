# Stage 09 — About, Contact, Privacy, and Terms

## Objective

Complete the trust and conversion surfaces without introducing a fragile lead form or unapproved legal copy.

## About

Explain why Dima exists, its connection to operational data work, and the people/product perspective that is approved for publication. Keep the page customer-relevant and avoid invented team metrics or investor language.

## Contact

Use the existing contact form/component patterns where possible. The form must have:

- visible labels;
- semantic input types and autocomplete;
- server-side validation;
- honeypot/rate-limit or existing anti-abuse control;
- clear loading, success, and recoverable error states;
- keyboard and screen-reader feedback;
- privacy acknowledgement;
- no PII in analytics events or client logs.

If a production-safe destination/endpoint is not available, do not silently wire a fake success or a mailto-only flow. Document the dependency and use an honest unavailable/intent state approved by the product owner.

## Privacy and Terms

Use approved legal source text. If the current legal pages are placeholders, identify the exact missing approval instead of inventing a complete policy. Ensure:

- readable long-form measure;
- heading hierarchy;
- table of contents/back links where helpful;
- canonical metadata;
- correct noindex/index decision;
- no misleading “we comply” claims.

## Acceptance criteria

- Contact form has complete interaction and error recovery.
- Legal pages are accessible, linked, and clearly separated from promotional copy.
- About copy contains no unsupported company facts.
- No PII is emitted to analytics or console.
- All footer links are real and intentional.

## Verification

Test form keyboard flow, invalid/submission/error states, mobile behavior, legal deep links, metadata, and privacy-sensitive instrumentation.

