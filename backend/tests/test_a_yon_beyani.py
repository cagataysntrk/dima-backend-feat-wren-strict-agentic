r"""🔴 `§A.3` — **YÖN BEYANSIZLIĞI SESSİZDİ, ve borç ÖLÇÜLMEMİŞTİ.**

## Ölçüm (2026-08-12, gerçek katalog)

```
23 küp · 136 ölçü · 816 ayrık terim
yön beyansız: 68 / 136  (%50,0)
```

Şema **yalnız** `lower_is_better` taşıyor; bir `higher_is_better` listesi **yok**.
`kok_neden._yon_beyanli:400` bunu kendi docstring'inde **zaten ölçmüş**:

> *«Listede değil» iki farklı şey demek olabilir: «yüksek iyidir» ya da «yönü yoktur»
> (adet gibi nötr bir sayı). `GG8` gereği ikisi **ayrılmaz sayılır**: beyan yoksa yön
> **bilinmiyordur**.*
>
> *Bir listede olmamak, karşıt listede olmak değildir.*

✅ **Davranış zaten fail-safe'ti**: yön bilinmiyorsa `dusuk_iyi=None` geçiyor ve yargı
üretilmiyor → **sessiz-yanlış yok**.
🔴 **Ama sessizlik iki durumu birleştiriyordu** ve kullanıcı hangisinde olduğunu
bilemiyordu. Onarım `§E2`/`§E3` ile aynı: ölçüyü uydurma, **ölçemediğini söyle**.

⚠ `§101.1`: beyan **yalnız** bir yön yargısının zaten basılacağı cümlede. Her cevabın
altına eklenirse uyarı okunmaz olur.
"""

from __future__ import annotations

#: 🔴 Bugünkü ölçüm: **68/136**. Kapı bunun **üstüne çıkmayı** yasaklar — katalog
#: büyürken borç **sessizce** büyümesin. ⊙ Düşürmek serbest ve **beklenen** yön.
#: *Bir raporun sayısını kapıya bağlamazsan, o sayı bir sonraki turda bir hatıra olur.*
AZAMI_YONSUZ_ORAN = 0.50

_BOYUT, _OLCU = "kaynak", "toplam_enpg"
_CQ = {"cube": "enerji_sapma", "measures": [_OLCU], "dimensions": [_BOYUT], "filters": []}


def _kos(degerler):
    satirlar = [{_BOYUT: f"S{i}", _OLCU: v} for i, v in enumerate(degerler)]
    return lambda cq: list(satirlar)


def _meta(*, dusuk_iyi: bool):
    m = {"name": "enerji_sapma", "measure_expressions": {_OLCU: f"SUM({_OLCU})"},
         "dimensions": [_BOYUT], "measures": [_OLCU]}
    if dusuk_iyi:
        m["lower_is_better"] = [_OLCU]
    return m


def test_YON_BEYANSIZSA_SOYLENIYOR():
    """🔴🔴 **ASIL KAPI.** Yön beyanı yoksa cümle bunu **söylemeli** — sessiz kalmak,
    *«yüksek iyidir»* ile *«bilinmiyor»*u aynı yere koymaktır."""
    from app import kok_neden as kn

    r = kn.toplam_turu(_CQ, _meta(dusuk_iyi=False), kos=_kos([100.0, 50.0, 30.0, 20.0]))
    assert r, "⊘ ölçüm tabanı çöktü: cümle üretilmedi"
    m = str(r.get("anlati") or "")
    assert "beyan edilmemiş" in m, (
        f"🔴 yön beyansız ölçüde cümle SESSİZ — kullanıcı «arttı, iyi mi kötü mü» "
        f"sorusunun cevapsız kaldığını bilmiyor:\n{m[:400]}")
    assert "yargı verilmez" in m, (
        f"🔴 beyan var ama **ne yapılmadığını** söylemiyor:\n{m[:400]}")


def test_YON_BEYANLIYSA_UYARI_BASILMIYOR():
    """⚠ `§101.1` — yön **beyanlı** bir ölçüde uyarı basmak bir **yanlış-pozitiftir** ve
    beyanı gürültüye çevirir."""
    from app import kok_neden as kn

    r = kn.toplam_turu(_CQ, _meta(dusuk_iyi=True), kos=_kos([100.0, 50.0, 30.0, 20.0]))
    m = str((r or {}).get("anlati") or "")
    assert "düşük** iyidir" in m, f"⊘ ölçüm tabanı: yargı basılmadı:\n{m[:300]}"
    assert "beyan edilmemiş" not in m, (
        f"🔴 yön BEYANLI ölçüde de uyarı basılıyor — yanlış uyarı:\n{m[:400]}")


def test_BORC_ORANI_TAVANI_ASMIYOR(schema):
    """🔴 **BORÇ KAPISI.** Bugün **68/136 (%50)**. Katalog büyürken bu oran artarsa
    borç **sessizce** büyümüş demektir — kapı onu **görünür** yapar.

    ⊙ Oranı **düşürmek** serbesttir ve beklenen yöndür; kapı yalnız **artışı** yasaklar.
    """
    tum = yonsuz = 0
    for c in schema["cubes"]:
        lower = set(c.get("lower_is_better") or [])
        for m in (c.get("measures") or []):
            ad = m.get("name") if isinstance(m, dict) else m
            tum += 1
            if ad not in lower:
                yonsuz += 1
    assert tum >= 100, f"⊘ ölçüm tabanı çöktü: {tum} ölçü (beklenen ≥100)"
    oran = yonsuz / tum
    assert oran <= AZAMI_YONSUZ_ORAN + 1e-9, (
        f"🔴 YÖN BEYANSIZ ORAN ARTTI: {yonsuz}/{tum} = %{oran * 100:.1f} > "
        f"%{AZAMI_YONSUZ_ORAN * 100:.0f}. Katalog büyürken yön beyanı geride kaldı — "
        "yeni ölçüler `lower_is_better`'a ya da (kararı verilirse) bir "
        "`higher_is_better` listesine yazılmalı.")


def test_SAHIP_TEK_yon_okuma_ikinci_kez_yazilmadi():
    """⚠ `KAT-1` — yön beyanını okuyan **tek** yer `_yon_beyanli`. Beyan cümlesi de onu
    çağırmalı; ikinci bir `lower_is_better` okuması bir gün ötekinden ayrışır."""
    import inspect

    from app import kok_neden as kn

    kaynak = inspect.getsource(kn.toplam_turu)
    assert "_yon_beyanli(olcu, cube_meta)" in kaynak, (
        "🔴 beyan cümlesi `_yon_beyanli`'yi ÇAĞIRMIYOR — yön okuması ikinci kez "
        "yazılmış olabilir (`KAT-1`).")
