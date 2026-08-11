"""🔴 `§D1` — ŞABLON ANLATICI ÜRETİLEN HER OLGUYU TANIMALI.

`anlatici.TANINAN` **kapalı** bir kümedir ve modülün kendi uyarısı şudur: *«yeni bir tür
`interpret()`'e eklenirse bu basamak onu tanımaz ve turu **LLM'e devreder**»*.

Ölçüldü (2026-08-11): `kiyas` (`§D11` ile eklendi) ve **zaten üretilmekte olan**
`segment_delta` kümede **yoktu** → ikisini taşıyan her cevap, şablonla 0 token
anlatılabilecekken **LLM'e** düşüyordu. Canlı ölçüm: anlatı LLM'i bir turda **22,5 sn /
turun %93'ü**.

⚠ Bu kapı bir **eşleşme kapısıdır**: `interpret` yeni bir tip üretmeye başlarsa burada
kırmızı verir. *Bir kapalı kümenin bedeli, kapandığını unutmaktır.*
"""

from app import anlatici
from app.interpret import interpret


def _sonuc(cols, rows):
    return {"columns": cols, "rows": rows, "row_count": len(rows)}


def test_URETILEN_HER_TIP_TANINIYOR():
    """🔴 Asıl kapı: `interpret`'in ürettiği tipler ⊆ anlatıcının tanıdıkları.

    Üretilen tipler **canlıdan** değil, üreticilerin **kendi** çıktı sözcüklerinden
    toplanır — böylece yeni bir `facts.append` eklendiğinde kapı konuşur.
    """
    import re

    kaynak = (__import__("pathlib").Path(anlatici.__file__).parent
              / "interpret.py").read_text(encoding="utf-8")
    uretilen = set(re.findall(r'"type":\s*"([a-z_]+)"', kaynak))
    bilinen_istisna = {
        "kpi_components",   # `kpi_value` ile birlikte gelir; ikincil satır
        "measures",         # «N ölçü: …» — bir olgu değil bir ENVANTER satırı
    }
    eksik = uretilen - set(anlatici.TANINAN) - bilinen_istisna
    assert not eksik, (
        f"🔴 `interpret` şu tipleri üretiyor ama anlatıcı tanımıyor: {sorted(eksik)}\n"
        "  Sonuç: bu olguları taşıyan her cevap şablon yerine LLM'e düşer.\n"
        "  `anlatici.TANINAN` + `_ONCELIK` listelerine ekle.")


def test_kiyas_SABLON_BASAMAGINDA_DURUR_llm_e_gitmez():
    """🔴 **Asıl kazanç metin değil, YAPILMAYAN ÇAĞRI** — modülün kendi cümlesi.

    ⚠ Ve bu testi ilk yazımda yanlış kurdum: `anlat()`'ın **metin** döndürmesini
    bekledim, oysa **yankı kapısı** devrede — üretilecek cümle `summary` ile birebir
    aynı olacaksa `None` döner (ikinci kez, cümle biçiminde tekrarlamak bir özet değil
    bir gürültüdür). Ölçüt `basit_mi`'dir: `True` ise `answer.py` `narration_kaynak =
    "sablon"` yazar ve **LLM adımını hiç çağırmaz**.

    ⊙ Canlı ölçüm bu kazancın büyüklüğünü veriyor: anlatı LLM'i bir turda **22,5 sn**,
    turun **%93'ü**.
    """
    y = interpret(_sonuc(["toplam_ciro", "toplam_ciro_gecen", "toplam_ciro_degisim_yuzde"],
                         [{"toplam_ciro": 100.0, "toplam_ciro_gecen": 80.0,
                           "toplam_ciro_degisim_yuzde": 25.0}]),
                  cube_query={"cube": "parti", "measures": ["toplam_ciro"]})
    assert anlatici.basit_mi(y), "tek ölçülü kıyas şablon basamağında durmalı (0 LLM)"
    # Ve olgu gerçekten kıyası taşıyor — `summary` onu kullanıcıya zaten söylüyor.
    assert any(f["type"] == "kiyas" for f in y["facts"])
    assert "arttı" in y["summary"]


def test_ONCELIK_ve_TANINAN_ayni_kumeyi_tasir():
    """`KAT-1` — iki liste ayrışırsa bir tip tanınır ama sıralanamaz (99'a düşer)."""
    assert set(anlatici.TANINAN) == set(anlatici._ONCELIK)


def test_COK_OLCULU_KIYAS_hala_LLM_e_gider():
    """⚠ Genişletme kapıyı GEVŞETMEZ: iki ölçüyü tek cümlede yan yana koymak bir
    **ilişki** ima eder ve o çıkarım bu basamağın yetkisinde değildir."""
    y = interpret(_sonuc(["toplam_ciro", "toplam_ciro_gecen", "toplam_ciro_degisim_yuzde",
                          "kar", "kar_gecen", "kar_degisim_yuzde"],
                         [{"toplam_ciro": 100.0, "toplam_ciro_gecen": 80.0,
                           "toplam_ciro_degisim_yuzde": 25.0, "kar": 10.0,
                           "kar_gecen": 12.0, "kar_degisim_yuzde": -16.7}]),
                  cube_query={"cube": "parti", "measures": ["toplam_ciro", "kar"]})
    assert not anlatici.basit_mi(y), "çok ölçülü tur şablona bırakılmamalı"
