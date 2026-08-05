"""**FAZ 5.10 — KPI PİN ZİNCİRİ BAĞLANDI.** [bayrak: `kpi_pin`]

## 🔴 Ölçülen kusur

`app/kpi_pin.py` — **85 satır, 10 test**, ve üretim kodunda **hiç import edilmiyordu**.
Semantik yazılmıştı; **kolonu yoktu, ucu yoktu, ekranı yoktu**. Denetimin *"12 yetim
modül"* bulgusunun dördüncü kalemi.

> 🔴 *Bir modülün testleri, o modül hiç çağrılmasa da yeşildir.* — **birim yeşili,
> sistem kırmızısı**.

⚠ Yetim modül: **12 → 7** (`certification` · `onay_akisi` · `tazelik` · `kpi_pin`;
`main` yanlış-pozitif).

## Kararın sahibi TEK

Sınır (`_MAX_PER_USER`) ve *"sessizce düşürme"* yasağı `kpi_pin`'de yazılı; router onu
**çağırır**, yeniden yazmaz. Sıralama da öyle (`sirala`).
"""

from __future__ import annotations

import ast
from pathlib import Path

from tests.kapi_ortak import fe_dosyalari

_KOK = Path(__file__).resolve().parents[1]


def test_MODUL_ARTIK_CAGRILIYOR():
    src = (_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8")
    assert "from app import kpi_pin" in src
    assert "kpi_pin.pin_karari(" in src and "kpi_pin.sirala(" in src


def test_SINIR_ROUTERDA_YENIDEN_YAZILMADI():
    """🔴 *Aynı kuralın iki sahibi ayrışır.* Router sınırı `kpi_pin`'den okur."""
    agac = ast.parse((_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "patch_widget")
    govde = ast.unparse(fn)
    assert "pin_karari" in govde
    assert "_MAX_PER_USER" not in govde, "🔴 sınır router'da elle yazılmış — ikinci sahip"


def test_SINIR_ASILINCA_400_ve_SEBEP():
    """🔴 *Bir pin bir karardır ve kullanıcının kendi eliyle koyduğu bir şeyi haber
    vermeden kaldırmak, ürünün onun yerine karar vermesidir.* Sessiz düşürme YOK."""
    src = (_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8")
    i = src.index("kpi_pin.pin_karari(")
    blok = src[i:i + 700]
    assert "status_code=400" in blok and 'karar["sebep"]' in blok


def test_MODULUN_KENDI_KARARI_KORUNDU():
    """`kpi_pin` sınır aşımında **en eskiyi düşürmüyor** — kapı bunu modülde doğrular."""
    from app import kpi_pin

    mevcut = [{"id": f"w{i}", "pinned": True} for i in range(kpi_pin.azami_pin(10))]
    karar = kpi_pin.pin_karari(mevcut, "yeni", azami=10)
    assert karar["izin"] is False and "önce birini kaldır" in karar["sebep"]


def test_ZATEN_PINLI_HATA_DEGIL():
    """⚠ *Bir işlemin ikinci kez uygulanması bir hata değildir.*"""
    from app import kpi_pin

    karar = kpi_pin.pin_karari([{"id": "w1", "pinned": True}], "w1", azami=1)
    assert karar["izin"] is True


def test_SIRALAMA_MODULE_devredildi():
    """⚠ Sıralamayı router'da elle yazmak, aynı kuralın ikinci sahibi olurdu."""
    agac = ast.parse((_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_widgets_of")
    assert "kpi_pin.sirala(" in ast.unparse(fn)


def test_MODEL_ve_GOC():
    """⚠ `nullable=False, default=False`: mevcut widget'lar pin'siz doğar — *hiç kimse
    onları pin'lemedi.* `NULL`, "pin'lenmemiş" ile "bilinmiyor"u karıştırırdı."""
    from control_plane.models import DashboardWidget

    assert "pinned" in DashboardWidget.model_fields
    goc = (_KOK / "migrations/versions/a2d5e81c93f7_widget_pinned.py").read_text(
        encoding="utf-8")
    assert "nullable=False" in goc and "server_default=sa.false()" in goc
    assert "pin kararlarını siler" in goc, "🔴 geri almanın bedeli yazılı değil"


def test_OKUMA_TARAFI_da_TASIYOR():
    """K2: alan yazılıp okunmuyorsa, ekran onu **hiç göremez**."""
    src = (_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8")
    assert '"pinned": bool(getattr(w, "pinned", False))' in src


# --- Arayüz ---------------------------------------------------------------------------

def test_EKRANDA_DUGME_var():
    """K2: yeni bir uç **frontend tüketicisi olmadan** eklenemez."""
    src = fe_dosyalari()["components/DashboardView.tsx"]
    assert "pin.mutate({ wid: w.id, pinned: !w.pinned })" in src


def test_RENK_TEK_KANAL_DEGIL():
    """A11Y-9: sabitlenmiş hâl ayrıca **dolu bir glif** ve `aria-pressed` taşır."""
    src = fe_dosyalari()["components/DashboardView.tsx"]
    assert "aria-pressed={Boolean(w.pinned)}" in src
    assert "◆ sabit" in src and "◇ sabitle" in src


def test_SUNUCUNUN_SEBEBI_EKRANA_ulasiyor():
    """⚠ Sınır aşımında sunucu **kendi cümlesini** yazıyor; `hataMetni` onu önceler."""
    src = fe_dosyalari()["components/DashboardView.tsx"]
    assert "hataMetni(e, \"Sabitleme\")" in src and "<HataSeridi" in src


def test_PIN_yeni_PANEL_acmadi():
    """PK-1/K5: *pin bir katmandır, panel değil.* Tavan 13/13."""
    from tests.test_panel_sayisi import DESEN, TAVAN

    toplam = sum(len(DESEN.findall(v)) for v in fe_dosyalari().values())
    assert toplam <= TAVAN


def test_BAYRAK_KAPISI_var():
    """🔴 **Kendi ürettiğim kusur.** Modülü bağladım ama **bayrağı bağlamadım**:
    `kpi_pin` açıp kapatmak **hiçbir şey yapmıyordu** — denetimin §11/GRUP 2'sinin
    adlandırdığı *"kapısız bayrak"* sınıfını, tam onu kapatırken ürettim.

    ⚠ Kapalıyken `pinned` **sessizce yok sayılmaz**, 400 döner: *sessizce yok sayılan bir
    istek, kullanıcıya işlemin olduğunu düşündürür.*
    """
    import ast

    agac = ast.parse((_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "patch_widget")
    govde = ast.unparse(fn)
    assert "'kpi_pin' not in _rf(" in govde or '"kpi_pin" not in _rf(' in govde
    assert "status_code=400" in govde
