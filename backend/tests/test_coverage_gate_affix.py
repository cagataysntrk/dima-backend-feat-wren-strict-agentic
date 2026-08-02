"""FAZ 0.4 — kapsam kapısının ek-farkındalığı: SESSİZ-YANLIŞ regresyon kilitleri.

`_uncovered` (ADR-0008 "anlamadığını bil" kapısı) bir kelimeyi "tanınmış" saymak için
`known in word` — yani HERHANGİ BİR KONUMDA alt-dizi — kullanıyordu. Türkçe eklemeli bir
dildir; ek SONA gelir. Konum serbest bırakılınca kapı delindi ve sistem, anlamadığı
kelimeleri anladığını sanıp cevap üretti.

Kanıtlanmış vakalar (hepsi canlı `route()` üzerinde çalıştırılarak doğrulandı):

    "firesiz partilerin cirosu"       → measures=[toplam_fire_kg]   ← sorulanın TAM TERSİ
    "reddedilmeyen partilerin cirosu" → filtresiz toplam_ciro        ← reddedilenler DAHİL
    "sapmasiz partiler"               → ort_renk_sapmasi
    "ankara icin kar"                 → kar, ANKARA FİLTRESİ SESSİZCE DÜŞMÜŞ
    "veresiye satislar"               → tüm satışlar (veresiye "ver" dolgusuna yutuldu)

Hepsi `source="cube"` rozetiyle, Query Contract'ıyla ve chip'leriyle geliyordu — yani
sistemin üretebileceği EN KÖTÜ hata sınıfı: tam yetkiyle sunulan yanlış sayı.

Düzeltme iki ayrı mekanizmadır ve bilinçli olarak AYRI tutulmuştur:
  * `_covers()`  — bilinen kelime ⊕ soru kelimesi: önek + olumsuzluk-eki reddi + geçerli
                   ek zinciri. (Biçimbirim sorunu.)
  * `_STOP_EXACT` — elle kısaltılmış dolgu köklerinden gerçek iş kelimelerini yutanlar.
                   (Sözlük sorunu; kanıta dayalı, denetlenebilir liste.)
"""

from __future__ import annotations

import pytest

from app.cube_router import _covers, _is_stop_word, _uncovered

# --- (a) alt-dizi körlüğü: ek BAŞA gelmez -----------------------------------

@pytest.mark.parametrize("known,word", [
    ("kar", "ankara"),        # şehir adı, kâr değil
    ("mal", "imalat"),
    ("son", "personel"),      # "son 6 ay" + "personel" → asıl çapraz-alan vakası
    ("gun", "uygun"),
    ("kar", "kargo"),
])
def test_bilinen_kelime_ortasinda_gecerse_KAPSAMAZ(known: str, word: str):
    assert not _covers(known, word), f"{known!r} {word!r} kelimesini kapsamamalı"


# --- (b) olumsuzluk ekleri çekim değil, NİYET operatörüdür -------------------

@pytest.mark.parametrize("known,word", [
    ("fire", "firesiz"),          # fire YOK demek
    ("sapma", "sapmasiz"),
    ("kar", "karsiz"),
    ("reddedil", "reddedilmeyen"),
    ("odenmis", "odenmemis"),
])
def test_olumsuzluk_eki_KAPSAMAZ(known: str, word: str):
    """Faz 3.3'te bu ekler `neq`/`not_in` üretecek. O zamana kadar kapsanmamış sayılıp
    dürüst redde/LLM'e düşmeleri tek doğru davranış — sessizce TERS metriği döndürmek
    değil."""
    assert not _covers(known, word)


# --- (c) meşru Türkçe çekimler KORUNMALI ------------------------------------

@pytest.mark.parametrize("known,word", [
    ("ciro", "cirosu"), ("ciro", "cirosunu"),
    ("makine", "makineler"), ("makine", "makinelerin"),
    ("renk", "renklerine"),
    ("oee", "oeeyi"),                       # "oee'yi" → _norm kesme işaretini siler
    ("verim", "verimliligi"), ("verim", "verimlilikleri"),
    ("musteri", "musterilere"), ("musteri", "musterininkileri"),
    ("cins", "cinsleri"), ("hafta", "haftanin"), ("gun", "gunu"),
    ("fire", "firenin"), ("kar", "kari"),
])
def test_mesru_cekim_KAPSANIR(known: str, word: str):
    assert _covers(known, word), f"{known!r} → {word!r} meşru çekim, kapsanmalı"


