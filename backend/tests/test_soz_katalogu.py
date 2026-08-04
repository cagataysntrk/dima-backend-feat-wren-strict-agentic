"""FAZ 5.17 kapısı — **tek ses.** [bayraksız: kök neden]

## Ölçülen kusur

Kullanıcıya dönen metinlerin hepsi satır içi f-string'di; merkezî katalog **yoktu**:

- 🔴 **hitap aynı oturumda değişiyordu** (`ask.py` *"sen"* ↔ `eylem.py` *"siz"*)
- aynı cümle **iki yerde birebir** tekrar ediyordu
- **jargon sızıyordu**: kullanıcıya *"yapısal bir `cube_query` taşımıyor"* deniyordu

## Üç şart — yol haritasının kapısı

Her kayıt: (a) **tek hitap kipinde**, (b) **ham küp kolon adı içermiyor**,
(c) `kind=="netlestirme"` ise **soru işaretiyle bitiyor**.
"""

from __future__ import annotations

import re

import pytest

from app.soz import HITAP, JARGON, KATALOG, TURLER, BilinmeyenSoz, soz

#: *"siz"* kipinin izleri — ikinci çoğul ekleri. ⚠ Kelime sınırıyla aranır: *"anlarsınız"*
#: yakalanmalı ama *"kısınız"* gibi bir kök içinde geçen dizi yakalanmamalı.
_SIZ_KIPI = re.compile(
    r"\b\w*(?:ınız|iniz|unuz|ünüz|sınız|siniz|sunuz|sünüz|ınızı|inizi)\b", re.I)


@pytest.mark.parametrize("kimlik", sorted(KATALOG))
def test_a_TEK_HITAP_kipinde(kimlik):
    """🔴 Ölçülen kusur: `ask.py` **"sen"** (15 isabet), `eylem.py` **"siz"**.

    İkisi aynı oturumda karşılaşınca ürün **iki kişi gibi** konuşuyordu. *Hangi kipin
    seçildiği önemli değil; SEÇİLMİŞ olması önemli.*
    """
    assert HITAP == "sen"
    metin = str(KATALOG[kimlik]["metin"])
    bulunan = _SIZ_KIPI.findall(metin)
    assert not bulunan, (
        f"`{kimlik}` **siz** kipinde yazılmış ({bulunan}) — katalog `{HITAP}` kipinde. "
        f"Aynı oturumda iki hitap, ürünü iki kişi gibi konuşturur.")


@pytest.mark.parametrize("kimlik", sorted(KATALOG))
def test_b_JARGON_sizmiyor(kimlik):
    """🔴 Kullanıcıya iç terim söylemek, ona **bizim sorunumuzu** anlatmaktır."""
    metin = str(KATALOG[kimlik]["metin"]).lower()
    for j in JARGON:
        assert j not in metin, (
            f"`{kimlik}` jargon sızdırıyor: {j!r}. Ölçülen örnek buydu — kullanıcıya "
            f"*«yapısal bir cube_query taşımıyor (Discovery/ham SQL)»* deniyordu.")


@pytest.mark.parametrize("kimlik", sorted(KATALOG))
def test_c_NETLESTIRME_soru_isaretiyle_biter(kimlik):
    """🔴 *"Neyi karşılaştırmak istediğini anlayamadım"* bir **form doğrulayıcısıdır**,
    bir soru değil."""
    k = KATALOG[kimlik]
    if k["kind"] != "netlestirme":
        return
    assert str(k["metin"]).rstrip().endswith("?"), (
        f"`{kimlik}` bir netleştirme ama **soru değil**. Netleştirme bir form hatası "
        f"gibi değil, bir SORU gibi okunmalı.")


@pytest.mark.parametrize("kimlik", sorted(KATALOG))
def test_TUR_gecerli(kimlik):
    assert KATALOG[kimlik]["kind"] in TURLER


def test_NETLESTIRME_once_NE_ANLADIGINI_soyler():
    """**Metin şekli kuralı:** önce ne anladığını söyle, sonra sor.

    Dönem netleştirmesi *"Hangi dönem için?"* diye **başlamamalı**: kullanıcı sistemin
    onu anlayıp anlamadığını bilmiyor ve bir form alanı doldurduğunu sanıyor.
    """
    m = soz("netlestirme.donem", ne="Fire toplamını")
    assert m.startswith("Fire toplamını"), (
        "🔴 Netleştirme, ne anlaşıldığını SÖYLEMEDEN soruyor — bu bir form "
        "doğrulayıcısıdır, bir soru değil.")
    assert m.endswith("?")
    # Bilinmeyen bağlamda bile ÖNCE yetenek beyanı gelir.
    assert soz("netlestirme.donem_sade").startswith("Bunu çıkarabilirim")


def test_EKSIK_ALAN_cevabi_DUSURMEZ():
    """⚠ Biçimlendirme hatası bir cevabı düşürmemeli: kullanıcı eksik bir kelimeyle
    yaşayabilir, **cevapsızlıkla** yaşayamaz."""
    m = soz("netlestirme.donem")            # `ne` verilmedi
    assert "{" not in m and "}" not in m
    assert m.endswith("?")


def test_BILINMEYEN_ID_fail_closed():
    """Uydurulmuş bir ID sessizce boş metin üretirse kullanıcı **hiçbir şey** görmez."""
    with pytest.raises(BilinmeyenSoz):
        soz("olmayan.kimlik")


def test_AYNI_METIN_IKI_KEZ_yazilmaz():
    """🔴 Ölçülen kusur: *"Bu soru için güvenilir bir sorgu üretemedim."* **iki ayrı
    yerde birebir** tekrar ediyordu."""
    metinler = [str(v["metin"]).strip() for v in KATALOG.values()]
    tekrar = {m for m in metinler if metinler.count(m) > 1}
    assert not tekrar, f"Katalogda birebir tekrar eden metin(ler): {tekrar}"


def test_KATALOG_bir_VERI_MODULU():
    """*Bir metin katalogunun tek işi metinleri bir yerde tutmaktır; ikinci bir işi
    olduğu anda kimse ona metin yazmaz.*

    ⚠ Belirteç yapısal: modülde sınıf hiyerarşisi / şablon motoru / i18n çerçevesi
    **olmamalı**.
    """
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/soz.py")
                     .read_text(encoding="utf-8"))
    siniflar = [n.name for n in ast.walk(agac) if isinstance(n, ast.ClassDef)]
    assert siniflar == ["BilinmeyenSoz"], (
        f"🔴 `soz.py` bir soyutlama katmanına dönüşmüş: {siniflar}. Bu bir VERİ "
        f"MODÜLÜDÜR — sözlük + üç alan, başka bir şey değil.")
    fonksiyonlar = {n.name for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)}
    assert fonksiyonlar <= {"soz", "tur"}, f"beklenmedik fonksiyon: {fonksiyonlar}"
