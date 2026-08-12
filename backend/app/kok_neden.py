"""🔴🔴 `§KN` — **KÖK-NEDEN CEBİRİ: bir sayı neden düşük olduğunu FORMÜLÜNDE saklar.**

## Kullanıcının şartı (2026-08-11)

> *«Neden sorusu geldiğinde adeta insan zihnini simüle etmeliyiz. O sayıların hesabı bir
> formüle dayanıyor; o formülde **paydaki** değerler arttıkça değer büyür, **payda**
> arttıkça değer düşer. RAM-3 değerinin düşük olması… ya payı düşürenleri bulmalıyım ya
> paydayı diğerlerine göre daha yüksek yapan bileşenleri. Sonra en köke inmeli: «en dibe
> indim ve gördüm ki vardiya 1'de malzeme bekleme nedeniyle bu makine çok durmuş, duruş
> zamanı yükselmiş, verimlilik bu yüzden düşmüş.»*

## Ve kök, kataloğun İÇİNDE zaten yazılıydı

Bu modülün varlık sebebi bir **ölçümdür**: `oee` küpünün kataloğu okununca görüldü ki
`ort_oee`'nin ifadesi, üç ayrı ölçünün ifadelerinin **birebir çarpımıdır**:

    ort_oee               = (…kullanilabilirlik ifadesi…)
                          * (…performans ifadesi…)
                          * (…kalite ifadesi…)
    ort_kullanilabilirlik = 1.0*SUM(calisma_suresi_dk)/NULLIF(SUM(planli_uretim_suresi_dk),0)
    ort_performans        = SUM(performans_PV*planli_uretim_suresi_dk)/NULLIF(SUM(planli…),0)
    ort_kalite            = 1.0*SUM(uretim_kg - hatali_kg)/NULLIF(SUM(uretim_kg),0)

Yani **bileşen keşfi bir SQL ayrıştırma işi değil**, kataloğun kendi metninde bir
**alt-ifade eşleşmesidir**: deterministik, sözlüksüz, LLM'siz. Bir SQL cebiri motoru
yazmak hem kırılgan olurdu hem de kataloğun zaten söylediği şeyi ikinci kez tahmin
etmek — *bir sistemin kendi hakkında söylediğini okumak varken, onu çözümlemeye
çalışmak, cevabı bilerek zor yoldan aramaktır.*

## Neden logaritma — ve neden bu bir süs değil

Bir **çarpım** ölçüsünde (`OEE = A × P × Q`) *«hangi faktör farkın ne kadarını
açıklıyor»* sorusunun **kesin** bir cevabı vardır:

    ln(v_hedef) − ln(v_akran) = Σ [ ln(f_i,hedef) − ln(f_i,akran) ]

Toplam **birebir** ayrışır (artık yok). Yani *«kullanılabilirlik farkın %78'ini
açıklıyor»* bir sezgi değil bir **özdeşliktir**. Aynı şey oran ölçüsünde de geçerlidir:
`ln(A/B) = ln A − ln B` → *«pay mı düştü, payda mı yükseldi»* sorusu tam olarak
cevaplanır ve ikisinin payı toplanır.

⚠ Yüzdeler **mutlak** katkılar üzerinden normalize edilir: bir faktör iyileşirken
öteki kötüleşiyorsa (birbirini kısmen götürüyorsa) payları toplamı yüzde yüzü aşabilir;
mutlak normalizasyon bunu *«şu kadarını açıklıyor, şu kadarını telafi ediyor»* diye
dürüstçe gösterir.

⚠ **Bu modül hiçbir sorgu koşmaz.** Girdisi katalog + zaten hesaplanmış sayılardır;
çıktısı bir **ayrıştırma** ve bir **cümledir**. Koşmayı çağıran yapar — böylece hem
test edilebilir kalır hem de aynı cebir hem `/ask` hem rapor yolunda kullanılabilir.
"""

from __future__ import annotations

import json
import math
import re

from app.logging_setup import get_logger

_log = get_logger("kok_neden")
from dataclasses import dataclass, field

#: Bir bileşenin ölçüdeki **rolü**. Kapalı bir küme: kataloğun ifade dilinde bir
#: bileşen ya çarpandır, ya paydır, ya paydadır, ya da toplanan bir terimdir.
#: `§KN` — derinleşmede **kaç aday** koşulur. Bir sabit değil bir **karar**: her aday
#: bir sorgudur ve üçüncüden sonrası, kullanıcının beklediği zamandan ödenir.
AZAMI_ADAY = 3

CARPAN = "carpan"
PAY = "pay"
PAYDA = "payda"
TERIM = "terim"


@dataclass
class Bilesen:
    """Bir ölçünün formülündeki bir bileşen — **kataloğun kendi ölçüsü**."""

    ad: str
    rol: str
    #: Rolün yön işareti: bileşen artınca ölçü **artıyor** mu (`+1`) yoksa **azalıyor**
    #: mu (`-1`)? Kullanıcının cümlesinin birebir karşılığı: *«payda arttıkça değer
    #: düşer»*.
    yon: int = 1
    display: str = ""


@dataclass
class Katki:
    """Bir bileşenin, hedef ile akran arasındaki farka **ölçülmüş** katkısı."""

    bilesen: Bilesen
    hedef: float
    akran: float
    #: `ln(hedef) − ln(akran)`, rol yönüyle işaretli. Toplamı, ölçünün log-farkına eşittir.
    katki: float
    #: Mutlak katkıların toplamına göre pay (%). Bkz. modül docstring'i.
    pay_yuzde: float = 0.0
    #: Bileşenin kendisi ölçünün **payında** mı paydasında mı — anlatı bunu söyler.
    def dusuruyor_mu(self) -> bool:
        return self.katki < 0


@dataclass
class Ayristirma:
    """`§KN`'nin çıktısı: hangi bileşen, farkın ne kadarını açıklıyor."""

    olcu: str
    hedef_deger: float
    akran_deger: float
    katkilar: list[Katki] = field(default_factory=list)
    #: En çok **düşüren** bileşen (varsa) — derinleşmenin bir sonraki adımı odur.
    sucllu: Bilesen | None = None


_SUM_RE = re.compile(r"SUM\s*\(", re.IGNORECASE)


#: 🔴 `§KN` — kataloğun **kendi** kullandığı iki teknik sarmal. Kapalı bir küme ve bir
#: **alan sözlüğü değil**: `ROUND` bir yuvarlama, `NULLIF` bir sıfıra-bölme koruması;
#: ikisi de ölçünün *anlamını* değiştirmez, yalnız yazımını sarar. ADR-0008 bir **alan
#: terimi** listesi yasaklar; bunlar SQL'in kendi işlevleridir.
_SARMAL_RE = re.compile(r"(?i)^(ROUND|NULLIF)\((.*)\)$")


def _son_virgul(ic: str) -> int:
    """Derinlik-0'daki **son** virgülün konumu (`ROUND(x, 2)`'nin ikinci argümanı)."""
    d = 0
    for i in range(len(ic) - 1, -1, -1):
        if ic[i] == ")":
            d += 1
        elif ic[i] == "(":
            d -= 1
        elif ic[i] == "," and d == 0:
            return i
    return -1


def _sadelestir(ifade: str) -> str:
    """İfadeyi **karşılaştırılabilir** hâle getirir: boşluklar, dış parantezler ve
    kataloğun teknik sarmalları (`ROUND`/`NULLIF`) düşer.

    ⚠ Bir SQL ayrıştırıcısı DEĞİL. Tek işi, kataloğun kendi ürettiği iki metnin aynı
    şeyi söyleyip söylemediğine bakmak. *Bir eşitliği aramak, bir dili çözümlemekten
    başka bir iştir.*

    🔴🔴 **SARMAL AÇMA BİR SÜS DEĞİL — ÖLÇÜLDÜ: 1 → 8.** Sarmalsız hâlde bütün katalogda
    **tek** bir ölçü ayrışıyordu (`ort_oee`). Sarmallar açılınca **sekiz** oldu ve
    çıkanlar tam da kullanıcının tarif ettiği *pay/payda* vakaları:

        fire_orani_yuzde = toplam_fire_kg (pay) / toplam_agirlik_kg (payda)
        kar_marji_yuzde  = kar (pay)            / toplam_ciro (payda)
        km_basi_maliyet  = nakliye_maliyeti     / toplam_mesafe

    ⊙ Ve **iki ölçüm gerekti**: yalnız `ROUND` açıldığında kazanç **sıfırdı** (1 → 1) ve
    az kalsın *«kazanç yok»* diye bırakıyordum. Eksik parça `NULLIF`'ti — payda hep
    `NULLIF(SUM(x),0)` biçiminde sarılı olduğu için hiçbir payda ölçüsü eşleşmiyordu.
    *Bir kazancı ölçerken yarım ölçmek, kazancın yokluğunu kanıtlamaz — yalnız yarısını
    görmemiş olursunuz.*
    """
    s = re.sub(r"\s+", "", str(ifade or ""))
    while s.startswith("(") and s.endswith(")"):
        # Dış parantez gerçekten eşleşiyor mu (yoksa "(a)*(b)" kırpılırdı)
        derinlik = 0
        kapali_disarida = False
        for i, ch in enumerate(s):
            derinlik += (ch == "(") - (ch == ")")
            if derinlik == 0 and i < len(s) - 1:
                kapali_disarida = True
                break
        if kapali_disarida:
            break
        s = s[1:-1]
    # Teknik sarmalları soy (iç içe olabilir: `ROUND(NULLIF(…),2)`); sınır bilinçli —
    # dört kat, bu katalogda ölçülen azami derinliğin iki katı.
    for _ in range(4):
        m = _SARMAL_RE.match(s)
        if not m:
            break
        ic = m.group(2)
        v = _son_virgul(ic)
        s = _sadelestir(ic[:v] if v > 0 else ic)
    return s


