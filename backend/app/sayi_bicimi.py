"""🔴🔴 `§SB-metin` — **BİR SAYININ TÜRKÇESİ TEK BİR YERDE YAZILIR.**

## Neden bu dosya var — ölçülmüş bir ayrışma

⊙ Ölçüldü (curl `DD` turu, DD-13): aynı üründe iki farklı sayı Türkçesi konuşuluyordu.

    `§KN`         → «fire: 70.057 ↔ akran 38.442 — farkın %56,1'ini yükseltiyor»   ✅
    `contribution` → «Malzeme/Parti Bekleme — 47,836 dk azaldı (net değişimin %83.4'i)» 🔴

İkincisinde **üç** hata var ve üçü de aynı kökten: binlik ayırıcı İngilizce (`47,836`),
ondalık ayırıcı İngilizce (`%83.4`), ek sabit (`'i` — doğrusu `'ü`).

⚠ Ve niyet **zaten doğruydu**: `context.py:362` beklenen çıktıyı *«46.524 dk AZALDI
(net değişimin %83,6'sı)»* diye yazmış. Yani kusur bir karar eksikliği değil, kararın
**ikinci bir yerde yeniden uygulanmasıydı** — `KAT-1`'in tam tanımı.

*İki yerde biçimlendirilen bir sayı, er ya da geç iki farklı sayı gibi okunur.*

## `ek()` — kapalı bir sınıf, bir sözlük değil

Türkçede bir sayıya gelen ek, sayının **okunuşundaki son sözcüğe** göre çekimlenir ve o
sözcük yalnız **son rakamdan** belirlenir: on olasılık, hepsi bu. Tablo tek bir olgudan
türer — son rakamın sözcüğü (`sıfır bir iki üç dört beş altı yedi sekiz dokuz`):
(a) ünlüyle bitiyor mu (kaynaştırma `s` gerekir mi), (b) son ünlüsünün dört-yönlü
uyumdaki karşılığı (`dört`→`ö`⇒`ü`, `beş`→`e`⇒`i`).

    iyelik  = [s] + ünlü          → «%84,1'i»  «%2,2'si»  «%13,3'ü»
    belirtme = iyelik + n + ünlü   → «%84,1'ini» «%2,2'sini» «%13,3'ünü»

⚠ `ADR-0008` ile uyumlu: bu bir **alan sözlüğü** değil, on elemanlı bir sayı sınıfıdır
ve **büyüyemez** — Türkçede on bir rakam yoktur.
"""

from __future__ import annotations

_RAKAM_EKI = {"0": (False, "ı"), "1": (False, "i"), "2": (True, "i"),
              "3": (False, "ü"), "4": (False, "ü"), "5": (False, "i"),
              "6": (True, "ı"), "7": (True, "i"), "8": (False, "i"),
              "9": (False, "u")}


def ek(metin: str, belirtme: bool = False) -> str:
    """`«%2,2»` → `«%2,2'sini»` (belirtme) · `«%84,1»` → `«%84,1'i»` (iyelik)."""
    _son = next((c for c in reversed(str(metin)) if c.isdigit()), "0")
    _unlu_sonu, _u = _RAKAM_EKI[_son]
    _iyelik = ("s" if _unlu_sonu else "") + _u
    return f"{metin}'{_iyelik + 'n' + _u if belirtme else _iyelik}"


def sayi(x) -> str:
    """İnsan için sayı: `3.17e+05` **bir sayı değil bir gösterimdir**.

    ⊙ Canlıda ölçüldü: *«ağırlık: 3.17e+05 ↔ akran 2.83e+05»* — teknik olarak doğru,
    okunabilir olarak **hiç**. Bir iş kullanıcısı bilimsel gösterimi zihninde çevirmek
    zorunda kalıyorsa, cevap ona ulaşmamıştır.
    """
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if abs(v) >= 1000:
        return f"{v:,.0f}".replace(",", ".")
    # ⚠ **TAM SAYI ONDALIK TAŞIMAZ.** Ölçüldü (curl `FF` turu, FF-6): bir **sayaç**
    # (`kaza_adedi`) *«**3,00** ↔ öteki departman ortalaması **1,75**»* diye basıldı.
    # Ortalama gerçekten kesirlidir; sayaç değildir — ve `3,00` okuyucuya *«burada bir
    # kesir var»* der. *Bir gösterimin fazladan basamağı, olmayan bir kesinliği vaat eder.*
    if abs(v) >= 1:
        return (f"{v:,.0f}".replace(",", ".") if float(v).is_integer()
                else f"{v:,.2f}".replace(",", "~").replace(".", ",").replace("~", "."))
    return f"{v:.3f}".replace(".", ",")


def yuzde(x: float, basamak: int = 1) -> str:
    """`«%83,4»` — ondalık ayırıcı **virgül**, çünkü cümlenin dili Türkçe."""
    try:
        return f"%{float(x):.{basamak}f}".replace(".", ",")
    except (TypeError, ValueError):
        return f"%{x}"
