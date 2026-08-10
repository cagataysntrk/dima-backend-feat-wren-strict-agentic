"""🔴🔴 `C1`+`C3`+`C3-D` — **TERS YÖN: sistem sözlüğünü KULLANIMDAN yazar.**

Kullanıcı kuralı: *"tek tek sinonim yazmak mesela aptallık."* Bu modül o kuralın
**ikinci yarısını** da taşır: LLM'den istemek de bir çözüm değil — aynı işi her gün
**yeniden satın almaktır**.

| yol | ek maliyet | canlı sonuç |
|---|---|---|
| `prompt_enhancer` | 🔴 **+1 LLM turu** | `C6`'da ölçülüp reddedildi |
| `eslesen_terim` alanı — modelden **iste** | +379 karakter × k=3 | 🔴 iki biçim, iki başarısızlık |
| ✅ **`eslesen_terim_cikar` — çıkar** | **0 token** | dördü de çalıştı |

## Neden `cube_router`'dan ÇIKARILDI — ve bunu bir KAPI istedi

`cube_router.py` bugün 1964 satıra çıktı ve **modül büyüme tavanı** (1893) kırmızı
verdi. Kapının kendi mesajı: *«yeni davranışı modüle çıkar, tavanı yükseltme. Tavanı
yükseltmek kapıyı kapının kendisiyle çürütür.»*

⊙ Ve ayrım **yapısal olarak doğru**: bu dosya *«kullanıcının sözü hangi katalog adına
karşılık gelir»* sorusunu **kaydeder**; `cube_router` ise *«bu soru hangi sorguya
çevrilir»* sorusunu **cevaplar**. İkisi aynı sözlüğü okur ama biri **öğrenir**, öteki
**çalışır**.

*Bir tavanı yükseltmek bir kazanç değildir; ölçülmeden yükseltmek bir borçtur.*
"""

from __future__ import annotations

from app.cube_router import _syn_hit_words, partial_unknowns

#: 🔴 `C3` — ters yön alanının **iz öneki**. Sabit, çünkü `lab/sinonim_hasadi.py` bu
#: dizeyi `interaction_log.trace_json` içinde arayarak kanıtlı aday üretir. *Bir izi
#: makine okuyacaksa, o iz bir biçimdir; biçimi değiştirmek okuyucuyu kırar.*
TERIM_IZ_ONEKI = "ters-yön eşlemesi: "

#: Kazanan `cq`'ya iliştirilen taşıyıcı. **Oylamadan SONRA** konur (`_select_consistent`),
#: yani hiçbir oy anahtarına giremez; huni onu boşaltır (`donem_capasi._TASIYICI` deseni).
TERIM_TASIYICI = "_eslesen_terim"


def eslesen_terim_oku(ham: str, index: dict, cube: str | None) -> dict | None:
    """🔴🔴 `C1`+`C3` — **TERS YÖN: sistem sözlüğünü KULLANIMDAN yazar.**

    ## Neden bir alan, bir ÇAĞRI değil

    Kullanıcı kararı (`E-7`): *"belki bunu sorgu içinde çözeriz, ayrı LLM sorgusu
    olmayacak — dikkat, çok vakit ve maliyet kaybı olur."* Bugünkü `prompt_enhancer`
    **ikinci bir tur**dur. Oysa Intent çağrısı kataloğu **zaten** görüyor ve **zaten**
    koşuyor: model `zayiat → toplam_fire_kg` eşlemesini **zaten yapıyor**, ondan istenen
    tek şey onu **söylemesi**. Ek çağrı **sıfır**.

    ## Ve sorunun BİÇİMİ — açık üretim değil, KAPALI SEÇİM (`C1`)

    Kullanıcı kararı: *"LLM de tüm eş anlamlıları bulmayacak; **katalogdaki
    kelimelerden birinin** eş anlamlısı var mı diye bakacak — yani nokta atışı."*

    | | ❌ açık üretim | ✅ **kapalı seçim** |
    |---|---|---|
    | çıktı | serbest **metin** | katalogdan **bir ad** ya da **hiçbiri** |
    | doğrulanabilir mi | 🔴 hayır — `route()` yeniden koşulmadan anlaşılmaz | ✅ **evet** — dönen ad beyaz listede sınanır |

    Bu fonksiyon o sınamadır: `katalog_adi` **seçilen küpün** ölçü/boyut listesinde
    yoksa eşleme **yok sayılır**. Model bir ad **uyduramaz**, yalnız **seçebilir**.

    ## Sert sınırlar (`B-8`)

    * `kullanicinin_sozu` kataloğun **zaten bildiği** bir kelimeyse eşleme değersizdir
      (bir sinonim zaten var) → düşürülür.
    * Eşleme **izde görünür** — sessiz bir öğrenme, öğrenme değil **sızıntıdır**.
    * ⚠ **Belirsizlik burada çözülmez:** `bakiye` gibi ≥2 sahipli bir terim için üretilen
      eşleme kuyruğa **düşmez** — o kararı `sinonim_hasadi.siniflandir` verir ve
      *«`bakiye`'nin ₺11,86 milyonluk seçimini KALICI yapmak»* yasaktır.

    Döner: `{"soz": …, "ad": …}` ya da `None`.
    """
    import json as _json

    try:
        ham_cq = _json.loads(ham)
    except Exception:                                   # noqa: BLE001 — tur düşmez
        return None
    if not isinstance(ham_cq, dict):
        return None
    et = ham_cq.get("eslesen_terim")
    if not isinstance(et, dict):
        return None
    soz = str(et.get("kullanicinin_sozu") or "").strip()
    ad = str(et.get("katalog_adi") or "").strip()
    if not soz or not ad or len(soz) < 3:
        return None
    spec = index.get(cube or ham_cq.get("cube")) or {}
    # 🔴 KAPALI SEÇİM DOĞRULAMASI — model **seçer**, uyduramaz.
    if ad not in set(spec.get("measures") or []) | set(spec.get("dimensions") or []):
        return None
    return {"soz": soz, "ad": ad}


