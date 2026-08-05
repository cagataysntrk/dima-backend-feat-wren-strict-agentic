"""🔴 KÖK-5c — **bir ölçünün ifadesi kendi adına referans veremez.** (Derleme kapısı)

## Neden bu kapı var — ölçülmüş kusur

Denetim raporu **KN-6** (2026-08-05):

```yaml
- name: iade_kg
  expression: SUM(iade_kg)     # ← ölçünün ADI == ifadesindeki KOLON adı
```

Motor bunu **derlemede kabul ediyor**: `mdl.json` üretiliyor, `sikayet` cube'u katalogda
**görünüyor**, `validate_project` **hiçbir şey demiyor**. Kusur ancak o cube'a bir sorgu
dokunduğunda çıkıyor — ve **cube düzeyinde**:

> `[INVALID_SQL] Cube 'sikayet': circular dependency detected in measure expressions
> phase=SQL_PLANNING`

Tek YAML satırı, **6 ölçü + 9 boyutu** birden öldürüyor.

## Ve asıl tehlike hata mesajı DEĞİL

Kullanıcı bu hatayı **hiç görmüyor**: `route()` ölü cube'a ulaşamıyor → soru
**Discovery'ye** düşüyor → LLM ham SQL yazıyor → **bir sayı dönüyor**. Yani katalog
kusuru, kullanıcıya *"başka bir yoldan gelmiş bir cevap"* olarak ulaşıyor.

*Bir katalog kusuru bir kullanıcı deneyimi olmamalıdır.*
"""

from __future__ import annotations

import pathlib
import re

import pytest
import yaml

from app.compose import _ozyineli_olcu

PAKETLER = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs"


def _cube_dosyalari() -> list[pathlib.Path]:
    return sorted(PAKETLER.rglob("cubes/*/metadata.yml"))


def test_KAYNAK_KATALOGDA_OZ_REFERANS_YOK():
    """🔴 **ASIL KAPI** — bütün paket kataloğu, cube başına.

    ⚠ Derlenmiş çıktıya değil **kaynağa** bakar: derlenmiş ağaç bir türev, kusur
    kaynakta doğar ve düzeltme de orada yapılır."""
    kotu = []
    for y in _cube_dosyalari():
        d = yaml.safe_load(y.read_text(encoding="utf-8")) or {}
        cube = d.get("name") or y.parent.name
        for m in (d.get("measures") or []):
            ad, ifade = m.get("name"), str(m.get("expression") or "")
            if ad and ifade and ad in set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", ifade)):
                kotu.append(f"{cube}.{ad} → {ifade}  ({y.relative_to(PAKETLER)})")
    assert not kotu, (
        "🔴 ÖZ-REFERANSLI ÖLÇÜ:\n  " + "\n  ".join(kotu) +
        "\n\nYAPILACAK: ölçüyü yeniden adlandır (`iade_kg` → `toplam_iade_kg`); "
        "ifade AYNI kalır. Sinonimler korunursa kullanıcı yüzeyi hiç değişmez.")


def test_KAPI_GERCEKTEN_KIRMIZI_VERIYOR(tmp_path):
    """⚠ *Kırmızı veremeyen bir kapı, olmayan bir kapıdır.*

    Kusurlu deseni **enjekte edip** kapının onu yakaladığını ölçer — kapının kendi
    doğruluğu, koruduğu kuraldan bağımsız olarak sınanmalıdır."""
    cubes = tmp_path / "cubes" / "deneme"
    cubes.mkdir(parents=True)
    (cubes / "metadata.yml").write_text(
        "name: deneme\nmeasures:\n  - name: iade_kg\n    expression: SUM(iade_kg)\n",
        encoding="utf-8")
    bulgu = _ozyineli_olcu(tmp_path)
    assert bulgu and "deneme.iade_kg" in bulgu[0], f"kapı deseni kaçırdı: {bulgu}"


def test_MESRU_OLCU_YANLIS_POZITIF_VERMIYOR(tmp_path):
    """🔴 **Ters yön — bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.**

    Kolon adı ölçü adından farklı olduğu sürece desen meşrudur ve katalogda **çoğunluk**
    budur (`toplam_fire_kg → SUM(fire_kg)`). Kapı bunları yakalarsa 172 ölçünün
    neredeyse tamamını kırar."""
    cubes = tmp_path / "cubes" / "deneme"
    cubes.mkdir(parents=True)
    (cubes / "metadata.yml").write_text(
        "name: deneme\n"
        "measures:\n"
        "  - name: toplam_fire_kg\n    expression: SUM(fire_kg)\n"
        "  - name: ort_dE\n    expression: \"ROUND(AVG(uretim_dE),3)\"\n"
        "  - name: adet\n    expression: \"COUNT(*)\"\n",
        encoding="utf-8")
    assert _ozyineli_olcu(tmp_path) == []


def test_DERLEME_FAIL_CLOSED(tmp_path):
    """🔴 Kapı **fail-closed**: bulgu varsa MDL **üretilmez**.

    ⚠ *Bozuk bir zeminden MDL üretmek, hatayı sorgu anında kullanıcının yüzüne çıkarır*
    — `dogrula()`'nın kendi gerekçesi. Öz-referans tam olarak o sınıftır: derleme
    sessiz, sorgu gürültülü."""
    from app.compose import ProjectValidationError, dogrula

    cubes = tmp_path / "cubes" / "deneme"
    cubes.mkdir(parents=True)
    (cubes / "metadata.yml").write_text(
        "name: deneme\nmeasures:\n  - name: x\n    expression: SUM(x)\n", encoding="utf-8")
    with pytest.raises(ProjectValidationError, match="ÖZ-REFERANSLI"):
        dogrula(tmp_path)


def test_SIKAYET_CUBE_CANLI():
    """⊙ KN-6'nın somut kurbanı: `sikayet`'in **6 ölçüsü + 9 boyutu**.

    Ad düzeltildi (`iade_kg` → `toplam_iade_kg`), **sinonimler korundu** — yani
    kullanıcının yazdığı *"iade"* hâlâ aynı ölçüye gidiyor. *Bir düzeltme, düzelttiği
    yüzeyi de değiştirirse, düzeltme değil bir değişikliktir.*"""
    y = PAKETLER / "sektor/boyahane/cubes/sikayet/metadata.yml"
    d = yaml.safe_load(y.read_text(encoding="utf-8"))
    olculer = {m["name"]: m for m in d["measures"]}
    assert "toplam_iade_kg" in olculer, "🔴 ölçü yeniden adlandırılmamış"
    assert "iade_kg" not in olculer, "🔴 öz-referanslı ad geri gelmiş"
    assert olculer["toplam_iade_kg"]["expression"] == "SUM(iade_kg)", \
        "🔴 ifade değişmiş — düzeltme yalnız ADI değiştirmeliydi"
    assert "iade" in olculer["toplam_iade_kg"]["synonyms"], \
        "🔴 kullanıcı yüzeyi (sinonim) kaybolmuş"
