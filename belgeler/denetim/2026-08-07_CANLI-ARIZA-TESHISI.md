# Canlı arıza teşhisi — *"intent LLM'e gitmiyor"*

**Tarih:** 2026-08-07 · **Kapsam:** canlı `dima-backend-core` konteyneri (09:07–09:41 UTC)
**Yöntem:** kod okuma + **canlı log** + konteyner içinde **yerinde ölçüm**. Hiçbir iddia
tahmine dayanmıyor; her başlığın altında onu üreten komut/çıktı var.

> ⚠ Bu belge bir **denetim raporudur**, bir plan değildir. Hiçbir kod değiştirilmedi.

---

## 0 · Yönetici özeti — üç şikâyet, üç ayrı kök

| # | Kullanıcının gördüğü | Gerçek kök neden | Doğruluk |
|---|---|---|---|
| 1 | *"intent LLM'e gitmiyor, deterministiğe gidiyor"* | 🔴 **LLM'e GİDİYOR — ama körlemesine.** Prompt kataloğu, şemadaki **Türkçe eşanlam katmanını taşımıyor**. LLM gördüğü şeyle `{"cube":null}` demekte **haklı** | ölçüldü: **9/9 çağrı `cube:null`** |
| 2 | *"anlatı hep LLM'e gidiyor, deterministik ilk basamak yoktu"* | ✅ **Doğru.** `_anlati_ekle` tek basamaklı: `t2_anlatici` açıksa **doğrudan LLM**. Şablon basamağı **hiç yazılmadı** | kod: `app/answer.py:424-470` |
| 3 | *"takipte 500 aldım"* | 🔴 **500 backend'den ÇIKMADI.** Canlı backend'in tüm ömründe **sıfır 5xx** var; istek backend'e **hiç ulaşmadı** | erişim logu tamamı taranmış |

🔴 **En önemli bulgu (1)** kullanıcının teşhisini **doğruluyor ama sebebini değiştiriyor**:
sorun *"LLM çağrılmıyor"* değil, **LLM'e Türkçe sorulmuyor**.

---

## 1 · Şikâyet #1 — LLM çağrılıyor, cevabı atılıyor, sebebi katalog

### 1.1 Önce ölçüm: LLM gerçekten çağrılıyor mu?

Canlı log, kullanıcının iki sorusunu ve altındaki LLM trafiğini gösteriyor:

```
09:09:38  dima.llm: openrouter API başarılı (deepseek/deepseek-v4-flash, 2164ms)
09:09:38  dima.llm: openrouter API başarılı (deepseek/deepseek-v4-flash, 2654ms)
09:09:38  dima.llm: openrouter API başarılı (deepseek/deepseek-v4-flash, 2706ms)
09:09:39  dima.ask: CEVAP /ask: q='şubatta ocağa göre ciro artışı ve sebepleri'
          source=None süre=4017ms not='"ocaga ciro" başka bir konu gibi görünüyor…'

09:13:32  dima.llm: openrouter API başarılı (…, 22558ms)
09:13:37  dima.llm: openrouter API başarılı (…,  4479ms)
09:13:40  dima.llm: openrouter API başarılı (…,  7921ms)
09:13:44  dima.llm: openrouter API başarılı (…, 11683ms)
09:13:45  dima.ask: CEVAP /ask: q='personel verimliliklerini kıyasla'
          source=None süre=35288ms not='"personel" başka bir konu gibi görünüyor…'
```

**Bulgu:** `ask_intent_first` bayrağı **açık** (`beta`), `consistency_k=3`, ve her soru için
**3 paralel LLM çağrısı gerçekten yapıldı**. Yani merdiven LLM'i **atlamıyor**.

```
$ docker exec dima-backend-core python -c "…resolve_for(Settings(), None)…"
  ask_intent_first       = beta        ← AÇIK
  llm_sema_kisitli       = beta
  netlestirme_onceligi   = OFF         ← kapalı (yani onu suçlamak yanlış olurdu)
  prompt_enhancer        = OFF
  t2_anlatici            = alpha
  consistency_k = 3 · llm provider = openrouter · DB override: []
```

⚠ Dikkat: `netlestirme_onceligi` **kapalı**. Yani *"netleştirme Intent-JSON'u öncelliyor"*
hipotezi bu kurulumda **yanlıştır** — netleştirme, LLM'den **sonra** çalışıyor.

### 1.2 Sonra kanıt: LLM ne cevap verdi?

```
$ docker logs dima-backend-core | grep -c "whitelist REDD"
9
$ docker logs dima-backend-core | grep "whitelist REDD"
09:09:38  intent: whitelist REDDİ (sema=kapali) — ham={"cube":null}     ×3
09:11:02  intent: whitelist REDDİ (sema=kapali) — ham={"cube":null}     ×3
09:13:37  intent: whitelist REDDİ (sema=kapali) — ham={"cube":null}     ×3
```

🔴 **9/9 = %100.** Model her seferinde **reddetme dalını** seçti. Yani `_select_consistent`
bir *oylama uyuşmazlığı* yaşamadı — **oy verecek aday hiç oluşmadı**.

Bu, teşhisin yönünü değiştirir: kusur **oylama eşiğinde** ya da **netleştirmenin
önceliğinde** değil, **modele verilen girdide**.

### 1.3 🔴 KÖK NEDEN — katalog, şemanın Türkçe katmanını taşımıyor

`cube_router.build_catalog()` LLM'e giden metni üretiyor. Ürettiği şey:

```
- oee: measures[ort_oee, ort_kullanilabilirlik, ort_performans, …]; dimensions[…]; time[tarih]
- ik:  measures[toplam_brut_maas, …, personel_sayisi]; dimensions[departman, …]; time[tarih]
- parti: measures[toplam_fire_kg, …, toplam_ciro, kar, …]; dimensions[makine, hat, …]
```

Yani **yalnız teknik kolon adları**. Oysa **aynı şema nesnesi** şunları taşıyor:

