"""FAZ 0.21 — **MODÜL BÜYÜME KAPISI.** Borç büyümesini durdurur; küçültmeyi zorlamaz.

## Neden

`ask()` **tek fonksiyon** ve gövdesi **2.052 ham satır / 19 iç fonksiyon**. FAZ 0/2/5/6'nın
neredeyse her maddesi oraya dokunuyor ve depo **paylaşılan bir dizinde** — yani bu fonksiyon
aynı zamanda bir **çakışma jeneratörü**. Ve `K3`'ün kusuru tam bu boyuttan doğuyor: iki bin
satırlık bir gövdede bir çağrının **yanlış `if`in içinde** olduğu **görünmüyor**.

⚠ **Bilinçle *"şimdi refactor et"* DENMİYOR.** Büyük refactor'ün kazancı **ölçülmedi**;
kapı refactor'ü **zorlamadan** borcun büyümesini durdurur. Maliyeti **bir test dosyası**.

🔴 **Bu bir TAVAN, bir HEDEF değil.** Küçültmek serbesttir ve ayrı bir maddedir; bu dosya
yalnız *"buradan yukarı çıkma"* der.

## 🔴 BİRİM KARARI — ve onu belirleyen ölçüm

Kapı **ham satır saymaz, KOD satırı sayar** (yorum ve docstring hariç). Sebep tahmin değil,
ölçüm (`c3fcfe7` → `a41f981`):

| | ham satır | **kod satırı** |
|---|---|---|
| `ask.py` | 3991 → 4035 (**+44**) | 2394 → 2406 (**+12**) |
| `cube_router.py` | 3565 → 3592 (**+27**) | 1723 → 1736 (**+13**) |

Yani FAZ 0'ın `ask.py`'ye kattığı ham satırın **%73'ü belgelemedir**. Ham satır sayan bir
kapı, bu depoda **ölçülmüş kusurların kaydedildiği mekanizmayı** vergilendirirdi — ve
geliştiriciyi *"yorumu silersem kapı yeşile döner"* diye ödüllendirirdi. Bu belge kültürünü
kapıyla cezalandırmak, kapının korumaya çalıştığı bilgiyi yok etmek olurdu.
*(`cube_router.py` bugün **%52 belge**; ham sayıya bakan bir okuyucu modülü iki kat büyük sanır.)*

## Neden `ask()` FONKSİYONU, `ask.py` DOSYASI değil

Zarar dosyada değil **fonksiyonda**: 19 iç fonksiyon **aynı kapsamı paylaşıyor**. Kodu
`ask()`'ten çıkarıp aynı dosyada modül düzeyine almak **istenen** yöndür — dosya kapısı
onu **cezalandırırdı**. Yine de dosya bütünü **kod satırı** üzerinden sınırlı: yoksa
`ask()` küçülürken dosyanın geri kalanı sessizce şişerdi.

## FAZ 0 MUAFİYETLERİ — madde madde, gerekçeli

Tavan **FAZ 0 ÖNCESİ** ölçümden (`c3fcfe7`) alınır; FAZ 0'ın eklediği her satır **ayrı bir
muafiyet satırı** olarak yazılır. Bugünkü sayıyı doğrudan tavan yapmak, **şişmiş bir tavanı
kilitlemek** olurdu ve kapı hiç iş görmezdi (yol haritasının §A.5/4 ihlali).
"""

from __future__ import annotations

import ast
import pathlib

import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app"

# ── TAVAN: FAZ 0 ÖNCESİ ölçüm (@`c3fcfe7`) ───────────────────────────────────
TABAN_ASK_KOD = 1135          # ask() gövdesi, yorum/docstring hariç
TABAN_ASK_IC_FN = 19          # iç fonksiyon (closure) sayısı
#: 🔴 **1723 → 1703 (2026-08-05): TAVAN İNDİ, ve inmesi bir KURAL GEREĞİDİR.**
#:
#: `cube_query_json_schema` `app/intent_semasi.py`'ye taşındığında modül 1749'dan 1703'e
#: düştü ve tavanda **38 satır boşluk** kaldı. Meta-kapı (`test_TAVAN_KAPISI_GERCEKTEN
#: _KIRMIZI_VERIYOR`) bunu **kırmızı** verdi ve haklıydı: *boşluklu bir tavan büyümeyi
#: durdurmaz — bir kod satırı eklenir, kapı yine yeşil der.*
#:
#: ⚠ Taban **ölçülen değere** indirildi, muafiyetler **korundu**: muafiyetler geçmiş
#: kararların kaydıdır ve bir taşıma onları geçersiz kılmaz. *Bir tavanı indirmek bir
#: iyileşmedir; muafiyet listesini silmek bir hafıza kaybıdır.*
#: ⚠ **VE TABAN, MUAFİYETLERİN DÜŞÜLDÜĞÜ HÂLDİR — ilk düzeltmem yanlıştı.**
#: `TAVAN = TABAN + Σmuafiyet` olduğu için tabanı ölçülen değere (1703) koymak, tavanı
#: 1721'e çıkarıp **18 satır boşluk** bıraktı; meta-kapı yine kırmızı verdi. Muafiyetler
#: ölçülen değerin **İÇİNDE** zaten var — onları bir kez daha eklemek **çifte sayımdır**.
#: Doğru taban: `ölçülen (1703) − Σmuafiyet (18) = 1685`, ve tavan yine tam 1703.
#: *Bir formülü düzeltmeden bir sayıyı düzeltmek, sayıyı ikinci kez yanlış yapar.*
TABAN_CUBE_ROUTER_KOD = 1663  # 1739 ölçüldü − 75 muafiyet = taban; tavan tam 1739
#: 🔴 **1664 → 1663 (`§34`): SIRALAMA KURALI ÇIKTI, PAY İNDİ.**
#: *"Üstünlük istendi ve sıralama yok"* kuralı `app/siralama.py`'ye taşındı. Taşıma
#: dosyaya **net −1** kod satırı bıraktı (4 satırlık blok → 3 satırlık devir) ve
#: meta-kapı boşluğu anında kırmızı verdi: `assert not 1815 <= 1815`.
#: ⚠ Doğru tepki payı **yerinde bırakmak değil**: bırakılsaydı bir sonraki artış
#: sessizce kabul edilirdi. *Bir taşımadan artan boşluk, bir sonraki borcun peşin
#: ödenmiş faturasıdır — ve o fatura kimseye kesilmemelidir.*
#: 🔴 **1685 → 1664 (2026-08-07): TAVAN YİNE İNDİ — ve yine bir KURAL GEREĞİ.**
#: `build_catalog` `app/katalog_metni.py`'ye taşındı (LLM'in gördüğü METNİN sahibi
#: `cube_router` değil); dosya 1760'tan 1739'a düştü ve tavanda **21 satır boşluk**
#: kaldı. Meta-kapı (`test_TAVAN_KAPISI_GERCEKTEN_KAPI_MI`) bunu **kendisi yakaladı**:
#: boşluklu bir tavan, büyümeyi durdurmayan bir tavandır.
#: *Bir tavanı indirmemek, onu yükseltmenin sessiz biçimidir.*

