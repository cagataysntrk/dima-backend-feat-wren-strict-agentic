"""Katkı ayrıştırması (Faz 5.2) — *"neden değişti?"* sorusunun CubeQuery üzerinde ifadesi.

Rakiplerin hepsinde bir karşılığı var (Snowflake `TOP_INSIGHTS`, Power BI Key Influencers,
Tableau Pulse) ve hepsi semantic layer'ın **dışında** duruyor: ürettikleri şey bir metin ya
da bir görsel: yeniden tarihlenemez, kırılamaz, sözleşme taşımaz. Buradaki fark tam olarak
budur — **her bulgu kendi başına bir CubeQuery'dir**: tıklanır, yeniden çalışır, Query
Contract üretir, üstüne yeni kırılım eklenebilir. Skor bir "içgörü" değil, doğrulanabilir
bir sorgunun etiketi.

Yöntem MacroBase `DIFF` / Adtributor kalıbının en yalın hali ve **cebirseldir** — ML yok,
eğitim yok, rastgelelik yok (`interpret.py`'nin deterministik felsefesi). İki dönem
arasındaki değişim, kullanılmayan bir boyutun değerlerine dağıtılır.

## Neden `_ayristirilabilir_mi` bu modülün en önemli fonksiyonu

Katkı ayrıştırması **yalnız TOPLANABİLİR ölçülerde tanımlıdır**. `SUM(ciro)` için
segmentlerin değişimleri toplamı, toplamın değişimine EŞİTTİR. `AVG(...)`, oran
(`.../...*100`) ya da `COUNT(DISTINCT ...)` için EŞİT DEĞİLDİR: parçalar toplamı tutmaz ve
"bu segment değişimin %40'ını açıklıyor" cümlesi **matematiksel olarak yanlış** olur.

Bu, bu araç sınıfının klasik sessiz hatasıdır — sayı makul görünür, kimse toplamı kontrol
etmez. Burada ayrıştırma o ölçüler için **yapılmaz ve nedeni söylenir**; ADR-0008'in
("anlamadığını bil") ölçü-matematiği tarafındaki karşılığıdır.

## Neden iki ayrı pay

Segmentler birbirini götürebilir: biri +100, öteki −100 → net değişim 0 ama ortada
anlatılacak bir hikâye VAR. Tek bir "net payı" gösteren araç bu durumda ya sıfıra bölme
yapar ya da hiçbir şey göstermez. Bu yüzden her segment iki pay taşır:
  `net_pay`  — değişimin işaretli toplamına oranı (net ~0 ise **None**, uydurulmaz).
  `brut_pay` — mutlak hareketlerin toplamına oranı (her zaman tanımlı; götürme olsa da
               "en çok kim kıpırdadı" sorusunu cevaplar).
"""

from __future__ import annotations

# 🔴 `§SB-metin` — **MODÜL DÜZEYİNDE, ve bunu bir kapı öğretti.** İlk yazımda bu import
# iki ayrı fonksiyonun İÇİNDEYDİ ve `_b3 = _ssayi` üçüncü bir fonksiyondaydı:
# `F821 Undefined name` — yani o satır koştuğu an bir **`NameError`**. Süit yakaladı
# (`test_COZULMEYEN_ISIM_YOK`), canlı curl **yakalamadı**, çünkü o dal ancak belli bir
# akran kıyasında koşuyor.
# *Bir ismi kullandığın yerde değil, çözüldüğü yerde tanımlamak gerekir.*
from app.sayi_bicimi import ek as _sek, sayi as _ssayi, yuzde as _syuzde

from typing import Any

from app.logging_setup import get_logger

_log = get_logger("contribution")

# Bir segmentin "gürültü" sayılacağı eşik: brüt harekete katkısı bunun altındaysa listeye
# girmez. Amaç UI'ı 200 satırlık bir kuyrukla doldurmamak; kesilen miktar RAPORLANIR
# (bkz. `decompose` → `kirpilan`), çünkü sessiz kırpma "her şey kapsandı" gibi okunur.
_GURULTU_PAYI = 1.0  # %

# Taranacak en fazla boyut. Kombinatorik patlama gerçek: her boyut AYRI bir kıyas sorgusu
# (cari + geçen dönem) demek. Sınır konur ama KONAN SINIR LOGLANIR.
MAX_BOYUT = 6


def _sayi(v: Any) -> float:
    """Sayısal test `app/result_shape.py`'den (Faz C2); sayı değilse katkı 0'dır."""
    from app.result_shape import is_num

    return float(v) if is_num(v) and not isinstance(v, str) else (
        float(str(v).replace(".", "").replace(",", ".")) if is_num(v) else 0.0)



#: Toplanabilirlik sınıfları. 🔴 Bu bir **SAYILAN KÜME değil**, OLAP literatürünün
#: kapalı cebirsel taksonomisidir (additive / semi-additive / non-additive) — kullanıcıya
#: dönük bir anlam ekseni değil, ölçünün **matematiksel davranışı**. `KAT-5` anlam
#: eksenlerinin literal listelenmesini yasaklar; bu onlardan biri değildir.
TAM, YARI, YOK, BILINMIYOR = "tam", "yari", "yok", "bilinmiyor"


