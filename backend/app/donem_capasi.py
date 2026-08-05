"""🔴 KÖK-4 — **TAKİP TURUNDA DÖNEM ÇAPASI.** (denetim raporu KN-1)

## Ölçülen kusur — sondanın **en büyük tek kümesi**

| | |
|---|---|
| Toplam netleştirme | **43** |
| — *"Hangi dönem için?"* | **34** (%79) |
| — bunların ilk turda olanı | 8 → **doğru davranış** (ADR-0007-K3) |
| — 🔴 **takip turunda** olanı | **26** |
| Takipte, önceki turda dönem var mıydı | 🔴 **26/26 EVET** |

```
tur 1  bu yıl makine bazında oee        ✅ oee.ort_oee × makine
tur 2  en düşük hangisi                 ✅ aynı cube, dönem KORUNUYOR
tur 3  o makinenin duruşları ne kadar   🔵 «Hangi dönem için?»
tur 4  peki fire tarafı nasıl           🔵 «Hangi dönem için?»
```

Fark: 2. tur **aynı ölçüyü** sıralıyor; 3. tur **yeni bir ölçü** istiyor. Yani dönem,
**ölçü değişince** düşüyor.

## Kod yolu — raporun bulduğu tek satır

`cube_router.py:1112-1113`:

```python
if em and em not in prev.get("measures", []) and swap is None and topn is None:
    return None  # farklı metrik açıkça isteniyor → yeni sorgu, LLM sınıflandırsın
```

`deterministic_refine` **`None`** dönünce soru **taze soru** sayılıyor; `route()` çıplak
takip metnini görüyor (`o makinenin duruşları ne kadar`) → dönem yok → **netleştirme**.

⚠ Ve kanıtı kesinleştiren ayrıntı: dönemi taşıyacak mekanizma **iki satır aşağıda zaten
var** (`cq = copy.deepcopy(prev)`); ölçü-değişimi dalı ona **hiç ulaşmıyor**.
🔴 *Bilgi var, temsil yok — en saf hâli.*

## 🔴 Neden `return None` KALDIRILMIYOR

Raporun kendi anti-çözüm listesi (**A4**): *"o dal **bilinçli** — farklı metrik
gerçekten yeni bir sorudur. Kaldırmak **ölçü karışması** üretir."*

> Doğru olan **dönemi soruya değil, OTURUMA bağlamaktır**: ölçü değişse de dönem
> çapası yaşasın.

Bu modül tam olarak onu yapar ve **başka hiçbir şeye dokunmaz**: cube değişebilir,
ölçü değişebilir, kırılım değişebilir — **yalnız dönem** taşınır.

## Üç şart — üçü birden

Çapa YALNIZ şu üç şart aynı anda sağlanınca taşınır:

1. Yeni sorgu **hiç dönem filtresi taşımıyor** → kullanıcı bu turda dönem söylemedi.
2. Önceki sorgu **dönem filtresi taşıyor** → oturumda bir dönem *kurulmuş*.
3. Soru **"tüm zamanlar" demiyor** → filtre yokluğu **kasıtlı değil**.

⚠ Üçüncüsü olmadan `tüm zamanlar` isteği sessizce eski döneme geri dönerdi — yani
kullanıcının **açık** talimatı, hatırlanan bir bağlam tarafından ezilirdi. *Bir bağlam,
kendisini ezmek için verilmiş bir talimatı ezemez.*
"""

from __future__ import annotations

from app.logging_setup import get_logger

_log = get_logger("donem_capasi")

#: Dönem filtresi sayılan operatörler. ⚠ `eq` DEĞİL: `tarih = '2026-01-01'` bir dönem
#: değil bir nokta seçimidir ve taşınması yanlış olurdu.
_DONEM_OP = ("gte", "lte", "gt", "lt", ">=", "<=", ">", "<")


def _donem_filtreleri(cq: dict | None) -> list[dict]:
    """Bir `cube_query`'nin dönem filtreleri — **değere** bakarak, ada değil.

    ⚠ Zaman boyutunun adı cube'a göre değişir (`tarih` · `donem_tarih` ·
    `acilis_tarihi`); bir ada göre aramak yeni her cube'da sessizce boş döner.
    """
    out = []
    for f in ((cq or {}).get("filters") or []):
        v = f.get("value")
        if (str(f.get("operator")) in _DONEM_OP and isinstance(v, str)
                and len(v) >= 10 and v[:4].isdigit() and v[4] == "-"):
            out.append(f)
    return out


