"""PLAN ÇALIŞTIRICISI — adımları sırayla koşar, değerleri birbirine geçirir (FAZ O-2).

## Ne yapar, ne YAPMAZ

| yapar | **yapmaz** |
|---|---|
| adımları sırayla koşar | ❌ LLM çağırmaz |
| `$1` referanslarını çözer | ❌ SQL **yazmaz** |
| her adımın makbuzunu tutar | ❌ aritmetik yapmaz |
| bütçeyi sayar | ❌ katalog dışına çıkamaz |

🔴 **Sayıyı her zaman küp koyar.** Bu dosya bir sayı **hesaplamaz**; hesaplayan
`ilkeller`dir ve o da yalnız **koşmuş satırlar** üzerinde çalışır. Orkestratörün
Discovery'den farkı tam burada: *Discovery'de LLM **cevabı** üretir; burada LLM **soruyu
böler**, cevabı her parçada **küp** verir.*

## Neden `planner.Planlayici`'nin içine değil

`Planlayici` bir **yönetişim** katmanıdır: dört kapı (kayıt · yetki · deterministik-önce ·
bütçe) ve adım makbuzu. Bu dosya bir **yorumlayıcıdır**: referans çözer, sıra kurar.
İkisini aynı sınıfa koymak, *"aynı sınıfa iki farklı soru sordurmak"*tı — bu deponun
`toplanabilirlik()` docstring'inde adıyla kayıtlı desen.

⚠ `KURAL B`: bugün **hiçbir yol** bu dosyayı çağırmıyor. Bağlanması `O-4`'ün işi ve o
faz kendi bayrağıyla gelir. *Bir yorumlayıcıyı önce yazıp sonra bağlamak, ikisini birden
yapmaktan daha az risklidir.*
"""

from __future__ import annotations

import re
from typing import Any

from app.logging_setup import get_logger

_log = get_logger("plan_kosucu")

_REF = re.compile(r"^\$([1-9][0-9]?)$")

#: 🔴 **SORGU BÜTÇESİ.** `Butce`'nin sorgu ayağının bu katmandaki karşılığı.
#: ⚠ `plan_semasi.AZAMI_ADIM` ile aynı sayı olması **tesadüf değil**: 8 adımlık bir
#: planın hepsi `SORGU` olabilir (rapor yeteneği tam da öyle bir plandır). Daha küçük
#: bir bütçe, şemanın izin verdiği bir planı koşum anında reddederdi — ve o red
#: `dogrula`'da bile olsa **geç**tir: plan kurulmuş, model çağrılmış olurdu.
AZAMI_SORGU = 8



class PlanHatasi(Exception):
    """Bir adım koşulamadı — **fail-closed**. Sessizce atlanmaz, tur düşürülür.

    ⚠ Neden istisna: bir adımın sessizce düşmesi, sonraki adımların **eksik bir girdiyle**
    koşması demektir ve sonuç `source=cube` rozetiyle döner. Bu deponun en tehlikeli
    sınıfı. *Derlenmeyen bir plan, sessizce yanlış bir plandan iyidir.*
    """


def _coz(deger: Any, ciktilar: list[Any]) -> Any:
    """`$1` gibi bir referansı önceki adımın çıktısına çevirir; değilse aynen döner.

    ⚠ **İleri referans yasak**: `$3` üçüncü adımdayken henüz yoktur. Şema bunu
    engellemiyor (JSON Schema sıra bilmez), o yüzden kapı **burada**.
    """
    if isinstance(deger, list):
        return [_coz(t, ciktilar) for t in deger]
    if not isinstance(deger, str):
        return deger
    m = _REF.match(deger)
    if not m:
        return deger
    i = int(m.group(1))
    if i < 1 or i > len(ciktilar):
        raise PlanHatasi(f"`${i}` henüz koşmamış bir adıma işaret ediyor "
                         f"(o anda {len(ciktilar)} adım tamamlanmıştı)")
    return ciktilar[i - 1]


def _referanslar(adim: dict) -> list[tuple[str, int]]:
    """Bir adımın taşıdığı `(alan, hedef_adım_no)` referansları. Tek kanal `$n`'dir.

    ⚠ `FAZ 3` — bir alan **liste** de olabilir (`kaynaklar: ["$1","$3"]`). O zaman her
    öğe ayrı bir kenardır; alan adı aynı kalır ki tip denetimi hepsini aynı beklentiye
    karşı sınasın.
    """
    out: list[tuple[str, int]] = []
    for alan, deger in (adim or {}).items():
        if alan == "fiil":
            continue
        for tek in (deger if isinstance(deger, list) else [deger]):
            if isinstance(tek, str) and (m := _REF.match(tek)):
                out.append((alan, int(m.group(1))))
    return out


