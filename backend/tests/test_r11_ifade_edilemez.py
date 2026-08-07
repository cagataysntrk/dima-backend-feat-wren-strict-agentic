"""🔴 `G6` — KIYAS EKSENİ, ve **`R11`'in ÖLÇÜLÜP GERİ ALINMASI**.

## Dosya adı bir kararın kaydıdır

Bu dosya `R11` (*"anlaşıldı ama ifade edilemez"*) kodu için açıldı. Kod yazıldı, nüfusu
ölçüldü (**30/408**), makul görünüyordu — ve **kapı çürüttü**:

> `test_TANINAN_SORUDA_HAM_KOD_KORUNUYOR`: *"tanınmayan kelime **yoksa** ham kapı kodu
> **olduğu gibi** kalır. Her reddi R10 yapmak, teşhisi ikinci kez yanlış yapardı."*

`R11` tam bunu yapıyordu: `R9` diye gerçek bir gerekçe varken onu **örtüp** geliştiriciyi
cebire yolluyordu — oysa cebir zaten indi (`app/kiyas_cebiri.py`) ve o sorular **başka**
bir sebepten düşüyordu. `KÖK-9`'un kendi cümlesi: *kusuru gizlemekten daha kötüsü yanlış
yeri işaret etmektir.*

⊙ **Ders:** *bir sayının varlığı, o sayının doğru şeyi saydığının kanıtı değildir.*
30 vaka gerçekti; **etiketleri** gerçek değildi.

Dosya **silinmedi** (*kapananlar işaretlenir, silinmez* — `MIMARI §10`): adı kararın
kaydını taşır, içeriği ayakta kalan **kıyas ekseni** kapılarıdır.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr
from app.niyet import coz_soru


# --- ⊘ GERİ ALINAN KARAR KİLİTLENDİ ------------------------------------------------


def test_R11_GERI_ALINDI_ve_geri_gelmemeli():
    """🔴 Teşhis, `route()`'un **gerçekten** hangi dalda durduğunu söyler; bir yüklemin
    varlığından türetilen kod, o gerçeği örter."""
    kaynak = (cr.__file__ and open(cr.__file__, encoding="utf-8").read()) or ""
    assert 'return "R11"' not in kaynak, (
        "🔴 `R11` geri gelmiş. Ölçüldü ve geri alındı: gerçek gerekçeyi (`R9`, `R1`, …) "
        "ÖRTÜYORDU. Yeniden eklenecekse önce `test_TANINAN_SORUDA_HAM_KOD_KORUNUYOR`'un "
        "kuralı karşılanmalı — ham kod tanınan soruda korunur.")
    assert "R11 DENENDİ ve GERİ ALINDI" in kaynak, "kararın kaydı silinmiş"


def test_TANINMAYAN_KELIME_R10(schema):
    """Öncelik değişmedi: tanınmayan kelime varsa teşhis **R10**'dur."""
    q = cr._norm("zxqw plmk asdf")
    cr.route(q, schema)
    assert cr.teshis(q, schema) == "R10"


def test_BASARILI_route_TESHIS_URETMEZ(schema):
    assert cr.route("bu yıl toplam ciro", schema) is not None
    assert cr.teshis("bu yıl toplam ciro", schema) is None


# --- NİYET NESNESİ -----------------------------------------------------------------


def test_NIYET_temsil_edilemeyeni_ARTIK_YANILTMIYOR():
    """🔴 `G6.4` — **KAYITLI BORÇ KAPANDI, ve tuzağı TERSİNE ÇEVRİLDİ.**

    Bu testin eski hâli `assert …temsil_edilemeyen` diyordu ve kendi şerhi kusuru
    itiraf ediyordu: *"bu **soruya** bakar, **sorguya** değil: `route()` indirgeme yapsa
    bile iz hâlâ «temsil-yok» yazar… iz YANILTICIDIR."* Yani yeşil olan şey, düzeltilmesi
    gereken şeydi.

    ⊙ Sebep ölçüldü: hesap yalnız **kaç dönem adlandığına** bakıyordu. `Niyet.referans`
    artık cebrin indirgeyicisine soruyor — iz ile sorgu **aynı kaynağa** bakıyor.

    ⚠ Ve kapı iki yönlü: indirgenemeyen kıyas hâlâ *temsil-yok* demeli. Tek yönlü bir
    kapı, borcu kapatmak yerine **ters yöne** kaydırırdı.

    *Kapananlar işaretlenmez — tuzakları TERSİNE çevrilir; yoksa kapanış, yalnızca
    testin susturulması olur.*
    """
    # (a) indirgenebilir kıyas → temsil EDİLEBİLİR (eski hâlde burada "cok_donem" yazardı)
    n = coz_soru("mart cirosunu şubat ile kıyasla")
    assert n.referans and n.referans["eksen"] == "donem", "iki uç adlandırılmadı"
    assert not n.temsil_edilemeyen, (
        f"🔴 indirgenen kıyas hâlâ temsil-yok diyor: {n.temsil_edilemeyen} — "
        f"borç kapandı sanılmış ama iz eski kaynaktan okuyor")

    # (b) indirgenemeyen kıyas → temsil-YOK demeye DEVAM etmeli
    n2 = coz_soru("ocak ve haziran cirosunu karşılaştır")
    assert n2.referans is None, "5 ay arayla indirgeme YOK — cebir gevşemiş"
    assert n2.temsil_edilemeyen, "🔴 indirgenemeyen kıyas sessizleşti"


# --- 🔴 KIYASIN İKİ AKIBETİ — ikisi de dürüst --------------------------------------


