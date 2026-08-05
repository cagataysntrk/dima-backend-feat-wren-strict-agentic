# ADR-0034 — **Görsel dilbilgisi daralması** — ne zaman grafik ÇİZİLMEZ

**Durum:** kabul edildi · **Faz:** FAZ 5.11 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 5.11` ile inerken, aynı
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

~50.000 yanıtlık bir çalışma genel kullanıcının grafiği tercih ettiğini gösteriyor **ama karar-vericiler ve finans profesyonelleri TABLO tercih ediyor** `[DOĞRULANMADI — birincil kaynak okunmadı]`.

## Karar

Dört **daraltıcı** kural (bir grafiği tabloya/cümleye çevirir, tersi asla): ≤2 satır **veya** ≤3 kategori (tek ölçü) → cümle · >20 kategori **ve sıralanmamış** → tablo · finans/muhasebe cube'u → tablo. Kurallar yalnız **varsayılan `bar`**'a uygulanır.

## Sonuçlar

- 🔴 Kural 3'ün şartı **SIRA**, sayı değil: 50 kategorili bir Top-N çubuğu okunabilir, 21 kategorili alfabetik bir çubuk okunamaz.
- ⚠ **Zaman serisi hiçbir kuralda tabloya çevrilmez** — bir trend tablo hâlinde **görülemez**.
- ⚠ Daraltma **teklifleri de kapatır**: *bir karar, kendi alternatifini önermez.*
- 🔴 `cizilmedi` gerekçesi **kullanıcıya gösterilir** — aksi hâlde deterministik bir karar bir **arıza** gibi görünür.

## Kanıt — **tek doğrulama yolu**

- `app/viz.py` `_cizme_kurallari`
- `tests/test_viz.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
