"""🔴 `§F13` — *«AGENTIC'İN ASIL KİLİDİ»*: NE **VAR**, NE **YOK** — ölçüldü.

## Kartın iddiası

> Bugün `_yazma_araclari` **bilerek** `llm_araclari` dışında — *«ajan YAZAMAZ»*. Sonuç:
> *«bunu panoya ekle»* · *«her pazartesi yolla»* **yapılamıyor**. ⊙ Yasak **kaldırılmaz,
> KADEMELENDİRİLİR** — ajan yazma aracını **öneri** olarak üretir → kullanıcı **onaylar**
> → `authorize()` + audit (**ikisi de zaten var**) → çalışır.

## Ölçüm (2026-08-12) — ONAY ALTYAPISI ZATEN CANLI

| parça | durum |
|---|---|
| `app/onay_akisi.py` (**289 satır**) | ✅ durumlar · risk kademeleri (`dusuk`/`orta`/`geri_alinamaz`) · bilet ömrü · **yasak argüman** listesi (parola/token…) |
| `app/yazma_araclari.py` | ✅ *«Yalnız `onay_akisi` üzerinden çağrılabilir — doğrudan çağrı, onayı bir **süs** yapardı»* |
| `POST /ask/eylem` | ✅ canlı uç; `onay_akisi.bilet_dogrula` çağırıyor |
| `schemas.py` bilet alanı | ✅ **fail-closed** varsayılan (`""`) |
| `authorize()` + audit | ✅ ikisi de var (kartın kendi tespiti) |

🔴 **VE BAYRAĞIN ADI YANILTIYOR — kartı okuyanın düşeceği tuzak.** `onay_akisi: "off"`
bir *«onay akışı kapalı»* **değildir**; bayrağın kendi açıklaması tersini söylüyor:

> *«D9: kapsam **İÇİ** ve **GERİ ALINABİLİR** bir eylem **İSTEMSİZ** koşar… ⚠ YAZMA
> YÜZEYİ BÜYÜMEZ: ajan hâlâ yazma aracı **ÇAĞIRMIYOR**; değişen tek şey kullanıcının
> **KENDİ** eyleminin kaç tıkla tamamlandığı.»*

Yani bayrak **istem kaldırır**, onay eklemez. Kapalıyken davranış *«her yazmaya istem»* —
yani **daha muhafazakâr** olan. *Bir bayrağın adı, ne yaptığının kanıtı değildir.*

## 🔴 GERÇEKTEN EKSİK OLAN TEK ŞEY

Ajanın bir yazma aracını **öneri olarak üretmesi**: `tools.KAYIT`'ta `yan_etki="yazar"`
araç **yok** (`§C3`'te ölçüldü: `{'yok': 25}`), dolayısıyla planlayıcı onu **seçemez**.
Zincirin *«kullanıcı onaylar → çalışır»* yarısı **kurulu**; *«ajan önerir»* yarısı **yok**.

⊙ Bu bir **kablolama** değil bir **karar** işidir: kayda bir `yazar` araç girdiği an
`§C3`'ün MCP kapısı da kırmızıya döner (orası *«yazma aracı yok»*u bir açılış şartı
sayıyor). İkisi **aynı kararın iki yüzü** ve birlikte verilmeli.

*Bir kilidin iki yarısından biri kuruluysa, eksik olan yarı değil KARARDIR.*
"""

from __future__ import annotations

import pathlib

import yaml

from app import onay_akisi, tools

_APP = pathlib.Path(__file__).parent.parent / "app"
_PACK = pathlib.Path(__file__).parent.parent / "demo" / "packs" / "features.yml"


def _bayrak(ad: str) -> str:
    d = yaml.safe_load(_PACK.read_text(encoding="utf-8")) or {}
    for blok in (d.values() if isinstance(d, dict) else []):
        if isinstance(blok, dict) and ad in blok:
            return str(blok[ad])
    return ""


