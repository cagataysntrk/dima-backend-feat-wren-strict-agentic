"""🔴 `§C3` — MCP YÜZEYİ **AÇILMADI**: dört şarttan **ikisi** karşılanmıyor.

## Kartın azaltma listesi = açılış şartları

> **risk:** Prompt injection. 14 CVE · 2.614 uygulamada **%82 path traversal, %67 code
> injection**. ⊙ **Bizim özel riskimiz:** veri tablolarındaki **serbest metin hücreleri**
> (müşteri notu, ürün açıklaması) MCP yanıtı olarak modele döner.
> **azaltma:** Salt-okuma; **yazma araçları kayıtta yok**; serbest metin alanları için
> **çıktı sanitizasyonu**; araç sayısı **≤20**.

Bir azaltma listesi bir dilek listesi değildir — **açılış şartıdır**. Ölçüldü (2026-08-12):

| # | şart | ölçülen | |
|---|---|---|---|
| ① | araç sayısı **≤20** | `KAYIT` **25** · `llm_araclari(None)` **25** · `mcp.araclar(None)` **25** | 🔴 |
| ② | yazma aracı **yok** | `yan_etki` dağılımı **`{'yok': 25}`** — sıfır `yazar` | ✅ |
| ③ | salt-okuma / **dört kapı** | `mcp.cagir` bir `Planlayici` **istiyor** ve `calistir` çağırıyor | ✅ |
| ④ | serbest metin **sanitizasyonu** | `mcp.py`'de `sanit`/`temizle`/`kaçış`/`pii` izi **HİÇBİRİ**; `cagir` PII çağırmıyor | 🔴 |

## 🔴 KARAR: AÇILMIYOR — ve iki eksik **ayrı cinsten**

* **④ eksik bir KONTROL.** Kartın *«bizim özel riskimiz»* dediği yol tam olarak açık:
  bir müşteri notu hücresine yazılmış talimat, MCP yanıtı olarak modele döner. Bu bir
  tasarım işidir (neyin süzüleceği, süzmenin **beyan edilmesi**), tek satır değil.
* **① bir KARAR.** Kartın `≤20`'si raporun kendi dış dayanağının daha katı bir vekilidir:
  OpenAI eşiği *«15'ten fazla **ayrık** araç sorun değil; **10'dan az ÖRTÜŞEN** araç
  sorun»* der — yani ölçüt **sayı değil ÖRTÜŞME**. 25 aracın örtüşmesi **ölçülmedi**;
  ölçülmeden ne *«eşiği gevşet»* ne *«beş araç kes»* denebilir.
  ⚠ Ve `§C1` tam bu ölçümü bekliyor (fiil↔araç eşleşmesi) — ikisi **aynı ölçüme** bağlı.

⊙ Bu, ölçüye dayanan **on ikinci** *«yapma»* kararıdır. Ama bir red bir **borçtur**
(`feedback_durust_red_basari_degil`): bu yüzden aşağıdaki kapı, şartlar karşılanmadan
bayrak açılırsa **kırmızı** olur ve neyin eksik olduğunu **adıyla** söyler.

*Bir güvenlik sınırını «sonra bakarız» diye açmak, sınırı hiç koymamaktır.*
"""

from __future__ import annotations

import inspect
import pathlib

import yaml

from app import mcp, tools

_PACK = pathlib.Path(__file__).parent.parent / "demo" / "packs" / "features.yml"
#: Kartın yazdığı eşik. Değiştirilecekse **ölçümle** değiştirilir (bkz. modül docstring'i).
ARAC_TAVANI = 20


def _bayrak(ad: str) -> str:
    d = yaml.safe_load(_PACK.read_text(encoding="utf-8")) or {}
    for blok in (d.values() if isinstance(d, dict) else []):
        if isinstance(blok, dict) and ad in blok:
            return str(blok[ad])
    return ""


def _sanitizasyon_var() -> bool:
    src = inspect.getsource(mcp).lower()
    return any(k in src for k in ("sanit", "temizle", "kacis", "kaçış", "pii", "maskele"))


# --- KARŞILANAN İKİ ŞART: kilitlenir, geri düşemez -------------------------------

def test_YAZMA_ARACI_kayitta_YOK():
    """✅ Şart ②. *«Ajan YAZAMAZ»* — `tools.py`'nin dört değişmezinden biri. Bir gün bir
    yazma aracı kayda girerse MCP **açılmadan önce** bu test kırılır."""
    yazanlar = [getattr(a, "ad", "?") for a in tools.KAYIT
                if getattr(a, "yan_etki", "") == "yazar"]
    assert not yazanlar, f"🔴 kayda yazma aracı girdi: {yazanlar} — MCP açılışı bloke"


def test_MCP_CAGRISI_DORT_KAPIDAN_geciyor():
    """✅ Şart ③. `cagir()` bir `Planlayici` **ister**; istemeseydi kapıları atlamak bir
    imza değişikliği kadar kolay olurdu. *İstediği için atlamak imkânsızdır.*"""
    cs = inspect.getsource(mcp.cagir)
    assert "Planlayici" in cs or "planlayici" in cs.lower(), (
        "MCP kendi yürütme yolunu açmış olabilir — makbuz ve dört kapı kaybolur")
    assert "calistir" in cs


def test_MCP_KENDI_KAYDINI_KURMUYOR():
    """`KAT-1` — üç yüzey (LLM · MCP · UI) tek kayıttan beslenir; ayrışırlarsa bir araç
    bir yüzeyde açık ötekinde kapalı olur ve hangisinin doğru olduğu bilinemez."""
    assert len(mcp.araclar(None)) == len(tools.llm_araclari(None))


# --- KARŞILANMAYAN İKİ ŞART: borç, ve kendini topluyor ---------------------------

def test_BORC_KENDINI_TOPLUYOR_mcp_acilirsa_KIRMIZI():
    """🔴 **C3'ün vadesi budur.** Bayrak, iki eksik şart kapanmadan açılırsa bu test
    kırılır ve eksiği adıyla söyler."""
    if _bayrak("mcp_yuzeyi") == "off":
        return                      # kapalı → şartlar henüz aranmaz
    n = len(mcp.araclar(None))
    eksik = []
    if n > ARAC_TAVANI:
        eksik.append(f"① araç sayısı {n} > {ARAC_TAVANI} (ya kes ya ÖRTÜŞMEYİ ölçüp "
                     "eşiği gerekçesiyle değiştir — OpenAI ölçütü sayı değil örtüşmedir)")
    if not _sanitizasyon_var():
        eksik.append("④ serbest metin sanitizasyonu YOK — müşteri notu/ürün açıklaması "
                     "hücrelerindeki talimatlar MCP yanıtı olarak modele döner")
    assert not eksik, (
        "🔴 `mcp_yuzeyi` AÇILDI ama kartın azaltma listesi karşılanmadı:\n  "
        + "\n  ".join(eksik)
        + "\n\nBir güvenlik sınırını «sonra bakarız» diye açmak, sınırı hiç koymamaktır.")


def test_KAPALIYKEN_bugunku_davranis():
    """`KURAL B` — kapalıyken uçlar 404; bu kapı bayrağın hâlâ kapalı olduğunu **kayda
    geçirir**, ki açıldığı gün yukarıdaki test bilinçli bir kararın sonucu olsun."""
    assert _bayrak("mcp_yuzeyi") == "off", (
        "bayrak açılmış — `test_BORC_KENDINI_TOPLUYOR_mcp_acilirsa_KIRMIZI` ve "
        "`test_c1_tek_yetenek_kaydi.py::test_BORC_KENDINI_TOPLUYOR` birlikte okunmalı")
