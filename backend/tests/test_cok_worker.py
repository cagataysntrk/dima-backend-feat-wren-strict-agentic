"""FAZ 8.3 kapısı — **çok-worker dağıtım: iki süreç aynı dizine compose eder, MDL
bozulmaz.** [bayraksız: altyapı]

## Neden bu kapı var — ve neden bir varsayım değil, bir GÖZLEM

Yarış **iki kez** gerçekleşti:

| ne zaman | nasıl görüldü |
|---|---|
| 2026-08-02 | elle **yeniden üretildi** |
| 2026-08-04 | 🔴 **kendiliğinden**: demet 9'da `gitas` korpustan **tamamen düştü** — `FileNotFoundError: demo/wren-project/cubes/enerji_makine/metadata.yml`, ve dosya sonradan **yerindeydi** |

İkincisi kapının tüm gerekçesidir: okuyucu compose'un **ortasına** denk geldi. Ve o
koşumda korpus doğruluğu **düşmedi, YÜKSELDİ** (%93,2 → %94,3) çünkü payda küçüldü.
*Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla da olur.*

## ⚠ `gunicorn` duman testi burada koşmuyor — ve bu gizlenmiyor

Yol haritası *"gunicorn 4 worker duman testi"* diyor. Bu kapı **ağsız** bir konteynerde
koşar ve bir HTTP sunucusu ayağa kaldırmaz. Ölçülen şey **kilidin kendisidir**: dört
worker'ın paylaştığı tek risk, aynı çıktı dizinine eş zamanlı yazmaktır ve kilit orada
durur. *Ölçemediğimiz kısmı ölçmüş gibi göstermek, kapıyı bir temenniye çevirir.*
"""

from __future__ import annotations

import multiprocessing as mp
import os
import time
from pathlib import Path

import pytest

from app.compose import DerlemeKilidi

_KOK = Path(__file__).resolve().parents[1]


def _yazar(dizin: str, damga: str, tekrar: int, kuyruk) -> None:
    """Kilit altında bir dosyayı **parça parça** yazar.

    🔴 Tek `write_text` yarışı **gizlerdi**: küçük bir yazma çoğu zaman atomik görünür ve
    test yeşil kalırdı. Yarışı görünür kılmak için yazma bilerek **bölünüyor** ve araya
    bir duraklama konuyor — kilit yoksa iki süreç birbirinin ortasına girer.
    """
    hedef = Path(dizin) / "metadata.yml"
    try:
        for _ in range(tekrar):
            with DerlemeKilidi(Path(dizin)):
                with open(hedef, "w", encoding="utf-8") as f:
                    f.write(f"# {damga} BAS\n")
                    f.flush()
                    time.sleep(0.01)
                    f.write(f"govde: {damga * 20}\n")
                    f.flush()
                    time.sleep(0.01)
                    f.write(f"# {damga} SON\n")
                # Kilit BIRAKILDIKTAN sonra okumak, gerçek okuyucunun (korpus) yaptığıdır.
                metin = hedef.read_text(encoding="utf-8")
            kuyruk.put(metin)
    except Exception as e:                                     # pragma: no cover
        kuyruk.put(f"HATA: {e!r}")


@pytest.mark.skipif(not hasattr(os, "fork"), reason="⊘ POSIX dışı — süreç-arası kilit yok")
def test_IKI_SUREC_ayni_dizine_compose_eder_MDL_BOZULMAZ():
    """🔴 **8.3'ün asıl kapısı.** Kilit çalışıyorsa her okuma **tek bir yazarın tam
    çıktısıdır**; karışmışsa bir satır A'dan, diğeri B'den gelir.

    ⚠ Ölçüt *"dosya var mı"* **değil**: yarışın 2026-08-04'teki hâli tam da dosyanın
    **sonradan yerinde olmasıydı**. Ölçüt, **içeriğin tek kaynaklı** olmasıdır.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        ctx = mp.get_context("spawn")
        kuyruk = ctx.Queue()
        surecler = [ctx.Process(target=_yazar, args=(d, harf, 5, kuyruk))
                    for harf in ("A", "B", "C", "D")]  # 4 worker — gunicorn varsayılanı
        for p in surecler:
            p.start()
        for p in surecler:
            p.join(timeout=60)
            assert p.exitcode == 0, f"🔴 worker çöktü: exitcode={p.exitcode}"

        okumalar = []
        while not kuyruk.empty():
            okumalar.append(kuyruk.get())
        assert len(okumalar) == 20, f"🔴 beklenen 20 okuma, gelen {len(okumalar)}"

        for metin in okumalar:
            assert not metin.startswith("HATA:"), metin
            satirlar = [s for s in metin.strip().split("\n") if s]
            assert len(satirlar) == 3, (
                f"🔴 MDL BOZULDU — {len(satirlar)} satır:\n{metin}\n"
                f"Bir okuma başka bir yazarın ortasına denk geldi.")
            damgalar = {s.split()[1] for s in satirlar if s.startswith("#")}
            assert len(damgalar) == 1, (
                f"🔴 MDL KARIŞTI — tek dosyada {damgalar} damgaları bir arada:\n{metin}")


def test_KILIT_SUREC_ICI_de_SURECLER_ARASI_da():
    """⚠ İki kademe **ayrı sorunları** çözer ve biri diğerinin yerine geçmez: `threading.
    Lock` süreç-arası **hiçbir şey** yapmaz, `flock` ise aynı süreçteki iki thread için
    gereksiz bir sistem çağrısıdır."""
    import inspect

    kaynak = inspect.getsource(DerlemeKilidi)
    assert "threading.Lock()" in kaynak, "🔴 süreç-içi kademe yok"
    assert "fcntl.flock" in kaynak, "🔴 süreç-arası kademe yok"


def test_FCNTL_YOKSA_sessizce_DUSMUYOR():
    """🔴 *Sessizce düşürmek, kilidin var olmadığı bir ortamda "korunuyoruz" sanmak
    olurdu.* Süreci reddetmek ise orantısız: tek süreçli bir kurulumda iç kademe doğru
    ve yeterlidir — bu yüzden **gürültülü bir uyarı**."""
    kaynak = (_KOK / "app/compose.py").read_text(encoding="utf-8")
    i = kaynak.index("except ImportError")
    assert "_log.warning" in kaynak[i:i + 400], (
        "🔴 `fcntl` yokluğu loglanmıyor — koruma sessizce kayboluyor.")


def test_KILIT_HATA_ANINDA_da_BIRAKILIYOR():
    """🔴 Bırakılmayan bir kilit, dört worker'lık bir dağıtımı **tek worker'a** indirir —
    ve bu, bir hata olarak değil bir **yavaşlık** olarak görünür: teşhisi en zor arıza."""
    import inspect

    kaynak = inspect.getsource(DerlemeKilidi)
    assert "except BaseException" in kaynak, (
        "🔴 `__enter__` içinde kilit alınırken hata olursa yerel kilit BIRAKILMIYOR.")
    assert "finally:" in kaynak, "🔴 `__exit__` `finally` kullanmıyor"


def test_GUNICORN_dumani_OLCULMEDI_ve_YAZILI():
    """⊘ *Ölçemediğimiz kısmı ölçmüş gibi göstermek, kapıyı bir temenniye çevirir.*"""
    doc = __doc__ or ""
    assert "gunicorn" in doc and "gizlenmiyor" in doc
