"""FAZ 5.16 — **NETLEŞTİRME DÜZEYİ: bir AYAR.** [bayrak: `netlestirme_duzeyi`]

## Neden bir ayar

[KANIT §11.2] bunu *"ayrı bir ürün sorusu, karar verilmedi, kayda geçti"* diye **açık
bırakmıştı**. Rakip zemininde karşılığı var: bir satıcıda `Clarification Mode` admin
tarafından `None → High` ayarlanabiliyor.

🔴 Bu, `yol_siniri` ile **aynı ailedendir**: sayısal bir güven eşiği **değil**, **adı
konmuş bir yol seçimi**. Kullanıcı kendi **risk tercihini** verir.

## 🔴 ÜÇ SERTLEŞTİRME — dış öneri OLDUĞU GİBİ kabul EDİLMEDİ

Dış denetim *"`kapali` seçilirse eksik dönem **varsayılanla** cevaplanır"* öneriyordu.
Bu, MIMARI'nin avladığı **sessiz-yanlış sınıfının ta kendisidir**. Kabul şartları:

1. **Varsayım cevabın GÖVDESİNDE görünür** — *"Dönem belirtilmedi — bu yıl varsayıldı."*
   Rozet ya da tooltip **değil**. *Kenara yazılmış bir varsayım, yazılmamış bir
   varsayımdır.*
2. Ayar **tenant-admin'e kilitli**; her değişiklik `AuditLog`'a **ayrı satır**.
3. `kapali` düzeyinde üretilen her cevap **`kanit_sinifi="probabilistik"`** taşır.

## Üç düzey

| düzey | dönem eksikse | not |
|---|---|---|
| `normal` *(varsayılan)* | **SORAR** | bugünkü davranış **birebir** — §C/3 korunur |
| `kapali` | **varsayar ve GÖVDEDE söyler** | üç sertleştirme bağlayıcı |
| `yuksek` | sorar **+ belirsiz ölçü/boyutta da sorar** | kapsam düşer, sessiz-yanlış da |
"""

from __future__ import annotations

from typing import Any

DUZEYLER = ("kapali", "normal", "yuksek")
VARSAYILAN = "normal"

#: `kapali` düzeyinde varsayılan dönem. ⚠ **"Tüm zamanlar" DEĞİL**: bir BI sorusunun
#: sessiz cevabı *"tarihin başından beri"* olamaz — o, kullanıcının hiç sormadığı bir
#: soruya cevaptır. `bu yıl` en dar makul varsayımdır ve **gövdede söylenir**.
KAPALI_VARSAYIM = "bu yıl"


def duzey(config_degeri: str | None) -> str:
    """Geçerli düzey — bilinmeyen değer **sessizce `normal`e düşer**.

    ⚠ Fail-safe **`normal`**, `kapali` değil: bozuk bir ayarın sonucu *"daha az soru"*
    olsaydı, bir yazım hatası sessiz-yanlış üretirdi.
    """
    d = str(config_degeri or "").strip().lower()
    return d if d in DUZEYLER else VARSAYILAN


def sorar_mi(seviye: str, *, belirsizlik: str = "donem") -> bool:
    """Bu belirsizlikte netleştirme sorulur mu?

    `belirsizlik` ∈ `donem | olcu | boyut`.

    🔴 `normal` **bugünkü davranıştır**: yalnız dönem sorulur (`ADR-0007-K3`). `yuksek`
    ölçü/boyut belirsizliğinde de sorar — **kapsamı düşürür** ve bu bilinçli bir takas.
    """
    s = duzey(seviye)
    if s == "kapali":
        return False
    if s == "yuksek":
        return True
    return belirsizlik == "donem"


def govde_notu(seviye: str, *, varsayim: str = KAPALI_VARSAYIM) -> str | None:
    """🔴 **ŞART 1: varsayım cevabın GÖVDESİNDE.**

    *Kenara yazılmış bir varsayım, yazılmamış bir varsayımdır.* `explain.assumptions`
    bir **denetim** alanıdır; kullanıcı onu okumaz ve okumak zorunda da değildir.
    """
    if duzey(seviye) != "kapali":
        return None
    return f"Dönem belirtilmedi — {varsayim} varsayıldı."


def kanit_sinifi(seviye: str, bugunku: str | None) -> str | None:
    """🔴 **ŞART 3:** `kapali` düzeyinde üretilen her cevap **probabilistik**tir.

    ⚠ Sınıf **düşürülür, yükseltilmez**: deterministik bir yoldan gelmiş olsa bile
    cevabın **sorusu** varsayımla tamamlandıysa, sonuç artık o varsayıma bağlıdır.
    *Kesin bir hesabın belirsiz bir girdisi, hesabı belirsiz yapar.*
    """
    if duzey(seviye) != "kapali":
        return bugunku
    return "probabilistik"


def degisiklik_denetim_satiri(eski: str | None, yeni: str | None,
                              principal: Any = None) -> dict[str, Any]:
    """🔴 **ŞART 2:** her değişiklik `AuditLog`'a **ayrı satır**.

    ⚠ Bu ayar bir **risk tercihini** değiştirir; kim ne zaman değiştirdiği sorusu bir
    olaydan **sonra** sorulur ve o an cevabın var olması gerekir.
    """
    return {
        "action": "netlestirme_duzeyi.degisti",
        "eski": duzey(eski),
        "yeni": duzey(yeni),
        "user_id": str(getattr(principal, "user_id", "") or "") or None,
        "tenant_id": str(getattr(principal, "tenant_id", "") or "") or None,
    }
