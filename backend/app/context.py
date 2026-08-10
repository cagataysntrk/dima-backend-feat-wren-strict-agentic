"""BAĞLAM ÇÖZÜCÜ — sunucu tarafında, deterministik, GEREKÇELİ (Faz G5).

## Ölçülen durum (2 Ağustos 2026)

    ask.py:  structural_followup = bool(body.cube_query)
             raw_followup        = bool(prev_sql) and bool(history) and not structural
             is_followup         = structural or raw
             ... seal(..., thread_id=body.thread_id, reply_to_label=body.reply_to_label,
                          is_new_topic=not is_followup)

`thread_id` ve `reply_to_label` **salt echo**: sunucu onları alır ve aynen geri verir.
`is_new_topic` yalnız `not is_followup`'tan türeyen bir boolean. Yani **sunucunun bir bağlam
modeli YOKTU** — hangi soru hangi bağlama ait, sunucu bilmiyordu, istemciye güveniyordu.

Agentic (F) ve konuşma (G) katmanlarının ikisi de bunun üstüne oturacağı için burası
**taşıyıcı kolondur**.

## Korunan değişmez (kayıtlı karar, tartışmaya kapalı)

> **Thread bir UI GRUPLAMASIDIR, SEMANTİK SINIR DEĞİLDİR.**

Bir thread cube/bağlam sınırı taşımaz; yeni thread **yalnız açık kullanıcı eylemiyle**
doğar. Sunucu bir soruyu *"yeni konu"* ilan ederek bağlamı **sessizce koparamaz**. Bu modül
`taze` bir bağlam döndürebilir ama bunu **her zaman bir kuralla gerekçelendirir** ve o
gerekçe makbuza yazılır — *"neden bu sayı?"* sorusunun yanında *"neden bu bağlam?"* da
cevaplanabilir olur.

## "Kanıtlı olmalı" — somut karşılığı üç şey

1. **Gerekçe makbuza yazılır** (`kural` + `resolved_context` → `contract_log.provenance_json`).
2. **Saf fonksiyon, izole test edilebilir.** Bugüne kadar bu mantık `ask()` closure'larının
   içindeydi ve **test edilemezdi** — 1180 satırlık bir fonksiyonun içinden bir kararı
   ayıklayamazsın.
3. **Çok turlu altın senaryolar** (`lab/nl_corpus.py::gen_processes`) bağlam sürekliliğini
   ölçebilir hale gelir: kaç turda doğru çapaya bağlandı, kaç turda sessizce koptu.

## Neden LLM YOK

Bağlam çözümü bir anlama işi değil bir **muhasebe** işidir: hangi çapa verildi, hangi sorgu
taşındı, hangi eksen zaten kullanıldı. LLM'e verilseydi aynı girdi farklı turlarda farklı
bağlama bağlanabilirdi ve *"kanıtlı"* iddiası çökerdi.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# --- KURALLAR (adlandırılmış, sıralı) --------------------------------------------
# Ad string'dir çünkü makbuza yazılır ve DIŞARIDAN okunur (denetçi, destek, altın vaka).
# Sıra ÖNEMLİDİR: yukarıdaki kural aşağıdakini ezer ve bu öncelik açıkça test edilir.
KURAL_CAPA = "capa:karta-yanit"          # kullanıcı belirli bir karta yanıt verdi
KURAL_COKLU = "capa:coklu-kesisim"       # birden çok kart seçildi, kesişim kuruldu
KURAL_CELISKI = "capa:coklu-celiski"     # birden çok kart seçildi, ÇELİŞİYOR → SOR
KURAL_YAPISAL = "yapisal:cube_query"     # istemci açık cube_query taşıdı
KURAL_HAM = "ham:onceki-sql"             # ham-SQL takibi (Discovery zinciri)
KURAL_TAZE = "taze:capa-yok"             # hiçbir çapa yok — yeni soru
#: 🔴 `G2` — bir önceki tur bir YUVA SORDU ve bu tur onun CEVABI. Yeni bir soru değil.
#: Ölçülen kusur: netleştirme dalları `cube_query=None` döndürdüğü için kullanıcının
#: *"geçen ay"* cevabı `KURAL_TAZE`'ye düşüyor ve tur **sıfırdan** koşuyordu.
KURAL_DEVAM = "devam:bekleyen-yanit"
# FAZ E — kullanıcı ÖNCEKİ TURUN METNİNE işaret etti ("az önce dediğin gibi…",
# "yukarıdaki raporu…"). Yapısal bağlam (cube_query) YOK ama çapa **ham ifadededir**.
KURAL_ATIF = "atif:onceki-tur"


@dataclass(frozen=True)
class Baglam:
    """Çözülmüş bağlam + **GEREKÇESİ**. Gerekçesiz bağlam bir tahmindir."""

    kural: str
    cube_query: dict[str, Any] | None = None
    kok_makbuz: str | None = None
    capa_etiketi: str | None = None
    # Bu bağlamda ZATEN kullanılmış gezinme eksenleri (boyutlar + zaman granülerliği).
    # "Peki ya makine bazında?" sorusunda aynı ekseni ikinci kez önermemek için.
    kullanilmis_eksenler: tuple[str, ...] = ()
    # Çelişkide SORULACAK adaylar. Boş değilse çağıran **sormalı**, seçmemeli.
    adaylar: tuple[dict[str, Any], ...] = ()
    # FAZ E — SON İKİ TURUN HAM METNİ. Neden bir alan, neden İKİ tur:
    #
    # Ölçüldü: `history` sunucuya geliyordu ama **yalnız boolean olarak** okunuyordu
    # (`prev_sql and history` → KURAL_HAM). İçeriğine hiç bakılmıyordu; sonuç, atıflı bir
    # takip mesajının ham SQL üretmesiydi (`source=rule`) — kullanıcının işaret ettiği
    # rapor DEĞİL, uydurulmuş bir sorgu.
    #
    # Pencere **iki turdur** ve bu bir sınır değil bir KARAR: üç ve üzeri tur, "hangi tur
    # kastedildi" sorusunu doğurur ve o soru bir **retrieval** problemidir. Raporun kendi
    # ölçümü retrieval'ı reddetti (+14/−16) ve bu modülün kuralı da açık: bağlam çözümü
    # bir anlama değil bir **muhasebe** işidir. İki tur, muhasebeyle çözülebilen en geniş
    # penceredir: "az önce" ve "ondan önceki".
    ham_ifade: tuple[str, ...] = ()
    notlar: str = ""

    @property
    def celiskili(self) -> bool:
        return self.kural == KURAL_CELISKI

    @property
    def taze(self) -> bool:
        return self.kural == KURAL_TAZE

    def makbuza(self) -> dict[str, Any]:
        """Makbuza yazılacak biçim — `contract_log.provenance_json` içine gömülür.

        Ayrı bir kolon AÇILMADI: `provenance_json` zaten *"bu cevap nereden geldi"*
        sorusunun kaydıdır ve köken (hangi join) ile bağlam (hangi çapa) o sorunun iki
        yüzüdür. İkinci bir kolon, iki yarısı ayrı yerlerde duran bir kanıt üretirdi.
        """
        return {
            "context_rule": self.kural,
            "resolved_context": {
                "cube": (self.cube_query or {}).get("cube"),
                "root_contract": self.kok_makbuz,
                "anchor": self.capa_etiketi,
                "used_axes": list(self.kullanilmis_eksenler),
                "candidates": len(self.adaylar),
                # Ham pencere makbuza YAZILIR: *"neden bu bağlam?"* sorusunun cevabı
                # atıf yolunda METİNDİR, bir cube_query değil. Yazılmasaydı o yolla
                # üretilen her cevap gerekçesiz kalırdı.
                "raw_window": list(self.ham_ifade),
            },
        }


def _eksenler(cq: dict | None) -> tuple[str, ...]:
    """Bir sorgunun KULLANILMIŞ gezinme eksenleri: boyutlar + zaman granülerliği."""
    if not cq:
        return ()
    eksen = list(cq.get("dimensions") or [])
    for td in cq.get("timeDimensions") or []:
        if isinstance(td, dict) and td.get("granularity"):
            eksen.append(f"{td.get('dimension', 'tarih')}__{td['granularity']}")
    return tuple(dict.fromkeys(eksen))


def _uyumlu(a: dict, b: dict) -> bool:
    """İki bağlam KESİŞTİRİLEBİLİR mi? Aynı cube ise evet.

    Farklı cube'lar birleştirilemez: cube'lar farklı **grain**lerdir ve iki grain'i
    sessizce birleştirmek fan-out'un diyalog seviyesindeki karşılığı olurdu — sayı
    değişir, kimse fark etmez.
    """
    return (a or {}).get("cube") == (b or {}).get("cube")


def _kesistir(cqs: list[dict]) -> dict:
    """Aynı cube'daki birden çok bağlamın kesişimi: ORTAK ölçüler + ortak boyutlar.

    Birleşim DEĞİL kesişim: kullanıcı iki karta işaret ettiğinde *"ikisinde de olan"*
    demek istiyordur. Birleşim alsaydık, seçilmemiş bir ölçü sessizce rapora girerdi.
    """
    ilk = cqs[0]
    ortak_m = [m for m in (ilk.get("measures") or [])
               if all(m in (c.get("measures") or []) for c in cqs[1:])]
    ortak_d = [d for d in (ilk.get("dimensions") or [])
               if all(d in (c.get("dimensions") or []) for c in cqs[1:])]
    return {**ilk, "measures": ortak_m, "dimensions": ortak_d}


def coz(
    *,
    cube_query: dict | None = None,
    prev_sql: str | None = None,
    history: list[str] | None = None,
    capalar: list[dict] | None = None,
    capa_etiketi: str | None = None,
    kok_makbuz: str | None = None,
    atif: bool = False,
    diyalog_durumu: dict | None = None,
) -> Baglam:
    """Bağlamı çözer ve **gerekçesini** birlikte döndürür. Saf fonksiyon — I/O yok.

    `capalar`: kullanıcının işaret ettiği kart(lar)ın `cube_query`'leri (çoklu seçim).
    Tek eleman → o karta yanıt. Birden çok → **kesişim**, çelişkide **SOR**.

    Öncelik sırası bilinçlidir ve test edilir: kullanıcının AÇIK eylemi (çapa) her zaman
    istemcinin taşıdığı örtük duruma (cube_query) baskın gelir. Aksi halde bir karta
    yanıt verirken en son raporun bağlamına kayardık — kullanıcının işaret ettiği yer
    ile cevabın bağlandığı yer ayrışırdı ve bu **sessizce** olurdu.
    """
    capalar = [c for c in (capalar or []) if c]
    # İKİ TURLUK PENCERE — her dalda taşınır (çapa dalında da: makbuz *"kullanıcı hangi
    # cümlelerin üstünde konuşuyordu"* sorusunu her yolda cevaplayabilmeli).
    pencere = tuple(x for x in (history or [])[-2:] if x)
    if len(capalar) == 1:
        return Baglam(kural=KURAL_CAPA, cube_query=capalar[0], kok_makbuz=kok_makbuz,
                      capa_etiketi=capa_etiketi, ham_ifade=pencere,
                      kullanilmis_eksenler=_eksenler(capalar[0]))
    if len(capalar) > 1:
        ilk = capalar[0]
        if all(_uyumlu(ilk, c) for c in capalar[1:]):
            birlesik = _kesistir(capalar)
            return Baglam(kural=KURAL_COKLU, cube_query=birlesik, kok_makbuz=kok_makbuz,
                          capa_etiketi=capa_etiketi, ham_ifade=pencere,
                          kullanilmis_eksenler=_eksenler(birlesik),
                          notlar=f"{len(capalar)} kart kesiştirildi")
        # ÇELİŞKİ: farklı cube'lar. SESSİZCE BİRİNİ SEÇME — bu, Faz 3.1'in cube-beraberlik
        # chip'inin diyalog seviyesindeki karşılığıdır (ADR-0008: belirsizlikte SOR).
        return Baglam(kural=KURAL_CELISKI, adaylar=tuple(capalar), kok_makbuz=kok_makbuz,
                      capa_etiketi=capa_etiketi, ham_ifade=pencere,
                      notlar="seçilen kartlar farklı cube'lara ait — birleştirilemez")
    # 🔴 `G2` — DEVAM. Yapısal bağlamdan ÖNCE gelmez (istemci `cube_query` yolluyorsa o
    # daha güçlü bir sinyaldir) ama `KURAL_TAZE`'den **önce** gelir: bekleyen bir soruya
    # verilen cevap, yeni bir soru DEĞİLDİR.
    if not cube_query:
        from app.diyalog import devam_edilebilir

        if (kismi := devam_edilebilir(diyalog_durumu)) is not None:
            return Baglam(kural=KURAL_DEVAM, cube_query=kismi, kok_makbuz=kok_makbuz,
                          ham_ifade=pencere, kullanilmis_eksenler=_eksenler(kismi),
                          notlar="bekleyen yuvaya cevap — özgün niyet KORUNDU")
    if cube_query:
        return Baglam(kural=KURAL_YAPISAL, cube_query=cube_query, kok_makbuz=kok_makbuz,
                      ham_ifade=pencere,
                      kullanilmis_eksenler=_eksenler(cube_query))
    # ATIF (Faz E) — yapısal bağlam yok ama kullanıcı ÖNCEKİ TURUN METNİNE işaret etti.
    # HAM'dan ÖNCE gelir: ham-SQL zinciri *"bağlam yok"* der ve çağıranı Discovery'ye
    # bırakır; atıf ise *"bağlam VAR, ham ifadededir"* der ve çağıran onu deterministik
    # olarak yeniden çözebilir. Ölçüldü: atıf HAM'a düştüğünde uydurma SQL üretiliyordu.
    if atif and pencere:
        return Baglam(kural=KURAL_ATIF, kok_makbuz=kok_makbuz, ham_ifade=pencere,
                      notlar="çapa ham ifadede — önceki turun metni yeniden çözülmeli")
    if prev_sql and history:
        return Baglam(kural=KURAL_HAM, kok_makbuz=kok_makbuz, ham_ifade=pencere,
                      notlar="ham-SQL zinciri — yapısal bağlam YOK, cube_query taşınmıyor")
    return Baglam(kural=KURAL_TAZE, ham_ifade=pencere)


# --- Bağlam SÜREKLİLİĞİ ölçümü (G5'in "kanıtlı" iddiasının sayısal karşılığı) -----

@dataclass
class SureklilikOlcumu:
    """Çok turlu bir senaryoda bağlamın kaç turda korunduğu / koptuğu.

    `lab/nl_corpus.py::gen_processes` 3/5/10 adımlı süreçler üretiyor ama bugüne kadar
    yalnız **tur başına doğruluk** ölçüyordu. Bağlam sürekliliği ayrı bir sorudur:
    *"doğru cevabı verdi ama doğru şeyin devamı mıydı?"*
    """

    toplam: int = 0
    korunan: int = 0
    kopan: int = 0
    kurallar: dict[str, int] = field(default_factory=dict)

    def kaydet(self, b: Baglam, *, takip_bekleniyordu: bool) -> None:
        self.toplam += 1
        self.kurallar[b.kural] = self.kurallar.get(b.kural, 0) + 1
        if not takip_bekleniyordu:
            return
        # Takip bekleniyorken TAZE dönmek = bağlam SESSİZCE koptu.
        if b.taze:
            self.kopan += 1
        else:
            self.korunan += 1

    @property
    def oran(self) -> float | None:
        """Korunma oranı; hiç takip turu yoksa `None` — 0.0 DEĞİL.

        `0.0` *"hep koptu"* demektir; `None` *"bu soru sorulamaz"*. Aynı ayrım
        `app/stats.py::z_skorlari`'nda da var ve aynı nedenle: ölçülemeyeni kötü
        göstermek, ölçmemekten daha yanıltıcıdır.
        """
        n = self.korunan + self.kopan
        return (self.korunan / n) if n else None


def capa_degerleri(cube_query: dict | None, schema: dict | None) -> frozenset[str] | None:
    """🔴 Ekrandaki raporun **satır etiketleri** — bir takip sorusunun çapası.

    ## Neden burada

    *"Yıkama neden yüksek"*i eldeki cevaba bağlayan şey `yıkama`'nın **mevcut raporun
    kırılım değerlerinden biri** olmasıdır — zamirden **güçlü** bir bağ, çünkü zamir
    *"şu"* der, değer **hangisi** olduğunu söyler.

    ⚠ `followup.sinifla` bir **sınıflandırıcıdır**; katalog/sonuç okumak onun işi değil
    (`KAT-1`). *"Ekranda ne var"* sorusunun sahibi **bağlam katmanıdır** ve burası odur.

    🔴 Uydurma yok: kaynak yalnız `previous_result`'ın satırları. Rapor yoksa `None` ve
    çağıran bugünkü davranışına döner (`KURAL B`).

    ⚠ İlk 200 satır: bir kırılım daha uzunsa etiketleri bir **takip zamiri** gibi
    kullanılamaz zaten (kullanıcı 500. satırı adıyla anmaz), ve tarama maliyeti
    sınırsız olamaz.
    """
    # 🔴 **KAYNAK: KATALOG, ekran DEĞİL — ve bu bir düzeltmenin kaydı.**
    #
    # İlk yazım `previous_result`'ın satırlarını okuyordu. Curl ile doğrulandı ve
    # **çalışmadı**: `AskRequest`'te öyle bir alan **yok** — istemci satırları hiç
    # göndermiyor. Yani okuduğum şey her zaman `None`du.
    #
    # ⊙ Doğru kaynak zaten elde: kataloğun `dimension_values`'ı (`value_index` de onu
    # okuyor). Ve **daha iyi**: kullanıcı ikinci sayfadaki bir satırı da adıyla anabilir;
    # ekran görünenle sınırlıdır, katalog değil.
    #
    # *Var olmayan bir alanı okuyan kod, sessizce hiçbir şey yapar — ve testi geçer.*
    from app import cube_router as cr

    dims = {str(d) for d in ((cube_query or {}).get("dimensions") or [])}
    cube = (cube_query or {}).get("cube")
    if not dims or not cube:
        return None
    out: set[str] = set()
    for c in (schema or {}).get("cubes") or []:
        if c.get("name") != cube:
            continue
        for ad, degerler in (c.get("dimension_values") or {}).items():
            if ad in dims:
                out |= {cr._norm(str(v)) for v in (degerler or []) if str(v).strip()}
    # ⚠ En az üç harf: kısa bir değer (`A`, `12`) cümlenin ortasında tesadüfen geçer ve
    # alakasız bir soruyu takip sanardık. *Bir bağ, tesadüfen kurulabiliyorsa bağ değildir.*
    return frozenset(x for x in out if len(x) >= 3) or None


def sinif_ipuclari(cube_query: dict | None,
                   schema: dict | None) -> tuple[frozenset[str] | None, frozenset[str] | None]:
    """🔴 **SINIFLANDIRICININ EKRANDAN İSTEDİĞİ HER ŞEY — tek çağrı, tek sahip.**

    Döner: `(çapa_değerleri, açık_boyutlar)` — *«ekranda hangi satırlar var»* ve
    *«ekranda hangi boyut YOK»*.

    ⚠ İkisini tek çağrıya toplamak bir kolaylık değil bir **sınır** kararıdır: ikisi de
    aynı soruyu (*«ekranda ne var»*) farklı yönden sorar ve `followup.sinifla`'nın tek
    bir bağlam görüntüsü görmesi gerekir. Ayrı çağrılarda biri düşüp öteki dursaydı
    sınıflandırıcı **yarım bir ekran** üstünde karar verirdi.

    ⚠ Ve `ask()`'in büyüme kapısı bunu ayrıca istedi: iki ayrı `try/except` orada
    **altı kod satırıydı**; karar burada, çağrı orada. *Bir cevabın bağlamını kuran yer,
    onu kuran TEK yer olmalıdır* (`bos_sonuc_notu`'nun aynı gerekçesi).

    ⚠ **Best-effort:** okunamayan taraf `None` döner ve o eksen bugünkü davranışına
    düşer (`KURAL B`) — sınıflandırma **düşmez**.
    """
    from app.logging_setup import get_logger

    log = get_logger("dima.ask")
    try:
        capa = capa_degerleri(cube_query, schema)
    except Exception:                                  # noqa: BLE001 — sınıflandırma düşmez
        capa = None
        log.warning("çapa değerleri okunamadı (best-effort)", exc_info=True)
    try:
        acik = acik_boyutlar(cube_query, schema)
    except Exception:                                  # noqa: BLE001 — sınıflandırma düşmez
        acik = None
        log.warning("açık boyutlar okunamadı (best-effort)", exc_info=True)
    return capa, acik


def acik_boyutlar(cube_query: dict | None, schema: dict | None) -> frozenset[str] | None:
    """🔴🔴 `§NÇ` — **EKRANDA OLMAYAN BİR BOYUTU ANMAK, «NEDEN» SORMAK DEĞİLDİR.**

    Mevcut küpün, **raporda henüz bulunmayan** boyut adları (+ sinonimleri).

    ## Ölçülen kusur (curl `N` turu, 2026-08-10 · beş turluk thread)

        tur 1  «bu yıl duruş nedenleri»              → tek toplam
        tur 3  «en büyük **nedeni** hangi makinede»
               → sınıf: TUR_NEDEN  → **katkı analizi** koştu
               → cevap: «duruş nedeni X — 46.524 dk AZALDI (net değişimin %83,6'sı)»

    Kullanıcı *«hangi makinede»* diye sordu; sistem *«hangi neden ne kadar değişti»*
    diye cevapladı. **Başka bir sorunun** doğru cevabı.

    🔴 Kök: Türkçede `neden` iki ayrı kelimedir — **soru zarfı** (*«neden düştü?»*) ve
    **isim** (*«duruşun nedeni»*). `_syn_hit` ek zincirini takip eder ve `nedeni`yi
    `neden`e bağlar; ikisi ayrılamaz hâle gelir.

    ## Neden çözüm bir kelime kuralı DEĞİL

    `-i` ekini yasaklamak `«bu farkın sebebini aç»`ı da kırardı — o **gerçek** bir
    *neden* takibidir. Ayrım ekte değil, sorunun **neye** işaret ettiğinde:

    > Bir *«neden»* takibi **eldeki cevabı** açıklar. Soru, o cevapta **bulunmayan** bir
    > boyutu anıyorsa, açıklanacak şey ekranda yoktur — yeni satırlar isteniyordur.

    ⊙ Bu yüklem **katalogdan** okunur, sözlükten değil: hangi boyutların var olduğunu ve
    hangilerinin raporda bulunduğunu küp söyler. Yani ADR-0008'in yasakladığı sınıfa
    girmez — bu bir dil kuralı değil, bir **kapsam karşılaştırmasıdır**.

    ⚠ Sahibi **bağlam katmanıdır**, sınıflandırıcı değil (`KAT-1`) — `capa_degerleri`
    ile birebir aynı gerekçe ve birebir aynı kalıp. Sınıflandırıcı yalnız tüketir.

    ⚠ Raporda **zaten olan** boyutlar dışarıda: *«makine bazında bak — makine neden
    kötü»* gerçek bir açıklama isteğidir ve bozulmamalıdır.

    *Bir cevabın üstünde konuşmak, o cevabın içinde olan şeyler hakkında konuşmaktır.*
    """
    from app import cube_router as cr

    cube = (cube_query or {}).get("cube")
    if not cube:
        return None
    mevcut = {str(d) for d in ((cube_query or {}).get("dimensions") or [])}
    mevcut |= {str(t.get("dimension")) for t in ((cube_query or {}).get("timeDimensions") or [])
               if isinstance(t, dict)}
    out: set[str] = set()
    for c in (schema or {}).get("cubes") or []:
        if c.get("name") != cube:
            continue
        sinonimler = c.get("dimension_synonyms") or {}
        for ad in (c.get("dimensions") or []):
            if str(ad) in mevcut:
                continue
            out.add(cr._norm(str(ad)))
            out |= {cr._norm(str(s)) for s in (sinonimler.get(ad) or [])}
    # ⚠ `capa_degerleri` ile aynı üç-harf disiplini: kısa bir ad cümlede tesadüfen geçer.
    return frozenset(x for x in out if len(x) >= 3) or None
