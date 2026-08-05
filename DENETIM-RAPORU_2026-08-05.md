# DENETİM RAPORU — *"planda olan ama geliştirilmeyen her şey"*

**Kapsam:** yol haritası ↔ `OPERASYON-DURUM.md` ↔ HEAD'in gerçek kodu.
**Bu turda geliştirme YAPILMADI**, hiçbir kaynak dosyaya dokunulmadı; yalnız tespit.

---

## 0 · Bu dosya ne değildir, ve neden sayı tutmuyor

🔴 **Bu dosya OTORİTE TAŞIMAZ.** Otorite sırası değişmedi: `OPERASYON.md` (kural seti) →
`OPERASYON-DURUM.md` (**durumun tek kaydı**) → yol haritası (ne yapılacak) → `MIMARI.md`
(değişmezler). Buradaki bulgular borç defterine geçtiğinde **bu dosya silinebilir**; ikinci
bir durum kaydı yaşatmak, deponun kendi avladığı *"aynı kural iki yerde"* sınıfını doğurur.

🔴 **Ve bu rapor bilerek SAYI TUTMAZ.** Denetim koşarken sistem gelişmeye devam etti;
iki bulgu **tur bitmeden çürüdü** — biri *"şu iş commit edilmemiş"* diyordu, commit edildi;
öteki *"şu kayıt hiç yok"* diyordu, yazılmaya başlandı. Ders açık: **rakam ve satır numarası
çürür, mekanizma çürümez.** Bu yüzden aşağıda kaç tane değil, **hangi sınıf** yazılı.
Sayı isteyen, `OPERASYON-DURUM.md`'nin ölçüm tabanına ve `lab/` araçlarına bakar — sayının
evi orasıdır, burası değil.

---

## 1 · ⚠ AGENT'A UYARI

**Depo paylaşılıyor ve canlı.** Bu denetim sırasında HEAD ilerledi ve çalışma ağacına
commit edilmemiş yeni iş girdi. Bir sonraki koşum, dokunmadan önce **kendi `git status`'unu
almak zorunda** — bu raporun anlattığı durum bile tek başına güvenilmez, çünkü rapor
yazılırken değişti.

**İkinci uyarı, daha kalıcı:** `OPERASYON-DURUM.md`'nin başlığı ve `ŞU AN` tablosu **geride
kalmış** — çoktan bitmiş bir fazı *"buradayız"* diye gösteriyor ve kapanmış fazlardan artakalan
sıra satırları duruyor. O dosya *"bağlam sıfırlanırsa buradan başla"* diye ilan edilmiş; bayat
kalırsa **bir sonraki agent yanlış fazdan devam eder**. Deponun en pahalı hatası bu olur,
çünkü sessizdir.

**Üçüncüsü:** borç defteri, fazlar kapandıkça **uzlaştırılmıyor**. Sahibi olarak *çoktan inmiş*
bir fazı gösteren borçlar var; kapandılar mı kapanmadılar mı yazılmamış. Bir borcun sahibi
kapanmış bir fazsa, o borç artık **sahipsizdir** — ve sahipsiz borç, unutulmuş borçtur.

---

## 2 · KARAR

> **Planda olan her şey geliştirilecek. Ölçüm HEDEF koyar, MADDE SİLMEZ.**

Bir ölçüm yalnız *bugünkü yapı* hakkında kanıttır; *planlanan yeteneğin var olup olmayacağı*
hakkında yetkisi yoktur. Bu operasyonda tersi oldu: ölçüme veto yetkisi verildi ve
§3/A'daki envanter böyle oluştu.

**"Hepsini geliştir" ile "sistemi bozma" çelişmiyor** — planın mekanizması zaten bunun için:

- **Her madde kendi bayrağıyla iner ve kapalı doğar.** `GERİ AL` sözleşmesi *"kapalıyken
  davranış birebir bugünkü"* der ve testlidir. **Geliştirmek risksiz; AÇMAK karardır.**
- **Bayraklar teker teker açılır.** Toplu açış, hangi bayrağın neyi kırdığını ölçülemez kılar.
- **Payda kutsaldır.** Korpus seyreltilmez, paralelleştirilir. Bir kapı, ölçmediği şeye
  *"geçti"* diyemez.

---

## 3 · BULGULAR — sınıf sınıf

### A · Ölçüm reddetti diye geliştirilmemişler *(ana bulgu)*

