"""FAZ −1/A6 — MIMARI'de ANILAN HER DOSYA GERÇEKTEN VAR MI?

## Neden bu kapı var — ve neden tam bu sınıf

`MIMARI.md` **kanoniktir**: bir okuyucu orada *"kolon doğrulaması
`tests/test_member_sweep.py`'nin build-time taramasıdır"* yazdığını görür ve **öyle
olduğuna güvenir**. O dosya yoksa belge bir **yetenek uyduruyor** demektir — bu deponun
avladığı *"beyan var, kod onu tanımıyor"* sınıfının belge tarafındaki hâli.

## ⚠ VE BU KAPI, KENDİSİNİ DOĞURAN İDDİAYI ÇÜRÜTTÜ

Yol haritası (`FAZ −1`, kalem **A6**) şöyle diyordu:

> *"§5 `tests/test_member_sweep.py`'nin build-time `LIMIT 0` taraması — 🔴 **O DOSYA YOK**
> (`grep -rl member_sweep` → boş)"*

Ölçüldü @`81ad10b`: **dosya VAR** (`tests/test_member_sweep.py`, 5094 bayt, `f5f4048`).
Yol haritasının grep'i **içerik** taradı (`grep -rl` = *"içinde geçen dosyayı listele"*),
**dosya adını** değil — ve o test kendi adını metninde geçirmiyor. **MIMARI haklıydı,
denetim yanlıştı.**

> **Ders (`OPERASYON.md` §6/5):** *ölçüm aracının kendisi de bir bağımlılıktır.*
> Bir kapının **doğru sonuç vermesi**, doğru şeyi ölçtüğünü göstermez — ve bu kez
> **yanlış** sonuç verdi. Bu dosya, o hatanın tekrarını **dosya sisteminden** doğrular.
"""

from __future__ import annotations

import pathlib
import re

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]
MIMARI = KOK / "MIMARI.md"

#: MIMARI'de anılıp da repoda olmaması MEŞRU olanlar — gerekçesiyle.
#: ⚠ Liste büyütmek bir çözüm DEĞİLDİR (ADR-0008): her giriş bir KARARDIR.
MUAF: dict[str, str] = {
    # Yol haritasının üreteceği, henüz inmemiş kapılar — ⟳ bloğunda otoritesi yazılı.
    "tests/test_panel_sayisi.py": "FAZ 0.14'te yazılır (§C/11 kendisi kaydediyor)",
    "tests/test_yol_haritasi_butunlugu.py": "FAZ 0.14'te yazılır (D5'in kapısı)",
    "tests/test_sayim_yerine_kapanis.py": "FAZ 0.14'te yazılır (KAT-5'in kapısı)",
}


def _anilan_test_dosyalari() -> set[str]:
    """MIMARI'de anılan `tests/test_*.py` yolları — backtick içinde ya da düz."""
    metin = MIMARI.read_text(encoding="utf-8")
    return set(re.findall(r"tests/test_[a-z0-9_]+\.py", metin))


def test_MIMARI_ANILAN_TEST_DOSYALARI_VAR():
    """Anılan her test dosyası **gerçekten** mevcut olmalı."""
    eksik = [y for y in sorted(_anilan_test_dosyalari())
             if y not in MUAF and not (KOK / y).exists()]
    assert not eksik, (
        "MIMARI'de ANILAN ama REPODA OLMAYAN test dosyası:\n  " + "\n  ".join(eksik)
        + "\nBelge bir yetenek uyduruyor. Ya dosyayı yaz, ya atfı düzelt, ya MUAF'a "
          "GEREKÇESİYLE ekle — üçüncü seçenek yok.")


def test_MUAFIYET_LISTESI_BAYATLAMIYOR():
    """Muaf bir dosya **yazıldığında** listeden düşmeli — aksi hâlde muafiyet, gerçek bir
    eksiği sonsuza kadar gizler. *(Bu, muafiyet listelerinin klasik çürüme biçimidir.)*"""
    artik_var = [y for y in MUAF if (KOK / y).exists()]
    assert not artik_var, (
        "MUAF listesindeki dosya(lar) ARTIK VAR — muafiyeti kaldır:\n  "
        + "\n  ".join(artik_var))


def test_A6_IDDIASI_CURUTULDU():
    """🔴 Yol haritasının `A6` kalemi *"`test_member_sweep.py` YOK"* diyordu. **Var.**

    Bu test o düzeltmeyi **kilitler**: dosya silinirse ya da yeniden adlandırılırsa,
    MIMARI §5'in beyanı sessizce yalan olur.
    """
    assert (KOK / "tests/test_member_sweep.py").exists(), (
        "test_member_sweep.py kayboldu — MIMARI §5'in kolon-doğrulama beyanı artık "
        "karşılıksız. Ya dosyayı geri getir ya §5'i düzelt.")


@pytest.mark.parametrize("modul", [
    "app/cube_router.py", "app/routers/ask.py", "app/planner.py", "app/tools.py",
    "app/compose.py", "app/narration_guard.py", "app/eylem.py", "app/context.py",
    "lab/nl_corpus.py", "lab/deneyim.py", "lab/kapi.py",
])
def test_MIMARI_ANILAN_MODULLER_VAR(modul):
    """Aynı sınıf, kaynak tarafı: MIMARI'nin omurga modülleri yerinde mi.

    Bir modül yeniden adlandırıldığında MIMARI'nin onlarca atfı **sessizce** bayatlar;
    bu kapı o anı yakalar."""
    if modul not in MIMARI.read_text(encoding="utf-8"):
        pytest.skip(f"{modul} MIMARI'de anılmıyor — kapının konusu değil")
    assert (KOK / modul).exists(), f"MIMARI {modul}'ü anıyor ama dosya YOK"
