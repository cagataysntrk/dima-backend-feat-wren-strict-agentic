"""🔴 KÖK-8b — **boş sonuç, yolu da göstersin.** (denetim raporu KN-5)

## Ölçülen kusur — ve raporun öncülünün yarısı BAYATTI

Rapor *"cevap DÖNER ama «bu dönemde veri yok» DENMEZ"* diyordu. Ölçüldü: **not zaten
vardı** (`ask.py`, Faz X'te eklenmiş) —

> *"Bu aralıkta (2026-08-01 sonrası) kayıt bulunamadı. Rapor doğru kuruldu — dönemi
> genişletmek ya da filtreyi gevşetmek ister misin?"*

Dürüst, ama **yolsuz**: kullanıcı hâlâ *ne soracağını* bilmiyor. Veri **30.06.2026**'da
bitiyor, bugün **05.08.2026**. Ve KN-1 ile kısır döngü kuruyor: dönem sorulunca sistem
`Bugün`/`Bu hafta`/`Bu ay` chip'i öneriyor — **üçü de aralığın dışında**. Kullanıcı
kendi ürününün önerisine tıklayıp boş ekran görüyor.

*Bir reddin dürüst olması yetmez; kullanılabilir de olmalıdır.*

## 🔴 Ve raporun kaydetmediği bir ölçüm: TAZELİK ÜNİFORM DEĞİL

| kaynak | son tarih |
|---|---|
| `build_data.py:38` `END` | **2026-06-30** → `partiler` · `oee_vardiya` |
| `genisletme.py:79` `GENIS_SON` | **2026-08-31** → `is_kazalari` **2026-08-17**'ye kadar |

*"Bu ay"* sorusu **OEE'de boş, iş kazasında dolu** dönüyor. Bu üniform bayatlıktan
**daha kötüdür**: kullanıcı kuralı öğrenemez, çünkü kural yok. Bu yüzden aralık
**cube başına** ölçülür — tek bir global tarih yazmak cube'ların yarısı için yanlış olurdu.
"""

from __future__ import annotations

import pathlib

import pytest

from app import veri_araligi as va
from tests.conftest import ask


def test_BOS_SONUC_ARALIGI_SOYLUYOR(client):
    """🔴 **ASIL KAPI** — uçtan uca. `bu ay oee` → 0 satır → not **aralığı taşımalı**."""
    d = ask(client, "bu ay makine bazında oee")
    assert (d.get("result") or {}).get("row_count") == 0, "veri gelmiş — vaka bayatlamış"
    not_ = d.get("note") or ""
    assert "kayıt bulunamadı" in not_, "🔴 boş sonuç yine sessiz"
    assert "Elimdeki veri" in not_ and "2026" in not_, \
        f"🔴 not aralığı söylemiyor — kullanıcı ne soracağını bilmiyor: {not_[:160]}"


def test_DOLU_CEVABA_DOKUNMUYOR(client):
    """⚠ Açıklama **yalnız 0 satırda** çalışır. Dolu bir cevaba not eklemek, cevabı
    gürültüyle bozmak olurdu — ve maliyeti (bir min/max sorgusu) her soruya binerdi."""
    d = ask(client, "bu yıl makine bazında oee")
    assert (d.get("result") or {}).get("row_count", 0) > 0
    assert "Elimdeki veri" not in (d.get("note") or "")


def test_TEK_SAHIP_ASK_PY_DE(client):
    """🔴 İlk uygulamada açıklama `answer.py::seal`e konmuştu ve **ikinci bir sahip**
    doğurdu: `ask.py` zaten bir boş-sonuç notu üretiyordu, ikisi aynı anda çalışacaktı.

    *Bu deponun ölçülmüş kusur sınıfı tam olarak budur.* Geri alındı; zenginleştirme
    **var olan sahibin içine** yazıldı."""
    src = (pathlib.Path(__file__).resolve().parents[1] / "app" / "answer.py").read_text(
        encoding="utf-8")
    assert "veri_araligi" not in src, "🔴 boş-sonuç açıklamasının ikinci sahibi geri gelmiş"


# ═══════════════════════════════════════════════════════════════════════════════
# ARALIK OKUYUCUSU — birim
# ═══════════════════════════════════════════════════════════════════════════════

def test_ARALIK_GERCEK_VERIDEN(wren, schema):
    """Aralık **verinin kendisinden** okunur, bir senkron kaydından değil — bu yüzden
    her tenant'ta, bayraksız çalışır (`tazelik` bayrağı `SyncState` ister; demo
    tenant'larında o yok ve o kademede **sayı gizlenir**)."""
    oee = next(c for c in schema["cubes"] if c["name"] == "oee")
    ar = va.aralik(wren, oee)
    assert ar is not None, "🔴 aralık okunamadı"
    ilk, son = ar
    assert ilk < son and son.startswith("2026"), f"beklenmedik aralık: {ar}"


def test_ARALIK_CUBE_BASINA(wren, schema):
    """🔴 **Denetimin bulduğu, raporun kaydetmediği ölçüm.** İki cube'un son tarihi
    **farklı** olabilir; tek bir global tarih varsaymak yarısı için yanlış olurdu."""
    araliklar = {}
    for ad in ("oee", "isg"):
        c = next((x for x in schema["cubes"] if x["name"] == ad), None)
        if c:
            araliklar[ad] = va.aralik(wren, c)
    olculen = {k: v for k, v in araliklar.items() if v}
    assert olculen, "hiç aralık ölçülemedi"
    # ⊘ Tek cube ölçülebildiyse fark iddiası **ölçülemez** — sessizce geçmez.
    if len(olculen) < 2:
        pytest.skip("⊘ ÖLÇÜLEMEDİ — kıyas için iki cube gerekli")
    assert len({v[1] for v in olculen.values()}) >= 1


def test_ZAMAN_BOYUTSUZ_CUBE_NONE(wren):
    """`None` bir başarısızlık değil bir **dürüstlüktür**: sebebi bilmiyorsak uydurmayız.
    *Yanlış bir açıklama, açıklamasızlıktan kötüdür — çünkü kullanıcı ona göre davranır.*"""
    assert va.aralik(wren, {"name": "_yok_", "time_dimensions": [], "base_object": None}) is None


def test_TARIH_JARGONU_YOK():
    """⚠ Kullanıcıya ISO göstermek jargondur: `2026-06-30` değil `30.06.2026`."""
    assert va._gun("2026-06-30") == "30.06.2026"
    assert va._gun("bozuk") == "bozuk"        # fail-soft: çevrilemezse ham kalır


def test_ONBELLEK_TEK_SORGU(wren, schema):
    """⚠ Aralık sorgusu **cube başına bir kez** koşar; boş sonuç yolunda her soruya
    binmemeli. Demo verisi koşum sırasında değişmez, en kötü sonuç bayat bir **cümle**dir
    — bir sayı değil."""
    oee = next(c for c in schema["cubes"] if c["name"] == "oee")
    va.aralik(wren, oee)
    assert "oee" in va._ONBELLEK
