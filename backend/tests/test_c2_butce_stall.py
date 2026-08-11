"""🔴 `§C2` — BÜTÇE VE STALL SAYACI **CANLI**; RAPORUN SAYILARI BAYAT ÇIKTI.

## Raporun iddiası (`§14` FAZ 2 · C2)

> **ÖNCE:** `planner.Butce(adim=3, saniye=10, **sorgu=0**)` **uykuda**; **stall sayacı
> YOK**. Ve ölçüm: planların **%60'ı tek adım**, en uzunu **7** — `AZAMI_ADIM=12` **hiç
> bağlayıcı olmamış**.

## Ölçüm (2026-08-12)

| | rapor | **bugün** |
|---|---|---|
| `Butce.adim` | 3 | **8** |
| `Butce.saniye` | 10 | **30,0** |
| `Butce.sorgu` | **0 — uykuda** | **12 — CANLI** (`if b.sorgu and …` uygulanıyor) |
| stall sayacı | **YOK** | **`ONARIM_TAVANI = 2`** — *«Magentic-One stall ≤2»*, `plan_garson` |
| `AZAMI_ADIM` | *«hiç bağlayıcı olmamış»* | **12**, `plan_kosucu.dogrula`'da **koşmadan önce** uygulanıyor |
| `AZAMI_SORGU` | — | **8** (`Butce`'nin sorgu ayağının plan katmanındaki karşılığı) |

`Planlayici._kis()` tavanı aşınca `ButceAsimi` **fırlatıyor** ve sınıfın kendi docstring'i
kısmi-cevap kalıbını yazıyor: *«o ana kadarki adımlar GEÇERLİ — kısmi cevap ver»*.

⊙ Ve `%60 tek adım` rakamı `§A13` ile zaten çürümüştü (**%21**); `§17.6` bu yüzden
`✅ TEŞHİS BAYAT` diye işaretli.

🔴 **Stall sayacının bu oturumda geldiği yer:** `§B4` onarım döngüsü. C2'nin kendi satırı
*«serbest döngüye (B4) geçerken **pazarlık dışı**»* diyordu — B4 canlıya alınırken tavan
onunla birlikte kondu. *Bir şartı, şartı doğuran işi yaparken ödemek en ucuzudur.*

## Neden bu kapı — sayılar SESSİZCE geri düşebilir

Bunlar **güvenlik tavanlarıdır**. Biri `sorgu=0` yazarsa (raporun tarif ettiği eski hâl)
koruma **sessizce** kalkar: hiçbir test kırılmaz, hiçbir cevap bozulmaz, yalnız kaçak bir
döngü artık durdurulmaz. Bu dosya o sessizliği yasaklar.

*Uygulanmayan bir tavan, olmayan bir tavandan daha kötüdür: birincisine güvenilir.*
"""

from __future__ import annotations

import ast
import inspect

import pytest

from app.plan_garson import ONARIM_TAVANI
from app.plan_kosucu import AZAMI_SORGU, PlanHatasi
from app.plan_semasi import AZAMI_ADIM
from app.planner import Butce, ButceAsimi, Planlayici


def test_BUTCE_HICBIR_EKSENDE_uykuda_degil():
    """🔴 `0`/`None` = o eksende **sınırsız** (sınıfın kendi sözleşmesi). Raporun tarif
    ettiği `sorgu=0` hâli bir korumanın **kapalı** olması demekti."""
    b = Butce()
    assert b.adim > 0, "adım tavanı uykuda"
    assert b.saniye > 0, "süre tavanı uykuda"
    assert b.sorgu > 0, "🔴 sorgu tavanı uykuda — raporun tarif ettiği eski hâl geri geldi"


def test_TOKEN_ekseni_SINIRSIZ_ve_GEREKCELI():
    """⚠ Tek sınırsız eksen `token` ve gerekçesi **yazılı**: telemetri boş. *Ölçülmemiş
    bir eşik koymak, kapsamı gerekçesiz daraltmak olurdu.* Gerekçe silinirse bu test
    kırılır ve karar yeniden verilir."""
    assert Butce().token == 0
    d = (Butce.__doc__ or "")
    assert "ölçülemiyor" in d or "telemetri" in d, "sınırsızlığın gerekçesi kayboldu"


def test_STALL_SAYACI_iki():
    """Magentic-One eşiği. `§B4` onarım döngüsünün tavanı ile **aynı sayı** olması
    tesadüf değil — ikisi aynı korumadır."""
    assert ONARIM_TAVANI == 2


def test_UZUN_PLAN_kosmadan_ONCE_reddediliyor():
    """*Bir planı koşarken reddetmek, hiç kurmamaktan pahalıdır* — ilk adım o ana kadar
    çoktan koşmuş olurdu.

    ⚠ **Hangi tavanın bağladığını iddia ETMİYORUZ, bağlanmasını iddia ediyoruz.** İlk
    sürüm `AZAMI_ADIM` (12) bekliyordu ve kırmızı verdi: 13 `SORGU` adımında **sorgu
    tavanı (8) daha önce** bağlıyor. Ürün doğruydu — *dar olan bağlar* — kusur testin
    varsayımındaydı. Bu turda **altıncı** kez aracı ürünü suçladı.
    """
    from app.plan_kosucu import dogrula
    adim = {"fiil": "SORGU", "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}}
    with pytest.raises(PlanHatasi) as e:
        dogrula({"adimlar": [dict(adim) for _ in range(AZAMI_ADIM + 1)]})
    mesaj = str(e.value)
    assert "bütçe" in mesaj or "tavan" in mesaj, mesaj
    # Ve hangi tavan bağlarsa bağlasın, sayısı mesajda **yazılı** olmalı: gerekçesiz bir
    # red, kullanıcıya da garsona da onarılacak bir şey vermez (`ADR-0020`).
    assert any(str(x) in mesaj for x in (AZAMI_ADIM, AZAMI_SORGU)), mesaj


def test_SORGU_TAVANI_plan_katmaninda_da_var():
    """İki katman, **tek** koruma: `Butce.sorgu` ajan yolunda, `AZAMI_SORGU` plan
    yolunda. Biri düşerse öteki yolu korumasız kalır."""
    assert AZAMI_SORGU > 0
    assert AZAMI_SORGU <= Butce().sorgu, (
        "plan katmanı ajan bütçesinden GEVŞEK olamaz — dar olan bağlayıcıdır")


def test_TAVAN_ASIMI_ISTISNA_firlatiyor():
    """Sessiz kısma yok: tavan aşımı bir **istisnadır** ve çağıran onu yakalayıp kısmi
    cevap verir (`Planlayici` docstring'indeki kalıp)."""
    src = inspect.getsource(Planlayici)
    assert "raise ButceAsimi" in src, "tavan aşımı sessizce yutuluyor olabilir"
    assert "ButceAsimi" in (Planlayici.__doc__ or ""), "kısmi-cevap kalıbı belgesiz"


def test_KISILMA_NEDENI_kayda_geciyor():
    """`ADR-0020` — sessiz yutma yok: neden **hem** kütüğe **hem** koşum kaydına yazılır."""
    src = inspect.getsource(Planlayici)
    t = ast.parse(src.lstrip())
    kis = next((n for n in ast.walk(t)
                if isinstance(n, ast.FunctionDef) and n.name == "_kis"), None)
    assert kis, "_kis kayboldu"
    govde = "\n".join(ast.dump(x) for x in kis.body)
    assert "kisilma_nedeni" in govde and "_log" in govde
