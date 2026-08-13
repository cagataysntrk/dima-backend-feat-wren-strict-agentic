r"""🔴 `FAZ 5` — **ÖNERİ MOTORU** (yazarken-ara / typeahead).

Kullanıcı yazarken katalogdan aday terim önerir. **Saf**: sorgu koşmaz, LLM çağırmaz,
`/ask` yoluna **hiç** dokunmaz (`E-8`: sıcak yolda seri ikinci tur yok).

## Ön koşul — ve neden yazılı

`FAZ 0` ölçtü: **`Recall@3 = %89,5`** (vektör ayağı, `intfloat/multilingual-e5-large`,
payda **19**). Eşik `%85`'ti; faz bu ölçümle açıldı. Kapı:
`tests/test_oneri_on_kosulu_model_kimligi.py` — üretim gömücüsü ölçülenden ayrılırsa
kırmızı verir 🅕.

## 🔴 `5.2` — YETKİ SÜZMESİ **SIRALAMADAN ÖNCE** (fazın tek güvenlik kalemi)

Bir öneri listesi **envanterdir**. Yetkisiz bir ölçünün adını açılır listede göstermek,
o ölçüyü koşturmaya izin vermesek bile **bilgi sızıntısıdır**. Bu yüzden süzme
**sıralamadan önce** yapılır: sıralama yalnız **görmeye hakkı olan** kümede çalışır.

⚠ ㊱ **Planın adlandırması yanlıştı ve düzeltildi.** Plan *«`authorize()` süzmesi»*
diyordu; ölçüldü ki `authorize(principal, action, resource)` **eylem düzeyi** kaba bir
kapıdır (Katman A) ve izin varsa **sessiz döner** — kaynak başına süzemez. Kaynak
başına yetki **Katman B**'dedir: `katman_b.karar(referanslar, izinliler)`, **saf**
fonksiyon, ve *«yapılandırılmamış»* (`izinliler is None`) ile *«boş allowlist»*
ayrımını **o** taşır. Burada o fonksiyon **çağrılır**; ikinci bir yetki kuralı
yazılmaz (`KAT-1`).

Küp → model bağı `base_object`'tir (`wren_service.py:793`).

## `5.8` — Gömücü soğuksa ÇÖKME, leksik kipe düş

`vqr._embedder()` tembel ve **bloklamayan**: başka bir iş parçacığı modeli indiriyorsa
`None` döner (ölçülmüş kusur: eskiden bloklayan kilit bir isteği **dakikalarca**
astırıyordu). Bu modül o `None`'ı bir **hâl** olarak kabul eder — vektör ayağı düşer,
leksik ayak cevabı verir, `kip` alanı bunu **beyan eder** 🅖.

## Füzyon — `k` bilinçli seçildi ve YAZILDI

RRF (`1/(k+sıra)`) için literatürün `k=60`'ı **uzun** listeler içindir; orada amaç
sıra farklarını **yumuşatmaktır**. Burada aday havuzu kısadır (ayak başına `_HAVUZ`),
ve `k=60` seçilseydi `1/61` ile `1/70` arasındaki fark **binde bir**e inerdi: füzyon
**hiçbir şey sıralamaz**, çıktı iki ayağın rastgele birleşimi olurdu. Bu yüzden
`_RRF_K = 10` — sıra **anlamını korusun** diye.

⚠ 🅖 **Bu sayı kalibre EDİLMEDİ**, seçildi. Kalibrasyonu `FAZ 0` paydasının **19 → 30–40**
büyütülmesine bağlıdır (açık borç). Bir sayının gerekçesi olması, ölçülmüş olması
demek değildir.

## ⚠ MUTLAK EŞİK YOK

`FAZ 0`'ın ikinci bulgusu bağlayıcı: gürültü kelimesi *«vardya»* kosinüs **0,851**
aldı — yani *«skor > X ⇒ iyi aday»* **çalışmaz**. Bu modül hiçbir yerde çıplak bir
kosinüs eşiği kullanmaz; vektör ayağı yalnız **sıra** üretir. Leksik ayakta kullanılan
eşik (`_TYPO_MID`) katalog kelimeleri için **kalibre edilmiş** bir sabittir ve
`cube_router`'dan **ödünç alınır**, yeniden tanımlanmaz (`KAT-1`).

## 🔴🔴 `§18.7` — GÖMÜLEN ŞEY **ALAN ADI DEĞİL**, ÇOK GÖRÜNÜMLÜ TEMSİLDİR

⟳ **DÜZELTİLDİ (2026-08-13).** Bu modül `FAZ 0`'ın ölçtüğü şeyi **koşmuyordu**.

`FAZ 0` (`lab/oneri_olcum.py::gorunumler`) her ölçüyü **çok görünümlü** bir havuzla
ölçtü — ad · etiket · sinonimler — ve `Recall@3 = %89,5` sayısı **oradan** çıktı.
Üretimdeki bu modül ise ölçü başına **tek** bir metin gömüyordu: çıplak görünen
etiket. Yani kapıdaki sayı ile koşan kod **aynı temsili paylaşmıyordu**.

⊙ **Ölçüldü (aynı etiketli küme, `ara()` boru hattının tamamı, payda 19):**

| temsil | `Recall@1` | `Recall@3` | `MRR` |
|---|---|---|---|
| çıplak etiket *(önceki üretim)* | %68,4 | **%68,4** | 0,703 |
| **çok görünümlü** *(bu hâl)* | %89,5 | **%89,5** | **0,895** |

🔴 `§13.1`'in karar tablosuna göre **%68,4 «🔴 DUR» bandındadır** (`< %70`) — yani
üretim, planın ölüm şartını **sağlamayan** bir temsille koşuyordu ve bunu kimse
görmüyordu, çünkü ölçüm aracı **kendi** havuzunu kuruyordu 🅕.

*Bir ölçümün taşınabilmesi için, ölçtüğü temsilin üretimde de kurulmuş olması gerekir;
aksi hâlde yayınlanan sayı başka bir sistemin sayısıdır.*

### Dört görünüm — üçü de zaten katalogda (`§18.7`: *«ek yazım işi yok»*)

```
alan: surdurulebilirlik.toplam_su_lt
 ├ ① görünen etiket : "su"            ← measure_synonyms_display
 ├ ② sinonimler     : "su, su tüket, toplam su"  ← cube_synonyms.yml
 ├ ③ küp bağlamı    : "sürdürülebilirlik · su"   ← cube `display`
 └ ④ birim          : "su (lt)"                  ← measure `unit`
```

Sorgu **en yakın görünüme** eşleşir, alan o görünümden **türer**; bir alan birden çok
görünümden gelirse **tekilleştirilir** — en iyi görünüm kazanır (`max`). Bu bir füzyon
değil bir **temsil** kararıdır: aday havuzu hâlâ **alan** başınadır, görünüm sayısı
sıralamayı şişirmez.

### 🔴 `①`'in inceliği: **BAĞLAMSIZ KISA AD GÖMÜLMEZ** (`_KISA_ESIK`)

Ölçülen kusur (canlı curl, 2026-08-13): `q=fi` → `fire·oee, fire·parti, fırsat adedi,
fire oranı, **su·surdurulebilirlik**, **set·enerji_tesis**`. Son ikisi alakasız.
Sebep `§18.6`'nın işaret ettiği yer: `toplam_su_lt`'nin görünen etiketi **`"su"`**,
`set_tep_ton`'unki **`"set"`** — iki karakterlik bir sorgu (`fi`) ile iki karakterlik
bir etiket arasındaki kosinüs, **anlamdan değil kısalıktan** gelir.

Bu yüzden `①` çıplak etiketi **yalnız kendi başına durabiliyorsa** gömer; kısaysa küp
bağlamına füzelenir (`"sürdürülebilirlik · su"`). Alan **kaybolmaz** — `su` yazan
kullanıcı onu hâlâ `①`/`②`/`③` üzerinden bulur (ölçüldü: `q=su` → aynı alan **1.**).

⚠ 🅖 **`_KISA_ESIK = 4` ÖLÇÜLDÜ, ödünç alınmadı.** `§18.8` iki bağımsız satıcının
(Algolia · Typesense) *«1 hata için asgari uzunluk = 4»* sayısını verir **ve** onu
benimsemeyi yasaklar (*«Latin kelime uzunluk dağılımına kalibre; ölçmeden benimseme»*).
Ölçüldü: `3·4·5·6` değerlerinin **dördü de** aynı `Recall@3 = %89,5`'i veriyor — yani
sayı erişimde **yansız**. Seçimi yapan şey ölçülen kusurdur: `su` (2) ve `set` (3)
harflik iki etiketi birden bağlama sokan **en küçük** değer **4**'tür.

### ⚠🅖 BEDELİ — ölçüldü ve GİZLENMİYOR

Havuz `136` metinden `534` görünüme çıktı (`3,93`/alan). Aynı konteynerde, gerçek
gömücüyle:

| `lab/oneri_p95.py` (payda **90**) | önce | sonra | kapı |
|---|---|---|---|
| ılık `p50` | 39,63 ms | **50,86 ms** | — |
| ılık `p95` | 49,23 ms | **53,88 ms** | `< 300 ms` ✅ |
| **soğuk (ilk istek)** | 1.514,5 ms | 🔴 **24.799,7 ms** | *(kapı yok)* |

⊙ Ilık yol **tabanın yanında kaldı** (`+%9,4`) — ama bedavaya değil: ilk yazılışta
`p95 = 147,03 ms` ölçüldü (`+%199`) ve sebep temsil değil `M @ qn`'in **iş parçacığı
yan etkisiydi**; elemanwise indirgemeyle geri alındı (gerekçe `_vektor_sira` içinde).
*Bir yavaşlamayı ölçmeden yeni özelliğe yazmak, yanlış şeyi geri almaktır.*

🔴 **Soğuk maliyet `16×` arttı ve bu AÇIK BİR BORÇTUR.** İki sebebi var ve ikisi de
ölçüldü: görünüm **sayısı** (`3,93×`) ve görünümlerin **uzunluğu** (sinonim cümlesi
uzun; metin başına `11,3 → 47,8` ms). Kısaltma denendi ve **reddedildi**: sinonimleri
`4`'e kırpmak soğuğu `16,8` sn'ye indiriyor ama `Recall@3`'ü **%89,5 → %84,2**
düşürüyor — yani ucuzluk doğrudan erişimden ödeniyor.

⊙ **Ölçülmüş bir kaldıraç var, alınMADI** ㊴: `③ küp bağlamı` görünümünü düşürmek
(`407` görünüm, soğuk `18,4` sn) `Recall@3`'ü **hiç** değiştirmiyor (%89,5). Ama payda
**19**'dur ve iki kurulum orada **tavana** vurmaktadır: bu bir *«③ işe yaramıyor»*
kanıtı değil, **ölçütün ayırt edemediği** bir yerdir 🅜. `§18.7` o görünümü açıkça
istiyor; düşürme kararı **payda büyütülmeden** verilemez.

⚠ Doğru çözüm kırpma değil **ısıtmadır** ve adresi bu modülde değil: `main.py`
gömücüyü zaten arka planda ısıtıyor, indeks ısıtılmıyor (`lab/oneri_p95.py`'de yazılı
⊘). O ⊘ bugüne kadar `1,5` sn'lik bir borçtu; bugünden sonra `25` sn'lik bir borçtur.
"""

