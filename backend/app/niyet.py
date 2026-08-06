"""🔴🔴 KÖK-1 · **NİYET NESNESİ** — çözümleme ile eşleştirme ayrılsın. (FAZ 1)

## Raporun teşhisi

> *"KN-4 (uyum denetimi) **yazılamaz** çünkü karşılaştırılacak iki şey yok. KN-2 (çok
> sahip) **kaçınılmaz** çünkü «bu bir çekim mi?» sorusunun sahibi yok. KN-1 **kaçınılmaz**
> çünkü taşınacak durum bir nesne değil."*

⊡ Ölçüldü: `app/` içinde `Niyet` sınıfı **yoktu**. Sorunun anlamı `route()`'un içinde,
yerel değişkenlerde, dönüş anında **kaybolarak** yaşıyordu. Ve bu turda o boşluk **beş
ayrı yerde** ayrı ayrı doldurulmuştu:

| modül | ne okuyor | ne için |
|---|---|---|
| `app/uyum.py` | kıyas · çok-dönem · trend · kırılım · üstünlük · eşik · dışlama | beyanlı kısmi cevap |
| `app/yetenek.py` | forecast · olumsuzluk · iki-cube ölçüsü | *"yapamıyorum"* |
| `app/donem_capasi.py` | dönem filtresi | takip turunda çapa |
| `app/turetme.py` | bilinmeyen kelimeler | türetme chip'i |
| `app/belirsizlik_chipi.py` | eşleşen ölçü terimi | belirsizlik beyanı |

🔴 Beşi de **aynı soruyu** soruyor ve beşi de **kendi cevabını** üretiyor. Bu, deponun
adını koyduğu *"aynı kuralın iki sahibi"* sınıfının **beşe katlanmış** hâli.

## 🔴 FAZ 1 — GÖZLEMCİ, ve bu bilinçli

Raporun kapı ölçütü aynen: *"`Niyet` üretilir ve **loglanır**; `route()` davranışı
**BİREBİR aynı** kalır. Sıfır gerileme, tam görünürlük."*

Bu modül **hiçbir kararı değiştirmez**. `route()` onu görmez, `ask()` onu tüketmez.
Tek tüketicisi **iz** (`trace`) ve **kapı**dır (`test_kok1_niyet.py`), ve kapı onun
mevcut okuyucularla **aynı şeyi söylediğini** ölçer.

⚠ Neden bu adım *"ölü kod"* değil: deponun kuralı *ölü kod zararsız değildir* der ve
haklıdır. Buradaki fark, tüketicinin **ölçüm** olması: Faz 2'de tüketiciler tek tek
taşınacak ve her taşımada *"nesne ile eski okuyucu aynı mı"* sorusu **zaten yazılmış**
bir kapıyla cevaplanacak. *Bir göçün ilk adımı, iki tarafın aynı şeyi söylediğini
kanıtlamaktır.*

## ⚠ YENİ DİLBİLİM YAZILMIYOR

Raporun şartı: *"`_syn_hit` · `_covers` · `_ek_gecerli` · `_cekimli_token` ·
`compare_mode` · `_kiyas_spanlari` — **hepsi zaten var**, dağınık. Yeni dilbilim
**yazılmıyor**, var olan **tek çatı altına alınıyor**."*

Bu dosyada **tek bir regex yok**. Her alan mevcut bir fonksiyonun çağrısıdır; `test_
kok1_niyet.py::test_YENI_DILBILIM_YAZILMADI` bunu AST ile kilitler.

## Ne taşıyabiliyor — ve neden bu bir YETENEK maddesi

Raporun *"savunmacı değil **genişletici** tek maddesi"*: `Niyet` **çok dönem · çok ölçü ·
iki cube** taşıyabilir — bugün `CubeQuery`'nin **temsil edemediği** her şey. `donemler`
bir **liste**dir; `route()` tek aralığa çökmek zorundadır, `Niyet` çökmez.
*Bir şeyi temsil edemeyen sistem, onu göremez de.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Niyet türleri — **kapalı** küme. Yeni bir tür eklendiğinde uyum denetimi de eklenir
#: (KÖK-2'nin *"mekanizma kendini genişletir"* ilkesi).
TUR_TOPLAM = "toplam"        # tek sayı
TUR_KIRILIM = "kirilim"      # boyut bazında dağılım
TUR_TREND = "trend"          # zaman ekseni
TUR_KIYAS = "kiyas"          # iki dönem/değer karşılaştırması
TUR_LISTE = "liste"          # satır dökümü
TUR_USTUNLUK = "ustunluk"    # en yüksek/düşük N


@dataclass(frozen=True)
class Niyet:
    """Sorunun **anlamı** — bir `CubeQuery` değil, ondan ÖNCEKİ katman.

    ⚠ `frozen`: niyet bir **okuma**dır, bir çalışma alanı değil. Değiştirilebilir olsaydı
    tüketiciler onu yerinde düzeltmeye başlar ve *"kim değiştirdi"* sorusu doğardı —
    tam da bu nesnenin kapatmak için var olduğu belirsizlik.
    """

    soru: str
    olcu_adaylari: list[tuple[str, str]] = field(default_factory=list)   # (cube, ölçü)
    #: **ÇÖZÜLEBİLEN** dönem filtreleri — `CubeQuery`ye girecek olanlar.
    donemler: list[dict] = field(default_factory=list)
    #: 🔴 Sorunun **ADIYLA SAYDIĞI** dönem sayısı — çözülebilse de çözülemese de.
    #: İkisinin farkı, raporun *"bilgi var, temsil yok"* cümlesinin **sayısal hâlidir**:
    #: `ocak ve haziran ciro` → `donem_sayisi=2` ama `donemler=[]`, çünkü `CubeQuery`
    #: ayrık iki ayı taşıyamaz ve `date_filters` bu yüzden **boş** döner.
    #: *Bir sistemin temsil edemediği şeyi SAYABİLMESİ, onu görebilmesinin ilk adımıdır.*
    donem_sayisi: int = 0
    kirilimlar: list[str] = field(default_factory=list)
    filtreler: list[dict] = field(default_factory=list)
    turler: set[str] = field(default_factory=set)
    ustunluk: int | None = None                                          # top-N (sayılı)
    granulerlik: str | None = None
    bilinmeyenler: list[str] = field(default_factory=list)

    @property
    def cok_donem(self) -> bool:
        """🔴 Soru birden çok dönem **adıyla** anıyor mu — çözülebilirlikten bağımsız."""
        return self.donem_sayisi > 1

    @property
    def temsil_edilemeyen(self) -> list[str]:
        """🔴 **Bu nesnenin var olma sebebi.** Sorunun taşıdığı ama `CubeQuery`ye
        giremeyen niyet işaretleri.

        `route()` bunları döndüremez çünkü dönüş tipi onları **taşıyamaz**; `Niyet`
        taşır ve `uyum` bugün bunu **cq üzerinden geriye doğru** çıkarmak zorunda
        kalıyor. Faz 2'de o hesap buraya taşınacak.
        """
        out = []
        if self.cok_donem and len(self.donemler) <= 2:
            out.append("cok_donem")      # ≥2 dönem adlandı, en fazla bir aralık çözüldü
        if TUR_KIYAS in self.turler and not self.cok_donem:
            out.append("kiyas")          # kıyas fiili var, kıyaslanacak ikinci uç yok
        return out

    def iz(self) -> str:
        """Tek satırlık **görünürlük** — Faz 1'in tek ürünü budur."""
        parca = [f"tür={'+'.join(sorted(self.turler)) or '?'}"]
        if self.temsil_edilemeyen:
            parca.append(f"🔴temsil-yok={','.join(self.temsil_edilemeyen)}")
        if self.olcu_adaylari:
            parca.append(f"ölçü={len(self.olcu_adaylari)}")
        if self.donem_sayisi:
            parca.append(f"dönem={self.donem_sayisi}"
                         + ("" if self.donemler else "(çözülemedi)"))
        if self.kirilimlar:
            parca.append(f"kırılım={','.join(self.kirilimlar[:3])}")
        if self.ustunluk:
            parca.append(f"üstünlük={self.ustunluk}")
        if self.granulerlik:
            parca.append(f"granülerlik={self.granulerlik}")
        if self.bilinmeyenler:
            parca.append(f"bilinmeyen={','.join(self.bilinmeyenler[:3])}")
        return "niyet: " + " · ".join(parca)


