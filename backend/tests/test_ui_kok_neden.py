"""🌳 FAZ 4B — kök-neden haritasının **arayüz** kapıları.

Planın kapı listesi birebir:
- `DrillDownPanel`'in **her** işlevi erişilebilir kalmalı
- dört durumun dördü de **çizilebiliyor**; **silik olan tıklanabilir**
- kaydedilen notta **yol** var
- `<768px`'te **ağaç çizilmiyor**, çip+liste çiziliyor
- panel sayısı ≤13 *(kendi kapısı: `test_panel_sayisi.py`)*

⚠ Bu dosya **çizimi** denetler; puanlamayı `test_kok_neden.py` denetler. *Bir kapının
neyi ölçmediğini bilmek, neyi ölçtüğünü bilmek kadar önemlidir.*
"""

from __future__ import annotations

import re

from tests.kapi_ortak import frontend_dir, yorumsuz

HARITA = "components/KokNedenHaritasi.tsx"


def _src(ad: str = HARITA) -> str:
    return (frontend_dir() / ad).read_text(encoding="utf-8")


def _kod(ad: str = HARITA) -> str:
    """Yorumsuz gövde. 🔴 Bu dosya iki kez kendi belgesini yakaladı (`aria-modal`,
    `"{0,"`); tarama **her zaman** yorumsuz gövdede yapılır."""
    return yorumsuz(_src(ad))


# ═══════════════════════════════════════════════════════════════════════════════
# ADLANDIRMA — K1
# ═══════════════════════════════════════════════════════════════════════════════

def test_PANEL_DEGIL_ARAC():
    """🔴 K1: ad `…Panel` **değil**. Bu bir yüzey türü değil bir **araştırma aracı**;
    `AnalizPaneli`nin içinde yaşar, kendi panelini açmaz — panel sayısı sabit kalır."""
    assert (frontend_dir() / HARITA).exists(), "🔴 KokNedenHaritasi.tsx yok"
    assert not (frontend_dir() / "components/KokNedenPanel.tsx").exists()


def test_PUANLAMA_ARAYUZDE_DEGIL():
    """🔴 **D.6'nın şartı.** İnsanın tıklayarak verdiği karar (*"hangi boyutta
    dallanayım"*) ile bir ajanın vereceği karar **aynı karardır**; frontend'e gömülü
    bir mantık **çağrılamaz**.

    Kapı, arayüzün `sinyal`/`durum` **hesaplamadığını** ölçer: eşik sabitleri, z-skoru
    ya da pay aritmetiği burada olmamalı."""
    kod = _kod()
    for yasak in ("Math.sqrt", "stdev", "zSkor", "z_score", "esik", "threshold"):
        assert yasak not in kod, f"🔴 puanlama arayüze sızmış: {yasak}"


# ═══════════════════════════════════════════════════════════════════════════════
# DÖRT DURUM — ve 🔴 silik olanın TIKLANABİLİRLİĞİ
# ═══════════════════════════════════════════════════════════════════════════════

DURUMLAR = ("kanitli", "zayif", "olculemedi", "kapsam_disi")


def test_DORT_DURUM_CIZILEBILIYOR():
    """Dördünün de bir görsel karşılığı olmalı — yoksa backend'in ürettiği bir durum
    ekranda **kaybolur** ve kimse fark etmez."""
    kod = _kod()
    for d in DURUMLAR:
        assert d in kod, f"🔴 `{d}` durumunun görsel karşılığı yok"


def test_SILIK_DUGUM_DEVRE_DISI_DEGIL():
    """🔴 **Planın en önemli kapısı.** ⚠ Silik ≠ kapalı.

    Bir düğümü *"veri yok"* diye **devre dışı bırakmak** bu tasarımın tek fikrini
    öldürür: bazen **verinin yokluğu bulgunun kendisidir** (*"o vardiyada hiç kayıt
    yok"*). `disabled` niteliği düğüm kartında **hiç** geçmemeli."""
    kod = _kod()
    kart = kod[kod.index("function DugumKarti"):kod.index("export function KokNedenHaritasi")]
    assert "disabled" not in kart, \
        "🔴 düğüm kartında `disabled` var — silik bir düğüm KAPATILMIŞ"


