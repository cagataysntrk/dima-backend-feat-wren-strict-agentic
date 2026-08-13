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

#: 🔴🔴 `§64` — **AYNI FİİLİN İKİNCİ KİPİ: ÖNİZLEME SATIRI** 🅔.
#:
#: `FIIL_ANLAMI` bir **tanımdır** ve okuru geliştiricidir: *«KIR — bir sorguya kırılım
#: boyutu EKLER — çıktısı satır değil, yeni bir SORGU»*. O cümledeki son yarı bir
#: **kısıttır**, bir açıklama değil; makbuzda (geriye dönük, tanı için) yerindedir.
#:
#: Ama `§28.3` önizlemesinin okuru **kullanıcıdır** ve verdiği şey bir **karardır**
#: (*«kullanıcı KARARI VERİR — bir tık»*, `§3.1`). Bir kararın önüne konan cümle,
#: kararın **sonucunu** söylemelidir: *«makine kırılımı ekler»*. Ölçüldü (canlı `s25`):
#: önizlemede beş satırın **üçü** iç kısıt cümlesiydi (*«YALNIZ son adım olabilir»*).
#:
#: ⚠ Bu **ikinci bir sahip değildir**: sözlük yine burada, yine tek kayıt, yalnız iki
#: **kipi** var (`KAT-1` korunur). İkisini iki dosyaya bölmek bir sahip ikilemesi olurdu.
#: ⚠ **`{boyut}` bir yuvadır, bir biçimlendirme değil**: Türkçe eki cümlenin **içinde**
#: durur (*«makine kırılımı ekler»*) ve onu dışarıdan iliştirmeye çalışmak bu deponun
#: `§18.8`'de yazılı morfoloji tuzağıdır. Adımda boyut yoksa yuva **cümleden düşer**.
#: ⚠ **Payda kutsaldır** 🅜: `test_plan_semasi` her fiilin burada bir karşılığı olmasını
#: şart koşar — bir fiil eklenip önizleme kipi unutulursa kullanıcı **boş satır** görür.
FIIL_ONIZLEME: dict[str, str] = {
    "SORGU": "veriyi çeker",
    "KIYASLA": "akran ortalamasıyla karşılaştırır",
    "AYRISTIR": "toplamı bileşenlerine ayırır",
    "BAGLA": "en dikkat çeken varlığı seçer",
    "HESAPLA": "akrandan farkı hesaplar",
    "TREND": "önceki dönemle karşılaştırır",
    "ANLAT": "bulguları cümleye çevirir",
    "KIR": "{boyut} kırılımı ekler",
    "SUZ": "{boyut} kategorisine daraltır",
    "BOYUTSEC": "farkı en çok açıklayan boyutu bulur",
    "MATRIS": "adayları ölçütlerle yan yana koyar",
    "SIRALA": "adayları çok ölçütle sıralar",
    "RAPOR": "bölümleri tek belgeye dizer",
    "GORSEL": "grafik kararını üretir",
    "PANO": "pano taslağı kurar",
}
#: 🔴🔴 `§D6`/`§C1` — **FİİL KÜMESİ ARTIK YETENEK KAYDINDAN TÜRETİLİYOR.**
#:
#: ## Raporun isteği ve `C1`'in koyduğu şart
#:
#: > *«`FIIL_ANLAMI` `tools.py`'den üretilir; kapalı `enum` korunur — yalnız artık
#: > türetilmiş olur. Kazanç: tek kayıt (`KAT-1`).»*
#:
#: `C1` kartı bunu **üç ölçülmüş gerekçeyle** ertelemişti ve üçüncüsü şuydu: *«adlar
#: örtüşmediği için türetim bir EŞLEME TABLOSU ister — iki kayıt yerine ÜÇ şey»*.
#: O şart artık **karşılandı**: eşleme ayrı bir tabloda değil, her **aracın kendi
#: beyanında** duruyor (`tools.Arac.fiil`), ve kayıt tamamlandı — planın 15 fiilinin
#: 15'i de bir aracın gövdesi (önce **altısı kayıtta hiç yoktu**).
#:
#: ## ⚠ Neden METİNLER hâlâ burada — ve bu bir yarım iş DEĞİL
#:
#: Araç `ozet`leri planlayıcı için değil **MCP/araç seçimi** için yazılmış uzun
#: metinlerdir (`[Erişim: …] [Ne zaman: …] [NE ZAMAN KULLANILMAZ: …]`). Onları plan
#: istemine dökmek istemi birkaç kat büyütür ve **davranışı değiştirir** — `KURAL B`'nin
#: yasakladığı şey tam da bu. Bu yüzden ayrım şöyle kuruldu:
#:
#:   · **HANGİ fiiller var** → yetenek kaydı karar verir (tek sahip, `KAT-1`)
#:   · **Plan istemindeki cümle** → burada durur (kullanıcıya/modele bakan yüzey)
#:
#: 🔴 Ve ayrışma **imkânsız**: aşağıdaki denetim **içe aktarma anında** koşar. Bir fiil
#: eklenip aracı yazılmazsa (ya da tersi) uygulama **ayağa kalkmaz** — sessizce
#: kaymaz.
#:
#: *Bir türetimin amacı metni kopyalamak değil, iki listenin ayrışmasını imkânsız
#: kılmaktır.*
def _fiilleri_kayittan_dogrula() -> tuple[str, ...]:
    """Yetenek kaydındaki fiil beyanlarıyla `FIIL_ANLAMI` **aynı kümeyi** taşımalı."""
    from app import tools as _t

    beyan = {a.fiil for a in _t.KAYIT if a.fiil}
    yazili = set(FIIL_ANLAMI)
    if beyan != yazili:
        raise RuntimeError(
            "🔴 `KAT-1` ihlali — plan fiilleri ile yetenek kaydı AYRIŞTI.\n"
            f"  kayıtta beyanlı ama plan şemasında yok: {sorted(beyan - yazili)}\n"
            f"  plan şemasında var ama hiçbir araç beyan etmiyor: {sorted(yazili - beyan)}\n"
            "Her plan fiili bir aracın gövdesidir; aracı `fiil=\"...\"` ile beyan etmeli.")
    # ⚠ Sıra **buradan** gelir, kayıttan değil: istem metninin sırası bir sözleşmedir
    # (`KURAL B` — bayt bayt aynı). Kayıt yalnız KÜMEYİ belirler.
    return tuple(FIIL_ANLAMI)


