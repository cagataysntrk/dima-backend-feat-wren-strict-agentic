"""🔴 ANLAŞILMAMIŞ SORUYA **SAYI ÜRETİLMEZ.** (canlı ölçüm, 2026-08-06)

## Ölçülen kusur — sınıfın KENDİ belgesinin ihlali

`RuleBasedSqlGenerator`'ın docstring'i *"sessiz yanlış üretmek yerine ... dürüstçe
reddeder"* diyor. Ama `_partiler_sql`in son dalı **koşulsuz** bir sayma dalıydı:

    else:
        measure, alias = "COUNT(*)", "parti_sayisi"

⊙ Sonucu canlı ölçüldü — dördü de `source=rule` rozetiyle, **notsuz**, tek sayı:

| soru | üretilen SQL | cevap |
|---|---|---|
| `zombixyz ne kadar` | `SELECT COUNT(*) FROM partiler` | **37 878** |
| `flarnak bizde kac` | aynı SQL | **37 878** |
| `qwertyuiop ne durumda` | aynı SQL | **37 878** |
| `zombixyz ve flarnak kiyasla` | aynı SQL | **37 878** |

🔴 Bu, deponun adını koyduğu **en kötü hata sınıfıdır**: anlaşılmamış bir soruya
kendinden emin bir sayı. ADR-0008'in birinci yasağı tam olarak budur.

## ⚠ Ve bilgi ZATEN VARDI

`partial_unknowns` bu sorularda `['zombixyz']` döndürüyor; kapsam kapısı kelimeyi
tanımıyor. Bilgi vardı, o dala **ulaşmıyordu**.
*Merdivenin alt basamağı, üst basamağın bildiğini bilmiyordu.*

## Şart iki kez yazıldı — ikincisi ÖLÇÜMLE

İlk yazımda *"sayma niyeti VEYA tanınan varlık"* dendi. Ölçüm çürüttü:
`flarnak bizde kac` sayma niyeti taşıyor ve yine **37 878** döndürdü.

> Sayma niyeti *sayının istendiğini* söyler, **neyin sayılacağını** söylemez.

→ Şart **VE** oldu: açık sayma niyeti **ve** tanınan bir kolon kökü.
⚠ Kapsam bedeli bilerek ödendi (`kaç kayıt var` gibi varlıksız sorular da düşer);
kural motoru anahtarsız **yedektir** ve üst basamak (Discovery) onları hâlâ deneyebilir.
"""

from __future__ import annotations

import pytest

from app.llm import RuleBasedSqlGenerator, _sayma_dayanagi
from tests.conftest import ask

#: Canlıda ölçülen dört vaka — hepsi 37 878 döndürüyordu.
ANLAMSIZ = ["zombixyz ne kadar", "flarnak bizde kac",
            "qwertyuiop ne durumda", "zombixyz ve flarnak kiyasla"]


@pytest.mark.parametrize("q", ANLAMSIZ)
def test_ANLAMSIZ_SORUYA_SAYI_YOK(q, client):
    """🔴 **ASIL KAPI** — uçtan uca. Anlaşılmamış soru bir SAYI ile dönmemeli."""
    d = ask(client, q)
    satir = (d.get("result") or {}).get("row_count")
    assert not satir, (
        f"🔴 «{q}» → {satir} satır, source={d.get('source')}, "
        f"sql={(d.get('sql') or '')[:80]} — anlaşılmamış soruya SAYI üretildi")
    assert d.get("note"), "🔴 ret var ama gerekçe yok — sessiz ret de bir kusurdur"


def test_HEPSI_AYNI_SAYIYI_DONDURMUYOR(client):
    """🔴 Kusurun **imzası**: dört farklı soru **aynı** sayıyı veriyordu. Aynı cevabı
    veren farklı sorular, cevabın soruya bakmadığının kanıtıdır."""
    cevaplar = {str((ask(client, q).get("result") or {}).get("rows")) for q in ANLAMSIZ}
    assert cevaplar == {"None"}, f"🔴 hâlâ sayı üretiliyor: {cevaplar}"


# ═══════════════════════════════════════════════════════════════════════════════
# ŞARTIN KENDİSİ — ve ölçümle düzeltilmiş hâli
# ═══════════════════════════════════════════════════════════════════════════════

COLS = {"parti_no", "musteri", "kumas_cinsi", "agirlik_kg", "fire_kg", "tarih"}


def test_IKI_SART_BIRDEN():
    """🔴 *"VEYA"* ölçümle *"VE"*ye çevrildi: `flarnak bizde kac` sayma niyeti taşıyor
    ama sayılacak şey tanınmıyor. *Sayma niyeti sayının istendiğini söyler, neyin
    sayılacağını söylemez.*"""
    assert _sayma_dayanagi("bu yil kac parti", COLS), "⊘ meşru sayma sorusu düştü"
    assert not _sayma_dayanagi("flarnak bizde kac", COLS), "🔴 tanınmayan varlık sayıldı"
    assert not _sayma_dayanagi("zombixyz ne kadar", COLS), "🔴 sayma niyeti bile yok"
    assert not _sayma_dayanagi("musteri bazinda ciro", COLS), "🔴 sayma niyeti yok"


def test_JENERATOR_DURUSTCE_REDDEDIYOR(schema):
    """⚠ Ret bir **istisna**dır, boş bir SQL değil: üst basamak (Discovery) onu görüp
    kendi denemesini yapabilsin. *Sessiz bir başarısızlık, denenmemiş bir alternatiftir.*"""
    g = RuleBasedSqlGenerator()
    with pytest.raises(ValueError, match="uydurmak yerine|desteklemiyor"):
        g.generate_sql("zombixyz ne kadar", schema)


def test_MESRU_SORULAR_BOZULMADI(client):
    """🔴 Kapının **asıl sınavı**: kural motorunun gerçekten cevaplayabildiği sorular
    kaybolmamalı. *Bir kapıyı kapatmak, kapının arkasındakileri de dışarı atmak değildir.*"""
    for q in ("bu yıl toplam ciro", "makine bazında fire", "geçen ay kaç parti işlendi"):
        d = ask(client, q)
        assert d.get("source") or d.get("note"), f"⊘ «{q}» sessizce kayboldu"
        assert "anlayamadım" not in (d.get("note") or "").lower() or d.get("suggestions"), \
            f"🔴 meşru soru gerekçesiz reddedildi: {q}"
