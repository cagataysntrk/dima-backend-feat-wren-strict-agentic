# 07 — Competitive and Best-Practice Research

## 1. Research goal

The goal was not to copy a competitor page. The goal was to understand what the current AI analytics / conversational BI category has trained buyers to expect, then identify where Dima should conform and where it should diverge.

## 2. Category pattern: natural language is no longer enough

Across current category leaders, “ask a question in plain English” is table stakes. Stronger products increasingly emphasize:

- governed or trusted answers,
- a semantic/context layer,
- permissions,
- explainability,
- reusable workflows,
- integration with the existing data stack,
- visible product evidence.

Therefore, Dima's homepage should not lead with “AI can write SQL.” It should lead with the trust architecture around that SQL.

## 3. WrenAI pattern

WrenAI positions itself around an open context layer and governed BI for agents. Its strongest reusable lesson is:

- schema alone is not business meaning,
- approved definitions and relationships need a reviewable layer,
- agents need deterministic primitives, not only prompt instructions.

Dima should translate this into a customer-facing workflow rather than presenting itself as a developer engine:

> Dima understands the modeled business meaning, validates the query, and presents a traceable answer inside an end-user product.

Avoid reusing Wren's exact “Generate · Deploy · Know” framework or implying all Wren OSS capabilities are production-ready in Dima.

## 4. ThoughtSpot pattern

ThoughtSpot's current messaging uses AI analytics, natural-language exploration and trust/governance. The lesson is that enterprise buyers expect:

- permissions and governance,
- broad self-service,
- embedded/product workflows,
- security proof.

Dima should not try to out-broaden ThoughtSpot. It should be more concrete:
- Turkish-first,
- operational data,
- modeled SQL validation,
- textile/dyehouse proof,
- inspectable SQL and query lifecycle.

## 5. Hex pattern

Hex presents a collaborative workspace that combines analysis, notebooks, apps and AI. The lesson is product proof: the site shows the actual working surface and how different roles collaborate.

Dima should similarly show:
- real prompt,
- plan,
- validated query,
- report,
- follow-up,
rather than abstract AI gradients.

Dima should not imitate notebook positioning; its advantage is a simpler business-user workflow.

## 6. Omni pattern

Omni emphasizes a governed semantic model combined with flexible exploration and AI. The relevant lesson:

- semantic model should appear as a value enabler, not an implementation burden,
- governance and self-service can coexist.

Dima's copy should explain “modeled” in business language:
- metric definitions,
- joins,
- units,
- approved logic,
not only “MDL.”

## 7. Metabase pattern

Metabase historically wins on accessibility and fast self-service. Its AI messaging extends an already understandable BI product.

The lesson:
- do not let AI terminology obscure the basic job,
- show that users can get a table, chart or dashboard quickly,
- keep the interface approachable.

Dima should use its technical trust mechanism beneath a very simple top-level promise.

## 8. Seek AI pattern

Seek AI focuses on natural-language data access and data-team productivity. The lesson is to address both:
- business users want fast answers,
- data teams want control and reduced ad-hoc workload.

Dima's persona narrative should explicitly include IT/data owners, not only factory managers.

## 9. Recommended category conformity

Dima should include expected buyer information:

- Product
- How it works
- Solutions
- Security
- Integrations
- Contact/demo
- visible login
- real screenshots
- deployment/data source explanation
- FAQ
- legal pages

## 10. Recommended differentiation

Dima should own:

1. **Deterministic trust pipeline**
   `Question → modeled context → guarded SQL → dry-plan → result`

2. **Inspectable answer**
   SQL, trace, source and result are visible.

3. **Operational/industrial proof**
   OEE, fire, recipe, energy, deadline, shipment.

4. **Turkish-first product language**
   Not a translated generic US SaaS page.

5. **Reusable analytics**
   Verify, contract, schedule and notification with honest status labels.

## 11. Landing-page best practices derived from research

### Above the fold
- One category statement.
- One differentiator.
- One primary CTA.
- Immediate proof.
- No overloaded logo cloud.

### Product proof
- Use a realistic task.
- Show state transitions.
- Annotate the trust mechanism.
- Keep the visual legible on mobile.
- Avoid video-only explanation.

### Information scent
Navigation labels should be conventional. Clever labels reduce discoverability.

### Conversion
For an early B2B product:
- Primary: Demo request.
- Secondary: Login.
- Optional tertiary: See how it works.
Pricing should not be invented.

### Trust
Use mechanism proof before compliance badges:
- read-only query policy,
- modeled context,
- permission boundary,
- auditability,
- query visibility.

## 12. Next.js implementation best practices

Official App Router guidance supports:

- layouts/pages as Server Components by default,
- Client Components only for state, event handlers and browser APIs,
- route groups to organize layouts without changing URLs,
- route-level metadata and generated OG assets,
- `next/font` and `next/image`,
- production build and performance validation.

For Dima this means:
- marketing sections are server-rendered,
- product proof animation is a small client island,
- product providers stay outside marketing,
- route groups isolate scroll/runtime assumptions.

## 13. Web performance best practices

Core Web Vitals targets:
- LCP at or below 2.5 seconds,
- INP at or below 200 milliseconds,
- CLS at or below 0.1,
measured at the 75th percentile.

Dima-specific implications:
- no product chart bundle on homepage,
- no canvas particle field,
- reserve screenshot dimensions,
- keep hero image optimized,
- avoid client-rendering all marketing copy,
- keep sticky header from creating layout shifts.

## 14. WCAG 2.2 implications

WCAG 2.2 AA adds particular relevance for:
- focus not obscured,
- dragging alternatives,
- minimum target sizing,
- accessible authentication.

Implementation targets:
- 24×24px minimum pointer target or required spacing,
- 44×44px practical target for primary controls,
- visible focus, ideally a clear 2px perimeter,
- keyboard menu and accordion,
- no focus hidden by sticky header,
- no CAPTCHA/cognitive test without accessible alternative,
- reduced motion and predictable focus behavior.

## 15. Structured data

Use only structured data matching visible, factual content:
- Organization
- SoftwareApplication

Do not add:
- aggregateRating without real reviews,
- offers/pricing without actual public price,
- FAQ schema for hidden or mismatched content,
- fake award/certification fields.

## 16. Competitive anti-copy rule

Do not reproduce:
- competitor headlines,
- distinctive animations,
- illustrations,
- comparison tables,
- customer logos,
- screenshots,
- proprietary UI code.

Research informs strategy; Dima implementation must be original.
