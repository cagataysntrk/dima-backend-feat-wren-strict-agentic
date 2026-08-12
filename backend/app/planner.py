"""PLANLAYICI ÇEKİRDEĞİ — bütçeli, denetlenen, makbuzlu adım yürütücü (Faz F2).

## Ne yapar, ne YAPMAZ

Bu modül **bir LLM döngüsü değildir.**

> ⟳ **FAZ 4 (2026-08-03) — BEYAN GÜNCELLENDİ.** Eski metin: *"Bir ReAct planlayıcısının
> 'hangi adımı seçeyim' kısmı henüz YOK ve bilinçli olarak yok: o karar telemetriyle
> kalibre edilmeli."* Faz 0 telemetriyi (`reject_reason`) kurdu, Faz 2b onu triyaja
> bağladı; `sec()` artık **var**. Ama tez değişmedi, **güçlendi**: `sec()` bir döngü
> değil, tek atımlık bir **öneri**dir ve önerinin kendisi hiçbir kapıyı atlamaz. Yani
> "planlayıcı zekâsı" eklendi ama **yönetişimin ÜSTÜNE**, yerine değil.

Burada olan şey **yürütmenin YÖNETİŞİMİDİR**: bir plan hangi araçları çağırırsa çağırsın,
her adım bütçeye, yetkiye ve deterministik-önce kuralına **tabidir** ve **makbuz üretir**.

> Planlayıcı zekâsı olmadan yönetişim işe yarar (bugünkü sabit kompozisyonlar da ondan
> geçebilir). Yönetişim olmadan planlayıcı zekâsı **tehlikelidir** — sınırsız bir döngü,
> denetlenmeyen bir yetki ve izlenmeyen bir maliyet demektir. Sıra bu yüzden böyle.

## Dört kapı

| Kapı | Ne yapar | Neden |
|---|---|---|
| **Kayıt** | Araç `app/tools.py`'de yoksa **red** | Planlayıcı araç UYDURAMAZ |
| **Yetki** | `izinli_araclar(principal)` dışındaysa **red** | Ajan kullanıcının yetkisini aşamaz |
| **Deterministik-önce** | Deterministik kardeşi DENENMEDEN LLM aracı **seçilemez** | Merdivenin felsefesi (MIMARI §2) plan seviyesinde |
| **Bütçe** | Adım/süre/sorgu tavanı aşılırsa **dur** | Şartname 4.16 — bugüne kadar SIFIR tavan vardı |

## Bütçe aşımı = DÜRÜST KISMİ CEVAP

Tavan aşıldığında koşum **sessizce kesilmez**: o ana kadar toplanan adımlar geçerlidir ve
`Kosum.kisildi` + `kisilma_nedeni` ile birlikte döner. Çağıran bunu kullanıcıya
söylemekle yükümlüdür — `contribution`'ın `kirpilan_segment`'i ve `taranmayan_boyut`'u ile
**aynı desen**: kapsamı daraltan her sınır görünür olur.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any

from app import tools
from app.logging_setup import get_logger

_log = get_logger("planner")

#: `sec()` çıktısındaki kod çiti — model JSON'u ```json ile sarabilir.
_FENCE_RE = re.compile(r"^```[a-z]*|```$", re.M)


class ButceAsimi(RuntimeError):
    """Tavan aşıldı — koşum durur ama o ana kadarki adımlar GEÇERLİDİR."""


class AracReddi(RuntimeError):
    """Araç kaydı / yetki / deterministik-önce kapısı reddetti."""


@dataclass(frozen=True)
class Butce:
    """Bir ajan koşusunun tavanları. `0`/`None` = o eksende sınırsız.

    Varsayılanlar **muhafazakârdır**: bir kullanıcı sorusunun cevabı 8 adımı geçiyorsa
    büyük olasılıkla plan yanlıştır ve daha fazla adım daha iyi bir cevap değil, daha
    pahalı bir başarısızlık üretir.

    `token` bugün **ölçülemiyor** (telemetri boş — Faz E-1) ve bu yüzden varsayılanı
    sınırsızdır. Ölçülmemiş bir eşik koymak, kapsamı gerekçesiz daraltmak olurdu; alan
    şimdiden var ki telemetri gelince **kod değil yalnız değer** değişsin.
    """

    adim: int = 8
    saniye: float = 30.0
    sorgu: int = 12
    token: int = 0


@dataclass
class Adim:
    """Tek bir araç çağrısının kaydı — makbuz ağacının yaprağı."""

    arac: str
    determinizm: str
    sure_ms: int
    makbuz: str | None = None
    hata: str | None = None
    # Kayıtlı bir araç DEĞİL (bileşik/eski yol) → kapılardan geçmedi. Gizlenmez:
    # denetçi hangi adımların denetlenmediğini görebilmeli.
    kapisiz: bool = False
    dis_maliyet: str = ""
    notlar: str = ""

    def ozet(self) -> dict[str, Any]:
        # ⚠️ DENETİM DÜZELTMESİ — bilinmeyen ad MAKBUZDA GÖRÜNÜR.
        # `Kosum.sorgu_sayisi` kayıtta olmayan bir adı "temkinli" sayıyor (çökmemek için,
        # bkz. oradaki gerekçe) ve WARNING yazıyor; ama makbuza HİÇBİR İZ düşmüyordu →
        # `query_count` işaretsiz bir tahmin taşıyordu. *"Kapsamı daraltan ya da tahmine
        # dayanan her sınır GÖRÜNÜR olur"* — bu deponun kendi kuralı.
        bilinmeyen = not self.kapisiz and not tools.kayitli_mi(self.arac)
        not_ = self.notlar or ("kayıtta olmayan ad — maliyeti TEMKİNLİ sayıldı"
                               if bilinmeyen else "")
        return {"tool": self.arac, "determinism": self.determinizm,
                "ms": self.sure_ms, "receipt": self.makbuz,
                **({"error": self.hata} if self.hata else {}),
                **({"gated": False, "note": not_} if (self.kapisiz or bilinmeyen) else {})}


@dataclass(frozen=True)
class PlanTaslagi:
    """🔴 **FAZ 6.4 — DONDURULMUŞ PLAN** (§8.1).

    ## Neden dondurulur — güvenlik gerekçesi

    **Kontrol-akışı bütünlüğü**: plan, **güvenilmeyen araç çıktısı bağlama girmeden**
    donar. Bir araç çıktısı planı değiştirebilseydi, dış veri (bir cube satırı, bir LLM
    metni) **koşumun akışını yönlendirebilirdi** — ve o an sistem bir ReAct döngüsüne
    dönerdi.

    > MIMARI §11.5 korunur: **bu modül bir ReAct döngüsü DEĞİLDİR.**

    ⚠ `frozen=True` bir **süs değil**: doğrulama düşünce **yalnız o noktadan** yeniden
    planlanır ve yeni bir taslak **üretilir** — var olanı düzenlemek, dondurmayı bir
    temenniye çevirirdi.
    """

    adimlar: tuple[dict[str, Any], ...]
    donduruldu: bool = True

    def __len__(self) -> int:
        return len(self.adimlar)


def dondur(adimlar: list[dict[str, Any]]) -> PlanTaslagi:
    """Öneri listesini **dondurulmuş** bir taslağa çevirir.

    ⚠ İç sözlükler de kopyalanır: bir çağıranın elindeki referansla adımı sonradan
    değiştirmesi, dondurmayı **görünmez biçimde** delerdi.
    """
    return PlanTaslagi(adimlar=tuple(dict(a) for a in (adimlar or [])))


# --- DÖRT KATMANLI ADIM DOĞRULAMA (§8.6) ------------------------------------------

#: Büyüklük mertebesi sapma eşiği — medyana göre **100×**. ⚠ Bir sapma bir **hata
#: değildir**, bir **işarettir**: doğrulama adımı düşürmez, **yeniden planlamayı**
#: tetikler.
MERTEBE_ESIGI = 100.0

#: Null oranı eşiği. Bir kolonun %90'ı boşsa o kolon bir **cevap taşımıyordur**.
NULL_ESIGI = 0.90


def adim_dogrula(sonuc: dict[str, Any] | None, *, olcu: str | None = None,
                 beklenen_kolonlar: list[str] | None = None) -> dict[str, Any]:
    """§8.6 — **dört katman**. Döner: `{gecti, katman, neden}`.

    | katman | koşul | neden önemli |
    |---|---|---|
    | `satir` | `row_count == 0` | boş bir sonuç bir cevap değil, bir **sessizliktir** |
    | `null` | `null_orani > %90` | kolon var ama **veri yok** — grafik boş çizilir |
    | `mertebe` | medyana göre **≥100×** sapma | birim/ölçek hatasının **tek** işareti |
    | `sema` | beklenen kolon yok | sorgu değişmiş, cevap **başka bir soruya** ait |

    🔴 **Doğrulama adımı DÜŞÜRMEZ.** Bir `gecti=False`, *"bu sonuç yanlış"* demez;
    *"bu noktadan yeniden planla"* der. Sonucu atmak, kullanıcıya hiçbir şey
    göstermemek olurdu — oysa **şüpheli bir sayı, yokluğundan daha bilgilendiricidir**,
    yeter ki şüphe **söylensin**.
    """
    satirlar = (sonuc or {}).get("rows") or []
    if not satirlar:
        return {"gecti": False, "katman": "satir",
                "neden": "sonuç boş — boş bir sonuç bir cevap değil, bir sessizliktir"}

    kolonlar = list((sonuc or {}).get("columns") or (satirlar[0].keys() if satirlar else []))
    if beklenen_kolonlar:
        eksik = [k for k in beklenen_kolonlar if k not in kolonlar]
        if eksik:
            return {"gecti": False, "katman": "sema",
                    "neden": f"beklenen kolon(lar) yok: {eksik} — cevap başka bir soruya ait"}

    hedef = olcu or next((k for k in kolonlar
                          if any(isinstance(r.get(k), (int, float)) for r in satirlar)), None)
    if hedef is None:
        return {"gecti": True, "katman": None, "neden": ""}

    degerler = [r.get(hedef) for r in satirlar]
    bos = sum(1 for v in degerler if v is None)
    if len(degerler) and bos / len(degerler) > NULL_ESIGI:
        return {"gecti": False, "katman": "null",
                "neden": f"`{hedef}` kolonunun %{bos / len(degerler) * 100:.0f}'i boş — "
                         f"kolon var ama veri yok"}

    sayilar = sorted(float(v) for v in degerler
                     if isinstance(v, (int, float)) and v is not None)
    # ⚠ Mertebe sapması **en az 3 gözlem** ister: iki noktada "medyan" bir merkez
    # değil, noktalardan biridir.
    if len(sayilar) >= 3:
        orta = sayilar[len(sayilar) // 2]
        if orta:
            enb = max(abs(x) for x in sayilar)
            if enb / abs(orta) >= MERTEBE_ESIGI:
                return {"gecti": False, "katman": "mertebe",
                        "neden": f"en büyük değer medyanın {enb / abs(orta):.0f}× katı — "
                                 f"birim/ölçek hatasının tek işareti budur"}
    return {"gecti": True, "katman": None, "neden": ""}


# --- HATA SINIFLANDIRMA (§8.8) ------------------------------------------------------

def hata_imzasi(arac: str, hata: str | None) -> str:
    """Aynı hatanın **kimliği** — mesaj metni değil, **sınıfı**.

    ⚠ Mesajın tamamını imza saymak, içindeki değişken parçalar (id'ler, sayılar)
    yüzünden **aynı hatayı her seferinde yeni** gösterirdi ve strateji hiç değişmezdi.
    """
    tip = str(hata or "").split(":", 1)[0].strip() or "?"
    return f"{arac}|{tip}"


def strateji_degistir_mi(imzalar: list[str], yeni: str) -> bool:
    """§8.8 — **aynı hata imzası 2. kez → strateji değiştir**.

    *Aynı yoldan ikinci kez geçmek bir ısrar değil, bir döngüdür.*
    """
    return imzalar.count(yeni) >= 1


@dataclass
class Kosum:
    """Bir ajan koşusunun tamamı: adımlar + bütçe durumu + kısılma gerekçesi."""

    adimlar: list[Adim] = field(default_factory=list)
    kisildi: bool = False
    kisilma_nedeni: str = ""
    kok_makbuz: str | None = None
    #: 🔴 FAZ 6.4 — **PLAN KONTROL LİSTESİ** (§8.7). *Kaç adım planlandı, kaçı tamamlandı*
    #: — bu ikisi ayrışırsa koşum **yarım kalmıştır** ve makbuz bunu söylemeli.
    adimlar_toplam: int = 0

    @property
    def adimlar_tamam(self) -> int:
        """Hatasız tamamlanan adım sayısı. ⚠ Hatalı adım da **kaydedilir** ama
        *tamamlandı* sayılmaz — ikisini karıştırmak, yarım bir koşumu tam gösterirdi."""
        return sum(1 for a in self.adimlar if not a.hata)

    @property
    def sorgu_sayisi(self) -> int:
        """Veriye dokunan adımlar (maliyet sınıfı `sifir` olmayanlar).

        Kapısız (bileşik) adımlar kayıtta olmadığı için maliyetlerini KENDİLERİ taşır —
        aksi halde `tools.get()` patlar ve bütçe muhasebesi bileşikleri hiç saymazdı.

        ⚠️ **FAZ 0.2 — MAKBUZ KENDİNİ YIKAMAZ.** Bu özellik `agent_run` makbuzunun
        üretim yolundadır: burada atılan bir istisna **makbuzun tamamını** düşürür ve
        `_butce_kapisi`'nı sessizce atlatır. Yani *"bilinmeyen araç"* durumunda doğru
        davranış **çökmek değil, TEMKİNLİ SAYMAK**tır — bir denetim aracı, denetlediği
        şeyin kusuru yüzünden **susmamalıdır**. Bilinmeyen ad `hata` alanıyla zaten
        makbuzda görünür; ayrıca `WARNING` yazılır — sessiz yutma YOK (ADR-0020).
        """
        n = 0
        for a in self.adimlar:
            if a.kapisiz:
                maliyet = a.dis_maliyet
            else:
                try:
                    maliyet = tools.get(a.arac).maliyet
                except KeyError:
                    # Kayıtta olmayan bir ad `kapisiz=False` ile kaydedilmiş: bu bir
                    # KUSURDUR (kaydeden yer düzeltilmeli) ama makbuzu yok etmez.
                    _log.warning("makbuz: kayıtta olmayan araç adı %r kapisiz=False ile "
                                 "kaydedilmiş — temkinli sayılıyor", a.arac)
                    maliyet = "pahali"
            if maliyet != "sifir":
                n += 1
        return n

    def makbuza(self) -> dict[str, Any]:
        """Kök makbuza yazılacak biçim — adım ağacı + kısılma kaydı.

        `truncated` alanı **her zaman** yazılır (False olsa bile): *"kısılmadı"* ile
        *"kısılma sorulmadı"* farklı şeylerdir ve bu ayrım denetçinin işine yarar.
        """
        return {
            "agent_run": {
                "steps": [a.ozet() for a in self.adimlar],
                "step_count": len(self.adimlar),
                "query_count": self.sorgu_sayisi,
                "truncated": self.kisildi,
                "truncation_reason": self.kisilma_nedeni or None,
            }
        }


class Planlayici:
    """Araç çağrılarını yöneten yürütücü.

    ⟳ **FAZ 4 (2026-08-03) — BEYAN GÜNCELLENDİ.** Eski metin *"**Plan seçmez**, planı
    UYGULAR"* diyordu; artık `sec()` ile **plan da önerebiliyor**. Ama ayrım korunuyor ve
    bu fazın omurgası odur: **`sec()` yalnız ÖNERİR, `calistir()` uygular.** Öneri hiçbir
    kapıyı atlamaz — LLM'in seçtiği bir araç, insanın seçtiği bir araçla **aynı dört
    kapıdan** geçer. Yani "LLM garson olur, işi küpler yapar" bir **beyan değil bir
    KAPIDIR**.

    Kullanım:

        p = Planlayici(principal=principal, butce=Butce(adim=5))
        try:
            cq = p.calistir("route", soru, schema)
            rapor = p.calistir("contribution.decompose", ...)
        except ButceAsimi:
            pass          # o ana kadarki adımlar GEÇERLİ — kısmi cevap ver
        makbuz = p.kosum.makbuza()
    """

    def __init__(self, *, principal: Any = None, butce: Butce | None = None,
                 kaynaklar: dict[str, Any] | None = None,
                 onay_biletleri: dict[str, str] | None = None) -> None:
        self.principal = principal
        self.butce = butce or Butce()
        # Servise bağlı araçlar için istek-kapsamlı nesneler: {"servis:wren": svc, …}
        self.kaynaklar = kaynaklar or {}
        # 🔴 ONAY BİLETLERİ — `{araç adı: bilet}`. Boş sözlük = **hiçbir yazma yok**.
        # Fail-closed bilinçlidir: bileti olmayan bir yazma aracı çalışmaz. Bunu
        # opsiyonel yapmak, onayı bir "unutulabilir adım" hâline getirirdi.
        self.onay_biletleri: dict[str, str] = dict(onay_biletleri or {})
        self.kosum = Kosum()
        self._baslangic = time.monotonic()
        # Bu koşumda DENENMİŞ deterministik ARAÇ ADLARI — deterministik-önce kapısının belleği.
        # DİKKAT: ad tutulur, etiket değil. İlk sürüm etiket tutuyor ve araç ADLARINI o
        # kümeye karşı sınıyordu — kapı `route` çalıştıktan sonra bile reddediyordu
        # (kendi testim yakaladı). Kapının yanlış-pozitifi, kapının olmamasından kötüdür:
        # meşru bir merdiven basamağını kapatır ve kural "işe yaramıyor" diye sökülür.
        self._denenen_araclar: set[str] = set()

    # --- kapılar -----------------------------------------------------------------

    def _yetki_kapisi(self, arac: tools.Arac) -> None:
        if self.principal is None:
            return          # kimliksiz çağrı (test/dahili) — yetki kapısı uygulanmaz
        if arac not in tools.izinli_araclar(self.principal):
            raise AracReddi(
                f"{arac.ad}: bu kullanıcının yetkisi yok ({arac.izin}). Ajan, kullanıcının "
                "kendi eliyle yapamayacağı bir işi onun adına YAPAMAZ.")

    def _onay_kapisi(self, arac: tools.Arac) -> None:
        """🔴 **BEŞİNCİ KAPI (2026-08-12) — `yan_etki != "yok"` ise ONAY BİLETİ ŞART.**

        ## Neden bu kapı doğdu — ölçülmüş bir boşluk

        `app/yazma_araclari.py` üç yazma aracını *"**yalnız** `onay_akisi` üzerinden
        çağrılabilir"* diye ilan ediyor ve bunu her aracın `notlar` alanına da yazıyor.
        Ölçüldü: `calistir()`'in dört kapısında `yan_etki` · `onay` · `bilet`
        kelimelerinin **hiçbiri geçmiyordu**. Yani değişmez **düzyazıydı**.

        > *Beyan edilmiş ama uygulanmamış bir kural, bir kural değil bir niyettir.*
        > Bu turda aynı sınıf `consistency_k` · `expose:` üreteci · fan-out ölçümü ·
        > `_select_consistent`'ta da ölçülmüştü — bu, o listenin beşincisidir.

        ## ⚠ Ve boşluğu GİZLEYEN şey, ikinci bir kusurdu

        Kural neden hiç fark edilmedi? Çünkü yazma araçları **zaten çalışmıyordu**:
        ilan edilen `girdi` (`title` · `cube_query`) gerçek imzayla
        (`request` · `did` · `body` · `session`) tutmuyor ve çağrı `TypeError` veriyor.
        Yani bugünkü güvenlik bir **kaza**ydı — bir kapı değil, bir uyumsuzluk.

        🔴 Ve bir `TypeError` bir **red değildir** (`ADR-0020` · *dürüst red* kültürü):
        çağırana neyin neden yapılmadığını söylemez, denetim kaydına bir gerekçe
        yazmaz, ve uyumsuzluk bir gün giderilirse **sessizce yazmaya döner**.

        ## Kapının biçimi — fail-closed

        Bilet `onay_akisi.bilet_dogrula()` ile doğrulanır (imza + ömür). Bilet yoksa,
        yanlışsa ya da süresi geçmişse araç **koşmaz**. `self.onay_biletleri` varsayılan
        olarak **boştur**: bir planlayıcıyı elle kurmak, yazma yetkisi vermez.
        """
        if arac.yan_etki == "yok":
            return
        token = self.onay_biletleri.get(arac.ad)
        if not token:
            raise AracReddi(
                f"{arac.ad}: bu araç `yan_etki={arac.yan_etki!r}` beyan ediyor ve "
                "ONAY BİLETİ olmadan çalıştırılamaz. Ajan bir yazma işini ancak "
                "ÖNERİR; onayı kullanıcı verir (`POST /ask/eylem` — bilet + denetim "
                "kaydı). Onaysız yazma, onayı bir süs yapardı.")
        from app import onay_akisi
        try:
            onay_akisi.bilet_dogrula(token, arac.ad)
        except Exception as exc:                              # noqa: BLE001
            raise AracReddi(
                f"{arac.ad}: onay bileti GEÇERSİZ ({type(exc).__name__}). Süresi "
                "geçmiş ya da başka bir eylem için verilmiş bir bilet, verilmemiş bir "
                "biletle aynıdır.") from exc

    def _deterministik_once_kapisi(self, arac: tools.Arac) -> None:
        """LLM aracı, aynı etiketteki deterministik kardeşi DENENMEDEN seçilemez.

        Bu, MIMARI §2'nin merdiven felsefesinin plan seviyesindeki karşılığıdır ve bir
        **kural değil bir KAPIDIR**: kural denetlenemezse kural değildir (bu turda
        `consistency_k`, `expose:` üreteci, fan-out ölçümü ve `_select_consistent`
        aynı sınıfta ölçüldü — hepsi beyan edilmiş, hiçbiri uygulanmamıştı).
        """
        if arac.determinizm != "llm":
            return
        kardesler = [
            d for d in tools.deterministik_olanlar()
            if set(d.etiketler) & (set(arac.etiketler) - {"llm"})
        ]
        denenmemis = [d.ad for d in kardesler if d.ad not in self._denenen_araclar]
        if kardesler and denenmemis:
            raise AracReddi(
                f"{arac.ad}: DETERMİNİSTİK-ÖNCE ihlali — önce {denenmemis} denenmeli. "
                "Bir işi deterministik bir araç yapabiliyorsa LLM aracı seçilemez.")

    def _butce_kapisi(self, arac: tools.Arac) -> None:
        b = self.butce
        if b.adim and len(self.kosum.adimlar) >= b.adim:
            self._kis(f"adım tavanı ({b.adim})")
        gecen = time.monotonic() - self._baslangic
        if b.saniye and gecen >= b.saniye:
            self._kis(f"süre tavanı ({b.saniye:.0f} sn)")
        if b.sorgu and arac.maliyet != "sifir" and self.kosum.sorgu_sayisi >= b.sorgu:
            self._kis(f"sorgu tavanı ({b.sorgu})")

    def _kis(self, neden: str) -> None:
        self.kosum.kisildi = True
        self.kosum.kisilma_nedeni = neden
        _log.info("ajan koşusu kısıldı: %s (adım=%d sorgu=%d)",
                  neden, len(self.kosum.adimlar), self.kosum.sorgu_sayisi)
        raise ButceAsimi(neden)

    # --- yürütme -----------------------------------------------------------------

    # --- PLAN SEÇİMİ (FAZ 4 / K3) -------------------------------------------------

    def sec(self, soru: str, llm: Any = None, *, ipucu: str = "") -> list[dict]:
        """Soruyu araç adımlarına ayırma ÖNERİSİ üretir. **Çalıştırmaz.**

        ## Seçim ≠ çalıştırma — bu fazın omurgası

        Dönen liste bir **öneridir**; her adım yine `calistir()`'e verilir ve orada dört
        kapıdan (kayıt · yetki · deterministik-önce · bütçe) geçer. Bu ayrım şunu garanti
        eder: **LLM'in uydurduğu bir araç adı KAYIT kapısında ölür**, yetkisiz bir araç
        YETKİ kapısında ölür, `route` denenmeden seçilen bir LLM aracı DETERMİNİSTİK-ÖNCE
        kapısında ölür. Yani seçicinin yanılması **yeni bir risk açmaz** — var olan
        kapılar zaten onu karşılar.

        ## LLM ne GÖRÜR

        `tools.llm_araclari(principal)` — ve o liste **yetkiye göre süzülmüş**tür, ayrıca
        yazma yan etkili araçları (`dashboards.create` · `schedules.create` ·
        `measures.approve`) ve gizlilik yapraklarını (`drill.raw` · `vqr.recall`)
        **beyan edilerek dışarıda bırakır** (`tools.py`). Ajan kullanıcıyı **aşamaz**.

        ## LLM yoksa

        Deterministik yedek: `["route"]`. Merdivenin birinci basamağı zaten her zaman
        denenmeli — yani sağlayıcı yokluğu bir hata değil, **plan zaten belliydi** demek.
        """
        adaylar = tools.llm_araclari(self.principal)
        gecerli = {a["name"] for a in adaylar}
        if llm is None or not hasattr(llm, "plan_sec") or not gecerli:
            return [{"arac": "route", "neden": "deterministik yedek (sağlayıcı yok)"}]
        try:
            import json as _json

            ham = llm.plan_sec(soru, _json.dumps(adaylar, ensure_ascii=False), ipucu)
            onerilen = _json.loads(_FENCE_RE.sub("", (ham or "").strip()))
        except Exception as exc:  # noqa: BLE001 — seçim başarısızsa merdiven zaten var
            _log.info("plan seçimi başarısız → deterministik yedek: %s", exc)
            return [{"arac": "route", "neden": "seçim başarısız → deterministik yedek"}]

        if isinstance(onerilen, dict):
            onerilen = onerilen.get("adimlar") or onerilen.get("steps") or []
        temiz: list[dict] = []
        for x in onerilen if isinstance(onerilen, list) else []:
            ad = (x or {}).get("arac") or (x or {}).get("tool") if isinstance(x, dict) else x
            if not isinstance(ad, str):
                continue
            if ad not in gecerli:
                # SESSİZ DÜŞÜRME YOK: uydurulmuş/yetkisiz bir araç adı KAYDA GEÇER.
                # Sessizce elemek, seçicinin ne kadar yanıldığını ölçülemez yapardı ve
                # bu deponun "sessiz kırpma yok" disiplinini delerdi.
                # ⚠️ FAZ 0.2 — `kapisiz=True` ZORUNLU: bu ad `tools.KAYIT`'ta YOK.
                # `False` bırakılırsa `Kosum.sorgu_sayisi` (yukarıda) `tools.get(ad)` çağırır
                # ve **KeyError** atar → `agent_run` makbuzu TAMAMEN düşer (`ask.py`'de
                # makbuz üretimi try/except içinde), `_butce_kapisi` de aynı yoldan patlayıp
                # `continue` ile yutulur → **bütçe kapısı SESSİZCE atlanır**. Yani makbuzun
                # en çok gerektiği anda (model bir araç adı UYDURDU) makbuz kaybolurdu.
                # `dis_maliyet="sifir"`: reddedilen adım veriye DOKUNMADI, sorgu saymaz —
                # ama adım olarak sayılır (bütçe muhasebesi eksik kalmaz).
                self.kosum.adimlar.append(Adim(
                    arac=ad, determinizm="llm", sure_ms=0, makbuz=None,
                    kapisiz=True, dis_maliyet="sifir",
                    notlar="seçim aşamasında reddedildi — hiç çalıştırılmadı",
                    hata="SEÇİM REDDİ: kayıtta yok ya da yetki dışı"))
                continue
            if ad not in {a["arac"] for a in temiz}:
                # FAZ O-2 (B1) — PLAN PARAMETRESIZDI: adim yalniz ARAC ADI tasiyordu.
                #
                # `sec()` bugune kadar LLM'in adim nesnesinden yalniz `arac` ve `neden`i
                # aliyor, kalanini DUSURUYORDU. Yani plan su cumleyi kurabiliyordu:
                # "once route, sonra contribution" — ama SUNU kuramiyordu:
                # "contribution'i MAKINE boyutunda, FIRE olcusunde calistir".
                #
                # Parametresiz bir plan, bir zincir degil bir SIRALAMADIR: adimlar
                # birbirine deger gecirmez, her biri kendi varsayimiyla kosar.
                #
                # Burada YALNIZ TASINIYOR — tuketici YOK. Bu bilincli: KURAL B geregi
                # davranis bayt bayt bugunku kalir, ve parametreleri okuyacak taraf
                # (plan semasi + calistirici) kendi faziyla, kendi bayragiyla gelir.
                # *Bir alani once tasimak, sonra okumak; ikisini birden yapmaktan
                # daha az riskli ve daha kolay geri alinabilirdir.*
                #
                # GUVENLIK DEGISMEDI: `arac` adi yine beyaz listeden geciyor (yukarida),
                # dort kapi (kayit·yetki·deterministik-once·butce) aynen yurulukte.
                # Parametreler bir ARAC ADI degildir; bir arac uydurmaya yaramaz.
                _par = x.get("parametreler") or x.get("params") or x.get("args") \
                    if isinstance(x, dict) else None
                _adim = {"arac": ad,
                         "neden": (x.get("neden") or x.get("why") or "")[:120]
                         if isinstance(x, dict) else ""}
                # Sozluk DISI bir sey tasinmaz: liste/metin/sayi bir parametre kumesi
                # degildir ve sessizce kabul edilirse tuketici tarafinda sasirtir.
                if isinstance(_par, dict) and _par:
                    _adim["parametreler"] = _par
                temiz.append(_adim)
        if not temiz:
            return [{"arac": "route", "neden": "geçerli adım kalmadı → deterministik yedek"}]
        # DETERMİNİSTİK-ÖNCE, PLAN SEVİYESİNDE: `route` öneride yoksa BAŞA eklenir.
        # Kapı zaten çalıştırmada bunu zorlar; burada eklemek, planın ilk adımda
        # ButceAsimi'na girip hiç denememesini önler (kapı ceza değil YÖNLENDİRME).
        if not any(a["arac"] == "route" for a in temiz):
            temiz.insert(0, {"arac": "route", "neden": "deterministik-önce (plan seviyesi)"})
        return temiz

    def calistir(self, arac_adi: str, *args: Any, makbuz: str | None = None,
                 **kwargs: Any) -> Any:
        """Tek bir aracı **dört kapıdan geçirerek** çalıştırır ve adımı kaydeder.

        `makbuz`: bu adımın ürettiği kanıtın kimliği (çağıran biliyorsa geçirir).
        Araç `makbuz` beyan ediyor ama çağıran kimlik vermiyorsa bu bir **boşluktur**
        ve adım kaydında `receipt=None` olarak görünür — gizlenmez.
        """
        arac = tools.get(arac_adi)                 # KAYIT kapısı (uydurma araç = KeyError)
        self._yetki_kapisi(arac)
        self._onay_kapisi(arac)
        self._deterministik_once_kapisi(arac)
        self._butce_kapisi(arac)

        kaynak = self.kaynaklar.get(arac.baglanma) if arac.baglanma != "modul" else None
        t0 = time.monotonic()
        hata = None
        try:
            fn = arac.cagir(kaynak)
            sonuc = fn(*args, **kwargs)
        except Exception as exc:
            hata = f"{type(exc).__name__}: {exc}"[:200]
            raise
        finally:
            # Adım BAŞARISIZ olsa da kaydedilir: bütçe tüketildi ve denetçi neyin
            # denendiğini görmeli. Sessizce kaybolan bir adım, yapılmamış bir adım
            # gibi okunur ve koşumun maliyeti anlaşılmaz olur.
            self.kosum.adimlar.append(Adim(
                arac=arac.ad, determinizm=arac.determinizm,
                sure_ms=int((time.monotonic() - t0) * 1000),
                makbuz=makbuz, hata=hata,
            ))
            if arac.determinizm == "deterministik":
                self._denenen_araclar.add(arac.ad)
        return sonuc

    def dis_adim(self, ad: str, *, sure_ms: int, makbuz: str | None = None,
                 maliyet: str = "pahali", not_: str = "") -> None:
        """Kayıtlı bir araç OLMAYAN bir işi adım ağacına **dürüstçe** kaydeder.

        Neden var: bugünkü kompozisyonların bir kısmı tek bir kayıtlı aracı değil, bir
        **bileşiği** çağırıyor (ör. katkı ayrıştırması bir uç noktanın gövdesidir ve içinde
        boyut başına ayrı sorgular koşar). Onu `tools.KAYIT`'a tek bir araçmış gibi yazmak
        **yalan olurdu**: ne girdisi tipli, ne çıktısı, ne de kapılardan geçiyor.

        Bu metot alternatifi değil **itirafıdır**: adım makbuzda görünür, maliyeti sayılır
        ve `gated=False` ile işaretlenir — yani denetçi hangi adımların kapılardan
        GEÇMEDİĞİNİ görebilir. Kayıtsız bir adımı hiç yazmamak, koşumu olduğundan ucuz ve
        daha denetlenmiş göstermek olurdu.

        Bütçeye **dahildir**: adım sayılır, `maliyet != "sifir"` ise sorgu sayılır. Yani
        yönetişim eksik olsa da maliyet muhasebesi eksik değildir.
        """
        self.kosum.adimlar.append(Adim(
            arac=ad, determinizm="karma", sure_ms=sure_ms, makbuz=makbuz,
            hata=None, kapisiz=True, dis_maliyet=maliyet, notlar=not_,
        ))

    def kalan(self) -> dict[str, Any]:
        """Bütçenin kalanı — çağıran bir sonraki adımı göze alıp alamayacağını sorabilir."""
        b = self.butce
        return {
            "adim": max(0, b.adim - len(self.kosum.adimlar)) if b.adim else None,
            "saniye": max(0.0, b.saniye - (time.monotonic() - self._baslangic))
                      if b.saniye else None,
            "sorgu": max(0, b.sorgu - self.kosum.sorgu_sayisi) if b.sorgu else None,
        }
