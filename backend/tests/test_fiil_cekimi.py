"""🔴🔴 `§FÇ` — **FİİL ÇEKİMİ: ad çekimi zinciri bu soruyu CEVAPLAYAMAZ.**

## Ölçülen kusur (süit, 2026-08-10)

    niyet_kalibi_var("bu grafiği yorumla")     → 'anlat'   ✅
    niyet_kalibi_var("bunu nasıl yorumlarsın") →  None     🔴

`yorumla` bir **fiil kökü**; `yorumlarsın` = `yorumla` + `-r` + `-sın`. `_syn_hit`'in
zinciri (`_SUFFIX_ATOMS`) **ad** çekimini doğrular — kişi eki orada yoktur **ve
olmamalıdır**: katalog terimleri isimdir, isimler kişiye göre çekilmez.

🔴 Bedeli `R2` sınıfı: tanınmayan bir niyet, sosyal kapıda bir **kapanış** sanılabilir
→ *«Görüşürüz!»*. En üst kuralın (*«anlamadım YOK»*) doğrudan ihlali.

## Ve tablo kanıtı kendi içinde taşıyordu

    _ANLAT = (…, "yorumla", "yorumlar misin", "yorumlasana", "aciklar misin", "acikla")
                   └─ dört giriş, İKİ fiilin ELLE YAZILMIŞ çekimi ─┘

*Bir dilbilgisi kuralını tamamlamak, bir sözlüğe kelime eklemekten farklıdır: birincisi
bir kez yazılır ve bütün fiiller için çalışır.*
"""

import pytest

from app.cube_router import _norm
from app.followup import _fiil_hit, niyet_kalibi_var


@pytest.mark.parametrize("soru", [
    "bunu nasıl yorumlarsın",          # geniş zaman + 2. tekil  ← ÖLÇÜLEN kusur
    "bunu yorumlayabilir misin",       # yeterlilik + soru
    "şunu açıklarsın",                 # ünlüyle biten kök + rsin
    "bunu değerlendirirsin",           # ünsüzle biten kök + irsin
    "yorumlasana",                     # rica kipi
])
def test_CEKIMLI_FIIL_NIYET_OLARAK_TANINIR(soru):
    """🔴 Beşi de `TUR_ANLAT`'ın **zaten tanıdığı** bir fiilin çekimidir; sistem cevabı
    biliyordu ve kendi bilgisini kendi susturuyordu."""
    assert niyet_kalibi_var(_norm(soru)) == "anlat", soru


def test_EMIR_KIPI_HALA_CALISIR():
    """⚠ Zincir bir **ekleme**dir: var olan eşleşmeler aynen durur (`KURAL B`'nin ruhu)."""
    assert niyet_kalibi_var(_norm("bu grafiği yorumla")) == "anlat"
    assert niyet_kalibi_var(_norm("neden düştü")) == "neden"


# ── 🔴🔴 KAPININ KENDİ RİSKİ — `§101.1` ───────────────────────────────────────

@pytest.mark.parametrize("soru,kok", [
    ("aciklama tablosu", "acikla"),        # -ma: **ad** türetimi, fiil çekimi DEĞİL
    ("degerlendirme formu", "degerlendir"),
    ("yorum sayisi", "yorumla"),
    ("acik bakiye", "acikla"),
    ("toplam ciro", "yorumla"),
])
def test_FIIL_ZINCIRI_AD_TURETIMINI_YUTMAZ(soru, kok):
    """🔴 Zincir **yalnız fiil çekimini** tanır. `-ma`/`-me` bir ad türetimidir
    (*«açıklama»* bir isimdir) ve bu zincire **girmez**.

    ⚠ Ölçüm kaydı: `aciklama tablosu` ve `degerlendirme formu` `niyet_kalibi_var`'da
    zaten `anlat` dönüyordu — ama sebebi `_syn_hit` (ad zinciri), **bu zincir değil**.
    Ayrım önemli: bir kusuru miras almakla üretmek aynı şey değildir, ve bu satır
    ikincisini yasaklıyor.
    """
    assert _fiil_hit(_norm(soru), kok) is False, f"{soru} ← {kok}"


def test_COK_KELIMELI_KALIP_CEKILMEZ():
    """*«analiz et»* iki kelimedir; bir fiil kökü gibi çekilemez — `_syn_hit` onu olduğu
    gibi arar ve bu zincir ona **hiç dokunmaz**."""
    assert _fiil_hit(_norm("analiz etmelisin"), "analiz et") is False


def test_CIPLAK_R_EKI_ATOM_DEGILDIR():
    """🔴🔴 **Deponun kendi ölçülmüş dersi** (`cube_router` `§73`): *«tek harflik ünsüz
    atomlar neredeyse HER harf dizisini geçerli bir ek zinciri yapıyordu»* — `s` yüzünden
    `karsilastir` *«kâr»* okunmuştu.

    Bu yüzden ekler **bileşiktir** (`rsin`·`irsin`), tek harf değil. Bu satır çıplak bir
    `r`'nin sonradan eklenmesini yasaklar. *Bir ekin kısalığı, onun tehlikesidir.*
    """
    from app.followup import _FIIL_EKLERI

    kisa = [e for e in _FIIL_EKLERI if len(e) < 3]
    assert not kisa, f"🔴 üç harften kısa fiil eki eklenmiş: {kisa}"


def test_PAYLASILAN_ATOM_LISTESI_KIRLETILMEDI():
    """🔴🔴 **İkinci tasarım kararı, ve korpusun güvencesi.**

    Kişi ekleri `cube_router._SUFFIX_ATOMS`'a **girmedi**: o liste katalog terimlerini
    (isimleri) eşler ve oraya kişi eki koymak route'a **sıfır fayda, artı risk** olurdu —
    üstelik o listenin geri alınmış bir gerileme geçmişi var (`mal`+`iyeti`).

    ⊙ Ayrı tutmak `KAT-1` ihlali **değildir**: *«bu geçerli bir AD çekimi mi»* ile
    *«geçerli bir FİİL çekimi mi»* aynı soru değildir. Ve ayrı tutulunca korpus
    **yapısal olarak** gerileyemez — bu satır o güvenceyi kilitler.
    """
    from app.cube_router import _SUFFIX_ATOMS
    from app.followup import _FIIL_EKLERI

    sizinti = sorted(set(_FIIL_EKLERI) & set(_SUFFIX_ATOMS))
    assert not sizinti, (
        f"🔴 fiil kişi eki paylaşılan ad-çekimi listesine sızdı: {sizinti} — "
        "route/korpus riski açıldı"
    )
