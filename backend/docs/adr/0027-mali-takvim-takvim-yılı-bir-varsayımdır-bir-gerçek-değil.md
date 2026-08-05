# ADR-0027 — **Mali takvim** — takvim yılı bir varsayımdır, bir gerçek değil

**Durum:** kabul edildi · **Faz:** FAZ 2.6 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 2.6` ile inerken, aynı
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

*“Bu yıl”* sorusunun cevabı, mali yılı Nisan'da başlayan bir şirkette **üç ay kayıktır**. Doğru sayı, yanlış soruya cevap olur ve kullanıcı bunu fark etmez.

## Karar

Mali yıl başlangıç ayı tenant yapılandırmasında; dönem çözümü `ContextVar` üzerinden derinlere iner (imzalar değişmez). 🔴 **Takvim yılından farklı bir pencere kullanıcıya SÖYLENİR** (`AskResponse.mali_donem`); aynıysa alan `None` kalır — gürültü üretmez, yalnız **fark varken** konuşur.

## Sonuçlar

- ⚠ `ContextVar` deseni bu depoda **üç kez** kanıtlandı (`llm._llm_usage_var`, `cube_router._reddi_var`, `mali_takvim._ay_var`): derin fonksiyon okur, sığ fonksiyon yazar, **imzalar değişmez**.

## Kanıt — **tek doğrulama yolu**

- `app/mali_takvim.py`
- `tests/test_mali_takvim.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