```
$ docker exec … "oee cube ALANLARI"
['always_filter','base_object','cekirdek_metrik','default_measure','dimension_labels',
 'dimension_origin','dimension_synonyms','dimension_values','dimensions','display',
 'hedefler','kiyaslanamaz','lower_is_better','measure_expressions','measure_synonyms',
 'measure_synonyms_display','measures','name','non_additive','pvm','semi_additive',
 'synonyms','time_dimensions','units']

oee.display            = 'OEE'
oee.synonyms           = ['oee','verim','randiman','vardiya','kullanilabilirlik',
                          'availability','performans','durus','ariza','downtime',…]
oee.measure_synonyms['ort_oee'] = ['oee','verim','randiman','toplam ekipman etkinligi',…]
ik.display             = 'İK / bordro'
ik.synonyms            = ['ik','insan kaynaklari','bordro','maas','ucret','sgk','mesai',…]
```

**`build_catalog` bunların HİÇBİRİNİ yazmıyor**: ne `synonyms`, ne `measure_synonyms`,
ne `display`, ne `dimension_labels`. Katalogda ölçülen sonuç:

```
katalogda 'verimlilik' geçiyor mu : 0 kez
katalogda 'ciro'                  : 2 kez (yalnız `toplam_ciro` kolonu içinde)
```

> 🔴 **Mimarinin tersine dönmesi.** Deterministik `route()` **tam Türkçe eşanlam
> katmanını** kullanıyor; **LLM ise ondan yoksun bir kolon dökümü** görüyor. Yani sistem,
> güvendiğini söylediği basamağı **en kör hâliyle** çalıştırıyor.
>
> *Bir modele soruyu kendi dilinde sormazsan, aldığın "bilmiyorum" onun cehaleti değil,
> senin sorunun olur.*

### 1.4 İki vakanın satır satır açıklaması

**`personel verimliliklerini kıyasla`**
* `verimlilik` → `route()`: `oee.synonyms` içinde **`verim` var** ✓
* `verimlilik` → **LLM kataloğu: 0 eşleşme** ✗ → `{"cube":null}` ×3
* `personel` → `ik`/`parti` kimliği tetikliyor → `partial_unknowns` çapraz-konu dalı
* **Sonuç:** *"«personel» başka bir konu gibi görünüyor"* — LLM devre dışı kaldığı için
  geriye **yalnız** deterministik netleştirme kalıyor.

**`şubatta ocağa göre ciro artışı ve sebepleri`**
* `ciro` katalogda yalnız **`parti.toplam_ciro`** olarak var. Modelin *"ciro"* kelimesini,
  **`parti`** (boya partisi) adlı bir cube'un içinde araması gerekiyor — `display`
  (*"Üretim partileri"*) ve `synonyms` verilmediği için bu **çıkarılabilir değil**.
* 🔴 **İkinci, bağımsız kusur:** *"ocağa"* = **Ocak** ayının yönelme hâli
  (`k→ğ` yumuşaması). Dönem çözücü bunu tanımıyor → kelime **bilinmeyene** düşüyor ve
  çapraz-konu notunun içine sızıyor: `"ocaga ciro" başka bir konu gibi görünüyor`.
  Bu, `ADR-0008`'in kelime listesiyle çözülmemesi gereken, **morfolojik** bir eksik.
* Ayrıca soru bir **MoM kıyası** (`şubat` ↔ `ocak`) — `G6`'nın `kiyas_cebiri`'nin tam
  nüfusu. Kıyas sökülemediği için o yol da hiç denenmiyor.

### 1.5 Yan bulgu — şema kısıtı sevk edilen sağlayıcıda çalışmıyor

Log her satırda `sema=kapali` diyor. Sebep ölçüldü:

```
sağlayıcı sınıfı : OpenAICompatibleSqlGenerator
select_cube var  : True
sema_kullanir    : False          ← `oneOf` desteklenmiyor (deepseek-v4-flash)
```

`llm_sema_kisitli` bayrağı **açık** olmasına rağmen `intent_semasi.cube_query_json_schema`
üretilmiyor. Yani modele **ne eşanlam ne şema** gidiyor: yapılandırılmış yardımın
**ikisi de yok**. Kurulum `B5` gereği doğru davranıyor (boşuna şema üretmiyor) — ama sonuç
şu: **bu sağlayıcıda Intent-JSON, elindeki iki koltuk değneğinden ikisini de kullanamıyor.**

### 1.6 Maliyet ölçüldü — öneri bedava değil, ama ucuz

```
bugünkü katalog : 12.115 char ≈ 4.038 token
eşanlam eki     :  6.577 char ≈ 2.192 token
toplam olurdu   : 18.692 char ≈ 6.230 token      (+%54)
```

Örnek zenginleştirilmiş satır (yalnız ölçüm için üretildi, koda girmedi):

```
oee = OEE | eşanlam: oee, verim, randiman, vardiya, kullanilabilirlik, availability,
      performans, durus | ölçü adları: ort_oee=oee, ort_kullanilabilirlik=kullanılabilirlik,
      ort_performans=performans, ort_kalite=kalite, toplam_durus_dakika=duruş
```

⚠ Ve bu ek **sabit bir önektir** (soru başına değişmez) → yol haritasının **üç katmanlı
önek** kararının tam olarak *"cache'lenir"* dediği katmana düşer. Yani `+%54` token,
prompt-caching borcunun (`B6`) ödenmesiyle **tekrar eden maliyet olmaktan çıkar**.

---

## 2 · Şikâyet #2 — anlatı merdiveni yok, tek basamak var

**Doğrulandı.** `app/answer.py::_anlati_ekle` (satır ~424):

```python
if "t2_anlatici" not in resolve_for(get_settings(), principal):
    return                      # KURAL B — kapalıyken davranış BİREBİR bugünkü
llm = getattr(request.app.state, "llm", None)
if llm is None or not hasattr(llm, "anlat"):
    return                      # kural-tabanlı sağlayıcı: YOL KAPALI, hata DEĞİL
gercekler = [f["text"] for f in (yorum.get("facts") or []) …]
…
plan = _planner.Planlayici(…)   # → LLM
```

Merdivenin bugünkü hâli:

| basamak | var mı | not |
|---|---|---|
| `interpret()` → **olgular** (deterministik) | ✅ | *"şu kadar arttı"* olguları LLM'siz üretiliyor |
| **şablon anlatı** (olguları düzyazıya çeviren, 0 token) | 🔴 **YOK** | planda vardı, **hiç yazılmadı** |
| LLM anlatı + `narration_guard` + `iddia` | ✅ | tek ve **varsayılan** basamak |

