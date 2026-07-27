# dima — Design System

Premium, editorial, eye-comfortable in **both** light and dark. The bar is Attio /
Linear / Vercel / x.com surface quality, with a chat-first UX like Claude & ChatGPT.
The name is the thesis: **D**eterministic · **I**ntelligent · **M**odeled · **A**gentic.

> This is the product's design contract. New UI uses these tokens and primitives —
> never raw colors, never a second charting engine, never ad-hoc inputs.

## Principles

1. **Editorial, not generic SaaS.** Monochrome-forward (ink primary), one restrained
   brand accent (indigo-violet), generous type, hairline borders, tight radii. No
   stock-blue-primary template look.
2. **Comfortable in both modes.** Backgrounds are a soft off-white / warm editorial
   near-black — never pure `#fff` / `#000` (which fatigue the eye and halate on OLED).
3. **Trust is visible.** Provenance (`◆ CUBE` / `▚ LLM` / `⚙ KURAL`), the verify loop,
   query-contract evidence, and scheduled-report alerts are first-class, not hidden.
4. **Chat-first.** Left nav · center conversation (charts inline) · right artifact panel
   for reports/dashboards/schema. Collapsible rails; Sheets on mobile.
5. **Respect the engine.** LLM proposes, the engine validates. The UI never fakes
   confidence — badges reflect the real `source`.

## Tokens (`src/app/globals.css`)

Authored in **oklch** for perceptual light/dark parity, via Tailwind 4 `@theme inline`.
Dark mode is class-driven (`.dark`, toggled by next-themes), overriding OS.

| Token | Role | Light | Dark |
|---|---|---|---|
| `--background` | app surface (off-white / editorial black) | `oklch(0.985 0.003 95)` | `oklch(0.17 0.004 65)` |
| `--foreground` | primary text | `oklch(0.22 0.006 65)` | `oklch(0.925 0.004 90)` |
| `--card` / `--popover` | elevated surfaces | near-white | `oklch(0.205 …)` |
| `--primary` | **ink** — solid buttons, emphasis | near-black | near-white (inverted) |
| `--secondary` | subtle surface / chat bubbles | `oklch(0.955 …)` | `oklch(0.25 …)` |
| `--muted` / `--muted-foreground` | muted surface / mid-gray text | — | — |
| `--accent` | subtle hover/selected surface (shadcn) | neutral | neutral |
| `--brand` / `--brand-foreground` | **dima violet** — provenance, focus, chart-1 | `oklch(0.551 0.26 292)` `#7e38f8` | `oklch(0.615 0.231 293)` `#8f5bff` |
| `--destructive` | errors / alerts | red | red |
| `--border` / `--input` / `--ring` | hairline / field / focus ring (=brand) | — | — |
| `--chart-1..5` | categorical, **validator-passed**: violet · aqua · orange · blue · magenta. Slot order IS the CVD-safety mechanism — do not reorder. Dark has its own steps, not a flip. | `#7e38f8 #1baf7a #eb6834 #2a78d6 #e87ba4` | `#8f5bff #199e70 #d95926 #3987e5 #d55181` |
| `--sidebar-*` | left-nav surface set | — | — |
| `--radius` | `0.625rem` (editorial, tight) | — | — |
| `--shadow-*` | subtle neutral elevation (overlays only; surfaces stay flat + hairline) | — | stronger |

**Rules:** use semantic utilities (`bg-background`, `text-muted-foreground`,
`border-border`, `bg-brand`) — never raw `neutral-*` or hex. The violet is `--brand`
(reserved for provenance/brand/focus), *not* shadcn `--accent`.

## Type

- **Playfair Display** (`font-display`) — **marketing sayfaları için ayrılmıştır.**
  Uygulama içinde (paneller, başlıklar, kartlar) KULLANILMAZ; oradaki hiyerarşi
  Jakarta ağırlıklarıyla (`font-medium` / `font-semibold`) kurulur.
- **Plus Jakarta Sans** (`font-sans`) — the interface voice: body, labels, buttons.
- **JetBrains Mono** (`font-mono`) — SQL, numbers (`tabular-nums`), provenance, IDs, metadata.

All loaded via `next/font` with `latin-ext` for Turkish glyphs (ş/ğ/ı/İ/ç/ö/ü).

## Motion

Framer Motion (`motion`), Emil Kowalski philosophy: purposeful, fast, spring-based,
subtle. Respect `prefers-reduced-motion`. Examples in the codebase: theme-toggle icon
cross-fade, brand mark draw-in. Don't animate for decoration; animate to explain change.

## Components

Built on **shadcn/ui** (new-york) in `src/components/ui/` — do not hand-fork; restyle
centrally via tokens. Compose class names with `cn()` (`src/lib/utils.ts`).

- **Custom variants added:** `Button variant="brand"`, `Badge variant="brand" | "brand-subtle"`.
- **Shell** (`src/components/shell/`): `AppShell` (SidebarProvider + center + ArtifactPanel),
  `AppSidebar`, `ArtifactPanel` (desktop panel / mobile Sheet), `Composer` (auto-grow
  chat input), `ThemeToggle`, `LocaleSwitcher`, `NotificationsPopover`.
- **Report** (`src/components/report/`): `SourceBadge` (provenance). Report surfaces:
  `ReportPanel`, `InterpretationBar` (CubeQuery chips → shadcn DropdownMenu), `ResultView`, `ResultTable`.
