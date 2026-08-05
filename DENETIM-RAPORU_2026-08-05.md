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

---
---

# İKİNCİ TUR — *rapordan SONRAKİ dünyanın denetimi* · 2026-08-05 @`cb321fd`

> 🔴 **Bu bölüm bir DENETİMDİR, bir geliştirme turu değil.** Hiçbir kaynak dosyaya
> dokunulmadı; yalnız okundu, `grep`lendi, AST'si çıkarıldı.
>
> ⚠ **ÇAKIŞMA YASAĞI — kasten uygulandı.** `V1-SON-KONTROL.md`'nin ölçtüğü hiçbir sayı
> burada **tekrar edilmez** (kapı sonuçları · §C'nin 16 ölçütü · yedi açık borç · FAZ 7-8'in
> sekiz kusuru · kapıların yedi kendi kusuru). O dosya **o ölçümlerin evidir**; burada
> yalnız **oraya girmemiş** olan yazılıdır. İki durum kaydı yaşatmak, §0'ın yasakladığı
> şeydir.
>
> §0'ın *"bu rapor sayı tutmaz"* kuralı bu bölümde **daraltılarak** korunuyor: aşağıdaki
> her sayının **yanında onu üreten komut** vardır (kural D2). Sayı çürüdüğünde komut
> koşulur; rapor değil **ölçüm** otoritedir.

## ⚠ AGENT'A UYARI — birinci turdaki uyarı YİNE GERÇEKLEŞTİ

Bu denetim koşarken HEAD **iki kez ilerledi**: tur başında çalışma ağacında commit
edilmemiş iş vardı (`app/discovery_kuyrugu.py` · `app/gorsel_ekleme.py` yeni,
`routers/ask.py` −183 satır), tur biterken o iş `cb321fd` olarak **commit edilmişti**.
Depo paylaşılıyor ve canlı. **Bir sonraki koşum kendi `git status`'unu almak zorundadır.**

---

## §7 · FAZ FAZ TARAMA — *"planda olup kaydı olmayan"*

**Yöntem:** yol haritasının **Bölüm I**'i (v1) ayrıştırıldı → **98 madde başlığı**; her
madde kimliği hem `OPERASYON-DURUM.md`'de hem git kütüğünde arandı.

```bash
# madde envanteri + durum/kütük kesişimi
python3 - <<'EOF'
import re,pathlib
d=pathlib.Path('~/.claude/plans/DIMA-V1-YOL-HARITASI.md').expanduser().read_text()
sec=d[d.index('# BÖLÜM I — v1'):]
print(len(re.findall(r'^### (−?\d+\.\d*[a-z]?)\s*·', sec, re.M)))
EOF
git log --format=%B -100 | grep -c "faz "
```

### 7.1 · 🔴 **Tek madde bulundu: `3.0` — hiçbir yerde yok**

| Madde | Ne | Durum kaydı | Git kütüğü | Kod |
|---|---|---|---|---|
| **`3.0` ⭐ Tenant açılışı — uçtan uca zincir** *(D8)* | `db_introspect → Ossie ithali (3.4) → cold-start (3.6) → sahiplik turu (3.1) → ilk nl_corpus koşumu` | ⊘ **anılmıyor** | ⊘ **hiç geçmiyor** | halkalar var, **zincir hiç koşulmadı** |

Diğer 97 maddenin **hepsi** ya durum kaydında ya commit mesajında geçiyor — yani
*"sessizce atlanan madde"* sınıfı **tek elemanlıdır**. Ama o tek eleman ağırdır ve
üç sebeple:

1. **Maddenin kendi metni onu bir geliştirme değil bir KOŞUM olarak tanımlıyor:**
   *"Yeni motor yazılmıyor — zincirin her halkası zaten var; eksik olan **uçtan uca hiç
   koşulmamış olması**."* Yani ucuz bir madde, ve ucuzluğu **atlanmasının gerekçesi
   değil, atlanmasının utancıdır**.
2. **Kapısı `§C/14`'tür** — *"yeni bir tenant için ilk doğru cevaba kadar İNSAN-SAAT"*.
   `V1-SON-KONTROL.md` ölçüt 14'ü ✅ sayıyor; **ölçütün ölçüm aracı ise bu madde.**
   ⚠ Bu bir çelişki iddiası değil, bir **kapsam doğrulama talebidir**: 14'ün yeşili
   `3.0` koşulmadan verildiyse, neye dayandığı yazılmalı.
3. **Maddenin kendi `SONUÇ` cümlesi ticari:** *"3.4 bir FAZ 3 maddesi değil, ürünün
   ticari kilididir."* Kilit denenmedi.

> 🔴 **Ve `3.0` bir taşımanın hedefiydi:** *"(8.2 buraya taşındı; FAZ 8'de yalnız 8.3
> kalır.)"* — yani `8.2` **silinmedi, buraya taşındı** ve burası **hiç açılmadı**.
> Bir maddeyi taşıyıp hedefini açmamak, onu **kütükle birlikte kaybetmektir**.

### 7.2 · Planlanan bayrak ↔ gerçek bayrak — **19 ad tutmuyor**, üçü gerçek borç

```bash
# planda [bayrak: x] geçen adlar ↔ FLAG_REGISTRY anahtarları
grep -oE '\[bayrak: [^]]*\]' ~/.claude/plans/DIMA-V1-YOL-HARITASI.md | sort -u
python3 -c "import ast,pathlib;t=ast.parse(pathlib.Path('backend/app/features.py').read_text());
print(len([k for n in ast.walk(t) if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','')=='FLAG_REGISTRY' for k in n.value.keys]))"
```

| Sınıf | Adlar | Yargı |
|---|---|---|
| **§G / ajan katmanı** *(7)* | `diyalog` · `referans_dili` · `tur_yoneticisi` · `calisirken_sorma` · `oturumlar_arasi_hafiza` · `adim_zinciri` · `bilesik_rapor` | ✅ **borç değil** — §B: §G **v1'e paralel ayrı sürüm izi**, v1 kapısına girmez |
| **`Settings` olarak indi** *(4)* | `motor_rls` · `motor_cls` · `yazma_araclari` · `netlestirme_duzeyi` | ◐ **meşru ama beyanı bayat** — üçünün gerekçesi `config.py`'de **yazılı** (import zamanı / istek bağlamı yok). ⚠ `netlestirme_duzeyi` `TenantConfig` alanı olarak indi ama modülün docstring'i hâlâ `[bayrak: …]` diyor → **beyan ↔ kod ayrışması** |
| **Bilinen/kayıtlı bloke** *(2)* | `peer_kiyasi` *(5.6 ← AJ2)* · `ui_settings_tam_sayfa` *(7.7)* | ✅ borç defterinde sahibiyle duruyor |
| **Kanal bayrakları** *(3)* | `kanal_slack` · `kanal_whatsapp` · `sabah_digest` *(5.9)* | 🔴 **hiçbir yerde yok** — `app/channels.py`'de Slack **kaydı** var, bayrak yok; yani 5.9'un `GERİ AL` sözleşmesi **uygulanamaz** |
| 🔴 **Kapısız kaldı** *(3)* | `coldstart_metrik` *(3.6)* · `ui_metrik_yonetimi` *(2.2b)* · `netlestirme_kapanisi` *(0.5b)* | 🔴 **GERÇEK BORÇ** — aşağıda |

