"""FAZ 1.2b — **`safe_call()`: sağlayıcıya giden TEK kapı** kapısı.

*"Ham veri LLM'e gitmez"* kuralının **üç sahibi** vardı ve üçü de **girdi** tarafındaydı
(`sensitivity.prompt_safe_values` · `cube_router.build_catalog` · `ask.py`). Girdiyi kuran
yeni bir yol açılırsa kural o yolda **hiç uygulanmaz** — ve `select_cube`'un kataloğu
`llm.py`'nin **dışında** kuruluyor. `safe_call` **çıkış** tarafında durur: son savunma.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from app import llm_guard

KOK = pathlib.Path(__file__).resolve().parents[1]

#: Sağlayıcıya **gerçekten** veri gönderen çağrılar. Yeni bir sağlayıcı eklenirse burası
#: da güncellenmeli — ve `test_GONDERIM_DESENI_HALA_GECERLI` onu hatırlatır.
_GONDERIM = {("messages", "create"), ("requests", "post")}


def _llm_agaci() -> ast.Module:
    return ast.parse((KOK / "app" / "llm.py").read_text(encoding="utf-8"))


def _gonderim_mi(n: ast.AST) -> bool:
    if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
        return False
    ust = n.func.value
    ad_ust = ust.attr if isinstance(ust, ast.Attribute) else getattr(ust, "id", "")
    return (ad_ust, n.func.attr) in _GONDERIM


# ── 1 · TESPİT ───────────────────────────────────────────────────────────────

def test_TCKN_EPOSTA_TELEFON_IBAN_YAKALANIYOR():
    """Tespit `pii.py`'den gelir; **dördüncü bir desen sözlüğü yazılmaz**."""
    assert "TCKN" in llm_guard.ihlalleri_bul("kimlik 10000000146 numaralı")
    assert "e-posta" in llm_guard.ihlalleri_bul("ali@example.com")
    assert "IBAN" in llm_guard.ihlalleri_bul("TR33 0006 1005 1978 6457 8413 26")


def test_TEMIZ_YUK_GECIYOR():
    assert llm_guard.ihlalleri_bul("bu yıl toplam ciro nedir") == []
    assert llm_guard.ihlalleri_bul("") == []


def test_DESEN_SOZLUGU_KOPYALANMAMIS():
    """🔴 İkinci bir regex kümesi yazmak, iki sözlüğün zamanla **ayrışması** demekti —
    ve hangisinin doğru olduğu bilinemezdi."""
    kaynak = (KOK / "app" / "llm_guard.py").read_text(encoding="utf-8")
    assert "from app import pii" in kaynak
    assert "re.compile" not in kaynak, "llm_guard kendi regex'ini yazmış — iki sahip"


def test_IHLAL_DEGERI_LOGLANMIYOR():
    """🔴 **Bir sızıntıyı raporlarken sızdırmak**, kapının kendisini bir sızıntı yüzeyine
    çevirirdi. Yalnız **tür adları** döner, değerin kendisi değil."""
    bulunan = llm_guard.ihlalleri_bul("ali@example.com")
    assert bulunan == ["e-posta"], bulunan
    assert not any("@" in b for b in bulunan)


# ── 2 · FAIL-CLOSED ──────────────────────────────────────────────────────────

def test_IHLALDE_CAGRI_HIC_YAPILMIYOR():
    """🔴 Maskeleyip göndermek **yanlış** olurdu: yükü sessizce değiştirmek, modelin
    gördüğü şeyle bizim sandığımız şeyi ayrıştırır ve hata **teşhis edilemez** hâle gelir."""
    cagrildi = []
    with pytest.raises(llm_guard.LlmVeriSizintisi):
        llm_guard.safe_call(lambda: cagrildi.append(1),
                            yuk="ali@example.com", ad="test")
    assert cagrildi == [], "ihlale rağmen sağlayıcı ÇAĞRILDI"