def test_DURUM_DOM_DA_OKUNABILIR():
    """⚠ Durum yalnız bir sınıf adına gömülüyse **denetlenemez** (ne testle, ne bir
    ajanla). `data-durum` onu DOM'da birinci sınıf bir olguya çevirir."""
    assert "data-durum" in _kod(), "🔴 düğüm durumu DOM'da okunabilir değil"


# ═══════════════════════════════════════════════════════════════════════════════
# NOT — kökeniyle kaydedilir
# ═══════════════════════════════════════════════════════════════════════════════

def test_NOT_YOLU_TASIYOR():
    """🔴 *Bir not, kökeni olmadan bir kanaattir.*

    Bu, deponun makbuz kültürünün birebir karşılığı: yol kaydedilmezse not yeniden
    üretilemez, doğrulanamaz, tartışılamaz. Kapı, not geri çağrısının `yol`u **taşıdığını**
    ve sohbete yazılırken **görselleştirildiğini** ister."""
    kod = _kod()
    assert re.search(r"onNot\?:\s*\(kayit:\s*\{\s*yol:", kod), \
        "🔴 not geri çağrısı yolu taşımıyor"
    makine = _kod("components/KartMakinesi.tsx")
    assert "yol.join" in makine, \
        "🔴 yol sohbete yazılırken görselleştirilmiyor (`fire ↑ ── makine: RAM-2 ── ✎ …`)"


def test_NOT_IKI_YERDE_DE_CALISIYOR():
    """⚠ Makine iki yerde yaşıyor (kart · panel) ama not yolu **tek** olmalı.

    *Yalnız kartta çalışan bir not, panelde çalışmayan bir nottur* — ve kullanıcı
    hangisinde olduğunu hatırlamak zorunda kalırdı."""
    for ad in ("components/ReportCard.tsx", "app/page.tsx"):
        assert "onNot=" in _kod(ad), f"🔴 {ad}: not zinciri bağlı değil"


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSIVE — ağaç küçük ekranda ağaç DEĞİLDİR
# ═══════════════════════════════════════════════════════════════════════════════

def test_KUCUK_EKRANDA_AGAC_YOK():
    """🔴 375px'lik bir ekranda ağaç çizmek okunamaz. Aynı veri, **farklı izdüşüm**.

    Kapı iki şeyi ister: (a) düğümler dar ekranda **tek sütun** (kart listesi) ve
    ancak `md`/`xl`de yayılır; (b) yol her izdüşümde **kaydırılabilir çip şeridi**
    olarak görünür."""
    kod = _kod()
    assert "md:grid-cols-2" in kod and "xl:grid-cols-3" in kod, \
        "🔴 düğümler dar ekranda kart listesine düşmüyor"
    assert "overflow-x-auto" in kod, "🔴 yol dar ekranda kaydırılamıyor"


def test_YOL_HER_IZDUSUMDE_GORUNUR():
    """*Yol, ağacın kendisinden önemlidir:* kullanıcı nerede olduğunu kaybederse
    ağacın çizimi bir işe yaramaz. Bu yüzden yol hiçbir kırılım noktasında gizlenmez."""
    kod = _kod()
    yol = kod[kod.index("data-yol"):kod.index("data-yol") + 400]
    for gizle in ("max-md:hidden", "hidden md:", "max-lg:hidden"):
        assert gizle not in yol, f"🔴 yol bir izdüşümde gizleniyor: {gizle}"


# ═══════════════════════════════════════════════════════════════════════════════
# BOĞULMAMA — yol + BİR kat
# ═══════════════════════════════════════════════════════════════════════════════

def test_TEK_KAT_CIZILIYOR():
    """*Bir ağaç, tüm dallarını aynı anda gösterdiğinde ağaç olmaktan çıkar, yığın olur*
    — ve yığın, kullanıcının şikâyet ettiği şeyin ta kendisi.

    Kapı: bileşen `cocuklar`ı **özyinelemeli çizmemeli** (kendini çağırmamalı)."""
    kod = _kod()
    kart = kod[kod.index("function DugumKarti"):kod.index("export function KokNedenHaritasi")]
    assert "<DugumKarti" not in kart, "🔴 düğüm kartı kendini çiziyor — bütün ağaç açılıyor"
    assert "d.cocuklar" not in kod, "🔴 çocuklar aynı anda çiziliyor — yığın"


