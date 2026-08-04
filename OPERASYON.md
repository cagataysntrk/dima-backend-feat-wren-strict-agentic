# OPERASYON — DİMA v1 · kural seti ve yürütme sözleşmesi

> 🔴 **BU DOSYA HER OTURUMDA OKUNUR.** Bağlam sıfırlanırsa (compact / yeni oturum) buradan
> devam edilir. Yanında **`OPERASYON-DURUM.md`** vardır: *nerede kaldık*. İkisi birlikte
> operasyonun **tam durumunu** taşır — sohbet geçmişine bağımlılık YOKTUR.

---

## 0 · OPERASYONUN TANIMI

**Hedef:** `DIMA-V1-YOL-HARITASI.md`'nin **v1 kısmını** (FAZ −1 → FAZ 8) uçtan uca teslim
etmek. **v2/v3 bu döngünün kapsamı DIŞINDA** — ayrı döngülerde yapılacak.

**Nihai vaat (kullanıcının kendi cümlesi):** *"verinizi bilen, ayrıştırabilen,
konuşabilen, onayla iş yapabilen ve her sayısını kanıtlayabilen bir meslektaş."*
Ve teknik hedefi: ***"Mükemmel motor + insani yüz tek sistemde."***

**Bitiş ölçütü:** §C'nin **16 ölçütü** yeşil. *"Bitti" bir kanaat değil, bir sayıdır.*

---

## 1 · OTORİTE SIRASI *(çelişkide yukarıdaki kazanır)*

| # | Belge | Yol |
|---|---|---|
| 1 | **MIMARI değişmezleri (§4) ve yasakları (§5)** | `backend/MIMARI.md` |
| 2 | **YOL HARİTASI** — ne, hangi sırayla, hangi kapıyla | `~/.claude/plans/DIMA-V1-YOL-HARITASI.md` |
| 3 | **BU DOSYA** — nasıl çalışılır | `OPERASYON.md` |
| 4 | **DURUM** — nerede kaldık | `OPERASYON-DURUM.md` |
| 5 | Kanıt / ölçümler | `~/.claude/plans/polymorphic-tumbling-riddle.md` |
| 6 | Ürün şartnamesi *(mimari otorite DEĞİL)* | `Dima-0-100-Gorev-Takip-Dosyasi (2).md` |

> ⚠ **İSTİSNA:** Yol haritası FAZ −1'in `⟳ YÜRÜRLÜKTE` bloğunda listelenen `MIMARI.md`
> başlıklarında **yol haritası kazanır** — ve o işaret, ilgili madde indiğinde **silinip
> ölçümlü bir `✅` kaydına dönüşür**.

**Yol haritasının yedeği:** `~/.claude/plans/.yedek/` — belge **git altında değildir**,
her düzenlemeden **önce** zaman damgalı yedek alınır ve `md5sum` ile doğrulanır.

---

## 2 · 🔴 DÖNGÜNÜN ADIMLARI — her madde için, istisnasız

```
1. OKU      → yol haritasının İLGİLİ maddesini (ve atıf verdiği yerleri) yeniden oku
2. PLANLA   → terminale kapsamlı TO-DO bas: backend · sözleşme · frontend · kapı
3. ÖLÇ      → kusuru ÖNCE ölç (sayıyla, HEAD damgasıyla). Ölçülmemiş kusur düzeltilmez
4. GELİŞTİR → backend + sözleşme + frontend BİRLİKTE (yetim bırakma yasağı)
5. KAPI     → düzeltmeyi TESTE çevir; kapısız inen madde "bitti" DEĞİLDİR
6. DOĞRULA  → seviye 0 + `--hizli` YALNIZCA. 🔴 UZUN TEST BU ADIMDA KOŞMAZ
7. BELGELE  → MIMARI.md'yi AYNI commit'te güncelle (⟳ → ✅, ölçümle)
8. COMMIT   → açıklayıcı mesaj: kusur · kök neden · düzeltme · ölçüm
9. DURUM    → OPERASYON-DURUM.md'ye TEK SATIR ekle (tam tur demet sonunda)
10. → bir sonraki maddeye geç. DEMET KAPANDIYSA §3'ün demet kapanış listesini koş
```