# --- KURULU YARI: kilitlenir, sessizce kaybolamaz --------------------------------

def test_ONAY_AKISI_kurulu():
    """Risk kademeleri + durum makinesi + bilet — kartın *«zaten var»* dediği yarı."""
    assert onay_akisi.DURUMLAR
    assert {onay_akisi.RISK_DUSUK, onay_akisi.RISK_ORTA,
            onay_akisi.RISK_GERI_ALINAMAZ} <= set(dir(onay_akisi)) | {
        onay_akisi.RISK_DUSUK, onay_akisi.RISK_ORTA, onay_akisi.RISK_GERI_ALINAMAZ}
    assert hasattr(onay_akisi, "bilet_dogrula")


def test_YASAK_ARGUMAN_listesi_SIR_kacirmiyor():
    """Onay biletine parola/token yazılamaz — *bir onay ekranı, sırrı gösterdiği anda
    bir sızıntı yüzeyi olur.*"""
    y = {a.lower() for a in onay_akisi.YASAK_ARGUMAN}
    assert {"password", "token"} <= y


def test_YAZMA_ARACLARI_yalniz_ONAYDAN_gecer():
    """`yazma_araclari`'nın kendi sözleşmesi: doğrudan çağrı onayı bir **süs** yapardı."""
    src = (_APP / "yazma_araclari.py").read_text(encoding="utf-8")
    assert "onay_akisi" in src


def test_EYLEM_UCU_bileti_DOGRULUYOR():
    """`/ask/eylem` biletsiz çalışmaz; şema varsayılanı **fail-closed** (`\"\"`)."""
    e = (_APP / "routers" / "eylem.py").read_text(encoding="utf-8")
    assert "bilet_dogrula" in e and "OnayHatasi" in e


# --- BAYRAĞIN ADI YANILTIYOR: kayda geçiyor --------------------------------------

def test_ONAY_AKISI_BAYRAGI_ONAY_EKLEMEZ_ISTEM_KALDIRIR():
    """🔴 Kartı okuyanın düşeceği tuzak. `off` **daha muhafazakâr** olandır; bayrak
    açılınca *kapsam içi ve geri alınabilir* eylemler istemsiz koşar."""
    from app.features import FLAG_REGISTRY
    aciklama = (FLAG_REGISTRY.get("onay_akisi") or {}).get("description", "")
    assert "İSTEMSİZ" in aciklama or "istemsiz" in aciklama
    assert "YAZMA YÜZEYİ BÜYÜMEZ" in aciklama, (
        "bayrağın kendi sınırı silinmiş — adı yaptığını anlatmıyor")
    assert _bayrak("onay_akisi") == "off"


# --- EKSİK YARI: karar verilmeden yazılamaz --------------------------------------

def test_AJAN_HALA_YAZMA_ARACI_ONERMIYOR():
    """🔴 `F13`'ün gerçekte eksik olan tek parçası. Kayda bir `yazar` araç girdiği an
    bu test **ve** `§C3`'ün MCP kapısı birlikte konuşur — ikisi aynı kararın iki yüzü."""
    yazanlar = [getattr(a, "ad", "?") for a in tools.KAYIT
                if getattr(a, "yan_etki", "") == "yazar"]
    assert not yazanlar, (
        f"🔴 kayda `yazar` araç girdi: {yazanlar}\n"
        "`F13` kademelendirmesi ancak ŞU ÜÇÜ birlikte kurulunca tamamdır:\n"
        "  ① ajan aracı **öneri** olarak üretir (plan/`tools` kaydı)\n"
        "  ② kullanıcı **onaylar** → `onay_akisi` bileti (kurulu ✅)\n"
        "  ③ `authorize()` + audit ayrı satır (kurulu ✅)\n"
        "⚠ Ve `tests/test_c3_mcp_acilis_sartlari.py::test_YAZMA_ARACI_kayitta_YOK` "
        "aynı anda kırmızıya döner — MCP açılış şartı 'yazma aracı yok'tur.")
