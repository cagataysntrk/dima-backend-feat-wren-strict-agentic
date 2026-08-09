"""🔴 KAPININ KENDİ MALİYETİNİN KAPISI (2026-08-09).

## Neden bu dosya var

`belgeler/denetim/2026-08-09_KAPI-YAVASLAMASI-TESHISI.md` şunu ölçtü: korpus adımı
**1 dk 50 sn → 13 dk 00 sn** (7,1×) çıktı ve **kimse görmedi**. Sebep bir kusur değil,
bir **kapı boşluğuydu**:

> Bu depo modül **büyümesini** tavanla sınırlıyor (`test_modul_buyume.py`), ama
> **süre** için hiçbir tavan yok. `/ask` 47 ms'den 177 ms'ye çıkarken hiçbir kapı
> kırmızı vermedi.

*Ölçülmeyen bir boyut, sessizce gerileyen bir boyuttur.*

⚠ Bu dosya **süreyi ölçmez** — süre ölçen bir birim testi belirlenimsiz olurdu (makine
yükü, çekirdek sayısı). Ölçtüğü şey, **süreyi belirleyen KARARLARIN** doğruluğudur:
kaç adım koşuyor, dilimler nasıl bölünüyor, bir sabit bayatlayabilir mi.

🔴 Latency tavanının kendisi (medyan `/ask` > X ms → kırmızı) **ayrı bir iştir** ve
teşhis belgesinin Öneri 4'ünde duruyor: profil olmadan eşik seçmek, ölçmeden sabit
yazmaktır — yani bu dosyanın kapattığı kusurun ta kendisi.
"""

from __future__ import annotations

import json

import pytest

from lab import kapi


# ---------------------------------------------------------------- adım süzgeci


def test_TOPLU_KOSUMDA_BELIRLENIMSIZ_ADIM_YOK():
    """`--hepsi` gerçek sağlayıcı/ağ isteyen adımları koşmaz — **koduyla, belgesiyle değil**.

    Ölçülen kusur: `eval_llm`'in docstring'i *"Toplu koşuma girmez"* diyordu ama süzgeç
    tek elemanlı bir dizeye (`GARSON_TOPLUDA_YOK`) bağlıydı ve yalnız `garson`'u eliyordu.
    Canlı kütükte (`dima-kapi-z`, 03:29:38) **`▶ eval LLM dilimi` koşuyordu**.
    """
    hepsi = [a for a in kapi.ADIM_ANAHTARLARI if a not in kapi.TOPLUDA_YOK]
    assert "garson" not in hepsi, "garson `--hepsi`'ye sızdı — `--live` + kota ister"
    assert "eval_llm" not in hepsi, (
        "eval_llm `--hepsi`'ye sızdı — gerçek sağlayıcı ister ve BELİRLENİMSİZDİR; "
        "kendi docstring'i 'toplu koşuma girmez' diyor")


def test_TOPLUDA_YOK_GERCEK_ADIMLARI_ADLANDIRIR():
    """Kümedeki her ad gerçek bir adım olmalı — yazım hatası sessizce **hiçbir şey elemez**."""
    bilinmeyen = set(kapi.TOPLUDA_YOK) - set(kapi.ADIM_ANAHTARLARI)
    assert not bilinmeyen, f"TOPLUDA_YOK'ta bilinmeyen adım: {bilinmeyen}"


def test_ATLANAN_ADIMLAR_HALA_CAGRILABILIR():
    """Adımlar toplu koşumdan **çıkarıldı**, silinmedi (MIMARI §10)."""
    for ad in kapi.TOPLUDA_YOK:
        assert ad in kapi.ADIM_ANAHTARLARI, f"{ad} `--sadece` ile çağrılamaz hâle gelmiş"


def test_YEREL_KAPI_DARALMADI():
    """⚠ Bu dosyanın hızlandırmaları **yerel kapının kapsamına dokunmamalı**."""
    assert set(kapi.YEREL_KAPI) == {"korpus", "gercek"}, (
        "yerel demet kapısı değişmiş — hız için kapsam kırpmak bu depoda YASAK")


# ------------------------------------------------------- dilim dağılımı (payda)


@pytest.fixture
def dagit(monkeypatch, tmp_path):
    """`_dilim_dagilimi`'yi sahte bir raporla çağıran yardımcı."""
    from lab import nl_corpus

    rapor = tmp_path / "nl_corpus.json"
    monkeypatch.setattr(nl_corpus, "_RAPOR", rapor)

    def _cagir(kayitlar, paralel=16):
        if kayitlar is not None:
            rapor.write_text(json.dumps(kayitlar), encoding="utf-8")
        return nl_corpus._dilim_dagilimi(paralel)

    return _cagir


#: Teşhis belgesindeki ölçülmüş korpus (2026-08-09).
_TUR = {"boyahane": 9413, "atiksan": 1447, "gulteks": 1618, "gitas": 2479}
_YUK = {a: t * (2.2 if a == "boyahane" else 1.0) for a, t in _TUR.items()}


def _en_uzun(dagilim: dict[str, int]) -> float:
    """Duvar saatini belirleyen dilim — *toplam değil, EN UZUN.*"""
    return max(_YUK[a] / dagilim[a] for a in dagilim)


def test_DILIM_SAYISI_SURECLERI_TAM_DOLDURUR(dagit):
    """Süreçten çok dilim = kuyruk; az dilim = boş çekirdek. **Tam eşit** olmalı."""
    for paralel in (4, 8, 16):
        dagilim, _ = dagit([{"company": a, "sure_sn": s} for a, s in _YUK.items()], paralel)
        assert sum(dagilim.values()) == paralel, f"paralel={paralel}: {dagilim}"


