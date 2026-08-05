"""FAZ 6.5 kapısı — **public API + idempotency + embed kapsamı.**
[bayrak: `public_api` · `embed`]

## 🔴 P0 — `embed` BU TURDA AÇILAMAZ, ve sebebi ÖLÇÜLDÜ

Yol haritasının bağlayıcı şartı: *"Wren RLS'i gömülü pano grafiklerini kapsamıyorsa
`embed` **AÇILMAZ**; `always_filter` tek başına yeterli sayılmaz."*

**Ölçüm:** `Settings.motor_cls == "off"` — motor-RLS **hiç açık değil** (açılması 36
çağrı sitesinin kimlik geçirmesine bağlı, açık borç #1). Şartın *"kapsıyor mu"* sorusu
**sorulamıyor**: kapsayacak mekanizma **çalışmıyor**.

> *Bir güvenlik sınırını ölçmeden açmak, onu hiç kurmamaktan kötüdür: kurulduğu sanılır.*
"""

from __future__ import annotations

import pytest

from app import embed_kapsam as ek


class _S:
    motor_cls = "off"


# --- P0 KAPISI ----------------------------------------------------------------------

def test_P0_embed_ACILAMAZ_ve_sebep_YAZILI():
    """🔴 Bir ön koşulu **belgeye yazıp koda yazmamak**, onu ilan edip uygulamamaktır."""
    sebep = ek.p0_engeli(_S())
    assert sebep and "motor-RLS" in sebep and "AÇILAMAZ" in sebep


def test_P0_motor_RLS_acikken_engel_KALKAR():
    """⚠ Kapı bir **duvar değil bir şart**: motor-RLS `on` olduğu gün engel kalkar — ama
    o gün de gömülü yüzeyin **davranışsal** ölçümü ayrıca koşmalıdır (bugün `⊘`)."""
    class _On:
        motor_cls = "on"

    assert ek.p0_engeli(_On()) is None


def test_GERCEK_AYAR_bugun_kapali():
    """Beyanın kendisi de doğrulanır: bugün gerçekten `off` mu?"""
    from app.config import get_settings

    assert str(getattr(get_settings(), "motor_cls", "off")).lower() != "on", (
        "🔴 `motor_cls` artık AÇIK — P0 ön koşulu yeniden değerlendirilmeli ve gömülü "
        "yüzeyin davranışsal RLS ölçümü YAZILMALI (bugün ⊘ ÖLÇÜLEMEDİ).")


# --- KAPSAM: BEYAZ LİSTE, FAIL-CLOSED ------------------------------------------------

_SCOPE = {"cubes": ["parti"], "izin": {"parti": {"measures": ["fire_orani_yuzde"],
                                                 "dimensions": ["makine"]}}}


def test_KAPSAM_DISI_cube_REDDEDILIR():
    with pytest.raises(ek.EmbedReddi, match="kapsamı dışında"):
        ek.kapsam_izin_veriyor_mu(_SCOPE, "oee")


def test_KAPSAM_DISI_olcu_ve_boyut_REDDEDILIR():
    with pytest.raises(ek.EmbedReddi, match="measures"):
        ek.kapsam_izin_veriyor_mu(_SCOPE, "parti", olculer=["toplam_fire_kg"])
    with pytest.raises(ek.EmbedReddi, match="dimensions"):
        ek.kapsam_izin_veriyor_mu(_SCOPE, "parti", boyutlar=["hat"])


def test_KAPSAM_ICI_gecer():
    ek.kapsam_izin_veriyor_mu(_SCOPE, "parti", olculer=["fire_orani_yuzde"],
                              boyutlar=["makine"])


@pytest.mark.parametrize("bos", [None, {}, {"cubes": []}, {"cubes": None}])
def test_BOS_KAPSAM_hicbir_seyi_ACMAZ(bos):
    """🔴 *"Kapsam belirtilmedi"* ile *"kapsam sınırsız"* **aynı şey değildir** ve
    ikincisi asla varsayılan olamaz."""
    with pytest.raises(ek.EmbedReddi, match="kapsamsız"):
        ek.kapsam_izin_veriyor_mu(bos, "parti")


