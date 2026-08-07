

# --- 🔴 DA-2 — ALETİN KENDİ KÖRLÜĞÜ ------------------------------------------------


def test_HER_SATIR_EN_AZ_BIR_SENARYODA_OLCULUYOR():
    """🔴 **Ölçülmemiş ile başarısız aynı görünüyordu.**

    `TUM_SATIRLAR` on satır ilan ediyor ve rapor onları basıyor. Ama `1·çapa` · `2·anlat`
    · `4·sosyal` · `7·geri dönüş` **hiçbir senaryonun** `olculen`'inde yoktu → sekiz canlı
    raporun sekizinde de `0|0|0`. Bir denetim ajanı yakaladı.

    En ağırı `2·anlat`: `G5` `t2_anlatici`'yi **açtıktan sonra da** 0 kaldı — fazın amiral
    yeteneği kendi kapısında görünmezdi. Ve `G0.12`'nin kırmızı çizgisi (*"t2 açık/kapalı
    farklı çıkmalı; çıkmıyorsa alet KÖR, `G1` başlamaz"*) bu yüzden fiilen sınanamadı.

    *Bir satırı raporlamak, onu ölçmek değildir — ve raporlanan ölçülmemiş bir satır,
    başarısız bir satırdan daha zararlıdır: sessizdir.*
    """
    import lab.garson as g

    olculen = {s for sen in g.SENARYOLAR for s in sen["olculen"]}
    kor = [s for s in g.TUM_SATIRLAR if s not in olculen]
    assert not kor, (
        "🔴 RAPORLANAN AMA HİÇ ÖLÇÜLMEYEN SATIR:\n  " + "\n  ".join(kor)
        + "\n\nBu satırlar raporda `0|0|0` çıkar ve **başarısız** gibi okunur. "
          "Ya bir senaryonun `olculen`'ine gir, ya `TUM_SATIRLAR`'dan çık.")


def test_ANLATICININ_KENDI_SATIRI_OLCULUYOR():
    """⚠ Özel olarak `2·anlat`: bu fazın amiral yeteneği (`G5`) ve onu ölçebilen tek
    yer canlı kapıdır — anlatıcı yalnız gerçek sağlayıcıyla koşar."""
    import lab.garson as g

    olculen = {s for sen in g.SENARYOLAR for s in sen["olculen"]}
    assert g.S2_ANLAT in olculen, "🔴 anlatıcı kendi kapısında ölçülmüyor"
    assert g.S1_CAPA in olculen, "🔴 «konuşma turu yeni SQL yazmaz» ölçülmüyor"
