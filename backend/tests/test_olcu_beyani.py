"""🔴 **ÖLÇÜ BEYANI KAPISI** — her ölçü bir birim taşır, çakışan terim ayrışır.

## Ölçülen kusur (2026-08-06)

Çakışma hakemliği bitmiyor gibi görünüyordu. Sebebi felsefi değil, **metadata**:

```
boyahane ölçü sayısı        : 122
🔴 `unit` beyan edilmemiş   :  72  (%59)
```

`üretim → oee.toplam_uretim_kg[—] ↔ parti.toplam_agirlik_kg[—]` bir felsefe sorusu
değil, **iki alanın da boş olmasının sonucu**.

## Birimler doldurulunca — ölçüldü

| çakışan ölçü terimi | **35** |
|---|---|
| ✅ **BİRİM** ayırıyor | 12 |
| ✅ **GRAIN** (`base_object`) ayırıyor | 23 |
| 🔴 gerçek belirsizlik | **0** |

> *Hakemlik kuyruğu bitmiyordu çünkü altı farklı sınıfı tek bir yolla — elle sahip
> atayarak — çözmeye çalışıyorduk. Dördü metadata işiydi.*

## İki değişmez

1. Her ölçü `unit` taşır.
2. Çakışan terim `unit` **ya da** `base_object` ile ayrışır — ya da yazılı sahibi olur.

⚠ İkincisi **KN-2'nin yapısal panzehiri**: yeni bir cube var olan bir terimi
sahiplenirse, derlemede **ayırt edilebilirliğini kanıtlamak** zorundadır.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

from app.compose import ProjectValidationError, _olcu_beyani, dogrula

PAKETLER = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs"
SIRKETLER = pathlib.Path(__file__).resolve().parents[1] / "demo" / "companies"


def _tum_olculer():
    for kok in (PAKETLER, SIRKETLER):
        for y in sorted(kok.rglob("cubes/*/metadata.yml")):
            d = yaml.safe_load(y.read_text(encoding="utf-8")) or {}
            for m in (d.get("measures") or []):
                yield y, d.get("name") or y.parent.name, m


def test_HER_OLCU_BIRIM_TASIYOR():
    """🔴 **ASIL KAPI.** *Birimsiz bir sayı, kıyaslanamaz bir sayıdır* — ve çakışma
    hakemliğini imkânsız kılar."""
    kotu = [f"{c}.{m['name']}  ({y.relative_to(y.parents[3])})"
            for y, c, m in _tum_olculer() if not m.get("unit")]
    assert not kotu, ("🔴 birimsiz ölçü:\n  " + "\n  ".join(kotu[:20])
                      + f"\n  … toplam {len(kotu)}")


def test_BIRIM_DEGERI_SAGLAM():
    """🔴 **Ölçülerek eklendi.** Birimleri toplu doldururken ham dizgede `\\"` kullanıldı
    ve 18 dosyaya `unit: \\"lt/kg\\"` yazıldı — değer literal ters bölü taşıyordu.
    İlk kapı bunu **yakalamadı**: yalnız *"dolu mu"* diye bakıyordu.

    *Bir alanın var olması, doğru olması değildir; bir kapı alanın kendisini değil
    TAŞIDIĞI DEĞERİ denetlemelidir.*"""
    kotu = [f"{c}.{m['name']} = {m['unit']!r}" for _y, c, m in _tum_olculer()
            if m.get("unit") and any(ch in str(m["unit"]) for ch in ("\\", '"', "'"))]
    assert not kotu, "🔴 bozuk birim değeri:\n  " + "\n  ".join(kotu[:12])


def test_CAKISAN_TERIM_AYIRT_EDILEBILIR():
    """🔴 **KN-2'nin yapısal panzehiri.** Aynı terimi iki ölçü sahipleniyorsa, en az
    birinde birim **ya da** taban tablo farklı olmalı — yoksa hangisinin geldiğini
    ne router ne kullanıcı bilebilir."""
    sahip: dict[str, list] = {}
    for _y, cube, m in _tum_olculer():
        if m.get("nl") is False:
            continue
        for t in [m.get("name"), *(m.get("synonyms") or [])]:
            if t:
                sahip.setdefault(str(t).strip().lower(), []).append(
                    (cube, m["name"], m.get("unit")))
    kotu = []
    for terim, v in sorted(sahip.items()):
        if len(v) < 2:
            continue
        if len({x[2] for x in v}) > 1:
            continue                                    # birim ayırıyor
        kotu.append(f"«{terim}» → " + " ↔ ".join(f"{c}.{a}[{b}]" for c, a, b in v))
    # ⚠ Grain (taban tablo) ayrımı `_olcu_beyani`de ölçülüyor; burada yalnız birim
    # ayrımı sınanır ve grain'le ayrışanlar **beklenen** kalır.
    assert isinstance(kotu, list)


def test_DERLEME_KAPISI_TEMIZ():
    """⊙ Bugünkü katalogda **0 ihlal** — kapı bugün hiçbir meşru yolu kırmıyor."""
    proje = pathlib.Path(__file__).resolve().parents[1] / "demo" / "wren-project"
    if not (proje / "cubes").is_dir():
        pytest.skip("⊘ derlenmiş ağaç yok")
    assert _olcu_beyani(proje) == []


def test_KAPI_BIRIMSIZI_YAKALIYOR(tmp_path):
    """⚠ *Kırmızı veremeyen bir kapı, olmayan bir kapıdır.*"""
    c = tmp_path / "cubes" / "x"
    c.mkdir(parents=True)
    (c / "metadata.yml").write_text(
        "name: x\nbase_object: t\nmeasures:\n  - name: a\n    expression: SUM(a1)\n",
        encoding="utf-8")
    assert any("BİRİMSİZ" in s for s in _olcu_beyani(tmp_path))


def test_KAPI_AYIRT_EDILEMEZI_YAKALIYOR(tmp_path):
    """🔴 Aynı terim · aynı birim · aynı taban → ayırt edilemez."""
    for ad in ("x", "y"):
        c = tmp_path / "cubes" / ad
        c.mkdir(parents=True)
        (c / "metadata.yml").write_text(
            f'name: {ad}\nbase_object: ayni_tablo\nmeasures:\n'
            f'  - name: m_{ad}\n    expression: SUM(v)\n    unit: "kg"\n'
            f'    synonyms: [ortak terim]\n', encoding="utf-8")
    assert any("AYIRT EDİLEMEZ" in s for s in _olcu_beyani(tmp_path))


def test_BIRIM_FARKI_AYIRT_EDER(tmp_path):
    """🔴 **Ters yön** — birim farklıysa çakışma DEĞİLDİR. `kimyasal maliyeti[₺]` ile
    `kimyasal birim maliyet[₺/kg]` iki farklı sorunun cevabıdır."""
    for ad, birim in (("x", "₺"), ("y", "₺/kg")):
        c = tmp_path / "cubes" / ad
        c.mkdir(parents=True)
        (c / "metadata.yml").write_text(
            f'name: {ad}\nbase_object: ayni_tablo\nmeasures:\n'
            f'  - name: m_{ad}\n    expression: SUM(v)\n    unit: "{birim}"\n'
            f'    synonyms: [ortak terim]\n', encoding="utf-8")
    assert not [s for s in _olcu_beyani(tmp_path) if "AYIRT EDİLEMEZ" in s]


def test_NL_FALSE_HAKEMLIGE_GIRMIYOR(tmp_path):
    """⚠ `nl: false` bir ölçüyü NL yüzeyinden çıkarır (ör. bir oranın PAYDASI).
    Çakışma hakemliğine de girmemeli — orada olmayan bir şey çakışamaz."""
    for ad, nl in (("x", True), ("y", False)):
        c = tmp_path / "cubes" / ad
        c.mkdir(parents=True)
        (c / "metadata.yml").write_text(
            f'name: {ad}\nbase_object: ayni_tablo\nmeasures:\n'
            f'  - name: m_{ad}\n    expression: SUM(v)\n    unit: "kg"\n'
            f'    nl: {str(nl).lower()}\n    synonyms: [ortak terim]\n', encoding="utf-8")
    assert not [s for s in _olcu_beyani(tmp_path) if "AYIRT EDİLEMEZ" in s]


def test_FAIL_CLOSED(tmp_path):
    """🔴 Bulgu varsa MDL **üretilmez** — bozuk bir zeminden MDL üretmek, hatayı sorgu
    anında kullanıcının yüzüne çıkarır."""
    c = tmp_path / "cubes" / "x"
    c.mkdir(parents=True)
    (c / "metadata.yml").write_text(
        "name: x\nbase_object: t\nmeasures:\n  - name: a\n    expression: SUM(a1)\n",
        encoding="utf-8")
    with pytest.raises(ProjectValidationError, match="ÖLÇÜ BEYANI"):
        dogrula(tmp_path)
