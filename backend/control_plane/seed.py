"""Lokal demo fixture — YALNIZ geliştirme (canlıda çalıştırılmaz).

İdempotent: tenant/kullanıcı zaten varsa atlar, ASLA duplicate oluşturmaz.
Çalıştır: ``PYTHONPATH=. .venv/bin/python -m control_plane.cli seed-demo``
"""

from __future__ import annotations

from sqlmodel import Session, select

from control_plane.db import engine, init_db
from control_plane.models import Membership, Role, Tenant, User
from control_plane.security import hash_password

# Local dev fixture parolası (owner kullanıcıları). Yalnız geliştirme.
DEMO_OWNER_PASSWORD = "dima-demo-1234"

DEMO_TENANTS: list[tuple[str, str]] = [
    ("demo-boyahane", "Demo Boyahane"),
    ("demo-geri-donusum", "Demo Geri Dönüşüm"),
]

_DEFAULT_ROLES = ("owner",)  # bu fazda tek rol (rol matrisi uykuda)


def _ensure_tenant(session: Session, slug: str, name: str) -> Tenant:
    tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
    if tenant:
        print(f"tenant zaten var:   {slug}")
        return tenant
    tenant = Tenant(slug=slug, name=name)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    for key in _DEFAULT_ROLES:
        session.add(Role(tenant_id=tenant.id, key=key, name=key.capitalize()))
    session.commit()
    print(f"tenant oluşturuldu: {slug}")
    return tenant


def _ensure_owner(session: Session, tenant: Tenant, email: str) -> None:
    if session.exec(select(User).where(User.email == email)).first():
        print(f"owner zaten var:    {email}")
        return
    user = User(tenant_id=tenant.id, email=email,
                password_hash=hash_password(DEMO_OWNER_PASSWORD))
    session.add(user)
    session.commit()
    session.refresh(user)
    owner_role = session.exec(
        select(Role).where(Role.tenant_id == tenant.id, Role.key == "owner")
    ).first()
    session.add(Membership(tenant_id=tenant.id, user_id=user.id, role_id=owner_role.id))
    session.commit()
    print(f"owner oluşturuldu:  {email}  (parola: {DEMO_OWNER_PASSWORD})")


