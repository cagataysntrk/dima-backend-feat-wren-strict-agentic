"""🔴 `D9`/`E-4` — **HER `beta` BAYRAĞIN YAZILI BİR `on` ŞARTI OLMALI.**

Rapor `E-4`: *"`on` şartı olmayan bir bayrak `beta`'da **süresiz** yaşar — bugün 21
bayrak o durumda ve **hiçbiri** `on` olmadı."*

⊙ Bugün ölçüldü: 24 `beta` bayrağın **15'inin** şartı YAML yorumunda zaten yazılıydı;
**9'unda yoktu**. Rapordaki *21* sayısı bayattı — ve bu, raporun kendi kuralının
(*"ölçüm yüzeyinden şüphelen"*) bir örneği.

## Neden yorum değil ALAN

Şartlar YAML yorumlarında yaşıyordu. Bir kapının onları **metin arayarak** bulması
gerekirdi — ve bu dosyanın ilk taslağı tam olarak öyle yapıyordu: `"ŞARTI" in blok`.
Böyle bir kapı, bir cümlenin kelimelerine bağlıdır ve yeniden yazılan her yorumda
kırılır ya da **sessizce yeşile döner**.

*Bir eşik yazılmadan geçilemez; yazılmayan eşik geçilmiş sayılmaz.*
"""

from __future__ import annotations

import pathlib

import yaml

from app.features import FLAG_REGISTRY

_YML = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs" / "features.yml"

#: 🔴 Şartı **YAML yorumunda** yazılı olanlar — bu kapı onları saymaz ama borç da saymaz.
#: ⚠ Liste yalnız **küçülebilir**: bir bayrak buradan çıkıp `on_sarti` alanına geçebilir,
#: tersi olamaz. *Bir muafiyet listesi büyüyebiliyorsa, o bir muafiyet değil bir kapıdır
#: ve kapı yanlış taraftadır.*
YORUMDA_YAZILI: frozenset[str] = frozenset({
    "tur_takip", "hizli_derin", "tur_paylas", "hedef_kiyasi", "cikti_yorumlama",
    "sql_display", "verify_button", "scheduled_reports", "dashboards", "next_steps",
    "ask_intent_first", "oylama_cekirdek", "katalog_sozlugu", "varlik_perdesi",
    "referans_dili",
})


def _beta_bayraklar() -> set[str]:
    d = yaml.safe_load(_YML.read_text(encoding="utf-8")) or {}
    return {k for k, v in (d.get("features") or {}).items() if str(v) == "beta"}


def test_HER_BETA_BAYRAK_ON_SARTI_TASIR():
    """🔴 Şartsız bir bayrak bir karar değil bir **ertelemedir** (`E-1`)."""
    sartsiz = sorted(
        ad for ad in _beta_bayraklar()
        if ad not in YORUMDA_YAZILI
        and not (FLAG_REGISTRY.get(ad) or {}).get("on_sarti"))
    assert not sartsiz, (
        f"🔴 {len(sartsiz)} `beta` bayrağın yazılı `on` şartı YOK: {sartsiz}\n"
        "  `app/features.py` kaydına `on_sarti: \"<şart>\"` yaz.\n"
        "  ⚠ Şart bir dilek değil bir **ölçüttür**: karşılandığı GÖZLENEBİLİR olmalı.")


def test_ON_SARTI_OLCUT_OLMALI_DILEK_DEGIL():
    """*Bir şart, karşılandığı gözlenemiyorsa bir şart değil bir temennidir.*"""
    for ad, k in FLAG_REGISTRY.items():
        s = k.get("on_sarti")
        if s is not None:
            assert isinstance(s, str) and len(s.strip()) >= 60, \
                f"{ad}: `on_sarti` çok kısa — ölçüt değil dilek olur"


def test_MUAFIYET_LISTESI_BUYUYEMEZ():
    """🔴 Liste yalnız **küçülür**: hepsi `on_sarti`'ya geçince boşalır.

    ⚠ Ve bugün `beta` olmayan bir ad listede kalırsa, liste **bayatlamıştır**:
    *bir muafiyet listesi, muaf tuttuğu şey ortadan kalkınca kendini temizlemelidir.*
    """
    beta = _beta_bayraklar()
    hayalet = sorted(YORUMDA_YAZILI - beta)
    assert not hayalet, (
        f"artık `beta` olmayan ad(lar) muafiyet listesinde: {hayalet} — liste bayat")
    assert len(YORUMDA_YAZILI) <= 15, "muafiyet listesi BÜYÜMÜŞ — yalnız küçülebilir"


def test_ON_OLAN_BAYRAK_SARTINI_KARSILAMIS_OLMALI():
    """⚠ `on`'a çıkan bir bayrak şartını **yazılı** bırakır — silinmez.

    Şart silinirse *neden* açıldığı kaybolur ve geri alma kararı verilemez.
    """
    d = yaml.safe_load(_YML.read_text(encoding="utf-8")) or {}
    for ad, deger in (d.get("features") or {}).items():
        if str(deger) in ("on", "prod"):
            k = FLAG_REGISTRY.get(ad) or {}
            assert k.get("on_sarti") or ad in YORUMDA_YAZILI or k.get("description"), \
                f"{ad}: `on`/`prod` ama hiçbir gerekçe taşımıyor"
