"""FAZ 7.4 kapısı — **EK H'nin panel/katman kuralları.** [bayraksız: K5]

`test_panel_sayisi.py` **sayıyı** kilitliyor (K5, tavan 13). Bu kapı **kuralları**
kilitler: PK-1 · PK-9 · PK-13 · PK-22 · PK-23 · PK-24.

## Neden ayrı bir dosya

Sayı ile kural **farklı şeylerdir**, ve bu ayrım bir kusurdan doğdu: tavan 13'te
tutulurken bir yetenek pekâlâ **var olan bir paneli şişirebilir** ya da tavanı
aşmadan bir **modal** açabilir. *Bir sayacı geçmek, kurala uymak değildir.*

## PK-23: tavan **sürüme bağlıdır** — ve sürüm bir yerde yazılı olmalı

v1 = **13** · v2+ = **15** (`WhatIfPaneli` + `DuyarlilikPaneli` **gerçek panellerdir**).
🔴 Sürüm 3'te bu sayı belgede **beş yerde** geçiyordu ve **üç farklı değer** taşıyordu.
*Tanımsız bir sayının beş kopyası, beş ayrı bayatlama yüzeyidir.* Bu kapı, sayının
**tek** kaynağı olduğunu doğrular: `test_panel_sayisi.TAVAN`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.kapi_ortak import fe_dosyalari, fe_kaynak, frontend_dir
from tests.test_panel_sayisi import DESEN, TAVAN

_KOK = Path(__file__).resolve().parents[1]


# --- PK-23: sayının TEK kaynağı --------------------------------------------------------

def test_PK23_TAVAN_tek_kaynaktan_okunur():
    """🔴 *Bir sayıyı iki dosyaya yazmak, onu iki kez bayatlatmaktır.*

    Bu kapı tavanı **kendi içinde yeniden yazmaz** — `test_panel_sayisi`'nden alır.
    O dosya v2'de 15'e çıktığında burası **kendiliğinden** hizalanır.
    """
    assert TAVAN == 13, (
        f"🔴 v1 tavanı {TAVAN}. Yükseltmek bir KARARDIR: EK H/PK-23 ve §C/11 ile "
        f"birlikte yapılır, sessizce değil.")


def test_PK23_v2_PANELLERI_v1de_YOK():
    """⚠ `WhatIfPaneli`/`DuyarlilikPaneli` **Bölüm II**'nindir. v1'de var olsalardı tavan
    zaten aşılırdı — ve bu, sayının bir tesadüf değil bir **karar** olduğunu gösterir."""
    kaynak = fe_kaynak()
    for ad in ("WhatIfPaneli", "DuyarlilikPaneli"):
        assert ad not in kaynak, (
            f"🔴 `{ad}` v1'e sızmış — o bir Bölüm II panelidir ve tavanı 15'e çıkarır.")


# --- PK-1: yeni yetenek yeni panel doğurmaz -------------------------------------------

#: FAZ 5-7'de eklenen yetenekler ve **bağlandıkları var olan yüzey**. Her satır bir
#: *"panel açmadım"* iddiasıdır ve iddia **ölçülür**.
_YETENEK_YUZEY = {
    "tema (7.2)": ("TemaDugmesi", "components/FloatingControls.tsx"),
    "ad sorma (7.5)": ("useAdSor", "components/AdSor.tsx"),
    "sonraki adım (5.x)": ("NextStepChips", "components/NextStepChips.tsx"),
}


@pytest.mark.parametrize("yetenek", sorted(_YETENEK_YUZEY))
def test_PK1_yeni_yetenek_yeni_PANEL_dogurmadi(yetenek):
    """🔴 EK H/PK-1. ⚠ Ölçüt **dosya değil, `export …Panel`**: bir yetenek kendi
    dosyasında yaşayabilir; yasak olan **ayrı bir panel yüzeyi** açmasıdır.

    (`AdSor` bir *modal*dir, panel değil — ve modal olması da bir karardır: ad sorma
    **kalıcı bir artefakt değildir**, PK-2'nin panel ölçütünü karşılamaz.)
    """
    _, dosya = _YETENEK_YUZEY[yetenek]
    src = fe_dosyalari().get(dosya, "")
    assert src, f"⊘ {dosya} yok — iddia ÖLÇÜLEMEZ"
    assert not DESEN.findall(src), (
        f"🔴 `{dosya}` bir panel export ediyor — `{yetenek}` yeni bir panel doğurdu.")


def test_PK2_PANEL_sayilanlar_KALICI_ARTEFAKT():
    """PK-2: panel yalnız **kalıcı artefaktlar** için — pano · zamanlanmış rapor ·
    bağlantı · inceleme · geçmiş · bildirim · yardım · tercih · sözleşme · şema.

    ⚠ Bu liste **kapalıdır**: yeni bir ad eklemek, PK-2'nin sınıfını genişletmek
    demektir ve o bir **karardır**. Kapı, kararı görünür kılar.
    """
    izinli = {
        "ChatPanel", "ConnectionReviewPanel", "ContractDetailPanel", "DashboardsPanel",
        "DrillDownPanel", "HelpPanel", "HistoryPanel", "NotificationsPanel",
        "ReportPanel", "ReviewPanel", "SchedulesPanel", "SchemaPanel", "TercihlerPanel",
    }
    bulunan = {ad for src in fe_dosyalari().values() for ad in DESEN.findall(src)}
    yeni = sorted(bulunan - izinli)
    assert not yeni, (
        f"🔴 PK-2 sınıfında OLMAYAN yeni panel(ler): {yeni}. Kalıcı bir artefakt mı "
        f"gösteriyor? Değilse yeri cevabın **kendi kartıdır**.")
    assert len(bulunan) <= TAVAN


# --- PK-9 / PK-10: kök neden MODAL DEĞİL, inline ---------------------------------------

def test_PK9_KOK_NEDEN_yeni_sekme_MODAL_acmiyor():
    """PK-9: tıklama yeni sekme/modal **açmaz**, ağacı **büyütür**.

    ⚠ `DrillDownPanel` bugün bir modaldir ve bu **bilinen bir borçtur** — PK-9 onun
    *"tıklamanın ağacı büyütmesi"* şartını koyar, kapı da tam olarak onu ölçer:
    ağaç içi tıklama `window.open` ya da yeni bir modal state'i **açmamalı**.
    """
    src = fe_dosyalari()["components/DrillDownPanel.tsx"]
    assert "window.open" not in src, (
        "🔴 Kök neden tıklaması yeni sekme açıyor — kullanıcı bağlamını kaybeder.")
    # Ağaç adımları AYNI panelde birikiyor mu (yeni modal değil)?
    assert "steps" in src, "🔴 adımlar aynı yüzeyde birikmiyor"


def test_PK10_PANODA_AYRI_drill_mekanizmasi_YOK():
    """PK-10/KD-10: *"Panoda ayrı drill mekanizması YAZILMAZ — AYNI `KokNedenHaritasi`."*"""
    dv = fe_dosyalari().get("components/DashboardView.tsx", "")
    assert "DrillDownPanel" in dv or "drill" not in dv.lower(), (
        "🔴 Pano kendi drill mekanizmasını yazmış — iki mekanizma AYRIŞIR.")


# --- PK-13 + A11Y-9: soluk ≠ devre dışı ------------------------------------------------

def test_PK13_SOLUK_ile_DEVRE_DISI_ayri_token():
    """PK-13'ün son cümlesi: *"Soluk ama tıklanabilir" ile "devre dışı" **ASLA aynı
    token'ı paylaşmaz.*"

    (Ölçümü ve gerekçesi `test_a11y.py`'de; burada **PK-13 adına** kilitleniyor —
    aynı kural iki kapıda **aynı kaynağa** bakar, iki farklı tanıma değil.)
    """
    css = (frontend_dir() / "app/globals.css").read_text(encoding="utf-8")
    assert "--opacity-disabled" in css and "--opacity-soluk" in css
    assert not re.search(r"disabled:opacity-\d", fe_kaynak())


def test_PK6_DUSUK_SINYAL_gizlenmez_SOLUKLASIR():
    """PK-6'nın genel ilkesi: *"asla gizleme — düşük sinyalli öge **soluk** gösterilir,
    kaldırılmaz."*

    🔴 Bu, `--opacity-soluk`'un **var olma sebebidir**: gizlemek bir bilgi kaybıdır ve
    kullanıcı neyi kaçırdığını **bilemez**.
    """
    css = (frontend_dir() / "app/globals.css").read_text(encoding="utf-8")
    assert "--opacity-soluk" in css


# --- PK-22: rota sayısı ----------------------------------------------------------------

def test_PK22_ROTA_sayisi_MENUYU_sismiyor():
    """PK-22 hedefi **4 → ~10-12** (*"hâlâ az, menü şişmez"*).

    ⚠ **Bu bir TAVAN, bir hedef değil.** Ölçüm bugün **5** rota gösteriyor
    (`/` · `/login` · `/review` · `/paylasim/[token]` · `/brand`) — hedefin altında
    olmak bir kusur DEĞİLDİR; hedefi **aşmak** kusurdur. *Bir "10-12 olsun" cümlesini
    bir zorunluluğa çevirmek, panel enflasyonunu rota enflasyonuna taşımak olurdu.*
    """
    rotalar = sorted(p.parent.relative_to(frontend_dir() / "app").as_posix()
                     for p in (frontend_dir() / "app").rglob("page.tsx"))
    assert len(rotalar) <= 12, (
        f"🔴 Rota sayısı {len(rotalar)} — PK-22 tavanı 12: {rotalar}")
    assert "brand" in rotalar, "⚠ `/brand` KD-3 ile kapsam dışı ama VAR; sayım eksik"


# --- PK-24: yüzey kırpması yasağı (K4 ile aynı kaynağa bakar) --------------------------

def test_PK24_KAPISI_VAR_ve_kural_YAZILI():
    """🔴 PK-24 sürüm 4'te **atıf alıyordu ama tanımlı değildi** — belgenin kendi avladığı
    *"beyan var, kod onu tanımıyor"* sınıfının **belge-içi hâli**.

    Kapısı `test_yuzey_sadakati.py` (K4); burada onun **varlığı** kilitleniyor: bir
    kuralın kapısının silinmesi, kuralın silinmesidir.
    """
    kapi = _KOK / "tests/test_yuzey_sadakati.py"
    assert kapi.exists(), "🔴 PK-24'ün kapısı (K4) yok"
    src = kapi.read_text(encoding="utf-8")
    assert "source" in src, "🔴 K4 `source` rozetini ölçmüyor"


def test_PK24_YENI_YUZEY_de_rozeti_dusurmuyor():
    """⚠ PK-24'ün ölçülmüş üç örneğinden biri `AnalysisCanvas`ın rozet basmamasıydı.
    Bu turda eklenen yüzeyler (`AdSor`) bir **cevap** göstermiyor — dolayısıyla PK-24
    kapsamında değil; ve *bu ayrım yazılı olmalı ki bir gün biri "modal de yüzeydir"
    diye kapıyı yanlış yerde kırmızı yapmasın.*"""
    src = fe_dosyalari()["components/AdSor.tsx"]
    assert "AskResponse" not in src, (
        "🔴 `AdSor` artık bir cevap gösteriyor — PK-24 kapsamına girdi, rozet/`explain` "
        "taşımalı.")
