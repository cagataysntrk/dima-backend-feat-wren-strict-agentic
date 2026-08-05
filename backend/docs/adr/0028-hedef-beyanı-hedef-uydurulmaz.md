# ADR-0028 — **Hedef beyanı** — hedef UYDURULMAZ

**Durum:** kabul edildi · **Faz:** FAZ 2.5 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 2.5` ile inerken, aynı
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

Grafikteki referans çizgisi **hedef değil ORTALAMAYDI** ve kod bunu kendi yorumunda **itiraf ediyordu**. Bir ortalamayı hedef diye göstermek, ölçünün **iyi mi kötü mü** olduğunu uydurmaktır.

## Karar

Çizgi ancak cube'da `target:` **beyan edilmişse** hedeftir; beyan yoksa bugünkü anlamını (ortalama, `Ort.` etiketiyle) **korur**. 🔴 *“Hedef yok”* ile *“hedef 0”* asla karıştırılmaz.

## Sonuçlar

- Bayrak `hedef_kiyasi`; kapalıyken yanıt **bayt bayt** bugünküyle aynı.
- ⚠ Bu bayrak bir denetimde **kayıp** bulundu: yol haritası onu ilan ediyordu ama kod bayrağı **tanımıyordu** — bayraksız bir özellik **geri alınamaz**.

## Kanıt — **tek doğrulama yolu**

- `app/hedef.py`
- `tests/test_hedef_kiyasi.py`
- `app/viz.py` `reference_line`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
