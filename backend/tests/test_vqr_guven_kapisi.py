"""FAZ 4.1 — VQR güven kapısı: incelenmemiş ham SQL TEKRAR OYNATILMAZ.

BULUNAN KUSUR (kod okunarak, 2 Ağustos 2026): `ask.py`'nin Discovery bloğu, başarılı HER
bağımsız cevabı ham LLM SQL'iyle birlikte `source="auto"` olarak VQR'a yazıyordu ve
`near_exact` kaynağa **bakmıyordu**. Sonuç: LLM'in kendi tahmini, insan onaylı bir kayıtla
**aynı otoriteyle**, üstelik yalnızca BENZER (birebir değil — eşik 0,92 embedding / 0,85
sözlüksel) bir soru için birebir tekrar oynatılıyordu.

Neden ciddi: ham SQL semantik katmanın yönetmediği kolonlara/filtrelere erişebilir ve
`always_filter` baypası (MIMARI.md §6.3) bu yolla **öğrenilmiş** hale gelir. Planın
alıntıladığı Snowflake uyarısı tam bu vakadır: *kötü kayıt doğruluğu aktif olarak düşürür.*

TASARIM — iki mekanizma AYNI riskte değil, aynı kapıdan geçmiyorlar:
  `near_exact`      → saklanan SQL'i birebir, yeniden doğrulanmadan çalıştırır → TAM blast
                      radius → yalnız güvenilir kaynaklar.
  `few_shot_block`  → bir üretece örnek verir, çıktısı ayrıca doğrulanır → dolaylı → hepsi.

Güvenilmez kayıt **silinmez**: terfi kuyruğunun ham maddesidir ve few-shot değeri taşır.
"""

from __future__ import annotations

import json

import pytest

from app import vqr as vqr_mod


@pytest.fixture
def depo(monkeypatch):
    """DB'siz VQR — bu dosya DEPOLAMAYI değil GÜVEN KARARINI sınar."""
    v = vqr_mod.VQR(company="test-guven")
    v._pairs = []
    monkeypatch.setattr(v, "_db_upsert", lambda *a, **k: None)
    monkeypatch.setattr(v, "_db_soft_delete", lambda *a, **k: None)
    return v


SQL = "SELECT 1"


def _payload():
    return {"wren_sql": SQL, "mdl_version": "v1"}


@pytest.mark.parametrize("source", sorted(vqr_mod._TRUSTED_SOURCES))
def test_guvenilir_kaynak_TEKRAR_OYNATILIR(depo, source):
    depo.store("bu yıl ciro", _payload(), source=source)
    hit = depo.near_exact("bu yıl ciro")
    assert hit and hit["source"] == source


@pytest.mark.parametrize("source", ["auto_discovery", "auto"])
def test_guvenilmez_kaynak_TEKRAR_OYNATILMAZ(depo, source):
    """`auto_discovery` incelenmemiş ham SQL'dir. `auto` ise ayrım ÖNCESİ eski kayıttır ve
    kökeni kayıtta YOK — bir kısmı ham Discovery SQL'i. Bilinmeyen köken güvenilir
    sayılamaz; tahmin etmek, güvenilmez kayıtları güvenilir saymak demek olurdu."""
    depo.store("bu yıl ciro", _payload(), source=source)
    assert depo.near_exact("bu yıl ciro") is None


def test_BIREBIR_soru_bile_kapidan_muaf_degil(depo):
    """Aynı soruyu ikinci kez soran kullanıcı, ilk seferde LLM'in ürettiği İNCELENMEMİŞ
    SQL'i "doğrulanmış" rozetiyle geri almamalıdır — o cevap hiç incelenmedi. Kapı
    yalnız bulanık eşleşmeye konulsaydı en sık vaka (aynı soruyu tekrar sormak) açık
    kalırdı."""
    depo.store("bu yıl ciro", _payload(), source="auto_discovery")
    assert depo.near_exact("bu yıl ciro") is None


