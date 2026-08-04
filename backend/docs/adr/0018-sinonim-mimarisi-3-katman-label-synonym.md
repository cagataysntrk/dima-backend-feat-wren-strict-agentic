# ADR-0018 — Sinonim mimarisi 3 katman — **LABEL ⊆ SYNONYM**

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **34** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **34 atıf** aldı ve `docs/adr/` dizini
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

Kullanıcı *"hasılat"* diyor, cube *"toplam_ciro"* diyor. Bu boşluk kapanmazsa kapsam küratörlük emeğiyle **doğrusal** sınırlanır.

## Karar

Üç katman: **pack YAML ⊕ arketip ⊕ canlı öğrenilen overlay**. Overlay **additive**'dir ve **asla silmez**. Evrensel kural: **LABEL ⊆ SYNONYM** — bir şeyin ekranda görünen adı, ona ulaşmanın da yolu olmalıdır.

## Sonuçlar

- 🔴 **Adaylar otomatik canlıya çıkmaz** — öğrenme bir **öneri**, terfi bir **karar**.
- ⚠ Bu ADR ile ADR-0008 gerilimlidir ve gerilim **bilinçlidir**: sinonim eklemek kapsamı artırır, refleksle eklemek ise 0008'in yasağıdır. Ayrım: **mekanizma mı, örnek mi?**

## Kanıt — **tek doğrulama yolu**

- `app/synonyms.py`
- `SynonymOverride`
- `app/archetypes.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
