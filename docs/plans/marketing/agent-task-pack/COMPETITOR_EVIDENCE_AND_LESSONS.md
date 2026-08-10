# Competitor Evidence and Lessons

This document turns the crawl into design decisions. It is not a request to imitate competitors. Use it to understand category expectations, then express the useful mechanisms in Dima's own visual and verbal system.

## Competitors reviewed

| Competitor | Official starting point | Dominant lesson |
|---|---|---|
| Wren AI | [getwren.ai](https://www.getwren.ai/) | Context layer, governed execution, and a product proof path from question to GenBI app. |
| Zenlytic | [zenlytic.com](https://zenlytic.com/) | Warm editorial positioning, self-onboarding, and “show your work” proof. |
| Upsolve AI | [upsolve.ai](https://upsolve.ai/) | Institutional context is a product surface: tables, SQL patterns, semantic models, and business rules. |
| Datost | [datost.com](https://datost.com/) | Positioning and public page inventory are sparse; clarity must come from the product mechanism. |
| Numbers Station | [docs.numbersstation.ai](https://docs.numbersstation.ai/) | Documentation is part of trust: explain deployment, setup, and operational detail. |
| Atlas | [useatlas.dev](https://www.useatlas.dev/) | Strong ask → semantic layer → validation → answer narrative with technical proof and pricing clarity. |
| Vanna AI | [vanna.ai](https://vanna.ai/) | Developer extensibility, deployment options, and approachable natural-language SQL framing. |
| Defog | [defog.ai](https://defog.ai/) | Minimal, direct trust language; connectors and SQL visibility support the promise. |
| Dot / GetDot | [getdot.ai](https://www.getdot.ai/) | Product-led interface framing and concrete paths for business and data teams. |
| Seek AI | [seek.ai](https://www.seek.ai/) | Embedded AI analyst is a distinct distribution/use-case story; live origin was blocked during crawl. |
| Datyo | [datyo.ai](https://datyo.ai/) | Agent-native analytics, scheduled monitoring, chat integrations, and a deep public docs graph. |
| Kaelio / ktx | [kaelio.com](https://www.kaelio.com/) | Context is treated as infrastructure with build, runtime, and review loops. |
| nao Labs | [getnao.io](https://getnao.io/) | “Context engineering” is made tangible through files, YAML, code, and deployment surfaces. |
| Motley / SLayer | [motley.ai](https://motley.ai/) | Operational analytics can be made legible through focused workflows instead of a generic AI hero. |
| Honeydew | [honeydew.ai](https://honeydew.ai/) | Data workspace and collaboration framing make analytics feel usable beyond the data team. |
| Timbr | [timbr.ai](https://timbr.ai/) | Semantic knowledge graph and enterprise data foundation are the mechanism, not an afterthought. |
| MINEO Manufacturing | [mineo.app/solutions/manufacturing](https://www.mineo.app/solutions/manufacturing/) | Manufacturing buyers need long-form domain proof, visual systems, and governance reassurance. |
| oee.ai | [oee.ai/en](https://www.oee.ai/en) | Industrial/OEE language works when the page leads with measurable operational questions. |
| Premisys | [premisys.ai](https://premisys.ai/) | Narrower industrial positioning can be more credible than a broad AI category claim. |
| Zentio | [zentio.ai](https://zentio.ai/) | Operations and decision-support stories should connect to concrete outcomes and users. |
| Loukamotive / IF | [loukamotive.com](https://loukamotive.com/) | Industrial workflow narrative and sector specificity create differentiation. |

## Repeated patterns worth adapting

### 1. Show the mechanism near the promise

The strongest pages do not leave “AI analytics” abstract. They show a visible chain:

`ask → context/semantic model → plan/guard → answer → reusable artifact`

Dima translation:

`soru → modellenmiş bağlam → SELECT-only guard → dry-plan → tablo/grafik → provenance`

The proof should appear above or immediately below the fold. A decorative illustration is not a substitute for this sequence.

### 2. Make trust observable

Competitors repeatedly surface SQL, semantic definitions, context files, query plans, permissions, deployment, or operational status. Dima should expose small, legible evidence labels such as:

- `MODELED CONTEXT`
- `SELECT ONLY`
- `DRY-PLAN VERIFIED`
- `TENANT SCOPED`
- `PROVENANCE AVAILABLE`

These labels are mechanisms. They must be tied to a visible UI state, not used as unsupported slogans.

### 3. Separate audiences without diluting the homepage

Common paths include business users, data teams, developers, embedded analytics buyers, and industry operators. Dima should use the homepage for the shared promise, then route visitors to:

- `/product` for capability understanding,
- `/how-it-works` for technical trust,
- `/solutions` for persona/use-case choice,
- `/solutions/textile-dyehouse` for industry language,
- `/security` and `/integrations` for buying friction.

### 4. Use long-form pages where the buying question is complex

Manufacturing, security, deployment, and semantic modeling need more than three cards. Use progressive evidence: a clear section claim, a product-derived visual, a short explanation, and a next action. Avoid wall-of-text pages and avoid hiding critical proof in carousels.

### 5. Treat docs and deployment as marketing evidence

Datyo, Wren, Numbers Station, Vanna, and Kaelio show that public documentation can increase trust. Dima should link to real docs only when they exist and are maintained. It should not create an empty `/docs` shell to imitate the category.

## Dima-specific design translation

| Category pattern | Dima expression |
|---|---|
| Semantic/context layer | “Modellenmiş bağlam” with a small data-map or context chip visual. |
| Governed SQL | SQL excerpt plus `SELECT ONLY` and `DRY-PLAN VERIFIED` status. |
| Product proof | Sanitized local choreography, not anonymous API calls. |
| Industrial specialization | Dyehouse terminology: batch, recipe, machine, OEE, waste, quality, water, energy, deadline. |
| Trust page | Explain boundaries: session, tenant, permissions, read-only guard, audit/provenance. |
| Editorial competitors | Warm off-white sections, strong display type, controlled rhythm, sparse accents. |
| Technical competitors | JetBrains Mono details, trace lines, labels, and process diagrams. |
| Conversion | One primary action per page; qualified demo language instead of fabricated instant self-serve claims. |

## Patterns to reject

- Copying a competitor's headline, section sequence, illustration, screenshot, or distinctive visual motif.
- “Trusted by” logo strips without written permission and real customers.
- Unsupported numbers such as “20+ connectors,” “100% accurate,” “7 days,” or “10× faster.”
- Generic purple-gradient AI landing pages with no Dima mechanism.
- Infinite marquees, noisy particle backgrounds, or motion that obscures the product proof.
- Fake dashboard values presented as measured Dima outcomes.
- A broad “for every industry” promise before the textile/dyehouse wedge is credible.

