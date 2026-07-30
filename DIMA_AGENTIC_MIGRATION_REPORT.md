# DİMA Backend - Pür Agentic (Wren SQL) Mevcut Durum Raporu

**Tarih:** 30 Temmuz 2026
**Konu:** Eski hibrit "Cortex/Gold Trust" sisteminden tamamen arındırılmış saf Agentic Wren altyapısına geçişte şu ana kadar yapılan işlemlerin özeti ve sistemin mevcut çalışma senaryosudur.

---

## 1. Şu Ana Kadar Hangi Dosyada Ne Yapıldı?

# DİMA Backend - Strict Agentic (Wren SQL) Migration Report

**Tarih:** 30 Temmuz 2026
**Konu:** Hibrit (NLP tabanlı `cube_router`) sistemden, Wren SQL merkezli Doğrudan (Strict) Agentic sisteme geçişin cerrahi raporudur.

## 1. Mimari Değişiklik (Nedeni ve Hedefi)
Eski sistemde, LLM'e kullanıcı isteği gönderiliyor ve LLM'den bir **CubeQuery (AST)** JSON'u dönmesi bekleniyordu. Bu yapı, hem doğruluk payını düşürüyor hem de gereksiz bir hibrit NLP karmaşasına yol açıyordu. 
Yeni "Strict Agentic" yapıda bu mantık tamamen söküldü. Ajan artık bir aracı (AST) üretmek yerine, doğrudan **Semantic Model (MDL)** şemasını okuyarak saf **Wren SQL** üretiyor.

## 2. Yapılan Temel İşlemler

### A. Klasör Yapısı ve Temizlik
- Eski backend kodlarının bulunduğu `legacy/dima-backend-*` klasörü tamamen kök dizindeki `backend` dizinine taşındı.
- Eski mimariyi anlatan markdown belgeleri (roadmap, mimari-akis vb.) dışında, `legacy` klasöründe hiçbir kod veya sistem dosyası bırakılmadı. Tam temizlik sağlandı.
- Eski `cube_router` NLP bağımlılıklarının tamamı temizlendi.

### B. `app/routers/ask.py` Cerrahi Operasyonu
- 1800 satırlık devasa ve karmaşık `cube_router` tahmin mekanizması tamamen kaldırıldı.
- Yerine 6 adımdan oluşan (Strict Agent) yeni akış entegre edildi:
  1. `service.schema()` üzerinden sistemin Metadata/Cube yapısı (MDL) çekildi.
  2. Doğrudan OpenAI/OpenRouter (LLM) kullanılarak `wren_sql` üretimi sağlandı.
  3. Üretilen SQL, Wren motorunda `dry_plan` üzerinden doğrulandı.
  4. Eğer hata alınırsa LLM'e hatayı vererek SQL'i kendi kendine onarma (Self-Healing) mekanizması kuruldu.
  5. Başarılı SQL, çalıştırılıp sonucu (`rows`, `columns`) alındı.
  6. Başarılı sorgu için `SHA-256` ile **GOLD_TRUST_BADGE** sertifikası mühürlendi.

### C. Şema (API Sözleşmesi) Güncellemeleri
- `AskResponse` Pydantic şemasına, yeni frontend'in (DIMAInsightCard) beklentilerine uygun olarak şu alanlar eklendi:
  - `badge="GOLD_TRUST_BADGE"`
  - `proof={"executed_wren_sql": "...", "query_contract_hash": "..."}`
  - `data=[...]` (Wren motorundan dönen ham satırlar)
  - `suggested_follow_up_questions=[...]`

### D. Altyapı ve Bağımlılık (DevOps) İyileştirmeleri
- **Bağımlılıklar:** `backend/pyproject.toml` ve `backend/Dockerfile` içerisine yeni Ajanın çalışması için şart olan `openai` ve `wrenai` kütüphaneleri eklendi.
- **Port Çakışması:** Sunucudaki `trendyol_backend` ile yaşanacak muhtemel 8000 port çakışması tespit edilip `dima-backend` container'ı **8001** portuna taşındı.
- **Frontend Uyumu:** Frontend klasöründeki (`dima-frontend-demo-master/.env.local`) ortam değişkenleri `BACKEND_ORIGIN=http://localhost:8001` olarak güncellendi ve frontend'in yeni akıllı backend'i otomatik görmesi sağlandı.

