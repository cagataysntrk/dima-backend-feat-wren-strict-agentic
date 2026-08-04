# ADR-0009 — Feature flag: global ⊕ sektör ⊕ şirket ⊕ DB override

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **9** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **9 atıf** aldı ve `docs/adr/` dizini
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

Bir özelliği herkese aynı anda açmak, ölçmeden sevk etmektir.

## Karar

Bayraklar **en spesifik kazanacak** şekilde çözülür: `global < sektör < tenant < rol < kullanıcı`. Metadata tek kaynakta (`FLAG_REGISTRY`).

## Sonuçlar

- 🔴 **BAYRAK ≠ YETKİ.** Bayrak rollout/görünürlük içindir; güvenlik sınırı **her zaman** `authorize()`'dır ve bir bayrak onu **gevşetemez**.
- **KURAL B** buradan doğar: bayrak `off` iken davranış **bayt bayt** öncekiyle aynı olmalı ve bu bir **testle** kilitlenmeli — aksi hâlde 'geri al' bir temennidir.

## Kanıt — **tek doğrulama yolu**

- `app/features.py`
- `demo/packs/features.yml`
- `FeatureOverride`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
