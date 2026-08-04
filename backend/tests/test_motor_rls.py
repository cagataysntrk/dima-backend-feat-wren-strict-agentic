"""FAZ 1.1 — **MOTOR-SEVİYESİ RLS** kapısı.

Ön koşul (motorun yeteneği) `tests/test_motor_rls_onkosul.py`'de ölçülüp donduruldu.
Bu dosya **bizim** tarafımızı kilitler: çeviri doğru mu, `off` birebir mi, iki sahip
oluşuyor mu, ve ölçülen iki baypas gerçekten kapanıyor mu.
"""

from __future__ import annotations

import base64
import json
import pathlib

import pytest

from app import rls

KOK = pathlib.Path(__file__).resolve().parents[1]
GULTEKS = KOK / "demo" / "wren-projects" / "gulteks" / "target" / "mdl.json"


def _ham() -> bytes:
    if not GULTEKS.exists():
        pytest.skip("gulteks manifesti derlenmemiş")
    return GULTEKS.read_bytes()


# ── 1 · KURAL B: `off` BİREBİR ───────────────────────────────────────────────

def test_OFF_MANIFESTE_HIC_DOKUNMUYOR():
    """🔴 **KURAL B.** `off` → bayt bayt aynı manifest. `is` değil `==` yetmez: aynı
    baytlar dönmeli ki base64 ve motor önbelleği de aynı kalsın."""
    ham = _ham()
    yeni, n = rls.manifeste_yaz(ham, kademe="off")
    assert yeni == ham and n == 0


def test_SHADOW_DA_SERVIS_EDILEN_MANIFESTE_DOKUNMUYOR():
    """🔴 **GÖLGE ÖLÇER, DAVRANMAZ — ve bu bir düzeltmedir.**

    İlk sürüm `shadow`'da da manifeste yazıyordu; o hâlde motor filtreyi **uygular** ve
    **ham SQL yolundaki cevap DEĞİŞİRDİ**. Yani "gölge" adı altında canlı bir davranış
    değişikliği sevk edilirdi.

    ⚠ **801 yeşil test bunu YAKALAMADI:** `alwaysFilter` yalnız gulteks'te var ve süit o
    tenant'ın ham-SQL yolunu ölçmüyor. Yeşil bir süit, **ölçmediği** bir davranış hakkında
    hiçbir şey söylemez — bu test tam o boşluğu kapatıyor.
    """
    ham = _ham()
    yeni, n = rls.manifeste_yaz(ham, kademe="shadow")
    assert yeni == ham and n == 0, (
        "gölge kademesi manifesti DEĞİŞTİRİYOR — servis edilen cevap kayar ve ölçüm bir "
        "kıyas olmaktan çıkar (`strict_sql_policy`'nin gölge deseniyle çelişir)")


def test_GOLGE_MANIFESTI_AYRICA_URETILEBILIYOR():
    """Gölge **kıyas** yapabilmeli: RLAC'lı manifest kademeden bağımsız üretilir."""
    ham = _ham()
    golge, n = rls.rlac_manifesti(ham)
    assert n >= 1 and golge != ham


def test_GECERSIZ_KADEME_HATA_VERIR():
    """Sessizce `off`'a düşmek, *"açtım ama çalışmıyor"* hâlini **sessiz** yapardı."""
    with pytest.raises(ValueError):
        rls.manifeste_yaz(_ham(), kademe="acik")


# ── 2 · ÇEVİRİ ───────────────────────────────────────────────────────────────

