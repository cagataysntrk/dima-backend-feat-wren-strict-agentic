"""FAZ 4.5 — **MCP YÜZEYİ.** [bayrak: `mcp_yuzeyi`]

## Neden

Model Context Protocol, **Linux Foundation / Agentic AI Foundation** yönetiminde; kararlı
spec **2025-11-25**. dbt · Cube · AtScale kendi MCP sunucularını yayımlıyor. Yani
*"ajanına bağlan"* artık bir farklılaşma değil, bir **giriş bileti**.

## 🔴 İNCE ÇEVİRİCİ — KENDİ KAYDINI KURMAZ

`app/tools.py` **zaten** hem şemayı hem yetki süzgecini üretiyor ve dosyanın kendi notu
şunu söylüyor: *"MCP adaptörü — ileride **ince bir çevirici**; kendi kaydını KURMAZ."*
Bu modül o cümlenin kodudur. İkinci bir araç kaydı yazmak, üç yüzeyin (LLM · MCP · UI)
**ayrışması** demekti: bir araç bir yüzeyde açık, ötekinde kapalı olurdu ve hangisinin
doğru olduğunu kimse bilemezdi.

## 🔴 DEĞİŞMEZ — AYNI DÖRT KAPI, AYNI MAKBUZ

MCP'den çağrılan bir araç `Planlayici.calistir()`'in **aynı dört kapısından** geçer
(`KAYIT · yetki · deterministik-önce · bütçe`) ve **aynı makbuzu** üretir. Ayrı bir
yürütme yolu açılırsa **bu madde yanlış yapılmış demektir** — ve fark tam olarak burada:

| jenerik MCP sunucusu | biz |
|---|---|
| aracı çağırır, sonucu döner | aracı **dört kapıdan** geçirir |
| makbuz **yok** | her çağrı `Kosum` adımı üretir (araç · determinizm · süre · makbuz) |
| yetki sunucunun kendi ayarı | yetki **`authorize()` matrisi** — ajan kullanıcıyı aşamaz |

⚠ Bu yüzden `cagir()` bir `Planlayici` **ister**. İstemeseydi kapıları atlamak bir
imza değişikliği kadar kolay olurdu; istediği için atlamak **imkânsızdır**.

> **Karar kaydı: `ADR-0031`** — MCP yüzeyi — HTTP'nin YANINA değil İÇİNE.
> ⚠ Atıf, kararın **yaşadığı yere** yazılır: kayıt ile kod birbirini ancak
> böyle doğrulayabilir (`tests/test_adr_dosyalari.py` iki yönü de kilitler).
"""

from __future__ import annotations

from typing import Any

from app import tools

#: MCP `tools/list` yanıtındaki alan adı. Spec **camelCase** kullanıyor; `tools.py`'nin
#: sağlayıcı-bağımsız temsili `snake_case`. ⚠ Fark yalnız **burada** çevrilir —
#: `tools.py`'yi MCP'ye göre yeniden adlandırmak, LLM tarafını MCP'ye bağımlı kılardı.
SEMA_ALANI = "inputSchema"


def araclar(principal: Any = None) -> list[dict[str, Any]]:
    """MCP `tools/list` — **`tools.llm_araclari()`'nin çevirisidir**, kopyası değil.

    🔴 Yetki süzgeci burada YENİDEN YAZILMAZ: `llm_araclari(principal)` zaten
    `izinli_araclar()`'a, o da `authorize()` matrisine bağlı. İkinci bir süzgeç,
    matrisin ikinci bir kopyası olurdu ve iki kopya **ayrışır**.
    """
    out = []
    for a in tools.llm_araclari(principal):
        kayit = dict(a)
        kayit[SEMA_ALANI] = kayit.pop("input_schema")
        out.append(kayit)
    return out


def cagir(planlayici: Any, ad: str, argumanlar: dict[str, Any] | None = None,
          *, makbuz: str | None = None) -> dict[str, Any]:
    """MCP `tools/call` — **`Planlayici.calistir()` üzerinden**, kapıları atlamadan.

    🔴 `planlayici` zorunlu bir parametredir ve bu **bilinçlidir**: opsiyonel olsaydı
    kapıları atlamak bir `None` geçmek kadar kolay olurdu.

    Döner: MCP `CallToolResult` + `_meta.makbuz` (adım kaydı).

    ⚠ Hata **yutulmaz**: `isError: true` döner ve **adım kaydı yine yazılır** —
    `calistir()`'in `finally` bloğu başarısız adımı da kaydeder. *Sessizce kaybolan bir
    adım, yapılmamış bir adım gibi okunur ve koşumun maliyeti anlaşılmaz olur.*
    """
    if planlayici is None:
        raise ValueError(
            "MCP çağrısı bir `Planlayici` İSTER — dört kapı (KAYIT · yetki · "
            "deterministik-önce · bütçe) orada uygulanır. Kapısız bir MCP yolu açmak, "
            "bu maddenin tek değişmezini çiğnerdi.")
    try:
        sonuc = planlayici.calistir(ad, **(argumanlar or {}), makbuz=makbuz)
        hata = None
    except Exception as exc:                                  # noqa: BLE001
        sonuc, hata = None, f"{type(exc).__name__}: {exc}"[:300]

    adimlar = getattr(getattr(planlayici, "kosum", None), "adimlar", []) or []
    son = adimlar[-1] if adimlar else None
    return {
        "content": [{"type": "text",
                     "text": hata if hata else _metin(sonuc)}],
        "isError": bool(hata),
        # 🔴 **MAKBUZ** — jenerik MCP sunucularında olmayan fark. Aynı `Adim` nesnesi
        # HTTP yolunda da üretilir; burada yeniden BİÇİMLENDİRİLMEZ, olduğu gibi verilir.
        "_meta": {"makbuz": _adim_sozlugu(son)},
    }


def _metin(x: Any) -> str:
    """Sonucu MCP'nin `text` içeriğine çevirir. ⚠ Kısaltmaz — kesilmiş bir sonuç,
    ajanın yanlış bir çıkarım yapması demektir."""
    import json

    if isinstance(x, str):
        return x
    try:
        return json.dumps(x, ensure_ascii=False, default=str)
    except Exception:                                         # noqa: BLE001
        return str(x)


def _adim_sozlugu(adim: Any) -> dict[str, Any] | None:
    """`Adim` → sözlük. Alan adları **HTTP yolundakiyle aynı** — ayrışırlarsa iki yüzey
    aynı koşumu farklı anlatır ve denetçi hangisine bakacağını bilemez."""
    if adim is None:
        return None
    if hasattr(adim, "model_dump"):
        return adim.model_dump()
    if hasattr(adim, "__dict__"):
        return dict(adim.__dict__)
    return None
