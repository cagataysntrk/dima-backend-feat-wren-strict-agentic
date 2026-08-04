"""FAZ 2.5 — **HEDEF KIYASI.** Grafikteki çizgi *hedef* mi, *ortalama* mı?

## Ölçülen durum — ve neyin kusur OLMADIĞI

`viz.py` referans çizgisini `{"kind": "average", …}` diye üretiyor ve `chart.ts` onu
`Ort. …` diye etiketliyor. Yani **yanlış etiketleme YOK** — sistem bugün dürüst.

Eksik olan **mekanizmanın kendisi**: `target:` beyanı **hiçbir cube'da yok**, dolayısıyla
kullanıcı *"hedefimin altında mıyım"* sorusunu soramıyor ve grafikte gördüğü çizgi her
zaman **kendi ortalaması** — yani kendi kendine kıyas.

## 🔴 DEĞİŞMEZ: HEDEF UYDURULMAZ

Beyan yoksa **bayrak açık olsa bile** hedef çizgisi çizilmez ve etiket `Ort.` kalır.
*"Hedef yok"* ile *"hedef 0"* asla karıştırılmaz — sıfır hedef, ulaşılmış bir hedeftir;
hedefsizlik ise **ölçülemezliktir**. Bir hedefi tahmin etmek (geçen yılın ortalaması,
sektör medyanı…) kullanıcının **kendi sınırını** sistemin uydurmasıyla değiştirirdi.

## ⚠ KAPSAM — bu dilim yalnız BEYAN yolunu açar

Yol haritası `MetricTarget`'ı SCD-2 olarak tanımlıyor (`scope` ∈ `tenant|branch|user|
sirket_ana_hedef` · `effective_from`/`to` · `set_by` · `supersedes` · `as_of` yeniden
oynatma). Bu dilim **cube YAML'ındaki `target:` beyanını** okur; kişi/şube kapsamlı ve
tarihli hedefler **ayrı bir dilimdir** ve o dilim gelene kadar burada **uydurulmaz**.

*Yarım inmiş bir mekanizmayı tam gibi göstermek, hiç indirmemekten kötüdür* — bu yüzden
sınır burada yazılı ve kapı onu kilitliyor.
"""

from __future__ import annotations

from typing import Any

#: Ölçü metadata'sındaki beyan anahtarı. Tek ad, tek yer.
BEYAN_ANAHTARI = "target"

#: Yön: hedefin **üstünde** mi olmak iyidir, **altında** mı? `lower_is_better`'dan türer —
#: ikinci bir yön beyanı yazmak, iki yönün ayrışması demekti.
YON_YUKSEK_IYI = "yuksek_iyi"
YON_DUSUK_IYI = "dusuk_iyi"


def beyan(schema: dict[str, Any], cube: str | None, olcu: str | None) -> float | None:
    """Cube metadata'sında beyan edilmiş hedef — yoksa `None`.

    🔴 `None` *"hedef 0"* DEĞİLDİR. Çağıran bu ayrımı korumak zorunda: sıfır hedef
    **ulaşılmış** bir hedeftir, hedefsizlik ise **ölçülemezliktir**.
    """
    if not cube or not olcu:
        return None
    for c in schema.get("cubes") or []:
        if c.get("name") != cube:
            continue
        ham = (c.get("hedefler") or {}).get(olcu)
        try:
            return float(ham) if ham is not None else None
        except (TypeError, ValueError):
            return None                      # bozuk beyan = beyan YOK (uydurma yapılmaz)
    return None


def yon(schema: dict[str, Any], cube: str | None, olcu: str | None) -> str:
    """Hedefin hangi yönü *iyi*. `lower_is_better`'dan **türer**, yeniden beyan edilmez."""
    for c in schema.get("cubes") or []:
        if c.get("name") == cube and olcu in (c.get("lower_is_better") or []):
            return YON_DUSUK_IYI
    return YON_YUKSEK_IYI


def blok(schema: dict[str, Any], cq: dict[str, Any] | None,
         sonuc: dict[str, Any] | None) -> dict[str, Any] | None:
    """`AskResponse.hedef` bloğu — beyan yoksa **None** (çizgi ortalama kalır).

    Döner: `{olcu, hedef, gerceklesen, yon, ulasildi, sapma_yuzde}`

    ⚠ `gerceklesen` **sonuçtan** okunur, hedeften türetilmez: hedefe göre normalize
    edilmiş bir *"gerçekleşen"* uydurmak, kullanıcının sayısını sistemin sayısıyla
    değiştirmek olurdu.
    """
    cq = cq or {}
    olculer = list(cq.get("measures") or [])
    if len(olculer) != 1:
        return None                          # çok ölçülü rapor: hangi hedef? — BELİRSİZ
    olcu, cube = olculer[0], cq.get("cube")
    h = beyan(schema, cube, olcu)
    if h is None:
        return None
    satirlar = (sonuc or {}).get("rows") or []
    degerler = [r.get(olcu) for r in satirlar if isinstance(r.get(olcu), (int, float))]
    if not degerler:
        return None
    gerceklesen = float(sum(degerler)) / len(degerler) if len(degerler) > 1 \
        else float(degerler[0])
    y = yon(schema, cube, olcu)
    ulasildi = gerceklesen <= h if y == YON_DUSUK_IYI else gerceklesen >= h
    return {
        "olcu": olcu,
        "hedef": h,
        "gerceklesen": round(gerceklesen, 4),
        "yon": y,
        "ulasildi": bool(ulasildi),
        # ⚠ Sıfır hedefte yüzde **tanımsızdır** ve `None` döner — `inf`/`0` yazmak, bir
        # tanımsızlığı bir ölçüm gibi gösterirdi.
        "sapma_yuzde": round((gerceklesen - h) * 100.0 / h, 2) if h else None,
    }
