"""🔴 **OYLAMANIN PAYDASI** — çekimser oylar sayılmıyordu.

## Ölçülen kusur

`_select_consistent`: `cands = [c for c in ... if c]` → `agreement = len(best)/len(cands)`.
`{cube:null}` (*"bilmiyorum"*) oyları **paydadan düşüyordu**. 3 çağrının 1'i cevap, 2'si
bilmiyorum ise → **uyum 1,0**.

> Yani **şüphenin en yüksek olduğu durum, sistemin en emin göründüğü durumdu.**

`MIMARI`'nin açık kararı bunu yasaklıyor: *"kalibre edilmediği sürece o sayı bir güven
değil bir **süstür**."*

⚠ Çekimser bir **bilgidir**, gürültü değil: `{cube:null}` *"bu soru tek bir cube ile
yanıtlanamaz"* demektir. Onu paydadan düşürmek, hayır oylarını saymadan oy birliği ilan
etmektir.

## 🔴 Neden bayrak KAPALI

Karar eşiği (`>= 2/3`) **aynı orandan** geçiyor: payda büyüyünce bazı cevaplar
netleştirmeye düşer. Yön doğru (tahmin yerine soru — kullanıcının açık tercihi) ama
kapsam bedeli **bu koşumda ölçülemez**: `nl_corpus` tanımı gereği `rule` sağlayıcıyla
koşar, `eval --slice llm` **4 vaka**.

*Ölçülemeyen bir takası varsayılan yapmak, kullanıcı adına karar vermektir.*

**ÖN KOŞUL:** `eval --slice llm` büyüsün — `G3.2` ve `§AJ2` ile **aynı** alet borcu.
"""

from __future__ import annotations

import inspect

from app.routers import ask as ask_mod


def test_PAYDA_CEKIMSERLERI_DE_SAYABILIYOR():
    """Mekanizma var: ham oy listesi tutuluyor ve payda ondan seçilebiliyor."""
    src = inspect.getsource(ask_mod._select_consistent)
    assert "oylar = list(" in src, "🔴 ham oy listesi tutulmuyor — çekimser sayılamaz"
    assert "len(oylar) if _tam_payda else len(cands)" in src, (
        "🔴 payda seçimi yok — kusur ya hiç düzelmemiş ya bayraksız açılmış")


def test_VARSAYILAN_BUGUNKU_DAVRANIS():
    """`KURAL B`: bayrak kapalıyken hesap **bayt bayt bugünkü**."""
    src = inspect.getsource(ask_mod._select_consistent)
    assert '"oylama_paydasi"' in src
    assert "_tam_payda = False" in src, "🔴 çözülemezse AÇIK varsayılıyor — fail-open"


def test_BAYRAK_KAYITLI_ve_KAPALI():
    from app.features import FLAG_REGISTRY

    assert "oylama_paydasi" in FLAG_REGISTRY
    yml = (__import__("pathlib").Path(ask_mod.__file__).parents[2]
           / "demo/packs/features.yml").read_text()
    assert 'oylama_paydasi: "off"' in yml, (
        "🔴 açılmış — takas hâlâ ölçülemiyorsa bu bir karar değil bir tahmindir")


def test_IMZA_EN_DAR_KAPSAMA_GORE():
    """🔴 Bu turda aynı tuzağa bir kez düşüldü (`katalog_metni` zorunlu `settings` istedi,
    iki çağıranda o isim yoktu, `NameError` yutuldu). Ders burada uygulandı: bir oylama
    hesabı **kimlik bilmez**, bayrak global kapsamda çözülür."""
    src = inspect.getsource(ask_mod._select_consistent)
    assert "_rf4(get_settings(), None)" in src, (
        "🔴 `principal` kullanılmış — bu fonksiyonun kapsamında o isim YOK")
