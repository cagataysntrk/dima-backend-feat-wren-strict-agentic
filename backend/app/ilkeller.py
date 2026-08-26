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


def hesapla_cumle(c: dict | None) -> str | None:
    """`hesapla()` çıktısını insan-okur bir cümleye çevirir — **TEK sahip** (`KAT-1`):
    plan_tuketici'nin hem teknik makbuzu (`_bulgu_metni`) hem kullanıcıya giden
    anlatısı (`_anlat`) aynı cümleyi buradan alır, iki ayrı şablon yazılmaz.

    ⚠ `fark_yuzde` `None` ise (payda sıfır — `hesapla()`'nın kendi uyarısı) `None`
    döner: doğrulanamaz bir "%0,0" uydurmaktansa cümleyi hiç kurmamak yeğdir.
    """
    if not isinstance(c, dict) or c.get("fark_yuzde") is None:
        return None
    from app.sayi_bicimi import sayi as _b, yuzde as _syuzde
    yon = "düşük" if (c.get("fark") or 0) < 0 else "yüksek"
    return (f"Akran ortalaması {_b(c.get('akran_ortalamasi'))} "
            f"({c.get('akran_sayisi')} akran) — aradaki fark "
            f"**{_syuzde(abs(c.get('fark_yuzde') or 0))} {yon}**.")


def matris(kaynaklar: list[list[dict]], boyut: str) -> list[dict]:
    """**`MATRIS` · SATIRLAR[] → SATIRLAR** — adayları ölçütlerle yan yana koyar.

    Her kaynak bir **ölçüt sütunu** getirir; `boyut` aday anahtarıdır. Saf ilişkisel
    birleştirme: LLM yok, SQL yok, aritmetik yok — yalnız hizalama.

    ## 🔴 SINIR — `MIMARI §12.9` ile çelişmez, onunla ÇİZİLMİŞTİR

    O bölüm *"seçenekler × ölçütler × ağırlıklar"* matrisini **bilinçle reddediyor**:
    *«kontrol edilebilirlik · uygulama maliyeti · risk … hiçbiri veride yok ve tahmin
    edilemez … `source=cube` rozetiyle uydurma sıralama»*.

    Buradaki matris o matris **değildir**:

    | reddedilen | bu |
    |---|---|
    | ölçütler **uydurulur** (risk, çaba) | ölçütler **katalogda var olan ölçülerdir** |
    | ağırlıklar modelden/sezgiden | ağırlık **yok** (bkz. `sirala`) |
    | sıralama bir **yargıdır** | sıralama bir **ölçümdür** |

    ⚠ Yani bu bir *karar* matrisi değil bir **karşılaştırma** tablosudur; kararı hâlâ
    insan verir. *Bir tabloyu karar diye satmak, ölçemediğin şeyi ölçmüş gibi
    göstermektir.*

    ⊙ Eksik hücre `None` kalır — sıfır **yazılmaz**. Bir adayda o ölçü hiç yoksa
    *"sıfır"* demek, yokluğu bir değere çevirmektir.
    """
    satirlar: dict[Any, dict] = {}
    for kaynak in (kaynaklar or []):
        for r in (kaynak or []):
            if not isinstance(r, dict) or boyut not in r:
                continue
            anahtar = r[boyut]
            hedef = satirlar.setdefault(anahtar, {boyut: anahtar})
            for k, v in r.items():
                if k != boyut and k not in hedef:
                    hedef[k] = v
    return list(satirlar.values())


def sirala(rows: list[dict], boyut: str, olculer: list[str],
           *, az_iyi: set[str] | frozenset[str] | None = None) -> list[dict]:
    """**`SIRALA` · SATIRLAR → SATIRLAR** — adayları çok ölçütle sıralar. **Ağırlık YOK.**

    🔴🔴 **AĞIRLIĞI MODEL KOYMAZ — ve burada hiç kimse koymaz.**

    *«Sayıyı her zaman küp koyar»* ilkesinin karar-matrisi karşılığı budur. Bir `agirliklar`
    alanı açmak, yasakladığımız aritmetiği **arka kapıdan** geri getirirdi: model bir sayı
    uydurur, o sayı sıralamayı belirler ve sonuç `source=cube` rozetiyle döner.

    Bu yüzden ağırlıklar **eşittir** ve bu bir varsayım değil bir **beyandır**: *"bu
    sıralama bütün ölçütlere eşit ağırlık verir"* denilebilir; *"risk %30, maliyet %70"*
    denemez, çünkü o oran hiçbir yerde ölçülmemiştir.

    Yön **beyandan** okunur (`az_iyi` ← `lower_is_better`), sözlükten değil — `§W-C`'nin
    dersi. Normalleştirme min-maks: tek satırda ya da sabit sütunda skor `1.0` (bölme
    yok).

    ⚠ Eksik hücre skora **girmez**, sıfır sayılmaz: eksik veriyle en kötü sıraya
    düşürmek, ölçülmemiş olanı ölçülmüş gibi cezalandırmaktır. Payda satır başına
    ayrı tutulur ve `_olcut_sayisi` olarak **yazılır** — kaç ölçütle sıralandığı
    görünmeden sıra okunamaz.
    """
    _az = set(az_iyi or ())
    _sinir: dict[str, tuple[float, float]] = {}
    for m in (olculer or []):
        _dgr = [sayi(r.get(m)) for r in (rows or [])]
        _dgr = [d for d in _dgr if d is not None]
        if _dgr:
            _sinir[m] = (min(_dgr), max(_dgr))

    out: list[dict] = []
    for r in (rows or []):
        toplam, n = 0.0, 0
        for m in (olculer or []):
            d = sayi(r.get(m))
            if d is None or m not in _sinir:
                continue
            lo, hi = _sinir[m]
            pay = 1.0 if hi == lo else (d - lo) / (hi - lo)
            toplam += (1.0 - pay) if m in _az else pay
            n += 1
        yeni = dict(r)
        yeni["_skor"] = round(toplam / n, 4) if n else None
        yeni["_olcut_sayisi"] = n
        out.append(yeni)
    # ⚠ Skorsuz satırlar **silinmez**, sona konur: bir adayı listeden düşürmek, onu
    # değerlendirilmiş göstermektir.
    return sorted(out, key=lambda r: (r["_skor"] is None, -(r["_skor"] or 0.0),
                                      str(r.get(boyut))))


