# NELER DEĞİŞTİ — arayüz turu · 2026-08-05

**Kime:** ürünü kullanan ve test eden herkes. Teknik bilgi gerekmez.
**Neden okuyun:** ekranın **düzeni** değişti. Hiçbir özellik kaybolmadı, ama bazıları
**başka yere** taşındı — ve nereye taşındığını bilmek aramaktan hızlıdır.

> 🔴 **Değişmeyen tek söz:** hiçbir yetenek silinmedi. Bir kapı bunu her koşumda
> ölçüyor (arayüzdeki **269 işlev** tek tek sayılıp erişilebilirlikleri denetleniyor).

---

## 1 · Sağdaki ikon şeridi **kalktı**, soldaki çubuk **açılır** oldu

**Önce:** sağ kenarda dar bir ikon şeridi; soldaki sohbet paneli **hep açıktı**.
**Şimdi:** solda açılır/kapanır bir çubuk (Gemini/Claude gibi). `Ctrl/⌘+B` ile aç-kapa.

| Aradığınız şey | Şimdi nerede |
|---|---|
| Yeni sohbet | Çubuktaki **✎** — 🔴 **çubuk kapalıyken de görünür** |
| Sohbet geçmişi | Çubuğun içinde, *Bugün · Dün · Son 7 gün · Son 30 gün · Ocak 2026…* diye gruplu |
| Bildirim · Pano · Yardım · Ayarlar | Çubuğun alt bölümünde, aynı isimlerle |
| Kimlik · bağlantı durumu · tema · çıkış | Çubuğun **en altında** |

⚠ **Neden taşındı:** sol panel *"sohbet"* gibi görünüyordu ama aslında **yeni konu +
geçmiş** idi. Bir şeyin **ne olduğu** ile **neye benzediği** ayrıştığında, kullanıcı
her seferinde yeniden öğrenmek zorunda kalır.

📱 **Mobilde:** çubuk üstte bir bant olur, dokununca kayarak açılır.

---

## 2 · Grafikler artık **boğmuyor** — makine panele taşındı

**Önce:** her cevap kartında grafiğin etrafında **~59 düğme/katman** vardı. Grafik,
cevabın kendisiymiş gibi duruyordu.

**Şimdi:**

| | sohbette | panelde |
|---|---|---|
| ne var | cevap cümlesi + sayı + **temiz grafik** | aynı grafik + **tüm makine** |
| kontrol | 🔴 sıfır — bir tek *"panelde aç"* | yorum çubuğu · katkı · reçete · kök-neden |
| rolü | **okunur** | **çalışılır** |

🔴 **Panel bir modal DEĞİLDİR** ve bu bilinçli: panel açıkken **sohbete yazmaya devam
edebilirsiniz**. Grafiğe bakarken yorum yazmak için onu kapatmak zorunda kalmazsınız.
Panelin sol kenarından **sürükleyerek** genişletebilir, klavyeyle de (`←`/`→`/`Home`/`End`)
boyutlandırabilirsiniz. `Esc` yalnız **odak panelin içindeyken** kapatır — komposere
yazarken bastığınız `Esc` paneli kapatmaz.

---

## 3 · 🌳 Kök-neden haritası — *"hangi yola bakmaya değer?"*

**Önce:** kırılıma inmek bir **tablo yığınıydı**; hangi yolun anlamlı olduğunu ürün
söylemiyordu, sayıların içinde kaybolmak kolaydı.

**Şimdi:** panelde **🌳 kök neden haritası** açılır. Her aday bir **hipotez kartıdır** ve
**siz tıklamadan önce** puanlanmıştır:

| görünüm | anlamı |
|---|---|
| **koyu · dolu · turuncu** | **kanıtlı** — veri var, sinyal güçlü |
| **orta ton** | **zayıf** — veri var ama değişim dağılmış, tek sorumlu yok |
| **silik · kesik kenarlı** | **⊘ ölçülemedi** — *bakılmadı*, **"yok" DEĞİL** |
| **en silik** | **kapsam dışı** — bu konu o boyutu taşımıyor, ilişkili bir konu taşıyor |

🔴 **Silik olanlar da tıklanabilir.** Hiçbiri devre dışı bırakılmaz — çünkü bazen
**verinin yokluğu bulgunun kendisidir** (*"o vardiyada hiç kayıt yok"*).

