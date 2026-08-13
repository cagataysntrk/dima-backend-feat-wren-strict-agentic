"""🔴 `§57`+`§59` — **ÇOK KELİMELİ GİRDİ**: tamamlama yazıldıkça körleşmez.

## Ölçülen kusur (kullanıcı ekranı, 2026-08-13)

`q=«ram 3 neden düşük»` yazıldı; öneri listesinde **`RAM 3` hiç yoktu** — gelenler
*«en düşük kur»*, *«doğalgaz»*, *«ramak kala»*. Motor ölçüldü:

    ara(«ram 3»)             → RAM 3 · RAM-3 …   ✅
    ara(«ram 3 neden»)       → RAM 3 · RAM-3 …   ✅
    ara(«ram 3 neden dusuk») → **[]**            🔴

Leksik eşleşme **tüm diziyi** önek sayıyordu; kullanıcı cümlesini uzattıkça yazdığı
varlık listeden **siliniyordu** ve boşluğu vektör ayağı (bir **sıralayıcı**, süzgeç
değil) anlamca uzak ölçülerle dolduruyordu.

## İki yüklem, iki ayrı ders

| # | savunulan | ders |
|---|---|---|
| 1 | çok kelimeli girdide **token kapsamı** çalışır | 🆫 tamamlama körleşmez |
| 2 | **rakam pekiştirir, kanıtlamaz** | 🆢 tek başına duran rakam bir arama terimi değil, bir **kimlik parçasıdır** |

İkincisinin **kendi tarihi** var: ilk çare rakamı **toptan elemekti** ve komşuyu bozdu
⑯ — `RAM 3` ile `RAM-1` eşitlendi, sıra kayboldu. Doğru ölçüt uzunluk değil **cins**:
`«ram»` (3 harf) ile `«3»` (1 hane) uzunlukla ayrılmaz.
"""

from __future__ import annotations

from app import oneri, oneri_cumle


def _metinler(q: str, schema) -> list[str]:
    return [o.metin for o in
            oneri_cumle.cumleler(oneri.ara(q, schema), capa=None, schema=schema, soru=q)]


def test_UZUN_CUMLE_VARLIGI_KAYBETMEZ(schema):
    """🆫 Kullanıcı yazmaya devam ettikçe eşleşme **sıfırlanmamalı**."""
    for q in ("ram 3", "ram 3 neden", "ram 3 neden düşük"):
        m = _metinler(q, schema)
        assert m, f"🔴 «{q}» için hiç öneri yok — eşleşme sıfırlandı"
        assert any("RAM 3" in s or "RAM-3" in s for s in m[:3]), (
            f"🔴 «{q}»: ilk üç satırda yazılan varlık yok → {m[:3]}")


def test_TEK_HANELI_DEGER_TEK_BASINA_ESLESMEZ(schema):
    """🆢 Katalogdaki `3` (şiddet kodu) sorgudaki `3`'e **tek başına** vurmamalı."""
    m = _metinler("ram 3 neden düşük", schema)
    assert not any(s.startswith("bu ay 3'") for s in m), (
        f"🔴 tek haneli değer tek başına eşleşti → {m}")


def test_ZIT_OLCUT_RAKAM_HALA_AYIRT_EDIYOR(schema):
    """🆃 Kuralın **kurbanı** da kapıya yazılır.

    İlk çare rakamı toptan elemişti ve `RAM 3` ile `RAM-1` **eşitlenmişti** ⑯. Rakam
    hâlâ bir **pekiştirici** olmalı: `«ram 3»` yazan kullanıcı `RAM 1`'i değil `RAM 3`'ü
    üstte görmeli.
    """
    m = _metinler("ram 3", schema)
    ilk = " ".join(m[:2])
    assert "RAM 3" in ilk or "RAM-3" in ilk, f"🔴 rakam ayırt etmiyor → {m[:3]}"


def test_TEK_KELIME_DAVRANISI_DEGISMEDI(schema):
    """⚠ `tokenlar == [q]` hâlinde kapsam kovası önek kovasıyla çakışır — tek kelimelik
    girdide davranış **birebir aynı** kalmalı (`KURAL B` ruhu)."""
    m = _metinler("fire", schema)
    assert m and all("fire" in s.lower() for s in m), f"🔴 tek kelime yolu bozuldu → {m}"
