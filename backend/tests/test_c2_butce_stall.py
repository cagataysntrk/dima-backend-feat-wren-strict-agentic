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


def test_HER_BUTCE_CAGRISINDA_SIFIR_EKSEN_GEREKCELI():
    """🔴🔴 `§C2` — **tüm çağrı yerleri**, yalnız varsayılan değil.

    Kardeş test (`test_BUTCE_HICBIR_EKSENDE_uykuda_degil`) yalnız `Butce()`
    **varsayılanını** ölçüyordu. Ölçüldü (08-12, denetim ajanı): **iki CANLI çağrı**
    `sorgu=0` geçiyordu (`routers/ask.py:273` · `answer.py:567`) ve `Butce`'nin kendi
    sözleşmesine göre `0` = **o eksende SINIRSIZ** — yani kardeş testin *adıyla*
    yasakladığı hâl iki yerde mevcuttu ve kapı yeşildi.

    ⊙ İkisi **aynı şey değildi**, ayrım ölçümle çıktı:
    · `answer.py` planlayıcısına `servis:wren` **hiç verilmiyor** → sorgu **koşamaz**;
      eksen sınırsız değil **uygulanamaz** (meşru, gerekçesi yazıldı).
    · `routers/ask.py` planlayıcısına `servis:wren` **veriliyor** → koşabilirdi;
      tavan adım sayısına **eşitlendi** (`sorgu=3`). *Bir tavanın pratikte var olması,
      ilan edilmiş olması demek değildir.*

    ⚠ **VE BU KAPI KENDİ ARACININ YANILMASINDAN DOĞDU:** ilk taramam yalnız
    `Butce(...)` (`ast.Name`) biçimini arıyordu ve **2** çağrı buldu; ürün kodu
    `_planner.Butce(...)` (`ast.Attribute`) yazıyor. Doğru tarayıcı **6** buldu.
    *Bir çağrıyı tek yazım biçiminde aramak, öteki biçimdekileri yok saymaktır.*
    """
    import ast
    import pathlib as _p

    kok = _p.Path(__file__).parent.parent / "app"
    kacak, toplam = [], 0
    for f in sorted(kok.rglob("*.py")):
        try:
            agac = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):            # noqa: PERF203
            continue
        satirlar = f.read_text(encoding="utf-8").splitlines()
        for n in ast.walk(agac):
            if not isinstance(n, ast.Call):
                continue
            # 🔴 İKİ YAZIM BİÇİMİ DE: `Butce(...)` ve `_planner.Butce(...)`
            ad = (n.func.attr if isinstance(n.func, ast.Attribute)
                  else getattr(n.func, "id", None))
            if ad != "Butce":
                continue
            toplam += 1
            sifir = [k.arg for k in n.keywords
                     if isinstance(k.value, ast.Constant) and k.value.value == 0]
            if not sifir:
                continue
            # gerekçe: çağrının hemen üstündeki yorum bloğunda `sorgu=0`/`sınırsız` geçmeli
            once = "\n".join(satirlar[max(0, n.lineno - 9):n.lineno - 1])
            if not any(x in once for x in ("sınırsız", "uygulanamaz", "SINIRSIZ")):
                kacak.append(f"{f.relative_to(kok)}:{n.lineno} → {sifir}")
    assert toplam >= 4, (
        f"⊘ ölçüm tabanı çöktü: yalnız {toplam} `Butce(...)` çağrısı bulundu — "
        "tarayıcı büyük olasılıkla bir yazım biçimini kaçırıyor (ders: `ast.Attribute`).")
    assert not kacak, (
        f"🔴 GEREKÇESİZ SIFIR EKSEN: {kacak}\n"
        "`Butce` sözleşmesi: `0`/`None` = **o eksende sınırsız**. Sınırsız bırakmak "
        "meşru olabilir — ama **yazılı** olmalı: çağrının üstüne neden sınırsız "
        "olduğunu (ör. o kaynağa hiç erişemiyor) yazın.\n"
        "*Bir kapsamı daraltmak meşrudur; daraltmayı yazmamak değildir.*")
