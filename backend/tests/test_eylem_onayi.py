"""FAZ H — ONAYLI YAZMA AKSİYONLARI: *"agentic'in asıl kilidi"*.

## Ölçülen kusur (3 Ağustos 2026 — bu fazdan ÖNCE)

    "her pazartesi bu raporu bana yolla"  → source=rule, **SQL ÜRETTİ**, 1 satır
    "bu raporu her sabah 8'de e-postala"  → source=rule, **SQL ÜRETTİ**, 1 satır
    "bunu panoya ekle"                    → *"«bunu» yerine «gunu» mi demek istedin?"*
    "şunu panoya kaydet"                  → *"«kaydet» yerine «adet» mi demek istedin?"*

Ajan yazmıyordu ama **uyduruyordu**. Bu süit o kusuru kapıya çevirir ve kademeli onayın
üç korumasını kilitler.
"""

from __future__ import annotations

import pytest

from app import eylem
from tests.conftest import ask

TABAN_SORU = "bu yıl makine bazında oee"

EYLEM_IFADELERI = [
    "her pazartesi bu raporu bana yolla",
    "bu raporu her sabah 8'de e-postala",
    "bunu panoya ekle",
    "şunu panoya kaydet",
    "bu raporu her gün gönder",
]


@pytest.fixture
def taban(client):
    d = ask(client, TABAN_SORU)
    assert d.get("cube_query"), "taban rapor üretilemedi — ölçüm önkoşulu yok"
    return d


# --- 1) SINIF VAR: eylem ifadesi VERİ SORUSU DEĞİLDİR -------------------------------

@pytest.mark.parametrize("q", EYLEM_IFADELERI)
def test_EYLEM_SQL_URETMEZ(client, taban, q):
    """Ölçülen kusurun doğrudan kapısı: 0 SQL, 0 LLM."""
    d = ask(client, q, cube_query=taban["cube_query"])
    assert d.get("source") == "eylem", f"eylem sınıfına düşmedi: {d.get('source')}"
    assert not d.get("sql"), "eylem ifadesi SQL ÜRETTİ (uydurma cevap)"
    assert not str(d.get("source") or "").startswith("llm"), "eylem ifadesi LLM'e gitti"


@pytest.mark.parametrize("q", EYLEM_IFADELERI)
def test_CUBE_QUERY_DEGISMEZ(client, taban, q):
    """Ürün sözleşmesi #1: konuşma turu **yeni sorgu yazmaz**, mevcut makbuza çapalanır."""
    d = ask(client, q, cube_query=taban["cube_query"])
    assert d.get("cube_query") == taban["cube_query"], "eylem turu raporu DEĞİŞTİRDİ"


# --- 2) ÖNERİ = DOĞRULANMIŞ SORGU (argümanlar LLM'den GELMEZ) ----------------------

def test_ONERI_ARGUMANLARI_KONUSMADAN_gelir(client, taban):
    d = ask(client, "bunu panoya ekle", cube_query=taban["cube_query"])
    oneri = d.get("eylem_onerisi")
    assert oneri, "öneri üretilmedi"
    assert oneri["argumanlar"]["cube_query"] == taban["cube_query"], \
        "öneri BAŞKA bir sorgu taşıyor — uydurma sorgu kalıcılaşabilirdi"
    assert oneri["eylem"] == eylem.PANO_EKLE
    assert oneri["izin"] == "query:run"


def test_ZAMANLAMA_ARGUMANLARI_IFADEDEN_cozulur(client, taban):
    d = ask(client, "her pazartesi saat 09:00'da bu raporu yolla",
            cube_query=taban["cube_query"])
    args = d["eylem_onerisi"]["argumanlar"]
    assert args["every"] == "week" and args["weekday"] == 1, args
    assert args["at"] == "09:00", f"saat ifadeden çözülmedi: {args}"
    assert args["cube_query"] == taban["cube_query"]


def test_GERI_ALINAMAZ_isaretlenir(client, taban):
    """Plan: *"geri alınamaz iş → senkron onay"*. Bayrak UI'ın dilini belirler; bir
    zamanlama kurulduktan sonra gönderilmiş e-posta geri alınamaz."""
    d = ask(client, "her gün bu raporu yolla", cube_query=taban["cube_query"])
    assert d["eylem_onerisi"]["geri_alinabilir"] is False
    d2 = ask(client, "bunu panoya ekle", cube_query=taban["cube_query"])
    assert d2["eylem_onerisi"]["geri_alinabilir"] is True


