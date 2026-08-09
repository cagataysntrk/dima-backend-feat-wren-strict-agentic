"""PLAN ŞEMASI — orkestratörün **kapalı fiil kümesi** (FAZ O-2, ikinci yarı).

## Neden bir şema, neden kapalı

Rapor bu kararı taşıyıcı kolon ilan ediyor ve gerekçesi keskin:

> Serbest plan **yasak**. Açık bırakılırsa plan üreten LLM, SQL üreten LLM'den **daha az**
> denetlenebilir olur — çünkü hatası birkaç adım sonra, **birleşik sonuçta** ortaya çıkar
> ve hangi adımdan geldiği görünmez.

⊙ Discovery'nin tehlikesi LLM olması değil, **ham SQL'in denetlenemez** olmasıydı. Bir
plan denetlenebilir kalır **ancak** fiilleri sonluysa ve her adım aynı beyaz listeden
geçiyorsa. Bu dosya o sonluluğu **şema düzeyinde** kurar: model kelime uyduramaz, çünkü
`enum` dışına çıkamaz.

## 🔴 `cube_query` ŞEMASI YENİDEN YAZILMIYOR — ÇAĞRILIYOR

`SORGU` fiilinin gövdesi `intent_semasi.cube_query_json_schema`'dır. İkinci bir kopya
yazmak, katalog değişince **birinin bayatlaması** demekti — bu deponun `KAT-1` sınıfı.
*Bir şemayı iki yerde tanımlamak, iki farklı katalogla koşmaya razı olmaktır.*

## ⚠ NE YAPMIYOR — sınırı yazılı

Bu dosya bir **sözleşmedir**, bir çalıştırıcı değil. Hiçbir şeyi koşturmaz, hiçbir LLM
çağırmaz. Şemayı **tüketen** taraf (`plan_kur` + çalıştırıcı) kendi faziyla, kendi
bayrağıyla gelir — ve o gelene kadar bu dosya **ölü ağırlık değil, ölçülebilir bir
sözleşmedir**: geçerli/geçersiz plan örnekleriyle sınanabilir.

⚠ `KURAL B`: hiçbir yol bu şemayı bugün okumuyor; davranış **bayt bayt** bugünkü.

*Bir sözleşmeyi önce yazıp sonra bağlamak, ikisini birden yapmaktan daha az risklidir.*
"""

from __future__ import annotations

from typing import Any

