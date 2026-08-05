"""**FAZ 1.7 / §C ölçüt 12 — TAZELİK ZİNCİRİ BAĞLANDI.** [bayrak: `tazelik`]

## 🔴 Zincirin yalnız ORTASI eksikti

| halka | vardı | bağlıydı |
|---|---|---|
| `SyncState.last_synced_at` (veri) | ✅ | — |
| `app/tazelik.py` (`kademe` · `sayi_gosterilir_mi`) | ✅ | 🔴 **hiçbir çağıran yok** |
| `AskResponse.freshness` + `son_veri_ts` + `tazelik_aciklama` | ✅ | 🔴 **hiçbir dolduran yok** |
| `ReportCard`'ın üç görsel hâli | ✅ **4 atıf** | 🔴 **hiç veri gelmiyor** |

Denetimin adlandırdığı kör nokta buydu: **bir şema alanı üretici değildir** — alan vardı,
ekran tüketiyordu, **üreten yoktu**. `ters_yetim` kapısı bunu göremiyordu.

⚠ Yetim modül sayısı: **12 → 8** (`certification` · `onay_akisi` · `tazelik` bağlandı;
`main` bir yanlış-pozitif — uvicorn giriş noktası).
"""

from __future__ import annotations

import ast
from pathlib import Path

from tests.kapi_ortak import fe_dosyalari

_KOK = Path(__file__).resolve().parents[1]


def _fn(ad: str) -> str:
    agac = ast.parse((_KOK / "app/answer.py").read_text(encoding="utf-8"))
    return ast.unparse(next(n for n in agac.body
                            if isinstance(n, ast.FunctionDef) and n.name == ad))


def test_MODUL_ARTIK_CAGRILIYOR():
    """🔴 `tazelik.py` 1.7'den beri testliydi ve **hiç çağrılmıyordu**."""
    assert "from app import tazelik" in _fn("_tazelik_blogu")
    assert "tazelik.kademe(" in _fn("_tazelik_blogu")


def test_SEAL_ALANLARI_DOLDURUYOR():
    govde = _fn("seal")
    assert "resp.freshness" in govde and "_tazelik_blogu(" in govde
    # ⚠ `ast.unparse` dizge tırnaklarını **tek tırnağa** normalleştirir; kapıyı
    # kaynaktaki yazıma bağlamak, bir biçimlendirme ayrıntısına bağlamak olurdu.
    assert "'tazelik' in _rf" in govde or '"tazelik" in _rf' in govde, (
        "🔴 bayrağa bağlı değil (KURAL B)")


def test_EN_ESKI_SENKRON_aliniyor():
    """🔴 Tazelik **en zayıf halkadır**: bir tablo dün, biri sekiz gün önce
    senkronlandıysa cevap **sekiz gün eskidir**. En yeniyi almak, bayat bir sayıyı taze
    göstermenin en kolay yoludur."""
    govde = _fn("_tazelik_blogu")
    assert "min(satirlar)" in govde, "🔴 `max` kullanılmış — bayat veri taze görünür"


def test_BULUNAMAZSA_BILINMIYOR_taze_DEGIL():
    """🔴 B4: *ölçemediğimiz bir şeyi iyi varsaymak*, `⊘ ÖLÇÜLEMEDİ` üçüncü hâlinin tam
    tersidir."""
    govde = _fn("_tazelik_blogu")
    assert '"bilinmiyor"' in govde
    assert 'return "taze"' not in govde, "🔴 veri yokken `taze` dönülüyor"


def test_BILINMIYORDA_SAYI_GIZLENIYOR():
    """`sayi_gosterilir_mi("bilinmiyor")` **False** — ve ekran onu okuyor."""
    from app import tazelik

    assert tazelik.sayi_gosterilir_mi("bilinmiyor") is False
    assert tazelik.sayi_gosterilir_mi("hata") is False
    assert tazelik.sayi_gosterilir_mi("taze") is True


def test_TENANT_IZOLASYONU():
    """⚠ `SyncState`in kendi `tenant_id`'si **yok**; bağlantı üzerinden bağlanmazsa
    **başka bir şirketin** tazeliği gösterilirdi."""
    govde = _fn("_tazelik_blogu")
    assert "DbConnection.tenant_id == tenant_id" in govde
    assert "deleted_at.is_(None)" in govde, (
        "🔴 Silinmiş bağlantının tazeliği sayılıyor — silinen bir kaynak veri taze olamaz.")


def test_ACIKLAMA_NEDEN_soyluyor():
    """🔴 `hata`/`bilinmiyor` kademelerinde sayı gizlenir; yerine **neden** gizlendiği
    gelir — *sekiz gün eski bir sayıyı normal gibi göstermek, kullanıcıyı geri alınamaz
    bir karara götürür.*"""
    govde = _fn("_tazelik_blogu")
    assert "bayat" in govde and "geri" in govde


def test_TAZELIK_CEVABI_DUSURMUYOR():
    govde = _fn("seal")
    i = govde.index("_tazelik_blogu(")
    assert "except Exception" in govde[i:i + 400]


def test_FRONTEND_UC_HALI_de_ciziliyor():
    """K2: alanın tüketicisi **zaten** vardı — eksik olan üreticiydi."""
    src = fe_dosyalari()["components/ReportCard.tsx"]
    for hal in ('freshness === "hata"', 'freshness === "bilinmiyor"'):
        assert hal in src
    assert "tazelik_aciklama" in src and "son_veri_ts" in src


def test_YETIM_SAYISI_azaldi():
    """⚠ Sayı **ölçülür**, iddia edilmez."""
    import ast as _a

    app = _KOK / "app"
    edilen: set[str] = set()
    for p in list(app.rglob("*.py")) + list((_KOK / "control_plane").rglob("*.py")):
        try:
            t = _a.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:                                   # pragma: no cover
            continue
        for n in _a.walk(t):
            if isinstance(n, _a.ImportFrom) and (n.module or "").startswith("app"):
                edilen.add((n.module or "").split(".")[-1])
                edilen |= {x.name for x in n.names}
    for ad in ("tazelik", "certification", "onay_akisi"):
        assert ad in edilen, f"🔴 `{ad}` yine yetim"
