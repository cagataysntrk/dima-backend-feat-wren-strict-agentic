"""FAZ 4.3 — kanonik CubeQuery kimliği.

Plan bir CACHE ANAHTARI istiyordu ("NL-benzerlik cevap cache'i kullanma — anahtar kanonik
CubeQuery hash'i olmalı"). **Cache kurulmadı**: tekrar oranı ölçülmedi (`interaction_log`
telemetrisi yeni kalıcı oldu, veri birikmedi) ve ölçülmemiş bir ihtiyaç için altyapı
kurulmaz. Kurulan şey ANAHTAR: sözleşme kimliği, terfi kuyruğu tekilleştirmesi ve "aynı
sorgu mu" karşılaştırması bunu zaten istiyor — ve biri cache eklemek isterse doğru anahtar
hazır olsun diye.

Sözleşme **`result_hash`ten farklıdır** ve fark bilinçlidir:
  `result_hash`      → "SAYILAR değişti mi" — satır sırasını umursamaz.
  `cube_query_hash`  → "aynı hash ⇒ aynı ÇIKTI" — kolon sırası dahil. Bir cache anahtarı
                       olabilecek kadar sıkı olmak zorunda.
"""

from __future__ import annotations

from app.contracts import cube_query_hash

TEMEL = {"cube": "kalite", "measures": ["toplam_rework_kg"], "dimensions": ["renk"]}


def test_ayni_sorgu_AYNI_hash():
    assert cube_query_hash(dict(TEMEL)) == cube_query_hash(dict(TEMEL))


def test_filtre_SIRASI_onemsiz():
    """Saf AND birleşimi — çıktıya hiçbir etkisi yok."""
    a = {**TEMEL, "filters": [
        {"dimension": "renk", "operator": "neq", "value": "Beyaz"},
        {"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    b = {**TEMEL, "filters": list(reversed(a["filters"]))}
    assert cube_query_hash(a) == cube_query_hash(b)


def test_in_liste_SIRASI_onemsiz():
    a = {**TEMEL, "filters": [{"dimension": "renk", "operator": "in",
                               "value": ["Beyaz", "Siyah"]}]}
    b = {**TEMEL, "filters": [{"dimension": "renk", "operator": "in",
                               "value": ["Siyah", "Beyaz"]}]}
    assert cube_query_hash(a) == cube_query_hash(b)


def test_OPERATOR_farki_hash_degistirir():
    """Faz 3.3'ten sonra kritik: `eq` ile `neq` TAM TERS sonuç verir. Aynı anahtara
    düşselerdi bir cache "beyaz hariç" sorusuna beyazın kendisini döndürürdü."""
    a = {**TEMEL, "filters": [{"dimension": "renk", "operator": "eq", "value": "Beyaz"}]}
    b = {**TEMEL, "filters": [{"dimension": "renk", "operator": "neq", "value": "Beyaz"}]}
    assert cube_query_hash(a) != cube_query_hash(b)


def test_in_ile_not_in_FARKLI():
    a = {**TEMEL, "filters": [{"dimension": "renk", "operator": "in",
                               "value": ["Beyaz", "Siyah"]}]}
    b = {**TEMEL, "filters": [{"dimension": "renk", "operator": "not_in",
                               "value": ["Beyaz", "Siyah"]}]}
    assert cube_query_hash(a) != cube_query_hash(b)


def test_deger_farki_hash_degistirir():
    a = {**TEMEL, "filters": [{"dimension": "renk", "operator": "eq", "value": "Beyaz"}]}
    b = {**TEMEL, "filters": [{"dimension": "renk", "operator": "eq", "value": "Siyah"}]}
    assert cube_query_hash(a) != cube_query_hash(b)


def test_olcu_SIRASI_ONEMLI():
    """Kolon sırasını belirler. Sıralasaydık `[a,b]` için önbelleğe alınan sonuç `[b,a]`
    sorgusuna kolonları TERS sırada döndürülürdü — sessiz bir sunum hatası."""
    a = {**TEMEL, "measures": ["toplam_rework_kg", "tamir_sayisi"]}
    b = {**TEMEL, "measures": ["tamir_sayisi", "toplam_rework_kg"]}
    assert cube_query_hash(a) != cube_query_hash(b)


def test_boyut_SIRASI_ONEMLI():
    """GROUP BY sırası satır sırasını belirler."""
    a = {**TEMEL, "dimensions": ["renk", "makine"]}
    b = {**TEMEL, "dimensions": ["makine", "renk"]}
    assert cube_query_hash(a) != cube_query_hash(b)


def test_AKIS_BAYRAGI_hashi_degistirmez():
    """`period_confirmed` bir UI/merdiven durumudur; üretilen SQL birebir aynıdır.
    Kimliğe girseydi dönem chip'ine tıklamadan önce ve sonra AYNI sorgu FARKLI hash
    alırdı — cache her tıklamada ıskalardı, sözleşme de sahte bir "değişti" gösterirdi."""
    a = dict(TEMEL)
    b = {**TEMEL, "period_confirmed": True}
    assert cube_query_hash(a) == cube_query_hash(b)


def test_akis_bayragi_IC_ICE_de_dusurulur():
    a = {**TEMEL, "filters": [{"dimension": "renk", "operator": "eq", "value": "Beyaz"}]}
    b = {**TEMEL, "period_confirmed": False,
         "filters": [{"dimension": "renk", "operator": "eq", "value": "Beyaz",
                      "period_confirmed": True}]}
    assert cube_query_hash(a) == cube_query_hash(b)


def test_MDL_SURUMU_kimlige_girer():
    """Şema değişince aynı CubeQuery başka bir şey ifade eder (ölçü ifadesi değişmiş,
    boyut başka bir kolona bağlanmış olabilir). Bayat bir sonuç yeni şemada YANLIŞTIR."""
    assert cube_query_hash(TEMEL, mdl_version="v1") != cube_query_hash(TEMEL, mdl_version="v2")


def test_KIRACI_izolasyonu():
    """İki kiracının aynı sorgusu ASLA aynı anahtara düşmemeli — bir cache bunu yaparsa
    tenant sızıntısı olur ve `authorize()` devreye bile giremez."""
    assert (cube_query_hash(TEMEL, company="a", tenant_id="t1")
            != cube_query_hash(TEMEL, company="b", tenant_id="t2"))
    assert (cube_query_hash(TEMEL, company="a", tenant_id="t1")
            != cube_query_hash(TEMEL, company="a", tenant_id="t2"))


def test_bos_ve_None_patlamaz():
    assert cube_query_hash(None).startswith("sha256:")
    assert cube_query_hash({}) == cube_query_hash(None)


def test_girdi_MUTASYONA_ugramaz():
    """Kimlik hesaplamak çağıranın sorgusunu değiştirmemeli — hash'lenen nesne sonra
    çalıştırılıyor."""
    import copy

    cq = {**TEMEL, "period_confirmed": True, "filters": [
        {"dimension": "renk", "operator": "in", "value": ["Siyah", "Beyaz"]},
        {"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    once = copy.deepcopy(cq)
    cube_query_hash(cq)
    assert cq == once


def test_result_hash_ile_KARISTIRILAMAZ():
    """İki fonksiyon farklı sözleşmeler taşır; biri diğerinin yerine kullanılamasın diye
    aynı girdide farklı değer ürettikleri kayda geçer."""
    from app.contracts import result_hash

    r = {"columns": ["renk"], "rows": [{"renk": "Beyaz"}]}
    assert result_hash(r) != cube_query_hash(TEMEL)
