"""🔴 **KATALOG METNİ** — LLM'in gördüğü dünya. [bayrak: `katalog_sozlugu`]

## Ölçülen kusur — ve neden mimarinin TERSİ

`route()` zengin bir Türkçe eşanlam katmanı kullanır: `oee` cube'u *"verim"*, *"randiman"*,
*"performans"* diye de anılabilir; `ort_oee` ölçüsünün sekiz sinonimi vardır. Bu katman
şemada **beyan edilmiş** ve deterministik yol onu **tam kullanıyor**.

⊙ Ölçüldü (2026-08-07, canlı denetim + yerinde doğrulama):

| | eşanlam katmanı | |
|---|---|---|
| `route()` — *en az güvendiğimiz basamak* | ✅ **tam** | `_syn_hit` · `_match_measure` |
| LLM — *en çok güvendiğimiz basamak* | 🔴 **HİÇ** | yalnız teknik kolon adları |

`build_catalog` prompt'a şunu yazıyordu:

    - oee: measures[ort_oee, ort_kullanilabilirlik, …]; dimensions[…]; time[tarih]

Katalogda `verim` **0 kez** · `randiman` **0** · `verimlilik` **0** · `hasılat` **0** ·
`bordro` **0** geçiyordu. 23 cube'un **23'ünde** `synonyms` **ve** `measure_synonyms`
beyan edilmiş olmasına rağmen.

🔴 Canlı sonucu: *"verimlilik"* soran bir kullanıcı için **9/9 Intent çağrısı
`{"cube":null}`** döndü. Oylama uyuşmazlığı değil — **aday yokluğu**. Model reddetti,
çünkü elindeki listede o kelime **yoktu**.

> Mimari tersine dönmüştü: *en çok güvendiğimiz basamak, en kör hâliyle koşuyordu.*

## ⚠ Bu `ADR-0008`'in İHLALİ DEĞİL — tam tersi

`ADR-0008`: *"dile kelime listesiyle yetişilmez."* Burada **yeni bir liste yazılmıyor**;
şemanın **zaten beyan ettiği** liste, onu okuması gereken ikinci tüketiciye veriliyor.
Yasak olan şey bir sözlük **icat etmek**tir; var olanı iki tüketiciden yalnız birine
göstermek bir tasarruf değil, bir **eşitsizliktir**.

*Bir bilgiyi beyan edip tüketicilerinden birine göstermemek, onu iki kez tanımlamaya
davettir — çünkü göremeyen taraf er ya da geç kendi listesini yazar.*

## Neden AYRI MODÜL

`cube_router.py` modül tavanında. Ve taşınacak şey rastgele seçilmedi: bu fonksiyon bir
**yönlendirme kararı vermez**, *"LLM'in gördüğü metin nasıl görünür"* sorusunu yanıtlar —
`app/intent_semasi.py` ile **aynı sınırın** öteki yarısı (o şemayı, bu düz metni üretir).
`cube_router` *"hangi cube, hangi ölçü"*nun sahibidir.

## 🔴 MALİYET ÖLÇÜLDÜ ve GİZLENMİYOR

Sözlük eki katalog metnini **~%54 büyütüyor** (ölçüm `tests/test_katalog_sozlugu.py`'de,
kapıyla kilitli). Ama bu **sabit bir önektir**: soru başına değişmez. Önbellekleme borcu
(`B6` — üç katmanlı önek) ödendiğinde tekrar etmeyen maliyete döner. Borç
`OPERASYON-DURUM.md`'de yazılı ve bu modül onun **ilk müşterisidir**.

⚠ **Liste içinden KIRPMA YOK.** Bir sinonimi listeden çıkarmak, tam da kapatmaya
çalıştığımız boşluğu o kelime için yeniden açardı. Sözlük **dedup** edilir (cube sinonimi
ölçü sinonimini tekrar ediyorsa bir kez yazılır), **kısaltılmaz**.

## 🔴 AMA BİR KATEGORİ DIŞARIDA: `dimension_synonyms` — ve sebebi ÖLÇÜLDÜ

| kapsam | katalog | oran |
|---|---|---|
| bugünkü (sözlüksüz) | 12.115 karakter | 1,00× |
| + cube sinonimleri | 14.709 | 1,21× |
| **+ ölçü sinonimleri** *(seçilen)* | **23.417** | **1,93×** |
| + boyut sinonimleri | 29.889 | 2,47× |

⚠ **İlk tahmin yanlıştı ve ölçüm düzeltti:** canlı denetim maliyeti *"+%54"* diye
raporlamıştı; yerinde ölçüm **2,47×** dedi. *Bir maliyet tahmini, ölçülene kadar bir
maliyet değildir.*

🔴 Boyut sinonimleri **maliyetin %30'unu** yiyor ama **ölçülen kusuru çözmüyor**: canlıda
başarısız olan şey **cube seçimiydi** (`{"cube":null}`), ve cube seçimini cube+ölçü
sinonimleri taşır. Boyut eşleştirmesi `route()`'un güçlü olduğu yerdir; model boyut
**adlarını** zaten görüyor ve o adlar zaten Türkçe (`hat`, `makine`, `vardiya`).

Bu bir kırpma değil bir **kapsam kararıdır** ve kapıyla kilitli
(`test_BOYUT_SINONIMLERI_BILEREK_DISARIDA`). Ölçüm tersini gösterirse karar geri alınır —
bu yüzden sayılar burada, gerekçenin yanında duruyor.

*Bir maliyeti ödemek için önce neyi satın aldığını ölçmek gerekir.*
"""