⚠ Ve her kart **neden** o ağırlıkta olduğunu **yazar**: *"en büyük tek segment değişimin
%61'ini taşıyor (7 segment arasında — eşit dağılsa %14 olurdu)."*

**Boğulmama kuralı:** ekranda her an yalnız **kat ettiğiniz yol** ve **açık olan tek kat**
bulunur. Kardeş dallar açılmaz.

### Not alma — *kökeniyle birlikte*

Herhangi bir düğümde **✎ bu noktada not al** deyip yazdığınızda, not sohbete **yolu ile
birlikte** düşer:

```
kök ── Makine ── Vardiya ── ✎ "kalibrasyon şüphesi"
```

> *Bir not, kökeni olmadan bir kanaattir.* Yol kaydedilmezse not yeniden üretilemez,
> doğrulanamaz, tartışılamaz.

---

## 4 · Artık **her grafik türüne** tıklanabiliyor

**Önce:** çizgi/sütun/pasta grafiklerinde bir noktaya tıklayıp kırılıma inebiliyordunuz,
ama **panelli grafik** ve **ısı haritası** tıklamaya cevap vermiyordu.

**Şimdi:** hepsi çalışıyor. Panelli bir grafikte bir çubuğa tıklamak (panel + kategori +
seri) ya da ısı haritasında bir hücreye tıklamak (satır + sütun) artık **tüm koordinatı**
birlikte taşıyor.

⚠ **Tek istisna ve sebebi yazılı:** ısı haritasının **kenar hücreleri** (satır/sütun
ortalamaları) bir kesişim değil bir **özettir** — orada kırılacak tek bir satır kümesi
yoktur ve ürün bunu **söyler**, sessizce hiçbir şey yapmaz.

---

## 5 · Okunabilirlik — *metin artık metin gibi görünüyor*

- Cevabın **anlatımı** 12 pikselden **16 piksele** çıktı, satır aralığı açıldı.
- Sohbet akışında **10 pikselin altında metin kalmadı**.
- ⚠ **Sayılar, SQL, kod ve tablo hücreleri sabit genişlikte (mono) KALDI** — bu bir
  süs değil: orantılı yazı tipinde bir sütundaki rakamlar birbirinin altına düşmez.
- Kartlar artık **yüzey** kazandı (yumuşak köşe + kendi zemini); ayrımlar çizgiyle
  değil boşlukla kuruluyor. *"Bembeyaz dikdörtgen"* görüntüsü buradan geliyordu:
  kart beyazdı ve sayfa da beyazdı, yani hiç katman yoktu.
- **Karanlık temada** zemin biraz açıldı: saf siyaha çok yakın bir zeminde beyaz metin
  *kanar* (halation) ve göz yorar.

---

## 6 · Küçük ama sinsi düzeltmeler

| ne | önce | şimdi |
|---|---|---|
| **⇩ Denetim kaydı (JSON-LD)** | koddaydı ama **hiçbir yerden açılamıyordu** | sol çubuk → **Kanıt geçmişi** |
| **Kanıt geçmişi (son 20 makbuz)** | aynı sebep | aynı yer; bir kayda tıklayınca detayı açılır |
| **"portföy" kapsamı** *(süperadmin)* | seçenek **hiç görünmüyordu** | görünüyor *(görünürlük bir yetki değil; sınırı sunucu koyar)* |
| **Tema anahtarı** | iki yerde vardı ve **birbirinden habersizdi** | ikisi aynı değeri gösterir |
| **Takip sorusunda kapsam/mod ayarları** | yalnız ilk soruda vardı | her iki komposerde de aynı |

---

## 7 · Test ederken bakılacak beş şey

1. Çubuğu kapatın — **✎ hâlâ görünüyor mu?**
2. Bir kartta **"panelde aç"** deyin — panel açıkken **sohbete yazabiliyor musunuz?**
3. Panelde **🌳 kök neden haritası** açın — **silik** bir düğüme tıklanıyor mu?
4. Bir düğüme inip **✎ not al** — not sohbete **yolla birlikte** düştü mü?
5. Ekranı **375px**'e daraltın — taşma var mı, üst bant çıktı mı, yol çipleri kaydırılıyor mu?

> ⚠ **2. madde en değerlisidir.** Bir analiz yüzeyinin modal olması, kullanıcıyı
> *"bak"* ile *"yaz"* arasında seçim yapmaya zorlar — ve insanlar bunu aşmak için
> aynı sayfayı ikinci bir sekmede açar. O davranış, ürünün başarısızlık sinyalidir.