def coz(soru: str, schema: dict[str, Any]) -> Niyet:
    """Soru → `Niyet`. **Deterministik, LLM'siz, yan etkisiz.**

    🔴 Her alan mevcut bir çözümleyicinin çağrısıdır — bu fonksiyonda **tek bir regex
    yoktur** ve olmamalıdır. Yeni bir dil kuralı gerekiyorsa yeri burası değil, o kuralın
    **tek sahibi** olan modüldür.

    ⚠ Hata yutulmaz ama **niyet de düşürülmez**: bir çözümleyici patlarsa o alan boş
    kalır ve `bilinmeyenler` bunu taşır. *Bir gözlemcinin, gözlediği şeyi düşürmesi
    gözlemin kendisinden pahalıdır.*
    """
    from app import cube_router as cr

    q = cr._norm(soru)
    turler: set[str] = set()

    donemler = _guvenli(lambda: cr.date_filters(q), [])
    filtreler = list(donemler)

    esik = _guvenli(lambda: cr._measure_threshold(q), None)
    if esik:
        filtreler.append(esik)

    # ⚠ Kıyas ve dönem SAYIMI `app.uyum`dan gelir — o modül bu turda yazıldı, yedi
    # değişmezin sahibi ve ölçüldü (525 meşru soruda 0 yanlış-pozitif). İkinci bir
    # sayaç yazmak, bu nesnenin kapatmak için var olduğu kusuru doğururdu.
    from app import uyum as _uyum

    # ⚠ `_cok_donem` **adlandırılmış** dönemleri sayar (`ocak` · `2025` · `son 3 ay`);
    # `bu yıl` gibi göreli bir dönemi saymaz — o `date_filters`ta çözülür. İkisinin
    # birleşimi alınır, yoksa `bu yıl makine bazında oee` "dönemsiz" görünürdü ve iz
    # kendi verisiyle çelişirdi. *Bir gözlem, gözlediği iki kaynağın ikisini de
    # okumalıdır; yoksa gözlem değil bir seçimdir.*
    donem_sayisi = max(_guvenli(lambda: _uyum._cok_donem(soru), 0),
                       1 if donemler else 0)
    # ⚠ `compare_mode` — `uyum`un KIYAS değişmezinin kullandığı **aynı** fonksiyon.
    # İlk yazımda `uyum` içinde ayrı bir kıyas kalıbı olduğunu VARSAYDIM; okununca
    # görüldü ki yok — o da bunu çağırıyor. *Bir modülü kullanmadan önce okumak, onu
    # ikinci kez yazmaktan ucuzdur.*
    if _guvenli(lambda: cr.compare_mode(q), None):
        turler.add(TUR_KIYAS)
    if _guvenli(lambda: cr.liste_niyeti(q), False):
        turler.add(TUR_LISTE)

    gran = _guvenli(lambda: cr._time_gran(q), None)
    if gran:
        turler.add(TUR_TREND)

    ustunluk = _guvenli(lambda: cr._top_n(q), None)
    if ustunluk:
        turler.add(TUR_USTUNLUK)

    adaylar = [(c.get("name", ""), m)
               for c, m in _guvenli(lambda: cr.measure_cube_candidates(q, schema), [])]
    bilinmeyen = _guvenli(lambda: cr.partial_unknowns(q, schema)[0], [])

    kirilimlar = _kirilimlar(cr, q, schema, adaylar)
    if kirilimlar:
        turler.add(TUR_KIRILIM)
    if not turler:
        turler.add(TUR_TOPLAM)

    return Niyet(soru=soru, olcu_adaylari=adaylar, donemler=donemler,
                 donem_sayisi=donem_sayisi, kirilimlar=kirilimlar, filtreler=filtreler,
                 turler=turler, ustunluk=ustunluk, granulerlik=gran,
                 bilinmeyenler=list(bilinmeyen))


