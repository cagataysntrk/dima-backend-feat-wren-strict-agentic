# ADR-0010 — Query Contract: SQL + MDL sürümü + parametre + sonuç hash'i

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **20** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **20 atıf** aldı ve `docs/adr/` dizini
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

Bir sayı bugün doğruysa yarın da doğru mudur? Şema değişmiş, ölçü tanımı güncellenmiş olabilir. **Sayının kendisi bunu söylemez.**

## Karar

Her çalıştırma bir **sözleşme** yazar: SQL · MDL sürümü · parametreler · sonuç hash'i. Postgres tek kaynaktır.

## Sonuçlar

- Aynı soru aynı sözleşmeyle **yeniden koşulabilir** (`POST /cube` — 0 LLM).
- Sonuç değişmişse **neyin** değiştiği (şema mı, veri mi) ayırt edilebilir.

## Kanıt — **tek doğrulama yolu**

- `app/contracts.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
