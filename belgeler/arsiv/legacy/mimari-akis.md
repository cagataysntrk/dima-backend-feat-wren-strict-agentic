# dima — Normatif akış ve mevcut durum (2026-07-20, kod-doğrulanmış)

> "Bu iş nasıl olmalı?" sorusunun tek-sayfa cevabı. Mevcut durum `ask.py@6056cd2`
> üzerinden satır referanslıdır; hedef, ADR-0004/0007/0008'in birleşimidir.
>
> **Kapsam notu (güncel 2026-07-27):** bu sayfa ana NL→SQL/cube ask akışını anlatır. Sonradan
> eklenen alt-sistemler ayrı ADR'lerde: chat persistence (ADR-0007), canlı klon/sync (ADR-0017
> §9), soft-delete (ADR-0019), loglama/observability (ADR-0020), Excel/CSV yükleme (ADR-0021),
> çıktı yorumlama (ADR-0022).

## 1. HEDEF: Üç katman, net sorumluluk

```
┌─ 1. NİYET & SLOTLAR (anlama) ──────────────────────────────────────────────┐
│ Sahibi: LLM (gemini→groq failover) — ADR-0008 K1                            │
│ Girdi:  mesaj + mevcut CubeQuery (bağlam) + cube kataloğu (+ ileride recall)│
│ Çıktı:  YAPISAL karar JSON'u — asla SQL, asla tarih aritmetiği:             │
│   {action: new|edit|unavailable|meta|view,                                  │
│    cube_query?: {...},           ← yalnız katalogdaki ölçü/boyut/filtre     │
│    period_expr?: "1 ocak 31 mart arası",  ← İFADE, hesap değil (K3)         │
│    view?: chart|table|...:param}                                            │
│ Hızlı-yollar (LLM'i atlar, ADR-0008 K2 disipliniyle sınırlı):               │
│   chip metinleri · no-op · synonyms-metadata eşleşmesi · meta/selamlama     │
└──────────────────────────────┬──────────────────────────────────────────────┘
┌─ 2. DOĞRULAMA & HESAP (deterministik çekirdek) ─────────────────────────────┐
│ Sahibi: Python + Wren motoru                                                │
│ parse_cube_query → katalog doğrulaması (halüsinasyon yapısal imkânsız)      │
│ period_expr → date_filters (Python takvim aritmetiği; çözülmezse SOR)       │
│ Eksik zorunlu slot (dönem) → clarification chip'leri (ADR-0007 K3)          │
│ cube_query_to_sql → SQL'i MOTOR üretir → dry-plan → çalıştır                │
└──────────────────────────────┬──────────────────────────────────────────────┘
┌─ 3. SUNUM & KONTROL (client) ───────────────────────────────────────────────┐
│ Yorum chip'leri = CubeQuery'nin görünür hali; her slot düzenlenebilir       │
│ (/cube, deterministik). Grafik seçimi veri şeklinden; view_hint override.   │
│ Bağlam görünür + × ile sıfırlanır. source/trace/log her yanıtta.            │
└─────────────────────────────────────────────────────────────────────────────┘
```

İlke özeti: **LLM anlar (yapısal, kısıtlı) · Python doğrular+hesaplar · Motor sayıyı
üretir · Chip'ler kullanıcıya son sözü verir.** Serbest SQL yalnız cube-dışı sorular
için son çaredir (LAG/listeler), golden SQL + dry-plan + repair ile.

## 2. MEVCUT durum (ask.py akışı, doğrulanmış)

| Sıra | Adım | Satır | Katman |
|---|---|---|---|
| M | meta/ürün → yardım+chip | 242 | hızlı-yol ✓ |
| — | bağlam kopması (farklı cube → yeni) | 254 | hızlı-yol ✓ |
| — | görünüm isteği (+facet:param) | 266/309 | hızlı-yol ✓ |
| — | dönem chip'i (bu ay/tümü/ay adı) | 279 | chip ✓ |
| R1 | deterministik refine (gran/boyut/değer/tarih) | 295 | hızlı-yol ✓ |
| R2 | LLM refine (edit/unavailable/new) + tarih ezme | 318-358 | **LLM ✓ ama protokol eski** |
| 0 | route (synonyms-metadata) + dönem clarify | 360 | hızlı-yol ✓ |
| 0.5 | LLM select_cube + clarify | 385 | LLM ✓ |
| — | konuşmada çıplak parça → dürüst not | 400 | guard ✓ |
| 1-3 | serbest SQL + dry-plan + repair + kural yedeği | 405-457 | son çare ✓ |

Güvence: 48 golden test · trace+JSONL log · provenance rozetleri · yorum chip'leri.

**Sağlık:** Akış tutarlı ve test altında; "kaos" yok. Ama iki gerçek zaaf var:
(a) anlamanın merkezi hâlâ hızlı-yol öncelikli — R1 bilinmeyen içeriği fark edemez
(no-op yutma riski sınırlandı ama sıfır değil); (b) LLM protokolü eski: tek "edit"
JSON'u, period_expr yok, few-shot/recall yok.

## 3. ADR-0008 uygulama durumu (dürüst)

| Karar | Durum |
|---|---|
| K1 LLM birincil anlama | **KISMEN** — LLM refine/select var ama hızlı-yol R1 hâlâ önde ve protokol zayıf |
| K2 disiplinli terfi | ✓ işaret kondu; bu oturumda yeni keyword eklenmedi (chip/tarih hariç — muaf) |
| K3 tarih: LLM anlamaz-yazar, Python hesaplar | **KISMEN** — Python q'dan ezme var; `period_expr` yapısal protokolü YOK |
| K4 gemini→groq birincil | ✓ (zaten auto zincirin başı) |
| K5 eval+chip güvenlik ağı | ✓ (48 test, yorum çubuğu) |
| K6 memory recall | **YOK** (A#4 bekliyor) |

## 4. Kalan iş — sıralı (LLM bağlama çekirdeği)

1. **Refine/select protokol yenileme:** tek prompt → yapısal karar (action + cube_query
   + period_expr + view); tarih yazmak YASAK talimatı; ask.py'de period_expr →
   date_filters, çözülmezse dönem chip'i. R1'i "tam kapsanan mesaj" koşuluna bağla
   (kapsanmayan içerik varsa LLM'e düş — yutma sıfırlanır).
2. **A#4 memory recall:** `wren memory` (LanceDB, çokdilli) — onaylanan soru→CubeQuery
   çiftleri few-shot; `store_query` geri-besleme.
3. **Eval genişletme:** LLM'li yollar için işaretli eval (kayıtlı LLM yanıtlarıyla).
4. **A#2 kompozisyon** (packs/companies/composer) — dikey ölçeklenme.
5. A#5 temizlik: `RuleBasedSqlGenerator` demo-only izolasyonu; `"tarih"` hardcode →
   `time_dimensions[0]` kalanları.
