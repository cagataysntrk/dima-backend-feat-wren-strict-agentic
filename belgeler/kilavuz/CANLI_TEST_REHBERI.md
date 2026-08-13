# DİMA — Canlı Test Rehberi

Bu belge, çalışan bir backend'e **gerçek LLM sağlayıcısıyla** soru sorarken izlenecek
sırayı, harcanabilecek istek bütçesini ve dönen cevapta neye bakılacağını anlatır.

Kapsam: `backend/` (FastAPI). ⚠ **Konteyner adı ve port ölçülerek yazılır** ㊱ — `docker ps --format '{{.Names}}\t{{.Ports}}'`. Bugünkü hâl: öngörü/geliştirme kabı **`dima-oneri-8002`** → `localhost:8002`; ayrıca **`dima-backend-temiz`** → `:8001`. *(Eski metin `dima-backend-core` diyordu; öyle bir kap **yok**.)*
Kurulum/log komutları `belgeler/kilavuz/SERVER_COMMANDS.md`'den alınmıştır; mimari iddialar
`backend/MIMARI.md`'ye aittir.

> **Önce §2'yi oku.** LLM istek bütçesi ölçülmüş ve dardır; testlerin çoğu bütçe
> harcamadan yapılabilir (§2.3).

---

## 1. Kurulum

### 1.1 Rebuild (kod değiştiyse ZORUNLU)

`docker-compose.yml`'de `backend` için volume **yoktur** — Python kodu değiştiğinde imaj
yeniden inşa edilmezse **eski kod koşmaya devam eder** (`belgeler/kilavuz/SERVER_COMMANDS.md` §1).

Ana proje dizininde:

```bash
export DOCKER_BUILDKIT=0 && export COMPOSE_DOCKER_CLI_BUILD=0 && \
docker-compose build dima-backend && \
docker rm -f dima-backend-core && \
docker-compose up -d dima-backend
```

### 1.2 Seed (rebuild sonrası ZORUNLU)

```bash
docker exec dima-backend-core python -m control_plane.cli seed-demo
```

> **Not — `belgeler/kilavuz/SERVER_COMMANDS.md`'ye göre değişen davranış.** O belge "konteyner silinince
> demo DB sıfırlanabilir" der; bu artık **genelde olmaz**: `docker-compose.yml` 2 Ağustos
> 2026'da `dima_logs:/app/logs` adlı bir named volume kazandı ve control-plane SQLite'ı
> (`.../logs/control_plane.db`, `control_plane/config.py:104`) orada yaşıyor. Yani DB
> rebuild'i **atlatır**.
>
> Bunun iki sonucu var: (a) `seed-demo` idempotent olduğu için yine de her rebuild sonrası
> koşulmalıdır — zararsızdır ve `init_db()` üzerinden eksik kolonları onarır; (b) DB
> hayatta kaldığı için **şema geride kalma riski gerçektir** — bkz. §6.1.

`seed-demo` idempotenttir (`backend/control_plane/seed.py`). Kurduğu şeyler:

| ne | değer | kaynak |
|---|---|---|
| tenant | `demo-boyahane` · `demo-geri-donusum` | `seed.py::DEMO_TENANTS` |
| owner | `<slug>@usedima.com`, parola `dima-demo-1234` | `seed.py::_ensure_owner` |
| eşik alarmı | `parti.toplam_fire_kg > 500`, dönem "son 7 gün" | `_senaryo_fixtureleri` (1) |
| VQR kaydı A | `"geçen ay toplam ciro"` → `source=user_verified` | `_senaryo_fixtureleri` (2) |
| VQR kaydı B | `"geçen ay toplam fire"` → `source=auto_cube` | `_senaryo_fixtureleri` (2) |
| sinonim adayı | `parti.toplam_ciro` ← "döviz cirosu"/"net hasılat", `approved=False` | `_senaryo_fixtureleri` (3) |

Bu fixture'lar kod yolundan üretilemeyen girdilerdir; yoksa ilgili yol **sessizce boş**
çalışır ("çalışıyor" görünür, hiçbir şey ölçmez — `seed.py` docstring).