from __future__ import annotations

from app.logging_setup import get_logger

_log = get_logger("katalog_metni")

#: Tek bir madde için yazılacak sinonimleri saran işaretler. Köşeli/parantez DEĞİL:
#: ölçü adları zaten `[...]` içinde listeleniyor ve iç içe köşeli parantez, modelin
#: sınırı yanlış okuduğu ilk yerdir (ölçüldü: `measures[a [x, y], b]` → `a [x` ölçüsü).
_AC, _KAPA = "«", "»"


def _ek(adlar: list[str] | None, gorulen: set[str]) -> str:
    """`«a, b, c»` — **yeni** olanlar. Görülen bir terim ikinci kez yazılmaz.

    Dedup neden gerekli: bir cube'un kendi sinonimi çoğu zaman ana ölçüsünün sinonimini
    tekrar eder (`oee` → hem cube hem `ort_oee`). İkisini de yazmak metni büyütür ve
    modele **aynı bilgiyi iki kez** verir — ikinci kopya bir vurgu gibi okunabilir.
    """
    yeni = []
    for a in adlar or []:
        s = str(a).strip().rstrip("!")
        if s and s.lower() not in gorulen:
            gorulen.add(s.lower())
            yeni.append(s)
    return f" {_AC}{', '.join(yeni)}{_KAPA}" if yeni else ""


#: 🔴🔴 **`§W-C` — «EN KÖTÜ» BİR YÖNDÜR VE MENÜDE YAZMIYORDU.**
#:
#: Ölçüldü (`W19`): *«bu yıl kısım bazında karbon ayak izini **en kötüden iyiye** sırala»*
#: → `order: {"direction": **"asc"**}`. Yani en **düşük** karbon en üste kondu: sistem
#: kullanıcıya *«en iyiden kötüye»* verdi ve **öyle olduğunu söylemedi**.
#:
#: ⊙ Kusur garsonda değil **menüdeydi**: `lower_is_better` katalogda **beyan edilmiş** bir
#: alandır (`wren_service.schema()` yayımlıyor, `uyum.py` ve reçete motoru okuyor) — ama
#: garsonun okuduğu **katalog metninde hiç geçmiyordu**. Garson `toplam_tep` için
#: *«az olan iyidir»*i bilemez; bilemeyince *«kötü»* kelimesi bir yön taşımaz.
#:
#: ⊙ `§M-6`'nın dersinin birebir tekrarı: *mutfak o yemeği yapabiliyorsa menüde de
#: yazmalı; yoksa garson isteyemez ve niteleme cevaptan **sessizce** düşer.* Orada
#: `pencere`/`turev` içindi, burada **yön** için.
#:
#: ⚠ İşaret bilerek **tek karakter** (`↓`): katalog metni her Intent çağrısında
#: gönderiliyor, açıklama cümlesi eklemek token maliyetini ölçü sayısıyla çarpardı.
#: Anlamı istemde **bir kez** yazılır.
_AZ_IYI = "↓"


