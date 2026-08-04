# ADR-0023 — Yeni cube kapısı: yazılı gerekçe + başka modülün grain'ini çalmama

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **1** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **1 atıf** aldı ve `docs/adr/` dizini
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

Her yeni soru için yeni bir cube açmak, kataloğu **birbirinin kopyası** cube'larla doldurur ve yönlendirmeyi belirsizleştirir (FAZ 2.1'in ölçtüğü kusur).

## Karar

Yeni bir cube **yazılı gerekçe** ister ve **başka bir modülün grain'ini çalamaz**. Aynı grain'deki bir ihtiyaç bir **mercek** olarak yaşar, ikinci bir cube olarak değil.

## Sonuçlar

- ⚠ Bu ADR **en az atıf alan** kararlardan (1) ama FAZ 2.1/2.4'ün tamamı ona dayandı — *atıf sayısı bir önem ölçüsü değildir.*

## Kanıt — **tek doğrulama yolu**

- `demo/packs/modul/enerji/` yorumları
- `tests/test_yeni_kup_kapisi.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
