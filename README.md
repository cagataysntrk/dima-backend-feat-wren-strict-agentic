# dima-frontend

`dima`'nın kullanıcı arayüzü — **Next.js 16** (App Router) + React 19 + Tailwind 4.
Doğal dille soru sor, dima'nın ürettiği SQL'i ve sonuç tablosunu gör.

WrenAI (dima-wrenai) açık kaynak tarafında hazır bir son-kullanıcı UI sunmaz; bu arayüzü
biz geliştiriyoruz. `dima-backend` (FastAPI) üzerinden `dima-wrenai` motoruna bağlanır.

```
dima-frontend (bu repo)  ──HTTP──►  dima-backend  ──►  dima-wrenai (Wren) motoru  ──►  DB
```

## Teknoloji
- Next.js 16 (App Router) · React 19 · TypeScript (strict) · Tailwind 4
- **shadcn/ui** (Radix) tasarım sistemi · **next-intl** (çok-dil) · next-themes · lucide ikonlar
- TanStack Query (server state) · Zustand (client state) · axios (`lib/api-client.ts`)
- Recharts (grafik) · motion (animasyon) · sonner (toast)

## Kurulum
```bash
pnpm install
cp .env.local.example .env.local   # BACKEND_ORIGIN → dima-backend (server-side)
pnpm dev
```

### localtld (yerel domain)
`pnpm dev`, [localtld](https://github.com/abdullahharunozturk) kuruluysa uygulamayı
sabit bir domain altında çalıştırır (yoksa düz `next dev`'e düşer):

- Frontend → **http://frontend.dima.localtld** (`package.json` › `localtld: frontend.dima`)
- Backend  → **http://backend.dima.localtld** (`.env.local` › `BACKEND_ORIGIN`)

> Domain `.localtld`'dir (localtld servisi); `allowedDevOrigins` ve backend CORS bunu kapsar.

Böylece `localhost:3000`/`:8000` yerine kalıcı domainler kullanılır (aaron/mamut ile aynı desen).
İlk sefer: `localtld setup`. localtld yoksa `BACKEND_ORIGIN=http://localhost:8000` yapın.

## Yapı
```
src/
├── app/
│   ├── (auth)/          # login · register · forgot-password
│   ├── (marketing)/     # pazarlama sayfaları (about, product, solutions, security, …)
│   ├── (product)/app/   # asıl dima uygulaması (sohbet + rapor)
│   └── api/[...path]/    # same-origin proxy → BACKEND_ORIGIN
├── components/
│   ├── ui/              # shadcn/ui primitifleri (Radix)
│   ├── shell/           # AppShell · AppSidebar · Composer · drawer'lar
│   ├── ai/ chart/ report/ schema/ auth/ marketing/
│   ├── ChatPanel · ReportPanel · ResultView · ResultTable · PivotTable
│   ├── KpiCard · OutputInsight (çıktı yorumu, ADR-0022) · InterpretationBar (cube-query chip'leri)
│   └── SchemaPanel · Landing · NotificationsBell · ConnectionBadge · …
├── lib/                 # api-client (tüm HTTP) · chart · format · thinking · access · types · utils
├── stores/conversations.ts   # Zustand: sohbet listesi (memory; backend persist ileride)
└── hooks/ · i18n/ · content/
```

## Canlıya alma (Vercel)
`vercel.json` framework'ü `nextjs`, paket yöneticisini `pnpm` olarak sabitler. Backend
adresi **server-side** env'den gelir: **`BACKEND_ORIGIN`** (Vercel → Environment
Variables). Tarayıcı backend'i hiç görmez: istekler same-origin `/api/*`'e gider, Next
rewrite-proxy'si backend'e iletir (refresh cookie same-origin kalır, CORS gerekmez).
Bu repo backend'den bağımsız deploy edilir (ekip ayrımı). Detay: dima kökü
[`docs/deployment.md`](../docs/deployment.md).

## Kimlik doğrulama
Login **zorunludur** (ADR-0014): `/login` sayfası → Bearer access token **memory'de**
(localStorage'a asla yazılmaz), refresh token **HTTP-only cookie'de** (`dima_refresh`;
adı `NEXT_PUBLIC_SESSION_COOKIE` ile senkronlanır). Sayfa koruması `src/proxy.ts`
(cookie yoksa `/login`); 401 → sessiz refresh → retry zinciri `api-client.ts`'te.
MFA'lı hesapta doğru paroladan sonra OTP alanı açılır. Verify (✓/✗) ve 🔔 zamanla
butonları `/auth/me` `permissions` listesine bağlıdır — rol semantiği UI'a kopyalanmaz.

## UI düzeni (chrome)
shadcn tabanlı uygulama kabuğu: `components/shell/AppShell` + `AppSidebar` (sol kenar çubuğu —
gezinme + sohbetler), `Composer` (soru girişi + 📎 dosya). Sheet/dialog/popover shadcn `ui/`
primitifleriyle; tema `next-themes` (amber-CRT), çok-dil `next-intl`. Isı haritası renk yönü
`/schema cubes[].lower_is_better` metadata'sından gelir (regex yalnız yedek).

## Notlar
- Güvenlik başlıkları `next.config.ts › headers()` içinde (frame/sniff/referrer/permissions).
- Standartlar: kök `saka-standards` submodule'ü (strict TS, no `any`, `lib/api-client.ts` tekil).