#: `(sha, Δ, gerekçe)` — her satır **bir maddeye** aittir ve nedeni yazılıdır.
#: 🔴 Toplamları aşağıda **kapıyla** doğrulanır: kimse listeye bakmadan tavanı büyütemez.
MUAFIYET_ASK_KOD = [
    ("rd-takip-belge-once", 11,
     "🔴🔴 **`§RD-takip` — BELGE DÜZENLEME, FİŞ DÜZENLEMEDEN ÖNCE GELİR.** "
     "⊙ Ölçüldü (curl `CC` turu, CC-21/CC-22): ekranda **4 bölümlü** bir belge varken "
     "*«rapora fire oranını da ekle»* → `refine → deterministik düzenleme` → "
     "**`rapor=None`**; belge yok oldu, yerine tek bloklu bir saçılım grafiği geldi. "
     "⊙ Kök bir **öncelik ters çevrilmesidir**, eksik bir yetenek değil: `§RD-4`'ün "
     "*«düzenleyemezsen KORU»* koruması yalnız taze dalda yaşıyordu ve yapısal takip "
     "zinciri ondan önce koşuyordu — koruma **erişilemezdi**. "
     "⊙ İki hipotez ölçümle **çürütüldü**: *«bölüm» sözcüğü suçlu* (o sözcüksüz cümle de "
     "belgeyi yok etti) ve *ölçüm artefaktı* (`page.tsx:265` `cube_query` **ve** "
     "`previous_rapor`'u birlikte gönderiyor). "
     "⊙ Δ = 11: **gövdenin tamamı modülde** (`plan_tuketici.belge_takibi` — çağrı, "
     "`koru=False` kademesi, *yalnız belge üretirse kabul* kuralı, iz); burada kalan "
     "on bir satır bir **çağrı** ve bir `AskResponse` kurulumu. "
     "⚠ **TAŞINAMAZ:** bu bir **kontrol akışı önceliğidir** — hangi basamağın hangisinden "
     "önce geleceği tam olarak `ask()`in işidir, ve `AskResponse` onun yerelleriyle "
     "(`body`, `_finish`, `_attach_viz`) kurulur. "
     "*Elindeki belgeyi kaybederek verilen bir cevap, cevap değil bir zarardır.* "
     "`sha=0c42572`"),
    ("ka-tanimadan-cevap", 5,
     "🔴🔴 **`§KA` — HİÇBİR ŞEYİ TANIMADAN VERİLEN GÜVENLİ BİR CEVAP BİR UYDURMADIR.** "
     "⊙ Ölçüldü (curl `CC` turu, CC-15): *«asdfgh qwerty»* → `source=cube+llm`, **11 "
     "satırlık makine bazında OEE raporu**, not YOK, beyan YOK. `route()`in **kapsam "
     "kapısı** var (`partial_unknowns`), garson devraldığında o kapı hiç koşmuyor. "
     "⊙ Bir kapı değil bir **beyandır**: doktrin *«anlamadım bir son cevap olamaz»* diyor "
     "→ cevap **gider**, yanına varsayım olduğu yazılır. Reddetmek `§0.0`'ı, susmak "
     "`E-2`'yi çiğnerdi. "
     "⊙ Δ = 5: **yüklem ve metin modülde** (`uyum.tanimadan_cevap_notu` + "
     "`uyum.uydurma_beyani`); burada kalan beş satır bir **kapı** (`source == "
     "\"cube+llm\"`) ve bir çağrı. "
     "⚠ **TAŞINAMAZ:** `_finish` merdivenin **tek** çıkışıdır ve kapı `resolve_for`/`body`/"
     "`schema` yerellerini okur; niyeti tek bir dala bağlamak ölçülmek isteneni yarım görürdü. "
     "*Bir hakeme niyetini sormak başka, ne attığını sormamak başkadır.* "
     "`sha=0c42572`"),
    ("uy-yoy-beyan-kacagi", 4,
     "🔴 **`§UY-yoy` — ÖLÇÜ-DÜŞME BEYANI DÖNEMSEL KIYAS YOLUNDA ATLANIYORDU.** "
     "⊙ Ölçüldü (curl `CC` turu, CC-18/CC-19) — aynı kayıp, iki yol, tek beyan: "
     "*«bu yıl toplam ciro **ve** fire oranı»* → ✅ *«soruda 2 ölçü, cevapta 1»*; "
     "*«geçen yıla göre ciro **ve** fire oranı değişimi»* → 🔴 aynı kayıp, **NOT YOK**. "
     "`yoy` kendi `AskResponse`'unu kurup doğrudan mühre gidiyordu. "
     "⊙ Δ = 4: **gövde modülde** (`uyum.beyan_ekle` — tek gövde, iki çağıran); burada "
     "kalan dört satır bir çağrı ve `cube_meta` çözümü. "
     "⚠ `final_cq` geçilir (`compare` alanıyla): `base_cq` geçilseydi düzeltmenin kendisi "
     "kıyas yapan yolu *«kıyas istendi ama yok»* diye suçlardı. "
     "*Bir kuralı yazmak, onu her çağrı yerinde kurmak değildir; ve eksik kurulan yer, "
     "kuralın hiç olmadığı yerden daha tehlikelidir.* "
     "`sha=0c42572`"),
    ("mk-formul-insanca", 3,
     "🔴 **`§MK-formül` — MAKBUZ HAM SQL BASIYOR, OYSA `§KN` İNSANCA FORMÜLÜ BİLİYOR.** "
     "⊙ Ölçüldü (curl `CC` turu, CC-2): *«bu nasıl hesaplandı»* → `ort_oee` için üç iç "
     "içe `SUM`/`NULLIF` ve kaçamak bir cümle (*«toplam/ortalamasıdır»*). Aynı turda "
     "CC-11 aynı ölçü için *«= kullanılabilirlik × performans × kalite»* diyebiliyordu. "
     "⊙ SQL **gizlenmez** (makbuzun kendi kararı); insanca formül onun **önüne** konur. "
     "⊙ Δ = 3: **gövde modülde** (`kok_neden.makbuz_satiri`); burada kalan üç satır "
     "makbuz döngüsünün içinde bir çağrı ve bir `append`. "
     "*Bir sistemin bildiğini bir yerde söyleyip başka yerde susması, bilgi eksikliği "
     "değil bir tutarsızlıktır.* "
     "`sha=0c42572`"),
    ("nb-neden-sessiz-dusemez", 4,
     "🔴🔴 **`§NB` — BİR «NEDEN» SORUSU CEVAPSIZ KALABİLİR; BAŞKA BİR SORUYA DÖNÜŞEMEZ.** "
     "⊙ Canlıda ölçüldü: *«makine bazında duruş dakika»* → *«neden böyle»* → **66 satırlık "
     "tablo**, not YOK, iz *«LLM-destekli yapısal düzenleme»*. "
     "🔴 Kök tam da bu dosyanın **kendi yorumunun** uyardığı yerdeydi: konuşma dalı "
     "`deterministic_refine`'dan önce yakalanır *«aksi halde «neden»/«düşüş» gibi "
     "kelimeler onun sözlük eşleşmesine karışır»* — ama dal **hiçbir şey üretemeyince** "
     "`None` dönüyor ve tur tam o çarpışmaya düşüyordu: `makine_duruslari`'nda `neden` "
     "**bir boyut adıdır** (duruş nedeni) ve garson *«neden böyle»*yi *«nedene göre kır»* "
     "diye okudu. Sonuç kazara makul bir tabloydu — bu onu **daha da kötü** yapar: "
     "kullanıcı bir açıklama sordu, sessizce başka bir sorunun cevabını aldı ve bunu "
     "anlamasının hiçbir yolu yoktu. "
     "⊙ Δ = 4: **gövde modülde** (`kok_neden.aciklanamadi` — dürüst beyan + kataloğun "
     "kendi boyutlarından chip'ler); burada kalan dört satır bir çağrı ve bir "
     "`AskResponse`. "
     "⚠ **TAŞINAMAZ:** `AskResponse` `ask()`in yerelleriyle kurulur (`body`, `iz`, "
     "`prev_cq`) ve `kok_neden` 🍳 mutfaktır — sunum katmanını oraya sokmak sınırı silerdi. "
     "*Cevaplayamadığını söylemeyen bir sistem, cevapladığını sanmaya devam eder.* "
     f"`sha=2726612`"),
    ("kn-kesitsel-neden", 7,
     "🔴🔴 **`§KN` — KESİTSEL NEDEN: «akranlarına göre neden farklı».** Kullanıcının "
     "şartı: *«neden sorusu geldiğinde adeta insan zihnini simüle etmeliyiz… formülde "
     "paydaki değerler arttıkça değer büyür, payda arttıkça düşer… en dibe indim ve "
     "gördüm ki vardiya 1'de…»*. "
     "⊙ Gerçek katalogla ölçüldü: `ort_oee = kullanılabilirlik × performans × kalite` → "
     "RAM-3 farkının **%84,1**'i performanstan, ve RAM-3 içinde performans en çok "
     "**3. Vardiya**'da ayrışıyor (0,702 ↔ 0,76). "
     "⊙ Δ = 6: **gövdenin tamamı modülde** (`app/kok_neden.py` — cebir, tam tur, "
     "derinleşme, motor adaptörü); burada kalan altı satır bir **çağrı** ve bir "
     "`AskResponse` kurulumu. "
     "⚠ **TAŞINAMAZ:** `AskResponse` `ask()`in yerelleridir (`body`, `iz`, `prev_cq`) ve "
     "onu modüle taşımak, sunum katmanını mutfağa sokmak olurdu — `§KN` 🍳 MUTFAK "
     "sınıfındadır ve orada kalmalıdır. "
     "⚠ Ve konum bilinçli: `contribution`dan **ÖNCE**. O *«geçen döneme göre neden "
     "değişti»*i açıklar, `§KN` *«akranlarına göre neden farklı»*yı; ekranda bir kırılım "
     "varken sorulan soru ikincisidir. `§KN` susarsa yol bayt bayt bugünkü (`KURAL B`). "
     "*Sorulmayan soruyu cevaplamak, cevap vermemekten farklı bir kusurdur.* "
     "⚠ **Δ 6 → 7'yi bir KAPI ekletti:** `oneri` bayrağını modülün kendi içinde "
     "`followup.TUR_NE_YAPMALI`'dan okumak istemiştim; `test_MUTFAK_dil_ayristiramaz` "
     "kırmızı verdi — `kok_neden` 🍳 mutfaktır, `followup` 🗣 garsondur ve bir dil "
     "sınıfını mutfaktan okumak sınırı silmektir. Bayrak çağıranda hesaplanıyor "
     "(`_oner`) ve **iki yerde** kullanılıyor (reçete dalı da ona bağlandı). "
     "*Bir sınırı korumanın bedeli, sınırı kaldırmanın bedelinden her zaman küçüktür.* "
     f"`sha=50b930e`"),
    ("kv-varlik-sorusu", 2,
     "🔴🔴 **`§KV` — BİR VARLIĞI SAYMAK, ONUN BİR ÖLÇÜSÜNÜ HESAPLAMAK DEĞİLDİR.** "
     "Canlı `V` turunda **dört** vaka ölçüldü: *«kaç makinemiz var»* → 11 satır "
     "`makine × ort_oee` **ve uydurma bir 12 aylık dönem**; *«kaç müşterimiz var»* → "
     "🔴 **tek satır** `{M1001, hareket_sayisi: 23}` — yani *«kaç müşteri»* sorusuna "
     "**bir müşterinin hareket sayısı**. Kullanıcı bir sayım istedi, bir metrik aldı. "
     "⊙ Negatif kontrol ayrımı doğruluyor: *«kaç parti üretildi bu yıl»* → "
     "`parti_sayisi=7595` **doğru** (orada `parti` bir **ölçü** sinonimi). "
     "⊙ Δ = 2: **gövde modülde** (`app/sayim.py` — yüklem + fiş normalleştirme + beyan); "
     "burada kalan iki satır **yalnız çağrı**: (1) fiş dönem kapısından **önce** "
     "düzeltilmeli (varsayımı üreten odur), (2) daraltma **beyan edilmeli**. "
     "⚠ **TAŞINAMAZ:** birincisi `_period_gate`'ten önceki tek nokta, ikincisi `resp` "
     "kurulduktan sonraki tek nokta — ikisi de `ask()`in kendi akışında. "
     "⚠ Ve `fisi()` bilerek **her zaman tuple** döner: dallanma çağırana yazılsaydı iki "
     "satır daha ederdi. *Bir tavan, kodu modüle iterken imzayı da biçimlendirir.* "
     f"`sha=2eca01a`"),
    ("es2-esik-hunide", 2,
     "🔴🔴 **`§EŞ-2` — EŞİK KURALI YALNIZ BİR DALDA GEÇERLİYDİ.** Canlı: *«bu yıl fire "
     "oranı %20 üstü olan hatlar»* → 8 hattın **hepsi** döndü ve `uyum` dürüstçe *«eşiği "
     "filtreye çeviremedim»* dedi. Oysa ayrıştırıcı **kusursuz**: `_measure_threshold` "
     "beş ayrı yazımda da `{'op':'>','value':20.0}` üretiyor (ölçüldü). "
     "🔴 Kök: `niyet_tasima.esik` **yalnız dönem-netleştirme dalında** çağrılıyordu "
     "(`§40`'ın kendi vakası); normal cevap yolunda hiç koşmuyordu. Kural yazılmıştı ama "
     "**tek bir dalda** yaşıyordu. "
     "⊙ Bugünün üçüncü aynı-sınıf bulgusu (`§DK-2` route-yalnız · `§AA1` çağıranda yok · "
     "bu): *bir kural yalnız bir basamakta geçerliyse, o kural değil bir tesadüftür.* "
     "⊙ Δ = 2: **gövde zaten modülde** (`niyet_tasima.esik`); burada kalan çağrı ve izi. "
     "⚠ **TAŞINAMAZ:** huni, kuralın **her** yolda geçerli olduğu tek yerdir — taşımak "
     "onu yine tek bir dala hapsetmek olurdu. "
     f"`sha=c5e7b38`"),
    ("aa2-red-yaninda-rapor", 6,
     "🔴🔴 **`§AA2` — BİR TEKNİĞİN REDDİ, TURUN REDDİ OLAMAZ.** Canlı 7 turluk zincirde "
     "ölçüldü: altı tur kusursuz aktı (odak beyanlı, yoy hesaplandı, ciro eklendi) ve "
     "yedincisi — *«özetle ne yapmalıyız»* — **bomboş** döndü: `rows=0` · olgu yok · "
     "chip yok, yalnız *«katkı payı tanımsız»* notu. Cümle **doğruydu** (bir oranda "
     "katkı payı gerçekten tanımsızdır) ama kullanıcı katkı payı **istememişti**, özet "
     "istemişti — ve özet **elde vardı**. "
     "⊙ Δ = 6: **gövde taşındı** (`contribution.yanindaki_rapor`; ilkenin evi orası, "
     "çünkü aynı ders `§AA1`'de o dosyada yazılı: *«Bir sınırı aşmıyoruz, yanına doğru "
     "soruyu koyuyoruz»*). Burada kalan **indirgenemez** üç şey: çağrı · `result=` "
     "ataması · izin beyanı. "
     "⚠ **TAŞINAMAZ:** çağrı, katkının reddettiği **dalın kendisidir**; başka bir yerde "
     "*«red oldu mu»* bilinmez. Ve `result` yanıta burada iliştirilir — *bir cevabı "
     "üretmek, onu taşıyan alana koymakla tamamlanır.* "
     "*«Yapamam» bir cevap değildir; «şunu yapamam ama şunu biliyorum» bir cevaptır.* "
     f"`sha=858336a`"),
    ("dk2-suzgec-degeri-hunide", 13,
     "🔴🔴 **`§DK-2` — SÜZGEÇ DEĞERİ ÇAPASI.** Garson süzgecin **değerini de kendisi "
     "yazar** ve varlığını hiçbir şey sormuyordu: `makine eq \"Bakım\"` → **0 satır, "
     "beyan yok**. Bir uydurma sayı değil bir **uydurma yokluk** — ve sıfır bir cevap "
     "gibi göründüğü için daha sinsi. "
     "⊙ Δ = 13: **kararın kendisi taşındı** (`deger_capasi.huni_karari`); burada kalan "
     "yalnız bayrak kontrolü, notun birleştirilmesi ve netleştirme dönüşü. İlk hâli 30 "
     "satırdı, kapı *«modüle çıkar»* dedi ve çıkarıldı — 13'e inen kısım budur. "
     "⚠ **TAŞINAMAZ ve bu maddenin VARLIK SEBEBİ odur:** `route()` bu doğrulamayı "
     "`value_index` ile **zaten** yapıyordu, ama **yalnız route yolunda**; garsonun fişi "
     "oradan geçmiyor. Kuralın huniye konması, onu merdivenin **her** basamağında "
     "geçerli kılan şeydir. *Bir kural yalnız bir basamakta geçerliyse, o kural değil "
     "bir tesadüftür.* "
     f"`sha=72e7e3b`"),
    ("c3d-ters-yon-tasiyicisi-bosaltilir", 8,
     "🔴 **`C1`+`C3`+`C3-D` — TERS YÖN.** Kullanıcı kuralı: *«tek tek sinonim yazmak "
     "aptallık.»* Sistem sözlüğünü **kullanımdan** yazıyor: `bilinmeyen=zayiat` ∩ "
     "garsonun seçtiği ad → `zayiat → toplam_fire_kg`, **0 ek token**. "
     "⊙ Δ = 8: okuma da çıkarım da `app/ters_yon.py`'ye taşındı (141 satır); burada "
     "kalan yalnız **taşıyıcının boşaltılması** ve izin yazılması. "
     "⚠ **TAŞINAMAZ:** taşıyıcı `cq` üzerinde gelir ve huniye varınca boşaltılmalıdır — "
     "kalırsa `cube_query` cevaba sızar ve SQL derleyicisine bilinmeyen bir alan olarak "
     "gider (`KÖK-4`'ün aynı dersi). *Bir taşıyıcı alan, taşıdığı yere varınca "
     "boşaltılmalıdır.* "
     f"`sha=72e7e3b`"),
    ("b9-odak-varlik-hunide", 2,
     "🔴🔴 **`B9` — ODAK VARLIK.** ⊙ Kusur canlıda İKİ thread'de ölçüldü ve ikisinde de "
     "kök aynıydı: bir önceki tur bir varlığı **adıyla seçmişti**, bir sonraki tur ona "
     "*«o …»* / *«peki neden …»* diye atıfta bulundu, ama diyalog durumunda taşınacak "
     "bir **odak** yoktu. A/3 *«peki neden düşük»* → 11 makinenin hepsi (olmalıydı: "
     "RAM-3) · B/5 *«o ayda hangi makine»* → yılın tamamı, 66 satır (olmalıydı: tur "
     "4'ün ayı, 11 satır). Taze sorulduğunda sistem doğru çalışıyordu — kaybolan soru "
     "değil **referanstı**. "
     "⊙ Δ = 2: `odak_uygula(...)` çağrısı, iki satıra sarılmış. **Bu, tavanı yükselten "
     "değil, kapının kendi talimatını izleyen bir kalemdir**: kapı *«yeni davranışı "
     "modüle çıkar»* dedi ve karar da (`odak_suzgeci`), uygulama da (`odak_uygula`), "
     "en-iyi-çaba sarmalayıcısı da `app/diyalog.py`'ye taşındı — `ask()`te yalnız "
     "**çağrı** kaldı ve o indirilemez. İlk hâli 20 satırdı; 2'ye inen kısım budur. "
     "⚠ **TAŞINAMAZ:** çağrının yeri `_answer_from_cube_query` hunisidir, çünkü kusur "
     "üreticiden bağımsızdır (`§34`'ün birebir gerekçesi): route · Intent · takip · "
     "orkestratör — hepsi oraya çıkar. Bir üreticiye koymak, kalan üçünde referansı "
     "yine kaybettirirdi."),
    ("o19-cokluk-netlestirmeyi-erteler", 5,
     "🔴🔴 **`O-19` — AYRIK ÖLÇÜ KÜMELERİ BİR BELİRSİZLİK DEĞİL, BİR ÇOKLUKTUR.** "
     "⊙ Ölçüldü (canlı `IV` turu, iki soru): *«iade oranı en yüksek 3 müşteriyi **ve** "
     "ciro paylarını göster»* ve *«hangi vardiyada kalite sorunları yoğunlaşıyor»* → "
     "ikisi de `%50 uyum · eksen=measures` ile **cevapsız** kaldı. Oyların hikâyesi: "
     "biri **çekimser** (*«tek cube ile olmaz»* — haklı), ikisi **farklı** küplerden "
     "**farklı** ölçüler seçiyor. Üç oy da doğru: soru gerçekten **iki parçalı** ve "
     "doğru cevap bir **plandır**. "
     "⊙ Δ = 5: ilklendirme (1) · çokluk dalı (2: `if` + saklama) · plan cevap veremezse "
     "ertelenen chip (2: `if` + `return`). "
     "⚠ **TAŞINAMAZ:** karar `ask()`in **akış sırasıdır** — netleştirmeyi erteleyip "
     "planı denemek, sonra ertelenmişi konuşturmak. Dışarı almak, bir dalın *nerede* "
     "döndüğünü iki dosyaya bölerdi. Yüklemin kendisi (`uyum.cokluk_mu`) **taşındı** ve "
     "tavan yalnız akış satırlarını sayıyor. "
     "⚠ **`§101.1` disiplini yüklemde:** kesişen kümeler çokluk sayılmaz "
     "(`{ciro}` ↔ `{ciro, fire}` bir zenginlik farkıdır, iki istek değil) ve "
     "`eksen=cube` (aynı ölçü, iki sahip) **aynen sorar**. "
     "⚠ **KAYIPSIZ:** plan cevap veremezse **birebir aynı** chip konuşur — en kötü "
     "durum bugünküyle bayt bayt aynı. `sha=7fbf8a2`"),
    ("o14-garson-orkestrator-oldu", 1,
     "🔴🔴 **`O-14` — GARSON = ORKESTRATÖR.** Tek satır: `_g = sarmala(...)`. ⊙ Bu bir "
     "**basamak eklemesi değil**, garsonun **çıktı biçiminin** genişlemesi — karar yüzeyi "
     "(route↔garson, ~100 testin koruduğu sınır) **dokunulmadan** kalıyor. *Bir yeteneği "
     "bir basamak olarak eklemek karar yüzeyini büyütür; bir çıktı biçimi olarak eklemek "
     "büyütmez.* ⚠ Satır `_select_consistent`'ın **argümanı** olduğu için ayrı: üç "
     "satırlık bir çağrıya sıkıştırmak yerine adlandırıldı, çünkü `sarmala()` bayrak "
     "çözümünü de yapıyor ve o karar okunabilir kalmalı. 🔴 LLM çağrı sayısı DEĞİŞMİYOR: "
     "garson zaten yalnız `route_hit is None` dalında çağrılıyor — göç *ne zaman* "
     "çağrıldığını değil *ne döndürdüğünü* değiştiriyor."),
    ("f821-capraz-alan-pilotu-ic-fonksiyonu-cagiriyordu", 1,
     "🔴 **GİZLİ BİR `NameError` KAPATILDI.** `_capraz_alan_pilotu` modül düzeyindeydi ama "
     "`ask()`in **iç** fonksiyonu `_answer_from_cube_query`'yi çağırıyordu: pilot bir cevap "
     "ürettiği an `NameError`. `ruff F821` buldu (`ask.py:394`), `agent_plan_secimi` kapalı "
     "olduğu için bugüne kadar hiç koşmamıştı. ⊙ Çözüm iç fonksiyonu **parametre** yapmak: "
     "iki çağrı yerinden biri tek satıra sığmadı, bedel **bir** satır. Alternatif "
     "(`_answer_from_cube_query`i modül düzeyine taşımak) çok daha pahalıydı — o fonksiyon "
     "`ask()`in on kadar yerel değişkenini okuyor. *Bir çağrının nereden geldiğini "
     "parametreyle söylemek, çağrılanı taşımaktan ucuzdur.*"),
    ("o4-merdivenin-boslugu-tek-kapidan", 7,
     "🔴 **`FAZ O-4` — MERDİVENİN BOŞLUĞU (`E3`).** Yedi satır: `_garson` başlangıcı (1), "
     "`_plan_tuketici.cevap(...)` çağrısı (2), `if` + `AskResponse` dönüşü (4). ⊙ Neden "
     "burada: bu dal **yalnız** `route_hit=None` iken, yani bugünkü sonucun Discovery ya "
     "da dürüst ret olduğu noktada çalışır — konumun kendisi `E3`'ün şartıdır ve konum "
     "`ask()`in akışında tanımlıdır, dışarı taşınamaz. ⊙ Karar, metin, hata sınıflaması "
     "ve `KURAL B` çözümü **hiç burada değil**: `plan_tuketici.cevap()` sarmalanmamış bir "
     "garsonda `None` döner, `ask()` onu bilmez bile. ⚠ `index`/`cube_meta` bilerek "
     "GEÇİRİLMEDİ: `ask()`in o noktasında ikisi de garantili tanımlı değil ve *«belki "
     "tanımlıdır»* diye bir değişken okumak, bir `NameError`'ı üretim kusuruna çevirmenin "
     "en kısa yoludur — `schema` geçilir, türetme tüketicide yapılır."),
    ("t1-etiketleri-ayni-adaylar-belirsizlik-degildir", 6,
     "🔴🔴 **SİSTEM CEVABI HESAPLIYOR, CHIP OLARAK GÖSTERİYOR VE «ANLAMADIM» DİYORDU.** "
     "Ölçüldü (T turu, **beş** kanıt — `t1`·`t11`·`t13`·`t16`·`t18`): "
     "`not = «Hangisini istiyorsun?»` ve yanında **TEK** bir chip: "
     "`[\"İSG / iş kazası · kaza adedi · vardiya\"]`. "
     "⊙ Sebep: oy `_canon_cq` ile **tam `cq`** üzerinde sayılıyor; iki oy önemsiz bir "
     "alanda ayrılınca (biri `order` yazmış, öteki yazmamış) uyum %50'ye düşüyor ve "
     "kazanan ilan edilmiyor — oysa **kullanıcının sorduğu şey** (küp · ölçü · kırılım) "
     "ikisinde de **birebir aynı**. "
     "🔴 `§0.0`: *kullanıcı asla cevapsız kalmaz.* Sorulacak bir şey yoksa soru sorulmaz. "
     "⚠ Bu bir **çoğunluk kuralı DEĞİLDİR** (`§77`'nin reddedilen yolu): oylar arasında "
     "tercih yapılmıyor, adayların **anlamca aynı** olduğu chip listesinin kendisiyle "
     "**gösteriliyor**. Gerçek belirsizlikte (`t13`: `elektrik` vs `tep` → iki chip) dal "
     "aynen sorar. *Bir soruyu sormak için önce iki farklı cevabın olması gerekir.*"),
    ("m4-capa-yoksa-beyanli-varsayim", 3,
     "🔴 **`M-4` — SORMAK TEK SEÇENEK DEĞİL.** Korpusun **%13,7'si** `CLARIFY:dönem`; "
     "canlı turlarda **on** kez ölçü·kırılım·sıralama çözülmüşken tek eksik dönem "
     "yüzünden cevap **tutuldu**. Bu üç satır, çapa taşınamadığında **beyanlı bir "
     "varsayım** dener; gövde `donem_capasi.varsayilan_yerinde`'de (router'da yalnız "
     "ÇAĞRI kalır — *taşınabilir olan her şey modüle gider*). "
     "⚠ Bayrak kapalıyken hiç koşmaz (`KURAL B`) ve netleştirme **aynen** durur: "
     "kaldırılmadı, **ikinci seçenek** oldu. "
     "⚠ Varsayım kataloğa değil **veriye** bağlı — raporun `varsayilan_donem:` menü "
     "alanı `M-2`/`M-9` ile aynı duvara çarpıyordu (MDL küp alanları sabit)."),
    ("m9a-kapsam-disi-bir-supheDIR-garsona-devret", 5,
     "🔴🔴 **ŞÜPHE, DEVİR KARARINDAN SONRA KEŞFEDİLİYORDU.** `route_supheli` yalnız "
     "`cq`'nun eksikliğine bakar (dönem yok · sıralama yok); üçüncü bir şüphe türü ise "
     "**soruda** yaşıyor: *route cümlenin bir parçasını hiç kapsamadı.* "
     "Ölçüldü (iki koşum birebir, `KURAL G-1`): `bu yıl aylık **kümülatif** fire` → route "
     "eksiksiz görünen bir `cq` üretti (dönem + ay kovası) → **şüphe yok** → garson "
     "çağrılmadı → tur *«\"kumulatif\" kısmını anlayamadım»* ile öldü (**LLM'siz**). "
     "İkizi: `her hattın **payı**` → *«\"payi\" başka bir konu gibi görünüyor»*. "
     "⊙ `§0.0`'ın devir tetikleyicileri listesi bu dalı **adıyla** sayıyor: *«anlayamadım» "
     "üretecek her dal*. Bir red cümlesi, hakeme sorulmadan yazılamaz. "
     "⚠ Bedeli bu turda somut: mutfak kümülatifi **yapabiliyor** (`M-9`), fiş alanı "
     "**taşıyor**, garsonun istemi onu **biliyor** — tur `kumulatif` kelimesinde ölüyordu. "
     "*Bir yeteneği üç katmanda kurup dördüncüde kapıda bırakmak, onu hiç kurmamaktır.* "
     "⚠ Maliyet sınırlı: tarama zaten aşağıda koşuyordu, yukarı alınıp **yeniden "
     "kullanıldı** (ikinci koşum kaldırıldı); şüphe yoksa davranış birebir bugünkü."),
    ("p1-adhoc-capa-degildir", 1,
     "🔴🔴 **DISCOVERY CEVABI THREAD'İ ÖLDÜRÜYORDU — 3/3 takip turu.** Ölçüldü (P turu, "
     "`T-P2`): `personel çalışma süreleri ve verimliliklerini kıyasla` Discovery'ye düştü "
     "ve **iyi bir cevap verdi** (29 satır, `cube:\"adhoc\"`); sonraki **üç** turun üçü de "
     "*«Önceki rapor artık çalıştırılamadı (şema değişmiş olabilir)»* aldı. "
     "⊙ Sebep: `adhoc` şemada bir küp **değildir**, bu yüzden Gitaş 500'ü için yazılmış "
     "*bayat cube_query* koruması **her** Discovery takibinde ateşliyordu — ve cümle bir "
     "**yalandı**, şema değişmemişti. `adhoc` bayat bir `cq` değil, yeniden "
     "çalıştırılabilir **yapısı olmayan** bir cevaptır. Tek satır: çapa `adhoc` ise "
     "yapısal takip sayılmaz, tur **taze**dir ve garson devreye girer (`§0.0`). "
     "*Bir cevabın üstüne devam edilemiyorsa sebebi söylenir; sebebi uydurulmaz.*"),
    ("n2-garsonun-karari-karsilastirmali-tartilir", 2,
     "🔴🔴 **HAKEM KONUŞTU, KARARI DUYULMADI — `§0.0`'ın en pahalı ihlali.** Canlı log "
     "zinciri, tek istek (`bakım süresi en uzun makine`): `route ŞÜPHELİ → garson "
     "çağrılıyor (§51)` → `intent: 3 oy · 1 farklı aday · kazanan 2 oy` → kullanıcıya "
     "giden cümle *«Hangisini istiyorsun?»*. Garson **oybirliğiyle geçerli** bir cevap "
     "üretti ve o cevap eleme süzgecinde çöpe gitti. "
     "⊙ Sebep: süzgeç *«garsonun cevabı DAHA İYİ mi»* diye sorması gerekirken "
     "*«KUSURSUZ mu»* diye soruyordu — soruda hiç dönem yoksa cevap her zaman *«hayır»*. "
     "Yani **dönemsiz her soruda** garsonun kararı otomatik olarak elenıyordu. "
     "⚠ Ve bedeli yalnız sessizlik değil: aynı süzgeç route'un **uydurduğu** filtreyi de "
     "hayatta bırakıyor (`en verimsiz hattı bul ve nedenini **açıkla**` → "
     "`filters:[{hat eq \"Açık\"}]`) — `§51`'in kendi kanıt tablosundaki 2. satır, hâlâ. "
     "İki satır: eksiklik kümelerini al, altküme ise garsonu kabul et. Ölçüt "
     "`app/niyet_tasima.eksiklik`'te **tek sahiptedir** ve `route_supheli` onu okur."),
    ("faz-56-garson-konustuysa", 6,
     "🔴🔴 **EN ÜST KURALIN (`§0.0`) YAPISAL HÂLİ — ve `§54`'ün kelime listesini "
     "GEREKSİZ KILAN madde.** Çapraz-konu reddi *«X başka bir konu gibi görünüyor»* der "
     "ve `X`'i kapsam kapısının bilinmeyen listesinden alır; o liste **Türkçe bir "
     "sözlüğe** dayanır. Soru İngilizce/Arapça olduğunda her sözcük bilinmeyen görünür ve "
     "**cevaplanabilir** bir soru reddedilir (E turu, dört kanıt). "
     "⊙ Garson bir aday ürettiyse o cümlenin **konusu vardır**, yalnız dili farklıdır — "
     "Türkçe sözlüğe dayanan bir reddin orada söz hakkı yoktur. "
     "⊙ Δ = 6: bayrak tanımı (1) + garson dalında işaretleme (1) + `if/log/atama` (3) + "
     "`else` (1). "
     "⚠ **TAŞINAMAZ:** bayrak `_try_fresh_intent`'in **yerel akış durumudur** — garsonun "
     "o turda konuşup konuşmadığı bilgisi başka hiçbir yerde yok. "
     "⚠ Kapsam dar: garson hiç konuşmadıysa dal aynen çalışır (`KURAL B`). "
     "*Bir cümleyi tanımayan sözlük, o cümle hakkında hüküm veremez.*"),
    ("faz-55-discovery-butcesi", 9,
     "🔴 **EN GÜVENMEDİĞİMİZ BASAMAK EN UZUN BEKLETİYORDU.** `§33` iki bütçe onardı "
     "(Intent oyları · T2 anlatısı) ama Discovery açıkta kaldı. Ölçüldü (E turu): "
     "`stok devir hızımız ne` → **63.526 ms**, `enerji maliyetimiz` → **49.311 ms**; "
     "ikisi de `cube=adhoc`, yani `§0.0`'a göre birer **mutfak eksiği raporu** — ve "
     "kullanıcı o raporu bir dakikaya yakın bekliyordu. "
     "⊙ Δ = 9: bütçe okuma (2) + `butce.kos` çağrısı (3) + aşım dalı (4: `if` + üç "
     "satırlık dürüst ret) + `wren_sql` ataması (1) − eski tek satır. "
     "⚠ **TAŞINAMAZ:** aşım dalı `_honest_refusal`'a döner ve o `ask()`'in kendi "
     "kapanış sözleşmesidir; bütçenin KENDİSİ zaten `app/butce.py`'de (tek sahip). "
     "*En güvenmediğimiz basamağın en uzun bütçeye sahip olması, bir sıralama hatasıdır.*"),
    ("faz-54-islev-kapisi", 4,
     "🔴 **İŞLEV SÖZCÜKLERİ BİR KONU DEĞİLDİR — süzgeç YALNIZ GÖSTERİMDEYDİ.** Ölçüldü "
     "(E turu, dört kanıt): *«birlikte» başka bir konu gibi görünüyor* · *«bakim maliyeti "
     "iliskili» başka bir konu* · *«which had the highest last month» başka bir konu*. "
     "Süzgeç vardı ama yalnız cümleyi güzelleştiriyordu; dalın ATEŞLENMESİNİ "
     "engellemiyordu — sistem anlamadığını gizliyor, yine de reddediyordu. "
     "⊙ Δ = 4: `if not _gosterilecek` (1) + iz kaydı (1) + `other_topic=False` (1) + "
     "`unknown=[]` (1). "
     "⚠ **TAŞINAMAZ:** üçü de bu dalın **yerel durumudur** (`other_topic` ve `unknown` "
     "aşağıdaki iki cümleyi seçer); bir modüle taşımak, dalın kararını dalın dışına "
     "çıkarmak olurdu. "
     "*Bir cümleyi reddetmek için, reddedilen şeyin adı olmalıdır.*"),
    ("faz-51-supheli-devir", 5,
     "🔴🔴 **EN ÜST KURALIN (`§0.0`) UYGULAMASI — şüphe garsonu çağırır.** Koşul "
     "`route_hit is None` idi: route **herhangi bir şey** bulduysa, o şey ne kadar eksik "
     "olursa olsun garson hiç devreye girmiyordu. Ölçüldü: `top 5 customers by profit "
     "this quarter` → route ölçü+boyut buldu, `top 5` ve `this quarter` düştü, kullanıcı "
     "*«hangi dönem için?»* gördü — garsona **sorulmadan**. `en çok duruş yaşayan hattı "
     "bul ve nedenini **açıkla**` → route **uydurma** bir değer filtresi üretti "
     "(`neden = \"Açık\"`) ve o sahte kesinlik garsonu engelledi. "
     "⊙ Kural: *«aşçı KESİNLİKLE duyduysa hemen yapar; en ufak anlamama varsa garson "
     "gider.»* Yarım duymak bir duyma değildir. "
     "⚠ **TAŞINAMAZ:** yüklem (`route_supheli`) **modülde** — burada kalan yalnız çağrı "
     "(1), iz kaydı (2: `if` + `log`) ve devirden dönen sonucu **yalnız daha iyiyse** "
     "kabul eden iki satır. Sonuncusu zorunlu: bir devir, elde olanı KÖTÜLEŞTİRMEMELİDİR. "
     "Δ = 1 (şüphe) + 2 (iz) + 2 (daha-iyi süzgeci)"),
    ("gosterim-suzgeci/2", 2,
     "🔴 **İKİ SORU, İKİ LİSTE.** Curl'de ölçüldü: *«bu yıl hangi müşteri en çok iade etti»* → ***«hangi etti» kısmını anlayamadım***. Kullanıcı ne yaptığını anlamaz: `hangi` bir soru sözcüğü, `etti` bir yardımcı fiil — ikisi de **sorusunun konusu değil**. ⊙ `unknown` **kapsam kapısının** listesidir (*kaç kelimeyi açıklayamadım*); gösterim başka bir sorunun cevabıdır (*neyi anlamadım*). 🔴 Kapı onları **saymak zorunda**: dolgu sınıfına eklemek denendi ve `sessiz_yanlis` **12 → 13** çıktı (`§26.1`). Yani **sayılmalı ama gösterilmemeli**. ⚠ **TAŞINAMAZ:** süzgeç `unknown` ile `note`'un **ikisinin birden** elde olduğu tek yer; yardımcı (`_islev_sozcugu`) zaten modül düzeyine çıkarıldı. *Aynı kelime bir kapıda kanıt, bir cümlede gürültü olabilir.*"),
    ("kok-cozum/capa-degerleri", 7,
     "🔴 **KÖK ÇÖZÜM — kelime listesi SİLİNDİ.** Önceki sürüm `_KARSILASTIRMA` listesi + 4-kelime eşiği taşıyordu; çalışıyordu ama **tikel**di (*«yıkama neden geride kaldı»* · *«3. vardiya neden zayıf»* yine düşerdi, her biri listeye bir kelime daha eklettirirdi — `ADR-0008`). Yerine **yapısal bağ**: takip sorusu ekrandaki raporun bir **satırını** adlandırıyorsa bağlıdır. ⊙ Bu ayrım *«…olur genel olarak»* sorusunu **kendiliğinden** dışarıda bırakır — eşiğe gerek kalmaz. ⚠ **TAŞINAMAZ:** hesap **zaten taşındı** (`app/context.py::capa_degerleri` — *«ekranda ne var»* bağlam katmanının sorusu, sınıflandırıcının değil). Burada kalan yalnız çağrı ve `try/except`: `body.cube_query` ile `body.previous_result`'ın **ikisinin birden** elde olduğu tek yer. *Bir kusuru gördüğü yerde yamamak, sınıfını görmemenin en pahalı biçimidir: her yeni örnek yeni bir yama ister ve yamalar birbirini tanımaz.*"),
    ("sinir-llm-oncesi/5", 5,
     "🔴🔴 **KUSUR BENİMDİ ve canlı curl ÖLÇTÜ.** `§AJ3` ile modeli yorumlamaya **istekli** hâle getirdim (dönem alanı · karşı ağırlık · örnekler). Yan etki: *«gelecek ay ciro tahmini»* `cube+llm` ile **30 satır GEÇMİŞ veri** döndü — not yok, sınır yok, **sessiz-yanlış**. Yani modeli konuşkan yapmak, sınır kapısını **daha erken** gerektirdi. ⚠ Kapsam dar: `kapsam_disi` **beyan edilmiş** sınıfları tanır (tahmin · yargı · iki-cube · olumsuzluk), tahmin yürütmez; `None` dönerse merdiven aynen devam eder — bu bir **kesme** değil bir **öncelik**. ⚠ **TAŞINAMAZ:** karar `route_hit is None` ile Intent dalının **arasında** durmak zorunda. *Bir basamağı daha yetenekli yapmak, ondan önceki sınırı daha erken sormayı gerektirir — yoksa yeni yetenek, ilk olarak yapamadığımız şeyi yapmayı dener.*"),
    ("sinir-kismi-anlama/4", 4,
     "🔴 **CANLI CURL TURU 2: *«anlamadım»* ile *«yapamıyorum»* aynı cevabı hak etmez.** Ölçüldü: *«gelecek ay ciro tahmini»* → *«gelecek tahmini kısmını anlayamadım»*. Dürüst ama **yanlış cümle**: sistem o kelimeleri anlıyor, **yapamadığı** onların istediği şey. ⚠ *«Anlamadım»* kullanıcıyı **yeniden yazmaya** çağırır, *«yapamıyorum»* sınırı söyler; yanlışını seçmek kullanıcıyı **sonuçsuz bir döngüye** sokar. ⚠ **TAŞINAMAZ:** kontrol bu dalın **girişinde** durmak zorunda — chip/etiket üretimi başladıktan sonra sorulursa sınır beyanı o chip'lerin altında kalır. Sözleşme (`_guvenli_kapsam_disi`) zaten **tek** yerde; burada kalan yalnız çağrı. *Anlaşılmayan bir kelime ile yapılamayan bir istek aynı cevabı hak etmez.*"),
    ("sinir-once/3", 3,
     "🔴 **CANLI CURL BULGUSU: sınır GEÇ konuştu, yani hiç konuşmadı.** *«gelecek ay ciro tahmini»* → *«toplam ciro çıkarabilirim — hangi dönem için?»*. Kullanıcı **gelecek** sordu, sistem **geçmiş** için dönem soruyor; bir dönem söylerse sistem **yapamadığı şeyi yapmış gibi** sayı döner. ⊙ Sınır **vardı** (`kapsam_disi` → `forecast`), kapısı bu daldan çok sonra duruyordu. ⚠ **TAŞINAMAZ:** kapı yukarı **taşınmadı** — yalnız dönem netleştirmesi ona soruyor. Taşımak `route()`/Intent-JSON'un cevapladığı soruları da sınır beyanına çevirebilirdi ve o takas **ölçülmedi**. *Bir sırayı düzeltmek, sırayı baştan yazmak değildir.* *Bir sınırı bilmek, onu doğru anda söylemekten farklıdır; geç söylenen sınır, söylenmemiş sınırdır.*"),
    ("sosyal/baglam-kapisi", 2,
     "🔴 **CANLI CURL BULGUSU: kök-neden sorusu VEDA sanıldı.** *«peki bu neden düşük»* → "
     "*«Görüşürüz! İstediğin zaman buradayım.»* — 371 ms, 0 LLM, kendinden emin: en ucuz, "
     "en hızlı, en yanlış cevap. "
     "⊙ Kontrollü karşılaştırma tetikleyiciyi izole etti (*«peki bu ay ciro»* DOĞRU "
     "çalışıyor): kusur `peki`'nin sözlükte olmasında değil, **veri sinyalinin tanımında**. "
     "Bir takip sorusu (`bu`·`neden`·`düşük`) katalog terimi **taşımaz** — onu önceki tur "
     "taşır ve o tur istekte **elde durur**. "
     "⚠ **TAŞINAMAZ:** kapı iki kanatlı ve karar `body` ile `q_norm`'un **ikisinin birden** "
     "elde olduğu tek yerde; bir modüle çıkarmak istek nesnesini o modüle taşımak olurdu. "
     "🔴 İki kanat **ayrı** tutuldu: *tam kaplama* bağlamdan bağımsız kazanmaya devam eder "
     "(thread ortasındaki *«teşekkürler»* hâlâ sosyaldir); bağlama bağlanan yalnız **zayıf** "
     "kanat — yanılabildiği yer orasıydı. "
     "*Bir cümlenin veri sorusu olup olmadığı yalnız kendi kelimelerinden okunamaz; bağlamı "
     "elde tutan bir sistem için bu bilgi zaten mevcuttur.*"),
    ("VQR/eksik-niyet-ogrenmez", 4,
     "🔴 **EKSİK NİYETLİ CEVAP «DOĞRULANMIŞ» SAYILAMAZ.** Canlı denetim: *«şubatta ciro "
     "ocağa göre nasıl değişti»* → `source=vqr`, 434 ms, `eksik_niyet=['kiyas','trend']` — "
     "**beyanlı kısmi** bir cevap doğrulanmış soru deposuna girmişti. "
     "⚠ Zararı **bileşik**: VQR merdivenin **İLK** basamağı; deterministik yol iyileşse "
     "bile (bu turda `Ö10` tam o soruyu düzeltti) kayıt onu **es geçtirir** — depo, "
     "düzelttiğimiz kusuru **dondurup korur**. "
     "⚠ **TAŞINAMAZ:** karar `learn` bayrağının ve `resp`in **ikisinin birden** elde olduğu "
     "tek yer, ve `vqr.store` çağrısının **hemen üstünde** durmak zorunda — araya giren bir "
     "dal kaydı yine yazdırırdı. "
     "⊙ `app/vqr.py`'nin kendi şerhi bunu zaten biliyordu (*«dondurulmuş kayıt İYİLEŞMEZ, "
     "router İYİLEŞİR»*) ama kuralı yalnız **okumaya** uyguluyordu. "
     "*Bir öğrenme deposu, öğrendiği şeyin eksik olduğunu bilmiyorsa öğrenmez — ezberler.*"),
    ("AJ3.3/donem-ifadesi", 2,
     "🔴 **İFADE BOŞLUĞU — model dönemi hiçbir yere KOYAMIYORDU.** Prompt *«tarih yazma (sistem hesaplar)»* diyordu ve dönemi yazacak bir **alan yoktu**; tutarlı tek davranışı dönemi düşürmek ya da tüm soruyu reddetmekti (canlı: **9/9 `{cube:null}`**). ⚠ **TAŞINAMAZ:** çözüm `_resolve_period`'ün işi ve o **zaten var** (takip yolu); burada kalan yalnız **çağrı** ve alanın sorgudan çıkarılması. İkinci bir çözücü yazmak, aynı ifadenin iki farklı tarihe çözülmesi demekti. 🔴 Tasarım **icat edilmedi**, takip yolundan alındı (`period_expr`) — orada ölçülmüş ve çalışıyor."),
    ("katalog-sozlugu/tek-cozum", 2,
     "🔴 `catalog_text` **dört** çağrı yerinde üretiliyor (planlayıcı · `llm.select_cube` · "
     "Intent-JSON · `refine_cube`) ve dördü de `katalog_metni.metin_ve_indeks`'ten geçiyor. "
     "Δ yalnız iki satır sarmadan geliyor (satır uzunluğu sınırı). "
     "⚠ **TAŞINAMAZ:** bayrak çözümü **zaten taşındı** — bu dosyada kalan yalnız çağrı. "
     "*Bir bayrağı N yerde okumak, N−1 yerde okumaya giden yoldur*; dördünü tek yardımcıya "
     "bağlamak o yolu kapatır."),
    ("G0b.6/varlik-perdesi", 4,
     "🔴 **HAVA BOŞLUĞU: gerçek değer sağlayıcıya HAM gitmez.** Mekanizmanın tamamı "
     "`app/varlik.py`'de (perdele + fail-closed geri koyma); burada kalan **yalnız üç "
     "satır**: bayrak, çağrı, geri koyma. ⚠ **TAŞINAMAZ:** perdelenecek metin "
     "(`body.question`), süzgeç bağlamı (`schema`) ve geri konacak sonuç (`parsed`) "
     "**yalnız burada** bir aradadır — bir modüle çıkarmak, LLM çağrısını da o modüle "
     "taşımak olurdu. 🔴 Ve `parsed = varlik.geri_koy(...)` çağrının **hemen altında** "
     "durmak zorunda: araya giren tek bir satır, yuvaları çözülmemiş bir sorguyu "
     "tüketiciye açardı. *Yanlış bir boşluk, görünür bir hatadan beterdir.*"),
    ("G6.5/harman-bayragi", 2,
     "🔴 Intent-JSON şeması `harman=` ile üretiliyor — `blend`'in kill-switch'i (`KURAL B`). "
     "⚠ **TAŞINAMAZ:** şema **zaten burada** üretiliyor ve bayrak **zaten burada** "
     "çözülüyor (`llm_sema_kisitli` aynı satırda); ikinci bir `resolve_for` çağrısı aynı "
     "soruyu iki kez sormak olurdu. 🔴 `harman` varsayılanı **kapalı**: kapalı bir "
     "kill-switch'in yanından geçen tek çağrı, kill-switch'i iptal eder."),
    ("G2.9/yuksek-duzey", 3,
     "🔴 `yuksek` düzeyinde **boyut** adaylarını da ekleyen üç satır. `G2.9` planda "
     "vardı ve **hiç uygulanmamıştı**; kodun kendi itirafı (*«kapı yalnız `kapali`'yı "
     "uygular»*) yerinde duruyordu. "
     "⚠ **TAŞINAMAZ:** karar noktası burasıdır — `request`'ten düzeyi çözen "
     "`_netlestirme_duzeyi` ile aday listesinin **ikisinin birden** elde olduğu tek yer. "
     "Bir modüle çıkarmak, isteğe bağlı bir ayarı okumak için istek nesnesini bir modüle "
     "taşımak olurdu. "
     "🔴 `normal`'da davranış **birebir bugünkü** (`KURAL B`) — modülün kendi uyarısı "
     "`yuksek` için *«kapsam düşer, sessiz-yanlış da»* diyor; bu bir **takas** ve takası "
     "seçen **kiracıdır**. *Bir kapsam kaybını varsayılan yapmak, kullanıcı adına karar "
     "vermektir.*"),
    ("B5/sema-israfi", 1,
     "🔴 **ŞEMA ÜRETİLİP ATILIYORDU.** `llm_sema_kisitli: beta` açık ve `ask()` her "
     "istekte `cube_query_json_schema` çağırıyordu; ama aktif sağlayıcı "
     "(`openrouter` → `OpenAICompatibleSqlGenerator`) `sema` argümanını **hiç okumuyor** — "
     "kendi docstring'i söylüyor: *«BU SAĞLAYICIDA KULLANILMAZ»* (`oneOf` desteklenmiyor). "
     "⊙ Ölçüldü: 23 cube'luk demoda ~**10.000 token**lık bir yapı kuruluyor ve atılıyor. "
     "⚠ **TAŞINAMAZ:** eklenen tek satır bir `and` koşuludur ve `_sema = None` ile bayrak "
     "kontrolü **arasında** durmak zorunda — `test_BAYRAK_KAPALIYKEN_sema_URETILMIYOR` iki "
     "ifade arasındaki mesafeyi ölçüyor. Bir modüle çıkarmak bu yakınlığı kırar, yani "
     "kill-switch'in yarım olmadığını **okuyarak görme** imkânını yok eder. "
     "🔴 Karar `isinstance` ile verilmiyor: sağlayıcı yeteneğini **kendisi** beyan ediyor "
     "(`llm.py::sema_kullanir`), çağıran sorar; bilinmeyen sağlayıcıda varsayılan **True** "
     "(fail-open, davranış birebir aynı). *Bir yeteneği dışarıdan tahmin etmek, onu iki "
     "yerde tanımlamaktır.*"),
    ("garson/DA-5+DA-10", 9,
     "🔴 İKİ DENETİM BULGUSU, ikisi de `ask()` gövdesinde ve ikisi de TAŞINAMAZ. "
     "**(a) `DA-5` — `G2`'nin kill-switch'i (`diyalog_bellegi`).** Katman inmişti, bayrağı "
     "YOKTU: GERİ AL sözleşmesi (*«off → davranış birebir bugünkü»*) uygulanamaz "
     "durumdaydı. `MIMARI §9.11`: *bir kill-switch yalnız KODDA varsa yarımdır.* Kesme "
     "noktası **girişte** ve TEK: durum sunucuya hiç girmezse `devam_edilebilir(None)` "
     "zaten `None` döner. Bir modüle çıkarmak, bir `if`'i bir dolaylamaya çevirirdi. "
     "**(b) `DA-10` — dönem netleştirmesi katalogdan okuyor.** `soz.py:19`'un kendi kuralı "
     "(*«ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR»*) katalogda yazılıydı ama üretimde "
     "`_PERIOD_TEXT` sabiti basılıyordu; katalog girdisinin **hiç çağıranı yoktu**. "
     "⊙ Ağırlığı ölçülü: netleştirmelerin **%79'u** dönem sorusudur (`donem_capasi.py:8`). "
     "`{ne}` yuvasını `temellendirme` doldurur — ikinci bir adlandırıcı yazmak `KAT-1` "
     "olurdu; yani satırlar burada, **karar noktasında** kalmak zorunda."),
    ("9a138a9", 11, "0.5 · çapa zinciri — `coz(..., capalar=…)` bağlandı; "
                    "bayrak `capa_zinciri`, varsayılan `off`"),
    ("98a5071", 1, "0.12/0.13/0.6 · gerçek kill-switch + kanıt geçmişi"),
    ("faz-2.2b/borc11", 1, "grain-farkında çapraz-cube geçişi — kullanıcıya gösterilen "
                          "notun içine tanelik uyarısı giriyor (`grain_uyarisi`). Uyarıyı "
                          "cevaba TAŞIYAN satır `ask()` içinde olmak zorunda: notu üreten "
                          "yer orası. Karar ve metin `app/cekirdek.py`'de"),
    ("faz-5.16", 1, "NETLEŞTİRME DÜZEYİ bağlandı — `_olcu_belirsizligi_netlestir`'in "
                    "ilk satırı `netlestirme.sorar_mi()`'ye sorar. 🔴 Bu satır TAŞINAMAZ: "
                    "karar noktası `ask()`in kendi dalıdır ve kararı bir modüle çıkarmak "
                    "dalın kendisini de çıkarmak demektir (o da 33 satır ve `ask()`in "
                    "yerellerine bağlı). Kapının ölçüsü **eklenen kod**, ve eklenen kod "
                    "TEK satır: `sorar_mi()` çağrısı. Eşik ve düzey çözümü modüle ve "
                    "modül-düzeyi yardımcıya ait — `ask()`e giren yalnız SORU"),
    ("KÖK-4/donem_capasi", 3,
     "🔴 TAKİP TURUNDA DÖNEM ÇAPASI (denetim raporu KN-1) — sondanın EN BÜYÜK tek "
     "kümesi: 43 netleştirmenin 34'ü dönem, 26'sı TAKİP turunda ve 26/26'sında önceki "
     "turda dönem VARDI. Ölçü değişince `deterministic_refine` dönemi düşürüyor ve "
     "`_period_gate` «Hangi dönem için?» diye soruyor — oysa cevap bir tur önce "
     "verilmişti. "
     "🔴 Bu altı satır TAŞINAMAZ ve sebebi konum: `_period_gate` takip zincirinin DÖRT "
     "dalının da (refine · cross_cube_add · cross_cube_dim_switch · taze route) geçtiği "
     "TEK karar noktasıdır. Dört yere ayrı ayrı yazmak 'aynı kuralın iki sahibi' "
     "sınıfını DÖRDE katlardı. Taşınabilir olan her şey `app/donem_capasi.py`'de: üç "
     "şart, zaman-boyutu yeniden adlandırma, not metni, TAŞIYICI temizliği. "
     "⊙ Büyüme kapısı bunu İKİ KEZ ölçtü ve iki kez de tasarımı düzeltti: "
     "10 satır → 3 (yerinde taşıma + notu_al modüle gitti). "
     "⚠ Ve `return None` KALDIRILMADI (anti-çözüm A4): o dal bilinçli — farklı metrik "
     "gerçekten yeni bir sorudur. Dönem soruya değil OTURUMA bağlandı"),
    ("KÖK-2+3/uyum", 8,
     "🔴 UYUM KAPISI + BEYANLI KISMİ CEVAP (denetim raporu KÖK-2·KÖK-3). Ölçülen: "
     "`route()` bir CubeQuery üretiyor ama sorudaki NİYET İŞARETİNİN sorguda karşılığı "
     "olduğu hiçbir yerde denetlenmiyordu — `ocak ve haziran ciro karşılaştır` → "
     "Ocak-Haziran TOPLAMI, üstelik `source=cube` rozetiyle. "
     "🔴 Bu sekiz satır TAŞINAMAZ ve sebebi konum: denetim, sorgunun ÇALIŞTIĞI ve "
     "sonucun BİLİNDİĞİ noktada yapılmalı (`_answer_from_cube_query`); daha erken "
     "yapılsa `order`/`limit` henüz yok, daha geç yapılsa cevap çoktan gitmiş olur. "
     "Taşınabilir olan HER ŞEY `app/uyum.py`'de: yedi değişmez, dedektörler, "
     "kısmi-cevap metni. `ask()`e giren yalnız ÇAĞRI, cube_meta çözümü ve İKİ ATAMA. "
     "⊙ Ölçüldü: 525 meşru soruda 0 yanlış-pozitif, 5/5 hedef yakalandı; ölçüt üç kez "
     "düzeltildi ve her düzeltme bir yanlış-pozitif ölçümünden geldi"),
    ("KÖK-7d/turetme", 4,
     "🔴 TÜRETME KATMANI (denetim raporu KN-8/KÇ-10) — katalog yalnız İSİM biçimini "
     "biliyor, kullanıcı FİİL kuruyor: `sattık`→satış · `ürettik`→üretim · "
     "`alacağımız`→alacak; üçü de **R10** ile ölüyordu. `_ek_gecerli` ÇEKİMİ çözer, bu "
     "TÜRETMEDİR — farklı bir dilbilimsel işlem ve depoda karşılığı yoktu. "
     "🔴 Bu 4 satır `_honest_refusal`in içinde ve TAŞINAMAZ: o yardımcı deponun BÜTÜN "
     "dürüst retlerinin TEK ÇIKIŞ KAPISIDIR; türetmeyi tek tek dallara yazmak 'aynı "
     "kuralın iki sahibi' sınıfını DÖRDE katlardı. Karar `app/turetme.py`'de (kapalı ek "
     "envanterleri · yumuşama geri alma · hafif-fiil sınıfı), şema çözümü modül düzeyi "
     "`_turetme_adaylari`'nda (ayrı muafiyet). "
     "⚠ FAIL-CLOSED: chip üretir, CEVAP ÜRETMEZ — `route()` bu modülü hiç görmez ve "
     "`test_ROUTE_TURETMEYI_GORMUYOR` bunu kilitler. Kapsam riski YAPISAL olarak sıfır; "
     "KÖK-7b'nin ölçülmüş dersi budur (o, kapsamı AÇARAK denedi: ölçüt tuttu ama "
     "kabul 1150→1117, sessiz_yanlis 12→30). "
     "⊙ İki ölçüm, iki düzeltme: 1. turda korpusta **191 (%9,0)** chip üretti ve ÇOĞU "
     "SAHTEYDİ (`may`→prim · `ogrnim`→kar oranı — kelimenin KENDİSİ aday sayılıyordu); "
     "kullanıcı tarafı gerçek bir çekim soymak zorunda kılınınca **0**'a indi. "
     "*Bir tahminin ucuz olması, yanlış olmasını ucuzlaştırmaz*"),
    ("AJ0/kisa-devre-yasagi", 6,
     "🔴🔴 KISA DEVRE YASAĞI — MIMARI §5'in **18. yasağı** (yol haritası §G/AJ0, "
     "*'ÖNCE BU İNER'*). Ölçüldü: *«mart ayında ciro şubata göre nasıl DEĞİŞTİ»* → "
     "**«degisti» yerine «egitim» mi demek istedin?** Bir yazım TAHMİNİ, cevap "
     "üretebilecek bir yolun (Discovery) önünü kesiyordu; ikinci vaka "
     "`enerji kaynağı→enerji tep`. Kodun KENDİ yorumları aynı hatayı ÜÇ KEZ kaydetmiş "
     "— her seferinde çağrı yerinde yamalanmış, KAPININ KENDİSİNDE HİÇ. "
     "🔴 Bu 6 satır TAŞINAMAZ ve sebebi konum: üç `_try_fresh_intent()` çağrı yeri + "
     "typo dalının `_merdiven.kaydet` çevrimi + Discovery başarısızlığında aday dönüşü "
     "— hepsi `ask()`in KENDİ akış noktaları. Mekanizmanın tamamı `app/merdiven.py`'de "
     "(aday defteri + üç bitirici) ve `ask()`e giren yalnız BİR nesne + çağrılar. "
     "⚠ İlk uygulama üç CLOSURE'dı ve büyüme kapısı iç-fonksiyon tavanını (19) kırmızı "
     "verdi; kapı haklıydı — mekanizma `ask()`in hiçbir yereline bağlı değil. "
     "⊙ Sonuç: kısa devre 11 → **10**, ve envanter düşüşü KENDİ bildirdi"),
    ("KÖK-1/faz2-bellek", 1,
     "🔴 NİYET BELLEĞİ İSTEK SINIRINDA (`bellek_sifirla()`) — KÖK-1 Faz 2'nin ÖN KOŞULU. "
     "Ölçüldü: reddedilen bir soruda `partial_unknowns` **DÖRT KEZ** koşuyordu. Niyet "
     "nesnesi 'tek çatı' olacaksa çatıya girmek UCUZ olmalı; aksi hâlde her yeni tüketici "
     "tam bir yeniden-çözümleme ekler ve tek çatı, dağınık okuyuculardan PAHALI hâle "
     "gelir — yani KÖK-1'in kendisi bir maliyet kalemine dönüşür. "
     "🔴 Bu TEK satır TAŞINAMAZ ve yeri tesadüf değil: `reset_llm_usage()` ile AYNI "
     "yerde, çünkü ikisi de istek-kapsamlı bir birikimi temizler. Daha geç konsa bir "
     "önceki isteğin niyeti sızardı (`test_BELLEK_ISTEK_SINIRINA_BAGLI` sırayı kilitler). "
     "⊙ Sonuç: türetme çağrı yeri niyetten okumaya geçince 4 → 3. "
     "*Bir soyutlamanın benimsenmesi, ona girmenin maliyetiyle ters orantılıdır*"),
    ("KÖK-1/niyet-izi", 2,
     "🔴🔴 NİYET NESNESİ FAZ 1 (denetim raporu KÖK-1 · devralınan KÇ-0). Raporun "
     "teşhisi: *«KN-4 (uyum denetimi) YAZILAMAZ çünkü karşılaştırılacak iki şey yok; "
     "KN-1 kaçınılmaz çünkü taşınacak durum bir NESNE DEĞİL.»* Ölçüldü: `app/`'de "
     "`Niyet` sınıfı YOKTU ve o boşluk bu turda **BEŞ ayrı yerde** ayrı ayrı dolduruldu "
     "(`uyum` · `yetenek` · `donem_capasi` · `turetme` · `belirsizlik_chipi`) — 'aynı "
     "kuralın iki sahibi' sınıfının BEŞE KATLANMIŞ hâli. "
     "🔴 Bu 2 satır (`if bayrak:` + atama) `_finish`in içinde ve TAŞINAMAZ: merdivenin "
     "HANGİ basamağından çıkılırsa çıkılsın oradan geçilir; niyeti tek bir dala bağlamak "
     "ölçmek istediğimiz şeyin YARISINI görmemek olurdu. Nesne `app/niyet.py`'de, "
     "şema çözümü modül düzeyi `_niyet_izi`'nde (ayrı muafiyet). "
     "⚠ FAZ 1 SÖZLEŞMESİ: hiçbir karar değişmez — `route()` nesneyi GÖRMEZ "
     "(`test_ROUTE_NIYETI_GORMUYOR`), davranış birebir aynı "
     "(`test_ROUTE_DAVRANISI_DEGISMEDI`), bayrak kapalıyken TEK SATIR bile eklenmez. "
     "⊙ Ve ölçülebilir hâle gelen şey: `ocak ve haziran ciro` → `dönem=2(çözülemedi)` · "
     "`🔴temsil-yok=cok_donem`. *Bir sistemin temsil edemediği şeyi SAYABİLMESİ, onu "
     "görebilmesinin ilk adımıdır*"),
    ("KÖK-9/belirsizlik-chipi", 1,
     "🔴 BİLİNEN BELİRSİZLİK BEYAN EDİLİR (denetim raporu KN-6/KÇ-6). Ölçüldü: "
     "`metrik_kaydi` kaydındaki **62/62** terim ≥2 adaylı ve HİÇBİRİNİN sahibi yok; "
     "cevaplanan soruların **%11,7'si** (18/154) bu terimlerden biri üzerinden gidiyor "
     "ve kullanıcı hangi tanımın kullanıldığını HİÇBİR YERDEN öğrenemiyordu "
     "(`parti sayısı`→oee/parti · `enerji tep`→3 cube · `adet`→**6** cube). "
     "Kazananı bir karar değil bir YAN ETKİ belirliyordu: aday üretecinde boyut sayısı. "
     "🔴 Bu TEK satır bir çağrıdır; karar `app/belirsizlik_chipi.py` ile "
     "`app/metrik_kaydi.py` arasında ve yardımcı `_belirsizlik_beyani` MODÜL DÜZEYİNDE "
     "(ayrı muafiyet listesinde) — `ask()` gövdesine giren yalnız atama. "
     "⚠ REDDETMEK DEĞİL, ve sebebi ölçüldü: belirsizse `route()`u susturmak korpusu "
     "%94,3 → **%83,6** düşürdü (dar hâli bile boyahane erişimini %69→%66 yaptı). "
     "Raporun ölçütü *belirsizlik sıraya değil CHİP'e* — cevap gider, alternatif beyan "
     "edilir, **kapsam maliyeti sıfırdır**"),
    ("KÖK-6/yetenek", 2, "🔴 YETENEK KAPISI (denetim raporu KN-3) — *"
                         "«forecast v1'de yok» gibi ÜRÜN-DÜZEYİ bir sınır Discovery'ye "
                         "düşüp bir SAYIYA dönüşüyordu (`adhoc.toplam_toplam_ciro`). "
                         "🔴 Bu iki satır TAŞINAMAZ ve sebebi kod değil KONUM: kapının "
                         "tek güvencesi *«route() ve Intent-JSON'ın İKİSİ de pes ettikten "
                         "SONRA»* çalışmasıdır. Daha erken bir yere konsa cevaplanabilir "
                         "soruları keserdi; daha geç konsa Discovery zaten devralmış "
                         "olurdu. Taşınabilir olan HER ŞEY `app/yetenek.py`'de: üç "
                         "dedektör, üç kutu, mesajlar ve yanıt alanları. `ask()`'e giren "
                         "yalnız ÇAĞRI ve DÖNÜŞ. ⊙ Ölçüldü: 968 meşru soruda "
                         "**0 yanlış-pozitif**, 3/3 hedef yakalandı"),
    ("faz-1.3b/2", 3, "Katman B'nin Discovery çağrı yolu — TAŞINABİLİR OLAN HER ŞEY "
                      "`app/katman_b.py`'ye taşındı (zorlama · allowlist okuma · ret notu "
                      "· sarmal sınıf). `ask()`'te kalan üç satır taşınamaz: motoru bir kez "
                      "saran bağlama (1) + yetki reddini onarım yoluna DÜŞÜRMEYEN `except` "
                      "(2). Reddi onarıma bırakmak 2 satır kazandırırdı ama bir yetki "
                      "sınırını 'güvenilir bir sorgu üretemedim' diye raporlardı — tavan, "
                      "dürüst olmayan bir mesajı SATIN ALMAZ"),
    ("faz-34-siralama", 4,
     "🔴 **ÜSTÜNLÜK SIRALAMASININ İKİ ÇAĞRI YERİ** — kuralın kendisi `app/siralama.py`'de "
     "(bu kapının istediği gibi **modüle çıkarıldı**); `ask()`'te kalan yalnız iki çağrı: "
     "ortak huni (`_answer_from_cube_query`, 2 satır — biri çağrı biri **iz kaydı**) ve "
     "dönem netleştirmesi (1 satır) — ve `§40`'ta aynı yere EŞİK taşıma çağrısı "
     "eklendi (1 satır): niyet parçaları netleştirmeden birlikte sağ çıkmalı. "
     "⚠ **TAŞINAMAZ:** ikisi de *bir cq'nun hayatındaki AN*'dır, bir hesap değil. Huni "
     "zaten dört üreticinin tek buluşma noktası (kendi docstring'i: *«her yeni Intent-path "
     "kaynağında yeniden yazılmasın»*); netleştirme ise `cq`'yu **cevaba koymadan önceki** "
     "son andır. Çağrıyı dışarı almak, çağrının **yerini** kaybetmek olurdu. "
     "⊙ İz satırı bilerek burada: kullanıcının gördüğü sıralamayı **sistemin koyduğu** "
     "makbuza yazılmazsa, kullanıcı onu kendi yazdığını sanır"),
    ("bbb-merdiven-bos-cevap-dondurebiliyordu", 1,
     "🔴🔴 **MERDİVEN BOŞ BİR CEVAP DÖNDÜREBİLİYORDU.** Ölçüldü (`BB19`/`BB20`, canlıda "
     "tekrarlandı): `source=None · note=None · trace=[] · chip=0 · satır=0` — kullanıcı "
     "ekranda HİÇBİR ŞEY görüyordu. `§0.0`'ın en açık ihlali (*kullanıcı asla cevapsız "
     "kalmaz*) ve en sinsi biçimi: bir hata bile değil, sistem «başarıyla» boş döndü. "
     "⊙ Kusurun yeri bir DAL DEĞİL — merdivenin herhangi bir basamağı boş bir nesne "
     "üretebilir ve hepsini tek tek denetlemek `KAT-1`'in kendisidir. Değişmez UCUN "
     "değişmezidir → kapanış hunisinde durur (`_finish` zaten *«hangi basamaktan "
     "çıkılırsa çıkılsın buradan geçilir»* diye seçilmiş tek huni). "
     "⚠ **TAŞINAMAZ:** mühürden (`seal`) hemen önce olmalı — sonra konsa boş cevap zaten "
     "mühürlenmiş, yani KAYDEDİLMİŞ olurdu. "
     "⚠ Yüklem İKİ KEZ yanlış yazıldı ve ikisi de ölçüldü: (1) `trace`/`source` içerik "
     "sayıldı → guard sessiz kaldı; (2) alanlar ELLE sayıldı ve `kpi` unutuldu → geçerli "
     "bir KPI cevabının üstüne yazdı (`§101.1`). Nihai yüklem TERSİNE çevrildi: cevap, "
     "`question` dışındaki HER alanı boş olduğunda boştur — yarın eklenen bir alan "
     "guard'ı kendiliğinden doğru tutar. ⚠ **VE KAPI BANA NEREYE KOYACAĞIMI DA SÖYLEDİ:** ilk yazımda `ask()` içinde bir closure'dı ve `test_ASK_IC_FONKSIYON_SAYISI_ARTMIYOR` kırmızı verdi — o ölçütün muafiyet listesi BOŞTUR ve boş kalması bir başarıdır. Kapının kendi cümlesi: *«yeni bir yardımcı gerekiyorsa MODÜL DÜZEYİNE al: saf bir fonksiyon test edilebilir, closure edilemez»*. Taşındı; `ask()` içinde kalan tek satır **çağrının kendisidir**. *Bir kapı yalnız hayır demez, bazen nereye koyacağını da söyler.*"),
    ("aa2-v4un-ikinci-dali-makbuz-yine-llmsiz-diyordu", 5,
     "🔴 **`§V4`'ÜN İKİNCİ DALI — ve `§72`'nin ölçüm aletini TERS okutuyordu.** Ölçüldü "
     "(`AA16`, Hollandaca — *«Waarom is de OEE van RAM-3 lager dan de andere machines?»*): "
     "iz `çapraz konu → netleştirme (LLM'siz)` yazdı; oysa `route_hit is None` olduğu için "
     "garson YUKARIDA çağrılmıştı ve kullanılabilir bir karar üretemedi. "
     "⊙ `§72` yabancı dili bir ÜRÜN HEDEFİ değil bir ÖLÇÜM ALETİ olarak kuruyor: "
     "route'tan bağımsız olduğu için garsonun işini yapıp yapmadığını temiz gösterir. "
     "Ama iz *«LLM'siz»* dediği sürece gösterge TERS okunuyordu — sanki garson hiç "
     "çağrılmamış gibi. `§V4` bu kusuru ÖTEKİ dalda düzeltmişti; bu dal o göçün dışında "
     "kalmıştı (`KAT-1`: aynı kuralın iki dalı, biri düzeltilmiş). "
     "⚠ **TAŞINAMAZ:** düzeltme `_belirsiz`in DÖNDÜĞÜ yerde olmalı — iz orada üretiliyor "
     "ve `_garson_konustu` yalnız orada kapsamda. "
     "*Bir ölçüm aletini yanlış etiketlemek, ölçtüğü şeyi görünmez yapar.*"),
    ("x5-kapi-neden-atesledigini-soylemiyordu", 3,
     "🔴 **BİR KAPININ KARARI, GİRDİSİYLE BİRLİKTE LOGLANMAZSA DENETLENEMEZ** "
     "(`ADR-0020`: sessiz yutma yok). Ölçüldü (`X5` Fransızca · `X19` Rusça · `Y1`): "
     "cevap dönem filtresini **taşıyordu** ve kapı yine *«hangi dönem için?»* dedi — "
     "hangi zaman boyutuna bakıldığı, elde hangi filtrelerin olduğu ve `period_optional`'ın "
     "ne olduğu **hiçbir yerde yazmıyordu**. Sonuç: teşhis üç turda da tahmine kaldı ve "
     "`§X1` (sabit `\"tarih\"`) ancak kaynağı **okuyarak** bulunabildi. "
     "⚠ **TAŞINAMAZ:** kararın verildiği yerde, `return`'ün hemen öncesinde — bir karar "
     "logunun değeri, kararla **aynı** kod noktasında olmasından gelir; başka yere "
     "konursa aradaki her dal onu geçersiz kılabilir. "
     "⊙ `§47`'nin (*«garsonun kararı kayboldu»*) aynı dersinin dönem kapısındaki hâli."),
    ("x4-hesabi-sorulacak-rapor-yoksa-merdivene-inilmez", 15,
     "🔴🔴 **BAĞLAMSIZ BİR MAKBUZ SORUSU DISCOVERY'DE 25 SANİYE YANDI.** Ölçüldü (`X3` — "
     "*«bu kıyas hangi tarih aralığını kapsıyor»*, önceki tur cevapsız kalmıştı): "
     "`Discovery: bütçe aşıldı (25 sn) → dürüst ret`. "
     "⊙ İki kayıp: (1) 25 sn + bir Discovery ateşlemesi — `§0.0`'a göre her ateşleme bir "
     "MUTFAK EKSİKLİĞİ RAPORUDUR, ve bu raporlanacak bir eksiklik bile değildi; "
     "(2) cevap YANLIŞ CİNSTEN — Discovery ham SQL üretir, oysa soru veriye değil "
     "EKRANDAKİNE dair; hiçbir SQL *«ortada rapor var mı»*yı cevaplayamaz. "
     "⊙ Doğru cevap tek satırlık ve KESİN OLARAK BİLİNEN bir olgu: ekranda rapor yok. "
     "Onu söylemek için ne LLM ne sorgu gerekir (0 ms). "
     "⚠ **TAŞINAMAZ:** `sinifla()` çağrısının **hemen ardında** durmalı — kusur tam olarak "
     "niyetin doğru sınıflanıp yanlış basamağa gönderilmesiydi; kararı çağrıdan uzağa "
     "koymak aradaki her dalın yeniden aynı tuzağa düşmesine kapı açardı. "
     "⚠ Uydurma yok: yalnız bilinen olgu + ne yapılabileceği (`D4` proaktif sınır deseni)."),
    ("v1-makbuz-sorusu-8-konusma-turu", 31,
     "🔴🔴 **SİSTEM CEVABI ÜRETİYOR AMA ONA ULAŞAN KAPI YOKTU — üç kanıt.** "
     "`u2` *«bu nasıl hesaplandı?»* → dürüst ret · `V2` *«bu rakama neler dahil, nasıl "
     "bulundu»* → dürüst ret · `V17` *«bu sayı neyi kapsıyor, hangi tarih aralığı»* → "
     "**aynı tablo ikinci kez sunuldu**. ⊙ `V2`'nin reddi en öğreticiydi: sistem soruyu "
     "*«mevcut raporun hesaplama yöntemini sorguluyor»* diye **doğru tarif edip** attı. "
     "🔴 Oysa cevap ZATEN üretiliyor: `drill.formula_explanation` her cevaba "
     "`calculation_explanation` olarak yazılıyor; `temellendirme` ve `explain` de dolu. "
     "Üç alan doluydu, **konuşma türü yoktu**. "
     "⚠ **TAŞINAMAZ:** bu bir hesap değil, `_cevap_ustunde_konus`'un altıncı **dalıdır** — "
     "kardeşleri (`NEDEN`/`NORMAL`/`NE_YAPMALI`) de burada duruyor ve hepsi aynı üç şeyi "
     "paylaşıyor: `prev_cq` · `cube_meta` · `_finish`. Dalı dışarı almak bu üçünü "
     "parametre olarak taşımak olurdu — yani closure'ı elle yeniden kurmak. "
     "⊙ Dalın kendisi **yeni motor açmıyor**: üç kaynağın üçü de var olan katalog "
     "alanları (`measure_expressions` · `units` · `base_object`) ve yeni sorgu koşmuyor — "
     "`V17`'nin kusuru tam da yeni sorgu koşmaktı. *Bir fişi okumak için mutfağa gidilmez.*"),
]
MUAFIYET_CUBE_ROUTER_KOD = [
    ("kv-olcusuz-fis-donem-sormaz", 2,
     "🔴 **`§KV` — ÖLÇÜSÜZ BİR FİŞTE DÖNEM SORULMAZ.** Canlı `V` turunda ölçüldü: "
     "*«kaç makinemiz var»* fişi `measures: []` ile geliyor (varlık sorusu, "
     "`app/sayim.py`) ama dönem kapısı yine *«dönemi çözemedim — son 12 ayı aldım»* "
     "deyip **filtre ekliyordu**. Yani cevabın kendi beyanı (*«bir dönem "
     "varsayılmadı»*) ile fişi **çelişiyordu** — `§RE`'nin aynı sınıfı. "
     "⊙ Δ = 2: `if measure is None: return True`. "
     "⚠ **TAŞINAMAZ:** `is_period_optional`'ın kendi docstring'i *«dönem-kapısı için TEK "
     "gerçek kaynak»* diyor; kuralı başka yere yazmak ikinci bir sahip demekti (`KAT-1`). "
     "⚠ Ve bu bir istisna değil, o docstring'in **devamı**: dönem sorusu *«bu ölçü hangi "
     "aralıkta toplanacak»* demektir; toplanacak ölçü yoksa sorunun kendisi yoktur. "
     "`None` bu yüzeyde yalnız boş `measures`'tan doğar — üç çağıranın üçü de ölçüldü. "
     "*Bir listeye «hangi dönem» diye sormak, listeyi bir toplam sanmaktır.* "
     f"`sha=2eca01a`"),
    ("dk3-tek-kaynak-erisimci", 11,
     "🔴🔴 **`§DK-3` — ROUTE İLE GARSON AYNI MENÜYE BAKAR.** Route değerleri ham model "
     "kolonlarından **boyut adıyla** okuyordu; `vardiya` için o kaynakta kolon **hiç "
     "yok** → süzgeç yapısal olarak imkânsızdı. Canlı bedeli bir **sessiz yanlış**: "
     "*«bu yıl 1. vardiyada fire oranı»* → üç vardiya birden, ilk satır *«3. Vardiya»*, "
     "beyan yok. Düzeltmeden sonra **%16,78**, doğru vardiya. "
     "⊙ Δ = 11: eşleştirmenin **tamamı** `app/deger_eslesme.py`'ye taşındı (62 satır); "
     "burada kalan iki **çağrı** ve bir **yerel-import erişimcisi**. "
     "⚠ **TAŞINAMAZ:** erişimci bir döngüyü kırıyor — `deger_eslesme` bu dosyadan "
     "`_norm` ve `_value_token_hit` alıyor, modül düzeyinde import bir **döngü** olurdu. "
     "Ve iki çağrı yeri route'un kendi süzgeç kurma satırlarıdır. "
     "*Bir bağımlılığı tersine çevirmek yerine geciktirmek, deponun kayıtlı desenidir.* "
     f"`sha=72e7e3b`"),
    ("yb-yon-beyani-cagirana-gecirildi", 1,
     "🔴🔴 **`§YB` — BEYAN VARDI, ÇAĞIRAN OKUMUYORDU.** `_direction`'ın `az_iyi` "
     "parametresi `§W-C`'de eklendi ve doğru çalışıyor (*«en kötü»* + `lower_is_better` "
     "→ `DESC`); ama route'un **kendi** sıralaması onu hiç geçirmiyordu — `siralama."
     "tamamla` dışında kimse geçirmiyordu. "
     "⊙ Ölçüldü (canlı curl): *«bu yıl **en kötü** bakım maliyeti olan makine»* → "
     "`direction: asc` → **ROTASYON BASKI · 15.161 ₺**, yani **EN UCUZ** makine; "
     "`source=cube`, beyan yok. Bir maliyette *«en kötü»* en yükseğidir. "
     "⚠ Ve beyan **eksik değildi**: `bakim_maliyeti` pack'te ilan edilmiş ve şemaya "
     "ulaşıyordu. Kusur bilgide değil, bilgiyi **okumayan çağırandaydı**. "
     "⊙ Δ = 1: `direction = _direction(q, <az_iyi>)` tek satıra sığdı. "
     "⚠ **TAŞINAMAZ:** karar `route()`in **kendi** sıralama satırıdır. "
     "*Bir beyanı bir çağıranda okumak, onu beyan etmiş saymaz.* `sha=f9cd3cb`"),
    ("eb-t-ayirt-etmeyen-token-taninir", 1,
     "🔴 **`§EB/T` — AYIRT ETMEYEN AMA TANINAN TOKEN.** ⊙ Ölçüldü: `grubu` iki boyutun "
     "**etiketinden** türediği için kırılım seçiminden düşürüldü (`§EB`) — ve o anda "
     "**kapsam kapısı** da onu kaybetti: *«bu yıl yas_grubu bazında işlenen kg»* → "
     "*«\"grubu\" başka bir konu gibi görünüyor»*. "
     "⊙ Kusur ayrımda: `partial_unknowns` *«bu kelime dağarcığımızda mı»* diye sorar, "
     "`_match_dimension` *«hangi boyutu adlandırıyor»* diye — **ikisi aynı listeden "
     "okuyordu**. "
     "⊙ Δ = 1: `known |= _syn_hit_words(q, c.get(\"belirsiz_boyut_tokenlari\"))`. "
     "⚠ **TAŞINAMAZ:** `known` kümesi bu fonksiyonun **kendi** birikimidir; dışarı "
     "almak kapsam kararını iki dosyaya bölerdi. "
     "*Bir kelimeyi tanımak ile onunla bir şeyi seçmek aynı yetenek değildir; birini "
     "kaldırmak ötekini de kaldırıyorsa liste iki iş yapıyordur.* `sha=4d325dd`"),
    ("gg9-tam-kelime-siniri-alfabesinin-yarisini-taniyordu", 1,
     "🔴🔴 **TAM-KELİME SINIRI ASCII-ONLY'Dİ.** Ölçüldü (canlı `GG9`): *«nasıl "
     "**de**ğişti»* → `kalite.ort_dE` eşleşti ve soru iki-cube yetenek sınırına düştü. "
     "Sebep `(?![a-z0-9])`: `ğ` bu sınıfta YOK, yani `de` + `ğ` bir **kelime sonu** gibi "
     "okundu ve `\"dE!\"` işaretinin (tam-kelime) koruması **tam da korumak için konduğu "
     "yerde** çöktü. ⊙ Pack bu tehlikeyi ÖNCEDEN yazmıştı: *«2 harfli kısa sinonim "
     "substring-eşleşmede tehlikeli»* — koruma vardı, sınır yanlıştı. "
     "⚠ Bedel **bir** satır: regex çok satıra yayıldı (100 karakter sınırı). "
     "Alternatif — `_match_measure`'ün normalize etmesi — reddedildi: o, çağıranın "
     "hafızasına güvenmek olurdu; bu sınır normalize edilmiş girdide de **doğru** "
     "(no-op). 🔴 Ve bu bir dil kuralı EKLEMEK değil: `ADR-0008` sözcük listesi "
     "yasaklar, **alfabe tanımını** değil. *Bir kelime sınırını alfabesinin yarısıyla "
     "tanımlamak, öteki yarısını sınır sanmaktır.*"),
    ("wc-en-kotu-bir-yondur-buyukluk-degil", 6,
     "🔴🔴 **`lower_is_better` BEYANLI HER ÖLÇÜDE «EN KÖTÜ» TAM TERSİNİ VERİYORDU.** "
     "`_AZLIK_KUTBU` iki farklı CİNS kelime taşıyordu: `dusuk/az/kisa/kucuk/yavas` bir "
     "**BÜYÜKLÜK** bildirir (koşulsuz `ASC`), `kotu/verimsiz` ise bir **NİTELİK** "
     "bildirir ve yönü ölçünün iyi yönüne bağlıdır — `toplam_ciro`'da «en kötü» = en AZ, "
     "`toplam_fire_kg`'de «en kötü» = en ÇOK. "
     "⊙ Ölçüldü (`W19` · `E3`): *«karbon ayak izini en kötüden iyiye sırala»* → `asc`, "
     "yani EN TEMİZ kısım en üste kondu ve cevap bunu SÖYLEMEDİ (sessiz-yanlış). "
     "⊙ `lower_is_better` katalogda HEP vardı; okuyan yoktu. Bir sıfatın yönünü "
     "sözlükten okumak, ölçünün kendi beyanını görmezden gelmektir. "
     "⚠ **SÖZLÜK BÜYÜMEDİ** — iki kelime bir kümeden ötekine TAŞINDI; `iyi`/`verimli` "
     "bilerek eklenmedi (bugünkü `DESC` varsayılanlarının ölçülmüş bir kusuru yok; bir "
     "kutbu simetri uğruna doldurmak ölçülmemiş bir değişikliktir). "
     "⚠ **TAŞINAMAZ:** `_direction`'ın gövdesinde — kutupların **yanında** durmalı, "
     "çünkü kusur tam olarak ikisinin aynı kümede yaşamasıydı; ayırmayı başka dosyaya "
     "koymak ayrımı bir daha yan yana okunamaz kılardı. "
     "⚠ İmza geriye uyumlu (`az_iyi=None` → bugünkü davranış): meta taşımayan iki çağıran "
     "bayt bayt aynı kalır."),
    ("o6-ayrik-donem-on-kosulunu-kimse-kurmuyordu", 3,
     "🔴🔴 **`FAZ O-6` — `§49`'UN TEŞHİSİ YARIM DOĞRUYMUŞ.** Rapor *«`CubeQuery` iki ayrık "
     "dönemi TEMSİL EDEMİYOR»* diyordu (dokuz kanıt: `V12`·`X2`·`X11`·`X13`·`AA9`·`BB10`…). "
     "⊙ Ölçüldü (canlı): mekanizma **zaten vardı** — `ayrik_aylar` işareti üretiliyor ve "
     "`wren_service._ayrik_ay_sar` onu uyguluyor. Eksik olan **ay kovasıydı**: sarma ay "
     "granülerliği yoksa çalışamıyor (fail-closed) ve sorgu sessizce **kapsayan aralığa** "
     "düşüyordu. Yani `CubeQuery` iki dönemi TAŞIYABİLİYORDU; ön koşulunu kuran yoktu. "
     "⊙ İKİNCİ KUSUR aynı satırda çıktı: *«bu yıl»* ayrık-ay tespitini **tamamen "
     "kapatıyordu** — koşul *«zaman filtresi varsa ayrık arama»* idi ve yıl filtresini "
     "*«kullanıcı aralık yazdı»* diye okuyordu. Oysa **yıl bir KAPSAM, aylar o kapsamın "
     "İÇİNDEKİ seçimdir**; ikisi çelişmez, biri ötekini DARALTIR. Kural daraltıldı: "
     "yalnız ay-düzeyinde bir çift (gte+lte) tespiti kapatır. "
     "✅ Canlı: *«bu yıl ocak ve haziran ayında fire oranı»* → **2 satır** (ocak %20,47 + "
     "haziran). Gerileme yok: aylık trend 6 satır, gerçekten toplanan soru hâlâ beyanlı. "
     "⚠ **TAŞINAMAZ:** `ayrik` hesabının **hemen yanında** — ön koşul, koşulladığı şeyin "
     "yanında kurulmalı; ayrı yere konsa aradaki her dal onu yine kapatabilirdi. "
     "*Bir yeteneği kurup ön koşulunu kurmamak, onu hiç kurmamaktır.*"),
    ("ccd-cce-isaret-sizintisi-ve-ayrilma-eki", 6,
     "🔴🔴 **İKİ KÖK, İKİSİ DE `cube_router`'da ve ikisi de ÖLÇÜLDÜ.** "
     "**`§CC-D`** — `§W-C`'de katalog metnine eklediğim yön işareti (`↓`) ölçü adına "
     "SIZIYORDU: canlı log `intent: whitelist REDDİ — ham={\"measures\":"
     "[\"toplam_su_lt↓\"]}`. Garson işareti ADIN PARÇASI sandı; beyaz liste DOĞRU "
     "reddetti. `↓` taşıyan HER ölçü (fire · duruş · maliyet · karbon) sessizce "
     "erişilemez olmuştu — `§72`'nin ampulü kırmızı yandı ama sebebi dil değil BENİM "
     "eklediğim bir karakterdi. Çözüm işareti kaldırmak DEĞİL (`§W-C` ölçülmüş kazanç): "
     "ad NORMALLEŞTİRİLİR — işaret sunumdur, kimlik değil. Sondaj 3/3. "
     "*Bir ada eklenen her süs, o adın bir varyantını doğurur; doğrulayan taraf varyantı "
     "bilmiyorsa süs bir kusura dönüşür.* "
     "**`§CC-E`** — `_THRESHOLD_RE` *«dan az»*ı İKİ KELİME sanıyordu; oysa ayrılma hâli "
     "bir EKTİR ve sayının ardından gelen İSME yapışır (*«100 partiden az»* · *«5 "
     "makineden fazla»*). `CC17`'de eşik hiç uygulanmadı. Yeni kelime yok — eklenen şey "
     "sayı ile karşılaştırıcı arasına EK ALMIŞ BİR İSMİN girebilmesi. Sondaj 8/8; "
     "*«3 makine bazında»*/*«ilk 5 müşteri»*/*«2026 yılında»* temiz. "
     "⚠ **TAŞINAMAZ:** ikisi de kendi yükleminin YANINDA — `_AZ_IYI_ISARETI` beyaz "
     "listenin, eşik deseni `_measure_threshold`'un. Ayırmak, kuralı okuyan yerden "
     "uzaklaştırırdı."),
    ("v5-sifat-fiil-kategori-degeri-degildir", 8,
     "🔴🔴 **BİR SIFAT/FİİL BİR KATEGORİ DEĞERİ DEĞİLDİR — üç kanıt, tek kök.** "
     "`t19` *«ortalama şiddet»* → `siddet eq 'ORTA'` + `renk eq 'Orta'` · "
     "`§86.8` *«bu grafiği açıkla»* → `renk_derinlik eq 'Açık'` · *«hariç tut»* → "
     "cümlenin kendisi filtreye dönüyordu. "
     "⊙ Sondaj (kaynak okundu, koşulmadı) kökü tek satırda gösterdi: `_value_token_hit` "
     "`\\b{nv}\\w*` ile **SINIRSIZ** ek kabul ediyordu; kardeşi `_syn_hit` ise "
     "`_ek_gecerli` → `_SUFFIX_CHAIN_RE` disiplinini kullanıyor. Yani `KAT-1`: **aynı "
     "sorunun iki sahibi** — `_syn_hit` iki kez (Faz 0.4 · D3) düz alt-dizeden "
     "kurtarıldı, DEĞER eşleştiricisi o göçün dışında kaldı. "
     "⚠ Zincire geçmek yetmedi (`lama` = `la`+`m`+`a`, üçü de atom): ikinci kural "
     "**isimden fiil yapan ek bir ÇEKİM DEĞİLDİR** — `_NEGATION_SUFFIXES`'in gerekçesiyle "
     "birebir aynı mantık (*«ek anlamı tersine çevirir: fire ≠ firesiz»*), burada ek "
     "**sözcük sınıfını** çevirir: `orta` sıfat, `ortala-` fiil. "
     "⊙ `ADR-0008` kelime listesini yasaklar, gramerin **kapalı sınıflarını** serbest "
     "bırakır ve Türkçenin isimden-fiil ekleri sonludur. "
     "⚠ **TAŞINAMAZ:** `_value_token_hit`'in yanında durmalı — ayrılırsa `_syn_hit` ile "
     "arasındaki *«hangi disiplin nerede geçerli»* ayrımı bir daha yan yana okunamaz; "
     "bugüne kadar görünmemesinin sebebi tam olarak buydu. "
     "⚠ Bilinen bedel yazıldı: ünsüzle biten değerden sonra vasıta hâli de `-la` alır "
     "(*«kamyonla»*) ve **korpus bunu ÖLÇEMEZ** (soruları katalogdan üretir). "
     "Kazanç üç kanıtlı, kayıp varsayımsal."),
    ("m1a-chip-tesadufi-ayirt-ediciye-bagliydi", 13,
     "🔴🔴 **NETLEŞTİRME CHIP'İ TESADÜFİ BİR AYIRT EDİCİYE BAĞLIYDI.** `_calisan_sorgu` "
     "ölçünün yalnız **görünen adını** deniyordu; iki küp aynı adı taşıyorsa (`oee` ve "
     "`parti` → ikisi de *«fire»*) chip ancak bir küp sinonimi **tesadüfen tekil** ise "
     "ayakta kalıyordu. "
     "⊙ Ölçüldü (`M-1` denemesi, kapının kendi fikstürüyle): TABAN'da `oee`nin chip "
     "sorgusu **«vardiya fire»**'ydi; `parti`ye `vardiya` boyutu eklenince `oee` → "
     "`sorgu=None` → chip **düştü** ve `scrap`/`waste`/`defect` ailesi (6 sinonim) "
     "netleştirme yerine **Discovery'ye** kaydı. "
     "🔴 *Bir küpü yetenekli yapmak, bir kelimeyi ayırt edici olmaktan çıkarır* — ve "
     "kusur o küpün değil, **bu fonksiyonun**dı: ölçünün ÖTEKİ sinonimlerini hiç "
     "denemiyordu. `oee.toplam_fire_kg` → `hatali`·`hurda` **oee'ye özgüdür**; ayırt "
     "edici bilgi elimizde **vardı**. "
     "⚠ Yeni sözlük yazılmadı (katalogun kendi sinonimleri) ve sıra ucuzdan pahalıya: "
     "önce çıplak öteki sinonim (tek `route()`), sonra küp adıyla nitelenmiş hâli, en "
     "fazla üç küp adıyla. *Elindeki ayırt ediciyi denemeden tesadüfe güvenmek, ölçmeden "
     "varsaymaktır.*"),
    ("m9-m3-pencere-ve-turev-fisi-gecirilir", 18,
     "🔴🔴 **PENCERE VE TÜREV ALANLARI SİPARİŞ FİŞİNDEN GEÇİRİLİR.** `wren_service` "
     "kümülatifi · hareketli ortalamayı · grup-içi sırayı · oran/pay'ı **sarabiliyor**; "
     "bu satırlar olmadan o yetenek **erişilemez** kalırdı — çünkü `parse_cube_query` "
     "beyaz listesinde olmayan her alanı **düşürür**. "
     "⊙ Bu dosyanın hemen üstündeki üç yorum (`period_expr` · `measure_having` · "
     "`compare`) **aynı dersi üç kez** yazmış: *«bir alanı düşürmek, onu hiç istememekle "
     "aynı sonucu verir.»* Dördüncü kez yazılmasın diye buradalar. "
     "Ölçülen kusur (canlı, dört kanıt): `p15` *«aylık **kümülatif** fire»* → düz seri · "
     "`r18` *«**hareketli** 3 aylık ortalama»* → düz seri · `p16` *«her hattın **payı**»* "
     "→ mutlak kg · `r12` *«her biri için **en sık** sebep»* → 66 satır. Dördünde de "
     "`niyet.bilinmeyenler` düşen kelimeyi **yazıyordu**; cevap *«anlamadım»* değil, "
     "**sorulanın bir parçasına** verilmiş doğru bir cevaptı — `KÖK-3`'ün kapsamadığı "
     "bölge. ⚠ Doğrulama **dar**: taban/pay/payda bu küpün ölçüsü olmalı, kip kapalı "
     "kümede (`app/cube_operatorleri.py` — tek sahip, çünkü `cube_router` bir motor "
     "modülünü import **edemez**: `test_alan_haritasi`)."),
    ("m6-operator-de-denetlenir", 3,
     "🔴 **`parse_cube_query` OPERATÖRÜ HİÇ DENETLEMİYORDU.** `dimension` beyaz listeden "
     "geçiyor, `operator` olduğu gibi motora gidiyordu. Ölçüldü (canlı `/cube`, iki "
     "koşum): Intent-JSON şemasının modele yazdırdığı `ne` operatörü motorda **yok** ve "
     "tur HTTP **400** ile ölüyor — motorun kendi cümlesi: *«unknown variant `ne`, "
     "expected one of `eq`, `neq`, `in`, `not_in`, `gt`, `gte`, `lt`, `lte`, `contains`, "
     "`starts_with`, `is_null`, `is_not_null`»*. Denetim burada olsaydı o oy **daha "
     "ucuza** ve **loglanarak** düşerdi (`intent: whitelist REDDİ`). "
     "⚠ Filtre **düşürülmez, sorgu reddedilir**: sessiz düşürme bu depoda `compare`'ın "
     "ve `measure_having`'in başına geldi ve ikisi de aynı dersi yazdı — *«düşürülen şey "
     "geçersiz bir değer değil, var olan bir yetenekti»*. "
     "Küme `app/cube_operatorleri.py`'de **tek sahiptedir**; üç kopyası vardı "
     "(`intent_semasi` 7 üyeyle ve **yanlış** bir adla, test dosyası 12 üyeyle) ve "
     "üçü ayrışmıştı. *Bir kümenin üç kopyası, üç farklı küme demektir.*"),
    ("m7-menu-pusulasi-on-kosulu-sozlesmeye-cevrildi", 2,
     "🔴🔴 **MENÜ PUSULASI BOZUKTU — yazılmamış bir ön koşul, denetleyeni olmayan.** "
     "`_uncovered` kelimeleri `re.findall(r\"[a-z]+\", q)` ile ayırıyor; Türkçe harfler "
     "`[a-z]` dışında olduğu için ham metin kelimenin **ortasından** bölünüyordu: "
     "`müşteri`→`teri` · `bazında`→`baz`+`nda` · `çeyrek`→`eyrek`. Altı çağıranın beşi "
     "normalize gönderiyordu; `app/answer.py:181` **ham** gönderiyordu — ve orası tam "
     "olarak **telemetriyi** yazan yer. Ölçüldü (canlı kütük, 769 tur): `uncovered_words` "
     "dolu **196 satırın 115'i (%58,7)** parça içeriyor; en sık *«bilinmeyen "
     "kelimelerimiz»* `nda` (36) · `baz` (29) · `duru` (16). "
     "🔴 Görüntü kusuru değil **körlük** kusuru: menüyü hangi yönde büyüteceğimize karar "
     "verirken baktığımız TEK sinyal budur. İki satır (ikiz `measure_cube_candidates` "
     "aynı ön koşulu taşıyordu, aynı çağrı satırından ham besleniyordu). "
     "⚠ `_norm` idempotent → normalize gönderen beş çağıran **hiç etkilenmez**. "
     "*Bir ön koşulu ortadan kaldırmak, onu doğrulamaktan ucuzdur.*"),
    ("n1-ilgili-cubelar-siralanir", 10,
     "🔴 **SIRALANMAMIŞ BİR LİSTEYE DİLİM ATMAK BİR SEÇİM DEĞİL, BİR KURADIR.** "
     "`ilgili_cubelar` `schema[\"cubes\"]` **dosya sırasında** dönüyordu; üç çağıranın "
     "üçü de `[:3]`/`[:4]` diyerek onu sıralıymış gibi kesiyordu. Ölçüldü (canlı akışa "
     "geçici log, `§83.4` yol-1): `q='bu yil vardiya bazinda fire orani'` → "
     "`ilgili=['ik','isg','kalite','makine_duruslari','oee','parti']` — ölçünün gerçek "
     "sahipleri (`parti.fire_orani_yuzde`, `oee.toplam_fire_kg`) **5. ve 6.** sırada, "
     "yani kesilen kısımda. Kullanıcı bir **fire** sorusuna `brüt maaş · net maaş · "
     "işveren maliyeti` chip'i gördü. İkinci kanıt: *«son 3 ayda hangi müşteriden kaç "
     "şikayet geldi»* → `sikayet` küpü var, listede yok. "
     "⚠ **YENİ SİNYAL ÜRETİLMEDİ** (`ADR-0008`): sıra zaten hesaplanan üç şeyden okunur — "
     "ölçü sahipliği · küp-düzeyi isabet · boyut-düzeyi isabet. Eşitlikte Python'un "
     "kararlı sıralaması dosya sırasını korur, hiçbir eşitlik yeni keyfilik doğurmaz."),
    ("n4-zaman-tek-kirilimsa-satir-limiti-serisi-kesmez", 1,
     "🔴 **«SERİYİ KESER» GEREKÇESİ, SERİ OLMAYAN DURUMA DA UYGULANIYORDU.** Satır limiti "
     "zaman kovası varken **hiç** konmuyordu; oysa limit seriyi ancak seri BAŞKA bir "
     "boyut üzerinde akıyorsa keser. Zaman **tek** kırılımsa sıralanan varlık ayın "
     "kendisidir. Ölçüldü (thread T1·5, `en yüksek 3 ayı göster`): `niyet` "
     "**`üstünlük=3`** yazdı, `order` kondu, `limit` konmadı → kullanıcı **12 satır** "
     "aldı. *Sistem sayabildiği şeyi temsil edemiyordu.* "
     "⚠ Kapsam dar: `dimensions` doluyken davranış **birebir** korunur — orada gerekçe "
     "hâlâ geçerli ve `entity_limit` zaten o işin sahibi."),
    ("faz-46-konusma-fiilleri", 5,
     "🔴 **KONUŞMA FİİLLERİ BİR KONU DEĞİLDİR.** Ölçüldü: `…en yüksek olanı **analiz et**` "
     "→ `source=catalog` (**tüm menü dökümü**); `…nedenini analiz et` → *«analiz başka bir "
     "konu gibi görünüyor»*. Geri kalan tamamen anlaşılmışken soru reddediliyordu — ve "
     "düşen cümleler kullanıcının **kendi örnek tarzı**. "
     "⊙ `_ANLAT` `analiz et`'i **zaten** tanıyor; ama `sinifla()` yalnız TAKİP turunda "
     "koşar, taze soruda kapsam kapısı o sözcükleri bilinmeyen sayar. Bu, depoda ölçülmüş "
     "*«ayrıştırıcı tüketti → bilinen sayılır»* kuralının **üçüncü** örneği "
     "(`ustunluk_sozcukleri` · `_LISTE_RE` · bu). "
     "⚠ **KELİME LİSTESİ YAZILMADI:** sınıflandırıcının kendi kalıpları çağrılıyor, yoksa "
     "iki taraf ayrışır (`KAT-1`) — ki kusur tam olarak buydu, bir kat aşağıda. "
     "⚠ **TAŞINAMAZ:** kapsam kapısının bilinen-sözcük katkıları burada yaşıyor "
     "(`ustunluk_sozcukleri` kardeşi); köprü **tembel** import eder çünkü `followup.py:57` "
     "bu modülü import ediyor — modül düzeyinde bir döngü olurdu. Δ = 3 (köprü) + 2 (iki "
     "kapsam kapısı çağrısı)"),
    ("faz-43-dagilim-sarma", 1,
     "⚠ **BİR SATIRLIK SARMA — davranış değil BİÇİM.** `§43` `_LISTE_RE`'ye `dagili\\w*` "
     "ekledi (görünüm niyeti sınıfının eksik üyesi); desen tek satırda **104 karakter** "
     "oldu ve `line-length = 100` sınırını aştı, ikinci satıra sarıldı. "
     "⊙ Bu bir borç değil bir **sarma**dır; listede olması, *«neden tavan bir arttı?»* "
     "sorusunun cevabının kaybolmaması içindir. "
     "⚠ **TAŞINAMAZ:** desenin evi `liste_niyeti`'nin yanıdır; iki satırı ayırmak "
     "okunaklılığı düşürür, modüle taşımak tek bir regex için bir dosya açmak olurdu. "
     "*Bir tavan biçimsel bir satırı da sayar — saymasaydı, biçim bir kaçış yolu olurdu.*"),
    ("morfoloji/fiil-cekimi", 6,
     "🔴 **ENVANTERİN EKSİK YARISI.** `_SUFFIX_ATOMS` **ad** çekimini biliyordu (hâl · çoğul "
     "· iyelik); `üretildi`·`işlenen`·`veren` gibi **fiil** biçimleri hiç tanınmıyordu ve "
     "on iki morfoloji vakasının kalan katı buydu (`§31.2`). "
     "⊙ Eklenenler de **dilbilgisi**, alan sözlüğü değil: edilgen (`-il`), sıfat-fiil "
     "(`-en`), görülen geçmiş (`-di`), şimdiki (`-yor`), ortaç (`-dik`). "
     "🔴 **VE BU CÜMLENİN İLK HÂLİ YANLIŞ ÇIKTI — kapı onu ÇÜRÜTTÜ.** Burada önce "
     "*«kısa ekler tek başlarına tehlikeli görünür ama zincir kalanın tamamını eşlemek "
     "zorunda, yüzey iki yandan sınırlı»* yazıyordu. İlk yazımda `di`·`du`·`ti`·`tu` ve "
     "`il`·`ıl`·`ul`·`ül` de vardı; demet kapısı `_covers('mal', 'maliyeti')` → **True** "
     "verdi — yani `_covers`'ın **var olma sebebi** olan `mal ⊂ maliyeti` sessiz-yanlışı "
     "geri geldi (`i`+`ye`+`ti` zincirlendi). "
     "⊙ Yanıldığım nokta: *«iki yandan sınırlı»* bir yüzeyin **hâlâ geniş** olabileceği. "
     "İki harflik bir ek zincirde **her yere** sığar; kısalık bir güvence değil, tam "
     "tersine tehlikenin ta kendisidir. Kısa biçimler düşürüldü, yerlerine **bileşik** "
     "olanlar (`ildi`·`ilen`) kondu — aynı işi görürler, kazayla eşleşemezler. "
     "Hakem yine **korpus**: `sessiz_yanlis` artarsa geri alınır (`§26.1`). "
     "⚠ **TAŞINAMAZ:** envanter `_SUFFIX_CHAIN_RE`'nin kaynağı ve `_ek_gecerli` onun tek "
     "tüketicisi; bir modüle çıkarmak Türkçenin ek listesini iki dosyaya bölerdi."),
    ("morfoloji/ters-yon-kok", 9,
     "🔴 **ON İKİ MORFOLOJİ VAKASININ ORTAK KÖKÜ.** Katalogda **ad** var (`uretim`·`islem`), "
     "kullanıcıda **fiil** (`üretildi`·`işlenen`); `_covers` ikisini bağlayamıyor çünkü "
     "hiçbiri ötekinin öneki değil — ortak olan **kök**tür (`üret`·`işle`). "
     "⊙ Ek kümesi Türkçe **dilbilgisidir**, alan sözlüğü değil (`-im/-ım/-um/-üm`, `-me/-ma`, "
     "`-iş/-ış/-uş/-üş`): `ADR-0008` alan diline kelime listesiyle yetişmeyi yasaklar, bir "
     "dilin **ek envanterini** tanımayı değil. "
     "🔴 Soyma **yalnız katalog terimine** uygulanır: kullanıcının ne yazdığını bilmiyoruz, "
     "katalog ise **bizim beyanımız**. *Bir eşleşmeyi genişletirken, tahmin edilen tarafı "
     "değil beyan edilen tarafı esnet.* "
     "⚠ Kök **en az dört harf** — daha kısası `_covers`'ın kendi belgelediği sessiz-yanlışları "
     "(`kar ⊂ ankara`) geri getirirdi. Ve ek zinciri doğrulaması **aynen** uygulanıyor: "
     "gevşeme yok, yalnız başlangıç noktası kısalıyor. "
     "⚠ **TAŞINAMAZ:** `_covers` bu dosyanın çekirdek eşleştiricisi ve `_kok` onun **iç** "
     "yardımcısı; ayırmak, tek bir eşleşme kararını iki dosyaya bölerdi."),
    ("ustunluk/yapi-liste-degil", 5,
     "🔴 **ÜSTÜNLÜK BİR YAPIDIR, BİR LİSTE DEĞİL.** Curl'de ölçüldü (`§28.4/P2`): *«bu yıl "
     "en uzun duruş hangi makinede»* → *«uzun başka bir konu gibi görünüyor»*. `_direction` "
     "on bir kalıplık bir **sıfat listesiydi** ve `en uzun` yoktu — yarın `en kısa`, `en "
     "ağır`, `en hızlı` olacaktı (`ADR-0008`). "
     "⊙ Türkçede üstünlük **kapalı bir yapıdır**: `en` + sıfat. Yapıyı tanımak için sıfatı "
     "bilmek gerekmez; **yön** için gerekir ve o da küçük bir **kutupluluk** kümesiyle "
     "çözülür. 🔴 Böylece liste **büyümedi, küçüldü**: 11 kalıp → 1 yapı + 4 kutup (+3 "
     "yeni kutup ekleyerek 7). "
     "⚠ Ve `§22.4`'ün kuralı uygulandı: yapının tükettiği iki kelime kapsam kapısında "
     "**konu sayılmaz** — kapsam dar, yalnız yapı gerçekten eşleştiyse. "
     "⚠ **TAŞINAMAZ:** `_direction` ve kapsam kapısı aynı dosyada ve `known` yerel; ayrıca "
     "`_USTUNLUK_RE` iki tüketiciye birden hizmet ediyor (yön + kapsam). "
     "*Bir dilin yapısını tanımak, o yapının bütün örneklerini saymaktan hem kısadır hem "
     "doğrudur.*"),
    ("AJ4/measure-having-beyaz-liste", 6,
     "🔴 **GARSONUN FİŞİ EKSİKTİ.** Ölçüldü (`§AJ4`): `route()` bir sorguya **12 anahtar** "
     "yazabiliyor, LLM'e sunulan şema **7** tanıyordu — ve beyaz liste `measure_having`'i "
     "**düşürüyordu**. Yani model *«10 milyon üzeri»*yi doğru anlasa bile eşik mutfak "
     "kapısında ölüyordu: `compare`'ın başına gelen şeyin aynısı (`dashboards.py` onu elle "
     "geri eklemek zorunda kalmıştı). "
     "⚠ **TAŞINAMAZ:** beyaz liste `parse_cube_query`'nin **kendisidir** ve doğrulama "
     "`spec[\"measures\"]`'a karşı yapılıyor — o da bu fonksiyonun yerel değişkeni. "
     "🔴 Kapsam değiştiren bir alanın sessizce düşmesi, kullanıcı için **fark edilemez** "
     "bir kayıptır — `G6.5`'te kurulan *sunum vs kapsam* ayrımının aynısı."),
    ("donem/goreli-ceyrek", 14,
     "🔴 **KÖK ÇÖZÜM: bir birim, bir ailede tanınıp ötekinde tanınmıyordu.** Curl'de "
     "ölçüldü: `2. çeyrek toplam fire` ✅ (`_QUARTER_RE`) ama `geçen çeyrek toplam fire` → "
     "**dönem hiç yok**, sistem *«hangi dönem için?»* diye soruyor. "
     "⊙ `ceyrek` bu dosyada **zaten bilinen** bir takvim birimi (`_QUARTER_RE` · "
     "`_GRAN_LADDER` · `mali_takvim`); göreli dönem ailesi (`geçen ay`/`geçen yıl`) onu "
     "taşımıyordu. Bu bir kelime eklemek değil, **var olan birim kümesini tutarlı kılmak**. "
     "🔴 Hesap `mali_takvim.yil_basi`'na dayanır — Ocak'ta başlamayan mali yılda da doğru "
     "(`FAZ 2.6`'nın aynı dersi), ve ay sonu `calendar` ile (elle 30/31 yok). "
     "⚠ **TAŞINAMAZ:** dal `_prev_period_filters`'ın **birim anahtarının** içinde; bir "
     "modüle çıkarmak aynı `if/elif` zincirini ikiye bölerdi. "
     "*Bir birimi bir ailede tanıyıp ötekinde tanımamak, kullanıcıya dilin kurallarını "
     "değil bizim dosya düzenimizi öğretmektir.*"),
    ("kapsam/ayristirici-tuketti-TAKIP", 5,
     "🔴 **AYNI KURAL, TAKİP YOLUNDA — ve ilk düzeltmem YANLIŞ KATMANDAYDI.** Kuralı "
     "`route()`'un kapısına yazdım, curl ile doğruladım ve **hâlâ kırıktı**: kullanıcının "
     "bildirdiği bağlam kopması (*«en yüksek 3'ünü getir»* → *«ilişkilendiremedim»*) "
     "`deterministic_refine`'ın **kendi** kapısından geçiyor (`:1423`). "
     "⊙ İzole edildi: `refine(prev, «en yuksek 3»)` → ✅ `limit=3`; `«en yuksek 3 unu "
     "getir»` → **None**. Fark **tek kelime**: `unu`. "
     "⚠ Ve `deterministic_refine`'ın kendi şerhi bunu **zaten** uyarıyordu: *«DÖRT "
     "tüketicinin DÖRDÜNDE de dolgu sayılır — biri atlanırsa aynı soru geldiği yola göre "
     "farklı davranır.»* Beşinci bir dolgu sınıfı ekleyip yalnız birinde uyguladım. "
     "⚠ **TAŞINAMAZ:** `known` her iki fonksiyonun da **yerel** değişkeni; ortak bir "
     "yardımcı, kümeyi iki fonksiyondan da dışarı vermeyi gerektirirdi. "
     "*Bir kusuru doğru teşhis edip yanlış katmanda düzeltmek, onu ikinci kez bulmayı "
     "gerektirir.*"),
    ("kapsam/ayristirici-tuketti", 5,
     "🔴🔴 **ALTI KUSURUN TEK KÖKÜ** — canlı curl turunda bulundu: `3'ünü` · `3 tanesi` · "
     "`üretildi` · `çeyreklere` · `ocağa` · `5 milyon üzeri`. Hepsinde ayrıştırıcı ✅ ve "
     "tüketici ✅ çalışıyordu; tur, ayrıştırıcının **zaten tükettiği** kelime *bilinmeyen* "
     "sayıldığı için kapsam kapısında ölüyordu — ve kullanıcının bildirdiği **bağlam "
     "kopması** (*«bu takip mesajını ilişkilendiremedim»*) tam buydu. "
     "⊙ **Emsal ÜSTTEKİ ÜÇ SATIR**: eşik için bu bağışıklık zaten veriliyordu, `_top_n` "
     "için verilmemişti. ⚠ **TAŞINAMAZ:** `known` kümesi bu fonksiyonun yerel değişkeni ve "
     "kapı iki satır aşağıda; bir modüle çıkarmak kümeyi dışarı vermek olurdu. "
     "🔴 Yeni sözlük YOK (`_TOPN_CUE` mevcut) ve kapsam dar: yalnız `_top_n` **gerçekten "
     "eşleştiyse**. *Bir yolun iki ucu da çalışırken yol çalışmıyorsa, kusur uçlarda değil "
     "kapıdadır.*"),
    ("Ö10/gore-ayrimi", 18,
     "🔴 **KULLANICININ KENDİ VAKASI.** *«şubatta ciro ocağa göre nasıl değişti»* → "
     "`tür=**kirilim**+trend`, cevap *«şubat toplamı»*, ve `uyum` kullanıcıya *«bir kırılım "
     "istedin ama boyut taşıyamadım»* diyordu. Kullanıcı kırılım **istemedi**; `gore` bir "
     "kıyas edatıydı. *Yanlış bir beyan, sessizlikten kötüdür: sistem kullanıcıya onun "
     "söylemediği bir şeyi söylediğini söylüyor.* "
     "Δ iki kusuru birden kapatıyor: (a) `gore_donem_mi` — `gore`'den önce **adlandırılmış** "
     "bir dönem varsa o `gore` kırılım işareti değildir; (b) ünsüz yumuşaması — `ocağa` hiç "
     "tanınmıyordu (`ocak`+ünlü → `k`→`ğ`). "
     "⚠ **TAŞINAMAZ:** ölçüt `date_filters`'ın **kendisidir** ve o bu dosyada; bir modüle "
     "çıkarmak ikinci bir dönem tanıyıcısı doğururdu (`KAT-1`). Ve `_MONTH_ALT` zaten "
     "burada — ay adlarının ikinci bir kopyası, bir ayın iki numaraya çözülmesi demekti. "
     "🔴 Kapsam `Ö10`'un **kendi sözüyle** sınırlı (**ay adı**, göreli ifade değil): "
     "*«son N ay'a göre»* bu depoyu **üç kez** ısırdı ve kapı onu dışarıda tutuyor. "
     "*Bir ayrımı, ayrımın yapıldığı belgeden daha geniş kurmak düzeltme değil kumardır.*"),
    ("AJ3.3/period-expr-beyaz-liste", 2,
     "🔴 Dönem ifadesi **taşınır, çözülmez**. Beyaz listeden geçmezse alan **düşerdi** ve "
     "model dönemi söylese bile sistem duymazdı — `compare`'ın başına gelen şeyin aynısı "
     "(`dashboards.py` onu elle geri eklemek zorunda kalmıştı). "
     "⚠ **TAŞINAMAZ:** beyaz liste `parse_cube_query`'nin **kendisidir**. "
     "*Bir alanı düşürmek, onu hiç istememekle aynı sonucu verir.*"),
    ("YTD/sessiz-yanlis", 6,
     "🔴 **ÖLÇÜLEN SESSİZ-YANLIŞ.** *«yılbaşından bugüne hasılat»* → `gte 2026-08-07`: "
     "`bugune` çekimi `_current_period_filter`'ın `bugun` kuralına takılıyor ve *«bugün ve "
     "sonrası»* filtresi kuruluyordu. Kullanıcı **yıl başından bugüne** sorup **bugünden "
     "ileriye** bakan bir sayı alıyordu — rozet `◆ CUBE`, güven yüksek, sayı **yanlış**. "
     "⚠ **TAŞINAMAZ:** kural `date_filters`'ın **sırasında** durmak zorunda — "
     "`_current_period_filter`'dan önce, `_prev_period_filters`'tan sonra. Bir modüle "
     "çıkarmak, sırayı iki dosyaya bölmek olurdu ve o sıra kuralın **kendisidir**. "
     "🔴 Yeni sözlük YAZILMADI: *«yıl başı»*nın sahibi `app/mali_takvim.py` ve `yoy.compute` "
     "YTD'yi tam böyle kuruyor — burada yalnız bir **bağ** var. `ADR-0008` sözlük icat "
     "etmeyi yasaklar, sahibini çağırmayı değil."),
    ("G6.3/referans-ekseni", 16,
     "🔴 **KIYAS BİR MOD KODU DEĞİL, İKİ ADLANDIRILMIŞ UÇ.** `compare` iki değerlik bir "
     "enum'dur (`yoy`/`mom`) — motor için doğru soyutlama, **kullanıcı için değil**. "
     "*«Mart'ı şubatla kıyasla»* diyen biri `mom` duymaz. Bu Δ üç işi taşır: "
     "(a) `referans` geçişi — ⚠ **derlenemeyen GEÇMEZ**, çünkü geçseydi sorgu kıyassız "
     "çalışıp cevap kıyas etiketiyle sunulurdu (§6.1'in en ikna edici sessiz-yanlışı); "
     "(b) `blend_uyumlu` — `blend_sql`'in sözleşmesi *«çağıran garantiler»* diyor ve "
     "`G6.5`'e kadar **tek** çağıran vardı. İkinci çağıran (Intent-JSON) doğunca garanti "
     "**iki yerde** verilecekti; bir yükleme çıkarıldı. 🔴 Ve eski tek satır **eksikti**: "
     "yalnız `dimensions`'a bakıyordu, oysa **filtreler de** tüm cube'lara uygulanıyor — "
     "hedef cube'da olmayan bir boyuta filtre, iki seriyi **farklı evrenlerden** getirirdi; "
     "(c) `_kc_modul()` — `kiyas_cebiri` bizi çağırdığı için fonksiyon-içi import. "
     "⚠ **TAŞINAMAZ:** cebir zaten `app/kiyas_cebiri.py`'de; buradaki Δ o cebrin **kapısı**, "
     "ve kapı `parse_cube_query`'nin yanında durmak zorunda. *Bir garantiyi iki yerde "
     "vermek, bir gün yalnız birinde vermektir.*"),
    ("G2.9/boyut-adaylari", 9,
     "🔴 **`yuksek` DÜZEYİN KALAN FARKI: BOYUT.** `app/netlestirme.py`'nin tablosu "
     "`yuksek` için *«belirsiz ölçü/**boyutta** da sorar»* diyor. Ölçü tarafı `normal`'da "
     "bile zaten soruluyor (`ask.py`'nin kendi şerhi: modülün modeli sevk edilen "
     "davranışla çelişiyordu, kazanan sevk edilen davranış oldu) — yani `yuksek`'in "
     "gerçek deltası **boyut belirsizliğiydi** ve o **hiç uygulanmamıştı**. "
     "⚠ **TAŞINAMAZ:** `dimension_cube_candidates`, `measure_cube_candidates`'in "
     "**ikizidir** ve onun **iki satır yanında** durmak zorunda. Bir modüle çıkarmak, "
     "aynı soruya (*«bu terim birden çok cube'a mı ait?»*) cevap veren iki fonksiyonu "
     "**iki dosyaya** bölerdi — ve ikisi zamanla iki farklı cevap verirdi. "
     "🔴 Yeni tarayıcı **yazılmadı**: eşleştirmeyi `_match_dims` yapıyor, bu fonksiyon "
     "yalnız *«kaç cube sahiplendi»* diye sayıyor. *Bir soruyu iki kez sormak, iki kez "
     "cevaplamayı göze almaktır.* "
     "⚠ Ve `yuksek` **varsayılan değil**: `normal`'da davranış birebir bugünkü (`KURAL B`)."),
    ("G6/kiyas-cebiri-cagrisi", 4,
     "🔴 **MUTLAK KIYAS → GÖRELİ KIYAS.** `route()` iki dönem adını **tek aralığa "
     "çöktürüyordu**: *«mart cirosunu şubat ile kıyasla»* → `gte 2026-02-01` + "
     "`lte 2026-03-31`, yani **iki ayın TOPLAMI**. ⊙ Ölçüldü: 408 kıyas sorusunun "
     "**305**'i bu yoldan cevaplanıyordu; cebir bağlandıktan sonra **122**'si gerçek "
     "kıyas hesaplıyor, kalanı `uyum` tarafından **etiketli** (sessiz **0**). "
     "⚠ **Cebrin kendisi burada DEĞİL** — `app/kiyas_cebiri.py`'de (saf fonksiyon, 13 "
     "test). Bu dosyada kalan yalnız ÇAĞRI: kararın verileceği yer, `filters` ile "
     "`cq`'nun ikisinin birden elde olduğu tek nokta. Motor da yeni değil: `app/yoy.py` "
     "+ `shift_period_back` zaten vardı ve `compare` uçtan uca akıyordu (`viz` · "
     "`report` · `dashboards` · `contribution` · chip yolu). *Eksik olan motor değil, "
     "iki uçlu bir ifadeyi göreli bir ifadeye çeviren cebirdi.*"),
    ("G6/kiyas-niyeti+R11", 6,
     "🔴 **KIYAS FİİLİ SÖKÜLÜYORDU AMA SAYILMIYORDU.** `_KIYAS_FIIL` bu modülde 2019'dan "
     "beri var ve `strip_compare` onu sorudan **söküyor**; ama hiçbir yerde *«kıyas "
     "istendi»* diye bir **yüklem** yoktu. `TUR_KIYAS`'ın tek kaynağı `compare_mode`'du "
     "ve o **göreli** kıyastır (`yoy`/`mom`) — *«mart cirosunu şubat ile kıyasla»* iki "
     "uçludur, ona `None` der. ⊙ Ölçüldü (10 kıyas sorusu): red **3** · **SESSİZ YARIM "
     "5** · temiz 2. O beşin en kötüsü *«mart cirosunu şubat ile kıyasla»* → **1 Şubat–31 "
     "Mart TOPLAMI** döndü ve `uyum` dâhil **hiçbir kapı etiketlemedi** (`\" ile \"` "
     "`_ARALIK`'ta olduğu için `cok_donem` bastırılıyordu). "
     "⚠ **Taşınamaz:** `kiyas_niyeti` `_KIYAS_FIIL` + `_syn_hit`'in üstünde durur; bir "
     "modüle çıkarmak sözlüğü sahibinden ayırır, yani `KAT-1`'i (*«aynı kuralın iki "
     "sahibi»*) tam olarak doğurur. 2 satır yüklem + 2 satır `R11` dalı + 2 satır "
     "`return`/boşluk. `R11` niyet katmanını **çağırmaz** — ilk yazım çağırdı ve "
     "`KÖK-1 Faz 1`'in *«sıfır müdahale»* kapısı haklı olarak kırmızı verdi"),
    ("KÖK-9/tek-teshis", 12,
     "🔴 TEK TEŞHİS KAYNAĞI (denetim raporu KN-5/KÇ-5) — `teshis()`. Ölçüldü: **2 116** "
     "reddedilen soruda ham kapı kodu R10 OLMADIĞI HÂLDE tanınmayan kelime VARDI → "
     "**914 soru, %43,2**. Dağılım: R1 **646** · R2 149 · R4 61 · R9 44. Yani telemetri "
     "*«cube eşleşmedi»* diyordu, gerçek sorun kullanıcının YAZDIĞI KELİMELERDİ — ve bu "
     "kodları okuyan araçlar (`lab/r1_envanteri.py` · `lab/risk_kapsam.py`) GELİŞTİRME "
     "ÖNCELİĞİNİ ona göre çıkarıyordu. Raporun cümlesi: *kusuru gizlemekten daha kötüsü "
     "yanlış yeri işaret etmektir* — burada yanlış yer gösterilen KULLANICI DEĞİL, "
     "GELİŞTİRİCİYDİ (kullanıcı mesajı `partial_unknowns` üzerinden zaten dürüsttü). "
     "⚠ Raporun kendi önerisi (*«R10'u kapı sırasında başa al»*) UYGULANAMAZ: kapsam "
     "denetimi `known_words` ister ve o küme R1…R9'un EŞLEŞMELERİNDEN doğar — R10 en "
     "sonda çünkü ötekilerin ÇIKTISINA BAĞIMLI. Sırayı çevirmek eşleştirmeyi ikinci kez "
     "yazmak, yani 'aynı kuralın iki sahibi' sınıfını doğurmak olurdu. "
     "🔴 Doğru çözüm sırayı değil KAYNAĞI tekleştirmek: teşhis, kullanıcıya giden mesajı "
     "üreten HESABIN AYNISINDAN (`partial_unknowns`) türer. *İki sayı ayrışıyorsa çare "
     "ikisini de düzeltmek değil, birini ötekinden türetmektir.* "
     "⊙ 12 satırın 4'ü BOŞ ŞEMA TUZAĞINI kapatıyor — kapı bunu kendi yakaladı: şema `{}` "
     "gelirse `partial_unknowns` HER kelimeyi tanınmaz sayar ve teşhis sahte bir R10'a "
     "çakılırdı; telemetriyi düzeltmek için yazılan kod onu ikinci kez yanlış yapardı"),
    ("KÖK-7a/in-q-yasagi", 6,
     "🔴 `in q` YASAĞI (denetim raporu KÖK-7a). Modülde **25 yerde** sözlükler düz "
     "alt-dize (`w in q`) ile taranıyordu; `_covers` (Faz 0.4) ve `_syn_hit` (Faz D3) "
     "aynı kusurdan AYRI AYRI kurtarılmış, ama kural ZORUNLU KILINMAMIŞTI. Ölçülen "
     "sahte eşleşmeler: `trendyol satislari`→`trend` (müşteri adı soruyu ZAMAN SERİSİNE "
     "çeviriyordu) · `bu ayrica`→`bu ay` (dönem filtresi) · `uygun fiyat`→`gun`. "
     "Bu 6 satır TAŞINAMAZ: `_herhangi`+`_gecenler` (4) — 25 çağrı yerini tek bir "
     "biçime indirger ve grep/AST kapısının tarayabileceği yüzeyi oluşturur; "
     "`_DUN_RE` (1) ve `ku` atomu (1). "
     "⚠ Yardımcılar YENİ KURAL TAŞIMAZ — kararı `_syn_hit`→`_ek_gecerli` verir "
     "(çekimin tek sahibi); var olma sebepleri kuralı ZORUNLU kılmaktır. "
     "⊙ `ku` atomu ölçüyle zorunlu oldu: yasak uygulanınca `bugunku ciro` dönem "
     "filtresini kaybetti — alt-dize taraması biçimbirim tablosundaki bir DELİĞİ "
     "örtüyormuş. `_DUN_RE` ise ters yönün kanıtı: `dun`+`ya` geçerli bir zincir olduğu "
     "için genel çekim denetimi `dünya geneli ciro`ya dün filtresi taktı — kapalı sınıf "
     "kelime kendi sınırını taşımalı"),
    ("KÖK-7e/ay-cekimi", 4,
     "🔴 AY ÇEKİMİ TEK SAHİPTEN (denetim raporu KÖK-7e). Ölçüldü: `_AY_ADI_RE` ay "
     "adından SONRA `\\b` istiyordu ve Türkçenin en doğal söyleyişlerini GÖRMÜYORDU — "
     "60 çekimin 11'i (%18) geçiyordu (`ocakta`·`martta`·`subattan` hepsi kaçıyordu). "
     "🔴 Ve asıl kusur kalıpta değil İKİ SAHİPTE: tarih ÇÖZÜCÜSÜ `ocakta`yı doğru "
     "çözüyordu ([2026-01-01, 2026-01-31]) ama KAPSAM KAPISI kendi ay kalıbını taşıyor "
     "ve görmüyordu → soru R10 ile reddediliyordu. Sistem tarihi biliyor ama bildiğini "
     "bilmiyordu. "
     "Bu yedi satır TAŞINAMAZ: kalıbın kendisi (2) ve İKİ tüketicideki çekim denetimi "
     "(5). Denetimin kararı zaten `_ek_gecerli`de — çekimin TEK sahibi; buraya giren "
     "yalnız ÇAĞRI. Yeni ek listesi YAZILMADI (ADR-0008). "
     "⊙ Sonuç: %18 → **%100 (60/60)**, üç yanlış-pozitif kapısı temiz "
     "(`mart ayakkabi` · `kargo` · `ekim ekipmani`). "
     "⟳ **7 → 4 (KÖK-7c): PAY İNDİ.** 7c, 7e'nin geride bıraktığı ÖLÜ ikinci ay "
     "taramasını (`\\b(month)\\b(\\s+ayi\\w*)?`) sildi — o kalıp `_ek_gecerli` süzgecini "
     "ATLAYARAK eşleşiyordu, yani ölü ama sahipsiz değildi. 🔴 Meta-kapı boşluğu "
     "(3 satır) HEMEN kırmızı verdi; payı indirmemek, temizlikle kazanılanı sessizce "
     "yeni büyümeye açardı. *Bir tavanı bir temizlikten sonra indirmemek, o temizliği "
     "geri almakla aynı kapıyı üretir.*"),
    ("faz-2.2b/borc11", 5, "grain-farkında çapraz-cube geçişi — ölçü eşlemesi ADLA değil "
                           "KAVRAMLA yapılıyor. 🔴 Taşınabilir olan HER ŞEY taşındı: "
                           "`olcu_eslemesi` + `grain_uyarisi` `app/cekirdek.py`'ye "
                           "(varyant bilgisi ÇEKİRDEK KATMANIN sorusudur, router'ın "
                           "değil); burada kalan yalnız çağrı ve döngünün yeni şekli"),
    ("9164806", 13, "0.18 · metrik kaydı = hakem — `_match_cube`'un İLK satırı "
                    "`schema['metrik_kaydi']`'na bakar; kayıt yoksa davranış birebir bugünkü"),
]
#: 🔴 **AYRI LİSTE — ve bu bir ÖLÇÜM ARACI DÜZELTMESİDİR.** İlk tasarımda dosya tavanı
#: `TAVAN_ASK_KOD + 1259` idi; yani **modül düzeyine** eklenen bir satır için `MUAFIYET_
#: ASK_KOD`'a yazmak gerekirdi ve o liste **aynı anda `ask()` gövdesinin tavanını da**
#: yükseltirdi. `ask()` bugün tam tavanında (1147/1147) duruyor — modül düzeyindeki bir
#: uç kaydı ona **bedava pay** açardı. *Bir tavanı yanlışlıkla yükselten muafiyet, muafiyet
#: değil sessiz bir tavan artışıdır* (bu dosyanın kendi cümlesi). Dosya muafiyeti bu yüzden
#: **ayrı** sayılır ve `ask()` tavanına **dokunmaz**.
MUAFIYET_ASK_DOSYA = [
    ("aa2-red-yaninda-rapor-dosya", 6,
     "🔴 `§AA2`'nin dosya-toplamı payı — `ask()` muafiyetinin aynısı ve **aynı "
     "gerekçeyle**: gövde `contribution.yanindaki_rapor`'a taşındı, burada yalnız çağrı "
     "kaldı. Toplam tavanı `ask()` tavanını içerdiği için ikisi birlikte hareket eder. "
     f"`sha=858336a`"),
    ("d2k-oylama-esigi-kisayolu", 10,
     "🔴🔴 **`§D2/K` — «TEK ADAY» KISAYOLU EŞİĞİ ATLIYORDU.** `D2` (`oylama_paydasi`) bir "
     "**yalanı** kapatmıştı: 1 cevap + 2 çekimser, payda `cands` ile **%100 «oy birliği»** "
     "görünüyordu; bayrak paydayı düzeltti ve makbuz artık **%33** yazıyor. Ama **kararı** "
     "düzeltmedi: `if len(votes) == 1 or agreement >= 2/3` dalı eşiği **hiç sormadan** "
     "dönüyordu. "
     "⊙ Canlı kanıt (curl): *«bunu nasıl yorumlarsın»* → iz `self-consistency %33 (3 "
     "örnek)` **ve cevap verdi**. Yani makbuz *«%33 uyum»* yazarken sistem **oy "
     "birliğiyle** davranıyordu — raporun `D2` için yazdığı cümle birebir geçerli: "
     "*şüphenin en yüksek olduğu durum, sistemin en emin göründüğü durumdu.* "
     "⊙ Δ = 10: değişen **tek satır** (`or len(votes) == 1` kalktı); kalan 9 satır o "
     "kararın **neden** değiştiğini taşıyan gerekçedir ve bu dosyanın kendi kuralı onu "
     "zorunlu kılar — *gerekçesiz bir sayı muafiyet değil, sessiz bir tavan artışıdır.* "
     "⚠ **TAŞINAMAZ:** karar `_select_consistent`'ın oylama satırıdır; oyu sayan yerden "
     "başka bir yerde verilemez. "
     "⚠ `KURAL B` **bedavaya** sağlandı: bayrak kapalıyken payda `cands`'tir ve tek "
     "adayda oran **her zaman 1.0** → eski davranış birebir korunur; yeni koşul yalnız "
     "bayrak açıkken ısırır. Kapı: `test_oylama_esigi_kisayolu.py` (6). "
     "*Bir sayıyı dürüst yazmak, ona göre davranmakla aynı şey değildir.* "
     f"`sha=72e7e3b`"),

    ("o19-cokluk-netlestirmeyi-erteler", 5,
     "🔴🔴 **`O-19` — AYRIK ÖLÇÜ KÜMELERİ BİR BELİRSİZLİK DEĞİL, BİR ÇOKLUKTUR.** "
     "⊙ Ölçüldü (canlı `IV` turu, iki soru): *«iade oranı en yüksek 3 müşteriyi **ve** "
     "ciro paylarını göster»* ve *«hangi vardiyada kalite sorunları yoğunlaşıyor»* → "
     "ikisi de `%50 uyum · eksen=measures` ile **cevapsız** kaldı. Oyların hikâyesi: "
     "biri **çekimser** (*«tek cube ile olmaz»* — haklı), ikisi **farklı** küplerden "
     "**farklı** ölçüler seçiyor. Üç oy da doğru: soru gerçekten **iki parçalı** ve "
     "doğru cevap bir **plandır**. "
     "⊙ Δ = 5: ilklendirme (1) · çokluk dalı (2: `if` + saklama) · plan cevap veremezse "
     "ertelenen chip (2: `if` + `return`). "
     "⚠ **TAŞINAMAZ:** karar `ask()`in **akış sırasıdır** — netleştirmeyi erteleyip "
     "planı denemek, sonra ertelenmişi konuşturmak. Dışarı almak, bir dalın *nerede* "
     "döndüğünü iki dosyaya bölerdi. Yüklemin kendisi (`uyum.cokluk_mu`) **taşındı** ve "
     "tavan yalnız akış satırlarını sayıyor. "
     "⚠ **`§101.1` disiplini yüklemde:** kesişen kümeler çokluk sayılmaz "
     "(`{ciro}` ↔ `{ciro, fire}` bir zenginlik farkıdır, iki istek değil) ve "
     "`eksen=cube` (aynı ölçü, iki sahip) **aynen sorar**. "
     "⚠ **KAYIPSIZ:** plan cevap veremezse **birebir aynı** chip konuşur — en kötü "
     "durum bugünküyle bayt bayt aynı. `sha=7fbf8a2`"),
    ("faz-75-salinim-yonetimi", 5,
     "🔴 **SALINIMI YÖNETMEK, DALLARI YAMAMAKTAN ÖNCE GELİR.** Üç sondajla ölçüldü: "
     "**aynı soru, aynı sistem, aynı dakika** — bazen tam cevap, bazen netleştirme "
     "(`3 oy · 2 farklı aday · kazanan 1 oy` → *«hangi ölçüyü istiyorsun»*; `3 oy · 1 "
     "aday · kazanan 3 oy` → 11 satır). Kusur **anlama** değil **eşik**: `k=3`'te `2/3` "
     "pratikte *«üç örneklemin ikisi birebir aynı JSON»* demektir. "
     "⊙ Δ = 5: bayrak çözümü (3 satır `try/except`) + çoğunluk dalı (2: `if` + `return`); "
     "`_log` satırı ize yazılan **dereceyi** görünür kılar. "
     "⚠ **TAŞINAMAZ:** karar `_select_consistent`'in **kendi dönüş sözleşmesidir**; "
     "dışarı almak, oy sayımıyla oyun sonucunu iki dosyaya bölerdi. "
     "⚠ `KURAL B` + korpus hakem (`§73.7`: yeşil bir veto, yeşil bir karar değildir)."),
    ("gosterim-suzgeci/20", 20,
     "🔴 **İKİ SORU, İKİ LİSTE.** Curl'de ölçüldü: *«bu yıl hangi müşteri en çok iade etti»* → ***«hangi etti» kısmını anlayamadım***. Kullanıcı ne yaptığını anlamaz: `hangi` bir soru sözcüğü, `etti` bir yardımcı fiil — ikisi de **sorusunun konusu değil**. ⊙ `unknown` **kapsam kapısının** listesidir (*kaç kelimeyi açıklayamadım*); gösterim başka bir sorunun cevabıdır (*neyi anlamadım*). 🔴 Kapı onları **saymak zorunda**: dolgu sınıfına eklemek denendi ve `sessiz_yanlis` **12 → 13** çıktı (`§26.1`). Yani **sayılmalı ama gösterilmemeli**. ⚠ **TAŞINAMAZ:** süzgeç `unknown` ile `note`'un **ikisinin birden** elde olduğu tek yer; yardımcı (`_islev_sozcugu`) zaten modül düzeyine çıkarıldı. *Aynı kelime bir kapıda kanıt, bir cümlede gürültü olabilir.*"),
    ("kok-cozum/capa-degerleri", 7,
     "🔴 **KÖK ÇÖZÜM — kelime listesi SİLİNDİ.** Önceki sürüm `_KARSILASTIRMA` listesi + 4-kelime eşiği taşıyordu; çalışıyordu ama **tikel**di (*«yıkama neden geride kaldı»* · *«3. vardiya neden zayıf»* yine düşerdi, her biri listeye bir kelime daha eklettirirdi — `ADR-0008`). Yerine **yapısal bağ**: takip sorusu ekrandaki raporun bir **satırını** adlandırıyorsa bağlıdır. ⊙ Bu ayrım *«…olur genel olarak»* sorusunu **kendiliğinden** dışarıda bırakır — eşiğe gerek kalmaz. ⚠ **TAŞINAMAZ:** hesap **zaten taşındı** (`app/context.py::capa_degerleri` — *«ekranda ne var»* bağlam katmanının sorusu, sınıflandırıcının değil). Burada kalan yalnız çağrı ve `try/except`: `body.cube_query` ile `body.previous_result`'ın **ikisinin birden** elde olduğu tek yer. *Bir kusuru gördüğü yerde yamamak, sınıfını görmemenin en pahalı biçimidir: her yeni örnek yeni bir yama ister ve yamalar birbirini tanımaz.*"),
    ("sinir-llm-oncesi/4", 4,
     "🔴🔴 **KUSUR BENİMDİ ve canlı curl ÖLÇTÜ.** `§AJ3` ile modeli yorumlamaya **istekli** hâle getirdim (dönem alanı · karşı ağırlık · örnekler). Yan etki: *«gelecek ay ciro tahmini»* `cube+llm` ile **30 satır GEÇMİŞ veri** döndü — not yok, sınır yok, **sessiz-yanlış**. Yani modeli konuşkan yapmak, sınır kapısını **daha erken** gerektirdi. ⚠ Kapsam dar: `kapsam_disi` **beyan edilmiş** sınıfları tanır (tahmin · yargı · iki-cube · olumsuzluk), tahmin yürütmez; `None` dönerse merdiven aynen devam eder — bu bir **kesme** değil bir **öncelik**. ⚠ **TAŞINAMAZ:** karar `route_hit is None` ile Intent dalının **arasında** durmak zorunda. *Bir basamağı daha yetenekli yapmak, ondan önceki sınırı daha erken sormayı gerektirir — yoksa yeni yetenek, ilk olarak yapamadığımız şeyi yapmayı dener.*"),
    ("sinir-kismi-anlama/3", 3,
     "🔴 **CANLI CURL TURU 2: *«anlamadım»* ile *«yapamıyorum»* aynı cevabı hak etmez.** Ölçüldü: *«gelecek ay ciro tahmini»* → *«gelecek tahmini kısmını anlayamadım»*. Dürüst ama **yanlış cümle**: sistem o kelimeleri anlıyor, **yapamadığı** onların istediği şey. ⚠ *«Anlamadım»* kullanıcıyı **yeniden yazmaya** çağırır, *«yapamıyorum»* sınırı söyler; yanlışını seçmek kullanıcıyı **sonuçsuz bir döngüye** sokar. ⚠ **TAŞINAMAZ:** kontrol bu dalın **girişinde** durmak zorunda — chip/etiket üretimi başladıktan sonra sorulursa sınır beyanı o chip'lerin altında kalır. Sözleşme (`_guvenli_kapsam_disi`) zaten **tek** yerde; burada kalan yalnız çağrı. *Anlaşılmayan bir kelime ile yapılamayan bir istek aynı cevabı hak etmez.*"),
    ("sinir-once/6", 6,
     "🔴 **CANLI CURL BULGUSU: sınır GEÇ konuştu, yani hiç konuşmadı.** *«gelecek ay ciro tahmini»* → *«toplam ciro çıkarabilirim — hangi dönem için?»*. Kullanıcı **gelecek** sordu, sistem **geçmiş** için dönem soruyor; bir dönem söylerse sistem **yapamadığı şeyi yapmış gibi** sayı döner. ⊙ Sınır **vardı** (`kapsam_disi` → `forecast`), kapısı bu daldan çok sonra duruyordu. ⚠ **TAŞINAMAZ:** kapı yukarı **taşınmadı** — yalnız dönem netleştirmesi ona soruyor. Taşımak `route()`/Intent-JSON'un cevapladığı soruları da sınır beyanına çevirebilirdi ve o takas **ölçülmedi**. *Bir sırayı düzeltmek, sırayı baştan yazmak değildir.* *Bir sınırı bilmek, onu doğru anda söylemekten farklıdır; geç söylenen sınır, söylenmemiş sınırdır.*"),
    ("garson/DA-5+DA-10", 7,
     "🔴 İKİ DENETİM BULGUSU, ikisi de `ask()` gövdesinde ve ikisi de TAŞINAMAZ. "
     "**(a) `DA-5` — `G2`'nin kill-switch'i (`diyalog_bellegi`).** Katman inmişti, bayrağı "
     "YOKTU: GERİ AL sözleşmesi (*«off → davranış birebir bugünkü»*) uygulanamaz "
     "durumdaydı. `MIMARI §9.11`: *bir kill-switch yalnız KODDA varsa yarımdır.* Kesme "
     "noktası **girişte** ve TEK: durum sunucuya hiç girmezse `devam_edilebilir(None)` "
     "zaten `None` döner. Bir modüle çıkarmak, bir `if`'i bir dolaylamaya çevirirdi. "
     "**(b) `DA-10` — dönem netleştirmesi katalogdan okuyor.** `soz.py:19`'un kendi kuralı "
     "(*«ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR»*) katalogda yazılıydı ama üretimde "
     "`_PERIOD_TEXT` sabiti basılıyordu; katalog girdisinin **hiç çağıranı yoktu**. "
     "⊙ Ağırlığı ölçülü: netleştirmelerin **%79'u** dönem sorusudur (`donem_capasi.py:8`). "
     "`{ne}` yuvasını `temellendirme` doldurur — ikinci bir adlandırıcı yazmak `KAT-1` "
     "olurdu; yani satırlar burada, **karar noktasında** kalmak zorunda."),
    ("AJ0/merdiven-baglantisi", 3,
     "🔴 AJ0 kısa devre yasağının MODÜL-DÜZEYİ bağlantısı: `app/merdiven.py`'den üç ad "
     "(`Merdiven` · `ZORUNLU` · `ADAY_IZI`) import edilir. Mekanizmanın TAMAMI o "
     "modülde; `ask.py`'de kalan yalnız isimlerin bağlanması. ⚠ Sabitleri `ask.py`'de "
     "tanımlamak, işaretçiyi iki sahibe açardı — dönem kapısı onu TAKAR, merdiven "
     "OKUR ve ikisi ayrışırsa zorunlu netleştirme sessizce adaya düşerdi"),
    ("KÖK-1/niyet-izi-yardimcisi", 5,
     "🔴 `_niyet_izi()` MODÜL-DÜZEYİ yardımcısı — niyeti çözer ve tek satırlık izi "
     "döndürür. `ask()`in İÇİNE yazılsaydı gövde tavanını aşardı ve `ask()` zaten tam "
     "tavanında; dışarı alınması hem tavanı korur hem DOĞRU YERDİR (bir GÖZLEM bir "
     "cevaplama adımı değildir — `_netlestirme_duzeyi` · `_belirsizlik_beyani` · "
     "`_turetme_adaylari` ile aynı gerekçe). "
     "⚠ ASLA FIRLATMAZ: bir gözlem, gözlediği cevabı düşüremez"),
    ("KÖK-7d/turetme-adaylari", 14,
     "🔴 `_turetme_adaylari()` MODÜL-DÜZEYİ yardımcısı — bir dürüst reddin yanına konacak "
     "türetme chip'lerini hesaplar. `ask()`in İÇİNE yazılsaydı gövde tavanını aşardı ve "
     "`ask()` zaten tam tavanında; dışarı alınması hem tavanı korur hem DOĞRU YERDİR — "
     "bir ÖNERİ hesabı bir cevaplama adımı değildir (aynı gerekçe `_netlestirme_duzeyi` "
     "ve `_belirsizlik_beyani` muafiyetlerinde de yazılı). "
     "⚠ Taşınabilir olan HER ŞEY `app/turetme.py`'de; burada kalan yalnız ŞEMAYI ÇÖZMEK "
     "ve ÇAĞIRMAK. Şema okunamazsa boş liste döner — *bir öneri, önerdiği şeyden daha "
     "kırılgan olmamalıdır*"),
    ("KÖK-9/belirsizlik-beyani", 20,
     "🔴 `_belirsizlik_beyani()` MODÜL-DÜZEYİ yardımcısı — çok-sahipli bir terimde cevaba "
     "alternatif chip'ini ve beyan notunu ekler. `ask()`in İÇİNE yazılsaydı gövde tavanını "
     "20 satır aşardı ve `ask()` zaten tam tavanında duruyor; dışarı alınması hem tavanı "
     "korur hem DOĞRU YERDİR — bir cevabın ZENGİNLEŞTİRİLMESİ bir cevaplama ADIMI değildir "
     "(aynı gerekçe `_netlestirme_duzeyi` muafiyetinde de yazılı). "
     "⚠ Ve taşınabilir olan HER ŞEY zaten taşındı: adaylar `app/metrik_kaydi.py`, etiket/"
     "not/chip `app/belirsizlik_chipi.py`; burada kalan yalnız İKİ SÖZLEŞMEYİ BAĞLAMAK — "
     "`_match_measure`in eşleşen terimi ile kaydın adayları. "
     "⚠ Ve bir GERİ AL şartı: `metrik_kaydi` bayrağı kapalıysa şemada anahtar yoktur, "
     "fonksiyon ilk satırında çıkar ve davranış BİREBİR bugünküdür — bir özelliğin geri "
     "alınması bir kod değişikliği gerektirmemelidir"),
    ("faz-5.16", 17, "`_netlestirme_duzeyi()` modül-düzeyi yardımcısı: tenant ayarını "
                     "okur ve `netlestirme.duzey()`e verir. 🔴 `ask()`in İÇİNE "
                     "yazılsaydı gövde tavanını 17 satır aşardı; dışarı alınması hem "
                     "tavanı korur hem doğru yerdir — bir AYAR okuması bir cevaplama "
                     "adımı değildir. ⚠ Okunamazsa `normal` döner: varsayılan BUGÜNKÜ "
                     "davranıştır ve bir ayar okunamadığında davranışı değiştirmek "
                     "sessiz bir kapsam kaybı olurdu"),
    ("o4-planlayici-ile-garson-ayni-kisi", 2,
     "🔴 **`FAZ O-4` — PLANLAYICI İLE GARSON AYNI KİŞİ.** İki satır: `plan_garson` "
     "importu (1) ve `_garson = _plan_garson.sarmala(...)` (1). ⊙ Neden bu iki satır "
     "`ask.py`'den çıkarılamaz: `_select_consistent`'a **hangi nesnenin** verileceği "
     "kararıdır ve o çağrı burada. ⊙ Alternatif ölçüldü ve daha PAHALI çıktı: "
     "`_select_consistent`'ın gövdesini plan-farkında yapmak, bir OYLAMA yordamına ne "
     "oyladığını öğretmek olurdu — oysa sarmalayıcı ona bugünkü sözleşmeyi konuşuyor ve "
     "yordam **hiç değişmedi**. ⚠ Bayrak çözümü bilerek `ask.py`'de DEĞİL: bayrak adı "
     "`plan_garson.BAYRAK`'ta tek sahipli kalsın ve `sarmala()` kapalıyken **nesnenin "
     "kendisini** döndürebilsin diye (`KURAL B`'nin kanıtı «aynı davranış» değil «aynı "
     "nesne»dir). *Bir kararı doğru yere koymanın bedeli iki satırsa, o bedel tavandan "
     "ödenir — kararın yerinden değil.*"),
    ("faz-1.12", 9, "AI Act Md.14 durdurma ucu — karar+yazma `app/ask_jobs.py`'de; `ask.py`'de "
                "kalan yalnız UÇ KAYDI (dekoratör 2 + imza 1 + delege 1 + `ask_jobs` "
                "importu 1), `_bg`'nin iki dalındaki iptal kontrolü (2) ve akışın `iptal` "
                "olayı (3 — durdurma `hata` değildir ve dalsız akış 6 dk açık kalırdı). "
                "Bir HTTP uç kaydı router modülünden çıkarılamaz; çıkarmak `/ask/jobs` "
                "kaynağını iki dosyaya bölerdi"),
    ("wb-ayni-kume-iki-secenek-degildir", 2,
     "🔴🔴 **KULLANICIYA CEVAPLAYAMAYACAĞI BİR SORU SORULUYORDU.** Ölçüldü (`W5` — *«her "
     "vardiya için en çok duran makineyi bul»*): `not = «Hangi kırılımı istiyorsun?»` ve "
     "chip'ler `[\"makine × vardiya\", \"vardiya × makine\"]` — **aynı küme**, yalnız "
     "sütun sırası farklı. ⊙ Sütun sırası bir sunum tercihidir, bir niyet ayrımı değil; "
     "`_canon_cq` bunu **zaten biliyor** (`dimensions`'ı sıralıyor) ama dedup etiket "
     "**dizisine** bakıyordu — `KAT-1`: aynı gerçeği iki modülden biri normalleştiriyor, "
     "öteki normalleştirmiyordu. ⊙ `§T1`'in doğal devamı (*«bir soruyu sormak için önce "
     "İKİ FARKLI cevap gerekir»*): `§T1` birebir aynı etiketleri eledi, sırası farklı "
     "olanlar süzgeçten geçiyordu. Elenince chip 1'e düşer ve `§T1` dalı devralıp CEVAP "
     "VERİR — yani bu iki satır kendi başına cevap üretmiyor, var olan doğru dalın önünü "
     "açıyor. ⚠ Gösterilen etiket ilk adayın sırasını korur: normalleştirme yalnız "
     "*«aynı mı»* sorusuna uygulanır."),
    ("x1-tarih-sabit-kodluydu-kodun-kendi-ongordugu-kusur", 2,
     "🔴🔴 **`_resolve_period` «tarih» ADINI SABİT KODLUYORDU — ve bunu KODUN KENDİSİ "
     "ÖNGÖRMÜŞTÜ.** Kardeş dalın yorumu bugüne kadar şunu yazıyordu: *«`_resolve_period` "
     "doğrudan çağrılMADI çünkü o «tarih» adını SABİT kodluyor; zaman boyutu farklı adlı "
     "bir cube'da VAR OLMAYAN BİR KOLONA filtre yazardı.»* Kardeş dal kendini korudu, "
     "`§48` dalı aynı fonksiyonu DOĞRUDAN çağırdı. "
     "⊙ Ölçüldü (`X5` Fransızca · `X19` Rusça — *«cette année»* / *«в этом году»*): cq "
     "`enerji_makine`'ye çözüldü, dönem filtresi `tarih`'e yazıldı — o küpün zaman boyutu "
     "**`donem_tarih`**. Sonuç iki katmanlı: filtre YANLIŞ KOLONA yazıldı, ve dönem kapısı "
     "`donem_tarih`'te filtre bulamayıp *«hangi dönem için?»* dedi — kullanıcı dönemi "
     "SÖYLEMİŞTİ, cevap TAŞIYORDU, sistem yine sordu. "
     "⚠ Ve bu kusuru KENDİ DÜZELTMEM görünür kıldı: `§W-A` `period_expr`'i oylamadan sağ "
     "çıkarınca bu dal daha sık koşar oldu. *Bir yolu açmak, üstündeki çukuru devralmaktır.* "
     "⚠ İki satır: imza (`time_dim` parametresi) — gövde sabitleri parametreye ÇEVRİLDİ, "
     "eklenmedi. Varsayılan `\"tarih\"` → çağıranların hepsi bayt bayt aynı. Sondaj 3/3."),
    ("bbb-bos-cevap-guardi-ask-DISINDA", 16,
     "🔴🔴 **`§BB-B`'nin gövdesi `ask()` DIŞINDA — ve orada olması kapının kendi "
     "TALİMATIDIR.** `test_ASK_IC_FONKSIYON_SAYISI_ARTMIYOR` kırmızı verdi ve cümlesi "
     "şuydu: *«yeni bir yardımcı gerekiyorsa MODÜL DÜZEYİNE al: saf bir fonksiyon test "
     "edilebilir, closure edilemez»*. O ölçütün muafiyet listesi BOŞTUR ve boş kalması "
     "bir başarıdır — bu yüzden borç `ask()`'e değil dosyaya yazıldı. "
     "⊙ Ve taşıma fonksiyonu GERÇEKTEN saflaştırdı: tek bağımlılığı `body.question`'dı, "
     "artık bir parametre. Kapsam paylaşmıyor, tek başına test edilebilir. "
     "⚠ **TAŞINAMAZ (dosya dışına):** `AskResponse`'un boşluk tanımı `/ask`'in "
     "sözleşmesidir; başka bir modüle koymak, cevabın ne olduğunu bilen yerden "
     "uzaklaştırırdı. `_canon_cq`'nun yanında duruyor — ikisi de saf, ikisi de bu ucun "
     "değişmezlerini taşıyor. "
     "*Bir kapı yalnız hayır demez, bazen nereye koyacağını da söyler.*"),
    ("v2-oylama-zenginligi-cezalandiriyordu", 49,
     "🔴🔴 **OYLAMA, ZENGİN CEVABI KENDİ ZENGİNLİĞİ YÜZÜNDEN ELİYORDU.** Kanonik anahtar "
     "**tam `cq`** olduğu için `order`/`limit`/`pencere`/`turev` yazmayan iki oy "
     "birbiriyle **bedavaya** uyuşuyor, onu yazan tek oy yalnız kalıyordu. "
     "⊙ Ölçüldü (V turu, konteyner logu, on Intent turu): kazanan 3 oy → 1 kez · "
     "2 oy → 1 kez · **1 oy → 7 kez**. Yani uzlaşma kural değil istisna, ve kurulduğunda "
     "**en yalın okuma** kazanıyor. Canlı bedeli: `V13` *«azalan sırada ilk 5»* → "
     "`order`+`limit` düştü, **11 satır**; `V14` *«yüzde kaçını»* → `pencere:pay` düştü. "
     "⟳ `§T1` bu kökü **teşhis etmişti** ama semptomu yamadı (*«anlamca aynıysa ilkini "
     "al»* — ilki KEYFÎ bir oydur, ve V13'te `order`'ı gören oy tam da atılan oydu). "
     "⊙ Ayrım: fazladan alan yazmak bir **anlaşmazlık değil, ek bilgidir**; anlaşmazlık "
     "aynı alana **iki farklı değer** yazmaktır. "
     "⚠ **`ask()` DIŞINDA, modül düzeyinde** (üç saf fonksiyon) ve `_canon_cq`'nun tam "
     "yanında — ikisi **aynı sorunun iki cevabıdır**; ayrı dosyalara konsalardı "
     "hangisinin ne saydığı bir daha yan yana okunamazdı. "
     "⚠ Fail-closed: çelişkide alan **düşer** (en kötü durum bugünkü davranış) ve "
     "referansları kazananın sözlüğüne oturmayan alan **alınmaz**."),
]
#: 🔴 `0619bfd` (0.22 · `migration_trace` `UnboundLocalError`) ham satırda **+8** getirdi
#: ama **kod satırında 0**: bildirim `if` bloğundan gövde başına **TAŞINDI**. Bir taşıma
#: borç değildir ve muafiyet listesinde yeri yoktur — burada yazılı olması, *"neden bu
#: madde listede yok?"* sorusunun cevabının kaybolmaması içindir.