from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass

from app.llm import _norm

__all__ = ["Aday", "ara", "terimler"]

#: Ayak başına havuz — füzyona giren aday sayısı. Kısa tutulur: typeahead'de
#: yirminci aday hiçbir zaman görülmez, ama her aday bir gömme kıyası demektir.
_HAVUZ = 20

#: RRF sabiti — gerekçesi modül başlığında. **Kalibre değil, seçilmiş** 🅖.
_RRF_K = 10

#: Öneri şeridinin tavanı (`FAZ 6.4`: **≤7**).
VARSAYILAN_LIMIT = 7

#: 🔴 `§18.7` — **bağlamsız kısa ad gömülmez.** Bundan kısa bir görünen etiket kendi
#: başına bir görünüm olmaz; küp bağlamına füzelenir. Gerekçesi ve **ölçümü** modül
#: başlığında (`3·4·5·6` erişimde yansız; `4`, ölçülen iki kusurlu etiketi —
#: `su`·`set` — birden kapsayan en küçük değer).
_KISA_ESIK = 4


@dataclass(frozen=True)
class Aday:
    """Bir öneri. `kip` **hangi ayağın** bulduğunu beyan eder 🅖.

    `gorunumler` — `§18.7`'nin **çok görünümlü temsili**: aynı alanın etiketi ·
    sinonim cümlesi · küp bağlamı · birimi. İki ayak da (leksik **ve** vektör) bu
    kümede arar; aday yine **alan başınadır**, yani bir alan kaç görünümden gelirse
    gelsin listede **bir kez** görünür 🆈.
    """

    kimlik: str        # `cube.olcu` — tıklanınca sorguyu kuran taraf bunu çözer
    etiket: str        # kullanıcıya görünen ad
    cube: str
    kip: str           # "leksik" | "vektor" | "leksik+vektor"
    gorunumler: tuple[str, ...] = ()   # `§18.7` — aranan metinler (etiket DEĞİL, temsil)


