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
TABAN_CUBE_ROUTER_KOD = 1664  # 1739 ölçüldü − 75 muafiyet = taban; tavan tam 1739
#: 🔴 **1685 → 1664 (2026-08-07): TAVAN YİNE İNDİ — ve yine bir KURAL GEREĞİ.**
#: `build_catalog` `app/katalog_metni.py`'ye taşındı (LLM'in gördüğü METNİN sahibi
#: `cube_router` değil); dosya 1760'tan 1739'a düştü ve tavanda **21 satır boşluk**
#: kaldı. Meta-kapı (`test_TAVAN_KAPISI_GERCEKTEN_KAPI_MI`) bunu **kendisi yakaladı**:
#: boşluklu bir tavan, büyümeyi durdurmayan bir tavandır.
#: *Bir tavanı indirmemek, onu yükseltmenin sessiz biçimidir.*

#: `(sha, Δ, gerekçe)` — her satır **bir maddeye** aittir ve nedeni yazılıdır.
#: 🔴 Toplamları aşağıda **kapıyla** doğrulanır: kimse listeye bakmadan tavanı büyütemez.
MUAFIYET_ASK_KOD = [
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
]
MUAFIYET_CUBE_ROUTER_KOD = [
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
    ("faz-1.12", 9, "AI Act Md.14 durdurma ucu — karar+yazma `app/ask_jobs.py`'de; `ask.py`'de "
                "kalan yalnız UÇ KAYDI (dekoratör 2 + imza 1 + delege 1 + `ask_jobs` "
                "importu 1), `_bg`'nin iki dalındaki iptal kontrolü (2) ve akışın `iptal` "
                "olayı (3 — durdurma `hata` değildir ve dalsız akış 6 dk açık kalırdı). "
                "Bir HTTP uç kaydı router modülünden çıkarılamaz; çıkarmak `/ask/jobs` "
                "kaynağını iki dosyaya bölerdi"),
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
