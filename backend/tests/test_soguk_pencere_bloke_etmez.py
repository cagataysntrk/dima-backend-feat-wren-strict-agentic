"""🔴 `§65` — **ISINMA PENCERESİNDE İSTEK BLOKE OLMAZ** (`§46`'nın kapatılmamış deliği).

## Ölçülen kusur (canlı `s28`, kullanıcı *«canlıda hazır mıyız»* diye sorunca)

`§46` şunu yazmıştı: *«bir istek soğuk indekse rastlarsa vektör ayağı susar, leksik ayak
cevabı verir»*. Ama koruma **hiç ateşlenmiyordu**:

```
_ISITMA = False                       # modül globali
isit():  _ISITMA = True  …  False     # ısıtma ARKA PLANDA bir iplikte
ara():   if … and not _ISITMA …       # ısınma boyunca her iplikte True → atlama YOK
```

| ölçüm | değer |
|---|---|
| `GET /oneri?q=ram 3` (ısınma penceresi) | 🔴 **90 sn'de HTTP=000** |
| ısınma süresi | 🔴 **204.990 ms** *(beklenen ~48 sn — iki iplik aynı gömmeyi hesaplıyordu)* |

> *Bir bayrağın kapsamı, koruduğu şeyin kapsamıyla aynı olmalıdır.* İnşa hakkı **ısıtan
> ipliğin** hakkıdır, sürecin bir hâli değil — o yüzden `threading.local`.

## Bu kapının üç yüklemi

| # | savunulan |
|---|---|
| 1 | **başka bir iplik** ısıtırken istek yolu vektör ayağını **atlar** |
| 2 | ısıtan **iplik kendi** hakkını korur 🆃 — yoksa indeks hiç kurulmaz |
| 3 | ısınma **başlamamışsa** (test/lab) davranış eskisi gibi ㉖ |
"""

from __future__ import annotations

import threading

from app import oneri


def _yerel_sifirla() -> None:
    oneri._ISITMA_YEREL.acik = False


def test_BASKA_IPLIK_ISITIRKEN_ISTEK_ATLAR(schema):
    """🔴 **ASIL DEĞİŞMEZ.** Kullanıcı, başkasının ısınmasını beklemez."""
    onceki = oneri._ISITMA_BASLADI
    hak: list[bool] = []
    try:
        oneri._ISITMA_BASLADI = True
        _yerel_sifirla()

        def _isitan() -> None:
            oneri._ISITMA_YEREL.acik = True
            hak.append(oneri._insa_hakki())

        t = threading.Thread(target=_isitan)
        t.start()
        t.join()
        assert hak == [True], "🔴 ısıtan iplik kendi hakkını göremedi"
        assert not oneri._insa_hakki(), (
            "🔴 başka bir ipliğin ısıtma hakkı BU ipliğe sızdı — atlama koşulu hiç "
            "ateşlenmez ve kullanıcı ısınma boyunca bloke kalır (ölçüldü: 90 sn HTTP=000)")
    finally:
        oneri._ISITMA_BASLADI = onceki
        _yerel_sifirla()


def test_ZIT_OLCUT_ISITAN_IPLIK_INSA_EDEBILIR(schema):
    """🆃 Kapının kurbanı: hakkı **tümden** kapatmak indeksi hiç kurulmaz yapardı."""
    try:
        oneri._ISITMA_YEREL.acik = True
        assert oneri._insa_hakki(), "🔴 ısıtan iplik inşa edemiyor — indeks hiç kurulmaz"
    finally:
        _yerel_sifirla()


def test_ISITMA_BASLAMADIYSA_DAVRANIS_AYNI(schema):
    """㉖ Isıtmanın hiç çağrılmadığı ortamda (birim testi · `lab/`) istek yolu indeksi
    eskisi gibi kurar — yoksa ölçüm sessizce leksikleşirdi 🅣."""
    onceki = oneri._ISITMA_BASLADI
    try:
        oneri._ISITMA_BASLADI = False
        _yerel_sifirla()
        assert oneri.ara("fire", schema), "🔴 ısıtmasız ortamda arama boşaldı"
    finally:
        oneri._ISITMA_BASLADI = onceki
