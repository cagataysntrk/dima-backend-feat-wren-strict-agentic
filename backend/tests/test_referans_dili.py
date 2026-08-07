"""🔴 `G6` — **REFERANS DİLİ**: kıyas bir MOD KODU değil, iki ADLANDIRILMIŞ UÇ.

## Ne eksikti — ve neden `compare` yetmiyordu

`compare` iki değerlik bir enum'dur (`yoy`/`mom`). Motor için doğru soyutlama budur:
`app/yoy.py` bir dönemi geri kaydırır. Ama **kullanıcı için değil**. *"Mart'ı şubatla
kıyasla"* diyen biri `mom` duymaz; iki dönem adı duyar. Üç sonucu ölçüldü:

| yüzey | `compare` ile | eksik olan |
|---|---|---|
| makbuz (`temellendirme`) | kıyas **hiç yazmıyordu** | hangi iki dönem |
| Intent-JSON | `compare` var, **`blend` yok** | çapraz-cube (`Ö11`) |
| `Niyet` izi | *"temsil-yok"* diyordu, oysa temsil vardı | `referans` |

## Tek temsil — ve neden bir ALAN değil

`referans` üç yerde doğabilirdi (`_coz_soru`, `route()`, `parse_cube_query`) ve üçü de
biraz farklı doğururdu. Bu deponun bir numaralı kusur sınıfı budur (`KAT-1`). Bu yüzden:

* **cebir** tek yerde: `app/kiyas_cebiri.py` — ve iki yönü (`referans_uret` ↔
  `referans_modu`) **aynı kaydırıcıya** (`shift_period_back`) sorar, yani gidiş-dönüş
  bir gün başka bir yere varamaz;
* **niyet tarafı** bir alan değil bir **türev**: `Niyet.referans` bir `@property`
  (doldurulacak bir yer yok → iki değer de yok);
* **sorgu tarafı** yalnız `parse_cube_query`'den girer ve **derlenemeyen geçmez**.

*Bir değeri iki yerden yazılabilir yapmak, iki değeri garanti etmektir.*

## ⚠ ÖLÇÜM DÜRÜSTLÜĞÜ — planın bir kapı maddesi burada KARŞILANMIYOR

Plan: *"Intent-JSON `referans` üretebiliyor (**canlı**, `--live`)"*. Bu koşumda gerçek
sağlayıcı **yok** (`RuleBasedSqlGenerator`) ve karşılanmış gibi de gösterilmiyor —
`test_sema_kisitli.py`'nin aynı şerhi. Burada kilitlenen şey **mekanizmadır**: şemanın
doğruluğu, kapının grain kontrolü, bayrağın kapatabilmesi. Oranın ölçümü `eval --slice
llm`'in işidir ve o dilim **4 vaka** — borç `OPERASYON-DURUM.md`'de yazılı.
"""

from __future__ import annotations

import ast
import json
import pathlib

import pytest

from app import cube_router as cr
from app import kiyas_cebiri as kc


# --- EŞDEĞERLİK ÖNCE ÖLÇÜLÜR (Faz 2 deseni) --------------------------------------

@pytest.mark.parametrize("mod,kaynak,hedef", [
    ("mom", {"gte": "2026-03-01", "lte": "2026-03-31"}, {"gte": "2026-02-01", "lte": "2026-02-28"}),
    ("yoy", {"gte": "2026-03-01", "lte": "2026-03-31"}, {"gte": "2025-03-01", "lte": "2025-03-31"}),
])
def test_REFERANS_MODA_CEVRILINCE_BIREBIR_AYNI(mod, kaynak, hedef):
    """🔴 `G6.2` — **eşdeğerlik önce ölçülür.** Yeni bir temsil, eskisinin ürettiği SQL'i
    değiştiriyorsa o bir temsil değil bir **davranış değişikliğidir** — ve öyleyse
    eşdeğerlik iddiasıyla değil, ölçümle savunulmalıydı."""
    ref = {"eksen": kc.EKSEN_DONEM, "kaynak": kaynak, "hedef": hedef}
    assert kc.referans_modu(ref) == mod


