"""FAZ 7.1 kapısı — **bayrak sistemi TEK.** [bayraksız: değişmez]

## Yol haritasının teşhisi — ve bu daldaki ölçüm

Yol haritası *"bugün **ÜÇ paralel sistem**: `useFeature()` · `useUiFlag()` ·
`NEXT_PUBLIC_*`"* diyordu. **Ölçüldü: o teşhis TERK EDİLEN DAL içindi.** Bu dalda:

| sistem | ölçüm |
|---|---|
| `useFeature()` | ✅ tek tüketici |
| `uiFlags.ts` / `useUiFlag()` | **0** — dosya bile yok |
| `NEXT_PUBLIC_*` bayrağı | **0** *(tek `NEXT_PUBLIC_SESSION_COOKIE` var; o bir **çerez adı**, bayrak değil)* |

> 🔴 MIMARI §6.13z/9.11: *"kill-switch yalnız KOD'da varsa **YARIMDIR**."*

Yani iş **birleştirme** değil, **kilitleme**: ikinci bir sistem doğduğu gün bu kapı
kırmızı olur. *Bir dalda çözülmüş bir sorun, kilitlenmediyse çözülmemiştir.*

## İkinci ve daha önemli şart

Frontend'de okunan **her bayrak adı** `FLAG_REGISTRY`'de olmalı. Olmayan bir ad
`getFeatures()` yanıtında **hiç görünmez** → `useFeature` hep `null` döner → özellik
**sessizce ölür** ve kimse fark etmez.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_FE = Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"

pytestmark = pytest.mark.skipif(not _FE.exists(), reason="⊘ frontend ağacı yok")


def _fe_kaynak() -> str:
    return "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in _FE.rglob("*.ts*"))


def test_IKINCI_bayrak_sistemi_YOK():
    """🔴 *Bir dalda çözülmüş bir sorun, kilitlenmediyse çözülmemiştir.*"""
    assert not (_FE / "lib" / "uiFlags.ts").exists(), (
        "🔴 `uiFlags.ts` geri gelmiş — ikinci bir bayrak sistemi, bir kill-switch'in "
        "hangi yarısının çalıştığını belirsiz yapar.")
    kaynak = _fe_kaynak()
    assert "useUiFlag" not in kaynak, "🔴 `useUiFlag` geri gelmiş."


def test_ENV_bayragi_YOK():
    """⚠ `NEXT_PUBLIC_SESSION_COOKIE` bir **çerez adıdır**, bayrak değil — ve ayrım
    yazılı olmalı ki bir gün biri onu 'zaten env kullanıyoruz' diye örnek almasın."""
    kaynak = _fe_kaynak()
    envler = set(re.findall(r"NEXT_PUBLIC_[A-Z0-9_]+", kaynak))
    izinli = {"NEXT_PUBLIC_SESSION_COOKIE"}
    fazla = sorted(envler - izinli)
    assert not fazla, (
        f"🔴 Env üzerinden bayrak okunuyor: {fazla}. Bir kill-switch env'deyse, onu "
        f"kapatmak bir DEPLOY gerektirir — oysa bayrağın tüm amacı deploy'suz "
        f"kapatabilmektir.")


def test_HER_useFeature_adi_FLAG_REGISTRYde_var():
    """🔴 Kayıtta olmayan bir ad `getFeatures()` yanıtında **hiç görünmez** → `useFeature`
    hep `null` döner → özellik **sessizce ölür** ve kimse fark etmez.

    *Sessizce ölen bir özellik, yazılmamış bir özellikten kötüdür: bedeli ödenmiştir.*
    """
    from app.features import FLAG_REGISTRY

    adlar = set(re.findall(r'useFeature\(\s*"([a-z0-9_]+)"', _fe_kaynak()))
    assert adlar, "hiç `useFeature` çağrısı bulunamadı — test bir şey korumuyor"
    eksik = sorted(adlar - set(FLAG_REGISTRY))
    assert not eksik, (
        f"🔴 Frontend'de okunan ama `FLAG_REGISTRY`'de OLMAYAN bayrak(lar): {eksik}\n"
        f"`useFeature` bu adlar için hep `null` döner ve özellik sessizce ölür.")


def test_HER_useFeature_adi_features_YAMLde_de_var():
    """⚠ Kayıtta olup **fabrika varsayılanı yazılmamış** bir bayrak da `null` döndürür.

    İki liste ayrı ayrı doğrudur ama **birlikte** eksik olabilir — ve bu, tek tek
    bakıldığında görünmez.
    """
    from pathlib import Path as _P

    import yaml

    d = yaml.safe_load((_P(__file__).resolve().parents[1] / "demo/packs/features.yml")
                       .read_text(encoding="utf-8"))
    yml = set((d or {}).get("features") or {})
    adlar = set(re.findall(r'useFeature\(\s*"([a-z0-9_]+)"', _fe_kaynak()))
    eksik = sorted(adlar - yml)
    assert not eksik, (
        f"🔴 Frontend okuyor ama `features.yml`'de fabrika varsayılanı YOK: {eksik} — "
        f"`getFeatures()` onu döndürmez ve özellik sessizce ölür.")


def test_KILL_SWITCH_kodun_DISINDA_da_var():
    """🔴 MIMARI §6.13z/9.11: *"kill-switch yalnız KOD'da varsa YARIMDIR."*

    Her frontend bayrağının bir **DB override** yolu olmalı — yani `FLAG_REGISTRY`
    üzerinden çözülmeli (`resolve_for` zaten `global < sektör < tenant < rol <
    kullanıcı` sırasını uyguluyor). Bir bileşen bayrağı `if (true)` gibi sabitlerse,
    kapatma yolu **kodda kalır**.
    """
    kaynak = _fe_kaynak()
    # Sabitlenmiş bayrak deseni: `const X = true;` biçiminde bir "flag" adı.
    sabitler = re.findall(r"const\s+([A-Za-z0-9_]*[Ff]lag[A-Za-z0-9_]*)\s*=\s*true",
                          kaynak)
    assert not sabitler, (
        f"🔴 Sabitlenmiş bayrak: {sabitler}. Kapatma yolu kodda kalırsa kill-switch "
        f"YARIMDIR — kapatmak bir deploy gerektirir.")
