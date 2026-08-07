"""🔴 `G6` — **R11: «anlaşıldı ama İFADE EDİLEMEZ»**.

## Neden ayrı bir kod

`R1` *"kelimeyi bilmiyorum"* der ve geliştiriciyi **kataloğa** yollar.
`R11` *"biliyorum ama söyleyemiyorum"* der ve **CEBİRE** yollar.

İkisi aynı koda düşerse `referans` alanının **hedef nüfusu hiç görünmez** — ve bir alanın
kaç soruyu kurtaracağı, o alan **yazılmadan** ölçülebilmelidir.

## ⚠ Fikstür UYDURULMAZ

İlk sürüm elle bir `schema` sözlüğü yazdı ve `TypeError: unhashable type: 'dict'`
patladı: `cube_router` boyutları **düz ad listesi** bekliyor, benim yazdığım
`[{"name": ...}]`'ti. Şemanın şekli bir **varsayım** değil, derlenmiş bir **olgudur** —
`conftest`'in `schema` fikstürü onu gerçek MDL'den verir. *Bir şemayı hatırlamak,
onu okumaktan her zaman daha pahalıdır.*

⚠ **Yalnız ölçüm**: davranış değişmez, `route()` yine `None` döner.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr
from app.niyet import coz_soru


def test_NIYET_temsil_edilemeyeni_ZATEN_hesapliyor():
    """🔴 `R11` yeni bir hesap DEĞİL — var olan bir hesabın **adlandırılmasıdır**.

    `KÖK-1 Faz 1`'de yazılan `Niyet.temsil_edilemeyen` bugün `cok_donem`/`kiyas`
    döndürüyor ama **hiçbir teşhis kodu** onu okumuyordu: sistem temsil edemediği şeyi
    sayabiliyor, ama o sayı **red gerekçesine** ulaşmıyordu."""
    n = coz_soru("mart cirosunu şubat ile kıyasla")
    assert n.temsil_edilemeyen, "Niyet kıyas/çok-dönem eksiğini görmüyor"


@pytest.mark.parametrize("soru", [
    "bu ay ile geçen ayı kıyasla",
    "borc mart ile nisanı kıyasla",
])
def test_R11_anlasilan_ama_ifade_edilemeyen(schema, soru):
    """Anlaşılan ama ifade edilemeyen sorular `R11` almalı."""
    if cr.route(cr._norm(soru), schema) is not None:
        pytest.skip(f"vaka bayat — {soru!r} artık cevaplanıyor")
    kod = cr.teshis(cr._norm(soru), schema)
    assert kod == "R11", (
        f"{soru!r} → {kod}. Beklenen R11: her kelime tanındı, niyet anlaşıldı, "
        f"eksik olan CEBİR. temsil_edilemeyen={coz_soru(cr._norm(soru)).temsil_edilemeyen}")


def test_TANINMAYAN_KELIME_hala_R10(schema):
    """🔴 Öncelik korunur: tanınmayan kelime varsa teşhis **R10**'dur.
    `R11` yalnız *"her kelime tanındı ama yine de olmadı"* durumunda çıkar — yoksa
    katalog eksiği ile cebir eksiği aynı kovaya düşer ve ikisi de görünmez olur."""
    q = cr._norm("zxqw plmk asdf")
    cr.route(q, schema)
    assert cr.teshis(q, schema) == "R10"


def test_DAVRANIS_DEGISMEDI(schema):
    """⚠ `R11` **yalnız ölçümdür**. `route()` yine `None` döner, cevap yolu aynı —
    bir alanın hedef nüfusu, o alan yazılmadan **önce** sayılabilmelidir."""
    q = cr._norm("bu ay ile geçen ayı kıyasla")
    assert cr.route(q, schema) is None


# --- 🔴 ÖLÇÜLEN SINIR: R11 tehlikenin YARISIDIR ------------------------------------


@pytest.mark.parametrize("soru", [
    "mart cirosunu şubat ile kıyasla",
    "2025 ve 2026 ciro karşılaştır",
])
def test_SESSIZ_YARIM_R11_DEGILDIR_ve_bu_bir_SINIRDIR(schema, soru):
    """🔴 **Ölçüldü (10 kıyas sorusu): red 3 · SESSİZ YARIM 5 · temiz 2.**

    Yani kıyas niyetinin **çoğunluğu reddedilmiyor** — *cevaplanıyor*, ve kıyas
    **sessizce düşüyor**. `2025 ve 2026 ciro karşılaştır` sorusu bugün **hiç dönem
    filtresi olmadan** cevaplanıyor: kullanıcı iki yıl adlandırdı, sorgu sıfır yıl taşıdı.

    ⚠ `R11` bunları **görmez ve görmemelidir**: teşhis yalnız `route()` pes ettiğinde
    hesaplanır. Bu sınıfın sahibi `uyum.denetle`'dir (BEYAN-AÇIK: cevabı öldürmez,
    **etiketler**). İki kapı iki farklı soruyu yanıtlar:

    | kapı | soru |
    |---|---|
    | `R11` | *"anladım ama söyleyemedim — kaç kez?"* |
    | `uyum` | *"söyledim ama eksik söyledim — kaç kez?"* |

    ⊙ **Katalog genelinde ölçüldü (408 kıyas sorusu):** `R11` **30** · `R10` **73** ·
    **cevaplandı 305**. Yani kıyas niyetinin **%75'i reddedilmiyor** — asıl kütle burada.

    *Reddedilen bir soru sayılabilir; sessizce yarım cevaplanan bir soru, sayılmadıkça
    başarı gibi görünür.*
    """
    from app.uyum import denetle

    q = cr._norm(soru)
    hit = cr.route(q, schema)
    assert hit is not None, f"vaka bayat — {soru!r} artık reddediliyor"
    assert cr.teshis(q, schema) != "R11", "cevaplanan soru teşhis üretmemeli"
    isaretler = {i.isaret for i in denetle(soru, hit)}
    assert isaretler & {"kiyas", "cok_donem"}, (
        f"{soru!r} sessizce yarım cevaplandı ve HİÇBİR kapı etiketlemedi: {isaretler}")


def test_BOS_SEMA_TUZAGINA_dusmez():
    """Şema okunamayıp `{}` gelirse teşhis **ham koda** düşer (`KÖK-9`'un kendi kapanı).
    `R11` o tuzağın arkasında durmalı: boş şemada `partial_unknowns` her kelimeyi
    tanınmaz sayar ve teşhis bir **yankı** üretir, bir bilgi değil."""
    q = cr._norm("mart cirosunu şubat ile kıyasla")
    cr.route(q, {})
    assert cr.teshis(q, {}) != "R11"


def test_BASARILI_route_R11_URETMEZ(schema):
    """Cevaplanan bir soru hiçbir teşhis üretmez — `R11` de dahil."""
    assert cr.route("bu yıl toplam ciro", schema) is not None
    assert cr.teshis("bu yıl toplam ciro", schema) is None


# --- 🔴 SESSİZLİĞİN KAPANIŞI — A/B ile ölçüldü -------------------------------------


def test_KIYAS_CEVABI_ARTIK_ETIKETSIZ_GITMIYOR(schema):
    """🔴 `G6`'nın **asıl kazancı** — ve `R11` değil, `uyum` tarafında.

    ⊙ A/B (408 kıyas sorusu, aynı kod, yalnız iki kural geri alınarak):

    | | etiketlenen | **sessiz** |
    |---|---|---|
    | eski | 61 | 🔴 **244** |
    | yeni | **305** | **0** |

    İki kural: (1) `TUR_KIYAS` artık kıyas **fiilini** de görüyor (`kiyas_niyeti`),
    (2) `" ile "` kıyas fiili varken **birliktelik** okunuyor, aralık değil.

    ⚠ Ters yön de ölçüldü: kıyas **istemeyen** 554 cevaplanan soruda **0 yeni etiket** —
    gerçek aralık (*"ocak ile mart arası ciro"*) dâhil. *Bir kapıyı genişletmenin bedeli,
    genişlemenin dışında kalanlarda ölçülmeden bilinmez.*
    """
    from app.uyum import denetle

    for soru in ("borc mart ile nisanı kıyasla",
                 "borc 2025 ile 2026 karşılaştır"):
        hit = cr.route(cr._norm(soru), schema)
        if hit is None:
            continue
        assert denetle(soru, hit), f"🔴 {soru!r} kıyassız cevaplandı ve ETİKETSİZ gitti"


def test_GERCEK_ARALIK_ETIKETLENMIYOR(schema):
    """⚠ Genişlemenin sınırı: *"ocak ile mart arası"* bir **aralıktır**, kıyas değil.
    `" ile "` yalnız kıyas fiili varken birliktelik okunur — yoksa bu kural meşru
    aralıkları kırmızıya boğar ve *"kullanılamayan kapı kapatılır"*."""
    from app.uyum import denetle

    soru = "ocak ile mart arası ciro"
    hit = cr.route(cr._norm(soru), schema)
    if hit is None:
        pytest.skip("⊘ route reddetti")
    isaretler = {i.isaret for i in denetle(soru, hit)}
    assert not (isaretler & {"kiyas", "cok_donem"}), (
        f"🔴 meşru aralık kıyas sanıldı: {isaretler}")


def test_KIYAS_NIYETI_YENI_SOZLUK_DEGIL():
    """🔴 `ADR-0008` — dile kelime listesiyle yetişilmez. `kiyas_niyeti` yeni bir sözlük
    kurmaz, var olan `_KIYAS_FIIL`'i bir **yüklem** olarak açar. İkinci bir liste,
    `strip_compare` ile bu yüklemin **ayrışması** demekti: sistem bir fiili söker ama
    saymaz — bugünkü kusurun ta kendisi."""
    import inspect

    src = inspect.getsource(cr.kiyas_niyeti)
    assert "_KIYAS_FIIL" in src, "kıyas fiilinin sahibi `_KIYAS_FIIL` olmalı"
    govde = [l for l in src.splitlines() if l.strip() and not l.strip().startswith(("#", '"'))]
    assert not any('"' in l and "=" in l for l in govde), "ikinci bir sözlük yazılmış"
