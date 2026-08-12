"""🔴🔴 **`M-6` · OPERATÖR SÖZLÜĞÜ — TEK KAYNAK.** [bayrak yok: bir ad listesi, bir davranış değil]

## Ölçülen kusur — üç katman, üç farklı liste

`MUTFAK-DENETIMI` raporu bu kusuru **kod okumasıyla** işaretlemişti (🔍, *"canlıda
tetiklenmedi"*). Bu tur **ölçüldü** — çalışan konteynerin `/cube` ucuna her operatör
**tek tek** gönderilerek:

    eq neq in not_in gt gte lt lte contains starts_with is_null is_not_null  → 12'si de OK
    ne                                                                       → 🔴 satır=0

| katman | operatörler | |
|---|---|---|
| **motor** *(ölçüldü — canlı `/cube`)* | yukarıdaki **12** | ✅ |
| `route()`'un ürettiği | `eq` `neq` `in` `not_in` (+ tarih `gte`/`lte`) | ⊂ 12 |
| **Intent-JSON şeması** *(elle yazılmış)* | `eq` **`ne`** `gt` `gte` `lt` `lte` `in` — **7** | 🔴 |
| `parse_cube_query` denetimi | yalnız `dimension` beyaz listesi — **operatör HİÇ denetlenmiyor** | 🔴 |

## 🔴 `ne` — ve BU LİSTENİN KAYNAĞI MOTORUN KENDİ AĞZI

Motor `ne`'yi **gürültülü** reddediyor ve reddederken **geçerli kümeyi kendisi
sayıyor** (canlı `/cube`, HTTP **400**, iki koşum birebir — `KURAL G-1`):

    ValueError: Invalid CubeQuery JSON: unknown variant `ne`, expected one of
    `eq`, `neq`, `in`, `not_in`, `gt`, `gte`, `lt`, `lte`,
    `contains`, `starts_with`, `is_null`, `is_not_null`

⊙ Yani aşağıdaki demet bir **tahmin ya da kod okuması değil**; motorun kendi hata
mesajından **birebir** alınmıştır ve ayrıca on üç operatörün her biri tek tek
gönderilerek doğrulanmıştır.

⚠ **Ve ilk yazımım burada yanıldı — beşinci ölçüm-aleti hatası.** *"Sessizce boş
dönüyor"* diye yazmıştım; sondaj yazıcım **HTTP durum kodunu okumuyordu** ve 400'ü 0
satır sanmıştım. Motor sessiz değil, **aletim sağırdı**. Kusur `ne`'nin sessizliği
değil, şemanın motorda **olmayan** bir adı modele yazdırması ve motorun ölçülmüş 12
adından **beşinin** fişte hiç bulunmamasıdır.

*Bir aracın okumadığı alan, olmayan bir davranış uydurur.*

⚠ Bugün canlıda tetiklenmiyor çünkü şema-kısıtlı kip mevcut sağlayıcıda **NO-OP**
(`oneOf` desteklenmiyor). **Sağlayıcı değiştiği gün bu kusur üretime çıkar.** Ucuz bir
sigortayı, ateş çıkmadan önce yaptırmak gerekir.

## Neden ayrı bir modül — ve neden bir kelime listesi DEĞİL

Bu bir **dil** sözlüğü değil (`ADR-0008`'in konusu o); **kendi motorumuzun kabul ettiği
adların** listesi — tıpkı `viz.kind` değerleri ya da `EKSENLER` gibi **kapalı, sonlu ve
sahibi belli** bir küme. Bugün üç yerde ayrı ayrı yazılıydı ve üçü **ayrışmıştı**; asıl
kusur listenin varlığı değil, **üç kopyası** olmasıydı.

*Bir kümenin üç kopyası, üç farklı küme demektir.*
"""

from __future__ import annotations

#: 🔴 **MOTORUN KABUL ETTİĞİ OPERATÖRLER — ÖLÇÜLDÜ, VARSAYILMADI.**
#:
#: Her biri çalışan konteynerin `/cube` ucuna tek tek gönderildi ve **satır döndürdü**
#: (2026-08-08, `demo-boyahane`, `parti.renk`). Bir operatör buraya **ölçülmeden**
#: eklenemez: eklenirse garson onu yazar ve kullanıcı sessiz bir boşluk alır — `ne`'nin
#: başına gelen tam olarak budur.
MOTOR_OPERATORLERI: tuple[str, ...] = (
    "eq", "neq", "in", "not_in",
    "gt", "gte", "lt", "lte",
    "contains", "starts_with",
    "is_null", "is_not_null",
)

#: Değer **almayan** operatörler — şema `value`'yu zorunlu tutmamalı, `parse` boş değeri
#: eksik sanmamalı. (Ölçüldü: ikisi de `value:null` ile satır döndürdü.)
DEGERSIZ: frozenset[str] = frozenset({"is_null", "is_not_null"})


