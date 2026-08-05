"""Eval/golden-set test altyapısı (ADR-0004: doğruluk regresyon güvencesi).

Deterministik koşum: LLM sağlayıcısı `rule` zorlanır (ağ yok, anahtar gerekmez) —
böylece testler cube/clarify/meta/refine gibi DETERMİNİSTİK katmanları ölçer; LLM'e
bağımlı yollar ayrıca işaretlenir. Demo DuckDB + derlenmiş MDL (repo'da) kullanılır.
"""

from __future__ import annotations

import os

import pytest

# Settings @lru_cache'li — import/app kurulumundan ÖNCE ortamı sabitle.
os.environ["DIMA_LLM_PROVIDER"] = "rule"
# VQR izolasyonu: testler repo'daki doğrulanmış-çift dosyasını KİRLETMEZ.
import tempfile

os.environ["DIMA_VQR_PATH"] = os.path.join(tempfile.mkdtemp(prefix="dima-vqr-"), "queries.jsonl")
# HERMETİKLİK: VQR embedder KAPALI — testler ağa çıkmaz. `_embedder()` ilk çağrıda HF Hub'dan
# ~2.2 GB ONNX indirmeye çalışıyor; kimliksiz indirme oranlanıyor ve pratikte DURUYOR (ölçüldü:
# 20 sn'de 0 bayt, `.incomplete` 67 MB'da takılı) ve `fastembed`/`requests` katmanında timeout
# YOK → paket saatlerce asılı kalıyordu (canlı bildirim: ~10 saat, hiç bitmedi). Kapalıyken
# F5-token sözlüksel fallback koşar; VQR testleri zaten bu yola göre eşiklenmiştir
# (`_LEX_EXACT_THRESHOLD`), dolayısıyla koşum HEM hızlı HEM deterministik olur.
os.environ["DIMA_VQR_EMBEDDER"] = "off"
# Testler CANLI etkileşim loguna yazmaz (log→golden döngüsü gerçek oturumları temsil etmeli).
os.environ["DIMA_INTERACTION_LOG"] = "false"
# Zamanlanmış rapor tanımı + koşum durumu + bildirim + sözleşme kanıtı HEPSİ tek-kaynak
# DB'de (Faz 3) → dosya-yolu env'i yok; her test taze DB (create_all) ile izole.
os.environ["DIMA_SCHEDULER_ENABLED"] = "false"  # arka plan döngüsü testte koşmaz
# Control-plane (auth) izolasyonu: testler canlı logs/control_plane.db'yi KİRLETMEZ;
# secret'lar sabit (dev-random olursa her koşum farklı olur), plane'ler FARKLI.
os.environ["DIMA_DATABASE_URL"] = (
    "sqlite:///" + os.path.join(tempfile.mkdtemp(prefix="dima-cp-"), "control_plane.db")
)
# Superadmin public login IP kapısı: TestClient'ın istemci adresi "testclient".
os.environ["DIMA_SUPERADMIN_IP_ALLOWLIST"] = "testclient"
os.environ["DIMA_JWT_SECRET"] = "test-public-access-secret-0123456789abcdef"
os.environ["DIMA_JWT_REFRESH_SECRET"] = "test-public-refresh-secret-0123456789abcdef"
os.environ["DIMA_ADMIN_JWT_SECRET"] = "test-admin-access-secret-0123456789abcdef"
os.environ["DIMA_ADMIN_JWT_REFRESH_SECRET"] = "test-admin-refresh-secret-0123456789abcdef"
import base64 as _b64
# Müşteri DB sırrı şifrelemesi (ADR-0017): sabit test KEK'i (32 bayt).
os.environ["DIMA_CRED_KEK"] = _b64.b64encode(b"test-kek-32-byte-0123456789abcd!").decode()