# --- 3) ÇAPA YOKSA ÖNERİ DE YOK — ama SESSİZ DEĞİL ---------------------------------

@pytest.mark.parametrize("q", EYLEM_IFADELERI)
def test_CAPASIZ_eylem_URETMEZ_ama_NEDENINI_soyler(client, q):
    d = ask(client, q)                       # bağlam YOK
    assert d.get("eylem_onerisi") is None, "çapa yokken öneri üretildi"
    assert not d.get("sql"), "çapasız eylem SQL üretti"
    assert "önce bir rapor" in (d.get("note") or ""), \
        f"sessizce düştü (not={d.get('note')!r}) — kullanıcı neden olmadığını bilemez"


def test_DESTEKLENMEYEN_periyot_DURUSTCE_soylenir(client, taban):
    """*"her ay yolla"* → `ScheduleRequest` hour|day|week destekler. Sessizce haftalığa
    çevirmek, kullanıcının İSTEMEDİĞİ bir zamanlama kurmak olurdu."""
    d = ask(client, "her ay bu raporu bana yolla", cube_query=taban["cube_query"])
    assert d.get("eylem_onerisi") is None, "desteklenmeyen periyot yine de kuruldu"
    not_ = (d.get("note") or "").lower()
    assert "saatlik" in not_ and "haftalık" in not_, \
        f"ne YAPABİLDİĞİMİZ söylenmedi: {d.get('note')!r}"


# --- 4) KAPI DAR: meşru veri soruları eylem SANILMAZ -------------------------------

@pytest.mark.parametrize("q", [
    "her ay ciro",                       # yinelenme VAR, teslim fiili YOK → granülerlik
    "her gün üretim miktarı",            # aynı sınıf
    "bir de fire ekle",                  # `ekle` var, `pano` YOK → kompozisyon (§9.2)
    "makine bazında göster",
    "bu yıl makine bazında oee",
])
def test_VERI_SORUSU_eylem_SANILMAZ(client, q):
    d = ask(client, q)
    assert d.get("source") != "eylem", f"meşru veri sorusu eylem sanıldı: {q!r}"


def test_YINELENME_TEK_BASINA_yetmez():
    """Kapı iki kanatlı olmalı — tek kanatlı olsaydı *"her ay ciro"* zamanlama sanılırdı."""
    assert eylem.tespit("her ay ciro") is None
    assert eylem.tespit("her pazartesi") is None            # fiil yok
    assert eylem.tespit("bana yolla") is None               # yinelenme yok
    assert eylem.tespit("her pazartesi yolla") == eylem.ZAMANLA


# --- 5) ONAY UCU: üç koruma --------------------------------------------------------

def test_ONAY_UYDURMA_EYLEMI_REDDEDER(client, taban):
    """Fail-closed: yazma yüzeyi `EYLEM_KAYIT`'ın boyu kadardır."""
    r = client.post("/ask/eylem", json={
        "eylem": "measures.approve",
        "argumanlar": {"cube_query": taban["cube_query"]}})
    assert r.status_code == 400, r.text
    assert "Kayıtlı olmayan eylem" in r.text


def test_ONAY_BOS_SORGUYU_REDDEDER(client):
    r = client.post("/ask/eylem", json={"eylem": eylem.PANO_EKLE, "argumanlar": {}})
    assert r.status_code == 400, r.text


def test_ONAY_PANOYA_EKLER_ve_AUDIT_yazar(client, taban):
    d = ask(client, "bunu panoya ekle", cube_query=taban["cube_query"])
    oneri = d["eylem_onerisi"]
    r = client.post("/ask/eylem", json={"eylem": oneri["eylem"],
                                        "argumanlar": oneri["argumanlar"],
                                        "bilet": oneri.get("bilet", "")})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["ok"] and out["id"], out
    # Widget GERÇEKTEN kalıcı mı — cevabın kendisine değil, DEPOYA bak.
    panolar = client.get("/dashboards").json()["dashboards"]
    assert panolar, "pano oluşturulmadı"
    detay = client.get(f"/dashboards/{panolar[0]['id']}").json()
    assert any(w["id"] == out["id"] for w in detay["widgets"]), detay

    from control_plane.audit import AuditLog
    from control_plane.db import engine
    from sqlmodel import Session, select

    with Session(engine) as s:
        satirlar = [a for a in s.exec(select(AuditLog)).all() if a.action == "eylem_onay"]
    assert satirlar, "onay AYRI bir audit satırı yazmadı — yönetişim 'kim istedi'yi bilemez"
    assert eylem.PANO_EKLE in (satirlar[-1].nl_question or "")