**VQR çifti bilinçlidir:** ikisi de aynı şekilde, tek farkı `source`. `user_verified`
replay EDİLİR, `auto_cube` **edilmez** (`app/vqr.py::_FEW_SHOT_ONLY_SOURCES` — yalnız
few-shot promptunu besler). Yani bu iki soruyu yan yana sormak replay kararını doğrudan
gözlemlenebilir kılar.

Fixture'ların kapsamı `tenant.slug`'ın **kendisidir** (`demo-boyahane`), kırpılmışı değil
— ilk sürümde `demo-` atılıyordu ve VQR kayıtları hiç eşleşmiyordu (`seed.py` satır 86-90).

### 1.3 Login

```bash
BASE=http://localhost:8002
TOKEN=$(curl -s -X POST $BASE/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | jq -r .access_token)
echo "${TOKEN:0:24}…"
```

Auth **her zaman zorunludur**, kapatma bayrağı yoktur (`backend/CLAUDE.md`). Korunan her
uç `Authorization: Bearer <access_token>` ister.

Hızlı doğrulama (LLM harcamaz):

```bash
curl -s $BASE/health
curl -s $BASE/features    -H "Authorization: Bearer $TOKEN" | jq .
curl -s $BASE/schema      -H "Authorization: Bearer $TOKEN" | jq '.cubes | length'
curl -s $BASE/starters    -H "Authorization: Bearer $TOKEN" | jq .
```

### 1.4 Log izleme

```bash
docker logs -f dima-backend-core
```

Her `/ask` iki satır bırakır: `İSTEK /ask: q=… session=… thread=… followup=…`
(`app/routers/ask.py:1336`) ve `BAĞLAM /ask: kural=… cube=… eksen=…` (`ask.py:1330`).

---

## 2. İstek bütçesi kuralları

> Bu bölüm rehberin en kritik parçasıdır. Bütçe aşımı testin kendisini bozar.

### 2.1 Ölçülen sınır

**10 saniyede 10 istek.** Bu bir *hız* sınırıdır; ayrıca **bilinmeyen bir günlük kota**
vardır (kaynak: `backend/lab/konusma_senaryolari.py`, `LIVE_BEKLE` yorumu, satır 52-56).

### 2.2 Tur başına maliyet 1 DEĞİL 3

Intent-JSON yolundan geçen bir `/ask`, `consistency_k=3` (`app/config.py:92`) ile
`_select_consistent()`'a gider ve **üç LLM örneği** alır (`ask.py:2077-2091`). Yani:

```
1 /ask  (Intent-JSON yolu)  =  3 LLM çağrısı
```

`ask_intent_first` bayrağı `demo/packs/features.yml`'de **beta**'dır ve `resolve_for()`
`"off"` dışındaki her aşamayı açık sayar (`app/features.py:198`) — yani bu yol
**varsayılan olarak canlıdır**.

**Güvenli tempo: 5 saniyede en fazla 1 `/ask`.** Bu, 10 saniyede 6 LLM çağrısı demektir
ve tavanın altında kalır. `--live` senaryo koşucusu da tam olarak bunu uygular
(`LIVE_BEKLE = 5.0`).

### 2.3 LLM'e HİÇ gitmeyen yollar — bunlar sınırsız denenebilir

Testlerin **çoğu bedavadır**. Aşağıdaki yolların hiçbiri sağlayıcıya gitmez; peş peşe,
beklemeden, istediğin kadar koşturabilirsin:

| yol | tetikleyici | cevaptaki `source` |
|---|---|---|
| deterministik yönlendirme | `cube_router.route()` çözüyor | `cube` |
| yapısal takip | `deterministic_refine` / `cross_cube_add` / `cross_cube_dim_switch` | `cube` |
| dönemsel kıyas | "geçen yıla göre" → `strip_compare` + `route()` + `app.yoy` | `cube` |
| VQR replay | önceden doğrulanmış kaydın birebir eşleşmesi | `vqr` |
| meta / karşılama | `_is_meta()` — soruda "dima" geçiyor, "merhaba" vb. | `meta` |
| katalog keşfi | `_is_catalog_query()` — "neler sorabilirim", "hangi ölçüler var" | `catalog` |
| GL yapısal rapor | "gelir tablosu" / "bilanço" → `app/statements.py` | `statement` |
| chip düzenlemesi | `POST /cube` — **her zaman** LLM'siz | `cube` |
| katalog/şema uçları | `GET /schema`, `/starters`, `/features`, `/health` | — |