TAVAN_ASK_KOD = TABAN_ASK_KOD + sum(d for _s, d, _g in MUAFIYET_ASK_KOD)
TAVAN_CUBE_ROUTER_KOD = (TABAN_CUBE_ROUTER_KOD
                         + sum(d for _s, d, _g in MUAFIYET_CUBE_ROUTER_KOD))
#: Dosya tavanı: FAZ 0 ÖNCESİ dosya kodu (2394) − o günkü `ask()` kodu (1135) = 1259 taşınabilir
#: pay, artı `ask()` muafiyetleri (taşınabilir), artı **modül düzeyi** muafiyetleri (ayrı liste).
#:
#: 🔴 **1259 → 1217 (2026-08-05): PAY İNDİ, çünkü BOŞLUK BÜYÜMEYİ DURDURMAZ.**
#: `_attach_viz` → `app/gorsel_ekleme.py` ve `_queue_discovery_job` →
#: `app/discovery_kuyrugu.py` taşındıktan sonra dosya 2498'den **2377**'ye düştü ve
#: tavanda **42 satır boşluk** kaldı. `cube_router`'da meta-kapı aynı boşluğu kırmızı
#: vermişti; burada meta-kapı yok ama **kural aynı**: *bir tavanı bir taşımadan sonra
#: indirmemek, kazanılan payı sessizce yeni büyümeye açar.*
#:
#: ⚠ `ask()` tavanı **1151'de bırakıldı** (bugün 1150, boşluk **1**): gövde payı zaten
#: sıkı ve onu 1150'ye çekmek, bir sonraki tek satırlık düzeltmeyi bir muafiyet
#: tartışmasına çevirirdi. *Bir tavan sıfır boşlukla değil, ANLAMLI bir boşlukla sıkıdır.*
#: 🔴 **TEK KOPYA.** Bu sayı iki yerde yazılıydı — burada ve `test_MUAFIYETLER_GEREKCELI
#: _ve_TOPLAMI_TUTUYOR`'un içinde — ve indirdiğimde **ikincisi bayatladı**: kapı
#: `2410 + 9 == 2377` diye kırmızı verdi. *Tanımsız bir sayının iki kopyası, iki ayrı
#: bayatlama yüzeyidir* (bu dosyanın kendi cümlesi, bu kez kendi üstünde ölçüldü).
TASINABILIR_PAY = 1217
TAVAN_ASK_DOSYA = TAVAN_ASK_KOD + TASINABILIR_PAY + sum(d for _s, d, _g in MUAFIYET_ASK_DOSYA)


