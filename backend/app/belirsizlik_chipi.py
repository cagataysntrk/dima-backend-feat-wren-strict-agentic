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


def not_metni(terim: str, secilen_etiket: str, oteki_etiketler: list[str]) -> str:
    """Cevabın notuna eklenen beyan — **kısa, tek cümle, suçlayıcı değil**.

    ⚠ *"Yanlış olabilir"* DENMEZ: sayı doğrudur, yalnız **hangi tanımın** kullanıldığı
    bir tercihti. *Bir tercihi bildirmek özür dilemek değildir.*
    """
    if not oteki_etiketler:
        return ""
    oteki = " · ".join(oteki_etiketler)
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