def test_INDIRGEME_ve_REFERANS_AYNI_SEYI_soyluyor():
    """İki uçlu aralık → `indirge` bir MOD verir, `referans_uret` iki UÇ verir. İkisi
    aynı olguyu anlatmalı; anlatmıyorsa biri ötekini **sessizce** yalanlıyordur."""
    flt = [{"dimension": "tarih", "operator": "gte", "value": "2026-02-01"},
           {"dimension": "tarih", "operator": "lte", "value": "2026-03-31"}]
    _, mod = kc.indirge(flt)
    ref = kc.referans_uret(flt)
    assert mod == "mom" and ref["eksen"] == kc.EKSEN_DONEM
    assert kc.referans_modu(ref) == mod, "🔴 gidiş-dönüş başka bir yere vardı"
    assert ref["kaynak"]["gte"] == "2026-03-01", "baz GEÇ olan dönem olmalı"


def test_INDIRGENEMEYEN_REFERANS_URETMEZ():
    """FAIL-CLOSED. *"Ocak ve haziran"* beş ay arayla; bir `referans` üretmek, motorun
    kuramayacağı bir kıyası **kurulmuş gibi** göstermek olurdu."""
    flt = [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"},
           {"dimension": "tarih", "operator": "lte", "value": "2026-06-30"}]
    assert kc.referans_uret(flt) is None


# --- KAPI: DERLENEMEYEN REFERANS GEÇMEZ ------------------------------------------

def test_DERLENEMEYEN_EKSEN_REDDEDILIR():
    """🔴 Sözlük beş eksen tanır; **derleyicisi olan** bir tanedir. Ötekileri geçirmek,
    sorguyu kıyassız çalıştırıp cevabı kıyasmış gibi sunmak olurdu."""
    for eksen in kc.EKSENLER:
        ref = {"eksen": eksen,
               "kaynak": {"gte": "2026-03-01", "lte": "2026-03-31"},
               "hedef": {"gte": "2026-02-01", "lte": "2026-02-28"}}
        gecti = kc.referans_dogrula(ref) is not None
        assert gecti == (eksen in kc.DERLENEN_EKSENLER), (
            f"🔴 `{eksen}` ekseni için kapı yanlış karar verdi (geçti={gecti})")


def test_DERLENEMEYEN_PENCERE_de_REDDEDILIR():
    """Eksen doğru ama uçlar indirgenemiyorsa yine geçmez: eksen adı bir **söz**, uçlar
    ise **kanıttır**."""
    assert kc.referans_dogrula({"eksen": kc.EKSEN_DONEM,
                                "kaynak": {"gte": "2026-03-01", "lte": "2026-03-31"},
                                "hedef": {"gte": "2025-06-01", "lte": "2025-06-30"}}) is None


def test_PARSE_referansi_COMPARE_ILE_BIRLIKTE_gecirir(schema):
    """🔴 `referans` ile `compare` **birlikte doğar ya da hiç doğmaz** — biri insanın
    okuduğu, öteki motorun okuduğu izdüşüm. Yalnız birini saklamak çeviriyi kaybetmektir."""
    _, index = cr.build_catalog(schema)
    ad = next(a for a, s in index.items() if s.get("measures") and s.get("time_dimensions"))
    cq = {"cube": ad, "measures": index[ad]["measures"][:1],
          "referans": {"eksen": "donem",
                       "kaynak": {"gte": "2026-03-01", "lte": "2026-03-31"},
                       "hedef": {"gte": "2026-02-01", "lte": "2026-02-28"}}}
    out = cr.parse_cube_query(json.dumps(cq), index)
    assert out and out.get("compare") == "mom" and out.get("referans"), out

    cq["referans"]["hedef"] = {"gte": "2025-06-01", "lte": "2025-06-30"}   # indirgenemez
    out2 = cr.parse_cube_query(json.dumps(cq), index)
    assert out2 and "referans" not in out2 and "compare" not in out2, (
        f"🔴 derlenemeyen referans sızdı: {out2}")


# --- TEK SAHİP (planın AST kapısı) -----------------------------------------------

