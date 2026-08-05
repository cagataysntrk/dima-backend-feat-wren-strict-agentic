# ADR-0033 — **Tek ses** — kullanıcıya dönen metin tek katalogdan

**Durum:** kabul edildi · **Faz:** FAZ 5.17 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 5.17` ile inerken, aynı
> turda, kararı veren kodun yanında yazıldı (@`312b8d3`).
>
> ⚠ Fark önemlidir ve **karıştırılmamalıdır**: bir rekonstrüksiyonun başlıkları alıntı
> değildir ve *"kod bugün şöyle davranıyor"* diye okunur; bu dosya ise **kararın
> kendisidir**. Yine de çelişkide **kod kazanır** — çünkü karar yaşayan koddur, onun
> kaydı değil.
>
> 🔴 **Denetim bulgusu (2026-08-05):** *"en yüksek numaralı karardan sonra inen
> faz-düzeyi kararların hiçbirinin kaydı yok — kayıt kodun ~2 faz gerisinde."* Bu dosya
> o boşluğun bir satırını kapatır.


## Bağlam

Metinlerin hepsi satır içi f-string'di ve üç kusur **ölçüldü**: hitap aynı oturumda değişiyordu (*sen* ↔ *siz*), aynı cümle iki yerde **birebir** tekrar ediyordu, ve kullanıcıya **jargon** sızıyordu.

## Karar

`app/soz.py` — kararlı ID'li **veri modülü** (`metin` + `kind` + `hitap`). 🔴 **Metin şekli kuralı: ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR.** *“Neyi karşılaştırmak istediğini anlayamadım”* bir **form doğrulayıcısıdır**, bir soru değil.

⚠ `note` **yeniden kullanılmaz**: dört anlam taşıyor ve kalıcı `payload_json` geçmişi ona bağlı. Yeni alan `soz`; okuma `soz ?? note`.

## Sonuçlar

- Bu bir **veri modülüdür**, bir soyutlama katmanı değil — kapı sınıf hiyerarşisi ve şablon motorunu **AST ile** yasaklıyor. *Bir metin katalogunun ikinci bir işi olduğu anda kimse ona metin yazmaz.*

## Kanıt — **tek doğrulama yolu**

- `app/soz.py`
- `tests/test_soz_katalogu.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
