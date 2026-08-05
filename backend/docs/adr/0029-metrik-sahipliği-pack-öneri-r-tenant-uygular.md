# ADR-0029 — **Metrik sahipliği** — pack ÖNERİR, tenant UYGULAR

**Durum:** kabul edildi · **Faz:** FAZ 3.1b · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 3.1b` ile inerken, aynı
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

Aynı terim (`bakiye`) iki cube'un ölçüsü olduğunda sistem **sormadan** birini seçiyordu ve iki cevap **milyonlarca lira** ayrışıyordu. Ama sahipliği pack'e yazmak da yanlış çıktı: pack kararları **her tenant'a** uygulanınca korpus %93,2 → %92,6 **geriledi**.

## Karar

Pack bir **öneri** taşır; **karar tenant'ındır** (`MetricOwnership`). Bir hakem kaydı olmadan sistem seçim yapmaz — **sorar**.

## Sonuçlar

- 🔴 Ölçüm bir tasarımı çürüttü ve tasarım **değişti**: *pack karar verir* → *pack önerir*. Bu, ölçümün madde silmediği ama **şekil değiştirdiği** bir vaka.
- ⚠ `netlestirme_onceligi` bayrağı bu borcu **kapatmıyor** — o ayrı bir yolun önceliğidir; sahiplik kaydı ise **kararın kendisi**.

## Kanıt — **tek doğrulama yolu**

- `control_plane/models.py` `MetricOwnership`
- `tests/test_metrik_sahipligi.py`
- `demo/packs/cekirdek/sahiplik_kararlari.yml`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
