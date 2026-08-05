"""EKİLİ OLAY KAPILARI — *ground truth bir yorum değil, bir sorgu.*

Bu dosya olayların **veride** olup olmadığını sınamaz (o `genislet()`'in kendi
doğrulaması); **manifestin kendi tutarlılığını** sınar. Manifest bozuksa ölçüm
kurulamaz ve testler ürünü haksız yere suçlar.
"""

from __future__ import annotations

from demo import olaylar as OL


def test_BUYUKLUK_esigi_insightbench():
    """🔴 InsightBench'in ölçtüğü sınır: **eğimi 0,1'in altındaki trendleri hiçbir
    model yakalayamıyor.**

    Yani çok küçük ekilen bir olay *"sistem bulamadı"* değil **"ölçüm kurulamadı"**
    demektir — ve bu ikisini karıştırmak ürünü kendi kusuru olmayan bir şey için
    suçlar. Alt sınır **2,0×** (yani en az %100 artış)."""
    kucuk = [(o.kod, o.buyukluk) for o in OL.OLAYLAR if o.buyukluk < 2.0]
    assert not kucuk, f"🔴 ölçülemeyecek kadar küçük ekilen olaylar: {kucuk}"


def test_OLAYLAR_ayni_pencerede_CAKISMAZ():
    """⚠ Aynı tür iki olay aynı pencerede aynı hedefe ekilirse, *"hangisi sebep"*
    sorusunun **iki** doğru cevabı olur — ve iki doğru cevaplı bir soru ölçülemez.
    *Aynı anda iki şey ekmek, ikisini de ölçülemez yapar.*"""
    for i, a in enumerate(OL.OLAYLAR):
        for b in OL.OLAYLAR[i + 1:]:
            if a.tur != b.tur or a.hedef_deger != b.hedef_deger:
                continue
            cakisma = not (a.bitis < b.baslangic or b.bitis < a.baslangic)
            assert not cakisma, f"🔴 çakışan olay: {a.kod} ↔ {b.kod}"


def test_HER_OLAY_dogrulama_SQLi_tasir():
    """Doğrulama SQL'i olmayan bir olay, **kanıtsız bir iddiadır**: testin
    karşılaştıracağı bir gerçek yoktur."""
    for o in OL.OLAYLAR:
        assert "SELECT" in o.dogrulama_sql.upper(), f"{o.kod}: doğrulama SQL'i yok"
        assert o.kok_neden and len(o.kok_neden) > 25, f"{o.kod}: kök neden yetersiz"
        assert o.sorular, f"{o.kod}: bu olayı bulması gereken soru yazılmamış"


def test_HER_OLAY_gercek_kullanici_sorusu_tasir():
    """⚠ Bir olayın değeri, onu **ortaya çıkaracak sorunun** yazılmasındadır.
    Sorusuz bir olay veride durur ama hiçbir test ona ulaşamaz."""
    for o in OL.OLAYLAR:
        assert len(o.sorular) >= 3, f"{o.kod}: soru çeşitliliği düşük"
        # Sorular KATALOG DİLİYLE değil kullanıcı diliyle olmalı — en az biri
        # tam cümle/konuşma dili taşımalı.
        assert any(len(q.split()) >= 4 for q in o.sorular), \
            f"{o.kod}: sorular fazla kısa — gerçek kullanıcı cümlesi değil"


def test_ZINCIR_SENARYOLARI_cok_turlu():
    """🔴 *Bir kök-neden sorusu tek turda cevaplanmaz; bir sohbette ortaya çıkar.*

    Her olayın `zincir`'i, kullanıcının o sebebe **hangi turlardan geçerek**
    varacağını yazar — ve testin onu bir sohbette araması gerektiğini söyler."""
    senaryolar = OL.zincir_senaryolari()
    assert len(senaryolar) >= 5, f"zincir senaryosu az: {len(senaryolar)}"
    for s in senaryolar:
        assert len(s["turlar"]) >= 3, f"{s['olay']}: zincir çok kısa"
        assert s["beklenen_kok_neden"] and s["dogrulama_sql"]


def test_CARPAN_pencere_disinda_etkisiz():
    """Olay penceresi dışında çarpan **1,0** olmalı — aksi hâlde olay tüm veriye
    yayılır ve *"ne zaman oldu"* sorusu cevapsız kalır."""
    from datetime import date

    o = OL.OLAYLAR[0]
    assert OL.carpan(o.tur, o.baslangic, o.hedef_deger) > 1.0
    assert OL.carpan(o.tur, date(2020, 1, 1), o.hedef_deger) == 1.0
    assert OL.carpan(o.tur, o.baslangic, "OLMAYAN-HEDEF") == 1.0
