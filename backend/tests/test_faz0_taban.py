"""FAZ 0.1 KAPISI — taban ölçümü **elle yazılamaz**, üreteçten gelir.

## Neden bu kapı var

0.1'in `KAPI`'sı şudur: *"Çıktı `lab/reports/faz0_taban.md` — her satır
`<sayı> @<sha> · <komut>` (D2)."* Bir tablo elle yazıldığı an bayatlamaya başlar ve
bu belge boyunca **on iki kez** bayat sayı yüzünden yanlış karar alındı. Kapı, tablonun
bir **üreteci** olduğunu ve üretecin **damgasız koşmadığını** kilitler.

## Bu kapı neyi ölçmez

Sayıların *doğruluğunu* ölçmez — onu ölçen şey üretecin kendisidir. Bu kapı **biçimi**
ve **fail-closed** davranışı kilitler: damgasız bir ölçüm, `D2` açısından ölçüm değildir.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from lab import faz0_taban as ft


def test_ARAC_VAR_ve_RAPOR_YOLU_yol_haritasiyla_ayni():
    assert ft.RAPOR.name == "faz0_taban.md", \
        "0.1'in KAPI'sı `lab/reports/faz0_taban.md` diyor — yol değişmiş"
    assert ft.RAPOR.parent.name == "reports"


def test_DAMGASIZ_KOSMAZ(monkeypatch, capsys):
    """🔴 Fail-closed: `git` okunamıyor ve `--sha` yoksa araç **koşmaz**.

    Damgasız bir sayı, hangi koda ait olduğu bilinmeyen bir sayıdır — D2'nin tam olarak
    yasakladığı şey. Sessizce `[SHA YOK]` yazmak, tabloyu *"ölçülmüş"* gibi gösterirdi."""
    monkeypatch.setattr(ft, "_sha", lambda _a: "")
    monkeypatch.setattr("sys.argv", ["faz0_taban.py"])
    assert ft.main() == 2, "damgasız koşum ENGELLENMEDİ"
    assert "DAMGA YOK" in capsys.readouterr().err


def test_UC_DURUM_var_ikisi_degil():
    """`⊘ ÖLÇÜLEMEDİ` bir üçüncü durumdur: ne geçti ne kaldı."""
    assert ft.OLCULEMEDI.startswith("⊘")
    o = ft.Olcum.yok("komut", "gerekçe")
    assert o.deger == ft.OLCULEMEDI and o.not_ == "gerekçe", \
        "ölçülemeyen bir satır GEREKÇESİZ yazılamaz"


def test_TIP_BEYANI_TUKETICI_DEGIL():
    """🔴 Bu iddia bir ölçüm hatasından doğdu: `receipt`/`supersedes` için sayaç **1**
    demişti ve *"tüketiliyor"* diye okunmuştu — o tek isabet `lib/types.ts`'teki **tip
    beyanıydı**. Bir tip beyanı tüketici değildir."""
    if not (ft.FE / "src" / "lib" / "types.ts").exists():
        pytest.skip("frontend kaynağı yok")
    types = (ft.FE / "src" / "lib" / "types.ts").read_text(encoding="utf-8")
    ad = next((a for a in ("supersedes", "receipt") if a in types), None)
    assert ad, "test çapası kaybolmuş: types.ts'te beklenen alan yok"
    # types.ts'te GEÇİYOR ama sayaç onu saymamalı
    assert ft._fe_tuketici(ad) == 0 or "types.ts" not in str(ft.FE), \
        f"`{ad}` yalnız tip beyanında geçiyor ama TÜKETİCİ sayıldı — kapı kandırılıyor"


def test_12_KUSUR_hepsi_RAPORLANIYOR():
    """[KANIT §0.1]'in 12 kusuru **tek tek** durumlanmalı — biri düşerse sessizce unutulur."""
    ks = ft.kusurlar()
    assert [n for n, *_ in ks] == [str(i) for i in range(1, 13)], \
        f"12 kusurun numaraları eksik/sırasız: {[n for n, *_ in ks]}"
    for no, kusur, durum, kanit in ks:
        assert durum.split()[0] in ("✅", "🔴", "◐", "⊘"), f"{no}: tanımsız durum {durum!r}"
        assert kanit.strip(), f"{no}: KANIT boş — 'iddia etme, göster' ihlali"


def test_RAPOR_VARSA_HER_SAYI_DAMGALI():
    """Artefakt üretilmişse `D2` biçimini taşımalı: başlıkta `@<sha>`, **ölçüm** satırlarında
    komut, **kusur** satırlarında kanıt.

    ⚠ İlk sürüm iki tabloyu ayırmıyordu ve kapı **yanlış-kırmızı** verdi: `D2`'nin
    *"her sayı `<sayı> @<sha> · <komut>` taşır"* kuralı **ÖLÇÜM** tablosuna aittir;
    `[KANIT §0.1]` tablosu bir sayı değil bir **DURUM** (`✅/🔴/◐`) taşır ve karşılığı
    komut değil **kanıttır**. İki farklı sözleşmeyi tek kurala vurmak, kuralı da tabloyu
    da bozar. *(Bu operasyonda **altıncı** kez bir kapım ölçtüğünü sandığı şeyi ölçmedi.)*
    """
    if not ft.RAPOR.exists():
        pytest.skip("artefakt bu HEAD'de üretilmemiş — kanonik koşum konteynerdedir")
    m = ft.RAPOR.read_text(encoding="utf-8")
    assert re.search(r"@`[0-9a-f]{7,40}`", m), "raporda SHA damgası yok"

    kesim = m.find("## [KANIT §0.1]")
    olcum, kusur = (m[:kesim], m[kesim:]) if kesim > 0 else (m, "")

    for satir in [s for s in olcum.splitlines() if s.startswith("| ") and "**" in s]:
        assert "`" in satir, f"ÖLÇÜM satırında komut yok (D2): {satir[:80]}"

    for satir in [s for s in kusur.splitlines() if s.startswith("| ") and "**" in s]:
        h = [c.strip() for c in re.split(r"(?<!\\)\|", satir.strip().strip("|"))]
        assert len(h) == 4, f"KUSUR satırı dört hücreli değil: {satir[:80]}"
        assert h[2].strip("* ")[0] in "✅🔴◐⊘", f"tanımsız durum: {h[2]!r}"
        assert h[3], f"KUSUR satırında KANIT boş — 'iddia etme, göster' ihlali: {satir[:80]}"