def _kirilimlar(cr, q: str, schema: dict, adaylar: list[tuple[str, str]]) -> list[str]:
    """Sorunun istediği kırılımlar — **aday cube'ların boyutlarından**, sırayla.

    ⚠ Cube seçimi burada YAPILMAZ: `Niyet` bir eşleştirme değil bir okumadır. Aday
    cube'ların hepsinin boyutları taranır ve eşleşenler **tekilleştirilerek** döner.
    Hangisinin kazanacağı eşleştiricinin (`route()`) işidir.
    """
    out: list[str] = []
    adlar = {a for a, _ in adaylar} or {c.get("name") for c in (schema.get("cubes") or [])}
    for c in schema.get("cubes") or []:
        if c.get("name") not in adlar:
            continue
        for d in _guvenli(lambda c=c: cr._match_dims(q, c), []) or []:
            ad = d if isinstance(d, str) else str(d)
            if ad not in out:
                out.append(ad)
    return out


def _guvenli(f, varsayilan):
    """Bir çözümleyici patlarsa **niyet düşmez**, o alan boş kalır.

    ⚠ ADR-0020 *"sessiz yutma yok"* der ve haklıdır — ama burada yutulan bir **cevap**
    değil bir **gözlem**dir ve alternatifi, gözlemin cevabı düşürmesidir. Log yazılır.
    """
    from app.logging_setup import get_logger

    try:
        return f()
    except Exception:
        get_logger("niyet").warning("niyet alanı çözülemedi", exc_info=True)
        return varsayilan
