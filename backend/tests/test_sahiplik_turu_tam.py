"""🔴🔴 `B-6`/`B-4` — **ÇOK SAHİPLİ HER ÖLÇÜNÜN BİR KARARI OLMALI.**

## Ölçülen kusur

Canlı derlenmiş şemada **9** çok sahipli ölçü adı var; `sahiplik_kararlari.yml`'de
**6'sının kararı yoktu**. Rapor `B-4`: *"boş bırakmak üçüncü bir seçenek değildir"* —
bugün olan da oydu ve maliyeti kayıtlı: `bakiye` iki küpte, fark **₺11,86 milyon**,
seçim **sessiz**.

## Üç kutu, ve boş bırakmak bunlardan biri DEĞİL

| kutu | ne demek |
|---|---|
| `tek_sahip` | terim aslında bir küpün — hakem karar verir |
| `belirsiz` | kullanıcı hangisini kastettiği belli değil — **chip sorar** |
| `grain_hatasi` | iki küp aynı grain'de — modelleme borcu |

⚠ `belirsiz` bir **eksiklik değil bir karardır**: *gerçek belirsizliği tahminle
kapatmak, belirsizliği yok etmez — yalnız görünmez kılar.*
"""

from __future__ import annotations

import pathlib

import yaml

_KARAR = (pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs" /
          "cekirdek" / "sahiplik_kararlari.yml")
_KUTULAR = {"tek_sahip", "belirsiz", "grain_hatasi"}


def _kararlar() -> list[dict]:
    return (yaml.safe_load(_KARAR.read_text(encoding="utf-8")) or {}).get("kararlar") or []


def _cok_sahipli(schema) -> set[str]:
    from app.katalog_metni import cok_sahipli_olculer

    return set(cok_sahipli_olculer(schema.get("cubes") or []))


def test_HER_COK_SAHIPLI_OLCUNUN_KARARI_VAR(schema):
    """🔴 Çıkış ölçütü: **boş bırakılan kalem 0**.

    ⚠ Eşleşme `hakem()` gibi tam terim değil, **terim ↔ ölçü adı** üzerinden kurulur:
    karar `fire` yazar, ölçü `toplam_fire_kg`'dir. Kapı bu köprüyü **gevşek** tutar
    (terim ölçü adının içinde geçiyorsa sayılır) çünkü amacı eşleştirmeyi sınamak
    değil, **karar verilmemiş kalem kalmadığını** sınamaktır.
    """
    kapsanan: set[str] = set()
    terimler: list[str] = []
    for k in _kararlar():
        # 🔴 Önce **beyan** (`olculer:`), sonra alt-dize köprüsü. Beyan, tahminden
        # önce gelir — *bir bağı tahmine bırakmak, onu bir gün sessizce kopmaya
        # bırakmaktır.*
        kapsanan.update(str(a) for a in (k.get("olculer") or []))
        terimler.append(str(k.get("terim") or ""))
    kararsiz = [ad for ad in sorted(_cok_sahipli(schema))
                if ad not in kapsanan
                and not any(t and t.replace(" ", "_") in ad for t in terimler)]
    assert not kararsiz, (
        f"🔴 {len(kararsiz)} çok sahipli ölçünün kararı YOK: {kararsiz}\n"
        "  `demo/packs/cekirdek/sahiplik_kararlari.yml`'ye ya `tek_sahip` (sahip yaz) "
        "ya `belirsiz` (chip sorsun) ya da `grain_hatasi` yazılmalı.\n"
        "  ⚠ Boş bırakmak DÖRDÜNCÜ bir seçenek değildir — sistem o hâlde kura ile "
        "seçer, seçtiğini söylemez ve `bakiye` vakasında bu ₺11,86 milyona mal oldu.")


def test_HER_KARAR_KUTUSUNU_VE_GEREKCESINI_TASIR():
    """*Gerekçesiz bir karar, bir karar değil bir tercihtir.*"""
    for k in _kararlar():
        assert k.get("kutu") in _KUTULAR, f"{k.get('terim')}: geçersiz kutu {k.get('kutu')}"
        assert len((k.get("gerekce") or "").strip()) >= 40, \
            f"{k.get('terim')}: gerekçe çok kısa/yok"
        assert k.get("tarih"), f"{k.get('terim')}: tarih yok"


def test_TEK_SAHIP_KUTUSU_SAHIP_YAZAR_OTEKILER_YAZMAZ():
    """🔴 `belirsiz` bir sahip yazarsa, belirsizlik sessizce kapanır — kutunun anlamı ölür."""
    for k in _kararlar():
        if k.get("kutu") == "tek_sahip":
            assert k.get("sahip"), f"{k.get('terim')}: tek_sahip ama sahip yok"
        else:
            assert not k.get("sahip"), (
                f"{k.get('terim')}: `{k.get('kutu')}` kutusunda sahip YAZILAMAZ — "
                "yazılırsa kutu bir karar olmaktan çıkar")
