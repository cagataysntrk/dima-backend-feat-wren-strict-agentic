r"""🔴🔴 `§F7` — **DÜZYAZI `ciro` VAAT EDİYOR, CHİPLER `arıza` VERİYORDU.**

## İki kusur, ve ikisi birbirini besliyordu (denetim ajanı + kendi ölçümüm, 08-12)

**① Elle yazılmış örnek bir ÇIKMAZDI — ve modül bunu kendi docstring'inde yazmıştı.**
`yetenek.py`'nin `forecast` dalı *«Yapabildiğim: … «son 6 ayda ciro nasıl gitti»»* diyordu.
Ölçüldü (gerçek katalog):

    route(_norm("son 6 ayda ciro nasıl gitti"))  →  None     ← ÇIKMAZ
    route(_norm("son 6 ayda ciro"))              →  dict     ← ÇALIŞIYOR

`onerileri_kur`'un kendi docstring'i riski **önceden** yazmış: *«`Sinir.mesaj` içindeki
örnekler elle yazılmış … o cube yoksa öneri **ikinci bir duvara** çarptırır.»* Doğrulanmış
chip yolu **yazılmış ve bağlanmıştı**; silinmemiş olan **cümlenin kendisiydi**.

**② Chipler KONU-KÖRDÜ — üç ayrı sebeple.**

| sebep | ölçüm |
|---|---|
| katalog sırası | `for c in schema["cubes"][:6]` — alfabetik: `bakim`·`bakim_is_emri`·… |
| erken çıkış | ilk cube üç slotu doldurunca `return` — soru yükleme **hiç girmiyordu** |
| **sabit dilim** | `measures[:2]` — `parti`'nin **11** ölçüsü var, `toplam_ciro` **5. sırada** |

Canlı: *«gelecek ay ciro tahmini»* → `['son 6 ayda arıza sayısı', 'bu yıl arıza sayısı',
'son 6 ayda arıza duruşu']`. ⊙ Chipler `route()`-doğrulamalı olduğu için **ikinci duvara
çarptırmıyorlardı**; çarptıran **düzyazının kendisiydi**.

## Onarım — üç madde, hiçbiri yeni eşleştirici yazmıyor (`KAT-1`)

1. `soru` verilirse cube'lar `cube_router.ilgili_cubelar` ile **yeniden sıralanır**.
2. Adaylar cube'lar arasında **dönüşümlü** denenir — tek cube bütün slotları yemez ama
   `en_fazla` yine doldurulabilir (kör bir *«cube başına 2»* tavanı kapsamı **düşürürdü**).
3. Sorunun andığı ölçüler **dilimden önceye** alınır; ölçüt `cube_router._syn_hit`
   (biçimbirim disiplinli, kapalı — yeni sözcük listesi yok, `ADR-0008`).

⚠ **İlk düzeltmem YARIMDI (ders ㉚, iki kez):** ① cube'u başa almak yetmedi, sabit dilim
ölçüyü yine saklıyordu; ② sinonimi **ölçü sözlüğünde** aradım ve boş döndü — gerçek
katalogda görünen ad cube düzeyindeki `measure_synonyms_display`'dedir
(`toplam_ciro → «ciro»`, ölçüldü).

> *Bir tavanın altında kalan doğru cevap, yanlış cevaptan ayırt edilemez.*
"""

from __future__ import annotations

from app import cube_router, yetenek
from app.yetenek import kapsam_disi, onerileri_kur


def _chipler(schema, soru: str) -> list[str]:
    s = kapsam_disi(soru, schema)
    return [o["query"] for o in (getattr(s, "oneriler", None) or [])]


def test_OLCUM_TABANI_ESKI_ORNEK_GERCEKTEN_CIKMAZ(schema):
    """⊘ **Boş yeşil avı.** Eski örnek route ediyorsa bu kartın öncülü çürüktür ve
    aşağıdaki yüklemler boşa düşer."""
    assert cube_router.route(cube_router._norm("son 6 ayda ciro nasıl gitti"),
                             schema) is None, (
        "⊘ ölçüm tabanı: eski elle yazılmış örnek artık route EDİYOR — `§F7`'nin "
        "öncülü değişmiş, kart yeniden okunmalı.")
    assert cube_router.route(cube_router._norm("son 6 ayda ciro"), schema) is not None, (
        "⊘ ölçüm tabanı: kısa hâli de route etmiyor — katalogda `ciro` kalmamış olabilir.")


def test_CHIPLER_SORULAN_OLCUYU_GETIRIYOR(schema):
    """🔴🔴 **ASIL KAPI.** Kullanıcı `ciro` sorduysa chip `ciro` olmalı — `arıza` değil.

    ⚠ Yüklem **ilk chip**e bağlı: konu duyarlılığı bir *sıralama* iddiasıdır. Listede
    bir yerde geçmesi yetmez; *«soruyu gördü»* demek onu **öne** koymak demektir.
    """
    for soru, beklenen in (("gelecek ay ciro tahmini", "ciro"),
                           ("önümüzdeki çeyrek fire tahmini", "fire")):
        ch = _chipler(schema, soru)
        assert ch, f"⊘ ölçüm tabanı: «{soru}» için hiç chip üretilmedi"
        assert beklenen in ch[0], (
            f"🔴 KONU-KÖR: «{soru}» soruldu, ilk chip «{ch[0]}» — chipler soruyu "
            f"görmüyor. Tam liste: {ch}")


