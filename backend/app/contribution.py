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
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


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


def rank_dimensions(raporlar: list[dict]) -> list[dict]:
    """Boyutları AÇIKLAYICILIĞA göre sırala: en büyük tek segment payı yüksek olan önce.

    Sezgi: değişimin %70'i tek bir makineden geliyorsa `makine` boyutu, değişimi 12 eşit
    parçaya bölen `hafta_gunu`ndan daha AÇIKLAYICIDIR. Adtributor'ın "surprise" ölçüsünün
    en yalın, açıklanabilir hali — entropi yerine tek bir okunabilir sayı, çünkü kullanıcıya
    gösterilecek gerekçe de bu sayıdır.
    """
    def _skor(r: dict) -> float:
        return max((abs(b["brut_pay"] or 0) for b in r.get("bulgular") or []), default=0.0)

    return sorted(raporlar, key=_skor, reverse=True)
