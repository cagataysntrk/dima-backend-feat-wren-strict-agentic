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

from typing import Any

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



def ayristirilabilir_mi(measure: str, cube_meta: dict | None) -> tuple[bool, str | None]:
    """(ayrıştırılabilir?, ayrıştırılamıyorsa NEDENİ).

    Toplanabilirlik sezgiyle değil, cube metadata'sının KENDİ beyanıyla belirlenir
    (`non_additive` / `semi_additive`) — bu listeler zaten `is_period_optional` tarafından
    da okunuyor, yani ikinci bir doğruluk kaynağı YARATILMIYOR.

    Metadata sessizse ifadeye bakılır: `AVG`/`COUNT(DISTINCT`/oran kalıpları toplanabilir
    DEĞİLDİR. Emin olunamayan durumda ayrıştırma YAPILMAZ — yanlış bir yüzde, hiç yüzde
    olmamasından kötüdür.
    """
    if not measure:
        return False, "ölçü belirtilmemiş"
    meta = cube_meta or {}
    if measure in (meta.get("non_additive") or []):
        return False, (f"`{measure}` toplanabilir değil (cube metadata'sında `non_additive`) — "
                       "segmentlerin değişimleri toplamı, toplamın değişimini VERMEZ")
    if measure in (meta.get("semi_additive") or []):
        return False, (f"`{measure}` yarı-toplanabilir bir stok/bakiye ölçüsü — dönem içi "
                       "değişimi segmentlere dağıtmak anlamlı değil")
    ifade = ((meta.get("measure_expressions") or {}).get(measure) or "").upper()
    if ifade:
        if "AVG(" in ifade or "COUNT(DISTINCT" in ifade or "/" in ifade:
            return False, (f"`{measure}` bir ortalama/oran — parçaların toplamı bütünü "
                           "vermez, katkı payı matematiksel olarak tanımsız olur")
        return True, None
    # Metadata ifadeyi yayımlamıyorsa ad kalıbına düşülür (son çare, muhafazakâr).
    ad = measure.lower()
    if ad.startswith("ort_") or ad.endswith(("_yuzde", "_orani", "_pct")):
        return False, (f"`{measure}` bir ortalama/oran gibi görünüyor — parçaların toplamı "
                       "bütünü vermez, katkı payı tanımsız olur")
    return True, None


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
    return sorted(kalemler, key=lambda k: abs(k["delta"]), reverse=True)


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
        yon = "arttı" if k["delta"] > 0 else "azaldı"
        pay = (f" (net değişimin %{k['net_pay']}'i)" if k["net_pay"] is not None
               else f" (hareketin %{k['brut_pay']}'i)")
        bulgular.append({
            **k,
            "label": f"{etiket}: {k['deger']} — {abs(k['delta']):,.0f}{' ' + unit if unit else ''} "
                     f"{yon}{pay}",
            "kind": "dimension",
            "cube_query": select_cube_query(cube_query, dim, k["deger"]),
        })
    return {
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
