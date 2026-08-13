r"""🔴 `FAZ 5` ÖN KOŞULU — **ÖLÇÜLEN MODEL İLE ÜRETİMDEKİ MODEL AYNI OLMALI.**

`FAZ 5` (öneri motoru) bir eşiğe bağlıdır: *«`Recall@3 ≥ %85`»*. `FAZ 0` o eşiği
**ölçtü** — `%89,5` 🟢 — ve fazın önü açıldı. Ama bir geri getirme ölçümü **modelinden
ayrılamaz** 🅕: aynı korpus, başka bir gömücüyle başka bir sayı verir.

## Ölçülen — ve önce YANLIŞ okunan

⚠ ③ Bu kapı bir **yanlış alarmla** doğdu: `vqr._embedder()`'ın docstring'i *«fastembed
e5-small»* diyordu, ölçüm aracım (`lab/oneri_olcum.py`) ise **e5-large** kullanıyordu →
*«ön koşul başka modelde ölçülmüş»* diye okudum. **Gövdeye bakınca** (`vqr.py:86`)
ikisinin de `intfloat/multilingual-e5-large` olduğu görüldü; docstring **bayattı** 🅟
ve düzeltildi. *Bir modülün kendi cümlesi de bir ölçüm değildir* — bu oturumda **yedinci**
kez kendi beklentim koda bakınca düzeldi.

## Bu kapı neyi tutuyor

Üretim gömücüsü bir gün sessizce değişirse (*«small daha hızlı»*), `FAZ 0`'ın `%89,5`'i
**geçersizleşir** ve `FAZ 5`'in ön koşulu **ölçülmemiş** hâle gelir — ama hiçbir test
kırmızı vermezdi: öneri motoru yine *çalışırdı*, yalnız **daha kötü** bulurdu, ve bunu
kimse fark etmezdi 🆕.

㊻ *Bir ön koşul, kapısı yoksa bir temenni olarak kalır.*
"""

from __future__ import annotations

import pathlib
import re

_KOK = pathlib.Path(__file__).resolve().parents[1]

#: `FAZ 0`'ın ölçümünü yaptığı model — `lab/reports/oneri_olcum.json` bu modelle üretildi.
OLCULEN_MODEL = "intfloat/multilingual-e5-large"


def _model_adlari(yol: pathlib.Path) -> set[str]:
    """`TextEmbedding("…")` çağrılarındaki model adları."""
    return set(re.findall(r'TextEmbedding\(\s*"([^"]+)"', yol.read_text(encoding="utf-8")))


def test_URETIM_ve_OLCUM_ayni_modeli_kullaniyor():
    """🔴🔴 **`FAZ 5`'in ön koşulunun taşınabilirliği.**

    🅑 Mutasyon: `vqr.py`'deki model adı `e5-small`'a çevrilirse bu yüklem kırılır.
    """
    uretim = _model_adlari(_KOK / "app" / "vqr.py")
    olcum = _model_adlari(_KOK / "lab" / "oneri_olcum.py")

    assert uretim == {OLCULEN_MODEL}, (
        f"🔴 ÜRETİM gömücüsü değişti: {sorted(uretim)} — `FAZ 0`'ın `Recall@3 %89,5` "
        f"ölçümü `{OLCULEN_MODEL}` ile yapılmıştı ve **taşınamaz** 🅕. `FAZ 5`'in ön "
        "koşulu yeniden ölçülmeli (`python lab/oneri_olcum.py`).")
    assert olcum == {OLCULEN_MODEL}, (
        f"🔴 ÖLÇÜM aracı değişti: {sorted(olcum)} — rapor ile üretim ayrıştı.")


def test_gomucunun_KENDI_CUMLESI_de_dogru():
    """🅟 *Belge iddiası bayat olabilir* — ve bu satır **yük taşıyor**: okuyan
    *«üretim small»* sanarsa `FAZ 0`'ın eşiğini taşınamaz sayar.

    Kapı, düzeltilen cümlenin **geri bayatlamasını** engeller.
    """
    metin = (_KOK / "app" / "vqr.py").read_text(encoding="utf-8")
    # `_embedder()` docstring'i — ilk satırı
    govde = metin.split("def _embedder():", 1)[1][:400]
    assert "e5-small (lazy)" not in govde, (
        "🔴 `_embedder()` docstring'i yine *«e5-small»* diyor — gövde e5-LARGE yüklüyor. "
        "Bayat iddia geri geldi 🅟.")


def test_FAZ0_raporu_YERINDE_ve_esik_KARSILANDI():
    """㊻ Ön koşulun **kendisi**: rapor duruyor mu ve eşiği geçiyor mu.

    ⚠ ㉔ *Raporun sayısını ölçmeden alma* — sayı dosyadan **okunur**, buraya
    kopyalanmaz. ⚠ 🅬 **Alan adı da uydurulmaz:** bu yüklem ilk yazılışında düz bir
    `recall@3` aradı ve `None` buldu; gerçek şekil **ayak başına** iç içedir
    (`{"vektor": {"recall@3": …, "payda": …}}`). Ad **dönen nesneden** öğrenildi.
    """
    import json

    import pytest

    yol = _KOK / "lab" / "reports" / "oneri_olcum.json"
    if not yol.is_file():
        pytest.skip(f"⊘ `{yol.name}` yok — `python lab/oneri_olcum.py` koşulmalı.")
    d = json.loads(yol.read_text(encoding="utf-8"))
    vektor = d.get("vektor") or {}
    r3 = vektor.get("recall@3")
    assert isinstance(r3, (int, float)), (
        f"🔴 raporda `vektor.recall@3` yok/sayı değil: {r3!r} — şekil değişmiş 🅬.")
    assert r3 >= 85.0, (
        f"🔴 `FAZ 5`'in ön koşulu DÜŞTÜ: `Recall@3 = %{r3}` < %85. Öneri motoru bu "
        "eşiğe bağlıydı (`§42 · FAZ 5`).")
    # 🅜 **Payda kutsaldır** — bir oran paydasız taşınamaz ㉗. Plan 30–40 vaka ister;
    # bugünkü **19** bir borçtur ve burada **görünür** kalır (sessizce geçmesin 🅖).
    assert vektor.get("payda", 0) >= 19, (
        "🔴 ölçüm paydası küçüldü — oran aynı kalsa bile kanıt zayıfladı 🅜.")
