"""FAZ 5.10 — **KPI PİN SEMANTİĞİ.** [bayrak: `kpi_pin`]

## Ölçülen boşluk

Pano **var** (`dashboards.py`, `_MAX_PER_USER = 10`) ama **KPI-pin semantiği ayrı
değildi** ve **NL yolu yoktu**: kullanıcı *"bunu panoya sabitle"* diyemiyor, düğmeyi
fareyle aramak zorunda kalıyordu.

## 🔴 PİN BİR KATMAN, BİR PANEL DEĞİL (PK-1 · K5)

Panel tavanı **13/13 dolu** ve bu madde onu **artırmaz**. Pin, var olan pano widget'ının
bir **işaretidir** (`pinned`), yeni bir depo ya da yeni bir ekran değil.

> *Yeni bir yetenek yeni bir panel doğurmaz.* Doğursaydı her yetenek bir ekran ister ve
> ürün bir ayarlar labirentine dönerdi.

## 🔴 YENİ SINIR İCAT EDİLMEZ

Pin edilen KPI `dashboards`'ın **10/kullanıcı** sınırına tabidir. İkinci bir tavan
(*"en fazla 5 pin"*) yazmak, **aynı kuralın iki sahibi** olurdu ve ikisi ayrışırdı — bu
deponun ölçülmüş bir numaralı kusur sınıfı.

## NL yolu — ikinci bir niyet çözücü YAZILMAZ

*"Bunu panoya sabitle"* zaten `eylem.tespit()`'in `_PANO_KALIP` ailesine girer. Bu modül
yalnız **pin işaretini** ekler; niyet tanıma **tek yerde** kalır.
"""

from __future__ import annotations

from typing import Any

#: 🔴 Pin, widget'ın bir **alanıdır** — ayrı bir tablo değil. Ayrı tablo, aynı nesnenin
#: iki kaydı demekti ve silme/geri alma iki yerde yürütülürdü.
PIN_ALANI = "pinned"

#: `dashboards._MAX_PER_USER` ile **aynı** sınır. ⚠ Burada bir sayı **yazılmaz**:
#: kopyalanmış bir sabit, bir gün ötekinden ayrışır.
def azami_pin(dashboards_sinirlari: Any = None) -> int:
    """Pin tavanı — **`dashboards`'ın kendi sınırından okunur**, burada icat edilmez."""
    if dashboards_sinirlari is not None:
        return int(dashboards_sinirlari)
    from app.routers.dashboards import _MAX_PER_USER

    return int(_MAX_PER_USER)


def pinli_mi(widget: dict[str, Any]) -> bool:
    """Widget pin'li mi. ⚠ Alan yoksa **False** — eski widget'lar pin'siz doğar ve bu
    doğrudur: hiç kimse onları pin'lemedi."""
    return bool((widget or {}).get(PIN_ALANI))


def pin_karari(mevcut: list[dict[str, Any]], yeni_widget_id: str,
               *, azami: int | None = None) -> dict[str, Any]:
    """Bir widget'ı pin'lemeye çalışır. Döner: `{izin, sebep, pinli_sayi}`.

    🔴 **Sınır aşıldığında SESSİZCE eskiyi düşürmez.** Bir pin bir **karardır**;
    kullanıcının kendi eliyle koyduğu bir şeyi haber vermeden kaldırmak, ürünün onun
    yerine karar vermesidir. *En eskiyi düşürmek "akıllı" değil, sinsidir.*
    """
    tavan = azami if azami is not None else azami_pin()
    pinli = [w for w in (mevcut or []) if pinli_mi(w)]
    if any(str(w.get("id")) == str(yeni_widget_id) for w in pinli):
        return {"izin": True, "sebep": "zaten pinli", "pinli_sayi": len(pinli)}
    if len(pinli) >= tavan:
        return {
            "izin": False,
            "sebep": (f"Pano sınırın dolu ({tavan}). Yeni bir KPI sabitlemek için "
                      f"önce birini kaldır."),
            "pinli_sayi": len(pinli),
        }
    return {"izin": True, "sebep": "", "pinli_sayi": len(pinli) + 1}


def sirala(widgetlar: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pin'liler **önce**, kendi aralarında **sıra korunur**.

    ⚠ Kararlı sıralama: pin bir **öncelik** işaretidir, bir yeniden düzenleme aracı
    değil. Aynı girdi farklı turlarda farklı sıralanırsa kullanıcı bunu bir değişiklik
    sanar.
    """
    pinli = [w for w in (widgetlar or []) if pinli_mi(w)]
    digerleri = [w for w in (widgetlar or []) if not pinli_mi(w)]
    return pinli + digerleri
