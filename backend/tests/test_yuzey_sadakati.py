"""FAZ 0.14 / **K4 — YÜZEY SADAKATİ**: aynı cevap her yüzeyde AYNI garantiyi beyan eder.

## Kural

`MIMARI §5`: *"bir cevabın `source`'unu gizlemek ya da eşitlemek"* **yasaktır** — rozet
bir süs değil, bir **sözleşmedir**. Kullanıcı `▚ LLM` ile `⛁ küp` arasındaki farkı
görebilmelidir; aynı cevabı bir yüzeyde rozetli, ötekinde rozetsiz göstermek o sözleşmeyi
sessizce deler.

## Bugün

`viz` tarafı zaten kilitli (`test_faz_I4_I5`). Bu kapı onu **rozet/makbuz/`explain`**
eksenine genişletir.
"""

from __future__ import annotations

import pytest

from tests.kapi_ortak import fe_dosyalari

#: Bir cevabı **kart olarak** render eden yüzeyler. Her biri `source` rozetini basmalı.
CEVAP_YUZEYLERI = ("components/ReportCard.tsx", "components/AnalysisCanvas.tsx")

#: Rozetsiz kalması KABUL EDİLEN yüzeyler — her biri bir SAHİP gösterir.
ROZETSIZ_MUAF: dict[str, str] = {
    "components/AnalysisCanvas.tsx":
        "🔴 ÖLÇÜLDÜ ihlal [KANIT §0.1-2]: `SourceBadge` 0, `explain` 0 — aynı cevap "
        "sohbette `▚ LLM` rozetli, tuvalde ROZETSİZ. **FAZ 0.3**'ün konusu: "
        "`ChatPanel.SourceBadge` YENİDEN KULLANILIR, ikinci render edici yazılmaz. "
        "Muafiyet 0.3'te KALKAR.",
}


def test_K4_HER_CEVAP_YUZEYI_SOURCE_ROZETI_BASAR():
    """🔴 **ASIL KAPI.** Bir yüzey cevabı gösteriyorsa `source`'u da göstermeli."""
    dosyalar = fe_dosyalari()
    eksik = []
    for yol in CEVAP_YUZEYLERI:
        if yol not in dosyalar:
            pytest.skip(f"{yol} bulunamadı — çapa kaymış")
        if yol in ROZETSIZ_MUAF:
            continue
        if "SourceBadge" not in dosyalar[yol]:
            eksik.append(yol)
    assert not eksik, (
        "ROZETSİZ CEVAP YÜZEYİ (MIMARI §5 ihlali — `source` gizlenemez):\n  "
        + "\n  ".join(eksik)
        + "\n\nRozet süs değil SÖZLEŞMEDİR: kullanıcı `▚ LLM` ile `⛁ küp` farkını "
          "görmelidir. `ChatPanel.SourceBadge`'i YENİDEN KULLAN, ikinci render edici yazma.")


def test_K4_ROZETSIZ_MUAF_her_satirda_SAHIP_gosterir():
    """Muafiyet bir kusuru gizlemez, **sahibine işaret eder**."""
    for yol, gerekce in ROZETSIZ_MUAF.items():
        assert "FAZ" in gerekce, f"`{yol}` muafiyeti bir SAHİP göstermiyor"
        assert "KALKAR" in gerekce, f"`{yol}` muafiyeti ne zaman kalkacağını söylemiyor"


def test_K4_MUAF_BAYATLAMAZ():
    dosyalar = fe_dosyalari()
    olmayan = sorted(y for y in ROZETSIZ_MUAF if y not in dosyalar)
    assert not olmayan, f"ROZETSIZ_MUAF'ta artık var olmayan yüzey(ler): {olmayan}"


def test_K4_MUAF_KENDILIGINDEN_ERIMEZ():
    """🔴 Ters yön: muaf bir yüzey rozeti **eklerse** muafiyet KALDIRILMALI — yoksa
    liste bir çöplüğe döner ve kapı gerçekte neyi koruduğunu söyleyemez hâle gelir."""
    dosyalar = fe_dosyalari()
    artik_basiyor = [y for y in ROZETSIZ_MUAF
                     if y in dosyalar and "SourceBadge" in dosyalar[y]]
    assert not artik_basiyor, (
        f"Bu yüzey(ler) ARTIK rozet basıyor — muafiyeti KALDIR: {artik_basiyor}")
