# ADR-0017 — Kaynak-sistem pack facet'i + generic clone/sync motoru

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **50** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **50 atıf** aldı ve `docs/adr/` dizini
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

Müşterilerin ERP'leri farklı (logo-3 · mikro-v16 · netsis) ama **aynı iş kavramlarını** taşıyor. Her ERP için ayrı bir ürün yazmak, ürünü ERP sayısına bölmek olurdu.

## Karar

ERP **bir pack facet'idir**: parmak izi tanınır, canlı introspection yapılır, lehçe çevrilir. **§9: clone/sync motoru datasource-BAĞIMSIZ.** **K6/K9:** introspection sonuçları **insan onayından** geçmeden modele girmez.

## Sonuçlar

- Yeni ERP eklemek bir **pack** işidir, bir motor işi değil.
- ⚠ Şablonlu pack'lerde (logo-3) modeller **şirkete üretilir** — pack'te durmaz.

## Kanıt — **tek doğrulama yolu**

- `app/compose.py`
- `admin_app/clone/`
- `app/db_introspect.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