🔴 **HER COMMIT'TE UZUN TEST KOŞMAZ.** `--tam` · `eval` · korpus · senaryo · Ajan C
bu döngünün **hiçbir adımında** yer almaz — hepsi **demet kapanışına** aittir (§3).
Madde başına doğrulama tavanı **~1 dakikadır**; aşıyorsa kural çiğneniyordur.

**Bir sonraki maddeye geçmek için izin İSTENMEZ.** Döngü v1 bitene kadar sürer.

---

## 3 · 🔴 TEST KAPISI — **YENİ POLİTİKA (kullanıcı kararı, 2026-08-04)**

> *"Kapı testlerini iptal edelim, sadece korpus koşsun — o da sadece en gerekli
> zamanlarda, sıklığı düşük, demet sonu gibi. Çok daha hızlı geliştirmeliyiz;
> fazları hızlıca ama mükemmelce tamamlamalıyız."*

**Yerel kapı dört adımdan tek adıma indi** (~15 dk → **1 dk 57 sn**, ölçüldü — aşağıdaki
düzeltmeye bak). Kaybedilen ağ **gecelik CI'ya** taşındı, **silinmedi**.

| Seviye | Komut | Ne zaman | Süre |
|---|---|---|---|
| **0 · anlık** | `pytest tests/test_<dokunulan>.py` | her düzenlemeden sonra | 5–15 sn |
| **1 · hızlı sinyal** | `python lab/kapi.py --hizli --degisen <dosyalar>` | geliştirme sırasında | ~15–60 sn |
| **2 · DEMET kapısı** | `python lab/kapi.py --tam` → 🔴 **YALNIZ KORPUS** | **demet sonu**, commit'lerden sonra, **TEK sefer** | **1 dk 57 sn** |
| **3 · gecelik CI** | `python lab/kapi.py --hepsi` *(korpus + süit + eval + senaryo)* | 🔴 **YEREL KOŞULMAZ** — `nightly.yml` koşar | ~15 dk |

### 🔴 NEDEN korpus KALDI, öteki üçü ÇIKTI — ölçüm

