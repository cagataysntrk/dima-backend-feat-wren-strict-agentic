"""FAZ 1.9 — **NUMERIC FIDELITY: zorlama mekanizması.**

## 🔴 Yol haritasının saydığı üç yüzey BUGÜN YOK — ve bu ölçüldü

Madde *"`izinli_degerler()` yeni türevleri kapsar (MASE · kırılma-noktası % · karar
rozeti %)"* diyor. Ölçüldü (2026-08-04): **üçü de kodda yok** —
`grep -rn "MASE\\|kırılma\\|karar_rozet" app/` → **0 isabet** (yalnız alakasız
*"kırılmaz"* geçişleri). Olmayan metrikler için türetme eklemek, bu deponun avladığı
*"beyan var, karşılığı yok"* sınıfının **kendisi** olurdu: kapı genişler, koruduğu bir şey
olmaz, ve genişlemenin doğru olup olmadığı **hiç ölçülemez**.

→ Bu turda inen şey maddenin **kalıcı** yarısı: **zorlama mekanizması**. Yüzeyler
doğduğunda `ek=` ile beyan edilecekler; kapı onları o gün **zorlayacak**.

## Ne indi

1. `narration_guard.dogrula` **araç kaydına girdi** (`makbuz=None`, **kapıdır**).
2. Bu dosya, anlatı üreten **her** yolun guard'dan geçtiğini **kaynak taramasıyla**
   doğrular — kayıtsız bir anlatı üreticisi eklenirse **kırmızı**.

## ⚠ KD-21 SINIRI — ve neden burada yazılı

Guard **rakamsız** bir cümlede **yetkisizdir**: doğrulayacak sayı yoksa cümle geçer.
Yeni anlatı yüzeyleri **sayı taşıyan** cümleler üretmelidir, yoksa kapı onları **görmez**
ve *"guard'dan geçti"* cümlesi **karşılıksız** kalır.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]
APP = KOK / "app"


def _kaynak(ad: str) -> str:
    return (APP / ad).read_text(encoding="utf-8")


# ── 1 · GUARD ARAÇ KAYDINDA ─────────────────────────────────────────────────

def test_GUARD_ARAC_KAYDINDA():
    """🔴 Kayıtta **görünmeyen** bir kapı, planlayıcının **bilmediği** bir kapıdır. Yeni
    bir anlatı yüzeyi eklendiğinde onu atlamak bir *"unutma"* değil, *"kaydın söylemediği
    bir şeyi bilmemek"* olur."""
    from app import tools

    adlar = {a.ad for a in tools.hepsi()}
    assert "narration_guard.dogrula" in adlar, "guard araç kaydında YOK"


def test_GUARD_MAKBUZSUZ_ve_BU_BIR_BEYAN():
    """`makbuz=None` bir **eksiklik değil bir BEYANDIR**: bu araç veriye dokunmaz,
    eldeki metni okur (`interpret` ile aynı sınıf)."""
    from app import tools

    g = next(a for a in tools.hepsi() if a.ad == "narration_guard.dogrula")
    assert g.makbuz is None
    assert g.determinizm == "deterministik" and g.maliyet == "sifir"
    assert g.yan_etki == "yok"


def test_GUARD_KAYDI_KD21_SINIRINI_YAZIYOR():
    """⚠ Guard **rakamsız** cümlede yetkisizdir. Bu sınır kayıtta yazılı olmazsa, yeni bir
    yüzey *"guard'dan geçiyorum"* der ve **hiçbir şey doğrulanmaz**."""
    from app import tools

    g = next(a for a in tools.hepsi() if a.ad == "narration_guard.dogrula")
    assert "KD-21" in g.notlar and "RAKAMSIZ" in g.notlar


# ── 2 · 🔴 ANLATI ÜRETEN HER YOL GUARD'DAN GEÇİYOR ──────────────────────────