FIILLER: tuple[str, ...] = _fiilleri_kayittan_dogrula()

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
    "KIYASLA": ("cube_query",),
    "AYRISTIR": ("cube_query",),
    "TREND": ("cube_query",),
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
    # 🔴🔴 **`SORGU` BU TABLODA YOKTU — ve yokluğu denetimi TAMAMEN kapatıyordu.**
    #
    # ⊙ Ölçüldü (curl `EE` turu, EE-11): *«bu yıl km başına nakliye maliyeti neden
    # yüksek»* → plan `SORGU(cube_query="$3")` yazdı, `$3` ise bir **`HESAPLA`**
    # (`olcum`) adımıydı — doğrusu `$4` (`SUZ` → `sorgu`) olurdu. `dogrula` bunu
    # göremedi (`GIRDI_TIPI.get("SORGU")` → `None` → beklenen tip `None` → denetim
    # atlanır) ve kusur **koşum anında** patladı:
    # *«🔴 Ama tamamlayamadım: `(cube yok)` diye bir cube YOK»*.
    #
    # 🔴 Bu, `dogrula`'nın kendi var oluş gerekçesinin ihlaliydi: *«bir planı koşarken
    # reddetmek, hiç kurmamaktan pahalıdır»*. Denetim yazılıydı, tablo eksikti — ve
    # eksik bir tablo, denetimi **sessizce** kapatır.
    #
    # ⚠ Ve kazanç yalnız daha iyi bir hata mesajı değil: doğrulayıcı erken reddedince
    # `plan_garson`'un **DÜZELTME TURU** devreye girer, yani kullanıcı bir *«dürüst
    # red»* yerine **gerçek bir cevap** alır. *Dürüst bir red bir başarı değil, bir
    # borçtur.*
    #
    # ⚠ Satır içi `cube_query` (sözlük) istisnası `dogrula`'da zaten var.
    "SORGU": {"cube_query": "sorgu"},
    "BAGLA": {"kaynak": "satirlar"},
    "HESAPLA": {"kaynak": "satirlar", "hedef": "varlik"},
    "KIYASLA": {"cube_query": "sorgu"},
    "AYRISTIR": {"cube_query": "sorgu"},
    "TREND": {"cube_query": "sorgu"},
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

#: 🔴 **İSTEĞE BAĞLI ALANLAR — ve neden ayrı bir sözlük.**
#:
#: `_plani_oku` fazladan alan taşıyan adımı düşürür (`additionalProperties: False`'ın
#: serbest-JSON karşılığı). Bu doğru, ama **isteğe bağlı** bir alanı da düşürürdü —
#: yani şemanın izin verdiği bir planı doğrulayıcı reddederdi. İki tarafın **aynı**
#: sözlükten okuması bunu yapısal olarak imkânsız kılar.
ISTEGE_BAGLI_ALANLAR: dict[str, tuple[str, ...]] = {
    "AYRISTIR": ("mode",),      # "yoy" | "mom" — verilmezse `yoy`
    "TREND": ("mode",),
}

#: Adım referansı: `$1` = birinci adımın çıktısı. **Tek biçim, tek anlam.**
#: ⚠ Serbest bir ifade dili DEĞİL: `$` + sayı. Bir plan aritmetik yazamaz, koşul yazamaz,
#: döngü kuramaz. *Bir referans dilini genişletmek, onu bir programlama diline çevirir —
#: ve o dilin denetimi artık şemada değil, yorumlayıcıdadır.*
ADIM_REFERANSI = r"^\$[1-9][0-9]?$"


#: 🔴 **PLAN UZUNLUĞU TAVANI — DÖRT YETENEĞİN EN KISA ZİNCİRİNDEN TÜRETİLDİ.**
#:
#: `E9` haklı: plan uzunluğu bir **maliyettir**. Ama bir tavan, taşıması gereken işi
#: kesiyorsa maliyeti değil **yeteneği** kısar. Dört yeteneğin **en kısa** zincirleri
#: sayıldı (uydurulmadı):
#:
#: | yetenek | en kısa zincir | adım |
#: |---|---|---|
#: | kök-neden | `SORGU→BAGLA→SUZ→SORGU→AYRISTIR→ANLAT` | **6** |
#: | karar matrisi | `SORGU→SORGU→MATRIS→SIRALA→ANLAT` | 5 |
#: | rapor | `SORGU×3→RAPOR→ANLAT` | 5 |
#: | pano | `SORGU→KIR→KIR→PANO` | 4 |
#:
#: ⚠ Eski tavan **5**'ti, yani kök-neden inişini **yapısal olarak** imkânsız kılıyordu:
#: fiiller bağlanmış ama plan hiç kurulamamış olurdu. 6 + 2 pay = **8**; pay bilinçli
#: ve dar (bir `KIR` daha, bir `GORSEL` daha).
#:
#: ⟳ **8 → 12 (2026-08-09 akşamı) — ve yine SAYILARAK, seçilerek değil.**
#:
#: `HH1` (*«en kötü makineyi bul, o makinede en kötü vardiyayı bul, o vardiyada duruş
#: nedenlerini göster»*) canlıda **11 adımlık** bir zincir kurdu ve **koştu**:
#: `SORGU→BAGLA→SUZ→KIR→SORGU→BAGLA→SUZ→KIR→SORGU→…`. Üç seviyeli bir iniş, her
#: seviyede dört adım.
#:
#: 🔴 Ve o plan tavanı **aşarak** koştu: tavan yalnız `maxItems` olarak şemadaydı,
#: serbest-JSON sağlayıcı şemayı uygulamıyor. Yani tavan bir **temenniydi** — şimdi
#: `plan_kosucu.dogrula()` onu uyguluyor.
#:
#: 11 + 1 pay = **12**. ⚠ Pay dar: dördüncü bir seviye (15 adım) **kabul edilmiyor**,
#: çünkü o noktada plan uzunluğu bir cevaptan çok bir keşif gezisidir (`E9`).
#:
#: 🔴 Tek küresel tavan bilerek korundu: yetenek profili şu an **ölçülemiyor** (hangi
#: sorunun kök-neden olduğunu kim söyleyecek?). *Ölçemediğin bir ayrımı yapılandırmaya
#: koymak, onu bir varsayım olarak sabitlemektir.*
AZAMI_ADIM = 12


