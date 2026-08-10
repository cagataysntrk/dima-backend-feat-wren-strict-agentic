# Content and Claims Register

Marketing copy is a product surface. The agent must treat every statement as a typed claim, not as filler text.

## Capability status

Use one of these statuses in the content source:

| Status | Meaning | UI treatment |
|---|---|---|
| `available` | Verified in the current Dima product/repository and safe to describe as current. | Normal copy. |
| `pilot` | Exists for a controlled pilot or needs an explicit qualification. | “Pilot”, “for selected deployments”, or equivalent. |
| `planned` | Roadmap or architectural direction, not a current promise. | “Planned”, “coming later”, or omit from conversion copy. |

Unknown is not a status. If the agent cannot verify a claim, it must not publish it.

## Safe message territory

These themes are supported by the current product direction and may be expressed after wording review:

- Ask business questions in natural language.
- Use modeled business context rather than raw schema alone.
- Make SQL and validation steps visible.
- Restrict query intent with deterministic guards and dry-plan validation.
- Show results as tables, charts, KPIs, and reusable analytical outputs where the implementation supports them.
- Preserve tenant, permission, and session boundaries in the product experience.
- Build a Turkish-first experience for operational teams.
- Use textile/dyehouse scenarios as a focused, sanitized domain narrative.

## Claims requiring verification before publication

- Exact connector list or connector count.
- On-premise, thin-agent, private-cloud, or air-gapped deployment.
- Production availability of schedules, contracts, notifications, MCP, or embedded analytics.
- Pricing, free trials, self-serve signup, SLAs, uptime, latency, or performance numbers.
- Security certifications, legal compliance guarantees, or data residency.
- Customer logos, names, testimonials, case studies, and quantitative outcomes.
- Any statement about raw data leaving or never leaving a network.

## Forbidden default claims

Do not publish these without explicit legal/product approval and evidence:

- “100% accurate.”
- “Hallucination-free.”
- “Zero risk.”
- “Bank-grade” or “military-grade.”
- Fake customer counts, revenue, time saved, ROI, uptime, or benchmark results.
- Any certification badge that Dima does not actually hold.

## Copy rules

- Turkish is the primary editorial voice; English is a complete translation, not machine-shaped filler.
- Prefer concrete verbs: “sor”, “gör”, “doğrula”, “incele”, “tekrar kullan”.
- Explain feature → mechanism → user outcome.
- Keep one idea per section.
- Use one primary CTA per page and make its outcome explicit: “Demo talep et” or “İlk sorunu birlikte inceleyelim.”
- Do not use “Learn more”, “Submit”, or “Get started” when a more specific action is available.
- Never invent proof to make a section visually balanced. Omit the section or label it as planned.

## Required content source shape

Use a typed content source rather than scattered literals:

```ts
type CapabilityStatus = "available" | "pilot" | "planned";

type MarketingCapability = {
  slug: string;
  status: CapabilityStatus;
  title: string;
  shortDescription: string;
  proof?: string;
  sourceNote: string;
};
```

The exact file location must follow the existing repository conventions; a likely location is `apps/web/src/content/marketing/`. The agent must inspect the repo before creating it.