def _anlati_ureticileri() -> list[str]:
    """LLM'de **düz metin** üreten yöntemler — SQL/cube/seçim üretenler hariç.

    `test_beyanlar_curumesin.py::test_ANLATIM_DOGRULAYICI_GERCEKTEN_DEVREDE` ile **aynı
    tanım** kullanılır; ikinci bir üretici listesi yazmak, iki kapının zamanla ayrışması
    demekti (biri yeni yüzeyi görür, öteki görmez).
    """
    import re

    llm = _kaynak("llm.py")
    uretenler = set(re.findall(r"def (generate_\w+|\w*_?(?:narrate|anlat|prose)\w*)\(", llm))
    return sorted(a for a in uretenler
                  if not any(x in a for x in ("sql", "cube", "select", "refine", "repair")))


def test_ANLATI_URETICISI_VAR():
    """Ön koşul: üretici yoksa bu dosyanın ölçtüğü şey de yoktur."""
    assert _anlati_ureticileri(), (
        "llm.py'de düz metin üreten yöntem KALMADI — T2 anlatıcı geri mi alındı? "
        "O hâlde bu kapının kapsamı yeniden okunmalı.")


def test_HER_ANLATI_YOLU_GUARDDAN_GECIYOR():
    """🔴 **Maddenin kalbi — ve ölçüm YAPISAL.**

    `answer.py::_anlati_ekle` içinde LLM çağrısı ile `narration["..."]` ataması **arasında**
    `guvenli_anlatim` bulunmalı. Kapısız bir yol, ötekilerin hepsini anlamsız kılar.
    """
    agac = ast.parse(_kaynak("answer.py"))
    fn = next((n for n in ast.walk(agac)
               if isinstance(n, ast.FunctionDef) and n.name == "_anlati_ekle"), None)
    assert fn is not None, "`_anlati_ekle` YOK — anlatı yolu taşınmışsa kapı GÜNCELLENMELİ"
    cagrilar = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
    assert any(getattr(c.func, "id", "") == "guvenli_anlatim" for c in cagrilar), \
        "anlatı yolu guard'ı ÇAĞIRMIYOR — uydurma sayı yüzeyi korumasız"


def test_KAYITSIZ_ANLATI_URETICISI_KAYNAK_TARAMASINDA_GORUNUR():
    """Yeni bir anlatı üreticisi `app/` içinde **guard'sız** bir yayım yolu açarsa
    görünür olmalı. Ölçüm: `narration`/`anlati` alanına **atama** yapan her modül,
    `narration_guard`'ı da anmalı.
    """
    ihlaller: list[str] = []
    for yol in sorted(APP.rglob("*.py")):
        if yol.name in ("narration_guard.py", "llm.py"):
            continue
        metin = yol.read_text(encoding="utf-8", errors="ignore")
        yazar = '["narration"] =' in metin or '["anlati"] =' in metin
        if yazar and "narration_guard" not in metin and "guvenli_anlatim" not in metin:
            ihlaller.append(str(yol.relative_to(KOK)))
    assert not ihlaller, (
        f"🔴 GUARD'SIZ anlatı yayımı: {ihlaller}\n"
        "Kapısız bir yol, ötekilerin hepsini anlamsız kılar — uydurma bir sayı oradan "
        "sızar ve `source=cube` rozetiyle sunulur.")


# ── 3 · TÜRETME LİSTESİ KAPALI KALIYOR ──────────────────────────────────────

def test_TURETME_LISTESI_KAPALI():
    """🔴 *"Her aritmetik kombinasyon"* serbest bırakılsaydı **yeterince sayıyla her şey
    türetilebilirdi** ve kapı hiçbir şeyi engellemezdi. Yeni türetmeler `ek=` ile
    **beyan edilir**; kapalı liste genişletilmez."""
    from app.narration_guard import izinli_degerler

    import inspect

    assert "ek" in inspect.signature(izinli_degerler).parameters, \
        "beyan kanalı kaldırılmış — yeni yüzeyler kapalı listeyi ZORLAR"
    kaynak = _kaynak("narration_guard.py")
    assert "KAPALIDIR" in kaynak, "türetme listesinin kapalı olduğu beyanı silinmiş"


