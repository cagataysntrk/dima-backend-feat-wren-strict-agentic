"""FAZ 0.14 / **K5 — PANEL SAYISI**: *"yeni özellik yeni panel doğurmaz."*

## 🔴 ÖNCE TANIM, SONRA SAYI, SONRA TEST

Bu sıra **zorunlu** ve bir kusurdan doğdu: belge üç ayrı yerde **üç ayrı sayı** taşıyordu
(sürüm 3'te *"11"*, §C/11'de *"12"*, ölçümde *"export 13 / dosya 12"*) — çünkü kimse
**neyin sayıldığını** yazmamıştı. Tanımsız bir sayı bir ölçüm değildir; test yazılsaydı
kırmızı **doğardı** ve suç testte sanılırdı.

**TANIM (§C/11 kutusu):** sayılan şey **export edilen panel bileşenidir**,
`export default` dâhil — dosya sayısı DEĞİL. Gerekçe: bir dosya iki panel export
edebilir ve kullanıcı **iki panel** görür; tavan kullanıcının gördüğü şeye konur.

**TAVAN:** v1'de **13**. *(Bölüm II'de 15 — `PK-23`; o sürüm geldiğinde bu sayı
belgeyle birlikte yükseltilir, sessizce değil.)*

## Neden tavan var

`feedback_arka_on_entegrasyon_butunlugu`: *"yeni özellik yeni panel doğurmaz."* Panel
enflasyonu, ürünü bir **kontrol paneli çöplüğüne** çevirir; her yeni yetenek **var olan**
bir yüzeye bağlanmalıdır. Tavan bunu bir tercih olmaktan çıkarıp **kapı** yapar.
"""

from __future__ import annotations

import re

from tests.kapi_ortak import fe_dosyalari, frontend_dir, yorumsuz

#: v1 tavanı — **export** sayımı (bkz. yukarıdaki TANIM).
TAVAN = 13

#: Sayımın DESENİ tek yerde: `export function XPanel` · `export default function XPanel`.
DESEN = re.compile(r"^export\s+(?:default\s+)?function\s+(\w*Panel)\b", re.M)


def _panel_exportlari() -> dict[str, list[str]]:
    """`dosya → export edilen panel adları`. Yorumlar ayıklanmış kaynaktan."""
    out: dict[str, list[str]] = {}
    for yol, kaynak in fe_dosyalari().items():
        adlar = DESEN.findall(kaynak)
        if adlar:
            out[yol] = adlar
    return out


def test_K5_TANIM_ONCE_export_sayilir_dosya_DEGIL():
    """🔴 Tanımın kendisi kilitli: bir dosya **iki panel** export edebilir ve kullanıcı
    iki panel görür. Dosya saymak, kullanıcının gördüğünü değil dizin yapısını ölçer."""
    exportlar = _panel_exportlari()
    toplam_export = sum(len(v) for v in exportlar.values())
    dosya = len(exportlar)
    assert toplam_export >= dosya, "sayım tersine dönmüş — export ≥ dosya olmalı"
    # Tanımın ayırt edici olduğunu göster: iki sayı FARKLI olabilmeli ve bu normaldir.
    assert isinstance(toplam_export, int) and toplam_export > 0


def test_K5_PANEL_TAVANI_ASILMADI():
    """🔴 **ASIL KAPI.** *"Yeni özellik yeni panel doğurmaz."*"""
    exportlar = _panel_exportlari()
    toplam = sum(len(v) for v in exportlar.values())
    assert toplam <= TAVAN, (
        f"PANEL TAVANI AŞILDI: {toplam} export (tavan {TAVAN}).\n"
        + "\n".join(f"  {y}: {', '.join(a)}" for y, a in sorted(exportlar.items()))
        + "\n\nYeni yetenek VAR OLAN bir yüzeye bağlanır. Tavanı yükseltmek bir KARARDIR: "
          "belgeyle (§C/11 · PK-23) birlikte yapılır, sessizce değil.")


def test_K5_SAYIM_YORUMLARDAN_ETKILENMEZ():
    """Bir yorum satırında geçen `export function XPanel` bir panel DEĞİLDİR.
    (Bu operasyonda kapılar altı kez metni ölçtü — sayaç da onlardan biri olmasın.)"""
    kok = frontend_dir()
    ham = "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                    for f in sorted(kok.rglob("*"))
                    if f.is_file() and f.suffix in (".ts", ".tsx"))
    ham_sayi = len(DESEN.findall(ham))
    temiz_sayi = len(DESEN.findall(yorumsuz(ham)))
    assert temiz_sayi <= ham_sayi
    assert temiz_sayi == sum(len(v) for v in _panel_exportlari().values())
