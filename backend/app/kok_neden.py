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

import math
import re
from dataclasses import dataclass, field

#: Bir bileşenin ölçüdeki **rolü**. Kapalı bir küme: kataloğun ifade dilinde bir
#: bileşen ya çarpandır, ya paydır, ya paydadır, ya da toplanan bir terimdir.
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


def _sadelestir(ifade: str) -> str:
    """İfadeyi **karşılaştırılabilir** hâle getirir: boşluklar ve dış parantezler düşer.

    ⚠ Bir SQL ayrıştırıcısı DEĞİL. Tek işi, kataloğun kendi ürettiği iki metnin aynı
    şeyi söyleyip söylemediğine bakmak. *Bir eşitliği aramak, bir dili çözümlemekten
    başka bir iştir.*
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


def ayristir(olcu: str, hedef: dict, akran: dict, cube_meta: dict | None) -> Ayristirma | None:
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
        h, a = hedef.get(b.ad), akran.get(b.ad)
        try:
            h, a = float(h), float(a)
        except (TypeError, ValueError):
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
    katkilar.sort(key=lambda k: k.katki)          # en çok düşüren başa
    _suclu = katkilar[0].bilesen if katkilar[0].katki < 0 else None
    try:
        _h, _a = float(hedef.get(olcu)), float(akran.get(olcu))
    except (TypeError, ValueError):
        _h = _a = 0.0
    return Ayristirma(olcu=olcu, hedef_deger=_h, akran_deger=_a,
                      katkilar=katkilar, sucllu=_suclu)


def _yuzde(x: float) -> str:
    return f"%{x:.1f}".replace(".", ",")


def anlati(ayr: Ayristirma, *, segment: str, boyut: str,
           olcu_display: str = "") -> str:
    """`§KN` — ayrıştırmanın **cümlesi**: nereye baktım, ne gördüm, bu yüzden.

    ⚠ Cümle **ölçülmüş sayılardan** kurulur; hiçbir yargı eklenmez. `lower_is_better`
    bilgisi çağıranda olduğu için burada *«kötü»* denmez — *«daha düşük»* denir. Bir
    değer yargısı, ölçünün yönü beyan edilmeden verilemez (`GG8`).
    """
    _ad = olcu_display or ayr.olcu.replace("_", " ")
    bas = (f"**{segment}** ({boyut}) {_ad} değeri **{ayr.hedef_deger:.3g}** — "
           f"akran ortalaması **{ayr.akran_deger:.3g}**.")
    if not ayr.katkilar:
        return bas
    satirlar = []
    for k in ayr.katkilar:
        yon = "düşürüyor" if k.katki < 0 else "yükseltiyor"
        rol = {PAYDA: " (paydada)", TERIM: " (terim)"}.get(k.bilesen.rol, "")
        satirlar.append(f"· **{k.bilesen.display}**{rol}: {k.hedef:.3g} ↔ akran "
                        f"{k.akran:.3g} — farkın {_yuzde(k.pay_yuzde)}'ini {yon}")
    kuyruk = ""
    if ayr.sucllu:
        kuyruk = (f"\n\n→ Farkın en büyük kaynağı **{ayr.sucllu.display}**. "
                  f"Bir sonraki adım: onu kendi kırılımlarında açmak.")
    return bas + "\n" + "\n".join(satirlar) + kuyruk
