# ADR-0026 — Kapsam merceği — **görünürlük**, güvenlik sınırı DEĞİL

**Durum:** kabul edildi · **Faz:** FAZ 2.3 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 2.3` ile inerken, aynı
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

200 tablo gören bir kullanıcı, hangisinden başlayacağını bilmiyor. Ama kataloğu daraltmak bir **yetki** kararı gibi görünürse, bir gün güvenlik onun üstüne kurulur ve o gün mercek bir **delik** olur.

## Karar

Mercek `/schema` (katalog) üstünde çalışır, `/ask` (cevaplama) üstünde **değil**. 🔴 **Bir GÖRÜNÜRLÜK aracıdır, GÜVENLİK SINIRI DEĞİL** — kapatmak yetki **açmaz**.

## Sonuçlar

- 🔴 Yol haritası `AskRequest.scope` diyordu; ölçülüp **vazgeçildi**: merceği cevaplama yoluna bağlamak, **aynı sorunun kapsam değişince farklı sayı döndürmesi** demekti — bir görünürlük tercihini **sonuca** karıştırmak.
- `portfoy` kapsamı `is_superadmin` ile açılır; uydurma bir izin (`tenant:read_all`) yazmak, matriste **olmayan** bir yetkiye dayanmak olurdu.

## Kanıt — **tek doğrulama yolu**

- `app/kapsam.py`
- `tests/test_kapsam_mercegi.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