def _senaryo_fixtureleri(session: Session, tenant: Tenant) -> None:
    """SENARYO VERİSİ — canlı ölçüm turunun ihtiyaç duyduğu, kod yolundan ÜRETİLEMEYEN girdiler.

    ## Neden gerekli

    Seed bugüne kadar yalnız tenant + owner yaratıyordu. Ama sistemin birkaç yolu
    **kullanıcının kendi kurduğu veriye** dayanıyor ve o veri yoksa yol **sessizce boş**
    çalışır — yani "çalışıyor" görünür, hiçbir şey ölçmez:

    | fixture | hangi yolu AÇAR | yoksa ne olur |
    |---|---|---|
    | eşik alarmı | `interpret`'in **eşik kıyası** (Faz G3) | `esikler=[]` → kıyas cümlesi hiç üretilmez |
    | VQR: `user_verified` | `near_exact` **replay** yolu | replay hiç tetiklenmez, §1.7 ölçülemez |
    | VQR: `auto_cube` | Faz 2b'nin **replay'den çıkarma** kararı | kararın etkisi görünmez |
    | sinonim adayı | terfi kuyruğu (Faz 2b-1) | kuyruk boş → triyaj ölçülemez |

    **VQR çifti bilinçli:** ikisi de aynı yapıda, tek farkları `source`. Böylece §1.7'nin
    kararı **doğrudan gözlemlenebilir** olur — `user_verified` replay EDİLİR, `auto_cube`
    EDİLMEZ. Tek bir kayıtla bu ayrım görülemezdi.

    Hepsi **idempotent** ve **yalnız geliştirme**; canlıda bu fonksiyon çağrılmaz.
    """
    import json
    import uuid as _uuid

    from control_plane.models import ScheduleDefinition, SynonymOverride, VerifiedQuery

    # ŞİRKET KAPSAMI = `tenant.slug`'ın KENDİSİ, kırpılmışı DEĞİL.
    # ⚠️ İlk sürüm `.replace("demo-", "")` yapıyordu ve fixture'lar `company="boyahane"`
    # ile yazılıyordu; `settings.company` ise `"demo-boyahane"`. Sonuç: VQR kayıtları
    # **hiç eşleşmiyordu** ve replay yolu sessizce test edilmemiş kalıyordu — fixture
    # "var" görünüyor, hiçbir şey ölçmüyordu. Kapsam adını TAHMİN ETME, olduğu gibi kullan.
    sirket = tenant.slug

    # 1) EŞİK ALARMI — kullanıcının KENDİ kurduğu hedef. `interpret` bunu okur ve
    #    "kritik sınırın %X'i" cümlesini üretir. Cube metadata'sında `target:` YOKTUR
    #    (ölçüldü) ve demo için hedef UYDURMAK, `pvm:` eşleştirmesinde reddedilen şeyin
    #    aynısı olurdu — ama kullanıcı bir alarm kurduysa "benim için kritik sınır bu"
    #    DEMİŞTİR ve bu uydurulmuş değil BEYAN EDİLMİŞ bir hedeftir.
    esik_id = f"s-seed-{sirket[:8]}"
    if not session.get(ScheduleDefinition, esik_id):
        session.add(ScheduleDefinition(
            id=esik_id, company=sirket, tenant_id=str(tenant.id),
            label="Fire uyarısı (seed)",
            cube_query_json=json.dumps(
                {"cube": "parti", "measures": ["toplam_fire_kg"]}, ensure_ascii=False),
            period="son 7 gün", every="day", at="08:00",
            threshold_json=json.dumps({"measure": "toplam_fire_kg", "op": ">",
                                       "value": 500}, ensure_ascii=False)))
        print(f"eşik alarmı:        {esik_id} (parti.toplam_fire_kg > 500)")

    # 2) VQR ÇİFTİ — aynı yapı, FARKLI kaynak. §1.7'nin kararını gözlemlenebilir kılar.
    for kaynak, soru in (("user_verified", "geçen ay toplam ciro"),
                         ("auto_cube", "geçen ay toplam fire")):
        norm = soru.lower()
        var = session.exec(select(VerifiedQuery).where(
            VerifiedQuery.question_norm == norm,
            VerifiedQuery.company == sirket)).first()
        if var:
            continue
        session.add(VerifiedQuery(
            id=_uuid.uuid4(), company=sirket, tenant_id=str(tenant.id),
            question=soru, question_norm=norm,
            cube_query_json=json.dumps(
                {"cube": "parti",
                 "measures": ["toplam_ciro" if "ciro" in soru else "toplam_fire_kg"]},
                ensure_ascii=False),
            source=kaynak))
        print(f"VQR kaydı:          [{kaynak}] {soru!r}")

    # 3) SİNONİM ADAYI — terfi kuyruğu boş olmasın; `approved=False` (canlıya İNMEZ).
    aday = session.exec(select(SynonymOverride).where(
        SynonymOverride.cube == "parti",
        SynonymOverride.field_name == "toplam_ciro",
        SynonymOverride.scope_id == tenant.slug)).first()
    if not aday:
        session.add(SynonymOverride(
            scope_type="tenant", scope_id=tenant.slug, cube="parti",
            field_kind="measure", field_name="toplam_ciro",
            synonyms_json=json.dumps(["döviz cirosu", "net hasılat"], ensure_ascii=False),
            lang="tr", approved=False, source="mined"))
        print("sinonim adayı:      parti.toplam_ciro (approved=False — canlıya İNMEZ)")
    session.commit()


def seed_demo() -> int:
    """2 demo firması + owner kullanıcıları + SENARYO FİXTURE'LARI (idempotent)."""
    init_db()  # SQLite'ta tabloları kurar + eksik kolonları ekler; Postgres'te Alembic sahibi.
    with Session(engine) as session:
        for slug, name in DEMO_TENANTS:
            tenant = _ensure_tenant(session, slug, name)
            _ensure_owner(session, tenant, f"{slug}@usedima.com")
            _senaryo_fixtureleri(session, tenant)
    print(f"seed-demo tamam. (backend: {engine.url.get_backend_name()})")
    return 0
