"""§G/AJ0 — **örnek #1: yazım önerisi cevaplı yolu KESEMEZ.**

## Ölçülen kusur

Kullanıcı *"bu yıl fire ne kadar arttı"* yazdı — **doğru yazılmış** bir soru. Sistem
*«arttı» yerine «parti» mi demek istedin?* dedi ve **`source=None` ile döndü**, yani
cevap üretebilecek yolun (`route` sonrası merdiven) önünü **kesti**.

Ölçüldü (12 gerçekçi soru, 2026-08-04): **5'i** bu dalda ölüyordu ve önerilerin hepsi
saçmaydı — hepsi sıradan Türkçe **fiil**in katalog **ismine** benzetilmesiydi:

| yazılan | önerilen |
|---|---|
| `arttı` | `parti` |
| `veren` | `renk` |
| `işledik` | `iplik` |
| `sattık` | `hattı` |

🔴 **Kök neden:** bir kelimenin **katalogda olmaması**, onun yazım hatası olduğunun kanıtı
**değildir** — bir cümledeki kelimelerin çoğu zaten katalog dışıdır (fiiller, edatlar,
gündelik dil). Bulanık eşleştirici bunu bilmiyor, her bilinmeyen kelimeyi bir *"hata"*
sanıyordu.

## Düzeltme

Öneri **uygulanınca soru gerçekten cevaplanabilir hâle geliyor mu?** `route()` sıfır-LLM
ve deterministik; cevap **açmıyorsa** öneri gürültüdür ve **bastırılır**. Kullanıcıyı
cevapsız bir soruya ikinci kez çarptıran bir chip, chip olmamasından **kötüdür** — aynı
disiplin `olcu_netlestirme`'de de yazılı.

⚠ **Bu AJ0'ın TAMAMI DEĞİL, birinci örneğidir.** AJ0 ayrıca MIMARI §5'e **18. yasağı** ve
`explain.path`'in bir **merdiven izine** çevrilmesini istiyor. `§5-18.yasak` tuzağı bu
yüzden **⟳ olarak duruyor** — ve doğru duruyor.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]


def test_ONERI_ROUTE_ILE_DOGRULANIYOR():
    """🔴 **Ölçüm YAPISAL.** Bu oturumda metin taraması üç kez kendi yorumunu yakaladı;
    burada AST ile soruluyor: `typo_suggestion` doğrulanmış bir çağrıdan mı geliyor?

    ⟳ **KONUM DEĞİŞTİ (2026-08-04):** karar `ask()` içindeyken `0.21`'in modül büyüme
    kapısı tavanı aştığını gösterdi ve kendi talimatını uygulattı — *"yeni davranışı
    MODÜLE ÇIKAR, tavanı yükseltme."* Mantık `app/typo_onerisi.py`'de; `ask()` yalnız
    çağırıyor ve **hiç büyümedi** (kod satırı 1147, boşluk 0). Kapı güncellendi, silinmedi.
    """
    agac = ast.parse((KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8"))
    atamalar = [n for n in ast.walk(agac)
                if isinstance(n, ast.Assign)
                and any(getattr(t, "id", "") == "typo_suggestion" for t in n.targets)]
    assert atamalar, "`typo_suggestion` ataması YOK — dal silinmiş olabilir"
    dogrulanmis = [
        n for n in atamalar
        if any(isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "gecerli_oneri"
               for c in ast.walk(n))
        or isinstance(n.value, ast.IfExp)
    ]
    assert dogrulanmis, (
        "🔴 `typo_suggestion` DOĞRULANMADAN atanıyor: öneri, cevabı açıp açmadığına "
        "bakılmadan sunuluyor. Ölçüldü — 12 gerçekçi sorunun 5'i bu dalda ölüyordu.")


def test_DOGRULAMA_SIFIR_LLM():
    """Doğrulama `route()` ile yapılır: **sıfır-LLM ve deterministik**. Bir öneriyi
    doğrulamak için LLM çağırmak, gürültüyü **paralı** hâle getirirdi."""
    kaynak = (KOK / "app" / "typo_onerisi.py").read_text(encoding="utf-8")
    i = kaynak.index("def cevap_aciyor_mu")
    govde = kaynak[i:]
    assert "cube_router.route(" in govde, "doğrulama `route()` ile yapılmıyor"
    assert "llm" not in govde.lower().split('"""')[-1], \
        "doğrulama LLM'e gidiyor — gürültü paralı olurdu"