def bilesenler(olcu: str, cube_meta: dict | None) -> list[Bilesen]:
    """`§KN` — bir ölçünün formülündeki **katalog ölçüsü** bileşenleri.

    Kural: aynı küpteki başka bir ölçünün ifadesi, hedef ölçünün ifadesinde bir
    **alt-ifade** olarak geçiyorsa o bir bileşendir. Rolü, kendisinden hemen **önceki**
    işleçten okunur:

    | işleç | rol | yön | kullanıcının cümlesi |
    |---|---|---|---|
    | `*` (ya da ilk terim) | çarpan | `+1` | *«paydaki değerler arttıkça değer büyür»* |
    | `/` | payda | `-1` | *«payda arttıkça değer düşer»* |
    | `-` | terim | `-1` | |
    | `+` | terim | `+1` | |

    🔴🔴 **ALT-DİZE EŞLEŞMESİ YETMEZ — ve bunu ilk koşumda ölçtüm.** İlk yazımda bileşen
    *«ifadesi hedefin içinde geçiyorsa»* sayılıyordu ve gerçek katalogda şu çıktı:

        ort_oee bileşenleri: [kullanilabilirlik, performans, kalite, **toplam_uretim_kg**]

    `toplam_uretim_kg = SUM(uretim_kg)` ve o dizi `NULLIF(SUM(uretim_kg),0)`'ın **içinde**
    geçiyor — yani bir çarpan değil, kalite faktörünün **paydası**. Rolü de `carpan`
    hesaplanmıştı: kullanıcıya *«üretim kg, OEE'nin çarpanıdır»* denecekti. `§101.1`:
    böyle bir yanlış-pozitif, susmaktan **pahalıdır**.

    Doğru yüklem: bileşen, hedef ifadenin **ÜST-DÜZEY bir işleneni** olmalı. İfade
    derinlik-0'da işleçlerden bölünür ve her işlenen bir bileşen ifadesine **eşit** mi
    diye bakılır. Eşitlik, alt-dizeden başka bir iddiadır.

    *Bir parçayı bir bütünün içinde görmek, onun o bütünü oluşturduğunu göstermez.*
    """
    meta = cube_meta or {}
    ifadeler = meta.get("measure_expressions") or {}
    hedef = _sadelestir(ifadeler.get(olcu))
    if not hedef or not _SUM_RE.search(hedef):
        return []
    display = meta.get("measure_synonyms_display") or {}
    #: ifade → ölçü adı (üst-düzey işlenen eşitliği için)
    tersi = {_sadelestir(v): k for k, v in ifadeler.items() if k != olcu and v}
    _islenenler = _ust_duzey_islenenler(hedef)
    # ⚠ İlk işlenenin rolü **kendisinden sonra gelen işleçlere** bakar: hepsi `*` ise o
    # da bir **çarpandır**, bir «pay» değil. Bir çarpımın ilk terimine *«pay»* demek,
    # doğru yönü söyleyip yanlış adı vermektir — ve kullanıcı adı okur.
    _hepsi_carpim = all(i == "*" for i, _ in _islenenler[1:]) and len(_islenenler) > 1
    out: list[Bilesen] = []
    for islec, islenen in _islenenler:
        ad = tersi.get(islenen)
        if not ad:
            continue
        rol, yon = CARPAN, 1
        if islec == "/":
            rol, yon = PAYDA, -1
        elif islec == "-":
            rol, yon = TERIM, -1
        elif islec == "+":
            rol, yon = TERIM, 1
        elif islec == "":
            rol, yon = (CARPAN if _hepsi_carpim else PAY), 1
        out.append(Bilesen(ad=ad, rol=rol, yon=yon,
                           display=str(display.get(ad) or ad).replace("_", " ")))
    # ⚠ Tek bir bileşen bir **ayrıştırma** değildir (kendisiyle aynı şey olurdu).
    return out if len(out) >= 2 else []


def _ust_duzey_islenenler(ifade: str) -> list[tuple[str, str]]:
    """İfadeyi **derinlik-0** işleçlerinden böler → `[(önceki_işleç, işlenen), …]`.

    ⚠ Parantez derinliği sayılır: `NULLIF(SUM(x),0)` içindeki hiçbir şey üst düzey
    **değildir**. Bir SQL ayrıştırıcısı değil, bir **parantez sayacı** — ve yaptığı tek
    iddia budur.
    """
    out: list[tuple[str, str]] = []
    derinlik = 0
    parca: list[str] = []
    islec = ""
    for ch in ifade:
        if ch == "(":
            derinlik += 1
        elif ch == ")":
            derinlik -= 1
        if derinlik == 0 and ch in "*/+-" and parca:
            out.append((islec, _sadelestir("".join(parca))))
            islec, parca = ch, []
            continue
        parca.append(ch)
    if parca:
        out.append((islec, _sadelestir("".join(parca))))
    return out


def formul_metni(bl: list[Bilesen]) -> str:
    """`§KN` — bileşenlerin **rollerine göre** formül cümlesi.

    🔴 Ölçüldü (canlı, `kisi_basi_egitim_saati`): ilk yazımım bileşenleri koşulsuz
    `×` ile birleştiriyordu ve *«kişi başı eğitim = eğitim saati **×** eğitim alan»*
    yazdı — oysa **bölme**. Bir formülü yanlış beyan etmek, hiç beyan etmemekten
    kötüdür: kullanıcı onu doğru sanar ve üstüne akıl yürütür.

    *Bir açıklamanın ilk cümlesi yanlışsa, geri kalanı ne kadar doğru olursa olsun
    yanlış bir şeyin açıklamasıdır.*
    """
    _pay = [b.display for b in bl if b.yon > 0]
    _payda = [b.display for b in bl if b.yon < 0]
    if _payda:
        return (" × ".join(_pay) or "…") + " ÷ " + " × ".join(_payda)
    return " × ".join(_pay) or "…"


def ayristir(olcu: str, hedef: dict, akran: dict, cube_meta: dict | None,
             *, dusuk_iyi: bool | None = None) -> Ayristirma | None:
    """`§KN` — hedef ile akran arasındaki farkı **bileşenlere** ayırır.

    `hedef`/`akran`: `{ölçü_adı: değer}` — biri incelenen segment (ör. `RAM-3`), öteki
    karşılaştırma tabanı (ör. öteki makinelerin ortalaması). İkisi de **zaten
    hesaplanmıştır**; bu fonksiyon sorgu koşmaz.

    ⚠ Çarpımsal ayrıştırma yalnız **pozitif** değerlerde tanımlıdır (logaritma). Sıfır ya
    da negatif bir bileşen varsa `None` döner — *bir yöntemi tanımsız olduğu yerde
    zorlamak, bir sayı üretir ama bir bilgi üretmez.*
    """
    bl = [b for b in bilesenler(olcu, cube_meta)
          if b.ad in hedef and b.ad in akran]
    if len(bl) < 2:
        return None
    katkilar: list[Katki] = []
    for b in bl:
        from app.result_shape import sayi

        h, a = sayi(hedef.get(b.ad)), sayi(akran.get(b.ad))
        if h is None or a is None:
            return None
        if h <= 0 or a <= 0:
            return None
        katkilar.append(Katki(bilesen=b, hedef=h, akran=a,
                              katki=b.yon * (math.log(h) - math.log(a))))
    toplam = sum(abs(k.katki) for k in katkilar)
    if toplam <= 0:
        return None
    for k in katkilar:
        k.pay_yuzde = round(100.0 * abs(k.katki) / toplam, 1)
    # 🔴🔴 **«SUÇLU» ÖLÇÜNÜN YÖNÜNE GÖRE DEĞİŞİR — ve bunu canlıda ölçtüm.**
    #
    # ⊙ `fire_orani_yuzde`'de **düşük iyidir**. İlk yazımım *«en çok düşüren»* bileşeni
    # suçlu sayıyordu ve orada bu **yardım eden** bileşendi: iniş, oranı yükselten `fire`
    # yerine onu düşüren `ağırlık`ta derinleşti — yani doğru sayıyı bulup **yanlış taşı**
    # kaldırdı.
    #
    # Kural: ilgilenilen bileşen, ölçüyü **istenmeyen** yönde iten olandır. Yön beyan
    # edilmemişse (`GG8`) bir *«kötü»* yoktur; o zaman **en çok açıklayan** (mutlak
    # katkısı en büyük) seçilir ve anlatı bunu bir yargı olarak sunmaz.
    #
    # *Bir sayının hangi yöne gitmesinin kötü olduğunu bilmeden, sorumlusunu aramak
    # yalnız aritmetiktir.*
    if dusuk_iyi is None:
        katkilar.sort(key=lambda k: -abs(k.katki))
        _suclu = katkilar[0].bilesen if katkilar else None
    elif dusuk_iyi:
        katkilar.sort(key=lambda k: -k.katki)      # en çok YÜKSELTEN başa (yüksek = kötü)
        _suclu = katkilar[0].bilesen if katkilar[0].katki > 0 else None
    else:
        katkilar.sort(key=lambda k: k.katki)       # en çok DÜŞÜREN başa (düşük = kötü)
        _suclu = katkilar[0].bilesen if katkilar[0].katki < 0 else None
    try:
        _h, _a = float(hedef.get(olcu)), float(akran.get(olcu))
    except (TypeError, ValueError):
        _h = _a = 0.0
    return Ayristirma(olcu=olcu, hedef_deger=_h, akran_deger=_a,
                      katkilar=katkilar, sucllu=_suclu)


