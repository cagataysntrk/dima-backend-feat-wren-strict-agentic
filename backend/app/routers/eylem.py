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


def _uygula_dogrudan(request: Request, ad: str, argumanlar: dict) -> dict:
    """🔴 **FAZ 6.0 — D9: istemsiz koşum.** Kapsam içi + geri alınabilir bir eylemi
    kullanıcının **onay tıklamasını beklemeden** çalıştırır.

    ## 🔴 KAPILAR ATLANMIYOR — YALNIZ TIKLAMA ATLANIYOR

    Bu fonksiyon **kendi uygulamasını yazmaz**: `eylem_onayla`'yı **olduğu gibi** çağırır.
    Yani kayıt kapısı, `authorize()` **yeniden doğrulaması**, çapa şartı ve `eylem_onay`
    audit satırı **aynen** işler.

    *"İstemsiz koşmak", kapıları atlamak değil **kullanıcının kendi eylemi için ikinci
    kez tıklamasını** atlamaktır.* İkinci bir uygulama yazmak, o kapıların bir gün
    ayrışması demekti — ve ayrışan taraf her zaman daha gevşek olanıdır.

    Döner: `{"eylem", "id", "not", "geri_al"}` — `geri_al` kullanıcıya **nasıl geri
    alacağını** söyler; geri alınabilirliği ilan edip yolunu göstermemek, onu bir
    temenniye çevirirdi.
    """
    from app.schemas import EylemOnayRequest

    ses = next(get_session())
    try:
        cevap = eylem_onayla(request, EylemOnayRequest(eylem=ad, argumanlar=argumanlar),
                             ses)
    finally:
        ses.close()
    return {
        "eylem": cevap.eylem, "id": cevap.id, "not": cevap.note,
        # ⚠ Geri alma yolu **eyleme özgü** ve kayıttan türer — burada bir metin
        # uydurulmaz.
        "geri_al": ("Pano widget'ını panodan kaldırabilirsin."
                    if ad == _eylem.PANO_EKLE else
                    "Tercihi «tercihler» panelinden kaldırabilirsin."
                    if ad == _eylem.TERCIH_KAYDET else None),
    }


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

    # (2b) 🔴 **SÜRE KAPISI — §C ölçüt 6'nın üçüncü şartı.**
    #
    # Ölçüldü (okunarak): bu yolda **hiçbir süre kontrolü yoktu**; üç saat önceki bir
    # öneri onaylanıp koşabiliyordu. Şartın *"süre aşımı 30 dk"* yarısı **yalnız
    # `onay_akisi.py`'de** duruyordu — o modülün hiçbir üretim tüketicisi olmadan
    # (denetimin *"12 yetim modül"* bulgusu).
    #
    # ⚠ **Yetkiden SONRA — ve ilk yazımda önce koymuştum.** Gerekçem *"süresi dolmuş bir
    # öneri, yetkisi olsa bile koşmamalı"*ydı ve **yanlıştı**: yetki önce koşarsa yetkili
    # kullanıcı yine bu kapıya çarpar, yetkisiz olan ise **daha güçlü** bir kapıda durur.
    # Ters sıra yalnız bir şey yapıyordu: yetkisiz bir çağrıya *"bilet bozuk"* diyerek
    # **403 sinyalini gizliyordu**. `test_eylem_onayi` bunu yakaladı.
    # *Bir kapıyı öne almak, onu güçlendirmez; yalnız arkasındakinin sesini kısar.*
    from app import onay_akisi

    try:
        onay_akisi.bilet_dogrula(body.bilet, beyan.ad)
    except onay_akisi.OnayHatasi as exc:
        # 🔴 **410 değil 400**: 410 (Gone) bir kaynağın *"vardı, artık yok"* hâlidir;
        # burada kaynak duruyor, **onay** bayatladı. Ve mesaj NEDENİ söylüyor —
        # *süresi dolduğu söylenmeyen bir ret, bir arıza gibi okunur.*
        raise HTTPException(status_code=400, detail=str(exc)) from None

    args = dict(body.argumanlar or {})
    # RAPOR ÇAPASI ŞARTI eyleme ÖZELDİR: pano/zamanlama bir raporu kalıcılaştırır ve
    # doğrulanmış bir `cube_query` taşımak ZORUNDADIR (uydurma bir sorgu her hafta
    # koşardı). Sunum tercihi ise bir rapora değil GÖRÜNÜME bağlıdır — ondan cube_query
    # istemek, şartı anlamından kopuk bir tören hâline getirirdi.
    if beyan.ad in (_eylem.PANO_EKLE, _eylem.ZAMANLA) and \
            not (args.get("cube_query") or {}).get("cube"):
        raise HTTPException(status_code=400,
                            detail="Eylem için geçerli bir rapor (cube_query) gerekli.")

    from control_plane import audit

    ip = request.client.host if request.client else None

    if beyan.ad == _eylem.TERCIH_KAYDET:
        from app.routers.tercihler import tercih_yaz

        out = tercih_yaz(request, session, str(args.get("anahtar") or ""),
                         str(args.get("deger") or ""),
                         kaynak_ifade=args.get("kaynak_ifade"))
        audit.record(principal, "eylem_onay",
                     nl_question=f"{beyan.ad} → {json.dumps(args, ensure_ascii=False)[:400]}",
                     ip=ip)
        return EylemOnayResponse(ok=True, eylem=beyan.ad, id=out["id"],
                                 note="Tercihiniz kaydedildi.")

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
