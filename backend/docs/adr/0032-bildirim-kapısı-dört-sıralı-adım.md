# ADR-0032 — **Bildirim kapısı** — dört sıralı adım

**Durum:** kabul edildi · **Faz:** FAZ 5.9 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 5.9` ile inerken, aynı
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

`brief|digest` grep'i **sıfırdı**: her schedule ayrı bildirim atıyordu. *Bir uyarı sistemi, susturulduğu anda ölür* — ve susturulmasının en hızlı yolu **tekrarıdır**, yanlışlığı değil.

## Karar

`dedup_key = H(kaynak_tip, kaynak_id, yon)` → `suppression_window` → **önem sıralaması** → `correlation_group`. **Sıra bağlayıcıdır**: ters sırada bir birleştirme, bastırılacak bir sinyali gruba sokup **grubun tamamını** kurtarırdı.

## Sonuçlar

- 🔴 `yon` anahtarın **parçası**: *“fire yükseldi”* ile *“fire normale döndü”* aynı kaynaktan gelir ama **farklı haberlerdir**.
- 🔴 `critical` **bastırılmaz**: tekrar rahatsız edicidir, **kaçırılan** bir kritik sinyal geri alınamaz.
- 🔴 Bastırılan bildirim **silinmez, gizlenir** — *“neden bana haber verilmedi”* sorusu bir olaydan **sonra** sorulur.

## Kanıt — **tek doğrulama yolu**

- `app/bildirim_kapisi.py`
- `tests/test_bildirim_kapisi.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
