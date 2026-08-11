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


#: 🔴 `§KN-ek` — **SAYIYA EK GETİRMEK BİR KELİME LİSTESİ DEĞİL, KAPALI BİR SINIFTIR.**
#:
#: ⊙ Ölçüldü (curl `CC` turu, CC-11): *«farkın **%2,2'ini** düşürüyor»* — doğrusu
#: *«%2,2'**sini**»*. Ek, sayının **okunuşundaki son sözcüğe** göre çekimlenir ve o
#: sözcük yalnız **son rakamdan** belirlenir: on olasılık, hepsi bu.
#:
#: Tablo tek bir olgudan türer — son rakamın sözcüğü (`sıfır bir iki üç dört beş altı
#: yedi sekiz dokuz`): (a) ünlüyle bitiyor mu (kaynaştırma `s` gerekir mi), (b) son
#: ünlüsünün dört-yönlü uyumdaki karşılığı. `dört`→`ö`⇒`ü`, `beş`→`e`⇒`i`.
#: İyelik = `[s]` + ünlü · belirtme = iyelik + `n` + ünlü.
#:
#: ⚠ `ADR-0008` ile uyumlu: bu bir **alan sözlüğü** değil, on elemanlı bir sayı
#: sınıfıdır ve **büyüyemez** — Türkçede on bir rakam yoktur.
#:
#: *Bir sayıyı yanlış çekimlemek, cevabın doğruluğunu değiştirmez; ama onu yazanın
#: dikkatini gösterir.*
_RAKAM_EKI = {"0": (False, "ı"), "1": (False, "i"), "2": (True, "i"),
              "3": (False, "ü"), "4": (False, "ü"), "5": (False, "i"),
              "6": (True, "ı"), "7": (True, "i"), "8": (False, "i"),
              "9": (False, "u")}


def _ek(metin: str, belirtme: bool = False) -> str:
    """`«%2,2»` → `«%2,2'sini»` (belirtme) · `«%84,1»` → `«%84,1'i»` (iyelik)."""
    _son = next((c for c in reversed(metin) if c.isdigit()), "0")
    _unlu_sonu, _u = _RAKAM_EKI[_son]
    _iyelik = ("s" if _unlu_sonu else "") + _u
    return f"{metin}'{_iyelik + 'n' + _u if belirtme else _iyelik}"


def _yuzde(x: float) -> str:
    return f"%{x:.1f}".replace(".", ",")


def _sayi(x: float) -> str:
    """İnsan için sayı: `3.17e+05` **bir sayı değil bir gösterimdir**.

    ⊙ Canlıda ölçüldü: *«ağırlık: 3.17e+05 ↔ akran 2.83e+05»* — teknik olarak doğru,
    okunabilir olarak **hiç**. Bir iş kullanıcısı bilimsel gösterimi zihninde çevirmek
    zorunda kalıyorsa, cevap ona ulaşmamıştır.
    """
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if abs(v) >= 1000:
        return f"{v:,.0f}".replace(",", ".")
    if abs(v) >= 1:
        return f"{v:,.2f}".replace(",", "~").replace(".", ",").replace("~", ".")
    return f"{v:.3f}".replace(".", ",")


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
    if not olculer or not boyutlar:
        return None
    olcu, boyut = olculer[0], boyutlar[0]
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
    _cq["measures"] = [olcu] + [b.ad for b in bl]
    _cq["dimensions"] = [boyut]
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
    _isaret = next((1 if k.katki > 0 else -1 for k in ayr.katkilar
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
    en_iyi = None
    for aday in adaylar:
        _satirlar = kos({**_temel, "measures": [suclu.ad], "dimensions": [aday]}) or []
        _uygun = [r for r in _satirlar if sayi(r.get(suclu.ad)) is not None]
        if len(_uygun) < 2:
            continue
        _degerler = [sayi(r[suclu.ad]) for r in _uygun]
        _yayilim = max(_degerler) - min(_degerler)
        if en_iyi is None or _yayilim > en_iyi[0]:
            en_iyi = (_yayilim, aday, _uygun)
    if en_iyi is None:
        return None
    _, d2, uygun = en_iyi
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
    out = arastir(prev_cq, cube_meta, kos=kosucu(service, limit=limit), segment=segment,
                  oneri=oneri)
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
    return (f"**«{_ad}» için bir kök-neden ayrıştırması üretemedim.** Bu ölçünün formülü "
            f"tek parça (bileşenlerine ayrılmıyor) ve elimdeki dönemde açıklanacak bir "
            f"**değişim** de yok — yani söyleyebileceğim bir *neden* yok."
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
