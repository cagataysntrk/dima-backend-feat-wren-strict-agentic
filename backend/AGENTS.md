# DIMA V2 — GELİŞTİRİCİ / AJAN ÇALIŞMA SÖZLEŞMESİ

## DAY 6.5 RUNTIME-KERNEL / SUBSTRATE OVERRIDE — 2026-09-22

> Active phase-local authority: `belgeler/plan/DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md`.
>
> Architecture path only: `STANDARD | RESEARCH`.
> `STANDARD_DIRECT` / `STANDARD_BUILDER` are Standard outcomes/telemetry, not separate engines or authorities.
>
> D65-E3A-R **GREEN**: `app/v2/agent_runtime.py` now provides the minimal generic `BoundedAgentRuntimeKernel`; StandardBuilder consumes it. Focused gate `35693039369` = 22/22 PASS; runtime-aligned family closure `35693146320` = 94/94 PASS.
> Kernel owns only counters/budgets/observations/action+state fingerprints/duplicate prevention/terminal/no-progress/telemetry and MUST NOT import or know `AcceptedTurnContract`, `UserObligationLedger`, `ResearchDirective`, Evidence verification, semantic truth, join/query/numeric truth or completion truth.
>
> Do NOT refactor `manager_loop.py`, `manager_runtime.py`, `manager_tools.py`, `manager_preacceptance.py` into the kernel during Day 6.5.
> Existing Research Manager stays as-is.
>
> StandardBuilder/E4/E5 remain NO-ROLLBACK; StandardBuilder now consumes the generic kernel. Next gate is workers=1 focused live architecture validation.
>
> Wren is current incumbent analytics substrate. Metabase is architecture reference + post-engineering-closure challenger only.
> Do NOT add Metabase dependency/code/production query path now. Wren+Metabase equal production truth engines is STOP-THE-LINE.
>
> After engineering closure and DEV80: run D65-X isolated Wren-vs-Metabase substrate bake-off before Validation50/Hidden50 certification.
>
> Family closure history: first run `35691397377` = 87/88 with one `EVAL_ORACLE`; oracle sync sonrası `35691982389` = **88/88 PASS**. Do not reinterpret the first failure as semantic regression.


> **Kapsam:** `feat/ask-v2-mvp` ve bu branch'ten türeyen V2 geliştirme dalları.
> **Amaç:** Dima V2'yi mühürlü nihai rapor ve yol haritasına göre hızlı, izlenebilir ve
> eski semantic-front-door hatalarını tekrar etmeyecek biçimde geliştirmek.

## DAY 6.5 CURRENT CLOSURE OVERRIDE — 2026-09-22