#: 🔴 **KAPALI FİİL KÜMESİ — ve TEK SAHİPLİ.** Yenisini plan **icat edemez** (`enum` bunu
#: şema düzeyinde engeller). Her fiilin gövdesi **zaten var olan** bir modüldür; bu küme
#: yeni bir motor açmaz, var olanları **birbirine geçirir**.
#:
#: ⚠ Bu sözlük bir belge değil, **kaynağın kendisidir**: hem `FIILLER` hem modele giden
#: istem (`plan_sistem_metni`) buradan türer. Fiil listesini bir yerde, o fiillerin
#: modele anlatımını başka yerde tutmak `KAT-1`'in ta kendisiydi — bir fiil eklendiğinde
#: **birinin bayatlaması** demekti. *Bir kümeyi tarif eden metin, kümeden üretilmiyorsa
#: er ya da geç onu yanlış tarif eder.*
#:
#: | fiil | gövde | durum |
#: |---|---|---|
#: | `SORGU` | `wren_service.cube_sql` | ✅ |
#: | `KIYASLA` | `contribution._akran_kiyasi` | ✅ (`§AA1`) |
#: | `AYRISTIR` | `contribution.arastir` | ✅ |
#: | `BAGLA` | `ilkeller.bagla` | ✅ (`O-1`) |
#: | `HESAPLA` | `ilkeller.hesapla` | ✅ (`O-1`) |
#: | `TREND` | `yoy.compute` | ✅ |
#: | `ANLAT` | `answer.narration_guard` | ✅ |
FIIL_ANLAMI: dict[str, str] = {
    "SORGU": "katalogdan veri çeker — gövdesi bugünkü cube sorgusunun ta kendisidir",
    "KIYASLA": "bir varlığı akranlarıyla karşılaştırır (ortalamadan sapma)",
    "AYRISTIR": "bir toplamı bileşenlerine ayırır (hangi kalem ne kadar katkı verdi)",
    "BAGLA": "satırlar arasından bir varlık SEÇER — «en kötü hangisi» sorusunun cevabı",
    "HESAPLA": "seçilmiş varlığın akran ortalamasına göre farkını çıkarır",
    "TREND": "aynı ölçüyü önceki dönemle karşılaştırır",
    "ANLAT": "bulguları cümleye çevirir — YALNIZ son adım olabilir",
    # ⟳ `FAZ 7` — KÖK-NEDEN İNİŞİ. Üçü de **yeni kod değil**: `drill.py` bu gezintiyi
    # zaten yapıyordu, ama her adımı **kullanıcının tıklaması** tetikliyordu. Plana
    # açılınca aynı gezinti bir **zincir** olur — ve derinlik plan uzunluğuyla sınırlı
    # kalır, yani **döngü eklemeden** derinleşme. *Bir döngü eklemeden derinleşmenin
    # yolu, derinliği plana yazdırmaktır.*
    "KIR": "bir sorguya kırılım boyutu EKLER — çıktısı satır değil, yeni bir SORGU",
    "SUZ": "bir sorguyu tek bir kategoriye daraltır — çıktısı yeni bir SORGU",
    "BOYUTSEC": "hangi boyutun farkı en çok AÇIKLADIĞINI sıralar",
    # ⟳ `FAZ 7b` — KARAR MATRİSİ. ⚠ Bir *karar* matrisi değil bir **karşılaştırma**
    # tablosudur: ölçütler katalogda VAR OLAN ölçülerdir, ağırlık YOKTUR.
    "MATRIS": "adayları ölçütlerle yan yana koyar (satır=aday, sütun=ölçüt)",
    "SIRALA": "adayları çok ölçütle sıralar — ağırlık YOK, hepsi EŞİT",
    # ⟳ `FAZ 7c` — RAPOR. ⚠ Hiçbir şey hesaplamaz, koşmuş bölümleri **dizer**.
    "RAPOR": "koşmuş bölümleri tek bir belgeye dizer",
    "GORSEL": "bir bölüm için grafik kararı üretir (deterministik, LLM YOK)",
    # ⟳ `FAZ 7d` — PANO. 🔴 **YAZMAZ**: yalnız taslak üretir; kalıcılaştırma onayla.
    "PANO": "sorgulardan bir pano TASLAĞI kurar — hiçbir şey kaydetmez",
}

FIILLER: tuple[str, ...] = tuple(FIIL_ANLAMI)

#: 🔴 **HER FİİLİN ZORUNLU ALANLARI — TEK SAHİP.** Hem şema (`required`) hem serbest-JSON
#: doğrulaması (`plan_garson._plani_oku`) buradan okur.
#:
#: ⚠ Ölçüldü (`EE` turu, canlı, serbest-JSON sağlayıcı): şema uygulanamayan bir sağlayıcıda
#: model **fiil adını doğru, parametrelerini uydurma** yazıyor —
#: `{"fiil":"SORGU"}` (`cube_query` YOK) · `{"fiil":"AYRISTIR","ozellik":…,"detay":…}`.
#: Yalnız fiil adına bakan bir doğrulama bunları **plan sanıyordu** ve çalıştırıcı
#: `KeyError` ile düşüyordu. *Bir sözleşmenin adını doğrulamak, sözleşmeyi doğrulamak
#: değildir.*
ZORUNLU_ALANLAR: dict[str, tuple[str, ...]] = {
    "SORGU": ("cube_query",),
    "BAGLA": ("kaynak", "boyut", "olcu"),
    "HESAPLA": ("kaynak", "hedef", "boyut", "olcu"),
    "KIYASLA": ("kaynak",),
    "AYRISTIR": ("kaynak",),
    "TREND": ("kaynak",),
    "ANLAT": ("kaynaklar",),
    "KIR": ("cube_query", "boyut"),
    "SUZ": ("cube_query", "boyut", "deger"),
    "BOYUTSEC": ("kaynak",),
    "MATRIS": ("kaynaklar", "boyut"),
    "SIRALA": ("kaynak", "boyut", "olculer"),
    "RAPOR": ("kaynaklar", "baslik"),
    "GORSEL": ("kaynak", "cube_query"),
    "PANO": ("kaynaklar", "baslik"),
}