def test_guvenilmez_kayit_DEPODA_KALIR(depo):
    """Silinmiyor — terfi kuyruğunun ham maddesi ve few-shot değeri taşıyor. Kapı
    "unut" değil "tekrar oynatma" kapısıdır."""
    depo.store("bu yıl ciro", _payload(), source="auto_discovery")
    assert len(depo._load()) == 1
    assert depo.recall("bu yıl ciro", k=3), "geri çağırma da kapanmış"


def test_guvenilmez_kayit_FEW_SHOT_ta_kalir(depo):
    """Örnek gösterme ayrı kapıdan geçer: üretecin çıktısı ayrıca doğrulanır."""
    depo.store("bu yıl ciro", _payload(), source="auto_discovery")
    assert SQL in depo.few_shot_block("bu yıl ciro")


def test_guvenilmez_kayit_guvenilir_olani_GOLGELEMEZ(depo):
    """Kritik: filtre "en iyi skoru bul, sonra güvenilir mi bak" şeklinde yazılsaydı,
    güvenilmez bir kayıt daha yüksek skor aldığında güvenilir eşleşme kaybolurdu.
    Sıralama GÜVENİLİR ADAYLAR ARASINDA yapılmalı."""
    depo.store("bu yil ciro nedir acaba", _payload(), source="auto_discovery")
    depo.store("bu yıl ciro", {"wren_sql": "SELECT 2", "mdl_version": "v1"},
               source="user_verified")
    hit = depo.near_exact("bu yıl ciro")
    assert hit and hit["cube_query"]["wren_sql"] == "SELECT 2"


def test_hic_guvenilir_kayit_yokken_PATLAMAZ(depo):
    depo.store("bu yıl ciro", _payload(), source="auto_discovery")
    assert depo.near_exact("tamamen alakasız bir soru") is None


def test_verified_at_yalniz_INSAN_onayinda(monkeypatch):
    """Otomatik yazım bir DOĞRULAMA değildir ve öyleymiş gibi görünmemelidir."""
    yazilan = {}

    class _Row:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    v = vqr_mod.VQR(company="test-guven")
    v._pairs = []

    def _sahte_upsert(question, qn, cq, source, meta):
        vat = (vqr_mod.datetime.utcnow()
               if source in ("user_verified", "chip_approved") else None)
        yazilan[source] = vat

    monkeypatch.setattr(v, "_db_upsert", _sahte_upsert)
    for src in ("user_verified", "chip_approved", "auto_cube", "auto_discovery"):
        v.store(f"soru {src}", _payload(), source=src)
    assert yazilan["user_verified"] is not None
    assert yazilan["chip_approved"] is not None
    assert yazilan["auto_cube"] is None
    assert yazilan["auto_discovery"] is None


def test_ask_cagri_yerleri_AYRISMIS():
    """Kaynak ayrımı `ask.py`'de gerçekten yapıldı mı — kapı, ancak yazan taraf doğru
    etiketi koyarsa iş görür."""
    from pathlib import Path

    s = Path(vqr_mod.__file__).parent.joinpath("routers", "ask.py").read_text(encoding="utf-8")
    assert 'source="auto")' not in s, "hâlâ ayrışmamış `auto` yazımı var"
    assert 'source="auto_cube")' in s
    assert 'source="auto_discovery")' in s


def test_model_alanlari_ve_gocu_VAR():
    """Şema alanları + alembic göçü birlikte gitmeli; biri eksikse üretimde patlar."""
    from pathlib import Path

    from control_plane.models import VerifiedQuery

    alanlar = VerifiedQuery.model_fields
    assert "verified_at" in alanlar and "use_as_onboarding_question" in alanlar
    goc = Path(vqr_mod.__file__).parents[1] / "migrations" / "versions"
    metinler = " ".join(f.read_text(encoding="utf-8") for f in goc.glob("*.py"))
    assert "use_as_onboarding_question" in metinler, "alan eklendi ama göç yazılmadı"