Ücretli yollar yalnız ikisidir: `cube+llm` (Intent-JSON, ×3) ve `llm:<sağlayıcı>`
(Discovery — ham SQL üretimi). Yapısal takipte `llm.refine_cube` de LLM'e gider.

Sıcak yola ek LLM çağrısı ekleyen bayraklar `features.yml`'de **kapalıdır** ve öyle
bırakılmalıdır: `agent_plan_secimi: off`, `prompt_enhancer: off`, `t2_anlatici: off`.

### 2.4 Senaryo koşucusu

> ⚠️ **Bu araç konteynerin İÇİNDE yoktur.** `backend/Dockerfile` yalnız `app/`,
> `control_plane/`, `demo/` ve `pyproject.toml`'u kopyalar — `lab/` ve `tests/` imajda
> **yok**. Dolayısıyla `docker exec … lab/konusma_senaryolari.py` çalışmaz. Araç host'ta,
> `backend/` dizininden, backend bağımlılıklarının kurulu olduğu bir Python ortamıyla
> koşulur (`tests.conftest`'i import eder — modül docstring'i ve satır 44).

```bash
cd backend

# LLM YOK, ağsız, yapısal — sınırsız koşulabilir
python lab/konusma_senaryolari.py
python lab/konusma_senaryolari.py --json

# GERÇEK sağlayıcı, SIRALI, tur arası 5 sn bekleme
python lab/konusma_senaryolari.py --live --orneklem 3
```

`--live` sınıf başına en fazla `--orneklem` (varsayılan `LIVE_ORNEKLEM = 3`) senaryo
koşar ve **düşürülen tur sayısını raporlar** — sessiz kırpma yoktur.

Senaryo sınıfları (`_uret()`): `coklu_ay_trendli` · `coklu_ay_trendsiz` · `ayrik_ay` ·
`donem_duzeltme` · `gorunum_donusumu` · `liste_niyeti` · `konu_degisimi` ·
`netlestirme_cevabi` · `vqr_kalicilik`.

Vaka raporları **sınıf başına** yazılır (tur başına değil):
`backend/lab/reports/konusma_senaryolari/<sinif>.md`.

İki kanal **ayrı** ölçülür ve karıştırılmamalıdır:

* **ERİŞİM** — cevap üretildi mi (`sql` ya da `cube_query` doldu mu).
* **DOĞRULUK** — doğru cube/dönem/yapı seçildi mi (senaryonun `bekle` fonksiyonu).

Bir düzeltmenin *çalıştığı* görünmesi, DOĞRU şeyi düzelttiği anlamına gelmez — modülün
kendi kayıtlı dersi (`elektrik` vakası: yanlış→cevapsız dönüşümü "iyileşme" gibi
görünmüştü).

Not: bu araç kendi `TestClient`'ını ayağa kaldırır (in-process app), 8001'deki HTTP
sunucusuna gitmez. `--live` modda LLM gerçek, HTTP katmanı taklit.

---

## 3. Chat akışı / thread — peş peşe test nasıl yapılır

### 3.1 `/ask` gövdesinde takip bağlamı hangi alanlarla taşınır

`backend/app/schemas.py::AskRequest`:

| alan | tip | rolü |
|---|---|---|
| `question` | `str` (zorunlu) | doğal dil sorusu |
| `limit` | `int \| None` | satır tavanı (`≥1`) |
| `execute` | `bool` (vars. `True`) | `false` → yalnız SQL üret + doğrula, **çalıştırma** |
| `history` | `list[str]` (vars. `[]`) | önceki kullanıcı mesajları, eski→yeni |
| `cube_query` | `dict \| None` | önceki turun **yapısal** durumu — yapısal takibin anahtarı |
| `prev_sql` | `str \| None` | önceki turun **ham SQL**'i (Discovery zinciri) |
| `session_id` | `str \| None` | sohbet oturumu kimliği (client üretir) |
| `thread_id` | `str \| None` | konu kimliği — **salt pass-through/echo** |
| `reply_to_label` | `str \| None` | "bu karta yanıt ver" etiketi — salt echo |
| `extra_context` | `list[str] \| None` | çoklu-seçim özetleri; **yalnız** Discovery promptuna eklenir |
| `anchor` | `dict \| None` | grafik hücresine çapa: `{"dimension": …, "value": …}` |

