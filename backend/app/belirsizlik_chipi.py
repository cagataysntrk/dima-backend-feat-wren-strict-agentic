"""🔴 KÖK-9 — **BİLİNEN BELİRSİZLİK CHİP'E BAĞLANIR.** (denetim raporu KN-6 · KÇ-6)

## Ölçülen kusur

`schema["metrik_kaydi"]` bir terimi **kaç cube'un sahiplendiğini** derleme anında hesaplar.
Ölçüldü (2026-08-06, taze derleme):

    belirsiz terim: 62 / 62      ← kayıttaki HER terim ≥2 adaylı ve HİÇBİRİNİN sahibi yok
    cevaplanan sorularda: HIT+belirsiz 18 · HIT+net 136   → **%11,7**

Yani her sekiz cevaptan biri, **iki sahibi olduğu bilinen** bir terim üzerinden veriliyor
ve kullanıcı bunu **hiçbir yerden** öğrenemiyor:

| soru | terim | seçilen | adaylar |
|---|---|---|---|
| `haziran parti sayısı vardiya kırılımında` | `parti sayisi` | `oee` | `oee` · **`parti`** |
| `HAZIRAN ENERji tep çıkar` | `enerji tep` | `surdurulebilirlik` | `enerji_makine` · `enerji_tesis` · **`surdurulebilirlik`** |
| `vardiyalere göre adet getir` | `adet` | `oee` | **altı** cube |

⊙ Kazananı belirleyen şey bir karar değil bir **yan etkiydi**: aday üretecinde boyut
sayısı ve sinonim uzunluğu. *Sahipsiz bir terim yoktur; çok sahipli bir terim vardır.*

## 🔴 NEDEN REDDETMEK DEĞİL — ölçülüp reddedilmiş anti-çözüm

Aynı bilgiyle `route()`'u **susturmak** denendi (belirsizse `None` dön):

    korpus doğru-cube  %94,3 → **%83,6**      ← koşulsuz hâli
    boyahane erişim     %69  → %66            ← cube-düzeyi kanıt arayan dar hâli

Kaybın sebebi yapısal: bir soru terimi belirsiz olsa bile **cube'unu söylüyor** olabilir
(*"parti adedi"*). Reddetmek o kanıtı yok sayar.

> 🔴 Raporun ölçütü *"belirsizlik **sıraya** değil **CHİP'E** bağlansın"* der — sıradan
> çıkarmak değil, **yanına bir seçenek koymak**. Bu modül tam olarak onu yapar:
> **cevap gider, alternatif chip olarak beyan edilir.** Kapsam maliyeti **sıfırdır.**

Aynı disiplin `app/uyum.py`'nin *beyanlı kısmi cevabı*yla birebir aynıdır: ADR-0008'in
yasağı *"yanlış cevaba güven rozeti takmak"*tır; **beyan edilmiş** bir tercih rozet
takmaz — sorar.
"""

from __future__ import annotations

from typing import Any

#: Chip sayısı üst sınırı. ⚠ `adet` **altı** cube'a ait: altısını da basmak cevabı
#: gürültüye boğar ve *"her cevaba uyarı eklemek, uyarıyı okunmaz yapar"* (uyum.py'nin
#: kendi cümlesi). İlk üç alternatif, kullanıcının seçmesi için yeter.
EN_FAZLA = 3

#: Chip türü — `Suggestion.kind`. Frontend bunu AYRI bir grupta ve KENDİ açıklamasıyla
#: basar; devam sorusu kutusuna konamaz (bkz. `app/schemas.py::Suggestion`).
TUR_TANIM = "tanim"


