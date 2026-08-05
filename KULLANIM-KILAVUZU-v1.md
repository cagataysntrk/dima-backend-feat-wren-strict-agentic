# DİMA — KULLANIM KILAVUZU · v1

**Sürüm:** v1 · **Tarih:** 2026-08-05 · **HEAD:** `2bb190a`
**Kime:** ürünü kullanacak ve test edecek herkes — teknik bilgi gerekmez.

> 📌 Bu kılavuz **ölçülerek** yazıldı: kaynaktaki **165 buton** tek tek okundu, her
> maddenin karşılığı koddadır. *Ekranda olmayan bir şey burada anlatılmaz; burada
> anlatılan her şey ekrandadır.* Bugün **kapalı** olan yetenekler ayrı bölümde
> (**§9**) — orada olduğunu bilmek, aramakla vakit kaybetmekten iyidir.

---

## §1 · EKRANIN HARİTASI — üç bölge ve bir şerit

Uygulama **tek sayfadır**; menü ağacı yoktur. Her şey üç yerde olur:

```
┌────────────────────────────┬─────────────────────────────┬──┐
│   SOL — SOHBET             │   SAĞ — RAPOR               │şe│
│   sorunuzu buraya yazarsınız│   cevaplar burada birikir   │ri│
│   konu listesi burada       │   her cevap bir KART        │t │
└────────────────────────────┴─────────────────────────────┴──┘
```

| Bölge | Ne işe yarar |
|---|---|
| **Sol · Sohbet** | Soru yazarsınız. Geçmiş konularınız (*thread*) burada listelenir. Kapsam/mod anahtarları buradadır. |
| **Sağ · Rapor** | Cevaplar **kart** olarak birikir. Her kartın kendi düğmeleri vardır. Kartlar **konuya göre** gruplanır. |
| **Şerit (rail)** | Sağ kenarda yüzen ikonlar. **Mobilde ekranın altına iner.** |
| **Analiz Tuvali** | İsteğe bağlı üçüncü bölge: seçtiğiniz kartları **rapor hâline** getirir. |

### 1.1 · Şerit ikonları — yukarıdan aşağı

| İkon | Adı | Ne açar |
|---|---|---|
| ↺ | **Sohbet geçmişi** | Eski konuşmalarınız; birine tıklayınca kaldığınız yerden devam edersiniz |
| 🔔 | **Bildirimler** | Zamanlanmış raporlardan ve uyarılardan gelen bildirimler |
| ▦ | **Panolar** | Canlı izlenen KPI panolarınız |
| ✓ | **Ölçü inceleme** | Yeni ölçü adaylarının onay kuyruğu |
| ? | **Yardım** | *"Ne sorabilirim"* — departmana göre örnek sorular |
| ⚙ | **Ayarlar** | Şema · Veri Kaynağı Bağlantıları · Zamanlamalar · Tercihler |
| ⏻ | **Çıkış** | Oturumu kapatır |
| ☀/☾ | **Tema** | Aydınlık ↔ karanlık; tıklayınca değişir |

> ⚠ **Şeritte bazı ikonları göremeyebilirsiniz — bu bir hata değildir.**
> **Panolar** ikonu `dashboards` özelliği açıksa, **Ölçü inceleme** ikonu
> `measure:read` yetkiniz varsa çıkar. Şerit **rolünüze göre kısalır**.

---

## §2 · İLK SORU — en basit kullanım

1. Sol taraftaki kutuya sorunuzu **günlük Türkçe** ile yazın: *"bu ay toplam üretim"*.
2. **Enter**'a basın. *(Alt satıra geçmek için `Shift+Enter`.)*
3. Sağda bir **cevap kartı** belirir.

**İlk açılışta** kutunun altında **örnek sorular** görürsünüz (*Landing*). Bunlar
uydurma değildir — şirketinizin kataloğundan, departmana göre gelir:
*Üretim · Bakım · Kalite · Satış/Ticaret · Finans · Sürdürülebilirlik*.
Bir örneğe tıklamak onu **doğrudan sorar**.

