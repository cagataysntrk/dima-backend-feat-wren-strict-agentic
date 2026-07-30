# DİMA Server Başlatma ve Yönetim Komutları

Bu belge, DİMA Agentic projesinde (WrenAI entegreli yeni mimari) geliştirme yaparken backend (sunucu) ve frontend (arayüz) projelerini nasıl başlatacağınızı, yeniden başlatacağınızı ve logları nasıl izleyeceğinizi özetler.

---

## 1. Backend (FastAPI + Wren Engine) Yönetimi

`docker-compose.yml` dosyamızda `backend` klasörü için bir `volume` (canlı senkronizasyon) **tanımlı olmadığı için**, Python kodlarında (örneğin `ask.py` veya `interpret.py`) değişiklik yaptığınızda, Docker imajını **yeniden inşa etmeniz (rebuild)** gerekir. Aksi halde eski kod çalışmaya devam eder.

Aşağıdaki komutları ana proje dizinindeyken (`/home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic`) çalıştırın.

### A. Kodu Değiştirdikten Sonra Yeniden Başlatma (Tam Rebuild)
Kodda bir değişiklik yaptıktan sonra yeni kodun aktif olması için aşağıdaki komutu **tek seferde** kopyalayıp yapıştırın. Bu komut, eski konteyneri silip yenisini taze kodla ayağa kaldırır:

```bash
export DOCKER_BUILDKIT=0 && export COMPOSE_DOCKER_CLI_BUILD=0 && \
docker-compose build dima-backend && \
docker rm -f dima-backend-core && \
docker-compose up -d dima-backend
```

### B. Yeniden Başlatma Sonrası Demo Veritabanını Doldurma (Seed)
Tam rebuild işlemi yaptığınızda ve konteyneri sildiğinizde, içerideki SQLite (veya DuckDB) demo veritabanı sıfırlanabilir. API'ye giriş yapabilmek ve testleri çalıştırabilmek için **her rebuild sonrasında** şu komutla veritabanını doldurun:

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

## 2. Frontend (React / Vite) Yönetimi

Frontend projesi `dima-frontend-demo-master` klasöründedir ve canlı kod güncellemelerini destekler (Hot-Reload). Arayüz kodlarında değişiklik yaptığınızda yeniden başlatmanıza gerek yoktur, tarayıcı otomatik güncellenir.

### Frontend'i Başlatmak İçin:
Terminalinizde yeni bir sekme açın ve şu komutları çalıştırın:

```bash
cd dima-frontend-demo-master
npm install  # (Sadece ilk kurulumda veya paket eklendiğinde gerekir)
npm run dev
```

Eğer `npm run dev` komutunda hata alırsanız veya proje eski Vite/Next versiyonu kullanıyorsa, `npm start` komutunu da deneyebilirsiniz.

---

## 3. Test Komutları

Agentic mimarinin çalışıp çalışmadığını, LLM (Yapay zeka) yanıtlarını doğrudan test etmek için hızlı test betiğimizi kullanabilirsiniz.

Ana dizinde:
```bash
python3 test_auth.py
```
Bu script, backend'e giriş yapar (login), ardından `/ask` endpoint'ine bir soru gönderir ve dönen JSON yanıtını (grafik tipi, sql, kanıt zinciri vs.) ekrana yazdırır.
