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


# --- 🔴 DA-10 — KATALOGUN EN ÇOK KULLANILAN CÜMLESİ ÖLÜYDÜ -------------------------


def test_DONEM_NETLESTIRMESI_KATALOGDAN_okunuyor():
    """🔴 Bir denetim ajanı buldu: `netlestirme.donem` katalogda **düzeltilmiş** hâliyle
    duruyordu (*"{ne} çıkarabilirim — hangi dönem için?"*) ama üretimde **hiçbir çağıranı
    yoktu**; `ask.py` elle yazılmış `_PERIOD_TEXT`'i basıyordu.

    ⊙ Ağırlığı ölçülü: netleştirmelerin **%79'u** dönem sorusudur (`donem_capasi.py:8`).
    Yani katalogun en çok kullanılan cümlesi ölü koddu — ve `soz.py:19`'un kendi kuralı
    (*"ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR"*) o %79'da hiç uygulanmıyordu.
    """
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/routers/ask.py").read_text(encoding="utf-8")
    assert 'soz("netlestirme.donem"' in kaynak, (
        "🔴 dönem netleştirmesi katalogdan okumuyor — elle yazılmış metin geri gelmiş")
    assert 'soz("netlestirme.donem_sade")' in kaynak, (
        "🔴 ölçü çıkarılamadığında yedek katalog girdisi kullanılmıyor")


def test_UCTAN_UCA_DONEM_SORUSU_NE_ANLADIGINI_SOYLUYOR(client):
    """Uçtan uca: *"fire kg"* → sistem önce **ne yapabileceğini** söyler, sonra sorar."""
    from tests.conftest import ask

    d = ask(client, "fire kg", session_id="soz-donem")
    metin = (d.get("soz") or d.get("note") or "")
    if not metin or (d.get("cube_query") or {}).get("measures") is None:
        import pytest
        pytest.skip(f"⊘ vaka bayat: {metin[:60]!r}")
    # ⟳ **POLİTİKA DEVRİ (`D3` → `§TZ`).** `DA-10`'un kuralı — *«önce ne anladığını söyle,
    # sonra sor»* — kaybolmadı, **bir adım ileri gitti**: sistem artık ne anladığını
    # söylüyor, ne varsaydığını da söylüyor ve **sormuyor** çünkü cevabı zaten veriyor.
    # ⊙ `varsayilan_donem` korpus A/B'siyle ölçüldü (`D3`): doğru-cube %94,9→%95,0,
    # `sessiz_yanlis` 8→8. Ve `§TZ` düzeltme chip'lerini geri getirdi.
    # 🔴 Ölçüt bu yüzden *«hangi dönem»* metninden **garantiye** çevrildi: dönem hakkında
    # ne bilindiği/ne varsayıldığı **söylenir**, ve düzeltme **tek tıktır**.
    # *Bir sözün kipini kilitlemek, o sözün gelişmesini yasaklamaktır.*
    assert "dönem" in metin.lower(), (
        f"🔴 dönem hakkında hiçbir şey söylenmiyor: {metin!r}")
    assert ("çıkarabilirim" in metin
            or any(s["label"] == "Tümü" for s in (d.get("suggestions") or []))), (
        f"🔴 ne yapabileceğini de söylemiyor, düzeltme tıkı da sunmuyor: {metin!r}")


def test_KISMI_ANLAMA_CUMLESI_KELIME_SAYMIYOR():
    """🔴 **Cümle, tanınmayan kelimeyi değil ANLAŞILMAYANI söyler** (`§27.4`).

    Curl'de ölçüldü: *"bu yıl hangi müşteri en çok iade etti"* →
    ***"«hangi etti» başka bir konu gibi görünüyor"***. Kullanıcı ne yaptığını anlamaz:
    `hangi` bir soru sözcüğü, `etti` bir yardımcı fiil — ikisi de **sorusunun konusu
    değil**. Anlaşılmayan şey `iade`ydi.

    ⊙ Kök: `unknown` **kapsam kapısının** listesidir (dolgu olmayan her kelime), gösterim
    listesi değil. Kapı onu **saymak** için üretir; cümle onu **okumak** için kullanamaz.

    🔴 Çözüm bir liste değil bir **devir**: `netlestirme.olcu` bu cümleyi **zaten**
    taşıyordu ve bir denetim ajanı onun **sıfır tüketicili** olduğunu bulmuştu.

    *Bir kapının iç listesi, kullanıcıya gösterilecek bir metin değildir: biri saymak
    için, öteki anlatmak için vardır.*
    """
    import inspect

    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    i = src.index("_gosterilecek = [w for w in unknown")
    # ⟳ **PENCERE GENİŞLETİLDİ (`§54`)** — silinmedi. `§54` bu satırın hemen ardına bir
    # kapı ve gerekçesini koydu (*"adlandırılacak konu kalmadıysa dal düşer"*) ve
    # `netlestirme.olcu` yedeği pencerenin **dışına** taştı. Kapının ölçtüğü şey değişmedi:
    # *"kısmi anlama cümlesi bir yedek taşıyor mu"*.
    # ⚠ Sabit genişlikli bir pencere, koruduğu koda yorum eklendikçe kayar; doğru tepki
    # onu **koda göre** genişletmektir. *Bir çapa, çakıldığı tahta büyüdükçe yerini
    # korumaz — yeniden çakılır.*
    blok = src[max(0, i - 200):i + 2800]
    assert "_gosterilecek = [w for w in unknown if not _islev_sozcugu(w)]" in blok, (
        "🔴 gösterim süzgeci yok — işlev sözcükleri kullanıcıya basılıyor")
    # 🔴 **HER İKİ dalda** yedek cümle olmalı: `other_topic` → `netlestirme.konu`,
    # kısmi anlama → `netlestirme.olcu`. İlk yazımda yalnız birine uygulandı ve curl
    # *"«hangi etti» başka bir konu gibi görünüyor"*u aynen döndürdü.
    # *Bir düzeltmeyi tek dala uygulamak, iki dalı olan bir kusuru yarım kapatır.*
    for yedek in ('_soz.soz("netlestirme.olcu")', '_soz.soz("netlestirme.konu")'):
        assert yedek in blok, f"🔴 yedek cümle yok: {yedek}"
    # 🔴 Süzgeç YALNIZ gösterimde: `unknown`'a dokunmak kapsam kapısını gevşetir ve
    # `sessiz_yanlis` 12 → 13 çıkar (ölçüldü, §26.1).
    assert "unknown = [w for w in unknown" not in src, (
        "🔴 süzgeç kapsam kapısına sızmış — sessiz-yanlış artar")


def test_CAPRAZ_KONU_DALI_KORUNDU():
    """⚠ Genişlemenin sınırı: `other_topic` dalında gerçekten **rakip bir cube kimliği**
    var ve etiketleri göstermek anlamlı — o cümle kelime saymıyor.
    *Bir kuralı düzeltmek, komşusunu bozma hakkı vermez.*"""
    import inspect

    from app.routers import ask as ask_mod

    assert "başka bir konu gibi görünüyor" in inspect.getsource(ask_mod)
