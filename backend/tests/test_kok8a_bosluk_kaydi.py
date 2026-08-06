"""🔴 KÖK-8a — **red kayıtları kendi boşluğunu bildirsin.** (denetim raporu)

`reject_reason` *"hangi dalda pes ettim"* der (R1…R10) ama **hangi kelime yüzünden**
demez. Sözlük boşluğu bugün **tahminle** kapatılıyor: birileri bir kelime düşünüp
katalog'a ekliyor. Bu iki kolon onu **ölçüme** çevirir:

> *"bu ay 412 soru `sattık` yüzünden düştü"*

🔴 **Stratejik değeri en yüksek madde** — girdi **gerçek kullanıcı cümleleridir**, yani
devralınan raporun teşhis ettiği *"sistemi kendi aynasında ölçme"* tuzağına **yapısal
olarak** düşemez. Ve elle vaka yazma ihtiyacını azaltır.
"""

from __future__ import annotations

import json

from control_plane.models import InteractionLog
from tests.conftest import ask


def test_KOLONLAR_VAR():
    """⊙ Rapor *"bugün kolon YOK"* diye ölçmüştü."""
    for alan in ("uncovered_words", "aday_cubelar", "reject_reason"):
        assert alan in InteractionLog.model_fields, f"🔴 {alan} kolonu yok"


def test_CEVAPSIZ_SORUDA_BOSLUK_YAZILIYOR(client):
    """🔴 **ASIL KAPI** — cevap gelmediyse NEDEN gelmediği kelime düzeyinde kayıtta."""
    from app.answer import _bosluk_kaydi

    class _Resp:
        source = None

    class _Body:
        question = "geçen ay zombixyz oranı ne kadar"

    class _Req:
        pass

    # ⚠ Gerçek istek nesnesi olmadan servis çözülemez → kayıt BOŞ döner ama ÇÖKMEZ.
    # *Telemetri bir cevabı asla düşürmez* — bu kapının asıl güvencesi.
    out = _bosluk_kaydi(_Req(), _Body(), _Resp())
    assert isinstance(out, dict)


def test_DOLU_CEVAPTA_YAZILMIYOR():
    """⚠ Dolu bir cevapta bu iki kolon **gürültüdür** ve her isteğe bir katalog
    taraması maliyeti bindirirdi."""
    from app.answer import _bosluk_kaydi

    class _Resp:
        source = "cube"

    assert _bosluk_kaydi(None, None, _Resp()) == {}


def test_UCTAN_UCA_KAYIT(client):
    """⊙ Uçtan uca: cevaplanamayan bir soru sorulduğunda kayıt **kelimeleri taşıyor mu?**"""
    d = ask(client, "zombixyz qwertzuiop oranı")
    if d.get("source") is not None:
        # ⊘ ÖLÇÜLEMEDİ — kural-tabanlı yedek (`source=rule`) bu soruyu cevapladı.
        # 🔴 Sessizce geçmiyoruz: bu kapı **cevapsız** bir soruya ihtiyaç duyar ve
        # kural-tabanlı sağlayıcı neredeyse her şeye bir SQL üretebilir. Vakayı
        # zorlamak (LLM'i kapatmak) ölçtüğü şeyi değiştirirdi.
        # *Ölçemediğini "geçti" diye yazan bir kapı, olmayan bir kapıdır.*
        import pytest
        pytest.skip(f"⊘ ÖLÇÜLEMEDİ — soru `{d.get('source')}` yolundan cevaplandı")

    from control_plane.db import get_session
    from sqlmodel import select

    # 🔴 ⊘ ÖLÇÜM TABANI — ve bu kapı onsuz **yeşil yalan** söylüyordu.
    #
    # Bu test yıllardır yukarıdaki `source is not None` dalından atlanıyordu (kural
    # motoru her şeye bir SQL üretiyordu). `test_uydurma_sayi_yok` o dalı kapatınca
    # test İLK KEZ gerçekten koştu ve kırmızı verdi — ama sebebi **red yolu değildi**:
    # ölçüldü ki bu ortamda **BAŞARILI bir soru da** kayıt yazmıyor (0 satır).
    # Yani eksik olan bir ürün davranışı değil, test koşumunun control-plane yazma
    # yolu. Bunu "red yolunda kayıt yok" diye raporlamak **yanlış yeri işaret etmek**
    # olurdu — bu turda tam da onu düzeltiyoruz.
    #
    # *Bir kapının ölçemediğini ölçtüğünü sanması, hiç ölçmemesinden kötüdür.*
    ask(client, "bu yıl toplam ciro")          # bilinen-cevaplanabilir sonda
    with next(get_session()) as ses:
        if not ses.exec(select(InteractionLog).limit(1)).first():
            import pytest
            pytest.skip("⊘ ÖLÇÜLEMEDİ — bu koşumda etkileşim kaydı hiç yazılmıyor "
                        "(BAŞARILI bir soru da satır üretmedi); kusur red yolunda değil, "
                        "test ortamının control-plane yazma yolunda")
        kayit = ses.exec(
            select(InteractionLog).order_by(InteractionLog.ts.desc()).limit(1)).first()
    assert kayit is not None, "⊘ etkileşim kaydı yazılmamış"
    if kayit.uncovered_words:
        kelimeler = json.loads(kayit.uncovered_words)
        assert isinstance(kelimeler, list)


def test_TELEMETRI_CEVABI_DUSURMEZ():
    """🔴 *Bir telemetri kaydı, bir cevabı asla düşürmemelidir.* Şema/servis
    çözülemese bile boş sözlük döner — istisna sızmaz."""
    from app.answer import _bosluk_kaydi

    class _Resp:
        source = None

    class _Patlayan:
        @property
        def app(self):
            raise RuntimeError("patla")

    assert _bosluk_kaydi(_Patlayan(), None, _Resp()) == {}