Sınıflandırma kuralı (`ask.py:1309-1311`):

```python
structural_followup = bool(body.cube_query)
raw_followup        = bool(prev_sql) and bool(body.history) and not structural_followup
is_followup         = structural_followup or raw_followup
```

Yani: **`cube_query` tek başına yeterli sinyaldir**, `history` dolu olması şart değildir
(`ask.py:1305-1308`). `history` yalnız ham-SQL takibi için ek sinyaldir.
`prev_sql` bilerek `cube_query`'den ayrı bir alandır — `cube_query` frontend'de
scheduling/dashboard/verify gibi başka özelliklerin de kapısıdır, ham SQL'i onun içinde
taşımak o özellikleri yanlışlıkla açardı (`schemas.py:60-66`).

### 3.2 Çalışan zincir (kopyala-yapıştır)

`$BASE` ve `$TOKEN` §1.3'ten. Tur arası **5 saniye** bekle (§2.2).

**Tur 1 — ilk soru**

```bash
curl -s -X POST $BASE/ask \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"question":"bu yıl toplam fire",
       "session_id":"canli-test-1",
       "thread_id":"konu-1"}' > /tmp/t1.json

jq '{source, note, confidence: .explain.confidence, path: .explain.path,
     cube: .cube_query.cube, rows: .result.row_count,
     chip: [.suggestions[]?.label], adim: [.next_steps[]?.label]}' /tmp/t1.json
```

**Tur 2 — yapısal takip: cevabın `cube_query`'sini geri gönder**

```bash
sleep 5
CQ=$(jq -c '.cube_query' /tmp/t1.json)

jq -n --argjson cq "$CQ" '{
  question: "renk bazında",
  cube_query: $cq,
  history: ["bu yıl toplam fire"],
  session_id: "canli-test-1",
  thread_id: "konu-1"
}' > /tmp/req2.json

curl -s -X POST $BASE/ask \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d @/tmp/req2.json > /tmp/t2.json

jq '{source, cube: .cube_query.cube, dims: .cube_query.dimensions,
     confidence: .explain.confidence, is_new_topic}' /tmp/t2.json
```

