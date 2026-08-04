# ADR-0014 — Kimlik/yetki token'dan türer — **K6: her erişim iz bırakır**

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **25** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **25 atıf** aldı ve `docs/adr/` dizini
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

Kimliğin ikinci bir kopyası (istek gövdesinde tenant, header'da rol) **her zaman** asıl kaynakla ayrışır ve ayrışan taraf **daha gevşek** olanıdır.

## Karar

Her kimlik özniteliği **token'dan** türer. **K6: her veri erişimi kanıtlanabilir bir iz bırakır** (KVKK) — **audit satırı yazılmadan başarı raporlanmaz**.

## Sonuçlar

- Tenant-RLS token'daki `tsl` üzerinden zorlanır; gövdeden gelen tenant **yok sayılır**.
- 🔴 K6 bir **sıralama** kuralıdır: önce iz, sonra cevap. Tersi, denetlenemeyen bir başarı üretirdi.

## Kanıt — **tek doğrulama yolu**

- `control_plane/authorize.py`
- `app/audit.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