### 2.1 · Sistem sorunuzu anlamazsa ne olur

Üç dürüst davranıştan biri olur — **hiçbiri uydurma cevap değildir**:

| Ne görürsünüz | Anlamı | Ne yapmalısınız |
|---|---|---|
| *"Hangi dönem?"* | Tarih aralığı belirsiz | Dönem söyleyin: *"bu yıl"* |
| *"Hangi ölçü?"* / *"Hangi konu?"* | Birden fazla anlam mümkün | Şıklardan seçin |
| *"Şu kısmı anlayamadım…"* | Bir kelime tanınmadı | Farklı ifade edin |

> 🔴 **Netleştirme bir başarısızlık değildir.** Sistem *"cari mi mizan mı?"* diye
> sorduğunda **doğru davranmış** demektir; sormadan birini seçmek çok daha pahalıdır.

---

## §3 · CEVAP KARTI — arayüzün kalbi *(25 düğme)*

Her cevap bir karttır ve kartın üstünde şu düğmeler bulunur. **Kart, sorunun türüne
göre bazı düğmeleri göstermez** — hepsi her zaman çıkmaz.

### 3.1 · Görünüm düğmeleri

| Düğme | Ne yapar |
|---|---|
| **grafik / tablo / pivot** | Aynı sonucun üç görünümü. Pivot = çapraz tablo *(satır × sütun)*. |
| **◀ ▶** | Birden çok panel varsa paneller arasında gezinir |
| **Dışa aktar ▾** | Üç seçenek: **Grafik · SVG** · **Tablo · CSV** · **Yazdır / PDF** |
| **⎙ yazdır** | Rapor görünümünde yazdırma / PDF |

### 3.2 · Derinleşme düğmeleri

| Düğme | Ne yapar | Ne zaman kullanılır |
|---|---|---|
| **kırılım / drill** | *"Bu sayı hangi kırılımlardan oluşuyor?"* — alt kırılım paneli açılır | Bir toplam gördünüz, içini merak ediyorsunuz |
| **Hücreye tıklama** | Tablodaki bir hücrenin **altındaki** kırılıma iner | *"Bu makinede ne oldu?"* |
| **Grafikte bir çubuğa tıklama** | O dilimi çapa yapar; konuşma **o dilim üstünde** yürür | *"Şu düşüş ne?"* |
| **Sonraki adım chip'leri** | Sistemin önerdiği devam soruları — **tek tıkla** koşar | Ne soracağınızı bilmiyorsanız |

> 💡 **Chip'ler LLM kullanmaz** — düğmenin kendi ipucu bunu yazar:
> *"Deterministik koşar — LLM yok."* Yani hızlı ve tekrarlanabilirdir.

**Drill panelinde** ayrıca: geçmiş adımlar arasında gezinme · **SQL göster** ·
**SQL'i kopyala** · **sözleşme** *(kanıt kaydı)* · **Ham satırları göster**
*(bu dilimin gerçek kayıtları)*.

⚠ Bazı şekillerde drill **kısıtlıdır** ve sistem **sebebini söyler**: `facet`/`heatmap`
iki filtre gerektirir, bugünkü drill isteği tekildir. *Reddin sebepsiz olması bir
kusurdu; düzeltildi.*

### 3.3 · Güven ve kanıt düğmeleri

| Düğme | Ne gösterir |
|---|---|
| **iz göster** *(trace)* | *"Bu sorgu nasıl çözüldü?"* — hangi yoldan geçti |
| **SQL göster** | Üretilen SQL'in kendisi |
| **sözleşme** *(Query Contract)* | Soru + sorgu + sonuç özeti — **kanıt kaydı**. Bu kayıt **yeniden koşturulabilir** (`replay`) ve aynı sonucu vermelidir. |
| **makbuz** | Katmanlı kanıt: hangi araçlar çağrıldı, hangi maliyetle |
| **kaynak rozeti** | Cevabın nereden geldiği — `cube` *(deterministik)* · `vqr` *(öğrenilmiş)* · `catalog` · `meta` vb. **17 ayrı değer** |

