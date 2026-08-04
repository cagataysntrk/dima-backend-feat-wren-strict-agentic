"""FAZ 1.10 — **ESKALASYON MATRİSİ** kapısı: süre dolunca **bir üst kademeye** yükseliyor mu?

Bir eşik aşıldığında bildirim gider — ve orada **biter**. Kimse bakmazsa sistem *"haber
verdim"* der ve susar. Ama bir uyarının **işlevi** haber vermek değil, **bir karara yol
açmaktır**: *on iki saat kimsenin bakmadığı bir alarm, hiç gönderilmemiş bir alarmla aynı
sonucu üretir.*
"""

from __future__ import annotations

import ast
import pathlib
from datetime import datetime, timedelta, timezone

import pytest

from app import eskalasyon as E

KOK = pathlib.Path(__file__).resolve().parents[1]
_SIMDI = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


def _kural(**kw) -> dict:
    return {"id": "k1", "ad": "fire eşiği", "tetikleyici_esik": "fire>5",
            "sure_dakika": 60, "hedef_rol": "analyst", "otomatik_kilitle": False, **kw}


# ── 1 · SÜRE DOLUNCA BİR ÜST KADEMEYE ───────────────────────────────────────

def test_SURE_DOLUNCA_YUKSELIYOR():
    """🔴 **Maddenin kapısı, birebir.**"""
    karar = E.degerlendir(_kural(), ilk_asim=_SIMDI - timedelta(minutes=61), simdi=_SIMDI)
    assert karar["onceki_rol"] == "analyst" and karar["hedef_rol"] == "admin"
    assert "60 dk yanıtsız" in karar["ozet"]


def test_SURE_DOLMADAN_YUKSELMIYOR():
    assert E.degerlendir(_kural(), ilk_asim=_SIMDI - timedelta(minutes=59),
                         simdi=_SIMDI) is None


def test_ROL_MERDIVENI_YETKI_MATRISIYLE_AYNI():
    """🔴 İkinci bir merdiven yazmak, eskalasyonun **yetki matrisinden ayrışması**
    demekti: biri `analyst → admin` derken öteki başka bir sıra izlerdi."""
    from control_plane.authorize import ROLE_RANK

    assert E.ROL_SIRASI == tuple(sorted(ROLE_RANK, key=lambda r: ROLE_RANK[r]))


@pytest.mark.parametrize("simdiki,beklenen", [
    ("viewer", "analyst"), ("analyst", "admin"), ("admin", "owner"), ("owner", None),
])
def test_BIR_UST_ROL(simdiki, beklenen):
    assert E.bir_ust_rol(simdiki) == beklenen


def test_TEPEDE_YUKSELME_YOK():
    """`owner`'da takılı bir uyarı artık **insan kararı** bekler, otomatik bir kanal değil.
    Kendisine yükseltmek, bir döngü ve **sonsuz audit satırı** üretirdi."""
    assert E.degerlendir(_kural(hedef_rol="owner"),
                         ilk_asim=_SIMDI - timedelta(days=1), simdi=_SIMDI) is None


# ── 2 · FAIL-SAFE DALLAR ────────────────────────────────────────────────────

def test_ESIK_HIC_ASILMAMISSA_TETIKLENMIYOR():
    """🔴 `None`'ı *"çok eski"* saymak, **hiç tetiklenmemiş** bir kuralı **anında**
    yükseltirdi — ve her 60 sn'de bir yükseltmeye devam ederdi."""
    assert E.tetiklendi_mi(_kural(), ilk_asim=None, simdi=_SIMDI) is False


def test_GELECEK_ZAMAN_TETIKLEMIYOR():
    """Saat kayması bir **eskalasyon gerekçesi** değildir (`tazelik.kademe`'nin aynı kararı)."""
    assert E.tetiklendi_mi(_kural(), ilk_asim=_SIMDI + timedelta(hours=1),
                           simdi=_SIMDI) is False


@pytest.mark.parametrize("kotu", [0, -5, None, "abc"])
def test_GECERSIZ_SURE_VARSAYILANA_DUSUYOR(kotu):
    """`0` kabul etseydik kural **anında ve sürekli** tetiklenirdi."""
    assert E.tetiklendi_mi(_kural(sure_dakika=kotu),
                           ilk_asim=_SIMDI - timedelta(minutes=59), simdi=_SIMDI) is False
    assert E.tetiklendi_mi(_kural(sure_dakika=kotu),
                           ilk_asim=_SIMDI - timedelta(minutes=61), simdi=_SIMDI) is True


def test_BIR_KURALIN_HATASI_OTEKILERI_DURDURMUYOR():
    def _patlak(k):
        if k["id"] == "kotu":
            raise RuntimeError("eşik okunamadı")
        return _SIMDI - timedelta(hours=2)

    kararlar = E.kurallari_degerlendir(
        [_kural(id="kotu"), _kural(id="iyi")], asim_zamani=_patlak, simdi=_SIMDI)
    assert [k["kural_id"] for k in kararlar] == ["iyi"]


# ── 3 · 🔴 KİLİT UYGULANMIYOR — KARAR ÜRETİLİYOR ────────────────────────────

