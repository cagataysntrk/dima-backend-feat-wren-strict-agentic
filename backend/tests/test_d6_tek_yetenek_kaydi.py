"""🔴🔴 `§D6` — **TEK YETENEK KAYDI**: her plan fiili bir aracın gövdesidir.

## Raporun isteği

> `FIIL_ANLAMI` **`tools.py`'den TÜRETİLİR**; kapalı `enum` **korunur**, üretilmiş olur.
> Kazanç: **tek kayıt** (`KAT-1`).

## Ölçülen kusur (2026-08-12) — ve rapor «%73 örtüşür» diyordu

Eşleşme **gövde düzeyinde** sayıldı (ad benzerliğiyle değil — o kaba ölçü %26 verir ve
bir şeyi çürütemez):

    9/15 fiil kayıtlı bir aracın gövdesini çağırıyor
    🔴 6/15 fiilin gövdesi kayıtta HİÇ YOKTU:
        MATRIS · SIRALA · RAPOR · PANO   → `app.ilkeller.*`
        KIYASLA · BOYUTSEC               → `app.contribution.*`

⊙ Yani *«tek yetenek kaydı»* iddiası **altı yetenek eksikti**: planlayıcı onları
çağırabiliyordu ama envanter onları **bilmiyordu** — yetki sınıfı, determinizmi,
maliyeti hiçbir yerde beyanlı değildi.

> *Bir kaydın tekliği, sayısıyla değil KAPSAMIYLA ölçülür; kapsamadığı her yetenek, o
> kaydın söylemediği bir cümledir.*

## `C1`'in üçüncü gerekçesi karşılandı

`test_c1_tek_yetenek_kaydi.py` bu işi **üç ölçülmüş gerekçeyle** ertelemişti ve üçüncüsü
şuydu: *«adlar örtüşmediği için türetim bir EŞLEME TABLOSU ister — iki kayıt yerine ÜÇ
şey»*. Eşleme artık ayrı bir tabloda değil, her **aracın kendi beyanında**
(`tools.Arac.fiil`). Üçüncü kayıt **doğmadı**.

## ⚠ Metinler neden hâlâ `plan_semasi`'nde

Araç `ozet`leri **MCP/araç seçimi** için yazılmış uzun metinlerdir; plan istemine
dökmek istemi kat kat büyütür ve **davranışı değiştirir** — `KURAL B`'nin yasağı.
Ayrım: *hangi fiiller var* → kayıt karar verir · *plan istemindeki cümle* → `plan_semasi`.

*Bir türetimin amacı metni kopyalamak değil, iki listenin ayrışmasını imkânsız kılmaktır.*
"""

from __future__ import annotations

import pytest

from app import tools
from app.plan_semasi import FIIL_ANLAMI, FIILLER


def _beyan() -> dict[str, str]:
    return {a.fiil: a.ad for a in tools.KAYIT if a.fiil}


def test_HER_FIILIN_BIR_ARACI_VAR():
    """🔴 Kusurun ta kendisi: altı fiilin gövdesi kayıtta yoktu."""
    eksik = sorted(set(FIIL_ANLAMI) - set(_beyan()))
    assert not eksik, (
        f"🔴 şu fiilleri hiçbir araç beyan etmiyor: {eksik}\n"
        "Planlayıcı onları çağırabiliyor ama envanter bilmiyor — yetki sınıfı, "
        "determinizmi ve maliyeti hiçbir yerde beyanlı değil.")


def test_HER_BEYANIN_BIR_FIILI_VAR():
    """⊘ Öteki yön: bir araç var olmayan bir fiili beyan edemez (yazım hatası kapanı)."""
    fazla = sorted(set(_beyan()) - set(FIIL_ANLAMI))
    assert not fazla, f"🔴 kayıtta beyanlı ama plan şemasında olmayan fiil: {fazla}"


