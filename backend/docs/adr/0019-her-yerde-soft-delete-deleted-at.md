# ADR-0019 — Her yerde soft delete (`deleted_at`)

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **16** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **16 atıf** aldı ve `docs/adr/` dizini
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

Silinen bir kayıt, denetim izinin de silinmesi demek olabilir.

## Karar

Silme **işaretlemedir**; okuma filtreler. Kararlar **append-only** yazılır (revizyon `supersedes` ile yeni satır).

## Sonuçlar

- Denetim izi kopmaz.
- ⚠ KVKK silme talebi **ayrı bir yoldur** — soft delete onun yerine geçmez.

## Kanıt — **tek doğrulama yolu**

- `control_plane/models.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
