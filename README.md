# dima-frontend

`dima`'nın kullanıcı arayüzü — **Next.js 16** (App Router) + React 19 + Tailwind 4.
Doğal dille soru sor, dima'nın ürettiği SQL'i ve sonuç tablosunu gör.

WrenAI (dima-wrenai) açık kaynak tarafında hazır bir son-kullanıcı UI sunmaz; bu arayüzü
biz geliştiriyoruz. `dima-backend` (FastAPI) üzerinden `dima-wrenai` motoruna bağlanır.

```
dima-frontend (bu repo)  ──HTTP──►  dima-backend  ──►  dima-wrenai (Wren) motoru  ──►  DB
```

## Teknoloji
- Next.js 16 · React 19 · TypeScript (strict) · Tailwind 4
- TanStack Query (server state) · Zustand (client state) · axios (`lib/api-client.ts`)

## Kurulum
```bash
pnpm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL → dima-backend
pnpm dev
```

### localtld (yerel domain)
`pnpm dev`, [localtld](https://github.com/abdullahharunozturk) kuruluysa uygulamayı
sabit bir domain altında çalıştırır (yoksa düz `next dev`'e düşer):

- Frontend → **http://frontend.dima.localtld** (`package.json` › `localtld: frontend.dima`)
- Backend  → **http://backend.dima.localtld** (`.env.local` › `NEXT_PUBLIC_API_URL`)

> Domain `.localtld`'dir (localtld servisi); `allowedDevOrigins` ve backend CORS bunu kapsar.

Böylece `localhost:3000`/`:8000` yerine kalıcı domainler kullanılır (aaron/mamut ile aynı desen).
İlk sefer: `localtld setup`. localtld yoksa `NEXT_PUBLIC_API_URL=http://localhost:8000` yapın.

## Yapı
```
src/
├── app/
│   ├── layout.tsx      # Providers (React Query) sarmalar
│   └── page.tsx        # Ana demo: soru → SQL → sonuç
├── components/
│   ├── ResultTable.tsx
│   └── SchemaPanel.tsx # /schema'dan veri modeli
├── lib/
│   ├── api-client.ts   # tüm HTTP burada
│   ├── providers.tsx   # React Query provider
│   └── types.ts        # backend ile senkron tipler
└── stores/
    └── history.ts      # Zustand: son sorular
```

## Canlıya alma (Vercel)
`vercel.json` framework'ü `nextjs`, paket yöneticisini `pnpm` olarak sabitler. Backend URL'i
tek env değişkeninden gelir: **`NEXT_PUBLIC_API_URL`** (Vercel → Environment Variables;
`api-client.ts` bunu okur, yoksa `localhost:8000`'e düşer). `NEXT_PUBLIC_*` build-time
inline'dır — değişince yeniden deploy gerekir. Bu repo backend'den bağımsız deploy edilir
(ekip ayrımı); backend'e yalnızca HTTP + Swagger `/docs` üzerinden erişilir. Detay: dima kökü
[`docs/deployment.md`](../docs/deployment.md).

## Notlar
- Kimlik doğrulama demo fazında yok (planlı).
- Standartlar: kök `saka-standards` submodule'ü (strict TS, no `any`, `lib/api-client.ts` tekil).
