# dima-frontend — CLAUDE.md

> ⟳ **ÖNGÖRÜ KATMANI KURULDU (2026-08-13).** Yukarıdaki *«FAZ 6'da işin içine girer»*
> beklentisi gerçekleşti ve **büyüdü**: yalnız bir öneri şeridi değil, planın başlığındaki
> **rol değişikliği** de burada yüzünü buldu — *«route ve garson KARAR VERİCİ olmaktan
> çıkıp TAHMİNCİ oluyor … **kullanıcı KARARI VERİR (bir tık)**»*.
> Plan: `belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md` · durum:
> `belgeler/plan/ONGORU-DURUM.md` (`§63`–`§79`).

## 🔴 Öngörü katmanı — hangi dosya ne yapar

| dosya | işi |
|---|---|
| `components/OneriSeridi.tsx` | yazarken **cümle** önerir (`GET /oneri`); besteciyi **sarmalar** (çapa üstte, şerit altta); `>8 kelimede` **söner** |
| `components/PillSatiri.tsx` | *«ne anladım»* — `Niyet`in pill temsili. `verilen` prop'u doluysa **ağa çıkmaz**, verilen pill'leri çizer |
| `components/PlanOnizleme.tsx` | 🔴 **koşmadan gösterilen plan**: dikey adımlar + `[koş] [düzenle] [iptal]` · geçersiz plan da **gerekçesiyle** görünür |
| `lib/onizleme.ts` | önizlemenin **durum makinesi** ve onayı. `yakala()` `true` dönerse cevap **geçmişe yazılmaz** — koşmamış bir cevap kaydedilmez |
| `lib/api-client.ts` | `postMakro` (`kos` onayı) · **`postPlanKos`** (onaylanan planı koşar, ⊘ LLM) |

⚠ **Zincir kapılı**: `test_onizleme_zinciri_kopuk_degil.py` her halkayı tek tek sınar —
bu operasyonda zincir **iki kez** sessizce koptu (`kos` gönderilmiyordu · yutulmuş istisna).

## ⚠ Büyüme tavanı — `page.tsx` · `lib/types.ts` **tavana dayalı**

`backend/tests/test_frontend_buyume.py` dosya başına **kod satırı** tavanı tutar (yorum
sayılmaz). Tavan kırmızı verirse **yükseltme**: mantığı tavansız bir modüle çıkar
(`lib/onizleme.ts` böyle doğdu); taşınamayan satır **gerekçeli** `MUAFIYET`'e yazılır.

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
kimlikli) · `POST /ask` (strict-agentic wren_sql; takip bağlamı `prev_sql` ile taşınır,
+ flag'liyse `interpretation` — OutputInsight) `/cube` `/verify` (cube_query doğrulama)
`/ask/verify` (wren_sql doğrulama — VQR'a öğretir) `/query` · `POST /ask/upload`
(chat-scoped Excel/CSV → oto-cube) · `GET|DELETE /conversations`
(sohbet geçmişi + resume, soft-delete) · `/schedules*` `/notifications` `/contracts*`.

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
bandında. Rail: geçmiş 🕐 (sohbet listesi+resume) · bildirim · yardım · ayarlar. Composer'da
📎 Excel/CSV yükleme. Güvenlik başlıkları `next.config.ts › headers()`.
