"""🔴 `§D4` — `unit: "%"` AYNI KATALOGDA **İKİ ÖLÇEK** ANLAMINA GELİYORDU.

## Raporun D4 kartı ne diyordu — ve ölçüm ne dedi

| kartın iddiası | ölçülen (2026-08-12) |
|---|---|
| `Intl.NumberFormat("tr-TR",{style:"percent"})` → **`%56`**, 0 ondalık | ✅ doğru **ama ön-uç bunu KULLANMIYOR**: `format.ts` `{maximumFractionDigits: 2}` + birim eki → `55,55 %` (ondalık **korunuyor**) |
| `d3-format`'ta `tr-TR` locale'i **YOK** | ⊘ `d3-format` **hiç kullanılmıyor** — bağımlılık da import da yok |
| kompakt **`12 B`** = bin, İngilizcede milyar | ✅ ölçüldü: `12 B` · `1,2 Mn` · `1,2 Mr` — **Türkçesi doğru** |

⊙ Yani kartın **üç dayanağı da** bugünkü kodda karşılıksız. Ama ölçüm **başka ve daha
ağır** bir şey buldu.

## 🔴 ASIL KUSUR — ölçek ilanı ile değer birbirini tutmuyordu

Canlı (bu oturumda iki kez, bağımsız):

    «bölüm bazında oee»  → {"bolum": "Örgü", "ort_oee": 0.6411370547282164}
    «bu yıl ortalama oee» → özet: «Oee 0,58 %.»

`ort_oee` katalogda **`unit: "%"`** ilan ediyor ama değeri **0–1 oranı**. Kullanıcı
`0,58 %` okuyor; kastedilen **%58**. **100× yanlış** — ve hiçbir uyarı yok.

Ve aynı küpteki kardeşi `ilk_seferde_tamam_yuzde` **zaten ×100**. Yani `%` **tek bir
küpte iki farklı ölçek** demekti — bu deponun avladığı *«aynı kuralın iki anlamı»*
sınıfı, sunum katmanında.

## Düzeltme — ve neden KATALOGDA

Sunum katmanı bir sayının 0–1 mi 0–100 mü olduğunu **bilemez**; büyüklüğe bakıp tahmin
etmek bir **heuristik** olurdu (`ADR-0008`: liste/heuristikle dil kovalama yasak) ve
gerçekten %0,8 olan bir ölçüyü 100× şişirirdi. Ölçeği **ilan eden** taraf katalogdur.

Dört OEE oranı kardeşlerinin kuralına getirildi (`×100`, `ROUND 2`):
`ort_oee` · `ort_kullanilabilirlik` · `ort_performans` · `ort_kalite`.

## ⚠ KAPSAM DIŞI BIRAKILAN — ve gerekçesi

`maliyet.ort_kar_marji_yuzde` = `ROUND(AVG(kar_marji_yuzde),2)`. Kaynak **kolonun kendi
adı** `_yuzde`; yani muhtemelen **zaten** 0–100. İfadede `100` geçmediği için ilk kaba
taramam onu *«oran»* diye işaretledi — **yanlış pozitif**. Değerini doğrulayamadığım için
**dokunmadım**.

> *Bir ölçek düzeltmesi, ölçeği ölçülmemiş bir ölçüye uygulanırsa, düzelttiğinden fazlasını
> bozar.* Bu turda kaba ölçüm **dört kez** sahte kusur üretti; bu, beşincisi olabilirdi.
"""

from __future__ import annotations

import pathlib

import yaml

_PACKS = pathlib.Path(__file__).parent.parent / "demo" / "packs"
#: Ölçeği **doğrulanamayan** ve bu yüzden bilerek dokunulmayan ölçüler. Bir gün değeri
#: ölçülürse ya listeden çıkar ya da düzeltilir — ama **sessizce** kalmaz.
OLCULMEDI = {"maliyet.ort_kar_marji_yuzde"}


def _yuzde_olculeri() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in _PACKS.rglob("metadata.yml"):
        try:
            d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for m in (d.get("measures") or []):
            if isinstance(m, dict) and m.get("unit") == "%":
                out[f"{p.parent.name}.{m['name']}"] = str(m.get("expression") or "")
    return out


def test_YUZDE_OLCULERI_bulunuyor():
    """⚠ Ön koşul: tarayıcı gerçekten dosyaları buluyor mu. İlk sürümü **yanlış dizinden**
    koştu ve `0` buldu — bu turda aracın on ikinci sahte sonucu."""
    assert len(_yuzde_olculeri()) >= 15


def test_OEE_ORANLARI_artik_YUZDE():
    """🔴 Kusurun ta kendisi: `0,58 %` yerine `%58`."""
    o = _yuzde_olculeri()
    for ad in ("oee.ort_oee", "oee.ort_kullanilabilirlik",
               "oee.ort_performans", "oee.ort_kalite"):
        assert ad in o, f"{ad} kayboldu"
        assert "100" in o[ad], f"{ad} hâlâ 0-1 oranı — kullanıcı 100× küçük görür"


def test_AYNI_KUPTE_TEK_OLCEK():
    """`%` bir küpte **iki şey** anlatamaz: `ilk_seferde_tamam_yuzde` zaten ×100'dü."""
    o = {k: v for k, v in _yuzde_olculeri().items() if k.startswith("oee.")}
    assert o, "oee küpünde % ölçüsü kalmamış"
    assert all("100" in v for v in o.values()), (
        f"oee küpünde ölçek karışık: {[k for k, v in o.items() if '100' not in v]}")


def test_OLCULMEYEN_olcu_SESSIZCE_kalmiyor():
    """*Bir ölçek düzeltmesi, ölçeği ölçülmemiş bir ölçüye uygulanırsa düzelttiğinden
    fazlasını bozar.* Dokunulmayan kalem **adıyla** kayıtlı."""
    o = _yuzde_olculeri()
    for ad in OLCULMEDI:
        assert ad in o, f"{ad} katalogdan kalkmış — kayıt güncellensin"


def test_YENI_ORAN_OLCUSU_sessizce_GIREMEZ():
    """🔴 Yayılma kapısı: bundan sonra `unit: \"%\"` ilan eden her ölçü ya **×100**
    içerir ya da `OLCULMEDI`'ye **gerekçesiyle** yazılır."""
    kacak = [k for k, v in _yuzde_olculeri().items()
             if "100" not in v and k not in OLCULMEDI]
    assert not kacak, (
        "🔴 `unit: \"%\"` ilan edip 0-1 oranı üreten YENİ ölçü(ler):\n  "
        + "\n  ".join(kacak)
        + "\n\nKullanıcı bunları 100× küçük görür. Ya ifadeye `100.0 *` ekle, ya da "
          "değerini ÖLÇÜP `OLCULMEDI`'ye gerekçesiyle yaz — sessiz bırakma.")
