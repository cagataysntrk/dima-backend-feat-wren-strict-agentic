# SUNUCU KOMUTLARI — *ne yapacağım*

> 🔴 **BU DOSYA REÇETENİN SAHİBİDİR** ㊲. Kök [`README.md`](../../README.md) §3'te
> **kısaltılmış** bir kopya var (yeni gelen için); bir adım değişirse **önce burası**
> güncellenir, sonra oradaki özet. *İki reçete, bir gün iki farklı sistem demektir.*

> Ana proje dizininde çalıştır:
> `/home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic`

> ⟳ **2026-08-13'te baştan doğrulandı.** Önceki sürümdeki komutların **tamamı ölü bir
> konteyner adına** (`dima-backend-core`) gidiyordu ve rebuild reçetesi `docker-compose`
> kullanıyordu — ikisi de bugün **çalışmıyor**. Ayrıntı en altta.

---

## ⚡ EN SIK ÜÇ DURUM — kopyala yapıştır

### 1 · Backend kodunu değiştirdim → **yeniden derle**

```bash
cd /home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic

# ① Etiketi KENDİ hesapla — elle yazılan bir değişken unutulur ve boş kalır.
ETIKET="s$(( $(docker images --format '{{.Tag}}' dima-backend-temiz \
              | sed 's/^s//' | sort -n | tail -1) + 1 ))"
echo "yeni etiket: $ETIKET"

# ② ÖNCE DERLE. Derleme düşerse burada durur — çalışan kaba HİÇ dokunulmamış olur.
docker build -t "dima-backend-temiz:$ETIKET" backend/ || { echo "🔴 derleme düştü — kap YERİNDE, hiçbir şey yapma"; return 2>/dev/null || exit 1; }

# ③ Ancak imaj hazırsa değiştir.
docker rm -f dima-oneri-8002
docker run -d --name dima-oneri-8002 -p 8002:8000 --env-file .env \
  -v dima-backend-feat-wren-strict-agentic_dima_logs:/app/logs \
  -v dima-backend-feat-wren-strict-agentic_dima_hf_cache:/tmp/fastembed_cache \
  "dima-backend-temiz:$ETIKET"

# ④ Sağlık — 200 gelene kadar yokla (ısınma ~25 sn, öneri ucu o pencerede leksik cevap verir).
for i in $(seq 1 40); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' -m 4 localhost:8002/health)" = "200" ] \
    && { echo "✅ ayakta ($ETIKET)"; break; }
done
```

🔴🔴 **BU BLOK BİR KEZ BACKEND'İ ÇÖKERTTİ — ve sebebi SIRAYDI** *(ölçüldü, 2026-08-13)*.
Eski hâlinde `docker rm -f` **derlemeden önce** koşuyordu ve `ETIKET` elle atanan bir
değişkendi. Kullanıcı bloğu kopyalarken `ETIKET` satırı boş kaldı → `docker build -t
dima-backend-temiz:` **`invalid reference format`** ile düştü → ama bir sonraki satır
çalışan kabı **yine de sildi** → `docker run` da düştü ve **backend gitti**.

> *Yıkıcı adım, doğrulanmış adımdan sonra gelir.* Bir kurulum reçetesinde `rm -f`,
> yerine koyacağın şey **elinde olduktan sonra** yazılır — önce değil.

⚠ Ve `ETIKET` artık **elle yazılmaz**: yukarıdaki satır mevcut en büyük etiketi bulup bir
artırıyor. *Bir reçetenin doğru çalışması, kullanıcının bir satırı atlamamasına bağlı
olmamalıdır.*

**Çöktüyse — tek satırlık kurtarma** (son sağlam imajla geri kaldır):

```bash
docker run -d --name dima-oneri-8002 -p 8002:8000 --env-file .env \
  -v dima-backend-feat-wren-strict-agentic_dima_logs:/app/logs \
  -v dima-backend-feat-wren-strict-agentic_dima_hf_cache:/tmp/fastembed_cache \
  "dima-backend-temiz:$(docker images --format '{{.Tag}}' dima-backend-temiz | sed 's/^s//' | sort -n | tail -1 | sed 's/^/s/')"
```

⚠ **Rebuild şart** — kaynak kod konteynere bind-mount **edilmiyor**; `docker restart`
eski kodu çalıştırmaya devam eder. *(Bu, bu depoda defalarca «düzelttim ama değişmedi»
sanılmasına yol açtı: kod repoda doğruydu, konteynerde eskiydi.)*