> 🔴 **Rozete bakmayı alışkanlık edinin.** `source=cube` *"bu sayı sorgudan geldi"*
> demektir. Rozetsiz ya da farklı rozetli bir cevap, farklı bir güven düzeyindedir.

### 3.4 · Geri bildirim düğmeleri

| Düğme | Ne yapar |
|---|---|
| **✓ doğrula** | *"Bu cevap doğru"* — sistem bunu **öğrenir** (VQR) |
| **✗ yanlış** | *"Bu rapor yanlış"* — isteğe bağlı yorum ekleyebilirsiniz |
| **↩ geri al** | Verdiğiniz ✓/✗ oyunu geri alır |

> ✅ Bu, arayüzdeki **tek gerçek geri alma** yoludur. *(Silme işlemlerinde geri alma
> yoktur — **§8 uyarısına** bakın.)*

### 3.5 · Eylem düğmeleri

| Düğme | Ne yapar |
|---|---|
| **panoya ekle** | Bu grafiği/tabloyu bir panoya koyar — panoda **canlı izlenir**. Menüden pano seçer ya da **+ yeni pano** dersiniz. |
| **zamanla** | Bu raporu belirli aralıkla otomatik çalıştırır ve bildirim gönderir. Alarm türü ve periyot seçilir. |
| **karta yanıt ver** | Bu kartın **üstüne** konuşma açar; thread'in sonuna eklenir |
| **onay kartı** | Sistem bir iş önerdiğinde çıkar: **onayla** ya da **vazgeç** |

> ⚠ **Onay kartına yazıyla *"evet"* demek bugün çalışmıyor** — düğmeye basmak gerekir.
> *(Bilinen eksik; borç defterinde kayıtlı.)*

---

## §4 · YORUM ÇUBUĞU — sistemin anladığını *düzeltmek* *(19 düğme)*

Cevabın üstünde küçük etiketler (**chip**) görürsünüz: **ölçü** · **kırılım** ·
**filtre** · **dönem** · **zaman kovası**. Bunlar sistemin sorunuzdan **çıkardığı
yorumdur** ve **oynanabilir**.

| İşlem | Nasıl |
|---|---|
| Bir ölçüyü çıkar | Chip'in yanındaki **×** |
| Bir kırılımı çıkar | Kırılım chip'inin **×**'i |
| Kırılım değerlerini süz | Chip'e tıkla → listeden seç |
| Dönemi değiştir | Dönem chip'ine tıkla → hazır aralık **ya da özel tarih** gir |
| Zaman kovası *(aylık/haftalık)* | Kova chip'i |
| **Kıyas anahtarı** | *"Geçen dönemle karşılaştır"* — açık/kapalı |

> 🔴 **Buradaki her düzenleme LLM'siz çalışır.** Bileşenin kendi notu:
> *"Her düzenleme deterministik `/cube` ucuna gider (LLM yok)."* Yani düzeltmek
> **hızlıdır ve her seferinde aynı sonucu verir**.

**Neden önemli:** sistem sizi yanlış anladıysa **soruyu yeniden yazmanız gerekmez** —
yanlış chip'i düzeltirsiniz.

---

## §5 · SOHBET PANELİ — konu, kapsam, mod

| Kontrol | Ne yapar |
|---|---|
| **Thread listesi** | Konularınız. Birine tıklamak o konuya döner. |
| **× (thread kapat)** | Bu konuyu kapatır; sonraki soru **yeni bir konu** başlatır |
| **+ yeni sohbet** | Temiz bir başlangıç |
| **📎 Excel/CSV yükle** | Bu sohbete özel **geçici** veri kaynağı |
| **Kapsam anahtarı** | `departman` · `genel` · `portföy` — katalogun ne kadarını gördüğünüz |
| **Yol sınırı** | `deterministik` ↔ `llm` — cevabın hangi yoldan gelmesine izin verdiğiniz |
| **Mod** | `hızlı` ↔ `derin` |