# ── ÖLÇÜM ARACI ──────────────────────────────────────────────────────────────

def _belge_satirlari(agac: ast.AST) -> set[int]:
    """Docstring gövdelerinin kapladığı satır numaraları."""
    out: set[int] = set()
    for n in ast.walk(agac):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            ilk = n.body[0] if n.body else None
            if (isinstance(ilk, ast.Expr) and isinstance(ilk.value, ast.Constant)
                    and isinstance(ilk.value.value, str)):
                out.update(range(ilk.lineno, ilk.end_lineno + 1))
    return out


def kod_satiri(kaynak: str, bas: int | None = None, son: int | None = None) -> int:
    """Yorum · docstring · boş satır **hariç** satır sayısı.

    ⚠ **Ölçüm aracının kendisi de bir bağımlılıktır** (MIMARI §6.4). Bu fonksiyon sessizce
    değişirse tavan da sessizce değişir — bu yüzden `test_OLCUM_ARACI_KENDINI_OLCUYOR`
    onu sabit bir girdiyle kilitler.
    """
    agac = ast.parse(kaynak)
    belge = _belge_satirlari(agac)
    satirlar = kaynak.splitlines()
    bas, son = bas or 1, son or len(satirlar)
    return sum(1 for i in range(bas, son + 1)
               if satirlar[i - 1].strip()
               and not satirlar[i - 1].strip().startswith("#")
               and i not in belge)