def toplanabilirlik(measure: str, cube_meta: dict | None) -> tuple[str, str]:
    """(sınıf, gerekçe) — ölçü **hangi eksende** toplanabilir. **TEK OKUYUCU.**

    Cube metadata'sının `non_additive` / `semi_additive` / `measure_expressions`
    alanlarını yorumlayan tek yer burasıdır. Üç ayrı tüketici bu sınıftan **kendi
    politikasını** çıkarır — çünkü üçü **ayrı soru** sorar:

    | Tüketici | Sorusu | Kabul ettiği sınıf |
    |---|---|---|
    | `ayristirilabilir_mi` (katkı payı) | *"Δ segmentlere dağıtılabilir mi?"* | yalnız `TAM` |
    | `viz._additive` (yığma/pay grafiği) | *"ZAMAN ekseninde yığılabilir mi?"* | yalnız `TAM` |
    | `interpret` (dönem trendi) | *"ZAMAN-DIŞI eksende toplanabilir mi?"* | `TAM` + **`YARI`** |

    🔴 **Bu ayrım bir denetim bulgusundan doğdu.** `interpret` bir süre
    `ayristirilabilir_mi`'yi çağırdı ve **yarı-toplanabilir yedi ölçünün** trendini
    (`bakiye` · `acik_bakiye` · `acik_borc` · `net_bakiye` · `net_miktar` · `stok_deger` ·
    `vadesi_gecen`) **haksız yere** susturdu — üstelik gerekçe olarak katkı-ayrıştırmasına
    ait bir cümle bastı. Bir stok ölçüsü **müşteriler arasında pekâlâ toplanır**;
    toplanamadığı eksen **zamandır**. *"Aynı kuralın iki sahibi"*nin kardeşi:
    **aynı sahibe iki farklı soru sordurmak.**

    `BILINMIYOR`: metadata sessiz **ve** ad kalıbı da bir şey söylemiyor. Bu bir sınıf
    değil, bir **bilgi eksikliğidir** — politikayı çağıran belirler (trend tarafı
    **fail-closed**: yanlış bir trend, hiç trend olmamasından kötüdür).
    """
    meta = cube_meta or {}
    if not measure:
        return YOK, "ölçü belirtilmemiş"
    # ⚠ GEREKÇELER DÜZ METİNDİR: `interpret` bunları `summary`'ye koyuyor ve
    # `OutputInsight` onu düz metin basıyor — canlı kullanıcı ekranda backtick/yıldız
    # karakterlerini **harfi harfine** gördü. Biçimlendirme, metnin gideceği yeri bilmeyen
    # bir katmanda üretilmez.
    if measure in (meta.get("non_additive") or []):
        return YOK, (f"{measure} toplanabilir değil (cube metadata'sında non_additive)")
    if measure in (meta.get("semi_additive") or []):
        return YARI, (f"{measure} yarı-toplanabilir bir stok/bakiye ölçüsü — zaman-dışı "
                      "eksende toplanır, zaman ekseninde toplanmaz")
    ifade = ((meta.get("measure_expressions") or {}).get(measure) or "").upper()
    if ifade:
        if "AVG(" in ifade or "COUNT(DISTINCT" in ifade or "/" in ifade:
            return YOK, (f"{measure} bir ortalama/oran — parçaların toplamı bütünü vermez")
        if "MIN(" in ifade or "MAX(" in ifade:
            # Denetimde bulundu: eski sürüm MIN/MAX'ı hiç kontrol etmiyordu; eklenecek
            # ilk `MAX(...)` ölçüsü SESSİZCE toplanırdı.
            return YOK, (f"{measure} bir uç-değer ölçüsü (MIN/MAX) — parçaların toplamı "
                         "bütünü vermez")
        return TAM, ""
    ad = measure.lower()
    if ad.startswith("ort_") or ad.endswith(("_yuzde", "_orani", "_pct")):
        return YOK, (f"{measure} bir ortalama/oran gibi görünüyor — parçaların toplamı "
                     "bütünü vermez")
    return BILINMIYOR, (f"{measure} için toplanabilirlik beyanı YOK (cube metadata'sı "
                        "ifadeyi yayımlamıyor) — sınıf bilinmiyor")


def ayristirilabilir_mi(measure: str, cube_meta: dict | None) -> tuple[bool, str | None]:
    """(ayrıştırılabilir?, ayrıştırılamıyorsa NEDENİ).

    Sınıflandırma `toplanabilirlik()`'te (tek okuyucu); burada yalnız **politika** var:
    katkı payı **yalnız `TAM`** sınıfında tanımlıdır. Yarı-toplanabilir bir stok ölçüsünün
    dönem-içi değişimini segmentlere dağıtmak anlamlı değildir.

    ✅ **BORÇ KAPANDI (2026-08-11) — ve kapatan şey bir ÖLÇÜMDÜ.** Bu fonksiyon
    `BILINMIYOR` sınıfında **fail-OPEN**ti; docstring *«emin olunamayan durumda
    ayrıştırma yapılmaz»* diyor, kod ayrıştırıyordu. Yorumun kendi şartı *«davranış
    değişikliği kendi ölçümünü ister»*di — o ölçüm yapıldı:

        canlı katalog (demo-boyahane) → TAM 74 · YOK 60 · YARI 2 · **BİLİNMİYOR 0**

    ⊙ Yani fail-open dalı **pratikte hiç ulaşılmıyordu**: maruziyet **sıfır**. Kapatmanın
    kapsam maliyeti de sıfırdır, ve kapatmamanın bedeli bir gün **beyansız bir pack**
    geldiğinde sessizce yayımlanan bir katkı yüzdesidir.

    ⚠ Ve ölçüm kolay yanıltıyordu: ilk probum `measure_expressions`'ı **geçmedi** ve
    77 ölçü *«BİLİNMİYOR»* göründü. `toplanabilirlik` sınıfı oradan okur — küpün
    **kendisi** meta olarak verilmelidir. *Bir okuyucuya eksik bir sözlük vermek, onu
    yanlış bir cevaba değil, uydurulmuş bir soruna götürür.*

    ⊙ Trend tarafı (`interpret`) aynı sınıfta **zaten** fail-closed'dı; artık iki taraf
    da aynı şeyi söylüyor.
    """
    sinif, gerekce = toplanabilirlik(measure, cube_meta)
    if sinif == TAM:
        return True, None
    if sinif == YARI:
        return False, (f"`{measure}` yarı-toplanabilir bir stok/bakiye ölçüsü — dönem içi "
                       "değişimi segmentlere dağıtmak anlamlı değil")
    if sinif == YOK:
        return False, (gerekce + " — katkı payı matematiksel olarak tanımsız olur")
    # ✅ `BILINMIYOR` → **FAIL-CLOSED** (2026-08-11). Ölçüm: canlı katalogda bu sınıf
    # **sıfır** ölçüde geçiyor (TAM 74 · YOK 60 · YARI 2), yani kapsam maliyeti yok.
    # Beyansız bir ölçüde katkı yüzdesi yayımlamak, doğruluğu bilinmeyen bir sayıyı
    # **doğrulanmış gibi** sunmaktır — ve bu deponun en pahalı hata sınıfıdır.
    # Gerekçe ve ölçüm docstring'de.
    return False, (f"`{measure}` için toplanabilirlik beyanı YOK — katkı payı ancak "
                   "ölçünün segmentler arasında toplanabildiği **beyan edilmişse** "
                   "hesaplanabilir (cube metadata'sına `measure_expressions` ya da "
                   "`non_additive`/`semi_additive` yazılmalı)")


def contributions(rows: list[dict], dim: str, measure: str) -> list[dict]:
    """Kıyas satırlarından (`yoy.compute` çıktısı) segment katkıları.

    Beklenen kolonlar: `<measure>` (cari) ve `<measure>_gecen` (önceki dönem) — `app/yoy.py`
    bu adlarla üretiyor, burada yeniden hesaplanmıyor.
    """
    kalemler: list[dict] = []
    for r in rows or []:
        simdi = _sayi(r.get(measure))
        onceki = _sayi(r.get(f"{measure}_gecen"))
        kalemler.append({"deger": r.get(dim), "simdi": simdi, "onceki": onceki,
                         "delta": simdi - onceki})
    net = sum(k["delta"] for k in kalemler)
    brut = sum(abs(k["delta"]) for k in kalemler)
    for k in kalemler:
        # Net pay ancak net değişim BRÜT hareketin anlamlı bir kısmıysa yorumlanabilir.
        # Aksi halde (+100/−100 götürmesi) pay yüzdeleri patlar ve saçmalar.
        k["net_pay"] = (round(k["delta"] / net * 100, 1)
                        if net and abs(net) > brut * 0.01 else None)
        k["brut_pay"] = round(abs(k["delta"]) / brut * 100, 1) if brut else None
    _surprizi_isle(kalemler)
    return sorted(kalemler, key=lambda k: abs(k["delta"]), reverse=True)


