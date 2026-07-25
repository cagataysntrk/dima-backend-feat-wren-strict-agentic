# AGENTS.md — working in dima-frontend

Guidance for AI agents (and humans) contributing to this repo. Read alongside
`CLAUDE.md` (rules) and `DESIGN.md` (the design system). Keep changes consistent with
both.

## What this is

`dima` is the end-user UI for a generative-BI "brain": users connect a database and
**chat with their data**; the backend returns insights, charts, and decision suggestions.
The UI never touches data directly — everything goes through `dima-backend` over HTTP.

## Stack

- Next.js 16 (App Router) · React 19 · TypeScript **strict** · Tailwind 4 (CSS-first, no
  `tailwind.config`) · shadcn/ui (new-york) · Recharts · Framer Motion (`motion`) ·
  next-themes · next-intl.
- Server state → **TanStack Query**; client state → **Zustand**; forms → React Hook Form +
  Zod (when added).

## Non-negotiable rules (saka-standards)

- **All HTTP goes through `src/lib/api-client.ts`.** No scattered `fetch`/`axios`.
- **`any` is forbidden.** Strict types. Backend types mirror `dima-backend`'s
  `app/schemas.py` in `src/lib/types.ts` — keep them in sync; narrow enums (source,
  view_hint) to unions.
- Import alias **`@/*`**. Compose classes with **`cn()`** (`src/lib/utils.ts`).
- Branch is **`master`**. **English, conventional commits. NO Claude footer / co-author
  line** in commit messages.
- **User-facing copy is Turkish; code, identifiers, comments are English.** Route UI
  strings through `useTranslations()` (next-intl); add keys to `messages/tr.json` **and**
  `messages/en.json`. **Data labels** (measures/dimensions) come from the cube catalog
  (`display` / `dimension_labels` / `measure_synonyms_display`), never raw snake_case.
- Security headers live in `next.config.ts › headers()`.

## Design-system conventions (see DESIGN.md)

- Use **tokens**, never raw colors: `bg-background`, `text-muted-foreground`,
  `border-border`, `bg-brand`. The amber is `--brand` (provenance/brand/focus), not
  shadcn `--accent`.
- Use **shadcn primitives** from `@/components/ui/*`. `Button variant="brand"` and
  `Badge variant="brand"|"brand-subtle"` are custom additions. Don't hand-fork ui files
  (they're vendored and lint-ignored) — restyle centrally via tokens.
- **Charts only via the `<Chart>` façade** (`src/components/chart/Chart.tsx`). Never import
  Recharts in a feature. Shape logic lives in `src/lib/chart.ts` (`analyze`, `buildSeries`);
  formatting in `src/lib/format.ts`. Heatmap/facet fall back to a table (visx reserved) —
  do not reintroduce ECharts.
- Fonts: `font-sans` (Jakarta — UI *ve* başlıklar; hiyerarşi ağırlıkla kurulur),
  `font-display` (Playfair — YALNIZ marketing sayfaları, uygulama içinde kullanma), `font-mono`
  (JetBrains, numbers/SQL/IDs).
- Everything must work in **light and dark** and be **responsive** (rails → Sheets on
  mobile; wide content scrolls in its own container).

## Auth, permissions, feature flags

- Auth is mandatory. Access token in **memory** (never localStorage); refresh in an
  HTTP-only cookie; a single-flight 401→refresh→retry interceptor lives in `api-client.ts`.
  Page protection is `src/proxy.ts` (session cookie).
- **Button visibility reads `/auth/me` `permissions`** (`vqr:write`, `schedule:create`,
  `contract:read`, …) via `src/lib/access.ts` (`usePermission`) — the role matrix stays in
  the backend and is **never copied to the UI**. Permissions default to allowed until
  loaded (no first-paint regression; the backend re-enforces).
- **Feature flags** (`useFeature`, ADR-0009) gate rollout/visibility only — `alpha`/`beta`
  should render **with a badge**; `flag ≠ permission`. First flags: `verify_button`,
  `scheduled_reports`.

## Layout / file map

- `src/app/layout.tsx` — fonts, `NextIntlClientProvider`, `Providers`.
- `src/lib/providers.tsx` — ThemeProvider › QueryClient › TooltipProvider (+ Toaster) ›
  AuthBootstrap (silent refresh on mount).
- `src/app/page.tsx` — shell host; wires conversations, `ask`/`cube` mutations, artifact state.
- `src/components/shell/*` — AppShell, AppSidebar, ArtifactPanel, Composer, ThemeToggle,
  LocaleSwitcher, NotificationsPopover.
- `src/components/{report,chart}/*` + `ChatPanel`, `ReportPanel`, `InterpretationBar`,
  `ResultView`, `ResultTable`, `SchemaPanel`, `Landing` — feature surfaces.
- `src/stores/conversations.ts` — named chat sessions (memory; persist-ready).
- `src/i18n/*` — next-intl request config, locale cookie action, `config.ts`.
- **`/style`** — living style guide (tokens, primitives, charts). Keep it current when you
  add primitives.

## Backend contract (surface a UI can use)

`POST /ask /cube /verify /query` · `GET /schema /features /auth/me` · `/schedules*`
`/notifications` `/contracts*`. Provenance `source`: `cube` | `cube+llm` | `llm:<provider>`
| `rule`. Trust surfaces worth building on: provenance badges, verify (VQR) loop, Query
Contract **replay** (same / data-changed / definition-changed), threshold notifications.

## Definition of done

`pnpm build` and `pnpm lint` pass (strict TS, no `any`, no stray `fetch`, no raw
`neutral-*`/hex). New UI renders in **both themes** and is **responsive**. New copy is in
both message catalogs. Verify end-to-end against a running `dima-backend` when possible.
