"""ONAY UCU — ajanın önerdiği yazma eyleminin tek geçiş noktası (FAZ H).

## Neden ayrı bir uç

Ajan yazma araçlarını **çalıştırmaz** (`app/tools.py`: *"Ajan YAZAMAZ"*). Bu uç o kuralı
gevşetmez, **kademelendirir**: kullanıcı önce öneriyi görür, sonra onaylar; onay
kullanıcının kendi kimliğiyle gelen ayrı bir HTTP isteğidir.

## Üç koruma — ve neden bu sırayla

1. **Eylem kayıttan çözülür** (`eylem.beyan`) — kayıtta olmayan ad 400. İstemci eylem
   UYDURAMAZ; yazma yüzeyi `EYLEM_KAYIT`'ın boyu kadardır ve o kayıt okunabilir.
2. **`authorize()` YENİDEN çağrılır.** Öneri anındaki yetkiye güvenmek TOCTOU olurdu:
   rol öneriyle onay arasında düşmüş olabilir. Yetki kaynağı yine `control_plane.
   authorize` — burada ikinci bir kopya YOKTUR.
3. **Argümanlar VAR OLAN handler'a verilir.** `cube_query` katalog doğrulamasından,
   e-posta biçim denetiminden, tenant damgasından **o handler'da** geçer. Buraya bir
   doğrulama kopyalansaydı zamanla ayrışırdı — bu deponun ölçülmüş bir numaralı kusur
   sınıfı (`tools.py` girişindeki üç örnek).

## Öneri neden GÜVENİLMEZ bir girdi olarak ele alınıyor

Çünkü öyle. Bir istemci `argumanlar`'ı istediği gibi değiştirebilir. Bunun **zarar
üretmemesinin** nedeni bir imza ya da sunucu-tarafı öneri deposu değil, daha basit bir
gerçek: bu uç, kullanıcının **zaten kendi eliyle çağırabileceği** ucu çağırır. Öneri
yeni bir yetki YARATMAZ — dolayısıyla kurcalanmasından kazanılacak bir şey yoktur.

## Yönetişim: onay AYRI bir audit satırıdır

`schedule_create` satırı *"bir zamanlama kuruldu"* der. Yönetişimin sorduğu soru ise
*"bunu kullanıcı kendi mi istedi, sistem mi önerdi?"*dur. Bu yüzden onay, handler'ın
kendi audit satırının **üstüne** `eylem_onay` satırı yazar.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, col, select

from app import eylem as _eylem
from app.auth.dependencies import require_company
from app.schemas import EylemOnayRequest, EylemOnayResponse
from control_plane.authorize import can
from control_plane.db import get_session
from control_plane.models import Dashboard

router = APIRouter(tags=["eylem"])


def _principal(request: Request):
    p = getattr(request.state, "principal", None)
    if p is None:
        raise HTTPException(status_code=401, detail="Kimlik gerekli")
    return p


def _hedef_pano(session: Session, principal) -> Dashboard:
    """Widget'ın gideceği pano: kullanıcının EN ESKİ panosu, yoksa oluşturulur.

    Oluşturma bir sürpriz DEĞİLDİR — önerinin özeti *"panona ekleyeyim mi?"* der ve
    panosu olmayan bir kullanıcı için o cümlenin tek dürüst karşılığı budur. Sessiz
    olan şey zararlıdır; beyan edilmiş olan değil.
    """
    owned = session.exec(
        select(Dashboard)
        .where(Dashboard.user_id == principal.user_id)
        .where(col(Dashboard.deleted_at).is_(None))
        .order_by(col(Dashboard.created_at))
    ).first()
    if owned is not None:
        return owned
    d = Dashboard(user_id=principal.user_id, tenant_id=principal.tenant_id,
                  title="Panom")
    session.add(d)
    session.commit()
    session.refresh(d)
    return d


@router.post("/ask/eylem", dependencies=[Depends(require_company)])
def eylem_onayla(request: Request, body: EylemOnayRequest,
                 session: Session = Depends(get_session)) -> EylemOnayResponse:
    principal = _principal(request)

    # (1) KAYITTAN ÇÖZ — fail-closed.
    try:
        beyan = _eylem.beyan(body.eylem)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

    # (2) YETKİYİ YENİDEN DOĞRULA — öneri anındaki yetkiye GÜVENİLMEZ (TOCTOU).
    if not can(principal, beyan.izin):
        raise HTTPException(
            status_code=403,
            detail=f"Bu işlem için yetkiniz yok ({beyan.izin}).")

    args = dict(body.argumanlar or {})
    if not (args.get("cube_query") or {}).get("cube"):
        # Öneri her zaman DOĞRULANMIŞ bir cube_query taşır; taşımıyorsa bu bir öneri
        # değildir. Boş/uydurma bir sorguyu kalıcılaştırmak, bu fazın kapatmak için
        # var olduğu kusurun ta kendisi olurdu.
        raise HTTPException(status_code=400,
                            detail="Eylem için geçerli bir rapor (cube_query) gerekli.")

    from control_plane import audit

    ip = request.client.host if request.client else None

    # (3) VAR OLAN handler'a devret — doğrulama İKİNCİ KEZ YAZILMAZ.
    if beyan.ad == _eylem.PANO_EKLE:
        from app.routers.dashboards import WidgetCreate, add_widget

        did = body.dashboard_id or str(_hedef_pano(session, principal).id)
        out = add_widget(request, did, WidgetCreate(**args), session)
        audit.record(principal, "eylem_onay",
                     nl_question=f"{beyan.ad} → pano={did} {json.dumps(args, ensure_ascii=False)[:400]}",
                     ip=ip)
        return EylemOnayResponse(ok=True, eylem=beyan.ad, id=str(out.get("id")),
                                 note="Rapor panona eklendi.")

    from app.routers.schedules import ScheduleRequest, create_schedule

    out = create_schedule(request, ScheduleRequest(**args))
    sid = str((out.get("schedule") or {}).get("id") or "")
    audit.record(principal, "eylem_onay",
                 nl_question=f"{beyan.ad} → {json.dumps(args, ensure_ascii=False)[:400]}",
                 ip=ip)
    return EylemOnayResponse(ok=True, eylem=beyan.ad, id=sid or None,
                             note="Zamanlama kuruldu.")