def _surprizi_isle(kalemler: list[dict]) -> None:
    """🔴🔴 `§E2` — **SÜRPRİZ: SEGMENTİN PAYI DEĞİŞTİ Mİ?** (Jensen-Shannon)

    ## Ölçülen kusur — ve raporun kurucu örneği kendi kodumuzda üredi

    Adtributor'ın (NSDI'14) kurucu örneği bu modüle verildi (2026-08-11):

        toplam 100 → 50 ·  X: 94→47 · Mobile: 5→1 · Tablet: 1→2
        bizim çıktımız →  **X — «net değişimin %94,0'ı»**  (1. sırada)

    Ama **X'in payı hiç değişmedi**: `94/100 = %94` → `47/50 = %94`. X bir sebep değil,
    **işin kendisidir**. Gerçek sinyal `Mobile` (%5→%2) ve `Tablet` (%1→%4) — yani
    **dağılımı değişenler**.

    > *«Yalnız explanatory power kullanan her katkı analizi, büyük segmentleri
    > **sistematik olarak** suçlar.»* — `§10.2`

    ⊙ Bu, kullanıcının *«en büyük müşteri hep suçlu çıkıyor»* şikâyetinin matematiksel
    adıdır (`§12.7`).

    ## Ne HESAPLANIR

    Her segment için **pay** (share) iki dönemde: `p = önceki/Σönceki`,
    `q = şimdi/Σşimdi`. Sürpriz, o segmentin **Jensen-Shannon diverjansına katkısıdır**:

        js_i = ½·[ p·log₂(p/m) + q·log₂(q/m) ],   m = (p+q)/2

    ⚠ **Forecast GEREKMİYOR.** Adtributor `F` (beklenen) ister; bizim `F`'imiz **önceki
    dönemin kendisidir** ve `yoy.compute` onu `*_gecen` kolonunda **zaten** veriyor.
    Bir tahmin motoru eklemek, elimizdeki ölçülmüş taban dururken **uydurulmuş** bir
    taban kurmak olurdu.

    ## 🔴 SIRALAMA DEĞİŞTİRİLMEZ — ve bu bilinçli

    `E2`'nin kendi risk satırı: *«bugünkü cevapları değiştirir — ölçüm gerekir, tahmin
    değil»*. Bu yüzden burada sıra **aynen** `|delta|`'da kalır; eklenen şey bir
    **ölçü** ve onun **beyanıdır** (`surpriz_notu`). Sessizce yeniden sıralamak, her
    mevcut cevabı ölçülmemiş biçimde oynatırdı.

    ⚠ Negatif değerli segmentlerde pay tanımsızdır (`Σ<0` ya da karışık işaret) →
    sürpriz **hesaplanmaz** (`None`). Susmak, anlamsız bir yüzdeden iyidir.
    """
    import math

    t0 = sum(k["onceki"] for k in kalemler)
    t1 = sum(k["simdi"] for k in kalemler)
    # Paylar ancak aynı işaretli ve sıfırdan farklı toplamlarda anlamlıdır.
    if t0 <= 0 or t1 <= 0 or any(k["onceki"] < 0 or k["simdi"] < 0 for k in kalemler):
        for k in kalemler:
            k["pay_onceki"] = k["pay_simdi"] = k["surpriz"] = None
        return
    for k in kalemler:
        p, q = k["onceki"] / t0, k["simdi"] / t1
        m = (p + q) / 2
        js = 0.0
        if p > 0 and m > 0:
            js += 0.5 * p * math.log2(p / m)
        if q > 0 and m > 0:
            js += 0.5 * q * math.log2(q / m)
        k["pay_onceki"] = round(p * 100, 1)
        k["pay_simdi"] = round(q * 100, 1)
        k["surpriz"] = round(js, 6)
    toplam_js = sum(k["surpriz"] for k in kalemler) or 0.0
    for k in kalemler:
        # Sürpriz PAYI: bu segment, dağılım değişiminin yüzde kaçını taşıyor?
        k["surpriz_pay"] = (round(k["surpriz"] / toplam_js * 100, 1)
                            if toplam_js > 0 else None)


#: Bir segmentin payı bu kadar oynamadıysa *«dağılımı değişmedi»* sayılır (yüzde puan).
#: ⚠ Eşik bir **görünürlük** ölçütüdür, bir red değil: altında kalan bir segment yine
#: raporlanır, yalnız *«payı değişmedi»* diye **beyan edilir**.
SURPRIZ_ESIGI_PUAN = 1.0


def surpriz_notu(bulgular: list[dict]) -> str:
    """🔴 `§E2` — EN BÜYÜK KALEMİN PAYI DEĞİŞMEDİYSE **SÖYLENİR**.

    Adtributor'ın kurucu örneğinde doğru cevap *«X'i suçlama»* değil, *«X en büyük
    düşüşü taşıyor **ama payı değişmedi**; dağılımı değişen segment şu»*dur. Kullanıcı
    ikisini birden görünce kendi kararını verebilir — bizim onun yerine karar vermemize
    gerek kalmaz.

    Döner: beyan cümlesi ya da `""`.
    """
    if not bulgular:
        return ""
    bas = bulgular[0]
    if bas.get("pay_onceki") is None or bas.get("surpriz") is None:
        return ""                                  # pay tanımsız → susulur
    oynama = abs(bas["pay_simdi"] - bas["pay_onceki"])
    if oynama >= SURPRIZ_ESIGI_PUAN:
        return ""                                  # zaten dağılımı değişmiş → sürpriz yok
    # Dağılımı EN ÇOK değişen aday (kendisi değilse)
    aday = max((b for b in bulgular if b is not bas and b.get("surpriz") is not None),
               key=lambda b: b["surpriz"], default=None)
    _s = (f"«{bas['deger']}» en büyük hareketi taşıyor ama **payı değişmedi** "
          f"(%{bas['pay_onceki']:g} → %{bas['pay_simdi']:g}) — yani bu bir **sebep "
          f"değil, ölçeğin kendisi**.")
    if aday is not None and abs(aday["pay_simdi"] - aday["pay_onceki"]) >= SURPRIZ_ESIGI_PUAN:
        _s += (f" 🔴 Dağılımı en çok değişen: «{aday['deger']}» "
               f"(%{aday['pay_onceki']:g} → %{aday['pay_simdi']:g}).")
    return _s