# ⚡ PARALEL KOŞUM (pytest-xdist) — her worker KENDİ derlenmiş proje ağacına yazar.
#
# Paylaşılan `demo/wren-project` üzerinde EŞZAMANLI compose, korpusun yakaladığı
# 445→342 vakasını doğuran YARIŞIN ta kendisidir (CLAUDE.md test kapısı: *"iki test
# konteyneri ASLA paralel koşmaz — compose kilidi metadata.yml'de çakışır"*). O kural
# **paylaşılan çıktı dizini** varsayımına dayanır: `compose.build_lock_for()` yalnız
# DİZİN BAŞINA kilitler → her worker'a ayrı dizin verilirse yarış **yapısal olarak**
# ortadan kalkar, kilit beklemesi de olmaz.
#
# `compose_and_build()` packs/companies tabanını `project_dir`'in EBEVEYNİNDEN türetir
# (`app/compose.py:814`; `demo_root` ayarı YOK). Bu yüzden geçici tabana `packs`/
# `companies` **sembolik bağ** kurulur — repoya tek bayt yazılmaz (kapı kuralı:
# *"kapı koşarken repoya YAZILMAZ"*), taban salt-okunur tüketilir.
# ⚡ PARALEL SÜİT (pytest-xdist): her worker KENDİ derlenmiş proje ağacına yazar, böylece
# `demo/wren-project` üzerindeki compose yarışı YAPISAL olarak ortadan kalkar. Gerekçenin
# tamamı ve neden düz `mkdtemp`'in yetmediği `lab/izolasyon.py` başında.
_XDIST_WORKER = os.environ.get("PYTEST_XDIST_WORKER")
if _XDIST_WORKER:
    import sys as _sys

    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lab.izolasyon import izole_proje_ayna

    os.environ["DIMA_PROJECT_DIR"] = izole_proje_ayna(_XDIST_WORKER)

TEST_USER = {"email": "test@dima.local", "password": "test-parola-123"}
TEST_SUPERADMIN = {"email": "root@dima.local", "password": "root-parola-123"}


def make_tenant_user(email: str, password: str, role_key: str = "owner",
                     tenant_slug: str | None = None) -> None:
    """Verilen tenant'ta (yoksa kurar) verilen rolde kullanıcı yaratır (idempotent).

    Rol matrisi bu fazda uykuda (üründe yalnız owner) ama authorize() mantığı
    testli kalmalı — analyst/viewer rolleri test DB'sine doğrudan yazılır."""
    from sqlmodel import Session, select

    from app.config import get_settings
    from control_plane.db import engine, init_db
    from control_plane.models import Membership, Role, Tenant, User
    from control_plane.security import hash_password

    init_db()
    slug = tenant_slug or get_settings().company  # veri-düzlemi bağı: aktif şirket
    with Session(engine) as s:
        if s.exec(select(User).where(User.email == email)).first():
            return
        tenant = s.exec(select(Tenant).where(Tenant.slug == slug)).first()
        if tenant is None:
            tenant = Tenant(slug=slug, name=slug)
            s.add(tenant)
            s.commit()
            s.refresh(tenant)
            for key in ("owner", "admin", "analyst", "viewer"):
                s.add(Role(tenant_id=tenant.id, key=key, name=key.capitalize()))
            s.commit()
        role = s.exec(select(Role).where(Role.tenant_id == tenant.id,
                                         Role.key == role_key)).one()
        user = User(tenant_id=tenant.id, email=email,
                    password_hash=hash_password(password))
        s.add(user)
        s.commit()
        s.refresh(user)
        s.add(Membership(tenant_id=tenant.id, user_id=user.id, role_id=role.id))
        s.commit()


def _ensure_test_users() -> None:
    """Aktif şirkete bağlı owner kullanıcı + superadmin (idempotent)."""
    from sqlmodel import Session, select

    from control_plane.db import engine, init_db
    from control_plane.models import User
    from control_plane.security import hash_password

    make_tenant_user(TEST_USER["email"], TEST_USER["password"], "owner")
    init_db()
    with Session(engine) as s:
        if not s.exec(select(User).where(User.email == TEST_SUPERADMIN["email"])).first():
            s.add(User(email=TEST_SUPERADMIN["email"],
                       password_hash=hash_password(TEST_SUPERADMIN["password"]),
                       is_superadmin=True))
            s.commit()


@pytest.fixture(scope="session", autouse=True)
def _composed():
    """ADR-0005: testler derlenmiş wren-project üzerinde koşar — önce compose+build."""
    from app.compose import compose_and_build
    from app.config import get_settings

    get_settings.cache_clear()
    compose_and_build(get_settings())


