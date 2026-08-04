# dima-backend — CLAUDE.md

> 🔴 **AKTİF OPERASYON: DİMA v1 yol haritası.** Bir geliştirme isteği geldiğinde **önce
> şunları oku** — bağlam sıfırlansa bile operasyon buradan devam eder:
> 1. **`OPERASYON.md`** (repo kökü) — kural seti, döngü adımları, test kapısı, öz-denetim
> 2. **`OPERASYON-DURUM.md`** (repo kökü) — **nerede kaldık**, açık borçlar, ölçüm tabanı
> 3. **`~/.claude/plans/DIMA-V1-YOL-HARITASI.md`** — ne yapılacak (**5256** satır @`e22b2b9`
>    · `wc -l`; §10'daki bağlayıcı sıra)
>
> *Bu üçü + `MIMARI.md` operasyonun tam durumunu taşır; sohbet geçmişine ihtiyaç yoktur.*
>
> ✅ **DENETİM AJANLARI KULLANILIR** — her faz commit'inden sonra **üç ajan paralel**
> (`OPERASYON.md §7`, görev metinleri `OPERASYON-DENETIM.md`): **A** plan · **B** bütünlük ·
> **C** canlı kullanıcı. *(Bir ara «ajanlar sohbeti sildi» diye yasaklanmıştı; teşhis
> **yanlış** çıktı — sebep başarısız bir **daemon yükseltmesiydi**, ajanlar değil.)*

> **Mimari otorite `backend/MIMARI.md`'dir.** Bu dosya kısa bir kural indeksidir. Mimari bir
> soruda (cevaplama merdiveni, semantik katman, JOIN'in nerede oluştuğu, ne YAPILMAYACAĞI,
> bilinen kusurlar, ADR listesi) **önce `MIMARI.md`'yi oku** — çelişkide o kazanır.
> `HANDOFF_DOCS/*` tarihsel kayıttır; `Dima-0-100-Gorev-Takip-Dosyasi (2).md` ürün şartnamesidir,
> mimari otorite değildir.

## Rol
`dima-frontend-demo` ile `dima-wrenai` (Wren semantik SQL motoru) arasındaki **ince HTTP köprüsü**.
İş mantığı minimum: SQL üretimi (LLM), doğrulama (motor), çalıştırma (motor), guard'lar.
Ağır semantik iş `dima-wrenai` motorunda; UI `dima-frontend-demo`'de kalır.

## Teknoloji
- Python 3.11+ · FastAPI · Uvicorn
- `wren.engine.WrenEngine` (in-process; subprocess YOK)
- NL→SQL sağlayıcıları (pluggable,
  `DIMA_LLM_PROVIDER=auto|anthropic|xai|gemini|groq|ollama|rule`):
  Anthropic · xAI/Gemini/Groq/Ollama (OpenAI-uyumlu tek istemci) · **kural-tabanlı (anahtarsız)**
  fallback. `auto` → `FailoverSqlGenerator`, sıra `anthropic → gemini → groq → xai → ollama`,
  hepsi başarısızsa `rule`. Intent-JSON için ayrı/ucuz model (`*_select_model`).
- pydantic-settings (env, `DIMA_` öneki)

## Yapı
```
app/
├── main.py            # FastAPI app + lifespan (WrenService/LLM app.state'e; 60sn scheduler+materializer döngüsü)
├── config.py          # Settings (DIMA_ env), path çözümleme
├── schemas.py         # request/response modelleri
├── wren_service.py    # WrenEngine sarmalayıcı + SQL guard (SELECT-only)
├── llm.py             # NL→SQL sağlayıcıları (Anthropic/Groq/Ollama/kural-tabanlı), MDL grounding
├── auth/              # public plane auth: login/refresh/logout/me + require()/require_company
├── features.py        # bayrak çözümü: global YAML (packs/features.yml) ⊕ sektör ⊕ şirket ⊕ DB override
├── materialize.py     # TenantConfig → company.yml materializer (ADR-0016)
├── interpret.py       # evrensel çıktı yorumu (deterministik, flag'li — ADR-0022)
├── dataset.py         # chat-scoped Excel/CSV → oturum DuckDB + oto-cube (ADR-0021)
├── logging_setup.py   # system/app logger (ADR-0020 — sessiz yutma yok)
├── cube_router.py     # SIFIR-LLM deterministik NL→CubeQuery (~1763 satır; içerik YAML'da)
├── viz.py/report.py/viz_email.py  # deterministik grafik+rapor kararı (ADR-0024)
├── drill.py           # dallı kök-neden: saf yorum fonksiyonları + CubeQuery dönüşümleri
├── vqr.py             # doğrulanmış-soru deposu (embedder + leksik yedek)
├── kpi.py/statements.py/yoy.py    # çapraz-cube KPI · gelir tablosu/bilanço · dönemsel kıyas
├── contracts.py       # Query Contract (ADR-0010)  ·  pii.py  # maskeleme (tek çıkış noktası)
├── channels.py        # bildirim/teslim kanalları (ADR-0011)
├── db_introspect.py/mdl_writer.py # canlı şema keşfi → taslak MDL (ADR-0017)
├── value_index.py/archetypes.py/synonyms  # bulanık eşleşme + sinonim katmanları (ADR-0018)
└── routers/           # health(+features), query, ask(+cube/verify/upload/drill/jobs),
                       #   contracts, schedules, conversations (ADR-0007/0019),
                       #   connections (bağlantı sihirbazı), dashboards, measures (terfi), stats
control_plane/         # auth bounded-context: SQLModel entity'ler (Tenant/User/… + CloneJob,
                       # SyncState, Conversation(Message), InteractionLog), authorize() matrisi,
                       # JWT/TOTP/rate-limit, audit, crypto (AES-256-GCM cred, DIMA_CRED_KEK), Alembic
admin_app/             # dima-admin-api (AYRI süreç, Wren'siz): /sadmin/* + clone/ (datasource-bağımsız
                       #   clone/sync motoru — ADR-0017 §9); interactions viewer (ADR-0020)
admin-dev/             # admin-api localtld başlatıcısı (pnpm dev → admin-api.dima.localtld)
migrations/            # Alembic (control-plane şeması; Postgres'te sahibi admin-api)
demo/                  # kendi kendine yeten DuckDB boyahane (tekstil) + OEE demosu
│  ├── packs/kaynak/   # kaynak-sistem pack'leri (ADR-0017): mikro-v16 (modeller pack'te),
│  │                   #   logo-3 (şablonlu — modeller şirkete üretilir), netsis;
│  │                   #   sektor/ = kesişim katmanı
│  ├── packs/modul/    # ERP-BAĞIMSIZ dikeyler: oee, bakim, ik, enerji, kpi, turev
│  ├── packs/sektor/   # boyahane (cube'lu), geri-donusum/kumas-ticareti/tarim-ticareti (yalnız
│  │                   #   terminoloji: cube_synonyms.yml + knowledge/rules)
│  └── companies/atiksan, gulteks  # lab fixture'ları: mssql, lab/ SQL Server'ına bağlanır
lab/                   # müşteri DB laboratuvarı: Docker mssql + restore/import/envanter
```

Compose katman sırası (en spesifik kazanır, ADR-0005+0017):
`kaynak → modül → sektör → kesişim(kaynak∧sektör) → şirket`. Cube ifadeleri
DuckDB/ANSI yazılır; DuckDB-dışı datasource'ta `WrenService._dialect_sql` hedef
lehçeye çevirir (DATETRUNC, ordinal genişletme — testleri `test_kaynak_compose.py`).

## Komutlar
```bash
uvicorn app.main:app --reload --port 8000   # dev
```

## Değişmezler (kurallar)
- **Yalnızca read-only**: guard `SELECT/WITH` dışını reddeder; asla DDL/DML çalıştırma.
- **LLM önerir, motor doğrular**: her üretilen SQL çalıştırılmadan önce `dry_plan`'dan geçer.
- **Sırlar env'de**: DB kimlik bilgileri ve API key asla commit edilmez (`.env` gitignore'da).
- **MDL kaynağı `dima-wrenai` projesidir**: şema `target/mdl.json`'dan okunur; elle uydurma yok.
- **Auth HER ZAMAN zorunlu** — kapatma bayrağı YOKTUR (dev bypass yok): korunan her uç
  geçerli Bearer access token ister; refresh HTTP-only cookie'de (rotation + reuse).
  Ortak kod `control_plane/` (ADR-0015 K1); public `app/auth/`, admin `admin_app/` —
  admin plane AYRI JWT secret çiftiyle imzalar. saka-standards `02`/`08` + ADR-0014/0015.
