# ADR-0025 — Çekirdek katman + **grain sözleşmesi** (fail-closed)

**Durum:** kabul edildi · **Faz:** FAZ 2.1 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 2.1` ile inerken, aynı
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

Aynı iş kavramı (`cari`, `ticaret`) üç ERP pack'inde **üç kez** tanımlanmıştı. Her kopya kendi sinonimlerini, kendi birimlerini ve kendi `additive` beyanını taşıyordu — ve üçü **ayrışmıştı**. Kopyaları elle senkronlamak, kopya sayısıyla çarpan bir bakım borcudur.

## Karar

Kaynak-sistem katmanlarının **altına** bir **çekirdek katman** girer ve ortak kavramları **bir kez** tanımlar. Birleştirme **dar**: yalnız `synonyms` ve `unit`. 🔴 **`additive` BİRLEŞTİRİLMEZ** — bir ölçünün toplanabilirliği o ölçünün **kendi** gerçeğidir ve devralınırsa bir bakiye sessizce `SUM` edilir.

🔴 **GRAIN SÖZLEŞMESİ FAIL-CLOSED:** bir cube başka bir grain'in ölçüsünü taşıyorsa derleme **durur**. Sessizce geçirmek, fan-out'u derleme zamanından sorgu zamanına ertelemek olurdu.

## Sonuçlar

- Yeni bir ERP eklemek, ortak kavramları **yeniden tanımlamaz**.
- ⚠ Katman `cekirdek_katman` ayarıyla `off|shadow|on`: `shadow` derler ama kullanmaz — göçün maliyeti **ölçülerek** ödenir.
- ⚠ `lab/mdl_diff.py` gölge derlemeyi karşılaştırır; `additive` **sayı kovasında** (ilk sürümde 'sözlük' kovasındaydı ve **beş gerçek davranış değişikliğini** maskeledi).

## Kanıt — **tek doğrulama yolu**

- `app/cekirdek.py`
- `tests/test_cekirdek_katman.py`
- `demo/packs/cekirdek/pack.yml`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