@pytest.mark.parametrize("soru,indirgenir", [
    ("mart cirosunu şubat ile kıyasla", True),            # bitişik ay → `mom`
    ("ocak ve haziran cirosunu karşılaştır", False),      # 5 ay arayla → indirgenemez
])
def test_KIYASIN_IKI_AKIBETI(schema, soru, indirgenir):
    """⊙ Ölçüldü (408 kıyas sorusu): red 103 · cevaplandı 305.

    `G6` öncesinde o cevapların kıyası **sessizce düşüyordu**: *"mart cirosunu şubat ile
    kıyasla"* **1 Şubat–31 Mart TOPLAMINI** döndürüyordu. Artık iki akıbet var:

    | | sonuç | sahibi |
    |---|---|---|
    | indirgenebilir | `compare` kurulur, **kıyas gerçekten hesaplanır** | `kiyas_cebiri` |
    | indirgenemez | ihlal **etiketlenir**, cevap yaşar | `uyum` (BEYAN-AÇIK) |
    """
    from app.uyum import denetle

    q = cr._norm(soru)
    hit = cr.route(q, schema)
    if hit is None:
        pytest.skip("⊘ route reddetti — vaka bayat")
    ic = hit.get("cube_query") or {}
    if indirgenir:
        assert ic.get("compare") in ("mom", "yoy"), (
            f"🔴 {soru!r} indirgenebilirdi ama kıyas kurulmadı: {ic.get('filters')}")
        assert not denetle(soru, hit), "kıyas kurulduysa ihlal kalmamalı"
    else:
        assert {i.isaret for i in denetle(soru, hit)} & {"kiyas", "cok_donem"}, (
            f"🔴 {soru!r} indirgenemedi ve ETİKETSİZ gitti")


def test_KIYAS_CEVABI_ARTIK_ETIKETSIZ_GITMIYOR(schema):
    """🔴 `G6`'nın **asıl kazancı** — ve `R11` değil, `uyum` tarafında.

    ⊙ A/B (408 kıyas sorusu, aynı kod, yalnız iki kural geri alınarak):

    | | etiketlenen | **sessiz** |
    |---|---|---|
    | eski | 61 | 🔴 **244** |
    | yeni | **305** | **0** |

    İki kural: (1) `TUR_KIYAS` artık kıyas **fiilini** de görüyor (`kiyas_niyeti`),
    (2) `" ile "` kıyas fiili varken **birliktelik** okunuyor, aralık değil.
    """
    from app.uyum import denetle

    # 🔴 **BOŞUNA YEŞİL KAPANDI (denetim bulgusu).** Eskiden `if hit is None: continue`
    # vardı ve döngü dışında hiçbir iddia yoktu: iki soru da `route()`'tan düşerse test
    # **hiç iddia koşmadan** yeşil geçiyordu. Oysa bu, `G6`'nın *"sessiz 244 → 0"*
    # kazancının tek regresyon kapısı.
    # *Bir testin geçmesi, bir şeyi sınadığı anlamına gelmez — kaç kez sınadığını da
    # saymak gerekir.*
    # 🔴 **VE SAYAÇ KENDİ İŞİNİ YAPTI — vakalar BAYATTI.** Eski iki soru `borc` ölçüsünü
    # anıyordu; bu katalogda öyle bir ölçü **yok** (`mizan`'ınki `bakiye`), yani ikisi de
    # `R1`'den düşüyordu ve kapı `olculen == 0` ile kırmızıya döndü. Sayaç eklenmeseydi
    # bu dosya **yeşil görünmeye devam ederdi** — hiçbir şey ölçmeden.
    # ⊙ *Bir kapının bayatlaması sessizdir: kırmızıya dönmez, ölçmeyi bırakır.*
    olculen = 0
    for soru in ("ciro mart ile nisanı kıyasla", "fire mart ile nisanı kıyasla"):
        hit = cr.route(cr._norm(soru), schema)
        if hit is None:
            continue
        olculen += 1
        ic = hit.get("cube_query") or {}
        assert ic.get("compare") or denetle(soru, hit), (
            f"🔴 {soru!r} kıyassız cevaplandı ve ETİKETSİZ gitti")
    assert olculen, (
        "⊘ HİÇBİR VAKA ÖLÇÜLMEDİ — iki soru da `route()`'tan düştü. Bu bir başarı "
        "değil, ölçümün YOKLUĞU: vakalar bayatlamış olabilir. Ya vakaları tazele, ya "
        "kapının konusunu değiştir.")


def test_GERCEK_ARALIK_ETIKETLENMIYOR(schema):
    """⚠ Genişlemenin sınırı: *"ocak ile mart arası"* bir **aralıktır**, kıyas değil.

    ⊙ Ters yön ölçüldü: kıyas **istemeyen** 554 cevaplanan soruda **0 yeni etiket**.
    *Bir kapıyı genişletmenin bedeli, genişlemenin dışında kalanlarda ölçülmeden
    bilinmez* — ve kullanılamayan bir kapı kapatılır."""
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
    saymaz — düzelttiğimiz kusurun ta kendisi."""
    import inspect

    src = inspect.getsource(cr.kiyas_niyeti)
    assert "_KIYAS_FIIL" in src, "kıyas fiilinin sahibi `_KIYAS_FIIL` olmalı"
    govde = [l for l in src.splitlines()
             if l.strip() and not l.strip().startswith(("#", '"'))]
    assert not any('"' in l and "=" in l for l in govde), "ikinci bir sözlük yazılmış"
