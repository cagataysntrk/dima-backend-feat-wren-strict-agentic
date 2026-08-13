r"""🔴 `FAZ 6.1` — **`GET /oneri`**: yazarken-ara ucu.

`app/oneri.py` motorunu HTTP'ye açar. **İnce bir çevirici**: karar da, yetki süzmesi de
motorun içindedir; burası yalnız isteği çözer ve cevabı biçimler.

## Neden bu uç motorla AYNI DEMETTE geliyor

`FAZ 3`'ün bulgusu: bu depoda *«yazılmış ama bağlanmamış»* **beş kez** ölçüldü, ve
`test_g_yetim_modul_kapisi` bunu bir **borç tavanı** ile tutuyor — doktrini açık:
*«kapı yalnız artışı yasaklar.»* Motor bir tur önce doğdu (ön koşulu bir **ölçüme**
bağlıydı 🅕); kapı *«bağla»* dedi ve **haklıydı**. Bu dosya o bağlamadır.

⚠ Ve uç **tek başına** da yetmez: `test_g_yetim_uc_kapisi` bir ucun **FE'de geçmesini**
şart koşar (tavan **8**). O yüzden `6.2` (FE tüketicisi) bu commit'in **içinde**.

## ⊘ Ne YAPMIYOR

* Sorgu **koşmuyor** — dönen aday bir **ad**dır, bir sayı değil. Sayıyı küp koyar (`§38.4`).
* LLM **çağırmıyor** (`E-8`: sıcak yolda seri ikinci tur yok).
* `/ask` yoluna **dokunmuyor**.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request

from app.auth.dependencies import require_company

router = APIRouter(tags=["oneri"])


@router.get("/oneri", dependencies=[Depends(require_company)])
def oneri_ara(request: Request, q: str = Query("", max_length=120)) -> dict:
    """Katalogdan yazarken-ara adayları.

    🔴 **Yetki motorda süzülür, burada değil** (`KAT-1`): `app/oneri.terimler()`
    `katman_b.karar`'ı çağırır ve **sıralamadan önce** süzer. Buradaki tek iş
    allowlist'i **almak**tır (`katman_b.allowlist`), yorumlamak değil.
    """
    from app import katman_b, oneri
    from app.company_registry import wren_for_request

    principal = getattr(request.state, "principal", None)
    izinliler = katman_b.allowlist(request, principal)
    adaylar = oneri.ara(q, wren_for_request(request).schema(), izinliler=izinliler)
    return {
        "adaylar": [
            {"kimlik": a.kimlik, "etiket": a.etiket, "cube": a.cube, "kip": a.kip}
            for a in adaylar
        ],
        # 🅖 Kip **beyan edilir**: gömücü soğuksa liste leksik'tir ve kullanıcı arayüzü
        # bunu (isterse) söyleyebilir. Sessizce kalitesi düşen bir liste, düşmediğini
        # sandıran bir listedir.
        "kip": adaylar[0].kip if adaylar else "yok",
    }
