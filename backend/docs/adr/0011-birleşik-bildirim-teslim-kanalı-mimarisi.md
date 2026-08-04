# ADR-0011 — Birleşik bildirim/teslim kanalı mimarisi

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **18** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **18 atıf** aldı ve `docs/adr/` dizini
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

E-posta · panel · webhook ayrı ayrı yazılırsa, bir raporun *nereye* gittiği üç farklı yerde tanımlanır ve üçü **ayrışır**.

## Karar

Teslim tek bir **kanal** soyutlamasıdır; zamanlama ondan bağımsızdır.

## Sonuçlar

- Yeni bir kanal eklemek zamanlama koduna dokunmaz.
- ⚠ PII maskeleme **kanalın değil** `pii.py`'nin işidir — tek çıkış noktası.

## Kanıt — **tek doğrulama yolu**

- `app/channels.py`
- `app/schedules.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
