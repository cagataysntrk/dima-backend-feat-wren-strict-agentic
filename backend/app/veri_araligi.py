"""🔴 KÖK-8b — **boş sonuç sessiz kalmasın.** (denetim raporu KN-5)

## Ölçülen kusur

`partiler` ve `oee_vardiya` **2026-06-30**'da bitiyor; bugün **2026-08-05**. Yani
*"bu ay"* = Ağustos, *"geçen ay"* = Temmuz → **veri yok**.

```
"bu ay oee"  →  route() ✅ doğru cube + doğru ölçü + doğru dönem filtresi
             →  SQL koşar
             →  0 satır
             →  cevap DÖNER, ama "bu dönemde veri yok" DENMEZ
```

Cube seçimi doğru, ölçü doğru, filtre doğru — **yalnız o aralıkta veri yok.** Ve
kullanıcı bunu **bir ürün kusuru** sanıyor: sayı yok, hata yok, açıklama yok.

## 🔴 Ve rapordan bir adım öte: TAZELİK ÜNİFORM DEĞİL, KARIŞIK

Denetimde ölçüldü — rapor bunu kaydetmemişti:

| kaynak | son tarih |
|---|---|
| `build_data.py:38` `END` | **2026-06-30** → `partiler` · `oee_vardiya` |
| `genisletme.py:79` `GENIS_SON` | **2026-08-31** → `is_kazalari` **2026-08-17**'ye kadar dolu |

Yani *"bu ay"* sorusu **OEE'de boş, iş kazasında dolu** dönüyor. Bu üniform bayatlıktan
**daha kötüdür**: kullanıcı *"veri Haziran'da bitiyor"* kuralını **öğrenemez**, çünkü
kural yok. Bu yüzden aralık **cube başına** ölçülür, tek bir global tarih varsayılmaz.

## Neden `SyncState` tazelik zinciri DEĞİL

`tazelik` bayrağı (`features.yml`) `SyncState`e bağlı ve demo/DuckDB tenant'larında
`SyncState` **yok** → hepsi `bilinmiyor` → o kademede **sayı gizlenir**. Yani bayrağı
açmak bugün bütün demoda sayıları saklardı. Bu modül farklı bir soru soruyor:

> *"Sorgu 0 satır döndürdüyse, sebebi istenen dönemin veri aralığının dışında olması mı?"*

Cevap **verinin kendisinden** okunur (`min`/`max`), bir senkron kaydından değil — bu
yüzden her tenant'ta, bayraksız çalışır.

⚠ Ve **yalnız 0 satırda** çalışır: dolu bir cevaba hiç dokunmaz, maliyeti yoktur.
"""

from __future__ import annotations

import datetime as _dt
import threading

from app.logging_setup import get_logger

_log = get_logger("veri_araligi")

#: cube adı → (min, max) · `None` = ölçülemedi. Süreç ömrü boyunca önbellek.
#: ⚠ Demo verisi koşum sırasında değişmez; değişse bile en kötü sonuç **bayat bir
#: açıklama cümlesi**dir — sayı değil. *Bir önbelleğin riski, önbelleklediği şeyin
#: ağırlığı kadardır.*
_ONBELLEK: dict[str, tuple[str, str] | None] = {}
_KILIT = threading.Lock()


