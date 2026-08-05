"""FAZ 2.2b — **METRİK KAYDININ YÜZEYİ**: sahiplik artık BESLENEBİLİYOR.

🔴 **0.18 kendi kendine ATILDI.** Hakem (`metrik_kaydi.hakem`) kurulmuştu ama kayıt
katalogdan **taslak** üretiliyor ve `sahiplenilen_terimler` **boş** başlıyordu; boşu
dolduracak bir yol olmadığı için hakem **hiçbir zaman** karar veremezdi.
*Kurulmuş ama beslenemeyen bir hakem, kurulmamış bir hakemdir.*

⚠ **Bu dosya 2.2b'nin KENDİ kapısıdır** — `test_metrik_kaydi.py` 0.18'indir. Yol
haritasının kendi uyarısı: *"bir doğrulama turunda 2.2b, 0.18'in testiyle «bitti»
sayılabilirdi: kapı yanlış maddeyi yeşile boyar."*

> **Karar kaydı: `ADR-0029`** — metrik sahipliği — pack ÖNERİR, tenant UYGULAR.
"""

from __future__ import annotations

import pathlib

from app import metrik_kaydi as mk

KOK = pathlib.Path(__file__).resolve().parents[1]
FE = KOK.parent / "dima-frontend-demo-master" / "src"

_TASLAK = [{"terim": "satış", "adaylar": ["ticaret", "mal"],
            "sahiplenilen_terimler": [], "olusturulma_yontemi": "otomatik_taslak"}]


def test_SAHIPLIK_HAKEMI_BESLIYOR():
    """🔴 Maddenin özü: karar → kayıt → hakem. Zincirin herhangi bir halkası kopuksa
    mekanizma **atıldır**."""
    birlesik = mk.sahiplikle_birlestir(_TASLAK, {"satış": "ticaret"})
    assert birlesik[0]["sahiplenilen_terimler"] == ["ticaret"]
    assert birlesik[0]["olusturulma_yontemi"] == "insan_karari"
    assert mk.hakem("satış", birlesik) == "ticaret", "hakem hâlâ karar VEREMİYOR"


def test_KARAR_YOKKEN_BUGUNKU_YOL():
    """Karar verilmemişse hakem `None` döner ve `_match_cube` bugünkü yolunu izler —
    maddenin **kendi kendine güvenli** olmasının mekanizması."""
    assert mk.hakem("satış", mk.sahiplikle_birlestir(_TASLAK, {})) is None


def test_ADAY_OLMAYAN_SAHIP_SESSIZCE_YUTULMUYOR():
    """🔴 Aday olmayan bir cube'u sahip yazmak **sessizce hiçbir şey yapmazdı** (hakem
    onu döndürse `_match_cube` bulamazdı). *Sessizce yok saymak, kullanıcının kararını
    çöpe atıp ona söylememektir.* Kayıt `gecersiz_sahip` taşıyor."""
    b = mk.sahiplikle_birlestir(_TASLAK, {"satış": "olmayan_cube"})
    assert b[0]["sahiplenilen_terimler"] == []
    assert b[0]["gecersiz_sahip"] == "olmayan_cube"
    assert mk.hakem("satış", b) is None


def test_SAHIPLIK_KALDIRILINCA_KAYIT_SILINMIYOR():
    """`sahip_cube=None` → sahiplik kalkar ama satır **durur**: *kararın geri alındığı da
    bir kayıttır* — kim, ne zaman geri aldı görülebilmeli."""
    from control_plane.models import MetrikSahipligi

    assert MetrikSahipligi.model_fields["sahip_cube"].default is None
    assert "karar_veren_user_id" in MetrikSahipligi.model_fields


def test_TEK_SAHIP_KISITI_DB_DE_de_VAR():
    """🔴 Aynı kural **iki yerden** korunuyor ve bu bilinçli: `UniqueConstraint` **yazma**
    anını, `cift_sahiplik_denetle` **okuma** anını kollar."""
    kaynak = (KOK / "control_plane" / "models.py").read_text(encoding="utf-8")
    assert 'UniqueConstraint("tenant_id", "terim"' in kaynak
    assert mk.cift_sahiplik_denetle(
        [{"terim": "satış", "sahiplenilen_terimler": ["ticaret", "mal"]}])


