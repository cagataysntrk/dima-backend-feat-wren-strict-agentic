# DİMA Server Başlatma ve Yönetim Komutları

Bu belge, DİMA Agentic projesinde (WrenAI entegreli yeni mimari) geliştirme yaparken backend (sunucu) ve frontend (arayüz) projelerini nasıl başlatacağınızı, yeniden başlatacağınızı ve logları nasıl izleyeceğinizi özetler.

> ⟳ **DENETLENDİ — 2026-08-05.** Her komut `docker-compose.yml` · `control_plane/cli.py` ·
> `package.json` · `next.config.ts` · `test_auth.py` kaynaklarına karşı doğrulandı.
> **Beş hata bulundu ve düzeltildi**; düzeltmeler aşağıda 🔴 ile işaretli, eski hâl
> üstü çizili olarak **duruyor** (silinmedi — *yanlış bir talimatın nerede yanlış
> olduğunu bilmek, doğrusunu bilmek kadar işe yarar*).
>
> | # | neydi | ne oldu |
> |---|---|---|
> | 1 | frontend *"React / Vite"* + `npm` | 🔴 **Next.js 16.2.10** + **pnpm** (`packageManager: pnpm@10.12.1`) |
> | 2 | port hiç yazmıyordu | 🔴 backend **`localhost:8001`** (`8001:8000` eşlemesi) |
> | 3 | *"her rebuild sonrası seed"* | 🔴 gereksiz — `dima_logs` **adlandırılmış volume**, veri `docker rm`'i **atlatır** |
> | 4 | *"backend için volume tanımlı değil"* | ⚠ volume **var** (logs + HF önbelleği); olmayan şey **kaynak bind-mount**'u — sonuç (rebuild şart) yine doğru |
> | 5 | `.env` gereği yazmıyordu | ⚠ `env_file: .env` — dosya yoksa compose **başlamaz** |

---

## 1. Backend (FastAPI + Wren Engine) Yönetimi

⚠ **Düzeltme (4):** ~~`backend` klasörü için bir `volume` tanımlı olmadığı için~~ →
`dima-backend` servisinin **iki volume'u var** (`dima_logs`, `dima_hf_cache`), ama
**kaynak kodu bind-mount'u yok**. Yani Python kodunda (`ask.py`, `interpret.py`)
değişiklik yaptığınızda imajı **yeniden inşa etmeniz (rebuild)** gerekir — sonuç aynı,
gerekçe farklı.

🔴 **Erişim adresi: `http://localhost:8001`** — `docker-compose.yml` `8001:8000`
eşlemesi yapıyor (konteyner içi 8000, dışarısı **8001**). `test_auth.py` de 8001'e
gidiyor; frontend'in `.env.local`'ı da `BACKEND_ORIGIN=http://localhost:8001` diyor.
⚠ `next.config.ts`'in **varsayılanı 8000**'dir — `.env.local` olmadan frontend
backend'i **bulamaz**.

⚠ **`.env` zorunlu:** servis `env_file: .env` ile tanımlı. Dosya yoksa `docker-compose`
başlamaz. (Repo kökünde var; yeni bir makinede kurarken kopyalanmalı — **commit'li
değildir**, sırlar içerir.)

Aşağıdaki komutları ana proje dizinindeyken (`/home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic`) çalıştırın.

### A. Kodu Değiştirdikten Sonra Yeniden Başlatma (Tam Rebuild)
Kodda bir değişiklik yaptıktan sonra yeni kodun aktif olması için aşağıdaki komutu **tek seferde** kopyalayıp yapıştırın. Bu komut, eski konteyneri silip yenisini taze kodla ayağa kaldırır:

```bash
export DOCKER_BUILDKIT=0 && export COMPOSE_DOCKER_CLI_BUILD=0 && \
docker-compose build dima-backend && \
docker rm -f dima-backend-core && \
docker-compose up -d dima-backend
```

### B. Demo Veritabanını Doldurma (Seed) — 🔴 *"her rebuild"* DEĞİL

~~Tam rebuild yaptığınızda içerideki SQLite demo veritabanı sıfırlanabilir; **her
rebuild sonrasında** doldurun.~~

🔴 **Bu artık doğru değil ve nedeni `docker-compose.yml`'de yazılı.** 2 Ağustos 2026'da
`dima_logs` **adlandırılmış volume**'ü eklendi; compose dosyasının kendi yorumu şöyle
diyor: *"Önceden bu servisin HİÇ volume'u yoktu ve `sqlite:////app/logs/dima.db`
konteyner katmanına yazıyordu → **HER build tüm `interaction_log`'u, Query Contract
kanıtlarını, sohbet geçmişini SİLİYORDU**."*

Yani bugün veri **`docker rm -f`'i de rebuild'i de atlatır**. Seed yalnız şu üç
durumda gerekir:

| ne zaman | neden |
|---|---|
| **ilk kurulum** | volume henüz boş |
| `docker compose down **-v**` sonrası | `-v` volume'leri de siler |
| kullanıcı/şirket fixture'ı bozulduysa | elle sıfırlama |

⚠ *Gereksiz bir seed zararsız görünür ama bir alışkanlık üretir: "veri kaybolur"
inancı, gerçekten kaybolduğu günü fark etmeyi zorlaştırır.*

```bash
docker exec dima-backend-core python -m control_plane.cli seed-demo
```
*(Bunu yaptıktan sonra `demo-boyahane@usedima.com` şifre: `dima-demo-1234` kullanıcısı sisteme tanımlanır.)*

### C. Hızlı Yeniden Başlatma (Sadece Restart)
Eğer kodda değişiklik yapmadıysanız, sadece sunucu kilitlendiyse veya baştan başlamasını istiyorsanız, basit restart komutu:

```bash
docker restart dima-backend-core
```

### D. Logları Canlı Olarak İzleme
Sunucunun arka planda ne yaptığını (Hata mesajları, HTTP istekleri) görmek için:

```bash
docker logs -f dima-backend-core
```
*(Çıkmak için `CTRL + C` tuşlarına basın)*

---

## 2. Frontend (🔴 **Next.js 16** — Vite DEĞİL) Yönetimi

~~Frontend (React / Vite) … `npm install` … `npm run dev` … olmazsa `npm start`.~~

🔴 **Üç hata birden vardı, üçü de `package.json`'dan doğrulandı:**

| iddia | gerçek | kanıt |
|---|---|---|
| *"React / Vite"* | **Next.js 16.2.10** (App Router) | `package.json` → `"next": "16.2.10"` |
| `npm install` | **pnpm** | `package.json` → `"packageManager": "pnpm@10.12.1"` |
| *"olmazsa `npm start`"* | `start` = `next start` → **önce `build` ister** | `"start": "next start"` |

⚠ **Neden `npm` ile kurmak zararlı:** dizinde **hem** `pnpm-lock.yaml` (143 KB) **hem**
`package-lock.json` (242 KB) var. `npm install` ikincisini kullanır ve pnpm kilidinden
**farklı bir bağımlılık ağacı** üretir — sonra *"bende çalışıyordu"* sınıfı hatalar
başlar. `backend/../dima-frontend-demo-master/CLAUDE.md` de `pnpm` diyor.

Frontend canlı kod güncellemelerini destekler (Hot-Reload); arayüz değişikliğinde
yeniden başlatmanıza gerek yoktur.

### Frontend'i Başlatmak İçin:

```bash
cd dima-frontend-demo-master
pnpm install        # (sadece ilk kurulumda veya paket eklendiğinde)
pnpm dev            # → http://localhost:3000
```

⚠ `pnpm dev` betiği `localtld` varsa onu kullanır, yoksa düz `next dev`'e düşer —
ikisi de çalışır, ek kurulum gerekmez.

🔴 **Backend adresi:** tarayıcı same-origin `/api/*`'e konuşur, Next rewrite-proxy'si
`BACKEND_ORIGIN`'e iletir. `.env.local` içinde **`BACKEND_ORIGIN=http://localhost:8001`**
olmalı — `next.config.ts`'in varsayılanı **8000**'dir ve backend orada **değildir**.

### Prod derlemesi (dev değil)
```bash
pnpm build && pnpm start
```

---

## 3. Test Komutları

Agentic mimarinin çalışıp çalışmadığını, LLM (Yapay zeka) yanıtlarını doğrudan test etmek için hızlı test betiğimizi kullanabilirsiniz.

Ana dizinde:
```bash
python3 test_auth.py
```
Bu script, backend'e giriş yapar (login), ardından `/ask` endpoint'ine bir soru gönderir ve dönen JSON yanıtını (grafik tipi, sql, kanıt zinciri vs.) ekrana yazdırır.

✅ **Doğrulandı:** dosya repo kökünde mevcut ve `http://localhost:8001` adresine
gidiyor — yani yukarıdaki port düzeltmesiyle tutarlı.

⚠ **Bu betik CANLI LLM çağırır** (kota harcar). Kod değişikliğini sınamak için
uygun **değildir**; onun yeri `backend/lab/kapi.py` kapılarıdır:

```bash
cd backend
python lab/kapi.py --hizli --degisen <değişen dosyalar>   # ~15-60 sn, geliştirme sırasında
python lab/kapi.py --tam                                  # ~1 dk 50 sn, DEMET SONUNDA bir kez
```

🔴 `python lab/kapi.py --hepsi` **yerelde koşulmaz** — yeri gecelik CI'dır
(`backend/CLAUDE.md` test kapısı politikası).