> Bu bölüm eski Day 6.5 hazırlık/validation maddelerinin üzerinde okunur.
>
> Aktif phase-local authority:
> 1. `belgeler/plan/DIMA_DAY6_5_ENGINEERING_CLOSURE_PROTOCOL.md`
> 2. `belgeler/plan/DIMA_V2_GELISTIRME_DURUM.md`
> 3. `belgeler/plan/DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md`
> 4. `belgeler/plan/DIMA_DAY6_5_MANAGER_CONTRACT_SPEC_V0.md`
> 5. `eval/v2_day6_5_eval_manifest.yaml`
>
> Mühürlü nihai roadmap/report salt-okunur ve üst düzey authority olarak korunur.
>
> **Nihai architecture paths:** `STANDARD | RESEARCH`.
> Standard outcome telemetry: `DIRECT | BUILDER` (`STANDARD_DIRECT` / `STANDARD_BUILDER` eval labels may remain during transition).
> İki accepted authority ailesi:
> `AcceptedStandardAuthority` ve `AcceptedResearchAuthority`.
> `AcceptedResearchAuthority` yeni semantic body değildir; mevcut `AcceptedTurnContract`
> research authority gövdesidir, yeni isim yalnız alias/tagged-union seviyesinde kullanılabilir.
>
> **Hidden50 development blocker değildir.** External hidden yalnız final architecture certification seal'ini bloklar. D65-E1/E2 ve D65-E3A-R tamamlandı; current next gate workers=1 focused live architecture set. Sonra same-SHA A/B if needed → canary → Wren sentinels → freeze candidate → DEV80 → engineering closure → D65-X substrate challenger → certification.
>
> **Standard != daima one-shot.** `simple_standard_model_calls <= 1` evrensel mimari
> gate değildir. Direct yol minimum call hedefler; Builder bounded progress-driven retry yapabilir.
> Ancak `simple_standard_research_manager_loop = 0`.
>
> **Failure sınıflandırmadan patch YOK:**
> `MODEL_COGNITION | CONTRACT/ARCHITECTURE | RESOLVER_TRUTH | EVAL_ORACLE | TRANSPORT/PROVIDER`.
> Infra/provider failure semantic wrong değildir.
>
> **Workers=1 önce.** Semantic/mimari sertifikasyon concurrency'den önce tek işçidir.
>
> **Freeze disiplini:** önemli müdahale öncesi checkpoint SHA; A/B exact aynı backend SHA.
> `one DEV80 per engineering-freeze candidate`; code değişirse yeni candidate ve yeni DEV80 gerekir.
> Validation/Hidden fail sonrası code değişikliği certification freeze'i bozar; fresh set gerekir.
>
> **Operasyon sırası:** D65-E3A-R runtime-kernel realignment → provider-free family closure
> → workers=1 focused live → same-SHA reference A/B if needed → stratified canary
> → real Wren Standard + Research sentinel → freeze candidate → DEV80 → engineering closure
> → D65-X Wren-vs-Metabase substrate challenger → Validation50 → fresh Hidden50 → certification seal.
>
> **Tek cümlelik kural:** Vaka geçirerek sistem yapmıyoruz; doğru abstraction'ı kurup
> vakaların onun doğal sonucu olarak geçmesini istiyoruz.

## DAY 6.5 OVERRIDE — MANAGER ARCHITECTURE VALIDATION

> Bu bölüm Day 6.5 boyunca aşağıdaki tarihsel V2 semantic-owner maddelerinin üzerinde
> okunur. Day 6.5 living authority:
>
> - `belgeler/plan/DIMA_DAY6_5_MANAGER_ARCHITECTURE_VALIDATION.md`
> - `belgeler/plan/DIMA_DAY6_5_MANAGER_CONTRACT_SPEC_V0.md`
> - `belgeler/plan/ADR_DAY6_5_ONE_SHOT_COMPLEX_INTENT_REJECTED.md`
> - `eval/v2_day6_5_eval_manifest.yaml`
>
> Mühürlü nihai roadmap/report değiştirilmez. Manager production architecture henüz seal
> edilmemiştir; validation candidate'dır.
>
> Day 6.5 owner map:
>
> - FAST_LANGUAGE yalnız candidate attempt üretir; reddedilirse semantic izi downstream'a taşınmaz.
> - Complex raw-language cognition candidate owner = `ManagerRuntime`.
> - Accepted authority owner = `IntentAcceptanceGate` + runtime commit.
> - Canonical binding owner = `SemanticResolver`; Manager canonical ref yazamaz.
> - Source grounding owner = runtime `SourceSpanRegistry`; Manager source span uyduramaz.
> - Standard-vs-research owner = `RepresentabilityGate`; raw-length/keyword classifier yasak.
> - Numeric/query truth = existing Planner/Wren/DB/QueryContract trust plane.
> - Completion truth = `CompletionGate`; evidence varlığı VERIFIED anlamına gelmez.
> - accepted non-clarification turn başına exactly one active `AcceptedTurnContract`.
> - rejected model attempt semantic merge = 0.
> - `USER_MUST` ile `AGENT_DERIVED` origin asla birbirine promote edilmez.
>
> Bu eski hazırlık kuralı SUPERSEDED: external HIDDEN50 development blocker değildir; final certification seal blocker'ıdır. Current rule üstteki CURRENT CLOSURE OVERRIDE ve eval manifestidir.