def decompose(rows: list[dict], dim: str, measure: str, cube_query: dict,
              *, dim_label: str | None = None, unit: str | None = None) -> dict:
    """Tek bir boyut için katkı raporu + her segment için TIKLANABİLİR CubeQuery.

    Dönen `bulgular[i]["cube_query"]` o segmentin kendi sorgusudur — `/cube` ile LLM'siz
    koşar, Query Contract üretir, üstüne kırılım eklenebilir. Modülün varlık sebebi budur:
    skor bir metin değil, doğrulanabilir bir sorgunun etiketi.
    """
    from app.drill import select_cube_query

    hepsi = contributions(rows, dim, measure)
    brut = sum(abs(k["delta"]) for k in hepsi)
    tutulan = [k for k in hepsi
               if brut and abs(k["delta"]) / brut * 100 >= _GURULTU_PAYI]
    kirpilan = len(hepsi) - len(tutulan)
    etiket = dim_label or dim
    bulgular = []
    for k in tutulan:
        # 🔴🔴 `§SB-metin` — **SAYININ TÜRKÇESİ TEK SAHİPTEN.**
        #
        # ⊙ Ölçüldü (curl `DD` turu, DD-13): burası *«47,836 dk azaldı (net değişimin
        # %83.4'i)»* yazıyordu — **üç** hata: binlik ayırıcı İngilizce (`{:,.0f}`),
        # ondalık ayırıcı İngilizce, ek sabit (`'i`; doğrusu `'ü`). Aynı üründe `§KN`
        # *«farkın %56,1'ini»* diye **doğru** yazıyordu.
        #
        # ⚠ Ve niyet zaten doğruydu: `context.py:362` beklenen çıktıyı *«46.524 dk
        # AZALDI (net değişimin %83,6'sı)»* diye yazmış. Yani kusur bir karar eksikliği
        # değil, kararın **ikinci bir yerde yeniden uygulanmasıydı** (`KAT-1`).
        #
        # *İki yerde biçimlendirilen bir sayı, er ya da geç iki farklı sayı gibi okunur.*

        yon = "arttı" if k["delta"] > 0 else "azaldı"
        # ⚠ Takma adlar `_sek/_ssayi/_syuzde` — **`_sayi` bu modülde ZATEN VAR** ve o bir
        # *ayrıştırıcıdır* (`str→float`), bir biçimlendirici değil. İlk yazımda yerel bir
        # import onu fonksiyon içinde **gölgeliyordu**; import modül düzeyine çıkınca
        # `_sayi(abs(delta))` sessizce **ham float** basacaktı.
        # *Aynı adı iki farklı işe vermek, birini er ya da geç öteki sanmaktır.*
        pay = (f" (net değişimin {_sek(_syuzde(k['net_pay']))})" if k["net_pay"] is not None
               else f" (hareketin {_sek(_syuzde(k['brut_pay']))})")
        bulgular.append({
            **k,
            "label": f"{etiket}: {k['deger']} — {_ssayi(abs(k['delta']))}"
                     f"{' ' + unit if unit else ''} {yon}{pay}",
            "kind": "dimension",
            "cube_query": select_cube_query(cube_query, dim, k["deger"]),
        })
    return {
        # 🔴 `§E2` — sürpriz beyanı raporun **kendi alanında**: tüketici onu nota
        # ekler ya da eklemez, ama artık **görebilir**. Sıralama değişmedi.
        "surpriz_notu": surpriz_notu(bulgular),
        "dimension": dim, "dimension_label": etiket,
        "net_degisim": sum(k["delta"] for k in hepsi),
        "brut_hareket": brut,
        "bulgular": bulgular,
        # Sessiz kesme YOK (MIMARI.md): kırpılan segment sayısı ve payı açıkça raporlanır,
        # yoksa liste "her şey bu kadar" diye okunur.
        "kirpilan_segment": kirpilan,
        "kirpilan_esik_yuzde": _GURULTU_PAYI,
    }


# --- PVM: fiyat / miktar / birleşik (Faz 5.1) ------------------------------------
#
# `V = p · q` olan her ölçü çifti için değişim ARTIKSIZ üç parçaya ayrılır:
#
#     ΔV  =  (p₁−p₀)·q₀   +   p₀·(q₁−q₀)   +   (p₁−p₀)·(q₁−q₀)
#            └ fiyat ┘        └ miktar ┘        └ birleşik ┘
#
# Toplam **birebir** ΔV'dir (yuvarlama dışında artık YOKTUR) — bu, yöntemin cebirsel
# olmasının ve bir tahmin taşımamasının kanıtıdır ve `test_pvm_ARTIKSIZ` onu ölçer.
#
# Segment başına hesaplanır: her segment kendi fiyat/miktar etkisini taşır ve kendi
# CubeQuery'siyle döner (Faz 5.2 ile aynı ilke — skor değil, tıklanabilir sorgu).
#
# **Eşleştirme TAHMİN EDİLMEZ, BEYAN EDİLİR.** `toplam_ciro / toplam_agirlik_kg` gerçek bir
# TL/kg fiyatıdır; `toplam_tutar / fatura_sayisi` ise fiyat DEĞİL ortalama fatura
# büyüklüğüdür. Bu ayrım bir İÇERİK bilgisidir; ad kalıbından çıkarmak MIMARI.md §5'in
# yasakladığı kelimeye-özel yamadır ve yanlış eşleştirme GÜVENLE YANLIŞ ekonomi üretir
# (kullanıcı "birim fiyat %12 arttı" cümlesini sorgulamaz). Bu yüzden cube metadata'sında
# açık `pvm:` bloğu aranır; yoksa PVM sunulmaz.


def pvm_pairs(cube_meta: dict | None) -> list[dict]:
    """Cube'un BEYAN ETTİĞİ (value, volume, price_label) üçlüleri. Beyan yoksa boş liste.

    `price_label` İKİ yazımla da okunur: `build_json` MDL'e yazarken bilinmeyen anahtarları
    camelCase'e çeviriyor (`always_filter` → `alwaysFilter` ile aynı davranış), dolayısıyla
    YAML'daki `price_label` manifestte `priceLabel` olarak duruyor. Yalnız birini okumak,
    etiketin sessizce varsayılana düşmesi demekti.
    """
    out = []
    for p in ((cube_meta or {}).get("pvm") or []):
        if isinstance(p, dict) and p.get("value") and p.get("volume"):
            out.append({"value": p["value"], "volume": p["volume"],
                        "price_label": (p.get("price_label") or p.get("priceLabel")
                                        or "birim fiyat")})
    return out


def pvm(rows: list[dict], dim: str, value_measure: str, volume_measure: str) -> list[dict]:
    """Segment başına fiyat/miktar/birleşik etki (`yoy.compute` çıktısından).

    Miktarı sıfır olan bir segmentte fiyat TANIMSIZDIR (0'a bölme). O segment atlanmaz —
    tüm değişimi MİKTAR etkisi sayılır, çünkü ortada gerçekten bir hacim hareketi vardır
    (yeni ürün girmiş / tamamen durmuş) ve onu "fiyat" diye adlandırmak yanlış olurdu.
    """
    out = []
    for r in rows or []:
        v1, v0 = _sayi(r.get(value_measure)), _sayi(r.get(f"{value_measure}_gecen"))
        q1, q0 = _sayi(r.get(volume_measure)), _sayi(r.get(f"{volume_measure}_gecen"))
        if q0 and q1:
            p0, p1 = v0 / q0, v1 / q1
            fiyat = (p1 - p0) * q0
            miktar = p0 * (q1 - q0)
            birlesik = (p1 - p0) * (q1 - q0)
        else:
            # Bir tarafta hacim yoksa fiyat karşılaştırması kurulamaz — hepsi miktar.
            p0 = v0 / q0 if q0 else None
            p1 = v1 / q1 if q1 else None
            fiyat = birlesik = 0.0
            miktar = v1 - v0
        out.append({"deger": r.get(dim), "deger_simdi": v1, "deger_onceki": v0,
                    "miktar_simdi": q1, "miktar_onceki": q0,
                    "fiyat_simdi": p1, "fiyat_onceki": p0,
                    "fiyat_etkisi": fiyat, "miktar_etkisi": miktar,
                    "birlesik_etki": birlesik, "delta": v1 - v0})
    return sorted(out, key=lambda k: abs(k["delta"]), reverse=True)


