# dima-frontend — CLAUDE.md

## Rol
`dima`'nın son-kullanıcı arayüzü. WrenAI açık kaynak tarafında UI sunmadığından
bu arayüz sıfırdan bizim ürünümüz. Veriye asla doğrudan dokunmaz; her şey
`dima-backend` HTTP API'si üzerinden gider.

## Teknoloji
- Next.js 16 (App Router) · React 19 · TypeScript strict · Tailwind 4
- **shadcn/ui** (Radix) tasarım sistemi · **next-intl** (çok-dil) · next-themes · lucide
- TanStack Query (server state) · Zustand (client state, `stores/conversations.ts`) · axios
- Recharts (grafik) · motion (animasyon) · sonner (toast)
- Rota grupları: `(auth)` · `(marketing)` · `(product)/app` (asıl uygulama) · `api/[...path]` proxy

## Komutlar
```bash
pnpm dev       # geliştirme (:3000)
pnpm build     # prod build
pnpm lint      # eslint
```

## Kurallar (saka-standards)
- **Tüm HTTP `src/lib/api-client.ts`'ten** geçer — dağınık `fetch` yok.
- Server state → React Query; client state → Zustand; form → (eklenince) React Hook Form + Zod.
- `any` yasak; strict tipler. Backend tipleri `src/lib/types.ts`'te senkron tutulur.
- Import alias `@/*`.
- Commit mesajlarında Claude footer KULLANILMAZ.

## Backend sözleşmesi
Tarayıcı same-origin **`/api/*`**'e konuşur; Next rewrite-proxy'si `BACKEND_ORIGIN`'e
iletir (backend URL'i browser'a sızmaz, refresh cookie same-origin kalır).
Uçlar: `POST /auth/login|refresh|logout` · `GET /auth/me` (roller + `permissions`) ·
`GET /schema` (cube kataloğu + `lower_is_better`) · `GET /features` (bayraklar,
kimlikli) · `GET /starters` (K1 küratörlü başlangıç soruları) · `POST /ask`
(+ flag `cikti_yorumlama` açıksa yanıtta `interpretation` → OutputInsight, ADR-0022;
+ `next_steps`/`recommendations` → K2/K4) `/cube` `/verify` (opsiyonel `comment`)
`/query` · `/schedules*` (alarm: `threshold` eşik|zscore, `delivery.email`)
`/notifications` `/contracts*`.

## Rehberli analitik (K1–K4)
Cevabın altındaki yönlendirmeler; hepsi DETERMİNİSTİK (LLM yok) ve bayrak arkasında —
backend göndermezse hiç render edilmez.
- **K1** `/starters` → `HelpPanel` (küratör boşsa yerel yedek liste).
- **K2** `next_steps` → `report/NextSteps` chip'leri; tıklama TAM `cube_query` ile
  `/cube`'a gider (yorum çubuğundaki chip düzenlemesiyle aynı yol).
- **K3** `interpretation.signals` → `OutputInsight` içinde önem renkli kutular
  (anomali · yön · yoğunlaşma).
- **K4** `recommendations` → `report/Recommendations`; opsiyonel `action` K2'nin
  drill mekanizmasını yeniden kullanır.

## Kimlik doğrulama
- Auth ZORUNLU: access token memory'de (`api-client.ts` — localStorage'a ASLA), refresh
  HTTP-only cookie'de; 401 → tek uçuşta paylaşılan refresh → retry interceptor'ı.
- Sayfa koruması `src/proxy.ts` (cookie adı `NEXT_PUBLIC_SESSION_COOKIE ?? "dima_refresh"`).
- Login'de OTP adımı: backend 401 "OTP gerekli" dönerse alan açılır.
- Buton görünürlüğü `/auth/me` `permissions`'ından (`vqr:write`, `schedule:create`) —
  rol matrisi backend'dedir, UI'a KOPYALANMAZ.

## UI chrome
shadcn tabanlı kabuk: `components/shell/AppShell` + `AppSidebar` (sol kenar çubuğu — gezinme +
sohbetler) + `Composer` (soru + 📎 dosya). Sheet/dialog/popover `components/ui/` primitifleri;
tema `next-themes`, çok-dil `next-intl`. Güvenlik başlıkları `next.config.ts › headers()`.