def alternatifler(terim: str, kayit: list[dict[str, Any]] | None,
                  secilen_cube: str | None) -> list[str]:
    """Terimi sahiplenen **öteki** cube'lar — sahip beyan edilmişse **boş**.

    ⚠ Sahip beyan edilmişse belirsizlik **çözülmüştür**; chip basmak kullanıcıya
    kapatılmış bir soruyu tekrar sormak olurdu. `hakem` o durumda zaten seçimi yapar.
    """
    if not kayit or not terim:
        return []
    for k in kayit:
        if k.get("terim") != terim:
            continue
        if k.get("sahiplenilen_terimler"):
            return []                       # sahip var → belirsizlik yok
        adaylar = [str(a) for a in (k.get("adaylar") or [])]
        return [a for a in adaylar if a != secilen_cube][:EN_FAZLA]
    return []


def tanimlari_farkli_mi(terim: str, cubelar: list[str], schema: dict[str, Any]) -> bool:
    """🔴🔴 `§D10` — AYNI AD, **FARKLI FORMÜL** mü?

    ## Ölçülen kusur (2026-08-12)

    Katalogda **9 ölçü adı** birden çok küpte geçiyor. Üçünün formülü **farklı**:

        toplam_fire_kg          oee  : SUM(hatali_kg)
                                parti: SUM(CASE WHEN ilk_seferde_tamam = 0 THEN kg END)
        toplam_durus_dakika     bakim: SUM(durus_dakika)
                                oee  : SUM(planli_durus_dk + plansiz_durus_dk)
        ilk_seferde_tamam_yuzde oee  : … / NULLIF(SUM(parti_sayisi),0)
                                parti: … / NULLIF(COUNT(*),0)

    Öteki **altısı** (`bakiye` · `toplam_alacak` · `toplam_borc` · `toplam_dogalgaz_sm3` ·
    `toplam_tep` · `toplam_uretim_kg`) **bayt bayt aynı** formülü taşıyor.

    ⊙ Beyan bugüne kadar dokuzunu da **aynı cümleyle** geçiyordu: *«birden fazla yerde
    tanımlı»*. Ama iki durum aynı değil:

    | durum | kullanıcı için |
    |---|---|
    | aynı formül, iki küp | bir **kapsam** tercihi — sayı ikisinde de aynı hesaplanır |
    | **farklı formül** | bir **TANIM** farkı — öteki küpte sayı **başka bir şeydir** |

    WisdomAI'ın ölçümü bu ikinciyi *«açıklanamayan güven erozyonunun en büyük kaynağı»*
    diye adlandırıyor: kullanıcı iki yerde iki farklı sayı görür ve **ikisinin de doğru
    olduğunu** anlayamaz.

    > *İki tanımı «aynı ad» diye bir araya koymak, farkı adın arkasına saklamaktır.*

    ⚠ Yüklem **yapısal**: `measure_expressions` karşılaştırılır. Bir kelime listesi ya da
    bir sezgi değil — formül metni ya aynıdır ya değildir. Beyan yoksa (ifade
    yazılmamışsa) **fark iddia edilmez** (`§101.1`: bilinmeyeni bir fark saymak, olmayan
    bir riski icat etmektir).
    """
    ifadeler = set()
    for ad in cubelar:
        cm = next((c for c in (schema.get("cubes") or []) if c.get("name") == ad), None)
        e = ((cm or {}).get("measure_expressions") or {}).get(terim)
        if not e:
            return False                 # beyan eksik → fark İDDİA EDİLMEZ
        ifadeler.add(str(e).strip())
    return len(ifadeler) > 1