def test_ALAN_LISTESI_BILEREK_DARALTILDI():
    """⚠ Yol haritası `display_name · unit · rounding · description` da sayıyor; hepsi
    **cube YAML'ında zaten var**. DB'ye kopyalamak *"aynı kuralın iki sahibi"* olurdu —
    biri güncellenir, öteki unutulur ve kullanıcı hangi birimin doğru olduğunu bilemez.
    **DB'nin eklediği tek yeni bilgi SAHİPLİKTİR.**"""
    from control_plane.models import MetrikSahipligi

    fazla = {"display_name", "unit", "rounding", "description", "target_ref"} & set(
        MetrikSahipligi.model_fields)
    assert not fazla, f"katalogda zaten olan alanlar DB'ye kopyalanmış: {fazla}"
    kaynak = (KOK / "control_plane" / "models.py").read_text(encoding="utf-8")
    i = kaynak.index("class MetrikSahipligi")
    assert "aynı kuralın iki sahibi" in kaynak[i:i + 2500], "daraltmanın GEREKÇESİ yazılı değil"


def test_UCLAR_VAR_ve_YETKILI():
    """`PATCH`'in yetkisi `metric:certify`: bir terimin sahibini seçmek, o metriğin
    **tanımını** onaylamakla aynı sınıf bir karardır. Ayrı bir izin adı uydurmak, yetki
    matrisini kararın kendisinden **koparırdı**."""
    from app.main import create_app

    yollar = {y: {m.upper() for m in o} for y, o in create_app().openapi()["paths"].items()}
    assert "GET" in yollar.get("/metrics", set())
    assert "PATCH" in yollar.get("/metrics/{terim}", set())
    kaynak = (KOK / "app" / "routers" / "metrics.py").read_text(encoding="utf-8")
    assert 'require("metric:certify")' in kaynak
    assert "audit.record" in kaynak, "karar AUDIT'e yazılmıyor"


# ── K2 · YETİM UÇ YOK — ekran tüketicisi var, YENİ PANEL yok ────────────────

def _fe(*p: str) -> str:
    import pytest

    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    return FE.joinpath(*p).read_text(encoding="utf-8")


def test_EKRAN_TUKETICISI_VAR():
    """🔴 *Bir karar, verilebilir olmadıkça karar değildir.* `PATCH` ucu ekrandan
    çağrılmıyorsa sahiplik hâlâ **beslenemez** — yani 0.18 hâlâ atıldır."""
    panel = _fe("components", "SchemaPanel.tsx")
    assert "setMetrikSahibi" in panel and "getMetrics" in panel
    assert "setMetrikSahibi" in _fe("lib", "api-client.ts")


def test_YENI_PANEL_ACILMADI():
    """🔴 **K5 tavanı 13/13, pay 0.** Sahiplik bir **katalog** bilgisidir (*"şu terim
    hangi cube'a ait"*) ve yeri kataloğun kendisidir; ayrı bir ekran, kullanıcıyı aynı
    soruyu **iki yerde** aramaya iterdi."""
    import re

    if not FE.exists():
        import pytest

        pytest.skip("frontend mount edilmemiş")
    sayi = sum(
        len(re.findall(r"export (?:default )?function [A-Za-z]+Panel\b",
                       p.read_text(encoding="utf-8")))
        for p in (FE / "components").glob("*.tsx"))
    assert sayi <= 13, f"panel sayısı {sayi} — K5 tavanı 13"
    assert not (FE / "components" / "MetrikPanel.tsx").exists()


def test_YETKI_UIDA_KOPYALANMIYOR():
    """UI düğmeyi gizler ama **sınır backend'dedir** (`require("metric:certify")`).
    Rol semantiği frontend'e KOPYALANMAZ — izin `/auth/me`'den okunur (CLAUDE.md)."""
    panel = _fe("components", "SchemaPanel.tsx")
    assert 'usePermission("metric:certify")' in panel
    for sizinti in ("role ===", "owner", "is_superadmin"):
        assert sizinti not in panel, f"rol semantiği UI'a kopyalanmış ({sizinti!r})"


def test_GECERSIZ_SAHIP_EKRANDA_GORUNUYOR():
    """⚠ Aday olmayan bir sahiplik **kaydedilir ama uygulanmaz** — ve kullanıcı bunu
    görmeli. *Sessizce yok saymak, kullanıcının kararını çöpe atıp ona söylememektir.*"""
    panel = _fe("components", "SchemaPanel.tsx")
    assert "gecersiz_sahip" in panel and "geçersiz" in panel