def test_ALWAYS_FILTER_MODEL_RLAC_INE_CEVRILIYOR():
    """Cube `alwaysFilter` → **model** RLAC. Model düzeyi bilinçli: iki baypasın ikisi de
    (join `__source`'ta, ham SQL modele doğrudan) **model** seviyesinde oluyor."""
    ham = _ham()
    yeni, n = rls.manifeste_yaz(ham, kademe="on")
    assert n >= 1, "gulteks 3 `alwaysFilter` taşıyor — çeviri hiç kural üretmedi"
    m = json.loads(yeni)
    kurallı = {mm["name"]: mm[rls.MODEL_ANAHTARI] for mm in m["models"]
               if mm.get(rls.MODEL_ANAHTARI)}
    assert kurallı, "hiçbir modele RLAC yazılmadı"
    for _ad, kurallar in kurallı.items():
        for k in kurallar:
            assert k["condition"], k
            assert k["requiredProperties"] == [], (
                "sabit yükleme session property iliştirilmiş — uydurma bir bağımlılık")


def test_CEVRILEN_KURAL_SAYISI_KAYNAKLA_TUTUYOR():
    """Kaynak sayısı ile hedef sayısı ayrışırsa bir cube **sessizce** kapsanmamış olur."""
    ham = _ham()
    kaynak = json.loads(ham)
    beklenen_modeller = {
        (c.get("base_object") or c.get("baseObject"))
        for c in kaynak.get("cubes") or []
        if c.get("always_filter") or c.get("alwaysFilter")
    } & {m["name"] for m in kaynak.get("models") or []}
    uretilen = set(rls.always_filter_kurallari(kaynak))
    assert uretilen == beklenen_modeller, (uretilen, beklenen_modeller)


def test_AYNI_MODELE_IKI_CUBE_TEKILLESTIRILIYOR():
    """Aynı yüklem iki cube'dan gelirse **tek kez** yazılır; **farklı** yüklemler
    ikisi de yazılır ve motor onları `AND`'ler (ölçüldü). Birini seçmek, ötekinin
    kullanıcısına sessizce **fazla satır** göstermek olurdu."""
    man = {
        "models": [{"name": "m"}],
        "cubes": [
            {"name": "a", "baseObject": "m", "alwaysFilter": "x = 0"},
            {"name": "b", "baseObject": "m", "alwaysFilter": "x = 0"},
            {"name": "c", "baseObject": "m", "alwaysFilter": "y = 1"},
        ],
    }
    kurallar = rls.always_filter_kurallari(man)["m"]
    assert [k["condition"] for k in kurallar] == ["x = 0", "y = 1"]
    assert len({k["name"] for k in kurallar}) == 2, "kural adları çakışıyor"


def test_MODELI_OLMAYAN_CUBE_ATLANIYOR():
    """`baseObject` manifestte yoksa kural **yazılmaz**: olmayan bir modele RLAC yazmak,
    motorun reddedeceği bir manifest üretir ve **tüm** sorguları düşürürdü."""
    man = {"models": [{"name": "m"}],
           "cubes": [{"name": "a", "baseObject": "YOK", "alwaysFilter": "x = 0"}]}
    assert rls.always_filter_kurallari(man) == {}


# ── 3 · FAIL-OPEN DESENLERİ REDDEDİLİYOR ─────────────────────────────────────

def test_DEFAULT_EXPR_REDDEDILIYOR():
    """🔴 **Ölçülmüş fail-open.** `required=False` + `defaultExpr` verilirse property
    **hiç gönderilmese bile** sorgu varsayılanla koşar (`WHERE tenant = 'HERKES'`).
    Kimlik enjeksiyonunu unuttuğumuz gün sistem **hata vermez**, başka bir filtreyle
    cevap verir — ve bu, filtresiz cevaptan **daha sinsidir** çünkü sonuç makul görünür.
    """
    kotu = [{"name": "k", "condition": "t = @s",
             "requiredProperties": [{"name": "s", "required": False,
                                     "defaultExpr": "'HERKES'"}]}]
    ihlaller = rls.kurallari_denetle(kotu)
    assert any("defaultExpr" in i for i in ihlaller), ihlaller


def test_REQUIRED_FALSE_REDDEDILIYOR():
    kotu = [{"name": "k", "condition": "t = @s",
             "requiredProperties": [{"name": "s", "required": False}]}]
    assert rls.kurallari_denetle(kotu), "required=False sessizce geçti"


