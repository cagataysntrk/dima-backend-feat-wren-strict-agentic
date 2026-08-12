r"""🔴 `§G.2` — **BELGE DİZİNİ BAYATLAMAZ.**

## Neden bir kapı

Kullanıcının şikâyeti: *«`MIMARI.md` aşırı şişti, o yüzden kullanılamıyor.»*
Ölçüldü: **5.652 satır · 262 başlık** (h2 **16** · h3 **123**).

🆚 **Asıl sorun satır sayısı değil**: 5.652 satır bir mimari otorite için fazla değil,
**123 eşit görünen alt başlık** arasında aradığını bulamamak fazla. Çare **silmek**
olamaz — `MIMARI.md §10` *«kapananlar işaretlenir, silinmez»* der ve ㊿ *özeti korumak,
özetlediğini korumaz*: bir kararın gerekçesi kısaltılırsa altı ay sonra o karar
**yeniden tartışılır**.

Çare **gezinme**: `lab/belge_dizini.py` bölümleri satır numarasıyla listeler; okuyucu
123 eşit seçenek yerine **16 bölüm** arasından seçer.

## Ve bu kapı olmadan dizin bir YALANDIR

Elle bakılan bir dizin, belgenin **ilk düzenlemesinde** bayatlar ve *«burada yok»* diye
yanlış yönlendirir. 🆍 *Kendini temizlemeyen bir liste bir muafiyet değil bir perdedir.*

⚠ **Yazarken iki kez yanıldım, ikisi de buraya yazıldı:**
① Çapada `ı`→`i` çeviriyordum; GitHub `ı`'yı **korur** → ürettiğim bağlantı hiçbir yere
gitmezdi (görünür ama tıklanmaz bir dizin).
② ㉛ Dizin **kendini sayıyordu**: blok içindeki `## 🧭 DİZİN` başlığı bir bölüm sanılıyor,
her yazım satır numaralarını kaydırıyor ve dizin **hiçbir zaman** tazelenmiş sayılmıyordu.
"""

from __future__ import annotations

import pathlib
import sys

_KOK = pathlib.Path(__file__).resolve().parents[1]
if str(_KOK) not in sys.path:                          # pragma: no cover
    sys.path.insert(0, str(_KOK))


def test_OLCUM_TABANI_BELGE_VE_ISARETLER_YERINDE():
    """⊘ **Boş yeşil avı.** İşaretler yoksa aşağıdaki yüklem hiçbir şey ölçmez."""
    from lab.belge_dizini import BAS, BELGELER, SON

    for ad in BELGELER:
        metin = (_KOK / ad).read_text(encoding="utf-8")
        assert BAS in metin and SON in metin, (
            f"⊘ `{ad}` içinde dizin işaretleri (`{BAS}` / `{SON}`) yok — dizin "
            "yazılamaz.")


def test_DIZIN_TAZE():
    """🔴🔴 **ASIL KAPI.** Belgeye bir bölüm eklenir/silinir ya da satırlar kayarsa
    dizin **bayatlar** ve bu yüklem kırmızı olur.

    → Onarım tek komut: `python lab/belge_dizini.py --yaz`.

    *Bir dizinin bağlantısı da bir vaattir* 🆈 — tutulmuyorsa dizin, yokluğundan
    **kötüdür**: okuyan ona güvenir.
    """
    from lab.belge_dizini import kos

    bayat = [ad for ad, d in kos(yaz=False).items() if d["durum"] != "taze"]
    assert not bayat, (
        f"🔴 BELGE DİZİNİ BAYATLADI: {bayat}\n"
        "Belge değişti ama dizin güncellenmedi — satır numaraları artık başka yeri "
        "gösteriyor.\n→ `python lab/belge_dizini.py --yaz`")


def test_DIZIN_KENDINI_SAYMIYOR():
    """⚠ ㉛ **Yinelenme kapanı.** Blok içindeki `## 🧭 DİZİN` başlığı bir bölüm olarak
    sayılırsa üreteç **sabit noktaya oturmaz**: her yazım satırları kaydırır, kapı hep
    kırmızı kalır ve sonunda **atlanır**."""
    from lab.belge_dizini import uret

    blok = uret((_KOK / "MIMARI.md").read_text(encoding="utf-8"))
    assert "🧭 DİZİN" not in blok.split("| # |")[1], (
        "🔴 dizin KENDİ başlığını bölüm olarak listeliyor — üreteç yinelemeli.")


def test_SILME_YOK_BELGE_KISALMADI():
    """🔴 **`§G.2`'nin sınırı.** Bu iş bir **gezinme** işiydi; bir kısaltma işi **değil**.
    Belge dizinden **kısa** çıkarsa biri içerik silmiş demektir — ve `MIMARI.md §10`
    (*«kapananlar işaretlenir, silinmez»*) çiğnenmiş olur.

    ⊙ Taban **5.652** (dizinden önce ölçülen). Dizin kendisi ~26 satır eklediği için
    bugünkü sayı bunun üstünde olmalı; altına düşerse **silme** olmuştur.
    """
    n = len((_KOK / "MIMARI.md").read_text(encoding="utf-8").splitlines())
    assert n >= 5652, (
        f"🔴 `MIMARI.md` KISALDI: {n} satır (taban 5.652). `§G.2` bir gezinme işiydi, "
        "bir silme işi değil — `MIMARI.md §10`: «kapananlar işaretlenir, silinmez».")