def beyani_ilistir(resp, terim: str, cube_meta: dict | None, chipler_: list[dict],
                   cq: dict, oteki: list[str], schema: dict[str, Any]) -> None:
    """🔴 `§Cİ`/`§D10` — **TEK ÇAĞRILIK YÜZ**: notu kurar ve cevaba iliştirir.

    ## Neden burada — ve bunu bir kapı söyledi

    Gövde `ask.py`'deydi ve dosya büyüme tavanı (`test_ASK_PY_DOSYASI_ASK_DISINDA_
    SESSIZCE_SISMIYOR`) kırmızı verdi. Kapının emri değişmiyor: *«yeni davranışı MODÜLE
    çıkar, tavanı yükseltme»*.

    ⊙ Ve doğrusu da bu: **karar** (hangi tanım seçildi · formüller farklı mı), **metin**
    ve **chip** aynı modülde durur. `ask.py`'de kalan tek şey çağrıdır.

    *Bir kararın, metninin ve chip'inin ayrı evlerde oturması, üç sahip demektir.*
    """
    resp.note = " ".join(x for x in [
        resp.note,
        not_metni(terim, cube_etiketi(cube_meta), [c["label"] for c in chipler_],
                  olcu=next(iter(cq.get("measures") or []), terim),
                  cubelar=[cq.get("cube"), *oteki], schema=schema),
    ] if x)


def not_metni(terim: str, secilen_etiket: str, oteki_etiketler: list[str],
              *, tanim_farkli: bool = False,
              olcu: str | None = None, cubelar: list[str] | None = None,
              schema: dict[str, Any] | None = None) -> str:
    """Cevabın notuna eklenen beyan — **kısa, tek cümle, suçlayıcı değil**.

    ⚠ *"Yanlış olabilir"* DENMEZ: sayı doğrudur, yalnız **hangi tanımın** kullanıldığı
    bir tercihti. *Bir tercihi bildirmek özür dilemek değildir.*

    ⟳ `§D10` (2026-08-12): `tanim_farkli=True` ise cümle **sertleşir** — çünkü o durumda
    öteki küpteki sayı bir kapsam farkı değil **başka bir hesap**tır. Varsayılan `False`:
    çağıran ölçmediyse fark iddia edilmez (`KURAL B` — eski çağrılar birebir aynı).
    """
    if not oteki_etiketler:
        return ""
    # ⟳ Karar **burada** verilebilir (2026-08-12): çağıran `olcu`+`cubelar`+`schema`
    # geçerse fark **bu modülde** hesaplanır. Sebep bir büyüme kapısıydı — `ask.py`'nin
    # dosya tavanı aşıldı ve kapının emri açık: *«yeni davranışı MODÜLE çıkar, tavanı
    # yükseltme»*. Ve doğrusu da bu: kararın ve metnin **tek sahibi** burasıdır.
    if olcu and cubelar and schema is not None:
        tanim_farkli = tanimlari_farkli_mi(olcu, cubelar, schema)
    oteki = " · ".join(oteki_etiketler)
    if tanim_farkli:
        return (f"⚠ «{terim}» birden fazla yerde ve **FARKLI FORMÜLLE** tanımlı — bu "
                f"cevap **{secilen_etiket}** tanımıyla hesaplandı. Diğerleri: {oteki}. "
                "Öteki tanımdaki sayı bir kapsam farkı değil, **başka bir hesaptır**.")
    return (f"«{terim}» birden fazla yerde tanımlı — bu cevap **{secilen_etiket}** "
            f"tanımıyla hesaplandı. Diğerleri: {oteki}.")


