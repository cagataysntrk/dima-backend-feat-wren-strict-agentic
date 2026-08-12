"""🔴🔴 `§D9`/`§B10` — **METODOLOJİ SKILL'LERİ**: kohort · huni · YoY-oranı.

## Raporun isteği

> `§36.1-5` madde 5: *«**Skills (markdown)** — kapalı fiil listesinin ilacı, **kod
> yazmadan**»*. `§D9`: *«Metodoloji (kohort/funnel/YoY-oranı) — ❌ yok»*.

Mekanizma `§B10` ile kurulmuştu (`katalog_metni.skills_metni()` + `skills` bayrağı +
`yoy-orani.md`). Eksik olan **metinlerdi** — ve eksikliğin bedeli `§18.6`'da ölçüldü:

    «müşteri kohort analizi yap» → müşteri × dönem PİVOTU teslim edildi
                                 → «kohort uygulanmadı» beyanı: YOK

## Bu turda yazılan iki metin — ve ikisi ZITTIR

| skill | ne diyor | dayanağı |
|---|---|---|
| `huni.md` | ✅ **YAPILABİLİR** — `firsat` küpü zaten bir satış hunisi | ölçüldü: sinonimler `huni`·`pipeline`, `asama` boyutu, gerçek aşama değerleri |
| `kohort.md` | 🔴 **YAPILAMAZ** — ve pivot onun yerine geçmez | ölçüldü: kohort *ilk dönem* + *görece zaman* ister; küp sözleşmesinde **ikisi de yok** |

⊙ Bir skill kümesinin değeri yalnız *«şunu şöyle yap»* demekte değil, **sınırı
yazmakta**: `kohort.md`'nin tamamı bir *«yapamam ama şunu beyan et»* talimatıdır.

> *Bir yeteneğin yokluğunu, ona benzeyen bir çıktıyla kapatmak, yokluğu gizlemez —
> yalnız keşfini kullanıcıya bırakır.*

## ⚠ Skill'ler yeni FİİL/ÖLÇÜ tanımlamaz

`§38.4` dokunulmazı: kapalı fiil kümesi. Skill garsona *«hangi VAR OLAN yapıyla
karşıla»* der; bir yetenek **icat etmez**. Aşağıdaki kapı bunu ölçer.

⊙ **İŞ BÖLÜMÜ (`KAT-1`, ⟳ 08-12):** bu dosya üç metodoloji dosyasının **İÇERİĞİNİ**
sahiplenir. **MEKANİZMA** (`tests/test_b10_skills.py`): yükleyici · `KURAL B` · indeks
dokunulmazlığı · açılış şartı · kiracı bağlaması.
⚠ *«Skill yeni fiil icat etmiyor»* iki dosyada da ölçülüyor — **iki ayrı yüklemle**,
bilinçli bir ikinci göz. Biri bayatlarsa öteki konuşur.
"""

from __future__ import annotations

import pathlib

import pytest

_SKILLS = pathlib.Path(__file__).parent.parent / "demo" / "skills"
_BEKLENEN = ("yoy-orani.md", "huni.md", "kohort.md")


@pytest.mark.parametrize("ad", _BEKLENEN)
def test_UC_METODOLOJI_DOSYASI_VAR(ad):
    """🔴 `§D9`'un istediği üç metodoloji: dönem kıyası · huni · kohort."""
    f = _SKILLS / ad
    assert f.is_file(), f"🔴 `demo/skills/{ad}` yok — `§D9` metodolojisi eksik."
    assert len(f.read_text(encoding="utf-8")) > 800, (
        f"{ad} çok kısa — bir metodoloji dosyası bir başlık değildir.")


def test_HUNI_GERCEK_KUPU_ADIYLA_GOSTERIYOR():
    """Skill bir dilek değil bir **yönlendirme**: hangi küp, hangi boyut, hangi ölçü."""
    m = (_SKILLS / "huni.md").read_text(encoding="utf-8")
    for parca in ("firsat", "asama", "firsat_adedi", "kazanma_orani_yuzde"):
        assert parca in m, f"🔴 huni skill'i `{parca}` adını anmıyor — yönlendirmiyor."


