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
6. DOĞRULA  → hızlı kapı (geliştirme) → tam kapı (faz sonu, TEK sefer)
7. BELGELE  → MIMARI.md'yi AYNI commit'te güncelle (⟳ → ✅, ölçümle)
8. COMMIT   → açıklayıcı mesaj: kusur · kök neden · düzeltme · ölçüm
9. DURUM    → OPERASYON-DURUM.md güncelle + commit
10. DENETİM → arka plan ajanları raporunu oku, bulguları işle
```

**Bir sonraki maddeye geçmek için izin İSTENMEZ.** Döngü v1 bitene kadar sürer.

---

## 3 · 🔴 TEST KAPISI — geliştirmeyi boğmayan disiplin

> Ölçüldü: tam kapı **~15 dk**. İsraf aracın yavaşlığı değil, **faz başına 2-3 kez
> koşturmaktı**.

| Seviye | Komut | Ne zaman | Süre |
|---|---|---|---|
| **0 · anlık** | `pytest tests/test_<dokunulan>.py` | her düzenlemeden sonra | 5–15 sn |
| **1 · hızlı kapı** | `python lab/kapi.py --hizli --degisen <dosyalar>` | geliştirme sırasında | ~40 sn |
| **2 · faz kapısı** | `python lab/kapi.py --tam` | **faz sonu, commit'ten hemen önce, TEK sefer** | ~15 dk |

**Bağlayıcı kurallar:**
* **Ara koşum YOK.** *"Bir de şuna bakayım"* diye tam süit koşturulmaz.
* **Kapsam KIRPILMAZ.** Hız **tekrarı azaltarak** kazanılır, kapıyı gevşeterek değil.
* 🔴 **İki test konteyneri ASLA paralel koşmaz** (compose kilidi `metadata.yml`'de çakışır).
* 🔴 **Kapı konteyneri koşarken repoya YAZILMAZ** — mount canlıdır; bu turda iki sahte hata üretti.
* **Konteyner ADLANDIRILIR** (`--name`) ve bitmeden ikincisi açılmaz.
* `--hizli` bir **KAPI DEĞİL, SİNYALDİR** — kapsanmayan dosya sayısını kendisi yazar.

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
