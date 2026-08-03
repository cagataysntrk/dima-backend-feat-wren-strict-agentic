"""FAZ D1 — SOSYAL SINIF: veri niyeti olmayan ifade SQL üretemez.

## Ölçülen kusur (3 Ağustos 2026)

Sistemde *"veri niyeti olmayan ifade"* diye bir sınıf **yoktu**. 16 sosyal ifade ölçüldü:

    merhaba · selam                     → source=meta   ✅  (`_META_HINTS`'te TESADÜFEN vardı)
    teşekkürler · sağol · günaydın · görüşürüz · tamam · peki · ok · süper · anladım ·
    eyvallah · iyi çalışmalar · çok iyi → source=rule   ❌  **12'si SQL ÜRETTİ**
    teşekkür ederim                     → *"«ederim» yerine «verim» mi demek istedin?"*
    harika                              → *"«harika» yerine «ariza» mi demek istedin?"*

Üretimde bunların **her biri bir LLM çağrısı** (ölçülen sınır: 10 sn'de 10 istek). Son iki
satır aynı kökün ikinci belirtisi: sınıf olmadığı için boru hattı sosyal kelimeyi **yanlış
yazılmış bir katalog terimi** sanıyor.

## İKİNCİ, TERS YÖNLÜ KUSUR — kibar kullanıcı cezalandırılıyordu

Aynı ölçümde çıktı: *"merhaba bu yıl makine bazında oee"* → **R10**, *"iyi çalışmalar,
geçen ay fire nedir"* → **R1**. Yani selamlaşan kullanıcı **cevapsız** kalıyordu. İkinci
vakanın kökü daha ince: `oee`'nin cube sinonimlerinden biri **`calisma`** ve *"iyi
çalışmalar"* kalıbı ona rakip bir kimlik enjekte ediyordu.

## Neden `_META_HINTS`'e kelime EKLENMEDİ

O liste elle yazılmış bir **torba**ydı (ürün soruları + selamlaşma karışık). `teşekkür`
eklemek ADR-0008'in yasakladığı şeydir — bir sonraki kelimede kusur tekrarlar. Kök neden
**sınıfın yokluğu**dur. Liste **büyümedi, KÜÇÜLDÜ**: selamlaşma oradan çıkıp sınıfa taşındı.

## Üç mekanizma, tek sözlük

| Mekanizma | Ne yapar |
|---|---|
| `veri_niyeti_var` | YAPISAL kapı: cube/boyut ∨ ölçü ∨ dönem ∨ kıyas ∨ liste sinyali var mı |
| `sosyal_edim` | SINIF: tür + **tam kaplama** (kalıp ifade tüm mesajı kaplıyor mu) |
| `sosyal_ayikla` | Kalıp ifadenin sözcüklerini **katalog eşleşmesinden çıkarır** |

Sözlüğün **tek sahibi** `cube_router` — çünkü dört tüketicisi var (sosyal cevap · kapsam
kapısı · takip düzenlemesi · kısmi-anlama). Ayrı liste tutmak iki tarafı ayrıştırırdı.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr

#: 16'sı da ölçülmüş gerçek vakalar; 12'si SQL üretiyordu.
SOSYAL = ["merhaba", "selam", "teşekkürler", "teşekkür ederim", "sağol", "eyvallah",
          "günaydın", "iyi çalışmalar", "görüşürüz", "tamam", "peki", "harika",
          "süper", "çok iyi", "anladım", "ok"]

#: Sosyal sözcük İÇEREN ama veri sorusu olan ifadeler — kapı bunları KESMEMELİ.
KIBAR_VERI = ["teşekkürler, bu yıl toplam ciro ne kadar",
              "merhaba bu yıl makine bazında oee",
              "iyi çalışmalar, geçen ay fire nedir"]


# --- ASIL KAPI: sosyal ifade SQL üretemez -----------------------------------------

@pytest.mark.parametrize("soru", SOSYAL)
def test_SOSYAL_ifade_SQL_URETMEZ(client, soru):
    from tests.conftest import ask

    d = ask(client, soru)
    assert not d.get("sql"), (
        f"{soru!r} SQL üretti (source={d.get('source')}) — üretimde bu bir LLM çağrısı "
        "ve uydurma bir sorgudur")
    assert d.get("source") in ("meta", "catalog"), (
        f"{soru!r} → source={d.get('source')}; sosyal ifade deterministik yanıt almalı")


@pytest.mark.parametrize("soru", KIBAR_VERI)
def test_KIBAR_veri_sorusu_CEVAPLANIYOR(client, soru):
    """Ters yön: kapı fazla geniş olursa selamlaşan kullanıcı cevapsız kalır — ölçüldü,
    düzeltmeden ÖNCE `merhaba…oee` **R10**, `iyi çalışmalar…fire` **R1** veriyordu."""
    from tests.conftest import ask

    d = ask(client, soru)
    assert d.get("sql"), f"{soru!r} cevapsız kaldı (source={d.get('source')})"


# --- YAPISAL KAPI ------------------------------------------------------------------

def test_VERI_NIYETI_sinyalsiz_ifadede_YOK(schema):
    for q in ("tesekkurler", "gorusuruz", "ok", "merhaba"):
        assert not cr.veri_niyeti_var(q, schema), f"{q!r} veri sorusu sayıldı"


def test_VERI_NIYETI_gercek_soruda_VAR(schema):
    for q in ("bu yil ciro", "makine bazinda oee", "gecen ay fire",
              "listele musteri", "bu yil ile gecen yil kiyasla"):
        assert cr.veri_niyeti_var(q, schema), f"{q!r} veri sorusu SAYILMADI"


def test_VERI_NIYETI_var_olan_fonksiyonlari_CAGIRIYOR():
    """Yeni bir sinyal listesi yazılmadı — beşi de ZATEN VAR olan kapılar. Ayrı liste
    tutmak `route()`'un gerçekte baktığından başka bir şeye bakmaya başlardı."""
    import inspect

    govde = inspect.getsource(cr.veri_niyeti_var)
    for fn in ("_period_hit_words", "compare_mode", "liste_niyeti",
               "ilgili_cubelar", "measure_cube_candidates"):
        assert fn in govde, f"{fn} çağrılmıyor — sinyal kaynağı ayrışıyor"