> ⚠ **Kapsam · Mod anahtarları bugün kapalı olabilir** (`kapsam_mercegi`,
> `hizli_derin` özellikleri). Görmüyorsanız **§9**'a bakın.
>
> 🔴 **Kapsam bir GÖRÜNÜRLÜK aracıdır, güvenlik sınırı DEĞİLDİR.** Kapsamı genişletmek
> size yetkiniz olmayan veriyi **açmaz**; yalnız katalogda daha fazlasını gösterir.

---

## §6 · ANALİZ TUVALİ — kartlardan rapor yapmak

| Düğme | Ne yapar |
|---|---|
| **tuval modu** | Açıkken tıkladığınız kart/öneri **tuvale eklenir** |
| **▲ ▼** | Blokları sıralar |
| **×** | Bloğu tuvalden kaldırır |
| **▦ panoya ekle** | Bloğu bir panoya taşır |
| **dışa aktar** | Tuvali rapor olarak dışa aktarır |
| **tuvali temizle** | Tuvalı boşaltır |

**Kullanım:** üç dört soru sorun → beğendiğiniz kartları tuvale ekleyin → sıralayın →
dışa aktarın. Bu, *"müdüre sunum"* akışının v1'deki karşılığıdır.

---

## §7 · PANELLER — şeritten açılanlar

### 7.1 · Sohbet geçmişi
Eski konuşmalar. **Bir satıra tıkla** → devam et. **+ yeni sohbet**. **sil** *(⚠ §8)*.

### 7.2 · Bildirimler 🔔
Zamanlanmış raporlardan gelen uyarılar. Her uyarıda:
**"bu uyarı neden geldi"** *(aç/kapa)* ve **kanıt kaydı** *(sözleşme)*.

### 7.3 · Panolar ▦
| Düğme | Ne yapar |
|---|---|
| **+ yeni pano** | Pano oluşturur (ad sorulur) |
| **panoya tıkla** | Panoyu açar |
| **yeniden adlandır** | Ad değiştirir |
| **görünürlük** | Özel ↔ paylaşılan |
| **sil** | Panoyu siler *(⚠ §8)* |

**Pano görünümünde:** **↻ yenile** · **dışa aktar** · widget **genişliği** *(1↔2 sütun)* ·
widget **kaldır** · **✕ kapat**.

### 7.4 · Ölçü inceleme ✓
Sistemin bulduğu **yeni ölçü adaylarının** onay kuyruğu. Durum süzgeçleri
*(tümü/bekleyen/…)* ve dört eylem:

| Düğme | Ne yapar |
|---|---|
| **önizle** | Aday ölçüyü **uygulamadan** dener |
| **onayla** | Ölçüyü kataloğa alır |
| **reddet** | Adayı eler |
| **kullanımdan kaldır** | Var olan bir ölçüyü emekliye ayırır |

> 💡 Onaylamadan önce **blast-radius** *(etki alanı)* bilgisi vardır: bu ölçü
> değişirse **neler etkilenir**.

### 7.5 · Yardım ?
Departman sekmeleri + örnek sorular. Bir örneğe tıklamak onu **sorar**.

### 7.6 · Ayarlar ⚙ — dört sekme

**Şema** — hangi cube/ölçü/boyutlar var. Ölçülere **sahip atama** yapılabilir
*(sahiplik kaldırıldığında kayıt silinmez)*.

**Veri Kaynağı Bağlantıları** — en kritik ekran:

| Adım | Düğme | Ne yapar |
|---|---|---|
| 1 | **bağlantıyı test et** | Erişimi dener |
| 2 | **oluştur** | Bağlantıyı kaydeder |
| 3 | **incele** | Keşfedilen şemayı taslak olarak gösterir |
| 4 | **onayla** | Taslağı semantik modele işler |
| — | **semantik model ithal / ihraç** | Hazır bir modeli getirir/dışarı verir |
| — | 🔴 **sil** | **Bağlantıyı KALICI siler** *(⚠ §8)* |

> ⚠ İnceleme adımında dört alan kontrol edilir: **fan-out sertifikası** ·
> `always_filter` · `additive:` · `dimension_origin`. Sessiz bir *"sağlıklı"*
> yeterli değildir.

**Zamanlamalar** — kurduğunuz otomatik raporlar. **▶ şimdi çalıştır** · **sil** *(⚠ §8)*.

**Tercihler** — sunum tercihleri ve bildirim kanalı tercihleri. **kaydet** · **sil**.

---

## §8 · 🔴 SİLME UYARISI — okumadan silmeyin

**Arayüzde 7 silme düğmesi vardır ve hiçbiri onay sormaz.** Tek tıkla iş biter.
**Geri alma düğmesi yoktur.**

| Silinen | Sunucuda ne olur | Pratikte |
|---|---|---|
| Sohbet · Pano · Widget · Tercihler | işaretlenir *(soft-delete)*, kayıt kalır | **Arayüzden geri getiremezsiniz** |
| 🔴 **Zamanlama** | **kalıcı silinir** | Geri dönüşü yok |
| 🔴 **Veri kaynağı bağlantısı** | **kalıcı silinir** | Geri dönüşü yok — yeniden kurmanız gerekir |

> 🔴 **Ayrıca:** dört panelde silme/yeniden adlandırma **başarısız olursa ekranda
> hiçbir uyarı çıkmaz** *(Panolar · Pano görünümü · Sohbet geçmişi · Analiz Tuvali)*.
> Satır yerinde durur. **Bir işlem olmadıysa sayfayı yenileyip doğrulayın.**
>
> Bu iki nokta `UI-UX-DENETIM.md` **F1 · F2 · F3**'te kayıtlıdır ve düzeltme sırası
> orada yazılıdır. Kılavuz **bugünü** anlatır, olması gerekeni değil.

---

## §9 · BUGÜN KAPALI OLANLAR — *"yok" değil, "kapalı"*

Aşağıdakiler **yazıldı ve testlendi**, ama v1'de kullanıcıya **açılmadı**. Aramayın;
görmüyor olmanız bir kurulum hatası değildir.

| Özellik | Ne yapacaktı | Durum |
|---|---|---|
| **Tazelik** | *"Bu veri hangi tarihe kadar?"* | 🔴 bağlanmamış |
| **Metrik sertifikası** | *"Bu tanımı kim onayladı?"* | 🔴 bağlanmamış |
| **KPI pin** | KPI'ı panoda sabitleme | 🔴 bağlanmamış |
| **"Bunu takip et"** | Sorudan otomatik zamanlama | ⚠ kapalı |
| **"Paylaş / müdüre 3 cümle"** | Paylaşılabilir özet | ⚠ kapalı |
| **Hedef kıyası** | *"Hedefin neresindeyiz?"* | ⚠ kapalı |
| **İçgörü paketi** | Aynı sonucun birden çok ekseni | ⚠ kapalı |
| **Bilgi merkezi** | Hayalet seri + iş kuralları | ⚠ kapalı |
| **DCM modu** | LLM'siz kilit mod *(banka/kamu)* | ⚠ kapalı |
| **Kapsam merceği** | Departman görünürlüğü | ⚠ kapalı |
| **Hızlı ↔ Derin** | Cevap derinliği anahtarı | ⚠ kapalı |
| **Onay talebi + süre aşımı** | Onayın 30 dk sonra düşmesi | ◐ yarısı bağlı |
| **`/settings` tam sayfa** | 8 sekmeli yönetim ekranı | ⊘ yapılmadı |
| **Sankey · Pareto · Bubble · Gauge · Harita** | 5 yeni grafik tipi | ⊘ yapılmadı |
| **Komut paleti** | `Cmd+K` hızlı erişim | ⊘ yapılmadı |
| **Kurulum sihirbazı** | Yeni müşteri açılışı | ⊘ yapılmadı |