def aralik(service, cube_meta: dict) -> tuple[str, str] | None:
    """Cube'un zaman boyutundaki **gerçek** (min, max) — tek sorgu, önbellekli.

    `None` döner: zaman boyutu yok · sorgu başarısız · sonuç boş. ⚠ Üçü de **sessizce**
    değil: `None`, çağıranın *"açıklama üretemedim"* demesine yol açar, uydurmasına değil.
    """
    ad = str(cube_meta.get("name") or "")
    if not ad:
        return None
    with _KILIT:
        if ad in _ONBELLEK:
            return _ONBELLEK[ad]

    sonuc: tuple[str, str] | None = None
    try:
        tds = cube_meta.get("time_dimensions") or []
        taban = cube_meta.get("base_object")
        if tds and taban:
            td = tds[0]
            sql = f'SELECT MIN("{td}") AS min_t, MAX("{td}") AS max_t FROM "{taban}"'
            r = service.query(sql, limit=1)
            satir = (r.get("rows") or [{}])[0]
            a, b = satir.get("min_t"), satir.get("max_t")
            if a is not None and b is not None:
                sonuc = (str(a)[:10], str(b)[:10])
    except Exception:                                   # ADR-0020: sessiz yutma yok
        _log.warning("veri aralığı okunamadı: cube=%s", ad, exc_info=True)

    with _KILIT:
        _ONBELLEK[ad] = sonuc
    return sonuc


def bos_mu(result: dict | None, cube_query: dict | None) -> bool:
    """🔴 **BOŞLUK, SATIR SAYISI DEĞİL ÖLÇÜ DEĞERİ MESELESİDİR.**

    ## Ölçülen kusur — iki tur, tek kök

    | soru | dönen | kullanıcının gördüğü |
    |---|---|---|
    | `geçen ay ciro düştü mü` | `[{"toplam_ciro": null}]` | *«1 satırlık sonuç.»* |
    | `bu ay neye dikkat etmeliyim` | `[{ort_oee:null, plansiz_durus:null, fire:null}]` | *«1 satırlık sonuç.»* |

    Dürüst boş-sonuç notu (*«Bu aralıkta kayıt bulunamadı… elimdeki veri 01.01.2024 –
    30.06.2026»*) **ikisinde de susmuştu**, çünkü koşulu `row_count == 0` idi.

    ⊙ Sebep SQL'in kendisi: **gruplamasız bir toplulaştırma boş kümede sıfır satır
    değil, BİR NULL satır döndürür.** `SUM(x)` üzerinde `WHERE` hiçbir şey tutmazsa
    sonuç `[(None,)]`'dır. Yani dedektör, boşluğun **en sık** biçimini tam olarak
    kaçırıyordu: kırılımsız, tek dönemli soruyu — ki en çok sorulan soru odur.

    ⚠ Ve aynı kusur `m32a`'da **görünmüyordu**: `geçen ay kaç parti üretildi` bir
    `granularity: month` taşıyordu, yani **gruplanmıştı** ve gerçekten 0 satır döndü —
    not oradaki tek doğru cevabını verdi. *Bir dedektörün çalıştığı vaka, çalışmadığı
    vakayı gizleyebilir.*

    ## Sınır: FAIL-OPEN

    Ölçü adları satırlarda hiç görünmüyorsa (takma ad, ham SQL) **boş DENMEZ**. Bir
    sonucu yanlışlıkla *"kayıt yok"* diye örtmek, onu göstermekten kötüdür.

    *Boş bir küme üstündeki toplam, bir sayı değil bir yokluktur — ve yokluk «1 satır»
    diye sunulamaz.*
    """
    # 🔴 **ÖLÇÜLMEMİŞ ≠ BOŞ — ve bu satır bir GERİLEMEYİ onarıyor.**
    #
    # İlk yazımda `result is None` de "boş" sayılıyordu. Tam süit bunu yakaladı
    # (`test_execute_false_sql_uretir_ama_calistirmaz`): `execute=false` ile sorgu
    # **hiç çalıştırılmaz**, `result` `None`'dır — ve "boş" denince boş-sonuç notu
    # devreye girip veri aralığını ölçmek için **SQL çalıştırıyordu**. Yani
    # *"çalıştırma"* diyen bayrak, tam da benim eklediğim satır yüzünden çalıştırıyordu.
    #
    # ⊙ Bu, `§33`'ün `ASIM is not None` dersinin birebir tekrarı: iki farklı sebebi tek
    # değere çökertmek ikisini de kaybettirir. *Bir ölçüm yapılmadıysa «boş» denemez;
    # ölçülmemiş bir küme, boş bir küme değildir.*
    if result is None:
        return False
    r = result.get("rows") or []
    if not r or result.get("row_count") == 0:
        return True
    olculer = [m for m in ((cube_query or {}).get("measures") or []) if m]
    gorulen = [(s, m) for s in r if isinstance(s, dict) for m in olculer if m in s]
    if not gorulen:
        return False
    return all(s.get(m) is None for s, m in gorulen)


