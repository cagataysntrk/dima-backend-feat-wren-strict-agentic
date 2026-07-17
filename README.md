# dima-frontend

`dima`'nın kullanıcı arayüzü — **Next.js 16** (App Router) + React 19 + Tailwind 4.
Doğal dille soru sor, dima'nın ürettiği SQL'i ve sonuç tablosunu gör.

WrenAI (dima) açık kaynak tarafında hazır bir son-kullanıcı UI sunmaz; bu arayüzü
biz geliştiriyoruz. `dima-backend` (FastAPI) üzerinden `dima` motoruna bağlanır.

```
dima-frontend (bu repo)  ──HTTP──►  dima-backend  ──►  dima (Wren) motoru  ──►  DB
```

## Teknoloji
- Next.js 16 · React 19 · TypeScript (strict) · Tailwind 4
- TanStack Query (server state) · Zustand (client state) · axios (`lib/api-client.ts`)

## Kurulum
```bash
pnpm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL → dima-backend
pnpm dev                            # http://localhost:3000
```
`dima-backend`'in `http://localhost:8000` üzerinde çalışıyor olması gerekir.

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

## Notlar
- Kimlik doğrulama demo fazında yok (planlı).
- Standartlar: kök `saka-standards` submodule'ü (strict TS, no `any`, `lib/api-client.ts` tekil).
