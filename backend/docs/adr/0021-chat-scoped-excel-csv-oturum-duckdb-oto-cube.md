# ADR-0021 — Chat-scoped Excel/CSV → oturum DuckDB → oto-cube

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

Kullanıcının elindeki dosyayı analiz edebilmek için ya serbest Python çalıştırılmalı (uydurma sayının kapısı) ya da dosya **modele** çevrilmeli.

## Karar

Yüklenen dosya oturum-kapsamlı bir DuckDB'ye ve **oto-cube**'a çevrilir; sonrasında **tüm pipeline bedava** çalışır (route · guard · makbuz).

## Sonuçlar

- 🔴 Ad-hoc cube **yapı verir, güven rozetini VERMEZ** — küratörlenmiş bir cube ile aynı şey değildir ve arayüzde de öyle görünür.
- ⚠ Veri **kalıcı değildir** (oturum kapsamı) — kalıcılık DB sihirbazının işidir.

## Kanıt — **tek doğrulama yolu**

- `app/dataset.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