def test_SAGLAM_KURAL_IHLAL_URETMIYOR():
    saglam = [{"name": "k", "condition": "t = @s",
               "requiredProperties": [{"name": "s", "required": True}]}]
    assert rls.kurallari_denetle(saglam) == []


# ── 4 · İKİ SAHİP OLMAZ ──────────────────────────────────────────────────────

def test_ON_KADEMESINDE_UYGULAMA_KATMANI_ELINI_CEKIYOR():
    """`on` → sahip motordur; `_inject_always_filter` o cube'a dokunmaz."""
    devir = rls.motorun_devraldigi_cubelar(_ham(), kademe="on")
    assert devir, "on kademesinde hiçbir cube devralınmadı — çift uygulama olurdu"


def test_SHADOW_KADEMESINDE_SAHIP_UYGULAMA_KATMANINDA_KALIYOR():
    """🔴 **Gölgenin işi ÖLÇMEK, davranmak değil.** Servis edilen cevap `off` ile birebir
    aynı olmalı ki ölçüm bir **kıyas** olabilsin. `strict_sql_policy`'nin gölge deseniyle
    aynı karar — orada da katı motor **paralel** koşuyor, servis etmiyor."""
    assert rls.motorun_devraldigi_cubelar(_ham(), kademe="shadow") == set()
    assert rls.motorun_devraldigi_cubelar(_ham(), kademe="off") == set()


# ── 5 · MOTOR GERÇEKTEN UYGULUYOR (uçtan uca) ────────────────────────────────

def _ctx(manifest_bytes: bytes):
    wc = pytest.importorskip("wren_core")
    return wc.SessionContext(base64.b64encode(manifest_bytes).decode(), None, None,
                             "duckdb")


def test_UCTAN_UCA_HAM_SQL_DE_FILTRELENIYOR():
    """🔴 **Baypas 2: Discovery ham SQL'i.** `_inject_always_filter` yalnız `cube_sql()`
    yolundan çağrılır; ham SQL o fonksiyona **hiç uğramaz**. Motor RLS'inde uğramasına
    gerek yok — koşul modelin kendisinde."""
    yeni, n = rls.manifeste_yaz(_ham(), kademe="on")
    if not n:
        pytest.skip("çevrilecek kural yok")
    m = json.loads(yeni)
    hedef = next(mm for mm in m["models"] if mm.get(rls.MODEL_ANAHTARI))
    kosul = hedef[rls.MODEL_ANAHTARI][0]["condition"].split("=")[0].strip()
    sql = _ctx(yeni).transform_sql(f'SELECT * FROM "{hedef["name"]}"')
    assert kosul.lower() in sql.lower(), (
        f"ham SQL'de `{kosul}` koşulu YOK — baypas kapanmamış:\n{sql[:400]}")


def test_UCTAN_UCA_JOIN_BAYPAS_EDEMIYOR():
    """🔴 **Baypas 1: JOIN.** `compose.py:434` (G10) birebir yazıyor: *"filtreli bir
    modele join'lemek `always_filter`'ı BAYPAS EDER"*. Motor RLS'inde filtre join'in
    **iki tarafına da** iner."""
    yeni, n = rls.manifeste_yaz(_ham(), kademe="on")
    if not n:
        pytest.skip("çevrilecek kural yok")
    m = json.loads(yeni)
    hedef = next(mm for mm in m["models"] if mm.get(rls.MODEL_ANAHTARI))
    kosul = hedef[rls.MODEL_ANAHTARI][0]["condition"].split("=")[0].strip()
    ad = hedef["name"]
    kolon = hedef["columns"][0]["name"]
    sql = _ctx(yeni).transform_sql(
        f'SELECT a."{kolon}" FROM "{ad}" a JOIN "{ad}" b ON a."{kolon}" = b."{kolon}"')
    assert sql.lower().count(kosul.lower()) >= 2, (
        f"filtre join'in iki tarafına inmedi:\n{sql[:500]}")
