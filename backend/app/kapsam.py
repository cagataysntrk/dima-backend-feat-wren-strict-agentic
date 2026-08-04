"""FAZ 2.3 — **DEPARTMAN = MERCEK, KÜP DEĞİL.** [bayrak: `kapsam_mercegi`]

## Neden bir *"satış küpü"* açmıyoruz

*"Bize bir satış küpü lazım"* isteğinin **meşru karşılığı** bir küp değil bir **kapsam
parametresidir** (Plan 3 §7.8: *"kapsam parametresi, yeni motor değil"*). Bir departmanı
küp yapmak, o departmanın **tüm sözlüğünü** kimliğe yapıştırır — `surdurulebilirlik`
felaketinin kökü tam buydu ve ölçüldü: kimliği sadeleştirme denemesi erişimi **%64 → %56**
düşürdü.

Mercek **yeni `base_object` DOĞURMAZ**. Aynı küpler, aynı sayılar; yalnız **hangilerinin
gösterileceği** değişir.

## 🔴 MERCEK BİR GÖRÜNÜRLÜK ARACIDIR, BİR GÜVENLİK SINIRI DEĞİL

Bu ayrım maddenin en kritik satırı: **merceği kapatmak yetki AÇMAZ**. Sınır her zaman
`authorize()` + RLS'tir (§D). Merceği bir güvenlik katmanı gibi kullanmak, kullanıcının
*"kapsamı genişlet"* düğmesini bir **yetki yükseltme** aracına çevirirdi.

⚠ Bu yüzden `daralt()` **asla** yetkiyi genişletmez, yalnız **görünen kümeyi küçültür** —
ve kapı bunu tersinden de doğrular: her mercek çıktısı, mercek kapalıyken görünen kümenin
**alt kümesidir**.

## Üç seviye

| kapsam | ne gösterir | kim |
|---|---|---|
| `departman` | kullanıcının departmanına **atanmış** metrikler | herkes |
| `genel` *(varsayılan)* | bugünkü **tam** katalog | herkes |
| `portfoy` | **çok-tenant** birleşik görünüm | 🔴 yalnız çok-tenant yetkisi |
"""

from __future__ import annotations

from typing import Any

KAPSAMLAR = ("departman", "genel", "portfoy")

#: Varsayılan: **bugünkü davranış**. Yapılandırılmamış her kurulum tam katalogu görür.
VARSAYILAN = "genel"

#: 🔴 `portfoy` **çok-tenant** bir görünümdür ve bu deponun çok-tenant sınırı bir eylem
#: adı değil, `Principal.is_superadmin` **bayrağıdır** (ADR-0015 K7 · `authorize.py`).
#: ⚠ **Bu bir düzeltmedir:** ilk yazımda `"tenant:read_all"` diye bir izin **uydurmuştum**
#: ve kapı onu yakaladı — matriste öyle bir eylem yok. *Var olmayan bir izne dayanan
#: kontrol, hiç yapılmayan bir kontroldür:* `izinli_mi` her zaman `False` dönerdi ve
#: `portfoy` **hiç kimseye** açılmazdı. Sessizce kapalı bir özellik, kapalı olduğunu
#: söylemeyen bir özelliktir.
PORTFOY_SUPERADMIN_ISTER = True


def gecerli(kapsam: Any) -> str:
    """Bilinmeyen/boş kapsam → **varsayılan**.

    ⚠ Geçersiz bir kapsamı **hata** yapmak, bir yazım hatasını cevapsızlığa çevirirdi;
    *daha geniş* bir kapsama düşürmek ise sessizce daha çok şey göstermek olurdu. İkisi
    de yanlış: varsayılan **bugünkü** davranıştır ve o zaten en geniş **meşru** kümedir.
    """
    k = str(kapsam or "").strip().lower()
    return k if k in KAPSAMLAR else VARSAYILAN


def izinli_mi(kapsam: str, principal: Any) -> bool:
    """`portfoy` **yalnız** superadmin'e. Ötekiler herkese açık.

    🔴 Bu **tek** yetki kontrolü mercekte vardır ve o da bir **genişletmeyi** engeller,
    bir daraltmayı değil: `portfoy` kullanıcıya **başka tenant'ların** verisini gösterme
    *isteğidir*; gerçek sınırı yine `authorize()` + RLS koyar, bu yalnız **isteği**
    kapıda tutar.
    """
    if kapsam != "portfoy":
        return True
    return bool(getattr(principal, "is_superadmin", False))


def daralt(schema: dict[str, Any], kapsam: str, *, departman: str | None) -> list[str]:
    """Mercekte **görünecek** cube adları. Mercek kapalıysa/`genel` ise **hepsi**.

    🔴 **Yeni `base_object` DOĞURMAZ** ve hiçbir sayıyı değiştirmez: dönen şey bir **ad
    listesidir**. Aynı küpler, aynı ifadeler, aynı sonuçlar.

    ⚠ Departman ataması **metrik kaydı üstünde** yaşar (`cube_meta["departman"]`),
    cube'un **kimliğinde** değil — kimliğe yazmak, tam olarak kaçındığımız şey olurdu.
    Ataması **olmayan** küp `departman` merceğinde de **görünür**: atanmamışlık bir
    *"gizle"* kararı değildir ve sessizce gizlemek, kullanıcının katalogdan haberi
    olmamasına yol açardı.
    """
    hepsi = [str(c.get("name")) for c in (schema.get("cubes") or []) if c.get("name")]
    if kapsam != "departman" or not departman:
        return hepsi
    hedef = str(departman).strip().lower()
    return [str(c.get("name")) for c in (schema.get("cubes") or [])
            if c.get("name") and (
                not c.get("departman")
                or str(c.get("departman")).strip().lower() == hedef)]
