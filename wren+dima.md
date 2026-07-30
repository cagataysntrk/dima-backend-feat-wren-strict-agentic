# WrenAI Kapsamlı Özellik ve Verimlilik Analizi Raporu

Bu rapor, WrenAI'nin (özellikle `wren-core` ve semantik RAG yapısının) sunduğu tüm özellikleri listeler ve DİMA projesinde bu özelliklerin ne kadarının tam verimlilikle kullanıldığını, nerelerde **gereksiz (redundant) kopyalama** yapıldığını detaylandırır.

---

## 1. WrenAI'nin Aslında Sahip Olduğu Tam Yetenek Seti (Full Capabilities)

WrenAI, sadece bir "Veritabanına SQL yazan LLM aracı" değildir. Mimarisi 3 temel direk üzerine kuruludur:

### A. MDL (Modeling Definition Language) Katmanı
MDL, veri tabanı ile yapay zeka arasında bir "Semantik Sözleşme" (Semantic Contract) kurar.
*   **Models & Views:** Veritabanındaki ham tabloları iş mantığına göre sanal modellere dönüştürür.
*   **Relationships (İlişkiler):** Tabloların birbirine nasıl bağlanacağını (Join yollarını) tanımlar.
*   **Metrics & Calculated Fields:** (ÖNEMLİ) Çapraz tablolar arasında çalışan hesaplanmış metrikleri (Örn: Brüt Kar = Toplam Satış - Toplam Maliyet) doğrudan şema seviyesinde tanımlamanızı sağlar.
*   **Macros:** JinJava kullanarak sık tekrarlanan SQL şablonlarını parametrik hale getirir.
*   **Data Governance:** Ajanların hangi tabloları birleştirebileceği, neleri görebileceği kurallara bağlanır.

### B. Wren Engine (wren-core) & Apache DataFusion
Rust tabanlı olan `wren-core`, MDL şemasını okuyan ve onu çalıştıran asıl beyindir.
*   **AST Transpilation:** LLM'den gelen veya MDL'den çıkan SQL'i, bağlandığınız veritabanı türüne (Postgres, BigQuery, Snowflake vb.) çevirir.
*   **Query Optimization:** Apache DataFusion yeteneklerini kullanarak, hantal sorguları parçalar, Time-Intelligence (Dönemsel fonksiyonlar, Window fonksiyonları) ve kompleks Join işlemlerini saniyenin altında planlar (Dry Plan).

### C. RAG, Memory & Semantic Search (Wren AI Ajan Mimarisi)
*   **Vector Search & Schema Retrieval:** Kullanıcının sorusunu alır, vektör embeddings oluşturur ve tüm veritabanı şemasını LLM'e yollamak yerine sadece ilgili tabloları/metrikleri context olarak getirir.
*   **Query History & Memory (Geçmiş Sorgu Hafızası):** Daha önce başarılı şekilde çalışmış "Soru - SQL" eşleşmelerini hafızasında (vektör db) tutar. Yeni bir soru geldiğinde eski soruları RAG (Retrieval-Augmented Generation) mantığıyla Few-Shot örneği olarak LLM'e verir.
*   **Value Profiling:** Boyut (kategorik) kolonlarındaki içerikleri indeksler. Kullanıcı eksik/hatalı bir değer yazsa bile vektör araması ile doğrusunu bulur.

---

## 2. DİMA'daki Durum: Gereksiz Kopyalanan Özellikler (Redundancies)

WrenAI'nin yukarıda sayılan tüm özelliklerine sahip olduğunu göz önüne aldığımızda, DİMA backend'inde yazılmış olan ve şu an aslında **"Tekerleği Yeniden İcat Eden (Reinventing the wheel)"** hantal Python kopyalarını tespit ettim. 

Aşağıdaki 4 modül **tamamen gereksizdir** ve WrenAI tam kapasite kullanılarak silinmelidir:

### ❌ 1. `kpi.py` (Metrik Hesaplama Kopyası)
*   **Ne yapıyor?** Birden fazla ölçüyü birleştirip bir formül (`CCC = DSO + DIO - DPO`) hesaplamak için veritabanına ayrı ayrı SQL'ler atıyor ve sonucu Python RAM'inde matematik kütüphanesiyle hesaplıyor.
*   **Wren Karşılığı:** Wren MDL şemasındaki **Metrics** özelliği.
*   **Değerlendirme:** Tamamen gereksiz. KPI formülleri doğrudan Wren MDL YAML dosyalarına taşınmalı ve hesaplama işi Wren Engine'in üstüne yıkılmalıdır.

