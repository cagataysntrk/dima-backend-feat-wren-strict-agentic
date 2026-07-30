# Panel Senaryo Defteri (tekrar önleme + durum)

Her satır bir derin 4-model karşılaştırma turu. TEKRAR ETME — yeni açı/zorluk kat.

| # | Senaryo | Konu ekseni | Tarih | Durum | Bulgu dosyası |
|---|---------|-------------|-------|-------|---------------|
| 001 | Düzeltmenin kendi regresyonu: semi-additive as-of + sayısal hayalet-filtre + always_filter fail-closed | Cube derinlik + son-72h + NL doğruluk | 2026-07-24 | tamam | findings/001-semi-additive-fix-regression.md |
| 002 | Continuation state-machine route-paritesi: in_convo yolları semi-additive/entity-limit/coverage korumalarını taşıyor mu | Çok-kiracılık runtime + konuşma-durumu geçişleri | 2026-07-24 | tamam | findings/002-continuation-route-parity.md |
| 003 | Niyet-sınıflandırma mimarisi: deterministik-önce yönlendirme yanlış-pozitif dal seçimi (kapsam kapısı substring körlüğü + negasyon eki yutma + ifade-uzayı boşluğu) | Sistem tasarımı + deterministik-önce yönlendirme | 2026-07-24 | tamam | findings/003-intent-signature-routing-arch.md |
| 004 | LLM/golden güvenlik ağı denetimi: deterministik-red sonrası LLM doğru+güvenli mi (golden retrieval, prompt kısıtları, self-consistency, serbest-SQL güvenlik katmanı) | WrenAI kullanım kapasitesi + güvenlik + LLM doğruluk | 2026-07-24 | tamam | findings/004-llm-golden-safety-net.md |
| 005 | Çok-kiracılık runtime & tenant izolasyonu: VQR/schedules/synonym-overlay/connection-cache çok-şirkette güvenli+canlı mı (paylaşılan state tenant sınırını deliyor mu) | Çok-kiracılık runtime + güvenlik (RLS/RLAC) | 2026-07-24 | tamam | findings/005-multitenant-runtime-isolation.md |
| 006 | (sıradaki) Onboarding/semantik keşif otomasyonu doğruluğu: yeni tenant pack'i canlı DB introspection'dan ne kadar güvenilir türetiliyor (yanlış tip/kardinalite, otomatik metadata, enum mining, pack-lint boşlukları) | Onboarding otomasyonu + cube doğruluk | — | planlandı | — |

## Kapanan alt-konular (tekrar etme)
- semi-additive as-of route() mantığı (001'de derinlemesine — ama continuation yolları AÇIK)
- _value_token_hit sayısal dal / 14-char pencere (001'de — ordinal ve pencere düzeltmeleri aksiyon)
- always_filter fail-closed enjeksiyon sırası (001'de — dialect-guard AÇIK)
- measure↔semi_additive namespace (001'de doğrulandı: TEMİZ, tekrar etme)

## Kapanan alt-konular (002)
- continuation semi-additive/coverage/entity_limit paritesi (002'de derinlemesine)
- deterministic_refine deepcopy davranışı (002'de doğrulandı: DEEP, güvenli — tekrar etme)
- niyet-operatörü STOP_STEMS körlüğü (002'de kök-neden — 003'te MİMARİ olarak açılacak)
- VQR replay coverage/semi boşluğu (002'de — aksiyon 7)

## Kapanan alt-konular (003)
- kapsam kapısı substring körlüğü (791 `k in w`) — canlı sessiz-yanlış, aksiyon 1
- negasyon eki yutma (-sIz/-mAyAn) — aksiyon 1-2
- STOP_STEMS kısa-prefix (793) — aksiyon 3
- binary route() güven-skorsuzluğu + belirsizlik-chip route()-içi yokluğu — aksiyon 5
- ÜÇLÜ ifade boşluğu + Rust 12-op vs Python 4-op fork alt-kümesi (Opus taç bulgu)

## Kapanan alt-konular (004)
- serbest-SQL always_filter/fail-closed baypası (güvenlik regresyonu) — aksiyon 1
- _schema_prompt/build_catalog kısıt-körlüğü — aksiyon 2
- golden blob (retrieval yok) + VQR ayrıklığı — aksiyon 6
- self-consistency temp=0 sahte-güven — aksiyon 5
- guard_sql tablo-allowlist yokluğu / RLAC-CLAC-PII yokluğu — aksiyon 4,8

## Kapanan alt-konular (005)
- schedules cross-tenant motor kaçağı (state.wren) — aksiyon 1 (KVKK)
- registry compose+build lock-dışı + compose in-place rmtree — aksiyon 2
- VQR tenant-kör retrieval + yalnız-default çalışma — aksiyon 5 (sızıntı YOK bugün, latent)
- overlay scope / IDOR / require_company — DOĞRULANDI güvenli (Ç2), tekrar etme
- schema() lazy-fill kilitsiz / invalidate stale / default-vs-registry çift-yol — aksiyon 3,4,6

## Açık iplikler (ileride tur olabilir)
- cube derleyici (wren-core cube.rs) additive/window semantiği hiç yok — derin bir "kablosuz motor envanteri" turu
- LLM golden retrieval yok (tek blob) — LLM yolu doğruluk turu
- multi-tenant metadata asimetrisi (always_filter, semi_additive tenant'lar arası) — tutarlılık turu
- pack-lint kapsamı: hangi sessiz-yanlış kombinasyonları lint'siz
