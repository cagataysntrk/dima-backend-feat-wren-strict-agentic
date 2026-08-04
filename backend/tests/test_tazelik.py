"""FAZ 1.7 — **TAZELİK MERDİVENİ** kapısı.

`grep -rl freshness backend/app/` → **0** idi. `SyncState.last_synced_at` yalnız admin
klon yolundaydı ve `/ask`'e **hiç ulaşmıyordu**: kullanıcı *"8 gündür veri gelmiyor"*u
**göremiyordu** — ve *"bu sayı neden düşük?"* sorusunun **en sık gerçek cevabı** budur.
"""

from __future__ import annotations

import pathlib
from datetime import datetime, timedelta, timezone

import pytest

from app import tazelik as T

KOK = pathlib.Path(__file__).resolve().parents[1]
FE = KOK.parent / "dima-frontend-demo-master" / "src"
_SIMDI = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


def _once(saat: float) -> datetime:
    return _SIMDI - timedelta(hours=saat)


# ── 1 · DÖRT KADEME ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("saat,beklenen", [
    (1, "taze"), (47, "taze"),          # 24×2 = 48 sn altı
    (48, "uyari"), (119, "uyari"),      # 24×5 = 120 sn altı
    (120, "hata"), (500, "hata"),
])
def test_KADEMELER_ESIKLERDEN_TURUYOR(saat, beklenen):
    assert T.kademe(_once(saat), simdi=_SIMDI) == beklenen


def test_KAYNAK_YOKSA_BILINMIYOR():
    assert T.kademe(None, simdi=_SIMDI) == "bilinmiyor"


def test_GELECEK_ZAMAN_DAMGASI_BILINMIYOR():
    """Saat kayması bir **tazelik kanıtı değildir**; *"çok taze"* diye okumak, bozuk bir
    saati **güvence** yapardı."""
    assert T.kademe(_SIMDI + timedelta(days=1), simdi=_SIMDI) == "bilinmiyor"


# ── 2 · 🔴 B4 — BİLİNMEYEN TAZELİK, TAZE DEĞİLDİR ───────────────────────────

def test_HATA_KADEMESINDE_SAYI_YOK():
    """🔴 Kaynak planlar bunun **tersini** yazıyordu; yol haritası *"bugünkü davranıştan
    **kasıtlı bir sertleşme**"* diye düzeltti. Sekiz gün eski bir sayıyı normal gibi
    göstermek, kullanıcıyı **yanlış bir karara** götürür — ve o karar geri alınamaz."""
    assert T.sayi_gosterilir_mi("hata") is False


def test_BILINMIYOR_HATA_ILE_AYNI_MUAMELE():
    """**B4.** Ölçemediğimiz bir şeyi **iyi** varsaymak, `⊘ ÖLÇÜLEMEDİ` üçüncü hâlinin
    tam tersi olurdu."""
    assert T.sayi_gosterilir_mi("bilinmiyor") is False
    assert set(T.SAYI_GIZLENEN) == {"hata", "bilinmiyor"}


def test_TAZE_VE_UYARIDA_SAYI_VAR():
    assert T.sayi_gosterilir_mi("taze") and T.sayi_gosterilir_mi("uyari")


def test_ALAN_YOKSA_SAYI_GIZLENIR():
    """`None` bir kademe **değildir** — ve *"kademe hiç hesaplanmadı"* da `bilinmiyor`'dur.
    Fail-closed: bilinmeyeni göstermek, B4'ü arka kapıdan çiğnemek olurdu."""
    assert T.sayi_gosterilir_mi(None) is False


# ── 3 · TEK SAYI YAPILANDIRILIR ─────────────────────────────────────────────

def test_ESIKLER_TEK_SAYIDAN_TURUYOR():
    """🔴 `warn_after` ve `error_after` **ayrı ayrı** ayarlanabilseydi biri ötekini
    geçebilirdi (`warn=10g`, `error=3g`) ve kullanıcı `uyari`'yı **hiç görmeden**
    `hata`'ya düşerdi. *Çelişebilen iki ayar, çelişecek demektir.*"""
    u, h = T.esikler(12)
    assert u == timedelta(hours=24) and h == timedelta(hours=60)
    assert u < h, "uyarı eşiği hata eşiğini geçmiş — merdiven anlamsızlaştı"


@pytest.mark.parametrize("kotu", [None, 0, -5, "abc"])
def test_GECERSIZ_PERIYOT_VARSAYILANA_DUSUYOR(kotu):
    """`0` kabul etseydik **her cevap anında `hata`** olurdu."""
    assert T.esikler(kotu) == T.esikler(T.VARSAYILAN_PERIYOT_SAAT)


