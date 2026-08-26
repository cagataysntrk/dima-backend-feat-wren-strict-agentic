"""TAKİP SORUSUNUN ÜÇÜNCÜ SINIFI — "cevap üstünde konuşma" (Faz G1).

## Ölçülen boşluk (2 Ağustos 2026)

Takip soruları bugüne kadar **iki** sınıfa ayrılıyordu:

    structural_followup = bool(body.cube_query)   # sorguyu DÜZENLE  → deterministic_refine
    raw_followup        = prev_sql and history    # ham SQL zinciri  → Discovery

*"Verdiğin cevap hakkında konuş"* diye **üçüncü bir sınıf yoktu**. Sonuç ölçüldü — bir
`parti` raporu üstünde:

| Soru | Bugünkü cevap |
|---|---|
| *"bu neden böyle?"* | "Bu takip mesajını önceki raporla ilişkilendiremedim." |
| *"normal mi?"* | aynı ölü uç |
| *"ne yapmalıyız?"* | aynı ölü uç |
| *"şu düşüş ne?"* | *"«dusus» kısmını anlayamadım"* |
| *"bunu nasıl iyileştiririz?"* | *"«bunu» yerine «gunu» mi demek istedin?"* ← anlamsız |

Altı sorunun altısı da duvara çarpıyor. Bu, ürünün **en görünür eksiğidir**: kullanıcı
hesaplanmış bir sonuca bakıp konuşamıyor.

## Sınıfın tanımı

**Bu sınıf YENİ BİR CEVAP ÜRETMEZ, VAR OLANI AÇAR.** Ayrım budur ve önemlidir:

- *"makine bazında"* → **yapısal**: sorgu değişir, yeni sayılar gelir.
- *"bu neden böyle?"* → **konuşma**: sorgu DEĞİŞMEZ; mevcut makbuza çapalanır, gerekirse
  **araç çağırır** (`contribution`, `yoy`, `drill`) ve anlatır.
- *"peki ciro?"* → **yeni konu**.

Konuşma sınıfının Discovery'ye **düşmemesi** kritiktir: Discovery bağlamsız ham SQL yazar
ve ölü tablo döndürür (ölçülen sorun tam olarak budur). Bir soru *"bu cevap hakkında"* ise,
cevabı zaten elimizdedir — yeni SQL yazmak yanlış araçtır.

## Sınıflandırma neden LLM'siz

Sınıf kararı bir **niyet tespitidir**, anlama değil: soru mevcut sonuca mı işaret ediyor,
yoksa yeni bir sorgu mu istiyor? LLM'e verilseydi aynı soru farklı turlarda farklı sınıfa
düşebilir ve bağlam sürekliliği (§12) ölçülemez hale gelirdi. Ayrıca bu yol **sıfır maliyetli**
olmalıdır — konuşma turları en sık turlardır.

## Kelime sınırı disiplini

Faz D3'ün dersi burada da geçerlidir: eşleşme **kelime başında** başlamalı ve arkasında
yalnız geçerli bir Türkçe ek zinciri kalmalıdır. Aksi halde *"neden"* kalıbı *"beden"*i,
*"iyi"* kalıbı *"iyileştirme"*yi yakalar. `cube_router._syn_hit` aynı disiplini uygular ve
**yeniden yazılmaz** — çağrılır.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.cube_router import _norm, _syn_hit

# --- SINIFLAR --------------------------------------------------------------------
SINIF_YAPISAL = "yapisal"      # sorguyu düzenle (bugün zaten var)
SINIF_KONUSMA = "konusma"      # YENİ: cevabın üstünde konuş
SINIF_YENI = "yeni"            # yeni konu

# --- KONUŞMA TÜRLERİ -------------------------------------------------------------
TUR_NEDEN = "neden"            # "bu neden böyle?" → katkı ayrıştırması
TUR_NORMAL = "normal_mi"       # "normal mi?"      → dönemsel kıyas + sinyal
TUR_NE_YAPMALI = "ne_yapmali"  # "ne yapmalıyız?"  → reçete (G3'ün tohumu)
TUR_ISARET = "isaret"          # "şu düşüş ne?"    → grafiğe çapa (G2)
TUR_ANLAT = "anlat"            # "bunu analiz et"  → ELDEKİ cevabı AÇ (Faz D2)
TUR_TAKIP = "takip"            # "bunu takip et"   → ZAMANLA ÖNERİSİ (FAZ 5.1)
TUR_PAYLAS = "paylas"          # "müdüre 3 cümle"  → PAYLAŞILABİLİR LİNK (FAZ 5.2)
TUR_MAKBUZ = "makbuz"          # "bu nasıl hesaplandı?" → FİŞİ OKU (§V1)

# Kalıplar `_norm` sonrası (ASCII, küçük harf) yazılır. Sonu "!" olanlar TAM KELİME
# eşleşir — Faz D3'ün `_syn_hit` disiplini; kalanlar geçerli ek zinciri kabul eder.
# ⚠ **FAZ 5.3 EKLERİ — ölçümle geldi, refleksle değil.** `lab/konusma_ifadeleri.py`
# gerçek kullanıcı ifadelerini koşturdu ve aşağıdaki dördü `sozlukte-yok` çıktı. Bu,
# ADR-0008'in yasakladığı *"kelimeye özel yama"* DEĞİLDİR: yama bir **örneği** düzeltir,
# bu ise kalıp sözlüğünü **kullanıcının kelimeleriyle besler** (5.3'ün tanımı). Fark,
# eklemeyi neyin tetiklediğidir — bir şikâyet mi, bir **ölçüm** mü.
_NEDEN = ("neden", "nicin", "niye", "sebebi", "sebep", "kaynaklan", "yol acan",
          "nereden geliyor", "niden",
          "ne etkiledi", "ne oldu", "yol acti", "neye bagli")
_NORMAL = ("normal mi", "olagan", "beklenen", "beklenir", "iyi mi", "kotu mu",
           "sorun var mi", "endise", "endiselenmeli", "alarm", "makul mu")
# DİKKAT — 1. ÇOĞUL ŞAHIS EKİ `-(y)İz` ÇEKİMLİ HÂLLERİYLE YAZILIR ("yapmaliyiz",
# "azaltiriz"). Ölçüldü: `cube_router._SUFFIX_ATOMS` tablosunda `iz`/`uz` atomları YOK,
# dolayısıyla `_syn_hit("ne yapmaliyiz", "ne yapmali")` FALSE dönüyor. Tabloya atom
# eklemek `_covers`'ı ve HER `_syn_hit` çağrısını etkiler; o dosyanın kendi uyarısı
# ("buraya atom eklerken…") bunun daha önce delik açtığını kaydediyor. Bu yüzden
# morfoloji tablosu DEĞİŞTİRİLMEDİ — bu bir SÖZLÜK dosyasıdır ve çekimli biçim eklemek
# sözlük işidir, kural değişikliği değil. Tabloyu genişletmek ayrı ve ÖLÇÜLMÜŞ bir
# değişiklik olmalıdır.
_NE_YAPMALI = ("ne yapmali", "ne yapmaliyiz", "ne yapabilir", "ne yapabiliriz",
               "ne onerir", "oneri", "aksiyon", "tavsiye", "onlem",
               "nasil iyilestir", "nasil iyilestiririz", "nasil duzelt", "nasil duzeltiriz",
               "nasil azalt", "nasil azaltiriz", "nasil artir", "nasil artiririz",
               "nasil yol al", "nasil yol aliriz", "ne tavsiye")
# ⚠ FAZ 5.3 ekleri (aynı gerekçe): kullanıcı bir grafikteki noktayı **coğrafi** kelimelerle
# gösteriyor — *tepe · çukur · zirve · dip*. Sözlük bunları hiç bilmiyordu.
_ISARET = ("su dusus", "su artis", "su sicrama", "su kirilma", "bu dusus", "bu artis",
           "sicrama", "dusus", "kirilma", "anomali", "aykiri",
           "tepe", "cukur", "zirve", "dip noktasi")
# ANLAT/ANALİZ — kullanıcının EN DOĞAL cümlesi ve Faz D2'ye kadar HİÇBİR türe girmiyordu.
#
# Ölçüldü (3 Ağustos 2026), bir `oee` raporu üstünde — altı ifadenin BEŞİ duvara çarpıyordu:
#
#     "bunu analiz et"     → *"«bunu» yerine «gunu» mi demek istedin?"*     (saçma)
#     "değerlendir"        → *"«degerlendir» yerine «degree» mi?"*          (saçma)
#     "yorumlar mısın"     → *"Bu takip mesajını önceki raporla ilişkilendiremedim"*
#     "özetle"             → aynı ölü uç
#     "bu grafiği açıkla"  → aynı ölü uç
#     "bu neden böyle?"    → ✅ (TUR_NEDEN zaten vardı)
#
# Yani bu dosyanın kendi docstring'inde tarif edilen ölü uç, **bir tür eksik olduğu için**
# yaşamaya devam ediyordu. Sınıfın tanımı değişmiyor: **yeni cevap üretilmez, var olan
# AÇILIR** — `interpret()` olguları zaten hesaplanmıştır, LLM yalnız üslup yazar.
#
# ⚠️ `ozet!` TAM KELİME: `_syn_hit` ek zincirine izin verdiği için tırnaksız `ozet`
# "özetle"yi de yakalar ama "özel"i yakalamaz (kelime başı + geçerli ek şartı). Buna
# rağmen TAM yazıldı ki bir gün eklenen bir `ozet_*` ölçüsü sessizce çalınmasın.
#: FAZ 5.1 — **6. TÜR: *"bunu takip et"***.
#:
#: 🔴 **Ölçülen erişilemezlik:** `sinifla` koşuldu, *"bunu takip et"* → `SINIF_YENI` →
#: kapsam kapısı **R10** → dürüst red. `takip et` grep'i `followup.py` ve
#: `cube_router.py`'de **sıfırdı**. Yani panoya/zamanlamaya giden **hiçbir doğal-dil
#: yolu yoktu**: kullanıcı 🔔 ve *"+ panoya ekle"* düğmelerini **fareyle bulmak
#: zorundaydı**. MIMARI §12.11 bunu kendisi de itiraf ediyor.
#:
#: ⚠ **Kalıplar tasarımcının değil kullanıcının kelimeleri** (5.3 disiplini): *"takip
#: et"* kadar *"izle"*, *"haberim olsun"*, *"bildir"* de gerçek ifadeler. Bir kelime
#: eklemek ADR-0008'in yasakladığı yamadır; bir **ifade ailesini** beyan etmek değildir.
_TAKIP = ("takip et", "takip ede", "takibe al", "takip etmek",
          "izle", "izlemeye al", "izlemek",
          "haberim olsun", "haber ver", "bildir", "bilgilendir",
          "duzenli gonder", "surekli gonder", "her seferinde gonder",
          "gozunu ayirma", "takipte kal", "gundemde tut")

#: FAZ 5.2 — **7. TÜR: *"paylaş / müdüre 3 cümle"***.
#:
#: 🔴 **En öğretici bulgu:** *"müdüre 3 cümle yaz"* niyet olarak `TUR_ANLAT`'a **çok
#: yakın** (aşağıdaki `_ANLAT` sözlüğü), ama sözlükte *"yaz"* / *"3 cümle"* olmadığı için
#: **yakalanmıyordu** → *çalışan, testli bir yetenek bir kelime yüzünden kullanıcıya
#: kapalı*. Bu tür yeni bir motor açmaz; `TUR_ANLAT`'ın zaten ürettiği şeye **erişim** ve
#: **taşınabilirlik** ekler.
#:
#: ⚠ Kalıplar **kullanıcının kelimeleri** (5.3): *"müdüre yaz"*, *"maille"*, *"link ver"*,
#: *"iki cümleyle özetle"*. Bir kelime eklemek ADR-0008'in yasakladığı yamadır; bir
#: **ifade ailesini** beyan etmek değildir.
_PAYLAS = ("paylas", "paylasabilir", "link ver", "link olustur", "linkini",
           "mudure yaz", "mudure gonder", "yoneticiye yaz", "patrona yaz",
           "maille", "mail at", "mail olarak",
           "uc cumle", "3 cumle", "iki cumle", "2 cumle", "bir paragraf",
           "kisaca yaz", "kisa bir ozet yaz", "sunuma koy")

#: 🔴🔴 **`§V1` — 8. TÜR: MAKBUZ SORUSU. Üç kanıt, ve sistem cevabı ZATEN taşıyordu.**
#:
#: | tur | soru | dönen |
#: |---|---|---|
#: | `u2` | *«bu nasıl hesaplandı?»* | 🔴 dürüst ret |
#: | `V2` | *«bu rakama neler dahil, nasıl bulundu»* | 🔴 dürüst ret |
#: | `V17` | *«bu sayı neyi kapsıyor, hangi tarih aralığı kullanıldı»* | 🔴 **aynı tabak tekrar** |
#:
#: ⊙ `V2`'nin cevabı en öğreticiydi — sistem soruyu **doğru tarif edip** reddetti:
#: *«Bu soru mevcut raporun içeriğini ve hesaplama yöntemini sorgulamaktadır; doğrudan
#: bir değişiklik talebi değildir.»* Yani anladı, sınıflandırdı, ve **karşılığı olmadığı
#: için** attı.
#:
#: 🔴 Oysa cevap **zaten üretiliyor**: `drill.formula_explanation` bir `cube_query`'den
#: deterministik, düz-dil bir hesap anlatımı çıkarır ve `gorsel_ekleme.py` onu her cevaba
#: `calculation_explanation` olarak **yazar**. `temellendirme` ve `explain` de aynı turda
#: dolar. Üç alan doluydu, onlara **ulaşan bir konuşma türü yoktu**.
#:
#: ⊙ Ayrım şu: bu bir **VERİ sorusu değil**, bir **MAKBUZ sorusudur.** Kullanıcı yeni bir
#: sayı istemiyor; eldeki sayının **fişini** istiyor. Yeni sorgu koşmak yanlış cevaptır —
#: `V17`'de tam olarak bu oldu ve aynı tablo ikinci kez sunuldu.
#:
#: ⚠ **Zamir şartından MUAF** (`TUR_PAYLAS` gibi): *«nasıl hesaplandı»* edilgen geçmiş
#: zamandır ve **hesaplanmış bir şeye** işaret etmekten başka bir şey yapamaz. Şart
#: konsaydı en doğal ifade yine kapalı kalırdı — düzeltilen kusurun aynısı, bir kat aşağıda.
#: ⚠ `baglam_var` kapısı zaten yukarıda: ekranda rapor yoksa bu tür hiç doğmaz, yani
#: *«fire nasıl hesaplanır?»* (tanım sorusu) yeni konu olarak kalır.
_MAKBUZ = ("nasil hesaplandi", "nasil hesapladin", "nasil hesaplanir", "nasil buldun",
           "nasil bulundu", "nasil cikti", "nasil olustu", "nasil geldi",
           "neler dahil", "ne dahil", "nelerden olusuyor", "neyi kapsiyor",
           "neyi iceriyor", "nelere bakti", "hangi verilerden", "hangi veriden",
           "hangi kayitlardan", "hangi tarih araligi", "hangi donem kullanildi",
           "kaynagi ne", "nereden geliyor", "nereden aldin", "hangi formul",
           "formulu ne", "formul ne", "hesap yontemi", "hesaplama yontemi",
           "bu guvenilir mi", "guvenilir mi", "emin misin", "dogru mu bu",
           "kanit", "makbuz", "hangi tabloda", "hangi kolon")

#: 🔴🔴 **`§BB1` — «NASIL» + EDİLGEN GEÇMİŞ, KAPALI BİR DİLBİLGİSİ AİLESİDİR.**
#:
#: Ölçüldü (`AA5` — *«bu analiz **nasıl yapıldı**, hangi sayılara baktın»*): makbuz türü
#: **doğmadı**, soru yapısal bir düzenleme sanıldı ve aynı tablo yeniden koştu.
#:
#: ⊙ Sebep `_MAKBUZ`'un altı *«nasıl …»* girdisi taşıması ama **yedincisini taşımaması**:
#: `hesaplandı` · `hesapladın` · `hesaplanır` · `buldun` · `bulundu` · `çıktı` · `oluştu` ·
#: `geldi` var, **`yapıldı`** yok. Sekizincisini eklemek de yalnız dokuzuncuyu bekletirdi
#: (`ADR-0008`: *dile kelime listesiyle yetişilmez*).
#:
#: ⊙ Asıl olgu **yapısal**: *«nasıl»* + **edilgen geçmiş** (`-ıldı/-ildi/-uldu/-üldü` ya da
#: `-ndı/-ndi`) bir **eylemin geçmişte nasıl gerçekleştiğini** sorar. Ekranda bir rapor
#: varken bu, o raporun **yapılış biçimini** sormaktan başka bir şey olamaz — yani bir
#: makbuz sorusudur. Edilgen çatı Türkçenin **kapalı** bir eki ve `ADR-0008` kapalı
#: sınıfları açıkça serbest bırakıyor.
#:
#: ⚠ *«nasıl»* şartı **zorunlu**: tek başına edilgen geçmiş (*«iade edildi»*) bir veri
#: sorusudur. İki öge **birlikte** aranır ve *«nasıl»* soruyu bir **yönteme** çevirir.
#:
#: *Bir listeye sekizinci kelimeyi eklemek, dokuzuncuyu beklemeye karar vermektir.*
#: ⚠ Ekler `_norm` **sonrası** biçimde: `ı→i`, `ü→u`. Ünsüzden sonra `-ildi/-indi/-uldu/
#: -undu` (yap+ILDI · al+INDI · bul+UNDU), ünlüden sonra `-ndi` (hesapla+NDI · özetle+NDI);
#: `-ilmis/-inmis/-ulmus/-unmus` aynı çatının duyulan geçmişi.
_MAKBUZ_EDILGEN = re.compile(
    r"\bnasil\b[^.?!]{0,40}?\b\w{2,}(?:ildi|indi|uldu|undu|ndi|ilmis|inmis|ulmus|unmus)\b")

_ANLAT = ("analiz et", "analiz eder", "analizini", "yorumla", "yorumlar misin",
          "yorumun", "yorumlasana", "degerlendir", "aciklar misin", "acikla",
          "ozetle", "ozetler misin", "ne diyor", "ne anlama gel", "ne anlama geliyor",
          "okur musun",
          "anlat", "yorum yap", "incele")

# Konuşma sınıfı YALNIZ bunlarla tetiklenmez: soru aynı zamanda MEVCUT CEVABA işaret
# etmelidir. "neden" tek başına yeni bir soru da olabilir ("fire neden yüksek olur?").
# Bu zamirler soruyu ELDEKI sonuca bağlar.
#
# 🔴🔴 FAZ 3.4 (`§AY/S`'in ÜÇÜNCÜ örneği) — ÇIPLAK `"bu"`/`"su"` BİLEREK DIŞARIDA:
# aşağıdaki `_bu_su_zamir_mi()` onları AYRI, TEMPORAL-FARKINDA bir kuralla karşılar.
# Ölçüldü (bu operasyonun kendi sohbetinde, FAZ 0.1'de): *"bu yıl her ay için
# ciro..."* cümlesi `açıkla` (`TUR_ANLAT`) → çıplak "bu" eşleşmesinden geçerek
# yanlış `konusma-baglamsiz` sayılıyordu (`test_CIPLAK_BU_TEMPORAL_IFADEYLE_
# KARISIYOR` kayda geçirmişti) — "bu yıl"/"bu ay" rapora işaret ETMEZ, bir zaman
# BELİRTECİDİR. "bu rapor"/"bu tablo"/"bu grafik"/"bu sonuc" gibi ÇOK-KELİMELİ,
# rapora GERÇEKTEN işaret eden biçimler AŞAĞIDA DEĞİŞMEDEN kalır.
_ISARET_ZAMIRI = ("bunu", "bunun", "buradaki", "sunu", "sunun",
                  "yukaridaki", "bu rapor", "bu tablo", "bu grafik", "bu sonuc")

#: 🔴🔴 FAZ 3.4 — Türkçenin takvim/zaman-birimi isimleri: SAYICA SINIRLI, KAPALI bir
#: dilbilgisi kümesi (`_BELGISIZ_ZAMIR`/`_COGUL_ISARET_ZAMIR`'in izlediği AYNI ilke,
#: `ADR-0008` bunu açıkça serbest bırakır) — yeni bir kelime listesi İCAT EDİLMEDİ.
_TEMPORAL_BIRIM = ("yil", "ay", "hafta", "gun", "donem", "ceyrek", "sene")

#: `bu`/`su` kökü + kelime içinde kalan HERHANGİ bir devam (ek zinciri OLABİLİR
#: — `_ek_gecerli` doğrular; "buyuk" gibi kazayla denk gelenleri eler).
_BU_SU_RE = re.compile(r"\b(bu|su)([a-z]*)")


def _bu_su_zamir_mi(q: str) -> str | None:
    """`bu`/`su` iki yoldan GERÇEK zamir sayılır: (1) ÜZERİNE doğrudan bir çekim
    eki YAPIŞMIŞSA — `"bunda"`/`"buyla"` gibi ("bu" Türkçede ünsüz-tampon `n` ile
    çekimlenir: bu+n+da, bu+n+u…) bu HER ZAMAN gerçek bir zamir kullanımıdır, ek
    ayrı bir kelimeye YAPIŞAMAZ; (2) ÇIPLAKSA (ek yok) ve ardından bir takvim/
    zaman-birimi isim GELMİYORSA — "bu yıl"/"bu ay" gibi TAMAMEN yaygın temporal
    belirteçleri "rapora işaret eden zamir" sanmamak için (`§AY/S`, FAZ 3.4).

    ⚠ Ek toleransı `cube_router._ek_gecerli`'den — TEK SAHİP, burada ikinci bir
    çekim kuralı YAZILMAZ (`uyum._grup_basina_istendi`'nin BİREBİR deseni). Bu,
    `_hit()`'in `_syn_hit` ile zaten yaptığı ek-zinciri toleransının BİREBİR
    aynısı — `_ISARET_ZAMIRI`'nden çıkarılan çıplak "bu"/"su" o toleransı
    kaybetmesin diye burada AÇIKÇA yeniden uygulanıyor (ölçülen regresyon:
    "bunda ne oldu?" ilk yazımda kaçıyordu — `\\bbu\\b` yalnız TAM kelimeyi
    arıyordu, "bunda" TEK bir tokendir, iki kelime değil)."""
    from app.cube_router import _ek_gecerli

    for m in _BU_SU_RE.finditer(q):
        zamir, kalan = m.group(1), m.group(2)
        if kalan:
            if _ek_gecerli(kalan):
                return zamir                  # "bunda"/"buyla" — çekimli, HER ZAMAN zamir
            continue                          # "buyuk" gibi — geçersiz çekim, eşleşme değil
        sonraki_m = re.match(r"\s+([a-z]+)", q[m.end():])
        sonraki = sonraki_m.group(1) if sonraki_m else None
        if sonraki:
            _temporal = any(
                sonraki == kok or (sonraki.startswith(kok) and _ek_gecerli(sonraki[len(kok):]))
                for kok in _TEMPORAL_BIRIM)
            if _temporal:
                continue                      # "bu yıl"/"bu ayın" — belirteç, zamir DEĞİL
        return zamir                          # "bu" tek başına ya da temporal-olmayan
    return None

#: 🔴 **BELGİSİZ ZAMİRLER — dilbilgisinin KAPALI sınıfı (`ADR-0008` bunu açıkça serbest
#: bırakır: kelime listesiyle dile yetişilmez, ama gramerin kapalı sınıfları listelenir).**
#:
#: Ölçüldü (`§36`): `neden diğerlerinden yüksek` → kök-neden yoluna **hiç girmedi**,
#: LLM'e düştü (23.646 ms) ve cevap önceki turun **birebir kopyası** oldu. Oysa aynı soru
#: zamirli yazılınca (`bu neden yüksek`) sistem **2.202 ms**'de gerçek bir katkı
#: ayrıştırması üretti: *«iplik grubu: Örme Kumaş — net değişimin %100'ü»*.
#:
#: ⊙ Yani makine kusursuz çalışıyordu; kapı açılmıyordu. Ve açılmama sebebi
#: `_ISARET_ZAMIRI`'nin yalnız **işaret** zamirlerini tanımasıydı — oysa *"diğerleri"*
#: de bir zamirdir ve bu bağlamda **daha güçlü** bir çapadır: *"şu"* bir şeyi işaret
#: eder, *"diğerleri"* **ekranda kalan satırlardan başka bir şey olamaz**.
#:
#: ⚠ Gövde eşlemesi bilerek: `diger`·`digerleri`·`digerlerinden`·`digerine` hepsi aynı
#: zamirin çekimidir. Çekimleri tek tek yazmak bir **kelime listesi** olurdu; gövdeyi
#: yazmak bir **kapalı sınıf**tır. Aynı biçim `_USTUNLUK_RE`'de de kullanılıyor.
_BELGISIZ_ZAMIR = re.compile(r"\b(diger|oteki|beriki)\w*\b")

#: 🔴 **İŞARET ZARFLARI** — `_ISARET_ZAMIRI`'nin kardeşi ve aynı işi görür: soruyu
#: **eldeki cevaba** bağlar. *«neden böyle»* bir belirsizlik değil bir **işarettir**.
#: Dilbilgisinin kapalı bir sınıfı (`ADR-0008` bunu açıkça serbest bırakır).
_ISARET_ZARFI = re.compile(r"\b(boyle|soyle|oyle)\b")

#: 🔴🔴 **`§AA4` — İŞARET ZAMİRİNİN ÇOĞULU YOKTU, ve agentic zincirler orada kopuyordu.**
#:
#: Ölçüldü (`AA9` — kullanıcının literal örneğinin ikinci adımı):
#:
#:     tur 1: «ciromun en büyük 3 kaynağı olan müşterilerimi bul»  → 3 müşteri ✅
#:     tur 2: «**BUNLARA** en çok neleri sattığımı üçü için ayrı ayrı karşılaştır»
#:            → `sevkiyat × varis_il` 🔴 — üç müşteriyle **hiçbir ilgisi yok**
#:
#: ⊙ `_ISARET_ZAMIRI` sekiz **tekil** biçim taşıyordu (`bu`·`bunu`·`bunun`·`şu`·`şunu`…)
#: ve **çoğulunu hiç taşımıyordu**. Oysa çok-adımlı bir zincirde ekrandaki şey neredeyse
#: her zaman bir **liste**dir — yani kullanıcının en doğal ikinci cümlesi *"bunlara"*,
#: *"bunların"*, *"onları"*dır. Zincirin en çok kullanılan bağı, tanınmayan tek bağdı.
#:
#: ⚠ Gövde eşlemesi `_BELGISIZ_ZAMIR`'in kurduğu desenle **aynı**: `bunlar`·`sunlar`·
#: `onlar` + çekim (`-a`·`-ı`·`-ın`·`-da`·`-dan`). Çekimleri tek tek yazmak bir **kelime
#: listesi** olurdu; gövdeyi yazmak bir **kapalı sınıftır** ve `ADR-0008` kapalı
#: dilbilgisi sınıflarını açıkça serbest bırakıyor.
#: ⚠ `onlar` bilerek içeride: üçüncü şahıs çoğul zamiri de ekrandaki satırlara işaret
#: eder (*"onları kıyasla"*) ve tekil `o` — belirsizliği yüzünden — bilerek **dışarıda**.
#:
#: *Bir zinciri kuran şey soru değil, sorunun bir öncekine tutunma biçimidir.*
_COGUL_ISARET_ZAMIR = re.compile(r"\b(bunlar|sunlar|onlar)\w*\b")

#: `§BB-A` — üstünlük çapası. `cube_router._USTUNLUK_RE` ile **aynı yapı** (`en <sıfat>`)
#: + adlaşmış biçimi (*«en kötüSÜ»*, *«en düşüĞÜ»*). Sahibi orası; burada yalnız
#: **çapa** olarak okunuyor — sözlük değil, aynı gramerin ikinci tüketicisi.
_USTUNLUK_CAPA = re.compile(r"\ben\s+[a-z]+\w*\b")

# YAPISAL düzenleme sinyalleri — bunlar varsa soru sorguyu DEĞİŞTİRMEK istiyordur ve
# konuşma sınıfına ALINMAZ. Çakışma gerçektir: "aylık neden düştü?" hem düzenleme hem
# konuşma gibi görünür; öncelik YAPISALDA olmalıdır çünkü kullanıcı yeni sayılar bekler.
#: 🔴🔴 **`§CC-A` — «KIR» BİR FİİLDİR ve `kirilim`in ta kendisidir.**
#:
#: Ölçüldü (CC turu, **iki kanıt**): *«bu farkın sebebini bir kat daha aç»* (`CC5`) ve
#: *«RAM 2'nin fire **nedenlerini KIR**»* (`CC6`) → ikisi de **akran kıyasını tekrarladı**,
#: istenen kırılımı vermedi.
#:
#: ⊙ Sebep `§BB-A`'nın **kenar etkisi**: üstünlüğü/değeri çapa yapınca, içinde *«neden»*
#: geçen **her** takip `TUR_NEDEN`'e düşer oldu. Ama *«nedenlerini kır»* bir **açıklama
#: isteği değil**, bir **yapısal düzenlemedir** — kullanıcı yeni satırlar bekliyor.
#: `_YAPISAL` sözlüğü `kirilim` adını taşıyordu, **fiilini** taşımıyordu.
#:
#: ⚠ Yeni kelime **değil**: `kir` ile `kirilim` aynı gövdedir ve `_syn_hit`'in ek zinciri
#: `kir`+`ilim`i zaten aynı köke bağlıyor. Eksik olan, **emir kipinin** sözlükte
#: olmamasıydı — sistemin adını bildiği şeyin **fiilini** bilmemesi.
#:
#: ⊙ Ve `_YAPISAL` önceliği bu yüzden var (kendi notu): *"kullanıcı yeni sayılar
#: bekliyorsa önce onları vermek gerekir — konuşma bir sonraki turda hâlâ mümkündür,
#: ama yanlış sayı geri alınamaz."*
#:
#: *Bir düzeltme, kapattığı kapının yanında yeni bir kapı açabilir; kenarını da ölçmek
#: gerekir.*
_YAPISAL = ("bazinda", "bazli", "kirilim", "kir", "aylik", "haftalik", "gunluk", "yillik",
            "ceyrek", "sirala", "ilk ", "en yuksek", "en dusuk", "top ", "grafik",
            "tablo", "pasta", "cizgi", "dagilimini", "ayri ayri")


@dataclass(frozen=True)
class Niyet:
    """Sınıflandırma sonucu + **GEREKÇESİ**. Gerekçesiz sınıf bir tahmindir."""

    sinif: str
    tur: str | None = None
    kural: str = ""
    # Eşleşen kalıp — hem hata ayıklama hem makbuz için ("hangi kelime bu sınıfa soktu").
    kanit: str = ""

    @property
    def konusma(self) -> bool:
        return self.sinif == SINIF_KONUSMA


#: 🔴🔴 **`§FÇ` — FİİL ÇEKİMİ: ad çekimi zinciri bu soruyu CEVAPLAYAMAZ.**
#:
#: ## Ölçülen kusur (süit, 2026-08-10)
#:
#:     niyet_kalibi_var("bu grafiği yorumla")     → 'anlat'   ✅
#:     niyet_kalibi_var("bunu nasıl yorumlarsın") →  None     🔴
#:
#: `yorumla` bir **fiil kökü**; `yorumlarsın` = `yorumla` + `-r` (geniş zaman) + `-sın`
#: (2. tekil kişi). `_syn_hit` → `_ek_gecerli` → `_SUFFIX_ATOMS` zinciri **ad** çekimini
#: (hâl · çoğul · iyelik) doğrular; **kişi eki** orada yoktur ve olmamalıdır — katalog
#: terimleri **isimdir** ve isimler kişiye göre çekilmez.
#:
#: 🔴 Bedeli `R2` sınıfı: *«bunu nasıl yorumlarsın»* tanınmış bir niyet taşımıyor sayılır
#: → sosyal kapı onu bir kapanış sanabilir → *«Görüşürüz!»*. En üst kuralın
#: (*«anlamadım/görüşürüz YOK»*) doğrudan ihlali.
#:
#: ## Ve tablo kanıtı KENDİ İÇİNDE taşıyordu
#:
#:     _ANLAT = (…, "yorumla", "yorumlar misin", "yorumlasana", "aciklar misin", "acikla")
#:                    └─ dört giriş, İKİ fiilin ELLE YAZILMIŞ çekimi ─┘
#:
#: Kullanıcının kuralı (*"tek tek yazmak aptallık"*) burada da geçerli — ve bu sefer
#: sinonim değil **çekim**. Kök çözüm: zinciri **tamamlamak**, listeyi büyütmek değil.
#:
#: ## İki tasarım kararı, ikisi de deponun kendi ölçümlerinden
#:
#: 1. 🔴 **ÇIPLAK `-r` YASAK.** `cube_router`'ın `§73` ölçümü: *«tek harflik ünsüz
#:    atomlar neredeyse HER harf dizisini geçerli bir ek zinciri yapıyordu»* (`s` yüzünden
#:    `karsilastir` → *«kâr»* okundu). Bu yüzden ekler **bileşiktir** (`rsin`·`irsin`),
#:    tek harf değil. *Bir ekin kısalığı, onun tehlikesidir.*
#: 2. 🔴 **PAYLAŞILAN ATOM LİSTESİNE GİRMEZ.** `_SUFFIX_ATOMS` katalog terimlerini
#:    (isimleri) eşler; oraya kişi eki koymak route'a **sıfır fayda, artı risk** olurdu —
#:    ve o listenin geri alınmış bir gerileme geçmişi var (`mal`+`iyeti`). Ayrı tutmak
#:    `KAT-1` ihlali **değildir**: *«bu geçerli bir AD çekimi mi»* ile *«geçerli bir FİİL
#:    çekimi mi»* aynı soru değildir. Ve ayrı tutulunca korpus **yapısal olarak**
#:    gerileyemez.
#:
#: *Bir dilbilgisi kuralını tamamlamak, bir sözlüğe kelime eklemekten farklıdır:
#: birincisi bir kez yazılır ve bütün fiiller için çalışır.*
_FIIL_EKLERI: tuple[str, ...] = (
    # geniş zaman + kişi — ünlüyle biten kök: "yorumla"+"rsin" · "acikla"+"riz"
    "rsin", "rsun", "rsiniz", "rsunuz", "rim", "rum", "riz", "ruz", "rlar", "rler",
    # geniş zaman + kişi — ünsüzle biten kök: "degerlendir"+"irsin" · "goster"+"irsiniz"
    "irsin", "ursun", "ersin", "arsin", "irsiniz", "ursunuz",
    "irim", "urum", "erim", "arim", "iriz", "uruz", "eriz", "ariz",
    # rica/emir: "yorumla"+"sana" (tabloda ELLE yazılıydı — artık kuralla geliyor)
    "sana", "sene",
    # yeterlilik: "yorumla"+"yabilir" · "degerlendir"+"ebilir"
    "yabilir", "yebilir", "abilir", "ebilir",
    "yabilirsin", "yebilirsin", "abilirsin", "ebilirsin",
    # soru: "yorumla"+"r misin" bitişik yazımı ("yorumlarmisin")
    "rmisin", "rmisiniz", "irmisin", "urmusun",
)

#: Zincir **tam** eşleşir: kalanın tamamı bir fiil eki olmalı, parçası değil.
_FIIL_EKI_RE = re.compile(r"(?:" + "|".join(sorted(_FIIL_EKLERI, key=len, reverse=True))
                          + r")\Z")


def _fiil_hit(q: str, kok: str) -> bool:
    """Kök, `q` içinde **çekimli** bir fiil olarak geçiyor mu?

    ⚠ Kelime sınırı `_syn_hit` ile aynı disiplinde: kök **kelime başından** aranır,
    kalan **tamamen** bir fiil eki olmalıdır. Böylece `acikla` ⊄ `aciklama tablosu`
    gibi ad türevleri buraya sızmaz — o kalanlar (`ma`·`masi`) fiil eki değildir.
    """
    if " " in kok:                     # çok kelimeli kalıplar çekilmez ("analiz et")
        return False
    for m in re.finditer(rf"(?:^|[^a-z0-9]){re.escape(kok)}([a-z]+)", q):
        if _FIIL_EKI_RE.fullmatch(m.group(1)):
            return True
    return False


def _hit(q: str, kaliplar: tuple[str, ...]) -> str | None:
    """Eşleşen ilk kalıbı döndürür — `_syn_hit` disipliniyle (kelime başı + ek zinciri).

    Çok kelimeli kalıplar bölünmez; `_syn_hit` onları olduğu gibi arar.

    🔴 `§FÇ` — ad çekimi tutmazsa **fiil çekimi** denenir. Sıra bilinçli: `_syn_hit` daha
    dar ve daha çok ölçülmüş; fiil zinciri yalnız onun **pes ettiği** yerde konuşur.
    """
    for k in kaliplar:
        if _syn_hit(q, k) or _fiil_hit(q, k):
            return k
    return None


def niyet_kalibi_var(soru: str) -> str | None:
    """🔴 `R2` — soru **tanınmış bir takip niyeti** taşıyor mu? → tür adı, yoksa `None`.

    ## Neden var — ölçülen kusur

    Canlıda: *«peki ne yapmalıyız»* → **«Görüşürüz! İstediğin zaman buradayım.»**
    (`sosyal sınıf (kapanis)`). Sebep `peki`'nin kapanış kalıplarında olması **değil**
    tek başına: sosyal sınıfın *tam kaplama* yüklemi yalnız **katalog** kelimesi arıyor
    ve *«ne yapmalıyız»* katalogda hiçbir terim taşımıyor — yani ifade "tamamen sosyal"
    sayılıyordu.

    ⊙ Oysa *«ne yapmalı»* bu modülün **zaten tanıdığı** bir türdür (`TUR_NE_YAPMALI`).
    Yani sistem cevabı biliyordu ve kendi bilgisini kendi susturuyordu.

    ⚠ Bu fonksiyon **yeni bir sözlük değildir**: `sinifla`'nın okuduğu **aynı** kapalı
    kalıp tablosunu okur. Var olma sebebi, o bilgiyi `sinifla`'nın `baglam_var`
    ön koşulu olmadan sorulabilir kılmaktır — sosyal kapı bir bağlam bilmez ama
    *«bu bir niyet mi»* sorusunun cevabına ihtiyaç duyar.

    *Bir sistemin kendi tanıdığı niyeti bir selamlaşma sanması, bilgi eksikliği değil
    sıralama hatasıdır.*
    """
    q = _norm(soru or "")
    for tur, kaliplar in ((TUR_PAYLAS, _PAYLAS),
                          (TUR_TAKIP, _TAKIP),
                          (TUR_NE_YAPMALI, _NE_YAPMALI),
                          (TUR_NORMAL, _NORMAL),
                          (TUR_ANLAT, _ANLAT),
                          (TUR_NEDEN, _NEDEN)):
        if _hit(q, kaliplar):
            return tur
    return None


#: `§AY` — bağlamsız konuşma türlerinin **kullanıcı cümlesi**. Metnin sahibi burasıdır
#: (bu bir 🗣 modüldür); `ask()` yalnız çağırır ve atar. İkinci bir yazar, bir gün ikinci
#: bir cümle demektir.
_BAGLAMSIZ_METIN: dict[str, str] = {
    TUR_ANLAT: "Yorumlayabileceğim bir rapor **ekranda yok** — henüz bir sonuç üretmedim.",
    TUR_NORMAL: "*«Normal mi»* diye sorabileceğim bir sayı **ekranda yok**.",
    TUR_NE_YAPMALI: "Öneri çıkarabileceğim bir sonuç **ekranda yok**.",
    TUR_ISARET: "İşaret ettiğin şeyi görebileceğim bir grafik/rapor **ekranda yok**.",
}


#: `§X4`'ün makbuz cümlesi — `ask.py`'den **buraya taşındı**. Gerekçe iki katlı:
#: (1) `ask()`'in büyüme tavanı iki neredeyse-aynı dalı reddetti ve doğru hamle onları
#: **birleştirmekti**; (2) `ask.py` bir 🚪 dosyadır, kullanıcı dili yazmak 🗣 tarafın
#: işidir. *İki dalın aynı şeyi söylediği yerde, iki dal değil bir dal vardır.*
_MAKBUZ_BAGLAMSIZ = (
    "Bir sayının **nasıl hesaplandığını** soruyorsun ama ekranda henüz bir rapor yok — "
    "hesabını gösterebileceğim bir sonuç bulunmuyor.")


def baglamsiz_metni(tur: str | None, kural: str | None = None) -> str:
    """`§AY`+`§X4` — *«ortada rapor yok»*u **türüne göre** söyler ve ne yapılacağını ekler.

    ⚠ Cevap **uydurmaz**: yalnız kesin olarak bilinen bir olguyu söyler. LLM yok, sorgu
    yok, 0 ms. Ve iki kuralın **tek yazarı** burasıdır — ikinci bir yazar, bir gün ikinci
    bir cümle demektir.
    """
    if kural == "makbuz-baglamsiz":
        bas = _MAKBUZ_BAGLAMSIZ
        kuyruk = ("\n\nÖnce bir soru sor (ör. *«bu yıl bölüm bazında elektrik "
                  "tüketimi»*); cevabın altında **hangi ölçü · hangi formül · hangi "
                  "tablo · hangi süzgeçler** kullanıldığını olduğu gibi gösterebilirim.")
    else:
        bas = _BAGLAMSIZ_METIN.get(str(tur or ""), _BAGLAMSIZ_METIN[TUR_ANLAT])
        kuyruk = ("\n\nÖnce bir soru sor (ör. *«bu yıl makine bazında oee»*); cevabın "
                  "üstünde *«bunu yorumla»* · *«neden böyle»* · *«ne yapmalıyız»* "
                  "diyebilirsin.")
    return bas + kuyruk


def _konusma_baglamsiz(q: str) -> str | None:
    """`§AY` — bağlam yokken bile **tanınan** bir konuşma türü var mı? → tür adı.

    ⚠ Zamir/kısalık şartı `sinifla`'nın bağlamlı dalıyla **birebir aynı** tutulur: orada
    bu şart *«fire analizini yap»* gibi bir **konu değişimini** konuşma sanmayı önlüyor;
    burada da aynı işi görür. Şartı gevşetmek, kullanıcının yeni sorusunu bir *«rapor
    yok»* cümlesine çevirirdi — yani bir kusuru düzeltirken daha görünür bir tanesini
    açardı.

    ⚠ `_NEDEN` **dışarıda**: *«neden fire yüksek olur»* bağlamsız da olsa gerçek bir
    veri sorusudur ve merdivenin cevaplaması gerekir. Ötekiler (`anlat`·`normal mi`·
    `ne yapmalı`·`işaret`) **tanım gereği** ekrandaki bir sonuca dairdir.

    🔴🔴 `§AY/S` — **`TUR_NORMAL`/`TUR_NE_YAPMALI` AYNI ŞARTA TABİ DEĞİLDİ, TAM RET
    ÜRETİYORDU.** Ölçüldü (canlı, iki bağımsız senaryo + bu belgenin kendi §10.3
    örneğine "optimizasyon önerisi ver" eklenince üçüncü kez): *«…araştır, … göster,
    … hangi ay en kötüsüydü açıkla, … ne yapmalıyız söyle»* gibi UZUN, baştan sona
    geçerli bir YENİ veri isteği, içinde bir yerde `ne_yapmali`/`normal` kalıbı
    geçtiği için **tamamen** "ekranda rapor yok" diye reddediliyordu — tıpkı bu
    fonksiyonun `anlat`/`işaret` için ZATEN önlediği hatanın (*"fire analizini yap"*
    yanlışlıkla konuşma sayılması) aynısı, yalnız iki tür için korunmamış hâli.
    `TUR_NORMAL`/`TUR_NE_YAPMALI` artık ÖTEKİLERLE **aynı** zamir/kısalık şartına
    tabi — yeni bir kural İCAT EDİLMEDİ, dosyanın kendi tutarlılık ilkesi
    genişletildi (bkz. `§NÇ`'nin kendi dersi: *"bir dosyada iki kural aynı ayrımı
    yapıyorsa, biri ötekini sormak zorundadır"*).
    """
    zamir = (_hit(q, _ISARET_ZAMIRI) or bool(_COGUL_ISARET_ZAMIR.search(q))
             or bool(_bu_su_zamir_mi(q)))
    for tur, kaliplar in ((TUR_ANLAT, _ANLAT), (TUR_NORMAL, _NORMAL),
                          (TUR_NE_YAPMALI, _NE_YAPMALI), (TUR_ISARET, _ISARET)):
        if not _hit(q, kaliplar):
            continue
        if zamir or _kisa_soru(q):
            return tur
    return None


def sinifla(soru: str, *, baglam_var: bool,
            capa_degerleri: frozenset[str] | None = None,
            acik_boyutlar: frozenset[str] | None = None) -> Niyet:
    """Takip sorusunu üç sınıftan birine ayırır. **Saf fonksiyon, LLM YOK.**

    `baglam_var`: elde bir cevap (cube_query) var mı? Yoksa "cevap üstünde konuşma"
    tanımsızdır — konuşulacak bir cevap yoktur ve soru yeni konudur. Bu kapı olmadan
    *"bu neden böyle?"* diye başlayan bir OTURUM konuşma sınıfına düşer ve
    çapalanacağı bir makbuz bulamaz.
    """
    q = _norm(soru or "")
    if not q.strip():
        return Niyet(sinif=SINIF_YENI, kural="bos-soru")
    if not baglam_var:
        # 🔴🔴 **`§X4` — BAĞLAMSIZ BİR MAKBUZ SORUSU DISCOVERY'YE DÜŞÜYORDU.**
        #
        # Ölçüldü (`X3` — önceki tur cevapsız kalmıştı, sonra *«bu kıyas hangi tarih
        # aralığını kapsıyor»*):
        #
        #     Discovery: bütçe aşıldı (25 sn) → dürüst ret
        #     "Bu soru için zamanında güvenilir bir sorgu üretemedim."
        #
        # ⊙ İki kayıp birden: (1) **25 saniye** ve bir Discovery ateşlemesi — `§0.0`'a
        # göre her ateşleme bir **mutfak eksikliği raporudur** ve bu, raporlanacak bir
        # eksiklik bile değildi; (2) cevap **yanlış cinsten**: Discovery ham SQL üretir,
        # oysa ortada **sorgulanacak bir rapor yok**. Hiçbir SQL *"ekranda ne var"*
        # sorusunu cevaplayamaz.
        #
        # ⊙ Doğru cevap tek satırlık ve **kesin olarak bilinen** bir olgudur: *ekranda bir
        # rapor yok.* Onu söylemek için ne LLM ne sorgu gerekir.
        #
        # ⚠ Sınıf `SINIF_YENI` **kalır** (yol değişmez); yalnız `kural` alanı gerçeği
        # söyler ki çağıran bu turu bir veri sorusu sanıp merdiveni sonuna kadar
        # inmesin. *Bir niyetin adını doğru koymak, onu doğru yere göndermenin ön koşuludur.*
        if _hit(q, _MAKBUZ):
            return Niyet(sinif=SINIF_YENI, kural="makbuz-baglamsiz",
                         kanit="hesabı sorulacak bir rapor yok")
        # 🔴🔴 `§AY` — **YORUMLANACAK ŞEY YOKKEN DISCOVERY ATEŞLİYORDU.**
        #
        # ⊙ Canlı ölçüm (curl `O` turu, 2026-08-10 · beş turluk thread):
        #
        #     t1 «bu yıl kalite sorunları» → netleştirme (ortada RAPOR YOK)
        #     t2 «bunu yorumla»            → 🔴 Discovery: 18 satır vardiya×gün OEE
        #
        # Kullanıcı **ekrandaki** cevabı yorumlamak istedi; ekranda cevap yoktu; sistem
        # ham SQL yazıp **alakasız** bir tablo üretti. Ve bedeli turla sınırlı kalmadı:
        # `adhoc` cevap thread'in **çapası** oldu ve sonraki turlar
        # *«bu takip mesajını ilişkilendiremedim»* ile öldü.
        #
        # ⊙ `§X4` bu kuralı **zaten yazmıştı** — ama yalnız `TUR_MAKBUZ`'a. Aynı gerekçe
        # bütün **konuşma** türleri için geçerlidir ve daha güçlüdür: *yok olan bir
        # raporu yorumlamak, açıklamak ya da «normal mi» diye sormak tanımsızdır.*
        # Hiçbir SQL bu soruları cevaplayamaz, çünkü sordukları şey veride değil
        # **ekranda**dır. Bugün altıncı kez: *bir kural yalnız bir basamakta geçerliyse,
        # o kural değil bir tesadüftür.*
        #
        # ⚠ Sınıf yine `SINIF_YENI` **kalır** (yol değişmez); yalnız `kural` gerçeği
        # söyler ki çağıran merdiveni sonuna kadar inmesin.
        # ⚠ Ve kapsam **dar**: yalnız zamir/kısalık şartını geçen ifadeler. *«fire
        # analizini yap»* bir konu değişimidir ve buraya girmez — `_konusma_baglamsiz`
        # o şartı `sinifla`'nın bağlamlı dalıyla **aynı** biçimde uygular.
        _ky = _konusma_baglamsiz(q)
        if _ky:
            return Niyet(sinif=SINIF_YENI, kural="konusma-baglamsiz", tur=_ky,
                         kanit="konuşulacak bir rapor yok")
        return Niyet(sinif=SINIF_YENI, kural="baglam-yok",
                     kanit="konuşulacak bir cevap yok")

    # 🔴 `§V1` — **MAKBUZ, YAPISALDAN ÖNCE GELİR ve bu bir istisna değil, kuralın kendisi.**
    #
    # `_YAPISAL`'ın gerekçesi şu: *"kullanıcı yeni sayılar bekliyorsa önce onları vermek
    # gerekir"*. Makbuz sorusunda bu gerekçe **tersine döner** — kullanıcı yeni sayı
    # istemiyor, eldeki sayının fişini istiyor.
    #
    # ⚠ Ve bu soyut bir ihtimal değil: kullanıcının kendi cümlesi *«bir **GRAFİK** gelince
    # bu nasıl hesaplandıya da cevap verebilmeli»*. `grafik` `_YAPISAL`'da bir sinyaldir;
    # öncelik yapısalda kalsaydı **kullanıcının literal örneği** yeni bir sorguya düşerdi.
    #
    # *Bir önceliği koyan gerekçe geçerliliğini yitirdiğinde, öncelik de yitirir.*
    _mkb = _hit(q, _MAKBUZ) or (_MAKBUZ_EDILGEN.search(q) and "nasıl <edilgen geçmiş>")
    if _mkb:
        return Niyet(sinif=SINIF_KONUSMA, tur=TUR_MAKBUZ,
                     kural=f"konusma:{TUR_MAKBUZ}", kanit=_mkb)

    # YAPISAL ÖNCELİĞİ. "aylık neden düştü?" hem düzenleme hem konuşma gibi görünür;
    # kullanıcı yeni sayılar bekliyorsa önce onları vermek gerekir — konuşma bir sonraki
    # turda hâlâ mümkündür, ama yanlış sayı geri alınamaz.
    yapisal = _hit(q, _YAPISAL)
    if yapisal:
        return Niyet(sinif=SINIF_YAPISAL, kural="yapisal-sinyal", kanit=yapisal)

    # `§AA4` — çoğul işaret zamiri de bir çapadır ve tekil olanla **aynı işi** görür.
    zamir = _hit(q, _ISARET_ZAMIRI) or (
        _COGUL_ISARET_ZAMIR.search(q) and "bunlar/şunlar/onlar") or _bu_su_zamir_mi(q)
    for tur, kaliplar in ((TUR_PAYLAS, _PAYLAS),
                          (TUR_TAKIP, _TAKIP),
                          (TUR_NE_YAPMALI, _NE_YAPMALI),
                          (TUR_NORMAL, _NORMAL),
                          (TUR_ANLAT, _ANLAT),
                          (TUR_NEDEN, _NEDEN),
                          (TUR_ISARET, _ISARET)):
        k = _hit(q, kaliplar)
        if not k:
            continue
        # 🔴🔴 `§NÇ` — **«NEDEN» İKİ KELİMEDİR: soru zarfı ve isim.**
        #
        # ⊙ Canlı ölçüm (curl `N` turu, 2026-08-10): *«en büyük **nedeni** hangi
        # makinede»* → `TUR_NEDEN` → **katkı analizi**. Kullanıcı *«hangi makinede»*
        # sordu, sistem *«hangi neden ne kadar değişti»* cevapladı.
        #
        # ⊙ Ayrım ekte değil **işarette**: bir *neden* takibi **eldeki cevabı** açıklar.
        # Soru, o cevapta **bulunmayan** bir boyutu anıyorsa açıklanacak şey ekranda
        # yoktur — kullanıcı yeni satırlar istiyordur. Yüklem katalogdan okunur
        # (`context.acik_boyutlar`), sözlükten değil: ADR-0008'in yasakladığı sınıfa
        # girmez, bu bir **kapsam karşılaştırmasıdır**.
        #
        # ⚠ Kapsam **yalnız `TUR_NEDEN`**: `NORMAL`/`NE_YAPMALI` eldeki sonuca dairdir ve
        # yanlarında bir boyut adı geçmesi onları yeni soru yapmaz. Dar tutulmasının
        # sebebi `§101.1`: bu kapı ne kadar genişse o kadar çok **doğru** konuşmayı
        # yapısala sürükler.
        #
        # *Bir cevabın üstünde konuşmak, o cevabın içinde olan şeyler hakkında
        # konuşmaktır; dışındakini sormak yeni bir sipariştir.*
        # 🔴🔴 **`§NÇ` ÇOK GENİŞTİ — VE BUNU CANLIDA ÖLÇTÜM.**
        #
        # ⊙ Ölçülen kusur (curl, 2026-08-11): *«bu yıl makine bazında duruş dakika»* →
        # *«**neden böyle**»* → **66 satırlık tablo**, not YOK. Kural doğru çalışıyordu:
        # `makine_duruslari`'nda `neden` **raporda bulunmayan** bir boyuttur, dolayısıyla
        # tur *yapısal* sayıldı ve *«nedene göre kır»* diye okundu.
        #
        # 🔴 Ama *«neden **böyle**»*'deki `böyle` bir **işaret zarfıdır** ve ekrandaki
        # cevaba işaret eder. Orada belirsizlik **yoktur**: kullanıcı yeni satır değil
        # açıklama istiyor. Kuralın kendi cümlesi de bunu söylüyor — *«bir cevabın
        # üstünde konuşmak, o cevabın içinde olan şeyler hakkında konuşmaktır»*.
        #
        # ⚠ `ADR-0008` temiz: işaret zarfları dilbilgisinin **kapalı** bir sınıfıdır
        # (`_ISARET_ZAMIRI`'nin kardeşi), bir alan sözlüğü değil.
        #
        # *Bir belirsizlik kuralını, belirsizliğin ortadan kalktığı yerde de uygulamak,
        # kuralı değil alışkanlığı sürdürmektir.*
        # 🔴🔴 **`§NÇ` HÂLÂ GENİŞTİ — VE KAÇAN VAKA ÇIPLAK «NEDEN»'DİR.**
        #
        # ⊙ Ölçüldü (curl `FF` turu, FF-6): *«departman bazında bu yıl kaza adedi»* →
        # *«**neden**»* → `refine → deterministik düzenleme`, **8 satır**, açıklama
        # **YOK**. Sebep: `isg.kok_neden`'in sinonimleri arasında birebir **«neden»**
        # var ve o boyut ekranda değil — yani kural *«kullanıcı yeni satır istiyor»*
        # diye okudu. Kullanıcı ise tek kelime yazmıştı.
        #
        # ⚠ `_ISARET_ZARFI` düzeltmesi *«neden **böyle**»*i kurtarıyordu; **çıplak**
        # «neden» ne zamir ne zarf taşır, o yüzden süzgeçten geçiyordu.
        #
        # 🔴 Ve doğru ayrım bu dosyada **zaten yazılıydı** — `_kisa_soru`'nun kendi
        # docstring'i tam bu örneği veriyor: *«Çok kısa takip soruları («neden?»,
        # «niye?») **zaten eldeki cevaba dairdir** — yeni bir konu üç kelimeden az
        # ifade edilmez.»* `§NÇ` o yüklemi hiç sormuyordu.
        #
        # ⚠ Ölçülen doğru-pozitif **korunur**: *«en büyük **nedeni** hangi makinede»*
        # beş kelimedir, kısa soru değildir → kural aynen ateşler.
        #
        # *Bir dosyada iki kural aynı ayrımı yapıyorsa, biri ötekini sormak zorundadır;
        # sormadığı gün, ikisi ayrı şeyler söyler.*
        if (tur == TUR_NEDEN and not zamir and not _ISARET_ZARFI.search(q)
                and not _kisa_soru(q)
                and acik_boyutlar and any(_syn_hit(q, b) for b in acik_boyutlar)):
            return Niyet(sinif=SINIF_YAPISAL, kural="§NÇ:ekranda-olmayan-boyut")
        # "ne yapmalıyız?" ve "normal mi?" zaten ELDEKİ sonuca dairdir — zamir aranmaz.
        # "neden"/"düşüş" ise tek başına yeni bir soru olabilir ("fire neden yüksek olur?"),
        # o yüzden mevcut cevaba bağlayan bir işaret zamiri istenir.
        #
        # ⟳ FAZ D2 — `TUR_ANLAT` da AYNI disipline tabi ve bu ZORUNLU: *"fire analizini
        # yap"* eldeki `oee` raporunu açmak DEĞİL, YENİ bir konu istemektir. Zamir/kısalık
        # şartı olmadan bu tür konu değişimini çalardı (`konu_degisimi` senaryo sınıfı).
        # Şart sağlanınca doğal biçimlerin hepsi geçiyor: "bunu analiz et" (zamir) ·
        # "özetle"/"yorumla"/"değerlendir" (tek kelime) · "yorumlar mısın" (iki kelime) ·
        # "bu grafiği açıkla" (zamir). Yanlış-negatif normal zincire düşer (zarar yok);
        # yanlış-pozitif kullanıcının yeni sorusunu YUTARDI.
        # ⚠ `TUR_TAKIP` de AYNI disipline tabi ve bu ZORUNLU: *"fire takibi nasıl
        # yapılır"* eldeki raporu zamanlamak DEĞİL, yeni bir konudur. Zamir/kısalık şartı
        # olmadan bu tür **konu değişimini çalardı** (`konu_degisimi` senaryo sınıfı).
        # ⚠ `TUR_PAYLAS` **zamir şartından MUAF**: *"müdüre 3 cümle yaz"* eldeki cevaba
        # dair olduğunu **hedefiyle** söyler (*müdüre*, *3 cümle*) ve bir işaret zamiri
        # taşımak zorunda değildir. Şart konsaydı en doğal ifade yine kapalı kalırdı —
        # yani düzeltilen kusurun aynısı, bir kat aşağıda tekrarlanırdı.
        if (tur in (TUR_NEDEN, TUR_ISARET, TUR_ANLAT, TUR_TAKIP)
                and not zamir and not _kisa_soru(q)
                # 🔴 Karşılaştırmalı sıfat zamirin yerini tutar — yalnız `TUR_NEDEN`'de
                # ve yalnız ekranda rapor varken. Ötekilerde (`ANLAT`/`TAKİP`) bu gevşeme
                # konu değişimini çalardı; *"fire analizini yap"* bir karşılaştırma
                # taşımaz zaten, ama sınırı **yazarak** koymak gerekiyor.
                # 🔴 Ekrandaki raporun bir satırını adlandırmak, zamirden **güçlü**
                # bir bağdır: zamir *"şu"* der, değer **hangisi** olduğunu söyler.
                # 🔴 Ve bir **belgisiz zamir** de zamirdir (`§36`): *"diğerlerinden"*
                # takip turunda ekrandaki kalan satırlardan başka bir şeye işaret edemez.
                # ⚠ Kapsam `TUR_NEDEN` + `baglam_var` ile **sınırlı**: `ANLAT`/`TAKİP`'te
                # aynı gevşeme konu değişimini çalardı (*"diğer makineleri göster"* yeni
                # bir sorudur). *Bir gevşemeyi ölçülen türle sınırlamak, onu bir sonraki
                # turda geri almak zorunda kalmamaktır.*
                # 🔴🔴 `§BB-A` — **ÜSTÜNLÜK İFADESİ DE BİR ÇAPADIR.**
                #
                # Ölçüldü (BB turu, iki kanıt): *«en kötü vardiya neden geride»* (`BB2`) ve
                # *«en kötüsünün rework sebeplerini kır»* (`BB9`). İkisi de ekrandaki
                # raporun **bir satırını** gösteriyor — ama zamir taşımadıkları için
                # konuşma sınıfına hiç girmediler ve `§AA1`'in akran kıyası **ateşlemedi**.
                #
                # ⊙ Oysa bu bağ zamirden **güçlüdür**: *"şu"* bir şeyi işaret eder,
                # *«en kötü»* ekrandaki satırlardan **hangisi olduğunu hesaplar**. Bu
                # dosyanın kendi gerekçesi bunu zaten kuruyor (*"ekrandaki raporun bir
                # satırını adlandırmak, zamirden güçlü bir bağdır"*) ama yalnız **değer
                # adı** için; **üstünlük** o kapsamın dışında kalmıştı.
                #
                # ⚠ Yeni sözlük **yok**: `_USTUNLUK_RE` `cube_router`'ın — çekimin tek
                # sahibi orası ve buraya ikinci bir kopya yazılmıyor.
                # ⚠ Kapsam `TUR_NEDEN` + `baglam_var` ile sınırlı, kardeş gevşemelerle
                # birebir aynı: ekranda rapor yoksa *«en kötü X neden»* yeni bir sorudur.
                #
                # *Bir satırı adıyla göstermekle, onu üstünlüğüyle göstermek arasında
                # kullanıcı açısından hiçbir fark yoktur.*
                and not (tur == TUR_NEDEN and baglam_var
                         and (_capaya_deger(q, capa_degerleri)
                              or _BELGISIZ_ZAMIR.search(q)
                              or _USTUNLUK_CAPA.search(q)))):
            continue
        return Niyet(sinif=SINIF_KONUSMA, tur=tur, kural=f"konusma:{tur}", kanit=k)

    return Niyet(sinif=SINIF_YENI, kural="kalip-yok")


#: FAZ 6.8 — `niyet_garsondan`'ın kabul ettiği kapalı küme. Garson bunun DIŞINDA bir
#: `tur` uydurursa (halüsinasyon) sonuç `None`e döner — bir tür İCAT EDİLMEZ.
_GARSON_TUR_GECERLI = frozenset({TUR_NEDEN, TUR_NE_YAPMALI, TUR_NORMAL, TUR_ANLAT, TUR_MAKBUZ})


def niyet_garsondan(karar: dict, mesaj: str) -> "Niyet | None":
    """🔴🔴 FAZ 6.8 — **GARSON DEVRİ, `sinifla()`in kalıp bulamadığı yerde.**

    `sinifla()` yukarıda `kural="kalip-yok"` döndürdüğünde (hiçbir kelime listesi/ek
    zinciri eşleşmedi) EN ÜST KURAL'ın kendi cümlesi devreye girer: *"bir cümle
    anlaşılmıyorsa çözüm route'u genişletmek değil devri tetiklemektir."* Bu fonksiyon
    o devrin SONUCUNU (garsonun LLM kararı, `app/llm.py::_takip_sinif_system` ile
    üretilir) bu modülün ZATEN TANIDIĞI `Niyet` sözleşmesine çevirir — yeni bir sınıf
    İCAT EDİLMEZ, yalnız `kural` alanı kaynağı söyler (`"garson-devri"`).

    ⚠ **Katkı listesi değil bir HAKEM kararı**: bu fonksiyon `karar` sözlüğünü METİN
    olarak değil YAPISAL olarak okur (`konusma`/`tur` anahtarları) — çağıran
    (`routers/ask.py::_garson_konusma_dene`) ham LLM çıktısını ayrıştırıp buraya
    sözlük verir (`KAT-1`: JSON ayrıştırma orada, tür sözleşmesi burada).

    Fail-closed: `konusma` yoksa/`False`sa, `tur` kapalı kümenin dışındaysa ya da
    `karar` bozuksa `None` döner — çağıran mevcut `niyet`i (dürüst ret) KORUR. Yani en
    kötü durumda garson devri hiç OLMAMIŞ gibi davranılır, asla uydurma bir tür YAYILMAZ.
    """
    if not isinstance(karar, dict) or not karar.get("konusma"):
        return None
    tur = karar.get("tur")
    if tur not in _GARSON_TUR_GECERLI:
        return None
    return Niyet(sinif=SINIF_KONUSMA, tur=tur, kural="garson-devri",
                 kanit=(mesaj or "")[:120])


#: 🔴 **KÖK ÇÖZÜM — kelime listesi SİLİNDİ.** Önceki sürüm bir `_KARSILASTIRMA` listesi
#: (`yuksek`·`dusuk`·`fazla`…) ve bir uzunluk eşiği (4 kelime) taşıyordu. Çalışıyordu ama
#: **tikel**di: *"yıkama neden geride kaldı"* · *"3. vardiya neden zayıf"* · *"bu aşama
#: neden sorunlu"* yine düşerdi ve her biri listeye bir kelime daha eklettirirdi
#: (`ADR-0008`: *dile kelime listesiyle yetişilmez*).
#:
#: ⊙ Asıl bağ **yapısal**: takip sorusu, ekrandaki raporun **bir satırını adlandırıyor**.
#:
#: | soru | bağ |
#: |---|---|
#: | `yıkama neden yüksek` | `yıkama` ∈ mevcut kırılımın **değerleri** ✅ |
#: | `3. vardiya neden düşük` | `3. Vardiya (00-08)` ∈ `vardiya` değerleri ✅ |
#: | `fire oranı neden yüksek olur genel olarak` | `fire oranı` bir **ölçü adı** → bağ YOK |
#:
#: 🔴 Ve bu ayrım *"genel olarak"* sorusunu **kendiliğinden** dışarıda bırakır — uzunluk
#: eşiğine gerek kalmaz. Kelime listesi de, eşik de silindi.
#:
#: ⚠ Değerleri **bu modül okumaz**: çağıran verir (`capa_degerleri`). Sebep `KAT-1`:
#: *"hangi değerler ekranda"* sorusunun sahibi `ask.py`'nin bağlam katmanıdır, bir
#: sınıflandırıcı değil. Boş geçilirse davranış **bugünküyle birebir** (zamir şartı).
#:
#: *Bir kusuru gördüğü yerde yamamak, sınıfını görmemenin en pahalı biçimidir: her yeni
#: örnek yeni bir yama ister ve yamalar birbirini tanımaz.*


def _capaya_deger(q: str, capa_degerleri: frozenset[str] | None) -> bool:
    """Soru, ekrandaki raporun bir **satırını** adlandırıyor mu?

    🔴🔴 Kullanıcı bulgusu (2026-08-26): *"ram 3 neden düşük"* → `RAM-3`'ün ZATEN
    ekrandaki raporda olmasına RAĞMEN bu tur *yeni bir konu* sayılıyordu (`kalip-yok`)
    — `_NEDEN` sözlüğü eşleşiyordu ama bu fonksiyon *"ram 3" `capa_degerleri`'nde YOK*
    diyordu, çünkü katalog değeri **tireli** (`RAM-3` → `_norm` sonrası `ram-3`),
    kullanıcı **boşlukla** yazmıştı (`ram 3`) — `_norm()` (ASCII-katlama) tire/boşluk
    ayrımını hiç birleştirmiyor (o onun işi değil, yapısal bir işaret). Sonuç: `neden`
    hiç `_anlat`/`kok_neden`/`contribution`'a ULAŞMADAN, sıradan yeni bir sorgu gibi
    çözülüyordu — kullanıcının bildirdiği "sadece ham sayı geliyor" şikayetinin GERÇEK
    kökü BUYDU (`plan_tuketici._anlat`'ın HESAPLA/BAGLA düzeltmesi bile bu tur hiç
    devreye girmediği için işe yaramıyordu).

    ⚠ Kök çözüm `_norm()`'u DEĞİŞTİRMEZ (o repo-genelinde paylaşılan tek normalize edici
    — küp/ölçü/boyut eşleştirmesinde tire ANLAMLI olabilir, orayı gevşetmek başka
    kusurlar açabilirdi). Bu fonksiyonun işi farklı ve DAR: *"bu katalog değeri
    cümlede geçiyor mu"* — gevşek bir metin-içinde-geçme testi, yapısal bir eşleştirme
    değil. Tire/boşluk eşdeğerliği yalnız BURADA, bu dar kapsamda uygulanır.
    """
    if not capa_degerleri:
        return False
    _q = q.replace("-", " ")
    return any(d and d.replace("-", " ") in _q for d in capa_degerleri)


def konusma_sozcukleri(q: str) -> set[str]:
    """🔴 **`§46` — KONUŞMA FİİLLERİ BİR KONU DEĞİLDİR.**

    ## Ölçülen kusur

    | soru | sonuç |
    |---|---|
    | `bu yıl kar marjı en düşük 3 müşteri ve nedenini **analiz et**` | *«"analiz" başka bir konu gibi görünüyor»* |
    | `bu yıl makine bazında fire oranını kıyasla ve listele ve en yüksek olanı **analiz et**` | 🔴 `source=catalog` — **tüm menü dökümü** |
    | `bu yıl vardiya bazında oee **yorumla**` | ✅ çalışıyor |

    Üçü de aynı yapıda; ikisi düşüyor. Ve düşenler **kullanıcının kendi örnek cümle
    tarzı** (*"…en düşüğün neden diğerlerinden düşük olduğunu bul analiz et"*).

    ## Kök

    `_ANLAT` **`analiz et`'i zaten tanıyor** — ama `sinifla()` yalnız **takip** turunda
    koşar. **Taze** bir soruda `route()`'un kapsam kapısı `analiz`/`et` sözcüklerini
    *"tanımadığım bir konu"* sayar ve soruyu — geri kalanı tamamen anlaşılmışken —
    reddeder.

    ⊙ Bu, bu depoda ölçülmüş *"ayrıştırıcı tüketti → bilinen sayılır"* kuralının
    **üçüncü** örneği (`ustunluk_sozcukleri` · `_LISTE_RE` · şimdi bu). Kelime listesi
    **yazılmıyor**: sınıflandırıcının **kendi** kalıpları okunuyor, yani iki taraf
    ayrışamaz (`KAT-1`).

    *Bir cümlenin ne yapılacağını söyleyen kısmı, neyin sorulduğunu söyleyen kısmı
    gölgelememelidir.*

    ⚠ Kapsam **dar**: yalnız *"cevabın üstünde konuşma"* fiilleri (`ANLAT`·`NEDEN`·
    `NE_YAPMALI`). `TAKIP`/`PAYLAS` **dışarıda** — onlar bir **eylem** ister (bildirim,
    mail) ve bir veri sorusunda geçmeleri gerçekten yeni bir konudur.
    """
    out: set[str] = set()
    qn = _norm(q or "")
    for kaliplar in (_ANLAT, _NEDEN, _NE_YAPMALI):
        for k in kaliplar:
            if k in qn:
                out.update(re.findall(r"[a-z]+", k))
    return out


def _kisa_soru(q: str) -> bool:
    """Çok kısa takip soruları ("neden?", "niye?") zaten eldeki cevaba dairdir —
    yeni bir konu üç kelimeden az ifade edilmez. Zamir aramak burada gereksiz katılık
    olurdu ve en doğal konuşma biçimini kapı dışında bırakırdı."""
    return len(re.findall(r"[a-z]+", q)) <= 2


def makbuza(n: Niyet) -> dict:
    """Sınıflandırma kararı makbuza yazılır: *"neden bu cevap bu biçimde geldi?"*"""
    return {"followup_class": n.sinif, "followup_kind": n.tur,
            "followup_rule": n.kural, "followup_evidence": n.kanit}


def neden_sorusu(q: str) -> bool:
    """🔴🔴 `§KN-taze` — soru, **bağlamdan bağımsız olarak**, bir *«neden»* taşıyor mu?

    ⊙ Ölçüldü (curl `DD` turu, DD-20): *«bu yıl enerji tüketimi **neden yüksek**»* →
    düz bir metrik döndü (`elektrik_tuketimi_kwh`, `tep_toplam`), kök-neden **hiç**
    çalışmadı. Sebep bu dosyanın kendi kararıydı ve doğruydu: `_NEDEN` bağlamsız dalda
    **dışarıda** bırakılmıştı, çünkü *«neden fire yüksek olur»* gerçek bir **veri
    sorusudur** ve merdivenin cevaplaması gerekir.

    ⊙ Eksik olan o karar değil, **devamıydı**: merdiven sayıyı verir, ama sorunun
    *«neden»* kısmını kimse ele almaz. Kullanıcının şartında bir takip koşulu yok —
    *«neden sorusu geldiğinde adeta insan zihnini simüle etmeliyiz»*.

    ⚠ Bu yüklem **yol seçmez**: cevap bugünkü gibi hesaplanır, `§KN` onun **üstüne**
    yazar. Yanlış-pozitifi ucuzdur (fazladan bir ayrıştırma cümlesi), yanlış-negatifi
    ise kullanıcının sorusunun yarısını cevapsız bırakmaktır.

    ⚠ Sözlük `_NEDEN`'dir — **yeni bir liste yazılmaz** (`KAT-1`): aynı kalıplar
    `sinifla`'nın takip dalını da besliyor ve ikisi ayrışamaz.

    *Bir soruyu iki parçaya bölüp yalnız birini cevaplamak, cevaplamamanın kibar hâlidir.*
    """
    return bool(_hit(_norm(q or ""), _NEDEN))
