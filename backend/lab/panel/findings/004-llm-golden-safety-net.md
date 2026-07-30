# Panel Turu 004 — LLM/golden güvenlik ağı: "deterministik-red → LLM devralsın" çözümünün kendisi kablosuz-motor mu?

**Tarih:** 2026-07-24
**Senaryo tipi:** Güvenlik ağı denetimi (R1-R3'ün tüm çözümleri "LLM'e düş"e dayanıyordu — ağ sağlam mı?)
**Kapsam:** `app/llm.py` (_schema_prompt 49-73, _build_system 97-113, temperature 231, generators 177-260), `app/routers/ask.py` (serbest-SQL 1147-1204, _select_consistent 240-274), `app/wren_service.py` (guard_sql 30-39, query 497-508, dry_plan 475-479, _inject_always_filter 379-423, _load_knowledge/golden 209,304-319)
**Modeller:** Haiku (golden retrieval), Sonnet (prompt kısıt-farkındalığı), Opus (serbest-SQL güvenlik), Fable (self-consistency)

## Araştırma sorusu
R1-R3'ün her çözümü "deterministik reddet → LLM devralsın"dı. Bu güvenlik ağı SAĞLAM mı? golden retrieval var mı, prompt kısıtları biliyor mu, self-consistency gerçek güven mi, serbest-SQL güvenlik katmanlarından geçiyor mu?

## GENEL YARGI (çapraz-model, orkestratör KANITLADI)
**HAYIR — "LLM'e düş" çözümü büyük ölçüde kablosuz-motor.** Deterministik yolun reddettiği vakaları LLM ne biliyor (prompt kısıt-kör), ne öğreniyor (golden blob + VQR ayrık), ne güvenle seçiyor (self-consistency yarı-sahte), ne güvenle çalıştırıyor (serbest-SQL always_filter/fail-closed baypas). R1-R3'ün "reddet ve devret" stratejisi bu turda temelinden sorgulandı.

---

## (a) UZLAŞILAR (yüksek güven, orkestratör doğruladı)

### U1 — [P0 GÜVENLİK+DOĞRULUK] SERBEST-SQL always_filter'ı ve R1 fail-closed'unu BAYPAS ediyor (Opus + Sonnet, orkestratör KANITLADI)
`_inject_always_filter` YALNIZ `cube_sql:379`'da çağrılıyor. `query()` (wren_service.py:498) ve `dry_plan()` (477) SADECE `guard_sql` (SELECT-only) çağırıyor — orkestratör satır 497-508 ve 475-479'u okuyarak DOĞRULADI, always_filter enjeksiyonu YOK. Serbest-SQL (ask.py:1169-1170) bu korumasız yoldan geçiyor:
- LLM "toplam ciro" için `SELECT SUM(tutar) FROM fatura` yazarsa `CANCELLED=0` EKLENMEZ → iptal faturaları toplama dahil (iptal-kaydı sızıntısı).
- Bu tam olarak R1'in fail-closed düzeltmesinin (wren_service.py:408-423) önlediği durum — ama fail-closed yalnız cube_sql'de tetiklenir. **R1 düzeltmesi serbest-SQL'de yapısal olarak baypas = güvenlik + doğruluk REGRESYONU.** Ve R1-R3 boyunca "LLM'e düş" denen her vaka bu korumasız yola gidiyor.

### U2 — [P0] _schema_prompt cube/semi_additive/always_filter/units'i LLM'e HİÇ geçirmiyor (Sonnet + Haiku)
`_schema_prompt` (llm.py:49-73) yalnız `models` + `relationships` okuyor. `schema()` çıktısındaki (wren_service.py:75-210) `cubes, measures, semi_additive (177), non_additive (184), always_filter (188), units (169), lower_is_better (160)` — HİÇBİRİ prompt'a girmiyor. Sonuç: LLM "bakiye"yi düz SUM'lar (semi-additive bilmez — R1'in önlediği net-hareket tuzağını LLM ÜRETİR), iptal filtrelemez (always_filter bilmez). **R1/R3'ün "LLM as-of/negasyon yazar" varsayımı BOŞ — LLM'e bu bilgi hiç verilmiyor.** `build_catalog` (cube_router.py) da bu alanları katalog metnine yazmıyor.

### U3 — [P0/P1] golden TEK BLOB, retrieval YOK; VQR golden'a beslenmiyor (Haiku)
`golden_sql = _load_knowledge("sql")` (wren_service.py:209) → `_load_knowledge` (304-319) tüm `*.md`'yi `"\n\n".join` ile ham birleştiriyor. Retrieval/embedding/ranking YOK. Her soruya AYNI blob prompt sonuna ekleniyor (llm.py:107-110) → alakasız örnekler bağlam kirletir, lost-in-middle. VQR doğrulanmış çiftler yalnız cube-select yoluna few-shot besleniyor (ask.py:1035); serbest-SQL (ask.py:1150) VQR few-shot ALMIYOR, yalnız near_exact replay (607). Sistem doğrulanmış bilgiyi LLM'e öğretmiyor. golden'da LAG örneği var ama negasyon (neq) YOK, semi-additive as-of talimatı YOK → R1-R3 vakalarını kapsamıyor.

### U4 — [P0] SELF-CONSISTENCY yarı-SAHTE: OpenAI-compat'ta temperature=0 (Fable, orkestratör KANITLADI)
`OpenAICompatibleSqlGenerator` `temperature: 0` HARDCODED (llm.py:231 — orkestratör doğruladı). `_select_consistent` (ask.py:248-250) `one(_i)` prompt'a varyasyon/seed EKLEMİYOR (`_i` kullanılmıyor). temperature=0 + özdeş prompt → k örnek ÖZDEŞ → `len(votes)==1` → agreement=1.0 HER ZAMAN → uyuşmazlık-chip makinesi (ask.py:1044+) gemini/groq/xai/ollama'da ÖLÜ KOD. **3× para ödenip 1× bilgi alınıyor.** Yalnız Anthropic'te (temperature set edilmemiş → API varsayılan ~1.0) varyans gerçek. Failover heterojen oy havuzu üretebilir (bir kısmı varyanslı, bir kısmı deterministik) → uyum oranı yorumlanamaz.

### U5 — [P1] TUTARLI-YANLIŞ oylamayla yakalanmıyor (Fable)
Oylama yalnız `_canon_cq` eşitliğine bakar; sistematik hata (morfoloji tuzağıyla "bakiye"→yanlış cube) k kez AYNI yanlışı verir → agreement=1.0 → tam güvenle sunulur. Oylama varyansı ölçer, bias'ı değil. Docstring "Uyuşma = doğruluk sinyali" (ask.py:242) YANLIŞ. Ek kusur: `agreement = len(best)/len(cands)` — hatalı örnekler `cands`'ı küçültür → 1 örnek sağ kalırsa agreement=1.0 (tek-örnek %100 sahte uyum, orkestratör doğruladı).

---

## (b) ÇELİŞKİLER & KİM HAKLI
Bu tur ortogonal facet'ler; doğrudan çelişki yok. Nüans:
- Fable "Anthropic temperature belirsiz" (llm.py:186-191 set edilmemiş) — orkestratör doğruladı: llm.py'de tek `temperature` occurrence satır 231 (OpenAI-compat), Anthropic çağrısında yok → API varsayılanına örtük bağımlılık (P2, kırılgan ama bugün çalışıyor).
- Haiku'nun VQR→golden ayrıklığı ile Fable'ın self-consistency asimetrisi AYNI kök: doğrulanmış-bilgi ve güven-sinyali serbest-SQL yoluna hiç ulaşmıyor. Örtüşme, çelişki değil.

---

## (c) HER MODELİN ÖZGÜN BULGUSU
- **Opus:** serbest-SQL güvenlik katman tablosu (guard✓ / always_filter✗ / fail-closed✗ / dialect✗ / tablo-allowlist✗ / RLAC-CLAC-PII✗); guard_sql tablo-allowlist YAPMIYOR → UNION sızıntısı (`SELECT a FROM cube UNION SELECT parola FROM users` guard'dan geçer); tenant izolasyonu per-service/connection (SQL RLS değil) — makul ama tek-tenant DB içinde satır/kolon RLAC/CLAC/PII maskeleme HİÇ YOK ("tenant" ask.py'de yalnız log alanı); self-repair guard bütünlüğü TEMİZ (her 3-tur SQL guard'lanıyor — adil pay).
- **Sonnet:** schema()→prompt bilgi-kaybı tablosu (10 alan, hangisi düşüyor); red-sebebi LLM'e sinyallenmiyor (route None→ask.py:1150 çıplak soru+şema, "neden reddettim" yok → LLM aynı tuzağa düşer); build_catalog kısıt-kör.
- **Fable:** temperature=0 sahte-güven (U4) + tek-örnek %100 uyum + LLM-yolu güven-kontrol haritası (select_cube k=3 / refine tek-atış / generate_sql tek-atış / repair tek-atış — en riskli yol en az kontrollü) + maliyet (3× token, cache yok) + `_last` yarış durumu provenance bozar.
- **Haiku:** golden blob vs retrieval (U3) + VQR ayrıklığı + golden'ın R1-R3 desenlerini kapsamadığı (LAG var, neq yok, as-of talimatı yok).

---

## (d) "MÜKEMMEL SENARYO" ÖNERİSİ
"LLM'e düş" gerçek bir güvenlik ağı olmalı: (1) serbest-SQL de always_filter/fail-closed/dialect/tablo-allowlist'ten GEÇMELİ (query/dry_plan'da AST-tabanlı tablo çıkarımı + her tabloya always_filter enjeksiyonu, fail-closed); (2) prompt cube/semi_additive/always_filter/units + RED-SEBEBİNİ bilmeli; (3) golden embedding-retrieval + VQR few-shot serbest-SQL'e de; (4) self-consistency gerçek varyansla (T>0 örnekleme) veya temp=0'da k=1'e düş (maliyet kes) + tutarlı-yanlışı ayrı doğrulayıcıyla yakala (soru↔tablo çapraz kontrol). Kısaca: deterministik yoldaki HER koruma serbest-SQL yolunda da bulunmalı — güvenlik iki yolda simetrik olmalı.

---

## (e) SOMUT AKSİYON MADDELERİ (önem-sıralı)

1. **[P0 GÜVENLİK] Serbest-SQL'e always_filter + fail-closed** — `query()`/`dry_plan()` (wren_service.py:497/475) SQL'i sqlglot ile parse edip dokunulan HER base tablo/cube'a always_filter enjekte etsin; başarısızsa fail-closed reddetsin. R1 düzeltmesinin serbest-SQL baypasını kapatır. **En kritik — güvenlik+doğruluk regresyonu.**
2. **[P0] _schema_prompt + build_catalog kısıt-farkındalığı** — semi_additive/always_filter/units/non_additive'i prompt'a ve kataloğa ekle. LLM "bakiye"yi as-of, iptal'i filtreli yazsın. R1/R3 "LLM devralsın" çözümünü GERÇEK yapar.
3. **[P0] Red-sebebini LLM'e sinyalle** — route None sebebini (as-of gerekli / negasyon / gran+semi) `_build_system`'e ek yönerge olarak geçir (ask.py:1150 öncesi). LLM aynı tuzağa düşmesin.
4. **[P0] guard_sql tablo-allowlist** — sqlglot AST'de tüm `exp.Table` düğümlerini MDL cube/model allowlist'ine karşı doğrula (UNION/subquery dahil). UNION sızıntısını kapatır.
5. **[P0] self-consistency sahte-güven** — OpenAI-compat'ta consistency örneklemesinde temperature ayrılabilir yap (T~0.7) VEYA temp=0 sağlayıcıda k=1'e düş (3× maliyeti kes); `agreement = len(best)/k` (hatalı örnek=uyumsuz oy), `len(cands)<2` → "güven bilinmiyor".
6. **[P1] golden embedding-retrieval + VQR few-shot serbest-SQL'e** — `_load_knowledge` blob yerine top-k retrieval (VQR embedding modelini reuse); VQR few_shot_block'u ask.py:1150 serbest-SQL çağrısına da ekle.
7. **[P1] Tutarlı-yanlış doğrulayıcı** — agreement=1.0 vakalarını trace/Query-Contract'a logla; serbest-SQL'de dokunulan tabloları soru konusuyla çapraz doğrula.
8. **[P1] RLAC/CLAC/PII maskeleme** — MDL kolon metadata'sına `pii/masked` bayrağı; guard/dry_plan maskeli kolona SELECT'i reddetsin/sarsın. Tek-tenant DB içi erişim kontrolü boşluğu.
9. **[P1] Serbest-SQL dialect transpile** — `_dialect_sql` serbest-SQL'e de (mssql/oracle tenant'ında ham DuckDB-varsayımlı SQL kırılır/yanlış semantik).
10. **[P2] Anthropic temperature'ı açıkça set et** (llm.py:186); `_last` yarış durumu provenance.

---

## (f) SONRAKİ TUR (zorluk artışı)
**005 — "Çok-kiracılık runtime & tenant izolasyonu: VQR/schedules/synonym-overlay çok-şirkette güvenli ve canlı mı":** R4 tenant izolasyonunun per-service/connection olduğunu (SQL RLS değil) ve tek-tenant içi RLAC/CLAC/PII'nin yokluğunu ortaya çıkardı. Şimdi çok-kiracılık RUNTIME'ını denetle: (1) VQR deposu tenant-scope'lu mu yoksa bir tenant'ın doğrulanmış çifti başka tenant'a replay/few-shot sızıyor mu (near_exact + few_shot_block tenant filtresi); (2) schedules/threshold-alerts (ADR-0011) çok-şirkette hangi TenantContext'te koşuyor, cron bir şirketin bağlantısıyla başka şirketin verisini mi sorguluyor; (3) synonym-overlay (ADR-0018 katman-3, company_slug scope) tenant sızıntısı; (4) bağlantı havuzu/WrenService cache çok-şirkette paylaşımı — bir tenant'ın schema_cache'i başka tenant'a; (5) company_registry on-demand compose/build yarış durumları. Kısaca: R4'ün "izolasyon connection düzeyinde" bulgusunu runtime'da stres-test et — hangi paylaşılan state tenant sınırını deliyor.