### ❌ 2. `yoy.py` (Geçen Yılla Kıyaslama Kopyası)
*   **Ne yapıyor?** Kullanıcı "Geçen yılla kıyasla" dediğinde, Python ile dönemi hesaplayıp veritabanına 2 ayrı sorgu gönderiyor, dönen 2 JSON'u hafızaya alıp For döngüsüyle satır satır birbirine dikiyor (Merge/Join).
*   **Wren Karşılığı:** DataFusion tabanlı Wren Engine, Time-Intelligence ve SQL Join işlemlerini çoktan native olarak yapabiliyor. Hatta bir önceki adımda ajan prompt'u üzerinden bu işi çözdük.
*   **Değerlendirme:** Gereksiz. Ciddi performans kaybı yaratıyor. Silinmelidir.

### ❌ 3. `vqr.py` (Doğrulanmış Sorgu Hafızası)
*   **Ne yapıyor?** Kullanıcıların sorularını alıp, `fastembed` (multilingual-e5-large) ile vektör indekslemesi yapıyor ve PostgreSQL'e kaydediyor. Soru geldiğinde vektör aramasıyla benzer geçmiş soruları bulup LLM'e prompt (Few-shot) olarak ekliyor.
*   **Wren Karşılığı:** WrenAI ajan mimarisinin kalbindeki "Query History & RAG" özelliği tamamen bunun aynısıdır. Wren zaten geçmiş sorguları hafızaya alır ve RAG pipeline'ı ile benzer soruları bağlam olarak çeker.
*   **Değerlendirme:** Sisteme inanılmaz bir vektör arama (fastembed) yükü ve ekstra DB yükü getiriyor. Wren'in native hafızası kullanılmalı ve bu modül çöpe atılmalıdır.

### ❌ 4. `value_index.py` (Kategorik Kelime Düzeltme)
*   **Ne yapıyor?** Kullanıcının yanlış yazdığı kelimeleri (örn: "Efe Dokma") sistemde var olan "Efe Dokuma" ile Levenshtein mesafesi algoritması kullanarak eşleştirmeye çalışıyor.
*   **Wren Karşılığı:** Wren'in "Value Profiling" özelliği kategorik dataları vektörel olarak indeksler ve semantic mapping yapar.
*   **Değerlendirme:** Python üzerinde çalıştırılan bu kelime benzerlik motoru yerine, Wren'in vektörel value search mekanizmasına güvenilmelidir. Silinmelidir.

---

## 3. DİMA'da Kalması Gereken Eşsiz Özellikler (Complementaries)

WrenAI, sonuç olarak **SQL yazan ve Veri getiren** bir platformdur. Kullanıcıya veriyi nasıl göstereceğiniz, veriden nasıl sözel bir özet çıkaracağınız Wren'in umurunda değildir. Bu noktada DİMA backend'inde yazılan 2 modül müthiştir ve kesinlikle **korunmalıdır**:

### ✅ 1. `viz.py` (Algısal Görselleştirme Karar Motoru)
*   Wren veriyi kolon ve satır döner. `viz.py` ise gelen verinin veri tipi ve kardinalitesine (Stevens ölçekleri vb.) bakarak "Buraya Çizgi Grafik uygundur", "Bu veriden Pasta Grafik olmaz" gibi kararları deterministik olarak saniyeler içinde verir. Bu Wren'de yoktur ve DİMA'yı çok premium hissettirir.

### ✅ 2. `interpret.py` (Veri İçgörü ve Sinyal Motoru)
*   Wren'in getirdiği verileri tarayıp, **"Bu ay %15 artış var, dikkat!"** veya **"En çok satış X'ten geldi"** gibi veriyi okuyan ve Türkçe özet çıkaran (LLM kullanmadan, çok hızlı ve KVKK uyumlu) bu yapı Wren'de mevcut değildir. Frontend'in interpretation bar'ını besleyen bu modül paha biçilemezdir.

---

## Sonuç
DİMA Backend, zamanında Wren'in API'ını bir "Black Box" (Siyah kutu) gibi görüp, tüm akıllı işlemleri (Vektör RAG, Kelime düzeltme, Metrik birleştirme, Tarih kıyaslama) kendi üstüne (Python katmanına) alarak **gereksiz kopyalar** yaratmış ve hantallaşmıştır.

Şimdi Wren'in tam kapasitesini anladığımıza göre; `kpi.py`, `yoy.py`, `vqr.py` ve `value_index.py` silinerek sistem **saf, pürüzsüz ve strict agentic** hale getirilmelidir. İş mantığı tamamen Wren MDL içerisine kaydırılmalıdır.