def _tekil(*parcalar: str) -> tuple[str, ...]:
    """Normalize edilmiş hâli aynı olan görünümleri **teke indirir**, sırayı korur.

    ⚠ Aynı metni iki kez gömmek yalnız maliyet değildir: `max` havuzunda bir alanın
    aynı görünümü iki kez sayılmaz ama **soğuk maliyet** iki katına çıkar.
    """
    gorulen: set[str] = set()
    out: list[str] = []
    for p in parcalar:
        m = str(p or "").strip()
        k = _norm(m).strip()
        if k and k not in gorulen:
            gorulen.add(k)
            out.append(m)
    return tuple(out)


def _gorunumler(etiket: str, sinonimler, kup_display: str, birim: str) -> tuple[str, ...]:
    """🔴 `§18.7` — bir alanın **çok görünümlü temsili**. Üç kaynak da katalogda.

    `①` görünen etiket · `②` etiket+sinonim cümlesi · `③` küp bağlamı · `④` birim.

    🔴 `①`'in tek sapması: **çıplak kısa ad gömülmez** (`_KISA_ESIK`) — `"su"`/`"set"`
    gibi bir etiketin gömmesi alanın anlamını değil kelimenin **kısalığını** taşır
    (`§18.6`: literatürde tek kelime performansı için ölçüm **yok**; `§12.1`: ölüm
    şartı tam burada). O hâlde etiket `③` ile aynı metne düşer ve alan bağlamıyla
    gömülür — **kaybolmaz**, yalnızca yalnız bırakılmaz.
    """
    etiket = str(etiket or "").strip()
    kup_display = str(kup_display or "").strip()
    baglam = f"{kup_display} · {etiket}" if kup_display and etiket else etiket
    birim = str(birim or "").strip()

    ilk = etiket if len(_norm(etiket).strip()) >= _KISA_ESIK else baglam
    sozluk = _tekil(etiket, *[str(s) for s in (sinonimler or [])])
    dortlu = [ilk, ", ".join(sozluk), baglam]
    if birim and etiket:
        dortlu.append(f"{etiket} ({birim})")
    return _tekil(*dortlu) or ((etiket,) if etiket else ())