def pvm_report(rows: list[dict], dim: str, pair: dict, cube_query: dict,
               *, dim_label: str | None = None, unit: str | None = None) -> dict:
    """PVM raporu + her segment için tıklanabilir CubeQuery."""
    from app.drill import select_cube_query

    kalemler = pvm(rows, dim, pair["value"], pair["volume"])
    brut = sum(abs(k["delta"]) for k in kalemler)
    etiket = dim_label or dim
    bulgular = []
    kirpilan = 0
    for k in kalemler:
        if brut and abs(k["delta"]) / brut * 100 < _GURULTU_PAYI:
            kirpilan += 1
            continue
        baskin = max(("fiyat", abs(k["fiyat_etkisi"])), ("miktar", abs(k["miktar_etkisi"])),
                     key=lambda t: t[1])[0]
        bulgular.append({
            **k, "baskin_etken": baskin, "kind": "dimension",
            "label": (f"{etiket}: {k['deger']} — {k['delta']:+,.0f}"
                      f"{' ' + unit if unit else ''} "
                      f"(fiyat {k['fiyat_etkisi']:+,.0f} · miktar {k['miktar_etkisi']:+,.0f})"),
            "cube_query": select_cube_query(cube_query, dim, k["deger"]),
        })
    return {
        "dimension": dim, "dimension_label": etiket,
        "value_measure": pair["value"], "volume_measure": pair["volume"],
        "price_label": pair["price_label"],
        "net_degisim": sum(k["delta"] for k in kalemler),
        "fiyat_etkisi": sum(k["fiyat_etkisi"] for k in kalemler),
        "miktar_etkisi": sum(k["miktar_etkisi"] for k in kalemler),
        "birlesik_etki": sum(k["birlesik_etki"] for k in kalemler),
        "bulgular": bulgular,
        "kirpilan_segment": kirpilan,
        "kirpilan_esik_yuzde": _GURULTU_PAYI,
    }


def rank_dimensions(raporlar: list[dict]) -> list[dict]:
    """Boyutları AÇIKLAYICILIĞA göre sırala: en büyük tek segment payı yüksek olan önce.

    Sezgi: değişimin %70'i tek bir makineden geliyorsa `makine` boyutu, değişimi 12 eşit
    parçaya bölen `hafta_gunu`ndan daha AÇIKLAYICIDIR. Adtributor'ın "surprise" ölçüsünün
    en yalın, açıklanabilir hali — entropi yerine tek bir okunabilir sayı, çünkü kullanıcıya
    gösterilecek gerekçe de bu sayıdır.
    """
    def _skor(r: dict) -> float:
        bulgular = r.get("bulgular") or []
        if not bulgular:
            return 0.0
        # Segment raporunda `brut_pay` hazır; PVM raporunda yok (orada bulgular fiyat/miktar
        # ayrışması taşır) — o durumda aynı büyüklük |delta| paylarından hesaplanır. Tek bir
        # sıralama kuralı iki rapor türüne de uygulanır ki "hangi boyut daha açıklayıcı"
        # sorusunun cevabı ayrışmasın.
        if bulgular[0].get("brut_pay") is not None:
            return max(abs(b.get("brut_pay") or 0) for b in bulgular)
        brut = sum(abs(b.get("delta") or 0) for b in bulgular)
        return (max(abs(b.get("delta") or 0) for b in bulgular) / brut * 100) if brut else 0.0

    return sorted(raporlar, key=_skor, reverse=True)


# --- ORKESTRASYON: boyut taraması (Faz F3) ---------------------------------------
#
# `arastir()` bu modülün ilk BİLEŞİK fonksiyonudur: yukarıdakiler saf matematik, bu ise
# boyut seçer, dönemsel kıyas koşar, ayrıştırır ve sıralar. Neden burada:
#
# Faz 5.2'de bu gövde `/ask/contribution`'ın router fonksiyonuna yazılmıştı ve HTTP'ye
# yapışıktı (`request`, `_service_for`, `_drill_record_contract`). Sonucu ölçüldü:
#   * `ask.py` içindeki konuşma katmanı onu ancak router'ı ÇAĞIRARAK kullanabildi ve
#     planlayıcıya `dis_adim(..., gated: false)` diye İTİRAF olarak girdi — kayıtlı bir
#     araç değildi, dört kapıdan (kayıt · yetki · deterministik-önce · bütçe) geçmiyordu.
#   * Zamanlanmış uyarılar (arka plan işi, `request` YOK) onu HİÇ kullanamadı — bu yüzden
#     uyarı bugün NE olduğunu söylüyor, NEDEN olduğunu söylemiyor.
#
# HTTP'den ayrılınca ikisi de düzelir: aynı gövde `tools.KAYIT`'a girer ve arka plan işi
# de çağırabilir. Kural (MIMARI §5): aynı kural iki yerde yaşamasın.