Beklenen: `source="cube"` (deterministik düzenleme, LLM'siz), `is_new_topic=false`.
`source="cube+llm"` gelirse deterministik düzenleme tutmamış, `llm.refine_cube` devreye
girmiş demektir — o tur **3 LLM çağrısı** harcamıştır.

**Tur 3 — ikinci takip: bu kez Tur 2'nin `cube_query`'si taşınır**

```bash
sleep 5
CQ2=$(jq -c '.cube_query' /tmp/t2.json)

jq -n --argjson cq "$CQ2" '{
  question: "sadece son 3 ay",
  cube_query: $cq,
  history: ["bu yıl toplam fire", "renk bazında"],
  session_id: "canli-test-1",
  thread_id: "konu-1"
}' > /tmp/req3.json

curl -s -X POST $BASE/ask \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d @/tmp/req3.json > /tmp/t3.json

jq '{source, filters: .cube_query.filters, dims: .cube_query.dimensions}' /tmp/t3.json
```

Zincirin kuralı: **her tur bir öncekinin `cube_query`'sini taşır**, ilk turun değil.

**Ham-SQL (Discovery) zinciri** farklı taşınır — önceki tur `cube_query` üretmediyse
`prev_sql` + `history` gönder:

```bash
jq -n --arg sql "$(jq -r '.sql' /tmp/t1.json)" '{
  question: "peki geçen yıl?",
  prev_sql: $sql,
  history: ["bu yıl toplam fire"],
  session_id: "canli-test-1"
}'
```

### 3.3 Chip tıklama — `POST /cube` (LLM'siz, bedava)

`CubeRequest` alanları: `cube_query` (zorunlu) · `label` · `limit` · `session_id` ·
`thread_id` · `verdict` · `undo` · `comment` (`schemas.py:100-115`).

`next_steps[]` chip'leri **tam `cube_query`** taşır; tıklama bunu aynen `/cube`'a
göndermektir:

```bash
NS=$(jq -c '.next_steps[0]' /tmp/t2.json)

jq -n --argjson ns "$NS" '{
  cube_query: $ns.cube_query,
  label:      $ns.label,
  session_id: "canli-test-1",
  thread_id:  "konu-1"
}' > /tmp/req_chip.json

curl -s -X POST $BASE/cube \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d @/tmp/req_chip.json | jq '{source, question, rows: .result.row_count, contract_id}'
```

`/cube` her zaman `source="cube"` döner ve `question` alanına `label`'ı yazar
(`ask.py:892-901`). Geçersiz bir `cube_query` → **400**, çıplak 500 değil.

Netleştirme chip'i (`suggestions[]`) farklıdır: o `{label, query}` taşır ve tıklama
`query` metnini yeni bir `/ask` olarak göndermektir.

### 3.4 `session_id` ile `thread_id` farkı

* **`session_id`** — sohbet oturumu. Kalıcı logda sohbeti yeniden kurmak için kullanılır
  (`schemas.py:67`) ve yüklenen Excel/CSV'nin oturum DuckDB servisini seçer
  (`ask.py::_service_for`). Yani gerçek bir kaynak seçicisidir.
* **`thread_id`** — **salt pass-through**. `is_followup` mantığına **hiç karışmaz**,
  yalnız etiketleme/echo içindir; `AskResponse.thread_id` olarak aynen geri yansıtılır
  (`schemas.py:69-72`, `ask.py:1348`).

**Korunan değişmez (MIMARI §12.1, tartışmaya kapalı):**

> **Thread bir UI GRUPLAMASIDIR, SEMANTİK SINIR DEĞİLDİR.** Bir thread cube/bağlam sınırı
> taşımaz; yeni thread **yalnız açık kullanıcı eylemiyle** doğar. Sunucu bir soruyu
> *"yeni konu"* ilan ederek bağlamı **sessizce koparamaz**.

Pratik sonucu: `thread_id`'yi değiştirmek bağlamı sıfırlamaz. Bağlamı taşıyan şey
`cube_query`/`prev_sql`'dir. Yeni konuya geçmek istiyorsan **`cube_query` gönderme**.

`is_new_topic` da yalnız bilgilendirici bir kart-başı etikettir (`not is_followup`),
frontend'in thread mantığına karışmaz (`schemas.py:245-256`).

---

## 4. Ne ölçülür — cevaptaki alanların anlamı

### 4.1 `source` — SQL'i kim üretti

| değer | anlamı | LLM? |
|---|---|---|
| `cube` | `route()` / deterministik düzenleme / `/cube` chip'i | hayır |
| `cube+llm` | LLM **SQL değil Intent-JSON** doldurdu, motor derledi | evet (×3) |
| `vqr` | önceden doğrulanmış kayıt tekrar oynatıldı | hayır |
| `meta` | ürün/karşılama sorusu | hayır |
| `catalog` | katalog keşfi | hayır |
| `statement` | gelir tablosu / bilanço | hayır |
| `llm:<sağlayıcı>` | Discovery — ham Wren SQL üretildi | evet |
| `rule` | kural-tabanlı, anahtarsız yedek | hayır (LLM yok) |
| `upload` / `drill` | yükleme özeti / drill adımı | hayır |

`source` **boşsa** rapor üretilmemiştir (netleştirme, dürüst ret) — o durumda `note`
doludur.

### 4.2 `explain` — `{path, confidence, assumptions}`

`confidence` tablosu (`app/answer.py::_EXPLAIN_PATH`):

| `source` | `confidence` | neden |
|---|---|---|
| `cube`, `meta`, `catalog`, `statement` | **1.0** | tamamen deterministik |
| `vqr` | **0.95** | önceden doğrulanmış ama dondurulmuş kayıt |
| `cube+llm` | **0.85** | yapıyı LLM seçti, motor doğruladı |
| `llm:*`, `rule` | **None** | ölçülebilir güven skoru **yok** — uydurma sayı yerine boş |

`cube+llm`'in `1.0` görünmesi bilinen ve **düzeltilmiş** bir hataydı: en uzun önek
kazanacak şekilde çözülüyor (`answer.py:106-125`). Eğer bir Intent-JSON cevabında yeniden
`1.0` görürsen, bu bir regresyondur.

`assumptions` **yalnız gerçekten sessiz bir varsayım yapıldıysa** dolar (ör. dönem
belirtilmedi → "tüm zamanlar" seçildi/onaylandı). Doluysa `confidence` bir kademe düşer:
`-0.15` (`answer.py:141-142`). Yani `cube`+varsayım → **0.85**, `vqr`+varsayım → **0.80**.

`path` insan-okur etikettir; `source`'un normalize hâli.

### 4.3 `cube_query`

Doluysa cevap **yapısal** üretilmiştir ve takip için geri gönderilebilir. Boşsa ya
netleştirmeye düşülmüştür (`suggestions` dolu), ya Discovery'ye (`source=llm:*`).

`adhoc_cube` bayrağı açıkken (features.yml: `beta`) Discovery cevabından oturum-scoped bir
ad-hoc cube türetilebilir — `cube_query.adhoc = true` olur. **Yapı açılır ama güven
açılmaz**: `source` `llm:*` KALIR, `confidence` `None` KALIR (`app/adhoc_cube.py:22`).

`cube_query.kirpilmis` doluysa satır tavanına değilmiş demektir; `next_steps` **bilerek
boş bırakılır** ve `note`'a gerekçe eklenir (`answer.py:382-386`).

### 4.4 `note`

Rapor **üretilmediğinde** dürüst açıklamadır (istenen alan modelde yok, soru anlaşılmadı,
kapsam dışı). Bu durumda `sql`/`result` boştur ve client mevcut raporu korumalıdır
(`schemas.py:234-236`). `meta`/`catalog` cevaplarında ise `note` **cevabın gövdesidir**.

### 4.5 `suggestions` — netleştirme / örnek chip'i

`[{label, query}]`. İki bağlamda dolar:

* **netleştirme** — soru belirsiz; sistem tahmin etmek yerine **sorar**. Bu durumda
  `cube_query` **yoktur** ve bu bir kusur değildir: netleştirme geçerli ve doğru bir
  cevaptır. Senaryo koşucusu bunu bilerek "erişim 0/1, doğruluk 1/1" diye raporlar
  (`konusma_senaryolari.py` `netlestirme_cevabi` notu).
* **meta/katalog** — tıklanır örnek sorular.

Tıklama = `query` metnini yeni bir `/ask` olarak göndermek.

### 4.6 `next_steps` — rehberli analitik chip'leri

`[{label, kind, cube_query}]`, `kind ∈ {dimension, measure, time}`. Katalogdan
**deterministik** türetilir (LLM yok), yalnız `cube_query` **ve** `result` varsa üretilir.
Her chip tam `cube_query` taşır → `/cube` ile LLM'siz koşar. Bayrak: `next_steps` (beta).

### 4.7 `view_hint`

Veri değil **sunum**: `chart | table | line | bar | pie | heatmap | facet`
(`ask.py::_VIZ_KINDS`). "pasta grafik" gibi bir takip mesajı yapıyı **silmemeli** —
`cube_query` yerinde kalmalı, yalnız `view_hint` değişmelidir. Bu şartın ihlali
`gorunum_donusumu` senaryosunun ölçtüğü tek şeydir.

### 4.8 `agent_run` — ajan koşum makbuzu

Yalnız planlayıcıdan geçen cevaplarda dolar; diğerlerinde `None` (uydurulmaz).
`{steps, step_count, query_count, truncated}`: hangi araçlar, hangi sırayla, kaç ms,
hangi adım reddedildi, bütçe kısıldı mı (`ask.py:284-363`).

Bunu üreten `agent_plan_secimi` bayrağı `features.yml`'de **`off`**'tur — varsayılan
koşumda bu alanın `None` gelmesi **doğru** davranıştır, eksiklik değil.

### 4.9 `interpretation` ve `interpretation.narration`

`interpretation` = `{facts: [...], summary: "Türkçe"}`, deterministik ve data-güdümlü;
ham veri LLM'e gitmez. Bayrak: `cikti_yorumlama` (beta → açık). Kapalıysa `None`.

`interpretation.narration` **ayrı bir şeydir**: guarded LLM anlatıcı (`t2_anlatici`).
`features.yml`'de **`off`** — varsayılanda hiç gelmez. Açıksa bile
`narration_guard.guvenli_anlatim` **zorunlu çıkış kapısıdır**: sonuç kümesiyle
eşleşmeyen sayı taşıyan cümle yayımlanmaz; hiçbir cümle sağ kalmazsa anlatı hiç
eklenmez, deterministik `summary` yerinde kalır (`answer.py:299-340`).

`narration` doluysa `summary`/`facts` **yine de yerindedir** — anlatı şablonu ezmez,
üstüne biner.

### 4.10 Yan alanlar

* `trace[]` — pipeline adımları; son eleman en öğreticidir. Intent yolunda
  `"self-consistency %XX (3 örnek)"` notunu burada görürsün (`ask.py:2098`).
* `contract_id` — Query Contract kaydı; `GET /contracts/{id}/replay` ile
  "veri mi değişti, tanım mı?" teşhisi.
* `calculation_explanation` — ölçünün **nasıl hesaplandığının** düz-dil anlatımı.
  `explain` ile karıştırma: `explain` provenance, bu alan formül. `cube_query` yoksa
  `None` kalır.
* `viz` — grafik/tablo/pivot kararı; backend'de deterministik alınır (ADR-0024).
* `job_id` — yalnız `ask_async_discovery` bayrağı açıkken dolar; varsayılanda `None`.

---

## 5. Altın kurallar

1. **Backend kodu değiştiyse REBUILD şart.** Volume yok — rebuild etmezsen **eski kod
   koşar** ve ölçtüğün şey senin değişikliğin değildir.
2. **Rebuild sonrası SEED şart.** Konteyner silindiğinde demo DB sıfırlanır; seed
   olmadan login bile olamazsın, fixture'a bağlı yollar (VQR replay, eşik kıyası, sinonim
   kuyruğu) sessizce boş çalışır.
