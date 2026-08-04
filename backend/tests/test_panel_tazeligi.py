"""FAZ 1.13 — **DÜŞMAN DENETİM PANELİ TAZELİĞİ.**

Panel `2026-07-24`'te donmuştu: **47 açık aksiyon**, en az altısı o tarihten sonra
kapandı ama panel bunu **bilmiyordu**. Bir denetim paneli bayatladığında iki yönde birden
yalan söyler: kapanmış maddeler *"hâlâ açık"* görünür (boşa iş), açık maddeler ise
kalabalıkta **kaybolur**.

## 🔴 Bu kapı, panelin *"kapandı"* dediği her maddeyi KODLA doğrular

*Yanlış bir «kapandı» işareti, hiç işaretlenmemiş bir maddeden daha tehlikelidir:* kimse
ona bir daha bakmaz. O yüzden her ✅ satırı burada **çalıştırılabilir bir yüklem**e
bağlıdır — düzeltme geri alınırsa kapı **kırmızı** verir.

## ⚠ KAPANANLAR SİLİNMEZ (MIMARI §10)

Kapı, kapanmış maddelerin tablodan **çıkarılmadığını** da doğrular. Silinen bir madde,
hiç bulunmamış bir maddeyle aynı yere düşer — ve panelin tüm değeri *"neyin ne zaman
kanıtlandığı"* kaydında.

## ⚠ Durumun TEK SAHİBİ `index.md`

`findings/*.md` **tarihsel kayıttır** ve bilerek güncellenmez. Oraya da durum yazmak,
aynı bilginin iki sahibi olması demekti — biri güncellenir, öteki unutulurdu.
"""

from __future__ import annotations

import pathlib
import re

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]
PANEL = KOK / "lab" / "panel"
INDEX = PANEL / "index.md"
BULGULAR = sorted((PANEL / "findings").glob("*.md"))

#: Aksiyon satırı: `1. **[P0] …`
_AKSIYON = re.compile(r"^\d+\.\s+\*\*\[P", re.M)


def _index() -> str:
    return INDEX.read_text(encoding="utf-8")


def _kaynak(*parca: str) -> str:
    return KOK.joinpath(*parca).read_text(encoding="utf-8")


# ── 1 · SAYIM — beyan ile gerçek ─────────────────────────────────────────────

def test_AKSIYON_SAYISI_BEYANLA_UYUSUYOR():
    """🔴 Bu deponun en sık kusuru: *"beyan var, sayım yok"*. Panel **47** diyor —
    dosyalar kaç diyor?"""
    gercek = sum(len(_AKSIYON.findall(p.read_text(encoding="utf-8"))) for p in BULGULAR)
    assert gercek == 47, f"panel 47 aksiyon beyan ediyor, dosyalarda {gercek} var"
    assert "**47**" in _index(), "başlıktaki sayı güncellenmemiş"


def test_DURUM_TOPLAMI_47_YE_ESIT():
    """🔴 **Bu kapı, ilk yazımda KENDİ metnimi yakaladı:** başlıkta *"38 açık"* yazıyordu,
    tablodaki gerçek sayım **36**'ydı. Yani panelin teşhis ettiği kusur sınıfı, panelin
    kendi özet satırında yaşıyordu. Toplam artık **eşit olmak zorunda**."""
    m = re.search(r"✅ (\d+) kapandı · ◐ (\d+) kısmen · ⊘ (\d+) [^·]+· ⬜ (\d+) açık",
                  _index())
    assert m, "durum özeti bulunamadı — biçim değişmişse kapı GÜNCELLENMELİ, silinmemeli"
    kapali, kismen, olculemedi, acik = (int(g) for g in m.groups())
    assert kapali + kismen + olculemedi + acik == 47, (
        f"{kapali}+{kismen}+{olculemedi}+{acik} = "
        f"{kapali + kismen + olculemedi + acik} ≠ 47")


def test_KAPANANLAR_SILINMEMIS():
    """⚠ **MIMARI §10.** Silinen bir madde, hiç bulunmamış bir maddeyle aynı yere düşer."""
    tablo = _index()
    for mid in ("R5-1", "R5-2", "R3-1", "R3-2", "R4-4", "R2-8"):
        assert f"**{mid}**" in tablo, f"{mid} tablodan SİLİNMİŞ — işaretlenmeliydi"


# ── 2 · HER «KAPANDI» İDDİASI KODLA DOĞRULANIR ──────────────────────────────
#
# 🔴 Yüklemler **kaynak koda** bakar, panelin metnine değil: metin taraması, iddianın
# kendisini kanıt sayardı (bu oturumda yedi kez o tuzağa düşüldü).

# ⚠ Yüklemler kaynağı **doğrudan okumaz, bir OKUYUCU alır** — böylece kapının kendisi
# `test_KAPI_SAHTE_DEGIL`'de boş bir okuyucuyla **mutasyona uğratılıp** kırmızı olabildiği
# kanıtlanabilir. *Bir kapı, kırmızı olabildiğini kanıtlayana kadar kapı değildir.*

def _r5_1(oku) -> bool:                    # scheduler tenant-farkında motor
    return "registry.service_for(slug)" in oku("app", "schedules.py")