def test_EK_KANALI_UCTAN_UCA_CALISIYOR():
    """Beyan kanalı **işe yaramalı**: beyan edilen bir değer doğrulamayı geçmeli,
    edilmeyen geçmemeli. Aksi hâlde *"yeni yüzeyler beyan etsin"* boş bir tavsiyedir.

    ⚠ **Kanal iki adla anılıyor** ve bu ölçüldü: `izinli_degerler(..., ek=)` ·
    `dogrula(..., ek_degerler=)`. İkisi **aynı** kavram. Yeniden adlandırmak ölçülmüş bir
    kazanç getirmiyor (churn), ama farkın **yazılı olmaması** bir sonraki turda yanlış adı
    kullandırır — nitekim bu test ilk yazımda tam olarak ona takıldı.

    🔴 Ve kanal **uçtan uca** sınanır (`guvenli_anlatim` → `dogrula`): yalnız iç fonksiyonu
    test etmek, dışa açık yolun kanalı **geçirdiğini** kanıtlamazdı.
    """
    from app.narration_guard import dogrula, guvenli_anlatim

    result = {"columns": ["ciro"], "rows": [{"ciro": 100.0}], "row_count": 1}
    assert not dogrula("MASE 0.42 çıktı.", result).gecti
    assert dogrula("MASE 0.42 çıktı.", result, ek_degerler=[0.42]).gecti
    metin, _r = guvenli_anlatim("MASE 0.42 çıktı.", result, ek_degerler=[0.42])
    assert "0.42" in metin, "beyan kanalı DIŞA AÇIK yoldan geçmiyor"


# ── 4 · ⚠ KD-21 SINIRI ÖLÇÜLÜYOR ───────────────────────────────────────────

def test_RAKAMSIZ_CUMLE_GUARDDAN_GECER():
    """⚠ **Guard rakamsız cümlede YETKİSİZDİR** — doğrulayacak sayı yoktur.

    Bu bir kusur değil bir **sınırdır** ve yazılı olması şart: yeni bir yüzey rakamsız
    cümleler üretirse *"guard'dan geçti"* cümlesi **karşılıksız** kalır ve kimse fark
    etmez.
    """
    from app.narration_guard import dogrula

    result = {"columns": ["ciro"], "rows": [{"ciro": 100.0}], "row_count": 1}
    r = dogrula("Satışlar genel olarak iyi görünüyor.", result)
    assert r.gecti, "rakamsız cümle reddedildi — guard kapsamı dışına taşmış"


def test_KD21_SINIRI_BELGEDE():
    """Bir sınır, yazılı değilse bir sonraki tur onu **yok** sanar."""
    kaynak = (KOK / "tests" / "test_numeric_fidelity.py").read_text(encoding="utf-8")
    assert "KD-21" in kaynak and "yetkisiz" in kaynak.lower()


# ── 5 · YOL HARİTASININ ÜÇ YÜZEYİ: BUGÜN YOK (ölçüm dondu) ──────────────────

@pytest.mark.parametrize("yuzey,desen", [
    ("MASE", "MASE"),
    ("kırılma-noktası %", "kirilma_noktasi"),
    ("karar rozeti %", "karar_rozeti"),
])
def test_UC_YUZEY_HENUZ_YOK_olculdu(yuzey, desen):
    """🔴 **Ölçüm donduruluyor.** Madde *"`izinli_degerler()` bu üç türevi kapsar"* diyor;
    üçü de **bugün kodda yok**. Olmayan metrikler için türetme eklemek *"beyan var,
    karşılığı yok"* olurdu: kapı genişler, koruduğu bir şey olmaz, genişlemenin doğru
    olup olmadığı **hiç ölçülemez**.

    Yüzey doğduğu gün bu test **kırılır** ve `ek=` ile beyan edilmesini zorlar —
    ⟳ tuzak deseninin aynısı: *bir gerçek bayatladığında CI kırılır.*
    """
    var = any(desen.lower() in y.read_text(encoding="utf-8", errors="ignore").lower()
              for y in APP.rglob("*.py"))
    assert not var, (
        f"🎉 `{yuzey}` yüzeyi İNDİ — şimdi yapılacak: ürettiği sayıları "
        "`narration_guard.dogrula(..., ek=[...])` ile BEYAN ET ve bu satırı tuzaktan "
        "kapıya çevir (silme). ⚠ Ve cümleler SAYI TAŞIMALI, yoksa guard onları görmez.")