3. **Aynı anda İKİ test konteyneri koşturma.** Compose kilidi süreç-içidir.
4. **`source=cube` bir cevabın DOĞRU olduğunu göstermez**, yalnız **deterministik**
   üretildiğini. Erişim ve doğruluk ayrı kanallardır (§2.4).
5. **Bir ölçüm aracı da bir bağımlılıktır.** Sayı beklenmedikse **önce ARACI şüphelen**.
   Bu depoda ölçüm aracının kendisi defalarca yanlış ölçtü — `_net_olcu` belirsiz bir
   ölçü seçip netleştirme yolunu "başarısızlık" sayması, `_daraldi`'nin zaman boyutunu
   sabitleyip çalışan bir düzeltmeyi "başarısız" raporlaması (MIMARI §6.4).
6. **Tur arası 5 saniye.** `sleep 5` yazmayı unutma; Intent yolunda her tur 3 çağrıdır.
7. **Bedava yolları önce tüket.** §2.3'teki her şey sınırsızdır; bütçeyi yalnız gerçekten
   Intent-JSON/Discovery gerektiren sorulara harca.
8. **Sıcak yola LLM ekleyen bayrakları açma** (`prompt_enhancer`, `t2_anlatici`,
   `agent_plan_secimi`) — açmak bilinçli bir karar olmalı ve bütçeyi katlar.