**"GÜVENCE" fazı bitti ilan edildi, ama üç ana teslimatı da üretimde kapalı:** veri tazeliği,
kolon düzeyi köken (`lineage`), metrik sertifikası. Üçü de yazıldı, testlendi, bayrağı `off`
bırakıldı.

Bu soyut değil: borç defterindeki canlı bulgulardan biri *"veri sonu tarihi hiç söylenmiyor;
kullanıcı üç turunu bunu keşfetmeye harcadı"* diyor. **O şikâyeti çözecek özellik yazılmış
hâlde kapalı duruyor.** Ödenmiş bir yeteneğin kullanıcıya ulaşmaması, hiç yazılmamasından
daha pahalıdır — çünkü bedeli ödendi ve karşılığı alınmadı.

Aynı sınıftan diğerleri:

- **Çok-turlu konuşma benchmark'ı kendi hedefini tutturamadı** ve kök nedeni isimlendirildi:
  takip mesajı **çıplak bir ikinci ölçü adı** olduğunda `deterministic_refine` bunu bir
  yenileme saymıyor, tur `route()`'a düşüyor, orada da tek başına ölçü adı taban üretmiyor.
  Defter *"bu turda düzeltilmedi, **bilerek**"* diyor.
- **`capa_zinciri` kapalı.** Çapa zinciri fazı indi ama bayrak `off`; yani çapa listesi hep
  boş kalıyor ve **karta yanıt verme kuralı üretimde hiç ateşlenmiyor**. Mekanizma var,
  yolu kapalı.
- **Netleştirme önceliği kapalı** — ve defter açıkça söylüyor: aynı ölçü adının iki farklı
  cube'ta yaşadığı, sistemin **sormadan birini seçtiği** ve iki cevabın milyonlarca lira
  ayrıştığı borcu bu bayrak **kapatmıyor**.
- **Kapsam merceği**, **prompt zenginleştirici**, **planlayıcı seçimi**, **guarded anlatıcı**
  — hepsi ölçüldü, hepsi kapalı ya da ertelenmiş bırakıldı.

⚠ Ayrım şart: kapalı bayrakların bir kısmı **meşru rollout kapısıdır** (uç kapalıyken 404
döner, davranış birebir aynı kalır). Sorun onlar değil; sorun **ölçüm-reddi** grubudur.

### B · Yazıldı ama erişilemez — *"beyan var, yolu yok"*

- 🔴 **Diyalog yöneticisi.** Takip sorusunu sınıflandıran fonksiyonun **tek çağrı yeri**,
  `ask.py`'de *yapısal takip* dalının **içinde**. Yani istemci önceki sorguyu taşımıyorsa
  (Discovery ya da ham thread), **konuşma türlerinin hiçbiri sınıflanmıyor** — *"bu neden
  böyle?"*, *"normal mi?"*, *"analiz et"* o thread'lerde yapısal olarak erişilemez. Üstelik
  fonksiyonun *"bağlam yok"* kolu **sabit bir doğruyla** çağrıldığı için üretimde hiç
  ateşlenmiyor; yalnız birim testinde yaşıyor. Bu bayraksız bir **hata** olarak planda ve inmedi.
- **Konuşma türü sayısı v1 hedefinin altında** — *"bunu takip et"* ve *"paylaş / müdüre üç
  cümle yaz"* türleri yok. İkincisinin motoru **zaten çalışıyor**; eksik olan sadece
  kullanıcının kelimeleri.
- **Dönem-yalnız sorgu yordayıcısı hâlâ çağrısız** — yazıldı, kimse kullanmıyor. Yetim
  fonksiyon, yetim uç ile aynı sınıf.

### C · Karar kaydı, kodun gerisinde

Mimari kararlara metinlerde bolca atıf var ama **dosyaları yeni yeni yazılıyor** (bu turda
uçuşta yakalandı). Daha önemlisi: **en yüksek numaralı karardan sonra inen faz-düzeyi
kararların hiçbirinin kaydı yok** — grain sözleşmesi, çekirdek katman, kapsam merceği, mali
takvim, sahiplik hakemi, semantik model ithal/ihracı, makine yüzeyi. Yani kayıt **kodun
yaklaşık iki faz gerisinde**. Kapatılan iş bu boşluğu gerçekten kapatıyor mu, **kapsamı
doğrulanmalı** — dosya saymak yetmez.

### D · Hiç başlanmamış planlı iş

- **Konuşma ve deneyim fazının tamamı** — tek maddesi bile inmedi. Diyalog yönetiminin
  bütünü burada oturuyor.