def dogrula(plan: dict, *, azami_sorgu: int = AZAMI_SORGU) -> list[list[int]]:
    """🔴🔴 **KOŞMADAN ÖNCE DOĞRULA** — ve aynı geçişte **DAG'ı kur**.

    Döner: topolojik **katmanlar** (adım numaraları, 1'den). Aynı katmandaki adımlar
    birbirinden bağımsızdır. Bugün koşum hâlâ sıralı; katmanlar `FAZ 4`'ün (paralel
    `SORGU`) zeminidir. ⚠ Bir kez yazılıp iki iş görür: doğrulayıcı **ve** zamanlayıcı.

    ## Neden bu geçiş şart — ölçülmüş bir çelişki

    `plan_garson` şunu yazıyordu: *"Bir planı koşarken reddetmek, hiç kurmamaktan
    pahalıdır — ilk adım o ana kadar çoktan koşmuştur."* Ama ileri referans denetimi
    `_coz` içindeydi, yani **tam da koşum anında**: `$3` hatası, birinci `SORGU` motora
    gitmişken patlıyordu. Bu fonksiyon o çelişkiyi kapatır.

    ## Şemanın **yapısal olarak** ifade edemedikleri

    | denetim | neden şema yapamaz |
    |---|---|
    | ileri referans | JSON Schema **sıra** bilmez |
    | tip uyumu (`HESAPLA.hedef` bir `varlik` ister) | çıktı tipleri şemada değil, `CIKTI_TIPI`'nde |
    | `ANLAT` yalnız son adım | `oneOf` **konum** bilmez |
    | toplam sorgu bütçesi | bütçe koşum-zamanı bir sayaçtı; artımlı sayıldığı için ilk sorgular koşup **sonra** düşüyordu |
    | ulaşılamaz adım | plan uzunluğu bir **maliyettir** (`E9`) |

    *Bir zinciri koşmadan denetlemek, halkalarının neye benzediğini yazmakla mümkündür.*
    """
    from app.plan_semasi import CIKTI_TIPI, GIRDI_TIPI, SON_ADIM_FIILLERI

    adimlar = (plan or {}).get("adimlar") or []
    if not adimlar:
        raise PlanHatasi("plan boş — koşulacak adım yok")

    n = len(adimlar)
    kenarlar: dict[int, set[int]] = {i: set() for i in range(1, n + 1)}
    kullanilan: set[int] = set()
    sorgu_sayisi = 0

    for sira, adim in enumerate(adimlar, 1):
        fiil = adim.get("fiil")
        if fiil == "SORGU":
            sorgu_sayisi += 1
        if fiil in SON_ADIM_FIILLERI and sira != n:
            raise PlanHatasi(
                f"`{fiil}` yalnız SON adım olabilir (adım {sira}/{n}) — bir anlatı, "
                "anlatacağı bulgulardan önce yazılamaz")
        for alan, hedef in _referanslar(adim):
            if hedef >= sira:
                raise PlanHatasi(
                    f"adım {sira} (`{fiil}`) `${hedef}` diyor — o adım henüz koşmamış "
                    "olurdu (ileri referans)")
            kenarlar[sira].add(hedef)
            kullanilan.add(hedef)
            beklenen = (GIRDI_TIPI.get(fiil) or {}).get(alan)
            _hedef_fiil = adimlar[hedef - 1].get("fiil")
            gelen = CIKTI_TIPI.get(_hedef_fiil)
            # 🔴🔴 **BİR `SORGU` ADIMINA REFERANS, ONUN SORGUSUNA DA REFERANSTIR.**
            #
            # Ölçüldü (canlı `FF4`, **üç ayrı koşumda**): model ısrarla
            # `SUZ(cube_query="$1")` yazıyor — yani *«birinci adımın sorgusunu daralt»*.
            # Semantik olarak **tam doğru**; reddeden şey benim tip tablomdu: `SORGU`'nun
            # çıktısı `satirlar` sayılıyordu ve `sorgu` bekleyen alan onu almıyordu.
            #
            # ⊙ Ama bir `SORGU` adımı **iki şey** taşır: koştuğu sorgu ve döndürdüğü
            # satırlar. Alan `sorgu` bekliyorsa kastedilen birincisidir ve o **yazılı**
            # olarak elimizdedir (`adim["cube_query"]`).
            #
            # *En doğal ifadeyi yasaklayan bir tip sistemi, modeli eğitmez — ona
            # yalvarır.*
            if beklenen == "sorgu" and _hedef_fiil == "SORGU":
                gelen = "sorgu"
            if beklenen is not None and gelen is not None and beklenen != gelen:
                raise PlanHatasi(
                    f"adım {sira} (`{fiil}.{alan}`) bir **{beklenen}** bekliyor ama "
                    f"`${hedef}` bir **{gelen}** üretiyor "
                    f"(`{adimlar[hedef - 1].get('fiil')}`)")

    if sorgu_sayisi > azami_sorgu:
        raise PlanHatasi(f"plan {sorgu_sayisi} sorgu istiyor, bütçe {azami_sorgu}")

    # ⚠ Ulaşılamaz adım: kimsenin referans etmediği ve **son** da olmayan bir adım
    # koşulur, ödenir ve **atılır**. `E9`: plan uzunluğu bir ölçüdür.
    for sira in range(1, n):
        if sira not in kullanilan:
            raise PlanHatasi(
                f"adım {sira} (`{adimlar[sira - 1].get('fiil')}`) hiçbir adım tarafından "
                "kullanılmıyor ve son adım da değil — koşulup atılırdı")

    # Kahn katmanları. `$n` tek veri kanalı olduğu için grafik **eksiksizdir**.
    kalan = dict(kenarlar)
    bitmis: set[int] = set()
    katmanlar: list[list[int]] = []
    while kalan:
        katman = sorted(i for i, bag in kalan.items() if bag <= bitmis)
        if not katman:      # pragma: no cover - ileri referans yasağı döngüyü imkânsız kılar
            raise PlanHatasi("planda çözülemeyen bir bağımlılık döngüsü var")
        katmanlar.append(katman)
        bitmis |= set(katman)
        kalan = {i: b for i, b in kalan.items() if i not in bitmis}
    return katmanlar