def chipler(terim: str, oteki_cubelar: list[str],
            schema: dict[str, Any],
            gereken_boyutlar: list[str] | None = None) -> list[dict[str, str]]:
    """`[{label, query}]` — chip tıklanınca **aynı belirsizliğe geri dönmemeli**.

    Bu yüzden `query` cube adıyla **nitelenir** (`olcu_netlestirme`'nin ve
    `ay_netlestirme`'nin aynı disiplini): *"kullanıcıyı aynı duvara ikinci kez çarptıran
    bir chip, chip olmamasından kötüdür."*

    ## 🔴 `gereken_boyutlar` — SORULAN KIRILIMI TAŞIMAYAN KÜP BİR ALTERNATİF DEĞİLDİR

    Canlıda ölçüldü (2026-08-12), *«bu yıl makine bazında tep»*:

        note = «tep» birden fazla yerde tanımlı — bu cevap **sürdürülebilirlik**
               tanımıyla hesaplandı. Diğerleri: tep (bölüm/makine enerji (ölçülen)) ·
               tep (tesis enerji (ISO-50001)).

    İkinci alternatif `enerji_tesis`'tir ve **`makine` boyutu YOKTUR** — yani kullanıcı
    o tanımı seçse *makine bazında* bir cevap **alamaz**. Beyan, veremeyeceği bir şeyi
    sayıyordu.

    ⊙ Ve bu, bu dosyanın kendi cümlesinin ihlaliydi: *"kullanıcıyı aynı duvara ikinci
    kez çarptıran bir chip, chip olmamasından kötüdür."* Kural yazılıydı; **kırılım
    ekseninde uygulanmıyordu**.

    ⚠ Süzgeç **yapısaldır** (boyut adı katalogda var mı), bir tahmin değil. Ve
    `gereken_boyutlar` boşsa (kırılımsız soru) hiçbir şey elenmez — bir süzgecin
    kapsamı, ölçtüğü şeyle sınırlı kalmalıdır.

    > *Bir alternatifi sunmak, onun sorulan soruyu cevaplayabileceğini söylemektir.*
    """
    gerekli = [str(b) for b in (gereken_boyutlar or []) if b]
    out: list[dict[str, str]] = []
    for ad in oteki_cubelar:
        cm = next((c for c in (schema.get("cubes") or []) if c.get("name") == ad), None)
        if cm is None:
            continue
        if gerekli:
            var = {(d.get("name") if isinstance(d, dict) else d)
                   for d in (cm.get("dimensions") or [])}
            if not set(gerekli) <= var:
                continue                # sorulan kırılımı veremiyor → alternatif DEĞİL
        etiket = cube_etiketi(cm)
        # 🔴 `kind="tanim"` — bu chip bir DEVAM SORUSU değil: aynı soruyu BAŞKA BİR
        # TANIMLA yeniden sorar. `ReportCard` devam sorularını *"bu cevabın üstünde
        # konuşur — yeni sorgu yazılmaz"* diye açıklıyor ve o cümle bunun için YANLIŞ
        # olurdu. *Bir chip'in yanındaki açıklama, chip'in kendisi kadar bir vaattir.*
        out.append({"label": f"{terim} ({etiket})", "query": f"{etiket} {terim}",
                    "kind": TUR_TANIM})
    return out


def cube_etiketi(cube_meta: dict[str, Any]) -> str:
    """Kullanıcıya gösterilecek cube adı.

    ## 🔴 SIRA ÖLÇÜMLE DÜZELTİLDİ — ilk yazım YANILTICIYDI

    İlk yazım *"ilk sinonim, yoksa teknik ad"* diyordu ve `eval` koşumunda ne ürettiği
    görüldü:

        «sapma» birden fazla yerde tanımlı — bu cevap **fire** tanımıyla hesaplandı.

    `fire`, `parti` cube'unun ilk sinonimidir — ama kullanıcı için o **başka bir
    ölçünün adıdır**. Cümle *"sapmayı fire olarak hesapladım"* diye okunuyordu ve bu,
    beyan etmeye çalıştığımız şeyin tam tersini söylüyordu.

    🔴 Doğru sıra: **`display` → teknik ad → ilk sinonim.** `display` katalogda tam da
    *"bu cube'un insan adı"* olarak duruyor; sinonimler ise **eşleşme** için var ve
    ilkinin bir ad olması **tesadüftür**.

    *Bir alanı amacı dışında kullanmak, çoğu zaman bir kez işe yarar ve sonra yanıltır.*

    ⚠ `!` işaretçisi kırpılır — o bir eşleşme kuralıdır, gösterilecek metin değil.
    """
    ad = cube_meta.get("display") or cube_meta.get("name")
    if ad:
        return str(ad).removesuffix("!")
    syns = cube_meta.get("synonyms") or []
    return str(syns[0]).removesuffix("!") if syns else ""

