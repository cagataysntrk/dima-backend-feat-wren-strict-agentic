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