🔴 Yani anlatı için karar *"önce deterministik dene, karmaşıksa LLM"* değil, **"olgu üret →
doğrudan LLM"**. Deterministik olgular, LLM'in **girdisi**; **alternatifi değil**.

⚠ İkinci gözlem: bu, `t2_anlatici` hâlâ `alpha` iken bile **gecikmenin** ana kalemi.
Ölçülen: `ram 3 sorunlar neler neden düşük çıktı` → **39.422 ms** (iki LLM turu:
24.442 ms + 14.418 ms).

---

## 3 · Şikâyet #3 — 500 backend'den çıkmadı

### 3.1 Kanıt: canlı backend'in tüm ömründe sıfır 5xx

```
$ docker inspect dima-backend-core --format '…'
started=2026-08-07T09:07:59Z  restarts=0  oomkilled=false     ← log KESİNTİSİZ

$ docker logs dima-backend-core | grep -oE '"(GET|POST) [^"]+" [0-9]{3} …' | sort | uniq -c
     68 "GET  /schema"              200 OK
     14 "POST /ask"                 200 OK      ← hepsi 200
     13 "GET  /features"            401 Unauthorized
      3 "POST /ask/contribution"    200 OK
      1 "POST /cube"                200 OK
   … 5xx: HİÇ YOK
```

### 3.2 Kanıt: istek backend'e hiç ulaşmadı

Kullanıcının olay sırası ile logun sırası:

```
09:11:29  'makine bazında ortalama oee'   → netleştirme  (251 ms)
09:11:35  'bu yıl'                        → source=cube · 11 satır ✅  (OEE hesaplandı)
09:12:00  /cube 'geçen yıla göre kıyasla' → source=cube · 11 satır ✅
09:13:45  'personel verimliliklerini…'    → netleştirme (35.288 ms)
   ────────────  22 DAKİKALIK BOŞLUK — HİÇ /ask YOK  ────────────   ← 500 BURADA
09:34:49  POST /auth/refresh ×3                         ← ön yüz YENİDEN BAŞLADI
09:35:44  'makine bazında ortalama oee'   → thread=legacy-0 (yeni oturum)
```

Ve süreç tablosu bunu doğruluyor: `next dev` (pid 2288987) **12:34 yerel = 09:34 UTC**'de
başlatılmış — boşluğun bittiği an.

🔴 **Sonuç:** 500'ü üreten katman **Next.js dev sunucusunun rewrite-proxy'si**
(`next.config.ts` → `/api/:path* → ${BACKEND_ORIGIN}/:path*`). O sırada ön yüz süreci
ölü/derleme hâlindeydi; tarayıcıdaki axios bunu `Request failed with status code 500`
diye gösterdi. Dima **o isteği hiç görmedi**.

### 3.3 Yetenek çalışıyor — sorun gecikme

Aynı soru ön yüz düzeldikten sonra **başarılı**:

```
09:40:45  CEVAP /ask: q='ram 3 sorunlar neler neden düşük çıktı'
          source=cube+llm · satır=11 · süre=39.422ms
```

⚠ Ama **39 saniye**. `apiClient`'ta **hiçbir timeout tanımlı değil**
(`axios.create({baseURL, withCredentials, headers})` — `timeout` yok), yani kullanıcı
39 saniye boyunca **hiçbir geri bildirim almadan** bekliyor. Bir sonraki 500'ün en olası
sebebi budur.

### 3.4 Yan bulgu — `wren-engine` 651 kez yeniden başlamış

```
$ docker inspect b84deddc0a57_dima-wren-engine
StartedAt=2026-08-07T09:51:18Z  RestartCount=651
Caused by: java.io.FileNotFoundException: etc/config.properties (No such file or directory)
```