def _ask_dugumu() -> tuple[str, ast.AST]:
    kaynak = (APP / "routers" / "ask.py").read_text(encoding="utf-8")
    for n in ast.walk(ast.parse(kaynak)):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "ask":
            return kaynak, n
    pytest.fail("`ask()` fonksiyonu bulunamadı — taşınmışsa kapı GÜNCELLENMELİ, silinmemeli")


# ── KAPILAR ──────────────────────────────────────────────────────────────────

def test_OLCUM_ARACI_KENDINI_OLCUYOR():
    """Tavan, `kod_satiri`'nin doğruluğuna dayanır. Araç kayarsa kapı **sessizce** kayar."""
    ornek = (
        '"""Modül belgesi\nikinci satır."""\n'      # 2 satır belge → sayılmaz
        "# yorum\n"                                  # sayılmaz
        "\n"                                          # sayılmaz
        "import os\n"                                # 1
        "def f():\n"                                 # 2
        '    """tek satır belge."""\n'               # sayılmaz
        "    return os\n"                            # 3
    )
    assert kod_satiri(ornek) == 3, kod_satiri(ornek)


def test_ASK_FONKSIYONU_TAVANI_ASMIYOR():
    """`ask()` gövdesi **kod satırı** olarak tavanı aşamaz."""
    kaynak, n = _ask_dugumu()
    kod = kod_satiri(kaynak, n.lineno, n.end_lineno)
    assert kod <= TAVAN_ASK_KOD, (
        f"🔴 `ask()` {kod} kod satırı — tavan {TAVAN_ASK_KOD} "
        f"(FAZ 0 ÖNCESİ {TABAN_ASK_KOD} + {len(MUAFIYET_ASK_KOD)} muafiyet).\n"
        "YAPILACAK: yeni davranışı **modüle çıkar**, tavanı yükseltme. Tavanı yükseltmek "
        "kapıyı kapının kendisiyle çürütür — bu madde tam olarak onu engellemek için var.\n"
        "Gerçekten muaf bir iş ise MUAFIYET_ASK_KOD'a **sha + Δ + GEREKÇE** ile yazılır; "
        "gerekçesiz bir sayı muafiyet değil, sessiz bir tavan artışıdır.")


