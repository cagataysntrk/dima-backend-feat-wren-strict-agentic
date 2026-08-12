"""🔴 ④+⑤ — BİR SAHİPLİK KARARININ **FİYATI** KORPUSTA GÖRÜNÜR, VE BU BİR KUSUR DEĞİLDİR.

## Ölçülen (2026-08-12)

`lab/reports/nl_corpus.md`'deki yanlış-cube satırlarının çiftleri:

| beklenen → seçilen | adet | yazılı karar |
|---|---|---|
| `karlilik` → `ticaret` | **21** | `satis` → `ticaret` *(çekirdek, 2026-08-04)* |
| `mal` → `ticaret` | **8** | aynı karar (`mal` stok hareketidir, satışın kendisi değil) |
| `enerji_makine` → `surdurulebilirlik` | **4** | `tep` → `surdurulebilirlik` *(çekirdek, 2026-08-10)* |
| `oee` → `parti` | 5 | `fire` → `parti` *(çekirdek, 2026-08-10)* |

⊙ Listelenen 40 satırın **33'ünde** sistem, yazılı bir kararın **söylediği** küpü
seçmiş. Yani bu satırlar kararın **kusuru** değil **FİYATIDIR**.

## Neden bu bir kapı

Korpusun *«beklenen»*i bir anlam yargısı değil, sorunun **üretildiği küpün kaydıdır**.
Bir terime sahip atandığı anda, öteki küpten üretilmiş sorular **tanımı gereği**
kırmızıya döner. Bunu bilmeyen biri iki yoldan birine sapar:

* ① kararı **geri alır** (*"bak, 21 soru kırmızı"*) — ve gerçek bir düzelmeyi bozar;
* ② sinonimi **siler** — ki bu deney `surdurulebilirlik`te **ölçüldü**: yanlış-cube
  245→135 **ama erişim %64→%56**, `eval_gate` kırmızı. Deponun kendi cümlesi:
  *«Doğru çözüm bir SAHİPLİK KARARIDIR, kimlik silmek değil.»*

Bu dosya o iki sapmayı **pahalı** kılar: bir karar geri alınırsa test konuşur ve
gerekçesini okutur.

> *Bir kararın fiyatını ödemeyi reddetmek, kararı almamış olmaktır.*

## ⚠ Ne YAPMIYOR

Korpusun puanlamasını **düzeltmiyor** (*«sahibi seçtiyse doğru say»*). O bir ölçüm
altyapısı işidir ve kullanıcının bağlayıcı kuralıyla **park**: *«ölçüm/altyapı tesisatı
ürün değildir»*. Burada yapılan tek şey, ödenen fiyatı **yazılı** kılmaktır — ki bir gün
biri onu bir kusur sanıp geri almasın.
"""

from __future__ import annotations

import pathlib

import yaml

_PACKS = pathlib.Path(__file__).parent.parent / "demo" / "packs"

#: 🔴 Ölçülmüş kararlar: `terim → sahip`. Liste **kapalı**: yalnız korpusta fiyatı
#: **sayılmış** kalemler. Yeni bir kalem ancak fiyatı ölçülünce eklenir.
FIYATI_OLCULEN = {
    "satis": ("ticaret", 29),          # karlilik→ticaret 21 + mal→ticaret 8
    "tep": ("surdurulebilirlik", 4),
}


def _kararlar() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in _PACKS.rglob("sahiplik_kararlari.yml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for k in (d.get("kararlar") or []):
            if k.get("sahip"):
                out.setdefault(str(k.get("terim")), k)
    return out


def test_FIYATI_ODENEN_KARARLAR_hala_YERINDE():
    """🔴 Kararı geri almak **ucuz olmamalı**: sildiğinde bu test fiyatı hatırlatır."""
    k = _kararlar()
    for terim, (sahip, fiyat) in FIYATI_OLCULEN.items():
        assert terim in k, (
            f"🔴 `{terim}` sahiplik kararı SİLİNMİŞ. O karar korpusta **{fiyat}** satır "
            f"kırmızı üretiyor ve bu bir kusur DEĞİL, kararın fiyatıdır. Geri alınacaksa "
            "gerekçesi yazılsın — bir kararı sessizce geri almak, hiç almamış olmaktır.")
        assert k[terim].get("sahip") == sahip, (
            f"🔴 `{terim}` sahibi `{k[terim].get('sahip')}` olmuş (önce `{sahip}`). "
            "Sahip değişimi bir ölçüm gerektirir: yeni sahibin korpustaki fiyatı kaç?")


def test_HER_KARARIN_GEREKCESI_var():
    """`FAZ 3.1`'in kendi kuralı: *gerekçesiz muafiyet yok* — sahiplik de öyle."""
    eksik = [t for t, k in _kararlar().items() if not str(k.get("gerekce") or "").strip()]
    assert not eksik, f"gerekçesiz sahiplik kararı: {eksik}"


def test_KIYASLANAMAZ_olcu_CIPLAK_terimi_TALEP_EDIYORSA_karari_VAR():
    """🔴 Ölçümün bulduğu asıl çelişki — ve neden sinonim SİLİNMEDİ.

    `karlilik.satis_tutari_turev` kendi beyanıyla `kiyaslanamaz: true` ve
    `cekirdek_metrik: satis_tutari`; dosyanın kendi cümlesi *«ŞİRKETLER ARASI
    KIYASLANMAZ — kârlılık hesabının GİRDİSİDİR»*. Buna rağmen çıplak `satış`
    sinonimini taşıyor.

    ⊘ Çözüm sinonimi silmek **değil** (ölçüldü: erişim düşer, `eval_gate` kırmızı);
    çözüm bir **sahiplik kararıdır** ve o karar var. Bu test ikisini **birbirine
    bağlar**: `kiyaslanamaz` bir ölçü çıplak bir terimi talep ediyorsa, o terimin
    yazılı bir sahibi **olmak zorundadır** — yoksa hakem susar ve türev ölçü kanonik
    sorunun cevabı olur.
    """
    kararlar = _kararlar()
    acikta: list[str] = []
    for p in _PACKS.rglob("*.yml"):
        try:
            d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:                                     # noqa: BLE001
            continue
        cube = d.get("cube") if isinstance(d.get("cube"), dict) else d
        for m in (cube.get("measures") or []):
            if not isinstance(m, dict) or not m.get("kiyaslanamaz"):
                continue
            cek = str(m.get("cekirdek_metrik") or "")
            if not cek:
                continue
            # Çıplak terim = çekirdek metriğin kök adı (`satis_tutari` → `satis`).
            kok = cek.split("_")[0]
            if kok not in kararlar:
                acikta.append(f"{p.name}:{m['name']} → «{kok}» sahipsiz")
    assert not acikta, (
        "🔴 `kiyaslanamaz` bir türev ölçü çıplak bir terimi talep ediyor ama o terimin "
        "yazılı sahibi YOK:\n  " + "\n  ".join(acikta)
        + "\n\nHakem susar ve türev ölçü kanonik sorunun cevabı olur — üstelik kendi "
          "beyanı «şirketler arası kıyaslanmaz» derken.")
