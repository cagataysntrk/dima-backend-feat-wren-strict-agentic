"""🔴 **İŞLEV SÖZCÜKLERİ — ve bu dosyanın var olma sebebi bir BORÇTUR.**

Bu modül bir çözüm değil, **görünür bırakılmış bir borçtur** (`§56`): burada bir kelime
listesi duruyor ve `§0.0`'ın en üst kuralı *"route'a dil öğretme"* diyor. Liste
`ask.py`'den buraya taşındı ki **büyüdüğü görülsün** — bir dosyanın adı, içindeki şeyin
ne olduğunu söyler.

## Neden şimdilik var

Çapraz-konu reddi (*"«X» başka bir konu gibi görünüyor"*) `X`'i **kapsam kapısının
bilinmeyen listesinden** alıyor. O liste Türkçe bir sözlüğe dayanıyor; soru İngilizce ya
da Arapça olduğunda **her sözcük** bilinmeyen görünüyor ve sistem cevaplanabilir bir
soruyu *"başka bir konu"* diye reddediyor. Ölçüldü (E turu, dört kanıt).

## 🔴 KAPANIŞ KOŞULU — `§56`

> **Garson bir aday ürettiyse Türkçe kapsam reddi hiç koşmamalıdır.**

O yapıldığında bu dosya **silinir**. Yeni dil eklendikçe liste uzatılırsa, kural
çiğnenmiş demektir.

*Bir listeyi uzatmak, listenin yanlış araç olduğunu gizler.*
"""

from __future__ import annotations

#: 🔴 **`§54` — İŞLEV SÖZCÜKLERİ BİR KONU DEĞİLDİR ve süzgeç YALNIZ GÖSTERİMDEYDİ.**
#:
#: Ölçüldü (E turu, **dört** kanıt): `aylık üretim ve enerji tüketimini **birlikte**
#: göster` → *«"birlikte" başka bir konu gibi görünüyor»*; `bakım maliyeti ile arıza
#: sayısı **ilişkili** mi` → *«"bakim maliyeti iliskili" başka bir konu»*; `which machines
#: had the highest downtime last month` → *«"which had the highest last month" başka bir
#: konu»*.
#:
#: ⊙ Süzgeç vardı ama **yalnız cümleyi güzelleştiriyordu**; dalın **ateşlenmesini**
#: engellemiyordu. Yani sistem anlamadığını gizliyor, ama yine de reddediyordu.
#:
#: 🔴 **İngilizce işlev sözcükleri de eklendi** ve bu `ADR-0008`'e uygundur: `which`·`the`·
#: `had`·`by`·`as` bir **kapalı dilbilgisi sınıfıdır** (artikel · yardımcı fiil · soru
#: sözcüğü · edat), bir alan sözlüğü değil. Ve `§0.0` gereği: kullanıcı İngilizce
#: yazdığında sistem *"bu başka bir konu"* diyemez — o cümlenin konusu **vardır**,
#: yalnız dili farklıdır.
#:
#: *Bir cümlenin dilbilgisi, o cümlenin konusu değildir.*
_ISLEV_SOZCUKLERI = frozenset({
    "hangi", "hangisi", "hangileri", "kim", "kimin", "kime",
    "etti", "ettik", "ettiler", "etmis", "ediyor", "eden", "edildi",
    # bağlaç · zarf — bir konu adı değil, iki şeyi birbirine bağlayan sözcük
    "birlikte", "beraber", "ayrica", "ayni", "anda", "iliskili", "iliski", "arasindaki",
    "arasinda", "kiyasla", "karsilastir", "gore",
    # 🔴 İngilizce kapalı sınıf: artikel · yardımcı · soru · edat · bağlaç
    "which", "what", "who", "the", "a", "an", "is", "are", "was", "were", "had", "has",
    "have", "do", "does", "did", "show", "me", "my", "our", "by", "as", "with", "and",
    "or", "of", "for", "to", "in", "on", "at", "this", "that", "them", "their", "it",
    "highest", "lowest", "top", "best", "worst", "most", "least", "compare", "between",
    # zaman — İngilizcenin kapalı dönem sözcükleri (Türkçedeki `_ZAMAN_BIRIMI`'nin ikizi)
    "last", "next", "previous", "current", "this", "past", "month", "months", "year",
    "years", "week", "weeks", "day", "days", "quarter", "quarters", "today", "yesterday",
    "since", "until", "ago", "now",
})
#: ⚠ **VE BU LİSTE UZAMAMALI — kalıcı çözüm bu değil.** Her yeni dilde yeni bir kapalı
#: sınıf yazmak, `§0.0`'ın yasakladığı *"route'a dil öğretme"*nin bir başka biçimidir.
#: Yapısal çözüm: **garson bir aday üretmişse Türkçe kapsam reddi hiç koşmamalıdır** —
#: çünkü o reddin dayanağı Türkçe bir sözlüktür ve soru Türkçe değildir.
#: `§56` olarak kayıtlı, sıradaki iş.
#:
#: *Bir listeyi uzatmak, listenin yanlış araç olduğunu gizler.*


def _islev_sozcugu(w: str) -> bool:
    return str(w).lower() in _ISLEV_SOZCUKLERI