def terimler(schema: dict, izinliler: set[str] | None) -> list[Aday]:
    """🔴 `5.2` — **ÖNCE YETKİ, SONRA HER ŞEY.**

    Katalogdan aday terimleri toplar; **görmeye hakkı olmayan** küplerin hiçbir terimi
    listeye girmez. Sıralama bu listenin **üstünde** çalışır, tersi değil.

    `izinliler is None` → Katman B bu tenant'ta yapılandırılmamış; kararı
    `katman_b.karar` verir (Katman A yönetir). Kural burada **tekrarlanmaz**.

    🔴 `§18.7` — her aday **çok görünümlü** doğar. Havuzun **boyu değişmez** (aday
    hâlâ alan başına birdir); değişen, o adayın **hangi metinlerle arandığıdır** 🅐.
    """
    from app.katman_b import karar

    out: list[Aday] = []
    for c in schema.get("cubes") or []:
        model = c.get("base_object") or c.get("name") or ""
        gecer, _ = karar({model} if model else set(), izinliler)
        if not gecer:
            continue  # 🔴 yetkisiz küp → adı bile geçmez (envanter sızıntısı)
        cube = str(c.get("name") or "")
        # `③` küp bağlamı — `display` **zaten** şemada (`wren_service.py:846` deseni):
        # `label` > ilk sinonim > ad. İkinci bir sözlük açılmıyor (`KAT-1`).
        kup_display = str(c.get("display") or cube)
        gorunen = c.get("measure_synonyms_display") or {}
        sinonimler = c.get("measure_synonyms") or {}    # `②` — cube_synonyms.yml
        birimler = c.get("units") or {}                 # `④` — measure `unit`
        for olcu, etiket in gorunen.items():
            ad = str(etiket or "").strip() or str(olcu)
            out.append(Aday(
                kimlik=f"{cube}.{olcu}", etiket=ad, cube=cube, kip="leksik",
                gorunumler=_gorunumler(ad, sinonimler.get(olcu), kup_display,
                                       birimler.get(olcu))))
        out.extend(_deger_adaylari(c, cube, kup_display, gorunen))
    return out


