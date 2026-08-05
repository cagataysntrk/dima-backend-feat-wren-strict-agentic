"""FAZ 6.1 kapısı — **onay akışı.** [bayrak: `onay_akisi`]

Yol haritasının kapısı (D9 ile güncellenmiş): onaysız **kapsam dışı** yazma **imkânsız** ·
`geri_alinamaz` eylem **her zaman** senkron istem · her onay **ayrı audit satırı** ·
süresi geçmiş onay **reddediliyor** · 🔴 **istem sayısı/tur telemetriye yazılır ve
ARTARSA KIRMIZI**.

## 🔴 "Onay bir buton değildir"

Anthropic telemetrisi: kullanıcılar izin isteklerinin **~%93'ünü** onaylıyor. **Onay
yorgunluğu ölçülmüş bir olgudur** — bu yüzden varsayılan **sınır**, istem değil (FAZ 6.0)
ve bu modül yalnız **istem gereken** hâli yönetir.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app import onay_akisi as oa


def _talep(**kw):
    return oa.olustur("zamanla.olustur", {"label": "Aylık fire"},
                      kaynak="kullanici", **kw)


# --- DURUM MAKİNESİ: KAPALI --------------------------------------------------------

def test_GECIS_MAKINESI_kapali():
    """*Serbest bir durum alanı, bir durum makinesi değil bir dilektir.*"""
    t = _talep()
    assert t.durum == oa.TASLAK
    oa.gecis(t, oa.ONAY_BEKLIYOR)
    oa.gecis(t, oa.ONAYLANDI)
    oa.gecis(t, oa.GERI_ALINDI)
    with pytest.raises(oa.OnayHatasi):
        oa.gecis(t, oa.ONAYLANDI)          # son durumdan çıkış yok


def test_TASLAKTAN_dogrudan_ONAYLANDIYA_gecilemez():
    with pytest.raises(oa.OnayHatasi, match="geçişi YOK"):
        oa.gecis(_talep(), oa.ONAYLANDI)


def test_REDDEDILEN_is_GERI_ALINAMAZ():
    """⚠ *Yapılmamış bir şeyi geri almak, olmayan bir olayı kayda geçirmektir.*"""
    t = _talep()
    oa.gecis(t, oa.ONAY_BEKLIYOR)
    oa.gecis(t, oa.REDDEDILDI)
    with pytest.raises(oa.OnayHatasi):
        oa.gecis(t, oa.GERI_ALINDI)


def test_BILINMEYEN_durum_reddedilir():
    with pytest.raises(oa.OnayHatasi, match="bilinmeyen durum"):
        oa.gecis(_talep(), "her_neyse")


# --- SÜRE AŞIMI --------------------------------------------------------------------

def test_SURESI_GECMIS_onay_REDDEDILIR():
    """🔴 *Dün verilmiş bir "evet", bugünün dünyasına verilmemiştir.*"""
    t0 = datetime(2026, 8, 5, 10, 0, tzinfo=timezone.utc)
    t = _talep(simdi=t0)
    oa.gecis(t, oa.ONAY_BEKLIYOR)
    oa.gecis(t, oa.ONAYLANDI)
    oa.calistirilabilir_mi(t, t0 + timedelta(minutes=29))       # geçerli
    with pytest.raises(oa.OnayHatasi, match="süresi doldu"):
        oa.calistirilabilir_mi(t, t0 + timedelta(minutes=31))


def test_VARSAYILAN_OMUR_otuz_dakika():
    assert oa.VARSAYILAN_OMUR_SN == 30 * 60


def test_ONAYLANMAMIS_talep_CALISTIRILAMAZ():
    """🔴 Ret **sebebiyle birlikte** gelmeli: *"onay geçersiz"* diyen bir `False`,
    kullanıcıya neyi düzelteceğini söylemez."""
    with pytest.raises(oa.OnayHatasi, match="durumunda"):
        oa.calistirilabilir_mi(_talep())


# --- RİSKE GÖRE YÖNLENDİRME --------------------------------------------------------

def test_GERI_ALINAMAZ_her_zaman_SENKRON():
    assert oa.senkron_mu(oa.RISK_GERI_ALINAMAZ) is True


def test_ORTA_ve_DUSUK_kuyruga():
    """⚠ Düşük riskli bir işi senkron istem yapmak, tam da **ölçülmüş yorgunluğu**
    üretir."""
    assert oa.senkron_mu(oa.RISK_ORTA) is False
    assert oa.senkron_mu(oa.RISK_DUSUK) is False


def test_BILINMEYEN_risk_reddedilir():
    with pytest.raises(oa.OnayHatasi, match="bilinmeyen risk"):
        oa.olustur("x", {}, kaynak="k", risk="kritik")


# --- ONAY KAPSAMI BİR NESNEDİR ------------------------------------------------------

def test_KAPSAM_bir_NESNE():
    """*"Evet"in sınırı yazılı olmalı; sınırsız bir "evet", onay değil bir İMZADIR.*"""
    t = _talep()
    d = t.sozluk()
    for alan in ("arac", "argumanlar", "kaynak", "risk", "son_gecerlilik",
                 "geri_alma_fonksiyonu_ref"):
        assert alan in d, f"onay kapsamında `{alan}` yok"


@pytest.mark.parametrize("yasak", ["password", "api_key", "token", "iban", "cvv"])
def test_SIR_tasiyan_talep_URETILMEZ(yasak):
    """🔴 MCP'nin normatif yasağı — ve asıl sebep daha basit: bir onay kartında görünen
    parola, **ekran görüntüsüne** ve **audit satırına** girer."""
    with pytest.raises(oa.OnayHatasi, match=yasak):
        oa.olustur("x", {yasak: "gizli"}, kaynak="k")


def test_GERI_ALMA_referansi_METIN():
    """⚠ Bir çağrılabiliri kayda koymak onu **serileştirilemez** ve denetlenemez yapardı."""
    t = oa.olustur("x", {}, kaynak="k", geri_alma_ref="dashboards.remove_widget")
    assert isinstance(t.geri_alma_fonksiyonu_ref, str)
    assert isinstance(t.sozluk()["geri_alma_fonksiyonu_ref"], str)


def test_MCP_hizalamasi_DOGRULANMADI_damgali():
    """🔴 *Doğrulanmamış bir uyumluluk beyanı, uyumsuzluktan kötüdür.*

    Spec sürümü çelişkili (bir kaynak *2026-07-28*, öteki *2025-11-25*) — hizalama bir
    **iddia** olarak duruyor ve öyle **damgalanıyor**.
    """
    assert "[DOĞRULANMADI]" in oa.MCP_HIZALAMA
    assert "[DOĞRULANMADI]" in _talep().sozluk()["mcp_hizalama"]


# --- TELEMETRİ: ONAY YORGUNLUĞU -----------------------------------------------------

def test_ISTEM_ORANI_olculuyor():
    """🔴 *İstem sayısı/tur — ARTARSA KIRMIZI.*"""
    r = oa.istem_orani(tur_sayisi=100, istem_sayisi=12)
    assert r["oran"] == 0.12 and r["tur"] == 100
    assert "yorgunlu" in r["not"]   # yorgunluğu/yorgunluk — kök yeterli


def test_HIC_TUR_YOKKEN_oran_UCUNCU_HALDIR():
    """⚠ *Hiç tur yokken "%0 istem" demek, çalışmayan bir sistemi başarılı gösterirdi.*"""
    r = oa.istem_orani(tur_sayisi=0, istem_sayisi=0)
    assert r["oran"] is None and "ÖLÇÜLEMEDİ" in r["not"]


# --- D9 İLE TUTARLILIK ---------------------------------------------------------------

def test_D9_ile_TUTARLI_gerialinabilir_is_ISTEM_ISTEMEZ(monkeypatch):
    """FAZ 6.0 ile aynı hükmü paylaşır: kapsam içi + geri alınabilir → **istem yok**."""
    import control_plane.authorize as az

    from app import eylem

    monkeypatch.setattr(az, "can", lambda p, i: True)

    class _P:
        user_id = "u1"
        tenant_id = "t1"

    assert eylem.d9_istemsiz_mi(eylem.PANO_EKLE, _P()) is True
    # Ve geri alınamaz olan HÂLÂ senkron istem ister.
    assert eylem.d9_istemsiz_mi(eylem.ZAMANLA, _P()) is False
    assert oa.senkron_mu(oa.RISK_GERI_ALINAMAZ) is True


def test_YAZMA_YUZEYI_BUYUMEDI():
    """🔴 *H'nin dersi korunur:* yazma aracı **araç kaydına GİRMEZ**.

    *"Güvenlik imzadan değil, yetki yüzeyinin genişlememesinden geliyor."*
    """
    from app import tools

    assert not [a.ad for a in tools.hepsi() if a.yan_etki == "yazar"]
