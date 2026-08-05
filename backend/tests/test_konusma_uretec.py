"""KONUŞMA ÜRETECİ KAPILARI — *akan sohbet ölçülebiliyor mu?*

Kullanıcı kuralı (2026-08-05): *"tek soru cevaplardan öte … thread mantığı follow
up'lar yani chatte 1 sordun cevap geldi üstüne bi şey daha bi şey daha gibi akan
mantıktaki gerçek dünya senaryoları."*

Bu dosya ürünü sınamaz — **üretecin kendi kapsamını** sınar. *Bir sohbet korpusunun
değeri, kaç sohbet ürettiğinde değil, hangi geçişleri kapsadığındadır.*
"""

from __future__ import annotations

import random

from lab import konusma_uretec as K


def test_GECIS_KAPSAMI_tam():
    """🔴 Her ardışık tur çifti en az bir sohbette görünmeli.

    17 tur × 8 derinlik = ~7 milyar dizi; hepsini üretmek imkânsız. Ölçü, **ikili
    geçişlerin** tamamı — çünkü bir bağlam kusuru tipik olarak iki ardışık turun
    etkileşiminden doğar. *Kapsanmayan bir geçiş, o geçişte yaşayan kusurun
    görünmez kalması demektir.*"""
    zincirler = K.gecis_kapsami(K.UZUNLUKLAR, random.Random(1))
    gorulen = {(a, b) for z in zincirler for a, b in zip(z, z[1:])}
    eksik = {(a, b) for a in K.TUR_TURLERI for b in K.TUR_TURLERI} - gorulen
    assert not eksik, f"kapsanmayan geçiş ({len(eksik)}): {sorted(eksik)[:8]}"


def test_DERINLIK_ayri_eksen():
    """⚠ *"Beşinci turda bağlam hâlâ duruyor mu"* sorusu iki turlu bir sohbette
    sorulamaz. Derinlik bu yüzden ayrı bir eksendir ve dördü de üretilmelidir."""
    zincirler = K.gecis_kapsami(K.UZUNLUKLAR, random.Random(2))
    boylar = {len(z) for z in zincirler}
    assert set(K.UZUNLUKLAR) <= boylar, f"eksik derinlik: {set(K.UZUNLUKLAR) - boylar}"
    assert max(boylar) >= 8, "uzun sohbet üretilmiyor — bağlam ömrü ölçülemez"


def test_BAGLAM_SINIFLARI_cakismaz():
    """Bir tur hem bağlamı değiştiren hem koruyan olamaz — çelişkili bir beklenti,
    ölçümü her iki yönde de haklı çıkarır ve hiçbir şey ölçmez."""
    assert not (K.BAGLAM_DEGISTIREN & K.BAGLAM_KORUYAN)
    assert K.BAGLAM_DEGISTIREN <= set(K.TUR_TURLERI)
    assert K.BAGLAM_KORUYAN <= set(K.TUR_TURLERI)


def test_NEGATIF_BAGINTI_var():
    """🔴 *"Sıra önemlidir"* ve *"konu değişince bağlam değişir"* bağıntıları,
    tek-soru korpusundaki **negatif bağıntıların** sohbetteki karşılığıdır.

    Onlarsız, **her turu görmezden gelen** bir ürün tüm testleri geçer: her takip
    turuna ilk raporu tekrar verirse bütün *"aynı kalmalı"* bağıntıları sağlanır.
    *Bir tutarlılık ölçüsü, sabit bir cevabı mükemmel sanır.*"""
    farkli = [k for k, _a, b in K.SOHBET_BAGINTILARI if b == "farkli"]
    assert len(farkli) >= 2, f"negatif sohbet bağıntısı yetersiz: {farkli}"
    assert "s.sira_onemli" in farkli


def test_HER_TUR_TURUNUN_metni_var():
    """Metni olmayan bir tur türü, üretimde sessizce `KeyError` verir ya da atlanır —
    ikisi de kapsamı **beyan edilenden küçük** yapar."""
    disaridan = {K.T_ACILIS, K.T_KONU_DEGIS, K.T_IC_ICE}   # metni tekil korpustan gelir
    for t in K.TUR_TURLERI:
        if t in disaridan:
            continue
        assert t in K._KALIPLAR, f"tur metni yok: {t}"
        assert len(K._KALIPLAR[t]) >= 4, f"{t}: kalıp çeşitliliği düşük"


def test_ILK_TUR_BAGLAMSIZ_TAKIP_durust_ret_bekler():
    """⚠ *Aynı cümle, bulunduğu yere göre farklı doğru cevaba sahiptir.*

    Sohbetin ilk turunda *"neden?"* demek bağlamsızdır → **dürüst ret**. Aynı tur
    beşinci sırada geldiğinde cevap beklenir. Bu ayrımı yapmayan bir korpus, ürünü
    haksız yere ya cömert ya cimri gösterir."""
    from lab.senaryo_uretec import DURUST_RET

    assert DURUST_RET in K._kabul(K.T_NEDEN, 0)
    assert DURUST_RET not in K._kabul(K.T_KIRILIM, 3)


def test_SOSYAL_TUR_baglami_korur_beklentisi():
    """🔴 Ölçülmüş kusur sınıfı: *"teşekkürler"* bir veri sorusu sanılıp
    `llm:gemini`'ye gidiyor ve **uydurma SQL** üretiyordu (Faz D1). Sosyal edim
    **dolgudur**; araya girmesi raporu düşürmemeli."""
    b = K._beklenen_baglam(K.T_SOSYAL, {"cube": "parti", "olcu": "ciro"}, None)
    assert b["degisti"] is False
    assert "dolgu" in b.get("not", "").lower()


def test_IC_ICE_istek_uretilir():
    """🔴 Kullanıcı kuralı: *"iç içe birden fazla şey isteyen sorular"*.

    Doğru cevap tek bir şey **değildir**: ürün ya ikisini de yapmalı ya *"önce
    hangisi"* diye sormalı. Sessizce birini seçip ötekini düşürmek yasaktır."""
    tekil = [{"soru": "bu ay ciro", "cube": "parti", "olcu_ifade": "ciro"},
             {"soru": "geçen ay fire oranı", "cube": "kalite", "olcu_ifade": "fire"}]
    metin = K._ic_ice(tekil, random.Random(3))
    assert any(x in metin for x in (" ve ", "bir de", "ayrıca", "sonra", "eğer"))
    assert K._yasak(K.T_IC_ICE).count("SESSİZCE") == 1
