"""FAZ 4.6 yan kapısı — **`FLAG_REGISTRY` ile `features.yml` AYRIŞAMAZ.**

## Ölçülen boşluk

Bir denetim ölçtü: kayıtta **29**, YAML'de **25** bayrak vardı. Dördü (`ask_async_discovery`
· `ayni_grain_gocu` · `cekirdek_katman` · `threaded_chat`) kayıtta duruyor ama **fabrika
varsayılanı hiçbir yerde yazılı değildi**.

## Neden bir kusur — "zaten kapalı" cevabı yetmiyor

Çözümlemede yokluk ile `"off"` **aynı** sonucu verir (`resolve_for` `off`u kümeden
düşürür). Yani davranış açısından fark yok. Kusur **okunabilirlikte**: *"bu bayrak var ve
kapalı"* ile *"böyle bir bayrak yok"* aynı şey değildir. Birincisi tartışılabilir bir
karardır, ikincisi bir **unutulmuşluk**.

🔴 *Yazılı olmayan bir varsayılan, tartışılamayan bir varsayılandır.*

## Muafiyet — ve neden sessiz olamaz

Bir bayrak bilinçli olarak YAML'e **eklenmemiş** olabilir. O zaman gerekçe `MUAF`'a
yazılır — sessizce dışarıda bırakılmaz.
"""

from __future__ import annotations

import ast
from pathlib import Path

import yaml

_KOK = Path(__file__).resolve().parents[1]

#: 🔴 Fabrika varsayılanı BİLEREK yazılmayan bayraklar — gerekçesiyle.
MUAF: dict[str, str] = {
    "ayni_grain_gocu":
        "FAZ 2.4 — göç ÖLÇÜLDÜ ve REDDEDİLDİ: `surdurulebilirlik` kimliğinden ham kaynak "
        "adları çıkarılınca erişim %64 → %56 düştü (110 sessiz-yanlış kapandı ama 388 "
        "cevap kayboldu — 3,5:1 kötü takas). Bayrak KAYITTA kalıyor çünkü mekanizma "
        "yazıldı ve testli; fabrika varsayılanı YAZILMIYOR çünkü bir fabrika varsayılanı "
        "yazmak, o yolun bir gün açılacağını ima eder. *Ölçüm onu haklı çıkarmadı ve "
        "kayıt bunu söylemeli.*",
}


def _kayit() -> set[str]:
    agac = ast.parse((_KOK / "app/features.py").read_text(encoding="utf-8"))
    for n in ast.walk(agac):
        hedefler = (n.targets if isinstance(n, ast.Assign)
                    else [n.target] if isinstance(n, ast.AnnAssign) else [])
        if (any(getattr(t, "id", "") == "FLAG_REGISTRY" for t in hedefler)
                and isinstance(n.value, ast.Dict)):
            return {k.value for k in n.value.keys if isinstance(k, ast.Constant)}
    raise AssertionError("`FLAG_REGISTRY` bulunamadı — ölçüm aracı kırık.")


def _yaml() -> set[str]:
    d = yaml.safe_load((_KOK / "demo/packs/features.yml").read_text(encoding="utf-8"))
    return set((d or {}).get("features") or {})


def test_KAYITTAKI_her_bayragin_FABRIKA_VARSAYILANI_yazili():
    eksik = sorted(_kayit() - _yaml() - set(MUAF))
    assert not eksik, (
        f"🔴 FABRİKA VARSAYILANI YAZILMAMIŞ bayrak(lar): {eksik}\n"
        f"`FLAG_REGISTRY`'de kayıtlı ama `demo/packs/features.yml`'de yok. "
        f"'Zaten kapalı' bir cevap DEĞİL: yokluk ile `\"off\"` çözümlemede aynı sonucu "
        f"verir ama *okuyucu* için aynı şey değildir.\nİki seçenek: (1) `features.yml`'e "
        f"yaz, (2) gerekçesiyle `MUAF`'a ekle.")


def test_YAMLDEKI_her_bayrak_KAYITTA_var():
    """Ters yön: metadata'sı olmayan bir bayrak admin panelinde **adsız** görünür."""
    hayalet = sorted(_yaml() - _kayit())
    assert not hayalet, (
        f"🔴 `FLAG_REGISTRY`'de metadata'sı OLMAYAN bayrak(lar): {hayalet}. Admin "
        f"panelinde etiketsiz/açıklamasız görünür — bir yönetici neyi açtığını bilemez.")


def test_MUAF_beyani_BAYATLAMAZ():
    """Muaf bir bayrak YAML'e eklendiyse gerekçe artık yalan söylüyordur."""
    bayat = sorted(set(MUAF) & _yaml())
    assert not bayat, (
        f"🔴 `MUAF` beyanı bayatlamış: {bayat} artık `features.yml`'de VAR. Gerekçeyi "
        f"kaldırın — *bayat bir muafiyet, muafiyeti olmayan bir bayraktan tehlikelidir, "
        f"çünkü sessizce doğru görünür.*")


def test_MUAF_beyani_KAYITTA_karsiligi_olmadan_yazilamaz():
    hayalet = sorted(set(MUAF) - _kayit())
    assert not hayalet, f"`MUAF`'ta kayıtta olmayan bayrak: {hayalet}"
