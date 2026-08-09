"""ORKESTRATÖRÜN İLKELLERİ — `BAGLA` ve `HESAPLA` (FAZ O-1).

Bu modül, `belgeler/plan/2026-08-09_ORKESTRATOR-KATMANI-VE-OLCEKLENME.md`'nin **ilk
fazıdır** ve bilerek **en dar** dilimdir: iki **saf fonksiyon**, LLM yok, SQL yok, ağ yok.

## Neden bu iki fonksiyon

Raporun kapanış tablosu evrende üç nesne tanımlıyor — `CQ` (koşmamış soru) · `SATIR`
(koşmuş cevap) · `DEĞER` (skaler) — ve bir zincirin ancak `SATIR → DEĞER` köprüsü varsa
kurulabileceğini gösteriyor:

    COZ      metin  → CQ
    SEC/KIR/SUZ/…   CQ → CQ          ✅ hepsi var (12 operatör · 6 pencere · 3 türev kipi)
    CALISTIR        CQ → SATIR       ✅ var (`wren_service.cube_sql`)
    BAGLA           SATIR → DEĞER    🔴 programatik tetikleyicisi YOKTU
    HESAPLA         SATIR → SATIR    🔴 YOKTU
    ANLAT           SATIR → metin    ✅ var

⊙ Yani eksik olan **yetenek değil, halka**: mutfak her adımı yapabiliyordu ama bir adımın
çıktısını öteki adımın **girdisine** çeviren bir şey yoktu.

## 🔴 BU FAZ BİR YETENEK EKLEMESİ DEĞİL, DENKLİĞİ KANITLANAN BİR REFACTOR

Kabul ölçütü raporda yazılı ve **ölçülebilir**: *«`§AA1`'in bugünkü çıktısı bu ikisi
çağrılarak birebir üretilebiliyor»*. `contribution._akran_kiyasi` bugün canlıda çalışıyor
(`AA2`·`BB2`·`CC4`·`DD8`) ve `E4` onu **korumaya almış**: bileşim aynı sonucu verene kadar
elle yazılmış sürüm yerinde kalır.

Bu yüzden burada **hiçbir davranış değişmiyor**: iki fonksiyon yazılıyor, `_akran_kiyasi`
onları **çağırıyor**, ve çıktı bayt bayt aynı kalıyor. Zemin kurulmuş olur; plan gelince
aynı ilkelleri **başka sırayla** dizecek.

⚠ `ask()` **dışında** ve `contribution` **dışında** duruyorlar: ikisi de saf, ikisi de
tek başına test edilebilir. `test_ASK_IC_FONKSIYON_SAYISI_ARTMIYOR`'un dersi (*«yeni bir
yardımcı gerekiyorsa modül düzeyine al: saf bir fonksiyon test edilebilir, closure
edilemez»*) bu modülün var olma sebebidir.

*Bir zinciri kuran şey halkalar değil, halkaların birbirine geçtiği yerdir.*
"""

from __future__ import annotations

from typing import Any


def sayi(v: Any) -> float | None:
    """Satır değerini sayıya çevirir; çevrilemiyorsa **`None`** — uydurma yok.

    ⚠ `contribution._sayi` ile **bilerek ayrı**: o eksiği `0.0` sayar (*«eksik geçen dönem
    SIFIR sayılır»*, kendi kapısı var). İkisi de doğru — **farklı sorular için**. Bir ada
    sahip çıkmadan bir sözleşme yazılmaz (`§AA1`'in üçüncü hatası tam buydu).
    """
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def bagla(rows: list[dict], boyut: str, olcu: str, *, en_iyi_az: bool = False
          ) -> tuple[str | None, float | None]:
    """**`BAGLA` · SATIR → DEĞER** — satırlardan **bir varlığı** seçip değerini döndürür.

    Zincirin can damarı: bir adımın çıktısındaki *«hangisi»* sorusunu cevaplayıp sonraki
    adıma **tek bir ad** verir (*«en kötü makine»* → `"RAM-3"`).

    `en_iyi_az`: ölçüde **az olan iyi** mi (`lower_is_better`). Yön sözlükten değil
    **beyandan** okunur — `§W-C`'nin dersi: *bir sıfatın yönünü sözlükten okumak, ölçünün
    kendi beyanını görmezden gelmektir.*

    Döner: `(varlık, değer)` — satır yoksa `(None, None)`. **Uydurmaz.**
    """
    deg = {str(r.get(boyut)): sayi(r.get(olcu))
           for r in (rows or []) if r.get(boyut) is not None}
    deg = {k: v for k, v in deg.items() if v is not None}
    if not deg:
        return None, None
    hedef = max(deg, key=deg.get) if en_iyi_az else min(deg, key=deg.get)
    return hedef, deg[hedef]


def hesapla(rows: list[dict], boyut: str, olcu: str, hedef: str) -> dict | None:
    """**`HESAPLA` · SATIR → DEĞER kümesi** — hedefi **akranlarıyla** kıyaslar.

    Döner: `{hedef_deger, akran_ortalamasi, fark, fark_yuzde, akran_sayisi}` — ya da
    akran yoksa `None`.

    ⚠ **En az iki akran** şartı: tek akranla *«ortalama»* bir kıyas değil, ikinci bir
    sayıdır. `contribution`'ın bugünkü eşiği (`len(_deg) < 3`) burada **korunuyor** —
    denkliğin şartı bu.
    ⚠ Payda sıfırsa `fark_yuzde` **`None`** kalır: bölme uydurulmaz.
    """
    deg = {str(r.get(boyut)): sayi(r.get(olcu))
           for r in (rows or []) if r.get(boyut) is not None}
    deg = {k: v for k, v in deg.items() if v is not None}
    if len(deg) < 3 or hedef not in deg:
        return None
    akranlar = [v for k, v in deg.items() if k != hedef]
    ort = sum(akranlar) / len(akranlar)
    fark = deg[hedef] - ort
    return {"hedef_deger": deg[hedef], "akran_ortalamasi": round(ort, 4),
            "fark": round(fark, 4),
            "fark_yuzde": round(100.0 * fark / ort, 1) if ort else None,
            "akran_sayisi": len(akranlar)}
