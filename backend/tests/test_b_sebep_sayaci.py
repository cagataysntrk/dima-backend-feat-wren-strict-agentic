r"""🔴 `§B.6/①` — **KESMENİN SEBEBİ SAYILIYOR; PAYDA DEĞİŞMİYOR.**

`§B.1` ölçtü: çok sahipli bir terimde `route()` **çekiliyor**. `§B.4` sebebi
**adlandırdı** (`Niyet.cekilme_sebebi`). Ama **sayılmıyordu** — *«garsonun yükünün
%kaçı belirsizlikten»* sorusu cevapsızdı.

✅ `lab/nl_corpus.py` artık **yalnız kesilen turda** sebebi hesaplayıp `sebep::<x>`
kovasına yazıyor.

## 🅜 PAYDA KUTSALDIR — bu değişikliğin **tek gerçek riski**

Korpusun tek gerçek yakalaması (`gitas` düştü → payda **445→342** → doğruluk
**YÜKSELDİ**) paydanın **sabitliğine** dayanır. Yeni bir kova **ayrı bir ad-uzayıdır**
ve `kesme_toplam`/`vaka_toplam` sayaçlarına **dokunmaz**; bu kapı onu **yapısal** olarak
doğrular.

> *Bir ölçüme kova eklemek, paydasına dokunmadıysa bir zenginleşmedir; dokunduysa bir
> gerilemedir ve iyileşme gibi görünür.*
"""

from __future__ import annotations

import ast
import inspect
import pathlib

_KOK = pathlib.Path(__file__).resolve().parents[1]


def _kaynak() -> str:
    return (_KOK / "lab" / "nl_corpus.py").read_text(encoding="utf-8")


def test_SEBEP_KOVASI_VAR():
    """🔴 **ASIL KAPI.** Sayaç yoksa `§B.4`'ün adlandırması bir süs kalır."""
    assert 'cats[f"sebep::' in _kaynak(), (
        "🔴 kesme sebebi SAYILMIYOR — `Niyet.cekilme_sebebi` adlandırıldı ama korpusta "
        "kovası yok; *bir boşluğu saymak için önce ona bir ad vermek gerekir, ama ad "
        "tek başına sayı değildir.*")


def test_SEBEP_YALNIZ_KESILEN_TURDA_HESAPLANIYOR():
    """⚠ **MALİYET.** Her soruda `niyet.coz` çağırmak korpusu yavaşlatırdı ve ölçmek
    istediğimiz popülasyon zaten **kesilenler**. Yüklem yapısal: sebep bloğu
    `_cevapsiz_kesme` dalının **içinde** olmalı."""
    k = _kaynak()
    i = k.index("if _cevapsiz_kesme(d):")
    j = k.index('cats[f"tekil::', i)
    dal = k[i:j]
    assert 'cats[f"sebep::' in dal, (
        "🔴 sebep sayacı kesme dalının DIŞINDA — her soruda `niyet.coz` çağrılıyor "
        "olabilir; korpus yavaşlar ve popülasyon yanlış olur.")


def test_PAYDA_SAYACLARINA_DOKUNULMUYOR():
    """🔴🔴 🅜 **PAYDA KUTSALDIR.** Yeni kova, payda sayaçlarını **artırmamalı**.

    Yüklem `ast` üstünde: `kesme_toplam` / `vaka_toplam` yalnız kendi yerlerinde
    artırılıyor mu, sebep bloğu onlara dokunuyor mu.
    """
    # ⚠ **İLK YÜKLEMİM YORUMU ÖLÇTÜ** ve yanlış kırmızı verdi (⟳ ders ㉚/🅐): blokta
    # geçen `kesme_toplam` bir **yorumdaki** kelimeydi, bir atama değil. Bu, deponun
    # `test_d7`/`test_e7`'de iki kez ölçtüğü kusurun aynısı.
    # ✅ Yüklem artık `ast` üstünde: yalnız **gerçek atama/artırma** hedefleri sayılır.
    agac = ast.parse(_kaynak())
    dokunulan: set[str] = set()
    for n in ast.walk(agac):
        if not isinstance(n, ast.If):
            continue
        _t = n.test
        if not (isinstance(_t, ast.Call) and getattr(_t.func, "id", "") == "_cevapsiz_kesme"):
            continue
        for m in ast.walk(n):
            hedefler = ([m.target] if isinstance(m, ast.AugAssign)
                        else list(m.targets) if isinstance(m, ast.Assign) else [])
            for h in hedefler:
                kok = h
                while isinstance(kok, ast.Subscript | ast.Attribute):
                    kok = kok.value
                if isinstance(kok, ast.Name):
                    dokunulan.add(kok.id)
    assert dokunulan, "⊘ ölçüm tabanı çöktü: kesme dalı bulunamadı"
    kotu = dokunulan & {"kesme_toplam", "vaka_toplam", "vaka_dogru", "singles"}
    assert not kotu, (
        f"🔴 sebep bloğu payda sayaç(lar)ına DOKUNUYOR: {sorted(kotu)} — bir kova "
        "eklemek paydayı değiştirdiyse, ölçüm zenginleşmedi **bozuldu**.")


def test_OLCUM_COKERSE_KORPUS_DUSMUYOR():
    """⚠ `ADR-0020` disiplini: bir **ölçüm** aracı, ölçtüğü koşumu düşürmemeli.
    Sebep hesabı patlarsa kova `olculemedi` alır ve tur devam eder."""
    k = _kaynak()
    i = k.index("if _cevapsiz_kesme(d):")
    j = k.index('cats[f"tekil::', i)
    dal = k[i:j]
    assert "except Exception" in dal and "olculemedi" in dal, (
        "🔴 sebep hesabı korunmasız — bir istisna bütün korpus koşumunu düşürebilir.")


def test_NIYET_SEBEBI_HALA_KAPALI_KUME():
    """⚠ Zincir: kova, `Niyet`'in **kapalı** sebep kümesinden besleniyor. Küme açık uçlu
    bir dizeye dönerse kova sayılamaz hâle gelir (`ADR-0008`)."""
    from app.niyet import Niyet

    kapali = {Niyet.SEBEP_COK_SAHIP, Niyet.SEBEP_BILINMEYEN, Niyet.SEBEP_OLCU_YOK}
    assert len(kapali) == 3
    assert "cekilme_sebebi" in dict(inspect.getmembers(Niyet))


def test_KAYNAK_AYRISTIRILABILIR():
    """⊘ Ölçüm tabanı: dosya bozulduysa yukarıdaki metin yüklemleri anlamsızdır."""
    ast.parse(_kaynak())