# DİMA Özellik Haritası (Ç1-Ç18) ve WrenAI Maksimum Verimlilik Raporu

Bu rapor, DİMA'nın hedeflenen 18 temel özelliğini (Ç1-Ç18) inceleyerek; hangi özelliklerin doğrudan **WrenAI'nin native (doğal) yetenekleriyle** %100 verimlilikle çözüleceğini, hangilerinde WrenAI'ın yetersiz kalıp **DİMA'nın özel (custom) motorlarına** ihtiyaç duyduğunu detaylandırmaktadır. 

Amaç: Wren'i bir "kara kutu" olarak değil, DİMA'nın kalbi olarak tam kapasite kullanmaktır.

---

## KATEGORİ 1: WrenAI'ın %100 Doğal (Native) Olarak Çözdüğü Özellikler
*Bu özellikler için DİMA backend'inde özel bir Python kodu veya hantal bir yapı yazılmasına **kesinlikle gerek yoktur**. Tüm yük Wren'e (MDL ve Engine) devredilmelidir.*

*   **Ç2 - Anlamlandırma / Semantik Katman:** 
    *   **Nasıl Çözülür?** Tamamen **Wren MDL (Modeling Definition Language)** ile. Metrikler, küpler, boyutlar ve ilişkiler (relationships) Wren'in JSON/YAML şemasında tanımlanır. Wren bu şemayı kullanarak sistemi "anlar".
*   **Ç3 - Türkçe Doğal Dilde Soru Sorma:**
    *   **Nasıl Çözülür?** WrenAI'ın LLM prompt mekanizması (Semantic RAG) zaten gelen soruyu MDL bağlamına (context) oturtarak SQL üretir.
*   **Ç4 - Deterministik Metrik Cevabı (Altın Yol):**
    *   **Nasıl Çözülür?** (Önceki `kpi.py` kopyasını sileceğimiz yer). Wren MDL içerisinde tanımlanan `Metrics` ve `Calculated Fields`, yapay zeka halüsinasyonu olmadan, %100 deterministik ve kesin SQL kurallarıyla çalışır.
*   **Ç10 - Kanıt Zinciri (Kaynak, Sorgu, Formül):**
    *   **Nasıl Çözülür?** WrenAI'ın `wren_dry_plan` ve `wren_fetch_context` API'leri, oluşturulan SQL'i, kullanılan tabloları ve şemayı metadata olarak geri döner. UI bu metadatayı kullanarak kanıt zincirini çizer.
*   **Ç17 - Veri Egemenliği ve AI-Kapalı Mod:**
    *   **Nasıl Çözülür?** Wren-Core (Rust motoru) LLM'den bağımsız çalışabilir. UI'dan gönderilen deterministik JSON (MDL) filtreleri, AI kapalıyken bile DataFusion üzerinden SQL'e dönüştürülüp veri getirebilir.
*   **Ç18 - Çok Kullanıcılı Yetki (RLS/CLS):**
    *   **Nasıl Çözülür?** WrenAI doğal olarak **Row-Level Security (RLS)** ve **Column-Level Security (CLS)** destekler. DİMA backend'i kullanıcının oturum bilgilerini (`tenant_id`, `org_id`) Wren engine'e session property olarak geçirir, Wren üretilen SQL'in sonuna güvenli WHERE filtrelerini otomatik ekler (Zero-trust architecture).

---

## KATEGORİ 2: WrenAI'ın Alt Yapı Sağladığı, UI'ın Tamamladığı Özellikler
*Wren veriyi ve kurguyu hazırlar, ancak son kullanıcıya sunum kısmı Frontend (UI) tarafında gerçekleşir.*

*   **Ç1 - Çoklu Veri Kaynağı Bağlama:**
    *   **Nasıl Çözülür?** WrenAI doğrudan Postgres, BigQuery vb. bağlanır. Ancak Excel/Dosya yüklemeleri için DİMA backend'i DuckDB aracılığıyla veriyi alıp Wren'in MDL'ine sanal model olarak kaydetmelidir.
*   **Ç5 - Otomatik Grafik Üretimi:**
    *   **Nasıl Çözülür?** Wren SADECE SQL ve veri döner. Hangi grafiğin çizileceğine DİMA'nın eşsiz **`viz.py`** motoru karar vermelidir (DİMA Backend gerektirir).
*   **Ç8 - Rapor Üretimi (Excel/PDF) & Ç16 - Dışa Aktarım:**
    *   **Nasıl Çözülür?** Wren ham veriyi JSON/Arrow döner. Backend veya Frontend kütüphaneleri bunu PDF'e veya CSV'ye çevirir.