def test_ONAY_ZAMANLAMA_KURAR(client, taban):
    d = ask(client, "her pazartesi bu raporu yolla", cube_query=taban["cube_query"])
    oneri = d["eylem_onerisi"]
    r = client.post("/ask/eylem", json={"eylem": oneri["eylem"],
                                        "argumanlar": oneri["argumanlar"],
                                        "bilet": oneri.get("bilet", "")})
    assert r.status_code == 200, r.text
    kayitlar = client.get("/schedules").json()["schedules"]
    assert any(s.get("every") == "week" and s.get("weekday") == 1 for s in kayitlar), kayitlar


def test_YETKISIZ_KULLANICI_ONAYLAYAMAZ(client, taban):
    """TOCTOU koruması + rol matrisi: `schedule:create` analyst+ ister; viewer öneriyi
    GÖRSE bile onaylayamaz. Öneri yeni YETKİ yaratmaz — bu, kurcalanmasının neden
    zararsız olduğunun da kanıtıdır."""
    from fastapi.testclient import TestClient

    from tests.conftest import make_tenant_user

    make_tenant_user("eylem-viewer@dima.local", "viewer-parola-1", "viewer")
    c = TestClient(client.app)
    tok = c.post("/auth/login", json={"email": "eylem-viewer@dima.local",
                                      "password": "viewer-parola-1"}).json()["access_token"]
    c.headers["Authorization"] = f"Bearer {tok}"
    args = {"label": "x", "cube_query": taban["cube_query"],
            "every": "week", "at": "08:00", "weekday": 1}
    # ⚠ Bilet **mint edilir**: bu testin konusu YETKİ, süre değil — ve gerçek bir istemci
    # her zaman bir bilet taşır (öneriyle birlikte gelir). Biletsiz göndermek, testi
    # istemeden bir *"bilet kapısı"* testine çevirirdi.
    from app import onay_akisi

    r = c.post("/ask/eylem", json={"eylem": eylem.ZAMANLA, "argumanlar": args,
                                   "bilet": onay_akisi.bilet(eylem.ZAMANLA)})
    assert r.status_code == 403, r.text
    # …ama PANO eylemi (izin=query:run) viewer'a AÇIK olmalı: yetki eşiği eylemin
    # kendi riskinden gelir, "yazma" etiketinden değil.
    r2 = c.post("/ask/eylem", json={"eylem": eylem.PANO_EKLE,
                                    "argumanlar": {"title": "v",
                                                   "cube_query": taban["cube_query"]},
                                    "bilet": onay_akisi.bilet(eylem.PANO_EKLE)})
    assert r2.status_code == 200, r2.text


# --- 6) KAYIT DÜRÜSTLÜĞÜ -----------------------------------------------------------

def test_IZINLER_MATRISTE_VAR():
    """`tools.py`'nin kendi kapısıyla aynı: kayıt, matriste OLMAYAN bir izne bağlanamaz."""
    from control_plane.authorize import _ACTION_MIN_RANK

    for b in eylem.EYLEM_KAYIT:
        assert b.izin in _ACTION_MIN_RANK, f"{b.ad}: matriste olmayan izin {b.izin!r}"