---

## 6. Sorun giderme

### 6.1 DB şeması geride kalırsa ne olur

`create_all` yalnız **eksik TABLOYU** yaratır, var olan tabloya **kolon eklemez**.
Geliştirme SQLite'ı ilk koşuda modelin o günkü hâlinden doğar, model ilerler, DB kalır.
Ve her yazma yolu bilinçli olarak best-effort (`try/except` + WARNING) olduğu için hata
**görünmez — özellik sessizce ölür** (`control_plane/db.py:40-70`).

Çalışan demo konteynerinde ölçülen hasar:

| tablo | eksik kolon | sessiz sonuç |
|---|---|---|
| `verified_query` | `verified_at` | **VQR tamamen ölü** — ne okuma ne yazma |
| `interaction_log` | `reject_reason` | red gerekçesi telemetrisi yazılamıyor |
| `contract_log` | `provenance_json` | makbuz DB yerine spool'a düşüyor |
| `notification_log` | `neden_json` | uyarı **nedeni** kaydedilemiyor |

`init_db()` (yani `seed-demo`) SQLite'ta eksik kolonları **ekler ve loglar** — ama bu bir
migration motoru değildir: yalnız `ADD COLUMN`, yalnız SQLite. `NOT NULL` + varsayılansız
bir kolon eklenemez; o durumda WARNING basılır ve o kolona yazan özellik sessizce
çalışmaz.

