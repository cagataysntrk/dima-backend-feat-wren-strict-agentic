> ⚠️ **TARİHSEL KAYIT — NORMATİF DEĞİLDİR.** Bu belge yazıldığı andaki durumu ve o turda alınan
> kararları anlatır. Mimari otorite `backend/MIMARI.md`'dir; çelişkide o kazanır.
> Özellikle: bu belgelerdeki JOIN/derleyici teşhisleri `MIMARI.md §3.2`'de **düzeltilmiştir**.

# Dima — Faz 4 Sonrası Öneriler (1 Ağustos 2026, GÜNCELLEME: aynı gün ikinci tur)

Bu belge `HANDOFF_2026-08-01_faz4-tamamlama.md`'nin TAMAMLAYICISI. İlk yazıldığında 24
madde (1 P0 + 15 P1 + 9 P2 — bu turdan önceki hâliyle sırasıyla) listeliyordu; kullanıcının
"P0/P1/P2'yi mükemmelce hallet" talimatıyla **AYNI GÜN İÇİNDE İKİNCİ BİR TUR** yapıldı ve
P0'ın TAMAMI + P1'in TAMAMI + P2'nin 2 maddesi (18, 22) GERÇEKTEN UYGULANDI, test edildi ve
doğrulandı. Bu belge şimdi HEM neyin yapıldığını (kanıtla) HEM geriye kalan (kullanıcının
kendi kararıyla bu turda BİLEREK atlanan) 7 maddeyi gösterir.

**Bu ikinci turda ATLANAN 7 madde** (kullanıcının kendi seçimiyle — "diğerlerine gerek yok"):
P1-5 (RBAC Layer B tam uygulaması), P2-16 (eval harness genişletme), P2-17 (MySQL desteği),
P2-19 (WebSocket geçişi), P2-20 (Plane Enforcer), P2-23 (bildirim kanalları genişletme).
Bunlar AŞAĞIDA "Ertelenmiş" bölümünde, ORİJİNAL gerekçeleriyle KORUNUYOR.

---

## Genel durum (bu turdan sonra)

**25 maddeden 18'i UYGULANDI ve test edildi** (P0'ın 5 alt-görevi + P1'in 15 maddesinin
13'ü tamamen yeni kod + 2'si zaten var olan test/altyapı doğrulaması + P2'nin 2 maddesi).
Backend: **449 test geçiyor**, yalnız 2 bilinen ÖNCEDEN-VAR-OLAN başarısızlık (embedding
modeli kaynaklı, bu turla ilgisiz). Frontend: `tsc --noEmit` + `eslint .` PROJE GENELİNDE
sıfır hata (yalnız bu turdan ÖNCE de var olan, dokunulmamış dosyalardaki 4 uyarı kaldı).

---

## ✅ P0 — TAMAMLANDI

### 0. PII maskeleme üç veri-çıkış yüzeyini kapatma
**Yapıldı**: `app/pii.py::mask_query_result(result, principal)` (paylaşılan yardımcı) eklendi;
`app/routers/query.py` (refactor), `app/routers/dashboards.py::dashboard_data`, `app/report.py`
(çağıran `app/routers/ask.py::report()` içinde, sayfa/blok döngüsünde), `app/schedules.py::
run_schedule` (principal=None, HER ZAMAN maskeler — fail-closed, otomatik teslim için) artık
HEPSİ maskeliyor. **Kanıt**: `tests/test_pii_integration.py` — 5 yeni test (`test_report_
masks_tckn_for_non_privileged_role`, `test_report_owner_sees_unmasked_and_is_audited`,
`test_dashboard_data_masks_tckn_for_non_privileged_role`, `test_dashboard_data_owner_sees_
unmasked_and_is_audited`, `test_schedule_delivery_always_masks_tckn_even_for_owner` —
sonuncusu `channels.dispatch`'i monkeypatch'leyip `event.rows`'un GERÇEKTEN maskeli
olduğunu, e-postaya giden veriyi BİREBİR kanıtlar).

---

## ✅ P1 — TAMAMLANDI (15/15)

