"""FAZ 3.3 — **TERFİ KUYRUĞU KAPANIŞ ORANI.** Açılan boşlukların kaçı kapanıyor?

## Ölçülen boşluk

MIMARI §9 ilke 4: *"her Discovery cevabı bir **kapsam boşluğunun belgesidir**"* — ve o
belge `MeasureCandidate` olarak kuyruğa giriyor. Ama **kaçının kapandığını kimse
ölçmüyordu**: kuyruk büyüyor mu, eriyor mu, yoksa yalnız **birikiyor** mu?

*Ölçülmeyen bir kuyruk, kuyruk değil bir çöp kutusudur.*

## 🔴 ORAN NEDEN "onaylanan / toplam" DEĞİL

Bir adayın **reddedilmesi de kapanıştır**: *"bu bir metrik değil"* kararı, boşluğun
kapandığı anlamına gelir — kuyruktan çıkmıştır ve bir daha bakılmayacaktır. Yalnız
onayları saymak, **doğru reddi bir başarısızlık gibi** gösterirdi ve incelemeciyi
onaylamaya iterdi.

    kapanış = (onaylanan + reddedilen + kullanımdan_kaldırılan) / toplam

⚠ `draft` **açık** sayılır: henüz kimse bakmamış demektir. `pending_review` de açıktır —
*bakılmayı bekleyen bir karar, verilmiş bir karar değildir.*

## ⚠ Bu modül ORAN HESAPLAR, EŞİK KOYMAZ

Eşik bir **iş kararıdır** (haftada kaç aday kapatılmalı?) ve veri olmadan konulamaz. Bugün
ölçüm başlıyor; eşik, taban oluştuktan sonra bir sonraki turun işi. *Ölçülmemiş bir eşik,
uydurulmuş bir hedeftir.*
"""

from __future__ import annotations

from typing import Any

#: `MeasureCandidate.status` sözlüğü (`control_plane/models.py`) — **oradaki adlar**.
ACIK_DURUMLAR = ("draft", "pending_review")
KAPALI_DURUMLAR = ("approved", "rejected", "deprecated")


def oran(sayimlar: dict[str, int]) -> dict[str, Any]:
    """`{durum: adet}` → kapanış raporu. **Saf fonksiyon** — DB'siz test edilebilir.

    Döner: `{toplam, acik, kapali, kapanis_orani, dagilim}`

    🔴 `toplam == 0` → `kapanis_orani = None`, **`0.0` değil**: hiç aday yokken *"%0
    kapanış"* demek, çalışmayan bir kuyruğu **başarısız** gibi gösterirdi. *Yokluk bir
    başarısızlık değildir.*
    """
    dagilim = {k: int(v or 0) for k, v in (sayimlar or {}).items()}
    toplam = sum(dagilim.values())
    acik = sum(dagilim.get(d, 0) for d in ACIK_DURUMLAR)
    kapali = sum(dagilim.get(d, 0) for d in KAPALI_DURUMLAR)
    # ⚠ Bilinmeyen bir durum ne açık ne kapalı sayılır ama TOPLAMA girer — sessizce
    # düşürmek oranı olduğundan yüksek gösterirdi.
    return {
        "toplam": toplam,
        "acik": acik,
        "kapali": kapali,
        "kapanis_orani": round(kapali / toplam, 4) if toplam else None,
        "dagilim": dagilim,
    }


def rapor_metni(r: dict[str, Any]) -> str:
    """`lab/reports/terfi_kapanis.md` gövdesi — insan-okur özet."""
    o = r.get("kapanis_orani")
    yuzde = "⊘ ÖLÇÜLEMEDİ (hiç aday yok)" if o is None else f"%{o * 100:.1f}"
    satirlar = [
        "# Terfi kuyruğu — kapanış oranı",
        "",
        "> *Ölçülmeyen bir kuyruk, kuyruk değil bir çöp kutusudur.*",
        "",
        f"- **Kapanış oranı:** {yuzde}",
        f"- Toplam aday: **{r.get('toplam', 0)}** · açık **{r.get('acik', 0)}** · "
        f"kapalı **{r.get('kapali', 0)}**",
        "",
        "| durum | adet |",
        "|---|---|",
    ]
    satirlar += [f"| `{k}` | {v} |" for k, v in sorted((r.get("dagilim") or {}).items())]
    satirlar += [
        "",
        "⚠ **Reddedilen de KAPANIŞTIR:** *\"bu bir metrik değil\"* kararı boşluğun "
        "kapandığı anlamına gelir. Yalnız onayları saymak, doğru reddi bir başarısızlık "
        "gibi gösterir ve incelemeciyi onaylamaya iterdi.",
        "",
        "⚠ **Eşik BU TURDA KONMADI:** eşik bir iş kararıdır ve veri olmadan konulamaz. "
        "Ölçüm bugün başlıyor; taban oluştuktan sonra eşik bir sonraki turun işi. "
        "*Ölçülmemiş bir eşik, uydurulmuş bir hedeftir.*",
    ]
    return "\n".join(satirlar) + "\n"


def sayimlari_topla(oturum: Any, *, tenant_id: Any = None) -> dict[str, int]:
    """DB'den `{durum: adet}`. Erişilemezse **boş** — ve boş, `⊘` demektir.

    ⚠ Hata **yutulmaz ama akışı kırmaz**: bir ölçüm aracının çökmesi, ölçtüğü şeyi
    durdurmamalı. Ama boş sonuç *"kapanış %0"* diye de raporlanmaz (bkz. `oran`).
    """
    try:
        from sqlmodel import select

        from control_plane.models import MeasureCandidate

        sorgu = select(MeasureCandidate)
        if tenant_id is not None:
            sorgu = sorgu.where(MeasureCandidate.tenant_id == tenant_id)
        out: dict[str, int] = {}
        for c in oturum.exec(sorgu):
            out[str(c.status)] = out.get(str(c.status), 0) + 1
        return out
    except Exception:                                        # noqa: BLE001
        return {}