- **AI chat** (`src/components/ai/chat.tsx`): `MessageScroller` (stick-to-bottom + jump),
  `Message`, `Bubble`, `Attachment` — local primitives modeled on the shadcn AI set
  (the core shadcn registry doesn't ship them; swap for an upstream registry if adopted).
  `ChatPanel` is built on these.
- **Schema** (`src/components/schema/ErdView.tsx`): React Flow (`@xyflow/react`) ERD —
  tables as nodes, relationships as edges, `colorMode` from the theme. Used by `SchemaPanel`'s
  *Diyagram* tab (which also has *Tablolar* / *İlişkiler*).

## Charts

**One engine: Recharts** (via shadcn's chart kit), painted by our `--chart-*` tokens —
dark-correct for free. Tremor's tile pattern is implemented natively on shadcn to stay
Tailwind-v4-clean.

- Always go through the **`<Chart>` façade** (`src/components/chart/Chart.tsx`) — never
  import Recharts directly in a feature. The façade dispatches by `kind`.
- Shape analysis lives in `src/lib/chart.ts` (`analyze()` → default kind, `buildSeries()`
  → engine-neutral data). Unit-aware formatting via `src/lib/format.ts` (₺, kg, %, kWh…).
- **Supported now:** bar (single + grouped), line, pie, KPI tiles (`chart/kpi.tsx`).
  **Table fallback:** heatmap & faceted small-multiples (reserved for a future **visx/D3**
  renderer behind the same façade — do not reach for ECharts).
- A chart-type dropdown reshapes the **same dataset** (`ResultView`).
- Which chart: 1 row → KPI · time axis → line · 1 dim → bar · 2 dims → grouped bar ·
  ≤12 slices of a share → pie. Categorical colors must stay distinct (no two greens).

## Layout & responsive

Two-rail shell: left nav and right artifact both collapse; on mobile (`use-mobile`) they
become Sheets and the center chat goes full-width. Wide content (tables, charts) scrolls
inside its own `overflow-x-auto`; the page body never scrolls horizontally.

## Marketing kart ölçeği

Marketing yüzeyinde (`src/app/(marketing)`, `src/components/marketing`) kartlar
**içeriğe göre** boyutlanır. Sabit satır yüksekliği, `min-h` tabanı veya sihirli
`mt-N` boşluğu ile hizalama yapılmaz.

- **Kart padding — yalnız üç değer:** `p-4` (görsel içi yoğun tile) · `p-5`
  (varsayılan kart) · `p-6` (öne çıkan kart / bağımsız yüzey). `p-8` sadece
  container-kapsamlı adım olarak (`@2xl/stage:p-8`). Chip/buton/tablo hücresi
  padding'i kontrol padding'idir, bu ölçeğin dışındadır.
- **Bölüm ritmi — yalnız üç değer:** `py-16 sm:py-24` (içerik bölümleri) ·
  `py-20 sm:py-28` (hero'lar) · `py-8` (marquee bandı).
- **Tipografi tabanı:** en küçük boy `text-micro` (10px) ve **yalnızca** `font-mono`
  büyük harf / meta etiketlerde (`01`, `hazır`, `doğrulandı`). Cümle, başlık veya
  isim tamlaması olan her şey en az `text-xs` (12px). Rastgele `text-[Npx]` yok.
- **Kart içi düzen container query ile kırılır**, viewport breakpoint'i ile değil.
  Aynı bileşen hem dar bento hücresinde hem geniş sayfa hero'sunda render ediliyor;
  `sm:`/`lg:` "pencere genişse" der, "ben genişsem" diyemez. Sahne kökleri
  `@container/stage`, `@container/pane`, `@container/proof`, `@container/panel`,
  `@container/tile`. **Container ölçeği breakpoint ölçeği değildir:** `@sm`=384px,
  `@md`=448, `@lg`=512, `@xl`=576, `@2xl`=672, `@3xl`=768, `@4xl`=896.
  Viewport breakpoint'i yalnızca gerçek sayfa düzeyi ızgaralarda kalır.
- **Dikey hizalama `mt-auto` ile yapılır** — `TileBody` (`MarketingPrimitives.tsx`)
  üstte meta satırı, altta tabana sabitlenen içerik verir. Sabit `mt-6/7/8/16`
  hizalama YAPMAZ: bir hücrenin başlığı sarıp komşusununki sarmayınca kayar.
- **Taşma yerine sarma:** flex satırlarında ikonlara `shrink-0`, metne `min-w-0`;
  bilinen uzun tokenlar (`contact@upcytech.com`) `break-anywhere`.

## Accessibility & i18n

- Copy is Turkish-first with English available (next-intl, `messages/{tr,en}.json`,
  cookie locale, sidebar switcher). Route UI strings through `useTranslations()`.
- **Data labels come from the cube catalog** (`display` / `dimension_labels` /
  `measure_synonyms_display`), never raw snake_case — see the terminology research doc.
- Focus rings use `--ring` (brand); interactive controls have `aria-label`s; theme works
  in both modes at WCAG-reasonable contrast.

## Brand

Lowercase **`dima`**. Wordmark = `BrandMark` (Plus Jakarta Sans 400, dotless `ı` + a
separate `--brand` dot — the i-dot "atom"). The four pillars stay English:
`Deterministic · Intelligent · Modeled · Agentic`. The indigo-violet (`--brand`) is the
brand/provenance accent — used sparingly. Living reference: **`/app/style`**.
