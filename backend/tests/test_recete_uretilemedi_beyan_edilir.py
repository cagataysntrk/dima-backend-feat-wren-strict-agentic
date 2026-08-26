"""🔴🔴 `§K9` — **REÇETE İSTENDİ AMA ÜRETİLEMEDİ: BEYAN EDİLİR, "NEDEN"İN AYNISI DÖNMEZ.**

## Ölçülen kusur (Playwright kampanyası, `2026-08-26_PLAYWRIGHT-CANLI-TEST-
## KAMPANYASI.md` §K9 — canlı, iki farklı domainle doğrulandı)

*"bu neden böyle?"* ve *"ne yapmalıyız?"* **birebir aynı** metni dönüyordu.
Kanıtlandı (canlı debug log): `tur=ne_yapmali _oner=True raporlar=0` —
sınıflandırma doğruydu, ama `if _oner and katki.raporlar:` koşulu
`katki.raporlar` boş çıktığında (ölçü formül-bileşenli, segment ayrıştırması
üretilemiyor) hiç çalışmıyordu ve `not_metni` sessizce `katki.note`'ta
("neden"le aynı metinde) kalıyordu.

⚠ **Bu OEE'ye özel bir kusur DEĞİL** — `_oner`/`katki` ikisi de bu noktadan
önce zaten domain-agnostik hesaplanmış değişkenler. Düzeltme canlıda hem
`oee` (formül-bileşenli) hem `mizan.bakiye` (yarı-toplanabilir stok ölçüsü —
tamamen farklı bir sınıf) ile doğrulandı — ikisinde de "neden" ile
"ne yapmalıyız" artık **farklı**.
"""

from __future__ import annotations

import pathlib

_ASK = pathlib.Path(__file__).resolve().parents[1] / "app" / "routers" / "ask.py"
_KAYNAK = _ASK.read_text(encoding="utf-8")


def _blok() -> str:
    """`if _oner and katki.raporlar:` dalının başından `elif _oner:` dalının
    sonuna kadar — ikisi de aynı pencerede olmalı (biri öbürünün yoklukta
    devreye giren kardeşi)."""
    i = _KAYNAK.find("if _oner and katki.raporlar:")
    assert i > 0, "🔴 gerçek-reçete dalı kayboldu — yapı değişmiş"
    j = _KAYNAK.find('iz.append("Reçete: segment ayrıştırması yok', i)
    assert j > i, "🔴 `§K9` beyan dalının gövdesi bulunamadı — reçete yine sessizce boş dönüyor olabilir"
    return _KAYNAK[i:j + 100]


def _yalniz_kod(blok: str) -> str:
    """Yorum satırlarını (`#` ile başlayan) eler — genellik testi yalnız
    ÇALIŞAN KODA bakmalı, açıklayıcı yorumdaki bir örnek isme değil."""
    return "\n".join(s for ln in blok.splitlines()
                     if not (s := ln.strip()).startswith("#"))


def test_BOS_RAPORLARDA_BEYAN_EKLENIR():
    """🔴 **ASIL KAPI.** `katki.raporlar` boşken (herhangi bir ölçü) `_oner=True`
    hâlâ bir şey söyler — sessizce `katki.note`'ta (yani "neden"le aynı
    metinde) kalınmaz."""
    b = _blok()
    assert "elif _oner:" in b, "🔴 boş-raporlar dalı yok — koşul hâlâ sessiz düşüyor"
    assert "not_metni +=" in b, "🔴 beyan `not_metni`'ye eklenmiyor"
    assert "Reçete üretilemedi" in b, "🔴 beyan metni kayıp"


def test_DOMAIN_OZEL_DAL_YOK():
    """⚠ **Genellik kapısı** (kullanıcı uyarısı — kök çözüm tekil olmasın).
    Beyan dalı hiçbir küp/ölçü adı içermemeli; içeriyorsa bu OEE'ye özel bir
    yama yazıldığının kanıtıdır. ⚠ Yalnız **kod** satırlarına bakılır —
    açıklayıcı yorumda "canlıda OEE ile ölçüldü" demek meşrudur, kanıt
    kod satırındadır."""
    kod = _yalniz_kod(_blok())
    for yasakli in ("\"oee\"", "'oee'", "== \"oee\"", "\"parti\"", "'parti'",
                    "cube ==", "measure =="):
        assert yasakli not in kod, f"🔴 beyan dalı domaine özel görünüyor: {yasakli!r}"


def test_ZIT_OLCUT_DOLU_RAPORLAR_HALA_GERCEK_RECETE_URETIR():
    """🆃 Kapının kurbanı: `elif _oner` dalını HER durumda tetiklemek de yeşil
    kalırdı — dolu `katki.raporlar` varken gerçek reçete (`prescribe.recete`)
    hâlâ **öncelikli** olmalı, beyan yalnız YOKLUĞUNDA devreye girmeli."""
    b = _blok()
    if_i = b.find("if _oner and katki.raporlar:")
    elif_i = b.find("elif _oner:")
    assert 0 <= if_i < elif_i, "🔴 `if` (gerçek reçete) dalı `elif` (beyan) dalından SONRA geliyor olamaz"