# 🔴 `§KN-ek`/`§KN-sayı` — **BİÇİM TEK SAHİPTE.** Bu üç fonksiyon burada doğdu ve
# `contribution` kendi kopyasını yazdığı için ayrıştılar (ölçüldü, `DD` turu, DD-13:
# *«47,836 dk … %83.4'i»* — üç ayrı hata). Gövde artık `app/sayi_bicimi.py`'de; burada
# yalnız **takma ad** var ki bu dosyanın çağrı yerleri değişmesin.
# *İki yerde biçimlendirilen bir sayı, er ya da geç iki farklı sayı gibi okunur.*
from app.sayi_bicimi import ek as _ek, sayi as _sayi, yuzde as _yuzde  # noqa: E402


def anlati(ayr: Ayristirma, *, segment: str, boyut: str,
           olcu_display: str = "", derinlesildi: bool = False) -> str:
    """`§KN` — ayrıştırmanın **cümlesi**: nereye baktım, ne gördüm, bu yüzden.

    ⚠ Cümle **ölçülmüş sayılardan** kurulur; hiçbir yargı eklenmez. `lower_is_better`
    bilgisi çağıranda olduğu için burada *«kötü»* denmez — *«daha düşük»* denir. Bir
    değer yargısı, ölçünün yönü beyan edilmeden verilemez (`GG8`).
    """
    _ad = olcu_display or ayr.olcu.replace("_", " ")
    bas = (f"**{segment}** ({boyut}) {_ad} değeri **{_sayi(ayr.hedef_deger)}** — "
           f"akran ortalaması **{_sayi(ayr.akran_deger)}**.")
    if not ayr.katkilar:
        return bas
    satirlar = []
    for k in ayr.katkilar:
        yon = "düşürüyor" if k.katki < 0 else "yükseltiyor"
        rol = {PAYDA: " (paydada)", TERIM: " (terim)"}.get(k.bilesen.rol, "")
        satirlar.append(f"· **{k.bilesen.display}**{rol}: {_sayi(k.hedef)} ↔ akran "
                        f"{_sayi(k.akran)} — farkın {_ek(_yuzde(k.pay_yuzde), True)} {yon}")
    # ⚠ Derinleşme **gerçekten** yapıldıysa *«bir sonraki adım onu açmak»* demek, yapılan
    # işi bir plan gibi sunmaktır. Kuyruk yalnız inilemediğinde yazılır.
    kuyruk = ""
    if ayr.sucllu and not derinlesildi:
        kuyruk = (f"\n\n→ Farkın en büyük kaynağı **{ayr.sucllu.display}**. "
                  f"Bir sonraki adım: onu kendi kırılımlarında açmak.")
    return bas + "\n" + "\n".join(satirlar) + kuyruk


# --- TAM TUR: bileşen sorgusu → akran tabanı → ayrıştırma → DERİNLEŞME ----------------
#
# ⚠ Bu bölüm de **sorgu koşmaz**: koşucuyu çağıran enjekte eder (`kos`). Böylece cebir
# testte gerçek bir motor olmadan sınanır ve aynı gövde hem `/ask` hem rapor yolunda
# kullanılabilir. `plan.calistir`'ın deseni birebir aynı sebeple böyledir.


def _yon_beyanli(olcu: str, cube_meta: dict | None) -> bool:
    """Ölçünün yönü katalogda **beyan edilmiş** mi?

    ⊙ Ölçüldü: şema **yalnız** `lower_is_better` listesini taşıyor; bir
    `higher_is_better` listesi **yok**. Yani *«listede değil»* iki farklı şey demek
    olabilir: *«yüksek iyidir»* ya da *«yönü yoktur»* (adet gibi nötr bir sayı).

    ⚠ `GG8` gereği ikisi **ayrılmaz sayılır**: beyan yoksa yön **bilinmiyordur**. O
    durumda `ayristir` bir *«kötü yön»* varsaymaz, yalnız **en çok açıklayanı** seçer —
    ve anlatı bunu bir yargı olarak sunmaz.

    *Bir listede olmamak, karşıt listede olmak değildir.*
    """
    return olcu in ((cube_meta or {}).get("lower_is_better") or [])


def _akran_ortalamasi(satirlar: list[dict], hedef_satir: dict, boyut: str,
                      alanlar: list[str]) -> dict:
    """Hedef DIŞINDAKİ satırların ortalaması — *«akran»* budur.

    ⚠ Ortalama, ağırlıksız: bir akranın *«tipik»* değeri sorulduğunda büyük segmentin
    küçüğü ezmesi istenmez. (Ağırlıklı taban ayrı bir sorunun cevabıdır ve o soru
    sorulmadı.)
    """
    from app.result_shape import sayi

    ötekiler = [r for r in satirlar if r is not hedef_satir]
    out: dict = {}
    for a in alanlar:
        # ⚠ `sayi()` — motor bazı ölçüleri **metin** döndürüyor (`"316"`, canlıda
        # ölçüldü) ve `isinstance` süzgeci onları eliyordu; bileşen sessizce düşüyordu.
        vals = [v for r in ötekiler if (v := sayi(r.get(a))) is not None]
        if vals:
            out[a] = sum(vals) / len(vals)
    return out


def hedef_sec(satirlar: list[dict], olcu: str, *, dusuk_iyi: bool,
              segment: str | None = None, boyut: str | None = None) -> dict | None:
    """İncelenecek segment: kullanıcı söylediyse **o**, söylemediyse **en aykırı** olan.

    ⚠ *«En aykırı»* ölçünün yönüne göredir (`lower_is_better`): düşük-iyi bir ölçüde
    en **yüksek** olan, yüksek-iyi bir ölçüde en **düşük** olan incelenir. Yönü beyan
    edilmemiş bir ölçüde *«kötü»* diye bir şey yoktur (`GG8`) — o zaman da en uçtaki
    değil, **en düşük** alınır ve anlatı bunu bir yargı olarak sunmaz.
    """
    from app.result_shape import sayi

    uygun = [r for r in satirlar if sayi(r.get(olcu)) is not None]
    if not uygun:
        return None
    if segment and boyut:
        for r in uygun:
            if str(r.get(boyut)) == str(segment):
                return r
    return (max(uygun, key=lambda r: sayi(r[olcu])) if dusuk_iyi
            else min(uygun, key=lambda r: sayi(r[olcu])))