#: 🔴 **HER FİİLİN ÇIKTI TİPİ — beyan edilir, tahmin edilmez.**
#:
#: ⚠ Bu beyan olmadan bir plan **koşmadan doğrulanamaz**: `HESAPLA.hedef` bir *varlık*
#: bekler, ama `$2` bir `SORGU` adımını gösteriyorsa oraya **satırlar** gider ve kusur
#: ancak `ilkeller.hesapla` içinde, koşum anında, üstelik önceki `SORGU` motora çoktan
#: gitmişken bulunur.
#:
#: Tipler bilinçli olarak **beş** tanedir; genişlemesi bir tasarım kararıdır:
#:   `satirlar` (list[dict]) · `varlik` ((ad, deger)) · `olcum` (dict[str, sayı]) ·
#:   `bulgular` (ayrıştırma raporu) · `metin` (str)
#:
#: *Bir zinciri koşmadan denetlemenin bedeli, halkalarının neye benzediğini yazmaktır.*
CIKTI_TIPI: dict[str, str] = {
    "SORGU": "satirlar",
    # 🔴 `KIR`/`SUZ` **satır üretmez, SORGU üretir** — ve bu ayrım kök-neden inişinin
    # bütün mekanizmasıdır: bir adım bir sorgu üretir, sonraki adım onu **koşar**.
    # Tip sistemi olmasaydı `BAGLA($kir)` bir `cube_query` sözlüğünü satır sanardı.
    "KIR": "sorgu",
    "SUZ": "sorgu",
    "BOYUTSEC": "bulgular",
    "MATRIS": "satirlar",
    "SIRALA": "satirlar",
    "RAPOR": "bulgular",
    "GORSEL": "bulgular",
    "PANO": "bulgular",
    "TREND": "satirlar",      # dönem kaydırılmış satırlar — hâlâ satır
    "BAGLA": "varlik",
    "HESAPLA": "olcum",
    "KIYASLA": "olcum",
    "AYRISTIR": "bulgular",
    "ANLAT": "metin",
}

#: Hangi alan hangi tipi bekler. `None` = **her tip kabul** (`ANLAT` her bulguyu anlatır).
#: ⚠ Yalnız **referans taşıyan** alanlar burada; `boyut`/`olcu` gibi sabit alanlar şemanın
#: `enum`'uyla zaten kısıtlı.
GIRDI_TIPI: dict[str, dict[str, str | None]] = {
    "BAGLA": {"kaynak": "satirlar"},
    "HESAPLA": {"kaynak": "satirlar", "hedef": "varlik"},
    "KIYASLA": {"kaynak": "satirlar"},
    "AYRISTIR": {"kaynak": "satirlar"},
    "TREND": {"kaynak": "satirlar"},
    "ANLAT": {"kaynaklar": None},
    "KIR": {"cube_query": "sorgu"},     # ⚠ referanssa bir SORGU olmalı; inline da olabilir
    "SUZ": {"cube_query": "sorgu"},
    "BOYUTSEC": {"kaynak": "bulgular"},
    "MATRIS": {"kaynaklar": "satirlar"},
    "SIRALA": {"kaynak": "satirlar"},
    "RAPOR": {"kaynaklar": "satirlar"},
    "GORSEL": {"kaynak": "satirlar"},
    # 🔴 Widget'lar **satır değil SORGU** taşır: satır kaydetmek bir fotoğraf, sorgu
    # kaydetmek bir pano yapar.
    "PANO": {"kaynaklar": "sorgu"},
}

#: 🔴 Yalnız **son** adım olabilen fiiller. Şema bunu ifade EDEMEZ (`oneOf` konum bilmez);
#: bugüne kadar yalnız istemde yazılıydı, yani **denetlenmiyordu**.
SON_ADIM_FIILLERI: frozenset[str] = frozenset({"ANLAT"})

#: Adım referansı: `$1` = birinci adımın çıktısı. **Tek biçim, tek anlam.**
#: ⚠ Serbest bir ifade dili DEĞİL: `$` + sayı. Bir plan aritmetik yazamaz, koşul yazamaz,
#: döngü kuramaz. *Bir referans dilini genişletmek, onu bir programlama diline çevirir —
#: ve o dilin denetimi artık şemada değil, yorumlayıcıdadır.*
ADIM_REFERANSI = r"^\$[1-9][0-9]?$"


