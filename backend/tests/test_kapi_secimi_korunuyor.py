"""🔴 HIZLI KAPININ SEÇİMİ — *bir kapının kapsamı, onu tetikleyen sinyalden büyük olamaz.*

## Ölçülen kusur (2026-08-06)

`test_frontend_buyume` **üç commit boyunca kırmızıydı** (`ReportCard.tsx` 985/948) ve
hızlı kapı her seferinde **yeşil** dedi.

Sebep bir kod kusuru değil bir **seçim** kusuruydu: `lab/kapi.py --hizli --degisen` listesi
**elle** verilir; o demette `.tsx` dosyası listeye **yazılmamıştı** → `_frontend_degisti()`
`False` döndü → frontend kapıları hiç seçilmedi.

⚠ Ve bu, `_frontend_degisti`'nin kendi docstring'indeki dersin **ikinci hâlidir**: orada
kapsam *uzantı süzgecinden* dardı, burada *girdi listesinden*.

## Neden büyüme kapıları ÇEKİRDEĞE alındı

Bir tavanı **her değişiklik** aşabilir. Import bağımlılığına bakan bir seçim onu asla
güvenilir bulamaz — çünkü tavan bir **dosya boyutudur**, bir **çağrı grafiği** değil.
Maliyeti ölçüldü: ikisi birlikte **~5 sn**.

🔴 Ve yerel kapının 2026-08-04'te *yalnız korpusa* indirilmesi bu sınıfı **görünmez**
yapmıştı: süit gecelik CI'ya taşındı, kırmızı orada kaldı, kimse bakmadı.
*Bir kapıyı ucuzlaştırmak, onu görünmez yapmanın da yoludur.*
"""

from __future__ import annotations

import pathlib
import re

KAPI = pathlib.Path(__file__).resolve().parents[1] / "lab" / "kapi.py"
KAYNAK = KAPI.read_text(encoding="utf-8")

#: Değişen dosyadan BAĞIMSIZ koşması gereken kapılar — her biri bir gerekçe taşır.
ZORUNLU_CEKIRDEK = {
    "test_modul_buyume.py": "tavan bir DOSYA BOYUTUDUR; hiçbir import grafiği onu bulmaz",
    "test_frontend_buyume.py": "aynı gerekçe + `.tsx` sinyali ELLE verilen listeye bağlı",
    "test_cevap_alani_yetim_degil.py": "arka-ön bütünlüğü: yetim uç bir CI hatasıdır",
}


def _cekirdek() -> set[str]:
    m = re.search(r"^CEKIRDEK\s*=\s*\((.*?)^\)", KAYNAK, re.S | re.M)
    assert m, "⊘ CEKIRDEK bulunamadı — kapı bayatlamış"
    return set(re.findall(r'"(test_[a-z0-9_]+\.py)"', m.group(1)))


def test_BUYUME_KAPILARI_CEKIRDEKTE():
    """🔴 **ASIL KAPI** — üç commit boyunca görünmeyen kırmızının yapısal panzehiri."""
    eksik = {a: n for a, n in ZORUNLU_CEKIRDEK.items() if a not in _cekirdek()}
    assert not eksik, (
        "🔴 `lab/kapi.py::CEKIRDEK`'ten çıkarılmış:\n  "
        + "\n  ".join(f"{a} — {n}" for a, n in eksik.items())
        + "\n⚠ Bu dosyalar `--degisen` listesine BAKMADAN koşmalı: bir tavanı her "
          "değişiklik aşabilir ve `--degisen` ELLE verilir (unutulabilir).")


def test_CEKIRDEK_DOSYALARI_GERCEKTEN_VAR():
    """⊘ Ölçüm tabanı: çekirdekte adı geçen bir dosya yoksa pytest onu **sessizce**
    atlar ve kapı hiç koşmadan yeşil görünür. *Bir listeye yazmak, var olmak değildir.*"""
    testler = pathlib.Path(__file__).resolve().parent
    yok = [a for a in _cekirdek() if not (testler / a).exists()]
    assert not yok, f"🔴 ÇEKİRDEK'te var, diskte yok: {yok}"


def test_FRONTEND_SINYALI_HALA_VAR():
    """⚠ Çekirdeğe eklemek `_frontend_degisti`'yi **gereksizleştirmez**: o, `.tsx`
    değişiminde çekirdek DIŞINDAKİ frontend kapılarını da seçer (tasarım sistemi,
    AI-Act uyumu). İkisi farklı kapsamlardır ve biri ötekinin yerine geçmez."""
    assert "_frontend_degisti" in KAYNAK
    assert ".tsx" in KAYNAK and ".css" in KAYNAK