def _sorgu_coz(deger: Any, adimlar: list[dict], ciktilar: list[Any]) -> Any:
    """`cube_query` alanına özel çözümleme: referans bir **`SORGU` adımını** gösteriyorsa
    o adımın **sorgusu** verilir, satırları değil.

    ⚠ Ve o adımın kendi `cube_query`'si de bir referans olabilir (`SORGU($3)` gibi) —
    o yüzden özyinelemeli. Zincir sonludur: ileri referans yasağı döngüyü imkânsız kılar.
    """
    if isinstance(deger, str):
        m = _REF.match(deger)
        if m:
            i = int(m.group(1))
            if 1 <= i <= len(adimlar) and adimlar[i - 1].get("fiil") == "SORGU":
                return _sorgu_coz(adimlar[i - 1].get("cube_query"), adimlar, ciktilar)
    return _coz(deger, ciktilar)


def _adim_coz(adim: dict, adimlar: list[dict], ciktilar: list[Any]) -> dict:
    """Adımın **bütün** `$n` alanlarını çözer. Referans çözmek yorumlayıcının işidir;
    çözülmüş adımı ne yapacağı gövdenin.

    ⚠ `cube_query` alanı **ayrı** çözülür (`_sorgu_coz`): orada bir referans satır değil
    **sorgu** demektir."""
    return {k: (_sorgu_coz(v, adimlar, ciktilar) if k == "cube_query"
                else _coz(v, ciktilar))
            for k, v in (adim or {}).items()}


#: 🔴 **YORUMLAYICININ KENDİ BİLDİĞİ FİİLLER — TEK SAHİP.**
#:
#: Gövdeleri ya `sorgu_kos`'tan (`SORGU`) ya `ilkeller`den gelir; ikincisi **saf**tır —
#: satır alır, değer verir, motora dokunmaz. Kalan fiiller `govdeler` ile **enjekte**
#: edilir çünkü bir motor isterler.
#:
#: ⚠ Bu demet bir belge değil **kaynağın kendisidir**: `plan_tuketici`'nin kapısı
#: (*«yedi fiilin yedisi de bağlı»*) buradan okur. Elle yazılmış bir kopya, bir fiil
#: buraya eklendiğinde **bayatlardı** — ve bayatladı da: `MATRIS`/`SIRALA` eklenince
#: kapı onları *«bağlanmamış»* sandı. *Bir kümeyi tarif eden liste, kümeden
#: üretilmiyorsa er ya da geç onu yanlış tarif eder.*
ICSEL_FIILLER: frozenset[str] = frozenset({
    "SORGU", "BAGLA", "HESAPLA", "MATRIS", "SIRALA", "RAPOR", "PANO",
})

