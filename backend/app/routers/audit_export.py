"""FAZ 1.12 — **`GET /audit/export`**: denetleyici-okunabilir kayıt (AI Act Md.13).

## Neden ayrı bir uç

Md.13 *"denetleyici-okunabilir log"* istiyor. `AuditLog` **zaten** her erişimi tutuyor;
eksik olan **dışa aktarılabilir, standart adlı** bir görünümdü. Bir kanıt defteri, yalnız
onu yazan sistemin okuyabildiği bir biçimdeyse **denetlenebilir değildir**.

## 🔴 İKİNCİ BİR EŞLEME YAZILMADI

Standart adlara çeviri `app/audit_zinciri.py::otel_nitelikleri`'nde (FAZ 1.8) **zaten
var**. Burada ikinci bir çevirici yazmak, iki dışa aktarımın **farklı adlar** kullanması
demekti — ve denetleyici hangisinin doğru olduğunu bilemezdi.

## ⚠ Zincir bütünlüğü de İHRAÇ EDİLİR

Dışa aktarım `zincir_bulgulari` taşır. Bir kanıt defterini **bütünlük raporu olmadan**
teslim etmek, *"işte kayıtlarım"* deyip **eksik olup olmadığını söylememektir**.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, col, select

from app.auth.dependencies import require

router = APIRouter(tags=["audit"])

#: Tek seferde ihraç edilen tavan. ⚠ Kırpma **sessiz değildir**: yanıt `kirpildi` ve
#: `toplam` taşır — sessizce kırpılmış bir kanıt defteri, eksik bir kanıt defteridir.
TAVAN = 5000


@router.get("/audit/export", dependencies=[Depends(require("contract:read"))])
def audit_export(request: Request, limit: int = 500) -> dict:
    """JSON-LD / PROV-O çerçeveli audit ihracı.

    ⚠ Yetki `contract:read` ve seçim bilinçli: bir kaydı **görmek**, dayandığı raporu
    görmekle eşdeğerdir (`authorize.py`'nin `decision:read` için verdiği aynı gerekçe).
    Denetlenebilirliği admin'e kilitlemek, denetimi **yönetime bağımlı** kılardı.
    """
    from app.audit_zinciri import otel_nitelikleri, zinciri_dogrula
    from control_plane.authorize import Principal
    from control_plane.db import engine
    from control_plane.models import AuditLog

    p: Principal | None = getattr(request.state, "principal", None)
    n = max(1, min(int(limit or 500), TAVAN))
    with Session(engine) as s:
        sorgu = select(AuditLog).order_by(col(AuditLog.ts).desc()).limit(n)
        if p is not None and not p.is_superadmin and p.tenant_id:
            sorgu = sorgu.where(AuditLog.tenant_id == p.tenant_id)
        satirlar = list(s.exec(sorgu))

    kayitlar = [r.model_dump() for r in satirlar]
    return {
        "@context": {
            "prov": "http://www.w3.org/ns/prov#",
            "gen_ai": "https://opentelemetry.io/schemas/gen_ai/",
        },
        "@type": "prov:Bundle",
        "toplam": len(kayitlar),
        "kirpildi": len(kayitlar) >= n,
        # 🔴 Bütünlük raporu BİRLİKTE gider: bir kanıt defterini bütünlük raporu olmadan
        # teslim etmek, "işte kayıtlarım" deyip EKSİK OLUP OLMADIĞINI söylememektir.
        # ⚠ Kayıtlar `ts DESC` geldiği için doğrulama KRONOLOJİK sırada yapılır.
        "zincir_bulgulari": zinciri_dogrula(list(reversed(kayitlar))),
        "kayitlar": [{**k, **otel_nitelikleri(k)} for k in kayitlar],
    }