def test_HICBIR_SIRKET_DUSMEZ(dagit):
    """🔴 **PAYDA KUTSALDIR.** Sıfır dilim = şirket korpustan düşer.

    Bu deponun en pahalı dersi: `gitas` bir compose yarışıyla düştü, payda **445→342**
    indi ve doğruluk **%93,2→%94,3'e ÇIKTI** — *sistem bozulurken sayı iyileşti.*
    """
    for paralel in (1, 2, 4, 16, 64):
        dagilim, _ = dagit([{"company": a, "sure_sn": s} for a, s in _YUK.items()], paralel)
        assert set(dagilim) == set(_TUR), f"şirket kaybı: {set(_TUR) - set(dagilim)}"
        assert all(n >= 1 for n in dagilim.values()), f"sıfır dilim: {dagilim}"


def test_EN_UZUN_DILIM_BAYAT_SABITTEN_KISA(dagit):
    """Ölçümden türetilen dağılım, elle yazılmış sabitten **daha iyi** olmalı.

    ⚠ Kıyas ölçütü **ortalama değil, EN UZUN dilim**: ilk yazımım payı iş yüküne
    *orantılı* dağıtıyordu ve kuru prova onu çürüttü — orantısal dağıtım bugünkünden
    **%8 KÖTÜ** çıkıyordu, çünkü ortalamayı iyileştirip makespan'i bozuyordu.
    *Yanlış büyüklüğü eniyileyen bir hızlandırma, bir yavaşlatmadır.*
    """
    from lab import nl_corpus

    yeni, kaynak = dagit([{"company": a, "sure_sn": s} for a, s in _YUK.items()], 16)
    assert kaynak.startswith("ÖLÇÜM")
    assert _en_uzun(yeni) < _en_uzun(nl_corpus._AGIR), (
        f"ölçümden türetilen dağılım {yeni} (en uzun {_en_uzun(yeni):.0f}), "
        f"bayat sabit {nl_corpus._AGIR} (en uzun {_en_uzun(nl_corpus._AGIR):.0f}) "
        "kadar bile iyi değil")


def test_OLCUM_YOKSA_YEDEGE_DUSER_KIRILMAZ(dagit):
    """🔴 Rapor **gitignore'lu bir artefakttır** — taze klonda/CI'da YOKTUR.

    Üç bozuk hâlin üçünde de kapı **koşmaya devam etmeli**: *bir hızlandırmanın arızası,
    ölçümün kendisini düşürmemelidir.*
    """
    from lab import nl_corpus

    # 1) rapor hiç yok  2) şirket eksik/hatalı  3) bozuk JSON
    for kayitlar in (None,
                     [{"company": "boyahane", "error": "patladı"}],
                     [{"company": "atiksan", "cats": {"x": 9}}]):
        dagilim, kaynak = dagit(kayitlar)
        assert dagilim == {a: min(nl_corpus._AGIR.get(a, 1), 16) for a in dagilim}
        assert "YEDEK" in kaynak, f"sessizce ölçüm iddia etti: {kaynak}"


def test_BOZUK_JSON_ISTISNA_YUKSELTMEZ(dagit, tmp_path, monkeypatch):
    """Okunamayan rapor bir **çizelgeleme ipucudur**, bir kapı değil."""
    from lab import nl_corpus

    rapor = tmp_path / "bozuk.json"
    rapor.write_text("{bu json değil", encoding="utf-8")
    monkeypatch.setattr(nl_corpus, "_RAPOR", rapor)
    dagilim, kaynak = nl_corpus._dilim_dagilimi(16)
    assert "YEDEK" in kaynak and sum(dagilim.values()) >= len(dagilim)


def test_ILK_KOSUM_SURE_YOKKEN_TUR_SAYISINI_KULLANIR(dagit):
    """`sure_sn` henüz yazılmamışken (ilk koşum) tur sayısı × ağırlık devreye girer."""
    dagilim, kaynak = dagit([{"company": a, "cats": {"x": t}} for a, t in _TUR.items()])
    assert kaynak.startswith("ÖLÇÜM")
    assert sum(dagilim.values()) == 16


def test_SERI_KOSUMDA_HER_SIRKET_TEK_DILIM(dagit):
    """`DIMA_KORPUS_PARALEL=1` geri alma yolu — bölme yok."""
    dagilim, kaynak = dagit([{"company": a, "sure_sn": s} for a, s in _YUK.items()], 1)
    assert kaynak == "seri" and set(dagilim.values()) == {1}


# ------------------------------------------------------------------ süre kaydı


def test_RAPOR_KENDI_SURESINI_KAYDEDER():
    """🔴 Ölçüm aracı **kendi maliyetini** de ölçmeli.

    Bayat `_AGIR` sabiti tam bu yüzden fark edilmedi: rapor doğruluğu ölçüyor, süreyi
    ölçmüyordu. *Kendi maliyetini ölçmeyen bir araç, pahalılaştığını da öğrenemez.*
    """
    from lab import nl_corpus

    dilimler = [{"company": "x", "cats": {}, "n_single": 0, "n_proc_steps": 0,
                 "sure_sn": 10.0},
                {"company": "x", "cats": {}, "n_single": 0, "n_proc_steps": 0,
                 "sure_sn": 30.0}]
    birlesik = nl_corpus.birlestir(dilimler)
    assert birlesik["sure_sn"] == 40.0, "iş yükü dilimlerin TOPLAMIdır"
    assert birlesik["sure_en_uzun_dilim_sn"] == 30.0, (
        "duvar saati en UZUN dilimdir — ikisini tek alana katlamak dengesizliği "
        "görünmez kılar")
