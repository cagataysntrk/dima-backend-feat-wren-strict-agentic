# ADR-0030 — **Apache Ossie** ithal/ihraç — çevirici yazılır, motor yazılmaz

**Durum:** kabul edildi · **Faz:** FAZ 3.4 · 4.4 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 3.4 · 4.4` ile inerken, aynı
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

Sektörün fiili standardı ASF'e bağışlandı ve YAML üst-yapıları **bizimkiyle neredeyse birebir**. MIMARI §3.4 *“bilerek alınmayanlar”* listesinde `osi` vardı; standardın ASF'e geçişi o kararı **geçersiz kıldı**.

## Karar

Bir **eşleme** yazılır (`datasets→models` · `metrics→measures` · `ai_context→synonyms`), ikinci bir semantik motor **değil**. Farkımız `x-dima` **Custom Extensions** içinde gider: fan-out sertifikası · `always_filter` · `additive` · `dimension_origin`.

🔴 **İthal edilen her ilişki `certified: "olculmedi"` damgasıyla gelir.**

## Sonuçlar

- 🔴 **Round-trip kapısı bayraktan BAĞIMSIZ**: ihraç → geri ithal **birebir aynı SQL** vermiyorsa bayrak açılmaz. Kapı ilk koşumda kırmızı verdi — `time_dimensions` ayrı bir üst-düzey anahtardı ve ihraç onu hiç görmüyordu.
- ⚠ Standarda uyarken **farkı kaybetmek** ihracın bedeli olamaz: dört alanın da Ossie'de karşılığı yok ve dördü de **sessiz-yanlışı** önlüyor.

## Kanıt — **tek doğrulama yolu**

- `app/ossie.py`
- `tests/test_ossie_ithal.py`
- `tests/test_ossie_ihrac.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