**`coldstart_metrik`:** `app/coldstart.py`'nin **birinci satırı** `[bayrak:
coldstart_metrik]` diyor; o ad ne `FLAG_REGISTRY`'de ne `features.yml`'de ne
`config.py`'de var. Modülün tek üretim çağıranı `mdl_writer.py:344`
(`gorunur_kolonlar`) ve o çağrı **kapısız**. Yani FAZ 3.6 **`GERİ AL` sözleşmesi olmadan
üretimde canlıdır** — planın *"her madde kendi bayrağıyla iner ve kapalı doğar"*
mekanizmasının **dışında**.

**`netlestirme_kapanisi` (`0.5b` — bekleyen netleştirme, DURUMSUZ):** ad **hiçbir
dosyada geçmiyor** (`app/` · `tests/` · `config.py` → 0). Madde sohbet raporunun M4/B3
bulgusundan doğmuştu. `0.5` (çapa zinciri) indi, `0.5b` **inmedi ve atlandığı yazılmadı**.

---

## §8 · 🔴 BU TURUN ANA BULGUSU — **«yetim modül» sınıfı**

Birinci tur *"yazıldı ama erişilemez"* diye bir sınıf açmıştı (§3B) ve içine **iki**
kalem koymuştu (diyalog yöneticisi · `is_period_only`). O sınıf **çok daha büyük çıktı.**

**Ölçüm** — `app/` altındaki her modülün `app/` içinden **gerçekten import edilip
edilmediği** (AST ile; alt-dize değil, `import` deyimi):

```bash
cd backend && python3 - <<'EOF'
import ast,pathlib
app=pathlib.Path('app'); mods={p.stem for p in app.glob('*.py')}-{'__init__'}
imp=set()
for p in app.rglob('*.py'):
    for n in ast.walk(ast.parse(p.read_text(errors='ignore'))):
        if isinstance(n,ast.ImportFrom) and ((n.module or '').startswith('app') or n.level):
            imp |= {a.name for a in n.names} | {(n.module or '').split('.')[-1]}
        elif isinstance(n,ast.Import):
            imp |= {a.name.split('.')[-1] for a in n.names}