def cube_satiri(c: dict, *, sozluk: bool) -> str:
    """Tek bir cube'un katalog satırı. `sozluk=False` → **bayt bayt bugünkü biçim**."""
    olculer = list(c.get("measures") or [])
    boyutlar = list(c.get("dimensions") or [])
    zamanlar = list(c.get("time_dimensions") or [])
    if not sozluk:
        line = f'- {c["name"]}: measures[{", ".join(olculer)}]'
        if boyutlar:
            line += f'; dimensions[{", ".join(boyutlar)}]'
        if zamanlar:
            line += f'; time[{", ".join(zamanlar)}]'
        return line

    # 🔴 Sıra önemli: cube adı → cube sinonimleri → ölçüler → boyutlar. Dedup **bu
    # sırayla** ilerler, yani en genel terim en üstte kalır (*"verim"* cube'a yazılır,
    # `ort_oee`'de tekrar edilmez) — model önce konuyu, sonra ayrıntıyı okur.
    gorulen: set[str] = {str(c["name"]).lower()}
    ms = c.get("measure_synonyms") or {}
    # `§W-C` — yön işareti ölçü **adına bitişik**: garson onu ölçüyle birlikte okur.
    _az = set(c.get("lower_is_better") or [])
    line = f'- {c["name"]}{_ek(list(c.get("synonyms") or []), gorulen)}'
    line += (f': measures['
             + ", ".join(m + (_AZ_IYI if m in _az else "") + _ek(ms.get(m), gorulen)
                         for m in olculer) + "]")
    if boyutlar:
        line += f'; dimensions[{", ".join(boyutlar)}]'
    if zamanlar:
        line += f'; time[{", ".join(zamanlar)}]'
    return line


def cok_sahipli_olculer(cubes: list[dict]) -> dict[str, list[str]]:
    """Birden çok küpte tanımlı ölçü adları → sahipleri. **Ölçülür, beyan edilmez.**

    ⊙ Ölçüldü (2026-08-09, boyahane): 127 ölçü adının **9'u** çok sahipli
    (`toplam_fire_kg` · `ilk_seferde_tamam_yuzde` · `bakiye` · `toplam_durus_dakika` …).
    Ve modelin kararsızlığının **tamamı** bu dokuzun etrafında dönüyor.
    """
    from collections import defaultdict

    sahip: dict[str, list[str]] = defaultdict(list)
    for c in (cubes or []):
        for m in (c.get("measures") or []):
            sahip[str(m)].append(str(c.get("name")))
    return {m: v for m, v in sorted(sahip.items()) if len(v) > 1}


def _belirsizlik_bloku(cubes: list[dict]) -> str:
    """🔴🔴 **BELİRSİZLİĞİ MODELE GÖSTER — çünkü seçemediği için değil, belirsiz
    olduğunu BİLMEDİĞİ için savruluyor.**

    Ölçüldü: aynı soru iki kez sorulduğunda üretim yolu (k=3 oylama) **8'de 1**
    farklı `cube_query` üretiyor; ham tek çağrıda **8'de 2**. Sapan soruların hepsi
    çok sahipli bir ölçü içeriyordu. Katalog o güne kadar bu ölçülerin **birden çok
    küpte** olduğunu hiçbir yerde söylemiyordu — model iki geçerli seçenek arasında
    yazı-tura atıyordu ve bunu bilmiyordu bile.

    🔴 **İşaret ölçü adına BİTİŞİK DEĞİL — ve bu bir üslup tercihi değil, ödenmiş bir
    faturadır.** `§CC-D`'de yön işareti (`↓`) ölçü adının yanına yazılmıştı; model onu
    **adın parçası** sandı (`toplam_su_lt↓`) ve beyaz liste her `↓` taşıyan ölçüyü
    reddetti. *Bir metne konan her işaret, o metnin bir parçası olarak okunabilir —
    o yüzden işaretler ayrı bir bölümde durur.*

    ⚠ Bu blok bir **karar vermez**: hangisinin doğru olduğunu söylemez, yalnız
    *«burada bir seçim var»* der. Sahiplik bir **alan kararıdır** ve onu araca
    verdirmek dayatmadır (`r1_envanteri`'nin ölçtüğü ders: karar araca bırakılınca
    korpus %93,2 → %92,6).
    """
    cok = cok_sahipli_olculer(cubes)
    if not cok:
        return ""
    satirlar = "\n".join(f"  {m}: {' | '.join(v)}" for m, v in cok.items())
    return ("\n\n⚠ AYNI ADI TAŞIYAN ÖLÇÜLER (birden çok cube'da tanımlı — hangisini "
            "kastettiğini SORUDAN çıkar, rastgele seçme):\n" + satirlar)