#: Bir küpten indekse girecek **en çok** değer. ⚠ Havuz ölçüldü: dört şirketin
#: kataloğunda toplam **776** değer var, en kalabalık küp **88** (`parti`). Sınır bu
#: sayının **üstünde** tutuldu ki bugün hiçbir değer düşmesin; amacı bir gün onbinlerce
#: değerli bir kiracıda sıcak yolu korumak 🅜 — *bir sınırın işi bugünü kırpmak değil,
#: yarını taşınabilir kılmaktır.*
_DEGER_TAVANI = 200


def _deger_adaylari(c: dict, cube: str, kup_display: str, gorunen: dict) -> list[Aday]:
    """🔴 `§40` — **BOYUT DEĞERLERİ DE ADAYDIR**: *«ram 3»* → `RAM-3`.

    ## Ölçülen kusur (kullanıcı, 2026-08-13)

    Kullanıcı `ram 3 neden` yazdı ve öneri şeridinde **`RAM-3` hiç geçmedi**; gelenler
    katalog alan adlarıydı. Ölçüldü: `oneri.ara("ram 3", schema)` → **0 aday**, çünkü bu
    modülün evreninde **yalnız ölçüler** vardı (`dimension_values` → 0 geçiş) 🆘.

    *Bir öngörü, yazılanı içeremiyorsa bir öngörü değildir* — ve içeremiyordu, çünkü
    yazılan şey (bir **makine adı**) sistemin aday listesinde hiç yoktu.

    ## Aday şekli — ve neden ölçüsüz bir değer YETMEZ

    Bir değer tek başına **cevaplanabilir değildir**: *«RAM-3»* bir soru değil bir
    özne. Bu yüzden her değer, küpün **varsayılan ölçüsüyle** (`default_measure`)
    eşleştirilip tam bir cümlenin iskeleti olarak doğar:

        kimlik = "oee.ort_oee#makine=RAM-3"   →   «bu ay RAM-3'ün ortalama OEE'si …»

    `#` ayırıcısı **yeni bir sözleşme değil**: kırılımlı öneriler onu zaten kullanıyor 🆍.

    ⚠ `default_measure` yoksa küp **atlanır** — uydurma ölçü seçmek, sessiz-yanlış bir
    sorgu üretmenin en kısa yoludur ㊱.
    """
    olcu = str(c.get("default_measure") or "").strip()
    if not olcu:
        return []
    out: list[Aday] = []
    for boyut, degerler in (c.get("dimension_values") or {}).items():
        for deger in (degerler or [])[:_DEGER_TAVANI]:
            d = str(deger).strip()
            if not d:
                continue
            out.append(Aday(
                kimlik=f"{cube}.{olcu}#{boyut}={d}", etiket=d, cube=cube, kip="leksik",
                gorunumler=_tekil(d, f"{d} {kup_display}",
                                  f"{d} {str(gorunen.get(olcu) or olcu)}")))
    return out


def _leksik_sira(kismi: str, adaylar: list[Aday]) -> list[int]:
    """Edge n-gram **önce**, bulanık benzerlik **sonra** (`5.3`).

    Önek eşleşmesi typeahead'in doğal davranışıdır ve **bedavadır**; bulanık ayak
    yalnız önek hiçbir şey bulamadığında anlamlıdır. Eşik `cube_router`'dan **ödünç
    alınır** — bu depoda o sabitler katalog kelimeleriyle kalibre edildi (`KAT-1`).

    🔴 `§18.7` — arama **görünümler üstünde** yapılır, çıplak etiket üstünde değil:
    *«zayiat»* yazan kullanıcı `toplam_fire_kg`'ye **sinonim görünümünden** ulaşır ve
    bu ulaşma gömücüye **borçlu değildir** (`5.8`: gömücü soğuksa da çalışır) 🅖.
    En iyi görünüm alanın skoru olur — alan **bir kez** aday olur.
    """
    from app.cube_router import _TYPO_MID

    q = _norm(kismi).strip()
    if not q:
        return []
    onek, bulanik = [], []
    for i, a in enumerate(adaylar):
        vurdu, en_iyi = False, -1.0
        for g in (a.gorunumler or (a.etiket,)):
            e = _norm(g)
            if e.startswith(q) or any(p.startswith(q) for p in e.split()):
                vurdu = True
                break
            en_iyi = max(en_iyi, difflib.SequenceMatcher(None, q, e).ratio())
        if vurdu:
            onek.append((0.0, i))
        elif en_iyi >= _TYPO_MID:
            bulanik.append((-en_iyi, i))
    onek.sort(key=lambda t: (t[0], len(adaylar[t[1]].etiket)))
    bulanik.sort()
    return [i for _, i in onek][:_HAVUZ] + [i for _, i in bulanik][:_HAVUZ]


