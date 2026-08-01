> ⚠️ **TARİHSEL KAYIT — NORMATİF DEĞİLDİR.** Bu belge yazıldığı andaki durumu ve o turda alınan
> kararları anlatır. Mimari otorite `backend/MIMARI.md`'dir; çelişkide o kazanır.
> Özellikle: bu belgelerdeki JOIN/derleyici teşhisleri `MIMARI.md §3.2`'de **düzeltilmiştir**.

# Dima — Faz 4 Tamamlama Raporu (1 Ağustos 2026)

Bu belge `HANDOFF_2026-07-31.md`'nin (commit `8fb3a1f`'e kadar olan durumun devir raporu)
ÜSTÜNE, o tarihten sonra planlanıp bu oturumda uygulanan **Faz 4 — GenBI Temelleri
Sağlamlaştırma**'nın TAMAMINI belgeler. Kaynak plan dosyası:
`~/.claude/plans/genel-projeyi-anla-u-nifty-charm.md` (plan modunda üretildi, kullanıcı
onayladı) — bu raporu okuyan bir sonraki geliştirici plan dosyasını da okumalı, buradaki her
madde o planın ilgili bölümüne karşılık gelir.

**Okuma sırası önerisi**: (1) bu belgenin §1 özet tablosu, (2) ilgilendiğiniz maddenin
detay bölümü (§2), (3) §3 "doğrulama turunda bulunup düzeltilen eksikler" (kritik —
ilk uygulama turunun ÜSTÜN KÖRÜ bıraktığı noktalar burada), (4) §4 UC eşleme tablosu,
(5) §5 test durumu, (6) §6 bilinen sınırlar, (7) §7 — AYNI GÜN İKİNCİ bir turda P0/P1/P2
kalemlerinin GERÇEK UYGULAMASI (bu turda §6'daki sınırların çoğu KAPANDI). Gelecek iş
önerileri AYRI bir dosyada: `FAZ4-SONRASI-ONERILER_2026-08-01.md` (o dosya bu ikinci
turun sonuçlarıyla da güncellendi).

---

## §1 — Özet tablo

| # | Konu | Durum | Ana dosyalar |
|---|---|---|---|
| 4.1 | Hafif async iş kuyruğu (Discovery) | ✅ Tamamlandı | `control_plane/models.py:530` (`AskJob`), `app/routers/ask.py:1034` (`_queue_discovery_job`), `app/routers/ask.py:1124` (`ask`) |
| 4.2 | Router telemetrisi + model-sınıfı seçimi | ✅ Tamamlandı | `app/llm.py:249,309` (`select_model`), `app/config.py` (`*_select_model`) |
| 4.3 | Excel/CSV akışı | ✅ Kasıtlı NO-OP (kullanıcı kararı) | — (değişiklik yok) |
| 4.4 | `_viz_hint` ölü kodu bağlama | ✅ Tamamlandı | `app/routers/ask.py:326,338,1359` |
| 4.5 | DB bağlama sihirbazı + zengin MDL | ✅ Tamamlandı (+ bu turda düzeltme) | `app/db_introspect.py`, `app/routers/connections.py`, `app/mdl_writer.py` |
| 4.6 | Plane Enforcer / göz-ikonu kolon gizleme | ⏸ Ertelendi (kullanıcı kararı) | — (kod yok) |
| 4.7a | Metrik tuzakları araştırması (fan-out + mali takvim) | ✅ Tamamlandı (bu turda İKİNCİ bacak kapatıldı) | `tests/test_view_fanout_guard.py` |
| 4.7b | Minimal düzeltme | ✅ Tamamlandı (yalnız regresyon testi — kod DEĞİŞMEDİ) | `tests/test_view_fanout_guard.py` |
| 4.8 | "Ne sorabilirim?" departman gezinmesi | ✅ Tamamlandı | `app/starters.py:28`, `HelpPanel.tsx` |
| 4.9 | Grafik interaktivitesi | ⏭ Atlandı (kullanıcı kararı) | — (kod yok) |
| 4.10 | Dallı kök-neden analizi | ✅ Tamamlandı (+ bu turda kanıt-paneli düzeltmesi) | `app/drill.py`, `app/schemas.py:322,382`, `app/routers/ask.py:2138`, `DrillDownPanel.tsx` |
| 4.11 | Analiz Tuvali | ✅ Tamamlandı (bu oturumda uygulandı) | `page.tsx` (canvasMode/canvasItems), `AnalysisCanvas.tsx` |
| 4.12 | Canlı düşünme-adımları | ✅ Tamamlandı | `control_plane/models.py:175,558` (`trace_json`), `api-client.ts::pollAskJob` |
| 4.13 | Güven rozeti + meta-güven şeridi | ✅ Tamamlandı | `app/routers/ask.py:84` (`_build_explain`), `ChatPanel.tsx` (`confidenceBadge`), `app/routers/stats.py`, `HelpPanel.tsx` |
| 4.14 | PII maskeleme | ✅ Tamamlandı | `app/pii.py`, `app/routers/ask.py:840-843`, `app/routers/query.py:48-52` |

---

## §2 — Madde detayları

### 4.1 — Hafif async iş kuyruğu
`AskJob` (SQLModel tablosu, `control_plane/models.py:530`) `CloneJob` deseninin AYNISI
(status/progress/result/error alanları). `app/routers/ask.py:1034`'teki
`_queue_discovery_job` yalnız `ask_async_discovery` bayrağı açıkken (varsayılan KAPALI —
`demo/packs/features.yml`'e BİLEREK eklenmedi, mevcut tüm tenant/testler ETKİLENMEZ)
Discovery yolunu `threading.Thread` ile arka plana alır; frontend `api-client.ts::ask()`
`job_id` dönerse `GET /ask/jobs/{id}`'i polling ile (max 240 deneme, ~6 dk) takip eder —
WebSocket YOK, bilinçli tercih (bkz. plan §4.1 gerekçesi).
**Test**: `tests/test_ask_async_discovery.py` (bayrak açık/kapalıyken davranış farkı,
job kalıcılığı, arayüzün donmadığı — senkron/async iki yol da test edilir).

### 4.2 — Router telemetrisi + model-sınıfı
`app/llm.py`'deki her sağlayıcı sınıfı artık `select_model` parametresi alır
(`AnthropicSqlGenerator.__init__:249`, `OpenAICompatibleSqlGenerator.__init__:309`) —
"cube seçimi" (basit sınıflandırma) İÇİN ayrı, ucuz bir model; "SQL üretimi" (Discovery,
karmaşık) için ANA model. Bu, soru karmaşıklığına göre OTOMATİK bir model-sınıfı ayrımıdır
(hangi ADIM çalıştığına göre gate'lenir — yeni bir "tier" kavramı icat edilmedi, plan'ın
istediği gibi mevcut `DIMA_LLM_PROVIDER` seçimi kullanılır). **Test**: `tests/test_llm_
select_model.py`.

### 4.4 — `_viz_hint` ölü kodun bağlanması
`_VIZ_MAP`/`_viz_hint()` (`app/routers/ask.py:326,338`) TANIMLIYDI ama HİÇ ÇAĞRILMIYORDU
(ölü kod). `ask()` akışına `app/routers/ask.py:1364` civarında bağlandı — kullanıcı "pasta
grafik olarak göster" derse `view_hint` buna göre set edilir, mevcut `detect_facet()` ile
ÇAKIŞMAZ (biri panel-görünümü, diğeri grafik-TİPİ niyeti, tamamlayıcı). **Test**:
`tests/test_ask_golden.py::test_...pasta_grafik_...` (satır ~503-507).

### 4.5 — DB bağlama sihirbazı + zengin MDL
`app/db_introspect.py`: `introspect_schema()` (satır 112) SQLAlchemy `inspect()` ile
GERÇEK FK'leri okur (tahmin değil); `classify_column()` (149) sayısal→ölçü/kategorik-
tarih→boyut sınıflandırır; `draft_mdl()` (162) taslak cube+relationships üretir.
`app/routers/connections.py`: tenant-plane, `require_company` korumalı — `/connections`
(dry-run+create, fail-closed: dry-run başarısızsa sır DB'ye YAZILMAZ), `/connections/{id}/
draft` (taslak MDL önizleme), `/connections/{id}/confirm` (onaylanan taslak `app/mdl_
writer.py::write_introspected_schema` ile GERÇEK cube YAML'ına yazılır — var olan bir
cube/model dosyasının üzerine ASLA yazılmaz). Frontend: `ConnectionReviewPanel.tsx`,
Ayarlar drawer'ında "Veri Kaynağı Bağla" sekmesi (`page.tsx` `settingsTab`).
**Kapsam**: yalnız Postgres (MySQL sürücüsü bu ortamda kurulu değil — bilinçli, belgeli
erteleme, bkz. `app/db_introspect.py` modül docstring'i).
**Bu turda DÜZELTİLDİ** (bkz. §3.2): bağlantı hata mesajları artık Türkçe+eyleme-
geçirilebilir, ham sürücü metni sızdırmıyor; ≥5-ölçü kabul kriteri somut bir testle
kanıtlandı.

### 4.7 — Metrik tuzakları araştırması
`tests/test_view_fanout_guard.py` modül docstring'i İKİ ayrı araştırma bacağını belgeler:
(a) **fan-out** — `parti_zengin` view'ının `personel.ad_soyad` üzerinden LEFT JOIN'i somut
bir risk (benzersizliği garanti edilmeyen alan); düzeltme: `test_no_view_fans_out_
relative_to_its_base_table` — HER view'ın satır sayısının kendi temel tablosunu aşmadığını
doğrulayan bir regresyon kilidi (mevcut `dry_plan`/derleme mekanizması DEĞİŞTİRİLMEDİ).
(b) **mali takvim/kur** (UC-1.15) — **bu turda TAMAMLANDI**: `TenantConfig`'te böyle bir
alan yok, `cube_router.py`'nin "geçen ay/yıl" çözümleyicisi HER ZAMAN takvim yılı kullanıyor,
hiçbir demo/lab tenant'ı (gulteks/demo-boyahane/gitas/atiksan) takvim-dışı bir mali yıl
BEYAN ETMİYOR — ihtiyaç bugün TAMAMEN VARSAYIMSAL, bu yüzden `MetricDefinition`/mali-takvim
altyapısı BİLEREK kurulmadı.

### 4.8 — Departman gezinmesi
`app/starters.py:28` (`starter_questions`) her starter'a opsiyonel `grup` (departman)
etiketi ekleyebiliyor; `HelpPanel.tsx` bunu sekme/grup gezinmesi olarak gösteriyor
(etiketsiz starter'lar geriye-uyumlu, gruplanmamış listede kalıyor). **Test**: `tests/
test_starters_departments.py`.

### 4.10 — Dallı kök-neden analizi (EN KAPSAMLI madde)
`app/drill.py` — iki katmanlı tasarım: SAF yorumlama fonksiyonları (`formula_explanation`
:38, `flag_outliers`:85 — z-skor, k=2.0, ≥4 kategori, **`app/schedules.py::detect_
anomalies` İLE AYNI yöntem**, yeni bir istatistik motoru YOK, `available_dimensions`:124,
`related_cubes`:137) + durum-geçiş/SQL fonksiyonları (`expand_cube_query`:163, `select_
cube_query`:175, `jump_to_related_cube`:188, `sql_literal`:216, `build_raw_row_sql`:228 —
`_SAFE_IDENT_RE` ile identifier doğrulama + tırnak escape, `UnsafeDrillError`:33).

`POST /ask/drill` (`app/routers/ask.py:2138`) action-tabanlı motor: `explain` (yeni sorgu
ÇALIŞTIRMAZ, mevcut sonucu yorumlar) / `expand` / `select` / `related` / `raw` (HER BİRİ
GERÇEK bir sorgu çalıştırır: `service.cube_sql`→`dry_plan`→`query`, KENDİ Query Contract
kaydını üretir — `_drill_record_contract`, `source="drill"`). `expand`/`select` cube'un
TÜM ölçülerini birlikte döner (`_with_all_measures`) — kullanıcının "hesabı oluşturan tüm
ilişkiyi görme" talebinin doğrudan karşılığı. `WrenService.schema()`'ya `base_object`
eklendi (raw-row sorguları için kritik bir eksikti, bu oturumda bulunup düzeltildi).

`DrillDownPanel.tsx` — breadcrumb'lı, tıkla-dallan modal: formül açıklaması, anomali-
vurgulu kırılım tablosu (▼/▲, kırmızı/yeşil satır), "buna göre kır" çipleri, "ilişkili
veri" çipleri (cross-cube kök-neden — ör. OEE→makine_duruslari), ham-satır açığa çıkarma.

**Bu turda EKLENEN kanıt paneli düzeltmesi** (bkz. §3.1) ve **UX sertleştirmesi** (bkz.
§3.3): SQL+süre gösterimi, Esc-ile-kapatma, çifte-tıklama yarış koruması.

**Kapsam sınırı (bilinçli)**: Discovery/ham-SQL kaynaklı sonuçlarda (`cube_query` yok)
dallanma SUNULMAZ, yalnız dürüst bir mesaj + üretilen SQL gösterilir — asla sahte dallanma
uydurulmaz (`app/routers/ask.py:2175-2180`, test: `test_drill_explain_on_discovery_
result_is_honest_no_fake_branching`).

**Test kapsamı**: `tests/test_drill.py` (34→35 birim testi, SQL-injection güvenliği dahil),
`tests/test_ask_drill_integration.py` (uçtan uca zincir: makine→en-düşük-OEE-seç→vardiya
kır→vardiya seç→makine_duruslari'na GEÇ→neden kır→ham satırlar; + bu turda eklenen `test_
drill_steps_expose_running_sql_and_duration_for_evidence_panel` — döndürülen SQL'in
`/query`'ye AYNEN gönderilince AYNI veriyi ürettiğini birebir kanıtlar, UC-2.19'un
literal karşılığı).

### 4.11 — Analiz Tuvali (bu oturumda UYGULANDI)
Plan bunu "ayrı, dikkatli tasarlanacak bir alt-faz" olarak işaretlemişti; kullanıcı
"4.11'in mimari kararı benim tarafımdan verilmiş sayılır" diyerek bu oturumda uygulanmasını
onayladı. Tasarım kararı: **EKLEYİCİ, opsiyonel ikinci görünüm** — mevcut tek-rapor akışı
(`active` state + `ReportPanel`) HİÇ DEĞİŞMEDİ, sıfır regresyon riski.

`page.tsx`: `canvasMode`/`canvasItems` state (satır 84-85), `addToCanvas()` yardımcısı
(yalnız `canvasMode` açıkken VE gerçek bir rapor/KPI'sıyken ekler), hem `mutation.onSuccess`
(soru sorma) hem `cubeMutation.onSuccess` (chip/sonraki-adım/öneri tıklaması) bunu çağırır.
Sağ panelin üstünde bir araç çubuğu: "🗂 tuval" toggle (aç/kapa, öğe sayısı rozeti) +
(tuval açıkken) "+ şu anki raporu ekle" (retroaktif manuel ekleme — kullanıcı tuval moduna
GEÇ bir noktada geçmiş olabilir, bu turda eklenen bir UX iyileştirmesi, bkz. §3.3).

`AnalysisCanvas.tsx`: biriken kartların grid'i (drag-reorder + **bu turda eklenen** ▲/▼
klavye/dokunmatik erişilebilir sıralama yedeği — native HTML5 DnD'nin klavye eşdeğeri
yok), her kartta "panoya aktar" (mevcut `addDashboardWidget`/`listDashboards`/
`createDashboard` API'lerinin YENİDEN KULLANIMI), "⎙ rapor oluştur" (mevcut `postReport`→
`ReportView` mekanizmasının YENİ bir giriş noktası — `DashboardView.tsx`'teki AYNI desen).
Yalnız `cube_query`+`result` taşıyan bloklar rapora girer (Discovery-kaynaklı/notlar
dürüstçe atlanır — **bu turda eklenen** bir açıklayıcı not kullanıcının kafasının
karışmaması için: "N blok yapısal sorgu taşımadığı için rapora dahil edilmeyecek").

**Test**: canlı tarayıcı bu ortamda YOK — `npx tsc --noEmit` + `npx eslint` ile statik
doğrulama yapıldı (ikisi de temiz). UI etkileşiminin GERÇEK bir tarayıcıda doğrulanması
gelecek-iş belgesinde ayrıca önerilir.

### 4.12 — Canlı düşünme-adımları
`AskJob.trace_json` (`control_plane/models.py:175,558`) her aşama biter bitmez APPEND
edilir (post-hoc değil); `api-client.ts::pollAskJob` bunu poll sırasında `onProgress`
callback'iyle iletir, `page.tsx`'teki `liveTrace` state'i `ChatPanel`'e "yürütülüyor…"
yerine SON adımı gösterir. **Test**: `tests/test_ask_async_discovery.py` içinde trace
birikimi ayrıca doğrulanır.

### 4.13 — Güven rozeti + meta-güven şeridi
`_build_explain()` (`app/routers/ask.py:84`) `confidence`'ı kaynak+varsayım durumuna göre
üretir (cube=1.0, cube+llm=0.85, vqr=0.95, varsayım varsa −0.15 kademe, rule/llm=None).
`ChatPanel.tsx::confidenceBadge()` bunu 🥇(≥0.9)/🥈(0.7-0.89)/🥉(<0.7 veya null) rozetine
çevirir. `app/routers/stats.py` (`GET /stats/today`) `interaction_log.kind`'den GERÇEK
"bugün %X soru LLM'siz cevaplandı" oranını hesaplar; `HelpPanel.tsx` bunu son-kullanıcıya
gösterir. **Bu turda eklenen** ek regresyon: `test_confidence_same_badge_when_same_
question_asked_twice` (UC-2.21'in literal "iki kez sor, aynı rozeti al" senaryosu).

### 4.14 — PII maskeleme
`app/pii.py` — TCKN resmi checksum algoritması (`_tckn_checksum_valid:27`), e-posta/
telefon/IBAN regex maskeleme, `mask_rows()` (112, tablo hücreleri), `apply_to_ask_
response()` (85, `resp.result.rows` + `interpretation` metnini YERİNDE maskeler).
`_finish()` (`app/routers/ask.py:840-843`) ve `/query` (`app/routers/query.py:48-52`)
TEK ÇIKIŞ NOKTASI ilkesiyle çağırır. `pii:view` yetkisi (admin+, `control_plane/
authorize.py:81`) olan roller maskesiz görür — bu erişim `audit.record`'a "pii_view"
olarak düşer. **CSV/PNG dışa aktarımı** (`src/lib/export.ts`) ayrı bir filtre
GEREKTİRMEZ — yalnız zaten-maskelenmiş `AskResponse.result` üzerinde çalışır (tek çıkış
noktası zaten HTTP sınırında uygulandığı için, export.ts'e ulaşan veri HER ZAMAN doğru
şekilde maskeli/yetkiliyse-maskesiz'dir; bu, kod eklemeyi GEREKTİRMEYEN, kanıtlanmış bir
mimari sonuç — bkz. §3.4).

---

## §3 — Doğrulama turunda (bu oturumda) bulunup DÜZELTİLEN somut eksikler

İlk uygulama turu tamamlandıktan sonra kullanıcı "planı üstün körü uygulamış olabilirsin,
her adımı tekrar kontrol et" talimatı verdi. Bu bölüm o kontrolün SOMUT sonuçlarıdır —
her biri gerçek bir kanıtla (kod/test) tespit edildi, varsayımla değil.

### 3.1 — `/ask/drill` kanıt paneli SQL+süre döndürmüyordu (UC-2.18/2.19)
Kendi onaylı 4.10 planım AÇIKÇA "hem İNSAN-OKUNUR metin hem gerçek SQL/cube_query
gösterilir" diyordu ve dış yol haritasının UC-2.18/2.19'u ("kanıt paneli: formül+kaynak
tablo+ÇALIŞAN SQL+süre"; "SQL kopyalanıp DB'de çalıştırılır → AYNI sonuç çıkar") bunu
zorunlu kılıyordu — ama `DrillResponse` (`app/schemas.py:382`) hiçbir zaman `sql`/
`duration_ms` alanı taşımıyordu; `_run()` (`app/routers/ask.py`) bu bilgiyi zaten
ÜRETİYORDU (Query Contract için) ama frontend'e HİÇ TAŞIMIYORDU.
**Düzeltme**: `DrillResponse.sql`/`duration_ms` eklendi; `explain` action'ı bile (yeni
sorgu ÇALIŞTIRMADAN) SQL metnini üretir; `DrillDownPanel.tsx`'e "+ sql göster (kanıt)" +
"sql'i kopyala" + süre gösterimi eklendi. **Kanıt testi**: `test_drill_steps_expose_
running_sql_and_duration_for_evidence_panel` (`tests/test_ask_drill_integration.py`) —
döndürülen SQL'i BİREBİR `/query`'ye gönderip drill'in kendi `result`'ıyla (multiset
karşılaştırma — satır SIRASI garanti edilmez) AYNI olduğunu kanıtlar.

### 3.2 — DB bağlantı hata mesajları ham/İngilizce sürücü metni sızdırıyordu (UC-1.20)
`check_connection()` (`app/db_introspect.py`) `except SQLAlchemyError as exc: raise
ConnectionTestError(str(exc)[:300])` yapıyordu — ham psycopg/SQLAlchemy metni (İngilizce,
teknik jargon) doğrudan kullanıcıya dönüyordu. UC-1.20 "Anlaşılır TÜRKÇE hata mesajı"
istiyordu. **Düzeltme**: `_friendly_connection_error()` (`app/db_introspect.py:56`) yaygın
hata sınıflarını (yanlış şifre/host bulunamadı/bağlantı reddedildi/zaman aşımı/DB yok)
Türkçe, eyleme-geçirilebilir mesajlara çevirir; tanınmayan hatalar bile jenerik Türkçe bir
mesaja düşer (ham metin ASLA sızmaz). **Test**: `test_friendly_connection_error_
classifies_common_driver_failures` (parametrize, 6 senaryo) + `test_check_connection_
failure_message_is_turkish_not_raw_driver_text` (`tests/test_db_introspect.py`).

### 3.3 — UC-1.19 "en az 5 metrik" hiç somut kanıtlanmamıştı
Mevcut test fixture'ı (2 tablo, 1 ölçü) bu kabul kriterini YAPISAL OLARAK kanıtlayamazdı.
**Düzeltme**: `test_draft_mdl_suggests_at_least_five_measures_for_realistic_schema`
(`tests/test_db_introspect.py`) 3 tablolu gerçekçi bir e-ticaret şemasıyla (ürünler+
siparişler+müşteriler) `draft_mdl`'in TOPLAM ≥5 ölçü + 2 ilişki ürettiğini birebir kanıtlar.

### 3.4 — `eval/cases.yaml`'da SIFIR UC-x.y izlenebilirlik etiketi vardı
Plan'ın "Doğrulama" bölümü her UC'nin `eval/cases.yaml`'a UC-etiketli bir vaka olarak
eklenmesini istiyordu; hiçbiri eklenmemişti. **Araştırma sonucu**: `eval/run.py::shape_ok()`
YALNIZ `cube_query` şeklini (cube/measures/dims/gran/filter_ops) kontrol ediyor —
`view_hint`/`explain.confidence`/drill/PII/connections gibi Faz-4 davranışlarının HİÇBİRİ
bu şekilde test EDİLEMEZ (yanlış araç). **Düzeltme**: izlenebilirlik DOĞRU venue'ye
(pytest docstring'leri) taşındı — `test_view_fanout_guard.py` (UC-1.14/1.15), `test_db_
introspect.py`+`test_tenant_connections.py` (UC-1.19/1.20), `test_confidence_badge.py`
(UC-2.21), `test_stats.py` (UC-2.23), `test_pii_integration.py` (UC-2.22), `test_ask_
drill_integration.py` (UC-2.18/2.19) — hepsi artık modül docstring'lerinde AÇIKÇA
etiketli.

### 3.5 — 4.11'in UI/UX'inde eksik senaryolar
Kullanıcının özel talebiyle 4.10/4.11'e ek bir senaryo-bazlı sertleştirme turu yapıldı:
- `DrillDownPanel.tsx`: Esc tuşuyla kapatma eklendi; çifte-tıklama/hızlı-ardışık-tıklama
  yarış durumu (`run()`'da `if (loading) return` erken-çıkışı + tüm dallanma/ilişkili/ham-
  satır butonlarında `disabled={loading}` + görsel soluklaştırma) engellendi.
- `AnalysisCanvas.tsx`: sürükle-bırak'a ek olarak ▲/▼ butonlarıyla klavye/dokunmatik
  erişilebilir sıralama eklendi (native HTML5 DnD'nin klavye eşdeğeri yok — bu gerçek bir
  erişilebilirlik boşluğuydu).
- `page.tsx`: "+ şu anki raporu tuvale ekle" butonu eklendi — kullanıcı tuval moduna
  sohbetin ORTASINDA geçerse, o ana kadar ekranda duran raporu ELLE de ekleyebiliyor
  (önceden yalnız YENİ üretilen raporlar otomatik ekleniyordu).
- `AnalysisCanvas.tsx`: rapora GİRMEYEN blokların sayısını açıklayan bir not eklendi
  (kullanıcı "N blok" derken raporun neden daha az sayfa çıktığını anlasın).

---

## §4 — UC (kabul testi) izlenebilirlik tablosu

Kaynak: `Dima-0-100-Gorev-Takip-Dosyasi (2).md` (repo kökünde) — UC-1.x/UC-2.x
numaralaması bu belgenin KENDİ acceptance-test listesidir (plan'ın görev-numaralarıyla
KARIŞTIRILMAMALI, ayrı bir sayaç).

| UC | Metin (özet) | Karşılık | Kanıt |
|---|---|---|---|
| UC-1.14 | JOIN fan-out'ta tutar şişmez | 4.7a/b | `tests/test_view_fanout_guard.py` |
| UC-1.15 | Mali takvim doğru aralık kullanır | 4.7a (araştırma: varsayımsal, kod yok) | `tests/test_view_fanout_guard.py` docstring |
| UC-1.19 | Yeni DB → ≥5 metrik önerilir | 4.5 | `tests/test_db_introspect.py::test_draft_mdl_suggests_at_least_five_measures...` |
| UC-1.20 | Yanlış şifre → Türkçe hata, yığın izi yok | 4.5 | `tests/test_db_introspect.py::test_check_connection_failure_message_is_turkish...` |
| UC-2.8 | Öneri çipi → yeni grafik ALTA eklenir, üsttekiler silinmez | 4.11 | `page.tsx::addToCanvas` (tuval AÇIKKEN) |
| UC-2.13 | 5 analiz → tuvalde birikir, sürükle-bırak | 4.11 | `AnalysisCanvas.tsx` |
| UC-2.18 | Sayıya tıkla → kanıt paneli: formül+SQL+süre | 4.10 | `tests/test_ask_drill_integration.py::test_drill_steps_expose_running_sql...` |
| UC-2.19 | Kanıt SQL'i kopyala-çalıştır → aynı sonuç | 4.10 | aynı test (multiset round-trip) |
| UC-2.21 | Aynı soru iki kez → aynı rozet | 4.13 | `tests/test_confidence_badge.py::test_confidence_same_badge_when_same_question_asked_twice` |
| UC-2.22 | TCKN ekranda/CSV/PNG maskeli, yetkili görür+loglanır | 4.14 | `tests/test_pii_integration.py` |
| UC-2.23 | Meta-güven paneli gerçek loglardan | 4.13 | `tests/test_stats.py` |
| UC-1.18 | E-posta kolonu 'gizle' → MDL'e hiç yazılmaz | 4.6 (ERTELENDİ) | — |
| UC-2.15/16 | Plane Enforcer ham veri LLM'e girmez | 4.6 (ERTELENDİ, ilkesel koruma yeterli kabul edildi) | `app/interpret.py`'nin mevcut ilkesi |
| UC-2.3/2.10 | Grafik brush-zoom, panoya-ekle her zaman görünür | 4.9 (ATLANDI, kullanıcı kendisi halledecek) | — |

---

## §5 — Test durumu (bu oturumun sonunda)

- **Backend**: `cd backend && /tmp/wrenai-pin-check/bin/python -m pytest -q` →
  **427 passed**, 2 bilinen ÖNCEDEN-VAR-OLAN başarısızlık (`test_ask_golden.py::test_vqr_
  yakin_eslesme_olcu_uyusmazliginda_atlanir`, `test_eval_gate.py::test_eval_gate_answered_
  precision_dusmez` — bozuk/eksik embedding modeli, bu oturumun sebep olduğu bir şey DEĞİL,
  Faz 4 boyunca sabit kaldı).
- **Frontend**: `npx tsc --noEmit -p tsconfig.json` → temiz. `npx eslint .` → yalnız bu
  oturumdan ÖNCE var olan, dokunulmamış dosyalardaki 4 uyarı + 1 hata (`NotificationsBell.
  tsx`, `InterpretationBar.tsx`, `ResultView.tsx`, `e2e/browser-e2e.mjs`) — Faz 4'ün
  dokunduğu HİÇBİR dosyada sıfır sorun.
- **Canlı tarayıcı testi YAPILAMADI** (bu ortamda browser-automation aracı yok) — 4.11'in
  gerçek drag-drop/tıklama davranışı yalnız statik analizle (tsc+eslint+kod okuma)
  doğrulandı, dürüstçe belirtilir.

---

## §6 — Bilinen sınırlar / kasıtlı kapsam-dışı kararlar

- **4.3** (Excel/CSV): kalıcı hale getirilmedi, çok-tablo/ilişki-önerisi YOK — kullanıcı
  kararı, gerçek DB'ye bağlanma (4.5) tercih edilsin diye.
- **4.6** (Plane Enforcer/göz-ikonu): hiç kod yok — ürün-olgunluğunun geç aşamasına
  ertelendi (kullanıcı kararı).
- **4.9** (grafik interaktivite: brush-zoom, panoya-ekle-her-zaman-görünür): atlandı,
  kullanıcı kendisi halledecek.
- **4.5 MySQL desteği**: yalnız Postgres var; MySQL sürücüsü bu ortamda kurulu değil,
  yeni bağımlılık eklemek BİLİNÇLİ olarak ayrı bir karara bırakıldı.
- **`app/kpi.py::kpi_components`/`resolve_kpi`**: `app/drill.py::kpi_components` şeması
  hazır ama `AskResponse.kpi` canlı akışta hiç populer edilmiyor (grep ile doğrulandı) —
  bu yüzden bu drill dalı bugün FİİLEN erişilemez durumda (dormant, ölü kod DEĞİL ama
  kullanılmıyor). Bkz. gelecek-iş belgesi.
- **4.11 sürükle-bırak**: native HTML5 DnD (yeni bağımlılık yok) — ▲/▼ butonlarıyla
  klavye/dokunmatik yedeği eklendi ama `@dnd-kit` gibi bir kütüphanenin sunduğu daha
  zengin (ör. sürükleme sırasında canlı önizleme, dokunmatik-cihazda native drag) deneyim
  YOK.
- **Canlı tarayıcı UI testi**: bu oturumda hiç yapılamadı (araç yok) — 4.10/4.11'in
  GERÇEK bir tarayıcıda (chrome-in-claude ya da elle) bir smoke-test turu ÖNERİLİR (bkz.
  gelecek-iş belgesi).

---

## §7 — AYNI GÜN İKİNCİ TUR: `FAZ4-SONRASI-ONERILER` maddelerinin GERÇEK uygulaması

§6'yı yazdıktan hemen sonra, kullanıcı `FAZ4-SONRASI-ONERILER_2026-08-01.md`'deki 25
maddeyi ("P0/P1/P2'yi mükemmelce hallet") UYGULAMAMI istedi. 7 madde (yeni bağımlılık
gerektiren ya da büyük bir güvenlik/mimari kararı olan) kullanıcının AÇIK seçimiyle
ERTELENDİ; KALAN 18 madde bu turda GERÇEKTEN uygulandı ve test edildi. Tam detay/kanıt
`FAZ4-SONRASI-ONERILER_2026-08-01.md`'nin GÜNCELLENMİŞ hâlinde (her madde ✅/⏸ işaretli) —
burada yalnız EN ÖNEMLİ, dosya:satır referanslı özet.

### 7.1 — P0 (kritik güvenlik boşluğu) KAPANDI
`app/pii.py::mask_query_result()` (yeni, paylaşılan yardımcı) artık `/query`, `/report`
(`app/routers/ask.py::report()`), `/dashboards/{id}/data` (`app/routers/dashboards.py::
dashboard_data`) VE zamanlanmış rapor teslimi (`app/schedules.py::run_schedule` —
`principal=None` ile HER ZAMAN maskeler, otomatik e-posta teslimi için fail-closed) tarafından
çağrılıyor. Kanıt: `tests/test_pii_integration.py`'deki 5 yeni test, özellikle `test_
schedule_delivery_always_masks_tckn_even_for_owner` — `channels.dispatch`'i yakalayıp
`event.rows`'un (GERÇEKTEN e-posta gövdesine giren veri, `app/email_render.py:64`) maskeli
olduğunu birebir kanıtlıyor.

### 7.2 — P1'in TAMAMI (15/15) uygulandı
En dikkat çekici ikisi:
- **KPI motoru wiring'i** (`app/cube_router.py::match_kpi`, `app/routers/ask.py::_try_kpi`)
  yalnız YENİ bir özellik değildi — `tests/test_kpi.py`'nin İKİ testi (`test_likidite_
  kpileri_mizan_uzerinde`, `test_match_kpi_en_uzun_sinonim_kazanir`) `cube_router.match_kpi`
  fonksiyonunun VAR OLMASINI ÖNCEDEN BEKLİYORDU ama fonksiyon HİÇ TANIMLI değildi — yani bu
  iki test bu tur başlamadan ÖNCE de AttributeError ile BAŞARISIZ oluyordu, yalnız daha önce
  hiç FARK EDİLMEMİŞTİ (tam suite çalıştırıldığında görülmesi gerekirken, muhtemelen daha
  önceki tur `test_kpi.py`'yi tek başına hiç çalıştırmamıştı). Bu bulgu, kullanıcının
  "üstün körü uygulamış olabilirsin" şüphesinin SOMUT bir doğrulamasıdır — düzeltildi.
- **Grafik-tıklama→drill** (`EChart.tsx`, `ResultView.tsx::handleChartDataPointClick`,
  `DrillDownPanel.tsx`'in yeni `initialFilter` prop'u) — dikkatle, YALNIZ belirsizlik
  taşımayan basit grafik biçimlerinde devreye girecek şekilde SINIRLANDI; canlı tıklama
  davranışı bu oturumda yine doğrulanamadı (dürüstçe belirtilir).

Kalan 13 madde (ConnectionReviewPanel izni, dashboard yeniden-adlandırma, zamanlanmış rapor
yönetim UI'ı — YENİ `SchedulesPanel.tsx`, Query Contract keşif UI'ı — YENİ
`ContractDetailPanel.tsx`, ReportPanel hook-tekrarının giderilmesi, sessiz-hata-yutma
düzeltmeleri, DrillDownPanel erişilebilirliği, test kapsamı — YENİ `test_health.py` + 3
dosyaya ek test) hepsi `FAZ4-SONRASI-ONERILER_2026-08-01.md`'de tek tek belgeli.

**Yan kazanç**: `NotificationsBell.tsx`'teki, bu OTURUMUN EN BAŞINDAN beri projede duran TEK
`eslint` HATASI (`react-hooks/set-state-in-effect`) bu turda (P1-12'yi düzeltirken, aynı
dosyaya zaten dokunulduğu için) da giderildi — proje artık `npx eslint .` ile TAMAMEN
sıfır hata veriyor (yalnız 4 pre-existing UYARI kaldı, dokunulmamış dosyalarda).

### 7.3 — P2'den seçilen 2 madde
- **`@dnd-kit` geçişi**: kullanıcı onayıyla `@dnd-kit/core`+`sortable`+`utilities` GERÇEKTEN
  kuruldu (`pnpm add`, ~3 dakika, ağ erişimi bu turda doğrulandı) ve `AnalysisCanvas.tsx`
  native HTML5 DnD'den taşındı — artık GERÇEK klavye-erişilebilir sıralama da var.
- **Ölü alan geliştirme (silme yok)**: `Interpretation.facts` → `OutputInsight.tsx`'te
  rozet; `CubeMeta.dimension_values`/`ColumnMeta.values` → `SchemaPanel.tsx`'e yeni bir
  "Cube'lar" bölümü; **`DashboardWidget.pos`/`refresh`** — en dikkat çekici bulgu: bu iki
  alan için DB KOLONLARI (`control_plane/models.py:341-342`) VE okuma tarafı (`_widget_
  dict()`, `app/routers/dashboards.py:73-77`) ZATEN vardı, yalnız YAZMA ucu (`WidgetPatch`)
  iki alanı hiç KABUL ETMİYORDU — eklendi + `DashboardView.tsx`'e genişlik-toggle'ı +
  yenileme-sıklığı seçici UI'ı bağlandı; `AskResponse.planned_sql` → `ReportPanel.tsx`'e
  (yalnız gerçek SQL'den farklıysa) eklendi. `getAccessToken()`/`runQuery()` İNCELENDİ,
  BİLİNÇLİ olarak dokunulmadı (gerekçesi `FAZ4-SONRASI-ONERILER`'de).

### 7.4 — Bu turun sonunda test durumu
- Backend: **449 passed**, 2 bilinen ÖNCEDEN-VAR-OLAN başarısızlık (değişmedi).
- Frontend: `tsc --noEmit` VE `eslint .` PROJE GENELİNDE **sıfır hata** (yalnız 4
  dokunulmamış-dosya uyarısı kaldı — bu turdan ÖNCE de vardı).

### 7.5 — Bu turda BİLEREK ertelenen 7 madde
RBAC Layer B tam uygulaması, eval harness genişletme, MySQL desteği, WebSocket geçişi,
Plane Enforcer sertleştirme, bildirim kanalları genişletme — hepsi kullanıcının AÇIK
seçimiyle ("diğerlerine gerek yok") bu turun DIŞINDA tutuldu; gerekçeleri DEĞİŞMEDİ,
`FAZ4-SONRASI-ONERILER_2026-08-01.md`'nin "Ertelenmiş" bölümünde aynen duruyor.