def eslesen_terim_cikar(q: str, cq: dict | None, schema: dict) -> dict | None:
    """🔴🔴 `C3-D` — **EŞLEME MODELDEN İSTENMEZ, ÇIKARILIR.**

    ## Ölçülen kusur — ve iki başarısız prompt denemesi

    `C3`'ün ilk yazımı eşlemeyi **modelden** istiyordu (`eslesen_terim` alanı). Canlıda
    **iki kez** ölçüldü ve **ikisi de başarısız**:

    | deneme | biçim | sonuç |
    |---|---|---|
    | 1 | düzyazı talimat, *"isteğe bağlı"* | alan **hiç** yazılmadı |
    | 2 | `Biçim:` şablonunda + **"ZORUNLUDUR"** | alan yine **hiç** yazılmadı |

    Üç turda üçünde de model **doğru çevirdi** (`zayiat→toplam_fire_kg` ·
    `hasılat→toplam_ciro` · `alıcı→musteri`) ama çevirisini **söylemedi**. Ne kabul ne
    red izi — yani alanı hiç üretmedi.

    ⊙ *Bir modelden cevabı taşımayan bir alanı doldurmasını istemek, ona bir dipnot
    yazdırmaktır; cevabı verir, dipnotu atlar.*

    ## Kök çözüm: sinyaller ZATEN elde

    Sistem her turda **iki şeyi birden** hesaplıyor ve **ikisini de ize yazıyor**:

        niyet: … bilinmeyen=zayiat        ← route'un çözemediği kelime
        cq:   measures:["toplam_fire_kg"] ← garsonun seçtiği ad

    Eşleme bu ikisinin **kesişimidir**. Modelden bir şey istemeye gerek yok: ek token
    yok, sağlayıcı bağımlılığı yok, prompt riski yok.

    ## Kural — ve neden bu kadar dar

    1. Soruda **tam bir** bilinmeyen kelime olmalı.
    2. `cq`'daki ölçü/boyut adlarından **route'un kendi sözlüğüyle ulaşabildikleri**
       elenir — o adlar zaten biliniyordu, bilinmeyen kelimenin karşılığı olamazlar.
    3. Geriye **tam bir** hedef kalmalı.

    ⚠ Üçünden biri tutmazsa `None`. *«alıcı bazında ciro»* bu yüzden çalışır: `ciro`
    route'un sözlüğünde **var** (elenir), `musteri` **yok** (kalır) → `alici → musteri`.
    Ama iki bilinmeyenli bir soruda hangi kelimenin hangi ada gittiği **bilinemez** ve
    tahmin etmek, bu deponun bugün üç kez uyguladığı *«tekil aday yoksa sus»*
    disiplinini bozardı.

    *Bir sistemin sözlüğünü elle yazmak, onu her gün yeniden yazmaya razı olmaktır —
    ama bir LLM'den yazmasını istemek de onu her gün yeniden SATIN ALMAKTIR.*
    """
    if not isinstance(cq, dict) or not cq.get("cube"):
        return None
    bilinmeyen, _hits = partial_unknowns(q, schema)
    if len(bilinmeyen) != 1:
        return None
    soz = str(bilinmeyen[0])
    if len(soz) < 3:
        return None
    spec = next((c for c in (schema or {}).get("cubes") or []
                 if c.get("name") == cq["cube"]), None)
    if not spec:
        return None
    msyn = spec.get("measure_synonyms") or {}
    dsyn = spec.get("dimension_synonyms") or {}
    hedefler: list[str] = []
    for ad in [*(cq.get("measures") or []), *(cq.get("dimensions") or [])]:
        ad = str(ad)
        syns = list(msyn.get(ad) or dsyn.get(ad) or [])
        # 🔴 Route bu adı sorudan **bulabiliyorsa** o ad zaten biliniyordu; bilinmeyen
        # kelimenin karşılığı olamaz. Aynı `_syn_hit_words`, aynı kapsam kuralı —
        # ikinci bir eşleştirici yazmak `KAT-1` olurdu.
        if not _syn_hit_words(q, [ad, *syns]):
            hedefler.append(ad)
    if len(hedefler) != 1:
        return None
    return {"soz": soz, "ad": hedefler[0]}
