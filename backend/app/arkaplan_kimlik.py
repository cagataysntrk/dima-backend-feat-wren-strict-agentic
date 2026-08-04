"""FAZ 1.1b — **ARKA PLAN İŞİ KİMLİKSİZ KOŞMAZ.**

## Ölçülen boşluk

`1.1` yalnız **istek yolunu** kapatıyor; **zamanlayıcı yolu açıktı**. `app/main.py`'nin
60 saniyelik döngüsü `run_schedule(state, sched)`'ı **`principal` olmadan** çağırıyordu
(`schedules.py:653`). İki sonuç:

* `authorize()` **hiç çalışmıyor** — zamanlanmış bir rapor, sahibinin yetkisi **alındıktan
  sonra da** koşmaya devam eder; kullanıcı `viewer`'a düşürülse, hatta **silinse** bile.
* `1.1`'in session-property enjeksiyonu (geldiğinde) buraya **hiç uğramaz** → *"istek yolu
  güvenli, zamanlayıcı yolu açık"* asimetrisi.

Plan 3 bunu *"B9'un zamanlayıcı tarafındaki karşılığı"* diye adlandırmış; ölçüm doğruladı.

## 🔴 Fail-closed KESİNTİ ÜRETMEDEN — çünkü cevap zaten kayıtta

Yol haritası *"`principal=None` ile `run_schedule` **reddedilir**"* diyor ve bunu **geri
alınamaz bir değişmez** ilan ediyor. Harfi harfine uygulanırsa **her zamanlanmış rapor
durur**.

Ölçüldü: kayıt **`created_by` alanını zaten taşıyor** (`schedules.py:54`). Yani *"bu iş
kimin adına koşuyor"* sorusunun cevabı **kayıtta duruyordu**, hiç **sorulmuyordu**.

| kayıt | karar |
|---|---|
| `run_as_user_id` var | o kullanıcı adına koşar |
| yok ama `created_by` var | **geriye doldurulur** — kesinti yok |
| ikisi de yok | 🔴 **REDDEDİLİR** (fail-closed) |

⚠ **Sahipsiz kayıt bir "eski veri" değil, bir BULGUDUR** — reddin gerekçesi zamanlamanın
**adıyla** yazılır. Sessizce atlamak, deliği *"eski kayıt"* diye meşrulaştırırdı.

## Neden `Principal` yeniden kuruluyor, saklanmıyor

Token saklamak bir **sır saklamaktır** ve süresi dolar. Kimlik her koşumda **kaynaktan**
(`app_user` + `membership` + `role`) yeniden kurulur; böylece rol değişikliği **bir sonraki
koşumda** etkili olur. Saklanmış bir yetki, iptal edilemeyen bir yetkidir.
"""

from __future__ import annotations

from typing import Any


class KimliksizArkaPlanIsi(Exception):
    """Sahibi çözülemeyen bir arka plan işi. **Fail-closed** — koşum yapılmaz."""


def sahip_kimligi(sched: dict[str, Any]) -> str | None:
    """`run_as_user_id` → yoksa `created_by`. İkisi de yoksa `None`.

    `created_by`'a düşmek bir **geriye doldurmadır**, bir gevşetme değil: kayıt zaten
    *"bunu kim oluşturdu"* bilgisini taşıyordu ve bir zamanlamanın **varsayılan sahibi**
    onu kuran kişidir. Alan açıkça verildiğinde (`run_as_user_id`) o kazanır.
    """
    return (sched.get("run_as_user_id") or sched.get("created_by")) or None


def kimlik_coz(user_id: str, tenant_id: str | None, oturum: Any):
    """`(user_id, tenant_id)` → `Principal`. Çözülemezse `None`.

    Roller **`membership` → `role`** üzerinden okunur (tek kaynak: `authorize` matrisi
    aynı anahtarları kullanır). Kullanıcı **pasifse** `None` döner — askıya alınmış bir
    hesabın zamanlanmış raporu koşmaya devam etmemelidir; bu, `_tenant_active` kapısının
    arka plan yolundaki karşılığıdır.
    """
    from sqlmodel import select

    from control_plane.authorize import Principal
    from control_plane.models import Membership, Role, Tenant, User

    try:
        kullanici = oturum.get(User, user_id)
    except Exception:                                        # noqa: BLE001
        kullanici = None
    if kullanici is None or getattr(kullanici, "status", "active") != "active":
        return None

    tid = str(kullanici.tenant_id) if kullanici.tenant_id else (tenant_id or None)
    roller: list[str] = []
    slug = None
    if tid:
        rol_kimlikleri = {m.role_id for m in oturum.exec(
            select(Membership).where(Membership.user_id == kullanici.id))}
        roller = sorted({r.key for r in oturum.exec(
            select(Role).where(Role.tenant_id == kullanici.tenant_id))
            if r.id in rol_kimlikleri})
        tenant = oturum.get(Tenant, kullanici.tenant_id)
        slug = getattr(tenant, "slug", None)
    return Principal(user_id=str(kullanici.id), tenant_id=tid,
                     is_superadmin=bool(kullanici.is_superadmin),
                     roles=roller, tenant_slug=slug)


def yetkilendir(sched: dict[str, Any], oturum: Any, *, aksiyon: str = "query:run"):
    """Zamanlamanın sahibini çözer ve **yetkilendirir**. Döner: `Principal`.

    🔴 **Üç fail-closed kapısı, üçü de ayrı gerekçeli:**
    1. Sahip **yok** → sahipsiz arka plan işi tam olarak kapatılan delik.
    2. Sahip **çözülemiyor** (silinmiş/pasif kullanıcı) → yetkisi de yok demektir.
    3. Sahip var ama **aksiyona yetkisi yok** → yetki alındığı an iş de durmalı.
       *Yetki, verildiği an değil **kullanıldığı an** geçerli olmalıdır.*
    """
    from control_plane.authorize import AuthzError, authorize

    kimlik = sahip_kimligi(sched)
    if not kimlik:
        raise KimliksizArkaPlanIsi(
            f"schedule {sched.get('id')!r} ({sched.get('label')!r}): SAHİBİ YOK "
            "(`run_as_user_id` ve `created_by` boş) — kimliksiz bir arka plan işi "
            "`authorize()`'ı hiç çağırmaz ve sahibinin yetkisi alındıktan sonra da koşar. "
            "Fail-closed: koşum YAPILMADI. Düzeltme: kayda `run_as_user_id` yazın.")

    principal = kimlik_coz(str(kimlik), sched.get("tenant_id"), oturum)
    if principal is None:
        raise KimliksizArkaPlanIsi(
            f"schedule {sched.get('id')!r}: sahip {kimlik!r} ÇÖZÜLEMEDİ (silinmiş ya da "
            "pasif kullanıcı). Askıya alınmış bir hesabın zamanlanmış raporu koşmaya "
            "devam etmemelidir — `_tenant_active` kapısının arka plan karşılığı.")

    try:
        authorize(principal, aksiyon, f"data:{aksiyon.split(':', 1)[0]}")
    except AuthzError as exc:
        raise KimliksizArkaPlanIsi(
            f"schedule {sched.get('id')!r}: sahip {kimlik!r} artık `{aksiyon}` yetkisine "
            f"sahip DEĞİL ({exc}). Yetki, verildiği an değil KULLANILDIĞI AN geçerli "
            "olmalıdır.") from exc
    return principal