def plan_json_schema(index: dict, *, azami_adim: int = AZAMI_ADIM) -> dict[str, Any]:
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
        # ⟳ **GÖVDE İLE ŞEMA AYRIŞMIŞTI (2026-08-09).** Şema `kaynak` (satırlar)
        # veriyordu; gövde (`contribution`/`yoy`) bir **cube_query** okuyor. Yani
        # şema-geçerli bir adım gövdeye **boş** varıyordu ve fiil yapısal olarak
        # ÖLÜYDÜ. Ölçüldü: canlı plan üretiminde bu üçü **hiç** kullanılmadı.
        # *İstem kusurunun ayna görüntüsü: orada model sözleşmeyi görmüyordu,
        # burada gövde başka bir sözleşmeye göre yazılmıştı.*
        {"type": "object", "additionalProperties": False, "title": "KIYASLA",
         "properties": {"fiil": {"const": "KIYASLA"},
                        "cube_query": {"oneOf": [cq, _ref("kıyaslanacak sorgu")]}},
         "required": ["fiil", *ZORUNLU_ALANLAR["KIYASLA"]]},
        # ⟳ **GÖVDE İLE ŞEMA AYRIŞMIŞTI (2026-08-09).** Şema `kaynak` (satırlar)
        # veriyordu; gövde (`contribution`/`yoy`) bir **cube_query** okuyor. Yani
        # şema-geçerli bir adım gövdeye **boş** varıyordu ve fiil yapısal olarak
        # ÖLÜYDÜ. Ölçüldü: canlı plan üretiminde bu üçü **hiç** kullanılmadı.
        # *İstem kusurunun ayna görüntüsü: orada model sözleşmeyi görmüyordu,
        # burada gövde başka bir sözleşmeye göre yazılmıştı.*
        {"type": "object", "additionalProperties": False, "title": "AYRISTIR",
         "properties": {"fiil": {"const": "AYRISTIR"},
                        "mode": {"type": "string", "enum": ["yoy", "mom"]},
                        "cube_query": {"oneOf": [cq, _ref("kıyaslanacak sorgu")]}},
         "required": ["fiil", *ZORUNLU_ALANLAR["AYRISTIR"]]},
        # ⟳ **GÖVDE İLE ŞEMA AYRIŞMIŞTI (2026-08-09).** Şema `kaynak` (satırlar)
        # veriyordu; gövde (`contribution`/`yoy`) bir **cube_query** okuyor. Yani
        # şema-geçerli bir adım gövdeye **boş** varıyordu ve fiil yapısal olarak
        # ÖLÜYDÜ. Ölçüldü: canlı plan üretiminde bu üçü **hiç** kullanılmadı.
        # *İstem kusurunun ayna görüntüsü: orada model sözleşmeyi görmüyordu,
        # burada gövde başka bir sözleşmeye göre yazılmıştı.*
        {"type": "object", "additionalProperties": False, "title": "TREND",
         "properties": {"fiil": {"const": "TREND"},
                        "mode": {"type": "string", "enum": ["yoy", "mom"]},
                        "cube_query": {"oneOf": [cq, _ref("kıyaslanacak sorgu")]}},
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
                        "items": {"type": "object", "oneOf": dallar}},
            # 🔴🔴 `§YS-plan` — **KÜP YOLUNDA VARDI, PLAN YOLUNDA YOKTU.**
            #
            # Canlı ölçüm (curl, 2026-08-12): *«müşteri kohort analizi yap»* → plan
            # koştu, **müşteri × dönem PİVOTU** teslim edildi (8 satır, 3 adımlık
            # makbuz) ve *«kohort metodolojisi uygulanmadı»* diye **tek kelime yok**.
            #
            # ⊙ Sebep ölçüldü ve yapısal: `uyum.yok_sayilan_beyani` **yalnız** küp
            # yolunda çağrılıyor (`ask.py:3151`); plan yolu ondan önce dönüyor
            # (`ask.py:4222`). Ama asıl eksik çağrı değil **girdi**ydi: plan şemasında
            # `yok_sayilan` alanı **hiç yoktu**, yani plan garsonu *«şunu temsil
            # edemedim»* diyemiyordu bile.
            #
            # ⚠ `§EŞ`'in birebir aynı dersi (`intent_semasi`'de de aynı yorum duruyor):
            # *bir menüde olmayan yemek, mutfakta pişebiliyor olsa da sipariş edilemez.*
            #
            # 🔴 Ve çözüm bir **kelime listesi değil** (`ADR-0008`): hangi sözcüğün
            # temsil edilemediğini bilen tek merci garsonun kendisidir; iddiası
            # `uyum.yok_sayilan_beyani`'nin **iki deterministik süzgecinden** geçer
            # (sözcük soruda GEÇMELİ · teslim edilen fişte GEÇMEMELİ). Kural tek sahipli
            # kalıyor — bu alan yalnız aynı sahibi **plan yoluna da** besliyor.
            "yok_sayilan": {
                "type": "array", "items": {"type": "string"},
                "description": "Sorunun bu PLANA yansımayan sözcükleri (uygulanmayan "
                               "bir metodoloji · olmayan bir ölçü · karşılığı olmayan "
                               "bir şey). Hepsi yansıdıysa alanı hiç yazma. ⚠ Soru "
                               "sözcükleri ve nezaket kalıpları yok sayılan DEĞİLDİR — "
                               "yalnız İÇERİK taşıyan sözcükleri yaz."}},
        "required": ["adimlar"],
    }