def test_gocler_TEK_HEAD(monkeypatch):
    """İki head = `alembic upgrade head` üretimde patlar. Yeni göç zincire eklendi mi?"""
    import re
    from pathlib import Path

    d = Path(vqr_mod.__file__).parents[1] / "migrations" / "versions"
    revs, downs = set(), set()
    for f in d.glob("*.py"):
        t = f.read_text(encoding="utf-8")
        if m := re.search(r"^revision(?::\s*str)?\s*=\s*[\"']([^\"']+)", t, re.M):
            revs.add(m.group(1))
        if m := re.search(r"^down_revision(?::[^=]+)?=\s*[\"']([^\"']+)", t, re.M):
            downs.add(m.group(1))
    head = revs - downs
    assert len(head) == 1, f"birden fazla alembic head: {sorted(head)}"


def test_her_kaynak_SINIFLANDIRILMIS():
    """İZİN LİSTESİNİN BEDELİ. Güvenilirlik bir deny-list olsaydı yarın eklenecek bir
    `auto_<birşey>` sessizce GÜVENİLİR sayılırdı — bu yüzden allow-list. Ama allow-list'in
    kendi riski var: yeni bir kaynak adı sessizce ENGELLENİR ve replay bir daha hiç
    çalışmaz, kimse fark etmez. Bu test o riski kapatır: koddaki HER `source=` literali
    iki kümeden birinde olmak zorunda.
    """
    import ast
    from pathlib import Path

    # AST ile, düz metin araması DEĞİL: `source=` adı `AskResponse(source="cube")` gibi
    # TAMAMEN AYRI bir kavramda (yanıt rozeti) da geçiyor. Yalnız `<bir şey>.store(...)`
    # çağrılarının `source` argümanı bu kapıyı ilgilendirir.
    kok = Path(vqr_mod.__file__).parent
    bulunan = set()
    for f in kok.rglob("*.py"):
        if f.name == "vqr.py":
            continue
        for d in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and d.func.attr == "store"):
                continue
            for kw in d.keywords:
                if kw.arg == "source" and isinstance(kw.value, ast.Constant) \
                        and isinstance(kw.value.value, str):
                    bulunan.add(kw.value.value)
    assert bulunan, "hiç `store(source=...)` çağrısı bulunamadı — tarama bozulmuş olabilir"
    siniflandirilmamis = bulunan - vqr_mod.KNOWN_SOURCES
    assert not siniflandirilmamis, (
        f"VQR kaynağı sınıflandırılmamış: {sorted(siniflandirilmamis)} — app/vqr.py'de "
        "_TRUSTED_SOURCES / _FEW_SHOT_ONLY_SOURCES / _UNTRUSTED_SOURCES'tan birine "
        "eklenmeli. Sınıflandırılmayan bir "
        "kaynak sessizce tekrar-oynatılamaz hale gelir.")


def test_iki_kume_KESISMIYOR():
    assert not (vqr_mod._TRUSTED_SOURCES & vqr_mod._UNTRUSTED_SOURCES)
    # ⟳ FAZ 2b — üçüncü sınıf: few-shot'ta VAR, replay'de YOK.
    assert not (vqr_mod._FEW_SHOT_ONLY_SOURCES & vqr_mod._TRUSTED_SOURCES)
    assert not (vqr_mod._FEW_SHOT_ONLY_SOURCES & vqr_mod._UNTRUSTED_SOURCES)


def test_ilgisiz_json_bozulmadi(depo):
    """Depolanan payload dokunulmadan geri gelmeli (kapı içeriği değiştirmez)."""
    depo.store("bu yıl ciro", _payload(), source="user_verified")
    hit = depo.near_exact("bu yıl ciro")
    assert json.dumps(hit["cube_query"], sort_keys=True) == json.dumps(_payload(), sort_keys=True)