*   **Ç9 - Pano Üretimi ve Kalıcılığı (Dashboarding):**
    *   **Nasıl Çözülür?** Wren'in ürettiği "Verified SQL" (Doğrulanmış Sorgu) veritabanında saklanır. Pano açıldığında bu SQL tekrar Wren Engine üzerinden (LLM'e gitmeden) çalıştırılarak anlık veri çekilir.

---

## KATEGORİ 3: WrenAI'ın Yetersiz Kaldığı & DİMA'nın Kendi Zekasını Kattığı Özellikler
*WrenAI sadece bir veri/SQL motorudur. Aşağıdaki özellikler Wren'in sınırlarını aşar ve DİMA'nın şu anki eşsiz Python zekasına (Örn: K2, K3 sistemleri) muhtaçtır.*

*   **Ç6 - Zorunlu İçgörü Yorumu:**
    *   **Durum:** Wren veriyi getirir ama "Satışlar düştü, sebebi şu olabilir" demez. 
    *   **DİMA Çözümü:** `interpret.py` (Mevcut DİMA kodu). Wren'den gelen veriyi istatistiksel olarak analiz edip deterministik Türkçe içgörüler üreten bu kod **kesinlikle korunmalıdır**.
*   **Ç7 - Tıklanabilir Öneri Zinciri (Guided Analytics):**
    *   **Durum:** Derinleşme ve drill-down mantığı.
    *   **DİMA Çözümü:** Wren'in döndüğü boyutlar `viz.py` üzerinden geçirilerek "Kategoriye göre kır" gibi akıllı Chip'ler DİMA Backend tarafından üretilir.
*   **Ç11 - Dürüst Red:**
    *   **Durum:** Wren bağlamı bulamazsa SQL üretemez ancak kullanıcıya mantıklı bir açıklama yapması DİMA'nın Promting yeteneğine bağlıdır. DİMA'nın System Prompt'unda bu kural katı olarak belirtilmelidir.
*   **Ç12 - Kalibre Edilmiş Güven Rozeti:**
    *   **Durum:** LLM'e güvenmek yerine, üretilen SQL'in Wren Dry Plan'den sorunsuz geçmesi ve VQR (Geçmiş doğrulanmış hafıza) skoruyla matematiksel olarak hesaplanan bir sistem. (Şu an kaldırıldı, ancak geri istenirse DİMA'nın kendi skorlama algoritması kullanılmalıdır).
*   **Ç13 - Kök-Neden Analizi (Root-cause):**
    *   **Durum:** "Neden düştü?" sorusuna % katkılarla (waterfall) cevap vermek Wren'in tek bir SQL ile yapabileceği bir şey değildir.
    *   **DİMA Çözümü:** DİMA backend'inde özel bir "Driver Analysis" (Sürücü analizi) algoritması çalışmalı, Wren'den birden fazla boyut kırılımı (Drill-down SQL) isteyerek varyans analizi yapmalıdır.
*   **Ç14 - Tahmin ve Senaryo (What-if):**
    *   **Durum:** Wren makine öğrenmesi tahmini yapmaz.
    *   **DİMA Çözümü:** Wren'den tarihi veri çekilip, Python (Statsmodels/Prophet) ile backend'de forecast edilmelidir.
*   **Ç15 - Karar Motoru (Decision Engine):**
    *   **Durum:** Kriter ağırlıklandırma (MCDA). Tamamen DİMA'ya özel, literatür ötesi bir iş mantığıdır. Wren sadece matrisi besleyen sayıları getiren bir araç (driver) olarak konumlandırılır.

---

## ÖZET AKSİYON LİSTESİ (DİMA'yı Maksimum Verimliliğe Taşıma)

1.  **DİMA'daki Wren Kopyalarını Sil (Redundant):** `kpi.py`, `yoy.py`, `vqr.py` ve `value_index.py` silinerek tüm metrik, dönemsel kıyaslama, RAG vektör hafızası ve kelime düzeltme yükü Wren'e (MDL ve AI) bırakılacak.
2.  **RLS Katmanını Bağla:** Çok oyunculu (Multi-tenant) yapı için Wren Engine'e `tenant_id` session parametresini entegre et (Ç18).
3.  **DİMA Zekasını Koru:** `viz.py` ve `interpret.py` (Ç5, Ç6) gibi sunum/analiz algoritmalarını Wren'in üzerine taç olarak oturt.
4.  **Kök Neden & Tahmin (Ç13, Ç14):** Wren'in getirdiği ham veri üzerinden çalışacak yeni, izole Python analiz pipeline'ları (Driver Analysis) kur.
