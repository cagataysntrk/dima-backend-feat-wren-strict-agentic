# Panel Turu 005 — Çok-kiracılık runtime & tenant izolasyonu: paylaşılan state tenant sınırını deliyor mu?

**Tarih:** 2026-07-24
**Senaryo tipi:** Güvenlik/eşzamanlılık denetimi (R4'ün "izolasyon connection düzeyinde, SQL RLS yok" bulgusunun runtime stres-testi)
**Kapsam:** `app/vqr.py` (110-230), `app/schedules.py` (178-259), `app/routers/schedules.py`, `app/company_registry.py` (24-98), `app/compose.py` (75-93), `app/wren_service.py` (schema/overlay/_engine), `app/main.py`, auth/dependencies
**Modeller:** Haiku (VQR scope), Sonnet (schedules tenant), Opus (registry cache/race), Fable (overlay + request→tenant + auth)

## Araştırma sorusu
Çok-kiracılık RUNTIME'ında hangi paylaşılan state (VQR, schema_cache, cron TenantContext, overlay, registry) tenant sınırını deliyor? Bir tenant'ın verisi/bilgisi başka tenant'a sızıyor mu; eşzamanlılık izolasyonu bozuyor mu?

## GENEL YARGI
İzolasyon **request/auth düzeyinde sağlam** (IDOR kapalı, overlay scope doğru, require_company veri uçlarında tam) AMA **arka-plan ve paylaşılan-state düzeyinde kırık**: (1) scheduler cron'ları default tenant motorunda koşuyor → cross-tenant veri sızıntısı; (2) registry compose+build lock-dışı + in-place rmtree → eşzamanlılıkta bozuk MDL; (3) VQR yalnız default tenant'ta çalışıyor (diğerleri öğrenmeden yoksun).

---

## (a) UZLAŞILAR (yüksek güven, orkestratör KAYNAKTA doğruladı)

### U1 — [P0 GÜVENLİK/KVKK] SCHEDULES CROSS-TENANT MOTOR KAÇAĞI (Sonnet + Fable, orkestratör KANITLADI)
`run_schedule` (schedules.py:184) `svc = state.wren` — DEFAULT şirketin WrenService'i. `sched["tenant_id"]` kaydediliyor (routers/schedules.py:72) ama connection seçiminde HİÇ kullanılmıyor; `company_registry.service_for` schedule yolunda ÇAĞRILMIYOR (grep boş). `run_due` (245-255) tüm tenant'ların schedule'larını tek `state.wren` ile koşuyor. **Sonuç:** tenant B'nin cron'u tenant A'nın (default) veritabanını sorgular → B'nin raporunda A'nın verisi. RLS (`_visible`/tenant_id) yalnız bildirim GÖRÜNÜRLÜĞÜNÜ sınırlıyor, sorgunun HANGİ motorda koştuğunu değil. **KVKK 12 ihlali.** `create_schedule` (routers/schedules.py:55) da `request.state.wren` yerine `app.state.wren` ile doğruluyor → yanlış şemaya karşı cube-query doğrulaması.
- Orkestratör kaynakta doğruladı: schedules.py:184 `svc = state.wren`, tenant_id connection'da kullanılmıyor.

### U2 — [P0 EŞZAMANLILIK] REGISTRY compose+build LOCK-DIŞI + IN-PLACE rmtree → BOZUK MDL (Opus, orkestratör KANITLADI)
`service_for` (company_registry.py:37-55): lock içinde cache OKU (37-38), lock BIRAK (39), lock DIŞINDA `compose()` + `build()` (45-46), lock içinde YAZ (53-54). Double-check yok. İki eşzamanlı istek (veya istek + scheduler recompose) aynı `demo/wren-projects/<slug>/` dizinine paralel çalışır. `compose` (compose.py:75-77) `if out.exists(): shutil.rmtree(out); out.mkdir()` — IN-PLACE yıkıcı yeniden-inşa. Ölümcül interleaving: T1 copy2 ederken T2 rmtree → FileNotFoundError/FileExistsError ya da yarım `target/mdl.json`. **Kalıcı bozuk artefakt** → sonraki tüm istekler bozuk MDL okur. Orkestratör kaynakta doğruladı (company_registry.py:37-46, compose.py:75-77).

### U3 — [P1] VQR RETRIEVAL TENANT-KÖR + yalnız-default-tenant çalışıyor (Haiku buldu, Fable NÜANSLADI)
`recall`/`near_exact`/`few_shot_block` (vqr.py:186,192,208) `self._load()` ile TÜM çiftleri okur, tenant filtresi YOK. AMA Fable'ın nüansı doğru (orkestratör onayladı): `vqr = None if request.state.wren else app.state.vqr` (ask.py:366,623) + tüm VQR uçları require_company taşıdığından, **non-default tenant'ta VQR TAMAMEN KAPALI** → Haiku'nun "sessiz default'a yazma sızıntısı" GERÇEKLEŞMİYOR. Gerçek sorun: (a) non-default tenant'lar VQR öğrenmesinden HİÇ faydalanmıyor (işlevsel boşluk, P3); (b) global tek-dosya + tenant-kör retrieval, ileride VQR çok-tenant açılırsa sızıntıya HAZIR (latent). Düzeltme yine de gerekli: recall/near_exact/few_shot_block'a tenant_id filtresi.

---

## (b) ÇELİŞKİLER & KİM HAKLI (orkestratör doğruladı)

### Ç1 — Haiku "VQR cross-tenant sızıntısı P0" → Fable ÇÜRÜTTÜ (Fable haklı)
Haiku "tenant B few-shot'ta A'nın sorusunu görür" dedi. Fable kanıtladı: non-default tenant'ta `request.state.wren` set olduğundan `vqr=None` → VQR hiç çalışmaz, sızıntı olmaz. Haiku'nun senaryosu yalnız "token fraud / default session'a girme" varsayımıyla geçerli (ayrı bir auth-bypass gerekir). **Fable haklı: bugünkü sızıntı YOK, ama VQR mimarisi tenant-kör (latent + işlevsel boşluk).** Haiku'nun retrieval-filtresi-yok tespiti doğru; sadece istismar-edilebilirlik iddiası abartılı.

### Ç2 — "IDOR: başka tenant slug'ı ile service_for" → YOK (Fable, orkestratör onayladı)
`service_for(slug)` kör servis döner (yetki yok) ama TEK çağıran `require_company` imzalı JWT claim'inden (`principal.tenant_slug`, dependencies.py:132) slug geçiriyor; request'ten slug HİÇ okunmuyor. IDOR kapalı. Overlay scope de (wren_service.py:228-238) global+kendi-tenant birleşimini doğru uyguluyor, sızıntı yok. **İzolasyonun auth tarafı sağlam** — bu adil bir "yanlış-alarm değil" tespiti.

---

## (c) HER MODELİN ÖZGÜN BULGUSU
- **Opus (eşzamanlılık):** U2 (compose race) + `invalidate` stale-referans (pop dict'ten ama in-flight istek eski instance+eski MDL ile devam, recompose rmtree'si altından çeker) + `schema()` lazy-fill kilitsiz (eşzamanlı çift full-compute: DB DISTINCT probları + control-plane DB çift sorgu) + default (`app.state.wren`) vs registry çift-yol (çatallı invalidation, default registry'ye sızarsa farklı project_dir/MDL çift-instance). Adil pay: `_engine()` (her query yeni engine + dict-kopya connection) thread-safe.
- **Sonnet (schedules):** U1 + ScheduleStore tek-tenant flat dosya (main.py:80, tüm tenant'lar tek schedules.yaml, disk izolasyonu yok) + `run_due` sessiz hata yutma (except Exception: continue — cross-tenant çökme loglanmaz) + superadmin run tenant-körü (default DB).
- **Fable (overlay+auth):** overlay scope DOĞRU (sızıntı yok, güvenli tespit) + require_company kapsam tablosu (veri uçları tam, schedule uçları `state.wren` istisnası) + IDOR kapalı + `/health/ready` default mdl-path ifşası (P2 bilgi sızıntısı) + overlay scope_id tenant-varlık doğrulaması yok (global yanlış seçilirse tüm tenant'lara iner, P2).
- **Haiku:** VQR retrieval tenant-körlüğü (recall/near_exact/few_shot_block filtre yok) — mekanizma doğru, istismar abartılı (Ç1); tenant-filtre düzeltme yönü geçerli.

---

## (d) "MÜKEMMEL SENARYO" ÖNERİSİ
Tenant sınırı HER katmanda (auth ✓, ama arka-plan + paylaşılan-state ✗) tutmalı. İdeal: (1) scheduler her schedule'ı kendi tenant'ının `service_for(slug)` motorunda koşsun (cron'a tenant_slug persist et); (2) compose atomik (temp dizine yaz + `os.replace`), per-slug lock + double-check; (3) schema() lock'lu double-check; (4) VQR tenant-scope'lu (her tenant kendi öğrenmesi, retrieval tenant-filtreli); (5) default tenant registry tek-yolunda. Kısaca: request-düzeyi izolasyonu arka-plan ve dosya-sistemi düzeyine genişlet.

---

## (e) SOMUT AKSİYON MADDELERİ (önem-sıralı)

1. **[P0 GÜVENLİK] Scheduler tenant-farkında motor** — `run_schedule` (schedules.py:184) `state.wren` yerine `sched` tenant_slug'ından `registry.service_for(slug)` çözsün; `create_schedule` (routers/schedules.py:55) `wren_for_request(request)` kullansın. Cron'a tenant_slug persist et (arka-plan döngüde principal yok). Cross-tenant veri sızıntısını (KVKK) kapatır. **En kritik.**
2. **[P0 EŞZAMANLILIK] Atomik compose + per-slug lock** — `service_for` (company_registry.py:36) per-slug lock + double-check; `compose` (compose.py:75-77) in-place rmtree yerine temp dizine yazıp `os.replace` ile atomik takas. Bozuk-MDL yarışını ve in-flight rmtree-çekilmesini kapatır.
3. **[P1] invalidate → yeni-instance/yeni-dizin** — pop yerine recompose yeni dizine, yeni WrenService cache'e, eski instance GC'ye (in-flight okuma eski inode'da güvenli devam eder).
4. **[P1] schema() lazy-fill lock** — instance-lock + double-check; eşzamanlı çift full-compute (DB probları) + kısmi-cache okumasını engelle.
5. **[P1] VQR tenant-scope** — recall/near_exact/few_shot_block'a tenant_id filtresi (vqr.py:186,192,208); her tenant kendi VQR öğrenmesi (per-tenant path). İşlevsel boşluğu + latent sızıntıyı kapatır.
6. **[P1] default vs registry tek-yol** — default tenant'ı da `service_for(settings.company)` üzerinden yönet; çatallı invalidation'ı birleştir.
7. **[P1] run_due sessiz-hata loglama** — `except Exception: continue` (schedules.py) audit/log; cross-tenant çökme görünür olsun.
8. **[P2] ScheduleStore tenant-disk izolasyonu** — tek flat schedules.yaml yerine per-tenant; bugün yalnız tenant_id alanıyla ayrım.
9. **[P2] overlay scope_id doğrula + /health/ready tenant-nötr** — scope_id Tenant.slug'a karşı doğrulansın; ready default mdl-path ifşa etmesin.

---

## (f) SONRAKİ TUR (zorluk artışı)
**006 — "Onboarding/semantik keşif otomasyonu doğruluğu: yeni tenant pack'i canlı DB'den ne kadar güvenilir türetiliyor":** R5 arka-plan/paylaşılan-state sorunlarını gösterdi; şimdi pack ÜRETİM yolunu denetle. Yeni bir müşteri bağlandığında (ADR-0017 fingerprint, netsis/logo introspection, e7472e7/a3016bb commit'leri) semantik keşif (base-type resolution, DATE_TRUNC version-safe, read_only_verified, categorical enum mining) hangi noktalarda SESSİZ-YANLIŞ pack üretiyor? (1) introspection bir kolonu yanlış tipte/kardinalitede algılayıp yanlış cube/dimension üretir mi; (2) always_filter/semi_additive metadata otomatik mı manuel mi — otomatikse yanlış işaretleme kablosuz-motoru besler (R1); (3) enum mining (_MAX_ENUM=25) yüksek-kardinalite kolonu düşük sanıp değer-filtresi hayaleti üretir mi (R3 substring ile birleşir); (4) pack-lint (ADR-0017 source-agnostic) hangi hataları yakalamıyor; (5) çok-firma/çok-dönem (firma/donem binding) yanlış şubeyi/dönemi bağlar mı. Onboarding doğruluğu = tüm downstream doğruluğun temeli.