#: 🔴 `5.7` — **İNDEKS: SÜRÜM ANAHTARLI, BELLEKTE, BAYATLAYAMAZ.**
#:
#: ⊙ Ölçülen maliyet: her `/oneri` isteği katalogdaki **136 ölçü** etiketini yeniden
#: gömüyordu. Debounce (200 ms) bunu seyreltir ama **kaldırmaz** — bir kullanıcı bir
#: cümlede onlarca istek üretir.
#:
#: ⚠ **Planın «tazelik damgası» maddesi burada bir ADIM İLERİ taşındı** 🅐: bir damga
#: bayatlığı *«beyan eder»*; **sürüm anahtarlı bir önbellek** onu **imkânsız kılar**.
#: Anahtar `schema["version"]`'dır (`mdl_version` deseni — `contracts.py:75` bayatlığı
#: tam bu kıyasla ölçer). Şema değişince anahtar değişir, eski girdi **kullanılamaz**.
#: *Bir değişmezi ilan etmek onu kurmaz; anahtarı değişmezin kendisi yapmak kurar.*
#:
#: ⊘ **Diskte artefakt YOK** ⑪: bu depo bir kez *«gitignore'lu bir derleme
#: artefaktından okuyan ölçüm»* yüzünden aynı kaynakta farklı sayı gördü. Bellekteki
#: önbellek süreçle doğar, süreçle ölür — okunacak bayat bir dosya yoktur.
_INDEKS: dict[str, tuple[tuple[str, ...], tuple[str, ...], object]] = {}


def _anahtar(surum: str, kimlikler: tuple[str, ...],
             gorunumler: tuple[str, ...] = ()) -> str:
    """Önbellek anahtarının **tek sahibi** ㊲.

    ⚠ İlk yazılışta anahtar **iki yerde** kuruluyordu: `_vektor_sira` `f"{surum}|{n}"`
    üretiyor, `indeks_durumu` düz `surum` arıyordu — yani durum beyanı **hep «yok»**
    diyordu ve kapı bunu ilk koşumda yakaladı. *İki satırın aynı işi yaptığı yerde,
    bir gün biri değişir.*

    ⟳🔴 **DÜZELTİLDİ (denetim ajanı):** anahtar **aday SAYISINA** bağlıydı. Farklı
    allowlist'li iki kiracı aynı sayıya düşerse **aynı girdiye** yazıyorlardı: kimlik
    kontrolü doğruluğu koruyordu ama önbellek **her istekte ıskalıyordu** — yani ölçülen
    `p95 = 49,23 ms` **tek havuzludur** ve çok kiracılıya **taşınmaz** 🅕.
    ⊙ Artık anahtar **kimliklerin özetini** taşıyor: iki farklı havuz **iki ayrı girdi**.

    ⟳🔴 **`§18.7` ile bir ÜÇÜNCÜ boyut daha eklendi: GÖRÜNÜM KÜMESİ.** Matrisin satır
    sayısı artık aday sayısı değil **görünüm** sayısıdır; katalog aynı kimlikleri
    koruyup bir etiketi/sinonimi/birimi değiştirdiğinde eski matris yeni havuza
    **uymaz** — ve şema sürümü her zaman değişmeyebilir (fikstür, kiracı-içi düzeltme).
    Anahtar bunu taşımazsa skorlar **yanlış görünüme** atanır: sessiz bir hizasızlık.
    *Bir önbelleğin anahtarı, sakladığı şeyin bağlı olduğu HER girdiyi taşımalıdır.*
    """
    ozet = hashlib.blake2s(
        "\x00".join((*kimlikler, "\x01", *gorunumler)).encode("utf-8"),
        digest_size=8).hexdigest()
    return f"{surum}|{len(kimlikler)}|{ozet}"