## 3. Sistemin Mevcut Durumu ve Kurulum
Şu an sistem eski yeteneklerini (Kullanıcı Oturumları, Admin Paneli, Çoklu Tenant, Dashboard Widget'ları) **tamamen koruyarak**, çok daha kararlı ve doğrulanabilir bir dil motoruna sahip olmuştur.

Yeni demo veritabanını oluşturmak için container çalıştıktan sonra aşağıdaki komutun çalıştırılması yeterlidir:
```bash
docker exec -it dima-backend-core python -m control_plane.cli seed-demo
```


Eski sistemdeki karmaşık kriptografik kanıt ("Gold Trust Badge") ve kullanılmayan bilişsel ("Cortex") veri katmanları sistemden sökülerek arayüz ve backend hafifletildi.

*   **`backend/app/schemas.py` (API Sözleşmesi Temizliği):**
    *   `AskResponse` modelindeki gereksiz `badge`, `proof`, `data`, `suggested_follow_up_questions` alanları silindi.
    *   Sistem artık dışarıya sadece saf `question`, `sql`, `planned_sql` ve `result` (Wren verisi) dönüyor.
*   **`backend/app/routers/ask.py` (Backend Router Temizliği):**
    *   Kriptografik doğrulama yapan `DIMAQueryContract` sınıfı ve SHA-256 mühürleme algoritmaları tamamen silindi.
    *   Yeni `ask()` endpointi, OpenAI API anahtarını statik değil *dinamik* olarak çevre değişkenlerinden (`DIMA_OPENROUTER_API_KEY`) okuyacak şekilde yeniden yapılandırıldı (Global scope hatasını önlemek için).
    *   Yanıt oluşturulurken artık sadece saf `wren_sql` ve Wren'in ürettiği sonuçlar (`QueryResult`) kullanılıyor.
*   **`dima-frontend-demo-master/src/components/ReportPanel.tsx` (Arayüz Temizliği):**
    *   UI'da "Gold Trust Badge" göstermek için kullanılan `DIMAInsightCard` komponenti ve bağımlılıkları tamamen silindi.
    *   Sonuçların arayüzde standart, temiz bir formatta (fazla metadata yığını olmadan) renderlanması sağlandı.
*   **DevOps / Hata Giderimi:**
    *   Backend `wren-engine` iletişimindeki timeout'ları ve 500 hatalarını çözmek için container'lar doğru port eşleşmeleriyle yeniden başlatıldı.

---

## 2. Sistem Şu An Nasıl Çalışıyor? (Uçtan Uca Prompt Senaryosu)

Şu anda mevcut olan yeni mimaride bir kullanıcı prompt girdiğinde, sistem arkada şu mükemmel zincirle çalışmaktadır:

**Senaryo:** Kullanıcı chat ekranına *"Bana son 3 ayın en çok satan 5 müşterisini getir"* yazar.

1.  **İsteğin Karşılanması (Frontend -> Proxy -> Backend):**
    *   Frontend bu metni `/api/ask` üzerinden Next.js'e gönderir. Next.js bu isteği yakalar ve arkadaki FastAPI sunucusunun (Port 8001) `POST /ask` endpoint'ine iletir.
2.  **LLM'in Devreye Girmesi (SQL Üretimi):**
    *   Backend, kullanıcının şirket/tenant bilgilerine göre ilgili Wren (MDL) şemasını çeker.
    *   `call_llm_for_wren_sql()` fonksiyonu tetiklenir. Ajan (LLM), sistemdeki tabloları, boyutları ve ölçüleri içeren prompt'u ve kullanıcının sorusunu okuyarak saf bir **Wren SQL** kodu yazar.
3.  **Wren Engine Üzerinden Doğrulama (Dry Plan):**
    *   Üretilen SQL doğrudan veritabanına gönderilmez. Önce `service.dry_plan(wren_sql)` ile Wren Engine Semantic Layer'ından geçirilir. Burada tablonun veya ilişkilerin doğruluğu test edilir.
4.  **Kendi Kendini Onarma (Self-Healing) - Eğer Hata Varsa:**
    *   Eğer Wren Engine *"Böyle bir kolon yok"* gibi bir hata verirse (Exception), backend çökmez!
    *   Sistem `fix_llm_sql()` fonksiyonunu devreye sokar. LLM'e *"Sen bu SQL'i yazdın ama Wren şu hatayı verdi, bunu düzelt"* diyerek SQL'i kendi kendine düzelttirir.
5.  **Verinin Çekilmesi (Execution):**
    *   Doğrulanan (veya düzeltilen) kusursuz SQL, `service.query(wren_sql)` ile çalıştırılır ve veritabanından saf tabular veri (`rows`, `columns`) döner.
6.  **Kalıcı Loglama ve Dönüş:**
    *   Backend, bu başarılı işlemi (`_log_interaction` ve `_persist_message`) aracılığıyla sisteme kaydeder (geçmiş sohbetlerde görünmesi için).
    *   En son olarak, tertemiz oluşturulmuş `AskResponse` JSON'u frontend'e gönderilir.
7.  **Sonuç (UI Rendering):**
    *   Frontend, karmaşık badge ve kural katmanlarıyla uğraşmadan, dönen veriyi doğrudan ekranda tablo veya grafik olarak mükemmelce çizer.

---

## 3. Henüz Uygulanmayan Temizlik (Planımızdaki Kısım)
Yukarıdaki kusursuz akış `/ask` endpoint'i üzerinden çalışmasına rağmen, `ask.py` dosyasının içerisinde ve projede hala **eski kural bazlı sistemi (`cube_router.py`) tetikleyen `/cube`, `/report` gibi kullanımdan kalkan yan yollar** bulunmaktadır. 
*Onayladığın plan, sisteme zarar vermeden işte bu kalabalığı kökünden sökmeyi hedeflemektedir.*
 plan şöyle: ancak karar verilmedi***
 # DİMA Strict Agentic Architecture Transition Plan (Güncellenmiş)

Önceki plandaki geribildirimini anladım. Diğer özellikler (viz, KPI, YoY, vs.) Wren'den bağımsız ve korunması gereken ayrı ürün yetenekleri. Sistemdeki asıl "karıştırıcı" ve eski "Hibrit" yapının kalıntısı olan kısım sadece `cube_router.py` ve onun deterministik kural motoru.

Amacımız: Sistemi saf (strict) Wren Core ile çalışacak şekilde ayarlarken, `cube_router`'ın kelime bazlı, kendi kendine karar vermeye çalışan araya girme mantığını sistemden tamamen sökmek.

## 🗑️ Faz 1: `cube_router.py`'nin Sistemden Sökülmesi
`cube_router.py` içerisindeki regex bazlı tahminleme, deterministik eşleştirme ve LLM'i bypass etme mantığı tamamen kaldırılacak.
- `backend/app/cube_router.py` dosyası projeden silinecek.

## 🧨 Faz 2: `ask.py` İçerisindeki Bağımlılıkların Temizlenmesi
`cube_router` silindiğinde `ask.py` içindeki diğer uç noktalar (`/cube`, `/report`, `/verify` vb.) ve `ask.py` içindeki eski `ask` mantığı (varsa) hata verecektir.
- Eski "heuristic" (kural bazlı) `ask` akışı (eğer hala bir yerlerde tetikleniyorsa) tamamen devre dışı bırakılıp, sadece bizim yazdığımız saf `call_llm_for_wren_sql` akışı kullanılacak.
- `/cube`, `/report`, `/verify` gibi endpoint'lerin `cube_router.parse_cube_query` veya `cube_router.suggest_next_steps` gibi fonksiyonlara olan bağımlılıkları temizlenecek. Bu uç noktaların Wren üzerinden veya doğrudan bağımsız şekilde çalışması sağlanacak.
- `ask.py` içinde `cube_router` import eden her yer temizlenecek ve refaktör edilecek.

## 🛡️ Faz 3: Diğer Özelliklerin Korunması (Dokunulmayacaklar)
Aşağıdaki modüller ve şemalar sistemin bir parçası olarak **aynen korunacaktır**:
- `viz.py`, `yoy.py` vb. özellik modülleri.
- Frontend'in kullandığı grafik (viz), kpi, interpretation gibi yanıt modelleri ve şemaları (`AskResponse` içindeki bu alanlar kalacak).
- Yükleme (`/ask/upload`) ve raporlama mekanizmaları (yalnızca `cube_router` bağımlılıkları çözülerek çalışır durumda tutulacak).

---

**Nasıl İlerleyelim?**
Planı sadece `cube_router`'ı yok etme ve `ask.py`'yi bu bağımlılıktan kurtarma üzerine güncelledim. Başka bir eklenti veya düzeltme yoksa, onayladığın an işlemlere (Faz 1 ve Faz 2) başlayabilirim.
