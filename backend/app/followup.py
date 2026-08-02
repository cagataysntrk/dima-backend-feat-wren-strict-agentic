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

# Kalıplar `_norm` sonrası (ASCII, küçük harf) yazılır. Sonu "!" olanlar TAM KELİME
# eşleşir — Faz D3'ün `_syn_hit` disiplini; kalanlar geçerli ek zinciri kabul eder.
_NEDEN = ("neden", "nicin", "niye", "sebebi", "sebep", "kaynaklan", "yol acan",
          "nereden geliyor", "niden")
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
_ISARET = ("su dusus", "su artis", "su sicrama", "su kirilma", "bu dusus", "bu artis",
           "sicrama", "dusus", "kirilma", "anomali", "aykiri")

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
    for tur, kaliplar in ((TUR_NE_YAPMALI, _NE_YAPMALI),
                          (TUR_NORMAL, _NORMAL),
                          (TUR_NEDEN, _NEDEN),
                          (TUR_ISARET, _ISARET)):
        k = _hit(q, kaliplar)
        if not k:
            continue
        # "ne yapmalıyız?" ve "normal mi?" zaten ELDEKİ sonuca dairdir — zamir aranmaz.
        # "neden"/"düşüş" ise tek başına yeni bir soru olabilir ("fire neden yüksek olur?"),
        # o yüzden mevcut cevaba bağlayan bir işaret zamiri istenir.
        if tur in (TUR_NEDEN, TUR_ISARET) and not zamir and not _kisa_soru(q):
            continue
        return Niyet(sinif=SINIF_KONUSMA, tur=tur, kural=f"konusma:{tur}", kanit=k)

    return Niyet(sinif=SINIF_YENI, kural="kalip-yok")


def _kisa_soru(q: str) -> bool:
    """Çok kısa takip soruları ("neden?", "niye?") zaten eldeki cevaba dairdir —
    yeni bir konu üç kelimeden az ifade edilmez. Zamir aramak burada gereksiz katılık
    olurdu ve en doğal konuşma biçimini kapı dışında bırakırdı."""
    return len(re.findall(r"[a-z]+", q)) <= 2


def makbuza(n: Niyet) -> dict:
    """Sınıflandırma kararı makbuza yazılır: *"neden bu cevap bu biçimde geldi?"*"""
    return {"followup_class": n.sinif, "followup_kind": n.tur,
            "followup_rule": n.kural, "followup_evidence": n.kanit}