def test_HARITA_VARSAYILAN_KAPALI():
    """⚠ Panel zaten yoğun; harita bir **araç**tır, bir katman değil. Açık gelseydi tam
    da düzeltmeye çalıştığı boğulmayı üretirdi."""
    makine = _kod("components/KartMakinesi.tsx")
    assert "useState(false)" in makine, "🔴 kök-neden haritası varsayılan açık"


def test_HER_ADIM_KENDI_GRAFIGINI_URETIYOR():
    """Planın D.2'si: *"Her genişletme adımı kendi küçük grafiğini üretir — çıplak tablo
    ASLA."* Grafik/tablo kararı `ResultView`'ındır (ADR-0024) — burada yeniden verilmez."""
    kod = _kod()
    assert "<ResultView" in kod, "🔴 açılan kat kendi grafiğini çizmiyor"
    assert "SinyalCubugu" in kod, "🔴 düğümün kendi mikro grafiği yok"


# ═══════════════════════════════════════════════════════════════════════════════
# D.3 — HER GRAFİK TÜRÜ BİR GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════════════════════════════════

def test_PANELLI_VE_ISI_TIKLAMASI_ACILDI():
    """🔴 Kısıt bir UI tercihi değil, **sözleşmenin tekilliğiydi**: `dimension` +
    `filter_value` tek çapa taşıyordu, oysa panelli grafikte bir tıklama (panel +
    kategori) ve ısı haritasında bir hücre (satır + sütun) **iki** filtre demek.

    ⚠ Çapalar **veri ögesine** iliştirildi, `seriesIndex`ten geri hesaplanmadı: indis
    aritmetiği panel sarma/sıra kurallarına bağımlı olurdu ve o kurallar değiştiğinde
    **sessizce** yanlışlanırdı."""
    chart = _kod("lib/chart.ts")
    assert chart.count("capalar") >= 2, "🔴 panelli/ısı noktaları kendi çapasını taşımıyor"
    rv = _kod("components/ResultView.tsx")
    assert "capalar" in rv, "🔴 ResultView çapaları okumuyor"


def test_KENAR_OZETI_HALA_DURUST_REDDEDIYOR():
    """⚠ Isı haritasının kenar hücreleri (satır/sütun ortalaması) bir kesişim **değil**
    bir özettir; orada kırılacak tek bir satır kümesi YOKTUR.

    *Bir kısıtı kaldırmak, her noktayı tıklanabilir ilan etmek değildir* — kalan tek
    dürüst red **sebebini söyleyerek** kalır."""
    rv = _kod("components/ResultView.tsx")
    assert "setNoDrillHint" in rv, "🔴 sessiz ret geri gelmiş"
    assert "ÖZET" in rv or "özet" in rv, "🔴 kenar özeti için gerekçe yok"


# ═══════════════════════════════════════════════════════════════════════════════
# DEVRALMA — DrillDownPanel'in işlevleri KAYBOLMADI
# ═══════════════════════════════════════════════════════════════════════════════

def test_DRILL_ISLEVLERI_ERISILEBILIR():
    """🔴 Planın kapısı: *`DrillDownPanel`'in **her** işlevi taşınmış olmalı.*

    ⚠ *Taşınmış* ≠ *silinmiş*: harita bir **öncelik katmanıdır**, `DrillDownPanel`in
    yerine geçen bir kopya değil. Beşi de erişilebilir kalmalı — çünkü kaybolan bir
    işlev, kaybolduğu gün değil ihtiyaç duyulduğu gün fark edilir."""
    drill = _kod("components/DrillDownPanel.tsx")
    for eylem in ('"expand"', '"select"', '"raw"', '"related"', '"explain"'):
        assert eylem in drill, f"🔴 drill eylemi kaybolmuş: {eylem}"
    kart = _kod("components/ReportCard.tsx")
    assert "<DrillDownPanel" in kart, "🔴 DrillDownPanel artık hiç açılmıyor"