def arastir(prev_cq: dict, cube_meta: dict | None, *, kos,
            segment: str | None = None, azami_derinlik: int = 1,
            oneri: bool = False) -> dict | None:
    """🔴🔴 `§KN` — **TAM TUR: «şuna baktım, şuraya gittim, gördüm ki…»**

    Kullanıcının istediği zincir:

    1. Ölçünün **formülünü** kataloğun içinden oku (bileşenler).
    2. İncelenen segmenti **akranlarıyla** kıyasla; hangi bileşen farkı açıklıyor?
    3. Suçlu bileşeni, o segmentin **içinde** bir başka kırılımda aç — **en dibe in**.
    4. Yolu anlat.

    ⚠ Bugünkü *«neden»* yolu (`contribution`) **zaman içindeki değişimi** açıklar. Bu
    onun rakibi değil **kardeşi**: burada soru *«neden geçen yıla göre düştü»* değil,
    *«neden akranlarından düşük»*. İkisi farklı sorulardır ve birini ötekinin yerine
    koymak, sorulmayan soruyu cevaplamaktır.

    Döner: `{anlati, ayristirma, adimlar}` ya da `None` (*«bu ölçü ayrıştırılamaz»*).
    """
    if not isinstance(prev_cq, dict):
        return None
    olculer = [str(m) for m in (prev_cq.get("measures") or [])]
    boyutlar = [str(d) for d in (prev_cq.get("dimensions") or [])]
    if not olculer:
        return None
    olcu = olculer[0]
    bl = bilesenler(olcu, cube_meta)
    if len(bl) < 2:
        _log.info("§KN: ayrıştırma YOK — «%s» için bileşen sayısı %d (<2)", olcu, len(bl))
        return None

    adimlar: list[str] = [f"formül okundu: **{olcu}** = {formul_metni(bl)}"]
    # 🔴🔴 **KESİTSEL KIYAS BİR ZAMAN SERİSİ DEĞİLDİR.**
    #
    # `timeDimensions` de düşer: ekrandaki cevap *«aylık makine bazında oee»* ise, onu
    # olduğu gibi kullanmak akran kıyasını `makine × ay` **hücrelerine** indirirdi —
    # yani *«RAM-3 akranlarına göre nasıl»* sorusu *«RAM-3'ün Mart ayı öteki hücrelere
    # göre nasıl»*a dönerdi. Soru segmentler arasıdır, zaman içinde değil.
    #
    # ⊙ Bu, `§RZ`'de canlıda ölçtüğüm kusurun **birebir kardeşi** (orada kırılım adayları
    # temelin zaman kovasını miras alıp kartezyene dönmüştü) — bu turda kendi kodumu
    # okurken yakalandı, kullanıcı görmeden.
    #
    # *Bir sorunun eksenini değiştiren her miras, cevabı da başka bir sorunun cevabına
    # çevirir.*
    _cq = {k: v for k, v in prev_cq.items()
           if k not in ("order", "limit", "pencere", "timeDimensions")}
    _alanlar = [olcu] + [b.ad for b in bl]
    # 🔴🔴 `§KN-tek` — **TEK BİR SAYIYA DA «NEDEN» SORULABİLİR; SORAN KIRILIM İSTEMEZ.**
    #
    # ⊙ Ölçüldü (curl `DD` turu, DD-8/DD-10): *«bu yıl ortalama oee»* → *«neden böyle»*
    # ve *«bu yıl kâr marjı»* → *«neden bu kadar düşük»* — ikisi de teknik bir **red**
    # alıyordu: *«ort_oee toplanabilir değil (cube metadata'sında non_additive) — katkı
    # payı matematiksel olarak tanımsız olur»*. Yani formülü **bildiğimiz** ölçüler,
    # tam da formülleri yüzünden cevapsız kalıyordu.
    #
    # ⊙ Kök: bu tur bir **akran kıyasıyla** başlıyordu ve akran bir **kırılım** ister.
    # Ekranda kırılım yoksa tur hiç başlamıyordu. Ama kullanıcının şartı açık:
    # *«bu tek bir değer olsa bile «neden böyle» sorulabilir, yine en köke inip
    # anlatmalı»*.
    #
    # ⚠ Çözüm bir varsayılan boyut **seçmek değil, ölçmektir**: adaylar koşulur ve
    # ölçüyü **en çok ayrıştıran** kırılım kazanır (`_en_ayristiran` — `derinles` ile
    # **aynı gövde**). İnsanın yaptığı da budur: *«bu sayı neden böyle?»* diye sorulunca
    # önce onu **neyin ayırdığına** bakarız.
    #
    # ⚠ Kazanan koşumun satırları **yeniden kullanılır**: bileşenler zaten `_alanlar`
    # ile birlikte çekilir, yani seçim bedava gelmez ama **iki kez** de ödenmez.
    #
    # *Bir sayının nedenini sormak için önce onu bölmek gerekir; hangi bıçakla
    # böleceğini bilmiyorsan, bıçakları dene.*
    satirlar: list[dict] = []
    if not boyutlar:
        from app.drill import available_dimensions

        _adaylar = [d["name"] for d in available_dimensions(cube_meta or {}, _cq)]
        _sec = _en_ayristiran(_cq, _alanlar, olcu, _adaylar[:AZAMI_ADAY], kos=kos)
        if _sec is None:
            _log.info("§KN-tek: ayrıştıran bir kırılım bulunamadı — «%s»", olcu)
            return None
        boyut, satirlar = _sec
        adimlar.append(f"ekranda kırılım yoktu → ölçüyü en çok ayrıştıran kırılım "
                       f"**{boyut}** seçildi")
    else:
        boyut = boyutlar[0]
    _cq["measures"] = _alanlar
    _cq["dimensions"] = [boyut]
    if not satirlar:
        satirlar = kos(_cq) or []
    if len(satirlar) < 2:
        _log.info("§KN: ayrıştırma YOK — bileşen sorgusu %d satır döndü (<2)", len(satirlar))
        return None
    adimlar.append(f"**{boyut}** kırılımında {len(satirlar)} segment ve "
                   f"{len(bl)} bileşen ölçüldü")

    dusuk_iyi = olcu in ((cube_meta or {}).get("lower_is_better") or [])
    hedef_satir = hedef_sec(satirlar, olcu, dusuk_iyi=dusuk_iyi,
                            segment=segment, boyut=boyut)
    if not hedef_satir:
        return None
    alanlar = [olcu] + [b.ad for b in bl]
    akran = _akran_ortalamasi(satirlar, hedef_satir, boyut, alanlar)
    ayr = ayristir(olcu, hedef_satir, akran, cube_meta,
                   dusuk_iyi=dusuk_iyi if _yon_beyanli(olcu, cube_meta) else None)
    if ayr is None:
        _log.info("§KN: ayrıştırma YOK — «%s» segmentinde bileşen değerleri "
                  "logaritmaya uygun değil (sıfır/negatif/okunamaz)", hedef_satir)
        return None
    _seg = str(hedef_satir.get(boyut))
    adimlar.append(f"**{_seg}** akran ortalamasıyla kıyaslandı → farkın kaynağı "
                   f"**{(ayr.sucllu or bl[0]).display}**")
    # 3 · DERİNLEŞME — suçlu bileşeni, hedef segmentin İÇİNDE başka bir kırılımda aç.
    # 🔴🔴 `§KN-yon2` — **İNİŞ YÖNÜ, BİLEŞENİN KENDİ DEĞERİNİN YÖNÜDÜR — ROLÜYLE
    # BİRLİKTE.** Ve bunu `§KN-tek` açtığı yeni bir vaka ortaya çıkardı.
    #
    # ⊙ Ölçüldü (curl `DD` turu, DD-12): `kar_marji_yuzde = kar ÷ ciro`, RAM-3 marjı
    # düşük ve suçlu **ciro** — çünkü RAM-3'ün cirosu akranlardan **YÜKSEK** (9,88M ↔
    # 6,41M) ve o **paydada**. İniş ise en **DÜŞÜK** cirolu tedarikçiyi gösterdi
    # (1,33M ↔ 2,14M) — yani sorunun kaynağını sorarken **en masumu** işaret etti.
    # Bu, daha önce `fire` üzerinde düzeltilen kusurun **payda ekseninde tekrarıydı**.
    #
    # ⊙ Kök tek satırda: `katki` **zaten** `b.yon * Δln`'dir (`ayristir`). Yani
    # `sign(katki)` bileşenin **ölçü üzerindeki etkisini** söyler, kendi değerinin
    # yönünü değil. İkisi payda bileşenlerinde **terstir**: ciro yükselince marj düşer.
    # Doğru işaret `sign(katki) × yon` — çünkü `sign(Δln) = sign(katki)·sign(yon)`.
    #
    #     fire (pay, katki+)     → +1 → en YÜKSEK fireli    ✅
    #     performans (pay, −)    → −1 → en DÜŞÜK performans ✅
    #     ciro (payda, −)        → +1 → en YÜKSEK cirolu    ✅ (önceden −1'di)
    #
    # *Bir sorumluyu ararken rolü unutmak, aynı veriyle en masumu suçlamaktır.*
    _isaret = next(((1 if k.katki > 0 else -1) * (k.bilesen.yon or 1)
                    for k in ayr.katkilar
                    if ayr.sucllu and k.bilesen.ad == ayr.sucllu.ad), -1)
    derin = (derinles(prev_cq, cube_meta, ayr.sucllu, _seg, boyut, kos=kos,
                      katki_isareti=_isaret)
             if (ayr.sucllu and azami_derinlik > 0) else None)
    metin = anlati(ayr, segment=_seg, boyut=boyut, derinlesildi=bool(derin),
                   olcu_display=str(((cube_meta or {}).get("measure_synonyms_display")
                                     or {}).get(olcu) or olcu).replace("_", " "))
    if derin:
        metin += "\n\n" + derin["metin"]
        adimlar.append(derin["adim"])
    if oneri:
        metin += "\n\n" + nereye_bak(ayr, _seg, boyut, derin)
    # 🔴🔴 **GİDİŞ YOLU BİR SÜS DEĞİL İÇERİKTİR — ve iki tık derinde duruyordu.**
    #
    # ⊙ Ölçüldü (frontend okundu): adımlar `trace`e yazılıyor, `Makbuz` onları çiziyor —
    # ama makbuz **kapalı bir `<details>`** ve tam iz **ikinci** bir `<details>`in içinde.
    # Yani kullanıcının *«şuna baktım, şuraya gittim»* zincirini görmesi için **iki tık**
    # gerekiyordu. Kullanıcının şartı ise onu **görmekti**.
    #
    # ⚠ Çözüm frontend'e satır eklemek değil (o dosya tavanda): yol **cevabın kendisine**
    # yazılır. Zaten öyledir — *nasıl bulduğunu söylemeyen bir kök-neden analizi, bir
    # iddiadan ibarettir.* İz makinece okunabilir kopyayı taşımaya devam eder.
    metin = ("🔍 **Nasıl buldum:** "
             + " → ".join(f"{i}\uFE0F\u20E3 {a}" for i, a in enumerate(adimlar, 1))
             + "\n\n" + metin)
    return {"anlati": metin, "ayristirma": ayr, "adimlar": adimlar,
            "segment": _seg, "boyut": boyut}