def rapor(bolumler: list[Any], baslik: str) -> dict:
    """**`RAPOR` · SATIRLAR[] → BELGE** — koşmuş bölümleri tek bir belgeye dizer.

    ## 🔴 Neden `report.compose_report` ÇAĞRILMIYOR

    O fonksiyon bir **şartnameden** rapor üretir: blok başına `cube_query` alır ve her
    bloğu **koşar**. Ama plan o sorguları **zaten koştu**; onu çağırmak aynı sorguları
    ikinci kez ödemek olurdu — ve `E6`'nın (gecikme) tam da cezalandırdığı şey.

    ⊙ Bölüşüm net: `report.compose_report` **HTTP `POST /report`** yolunun gövdesidir
    (kullanıcı blokları kendi verir); bu ise **plan** yolunun gövdesi (bloklar zaten
    koşmuştur). Aynı çıktıyı iki yoldan üretmek bir kopya değil, iki farklı **girdiden**
    aynı yere varmaktır.

    ⚠ Hiçbir şey **hesaplamaz**: sayıları koşmuş adımlar koydu. Bu fonksiyon yalnız
    **dizer** — ve dizmek bir yorum değildir. *Bir raporu üretmekle, bir raporu
    kurgulamak aynı şey değildir; ikincisi sayı uydurmanın kapısıdır.*
    """
    _b: list[dict] = []
    for i, kaynak in enumerate(bolumler or [], 1):
        satirlar = [r for r in (kaynak or []) if isinstance(r, dict)] \
            if isinstance(kaynak, list) else []
        _b.append({"sira": i, "satir_sayisi": len(satirlar),
                   "kolonlar": list(satirlar[0]) if satirlar else [],
                   "satirlar": satirlar})
    return {"baslik": baslik, "bolumler": _b,
            # ⚠ Boş bölüm **gizlenmez, sayılır**: bir raporun eksiğini saklamak, onu
            # tam göstermektir.
            "bos_bolum": sum(1 for b in _b if not b["satir_sayisi"])}


def pano_taslagi(sorgular: list[Any], baslik: str) -> dict:
    """**`PANO` · SORGU[] → TASLAK** — 🔴 **YAZMAZ.**

    ## Neden bir taslak, neden kayıt değil

    Çalıştırıcı bugün **salt-okunur ve idempotenttir**. İlk yan etkili fiil bu değişmezi
    kırardı ve bedeli somut:

    * yarıda kalan bir plan **yarım bir pano** bırakır
    * aynı plan iki kez koşunca pano **ikilenir**
    * `PlanHatasi` ile düşen bir tur, geri alınamayan bir yazma bırakır

    Kalıcılaştırma çalıştırıcının **dışında**, kullanıcı onayıyla olur — `onay_akisi`
    bayrağının ve `authorize()`ın zaten kurulu olduğu yerde. *Bir yan etkiyi bir
    yorumlayıcıya koymak, geri alınamazlığı sessizce satın almaktır.*

    ## Widget'lar satır değil **SORGU** taşır

    Bir pano canlıdır: her açılışta yeniden koşar. Satır kaydetmek bir **fotoğraf**,
    sorgu kaydetmek bir **pano** yapar. Bu yüzden `kaynaklar` tipi `sorgu`dur
    (`KIR`/`SUZ` çıktısı ya da bir `SORGU` adımının kendi sorgusu).

    ⚠ Aynı sorgu iki kez geçse bile **ikilenmez**: bir panoda aynı kartı iki kez
    göstermek bir bilgi değil bir gürültüdür.
    """
    import json as _json

    goruldu: set[str] = set()
    widgetlar: list[dict] = []
    for cq in (sorgular or []):
        if not isinstance(cq, dict) or not cq.get("cube"):
            continue
        imza = _json.dumps(cq, sort_keys=True, ensure_ascii=False)
        if imza in goruldu:
            continue
        goruldu.add(imza)
        widgetlar.append({"sira": len(widgetlar) + 1, "cube_query": cq})
    return {"baslik": baslik, "widgetlar": widgetlar,
            # 🔴 Taslak olduğu **yazılı**: bir çıktının kalıcı olup olmadığını okuyanın
            # tahmin etmesi gerekmemeli.
            "kalici": False,
            "not": "Bu bir TASLAKTIR — onaylanmadan hiçbir pano oluşturulmadı."}