#: 🔴 **EŞ ZAMANLILIK TAVANI — ÖLÇÜLDÜ, seçilmedi.** (`lab/olcumler/motor_eszamanlilik.md`)
#: 4 işçi **2,52×**, 8 işçi **1,86×** hızlandırdı: sekiz işçi yalnız çekişme ekliyor.
#: ⚠ Bir tavanı yükseltmek bir kazanç değildir; ölçülmeden yükseltmek bir borçtur.
AZAMI_ESZAMANLI = 4


def kos(plan: dict, *, sorgu_kos, govdeler: dict[str, Any] | None = None,
        cube_meta: dict | None = None, azami_sorgu: int = AZAMI_SORGU,
        paralel: bool = False) -> dict:
    """Planı koşar ve `{"ciktilar": [...], "makbuz": [...]}` döndürür.

    `sorgu_kos(cube_query) -> rows`: bilerek bir **parametre** — bu dosya `wren_service`'i
    tanımaz. Böylece testte sahte bir koşucuyla, üründe gerçek motorla aynı yorumlayıcı
    çalışır.

    `govdeler`: `fiil → f(çözülmüş_adım) -> çıktı`. 🔴 **Aynı enjeksiyon deseni, aynı
    sebep:** `TREND`/`AYRISTIR`/`KIYASLA` gövdeleri (`yoy.compute` ·
    `contribution.arastir` · `contribution._akran_kiyasi`) bir **motor** istiyor. Onları
    burada import etmek yorumlayıcıyı motora bağlardı. ⚠ `BAGLA`/`HESAPLA` istisna:
    gövdeleri `ilkeller`de ve **saf** — satır alır, değer verir.

    ⊙ Bölüşüm: **yorumlayıcı** referansı çözer, sırayı ve tipi denetler, bütçeyi sayar;
    **gövde** çözülmüş adımı alıp işini yapar. *Bir yorumlayıcının bilmesi gereken şey
    adımların ne YAPTIĞI değil, birbirine nasıl BAĞLANDIĞIDIR.*

    ⚠ `azami_sorgu`: `Butce`'nin sorgu ayağının bu katmandaki karşılığı. Aşımda
    `PlanHatasi` — çünkü bir planın yarısını koşup *"işte kısmi cevap"* demek, hangi
    adımın eksik olduğunu **kullanıcının** bulmasını istemektir.
    """
    from app import ilkeller as _ilk

    # 🔴 **ÖNCE DOĞRULA, SONRA KOŞ.** Motor bir tek sorgu bile görmeden plan ya geçerlidir
    # ya reddedilmiştir. `katmanlar` aynı geçişte çıkarılan DAG'dır.
    katmanlar = dogrula(plan, azami_sorgu=azami_sorgu)
    adimlar = plan["adimlar"]
    _lower = set((cube_meta or {}).get("lower_is_better") or [])
    # 🔴 **ÇIKTI ADIM SIRASINA YAZILIR, TAMAMLANMA SIRASINA DEĞİL.** Paralel koşumda
    # `append` kullanmak `$2`'yi başka bir adımın çıktısına bağlardı — ve bu, tekrar
    # üretilebilirliğin sessizce kaybolduğu yerdir. Ön tahsis bir üslup tercihi değil,
    # bir **doğruluk şartı**.
    ciktilar: list[Any] = [None] * len(adimlar)
    makbuz: list[Any] = [None] * len(adimlar)
    sorgu_sayisi = 0

    def _adim_kos(sira: int) -> Any:
        adim = adimlar[sira - 1]
        fiil = adim.get("fiil")
        try:
            if fiil == "SORGU":
                # ⚠ Bütçe **ön-geçişte** TOPLAM olarak denetlendi; burada yalnız koşulur.
                # 🔴 `FAZ 7` — `cube_query` bir **referans** de olabilir (`KIR`/`SUZ`
                # çıktısı). Kök-neden inişinin halkası budur: bir adım sorgu üretir,
                # bu adım onu **koşar**.
                return sorgu_kos(_sorgu_coz(adim["cube_query"], adimlar, ciktilar))
            if fiil == "BAGLA":
                olcu = adim["olcu"]
                return _ilk.bagla(_coz(adim["kaynak"], ciktilar), adim["boyut"], olcu,
                                  en_iyi_az=olcu in _lower)
            if fiil == "HESAPLA":
                hedef = _coz(adim["hedef"], ciktilar)
                # `BAGLA`'nın çıktısı `(varlık, değer)` — `HESAPLA` yalnız **varlığı**
                # ister. Bu dönüşüm burada, çünkü iki ilkelin sözleşmesini bilen tek yer
                # burası; `ilkeller` birbirini tanımaz ve tanımamalı (saf kalsın).
                if isinstance(hedef, tuple):
                    hedef = hedef[0]
                return _ilk.hesapla(_coz(adim["kaynak"], ciktilar), adim["boyut"],
                                    adim["olcu"], hedef)
            if fiil == "MATRIS":
                # ⚠ `BAGLA`/`HESAPLA` gibi **saf**: satır alır, satır verir. Enjeksiyon
                # gerekmez, çünkü motora dokunmuyor.
                return _ilk.matris(_coz(adim["kaynaklar"], ciktilar), adim["boyut"])
            if fiil == "SIRALA":
                return _ilk.sirala(_coz(adim["kaynak"], ciktilar), adim["boyut"],
                                   list(adim["olculer"]), az_iyi=_lower)
            if fiil == "RAPOR":
                return _ilk.rapor(_coz(adim["kaynaklar"], ciktilar), adim["baslik"])
            if fiil == "PANO":
                # 🔴 **YAZMAZ.** Çalıştırıcı salt-okunur ve idempotent kalıyor; ilk yan
                # etkili fiil bu değişmezi kırardı (yarım pano · ikilenen pano · geri
                # alınamayan yazma). Kalıcılaştırma onayla, dışarıda.
                return _ilk.pano_taslagi(_coz(adim["kaynaklar"], ciktilar), adim["baslik"])
            if fiil in (govdeler or {}):
                # ⟳ `FAZ 2` — kalan dört fiil enjekte edilen gövdelerle koşuyor. Adım
                # çözülmüş olarak verilir; gövde `$n` diye bir şey bilmez.
                return (govdeler or {})[fiil](_adim_coz(adim, adimlar, ciktilar))
            # 🔴 Gövdesi verilmemiş bir fiil sessizce atlanmaz: tur **düşer** ve sebebi
            # yazılır. *Bir fiili şemaya koyup çalıştırıcıda unutmak, onu sessizce yalan
            # yapmaktır.*
            raise PlanHatasi(f"`{fiil}` fiilinin çalıştırıcısı bu koşumda bağlı değil (O-4)")
        except PlanHatasi:
            raise
        except (KeyError, TypeError, ValueError) as e:
            raise PlanHatasi(f"adım {sira} (`{fiil}`) koşulamadı: {e}") from e

    for katman in katmanlar:
        _sorgu_sayisi_katman = sum(1 for i in katman
                                   if adimlar[i - 1].get("fiil") == "SORGU")
        sorgu_sayisi += _sorgu_sayisi_katman
        # ⚠ **Yalnız `SORGU` paralelleştirilir.** `BAGLA`/`HESAPLA`/`ANLAT` koşmuş satırlar
        # üzerinde saf fonksiyonlardır — mikrosaniyeler. Onları iş parçacığına atmak net
        # NEGATİF getiridir. Ve tek sorgulu bir katmanda havuz kurmak da öyle.
        if paralel and _sorgu_sayisi_katman >= 2:
            from concurrent.futures import ThreadPoolExecutor
            hatalar: list[str] = []
            with ThreadPoolExecutor(max_workers=min(AZAMI_ESZAMANLI, len(katman))) as _ex:
                _isler = {i: _ex.submit(_adim_kos, i) for i in katman}
            for i, _is in _isler.items():
                try:
                    ciktilar[i - 1] = _is.result()
                except Exception as e:      # noqa: BLE001 — hepsi toplanır, ilki değil
                    hatalar.append(f"adım {i}: {e}")
            if hatalar:
                # 🔴 Kardeşler **iptal edilmez, bitirilir** ve TÜM eksikler birlikte
                # söylenir. Kullanıcıya bir eksiği söyleyip ötekini saklamak, ikinci turu
                # boşa harcatır. ⚠ Kısmi sonuç **yayımlanmaz**: fail-closed sürüyor.
                raise PlanHatasi(" · ".join(hatalar))
        else:
            for i in katman:
                ciktilar[i - 1] = _adim_kos(i)
        for i in katman:
            _c = ciktilar[i - 1]
            makbuz[i - 1] = {"sira": i, "fiil": adimlar[i - 1].get("fiil"),
                             "satir": len(_c) if isinstance(_c, list) else None}

    _log.info("plan koştu: %d adım · %d sorgu · %d katman",
              len(adimlar), sorgu_sayisi, len(katmanlar))
    return {"ciktilar": ciktilar, "makbuz": makbuz, "sorgu_sayisi": sorgu_sayisi,
            "katmanlar": katmanlar}