def test_ASK_IC_FONKSIYON_SAYISI_ARTMIYOR():
    """🔴 Asıl zarar **paylaşılan kapsamdır**: 19 iç fonksiyon aynı yerel değişkenleri
    görüyor ve bir çağrının **yanlış `if`in içinde** olduğu görünmüyor (`K3`'ün kusuru
    buradan doğdu). Yirminci closure, o körlüğü büyütür.

    ⚠ FAZ 0'ın **hiçbir maddesi** bu sayıyı artırmadı — muafiyet listesi bu ölçüt için
    **boştur** ve boş kalması bir başarıdır.
    """
    _kaynak, n = _ask_dugumu()
    ic = sum(1 for c in ast.walk(n)
             if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)) and c is not n)
    assert ic <= TABAN_ASK_IC_FN, (
        f"🔴 `ask()` içinde {ic} iç fonksiyon — tavan {TABAN_ASK_IC_FN}.\n"
        "Yeni bir yardımcı gerekiyorsa **modül düzeyine** al: saf bir fonksiyon test "
        "edilebilir, closure edilemez. `ask()`'in kapsamına eklemek borcu büyütür.")


def test_CUBE_ROUTER_TAVANI_ASMIYOR():
    """`cube_router.py` modül bütünü — **kod satırı**."""
    kaynak = (APP / "cube_router.py").read_text(encoding="utf-8")
    kod = kod_satiri(kaynak)
    assert kod <= TAVAN_CUBE_ROUTER_KOD, (
        f"🔴 `cube_router.py` {kod} kod satırı — tavan {TAVAN_CUBE_ROUTER_KOD} "
        f"(FAZ 0 ÖNCESİ {TABAN_CUBE_ROUTER_KOD} + "
        f"{len(MUAFIYET_CUBE_ROUTER_KOD)} muafiyet).\n"
        "Yeni eşleştirme kuralı bir **modüle** çıkar; bu dosya zaten deterministik "
        "yolun tamamını taşıyor.")