def build_catalog(schema: dict, *, sozluk: bool = False,
                  belirsizlik: bool = False) -> tuple[str, dict]:
    """LLM prompt'u için cube kataloğu metni + doğrulama indeksi.

    ⚠ **İki dönüş, iki farklı sözleşme.** Metin sağlayıcıya gider ve **değişebilir**;
    indeks `parse_cube_query`'nin beyaz listesidir ve `sozluk` bayrağından **etkilenmez**.
    Bayrağın indeksi de değiştirmesi, bir prompt tercihinin doğrulama sınırını oynatması
    olurdu — *bir kapının genişliği, kapıdan geçenin nasıl anlatıldığına bağlı olamaz.*
    """
    from app.sensitivity import prompt_safe_values

    cubes = schema.get("cubes") or []
    cols = {c["name"]: c for m in schema.get("models", []) for c in m["columns"]}
    lines, enum_lines, index = [], [], {}
    for c in cubes:
        index[c["name"]] = c
        lines.append(cube_satiri(c, sozluk=sozluk))
        for dim in c.get("dimensions", []):
            col = cols.get(dim)
            # HASSAS KOLON DEĞERLERİ PROMPT'A GİRMEZ (Faz A1). Süzgeç `llm._schema_prompt`
            # ile AYNI kaynaktan (`app/sensitivity.py`) — eskiden iki prompt üreticisi
            # farklı politika uyguluyordu (burada ≤25 + cube whitelist, orada HER VARCHAR).
            vals = prompt_safe_values(col) if col else []
            if vals and len(vals) <= 25:
                enum_lines.append(f'  {c["name"]}.{dim} ∈ {{{", ".join(map(str, vals))}}}')
    catalog = "\n".join(lines)
    if sozluk and lines:
        catalog = (f"Kullanıcı bu terimleri Türkçe konuşur; {_AC}…{_KAPA} içindekiler "
                   f"AYNI şeyin başka adlarıdır (cevapta teknik adı kullan):\n" + catalog)
    if enum_lines:
        catalog += "\n\nFiltre değerleri (birebir kullan):\n" + "\n".join(enum_lines)
    # ⚠ `KURAL B`: bayrak kapalıyken **tek karakter** eklenmez → istem bayt bayt bugünkü.
    if belirsizlik:
        catalog += _belirsizlik_bloku(cubes)
    return catalog, index


