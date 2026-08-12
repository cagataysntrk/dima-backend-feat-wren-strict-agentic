"""ARAÇ KAYDI — agentic katmanın omurgası (Faz F1).

## Ne yapar, ne YAPMAZ

Bu modül **hiçbir yeteneği yeniden uygulamaz**. Dima'nın ~15 yeteneği zaten yazılı ve
testli; eksik olan şey onların **tipli, denetlenebilir, yetkiye bağlı birer araç olarak
BEYAN EDİLMESİYDİ**. Kayıt bir *bildirimdir*: her araç için kim olduğunu, ne aldığını, ne
döndürdüğünü, **deterministik mi** olduğunu, ne kadar pahalı olduğunu, yazıp yazmadığını,
hangi izne bağlı olduğunu ve **hangi makbuzu ürettiğini** söyler.

Sarmalayıcı yazmamanın gerekçesi ölçülmüş bir desendir: bu depoda "aynı kuralı ikinci kez
yazmak" defalarca sapmayla sonuçlandı (`drill.flag_outliers` ↔ `schedules.detect_anomalies`,
`interpret._fmt` ↔ `schedules._fmt_deger`, `_uncovered` ↔ `_syn_hit`). Bir aracın gövdesini
buraya kopyalamak aynı hatanın agentic ölçekteki hâli olurdu.

## Neden bu kayıt agentic katmanın ÖN KOŞULU

> *"Agentic katman, temelin ne ise onu ÇARPAR."*

Bir insan `/ask/drill action="raw"` yolunu yılda bir bulur; 15 araçlı bir planlayıcı onu
**ilk gün** bulur ve her gün kullanır. Bu yüzden araçlar serbest fonksiyonlar olarak değil,
**dört değişmeze bağlı** olarak açılır:

1. **Ajan kullanıcının yetkisini AŞAMAZ** — her araç bir `authorize()` aksiyonuna bağlıdır
   (`izin` alanı). Kayıt, matriste OLMAYAN bir izne bağlanamaz (test bunu kilitler).
2. **Ajan YAZAMAZ** — `yan_etki="yazar"` olan araçlar bu turda kayda **hiç alınmadı**.
   Yazma isteyen özellikler ayrı bir mimari karar ister; kayıt onları "ileride" diye
   içeri almaz, çünkü kayıtta görünen şey planlayıcının erişebildiği şeydir.
3. **Her adım bir MAKBUZ üretir** — `makbuz` alanı hangi kanıtın doğduğunu söyler.
   `makbuz=None` bir eksiklik değil bir BEYANDIR: o araç veriye dokunmaz (ör. `interpret`
   yalnız eldeki sonucu okur).
4. **Deterministik-önce** — `determinizm` alanı planlayıcının uyacağı kuralın verisidir:
   bir işi deterministik bir araç yapabiliyorsa LLM aracı SEÇİLEMEZ. Merdivenin felsefesi
   (MIMARI §2) plan seviyesine böyle taşınır.

## Bu modül üç yüzeyin ORTAK kaynağıdır

- **LLM'e verilen araç listesi** (`llm_araclari()`) — sağlayıcı-bağımsız şema.
- **MCP adaptörü** — ileride ince bir çevirici; kendi kaydını KURMAZ.
- **Yetki matrisi bağı** (`izinli_araclar()`) — UI'ın `permissions` listesiyle aynı kaynak.

Üçü ayrı ayrı yazılsaydı zamanla ayrışırlardı; bu depoda o desenin bedeli ölçüldü.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

Determinizm = Literal["deterministik", "llm", "karma"]
Maliyet = Literal["sifir", "ucuz", "pahali"]
YanEtki = Literal["yok", "yazar"]


@dataclass(frozen=True)
class Arac:
    """Tek bir yeteneğin beyanı. Gövde YOK — `cagir` var olan fonksiyonu gösterir."""

    ad: str
    ozet: str                       # planlayıcıya/LLM'e giden tek cümlelik tanım
    girdi: dict[str, str]           # alan → tip/anlam (JSON-Schema'ya çevrilir)
    cikti: str                      # ne döndürdüğü (tek cümle)
    determinizm: Determinizm
    maliyet: Maliyet
    yan_etki: YanEtki
    izin: str                       # authorize() aksiyonu — matriste VAR OLMALI
    makbuz: str | None              # ürettiği kanıt türü; None = veriye dokunmaz
    modul: str                      # "app.cube_router" ya da servis anahtarı (bkz. `baglanma`)
    fonksiyon: str                  # "route" · nokta içerebilir ("WrenService.cube_sql")
    # Çağrılabilir nesnenin NEREDEN geldiği. Bu alan olmadan kayıt yalan söylerdi: bazı
    # yetenekler modül fonksiyonu DEĞİL, istek-kapsamlı bir servisin metodudur ve onları
    # "app.x.y" diye bildirmek çözülemeyen bir işaretçi bırakırdı.
    #   "modul"       → `getattr(import_module(modul), fonksiyon)`
    #   "servis:wren" → `WrenService` örneğine bağlı metot (istek başına)
    #   "servis:llm"  → LLM sağlayıcısına bağlı metot (ördek-tipli, sağlayıcı değişir)
    baglanma: Literal["modul", "servis:wren", "servis:llm"] = "modul"
    #: 🔴🔴 `§D6`/`§C1` — **BU ARACIN KARŞILIK GELDİĞİ PLAN FİİLİ** (yoksa `None`).
    #:
    #: `C1` kartının kendi kararı bu biçimi **adıyla** istemişti:
    #:
    #: > *«Doğru biçim: her araç **kendi fiilini beyan eder** (`fiil` alanı) ve
    #: > `FIIL_ANLAMI` ondan türetilir.»*
    #:
    #: ⚠ Ve o kart üçüncü gerekçesinde şunu söylüyordu: *«adlar örtüşmediği için türetim
    #: bir EŞLEME TABLOSU ister — yani iki kayıt yerine ÜÇ şey»*. Bu alan tam olarak o
    #: üçüncü şeyin **doğmasını engeller**: eşleme ayrı bir tabloda değil, **aracın kendi
    #: beyanında** durur. `KAT-1` adına yapılan bir iş, üçüncü bir kayıt doğurmuyor.
    #:
    #: ⊙ `None` olması bir eksiklik değildir: araçların çoğu (`route` · `cube_sql` ·
    #: `llm.*` · `stats.*`) plan fiili değil, **alt yapı**dır.
    fiil: str | None = None
    # 🔴 **ÇALIŞTIRICININ VERDİĞİ PARAMETRELER — model ASLA vermez.**
    #
    # Ölçüldü (2026-08-09, `FAZ O` demeti): 25 aracın **yedisinin** `girdi` beyanı gerçek
    # imzayla uyuşmuyordu. İki ayrı sınıf çıktı ve ikisi de bu alan olmadan ayırt
    # edilemiyordu:
    #   · `girdi`de olup imzada OLMAYAN ad → LLM onu yazarsa `TypeError` (gerçek kusur)
    #   · imzada ZORUNLU olup `girdi`de olmayan ad → ya kusur ya **enjeksiyon**
    #
    # `svc`/`service`/`schema` gibi parametreler istek kapsamından gelir; onları `girdi`ye
    # yazmak modele *"bir motor nesnesi uydur"* demek olurdu. Bu alan o ayrımı **beyan
    # edilebilir** yapar ve kapı (`test_arac_beyani_imzayla_uyusur.py`) onu ölçer.
    #
    # *Bir sözleşmenin iki tarafı vardır: modelin verdiği ve çalıştırıcının verdiği.
    # İkisini ayırmayan bir beyan, ikisi hakkında da yalan söyler.*
    enjekte: tuple[str, ...] = field(default_factory=tuple)
    notlar: str = ""                # sınırlar, tuzaklar — planlayıcı bilmeli
    # 🔴 FAZ 6.2 — **GERİ ALMA REFERANSI.** `yan_etki="yazar"` bir araç bunu **taşımak
    # zorundadır**; `None` ise eylem **geri alınamaz** demektir ve bu **açıkça** böyle
    # işaretlenir. *Geri alınamazlığı gizlemek, onu geri alınabilir sanmaktan kötüdür:
    # kullanıcı bir daha hiç sormaz.*
    #
    # ⚠ Bir **metin referanstır**, çağrılabilir değil — çağrılabiliri kayda koymak onu
    # serileştirilemez ve **denetlenemez** yapardı (`onay_akisi.OnayTalebi` ile aynı
    # gerekçe).
    geri_alma_ref: str | None = None
    etiketler: tuple[str, ...] = field(default_factory=tuple)

    def cagir(self, kaynak: Any = None) -> Callable[..., Any]:
        """Beyan edilen çağrılabiliri ÇÖZER. Kayıt bir **işaretçidir**, bir kopya değil.

        `baglanma != "modul"` olan araçlar istek-kapsamlı bir nesneye bağlıdır ve `kaynak`
        verilmeden çözülemez — bu bilinçli: bir servis metodunu modül seviyesinde
        "çözülmüş" göstermek, hangi tenant'ın motoruna gittiğini gizlerdi.
        """
        if self.baglanma != "modul":
            if kaynak is None:
                raise ValueError(
                    f"{self.ad}: `{self.baglanma}` bağlı bir araç — çözmek için `kaynak` "
                    "(servis örneği) gerekir. İstek kapsamı olmadan çağrılamaz.")
            hedef: Any = kaynak
        else:
            import importlib

            hedef = importlib.import_module(self.modul)
        for parca in self.fonksiyon.split("."):
            hedef = getattr(hedef, parca)
        return hedef


# --- KAYIT ------------------------------------------------------------------------
#
# Sıra ÖNEMLİ DEĞİL ama gruplama okunabilirlik içindir: önce sorgu üretenler (merdivenin
# basamakları), sonra sorgu DÖNÜŞTÜRENLER, sonra sonuç YORUMLAYANLAR.
#
# Bu turda kayda ALINMAYANLAR ve nedenleri:
#   · `dashboards.create` / `schedules.create` / `measures.approve` → `yan_etki="yazar"`.
#     Ajanın yazma yetkisi ayrı bir mimari karardır (MIMARI §4: read-only değişmezi).
#   · `drill.raw` (ham satır) → T1/T2 gizlilik sınırının en hassas yaprağı; ajan yüzeyine
#     açılması Faz A2'nin kapattığı boşluğu sistematikleştirme riski taşır.
#   · `vqr.recall` → ham-SQL replay'i; şema-sürüm kapısı var ama ajan için ayrı bir
#     güven kalibrasyonu gerektirir (Faz E-3'ün hafıza tasarımına bağlı).
# Bunlar "unutuldu" değil, "beyan edilerek dışarıda bırakıldı" — kayıtta görünmeyen şey
# planlayıcının erişemediği şeydir ve bu liste onun sınırının kanıtıdır.

KAYIT: tuple[Arac, ...] = (
    # --- sorgu ÜRETENLER (merdiven) ---------------------------------------------
    # FAZ O-3 — ORKESTRATORUN ILKELLERI KAYDA GIRDI.
    #
    # Rapor (belgeler/plan/2026-08-09_ORKESTRATOR-KATMANI-VE-OLCEKLENME.md) su ayrimi
    # kuruyor: bugunku kayit 23 aracin 10'u RECETEDIR (yoy.compute · contribution.* ·
    # stats.* · kpi.resolve …). Bir recete takimi YAZILDIGI KADAR soru sekli karsilar;
    # bir ILKEL takim BILESIMLERININ TAMAMINI.
    #
    # Bu iki ilkel zincirin eksik halkasiydi: mutfak her adimi yapabiliyordu ama bir
    # adimin CIKTISINI otekinin GIRDISINE ceviren bir sey yoktu.
    #
    # E2 KORUMASI: liste BUYUMUYOR, YER DEGISTIRIYOR. Iki ilkel giriyor; receteler
    # SILINMIYOR (uclari calismaya devam ediyor) ama planlayicinin secim listesinden
    # kademeli cikacaklar. §99.1'in emsali burada da gecerli: uzun bir liste, secimi
    # kotulestirir.
    #
    # ⚠ Ikisi de `dis_maliyet="sifir"` ve `yan_etki="yok"`: veriye DOKUNMUYORLAR, ellerine
    # verilen satirlar uzerinde saf hesap yapiyorlar. Sorgu saymazlar — cunku sorgu
    # kosmazlar. Butce muhasebesi bu yuzden bozulmaz.
    Arac(
        ad="bagla",
        fiil="BAGLA",
        ozet="Koşmuş satırlardan BİR VARLIĞI seçip değerini döndürür — zincirin SATIR→DEĞER halkası. [Erişim: ELDEKİ SATIRLAR — yeni sorgu YOK, LLM YOK] "
             "[Ne zaman: bir adımın çıktısındaki «hangisi» sorusunu cevaplayıp sonraki "
             "adıma TEK BİR AD vermek gerektiğinde] [NE ZAMAN KULLANILMAZ: satır yoksa; "
             "bir sıralama isteniyorsa (o `order`'ın işi)]",
        girdi={"rows": "koşmuş sorgunun satırları",
               "boyut": "hangi kolondan varlık seçilecek",
               "olcu": "hangi ölçüye göre",
               "en_iyi_az": "ölçüde az olan iyi mi (lower_is_better beyanı)"},
        cikti="(varlık, değer) — satır yoksa (None, None)",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.ilkeller", fonksiyon="bagla",
        notlar="Yon SOZLUKTEN degil BEYANDAN okunur (`lower_is_better`) — §W-C'nin dersi. "
               "Uydurmaz: satir yoksa None doner.",
        etiketler=("ilkel", "llmsiz", "zincir"),
    ),
    Arac(
        ad="hesapla",
        fiil="HESAPLA",
        ozet="Bir hedefi AKRANLARIYLA kıyaslar: fark, yüzde ve akran sayısı. [Erişim: "
             "ELDEKİ SATIRLAR — yeni sorgu YOK, LLM YOK] [Ne zaman: «X neden ötekilerden düşük/yüksek» ailesinde, `bagla` hedefi sectikten SONRA] "
             "[NE ZAMAN KULLANILMAZ: ikiden az akran varsa — o bir kıyas değil ikinci "
             "bir sayıdır]",
        girdi={"rows": "koşmuş sorgunun satırları",
               "boyut": "kırılım kolonu", "olcu": "kıyaslanan ölçü",
               "hedef": "`bagla`'nın seçtiği varlık"},
        cikti="{hedef_deger, akran_ortalamasi, fark, fark_yuzde, akran_sayisi} ya da None",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.ilkeller", fonksiyon="hesapla",
        notlar="§AA1'in canli calisan gövdesi BUNUN uzerine kuruldu ve ciktisi bayt bayt "
               "korundu (E4). Payda sifirsa `fark_yuzde` None kalir — bolme uydurulmaz.",
        etiketler=("ilkel", "llmsiz", "zincir"),
    ),
    Arac(
        ad="route",
        fiil="SORGU",
        ozet="Türkçe soruyu SIFIR LLM ile bir CubeQuery'ye çözer; çözemezse None döner. [Erişim: yalnız KATALOG (ölçü/boyut adları) — ham veri YOK] [Ne zaman: her soruda İLK basamak] [NE ZAMAN KULLANILMAZ: takip mesajlarında (o `deterministic_refine`'ın işi); bir cevabın ÜSTÜNDE konuşurken]",
        girdi={"question": "kullanıcının sorusu (ham metin)",},
        enjekte=("schema",),
        cikti="{cube_query, order, limit} ya da None",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.cube_router", fonksiyon="route",
        notlar="Merdivenin BİRİNCİ basamağı. Deterministik-önce kuralı gereği planlayıcı "
               "bir soruyu LLM aracına vermeden ÖNCE bunu denemek ZORUNDADIR. `None` bir "
               "hata değil bir sinyaldir: kapsam boşluğu.",
        etiketler=("sorgu-uretimi", "llmsiz"),
    ),
    Arac(
        ad="deterministic_refine",
        ozet="Var olan bir CubeQuery'yi takip sorusuyla düzenler (granülerlik, kırılım, "
             "sıralama, dönem) — yeni sorgu üretmez, mevcut olanı değiştirir. [Erişim: önceki CubeQuery + katalog] [Ne zaman: elde bir rapor VARKEN gelen takip mesajında] [NE ZAMAN KULLANILMAZ: taze soruda (önceki sorgu yoksa); konu değiştiğinde]",
        girdi={"prev": "önceki cube_query", "q": "normalize edilmiş takip sorusu",},
        enjekte=("schema",),
        cikti="düzenlenmiş cube_query ya da None",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.cube_router", fonksiyon="deterministic_refine",
        notlar="Takip sorusu EKSİK CÜMLEDİR; bu yol kapsam kapısından GEÇMEZ (geçemez). "
               "Faz D3'te tam bu yüzden sessiz-yanlış üretiyordu — planlayıcı çıktısını "
               "körü körüne kabul etmemeli, boyut listesini kullanıcıya göstermeli.",
        etiketler=("sorgu-duzenleme", "llmsiz"),
    ),
    Arac(
        ad="cube_sql",
        ozet="CubeQuery'yi çalıştırılabilir SQL'e derler (JOIN YAZMAZ — cube derleyicisi). [Erişim: MDL + CubeQuery] [Ne zaman: çalıştırmadan hemen önce] [NE ZAMAN KULLANILMAZ: JOIN yazmak için — JOIN'i cube derleyicisi kurar; ham SQL üretmek için]",
        girdi={"cube_query": "CubeQuery", "order": "(ölçü, yön) ya da None",
               "limit": "satır üst sınırı ya da None"},
        cikti="SQL metni",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.wren_service", fonksiyon="cube_sql", baglanma="servis:wren",
        notlar="JOIN üretmez; ilişki-türevi boyutlar MDL'de HAZIR olmalıdır (MIMARI §3.2). "
               "Bir kolonun var olduğunu varsayma — `dry_plan` kolon varlığını denetlemez.",
        etiketler=("derleme", "llmsiz"),
    ),
    # --- sorgu DÖNÜŞTÜRENLER (gezinme) -------------------------------------------
    Arac(
        ad="drill.expand",
        fiil="KIR",
        ozet="Bir CubeQuery'ye yeni bir kırılım boyutu ekler (bir seviye aşağı in). [Erişim: CubeQuery + katalog boyutları] [Ne zaman: kullanıcı 'neden' diye sorup bir kırılım aradığında] [NE ZAMAN KULLANILMAZ: iki kırılım zaten varken (satır patlar); ölçü değiştirmek için]",
        girdi={"cube_query": "CubeQuery", "dimension": "eklenecek boyut adı"},
        cikti="genişletilmiş CubeQuery",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="drill:run", makbuz=None,
        modul="app.drill", fonksiyon="expand_cube_query",
        notlar="Boyutun HEDEF CUBE'DA var olduğu çağıranın sorumluluğudur. İlişki-türevi "
               "boyutlarda fan-out sertifikasına bak (`dimension_origin[*].certified`): "
               "`olculmedi` bir garanti DEĞİLDİR.",
        etiketler=("gezinme", "llmsiz"),
    ),
    Arac(
        ad="drill.select",
        fiil="SUZ",
        ozet="Bir hücreyi/segmenti tek başına gösteren CubeQuery üretir (grafikten seçim). [Erişim: CubeQuery + seçilen hücre] [Ne zaman: kullanıcı grafikte bir noktaya işaret ettiğinde] [NE ZAMAN KULLANILMAZ: ham satır göstermek için (T1/T2 sınırı); seçim yokken]",
        girdi={"cube_query": "CubeQuery", "dimension": "boyut", "value": "seçilen değer"},
        cikti="filtrelenmiş CubeQuery",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="drill:run", makbuz=None,
        modul="app.drill", fonksiyon="select_cube_query",
        notlar="Faz G2'nin 'grafiğe çapalı diyalog'unun taşıyıcısı: kullanıcının işaret "
               "ettiği nokta bir metin değil, GERÇEK bir alt-sorguya çevrilir.",
        etiketler=("gezinme", "llmsiz"),
    ),
    Arac(
        ad="yoy.compute",
        fiil="TREND",
        ozet="Aynı raporu önceki dönemle (yıl ya da ay) hizalayıp kıyas kolonları ekler. [Erişim: CubeQuery + zaman boyutu] [Ne zaman: 'geçen yıla/aya göre' istendiğinde] [NE ZAMAN KULLANILMAZ: çok-yıl veri yoksa; zaman boyutu olmayan cube'da]",
        girdi={ "cq": "CubeQuery", "mode": "'yoy' | 'mom'",
               "time_dim": "zaman boyutu adı", "limit": "satır üst sınırı"},
        enjekte=("service",),
        cikti="{rows, columns} — <ölçü>_gecen ve <ölçü>_degisim_yuzde kolonlarıyla",
        determinizm="deterministik", maliyet="ucuz", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.yoy", fonksiyon="compute",
        notlar="İKİ sorgu çalıştırır (cari + önceki). Eşleşmeyen satırda `_gecen` None "
               "kalır — 0 DEĞİL; 0 yazmak 'geçen dönem sıfırdı' demektir ve yüzdeyi "
               "yanıltıcı yapar. Planlayıcı bunu anlatıma taşımalı.",
        etiketler=("kiyas", "llmsiz"),
    ),
    # --- AÇIKLAYICILAR (neden değişti) -------------------------------------------
    Arac(
        ad="contribution.decompose",
        ozet="Dönemsel değişimi SEGMENTLERE dağıtır: kim ne kadar sürükledi? [Erişim: iki dönemin sonuçları] [Ne zaman: 'neden değişti' sorusunda, kırılım BELLİYKEN] [NE ZAMAN KULLANILMAZ: toplanamayan (ortalama/oran) ölçüde — katkı MATEMATİKSEL OLARAK tanımsızdır]",
        girdi={"rows": "kıyas satırları", "dim": "boyut", "measure": "ölçü",
               "cube_query": "kaynak CubeQuery"},
        cikti="ContributionReport — her bulgu KENDİ cube_query'siyle",
        determinizm="deterministik", maliyet="ucuz", yan_etki="yok",
        izin="contribution:run", makbuz="ContractLog (bulgu başına)",
        modul="app.contribution", fonksiyon="decompose",
        notlar="TOPLANABİLİRLİK KAPISI: katkı payı yalnız toplanabilir ölçülerde "
               "TANIMLIDIR. AVG/oran/COUNT(DISTINCT) için 'bu segment değişimin %40'ını "
               "açıklıyor' cümlesi MATEMATİKSEL OLARAK YANLIŞTIR — bu araç o durumda "
               "dürüst bir `note` döndürür ve planlayıcı onu cümleye çevirmemelidir.",
        etiketler=("kok-neden", "llmsiz"),
    ),
    Arac(
        ad="contribution.report",
        fiil="AYRISTIR",
        ozet="KULLANILMAYAN boyutları tarar, değişimi ayrıştırır, açıklayıcılığa göre sıralar. [Erişim: kullanılmayan boyutlar + iki dönem] [Ne zaman: hangi kırılımın açıkladığı BİLİNMEDİĞİNDE] [NE ZAMAN KULLANILMAZ: pahalıdır (boyut başına sorgu) — kırılım belliyse `contribution.decompose` yeter]",
        girdi={ "cube_query": "kaynak CubeQuery",
               "mode": "yoy|mom", "kind": "segment|pvm", "max_dimensions": "tarama sınırı"},
        enjekte=("service", "schema"),
        cikti="{measure, mode, kind, raporlar[], pvm_raporlar[], taranmayan_boyut, note}",
        # Boyut başına AYRI bir kıyas sorgusu koşar (cari + geçen dönem) — tek bir
        # `decompose` çağrısından pahalıdır ve maliyet sınıfı bunu SÖYLEMELİDİR.
        determinizm="deterministik", maliyet="pahali", yan_etki="yok",
        izin="contribution:scan", makbuz="ContractLog (boyut başına, `kaydet` verilirse)",
        # `baglanma="modul"`: servis METODU değil, servisi ARGÜMAN alan bir modül
        # fonksiyonudur — `route`/`yoy.compute` ile aynı biçim.
        modul="app.contribution", fonksiyon="arastir",
        notlar="Faz F3'e kadar bu gövde `/ask/contribution` ROUTER'ININ İÇİNDEYDİ ve HTTP'ye "
               "yapışıktı: planlayıcıya `dis_adim(gated=false)` diye itiraf olarak giriyor, "
               "arka plan işleri (zamanlanmış uyarılar) onu hiç çağıramıyordu. Ayrılınca ikisi "
               "de düzeldi. Tarama sınırı SESSİZ DEĞİLDİR: `taranmayan_boyut` yanıtta döner.",
        etiketler=("kok-neden", "llmsiz", "bilesik"),
    ),
    Arac(
        ad="contribution.pvm",
        ozet="Değişimi FİYAT / MİKTAR / BİRLEŞİK etkiye ayrıştırır (artıksız). [Erişim: fiyat/miktar çifti BEYAN EDİLMİŞ cube] [Ne zaman: ciro/tutar değişimi ekonomik olarak ayrıştırılacaksa] [NE ZAMAN KULLANILMAZ: `pvm` beyanı yoksa — ad kalıbından çıkarmak GÜVENLE YANLIŞ ekonomi üretir]",
        girdi={"cube_meta": "cube metadata (pvm: beyanı olmalı)"},
        cikti="PvmReport listesi — fiyat+miktar+birleşik = net (birebir)",
        determinizm="deterministik", maliyet="ucuz", yan_etki="yok",
        izin="contribution:run", makbuz="ContractLog (bulgu başına)",
        modul="app.contribution", fonksiyon="pvm_pairs",
        notlar="Yalnız cube'un `pvm:` BEYANI varsa çalışır — eşleştirme TAHMİN EDİLMEZ. "
               "Ayrışma artıksızdır; üç etkiyi toplayan okuyucu net değişimi bulmalıdır.",
        etiketler=("kok-neden", "llmsiz"),
    ),
    Arac(
        ad="interpret",
        fiil="ANLAT",
        ozet="Eldeki sonuç tablosunu deterministik olarak yorumlar (sinyal/aykırılık/trend). [Erişim: eldeki sonuç tablosu — LLM'e ham veri GİTMEZ] [Ne zaman: her cevapta, sayıların üstüne] [NE ZAMAN KULLANILMAZ: sonuç boşken; tek satırlık sonuçta trend aramak için]",
        girdi={"result": "sorgu sonucu", "cube_query": "kaynak CubeQuery"},
        cikti="Interpretation — flag'li, veri-güdümlü ifadeler",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.interpret", fonksiyon="interpret",
        notlar="VERİYE DOKUNMAZ — yalnız çağıranın ZATEN aldığı sonucu okur. Bu yüzden "
               "makbuz üretmez ve T2 (anlatım) katmanının deterministik çekirdeğidir: "
               "LLM üslubu yazar, SAYIYI bu araç koyar.",
        etiketler=("anlatim", "llmsiz"),
    ),
    Arac(
        ad="viz.recommend",
        fiil="GORSEL",
        ozet="Sonucun doğru görselleştirmesini DETERMİNİSTİK seçer (Show-Me/Cleveland-McGill). [Erişim: sonuç + cube metadata (birim/additive)] [Ne zaman: sonuç dolu olduğunda] [NE ZAMAN KULLANILMAZ: grafik türünü LLM'e SEÇTİRMEK için — karar deterministiktir (ADR-0024)]",
        # ⟳ `cube_meta` **YANLIŞTI**: `recommend`'in böyle bir parametresi yok. Semantik
        # metadata `viz.meta_args(cube_meta)` ile `units`/`lower_set`/`non_additive`/
        # `hedefler`e AÇILIR ve öyle geçilir. *Bir kolaylık fonksiyonunun girdisini,
        # sardığı fonksiyonun girdisi diye beyan etmek, çağrıyı imkânsız kılar.*
        girdi={"result": "sorgu sonucu", "cube_query": "CubeQuery"},
        enjekte=("units", "lower_set", "non_additive", "hedefler"),
        cikti="VizSpec",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.viz", fonksiyon="recommend",
        notlar="ADR-0024: grafik KARARI LLM'e VERİLMEZ. Planlayıcı bir grafik türü "
               "'seçemez' — yalnız bu aracı çağırabilir.",
        etiketler=("gorsellestirme", "llmsiz"),
    ),
    Arac(
        ad="cross_cube_add",
        ozet="Mevcut rapora BAŞKA bir cube'un ölçüsünü `blend` olarak katar (LLM'siz). [Erişim: iki cube'un ölçüleri + ortak grain] [Ne zaman: kullanıcı ikinci bir cube'un ölçüsünü de istediğinde] [NE ZAMAN KULLANILMAZ: grain uyuşmuyorsa (fan-out); ilişki sertifikası `olculmedi` ise]",
        girdi={"prev": "mevcut CubeQuery", "q": "kullanıcının sorusu",},
        enjekte=("schema",),
        cikti="genişletilmiş CubeQuery (`blend` alanı dolu) ya da None",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.cube_router", fonksiyon="cross_cube_add",
        notlar="MIMARI §9.2'nin yapısal sınırının İKİ ADIMLI çözümü: bir cube'un ölçüsü + "
               "başka cube'un boyutu TEK CubeQuery'de ifade EDİLEMEZ, ama önce `route` "
               "sonra bu araç ile İKİ ADIMDA edilebilir. Uyum ŞARTLIDIR: hedef cube "
               "mevcut kırılımı taşımıyorsa `None` döner — o grain'de blend YANLIŞ olurdu. "
               "Deterministik: planlayıcı bunu bir LLM aracından ÖNCE denemek zorundadır.",
        # ETİKET AİLESİ AYRI ve bu bilinçli: bu araç sıfırdan sorgu ÜRETMEZ, var olan bir
        # sorguyu GENİŞLETİR — yani `route`/`llm.select_cube` ile AYNI İŞ İÇİN yarışmaz.
        # `sorgu-uretimi` verilseydi deterministik-önce kapısı onu her LLM aracından önce
        # ZORUNLU kılardı; ama `prev` bir CubeQuery ister ve o yokken uygulanamaz —
        # yani kapı, uygulanamaz bir aracı şart koşup meşru yolları kapatırdı.
        # (Kendi kapım bunu yakaladı: `prompt_enhancer` testleri kırıldı.)
        etiketler=("kompozisyon", "llmsiz"),
    ),
    # --- LLM araçları (yalnız deterministik yol tükendiğinde) --------------------
    Arac(
        ad="llm.prompt_enhance",
        ozet="Soruyu katalog terimleriyle YENİDEN YAZAR (yapı SEÇMEZ) — sonuç route()'a döner. [Erişim: soru metni + katalog terimleri — ham veri YOK] [Ne zaman: `route()` boş döndüğünde, LLM seçiminden ÖNCE] [NE ZAMAN KULLANILMAZ: yapı SEÇMEK için — yalnız yeniden yazar]",
        girdi={"soru": "kullanıcının ham sorusu", "catalog": "cube kataloğu metni"},
        cikti="düz metin (yeniden yazılmış soru) — DETERMİNİSTİK route()'a geri verilir",
        determinizm="llm", maliyet="ucuz", yan_etki="yok",
        izin="llm:invoke", makbuz=None,
        modul="app.llm", fonksiyon="prompt_enhance", baglanma="servis:llm",
        notlar="T1'in DÖRDÜNCÜ, AYRI LLM rolü: `llm.select_cube` ALAN SEÇER, bu yalnız "
               "METNİ iyileştirir — 'hangi ölçü/boyut' kararı HÂLÂ KÜPTEDİR. "
               "`sorgu-uretimi` etiketi DETERMİNİSTİK-ÖNCE kapısını bağlar: `route` "
               "denenmeden bu araç SEÇİLEMEZ (kapının kendisi bunu zorlar, bir kural "
               "olarak yazılmadı). Çıktı YAPI değil METİNDİR; uydurma bir terim üretse "
               "bile `route()` onu yine reddeder — yani hata yüzeyi yapısal olarak dar.",
        etiketler=("sorgu-uretimi", "llm"),
    ),
    Arac(
        ad="llm.anlat",
        ozet="Deterministik olguları AKICI Türkçeye çevirir — T2 anlatıcı (FAZ 5). [Erişim: deterministik OLGULAR — ham satır YOK] [Ne zaman: olgular hesaplandıktan sonra, üslup için] [NE ZAMAN KULLANILMAZ: SAYI üretmek için — sayıyı her zaman küp koyar ve `narration_guard` eşleşmeyeni DÜŞÜRÜR]",
        girdi={"soru": "kullanıcının sorusu",
               "gercekler": "interpret() facts listesi (ZATEN hesaplanmış)"},
        cikti="düz metin — narration_guard'tan GEÇMEDEN yayımlanamaz",
        determinizm="llm", maliyet="ucuz", yan_etki="yok",
        izin="llm:invoke", makbuz=None,
        modul="app.llm", fonksiyon="anlat", baglanma="servis:llm",
        notlar="LLM ÜSLUBU yazar, SAYIYI SİSTEM KOYAR (§4.4). SQL yazmaz, sayı "
               "hesaplamaz, cube seçmez, HAM SATIR GÖRMEZ — girdisi yalnız "
               "`interpret()`'in doğrulanmış olgularıdır. Çıktısı `narration_guard` "
               "kapısından ZORUNLU geçer: eşleşmeyen sayı taşıyan cümle DÜŞER; hiçbir "
               "cümle sağ kalmazsa anlatı HİÇ EKLENMEZ ve deterministik `summary` "
               "yerinde kalır. En kötü durum 'süssüz ama doğru', asla 'akıcı ama "
               "uydurma' DEĞİLDİR. HER SAĞLAYICIDA YOKTUR (kural-tabanlı taşımaz) — "
               "yokluğu bir hata değil YOL KAPALI sinyalidir.",
        etiketler=("anlatim", "t2", "guardli"),
    ),
    Arac(
        ad="narration_guard.dogrula",
        ozet="Bir anlatı metnindeki HER sayıyı sonuç kümesine karşı doğrular — KAPIDIR. [Erişim: anlatı metni + sonuç kümesi] [Ne zaman: her LLM anlatısından SONRA — KAPIDIR, seçenek değil] [NE ZAMAN KULLANILMAZ: atlanamaz; atlanırsa uydurma sayı yayımlanır]",
        girdi={"metin": "yayımlanmak istenen düz metin",
               "result": "cevabın sonuç kümesi (rows/columns)",
               # ⟳ `ek` → `ek_degerler`: imzadaki ad bu. Bir **ad kayması**, ve en
               # sinsi tür — anlam doğru, çağrı imkânsız.
               "ek_degerler": "beyan edilmiş ek türetmeler (ör. ara değerler)"},
        cikti="Rapor{gecti, temiz_metin, reddedilen, dogrulanamayan_sayilar}",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.narration_guard", fonksiyon="dogrula",
        notlar="⟳ FAZ 1.9 — KAYDA GİRDİ ve gerekçesi: kayıtta GÖRÜNMEYEN bir kapı, "
               "planlayıcının bilmediği bir kapıdır; yeni bir anlatı yüzeyi eklendiğinde "
               "onu ATLAMAK bir 'unutma' değil, 'kaydın söylemediği bir şeyi bilmemek' "
               "olur. `makbuz=None` bir eksiklik DEĞİL bir BEYANDIR: bu araç veriye "
               "dokunmaz, eldeki metni okur. "
               "🔴 KD-21 SINIRI: guard RAKAMSIZ bir cümlede YETKİSİZDİR — doğrulayacak "
               "sayı yoksa cümle geçer. Yeni anlatı yüzeyleri SAYI TAŞIYAN cümleler "
               "üretmelidir, yoksa kapı onları GÖRMEZ ve 'guard'dan geçti' cümlesi "
               "karşılıksız kalır. "
               "⚠ Yeni türetmeler `ek=` ile BEYAN EDİLİR; `izinli_degerler`'in KAPALI "
               "listesi genişletilmez — 'her aritmetik kombinasyon' serbest bırakılsaydı "
               "yeterince sayıyla her şey türetilebilir ve kapı hiçbir şeyi engellemezdi.",
        # 🔴 ETİKET "anlatim" DEĞİL — ve bu ölçülmüş bir düzeltme. İlk yazımda öyleydi
        # ve planlayıcının DETERMİNİSTİK-ÖNCE kuralı guard'ı `llm.anlat`'ın
        # ALTERNATİFİ sandı: `AracReddi: llm.anlat: DETERMİNİSTİK-ÖNCE ihlali — önce
        # ['narration_guard.dogrula'] denenmeli`. BİR KAPI, BİR ALTERNATİF DEĞİLDİR:
        # guard anlatı ÜRETMEZ, üretileni DOĞRULAR. Aynı etiketi paylaşmak "bir mekanizma
        # = bir iş" kuralının (KAT-1) ihlaliydi ve üç T2 testi anında kırmızı verdi.
        etiketler=("dogrulama", "kapi", "llmsiz"),
    ),
    Arac(
        ad="llm.select_cube",
        ozet="Katalogdan ölçü/boyut/filtre SEÇER (SQL YAZMAZ) — Intent-JSON. [Erişim: KATALOG metni (ad/etiket/sinonim) — ham veri YOK] [Ne zaman: `route()` çözemediğinde] [NE ZAMAN KULLANILMAZ: SQL yazmak için; `route()` zaten çözdüyse (deterministik-önce)]",
        girdi={"question": "soru", "catalog": "cube kataloğu metni"},
        cikti="CubeQuery (JSON) — deterministik derleyiciye gider",
        determinizm="llm", maliyet="ucuz", yan_etki="yok",
        izin="llm:invoke", makbuz=None,
        modul="app.llm", fonksiyon="select_cube", baglanma="servis:llm",
        notlar="HER SAĞLAYICIDA YOKTUR (ölçüldü): anahtarsız `RuleBasedSqlGenerator` bu "
               "metodu taşımaz ve üretim yolu `hasattr` ile denetler — planlayıcı yokluğunu "
               "bir hata değil bir YOL KAPALI sinyali saymalıdır. "
               "DETERMİNİSTİK-ÖNCE: `route` bir cevap veriyorsa bu araç SEÇİLEMEZ. "
               "LLM burada SQL yazmaz, yalnız SEÇER; sayıyı hâlâ derleyici üretir. "
               "`consistency_k>1` ise k örnek alınıp oylanır (Faz D4) ve uyum oranı "
               "planlayıcının güven sinyalidir.",
        etiketler=("sorgu-uretimi", "llm"),
    ),
)

# 🔴 FAZ 6.3 — **"ZATEN VAR AMA KAYITSIZ"**: sıfır yeni kod, yalnız **beyan**.
#
# Bu altı yetenek üründe **çalışıyordu** ama araç kaydında **yoktu** — yani planlayıcı
# onlara **erişemiyordu**. *Kayıtta görünmeyen şey, planlayıcının erişemediği şeydir* ve
# bu liste onun sınırının kanıtıdır; sınır **yanlış yerdeydi**.
#
# ⚠ **Bir ad düzeltildi:** yol haritası `kpi.resolve_series` diyordu; ölçüldü, öyle bir
# fonksiyon **yok** — gerçek ad `kpi.resolve_kpi`. *Bir plandaki ad, koddaki adın yerine
# geçmez.*
#: 🔴🔴 `§D6` — **PLAN İLKELLERİ KAYDA GİRDİ: «tek yetenek kaydı» artık GERÇEKTEN tek.**
#:
#: ## Ölçülen kusur (2026-08-12)
#:
#: `plan_semasi.FIIL_ANLAMI` **15 fiil** taşıyordu, `tools.KAYIT` **25 araç** — ve rapor
#: bunları *«%73 örtüşür»* diye kaydetmişti. Gerçek eşleşme **gövde düzeyinde** sayıldı:
#:
#:     9/15 fiil kayıtlı bir aracın gövdesini çağırıyor  (route · bagla · hesapla ·
#:                yoy.compute · contribution.report · drill.expand/select · viz.recommend)
#:     🔴 6/15 fiilin gövdesi kayıtta HİÇ YOKTU:
#:         MATRIS · SIRALA · RAPOR · PANO   → `app.ilkeller.*`
#:         KIYASLA · BOYUTSEC               → `app.contribution.*`
#:
#: ⊙ Yani *«tek yetenek kaydı»* iddiası **altı yetenek eksikti**: planlayıcı onları
#: çağırabiliyordu ama envanter onları **bilmiyordu** — yetki sınıfı, determinizmi,
#: maliyeti hiçbir yerde beyanlı değildi.
#:
#: > *Bir kaydın tekliği, sayısıyla değil KAPSAMIYLA ölçülür; kapsamadığı her yetenek,
#: > o kaydın söylemediği bir cümledir.*
#:
#: ⚠ Altısı da **aynı sınıf**: koşmuş satırlar üstünde saf dönüşüm — yeni sorgu YOK,
#: LLM YOK, yazma YOK. Bu yüzden `bagla`/`hesapla` ilkelleriyle **birebir aynı** beyanı
#: taşıyorlar (`determinizm=deterministik · maliyet=sifir · yan_etki=yok ·
#: izin=query:run · makbuz=None`). *Yeni bir yetki sınıfı açmak, olmayan bir riski
#: icat etmektir.*
PLAN_ILKELLERI: tuple[Arac, ...] = (
    Arac(
        ad="matris",
        fiil="MATRIS",
        ozet="Adayları ölçütlerle yan yana koyar (satır=aday, sütun=ölçüt) — saf "
             "hizalama. [Erişim: ELDEKİ SATIRLAR — yeni sorgu YOK, LLM YOK] "
             "[Ne zaman: birden çok adımın satırları TEK bir karşılaştırma tablosunda "
             "buluşacaksa] [NE ZAMAN KULLANILMAZ: tek kaynak varsa — hizalanacak bir "
             "şey yoktur]",
        girdi={"kaynaklar": "koşmuş adımların satır listeleri",
               "boyut": "aday anahtarı olan kolon"},
        cikti="birleştirilmiş satırlar (aday × ölçüt)",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.ilkeller", fonksiyon="matris",
        notlar="Aritmetik YOK, agirlik YOK: yalniz hizalama. Bir KARAR matrisi degil "
               "bir KARSILASTIRMA tablosudur.",
        etiketler=("ilkel", "llmsiz", "zincir"),
    ),
    Arac(
        ad="sirala",
        fiil="SIRALA",
        ozet="Adayları çok ölçütle sıralar — **ağırlık YOK, hepsi EŞİT**. "
             "[Erişim: ELDEKİ SATIRLAR — yeni sorgu YOK, LLM YOK] "
             "[Ne zaman: bir karşılaştırma tablosundan bir sıra çıkarılacaksa] "
             "[NE ZAMAN KULLANILMAZ: tek ölçüt varsa — o `order`'ın işidir]",
        girdi={"rows": "karşılaştırma tablosunun satırları",
               "boyut": "aday anahtarı", "olculer": "sıralamaya giren ölçüler",
               "az_iyi": "hangi ölçülerde AZ olan iyidir (beyan)"},
        cikti="sıralanmış satırlar (+ sıra bilgisi)",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.ilkeller", fonksiyon="sirala",
        notlar="Agirligi MODEL koymaz, hic kimse koymaz: agirlik bir IS KARARIDIR ve "
               "beyani yoktur. Yon `az_iyi` BEYANINDAN okunur.",
        etiketler=("ilkel", "llmsiz", "zincir"),
    ),
    Arac(
        ad="rapor",
        fiil="RAPOR",
        ozet="Koşmuş bölümleri tek bir belgeye dizer — hiçbir şey hesaplamaz. "
             "[Erişim: KOŞMUŞ BÖLÜMLER — yeni sorgu YOK, LLM YOK] "
             "[Ne zaman: çok bölümlü bir çıktı isteniyorsa] "
             "[NE ZAMAN KULLANILMAZ: tek bölüm varsa — belge bir zarf değil bir yüktür]",
        girdi={"bolumler": "koşmuş adımların çıktıları", "baslik": "belge başlığı"},
        cikti="belge (bölümler + başlık)",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.ilkeller", fonksiyon="rapor",
        notlar="Hicbir sey HESAPLAMAZ, dizer. Sayilar bolumlerin kendisinden gelir.",
        etiketler=("ilkel", "llmsiz", "belge"),
    ),
    Arac(
        ad="pano.taslak",
        fiil="PANO",
        ozet="Sorgulardan bir pano TASLAĞI kurar — 🔴 **hiçbir şey kaydetmez**. "
             "[Erişim: KOŞMUŞ SORGULAR — yazma YOK] "
             "[Ne zaman: kullanıcı bir pano istiyorsa] "
             "[NE ZAMAN KULLANILMAZ: kalıcılaştırma için — o onay akışının işidir]",
        girdi={"sorgular": "panoya girecek cube sorguları", "baslik": "pano başlığı"},
        cikti="pano taslağı (kaydedilmemiş)",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.ilkeller", fonksiyon="pano_taslagi",
        # ⚠ Yazma aracının ADI burada GEÇMEZ: bu metin seçici listesine giriyor ve
        # `test_SECICI_YALNIZ_bu_listeyi_gorur` orada bir yazma aracı adı görmemeli.
        # *Bir yasağın adını anmak, onu listeye sokmanın en sessiz yoludur.*
        notlar="YAZMAZ. Kalicilastirma AYRI bir yazma aracinin ve ONAYIN isidir; "
               "ikisini ayirmak calistiricinin salt-okunurlugunu korur (§D7).",
        etiketler=("ilkel", "llmsiz", "taslak"),
    ),
    Arac(
        ad="contribution.akran",
        fiil="KIYASLA",
        ozet="Bir hedefi AKRANLARIYLA kıyaslar ve farkı en çok açıklayan ölçüyü bulur. "
             "[Erişim: küp — akran satırları için sorgu koşar] "
             "[Ne zaman: «X neden ötekilerden farklı» ailesinde] "
             "[NE ZAMAN KULLANILMAZ: ikiden az akran varsa — o bir kıyas değildir]",
        girdi={"cq": "hedefin cube sorgusu", "measure": "kıyas ölçüsü",
               "cube_meta": "küp beyanı"},
        # ⚠ `service` istek kapsamlıdır — model bir motor nesnesi uyduramaz, çalıştırıcı
        # verir. Beyan kapısı (`test_ZORUNLU_PARAMETRE_YA_BEYANLI_YA_ENJEKTE`) bunu ilk
        # koşumda yakaladı: *yazılmayan bir zorunluluk, çağrı anında bulunur.*
        enjekte=("service",),
        cikti="akran kıyası (fark · yüzde · akran sayısı) ya da None",
        # ⚠ `yan_etki="yok"` — ilk yazımımda `"okur"` yazmıştım ve o değer bu kayıtta
        # **hiç kullanılmıyor**: sorgu koşan araçlar bile (`route` · `cube_sql` ·
        # `contribution.report`) `"yok"` beyan ediyor. *Yan etki VERİYE yapılan etkidir;
        # okumak bir yan etki değildir.* Uydurduğum değer, `§F13`'ün onay kapısına bu
        # aracı bir **yazma aracı** gibi gösterdi (kapı yakaladı).
        determinizm="deterministik", maliyet="dusuk", yan_etki="yok",
        izin="contribution:run", makbuz="sorgu",
        modul="app.contribution", fonksiyon="_akran_kiyasi",
        notlar="§AA1. Akran kumesi kupun kendi boyutundan gelir; uydurma akran YOK.",
        etiketler=("recete", "llmsiz", "kok-neden"),
    ),
    Arac(
        ad="contribution.boyutsec",
        fiil="BOYUTSEC",
        ozet="Hangi boyutun farkı en çok AÇIKLADIĞINI sıralar. "
             "[Erişim: KOŞMUŞ katkı raporları — yeni sorgu YOK, LLM YOK] "
             # ⚠ *«kök neden»* YAZILMAZ: `§E4`'ün kararı — biz **katkı** ölçüyoruz,
             # nedensel iddia nedensel bir graf beyanı ister ve o beyan yok. Kapı
             # (`test_ARKA_UCTA_kullaniciya_donen_kok_neden_METNI_YOK`) bunu ilk
             # koşumda yakaladı. *Bir adı düzeltmek, onu her yerde düzeltmektir.*
             "[Ne zaman: bir kırılımdan ötekine inerken sıradaki boyutu seçmek "
             "gerektiğinde] "
             "[NE ZAMAN KULLANILMAZ: elde katkı raporu yoksa — sıralanacak bir şey yok]",
        girdi={"raporlar": "katkı ayrıştırma raporları"},
        cikti="boyutlar, açıklayıcılığa göre sıralı",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.contribution", fonksiyon="rank_dimensions",
        notlar="Sezgi: degisimin buyuk kismi TEK bir segmentten geliyorsa o boyut daha "
               "aciklayicidir. Esik yok, sira var.",
        etiketler=("ilkel", "llmsiz", "kok-neden"),
    ),
)


KAYITSIZ_OLANLAR: tuple[Arac, ...] = (
    Arac(
        ad="prescribe.recete",
        ozet="Sinyallerden aksiyon reçetesi üretir (seçenekler + gerekçe). "
             "[Erişim: hesaplanmış sinyaller — ham veri YOK] "
             "[Ne zaman: 'ne yapmalıyız?' türü bir soruda] "
             "[NE ZAMAN KULLANILMAZ: sinyal yokken (reçete uydurur); bir SAYI sorusuna "
             "cevap olarak]",
        # 🔴 ⟳ **BEYAN TAMAMEN YANLIŞTI.** `recete(rapor, *, lower_is_better, azami, esik)`
        # imzasında ne `signals` ne `cube_query` var; girdi bir **`ContributionReport`
        # sözlüğüdür**. Bu araç bir plandan çağrılsaydı `TypeError` alırdı.
        girdi={"rapor": "ContributionReport sözlüğü "
                        "({net_degisim, brut_hareket, bulgular:[…]})"},
        enjekte=("lower_is_better",),
        cikti="seçenekler + gerekçe",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.prescribe", fonksiyon="recete",
        notlar="Deterministik: aynı sinyaller aynı reçeteyi verir.",
        etiketler=("yorum", "karar"),
    ),
    Arac(
        ad="statements.resolve",
        ozet="Gelir tablosu / bilanço gibi ÇOK SATIRLI mali tabloyu çözer. "
             "[Erişim: mali cube'lar (mizan/cari) + tablo tanımı] "
             "[Ne zaman: kullanıcı bir MALİ TABLO istediğinde] "
             "[NE ZAMAN KULLANILMAZ: tek bir ölçü sorusu için (aşırı ağır); mali tablo "
             "tanımı olmayan tenant'ta]",
        enjekte=("svc",),   # istek kapsamlı motor — model bir motor nesnesi uyduramaz
        girdi={"kind": "gelir_tablosu | bilanco",
               "extra_filters": "isteğe bağlı ek filtreler"},
        cikti="satır hiyerarşili mali tablo",
        determinizm="deterministik", maliyet="ucuz", yan_etki="yok",
        izin="query:run", makbuz="contract_id",
        modul="app.statements", fonksiyon="resolve_statement",
        notlar="⚠ Yol haritası bu aracı `statements.resolve` diye adlandırmıştı; öyle "
               "bir fonksiyon YOK — gerçek ad `resolve_statement`. **İki ad hatası** bu "
               "maddede ölçüldü (öteki: `kpi.resolve_series`). *Bir plandaki ad, koddaki "
               "adın yerine geçmez* — ve kapı artık her aracın gerçekten ÇÖZÜLDÜĞÜNÜ "
               "ölçüyor.",
        # ⚠ `sorgu-uretimi` etiketi **BİLEREK YOK**: o etiket merdivenin `route()`
        # basamağını işaretler ve *deterministik-önce* kapısının veri kaynağıdır. Mali
        # tablo bir **alternatif** değil, ayrı bir yetenektir; etiketi paylaşmak
        # planlayıcıya *"route yerine bunu kullanabilirsin"* dedirtirdi.
        etiketler=("mali",),
    ),
    Arac(
        ad="kpi.resolve",
        ozet="Çapraz-cube KPI'yı bileşenlerinden hesaplar (formül tanımdan gelir). "
             "[Erişim: KPI tanımı + bileşen cube'lar] "
             "[Ne zaman: kullanıcı tanımlı bir KPI sorduğunda] "
             "[NE ZAMAN KULLANILMAZ: formülü UYDURMAK için — tanımsız bir KPI "
             "hesaplanmaz, sorulur]",
        girdi={"spec": "KPI tanımı (JSON)", "where": "isteğe bağlı filtre"},
        enjekte=("svc",),
        cikti="KPI değeri + bileşenler",
        determinizm="deterministik", maliyet="pahali", yan_etki="yok",
        # ⚠ `contribution:scan` bu deponun **var olan** "pahalı çok-sorgulu tarama"
        # kapısıdır. Adı katkı-ayrıştırmasına özgü ama **anlamı** maliyet sınırıdır ve
        # yeni bir izin İCAT ETMEK, matrisi bir araç için genişletmek olurdu.
        # 🔴 Ad borcu kayda geçti: izin bir gün `scan:expensive` gibi nötr bir ada
        # taşınmalı — ama o, matrisi değiştiren AYRI bir karardır.
        izin="contribution:scan", makbuz="contract_id",
        modul="app.kpi", fonksiyon="resolve_kpi",
        notlar="⚠ Yol haritası bu aracı `resolve_series` diye adlandırmıştı; öyle bir "
               "fonksiyon YOK. Ad koddan alındı.",
        etiketler=("kpi",),
    ),
    Arac(
        ad="katalog",
        ozet="Bu kiracının KATALOG ENVANTERİ: hangi küpler, hangi ölçüler, hangi "
             "boyutlar var. "
             "[Erişim: yok — şema enjekte edilir] "
             "[Ne zaman: bir ajan MERDİVENE BAŞLAMADAN ÖNCE; `route` bir `schema` "
             "ister ve onu başka hiçbir araç vermiyordu] "
             "[NE ZAMAN KULLANILMAZ: bir soruyu cevaplamak için — bu bir keşif "
             "aracıdır, bir cevap aracı değil]",
        girdi={},
        enjekte=("schema",),
        cikti="küp/ölçü/boyut envanteri (salt-okuma)",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        etiketler=("llmsiz", "kesif"),
        izin="query:run", makbuz=None,
        modul="app.katalog_metni", fonksiyon="envanter",
        notlar="🔴 `§14.16 E` ölçümüyle doğdu: `route`'un `required` alanları "
               "`['question','schema']` idi ve ŞEMA DÖNDÜREN HİÇBİR ARAÇ YOKTU — "
               "yani sıfırdan başlayan bir ajan merdivenin BİRİNCİ BASAMAĞINA hiç "
               "ulaşamıyordu. Envanter tek sahipten gelir (`katalog_metni.envanter`, "
               "`/stats/katalog` ile AYNI fonksiyon; `KAT-1`).",
    ),
    Arac(
        ad="report.compose",
        ozet="Çok bloklu bir raporu derler (kapak + yönetici özeti + kartlar + kaynaklar). "
             "[Erişim: blok başına CubeQuery] "
             "[Ne zaman: kullanıcı birden çok raporu tek belgede istediğinde] "
             "[NE ZAMAN KULLANILMAZ: tek bir soru için; blok sayısı tavanı aşarsa]",
        girdi={"spec": "rapor şartnamesi (başlık + bloklar)"},
        enjekte=("service", "schema"),
        cikti="sayfalanmış rapor + kaynak listesi",
        determinizm="deterministik", maliyet="pahali", yan_etki="yok",
        # ⚠ Aynı gerekçe (`kpi.resolve`): blok başına bir sorgu koşar.
        izin="contribution:scan", makbuz="contract_id",
        modul="app.report", fonksiyon="compose_report",
        notlar="Her blok kendi makbuzunu yazar; kaynak listesi `pages`'ten BAĞIMSIZDIR.",
        etiketler=("rapor",),
    ),
    Arac(
        ad="schedules.uyari_nedeni",
        ozet="Bir alarmın NEDENİNİ çıkarır: hangi segmentler ihlali sürüklüyor. "
             "[Erişim: alarm sonucu + segment satırları (PII maskeli)] "
             "[Ne zaman: bir eşik/anomali ihlali bildirilirken] "
             "[NE ZAMAN KULLANILMAZ: ihlal yokken; tıklanabilir sorgu üretmek için — "
             "bildirim gövdesi sorgu TAŞIMAZ]",
        # 🔴 ⟳ **BEYAN TAMAMEN YANLIŞTI.** İmza `uyari_nedeni(svc, cq, threshold)`;
        # ne `result` ne `measure` var. `svc` istek kapsamlı motordur → **enjekte**.
        girdi={"cq": "alarmın CubeQuery'si", "threshold": "eşik tanımı (JSON | None)"},
        enjekte=("svc",),
        cikti="maskeli neden satırları + kırpma notu",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.schedules", fonksiyon="uyari_nedeni",
        notlar="Etiketler PII-maskeli.",
        etiketler=("yorum", "bildirim"),
    ),
    Arac(
        ad="stats.trend",
        ozet="Bir serinin regresyon EĞİMİNİ ve uyumunu (r²) hesaplar. "
             "[Erişim: sayı dizisi — ham satır YOK] "
             "[Ne zaman: bir eğilimin YÖNÜ ve gücü sorulduğunda] "
             "[NE ZAMAN KULLANILMAZ: n<5'te (gürültüye yön atfetmek olur); bir "
             "p-değeri/anlamlılık iddiası için — üretmez]",
        girdi={"degerler": "sayı dizisi"},
        cikti="{egim, r2, yon, n} ya da None",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.stats", fonksiyon="trend",
        notlar="🔴 n<5 → None: dört noktaya doğru çizmek, gürültüye bir YÖN atfetmektir.",
        etiketler=("yorum", "istatistik"),
    ),
    Arac(
        ad="stats.ozet",
        ozet="Bir serinin n/ortalama/std/min/maks/medyan özetini verir. "
             "[Erişim: sayı dizisi — ham satır YOK] "
             "[Ne zaman: dağılımın şekli sorulduğunda] "
             "[NE ZAMAN KULLANILMAZ: boş seride (None döner); tek değeri 'ortalama' "
             "diye sunmak için]",
        girdi={"degerler": "sayı dizisi"},
        cikti="{n, ortalama, std, min, maks, medyan} ya da None",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None,
        modul="app.stats", fonksiyon="ozet",
        notlar="Medyan çift gözlemde iki ortanın ortalamasıdır (alt-orta YANLI olurdu).",
        etiketler=("yorum", "istatistik"),
    ),
)


def _yazma_araclari() -> tuple[Arac, ...]:
    """🔴 **FAZ 6.2 — YAZMA ARAÇLARI.** [bayrak: `yazma_araclari`]

    ## GERİ ALMA *"kapatmak"* DEĞİL, **HİÇ AÇMAMAK**

    Bayrak kapalıyken bu araçlar **kayda HİÇ girmez** — bir filtreyle gizlenmez, bir
    yetki kontrolüyle engellenmez, **var olmaz**.

    > *"Güvenlik imzadan değil, **yetki yüzeyinin genişlememesinden** geliyor."*

    Bir aracı kayda alıp sonra engellemek, o engelin bir gün unutulabileceği anlamına
    gelir. Kayda **hiç almamak** unutulamaz.

    ⚠ Bayrak `Settings`'ten okunur (`DIMA_YAZMA_ARACLARI`), feature-flag katmanından
    **değil**: araç kaydı **import zamanında** kurulur ve o an bir tenant/principal
    bağlamı **yoktur**. Bir kurulum kararını istek bağlamına bağlamak, kaydın istekten
    isteğe **değişmesi** demekti — ve o an *"ajan neyi çağırabilir"* sorusunun tek bir
    cevabı kalmazdı.
    """
    from app.config import get_settings

    try:
        acik = str(getattr(get_settings(), "yazma_araclari", "") or "").lower() in (
            "1", "true", "on", "yes")
    except Exception:                                        # noqa: BLE001
        acik = False
    if not acik:
        return ()

    # ⚠ **TUPLE DEĞİL FONKSİYON** — dairesel import gerekçesi (ölçüldü 2026-08-12):
    # `yazma_araclari` ÖNCE import edilirse, o modül burayı tetikler ve `YAZMA_KAYIT`
    # henüz **atanmamıştır** (`ImportError: partially initialized`). `_kurul()` ise
    # tanımlı olur — fonksiyon tanımları atamalardan önce çalışır. Uygulama yolunda
    # `tools` önce geldiği için kusur görünmüyordu; yani yalnız bir **sıralama**
    # sayesinde çalışıyordu.
    from app import yazma_araclari as _ya

    return _ya._kurul()


KAYIT = KAYIT + PLAN_ILKELLERI + KAYITSIZ_OLANLAR + _yazma_araclari()

_ARACLAR: dict[str, Arac] = {a.ad: a for a in KAYIT}


def kayitli_mi(ad: str) -> bool:
    """Ad `KAYIT`'ta var mı — `get()`'i istisna kontrolü için kullanmaya gerek yok.

    Denetim kaynaklı: makbuz üretimi *"bu ad kayıtlı mı"* sorusunu soruyor ve bunu
    `try/except KeyError` ile sormak, sorunun kendisini bir hata gibi gösteriyordu.
    """
    return ad in _ARACLAR


def get(ad: str) -> Arac:
    """Adıyla araç. Bilinmeyen ad = hata (fail-closed): planlayıcı araç UYDURAMAZ."""
    try:
        return _ARACLAR[ad]
    except KeyError:
        # 🔴 **ENVANTER SIZDIRILMAZ** (⟳ 08-12, denetim bulgusu). Eski mesaj
        # `Mevcut: {sorted(_ARACLAR)}` ile **31 aracın tamamını** basıyordu ve
        # `principal`'a göre **süzülmüyordu**. Bu metin `mcp.cagir`'ın hata dalından
        # geçip **ajana dönüyor**: `/mcp/tools`'u görmemesi gereken bir kullanıcı,
        # bilerek hatalı bir çağrıyla envanteri **sayabilirdi**.
        # ⚠ Bugün ürünsel etkisi yoktu (yalnız `owner` kullanılıyor, rol matrisi uykuda)
        # — ama matris açıldığı gün **sessiz** bir sızıntıya dönerdi. Sayı kalıyor
        # (geliştiriciye yararlı), **adlar gidiyor**.
        # *Bir hata mesajı, başaramadığı işlemin yetkisini taşımaz.*
        raise KeyError(
            f"Kayıtlı olmayan araç: {ad!r}. Kayıtta olmayan bir yetenek ajana AÇIK "
            f"DEĞİLDİR (bkz. app/tools.py). Kayıtta {len(_ARACLAR)} araç var; "
            "YETKİNE GÖRE SÜZÜLMÜŞ listeyi `tools/list` ile alın.") from None


def hepsi() -> tuple[Arac, ...]:
    return KAYIT


def izinli_araclar(principal) -> list[Arac]:
    """Bu kullanıcının çağırabileceği araçlar — **ajan kullanıcının yetkisini AŞAMAZ**.

    Yetki kaynağı `control_plane.authorize` matrisidir; burada ikinci bir kopya YOKTUR
    (UI'ın `permissions` listesiyle de aynı kaynak). Planlayıcıya verilen araç listesi
    bu fonksiyondan geçmelidir — aksi halde ajan, kullanıcının kendi eliyle
    yapamayacağı bir işi onun adına yapabilir.
    """
    from control_plane.authorize import can

    return [a for a in KAYIT if can(principal, a.izin)]


def deterministik_olanlar(etiket: str | None = None) -> list[Arac]:
    """Deterministik araçlar (isteğe bağlı etikete göre) — DETERMİNİSTİK-ÖNCE kuralının
    veri kaynağı: planlayıcı bir işi bunlardan biriyle yapabiliyorsa LLM aracı seçemez."""
    return [a for a in KAYIT
            if a.determinizm == "deterministik" and (etiket is None or etiket in a.etiketler)]


#: JSON-Schema karşılıkları. ⚠ Kapalı eşleme: bilinmeyen bir açıklama `"string"`e düşer
#: — **bugünkü davranış**, yani `KURAL B` anlamında geri adım yok.
_JSON_TIPI = {"list": "array", "dict": "object", "int": "integer",
              "float": "number", "bool": "boolean", "str": "string"}


def _json_tipi(arac: "Arac", alan: str) -> str:
    """Bir aracın `girdi` alanının **GERÇEK** JSON-Schema tipi.

    ## 🔴🔴 Neden var — ölçülmüş bir yayın kusuru (2026-08-12)

    Üretec her alanı **`"type": "string"`** ilan ediyordu. Ölçüldü (denetim ajanı +
    kendi ölçümüm): **31 aracın 77 alanının tamamı** `string` yayımlanıyordu, oysa
    gerçek imzalarda **`object` 31 · `array` 14 · `boolean` 7 · sayısal 5** var.

    Sonucu bir varsayım değil, canlı ölçüm:

        POST /mcp/call {"name":"stats.ozet","arguments":{"degerler":"[1,2,3]"}}
          ← ŞEMAYA UYUYOR  → isError:true (ValueError)
        POST /mcp/call {"name":"stats.ozet","arguments":{"degerler":[1,2,3,10]}}
          ← ŞEMAYI YOK SAYIYOR → 200 ✅

    Yani **sözleşmeye uyan çağrı düşüyor, uymayan çalışıyordu**; merdivenin birinci
    basamağı `route` bile MCP'den çağrılamıyordu. Bir ajan için yanlış bir şema,
    olmayan bir araçtan **kötüdür** — çünkü deneyip başarısız olur ve nedenini bilemez.

    > *Yanlış yayımlanmış bir sözleşme, hiç yayımlanmamış bir sözleşmeden kötüdür:
    > birincisine uyulur.*

    ⚠ Tip **`girdi` metninden değil GERÇEK İMZADAN** türetilir (`modul.fonksiyon` →
    `inspect.signature`). İmza çözülemezse (**4/31**) bugünkü `"string"`e düşer —
    sessiz bir geri adım değil, **ölçülmüş** bir kapsam.
    """
    import importlib
    import inspect

    try:
        fn = getattr(importlib.import_module(arac.modul), arac.fonksiyon, None)
        if fn is None:
            return "string"
        par = inspect.signature(fn).parameters.get(alan)
    except Exception:                                        # noqa: BLE001
        return "string"
    if par is None or par.annotation is inspect.Parameter.empty:
        return "string"
    ann = str(par.annotation)
    for anahtar, tip in _JSON_TIPI.items():
        if ann.startswith(anahtar) or ann.startswith(f"<class '{anahtar}'>"):
            return tip
    return "string"


def llm_araclari(principal=None) -> list[dict]:
    """LLM'e verilecek araç listesi — sağlayıcı-bağımsız JSON şeması.

    Anthropic/OpenAI tool-calling biçimlerine çevirmek çağıranın işidir; burada tek bir
    yansız temsil tutulur ki üç yüzey (LLM · MCP · UI) ayrışmasın.
    """
    araclar = izinli_araclar(principal) if principal is not None else list(KAYIT)
    return [
        {
            "name": a.ad,
            "description": (
                f"{a.ozet} [determinizm={a.determinizm} · maliyet={a.maliyet}"
                + (f" · makbuz={a.makbuz}" if a.makbuz else "")
                + "]"
                + (f" NOT: {a.notlar}" if a.notlar else "")
            ),
            "input_schema": {
                "type": "object",
                "properties": {k: {"type": _json_tipi(a, k), "description": v}
                               for k, v in a.girdi.items()},
                "required": list(a.girdi),
            },
        }
        for a in araclar
    ]


def okuyan_araclar(principal=None) -> list[dict]:
    """🔴 **SALT-OKUMA yüzeyleri için araç listesi** — `yan_etki != "yok"` olan HİÇBİR
    araç dönmez.

    ## Neden bu süzgeç var — ölçülmüş bir sızıntı

    2026-08-12'de ölçüldü: `yazma_araclari` bayrağı **açıkken** `KAYIT` 25 → **28** olur
    ve `mcp.araclar(None)` de **28** döndürüyordu — yani `dashboards.create` ·
    `schedules.create` · `measures.approve` **MCP yüzeyinde görünüyordu**.

    `§C3` kartının azaltma satırı *«salt-okuma; **yazma araçları kayıtta yok** (zaten
    öyle)»* diyor. Parantez kartın kendi kaydıydı ve **doğruydu** — ama bir güvence
    değil bir **rastlantıydı**: kayıtta yazan araç olmadığı için MCP salt-okumaydı.
    `§F13`'ün bayrağı açıldığı an o rastlantı bitiyor ve güvence **sessizce** ölüyordu.

    > *Bir sınırı bir rastlantının koruması, o sınırın hiç konmamış olmasıdır — çünkü
    > rastlantı değişince kimse haberdar olmaz.*

    ## `KAT-1` — ikinci bir süzgeç DEĞİL

    Yetki süzgeci burada **yeniden yazılmıyor**: `llm_araclari(principal)` çağrılıyor ve
    o zaten `izinli_araclar()` → `authorize()` matrisine bağlı. Buraya eklenen tek şey
    **kaydın kendi beyan ettiği** `yan_etki` alanına bakan bir eleme. Yani otorite yine
    kaydın kendisidir; bu fonksiyon bir **karar** vermiyor, beyanı **uyguluyor**.
    """
    yazanlar = {a.ad for a in KAYIT if a.yan_etki != "yok"}
    return [a for a in llm_araclari(principal) if a["name"] not in yazanlar]
