"""🔴 **ÜSTÜNLÜK → SIRALAMA — tek sahip.**

Bu modülün var olma sebebi tek cümle: *"en çok fire veren makine hangisi"* **sırasız**
bir tablo döndürüyordu ve sistem bunu **beyan ediyordu** (`eksik_niyet:['ustunluk']`) —
yani eksikliği biliyor, kapatmıyordu.

Kural üç ayrı yerde yaşıyordu (`route` · `deterministic_refine` · Intent-JSON sonrası
**hiç**) ve üçü aynı cümleye farklı davranıyordu — `KAT-1`'in tanımı. Buraya taşındı;
tüketicileri `cube_router.deterministic_refine`, `ask.py`'nin ortak hunisi ve dönem
netleştirmesidir.

⚠ `cube_router`'ı **çağrı anında** import eder: `cube_router` bu modülü kullanıyor,
tersi bir modül-düzeyi import döngü olurdu.
"""

from __future__ import annotations

import re as _re


def _cr():
    from app import cube_router
    return cube_router


def olcut(q: str, olculer: list[str], cube_meta: dict | None):
    """Sıralama **ölçütü** — `en çok X` ifadesinden, TÜM sorgudan DEĞİL.

    ⚠ Bu ayrım canlıda ölçülerek öğrenildi (2026-07-25): *"en çok **SATILAN** 10 ürünün
    **ORTALAMA FİYATI**"* → fiyata göre sıralayıp **yanlış ürünleri** seçmişti. Yani
    gösterilen ölçü, sıralama ölçütünü **çalabilir**.

    Pencere: üstünlük ipucundan (`en çok`) sayıya kadar. Sayı yoksa ipucundan sonrası —
    çünkü *"en çok fire veren makine"*de ölçüt (`fire`) ipucunun hemen ardındadır.
    """
    if len(olculer) == 1:
        return olculer[0]
    q2 = _cr()._REL_DATE.sub(" ", q)
    cue = _cr()._TOPN_CUE.search(q2)
    if cue:
        nm = _re.search(r"\b(\d+)\b", q2[cue.end():])
        seg = q2[cue.end():cue.end() + nm.start()] if nm else q2[cue.end():]
        aday = _cr()._match_measure(seg, cube_meta)[0] if cube_meta else None
        if aday in olculer:
            return aday
    return olculer[0]


