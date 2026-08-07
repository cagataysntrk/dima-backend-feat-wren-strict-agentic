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
