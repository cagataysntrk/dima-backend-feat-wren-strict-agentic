# E2E — Uçtan uca test

Bağımlılıksız uçtan uca test: **dima-frontend + dima-backend + dima (Wren engine)**
zincirinin tamamını gerçek bir tarayıcıyla doğrular. Ekstra paket kurmaz — Node 22'nin
native `fetch` + `WebSocket`'ini ve sistemdeki Chrome'u (headless, CDP üzerinden) kullanır.

## Ne test edilir

**API katmanı** (`BACKEND_URL`):
- `/health` ayakta mı
- `/schema` tablolar-arası **ilişkileri** döndürüyor mu (makineler hub)
- `/ask` çapraz-tablo sorusuna **JOIN** üretip satır döndürüyor mu

**Tarayıcı katmanı** (`FRONTEND_URL`):
- Sayfa render ediliyor mu
- Client **hydrate** oluyor mu (React fiber) — localtld/Caddy origin'inde
  `allowedDevOrigins` eksikse burası patlar
- Örnek butona tıklayınca input doluyor mu
- Gerçek `fetch` sonrası üretilen SQL + sonuç tablosu geliyor mu

## Çalıştırma

Önce her iki servis de ayakta olmalı (ayrı terminallerde):

```bash
# dima-backend
cd ../dima-backend && npm run dev

# dima-frontend
npm run dev
```

Sonra:

```bash
npm run e2e
```

## Ortam değişkenleri

| Değişken       | Varsayılan                          |
| -------------- | ----------------------------------- |
| `FRONTEND_URL` | `http://frontend.dima.localtld`  |
| `BACKEND_URL`  | `http://backend.dima.localtld`   |
| `CHROME_BIN`   | otomatik bulunur                    |
| `CDP_PORT`     | `9222`                              |
| `HEADFUL=1`    | tarayıcıyı görünür başlatır (debug) |

localtld olmadan (düz localhost) çalıştırmak için:

```bash
FRONTEND_URL=http://localhost:3000 BACKEND_URL=http://localhost:8000 npm run e2e
```

Çıkış kodu: tümü geçerse `0`, aksi halde `1` (CI için uygun).