def test_REFERANS_IKINCI_BIR_YERDE_URETILMIYOR():
    """🔴 Planın `G6.4` kapısı: *"`referans` bilgisi `Niyet` dışında ikinci bir yerde
    tutulmaz."*

    Tarama **yazma** arıyor: bir sözlüğe `["referans"] = …` koyan ya da `referans=`
    anahtar sözcüğüyle bir `referans` **kuran** her yer. Okumak serbesttir; ikinci bir
    **üretici** serbest değildir.

    ⚠ İzinli iki yer ve gerekçeleri:
    * `app/kiyas_cebiri.py` — cebrin kendisi (sözlüğün ve iki yönlü çeviricinin sahibi);
    * `app/cube_router.py` — tek **kapı** (`parse_cube_query`), ve orada bile üretmiyor,
      cebre soruyor.
    """
    kok = pathlib.Path(cr.__file__).resolve().parent
    izinli = {"kiyas_cebiri.py", "cube_router.py"}
    suclu: list[str] = []
    for yol in sorted(kok.rglob("*.py")):
        if yol.name in izinli:
            continue
        try:
            agac = ast.parse(yol.read_text(encoding="utf-8"))
        except SyntaxError:                                # pragma: no cover
            continue
        for d in ast.walk(agac):
            hedefler = (d.targets if isinstance(d, ast.Assign)
                        else [d.target] if isinstance(d, ast.AnnAssign) else [])
            for h in hedefler:
                if (isinstance(h, ast.Subscript) and isinstance(h.slice, ast.Constant)
                        and h.slice.value == "referans"):
                    suclu.append(f"{yol.name}:{d.lineno}")
    assert not suclu, (
        "🔴 `referans` ikinci bir yerde ÜRETİLİYOR: " + ", ".join(suclu) +
        " — iki üretici, bir gün iki farklı kıyas demektir (`KAT-1`).")


def test_NIYET_REFERANSI_BIR_ALAN_DEGIL_TUREV():
    """Doldurulacak bir yer yoksa iki değer de yoktur. `Niyet.referans` bir `@property`;
    `dataclasses.fields` içinde **görünmemeli**."""
    import dataclasses

    from app.niyet import Niyet

    assert "referans" not in {f.name for f in dataclasses.fields(Niyet)}, (
        "🔴 `referans` bir ALAN olmuş — artık üç yerden doldurulabilir")
    assert isinstance(getattr(Niyet, "referans"), property)


# --- BAYRAK: KAPALIYKEN BAYT BAYT BUGÜNKÜ ---------------------------------------

def test_BAYRAK_KAYITLI_ve_GERI_ALMA_YOLU_VAR():
    """`KURAL B`: kill-switch'i olmayan bir özelliğin `GERİ AL` satırı temennidir."""
    from app.features import FLAG_REGISTRY

    assert "referans_dili" in FLAG_REGISTRY
    kayit = FLAG_REGISTRY["referans_dili"]
    assert kayit.get("label") and kayit.get("description")


def test_BAYRAK_KAPALIYKEN_MAKBUZDA_KIYAS_SATIRI_YOK():
    """🔴 Kapalıyken makbuz **bugünkü** — ve bugünkü makbuzda kıyas satırı hiç yoktu."""
    from app.temellendirme import kur

    cq = {"cube": "parti", "measures": ["toplam_ciro"], "compare": "mom",
          "referans": {"eksen": "donem",
                       "kaynak": {"gte": "2026-03-01", "lte": "2026-03-31"},
                       "hedef": {"gte": "2026-02-01", "lte": "2026-02-28"}}}
    assert "kiyas" not in (kur(cq, cube_etiketi="parti") or {})
    acik = kur(cq, cube_etiketi="parti", kiyas=True) or {}
    assert acik.get("kiyas") == "2026-03 ↔ 2026-02", acik


@pytest.mark.parametrize("pencere,beklenen", [
    ({"gte": "2026-03-01", "lte": "2026-03-31"}, "2026-03"),
    ({"gte": "2026-01-01", "lte": "2026-12-31"}, "2026"),
    ({"gte": "2026-03-05", "lte": "2026-03-28"}, "2026-03-05 … 2026-03-28"),
])
def test_PENCERE_ADI_KISALTMASI_YALNIZ_TAM_ORTUSMEDE(pencere, beklenen):
    """⚠ *"5–28 mart"*a **mart** demek, kullanıcının sormadığı bir aralığı sorduğunu
    sanmasına yol açardı. Kısaltma bir kolaylık; yanlış kısaltma bir **yanlış cevaptır**."""
    from app.temellendirme import _pencere_adi

    assert _pencere_adi(pencere) == beklenen