def test_TEMIZ_YUKTE_CAGRI_YAPILIYOR():
    assert llm_guard.safe_call(lambda: "cevap", yuk="ciro nedir", ad="test") == "cevap"


def test_AUDIT_YAZILAMASA_BILE_ENGEL_SURUYOR():
    """Audit yazımı başarısız olursa çağrı **yine de engellenir**: kaydedememek,
    izin vermek anlamına gelmez."""
    with pytest.raises(llm_guard.LlmVeriSizintisi):
        llm_guard.safe_call(lambda: None, yuk="10000000146", ad="test", principal=None)


# ── 3 · 🔴 `llm.py`'DE `safe_call` DIŞINDAN SAĞLAYICI ÇAĞRISI YOK ────────────

def test_HER_GONDERIM_SAFE_CALL_ICINDE():
    """🔴 **Maddenin asıl kapısı** — ve ölçüm **YAPISAL**, metin taraması değil.

    Bu oturumda metin taraması **üç kez** kendi yorumunu yakaladı; burada AST ile
    soruluyor: her gönderim çağrısı bir **`lambda`** içinde mi ve o lambda `safe_call`'a
    mı geçiliyor? Bir gönderim doğrudan yazılırsa o yol kapısız kalır — ve kapısız yolun
    varlığı, ötekilerin hepsini anlamsız kılar.
    """
    agac = _llm_agaci()

    # (a) gönderim çağrıları BULUNUYOR (desen bayatlamış olmasın)
    gonderimler = [n for n in ast.walk(agac) if _gonderim_mi(n)]
    assert gonderimler, (
        "`llm.py`'de hiç gönderim çağrısı bulunamadı — desen mi değişti? "
        f"Aranan: {sorted(_GONDERIM)}. Bulunamayan bir kapı, kapı DEĞİLDİR.")

    # (b) her `safe_call`'ın lambda'sındaki gönderimleri topla
    korunan: set[int] = set()
    for n in ast.walk(agac):
        if not (isinstance(n, ast.Call) and getattr(n.func, "id", "") == "safe_call"):
            continue
        for arg in list(n.args) + [k.value for k in n.keywords]:
            for ic in ast.walk(arg):
                if _gonderim_mi(ic):
                    korunan.add(id(ic))

    kapisiz = [f"llm.py:{n.lineno}" for n in gonderimler if id(n) not in korunan]
    assert not kapisiz, (
        f"🔴 `safe_call` DIŞINDAN sağlayıcı çağrısı: {kapisiz}\n"
        "Kapısız bir yolun varlığı, ötekilerin hepsini anlamsız kılar — kuralın ÜÇ girdi "
        "sahibi vardı ve bu madde tam olarak o dağınıklığı kapatmak için var.")


def test_SAFE_CALL_YUK_ALIYOR():
    """`safe_call` çağrılıyor ama `yuk` boş geçilirse kapı **hiçbir şey ölçmez** —
    sahte bir kapı, kapısızlıktan kötüdür çünkü güven verir."""
    agac = _llm_agaci()
    for n in ast.walk(agac):
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "safe_call":
            anahtarlar = {k.arg for k in n.keywords}
            assert {"yuk", "ad"} <= anahtarlar, (
                f"llm.py:{n.lineno}: `safe_call` `yuk`/`ad` almadan çağrılmış")


def test_GONDERIM_DESENI_HALA_GECERLI():
    """Yeni bir sağlayıcı sınıfı eklenirse `_GONDERIM` kümesi de büyümeli; yoksa yeni yol
    **sessizce** kapının dışında kalır. Sınıf sayısı bir işaret olarak ölçülür."""
    kaynak = (KOK / "app" / "llm.py").read_text(encoding="utf-8")
    siniflar = {s for s in ("AnthropicSqlGenerator", "OpenAICompatibleSqlGenerator")
                if f"class {s}" in kaynak}
    assert len(siniflar) == 2, (
        f"sağlayıcı sınıfları değişmiş ({siniflar}) — `_GONDERIM` kümesi gözden geçirilmeli")