def _sayi_ya_da_yok(v):
    """Satır değerini sayıya çevirir; çevrilemiyorsa **`None`** (uydurma yok).

    🔴 **`_sayi` DEĞİL — ve bu ayrım bir kapı yakalamasıyla öğrenildi.** İlk yazımda bu
    fonksiyonu `_sayi` diye tanımladım; modülde **zaten bir `_sayi` vardı** (`:53`) ve
    sözleşmesi **tam tersiydi**: eksik değeri `0.0` sayar (*"eksik geçen dönem SIFIR
    sayılır"*, kendi kapısı var). Python son tanımı kazandırdı ve katkı ayrıştırması
    `float - None` ile **patladı**.
    ⊙ `KAT-1`'in en sinsi biçimi: aynı kuralın iki sahibi değil, **aynı adın iki
    sözleşmesi**. Ve fark bir yazım değil bir **politikadır**: biri eksiği sıfır sayar,
    öteki eksiği **reddeder**. İkisi de doğru — ama farklı sorular için.
    *Bir ada sahip çıkmadan bir sözleşme yazılmaz.*
    """
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _akran_kiyasi(service, cq: dict, cube_meta: dict, measure: str,
                  satir_donustur=None) -> dict | None:
    """`§AA1` — hedefi AKRANLARIYLA kıyaslar ve farkı en çok açıklayan ölçüyü bulur.

    İki deterministik sorgu, **sıfır LLM**:
      1. `measure × boyut` → hedefin değeri ↔ ötekilerin ortalaması (fark, %)
      2. aynı boyutta küpün **öteki** ölçüleri → hedefin akran ortalamasından **oransal
         sapması**; en büyük sapmalar *"sürükleyen"* olarak sıralanır.

    ⚠ Oransal sapma bilerek: ölçüler farklı birimlerdedir (`dk` · `%` · `kg`) ve mutlak
    fark onları kıyaslanamaz kılar. Payda **akran ortalamasıdır**, sıfırsa o ölçü **elenir**
    (bölme uydurulmaz).
    ⚠ Yön `lower_is_better` beyanından okunur (`§W-C` ile aynı kaynak): duruşun **fazla**
    olması kötüdür, OEE'nin fazla olması iyidir. Yönsüz bir sapma bir açıklama değildir.
    ⚠ Hedef seçilemezse (`None`) çağıran eski davranışına döner — kapsam kaybı yok.
    """
    dims = [d for d in (cq.get("dimensions") or []) if d]
    if not dims:
        return None
    dim = dims[0]
    _tumu = list((cube_meta.get("measures") or []))
    _lower = set(cube_meta.get("lower_is_better") or [])
    _units = cube_meta.get("units") or {}
    _disp = cube_meta.get("measure_synonyms_display") or {}

    def _kos(olculer: list[str]) -> list[dict]:
        _q = {**cq, "measures": olculer, "dimensions": [dim]}
        for _k in ("order", "limit", "pencere", "turev", "entity_limit"):
            _q.pop(_k, None)
        try:
            _r = service.query(service.cube_sql(_q))
        except Exception:                                  # noqa: BLE001 — tur düşmez
            _log.warning("akran kıyası sorgusu düştü (best-effort)", exc_info=True)
            return []
        _rows = (_r or {}).get("rows") or []
        return satir_donustur(_rows) if satir_donustur else _rows

    # 🔴 **`FAZ O-1` — GÖVDE İKİ İLKELE TAŞINDI, DAVRANIŞ BİREBİR KORUNDU.**
    #
    # Bu satırlar önce burada, elle yazılıydı. Orkestratör planının ilk fazı (`O-1`) onları
    # `app/ilkeller.py`'ye **saf fonksiyon** olarak çıkardı: `bagla` (SATIR → hangi varlık)
    # ve `hesapla` (SATIR → akran farkı). ⊙ Amaç yeni bir yetenek DEĞİL: plan geldiğinde
    # **aynı ilkelleri başka sırayla** dizebilsin diye zemin kurmak.
    #
    # ⚠ Kabul ölçütü raporda yazılı ve burada **uygulanıyor**: *«`§AA1`'in bugünkü çıktısı
    # bu ikisi çağrılarak birebir üretilebiliyor»*. Eşikler (`len < 3`), yön kaynağı
    # (`lower_is_better`) ve payda-sıfır kuralı **aynen taşındı** — denkliğin şartı bu.
    # ⚠ `E4`: elle yazılmış sürüm **kaybolmadı**, ilkellere **taşındı**. Bir yolu
    # silmeden genelleştirmek, geri dönüşü açık bırakmaktır.
    from app import ilkeller as _ilk

    taban = _kos([measure])
    _az_iyi = measure in _lower
    hedef, _hd = _ilk.bagla(taban, dim, measure, en_iyi_az=_az_iyi)
    _k = _ilk.hesapla(taban, dim, measure, hedef) if hedef else None
    if _k is None:
        return None                       # akran yoksa kıyas da yok (istatistik anlamsız)
    _ort, _fark, _yuzde = (_k["akran_ortalamasi"], _k["fark"], _k["fark_yuzde"])
    _deg = {hedef: _k["hedef_deger"]}
    _akranlar = [None] * _k["akran_sayisi"]

    # 2. SORGU — küpün öteki ölçüleri. Hedef ölçü ve toplanabilirliği bilinmeyenler dışta.
    _otekiler = [m for m in _tumu if m != measure][:12]
    surukleyenler: list[dict] = []
    if _otekiler:
        for r in _kos(_otekiler):
            if str(r.get(dim)) != hedef:
                continue
            for m in _otekiler:
                hv = _sayi_ya_da_yok(r.get(m))
                if hv is None:
                    continue
                _ak = [_sayi_ya_da_yok(x.get(m)) for x in _kos([m]) if str(x.get(dim)) != hedef]
                _ak = [x for x in _ak if x is not None]
                if not _ak:
                    continue
                _o = sum(_ak) / len(_ak)
                if not _o:
                    continue                       # payda sıfır → bölme UYDURULMAZ
                _sp = round(100.0 * (hv - _o) / _o, 1)
                surukleyenler.append({
                    "measure": m, "label": _disp.get(m) or m, "unit": _units.get(m),
                    "hedef": hv, "akran_ort": round(_o, 2), "sapma_yuzde": _sp,
                    # 🔴 Yön beyandan: sapmanın **kötü** olup olmadığını sayı söylemez.
                    "kotu_yonde": (_sp > 0) if m in _lower else (_sp < 0)})
            break
    surukleyenler = sorted(
        [s for s in surukleyenler if s["kotu_yonde"]],
        key=lambda s: abs(s["sapma_yuzde"]), reverse=True)[:3]
    return {"hedef": hedef, "boyut": dim, "hedef_deger": _deg[hedef],
            "akran_ortalamasi": round(_ort, 4), "fark": round(_fark, 4),
            "fark_yuzde": _yuzde, "akran_sayisi": len(_akranlar),
            "surukleyenler": surukleyenler}