- **Rol matrisi uykuda**: authorize() viewer<analyst<admin<owner tanımlar ve testlidir,
  ama üründe bu fazda yalnız `owner` kullanılır (diğer role_key'ler admin API'de 400).
  UI izinleri login//auth/me `permissions` listesinden okur — matrisi frontend'e KOPYALAMA.
- **Tenant-RLS**: token'daki tenant slug (`tsl`) yüklü şirketle eşleşmeli; contracts/
  schedules/bildirimler tenant-damgalı yazılır ve okumada filtrelenir.
- **Bayraklar ≠ yetki**: feature flag rollout/görünürlük içindir (DB override, en spesifik
  kazanır); güvenlik sınırı her zaman authorize()'dır — bayrak onu gevşetemez.
- **DB→dosya tek yönlü** (ADR-0016): TenantConfig satırı olan tenant'ın company.yml'i
  TÜRETİLMİŞTİR; elle düzenleme materializer'da ezilir. Kaynak = control-plane DB.

## Test kapısı (ölçüldü — 3 Ağustos 2026)

Tam kapı **~15 dk**: süit **2068** test @`e22b2b9` (`pytest -q --collect-only`) ≈8,5 dk · `eval` ≈1,5 dk · `nl_corpus` ≈3-4 dk ·
`konusma_senaryolari` ≈1,5 dk. Fixture'lar zaten `session` kapsamlı, `pytest-xdist` imajda
yok — süre **gerçek iştir**; israf faz başına 2-3 kez koşturmaktı.

