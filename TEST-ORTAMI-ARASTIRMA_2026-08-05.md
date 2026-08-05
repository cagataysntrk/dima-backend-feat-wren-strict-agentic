# TEST ORTAMI — **WEB ARAŞTIRMASI**

> **Soru:** *"test ortamını muazzam ölçüde nasıl büyütürüz — ve büyüttüğümüzde
> gerçekten bir şey ölçüyor olur muyuz?"*
> **Yöntem:** 6 arama · 5 tam metin okuma · 1 erişilemedi (ACM 403).
> **Kesit:** 2026-08-05. **Bu belge kod değiştirmez** — ne bulunduğunu ve neyin bize
> uyup neyin uymadığını söyler.
> **Kardeş belge:** `TEST-ORTAMI-RAPORU_2026-08-05.md` *(bugünkü durum ölçümü)*.

---

## 0 · TEK CÜMLELİK SONUÇ

Aradığımız dört şeyin **dördü de** literatürde çözülmüş, adı konmuş ve ölçülmüş
problemler: **(1)** katalog sözlüğü yanlılığı, **(2)** netleştirme/cevaplanamazlığın
ölçülmesi, **(3)** elle yazmadan ground-truth üretimi, **(4)** altın cevap
**gerektirmeyen** bir doğruluk ölçüsü. Üçü doğrudan uygulanabilir; biri *(paraphrase
üretimi)* bize **yanlış** uygular.

---

## 1 · 🔴 EN ÖNEMLİ BULGU — bizim tablomuz bir istisna değil, **beklenen sonuç**

**BEAVER** (kurumsal veri ambarlarından gerçek sorgu kütüklerine dayalı text-to-SQL
kıyas kümesi) tek bir sayıyla bizim durumumuzu anlatıyor:

| kıyas kümesi | model başarımı |
|---|---|
| Spider / BIRD *(halka açık, küratörlü)* | **~%81** |
| **BEAVER** *(gerçek kurumsal ambar)* | **%10,8** |

Fark **modelde değil, verinin kendisinde**:

| boyut | BIRD | **BEAVER** |
|---|---|---|
| tablo | 6,8 | **101,5** |
| sütun | 72,5 | **869,4** |
| sorgu uzunluğu | 22 token | **316,7 token** |
| join | 0,6 | **5,7** |

Sebepler: **şifreli sütun adları** (`FCLT_BUILDING_KEY`) → anlamsal benzerlik çalışmıyor;
**beyan edilmemiş foreign key** → join yolu çıkarım gerektiriyor; **alan bilgisi**
şemada yazmıyor.

> 🔴 **Bizim için doğrudan sonuç:** `nl_corpus`'un **%93,1**'i ile `gercek_dunya`'nın
> **doğru = 0**'ı arasındaki uçurum bir kusur değil — **literatürün öngördüğü uçurumun
> aynısı**. Küratörlü korpusta yüksek puan almak, kurumsal veride başarının **kanıtı
> değildir**; BEAVER bunu 81 → 10,8 ile ölçmüş.

⚠ Ve bir **acı ders**: BEAVER'da modele beş alt görevin **hepsi için oracle ipucu**
verildiğinde başarım yalnız **%30,1**'e çıkıyor. *Yani doğru tabloyu, doğru join'i,
doğru sütunu bedava versen bile sistem hâlâ %70 yanılıyor.* Bizim `netleştirme`
mekanizmamız tam olarak bu ipucunu **kullanıcıdan** almaya çalışıyor — ipucunun tek
başına yetmediğini bilmek, netleştirmeden ne bekleyeceğimizi belirler.

---

## 2 · SÖZLÜK YANLILIĞI — bizim *"kural 1"* tuzağımızın **literatürdeki adı**

`gercek_dunya.py`'nin kural 1'i (*"soru ∩ katalog etiketleri = ∅"*) harfiyen
uygulandığında amacının tersine dönmüştü: `fire`, `bakiye`, `müşteri`, `ciro` elenmişti —
oysa bunlar işin **kendi kelimeleri**.

Literatür bu problemi **ölçmüş** ve bizimkinden **daha derin** bir tuzak bulmuş:

> Kıyas kümesi yazarları, açık şema atıflarını engellemek için şema adlarını
> **açıklamalarla** değiştiriyor. Ama *"kişiler veritabanı açıklamasında geçen terimleri
> derhal benimsiyor"* — sonuç: **açık şema atfı yerine geçen, yanlı bir sözlük**.
> *Yani yasağı koymak yanlılığı kaldırmıyor, yalnız kaynağını değiştiriyor.*