print(sorted(m for m in mods if m not in imp))
EOF
```

**Sonuç: `app/`'in 86 modülünden 12'si, ÜRETİM KODUNDA HİÇ IMPORT EDİLMİYOR** — tek
kullanıcıları **kendi testleri**.

| Modül | satır | Faz | Testi | Üretimde çağıranı |
|---|---|---|---|---|
| 🔴 `certification.py` | 165 | **1.5** metrik sertifikası | `test_sertifikasyon.py` | **0** |
| 🔴 `tazelik.py` | 146 | **1.7** tazelik merdiveni | `test_tazelik.py` | **0** |
| 🔴 `onay_akisi.py` | 207 | **6.1** onay akışı | `test_onay_akisi.py` | **0** |
| 🔴 `rules.py` | 124 | **5.13b** kural motoru | `test_rules.py` | **0** |
| 🔴 `bildirim_kapisi.py` | 146 | **5.9** bildirim kapısı | `test_bildirim_kapisi.py` | **0** |
| 🔴 `netlestirme.py` | 107 | **5.16** netleştirme düzeyi | `test_netlestirme_duzeyi.py` | **0** |
| 🔴 `kpi_pin.py` | 85 | **5.10** KPI pin | `test_kpi_pin.py` | **0** |
| 🔴 `kanal_kimlik.py` | 80 | **6.6** kanal kimliği | `test_kanal_kimlik.py` | **0** |
| 🔴 `sinonim_onerici.py` | 130 | **§4.5** sinonim önerici | `test_sinonim_onerici.py` | **0** |
| ◐ `bayrak_profilleri.py` | 110 | **0.20** bayrak profilleri | `test_bayrak_profilleri.py` | **0** *(kapı aracı — meşru olabilir)* |
| ◐ `embed_kapsam.py` | 97 | **6.5** embed P0 | `test_public_api.py` | **0** *(bilerek: P0 kapısı)* |
| ◐ `packs.py` | 75 | ADR-0005 pack keşfi | — | **0** *(ölü kalıntı olabilir)* |

**Toplam ≈ 1.470 satır ürün kodu, sıfır üretim çağrısı.**

### 8.1 · Neden hiçbir kapı bunu yakalamadı — **kapının kendi kör noktası**

Depoda **üç** yetim kapısı var (`uc_yetim` · `cevap_alani_yetim` · `ters_yetim`) ve üçü
de **yeşil**. Sebep, üçünün de **beyan ↔ beyan** kıyaslaması yapması:

- `test_ters_yetim.py` *"`types.ts`'te okunan her alan `schemas.py`'de var mı"* diye
  sorar. `tazelik.py`'nin ürettiği `freshness` alanı **`schemas.py:355`'te VAR** →
  kapı yeşil. Ama o alanı **dolduran hiçbir kod yok** (`grep -rn "freshness" backend/app/`
  → yalnız `tazelik.py`'nin kendi içi + şema beyanı + `lineage.py`'nin yorumu).
- `ReportCard.tsx:743` `item.freshness === "hata" || "bilinmiyor"` diye **tüketiyor**.
  Yani ekranda **tüketicisi olan, üreticisi olmayan** bir alan var.

> 🔴 **Sınıfın adı konuldu:** deponun kendi dersi *"bir TİP BEYANI tüketici değildir"*
> idi. **Aynası eksikti: bir ŞEMA ALANI da üretici değildir.** Bugünkü üç kapı
> *"alan iki tarafta da yazılı mı"* diye sorar; sorması gereken *"bu alanı bir istek
> yolunda **kim dolduruyor**"*dur.

### 8.2 · Bunun ölçütlere dokunduğu yer

⚠ Aşağıdakiler `V1-SON-KONTROL.md`'nin ölçüt yargılarını **tekrar etmiyor**, onlara
**yeni bir kanıt** ekliyor:

- **Ölçüt 12 (tazelik)** sarı yazılmış, gerekçe *"bayrak `off`"*. **Ölçüm daha ağırını
  söylüyor: bayrak `off` DEĞİL, bayrak KAPISIZ.** `"tazelik"` dizgesi hiçbir
  `resolve_for` çağrısında geçmiyor → bayrağı `prod`'a çekmek **hiçbir şeyi
  değiştirmez.** Borç *"açılmayı bekleyen özellik"* değil, **"bağlanmamış özellik"**.
- **Ölçüt 6 (onaysız yazma)** 🟢. Bu doğru ama **yarısı için**: D9'un *"kapsam içi iş
  istemsiz koşar"* yarısı `routers/ask.py` + `app/eylem.py` üzerinden **gerçekten
  bağlı** *(`grep -n '"onay_akisi" in resolve_for' backend/app/routers/ask.py` — ⚠ satır
  numarası bilerek yazılmadı: `ask.py` bu tur içinde **yeniden düzenlendi**, numara çürür)*. `onay_akisi.py`'nin taşıdığı öteki yarı — **onay kapsamı nesnesi · riske göre
  senkron/kuyruk yönlendirmesi · 30 dk SÜRE AŞIMI** — hiçbir istek yolunda **yok**.
  Modülün kendi başlığı *"tek modül, **beş tüketici**"* diyor; ölçülen tüketici **sıfır**.
  🔴 Bu bir **beyan ↔ kod ihlalidir** (`OPERASYON.md` B/6) ve *"süresi geçmiş bir onayla
  çalıştırma reddedilir"* hükmü bugün **uygulanmıyor**.

### 8.3 · Bayrak sisteminin **iki sahibi** — `cekirdek_katman`

```bash
grep -rn "cekirdek_katman" backend/app/config.py backend/app/cekirdek.py backend/app/features.py
```

`cekirdek_katman` **hem** `FLAG_REGISTRY` + `features.yml`'de (`off`) **hem** de
`Settings`'te (`config.py:184`, `off`) tanımlı. Kodu okuyan **tek yer**
`cekirdek.py:95` ve o **`Settings`'i** okuyor. Yani:

> 🔴 **Admin panelden ya da `features.yml`'den `cekirdek_katman`'ı açmak HİÇBİR ŞEY
> YAPMAZ.** Bayrak kaydındaki girdi **dekoratiftir.**

FAZ 7.1 tam bu sınıfı **frontend için** kilitlemişti (*"sessizce ölen bir özellik,
yazılmamış bir özellikten kötüdür"*). Aynı kilit **backend için kurulmamış**: bir adın
`FLAG_REGISTRY`'de olup hiçbir `resolve_for` çağrısında geçmemesi bugün **serbest**.

### 8.4 · Kapısız bayrakların tam listesi *(9)*

```bash
# bir bayrak adı, resolve_for/useFeature geçen bir satırda geçiyor mu?
grep -rn "resolve_for" backend/app --include=*.py | grep -oE '"[a-z_]+"' | sort -u
grep -rhoE 'useFeature\("[a-z_]+' dima-frontend-demo-master/src | sort -u
```

| Bayrak | Faz | Kapı | Yargı |
|---|---|---|---|
| `tazelik` | 1.7 | ✘ | 🔴 bağlanmamış |
| `metrik_sertifikasi` | 1.5 | ✘ | 🔴 bağlanmamış |
| `kpi_pin` | 5.10 | ✘ | 🔴 bağlanmamış |
| `kanal_kimlik` | 6.6 | ✘ | 🔴 bağlanmamış |
| `threaded_chat` | — | ✘ | 🔴 bağlanmamış |
| `public_api` | 6.5 | ✘ | 🔴 `app/` içinde **adı bile geçmiyor** |
| `cekirdek_katman` | 2.1 | ✘ | 🔴 **iki sahip** (`Settings` kazanıyor) |
| `embed` | 6.5 | ✘ | ◐ **bilerek** — P0 ölçülmüş, açılamaz |
| `ayni_grain_gocu` | 2.4 | ✘ | ✅ **beyanlı** istisna (`test_bayrak_kaydi_butun.py`) |

**Kalan 33 bayrağın kapısı var** ve doğrulandı (26 backend · 10 frontend, kesişim 3).

---

## §9 · 🔴 ÖLÇÜMÜN GEÇERLİLİĞİ — *"testler koda göre yazıldığı için yüksek çıkıyor"*

> **Kullanıcı direktifi (2026-08-05):** *"testler koda göre yazıldığı için yüksek çıkıyor
> meselesini de çözmemiz lazım… testleri gerçek dünyaya göre genişletelim, gerçek
> case'lerle, gerçek dünyadaki ihtimalleri düşünerek; kendini CEO/müdür/yönetici/kullanıcı
> yerine koysun, en basitten en karmaşığa tüm soruları düşünsün."*

**Bu şüphe ÖLÇÜLDÜ ve HAKLI ÇIKTI.** Aşağıdaki dört bulgu, oranların neden yüksek
olduğunu **mekanizmayla** açıklıyor.

### 9.1 · Korpus, soruyu **sistemin kendi sözlüğünden** kuruyor

`lab/nl_corpus.py::gen_single()` soruları şöyle üretiyor:
`_measure_words(cube)` → cube'un **`measure_synonyms_display`**'i · `_dim_words(cube)` →
cube'un **`dimension_labels`**'ı. Yani soru, **cevabın anahtarından** türetiliyor.

```bash
sed -n '/^def gen_single/,/^def gen_processes/p' backend/lab/nl_corpus.py
python3 -c "
import ast,pathlib
t=ast.parse(pathlib.Path('backend/lab/nl_corpus.py').read_text())
for n in ast.walk(t):
  if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','') in ('REAL_PHRASINGS','NOISE','CAPABILITY'):
    v=ast.literal_eval(n.value); print(n.targets[0].id, sum(len(x) for x in v.values()) if isinstance(v,dict) else len(v))"