@pytest.fixture(scope="session")
def client():
    """Kimlikli TestClient: test tenant kullanıcısıyla login olur, Bearer taşır."""
    from fastapi.testclient import TestClient

    from app.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as c:
        _ensure_test_users()

        def _giris() -> str:
            r = c.post("/auth/login", json=TEST_USER)
            assert r.status_code == 200, f"test login başarısız: {r.text}"
            return r.json()["access_token"]

        c.headers["Authorization"] = f"Bearer {_giris()}"

        # 🔴 KÖK-8d — ÖLÇÜM OTURUMU ÜRÜNÜN TOKEN ÖMRÜNÜ AŞMAMALI.
        #
        # Ölçülen (denetim raporu KN-4): `access_ttl_seconds = 15 * 60`. Süit tek
        # süreçte **19 dk 15 sn** koşuyor → 15. dakikadan sonraki **90 test** `401
        # "Geçersiz veya süresi dolmuş token"` alıyor ve **KIRMIZI** raporlanıyor.
        # Aynı testler `-n 8` ile 6 dakikada koşunca **0 hata** veriyor.
        #
        # 🔴 Bu bir ÜRÜN kusuru değil, ÖLÇÜM ARACI kusurudur — ve tehlikesi tam olarak
        # bu: rapor **112 hata** gösterdi, gerçek **22**'ydi. *Bir kapı, ölçemediği şeyi
        # "başarısız" diye raporlarsa ölçüm aracının kendisi bir kusur kaynağıdır.*
        #
        # ⚠ Çözüm ürünün kendi desenini AYNALAR: `api-client.ts` de 401'de tek uçuşta
        # yenileyip isteği tekrarlar. Ölçüm aracı, ölçtüğü ürünün oturum davranışını
        # taklit etmelidir — yoksa ölçtüğü şey ürün değil, kendi kurulumudur.
        #
        # ⚠ Bilinen sınır (yazılı): isteğe ELLE `Authorization` başlığı geçen bir test
        # yenilemeden yararlanmaz — orada başlık `c.headers`i ezer. Bugün öyle bir
        # çağıran yok; olursa bu yorum onu yakalar.
        _ham_request = c.request

        def _yenileyen_request(method, url, *a, **kw):
            r = _ham_request(method, url, *a, **kw)
            if r.status_code == 401 and "/auth/" not in str(url):
                c.headers["Authorization"] = f"Bearer {_giris()}"
                r = _ham_request(method, url, *a, **kw)
            return r

        c.request = _yenileyen_request
        yield c


@pytest.fixture(scope="session")
def wren():
    """Gerçek `WrenService` — SQL DERLEME ve ÇALIŞTIRMA gerektiren testler için.

    `schema` fixture'ı ile AYNI servisten gelir: bir test "route bu cq'yu üretti" derken
    öteki "o cq gerçekten şu satırları döndürüyor" diyebilsin. Derlendi ≠ doğru."""
    from app.config import get_settings
    from app.wren_service import WrenService

    get_settings.cache_clear()
    s = get_settings()
    return WrenService(
        project_dir=s.resolved_project_dir(),
        datasource=s.datasource,
        connection_info=s.connection_dict(),
    )


@pytest.fixture(scope="session")
def schema(wren):
    """Gerçek MDL'den türetilen şema (cube kataloğu dahil) — router birim testleri için."""
    return wren.schema()


def ask(client, question: str, **kw) -> dict:
    payload = {"question": question, "execute": True, "session_id": "eval", **kw}
    r = client.post("/ask", json=payload)
    assert r.status_code == 200, r.text
    return r.json()

@pytest.fixture(scope="session", autouse=True)
def _test_kimligi():
    """🔴 **Testler bir kullanıcıyı taklit eder — kimliği de taşımalı.**

    `motor_cls=on` ile ölçüldü: 39 kırmızının bir kısmı `svc.dry_plan(sql)` /
    `svc.query(sql)`'i **doğrudan**, kimliksiz çağıran testlerden geliyordu. Motor
    planlama aşamasında `session property session_gizlilik is required … but not found
    in headers` diyerek **fail-closed** patlıyordu — ve bu, **doğru davranıştır**:
    kimliksiz bir kullanıcı sorgusu gürültülü patlamalı.

    Kusur kodda değil, **koşum ortamındaydı**: gerçek bir istekte kimliği
    `get_current_principal` kurar; doğrudan çağrıda kimseyi kurmuyordu. Bu fixture o
    boşluğu kapatır — *bir testin ortamı, taklit ettiği ortamla aynı olmalıdır.*

    ⚠ **Bu bir kapı gevşetmesi DEĞİLDİR.** Ürün kodunda hiçbir şey değişmiyor;
    `motor_cls=off` iken bu kimliğin **hiçbir etkisi yok** (özellikler yalnız CLS
    kuralları varken okunur). Ve `test_istek_kimligi.py` bağlamın kendisini ayrı ayrı
    **kimliksiz** ölçmeye devam ediyor.

    ⚠ Kimlik **owner** seviyesinde: test kullanıcısı (`TEST_USER`) zaten owner'dır, yani
    fixture bir **ayrıcalık uydurmuyor** — HTTP yolunda çözülecek olanın aynısını kuruyor.
    """
    from app import istek_kimligi
    from control_plane.authorize import Principal

    p = Principal(user_id="test-user", tenant_id="test-tenant", roles=["owner"],
                  tenant_slug="demo-boyahane")
    token = istek_kimligi.ayarla(p)
    yield p
    istek_kimligi.sifirla(token)
