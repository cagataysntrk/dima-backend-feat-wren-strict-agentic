# SUNUCU KOMUTLARI — *ne yapacağım*

> Ana proje dizininde çalıştır:
> `/home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic`

---

## ⚡ EN SIK ÜÇ DURUM — kopyala yapıştır

### 1 · Backend kodunu değiştirdim
```bash
export DOCKER_BUILDKIT=0 && export COMPOSE_DOCKER_CLI_BUILD=0 && \
docker-compose build dima-backend && \
docker rm -f dima-backend-core && \
docker-compose up -d dima-backend
```
⚠ **Rebuild şart** — kaynak kodu konteynere bind-mount **edilmiyor**; `docker restart`
eski kodu çalıştırmaya devam eder.

### 2 · Frontend kodunu değiştirdim
**Hiçbir şey yapma.** Hot-reload var, tarayıcı kendi güncellenir.

### 3 · Sunucu takıldı, kod değişmedi
```bash
docker restart dima-backend-core
```

---

## ADRESLER

| ne | nerede |
|---|---|
| Backend API | **`http://localhost:8001`** |
| Frontend | `http://localhost:3000` |
| Giriş | `demo-boyahane@usedima.com` / `dima-demo-1234` |

⚠ Backend konteyner içinde 8000'de, dışarıya **8001** olarak açılıyor. Frontend'in
`.env.local`'ında `BACKEND_ORIGIN=http://localhost:8001` **olmalı** — `next.config.ts`'in
varsayılanı 8000'dir ve backend orada değildir.

---

## BACKEND

| ne yapmak istiyorsun | komut |
|---|---|
| logları izle | `docker logs -f dima-backend-core` *(çıkış: CTRL+C)* |
| yeniden başlat | `docker restart dima-backend-core` |
| durumu gör | `docker ps --filter name=dima-backend-core` |
| içine gir | `docker exec -it dima-backend-core bash` |

### Demo veritabanını doldur (seed)
```bash
docker exec dima-backend-core python -m control_plane.cli seed-demo
```

🔴 **Her rebuild'de GEREKMEZ.** Veri `dima_logs` adlandırılmış volume'ünde duruyor ve
`docker rm -f`'i de rebuild'i de **atlatır**. Yalnız şu üç durumda çalıştır:

- **ilk kurulum** (volume henüz boş)
- `docker compose down **-v**` sonrası (`-v` volume'leri de siler)
- kullanıcı/şirket fixture'ı bozulduysa

---

## FRONTEND — **pnpm** (npm değil)

```bash
cd dima-frontend-demo-master
pnpm install        # yalnız ilk kurulumda veya paket eklendiğinde
pnpm dev            # → http://localhost:3000
```

🔴 **`npm install` KULLANMA.** Proje `pnpm@10.12.1` ile yönetiliyor ama dizinde eski bir
`package-lock.json` da duruyor; `npm` onu kullanır ve **farklı bir bağımlılık ağacı**
kurar. Sonrası *"bende çalışıyordu"* sınıfı hatalar.

Prod derlemesi gerekiyorsa: `pnpm build && pnpm start`

---

## TEST — hangisini ne zaman

| durum | komut | süre |
|---|---|---|
| **bir dosya düzenledim** | `cd backend && python lab/kapi.py --hizli --degisen <dosyalar>` | ~15-60 sn |
| **demet bitti** *(bir kez)* | `cd backend && python lab/kapi.py --tam` | ~3 dk |
| gecelik CI | `python lab/kapi.py --hepsi` | ~5 dk |

🔴 **`--hepsi` yerelde koşulmaz** — yeri gecelik CI'dır.

### Canlı LLM denemesi
```bash
python3 test_auth.py
```
Giriş yapar, `/ask`'e soru gönderir, JSON cevabı basar.
⚠ **Gerçek LLM çağırır, kota harcar.** Kod değişikliğini sınamak için **kullanma** —
onun yeri yukarıdaki kapılar. Ayrıntı: `belgeler/kilavuz/TEST-ORTAMI-KILAVUZU.md`

---

## YENİ BİR MAKİNEDE İLK KURULUM

```bash
# 1 · .env dosyasını kök dizine koy  🔴 ZORUNLU — commit'li DEĞİL (sırlar içerir)
#     yoksa docker-compose hiç başlamaz

# 2 · servisleri ayağa kaldır
docker-compose up -d

# 3 · demo verisini yükle
docker exec dima-backend-core python -m control_plane.cli seed-demo

# 4 · frontend
cd dima-frontend-demo-master && pnpm install && pnpm dev
```

---

## SORUN GİDERME

| belirti | sebep | çözüm |
|---|---|---|
| Kod değişikliği etkisiz | rebuild yapılmadı | **Durum 1**'deki komut |
| `docker-compose` hiç başlamıyor | kökte `.env` yok | `.env` dosyasını koy |
| Frontend backend'i bulamıyor | `BACKEND_ORIGIN` yanlış/eksik | `.env.local` → `http://localhost:8001` |
| Giriş yapılamıyor | seed yapılmamış | seed komutu |
| Frontend paketleri tuhaf | `npm install` yapılmış | `rm -rf node_modules && pnpm install` |

---

<sub>⟳ **Denetim notu (2026-08-05):** bu belgedeki her komut `docker-compose.yml` ·
`control_plane/cli.py` · `package.json` · `next.config.ts` · `test_auth.py`
kaynaklarına karşı doğrulandı. Önceki sürümde beş hata vardı (frontend'in Vite+npm
sanılması · port yazmaması · gereksiz seed talimatı · volume gerekçesi · `.env`
gereğinin atlanması); hatalı hâl ve gerekçeleri commit `3466587`'de kayıtlıdır.</sub>
