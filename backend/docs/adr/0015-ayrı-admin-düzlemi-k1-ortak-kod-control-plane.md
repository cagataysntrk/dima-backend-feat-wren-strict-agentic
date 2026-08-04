# ADR-0015 — Ayrı admin düzlemi — **K1: ortak kod `control_plane/`**

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **53** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **53 atıf** aldı ve `docs/adr/` dizini
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

Admin ve müşteri düzlemleri aynı süreçte aynı secret'la çalışırsa, birinde açılan bir gedik ötekini de açar.

## Karar

Admin **ayrı süreç**, **ayrı JWT secret çifti**, **zorunlu 2FA**. **K1:** ortak auth kodu `control_plane/`'de durur, kopyalanmaz. **K7:** admin düzlemi müşteri verisine **doğrudan** erişmez.

## Sonuçlar

- İki düzlem birbirinin token'ını **doğrulayamaz** — bu bir kolaylık kaybı değil, kararın kendisidir.

## Kanıt — **tek doğrulama yolu**

- `admin_app/main.py`
- `control_plane/`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
