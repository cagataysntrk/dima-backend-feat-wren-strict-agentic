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
           olcu_display: str = "", derinlesildi: bool = False) -> str:
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


def _akran_ortalamasi(satirlar: list[dict], hedef_satir: dict, boyut: str,
                      alanlar: list[str]) -> dict:
    """Hedef DIŞINDAKİ satırların ortalaması — *«akran»* budur.

    ⚠ Ortalama, ağırlıksız: bir akranın *«tipik»* değeri sorulduğunda büyük segmentin
    küçüğü ezmesi istenmez. (Ağırlıklı taban ayrı bir sorunun cevabıdır ve o soru
    sorulmadı.)
    """
    ötekiler = [r for r in satirlar if r is not hedef_satir]
    out: dict = {}
    for a in alanlar:
        vals = [float(r[a]) for r in ötekiler
                if isinstance(r.get(a), (int, float)) and r.get(a) is not None]
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
    uygun = [r for r in satirlar if isinstance(r.get(olcu), (int, float))]
    if not uygun:
        return None
    if segment and boyut:
        for r in uygun:
            if str(r.get(boyut)) == str(segment):
                return r
    return max(uygun, key=lambda r: r[olcu]) if dusuk_iyi else min(uygun, key=lambda r: r[olcu])


def arastir(prev_cq: dict, cube_meta: dict | None, *, kos,
            segment: str | None = None, azami_derinlik: int = 1) -> dict | None:
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
        return None

    adimlar: list[str] = [f"formül okundu: **{olcu}** = "
                          + " × ".join(b.display for b in bl)]
    _cq = {k: v for k, v in prev_cq.items() if k not in ("order", "limit", "pencere")}
    _cq["measures"] = [olcu] + [b.ad for b in bl]
    _cq["dimensions"] = [boyut]
    satirlar = kos(_cq) or []
    if len(satirlar) < 2:
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
    ayr = ayristir(olcu, hedef_satir, akran, cube_meta)
    if ayr is None:
        return None
    _seg = str(hedef_satir.get(boyut))
    adimlar.append(f"**{_seg}** akran ortalamasıyla kıyaslandı → farkın kaynağı "
                   f"**{(ayr.sucllu or bl[0]).display}**")
    # 3 · DERİNLEŞME — suçlu bileşeni, hedef segmentin İÇİNDE başka bir kırılımda aç.
    derin = (derinles(prev_cq, cube_meta, ayr.sucllu, _seg, boyut, kos=kos)
             if (ayr.sucllu and azami_derinlik > 0) else None)
    metin = anlati(ayr, segment=_seg, boyut=boyut, derinlesildi=bool(derin),
                   olcu_display=str(((cube_meta or {}).get("measure_synonyms_display")
                                     or {}).get(olcu) or olcu).replace("_", " "))
    if derin:
        metin += "\n\n" + derin["metin"]
        adimlar.append(derin["adim"])
    return {"anlati": metin, "ayristirma": ayr, "adimlar": adimlar,
            "segment": _seg, "boyut": boyut}


def derinles(prev_cq: dict, cube_meta: dict | None, suclu: Bilesen,
             segment: str, boyut: str, *, kos) -> dict | None:
    """`§KN` — **en dibe in**: suçlu bileşeni, hedef segmentin içinde ikinci bir
    kırılımda aç ve en aykırı alt-segmenti bul.

    ⊙ Kullanıcının örneği birebir bu: *«en dibe indim ve gördüm ki vardiya 1'de …
    bu makine çok durmuş»*. Yani ikinci kırılım, birincinin **içindedir** — bir yan yana
    kıyas değil bir **iniş**.

    ⚠ İkinci boyutu `drill.available_dimensions` seçer (kullanılmış boyutları ve
    süzgeçtekileri eler) — ikinci bir sıralama kuralı yazmak `KAT-1` olurdu.
    """
    from app.drill import available_dimensions

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
        _uygun = [r for r in _satirlar if isinstance(r.get(suclu.ad), (int, float))]
        if len(_uygun) < 2:
            continue
        _degerler = [float(r[suclu.ad]) for r in _uygun]
        _yayilim = max(_degerler) - min(_degerler)
        if en_iyi is None or _yayilim > en_iyi[0]:
            en_iyi = (_yayilim, aday, _uygun)
    if en_iyi is None:
        return None
    _, d2, uygun = en_iyi
    # Suçlu bileşen **düşürüyor**sa en düşük alt-segment; yükseltiyorsa en yüksek.
    en = min(uygun, key=lambda r: r[suclu.ad]) if suclu.yon > 0 else \
        max(uygun, key=lambda r: r[suclu.ad])
    otekiler = [float(r[suclu.ad]) for r in uygun if r is not en]
    ort = sum(otekiler) / len(otekiler) if otekiler else float(en[suclu.ad])
    _lbl = ((cube_meta or {}).get("dimension_labels") or {}).get(d2, d2)
    return {
        "metin": (f"→ **{segment}** içinde {suclu.display} en çok **{en.get(d2)}** "
                  f"({_lbl}) tarafında ayrışıyor: **{float(en[suclu.ad]):.3g}** ↔ "
                  f"öteki {_lbl} ortalaması **{ort:.3g}**."),
        "adim": f"**{segment}** içinde **{_lbl}** kırılımı açıldı → **{en.get(d2)}**",
        "boyut": d2, "segment": str(en.get(d2)),
    }