def metin_ve_indeks(schema: dict, principal, settings=None) -> tuple[str, dict]:
    """`build_catalog` + bayrak çözümü — **tek yerde**.

    🔴 Neden bir yardımcı: `catalog_text` dört ayrı çağrı yerinde üretiliyor (planlayıcı ·
    `llm.select_cube` · Intent-JSON · `refine_cube`). Bayrağı dördünde ayrı ayrı çözmek,
    bir gün **üçünde** çözmek demekti — ve o üçüncü yol, sözlüğü göremeyen tek yol olurdu.

    *Bir bayrağı N yerde okumak, N−1 yerde okumaya giden yoldur.*

    ## ⚠ `settings` NEDEN İSTEĞE BAĞLI — kapı bunu yakaladı

    İlk sürüm `settings`'i **zorunlu** aldı ve dört çağrı yerinden **ikisinde o isim
    kapsamda yoktu** (`_prompt_enhance_dene` ve pilot dalı onu parametre almıyor).
    `NameError` çağıranın `except Exception`'ında **yutuldu** ve enhancer sessizce
    *"çözemedim"* demeye başladı — üç kapı kırmızıya döndü.

    🔴 Ders: bir yardımcının imzası, çağıranların **en dar** kapsamına göre çizilir.
    Aksi hâlde yardımcı, kaldırmaya çalıştığı tekrarı bir **bağımlılığa** çevirir.
    Ayarları burada çözmek bir gizleme değil, **sahiplenmedir**: bayrağın nereden
    okunduğu artık tek bir yerde yazılı.
    """
    from app.config import get_settings
    from app.features import resolve_for

    # ⚠ İkisi de `try`'dan ÖNCE bağlanır. Yalnız `try` içinde bağlamak, `except`
    # dalında `UnboundLocalError` demekti — bu oturumda **üçüncü** kez çıkan sınıf
    # (`llm_probe` · `AZAMI_SORGU` · bu). *Koşullu bağlanan bir ad, tanımsız bir addan
    # daha sinsidir: statik olarak var, çalışırken yok.*
    acik = _bel = False
    try:
        _bayraklar = resolve_for(settings or get_settings(), principal)
        acik = "katalog_sozlugu" in _bayraklar
        _bel = "katalog_belirsizlik" in _bayraklar
    except Exception:                                      # noqa: BLE001 — katalog düşmez
        _log.warning("katalog bayrakları çözülemedi → sade katalog", exc_info=True)
    return build_catalog(schema, sozluk=acik, belirsizlik=_bel)


def envanter(schema: dict) -> dict:
    """🔴🔴 `A11`/`B-0` — **KATALOĞUN KAÇ ÖLÇÜSÜ OLDUĞUNUN TEK CEVABI.**

    ## Ölçülen kusur — ve çelişki bir kusur DEĞİLDİ

    Rapor (`§B-0`) üç ayrı sayı buldu: **127** · **132** · **141**. Aynı soruya üç
    cevap, çünkü **üç ayrı soru** tek bir adla anılıyordu:

    | soru | bugünkü cevap |
    |---|---|
    | kaç **benzersiz ölçü adı** var | **127** |
    | kaç **ölçü tanımı** var (aynı ad iki küpte iki tanımdır) | **136** |
    | pack'lerde kaç ölçü **yazılı** (yüklü olmayan küpler dâhil) | daha büyük |

    ⊙ Yani sayılar tutarsız değil, **adsızdı**. Bir envanteri düzeltmenin yolu sayıyı
    değiştirmek değil, **hangi sayı olduğunu söylemektir**.

    ⚠ Bu fonksiyon **çözülmüş şemayı** sayar — yani bu kiracıya **yüklü** olanı. Pack'te
    yazılı olup yüklenmeyen bir küp burada **yoktur** ve olmamalıdır: kullanıcının
    sorabileceği şey yüklü olandır.

    *Sayısı olmayan bir borç kapanamaz; adı olmayan bir sayı ise kapandığını sanır.*
    """
    cubes = schema.get("cubes") or []
    olcu_tanimi = [m for c in cubes for m in (c.get("measures") or [])]
    boyut_tanimi = [d for c in cubes for d in (c.get("dimensions") or [])]
    cok_sahipli = cok_sahipli_olculer(cubes)
    yon_beyanli = {m for c in cubes for m in (c.get("lower_is_better") or [])}
    zamansiz = [c["name"] for c in cubes if not (c.get("time_dimensions") or [])]
    return {
        "kup": len(cubes),
        "olcu_tanimi": len(olcu_tanimi),
        "benzersiz_olcu": len(set(olcu_tanimi)),
        "cok_sahipli_olcu": len(cok_sahipli),
        "cok_sahipli_adlar": sorted(cok_sahipli),
        "boyut_tanimi": len(boyut_tanimi),
        "benzersiz_boyut": len(set(boyut_tanimi)),
        "yon_beyanli_olcu": len(yon_beyanli),
        "yon_beyansiz_olcu": len(set(olcu_tanimi)) - len(yon_beyanli & set(olcu_tanimi)),
        "zaman_ekseni_olmayan_kup": zamansiz,
    }
