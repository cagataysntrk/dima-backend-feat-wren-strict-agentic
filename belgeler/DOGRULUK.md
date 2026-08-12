# DİMA — DOĞRULUK SAYISI

> **Ölçüm tarihi:** 2026-08-12 · **Kod sürümü:** `ddc6fa3`
> **Yeniden üretmek için:** `python lab/kapi.py --tam` *(repo kökünden, ~1 dk 50 sn, LLM'siz)*
> **Ham çıktı:** `backend/lab/reports/nl_corpus.md` · `nl_corpus.json`

Bu belge bir pazarlama sayfası değil, bir **ölçüm kaydıdır**. Sayının yanında **paydanın
tanımı**, **yöntem** ve **bilinen körlükler** duruyor — çünkü bir doğruluk oranı, paydası
söylenmeden bir iddia bile değildir.

---

## 1 · Sayı

| ölçüt | sonuç | **%95 güven aralığı** | payda | ne ölçer |
|---|---|---|---|---|
| **Doğru küp** | **%95,6** | **[%95,2 – %96,0]** | **11.237** | Sorunun üretildiği küp ile cevabın küpü aynı mı |
| **Semantik vaka** | **%94,4** | **[%92,3 – %96,0]** | **591** | `(küp, ölçü, niyet)` üçlüsü — dönem/boyut çarpımı tek vakaya çöker |
| **Cevapsız kesme** | **%19,7** | **[%19,1 – %20,3]** | **14.957** | Cevap yok · kullanıcı durdurmadı · Discovery hiç koşmadı |
| **Sessiz yanlış** | **7** (%0,31) | **[%0,15 – %0,63]** | **2.286** | Gerçek-dünya korpusu: uyarısız, rozetli, yanlış sayı |

### 🔴 Aralık neden yazılı — ve neyi yasaklıyor (`§A8`)

Bir oran, **paydası** ve **belirsizliği** söylenmeden bir iddia bile değildir. Inspect
AI'ın sorusu şuydu: *«20 senaryoluk paydada %85 ile %90 arasındaki fark **gürültü mü**»* —
ve tek cevabı bir **aralıktır**.

    Wilson skor aralığı (z = 1,96) — nadir olaylarda normal yaklaşımdan doğru,
    payda küçüldükçe aralık GENİŞLER ve bu genişlik bir uyarıdır.

⚠ Ne yasaklıyor: **aralıkları örtüşen iki sayıyı «iyileşme» diye ilan etmek.**
`semantik vaka` aralığı **±1,87 puan** (n=591); yani %94,4 → %95,5 gibi bir değişim
**ölçüm gürültüsüdür**, bir kazanç değil. Buna karşılık `doğru küp` aralığı **±0,38
puan** (n=11.237) — orada yarım puanlık bir düşüş **gerçektir**.

> *Bir oranı aralığı olmadan yayımlamak, okuyucuya kendi payda duygusunu uydurtmaktır.*

### 🔴 GÜVENİLİRLİK — reddin İKİ TÜRÜ ayrı sayılır (`§A7`, EHRSQL deseni)

EHRSQL'in (NeurIPS 2022) ölçütü bir doğruluk oranı değil bir **davranış** ölçütüdür:

| davranış | işaret | bizde |
|---|---|---|
| kapsam-**dışı** soruya **red** | ✅ **pozitif** | **85** |
| kapsam-**dışı** soruya **CEVAP** | 🔴 **en ağır negatif** | **1** |
| kapsam-**içi** soruya **red** | 🔴 negatif | **339** (%2,3) |
| kapsam-**içi** soruya cevap | ✅ pozitif | **11.732** (%78,4) |

    gürültü (kapsam-dışı) paydası 86 → doğru red oranı **%98,8**
    netleştirme (bir red değil, bir SORU)                    2.755  (%18,4)

⊙ **Neden tek bir sayı yazılmıyor:** EHRSQL'in birleşik skoru bir **ceza katsayısı**
seçmeyi gerektirir (*«kapsam-içi bir red, kapsam-dışı bir cevaptan kaç kat hafiftir»*) ve
o katsayı bir **iş kararıdır**, bir ölçüm değil. Katsayıyı biz seçip tek bir sayı
yayımlasaydık, seçimimizi bir ölçüm gibi sunmuş olurduk.

⚠ Ve **netleştirme bir red değildir**: kullanıcıya bir soru sorulmuştur, cevap
kapanmamıştır. Onu redle aynı kefeye koymak, sistemin en dürüst davranışını bir
başarısızlık gibi saymak olurdu.

> *Bir güvenilirlik skoru, cezasının kim tarafından seçildiği yazılmadan bir ölçüm
> değil bir tercihtir.*

### Şirket kırılımı — ortalamanın arkasındaki dağılım

| şirket | sektör | doğru küp | semantik vaka | cevapsız | şişme |
|---|---|---|---|---|---|
| demo-boyahane | boyahane | **7.298 / 7.552** (%96) | 322/337 (%95) | 1.397/9.413 (%14,8) | 27,9× |
| atiksan | geri-dönüşüm | **931 / 949** (%98) | 66/68 (%97) | 413/1.447 (%28,5) | 21,3× |
| gulteks | kumaş ticareti | **995 / 1.040** (%95) | 78/83 (%93) | 479/1.618 (%29,6) | 19,5× |
| gitas | tarım ticareti | **1.517 / 1.696** (%89) | 92/103 (%89) | 657/2.479 (%26,5) | 24,1× |

🔴 **En düşük şirket de yazılıdır.** `gitas` %89 ve ortalamayı aşağı çekiyor; onu payda
dışına almak oranı yükseltirdi. Almadık — ve **almamak bu belgenin tek en önemli
cümlesidir**.

---

## 2 · Payda ne demek — ve neden İKİ payda birden yayınlıyoruz

Aynı ölçüm iki farklı paydayla iki farklı sayı verir ve **ikisi de doğrudur**:

* **Ham tur (14.957):** üretilen her soru bir tur. *«bu yıl ciro»* · *«geçen ay ciro»* ·
  *«2. çeyrek ciro»* → **üç** tur.
* **Semantik vaka (591):** dönem ve boyut çarpımı **tek** vakaya çöker; yukarıdaki üç tur
  **bir** vakadır. Şişme katsayısı **25,3×**.

⚠ **Şişme katsayısını gizlemek, payda oyununun kendisidir.** *«14.957 soruda %95»*
demek teknik olarak doğru ama **yanıltıcıdır** — çünkü o 14.957'nin çoğu birbirinin dönem
varyantıdır. Bu yüzden ikisi de burada.

### 🔴 Payda asla küçültülmez — ve bunun ölçülmüş bir sebebi var

Bir kez `gitas` bir derleme yarışı yüzünden korpustan **tamamen düştü**: payda `445 → 342`
indi ve doğruluk **%93,2 → %94,3'e ÇIKTI**. Sistem bozulurken sayı iyileşti. Aynı desen
ikinci kez ölçüldü: bir izin hatası üç şirketi düşürdü, toplam yine **%94,8** göründü —
çünkü **ayakta kalanlardan** hesaplanıyordu.

> *Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla da olur.*

Bu yüzden `CLAUDE.md`'de **seyreltme yasaktır** ve payda sabitliği bir kapıyla korunur.

---

## 3 · Yöntem

1. **Sorular katalogdan üretilir** — her küpün her ölçüsü ve boyutu için, dönem/kırılım
   varyantlarıyla. Elle seçilmiş bir "kolay küme" **yoktur**.
2. **Dört gerçek şirket kataloğu** üzerinde koşar (biri demo, üçü gerçek müşteri
   şemasından türetilmiş fikstür), **dört ayrı sektör**.
3. **LLM'siz ve kotasızdır** — `route()` deterministik yolunu ölçer. Günlük kota dolsa
   bile koşar, ve koşumlar arasında **değişmez**.
4. **Doğruluk ≠ erişim.** *«Bir yoldan SQL üretildi mi»* (erişim) ile *«doğru küpten mi
   geldi»* (doğruluk) **ayrı** sayılır ve ayrı yayımlanır.

---

## 4 · 🔴 BİLİNEN KÖRLÜKLER — sayının GÖRMEDİĞİ

Bunlar sayının kusurları değil, **kapsamının sınırlarıdır**; yazılı olmadan sayı
yanıltıcıdır.

| körlük | sonuç |
|---|---|
| **Sorular katalogdan üretiliyor** → hepsi **doğru yazılmış** | Yazım hatası yolu korpusta **hiç sorulmuyor**. %95 yeşilken gerçek kullanıcı deneyimi kırık olabilir — sayı yalan söylemiyor, **o yolu görmüyor** |
| Korpus `route()`'u ölçer | Discovery (ham SQL) yolundaki kusurları **görmez**; bir düzeltmenin meşru bir yolu kestiği ölçüldü ve korpus fark etmedi |
| *«Doğru küp»* ölçütü **üretim kaynağını** doğru sayar | Bir terimi iki küp de meşru olarak sahipleniyorsa, ilan edilmiş sahibe gitmek bu ölçütte *«yanlış»* görünebilir |
| Fikstürler gerçek müşteri **verisi** değil, gerçek müşteri **şeması** | Veri dağılımına bağlı kusurlar kapsam dışı |

Kullanıcı-deneyimi kusurları korpustan değil, **canlı turlardan** çıkar.

---

## 5 · Neden bunu yayınlıyoruz

İncelenen **13 üründen 10'u** doğruluk sayısı yayınlamıyor. Yayınlayan üçünün paydası ise
sorunlu: biri *«450+ soru»* diyor (gerçekte **30**), biri kaynaksız bir *«#1»* iddiası
taşıyor, biri **kendi verisinde** 95/100 ölçüyor. Bir başka satıcı **28 soruda** %84,5
yayınlıyor — o paydada güven aralığı **±13 puandır**.

⊙ Ölçülmüş bir sayıyı, paydası ve körlükleriyle birlikte yayınlamak taklit değil
**öncülüktür**.

> *Bir sayıyı savunmak için değil, sınanabilsin diye yayınlıyoruz. Payda gizlenirse sayı
> bir iddia bile değildir; körlük gizlenirse bir güvence hiç değildir.*

---

## 6 · Bu belge çürümez

Buradaki her sayı `backend/lab/reports/nl_corpus.json`'dan okunur ve
`backend/tests/test_f8_doğruluk_yayini.py` ikisini **karşılaştırır**. Ölçüm değişir de bu
belge güncellenmezse **kapı kırmızı** olur.

*Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan kötüdür — çünkü ona
güvenilir.*
