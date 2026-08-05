"""METAMORFİK BAĞINTI KAPILARI — *aracın kendisi doğru mu?*

⚠ Bu dosya ürünün tutarlılığını **ölçmez** (o `lab/metamorfik.py --ornek` işidir);
aracın **kendi doğruluğunu** kapıya bağlar. *Ölçüm aracının kendisi de bir
bağımlılıktır* — bu deponun defterindeki en sık tekrar eden sınıf, ve bir kez daha
tekrarlanmasın diye alet de kapılı.
"""

from __future__ import annotations

import random

from lab import metamorfik as M


def test_HER_BAGINTI_iki_yonden_birini_beyan_eder():
    """Bir bağıntı ya `ayni` ya `farkli` bekler — üçüncüsü yok, boş da olamaz."""
    for b in M.BAGINTILAR:
        assert b.beklenti in ("ayni", "farkli"), f"{b.kod}: geçersiz beklenti"


def test_ZIT_AILE_var_yoksa_olcum_totolojidir():
    """🔴 **Bu dosyanın en önemli testi.**

    Yalnız *"cevap değişmemeli"* diyen bir süit, her soruya `durust_ret` diyen bir
    ürün tarafından **%100** geçilir. *Bir tutarlılık ölçüsü, sabit bir cevabı
    mükemmel sanır.* Negatif bağıntılar bu tuzağı kıran tek mekanizmadır — ve
    silinirlerse ölçüm sessizce anlamsızlaşır."""
    zit = [b for b in M.BAGINTILAR if b.beklenti == "farkli"]
    assert len(zit) >= 3, f"negatif bağıntı yetersiz: {len(zit)} — ölçüm totolojiye döner"


def test_DILSEL_AILE_var_yanlis_yolun_zayifligini_olcmeyelim():
    """🔴 Araştırma bulgusu: **yüzey gürültüsü** tek-geçişli hatları, **dilsel
    çeşitlilik** ajanik kurulumları vurur. Bizde iki yol da var; yalnız yüzey
    bozulması ölçmek, *yanlış yolun* zayıflığını ölçmek olurdu."""
    dilsel = [b for b in M.BAGINTILAR if b.aile == "dilsel"]
    assert len(dilsel) >= 4, f"dilsel bağıntı yetersiz: {len(dilsel)}"


def test_DONUSUMLER_soruyu_gercekten_degistirir():
    """Bir dönüşüm girdiyi değiştirmiyorsa **sessizce hiçbir şey ölçmez** — ve
    raporda `tutarlı` diye görünür. *Hiç uygulanmamış bir bağıntı, geçmiş bir
    bağıntıdan ayırt edilemez.*"""
    ornekler = [
        "bu ay müşteri bazında ciro ne kadar",
        "geçen yıl fire oranı neden arttı",
        "makine bazında oee en yüksek hangisi",
    ]
    uygulanan = {b.kod for q in ornekler for b in M.BAGINTILAR
                 if (yeni := b.donusum(q, random.Random(1))) and yeni != q}
    eksik = {b.kod for b in M.BAGINTILAR} - uygulanan
    # ⚠ Bazı bağıntılar örneğe bağlıdır (`z.olumsuz` olumsuzlanacak fiil ister) —
    # o yüzden tam kapsam beklenmez, ama YARIDAN çoğu uygulanabilmeli.
    assert len(uygulanan) >= len(M.BAGINTILAR) // 2, f"uygulanamayan: {eksik}"


def test_TURKCE_KLAVYE_kullanilir_ingilizce_degil():
    """⚠ Kullanıcı **Türkçe Q klavye** kullanıyor; `ı`/`ö`/`ç`/`ş`/`ğ`/`ü` tuşları
    İngilizce QWERTY'den farklı yerde. Yanlış klavyeyle üretilmiş bir yazım hatası,
    gerçekte **hiç yapılmayan** bir hatadır — *gerçekleşmeyen bir hatayı test etmek,
    gerçekleşeni test etmemektir.*"""
    assert set("çğıöşü") <= set(M._KLAVYE_TR), "Türkçe harfler klavye haritasında yok"
    assert "ı" in M._KLAVYE_TR["u"], "Türkçe Q düzeni değil (u'nun komşusu ı olmalı)"


def test_IMZA_anlamsiz_farki_yok_sayar():
    """İmza yalnız **anlam taşıyan** alanları alır. Ham sözlüğü kıyaslamak, açıklama
    metni/sıra gibi farkları da 'değişmiş' gösterip her türevi kırılgan yapardı."""
    a = {"cube_query": {"cube": "parti", "measures": ["toplam_ciro"], "aciklama": "A"}}
    b = {"cube_query": {"cube": "parti", "measures": ["toplam_ciro"], "aciklama": "B"}}
    assert M.imza(a) == M.imza(b), "anlamsız fark imzayı değiştirdi"
    c = {"cube_query": {"cube": "parti", "measures": ["toplam_fire_kg"]}}
    assert M.imza(a) != M.imza(c), "anlamlı fark imzada görünmüyor"
    assert M.imza(None) == ("PES",)


def test_UCUNCU_HAL_pes_tabanini_kusur_saymaz():
    """⊘ **ÖLÇÜLEMEDİ** — geçmek de kalmak da değil.

    🔴 İlk koşumda `z.olumsuz` **51/51**, `z.donem` **29/29** kusur verdi. Şüpheli
    bir bütünlüktü; sebebi taban `PES` iken türevin de `PES` olmasıydı. Sistem
    **hiçbirini cevaplamadı** — cevaplamadığı iki soruyu *"aynı cevabı verdi"* diye
    suçlamak ölçümü yalancı çıkarır."""
    src = (__import__("pathlib").Path(M.__file__)).read_text(encoding="utf-8")
    assert "olculemedi" in src and 'taban == ("PES",)' in src, \
        "üçüncü hâl kaldırılmış — negatif bağıntılar haksız kusur üretir"
    assert "payda = ölçülenler" in src or "olculen" in src, \
        "ölçülemeyen türevler paydadan çıkarılmıyor"