def test_maliyet_mal_ile_kapsanmaz_ama_ek_zinciri_bozulmaz():
    """"mal"+"iyeti" bir çekim değil ("yet" Türkçe ek değildir), farklı bir sözcüktür.

    Bu vaka ek-zinciri kuralının ayarını korur: `ti`/`tu` atom olarak eklenirse "iyeti"
    i+ye+ti diye ayrışır ve delik geri açılır (bir kez denendi ve geri alındı).
    """
    assert not _covers("mal", "maliyeti")
    assert _covers("mal", "mallar")          # gerçek çekim etkilenmemeli


# --- (d) dolgu kökleri gerçek iş kelimelerini yutmamalı ---------------------

@pytest.mark.parametrize("word", ["veresiye", "tekstil", "turuncu", "sanayi", "getiri"])
def test_dolgu_koku_gercek_is_kelimesini_YUTMAZ(word: str):
    assert not _is_stop_word(word), f"{word!r} dolgu sayılıyor — kapsam kapısı deliniyor"


@pytest.mark.parametrize("word", ["goster", "gosterir", "bazinda", "hesapla", "cinsleri",
                                  "grafik", "grafigi", "ver", "tek"])
def test_gercek_dolgu_dolgu_kalir(word: str):
    """Regresyon: `_STOP_STEMS` girdileri sözcük kökü DEĞİL, elle kısaltılmış eşleşme
    köküdür ("grafi" → grafik/grafiği). Onlara biçimbirim kuralı uygulamak grafik isteyen
    her soruyu kapsam kapısına takıyordu — bir kez denendi ve geri alındı."""
    assert _is_stop_word(word)


# --- (e) uçtan uca: kapı artık doğru kelimeyi işaret ediyor -----------------

@pytest.mark.parametrize("q,known,beklenen", [
    ("ankara icin kar", {"kar"}, ["ankara"]),
    ("firesiz partilerin cirosu", {"fire", "parti", "ciro"}, ["firesiz"]),
    ("veresiye satislar", {"satis"}, ["veresiye"]),
    ("turuncu partiler", {"parti"}, ["turuncu"]),
    # ASIL ÇAPRAZ-ALAN VAKASI: eskiden "son" (son 6 ay) "personel"i SAHTE kapsıyordu.
    ("son 6 ayda personel bazinda verim", {"son", "ayda", "verim"}, ["personel"]),
    # tamamı tanınan soru: hiçbir şey düşmemeli
    ("makinelerin cirosu", {"makine", "ciro"}, []),
    ("renklerine gore aylik ciro", {"renk", "aylik", "ciro"}, []),
])
def test_uncovered_dogru_kelimeyi_isaret_eder(q: str, known: set, beklenen: list):
    assert _uncovered(q, known) == beklenen


# --- (f) BİLİNEN SINIR: 2 harflik tanınan kökler gürültü tabanının altında --

def test_bilinen_sinir_iki_harflik_kok_kapsama_saymaz():
    """`_uncovered` `known`'ı `len >= 3` ile süzer, yani 2 harflik tanınan kökler
    ("ay", "kg", "tl") kapsama SAYILMAZ.

    Sonuç: `"son 6 ayda ..."` sorusunda tanınan kök yalnız `"ay"` ise `"ayda"` kelimesi
    kapsanmamış görünür ve kapı gereksiz yere kapanır. Canlı akışta `_period_hit_words()`
    eşleşen dönem ifadesinin TAM metnini ("son 6 ayda") kelimelerine ayırarak eklediği
    için pratikte nadiren tetiklenir — bu yüzden Faz 0.4 kapsamında BİLİNÇLİ olarak
    ele alınmadı (eşiği düşürmek 2 harflik kazara eşleşmeleri geri açar; doğru çözüm
    dönem/gran sözlüklerinin tam ifadeyi eklemesini garanti etmektir).

    Bu test bir HATA raporu değil, sınırın KAYDIDIR: davranış değişirse burada görünür.
    """
    assert _uncovered("son 6 ayda ciro", {"son", "ay", "ciro"}) == ["ayda"]
    assert _uncovered("son 6 ayda ciro", {"son", "ayda", "ciro"}) == []