def tasi(yeni_cq: dict | None, onceki_cq: dict | None, soru: str,
         *, cube_meta: dict | None = None) -> tuple[dict | None, bool]:
    """Dönem çapasını taze sorguya taşı — `(cq, tasindi_mi)`.

    🔴 **Yalnız dönem taşınır.** Cube, ölçü, kırılım ve öteki filtreler **hiç
    dokunulmadan** kalır: bu modülün tek işi, ölçü değişiminde düşen tek şeyi
    yerine koymaktır.

    ⚠ Zaman boyutunun ADI cube'lar arasında farklı olabilir. Cube değiştiyse ve yeni
    cube'un zaman boyutu farklı adlanıyorsa filtre **yeniden adlandırılır** — yoksa
    var olmayan bir kolona filtre yazılır ve sorgu **çalışma anında** patlar.
    """
    from app.cube_router import _norm as _r_norm
    from app.cube_router import is_all_time

    if not yeni_cq or not onceki_cq:
        return yeni_cq, False
    if _donem_filtreleri(yeni_cq):
        return yeni_cq, False                    # kullanıcı bu turda dönem verdi
    onceki = _donem_filtreleri(onceki_cq)
    if not onceki:
        return yeni_cq, False                    # oturumda kurulmuş bir dönem yok
    # ⚠ `is_all_time` NORMALİZE metin bekler (`tüm` → `tum`). Ham metinle çağırınca
    # sessizce `False` döndü ve *"tüm zamanlar"* isteği eski döneme geri sarıldı —
    # yani kullanıcının AÇIK talimatı hatırlanan bir bağlamla ezildi.
    # *Bir yardımcıyı sözleşmesini okumadan çağırmak, onu çağırmamakla aynıdır.*
    if is_all_time(_r_norm(soru or "")):
        # 🔴 Açık talimat, hatırlanan bağlamı EZER — tersi değil.
        return yeni_cq, False

    hedef_zaman = _zaman_boyutu(yeni_cq, cube_meta)
    tasinan = []
    for f in onceki:
        g = dict(f)
        if hedef_zaman:
            g["dimension"] = hedef_zaman
        tasinan.append(g)

    cq = dict(yeni_cq)
    cq["filters"] = [*(cq.get("filters") or []), *tasinan]
    _log.info("KÖK-4 dönem çapası taşındı: %s → %s (%d filtre)",
              onceki_cq.get("cube"), cq.get("cube"), len(tasinan))
    return cq, True


def _zaman_boyutu(cq: dict, cube_meta: dict | None) -> str | None:
    """Hedef cube'un zaman boyutu adı — yoksa `None` (filtre adı korunur)."""
    tds = (cube_meta or {}).get("time_dimensions") or []
    if tds:
        return str(tds[0])
    # Cube meta yoksa mevcut filtrelerden çıkarım yapma; ad değiştirmeden bırak.
    return None


#: Kullanıcıya gösterilen iz — **sessiz bir taşıma, sessiz bir varsayımdır**.
IZ = "dönem çapası önceki turdan taşındı (KÖK-4)"

#: Cevabın notuna eklenen açıklama. ⚠ Taşıma **görünür** olmalı: kullanıcı hangi dönemin
#: geçerli olduğunu tahmin etmek zorunda kalmamalı.
def not_metni(filtreler: list[dict]) -> str:
    ilk = next((f["value"][:10] for f in filtreler
                if str(f.get("operator")) in ("gte", ">=", ">")), None)
    son = next((f["value"][:10] for f in filtreler
                if str(f.get("operator")) in ("lte", "<=", "<")), None)
    if ilk and son:
        aralik = f"{_gun(ilk)} – {_gun(son)}"
    elif ilk:
        aralik = f"{_gun(ilk)} sonrası"
    else:
        return ""
    return f"⏱ Önceki turun dönemi korundu ({aralik}). Değiştirmek için dönemi yaz."


def _gun(iso: str) -> str:
    y, a, g = iso[:4], iso[5:7], iso[8:10]
    return f"{g}.{a}.{y}"


#: Notun `cube_query` üstünde taşındığı geçici anahtar. ⚠ **Taşıyıcıdır**: vardığı yerde
#: `notu_al` tarafından SİLİNİR. Sızarsa `cube_query` cevaba kirli gider ve daha kötüsü
#: SQL derleyicisine bilinmeyen bir alan olarak ulaşır.
_TASIYICI = "_capa_notu"


def tasi_yerinde(cq: dict, onceki_cq: dict | None, soru: str,
                 cube_meta: dict | None = None) -> bool:
    """`cq`yi **yerinde** çapalar; taşındıysa `True`.

    🔴 Neden yerinde: çağıran `_period_gate`in sözleşmesi *"`None` = devam et"*tir.
    Yeni bir dönüş türü eklemek DÖRT çağıranı birden değiştirirdi. Ve router'da kalan
    kod **iki satıra** iner — *taşınabilir olan her şey modüle gider* kuralının somut
    hâli (büyüme kapısı bunu iki kez ölçerek dayattı).
    """
    yeni, tasindi = tasi(cq, onceki_cq, soru, cube_meta=cube_meta)
    if not tasindi:
        return False
    cq["filters"] = yeni.get("filters") or []
    cq[_TASIYICI] = not_metni(cq["filters"])
    return True


def notu_al(cq: dict, note: str | None, trace: list[str]) -> tuple[str | None, list[str]]:
    """Taşıyıcıyı **boşalt** ve notu/izi cevaba kat. *Bir taşıyıcı alan, taşıdığı yere
    varınca boşaltılmalıdır.*"""
    metin = cq.pop(_TASIYICI, None) if isinstance(cq, dict) else None
    if not metin:
        return note, trace
    return " ".join(x for x in [note, metin] if x), [*trace, IZ]
