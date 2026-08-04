"""FAZ 1.10 — **ESKALASYON MATRİSİ.** Bir uyarı, görülmezse yükselir.

## Neden

Bir eşik aşıldığında bildirim gider — ve orada **biter**. Kimse bakmazsa sistem
*"haber verdim"* der ve susar. Ama bir uyarının **işlevi** haber vermek değil, **bir
karara yol açmaktır**: on iki saat boyunca kimsenin bakmadığı bir alarm, hiç
gönderilmemiş bir alarmla **aynı sonucu** üretir.

## 🔴 YENİ CRON YOK — mevcut 60 sn döngüsü değerlendirir

Yol haritası bunu birebir söylüyor. İkinci bir zamanlayıcı kurmak iki ayrı *"şimdi
saat kaç"* sahibi yaratırdı ve ikisi kaymaya başladığında hangi kuralın ne zaman
koştuğu **bilinemezdi** (`OPERASYON`'un *"aynı kuralın iki sahibi"* sınıfı).

## Karar kuralı

Bir kural **tetiklenmiş** sayılır (`sure_dakika` boyunca eşik aşılı kalmışsa) →
`hedef_rol`'e yükselir. `otomatik_kilitle` ise **ek** bir eylemdir, eskalasyonun
kendisi değil.

⚠ **Kilitleme bu maddede UYGULANMIYOR, yalnız KARAR ÜRETİLİYOR.** Bir hesabı
otomatik kilitlemek **geri alınamaz** bir kullanıcı etkisidir ve FAZ 6'nın *"onaysız
hiçbir yazma"* değişmezine bağlıdır. Kararı üretip **uygulamamak** bir eksiklik değil,
o değişmezin **korunmasıdır** — ve karar `AuditLog`'a yazıldığı için **görünür**dür.
Uygulama kanalı doğduğunda (FAZ 6.1 onay akışı) bağlanır.

## ⚠ Zaman kaynağı DIŞARIDAN verilir

`simdi` parametresi bilinçli: bir zaman kuralını `datetime.now()`'a bağlamak, onu
**test edilemez** kılar ve bu depoda ölçüm araçlarının kendisi defalarca kusurlu çıktı.
Saf fonksiyon, saatini **çağırandan** alır.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

#: Rol merdiveni — `authorize.ROLE_RANK` ile **aynı sıra**. İkinci bir merdiven yazmak,
#: eskalasyonun yetki matrisinden **ayrışması** demekti.
ROL_SIRASI = ("viewer", "analyst", "admin", "owner")


def bir_ust_rol(rol: str | None) -> str | None:
    """Bir üst kademe — tepedeyse `None`.

    `None` *"yükselecek yer yok"* der ve bu bir **son durumdur**: `owner`'da takılı bir
    uyarı artık **insan kararı** bekler, otomatik bir kanal değil.
    """
    try:
        i = ROL_SIRASI.index(str(rol or "viewer"))
    except ValueError:
        i = 0
    return ROL_SIRASI[i + 1] if i + 1 < len(ROL_SIRASI) else None


def tetiklendi_mi(kural: dict[str, Any], *, ilk_asim: datetime | None,
                  simdi: datetime | None = None) -> bool:
    """Eşik `sure_dakika` boyunca **aşılı kaldı mı**?

    🔴 `ilk_asim is None` → **hayır**. Eşik hiç aşılmamışsa süre de işlemez; `None`'ı
    *"çok eski"* saymak, hiç tetiklenmemiş bir kuralı **anında** yükseltirdi.

    ⚠ Gelecekteki bir `ilk_asim` de **hayır**: saat kayması bir eskalasyon gerekçesi
    değildir (`tazelik.kademe`'nin aynı kararı).
    """
    if ilk_asim is None:
        return False
    simdi = simdi or datetime.now(timezone.utc)
    if ilk_asim.tzinfo is None:
        ilk_asim = ilk_asim.replace(tzinfo=timezone.utc)
    gecen = simdi - ilk_asim
    if gecen < timedelta(0):
        return False
    dk = kural.get("sure_dakika")
    dk = dk if isinstance(dk, int) and dk > 0 else 60
    return gecen >= timedelta(minutes=dk)


def degerlendir(kural: dict[str, Any], *, ilk_asim: datetime | None,
                simdi: datetime | None = None) -> dict[str, Any] | None:
    """Bir kuralın **kararı** — ya da `None` (yükselme yok).

    Döner: `{hedef_rol, onceki_rol, kilit_onerisi, ozet}`

    ⚠ `kilit_onerisi` bir **öneridir**, bir eylem değil: bir hesabı otomatik kilitlemek
    **geri alınamaz** ve FAZ 6'nın *"onaysız hiçbir yazma"* değişmezine bağlıdır. Kararı
    üretip uygulamamak bir eksiklik değil, o değişmezin **korunmasıdır**.
    """
    if not tetiklendi_mi(kural, ilk_asim=ilk_asim, simdi=simdi):
        return None
    onceki = str(kural.get("hedef_rol") or "analyst")
    hedef = bir_ust_rol(onceki)
    if hedef is None:
        return None                      # tepede — artık İNSAN kararı bekliyor
    return {
        "onceki_rol": onceki,
        "hedef_rol": hedef,
        "kilit_onerisi": bool(kural.get("otomatik_kilitle")),
        "ozet": f"eskalasyon: {onceki} → {hedef} "
                f"({kural.get('sure_dakika') or 60} dk yanıtsız)",
    }


def kurallari_degerlendir(kurallar, *, asim_zamani, simdi=None) -> list[dict[str, Any]]:
    """Tüm kuralları değerlendirir — **60 sn döngüsünün** çağırdığı tek nokta.

    `asim_zamani` bir **çağrılabilirdir** (`kural → ilk_aşım zamanı | None`): eşiğin ne
    zaman aşıldığını bilmek bu modülün işi **değildir** — o `schedules.py`'nin eşik
    değerlendirmesine aittir. Buraya bir sorgu koymak, eşik mantığının **ikinci bir
    sahibini** doğururdu.
    """
    out: list[dict[str, Any]] = []
    for k in kurallar or []:
        try:
            karar = degerlendir(k, ilk_asim=asim_zamani(k), simdi=simdi)
        except Exception:                                    # noqa: BLE001
            continue                                         # tek kural, ötekini durdurmaz
        if karar:
            out.append({**karar, "kural_id": k.get("id")})
    return out


def dongude_degerlendir(state: Any) -> int:
    """**60 sn döngüsünün** çağırdığı tek giriş — yükselen kural sayısını döner.

    🔴 **YENİ CRON YOK** (yol haritası birebir). Değerlendirici mevcut döngüye bindi;
    ikinci bir zamanlayıcı iki ayrı *"şimdi saat kaç"* sahibi yaratırdı ve ikisi
    kaydığında hangi kuralın ne zaman koştuğu **bilinemezdi**.

    ⚠ Kurallar **yoksa sessizce 0** döner: eskalasyon yapılandırılmamış bir tenant için
    bu bir hata değil bir **durumdur**. Uyarı basmak, kurmamayı bir kusur gibi gösterirdi.

    🔴 Her yükselme `AuditLog`'a yazılır — **kararın kendisi görünür olmalı**, çünkü
    uygulanmıyor: `kilit_onerisi` bir öneridir ve FAZ 6.1'in onay akışına bağlanacak.
    *Uygulanmayan ama kaydedilen bir karar, uygulanan ama kaydedilmeyen bir karardan
    her zaman daha iyidir.*
    """
    try:
        kurallar = list(getattr(state, "eskalasyon_kurallari", None) or [])
        if not kurallar:
            return 0
        kararlar = kurallari_degerlendir(
            kurallar, asim_zamani=getattr(state, "eskalasyon_asim_zamani", lambda _k: None))
        if not kararlar:
            return 0
        from control_plane import audit

        for k in kararlar:
            audit.record(None, "eskalasyon", generated_sql=k["ozet"])
        return len(kararlar)
    except Exception:                                        # noqa: BLE001
        return 0