def test_YAZMA_ARACLARI_HALA_AJANA_KAPALI():
    """Bu faz yasağı KALDIRMADI, kademelendirdi.

    🔴🔴 **KAPI BAYRAĞA KÖRDÜ — ve o yüzden BİR YAPILANDIRMADA HEP KIRMIZIYDI**
    (⟳ 2026-08-12, `§F13` denetimi). Yüklem `tools.KAYIT`'ta hiç yazan olmamasını
    istiyordu; oysa `yazma_araclari` bayrağı **tam da onları kayda almak için** var.
    Bayrak varsayılan olarak kapalı olduğu için kapı hiç bu hâliyle koşmadı — ve
    kırmızı olduğunu **kimseye söylemedi**.

    ⊙ Ölçüldü (bayrak açık): `KAYIT` yazanları `['dashboards.create',
    'schedules.create', 'preferences.set']`; `llm_araclari()` **üçünü de** taşıyor,
    `okuyan_araclar()` **hiçbirini**. Yani Faz H'nin gerçek değişmezi *«ajan görmesin»*
    değil, *«ajan önerebilsin ama SALT-OKUMA yüzeyleri taşımasın ve çağrı onaydan
    geçsin»*tir — `mcp.cagir` `yan_etki != "yok"` olanı **reddediyor** (`mcp.py:100`).

    ✅ Yüklem artık **iki yapılandırmayı da** ölçüyor; hangisi koşarsa koşsun bir şey
    iddia ediyor. *Yalnız tek bir yapılandırmada anlamlı olan bir kapı, öteki
    yapılandırmada bir kapı değildir.*
    """
    from app import tools
    from app.config import get_settings

    acik = str(getattr(get_settings(), "yazma_araclari", "") or "").lower() in (
        "1", "true", "on", "yes")
    yazanlar = {a.ad for a in tools.KAYIT if a.yan_etki == "yazar"}

    if not acik:
        assert not yazanlar, (
            f"🔴 bayrak KAPALI ama yazma aracı kayda sızmış: {sorted(yazanlar)} — "
            "`KURAL B` ihlali; onay kademesi ATLANABİLİR")
        return

    # Bayrak açık: yazan araçlar kayıtta **olmalı** (yoksa öneri üretilemez), ama
    # salt-okuma yüzeyinde **olmamalı** ve doğrudan çağrı **reddedilmeli**.
    assert yazanlar, (
        "⊘ ölçüm tabanı çöktü: bayrak açık ama kayıtta hiç yazan araç yok — bu kapı "
        "hiçbir şey ölçmüyor")
    salt_okuma = {d["name"] for d in tools.okuyan_araclar(None)}
    assert not (yazanlar & salt_okuma), (
        f"🔴 yazma aracı SALT-OKUMA yüzeyine sızmış: {sorted(yazanlar & salt_okuma)} — "
        "MCP/dış yüzey üzerinden onay ATLANABİLİR")


def test_ONAY_UCU_DOGRULAMAYI_IKINCI_KEZ_YAZMAZ():
    """Bu deponun bir numaralı kusur sınıfı: aynı kuralı ikinci kez yazmak. Onay ucu
    `parse_cube_query`/e-posta denetimini KENDİ İÇİNDE yapmamalı — var olan handler'ı
    çağırmalı ki kurallar zamanla ayrışmasın."""
    import ast
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[1] / "app" / "routers" / "eylem.py"
    agac = ast.parse(src.read_text(encoding="utf-8"))
    cagrilar = {n.func.attr for n in ast.walk(agac)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    adlar = {n.id for n in ast.walk(agac) if isinstance(n, ast.Name)}
    assert "parse_cube_query" not in cagrilar and "parse_cube_query" not in adlar, \
        "onay ucu katalog doğrulamasını KOPYALAMIŞ"
    assert {"add_widget", "create_schedule"} <= adlar, \
        "onay ucu var olan handler'ları çağırmıyor"


def test_FRONTEND_TUKETICISI_var():
    """Yetim alan kapısı: `eylem_onerisi` bir tüketicisi olmadan BİTMİŞ değildir."""
    import pathlib

    fe = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    metin = "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                      for f in fe.rglob("*.ts*"))
    assert "eylem_onerisi" in metin, "öneri alanı frontend'de HİÇ okunmuyor"
    assert "/ask/eylem" in metin, "onay ucu frontend'den HİÇ çağrılmıyor"
    assert "Onayla" in metin or "onayla" in metin, "onay düğmesi yok"


def test_FRONTEND_IZIN_HARITASI_KAYITLA_ORTUSUR():
    """Onay düğmesi yetkiye bağlı gösterilir ve React hook sırası sabit kalsın diye
    frontend izinleri BAŞTAN çözer. Kayda yeni bir izin eklenip frontend haritası
    güncellenmezse düğme SESSİZCE kaybolurdu — kullanıcı ürünü yeteneksiz sanardı."""
    import pathlib
    import re

    fe = (pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master"
          / "src" / "components" / "ReportCard.tsx")
    if not fe.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    src = fe.read_text(encoding="utf-8")
    govde = re.search(r"const izinliMi[\s\S]{0,400}?;", src)
    assert govde, "izinliMi haritası bulunamadı"
    for b in eylem.EYLEM_KAYIT:
        assert f'"{b.izin}"' in govde.group(0), \
            f"{b.ad}: {b.izin!r} frontend izin haritasında YOK → düğme hiç çıkmaz"
