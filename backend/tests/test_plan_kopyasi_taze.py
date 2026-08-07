"""🔴 **PLAN REPODA VE TEK NÜSHA** — *"aynı kuralın iki sahibi"* sınıfının belge hâli.

## Ne değişti

Plan bir süre `~/.claude/plans/` altında, repo **dışında** durdu. İki ölçülmüş riski
vardı:

1. **Sürüm bağı yok** — kod bir commit'te ilerlerken plan başka bir zamandaydı; *"bu kod
   hangi plana göre yazıldı"* sorusu **sorulamıyordu**.
2. **Kopya = iki sahip** — bir süre iki nüsha vardı; kopya sessizce bayatlar ve bayat bir
   plan, olmayan bir plandan **daha kötüdür**: bağlamı sıfırlanan bir ajan onu okur,
   güvenir ve **yanlış fazdan** devam eder. Bu depoda o kusur `OPERASYON-DURUM.md`
   başlığında **iki kez** yaşandı.

> *İki gerçek, sıfır gerçekten kötüdür: sıfır gerçek arattırır, iki gerçek yanıltır.*

Plan repoya taşındı (`belgeler/plan/`); eski yol **silinmedi**, yönlendirmeye çevrildi.

## Bu kapı neyi tutar

* Plan repoda **var** ve boş değil.
* Dışarıda **rakip bir nüsha** kalmamış — kalmışsa o bir yönlendirme olmalı, belge değil.

*Bir taşımanın tamamlandığını, taşınan şeyin arkasında bir şey kalmadığı kanıtlar.*
"""

from __future__ import annotations

import pathlib

import pytest

_REPO = pathlib.Path(__file__).resolve().parents[2]
_PLAN = _REPO / "belgeler" / "plan"
_ESKI = pathlib.Path.home() / ".claude" / "plans"

#: ⚠ **KAPININ SINIRI YAZILI.** Test konteyneri yalnız `backend/`'i mount ediyor
#: (`-v .../backend:/app`), yani repo kökü **görünmez** ve `belgeler/plan/` yoktur.
#: O ortamda bu kapı `skip` eder — *var olmayan bir şeyin yokluğunu kusur saymak, kapıyı
#: sahte kırmızıya boğar.*
#:
#: 🔴 Bu bir eksik değil bir sınırdır ve `tsc` kapısıyla **aynı sınıftır**: ikisi de
#: geliştirici makinesinde gerçek, konteynerde sessiz. Kalıcı çözüm ikisinde de aynı:
#: koşum reçetesine repo kökünü mount etmek (`-v $REPO:/repo:ro`) ya da CI adımına
#: eklemek. Borç `OPERASYON-DURUM.md`'de.
pytestmark = pytest.mark.skipif(
    not _PLAN.is_dir(),
    reason="⊘ repo kökü mount edilmemiş (`belgeler/plan/` görünmüyor) — konteyner ortamı")

#: Taşınan belgeler. ⚠ Elle liste **bilinçli**: bu kapı *"plan repoda mı"* diye sorar,
#: *"dizinde ne varsa"* diye değil — yeni bir dosya eklendiğinde sessizce kapsam
#: genişlemesin.
_BELGELER = ("DIMA-GARSON-ARA-FAZ.md", "DIMA-V1-YOL-HARITASI.md")

#: Bir dosyanın **yönlendirme** mi belge mi olduğunun ölçütü: yönlendirme kısadır ve
#: hedefi yazar. Boyutla ayırmak kırılgandı; **içerik** ölçütü kullanılır.
_YONLENDIRME_IZI = "belgeler/plan/"


def test_PLAN_REPODA_ve_DOLU():
    """🔴 Plan repoda olmalı: repo dışındaki bir plan, kodla **aynı tarihte** olduğunu
    kanıtlayamaz."""
    eksik = [ad for ad in _BELGELER if not (_PLAN / ad).exists()]
    assert not eksik, (
        f"🔴 plan repoda YOK: {eksik}. Repo dışındaki bir plan, hangi koda ait olduğunu "
        "söyleyemez — `git log belgeler/plan/` o soruyu cevaplayan tek şeydir.")
    bos = [ad for ad in _BELGELER if len((_PLAN / ad).read_text(encoding="utf-8")) < 1000]
    assert not bos, f"🔴 plan dosyası boş/kırpılmış: {bos}"


def test_DISARIDA_RAKIP_NUSHA_YOK():
    """🔴 **Taşımanın tamamlandığının kanıtı.**

    Eski yolda bir dosya kalmışsa **yönlendirme** olmalı, belge değil. İkinci bir nüsha,
    kaynak ilerleyince **sessizce** bayatlar ve o zaman iki gerçek olur.

    ⚠ Eski yol **erişilemiyorsa** (konteyner/CI) test atlanır — ve bu bir eksik değil bir
    **sınırdır**: orada zaten rakip nüsha olamaz.
    """
    if not _ESKI.is_dir():
        pytest.skip("⊘ eski yol yok — taşıma tamamlanmış ya da farklı ortam")

    rakip: list[str] = []
    for ad in _BELGELER:
        eski = _ESKI / ad
        if not eski.exists():
            continue                      # tamamen kaldırılmış — sorun yok
        metin = eski.read_text(encoding="utf-8")
        if _YONLENDIRME_IZI not in metin or len(metin) > 4000:
            rakip.append(f"{ad} ({len(metin.splitlines())} satır)")
    assert not rakip, (
        "🔴 ESKİ YOLDA RAKİP NÜSHA VAR:\n  " + "\n  ".join(rakip)
        + f"\n\nO dosyalar ya kaldırılmalı ya `{_YONLENDIRME_IZI}`'a işaret eden bir "
          "YÖNLENDİRMEYE çevrilmeli. İki nüsha = iki sahip; kopya sessizce bayatlar.")


def test_CANLI_ATIFLAR_REPOYU_GOSTERIYOR():
    """Bir belge taşındıysa **onu okuyanlar** da taşınmalı — yoksa taşıma yarımdır ve
    okuyan eski yolda boşluk bulur.

    ⚠ Tarihsel belgeler (`belgeler/denetim/*` · `belgeler/devir/*`) **kapsam dışı**:
    onlar bir günün fotoğrafıdır ve o gün belge gerçekten oradaydı. *Geçmişi bugünkü yola
    göre düzeltmek, kaydı yanlış yapar.*
    """
    canli = {
        "backend/CLAUDE.md": "belgeler/plan/DIMA-V1-YOL-HARITASI.md",
        "OPERASYON.md": "belgeler/plan/DIMA-V1-YOL-HARITASI.md",
        "OPERASYON-DENETIM.md": "belgeler/plan/DIMA-V1-YOL-HARITASI.md",
    }
    eksik = []
    for yol, beklenen in canli.items():
        p = _REPO / yol
        if not p.exists():
            continue
        if beklenen not in p.read_text(encoding="utf-8"):
            eksik.append(yol)
    assert not eksik, (
        f"🔴 bu belgeler hâlâ eski yolu gösteriyor: {eksik} — taşıma yarım kaldı")
