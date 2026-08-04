# ADR-0016 — DB→dosya tek yönlü materializer

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **4** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **4 atıf** aldı ve `docs/adr/` dizini
> *"ne diskte ne git geçmişinde"* vardı (MIMARI §8.2, ölçüldü). Bu dosya, o atıfların
> **bağlamından ve kodun kendisinden** türetildi (FAZ 4.6 @`5d2f37b`).
>
> **Başlıklar alıntı değildir.** Bir cümle *"ADR şöyle diyordu"* diye okunamaz; yalnız
> *"kod bugün şöyle davranıyor ve gerekçesi şu"* diye okunabilir. **Kanıt sütunu tek
> doğrulama yoludur** — çelişkide **kod kazanır**, bu dosya değil.
>
> *Var olmayan bir belgeye atıf yapmak bir eksiklikti; onu uydurulmuş bir tarihle
> doldurmak bir sahtekârlık olurdu.*


## Bağlam

Aynı gerçeğin iki sahibi (DB satırı ve YAML dosyası) olduğunda ikisi **ayrışır** ve hangisinin doğru olduğu ancak bir kusur çıkınca anlaşılır.

## Karar

`TenantConfig` satırı olan tenant'ın `company.yml`'i **TÜRETİLMİŞTİR**. Elle düzenleme materializer'da **ezilir**. Kaynak = control-plane DB.

## Sonuçlar

- 🔴 Tek yönlülük bir **kısıt değil, kararın kendisidir**: çift yönlü olsaydı 'aynı kuralın iki sahibi' kusuru yapısallaşırdı.

## Kanıt — **tek doğrulama yolu**

- `app/materialize.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
