"""FAZ 5.16 kapısı — **netleştirme düzeyi bir AYAR.** [bayrak: `netlestirme_duzeyi`]

## 🔴 Dış öneri OLDUĞU GİBİ kabul EDİLMEDİ

Dış denetim *"`kapali` seçilirse eksik dönem **varsayılanla** cevaplanır"* öneriyordu —
bu, MIMARI'nin avladığı **sessiz-yanlış sınıfının ta kendisidir**. Üç sertleştirme
şartıyla kabul edildi ve bu dosya **üçünü de ayrı ayrı** kilitler.
"""

from __future__ import annotations

import pytest

from app import netlestirme as n


def test_VARSAYILAN_bugunku_davranis():
    """`None` → `normal` → bugünkü davranış **birebir** (GERİ AL bedava)."""
    assert n.duzey(None) == "normal"
    assert n.sorar_mi(None) is True
    assert n.govde_notu(None) is None


def test_BOZUK_ayar_NORMALE_duser_kapaliya_DEGIL():
    """🔴 Fail-safe **`normal`**.

    Bozuk bir ayarın sonucu *"daha az soru"* olsaydı, bir **yazım hatası** sessiz-yanlış
    üretirdi.
    """
    for bozuk in ("KAPALİ", "off", "", "yüksek", "xyz", "  "):
        assert n.duzey(bozuk) in ("normal", "yuksek"), bozuk
    assert n.duzey("kapali ") == "kapali"      # yalnız boşluk kırpma
    assert n.duzey("off") == "normal", "🔴 tanınmayan değer `kapali`ya düşerse yazım "\
                                       "hatası sessiz-yanlış üretir"


def test_NORMAL_yalniz_donemi_sorar():
    """ADR-0007-K3 — bugünkü davranış."""
    assert n.sorar_mi("normal", belirsizlik="donem") is True
    assert n.sorar_mi("normal", belirsizlik="olcu") is False


def test_YUKSEK_olcu_ve_boyutta_da_sorar():
    """⚠ Kapsamı **düşürür** ve bu bilinçli bir takas."""
    for b in ("donem", "olcu", "boyut"):
        assert n.sorar_mi("yuksek", belirsizlik=b) is True


def test_KAPALI_hicbir_sey_sormaz():
    for b in ("donem", "olcu", "boyut"):
        assert n.sorar_mi("kapali", belirsizlik=b) is False


# --- ÜÇ SERTLEŞTİRME ---------------------------------------------------------------

def test_SERT_1_varsayim_GOVDEDE_rozette_DEGIL():
    """🔴 *Kenara yazılmış bir varsayım, yazılmamış bir varsayımdır.*

    `explain.assumptions` bir **denetim** alanıdır; kullanıcı onu okumaz ve okumak
    zorunda da değildir.
    """
    m = n.govde_notu("kapali")
    assert m and "varsayıldı" in m and "Dönem belirtilmedi" in m
    # `normal`/`yuksek`'te gürültü YOK.
    assert n.govde_notu("normal") is None and n.govde_notu("yuksek") is None


def test_SERT_1b_varsayim_TUM_ZAMANLAR_degil():
    """🔴 Bir BI sorusunun sessiz cevabı *"tarihin başından beri"* olamaz — o, kullanıcının
    **hiç sormadığı** bir soruya cevaptır."""
    assert n.KAPALI_VARSAYIM == "bu yıl"
    assert "tüm" not in n.govde_notu("kapali").lower()


def test_SERT_2_degisiklik_AUDIT_satiri_uretir():
    """⚠ Bu ayar bir **risk tercihini** değiştirir; *kim ne zaman değiştirdi* sorusu bir
    olaydan **sonra** sorulur."""
    class _P:
        user_id = "u1"
        tenant_id = "t1"

    s = n.degisiklik_denetim_satiri("normal", "kapali", _P())
    assert s["action"] == "netlestirme_duzeyi.degisti"
    assert s["eski"] == "normal" and s["yeni"] == "kapali"
    assert s["user_id"] == "u1" and s["tenant_id"] == "t1"


def test_SERT_3_KAPALI_cevaplari_PROBABILISTIK():
    """🔴 Sınıf **düşürülür, yükseltilmez**.

    Deterministik bir yoldan gelmiş olsa bile cevabın **sorusu** varsayımla
    tamamlandıysa, sonuç artık o varsayıma bağlıdır. *Kesin bir hesabın belirsiz bir
    girdisi, hesabı belirsiz yapar.*
    """
    assert n.kanit_sinifi("kapali", "deterministik") == "probabilistik"
    assert n.kanit_sinifi("kapali", None) == "probabilistik"
    # Diğer düzeylerde sınıf DEĞİŞMEZ.
    assert n.kanit_sinifi("normal", "deterministik") == "deterministik"
    assert n.kanit_sinifi("yuksek", "deterministik") == "deterministik"


def test_TENANT_CONFIG_alani_var():
    from control_plane.models import TenantConfig

    assert "netlestirme_duzeyi" in TenantConfig.model_fields


@pytest.mark.parametrize("d", n.DUZEYLER)
def test_UC_DUZEY_tanimli(d):
    assert n.duzey(d) == d