def nereye_bak(ayr: Ayristirma, segment: str, boyut: str,
               derin: dict | None) -> str:
    """`§KN` — *«ne yapmalıyız»*ın cevabı: **nereye bakılmalı**.

    🔴 Bilerek bir **reçete değil**, bir **işaret**. `prescribe.py` bir katkı raporundan
    aksiyon önerir; burada elimizde bir katkı raporu değil bir **formül ayrıştırması**
    var ve o, *«ne yapılmalı»*yı değil *«hangi taş kaldırılmalı»*yı bilir.

    ⚠ Uydurma alan tavsiyesi (*«bakım periyodunu kısaltın»*) **verilmez**: sistem
    makinenin fiziğini bilmez, verisini bilir. Söylediği tek şey ölçülmüş olandır —
    hangi bileşen, hangi alt-segment, ne kadar fark. *Bir öneri, dayanağından fazlasını
    iddia ettiği anda bir tahmine dönüşür.*
    """
    if not ayr.sucllu:
        return ""
    _pay = next((k.pay_yuzde for k in ayr.katkilar
                 if k.bilesen.ad == ayr.sucllu.ad), 0.0)
    nokta = (f" ve en çok **{derin['segment']}** tarafında ayrışıyor"
             if derin else "")
    return (f"→ **Öneri:** **{segment}** ({boyut}) için **{ayr.sucllu.display}** "
            f"incelenmeli — farkın {_ek(_yuzde(_pay))} oradan geliyor{nokta}. "
            f"Öteki bileşenler bu farkı açıklamıyor.")


def _en_ayristiran(temel: dict, olculer: list[str], sira_olcusu: str,
                   adaylar: list[str], *, kos) -> tuple[str, list[dict]] | None:
    """🔴🔴 **BİR KIRILIMIN AÇIKLAYICI OLUP OLMADIĞI ANCAK KOŞULARAK BİLİNİR.**

    Adaylar **sırayla koşulur**; ≥2 satır döndürenler arasından `sira_olcusu` üzerinde
    **yayılımı en geniş** olan seçilir. Yayılım, *«bu kırılım gerçekten ayrıştırıyor
    mu»* sorusunun ölçülmüş cevabıdır.

    ⊙ Ölçüldü (gerçek `oee` kataloğu, RAM-3): ilk aday `hat` seçilmişti ve derinleşme
    **hiç üretilmedi** — çünkü `hat` bir makinenin **içinde sabittir** (makine bir hatta
    aittir), tek satır döner. Sıra listesi bunu bilemez: `available_dimensions`
    maliyet/güven sıralar, **hiyerarşi** bilmez.

    ⚠ **Tek gövde, iki kat.** Aynı kural iki yerde gerekiyor — hangi kırılımda
    *başlanacağı* (`§KN-tek`) ve hangi kırılıma *inileceği* (`derinles`). İkinci bir
    kopya yazmak, zamanla iki farklı *«açıklayıcılık»* tanımı üretirdi (`KAT-1`).

    *Bir kırılımı denemeden seçmek, hiyerarşiyi bildiğini varsaymaktır.*
    """
    from app.result_shape import sayi

    en_iyi = None
    for aday in adaylar:
        _satirlar = kos({**temel, "measures": list(olculer),
                         "dimensions": [aday]}) or []
        _uygun = [r for r in _satirlar if sayi(r.get(sira_olcusu)) is not None]
        if len(_uygun) < 2:
            continue
        _degerler = [sayi(r[sira_olcusu]) for r in _uygun]
        _yayilim = max(_degerler) - min(_degerler)
        if en_iyi is None or _yayilim > en_iyi[0]:
            en_iyi = (_yayilim, aday, _uygun)
    return (en_iyi[1], en_iyi[2]) if en_iyi else None


def derinles(prev_cq: dict, cube_meta: dict | None, suclu: Bilesen,
             segment: str, boyut: str, *, kos, katki_isareti: int = -1) -> dict | None:
    """`§KN` — **en dibe in**: suçlu bileşeni, hedef segmentin içinde ikinci bir
    kırılımda aç ve en aykırı alt-segmenti bul.

    ⊙ Kullanıcının örneği birebir bu: *«en dibe indim ve gördüm ki vardiya 1'de …
    bu makine çok durmuş»*. Yani ikinci kırılım, birincinin **içindedir** — bir yan yana
    kıyas değil bir **iniş**.

    ⚠ İkinci boyutu `drill.available_dimensions` seçer (kullanılmış boyutları ve
    süzgeçtekileri eler) — ikinci bir sıralama kuralı yazmak `KAT-1` olurdu.
    """
    from app.drill import available_dimensions
    from app.result_shape import sayi

    _temel = {k: v for k, v in prev_cq.items()
              if k not in ("order", "limit", "pencere", "timeDimensions")}
    _temel["filters"] = [*(prev_cq.get("filters") or []),
                         {"dimension": boyut, "operator": "eq", "value": segment}]
    adaylar = [d["name"] for d in available_dimensions(cube_meta or {}, _temel)
               if d["name"] != boyut][:AZAMI_ADAY]
    if not adaylar:
        return None
    # 🔴🔴 **BİR KIRILIMIN AÇIKLAYICI OLUP OLMADIĞI ANCAK KOŞULARAK BİLİNİR.**
    #
    # ⊙ Ölçüldü (gerçek `oee` kataloğu, RAM-3): ilk aday `hat` seçildi ve derinleşme
    # **hiç üretilmedi** — çünkü `hat` bir makinenin **içinde sabittir** (makine bir
    # hatta aittir), tek satır döner. Sıra listesi bunu bilemez: `available_dimensions`
    # maliyet/güven sıralar, **hiyerarşi** bilmez ve kendi docstring'i de *«hangi boyutun
    # daha açıklayıcı olduğu önceden bilinemez»* diyor.
    #
    # Kural: adaylar **sırayla koşulur**, ≥2 satır döndürenler arasından **yayılımı en
    # geniş** olan seçilir. Yayılım, *«bu kırılım gerçekten ayrıştırıyor mu»* sorusunun
    # ölçülmüş cevabıdır. `§RZ-2`'nin birebir aynı dersi.
    #
    # *Bir kırılımı denemeden seçmek, hiyerarşiyi bildiğini varsaymaktır.*
    _en = _en_ayristiran(_temel, [suclu.ad], suclu.ad, adaylar, kos=kos)
    if _en is None:
        return None
    d2, uygun = _en
    # 🔴🔴 **İNİŞ YÖNÜ, BİLEŞENİN KATKI İŞARETİNE GÖRE — ve bunu canlıda ölçtüm.**
    #
    # ⊙ `fire_orani_yuzde` (düşük iyi): suçlu `fire` ve oranı **yükseltiyor** (+). İlk
    # yazımım *«pay bileşeninde en düşüğü ara»* diyordu ve **en az fire veren**
    # tedarikçiyi gösterdi (5.634 ↔ 16.106) — yani sorunun kaynağını sorarken **en
    # masumu** işaret etti.
    #
    # Doğru kural kendi içinde tutarlı ve fazladan bilgi istemez: alt-segment, suçlunun
    # **katkısıyla aynı yönde** en uçta olandır. `fire` yükseltiyorsa en **yüksek**
    # fireli, `performans` düşürüyorsa en **düşük** performanslı.
    #
    # *Bir sorumluyu ararken yönü karıştırmak, aynı veriyle en masumu suçlamaktır.*
    en = (max(uygun, key=lambda r: sayi(r[suclu.ad])) if katki_isareti > 0
          else min(uygun, key=lambda r: sayi(r[suclu.ad])))
    otekiler = [sayi(r[suclu.ad]) for r in uygun if r is not en]
    ort = sum(otekiler) / len(otekiler) if otekiler else sayi(en[suclu.ad])
    _lbl = ((cube_meta or {}).get("dimension_labels") or {}).get(d2, d2)
    return {
        "metin": (f"→ **{segment}** içinde {suclu.display} en çok **{en.get(d2)}** "
                  f"({_lbl}) tarafında ayrışıyor: **{_sayi(sayi(en[suclu.ad]))}** ↔ "
                  f"öteki {_lbl} ortalaması **{_sayi(ort)}**."),
        "adim": f"**{segment}** içinde **{_lbl}** kırılımı açıldı → **{en.get(d2)}**",
        "boyut": d2, "segment": str(en.get(d2)),
    }


# --- MOTORA BAĞLANTI: cebir ile motor arasındaki TEK yüzey ----------------------------


def kosucu(service, *, limit: int = 1000):
    """`§KN` — cebiri motora bağlayan **tek** yer.

    ⚠ Yukarıdaki her şey sorgu koşmaz ve bu bilinçlidir: cebir gerçek bir motor olmadan
    sınanabilsin. Burada da yeni bir çalıştırma yolu **icat edilmez** — `cube_sql` +
    `query`, yani `/cube`'un kullandığı aynı ikili. *Bir hesabı iki yoldan koşturmak,
    bir gün iki farklı sayı almanın en kısa yoludur.*
    """
    def _kos(cq: dict) -> list[dict]:
        try:
            return (service.query(service.cube_sql(cq), limit=limit) or {}).get("rows") or []
        except Exception:                      # noqa: BLE001 — bir aday düşerse tur düşmez
            # 🔴 `ADR-0020` — **SESSİZ YUTMA YOK.** İlk yazımda buradaki `except` sessizdi
            # ve tam da bu yüzden bir kusuru **teşhis edemedim**: `§KN` canlıda susuyordu,
            # logda hiçbir iz yoktu ve prob'da aynı sorgu çalışıyordu. Bir dalın sessizce
            # kapanması, o dalın var olmadığı anlamına gelmez — yalnız görünmediği.
            _log.info("§KN: bileşen sorgusu düştü (%s)",
                      json.dumps({k: v for k, v in (cq or {}).items()
                                  if k in ("cube", "measures", "dimensions")},
                                 ensure_ascii=False), exc_info=True)
            return []
    return _kos