| Adım | Bu operasyonda kaç kez **kırmızı** verdi | Maliyeti |
|---|---|---|
| `eval.run` | **0** *(her koşum `+0,0 / +0,0 / +0,0`)* | ~1,5 dk |
| konuşma senaryoları | **0** *(dokuz sınıf tabanda sabit)* | ~1,5 dk |
| tam süit | birkaç kez — **aynı kusurları seviye 1 de yakaladı** | ~8,5 dk |
| **korpus** | 🔴 **1 kez — ve başka hiçbir şeyin göremeyeceği bir kusuru** | **1 dk 57 sn** |
> ⚠ **ÖLÇÜLDÜ — ve ilan edilen sayı yanlıştı (düzeltildi, 2026-08-04).** `--tam` **13 dk
> 18 sn** sürüyor, *"~3,5 dk"* değil (`docker inspect dima-k1`: `15:51:07 → 16:04:25`).
> O rakam, dört adımlı koşumun **içindeki** korpus dilimiydi — ve o dilim, süit çoktan
> compose ettiği için **ısınmış** bir sistemde ölçülmüştü. Tek başına koşan korpus
> compose + MDL derlemesini **kendisi** yapıyor.
>
> Duvar saatinin **%71'i tek şirkette**: `boyahane` **5306 soru / 8 dk 49 sn** (10 soru/sn);
> öteki üçünün **toplamı** ~3,5 dk (atiksan 1462/1'05" · gulteks 1618/1'16" · gitas 2479).
> Yani ilan edilen sayı, farkında olmadan *"boyahane hariç"* ölçümüydü.
>
> ⟳ **VE SONRA PARALELLEŞTİRİLDİ (ölçüldü, aynı gün):** `13 dk 18 sn → **1 dk 57 sn**`
> (`docker inspect dima-k3`: `17:05:04 → 17:07:01`). **Kapsamdan tek soru gitmedi** —
> doğrulandı: payda **445**, doğruluk **%93,1**, dört şirket de tabanda ya da üstünde,
> yani seri koşumun sayılarıyla **birebir aynı**. Hız, boşta duran çekirdeklerden alındı:
> kapı 20 çekirdekli makinede tek çekirdeği %91'de tutuyordu.
>
> 🔴 **Seyreltme YAPILMADI ve bu bilinçli:** korpusun bu operasyondaki **tek** yakalaması
> (`gitas` compose yarışı) payda **445 → 342'ye düşerken** doğruluğun **%93,2 → %94,3'e
> ÇIKMASIYDI**. Soru matrisini seyreltmek tam da paydayı değiştirmektir — *"sistem
> bozulurken sayı iyileşir"* kusurunu gören mekanizmayı, o kusura benzeyen bir işlemle
> ucuzlatmak olurdu. Seyreltme bir **kullanıcı kararıdır**; sayı burada dürüstçe duruyor.


O tek yakalama, kararın **tamamıdır**: `gitas` bir compose yarışıyla korpustan
**tamamen düştü**, payda **445 → 342** indi, doğruluk **%93,2 → %94,3'e ÇIKTI**.
Sistem bozulurken **sayı iyileşti**; süit · `eval` · senaryolar üçü de **yeşildi**,
çünkü hiçbiri *"kaç soru cevaplanabiliyor"* sorusunu sormuyor.
*Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla da olur.*

⚠ **Korpusun bilinen körlüğü yazılıdır:** soruları **katalogdan üretiliyor**, hepsi
**doğru yazılmış** — typo yolu korpusta **hiç sorulmuyor**. Yeşil bir korpus, kırık bir
kullanıcı deneyimini **DIŞLAMAZ**. O kusurlar canlı turlardan çıkar (aşağıda, Ajan C).

⚠ **Silinen bir şey YOK** (MIMARI §10: *"kapananlar işaretlenir, silinmez"*). Geri alma
tek bayrak: `--hepsi`.

### 🔴 COMMIT ≠ KAPI — demet disiplini *(ölçülerek benimsendi)*

**Ölçüldü:** bir turda FAZ 0'ın ~4 maddesi indi ve tam kapı **6 kez** koştu (~90 dk).
Ama sürenin **%75'i kapıda değildi**; madde başına koşan 10 adımlık döngüdeydi
(ölç → düzelt → kapı → MIMARI → commit → DURUM → denetim). Ve `--tam`'ın **dört
bileşeninin üçü** (`eval` · korpus · senaryo) o turda **hiç kıpırdamadı**, çünkü
onları besleyen dosyalara dokunulmamıştı.

**Karar:** *commit ucuzdur, kapı pahalıdır.* Geri alınabilirlik **commit'ten** gelir,
kapıdan değil — ikisini ayırmak **hiçbir güvenlik kaybettirmez**.
Her madde kendi commit'ini alır (seviye 0+1 ile); **tam kapı demet sonunda bir kez** koşar.

🔴 **RİSK SINIRI — demete GİRMEYEN maddeler.** Aşağıdakilere dokunan bir madde
**kendi tam kapısını hemen koşar** (demet beklemez), çünkü kapının üç sessiz bileşenini
besleyen yollar bunlardır:

```
app/cube_router.py · app/interpret.py · app/answer.py · app/followup.py
app/routers/ask.py · app/contribution.py · demo/packs/**   (katalog/metadata)
```

Belge · frontend · test-aracı · `lab/` maddeleri **serbestçe demetlenir**.

### 🔴 DEMET NE ZAMAN KAPANIR — üç sınırdan hangisi ÖNCE gelirse

| # | Sınır | Neden bu sınır |
|---|---|---|
| **D-a** | **6 madde** doldu | Kırmızı çıkarsa şüpheli küme 6 commit'le sınırlı — `git bisect` ucuz kalır |
| **D-b** | **Risk dosyasına** dokunuldu *(yukarıdaki liste)* | O madde demeti **hemen kapatır**; kapı onunla birlikte koşar |
| **D-c** | **~2 saat** geliştirme geçti | Kırmızıyı 6 saat sonra öğrenmek, 6 madde geri sarmak demektir |

**Demet kapanış listesi** *(sırayla, TEK sefer)*:
```
1. python lab/kapi.py --tam        → ~2 dk    KORPUS (yeşil değilse buradan çıkılmaz)
   ⤷ KIRMIZI ÇIKARSA: düzelt ve YALNIZ onu tekrar koş (zaten tek adım).
   ⤷ 🔴 "Bir de süiti koşayım" YASAK — o gecelik CI'nın işi (`--hepsi`).
      Yerel bir `--hepsi` koşumu, bu kararın TAM OLARAK iptal ettiği şeydir.
2. MIMARI.md + OPERASYON-DURUM.md  → demetin TAMAMI için tek pas, tek commit
3. git push                        → 🔴 ARTIK BİRİNCİ AĞ: süit·eval·senaryo YALNIZ
                                      orada koşuyor. Push ERTELENMEZ.
4. Ajan C canlı turu               → AŞAĞIDAKİ SIKLIKLA (her demette DEĞİL)
```

🔴 **`git push` artık isteğe bağlı değil.** Süit · `eval` · senaryo yerel kapıdan
çıktığı için tek koşum yerleri gecelik CI'dır; push edilmemiş bir demet, o üç adım
tarafından **hiç ölçülmemiş** demektir. *Ağı CI'ya taşımak, ancak kod CI'ya ulaşırsa
bir ağdır.*

### 🔴 AJAN C — canlı kullanıcı turu, sabit sıklıkla

C **pahalıdır** (~10 dk + LLM kotası) ama bu operasyonun **en verimli kusur kaynağıdır**:
*"değişim istendi, TOPLAM verildi"* · *"`bakiye` iki cube'ta, fark ₺11,86M"* · *"ham kolon
adı ekranda"* — üçünü de süit değil, **C** buldu. Bu yüzden azaltılır, **kaldırılmaz**.

| Demet türü | C koşar mı |
|---|---|
| Risk dosyasına dokunan demet *(D-b)* | ✅ **Zorunlu** — kullanıcıya dönen anlam değişti |
| Kullanıcı yüzeyi *(frontend · chip · `next_steps` · görünen ad)* değişen demet | ✅ **Zorunlu** |
| Yalnız belge · test-aracı · `lab/` demeti | ⛔ **Koşmaz** — ölçecek davranış yok |
| Yukarıdakilerin hiçbiri | **Her 2. demette bir** |
| **Faz sonu** | ✅ **Her hâlükârda zorunlu**, atlanamaz |

C atlandığında **gerekçesi `OPERASYON-DURUM.md`'ye yazılır** — sessiz atlama, *"koşuldu ve
temizdi"* gibi okunur. Atlama kaydı bunu imkânsız kılar.

**Bağlayıcı kurallar:**
* 🔴 **PLANSIZ KAPI YASAKTIR.** `--tam` · `eval` · korpus · senaryo · Ajan C **yalnız**
  `D-a` · `D-b` · `D-c` · faz sonu · **kırmızı doğrulama** anlarında koşar. Bu beş
  andan **herhangi biri dışında** koşturmak — *"bir de şuna bakayım"*, *"emin olayım"*,
  *"nasılsa değiştirdim"* — **kural ihlalidir**, iyi niyetli olması durumu değiştirmez.
  Ölçüldü: bu turda kaybedilen sürenin **çoğu** tam bu plansız tekrar koşumlardandı.
* 🔴🔴 **TESTİN TESTİ DE YASAKTIR — en çok kullanılan kaçamak budur.**
  *"Yeni bir kapı yazdım, çalışıyor mu diye tam süiti koşturayım"* · *"kapıyı kırmızıya
  düşürüp doğrulayacağım"* · *"kapının kapsamını göreyim"* — **hiçbiri** uzun koşum
  gerekçesi değildir. Kullanıcı kararı (2026-08-04): *"kapı testlerini çalıştığını
  kontrol etmek için sürekli uzun test koşuyorsun; bu da yasak. **Uzun test kesinlikle
  demet harici, ne sebeple olursa olsun yasak.**"*

  **Bir kapı nasıl doğrulanır (tek yol):**
  ```
  pytest tests/test_<yeni_kapi>.py        # saniyeler — TEK dosya
  # "önce ölç": kusuru geri koy → AYNI tek dosyayı koş → kırmızı gör → düzelt
  ```
  *"Önce ölç"* disiplini **korunur**, ama tam süitle değil **tek dosyayla** yapılır;
  kusuru geri koyup bir dosya koşmak ~3 saniyedir. Yeni kapının süitin geri kalanıyla
  etkileşimi **demet kapısında** ölçülür — orası zaten koşacak.
* **Gerekçe BEYAN EDİLİR.** Her `--tam` koşumu, yukarıdaki beş andan **hangisi** olduğunu
  söyleyerek başlar ve bu `OPERASYON-DURUM.md`'ye yazılır. Beyansız koşum plansız kapıdır.
  ⟳ **YÜRÜRLÜKTE değil:** kuralı araca gömecek `kapi.py --tam --neden <D-a|D-b|D-c|
  faz-sonu|kirmizi>` kapısı **henüz yazılmadı** — bugün kural yalnız belgede, yani
  unutulabilir. Araca gömülene kadar bu satır bir **niyet**, bir kapı değil.
* **Demet içinde ara `--tam` YOK.** *"Bir de şuna bakayım"* diye tam süit koşturulmaz.
* **Kapsam KIRPILMAZ.** Hız **tekrarı azaltarak** kazanılır, kapıyı gevşeterek değil.
* 🔴 **İki test konteyneri ASLA paralel koşmaz** (compose kilidi `metadata.yml`'de çakışır).
* 🔴 **Kapı konteyneri koşarken repoya YAZILMAZ** — mount canlıdır; bu turda iki sahte hata üretti.
* **Konteyner ADLANDIRILIR** (`--name`) ve bitmeden ikincisi açılmaz.
* `--hizli` bir **KAPI DEĞİL, SİNYALDİR** — kapsanmayan dosya sayısını kendisi yazar.
* 🔴 **Kapı `--rm` ile koşturulmaz, `-d` ile koşturulur.** Ölçüldü: `--rm` konteyner
  çıkınca kütüğü **siler** ve kabuk sarmalayıcısı ölürse özet **tamamen kaybolur** —
  bu turda iki koşum böyle kayboldu. Doğrusu: `docker run -d --name dima-kapi<N> …`,
  sonra `docker wait` + `docker logs`, en sonda `docker rm -f`.
* **İKİNCİ AĞ — CI.** `.github/workflows/backend-ci.yml` her push'ta `pytest -q` koşar
  ve `tests/test_eval_gate.py` süitin içindedir → **eval + süit kapıları CI'da ZATEN VAR**
  *(ölçüldü: `2/4`; eksik olan **korpus + senaryo**, `FAZ 0.15`'in gerçek kapsamı budur —
  sıfırdan kurulum DEĞİL, mevcut workflow'a iki aşama eklemek)*. Demet sonunda push →
  yerelde kaçan bir kırmızıyı CI **eşzamansız ve bedava** yakalar.

**Canlı ortam nasıl üretilir** *(anahtarlar repoda DEĞİL — çalışan servisten alınır):*
```bash
T=$(mktemp -d)
docker inspect dima-backend-core --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | grep -E "^DIMA_(LLM_PROVIDER|LLM_MODEL|ANTHROPIC|GEMINI|GROQ|XAI|OPENROUTER|OLLAMA)" > $T/llm.env
echo "DIMA_VQR_EMBEDDER=off" >> $T/llm.env      # embedder soğuk başlangıcı turu kilitler
docker run --rm --name dima_canli --env-file $T/llm.env -v "$PWD/backend:/app" -w /app \
  dima-test python lab/<arac>.py --live
```
⚠ `$T` **geçicidir ve repoya YAZILMAZ** — anahtar sızıntısı yasağı. Her canlı turdan önce
yeniden üretilir.

**Canlı test (LLM yolunu değiştiren her maddede):**
* `--live` **fail-closed**: gerçek üretici kurulmuyorsa **koşmaz**, sessizce `rule`'a düşmez.
* **Tur arası 5 sn** — ölçülen sınır **10 sn / 10 istek**; bir Intent turu `consistency_k=3` ile **üç** çağrı.
* Rapor başlığı **üreticinin adını** taşır.

---

## 4 · 🔴 MİMARİ KURALLAR — `KAT-1…KAT-5` *(yol haritası §A.5)*

| # | Kural |
|---|---|
| **KAT-1** | **Bir mekanizma iki iş yapmaz.** İki iş yapıyorsa ikiye ayrılır, her birinin **kendi kapısı** olur |
| **KAT-2** | **Cevapsız bir dal, cevaplı bir yolu KESEMEZ.** `source=None` dönen dal `return` etmez |
| **KAT-3** | **Bir katman, kendisini BESLEYEN katmandan önce inşa edilmez** (enabler ≺ tüketici) |
| **KAT-4** | **Kazanç ve gerileme FARKLI ALETLERLE ölçülür** |
| **KAT-5** | **SAYMA — KAPAT.** Kullanıcıya dönük anlam ekseni literal kümeyle tanımlanamaz; **kayıttan türetilir**, **bileşimseldir**, ya da `[SAYIM MUAF]` gerekçesiyle ilan edilir |

> **`KAT-5` bu operasyonun kalbi:** *"bir case veriyorum, bin açık çıkıyor"*un mekanik
> cevabı. **Vaka sayısı sonsuz; kapı sayısı sonlu.**

---

## 5 · 🔴 BELGE KURALLARI — `D1…D5` *(yol haritası §A.2)*

| # | Kural |
|---|---|
| **D1** | **`NE` üç parçalıdır**: backend · sözleşme · frontend. Frontend'i olmayan madde yalnız **`api-only`** beyanıyla geçer |
| **D2** | **Sayı, HEAD damgası ve yeniden ölçüm komutu olmadan yazılmaz**: `<sayı> @<sha> · <komut>` |
| **D3** | **Kanıtsız madde `[DOĞRULANMADI]` işaretlenir**, gizlenmez |
| **D4** | **Her yeni kalıcı artefakt bir MAKBUZA bağlanır** |
| **D5** | **Taşınan madde eski yerinde KÜTÜK bırakır** — istisnasız |

---

## 6 · 🔴 GELİŞTİRME DEĞİŞMEZLERİ — bu depoya özel

1. **Yetim bırakma yasağı.** Backend yeteneği **frontend tüketicisi olmadan "bitti" değildir**.
   Yeni sözleşme alanı → tüketicisi **aynı commit'te**. Yeni uç → çağıranı **aynı commit'te**.
2. **Yeni özellik yeni panel doğurmaz** (PK-1). Panel tavanı **13 export** — doludur.
3. **Kök neden, tikel yama değil** (ADR-0008). Kelime listesi büyütmek çözüm **değildir**.
4. **Aynı kuralın iki sahibi olmaz.** Bu deponun **bir numaralı kusur sınıfı**; kopya yerine
   **çağır**.
5. **Ölçüm aracının kendisi de bir bağımlılıktır** (§6.4). Bu oturumda araç **12+ kez**
   yanlış ölçtü. *Bir kapının doğru sonuç vermesi, doğru şeyi ölçtüğünü göstermez.*
6. **Beyan var, kod onu tanımıyor** — en sık kusur sınıfı. Beyan yazıldıysa **kapısı** olmalı.
7. **Sessiz kesme / sessiz kırpma YOK.** Bir şey yapılmadıysa **nedeni yazılır**.
8. **Üçüncü durum `⊘ ÖLÇÜLEMEDİ`** — ne geçti ne kaldı. Yeşile yuvarlamak *"risk yok"*
   yalanı üretir.
9. **KURAL A** (dondurulmuş taban) · **KURAL B** (her canlı-yol maddesine kill-switch;
   bayrak kapalıyken davranış **birebir bugünkü**, testle kilitli).
10. **Paylaşılan repo:** her git işleminden önce durum yeniden kontrol edilir; ana dizinde
    **asla** `checkout`/`stash` yapılmaz.

---

## 7 · 🔴 ARKA PLAN DENETİMİ — üç ajan, her faz sonunda

> ✅ **Ajanlar bu operasyonun EN GÜÇLÜ YANI.** Bir ara *"arka plan ajanları ana sohbeti
> sildi"* teşhisiyle yasaklanmışlardı; **o teşhis yanlış çıktı** — olayı inceleyen kişi
> ölçtü: sebep başarısız bir **daemon yükseltmesiydi**, ajanlar değil. Yasak kaldırıldı.
>
> 🔴 **Dersi kayda geçiyor:** *teşhisin kendisi de kanıt ister.* Bir olay bir mekanizmayla
> **aynı anda** olduğu için o mekanizmanın suçlusu sayılamaz — bu depo tam bu sınıfı
> avlıyor (`A6`'nın düşme gerekçesi: *"kanıt cümlesi de kanıt ister"*), ve aynı hata
> **kural setinin kendisine** uygulandı: ölçülmemiş bir nedenle çalışan bir mekanizma
> kapatıldı.

Geliştirme **tek başına** yapılmaz. Her faz commit'inden sonra **paralel** üç ajan koşar;
raporları bir sonraki fazın **girdisidir**.

| Ajan | Sorusu | Çıktısı |
|---|---|---|
| **A · PLAN DENETÇİSİ** | *"Yol haritasının o maddesi **tam** uygulandı mı? `NE`'nin üç parçası (backend·sözleşme·frontend) da indi mi? `KAPI` gerçekten kuruldu mu?"* | Eksik kalem listesi + madde/satır atfı |
| **B · BÜTÜNLÜK DENETÇİSİ** | *"Yetim uç/alan doğdu mu? `KAT-1…KAT-5` çiğnendi mi? İkinci sahip doğdu mu? MIMARI güncel mi? Sayı beyanları bayat mı?"* | İhlal listesi + kanıt (dosya:satır) |
| **C · CANLI KULLANICI** | *"Gerçek bir kullanıcı gibi **tek tek** dene — toplu değil. Ne hissettim, nerede takıldım, ne anlaşılmadı?"* | Tur tur deneyim raporu + kırılma anları |

**Getirisi ölçüldü** — bu üç tur olmasa kaybedilecek olanlar:
* **A** → `§3.4-osi` tuzağının **yanlış-negatif** olduğu (faz indiğinde susacaktı)
* **B** → `raporlanabilir()`'in gövde alanlarını **sayması** (`KAT-5`) → `eylem_onerisi`,
  yani **onay kartı ekranda hiç yoktu** — üstelik kusur, o turda *"düzelttim"* denen
  kodun **içindeydi**
* **C** → aynı veriye **üç farklı yüzde** (`+%88` → `−%72 "iyileşti"` → `+%98`)

> 🔴 **C'nin kuralı:** **toplu koşum YAPMAZ.** İnsan gibi tek tek yazar, cevabı okur,
> ona göre bir sonrakini sorar. Rate limit: **tur arası 5 sn**.
> ⚠ **Konteyner:** C canlı tur için konteyner açar; o koşarken **ikinci test konteyneri
> açılmaz** (compose kilidi `metadata.yml`'de çakışır).

> ⚠ **Ajan raporu bir OTORİTE DEĞİLDİR.** İki kez düşük saydılar (14 ↔ gerçek 17 ·
> *"1/47"* ↔ gerçek 13). Kritik bir sayı **kendim ölçmeden** belgeye yazılmaz (§6/5).

**Denetim bulgusu = bir sonraki fazın girdisi.** Kritik bulgu varsa **sıradaki maddeden
önce** işlenir. Görev metinleri: **`OPERASYON-DENETIM.md`**.

---

## 8 · 🔴 BAĞLAM SIFIRLAMASINA KARŞI — üç katman

1. **`OPERASYON-DURUM.md`** — her faz sonunda güncellenir ve **commit edilir**:
   hangi faz · hangi madde · ne yapıldı · ne kaldı · bir sonraki adım · açık borçlar.
2. **`backend/CLAUDE.md`** — bu dosyalara **işaret eder** (her oturumda otomatik yüklenir).
3. **Kalıcı bellek** — `project_dima_v1_operasyon.md` (yol + kural seti + durum dosyası yolu).

> **Test:** bağlam tamamen silinse, `OPERASYON.md` + `OPERASYON-DURUM.md` + yol haritası
> okunarak **kaldığı yerden** devam edilebilmeli. Bu üçü yeterli değilse eksiklik burada
> giderilir.

---

## 9 · COMMIT DİSİPLİNİ

**Mesaj yapısı:**
```
<tip>(<faz>.<madde>): <tek cümle — NE düzeldi>

ÖLÇÜLEN KUSUR: <sayıyla, komutla>
KÖK NEDEN:     <sınıfı — tikel değil>
DÜZELTME:      <backend · sözleşme · frontend>
KAPI:          <test dosyası::test adı>
ÖLÇÜM:         <önce → sonra · eval · korpus · tsc>
```
* Claude footer **KULLANILMAZ** (saka standardı).
* `MIMARI.md` güncellemesi **aynı commit'te**.
* Faz sonu commit'i **tam kapı yeşil** olmadan atılmaz.

---

## 10 · SIRA — v1 yolu

```
FAZ −2  ✅ BİTTİ (belge onarımı: §G.6f · v2 kilidi · FAZ 0 sırası · 6.0 · Bölüm II borcu · VK-5)
FAZ −1     MIMARI ön hazırlığı (kod yok)
FAZ  0     25 madde — BAĞLAYICI KOŞUM SIRASI yol haritasında yazılı:
           0.22+0.2+0.23 → 0.1 → 0.16 → 0.14 → 0.19 → 0.18 → 0.4/0.5/0.5b → kalan → 0.21
FAZ  1     GÜVENCE (motor-RLS · yetki granülerliği · tazelik)
FAZ  2     SEMANTİK ÇEKİRDEK (hakem — en yüksek etki)
FAZ  3     KAPSAM (sahiplik turu · R1'i kapat)
FAZ  4     ÖLÇÜM ve KANIT
FAZ  5     KONUŞMA ve DENEYİM
FAZ  6     AGENTIC ve ONAYLI YAZMA (6.0 = D9 geri alma ÖNCE)
FAZ  7     ARAYÜZ
FAZ  8     AÇILMA (8.1 kod değil, takvim penceresi — FAZ 1'den sonra AÇILIR)
§G         AJAN KATMANI — v1'e PARALEL, ona bağımlı değil
```

⚠ **Kalan 10 belge kusuru** (sayı çelişkileri · 4 ölü bayrak · `II-D.1b` · iki biçim
hatası · FAZ 7 kapsamı) **ayrı tur açılmadan**, ilgili faza gelindiğinde düzeltilir.

---

## 11 · DURMA ŞARTLARI — sadece bunlar

Döngü **v1 bitene kadar** sürer. Yalnız şu üç durumda durulur ve sorulur:

1. **Geri alınamaz / dışa dönük** bir işlem gerekiyorsa (push · dış servis · veri silme).
2. **Alan bilgisi kararı** gerekiyorsa (ör. FAZ 3.1 sahiplik turu: *hangi cube `bakiye`'nin
   sahibi* — bu mühendislik değil **iş** kararıdır).
3. **Ölçüm, planın bir varsayımını çürütüyorsa** — plan değişikliği kullanıcının kararıdır.

*Bunların dışında izin istenmez.*