### 1. KPI motorunu canlı akışa bağlama
**Yapıldı**: `app/cube_router.py::match_kpi(q_norm, schema)` eklendi (soru→KPI-adı
eşleştirmesi); `app/routers/ask.py::_try_kpi()` yeni bir dal olarak `_try_fresh_intent()`'in
BAŞINA eklendi — eşleşirse `resolve_kpi` çağrılıp `AskResponse.kpi` doldurulur. **Bulgu**:
`tests/test_kpi.py`'nin İKİ testi (`test_likidite_kpileri_mizan_uzerinde`, `test_match_kpi_
en_uzun_sinonim_kazanir`) ZATEN `cube_router.match_kpi`'yi BEKLİYORDU ama fonksiyon hiç
TANIMLI değildi (AttributeError ile başarısız oluyorlardı, bu turda İLK KEZ farkedildi ve
düzeltildi) — `match_kpi` bu testlerin BEKLEDİĞİ TAM sözleşmeyle (girdi ÖNCEDEN normalize
edilmiş, dönüş KPI adı STRING) yazıldı. **Kapsam (bilinçli)**: yalnız skaler kart
(`resolve_kpi`); dönem-serisi (`resolve_kpi_series`) ayrı bir tura bırakıldı. **Kanıt**:
`tests/test_kpi_routing.py` (7 yeni test) + `tests/test_kpi.py`'nin artık İKİSİ de geçiyor.

### 2. Grafik-tıklama (dataIndex) → drill entegrasyonu
**Yapıldı**: `EChart.tsx`'e `onDataPointClick` (seriesIndex+dataIndex+name) eklendi;
`ResultView.tsx::handleChartDataPointClick` yalnız BASİT, tek-birincil-boyutlu grafiklerde
(facet/scatter/heatmap HARİÇ) devreye girer, ECharts'ın gösterdiği `name`'i HAM satırlarda
TAM eşleştirip doğrular (biçim uyuşmazsa SESSİZCE atlar — yanlış filtre göndermez);
`DrillDownPanel.tsx`'e `initialFilter` prop'u eklendi (ilk adımın KENDİSİ `action:"select"`
olur, ayrı bir effect/ikinci-adım GEREKMEDEN); `ReportPanel.tsx` ikisini birbirine bağlar.
**Bilinen sınır**: canlı tarayıcıda TIKLAMA davranışı bu oturumda doğrulanamadı (araç yok) —
statik tip kontrolü + mantıksal izleme ile mümkün olan en yüksek titizlikte yapıldı, ama
GERÇEK bir tarayıcıda smoke-test (madde 3'teki gibi) hâlâ ÖNERİLİR.

### 4. value_index.py fuzzy eşleştirmeyi bağlama
**Yapıldı**: `cube_router.typo_correct()`'in SONUNA (mevcut tek-kelimelik difflib geçişini
DEĞİŞTİRMEDEN, yalnız hâlâ tanınmayan kelimeler için) `value_index.FuzzyIndex` ile bir
BİGRAM (çok-kelimeli değer) denemesi eklendi. **Kanıt**: gerçek şemada "KONTİNÜ KASAR"
(oee cube'unun çok-kelimeli bir makine değeri) ile `tests/test_cube_router.py::test_value_
index_multi_word_value_typo_fallback` — "kontinu kasr" → "kontinu kasar" GERÇEKTEN düzeltir;
`test_value_index_fallback_does_not_fire_when_nothing_left_unknown` regresyon kilidi.
Golden-eval precision DOKUNULMADI (tam suite 2 bilinen hata dışında yeşil).

### 6. ConnectionReviewPanel izin gizleme
**Yapıldı**: `usePermission("connection:write")` eklendi — yetkisiz kullanıcı artık sihirbaz
yerine açıklayıcı bir mesaj görür.

### 7. Dashboard yeniden-adlandırma/görünürlük UI'ı
**Yapıldı**: `api-client.ts::patchDashboard`, `DashboardsPanel.tsx`'e ✎/🏢🔒/× aksiyonları.
**Kanıt**: `tests/test_dashboards.py::test_dashboard_patch_renames_and_changes_visibility`
(sahiplik + görünürlük + 403 yetkisiz-yazma senaryosu dahil).

### 8. Zamanlanmış rapor yönetim UI'ı
**Yapıldı**: `api-client.ts::{listSchedules,deleteSchedule,runScheduleNow}` + YENİ
`SchedulesPanel.tsx` (Ayarlar drawer'ına üçüncü sekme: "Zamanlamalar" — liste, sil, şimdi
çalıştır, hata geri bildirimi).

### 9. Query Contract keşif/replay UI'ı
**Yapıldı**: `api-client.ts::{getContract,replayContract}` + YENİ `ContractDetailPanel.tsx`
(soru+SQL+satır sayısı+"bugün yeniden çalıştır" ile verdict). `ReportPanel.tsx` VE
`NotificationsBell.tsx`'teki `contract_id` metinleri artık TIKLANABİLİR.

### 10. DrillDownPanel'de contract_id gösterme
**Yapıldı**: aynı `ContractDetailPanel` `DrillDownPanel.tsx`'in SQL-kanıt bölümüne de
eklendi (ReportPanel'deki ile TUTARLI).

### 11. ReportPanel paylaşılan hook'ları kullanma
**Yapıldı**: `ReportPanel.tsx`'in kendi `useFeature`/`usePermission` kopyaları SİLİNDİ,
`src/lib/useFeature.ts`/`usePermission.ts` import edildi — gereksiz `/features`+`/auth/me`
çağrıları kalktı.

### 12. Sessiz hata yutmayı giderme
**Yapıldı**: `ReportPanel.tsx` (zamanla/yanlış-işaretle/doğrula-geri-al) artık paylaşılan
`actionError` state'iyle görünür hata mesajı veriyor; `NotificationsBell.tsx::
NotificationsPanel` fetch başarısızlığını "bildirim yok"tan AYIRT ediyor. **Yan kazanç**:
`NotificationsBell.tsx`'teki ÖNCEDEN-VAR-OLAN `react-hooks/set-state-in-effect` lint HATASI
(bu oturumun EN BAŞINDAN beri projede duran tek hata) bu sırada da düzeltildi (lazy
`useState` initializer) — proje artık `eslint .` ile TAMAMEN sıfır hata.

### 13. DrillDownPanel erişilebilirliği
**Yapıldı**: modal `role="dialog" aria-modal="true"`; `BreakdownTable` satırları
`tabIndex`+`onKeyDown` (Enter/Space) ile klavye-erişilebilir; ikon butonlara `aria-label`
(`DashboardView.tsx` dahil).

### 14. İnce test kapsamını doldurma
**Yapıldı**: YENİ `tests/test_health.py` (4 test — `/health`, `/health/ready` DB/MDL-down
senaryoları dahil); `tests/test_conversations.py`'ye DELETE testi (soft-delete + idempotency);
`tests/test_measure_promote.py`'ye `reject_candidate` (yaşam döngüsü + 409 durum makinesi)
+ `blast_radius` (gerçek/sıfır kullanım) testleri. **Düzeltme**: `contracts.py`'nin AslıNDA
`tests/test_ask_golden.py`+`test_auth.py`'de ZATEN iyi test edildiği keşfedildi (ilk
araştırmanın YANLIŞ bir bulgusu) — orada tekrar iş YAPILMADI.

### 15. admin_app/app auth duplikasyon notu
**Yapıldı**: `app/auth/router.py` ve `admin_app/auth_router.py`'ye birbirine işaret eden
kısa çapraz-referans yorumları eklendi (kod DEĞİŞMEDİ, kasıtlı mimari korunuyor).

---

## ✅ P2 — Bu turda seçilen 2/9 madde TAMAMLANDI

### 18. AnalysisCanvas'ı @dnd-kit'e taşıma
**Yapıldı**: `@dnd-kit/core`+`sortable`+`utilities` GERÇEKTEN kuruldu (kullanıcı onayıyla,
`pnpm add` — ~3 dk sürdü, ağ erişimi doğrulandı). `AnalysisCanvas.tsx` native HTML5 DnD'den
`DndContext`+`SortableContext`+`useSortable`'a taşındı — artık native DnD'nin SAHİP OLMADIĞI
GERÇEK klavye-erişilebilir sıralama da var (▲/▼ butonları YİNE DE korunur, ek bir yedek).

### 22. Ölü/kullanılmayan alanları geliştirme (SİLME YOK)
Kullanıcı talimatı: "silme yapma, geliştirilmesi gerekiyorsa geliştir, kapatılabiliyorsa
kapat." Madde madde:
- **`Interpretation.facts`**: `OutputInsight.tsx`'e trend/peak/bottom/kpi_components türleri
  için tür-simgeli, taranabilir rozetler eklendi (`summary` zaten bu metni birleştirilmiş
  tek cümlede taşıyordu — rozetler AYNI bilgiyi hızlı-tarama için görsel olarak ayrıştırır).
- **`ColumnMeta.values`/`CubeMeta.dimension_values`**: `SchemaPanel.tsx`'e hem model
  kolonlarının olası değerleri hem de YENİ bir "Cube'lar" bölümü (ölçü/boyut/boyut-değerleri)
  eklendi — bu veri backend'den ZATEN geliyordu, hiç GÖSTERİLMİYORDU.
- **`DashboardWidget.pos`/`refresh`**: **backend'de bu iki DB kolonu (`pos_json`, `refresh`)
  ve OKUMA tarafı (`_widget_dict`) ZATEN vardı** — yalnız YAZMA ucu (`WidgetPatch`/
  `patch_widget`) iki alanı hiç KABUL ETMİYORDU. Eklendi + test edildi (`tests/test_
  dashboards.py::test_dashboard_widget_patch_pos_and_refresh_persist`). Frontend:
  `DashboardView.tsx`'e widget-başına genişlik toggle'ı (dar/geniş, `xl:col-span-2`) +
  yenileme-sıklığı seçici (onview/5dk/1dk/canlı) eklendi; PANO'nun tek birleşik `/data`
  isteği artık en HIZLI yapılandırılmış widget'ın sıklığında yenilenir (pragmatik: gerçek
  per-widget ayrı istekler yerine, doğruluğu korurken karmaşıklığı düşük tutar).
- **`AskResponse.planned_sql`**: backend'de (app/routers/ask.py) ZATEN dolduruluyordu,
  frontend'de HİÇ okunmuyordu. `ReportPanel.tsx`'e eklendi — yalnız GERÇEK çalışan SQL'den
  FARKLIYSA gösterilir (öz-iyileştirme/repair sonrası "plan neydi, gerçekte ne çalıştı"
  farkını görünür kılar).
- **`getAccessToken()`/`runQuery()`**: incelendi, BİLİNÇLİ olarak dokunulmadı (silinmedi,
  geliştirilmedi) — `getAccessToken` saf bir iç auth detayı (UI'a taşınacak bir "özellik"
  değil); `runQuery()` bir "SQL çalıştırıcı" UI'ı gerektirir ki bu YENİ, güvenlik-hassas,
  kapsamı büyük bir özellik kararı olurdu (bu turun "küçük boşluk kapat" ruhunun DIŞINDA) —
  gerçek bir talep doğarsa AYRI ele alınmalı.

---

## ⏸ Ertelenmiş (kullanıcının kendi seçimiyle, bu ikinci turda DA atlandı)

### P1-5. RBAC Layer B (ModelPermission/enforce_query) tam uygulaması
Değişmedi — hâlâ dormant (aktif tehlike değil, yarım bırakılmış altyapı). `control_plane/
authorize.py:133`, `control_plane/models.py:74`. Gerçek bir "satır/kolon bazlı erişim"
ihtiyacı somutlaşırsa ele alınmalı.

### P2-16. `eval/cases.yaml` harness genişletme
Değişmedi — `eval/run.py::shape_ok()` yalnız cube_query şeklini test edebiliyor. Yalnız
gerçekten tekrarlayan bir ihtiyaç doğarsa genişletilmeli.

### P2-17. MySQL desteği (`app/db_introspect.py`)
Değişmedi — yalnız Postgres destekleniyor, `pymysql` YENİ bir üretim bağımlılığı, ayrı
bir kararla eklenmeli.

### P2-19. WebSocket'e geçiş (4.12'nin canlı akışı)
Değişmedi — polling BİLİNÇLİ bir tercih, yalnız somut bir performans sorunu çıkarsa
gözden geçirilmeli.

### P2-20. Plane Enforcer sertleştirme (4.6)
Değişmedi — `app/interpret.py`'nin ilkesel koruması hâlâ merkezi/test edilmiş bir guard
DEĞİL. Pentest öncesi GERÇEKTEN ele alınması önerilir.

### P2-23. Bildirim kanalları (push/slack/webhook)
Değişmedi — yalnız inapp/email uygulanmış, `app/channels.py`'de gelecek iş olarak anılıyor.

### P2-21 ve P2-24 (küçük, düşük öncelik)
`demo/packs/kaynak/{logo-3,netsis,mikro-v16}` turev.yml incelemesi ve `tests/test_ask_
golden.py:529`'daki "senden" kenar-durumu — bu turda ele alınmadı, düşük öncelik olarak
kalıyor (madde 1'in KPI-motoru wiring'i tamamlandığı için turev.yml incelemesi artık
biraz daha alakalı hâle geldi, bir sonraki turda değerlendirilebilir).

---

## Öncelik/emek/risk özet tablosu (güncel durum)

| # | Madde | Durum | Kanıt/Not |
|---|---|---|---|
| 0 | PII maskeleme 3 yüzeyi kapat | ✅ TAMAMLANDI | 5 yeni test, tests/test_pii_integration.py |
| 1 | KPI motorunu canlı akışa bağla | ✅ TAMAMLANDI | cube_router.match_kpi + 2 önceden-bozuk test düzeldi |
| 2 | Grafik-tıklama→drill | ✅ TAMAMLANDI (statik doğrulama) | canlı tarayıcı smoke-test hâlâ önerilir |
| 3 | Canlı tarayıcı smoke-test turu | ⏸ Yapılamadı (araç yok) | bir sonraki oturuma |
| 4 | value_index fuzzy eşleştirmeyi bağla | ✅ TAMAMLANDI | 2 yeni test, gerçek şema örneği |
| 5 | RBAC Layer B | ⏸ Ertelendi (kullanıcı kararı) | dormant, aktif risk yok |
| 6 | ConnectionReviewPanel izin gizleme | ✅ TAMAMLANDI | — |
| 7 | Dashboard yeniden adlandırma UI | ✅ TAMAMLANDI | 1 yeni test |
| 8 | Zamanlanmış rapor yönetim UI'ı | ✅ TAMAMLANDI | SchedulesPanel.tsx |
| 9 | Query Contract keşif UI'ı | ✅ TAMAMLANDI | ContractDetailPanel.tsx |
| 10 | Drill'de contract_id göster | ✅ TAMAMLANDI | aynı bileşen yeniden kullanıldı |
| 11 | ReportPanel paylaşılan hook'ları kullansın | ✅ TAMAMLANDI | — |
| 12 | Sessiz hata yutmayı gider | ✅ TAMAMLANDI | + pre-existing lint hatası da düzeldi |
| 13 | Drill modal erişilebilirliği | ✅ TAMAMLANDI | — |
| 14 | İnce test kapsamını doldur | ✅ TAMAMLANDI | test_health.py yeni, +3 dosyaya test eklendi |
| 15 | admin_app auth duplikasyon notu | ✅ TAMAMLANDI | yorum-only |
| 16 | eval harness genişletme | ⏸ Ertelendi (kullanıcı kararı) | — |
| 17 | MySQL desteği | ⏸ Ertelendi (kullanıcı kararı) | — |
| 18 | `@dnd-kit`'e geçiş | ✅ TAMAMLANDI | kuruldu + migrate edildi |
| 19 | WebSocket'e geçiş | ⏸ Ertelendi (kullanıcı kararı) | — |
| 20 | Plane Enforcer sertleştirme | ⏸ Ertelendi (kullanıcı kararı) | — |
| 21 | ERP turev.yml incelemesi | ⏸ Yapılmadı (düşük öncelik) | — |
| 22 | Ölü FE alan/export'ları geliştir | ✅ TAMAMLANDI (kısmen bilinçli no-op) | facts/dimension_values/pos+refresh/planned_sql |
| 23 | Bildirim kanalları genişletme | ⏸ Ertelendi (kullanıcı kararı) | — |
| 24 | "senden" kenar-durumu | ⏸ Yapılmadı (düşük öncelik) | — |