def _alan_rehberi() -> str:
    """`intent_semasi.ALAN_REHBERI` — **tek sahip**, iki tüketici (`§AR`).

    ⚠ Fonksiyon içi import: `intent_semasi` bu modülü tanımıyor ama tersi doğru değil;
    modül düzeyinde bağlamak bir döngü riski taşırdı.
    """
    from app.intent_semasi import ALAN_REHBERI

    return ALAN_REHBERI


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
    # 🔴🔴 **ALANLAR DA ÜRETİLİR — ve bu satır ölçülmüş bir kusurdan doğdu.**
    #
    # İlk hâl yalnız `- FİİL: anlam` yazıyordu. Ölçüldü (2026-08-09): 15 fiilin
    # **6'sının** zorunlu alanı istemde **bir kez bile** geçmiyordu — `BAGLA.olcu` ·
    # `HESAPLA.hedef`+`olcu` · `SUZ.deger` · `SIRALA.olculer` · `RAPOR.baslik` ·
    # `PANO.baslik`. Yani model, kendisine **hiç gösterilmemiş** bir sözleşmeye göre
    # reddediliyordu (`_plani_oku` onları sessizce düşürüyordu).
    #
    # ⊙ Ve bu, bu docstring'in kendi uyardığı desendi: fiil **listesi** üretiliyordu,
    # fiillerin **alanları** üretilmiyordu. *İki sahip çelişmez, biri yalnızca EKSİK
    # kalır* — ve eksik olan taraf, kusuru bir **itaatsizlik** gibi gösterir.
    #
    # 🔴 En can alıcısı: eksik tarif edilen altı fiilden ikisi (`BAGLA`·`HESAPLA`)
    # kök-neden zincirinin tam ortasında. Sistem, en çok istediği zinciri üretmesi
    # **en zor** olan yerden tutuyordu.
    # 🔴🔴 **TİP AKIŞI DA GÖSTERİLİR — modelin bunu bilmesinin BAŞKA YOLU YOK.**
    #
    # Ölçüldü (canlı `FF12`, üç koşum): model `BOYUTSEC(kaynak="$1")` yazdı; `$1` bir
    # `SORGU` yani `satirlar`, oysa `BOYUTSEC` bir `bulgular` ister. Niyet **doğruydu**
    # (*«bu satırlarda hangi kırılım açıklıyor»*) ama araya `AYRISTIR` gerektiğini
    # görmesinin hiçbir yolu yoktu — istem fiilleri ve alanları anlatıyordu, **neyin
    # neye bağlanabileceğini** anlatmıyordu.
    #
    # ⊙ Yine tek sahipten üretiliyor (`CIKTI_TIPI` + `GIRDI_TIPI`): elle yazılmış bir
    # akış tablosu, bir fiil eklendiğinde **bayatlardı**.
    #
    # *Bir dili öğretirken kelimeleri vermek yetmez; hangi kelimenin hangisinden sonra
    # gelebileceğini de vermek gerekir.*
    def _tip_satiri(f: str) -> str:
        _girdi = GIRDI_TIPI.get(f) or {}
        _ister = ", ".join(f"{k}: {v or 'her tip'}" for k, v in _girdi.items()) or "—"
        return f"  üretir: {CIKTI_TIPI.get(f, '?')}  ·  ister: {_ister}"

    _fiiller = "\n".join(
        f"- {f}: {a}\n  zorunlu alanlar: " + ", ".join(ZORUNLU_ALANLAR.get(f, ()))
        + "\n" + _tip_satiri(f)
        for f, a in FIIL_ANLAMI.items())
    _ureten: dict[str, list[str]] = {}
    for _f, _t in CIKTI_TIPI.items():
        _ureten.setdefault(_t, []).append(_f)
    return (
        "Bir soruyu, YÖNETİLEN semantik katman üzerinde koşacak ADIMLARA ayırırsın.\n"
        "Yalnızca aşağıdaki cube'lar, ölçüler ve boyutlar VARDIR:\n\n" + catalog + "\n\n"
        "Kullanabileceğin TEK fiil kümesi (başka fiil YOKTUR):\n" + _fiiller + "\n\n"
        "🔴 TİP UYUŞMALI: bir alan hangi tipi istiyorsa, işaret ettiği adım o tipi "
        "ÜRETMELİ. Hangi tipi kim üretir:\n"
        + "\n".join(f"  {t}: {' | '.join(sorted(v))}" for t, v in sorted(_ureten.items()))
        + "\n⚠ Örnek: `BOYUTSEC` bir **bulgular** ister; onu yalnız `AYRISTIR` üretir. "
        "Yani zincir `SORGU → AYRISTIR → BOYUTSEC` olmalıdır, `SORGU → BOYUTSEC` değil.\n\n"
        "Kurallar:\n"
        '- SADECE JSON döndür: {"adimlar":[{"fiil":"...", ...}]}\n'
        # 🔴 `§YS-plan` — alan şemada var ama **istenmezse yazılmaz** (bu deponun
        # ölçülmüş dersi: `C3`'ün ilk yazımında model alanı üç turda da hiç doldurmadı).
        '- Sorunun bir kısmını bu plana YANSITAMADIYSAN (uygulanmayan bir metodoloji, '
        'karşılığı olmayan bir ölçü/şey) o sözcükleri `"yok_sayilan":["<sözcük>"]` '
        'olarak yaz — **atlamak bir hatadır**. Örnek: *«müşteri kohort analizi yap»* '
        'için kohort metodolojisi uygulanamıyorsa `"yok_sayilan":["kohort"]`.\n'
        "- 🔴 SORU TEK ADIMLA CEVAPLANIYORSA TEK ADIM YAZ. Plan uzunluğu bir maliyettir; "
        "gereksiz adım cevabı iyileştirmez, yalnız yavaşlatır.\n"
        "- Bir adım, önceki bir adımın çıktısına `$1` `$2` biçiminde işaret eder. "
        "İLERİ referans YOKTUR: `$3` ancak dördüncü adımda yazılabilir.\n"
        "- Bazı alanlar birden ÇOK adıma işaret eder: `\"kaynaklar\": [\"$1\",\"$3\"]`.\n"
        "- `KIR` ve `SUZ` satır DEĞİL yeni bir SORGU üretir; onu koşmak için sonraki "
        "adımda `{\"fiil\":\"SORGU\",\"cube_query\":\"$2\"}` yaz. Kök nedene inmenin "
        "yolu budur: sorgula → en kötüyü seç → oraya süz → yeniden sorgula.\n"
        # ⟳ Ölçüldü (canlı `FF4`, üç koşum): model ısrarla `SUZ(cube_query="$1")`
        # yazıyordu ve reddediliyordu. Yazdığı **doğruydu** — tip tablosu yanlıştı.
        # Artık geçerli; istem de açıkça söylüyor ki model tereddüt etmesin.
        "- Bir `cube_query` alanında bir `SORGU` adımına da işaret edebilirsin: `\"$1\"` "
        "o adımın **sorgusu** demektir (satırları değil). *«O makinede hangi vardiyada»* "
        "→ `SUZ` ile `$1`'in sorgusunu o makineye daralt, sonra yeniden `SORGU` at.\n"
        "- Aritmetik, koşul, döngü YAZAMAZSIN. Yalnız fiiller ve adım referansları.\n"
        # 🔴🔴 `§AR` — **ALAN REHBERİ PLAN İSTEMİNE DE GELİYOR.**
        #
        # ⊙ Ölçüldü (canlı `XII`): *«toplam ciromun **yüzde kaçı** ilk 3 müşteriden»* →
        # plan `SORGU×2 + ANLAT` kurdu ve *«Sayı doğru ama eksik»* beyan etti. Oysa cevap
        # **ifade edilebilir**: `pencere:{taban:toplam_ciro, kip:pay}`. Intent yolu bunu
        # biliyordu (istemi anlatıyor), plan yolu **bilmiyordu** — aynı `cube_query`
        # şemasını kullandığı hâlde.
        #
        # ⚠ Metin **kopyalanmadı**, `intent_semasi.ALAN_REHBERI`'nden **çağrıldı**: iki
        # istemde iki kopya, bir gün birinin bayatlaması demekti. Ve `llm.py`'nin kendi
        # yorumu bu dersi zaten yazmış: *«bir kuralı yanlış isteme yazmak, hiç
        # yazmamaktır»* — bu, o dersin **ikinci istem** hâli.
        + _alan_rehberi() +
        "- Tarih YAZMA: dönemi `period_expr` alanına kullanıcının kendi ifadesiyle "
        "(sistemin diline çevirerek) koy; tarihi Python hesaplar.\n"
        # 🔴 Bu satır `_cube_select_system`'den **ödünç alındı** ve gerekçesi ölçüldü:
        # plan istemi *"uydurma"* diyordu ama *"YALNIZ listelenenleri kullan"* demiyordu.
        # `O-13`: model `cube: "uretim"` / `toplam_miktar` uydurdu (ikisi de katalogda
        # YOK) ve beyaz listeden düştü — oysa **aynı katalogla** bugünkü istem uydurmuyor.
        # *Bir yasak, olumlu karşılığı yazılmadan yarım kalır.*
        "- 🔴 SADECE yukarıda listelenen cube / ölçü / boyut ADLARINI kullan. Katalogda "
        "karşılığı olmayan bir adım UYDURMA: o adımı hiç yazma.\n"
        "- 🔴 HER ADIMDA O FİİLİN ZORUNLU ALANLARININ HEPSİNİ YAZ. Eksik bir alan planı "
        "geçersiz kılar; fazladan bir alan da geçersiz kılar.\n"
        "- 🔴 SIRALAMA ve LİMİT bir `SORGU` adımının İÇİNDEDİR (`order`/`limit`), ayrı bir "
        "adım DEĞİLDİR. *«en yüksek 5 müşteri»* TEK adımdır.\n"
        # ⟳ Kural **iki kez** düzeltildi ve ikisi de `O-13` denklik kapısında ölçüldü:
        # (1) örnekteki `period_expr` her sorguya kopyalanıyordu → örnekten çıkarıldı;
        # (2) *"dönem uydurma"* denince model `period_expr`'i **tamamen bıraktı** ve
        # dönemi `timeDimensions`'a yazmaya başladı — aşırı düzeltme. İkisinin **ayrı**
        # işler olduğu artık açıkça yazılı. *Bir yasağı, yerine ne konacağını söylemeden
        # koymak, kusuru başka bir alana taşır.*
        "- 🔴 DÖNEM: kullanıcı bir dönem YAZDIYSA (*«bu yıl»*, *«geçen ay»*) onu "
        "`period_expr`'e **kullanıcının kendi ifadesiyle** yaz. YAZMADIYSA hiç koyma — "
        "*«makinelere göre ortalama oee»* dönemsizdir ve öyle kalmalıdır.\n"
        "- 🔴 `timeDimensions` DÖNEM FİLTRESİ DEĞİLDİR, **kırılımdır**: yalnız *«aylara "
        "göre»* / *«çeyreklere göre»* gibi bir zaman EKSENİ istendiğinde konur. Dönem "
        "`period_expr`'e gider, `timeDimensions`'a değil.\n"
        # 🔴🔴 `O-15/Z` — **KATALOGDAKİ `time[…]` HANGİ ALANA GİDER: HİÇ YAZMIYORDU.**
        #
        # Katalog satırı `- parti: measures[…]; dimensions[a, b]; time[tarih]` biçiminde.
        # İki liste **görsel olarak paralel** ve istem, `time[…]`'daki adın `dimensions`
        # alanına yazılMAyacağını hiçbir yerde söylemiyordu. Model doğal olanı yaptı.
        #
        # ⊙ Ölçüldü (canlı `II` turu): 20 senaryonun **üçü** yalnız bunun yüzünden düştü
        # (`II19`·`II20`), biri de sessizce dönemsiz kaldı (`II5`). Red mesajı bile
        # doğruydu — *«`parti`'de şu boyut(lar) yok: tarih»* — ama modele hiçbir şey
        # **öğretmiyordu**, çünkü model o adı katalogda **görmüştü**.
        #
        # *Bir listeyi göstermek, onun nereye yazılacağını söylemez; ve iki listeyi yan
        # yana göstermek, ikisini aynı alanın adayları gibi okutur.*
        "- 🔴🔴 KATALOGDAKİ İKİ LİSTE İKİ AYRI ALANA GİDER: `dimensions[…]`'daki adlar "
        "`dimensions` alanına, `time[…]`'daki adlar **YALNIZ** `timeDimensions` alanına "
        "yazılır. Bir zaman adını (`time[…]`) `dimensions`'a yazmak plan reddine yol "
        "açar. Biçim: `\"timeDimensions\":[{\"dimension\":\"<time[…]'daki ad>\","
        "\"granularity\":\"month\"}]` — `granularity` day|week|month|quarter|year.\n"
        "- 🔴 KIRILIM (`dimensions`) ve zaman ekseni de tek bir `SORGU` adımının "
        "içindedir. *«aylara göre üretim»* TEK adımdır.\n"
        # ⟳ Ölçüldü (canlı `FF4`): model `BAGLA` ile en kötüyü **buldu** ama sonra
        # **kullanmadı** — bir sonraki `SORGU`yu global attı. Plan reddedildi çünkü
        # `BAGLA` çıktısı ulaşılamaz kaldı.
        # 🔴🔴 `O-19/K` — **KAPSAMA KURALI: SORUNUN HER PARÇASI KARŞILANMALI.**
        #
        # ⊙ Ölçüldü (canlı `IV`): *«iade oranı en yüksek 3 müşteriyi **ve** ciro
        # paylarını göster»* → plan **tek adım** kurdu ve yalnız iadeyi verdi. Soru iki
        # şey istiyordu; cevap birini karşıladı ve öteki **sessizce düştü**.
        #
        # ⚠ İstem *"gereksiz adım yazma"* diyordu (doğru) ama *"eksik adım da yazma"*
        # demiyordu. Bir kısıtı tek yönlü yazmak, öteki yönü serbest bırakmaktır — ve
        # model daima ucuz olan yöne kayar.
        #
        # *Bir cevabın yarısı, yanlış bir cevaptan yalnızca daha kibardır.*
        "- 🔴 KAPSAMA: sorunun **her parçası** planda karşılanmalı. Kullanıcı iki şey "
        "istediyse (*«X'i ve Y'yi göster»*) iki `SORGU` yaz ve ikisini `RAPOR` ya da "
        "`MATRIS` ile birleştir — birini yazıp ötekini atlamak, cevabı yarım vermektir. "
        "⚠ Bu, yukarıdaki *«gereksiz adım yazma»* kuralının ZITTI değil ikizidir: "
        "gereksiz adım da eksik adım da bir kusurdur.\n"
        "- 🔴 HER ADIMIN ÇIKTISI KULLANILMALI: bir adım hiçbir adım tarafından "
        "gösterilmiyorsa ve son adım değilse plan REDDEDİLİR. `BAGLA` ile bir varlık "
        "seçtiysen onu **kullan** — *«o makinede»* demek için `SUZ` ile o varlığa süz, "
        "sonra yeniden `SORGU` at.\n"
        # 🔴 **İKİ ÖRNEK, VE BİRİNCİSİ TEK ADIMLI — sıra bilinçli.**
        # Ölçüldü (`O-13` denklik kapısı): tek örnek çok adımlı olduğunda model basit
        # soruyu da bölüyordu (*«en yüksek cirolu 5 müşteri»* → çok adımlı). Ve ilk
        # örnekteki `period_expr` **her** sorguya kopyalanıyordu — kullanıcı dönem
        # yazmadığı hâlde. *Bir örnek bir tarif değil bir kalıptır; içine koyduğun her
        # alan, koymadığın her sorguda da görünür.*
        "\nÖRNEK 1 — «makinelere göre ortalama oee» (TEK ADIM, dönem YOK):\n"
        '{"adimlar":[{"fiil":"SORGU","cube_query":'
        '{"cube":"oee","measures":["ort_oee"],"dimensions":["makine"]}}]}\n'
        "\nÖRNEK 2 — «en kötü makineyi bul ve neden öyle olduğunu araştır»:\n"
        '{"adimlar":[\n'
        '  {"fiil":"SORGU","cube_query":{"cube":"oee","measures":["ort_oee"],'
        '"dimensions":["makine"]}},\n'
        '  {"fiil":"BAGLA","kaynak":"$1","boyut":"makine","olcu":"ort_oee"},\n'
        '  {"fiil":"HESAPLA","kaynak":"$1","hedef":"$2","boyut":"makine","olcu":"ort_oee"},\n'
        '  {"fiil":"SUZ","cube_query":"$1","boyut":"makine","deger":"$2"},\n'
        '  {"fiil":"ANLAT","kaynaklar":["$1","$3"]}\n'
        "]}\n"
        "⚠ Bu örnekteki `cube_query` **satır içi bir nesnedir**; `$1` yazılan yerler ise "
        "**referanstır**. İkisini karıştırma.\n"
        # ⟳ Ölçüldü (canlı `HH3`): model `{"fiil":"SORGU","measures":[…],"dimensions":[…]}`
        # yazdı — alanları `cube_query`'nin İÇİNE değil adımın kendisine koydu. Olumlu
        # örnek yetmiyor; *bir kalıbı öğretmenin en hızlı yolu, yanlışını da göstermektir.*
        "\n🔴 SIK YAPILAN HATA — `SORGU` adımının alanları:\n"
        '  YANLIŞ: {"fiil":"SORGU","measures":["ort_oee"],"dimensions":["makine"]}\n'
        '  DOĞRU : {"fiil":"SORGU","cube_query":{"cube":"oee","measures":["ort_oee"],'
        '"dimensions":["makine"]}}\n'
        "⚠ `SORGU` adımının **tek** alanı `cube_query`'dir; `measures`/`dimensions`/"
        "`filters` onun **içine** yazılır."
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


#: 🔴🔴 `§RG` — **BİR BELGE, TEK FİŞLE KARŞILANAMAZ.**
#:
#: ## Ölçülen kusur (curl, 2026-08-10 · beş koşum)
#:
#:     «son 2 yıl satış raporu hazırla»
#:       SORGU,SORGU,RAPOR              → 2 blok  ✅
#:       (plan YOK)                     → rapor YOK   🔴
#:       SORGU×3,RAPOR                  → 3 blok  ✅
#:       SORGU×3,RAPOR                  → 3 blok  ✅
#:       SORGU×4,RAPOR                  → 4 blok  ✅
#:
#: **5'te 4.** Bir koşumda route/garson tek fişle cevapladı ve `plan_tuketici` sustu
#: (*«route zaten cevapladı → boşluk YOK»*). Kullanıcı bir **belge** istedi, bir **tablo**
#: aldı — ve hangisini alacağı **modelin o anki tercihine** kalmıştı.
#:
#: ## Yüklem — sözlük değil, **yetenek listesi**
#:
#: Aranan şey bir Türkçe kelime değil, **bu sistemin ürettiği teslimat türlerinin adı**:
#: `RAPOR` ve `PANO` bu dosyanın kendi `FIILLER`'inde yazılı. Yani yüklem kataloğa bakar —
#: `simge.sahipler`'in katalog kimliklerine, `§KD`'nin boyut adlarına baktığı gibi.
#: ADR-0008'in yasakladığı **açık uçlu sözlük** değildir: küme `FIILLER` kadar kapalıdır.
#:
#: ⚠ Ve karar **cevabı iptal etmez**: yalnız *«tek fiş yeterli değil»* der ve merdivenin
#: kendi kuralını uygular — *«tek fişte olmuyorsa orkestre eder»* (`§0.0`).
#:
#: ⚠ Kapsam **taze soruyla** sınırlı: *«bu raporu nasıl yorumlarsın»* bir takiptir ve
#: oraya `followup` bakar. Bir belgeyi **istemek** ile bir belge **hakkında konuşmak**
#: aynı şey değildir.
#:
#: *Bir teslimat türünü tanımayan sistem, onu ancak tesadüfen üretir.*
BELGE_FIILLERI: tuple[str, ...] = ("RAPOR", "PANO")


def belge_istegi(soru: str) -> str | None:
    """Soru bu sistemin ürettiği bir **teslimat türünü** adıyla istiyor mu? → fiil adı.

    ⚠ `cube_router._syn_hit` çağrılır (yeniden yazılmaz): kelime başı + geçerli ek
    zinciri disiplini bütün depoda aynıdır — *«raporu»*, *«panosu»*, *«raporunu»* geçer;
    *«raportaj»* geçmez.
    """
    from app.cube_router import _norm, _syn_hit

    q = _norm(soru or "")
    for fiil in BELGE_FIILLERI:
        if _syn_hit(q, fiil.lower()):
            return fiil
    return None


#: `§RZ` — bir belgeye türetilecek **azami** ek bölüm. Bir sabit değil bir **karar**:
#: dört bölüm bir kapak sayfasına sığar, sekiz bölüm bir döküme dönüşür (`§RK`'nın
#: aynı gerekçesi, blok düzeyinde).
BELGE_EN_AZ_BOLUM = 2
BELGE_AZAMI_EK = 3
#: Kaç kırılım **denenir** (koşulur), kaçı **seçilir** — bkz. `belge_bolum_sirala`.
#:
#: 🔴 Sınır **6 idi ve seçimi bozuyordu**: `parti`de `musteri` katalogda 10. sırada,
#: yani bir **satış** raporunun en doğal kırılımı hiç **ölçülmüyordu** bile. Ve kesmeyi
#: yapan sıranın kendisi anlamsız (`dimension_origin` boş → beyan sırası). *Anlamı
#: olmayan bir sıranın hangi adayın ölçüleceğine karar vermesi, kusurun kendisidir.*
#:
#: ⊙ **Bedeli ölçüldü ve beklentimi çürüttü.** Canlıda belge isteği ~27 sn sürüyordu ve
#: ilk teşhisim *«süpürme pahalı»* idi. Ölçüm (`kalite`, 13 aday):
#:
#:     süpürme (13 blok) = 0,61 sn   ·   tek blok = 0,03 sn
#:
#: Yani gecikmenin kaynağı süpürme **değil**, garsonun `k=3` planlamasıdır. Aday sayısını
#: kısmak **hiçbir şey** kazandırmaz, yalnız seçimi kör eder.
#: *Bir maliyeti ölçmeden kısmak, ölçülmemiş bir yerden ödemektir.*
BELGE_ADAY_KIRILIM = 24
#: Bir kırılımın **okunabilir** sayıldığı satır aralığı. Alt sınır: tek satırlık bir
#: kırılım bir kırılım değildir. Üst sınır `§RK`'nın kendi eşiği — orada bir blok artık
#: bir özet değil bir **döküm** sayılıyor; burada da bir bölüm olarak seçilmemeli.
BELGE_EN_AZ_SATIR = 3


def belge_ek_bolumleri(temel: dict, cube_meta: dict,
                       *, azami: int = BELGE_AZAMI_EK) -> list[dict]:
    """🔴🔴 `§RZ` — **BİR BELGE İSTEĞİ, TEK BÖLÜMLÜ BİR PLANLA KARŞILANAMAZ.**

    ## Ölçülen kusur (curl `T` turu, 2026-08-11 · **3/3 aynı**)

        «son 2 yıl satış raporu hazırla, kârlılık ve fire de olsun»
          plan: SORGU → ANLAT          → **1 bölüm** → `§RT`: «tek bölümlük bir sonuç çıktı»
          rapor: **YOK** (3 koşumda 3)

    Kullanıcı bir **belge** istedi; sistem dürüstçe *«olmadı»* dedi. Ama kullanıcının
    kuralı açık: **dürüst bir red bir başarı değildir** — cevaplanması gereken bir soruysa
    çözülmek zorundadır. Ve çözülebilirdi: aynı turda *«bana bir üretim panosu hazırla»*
    **altı** bölüm üretti. Yani eksik olan yetenek değil, **zenginleştirme**ydi.

    ## Neden bu iş planlayıcının kumarına bırakılamaz

    `§RB` planın belgeyle **bitmesini** garantiledi; kaç **bölüm** olacağını garanti eden
    hiçbir şey yoktu — o, garsonun o anki tercihiydi. Oysa bir belgenin bölümleri
    **kataloğun kendisinden** çıkar: aynı ölçüler, küpün kendi boyutlarıyla kesilir.

    ⚠ ADR-0008 temiz: burada bir **kelime listesi** yok. Kaynak `cube_meta`'nın kendi
    `dimensions`'ı, sıra kataloğun sırası — yani üretilen her bölümün karşılığı katalogda
    **vardır**, uydurulmaz.

    ⚠ Ölçüler ve süzgeçler **temelden aynen taşınır** (`§RD-3`): bir belgenin bütün
    bölümleri aynı dönemi konuşmak zorundadır; farklı dönemli iki bölüm yan yana bir
    belge değil bir yanılgıdır.

    *Bir belgeyi tek bölümle karşılamak, kullanıcıya kapağını gösterip içini vermemektir.*
    """
    if not isinstance(temel, dict) or not temel.get("cube"):
        return []
    _var = {str(d) for d in (temel.get("dimensions") or [])}
    ekler: list[dict] = []

    # 1) ZAMAN EKSENİ — bir belgenin en çok beklenen bölümü: aynı ölçünün seyri.
    # ⚠ Anahtar `time_dimensions` (ÇOĞUL) ve zaman boyutu `dimensions` listesinde
    # **yoktur** — ölçüldü. Tekil bir ada yazsaydım bu dal hiç koşmaz, kusur da
    # *"türetici zaman bölümü üretmiyor"* diye değil *"hiç üretmiyor"* diye görünürdü.
    _zaman = next((str(d) for d in (cube_meta.get("time_dimensions") or []) if d), "")
    if _zaman and not (temel.get("timeDimensions") or []):
        ekler.append({**{k: v for k, v in temel.items() if k != "dimensions"},
                      "timeDimensions": [{"dimension": _zaman, "granularity": "month"}]})

    # 2) KIRILIMLAR — sıra **kataloğun beyan sırası DEĞİL**, `drill.available_dimensions`.
    #
    # ⊙ İlk yazımda katalog sırasını kullandım ve canlıda ölçüldü: bir **satış** raporuna
    # `tedarikci` ve `vardiya` bölümleri geldi — `musteri` ve `kumas_cinsi` dururken.
    # Beyan sırasının bir anlamı yok; o dosyanın kendi cümlesi bunu zaten yazmış:
    # *«eskiden YAML beyan sırasında dönüyordu — yani hiçbir anlamı yoktu»*.
    #
    # ⚠ Ve o fonksiyon benim atladığım bir şeyi de yapıyor: **süzgeçteki** boyutları da
    # eler. Temel `musteri`ye süzülmüşse `musteri` kırılımı tek satırlık bir bölüm olurdu.
    # *Bir listeyi ikinci kez yazmak, birincinin öğrendiklerini ikincide unutmaktır.*
    #
    # ⊘ **`contribution.rank_dimensions` bilerek kullanılmadı:** o, bir **değişimin**
    # açıklayıcılığını sıralar — iki dönem ve boyut başına birer sorgu ister. Bir raporun
    # bölüm listesi bir varyans analizi değildir; oraya onun aletini tutmak, cevabı
    # pahalılaştırıp anlamını değiştirirdi.
    from app.drill import available_dimensions

    # 🔴🔴 **KIRILIM BİR SERİ DEĞİLDİR — ve bunu canlıda ölçerek öğrendim.**
    #
    # ⊙ Ölçülen gerileme (curl `X` turu, benim `§RZ` sürümüm): *«son 2 yıl satış raporu
    # hazırla»* → **18 blok** ve istek **2 dakikayı aştı**. Sebep: temel fiş bir **aylık
    # seyirdi** (`timeDimensions`) ve `{**temel, "dimensions": [ad]}` o kovayı da
    # **miras aldı**. Yani her kırılım `müşteri × ay` kartezyeni oldu — 253 satırlık
    # bloklar. Ve seçicinin *«seyir yarışmaz»* kuralı **bütün blokları** seyir sandığı
    # için hiçbiri elenmedi.
    #
    # ⚠ İki kusur bir kökten: bir **kırılım** ile bir **seyir** ayrı şeylerdir ve
    # ikisini aynı fişte birleştirmek ikisini de bozar.
    #
    # *Bir bölümü bir öncekinden türetirken, ondan neyi ALMAYACAĞINI da söylemek gerekir.*
    for aday in available_dimensions(cube_meta, temel):
        if len(ekler) >= azami + BELGE_ADAY_KIRILIM:
            break
        ad = str(aday.get("name") or "")
        if not ad or ad in _var or ad == _zaman:
            continue
        _kirilim = {k: v for k, v in temel.items() if k != "timeDimensions"}
        ekler.append({**_kirilim, "dimensions": [ad]})

    # ⚠ Zaman ekseni bilerek **başta**: temel kırılımlıysa ilk ek onu tekrar etmesin,
    # kırılımsızsa (çıplak toplam = kapak sayısı) onu ilk açıklayan şey seyri olsun.
    # Tek kural: *bir bölüm bir öncekini tekrar etmemelidir.*
    #
    # ⚠ Liste bilerek **azamiden uzun** döner: hangisinin bilgi taşıdığı koşmadan
    # bilinemez (`available_dimensions`'ın kendi itirafı). Seçimi `belge_bolum_sirala`
    # yapar — koşulmuş satırların üstünde, **ölçerek**.
    return ekler


def belge_bolum_sirala(bloklar: list[dict], *, azami: int = BELGE_AZAMI_EK) -> list[dict]:
    """🔴 `§RZ-2` — **HANGİ KIRILIM BİR BÖLÜM OLMAYA DEĞER? — TAHMİN DEĞİL, ÖLÇÜM.**

    ## Ölçülen kusur (canlı, `§RZ` ilk sürümü)

        «son 2 yıl satış raporu hazırla, kârlılık ve fire de olsun»
          türetilen bölümler: **tedarikçi** · **vardiya**        🔴 bir SATIŞ raporuna

    `musteri` ve `kumas_cinsi` dururken. Sebep ölçüldü: `parti` küpünde
    `dimension_origin` **boş**, yani `available_dimensions`'ın maliyet sıralaması her
    boyuta aynı skoru veriyor ve `sorted` kararlı olduğu için sonuç **katalog beyan
    sırası** — o dosyanın kendi cümlesiyle *«hiçbir anlamı yoktu»*.

    ## Neden bir tercih listesi YAZILMADI

    *«musteri, tedarikci'den önce gelir»* demek, her yeni katalog için elle bakım
    isteyen **açık uçlu bir liste** olurdu (ADR-0008) — ve kullanıcının kendi kuralı:
    *tek tek sinonim yazmak aptallıktır.* Katalogda ticari bir eksen beyanı **yok**
    (`pvm` ölçü çifti verir, boyut vermez; `dimension_values` boş) — yani bu bir
    **katalog borcudur**, kodla kapatılamaz.

    ## Bunun yerine: bilgi taşıyan bölüm ÖLÇÜLÜR

    İki ölçüt, ikisi de koşulmuş satırların üstünde:

    1. **Okunabilirlik** — `BELGE_EN_AZ_SATIR` ≤ satır ≤ `§RK`'nın özet eşiği. Tek
       satırlık bir kırılım bir kırılım değildir; 500 satırlık bir kırılım bir döküm.
    2. **Yoğunlaşma** — en büyük segmentin payı, **eşit bölüşüme göre**. Cironun %60'ı
       tek bir müşteriden geliyorsa `musteri` bir **etkileyen faktördür**; üçe eşit bölen
       `vardiya` değildir. `contribution.rank_dimensions`'ın *«en büyük tek segment
       payı»* sezgisinin aynısı.

       🔴 **Ham pay YETMEZ — ölçüldü ve ilk sürümüm bu yüzden yanlış seçti.** Ham pay
       kardinaliteye **ters orantılıdır**: 3 değerli `vardiya`nın en büyük payı (~%40)
       23 değerli `musteri`ninkinden (~%15) mekanik olarak büyüktür. Canlıda tam da bu
       oldu: bir **satış** raporuna `vardiya` ve `renk_derinlik` seçildi.

       Doğru ölçüt **kat**: `pay × n` — *«bu segment eşit bölüşümdeki payının kaç katı»*.
       `vardiya` 0,40×3 = **1,2**; `musteri` 0,15×23 = **3,5**. Aynı sayı kullanıcıya
       gösterilebilecek bir cümledir de: *«en büyük müşteri, eşit paydan 3,5 kat fazla»*.

       *Kardinalitesi farklı iki dağılımı ham payla kıyaslamak, küçük olanı her seferinde
       kazandırmaktır.*

    ⊘ `rank_dimensions`'ın **kendisi** çağrılmadı: onun girdisi bir **değişim** raporudur
    (`bulgular`/`delta`), iki dönem ister. Sözleşmesi tutmayan bir fonksiyonu çağırmak,
    onu çağırmamaktan daha kötüdür.

    *Bir bölümün değerini beyan sırasından okumak, hiç okumamaktır.*
    """
    from app.report import _OZET_ESIGI

    def _skor(b: dict) -> tuple:
        sonuc = b.get("result") or {}
        satir = int(sonuc.get("row_count") or 0)
        okunur = BELGE_EN_AZ_SATIR <= satir <= _OZET_ESIGI
        cq = b.get("cube_query") or {}
        olcu = next((str(m) for m in (cq.get("measures") or [])), "")
        degerler = [abs(float(r.get(olcu) or 0))
                    for r in (sonuc.get("rows") or []) if isinstance(r, dict)]
        toplam = sum(degerler)
        pay = (max(degerler) / toplam) if (toplam and degerler) else 0.0
        kat = pay * len(degerler)          # eşit bölüşümün kaç katı — bkz. docstring
        return (0 if okunur else 1, -kat)

    # ⚠ Zaman ekseni (seyir) **yarışmaz**: bir belgenin seyir bölümü bir kırılım değil,
    # onun omurgasıdır — yoğunlaşma ölçütü ona anlamsızdır.
    #
    # 🔴 Ama *«seyir»* yalnız `timeDimensions` varlığı **değildir**: bir kırılım da onu
    # miras alabilir (ve canlıda aldı — 17 blok birden *«seyir»* sayıldı, hiçbiri
    # elenmedi). Bir seyir **zaman kovası taşır ve kırılımı YOKTUR**; ikisi bir aradaysa
    # o bir seyir değil bir kartezyendir.
    #
    # *Bir şeyi tek bir işaretten tanımak, o işareti taşıyan her şeyi o şey sanmaktır.*
    seyir = [b for b in bloklar
             if (b.get("cube_query") or {}).get("timeDimensions")
             and not ((b.get("cube_query") or {}).get("dimensions") or [])]
    kirilim = [b for b in bloklar if b not in seyir]
    return seyir + sorted(kirilim, key=_skor)[:max(0, azami - len(seyir))]