def test_ASK_PY_DOSYASI_ASK_DISINDA_SESSIZCE_SISMIYOR():
    """`ask()` küçülürken dosyanın **geri kalanı** şişerse borç yer değiştirmiş olur.

    ⚠ Bu ölçüt `ask()` dışını sayar; `ask()`'ten modül düzeyine **taşınan** kod bu sayıyı
    artırır ve bu **istenen** yöndür — o yüzden tavan, taşınabilecek payı da kapsayacak
    şekilde `ask.py`'nin **bütünü** üzerinden kurulur (aşağıdaki toplam kapısı).
    """
    kaynak, n = _ask_dugumu()
    toplam, icinde = kod_satiri(kaynak), kod_satiri(kaynak, n.lineno, n.end_lineno)
    disinda = toplam - icinde
    assert toplam <= TAVAN_ASK_DOSYA, (
        f"🔴 `ask.py` toplam {toplam} kod satırı (`ask()` {icinde} · dışı {disinda}) — "
        f"tavan {TAVAN_ASK_DOSYA}.\n"
        "`ask()`'ten modül düzeyine TAŞIMAK bu sayıyı artırmaz (yer değiştirir); "
        "artıyorsa gerçekten YENİ kod eklenmiş demektir → ayrı bir modüle çıkar.")


