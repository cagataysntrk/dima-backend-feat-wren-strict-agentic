# ADR-0008 — **"Anlamadığını bil"** — tanınmayan kelime ⇒ cevap yok ve öneri yok

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **70** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **70 atıf** aldı ve `docs/adr/` dizini
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

Bir BI sisteminin en pahalı hatası *"cevap veremedim"* değil, **yanlış cevaba güven rozeti takmaktır**. Tek bir tanınmayan kelime, sorunun anlamını tamamen değiştirebilir.

## Karar

Soruda **tanınmayan bir kelime varsa cevap üretilmez** — ve **öneri de üretilmez**. **K1:** kapsam dışı bir soruya yakın bir cevap vermek, cevap vermemekten kötüdür. **K3: LLM TARİH HESAPLAMAZ** — dönem aritmetiği Python takvimidir.

🔴 **DİSİPLİN: REFLEKSLE YENİ REGEX EKLEME.** Kayıtlı desen: `_uncovered`'ın alt-dize körlüğü defalarca **kelimeye özel bir yamayla** geçiştirildi ve kök neden hiç düzeltilmedi. **Kural: kök nedeni düzelt, örneği değil.**

## Sonuçlar

- Bu ADR bu depodaki **en çok atıf alan** karardır (70) ve neredeyse her yeni özellik ona karşı sınanır: *bir sözlük mü ekliyorum, bir mekanizma mı?*
- ⚠ Sıralama/öneri üreten mekanizmalar bu kapsamın **dışındadır** (yanlış sıralama bir soruyu cevapsız bırakmaz) — ama bu istisna **yazılı olmak zorundadır**.

## Kanıt — **tek doğrulama yolu**

- `app/cube_router.py`
- `app/value_index.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
