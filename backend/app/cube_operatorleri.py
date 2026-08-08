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


def gecerli(op) -> bool:
    """Operatör motorun tanıdığı bir ad mı?

    ⚠ **Fail-closed ve GÜRÜLTÜLÜ:** çağıran (`parse_cube_query`) tanımadığı bir operatör
    görürse sorguyu **reddeder**, filtreyi sessizce **düşürmez**. Sessiz düşürme bu
    depoda `compare`'ın ve `measure_having`'in başına geldi ve ikisi de aynı dersi
    yazdı: *"düşürülen şey geçersiz bir değer değil, var olan bir yetenekti."*
    Bir red logda görünür (`intent: whitelist REDDİ`), sessiz bir düşüş görünmez.
    """
    return isinstance(op, str) and op in MOTOR_OPERATORLERI