Tek araç: **`lab/kapi.py`** (iki kademe, tek sahip).

- **Geliştirme sırasında:** `python lab/kapi.py --hizli --degisen <değişen dosyalar>` —
  değişen modüle bağımlı testler + çekirdek duman (~15-40 sn). **Bu bir KAPI DEĞİL,
  sinyaldir**: seçim `import` bağımlılığına bakar, davranışa dayanan bir test kaçabilir;
  araç her koşumda kapsanmayan dosya sayısını YAZAR (sessiz kırpma yok).
- **DEMET sonunda (4-6 madde), TEK SEFER:** `python lab/kapi.py --tam` — süit + `eval` +
  korpus + senaryo, **tek konteynerde ardışık**. Kapı budur. *(Eskiden «her faz sonunda»
  yazıyordu ve uygulamada **madde başına** koşuluyordu; ölçüldü — sürenin %75'i kapıda
  değil, madde başına tekrarlanan 10 adımlık döngüdeydi.)*
- **Demet içinde ara `--tam` YOK.** *"Bir de şuna bakayım"* diye tam süit koşturma.
- **Kapsam KIRPILMAZ.** Hız tekrarı azaltarak kazanılır, kapıyı gevşeterek değil.
- **İki test konteyneri ASLA paralel koşmaz** (compose kilidi `metadata.yml`'de çakışır) —
  bu kural hız için bile esnetilmez.
- 🔴 **KOŞUM HİJYENİ:** kapı `--rm` ile değil **`-d` ile** koşturulur, `--name` verilir,
  `docker wait` + `docker logs` ile okunur, sonda `docker rm -f` ile kapatılır.
  Ölçüldü: `--rm` konteyner çıkınca **kütüğü siler** ve kabuk sarmalayıcısı ölürse özet
  **tamamen kaybolur** — bu operasyonda **iki kapı koşumunun özeti böyle kayboldu**.
- 🔴 **Kapı koşarken repoya YAZILMAZ** — mount canlıdır; süit bitmiş olsa bile sonraki
  aşamalar yeni kodu import eder ve ölçüm **karışır**. (Bu operasyonda bir kez yaşandı,
  koşum iptal edilip temiz tekrarlandı.)
- **DEMET disiplini** (`OPERASYON.md §3`): **commit ≠ kapı**. Her madde kendi commit'ini
  alır (seviye 0+1); **tam kapı demet sonunda bir kez** koşar. `cube_router · interpret ·
  answer · followup · routers/ask · contribution · demo/packs` dosyalarına dokunan madde
  **demete girmez**, kendi kapısını hemen koşar.

## Standartlar
Kök `saka-standards` submodule'ü bağlayıcıdır (TypeScript tarafı için; Python tarafında
strict typing + ruff). Commit mesajlarında Claude footer KULLANILMAZ (saka standardı).
