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

_ANLAT = ("analiz et", "analiz eder", "analizini", "yorumla", "yorumlar misin",
          "yorumun", "yorumlasana", "degerlendir", "aciklar misin", "acikla",
          "ozetle", "ozetler misin", "ne diyor", "ne anlama gel", "ne anlama geliyor",
          "okur musun",
          "anlat", "yorum yap", "incele")

# Konuşma sınıfı YALNIZ bunlarla tetiklenmez: soru aynı zamanda MEVCUT CEVABA işaret
# etmelidir. "neden" tek başına yeni bir soru da olabilir ("fire neden yüksek olur?").
# Bu zamirler soruyu ELDEKI sonuca bağlar.
_ISARET_ZAMIRI = ("bu", "bunu", "bunun", "buradaki", "su", "sunu", "sunun",
                  "yukaridaki", "bu rapor", "bu tablo", "bu grafik", "bu sonuc")

# YAPISAL düzenleme sinyalleri — bunlar varsa soru sorguyu DEĞİŞTİRMEK istiyordur ve
# konuşma sınıfına ALINMAZ. Çakışma gerçektir: "aylık neden düştü?" hem düzenleme hem
# konuşma gibi görünür; öncelik YAPISALDA olmalıdır çünkü kullanıcı yeni sayılar bekler.
_YAPISAL = ("bazinda", "bazli", "kirilim", "aylik", "haftalik", "gunluk", "yillik",
            "ceyrek", "sirala", "ilk ", "en yuksek", "en dusuk", "top ", "grafik",
            "tablo", "pasta", "cizgi")


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


def _hit(q: str, kaliplar: tuple[str, ...]) -> str | None:
    """Eşleşen ilk kalıbı döndürür — `_syn_hit` disipliniyle (kelime başı + ek zinciri).

    Çok kelimeli kalıplar bölünmez; `_syn_hit` onları olduğu gibi arar.
    """
    for k in kaliplar:
        if _syn_hit(q, k):
            return k
    return None


def sinifla(soru: str, *, baglam_var: bool) -> Niyet:
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
        return Niyet(sinif=SINIF_YENI, kural="baglam-yok",
                     kanit="konuşulacak bir cevap yok")

    # YAPISAL ÖNCELİĞİ. "aylık neden düştü?" hem düzenleme hem konuşma gibi görünür;
    # kullanıcı yeni sayılar bekliyorsa önce onları vermek gerekir — konuşma bir sonraki
    # turda hâlâ mümkündür, ama yanlış sayı geri alınamaz.
    yapisal = _hit(q, _YAPISAL)
    if yapisal:
        return Niyet(sinif=SINIF_YAPISAL, kural="yapisal-sinyal", kanit=yapisal)

    zamir = _hit(q, _ISARET_ZAMIRI)
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
                and not (tur == TUR_NEDEN and baglam_var and _karsilastirmali(q))):
            continue
        return Niyet(sinif=SINIF_KONUSMA, tur=tur, kural=f"konusma:{tur}", kanit=k)

    return Niyet(sinif=SINIF_YENI, kural="kalip-yok")


#: 🔴 **KARŞILAŞTIRMALI SIFAT — zamirin yerini tutan yapısal bağ.** Canlı curl'de
#: ölçüldü: *"yıkama neden yüksek"* ve *"3. vardiya neden düşük"* `TUR_NEDEN`'e
#: **girmiyordu** (zamir yok, üç-dört kelime), tur **Discovery'ye** düşüyordu:
#: **78.834 ms** ve **54.231 ms**, biri `cube=adhoc` ham SQL, öteki **0 satır**.
#:
#: ⊙ Oysa bağ zamirden **daha güçlü**: kullanıcı ekrandaki raporun bir **satırını**
#: adlandırıyor (`yıkama` bir `asama` değeri, `3. vardiya` bir `vardiya` değeri).
#:
#: 🔴 Ve *"yüksek/düşük"* tek başına bir **karşılaştırmadır**: neye göre yüksek? Ekranda
#: duran şeye göre. Yani sıfat, bağlamı **ima etmekle kalmaz, gerektirir**.
#:
#: ⚠ Şart `baglam_var` ile birlikte uygulanır — ekranda rapor yoksa *"fire neden yüksek
#: olur"* yine yeni bir sorudur ve bu dal hiç açılmaz.
#:
#: *Bir cümleyi eldeki cevaba bağlayan tek şey zamir değildir; bir karşılaştırma da
#: bağlar — çünkü karşılaştırmanın öteki ucu zaten ekrandadır.*
_KARSILASTIRMA = ("yuksek", "yüksek", "dusuk", "düşük", "fazla", "az ",
                  "kotu", "kötü", "iyi", "geride", "onde", "önde")


#: 🔴 **UZUNLUK SINIRI — ve kapı bunu KENDİ yakaladı.** İlk yazımda yalnız karşılaştırmalı
#: sıfat aranıyordu ve `test_UZUN_neden_sorusu_ZAMIR_ister` kırmızı verdi:
#: *"fire oranı neden yüksek olur genel olarak"* bir **yeni konudur**, takip değil —
#: ve haklıydı.
#:
#: ⊙ Ayıran şey uzunluk: ekrandaki bir **satırı** adlandıran soru kısadır
#: (*"yıkama neden yüksek"* 3 · *"3. vardiya neden düşük"* 3 kelime), genel bir soru
#: uzar (*"…olur genel olarak"* 6).
#:
#: ⚠ Bu bir tahmin değil `_kisa_soru`'nun **aynı ilkesi**, bir kademe gevşetilmiş hâli:
#: orada eşik 2 (zamirsiz, sıfatsız), burada 4 — çünkü karşılaştırmalı sıfat **kendisi**
#: bir bağ taşır ve o bağ iki kelimelik payı hak eder.
#:
#: *Bir gevşemeyi, gevşettiği kuralın kendi ölçüsüyle sınırlamak, ikinci bir kural
#: yazmaktan güvenlidir.*
_KARSILASTIRMA_AZAMI_KELIME = 4


def _karsilastirmali(q: str) -> bool:
    return (any(w in q for w in _KARSILASTIRMA)
            and len(re.findall(r"[a-z]+", q)) <= _KARSILASTIRMA_AZAMI_KELIME)


def _kisa_soru(q: str) -> bool:
    """Çok kısa takip soruları ("neden?", "niye?") zaten eldeki cevaba dairdir —
    yeni bir konu üç kelimeden az ifade edilmez. Zamir aramak burada gereksiz katılık
    olurdu ve en doğal konuşma biçimini kapı dışında bırakırdı."""
    return len(re.findall(r"[a-z]+", q)) <= 2


def makbuza(n: Niyet) -> dict:
    """Sınıflandırma kararı makbuza yazılır: *"neden bu cevap bu biçimde geldi?"*"""
    return {"followup_class": n.sinif, "followup_kind": n.tur,
            "followup_rule": n.kural, "followup_evidence": n.kanit}
