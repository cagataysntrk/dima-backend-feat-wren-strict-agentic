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
`dima-backend` endpoint'leri: `GET /schema`, `POST /ask`, `POST /query`, `POST /dry-plan`.
`NEXT_PUBLIC_API_URL` ile adres verilir (varsayılan `http://localhost:8000`).
