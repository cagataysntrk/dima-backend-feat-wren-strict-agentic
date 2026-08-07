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
    # ⟳ ÇAPA KAYDI: liste artık `submit`/`result(timeout=)` ile **tek tek** toplanıyor
    # (Intent bütçesi, §22.5/N). Aşan oy `None` olarak listeye girer — yani çekimserle
    # **aynı** muamele görür ve payda doğruluğu korunur. Kapı gevşetilmedi: ölçtüğü şey
    # hâlâ *"ham oy listesi tutuluyor mu"*.
    assert "oylar = []" in src and "oylar.append(" in src, (
        "🔴 ham oy listesi tutulmuyor — çekimser sayılamaz")
    assert "TimeoutError" in src, "🔴 Intent bütçesi yok — aşan oy sonsuz bekler"
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


def test_BUTCE_SON_TARIH_OY_BASINA_PAY_DEGIL():
    """🔴 **Canlı ölçüm ilk tasarımı çürüttü** (`§27.2`).

    `intent_azami_saniye=20` konulu hâlde tek çağrı **47.544 ms** sürdü, istek
    **49.782 ms**. Sebep: her oy için ayrı `result(timeout=azami)` çağrılıyordu ve her
    çağrı **kendi anından** saymaya başlıyordu — ilk oy 7,6 sn sürünce ikinciye **20 sn
    daha** tanınıyordu.

    *Bir bütçeyi parça başına vermek, bütçeyi parça sayısıyla çarpmaktır.*

    ⚠ Son tarih **gönderimden önce** hesaplanmalı: `submit`'ten sonra hesaplamak, iş
    kuyrukta beklerken geçen süreyi bütçenin dışında bırakırdı.
    """
    import inspect

    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod._select_consistent)
    assert "_bitis = _time.monotonic() + _intent_azami" in src, (
        "🔴 bütçe hâlâ oy başına — toplam süre sınırsız kalır")
    assert "_bitis - _time.monotonic()" in src, "🔴 kalan süre hesaplanmıyor"
    i_bitis, i_submit = src.index("_bitis ="), src.index("ex.submit(one")
    assert i_bitis < i_submit, (
        "🔴 son tarih gönderimden SONRA hesaplanıyor — kuyruk süresi bütçe dışı kalır")