def test_HUNI_DONUSUM_SINIRINI_YAZIYOR():
    """🔴🔴 **EN ÖNEMLİ SATIR.** `asama` bugünkü aşamayı taşır; dönüşüm oranı **aşama
    geçmişi** ister ve o yok. Bir anlık dağılımı dönüşüm diye sunmak sessiz-yanlıştır."""
    m = (_SKILLS / "huni.md").read_text(encoding="utf-8")
    assert "DÖNÜŞÜM" in m and "yok_sayilan" in m, (
        "🔴 huni skill'i dönüşüm sınırını yazmıyor → anlık dağılım dönüşüm sanılır.")
    assert "Kazanıldı" in m and "Kaybedildi" in m, (
        "aşama sırası yazılmamış — katalog onu ALFABETİK verir, iş sırası değil.")


def test_KOHORT_YAPILAMAZ_DIYOR_ve_BEYANI_TARIF_EDIYOR():
    """🔴 Kusurun ta kendisi: pivot kohort diye teslim ediliyordu."""
    m = (_SKILLS / "kohort.md").read_text(encoding="utf-8")
    assert "İFADE EDİLEMEZ" in m or "YAPILAMAZ" in m, (
        "🔴 kohort skill'i sınırı söylemiyor.")
    assert "yok_sayilan" in m and "kohort" in m, (
        "🔴 skill BEYAN yolunu tarif etmiyor — sınırı bilmek, onu bildirmeyi gerektirir.")
    assert "pivot" in m.lower(), "pivot ile farkı yazılmamış — ikisi karıştırılır."


@pytest.mark.parametrize("ad", _BEKLENEN)
def test_SKILL_YENI_FIIL_ICAT_ETMIYOR(ad):
    """⚠ `§38.4` dokunulmazı: kapalı fiil kümesi. Skill **var olanı** gösterir.

    Yüklem yapısal: metinde `plan_semasi.FIIL_ANLAMI`'nda **olmayan** büyük harfli bir
    fiil adı geçmemeli."""
    import re

    from app.plan_semasi import FIIL_ANLAMI

    m = (_SKILLS / ad).read_text(encoding="utf-8")
    # Kod bloğu/backtick içinde geçen BÜYÜK HARFLİ tek sözcükler — fiil adayı.
    adaylar = {w for w in re.findall(r"`([A-ZÇĞİÖŞÜ]{3,})`", m)}
    icat = sorted(adaylar - set(FIIL_ANLAMI) - {"SQL", "MIN", "MAX", "SUM", "AVG"})
    assert not icat, (
        f"🔴 `{ad}` katalogda olmayan bir FİİL anıyor: {icat}. Skill yetenek İCAT ETMEZ; "
        "var olan yapıyı gösterir (`§38.4` — kapalı fiil kümesi).")


def test_YUKLEYICI_UCUNU_de_OKUYOR():
    """🔴 Yazılıp yüklenmeyen bir metin, yazılmamış bir metindir."""
    from app.katalog_metni import skills_metni

    metin = skills_metni()
    assert metin, "⊘ yükleyici boş döndü — `demo/skills/*.md` bulunamıyor."
    for anahtar in ("DEĞİŞİM ORANI", "SATIŞ HUNİSİ", "KOHORT"):
        assert anahtar in metin, (
            f"🔴 yükleyici `{anahtar}` başlıklı skill'i okumuyor — dosya var ama "
            "garsona ulaşmıyor.")


def test_KURAL_B_BAYRAK_KAPALIYKEN_KATALOG_DEGISMEZ(schema):
    """⚠ Bayrak `off`: iki yeni dosya kataloğu **bayt bayt** değiştirmemeli.

    *Ölçülemeyen bir kazancı varsayılan açmak, ölçümü bir törene çevirir* — açılış şartı
    `§26` (garson doğruluk ölçümü) hâlâ park edilmiş."""
    from app.katalog_metni import metin_ve_indeks

    # ⚠ İkinci parametre `principal` — imzayı ölçmeden çağırdım ve `TypeError`
    # aldım (ders ⑤: *şekli/adı ölç, varsayma*).
    metin, _ = metin_ve_indeks(schema, None)
    assert "SATIŞ HUNİSİ" not in metin and "KOHORT ANALİZİ" not in metin, (
        "🔴 bayrak kapalıyken skill metni kataloğa sızmış — `KURAL B` ihlali.")
