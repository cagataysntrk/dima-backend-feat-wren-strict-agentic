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
    schema = wren_for_request(request).schema()
    adaylar = oneri.ara(q, schema, izinliler=izinliler)
    return {
        "adaylar": [
            {"kimlik": a.kimlik, "etiket": a.etiket, "cube": a.cube, "kip": a.kip}
            for a in adaylar
        ],
        # 🅖 Kip **beyan edilir**: gömücü soğuksa liste leksik'tir ve kullanıcı arayüzü
        # bunu (isterse) söyleyebilir. Sessizce kalitesi düşen bir liste, düşmediğini
        # sandıran bir listedir.
        "kip": adaylar[0].kip if adaylar else "yok",
        # `5.7/④` — indeksin durumu **beyan edilir**: `taze` · `yok` (ilk istek, henüz
        # kurulmadı) · `kapali` (gömücü yok → liste leksiktir). Bayat bir hâl **yoktur**:
        # önbellek şema sürümüyle anahtarlıdır, eski sürüm okunamaz 🅐.
        "indeks": oneri.indeks_durumu(schema),
    }


@router.post("/oneri/tik", dependencies=[Depends(require_company)])
def oneri_tik(request: Request, govde: dict) -> dict:
    """🔴 `FAZ 8.1` — **tıklama kaydı**: `(ham ifade → seçilen alan → konum)`.

    ⊘ **Yeni bir tablo AÇILMADI** 🆝: kayıt `InteractionLog`'a `kind="oneri_tik"` ile
    düşer — denetim kanalı **zaten** bu; ikinci bir depo kurmak, aynı olayın iki
    sahibi demekti (`KAT-1`).

    ⚠ `§101.1` — öneri katmanı **cevabı bozmaz**: kayıt başarısız olursa istek yine
    `{"kaydedildi": false}` ile döner. Bir telemetri hatası bir ürün hatası **değildir**.

    ⚠ Sinyalin **sınıfı burada hesaplanır ama karar burada verilmez**: `hasat.sinyal`
    saf bir fonksiyondur ve **tek sahibidir**; bu uç yalnız onu **çağırır**.
    """
    from app import hasat

    t = hasat.Tiklama(
        ham_ifade=str(govde.get("ham_ifade") or "")[:200],
        gosterilen=tuple(str(x)[:80] for x in (govde.get("gosterilen") or [])[:7]),
        konum=int(govde.get("konum", -1)),
    )
    sinif = hasat.sinyal(t)
    kaydedildi = False
    try:                                                   # pragma: no cover - IO
        from control_plane.db import get_session
        from control_plane.models import InteractionLog

        principal = getattr(request.state, "principal", None)
        with next(get_session()) as oturum:
            oturum.add(InteractionLog(
                tenant_id=getattr(principal, "tenant_id", None),
                user_id=getattr(principal, "user_id", None),
                question=t.ham_ifade,
                kind="oneri_tik",
                source="oneri",
                note=hasat.not_yaz(t),   # ㊲ biçimin tek sahibi `hasat`
            ))
            oturum.commit()
        kaydedildi = True
    except Exception:                                      # noqa: BLE001 — §101.1
        kaydedildi = False
    # 🅖 Sinıf **her hâlde** dönülür: kayıt tutulamasa bile istemci ne olduğunu bilir.
    return {"sinyal": sinif, "kaydedildi": kaydedildi}