```

| Kaynak | Kaç soru | Nasıl yazıldı |
|---|---|---|
| **Katalog türevi** | `boyahane` tekilinin **≥%97'si** | ölçü/boyut **etiketinin kendisi** × 11 dönem × 4 boyut × 4 niyet |
| `REAL_PHRASINGS` *(gerçek kullanıcı dağarcığı)* | **13 ölçü · 41 ifade** × 3 dönem = **≤123** | elle yazılmış, etiket kelimesini **dışlıyor** |
| `NOISE` | **15** | gürültü/kötü niyet |
| `CAPABILITY` | **8** | *"neler yapabilirsin"* |

> Hesap (boyahane, `lab/reports/nl_corpus.md:5`): tekil senaryo **5077**;
> `5077 − 123 − 23 = 4931` → **≥%97,1 katalog türevi.**

🔴 **Bunun anlamı:** korpus *"sistem kendi kelimelerini tanıyor mu"* sorusunu ölçüyor —
**ve o soruya %93 vermek şaşırtıcı değil, beklenendir.** Ölçülmeyen soru şu:
*"kullanıcının kelimelerini tanıyor mu?"* — payda içindeki **≤%2,4**'lük dilim.

⚠ Aracın kendisi bunu **itiraf ediyor** (`nl_corpus.py:152`): *"üreteç yalnız kataloğun
bildiği ifadeleri kurar; bir kusur sınıfı korpusta **yapısal olarak görünmez** olabilir."*
Yani körlük **biliniyordu ve kayıtlıydı** — kapatılmadı.

### 9.2 · Payda **çarpımla şişiyor**, hata **tek terimle** çöküyor

Rapor dosyasının kendi satırı (`nl_corpus.md:6`): boyahane'de **şişme katsayısı 27,9×**
(5306 ham tur ↔ 190 semantik vaka); diğer üç şirkette **21,3× · 19,5× · 24,1×**.
`elektrik`in tek sahiplik hatası, 11 dönem × boyut ile **10+ ayrı başarısızlık** olarak
sayılıyor — ve doğrular da aynı katsayıyla çoğalıyor. **Yüzdenin içi bir çarpımdır.**

### 9.3 · Korpus **cevabı hiç görmüyor**

`nl_corpus.py`'nin kendi girişi: *"`/ask` HTTP yolunu TAM koşar ama **DB'ye BAĞLANMAZ** —
`execute=False` + enrichment no-op… **LLM yok** (rule provider)."*

Dolayısıyla korpusun ölçtüğü şey **yönlendirmedir**: doğru cube seçildi mi. Ölçmediği
şeyler: **sayının doğruluğu** · **anlatının doğruluğu** · **ekranda ne göründüğü** ·
**LLM'li yolun davranışı** · **çok turlu bağlam**. §C/16'nın uçtan uca aracı (`4.8`)
bunu ayrıca ölçüyor — ama **tek şirkette** (`demo-boyahane`), diğer üçü `⊘`.

### 9.4 · Yetim modül testleri **yapısal olarak yeşil**

§8'in 12 modülünün her biri testinde **doğrudan import** ediliyor
(`from app import tazelik as T`) ve **saf fonksiyonları** doğrulanıyor. Böyle bir test:

- modül **hiç çağrılmasa da** yeşildir,
- bayrak **kapısız** olsa da yeşildir,
- kullanıcı o özelliği **hiç göremese** de yeşildir.

> 🔴 **Sınıfın adı: «birim yeşili, sistem kırmızısı».** Bu, *"testler koda göre yazıldı"*
> şüphesinin **en somut kanıtıdır**: test, modülün **kendi sözleşmesini** doğruluyor;
> modülün **ürüne bağlı olup olmadığını** hiç sormuyor.

### 9.5 · Gerçek-dünya yüzeyleri **var ama küçük**

| Süit | Boyut | Ne ölçüyor |
|---|---|---|
| `lab/deneyim.py` | **15 senaryo · 58 tur** | çok turlu gerçek konuşma *(persona izleri: `uretim_muduru_sabahi` · `yazim_hatali_gercek_kullanici`)* |
| `eval/cases.yaml` | **119 vaka** | altın cevap |
| `tests/test_ask_golden.py` | **80 test** | altın süit *(çapraz-cube geçişini korpus kaçırırken **bu** yakaladı)* |
| `REAL_PHRASINGS` | **41 ifade** | katalog dışı dağarcık |

Yani gerçek-dünya kapsamı **toplamda birkaç yüz vaka**, katalog türevi korpus ise
**7.000+ tur**. Ağırlık merkezi yanlış yerde: **ölçümün %97'si en kolay soruya bakıyor.**

### 9.6 · 🔵 ÖNERİ — *gerçek-dünya korpusu*: persona × zorluk merdiveni

> ⚠ **Bu bir PLANDIR, uygulanmadı.** Denetim geliştirme yapmaz; madde açılması
> kullanıcının kararıdır. Aşağısı, açılırsa **nasıl** yazılacağının şartnamesidir.

**Kural 0 — payda kutsaldır.** Yeni korpus **var olanın yerine geçmez**, **yanına**
kurulur (`lab/gercek_dunya.py`). Eski taban bozulursa geçmiş ölçümler karşılaştırılamaz.

**Kural 1 — soru, cevabın anahtarından TÜRETİLMEZ.** Bir soru ancak **etiket kelimesini
kullanmıyorsa** bu korpusa girer. Kapı mekanik olabilir:
*soru metni ∩ (measure_synonyms_display ∪ dimension_labels) = ∅.*

**Kural 2 — altı persona, altı ayrı dil.** Aynı iş sorusu, altı ağızdan farklı sorulur:

| Persona | Nasıl konuşur | Örnek zorluk |
|---|---|---|
| **CEO / patron** | kısa, sonuç odaklı, ölçü adı **kullanmaz** | *"işler nasıl gidiyor"* · *"geçen aya göre iyi miyiz"* |
| **CFO / mali işler** | dönem + mutabakat dili, **mali takvim** | *"kapanışta bakiye tutuyor mu"* · *"3. çeyrek gerçekleşme"* |
| **Üretim müdürü** | vardiya/makine/parti, **kısaltma ve argo** | *"gece vardiyası niye düştü"* · *"2 nolu makine yine mi"* |
| **Kalite müdürü** | oran + neden zinciri | *"fire nerede artıyor, kimin yüzünden"* |
| **Satış müdürü** | müşteri/segment, kıyas | *"hangi müşteri bizi taşıyor"* |
| **Saha kullanıcısı** | 🔴 **yazım hatası · eksik cümle · konuşma dili** | *"bu ayki fire ne kdr"* · *"peki ya geçen sene"* |

**Kural 3 — beş zorluk kademesi, her personada.** Kademe atlanamaz; **payda kademeli
raporlanır** ki bir kademedeki kayıp ötekinde saklanmasın:

| Kademe | Ne | Örnek |
|---|---|---|
| **K1 · düz** | tek ölçü, tek dönem | *"bu ay ciro"* |
| **K2 · kırılımlı** | + boyut / sıralama | *"müşteri bazında, en yüksekten"* |
| **K3 · kıyaslı** | dönem/segment kıyası, **değişim** | *"ocakla haziranı karşılaştır"* |
| **K4 · nedensel** | *"neden"* · katkı ayrıştırması · aykırı değer | *"düşüşün sebebi ne"* |
| **K5 · kararsal** | *"ne yapmalıyım"* · hedef · senaryo | *"bu gidişle yılı nerede kapatırız"* |

**Kural 4 — her vaka üç şeyi birden beyan eder** *(yoksa vaka değildir)*:
`SORU` · `KABUL EDİLEBİLİR CEVAP SINIFI` *(doğru cevap ∨ **dürüst netleştirme** ∨
**dürüst ret**)* · `YASAK CEVAP` *(sessiz-yanlış: yanlış soruya kendinden emin cevap)*.

> 🔴 **En kritik nokta: «netleştirme» bir BAŞARIDIR, kayıp değil.** Bugünkü korpus
> `CLARIFY`'ı OK saymıyor; oysa *"bakiye: cari mi mizan mı?"* diye **sormak**, ₺11,86
> milyonluk sessiz seçimden **iyidir**. Yeni korpus bunu **ayrı bir kazanç sütunu**
> olarak saymalı.

**Kural 5 — vakalar gerçekten toplanır, uydurulmaz.** Üç kaynak, sırayla:
1. **FAZ 8.1 kullanım penceresi** — asıl kaynak; gerçek kullanıcı ifadeleri.
2. **`lab/deneyim.py`'nin 15 senaryosu** — persona iskeleti zaten burada, genişletilir.
3. **Borç defterinin canlı bulguları** — #16…#23 zaten **gerçek turlardan** geldi ve
   her biri bir vakadır *(çıkışsız yazım düzeltmesi · «değişim» istenip toplam verilmesi ·
   üstünlük ifadesinin cevaplanmaması · ham kolon adı · sözle «evet»)*.

**Kural 6 — kapı, bugünkü kapının yanına kurulur.** Hedef **yüzde değil ilerlemedir**:
ilk koşum **taban**dır; sonraki her tur o tabana göre ölçülür. *Bir kapının kapsamı,
ölçtüğü şey kadardır.*

---

## §10 · v1 İTİBARİYLE SİSTEM NE YAPIYOR — **tek tek test edilebilir liste**

**Yöntem/ölçüm:**
```bash
grep -rhoE '@router\.(get|post|put|patch|delete)\("[^"]*"' backend/app/routers/*.py | wc -l   # 69 uç
grep -nE "^TUR_[A-Z_]+ = " backend/app/followup.py                                            # 7 konuşma türü
python3 -c "import ast,pathlib; t=ast.parse(pathlib.Path('backend/app/tools.py').read_text());
print(sum(1 for n in ast.walk(t) if isinstance(n,ast.Call) and getattr(n.func,'id','')=='Arac'))"  # 23 araç
grep -rE "export (default )?function [A-Za-z]+Panel" dima-frontend-demo-master/src | wc -l    # 13 panel
find dima-frontend-demo-master/src/app -name page.tsx | wc -l                                 # 5 rota
```

**Yüzey:** **69 HTTP ucu** · **23 ajan aracı** *(5 ayrı izin)* · **7 konuşma türü** ·
**13 panel** · **5 rota** · **42 bayrak**.

### 10.1 · Çekirdek: soru → cevap

| # | Yetenek | Nasıl test edilir *(kullanıcı ağzından)* | Durum |
|---|---|---|---|
| **U1** | **Doğal dilde soru → tablo/sayı** *(LLM'siz deterministik merdiven: `route → refine → chip → dönem → LLM`)* | *"bu ay toplam üretim"* | ✅ |
| **U2** | **Kırılımlı sorgu** | *"makine bazında ortalama oee"* | ✅ |
| **U3** | **Üstünlük / Top-N** | *"en çok fire veren 5 makine"* | ✅ ⚠ borç #20: *"hangi makine en yüksek"* biçimi kataloğa düşebiliyor |
| **U4** | **Dönem netleştirme** — dönem yoksa **sorar** | *"ciro"* → *"hangi dönem?"* | ✅ |
| **U5** | **Belirsizlikte netleştirme** *(aynı ölçü iki cube'ta)* | *"bakiye"* | ⚠ `netlestirme_onceligi` **`off`** — borç #19 |
| **U6** | **Takip sorusu / yenileme** *(`deterministic_refine`)* | *"aylık"* → *"en yüksekten sırala"* → *"grafik ver"* | ✅ |
| **U7** | **Çıplak ikinci ölçü ekleme** | *"bir de fire oranı"* / *"fire orani yuzde"* | ✅ `olcu_ekleme_takibi` **beta** |
| **U8** | **Çapraz-cube ekleme + grain uyarısı** | *"buna bir de enerji tüketimini ekle"* | ✅ |
| **U9** | **Gürültü/kapsam dışı → dürüst duvar** | *"bana fıkra anlat"* · *"drop table"* | ✅ |
| **U10** | **Yetenek sorusu** | *"neler yapabilirsin"* · *"hangi kırılımlar var"* | ✅ |
| **U11** | **Excel/dosya yükleme** *(`POST /ask/upload`)* | dosya at, üzerine soru sor | ✅ |
| **U12** | **Ad-hoc cube** *(Discovery cevabına yapı)* | katalogda olmayan bir kesit | ✅ `adhoc_cube` **beta** |
| **U13** | **Arka plan Discovery işi** *(`/ask/jobs` · SSE stream)* | uzun soru → iş kuyruğu | ⚠ `ask_async_discovery` **`off`** |

### 10.2 · Konuşma türleri *(7/7 — v1 hedefi tam)*

| # | Tür | Test cümlesi | Durum |
|---|---|---|---|
| **K1** | `neden` — katkı ayrıştırması | *"bu neden böyle?"* | ✅ |
| **K2** | `normal_mi` — dönemsel kıyas + sinyal | *"normal mi?"* | ✅ |
| **K3** | `ne_yapmali` — reçete | *"ne yapmalıyız?"* | ⚠ borç #16b: `prescription` **hiç dolmuyor** |
| **K4** | `isaret` — grafiğe çapa | *"şu düşüş ne?"* | ✅ |
| **K5** | `anlat` — eldeki cevabı aç | *"bunu analiz et"* | ✅ |
| **K6** | `takip` — zamanlama önerisi | *"bunu takip et"* | ⚠ `tur_takip` **`off`** |
| **K7** | `paylas` — paylaşılabilir link | *"müdüre üç cümle yaz"* | ⚠ `tur_paylas` **`off`** |

> 🔴 **Kritik:** 7 tür **yazıldı** ama ikisi (`K6` · `K7`) **kapalı** → kullanıcının
> bugün erişebildiği tür sayısı **5**. Ölçüt 9'un yeşili *"yazıldı"* der, *"açık"* demez.

### 10.3 · Analiz derinliği

| # | Yetenek | Test | Durum |
|---|---|---|---|
| **A1** | **Drill-down** *(`drill.expand` · `drill.select`)* | grafikte bir çubuğa tıkla | ✅ *(reddi artık **sebep söylüyor** — 7.3/e)* |
| **A2** | **Katkı ayrıştırma** *(`contribution.decompose` · `.report` · `.pvm`)* | *"bu artışa en çok ne katkı yaptı"* | ✅ |
| **A3** | **YoY / dönem kıyası** *(`yoy.compute`)* | *"geçen yılın aynı ayına göre"* | ✅ |
| **A4** | **Değişim ekseni** | *"ocak ile haziran arasında fire değişimi"* | 🔴 **borç #17 — sessiz-yanlış**: değişim istendi, **toplam** verildi |
| **A5** | **Trend / özet** *(`stats.trend` · `stats.ozet`)* | *"aylık üretim trendi"* | ✅ |
| **A6** | **Δ kartı + streak** *(5.5)* | ardışık artış/azalış | ✅ |
| **A7** | **Segment A↔B farkı** *(5.7)* | iki segmenti kıyasla | ✅ |
| **A8** | **Hedef kıyası** *(`target:` beyanı)* | *"hedefin neresindeyiz"* | ⚠ `hedef_kiyasi` **`off`** |
| **A9** | **Peer / benzer kıyası** | *"benzer tesislere göre"* | ⊘ **5.6 BLOKE** (AJ2) |
| **A10** | **Kök neden ön-skorlama** | z-skorlu aykırı değer işareti | ⊘ **7.3/d yapılmadı** |

### 10.4 · Güven, kanıt, uyum

| # | Yetenek | Test | Durum |
|---|---|---|---|
| **G1** | **Kaynak rozeti** *(`source=cube/vqr/catalog/…` — **17** ayrı değer)* | cevabın nereden geldiği | ✅ |
| **G2** | **Katmanlı makbuz** *(7.8)* | *"bu sayı nasıl çıktı"* | ✅ `ui_kanit_gorunurlugu` **beta** |
| **G3** | **SQL'i göster** | *"+ sql göster"* | ✅ `sql_display` **beta** |
| **G4** | **Sözleşme + replay** *(`/contracts/{id}/replay`)* | aynı soruyu **yeniden koş** | ✅ |
| **G5** | **Audit zinciri + dışa aktarım** *(`/audit/export`)* | denetim kaydı indir | ✅ |
| **G6** | **Kolon kökeni (lineage)** | *"bu sayı hangi kolonlardan"* | ⚠ **`off`** *(ama **kapılı** — açılabilir)* |
| **G7** | **Tazelik** *("veri ne kadar eski")* | *"veri hangi tarihe kadar"* | 🔴 **`off` VE KAPISIZ** — §8.2 |
| **G8** | **Metrik sertifikası** *("tanımı kim onayladı")* | metrik kartı | 🔴 **`off` VE KAPISIZ** — §8 |
| **G9** | **DCM — Deterministik Cevap Modu** *(banka/kamu)* | LLM'siz kilit mod | ⚠ `ui_dcm_modu` **`off`** |
| **G10** | **Numeric fidelity + kademeli düşüş + eskalasyon** | LLM sayıyı bozarsa | ✅ |
| **G11** | **PII maskeleme + kolon düzeyi erişim** | kısıtlı rolle sor | ✅ *(motor-CLS ayrı: **açık borç**)* |

### 10.5 · Görselleştirme ve rapor

| # | Yetenek | Test | Durum |
|---|---|---|---|
| **V1** | **Grafik önerisi** *(`viz.recommend`)* | *"grafik ver"* · *"pasta"* | ✅ |
| **V2** | **«Ne zaman grafik ÇİZİLMEZ»** *(5.11)* | tek satırlık sonuç | ✅ |
| **V3** | **Pivot / çapraz tablo** | *"vardiya × haftanın günü"* | ✅ |
| **V4** | **Rapor derleme + sabit yapı** *(`report.compose`, 5.13b)* | *"rapor yap"* | ✅ |
| **V5** | **İçgörü paketi** *(aynı sonucun birden çok ekseni)* | — | ⚠ `ui_icgoru_paketi` **`off`** |
| **V6** | **Hayalet seri + kural motoru** | iş kuralı anlatıya girer | ⚠ `ui_knowledge_center` **`off`** *(motoru `rules.py` — **yetim modül**)* |
| **V7** | **5 yeni grafik tipi** *(Sankey·Pareto·Bubble·Gauge·Harita)* | — | ⊘ **7.3/l yapılmadı** |

### 10.6 · Otomasyon ve paylaşım

| # | Yetenek | Test | Durum |
|---|---|---|---|
| **O1** | **Pano / dashboard** *(9 uç)* | widget ekle, veri çek | ✅ `dashboards` **beta** |
| **O2** | **Zamanlanmış rapor + bildirim** *(5 uç)* | *"her pazartesi gönder"* | ✅ `scheduled_reports` **beta** |
| **O3** | **Bildirim tercihleri** *(3 uç)* | kanal/kategori kapat | ✅ *(kapı modülü `bildirim_kapisi.py` — **yetim**)* |
| **O4** | **Paylaşılabilir link** *(`/share` · `/share/{token}`)* | linki başkasına aç | ⚠ `tur_paylas` **`off`** |
| **O5** | **KPI pin** | KPI'ı panoya sabitle | 🔴 **`off` VE KAPISIZ** |
| **O6** | **Karar kaydı** *(`/decisions` — 3 uç)* | kararı kaydet/koştur | ✅ ⚠ **liste ucu yok**, `/decisions` rotası ⊘ |
| **O7** | **Doğrula (✓/✗) → VQR öğrenme** | cevabı onayla | ✅ `verify_button` **beta** |
| **O8** | **Onay akışı** *(D9: kapsam içi iş istemsiz koşar)* | *"panoma ekle"* | ◐ **yarısı bağlı** — §8.2 · ⚠ borç #21: **sözle «evet» işlemiyor** |

### 10.7 · Kurulum, semantik yönetim, yönetici

| # | Yetenek | Test | Durum |
|---|---|---|---|
| **S1** | **Bağlantı ekle + şema keşfi + onay** *(8 uç)* | yeni DB bağla | ✅ *(ekranı `ConnectionReviewPanel`)* |
| **S2** | **Ossie semantik model ithal/ihraç** | mevcut modeli getir | ⚠ ikisi de **`off`** *(kapılı, açılabilir)* |
| **S3** | **Cold-start metrik önerisi** | boş modelden başla | 🔴 **kapısız canlı** — §7.2 |
| **S4** | **Metrik kaydı = hakem** *(çakışmayı görünür kılar)* | aynı ad iki cube'ta | ✅ `metrik_kaydi` **beta** |
| **S5** | **Ölçü adayı kuyruğu** *(8 uç: preview·blast-radius·approve·deprecate)* | terfi kuyruğu | ✅ |
| **S6** | **Sinonim önerici** *(offline, insan onaylı)* | öneri listesi | 🔴 **yetim modül** |
| **S7** | **Kapsam merceği** *(departman görünürlüğü)* | dar rolle bak | ⚠ `kapsam_mercegi` **`off`** |
| **S8** | **Çekirdek katman + grain sözleşmesi** | çapraz-cube tutarlılık | 🔴 **`off`; bayrak İKİ SAHİPLİ** — §8.3 |
| **S9** | **MCP yüzeyi** *(`/mcp/tools` · `/mcp/call`)* | dış ajan bağla | ⚠ `mcp_yuzeyi` **`off`** *(kapılı)* |
| **S10** | **Public API + embed** | dış geliştirici | 🔴 `public_api` **kapısız** · `embed` **P0 bloke** |
| **S11** | **`/settings` — 8 sekmeli yönetim** | admin ekranı | ⊘ **7.7 yapılmadı** *(13 router tüketicisiz)* |

### 10.8 · Kullanıcının **bugün göremediği** ödenmiş yetenekler — özet

Test ederken *"neden yok"* diye şaşırma ihtimali en yüksek olanlar:
**tazelik** · **metrik sertifikası** · **KPI pin** · **«bunu takip et»** · **«paylaş»** ·
**hedef kıyası** · **içgörü paketi** · **bilgi merkezi** · **DCM modu** · **kapsam
merceği** · **hızlı↔derin anahtarı** · **onay talebi/süre aşımı**.

---

## §11 · A/B ADAYI KAPALI BAYRAKLAR — *hangisi açılmalı, hangisi açılamaz*

Kullanıcının 4. sorusu: *"bayrağı `off` olan ama belki de açmak gereken şeyler."*
Aşağıdaki üç grup **kapı durumuyla** ayrıldı; `V1-SON-KONTROL.md`'nin sayısı tekrar
edilmiyor, **adları ve açılabilirlikleri** veriliyor.

> 🔴 **Açış disiplini (raporun kendi §5/5'i):** bayraklar **teker teker** açılır,
> **geliştirmeyle aynı commit'te değil**, ve her açış **kendi ölçümünü** ister.

### 🟢 GRUP 1 — **A/B'ye hazır**: kapısı var, açış tek satır, ölçümü belli

| Bayrak | Ne açar | Neden aday | Ölçümü ne olmalı |
|---|---|---|---|
| 🔴 **`lineage`** | kolon kökeni | FAZ 1'in üç ana teslimatından **tek KAPILI olanı** — bugün açılabilir | `/ask` gecikmesi + kanıt panelinin dolması |
| **`netlestirme_onceligi`** | netleştirme LLM tahminini önceler | **borç #19'un** (₺11,86 M sessiz seçim) doğrudan panzehiri | `CLARIFY` oranı **artmalı** — bu bir kazanç, kayıp değil |
| **`tur_takip`** *(K6)* | *"bunu takip et"* | konuşma türü **yazılı ve testli**, kullanıcıya kapalı | tür tanıma oranı + zamanlama dönüşümü |
| **`tur_paylas`** *(K7)* | *"müdüre 3 cümle"* | aynı; **motoru zaten çalışıyor** *(§3B'nin kendi tespiti)* | paylaşım linki üretim sayısı |
| **`hedef_kiyasi`** | `target:` beyanıyla hedef kıyası | `off`'ken alan **hiç üretilmiyor** → geri alma bayt düzeyinde temiz | hedefi olan metriklerde kart |
| **`ui_icgoru_paketi`** | aynı sonucun birden çok ekseni | tek kart dönüşü **kırılmadan** ölçüldü | kart başına eksen sayısı |
| **`ui_knowledge_center`** | hayalet seri + kural motoru | ⚠ **motoru `rules.py` yetim** — açmadan önce **bağlanmalı** | anlatıda kural atfı |
| **`hizli_derin`** | Hızlı ↔ Derin anahtarı | *"LLM'siz cevap"* tezinin **kullanıcı kontrolü** | mod başına gecikme + memnuniyet |
| **`kapsam_mercegi`** | departman merceği | ⚠ **görünürlük** aracı, güvenlik sınırı **değil** | katalog boyutu ↔ doğru-cube |
| **`ossie_ithal` · `ossie_ihrac`** | semantik model taşıma | **`3.0`'ın ticari kilidi** — `3.0` koşulmadan değeri ölçülemez | ithal→ilk doğru cevap süresi |
| **`ui_dcm_modu`** | deterministik cevap modu | banka/kamu satışının **ön şartı** | LLM çağrısı **0** olmalı |
| **`ask_async_discovery`** | Discovery arka plana | uzun sorularda **kilitlenmeyi** çözer | p95 gecikme |
| **`agent_plan_secimi`** | planlayıcı plan **önerir** | ⚠ **sıcak yola LLM çağrısı ekler** — gecikme bütçesiyle birlikte ölçülmeli | gecikme + plan kabul oranı |
| **`prompt_enhancer`** | `route()` boşsa soruyu katalog terimleriyle yeniden yaz | 🔴 **§9'un doğrudan panzehiri**: kullanıcının kelimesini kataloğun kelimesine çevirir | **yalnız gerçek-dünya korpusunda** ölçülebilir |
| **`t2_anlatici`** | guarded LLM anlatıcı | §F.2'de **bilerek ertelendi** — kararı yazılı | anlatı sadakati (numeric fidelity) |
| **`mcp_yuzeyi`** | dış ajan yüzeyi | uç `off`'ken **404** — davranış birebir | — |

### 🔴 GRUP 2 — **AÇILAMAZ / açmadan önce iş var** *(bayrağı çevirmek yetmez)*

| Bayrak | Neden | Önce ne gerekir |
|---|---|---|
| **`tazelik`** | **KAPISIZ** — `resolve_for`'da adı geçmiyor, `freshness`'ı **kimse doldurmuyor** | `tazelik.kademe()`'yi cevap yoluna bağla *(ve `ters_yetim` kapısını **üreticiye** çevir)* |
| **`metrik_sertifikasi`** | **KAPISIZ** — `certification.py`'nin **sıfır** çağıranı | modülü metrik yoluna bağla |
| **`kpi_pin`** | **KAPISIZ** — `kpi_pin.py` yetim | panoya bağla |
| **`kanal_kimlik`** | **KAPISIZ** — `kanal_kimlik.py` yetim | bildirim yoluna bağla |
| **`threaded_chat`** | **KAPISIZ** — `app/` içinde adı yok | — |
| **`public_api`** | **KAPISIZ** — `app/` içinde adı **hiç geçmiyor** | uçları bayrağa bağla |
| **`cekirdek_katman`** | **İKİ SAHİPLİ** — açış `features.yml`'den **değil** `DIMA_CEKIRDEK_KATMAN` env'inden yapılır | tek sahibe indir *(ya da kaydı **beyanlı istisna** yap)* |
| **`embed`** | **P0 ölçülü**: `motor_cls=off` | motor-CLS açılmadan **asla** |
| **`onay_akisi`** | ◐ **yarısı bağlı** — açmak D9 yarısını açar, onay talebi/süre aşımını **açmaz** | `onay_akisi.py`'yi bağla |

> 🔴 **Test ederken kritik uyarı:** Grup 2'deki bir bayrağı `features.yml`'den açıp
> *"bir şey değişmedi"* görmek **bayrağın işe yaramadığı** anlamına gelmez — **hiç
> bağlanmadığı** anlamına gelir. İkisini karıştırmak, yanlış bir *"özellik işe yaramıyor"*
> yargısı doğurur.

### ⚖ GRUP 3 — **`beta` ama hakemi ölçüm değil, SEN'sin**

`cekirdek_katman` dışında, **korpusun yapısal olarak ölçemediği** yetenekler:
`cikti_yorumlama` · `next_steps` · `capa_zinciri` · `metrik_kaydi` · `liste_niyeti` ·
`ui_kanit_gorunurlugu` · `sql_display` · `verify_button` · `dashboards` ·
`scheduled_reports`. Bunlar **cevabın kendisini değil, cevabın çevresini** değiştirir;
korpus `execute=False` koştuğu için (§9.3) **ölçemez**. Değerlendirmesi **canlı turdur**.

---

## §12 · BU TURUN KAPANIŞI — ne bulundu, ne bulunmadı

**Bulundu** *(hepsi yeni; birinci turda ve `V1-SON-KONTROL.md`'de yok)*:

1. 🔴 **12 yetim modül** (~1.470 satır) — *"birim yeşili, sistem kırmızısı"* sınıfı.
2. 🔴 **9 kapısız bayrak** — üçü FAZ 1/5/6'nın ana teslimatı; açmak **hiçbir şey yapmaz**.
3. 🔴 **`cekirdek_katman` iki sahipli** — `FLAG_REGISTRY` girdisi **dekoratif**.
4. 🔴 **`3.0` (tenant açılışı) hiç açılmadı ve atlandığı hiçbir yere yazılmadı** —
   üstelik `8.2`'nin taşındığı hedef.
5. 🔴 **`coldstart_metrik` kapısız canlı** · **`netlestirme_kapanisi` (0.5b) hiç yok** ·
   **5.9'un üç kanal bayrağı yok**.
6. 🔴 **Korpusun ≥%97'si sistemin kendi sözlüğünden üretiliyor** — *"testler koda göre
   yazıldı"* şüphesi **mekanizmasıyla doğrulandı**; §9.6'da şartnamesi yazıldı.
7. ⚠ **`ters_yetim` kapısının kör noktası adlandırıldı**: *bir şema alanı üretici değildir.*

**Bulunmadı / bakılmadı** *(dürüstlük gereği yazılıyor)*:

- **Mimari harita uyumu** — kullanıcı talimatıyla **kapsam dışı** bırakıldı.
- **Test koşulmadı.** `OPERASYON-DENETIM.md`'nin ortak kuralı: denetim ajanları test
  koşmaz. Buradaki hiçbir satır *"şu test kırmızı"* demiyor; *"şu kod yolu yok"* diyor.
- **12 yetim modülün her biri için ayrı ayrı** *"acaba dolaylı bir yoldan çağrılıyor mu"*
  sorusu soruldu. AST + `grep`'e ek olarak deponun **tek dinamik import mekanizması** da
  tarandı — `app/tools.py:106`'nın `importlib.import_module(self.modul)`'ü:

  ```bash
  cd backend && python3 -c "import ast,pathlib;t=ast.parse(pathlib.Path('app/tools.py').read_text());
  print(sorted({k.value.value for n in ast.walk(t) if isinstance(n,ast.Call) and getattr(n.func,'id','')=='Arac'
  for k in n.keywords if k.arg=='modul'}))"
  ```
  **23 aracın işaret ettiği 15 modülün hiçbiri yetim listesinde değil** → dinamik yol
  onları kurtarmıyor. **Runtime izleme yine de yapılmadı**; bir modül `getattr`/`eval`
  ile çağrılıyorsa bu tarama onu kaçırır → itiraz gelirse **çağrı yolu gösterilerek**
  düşer. `[DOĞRULANMADI]` payı yalnız buradadır.

> *Birinci tur şunu bulmuştu: "yazıldı, ölçüldü, ölçüm hoşa gitmedi diye kapalı bırakıldı."*
> **İkinci tur bir kat daha aşağısını buluyor: bir kısmı kapalı bile değil — hiç bağlanmadı.
> Ve bunu hiçbir kapı görmedi, çünkü kapılar beyanları birbiriyle kıyaslıyor, kodu istek
> yoluyla değil.**