- **Agentic ve onaylı yazma fazı** — bir kararın *bugün ters uygulandığını* söyleyen ve
  *"yapılanı geri al"* diyen madde dahil.
- **Arayüz fazı** — ve panel tavanı zaten **dolu**; yeni yüzey açmak yerine var olanı
  düzeltmeyi zorunlu kılıyor.
- **Açılma fazı** — gerçek kullanım penceresi, yani kalıp sözlüklerini kullanıcının kendi
  ifadeleriyle besleyecek kaynak.
- **Ölçüm fazının kuyruğu** — ve burada **yazılı bir bağımlılık** var: teknik rapor,
  benchmark'ın hedefi tutturamamış sayısına bağlı; **o düzelmeden yayımlanamaz.**

Ayrıca `MIMARI.md`'nin kendi *"yürürlükte ama uygulanmadı"* indeksi duruyor: konuşma türleri,
görsel dilbilgisi, ajan yazma yasağının kademelenmesi — hepsi mimaride yazılı, kodda yok.

*(Bölüm II'nin v2/v3 maddeleri bu listeye dahil değil: onlar **bilinçli ve kayıtlı**
ertelemeler, borç değil.)*

### E · Ölçümün kendi körlükleri

- Süitte hatırı sayılır bir **atlanan/xfail** kütlesi var; kapı yeşilken ölçülmeyen alan
  kalıyor.
- **Korpus, yazım-hatası yolunu hiç sormuyor.** `CLAUDE.md`'nin kendi beyanı: korpus
  yeşilken gerçek kullanıcı deneyimi kırık olabilir. Nitekim *"çıkışsız yazım düzeltmesi"*
  borcu tam buradan geldi ve **canlıda yeniden üretildi**.
- **Deneyim süitinin çoğunluğu hiç koşmuyor.** Koşmayan vaka, geçen vaka değildir.

---

## 4 · RİSKLER — geliştirirken sistemi bozacak üç yer

1. 🔴 **Ölçü-ekleme kapısını genişletmek korpusu geriletebilir.** Çıplak ölçü adını tanıtmak,
   bugün **boyut** sanılan kelimeleri ölçüye çekebilir. Bu maddenin kapısı **yalnız benchmark
   değil, benchmark + korpus birlikte** olmalı — konuşma düzelirken katalog bozulursa net
   zarardayız.
2. 🔴 **Çapa zincirini açmak yol değiştirir.** Çapa kuralı ateşlenmeye başladığı an, bugün
   yapısal daldan akan **her tur** başka bir koldan geçer. Kendi turunda, kendi kapısıyla
   açılmalı; başka bir maddeyle aynı commit'e girmemeli.
3. ⚠ **Diyalog yöneticisi sıralamaya duyarlı.** Sınıflandırma çağrısı bloktan çıkarılırken
   yapısal thread'lerdeki **mevcut sıra korunmalı**: cube adı göçü → bayat sorgu kontrolü →
   yetenek sorusu → konuşma → görünüm değişikliği → yenileme. Sırayı bozmak **sessiz**
   gerileme üretir; bu deponun daha önce ölçtüğü hata sınıfı tam olarak budur.

---

## 5 · SIRA ÖNERİSİ *(planın kendi sırasını bozmadan)*

1. **Uçuştaki işi kapat ve commit et** — kayıp riski en yüksek olan şey, yarım kalmış iştir.
2. **`OPERASYON-DURUM.md`'yi bugüne uydur:** başlık, `ŞU AN` tablosu, ölçüm tabanı ve borç
   defteri uzlaştırması. Bu, bir sonraki bağlam sıfırlanmasının hayatta kalma şartıdır.
3. **Ölçüm fazını bitir** — teknik raporun bağımlılığı yazılı, o düğüm çözülmeden ilerlenmez.
4. **Konuşma fazına planın sırasıyla gir: önce erişim hatası, sonra kalıp sözlüğünün kök
   nedeni, en son yeni türler.** Sözlüğü kullanıcının kelimeleriyle beslemeden yeni tür
   eklemek, aynı duvarı bir kez daha örer — çünkü ilk duvar da tasarımcının kelimelerinden örüldü.
5. **Kapalı bayrakların açılışını ayrı bir tur yap.** Geliştirme ile açış aynı commit'e
   girmesin: biri risksiz, öteki kararlı.

---

## 6 · KAPANIŞ

Kod tarafında ilk fazlar gerçekten bitmiş, ölçüm fazı son maddelerinde. Asıl açık
*"yazılmadı"* değil — **yazıldı, ölçüldü, ölçüm hoşa gitmedi diye kapalı bırakıldı.**