def test_OTOMATIK_KILIT_SADECE_ONERI():
    """🔴 Bir hesabı otomatik kilitlemek **geri alınamaz** bir kullanıcı etkisidir ve
    FAZ 6'nın *"onaysız hiçbir yazma"* değişmezine bağlıdır. Kararı üretip **uygulamamak**
    bir eksiklik değil, o değişmezin **korunmasıdır** — ve karar `AuditLog`'a yazıldığı
    için **görünürdür**.

    *Uygulanmayan ama kaydedilen bir karar, uygulanan ama kaydedilmeyen bir karardan her
    zaman daha iyidir.*
    """
    karar = E.degerlendir(_kural(otomatik_kilitle=True),
                          ilk_asim=_SIMDI - timedelta(hours=2), simdi=_SIMDI)
    assert karar["kilit_onerisi"] is True

    kaynak = (KOK / "app" / "eskalasyon.py").read_text(encoding="utf-8")
    for eylem in ("status =", "suspend", "lock(", "delete"):
        assert eylem not in kaynak, f"eskalasyon KİLİTLEME EYLEMİ yapıyor ({eylem!r})"


def test_KILIT_ONERISININ_SAHIBI_YAZILI():
    """Uygulanmayan bir kararın **sahibi** yazılı olmazsa, bir sonraki tur onu ya
    *"unutulmuş"* sanar ya **sessizce uygular**."""
    kaynak = (KOK / "app" / "eskalasyon.py").read_text(encoding="utf-8")
    assert "FAZ 6" in kaynak and "onaysız hiçbir yazma" in kaynak


# ── 4 · 🔴 YENİ CRON YOK ────────────────────────────────────────────────────

def test_MEVCUT_DONGUYE_BAGLI_YENI_CRON_YOK():
    """🔴 İkinci bir zamanlayıcı, iki ayrı *"şimdi saat kaç"* sahibi yaratırdı ve ikisi
    kaydığında hangi kuralın ne zaman koştuğu **bilinemezdi**."""
    agac = ast.parse((KOK / "app" / "main.py").read_text(encoding="utf-8"))
    dongu = [n for n in ast.walk(agac)
             if isinstance(n, ast.FunctionDef) and n.name == "_scheduler_loop"]
    assert len(dongu) == 1, f"{len(dongu)} scheduler döngüsü var — ikinci bir zamanlayıcı"
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "dongude_degerlendir"
               for n in ast.walk(dongu[0])), "eskalasyon döngüye BAĞLI DEĞİL — modül ölü"

    kaynak = (KOK / "app" / "main.py").read_text(encoding="utf-8")
    assert kaynak.count("threading.Thread(target=_scheduler_loop") == 1


def test_ESIK_MANTIGI_BU_MODULUN_ISI_DEGIL():
    """`asim_zamani` bir **çağrılabilirdir**: eşiğin ne zaman aşıldığını bilmek bu modülün
    işi **değildir** (o `schedules.py`'nin). Buraya bir sorgu koymak, eşik mantığının
    **ikinci bir sahibini** doğururdu."""
    import inspect

    assert "asim_zamani" in inspect.signature(E.kurallari_degerlendir).parameters
    kaynak = (KOK / "app" / "eskalasyon.py").read_text(encoding="utf-8")
    assert "select(" not in kaynak, "eskalasyon kendi eşik sorgusunu yazmış — iki sahip"


# ── 5 · DÖNGÜ GİRİŞİ FAIL-SAFE ──────────────────────────────────────────────

class _Bos:
    pass


def test_KURAL_YOKSA_SESSIZCE_SIFIR():
    """Eskalasyon **yapılandırılmamış** bir tenant için bu bir hata değil bir **durumdur**.
    Uyarı basmak, kurmamayı bir **kusur** gibi gösterirdi."""
    assert E.dongude_degerlendir(_Bos()) == 0


def test_DONGU_HATASI_SCHEDULERI_DUSURMUYOR():
    """Eskalasyon bir **yardımcı** işlevdir; onun hatası zamanlanmış raporları
    durduramaz — döngü `except`'i `main.py`'de **ayrı** bir blokta."""
    kaynak = (KOK / "app" / "main.py").read_text(encoding="utf-8")
    i = kaynak.index("dongude_degerlendir")
    assert "except Exception" in kaynak[i:i + 400]
    assert E.dongude_degerlendir(None) == 0


# ── 6 · MODEL + GÖÇ ─────────────────────────────────────────────────────────

def test_MODEL_DORT_ALANI_TASIYOR():
    from control_plane.models import EskalasyonKurali

    for alan in ("tetikleyici_esik", "sure_dakika", "hedef_rol", "otomatik_kilitle"):
        assert alan in EskalasyonKurali.model_fields, alan


def test_ALEMBIC_TEK_HEAD():
    """Yeni göç zinciri **çatallamamalı** — `alembic upgrade head` patlarsa Postgres
    dağıtımı göç **edemez**."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(KOK / "alembic.ini"))
    cfg.set_main_option("script_location", str(KOK / "migrations"))
    assert len(ScriptDirectory.from_config(cfg).get_heads()) == 1