def arastir(service, schema: dict, cube_query: dict, *, mode: str = "yoy",
            kind: str = "segment", max_dimensions: int | None = None,
            kaydet=None, satir_donustur=None) -> dict:
    """Katkı ARAŞTIRMASI — kullanılmayan boyutları tarar, değişimi ayrıştırır, sıralar.

    Saf orkestrasyon: HTTP bilmez, FastAPI bilmez. Dönen sözlük `ContributionResponse`
    alanlarıyla birebir aynıdır (router onu doğrudan sarar).

    `kaydet(baslik, cube_query, sql, result) -> contract_id | None` — her kıyas sorgusu
    KENDİ kanıt kaydını üretir. `None` geçilirse makbuz yazılmaz; bu **bilinçli bir
    seçimdir**, sessiz bir kayıp değil: çağıran (ör. arka plan uyarısı) zaten kendi kök
    makbuzunu yazmışsa boyut başına ikinci bir kayıt gürültüdür.

    `satir_donustur(rows) -> rows` — ayrıştırmadan ÖNCE satırlara uygulanır. Zamanlanmış
    teslim bunu PII maskesi için kullanır: orada alıcının kim olduğu önceden bilinemez,
    bu yüzden fail-closed maskelenir (`schedules.run_schedule`'ın ana sonuçta uyguladığı
    disiplinin aynısı — ikinci bir sızıntı yüzeyi bırakılmaz).
    """
    from app import yoy as _yoy
    from app.drill import available_dimensions

    cq = dict(cube_query or {})
    if not cq.get("cube"):
        # 🔴 FAZ 5.17 — **JARGON SIZINTISI ÖLÇÜLDÜ.** Eski metin kullanıcıya
        # *"yapısal bir `cube_query` taşımıyor (Discovery/ham SQL)"* diyordu — yani
        # **bizim sorunumuzu** ona anlatıyordu. Kullanıcı bu cümleden ne yapması
        # gerektiğini çıkaramaz; yalnız bir şeyin bozuk olduğunu sanır.
        from app import soz as _soz

        return {"note": _soz.soz("bilgi.yapisal_sorgu_yok")}
    cube_meta = next((c for c in (schema.get("cubes") or [])
                      if c.get("name") == cq.get("cube")), None)
    if cube_meta is None:
        return {"note": f"`{cq.get('cube')}` cube'u şemada yok (şema değişmiş olabilir) — "
                        "katkı ayrıştırması yapılamaz.", "hata": "cube_yok"}

    kind = kind if kind in ("segment", "pvm") else "segment"
    mode = mode if mode in ("yoy", "mom") else "yoy"
    measure = (cq.get("measures") or [None])[0]

    if kind == "pvm":
        # Eşleştirme TAHMİN EDİLMEZ: cube'un `pvm:` beyanı yoksa PVM sunulmaz. Ad kalıbıyla
        # ("tutar/adet fiyattır") tahmin etmek, yanlış eşleştirmede GÜVENLE YANLIŞ ekonomi
        # üretirdi — kullanıcı "birim fiyat %12 arttı" cümlesini sorgulamaz.
        cift = next((p for p in pvm_pairs(cube_meta) if p["value"] == measure), None)
        if cift is None:
            return {"measure": measure, "mode": mode, "kind": kind,
                    "note": (f"`{cq.get('cube')}` cube'u `{measure}` için bir fiyat×miktar "
                             "eşleştirmesi BEYAN ETMİYOR (cube metadata'sında `pvm:`). Fiyat "
                             "ayrıştırması ancak beyan edilmiş bir değer/miktar çifti "
                             "üzerinde anlamlıdır; tahmin edilmez.")}
    else:
        ok, neden = ayristirilabilir_mi(measure, cube_meta)
        if not ok:
            # 🔴🔴 **`§AA1` — «NEDEN DÜŞÜK?» BİR AYRIŞTIRMA DEĞİL, BİR KIYASTIR.**
            #
            # Kullanıcı bildirdi, canlıda birebir doğrulandı (`AA2`):
            #
            #     soru : «RAM-3 neden diğerlerinden düşük»
            #     cevap: «ort_oee toplanabilir değil (non_additive) — katkı payı
            #             matematiksel olarak tanımsız olur»
            #
            # ⊙ Cümle **doğru** ama **başka bir sorunun** cevabı. Katkı payı şunu sorar:
            # *"toplamın yüzde kaçı bu segmentten geldi?"* — bir ortalamada bu gerçekten
            # tanımsızdır. Kullanıcının sorduğu ise: *"bu neden ÖTEKİLERDEN düşük?"* —
            # bu bir **karşılaştırmadır** ve bir ortalamada **pekâlâ tanımlıdır**.
            #
            # 🔴 Yani sistem, cevaplayabileceği bir soruyu, **sormadığı** bir sorunun
            # imkânsızlığıyla reddediyordu. `§1.5`'in en pahalı biçimi: doğru bir kapı,
            # yanlış kapıya konmuş.
            #
            # ⊙ Çözüm yeni bir motor DEĞİL, var olan iki şeyin kompozisyonu:
            #   1. **akran kıyası** — hedefin değeri ↔ ötekilerin ortalaması (fark, %)
            #   2. **sürükleyen ölçü** — aynı küpün ÖTEKİ ölçülerinde hedefin akranlardan
            #      en çok saptığı ölçü. `oee` için bunlar `ort_kullanilabilirlik` ·
            #      `ort_performans` · `ort_kalite` · `plansiz_durus_dakika`'dır ve hepsi
            #      **zaten tanımlı** — yani mutfak bu yemeği yapabiliyordu, tabağa
            #      koyacak kimse yoktu.
            #
            # ⚠ Katkı **payı** hâlâ üretilmez ve gerekçesi **korunur** (`YOK` sınıfı
            # doğrudur): dönen nesne bir *"yüzde kaçı"* iddiası taşımaz, yalnız **fark**
            # ve **sapma** taşır. Bir sınırı aşmıyoruz, yanına doğru soruyu koyuyoruz.
            #
            # *Bir sorunun cevaplanamaz olduğunu söylemeden önce, sorulan sorunun o soru
            # olduğundan emin olmak gerekir.*
            _akran = _akran_kiyasi(service, cq, cube_meta, measure, satir_donustur)
            if _akran is not None:
                # ⚠ **Bulgu `note`'a YAZILIR, ek alana değil** — ve bu bir sondaj
                # bulgusudur: `ContributionResponse` **sabit alanlıdır** (`arastir`'ın
                # kendi docstring'i *"dönen sözlük onun alanlarıyla birebir aynıdır"*
                # diyor). İlk yazımda `hedef`/`surukleyenler` diye yeni anahtarlar
                # döndürdüm; canlıda **sessizce düştüler** ve kullanıcıya yalnız
                # *"akran kıyası yapıldı"* cümlesi ulaştı — yapılan işin **kendisi**
                # değil. *Bir cevabı üretmek, onu taşıyan alana koymakla tamamlanır.*
                _b = _akran

                # ⚠ **Biçimlendirme burada, çünkü metin burada üretiliyor.** İlk canlı
                # koşumda ekrana `0.5245118291704627` ve `63452.000000000044` düştü —
                # kayan nokta gürültüsü. Bir makbuz cümlesi doğru olmakla yetinmez,
                # **okunabilir** de olmalı; okunamayan bir sayı sorgulanmaz, atlanır.
                # 🔴 `§SB-metin` — `_b3` bu sayının **DÖRDÜNCÜ** biçimlendiricisiydi
                # (ölçüldü, `EE` turu, EE-1: *«%8.7 düşük (74.39 ↔ 81.46)»* — ondalık
                # ayırıcı İngilizce). Tek sahip `app/sayi_bicimi.py`.
                # *Bir sayının Türkçesi tek bir yerde yazılır.*
                _b3 = _ssayi

                _yon = "düşük" if _b["fark"] < 0 else "yüksek"
                _sat = [f"**{_b['hedef']}**, öteki {_b['akran_sayisi']} "
                        f"{(cube_meta.get('dimension_labels') or {}).get(_b['boyut']) or _b['boyut']} "
                        f"ortalamasından **{_syuzde(abs(_b['fark_yuzde'] or 0))} {_yon}** "
                        f"({_b3(_b['hedef_deger'])} ↔ akran ort. {_b3(_b['akran_ortalamasi'])}).", ""]
                if _b["surukleyenler"]:
                    _sat.append("**Farkı en çok açıklayanlar** — aynı kırılımda, akran "
                                "ortalamasına göre:")
                    for _s in _b["surukleyenler"]:
                        _br = f" {_s['unit']}" if _s.get("unit") else ""
                        _sat.append(
                            f"• **{_s['label']}**: {_b3(_s['hedef'])}{_br} — akran ortalaması "
                            f"{_b3(_s['akran_ort'])}{_br} (**{_syuzde(abs(_s['sapma_yuzde']))} "
                            f"{'fazla' if _s['sapma_yuzde'] > 0 else 'az'}**, kötü yönde)")
                    _sat.append("")
                    _sat.append("Ayrıntı için: *«… nedenlerini kır»* ya da *«hangi "
                                "vardiyada»* diye devam edebilirsin.")
                else:
                    _sat.append("⚠ Aynı küpün öteki ölçülerinde akranlardan **kötü yönde "
                                "belirgin bir sapma bulunamadı** — fark bu küpteki "
                                "ölçülerle açıklanamıyor.")
                _akran.update({
                    "measure": measure, "mode": mode, "kind": "akran",
                    "raporlar": [], "pvm_raporlar": [], "contract_ids": [],
                    "taranmayan_boyut": 0, "taranmayan_adlar": [],
                    "note": "\n".join(_sat)})
                return _akran
            return {"measure": measure, "mode": mode, "kind": kind, "note": neden}
        cift = None

    time_dim = _yoy.time_dim_of(schema, cq.get("cube"))
    unit = (cube_meta.get("units") or {}).get(measure)
    labels = cube_meta.get("dimension_labels") or {}

    # SIRA ANLAMLIDIR (Faz B): `available_dimensions` adayları maliyet+güvene göre verir
    # (kendi tablosundaki boyut önce; sonra sıçrama sayısı; sonra fan-out sertifikası).
    # Kesme yapılacaksa denenmeye önce onlar değer — hangi boyutun daha AÇIKLAYICI olduğu
    # önceden bilinemez, onu `rank_dimensions` sorgudan SONRA ölçer.
    adaylar = [d["name"] for d in available_dimensions(cube_meta, cq)]
    sinir = max(1, int(max_dimensions or MAX_BOYUT))
    taranan, atlanan = adaylar[:sinir], adaylar[sinir:]
    taranmayan = len(atlanan)
    if taranmayan:
        # Sessiz kesme YOK: kapsamı daraltan her sınır loglanır VE yanıtta görünür.
        # Atlananlar ADIYLA taşınır — bir SAYI ("3 boyut taranmadı") kullanıcıya hangi
        # soruyu sorabileceğini söylemez; ad söyler ("peki renk bazında?").
        _log.info("katkı araması: %d boyuttan %d tanesi taranmadı (sınır=%d, cube=%s): %s",
                  len(adaylar), taranmayan, sinir, cq.get("cube"), ", ".join(atlanan))

    raporlar: list[dict] = []
    pvm_raporlar: list[dict] = []
    contract_ids: list[str] = []
    for dim in taranan:
        # PVM iki ölçüyü BİRLİKTE ister (değer ve miktar aynı kıyas sorgusunda gelsin ki
        # segment hizalaması kesin olsun; ayrı iki sorgu satır kümesi ayrışabilirdi).
        olculer = [cift["value"], cift["volume"]] if cift else list(cq.get("measures") or [])
        alt = {**cq, "measures": olculer, "dimensions": [dim]}
        try:
            out = _yoy.compute(service, {**alt, "compare": mode}, mode, time_dim)
        except Exception:
            _log.warning("katkı araması: %s boyutu için kıyas başarısız (atlanıyor)",
                         dim, exc_info=True)
            continue
        satirlar = out["rows"]
        if satir_donustur is not None:
            satirlar = satir_donustur(satirlar)
        if cift:
            rapor = pvm_report(satirlar, dim, cift, alt,
                               dim_label=labels.get(dim), unit=unit)
            if not rapor["bulgular"]:
                continue
            pvm_raporlar.append(rapor)
        else:
            rapor = decompose(satirlar, dim, measure, alt,
                              dim_label=labels.get(dim), unit=unit)
            if not rapor["bulgular"]:
                continue
            raporlar.append(rapor)
        # Her katkı sorgusu KENDİ kanıt kaydını üretir — "yeniden çalıştırılıp hash
        # eşlenebilen makbuz" değişmezi burada da geçerli (drill ile AYNI desen).
        if kaydet is not None:
            cid = kaydet(f"katkı araması: {measure} × {dim} ({mode})", {**alt, "compare": mode},
                         out["base_sql"], {"columns": out["columns"], "rows": satirlar,
                                           "row_count": out["row_count"]})
            if cid:
                contract_ids.append(cid)

    if not raporlar and not pvm_raporlar:
        return {"measure": measure, "mode": mode, "kind": kind,
                "taranmayan_boyut": taranmayan, "taranmayan_adlar": atlanan,
                "note": "Bu sorguda değişimi açıklayan bir kırılım bulunamadı — "
                        "kullanılmayan boyut yok ya da hiçbir segment anlamlı bir hareket "
                        "göstermiyor."}

    return {"measure": measure, "mode": mode, "kind": kind,
            "taranmayan_boyut": taranmayan, "taranmayan_adlar": atlanan,
            "contract_ids": contract_ids,
            "raporlar": rank_dimensions(raporlar),
            "pvm_raporlar": rank_dimensions(pvm_raporlar)}