⚠ Bu konteyner **kalıntı** (ad öneki `b84deddc0a57_` = compose'un yeniden adlandırdığı yetim)
ve `/ask` çalıştığına göre **kullanılmıyor**. Ama sürekli yeniden başlayarak CPU yakıyor ve
**bir sonraki teşhisi kirletir**. Temizlenmeli.

---

## 4 · Olması gereken hâl

### 4.1 Katalog — LLM, `route()` ile **aynı** sözlüğü görmeli

| bugün | olması gereken |
|---|---|
| `route()` → tam eşanlam katmanı | aynı |
| LLM → yalnız kolon adları | 🔴 **aynı eşanlam katmanı** |

Değişmez: *"aynı bilgiyi iki tüketiciye iki farklı biçimde vermek, iki farklı sistem
kurmaktır."* Katalog üreticisi **tek** kalmalı; LLM'in gördüğü, `route()`'un gördüğünün
**alt kümesi olmamalı**.

### 4.2 Anlatı — iki basamak

```
olgular (interpret) ──► ŞABLON ANLATI ──► yeterli mi? ──evet──► yayımla   (0 token)
                                              │hayır
                                              ▼
                                    LLM anlatı + guard + iddia
```

⚠ Şablonun *"yeterli"* ölçütü **veri şeklinden** türetilmeli (tek ölçü + tek dönem +
tek kırılım → şablon; çoklu sinyal/neden sorusu → LLM), metin uzunluğundan değil.

### 4.3 Ön yüz — sessiz bekleme yasak

* `apiClient`'a **timeout** + kullanıcıya **ilerleme** (LLM turu başladı/bitti).
* Rewrite-proxy hatası ile backend hatası **ayırt edilebilir** olmalı: bugün ikisi de
  `500` görünüyor ve teşhis 20 dakika sürüyor.

---

## 5 · Öneriler — sıralı, gerekçeli

| # | öneri | neden bu sırada | risk |
|---|---|---|---|
| 🔴 **1** | `build_catalog`'a `display` + `synonyms` + `measure_synonyms_display` ekle | **9/9 `cube:null`'ın tek sebebi.** Kullanıcının 1 numaralı şikâyeti bununla kapanır | düşük — yalnız metin büyür (+%54 token) |
| 🔴 **2** | Ölçüm önce: aynı 3 soruyu **zenginleştirilmiş katalogla** koştur, `cube:null` oranını **önce/sonra** yaz | Bu depoda *"beyan var, ölçüm yok"* en pahalı hata sınıfı. Kazanç **kanıtlanmadan** kapatılmaz | — |
| 🔴 **3** | `{"cube":null}` oranını **kalıcı sayaç** yap (bugün yalnız `INFO` log) | *"LLM ne sıklıkla pes ediyor"* bugün **grep ile** öğreniliyor; kapıya çevrilemez | düşük |
| 4 | Ay adlarının **çekimli** hâli (`ocağa`, `şubata`, `martta`) — morfolojik çözüm | `ADR-0008`: kelime listesi **yasak**; mevcut ek motoruna bağlanmalı | orta |
| 5 | `apiClient`'a timeout + ön yüzde ilerleme göstergesi | 39 sn sessiz bekleme, bir sonraki *"500"*ün kaynağı | düşük |
| 6 | Anlatı şablon basamağı (§4.2) | `t2_anlatici` **alpha**; gecikmenin ana kalemi | orta |
| 7 | Prompt-caching (`B6`, üç katmanlı önek) | (1)'in `+%54` token'ını **tekrar etmeyen** maliyete çevirir | orta |
| 8 | Yetim `dima-wren-engine` konteynerini kaldır | 651 restart; teşhis gürültüsü | yok |

### 5.1 Ölçülmeden yapılmaması gerekenler

* ⛔ **`consistency_k`'yi düşürmek.** Uyuşmazlık **yaşanmadı** (aday hiç oluşmadı) — k'yi
  düşürmek bu vakada **hiçbir şey** düzeltmez, yalnız gerçek belirsizlikte körleşir.
* ⛔ **Netleştirme dallarını kapatmak.** `netlestirme_onceligi` zaten **OFF**; çapraz-konu
  dalı LLM **pes ettikten sonra** çalışıyor. Kapatmak, `cube:null` vakasını *"cevap yok"*a
  çevirirdi — daha kötü.
* ⛔ **Sağlayıcıyı `oneOf` destekleyene çevirmek** — önce (1) ölçülmeli. Şema kısıtı
  eşanlam eksikliğini **telafi etmez**: şema da teknik adlarla yazılıyor.

---

## 6 · Bu raporun kendi sınırları

* Ölçümler **tek kurulumda** (`demo-boyahane`, 23 cube, openrouter/`deepseek-v4-flash`)
  yapıldı. Başka sağlayıcıda `cube:null` oranı farklı olabilir — ama **katalogda eşanlam
  yokluğu sağlayıcıdan bağımsızdır**.
* `%54` token artışı **tahmini biçimlendirmeye** dayanıyor; gerçek ek, seçilecek satır
  biçimine göre değişir.
* 500'ün **kesin** sebebi (ön yüz süreci neden öldü) ön yüz terminal çıktısı olmadan
  belirlenemedi; kanıtlanan şey **backend'in onu hiç görmediğidir**.
* Şikâyet #2 için *"şablonun yeterliliği"* ölçütü bu raporda **önerilmiştir, ölçülmemiştir**.

---

## 7 · Kanıt komutları (yeniden üretmek için)

```bash
# LLM çağrıldı mı + ne cevap verdi
docker logs dima-backend-core | grep -E "dima.llm:|dima.ask: CEVAP|whitelist REDD"

# Bayrakların canlı hâli
docker exec dima-backend-core python -c "
import app.features as F; from app.config import Settings
print(F.resolve_for(Settings(), None)); print(F._db_overrides())"

# LLM'in GERÇEKTEN gördüğü katalog
docker exec dima-backend-core python -c "
import app.cube_router as cr; from app.config import Settings
from app.wren_service import WrenService
s=Settings(); w=WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
  connection_info=s.connection_dict(), company_slug=s.company)
cat,_=cr.build_catalog(w.schema()); print(cat[:2000])"

# Şemanın TAŞIDIĞI ama kataloga GİRMEYEN alanlar
docker exec dima-backend-core python -c "… oee.get('synonyms') …"

# 5xx var mı
docker logs dima-backend-core | grep -oE '\" [0-9]{3} ' | sort | uniq -c
```

---
---

# EK DENETİM (aynı gün, 13:00–14:00 yerel) — *«anlamadım» bir cevap sınıfı olmamalı*

**Talimat:** *"Kişi tamamen anlamsız bir şey yazmadıkça sistem «anlamadım» dememeli;
en fazla «anladım, isteğiniz şu, ama şu anda bunu yapabilecek yeterliliğim yok»
demeli. Yanlış anlama ve «şunu mu dediniz» de sıkıntı."*

**Yöntem:** kod okuma + **yerinde ölçüm** (sıfır LLM, sıfır DB, ağ kapalı). Ölçümler
kaynak ağacının **o anki hâlinden** kuruldu (`izole_proje_ayna` + `compose_and_build`);
konteynerdeki imaj kullanılmadı — çünkü çalışma ağacında `cube_router` dâhil dokuz
modül değişik. *(Bayat artefakttan ölçmenin bedeli 2026-08-06’da ödenmişti; tekrarlanmadı.)*

> ⚠ Bu bölüm de bir **denetim raporudur**. Hiçbir kod değiştirilmedi.

---

## 8 · Yönetici özeti — talep haklı, ama kusur sanılan yerde değil

| # | bulgu | kanıt |
|---|---|---|
| 🔴 **A** | **Niyetin LLM'e giden kanalı, başarısızlıkta BİR BİT genişliğinde.** Sözleşme `CubeQuery` **ya da** `{"cube":null}`. Modelin *anladığını yazacağı alan YOK* | `llm.py:354-372` · `intent_semasi.py:79-87` |
| 🔴 **B** | **Sistem neden pes ettiğini BİLİYOR ve yalnız geliştiriciye söylüyor.** 10 kodluk teşhis tablosu → tek tüketici bir **telemetri kolonu** | `cube_router.py:3134` · `answer.py:234` |
| 🔴 **C** | *"Ne anladım"* mekanizması (`temellendirme`, 0 token) **`cube_query` yoksa yapısal olarak susar** — yani tam da gerekli olduğu yerde | `answer.py:633` |
| 🔴 **D** | *"Anladım ama yapamıyorum"* modülü **var** (`yetenek.py`) ama **sırası gelmiyor**: dört netleştirme çıkışı hem onu hem Discovery'yi atlatıyor | `ask.py:3596` ↔ `3644` |
| ⚠ **E** | **Tek-ses kataloğu bu dört çıkışa bağlanmamış**; katalogun yumuşak cümlesi (`netlestirme.olcu`) **sıfır tüketicili** | `soz.py:89` · `ask.py`'de `soz=` 8 yerde |
| ✅ **F** | Ön yüz **hazır**: `soz` ve `eksik_niyet` zaten çiziliyor. Boşluk **yalnız arka uçta** | `ReportCard.tsx:654,915` |

🔴 **Tek cümlede:** *sistem, anladığı yarıyı atıyor; anlamadığı yarıyı kullanıcıya
okuyor.* Bu bir model kusuru değil, bir **sözleşme kusuru**dur — ve talimat tam olarak
o sözleşmeyi hedefliyor.

---

## 9 · Bulgu A — LLM'in *"anladım"* diyecek bir alanı yok

Intent basamağının modelden istediği **tek** şey:

```python
# app/llm.py:354  _cube_select_system()
"- SADECE JSON döndür (SQL YOK, açıklama YOK).\n"
'- Biçim: {"cube":"<ad>","measures":[…],"dimensions":[…],…}\n'
'- Soru tek bir cube ile yanıtlanamıyorsa … KESİNLİKLE {"cube":null} döndür.\n'
```

Ve şema-kısıtlı biçimde ilk dal:

```python
# app/intent_semasi.py:79
dallar = [{"title": "cevaplanamaz",
           "properties": {"cube": {"type": "null"}}, "required": ["cube"],
           "additionalProperties": False}]     # ← başka alan YASAK
```

`additionalProperties: False` — yani model *"personel kırılımıyla verimlilik istiyor"*
diye **yazmak istese bile şema onu reddeder**.

### 9.1 Sağlayıcı protokolünün tamamı tarandı

| yöntem | ne üretir | *"ne anladım"* taşır mı |
|---|---|---|
| `generate_sql` · `generate_followup_sql` · `repair` | SQL | ✗ |
| `select_cube` · `refine_cube` | CubeQuery \| null | ✗ |
| `anlat` | olgulardan düzyazı (**cevap varken**) | ✗ |
| `plan_sec` | araç sırası | ✗ |
| `sinonim_oner` | katalog bakımı | ✗ |
| `prompt_enhance` | soruyu katalog terimleriyle **yeniden yazar** | ◐ **en yakın** |

🔴 **Dokuz giriş noktası, sıfır anlama beyanı.** Tek yaklaşan `prompt_enhance` ve canlı
kurulumda **kapalı** (§1.1: `prompt_enhancer = OFF`). Dahası kendi prompt'u (`llm.py:296`)
*"katalogda GEÇEN terimlerle yeniden yaz"* diyor — yani **§1.3'ün eşanlamsız kataloğuna
bağlı**. Aynı kök neden, ikinci LLM girişini de sakatlıyor.

> *Bir modele «anladığını söyle» demeyen sistem, aldığı sessizliği anlayışsızlık sanar.*

---

## 10 · Bulgu B — teşhis üretiliyor, kullanıcıya değil **veritabanına** gidiyor

`cube_router` reddin gerekçesini **kodlayarak** saklıyor:

```python
# app/cube_router.py:3134
RED_KODLARI = {"R1": "cube eşleşmedi", "R2": "liste/döküm niyeti", "R3": "kıyas dili",
               "R4": "ölçü eşleşmedi", "R5": "ortalama ölçü tanımlı değil",
               "R6": "dışlama yarım", "R7": "boyut adayı tek değil",
               "R8": "yarı-toplanabilir + zaman kovası", "R9": "kırılım istendi, boyut yok",
               "R10": "kapsam kapısı — tanınmayan kelime"}
```

**Tüketici taraması:**

```
$ grep -rn "RED_KODLARI" app/          → 1 satır (kendi tanımı)
$ grep -rn "red_gerekcesi\|teshis(" app/ → answer.py:235  (tek üretim tüketicisi)
```

```python
# app/answer.py:234 — InteractionLog satırı
reject_reason=_teshis(body.question, _sema(request)),
```

🔴 **Teşhis bir telemetri kolonudur.** Kullanıcıya dönen `note` alanı onu **hiç
görmüyor**. Ve `soz.JARGON` listesi `"r1"`, `"r10"` dizgelerini kullanıcı metninde
**yasaklıyor** — doğru bir yasak; ama on kodun **kullanıcı dilindeki karşılığı hiç
yazılmadı**. Yasak var, çeviri yok.

### 10.1 Ölçüm — teşhis ne diyor

Gerçek-dünya korpusunun **elle yazılmış** 42 vakası (`lab/gercek_dunya.VAKALAR`),
`route()` hepsini reddediyor:

```
ham kapı kodu → teshis()
    21  R1  → R10
    10  R10 → R10
     5  R1  → R1
     4  R4  → R10
     1  R4  → R4
     1  R9  → R10
```

⚠ **36/42 (%86) `R10`.** `teshis()` tanınmayan kelime varsa onu öne alıyor — `KÖK-9`'un
kararı ve gerekçesi doğru. Ama sonuç şu: **kullanıcıya söylenebilecek en zengin bilgi
(hangi ölçü eşleşti, hangi kırılım yok) teşhis kodunun içinde YOK**; kod yalnız
*"bir kelimeyi tanımadım"* diyor. Yani B'nin çözümü *"R kodunu yaz"* değil — **eşleşmeyi
yaz**.

---

## 11 · Bulgu C — *"ne anladım"* motoru retlerde YAPISAL OLARAK susuyor

`app/temellendirme.py` bu talimatın tam karşılığı: **0 LLM · 0 token**, *"sistem ne
anladığını söyler"*. Kapısı:

```python
# app/answer.py:633
if not resp.cube_query:
    return                     # ← düz retlerde cube_query BOŞ
```

Ve kapının kendi yorumu bunu **açıkça** yazıyor:

> *"⚠ Gürültü riski yok: düz retlerde `cube_query` **boştur** (ölçüldü: `{}`)…"*

🔴 O cümle, gürültü gerekçesiyle **tam da bu talimatın istediği davranışı** dışarıda
bırakıyor: sistem *"anladığım şu"* diyebilmek için **önce bir sorgu kurabilmiş olmak**
zorunda. Sorguyu kuramadığı an — yani kullanıcının açıklamaya en çok ihtiyaç duyduğu
an — **susuyor**.

⊙ Aynı asimetri `uyum.py`'de de var ve orada **doğru** çözülmüş: `eksik_niyet` +
`kismi_cevap_notu` *"cevap gitti ama eksik"* der (korpus: `beyanli_kismi = 72`). Yani
**«cevap var + eksik» beyanı yazıldı; «cevap yok + anladığım şu» beyanı yazılmadı.**
İkisi aynı desenin iki yarısıdır.

---

## 12 · Bulgu D — *"yapamıyorum"* kapısı VAR ama sırası gelmiyor

`app/yetenek.py` üç kutu tanımlıyor — ve **ikisini** uyguluyor:

| kutu | sabit | durum |
|---|---|---|
| `anlamadim` | — | 🔴 **hiç yazılmadı** (docstring tablosunda var, kod yok) |
| `yapamiyorum` | `KUTU_YAPAMIYORUM` | ✅ olumsuzluk |
| `yapmiyorum` | `KUTU_YAPMIYORUM` | ✅ forecast · iki-cube |

### 12.1 Sıra ölçüldü

```
ask.py:3596   fresh = _try_fresh_intent()   →  truthy dönerse RETURN
ask.py:3629   yol sınırı (kullanıcı tercihi)
ask.py:3644   _yetenek.kapsam_disi(...)     ←  YETENEK KAPISI
ask.py:3651   _run_discovery()              ←  ikinci LLM
```

`_try_fresh_intent` (2688–3181) LLM pes ettikten sonra **dört truthy çıkış** taşıyor:

| satır | kullanıcının gördüğü | sınıf |
|---|---|---|
| `3015` | *"«X» yerine «Y» mi demek istedin?"* | 🔴 yanlış-anlama önerisi |
| `3100` | *"«X» başka bir konu gibi görünüyor."* / *"«X» kısmını anlayamadım."* | 🔴 anlamadım |
| `3128` | *"…hangi ölçüyü istediğini anlayamadım."* | 🔴 anlamadım |
| `3176` | *"Neyi karşılaştırmak/görmek istediğini anlayamadım…"* | 🔴 anlamadım |

🔴 Bu dördünden biri ateşlediğinde **hem yetenek kapısı hem Discovery atlanır.** Yani
kullanıcı, cevaplayabilecek ikinci LLM basamağını **görmeden** *"anlamadım"* alır —
canlı turda ölçülen tam olarak buydu (§1.4).

### 12.2 ⚠ Ama sıra düzeltmesi TEK BAŞINA az iş görür — ölçüldü

42 vakalık gerçek-dünya korpusunda:

```
yetenek.kapsam_disi bir sınır BEYAN EDEBİLİYOR : 1 / 42
netleştirmenin onu ÖRTTÜĞÜ vaka               : 0
```

> 🔴 **Sıra kusuru gerçek ama nüfusu küçük.** *"Kapıyı yukarı al"* refleksi bu vakada
> neredeyse hiçbir şeyi düzeltmez; çünkü eksik olan **kapının yeri** değil,
> **söylenecek cümlenin kendisi**. Bunu ölçmeden yapmak, doğru işi yanlış yerde
> aramaktı.

### 12.3 Çıkış dağılımı — nüfus

Aynı 42 vaka, `_try_fresh_intent` merdiveni birebir taklit edilerek:

```
    20   47,6%   Discovery'ye geçiş
     8   19,0%   ANLAMADIM: hiçbir konu tanınmadı
     8   19,0%   ANLAMADIM: «X» kısmını anlayamadım
     2    4,8%   ANLAMADIM: «X» başka bir konu
     2    4,8%   SORU: hangi ölçü (konu belli)      ← meşru netleştirme
     1    2,4%   SORU: «X» yerine «Y» mi
     1    2,4%   cevap (yazım düzeltmesiyle)

«anlamadım» sınıfı : 18 / 42  = %42,9
"şunu mu dedin"    :  3 / 42  =  %7,1
```

⚠ **Payda seçimi kasıtlı.** Üretilmiş korpus (~2 300 vaka) **≥%97,1 katalog türevidir**
(`tests/test_gercek_dunya_korpusu.py:5`) — yani sistemin **kendi kelimelerini** sorar ve
bu soruda *"anlamadım"* oranını **yapay olarak düşürür**. Elle yazılmış 42 persona
vakası, bu talimatın doğru paydasıdır. Üretilmiş korpusla koşum başlatıldı ve
**bilerek durduruldu**; gerekçe budur.

---

## 13 · Bulgu E — tek-ses kataloğu bu dört çıkışa bağlı değil

`app/soz.py:19` kuralı **birebir bu talimattır**:

> **«Kural: ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR.»**
>
> | bugün | olacak |
> |---|---|
> | *"Hangi dönem için?"* | *"Fire toplamını çıkarabilirim — **hangi dönem?**"* |
> | *"…tanıdığım konu geçmiyor"* | *"Bu soruda tanıdığım bir ölçü yakalayamadım. **Şunlardan biri mi?**"* |

Ölçüm:

```
soz.KATALOG kaydı        : 15
ask.py'de `soz=` atanan  :  8 yer
§12.1'in dört çıkışında  :  0    ← hiçbiri katalogdan geçmiyor
netlestirme.olcu tüketici:  0    ← katalogun YUMUŞAK cümlesi ölü
```

🔴 Katalogun *"olacak"* sütununa yazdığı cümle (`netlestirme.olcu`) **yazıldı ve hiç
bağlanmadı**; onun yerine geçeceği *"form doğrulayıcısı"* cümle **hâlâ `ask.py:3176`'da
satır içi**. Yani karar alındı, kayda geçti, **uygulanmadı**.

⊙ İyi haber: desen zaten çalışıyor. `_period_gate` (`ask.py:2036`) `temellendirme`den
*"anladığım ölçü"*yü çekip `netlestirme.donem`'in `{ne}` yuvasına koyuyor —
*"Fire kg'yi çıkarabilirim — hangi dönem?"*. **Aynı üç satır**, dört red dalında yok.

---

## 14 · İki canlı sorunun yeniden okunması — sistem NE BİLİYORDU

Ölçüm (taze şema, 23 cube):

| soru | `route()` | ham→teşhis | `partial_unknowns` | `yetenek` |
|---|---|---|---|---|
| `personel verimliliklerini kıyasla` | pes | `R10→R10` | bilinmeyen=`[personel]` · **eşleşen ölçü=`ort_oee`** | — |
| `şubatta ocağa göre ciro artışı…` | pes | `R4→R10` | bilinmeyen=`[ocaga, ciro]` · **eşleşen ölçü=`toplam_ciro`** | — |
| `bu gidişle yılı nerede kapatırız` | pes | `R1→R10` | — | `yapmiyorum/forecast` |
| `firesiz partiler kaç tane` | pes | `R4→R10` | — | `yapamiyorum/olumsuzluk` |
| `fire ve rework birlikte` | pes | `R1→R10` | — | `yapmiyorum/iki_cube` |

🔴 **İlk satır bu raporun özeti.** Sistem, *"personel verimliliklerini kıyasla"* için
şunların **hepsini** biliyor:

* `verimlilik` → **`oee.ort_oee`** eşleşti *(hits)*
* `personel` → bu konuda **yok** *(unknown)*
* soru bir **kıyas** *(`Niyet.turler = {kiyas}`)*

ve kullanıcıya dediği: ***"«personel» başka bir konu gibi görünüyor."***

Söylenebilecek olan — **yeni hiçbir bilgi gerektirmeden**:

> *"Verimliliği (OEE) kıyaslayabilirim — ama «personel» kırılımı bu konuda yok.
> Makine, hat ya da vardiya kırılımıyla bakabilirim."*

⚠ Cümledeki üç kırılım **uydurulmadı**, katalogdan okundu: `oee.dimensions =
[makine, hat, vardiya, hafta_gunu]` (`demo/packs/modul/oee/cubes/oee/metadata.yml:81`).
Yani öneri, `_dogrulanmis_chipler` disiplininin **zaten** karşıladığı bir şeydir.

### 14.1 Yan bulgu — `ciro` aynı anda «bilinmeyen» ve «eşleşen»

İkinci satır: `partial_unknowns` `ciro`yu **bilinmeyen** listesine koyuyor **ve** aynı
çağrıda `toplam_ciro`yu eşleşen ölçü olarak döndürüyor. İçeride bu tutarlı — *"seçilen
cube'a göre bilinmiyor"* demek. Ama o liste **doğrudan kullanıcı metnine basılıyor**
(`ask.py:3075`) ve canlı nota `"ocaga ciro" başka bir konu gibi görünüyor` diye
sızıyor (§1.4).

🔴 Yani kullanıcı, **eşleşmiş bir ölçünün adını** *tanınmayan kelime* olarak geri
alıyor. İç doğru, dış yanlış — ve bu, *"yanlış anlama"* şikâyetinin somut kaynağı.

### 14.2 `Niyet` nesnesi — çatı var, anlama yarısı boş

`KÖK-1`'in niyet nesnesi (`app/niyet.py`) `coz(soru, schema)` ile zenginleşiyor. Ölçüldü:

```
personel verimliliklerini kıyasla
    bilinmeyenler  = ['personel']          ← partial_unknowns'tan
    olcu_adaylari  = []                    ← measure_cube_candidates'tan  🔴
```

⚠ İki alan **iki ayrı eşleştiriciden** doluyor: `bilinmeyenler` ← `partial_unknowns`,
`olcu_adaylari` ← `measure_cube_candidates`. Birincisi *"`ort_oee` eşleşti"* diyor,
ikincisi hiçbir şey bulmuyor — ve nesneye **yalnız ikincisinin sessizliği** yazılıyor.

> 🔴 *Tek çatı, anladığını değil anlamadığını topluyor.* `Niyet`'in kendi docstring'i
> *"bir sistemin temsil edemediği şeyi SAYABİLMESİ, onu görebilmesinin ilk adımıdır"*
> diyor; bu satır o adımın **yarısının atılmadığını** gösteriyor.

---

## 15 · Olması gereken hâl — üç değişmez

**1 · `{cube:null}` bir CEVAP değil, bir DEVİRDİR.**
Yapısal red **içeride kalır** (§`intent_semasi`'nin gerekçesi doğrudur: *"hiçbiri"*
seçeneği olmayan bir şema modeli yanlış seçime **zorlar**). Ama o dal artık kullanıcıya
çıkan bir cümle üretmez; bir sonraki basamağa **devreder**.

**2 · Kullanıcıya çıkan her ret üç parçalıdır.**

```
[anladığım]            ← temellendirme/partial_unknowns'un ZATEN ürettiği eşleşme
[sınır]                ← teşhis + yetenek kutusu, KULLANICI DİLİNDE
[yapabildiğim]         ← doğrulanmış chip (_dogrulanmis_chipler ZATEN var)
```

Üçünün de üreticisi **bugün mevcut**; eksik olan, red dalının onlara **bağlanmamış**
olması.

**3 · Tek istisna: veri niyeti taşımayan ifade.**
*"teşekkürler"*, *"asdf zxcv"* → sosyal/menü yolu (`_SOSYAL`, `ask.py:2260`) zaten
doğru davranıyor. Talimatın *"tamamen anlamsız"* kaydı **tam olarak budur** ve kapsamı
dardır.

---

## 16 · Öneriler — sıralı, gerekçeli, ölçütlü

| # | öneri | neden bu sırada | ölçütü |
|---|---|---|---|
| 🔴 **1** | **Red dalları `_honest_refusal` benzeri TEK huniden geçsin** ve huni `soz` + *"anladığım"* cümlesini eklesin | Dört dal bugün huniyi atlıyor (`3015·3100·3128·3176`); türetme chip'i de o yüzden görünmüyor (§13) | 42 vakada `soz` dolu ret oranı 0 → 100 |
| 🔴 **2** | **`temellendirme.kur()` kapısı `cube_query` yerine `eşleşen ölçü` ile açılsın** | *"Ne anladım"* motoru zaten var ve **0 token**; tek engel §11'deki tek satırlık kapı | *"anladığım"* satırı taşıyan ret sayısı |
| 🔴 **3** | **`Niyet.olcu_adaylari` `partial_unknowns`'un hits'iyle de beslensin** | İki eşleştirici aynı nesneye çelişik cevap veriyor (§14.2); *"anladığım"* cümlesinin **girdisi** budur | `personel verimliliklerini kıyasla` → `olcu_adaylari` boş DEĞİL |
| 🔴 **4** | **Intent sözleşmesine `anladigim` + `eksik` metin alanları** — `{"cube":null,"anladigim":"…","eksik":"personel kırılımı"}` | LLM'in *"anladım"* diyebileceği tek yer; §1.3'ün eşanlam düzeltmesiyle **birlikte** ölçülmeli | `cube:null` cevaplarının kaçında `anladigim` dolu |
| 5 | `netlestirme.olcu`'yu bağla; `ask.py:3176`'nın satır içi metnini kaldır | Karar alınmış, uygulanmamış (§13) | katalogda sıfır-tüketicili kayıt: 2 → 1 |
| 6 | **Kapı testi:** kullanıcıya giden hiçbir metin, yanında *"anladığım"* cümlesi olmadan *"anlayamadım/anlamadım"* içeremez | `soz.JARGON` kapısının aynı deseni; beyan çürümesini **kapıyla** durdurur | yeni test kırmızıdan yeşile |
| 7 | `partial_unknowns`'un çıktısı **kullanıcı metnine ham basılmasın** (§14.1) | *"Yanlış anlama"* şikâyetinin somut kaynağı | `"ocaga ciro"` gibi not üretilemez |
| 8 | `prompt_enhancer`'ı §1.3 düzeltmesinden **sonra** aç | Bugün eşanlamsız katalogla çalışıyor; erken açmak ölçümü kirletir | `cube:null` oranı önce/sonra |

### 16.1 Ölçülmeden yapılmaması gerekenler

* ⛔ **`{cube:null}` dalını şemadan kaldırmak.** `intent_semasi`'nin gerekçesi ölçülmüş:
  *"hiçbiri"* yoksa model **illa birini seçer** → sessiz-yanlış. Talimat bu dalı değil,
  onun **kullanıcıya çıkan cümlesini** hedefliyor.
* ⛔ **Yetenek kapısını yukarı almak — tek başına.** Ölçüldü: örtüşme **0/42** (§12.2).
* ⛔ **Netleştirme dallarını kapatmak.** Chip'ler doğru üretiliyor; kusur **cümlede**.
* ⛔ **`R11`'i geri getirmek.** Ölçüldü ve geri alındı (`tests/test_r11_ifade_edilemez.py`)
  — çünkü **geliştirici teşhisini** örtüyordu. ⚠ Ama geri alınan şey **teşhis kodudur**,
  bu raporun istediği **kullanıcı cümlesi değildir**. İkisi karıştırılmamalı: `R11`'in
  kullanıcıya bakan yarısı **hiç yazılmadı**.

---

## 17 · Bu ek raporun sınırları

* Nüfus ölçümü **42 elle yazılmış** persona vakası üstünde. Küçük bir paydadır; seçimi
  §12.3'te gerekçelendirildi ama **dar** olduğu kabul edilir. Üretilmiş korpusla ikinci
  bir tur, *"anlamadım"* oranını **düşük** gösterecektir — o sayı bu soru için yanıltıcıdır.
* Çıkış merdiveni **taklit edilerek** ölçüldü (`_try_fresh_intent`'in dal koşulları
  birebir kopyalandı), uçtan uca `/ask` koşulmadı: LLM ve DB kapalıydı. LLM açıkken
  `cube:null` dönmeyen sorular bu dağılımdan **düşer** — canlı turda oran 9/9 `null`'du,
  yani bugünkü kurulumda düşüş **beklenmez**.
* §16'nın 4 numaralı önerisi (şemaya metin alanı) **ölçülmedi**; token maliyeti ve
  sessiz-yanlış etkisi bilinmiyor. Serbest metin **hiçbir zaman sorguya dönüşmediği**
  için yapısal riski düşük görünüyor — ama *"görünüyor"* bir ölçüm değildir.
* ⚠ **Çalışma ağacı ölçüm sırasında canlıydı** (paylaşılan dizin, ikinci bir
  geliştirici eş zamanlı çalışıyor). Ölçüm turu boyunca `MIMARI.md`,
  `lab/nl_corpus.py` ve `tests/test_cevapsiz_kesme.py` değişti; ölçümün okuduğu
  modüller (`cube_router` · `niyet` · `yetenek` · `typo_onerisi`) **değişmedi**,
  ama tekrar üretimde ağacın **aynı** hâli kullanılmalıdır.
* `yetenek.kapsam_disi` yalnız **üç** sınır tanıyor. *"Boyut yok"* (`personel`) sınıfı
  hiçbir modülde yok; §16'nın 1–3'ü onu üretir, ama o üretim **yeni bir sınıf** açar ve
  yanlış-pozitifi ölçülmeden açılmamalıdır.

---

## 18 · Kanıt komutları (yeniden üretmek için)

```bash
# Ölçüm konteyneri — ÇALIŞMA AĞACINDAN, salt-okunur, ağsız
docker run --rm --network none \
  -v "$PWD/backend":/work/backend:ro -v /tmp/olcum:/out \
  -e DENETIM_KOK=/work/backend -e TMPDIR=/out/tmp -e DIMA_VQR_EMBEDDER=off \
  -w /work/backend --entrypoint python \
  dima-backend-feat-wren-strict-agentic_dima-backend /out/olc_anlamadim.py

# LLM'in "anladım" diyecek alanı var mı
sed -n '354,372p' backend/app/llm.py          # prompt sözleşmesi
sed -n '79,87p'   backend/app/intent_semasi.py # additionalProperties: False

# Teşhis kimin okuduğu
grep -rn "RED_KODLARI\|red_gerekcesi\|teshis(" backend/app/

# "Ne anladım" motorunun kapısı
sed -n '630,640p' backend/app/answer.py

# Tek-ses kataloğunun ölü kayıtları
grep -rn "netlestirme.olcu" backend/app/ | grep -v soz.py   # → boş
```

⚠ **Ölçüm aracının kendi tuzağı (yeniden üretmek isteyene):** `lab/izolasyon.py` gerçek
`demo/`deki **artakalan `wren-project.compose.lock`** dosyasını da aynaya sembolik bağla
kopyalar. Salt-okunur kaynakta derleme `EROFS` verir; **yazılabilir** kaynakta ise
"izole" iki koşum **aynı kilidi paylaşır** — yani izolasyon o noktada sızıyor. Ölçüm
betiği bağı siliyor; kalıcı çözüm `_CIKTI` süzgecinin `*.compose.lock`'u da kapsaması
olurdu. *(Kapsam dışı; tek cümlelik kayıt.)*
