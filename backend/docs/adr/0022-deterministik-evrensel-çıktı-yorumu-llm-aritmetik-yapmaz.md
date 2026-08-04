# ADR-0022 — Deterministik evrensel çıktı yorumu — LLM aritmetik yapmaz

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **3** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **3 atıf** aldı ve `docs/adr/` dizini
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

*"Satışlar %12 arttı"* cümlesindeki `%12`'yi bir dil modeli üretirse, o sayı **doğrulanamaz**.

## Karar

Olgular (`facts`) **deterministik** hesaplanır; LLM yalnız **üslup** koyar ve `narration_guard` eşleşmeyen sayı taşıyan cümleyi **düşürür**.

## Sonuçlar

- En kötü durum *"süssüz ama doğru"*tur.
- 🔴 Bu, **LLM anlar ve söyler; küp bilir ve kanıtlar** omurgasının çıktı tarafıdır.

## Kanıt — **tek doğrulama yolu**

- `app/interpret.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
