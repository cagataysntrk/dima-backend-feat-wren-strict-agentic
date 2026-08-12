# DİMA — HAVA BOŞLUĞU: modelin rakamı ÜRETEMEMESİ

> **Ölçüm tarihi:** 2026-08-12 · **Yöntem:** canlı `POST /ask` (12 cevap, tek tek curl)
> **Ham alan:** her cevabın `hava_boslugu` makbuzu · **Kod:** `app/yayilim.py` ·
> `app/answer.py:618-680` · `app/iddia.py` · `app/narration_guard.py`

Bu belge bir pazarlama sayfası değil, bir **ölçüm kaydıdır**. `§A14`'ün kendi cümlesi:
*«Ölçülüp yayınlanmadığı sürece sadece bir iddia.»*

---

## 1 · İddia

> **Bir dil modeli, DİMA'da kullanıcının gördüğü hiçbir sayıyı üretemez.**

Bu bir *«üretmemeye çalışıyoruz»* değil, bir **yapı** iddiasıdır: sayı modele hiç
gitmez; giderse yerine bir **yer tutucu** gider ve gerçek değer dönüşte geri konur.

⚠ Emsal farkı: Veezoo/Pyramid benzer bir ayrımı **gizlilik özelliği** diye satıyor. Bizim
için bu bir **güvenlik sınırıdır** — çünkü asıl korunan şey veri değil, **sayının
doğruluğu**dur.

---

## 2 · İki katman — ve birincisi daha güçlü

| katman | ne olur | modelin sayıya erişimi |
|---|---|---|
| **① Şablon** (`anlatici.py`) | cümleyi **deterministik kod** kurar | **hiç yok** — LLM çağrılmaz |
| **② Yer tutuculu anlatı** (`yayilim.py`) | LLM çağrılır ama sayılar **perdelenir** | yalnız `⟦0⟧` gibi belirteçler |

⊙ Katman ① bir *«yedek»* değil **birincil yol**dur: bir cevap şablonla anlatılabiliyorsa
LLM'e hiç gidilmez. `§D11-b` ve `§18.5` bu turda tam olarak o yolu **genişletti** —
yinelenen ölçü ve tek kalemde uydurma üstünlük kalkınca daha çok cevap ① katmanında
kaldı.

---

## 3 · Ölçüm (2026-08-12, 12 canlı cevap)

### Katman ① — LLM sayıyı hiç görmedi

    «bu yıl aylık ciro trendi»            → şablon · hava_boslugu YOK (LLM çağrılmadı)
    «makine bazında ortalama oee bu yıl»  → şablon
    «en çok fire veren makine hangisi»    → şablon
    «geçen yıla göre ciro nasıl değişti»  → şablon
    «müşteri bazında ciro bu yıl»         → şablon
    «vardiya bazında oee»                 → şablon
    «arıza tipine göre arıza sayısı»      → şablon
    «hedefin neresindeyiz»                → şablon
    «hangi müşteri riskli»                → şablon   (narration_kaynak = "sablon")

**9/12 cevapta LLM anlatı basamağı hiç koşmadı.**

### Katman ② — LLM koştu, sayılar perdelendi

| soru | `yer_tutucu` | `bozulan` | `iddia_dusen` | `anlati_dogrulandi` |
|---|---|---|---|---|
| *«makine bazında oee ve fire»* | **6** | **0** | **0** | ✅ |
| *«ciro ve kar marjı müşteri bazında»* | **7** | **0** | **0** | ✅ |
| *«enerji tüketimi ve karlılığı makine bazında»* (plan yolu) | **7** | **0** | **0** | — |

**Toplam: 20 yer tutucu · 0 bozulan · 0 düşen iddia.**

---

## 4 · Alanların anlamı — ve neden bunlar

| alan | ne sayar | neden bir makbuz |
|---|---|---|
| `yer_tutucu` | modele gitmeden **perdelenen** gerçek değer/sayı adedi | 0 ise ya cevapta sayı yoktu ya perdeleme koşmadı — ikisi ayırt edilebilir olmalı |
| `bozulan` | dönüşte **geri konamayan** yer tutucu | modelin belirteci bozması; **>0 bir kusurdur** ve loglanır |
| `iddia_dusen` | iddia kapısının **reddettiği** cümle | modelin katalogda karşılığı olmayan bir şey iddia etmesi |
| `anlati_dogrulandi` | `narration_guard`'ın cümledeki her sayıyı **fişe karşı** doğrulaması | eşleşmeyen sayı taşıyan cümle **yayımlanmaz** |

---

## 5 · Bilinen körlükler — ve neden yazılı

1. **Payda küçük (12).** Bu bir korpus değil, **canlı bir turdur**. Oran değil **varlık**
   kanıtlar: mekanizmanın koştuğunu ve bozulmanın sıfır olduğunu. Korpus ölçümü `§26`
   (garson doğruluk ölçümü) ile gelecek ve o **park edilmiş**.
2. **Discovery yolu ayrı.** Ham SQL yazan Discovery/adhoc yolunda sayı motordan gelir ama
   **SQL modelden** gelir; oranın güvencesi `§⑧`'in kapsam kapısıdır, bu belge değil.
   Rozet (`source=llm:*`) o ayrımı kullanıcıya söyler.
3. **`bozulan=0` bir tavan değil bir ölçümdür.** 20 yer tutucuda 0 bozulma, *«hiç
   bozulmaz»* demek değildir; bozulduğunda **görünür** olduğunu gösterir.
4. **`guard_muaf` alanı bir gevşetmedir** ve içeriği makbuzda yazılı (`yil: [1900,2100]`
   · `sira_esigi: 10`): yıl sayıları ve küçük sıra numaraları guard'dan muaftır, çünkü
   onlar bir ölçü değil bir **etikettir**. Muafiyetin kendisi de yayınlanır.

> *Bir güvenceyi ölçmeden yayımlamak bir iddiadır; körlüklerini yazmadan yayımlamak bir
> reklamdır.*

---

## 6 · Yeniden üretmek

```bash
# backend ayakta olmalı (:8001)
TOKEN=$(curl -s -X POST localhost:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s -X POST localhost:8001/ask -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"question":"makine bazında oee ve fire"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['hava_boslugu'])"
```

⚠ Çok **ölçülü** bir soru seçin: tek ölçülü sorular şablon yolunda kalır ve
`hava_boslugu` **boş** döner — bu bir eksiklik değil, katman ①'in kanıtıdır.