def yanindaki_rapor(service, cq: dict | None, *, limit: int = 200):
    """🔴🔴 `§AA2` — **REDDİN YANINA KONAN RAPOR: bir tekniğin sınırı, turun cevabı olamaz.**

    ## Ölçülen kusur (7 turluk canlı zincir, 2026-08-10)

    Altı tur kusursuz aktı; yedincisi — *«özetle ne yapmalıyız»* — **bomboş** döndü:

        source=None · rows=0 · interpretation=YOK · next_steps=[]
        note: «fire_orani_yuzde toplanabilir değil (non_additive) — katkı payı
               matematiksel olarak tanımsız olur»

    Cümle **doğru**: bir oranda katkı payı gerçekten tanımsızdır. Ama kullanıcı *katkı
    payı* istemedi, **özet** istedi — ve özet **elde vardı**.

    ⊙ Ve bu, bu dosyanın `§AA1`'de yazdığı dersin **birebir tekrarıydı**: *«Bir sınırı
    aşmıyoruz, yanına doğru soruyu koyuyoruz.»* Orada uygulanmış, çağıran tarafta
    uygulanmamıştı — o yüzden yardımcı **buraya** kondu: ilkenin evi burası.

    ## Ne yapar

    Eldeki fişi **LLM'siz** yeniden koşar (`D4`'ün checkpoint yeteneği) ve satırları
    döndürür; çağıran onları yanıta iliştirir, `_maybe_interpret` olguları ve devam
    chip'lerini **kendiliğinden** üretir.

    ⚠ En-iyi-çaba: koşum düşerse `None` döner ve **red yine döner** — bir yardımcı,
    yardım edemediğinde cevabı düşürmemelidir.

    *«Yapamam» bir cevap değildir; «şunu yapamam ama şunu biliyorum» bir cevaptır.*
    """
    if not cq or not cq.get("cube"):
        return None
    try:
        return service.query(service.cube_sql(cq), limit=limit)
    except Exception:                                   # noqa: BLE001 — red yine döner
        _log.warning("§AA2: red yanında eldeki rapor yeniden koşulamadı", exc_info=True)
        return None
