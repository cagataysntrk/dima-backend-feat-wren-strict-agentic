r"""🔴🔴 `§G` — **YETİM UÇ KAPISI**: *«geliştirdik, uç açtık, ön uç hiç çağırmadı.»*

## Kullanıcının teşhisi — ve neden MODÜL kapısı yetmedi

> *«Ne nereye bağlanmış karışıyor, hatta bazen geliştirip bağlanmıyor, bu da fark
> edilmiyor. Buna mutlak bir çözüm bulunmalı.»*

`test_g_yetim_modul_kapisi.py` bunun **yarısını** kapattı: bir modül yazılıp `app/`
içinden hiç import edilmezse kırmızı olur. Ama bir modül **import edilip** bir HTTP ucu
açabilir ve o uç **hiçbir ön uç tarafından çağrılmayabilir**. Modül kapısı bunu
**göremez** — modül bağlıdır, bağlı olmayan **uçtur**.

> 🅣 *Bir kapının yokluğu, aradığın yerin kapsamıyla sınırlıdır.*

## Ölçüm (2026-08-12, kendi koşumum)

```
app/routers/ altında HTTP ucu (ast, @router.<fiil>)   : 77
statik yolu ön uç kaynağında HİÇ geçmeyen             :  8
```

⚠ **İlk ölçütüm NAİFTİ ve onu düzelttim** (㊳): yolun **son parçasını** ön uç metninde
aramıştım (`/ask/{id}/cube` → `"cube"`), ki bu tesadüfen eşleşir ve **4** gibi düşük bir
sayı verir. Doğru ölçüt yolun **statik önekidir** (`/stats/plan` → `/stats/plan`), ve o
**8** diyor. *Her şeyi eşleştiren bir ölçüt hiçbir şeyi işaretlemez* 🆊.

## Sekizi de MEŞRU — ve üç ayrı sebeple

Bu kapı bir *«hepsi bağlansın»* dayatması **değildir**. Bir ucun ön uç tüketicisi
olmaması üç hâlde **doğrudur**: altyapı yoklaması · **başka bir istemci** (ajan/MCP) ·
işletme aracı. Kapının işi bunları **yasaklamak** değil, **beyansız** olanı yakalamaktır.

> 🆏 *Bir yetimliğin gerekçesi «neden bağlı değil»i değil, «bağlı olmadan nasıl
> çalışıyor»u anlatmalıdır.*
"""

from __future__ import annotations

import ast
import pathlib

import pytest

_KOK = pathlib.Path(__file__).resolve().parents[1]
_FE = _KOK.parent / "dima-frontend-demo-master" / "src"

_FIILLER = {"get", "post", "put", "patch", "delete"}

#: 🔴 **MEŞRU YETİM UÇLAR — ve her birinin ÇAĞIRANI.** Anahtar: statik yol öneki.
#: Buraya bir yol girecekse **kim çağırıyor** da girer; boş gerekçe kabul edilmez.
UC_YETIM_MESRU: dict[str, str] = {
    "/health": "altyapı yoklaması: konteyner sağlık kontrolü çağırır, ön uç değil",
    "/health/ready": "altyapı yoklaması: hazırlık probu (lifespan bitti mi) — ön uç değil",
    "/mcp/tools": "BAŞKA İSTEMCİ: MCP yüzeyi — çağıranı dış ajan, ön uç DEĞİL (§38.3 D13)",
    "/mcp/call": "BAŞKA İSTEMCİ: MCP araç çağrısı — çağıranı dış ajan (yayımlanan 29 araç)",
    "/stats/plan": "işletme aracı: plan onarım oranı — `lab/` ve curl okur (§B4 ölçümü)",
    "/stats/gecikme": "işletme aracı: gecikme bütçesi — `lab/` ve curl okur",
    # ⚠ İlk gerekçem *«AYNI fonksiyon, tek sahipli»* diyordu — doğru ama **çağıranı
    # söylemiyordu**, ve aşağıdaki yüklem onu **kırmızıya çevirdi**. Kapı ilk koşumunda
    # kendi yazarını yakaladı: bir gerekçe, ne olduğunu değil **kimin kullandığını**
    # anlatmalıdır 🆏.
    "/stats/katalog": "işletme aracı: katalog envanterini `lab/` araçları ve curl okur; "
                      "aynı fonksiyonu MCP `katalog` aracı çağırır (tek sahip, §C3)",
    "/dry-plan": "motor doğrulaması: üretilen SQL'i çalıştırmadan plan eder; çağıranı "
                 "backend'in kendi doğrulama yolu ve `lab/`, ön uç değil",
}

#: 🔴 **BORÇ TAVANI.** Bugün 8. Artış = *«bir uç daha açıldı, kimse çağırmıyor»*.
AZAMI_YETIM_UC = 8

_ONBELLEK: list[tuple[str, str, str]] | None = None


def _uclar() -> list[tuple[str, str, str]]:
    """`(modül, fiil, tam yol)` — **bir kez** ayrıştırılır.

    ⚠ Kapının maliyeti ölçüldü: 19 dosya, tek geçiş — **0,1 sn'nin altında**. Modül
    kapısının ilk yazımı 138 × tam tarama yapıp **2 dakikada bitmemişti**; aynı hatayı
    tekrarlamamak için önbellek baştan kondu.
    """
    global _ONBELLEK
    if _ONBELLEK is not None:
        return _ONBELLEK
    import re

    out: list[tuple[str, str, str]] = []
    for p in sorted((_KOK / "app" / "routers").rglob("*.py")):
        src = p.read_text(encoding="utf-8")
        ic = re.search(r'APIRouter\([^)]*prefix\s*=\s*"([^"]*)"', src, re.S)
        base = ic.group(1) if ic else ""
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for d in node.decorator_list:
                f = d.func if isinstance(d, ast.Call) else d
                if isinstance(f, ast.Attribute) and f.attr in _FIILLER:
                    yol = (d.args[0].value if isinstance(d, ast.Call) and d.args
                           and isinstance(d.args[0], ast.Constant) else "")
                    out.append((p.stem, f.attr, (base + yol) or "/"))
    _ONBELLEK = out
    return out


