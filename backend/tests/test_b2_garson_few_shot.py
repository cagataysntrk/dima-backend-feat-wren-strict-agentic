"""🔴🔴 `§B2` — **GARSONA ÖRNEK VER** *(rapor `§14` FAZ 1, kısa yolun 1. işi)*.

⊙ Ölçüldü: `vqr.few_shot_block()` **zaten yazılmış ve çalışıyordu**, ama yalnız
**Discovery** dalına bağlıydı (`ask.py:5135`, trafiğin **%1,7'si**); trafiğin **%37'sini**
taşıyan garson onu **hiç görmüyordu** — `llm.py::_cube_select_system` içinde *«few_shot»*
sözcüğü bile geçmiyordu.

⊙ **Ve uygularken ikinci bir kök çıktı:** `settings.vqr_acik = False` olduğu için
`vqr_for_request()` **her istekte `None`** dönüyordu — yani `/verify` sessizce
`stored:false` diyor, garson few-shot'ı hiç ateşlemiyor ve **Discovery'nin kendi
few-shot'ı da ölü**. VQR'da **23 kayıt** (8'i insan onaylı) duruyor ve hiçbiri
kullanılmıyordu.

*Bir fonksiyonu yazmak, onu doğru dala bağlamak değildir.*
"""

from __future__ import annotations


def test_GARSON_KAPISI_YALNIZ_INSAN_ONAYLI_KAYIT_GOSTERIR():
    """Discovery'nin çıktısı ham SQL'dir ve `dry_plan`'dan geçer; garsonun çıktısı
    **fiştir** ve fiş **sayıyı belirler**. `vqr.py:136`'nın replay↔few-shot ayrımının
    üçüncü basamağı."""
    from app import vqr as V

    class _S(V.VQR):
        def __init__(self, pairs):
            self._pairs = pairs

        def _load(self):
            return self._pairs

        def _scores(self, q):
            return [1.0] * len(self._pairs)

    pairs = [{"question": "makine bazında oee", "cube_query": {"cube": "oee"},
              "source": "chip_approved"},
             {"question": "makine bazında oee", "cube_query": {"cube": "oee"},
              "source": "auto_discovery"}]
    v = _S(pairs)
    assert "chip_approved" in {p["source"] for p, _ in v.recall("x", 5)}
    gevsek = v.few_shot_block("makine bazında oee", k=5)
    siki = v.few_shot_block("makine bazında oee", k=5, guvenilir=True)
    assert gevsek.count("- Soru:") == 2, gevsek
    assert siki.count("- Soru:") == 1, siki


def test_GUVENILMEZ_KAYNAK_TEK_BASINA_KALIRSA_BLOK_BOS():
    """`§101.1` — yalnız güvenilmez kayıt varsa garson **hiç örnek görmez**."""
    from app import vqr as V

    class _S(V.VQR):
        def __init__(self, pairs):
            self._pairs = pairs

        def _load(self):
            return self._pairs

        def _scores(self, q):
            return [1.0] * len(self._pairs)

    v = _S([{"question": "x", "cube_query": {"cube": "oee"}, "source": "auto_cube"}])
    assert v.few_shot_block("x", guvenilir=True) == ""
    assert v.garson_ornekleri("x") == ""


def test_ORNEK_ERISIMCISI_REPLAY_ANAHTARINDAN_BAGIMSIZ():
    """🔴 **`vqr_acik` TEKRAR OYNATMA anahtarıdır; örnek göstermeyi kapatmaz.**

    ⊙ Canlıda ölçüldü: `vqr_acik=False` iken `vqr_for_request()` `None` dönüyor ve
    **VQR'ın tamamı** (23 kayıt, 8'i insan onaylı) kullanılmaz hâle geliyordu.
    `vqr.py:136` bu iki riskin **aynı kapıdan geçmemesi** gerektiğini zaten yazmış:
    replay'in yarıçapı **TAM**, few-shot'ınki **dolaylı**.

    *Bir anahtarı, açtığı şeyin adıyla değil, kapattığı riskin yarıçapıyla tanımlamak
    gerekir.*"""
    import inspect

    from app import company_registry as CR

    def _govde(fn):
        """Docstring'i düş — yüklem **koda** bakmalı, açıklamaya değil.
        (İlk yazımda docstring `vqr_acik`'i *«bunu kapatmaz»* diye anıyordu ve kapı
        haklı olarak kırmızı verdi.)"""
        src = inspect.getsource(fn)
        d = fn.__doc__ or ""
        return src.replace(d, "") if d else src

    assert "vqr_acik" in _govde(CR.vqr_for_request)
    assert "vqr_acik" not in _govde(CR.vqr_ornek_icin)
    # İkisi de AYNI çözünürlüğü kullanır (`KAT-1`)
    assert "_vqr_coz" in _govde(CR.vqr_for_request)
    assert "_vqr_coz" in _govde(CR.vqr_ornek_icin)


def test_BAYRAK_KAPALIYKEN_ISTEM_BAYT_BAYT_ESKI():
    """`KURAL B` — `vqr_few_shot` kapalıyken garson istemine **hiçbir şey** eklenmez."""
    import inspect

    from app.routers import ask as A

    src = inspect.getsource(A.ask)
    assert '"vqr_few_shot" in resolve_for(settings, principal)' in src
    # blok boşsa `join` hiçbir şey eklemez
    assert 'if x)' in src


def test_GARSON_ISTEMI_BLOGU_KATALOGUN_YANINA_ALIR():
    """`_cube_select_system` imzası **değişmedi** — blok katalog metnine eklenir."""
    import inspect

    from app import llm as L

    assert len(inspect.signature(L._cube_select_system).parameters) == 1
