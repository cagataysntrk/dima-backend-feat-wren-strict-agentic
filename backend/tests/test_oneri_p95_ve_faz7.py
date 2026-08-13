r"""🔴 `FAZ 5` kapı `②` (**p95**) + `FAZ 7`'nin ⊘'sünün **doğrulanması**.

## `②` — ÖLÇÜLDÜ ve KAPIYA BAĞLANDI 🆇

`lab/oneri_p95.py`, **gerçek gömücüyle** (`intfloat/multilingual-e5-large`) koştu:

| ölçüm | değer |
|---|---|
| kip | **vektor** *(leksik değil — 🅕 gömücüsüz sayı taşınmaz)* |
| terim | **136** · payda **90** koşum |
| **ılık p50** | **50,77 ms** |
| **ılık p95** | **53,82 ms** — eşik **300 ms** ✅ *(≈5,6× pay)* |
| soğuk (indeks kurulumu) | **24.313,1 ms** |

## ⟳ İKİ SAYI DA DEĞİŞTİ — ve ikisinin de sebebi yazılı 🅟

⊙ **Ilık `39,63 → 50,77` ms**: `§18.7` çok görünümlü temsile geçildi (alan başına dört
görünüm). Bedeli ölçüldü, karşılığı da: **`Recall@3` %68,4 → %89,5**. Eşiğin altında
kalındı, yani `②` kapısı **hâlâ geçiliyor** — ama sayı bir **fotoğraftır** ve burada
tazelenmiştir.

⊙ **Soğuk `1.514 → 24.313` ms**: 136 etiket yerine **534 görünüm** gömülüyor.

🔴 **VE BU ARTIK KULLANICIYA YANSIMIYOR — ısıtma YAPILDI.** Bu bölümün eski hâli
*«⊘ şimdi yapılmadı, çünkü ısıtma bir şema ister ve şema tenant'a göre çözülür»*
diyordu. O gerekçe **ödendi**: `main.py`'nin `lifespan`'i şema ve gömücüyü zaten
ısıtıyordu; üçüncü bir ısıtma indeksi de kuruyor. Ölçüldü: ısıtmadan sonra **ilk
kullanıcı isteği 55,0 ms**. Kapısı `tests/test_oneri_isitma.py`.

⚠ **Soğuk sayı raporda KALMAYA devam ediyor** ve kalmalı 🅖: ısıtma onu **taşıdı**,
yok etmedi. Konteyner açılışından hemen sonra gelen bir istek hâlâ bekleyebilir ve
**çok kiracılı** kurulumda ikinci tenant'ın indeksi hâlâ ilk istekte kurulur.
*Bir maliyeti görünmez yapmak onu ödemek değildir; nereye taşındığını yazmaktır.*

⚠ 🅣 **Ve asıl ders bu kapının kendisindeydi:** `②` eşiği `p95`'e bakar, `p95` **ılık**
dağılımın ölçüsüdür ve ilk isteği **tanım gereği saymaz**. Kapı yeşilken kullanıcı 24
saniye bekliyordu. *Bir ölçütün kapsamı dışındaki kusur, o ölçüt için yok hükmündedir.*

## `FAZ 7` — planın ⊘'sü **DEVRALINMADI, DOĞRULANDI** ㉓

Plan diyor ki: *«`§40.4`'ün kararı: bu faz iddiayı kanıtlamıyor, zenginleştiriyor.
Demo başarılı olursa açılır. Alt maddeleri `§34/adım 7`'de duruyor — silinmedi,
ertelendi.»*

İki **doğrulanabilir** iddia var ve ikisi de ölçüldü:
* `§40.4` **var** (`:2141` — *«Demo KAPSAMI ↔ demo DIŞI»*) ve kararı yazıyor.
* `§34/Adım 7` **var** (`:1958`) ve alt maddeleri (`ChatPanel.tsx` · `ReportCard.tsx`
  · `plan_semasi` · pill sözleşmesi · `test_pill_niyet_aynasi.py`) **duruyor**.

⊙ Yani ⊘ bir **unutma** değil bir **karar**, ve geri dönüş adresi yazılı. Aşağıdaki
yüklem o adresi tutar: iddia bir gün **boşa düşerse** kapı kırmızı verir 🅟.
"""

from __future__ import annotations

import json
import pathlib

import pytest

_KOK = pathlib.Path(__file__).resolve().parents[1]
_PLAN = _KOK.parent / "belgeler" / "plan" / "2026-08-12_ONGORU-KATMANI-KARARI.md"

#: Plan `§42 · FAZ 5` kapı `②`.
ESIK_MS = 300.0