def cevap_verisi(prev_cq: dict, cube_meta: dict | None, *, service,
                 limit: int = 1000, segment: str | None = None,
                 oneri: bool = False) -> dict | None:
    """`§KN` — `/ask`'in *«neden böyle»* dalı için hazır cevap verisi.

    Döner: `{anlati, iz, chipler}` ya da `None` (*«bu ölçü kesitsel olarak
    ayrıştırılamaz»* → çağıran bugünkü `contribution` yoluna devam eder).

    ⚠ **`contribution`un rakibi değil kardeşi.** O *«geçen döneme göre neden değişti»*i
    açıklar; bu *«akranlarına göre neden farklı»*yı. İkisi farklı sorulardır; birini
    ötekinin yerine koymak, sorulmayan soruyu cevaplamaktır. Bu yüzden `§KN` **önce**
    denenir (kırılım + formül varsa soru kesitseldir) ama başarısız olursa yol
    **bayt bayt bugünküdür** (`KURAL B`).

    ⚠ Adımlar `iz`e yazılır: kullanıcının gördüğü *«şu anda şuna baktım, oraya gittim»*
    zinciri budur ve bir süs değil **denetlenebilirliktir** — her adım bir sorguya karşılık
    gelir.
    """
    # 🔴 `oneri` bir **bayrak** olarak gelir, bir **soru türü** olarak değil — ve bunu
    # bir kapı öğretti: `test_MUTFAK_dil_ayristiramaz`. Bu modül 🍳 mutfaktır; `followup`
    # bir 🗣 garson modülüdür ve `TUR_NE_YAPMALI` bir **dil sınıfıdır**. Onu buradan
    # okumak, mutfağa sipariş defterini açtırmak olurdu.
    # ⚠ Bedeli ölçüldü ve kabul edildi: `ask()`te **bir satır** (bkz. muafiyet
    # `kn-kesitsel-neden`). *Bir sınırı korumanın bedeli, sınırı kaldırmanın bedelinden
    # her zaman küçüktür.*
    _kos = kosucu(service, limit=limit)
    out = arastir(prev_cq, cube_meta, kos=_kos, segment=segment, oneri=oneri)
    # ⟳🔴 **`§KN-toplam` BURADAN KALDIRILDI — ÇÜNKÜ EZİYORDU, ZENGİNLEŞTİRMİYORDU.**
    #
    # ⊙ Ölçüldü (tam kapı, `EE` demeti): buraya konunca **altı** test kırmızı verdi ve
    # hepsi aynı şeyi söylüyordu — *«reçete izde yok»* · *«açıklama cevabı bozuldu»* ·
    # *«konuşma cevabı **zengin gövde** taşımıyor — UI chip'e düşer»*. Toplanabilir bir
    # ölçüde `contribution`/`prescribe` yolu **yapısal bir gövde** üretiyor (kartlar,
    # chip'ler, ajan izi); benim anlatım yalnız bir **not**tu. Yani daha iyi bir cümle
    # için daha zengin bir cevabı feda ediyordum.
    #
    # ⚠ Doğru yer `toplam_ek` (aşağıda): var olan cevabın **üstüne** yazar. Kullanıcı
    # hem yapısal gövdeyi hem iniş anlatısını alır. *Bir aracı öne almak, ondan iyi
    # olduğunu değil, ötekini görmediğini gösterir.*
    if not out:
        return None
    _boyut = out.get("boyut") or ""
    _seg = out.get("segment") or ""
    chipler = [{"label": f"{_seg} — tek başına aç", "kind": "dimension",
                "cube_query": {**{k: v for k, v in prev_cq.items()
                                  if k not in ("order", "limit", "pencere")},
                               "filters": [*(prev_cq.get("filters") or []),
                                           {"dimension": _boyut, "operator": "eq",
                                            "value": _seg}]}}]
    return {"anlati": out["anlati"],
            "iz": [f"§KN: {a}" for a in out["adimlar"]],
            "chipler": chipler}


# --- `§NB` · AÇIKLANAMAYAN BİR «NEDEN» SESSİZCE BAŞKA BİR SORUYA DÖNÜŞEMEZ -------------


def aciklanamadi(prev_cq: dict, cube_meta: dict | None) -> tuple[str, list[dict]]:
    """🔴🔴 `§NB` — **BİR «NEDEN» SORUSU CEVAPSIZ KALABİLİR; BAŞKA BİR SORUYA DÖNÜŞEMEZ.**

    ## Ölçülen kusur (curl, 2026-08-11)

        «bu yıl makine bazında duruş dakika»  →  «neden böyle»
          → 66 satırlık TABLO · not YOK · genel chip'ler
          iz: «Takip: LLM-destekli yapısal düzenleme»

    ⊙ Kök tam da `ask.py`'nin kendi yorumunun uyardığı yerdeydi: konuşma dalı
    `deterministic_refine`'dan **önce** yakalanır *(«aksi halde «neden»/«düşüş» gibi
    kelimeler onun sözlük eşleşmesine karışır»)* — ama o dal **hiçbir şey üretemeyince**
    `None` dönüyor ve tur tam o çarpışmanın içine düşüyordu: `makine_duruslari` küpünde
    `neden` **bir boyut adıdır** (duruş nedeni) ve garson *«neden böyle»*yi *«nedene göre
    kır»* diye okudu.

    🔴 Sonuç kazara **makul** bir tabloydu — ve bu onu daha da kötü yapar: kullanıcı bir
    **açıklama** sordu, sessizce **başka bir sorunun cevabını** aldı ve bunu anlamasının
    hiçbir yolu yoktu.

    ## Çözüm: düşüş SESSİZ olamaz

    Dürüst bir red **birinci sınıftır** ama tek başına yetmez (kullanıcının kuralı):
    yanına **yapılabilecek olan** konur. Burada o, kataloğun kendi boyutlarıdır —
    `drill.available_dimensions` (maliyet/güven sıralı, kullanılmışları eler).

    ⚠ Ve **uydurma bir sebep yazılmaz**: sistem *«şu yüzden düşük»* demez, *«bu ölçüyü
    ayrıştıramadım, şu kırılımlar açılabilir»* der.

    *Cevaplayamadığını söylemeyen bir sistem, cevapladığını sanmaya devam eder.*
    """
    from app.drill import available_dimensions

    olcu = next((str(m) for m in ((prev_cq or {}).get("measures") or [])), "")
    _ad = str(((cube_meta or {}).get("measure_synonyms_display") or {}).get(olcu)
              or olcu).replace("_", " ")
    adaylar = available_dimensions(cube_meta or {}, prev_cq or {})[:3]
    chipler = [{"label": f"{d['label']} kırılımı", "kind": "dimension",
                "cube_query": {**{k: v for k, v in (prev_cq or {}).items()
                                  if k not in ("order", "limit", "pencere")},
                               "dimensions": [*(prev_cq.get("dimensions") or []),
                                              d["name"]]}}
               for d in adaylar]
    _kuyruk = (" Şu kırılımlar açılabilir: "
               + " · ".join(f"**{d['label']}**" for d in adaylar) + "."
               if adaylar else "")
    # 🔴 `§E4` — *«kök neden»* bir NEDENSELLİK iddiasıdır; ölçtüğümüz **katkıdır**.
    # Kullanıcıya dönen tek sızıntı buydu (arka uçtaki öteki anmalar yorum/docstring).
    return (f"**«{_ad}» için bir katkı ayrıştırması üretemedim.** Bu ölçünün formülü "
            f"tek parça (bileşenlerine ayrılmıyor) ve elimdeki dönemde açıklanacak bir "
            f"**değişim** de yok — yani gösterebileceğim bir *katkı* yok."
            f"{_kuyruk}", chipler)


def makbuz_satiri(olcu: str, ad: str, cube_meta: dict | None) -> str | None:
    """🔴🔴 `§MK-formül` — **AYNI KATALOĞU İKİ YERDE OKUYUP BİRİNDE İNSANCA SÖYLEMEK,
    ÖTEKİNDE SUSMAK.**

    ⊙ Ölçüldü (curl `CC` turu, CC-2): *«bu nasıl hesaplandı»* → `ort_oee` için **ham
    SQL** (üç `SUM`/`NULLIF` iç içe) ve üstünde kaçamak bir cümle:
    *«toplam/ortalamasıdır»*. Aynı turda CC-11 (*«neden»*) **aynı** ölçü için
    *«ort_oee = kullanılabilirlik × performans × kalite»* diyebiliyordu — çünkü `§KN`
    bileşenleri kataloğun **kendi metninden** okuyor. Bilgi elimizdeydi; makbuz onu
    **istemiyordu**.

    ⚠ SQL **gizlenmiyor**: makbuzun kendi kararı (*«gizlemek makbuzu süse çevirir»*)
    geçerli. İnsanca formül SQL'in **yerine** değil, **önüne** konur.
    ⚠ Bileşen çıkmayan ölçüde `None` → bugünkü makbuz bayt bayt korunur (`KURAL B`).

    *Bir sistemin bildiğini bir yerde söyleyip başka yerde susması, bilgi eksikliği
    değil bir tutarsızlıktır — ve kullanıcı onu ikincisiyle tanır.*
    """
    try:
        bl = bilesenler(olcu, cube_meta)
    except Exception:                    # noqa: BLE001 — makbuz düşmez (ADR-0020)
        _log.warning("§MK-formül: bileşen okunamadı (best-effort)", exc_info=True)
        return None
    return f"  ↳ **{ad}** = {formul_metni(bl)}" if bl else None


