# ADR-0005 — Kompozisyon: şirket ⊕ sektör ⊕ modül → derlenmiş wren-projesi

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **21** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **21 atıf** aldı ve `docs/adr/` dizini
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

Her müşteri için ayrı bir semantik model yazmak, küratörlük emeğini müşteri sayısıyla **çarpardı**. Ama tek bir jenerik model de hiçbir müşteriye uymaz.

## Karar

**İçerik YAML'da, kod generic.** Katmanlar en spesifik kazanacak şekilde birleşir: `kaynak → modül → sektör → kesişim(kaynak∧sektör) → şirket`.

## Sonuçlar

- Yeni bir müşteri **kod değişikliği olmadan** açılabiliyor.
- Katman sırası bir **sözleşmedir**: sırayı değiştirmek sessizce başka bir modeli derler. `test_kaynak_compose.py` sırayı kilitler.
- ⚠ Derleme **fail-closed**: geçersiz bir katman sessizce atlanmaz, derleme durur (EK G'nin `G5`/`G10` kapıları).

## Kanıt — **tek doğrulama yolu**

- `app/compose.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
