# ADR-0020 — Sessiz yutma yok — sistem/app logger + `interaction_log`

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **30** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **30 atıf** aldı ve `docs/adr/` dizini
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

`except Exception: pass` bir hatayı **yok etmez**, yalnız **görünmez** yapar — ve görünmeyen bir hata, olmayan bir hatadan pahalıdır.

## Karar

Hiçbir hata sessizce yutulmaz. Yutulması gereken yerlerde (ölçüm araçları, opsiyonel bloklar) **kayıt yazılır** ve akış kırılmaz.

## Sonuçlar

- Bu depodaki `# noqa: BLE001` satırlarının her biri bir **beyandır**, bir kaçamak değil: yanına neden yutulduğu yazılır.

## Kanıt — **tek doğrulama yolu**

- `app/logging_setup.py`
- `InteractionLog`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
