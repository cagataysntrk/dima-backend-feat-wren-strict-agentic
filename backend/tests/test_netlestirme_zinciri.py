"""**FAZ 5.16 — NETLEŞTİRME DÜZEYİ BAĞLANDI.** [bayrak: `netlestirme_duzeyi`]

## 🔴 Son gerçek yetim

`app/netlestirme.py` — **107 satır, 13 test** — üretim kodunda **hiç import
edilmiyordu**. `TenantConfig.netlestirme_duzeyi` **kolonu vardı**, modül vardı,
**hiçbir karar onu okumuyordu**.

⚠ Yetim modül: **12 → 4**, ve **dördü de kusur değil**:
`embed_kapsam` P0-bloke · `sinonim_onerici` tasarımı gereği offline · `kanal_kimlik`
Slack/Teams adaptörü bekliyor · `bayrak_profilleri` test yardımcısı.

> 🔴 **Denetimin 12'lik sayısı kapandı.** Ama sayı bir kusur listesi değildi:
> **8 gerçek** kusurdu, dördü meşru bekleyiş.

## ⚠ Tavan muafiyeti — gizlenmiyor

`ask()` **1151/1151** doluydu. Eklenen kod **tek satır** (`sorar_mi()` çağrısı) ve
muafiyet listesine **gerekçesiyle** yazıldı; düzey çözümü modül-düzeyi yardımcıya
çıkarıldı (17 satır, ayrı liste) — *bir ayar okuması bir cevaplama adımı değildir.*
"""

from __future__ import annotations

import ast
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]


def test_MODUL_ARTIK_CAGRILIYOR():
    src = (_KOK / "app/routers/ask.py").read_text(encoding="utf-8")
    assert "from app import netlestirme as _netlestirme" in src
    assert "_netlestirme.duzey(" in src, "🔴 düzey çözümü modüle ait değil"


def test_SORAR_MI_KULLANILMADI_ve_SEBEBI_yazili():
    """🔴 **Modülün modeli sevk edilen davranışla ÇELİŞİYORDU** — ve bu, ölçümle
    yakalandı, tahminle değil.

    `sorar_mi("normal", belirsizlik="olcu")` **False** döner (modülün kendi belgesi:
    *"normal yalnız dönem sorar, ADR-0007 K3"*). Ama ürün **bugün** ölçü belirsizliğini
    de soruyor ve `test_netlestirme_onceligi::test_BAYRAK_ACIK_iken_LLM_HIC_CAGRILMIYOR`
    bunu kilitliyor. Modülü **olduğu gibi** uygulamak KURAL B'yi kırardı: varsayılan
    ayarda bir yetenek **sessizce kaybolurdu**.

    → Çağrı yeri yalnız `kapali`'yı uygular.
    *Bir modülün modeli ile sevk edilen davranış çelişiyorsa, kazanan sevk edilen
    davranıştır — çünkü kullanıcı onu görüyor.*
    """
    src = (_KOK / "app/routers/ask.py").read_text(encoding="utf-8")
    i = src.index('if _netlestirme_duzeyi(request) == "kapali":')
    assert "KURAL B" in src[i - 900:i], "🔴 çelişkinin gerekçesi yazılı değil"


def test_VARSAYILAN_BUGUNKU_davranis():
    """🔴 `normal` = bugünkü davranış (ADR-0007 K3): yalnız **dönem** sorulur.
    Yani kapı kapalıyken davranış **birebir** aynıdır (KURAL B)."""
    from app import netlestirme

    assert netlestirme.VARSAYILAN == "normal"
    assert netlestirme.sorar_mi("normal", belirsizlik="olcu") is False
    assert netlestirme.sorar_mi("normal", belirsizlik="donem") is True
    assert netlestirme.sorar_mi("yuksek", belirsizlik="olcu") is True
    assert netlestirme.sorar_mi("kapali", belirsizlik="donem") is False


def test_AYAR_OKUNAMAZSA_NORMAL():
    """⚠ *Bir ayar okunamadığında davranışı değiştirmek, sessiz bir kapsam kaybı olurdu.*"""
    agac = ast.parse((_KOK / "app/routers/ask.py").read_text(encoding="utf-8"))
    fn = next(n for n in agac.body
              if isinstance(n, ast.FunctionDef) and n.name == "_netlestirme_duzeyi")
    govde = ast.unparse(fn)
    assert govde.count("_netlestirme.VARSAYILAN") >= 2, (
        "🔴 hata ya da tenant yokluğu `normal`e düşmüyor")
    assert "except Exception" in govde


def test_AYAR_OKUMASI_ASK_DISINDA():
    """⚠ *Bir ayar okuması bir cevaplama adımı değildir* — ve `ask()` tavanı doluydu."""
    agac = ast.parse((_KOK / "app/routers/ask.py").read_text(encoding="utf-8"))
    assert any(isinstance(n, ast.FunctionDef) and n.name == "_netlestirme_duzeyi"
               for n in agac.body), "🔴 yardımcı `ask()` içinde — tavan aşılır"


def test_TAVAN_MUAFIYETI_GEREKCELI():
    """⚠ *Gerekçesiz bir muafiyet, muafiyet değil sessiz bir tavan artışıdır.*"""
    from tests.test_modul_buyume import MUAFIYET_ASK_DOSYA, MUAFIYET_ASK_KOD

    for liste in (MUAFIYET_ASK_KOD, MUAFIYET_ASK_DOSYA):
        satir = [x for x in liste if x[0] == "faz-5.16"]
        assert satir, "🔴 5.16 muafiyeti yazılmamış"
        assert len(satir[0][2]) > 80, "🔴 gerekçe yüzeysel"


def test_YETIM_SAYISI_ve_AYRIM_yazili():
    """🔴 *Bir sayıyı bir kusur listesi sanmak, dördünü haksız yere borç yazar.*"""
    doc = __doc__ or ""
    assert "dördü de kusur değil" in doc and "8 gerçek" in doc
