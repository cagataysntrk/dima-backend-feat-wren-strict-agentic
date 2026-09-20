# DIMA V2 — GELİŞTİRİCİ / AJAN ÇALIŞMA SÖZLEŞMESİ

> **Kapsam:** `feat/ask-v2-mvp` ve bu branch'ten türeyen V2 geliştirme dalları.
> **Amaç:** Dima V2'yi mühürlü nihai rapor ve yol haritasına göre hızlı, izlenebilir ve
> eski semantic-front-door hatalarını tekrar etmeyecek biçimde geliştirmek.

## 0. Her oturumda ilk okunacaklar

Sıra bağlayıcıdır:

1. `belgeler/plan/DIMA_V2_GELISTIRME_DURUM.md` — nerede kaldık, açık borçlar, sıradaki iş.
2. `belgeler/plan/DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` — **icra sırası authority**.
3. `belgeler/plan/DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md` — **hedef mimari ve gerekçe authority**.
4. `MIMARI.md` — mevcut çalışan sistem, reuse edilecek altyapı ve güvenlik/değişmezler.
5. Yalnız aktif ticket'ın dokunduğu kod ve testler.

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

- Raw kullanıcı dili yalnız `TurnInterpreter` tarafından yorumlanır.
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

- V2 için varsayılan OpenRouter modeli:
  `deepseek/deepseek-v4-flash`.
- Runtime source-of-truth:
  `app/config.py::openrouter_model`.
- GitHub Actions override source:
  Environment variable `DIMA_OPENROUTER_MODEL`.
- Focused workflow fallback'u da aynı model olmak zorunda.
- `DIMA_OPENROUTER_SELECT_MODEL` verilmezse ana model kullanılır.
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