**Bu senaryo bu depoda gerçek bir risktir** (§1.2): `dima_logs` volume'u sayesinde SQLite
rebuild'i atlatır, yani **yeni kod eski şemayla** karşılaşır. Rebuild'den sonra `seed-demo`
koşmayı atlarsan `init_db()` hiç çalışmaz ve onarım yapılmaz.

### 6.2 Nasıl görülür

```bash
docker logs dima-backend-core 2>&1 | grep -iE "şema|WARNING"
```

Aranacak satırlar:

* `SQLite şeması modele hizalandı — EKLENEN KOLONLAR: …` → şema geriydi, **onarıldı**.
* `ŞEMA GERİDE: <tablo>.<kolon> eklenemiyor (NOT NULL + varsayılansız)` → **onarılamadı**,
  Alembic gerekir; o kolona yazan özellik sessizce çalışmayacak.
* `ŞEMA GERİDE: <tablo>.<kolon> eklenemedi` → `ALTER TABLE` patladı.
* `VQR'daki SQL artık geçersiz (şema değişmiş olabilir)` → MDL değişmiş, kayıt bayat.
* `VQR CubeQuery çifti ayrıştırılamadı (şema değişmiş olabilir)`.

### 6.3 Diğer sessiz best-effort uyarıları

Bunlar cevabı **düşürmez** ama bir şeyin çalışmadığını söyler:

```
çıktı yorumu üretilemedi (best-effort)
sonraki adım önerileri üretilemedi (best-effort)
/cube görselleştirme kararı başarısız (best-effort)
hesaplama açıklaması üretilemedi (best-effort)
LLM Intent-JSON seçimi başarısız (best-effort)
şema üretilemedi → serbest-JSON yolu
```

Bir alan beklediğin hâlde `None` geliyorsa **önce loga bak** — büyük olasılıkla ilgili
`best-effort` bloğu WARNING basmıştır.

### 6.4 VQR replay beklendiği gibi davranmıyorsa

* VQR kapsamı `settings.company`'dir ve seed fixture'ları `tenant.slug`
  (`demo-boyahane`) ile yazılır. İkisi eşleşmiyorsa kayıt **hiç eşleşmez** ve yol sessizce
  test edilmemiş kalır.
* `auto_cube` kayıtları **bilerek** replay edilmez (`_FEW_SHOT_ONLY_SOURCES`) — yalnız
  few-shot promptunu besler. `auto_discovery` ve eski `auto` kayıtları **güvenilmezdir**.
* **Benzerlik** eşleşmesi `route()`'a yenilir; **birebir** eşleşme yenilmez
  (`ask.py:1798-1816`). Canlı turda ölçülen olay: *"geçen ay toplam **fire**"* sorusu
  embedding benzerliğiyle *"geçen ay toplam **ciro**"* kaydına eşleşip `SELECT SUM(ciro_tl)`
  döndürmüştü — `source="vqr"`, `confidence=0.95` rozetiyle, **sorulanın zıddı bir ölçü**.
* Ham-SQL kayıtları `mdl_version` damgası tutmuyorsa **bayat** sayılır ve kısayol atlanır
  (`ask.py:1832-1835`).