def taze_ek(resp, q_norm: str, cq: dict, cube_meta: dict | None, *, service,
            limit: int = 1000) -> bool:
    """🔴🔴 `§KN-taze` — **TAZE BİR «NEDEN» SORUSUNUN İKİNCİ YARISI DA CEVAPLANIR.**

    ⊙ Ölçüldü (curl `DD` turu, DD-20): *«bu yıl enerji tüketimi **neden yüksek**»* →
    `elektrik_tuketimi_kwh` + `tep_toplam` döndü, kök-neden **hiç** çalışmadı. `§KN`
    yalnız **takip** dalında yaşıyordu (`_cevap_ustunde_konus`), oysa kullanıcının
    şartında bir takip koşulu yok: *«neden sorusu geldiğinde adeta insan zihnini
    simüle etmeliyiz»*.

    ⚠ Sayı **bugünkü gibi** hesaplanır; bu fonksiyon onun **üstüne** yazar. Yani
    `KURAL B`: *«neden»* taşımayan hiçbir soruda tek bir bayt değişmez, ve `§KN`
    ayrıştıramazsa cevap aynen bugünküdür.

    ⚠ `oneri=False`: öneri **yalnız sorulduğunda** verilir (`§KN`'nin kendi kuralı);
    *«neden yüksek»* bir açıklama ister, bir aksiyon planı değil.

    Döner: eklendi mi (çağıran ize bunu yazar).
    """
    if not isinstance(cq, dict) or not (cq.get("measures") or []):
        return False
    try:
        out = cevap_verisi(cq, cube_meta, service=service, limit=limit, oneri=False)
    except Exception:                    # noqa: BLE001 — cevap düşmez (ADR-0020)
        _log.warning("§KN-taze: ayrıştırma hata verdi (best-effort)", exc_info=True)
        return False
    if not out:
        return False
    resp.note = "\n\n".join(x for x in [resp.note, out["anlati"]] if x)
    resp.trace = [*(resp.trace or []), *out["iz"]]
    # ⚠ `next_steps`'e **dokunulmaz**: taze yolda o liste `_attach_next_steps`'in
    # (sunum katmanı) ve pydantic modelinin işidir; buradan sözlük iliştirmek bir tip
    # kaçağı olurdu. Kullanıcının ihtiyacı olan **anlatı**dır; chip'ler zaten gelir.
    # *Bir modülün sınırı, elinden gelen son şeyi de yapmadığı yerdir.*
    return True