def test_p95_RAPORU_YERINDE_ve_ESIGI_GECIYOR():
    """🆇 **Raporun sayısını kapıya bağla.** Sayı dosyadan **okunur** ㉔.

    🅑 Mutasyon: `oneri.ara`'nın önbelleği kaldırılırsa p95 fırlar ve bu yüklem
    kırılır (araç yeniden koşulduğunda).
    """
    y = _KOK / "lab" / "reports" / "oneri_p95.json"
    if not y.is_file():
        pytest.skip(f"⊘ `{y.name}` yok — `python lab/oneri_p95.py` koşulmalı "
                    "(gömme mount'u ile).")
    d = json.loads(y.read_text(encoding="utf-8"))
    assert d.get("kip") == "vektor", (
        f"🔴 rapor **leksik** kiple üretilmiş (`kip={d.get('kip')!r}`) — bu bir p95 "
        "değil, vektör ayağı hiç koşmamış 🅕. `DIMA_VQR_EMBEDDER` konmadan ve gömme "
        "mount'uyla yeniden koşulmalı.")
    p95 = d.get("ilik_p95_ms")
    assert isinstance(p95, (int, float)) and p95 < ESIK_MS, (
        f"🔴 `FAZ 5` kapı `②` DÜŞTÜ: ılık p95 = {p95} ms ≥ {ESIK_MS} ms.")
    # 🅜 Payda kutsaldır — tek koşumdan p95 çıkmaz 🅢.
    assert d.get("payda", 0) >= 30, (
        f"🔴 payda küçük ({d.get('payda')}) — bu bir p95 değil bir gözlemdir ㉗.")


def test_SOGUK_MALIYET_RAPORDA_GORUNUYOR():
    """🅖 *Eksiği yayına yaz.* Soğuk ilk istek eşiğin **üstünde** (ölçüldü: ~1,5 s) ve
    raporun bunu **taşıması** gerekir; yalnız ılık sayıyı yayımlamak, kullanıcının
    yaşadığı ilk saniyeyi **gizlemek** olurdu 🅫.
    """
    y = _KOK / "lab" / "reports" / "oneri_p95.json"
    if not y.is_file():
        pytest.skip("⊘ rapor yok.")
    d = json.loads(y.read_text(encoding="utf-8"))
    assert "soguk_ms" in d and d["soguk_ms"] > 0, (
        "🔴 soğuk maliyet raporda yok — ılık p95 tek başına yayımlanırsa ilk isteğin "
        "bedeli görünmez olur.")


# ── `FAZ 7` ⊘'SÜNÜN İKİ DOĞRULANABİLİR İDDİASI ─────────────────────────────

def test_FAZ7_ERTELEMESI_ADRESI_DURUYOR():
    """🔴 ㉓ **«Plan böyle dedi» bir ölçüm değildir.** `FAZ 7`'nin ⊘'sü iki
    doğrulanabilir iddiaya dayanıyor; ikisi de burada tutuluyor.

    Biri kaybolursa (`§40.4` silinir ya da `Adım 7` başlığı gider) erteleme bir
    **unutmaya** dönüşür ve kapı bunu söyler 🅟.
    """
    if not _PLAN.is_file():
        pytest.skip("⊘ plan belgesi mount edilmemiş — `-v \"$PWD/belgeler:/belgeler:ro\"`.")
    metin = _PLAN.read_text(encoding="utf-8")
    assert "### Adım 7 · Çapa · pill · makro · plan önizleme" in metin, (
        "🔴 `§34/Adım 7` kayboldu — `FAZ 7`'nin *«alt maddeleri duruyor, silinmedi»* "
        "iddiası artık DOĞRU DEĞİL; erteleme bir unutmaya döndü.")
    assert "### 40.4 Demo KAPSAMI ↔ demo DIŞI" in metin, (
        "🔴 `§40.4` kayboldu — `FAZ 7`'nin ⊘ gerekçesinin dayanağı yok.")


def test_FAZ7_ALT_MADDELERI_ICERIK_TASIYOR():
    """⚠ Bir başlığın **durması** yetmez; altında **iş** olmalı 🆚. `Adım 7` dosya ·
    sözleşme · kapı üçlüsünü taşımalı — yoksa *«ertelendi»* bir kabuktur."""
    if not _PLAN.is_file():
        pytest.skip("⊘ plan belgesi mount edilmemiş.")
    metin = _PLAN.read_text(encoding="utf-8")
    blok = metin.split("### Adım 7 · Çapa", 1)[1].split("### Adım 8", 1)[0]
    for parca in ("DOSYA", "SÖZLEŞME", "KAPI", "test_pill_niyet_aynasi.py"):
        assert parca in blok, (
            f"🔴 `Adım 7` içeriği eksik ({parca!r}) — ertelenen şeyin ne olduğu artık "
            "okunamıyor.")