## 0. Her oturumda ilk okunacaklar

Sıra bağlayıcıdır:

1. `belgeler/plan/DIMA_V2_GELISTIRME_DURUM.md` — nerede kaldık, açık borçlar, sıradaki iş.
2. `belgeler/plan/DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md` — current Day 6.5 runtime-kernel / STANDARD|RESEARCH uygulama authority.
3. `belgeler/plan/DIMA_DAY6_5_ENGINEERING_CLOSURE_PROTOCOL.md` — Day 6.5 kesin closure sırası ve trust-plane sınırları.
4. `belgeler/plan/DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` — **icra sırası authority**.
5. `belgeler/plan/DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md` — **hedef mimari ve gerekçe authority**.
6. `MIMARI.md` — mevcut çalışan sistem, reuse edilecek altyapı ve güvenlik/değişmezler.
7. Yalnız aktif ticket'ın dokunduğu kod ve testler.

Eski operasyon belgeleri V2'nin `nerede kaldık` kaynağı değildir.

## 1. Mühürlü belge kuralı

Aşağıdaki iki dosya bu branch'in aktif, bağlayıcı ve **salt-okunur** kaynaklarıdır:

- `belgeler/plan/DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md`
- `belgeler/plan/DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md`

Geliştirme sırasında bu iki dosya düzenlenmez, yeniden yazılmaz, sadeleştirilmez ve silent
delete yapılmaz. Yeni bir karar bunlarla çelişiyorsa önce kullanıcı kararı gerekir.

Yaşayan kayıt yalnız:

- `belgeler/plan/DIMA_V2_GELISTIRME_DURUM.md`

dosyasında tutulur.

## 2. Her adımda P → R çapraz okuma zorunlu

Kod yazmadan önce:

1. Yol haritasındaki aktif `P...` bölümünü aç.
2. O bölümün `MİMARİ DAYANAK` olarak işaret ettiği `R...` bölümünü aç.
3. İlgili eski hata sınıfını özellikle R3/R3A'da kontrol et.
4. Ancak bundan sonra ticket contract'ını yaz ve kodla.

Bir geliştirici yalnız roadmap maddesini okuyup gerekçeyi okumadan implementation yapamaz.

## 3. Her ticket'ın zorunlu kayıt şekli

`DIMA_V2_GELISTIRME_DURUM.md` içine başlamadan önce:

- AMAÇ
- USER SCENARIO
- ROADMAP
- REPORT DAYANAK
- NEW OWNER
- REUSE EDİLEN PRIMITIVE
- FILES TO TOUCH
- FILES NOT TO TOUCH
- TARGETED TEST / DEMO
- EXIT
- STOP-THE-LINE

Bitince aynı karta:

- YAPILAN
- COMMIT(S)
- SONUÇ
- BORÇ / DEFER
- SONRAKİ ADIM

eklenir.

## 4. V2 semantic ownership değişmezleri

V2 hot path'te:

- Day0–5 standard/reference yolda raw kullanıcı dili `TurnInterpreter` owner'ıdır; Day6.5 complex validation candidate'ında iterative cognition `ManagerRuntime` owner'ıdır. Aynı turn'de iki accepted semantic authority üretilemez.
- Resolver raw question'ı ikinci kez parse etmez.
- Planner semantic anlam seçmez.
- Research worker raw user prompt'tan metric/dimension seçmez.
- Finalizer eksik requirement'ı tahminle tamamlamaz.
- UI semantic eksikliği heuristic ile kapatmaz.
- Belirsizlikte tahmin değil `ClarificationState` üretilir.
- SQL/Wren execution semantic anlamın sahibi değildir.
- LLM business truth, metric formula, aggregation, unit veya grain sahibi değildir.
- Silent fallback yasaktır.
- `None` farklı failure sınıflarının ortak semantiği yapılmaz; typed outcomes kullanılır.
- Official answer tek finalization/seal sınırından geçer.