def toplam_turu(prev_cq: dict, cube_meta: dict | None, *, kos,
                oneri: bool = False) -> dict | None:
    """🔴🔴 `§KN-toplam` — **FORMÜLÜ OLMAYAN BİR ÖLÇÜNÜN DE KÖKÜ VARDIR.**

    ## Kullanıcının şartı, birebir

    > *«Formül değerleri db'den gelir, yani bir şeyi temsil eder — satış adedi gibi,
    > duruş zamanı gibi. Ya da genel bir şeyi temsil eder, **onun da alt kırılımları
    > vardır, en köke kadar gitmeli**.»*

    ## Ölçülen kusur (curl `EE` turu, EE-2/EE-3)

        «müşteri bazında bu yıl toplam ciro» → «neden»
          → *«Değişimi en çok sürükleyen segmentler aşağıda…»*

    Soru **kesitseldi** (*«neden bu müşteri böyle»*), cevap **zamansaldı** (*«geçen
    döneme göre ne değişti»*). `§KN` susuyordu çünkü `toplam_ciro`'nun katalogda
    bileşeni yok — ve susunca `contribution` devralıyor, yani **başka bir sorunun**
    cevabı veriliyordu.

    ## Cebir — logaritma değil **pay**

    Bir çarpım/oran ölçüsünde soru *«hangi bileşen»*dir; bir **toplamda** böyle bir
    bileşen yoktur, çünkü toplam kendi alt segmentlerinin **doğrudan** toplamıdır:

        toplam = Σ segment_i        →  segment_i'nin payı = değer_i / toplam

    Yani iniş, bileşen ekseninde değil **kırılım ekseninde** olur: en büyük segmenti
    bul, payını söyle, sonra o segmentin **içinde** ikinci bir kırılım aç ve orada da
    en büyüğü bul. Kullanıcının *«en dibe indim ve gördüm ki…»* cümlesi budur.

    ⚠ Uydurma yok: yalnız **ölçülmüş** paylar yazılır, bir nedensellik iddia edilmez.
    Cümle *«şu kadarını bu taşıyor»* der, *«bu yüzden»* demez — çünkü bir pay bir
    açıklama değil bir **konumdur**. *Bir sayının nereden geldiğini söylemek, neden
    öyle olduğunu söylemekten farklıdır; ikincisini iddia etmek için bir formül gerekir.*

    ⚠ `lower_is_better` **okunur**: yön beyanı yoksa yargı da yoktur (`GG8`).

    Döner: `{anlati, adimlar, segment, boyut}` ya da `None`.
    """
    from app.drill import available_dimensions
    from app.result_shape import sayi

    if not isinstance(prev_cq, dict):
        return None
    olculer = [str(m) for m in (prev_cq.get("measures") or [])]
    if len(olculer) != 1:
        return None
    olcu = olculer[0]
    if len(bilesenler(olcu, cube_meta)) >= 2:
        return None                       # formül var → `arastir` onun işi
    # 🔴🔴 **PAY CEBİRİ YALNIZ TOPLANABİLİR BİR ÖLÇÜDE ANLAMLIDIR — ve bunu kendi
    # düzeltmem öğretti.**
    #
    # ⊙ İlk yazımda bu kapı yoktu ve canlı ölçüm (curl `EE` turu) şunu üretti:
    # *«MURAT DEMİR tek başına **ilk seferde tamam** toplamının %11,8'ini taşıyor»* —
    # `ilk_seferde_tamam_yuzde` bir **yüzde**. Yüzdeler toplanmaz; o cümlenin paydası
    # (85,39 + 80,09 + …) hiçbir şeydir. Yani doğru biçimlendirilmiş, akıcı ve
    # **anlamsız** bir cevap üretmiştim.
    #
    # ⚠ Sınıflandırıcı **yeniden yazılmadı, ÇAĞRILDI**: `contribution.toplanabilirlik`
    # `non_additive` beyanını, `AVG(`/`/`/`MIN(`/`MAX(` ifadesini ve ad sezgisini
    # (`ort_*`, `*_yuzde`) zaten biliyor. İkinci bir toplanabilirlik tanımı yazmak,
    # aynı ölçüye iki farklı cevap vermenin en kısa yoludur (`KAT-1`).
    #
    # ⚠ `TAM` şartı bilinçli: `YARI` (stok/bakiye) zaman-dışı eksende toplanır ama
    # burada hangi eksende olduğumuzu bilmiyoruz; `BILINMIYOR`da susmak `§101.1`.
    #
    # *Bir cebiri tanımsız olduğu yerde zorlamak, bir sayı üretir ama bir bilgi üretmez.*
    from app.contribution import TAM, toplanabilirlik

    if toplanabilirlik(olcu, cube_meta)[0] != TAM:
        return None
    _cq = {k: v for k, v in prev_cq.items()
           if k not in ("order", "limit", "pencere", "timeDimensions")}
    boyutlar = [str(d) for d in (prev_cq.get("dimensions") or [])]
    adimlar: list[str] = []
    if boyutlar:
        boyut = boyutlar[0]
        satirlar = kos({**_cq, "measures": [olcu], "dimensions": [boyut]}) or []
    else:
        _ad = [d["name"] for d in available_dimensions(cube_meta or {}, _cq)]
        _sec = _en_ayristiran(_cq, [olcu], olcu, _ad[:AZAMI_ADAY], kos=kos)
        if _sec is None:
            return None
        boyut, satirlar = _sec
        adimlar.append(f"ekranda kırılım yoktu → ölçüyü en çok ayrıştıran kırılım "
                       f"**{boyut}** seçildi")
    _uygun = [r for r in satirlar if sayi(r.get(olcu)) is not None]
    if len(_uygun) < 2:
        return None
    adimlar.insert(0, f"**{olcu}** bir toplam — bileşeni yok, o yüzden **kırılım "
                      f"ekseninde** ayrıştırıldı")
    adimlar.append(f"**{boyut}** kırılımında {len(_uygun)} segment ölçüldü")
    # 🔴🔴 **PAY CEBRİ — SESSİZ-YANLIŞ ONARILDI (⟳ 2026-08-12, denetim bulgusu).**
    #
    # Eski hâli paydayı **mutlak** toplamdan alıyordu (`sum(abs(...))`) ama cümle
    # *«toplamının %P'ini taşıyor»* diyordu; `_akran` da **mutlak** ortalamaydı ama
    # cümle *«öteki ortalaması»* diyordu. Karışık işaretli bir `SUM` ölçüsünde
    # (`enerji_sapma.toplam_enpg` — `lower_is_better`, tasarım gereği ±) ölçüldü:
    #
    #     değerler   : +9000 · −4500 · −3000 · 0
    #     brüt       : 16.500      net (GERÇEK toplam): 1.500
    #     basılan pay: %54,5       gerçek pay        : %600      ← 11 KAT
    #     basılan akran: +2.500    gerçek akran      : −2.500    ← İŞARET TERS
    #
    # Akıcı, doğru biçimlendirilmiş ve **güvenle yanlış** bir cümle. `§101.1`'in
    # tersi: bir yanlış-pozitif değil, **bir yanlış SAYI**.
    #
    # ⊙ Kural yeniden yazılmadı: `contribution.contributions()` (`:191-196`) bu cebri
    # **zaten** taşıyor — *«net pay ancak net değişim brüt hareketin anlamlı bir
    # kısmıysa yorumlanabilir»*. Aynı eşik (%1) burada da uygulanıyor (`KAT-1`).
    #
    # *Bir payı mutlak değerlerle hesaplayıp «toplamın payı» diye sunmak, işaretleri
    # yok sayıp güven satmaktır.*
    _brut = sum(abs(sayi(r[olcu]) or 0.0) for r in _uygun)
    _net = sum(sayi(r[olcu]) or 0.0 for r in _uygun)
    if _brut <= 0:
        return None
    _dusuk_iyi = olcu in ((cube_meta or {}).get("lower_is_better") or [])
    _hedef = max(_uygun, key=lambda r: abs(sayi(r[olcu]) or 0.0))
    _seg = str(_hedef.get(boyut))
    _hv = sayi(_hedef[olcu]) or 0.0
    # 🔴 **İKİ ŞART** — ve ikincisi ilk düzeltmemde EKSİKTİ (ders ㉚).
    # ① `contribution`'ın eşiği: net, brütün anlamlı bir kısmı olmalı (işaretler
    #    birbirini götürmesin).
    # ② **PAY %100'Ü AŞAMAZ.** Karışık işaretli bir toplamda bu matematiksel olarak
    #    mümkündür (+9000 / net 1500 = **%600**) ama cümle *«toplamının %P'ini
    #    taşıyor»* diyor — ve bir parçanın bütünün altı katını *taşıması* okuyucunun
    #    zihninde bir anlam taşımaz. İlk düzeltmem yalnız ①'i koydu ve kapı **%600**
    #    basmaya devam etti; ölçüm yakaladı.
    # *Doğru hesaplanmış bir sayı, yanlış bir cümlede hâlâ yanlıştır.*
    _ham = (100.0 * _hv / _net) if _net else None
    _pay = (_ham if (_ham is not None and abs(_net) > _brut * 0.01
                     and abs(_ham) <= 100.0) else None)
    _akran = (_net - _hv) / max(1, len(_uygun) - 1)          # 🔴 İŞARETLİ ortalama
    adimlar.append(f"en büyük segment **{_seg}** — toplamın {_ek(_yuzde(_pay))}"
                   if _pay is not None else
                   f"en büyük segment **{_seg}** — ⚠ pay hesaplanamadı: segmentler "
                   f"birbirini götürüyor (brüt {_sayi(_brut)} ↔ net {_sayi(_net)})")
    _disp = str(((cube_meta or {}).get("measure_synonyms_display") or {}).get(olcu)
                or olcu).replace("_", " ")
    _yargi = (" (bu ölçüde **düşük** iyidir)" if _dusuk_iyi else "")
    metin = ((f"**{_seg}** ({boyut}) tek başına **{_disp}** toplamının "
              f"{_ek(_yuzde(_pay), True)} taşıyor: **{_sayi(_hv)}** ↔ öteki "
              f"{boyut} ortalaması **{_sayi(_akran)}**{_yargi}.")
             if _pay is not None else
             # ⚠ Pay basılamıyorsa cümle **büyüklüğe** iner ve nedenini SÖYLER —
             # sessizce yanlış bir yüzde basmaktansa eksik ama doğru bir cümle.
             (f"**{_seg}** ({boyut}) en büyük tekil **{_disp}** hareketi: "
              f"**{_sayi(_hv)}** ↔ öteki {boyut} ortalaması **{_sayi(_akran)}**{_yargi}. "
              f"⚠ Toplam içindeki payı **hesaplanamadı**: segmentler birbirini "
              f"götürüyor (brüt {_sayi(_brut)} ↔ net {_sayi(_net)})."))
    # 🔴 EN DİBE İN — segmentin **içinde** ikinci bir kırılım. `derinles` bir `Bilesen`
    # ister (formül ekseni); burada eksen ölçünün kendisidir, o yüzden süpürücü
    # **doğrudan** çağrılır — ikinci bir «açıklayıcılık» tanımı yazılmaz (`KAT-1`).
    _ic = {**_cq, "filters": [*(prev_cq.get("filters") or []),
                              {"dimension": boyut, "operator": "eq", "value": _seg}]}
    _ad2 = [d["name"] for d in available_dimensions(cube_meta or {}, _ic)
            if d["name"] != boyut][:AZAMI_ADAY]
    _derin = _en_ayristiran(_ic, [olcu], olcu, _ad2, kos=kos) if _ad2 else None
    if _derin:
        d2, satir2 = _derin
        _u2 = [r for r in satir2 if sayi(r.get(olcu)) is not None]
        _t2 = sum(abs(sayi(r[olcu]) or 0.0) for r in _u2) or 1.0
        _h2 = max(_u2, key=lambda r: abs(sayi(r[olcu]) or 0.0))
        _p2 = 100.0 * abs(sayi(_h2[olcu]) or 0.0) / _t2
        adimlar.append(f"**{_seg}** içinde **{d2}** kırılımı açıldı → "
                       f"**{_h2.get(d2)}**")
        metin += (f"\n\n→ **{_seg}** içinde en çok **{_h2.get(d2)}** ({d2}) "
                  f"ayrışıyor: **{_sayi(sayi(_h2[olcu]))}**, bu segmentin "
                  f"{_ek(_yuzde(_p2))}.")
        if oneri:
            metin += (f"\n\n→ **Öneri:** **{_seg}** ({boyut}) içinde **{_h2.get(d2)}** "
                      f"({d2}) incelenmeli — segmentin {_ek(_yuzde(_p2))} oradan "
                      f"geliyor.")
    elif oneri:
        # ⚠ İKİNCİ pay cümlesi — `_pay` `None` olabilir (işaretler götürüyor ya da
        # pay %100'ü aşıyor). Korumasız bırakılırsa *«toplamın None'ı»* basardı.
        # *Bir düzeltme, aynı sayının ÖTEKİ kullanım yerini de kapsamalıdır* (ders ㉚).
        metin += (f"\n\n→ **Öneri:** **{_seg}** ({boyut}) incelenmeli — toplamın "
                  f"{_ek(_yuzde(_pay))} tek başına orada."
                  if _pay is not None else
                  f"\n\n→ **Öneri:** **{_seg}** ({boyut}) incelenmeli — en büyük tekil "
                  f"hareket orada (**{_sayi(_hv)}**).")
    metin = ("🔍 **Nasıl buldum:** "
             + " → ".join(f"{i}️⃣ {a}" for i, a in enumerate(adimlar, 1))
             + "\n\n" + metin)
    return {"anlati": metin, "adimlar": adimlar, "segment": _seg, "boyut": boyut}


def toplam_ek(resp, prev_cq: dict, cube_meta: dict | None, *, service,
              limit: int = 1000) -> bool:
    """`§KN-toplam`'ın **iliştirme** yarısı — var olan cevabı ezmez, zenginleştirir.

    ⊙ Ölçüldü (tam kapı, `EE` demeti): `cevap_verisi`'ne konunca altı test kırmızı
    verdi; toplanabilir ölçülerde `contribution`/`prescribe` **yapısal bir gövde**
    (kartlar · chip'ler · ajan izi) üretiyor ve onu bir notla değiştirmek, daha iyi bir
    cümle için daha zengin bir cevabı feda etmekti.

    ⚠ `oneri=False`: reçete yolu zaten *«ne yapmalı»*yı söylüyor; ikinci bir öneri
    aynı şeyi iki kez söylemek olurdu.

    Döner: eklendi mi.
    """
    if getattr(resp, "note", None) and "§KN" in str(getattr(resp, "trace", "") or ""):
        return False
    try:
        out = toplam_turu(prev_cq, cube_meta, kos=kosucu(service, limit=limit),
                          oneri=False)
    except Exception:                    # noqa: BLE001 — cevap düşmez (ADR-0020)
        _log.warning("§KN-toplam ek: ayrıştırma hata verdi (best-effort)", exc_info=True)
        return False
    if not out:
        return False
    resp.note = "\n\n".join(x for x in [getattr(resp, "note", None), out["anlati"]] if x)
    resp.trace = [*(getattr(resp, "trace", None) or []),
                  *[f"§KN: {a}" for a in out["adimlar"]]]
    return True