⚠ **`-v …_dima_hf_cache` satırını düşürme.** Gömme modeli orada duruyor; düşerse konteyner
her açılışta modeli **yeniden indirmeye** çalışır ve öneri/öngörü ucu ilk isteklerde
asılı kalır.

### 2 · Frontend kodunu değiştirdim
**Hiçbir şey yapma.** `pnpm dev` hot-reload ile kendini günceller.

### 3 · Sunucu takıldı, kod değişmedi
```bash
docker restart dima-oneri-8002
```

---

## ADRESLER

| ne | nerede |
|---|---|
| **Backend API (frontend'in konuştuğu)** | **`http://localhost:8002`** — kap `dima-oneri-8002` |
| Eski/ikinci backend | `http://localhost:8001` — kap `dima-backend-temiz` *(imaj `s06`, **eski**)* |
| Frontend | `http://localhost:3000` |
| Giriş | `demo-boyahane@usedima.com` / `dima-demo-1234` |

⚠ Backend konteyner içinde **8000**'de dinler, dışarıya **8002** olarak açılır.
Frontend'in `.env.local`'ında `BACKEND_ORIGIN=http://localhost:8002` **olmalı**
(`next.config.ts`'in varsayılanı `8000`'dir ve backend orada **değildir**).

🔴 **İki backend birden koşuyor.** `8001` eski bir imajı (`s06`) taşıyor ve kimse ona
konuşmuyor. Bir davranışı sınarken **hangi porta** baktığını doğrula — yoksa bugünkü
kodu sınadığını sanıp aylar öncesini ölçersin.

---

## BACKEND

| ne yapmak istiyorsun | komut |
|---|---|
| logları izle | `docker logs -f dima-oneri-8002` *(çıkış: CTRL+C)* |
| son 30 satır | `docker logs --tail 30 dima-oneri-8002` |
| yeniden başlat | `docker restart dima-oneri-8002` |
| durumu gör | `docker ps --filter name=dima-oneri-8002` |
| **hangi imajı koşuyor** | `docker inspect dima-oneri-8002 --format '{{.Config.Image}}'` |
| içine gir | `docker exec -it dima-oneri-8002 bash` |

### Demo veritabanını doldur (seed)
```bash
docker exec dima-oneri-8002 python -m control_plane.cli seed-demo
```

🔴 **Her rebuild'de GEREKMEZ.** Veri `…_dima_logs` adlandırılmış volume'ünde duruyor ve
`docker rm -f`'i de rebuild'i de **atlatır**. Yalnız şu üç durumda çalıştır:

- **ilk kurulum** (volume henüz boş)
- `docker volume rm` ya da `docker compose down **-v**` sonrası
- kullanıcı/şirket fixture'ı bozulduysa

### Sağlık ve hızlı duman testi
```bash
curl -s localhost:8002/health

TK=$(curl -s -X POST localhost:8002/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' -H "Authorization: Bearer $TK" \
  --get --data-urlencode 'q=fire' localhost:8002/oneri
```
⚠ **Token çabuk bayatlar** — her denemede yeniden al. `401` görürsen önce bunu şüphelen.

---

## FRONTEND — **pnpm** (npm değil)

```bash
cd dima-frontend-demo-master
pnpm install        # yalnız ilk kurulumda veya paket eklendiğinde
pnpm dev            # → http://localhost:3000
```

🔴 **`npm install` KULLANMA.** Proje `pnpm@10.12.1` ile yönetiliyor ama dizinde eski bir
`package-lock.json` da duruyor; `npm` onu kullanır ve **farklı bir bağımlılık ağacı**
kurar. Sonrası *«bende çalışıyordu»* sınıfı hatalar.

Prod derlemesi gerekiyorsa: `pnpm build && pnpm start`

---

## TEST — hangisini ne zaman

Kapılar **`dima-test` imajında** koşulur (ana makinedeki Python ortamı kapının beklediği
ortam değildir):

```bash
cd /home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic/backend

docker run -d --name kapi1 --network none \
  -v "$PWD:/app" -v "$PWD/../belgeler:/belgeler:ro" \
  -v "$PWD/../dima-frontend-demo-master:/dima-frontend-demo-master:ro" \
  -w /app --user "$(id -u):$(id -g)" -e DIMA_VQR_EMBEDDER=off \
  dima-test python lab/kapi.py --hizli --degisen <dosyalar>

docker wait kapi1 && docker logs kapi1 | grep -E '^FAILED|passed'
docker rm -f kapi1
```

| durum | ne koşulur | süre |
|---|---|---|
| **demet bitti** *(bir kez)* | `--hizli --degisen <demetin TÜM dosyaları>` | ~1-4 dk |
| korpus gerekiyorsa | `--tam` | ~2 dk |
| gecelik CI | `--hepsi` | ~4-6 dk |

🔴 **`--hepsi` yerelde koşulmaz** — yeri gecelik CI'dır.
🔴 **`belgeler` mount'unu düşürme:** yoksa iki yayın kapısı **sessizce atlanır**
(`11 skipped`) ve bu *iyi haber* gibi görünür.
⚠ `--user "$(id -u):$(id -g)"` **zorunlu** — unutulursa konteyner `demo/` altını root
sahipliğine geçirir ve sonraki koşumlar `Permission denied` ile düşer.

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

# 2 · imajı derle
docker build -t dima-backend-temiz:s1 backend/

# 3 · volume'leri yarat (adlar birebir bunlar olmalı)
docker volume create dima-backend-feat-wren-strict-agentic_dima_logs
docker volume create dima-backend-feat-wren-strict-agentic_dima_hf_cache

# 4 · backend'i kaldır
docker run -d --name dima-oneri-8002 -p 8002:8000 --env-file .env \
  -v dima-backend-feat-wren-strict-agentic_dima_logs:/app/logs \
  -v dima-backend-feat-wren-strict-agentic_dima_hf_cache:/tmp/fastembed_cache \
  dima-backend-temiz:s1

# 5 · demo verisini yükle
docker exec dima-oneri-8002 python -m control_plane.cli seed-demo

# 6 · frontend
cd dima-frontend-demo-master && pnpm install && pnpm dev
```

---

## 🔴 `docker-compose` KULLANMA

Bu makinedeki sürüm **1.29.2** ve yeni imaj biçimini okuyamıyor:
`KeyError: 'ContainerConfig'` ile düşüyor — **ve düşerken çalışan konteyneri
durduruyor** (ölçüldü: backend 40 sn kapalı kaldı). Yani `docker-compose up -d`
bir kurtarma değil, bir **kesinti** sebebidir.

⊙ `docker-compose.yml` **silinmedi**: kayıt olarak duruyor ve servislerin şeklini
gösteriyor. Ama ayağa kaldırma yolu yukarıdaki `docker run`'dır.

---

## SORUN GİDERME

| belirti | sebep | çözüm |
|---|---|---|
| Kod değişikliği etkisiz | rebuild yapılmadı | **Durum 1** |
| Doğru sanılan davranış eski çıkıyor | **8001**'e bakılmış (eski imaj `s06`) | `8002`'ye bak |
| Frontend backend'i bulamıyor | `BACKEND_ORIGIN` yanlış | `.env.local` → `http://localhost:8002` |
| `/oneri` uzun süre cevapsız, sonra bağlantı düşüyor | gömme modeli önbelleği yok ya da indeks çok büyük | `…_dima_hf_cache` volume'ü bağlı mı; `docker logs` içinde ısınma satırı var mı |
| `401` alıyorum | token bayatladı | token'ı yeniden al |
| Giriş yapılamıyor | seed yapılmamış | seed komutu |
| Kapı `11 skipped` diyor | `belgeler` mount'u verilmemiş | mount'u ekle |
| `Permission denied` (demo/ altında) | `--user` bayrağı unutulmuş | `chown -R $(id -u):$(id -g) backend/demo` |
| Frontend paketleri tuhaf | `npm install` yapılmış | `rm -rf node_modules && pnpm install` |

---

<sub>⟳ **Denetim notu (2026-08-13):** bu sürüm çalışan sisteme karşı **ölçülerek** yazıldı
(`docker ps` · `docker inspect` · `docker volume ls` · `.env.local` · `backend/Dockerfile` ·
`control_plane/cli.py`). Önceki sürümde **beş** hata vardı ve hepsi bugün doğrulandı:
① tüm komutlar `dima-backend-core` adına gidiyordu — **böyle bir konteyner yok**;
② rebuild reçetesi `docker-compose` kullanıyordu — sürüm **1.29.2**, çalışmıyor ve
çalışan kabı **durduruyor**; ③ backend adresi `8001` yazıyordu — frontend **8002**'ye
konuşuyor; ④ testler ana makinede koşuyormuş gibi yazılmıştı — kapılar `dima-test`
imajında, mount ve `--user` bayrağıyla koşar; ⑤ gömme modeli önbelleği (`dima_hf_cache`)
hiç anılmıyordu, oysa düşerse öneri ucu ilk isteklerde **asılı kalıyor**.
⚠ Anahtarlar bilerek **yazılmadı**: konteyner env'inde duruyorlar, belgeye değil
`.env`'e aittirler.</sub>
