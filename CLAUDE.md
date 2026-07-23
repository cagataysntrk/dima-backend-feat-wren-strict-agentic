# dima-frontend — CLAUDE.md

## Rol
`dima`'nın son-kullanıcı arayüzü. WrenAI açık kaynak tarafında UI sunmadığından
bu arayüz sıfırdan bizim ürünümüz. Veriye asla doğrudan dokunmaz; her şey
`dima-backend` HTTP API'si üzerinden gider.

## Teknoloji
- Next.js 16 (App Router) · React 19 · TypeScript strict · Tailwind 4
- TanStack Query (server state) · Zustand (client state) · axios

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
kimlikli) · `POST /ask` `/cube` `/verify` `/query` · `/schedules*` `/notifications`
`/contracts*`.

## Kimlik doğrulama
- Auth ZORUNLU: access token memory'de (`api-client.ts` — localStorage'a ASLA), refresh
  HTTP-only cookie'de; 401 → tek uçuşta paylaşılan refresh → retry interceptor'ı.
- Sayfa koruması `src/proxy.ts` (cookie adı `NEXT_PUBLIC_SESSION_COOKIE ?? "dima_refresh"`).
- Login'de OTP adımı: backend 401 "OTP gerekli" dönerse alan açılır.
- Buton görünürlüğü `/auth/me` `permissions`'ından (`vqr:write`, `schedule:create`) —
  rol matrisi backend'dedir, UI'a KOPYALANMAZ.

## UI chrome
Sağ kenarda görünmez ikon şeridi (rail, w-12; sayfa `pr-12` bırakır); sheet'ler şeridin
solunda (`right-12`) açılır, aynı ikona ikinci tıklama kapatır (toggle), ✕ şerit başlık
bandında. Güvenlik başlıkları `next.config.ts › headers()`.
