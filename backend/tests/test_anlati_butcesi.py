"""🔴 **SÜSÜN BÜTÇESİ** — canlı ölçüm: 2.936 / 22.564 / **69.399 ms**.

Aynı sağlayıcı (`deepseek-v4-flash`) aynı iş için 23 kat salındı. Ve anlatı bir
**süslemedir**: altındaki `summary` zaten yazılı ve doğru.

| tur | toplam | anlatı LLM | pay |
|---|---|---|---|
| *"makine bazında oee son 3 ay"* | 5.420 ms | 2.936 ms | %54 |
| *"aylara göre"* | 24.285 ms | 22.564 ms | %93 |
| *"çeyreklere böl"* | 🔴 **69.399 ms** | — | iki LLM çağrısı |

Aşılırsa anlatı **düşer**, cevap **düşmez** — `narration_guard`'ın kendi sözleşmesiyle
**aynı** en-kötü-durum: *"süssüz ama doğru"*.

⚠ Bütçe **çağırandadır**, sağlayıcıda değil: *"süs ne kadar bekletebilir"* bir **ürün
kararıdır**; sağlayıcıya koymak üç sağlayıcıda üç ayrı karar demekti.

*Bir süsün bütçesi, süslediği şeyin süresini aşamaz.*
"""

from __future__ import annotations

import inspect

from app import answer as answer_mod
from app.config import get_settings


def test_BUTCE_AYARLANABILIR_ve_MAKUL():
    s = get_settings()
    assert 0 < float(s.anlati_azami_saniye) <= 15, (
        "🔴 bütçe yok ya da süslemeye göre fazla geniş — ölçülen salınım 23 kat")


def test_BUTCE_ANLATI_CAGRISINA_UYGULANIYOR():
    """⟳ **ÇAPA TAŞINDI (`§33`) — silinmedi, GENİŞLETİLDİ.**

    Eski çapa `result(timeout=` metnini `_anlati_ekle`'nin içinde arıyordu ve **yeşildi**
    — oysa bütçe çalışmıyordu: `with ThreadPoolExecutor(...)` çıkışta `shutdown(wait=True)`
    çağırıyor, `result(timeout=)` beklemeyi keserken `with` onu geri koyuyordu. Canlı
    ölçüm: bütçe 8 sn, tur **81.656 ms**.

    ⊙ Yani kapı **doğru metni** arıyordu ve **yanlış şeyi** kanıtlıyordu. Uygulama
    `app/butce.py`'ye taşındı; çapa oraya çakıldı ve yanına **davranışsal** bir kapı
    kondu (`test_BUTCE_GERCEKTEN_BEKLEMEZ`) — metin değil, **süre** ölçen.

    *Bir metin çapası, metnin anlattığı davranışı kanıtlamaz; onu yalnız iddia eder.*
    """
    # ⚠ `rindex`: `"llm.anlat"` metni yukarıdaki **yorumda da** geçiyor (çapanın kendisi
    # orada anlatılıyor) ve `index` önce onu bulup gerçek çağrıyı kaçırıyordu.
    # *Bir kapı, aradığı metnin ilk değil DOĞRU örneğine bakmalı.*
    src = inspect.getsource(answer_mod._anlati_ekle)
    i = src.rindex('"llm.anlat"')
    yakin = src[max(0, i - 900):i + 900]
    assert "butce.kos" in yakin or "_butce.kos" in yakin, (
        "🔴 anlatı çağrısı bütçe sahibinden geçmiyor")
    assert "saniye=" in yakin, "🔴 çağrı bir zaman sınırı olmadan koşuyor"
    assert "ASIM" in yakin, "🔴 aşım dalı yok"


def test_ASIMDA_CEVAP_DUSMEZ():
    """🔴 En kötü durum *"süssüz ama doğru"* olmalı — asla *"cevapsız"*."""
    src = inspect.getsource(answer_mod._anlati_ekle)
    i = src.index("ASIM")
    blok = src[i:i + 500]
    assert "return" in blok and "raise" not in blok, (
        "🔴 aşım cevabı düşürüyor — anlatı bir süs, cevap değil")


def test_BUTCE_GERCEKTEN_BEKLEMEZ():
    """🔴 **KUSURU YAKALAYACAK OLAN KAPI — metin değil SÜRE ölçer.**

    Eski kapılar üçü de yeşildi ve bütçe **yine** çalışmıyordu, çünkü hepsi kaynağa
    bakıyordu. Bu kapı işi koşar ve **saate bakar**: bütçesi 0,3 sn olan bir çağrı
    3 sn'lik bir işi beklememelidir.
    """
    import time

    from app import butce

    basla = time.monotonic()
    sonuc = butce.kos([lambda: time.sleep(3) or "geç"], saniye=0.3, ad="test")
    gecen = time.monotonic() - basla
    assert sonuc[0] is butce.ASIM, "🔴 aşım işaretlenmedi"
    assert gecen < 1.5, (
        f"🔴 bütçe 0,3 sn'ydi, {gecen:.1f} sn beklendi — `with ThreadPoolExecutor` "
        f"çıkışta `shutdown(wait=True)` çağırıyor olabilir (`§33`'ün ta kendisi)")


def test_ASIM_NONE_DEGILDIR():
    """⚠ `None` **meşru bir sonuçtur** (model çekimser kalabilir); aşımla aynı değere
    çökerse çağıran *"bilmiyor"* ile *"geç kaldı"*yı ayırt edemez."""
    from app import butce
    assert butce.ASIM is not None
    assert butce.kos([lambda: None], saniye=5, ad="test") == [None]


def test_HICBIR_BUTCE_WITH_EXECUTOR_ICINDE_DEGIL():
    """🔴 **KUSUR SINIFININ KAPISI** — `§33`'ün kökü tek satırdı ve **iki yerde** vardı.

    `with ThreadPoolExecutor(...)` bloğunun içinde `result(timeout=…)` çağırmak, bütçeyi
    yazıp `__exit__`'te geri almaktır. Bu birleşim `app/` altında **hiçbir yerde**
    olmamalı; bütçenin tek evi `app/butce.py`'dir.
    """
    import pathlib as _pl
    import re as _re

    kok = _pl.Path(answer_mod.__file__).parent
    suclu = []
    for f in sorted(kok.rglob("*.py")):
        if f.name == "butce.py":
            continue
        g = f.read_text(encoding="utf-8")
        for m in _re.finditer(r"with\s+[\w.]*ThreadPoolExecutor\(", g):
            if "result(timeout=" in g[m.end():m.end() + 1200]:
                suclu.append(f"{f.relative_to(kok)}:{g[:m.start()].count(chr(10)) + 1}")
    assert not suclu, (
        "🔴 bütçe `with ThreadPoolExecutor` içinde uygulanıyor — çıkışta "
        f"`shutdown(wait=True)` onu iptal eder (`§33`): {suclu}")


def test_ISIN_ARKA_PLANDA_BITMESI_KAYITLI():
    """⚠ Thread öldürülemez: iş arka planda biter, ama cevabı **bekletmez**. Bu bir
    sınırdır ve yazılı olmalı — okuyan kişi *"sızıntı mı"* diye sormadan görsün."""
    src = inspect.getsource(answer_mod._anlati_ekle)
    assert "arka planda" in src and "öldürülemez" in src