def _r5_2(oku) -> bool:                    # atomik compose + per-slug lock
    return ("DerlemeKilidi" in oku("app", "compose.py")
            and "os.replace" in oku("app", "compose.py")
            and "build_lock_for" in oku("app", "company_registry.py"))


def _r3_1(oku) -> bool:                    # ek-farkında kapsam (substring yasak)
    k = oku("app", "cube_router.py")
    return ("def _covers" in k and "_NEGATION_SUFFIXES" in k
            and "word.startswith(known)" in k)


def _r3_2(oku) -> bool:                    # negasyon üretimi
    k = oku("app", "cube_router.py")
    return '"neq"' in k and '"not_in"' in k


def _r4_4(oku) -> bool:                    # tablo-allowlist (Katman B) — İKİ uçta
    return ("katman_b.zorla(" in oku("app", "routers", "query.py")
            and "katman_b.sarmala(" in oku("app", "routers", "ask.py"))


def _r2_8(oku) -> bool:                    # period_optional taşınabilir
    return "period_optional" in oku("app", "cube_router.py")


KAPANANLAR = {
    "R5-1": (_r5_1, "scheduler artık `state.wren` yerine tenant'ın motorunu çözüyor"),
    "R5-2": (_r5_2, "compose per-slug kilit + `os.replace` ile atomik"),
    "R3-1": (_r3_1, "kapsam eşleşmesi ek-farkında; olumsuzluk eki kapsama SAYILMAZ"),
    "R3-2": (_r3_2, "deterministik yol `neq`/`not_in` üretiyor"),
    "R4-4": (_r4_4, "Katman B ham SQL'in İKİ yolunda da zorlanıyor"),
    "R2-8": (_r2_8, "`period_optional` cube_query'ye gömülü, taşınabilir"),
}


@pytest.mark.parametrize("mid", sorted(KAPANANLAR))
def test_KAPANDI_IDDIASI_KODDA_DOGRU(mid):
    """🔴 *Yanlış bir «kapandı» işareti, hiç işaretlenmemiş bir maddeden daha tehlikelidir:*
    kimse ona bir daha bakmaz. Düzeltme geri alınırsa bu kapı kırmızı verir."""
    yuklem, gerekce = KAPANANLAR[mid]
    assert yuklem(_kaynak), f"{mid} panelde ✅ ama kodda DEĞİL — beklenen: {gerekce}"


@pytest.mark.parametrize("mid", sorted(KAPANANLAR))
def test_KAPI_SAHTE_DEGIL_duzeltme_geri_alininca_KIRMIZI(mid):
    """🔴 **Bir kapı, kırmızı olabildiğini kanıtlayana kadar kapı değildir.**

    Mutasyon **bellekte**: yüklem, düzeltmenin hiç yapılmadığı bir kaynak görürse `False`
    dönmeli. Yüklemlerden biri sessizce `True` dönen bir sabite dönüşürse (ya da aradığı
    dizi kaynaktan bağımsız hale gelirse) **bu test** yakalar — depoya hiçbir şey yazılmaz.
    """
    yuklem, _ = KAPANANLAR[mid]
    assert yuklem(lambda *_p: "") is False, (
        f"{mid} yüklemi BOŞ kaynakta da ✅ diyor — kapı hiçbir şey ölçmüyor")


# ── 3 · DURUMUN TEK SAHİBİ ──────────────────────────────────────────────────

def test_DURUM_BULGU_DOSYALARINA_KOPYALANMAMIS():
    """🔴 *"Aynı kuralın iki sahibi"* — bu deponun en sık kaydettiği kusur sınıfı.
    `findings/*.md` **tarihsel kayıttır**: güncellenmediği için değerlidir."""
    for p in BULGULAR:
        metin = p.read_text(encoding="utf-8")
        assert "✅ **KAPANDI**" not in metin, (
            f"{p.name}: durum bulgu dosyasına KOPYALANMIŞ — iki sahip ayrışır")


def test_TARIHSEL_LISTE_DONMUS_OLDUGUNU_SOYLUYOR():
    """Tur 5'in *"en kritik açık aksiyonlar"* listesi **değiştirilmedi**; okuyucu bunu
    bilmezse bugünkü durum sanır."""
    k = _index()
    i = k.index("## En kritik açık aksiyonlar")
    assert "TUR 5" in k[i:i + 400] and "DEĞİŞTİRİLMEDİ" in k[i:i + 400]


def test_PANEL_TARIHI_GUNCELLENDI():
    """Bayat bir panelin ilk belirtisi **tarihidir** — ve eski tarih **silinmez**,
    yanında durur (*"neyin ne zaman kanıtlandığı"*)."""
    k = _index()
    assert "2026-08-04" in k and "önceki: 2026-07-24" in k


# ── 4 · AÇIK KALANLARIN SAHİBİ YAZILI ───────────────────────────────────────

def test_ACIK_KALANLARIN_FAZI_YAZILI():
    """⚠ Sahibi olmayan bir açık madde, **kimsenin** maddesidir. Panelin 47'lik listesi
    tam olarak böyle bayatlamıştı: kim, ne zaman bakacak — yazılı değildi."""
    k = _index()
    i = k.index("### Açık kalan")
    blok = k[i:i + 3000]
    assert blok.count("FAZ") >= 6, "açık kümelerin çoğunun sahibi (fazı) yazılmamış"
