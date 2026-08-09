# ORKESTRATÖR A/B — `O-9` · `EE` turu (2026-08-09)

> Alet: `lab/discovery_orani.py` · payda **20** (aynı sorular, aynı sırayla, `curl` ile
> tek tek) · şirket `demo-boyahane` · sağlayıcı `openrouter/deepseek-v4-flash`

## Sonuç

| koşum | 🍳 cube | 🗣 cube+llm | 🥡 Discovery/adhoc | 🔴 cevapsız | **arıza oranı** |
|---|---|---|---|---|---|
| **A** · bayrak kapalı | %10 | **%35** | %10 | %45 | **%55** |
| **B** · plan `select_cube`'un YERİNE | %10 | %25 | 🔴 %25 | %40 | 🔴 **%65** *(+10)* |
| **B2** · plan YALNIZ boşlukta | %10 | **%35** | %5 | %50 | **%55** *(+0,0)* |

## 🔴🔴 `B`'nin öğrettiği — ve neden bir tasarım kararını çürüttü

Raporun `E6` düzeltmesi *"planlayıcı garsonun kendisi; plan `select_cube`'un **yerine**
geçer, LLM turu artmaz"* diyordu. Fikir doğru, **yeri** yanlıştı.

⊙ **Mekanizma:** `_select_consistent` `k` örneği **aynı** süreçten çeker ve oylar. Plan
araya girince örneklerin bir kısmı plandan, bir kısmı `select_cube` yedeğinden geliyordu —
oy artık **aynı dağılımdan** çekilmiyordu. *Bir oylamanın geçerliliği örneklerin
özdeşliğine dayanır; iki farklı süreci aynı sandığa atmak, oylamayı gürültüye çevirir.*

Somut kayıplar:

| soru | A | B |
|---|---|---|
| `EE6` *«geçen hafta hiç iş kazası oldu mu»* | `isg` · `{kaza_adedi: 0}` ✅ | 🔴 cevapsız |
| `EE14` *«ciromuz büyüdü mü»* | `parti.toplam_ciro` | 🔴 **İK'ya** düştü |
| `EE4` *«bu çeyrek ile geçen çeyrek»* | 10 satır | 🔴 cevapsız |

## ⟳ `B2` — `E3`'ün LAFZINA dönüldü

Plan artık `select_cube` ile yarışmıyor; yalnız **boşlukta** çağrılıyor (route boş **ve**
garsonun tek-cube cevabı yok). Sonuç: gerileme **tamamen** kapandı — `cube+llm` %35'e
geri döndü, arıza oranı tabana eşit.

## ⚠ Ama kazanç da SIFIR — ve sebebi yazılı

Canlı iki plan denemesinin ikisinde de **şema-geçerli bir plan çıkmadı**:

1. `TREND` · `AYRISTIR` · `KIYASLA` · `ANLAT` fiillerinin **çalıştırıcıları bağlı değil**.
2. Serbest-JSON sağlayıcı adım **sözleşmesine uymuyor** — fiili doğru yazıp parametrelerini
   uyduruyor (`{"fiil":"SORGU"}` · `{"fiil":"AYRISTIR","ozellik":…}`). `ZORUNLU_ALANLAR`
   bunları düşürüyor ve bu **doğru davranış**: yarım bir planı koşmak, koşmamaktan kötüdür.

## Karar

🔴 Bayrak **`off`** — ve faz **iptal değil**. Raporun kendi kuralı: *«oran düşmezse faz
GELİŞTİRİLİR, iptal edilmez»*. Sıradaki iş yukarıdaki iki maddedir.

*Bir bayrağı «belki bir işe yarar» diye açık bırakmak, ölçmemenin kibar hâlidir.*