# --- SINIF + TAM KAPLAMA ------------------------------------------------------------

def test_TAM_KAPLAMA_kalip_ifadeyi_SOSYAL_sayar():
    """*"iyi çalışmalar"* kalıp ifadedir; `çalışma` katalogda gerçek bir terim olsa bile
    parçası olduğu kalıbın anlamı geçerlidir."""
    tur, tam = cr.sosyal_edim("iyi calismalar")
    assert tur == "kapanis" and tam is True


def test_TAM_KAPLAMA_veri_sorusunda_KAPANIR():
    tur, tam = cr.sosyal_edim("tesekkurler bu yil ciro")
    assert tur == "tesekkur" and tam is False, "sosyal sözcük İÇEREN veri sorusu sosyal sayıldı"


def test_SOSYAL_EDIM_veri_sorusunda_None_DEGIL_ama_TAM_degil():
    """Sınıf bulunur (sözcük var) ama kaplama yoktur — karar çağıranın."""
    assert cr.sosyal_edim("bu yil ciro") is None


# --- AYIKLAMA: katalog eşleşmesi kalıbı görmez -------------------------------------

def test_AYIKLAMA_kalip_sozcuklerini_CIKARIR():
    assert cr.sosyal_ayikla("iyi calismalar gecen ay fire") == "gecen ay fire"


def test_AYIKLAMA_NOKTALAMALI_cumlede_de_calisir():
    """İlk sürüm `_norm`'un koruduğu virgülü hesaba katmıyordu ve `"calismalar,"`
    token'ını ayıklayamıyordu — kusur virgüllü cümlede aynen sürüyordu."""
    assert "calismalar" not in cr.sosyal_ayikla("iyi çalışmalar, geçen ay fire nedir")


def test_AYIKLAMA_KALIBA_bagli_kelimeye_DEGIL():
    """`"calismalar bazinda"` sorusunda `iyi calismalar` kalıbı eşleşmez → `calisma`
    DOKUNULMADAN kalır ve `oee` kimliğini korur. Ayıklama kalıba bağlıdır."""
    assert "calismalar" in cr.sosyal_ayikla("calismalar bazinda oee")


def test_AYIKLAMA_hepsi_dusunce_HAM_hali_doner():
    """Boş dize her kapıyı anlamsız kılardı."""
    assert cr.sosyal_ayikla("tesekkurler").strip()


# --- SÖZLÜK TEK SAHİPLİ, LİSTE BÜYÜMÜYOR -------------------------------------------

def test_META_HINTS_BUYUMEDI_selamlasma_CIKTI():
    """Kapının kendi sınavı: ADR-0008 kelime yaması yasak. Liste büyürse yine yama
    yapılmış demektir."""
    from app.routers.ask import _META_HINTS

    for selam in ("merhaba", "selam", "naber", "napiyorsun"):
        assert selam not in _META_HINTS, (
            f"{selam!r} hâlâ `_META_HINTS` torbasında — sosyal sınıfa taşınmalıydı")
    assert len(_META_HINTS) <= 14, f"liste büyümüş: {len(_META_HINTS)}"


def test_SOZLUK_TEK_SAHIPLI():
    """Dört tüketici aynı sözlüğü okur; `ask.py` kendi kopyasını tutmaz."""
    import inspect

    from app.routers import ask as ask_mod

    assert not hasattr(ask_mod, "_SOSYAL_SELAM"), "ask.py sözlüğün ikinci kopyasını tutuyor"
    assert "cube_router.sosyal_edim(" in inspect.getsource(ask_mod.ask)


def test_SOSYAL_SOZCUK_kapsam_kapisinda_DOLGU():
    """Dört tüketicinin hepsinde dolgu sayılmalı — biri atlanırsa aynı soru geldiği yola
    göre farklı davranır (Faz -1'in "üç çağrı yeri" dersi)."""
    import inspect

    kaynak = inspect.getsource(cr)
    assert kaynak.count("known |= _sosyal_hit_words(q)") >= 3, \
        "sosyal dolgu tüm kapsam kapılarına bağlı değil"
    assert "_sosyal_hit_words(q)" in inspect.getsource(cr.ilgili_cubelar), \
        "konu daraltmasında sosyal sözcük hâlâ konu sinyali sayılıyor"