def belirsizlik_meta(soru: str, cq: dict[str, Any] | None,
                     schema: dict[str, Any] | None) -> dict[str, Any] | None:
    """🔴🔴 `§14.11 D9` — **MAKİNE-OKUNUR BELİRSİZLİK** (MCP/ajan yüzeyi için).

    ## Ölçülen boşluk

    HTTP `/ask` belirsizliği **hem beyan ediyor hem yapısal aday veriyor**:

        note        : «fire» birden fazla yerde ve FARKLI FORMÜLLE tanımlı…
        suggestions : [{"kind":"tanim", "label":"fire (OEE)", "query":"OEE fire"}]

    MCP yolu (`mcp.cagir` → `Planlayici.calistir`) o zincire **hiç uğramıyordu**:
    aynı soruda ajan `toplam_fire_kg`'yi alıp `oee` küpündeki **aynı adlı, başka
    hesaplı** ölçünün varlığını **bilemiyordu**. `§14.14 D10`'un insanlar için
    kapattığı sessiz-yanlış, ajan yüzeyinde **açıktı**.

    ## ⊘ Ve kartın ÖTEKİ yarısı REDDEDİLDİ — gerekçesiyle

    Metabase deseni `400` + `agent_error: true` istiyor, yani **cevabı geri çekmek**.
    Bu depoda üç ölçülmüş sebeple alınmıyor:

    1. Bugünkü davranış **daha iyi**: cevap **verilir**, belirsizlik **beyan edilir**,
       öteki tanıma **tek tık** üretilir (`§38 D4` canlı doğrulandı). `400` bunu
       *«kullanıcı asla cevapsız kalmaz»* ve *«dürüst red başarı değil»* kurallarının
       **tersine** çevirirdi.
    2. MCP'de `400`'ün karşılığı `isError: true`'dur ve bir ajan için bu bir **araç
       arızasıdır**, bir netleştirme daveti değil — ajan ya yeniden dener ya **uydurur**.
    3. `§40.9`'un kendi ölçümü: **netleştirme bir red değildir** (2.755 · %18,4).
       Belirsizliği redde çevirmek o %18,4'ü `cevapsız`a yazmak olurdu.

    ✅ Alınan yarı budur: **aday listesi**, `isError`'a dokunmadan.

    ⚠ `KURAL B`: belirsizlik yoksa `None` döner ve çağıran hiçbir alan eklemez —
    çıktı bayt bayt eskisiyle aynı kalır.

    → `{"terim", "secilen_cube", "adaylar": [...], "tanim_farkli": bool, "beyan": str}`
    """
    if not cq or not schema:
        return None
    kayit = schema.get("metrik_kaydi")
    secilen = cq.get("cube")
    if not kayit or not secilen:
        return None
    from app import cube_router as _cr

    cm = next((c for c in (schema.get("cubes") or []) if c.get("name") == secilen), None)
    if cm is None:
        return None
    terim = _cr._match_measure(_cr._norm(soru or ""), cm)[1]
    if not terim:
        return None
    oteki = alternatifler(terim, kayit, secilen)
    if not oteki:
        return None
    farkli = tanimlari_farkli_mi(terim, [secilen, *oteki], schema)
    return {
        "terim": terim,
        "secilen_cube": secilen,
        "adaylar": [cube_etiketi(c) for ad in oteki
                    for c in (schema.get("cubes") or []) if c.get("name") == ad],
        "tanim_farkli": bool(farkli),
        "beyan": not_metni(terim, cube_etiketi(cm),
                           [cube_etiketi(c) for ad in oteki
                            for c in (schema.get("cubes") or []) if c.get("name") == ad],
                           tanim_farkli=bool(farkli), olcu=terim,
                           cubelar=[secilen, *oteki], schema=schema),
    }
