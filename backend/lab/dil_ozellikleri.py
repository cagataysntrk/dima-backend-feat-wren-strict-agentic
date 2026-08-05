"""TÜRKÇE İŞ SORUSU — DİLSEL ÖZELLİK TAKSONOMİSİ ve KAPSAM DEDEKTÖRLERİ.

## 🔴 Bu dosyanın varlık sebebi

Kullanıcı iki gerçek kusur bildirdi ve sordu: *"testler bunları yakalar mı?"*
Cevap **hayırdı**. İkisini eksen olarak ekledim. Sonra doğru soruyu sordu:

> *"bu ikisi en basiti bu tarz o zaman **binlerce eksik** vardır"*

Ve haklıydı. **Eksen eklemek bir çözüm değildir** — çünkü hangi eksenin eksik olduğunu
ancak bir kusur **canlıda patladığında** öğreniyoruz. O zaman test ortamı, kusurları
bulan bir alet değil, kusurların **arkasından koşan** bir alet olur.

*Bir test kümesinin kapsamı, yazarının aklına gelenler kadardır — o kapsam **ölçülmediği**
sürece.* Bu dosya kapsamı ölçülebilir kılar: dilin özellikleri **önce** sayılır, sonra
üretecin bunların kaçını ürettiği **rakamla** söylenir. Kapsanmayan bir özellik artık
bilinmeyen bir bilinmeyen değil, **raporun üstünde kırmızı bir satırdır**.

## Nasıl kullanılır

```python
from lab.dil_ozellikleri import kapsam_olc, OZELLIKLER
rapor = kapsam_olc([v["soru"] for v in vakalar])
rapor["bos"]     # → hiç üretilmeyen özellikler  ← 🔴 test ortamının deliği
rapor["zayif"]   # → 5'ten az üretilen özellikler
```

## Taksonomi nereden geldi — uydurulmadı

| aile | kaynak |
|---|---|
| ad çekimi · iyelik · çoğul | Türkçe dilbilgisinin **kapalı** ek kümesi (sonlu, sayılabilir) |
| fiil kipi/kişi | aynı — kapalı küme |
| söylem (dolgu · anafora · eksilti · öz-düzeltme) | `lab/deneyim.py`'nin 15 senaryosu + canlı turlar |
| sorgu semantiği | `cube_router`'ın **kendi** tanıdığı niyetler + katalog yapısı |
| dönem biçimi | `_period_hit_words`'ün tanıdığı biçimler + canlı kusur (`şubata`) |
| yazım | ölçülmüş kullanıcı hataları (harf devrikliği/düşmesi) + `_norm`'un kapsamı |
| kod-değiştirme | kataloğun **kendi** İngilizce sinonimleri (`revenue`, `downtime`, `oee`) |

⚠ **Kapalı kümelerin değeri:** Türkçenin durum ekleri **altı**, iyelik ekleri **altı**dır.
Bunlar bir liste değil, dilin **tamamı**dır — yani bu ailelerde *"acaba unuttuğum bir ek
var mı"* sorusu **kapanmıştır**. Açık olan aileler (söylem, semantik) ise açık kalır ve
bunu dosya **kendisi söyler** (`ACIK_AILELER`).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable

# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Ozellik:
    """Bir dilsel özellik + onu **tanıyan** dedektör.

    ⚠ `dedektor` bir **kural**dır, örnek listesi değil: örnek listesi yalnız kendi
    örneklerini tanır ve kapsam ölçümünü totolojiye çevirir.
    """
    kod: str
    aile: str
    aciklama: str
    ornek: str
    dedektor: Callable[[str], bool] = field(repr=False)


def _re(desen: str) -> Callable[[str], bool]:
    """Türkçe harfleri **koruyan** regex dedektörü.

    🔴 Bu satır bir kusurun anısıdır: `_uncovered` `[a-z]+` kullandığı için
    `şubata` → `ubata`, `üzerindeki` → `zerindeki`, `aylık` → `ayl` diye
    **parçalanıyordu**. Ölçüm aracı aynı hatayı yaparsa, kusuru göremez —
    *bir cetvel, ölçtüğü şeyle aynı çarpıklığı taşıyorsa düzgün gösterir.*
    """
    r = re.compile(desen, re.IGNORECASE | re.UNICODE)
    return lambda q: bool(r.search(q))


# Türkçe harf sınıfları — `[a-z]` YETMEZ.
TR = "a-zA-ZçÇğĞıİöÖşŞüÜ"
_S = rf"[{TR}]"           # tek Türkçe harf
_W = rf"{_S}+"            # Türkçe kelime


# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 1 · AD ÇEKİMİ — 🔴 KAPALI KÜME (Türkçede altı durum, hepsi burada)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Canlı kusur tam buradaydı: `şubata` (yönelme). Ay **biliniyordu**, **eki** tanınmadı.
# Kapalı küme olduğu için bu aile artık **tamamlanmıştır**: altı durumun altısı da
# ölçülüyor, ve yedincisi yok.

_AD_CEKIMI = [
    Ozellik("ad.yalin", "ad_cekimi", "Yalın hâl — eksiz", "mart cirosu",
            _re(rf"\b(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\b")),
    Ozellik("ad.belirtme", "ad_cekimi", "Belirtme (-ı/-i/-u/-ü)", "ciroyu göster",
            _re(rf"{_S}{{3,}}(yı|yi|yu|yü|ı|i|u|ü)\b(?=\s+(göster|getir|ver|hesapla|ölç|listele|kıyasla))")),
    Ozellik("ad.yonelme", "ad_cekimi", "🔴 Yönelme (-a/-e) — CANLI KUSUR", "şubata göre",
            _re(rf"{_S}{{3,}}(ya|ye|a|e)\b\s*(göre|kadar|kıyasla|karşı)")),
    Ozellik("ad.bulunma", "ad_cekimi", "Bulunma (-da/-de/-ta/-te)", "martta ne oldu",
            _re(rf"{_S}{{3,}}(da|de|ta|te)\b")),
    Ozellik("ad.ayrilma", "ad_cekimi", "Ayrılma (-dan/-den/-tan/-ten)", "marttan beri",
            _re(rf"{_S}{{3,}}(dan|den|tan|ten)\b")),
    Ozellik("ad.tamlayan", "ad_cekimi", "Tamlayan (-ın/-in/-un/-ün)", "martın cirosu",
            _re(rf"{_S}{{3,}}(nın|nin|nun|nün|ın|in|un|ün)\b\s+{_W}")),
    Ozellik("ad.vasita", "ad_cekimi", "Vasıta (-la/-le/ile)", "ocakla kıyasla",
            _re(rf"({_S}{{3,}}(yla|yle|la|le)\b|\bile\b)")),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 2 · İYELİK ve ÇOĞUL — 🔴 KAPALI KÜME
# ═══════════════════════════════════════════════════════════════════════════════
#
# `randımanımız`, `ciromuz`, `firemiz` — bir yöneticinin en doğal konuşma biçimi.
# ⚠ Ölçüldü: `randıman` çalışıyor, `randımanımız` da çalışıyor — yani morfoloji
# tarafı sağlam. Ama bu **ölçülerek** bilindi; ölçülmeseydi varsayım olurdu.

_IYELIK = [
    Ozellik("iy.1tekil", "iyelik", "1. tekil iyelik (-m)", "ciromu göster",
            _re(rf"{_S}{{3,}}(ım|im|um|üm)\b")),
    Ozellik("iy.1cogul", "iyelik", "1. çoğul iyelik (-mız) — en sık yönetici dili",
            "randımanımız kaç",
            _re(rf"{_S}{{3,}}(mız|miz|muz|müz)\b")),
    Ozellik("iy.3tekil", "iyelik", "3. tekil iyelik (-ı/-si)", "cirosu ne kadar",
            _re(rf"{_S}{{3,}}(sı|si|su|sü)\b")),
    Ozellik("iy.3cogul", "iyelik", "3. çoğul iyelik (-ları)", "müşterilerinin cirosu",
            _re(rf"{_S}{{3,}}(ları|leri)\b")),
    Ozellik("iy.cogul", "iyelik", "Çoğul (-lar/-ler)", "makineler",
            _re(rf"{_S}{{3,}}(lar|ler)\b")),
    Ozellik("iy.zincir", "iyelik", "🔴 İyelik + durum zinciri", "ciromuzu · randımanımızı",
            _re(rf"{_S}{{3,}}(mız|miz|muz|müz|sı|si|su|sü)(nı|ni|nu|nü|na|ne|nda|nde|ndan|nden)\b")),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 3 · FİİL — 🔴 KAPALI KÜME (kip/kişi sonlu)
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 Ölçülen kusur sınıfı: `fire` çalışıyor, `fire verdik` çalışmıyor. Fiil bir
# **kavram değildir** — cevabı değiştirmez — ama kapsam kapısına takılır.

_FIIL = [
    Ozellik("f.emir", "fiil", "🔴 Emir kipi — CANLI KUSUR (`ölç`)", "ciroyu ölç",
            _re(r"\b(ölç|kıyasla|hesapla|getir|göster|ver|çıkar|listele|bul|karşılaştır|analiz et|yorumla|özetle)\b")),
    Ozellik("f.gecmis1c", "fiil", "🔴 Görülen geçmiş 1.çoğul (`verdik`)", "ne kadar fire verdik",
            _re(rf"{_S}{{2,}}(dık|dik|duk|dük|tık|tik|tuk|tük)\b")),
    Ozellik("f.gecmis3t", "fiil", "Görülen geçmiş 3.tekil", "ciro düştü",
            _re(rf"{_S}{{2,}}(dı|di|du|dü|tı|ti|tu|tü)\b")),
    Ozellik("f.simdiki", "fiil", "Şimdiki zaman (-yor)", "artıyor mu",
            _re(r"\w*(ıyor|iyor|uyor|üyor)\b")),
    Ozellik("f.genis", "fiil", "Geniş zaman", "yılı nerede kapatır",
            _re(rf"{_S}{{3,}}(ar|er|ır|ir|ur|ür)\b\s*$")),
    Ozellik("f.gelecek", "fiil", "Gelecek zaman (-ecek)", "ne olacak",
            _re(r"\w*(acak|ecek)\b")),
    Ozellik("f.gereklilik", "fiil", "Gereklilik (-meli)", "ne yapmalıyız",
            _re(r"\w*(malı|meli)\w*\b")),
    Ozellik("f.soru_eki", "fiil", "Soru eki (mı/mi/mu/mü)", "iyi miyiz",
            _re(r"\b(mı|mi|mu|mü)\w*\b")),
    Ozellik("f.olumsuz", "fiil", "Olumsuzluk (-ma/-me)", "düşmedi mi",
            _re(r"\w*(madı|medi|mıyor|miyor|mez|maz)\b")),
    Ozellik("f.sifat_fiil", "fiil", "Sıfat-fiil (-en/-an, -dığı)", "en çok satan müşteri",
            _re(rf"{_S}{{3,}}(an|en)\b\s+{_W}|{_S}{{3,}}(dığı|diği|duğu|düğü)\b")),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 4 · SÖYLEM — ⚠ AÇIK KÜME (dil değil, kullanım; tamamlanmaz)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Canlı kusur: `…etkisini ölç **yani** kıyasla` — `yani` bir **öz-düzeltme**dir:
# kullanıcı düşüncesini yürürken düzeltiyor. Anlam taşımaz, kapıya takılır.

_SOYLEM = [
    Ozellik("s.dolgu", "soylem", "🔴 Söylem dolgusu (`yani`,`peki`)", "peki geçen ay",
            _re(r"\b(yani|peki|hani|şimdi|bak|işte|ee+|ya)\b")),
    Ozellik("s.oz_duzeltme", "soylem", "🔴 Öz-düzeltme — CANLI KUSUR", "ölç yani kıyasla",
            _re(r"\byani\s+\w+")),
    Ozellik("s.anafora", "soylem", "Atıf/anafora (`bunu`,`şunu`)", "bunu makinelere böl",
            _re(r"\b(bunu|şunu|onu|bunlar|az önceki|demin|yukarıdaki|o rapor)\b")),
    Ozellik("s.eksilti", "soylem", "Eksiltili cümle", "peki geçen ay",
            lambda q: len(q.split()) <= 3 and not q.strip().endswith("?")),
    Ozellik("s.nezaket", "soylem", "Nezaket/selamlama", "merhaba, teşekkürler",
            _re(r"\b(merhaba|selam|teşekkür|sağol|lütfen|günaydın|iyi günler|rica)\w*\b")),
    Ozellik("s.gerekce", "soylem", "Gerekçe/bağlam cümlesi", "toplantı var da, ciro?",
            _re(r"\b(çünkü|için|olduğundan|nedeniyle|dolayı|var da|lazım)\b")),
    Ozellik("s.coklu_soru", "soylem", "Tek mesajda iki soru", "ciro ne kadar, fire nasıl",
            lambda q: q.count("?") >= 2 or (", " in q and len(q.split()) > 7)),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 5 · SORGU SEMANTİĞİ — ⚠ AÇIK KÜME
# ═══════════════════════════════════════════════════════════════════════════════

_SEMANTIK = [
    Ozellik("q.tek_olcu", "semantik", "Tek ölçü", "bu ay ciro",
            lambda q: True),                       # taban — her soruda var sayılır
    Ozellik("q.iki_olcu", "semantik", "🔴 İki ölçü birlikte", "ciro ve fire",
            _re(r"\b(ve|ile|bir de|yanına|birlikte|hem)\b.*\b(ekle|göster|birlikte)\b|"
                r"\b\w+\s+ve\s+\w+\b")),
    Ozellik("q.iliski", "semantik", "🔴 Ölçü İLİŞKİSİ — CANLI KUSUR", "ciro üzerindeki etkisi",
            _re(r"\b(üzerindeki etki|etkisi|etkiliyor|korelasyon|ilişki|bağlantı|"
                r"artınca|arasında ilişki)\b")),
    Ozellik("q.kirilim", "semantik", "Kırılım", "makine bazında",
            _re(r"\b(bazında|bazlı|göre|kırılımında|ayrımında|dağılımı)\b")),
    Ozellik("q.cok_kirilim", "semantik", "İki kırılım", "makine ve vardiya bazında",
            _re(r"\b\w+\s+(ve|ile)\s+\w+\s+(bazında|bazlı|kırılımında)\b")),
    Ozellik("q.ustunluk", "semantik", "Üstünlük (en çok/en az)", "en çok satan",
            _re(r"\b(en çok|en az|en yüksek|en düşük|zirve|dip|ilk \d|son \d|top \d)\b")),
    Ozellik("q.kiyas_donem", "semantik", "Dönem kıyası", "geçen aya göre",
            _re(r"\b(göre|kıyasla|karşılaştır|farkı|değişim|yoy|geçen \w+e göre)\b")),
    Ozellik("q.trend", "semantik", "Trend/seyir", "nasıl gidiyor",
            _re(r"\b(trend|seyir|nasıl gidiyor|artıyor mu|gidişat|eğilim)\b")),
    Ozellik("q.neden", "semantik", "Nedensellik", "neden arttı",
            _re(r"\b(neden|niçin|niye|sebep|sebebi|yüzünden|kaynaklanıyor)\b")),
    Ozellik("q.katki", "semantik", "Katkı ayrıştırma", "kimin payı var",
            _re(r"\b(payı|katkı|hangi \w+ etkili|aşağı çekiyor|yukarı çekiyor|kim etkiledi)\b")),
    Ozellik("q.esik", "semantik", "Eşik/hedef kıyası", "hedefin neresinde",
            _re(r"\b(hedef|bütçe|plan|gerçekleşme|iyi mi|kötü mü|normal mi|yeterli mi|"
                r"neresinde|uyuyor mu)\b")),
    Ozellik("q.filtre_deger", "semantik", "Değer filtresi", "siyah renkli partiler",
            _re(r"\b(sadece|yalnız|olan|olanlar|'?(de|da|te|ta)ki)\b")),
    Ozellik("q.filtre_olumsuz", "semantik", "🔴 Olumsuz filtre", "X hariç",
            _re(r"\b(hariç|dışında|olmayan|haricinde|çıkar)\b")),
    Ozellik("q.aralik", "semantik", "Sayısal aralık", "100 ile 200 arasında",
            _re(r"\b\d+\s*(ile|-|,)\s*\d+\s*(arasında|aralığında)\b|\b(üstü|altı|üzeri|"
                r"fazla|az)\b\s*\d+")),
    Ozellik("q.oran", "semantik", "Oran/yüzde", "yüzde kaçı",
            _re(r"\b(oran|oranı|yüzde|%|pay|payı|/|başına|birim)\b")),
    Ozellik("q.toplama_turu", "semantik", "Toplama türü (ort/toplam/sayı)", "ortalama",
            _re(r"\b(ortalama|toplam|adet|sayı|sayısı|kaç tane|kaç adet|medyan|en fazla)\b")),
    Ozellik("q.karar", "semantik", "Karar/öneri isteği", "ne yapmalıyız",
            _re(r"\b(ne yapmalı|öner|tavsiye|nasıl iyileş|aksiyon|ne önerirsin)\w*\b")),
    Ozellik("q.tahmin", "semantik", "Tahmin/projeksiyon", "yılı nerede kapatırız",
            _re(r"\b(tahmin|projeksiyon|öngör|bu gidişle|kapatır|ne olur|forecast)\w*\b")),
    Ozellik("q.yetenek", "semantik", "Yetenek sorusu", "neler yapabilirsin",
            _re(r"\b(neler yapabilir|ne sorabilir|hangi ölçü|hangi kırılım|nasıl kullan)\w*\b")),
    Ozellik("q.kapsam_disi", "semantik", "Kapsam dışı / gürültü", "fıkra anlat",
            _re(r"\b(fıkra|hava|film|yaşındasın|şaka|drop table|select \*|asdf|qwerty)\b")),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 6 · DÖNEM BİÇİMİ
# ═══════════════════════════════════════════════════════════════════════════════

_DONEM = [
    Ozellik("d.goreli", "donem", "Göreli dönem", "bu ay · geçen yıl",
            _re(r"\b(bu|geçen|önceki|gelecek|önümüzdeki)\s+(gün|hafta|ay|yıl|çeyrek|sene)\b|"
                r"\b(dün|bugün|yarın)\b")),
    Ozellik("d.son_n", "donem", "Son N birim", "son 12 ay",
            _re(r"\bson\s+\d+\s*(gün|hafta|ay|yıl|çeyrek)\b")),
    Ozellik("d.ay_yalin", "donem", "Ay adı yalın", "ocak",
            _re(r"\b(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\b")),
    Ozellik("d.ay_cekimli", "donem", "🔴 Ay adı ÇEKİMLİ — CANLI KUSUR", "şubata · ocakla · martta",
            _re(r"\b(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)"
                r"(a|e|ta|te|tan|ten|da|de|dan|den|la|le|ın|in|un|ün|ı|i)\b")),
    Ozellik("d.yil", "donem", "Yıl", "2025'te",
            _re(r"\b(19|20)\d{2}\b")),
    Ozellik("d.ceyrek", "donem", "Çeyrek/yarıyıl", "2. çeyrek",
            _re(r"\b(\d\.?\s*çeyrek|q[1-4]|yarıyıl|ilk yarı|ikinci yarı)\b")),
    Ozellik("d.ytd", "donem", "YTD / kümülatif", "yılbaşından bugüne",
            _re(r"\b(yılbaşından|başından beri|bugüne kadar|ytd|kümülatif|yıl başından)\b")),
    Ozellik("d.aralik", "donem", "🔴 Dönem aralığı", "ocaktan marta",
            _re(r"\b\w+(tan|ten|dan|den)\s+\w+(a|e|ya|ye)\b|\b\w+\s*-\s*\w+\s+arası\b")),
    Ozellik("d.yok", "donem", "Dönemsiz soru", "ciro ne kadar",
            lambda q: not re.search(
                r"\b(bu|geçen|son|dün|bugün|ocak|şubat|mart|nisan|mayıs|haziran|temmuz|"
                r"ağustos|eylül|ekim|kasım|aralık|çeyrek|yılbaşı|(19|20)\d{2})", q, re.I)),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 7 · YAZIM ve BİÇİM
# ═══════════════════════════════════════════════════════════════════════════════
#
# ⚠ Aksansız yazım (`gecen`) BİLEREK ayrı bir özellik: ürün `_norm()` ile onu zaten
# katlıyor, yani **kapalı bir kapı**. Ölçülür ama kusur beklenmez — *kapalı bir kapıyı
# ölçmemek, onun kapalı kaldığını varsaymaktır.*

_YAZIM = [
    Ozellik("y.dogru", "yazim", "Doğru yazım", "müşteri bazında ciro",
            _re(rf"^[{TR}\s\d\.,%'’\-\?]+$")),
    Ozellik("y.aksansiz", "yazim", "Aksansız yazım (⚠ `_norm` kapatıyor)", "gecen hafta",
            lambda q: bool(re.search(r"\b(gecen|musteri|uretim|sikayet|firmasi|ariza|"
                                     r"olcu|dusuk|yuksek|toplam sayisi)\b", q, re.I))),
    Ozellik("y.devrik", "yazim", "🔴 Harf devrikliği", "musetri",
            lambda q: _tipik_typo(q)),
    Ozellik("y.kisaltma", "yazim", "Kısaltma", "ne kdr · bznd",
            _re(r"\b(kdr|kc|bznd|mşt|ort|tpl|gçn|mkn|vrd|ürtm|dgl|icn|vs|falan)\b")),
    Ozellik("y.bosluk", "yazim", "🔴 Boşluk hatası", "bu ay ki · nekadar",
            _re(r"\b(nekadar|nasil bir|bu ay ki|kac tane|her hangi|bir kaç|hiç bir)\b")),
    Ozellik("y.buyuk", "yazim", "Büyük harf", "CİRO NE KADAR",
            lambda q: sum(c.isupper() for c in q) >= max(3, len(q) * 0.30)),
    Ozellik("y.noktalama", "yazim", "Noktalama/emoji", "ciro?? · ciro!!!",
            _re(r"[?!]{2,}|[…]|[\U0001F300-\U0001FAFF]")),
    Ozellik("y.sayi_bicimi", "yazim", "Sayı biçimi", "1.000,50 · 1,5 milyon",
            _re(r"\b\d{1,3}([.\s]\d{3})+(,\d+)?\b|\b\d+[,.]\d+\s*(bin|milyon|milyar|k|m)\b")),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AİLE 8 · KOD-DEĞİŞTİRME ve JARGON
# ═══════════════════════════════════════════════════════════════════════════════
#
# Katalog **kendisi** İngilizce sinonim taşıyor (`revenue`, `downtime`, `oee`) —
# yani bu bir varsayım değil, kataloğun beyanı. Ve gerçek fabrikada da böyle konuşulur.

_JARGON = [
    Ozellik("j.ingilizce", "jargon", "İngilizce terim", "revenue · downtime",
            _re(r"\b(revenue|downtime|waste|efficiency|energy|cost|margin|"
                r"quality|delivery|forecast|budget|target|scrap|yield|debt|vat)\b")),
    Ozellik("j.kisaltma_teknik", "jargon", "Teknik kısaltma", "OEE · KPI · OTIF",
            _re(r"\b(oee|kpi|otif|mttr|mtbf|capa|iso|sla|roi|ebitda|kdv|sgk|tep)\b")),
    Ozellik("j.saha_argosu", "jargon", "🔴 Saha argosu", "tezgah · zayiat · randıman",
            _re(r"\b(tezgah|zayiat|randıman|eleman|makine yattı|vaziyet|ne alemde|"
                r"iş emri|makine bozuldu|hurda|ıskarta)\b")),
    Ozellik("j.kod_degistirme", "jargon", "Karışık dil", "total ciro",
            _re(r"\b(total|net|gross|per|by|last|monthly)\s+[çğıöşüa-z]+\b")),
]


def _tipik_typo(q: str) -> bool:
    """Harf devrikliği/düşmesi sezgisi — **sözlüksüz**.

    ⚠ Sözlük kullanmıyoruz bilerek: bir sözlük yalnız kendi kelimelerini tanır ve
    yeni bir katalog terimi eklendiğinde sessizce körleşir. Bunun yerine **yapısal**
    işaret: Türkçede olağandışı ünsüz kümeleri ya da aynı harfin üçlenmesi.
    """
    dusuk = re.search(r"[bcçdfgğhjklmnprsştvyz]{4,}", q, re.I)
    ucleme = re.search(r"(.)\1\1", q)
    return bool(dusuk or ucleme)


# ═══════════════════════════════════════════════════════════════════════════════

OZELLIKLER: tuple[Ozellik, ...] = tuple(
    _AD_CEKIMI + _IYELIK + _FIIL + _SOYLEM + _SEMANTIK + _DONEM + _YAZIM + _JARGON
)

#: 🔴 KAPALI aileler **tamamlanmıştır** — Türkçenin durum/iyelik/kip ekleri sonludur,
#: yani bu ailelerde *"acaba unuttuğum var mı"* sorusu KAPANMIŞTIR.
#: ⚠ AÇIK aileler kapanmaz ve bu dosya bunu **saklamaz**: söylem ve semantik dilin
#: değil kullanımın alanıdır; oraya her zaman yeni bir biçim eklenebilir.
#: *Bir taksonominin dürüstlüğü, neyi kapsamadığını söylemesindedir.*
KAPALI_AILELER = frozenset({"ad_cekimi", "iyelik", "fiil", "donem"})
ACIK_AILELER = frozenset({"soylem", "semantik", "yazim", "jargon"})


def kapsam_olc(sorular: list[str], *, zayif_esik: int = 5) -> dict:
    """Bir soru kümesinin dilsel kapsamını ölçer.

    Dönen sözlükteki **`bos`** listesi, test ortamının deliğidir: o özelliği taşıyan
    **hiçbir** vaka üretilmiyor demektir — yani o sınıftaki bir kusur, korpus ne kadar
    büyürse büyüsün **görünmez** kalır.
    """
    sayac: Counter = Counter()
    for q in sorular:
        for o in OZELLIKLER:
            try:
                if o.dedektor(q):
                    sayac[o.kod] += 1
            except Exception:                            # noqa: BLE001
                pass                                     # dedektör kusuru ölçümü durdurmaz
    bos = [o for o in OZELLIKLER if sayac[o.kod] == 0]
    zayif = [o for o in OZELLIKLER if 0 < sayac[o.kod] < zayif_esik]
    return {
        "toplam_soru": len(sorular),
        "ozellik_sayisi": len(OZELLIKLER),
        "kapsanan": len(OZELLIKLER) - len(bos),
        "kapsam_yuzde": round(100 * (len(OZELLIKLER) - len(bos)) / len(OZELLIKLER), 1),
        "sayac": dict(sayac),
        "bos": [{"kod": o.kod, "aile": o.aile, "aciklama": o.aciklama, "ornek": o.ornek}
                for o in bos],
        "zayif": [{"kod": o.kod, "aile": o.aile, "adet": sayac[o.kod], "ornek": o.ornek}
                  for o in zayif],
        "aile_kapsami": {
            aile: {
                "toplam": sum(1 for o in OZELLIKLER if o.aile == aile),
                "kapsanan": sum(1 for o in OZELLIKLER if o.aile == aile and sayac[o.kod]),
                "kapali_kume": aile in KAPALI_AILELER,
            }
            for aile in sorted({o.aile for o in OZELLIKLER})
        },
    }


def rapor(k: dict) -> str:
    """Kapsam raporu — **kapsanmayanı öne alır**, kapsananı değil.

    *Bir kapsam raporunun değeri yeşil satırlarında değil, kırmızı satırlarındadır;
    yeşil satırlar zaten bilinen şeyi tekrarlar.*
    """
    s = ["# DİLSEL KAPSAM — test ortamı neyi GÖREBİLİR", ""]
    s.append(f"Soru: **{k['toplam_soru']}** · özellik: **{k['ozellik_sayisi']}** · "
             f"kapsanan: **{k['kapsanan']}** (%{k['kapsam_yuzde']})")
    s += ["", "| aile | kapsanan/toplam | küme |", "|---|---|---|"]
    for aile, v in k["aile_kapsami"].items():
        isaret = "🔒 kapalı" if v["kapali_kume"] else "⚠ açık"
        tam = "" if v["kapsanan"] == v["toplam"] else " 🔴"
        s.append(f"| {aile} | {v['kapsanan']}/{v['toplam']}{tam} | {isaret} |")
    if k["bos"]:
        s += ["", "## 🔴 HİÇ ÜRETİLMEYEN — test ortamının deliği", "",
              "*Bu sınıftaki bir kusur, korpus ne kadar büyürse büyüsün görünmez kalır.*", ""]
        for o in k["bos"]:
            s.append(f"- **`{o['kod']}`** ({o['aile']}) — {o['aciklama']} · örnek: `{o['ornek']}`")
    else:
        s += ["", "✅ **Hiç boş özellik yok** — tanımlı her dilsel sınıf en az bir vakada üretiliyor."]
    if k["zayif"]:
        s += ["", "## ⚠ ZAYIF KAPSAM (<5 vaka)", ""]
        for o in k["zayif"]:
            s.append(f"- `{o['kod']}` ({o['aile']}) — **{o['adet']}** vaka · örnek: `{o['ornek']}`")
    return "\n".join(s)
