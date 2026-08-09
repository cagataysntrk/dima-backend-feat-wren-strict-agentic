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
        ozet="Türkçe soruyu SIFIR LLM ile bir CubeQuery'ye çözer; çözemezse None döner. [Erişim: yalnız KATALOG (ölçü/boyut adları) — ham veri YOK] [Ne zaman: her soruda İLK basamak] [NE ZAMAN KULLANILMAZ: takip mesajlarında (o `deterministic_refine`'ın işi); bir cevabın ÜSTÜNDE konuşurken]",
        girdi={"question": "kullanıcının sorusu (ham metin)",
               "schema": "cube kataloğu (WrenService.schema())"},
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
        girdi={"prev": "önceki cube_query", "q": "normalize edilmiş takip sorusu",
               "schema": "cube kataloğu"},
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
        ozet="Aynı raporu önceki dönemle (yıl ya da ay) hizalayıp kıyas kolonları ekler. [Erişim: CubeQuery + zaman boyutu] [Ne zaman: 'geçen yıla/aya göre' istendiğinde] [NE ZAMAN KULLANILMAZ: çok-yıl veri yoksa; zaman boyutu olmayan cube'da]",
        girdi={"service": "WrenService", "cq": "CubeQuery", "mode": "'yoy' | 'mom'",
               "time_dim": "zaman boyutu adı", "limit": "satır üst sınırı"},
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
        ozet="KULLANILMAYAN boyutları tarar, değişimi ayrıştırır, açıklayıcılığa göre sıralar. [Erişim: kullanılmayan boyutlar + iki dönem] [Ne zaman: hangi kırılımın açıkladığı BİLİNMEDİĞİNDE] [NE ZAMAN KULLANILMAZ: pahalıdır (boyut başına sorgu) — kırılım belliyse `contribution.decompose` yeter]",
        girdi={"service": "WrenService", "schema": "cube kataloğu", "cube_query": "kaynak CubeQuery",
               "mode": "yoy|mom", "kind": "segment|pvm", "max_dimensions": "tarama sınırı"},
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
        ozet="Sonucun doğru görselleştirmesini DETERMİNİSTİK seçer (Show-Me/Cleveland-McGill). [Erişim: sonuç + cube metadata (birim/additive)] [Ne zaman: sonuç dolu olduğunda] [NE ZAMAN KULLANILMAZ: grafik türünü LLM'e SEÇTİRMEK için — karar deterministiktir (ADR-0024)]",
        girdi={"result": "sorgu sonucu", "cube_query": "CubeQuery",
               "cube_meta": "semantik metadata (units, lower_is_better…)"},
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
        girdi={"prev": "mevcut CubeQuery", "q": "kullanıcının sorusu",
               "schema": "cube kataloğu"},
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
               "ek": "beyan edilmiş ek türetmeler (ör. yeni bir metriğin ara değerleri)"},
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
KAYITSIZ_OLANLAR: tuple[Arac, ...] = (
    Arac(
        ad="prescribe.recete",
        ozet="Sinyallerden aksiyon reçetesi üretir (seçenekler + gerekçe). "
             "[Erişim: hesaplanmış sinyaller — ham veri YOK] "
             "[Ne zaman: 'ne yapmalıyız?' türü bir soruda] "
             "[NE ZAMAN KULLANILMAZ: sinyal yokken (reçete uydurur); bir SAYI sorusuna "
             "cevap olarak]",
        girdi={"signals": "sinyal listesi (JSON)", "cube_query": "bağlam CubeQuery"},
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
        ad="report.compose",
        ozet="Çok bloklu bir raporu derler (kapak + yönetici özeti + kartlar + kaynaklar). "
             "[Erişim: blok başına CubeQuery] "
             "[Ne zaman: kullanıcı birden çok raporu tek belgede istediğinde] "
             "[NE ZAMAN KULLANILMAZ: tek bir soru için; blok sayısı tavanı aşarsa]",
        girdi={"spec": "rapor şartnamesi (başlık + bloklar)"},
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
        girdi={"result": "alarm sonucu", "measure": "ölçü adı"},
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

    from app.yazma_araclari import YAZMA_KAYIT

    return YAZMA_KAYIT


KAYIT = KAYIT + KAYITSIZ_OLANLAR + _yazma_araclari()

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
        raise KeyError(
            f"Kayıtlı olmayan araç: {ad!r}. Kayıtta olmayan bir yetenek ajana AÇIK DEĞİLDİR "
            f"(bkz. app/tools.py). Mevcut: {sorted(_ARACLAR)}") from None


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
                "properties": {k: {"type": "string", "description": v}
                               for k, v in a.girdi.items()},
                "required": list(a.girdi),
            },
        }
        for a in araclar
    ]