def test_DUZYAZI_ILE_CHIPLER_TEK_KAYNAKTAN(schema):
    """🔴 Kusur ① — düzyazıdaki örnek artık **ilk doğrulanmış chip'ten** türer. İkisi
    ayrı kaynaktan gelirse bir gün yine ayrışır ve düzyazı bir çıkmaz vaat eder."""
    soru = "gelecek ay ciro tahmini"
    s = kapsam_disi(soru, schema)
    mesaj, ch = (getattr(s, "mesaj", "") or ""), _chipler(schema, soru)
    assert ch, "⊘ ölçüm tabanı: chip yok"
    assert f"«{ch[0]}»" in mesaj, (
        f"🔴 düzyazıdaki örnek chip listesinden GELMİYOR — ikisi ayrışabilir.\n"
        f"chip[0]={ch[0]!r}\nmesaj kuyruğu={mesaj[-180:]!r}")


def test_DUZYAZIDA_ELLE_YAZILMIS_CIKMAZ_ORNEK_KALMADI_yapisal(schema):
    """🔴 Yapısal: `forecast` dalının gövdesinde artık **sabit bir örnek cümle**
    olmamalı. *Bir kusuru düzeltip onu üreten satırı bırakmak, düzeltmeyi bir sonraki
    turun geri alması demektir.*"""
    import inspect

    kaynak = inspect.getsource(yetenek)
    assert "son 6 ayda ciro nasıl gitti" not in kaynak.split('"""')[0] or True, ""
    # Yalnız KOD gövdesinde ara: docstring'lerde tarihsel kayıt olarak durabilir.
    import ast
    import textwrap

    agac = ast.parse(textwrap.dedent(kaynak))
    dizeler = {n.value for n in ast.walk(agac)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    # docstring'leri çıkar
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.FunctionDef | ast.ClassDef | ast.Module):
            d = ast.get_docstring(dugum, clean=False)
            if d:
                dizeler.discard(d)
    kacak = [d for d in dizeler if "nasıl gitti" in d]
    assert not kacak, (
        f"🔴 elle yazılmış örnek cümle KOD gövdesinde hâlâ var: {kacak} — `route()` onu "
        "doğrulamıyor ve kullanıcıyı ikinci bir duvara çarptırır.")


def test_TEK_CUBE_BUTUN_SLOTLARI_YEMIYOR(schema):
    """⚠ Dönüşümlü sıra bir **kapsam** kararıdır: eski gövde ilk cube'un üç ölçüsünü
    basıp dönüyordu ve katalogun geri kalanı hiç görünmüyordu."""
    ch = _chipler(schema, "gelecek ay ciro tahmini")
    assert len(ch) >= 2, f"⊘ ölçüm tabanı: {len(ch)} chip"
    assert len(set(ch)) == len(ch), f"🔴 yinelenen chip: {ch}"
    # Aynı ölçü adının üç kez geçmesi (tek cube'un yendiği hâl) reddedilir.
    ilk_kelime = [c.split()[-1] for c in ch]
    assert len(set(ilk_kelime)) >= 2, (
        f"🔴 chiplerin hepsi aynı ölçüden türemiş — tek cube bütün slotları yemiş: {ch}")


def test_SORU_VERILMEZSE_ESKI_DAVRANIS_KORUNUYOR(schema):
    """⚠ `soru=None` bir **geri uyumluluk** yoludur (`KURAL B` disiplini): sıralama
    yapılmaz, katalog sırası korunur. Yeni parametre eski çağıranı bozmamalı."""
    a = [o["query"] for o in onerileri_kur(schema, tur="forecast")]
    assert a, "⊘ ölçüm tabanı: `soru`suz çağrı hiç chip üretmedi"
    b = [o["query"] for o in onerileri_kur(schema, tur="forecast", soru=None)]
    assert a == b, f"🔴 `soru=None` ile varsayılan çağrı AYRIŞTI:\n{a}\n{b}"


def test_HER_CHIP_ROUTE_EDIYOR(schema):
    """🔴 Değişmez korunuyor: *«aynı duvara ikinci kez çarptıran bir chip, chip
    olmamasından kötüdür.»* Yeni sıralama bu doğrulamayı atlamamalı."""
    for soru in ("gelecek ay ciro tahmini", "önümüzdeki çeyrek fire tahmini"):
        for c in _chipler(schema, soru):
            assert cube_router.route(cube_router._norm(c), schema) is not None, (
                f"🔴 DOĞRULANMAMIŞ chip basıldı: «{c}» ({soru})")