def bos_sonuc_notu(service, cube_query: dict, schema: dict) -> str:
    """0 satır dönen bir cube sorgusunun **tam** notu — dönem aralığı + veri aralığı.

    ## 🔴 Neden notun TAMAMI burada

    İlk uygulamada `ask.py` notu kuruyordu ve bu modül yalnız bir **ek cümle** veriyordu.
    Sonuç: aynı cümlenin iki yazarı ve `ask()`in büyüme kapısında **+10 satır**.
    Kapı haklıydı — *bir cevabın metnini kuran yer, onu kuran TEK yer olmalıdır.*

    Router'a kalan: **çağrı ve atama**. Metin, dönem okuması ve aralık ölçümü burada.

    ⚠ Not **DETERMİNİSTİKTİR ve UYDURMAZ**: yalnız sorgunun kendi dönem filtresini ve
    verinin gerçek min/max'ını okur. *"Veri yok"* demez — *"bu aralıkta kayıt
    bulunamadı"* der; ikisi farklı iddialardır.
    """
    dnm = [f for f in (cube_query.get("filters") or [])
           if f.get("operator") in ("gte", "lte")]
    bas = next((f["value"] for f in dnm if f["operator"] == "gte"), None)
    son = next((f["value"] for f in dnm if f["operator"] == "lte"), None)
    pencere = (f" ({str(bas)[:10]} – {str(son)[:10]})" if bas and son
               else (f" ({str(bas)[:10]} sonrası)" if bas else ""))

    # 🔴 Aralık CUBE BAŞINA ölçülür, global bir tarih varsayılmaz: denetimde ölçüldü ki
    # tazelik ÜNİFORM DEĞİL — `is_kazalari` 2026-08-17'ye kadar dolu (`genisletme.py`
    # GENIS_SON=2026-08-31) ama `partiler`/`oee_vardiya` 2026-06-30'da bitiyor
    # (`build_data.py` END). Tek bir tarih yazmak cube'ların yarısı için YANLIŞ olurdu.
    ek = ""
    cm = next((c for c in (schema.get("cubes") or [])
               if c.get("name") == cube_query.get("cube")), None)
    if cm:
        ar = aralik(service, cm)
        if ar:
            ek = f" Elimdeki veri **{_gun(ar[0])} – {_gun(ar[1])}** aralığında."
    return (f"Bu aralıkta{pencere} kayıt bulunamadı. Rapor doğru kuruldu — "
            f"dönemi genişletmek ya da filtreyi gevşetmek ister misin?{ek}")


# ⟳ `bos_sonuc_aciklamasi` + `_istenen_ust_sinir` KALDIRILDI (aynı turda).
# İlk tasarımda not `answer.py::seal`de kuruluyordu; `ask.py`nin ZATEN bir boş-sonuç
# notu ürettiği ölçülünce tasarım `bos_sonuc_notu`ya toplandı ve o ikisi ölü kaldı.
# 🔴 Ölü bırakmak yerine silindi: *ölü kod zararsız değildir — canlanana kadar bakımsız
# kalır, canlandığında yanlış olur.* Ve burada özellikle tehlikeliydi: aynı cümlenin
# ikinci bir yazarı, tam da bu turda kaçınılan şey.

def _gun(iso: str) -> str:
    """`2026-06-30` → `30.06.2026`. ⚠ Kullanıcıya ISO göstermek jargondur."""
    try:
        d = _dt.date.fromisoformat(iso[:10])
        return f"{d.day:02d}.{d.month:02d}.{d.year}"
    except ValueError:
        return iso