def test_ESIK_TENANTCONFIG_TEN_OKUNUYOR_SABIT_KODLU_DEGIL():
    """Kapı (c): eşikler `TenantConfig`'ten okunur."""
    from control_plane.models import TenantConfig

    assert "tazelik_periyot_saat" in TenantConfig.model_fields


def test_EN_KOTU_KAZANIYOR():
    """Bir cevap iki tabloya dayanıyorsa tazeliği **en bayat** olanı belirler —
    ortalama almak, bayat yarıyı **gizlerdi**."""
    assert T.en_kotu(["taze", "uyari", "hata"]) == "hata"
    assert T.en_kotu(["taze", "bilinmiyor"]) == "bilinmiyor"
    assert T.en_kotu([]) == "bilinmiyor"


# ── 4 · RAPOR ───────────────────────────────────────────────────────────────

def test_RAPOR_ACIKLAMA_TASIYOR():
    """Sayının yerine **neden** gösterilmediği gelir — *neden*, sayının kendisinden
    daha değerlidir."""
    r = T.rapor(_once(200), simdi=_SIMDI)
    assert r["freshness"] == "hata" and r["aciklama"]
    assert "gösterilmiyor" in r["aciklama"]
    assert T.rapor(_once(1), simdi=_SIMDI)["aciklama"] is None


def test_SON_VERI_TS_NIN_NE_OLDUGU_YAZILI():
    """⚠ `son_veri_ts` **son BAŞARILI SENKRONdur**, verinin kendi zaman damgası değil —
    boru hattı çalışıp **boş** dönebilir. Keskin sinyal (zaman boyutunun `max()`'ı) her
    soruda **ek bir DB sorgusu** ister ve o karar (FAZ 0.17'nin gecikme bütçesi)
    **ölçülmeden alınmadı**. Ayrımın yazılı olması şart: yoksa alan adı yalan söyler."""
    kaynak = (KOK / "app" / "tazelik.py").read_text(encoding="utf-8")
    assert "boru hattı çalışıp" in kaynak.lower() or "boş** dönebilir" in kaynak
    assert "0.17" in kaynak, "gecikme bütçesi gerekçesi yazılı değil"


# ── 5 · SÖZLEŞME + FRONTEND (K2) ────────────────────────────────────────────

def test_SOZLESME_UC_ALANI_TASIYOR():
    from app.schemas import AskResponse

    for alan in ("freshness", "son_veri_ts", "tazelik_aciklama"):
        assert alan in AskResponse.model_fields, alan
    r = AskResponse(question="x")
    assert r.freshness is None, "varsayılan None değil — KURAL B kırık"


def test_FRONTEND_UC_GORSEL_HALI_UYGULUYOR():
    """🔴 **K2 + maddenin asıl kapısı.** `hata`/`bilinmiyor` kademesinde `ResultView`
    (yani SAYI) render edilmemeli."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert 'item.freshness === "hata"' in kart, "hata kademesi frontend'de hiç ele alınmamış"
    assert 'item.freshness === "bilinmiyor"' in kart, "bilinmiyor `hata` gibi işlenmiyor (B4)"
    assert 'item.freshness !== "hata" && item.freshness !== "bilinmiyor"' in kart, (
        "🔴 SAYI, bayat/bilinmeyen tazelikte HÂLÂ gösteriliyor — maddenin tek sert kuralı bu")
    assert "decoration-wavy" in kart, "`uyari` için dalgalı çizgi kanalı yok"


def test_FRONTEND_ESIK_KOPYALAMIYOR():
    """Kademe kararı **backend'de**; frontend'de ikinci bir eşik kümesi *"aynı kuralın iki
    sahibi"* olurdu ve ikisi ayrışınca kullanıcı **bayat bir sayıyı normal** görürdü."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    for sizinti in ("48", "120", "UYARI_CARPANI", "periyot"):
        assert sizinti not in kart, f"eşik frontend'e KOPYALANMIŞ ({sizinti!r}) — iki sahip"


def test_UYARI_ROZETLE_YARISMIYOR():
    """`uyari` **farklı bir görsel kanal** kullanır (renk + dalgalı alt çizgi), güven
    rozetinin emoji kanalıyla **yarışmaz** — iki uyarı üst üste binerse ikisi de okunmaz."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    i = kart.index("decoration-wavy")
    pencere = kart[max(0, i - 900):i]
    assert "yarışmaz" in pencere or "FARKLI bir" in pencere, \
        "kanal ayrımının gerekçesi yazılı değil"