def test_ESLEME_BIRE_BIR():
    """🔴 İki araç aynı fiili beyan ederse **hangisinin gövde olduğu belirsizleşir**.

    ⚠ Yüklem **SAYARAK** kurulu (ders ⑲): sözlük sessizce üzerine yazar, sayım yazmaz."""
    beyanlar = [a.fiil for a in tools.KAYIT if a.fiil]
    ikilenen = sorted({f for f in beyanlar if beyanlar.count(f) > 1})
    assert not ikilenen, (
        f"🔴 aynı fiili birden çok araç beyan ediyor: {ikilenen} — gövde belirsiz.")
    assert len(beyanlar) == len(FIIL_ANLAMI) == 15


def test_ITHAL_ANINDA_AYRISMA_PATLAR():
    """🔴🔴 **ASIL KAPI: ayrışma SESSİZ olamaz.**

    `plan_semasi` fiil kümesini içe aktarma anında kayda karşı doğruluyor. Bu test o
    denetimin **gerçekten koştuğunu** ölçer — yazılıp çağrılmayan bir denetim yoktur.
    """
    from app import plan_semasi

    assert hasattr(plan_semasi, "_fiilleri_kayittan_dogrula"), (
        "🔴 türetim denetimi silinmiş — iki liste sessizce ayrışabilir.")
    assert plan_semasi._fiilleri_kayittan_dogrula() == FIILLER

    import unittest.mock as _m

    sahte = tuple(a for a in tools.KAYIT if a.fiil != "MATRIS")
    with _m.patch.object(tools, "KAYIT", sahte), pytest.raises(RuntimeError, match="KAT-1"):
        plan_semasi._fiilleri_kayittan_dogrula()


def test_SIRA_KORUNUYOR_KURAL_B():
    """⚠ İstem metninin **sırası bir sözleşmedir**: kayıt yalnız KÜMEYİ belirler.

    Kayıt sırasından türetmek istemi yeniden dizerdi ve `KURAL B`'yi (davranış bayt bayt
    aynı) çiğnerdi. *Bir kümeyi türetmek, bir sırayı da devralmak zorunda değildir.*"""
    assert FIILLER == tuple(FIIL_ANLAMI)
    assert FIILLER[0] == "SORGU", "istem ilk fiili değişti — plan davranışı kayar"


@pytest.mark.parametrize("fiil,arac", [
    ("MATRIS", "matris"), ("SIRALA", "sirala"), ("RAPOR", "rapor"),
    ("PANO", "pano.taslak"), ("KIYASLA", "contribution.akran"),
    ("BOYUTSEC", "contribution.boyutsec"),
])
def test_ALTI_YENI_ILKEL_KAYITTA(fiil, arac):
    """Bu turda kayda giren altı ilkel — adıyla."""
    assert _beyan().get(fiil) == arac
    a = tools.get(arac)
    assert a.determinizm == "deterministik", f"{arac} belirlenimsiz beyan edilmiş"
    assert a.yan_etki in ("yok", "okur"), f"{arac} YAZAN bir araç gibi beyan edilmiş"


def test_ILKELLER_YENI_YETKI_SINIFI_ACMADI():
    """⚠ Altısı da koşmuş satırlar üstünde saf dönüşüm. Yeni bir `izin` değeri açmak,
    **olmayan bir riski icat etmek** olurdu — `bagla`/`hesapla` ile aynı sınıftalar."""
    izinler = {tools.get(a).izin for a in
               ("matris", "sirala", "rapor", "pano.taslak", "contribution.boyutsec")}
    assert izinler == {"query:run"}, f"beklenmeyen yetki sınıfı: {izinler}"


def test_PANO_ARACI_YAZMADIGINI_BEYAN_EDIYOR():
    """🔴 `§D7` ile aynı değişmez: plan yolundaki pano bir **taslaktır**."""
    a = tools.get("pano.taslak")
    assert a.yan_etki == "yok" and a.makbuz is None
    assert "kaydetmez" in a.ozet.lower() or "yazmaz" in a.notlar.lower()
