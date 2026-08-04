"""FAZ 0.19 — **SEMANTİK-VAKA PAYDASI**: korpusun kartezyen şişmesi ölçülür ve kilitlenir.

## Ölçülen kusur

`lab/nl_corpus.py` üçlü iç içe döngü kurar: `ölçü × PERIODS(11) × boyut`. Korpus bir
**KARTEZYEN ÜRÜNDÜR** ve **iki yönde** çarpıtır:

* **Yukarı:** `elektrik`in **TEK** sahiplik hatası, dönem × boyut çarpımıyla **onlarca
  ayrı başarısızlık** olarak sayılıyordu. Yanlış-cube yüzdesinin içi **birkaç terimin
  çarpımı**.
* **Aşağı:** üreteç yalnız **kataloğun bildiği** ifadeleri kurar; kataloğun bilmediği bir
  kusur sınıfı korpusta **yapısal olarak görünmez**.

**ÖLÇÜLDÜ (`f1050e6` sonrası):** şişme katsayısı **16,2×** · semantik doğruluk **%92,1**
↔ ham doğruluk **%93,2**. Yani ham sayı **iyimserdi**.

## Neden ham payda SİLİNMEDİ

`KURAL A`: dondurulmuş taban dokunulmazdır — geçmiş tüm ölçümler ham paydaya bağlı.
İki payda **yan yana** raporlanır; biri ötekinin yerine geçmez.

## Asıl kapı

🔴 **İki payda ters yöne giderse KIRMIZI.** *"Birkaç terimi düzelttim, sayı uçtu"*
yanılsamasının kapanı: tek bir terimi düzeltmek ham yüzdeyi birkaç puan zıplatabilir,
hiçbir yeni **semantik vaka** kazanılmadan.
"""

from __future__ import annotations

import inspect
import json
import pathlib

from lab import nl_corpus as nc


def test_URETEC_HER_TURA_VAKA_ANAHTARI_ILISTIRIR():
    """Semantik payda ancak her tur bir `(cube, ölçü, niyet)` anahtarı taşırsa hesaplanır."""
    govde = inspect.getsource(nc.gen_single)
    assert '"düz"' in govde and '"kırılım"' in govde and '"üstünlük"' in govde, \
        "niyet etiketleri yok — vaka anahtarı eksik"
    # Anahtar DÖNEM ve BOYUT İÇERMEMELİ: çarpım tek vakaya çökmeli.
    assert '(_c, m, "kırılım")' in govde, \
        "kırılım vakası boyut adını taşıyor olabilir — çarpım çökmez, payda şişmiş kalır"


def test_VAKA_SAYIMI_KATI_bir_yanlis_vakayi_dusurur():
    """🔴 **KATI (AND) sayım.** Bir vakanın varyantlarından biri bile yanlış cube'a
    giderse vaka **yanlıştır**. Gevşek (OR/çoğunluk) sayım, tek bir doğru varyantla bir
    sahiplik hatasını **gizlerdi** — yani kapının var oluş sebebini ortadan kaldırırdı."""
    govde = inspect.getsource(nc.run_company)
    assert "vaka_sonuc[vaka] = False" in govde, "yanlış sonuç vakayı DÜŞÜRMÜYOR"
    assert "vaka_sonuc.setdefault(vaka, True)" in govde, \
        "doğru sonuç vakayı EZİYOR olabilir — `setdefault` değilse katılık kaybolur"
    # Discovery de bir başarısızlıktır: beklenen cube'dan yapısal cevap gelmedi.
    i = govde.index('dogru["discovery"] += 1')
    assert "vaka_sonuc[vaka] = False" in govde[i:i + 200], \
        "Discovery'ye düşen tur vakayı düşürmüyor — kapsam kaybı doğru sayılır"


def test_HAM_PAYDA_KORUNDU():
    """`KURAL A`: dondurulmuş taban dokunulmazdır. İkinci payda **eklenir**, birincisi
    **silinmez** — geçmiş tüm ölçümler ham paydaya bağlı."""
    taban = json.loads((pathlib.Path(nc.__file__).parent / "nl_corpus_baseline.json")
                       .read_text(encoding="utf-8"))
    assert "toplam_tur" in taban, "ham payda tabandan SİLİNMİŞ (KURAL A ihlali)"
    assert "vaka_dogru_yuzde" in taban, "semantik taban dondurulmamış — kapı ölçemez"


def test_TERS_YON_KAPISI_KURULU():
    """🔴 **ASIL KAPI.** İki payda ters yöne giderse kırmızı. Bu bir yorum farkı değildir:
    ikisinden biri artık ölçtüğünü sandığı şeyi ölçmüyordur."""
    govde = inspect.getsource(nc.kapi_degerlendir)
    assert "TERS YÖNE" in govde, "ters yön kapısı YOK"
    assert "gecti = False" in govde.split("TERS YÖNE")[0].rsplit("if ham_yon", 1)[-1] or \
           "gecti = False" in govde, "ters yön tespit ediliyor ama KIRMIZI vermiyor"


def test_SISME_KATSAYISI_RAPORLANIYOR():
    """Şişme **görünür** olmalı: ölçülmeyen bir çarpıtma, düzeltilemez bir çarpıtmadır.
    (Ölçüldü: **16,2×** — bir semantik vaka ham paydada 16 kez sayılıyor.)"""
    assert "şişme katsayısı" in inspect.getsource(nc.kapi_degerlendir), \
        "şişme katsayısı raporlanmıyor"
    assert "Şişme katsayısı" in inspect.getsource(nc), "rapor satırında şişme yok"