#: 🔴 `M-9` — PENCERE KİPLERİ. Her biri bir `OVER (…)` sarmasıdır; gövde
#: `wren_service._pencere_sar`'da, **kümenin sahibi burası**.
#:
#: ⚠ Neden burada: `cube_router` (sipariş fişini doğrular) ile `wren_service` (SQL'i
#: sarar) **aynı** kümeyi bilmek zorunda, ama `cube_router` bir motor modülünü **import
#: edemez** (`test_alan_haritasi`: 🗣 modüller motora dokunamaz). Küme üçüncü bir yerde
#: yaşamazsa iki kopya doğardı — `M-6`'nın tam olarak ölçtüğü kusur.
PENCERE_KIPLERI: tuple[str, ...] = (
    "kumulatif", "hareketli_ort", "sira", "onceki", "degisim_yuzde",
    # 🔴 `pay` — *"toplam içindeki payı"*. Ölçülen kusur: bu alet **yoktu** ve garson
    # eksiği `turev` ile kapatmaya çalıştı: `pay=payda=toplam_fire_kg` → her satır
    # **%100** (canlı, `p16`). Pay bir **iki-ölçü oranı değil**, bir pencere işlemidir:
    # `x / SUM(x) OVER (…)`. *Bir aleti vermezsen, eldeki alet yanlış kullanılır.*
    "pay",
)

#: 🔴 `M-3` — TÜREV KİPLERİ (ölçü cebri: bölme/çıkarma). Gövde `_turev_sar`'da.
TUREV_KIPLERI: tuple[str, ...] = ("yuzde", "oran", "fark")


def gecerli(op) -> bool:
    """Operatör motorun tanıdığı bir ad mı?

    ⚠ **Fail-closed ve GÜRÜLTÜLÜ:** çağıran (`parse_cube_query`) tanımadığı bir operatör
    görürse sorguyu **reddeder**, filtreyi sessizce **düşürmez**. Sessiz düşürme bu
    depoda `compare`'ın ve `measure_having`'in başına geldi ve ikisi de aynı dersi
    yazdı: *"düşürülen şey geçersiz bir değer değil, var olan bir yetenekti."*
    Bir red logda görünür (`intent: whitelist REDDİ`), sessiz bir düşüş görünmez.
    """
    return isinstance(op, str) and op in MOTOR_OPERATORLERI

# ══ `§B12` · ZAMAN GRANÜLERLİĞİ — İKİNCİ KAPALI KÜME, AYNI SAHİP ═══════════════
#
# ## Ölçülen kusur (2026-08-12) — ajan İKİ dedi, ölçüm DÖRT buldu
#
# Aynı kapalı küme **dört yerde** elle yazılıydı:
#
#     app/intent_semasi.py:24   _GRAN_ENUM      ["year","quarter","month","week","day"]
#     app/plan_onarim.py:59     GRANULERLIKLER  ("day","week","month","quarter","year")
#     app/cube_router.py:4574   _GRAN_LADDER    ["year","quarter","month","week","day"]
#     app/llm.py:364            istem metni     "year|quarter|month|week|day"
#
# ⊙ Ve ikisinin **sırası bile farklıydı** — biri üyelik için (sıra önemsiz), öteki bir
# **merdiven** için (`.index(cur)+1` → daha ince granülerlik). Yani dört kopya, iki
# farklı sözleşme varsayımı. *Aynı kuralın dört sahibi, dört farklı gün ayrışır.*
#
# ⚠ Bu modül `operatorleri` adını taşıyor ama işi **küp sözleşmesinin kapalı
# kümelerinin tek sahibi** olmak; operatörler o kümelerin **ilkiydi**. Yeni bir modül
# açmak sahipliği daha da bölerdi — `KAT-1` tam bunun tersini ister.
#
# ## 🔴 SIRA BİR SÖZLEŞMEDİR: kabadan inceye
#
# `cube_router._GRAN_LADDER` sıralamaya **dayanıyor**; bu yüzden sahip sıralı bir
# tuple'dır ve sırası **kabadan inceye**dir. Üyelik için kullananlar (`plan_onarim`)
# sıradan etkilenmez.
#
# ⚠ `KURAL B`: dördünün de ürettiği değer **bayt bayt aynı** kalır —
# `test_b12_granulerlik_tek_sahip.py` bunu ölçer.
#
# ⊙ `hour`/`minute` **YOK ve bu bir karardır** — ama gerekçesi ⟳ **2026-08-12'de
# DÜZELTİLDİ** (`§40.7 B12`). Eski gerekçe *«motorun `timeDimensions.granularity`
# sözleşmesi bu beşini tanıyor»* idi ve **ölçülmeden** yazılmıştı; ölçüm onu çürüttü.
#
# 🔴 Gerçek sebep **motor değil VERİ** (ders ㊹): motor `hour`'u kabul etse bile bu
# depodaki zaman eksenleri `hour` çözünürlüğü **taşımıyor**. Kabul eden bir motor,
# olmayan bir çözünürlüğü **adlandırır** — ve adlandırılmış boş bir kova bir hata
# değil bir **sessiz-yanlıştır**.
#
# ⊘ Açılış şartı bu yüzden **gözlenebilir**: bir küpün zaman ekseni **TIMESTAMP**
# olmalı **ve** `day` ile `hour` kovaları **farklı satır sayısı** vermeli.
GRANULERLIKLER: tuple[str, ...] = ("year", "quarter", "month", "week", "day")

#: İstem metni için hazır biçim — `llm.py` onu elle yazmasın.
GRANULERLIK_ISTEM = "|".join(GRANULERLIKLER)