def test_DOGRULAMA_HATASI_ONERIYI_BASTIRIYOR():
    """`route()` patlarsa öneri **sunulmaz** (fail-closed): doğrulanamayan bir öneri,
    doğrulanmamış bir öneridir."""
    from app import typo_onerisi

    class _Patlak(dict):
        def get(self, *a, **k):
            raise RuntimeError("şema okunamadı")

    assert typo_onerisi.cevap_aciyor_mu({"corrected_q": "bu yıl ciro"}, _Patlak()) is False
    assert typo_onerisi.cevap_aciyor_mu(None, {}) is False
    assert typo_onerisi.gecerli_oneri([], {}) is None


def test_BANTLAR_AYRIK_DEGIL_olculdu():
    """🔴 **BİR İDDİA ÖLÇÜLDÜ VE ÇÜRÜTÜLDÜ — ve bu test onu DONDURUYOR.**

    Düzeltmeyi öneren tur *"gerçek hatalar **0,833–0,909**, saçmalar **0,667**; bantlar
    **ayrık**, eşik (`_TYPO_MID = 0,65`) tam ortalarına düşmüş"* dedi ve buradan
    *"eşiği yükselt"* sonucu çıkıyordu.

    Bağımsız ölçüm (daha geniş örneklem, 2026-08-04) bunu **çürüttü**:

    | küme | aralık |
    |---|---|
    | saçma (fiil→isim) | 0,600 – **0,769** |
    | gerçek yazım hatası | **0,714** – 0,923 |

    **ÇAKIŞIYORLAR.** Yani tek başına bir eşik bu ikisini **ayıramaz**; eşiği yükseltmek
    bir hatayı ötekiyle **takas** ederdi (`fıre→fire` 0,750 ve `musteri→müşteri` 0,714
    kaybedilirdi — ikisi de **gerçek** hata).

    Bu test bir **düzeltme** değil, bir **kilit**: sayılar kayarsa ya da biri eşiği bu
    çürütülmüş gerekçeyle değiştirirse kırılır. *Çürütülmüş bir gerekçe, yazılı değilse
    tekrar edilir.*
    """
    from difflib import SequenceMatcher

    def oran(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    sacma = [oran(*p) for p in
             (("arttı", "parti"), ("veren", "renk"), ("isledik", "iplik"),
              ("sattık", "hattı"), ("degisti", "egitim"))]
    gercek = [oran(*p) for p in
              (("makinalar", "makineler"), ("cirosu", "ciro"), ("fıre", "fire"),
               ("bakiyye", "bakiye"), ("musteri", "müşteri"))]
    assert max(sacma) > min(gercek), (
        f"bantlar artık AYRIK görünüyor (saçma≤{max(sacma):.3f} < gerçek≥{min(gercek):.3f}) "
        "— örneklem değiştiyse ölçüm YENİLENMELİ; eşik kararı buna dayanacak.")


@pytest.mark.xfail(strict=True, reason=(
    "🔴 AÇIK KUSUR — ölçüldü, düzeltilmedi, GÖRÜNÜR bırakıldı. Öneri artık `route()` ile "
    "doğrulanıyor ama saçma düzeltme de route ediyor: 'bu ay kaç parti işledik' → "
    "'…parti iplik' katalog terimlerinden oluştuğu için ÇÖZÜLÜYOR. Ayırıcı sinyal "
    "benzerlik ORANI DEĞİL (bantlar çakışıyor, bkz. test_BANTLAR_AYRIK_DEGIL_olculdu); "
    "gerçek sinyal Türkçe FİİL ÇEKİMİ — saçmaların hepsi fiil→isim. O iş §G/AJ0'ın "
    "morfoloji kalemine ait ve kanıtlanmamış bir eşik değişikliğiyle sevk edilmedi."))
@pytest.mark.parametrize("soru", [
    "bu yıl fire ne kadar arttı",
    "en çok fire veren makine",
    "bu ay kaç parti işledik",
])
def test_DOGRU_YAZILMIS_SORU_ONERIYLE_KESILMIYOR(client, soru):
    """🔴 **Uçtan uca hedef — bugün HENÜZ tutmuyor ve bu bilinçle kayıtlı.**

    Bunlar **doğru yazılmış** sorular; hiçbiri bir *"… mi demek istedin?"* chip'iyle
    kesilmemeli. `xfail(strict=True)`: düzeldiği gün bu test **kırılır** ve işareti
    kaldırmaya zorlar — bir kapı geri alınmaz, `xfail` işaretlenir (`GERİ AL` kuralı).
    """
    d = client.post("/ask", json={"question": soru, "execute": False}).json()
    not_metni = str(d.get("note") or "")
    assert "demek istedin" not in not_metni, (
        f"{soru!r} bir yazım önerisiyle kesildi: {not_metni!r}\n"
        "Doğru yazılmış bir soruya yazım hatası demek, kullanıcının güvenini "
        "cevapsızlıktan daha hızlı kaybettirir.")