def plan_json_schema(index: dict, *, azami_adim: int = 5) -> dict[str, Any]:
    """Plan için **şema-kısıtlı** JSON sözleşmesi üretir.

    `index`: `katalog_metni.metin_ve_indeks`'in ürettiği beyaz liste — **aynı** indeks.
    `azami_adim`: `E9`'un karşı önlemi. Plan uzunluğu bir **ölçüdür**: tek adımlık bir
    soruya beş adımlık plan kurulursa cevap yanlış olmaz ama **pahalı** olur ve `E6`'nın
    kapısına takılır. Şema burada sert bir tavan koyar.

    ⚠ `SORGU` fiilinin gövdesi `intent_semasi`'den **çağrılır**, kopyalanmaz.
    """
    from app.intent_semasi import cube_query_json_schema

    cq = cube_query_json_schema(index)
    boyutlar = sorted({d for spec in (index or {}).values()
                       for d in (spec.get("dimensions") or [])})
    olculer = sorted({m for spec in (index or {}).values()
                      for m in (spec.get("measures") or [])})

    def _ref(aciklama: str) -> dict:
        return {"type": "string", "pattern": ADIM_REFERANSI, "description": aciklama}

    def _ref_listesi(aciklama: str) -> dict:
        """🔴 **REFERANS DİLİNİN TEK VE BİLİNÇLİ GENİŞLEMESİ.**

        Bir anlatı — ve `FAZ 7`'nin rapor/pano/matris fiilleri — **birden çok** adımın
        çıktısına dayanır. Tek referansla bunu ifade etmenin yolu yok.

        ⚠ Genişleyen şey **çokluk**, ifade gücü değil: hâlâ aritmetik yok, koşul yok,
        alan erişimi yok. `["$1","$3"]` bir listedir, bir ifade değil. *Bir referans
        dilini genişletmek, onu bir programlama diline çevirmenin ilk adımıdır — o yüzden
        genişleme çokluğa kadar, oraya kadar.*
        """
        return {"type": "array", "minItems": 1, "maxItems": azami_adim,
                "items": _ref(aciklama), "description": aciklama}

    #: Her fiil kendi **zorunlu** alanlarını taşır — bir fiili parametresiz yazmak
    #: `B1`'in ta kendisiydi (*"parametresiz bir plan bir zincir değil bir sıralamadır"*).
    dallar: list[dict] = [
        # 🔴 `FAZ 7` — `cube_query` artık **inline bir nesne YA DA bir `$n` referansı**
        # olabilir. Kök-neden inişinin halkası budur: `KIR` bir sorgu üretir, `SORGU`
        # onu koşar. ⚠ Genişleyen şey yine **çokluk değil yön**: referans dili aynı
        # kaldı (`$n`), yalnız hangi alanda durabileceği genişledi.
        {"type": "object", "additionalProperties": False, "title": "SORGU",
         "properties": {"fiil": {"const": "SORGU"},
                        "cube_query": {"oneOf": [cq, _ref("koşulacak sorguyu üreten adım")]}},
         "required": ["fiil", *ZORUNLU_ALANLAR["SORGU"]]},
        {"type": "object", "additionalProperties": False, "title": "BAGLA",
         "properties": {"fiil": {"const": "BAGLA"},
                        "kaynak": _ref("hangi adımın satırları"),
                        "boyut": {"type": "string", "enum": boyutlar} if boyutlar
                                 else {"type": "string"},
                        "olcu": {"type": "string", "enum": olculer} if olculer
                                else {"type": "string"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["BAGLA"]]},
        {"type": "object", "additionalProperties": False, "title": "HESAPLA",
         "properties": {"fiil": {"const": "HESAPLA"},
                        "kaynak": _ref("hangi adımın satırları"),
                        "hedef": _ref("hangi adımın seçtiği varlık"),
                        "boyut": {"type": "string", "enum": boyutlar} if boyutlar
                                 else {"type": "string"},
                        "olcu": {"type": "string", "enum": olculer} if olculer
                                else {"type": "string"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["HESAPLA"]]},
        {"type": "object", "additionalProperties": False, "title": "KIYASLA",
         "properties": {"fiil": {"const": "KIYASLA"},
                        "kaynak": _ref("hangi adımın satırları")},
         "required": ["fiil", *ZORUNLU_ALANLAR["KIYASLA"]]},
        {"type": "object", "additionalProperties": False, "title": "AYRISTIR",
         "properties": {"fiil": {"const": "AYRISTIR"},
                        "kaynak": _ref("hangi adımın satırları")},
         "required": ["fiil", *ZORUNLU_ALANLAR["AYRISTIR"]]},
        {"type": "object", "additionalProperties": False, "title": "TREND",
         "properties": {"fiil": {"const": "TREND"},
                        "kaynak": _ref("hangi adımın satırları")},
         "required": ["fiil", *ZORUNLU_ALANLAR["TREND"]]},
        {"type": "object", "additionalProperties": False, "title": "KIR",
         "properties": {"fiil": {"const": "KIR"},
                        "cube_query": {"oneOf": [cq, _ref("kırılacak sorgu")]},
                        "boyut": {"type": "string", "enum": boyutlar} if boyutlar
                                 else {"type": "string"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["KIR"]]},
        {"type": "object", "additionalProperties": False, "title": "SUZ",
         "properties": {"fiil": {"const": "SUZ"},
                        "cube_query": {"oneOf": [cq, _ref("daraltılacak sorgu")]},
                        "boyut": {"type": "string", "enum": boyutlar} if boyutlar
                                 else {"type": "string"},
                        "deger": {"type": "string",
                                  "description": "kullanıcının YAZDIĞI ya da bir adımın "
                                                 "SEÇTİĞİ kategori"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["SUZ"]]},
        {"type": "object", "additionalProperties": False, "title": "BOYUTSEC",
         "properties": {"fiil": {"const": "BOYUTSEC"},
                        "kaynak": _ref("hangi adımın ayrıştırma raporu")},
         "required": ["fiil", *ZORUNLU_ALANLAR["BOYUTSEC"]]},
        {"type": "object", "additionalProperties": False, "title": "MATRIS",
         "properties": {"fiil": {"const": "MATRIS"},
                        "kaynaklar": _ref_listesi("hangi adımların satırları"),
                        "boyut": {"type": "string", "enum": boyutlar} if boyutlar
                                 else {"type": "string"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["MATRIS"]]},
        # 🔴 `agirliklar` diye bir alan **YOK** ve olmayacak: bir ağırlık bir SAYIDIR ve
        # modele sayı yazdırmak, `«sayıyı her zaman küp koyar»` ilkesini arka kapıdan
        # deler. Ağırlıklar **eşittir** ve bu bir varsayım değil bir **beyandır**.
        {"type": "object", "additionalProperties": False, "title": "SIRALA",
         "properties": {"fiil": {"const": "SIRALA"},
                        "kaynak": _ref("sıralanacak satırlar"),
                        "boyut": {"type": "string", "enum": boyutlar} if boyutlar
                                 else {"type": "string"},
                        "olculer": {"type": "array", "minItems": 1,
                                    "items": ({"type": "string", "enum": olculer}
                                              if olculer else {"type": "string"}),
                                    "description": "hangi ölçütlere göre sıralanacak"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["SIRALA"]]},
        {"type": "object", "additionalProperties": False, "title": "RAPOR",
         "properties": {"fiil": {"const": "RAPOR"},
                        "kaynaklar": _ref_listesi("rapora girecek bölümler"),
                        "baslik": {"type": "string"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["RAPOR"]]},
        # ⚠ Grafik kararı **modele sorulmaz**: `viz.recommend` deterministik (ADR-0024).
        # Fiilin işi *"hangi grafik"* demek değil, *"bu bölüme bir grafik kararı üret"*.
        {"type": "object", "additionalProperties": False, "title": "GORSEL",
         "properties": {"fiil": {"const": "GORSEL"},
                        "kaynak": _ref("grafiği çizilecek bölüm"),
                        "cube_query": {"oneOf": [cq, _ref("bölümü üreten sorgu")]}},
         "required": ["fiil", *ZORUNLU_ALANLAR["GORSEL"]]},
        {"type": "object", "additionalProperties": False, "title": "PANO",
         "properties": {"fiil": {"const": "PANO"},
                        "kaynaklar": _ref_listesi("panoya girecek SORGULAR"),
                        "baslik": {"type": "string"}},
         "required": ["fiil", *ZORUNLU_ALANLAR["PANO"]]},
        {"type": "object", "additionalProperties": False, "title": "ANLAT",
         "properties": {"fiil": {"const": "ANLAT"},
                        "kaynaklar": _ref_listesi("hangi adımların bulguları")},
         "required": ["fiil", *ZORUNLU_ALANLAR["ANLAT"]]},
    ]
    return {
        "type": "object", "additionalProperties": False,
        "properties": {
            "adimlar": {"type": "array", "minItems": 1, "maxItems": azami_adim,
                        "items": {"type": "object", "oneOf": dallar}}},
        "required": ["adimlar"],
    }


def plan_sistem_metni(catalog: str) -> str:
    """Garsona **plan** dilini öğreten istem — fiil listesi `FIIL_ANLAMI`'ndan **üretilir**.

    ⚠ Elle yazılmış bir fiil listesi burada olsaydı, `FIILLER`'e bir fiil eklendiğinde
    model onu **hiç öğrenmezdi** ve kusur ancak canlıda, *"neden bu fiili hiç kullanmıyor"*
    biçiminde görünürdü. `KAT-1`'in en sinsi türü budur: iki sahip **çelişmez**, biri
    yalnızca **eksik** kalır.

    🔴 Ve istem, şemanın söylediğini **tekrar etmez, gerekçelendirir**: şema neyin
    yazılabileceğini kısıtlar (`enum`), istem *ne zaman* yazılacağını anlatır. İkisi
    çakışsaydı biri gereksiz olurdu.
    """
    _fiiller = "\n".join(f"- {f}: {a}" for f, a in FIIL_ANLAMI.items())
    return (
        "Bir soruyu, YÖNETİLEN semantik katman üzerinde koşacak ADIMLARA ayırırsın.\n"
        "Yalnızca aşağıdaki cube'lar, ölçüler ve boyutlar VARDIR:\n\n" + catalog + "\n\n"
        "Kullanabileceğin TEK fiil kümesi (başka fiil YOKTUR):\n" + _fiiller + "\n\n"
        "Kurallar:\n"
        '- SADECE JSON döndür: {"adimlar":[{"fiil":"...", ...}]}\n'
        "- 🔴 SORU TEK ADIMLA CEVAPLANIYORSA TEK ADIM YAZ. Plan uzunluğu bir maliyettir; "
        "gereksiz adım cevabı iyileştirmez, yalnız yavaşlatır.\n"
        "- Bir adım, önceki bir adımın çıktısına `$1` `$2` biçiminde işaret eder. "
        "İLERİ referans YOKTUR: `$3` ancak dördüncü adımda yazılabilir.\n"
        "- Aritmetik, koşul, döngü YAZAMAZSIN. Yalnız fiiller ve adım referansları.\n"
        "- Tarih YAZMA: dönemi `period_expr` alanına kullanıcının kendi ifadesiyle "
        "(sistemin diline çevirerek) koy; tarihi Python hesaplar.\n"
        "- Katalogda karşılığı olmayan bir adım UYDURMA: o adımı hiç yazma."
    )


def tek_adimli(plan: dict | None) -> dict | None:
    """🔴 **TEK ADIMLI BİR PLAN, ZATEN BUGÜNKÜ `CubeQuery`'DİR.**

    `E6`'nın düzeltilmiş hâlinin kod karşılığı: `plan_kur` `select_cube`'un **yerine**
    geçtiğinde, basit sorular için çıktı **bire bir aynı** olmalı. Bu fonksiyon o
    denkliği kurar — plan tek `SORGU` adımından ibaretse `cube_query`'sini döndürür.

    ⊙ Böylece geçiş bir **davranış değişikliği** değil, bir **temsil genişlemesi** olur:
    bugünkü yol planın **özel hâlidir**, alternatifi değil.

    ⚠ Çok adımlıysa `None` — çağıran o zaman gerçek çalıştırıcıya gider.
    """
    adimlar = (plan or {}).get("adimlar") or []
    if len(adimlar) == 1 and adimlar[0].get("fiil") == "SORGU":
        return adimlar[0].get("cube_query")
    return None