def test_KAPI_SAHTE_DEGIL_bir_satir_eklenince_KIRMIZI():
    """🔴 **Bir kapı, kırmızı olabildiğini kanıtlayana kadar kapı değildir.**

    Bu operasyonda bir kapı **üç kez** yanlış yazıldı ve *"yeşil"* kaldığı için kusuru
    **taşıyarak** geçti. Burada mutasyon **bellekte** yapılır: gerçek kaynağa **tek bir
    kod satırı** enjekte edilir ve tavanın aşıldığı gösterilir. Depoya hiçbir şey yazılmaz.

    Ayrıca **ikinci bir şey** kanıtlanır: enjekte edilen satır bir **yorum** olsaydı kapı
    yeşil kalırdı — birim kararının (*"kod satırı, ham satır değil"*) davranıştaki
    karşılığı budur, bir niyet beyanı değil.
    """
    kaynak = (APP / "cube_router.py").read_text(encoding="utf-8")
    temiz = kod_satiri(kaynak)
    assert temiz <= TAVAN_CUBE_ROUTER_KOD, "ön koşul: dosya bugün tavanın altında olmalı"

    # (a) KOD satırı → tavan aşılır
    kodlu = kaynak + "\n_FAZ_0_21_MUTASYON = 1\n"
    assert kod_satiri(kodlu) == temiz + 1
    assert not (kod_satiri(kodlu) <= TAVAN_CUBE_ROUTER_KOD), (
        "🔴 KAPI SAHTE: bir kod satırı eklendi ve tavan hâlâ aşılmadı. Tavanda boşluk "
        f"var demektir ({TAVAN_CUBE_ROUTER_KOD - temiz}) — kapı büyümeyi DURDURMUYOR.")

    # (b) YORUM satırı → kapı sessiz kalır (belgeleme vergilendirilmez)
    yorumlu = kaynak + "\n# ölçülmüş bir kusurun kaydı buraya yazılabilmeli\n"
    assert kod_satiri(yorumlu) == temiz, "yorum kod sayılıyor — belge vergilendirilir"
    assert kod_satiri(yorumlu) <= TAVAN_CUBE_ROUTER_KOD


def test_MUAFIYETLER_GEREKCELI_ve_TOPLAMI_TUTUYOR():
    """🔴 **Gerekçesiz bir sayı muafiyet değil, sessiz bir tavan artışıdır.**

    Kapı burada kendi listesini denetler: her muafiyet bir **kaynak** (sha — ya da henüz
    commit'lenmemiş bir madde için `faz-N.M` kimliği), bir **Δ** ve bir **gerekçe**
    taşımalı; toplamları da ilan edilen tavanla birebir tutmalı. Aksi hâlde biri listeye
    bakmadan `TAVAN_*` sabitini büyütür ve kapı, kendi kendini çürütür.
    """
    for ad, liste, taban, tavan in (
            ("ASK", MUAFIYET_ASK_KOD, TABAN_ASK_KOD, TAVAN_ASK_KOD),
            ("CUBE_ROUTER", MUAFIYET_CUBE_ROUTER_KOD,
             TABAN_CUBE_ROUTER_KOD, TAVAN_CUBE_ROUTER_KOD),
            ("ASK_DOSYA", MUAFIYET_ASK_DOSYA, TAVAN_ASK_KOD + TASINABILIR_PAY,
             TAVAN_ASK_DOSYA)):
        for sha, delta, gerekce in liste:
            assert len(sha) >= 7 and delta > 0 and len(gerekce) > 25, \
                f"{ad}: muafiyet eksik/gerekçesiz: {(sha, delta, gerekce)}"
        assert taban + sum(d for _s, d, _g in liste) == tavan, \
            f"{ad}: muafiyet toplamı ilan edilen tavanla TUTMUYOR"


def test_DOSYA_MUAFIYETI_ASK_TAVANINI_YUKSELTMIYOR():
    """🔴 **Ölçüm aracının kendi kusuru — ve düzeltmesi.**

    `ask()` bugün tam tavanında (1147/1147). Modül düzeyine eklenen bir uç kaydı için
    `MUAFIYET_ASK_KOD`'a yazmak, **aynı anda** `ask()` gövdesine de o kadar pay açardı —
    yani *"fonksiyonu büyütme"* kuralı, dosyaya eklenen her satırla **sessizce** gevşerdi.
    *Bir tavanı yanlışlıkla yükselten muafiyet, muafiyet değil sessiz bir tavan artışıdır.*
    """
    assert TAVAN_ASK_KOD == TABAN_ASK_KOD + sum(d for _s, d, _g in MUAFIYET_ASK_KOD), \
        "dosya muafiyeti `ask()` tavanına sızmış"
    # ⚠ Karşılaştırma bilinçli olarak **sabit adı taşımıyor**: `test_KAPI_BIR_TAVAN_BIR_
    # HEDEF_DEGIL` tavan sabitiyle yapılan her karşılaştırmanın `<=` olmasını arar ve bu
    # satır `>` olduğu için onu **yanlışlıkla** kırmızı yapardı (kapının kapıyı yakalaması).
    assert sum(d for _s, d, _g in MUAFIYET_ASK_DOSYA) > 0, "dosya muafiyeti hiç uygulanmamış"


def test_KAPI_BIR_TAVAN_BIR_HEDEF_DEGIL():
    """Küçültme **serbesttir** ve ayrı bir maddedir. Kapı `<=` kullanır, `==` değil.

    `==` kullanmak, iyileştirmeyi **kırmızı** gösterirdi — bir kapının yapabileceği en
    ters şey, doğru işi cezalandırmaktır. Bu test o niyeti **kodla** kilitler.

    🔴 **İLK SÜRÜM METİN ARADI VE KENDİ İDDİASINI YAKALADI.** `"== TAVAN_ASK_KOD" not in
    kaynak` yazıyordu; o dizi **testin kendi assert satırında** geçiyordu → kapı, doğru
    yazılmış bir dosyayı *"eşitlikle kilitlenmiş"* ilan etti. Bu deponun tam olarak
    kaydettiği sınıf: *"testler METNİ ölçtü, davranışı değil"* (`⟳` sayacı da aynı yere
    düşmüştü: kendi paragrafını sayıp 14 ↔ 13 vermişti).

    Doğru ölçüm **yapısaldır**: tavan sabitleriyle yapılan karşılaştırmaların **operatörü**
    AST'ten okunur. Bir dizi değil, bir **düğüm**.
    """
    agac = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    tavanlar = {"TAVAN_ASK_KOD", "TAVAN_ASK_DOSYA", "TAVAN_CUBE_ROUTER_KOD",
                "TABAN_ASK_IC_FN"}
    bulunan = 0
    for n in ast.walk(agac):
        if not isinstance(n, ast.Compare):
            continue
        # Sağ tarafta bir tavan sabiti geçiyor mu (yalın ya da toplamın parçası olarak)?
        adlar = {a.id for k in n.comparators for a in ast.walk(k)
                 if isinstance(a, ast.Name)}
        if not (adlar & tavanlar):
            continue
        bulunan += 1
        assert all(isinstance(o, ast.LtE) for o in n.ops), (
            f"tavan karşılaştırması `<=` değil ({[type(o).__name__ for o in n.ops]}) — "
            "küçültme kırmızı verirdi; kapı bir TAVAN, bir hedef değil")
    assert bulunan >= 3, f"tavan karşılaştırması bulunamadı ({bulunan}) — kapı boş mu?"


def test_YOL_HARITASININ_ILAN_ETTIGI_SAYIYLA_FARK_YAZILI():
    """⚠ Yol haritası `0.21`'i *"~1.930 satır / **20 closure** @`c4b14d1`"* diye ilan etti;
    bu kapının ölçtüğü ise `c3fcfe7`'de **2008 ham / 1135 kod / 19 iç fonksiyon**.

    İkisi **çelişmiyor**, farklı şey sayıyorlar: farklı sha, ve *"closure"* ile *"iç
    fonksiyon"* aynı birim değil. Sessizce kendi sayımı benimsemek, bu deponun altı kez
    kaydettiği *"ölçüm birimi tanımlanmadan yapılan kıyas"* kusuru olurdu — fark **yazılı**.
    """
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "c4b14d1" in kaynak and "c3fcfe7" in kaynak, \
        "iki ölçüm noktası da belgede anılmalı"