Çapa zinciri + diyalog yöneticisinin erişim hatası + çıplak ölçü adının tanınmaması: bu üçü
birlikte **tek bir şeyi** verir — *çalışan bir diyalog yöneticisi*. Üçü de yazılı, üçü de
kapalı ya da erişilemez, üçünün de planda evi belli.

**Bundan sonrası plana uyar:** madde sırası, `KAPI` şartları, `GERİ AL` sözleşmesi, demet
disiplini. Ölçüm koşulur, **sonucu kaydedilir, maddeyi iptal etmez.**

---

# ✅ KAPANIŞ — bu raporun bulguları BORÇ DEFTERİNE GEÇTİ (@`7f3667a`)

Rapor kendi ömrünü §0'da ilan etmişti: *"buradaki bulgular borç defterine geçtiğinde bu
dosya silinebilir; ikinci bir durum kaydı yaşatmak, deponun kendi avladığı «aynı kural
iki yerde» sınıfını doğurur."* Bu bölüm o geçişin kaydıdır — **dosya artık silinebilir.**

| # | Bulgu | Kapanış | Kanıt |
|---|---|---|---|
| **D1** | Çıplak ikinci ölçü adı tanınmıyor (§3A · §6) | ✅ | düşüş **−%18,2 → −%4,5**, `kaldi` → `gecti`, korpus **sabit** |
| **D2** | ADR kaydı kodun ~2 faz gerisinde (§3C) | ✅ | **ADR-0025…0034**, kararın yaşadığı yere atıflı, kapı **köken beyanına** çevrildi |
| **D3** | `is_period_only` yetim fonksiyon (§3B) | ✅ | **önce şartname taşındı, sonra kaldırıldı** — 13 ifade artık `deterministic_refine` üstünde ölçülüyor |
| **D4** | `capa_zinciri` kapalı — kural hiç ateşlemiyor (§3A · §6) | ✅ | **beta**; senaryolar tabanda, kural ateşliyor, çelişkide **soruyor** |
| **D5** | Deneyim süitinin çoğunluğu koşmuyor (§3E) | ✅ | *"63 ⊘"* ölçüldü: **60 tasarım + 3 gerçek risk**; iki üçüncü hâl **ayrıldı** |
| — | Diyalog yöneticisinin erişim hatası (§3B) | ✅ | FAZ 5.0 |
| — | 6./7. konuşma türü (§3B) | ✅ | FAZ 5.1 · 5.2 |
| — | Kalıp sözlüğünün kök nedeni (§5/4) | ✅ | FAZ 5.3 — sözlük **kullanıcı ifadelerinden** besleniyor |
| — | `OPERASYON-DURUM.md` bayat (§1) | ✅ | başlık + `ŞU AN` + borç defteri uzlaştırıldı |

## 🔴 Raporun §6'daki üçlüsü TAMAMLANDI

> *"Çapa zinciri + diyalog yöneticisinin erişim hatası + çıplak ölçü adının tanınmaması:
> bu üçü birlikte **tek bir şeyi** verir — çalışan bir diyalog yöneticisi."*

Üçü de kapandı.

## ⚠ Raporun kendi dersi, ölçümle DOĞRULANDI

Rapor §4/risk-1'de *"çıplak ölçü adını tanıtmak, bugün **boyut** sanılan kelimeleri ölçüye
çekebilir"* diyordu ve **haklı çıktı**: `test_capraz_cube_gecis_notu` kırmızı verdi
(*"kumaş cinsine göre fire oranı bu yıl"* bir konu değişimidir, ekleme sanıldı).

⚠ Ama uyarının önerdiği kapı (**benchmark + korpus**) bile **yetmedi** — korpus bunu
görmedi (%93,1 birebir), yakalayan **altın süit** oldu. *Bir riskin ölçülmemesi, yokluğu
değildir* ve bir kapının kapsamı, ölçtüğü şey kadardır.

## ⏸ Kapanmayan — ve neden

**§3A'nın kalan `off` bayrakları** (`tazelik` · `lineage` · `metrik_sertifikasi` ve
diğerleri) **bilerek açılmadı**: raporun kendi §5/5'i *"kapalı bayrakların açılışını ayrı
bir tur yap"* diyor ve her açış **kendi ölçümünü** ister. Bu turda ölçümü yapılan iki
bayrak (`olcu_ekleme_takibi` · `capa_zinciri`) açıldı; kalanlar borç defterinde **sahibiyle
birlikte** duruyor.