def _statik(yol: str) -> str:
    """`/ask/{id}/cube` → `/ask` — **yol parametresinden önceki** sabit kısım.

    ⚠ ㊳ Ölçütün kendisi bir karardır: son parçayı aramak (`"cube"`) tesadüfen eşleşir
    ve borcu **olduğundan az** gösterir. Statik önek ön ucun gerçekten yazdığı şeydir.
    """
    parca: list[str] = []
    for s in yol.strip("/").split("/"):
        if s.startswith("{"):
            break
        parca.append(s)
    return "/" + "/".join(parca) if parca else "/"


def _fe_metni() -> str:
    if not _FE.is_dir():
        pytest.skip(
            "⊘ ÖN UÇ MOUNT'U YOK — bu kapı ÖLÇMEDEN atlandı. Koşum satırına "
            "`-v \"$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro\"` "
            "eklenmeli. (Bir kapıyı ortam eksiğinde susturmak dürüstlüktür; o susmayı "
            "DUYURMAMAK kapsamı sessizce kırpmaktır.)")
    return " ".join(x.read_text(encoding="utf-8", errors="ignore")
                    for x in _FE.rglob("*") if x.suffix in {".ts", ".tsx"})


def _yetimler() -> list[str]:
    fe = _fe_metni()
    return sorted({_statik(y) for _m, _f, y in _uclar() if _statik(y) not in fe})


def test_OLCUM_TABANI_UC_SAYISI_ANLAMLI():
    """⊘ **Boş yeşil avı.** Ayrıştırma çökerse aşağıdaki yüklemler hiçbir şey ölçmez."""
    n = len(_uclar())
    assert n >= 50, f"⊘ ölçüm tabanı çöktü: {n} HTTP ucu bulundu (beklenen ≥50)"


def test_HER_UCUN_YA_TUKETICISI_YA_GEREKCESI_VAR():
    """🔴🔴 **ASIL KAPI.** Yeni bir uç açılıp ön uç ondan haberdar olmazsa burada görünür.

    ⊙ Bugün **8/77**; hepsi `UC_YETIM_MESRU`'da **çağıranıyla** kayıtlı. Dokuzuncusu
    doğduğu gün yazan kişi **iki şeyden birini** yapmak zorunda kalır: ya ön ucu
    **bağlar**, ya **kimin çağırdığını yazar**.

    *Bir uç açıp bağlamamak bir hata değildir; bağlamadığını söylememektir.*
    """
    beyansiz = [y for y in _yetimler() if y not in UC_YETIM_MESRU]
    assert not beyansiz, (
        f"🔴 BEYANSIZ YETİM UÇ: {beyansiz}\n"
        "Bu uçlar `app/routers/` altında açık ama statik yolları ön uç kaynağında "
        "(`dima-frontend-demo-master/src`) **hiç geçmiyor** — yani yazıldılar, "
        "çağrılmadılar.\n"
        "→ Ya ön ucu bağla, ya `UC_YETIM_MESRU`'ya **çağıranıyla** yaz.")


def test_MESRU_LISTE_BAYATLAMIYOR():
    """⚠ **Ters yön.** Bir uç ön uca bağlandığı hâlde listede kalırsa, liste bir aklama
    kağıdına döner ve **bir sonraki gerçek yetimi de örter**.

    🆍 *Bir muafiyet listesi, kendini temizlemiyorsa bir muafiyet değil bir perdedir.*
    """
    bayat = sorted(set(UC_YETIM_MESRU) - set(_yetimler()))
    assert not bayat, (
        f"🔴 `UC_YETIM_MESRU` BAYATLADI: {bayat} artık ön uçtan çağrılıyor — listeden "
        "çıkarılmalı.")


def test_HER_GEREKCE_CAGIRANI_SOYLUYOR():
    """⚠ Boş ya da *«gerekmiyor»* diyen bir gerekçe, gerekçesizlikten kötüdür: okuyan
    onu **düşünülmüş** sanır. 🆏 Gerekçe **kimin çağırdığını** söylemeli."""
    for yol, sebep in UC_YETIM_MESRU.items():
        assert len(str(sebep).strip()) >= 30, (
            f"🔴 `{yol}` için gerekçe anlamsız kısa: {sebep!r}")
        assert "çağır" in sebep or "okur" in sebep or "probu" in sebep, (
            f"🔴 `{yol}` gerekçesi ÇAĞIRANI söylemiyor — *«bağlı olmadan nasıl "
            f"çalışıyor»* cevapsız: {sebep!r}")


def test_YETIM_UC_SAYISI_ARTMIYOR():
    """🔴 **BORÇ TAVANI.** Bugün **8**. Artış, *«bir uç daha açıldı, kimse çağırmıyor»*
    demektir — `UC_YETIM_MESRU`'ya ad eklemek kapıyı yeşil yapar ama **bu yüklem** borcu
    görünür tutar. ⊙ Azalma serbesttir ve beklenen yöndür. 🆇"""
    n = len(_yetimler())
    assert n <= AZAMI_YETIM_UC, (
        f"🔴 yetim uç sayısı {n} (tavan {AZAMI_YETIM_UC}) — yeni bir uç açılıp ön uca "
        "bağlanmamış.")