## 5. Legacy sınırı

İlk 10 gün wholesale refactor yok:

- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`

V2 semantic hot path bunların semantic owner fonksiyonlarını import etmez.

Reuse-first izin verilen ana altyapı:

- auth / Principal / authorize
- CompanyRegistry / tenant-bound Wren
- WrenService
- config
- mali_takvim
- safe privacy/entity primitives
- contracts
- mevcut deterministic analytical primitives
- viz/report/narration guard adapter'ları

Legacy primitive gerekiyorsa yalnız küçük, typed adapter veya pure extraction yapılır.

## 6. Hız ve test politikası

Amaç hızlı dikey geliştirmedir.

Her küçük değişiklikten sonra tam suite/kapı çalıştırılmaz.

Normal sıra:

1. kodla,
2. gerekliyse 3–15 sn hedefli unit/contract testi,
3. gerçek kullanıcı senaryosunu/daily demo'yu ilerlet,
4. aynı demette birkaç adımı tamamla,
5. milestone/exit gate'te toplu kontrol yap.

Full gate yalnız roadmap milestone/demet sonunda. Gecelik ağır suite CI'nın işidir.

Ancak şu sınıflarda hedefli test ertelenmez:

- cross-tenant / principal
- silent wrong
- requirement loss
- ambiguity auto-pick
- evidence grounding
- duplicate action / idempotency
- typed contract boundary

## 7. Günlük geliştirme ilkesi

Her gün sonunda çalışan bir dikey demo hedeflenir:

- Day 0 → V2 island boot/runtime boundary
- Day 1 → turn classification
- Day 2 → clarification
- Day 3 → real Wren query
- Day 4 → conversation/follow-up
- Day 5 → Core MVP
- Day 7 → adaptive research
- Day 10 → evidence-backed report

Demo yoksa yeni capability başlatma; fakat polish/refactor uğruna demo geciktirme.

## 8. Borç kaydı

Geçici workaround, bilinmeyen, ertelenen test, geçici adapter, eksik telemetry, eksik UI
veya security gate **aynı commit turunda** durum belgesine yazılır.

Borç kaydı şu alanları taşır:

- ID
- doğduğu P/R bölümü
- neden şimdi çözülmedi
- risk
- kapanış koşulu
- blocker: YES/NO
- hedef faz

Kodda TODO bırakıp durum belgesine yazmamak yasaktır.

## 9. Commit disiplini

Mümkün olduğunca her dikey adım kendi commit grubunda izlenebilir kalır.

Commit mesajı örüntüsü:

- `docs(v2): ...`
- `feat(v2-day0): ...`
- `feat(v2-day1): ...`
- `fix(v2): ...`
- `test(v2): ...`

Bir committe roadmap'te farklı capability'ler karıştırılmaz.

## 10. STOP-THE-LINE

Aşağıdakilerden biri görülürse yeni feature ekleme; sınırı düzelt:

- ikinci semantic owner doğuyor
- raw user text ikinci kez parse ediliyor
- blocking ambiguity auto-pick ediliyor
- MUST requirement sessiz düşüyor
- legacy silent fallback açılıyor
- evidence'sız numeric/causal claim üretiliyor
- tenant/principal explicit değil
- cross-domain grain kanıtlanmadan join yapılıyor
- LLM hesap/optimizasyon motoru gibi kullanılıyor
- V2 için legacy /ask davranışı authority oluyor

Bu dosyanın görevi uygulama planını değiştirmek değil, mühürlü planı doğru uygulamaktır.


## 11. V2 OPERASYONEL ÖĞRENİMLER — TEKRAR ETME

Aşağıdaki maddeler bu branch'te yaşanmış ve ölçülmüş operasyonel derslerdir. Bağlam
koptuğunda yeniden keşfedilmez; önce bunlar okunur.

### 11.1 Test / CI

- Eski sürekli `backend-ci.yml` kaldırıldı. **Yeniden yaratma.**
- Full suite her commit/push/PR'de çalıştırılmaz.
- Normal geliştirmede yalnız aktif P/R fazının focused contract/eval'ı çalıştırılır.
- Full regression yalnız milestone/release/security/parity gerektirdiğinde bilinçli karar
  ile çalıştırılır.
- Bir test infra/provider hatası veriyorsa correctness FAIL diye sınıflandırma; önce
  failure stage'i ayır.

### 11.2 OpenRouter secret / environment

- `DIMA_OPENROUTER_API_KEY` GitHub **Environment secret** olarak tutulur.
- Environment adı da `DIMA_OPENROUTER_API_KEY`.
- Secret kullanan Actions job'u açıkça
  `environment: DIMA_OPENROUTER_API_KEY` bağlamalıdır; aksi halde `secrets.*` boş gelir.
- API key hiçbir commit, .env örneği, log veya belge içine yazılmaz.

### 11.3 OpenRouter model authority

- Genel/SQL OpenRouter varsayılanı:
  `deepseek/deepseek-v4-flash`.
- Genel runtime source-of-truth:
  `app/config.py::openrouter_model`.
- GitHub Actions override source:
  Environment variable `DIMA_OPENROUTER_MODEL`.
- `DIMA_OPENROUTER_SELECT_MODEL` verilmezse legacy/general select ana modeli kullanır.
- **V2 TurnInterpreter bunun bilinçli istisnasıdır.** P7 DB-independent 30-turn live
  ölçümünde DeepSeek structured output'u korurken repair/refine speech-act gate'inde
  istikrarlı biçimde eşik-altı kaldı. TurnInterpreter'ın dedicated capability contract'ı:
  `app/config.py::v2_interpreter_provider` +
  `app/config.py::v2_interpreter_model`.
- Default dedicated interpreter:
  `openrouter / openai/gpt-5.6-luna`.
- Env overrides:
  `DIMA_V2_INTERPRETER_PROVIDER`,
  `DIMA_V2_INTERPRETER_MODEL`.
- Dedicated interpreter credential/model yoksa silent biçimde ucuz modele düşme; fail-closed.
  `provider=inherit` yalnız bilinçli explicit opt-in'dir.
- Bu model ayrımı semantic owner çoğaltmaz: raw language owner yine yalnız
  `TurnInterpreter`dır.
- Tarihsel ölçümde kullanılan modeli sonradan değiştirme; measurement provenance immutable
  kalır. Yeni model kararı yalnız ileriye dönük uygulanır.

### 11.4 OpenRouter reasoning / transport

- OpenRouter reasoning-capable hot-path modellerinde uzun reasoning açık bırakılmaz.
- `reasoning: {"exclude": true}` reasoning'i durdurmaz; yalnız dönen reasoning içeriğini
  gizler.
- Gerçek kapatma:
  `reasoning: {"enabled": false}`.
- Provider/model değiştirmeden önce tek-call transport smoke yap; model/config 400 veriyorsa
  28 vakayı boşuna koşturma.
- `openai/gpt-oss-120b` ile Day1 acceptance sırasında HTTP 400 görüldü; bunu tekrar
  default yapma.

### 11.5 Ollama / GitHub hosted runner

- GitHub hosted CPU runner üzerinde `qwen2.5:3b` ile 28-case acceptance pratik çıkmadı:
  structured çağrılar 30s HTTP read timeout'a girdi.
- Bu yol correctness kanıtı değildir ve tekrar denenmez.
- Local model ancak uygun donanım/timeout bütçesi olan gerçek local ortamda ayrıca ölçülür.

### 11.6 Day 1 ölçüm gerçeği

- Day1 strict P4 gerçek-provider kapısı OpenRouter üzerinde geçti:
  - model: `openai/gpt-5.6-luna` **yalnız tarihsel acceptance provenance'ı**
  - structured output: 28/28
  - turn act: 27/28
  - surface-grounding violation: 0
- Bu tarihsel sonuç, gelecekteki varsayılan modelin `deepseek/deepseek-v4-flash` olmasıyla
  yeniden yazılmaz.
- `sadece RAM-3` refine-vs-repair farkı Day4 conversation sentinel'idir; özel-case
  regex/hard-code yazma.



## 12. DATASET-AGNOSTIC GELİŞTİRME VE GERÇEKÇİ TEST KURALI

V2, repo içindeki demo veritabanına çalışan bir uygulama değil; farklı tenant/schema/data
bağlandığında aynı mimari sözleşmeyle çalışan bir analitik üründür. Bu nedenle demo DB'nin
isimleri, değerleri ve mevcut dağılımı **ürün mantığının gizli şartnamesi yapılamaz**.

### 12.1 Production code yasağı

Production V2 kodu:

- `demo-boyahane`, `parti`, `oee`, `RAM-3`, `Siyah`, `toplam_ciro` gibi mevcut
  fixture/tenant literal'larına göre branch açmaz.
- Bir metric/dimension/entity/cube varmış gibi varsaymaz; capability current tenant'ın
  `schema()/MDL/context` yüzeyinden türetilir.
- Testi geçirmek için örnek veri değerine özel regex/synonym/fallback eklemez.
- Tek demo şemada çalışan bir davranışı “generic” ilan etmez.
- DB'deki mevcut satırları önceden bilerek semantic karar vermez.
- Yeni tenant/schema bağlanınca uygulanamayacak hard-coded relationship, time axis, grain,
  metric veya entity assumption üretmez.

Bir capability yalnız belirli bir solution pack/domain'e aitse bu generic çekirdeğe
gizlenmez; explicit pack/capability contract olarak beyan edilir.

### 12.2 Test oracle bağımsızlığı

Test sorusu yalnız “bu demo DB'de hangi değer var?” diye bakılarak seçilemez. Özellikle
gerçekçi kullanıcı davranışını ölçen eval/test setlerinde:

- doğal, eksik, kısa, bağlamsal ve paraphrase kullanıcı cümleleri bulunur,
- canonical isimleri birebir söylemeye zorlayan yapay sorular ana doğruluk kanıtı olamaz,
- exact DB value yalnız **entity-resolution** yeteneğini test ediyorsa bilinçli fixture
  olabilir; genel language/planner başarısı diye sayılmaz,
- test oracle'ı implementation'ın ürettiği SQL/planı kopyalayarak kurulmaz; canonical
  semantic/result beklentisi bağımsız tanımlanır,
- “DB'de bu satır var, o halde doğru” yerine requirement/result equivalence ölçülür.

### 12.3 Her generic capability için en az iki kanıt türü

Mümkün olan aktif fazlarda generic capability şu iki sınıfın ikisini de taşır:

1. **Schema/data-independent contract test**
   - sentetik veya permüte edilmiş canonical adlar,
   - farklı metric/dimension/entity isimleri,
   - gerekirse ikinci küçük schema fixture,
   - aynı invariant'ın isimlerden bağımsız çalıştığını gösterir.

2. **Real engine / realistic user smoke**
   - gerçek Wren/DB execution,
   - doğal kullanıcı cümlesi veya typed output'un gerçekçi karşılığı,
   - yalnız demo fixture'ın varlığını değil gerçek boundary'yi sınar.

Demo DB smoke önemlidir ama **tek başına generic correctness kanıtı değildir**.

### 12.4 Metamorphic / permutation gate

Bir generic mekanizmanın doğruluğu literal isimlere bağlı olabilecekse en ucuz koruma:

```text
schema A → invariant PASS
canonical adları/değerleri permüte edilmiş schema B → aynı invariant PASS
```

Örnek:
- metric `toplam_ciro` yerine `net_revenue_x`,
- dimension `makine` yerine `asset_axis_q`,
- entity `RAM-3` yerine `UNIT-Z17`,
- cube `parti` yerine `fact_alpha`.

Production kod değişmeden iki fixture da geçmelidir. Bu isimler test fixture'ıdır;
production sözlüğü değildir.

### 12.5 Cross-tenant / unseen-schema düşünme zorunluluğu

Her yeni semantic/planner/conversation capability için code review'da şu soru sorulur:

> “Yarın tamamen farklı isimlere, başka time axis'e ve başka entity değerlerine sahip
> ikinci bir müşteri bağlansa bu kod hangi satırda bozulur?”

Cevap “fixture adını/değerini bilen bir satırda” ise feature tamamlanmış sayılmaz.

### 12.6 Test leakage STOP-THE-LINE

Aşağıdakiler görülürse yeni feature ekleme:

- production code test fixture literal'ını biliyor,
- test yalnız mevcut DB'ye uyacak şekilde soru seçiyor,
- canonical field adını söylemeyen gerçekçi paraphrase'ler sistematik olarak test dışı,
- fake schema'da geçen generic test ikinci/permuted schema'da kırılıyor,
- real DB smoke tek correctness kanıtı olarak sunuluyor,
- test oracle implementation'ın aynı helper'ından türetilip kendini doğruluyor,
- yeni tenant/schema için “sonra bakarız” denip generic çekirdek demo şemaya kilitleniyor.

Bu kural test sayısını büyütmek için değil, **yanlış güveni azaltmak** için vardır.
Az sayıda ama bağımsız, metamorphic ve gerçek boundary'yi ölçen test; çok sayıda
demo-fixture'a ezberlenmiş testten daha değerlidir.


## 13. SINGLE-OWNER ROOT-FIX KURALI — PATCH ZİNCİRİ YASAK

Her yeni failure'da ilk soru:

> **“Bu kararın tek sahibi kim?”**

Yeni hata görüldüğünde aşağıdaki refleks **yasaktır**:

```text
yeni prompt başarısız
→ resolver'a özel if
→ planner'a özel fallback
→ orchestrator'a exception branch
→ test yeşil
```

Bu zincir V1'de semantic kararların birçok katmana dağılmasının ve dev router/fallback
yığınlarının ana sebebidir. V2'de testin yeşile dönmesi tek başına başarı değildir; karar
doğru owner'da düzeltilmiş olmalıdır.

### 13.1 Failure triage sırası

Her failure için kod değiştirmeden önce:

1. **Observed failure** — kullanıcıya yanlış görünen somut davranış ne?
2. **Failure stage** — language, grounding, conversation, planning, execution, evidence,
   finalization, provider/infra?
3. **Normative requirement** — roadmap/report tam olarak neyi zorunlu kılıyor?
4. **Single owner** — bu kararı vermesi gereken TEK katman hangisi?
5. **Root fix** — yalnız owner contract/logic değişmeli.
6. **Downstream invariant check** — diğer katmanlar yeni semantic fallback eklemeden
   davranışı taşıyor mu?
7. **Focused proof** — en küçük bağımsız test/eval ile doğrula.

Owner dışında bir katmana semantic patch gerekiyorsa feature durdurulur ve mimari tekrar
incelenir.

### 13.2 Owner haritası

```text
raw user language / dialogue act / surface delta → TurnInterpreter
semantic catalog / candidate existence           → SemanticCandidateGenerator
surface → bounded candidate interpretation        → BoundedSemanticLinker (probabilistic, no authority)
candidate → canonical semantic authority          → SemanticBindingGate / SemanticHandleRegistry
typed temporal language intent                    → TypedTemporalNormalizer
temporal date arithmetic                          → TemporalBindingEngine
prior IR + slot delta + focus/state              → ConversationCoordinator
query gerekli mi                                 → DialoguePolicy
canonical AnalyticsIR requirement completeness   → AnalyticsIRBuilder / RequirementLedger
CubeQuery composition                            → CubePlanner
authorization / dry-plan / query                 → Official Wren execution boundary
result requirement verification                  → ResultValidator
execution evidence / seal                        → MinimumQueryContract / ContractStore
final wording                                    → Finalizer (ilgili faz geldiğinde)
```

Bir owner'ın kararını başka katman tekrar vermez.

### 13.3 Fallback yasağı

Aşağıdakiler root fix değildir:

- resolver'a bir phrase/literal için özel branch,
- planner'a “bulamazsan ilkini seç” fallback'i,
- orchestrator'a semantic exception yakalayıp başka yol deneme,
- UI'da backend semantic hatasını gizleyen heuristic,
- test fixture adını production sözlüğüne ekleme,
- malformed state'i legacy /ask'e sessiz düşürme,
- bir model hatasını downstream regex ile düzeltme.

Fail-closed typed outcome, yanlış semantic fallback'ten üstündür.

### 13.4 Test oracle da owner disiplinine uyar

Bir test/evaluator, roadmap'in ölçmediği proxy metriği release blocker yapamaz.
Örneğin iki farklı dialogue subtype aynı canonical state transition'ı ve aynı query policy'yi
üretiyorsa, roadmap exit "slot preservation/context correctness" diyorsa evaluator yalnız
etiket farkını semantic failure diye sayamaz.

Böyle durumda:
- raw measurement korunur,
- proxy metric diagnostic olarak raporlanır,
- normative exit metric kaynak belgeye göre yeniden hesaplanır,
- test case silinmez/değiştirilmez,
- production code test oracle'ına uydurulmaz.

### 13.5 Day 5 saldırı masası

Day 5 / P8 ciddi entegrasyon denetimidir. Yeni feature eklemek yerine gerçek kullanıcı gibi
`/ask-v2` yüzeyine saldırılır:

```text
paraphrase
typo
ambiguity
clarification
repair
follow-up
topic switch
comparison
ranking
result explain
pure social
malformed clarification token
stale context/version
provider/infra failure
cross-tenant isolation
silent-wrong attempts
```

Her failure yine aynı soruyla açılır: **“Bu kararın tek sahibi kim?”**
Day 5 boyunca yeni downstream semantic fallback birikimi kabul edilmez.


## 14. DAY 6.5 COGNITION / AUTHORITY SINIRI — KALICI KURAL

Day 6.5 ADR:
`belgeler/plan/DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md`

Temel invariant:

```text
LLM interprets bounded language.
Dima deterministic gates verify and confer authority.
Database proves numbers.
```

Manager semantic hot path'te aşağıdakiler YASAKTIR:
- yeni language regex ile semantic meaning çıkarmak,
- morphology/stemming score'u semantic truth yapmak,
- fuzzy/SequenceMatcher threshold'u ile `sem_*` authority üretmek,
- named eval case'i geçirmek için prompt'a phrase/example eklemek,
- Coverage critic'e canonical semantic veya clarification authority vermek,
- model `open_questions` alanını otomatik blocker yapmak,
- SemanticResolutionReceipt'i completeness parser'ına dönüştürmek,
- provider/transport failure'ı semantic NOT_ACCEPTED olarak saymak.

Doğru ownership:

```text
catalog concept exists?             → deterministic catalog
user surface means which candidate? → bounded Semantic Linker
candidate admissible/current?       → deterministic BindingGate
sem_* mint                          → SemanticHandleRegistry after gate
temporal phrase meaning             → typed temporal normalizer
actual dates                        → deterministic calendar engine
required binding complete?          → capability algebra / acceptance
obligation omitted?                 → coverage critic veto-only
numeric truth                       → governed Wren/DB
```

Unique exact verified alias doğrudan bağlanabilir; birden fazla exact candidate gerçek
ambiguity'dir ve guess edilmez. Candidate set fazla büyükse mevcut davranış fail-closed'dur;
bunu production phrase heuristic'i ile küçültmek yasaktır.

Legacy `SemanticResolver` ve `temporal.py` compatibility için kalabilir; Day 6.5 Manager
language authority olarak kullanılmaz. Bu ayrım değiştirilirse ADR + living status aynı
commit serisinde güncellenmelidir.