**Önerilen çözüm kelime yasağı değil, kaynak çeşitliliği:** anotasyoncular
**alt-gruplara** bölünüyor ve her grup veritabanını **farklı bir yoldan** öğreniyor
(farklı görev sürümleri) — böylece tek bir kelime kaynağı korpusun tamamına sızmıyor.

**Bize uyarlaması:**

| bugün | önerilen |
|---|---|
| Tek yazar (ajan) + iki mekanik imza *(ham tanımlayıcı · sorunun tamamı katalog kelimesi)* | **Vaka kaynağını çeşitlendir**: her vakanın `kaynak` alanı zaten var — ama bugün ağırlık `§9.6` (yani **katalogla aynı kafadan** yazılmış) |
| `REAL_PHRASINGS` + `deneyim.py` **ikincil** kaynak | Bunlar **birincil** olmalı; `§9.6` türevi vakalar **azınlıkta** kalmalı |
| — | 🔵 **Ölçülebilir kapı:** vakaların **kaynak dağılımı** raporlansın; tek kaynak %50'yi geçerse kapı uyarsın |

⚠ **Ve bir dürüstlük notu:** bugünkü 42 vakanın çoğunun `kaynak`'ı `§9.6 …` — yani
**korpusu yazan akıl ile kataloğu yazan akıl aynı**. Literatürün *"açıklamayı okuyan
anotasyoncu açıklamanın kelimelerini benimser"* bulgusu **bize birebir uyuyor**.

---

## 3 · NETLEŞTİRME ve DÜRÜST RET — bunlar **kaçamak değil, ölçülen sınıflar**

Bu, bugünkü tablomuzun en çok yanlış okunabilecek yeri: 41 sonucun 41'i `durust_ret`.
Literatür, bu davranışın **ölçülecek bir sınıf** olduğunu çoktan kabul etmiş:

| çalışma | ne yapıyor | bize ne veriyor |
|---|---|---|
| **PRACTIQ** *(Amazon/Anthropic ortak, konuşmalı)* | **Belirsiz** ve **cevaplanamaz** sorguları ayrı sınıflar olarak kuruyor; sistemden beklenen üç mod: **netleştir · reddet · cevapla** | Bizim `netlestirme`/`durust_ret`/`dogru` üçlümüzün **birebir karşılığı** — sınıflandırmamız literatürle uyumlu |
| **AmbiQT** *(EMNLP'23, 3000+ vaka)* | Her soru **iki geçerli SQL**'e açık; belirsizlik **sistemli olarak enjekte ediliyor**: sütun/tablo eşanlamları · örtüşen sütun adları (join belirsizliği) · toplulaştırma belirsizliği | 🔵 **Belirsizlik ÜRETİLEBİLİR** — elle vaka yazmadan. Bizim `bakiye` çakışmamız (iki cube'da aynı ölçü) tam olarak onların *"eşanlam enjeksiyonu"* sınıfı |
| **Expected Information Gain** ile disambiguation | *Hangi* netleştirme sorusunun sorulacağını **beklenen bilgi kazancıyla** seçiyor | Bizim netleştirme **hangi** soruyu soracağını bugün sezgiyle seçiyor; ölçülebilir bir ölçüt var |

**AmbiQT'nin ölçüsü bizim için doğrudan kullanılabilir:**
`EitherInTopK` *(iki geçerli yorumdan biri ilk-5'te mi)* ve **`BothInTopK`** *(ikisini de
yakalıyor mu)*. İkincisi tam olarak *"tahmin mi ediyor, yoksa belirsizliği görüyor mu"*
sorusunu ayırıyor.

> 🔵 **Somut öneri:** `gercek_dunya`'nın `kabul` listesine bir **üçüncü ölçü** eklensin:
> netleştirme yapıldığında **sunulan seçeneklerin doğru olanı içerip içermediği**.
> Bugün *"netleştirdi mi"* diye soruyoruz; *"doğru şıkları mı saydı"* diye sormuyoruz.
> **Netleştirmenin kendisi de yanlış olabilir** ve bunu bugün hiçbir şey yakalamıyor.

---

## 4 · GROUND-TRUTH'U **ELLE YAZMADAN** ÜRETMENİN ÜÇ YOLU

Görev **#33** ve **#35**'in tam karşılığı. Üçünü de buldum; **ikisi bize uyuyor, biri
uymuyor**.

### 🟢 (a) **Trend/olay enjeksiyonu** — *InsightBench yöntemi* → görev **#33**

InsightBench'in 100 veri kümesi · **475 içgörü** ground-truth'u şöyle kuruldu:

1. Şema seç (gerçek iş tablolarından)
2. **Matematiksel modelle trend enjekte et** *(ör. çözüm süresini artıran doğrusal
   fonksiyon)* — **anomali kasıtlı ekilir**
3. Kontrol edilmeyen sütunları rastgele/LLM ile doldur
4. Uzman not defteri: sıralı sorular + kod + görsel + **SMART hedef** + özet

Ground truth **ekilen trendin kendisidir** — kimse *"doğru cevap şu"* diye elle
yazmıyor. **`genisletme.py`'nin nedensel türetme tasarımı bu yöntemin tam da
gerektirdiği zemini kurmuş durumda** *(şikâyet sapan partiden doğuyor, iş emri gerçek
arızadan)*. Eksik olan tek şey: **olayın kasıtlı ve kayıtlı ekilmesi**.

**InsightBench'in dört içgörü sınıfı** bizim K1…K5 merdivenimizle örtüşüyor ve
**başarımın nerede çöktüğünü** de ölçmüş:

| sınıf | InsightBench başarımı |
|---|---|
| **Descriptive** *(ne oldu)* | 0,52–0,62 |
| **Diagnostic** *(neden)* | ↓ |
| **Prescriptive** *(ne yapmalı)* | ↓↓ |
| **Predictive** *(ne olacak)* | **en düşük** |

> 🔴 Bizim K3/K4/K5'in çökmesi **beklenen** desendir — ama InsightBench'inki 0'a değil,
> kademeli düşüyor. Bizimki **sıfır**. Fark, ölçtüğümüz katmanın sıfır-LLM olması.

⚠ **Ve bir eşik uyarısı:** InsightBench, **eğimi 0,1'in altındaki trendleri** hiçbir
modelin yakalayamadığını ölçmüş. Ekeceğimiz olayların **büyüklüğü**, ölçümün
anlamlılığını belirler — çok küçük ekilen bir olay *"sistem bulamadı"* değil *"ölçüm
kurulamadı"* demektir.

### 🟢 (b) **Yapısal Şablon Yeniden-Bileşimi** — *BEAVER yöntemi* → görev **#35**

BEAVER, gerçek kütüklerden **594 yinelenen analitik desen** çıkarıp bunları farklı şema
öğeleriyle sistemli olarak birleştirerek **8.874 doğrulanmış sentetik sorgu** üretmiş.

> 🔴 **Kritik kural: üreteç gerçeklikten TÜRETİLİR, hayalden değil.** Önce **gerçek
> iş yükünden desen çıkar**, sonra çoğalt. *"Saf sentetik üretimden kaçının."*

Bizde gerçek kütük yok — **ama muadili var**: `deneyim.py`'nin 15 senaryosu,
`REAL_PHRASINGS`'in 41 ifadesi, borç defterinin **canlı turlardan** gelen #16…#23
bulguları. Kombinatoryal üreteç bunların **deseni** üzerine kurulmalı; sıfırdan cümle
kurmamalı.

**BEAVER'ın ikinci dersi — tek sayı yerine alt görev anotasyonu:** her vaka için
*(tablo bulma · join · sütun eşleme · alan bilgisi · ayrıştırma)* ayrı ayrı işaretlenmiş.
Bu, *"kaçta kaç"* yerine **"nerede koptu"** demeyi sağlıyor. Bizim `gercek_dunya`
raporumuz bugün yalnız sınıf veriyor (`durust_ret`); **nerede koptuğunu** söylemiyor.

### 🔴 (c) **SQL2NL / şema-hizalı paraphrase** — *bize UYMUYOR, ve nedeni önemli*

Literatürde sorgudan otomatik, sözcüksel olarak çeşitli ama anlamca eşdeğer soru üreten
çerçeveler var (**SQL2NL**). Ölçek için cazip — **ama bizim probleminmizi büyütür**:
üretilen sorular **şema-hizalıdır**, yani §2'deki **sözlük yanlılığının ta kendisini**
otomatikleştirir. Katalogdan soru türetmeyi bırakmaya çalışırken, katalogdan soru
türetmeyi **sanayileştirmiş** oluruz.

> **Doğruluk ölçmek için kullanılmamalı. Yalnız §5'teki tutarlılık ölçüsü için
> kullanılabilir** — çünkü orada sorunun *nereden geldiği* değil, *aynı şeyi sorup
> sormadığı* önemlidir.

---

## 5 · 🔵 ALTIN CEVAP **GEREKTİRMEYEN** ÖLÇÜ — metamorfik tutarlılık

Bugünkü en büyük darboğazımız: `doğru` sütununu doldurmak için **her vakaya elle altın
cevap** gerekiyor. Literatürde bunu **tamamen atlayan** bir ölçü var.

**Metamorfik test** *(MT-TEQL çerçevesi)*: NL sorgusuna ve şemaya **anlam koruyan
dönüşümler** uygulanır; **beklenen sonuç, cevabın değişmemesidir**. Altın cevap
gerekmez — **kendi kendisiyle tutarlılık** ölçülür.

Ölçülmüş etkisi ciddi: paraphrase edilmiş Spider sorgularında yürütme doğruluğu
**%10,23** (LLaMa-3.3-70B) ve **~%20** (LLaMa-3.1-8B) düşüyor. *Yani standart kıyas
kümelerinin gösterdiğinden çok daha kırılgan.*

### 🔴 Ve bizim mimarimizi doğrudan ilgilendiren **asimetri**

| bozulma türü | kimi daha çok vuruyor |
|---|---|
| **Yüzey gürültüsü** *(yazım hatası, büyük/küçük harf, boşluk)* | **geleneksel tek-geçişli** hatlar |
| **Dilsel çeşitlilik** *(paraphrase, eşanlam, zaman/kip)* | 🔴 **ajanik (çok adımlı) kurulumlar** |

> Ajanik sistemler yüzey gürültüsünü **daha iyi**, dilsel çeşitliliği **daha kötü**
> kaldırıyor. Bizde **iki yol var**: deterministik `route()` *(tek geçiş)* ve
> Intent-JSON → Discovery *(ajanik)*. Bu bulgu, **hangi bozulmayı hangi yola karşı
> ölçmemiz gerektiğini** söylüyor — ve bugünkü korpusumuzda **yazım hatası vakaları var**
> (`ne kdr`, `musetri`, `mikatr`) ama **paraphrase vakası yok**. Yani şu an **yanlış
> yolun zayıflığını** ölçüyoruz.

**Yeniden uygulanabilir bozulma listesi** *(kaynak makalenin 10 türünden bize uyanlar)*:
`ButterFinger` (klavye-komşusu harf) · `SwapChar` (bitişik harf takası) ·
`ChangeCharCase` · `WhiteSpace` · **çekim/kip değiştirme** · **geri-çeviri**
(TR→EN→TR) · eşanlam ikamesi.

> 🔵 **Bu, #35'in en ucuz ve en yüksek getirili yarısı:** 42 vakadan, **altın cevap
> yazmadan**, yüzlerce türev üretilir; ölçü *"cevap aynı kaldı mı"*dır. Bugünkü
> `doğru = 0` dünyasında bile **anlamlı** çalışır: *aynı soruyu iki yazımla sorunca
> ikisinde de mi pes ediyor, yoksa birinde mi?* — bu, bugün cevabını **bilmediğimiz** bir
> soru.

---

## 6 · GÖREVLERE DÜŞEN — *ne benimsenmeli, ne benimsenmemeli*

| # | görev | araştırmanın söylediği |
|---|---|---|
| **#32** | seed'i süreç-zinciriyle büyüt | ✅ **`@bf5a7eb`'de kapandı** (33 tablo, `build()`'e bağlı). Referans bütünlüğü *"inşa gereği"* kuralı sektör standardı; **nedensel** bütünlük bir adım ötesi ve InsightBench'in enjeksiyon yöntemini mümkün kılan zemin |
| **#33** | ekilmiş kök-neden + manifest | 🟢 **Sıradaki gerçek iş · yöntem hazır**: matematiksel modelle trend ekle → ground truth **ekilen olayın kendisi**. ⚠ **Eşik uyarısı**: eğim 0,1 altındaki trend ölçülemez |
| **#34** | tabloları kataloğa aç | ✅ **`@bf5a7eb`'de kapandı** — katalog 13→23 cube. BEAVER'ın 101 tablo/869 sütun gerçeği, kataloğun **kendisinin** zorluk kaynağı olduğunu gösteriyor: 23 cube ile **artık ölçülebilir bir zorluk** var |
| **0** | 🔴 **korpusu yeniden koş** | **Listede olmayan, en ucuz adım.** Tek ölçüm katalog açılmadan (13 cube) alındı; 10 yeni cube'un kazancı **hiçbir sayıyla ifade edilmiyor** |
| **#35** | kombinatoryal üreteç | 🟡 **İkiye böl**: **(a)** metamorfik bozulma üreteci → **altın cevap gerekmez, hemen kurulabilir**; **(b)** desen-yeniden-bileşimi → **gerçek desenlerden** türetilmeli, hayalden değil. 🔴 SQL2NL paraphrase yolu **kullanılmamalı** (§4c) |
| **+yeni** | **kaynak dağılımı kapısı** | §2: tek kaynağın korpusa hâkim olması **ölçülen** bir yanlılık; bugün bizde `§9.6` hâkim |
| **+yeni** | **netleştirme İÇERİĞİ ölçüsü** | §3: *"netleştirdi mi"* ölçüyoruz, *"doğru şıkları mı sundu"* ölçmüyoruz (AmbiQT `BothInTopK`) |
| **+yeni** | **alt görev anotasyonu** | §4b: vaka başına *"nerede koptu"* — bugün yalnız sınıf var, teşhis yok |

---

## 7 · ⚠ NEYE DİKKAT — araştırmanın **bize uymayan** yanları

1. **Hepsi İngilizce ve çoğu tek geçişli SQL üretimi ölçüyor.** Bizim yüzeyimiz
   **Türkçe** ve **semantik katman** (cube) — SQL doğruluğu değil **ölçü/boyut seçimi**
   doğruluğu. Metrikler devşirilebilir, sayılar **kıyaslanamaz**.
2. **Türkçe morfoloji hiçbirinde yok.** `ButterFinger`/geri-çeviri gibi bozulmalar
   Türkçede **farklı** davranır (ekler, aksan). §5'in listesi **uyarlanmalı**, kopyalanmamalı.
3. **BEAVER'ın gerçek kütüğü var, bizim yok.** Onların *"saf sentetikten kaçının"*
   uyarısını karşılayan tek dayanağımız **canlı turlardan gelen borç defteri
   bulguları** — bu yüzden o kayıtlar korpusun **en değerli** kaynağı, `§9.6`
   türevleri değil.
4. **Hiçbiri okunmadan doğrulanmadı:** InsightBench ve BEAVER tam metin okundu; PRACTIQ
   **PDF'ten kısmi** çıkarıldı *(taksonomi başlıkları sıkıştırılmış akışta kaldı —
   kategori adları burada **iddia edilmiyor**)*; sözlük-yanlılığı makalesine **ACM 403**
   verdi, bulgu **arama özetinden** alındı → `[KISMİ]`.

---

## Kaynaklar

- [BEAVER: An Enterprise Benchmark for Text-to-SQL](https://arxiv.org/html/2409.02038v3) — 81% → 10,8%; şema ölçeği, oracle deneyi, Yapısal Şablon Yeniden-Bileşimi
- [Towards More Realistic Natural Language Queries in Text-to-SQL Benchmarks (HILDA)](https://dl.acm.org/doi/10.1145/3814573.3814945) — sözlük yanlılığı, anotasyoncu alt-grupları `[KISMİ — 403]`
- [LLM NL2SQL Robustness: Surface Noise vs. Linguistic Variation](https://arxiv.org/html/2603.17017v1) — asimetri: yüzey gürültüsü ↔ geleneksel hat, dilsel çeşitlilik ↔ ajanik; 10 bozulma türü
- [Evaluating NL2SQL via SQL2NL](https://arxiv.org/html/2509.04657) — şema-hizalı paraphrase; %10,23 / ~%20 düşüş
- [InsightBench: Evaluating Business Analytics Agents](https://arxiv.org/html/2407.06423v4) — trend enjeksiyonu, 475 içgörü, LLM-as-judge, içgörü sınıfı hiyerarşisi
- [PRACTIQ: Conversational Text-to-SQL with Ambiguous and Unanswerable Queries](https://arxiv.org/pdf/2410.11076) — netleştir/reddet/cevapla üçlüsü `[KISMİ]`
- [AmbiQT: Benchmarking and Improving Text-to-SQL Generation under Ambiguity](https://arxiv.org/pdf/2310.13659) — belirsizlik enjeksiyonu, `EitherInTopK` / `BothInTopK`
- [Interactive Text-to-SQL via Expected Information Gain for Disambiguation](https://arxiv.org/pdf/2507.06467) — hangi netleştirme sorusu sorulmalı
- [Referential Integrity: a Non-Negotiable (Perforce)](https://www.perforce.com/blog/pdx/synthetic-series-referential-integrity) — bütünlük **inşa gereği**, sonradan denetimle değil
- [Alibaba Cloud RCA Benchmark](https://www.alibabacloud.com/blog/alibaba-cloud-releases-rca-benchmark-the-industrys-first-open-source-root-cause-analysis-benchmark-system-for-agentic-ops_603252) — dört katmanlı ground truth: hata türü · varlık · **nedensel yayılım zinciri** · kanıt kenarı