> 🔴 **Test ederken kritik ayrım.** *"⚠ kapalı"* = bir ayar açılınca gelir.
> *"🔴 bağlanmamış"* = ayarı açmak **hiçbir şey yapmaz**, önce kod bağlanmalı.
> Ekranda ikisi **birebir aynı görünür**. Ayrıntı: `DENETIM-RAPORU_2026-08-05.md` §11.

---

## §10 · KLAVYE

| Tuş | Ne yapar |
|---|---|
| **Enter** | Soruyu gönderir |
| **Shift + Enter** | Alt satıra geçer |
| **Escape** | Açık modal/paneli kapatır |
| **Tab** | Modal açıkken odak **içeride** kalır |
| **Enter / Space** | Seçili tablo hücresinde drill yapar |

> ⚠ Global kısayol *(`Cmd+K` vb.)* **yoktur**. Komut paleti v1'de yok.

---

## §11 · ERİŞİLEBİLİRLİK — ürünün taahhüdü

Bunlar **testle kilitlidir**, iyi niyet beyanı değildir:

- Metinsiz her düğme **`aria-label` taşır** — *"bir etiketi hover'a bağlamak, onu fareye bağlamaktır."*
- İşlevsel kontroller **yalnız emojiden** ibaret olamaz.
- Modallar **odağı tutar** ve kapanınca odağı **geri verir**.
- **Renk tek kanal değildir**: *"devre dışı"* ile *"soluk ama tıklanabilir"* asla aynı
  görünmez; hata **metinle de** söylenir.
- Üç ekran genişliğinde *(375 / 768 / 1024)* **yatay taşma yok**.
- **Mobilde şerit alta iner** — başparmakla ulaşılabilir.

---

## §12 · HIZLI TEST TURU — 10 dakikada her şeye dokunmak

1. *"bu ay toplam üretim"* sor → kart geldi mi?
2. Yorum çubuğundan **dönemi** *"bu yıl"* yap → sayı değişti mi?
3. **grafik → tablo → pivot** geç → üçü de çalışıyor mu?
4. Bir çubuğa/hücreye tıkla → **drill** açıldı mı, **sebepli** mi?
5. **iz göster** + **SQL göster** + **sözleşme** → kanıt zinciri tam mı?
6. **Sonraki adım chip'ine** bas → LLM'siz, hızlı mı?
7. **✓ doğrula** → sonra **geri al** → oy geri alındı mı?
8. **panoya ekle** → **+ yeni pano** → panoda göründü mü?
9. **zamanla** → **Zamanlamalar** sekmesinde çıktı mı? → **▶ şimdi çalıştır**
10. **📎 Excel yükle** → yüklediğin veriye soru sor
11. *"asdf qwerty"* sor → **dürüst duvar** mı, uydurma mı?
12. *"neler yapabilirsin"* sor → yetenek cevabı geldi mi?
13. Ekranı **375px**'e daralt → taşma var mı, şerit alta indi mi?
14. **Tema** düğmesine bas → karanlık mod tutarlı mı?

> ⚠ **11. adım en değerlisidir.** Bir BI ürününün kalitesi doğru soruya verdiği
> cevapta değil, **cevaplayamadığı soruda ne yaptığında** ölçülür.

---

> *Bir kılavuz, ürünü olduğundan iyi anlatırsa kılavuz değil reklamdır.*
> *Bu yüzden §8 ve §9 burada — silinmesi kolay, ama okunması gereken iki bölüm.*