def indeks_durumu(schema: dict) -> dict:
    """`④` — indeksin **beyanı**. `durum`: `taze` (bu sürüm önbellekte) ·
    `yok` (henüz kurulmadı) · `kapali` (gömücü yok → vektör ayağı hiç çalışmaz)."""
    from app import vqr

    surum = str(schema.get("version") or "")
    if vqr._embedder() is None:
        return {"durum": "kapali", "surum": surum}
    onek = f"{surum}|"
    taze = any(k.startswith(onek) for k in _INDEKS)
    return {"durum": "taze" if taze else "yok", "surum": surum}


def _vektor_sira(kismi: str, adaylar: list[Aday], _surum: str = "") -> list[int]:
    """Vektör ayağı — **yalnız sıra üretir**, eşik üretmez (`FAZ 0` bulgusu).

    `5.8`: gömücü hazır değilse (`None`) **boş liste** döner ve çağıran leksik ayakla
    devam eder. Bu bir hata değil bir **hâl**dir.

    ⚠ E5 burada **simetrik** kullanılır (soru↔terim): `query: ` öneki **iki tarafa** da
    konur — `FAZ 0` ölçümü de böyle yapıldı, aksi hâlde ölçüm taşınmaz 🅕.

    🔴 `§18.7` — gömülen şey **alan adı değil**, alanın görünümleridir. Matris görünüm
    başına bir satır taşır; bir alanın skoru **en yakın görünümünün** skorudur (`max`).
    Yani sorgu bir **görünüme** eşleşir, aday o görünümden **türer** ve aynı alan iki
    görünümden gelse bile listeye **bir kez** girer — tekilleştirme burada olur.
    ⊘ Bu bir eleme **değildir**: dönen sıra hâlâ havuzun tamamını kapsar.
    """
    from app import vqr

    model = vqr._embedder()
    if model is None or not adaylar:
        return []
    onek = "query: "
    try:
        import numpy as np

        # 🔴 `5.7` — aday gömmeleri **sürüm anahtarıyla** önbellekte. Anahtar üç şey
        # taşır: şema sürümü · aday **kimlikleri** · **görünüm kümesi**. Allowlist
        # daralırsa havuz daralır, katalog metni değişirse görünümler değişir; iki
        # hâlde de eski matris yeni havuza **uymaz** — sessiz bir hizasızlık yerine
        # açık bir önbellek ıskası olur ㊴.
        kimlikler = tuple(a.kimlik for a in adaylar)
        duz: list[str] = []
        dilim: list[tuple[int, int]] = []
        for a in adaylar:
            bas = len(duz)
            duz.extend(a.gorunumler or (a.etiket,))
            dilim.append((bas, len(duz)))
        gorunum = tuple(duz)
        anahtar = _anahtar(_surum, kimlikler, gorunum)
        onbellek = _INDEKS.get(anahtar)
        if (onbellek is not None and onbellek[0] == kimlikler
                and onbellek[1] == gorunum):
            M = onbellek[2]
        else:
            M = np.asarray(list(model.embed([onek + g for g in duz])), dtype="float32")
            M /= (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
            _INDEKS[anahtar] = (kimlikler, gorunum, M)
        qv = list(model.embed([onek + kismi]))[0]
        qn = np.asarray(qv, dtype="float32")
        qn /= (np.linalg.norm(qn) + 1e-9)
        # 🔴🅫 **ÖLÇÜLMÜŞ: `M @ qn` BURADA ÜÇ KAT PAHALIYA MAL OLUYORDU.** Matris
        # görünümlerle `136 → 534` satıra çıkınca `matmul` **çok iş parçacıklı BLAS**
        # yoluna düşüyor; çarpımın kendisi 2,8 ms ama açtığı iş parçacığı havuzu bir
        # sonraki **ONNX gömme** çağrısını yavaşlatıyor. Ölçüldü (aynı konteyner,
        # gerçek gömücü, uçtan uca ılık çağrı):
        #
        #     M @ qn          → 113,2 ms   (yalnız sorgu gömme: 35,2 ms)
        #     (M * qn).sum(1) →  37,5 ms   ← temsil zenginleşti, gecikme **taban**da
        #
        # Elemanwise indirgeme tek iş parçacıklıdır ve bellek-bağımlıdır: `534×1024`
        # `float32` için ~2,2 MB geçici. `§18.2` bu ölçekte **exact arama** kararı
        # verdi; katalog büyürse geçici de büyür ve **o gün** parçalı indirgeme gerekir.
        # *Bir çarpımın maliyeti kendi süresi değildir; bıraktığı yan etkidir.*
        skor = (M * qn).sum(axis=1)
        # Görünüm skorlarını **alana** indir: en yakın görünüm alanın skorudur.
        en_yakin = np.asarray([float(skor[b:s].max()) for b, s in dilim],
                              dtype="float32")
        return [int(i) for i in en_yakin.argsort()[::-1][:_HAVUZ]]
    except Exception:  # noqa: BLE001 — öneri katmanı **cevabı bozmaz** (§101.1)
        return []


def ara(kismi: str, schema: dict, *, izinliler: set[str] | None = None,
        limit: int = VARSAYILAN_LIMIT) -> list[Aday]:
    """`5.1` — **saf** arama. Sorgu koşmaz, LLM çağırmaz, durum tutmaz.

    Sıra: ① yetki süzmesi ② iki ayak ③ **RRF** füzyonu ④ kesme.

    ⊙ Havuz **alan** başınadır (`§18.7`): iki ayak da alanın *görünümleri* içinde arar,
    ama sıra numaraları alanlara aittir — yani RRF bir alanı görünüm sayısı kadar
    ödüllendirmez. *Bir temsili zenginleştirmek, onu birden çok kez saymak değildir.*
    """
    havuz = terimler(schema, izinliler)
    if not havuz:
        return []

    lek = _leksik_sira(kismi, havuz)
    vek = _vektor_sira(kismi, havuz, str(schema.get("version") or ""))

    puan: dict[int, float] = {}
    kipler: dict[int, set[str]] = {}
    for ayak, sira in (("leksik", lek), ("vektor", vek)):
        for yer, i in enumerate(sira):
            puan[i] = puan.get(i, 0.0) + 1.0 / (_RRF_K + yer + 1)
            kipler.setdefault(i, set()).add(ayak)

    # 🔴 **K1 — DOLGU YOK** (insan testinde her turda görüldü: `fire` → `metre`·`enerji`;
    # `bu yıl ciro` → `borç`·`alacak`).
    #
    # Ölçülen yapı: `fire` için leksik ayak **3** aday buluyor, ekranda **7** görünüyordu —
    # yani **dördü dolguydu**. Füzyon listeyi `limit`e kadar dolduruyor ve kalanlar
    # yalnız vektör sırasından geliyor; kullanıcı *«fire»* yazıp *«doğalgaz»* okuyor.
    #
    # ⚠ Onarım bir **eşik değil bir kesme**dir — ve bu ayrım bu deponun kuralıdır:
    # vektör ayağı bilinçli olarak *«sıra üretir, **eşik üretmez**»* (`FAZ 0`), ve MIMARI
    # *«kalibre edilmemiş bir eşik bir güven değil bir **süstür**»* der. Buradaki kural
    # hiçbir sayı seçmez; yalnız *«hangi kanıt vardı»* diye sorar.
    #
    # ⚠ Ve vektör ayağı **susturulmuyor**: leksik ayak **hiçbir şey** bulamadığında
    # (ölçüldü: `zayiat` → 0, `vardya` → 0) vektör **tek çaredir** ve liste ondan kurulur.
    # Sinonim ve yazım hatası yolu tam olarak orada yaşıyor.
    #
    # ⊙ `§18.7`'den sonra leksik ayak **sinonimleri de** görüyor (ölçüldü: `ciro` →
    # `sipariş tutarı`), yani bu kesme kapsamı daraltmıyor; **gürültüyü** kesiyor.
    #
    # 🅑 Mutasyon: `if lek:` kaldırılırsa `fire` sorgusuna `metre`/`enerji` geri gelir.
    if lek:
        lek_kume = set(lek)
        puan = {i: p for i, p in puan.items() if i in lek_kume}

    # ⚠ Eşitlikte **leksik önde** olan kazanır: bir önek eşleşmesi kullanıcının
    # yazdığının **birebir** karşılığıdır; vektör benzerliği bir tahmindir ㊼.
    lek_yer = {i: y for y, i in enumerate(lek)}
    sirali = sorted(puan, key=lambda i: (-puan[i], lek_yer.get(i, 10**6), havuz[i].etiket))
    out: list[Aday] = []
    for i in sirali[:limit]:
        a = havuz[i]
        out.append(Aday(kimlik=a.kimlik, etiket=a.etiket, cube=a.cube,
                        kip="+".join(sorted(kipler[i])), gorunumler=a.gorunumler))
    return out