def tamamla(cq: dict, q: str, cube_meta: dict | None = None, *,
            sema: dict | None = None) -> bool:
    """🔴 **ÜSTÜNLÜK İSTENDİ VE SIRALAMA YOK → SİSTEM KOYAR.** Döner: değişti mi.

    ## Ölçülen kusur — dört tur, tek kök

    | soru | `cq` | beyan |
    |---|---|---|
    | `bu yıl en çok fire veren makine hangisi` | sırasız, 11 satır | `eksik_niyet:['ustunluk']` |
    | `bu üçüne en çok hangi renkleri sattığımı göster` | sırasız, 40 satır | `eksik_niyet:['ustunluk']` |
    | `ciromun en büyük 3 kaynağı olan müşterilerimi bul` | sırasız, 8 satır | — |
    | `en az üretim yapan 3 makine` | ✅ `order:asc` + `limit:3` | — |

    Dördüncüsü çalışıyordu; ilk üçü değil. Ve sistemin kendi cevabı kusuru **yazıyordu**:

    > *«en yüksek/en çok dedin ama sıralama uygulayamadım. **«en yüksek 5 makine» gibi
    > sayı verirsen** sıralayıp keserim.»*

    🔴 **Sıralama bir kesme sayısına ihtiyaç duymaz.** *"En çok fire veren makine
    hangisi"* sorusunun cevabı **sıralı bir tablonun ilk satırıdır**; sayı, kaç satır
    **gösterileceğini** söyler — hangisinin **önce** geleceğini değil. İkisini birbirine
    bağlamak, sistemi kendi bildiği bir şeyi uygulayamaz hâle getirir.

    ⊙ Ve sistem gerçekten **biliyordu**: `uyum.py` eksikliği tespit edip beyan ediyor,
    yön `_cr()._direction(q)`'dan deterministik geliyor, ölçüt `cq`'nun kendi ölçüsü.
    Elinde her şey vardı; yalnız **uygulamıyordu**.

    *Bir eksikliği doğru teşhis edip yalnız anlatmak, onu kapatmanın yerine geçmez.*

    ## Sınır

    ⚠ **Yalnız sıralama** konur, `limit` **konmaz**: kaç satır gösterileceği kullanıcının
    kararıdır ve sayı vermediyse **kesmemek** doğrudur. *Sıralamak bilgi ekler, kesmek
    bilgi çıkarır — ikisi aynı izinle yapılmaz.*

    ⚠ `entity_limit` varsa dokunulmaz: o zaten kendi sıralamasını taşır.
    """
    if not isinstance(cq, dict) or cq.get("order") or cq.get("entity_limit"):
        return False
    olculer = [m for m in (cq.get("measures") or []) if m]
    if not olculer:
        return False
    # ⚠ `cube_meta` her çağrı yerinde kapsamda **değil** (ortak huni yalnız `schema`
    # taşıyor). Aramayı buraya koymak, `ask.py`'de dördüncü bir `next(c for c in
    # schema["cubes"] …)` kopyası yazmaktan iyidir — o arama zaten o dosyada **beş** kez
    # tekrarlanıyor. *Bir aramanın tekrarı, aranan şeyin sahibinin belirsiz olduğunun
    # işaretidir.*
    if cube_meta is None and sema:
        cube_meta = next((c for c in (sema.get("cubes") or [])
                          if c.get("name") == cq.get("cube")), None)
    qn = _cr()._norm(q or "")
    # 🔴 `§W-C` — ÖLÇÜT ÖNCE, YÖN SONRA. Sıra bilerek ters çevrildi: *"en kötü"*nün yönü
    # **hangi ölçünün** sıralandığına bağlı (`lower_is_better`), yani ölçüt bilinmeden yön
    # bilinemez. Eskiden yön önce hesaplanıyordu ve ölçünün beyanı hiç sorulmuyordu —
    # sonuç: `lower_is_better` beyanlı HER ölçüde *"en kötü"* tam tersini veriyordu.
    # *Bir sıfatın yönünü sözlükten okumak, ölçünün kendi beyanını görmezden gelmektir.*
    _olcut = olcut(qn, olculer, cube_meta)
    _az_iyi = _olcut in set((cube_meta or {}).get("lower_is_better") or [])
    yon = _cr()._direction(qn, _az_iyi)
    if not yon:
        return False
    cq["order"] = {"measure": _olcut,
                   "direction": "asc" if yon == "ASC" else "desc"}
    # 🔴 **`§O3` — SIRALAMAYI KURTARDIK, SAYIYI YERDE BIRAKTIK.**
    #
    # Yukarıdaki sınır *"**sayı vermediyse** kesmemek doğrudur"* diyor — ve kendi
    # tablosunun 4. satırı (`en az üretim yapan 3 makine → order:asc + limit:3`) sayının
    # **verildiği** hâli **beklenen davranış** olarak gösteriyor. Yani kural zaten iki
    # durumu ayırıyordu; **uygulaması ayırmıyordu**.
    #
    # Ölçüldü (O turu, `o11`, **iki koşum birebir** — `KURAL G-1`): `en az arıza veren 5
    # makine` →
    #
    #     SONDAJ-O11: order=None limit=None cq_limit=None dims=['makine'] gran=None
    #     niyet: tür=kirilim+ustunluk · kırılım=makine,ariza_tipi · üstünlük=5
    #
    # `route()` **ikisini birden** düşürdü (yönü bulamayınca sayı da düştü); bu fonksiyon
    # sıralamayı geri koydu, **sayıyı kimse geri koymadı**. Kullanıcı *"5"* dedi ve
    # sıralanmış ama **kesilmemiş** bir tablo aldı. `niyet` sayıyı biliyordu.
    #
    # ⚠ Bu, `§N4`'ün **taze yoldaki ikizidir** (`§N4` takip/refine yolunu düzeltmişti) —
    # ve aynı seri-koruma kaydını taşır: zaman kovası **başka bir boyutla** birlikteyse
    # satır limiti seriyi keser, orada konmaz (`entity_limit`'in işi).
    #
    # ⚠ Sayı **çıkarımla değil, kullanıcının ağzından** gelir (`_top_n`). *Sayı verilmişse
    # kesmek bilgi çıkarmaz — sözü yerine getirir.*
    if not cq.get("limit") and not cq.get("entity_limit"):
        _n = _cr()._top_n(qn, cube_meta)
        _gran, _boy = bool(cq.get("timeDimensions")), bool(cq.get("dimensions"))
        if _n and not (_gran and _boy):
            cq["limit"] = _n
        elif _n:
            # 🔴 **`§R1b` — «SERİYİ KESER» DEDİM VE ORADA DURDUM; OYSA O DURUMUN ZATEN BİR
            # SAHİBİ VARDI.** `§O3`'te satır limitini zaman kovası + boyut birlikteyken
            # engelledim — gerekçe doğruydu (satır limiti seriyi ortadan keser) ama
            # **eksikti**: o durum bir *"yapılamaz"* değil, `entity_limit`'in **tam
            # tanımıdır** (ilk N **varlık** seçilir, serileri korunur; `ask.py`
            # `_resolve_entity_limit` ile iki adımda çözer).
            #
            # Ölçüldü (`r11`): `bu yıl en çok rework yapılan **3** makineyi bul` →
            # `üstünlük=3`, `order` kondu, kesme **hiç** olmadı → **11 satır**.
            # `route()` bu vakayı doğru çözüyor (`cube_router` `gran and dims and n and
            # direction` → `entity_limit`); garson yolundan gelen `cq` o dala hiç
            # uğramıyordu. Yani kural vardı, **ikinci yolda yoktu**.
            #
            # ⚠ Ölçüt route'un kendi ölçütüyle **aynı** tutuldu (ilk boyut · aynı ölçü ·
            # aynı yön) — ikinci bir top-N tanımı yazmak `KAT-1` olurdu.
            #
            # *Bir yeteneğin iki yoldan yalnız birinde bulunması, o yeteneğin yarısının
            # olmamasıdır.*
            cq["entity_limit"] = {
                "dimension": (cq.get("dimensions") or [None])[0],
                "measure": cq["order"]["measure"],
                "direction": cq["order"]["direction"],
                "n": _n,
            }
    return True