# --- İPTAL: ANINDA -------------------------------------------------------------------

def test_IPTAL_EDILMIS_token_ANINDA_dusiyor():
    """🔴 İmzalı bir URL'nin yapamadığı **tek şey** budur: dağıtılmış bir URL geri
    çağrılamaz."""
    ek.token_gecerli_mi(False)
    with pytest.raises(ek.EmbedReddi, match="iptal"):
        ek.token_gecerli_mi(True)


def test_LOOKER_imzali_URL_modeli_DEGIL():
    """⚠ Kapsam bir **KAYITTIR**, bir URL parametresi değil — ve kapı bunu kilitler:
    modülde bir imza/HMAC üretimi **olmamalı**."""
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/embed_kapsam.py")
                     .read_text(encoding="utf-8"))
    cagrilar = {getattr(c.func, "attr", getattr(c.func, "id", ""))
                for c in ast.walk(agac) if isinstance(c, ast.Call)}
    for yasak in ("new", "hexdigest", "sign", "urlsafe_b64encode"):
        assert yasak not in cagrilar, (
            f"🔴 `embed_kapsam.py` bir imza üretiyor (`{yasak}`) — Looker'ın imzalı-URL "
            f"modeli BİLEREK reddedildi: imzalı bir URL İPTAL EDİLEMEZ.")


# --- KOTA -----------------------------------------------------------------------------

def test_KOTA_BELIRTILMEMIS_token_REDDEDILIR():
    """🔴 `None` **sınırsız DEĞİL**: sınırsız bir gömme token'ı, faturayı **bilinmez**
    yapar ve bir gün kimsenin açıklayamadığı bir maliyet üretir."""
    with pytest.raises(ek.EmbedReddi, match="kota belirtilmemiş"):
        ek.kota_kontrol(None, 0)


def test_KOTA_asimi_reddedilir():
    ek.kota_kontrol(10, 9)
    with pytest.raises(ek.EmbedReddi, match="kota doldu"):
        ek.kota_kontrol(10, 10)


# --- IDEMPOTENCY: YENİ KUYRUK KURULMADI ------------------------------------------------

def test_YENI_KUYRUK_KURULMADI_AskJob_genellendi():
    """*Yeni kuyruk KURULMAZ* — `AskJob` genellenir."""
    import control_plane.models as m
    from control_plane.models import AskJob

    assert "client_idempotency_key" in AskJob.model_fields
    assert not hasattr(m, "PublicApiJob") and not hasattr(m, "ApiJob")


def test_IDEMPOTENCY_TENANT_ile_BIRLIKTE_benzersiz():
    """🔴 Tek başına anahtar **DEĞİL**: iki kiracının aynı anahtarı seçmesi mümkündür ve
    o an biri **ötekinin işini** görürdü.

    *Bir idempotency anahtarı, kiracı sınırının içinde benzersizdir.*
    """
    from pathlib import Path

    goc = (Path(__file__).resolve().parents[1]
           / "migrations/versions/d5a8c3f10e74_public_api_embed.py").read_text(
        encoding="utf-8")
    assert '["client_idempotency_key", "tenant_id"]' in goc and "unique=True" in goc, (
        "🔴 Benzersiz kısıt tenant'ı İÇERMİYOR — çapraz-tenant iş çalınması mümkün.")
    assert "IS NOT NULL" in goc, (
        "🔴 Kısıt partial değil — anahtar göndermeyen bütün çağrılar tek bir NULL'a "
        "çarpışır ve birbirinin işi olurdu.")


def test_EMBED_TOKEN_iptal_alani_var():
    from control_plane.models import EmbedToken

    for alan in ("tenant_id", "scope_json", "kota", "son_kullanim", "iptal_edildi"):
        assert alan in EmbedToken.model_fields, f"`{alan}` yok"
